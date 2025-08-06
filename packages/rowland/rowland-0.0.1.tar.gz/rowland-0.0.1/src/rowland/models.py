"""Models for Rowland APIs."""

from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel


class DocumentStatus(str, Enum):
    """Document processing status."""

    QUEUED = "queued"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class DocumentType(str, Enum):
    """Document type classification."""

    AFFIDAVIT = "affidavit"
    AMENDMENT = "amendment"
    ASSIGNMENT = "assignment"
    AUTHORIZATION_FOR_EXPENDITURE = "authorization_for_expenditure"
    CHAIN_OF_TITLE = "chain_of_title"
    COMMUNITIZATION_AGREEMENT = "communitization_agreement"
    CONFIDENTIALITY_AGREEMENT = "confidentiality_agreement"
    DEED = "deed"
    DIVISION_ORDER = "division_order"
    EASEMENT = "easement"
    FARMOUT_AGREEMENT = "farmout_agreement"
    GAS_GATHERING_AGREEMENT = "gas_gathering_agreement"
    GAS_PROCESSING_AGREEMENT = "gas_processing_agreement"
    JOINT_OPERATING_AGREEMENT = "joint_operating_agreement"
    LEASE = "lease"
    LETTER_AGREEMENT = "letter_agreement"
    LETTER_OF_INTENT = "letter_of_intent"
    LIEN = "lien"
    MARKETING_AGREEMENT = "marketing_agreement"
    MINERAL_DEED = "mineral_deed"
    MORTGAGE = "mortgage"
    NOTICE_OF_EXTENSION = "notice_of_extension"
    PARTICIPATION_AGREEMENT = "participation_agreement"
    POOLING_AGREEMENT = "pooling_agreement"
    PRODUCTION_SHARING_AGREEMENT = "production_sharing_agreement"
    PURCHASE_AND_SALE_AGREEMENT = "purchase_and_sale_agreement"
    RATIFICATION = "ratification"
    REGULATORY_FILING = "regulatory_filing"
    RELEASE = "release"
    RIGHT_OF_WAY = "right_of_way"
    ROYALTY_DEED = "royalty_deed"
    SALTWATER_DISPOSAL_AGREEMENT = "saltwater_disposal_agreement"
    SUBORDINATION_AGREEMENT = "subordination_agreement"
    SOLAR_LEASE = "solar_lease"
    STIPULATION = "stipulation"
    SURFACE_USE_AGREEMENT = "surface_use_agreement"
    TITLE_REPORT = "title_report"
    UNITIZATION_AGREEMENT = "unitization_agreement"
    WELL_PROPOSAL = "well_proposal"
    WIND_LEASE = "wind_lease"
    OTHER = "other"


class Document(BaseModel):
    """Document model."""

    id: str
    name: str
    folder_id: str | None = None
    s3_key: str | None = None
    file_size: int | None = None
    mime_type: str | None = None
    owner_id: str | None = None
    owner_organization_id: str | None = None
    summary: str | None = None
    status: DocumentStatus
    document_type: DocumentType = DocumentType.OTHER
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DocumentExtractionResponse(BaseModel):
    """Document extraction response model."""

    document_id: str
    document_name: str
    extraction_id: str
    consolidated_objects: list[dict[str, Any]] | None = None
    total_objects_found: int | None = None
    review_notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""

    items: list[T]
    total: int
    offset: int
    limit: int
    has_next: bool
    has_previous: bool
