from pydantic import BaseModel
from typing import List, Dict, Optional


class JobStatusUpdate(BaseModel):
    status: str


class SUTResult(BaseModel):
    success: bool
    message: Optional[str] = ""
    error: Optional[str] = ""


class JobResultPayload(BaseModel):
    result: List[Dict[str, SUTResult]]