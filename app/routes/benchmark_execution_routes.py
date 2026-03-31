from fastapi import APIRouter, Query

from app.schemas.benchmark_execution_schema import (
    BenchmarkExecutionCreate,
    BenchmarkExecutionPatch
)

from app.services.benchmark_execution_service import (
    create_benchmark_execution_service,
    get_benchmark_execution_service,
    patch_benchmark_execution_service,
    delete_benchmark_execution_service
)

from app.utils.response import success_response, error_response

router = APIRouter(prefix="/benchmark-execution", tags=["Benchmark Execution"])


@router.post("")
def create_execution(payload: BenchmarkExecutionCreate):
    try:
        data = create_benchmark_execution_service(payload)
        return success_response("execution created", data, 201)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


@router.get("")
def get_execution(
    id: str | None = Query(None),
    benchmark_name: str | None = Query(None),
    benchmark_category: str | None = Query(None)
):
    try:
        data = get_benchmark_execution_service(id, benchmark_name, benchmark_category)
        return success_response("execution fetched", data, 200)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


@router.patch("/{id}")
def patch_execution(id: str, payload: BenchmarkExecutionPatch):
    try:
        data = patch_benchmark_execution_service(id, payload)
        return success_response("execution updated", data, 200)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


@router.delete("/{id}")
def delete_execution(id: str):
    try:
        data = delete_benchmark_execution_service(id)
        return success_response("execution deleted", data, 200)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)
    


# from fastapi import APIRouter, Body

# from app.services.ai_service import generate_workflow_from_prompt
# from app.schemas.benchmark_execution_schema import BenchmarkExecutionCreate
# from app.utils.response import success_response, error_response

# router = APIRouter(prefix="/ai", tags=["AI"])


# @router.post("/generate-workflow")
# def generate_workflow(payload: dict = Body(...)):

#     prompt = payload.get("prompt")

#     if not prompt:
#         return error_response("prompt is required", 400)

#     try:
#         # -------------------------------
#         # GENERATE FROM AI
#         # -------------------------------
#         result = generate_workflow_from_prompt(prompt)

#         # -------------------------------
#         # VALIDATE USING YOUR SCHEMA
#         # -------------------------------
#         validated = BenchmarkExecutionCreate(**result)

#         return success_response(
#             "workflow generated successfully",
#             validated.dict(),
#             200
#         )

#     except Exception as e:
#         return error_response(str(e), 500)