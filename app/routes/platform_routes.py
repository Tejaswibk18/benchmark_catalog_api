from fastapi import APIRouter
from app.schemas.platform_schema import PlatformCreate
from app.services.platform_service import (
    create_platform_server,
    get_platform_servers_service
)
from app.utils.response import success_response, error_response

router = APIRouter(tags=["Platform Pool"])

from fastapi import Query
from app.services.platform_service import get_platform_servers_service



# -------------------------------
# POST API
# -------------------------------
@router.post("/platform-pool")
def create_server(payload: PlatformCreate):

    try:

        data = create_platform_server(payload)

        return success_response(
            "server added successfully",
            data,
            201
        )

    except Exception as e:
        return error_response(str(e), 500)


# -------------------------------
# GET API
# -------------------------------
@router.get("/platform-pool", tags=["Platform Pool"])
def get_servers(
    id: str | None = Query(None),
    os: str | None = Query(None),
    ip_address: str | None = Query(None),
    server_name: str | None = Query(None)
):

    try:

        data = get_platform_servers_service(
            id,
            os,
            ip_address,
            server_name
        )

        return success_response(
            "servers fetched successfully",
            data,
            200
        )

    except ValueError as e:
        return error_response(str(e), 400)

    except Exception as e:
        return error_response(str(e), 500)