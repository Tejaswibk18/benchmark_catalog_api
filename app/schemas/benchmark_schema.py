from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import FieldValidationInfo
from typing import List, Optional, Dict
import re


class Scripts(BaseModel):

    sut_teardown: str
    sut_setup: str
    lts_teardown: Optional[str] = None
    lts_setup: Optional[str] = None

    @field_validator("sut_teardown", "sut_setup")
    @classmethod
    def validate_scripts(cls, value, info: FieldValidationInfo):
        if not value or not value.strip():
            raise ValueError(f"{info.field_name} is missing")
        return value


class SutLtsConfig(BaseModel):

    sut: str
    lts: str

    @field_validator("sut", "lts")
    @classmethod
    def validate_os(cls, value):
        if value not in ["windows", "linux"]:
            raise ValueError("sut and lts must be either windows or linux")
        return value


class BenchmarkCreate(BaseModel):

    catalog_name: str
    benchmark_name: str
    benchmark_category: str
    description: Optional[str] = None
    scripts: Scripts
    run_parameters: Dict[str, Optional[Dict]]
    metrics: List[str]
    tags: Optional[List[str]] = None
    enable_lts_mode: bool = False
    sut_lts_config: Optional[SutLtsConfig] = None
    visibility: str

    @field_validator("catalog_name", "benchmark_name", "benchmark_category")
    @classmethod
    def validate_names(cls, value, info: FieldValidationInfo):
        if not value or not value.strip():
            raise ValueError(f"{info.field_name} is missing")
        if not re.fullmatch(r"[A-Za-z_]+", value):
            raise ValueError(f"{info.field_name} must contain only alphabets and underscore")
        return value

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, value):
        if not value or not value.strip():
            raise ValueError("visibility is missing")
        if value not in ["Public", "Private"]:
            raise ValueError("visibility must be Public or Private")
        return value

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, value):
        if not value:
            raise ValueError("metrics cannot be empty")
        if any(not m.strip() for m in value):
            raise ValueError("metrics cannot contain empty values")
        return value

    @field_validator("run_parameters")
    @classmethod
    def validate_run_parameters(cls, value):
        if not isinstance(value, dict) or not value.keys():
            raise ValueError("run_parameters must contain keys")
        return value

    @model_validator(mode="after")
    def validate_lts_mode(self):

        if self.enable_lts_mode:

            if not self.sut_lts_config:
                raise ValueError("sut_lts_config required when enable_lts_mode is true")

            if not self.scripts.lts_setup or not self.scripts.lts_teardown:
                raise ValueError("lts_setup and lts_teardown required when enable_lts_mode is true")

        return self
    

class BenchmarkPatch(BaseModel):

    catalog_name: Optional[str] = None
    benchmark_name: Optional[str] = None
    benchmark_category: Optional[str] = None
    description: Optional[str] = None
    scripts: Optional[Scripts] = None
    run_parameters: Optional[Dict] = None
    metrics: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    enable_lts_mode: Optional[bool] = None
    sut_lts_config: Optional[SutLtsConfig] = None
    visibility: Optional[str] = None
    status: Optional[str] = Field(...)