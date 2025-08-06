import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

from carestack.ai.ai_dto import DischargeSummaryResponse, FhirBundleResponse
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.encounter.dto.encounter_dto import (
    EncounterRequestDTO,
    OPConsultationDTO,
    DischargeSummaryDTO,
    OPConsultationSections,
    DischargeSummarySections,
    PatientDetails,
    DoctorDetails,
    VitalSign,
    InvestigationItem,
)
from carestack.encounter.encounter_service import Encounter
from carestack.common.enums import CaseType, AI_ENDPOINTS
from carestack.common.config_test import client_config


@pytest.fixture
def encounter_service(client_config: ClientConfig) -> Encounter:
    """Fixture for Encounter service instance."""
    with patch("carestack.encounter.encounter_service.AiUtilities") as mock_utilities:
        service = Encounter(client_config)
        service.utilities = mock_utilities.return_value
        return service


@pytest.fixture
def sample_vital_sign() -> VitalSign:
    """Sample vital sign for testing."""
    return VitalSign(value="120", unit="mmHg")


@pytest.fixture
def sample_patient_details() -> PatientDetails:
    """Sample patient details for testing."""
    return PatientDetails(
        name="John Doe",
        age="45",
        sex="Male",
        date_of_birth="1978-05-15",
        date_of_admission="2023-10-26",
        address="123 Main St, City",
        contact_number="555-1234",
        uhid="UHID123456",
        ip_number="IP789",
        marital_status="Married",
    )


@pytest.fixture
def sample_doctor_details() -> list[DoctorDetails]:
    """Sample doctor details for testing."""
    return [
        DoctorDetails(
            name="Dr. Smith", designation="Senior Consultant", department="Cardiology"
        ),
        DoctorDetails(
            name="Dr. Johnson", designation="Resident", department="Internal Medicine"
        ),
    ]


@pytest.fixture
def sample_investigation_item(sample_vital_sign: VitalSign) -> InvestigationItem:
    """Sample investigation item for testing."""
    return InvestigationItem(
        observations={"blood_glucose": sample_vital_sign},
        status="completed",
        recordedDate="2023-10-26",
    )


@pytest.fixture
def sample_op_consultation_sections(
    sample_patient_details: PatientDetails,
    sample_doctor_details: list[DoctorDetails],
) -> OPConsultationSections:
    """Sample OP consultation sections for testing."""
    return OPConsultationSections(
        patient_details=sample_patient_details,
        doctor_details=sample_doctor_details,
        chief_complaints="Chest pain and shortness of breath",
        medical_history=None,
        family_history=None,
        condtions=["Hypertension"],
        current_procedures=None,
        current_medications=["Lisinopril 10mg"],
        prescribed_medications=["Aspirin 81mg"],
        allergies=["Penicillin"],
        immunizations=["COVID-19"],
        advisory_notes=["Follow up in 2 weeks"],
        care_plan=["Lifestyle modifications"],
        follow_up=["Cardiology consultation"],
    )


@pytest.fixture
def sample_discharge_summary_sections(
    sample_patient_details: PatientDetails,
    sample_doctor_details: list[DoctorDetails],
    sample_investigation_item: InvestigationItem,
) -> DischargeSummarySections:
    """Sample discharge summary sections for testing."""
    return DischargeSummarySections(
        patient_details=sample_patient_details,
        doctor_details=sample_doctor_details,
        chief_complaints="Acute chest pain",
        investigations=sample_investigation_item,
        medical_history=None,
        family_history=None,
        condtions=["Acute MI"],
        current_procedures=None,
        current_medications=["Metoprolol"],
        prescribed_medications=["Atorvastatin"],
        allergies=None,
        immunizations=None,
        advisory_notes=["Cardiac rehabilitation"],
        care_plan=["Medication compliance"],
        follow_up=["Cardiology follow-up"],
    )


@pytest.fixture
def sample_op_consultation_dto_with_payload(
    sample_op_consultation_sections: OPConsultationSections,
) -> OPConsultationDTO:
    """Sample OP consultation DTO with payload."""
    return OPConsultationDTO(case_sheets=None, payload=sample_op_consultation_sections)


@pytest.fixture
def sample_op_consultation_dto_with_files() -> OPConsultationDTO:
    """Sample OP consultation DTO with case sheets."""
    return OPConsultationDTO(
        case_sheets=["case_sheet_1.pdf", "case_sheet_2.pdf"], payload=None
    )


@pytest.fixture
def sample_discharge_summary_dto_with_payload(
    sample_discharge_summary_sections: DischargeSummarySections,
) -> DischargeSummaryDTO:
    """Sample discharge summary DTO with payload."""
    return DischargeSummaryDTO(
        case_sheets=None, payload=sample_discharge_summary_sections
    )


@pytest.fixture
def sample_discharge_summary_dto_with_files() -> DischargeSummaryDTO:
    """Sample discharge summary DTO with case sheets."""
    return DischargeSummaryDTO(
        case_sheets=["discharge_sheet_1.pdf", "discharge_sheet_2.pdf"], payload=None
    )


@pytest.fixture
def sample_encounter_request_dto_with_payload(
    sample_op_consultation_dto_with_payload: OPConsultationDTO,
) -> EncounterRequestDTO:
    """Sample encounter request DTO with payload."""
    return EncounterRequestDTO(
        case_type=CaseType.OP_CONSULTATION,
        lab_reports=["lab_report_1.pdf", "lab_report_2.pdf"],
        dto=OPConsultationDTO(
            payload={
                "patient_details": {"name": "John"},
                "doctor_details": {
                    "name": "Dr. Smith",
                    "designation": "Cardiologist",
                    "department": "Cardiology",
                },
            }
        ),
    )


@pytest.fixture
def sample_encounter_request_dto_with_files(
    sample_discharge_summary_dto_with_files: DischargeSummaryDTO,
) -> EncounterRequestDTO:
    """Sample encounter request DTO with case sheets."""
    return EncounterRequestDTO(
        case_type=CaseType.DISCHARGE_SUMMARY,
        lab_reports=["lab_report_1.pdf"],
        dto=sample_discharge_summary_dto_with_files,
    )


@pytest.fixture
def sample_fhir_bundle() -> dict[str, Any]:
    """Sample FHIR bundle response."""
    return {
        "resourceType": "Bundle",
        "type": "document",
        "id": "bundle-123",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-123",
                    "name": [{"given": ["John"], "family": "Doe"}],
                    "gender": "male",
                    "birthDate": "1978-05-15",
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "encounter-123",
                    "status": "finished",
                    "subject": {"reference": "Patient/patient-123"},
                }
            },
        ],
    }


@pytest.fixture
def sample_discharge_summary_response() -> DischargeSummaryResponse:
    """Sample discharge summary response."""
    return DischargeSummaryResponse(
        id="summary-123",
        dischargeSummary={
            "patientName": "John Doe",
            "diagnosis": "Acute Myocardial Infarction",
            "treatment": "PCI with stent placement",
            "outcome": "Stable condition",
        },
        extracted_data={
            "patient": {"name": "John Doe", "age": 45, "gender": "Male"},
            "diagnosis": ["Acute MI"],
            "procedures": ["PCI"],
            "medications": ["Aspirin", "Metoprolol"],
        },
        fhir_bundle={},
    )


@pytest.fixture
def sample_fhir_bundle_response(
    sample_fhir_bundle: dict[str, Any],
) -> FhirBundleResponse:
    """Sample FHIR bundle response object."""
    mock_response = MagicMock()
    mock_response.root = sample_fhir_bundle
    return mock_response


class TestEncounterServiceValidation:
    """Test cases for validation methods."""

    def test_validate_request_data_success_with_case_sheets(
        self, encounter_service: Encounter
    ):
        """Test successful validation with case sheets."""
        dto = {"caseSheets": ["sheet1.pdf"]}

        # Should not raise any exception
        encounter_service._validate_request_data(dto)

    def test_validate_request_data_success_with_payload(
        self, encounter_service: Encounter
    ):
        """Test successful validation with payload."""
        dto = {"payload": {"patient_details": "data"}}

        # Should not raise any exception
        encounter_service._validate_request_data(dto)

    def test_validate_request_data_success_with_both(
        self, encounter_service: Encounter
    ):
        """Test successful validation with both case sheets and payload."""
        dto = {"caseSheets": ["sheet1.pdf"], "payload": {"patient_details": "data"}}

        # Should not raise any exception
        encounter_service._validate_request_data(dto)

    def test_validate_request_data_failure_no_data(self, encounter_service: Encounter):
        """Test validation failure when no data provided."""
        dto = {}

        with pytest.raises(ValueError) as exc_info:
            encounter_service._validate_request_data(dto)

        assert "No case_sheets or payload provided" in str(exc_info.value)

    def test_validate_request_data_failure_empty_case_sheets(
        self, encounter_service: Encounter
    ):
        """Test validation failure with empty case sheets."""
        dto = {"caseSheets": []}

        with pytest.raises(ValueError) as exc_info:
            encounter_service._validate_request_data(dto)

        assert "No case_sheets or payload provided" in str(exc_info.value)

    def test_validate_request_data_failure_none_payload(
        self, encounter_service: Encounter
    ):
        """Test validation failure with None payload."""
        dto = {"payload": None}

        with pytest.raises(ValueError) as exc_info:
            encounter_service._validate_request_data(dto)

        assert "No case_sheets or payload provided" in str(exc_info.value)


class TestEncounterServiceGenerateFhirFromFiles:
    """Test cases for generate_fhir_from_files method."""

    @pytest.mark.asyncio
    async def test_generate_fhir_from_files_exception_handling(
        self, encounter_service: Encounter
    ):
        """Test exception handling in generate_fhir_from_files."""
        case_sheets = ["sheet1.pdf"]
        document_references = ["doc_ref_1", "doc_ref_2"]
        encounter_service.utilities.encryption = AsyncMock(
            side_effect=Exception("Encryption failed")
        )

        with pytest.raises(Exception) as exc_info:
            await encounter_service.generate_fhir_from_files(
                CaseType.DISCHARGE_SUMMARY.value, case_sheets, document_references, None
            )

        assert "Encryption failed" in str(exc_info.value)


class TestEncounterServiceGenerateDischargeSummary:
    """Test cases for generate_discharge_summary method."""

    @pytest.mark.asyncio
    async def test_generate_discharge_summary_api_error(
        self, encounter_service: Encounter
    ):
        """Test API error handling in discharge summary generation."""
        encrypted_data = {"files": ["encrypted_data"]}
        error = EhrApiError("API failed", 500)
        encounter_service.post = AsyncMock(side_effect=error)

        with pytest.raises(EhrApiError) as exc_info:
            await encounter_service.generate_discharge_summary(
                CaseType.DISCHARGE_SUMMARY.value, encrypted_data
            )

        assert exc_info.value == error


# Additional fixtures for comprehensive testing
@pytest.fixture
def sample_get_appointment_response():
    """Mock GetAppointmentResponse for compatibility with existing test pattern."""
    mock_response = MagicMock()
    mock_response.type = "success"
    mock_response.message = "Appointments retrieved successfully"
    mock_response.total_records = 1
    mock_response.next_page = None
    return mock_response
