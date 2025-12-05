import pytest
from fastapi.testclient import TestClient
from app import app
import time
import os

client = TestClient(app)


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_models():
    """Test listing available models"""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0


def test_generate_smoke():
    """Smoke test: create a generation job with short duration"""
    # Create job
    response = client.post(
        "/api/generate",
        json={
            "model": "musicgen-small",
            "prompt": "test prompt for smoke test",
            "duration": 2,
            "seed": 42,
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "job_id" in data
    job_id = data["job_id"]
    assert data["status"] == "queued"
    
    # Poll for completion (with timeout)
    max_wait = 60  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        job_data = response.json()
        
        status = job_data["status"]
        
        if status == "done":
            # Verify file exists
            assert "result_url" in job_data
            assert job_data["result_url"] is not None
            
            # Try to download file
            filename = job_data["result_url"].split("/")[-1]
            file_response = client.get(f"/api/files/{filename}")
            assert file_response.status_code == 200
            assert len(file_response.content) > 0
            
            return  # Success
        
        elif status == "error":
            pytest.fail(f"Job failed: {job_data.get('error', 'Unknown error')}")
        
        time.sleep(1)
    
    pytest.fail(f"Job did not complete within {max_wait} seconds")

