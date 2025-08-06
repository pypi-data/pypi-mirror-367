import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from mapchete.enums import Status
from mapchete.types import Progress
from shapely import to_wkt
from shapely.geometry import box, shape

from mapchete_hub.db.base import BaseStatusHandler
from mapchete_hub.geometry import process_area_from_config
from mapchete_hub.models import JobEntry, MapcheteJob
from mapchete_hub.random_names import random_name
from mapchete_hub.settings import mhub_settings
from mapchete_hub.timetools import parse_to_date

logger = logging.getLogger(__name__)


class MemoryStatusHandler(BaseStatusHandler):
    """Abstraction layer over in-memory backend."""

    _jobs: Dict[str, JobEntry]

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        self._jobs = {}
        logger.debug("enter MemoryStatusHandler")
        return self

    def __exit__(self, *args, **kwargs):
        logger.debug("exit MemoryStatusHandler")

    def job(self, job_id) -> JobEntry:
        return self._jobs[job_id]

    def jobs(self, **kwargs) -> List[JobEntry]:
        query = {k: v for k, v in kwargs.items() if v is not None}

        logger.debug("raw query: %s", query)

        bounds = query.get("bounds")
        bbox = box(*bounds) if bounds else None

        def _intersects_with(job: JobEntry, value: Any) -> bool:
            return shape(job).intersects(value)

        def _updated_since(job: JobEntry, value: datetime) -> bool:
            if job.updated:
                return parse_to_date(job.updated) >= parse_to_date(value)
            raise ValueError("job does not have a timestamp")

        def _updated_until(job: JobEntry, value: datetime) -> bool:
            if job.updated:
                return parse_to_date(job.updated) <= parse_to_date(value)
            raise ValueError("job does not have a timestamp")

        def _field_equals(job: JobEntry, value: Any, field: str) -> bool:
            return getattr(job, field) == value

        result: List[JobEntry] = []
        for job in self._jobs.values():
            for field, value in query.items():
                # skip job if any query field does not match
                if field == "bounds":
                    if not _intersects_with(job, bbox):  # pragma: no cover
                        break
                elif field == "from_date":
                    if not _updated_since(job, value):
                        break
                elif field == "to_date":
                    if not _updated_until(job, value):
                        break
                elif field == "status":
                    status = value if isinstance(value, list) else [value]
                    status = [Status[status] for status in status]
                    if job.status not in status:
                        break
                elif not _field_equals(job, value, field=field):
                    break
            else:
                try:
                    result.append(job)
                except Exception as exc:  # pragma: no cover
                    logger.exception("cannot create GeoJSON from entry: %s", exc)
        return result

    def new(self, job_config: MapcheteJob):
        """
        Create new job entry in database.
        """
        job_id = uuid4().hex
        logger.debug(
            f"got new job with config {job_config} and assigning job ID {job_id}"
        )
        process_area = process_area_from_config(
            job_config, dst_crs=os.environ.get("MHUB_BACKEND_CRS", "EPSG:4326")
        )[0]

        submitted = datetime.now(timezone.utc)
        job_entry = JobEntry.from_dict(
            dict(
                job_id=job_id,
                url=os.path.join(mhub_settings.self_url, "jobs", job_id),
                status=Status.pending,
                geometry=process_area,
                bounds=list(shape(process_area).bounds),
                area=to_wkt(shape(process_area)),
                mapchete=job_config,
                output_path=job_config.config.output["path"],
                submitted=submitted,
                started=submitted,
                updated=submitted,
                job_name=job_config.params.get("job_name") or random_name(),
                dask_specs=job_config.params.get("dask_specs", dict()),
            )
        )
        self._jobs[job_id] = job_entry
        return self.job(job_id)

    def set(
        self,
        job_id: str,
        status: Optional[Status] = None,
        progress: Optional[Progress] = None,
        exception: Optional[str] = None,
        traceback: Optional[str] = None,
        dask_dashboard_link: Optional[str] = None,
        dask_specs: Optional[dict] = None,
        results: Optional[str] = None,
        **kwargs,
    ) -> JobEntry:
        entry = self._jobs[job_id]
        new_attributes: Dict[str, Any] = {
            k: v
            for k, v in dict(
                exception=exception if exception is None else str(exception),
                traceback=traceback,
                dask_dashboard_link=dask_dashboard_link,
                dask_specs=dask_specs,
                results=results,
                **kwargs,
            ).items()
            if v is not None
        }
        timestamp = datetime.now(timezone.utc)
        if status:
            new_attributes.update(status=Status[status])
            if status == Status.initializing:
                new_attributes.update(started=timestamp)
            elif status == Status.done:
                started = self.job(job_id).started
                if started:
                    new_attributes.update(
                        runtime=(timestamp - started).total_seconds(),
                        finished=timestamp,
                    )
        if progress:
            new_attributes.update(current_progress=progress.current)
            if progress.total is not None:
                new_attributes.update(total_progress=progress.total)
        logger.debug("%s: update attributes: %s", job_id, new_attributes)
        entry.update(**new_attributes)
        # add timestamp to entry
        entry.update(updated=timestamp)

        self._jobs[job_id] = entry
        return self.job(job_id)
