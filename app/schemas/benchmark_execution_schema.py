from pydantic import BaseModel, field_validator, model_validator
from typing import List, Dict, Any
from datetime import datetime
import re


# -------------------------------
# COMMON VALIDATOR
# -------------------------------
def validate_required_text(value: str, field_name: str):
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} cannot be empty")

    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise ValueError(
            f"{field_name} must contain only alphabets, numbers and underscore"
        )

    return value


# -------------------------------
# EXECUTOR
# -------------------------------
class Executor(BaseModel):
    type: str
    protocol: str
    target: str
    timeout_sec: int
    retry: int

    method: str | None = None
    url: str | None = None
    auth_ref: str | None = None
    command: str | None = None
    script_path: str | None = None

    @field_validator("type", "protocol", "target")
    def validate_executor(cls, v, info):
        return validate_required_text(v, info.field_name)


# -------------------------------
# PARAMETER SCHEMA
# -------------------------------
class ParameterSchema(BaseModel):
    data_type: str
    required: bool
    default: Any
    label: str


# -------------------------------
# PARAMETERS (STRUCTURED)
# -------------------------------
class Parameters(BaseModel):
    action: str | None = None
    sut_ids: List[str] | None = None
    user_email: str | None = None
    script_path: str | None = None
    run_configs: Dict[str, Any] | None = None


# -------------------------------
# STAGE
# -------------------------------
class Stage(BaseModel):
    stage_type: str
    stage_name: str
    stage_order: int

    task_type: str
    task_name: str
    task_order: int

    executor: Executor

    parameters: Parameters
    parameters_schema: Dict[str, ParameterSchema]

    visibility: List[str]
    target_sut: List[str]

    @field_validator("stage_type", "stage_name", "task_type", "task_name")
    def validate_stage(cls, v, info):
        return validate_required_text(v, info.field_name)


# -------------------------------
# WORKFLOW
# -------------------------------
class Workflow(BaseModel):
    stages: List[Stage]


# -------------------------------
# SCHEDULE
# -------------------------------
class ScheduleTest(BaseModel):
    test_name: str

    @field_validator("test_name")
    def validate_test(cls, v):
        return validate_required_text(v, "test_name")


class ScheduleDetails(BaseModel):
    date: datetime
    time: datetime
    no_of_runs: int
    iteration_per_run: int
    cores_per_instance: int


# -------------------------------
# MAIN PAYLOAD
# -------------------------------
class BenchmarkExecutionCreate(BaseModel):
    benchmark_name: str
    benchmark_category: str
    catalog_name: str
    group_id: str
    environment: str

    schedule_test: ScheduleTest
    schedule_details: ScheduleDetails

    no_of_sut: int

    workflow: Workflow

    save_to_workflow_catalog: bool

    #  CONDITIONAL FIELDS
    workflow_name: str | None = None
    workflow_visibility: str | None = None  # PUBLIC / PRIVATE

    custom_tags: List[str]

    # -------------------------------
    # VALIDATIONS
    # -------------------------------
    @field_validator(
        "benchmark_name",
        "benchmark_category",
        "catalog_name",
        "group_id",
        "environment"
    )
    def validate_main_fields(cls, v, info):
        return validate_required_text(v, info.field_name)

    @model_validator(mode="after")
    def validate_workflow_catalog_fields(self):

        if self.save_to_workflow_catalog:
            if not self.workflow_name:
                raise ValueError("workflow_name is required when save_to_workflow_catalog is true")

            if not self.workflow_visibility:
                raise ValueError("workflow_visibility is required when save_to_workflow_catalog is true")

            if self.workflow_visibility not in ["PUBLIC", "PRIVATE" , "public" , "private"]:
                raise ValueError("workflow_visibility must be PUBLIC or PRIVATE")

        return self


# -------------------------------
# PATCH
# -------------------------------
class BenchmarkExecutionPatch(BaseModel):
    benchmark_name: str | None = None
    benchmark_category: str | None = None
    catalog_name: str | None = None
    group_id: str | None = None
    environment: str | None = None
    no_of_sut: int | None = None
    stage_order: int | None = None

    @field_validator(
        "benchmark_name",
        "benchmark_category",
        "catalog_name",
        "group_id",
        "environment"
    )
    def validate_fields(cls, v, info):
        return validate_required_text(v, info.field_name)