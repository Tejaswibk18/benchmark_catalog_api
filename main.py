from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.benchmark_routes import router

app = FastAPI(
    title="Benchmark Catalog API",
    version="1.0"
)

app.include_router(router)


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




# from fastapi import FastAPI
# from app.routes.benchmark_routes import router

# app = FastAPI()

# app.include_router(router)