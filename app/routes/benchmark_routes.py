from fastapi import APIRouter, Query, Body, Depends

from app.auth.jwt_handler import create_token
from fastapi import APIRouter
from app.services.ai_service import validate_benchmark
from app.services.ai_service import generate_benchmark_from_text
from app.services.ai_service import auto_fix_benchmark

from app.auth.auth_dependency import get_current_user
from app.services.benchmark_service import (
    get_benchmarks,
    create_benchmark,
    update_benchmark_service,
    patch_benchmark_service,
    delete_benchmark_service
)

from app.schemas.benchmark_schema import BenchmarkCreate, BenchmarkPatch
from app.utils.response import success_response, error_response


router = APIRouter(tags=["Benchmark"])


# @router.post("/ai-validate")
# async def ai_validate(payload: dict):

#     result = validate_benchmark(payload)

#     return {
#         "status": "success",
#         "message": "AI validation completed",
#         "status_code": 200,
#         "data": result
#     }


# @router.post("/generate-benchmark")
# async def generate_benchmark(payload: dict):

#     prompt = payload.get("prompt")

#     result = generate_benchmark_from_text(prompt)

#     return {
#         "status": "success",
#         "message": "Benchmark generated using AI",
#         "status_code": 200,
#         "data": result
#     }


# @router.post("/ai-fix")
# def ai_fix(payload: dict):

#     try:

#         result = auto_fix_benchmark(payload)

#         return success_response(
#             "AI auto-fix completed",
#             result,
#             200
#         )

#     except Exception:
#         return error_response("internal server error", 500)


@router.post("/benchmark")
def create(payload: BenchmarkCreate):

    try:

        data = create_benchmark(payload)

        return success_response(
            "benchmark created",
            data,
            201
        )

    except Exception as e:
        return error_response(str(e), 400)
    


@router.get("/generate-token")
def generate_token():

    token = create_token({
        "user": "admin"
    })

    return {
        "status": "success",
        "message": "token generated",
        "status_code": 200,
        "data": {
            "token": token
        }
    }

@router.get("/benchmark")
def get_all_benchmarks(
    id: str | None = Query(None),
    benchmark_name: str | None = Query(None),
    benchmark_category: str | None = Query(None)
):

    try:

        data = get_benchmarks(id, benchmark_name, benchmark_category)

        return success_response(
            "benchmarks fetched successfully",
            data,
            200
        )

    except Exception as e:
        return error_response(str(e), 400)


@router.put("/benchmark/{id}")
def update_benchmark_api(
        id: str,
        payload: BenchmarkCreate = Body(...)
):

    try:

        data = update_benchmark_service(id, payload)

        return success_response(
            "benchmark updated successfully",
            data,
            200
        )

    except ValueError as e:
        return error_response(str(e), 400)

    except Exception:
        return error_response("internal server error", 500)


SECURE_STATUS = ["APPROVED", "REJECTED", "PUBLISHED"]


@router.patch("/benchmark/{id}")
def patch_benchmark_api(
        id: str,
        payload: BenchmarkPatch,
        user: dict = Depends(get_current_user)  # optional auth
):

    try:

        status = payload.status if hasattr(payload, "status") else None

        # if status requires auth and no token provided
        if status in SECURE_STATUS and not user:
            return error_response(
                "authentication required for this status change",
                403
            )

        username = user.get("user", "system") if user else "system"

        data = patch_benchmark_service(id, payload, username)

        return success_response(
            "benchmark updated successfully",
            data,
            200
        )

    except ValueError as e:
        return error_response(str(e), 400)

    except Exception:
        return error_response("internal server error", 500)

@router.delete("/benchmark/{id}")
def delete_benchmark_api(id: str, user=Depends(get_current_user)):

    try:

        data = delete_benchmark_service(id, user["email"])

        return success_response(
            "benchmark archived successfully",
            data,
            200
        )

    except ValueError as e:
        return error_response(str(e), 400)

    except Exception as e:
        return error_response(str(e), 500)