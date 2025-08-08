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


class LineNatureIndicator(Enum):
    """Line nature indicator enumeration."""

    PRODUCT = "PRODUCT"
    SERVICE = "SERVICE"
    OTHER = "OTHER"


class UnitOfMeasure(Enum):
    """Unit of measure enumeration."""

    PIECE = "PIECE"
    KILOGRAM = "KILOGRAM"
    TON = "TON"
    KWH = "KWH"
    DAY = "DAY"
    HOUR = "HOUR"
    MINUTE = "MINUTE"
    MONTH = "MONTH"
    LITER = "LITER"
    KILOMETER = "KILOMETER"
    CUBIC_METER = "CUBIC_METER"
    METER = "METER"
    LINEAR_METER = "LINEAR_METER"
    CARTON = "CARTON"
    PACK = "PACK"
    OWN = "OWN"


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
    group_member_tax_number: Optional[TaxNumber] = None
    community_vat_number: Optional[str] = None
    bank_account_number: Optional[str] = None
    individual_exemption: Optional[bool] = None
    excise_licence_num: Optional[str] = None


@dataclass
class CustomerInfo:
    """Customer information data structure."""

    name: str
    tax_number: Optional[TaxNumber] = None
    vat_status: Optional[CustomerVatStatus] = None
    address: Optional[Address] = None
    community_vat_number: Optional[str] = None
    third_country_tax_number: Optional[str] = None
    bank_account_number: Optional[str] = None


@dataclass
class FiscalRepresentativeInfo:
    """Fiscal representative information data structure."""

    tax_number: TaxNumber
    name: str
    address: Address
    bank_account_number: Optional[str] = None


@dataclass
class AdditionalData:
    """Additional data structure for non-standardized fields."""

    data_name: str  # Unique identifier like A00001_RENDELES_SZAM
    data_description: str  # Description of the data field
    data_value: str  # The actual data value


@dataclass
class ConventionalInvoiceInfo:
    """Conventional invoice information structure."""

    order_numbers: Optional[List[str]] = None
    delivery_notes: Optional[List[str]] = None
    shipping_dates: Optional[List[str]] = None
    contract_numbers: Optional[List[str]] = None


@dataclass
class VatRate:
    """VAT rate data structure."""

    vat_percentage: Optional[float] = None
    vat_exemption: Optional[str] = None
    vat_out_of_scope: Optional[str] = None
    vat_domestic_reverse_charge: Optional[bool] = None


@dataclass
class LineAmountsNormal:
    """Line amounts for normal invoices."""

    line_net_amount: float
    line_net_amount_huf: float
    line_vat_rate: VatRate
    line_vat_amount: Optional[float] = None
    line_vat_amount_huf: Optional[float] = None
    line_gross_amount: Optional[float] = None
    line_gross_amount_huf: Optional[float] = None


@dataclass
class LineAmountsSimplified:
    """Line amounts for simplified invoices."""

    line_vat_rate: VatRate
    line_gross_amount: float
    line_gross_amount_huf: float


@dataclass
class InvoiceLine:
    """Invoice line item structure."""

    line_number: int
    line_expression_indicator: bool
    line_nature_indicator: Optional[LineNatureIndicator] = None
    line_description: Optional[str] = None
    quantity: Optional[float] = None
    unit_of_measure: Optional[UnitOfMeasure] = None
    unit_price: Optional[float] = None
    line_amounts_normal: Optional[LineAmountsNormal] = None
    line_amounts_simplified: Optional[LineAmountsSimplified] = None


@dataclass
class InvoiceLines:
    """Invoice lines structure."""

    lines: List[InvoiceLine]


@dataclass
class SummaryByVatRate:
    """Summary by VAT rate structure."""

    vat_rate: VatRate
    vat_rate_net_amount: float
    vat_rate_net_amount_huf: float
    vat_rate_vat_amount: float
    vat_rate_vat_amount_huf: float


@dataclass
class SummaryNormal:
    """Summary for normal invoices."""

    summary_by_vat_rate: List[SummaryByVatRate]
    invoice_net_amount: float
    invoice_net_amount_huf: float
    invoice_vat_amount: float
    invoice_vat_amount_huf: float


@dataclass
class InvoiceSummary:
    """Invoice summary structure."""

    invoice_gross_amount: Optional[float] = None
    invoice_gross_amount_huf: Optional[float] = None
    summary_normal: Optional[SummaryNormal] = None


@dataclass
class VatRate:
    """VAT rate data structure."""

    vat_percentage: Optional[float] = None  # VAT percentage (e.g., 27.0)
    vat_exemption: Optional[str] = None  # VAT exemption code
    vat_out_of_scope: Optional[str] = None  # VAT out of scope code
    vat_domestic_reverse_charge: Optional[bool] = None  # Domestic reverse charge


@dataclass
class LineAmountsNormal:
    """Line amounts for normal (non-simplified) invoices."""

    line_net_amount: float  # Net amount in invoice currency
    line_net_amount_huf: float  # Net amount in HUF
    line_vat_rate: VatRate  # VAT rate data
    line_vat_amount: Optional[float] = None  # VAT amount in invoice currency
    line_vat_amount_huf: Optional[float] = None  # VAT amount in HUF
    line_gross_amount: Optional[float] = None  # Gross amount in invoice currency
    line_gross_amount_huf: Optional[float] = None  # Gross amount in HUF


@dataclass
class LineAmountsSimplified:
    """Line amounts for simplified invoices."""

    line_vat_rate: VatRate  # VAT rate data
    line_gross_amount: float  # Gross amount in invoice currency
    line_gross_amount_huf: float  # Gross amount in HUF


@dataclass
class ProductCode:
    """Product code structure."""

    product_code_category: str  # Category of the product code
    product_code_value: Optional[str] = None  # Standard product code value
    product_code_own_value: Optional[str] = None  # Own product code value


@dataclass
class DiscountData:
    """Discount data structure."""

    discount_description: str  # Description of the discount
    discount_value: Optional[float] = None  # Discount value
    discount_rate: Optional[float] = None  # Discount rate as percentage


@dataclass
class InvoiceLine:
    """Invoice line item structure."""

    line_number: int  # Line number (starting from 1)
    line_expression_indicator: (
        bool  # True if quantity can be expressed in natural units
    )

    # Product/service description
    line_nature_indicator: Optional[LineNatureIndicator] = None
    line_description: Optional[str] = None

    # Quantity and pricing
    quantity: Optional[float] = None
    unit_of_measure: Optional[UnitOfMeasure] = None
    unit_of_measure_own: Optional[str] = None  # Custom unit of measure
    unit_price: Optional[float] = None  # Unit price in invoice currency
    unit_price_huf: Optional[float] = None  # Unit price in HUF

    # Line amounts (one of these should be filled based on invoice type)
    line_amounts_normal: Optional[LineAmountsNormal] = None
    line_amounts_simplified: Optional[LineAmountsSimplified] = None

    # Additional line data
    product_codes: Optional[List[ProductCode]] = None
    line_discount_data: Optional[DiscountData] = None
    intermediated_service: Optional[bool] = None
    deposit_indicator: Optional[bool] = None
    obligated_for_product_fee: Optional[bool] = None
    gpc_excise: Optional[float] = None  # Gas, electricity, coal excise tax in HUF
    neta_declaration: Optional[bool] = None

    # Structured additional data
    conventional_line_info: Optional[ConventionalInvoiceInfo] = None
    additional_line_data: Optional[List[AdditionalData]] = None


@dataclass
class InvoiceLines:
    """Invoice lines structure."""

    lines: List[InvoiceLine]  # List of invoice line items


@dataclass
class SummaryByVatRate:
    """Summary by VAT rate structure."""

    vat_rate: VatRate  # VAT rate or exemption
    vat_rate_net_amount: float  # Net amount for this VAT rate in invoice currency
    vat_rate_net_amount_huf: float  # Net amount for this VAT rate in HUF
    vat_rate_vat_amount: float  # VAT amount for this VAT rate in invoice currency
    vat_rate_vat_amount_huf: float  # VAT amount for this VAT rate in HUF
    vat_rate_gross_amount: Optional[float] = None  # Gross amount in invoice currency
    vat_rate_gross_amount_huf: Optional[float] = None  # Gross amount in HUF


@dataclass
class SummaryNormal:
    """Summary for normal (non-simplified) invoices."""

    summary_by_vat_rate: List[SummaryByVatRate]  # Breakdown by VAT rates
    invoice_net_amount: float  # Total net amount in invoice currency
    invoice_net_amount_huf: float  # Total net amount in HUF
    invoice_vat_amount: float  # Total VAT amount in invoice currency
    invoice_vat_amount_huf: float  # Total VAT amount in HUF


@dataclass
class SummarySimplified:
    """Summary for simplified invoices."""

    vat_rate: VatRate  # VAT rate or exemption
    vat_content_gross_amount: float  # Gross amount in invoice currency
    vat_content_gross_amount_huf: float  # Gross amount in HUF


@dataclass
class InvoiceSummary:
    """Invoice summary structure."""

    # Gross amounts (always present)
    invoice_gross_amount: Optional[float] = (
        None  # Total gross amount in invoice currency
    )
    invoice_gross_amount_huf: Optional[float] = None  # Total gross amount in HUF

    # Type-specific summaries (one of these should be filled)
    summary_normal: Optional[SummaryNormal] = None  # For normal and aggregate invoices
    summary_simplified: Optional[SummarySimplified] = None  # For simplified invoices


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
    """Detailed invoice data structure according to API documentation."""

    # Core invoice information
    invoice_number: str
    issue_date: datetime
    completion_date: Optional[datetime] = None
    completeness_indicator: Optional[bool] = None

    # Invoice classification and delivery
    invoice_category: Optional[InvoiceCategory] = None
    invoice_delivery_date: Optional[datetime] = None
    invoice_delivery_period_start: Optional[datetime] = None
    invoice_delivery_period_end: Optional[datetime] = None
    invoice_accounting_delivery_date: Optional[datetime] = None

    # Invoice indicators and flags
    periodical_settlement: Optional[bool] = None
    small_business_indicator: Optional[bool] = None
    utility_settlement_indicator: Optional[bool] = None
    self_billing_indicator: Optional[bool] = None
    cash_accounting_indicator: Optional[bool] = None

    # Currency and exchange
    currency_code: str = "HUF"
    exchange_rate: Optional[float] = None

    # Payment information
    payment_method: Optional[PaymentMethod] = None
    payment_date: Optional[datetime] = None

    # Invoice appearance and source
    invoice_appearance: Optional[InvoiceAppearance] = None
    source: Optional[Source] = None

    # Party information
    supplier_info: Optional[SupplierInfo] = None
    customer_info: Optional[CustomerInfo] = None
    fiscal_representative_info: Optional[FiscalRepresentativeInfo] = None

    # Financial amounts
    invoice_net_amount: Optional[float] = None
    invoice_vat_amount: Optional[float] = None
    invoice_gross_amount: Optional[float] = None
    invoice_net_amount_huf: Optional[float] = None
    invoice_vat_amount_huf: Optional[float] = None

    # Additional structured data
    conventional_invoice_info: Optional[ConventionalInvoiceInfo] = None
    additional_invoice_data: Optional[List[AdditionalData]] = None

    # Complex invoice content (structured data)
    invoice_lines: Optional[InvoiceLines] = None
    invoice_summary: Optional[InvoiceSummary] = None

    # Legacy/compatibility field
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class NavCredentials:
    """NAV API credentials."""

    login: str
    password: str
    signer_key: str
    tax_number: str


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

    # Core identification
    invoice_number: str
    invoice_issue_date: datetime
    completeness_indicator: bool

    # Invoice direction and operation
    invoice_direction: InvoiceDirection
    invoice_operation: Optional[InvoiceOperation] = None

    # Invoice reference (for modifications)
    invoice_reference: Optional[Dict[str, Any]] = None  # InvoiceReferenceType

    # Main invoice content
    invoice_head: Optional[Dict[str, Any]] = (
        None  # InvoiceHeadType - contains supplier/customer info and invoice detail
    )
    invoice_lines: Optional[InvoiceLines] = None  # LinesType - structured line items
    invoice_summary: Optional[InvoiceSummary] = None  # SummaryType - structured totals

    # Legacy compatibility fields
    supplier_info: Optional[SupplierInfo] = None
    customer_info: Optional[CustomerInfo] = None
    invoice_main: Optional[Dict[str, Any]] = None  # Complex structure - can be expanded
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
