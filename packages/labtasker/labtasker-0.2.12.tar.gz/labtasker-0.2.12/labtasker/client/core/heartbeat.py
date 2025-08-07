import os
import threading
import time
from contextvars import ContextVar
from typing import Optional

from labtasker.client.core.api import refresh_task_heartbeat
from labtasker.client.core.config import get_client_config
from labtasker.client.core.exceptions import LabtaskerRuntimeError
from labtasker.client.core.logging import logger
from labtasker.client.core.paths import get_labtasker_log_dir

__all__ = [
    "start_heartbeat",
    "end_heartbeat",
]


class Heartbeat:

    def __init__(self, task_id, worker_id, heartbeat_interval):
        self.task_id = task_id
        self.worker_id = worker_id
        self.heartbeat_interval = heartbeat_interval

        self._thread = None
        self._stop_event = threading.Event()

        # the heartbeat.lock file is useful for stopping heartbeat in the scheduler process from the actual job process
        self._lockfile = get_labtasker_log_dir() / "heartbeat.lock"

    def start(self):
        """Start the heartbeat thread."""
        self._thread = threading.Thread(target=self._heartbeat, daemon=True)

        # create a heartbeat lock file
        fd = os.open(self._lockfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)

        self._thread.start()

    def delay(self, interval: float) -> bool:
        """Returns False if it should exit."""
        slice_t = 0.05  # check for stop event
        start_time = time.perf_counter()
        while True:
            elapsed_time = time.perf_counter() - start_time
            remaining_time = interval - elapsed_time

            if remaining_time <= 0:
                break

            if self._stop_event.is_set() or not os.path.exists(self._lockfile):
                return False

            if remaining_time > 0.02:
                time.sleep(
                    min(
                        max(remaining_time / 2, 0.0001),
                        slice_t,
                    )
                )  # Sleep for a fraction of remaining time
            else:
                pass  # Busy-wait for very short intervals

        return True

    def _heartbeat(self):
        """Refresh heartbeat periodically"""
        while True:
            try:
                refresh_task_heartbeat(task_id=self.task_id, worker_id=self.worker_id)
            except Exception as e:
                logger.error(f"Failed to refresh heartbeat: {str(e)}")
                raise

            # Check if heartbeat should stop
            if not self.delay(self.heartbeat_interval):
                break

    def stop(self):
        """Stop the heartbeat thread."""
        if self._thread:
            self._stop_event.set()
            self._thread.join(timeout=self.heartbeat_interval * 10)
            try:  # try to remove heartbeat lock file
                os.unlink(self._lockfile)
            except FileNotFoundError:
                pass

    def is_alive(self):
        return self._thread and self._thread.is_alive()


_current_heartbeat: ContextVar[Optional[Heartbeat]] = ContextVar(
    "heartbeat", default=None
)


def start_heartbeat(
    task_id,
    worker_id: Optional[str] = None,
    heartbeat_interval: Optional[float] = None,
    raise_error=True,
):
    logger.debug("Try starting heartbeat.")
    if _current_heartbeat.get() is not None:
        if raise_error:
            raise LabtaskerRuntimeError("Heartbeat already started.")
        return

    heartbeat_manager = Heartbeat(
        task_id=task_id,
        worker_id=worker_id,
        heartbeat_interval=heartbeat_interval
        or get_client_config().task.heartbeat_interval,
    )
    heartbeat_manager.start()
    _current_heartbeat.set(heartbeat_manager)
    logger.debug("Heartbeat started.")
    return heartbeat_manager


def end_heartbeat(raise_error=True):
    logger.debug("Try ending heartbeat.")
    heartbeat_manager = _current_heartbeat.get()
    if heartbeat_manager is None:
        if raise_error:
            raise LabtaskerRuntimeError("Heartbeat not started properly.")
        return
    heartbeat_manager.stop()
    _current_heartbeat.set(None)
    logger.debug("Heartbeat ended.")
