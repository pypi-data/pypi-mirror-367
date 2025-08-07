# FILE: boot/models/spec.py
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import List

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from boot.errors import SpecValidationError


class Project(BaseModel):
    """
    Defines the [project] section of the spec, containing metadata
    about the generated project.
    """

    name: str
    version: str
    description: str


class Dataset(BaseModel):
    """
    Defines a model for an input dataset in the [[datasets]] list,
    describing its structure and purpose.
    """

    name: str
    description: str
    schema_or_sample: str = Field(..., alias="schema_or_sample")


class Metric(BaseModel):
    """
    Defines a model for a business metric in the [[metrics]] list,
    detailing the logic for its calculation.
    """

    name: str
    logic: str
    aggregation: str
    aggregation_field: str = Field(..., alias="aggregationField")


class OutputDataset(BaseModel):
    """
    Defines a model for an output dataset in the [[outputDatasets]] list,
    describing the final data artifact to be produced.
    """

    name: str
    description: str
    schema_or_sample: str = Field(..., alias="schema_or_sample")


class SpexSpecification(BaseModel):
    """
    A strictly validated schema for a `spec.toml` file.

    This class uses Pydantic to ensure that any provided specification, whether
    from a local file or an API, conforms to the required structure before
    the generation process begins. It acts as the single source of truth for
    what constitutes a valid user request.
    """

    # Core required fields that define the project's high-level characteristics.
    language: str
    project_type: str = Field(..., alias="project_type")
    description: str
    project: Project

    # Optional but structured sections for data-centric projects.
    datasets: List[Dataset] | None = None
    metrics: List[Metric] | None = None
    output_datasets: List[OutputDataset] | None = Field(None, alias="outputDatasets")

    # Optional language-specific metadata.
    language_version: str | None = Field(None, alias="language_version")

    model_config = ConfigDict(
        populate_by_name=True,  # Allows using aliases like 'project_type'
    )

    @classmethod
    def from_toml(cls, path: Path) -> SpexSpecification:
        """
        Loads and validates a specification from a local .toml file path.

        Args:
            path: The pathlib.Path object pointing to the spec.toml file.

        Returns:
            An instance of SpexSpecification if validation is successful.

        Raises:
            SpecValidationError: If the file is not found, contains invalid TOML,
                                 or fails Pydantic model validation.
        """
        try:
            content = path.read_text("utf-8")
            return cls.from_toml_content(content)
        except FileNotFoundError as err:
            raise SpecValidationError(f"Specification file not found: {path}") from err
        except Exception as err:
            # Catch errors from from_toml_content and add file path context.
            raise SpecValidationError(
                f"Validation failed for spec file {path}: {err}"
            ) from err

    @classmethod
    def from_toml_content(cls, content: str) -> SpexSpecification:
        """
        Loads and validates a specification from a TOML string.

        This method is used to parse spec content fetched from remote sources,
        like the Community Hub API.

        Args:
            content: A string containing the raw TOML configuration.

        Returns:
            An instance of SpexSpecification if validation is successful.

        Raises:
            SpecValidationError: If the string contains invalid TOML or fails
                                 Pydantic model validation.
        """
        try:
            raw_data = tomllib.loads(content)
            return cls.model_validate(raw_data)
        except tomllib.TOMLDecodeError as err:
            raise SpecValidationError(f"Invalid TOML format: {err}") from err
        except ValidationError as err:
            # Re-raise Pydantic's specific error for better diagnostics.
            raise SpecValidationError(
                f"Specification content is invalid: {err}"
            ) from err
