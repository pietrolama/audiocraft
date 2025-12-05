from enum import Enum
from typing import Dict, Optional, Callable, Any
from datetime import datetime
from collections import defaultdict
import uuid
import asyncio
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class Job(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = 0  # 0-100
    message: str = ""
    result_url: Optional[str] = None
    error: Optional[str] = None
    params: Dict[str, Any] = {}
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class JobManager:
    """Manages job queue and execution"""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.workers: int = 1
        self.progress_callbacks: Dict[str, list[Callable]] = defaultdict(list)
        self._worker_task: Optional[asyncio.Task] = None
    
    def start_worker(self, process_fn: Callable):
        """Start background worker that processes jobs"""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._worker_loop(process_fn))
            logger.info("Job worker started")
    
    async def _worker_loop(self, process_fn: Callable):
        """Background worker loop"""
        while True:
            try:
                job_id = await self.queue.get()
                job = self.jobs[job_id]
                
                # Update status to running
                job.status = JobStatus.RUNNING
                job.started_at = datetime.now()
                self.update_job(job)
                
                try:
                    # Process job with callback for progress
                    def progress_callback(progress: int, message: str = ""):
                        job.progress = progress
                        job.message = message
                        self.update_job(job)
                    
                    # Register callback for this job
                    self.progress_callbacks[job_id].append(progress_callback)
                    
                    # Execute job
                    result = await process_fn(job, progress_callback)
                    
                    # Mark as done
                    job.status = JobStatus.DONE
                    job.progress = 100
                    job.result_url = result
                    job.completed_at = datetime.now()
                    self.update_job(job)
                    
                except Exception as e:
                    logger.error(f"Job {job_id} failed: {e}", exc_info=True)
                    job.status = JobStatus.ERROR
                    job.error = str(e)
                    job.completed_at = datetime.now()
                    self.update_job(job)
                
                finally:
                    # Cleanup callbacks
                    if job_id in self.progress_callbacks:
                        del self.progress_callbacks[job_id]
                    self.queue.task_done()
            
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    def create_job(self, params: Dict[str, Any]) -> Job:
        """Create a new job and add to queue"""
        job_id = str(uuid.uuid4())
        job = Job(
            job_id=job_id,
            status=JobStatus.QUEUED,
            params=params,
            created_at=datetime.now()
        )
        self.jobs[job_id] = job
        self.queue.put_nowait(job_id)
        logger.info(f"Created job {job_id}")
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def update_job(self, job: Job):
        """Update job state"""
        self.jobs[job.job_id] = job


# Global job manager instance
job_manager = JobManager()

