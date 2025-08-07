"""
Data models for NAV Online Számla API.

This module contains the data classes and models used by the NAV Online Számla API client.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class InvoiceDirection(Enum):
    """Invoice direction enumeration."""

    OUTBOUND = "OUTBOUND"  # Kiállító oldali
    INBOUND = "INBOUND"  # Vevő oldali


class InvoiceOperation(Enum):
    """Invoice operation enumeration."""

    CREATE = "CREATE"
    MODIFY = "MODIFY"
    STORNO = "STORNO"


class InvoiceCategory(Enum):
    """Invoice category enumeration."""

    NORMAL = "NORMAL"
    SIMPLIFIED = "SIMPLIFIED"
    AGGREGATE = "AGGREGATE"


class PaymentMethod(Enum):
    """Payment method enumeration."""

    TRANSFER = "TRANSFER"
    CASH = "CASH"
    CARD = "CARD"
    VOUCHER = "VOUCHER"
    OTHER = "OTHER"


class InvoiceAppearance(Enum):
    """Invoice appearance enumeration."""

    PAPER = "PAPER"
    ELECTRONIC = "ELECTRONIC"
    EDI = "EDI"
    UNKNOWN = "UNKNOWN"


class Source(Enum):
    """Source enumeration."""

    WEB = "WEB"
    XML = "XML"
    MGM = "MGM"
    OPG = "OPG"


class QueryOperator(Enum):
    """Query operator enumeration for relational queries."""

    EQ = "EQ"  # Equal
    GT = "GT"  # Greater than
    GTE = "GTE"  # Greater than or equal
    LT = "LT"  # Less than
    LTE = "LTE"  # Less than or equal


class CustomerVatStatus(Enum):
    """Customer VAT status enumeration."""

    DOMESTIC = "DOMESTIC"  # Belföldi ÁFA alany
    PRIVATE_PERSON = "PRIVATE_PERSON"  # Nem ÁFA alany természetes személy
    OTHER = "OTHER"  # Egyéb


@dataclass
class TaxNumber:
    """Tax number data structure."""

    taxpayer_id: str  # 8 digit taxpayer ID
    vat_code: Optional[str] = None
    county_code: Optional[str] = None


@dataclass
class Address:
    """Address data structure."""

    country_code: str
    postal_code: str
    city: str
    additional_address_detail: Optional[str] = None
    street_name: Optional[str] = None
    public_place_category: Optional[str] = None
    number: Optional[str] = None


@dataclass
class SupplierInfo:
    """Supplier information data structure."""

    tax_number: TaxNumber
    name: str
    address: Address


@dataclass
class CustomerInfo:
    """Customer information data structure."""

    name: str
    tax_number: Optional[TaxNumber] = None
    vat_status: Optional[CustomerVatStatus] = None
    address: Optional[Address] = None
    community_vat_number: Optional[str] = None
    third_country_tax_number: Optional[str] = None


@dataclass
class InvoiceDigest:
    """Invoice digest data structure returned by queryInvoiceDigest."""

    invoice_number: str
    batch_index: Optional[int]
    invoice_operation: InvoiceOperation
    supplier_name: str
    supplier_tax_number: str
    customer_name: Optional[str]
    customer_tax_number: Optional[str]
    issue_date: datetime
    completion_date: Optional[datetime]
    invoice_net_amount: float
    invoice_vat_amount: float
    invoice_gross_amount: float
    currency_code: str
    source: str  # PAPER, ELECTRONIC, EDI, UNKNOWN


@dataclass
class InvoiceDetail:
    """Detailed invoice data structure."""

    invoice_number: str
    issue_date: datetime
    completion_date: Optional[datetime]
    currency_code: str
    exchange_rate: Optional[float]
    supplier_info: SupplierInfo
    customer_info: CustomerInfo
    invoice_net_amount: float
    invoice_vat_amount: float
    invoice_gross_amount: float
    source: str
    # Additional fields can be added as needed
    additional_data: Dict[str, Any]


@dataclass
class NavCredentials:
    """NAV API credentials."""

    login: str
    password: str
    signer_key: str
    tax_number: str = "32703094"  # Default tax number


@dataclass
class DateRange:
    """Date range structure."""

    date_from: str  # YYYY-MM-DD format
    date_to: str  # YYYY-MM-DD format


@dataclass
class DateTimeRange:
    """DateTime range structure."""

    date_time_from: str  # YYYY-MM-DDTHH:MM:SS.sssZ format
    date_time_to: str  # YYYY-MM-DDTHH:MM:SS.sssZ format


@dataclass
class OriginalInvoiceNumber:
    """Original invoice number structure."""

    original_invoice_number: str


@dataclass
class MandatoryQueryParams:
    """Mandatory query parameters according to API documentation.

    One of the following must be provided:
    - invoiceIssueDate: Date range for invoice issue date
    - insDate: DateTime range for processing timestamp
    - originalInvoiceNumber: Original invoice number for chain queries
    """

    invoice_issue_date: Optional[DateRange] = None
    ins_date: Optional[DateTimeRange] = None
    original_invoice_number: Optional[OriginalInvoiceNumber] = None


@dataclass
class AdditionalQueryParams:
    """Additional query parameters according to API documentation."""

    tax_number: Optional[str] = None  # 8 digit tax number
    group_member_tax_number: Optional[str] = None  # 8 digit group member tax number
    name: Optional[str] = None  # Supplier/customer name (min 5 chars)
    invoice_category: Optional[InvoiceCategory] = None
    payment_method: Optional[PaymentMethod] = None
    invoice_appearance: Optional[InvoiceAppearance] = None
    source: Optional[Source] = None
    currency: Optional[str] = None  # 3 letter currency code


@dataclass
class RelationalQueryParam:
    """Single relational query parameter structure."""

    query_operator: QueryOperator
    query_value: str  # Value depends on the field type (date, decimal, etc.)


@dataclass
class RelationalQueryParams:
    """Relational query parameters according to API documentation."""

    invoice_delivery: Optional[RelationalQueryParam] = None
    payment_date: Optional[RelationalQueryParam] = None
    invoice_net_amount: Optional[RelationalQueryParam] = None
    invoice_net_amount_huf: Optional[RelationalQueryParam] = None
    invoice_vat_amount: Optional[RelationalQueryParam] = None
    invoice_vat_amount_huf: Optional[RelationalQueryParam] = None


@dataclass
class TransactionQueryParams:
    """Transaction query parameters according to API documentation."""

    transaction_id: Optional[str] = None  # Pattern: [+a-zA-Z0-9_]{1,30}
    index: Optional[int] = None  # Range: 1-100
    invoice_operation: Optional[InvoiceOperation] = None


@dataclass
class InvoiceQueryParams:
    """Invoice query parameters structure according to API documentation."""

    mandatory_query_params: MandatoryQueryParams
    additional_query_params: Optional[AdditionalQueryParams] = None
    relational_query_params: Optional[RelationalQueryParams] = None
    transaction_query_params: Optional[TransactionQueryParams] = None


@dataclass
class QueryInvoiceDigestRequest:
    """Query invoice digest request according to API documentation."""

    page: int  # minInclusive = 1
    invoice_direction: InvoiceDirection
    invoice_query_params: InvoiceQueryParams


@dataclass
class QueryInvoiceCheckRequest:
    """Query invoice check request according to API documentation."""

    invoice_number: str
    invoice_direction: InvoiceDirection
    batch_index: Optional[int] = None  # minInclusive = 1
    supplier_tax_number: Optional[str] = None  # 8 digit tax number


@dataclass
class QueryInvoiceDataRequest:
    """Query invoice data request according to API documentation."""

    invoice_number: str
    invoice_direction: InvoiceDirection
    batch_index: Optional[int] = None  # minInclusive = 1
    supplier_tax_number: Optional[str] = None  # 8 digit tax number


@dataclass
class QueryInvoiceChainDigestRequest:
    """Query invoice chain digest request according to API documentation."""

    page: int  # minInclusive = 1
    invoice_number: str
    invoice_direction: InvoiceDirection
    tax_number: Optional[str] = None  # 8 digit tax number


@dataclass
class ErrorInfo:
    """Error information structure."""

    error_code: str
    message: str
    timestamp: datetime


@dataclass
class ApiResponse:
    """Generic API response structure."""

    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorInfo] = None
    transaction_id: Optional[str] = None


# API-compliant response types according to API documentation


@dataclass
class SoftwareType:
    """Software type according to API documentation."""

    software_id: str  # 18 character ID [0-9A-Z\-]{18}
    software_name: str
    software_operation: str  # LOCAL_SOFTWARE, ONLINE_SERVICE
    software_main_version: str
    software_dev_name: str
    software_dev_contact: str
    software_dev_country_code: Optional[str] = None  # 2 letter country code
    software_dev_tax_number: Optional[str] = None


@dataclass
class BasicHeaderType:
    """Basic header type for API responses."""

    request_id: str
    timestamp: datetime
    request_version: str
    header_version: str


@dataclass
class NotificationType:
    """Notification type for API responses."""

    notification_code: str
    notification_text: str


@dataclass
class BasicResultType:
    """Basic result type according to API documentation."""

    func_code: str  # OK, ERROR
    error_code: Optional[str] = None
    message: Optional[str] = None
    notifications: Optional[List[NotificationType]] = None


@dataclass
class BasicOnlineInvoiceResponseType:
    """Basic online invoice response type according to API documentation."""

    header: BasicHeaderType
    result: BasicResultType
    software: Optional[SoftwareType] = None


@dataclass
class InvoiceDigestType:
    """Invoice digest type according to API documentation."""

    invoice_number: str
    invoice_direction: InvoiceDirection
    batch_index: Optional[int] = None
    invoice_operation: Optional[str] = None  # CREATE, MODIFY, STORNO
    invoice_category: Optional[str] = None  # NORMAL, SIMPLIFIED, AGGREGATE
    invoice_issue_date: Optional[datetime] = None
    supplier_tax_number: Optional[str] = None
    supplier_name: Optional[str] = None
    ins_date: Optional[datetime] = None
    supplier_group_member_tax_number: Optional[str] = None
    customer_tax_number: Optional[str] = None
    customer_group_member_tax_number: Optional[str] = None
    customer_name: Optional[str] = None
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None
    invoice_appearance: Optional[str] = None
    source: Optional[str] = None
    invoice_delivery_date: Optional[datetime] = None
    currency: Optional[str] = None
    invoice_net_amount: Optional[float] = None
    invoice_net_amount_huf: Optional[float] = None
    invoice_vat_amount: Optional[float] = None
    invoice_vat_amount_huf: Optional[float] = None
    transaction_id: Optional[str] = None
    index: Optional[int] = None
    original_invoice_number: Optional[str] = None
    modification_index: Optional[int] = None
    completeness_indicator: Optional[bool] = None
    original_request_version: Optional[str] = None


@dataclass
class QueryInvoiceDigestResponseType(BasicOnlineInvoiceResponseType):
    """Query invoice digest response type according to API documentation."""

    current_page: Optional[int] = None
    available_page: Optional[int] = None
    available_count: Optional[int] = None
    invoice_digests: Optional[List[InvoiceDigestType]] = None


@dataclass
class InvoiceCheckResultType:
    """Invoice check result type according to API documentation."""

    invoice_number: str
    batch_index: Optional[int]
    invoice_direction: InvoiceDirection
    query_result_code: str  # FOUND, NOT_FOUND


@dataclass
class QueryInvoiceCheckResponseType(BasicOnlineInvoiceResponseType):
    """Query invoice check response type according to API documentation."""

    query_results: Optional[List[InvoiceCheckResultType]] = None


@dataclass
class InvoiceDataType:
    """Invoice data type according to API documentation."""

    invoice_number: str
    invoice_direction: InvoiceDirection
    supplier_info: SupplierInfo
    customer_info: CustomerInfo
    invoice_main: Dict[str, Any]  # Complex structure - can be expanded
    invoice_summary: Dict[str, Any]  # Complex structure - can be expanded
    # Additional fields as needed


@dataclass
class QueryInvoiceDataResponseType(BasicOnlineInvoiceResponseType):
    """Query invoice data response type according to API documentation."""

    invoice_data: Optional[InvoiceDataType] = None


@dataclass
class InvoiceChainDigestType:
    """Invoice chain digest type according to API documentation."""

    invoice_chain_query: str
    invoice_chain_element: List[InvoiceDigestType]


@dataclass
class QueryInvoiceChainDigestResponseType(BasicOnlineInvoiceResponseType):
    """Query invoice chain digest response type according to API documentation."""

    invoice_chain_digest_result: Optional[InvoiceChainDigestType] = None
