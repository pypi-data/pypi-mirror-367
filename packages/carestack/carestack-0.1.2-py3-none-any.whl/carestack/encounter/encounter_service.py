import logging
from typing import Any, Optional, Union

from dotenv import load_dotenv

from carestack.ai.ai_dto import DischargeSummaryResponse, FhirBundleResponse
from carestack.ai.ai_utils import AiUtilities
from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import AI_ENDPOINTS
from carestack.encounter.dto.encounter_dto import EncounterRequestDTO

load_dotenv()


class Encounter(BaseService):
    """
    Service for managing healthcare encounters and generating FHIR bundles or discharge summaries.

    This service provides a unified interface to create FHIR bundles or discharge summaries based on provided encounter data.
    It handles validation, encryption, and orchestrates AI-powered healthcare processing endpoints.

    !!! note "Key Features"
        - Validates incoming encounter request data thoroughly.
        - Supports both file-based and payload-based FHIR bundle generation workflows.
        - Handles discharge summary generation from encrypted data.
        - Encrypts sensitive patient data and associated files before transmission.
        - Robust error handling with clear logging for diagnosis.

    Methods:
        create: Creates a FHIR bundle or discharge summary based on encounter data.
        generate_fhir_from_payload: Generates FHIR bundle from clinical payload and optional lab reports.
        generate_fhir_from_files: Generates FHIR bundle from case sheet files and optional lab reports.
        generate_discharge_summary: Calls AI endpoint to generate discharge summary.
        generate_fhir_bundle: Calls AI endpoint to generate FHIR bundle from extracted data and files.

    Args:
        config (ClientConfig): API credentials and settings for service initialization.

    Raises:
        EhrApiError: For validation, API call failures or unexpected errors.

    Example Usage:
        ```
        config = ClientConfig(
            api_base_url="https://api.example.com",
            api_key="your_api_key",
            api_secret="your_api_secret"
        )
        encounter_service = Encounter(config)
        request_body = EncounterRequestDTO(
            case_type="inpatient",
            lab_reports=["report1.pdf", "report2.pdf"],
            dto={
                "caseSheets": ["file1.pdf"],
            }
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.utilities = AiUtilities()

    async def create(self, request_body: EncounterRequestDTO) -> dict[str, Any]:
        """
        Creates a FHIR bundle or discharge summary based on the given encounter data.

        Handles both payload-based and file-based encounter data inputs. Validates input,
        encrypts sensitive components, and calls appropriate AI endpoints.

        Args:
            request_body (EncounterRequestDTO): The encounter request DTO containing case type, data, and optional lab reports.

        ### Returns:
            dict[str, Any]: The generated FHIR bundle or discharge summary as a serializable dictionary.

        Raises:
            EhrApiError: On input validation failure, API errors, or unforeseen exceptions.

        Example:
            ```
            encounter_request = EncounterRequestDTO(
                caseType=CaseType.OP_CONSULTATION,
                dto=OPConsultationDTO(
                    caseSheets=None,
                    payload=OPConsultationSections(
                        patient_details=PatientDetails(name="John Doe", ...),
                        doctor_details=[DoctorDetails(name="Dr. Smith", ...)],
                        chief_complaints="Fever and cough",
                        physical_examination=PhysicalExamination(...),
                        ...
                    )
                ),
                lab_reports=None
            )

            or

            encounter_request = EncounterRequestDTO(
                caseType=CaseType.OP_CONSULTATION,
                lab_reports=["lab_report_1.pdf", "lab_report_2.pdf"],
                dto=InpatientDTO(
                    caseType=InpatientCaseType.SURGERY,
                    caseSheets=["case_sheet_1.pdf", "case_sheet_2.pdf"],
                ),
                lab_reports=["lab_report_1.pdf"]
            )

            response = await encounter_service.create(encounter_request)
            print(response)
            ```

        ### Response:
            Sample Output for the given example:
            {
                "resourceType": "Bundle",
                "type": "document",
                "entry": [...FHIR resources...]
            }
        """
        try:
            case_type = request_body.case_type.value
            dto = request_body.dto.model_dump(by_alias=True, exclude_none=True)

            self._validate_request_data(dto)

            if "payload" in dto and dto["payload"] is not None:
                return await self.generate_fhir_from_payload(
                    case_type, dto["payload"], request_body.lab_reports
                )

            if dto.get("caseSheets"):
                return await self.generate_fhir_from_files(
                    case_type, dto["caseSheets"], request_body.lab_reports
                )

            raise ValueError("Unexpected state in encounter creation.")

        except EhrApiError as e:
            self.logger.error(
                f"EHR API error in FHIR bundle generation: {e.message}", exc_info=True
            )
            raise
        except ValueError as e:
            self.logger.error(
                f"Validation error in FHIR bundle generation: {e}", exc_info=True
            )
            raise EhrApiError(str(e), 422) from e
        except Exception as error:
            self.logger.error(
                f"Unexpected error in generate_fhir_bundle: {error}", exc_info=True
            )
            raise EhrApiError(
                f"An unexpected error occurred while generating FHIR bundle: {error}",
                500,
            ) from error

    def _validate_request_data(self, dto: dict[str, Any]) -> None:
        """
        Validates that the request contains the necessary data.

        Args:
            dto (dict[str, Any]): The DTO dictionary to validate.

        Raises:
            ValueError: If neither caseSheets nor payload is provided.
        """
        has_case_sheets = bool(dto.get("caseSheets"))
        has_payload = "payload" in dto and dto["payload"] is not None

        if not has_case_sheets and not has_payload:
            raise ValueError("No case_sheets or payload provided for the encounter.")

    async def generate_fhir_from_payload(
        self,
        case_type: str,
        payload: dict[str, Any],
        lab_reports: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Generates a FHIR bundle from extracted clinical payload and optional lab reports.

        Encrypts the payload and lab reports, then sends to AI endpoint to compose the FHIR bundle.

        Args:
            case_type (str): The type of clinical case.
            payload (dict[str, Any]): Extracted patient clinical data.
            lab_reports (Optional[list[str]]): Optional encrypted lab report files.

        ### Returns:
            dict[str, Any]: Generated FHIR bundle in dictionary form.

        Raises:
            EhrApiError: On encryption or AI API failure.

        Example:
            ```
            fhir_bundle = await encounter_service._generate_fhir_from_payload(
                caseType="OPConsultation",
                payload={"patient_details": {...}, "doctor_details": [...], "chief_complaints": "fever", ...},
                lab_reports=["encrypted_lab_report_1.pdf"]
            )
            print(fhir_bundle)
            ```

        ### Response:
            Sample Output:
            {
                "resourceType": "Bundle",
                "type": "document",
                "entry": [
                    {...}, {...}
                ]
            }
        """

        encryptedData = await self.utilities.encryption(payload=payload)

        request_payload = {
            "caseType": case_type,
            "encryptedData": encryptedData,
        }

        # If lab reports are provided, encrypt and include them
        if lab_reports:
            encrypted_lab_reports_resp = await self.utilities.encryption(
                payload={"files": lab_reports}
            )
            encrypted_lab_reports = self._normalize_encryption_response(
                encrypted_lab_reports_resp
            )
            request_payload["files"] = encrypted_lab_reports

        return await self.post(
            AI_ENDPOINTS.GENERATE_FHIR_BUNDLE,
            request_payload,
            response_model=dict[str, Any],
        )

    async def generate_fhir_from_files(
        self,
        case_type: str,
        case_sheets: list[str],
        lab_reports: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Generates a FHIR bundle from provided case sheet files and optional lab reports.

        ### Process:
            1. Encrypt case sheet files.
            2. Generate discharge summary from encrypted case sheets.
            3. Encrypt lab reports (if any).
            4. Generate FHIR bundle using extracted data and all encrypted files.

        Args:
            case_type (str): Type of clinical case.
            case_sheets (list[str]): List of case sheet file paths or identifiers.
            lab_reports (Optional[list[str]]): Optional lab report file identifiers.

        ### Returns:
            dict[str, Any]: Generated FHIR bundle.

        Raises:
            EhrApiError: On any failure during encryption or API calls.

        Example:
            ```
            fhir_bundle = await encounter_service._generate_fhir_from_files(
                caseType="Inpatient",
                caseSheets=["case_sheet_1.pdf", "case_sheet_2.pdf"],
                lab_reports=["lab_report_1.pdf"]
            )
            print(fhir_bundle)
            ```

        ### Response:
            Sample Output:
            {
                "resourceType": "Bundle",
                "type": "document",
                "entry": [
                    {...},
                    {...}
                ]
            }
        """
        try:
            # Step 1: Encrypt case sheets
            encrypted_case_sheets_resp = await self.utilities.encryption(
                payload={"files": case_sheets}
            )
            encrypted_case_sheets = self._normalize_encryption_response(
                encrypted_case_sheets_resp
            )

            # Step 2: Generate discharge summary
            discharge_response = await self.generate_discharge_summary(
                case_type, encrypted_case_sheets_resp
            )

            # Step 3: Encrypt lab reports if provided
            encrypted_lab_reports = []
            if lab_reports:
                encrypted_lab_reports_resp = await self.utilities.encryption(
                    payload={"files": lab_reports}
                )
                encrypted_lab_reports = self._normalize_encryption_response(
                    encrypted_lab_reports_resp
                )

            # Step 4: Generate FHIR bundle
            all_encrypted_files = encrypted_case_sheets + encrypted_lab_reports
            return await self.generate_fhir_bundle(
                case_type, discharge_response.extracted_data, all_encrypted_files
            )

        except Exception as e:
            self.logger.error(
                f"Error generating FHIR from files: {str(e)}", exc_info=True
            )
            raise

    def _normalize_encryption_response(
        self, response: Union[dict[str, Any], list[str], str]
    ) -> list[str]:
        """
        Normalizes encryption service responses to a uniform list of encrypted file identifiers.

        Args:
            response (Union[dict[str, Any], list[str], str]): The raw response from encryption utility.

        ### Returns:
            list[str]: List of encrypted file identifiers.

        Notes:
            Handles response formats which may be dict with 'files', list of strings, or single string.
        """
        if isinstance(response, dict):
            return response.get("files", [])
        elif isinstance(response, list):
            return response
        elif isinstance(response, str):
            return [response]
        else:
            self.logger.warning(
                f"Unexpected encryption response type: {type(response)}"
            )
            return []

    async def generate_discharge_summary(
        self, case_type: str, encrypted_data: Any
    ) -> DischargeSummaryResponse:
        """
        Generates a discharge summary from encrypted case sheet data.

        Args:
            case_type (str): Type of clinical case.
            encrypted_data (Any): Encrypted case sheet data (response from encryption service).

        ### Returns:
            DischargeSummaryResponse: AI-generated discharge summary response.

        Raises:
            EhrApiError: If AI endpoint or encryption call fails.

        Example:
            ```
            discharge_summary = await encounter_service._generate_discharge_summary(
                "Inpatient",
                encrypted_case_sheets_response
            )
            print(discharge_summary.dischargeSummary)
            ```

        ### Response:
            Sample Output:
            DischargeSummaryResponse(
                id="summary-xyz-123",
                dischargeSummary={
                    "patientName": "John Doe",
                    "diagnosis": "Acute Bronchitis",
                    "treatment": "Medication and rest"
                },
                extractedData={...},
                fhirBundle={...}
            )
        """
        discharge_payload = {
            "caseType": case_type,
            "encryptedData": encrypted_data,
        }

        return await self.post(
            AI_ENDPOINTS.GENERATE_DISCHARGE_SUMMARY,
            discharge_payload,
            response_model=DischargeSummaryResponse,
        )

    async def generate_fhir_bundle(
        self, case_type: str, extracted_data: Any, encrypted_files: list[str]
    ) -> dict[str, Any]:
        """
        Generates a FHIR-compliant bundle using extracted data and encrypted files.

        Args:
            case_type (str): Type of clinical case.
            extracted_data (Any): Data extracted from the discharge summary.
            encrypted_files (list[str]): List of encrypted file references.

        ### Returns:
            dict[str, Any]: The generated FHIR bundle.

        Raises:
            EhrApiError: On AI API call failure.

        Example:
            ```
            fhir_bundle = await encounter_service._generate_fhir_bundle(
                "Inpatient",
                extracted_data_from_discharge_summary,
                ["file1.enc", "file2.enc"]
            )
            print(fhir_bundle)
            ```

        ### Response:
            Sample Output:
            {
                "resourceType": "Bundle",
                "type": "document",
                "entry": [
                    {...},
                    {...}
                ]
            }
        """
        fhir_payload = {
            "caseType": case_type,
            "extractedData": extracted_data,
            "files": encrypted_files,
        }

        fhir_response = await self.post(
            AI_ENDPOINTS.GENERATE_FHIR_BUNDLE,
            fhir_payload,
            response_model=FhirBundleResponse,
        )

        return fhir_response.root
