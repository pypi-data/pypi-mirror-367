from typing import Any, Optional, Union
from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator
from carestack.common.enums import CaseType
from carestack.common.error_validation import check_not_empty


class VitalSign(BaseModel):
    """
    Represents a single vital sign measurement.

    ### Attributes:
        - value (str): The value of the vital sign.
        - unit (str): The unit of the vital sign.
    """

    value: str = Field(..., description="The value of the vital sign.")
    unit: str = Field(..., description="The unit of the vital sign.")

    @field_validator("value", "unit")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class PhysicalExamination(BaseModel):
    """
    Represents a physical examination section.

    ### Attributes:
        - blood_pressure (VitalSign): Blood pressure reading.
        - heart_rate (VitalSign): Heart rate reading.
        - respiratory_rate (VitalSign): Respiratory rate reading.
        - temperature (VitalSign): Temperature reading.
        - oxygen_saturation (VitalSign): Oxygen saturation reading.
        - height (VitalSign): Height measurement.
        - weight (VitalSign): Weight measurement.
    """

    blood_pressure: VitalSign = Field(
        ..., alias="bloodPressure", description="Blood pressure reading."
    )
    heart_rate: VitalSign = Field(
        ..., alias="heartRate", description="Heart rate reading."
    )
    respiratory_rate: VitalSign = Field(
        ..., alias="respiratoryRate", description="Respiratory rate reading."
    )
    temperature: VitalSign = Field(..., description="Temperature reading.")
    oxygen_saturation: VitalSign = Field(
        ..., alias="oxygenSaturation", description="Oxygen saturation reading."
    )
    height: VitalSign = Field(..., description="Height measurement.")
    weight: VitalSign = Field(..., description="Weight measurement.")


class MedicalHistoryItem(BaseModel):
    """
    Represents a single item in the patient's medical history.

    ### Attributes:
        - condition (Optional[str]): A medical condition in the patient's history.
        - procedure (Optional[str]): A medical procedure in the patient's history.
    """

    condition: Optional[str] = Field(
        None, description="A medical condition in the patient's history."
    )
    procedure: Optional[str] = Field(
        None, description="A medical procedure in the patient's history."
    )

    @field_validator("condition", "procedure")
    @classmethod
    def _validate_fields(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validates that condition and procedure is not empty if provided."""
        if v is not None:
            return check_not_empty(v, info.field_name)
        return v


class FamilyHistoryItem(BaseModel):
    """
    Represents a single item in the patient's family history.

    ### Attributes:
        - relation (str): The relation to the patient.
        - condition (str): The medical condition of the relative.
    """

    relation: str = Field(..., description="The relation to the patient.")
    condition: str = Field(..., description="The medical condition of the relative.")

    @field_validator("relation", "condition")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class ProcedureItem(BaseModel):
    """
    Represents a single procedure performed on the patient.

    ### Attributes:
        - description (str): Description of the procedure.
        - complications (Optional[str]): Any complications during the procedure.
    """

    description: str = Field(..., description="Description of the procedure.")
    complications: Optional[str] = Field(
        None, description="Any complications during the procedure."
    )

    @field_validator("description", "complications")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class InvestigationItem(BaseModel):
    """
    Represents a single investigation record.

    ### Attributes:
        - observations (dict[str, VitalSign]): Observed vital signs.
        - status (str): Status of the investigation.
        - recordedDate (str): Date when the investigation was recorded.
    """

    observations: dict[str, VitalSign]
    status: str
    recordedDate: str


class LabReportItem(BaseModel):
    """
    Represents a single lab report.

    ### Attributes:
        - observations (dict[str, VitalSign]): Observed vital signs.
        - status (str): Status of the lab report.
        - recordedDate (str): Date when the lab report was recorded.
        - category (str): Category of the lab report.
        - conclusion (str): Conclusion of the lab report.
    """

    observations: dict[str, VitalSign]
    status: str
    recordedDate: str
    category: str
    conclusion: str


class PatientDetails(BaseModel):
    """
    Represents patient demographic and admission details.

    ### Attributes:
        - name (Optional[str]): The patient's name.
        - age (Optional[str]): The patient's age.
        - sex (Optional[str]): The patient's sex.
        - date_of_birth (Optional[str]): The patient's date of birth.
        - date_of_admission (Optional[str]): The patient's date of admission.
        - address (Optional[str]): The patient's address.
        - contact_number (Optional[str]): The patient's contact number.
        - uhid (Optional[str]): The patient's UHID.
        - ip_number (Optional[str]): The patient's IP number.
        - marital_status (Optional[str]): The patient's marital status.
    """

    name: Optional[str] = Field(None, alias="Name", description="The patient's name.")
    age: Optional[str] = Field(None, alias="Age", description="The patient's age.")
    sex: Optional[str] = Field(None, alias="Sex", description="The patient's sex.")
    date_of_birth: Optional[str] = Field(
        None, alias="Date Of Birth", description="The patient's date of birth."
    )
    date_of_admission: Optional[str] = Field(
        None, alias="Date Of Admission", description="The patient's date of admission."
    )
    address: Optional[str] = Field(
        None, alias="Address", description="The patient's address."
    )
    contact_number: Optional[str] = Field(
        None, alias="Contact Number", description="The patient's contact number."
    )
    uhid: Optional[str] = Field(None, alias="UHID", description="The patient's UHID.")
    ip_number: Optional[str] = Field(
        None, alias="IP Number", description="The patient's IP number."
    )
    marital_status: Optional[str] = Field(
        None, alias="Marital Status", description="The patient's marital status."
    )


class DoctorDetails(BaseModel):
    """
    Represents doctor information.

    ### Attributes:
        - name (str): The doctor's name.
        - designation (str): The doctor's designation.
        - department (str): The doctor's department.
    """

    name: str = Field(..., alias="Name", description="The doctor's name.")
    designation: str = Field(
        ..., alias="Designation", description="The doctor's designation."
    )
    department: str = Field(
        ..., alias="Department", description="The doctor's department."
    )


class CommonHealthInformationDTO(BaseModel):
    """
    Base DTO for common health information sections.

    ### Attributes:
        - patient_details (PatientDetails): Patient's information.
        - doctor_details (list[DoctorDetails]): Doctor's information.
        - chief_complaints (str): The patient's chief complaints.
        - physical_examination (PhysicalExamination): Patient's physical examination.
        - medical_history (Optional[list[MedicalHistoryItem]]): Patient's medical history.
        - family_history (Optional[list[FamilyHistoryItem]]): Patient's family history.
        - condtions (Optional[list[str]]): Patient's conditions.
        - current_procedures (Optional[list[ProcedureItem]]): Patient's procedures.
        - current_medications (Optional[list[str]]): Patient's medications.
        - prescribed_medications (Optional[list[str]]): Patient's prescribed medications.
        - allergies (Optional[list[str]]): Patient's allergies.
        - immunizations (Optional[list[str]]): Patient's immunizations.
        - advisory_notes (Optional[list[str]]): Patient's advisory notes.
        - care_plan (Optional[list[str]]): Patient's care plan.
        - follow_up (Optional[list[str]]): Patient's follow-up plan.
    """

    patient_details: PatientDetails = Field(
        ..., alias="Patient Details", description="Patient's information."
    )
    doctor_details: list[DoctorDetails] = Field(
        ..., alias="Doctor Details", description="Doctor's information."
    )
    chief_complaints: str = Field(
        ..., alias="chiefComplaints", description="The patient's chief complaints."
    )
    physical_examination: PhysicalExamination = Field(
        ..., alias="physicalExamination", description="Patient's physical examination."
    )

    medical_history: Optional[list[MedicalHistoryItem]] = Field(
        None, alias="medicalHistory", description="Patient's medical history."
    )

    family_history: Optional[list[FamilyHistoryItem]] = Field(
        None, alias="familyHistory", description="Patient's family history."
    )

    condtions: Optional[list[str]] = Field(None, description="Patient's conditions.")

    current_procedures: Optional[list[ProcedureItem]] = Field(
        None, alias="currentProcedures", description="Patient's procedures."
    )
    current_medications: Optional[list[str]] = Field(
        None, alias="currentMedications", description="Patient's medications."
    )
    prescribed_medications: Optional[list[str]] = Field(
        None,
        alias="prescribedMedications",
        description="Patient's prescribed medications.",
    )
    allergies: Optional[list[str]] = Field(None, description="Patient's allergies.")
    immunizations: Optional[list[str]] = Field(
        None, alias="immunizations", description="Patient's immunizations."
    )
    advisory_notes: Optional[list[str]] = Field(
        None, alias="advisoryNotes", description="Patient's advisory notes."
    )
    care_plan: Optional[list[str]] = Field(
        None, alias="carePlan", description="Patient's care plan."
    )
    follow_up: Optional[list[str]] = Field(
        None, alias="followUp", description="Patient's follow-up plan."
    )


class OPConsultationSections(CommonHealthInformationDTO):
    """
    Represents the OP consultation section, inheriting common health information.
    """

    pass


class DischargeSummarySections(CommonHealthInformationDTO):
    """
    Represents the discharge summary section, inheriting common health information.

    ### Attributes:
        - investigations (InvestigationItem): Patient's investigations.
    """

    investigations: InvestigationItem = Field(
        ..., description="Patient's investigations."
    )


class PrescriptionSections(BaseModel):
    """
    Represents the prescription section.

    ### Attributes:
        - prescribed_medications (list[str]): Patient's prescribed medications.
    """

    prescribed_medications: list[str] = Field(
        ...,
        alias="prescribedMedications",
        description="Patient's prescribed medications.",
    )


class WellnessRecordSections(BaseModel):
    """
    Represents the wellness record section.

    ### Attributes:
        - patient_details (PatientDetails): Patient's information.
        - doctor_details (list[DoctorDetails]): Doctor's information.
        - vital_signs (Optional[dict[str, VitalSign]]): Patient's vital signs.
        - body_measurements (Optional[dict[str, VitalSign]]): Patient's body measurements.
        - physical_activities (Optional[dict[str, VitalSign]]): Patient's physical activities.
        - women_health (Optional[dict[str, VitalSign]]): Women's health data.
        - life_style (Optional[dict[str, VitalSign]]): Lifestyle data.
        - others (Optional[dict[str, VitalSign]]): Other health data.
    """

    patient_details: PatientDetails = Field(
        ..., alias="Patient Details", description="Patient's information."
    )
    doctor_details: list[DoctorDetails] = Field(
        ..., alias="Doctor Details", description="Doctor's information."
    )
    vital_signs: Optional[dict[str, VitalSign]] = Field(None, alias="vitalSigns")
    body_measurements: Optional[dict[str, VitalSign]] = Field(
        None, alias="bodyMeasurements"
    )
    physical_activities: Optional[dict[str, VitalSign]] = Field(
        None, alias="physicalActivities"
    )
    women_health: Optional[dict[str, VitalSign]] = Field(None, alias="womenHealth")
    life_style: Optional[dict[str, VitalSign]] = Field(None, alias="lifeStyle")
    others: Optional[dict[str, VitalSign]] = Field(None, alias="others")


class ImmunizationRecordSections(BaseModel):
    """
    Represents the immunization record section.

    ### Attributes:
        - patient_details (PatientDetails): Patient's information.
        - doctor_details (list[DoctorDetails]): Doctor's information.
        - immunizations (list[str]): Patient's immunizations.
    """

    patient_details: PatientDetails = Field(
        ..., alias="Patient Details", description="Patient's information."
    )
    doctor_details: list[DoctorDetails] = Field(
        ..., alias="Doctor Details", description="Doctor's information."
    )
    immunizations: list[str] = Field(..., description="Patient's immunizations.")


class DiagnosticReportSections(BaseModel):
    """
    Represents the diagnostic report section.

    ### Attributes:
        - patient_details (PatientDetails): Patient's information.
        - doctor_details (list[DoctorDetails]): Doctor's information.
        - lab_reports (LabReportItem): Patient's lab reports.
    """

    patient_details: PatientDetails = Field(
        ..., alias="Patient Details", description="Patient's information."
    )
    doctor_details: list[DoctorDetails] = Field(
        ..., alias="Doctor Details", description="Doctor's information."
    )
    lab_reports: LabReportItem = Field(..., description="Patient's lab reports.")


class OPConsultationDTO(BaseModel):
    """
    DTO for OP consultation records.

    ### Attributes:
        - case_sheets (Optional[list[str]]): Patient's case_sheets.
        - payload (Optional[OPConsultationSections]): Patient's raw data.
    """

    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[OPConsultationSections] = Field(
        None, alias="payload", description="Patient's raw data."
    )


class DischargeSummaryDTO(BaseModel):
    """
    DTO for discharge summary records.

    ### Attributes:
        - case_sheets (Optional[list[str]]): Patient's case_sheets.
        - payload (Optional[DischargeSummarySections]): Patient's raw data.
    """

    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[DischargeSummarySections] = Field(
        None, alias="payload", description="Patient's raw data."
    )


class PrescriptionRecordDTO(BaseModel):
    """
    DTO for prescription records.

    ### Attributes:
        - case_sheets (Optional[list[str]]): Patient's case_sheets.
        - payload (Optional[PrescriptionSections]): Patient's payload.
    """

    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[PrescriptionSections] = Field(
        None, description="Patient's payload."
    )


class WellnessRecordDTO(BaseModel):
    """
    DTO for wellness record data.

    ### Attributes:
        - case_sheets (Optional[list[str]]): Patient's case_sheets.
        - payload (Optional[WellnessRecordSections]): Patient's payload.
    """

    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[WellnessRecordSections] = Field(
        None, description="Patient's payload."
    )


class ImmunizationRecordDTO(BaseModel):
    """
    DTO for immunization record data.

    ### Attributes:
        - case_sheets (Optional[list[str]]): Patient's case_sheets.
        - payload (Optional[ImmunizationRecordSections]): Patient's payload.
    """

    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[ImmunizationRecordSections] = Field(
        None, description="Patient's payload."
    )


class DiagnosticReportDTO(BaseModel):
    """
    DTO for diagnostic report data.

    ### Attributes:
        - case_sheets (Optional[list[str]]): Patient's case_sheets.
        - payload (Optional[DiagnosticReportSections]): Patient's payload.
    """

    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[DiagnosticReportSections] = Field(
        None, description="Patient's payload."
    )


class HealthDocumentRecordDTO(BaseModel):
    """
    DTO for generic health document records.

    ### Attributes:
        - case_sheets (Optional[list[str]]): Patient's case_sheets.
    """

    case_sheets: Optional[list[str]] = Field(None, description="Patient's case_sheets.")


HealthInformationDTOUnion = Union[
    OPConsultationDTO,
    DischargeSummaryDTO,
    PrescriptionRecordDTO,
    WellnessRecordDTO,
    ImmunizationRecordDTO,
    DiagnosticReportDTO,
    HealthDocumentRecordDTO,
]


class EncounterRequestDTO(BaseModel):
    """
    DTO for encounter requests, representing a health information case.

    ### Attributes:
        - case_type (CaseType): The type of health information case.
        - lab_reports (Optional[list[str]]): The document references.
        - dto (HealthInformationDTOUnion): The health information data.
    """

    case_type: CaseType = Field(
        ..., alias="caseType", description="The type of health information case"
    )  # Changed from HealthInformationTypes
    lab_reports: Optional[list[str]] = Field(
        None, alias="labReports", description="The document references"
    )
    dto: HealthInformationDTOUnion = Field(
        ..., alias="dto", description="The health information data"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_case_type_and_data(cls, values: Any):
        """
        Validates and maps the `dto` field to the correct DTO class based on `case_type`.

        ### Raises:
            ValueError: If the data does not match the expected DTO class.
        """
        if isinstance(values, dict):
            case_type = values.get("case_type") or values.get("caseType")
            data = values.get("dto")

            if case_type and data:
                # Mapping of case types to their corresponding DTO classes
                health_information_dto_mapping = {
                    CaseType.OP_CONSULTATION.value: OPConsultationDTO,
                    CaseType.DISCHARGE_SUMMARY.value: DischargeSummaryDTO,
                    CaseType.PRESCRIPTION.value: PrescriptionRecordDTO,
                    CaseType.WellnessRecord.value: WellnessRecordDTO,
                    CaseType.ImmunizationRecord.value: ImmunizationRecordDTO,
                    CaseType.DiagnosticReport.value: DiagnosticReportDTO,
                }

                expected_dto_class = health_information_dto_mapping.get(case_type)
                if expected_dto_class:
                    # Convert the data to the expected DTO class
                    try:
                        values["dto"] = expected_dto_class(**data)
                    except Exception as e:
                        raise ValueError(
                            f"Invalid data for {expected_dto_class.__name__}: {str(e)}"
                        )

            return values
