"""
NAV Online Számla Python client library.

This package provides a Python client for interacting with the Hungarian NAV 
(National Tax and Customs Administration) Online Invoice API.
"""

from .client import NavOnlineInvoiceClient
from .models import (
    NavCredentials,
    InvoiceDirection,
    InvoiceOperation,
    CustomerVatStatus,
    InvoiceDigest,
    InvoiceDetail,
    ApiResponse,
    # New API-compliant request types
    QueryInvoiceDigestRequest,
    QueryInvoiceCheckRequest,
    QueryInvoiceDataRequest,
    QueryInvoiceChainDigestRequest,
    MandatoryQueryParams,
    AdditionalQueryParams,
    RelationalQueryParams,
    TransactionQueryParams,
    InvoiceQueryParams,
    DateRange,
    DateTimeRange,
    OriginalInvoiceNumber,
    RelationalQueryParam,
    # New API-compliant response types
    BasicOnlineInvoiceResponseType,
    QueryInvoiceDigestResponseType,
    QueryInvoiceCheckResponseType,
    QueryInvoiceDataResponseType,
    QueryInvoiceChainDigestResponseType,
    InvoiceDigestType,
    InvoiceCheckResultType,
    InvoiceDataType,
    InvoiceChainDigestType,
    BasicResultType,
    BasicHeaderType,
    SoftwareType,
    NotificationType,
    # New enums
    InvoiceCategory,
    PaymentMethod,
    InvoiceAppearance,
    Source,
    QueryOperator,
)
from .exceptions import (
    NavApiException,
    NavAuthenticationException,
    NavValidationException,
    NavNetworkException,
    NavRateLimitException,
    NavXmlParsingException,
    NavConfigurationException,
    NavInvoiceNotFoundException,
    NavRequestSignatureException,
)

__version__ = "0.0.1"
__author__ = "Gergo Emmert"
__email__ = "gergo.emmert@fxltech.com"

__all__ = [
    # Main client
    "NavOnlineInvoiceClient",
    # Models and data classes
    "NavCredentials",
    "InvoiceDirection",
    "InvoiceOperation",
    "CustomerVatStatus",
    "InvoiceDigest",
    "InvoiceDetail",
    "ApiResponse",
    # API-compliant request types
    "QueryInvoiceDigestRequest",
    "QueryInvoiceCheckRequest",
    "QueryInvoiceDataRequest",
    "QueryInvoiceChainDigestRequest",
    "MandatoryQueryParams",
    "AdditionalQueryParams",
    "RelationalQueryParams",
    "TransactionQueryParams",
    "InvoiceQueryParams",
    "DateRange",
    "DateTimeRange",
    "OriginalInvoiceNumber",
    "RelationalQueryParam",
    # API-compliant response types
    "BasicOnlineInvoiceResponseType",
    "QueryInvoiceDigestResponseType",
    "QueryInvoiceCheckResponseType",
    "QueryInvoiceDataResponseType",
    "QueryInvoiceChainDigestResponseType",
    "InvoiceDigestType",
    "InvoiceCheckResultType",
    "InvoiceDataType",
    "InvoiceChainDigestType",
    "BasicResultType",
    "BasicHeaderType",
    "SoftwareType",
    "NotificationType",
    # Enums
    "InvoiceCategory",
    "PaymentMethod",
    "InvoiceAppearance",
    "Source",
    "QueryOperator",
    # Exceptions
    "NavApiException",
    "NavAuthenticationException",
    "NavValidationException",
    "NavNetworkException",
    "NavRateLimitException",
    "NavXmlParsingException",
    "NavConfigurationException",
    "NavInvoiceNotFoundException",
    "NavRequestSignatureException",
]
