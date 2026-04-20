from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.benchmark_routes import router
from app.routes.platform_routes import router as platform_router

from app.routes.benchmark_routes import router as benchmark_router
from app.routes.benchmark_execution_routes import router as execution_router
from app.routes.job_routes import router as job_router
from app.routes.platform_profiler_routes import router as profiler_router

app = FastAPI(
    title="Benchmark Catalog API",
    version="1.0"
)

app.include_router(router)
app.include_router(benchmark_router)
app.include_router(execution_router)
app.include_router(platform_router)
app.include_router(job_router)
app.include_router(profiler_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    error_message = exc.errors()[0]["msg"] 

    return JSONResponse(
        status_code=400,
        content={
            "status": "failed",
            "message": error_message,
            "status_code": 400,
            "data": []
        }
    )

