from __future__ import annotations

import logging
import time
import traceback
from typing import Any, Dict, Optional

from mapchete.commands.observer import ObserverProtocol
from mapchete.enums import Status
from mapchete.errors import JobCancelledError
from mapchete.executor import DaskExecutor
from mapchete.types import Progress

from mapchete_hub.db import BaseStatusHandler
from mapchete_hub.models import JobEntry

logger = logging.getLogger(__name__)


class DBUpdater(ObserverProtocol):
    last_event: float = 0.0
    event_rate_limit: float = 0.2
    backend_db: BaseStatusHandler

    def __init__(
        self,
        backend_db: BaseStatusHandler,
        job_entry: JobEntry,
        event_rate_limit: float = 0.2,
    ):
        self.backend_db = backend_db
        self.job_entry = job_entry
        self.event_rate_limit = event_rate_limit

    def update(
        self,
        *_,
        status: Optional[Status] = None,
        progress: Optional[Progress] = None,
        executor: Optional[DaskExecutor] = None,
        exception: Optional[Exception] = None,
        result: Optional[dict] = None,
        **__,
    ):
        set_kwargs: Dict[str, Any] = dict()

        # check always if job was cancelled but respect the rate limit
        event_time_passed = time.time() - self.last_event
        if event_time_passed > self.event_rate_limit and status not in [
            Status.failed,
            Status.cancelled,
        ]:
            current_status = self.backend_db.job(self.job_entry.job_id).status
            # if job status was set to cancelled, raise a JobCancelledError
            if current_status == Status.cancelled:
                raise JobCancelledError("job was cancelled")

        # job status always has to be updated
        if status:
            set_kwargs.update(status=status)
            logger.debug(
                "DB update: job %s status changed to %s", self.job_entry.job_id, status
            )
            if status == Status.retrying:
                logger.debug("job retrying, reset dashboard link to None")
                self.set(dask_dashboard_link=None)

        if progress:
            # progress only at given minimal intervals
            event_time_passed = time.time() - self.last_event
            if (
                event_time_passed > self.event_rate_limit
                or progress.current == progress.total
            ):
                logger.debug(
                    "DB update: job %s progress changed to %s/%s",
                    self.job_entry.job_id,
                    progress.current,
                    progress.total,
                )
                set_kwargs.update(progress=progress)
                self.last_event = time.time()

        if executor:
            set_kwargs.update(dask_dashboard_link=executor._executor.dashboard_link)

        if exception:
            set_kwargs.update(
                exception=repr(exception),
                traceback="\n".join(traceback.format_tb(exception.__traceback__)),
            )

        if result:
            set_kwargs.update(result=result)

        if set_kwargs:
            self.set(**set_kwargs)

    def set(self, **kwargs):
        if kwargs:
            self.backend_db.set(self.job_entry.job_id, **kwargs)
