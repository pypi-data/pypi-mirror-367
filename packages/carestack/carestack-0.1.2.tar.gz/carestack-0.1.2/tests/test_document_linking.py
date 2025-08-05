import os
import uuid
from typing import Any, cast
from src.document_linking.document_dto.create_care_context_dto import (
    CreateCareContextDTO,
)
from pydantic import ValidationError
import pytest
from src.common.enums import AppointmentPriority, HealthInformationTypes
from src.document_linking.document_dto.health_document_linking_dto import (
    HealthDocumentLinkingDTO,
)
from src.document_linking.document_dto.health_information_dto import (
    HealthInformationDTO,
)
from src.document_linking.document_linking import DocumentLinking
from src.document_linking.document_dto.appointment_dto import AppointmentDTO
from src.base.base_types import ClientConfig
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def mock_document_linking() -> DocumentLinking:
    api_key = os.getenv("API_KEY")
    api_url = os.getenv("API_URL")

    if not api_key or not api_url:
        raise ValueError(
            "Missing required environment variables for API configuration."
        )
    config = ClientConfig(api_key=api_key, api_url=api_url)
    return DocumentLinking(config)


@pytest.fixture
def valid_uuid() -> str:
    """Fixture to generate a valid UUID string."""
    return str(uuid.uuid4())


def create_health_info_dto() -> HealthInformationDTO:
    """Helper function to create a HealthInformationDTO with default values."""
    return HealthInformationDTO(
        rawFhir=False,
        fhirDocument=None,
        informationType=HealthInformationTypes.OPConsultation,
        dto={"medications": [], "conditions": []},
    )


def create_health_document_linking_dto(**kwargs) -> HealthDocumentLinkingDTO:
    """Helper function to create a HealthDocumentLinkingDTO with default values."""
    default_data = {
        "patientReference": str(uuid.uuid4()),  # Generate a valid UUID
        "practitionerReference": str(uuid.uuid4()),  # Generate a valid UUID
        "patientAddress": "123 Main St, Springfield, IL",
        "patientName": "John Doe",
        "appointmentStartDate": "2025-02-28T09:00:00Z",
        "appointmentEndDate": "2025-02-28T10:00:00Z",
        "organizationId": "org123",
        "hiType": HealthInformationTypes.OPConsultation,
        "mobileNumber": "+911234567890",
        "healthRecords": [create_health_info_dto()],
    }
    default_data.update(kwargs)
    return HealthDocumentLinkingDTO(**default_data)


@pytest.mark.asyncio
async def test_create_appointment_valid_mapping(
    mock_document_linking: DocumentLinking,
) -> None:
    """Test case: Valid mapping of all fields from HealthDocumentLinkingDTO to AppointmentDTO."""
    input_data = create_health_document_linking_dto(
        appointmentPriority="EMERGENCY",
        appointmentSlot="slot123",
        reference="ref123",
        patientAbhaAddress="sbx@sbx",
    )
    appointment_dto: AppointmentDTO = await mock_document_linking._create_appointment(
        input_data
    )

    assert (
        str(appointment_dto.practitioner_reference) == input_data.practitioner_reference
    )
    assert str(appointment_dto.patient_reference) == input_data.patient_reference
    assert appointment_dto.start == input_data.appointment_start_date
    assert appointment_dto.end == input_data.appointment_end_date
    assert appointment_dto.priority == input_data.appointment_priority
    assert appointment_dto.slot == input_data.appointment_slot
    assert appointment_dto.reference == input_data.reference
    assert appointment_dto.organization_id == input_data.organization_id
    assert appointment_dto.slot == input_data.appointment_slot


@pytest.mark.asyncio
async def test_create_appointment_required_fields_present(
    mock_document_linking: DocumentLinking,
) -> None:
    """Test case: Check for the presence of required fields."""
    input_data = create_health_document_linking_dto()
    appointment_dto = await mock_document_linking._create_appointment(input_data)

    assert appointment_dto.practitioner_reference is not None
    assert appointment_dto.patient_reference is not None
    assert appointment_dto.start is not None
    assert appointment_dto.end is not None
    assert appointment_dto.organization_id is not None


@pytest.mark.asyncio
async def test_create_appointment_default_values(
    mock_document_linking: DocumentLinking,
) -> None:
    """Test case: Check for default values of priority."""
    input_data = create_health_document_linking_dto()
    appointment_dto = await mock_document_linking._create_appointment(input_data)

    assert appointment_dto.priority == AppointmentPriority.EMERGENCY


@pytest.mark.asyncio
async def test_create_appointment_invalid_input(
    mock_document_linking: DocumentLinking,
) -> None:
    """Test case: Invalid input (missing required fields)."""
    with pytest.raises(ValueError, match="Input data cannot be null") as exc_info:
        await mock_document_linking._create_appointment(cast(Any, None))
    assert "Input data cannot be null" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_appointment_invalid_data(
    mock_document_linking: DocumentLinking,
) -> None:
    """Test case: Invalid data (empty required fields)."""
    with pytest.raises(ValidationError) as exc_info:
        input_data = HealthDocumentLinkingDTO(
            patientReference="",
            practitionerReference="",
            patientAddress="123 Main St, Springfield, IL",
            patientName="John Doe",
            appointmentStartDate="",
            appointmentEndDate="",
            organizationId="",
            hiType=HealthInformationTypes.OPConsultation,
            mobileNumber="+911234567890",
            healthRecords=[create_health_info_dto()],
            appointmentPriority=None,
            appointmentSlot=None,
            reference=None,
            patientAbhaAddress=None,
        )
        await mock_document_linking._create_appointment(input_data)
    assert "5 validation errors for HealthDocumentLinkingDTO" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_care_context_valid_mapping(
    mock_document_linking: DocumentLinking, valid_uuid: str
) -> None:
    """Test case: Valid mapping of all fields from HealthDocumentLinkingDTO to CreateCareContextDTO."""
    input_data = create_health_document_linking_dto()
    appointment_response = {
        "resourceId": valid_uuid,
        "start": "2025-02-28T09:00:00Z",
        "end": "2025-02-28T10:00:00Z",
    }

    care_context_dto: CreateCareContextDTO = (
        await mock_document_linking._create_care_context(
            input_data,
            appointment_response,
        )
    )

    assert str(care_context_dto.patient_reference) == input_data.patient_reference
    assert (
        str(care_context_dto.practitioner_reference)
        == input_data.practitioner_reference
    )
    assert care_context_dto.appointment_reference == appointment_response["resourceId"]
    assert care_context_dto.hi_type == input_data.hi_type
    assert care_context_dto.patient_abha_address == input_data.patient_abha_address


@pytest.mark.asyncio
async def test_create_care_context_required_fields_present(
    mock_document_linking: DocumentLinking, valid_uuid: str
) -> None:
    """Test case: Check for the presence of required fields in CreateCareContextDTO."""
    input_data = create_health_document_linking_dto()
    appointment_response = {
        "resourceId": valid_uuid,
        "start": "2025-02-28T09:00:00Z",
        "end": "2025-02-28T10:00:00Z",
    }

    care_context_dto: CreateCareContextDTO = (
        await mock_document_linking._create_care_context(
            input_data, appointment_response
        )
    )

    assert care_context_dto.patient_reference is not None
    assert care_context_dto.practitioner_reference is not None
    assert care_context_dto.appointment_reference is not None
    assert care_context_dto.hi_type is not None
    assert care_context_dto.appointment_date is not None


@pytest.mark.asyncio
async def test_create_care_context_invalid_input(
    mock_document_linking: DocumentLinking,
) -> None:
    """Test case: Invalid input (missing required fields)."""
    with pytest.raises(ValueError, match="Input data cannot be null") as exc_info:
        await mock_document_linking._create_care_context(cast(Any, None), {})
    assert "Input data cannot be null" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_care_context_invalid_data(
    mock_document_linking: DocumentLinking, valid_uuid: str
) -> None:
    """Test case: Invalid data (empty required fields)."""
    with pytest.raises(ValidationError) as exc_info:
        input_data = HealthDocumentLinkingDTO(
            patientReference="",
            practitionerReference="",
            patientAddress="123 Main St, Springfield, IL",
            patientName="John Doe",
            appointmentStartDate="",
            appointmentEndDate="",
            organizationId="org123",
            hiType=HealthInformationTypes.OPConsultation,
            mobileNumber="+911234567890",
            healthRecords=[create_health_info_dto()],
            appointmentPriority=None,  # Optional, so None is valid
            appointmentSlot=None,  # Optional, so None is valid
            reference=None,  # Optional, so None is valid
            patientAbhaAddress=None,
        )
        appointment_response = {
            "resourceId": valid_uuid,
            "start": "2025-02-28T09:00:00Z",
            "end": "2025-02-28T10:00:00Z",
        }
        await mock_document_linking._create_care_context(
            input_data,
            appointment_response,
        )
    assert "4 validation errors for HealthDocumentLinkingDTO" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_care_context_invalid_uuid(
    mock_document_linking: DocumentLinking, valid_uuid: str
) -> None:
    """Test case: Invalid UUIDs in input data."""
    input_data = create_health_document_linking_dto(
        patientReference="invalid-uuid", practitionerReference="invalid-uuid"
    )
    appointment_response = {
        "resourceId": valid_uuid,
        "start": "2025-02-28T09:00:00Z",
        "end": "2025-02-28T10:00:00Z",
    }
    with pytest.raises(ValueError) as exc_info:
        await mock_document_linking._create_care_context(
            input_data,
            appointment_response,
        )
    assert "patientReference must be a valid 36-character UUID" in str(exc_info.value)
