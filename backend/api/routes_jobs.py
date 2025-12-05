from fastapi import APIRouter, HTTPException
from core.jobs import job_manager, Job
from core.sse import create_sse_response
from fastapi import Request

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and progress"""
    job = job_manager.get_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "message": job.message,
        "result_url": job.result_url,
        "error": job.error,
        "params": job.params,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


@router.get("/jobs/{job_id}/events")
async def stream_job_events(job_id: str, request: Request):
    """Stream job progress via Server-Sent Events"""
    job = job_manager.get_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return create_sse_response(job_id, request)

