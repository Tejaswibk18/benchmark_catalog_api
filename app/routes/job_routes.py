from fastapi import APIRouter
from fastapi import Query
from app.schemas.job_schema import JobResultPayload , JobStatusUpdate


from app.services.job_service import (
    update_job_status_service,
    get_jobs_summary_service,
    get_job_by_id_service,
    update_job_result_service
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
    

@router.patch("/{job_id}/result")
def update_job_result(job_id: str, payload: JobResultPayload):
    try:
        data = update_job_result_service(job_id, payload)
        return success_response("job result updated", data, 200)
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
    
# -------------------------------
# GET JOB BY ID
# -------------------------------
@router.get("")
def get_jobs(job_id: str | None = Query(None)):
    try:
        data = get_job_by_id_service(job_id)
        return success_response("job(s) fetched", data, 200)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)
