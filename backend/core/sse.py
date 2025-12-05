from sse_starlette.sse import EventSourceResponse
from fastapi import Request
from typing import AsyncGenerator
import asyncio
import json
import logging
from core.jobs import job_manager, Job

logger = logging.getLogger(__name__)


async def job_event_generator(job_id: str, request: Request) -> AsyncGenerator[str, None]:
    """Generate SSE events for job progress"""
    last_progress = -1
    
    while True:
        # Check if client disconnected
        if await request.is_disconnected():
            logger.info(f"Client disconnected for job {job_id}")
            break
        
        # Get current job state
        job = job_manager.get_job(job_id)
        
        if job is None:
            yield f"event: error\ndata: {json.dumps({'error': 'Job not found'})}\n\n"
            break
        
        # Send update if progress changed
        if job.progress != last_progress or job.status != "queued":
            event_data = {
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
                "message": job.message,
                "result_url": job.result_url,
                "error": job.error
            }
            
            yield f"event: progress\ndata: {json.dumps(event_data)}\n\n"
            last_progress = job.progress
        
        # If job is done or error, send final event and close
        if job.status in ["done", "error"]:
            await asyncio.sleep(0.5)  # Small delay to ensure final event is sent
            break
        
        await asyncio.sleep(0.5)  # Poll every 500ms


def create_sse_response(job_id: str, request: Request) -> EventSourceResponse:
    """Create SSE response for job events"""
    return EventSourceResponse(job_event_generator(job_id, request))

