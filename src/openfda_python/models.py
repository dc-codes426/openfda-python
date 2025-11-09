"""
Data models for FDA inputs and outputs.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Iterator, Union
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

# ====================
# Validation functions
# ====================

def validate_date(date: datetime) -> str:
    """Convert datetime to FDA API date format (YYYYMMDD)."""
    return date.strftime("%Y%m%d")


def validate_limit(limit: Optional[int]) -> None:
    """
    Validate limit parameter.

    Args:
        limit: Total results wanted. Use -1 for unlimited results.

    Raises:
        ValueError: If limit is invalid (< -1 or 0)
    """
    if limit is not None and limit < -1:
        raise ValueError(f"limit must be positive or -1 (unlimited), got {limit}")
    if limit == 0:
        raise ValueError(f"limit cannot be 0, use -1 for unlimited or a positive number")


def validate_skip(skip: Optional[int]) -> None:
    """Validate skip is non-negative."""
    if skip is not None and (skip < 0 or skip > 25000):
        raise ValueError(f"skip must be non-negative, got {skip}")

def validate_sort(sort: Optional[str]) -> None:
    """Validate sort parameter format (field:direction)."""
    if sort is not None and ':' in sort:
        order = sort.split(':')[1]
        allowed_orders = ['asc', 'desc']
        if order not in allowed_orders:
            raise ValueError(f"'{order}' not allowed. Choose either 'asc' or 'desc'.")

# ===============================================================
# API-Compliant Query Classes
# These classes are strict 1-to-1 mappings with openFDA endpoints
# ===============================================================

@dataclass
class BaseQuery(ABC):
    """
    Base query class with common parameters for all openFDA endpoints.

    Common query parameters:
    - search: Search query string (e.g., "patient.drug.openfda.brand_name:aspirin")
    - sort: Field to sort by with direction (e.g., "receivedate:desc")
    - count: Field to count unique values (e.g., "patient.reaction.reactionmeddrapt.exact")
    - limit: Maximum total number of records to return (default: 1000)
    - skip: Number of records to skip (used internally for pagination)

    Class attributes:
    - ENDPOINT_PATH: The FDA API endpoint path (e.g., '/drug/event.json')
    """
    # Subclasses must define this
    ENDPOINT_PATH: str = ""

    search: Optional[str] = None
    sort: Optional[str] = None
    count: Optional[str] = None
    limit: Optional[int] = 1000
    skip: Optional[int] = None

    def __post_init__(self):
        """Validate common parameters after initialization."""
        validate_limit(self.limit)
        validate_skip(self.skip)
        validate_sort(self.sort)
        self._validate_endpoint_specific()

    @abstractmethod
    def _validate_endpoint_specific(self) -> None:
        """Override this method to add endpoint-specific validation."""
        pass

@dataclass
class Drug_NDCQuery(BaseQuery):
    """
    Query for National Drug Code directory.

    Endpoint: /drug/ndc.json

    Common search fields:
    - brand_name: Brand/trade name of the drug
    - generic_name: Generic name of the drug
    - manufacturer_name: Company name
    - product_ndc: Product NDC code
    - package_ndc: Package NDC code
    - product_type: Type (e.g., "HUMAN PRESCRIPTION DRUG")
    - route: Route of administration (e.g., "ORAL")
    - active_ingredients.name: Active ingredient name

    Example:
        query = DrugNDCQuery(
            search='brand_name:"tylenol"',
            limit=25
        )
    """
    ENDPOINT_PATH: str = "/drug/ndc.json"

    @dataclass
    class active_ingredients:
        name: Optional[str] = None
        strength: Optional[str] = None

    @dataclass
    class packaging:
        package_ndc: Optional[str] = None
        description: Optional[str] = None
        marketing_start_date: Optional[datetime] = None
        marketing_end_date: Optional[datetime] = None
        sample: Optional[str] = None

    @dataclass
    class openfda:
        is_original_packager: Optional[str] = None
        manufacturer_name: Optional[str] = None
        nui: Optional[str] = None
        pharm_class_cs: Optional[str] = None
        pharm_class_epc: Optional[str] = None
        pharm_class_moa: Optional[str] = None
        pharm_class_pe: Optional[str] = None
        rxcui: Optional[str] = None
        spl_set_id: Optional[str] = None
        unii: Optional[str] = None
        upc: Optional[str] = None

    active_ingredients: Optional[active_ingredients] = None
    packaging: Optional[packaging] = None
    openfda: Optional[openfda] = None

    product_id: Optional[str] = None
    product_ndc: Optional[str] = None
    spl_id: Optional[str] = None
    product_type: Optional[str] = None
    finished: Optional[str] = None
    brand_name: Optional[str] = None
    brand_name_base: Optional[str] = None
    brand_name_suffix: Optional[str] = None
    generic_name: Optional[str] = None
    dosage_form: Optional[str] = None
    route: Optional[str] = None
    marketing_start_date: Optional[datetime] = None
    marketing_end_date: Optional[datetime] = None
    marketing_category: Optional[str] = None
    application_number: Optional[str] = None
    pharm_class: Optional[str] = None
    dea_schedule: Optional[str] = None
    listing_expiration_date: Optional[datetime] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate NDC specific parameters."""
        allowed_dea = ['CI', 'CII','CIII','CIV','CV']
        if self.dea_schedule and self.dea_schedule not in allowed_dea:
            raise ValueError(f"{self.dea_schedule} is not a valid input.")
        pass

@dataclass
class AnimalVetAdverseEventsQuery(BaseQuery):
    """
    Query for AnimalVet AdverseEvents.
    
    Endpoint: /animalandveterinary/event.json
    """

    @dataclass
    class Animal:
        @dataclass
        class Age:
            max: Optional[str] = None
            min: Optional[str] = None
            qualifier: Optional[str] = None
            unit: Optional[str] = None
        age: Optional[Age] = None
        @dataclass
        class Breed:
            is_crossbred: Optional[str] = None
            breed_component: Optional[str] = None
        breed: Optional[Breed] = None
        female_animal_physiological_status: Optional[str] = None
        gender: Optional[str] = None
        reproductive_status: Optional[str] = None
        species: Optional[str] = None
        @dataclass
        class Weight:
            max: Optional[str] = None
            min: Optional[str] = None
            qualifier: Optional[str] = None
            unit: Optional[str] = None
        weight: Optional[Weight] = None

    @dataclass
    class Drug:
        @dataclass
        class ActiveIngredients:
            name: Optional[str] = None
        active_ingredients: Optional[ActiveIngredients] = None
        administered_by: Optional[str] = None
        ae_abated_after_stopping_drug: Optional[str] = None
        ae_reappeared_after_resuming_drug: Optional[str] = None
        atc_vet_code: Optional[str] = None
        brand_name: Optional[str] = None
        dosage_form: Optional[str] = None
        first_exposure_date: Optional[datetime] = None
        @dataclass
        class FrequencyOfAdministration:
            unit: Optional[str] = None
            value: Optional[str] = None
        frequency_of_administration: Optional[FrequencyOfAdministration] = None
        last_exposure_date: Optional[datetime] = None
        lot_expiration: Optional[str] = None
        lot_number: Optional[str] = None
        @dataclass
        class Manufacturer:
            name: Optional[str] = None
            registration_number: Optional[str] = None
        manufacturer: Optional[Manufacturer] = None
        manufacturing_date: Optional[datetime] = None
        number_of_defective_items: Optional[str] = None
        number_of_items_returned: Optional[str] = None
        off_label_use: Optional[str] = None
        previous_ae_to_drug: Optional[str] = None
        previous_exposure_to_drug: Optional[str] = None
        product_ndc: Optional[str] = None
        route: Optional[str] = None
        used_according_to_label: Optional[str] = None

    @dataclass
    class Duration:
        unit: Optional[str] = None
        value: Optional[str] = None

    @dataclass
    class HealthAssessmentPriorToExposure:
        assessed_by: Optional[str] = None
        condition: Optional[str] = None

    @dataclass
    class Outcome:
        medical_status: Optional[str] = None
        number_of_animals_affected: Optional[str] = None

    @dataclass
    class Reaction:
        accuracy: Optional[str] = None
        number_of_animals_affected: Optional[str] = None
        veddra_term_code: Optional[str] = None
        veddra_term_name: Optional[str] = None
        veddra_version: Optional[str] = None

    @dataclass
    class Receiver:
        city: Optional[str] = None
        country: Optional[str] = None
        organization: Optional[str] = None
        postal_code: Optional[str] = None
        state: Optional[str] = None
        street_address: Optional[str] = None

    animal: Optional[Animal] = None
    drug: Optional[Drug] = None
    duration: Optional[Duration] = None
    health_assessment_prior_to_exposure: Optional[HealthAssessmentPriorToExposure] = None
    number_of_animals_affected: Optional[str] = None
    number_of_animals_treated: Optional[str] = None
    onset_date: Optional[datetime] = None
    original_receive_date: Optional[datetime] = None
    outcome: Optional[Outcome] = None
    primary_reporter: Optional[str] = None
    reaction: Optional[Reaction] = None
    receiver: Optional[Receiver] = None
    report_id: Optional[str] = None
    secondary_reporter: Optional[str] = None
    serious_ae: Optional[str] = None
    time_between_exposure_and_onset: Optional[str] = None
    treated_for_ae: Optional[str] = None
    type_of_information: Optional[str] = None
    unique_aer_id_number: Optional[str] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/animalandveterinary/event.json"

@dataclass
class CosmeticEventsQuery(BaseQuery):
    """
    Query for Cosmetic Events.
    
    Endpoint: /cosmetic/event.json
    """

    @dataclass
    class ProductsItem:
        product_name: Optional[str] = None
        role: Optional[str] = None

    @dataclass
    class Patient:
        age: Optional[str] = None
        age_unit: Optional[str] = None
        gender: Optional[str] = None

    report_number: Optional[str] = None
    report_version: Optional[str] = None
    legacy_report_id: Optional[str] = None
    report_type: Optional[str] = None
    initial_received_date: Optional[datetime] = None
    latest_received_date: Optional[datetime] = None
    event_date: Optional[datetime] = None
    products: Optional[List[ProductsItem]] = None
    patient: Optional[Patient] = None
    reactions: Optional[List[str]] = None
    meddra_version: Optional[str] = None
    outcomes: Optional[List[str]] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/cosmetic/event.json"

@dataclass
class Device510kQuery(BaseQuery):
    """
    Query for Device 510k reports.
    """
    ENDPOINT_PATH: str = "/device/510k.json"
    
    # missing attributes

@dataclass
class DeviceAdverseEventsQuery(BaseQuery):
    """
    Query for Device AdverseEvents.

    Endpoint: /device/event.json
    """
    ENDPOINT_PATH: str = "/device/event.json"

    @dataclass
    class DeviceItem:
        brand_name: Optional[str] = None
        catalog_number: Optional[str] = None
        date_received: Optional[datetime] = None
        date_removed_flag: Optional[str] = None
        date_returned_to_manufacturer: Optional[datetime] = None
        device_age_text: Optional[str] = None
        device_availability: Optional[str] = None
        device_evaluated_by_manufacturer: Optional[str] = None
        device_event_key: Optional[str] = None
        device_operator: Optional[str] = None
        device_report_product_code: Optional[str] = None
        device_sequence_number: Optional[str] = None
        expiration_date_of_device: Optional[datetime] = None
        generic_name: Optional[str] = None
        udi_di: Optional[str] = None
        implant_flag: Optional[str] = None
        lot_number: Optional[str] = None
        manufacturer_d_address_1: Optional[str] = None
        manufacturer_d_address_2: Optional[str] = None
        manufacturer_d_city: Optional[str] = None
        manufacturer_d_country: Optional[str] = None
        manufacturer_d_name: Optional[str] = None
        manufacturer_d_postal_code: Optional[str] = None
        manufacturer_d_state: Optional[str] = None
        manufacturer_d_zip_code: Optional[str] = None
        manufacturer_d_zip_code_ext: Optional[str] = None
        model_number: Optional[str] = None
        @dataclass
        class Openfda:
            device_class: Optional[str] = None
            device_name: Optional[str] = None
            fei_number: Optional[List[str]] = None
            medical_specialty_description: Optional[str] = None
            registration_number: Optional[List[str]] = None
            regulation_number: Optional[str] = None
        openfda: Optional[Openfda] = None
        other_id_number: Optional[str] = None
        udi_public: Optional[str] = None

    @dataclass
    class MdrTextItem:
        date_report: Optional[datetime] = None
        mdr_text_key: Optional[str] = None
        patient_sequence_number: Optional[str] = None
        text: Optional[str] = None
        text_type_code: Optional[str] = None

    @dataclass
    class PatientItem:
        date_received: Optional[datetime] = None
        patient_sequence_number: Optional[str] = None
        patient_age: Optional[str] = None
        patient_sex: Optional[str] = None
        patient_weight: Optional[str] = None
        patient_ethnicity: Optional[str] = None
        patient_race: Optional[str] = None
        patient_problems: Optional[List[str]] = None
        sequence_number_outcome: Optional[List[str]] = None
        sequence_number_treatment: Optional[List[str]] = None

    adverse_event_flag: Optional[str] = None
    date_facility_aware: Optional[datetime] = None
    date_manufacturer_received: Optional[datetime] = None
    date_of_event: Optional[datetime] = None
    date_received: Optional[datetime] = None
    date_report: Optional[datetime] = None
    date_report_to_fda: Optional[datetime] = None
    date_report_to_manufacturer: Optional[datetime] = None
    device: Optional[List[DeviceItem]] = None
    device_date_of_manufacturer: Optional[datetime] = None
    distributor_address_1: Optional[str] = None
    distributor_address_2: Optional[str] = None
    distributor_city: Optional[str] = None
    distributor_name: Optional[str] = None
    distributor_state: Optional[str] = None
    distributor_zip_code: Optional[str] = None
    distributor_zip_code_ext: Optional[str] = None
    event_key: Optional[str] = None
    event_location: Optional[str] = None
    event_type: Optional[str] = None
    expiration_date_of_device: Optional[datetime] = None
    health_professional: Optional[str] = None
    initial_report_to_fda: Optional[str] = None
    manufacturer_address_1: Optional[str] = None
    manufacturer_address_2: Optional[str] = None
    manufacturer_city: Optional[str] = None
    manufacturer_contact_address_1: Optional[str] = None
    manufacturer_contact_address_2: Optional[str] = None
    manufacturer_contact_area_code: Optional[str] = None
    manufacturer_contact_city: Optional[str] = None
    manufacturer_contact_country: Optional[str] = None
    manufacturer_contact_exchange: Optional[str] = None
    manufacturer_contact_extension: Optional[str] = None
    manufacturer_contact_f_name: Optional[str] = None
    manufacturer_contact_l_name: Optional[str] = None
    manufacturer_contact_pcity: Optional[str] = None
    manufacturer_contact_pcountry: Optional[str] = None
    manufacturer_contact_phone_number: Optional[str] = None
    manufacturer_contact_plocal: Optional[str] = None
    manufacturer_contact_postal_code: Optional[str] = None
    manufacturer_contact_state: Optional[str] = None
    manufacturer_contact_t_name: Optional[str] = None
    manufacturer_contact_zip_code: Optional[str] = None
    manufacturer_contact_zip_ext: Optional[str] = None
    manufacturer_country: Optional[str] = None
    manufacturer_g1_address_1: Optional[str] = None
    manufacturer_g1_address_2: Optional[str] = None
    manufacturer_g1_city: Optional[str] = None
    manufacturer_g1_country: Optional[str] = None
    manufacturer_g1_name: Optional[str] = None
    manufacturer_g1_postal_code: Optional[str] = None
    manufacturer_g1_state: Optional[str] = None
    manufacturer_g1_zip_code: Optional[str] = None
    manufacturer_g1_zip_code_ext: Optional[str] = None
    manufacturer_link_flag: Optional[str] = None
    manufacturer_name: Optional[str] = None
    manufacturer_postal_code: Optional[str] = None
    manufacturer_state: Optional[str] = None
    manufacturer_zip_code: Optional[str] = None
    manufacturer_zip_code_ext: Optional[str] = None
    mdr_report_key: Optional[str] = None
    mdr_text: Optional[List[MdrTextItem]] = None
    number_devices_in_event: Optional[str] = None
    number_patients_in_event: Optional[str] = None
    patient: Optional[List[PatientItem]] = None
    previous_use_code: Optional[str] = None
    product_problems: Optional[List[str]] = None
    product_problem_flag: Optional[str] = None
    remedial_action: Optional[List[str]] = None
    removal_correction_number: Optional[str] = None
    report_date: Optional[datetime] = None
    report_number: Optional[str] = None
    report_source_code: Optional[str] = None
    report_to_fda: Optional[str] = None
    report_to_manufacturer: Optional[str] = None
    reporter_occupation_code: Optional[str] = None
    reprocessed_and_reused_flag: Optional[str] = None
    single_use_flag: Optional[str] = None
    source_type: Optional[List[str]] = None
    type_of_report: Optional[List[str]] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

@dataclass
class DeviceClassificationQuery(BaseQuery):
    """
    Query for Device Classification.
    
    Endpoint: /device/classification.json
    """

    @dataclass
    class Openfda:
        fei_number: Optional[List[str]] = None
        k_number: Optional[List[str]] = None
        registration_number: Optional[List[str]] = None

    definition: Optional[str] = None
    device_class: Optional[str] = None
    device_name: Optional[str] = None
    gmp_exempt_flag: Optional[str] = None
    implant_flag: Optional[str] = None
    life_sustain_support_flag: Optional[str] = None
    medical_specialty: Optional[str] = None
    medical_specialty_description: Optional[str] = None
    openfda: Optional[Openfda] = None
    product_code: Optional[str] = None
    regulation_number: Optional[str] = None
    review_code: Optional[str] = None
    review_panel: Optional[str] = None
    submission_type_id: Optional[str] = None
    summary_malfunction_reporting: Optional[str] = None
    third_party_flag: Optional[str] = None
    unclassified_reason: Optional[str] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/device/classification.json"

@dataclass
class DeviceRecalls(BaseQuery):
    ENDPOINT_PATH = "device/recall.json"
    # missing attributes
    
    def _validate_endpoint_specific(self) -> None:
        pass
    
@dataclass
class DeviceRecallEnforcementReports(BaseQuery):
    ENDPOINT_PATH = 'device/enforcement.json'
    # missing attributes

    def _validate_endpoint_specific(self) -> None:
        pass

@dataclass
class DeviceCovid19TestingEvalsQuery(BaseQuery):
    """
    Query for Device Covid19TestingEvals.
    
    Endpoint: /device/covid19serology.json
    """
    manufacturer: Optional[str] = None
    device: Optional[str] = None
    date_performed: Optional[datetime] = None
    evaluation_id: Optional[str] = None
    lot_number: Optional[str] = None
    panel: Optional[str] = None
    sample_no: Optional[str] = None
    sample_id: Optional[str] = None
    type: Optional[str] = None
    group: Optional[str] = None
    days_from_symptom: Optional[str] = None
    igm_result: Optional[str] = None
    igg_result: Optional[str] = None
    iga_result: Optional[str] = None
    pan_result: Optional[str] = None
    igm_igg_result: Optional[str] = None
    igm_iga_result: Optional[str] = None
    control: Optional[str] = None
    igm_titer: Optional[str] = None
    igg_titer: Optional[str] = None
    pan_titer: Optional[str] = None
    igm_truth: Optional[str] = None
    igg_truth: Optional[str] = None
    antibody_truth: Optional[str] = None
    igm_agree: Optional[str] = None
    igg_agree: Optional[str] = None
    iga_agree: Optional[str] = None
    pan_agree: Optional[str] = None
    igm_igg_agree: Optional[str] = None
    igm_iga_agree: Optional[str] = None
    antibody_agree: Optional[str] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/device/covid19serology.json"

@dataclass
class DevicePremarketApprovalQuery(BaseQuery):
    """
    Query for Device PremarketApproval.
    
    Endpoint: /device/pma.json
    """

    @dataclass
    class Openfda:
        device_class: Optional[str] = None
        device_name: Optional[str] = None
        fei_number: Optional[List[str]] = None
        medical_specialty_description: Optional[str] = None
        registration_number: Optional[List[str]] = None
        regulation_number: Optional[List[str]] = None

    advisory_committee: Optional[str] = None
    advisory_committee_description: Optional[str] = None
    ao_statement: Optional[str] = None
    applicant: Optional[str] = None
    city: Optional[str] = None
    date_received: Optional[datetime] = None
    decision_code: Optional[str] = None
    decision_date: Optional[datetime] = None
    docket_number: Optional[str] = None
    expedited_review_flag: Optional[str] = None
    fed_reg_notice_date: Optional[datetime] = None
    generic_name: Optional[str] = None
    openfda: Optional[Openfda] = None
    pma_number: Optional[str] = None
    product_code: Optional[str] = None
    state: Optional[str] = None
    street_1: Optional[str] = None
    street_2: Optional[str] = None
    supplement_number: Optional[str] = None
    supplement_reason: Optional[str] = None
    supplement_type: Optional[str] = None
    trade_name: Optional[str] = None
    zip: Optional[str] = None
    zip_ext: Optional[str] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/device/pma.json"

@dataclass
class DeviceRegistrationsListingsQuery(BaseQuery):
    """
    Query for Device RegistrationsListings.
    
    Endpoint: /device/registrationlisting.json
    """

    @dataclass
    class ProductsItem:
        created_date: Optional[datetime] = None
        exempt: Optional[str] = None
        @dataclass
        class Openfda:
            device_class: Optional[str] = None
            device_name: Optional[str] = None
            medical_specialty_description: Optional[str] = None
            regulation_number: Optional[str] = None
        openfda: Optional[Openfda] = None
        owner_operator_number: Optional[str] = None
        product_code: Optional[str] = None

    @dataclass
    class Registration:
        address_line_1: Optional[str] = None
        address_line_2: Optional[str] = None
        city: Optional[str] = None
        fei_number: Optional[str] = None
        initial_importer_flag: Optional[str] = None
        iso_country_code: Optional[str] = None
        name: Optional[str] = None
        @dataclass
        class OwnerOperator:
            @dataclass
            class ContactAddress:
                address_1: Optional[str] = None
                address_2: Optional[str] = None
                city: Optional[str] = None
                iso_country_code: Optional[str] = None
                postal_code: Optional[str] = None
                state_code: Optional[str] = None
                state_province: Optional[str] = None
            contact_address: Optional[ContactAddress] = None
            firm_name: Optional[str] = None
            @dataclass
            class OfficialCorrespondent:
                first_name: Optional[str] = None
                last_name: Optional[str] = None
                middle_initial: Optional[str] = None
                phone_number: Optional[str] = None
                subaccount_company_name: Optional[str] = None
            official_correspondent: Optional[OfficialCorrespondent] = None
            owner_operator_number: Optional[str] = None
        owner_operator: Optional[OwnerOperator] = None
        postal_code: Optional[str] = None
        reg_expiry_date_year: Optional[str] = None
        registration_number: Optional[str] = None
        state_code: Optional[str] = None
        status_code: Optional[str] = None
        @dataclass
        class UsAgent:
            address_line_1: Optional[str] = None
            address_line_2: Optional[str] = None
            bus_phone_area_code: Optional[str] = None
            bus_phone_extn: Optional[str] = None
            bus_phone_num: Optional[str] = None
            business_name: Optional[str] = None
            city: Optional[str] = None
            email_address: Optional[str] = None
            fax_area_code: Optional[str] = None
            fax_num: Optional[str] = None
            iso_country_code: Optional[str] = None
            name: Optional[str] = None
            postal_code: Optional[str] = None
            state_code: Optional[str] = None
            zip_code: Optional[str] = None
        us_agent: Optional[UsAgent] = None
        zip_code: Optional[str] = None

    establishment_type: Optional[List[str]] = None
    k_number: Optional[str] = None
    pma_number: Optional[str] = None
    products: Optional[List[ProductsItem]] = None
    proprietary_name: Optional[List[str]] = None
    registration: Optional[Registration] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/device/registrationlisting.json"

@dataclass
class DeviceUniqueDeviceIDQuery(BaseQuery):
    """
    Query for Device UniqueDeviceID.
    
    Endpoint: /device/udi.json
    """

    @dataclass
    class CustomerContactsItem:
        email: Optional[str] = None
        phone: Optional[str] = None

    @dataclass
    class DeviceSizesItem:
        text: Optional[str] = None
        type: Optional[str] = None
        unit: Optional[str] = None
        value: Optional[str] = None

    @dataclass
    class GmdnTermsItem:
        code: Optional[str] = None
        definition: Optional[str] = None
        name: Optional[str] = None
        implantable: Optional[str] = None
        code_status: Optional[str] = None

    @dataclass
    class IdentifiersItem:
        id: Optional[str] = None
        issuing_agency: Optional[str] = None
        package_discontinue_date: Optional[datetime] = None
        package_status: Optional[str] = None
        package_type: Optional[str] = None
        quantity_per_package: Optional[str] = None
        type: Optional[str] = None
        unit_of_use_id: Optional[str] = None

    @dataclass
    class PremarketSubmissionsItem:
        submission_number: Optional[str] = None
        supplement_number: Optional[str] = None
        submission_type: Optional[str] = None

    @dataclass
    class ProductCodesItem:
        code: Optional[str] = None
        name: Optional[str] = None
        @dataclass
        class Openfda:
            device_class: Optional[str] = None
            device_name: Optional[str] = None
            medical_specialty_description: Optional[str] = None
            regulation_number: Optional[str] = None
        openfda: Optional[Openfda] = None

    @dataclass
    class Sterilization:
        is_sterile: Optional[str] = None
        is_sterilization_prior_use: Optional[str] = None
        sterilization_methods: Optional[str] = None

    @dataclass
    class StorageItem:
        @dataclass
        class High:
            unit: Optional[str] = None
            value: Optional[str] = None
        high: Optional[High] = None
        @dataclass
        class Low:
            unit: Optional[str] = None
            value: Optional[str] = None
        low: Optional[Low] = None
        special_conditions: Optional[str] = None
        type: Optional[str] = None

    brand_name: Optional[str] = None
    catalog_number: Optional[str] = None
    commercial_distribution_end_date: Optional[datetime] = None
    commercial_distribution_status: Optional[str] = None
    company_name: Optional[str] = None
    customer_contacts: Optional[List[CustomerContactsItem]] = None
    device_count_in_base_package: Optional[str] = None
    device_description: Optional[str] = None
    device_sizes: Optional[List[DeviceSizesItem]] = None
    gmdn_terms: Optional[List[GmdnTermsItem]] = None
    has_donation_id_number: Optional[str] = None
    has_expiration_date: Optional[str] = None
    has_lot_or_batch_number: Optional[str] = None
    has_manufacturing_date: Optional[str] = None
    has_serial_number: Optional[str] = None
    identifiers: Optional[List[IdentifiersItem]] = None
    is_combination_product: Optional[str] = None
    is_direct_marking_exempt: Optional[str] = None
    is_hct_p: Optional[str] = None
    is_kit: Optional[str] = None
    is_labeled_as_no_nrl: Optional[str] = None
    is_labeled_as_nrl: Optional[str] = None
    is_otc: Optional[str] = None
    is_pm_exempt: Optional[str] = None
    is_rx: Optional[str] = None
    is_single_use: Optional[str] = None
    labeler_duns_number: Optional[str] = None
    mri_safety: Optional[str] = None
    premarket_submissions: Optional[List[PremarketSubmissionsItem]] = None
    product_codes: Optional[List[ProductCodesItem]] = None
    publish_date: Optional[datetime] = None
    public_version_date: Optional[datetime] = None
    public_version_number: Optional[str] = None
    public_version_status: Optional[str] = None
    record_key: Optional[str] = None
    record_status: Optional[str] = None
    sterilization: Optional[Sterilization] = None
    storage: Optional[List[StorageItem]] = None
    version_or_model_number: Optional[str] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/device/udi.json"

@dataclass
class DrugAdverseEventsQuery(BaseQuery):
    """
    Query for Drug AdverseEvents.

    Endpoint: /drug/event.json
    """
    ENDPOINT_PATH: str = "/drug/event.json"

    @dataclass
    class Patient:
        @dataclass
        class DrugItem:
            actiondrug: Optional[int] = None
            @dataclass
            class Activesubstance:
                activesubstancename: Optional[str] = None
            activesubstance: Optional[Activesubstance] = None
            drugadditional: Optional[int] = None
            drugadministrationroute: Optional[str] = None
            drugauthorizationnumb: Optional[str] = None
            drugbatchnumb: Optional[str] = None
            drugcharacterization: Optional[int] = None
            drugcumulativedosagenumb: Optional[str] = None
            drugcumulativedosageunit: Optional[str] = None
            drugdosageform: Optional[str] = None
            drugdosagetext: Optional[str] = None
            drugenddate: Optional[datetime] = None
            drugenddateformat: Optional[str] = None
            drugindication: Optional[str] = None
            drugintervaldosagedefinition: Optional[int] = None
            drugintervaldosageunitnumb: Optional[int] = None
            drugrecurreadministration: Optional[int] = None
            drugrecurrence: Optional[str] = None
            drugseparatedosagenumb: Optional[int] = None
            drugstartdate: Optional[datetime] = None
            drugstartdateformat: Optional[str] = None
            drugstructuredosagenumb: Optional[str] = None
            drugstructuredosageunit: Optional[str] = None
            drugtreatmentduration: Optional[str] = None
            drugtreatmentdurationunit: Optional[str] = None
            medicinalproduct: Optional[str] = None
            @dataclass
            class Openfda:
                application_number: Optional[List[str]] = None
                brand_name: Optional[List[str]] = None
                generic_name: Optional[List[str]] = None
                manufacturer_name: Optional[List[str]] = None
                nui: Optional[List[str]] = None
                package_ndc: Optional[List[str]] = None
                pharm_class_cs: Optional[List[str]] = None
                pharm_class_epc: Optional[List[str]] = None
                pharm_class_pe: Optional[List[str]] = None
                pharm_class_moa: Optional[List[str]] = None
                product_ndc: Optional[List[str]] = None
                product_type: Optional[List[str]] = None
                route: Optional[List[str]] = None
                rxcui: Optional[List[str]] = None
                spl_id: Optional[List[str]] = None
                spl_set_id: Optional[List[str]] = None
                substance_name: Optional[List[str]] = None
                unii: Optional[List[str]] = None
            openfda: Optional[Openfda] = None
        drug: Optional[List[DrugItem]] = None
        patientagegroup: Optional[int] = None
        @dataclass
        class Patientdeath:
            patientdeathdate: Optional[datetime] = None
            patientdeathdateformat: Optional[str] = None
        patientdeath: Optional[Patientdeath] = None
        patientonsetage: Optional[str] = None
        patientonsetageunit: Optional[str] = None
        patientsex: Optional[int] = None
        patientweight: Optional[str] = None
        @dataclass
        class ReactionItem:
            reactionmeddrapt: Optional[str] = None
            reactionmeddraversionpt: Optional[str] = None
            reactionoutcome: Optional[int] = None
        reaction: Optional[List[ReactionItem]] = None
        @dataclass
        class Summary:
            narrativeincludeclinical: Optional[str] = None
        summary: Optional[Summary] = None

    @dataclass
    class Primarysource:
        literaturereference: Optional[str] = None
        qualification: Optional[str] = None
        reportercountry: Optional[str] = None

    @dataclass
    class Receiver:
        receiverorganization: Optional[str] = None
        receivertype: Optional[int] = None

    @dataclass
    class Reportduplicate:
        duplicatenumb: Optional[str] = None
        duplicatesource: Optional[str] = None

    @dataclass
    class Sender:
        senderorganization: Optional[str] = None
        sendertype: Optional[int] = None

    authoritynumb: Optional[str] = None
    companynumb: Optional[str] = None
    duplicate: Optional[str] = None
    fulfillexpeditecriteria: Optional[int] = None
    occurcountry: Optional[str] = None
    patient: Optional[Patient] = None
    primarysource: Optional[Primarysource] = None
    primarysourcecountry: Optional[str] = None
    receiptdate: Optional[datetime] = None
    receiptdateformat: Optional[str] = None
    receivedate: Optional[datetime] = None
    receivedateformat: Optional[str] = None
    receiver: Optional[Receiver] = None
    reportduplicate: Optional[Reportduplicate] = None
    reporttype: Optional[int] = None
    safetyreportid: Optional[str] = None
    safetyreportversion: Optional[int] = None
    sender: Optional[Sender] = None
    serious: Optional[int] = None
    seriousnesscongenitalanomali: Optional[int] = None
    seriousnessdeath: Optional[int] = None
    seriousnessdisabling: Optional[int] = None
    seriousnesshospitalization: Optional[int] = None
    seriousnesslifethreatening: Optional[int] = None
    seriousnessother: Optional[int] = None
    transmissiondate: Optional[datetime] = None
    transmissiondateformat: Optional[int] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

@dataclass
class DrugDrugShortagesQuery(BaseQuery):
    """
    Query for Drug DrugShortages.
    
    Endpoint: /drug/drugsfda.json
    """

    @dataclass
    class Openfda:
        brand_name: Optional[List[str]] = None
        dosage_form: Optional[List[str]] = None
        is_original_packager: Optional[List[str]] = None
        manufacturer_name: Optional[List[str]] = None
        nui: Optional[List[str]] = None
        original_packager_product_ndc: Optional[List[str]] = None
        package_ndc: Optional[List[str]] = None
        pharm_class_cs: Optional[List[str]] = None
        pharm_class_epc: Optional[List[str]] = None
        pharm_class_moa: Optional[List[str]] = None
        pharm_class_pe: Optional[List[str]] = None
        product_ndc: Optional[List[str]] = None
        product_type: Optional[List[str]] = None
        route: Optional[List[str]] = None
        rxcui: Optional[List[str]] = None
        spl_id: Optional[List[str]] = None
        spl_set_id: Optional[List[str]] = None
        substance_name: Optional[List[str]] = None
        unii: Optional[List[str]] = None
        upc: Optional[List[str]] = None

    package_ndc: Optional[str] = None
    generic_name: Optional[str] = None
    proprietary_name: Optional[str] = None
    company_name: Optional[str] = None
    contact_info: Optional[str] = None
    presentation: Optional[str] = None
    update_type: Optional[str] = None
    availability: Optional[str] = None
    related_info: Optional[str] = None
    related_info_link: Optional[str] = None
    resolved_note: Optional[str] = None
    shortage_reason: Optional[str] = None
    therapeutic_category: Optional[List[str]] = None
    dosage_form: Optional[str] = None
    strength: Optional[List[str]] = None
    status: Optional[str] = None
    update_date: Optional[datetime] = None
    change_date: Optional[datetime] = None
    discontinued_date: Optional[datetime] = None
    initial_posting_date: Optional[datetime] = None
    openfda: Optional[Openfda] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/drug/drugsfda.json"

@dataclass
class DrugDrugsatFDAQuery(BaseQuery):
    """
    Query for Drug DrugsatFDA.
    
    Endpoint: /drug/drugsfda.json
    """

    @dataclass
    class Openfda:
        application_number: Optional[List[str]] = None
        brand_name: Optional[List[str]] = None
        generic_name: Optional[List[str]] = None
        manufacturer_name: Optional[List[str]] = None
        nui: Optional[List[str]] = None
        package_ndc: Optional[List[str]] = None
        pharm_class_cs: Optional[List[str]] = None
        pharm_class_epc: Optional[List[str]] = None
        pharm_class_pe: Optional[List[str]] = None
        pharm_class_moa: Optional[List[str]] = None
        product_ndc: Optional[List[str]] = None
        route: Optional[List[str]] = None
        rxcui: Optional[List[str]] = None
        spl_id: Optional[List[str]] = None
        spl_set_id: Optional[List[str]] = None
        substance_name: Optional[List[str]] = None
        unii: Optional[List[str]] = None

    @dataclass
    class Products:
        @dataclass
        class ActiveIngredients:
            name: Optional[str] = None
            strength: Optional[str] = None
        active_ingredients: Optional[ActiveIngredients] = None
        brand_name: Optional[List[str]] = None
        dosage_form: Optional[str] = None
        marketing_status: Optional[str] = None
        product_number: Optional[str] = None
        reference_drug: Optional[str] = None
        reference_standard: Optional[str] = None
        route: Optional[str] = None
        te_code: Optional[str] = None

    @dataclass
    class Submissions:
        submission_property_type: Optional[List[str]] = None
        application_docs: Optional[List[str]] = None
        review_priority: Optional[str] = None
        submission_class_code: Optional[str] = None
        submission_class_code_description: Optional[str] = None
        submission_number: Optional[str] = None
        submission_public_notes: Optional[str] = None
        submission_status: Optional[str] = None
        submission_status_date: Optional[datetime] = None
        submission_type: Optional[str] = None

    application_number: Optional[str] = None
    openfda: Optional[Openfda] = None
    products: Optional[Products] = None
    sponsor_name: Optional[str] = None
    submissions: Optional[Submissions] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/drug/drugsfda.json"

@dataclass
class FoodAdverseEventsQuery(BaseQuery):
    ENDPOINT_PATH = 'food/event.json'

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

@dataclass
class FoodRecallEnforcementsQuery(BaseQuery):
    ENDPOINT_PATH = 'food/enforcement.json'
    # missing attributes

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

@dataclass
class OtherHistoricalDocumentsQuery(BaseQuery):
    """
    Query for Other HistoricalDocuments.
    
    Endpoint: /other/historicaldocument.json
    """
    doc_type: Optional[str] = None
    year: Optional[str] = None
    num_of_pages: Optional[str] = None
    text: Optional[str] = None
    download_url: Optional[str] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/other/historicaldocument.json"

@dataclass
class OtherSubstanceDataReportsQuery(BaseQuery):
    """
    Query for Other SubstanceDataReports.
    
    Endpoint: /other/substance.json
    """

    @dataclass
    class CodesItem:
        code: Optional[str] = None
        code_system: Optional[str] = None
        comments: Optional[str] = None
        references: Optional[List[str]] = None
        type: Optional[str] = None
        url: Optional[str] = None
        uuid: Optional[str] = None

    @dataclass
    class Mixture:
        @dataclass
        class ComponentsItem:
            references: Optional[List[str]] = None
            @dataclass
            class Substance:
                linking_id: Optional[str] = None
                name: Optional[str] = None
                ref_pname: Optional[str] = None
                references: Optional[List[str]] = None
                refuuid: Optional[str] = None
                substance_class: Optional[str] = None
                unii: Optional[str] = None
                uuid: Optional[str] = None
            substance: Optional[Substance] = None
            type: Optional[str] = None
            uuid: Optional[str] = None
        components: Optional[List[ComponentsItem]] = None
        @dataclass
        class ParentSubstance:
            linking_id: Optional[str] = None
            name: Optional[str] = None
            ref_pname: Optional[str] = None
            references: Optional[List[str]] = None
            refuuid: Optional[str] = None
            substance_class: Optional[str] = None
            unii: Optional[str] = None
            uuid: Optional[str] = None
        parent_substance: Optional[ParentSubstance] = None
        references: Optional[List[str]] = None
        uuid: Optional[str] = None

    @dataclass
    class Modifications:
        @dataclass
        class AgentModificationsItem:
            agent_modification_process: Optional[str] = None
            agent_modification_role: Optional[str] = None
            agent_modification_type: Optional[str] = None
            @dataclass
            class AgentSubstance:
                linking_id: Optional[str] = None
                name: Optional[str] = None
                ref_pname: Optional[str] = None
                references: Optional[str] = None
                refuuid: Optional[str] = None
                substance_class: Optional[str] = None
                unii: Optional[str] = None
                uuid: Optional[str] = None
            agent_substance: Optional[AgentSubstance] = None
            @dataclass
            class Amount:
                average: Optional[str] = None
                high: Optional[str] = None
                high_limit: Optional[str] = None
                low: Optional[str] = None
                low_limit: Optional[str] = None
                non_numeric_value: Optional[str] = None
                references: Optional[List[str]] = None
                type: Optional[str] = None
                units: Optional[str] = None
                uuid: Optional[str] = None
            amount: Optional[Amount] = None
            modification_group: Optional[str] = None
            references: Optional[List[str]] = None
            uuid: Optional[str] = None
        agent_modifications: Optional[List[AgentModificationsItem]] = None
        @dataclass
        class PhysicalModificationsItem:
            modification_group: Optional[str] = None
            @dataclass
            class ParametersItem:
                @dataclass
                class Amount:
                    average: Optional[str] = None
                    high_limit: Optional[str] = None
                    low_limit: Optional[str] = None
                    non_numeric_value: Optional[str] = None
                    references: Optional[List[str]] = None
                    type: Optional[str] = None
                    units: Optional[str] = None
                    uuid: Optional[str] = None
                amount: Optional[Amount] = None
                parameter_name: Optional[str] = None
                references: Optional[str] = None
                uuid: Optional[str] = None
            parameters: Optional[List[ParametersItem]] = None
            physical_modification_role: Optional[str] = None
            references: Optional[List[str]] = None
            uuid: Optional[str] = None
        physical_modifications: Optional[List[PhysicalModificationsItem]] = None
        references: Optional[List[str]] = None
        @dataclass
        class StructuralModificationsItem:
            extent: Optional[str] = None
            @dataclass
            class ExtentAmount:
                average: Optional[str] = None
                high: Optional[str] = None
                high_limit: Optional[str] = None
                low: Optional[str] = None
                low_limit: Optional[str] = None
                non_numeric_value: Optional[str] = None
                references: Optional[List[str]] = None
                type: Optional[str] = None
                units: Optional[str] = None
                uuid: Optional[str] = None
            extent_amount: Optional[ExtentAmount] = None
            location_type: Optional[str] = None
            modification_group: Optional[str] = None
            @dataclass
            class MolecularFragment:
                linking_id: Optional[str] = None
                name: Optional[str] = None
                ref_pname: Optional[str] = None
                references: Optional[List[str]] = None
                refuuid: Optional[str] = None
                substance_class: Optional[str] = None
                unii: Optional[str] = None
                uuid: Optional[str] = None
            molecular_fragment: Optional[MolecularFragment] = None
            references: Optional[List[str]] = None
            residue_modified: Optional[str] = None
            @dataclass
            class SitesItem:
                residue_index: Optional[str] = None
                subunit_index: Optional[str] = None
            sites: Optional[List[SitesItem]] = None
            structural_modification_type: Optional[str] = None
            uuid: Optional[str] = None
        structural_modifications: Optional[List[StructuralModificationsItem]] = None
        uuid: Optional[str] = None

    @dataclass
    class MoietiesItem:
        atropisomerism: Optional[str] = None
        charge: Optional[str] = None
        count: Optional[str] = None
        @dataclass
        class CountAmount:
            average: Optional[str] = None
            high: Optional[str] = None
            high_limit: Optional[str] = None
            low: Optional[str] = None
            low_limit: Optional[str] = None
            non_numeric_value: Optional[str] = None
            references: Optional[List[str]] = None
            type: Optional[str] = None
            units: Optional[str] = None
            uuid: Optional[str] = None
        count_amount: Optional[CountAmount] = None
        defined_stereo: Optional[str] = None
        digest: Optional[str] = None
        ez_centers: Optional[str] = None
        formula: Optional[str] = None
        id: Optional[str] = None
        molecular_weight: Optional[str] = None
        molfile: Optional[str] = None
        optical_activity: Optional[str] = None
        references: Optional[List[str]] = None
        smiles: Optional[str] = None
        stereo_centers: Optional[str] = None
        stereo_comments: Optional[str] = None
        stereochemistry: Optional[str] = None
        uuid: Optional[str] = None

    @dataclass
    class Names:
        display_name: Optional[str] = None
        domains: Optional[List[str]] = None
        languages: Optional[List[str]] = None
        name: Optional[str] = None
        name_jurisdiction: Optional[List[str]] = None
        @dataclass
        class NameOrgsItem:
            deprecated_date: Optional[str] = None
            name_org: Optional[str] = None
            references: Optional[List[str]] = None
            uuid: Optional[str] = None
        name_orgs: Optional[List[NameOrgsItem]] = None
        preferred: Optional[str] = None
        references: Optional[List[str]] = None
        type: Optional[str] = None
        uuid: Optional[str] = None

    @dataclass
    class Notes:
        note: Optional[str] = None
        references: Optional[List[str]] = None
        uuid: Optional[str] = None

    @dataclass
    class NucleicAcid:
        @dataclass
        class LinkagesItem:
            linkage: Optional[str] = None
            references: Optional[List[str]] = None
            @dataclass
            class Sites:
                residue_index: Optional[str] = None
                subunit_index: Optional[str] = None
            sites: Optional[Sites] = None
            uuid: Optional[str] = None
        linkages: Optional[List[LinkagesItem]] = None
        nucleic_acid_sub_type: Optional[str] = None
        nucleic_acid_type: Optional[str] = None
        references: Optional[List[str]] = None
        sequence_origin: Optional[str] = None
        sequence_type: Optional[str] = None
        @dataclass
        class SubunitsItem:
            references: Optional[List[str]] = None
            sequence: Optional[str] = None
            subunit_index: Optional[str] = None
            uuid: Optional[str] = None
        subunits: Optional[List[SubunitsItem]] = None
        @dataclass
        class SugarsItem:
            references: Optional[List[str]] = None
            @dataclass
            class SitesItem:
                residue_index: Optional[str] = None
                subunit_index: Optional[str] = None
            sites: Optional[List[SitesItem]] = None
            sugar: Optional[str] = None
            uuid: Optional[str] = None
        sugars: Optional[List[SugarsItem]] = None
        uuid: Optional[str] = None

    @dataclass
    class Polymer:
        @dataclass
        class Classification:
            @dataclass
            class ParentSubstance:
                linking_id: Optional[str] = None
                name: Optional[str] = None
                ref_pname: Optional[str] = None
                references: Optional[List[str]] = None
                refuuid: Optional[str] = None
                substance_class: Optional[str] = None
                unii: Optional[str] = None
                uuid: Optional[str] = None
            parent_substance: Optional[ParentSubstance] = None
            polymer_class: Optional[str] = None
            polymer_geometry: Optional[str] = None
            polymer_subclass: Optional[List[str]] = None
            references: Optional[List[str]] = None
            source_type: Optional[str] = None
            uuid: Optional[str] = None
        classification: Optional[Classification] = None
        @dataclass
        class DisplayStructure:
            charge: Optional[str] = None
            count: Optional[str] = None
            defined_stereo: Optional[str] = None
            ez_centers: Optional[str] = None
            id: Optional[str] = None
            molecular_weight: Optional[str] = None
            molfile: Optional[str] = None
            optical_activity: Optional[str] = None
            references: Optional[List[str]] = None
            stereo_centers: Optional[str] = None
            stereochemistry: Optional[str] = None
        display_structure: Optional[DisplayStructure] = None
        @dataclass
        class IdealizedStructure:
            charge: Optional[str] = None
            count: Optional[str] = None
            defined_stereo: Optional[str] = None
            ez_centers: Optional[str] = None
            id: Optional[str] = None
            molecular_weight: Optional[str] = None
            molfile: Optional[str] = None
            optical_activity: Optional[str] = None
            references: Optional[List[str]] = None
            stereo_centers: Optional[str] = None
            stereochemistry: Optional[str] = None
        idealized_structure: Optional[IdealizedStructure] = None
        @dataclass
        class MonomersItem:
            amount: Optional[str] = None
            defining: Optional[str] = None
            @dataclass
            class MonomerSubstance:
                linking_id: Optional[str] = None
                name: Optional[str] = None
                ref_pname: Optional[str] = None
                references: Optional[List[str]] = None
                refuuid: Optional[str] = None
                substance_class: Optional[str] = None
                unii: Optional[str] = None
                uuid: Optional[str] = None
            monomer_substance: Optional[MonomerSubstance] = None
            references: Optional[List[str]] = None
            type: Optional[str] = None
            uuid: Optional[str] = None
        monomers: Optional[List[MonomersItem]] = None
        references: Optional[List[str]] = None
        @dataclass
        class StructuralUnitsItem:
            amount: Optional[str] = None
            attachment_count: Optional[str] = None
            attachment_map: Optional[str] = None
            label: Optional[str] = None
            structure: Optional[str] = None
            type: Optional[str] = None
        structural_units: Optional[List[StructuralUnitsItem]] = None
        uuid: Optional[str] = None

    @dataclass
    class PropertiesItem:
        defining: Optional[str] = None
        name: Optional[str] = None
        @dataclass
        class Parameters:
            name: Optional[str] = None
            references: Optional[List[str]] = None
            type: Optional[str] = None
            uuid: Optional[str] = None
            @dataclass
            class Value:
                average: Optional[str] = None
                high: Optional[str] = None
                low: Optional[str] = None
                non_numeric_value: Optional[str] = None
                references: Optional[List[str]] = None
                type: Optional[str] = None
                units: Optional[str] = None
                uuid: Optional[str] = None
            value: Optional[Value] = None
        parameters: Optional[Parameters] = None
        property_type: Optional[str] = None
        references: Optional[List[str]] = None
        type: Optional[str] = None
        uuid: Optional[str] = None
        @dataclass
        class Value:
            average: Optional[str] = None
            high: Optional[str] = None
            high_limit: Optional[str] = None
            low: Optional[str] = None
            low_limit: Optional[str] = None
            non_numeric_value: Optional[str] = None
            references: Optional[List[str]] = None
            type: Optional[str] = None
            units: Optional[str] = None
            uuid: Optional[str] = None
        value: Optional[Value] = None

    @dataclass
    class Protein:
        @dataclass
        class DisulfideLinksItem:
            @dataclass
            class Sites:
                residue_index: Optional[str] = None
                subunit_index: Optional[str] = None
            sites: Optional[Sites] = None
        disulfide_links: Optional[List[DisulfideLinksItem]] = None
        @dataclass
        class Glycosylation:
            @dataclass
            class CGlycosylationSitesItem:
                residue_index: Optional[str] = None
                subunit_index: Optional[str] = None
            c_glycosylation_sites: Optional[List[CGlycosylationSitesItem]] = None
            glycosylation_type: Optional[str] = None
            @dataclass
            class NGlycosylationSitesItem:
                residue_index: Optional[str] = None
                subunit_index: Optional[str] = None
            n_glycosylation_sites: Optional[List[NGlycosylationSitesItem]] = None
            @dataclass
            class OGlycosylationSitesItem:
                residue_index: Optional[str] = None
                subunit_index: Optional[str] = None
            o_glycosylation_sites: Optional[List[OGlycosylationSitesItem]] = None
            references: Optional[List[str]] = None
            uuid: Optional[str] = None
        glycosylation: Optional[Glycosylation] = None
        @dataclass
        class OtherLinksItem:
            linkage_type: Optional[str] = None
            references: Optional[List[str]] = None
            @dataclass
            class SitesItem:
                residue_index: Optional[str] = None
                subunit_index: Optional[str] = None
            sites: Optional[List[SitesItem]] = None
            uuid: Optional[str] = None
        other_links: Optional[List[OtherLinksItem]] = None
        protein_sub_type: Optional[str] = None
        protein_type: Optional[str] = None
        references: Optional[List[str]] = None
        sequence_origin: Optional[str] = None
        sequence_type: Optional[str] = None
        @dataclass
        class SubunitsItem:
            references: Optional[List[str]] = None
            sequence: Optional[str] = None
            subunit_index: Optional[str] = None
            uuid: Optional[str] = None
        subunits: Optional[List[SubunitsItem]] = None
        uuid: Optional[str] = None

    @dataclass
    class ReferencesItem:
        citation: Optional[str] = None
        doc_type: Optional[str] = None
        document_date: Optional[str] = None
        id: Optional[str] = None
        public_domain: Optional[str] = None
        tags: Optional[List[str]] = None
        url: Optional[str] = None
        uuid: Optional[str] = None

    @dataclass
    class RelationshipsItem:
        @dataclass
        class Amount:
            average: Optional[str] = None
            high: Optional[str] = None
            high_limit: Optional[str] = None
            low: Optional[str] = None
            low_limit: Optional[str] = None
            non_numeric_value: Optional[str] = None
            references: Optional[List[str]] = None
            type: Optional[str] = None
            units: Optional[str] = None
            uuid: Optional[str] = None
        amount: Optional[Amount] = None
        comments: Optional[str] = None
        interaction_type: Optional[str] = None
        @dataclass
        class MediatorSubstance:
            linking_id: Optional[str] = None
            name: Optional[str] = None
            ref_pname: Optional[str] = None
            references: Optional[List[str]] = None
            refuuid: Optional[str] = None
            substance_class: Optional[str] = None
            unii: Optional[str] = None
            uuid: Optional[str] = None
        mediator_substance: Optional[MediatorSubstance] = None
        qualification: Optional[str] = None
        references: Optional[List[str]] = None
        @dataclass
        class RelatedSubstance:
            linking_id: Optional[str] = None
            name: Optional[str] = None
            ref_pname: Optional[str] = None
            references: Optional[List[str]] = None
            refuuid: Optional[str] = None
            substance_class: Optional[str] = None
            unii: Optional[str] = None
            uuid: Optional[str] = None
        related_substance: Optional[RelatedSubstance] = None
        type: Optional[str] = None
        uuid: Optional[str] = None

    @dataclass
    class StructurallyDiverse:
        developmental_stage: Optional[str] = None
        fraction_material_type: Optional[str] = None
        fraction_name: Optional[str] = None
        @dataclass
        class HybridSpeciesMaternalOrganism:
            linking_id: Optional[str] = None
            name: Optional[str] = None
            ref_pname: Optional[str] = None
            references: Optional[List[str]] = None
            refuuid: Optional[str] = None
            substance_class: Optional[str] = None
            unii: Optional[str] = None
            uuid: Optional[str] = None
        hybrid_species_maternal_organism: Optional[HybridSpeciesMaternalOrganism] = None
        @dataclass
        class HybridSpeciesPaternalOrganism:
            linking_id: Optional[str] = None
            name: Optional[str] = None
            ref_pname: Optional[str] = None
            references: Optional[List[str]] = None
            refuuid: Optional[str] = None
            substance_class: Optional[str] = None
            unii: Optional[str] = None
            uuid: Optional[str] = None
        hybrid_species_paternal_organism: Optional[HybridSpeciesPaternalOrganism] = None
        infra_specific_name: Optional[str] = None
        infra_specific_type: Optional[str] = None
        organism_author: Optional[str] = None
        organism_family: Optional[str] = None
        organism_genus: Optional[str] = None
        organism_species: Optional[str] = None
        @dataclass
        class ParentSubstance:
            linking_id: Optional[str] = None
            name: Optional[str] = None
            ref_pname: Optional[str] = None
            references: Optional[List[str]] = None
            refuuid: Optional[str] = None
            substance_class: Optional[str] = None
            unii: Optional[str] = None
            uuid: Optional[str] = None
        parent_substance: Optional[ParentSubstance] = None
        part: Optional[List[str]] = None
        part_location: Optional[str] = None
        references: Optional[List[str]] = None
        source_material_class: Optional[str] = None
        source_material_state: Optional[str] = None
        source_material_type: Optional[str] = None
        uuid: Optional[str] = None

    @dataclass
    class Structure:
        atropisomerism: Optional[str] = None
        charge: Optional[str] = None
        count: Optional[str] = None
        defined_stereo: Optional[str] = None
        ez_centers: Optional[str] = None
        formula: Optional[str] = None
        id: Optional[str] = None
        molecular_weight: Optional[str] = None
        molfile: Optional[str] = None
        optical_activity: Optional[str] = None
        references: Optional[List[str]] = None
        smiles: Optional[str] = None
        stereo_centers: Optional[str] = None
        stereo_comments: Optional[str] = None
        stereochemistry: Optional[str] = None

    codes: Optional[List[CodesItem]] = None
    definition_level: Optional[str] = None
    definition_type: Optional[str] = None
    mixture: Optional[Mixture] = None
    modifications: Optional[Modifications] = None
    moieties: Optional[List[MoietiesItem]] = None
    names: Optional[Names] = None
    notes: Optional[Notes] = None
    nucleic_acid: Optional[NucleicAcid] = None
    polymer: Optional[Polymer] = None
    properties: Optional[List[PropertiesItem]] = None
    protein: Optional[Protein] = None
    references: Optional[List[ReferencesItem]] = None
    relationships: Optional[List[RelationshipsItem]] = None
    structurally_diverse: Optional[StructurallyDiverse] = None
    structure: Optional[Structure] = None
    substance_class: Optional[str] = None
    tags: Optional[List[str]] = None
    unii: Optional[str] = None
    uuid: Optional[str] = None
    version: Optional[str] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/other/substance.json"

@dataclass
class DrugProductLabelingQuery(BaseQuery):
    """
    Query for Drug Product Labeling.

    Endpoint: /drug/label.json

    This endpoint contains detailed labeling information for prescription and OTC drugs,
    including dosage, administration, warnings, adverse reactions, and more.

    Common search fields:
    - openfda.brand_name: Brand or trade name of the drug product
    - openfda.generic_name: Generic name(s) of the drug product
    - openfda.manufacturer_name: Name of manufacturer
    - indications_and_usage: Drug's indications for use
    - warnings: Serious adverse reactions and safety hazards
    - adverse_reactions: Information about undesirable effects
    """
    ENDPOINT_PATH: str = "/drug/label.json"

    @dataclass
    class Openfda:
        application_number: Optional[List[str]] = None
        brand_name: Optional[List[str]] = None
        generic_name: Optional[List[str]] = None
        is_original_packager: Optional[str] = None
        manufacturer_name: Optional[List[str]] = None
        nui: Optional[List[str]] = None
        original_packager_product_ndc: Optional[List[str]] = None
        package_ndc: Optional[List[str]] = None
        pharm_class_cs: Optional[List[str]] = None
        pharm_class_epc: Optional[List[str]] = None
        pharm_class_pe: Optional[List[str]] = None
        pharm_class_moa: Optional[List[str]] = None
        product_ndc: Optional[List[str]] = None
        product_type: Optional[List[str]] = None
        route: Optional[List[str]] = None
        rxcui: Optional[List[str]] = None
        spl_id: Optional[List[str]] = None
        spl_set_id: Optional[List[str]] = None
        substance_name: Optional[List[str]] = None
        unii: Optional[List[str]] = None
        upc: Optional[List[str]] = None

    # Core identification fields
    id: Optional[str] = None
    set_id: Optional[str] = None
    effective_time: Optional[datetime] = None
    version: Optional[str] = None

    # OpenFDA harmonized fields
    openfda: Optional[Openfda] = None

    # Main labeling content fields
    abuse: Optional[List[str]] = None
    active_ingredient: Optional[List[str]] = None
    adverse_reactions: Optional[List[str]] = None
    boxed_warning: Optional[List[str]] = None
    clinical_pharmacology: Optional[List[str]] = None
    clinical_studies: Optional[List[str]] = None
    contraindications: Optional[List[str]] = None
    controlled_substance: Optional[List[str]] = None
    dependence: Optional[List[str]] = None
    description: Optional[List[str]] = None
    dosage_and_administration: Optional[List[str]] = None
    dosage_forms_and_strengths: Optional[List[str]] = None
    drug_abuse_and_dependence: Optional[List[str]] = None
    drug_interactions: Optional[List[str]] = None
    geriatric_use: Optional[List[str]] = None
    how_supplied: Optional[List[str]] = None
    inactive_ingredient: Optional[List[str]] = None
    indications_and_usage: Optional[List[str]] = None
    information_for_patients: Optional[List[str]] = None
    instructions_for_use: Optional[List[str]] = None
    keep_out_of_reach_of_children: Optional[List[str]] = None
    labor_and_delivery: Optional[List[str]] = None
    mechanism_of_action: Optional[List[str]] = None
    microbiology: Optional[List[str]] = None
    nonclinical_toxicology: Optional[List[str]] = None
    nursing_mothers: Optional[List[str]] = None
    overdosage: Optional[List[str]] = None
    package_label_principal_display_panel: Optional[List[str]] = None
    patient_medication_information: Optional[List[str]] = None
    pediatric_use: Optional[List[str]] = None
    pharmacodynamics: Optional[List[str]] = None
    pharmacokinetics: Optional[List[str]] = None
    precautions: Optional[List[str]] = None
    pregnancy: Optional[List[str]] = None
    purpose: Optional[List[str]] = None
    recent_major_changes: Optional[List[str]] = None
    references: Optional[List[str]] = None
    storage_and_handling: Optional[List[str]] = None
    use_in_specific_populations: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    warnings_and_cautions: Optional[List[str]] = None

    # OTC-specific fields
    ask_doctor: Optional[List[str]] = None
    ask_doctor_or_pharmacist: Optional[List[str]] = None
    do_not_use: Optional[List[str]] = None
    questions: Optional[List[str]] = None
    stop_use: Optional[List[str]] = None
    when_using: Optional[List[str]] = None

    # Additional fields
    carcinogenesis_and_mutagenesis_and_impairment_of_fertility: Optional[List[str]] = None
    drug_and_or_laboratory_test_interactions: Optional[List[str]] = None
    general_precautions: Optional[List[str]] = None
    laboratory_tests: Optional[List[str]] = None
    nonteratogenic_effects: Optional[List[str]] = None
    other_safety_information: Optional[List[str]] = None
    pregnancy_or_breast_feeding: Optional[List[str]] = None
    spl_medguide: Optional[List[str]] = None
    spl_patient_package_insert: Optional[List[str]] = None
    spl_product_data_elements: Optional[List[str]] = None
    spl_unclassified_section: Optional[List[str]] = None
    teratogenic_effects: Optional[List[str]] = None
    user_safety_warnings: Optional[List[str]] = None

    # Animal/veterinary specific fields
    animal_pharmacology_and_or_toxicology: Optional[List[str]] = None
    information_for_owners_or_caregivers: Optional[List[str]] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

@dataclass
class DrugRecallEnforcementReportsQuery(BaseQuery):
    """
    Query for Drug Recall Enforcement Reports.

    Endpoint: /drug/enforcement.json

    This endpoint contains information about drug product recalls, including the reason
    for recall, classification, status, and distribution pattern.

    Common search fields:
    - classification: Recall classification (Class I, II, or III)
    - status: Recall status (On-Going, Completed, Terminated, Pending)
    - recalling_firm: The firm that initiated the recall
    - reason_for_recall: Why the product is being recalled
    - openfda.brand_name: Brand name of recalled drug
    """
    ENDPOINT_PATH: str = "/drug/enforcement.json"

    @dataclass
    class Openfda:
        application_number: Optional[List[str]] = None
        brand_name: Optional[List[str]] = None
        generic_name: Optional[List[str]] = None
        is_original_packager: Optional[str] = None
        manufacturer_name: Optional[List[str]] = None
        nui: Optional[List[str]] = None
        original_packager_product_ndc: Optional[List[str]] = None
        package_ndc: Optional[List[str]] = None
        pharm_class_cs: Optional[List[str]] = None
        pharm_class_epc: Optional[List[str]] = None
        pharm_class_pe: Optional[List[str]] = None
        pharm_class_moa: Optional[List[str]] = None
        product_ndc: Optional[List[str]] = None
        product_type: Optional[List[str]] = None
        route: Optional[List[str]] = None
        rxcui: Optional[List[str]] = None
        spl_id: Optional[List[str]] = None
        spl_set_id: Optional[List[str]] = None
        substance_name: Optional[List[str]] = None
        unii: Optional[List[str]] = None
        upc: Optional[List[str]] = None

    # Firm location information
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    # Recall classification and dates
    center_classification_date: Optional[datetime] = None
    classification: Optional[str] = None
    event_id: Optional[str] = None
    recall_initiation_date: Optional[datetime] = None
    recall_number: Optional[str] = None
    report_date: Optional[datetime] = None
    termination_date: Optional[datetime] = None

    # Product information
    code_info: Optional[str] = None
    more_code_info: Optional[str] = None
    distribution_pattern: Optional[str] = None
    initial_firm_notification: Optional[str] = None
    product_code: Optional[str] = None
    product_description: Optional[str] = None
    product_quantity: Optional[str] = None
    product_type: Optional[str] = None

    # Recall details
    reason_for_recall: Optional[str] = None
    recalling_firm: Optional[str] = None
    status: Optional[str] = None
    voluntary_mandated: Optional[str] = None

    # OpenFDA harmonized fields
    openfda: Optional[Openfda] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        # Validate classification if provided
        if self.classification:
            allowed_classifications = ['Class I', 'Class II', 'Class III']
            if self.classification not in allowed_classifications:
                raise ValueError(
                    f"classification must be one of {allowed_classifications}, got '{self.classification}'"
                )

        # Validate status if provided
        if self.status:
            allowed_statuses = ['On-Going', 'Completed', 'Terminated', 'Pending']
            if self.status not in allowed_statuses:
                raise ValueError(
                    f"status must be one of {allowed_statuses}, got '{self.status}'"
                )

@dataclass
class TobaccoProblemReportsQuery(BaseQuery):
    """
    Query for Tobacco ProblemReports.

    Endpoint: /tobacco/problem.json
    """
    report_id: Optional[str] = None
    date_submitted: Optional[datetime] = None
    number_tobacco_products: Optional[str] = None
    tobacco_products: Optional[List[str]] = None
    number_health_problems: Optional[str] = None
    reported_health_problems: Optional[List[str]] = None
    nonuser_affected: Optional[str] = None
    number_product_problems: Optional[str] = None
    reported_product_problems: Optional[List[str]] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/tobacco/problem.json"

@dataclass
class TransparencyCRLSQuery(BaseQuery):
    """
    Query for Transparency CRLS.
    
    Endpoint: /other/crls.json
    """
    file_name: Optional[str] = None
    application_number: Optional[str] = None
    letter_type: Optional[str] = None
    letter_date: Optional[str] = None
    company_name: Optional[str] = None
    company_rep: Optional[str] = None
    company_address: Optional[str] = None
    approval_name: Optional[str] = None
    approval_title: Optional[str] = None
    approval_center: Optional[str] = None
    text: Optional[str] = None

    def _validate_endpoint_specific(self) -> None:
        """Validate endpoint specific parameters."""
        pass

    ENDPOINT_PATH = "/other/crls.json"

@dataclass
class Record:
    """Individual record from FDA API response."""
    raw_record: Dict[str, Any]

@dataclass
class QueryResult:
    """Complete result from an FDA API query."""
    query: Optional[BaseQuery] = None
    total_results: int = 0
    records: List[Record] = None

    def __post_init__(self):
        if self.records is None:
            self.records = []


