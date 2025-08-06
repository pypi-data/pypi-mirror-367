# FILE: boot/models/spec.py
from __future__ import annotations

from pathlib import Path
import tomllib
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from boot.errors import SpecValidationError


class Project(BaseModel):
    """Defines the [project] section of the spec."""

    name: str
    version: str
    description: str


class Dataset(BaseModel):
    """Defines a model for items in the [[datasets]] list."""

    name: str
    description: str
    schema_or_sample: str = Field(..., alias="schema_or_sample")


class Metric(BaseModel):
    """Defines a model for items in the [[metrics]] list."""

    name: str
    logic: str
    aggregation: str
    aggregation_field: str = Field(..., alias="aggregationField")


class OutputDataset(BaseModel):
    """Defines a model for items in the [[outputDatasets]] list."""

    name: str
    description: str
    schema_or_sample: str = Field(..., alias="schema_or_sample")


class SpexSpecification(BaseModel):
    """
    A strictly validated schema for spec.toml files.
    """

    # Core required fields
    language: str
    project_type: str = Field(..., alias="project_type")
    description: str
    project: Project

    # Optional but structured sections
    datasets: List[Dataset] | None = None
    metrics: List[Metric] | None = None
    output_datasets: List[OutputDataset] | None = Field(None, alias="outputDatasets")

    # Language-specific optional fields
    language_version: str | None = Field(None, alias="language_version")

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @classmethod
    def from_toml(cls, path: Path) -> SpexSpecification:
        """Load and validate a spec.toml file."""
        try:
            with path.open("rb") as f:
                raw_data = tomllib.load(f)
            return cls.model_validate(raw_data)
        except FileNotFoundError as err:
            raise SpecValidationError(f"Specification file not found: {path}") from err
        except tomllib.TOMLDecodeError as err:
            raise SpecValidationError(f"Invalid TOML format in {path}: {err}") from err
        except Exception as err:
            raise SpecValidationError(
                f"Validation failed for spec file {path}: {err}"
            ) from err
