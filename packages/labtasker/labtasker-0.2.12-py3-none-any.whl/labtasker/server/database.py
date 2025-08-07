from typing import Any, Dict, List, Mapping, Optional, Tuple, Union
from uuid import uuid4

from fastapi import HTTPException
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection, ReturnDocument
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from labtasker.constants import Priority
from labtasker.security import hash_password
from labtasker.server.db_utils import (
    arg_match,
    keys_to_query_dict,
    merge_filter,
    query_dict_to_mongo_filter,
    retry_on_transient,
    sanitize_dict,
    sanitize_query,
    sanitize_update,
    validate_arg,
)
from labtasker.server.fsm import (
    StateTransitionEventHandle,
    TaskFSM,
    TaskState,
    WorkerFSM,
    WorkerState,
)
from labtasker.server.logging import logger
from labtasker.utils import (
    add_key_prefix,
    get_current_time,
    parse_time_interval,
    risky,
    unflatten_dict,
)


class DBService:

    def __init__(
        self,
        db_name: str,
        uri: Optional[str] = None,
        client: Optional[MongoClient] = None,
    ):
        """
        Initialize database client. If client is provided, it will be used instead of connecting to MongoDB.
        The instances of this class is stateless. The instance itself does not preserve any state across API calls.
        """
        if client:
            self._client = client
            self._db = self._client[db_name]
            self._setup_collections()
            return

        try:
            self._client = MongoClient(uri, w="majority", retryWrites=True)
            self._client.admin.command("ping")
            self._db: Database = self._client[db_name]  # type: ignore
            self._setup_collections()
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to connect to MongoDB: {str(e)}",
            )

    def ping(self) -> bool:
        self._client.admin.command("ping")
        return True

    def is_empty(self):
        return (
            self._queues.count_documents({}) == 0
            and self._tasks.count_documents({}) == 0
            and self._workers.count_documents({}) == 0
        )

    def _setup_collections(self):
        """Setup collections and indexes."""
        # Queues collection
        self._queues: Collection = self._db.queues
        # _id is automatically indexed by MongoDB
        self._queues.create_index([("queue_name", ASCENDING)], unique=True)

        # Tasks collection
        self._tasks: Collection = self._db.tasks
        # _id is automatically indexed by MongoDB
        self._tasks.create_index([("queue_id", ASCENDING)])  # Reference to queue._id
        self._tasks.create_index([("status", ASCENDING)])
        self._tasks.create_index([("priority", DESCENDING)])  # Higher priority first
        self._tasks.create_index([("created_at", ASCENDING)])  # Older tasks first

        # Workers collection
        self._workers: Collection = self._db.workers
        # _id is automatically indexed by MongoDB
        self._workers.create_index([("queue_id", ASCENDING)])  # Reference to queue._id
        self._workers.create_index(
            [("worker_name", ASCENDING)]
        )  # Optional index for searching

    def close(self):
        """Close the database client."""
        self._client.close()

    def erase(self):
        """Erase all data"""
        for col_name in self._db.list_collection_names():
            collection = self._db[col_name]
            collection.drop()

        self._setup_collections()

    @retry_on_transient
    @validate_arg
    def query_collection(
        self,
        queue_id: str,
        collection_name: str,
        query: Dict[str, Any],  # MongoDB query
        limit: int = 100,
        offset: int = 0,
        sort: Optional[List[Tuple[str, int]]] = None,
        hide_id: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Query a collection with options to hide _id field and add collection-specific ID aliases.

        Args:
            queue_id: The queue ID for security filtering
            collection_name: Name of the collection to query (queues, tasks, workers)
            query: MongoDB query dictionary
            limit: Maximum number of results to return
            offset: Number of results to skip
            sort: List of (field, direction) tuples for sorting
            hide_id: Whether to hide the _id field in results

        Returns:
            List of documents matching the query
        """
        sort = sort or [
            ("last_modified", ASCENDING)
        ]  # Default sort by last_modified first
        with self._client.start_session() as session:
            with session.start_transaction():
                if collection_name not in ["queues", "tasks", "workers"]:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail="Invalid collection name. Must be one of: queues, tasks, workers",
                    )

                query = sanitize_query(queue_id, query)

                pipeline: List[Mapping[str, Any]] = []

                # Add ID field aliases based on collection type
                id_field_mapping = {
                    "tasks": "task_id",
                    "workers": "worker_id",
                    "queues": "queue_id",
                }

                collection_id_field = id_field_mapping.get(collection_name)
                if collection_id_field:
                    pipeline.append({"$addFields": {collection_id_field: "$_id"}})

                pipeline.extend(
                    [
                        {"$match": query},
                        {"$project": {"password": 0}},
                        {"$sort": {field: direction for field, direction in sort}},
                        {"$skip": offset},
                        {"$limit": limit},
                    ]
                )

                # Hide _id if requested
                if hide_id:
                    pipeline.append({"$project": {"_id": 0}})

                result = list(
                    self._db[collection_name].aggregate(pipeline, session=session)
                )
                return result

    @risky("Potential query injection")
    @retry_on_transient
    @validate_arg
    def update_collection(
        self,
        queue_id: str,
        collection_name: str,
        query: Dict[str, Any],  # MongoDB query
        update: Dict[str, Any],  # MongoDB update
    ) -> int:
        """Update a collection. Return modified count"""
        with self._client.start_session() as session:
            with session.start_transaction():
                if collection_name not in ["queues", "tasks", "workers"]:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail="Invalid collection name. Must be one of: queues, tasks, workers",
                    )

                # Prevent query injection
                query = sanitize_query(queue_id, query)

                now = get_current_time()

                update = sanitize_update(
                    update
                )  # make sure important fields are not tempered with

                if update.get("$set"):
                    update["$set"]["last_modified"] = now
                else:
                    update["$set"] = {"last_modified": now}

                result = self._db[collection_name].update_many(
                    query, update, session=session
                )
                return result.modified_count

    @retry_on_transient
    @validate_arg
    def create_queue(
        self,
        queue_name: str,
        password: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new queue."""
        if not queue_name:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Queue name is required"
            )
        with self._client.start_session() as session:
            with session.start_transaction():
                try:
                    now = get_current_time()
                    queue = {
                        "_id": str(uuid4()),
                        "queue_name": queue_name,
                        "password": hash_password(password),
                        "created_at": now,
                        "last_modified": now,
                        "metadata": unflatten_dict(metadata or {}),
                    }
                    result = self._queues.insert_one(queue, session=session)
                    return str(result.inserted_id)
                except DuplicateKeyError:
                    raise HTTPException(
                        status_code=HTTP_409_CONFLICT,
                        detail=f"Queue '{queue_name}' already exists",
                    )

    @retry_on_transient
    @validate_arg
    def create_task(
        self,
        queue_id: str,
        task_name: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        cmd: Optional[Union[str, List[str]]] = None,
        heartbeat_timeout: Optional[float] = None,
        task_timeout: Optional[
            int
        ] = None,  # Maximum time in seconds for task execution
        max_retries: int = 3,  # Maximum number of retries
        priority: int = Priority.MEDIUM,
    ) -> str:
        """Create a task related to a queue."""
        if not args and not cmd:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Either args or cmd must be provided",
            )
        with self._client.start_session() as session:
            with session.start_transaction():
                now = get_current_time()

                task_id = str(uuid4())

                fsm = TaskFSM(
                    queue_id=queue_id,
                    entity_id=task_id,
                    current_state=TaskState.CREATED,
                    retries=0,
                    max_retries=max_retries,
                    metadata=None,
                )
                event_handle = fsm.create()

                task = {
                    "_id": task_id,
                    "queue_id": queue_id,
                    "status": TaskState.PENDING,
                    "task_name": task_name,
                    "created_at": now,
                    "start_time": None,
                    "last_heartbeat": None,
                    "last_modified": now,
                    "heartbeat_timeout": heartbeat_timeout,
                    "task_timeout": task_timeout,
                    "max_retries": max_retries,
                    "retries": 0,
                    "priority": priority,
                    "metadata": unflatten_dict(metadata or {}),
                    "args": unflatten_dict(args or {}),
                    "cmd": cmd or "",
                    "summary": {},
                    "worker_id": None,
                }
                result = self._tasks.insert_one(task, session=session)

        event_handle.update_fsm_event(task, commit=True)

        return str(result.inserted_id)

    @retry_on_transient
    @validate_arg
    def create_worker(
        self,
        queue_id: str,
        worker_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> str:
        """Create a worker."""
        with self._client.start_session() as session:
            with session.start_transaction():
                now = get_current_time()

                worker_id = str(uuid4())

                fsm = WorkerFSM(
                    queue_id=queue_id,
                    entity_id=worker_id,
                    current_state=WorkerState.CREATED,
                    retries=0,
                    max_retries=max_retries,
                    metadata=None,
                )
                event_handle = fsm.create()

                worker = {
                    "_id": worker_id,
                    "queue_id": queue_id,
                    "status": WorkerState.ACTIVE,
                    "worker_name": worker_name,
                    "metadata": unflatten_dict(metadata or {}),
                    "retries": 0,
                    "max_retries": max_retries,
                    "created_at": now,
                    "last_modified": now,
                }
                result = self._workers.insert_one(worker, session=session)

        event_handle.update_fsm_event(worker, commit=True)

        return str(result.inserted_id)

    @retry_on_transient
    @validate_arg
    def delete_queue(
        self,
        queue_id,
        cascade_delete: bool = True,
    ) -> int:
        """
        Delete a queue.

        Args:
            queue_id (str): The id of the queue to delete.
            cascade_delete (bool): Whether to delete all tasks and workers in the queue.

        Return:
            deleted_count: total affected entries
        """
        with self._client.start_session() as session:
            with session.start_transaction():
                deleted_count = 0
                # Delete queue
                deleted_count += self._queues.delete_one(
                    {"_id": queue_id}, session=session
                ).deleted_count

                if cascade_delete:
                    # Delete all tasks in the queue
                    deleted_count += self._tasks.delete_many(
                        {"queue_id": queue_id}, session=session
                    ).deleted_count
                    # Delete all workers in the queue
                    deleted_count += self._workers.delete_many(
                        {"queue_id": queue_id}, session=session
                    ).deleted_count

                return deleted_count

    @retry_on_transient
    @validate_arg
    def delete_task(
        self,
        queue_id: str,
        task_id: str,
    ) -> int:
        """Delete a task."""
        with self._client.start_session() as session:
            with session.start_transaction():
                # Delete task
                return self._tasks.delete_one(
                    {"_id": task_id, "queue_id": queue_id}, session=session
                ).deleted_count

    @retry_on_transient
    @validate_arg
    def delete_worker(
        self,
        queue_id: str,
        worker_id: str,
        cascade_update: bool = True,
    ) -> int:
        """
        Delete a worker.

        Args:
            queue_id (str): The name of the queue to delete the worker from.
            worker_id (str): The ID of the worker to delete.
            cascade_update (bool): Whether to set worker_id to None for associated tasks.

        Return:
            affected_count:
        """
        with self._client.start_session() as session:
            with session.start_transaction():
                affected_count = 0
                # Delete worker
                affected_count += self._workers.delete_one(
                    {"_id": worker_id, "queue_id": queue_id}, session=session
                ).deleted_count

                now = get_current_time()
                if cascade_update:
                    # Update all tasks associated with the worker
                    affected_count += self._tasks.update_many(
                        {"queue_id": queue_id, "worker_id": worker_id},
                        {"$set": {"worker_id": None, "last_modified": now}},
                        session=session,
                    ).modified_count

                return affected_count

    @retry_on_transient
    @validate_arg
    def update_queue(
        self,
        queue_id: str,
        new_queue_name: Optional[str] = None,
        new_password: Optional[str] = None,
        metadata_update: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Update queue settings. Returns modified_count"""
        with self._client.start_session() as session:
            with session.start_transaction():
                # Make sure name does not already exist
                if new_queue_name and self._get_queue_by_name(
                    new_queue_name, session=session, raise_exception=False
                ):
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f"Queue name '{new_queue_name}' already exists",
                    )

                update_dict = {}

                if new_queue_name:
                    update_dict["queue_name"] = new_queue_name
                if new_password:
                    update_dict["password"] = hash_password(new_password)

                if metadata_update is None:
                    metadata_update = {}
                elif metadata_update == {}:  # set the metadata root field to empty dict
                    metadata_update = {"metadata": {}}
                else:
                    metadata_update = sanitize_dict(metadata_update)
                    metadata_update = add_key_prefix(
                        metadata_update, prefix="metadata."
                    )

                # Update queue settings
                update = {
                    "$set": {
                        **update_dict,
                        **metadata_update,
                        "last_modified": get_current_time(),
                    }
                }
                result = self._queues.update_one(
                    {"_id": queue_id}, update, session=session
                )
                return result.modified_count

    @retry_on_transient
    @validate_arg
    def fetch_task(
        self,
        queue_id: str,
        worker_id: Optional[str] = None,
        eta_max: Optional[str] = None,
        heartbeat_timeout: Optional[float] = None,
        start_heartbeat: bool = True,
        required_fields: Optional[List[str]] = None,
        extra_filter: Optional[Dict[str, Any]] = None,
        cmd: Optional[Union[str, List[str]]] = None,
    ) -> Optional[Mapping[str, Any]]:
        """
        Fetch next available task from queue.
        1. Fetch task from queue
        2. Set task status to RUNNING
        3. Set task worker_id to worker_id (if provided)
        4. Update related timestamps
        5. Return task

        Args:
            queue_id (str): The id of the queue to fetch the task from.
            worker_id (str, optional): The ID of the worker to assign the task to.
            eta_max (str, optional): The optional task execution timeout override. Recommended using when start_heartbeat is False.
            heartbeat_timeout (float, optional): The optional heartbeat timeout interval in seconds.
            start_heartbeat (bool): Whether to start heartbeat.
            required_fields (list, optional): Which fields are required. If None, no constraint is put on which fields should exist in args dict.
            extra_filter (Dict[str, Any], optional): Additional filter criteria for the task.
            cmd (Optional[Union[str, List[str]]]): The command that runs the job.
        """
        task_timeout = parse_time_interval(eta_max) if eta_max else None

        required_fields = required_fields or []

        allow_arbitrary_args = "*" in required_fields
        if allow_arbitrary_args:  # prevent "*" messing with constructed mongodb query
            required_fields.remove("*")

        if not start_heartbeat and not task_timeout:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Eta max must be specified when start_heartbeat is False",
            )

        fetched_task = None
        with self._client.start_session() as session:
            with session.start_transaction():
                # Verify worker status if specified
                if worker_id:
                    worker = self._workers.find_one(
                        {"_id": worker_id, "queue_id": queue_id}, session=session
                    )
                    if not worker:
                        raise HTTPException(
                            status_code=HTTP_404_NOT_FOUND,
                            detail=f"Worker '{worker_id}' not found in queue '{queue_id}'",
                        )
                    worker_status = worker["status"]
                    if worker_status != WorkerState.ACTIVE:
                        raise HTTPException(
                            status_code=HTTP_403_FORBIDDEN,
                            detail=f"Worker '{worker_id}' is {worker_status} in queue '{queue_id}'",
                        )

                # Fetch task
                now = get_current_time()

                # "no less" of the "no more, no less" principle, user demanded fields must
                # exist in task args
                # even if allow_arbitrary_args==True, this principle should still be followed
                # else it may lead to unexpected missing keys.
                try:
                    query_dict = keys_to_query_dict(required_fields, mode="deepest")
                except (TypeError, ValueError) as e:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f"Invalid required fields. Detail: {str(e)}",
                    )
                required_fields_filter = query_dict_to_mongo_filter(
                    query_dict, parent_key="args"
                )

                combined_filter = merge_filter(
                    required_fields_filter, extra_filter, logical_op="and"
                )

                sanitized_filter = sanitize_query(queue_id, combined_filter)

                # Construct the query
                query = {
                    **sanitized_filter,
                    "queue_id": queue_id,
                    "status": TaskState.PENDING,
                }

                update = {
                    "$set": {
                        "status": TaskState.RUNNING,
                        "start_time": now,
                        "last_heartbeat": now if start_heartbeat else None,
                        "last_modified": now,
                        "worker_id": worker_id,
                        "cmd": cmd,
                        "summary": {},  # clear previous summary before fetched
                    }
                }

                if task_timeout:
                    update["$set"]["task_timeout"] = task_timeout

                if heartbeat_timeout:
                    update["$set"]["heartbeat_timeout"] = heartbeat_timeout

                tasks = self._tasks.aggregate(
                    [
                        {"$match": query},
                        {"$addFields": {"task_id": "$_id"}},
                        # sort: highest priority, least recently modified, oldest created
                        {
                            "$sort": {
                                "priority": DESCENDING,
                                "last_modified": ASCENDING,
                                "created_at": ASCENDING,
                            }
                        },
                    ],
                    session=session,
                )

                # "no more" of the "no more, no less" principle
                # those specified in the task["args"] should be required
                required_fields_no_more = keys_to_query_dict(
                    required_fields, mode="topmost"
                )
                for task in tasks:
                    if task:
                        if (
                            not allow_arbitrary_args
                            and required_fields_no_more
                            and not arg_match(required_fields_no_more, task["args"])
                        ):
                            continue  # Skip to the next task if it doesn't match

                        fsm = TaskFSM.from_db_entry(task)
                        event_handle = fsm.fetch()

                        fetched_task = self._tasks.find_one_and_update(
                            {"_id": task["_id"]},
                            update,
                            session=session,
                            return_document=ReturnDocument.AFTER,
                        )
                        break

        if fetched_task:
            event_handle.update_fsm_event(fetched_task, commit=True)  # type: ignore
            return fetched_task

        return None  # Return None if no tasks matched

    @retry_on_transient
    @validate_arg
    def refresh_task_heartbeat(
        self, queue_id: str, task_id: str, worker_id: Optional[str] = None
    ):
        """Update task heartbeat timestamp."""
        query = {"_id": task_id, "queue_id": queue_id, "status": "running"}

        with self._client.start_session() as session:
            with session.start_transaction():
                # Find the task in a single query
                task = self._tasks.find_one(query)
                if not task:
                    raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail=f"Task '{task_id}' not found in queue '{queue_id}' or not in 'running' state",
                    )

                # Validate worker if provided
                if worker_id:
                    if task["worker_id"] != worker_id:
                        raise HTTPException(
                            status_code=HTTP_403_FORBIDDEN,
                            detail=f"Task '{task_id}' is assigned to worker '{task['worker_id']}', not '{worker_id}'",
                        )

                    # Check worker status in a single query
                    worker = self._workers.find_one(
                        {"_id": worker_id, "status": WorkerState.ACTIVE}
                    )
                    if not worker:
                        raise HTTPException(
                            status_code=HTTP_404_NOT_FOUND,
                            detail=f"Worker '{worker_id}' not found or not active",
                        )

                # Update the task heartbeat
                result = self._tasks.update_one(
                    query,
                    {"$set": {"last_heartbeat": get_current_time()}},
                    session=session,
                )

                if result.modified_count == 0:
                    raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail=f"Failed to update heartbeat for task '{task_id}' - it may have changed state during the operation",
                    )

    @retry_on_transient
    @validate_arg
    def worker_report_task_status(
        self,
        queue_id: str,
        task_id: str,
        worker_id: str,
        report_status: str,
        summary_update: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Report task status by a worker.
        Preventing the following conflicting scenario:
            1. task foo assigned to worker A.
            2. worker A timed out while running.
            3. task foo reassigned to worker B.
            4. worker A report task status, but the task is actually run by worker B, which leads to confusion.

        Args:
            queue_id:
            task_id:
            worker_id:
            report_status:
            summary_update:

        Returns:

        """
        with self._client.start_session() as session:
            with session.start_transaction():
                task = self._tasks.find_one(
                    {"_id": task_id, "queue_id": queue_id}, session=session
                )
                if not task:
                    raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail=f"Task {task_id} not found",
                    )

                # check if the task is assigned to the worker
                if task["worker_id"] != worker_id:
                    raise HTTPException(
                        status_code=HTTP_409_CONFLICT,
                        detail=f"Task {task_id} is assigned to worker {task['worker_id']}",
                    )

                # The worker status update is also handled by _report_task_status
                event_handles = self._report_task_status(
                    queue_id=queue_id,
                    task=task,
                    report_status=report_status,
                    summary_update=summary_update,
                    session=session,
                )

        for event_handle in event_handles:
            event_handle.commit()

        return True

    @retry_on_transient
    @validate_arg
    def report_task_status(
        self,
        queue_id: str,
        task_id: str,
        report_status: str,
        summary_update: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update task status. Used for reporting task execution results."""
        with self._client.start_session() as session:
            with session.start_transaction():
                task = self._tasks.find_one(
                    {"_id": task_id, "queue_id": queue_id}, session=session
                )
                if not task:
                    raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail=f"Task {task_id} not found",
                    )
                event_handles = self._report_task_status(
                    queue_id=queue_id,
                    task=task,
                    report_status=report_status,
                    summary_update=summary_update,
                    session=session,
                )

        for event_handle in event_handles:
            event_handle.commit()
        return True

    def _report_task_status(
        self, queue_id, task, report_status, summary_update, session
    ) -> List[StateTransitionEventHandle]:
        event_handles = []
        task_id = task["_id"]
        try:
            fsm = TaskFSM.from_db_entry(task)

            if report_status == "success":
                event_handle = fsm.complete()
            elif report_status == "failed":
                event_handle = fsm.fail()
            elif report_status == "cancelled":
                event_handle = fsm.cancel()
            else:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=f"Invalid report_status: {report_status}",
                )

        except Exception as e:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # Update worker status if worker is specified
        if report_status == "failed" and task["worker_id"]:
            worker_event_handle = self._report_worker_status(
                queue_id=queue_id,
                worker_id=task["worker_id"],
                report_status="failed",
                session=session,
            )
            event_handles.append(worker_event_handle)

        if summary_update is None:
            summary_update = {}
        elif summary_update == {}:  # set the summary root field to empty dict
            summary_update = {"summary": {}}
        else:
            summary_update = sanitize_dict(summary_update)
            summary_update = add_key_prefix(summary_update, prefix="summary.")

        update = {
            "$set": {
                **summary_update,
                "status": fsm.state,
                "retries": fsm.retries,
                "last_modified": get_current_time(),
                "worker_id": None,
            }
        }

        updated_task = self._tasks.find_one_and_update(
            {"_id": task_id},
            update,
            session=session,
            return_document=ReturnDocument.AFTER,
        )

        # Update the event with entity data and publish
        event_handle.update_fsm_event(updated_task)  # type: ignore
        event_handles.append(event_handle)

        return event_handles

    @retry_on_transient
    @validate_arg
    def update_task(
        self,
        queue_id: str,
        task_id: str,
        task_setting_update: Optional[Dict[str, Any]] = None,
        reset_pending: bool = True,
    ) -> bool:
        """
        Update task settings (optional) and set task status to PENDING.
        Can be used to manually restart crashed tasks after max retries.

        Args:
            queue_id (str): The name of the queue to update the task in.
            task_id (str): The ID of the task to update.
            task_setting_update (Dict[str, Any], optional): A dictionary of task settings to update.
            reset_pending (bool): reset state to pending after updating

        Banned Fields from Updating: [_id, queue_id, created_at, last_modified]
        Potentially Auto-Overwritten Fields: [status, retries]
        """
        with self._client.start_session() as session:
            with session.start_transaction():
                task = self._tasks.find_one(
                    {"_id": task_id, "queue_id": queue_id}, session=session
                )
                if not task:
                    return False

                # Update task settings
                if task_setting_update:
                    # disallow mongodb operators
                    task_setting_update = sanitize_dict(task_setting_update)
                    task_setting_update_keys = list(task_setting_update.keys())
                    # ignore disallowed fields
                    banned_fields = [
                        "_id",
                        "queue_id",
                        "created_at",
                        "last_modified",
                    ]
                    for k in task_setting_update_keys:
                        if k.split(".")[0] in banned_fields:
                            del task_setting_update[k]
                else:
                    task_setting_update = {}

                task_setting_update["last_modified"] = get_current_time()

                fsm = TaskFSM.from_db_entry(task)

                if reset_pending:
                    event_handle = fsm.reset()
                    task_setting_update["status"] = fsm.state  # PENDING
                    task_setting_update["retries"] = fsm.retries  # 0
                    task_setting_update["worker_id"] = None  # reset worker_id
                else:
                    event_handle = None

                update = {
                    "$set": {
                        **task_setting_update,
                    }
                }

                updated_task = self._tasks.find_one_and_update(
                    {"_id": task_id, "queue_id": queue_id},
                    update,
                    session=session,
                    return_document=ReturnDocument.AFTER,
                )

                # if the FSM state is modified by user manually
                if not reset_pending and updated_task["status"] != task["status"]:
                    event_handle = fsm.transition_to(updated_task["status"])

                # reset worker_id if the task is pending and worker_id is not None
                if (
                    updated_task["status"] == TaskState.PENDING
                    and updated_task["worker_id"] is not None
                ):
                    self._tasks.update_one(
                        {"_id": task_id, "queue_id": queue_id},
                        {"$set": {"worker_id": None}},
                        session=session,
                    )

        if event_handle:
            event_handle.update_fsm_event(updated_task, commit=True)

        return True

    def get_task(self, queue_id: str, task_id: str) -> Optional[Mapping[str, Any]]:
        """Retrieve a task by ID."""
        return self._tasks.find_one({"_id": task_id, "queue_id": queue_id})

    def _report_worker_status(
        self, queue_id: str, worker_id: str, report_status: str, session=None
    ) -> StateTransitionEventHandle:
        worker = self._workers.find_one(
            {"_id": worker_id, "queue_id": queue_id}, session=session
        )
        if not worker:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail=f"Worker {worker_id} not found"
            )

        try:
            fsm = WorkerFSM.from_db_entry(worker)

            if report_status == "active":
                event_handle = fsm.activate()
            elif report_status == "suspended":
                event_handle = fsm.suspend()
            elif report_status == "failed":
                event_handle = fsm.fail()
            else:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=f"Invalid report_status: {report_status}",
                )

        except Exception as e:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        update = {
            "$set": {
                "status": fsm.state,
                "retries": fsm.retries,
                "last_modified": get_current_time(),
            }
        }

        updated_worker = self._workers.find_one_and_update(
            {"_id": worker_id},
            update,
            session=session,
            return_document=ReturnDocument.AFTER,
        )

        # Update the event with entity data and publish
        event_handle.update_fsm_event(updated_worker)

        return event_handle

    @retry_on_transient
    @validate_arg
    def report_worker_status(
        self,
        queue_id: str,
        worker_id: str,
        report_status: str,
    ) -> bool:
        """Update worker status."""
        with self._client.start_session() as session:
            with session.start_transaction():
                event_handle = self._report_worker_status(
                    queue_id=queue_id,
                    worker_id=worker_id,
                    report_status=report_status,
                    session=session,
                )
        event_handle.commit()
        return True

    def get_worker(self, queue_id: str, worker_id: str) -> Optional[Mapping[str, Any]]:
        """Retrieve a worker by ID."""
        return self._workers.find_one({"_id": worker_id, "queue_id": queue_id})

    def _get_queue_by_name(
        self, queue_name: str, session=None, raise_exception=True
    ) -> Optional[Mapping[str, Any]]:
        """Get queue by name with error handling.

        Args:
            queue_name: Name of queue to find
            session: Optional MongoDB session for transactions
            raise_exception: if not found, raise HTTPException

        Returns:
            Queue document

        Raises:
            HTTPException: If queue not found
        """
        queue = self._queues.find_one({"queue_name": queue_name}, session=session)
        if not queue:
            if raise_exception:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail=f"Queue '{queue_name}' not found",
                )
            return None
        return queue

    @retry_on_transient
    @validate_arg
    def get_queue(
        self,
        queue_id: Optional[str] = None,
        queue_name: Optional[str] = None,
    ) -> Optional[Mapping[str, Any]]:
        """Get queue by id or name. Name and id must match."""
        with self._client.start_session() as session:
            with session.start_transaction():
                if queue_id:
                    queue = self._queues.find_one({"_id": queue_id}, session=session)
                else:
                    queue = self._get_queue_by_name(queue_name, session=session)  # type: ignore

                if not queue:
                    return None

                # Make sure the provided queue_name and queue_id match
                if queue_id and queue["_id"] != queue_id:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f"Queue '{queue_name}' does not match queue_id '{queue_id}'",
                    )

                if queue_name and queue["queue_name"] != queue_name:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f"Queue '{queue_name}' does not match queue_id '{queue_id}'",
                    )

                return queue

    @retry_on_transient
    def handle_timeouts(self) -> List[str]:
        """Check and handle task timeouts."""
        now = get_current_time()
        transitioned_tasks = []

        # Build query
        query = {
            "status": TaskState.RUNNING,
            "$or": [
                # Heartbeat timeout
                {
                    "last_heartbeat": {"$ne": None},
                    "heartbeat_timeout": {"$ne": None},
                    "$expr": {
                        "$gt": [
                            {
                                "$divide": [
                                    {"$subtract": [now, "$last_heartbeat"]},
                                    1000,
                                ]
                            },
                            "$heartbeat_timeout",
                        ]
                    },
                },
                # Task execution timeout
                {
                    "task_timeout": {"$ne": None},
                    "start_time": {"$ne": None},
                    "$expr": {
                        "$gt": [
                            {"$divide": [{"$subtract": [now, "$start_time"]}, 1000]},
                            "$task_timeout",
                        ]
                    },
                },
            ],
        }

        fsm_event_handles = []
        with self._client.start_session() as session:
            with session.start_transaction():
                # Find tasks that might have timed out
                tasks = self._tasks.find(query, session=session)

                tasks = list(tasks)  # type: ignore

                for task in tasks:
                    try:
                        # Create FSM with current state
                        fsm = TaskFSM.from_db_entry(task)

                        # Transition to FAILED state through FSM
                        event_handle = fsm.fail()

                        # Update worker status if worker is specified
                        if task["worker_id"]:
                            worker_event_handle = self._report_worker_status(
                                queue_id=task["queue_id"],
                                worker_id=task["worker_id"],
                                report_status="failed",
                                session=session,
                            )
                            fsm_event_handles.append(worker_event_handle)

                        # Update task in database
                        updated_task = self._tasks.find_one_and_update(
                            {"_id": task["_id"]},
                            {
                                "$set": {
                                    "status": fsm.state,
                                    "retries": fsm.retries,
                                    "last_modified": now,
                                    "worker_id": None,
                                    "summary.labtasker_error": "Either heartbeat or task execution timed out",
                                }
                            },
                            return_document=ReturnDocument.AFTER,
                            session=session,
                        )

                        event_handle.update_fsm_event(updated_task)
                        fsm_event_handles.append(event_handle)

                        transitioned_tasks.append(task["_id"])
                    except Exception as e:
                        # Log error but continue processing other tasks
                        logger.info(
                            f"Error handling timeout for task {task['_id']}: {e}"
                        )

        # commit the event after the transaction is completed
        for event_handle in fsm_event_handles:
            event_handle.commit()

        return transitioned_tasks


_db_service = None


def get_db() -> DBService:
    """Get database service instance."""
    if not _db_service:
        raise RuntimeError("Database service not initialized.")
    return _db_service  # type: ignore


def set_db_service(db_service: DBService):
    global _db_service
    _db_service = db_service
