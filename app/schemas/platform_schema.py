from pydantic import BaseModel, field_validator
import re


def validate_required_text(value: str, field_name: str):
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} cannot be empty")

    return value


class Network(BaseModel):
    bytes_sent: int
    bytes_received: int


class PlatformCreate(BaseModel):

    server_name: str
    ip_address: str
    os: str

    cpu_usage: float
    memory_usage: float

    network: Network   # nested required

    # -------------------------------
    # VALIDATION
    # -------------------------------
    @field_validator("server_name", "ip_address", "os")
    def validate_fields(cls, v, info):
        return validate_required_text(v, info.field_name)