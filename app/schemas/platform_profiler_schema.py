from pydantic import BaseModel


class PlatformProfilerResponse(BaseModel):
    benchmark_name: str
    platform_profile: dict
    workload_profile_path: str
    results: dict