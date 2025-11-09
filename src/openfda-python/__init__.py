"""FDA API client and data models."""

from .models import (
    # Base classes
    BaseQuery,
    Record,
    QueryResult,

    # Drug queries
    Drug_NDCQuery,
    DrugAdverseEventsQuery,
    DrugDrugShortagesQuery,
    DrugDrugsatFDAQuery,
    DrugProductLabelingQuery,
    DrugRecallEnforcementReportsQuery,

    # Device queries
    Device510kQuery,
    DeviceAdverseEventsQuery,
    DeviceClassificationQuery,
    DeviceCovid19TestingEvalsQuery,
    DevicePremarketApprovalQuery,
    DeviceRecalls,
    DeviceRecallEnforcementReports,
    DeviceRegistrationsListingsQuery,
    DeviceUniqueDeviceIDQuery,

    # Food queries
    FoodAdverseEventsQuery,
    FoodRecallEnforcementsQuery,

    # Animal/Veterinary queries
    AnimalVetAdverseEventsQuery,

    # Cosmetic queries
    CosmeticEventsQuery,

    # Tobacco queries
    TobaccoProblemReportsQuery,

    # Other queries
    OtherHistoricalDocumentsQuery,
    OtherSubstanceDataReportsQuery,
    TransparencyCRLSQuery,
)
from .openfda_client import FDAClient

__all__ = [
    # Base classes
    "BaseQuery",
    "Record",
    "QueryResult",

    # Client
    "FDAClient",

    # Drug queries
    "Drug_NDCQuery",
    "DrugAdverseEventsQuery",
    "DrugDrugShortagesQuery",
    "DrugDrugsatFDAQuery",
    "DrugProductLabelingQuery",
    "DrugRecallEnforcementReportsQuery",

    # Device queries
    "Device510kQuery",
    "DeviceAdverseEventsQuery",
    "DeviceClassificationQuery",
    "DeviceCovid19TestingEvalsQuery",
    "DevicePremarketApprovalQuery",
    "DeviceRecalls",
    "DeviceRecallEnforcementReports",
    "DeviceRegistrationsListingsQuery",
    "DeviceUniqueDeviceIDQuery",

    # Food queries
    "FoodAdverseEventsQuery",
    "FoodRecallEnforcementsQuery",

    # Animal/Veterinary queries
    "AnimalVetAdverseEventsQuery",

    # Cosmetic queries
    "CosmeticEventsQuery",

    # Tobacco queries
    "TobaccoProblemReportsQuery",

    # Other queries
    "OtherHistoricalDocumentsQuery",
    "OtherSubstanceDataReportsQuery",
    "TransparencyCRLSQuery",
]
