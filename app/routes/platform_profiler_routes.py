from fastapi import APIRouter, UploadFile, File

from app.services.platform_profiler_service import process_platform_profiler_service
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/platform-profiler", tags=["Platform Profiler"])


@router.post("")
def upload_platform_profiler(file: UploadFile = File(...)):
    try:
        data = process_platform_profiler_service(file)
        return success_response("file processed successfully", data, 201)
    except Exception as e:
        return error_response(str(e), 500)