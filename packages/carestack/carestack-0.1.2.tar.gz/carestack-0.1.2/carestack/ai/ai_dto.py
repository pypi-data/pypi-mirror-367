from typing import Any, Optional
from pydantic import BaseModel, Field, RootModel, field_validator


class ProcessDSDto(BaseModel):
    """
    Data Transfer Object for processing discharge summary requests.

    Attributes:
        case_type (str): The type of case (e.g., `inpatient`, `outpatient`). Serialized as `caseType`.
        files (Optional[list[str]]): List of file paths or file identifiers to be processed.
        encrypted_data (Optional[str]): Pre-encrypted data, if available.
        public_key (Optional[str]): Public key for encryption, if required.
    """

    case_type: str = Field(..., alias="caseType")
    files: Optional[list[str]] = None
    encrypted_data: Optional[str] = None
    public_key: Optional[str] = None


class DischargeSummaryResponse(BaseModel):
    """
    Represents the response for a discharge summary generation request.

    Attributes:
        id (str): Unique identifier for the discharge summary.
        discharge_summary (Optional[dict[str, Any]]): The generated discharge summary content, if available.
        extracted_data (dict[str, Any]): Extracted clinical data from the input.
        fhir_bundle (dict[str, Any]): FHIR-compliant bundle generated from the case data.
    """

    id: str
    discharge_summary: Optional[dict[str, Any]] = Field(None, alias="dischargeSummary")
    extracted_data: dict[str, Any] = Field(..., alias="extractedData")
    fhir_bundle: dict[str, Any] = Field(..., alias="fhirBundle")

    @field_validator("discharge_summary", mode="before")
    @classmethod
    def handle_empty_string(cls, value):
        # """
        # Ensures that an empty string or None for `discharge_summary` is converted to None,
        # and only a dictionary is accepted as valid content.
        # """
        if value == "" or value is None:
            return None
        if isinstance(value, dict):
            return value
        raise ValueError("dischargeSummary must be a dictionary or empty string")


class GenerateFhirBundleDto(BaseModel):
    """
    Data Transfer Object for generating a FHIR bundle.

    Attributes:
        case_type (str): The type of case (e.g., `inpatient`, `outpatient`). Serialized as `caseType`.
        record_id (Optional[str]): Identifier for the record, if available. Serialized as `recordId`.
        extracted_data (Optional[dict[str, Any]]): Extracted clinical data for the bundle.
        encrypted_data (Optional[str]): Pre-encrypted data, if available.
        public_key (Optional[str]): Public key for encryption, if required.
    """

    case_type: str = Field(..., alias="caseType")
    record_id: Optional[str] = Field(None, alias="recordId")
    extracted_data: Optional[dict[str, Any]] = Field(None, alias="extractedData")
    encrypted_data: Optional[str] = Field(None, alias="encryptedData")
    public_key: Optional[str] = Field(None, alias="publicKey")


class FhirBundleResponse(RootModel[dict[str, Any]]):
    """
    Represents the response for a FHIR bundle generation request.

    The root model is a dictionary containing the FHIR bundle content.
    """

    pass
