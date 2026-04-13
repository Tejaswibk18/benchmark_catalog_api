from fastapi import APIRouter

from app.schemas.job_schema import JobStatusUpdate
from app.services.job_service import (
    update_job_status_service,
    get_jobs_summary_service
)

from app.utils.response import success_response, error_response

router = APIRouter(prefix="/job-details", tags=["Job Details"])


# -------------------------------
# UPDATE JOB STATUS
# -------------------------------
@router.patch("/{job_id}/status")
def update_job_status(job_id: str, payload: JobStatusUpdate):
    try:
        data = update_job_status_service(job_id, payload.status)
        return success_response("job status updated", data, 200)
    except Exception as e:
        return error_response(str(e), 500)


# -------------------------------
# GET ALL JOBS (ID + STATUS)
# -------------------------------
@router.get("")
def get_jobs_summary():
    try:
        data = get_jobs_summary_service()
        return success_response("jobs fetched", data, 200)
    except Exception as e:
        return error_response(str(e), 500)