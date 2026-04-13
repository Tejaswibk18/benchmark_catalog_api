from pydantic import BaseModel


class JobStatusUpdate(BaseModel):
    status: str


class JobResponse(BaseModel):
    id: str
    status: str