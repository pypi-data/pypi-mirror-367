"""
Main NAV Online Számla API client.

This module provides the main client class for interacting with the NAV Online Számla API.
"""

import logging
from datetime import datetime
from typing import List, Optional
import json
import base64

from .config import (
    ONLINE_SZAMLA_URL,
    MAX_DATE_RANGE_DAYS,
    SOFTWARE_ID,
    SOFTWARE_NAME,
    SOFTWARE_VERSION,
    SOFTWARE_DEV_NAME,
    SOFTWARE_DEV_CONTACT,
    SOFTWARE_DEV_COUNTRY,
)
from .models import (
    NavCredentials,
    InvoiceDirection,
    InvoiceDigest,
    InvoiceDetail,
    ErrorInfo,
    TaxNumber,
    SupplierInfo,
    CustomerInfo,
    Address,
    InvoiceLines,
    InvoiceSummary,
    InvoiceLine,
    VatRate,
    LineAmountsNormal,
    SummaryNormal,
    SummaryByVatRate,
    QueryInvoiceDigestRequest,
    QueryInvoiceCheckRequest,
    QueryInvoiceDataRequest,
    QueryInvoiceChainDigestRequest,
    MandatoryQueryParams,
    InvoiceQueryParams,
    DateRange,
    # API-compliant response types
    QueryInvoiceDigestResponseType,
    QueryInvoiceCheckResponseType,
    QueryInvoiceDataResponseType,
    InvoiceDigestType,
    BasicResultType,
    BasicHeaderType,
    InvoiceOperation,
)
from .exceptions import (
    NavApiException,
    NavValidationException,
    NavXmlParsingException,
    NavInvoiceNotFoundException,
)
from .utils import (
    generate_password_hash,
    generate_custom_id,
    calculate_request_signature,
    validate_tax_number,
    parse_xml_safely,
    get_xml_element_value,
    format_timestamp_for_nav,
    is_network_error,
    find_xml_elements_with_namespace_aware,
)
from .http_client import NavHttpClient

logger = logging.getLogger(__name__)


class NavOnlineInvoiceClient:
    """
    Main client for interacting with the NAV Online Számla API.

    This client provides methods for querying invoice data, getting invoice details,
    and managing invoice operations through the NAV API.
    """

    def __init__(self, base_url: str = ONLINE_SZAMLA_URL, timeout: int = 30):
        """
        Initialize the NAV API client.

        Args:
            base_url: Base URL for the NAV API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.http_client = NavHttpClient(base_url, timeout)

    def validate_credentials(self, credentials: NavCredentials) -> None:
        """
        Validate NAV API credentials.

        Args:
            credentials: NAV API credentials

        Raises:
            NavValidationException: If credentials are invalid
        """
        if not all([credentials.login, credentials.password, credentials.signer_key]):
            raise NavValidationException(
                "Missing required credentials: login, password, or signer_key"
            )

        if not validate_tax_number(credentials.tax_number):
            raise NavValidationException(
                f"Invalid tax number format: {credentials.tax_number}"
            )

    def get_token(self, credentials: NavCredentials) -> str:
        """
        Get exchange token from NAV API.

        Args:
            credentials: NAV API credentials

        Returns:
            str: Exchange token

        Raises:
            NavValidationException: If credentials are invalid
            NavApiException: If API call fails
        """
        self.validate_credentials(credentials)

        request_id = generate_custom_id()
        timestamp = format_timestamp_for_nav(datetime.now())

        # Build token exchange request
        password_hash = generate_password_hash(credentials.password)
        request_signature = calculate_request_signature(
            request_id, timestamp, credentials.signer_key
        )

        request_data = {
            "user": {
                "login": credentials.login,
                "passwordHash": password_hash,
                "taxNumber": credentials.tax_number,
                "requestSignature": request_signature,
            }
        }

        with self.http_client as client:
            headers = {"Content-Type": "application/json"}
            response = client.post("/tokenExchange", json.dumps(request_data), headers)

        try:
            response_data = response.json()
        except ValueError:
            raise NavApiException("Invalid JSON response from token exchange")

        if response_data.get("result", {}).get("funcCode") == "OK":
            return response_data["result"]["encodedExchangeToken"]
        else:
            error_code = response_data.get("result", {}).get(
                "errorCode", "UNKNOWN_ERROR"
            )
            message = response_data.get("result", {}).get(
                "message", "Token exchange failed"
            )
            raise NavApiException(f"{error_code}: {message}")

    def _build_basic_request_xml(
        self, credentials: NavCredentials, request_id: str, timestamp: str
    ) -> str:
        """
        Build basic request XML structure with authentication.

        Args:
            credentials: NAV API credentials
            request_id: Unique request ID
            timestamp: Request timestamp

        Returns:
            str: Basic XML request structure
        """
        password_hash = generate_password_hash(credentials.password)
        request_signature = calculate_request_signature(
            request_id, timestamp, credentials.signer_key
        )

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<QueryInvoiceDigestRequest xmlns="http://schemas.nav.gov.hu/OSA/3.0/api" xmlns:common="http://schemas.nav.gov.hu/NTCA/1.0/common">
    <common:header>
        <common:requestId>{request_id}</common:requestId>
        <common:timestamp>{timestamp}</common:timestamp>
        <common:requestVersion>3.0</common:requestVersion>
        <common:headerVersion>1.0</common:headerVersion>
    </common:header>
    <common:user>
        <common:login>{credentials.login}</common:login>
        <common:passwordHash cryptoType="SHA-512">{password_hash}</common:passwordHash>
        <common:taxNumber>{credentials.tax_number}</common:taxNumber>
        <common:requestSignature cryptoType="SHA3-512">{request_signature}</common:requestSignature>
    </common:user>
    <software>
        <softwareId>{SOFTWARE_ID}</softwareId>
        <softwareName>{SOFTWARE_NAME}</softwareName>
        <softwareOperation>LOCAL_SOFTWARE</softwareOperation>
        <softwareMainVersion>{SOFTWARE_VERSION}</softwareMainVersion>
        <softwareDevName>{SOFTWARE_DEV_NAME}</softwareDevName>
        <softwareDevContact>{SOFTWARE_DEV_CONTACT}</softwareDevContact>
        <softwareDevCountryCode>{SOFTWARE_DEV_COUNTRY}</softwareDevCountryCode>
        <softwareDevTaxNumber>{credentials.tax_number}</softwareDevTaxNumber>
    </software>"""

    def _build_query_invoice_data_xml(
        self,
        credentials: NavCredentials,
        invoice_number: str,
        invoice_direction: InvoiceDirection,
        supplier_tax_number: Optional[str] = None,
        batch_index: Optional[int] = None,
    ) -> str:
        """
        Build XML for queryInvoiceData request.

        Args:
            credentials: NAV API credentials
            invoice_number: Invoice number to query
            invoice_direction: Invoice direction
            supplier_tax_number: Optional supplier tax number
            batch_index: Optional batch index

        Returns:
            str: Complete XML request
        """
        request_id = generate_custom_id()
        timestamp = format_timestamp_for_nav()
        password_hash = generate_password_hash(credentials.password)
        request_signature = calculate_request_signature(
            request_id, timestamp, credentials.signer_key
        )

        supplier_tax_filter = ""
        if supplier_tax_number:
            supplier_tax_filter = (
                f"<supplierTaxNumber>{supplier_tax_number}</supplierTaxNumber>"
            )

        batch_index_filter = ""
        if batch_index is not None:
            batch_index_filter = f"<batchIndex>{batch_index}</batchIndex>"

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<QueryInvoiceDataRequest xmlns="http://schemas.nav.gov.hu/OSA/3.0/api" xmlns:common="http://schemas.nav.gov.hu/NTCA/1.0/common">
    <common:header>
        <common:requestId>{request_id}</common:requestId>
        <common:timestamp>{timestamp}</common:timestamp>
        <common:requestVersion>3.0</common:requestVersion>
        <common:headerVersion>1.0</common:headerVersion>
    </common:header>
    <common:user>
        <common:login>{credentials.login}</common:login>
        <common:passwordHash cryptoType="SHA-512">{password_hash}</common:passwordHash>
        <common:taxNumber>{credentials.tax_number}</common:taxNumber>
        <common:requestSignature cryptoType="SHA3-512">{request_signature}</common:requestSignature>
    </common:user>
    <software>
        <softwareId>{SOFTWARE_ID}</softwareId>
        <softwareName>{SOFTWARE_NAME}</softwareName>
        <softwareOperation>LOCAL_SOFTWARE</softwareOperation>
        <softwareMainVersion>{SOFTWARE_VERSION}</softwareMainVersion>
        <softwareDevName>{SOFTWARE_DEV_NAME}</softwareDevName>
        <softwareDevContact>{SOFTWARE_DEV_CONTACT}</softwareDevContact>
        <softwareDevCountryCode>{SOFTWARE_DEV_COUNTRY}</softwareDevCountryCode>
        <softwareDevTaxNumber>{credentials.tax_number}</softwareDevTaxNumber>
    </software>
    <invoiceNumberQuery>
        <invoiceNumber>{invoice_number}</invoiceNumber>
        <invoiceDirection>{invoice_direction.value}</invoiceDirection>
        {supplier_tax_filter}
        {batch_index_filter}
    </invoiceNumberQuery>
</QueryInvoiceDataRequest>"""

    def _build_query_invoice_digest_request_xml(
        self, credentials: NavCredentials, request: QueryInvoiceDigestRequest
    ) -> str:
        """Build XML for QueryInvoiceDigest request according to API specification."""
        request_id = generate_custom_id()
        timestamp = format_timestamp_for_nav()
        password_hash = generate_password_hash(credentials.password)
        request_signature = calculate_request_signature(
            request_id, timestamp, credentials.signer_key
        )

        # Build mandatory query params
        mandatory_params = ""
        if request.invoice_query_params.mandatory_query_params.invoice_issue_date:
            date_range = (
                request.invoice_query_params.mandatory_query_params.invoice_issue_date
            )
            mandatory_params += f"""
            <invoiceIssueDate>
                <dateFrom>{date_range.date_from}</dateFrom>
                <dateTo>{date_range.date_to}</dateTo>
            </invoiceIssueDate>"""

        if request.invoice_query_params.mandatory_query_params.ins_date:
            datetime_range = (
                request.invoice_query_params.mandatory_query_params.ins_date
            )
            mandatory_params += f"""
            <insDate>
                <dateTimeFrom>{datetime_range.date_time_from}</dateTimeFrom>
                <dateTimeTo>{datetime_range.date_time_to}</dateTimeTo>
            </insDate>"""

        if request.invoice_query_params.mandatory_query_params.original_invoice_number:
            orig_num = (
                request.invoice_query_params.mandatory_query_params.original_invoice_number
            )
            mandatory_params += f"""
            <originalInvoiceNumber>
                <originalInvoiceNumber>{orig_num.original_invoice_number}</originalInvoiceNumber>
            </originalInvoiceNumber>"""

        # Build additional query params
        additional_params = ""
        if request.invoice_query_params.additional_query_params:
            add_params = request.invoice_query_params.additional_query_params
            additional_elements = []

            if add_params.tax_number:
                additional_elements.append(
                    f"<taxNumber>{add_params.tax_number}</taxNumber>"
                )
            if add_params.group_member_tax_number:
                additional_elements.append(
                    f"<groupMemberTaxNumber>{add_params.group_member_tax_number}</groupMemberTaxNumber>"
                )
            if add_params.name:
                additional_elements.append(f"<name>{add_params.name}</name>")
            if add_params.invoice_category:
                additional_elements.append(
                    f"<invoiceCategory>{add_params.invoice_category.value}</invoiceCategory>"
                )
            if add_params.payment_method:
                additional_elements.append(
                    f"<paymentMethod>{add_params.payment_method.value}</paymentMethod>"
                )
            if add_params.invoice_appearance:
                additional_elements.append(
                    f"<invoiceAppearance>{add_params.invoice_appearance.value}</invoiceAppearance>"
                )
            if add_params.source:
                additional_elements.append(
                    f"<source>{add_params.source.value}</source>"
                )
            if add_params.currency:
                additional_elements.append(
                    f"<currency>{add_params.currency}</currency>"
                )

            if additional_elements:
                additional_params = f"""
        <additionalQueryParams>
            {''.join(additional_elements)}
        </additionalQueryParams>"""

        # Build relational query params
        relational_params = ""
        if request.invoice_query_params.relational_query_params:
            rel_params = request.invoice_query_params.relational_query_params
            relational_elements = []

            if rel_params.invoice_delivery:
                relational_elements.append(
                    f"""
            <invoiceDelivery>
                <queryOperator>{rel_params.invoice_delivery.query_operator.value}</queryOperator>
                <queryValue>{rel_params.invoice_delivery.query_value}</queryValue>
            </invoiceDelivery>"""
                )

            if rel_params.payment_date:
                relational_elements.append(
                    f"""
            <paymentDate>
                <queryOperator>{rel_params.payment_date.query_operator.value}</queryOperator>
                <queryValue>{rel_params.payment_date.query_value}</queryValue>
            </paymentDate>"""
                )

            if rel_params.invoice_net_amount:
                relational_elements.append(
                    f"""
            <invoiceNetAmount>
                <queryOperator>{rel_params.invoice_net_amount.query_operator.value}</queryOperator>
                <queryValue>{rel_params.invoice_net_amount.query_value}</queryValue>
            </invoiceNetAmount>"""
                )

            if rel_params.invoice_net_amount_huf:
                relational_elements.append(
                    f"""
            <invoiceNetAmountHUF>
                <queryOperator>{rel_params.invoice_net_amount_huf.query_operator.value}</queryOperator>
                <queryValue>{rel_params.invoice_net_amount_huf.query_value}</queryValue>
            </invoiceNetAmountHUF>"""
                )

            if rel_params.invoice_vat_amount:
                relational_elements.append(
                    f"""
            <invoiceVatAmount>
                <queryOperator>{rel_params.invoice_vat_amount.query_operator.value}</queryOperator>
                <queryValue>{rel_params.invoice_vat_amount.query_value}</queryValue>
            </invoiceVatAmount>"""
                )

            if rel_params.invoice_vat_amount_huf:
                relational_elements.append(
                    f"""
            <invoiceVatAmountHUF>
                <queryOperator>{rel_params.invoice_vat_amount_huf.query_operator.value}</queryOperator>
                <queryValue>{rel_params.invoice_vat_amount_huf.query_value}</queryValue>
            </invoiceVatAmountHUF>"""
                )

            if relational_elements:
                relational_params = f"""
        <relationalQueryParams>
            {''.join(relational_elements)}
        </relationalQueryParams>"""

        # Build transaction query params
        transaction_params = ""
        if request.invoice_query_params.transaction_query_params:
            trans_params = request.invoice_query_params.transaction_query_params
            transaction_elements = []

            if trans_params.transaction_id:
                transaction_elements.append(
                    f"<transactionId>{trans_params.transaction_id}</transactionId>"
                )
            if trans_params.index:
                transaction_elements.append(f"<index>{trans_params.index}</index>")
            if trans_params.invoice_operation:
                transaction_elements.append(
                    f"<invoiceOperation>{trans_params.invoice_operation.value}</invoiceOperation>"
                )

            if transaction_elements:
                transaction_params = f"""
        <transactionQueryParams>
            {''.join(transaction_elements)}
        </transactionQueryParams>"""

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<QueryInvoiceDigestRequest xmlns="http://schemas.nav.gov.hu/OSA/3.0/api" xmlns:common="http://schemas.nav.gov.hu/NTCA/1.0/common">
    <common:header>
        <common:requestId>{request_id}</common:requestId>
        <common:timestamp>{timestamp}</common:timestamp>
        <common:requestVersion>3.0</common:requestVersion>
        <common:headerVersion>1.0</common:headerVersion>
    </common:header>
    <common:user>
        <common:login>{credentials.login}</common:login>
        <common:passwordHash cryptoType="SHA-512">{password_hash}</common:passwordHash>
        <common:taxNumber>{credentials.tax_number}</common:taxNumber>
        <common:requestSignature cryptoType="SHA3-512">{request_signature}</common:requestSignature>
    </common:user>
    <software>
        <softwareId>{SOFTWARE_ID}</softwareId>
        <softwareName>{SOFTWARE_NAME}</softwareName>
        <softwareOperation>LOCAL_SOFTWARE</softwareOperation>
        <softwareMainVersion>{SOFTWARE_VERSION}</softwareMainVersion>
        <softwareDevName>{SOFTWARE_DEV_NAME}</softwareDevName>
        <softwareDevContact>{SOFTWARE_DEV_CONTACT}</softwareDevContact>
        <softwareDevCountryCode>{SOFTWARE_DEV_COUNTRY}</softwareDevCountryCode>
        <softwareDevTaxNumber>{credentials.tax_number}</softwareDevTaxNumber>
    </software>
    <page>{request.page}</page>
    <invoiceDirection>{request.invoice_direction.value}</invoiceDirection>
    <invoiceQueryParams>
        <mandatoryQueryParams>{mandatory_params}
        </mandatoryQueryParams>{additional_params}{relational_params}{transaction_params}
    </invoiceQueryParams>
</QueryInvoiceDigestRequest>"""

    def _build_query_invoice_check_request_xml(
        self, credentials: NavCredentials, request: QueryInvoiceCheckRequest
    ) -> str:
        """Build XML for QueryInvoiceCheck request according to API specification."""
        request_id = generate_custom_id()
        timestamp = format_timestamp_for_nav()
        password_hash = generate_password_hash(credentials.password)
        request_signature = calculate_request_signature(
            request_id, timestamp, credentials.signer_key
        )

        batch_index_filter = ""
        if request.batch_index is not None:
            batch_index_filter = f"<batchIndex>{request.batch_index}</batchIndex>"

        supplier_tax_filter = ""
        if request.supplier_tax_number:
            supplier_tax_filter = (
                f"<supplierTaxNumber>{request.supplier_tax_number}</supplierTaxNumber>"
            )

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<QueryInvoiceCheckRequest xmlns="http://schemas.nav.gov.hu/OSA/3.0/api" xmlns:common="http://schemas.nav.gov.hu/NTCA/1.0/common">
    <common:header>
        <common:requestId>{request_id}</common:requestId>
        <common:timestamp>{timestamp}</common:timestamp>
        <common:requestVersion>3.0</common:requestVersion>
        <common:headerVersion>1.0</common:headerVersion>
    </common:header>
    <common:user>
        <common:login>{credentials.login}</common:login>
        <common:passwordHash cryptoType="SHA-512">{password_hash}</common:passwordHash>
        <common:taxNumber>{credentials.tax_number}</common:taxNumber>
        <common:requestSignature cryptoType="SHA3-512">{request_signature}</common:requestSignature>
    </common:user>
    <software>
        <softwareId>{SOFTWARE_ID}</softwareId>
        <softwareName>{SOFTWARE_NAME}</softwareName>
        <softwareOperation>LOCAL_SOFTWARE</softwareOperation>
        <softwareMainVersion>{SOFTWARE_VERSION}</softwareMainVersion>
        <softwareDevName>{SOFTWARE_DEV_NAME}</softwareDevName>
        <softwareDevContact>{SOFTWARE_DEV_CONTACT}</softwareDevContact>
        <softwareDevCountryCode>{SOFTWARE_DEV_COUNTRY}</softwareDevCountryCode>
        <softwareDevTaxNumber>{credentials.tax_number}</softwareDevTaxNumber>
    </software>
    <invoiceNumberQuery>
        <invoiceNumber>{request.invoice_number}</invoiceNumber>
        <invoiceDirection>{request.invoice_direction.value}</invoiceDirection>
        {supplier_tax_filter}
        {batch_index_filter}
    </invoiceNumberQuery>
</QueryInvoiceCheckRequest>"""

    def _build_query_invoice_data_request_xml(
        self, credentials: NavCredentials, request: QueryInvoiceDataRequest
    ) -> str:
        """Build XML for QueryInvoiceData request according to API specification."""
        request_id = generate_custom_id()
        timestamp = format_timestamp_for_nav()
        password_hash = generate_password_hash(credentials.password)
        request_signature = calculate_request_signature(
            request_id, timestamp, credentials.signer_key
        )

        batch_index_filter = ""
        if request.batch_index is not None:
            batch_index_filter = f"<batchIndex>{request.batch_index}</batchIndex>"

        supplier_tax_filter = ""
        if request.supplier_tax_number:
            supplier_tax_filter = (
                f"<supplierTaxNumber>{request.supplier_tax_number}</supplierTaxNumber>"
            )

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<QueryInvoiceDataRequest xmlns="http://schemas.nav.gov.hu/OSA/3.0/api" xmlns:common="http://schemas.nav.gov.hu/NTCA/1.0/common">
    <common:header>
        <common:requestId>{request_id}</common:requestId>
        <common:timestamp>{timestamp}</common:timestamp>
        <common:requestVersion>3.0</common:requestVersion>
        <common:headerVersion>1.0</common:headerVersion>
    </common:header>
    <common:user>
        <common:login>{credentials.login}</common:login>
        <common:passwordHash cryptoType="SHA-512">{password_hash}</common:passwordHash>
        <common:taxNumber>{credentials.tax_number}</common:taxNumber>
        <common:requestSignature cryptoType="SHA3-512">{request_signature}</common:requestSignature>
    </common:user>
    <software>
        <softwareId>{SOFTWARE_ID}</softwareId>
        <softwareName>{SOFTWARE_NAME}</softwareName>
        <softwareOperation>LOCAL_SOFTWARE</softwareOperation>
        <softwareMainVersion>{SOFTWARE_VERSION}</softwareMainVersion>
        <softwareDevName>{SOFTWARE_DEV_NAME}</softwareDevName>
        <softwareDevContact>{SOFTWARE_DEV_CONTACT}</softwareDevContact>
        <softwareDevCountryCode>{SOFTWARE_DEV_COUNTRY}</softwareDevCountryCode>
        <softwareDevTaxNumber>{credentials.tax_number}</softwareDevTaxNumber>
    </software>
    <invoiceNumberQuery>
        <invoiceNumber>{request.invoice_number}</invoiceNumber>
        <invoiceDirection>{request.invoice_direction.value}</invoiceDirection>
        {supplier_tax_filter}
        {batch_index_filter}
    </invoiceNumberQuery>
</QueryInvoiceDataRequest>"""

    def _build_query_invoice_chain_digest_request_xml(
        self, credentials: NavCredentials, request: QueryInvoiceChainDigestRequest
    ) -> str:
        """Build XML for QueryInvoiceChainDigest request according to API specification."""
        request_id = generate_custom_id()
        timestamp = format_timestamp_for_nav()
        password_hash = generate_password_hash(credentials.password)
        request_signature = calculate_request_signature(
            request_id, timestamp, credentials.signer_key
        )

        tax_number_filter = ""
        if request.tax_number:
            tax_number_filter = f"<taxNumber>{request.tax_number}</taxNumber>"

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<QueryInvoiceChainDigestRequest xmlns="http://schemas.nav.gov.hu/OSA/3.0/api" xmlns:common="http://schemas.nav.gov.hu/NTCA/1.0/common">
    <common:header>
        <common:requestId>{request_id}</common:requestId>
        <common:timestamp>{timestamp}</common:timestamp>
        <common:requestVersion>3.0</common:requestVersion>
        <common:headerVersion>1.0</common:headerVersion>
    </common:header>
    <common:user>
        <common:login>{credentials.login}</common:login>
        <common:passwordHash cryptoType="SHA-512">{password_hash}</common:passwordHash>
        <common:taxNumber>{credentials.tax_number}</common:taxNumber>
        <common:requestSignature cryptoType="SHA3-512">{request_signature}</common:requestSignature>
    </common:user>
    <software>
        <softwareId>{SOFTWARE_ID}</softwareId>
        <softwareName>{SOFTWARE_NAME}</softwareName>
        <softwareOperation>LOCAL_SOFTWARE</softwareOperation>
        <softwareMainVersion>{SOFTWARE_VERSION}</softwareMainVersion>
        <softwareDevName>{SOFTWARE_DEV_NAME}</softwareDevName>
        <softwareDevContact>{SOFTWARE_DEV_CONTACT}</softwareDevContact>
        <softwareDevCountryCode>{SOFTWARE_DEV_COUNTRY}</softwareDevCountryCode>
        <softwareDevTaxNumber>{credentials.tax_number}</softwareDevTaxNumber>
    </software>
    <page>{request.page}</page>
    <invoiceNumber>{request.invoice_number}</invoiceNumber>
    <invoiceDirection>{request.invoice_direction.value}</invoiceDirection>
    {tax_number_filter}
</QueryInvoiceChainDigestRequest>"""

    def _parse_error_response(self, xml_response: str) -> ErrorInfo:
        """
        Parse error response from NAV API.

        Args:
            xml_response: XML response string

        Returns:
            ErrorInfo: Parsed error information
        """
        try:
            dom = parse_xml_safely(xml_response)

            error_code = get_xml_element_value(dom, "errorCode", "UNKNOWN")
            message = get_xml_element_value(dom, "message", "Unknown error")

            return ErrorInfo(
                error_code=error_code, message=message, timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to parse error response: {e}")
            return ErrorInfo(
                error_code="XML_PARSE_ERROR",
                message=f"Failed to parse error response: {str(e)}",
                timestamp=datetime.now(),
            )

    def _parse_invoice_digest_response(self, xml_response: str) -> List[InvoiceDigest]:
        """
        Parse invoice digest response from XML.

        Args:
            xml_response: XML response string

        Returns:
            List[InvoiceDigest]: List of invoice digests
        """
        try:
            dom = parse_xml_safely(xml_response)

            # Check for errors first
            error_elements = find_xml_elements_with_namespace_aware(dom, "errorCode")
            if error_elements:
                error_info = self._parse_error_response(xml_response)
                raise NavApiException(
                    f"NAV API Error: {error_info.error_code} - {error_info.message}"
                )

            invoices = []
            invoice_elements = find_xml_elements_with_namespace_aware(
                dom, "invoiceDigest"
            )

            for invoice_elem in invoice_elements:
                try:
                    # Extract basic invoice information
                    invoice_number = get_xml_element_value(
                        invoice_elem, "invoiceNumber", ""
                    )

                    # Parse dates
                    issue_date_str = get_xml_element_value(
                        invoice_elem, "issueDate", ""
                    )
                    issue_date = (
                        datetime.strptime(issue_date_str, "%Y-%m-%d")
                        if issue_date_str
                        else datetime.now()
                    )

                    completion_date_str = get_xml_element_value(
                        invoice_elem, "completionDate", ""
                    )
                    completion_date = None
                    if completion_date_str:
                        try:
                            completion_date = datetime.strptime(
                                completion_date_str, "%Y-%m-%d"
                            )
                        except ValueError:
                            pass

                    # Parse amounts
                    net_amount = float(
                        get_xml_element_value(invoice_elem, "invoiceNetAmount", "0")
                        or "0"
                    )
                    vat_amount = float(
                        get_xml_element_value(invoice_elem, "invoiceVatAmount", "0")
                        or "0"
                    )
                    gross_amount = float(
                        get_xml_element_value(invoice_elem, "invoiceGrossAmount", "0")
                        or "0"
                    )

                    # Parse other fields
                    operation = get_xml_element_value(
                        invoice_elem, "invoiceOperation", "CREATE"
                    )
                    supplier_name = get_xml_element_value(
                        invoice_elem, "supplierName", ""
                    )
                    supplier_tax_number = get_xml_element_value(
                        invoice_elem, "supplierTaxNumber", ""
                    )
                    customer_name = get_xml_element_value(
                        invoice_elem, "customerName", ""
                    )
                    customer_tax_number = get_xml_element_value(
                        invoice_elem, "customerTaxNumber", ""
                    )
                    currency_code = get_xml_element_value(
                        invoice_elem, "currencyCode", "HUF"
                    )
                    source = get_xml_element_value(invoice_elem, "source", "UNKNOWN")

                    # Parse batch index if present
                    batch_index_str = get_xml_element_value(
                        invoice_elem, "batchIndex", ""
                    )
                    batch_index = int(batch_index_str) if batch_index_str else None

                    digest = InvoiceDigest(
                        invoice_number=invoice_number,
                        batch_index=batch_index,
                        invoice_operation=InvoiceOperation(operation),
                        supplier_name=supplier_name,
                        supplier_tax_number=supplier_tax_number,
                        customer_name=customer_name,
                        customer_tax_number=customer_tax_number,
                        issue_date=issue_date,
                        completion_date=completion_date,
                        invoice_net_amount=net_amount,
                        invoice_vat_amount=vat_amount,
                        invoice_gross_amount=gross_amount,
                        currency_code=currency_code,
                        source=source,
                    )

                    invoices.append(digest)

                except Exception as e:
                    logger.warning(f"Failed to parse invoice element: {e}")
                    continue

            return invoices

        except NavApiException:
            raise
        except Exception as e:
            raise NavXmlParsingException(
                f"Failed to parse invoice digest response: {str(e)}"
            )

    def _parse_api_compliant_invoice_digest_response(
        self, xml_response: str
    ) -> QueryInvoiceDigestResponseType:
        """
        Parse invoice digest response from XML to API-compliant response type.

        Args:
            xml_response: XML response string

        Returns:
            QueryInvoiceDigestResponseType: API-compliant response with invoice digests
        """
        try:
            dom = parse_xml_safely(xml_response)

            # Check for errors first
            error_elements = find_xml_elements_with_namespace_aware(dom, "errorCode")
            if error_elements:
                error_info = self._parse_error_response(xml_response)
                raise NavApiException(
                    f"NAV API Error: {error_info.error_code} - {error_info.message}"
                )

            # Parse header
            header_elements = find_xml_elements_with_namespace_aware(dom, "header")
            header = None
            if header_elements:
                header_elem = header_elements[0]
                header = BasicHeaderType(
                    request_id=get_xml_element_value(header_elem, "requestId", ""),
                    timestamp=get_xml_element_value(header_elem, "timestamp", ""),
                    request_version=get_xml_element_value(
                        header_elem, "requestVersion", "3.0"
                    ),
                    header_version=get_xml_element_value(
                        header_elem, "headerVersion", "1.0"
                    ),
                )

            # Parse result
            result_elements = find_xml_elements_with_namespace_aware(dom, "result")
            result = None
            if result_elements:
                result_elem = result_elements[0]
                result = BasicResultType(
                    func_code=get_xml_element_value(result_elem, "funcCode", "ERROR"),
                    error_code=get_xml_element_value(result_elem, "errorCode", None),
                    message=get_xml_element_value(result_elem, "message", None),
                )

            # Parse invoice digests
            invoice_digests = []
            invoice_elements = find_xml_elements_with_namespace_aware(
                dom, "invoiceDigest"
            )

            logger.debug(f"Found {len(invoice_elements)} invoice digest elements")

            for invoice_elem in invoice_elements:
                try:
                    # Extract basic invoice information
                    invoice_number = get_xml_element_value(
                        invoice_elem, "invoiceNumber", ""
                    )

                    # The digest response doesn't contain invoiceDirection directly
                    # For now, assume OUTBOUND since we queried for OUTBOUND invoices
                    # This could be improved by looking at the supplier tax number vs our tax number
                    invoice_direction = InvoiceDirection.OUTBOUND

                    # Parse batch index
                    batch_index_str = get_xml_element_value(
                        invoice_elem, "batchIndex", ""
                    )
                    batch_index = int(batch_index_str) if batch_index_str else None

                    # Parse invoice operation and category
                    invoice_operation = get_xml_element_value(
                        invoice_elem, "invoiceOperation", None
                    )
                    invoice_category = get_xml_element_value(
                        invoice_elem, "invoiceCategory", None
                    )

                    # Parse invoice issue date
                    invoice_issue_date_str = get_xml_element_value(
                        invoice_elem, "invoiceIssueDate", ""
                    )
                    invoice_issue_date = None
                    if invoice_issue_date_str:
                        try:
                            invoice_issue_date = datetime.strptime(
                                invoice_issue_date_str, "%Y-%m-%d"
                            )
                        except ValueError:
                            logger.warning(
                                f"Could not parse invoice issue date: {invoice_issue_date_str}"
                            )

                    # Parse supplier information
                    supplier_tax_number = get_xml_element_value(
                        invoice_elem, "supplierTaxNumber", None
                    )
                    supplier_group_member_tax_number = get_xml_element_value(
                        invoice_elem, "supplierGroupMemberTaxNumber", None
                    )
                    supplier_name = get_xml_element_value(
                        invoice_elem, "supplierName", None
                    )

                    # Parse insertion date
                    ins_date_str = get_xml_element_value(invoice_elem, "insDate", "")
                    ins_date = None
                    if ins_date_str:
                        try:
                            ins_date = datetime.fromisoformat(
                                ins_date_str.replace("Z", "+00:00")
                            )
                        except ValueError:
                            logger.warning(f"Could not parse ins date: {ins_date_str}")

                    # Parse customer information
                    customer_tax_number = get_xml_element_value(
                        invoice_elem, "customerTaxNumber", None
                    )
                    customer_group_member_tax_number = get_xml_element_value(
                        invoice_elem, "customerGroupMemberTaxNumber", None
                    )
                    customer_name = get_xml_element_value(
                        invoice_elem, "customerName", None
                    )

                    # Parse payment information
                    payment_method = get_xml_element_value(
                        invoice_elem, "paymentMethod", None
                    )
                    payment_date_str = get_xml_element_value(
                        invoice_elem, "paymentDate", ""
                    )
                    payment_date = None
                    if payment_date_str:
                        try:
                            payment_date = datetime.strptime(
                                payment_date_str, "%Y-%m-%d"
                            )
                        except ValueError:
                            logger.warning(
                                f"Could not parse payment date: {payment_date_str}"
                            )

                    # Parse invoice appearance and source
                    invoice_appearance = get_xml_element_value(
                        invoice_elem, "invoiceAppearance", None
                    )
                    source = get_xml_element_value(invoice_elem, "source", None)

                    # Parse invoice delivery date
                    invoice_delivery_date_str = get_xml_element_value(
                        invoice_elem, "invoiceDeliveryDate", ""
                    )
                    invoice_delivery_date = None
                    if invoice_delivery_date_str:
                        try:
                            invoice_delivery_date = datetime.strptime(
                                invoice_delivery_date_str, "%Y-%m-%d"
                            )
                        except ValueError:
                            logger.warning(
                                f"Could not parse invoice delivery date: {invoice_delivery_date_str}"
                            )

                    # Parse currency and amounts
                    currency = get_xml_element_value(invoice_elem, "currency", None)

                    # Parse invoice amounts
                    invoice_net_amount_str = get_xml_element_value(
                        invoice_elem, "invoiceNetAmount", ""
                    )
                    invoice_net_amount = None
                    if invoice_net_amount_str:
                        try:
                            invoice_net_amount = float(invoice_net_amount_str)
                        except ValueError:
                            logger.warning(
                                f"Could not parse invoice net amount: {invoice_net_amount_str}"
                            )

                    invoice_net_amount_huf_str = get_xml_element_value(
                        invoice_elem, "invoiceNetAmountHUF", ""
                    )
                    invoice_net_amount_huf = None
                    if invoice_net_amount_huf_str:
                        try:
                            invoice_net_amount_huf = float(invoice_net_amount_huf_str)
                        except ValueError:
                            logger.warning(
                                f"Could not parse invoice net amount HUF: {invoice_net_amount_huf_str}"
                            )

                    invoice_vat_amount_str = get_xml_element_value(
                        invoice_elem, "invoiceVatAmount", ""
                    )
                    invoice_vat_amount = None
                    if invoice_vat_amount_str:
                        try:
                            invoice_vat_amount = float(invoice_vat_amount_str)
                        except ValueError:
                            logger.warning(
                                f"Could not parse invoice VAT amount: {invoice_vat_amount_str}"
                            )

                    invoice_vat_amount_huf_str = get_xml_element_value(
                        invoice_elem, "invoiceVatAmountHUF", ""
                    )
                    invoice_vat_amount_huf = None
                    if invoice_vat_amount_huf_str:
                        try:
                            invoice_vat_amount_huf = float(invoice_vat_amount_huf_str)
                        except ValueError:
                            logger.warning(
                                f"Could not parse invoice VAT amount HUF: {invoice_vat_amount_huf_str}"
                            )

                    # Parse transaction information
                    transaction_id = get_xml_element_value(
                        invoice_elem, "transactionId", None
                    )
                    index_str = get_xml_element_value(invoice_elem, "index", "")
                    index = None
                    if index_str:
                        try:
                            index = int(index_str)
                        except ValueError:
                            logger.warning(f"Could not parse index: {index_str}")

                    # Parse modification information
                    original_invoice_number = get_xml_element_value(
                        invoice_elem, "originalInvoiceNumber", None
                    )
                    modification_index_str = get_xml_element_value(
                        invoice_elem, "modificationIndex", ""
                    )
                    modification_index = None
                    if modification_index_str:
                        try:
                            modification_index = int(modification_index_str)
                        except ValueError:
                            logger.warning(
                                f"Could not parse modification index: {modification_index_str}"
                            )

                    # Parse other fields
                    completeness_indicator = (
                        get_xml_element_value(
                            invoice_elem, "completenessIndicator", "false"
                        )
                        == "true"
                    )
                    original_request_version = get_xml_element_value(
                        invoice_elem, "originalRequestVersion", None
                    )

                    logger.debug(
                        f"Parsed invoice digest: {invoice_number}, operation: {invoice_operation}, supplier: {supplier_tax_number}, customer: {customer_tax_number}"
                    )

                    digest = InvoiceDigestType(
                        invoice_number=invoice_number,
                        invoice_direction=invoice_direction,
                        batch_index=batch_index,
                        invoice_operation=invoice_operation,
                        invoice_category=invoice_category,
                        invoice_issue_date=invoice_issue_date,
                        supplier_tax_number=supplier_tax_number,
                        supplier_name=supplier_name,
                        ins_date=ins_date,
                        supplier_group_member_tax_number=supplier_group_member_tax_number,
                        customer_tax_number=customer_tax_number,
                        customer_group_member_tax_number=customer_group_member_tax_number,
                        customer_name=customer_name,
                        payment_method=payment_method,
                        payment_date=payment_date,
                        invoice_appearance=invoice_appearance,
                        source=source,
                        invoice_delivery_date=invoice_delivery_date,
                        currency=currency,
                        invoice_net_amount=invoice_net_amount,
                        invoice_net_amount_huf=invoice_net_amount_huf,
                        invoice_vat_amount=invoice_vat_amount,
                        invoice_vat_amount_huf=invoice_vat_amount_huf,
                        transaction_id=transaction_id,
                        index=index,
                        original_invoice_number=original_invoice_number,
                        modification_index=modification_index,
                        completeness_indicator=completeness_indicator,
                        original_request_version=original_request_version,
                    )

                    invoice_digests.append(digest)

                except Exception as e:
                    logger.warning(f"Failed to parse invoice element: {e}")
                    continue

            # Parse pagination info
            current_page = None
            available_page = None
            available_count = None

            digest_result_elements = find_xml_elements_with_namespace_aware(
                dom, "invoiceDigestResult"
            )

            if digest_result_elements:
                digest_result = digest_result_elements[0]
                current_page_str = get_xml_element_value(
                    digest_result, "currentPage", ""
                )
                available_page_str = get_xml_element_value(
                    digest_result, "availablePage", ""
                )
                available_count_str = get_xml_element_value(
                    digest_result, "availableCount", ""
                )

                current_page = int(current_page_str) if current_page_str else None
                available_page = int(available_page_str) if available_page_str else None
                available_count = (
                    int(available_count_str) if available_count_str else None
                )

                logger.debug(
                    f"Pagination: current_page={current_page}, available_page={available_page}, available_count={available_count}"
                )
            else:
                logger.warning("No invoiceDigestResult element found in response")

            return QueryInvoiceDigestResponseType(
                header=header,
                result=result,
                software=None,  # Software info not typically in digest response
                current_page=current_page,
                available_page=available_page,
                available_count=available_count,
                invoice_digests=invoice_digests,
            )

        except NavApiException:
            raise
        except Exception as e:
            raise NavXmlParsingException(
                f"Failed to parse invoice digest response: {str(e)}"
            )

    def get_invoice_detail(
        self,
        credentials: NavCredentials,
        invoice_number: str,
        invoice_direction: InvoiceDirection,
        supplier_tax_number: Optional[str] = None,
        batch_index: Optional[int] = None,
    ) -> QueryInvoiceDataResponseType:
        """
        Get detailed information for a specific invoice.

        Args:
            credentials: NAV API credentials
            invoice_number: Invoice number to query
            invoice_direction: Invoice direction (OUTBOUND/INBOUND)
            supplier_tax_number: Optional supplier tax number
            batch_index: Optional batch index for batched invoices

        Returns:
            QueryInvoiceDataResponseType: API-compliant response with detailed invoice data

        Raises:
            NavValidationException: If parameters are invalid
            NavInvoiceNotFoundException: If invoice not found
            NavApiException: If API request fails
        """
        self.validate_credentials(credentials)

        if not invoice_number:
            raise NavValidationException("Invoice number is required")

        try:
            xml_request = self._build_query_invoice_data_xml(
                credentials,
                invoice_number,
                invoice_direction,
                supplier_tax_number,
                batch_index,
            )
            response = self.http_client.post("queryInvoiceData", xml_request)

            return self._parse_invoice_detail_response(response.text)

        except Exception as e:
            if is_network_error(str(e)):
                logger.error(f"Network error after retries: {e}")
                raise NavApiException(f"Network error: {str(e)}")
            raise

    def _parse_invoice_detail_response(self, xml_response: str) -> InvoiceDetail:
        """
        Parse invoice detail response from XML.

        Args:
            xml_response: XML response string

        Returns:
            InvoiceDetail: Parsed invoice detail
        """
        try:

            dom = parse_xml_safely(xml_response)

            # Check for errors first
            error_elements = find_xml_elements_with_namespace_aware(dom, "errorCode")
            if error_elements:
                error_info = self._parse_error_response(xml_response)
                if error_info.error_code in ["INVOICE_NOT_FOUND", "NO_INVOICE_FOUND"]:
                    raise NavInvoiceNotFoundException(
                        f"Invoice not found: {error_info.message}"
                    )
                raise NavApiException(
                    f"NAV API Error: {error_info.error_code} - {error_info.message}"
                )

            # Extract the base64 encoded invoice data
            invoice_data_elements = find_xml_elements_with_namespace_aware(
                dom, "invoiceData"
            )
            if not invoice_data_elements:
                raise NavXmlParsingException("No invoice data found in response")

            # Decode the base64 invoice data
            encoded_invoice_data = invoice_data_elements[0].firstChild.nodeValue
            if not encoded_invoice_data:
                raise NavXmlParsingException("Empty invoice data in response")

            # Decode from base64
            decoded_invoice_xml = base64.b64decode(encoded_invoice_data).decode("utf-8")
            logger.debug(f"Decoded invoice XML: {decoded_invoice_xml}")

            # Parse the decoded invoice XML
            invoice_dom = parse_xml_safely(decoded_invoice_xml)

            # Extract basic invoice information
            invoice_number = get_xml_element_value(invoice_dom, "invoiceNumber", "")

            # Parse issue date
            issue_date_str = get_xml_element_value(invoice_dom, "invoiceIssueDate", "")
            issue_date = datetime.now()
            if issue_date_str:
                try:
                    issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d")
                except ValueError:
                    logger.warning(f"Could not parse issue date: {issue_date_str}")

            # Parse completion date (if available)
            completion_date = None
            completion_date_str = get_xml_element_value(
                invoice_dom, "completionDate", ""
            )
            if completion_date_str:
                try:
                    completion_date = datetime.strptime(completion_date_str, "%Y-%m-%d")
                except ValueError:
                    logger.warning(
                        f"Could not parse completion date: {completion_date_str}"
                    )

            # Parse completeness indicator
            completeness_indicator = None
            completeness_str = get_xml_element_value(
                invoice_dom, "completenessIndicator", ""
            )
            if completeness_str:
                completeness_indicator = completeness_str.lower() == "true"

            # Parse currency and exchange rate
            currency_code = get_xml_element_value(invoice_dom, "currencyCode", "HUF")
            exchange_rate_str = get_xml_element_value(invoice_dom, "exchangeRate", "")
            exchange_rate = None
            if exchange_rate_str:
                try:
                    exchange_rate = float(exchange_rate_str)
                except ValueError:
                    logger.warning(
                        f"Could not parse exchange rate: {exchange_rate_str}"
                    )

            # Parse invoice detail fields (paymentDate, paymentMethod, invoiceDeliveryDate, etc.)
            payment_date = None
            payment_method = None
            invoice_delivery_date = None
            invoice_category = None
            invoice_appearance = None
            periodical_settlement = None
            small_business_indicator = None

            invoice_detail_elements = find_xml_elements_with_namespace_aware(
                invoice_dom, "invoiceDetail"
            )
            if invoice_detail_elements:
                detail_elem = invoice_detail_elements[0]

                # Parse payment date
                payment_date_str = get_xml_element_value(detail_elem, "paymentDate", "")
                if payment_date_str:
                    try:
                        payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d")
                    except ValueError:
                        logger.warning(
                            f"Could not parse payment date: {payment_date_str}"
                        )

                # Parse other invoice detail fields
                payment_method_str = get_xml_element_value(
                    detail_elem, "paymentMethod", ""
                )
                if payment_method_str:
                    # Convert to enum if we have it defined
                    from .models import PaymentMethod

                    try:
                        payment_method = PaymentMethod(payment_method_str)
                    except ValueError:
                        payment_method = payment_method_str

                # Parse delivery date
                delivery_date_str = get_xml_element_value(
                    detail_elem, "invoiceDeliveryDate", ""
                )
                if delivery_date_str:
                    try:
                        invoice_delivery_date = datetime.strptime(
                            delivery_date_str, "%Y-%m-%d"
                        )
                    except ValueError:
                        logger.warning(
                            f"Could not parse delivery date: {delivery_date_str}"
                        )

                # Parse invoice category
                invoice_category_str = get_xml_element_value(
                    detail_elem, "invoiceCategory", ""
                )
                if invoice_category_str:
                    from .models import InvoiceCategory

                    try:
                        invoice_category = InvoiceCategory(invoice_category_str)
                    except ValueError:
                        invoice_category = invoice_category_str

                # Parse invoice appearance
                appearance_str = get_xml_element_value(
                    detail_elem, "invoiceAppearance", ""
                )
                if appearance_str:
                    from .models import InvoiceAppearance

                    try:
                        invoice_appearance = InvoiceAppearance(appearance_str)
                    except ValueError:
                        invoice_appearance = appearance_str

                # Parse periodical settlement
                periodical_str = get_xml_element_value(
                    detail_elem, "periodicalSettlement", ""
                )
                if periodical_str:
                    periodical_settlement = periodical_str.lower() == "true"

                # Parse small business indicator
                small_business_str = get_xml_element_value(
                    detail_elem, "smallBusinessIndicator", ""
                )
                if small_business_str:
                    small_business_indicator = small_business_str.lower() == "true"

            # Parse supplier information
            supplier_info = None
            supplier_elements = find_xml_elements_with_namespace_aware(
                invoice_dom, "supplierInfo"
            )
            if supplier_elements:
                supplier_elem = supplier_elements[0]
                supplier_name = get_xml_element_value(supplier_elem, "supplierName", "")

                # Parse community VAT number
                community_vat_number = get_xml_element_value(
                    supplier_elem, "communityVatNumber", ""
                )

                # Parse bank account number
                bank_account_number = get_xml_element_value(
                    supplier_elem, "supplierBankAccountNumber", ""
                )

                # Parse supplier tax number
                supplier_tax_number = None
                tax_num_elements = find_xml_elements_with_namespace_aware(
                    supplier_elem, "supplierTaxNumber"
                )
                if tax_num_elements:
                    taxpayer_id = get_xml_element_value(
                        tax_num_elements[0], "taxpayerId", ""
                    )
                    vat_code = get_xml_element_value(tax_num_elements[0], "vatCode", "")
                    county_code = get_xml_element_value(
                        tax_num_elements[0], "countyCode", ""
                    )
                    if taxpayer_id:
                        supplier_tax_number = TaxNumber(
                            taxpayer_id=taxpayer_id,
                            vat_code=vat_code,
                            county_code=county_code,
                        )

                # Parse supplier address
                supplier_address = None
                address_elements = find_xml_elements_with_namespace_aware(
                    supplier_elem, "supplierAddress"
                )
                if address_elements:
                    detailed_addr_elements = find_xml_elements_with_namespace_aware(
                        address_elements[0], "detailedAddress"
                    )
                    if detailed_addr_elements:
                        addr_elem = detailed_addr_elements[0]
                        supplier_address = Address(
                            country_code=get_xml_element_value(
                                addr_elem, "countryCode", ""
                            ),
                            postal_code=get_xml_element_value(
                                addr_elem, "postalCode", ""
                            ),
                            city=get_xml_element_value(addr_elem, "city", ""),
                            street_name=get_xml_element_value(
                                addr_elem, "streetName", ""
                            ),
                            public_place_category=get_xml_element_value(
                                addr_elem, "publicPlaceCategory", ""
                            ),
                            number=get_xml_element_value(addr_elem, "number", ""),
                        )

                if supplier_name or supplier_tax_number:
                    supplier_info = SupplierInfo(
                        name=supplier_name,
                        tax_number=supplier_tax_number,
                        address=supplier_address,
                        community_vat_number=community_vat_number or None,
                        bank_account_number=bank_account_number or None,
                    )

            # Parse customer information
            customer_info = None
            customer_elements = find_xml_elements_with_namespace_aware(
                invoice_dom, "customerInfo"
            )
            if customer_elements:
                customer_elem = customer_elements[0]
                customer_name = get_xml_element_value(customer_elem, "customerName", "")

                # Parse customer VAT status
                customer_vat_status = get_xml_element_value(
                    customer_elem, "customerVatStatus", ""
                )

                # Parse customer tax number
                customer_tax_number = None
                cust_vat_data = find_xml_elements_with_namespace_aware(
                    customer_elem, "customerVatData"
                )
                if cust_vat_data:
                    tax_num_elements = find_xml_elements_with_namespace_aware(
                        cust_vat_data[0], "customerTaxNumber"
                    )
                    if tax_num_elements:
                        taxpayer_id = get_xml_element_value(
                            tax_num_elements[0], "taxpayerId", ""
                        )
                        vat_code = get_xml_element_value(
                            tax_num_elements[0], "vatCode", ""
                        )
                        county_code = get_xml_element_value(
                            tax_num_elements[0], "countyCode", ""
                        )
                        if taxpayer_id:
                            customer_tax_number = TaxNumber(
                                taxpayer_id=taxpayer_id,
                                vat_code=vat_code,
                                county_code=county_code,
                            )

                # Parse customer address
                customer_address = None
                address_elements = find_xml_elements_with_namespace_aware(
                    customer_elem, "customerAddress"
                )
                if address_elements:
                    detailed_addr_elements = find_xml_elements_with_namespace_aware(
                        address_elements[0], "detailedAddress"
                    )
                    if detailed_addr_elements:
                        addr_elem = detailed_addr_elements[0]
                        customer_address = Address(
                            country_code=get_xml_element_value(
                                addr_elem, "countryCode", ""
                            ),
                            postal_code=get_xml_element_value(
                                addr_elem, "postalCode", ""
                            ),
                            city=get_xml_element_value(addr_elem, "city", ""),
                            street_name=get_xml_element_value(
                                addr_elem, "streetName", ""
                            ),
                            public_place_category=get_xml_element_value(
                                addr_elem, "publicPlaceCategory", ""
                            ),
                            number=get_xml_element_value(addr_elem, "number", ""),
                        )

                if customer_name or customer_tax_number:
                    customer_info = CustomerInfo(
                        name=customer_name,
                        tax_number=customer_tax_number,
                        address=customer_address,
                        vat_status=customer_vat_status or None,
                    )

            # Parse invoice amounts from summary
            invoice_net_amount = 0.0
            invoice_vat_amount = 0.0
            invoice_gross_amount = 0.0

            summary_elements = find_xml_elements_with_namespace_aware(
                invoice_dom, "invoiceSummary"
            )
            if summary_elements:
                summary_elem = summary_elements[0]
                # Try to get from summaryNormal first
                normal_summary = find_xml_elements_with_namespace_aware(
                    summary_elem, "summaryNormal"
                )
                if normal_summary:
                    net_amount_str = get_xml_element_value(
                        normal_summary[0], "invoiceNetAmount", "0"
                    )
                    vat_amount_str = get_xml_element_value(
                        normal_summary[0], "invoiceVatAmount", "0"
                    )

                    try:
                        invoice_net_amount = float(net_amount_str)
                        invoice_vat_amount = float(vat_amount_str)
                    except ValueError:
                        logger.warning(
                            f"Could not parse invoice amounts: net={net_amount_str}, vat={vat_amount_str}"
                        )

                # Get gross amount from summaryGrossData
                gross_summary = find_xml_elements_with_namespace_aware(
                    summary_elem, "summaryGrossData"
                )
                if gross_summary:
                    gross_amount_str = get_xml_element_value(
                        gross_summary[0], "invoiceGrossAmount", "0"
                    )
                    try:
                        invoice_gross_amount = float(gross_amount_str)
                    except ValueError:
                        logger.warning(
                            f"Could not parse gross amount: {gross_amount_str}"
                        )

            # Parse invoice lines
            invoice_lines = None
            lines_elements = find_xml_elements_with_namespace_aware(
                invoice_dom, "invoiceLines"
            )
            if lines_elements:
                lines_elem = lines_elements[0]

                # Parse merged item indicator
                merged_item_indicator = False
                merged_str = get_xml_element_value(
                    lines_elem, "mergedItemIndicator", ""
                )
                if merged_str:
                    merged_item_indicator = merged_str.lower() == "true"

                # Parse individual lines
                parsed_lines = []
                line_elements = find_xml_elements_with_namespace_aware(
                    lines_elem, "line"
                )

                for line_elem in line_elements:
                    try:
                        line_number_str = get_xml_element_value(
                            line_elem, "lineNumber", ""
                        )
                        line_number = int(line_number_str) if line_number_str else None

                        line_description = get_xml_element_value(
                            line_elem, "lineDescription", ""
                        )

                        # Parse line expression indicator
                        line_expression_str = get_xml_element_value(
                            line_elem, "lineExpressionIndicator", ""
                        )
                        line_expression_indicator = (
                            line_expression_str.lower() == "true"
                            if line_expression_str
                            else False
                        )

                        quantity_str = get_xml_element_value(line_elem, "quantity", "")
                        quantity = float(quantity_str) if quantity_str else None

                        unit_of_measure = get_xml_element_value(
                            line_elem, "unitOfMeasure", ""
                        )

                        unit_price_str = get_xml_element_value(
                            line_elem, "unitPrice", ""
                        )
                        unit_price = float(unit_price_str) if unit_price_str else None

                        # Parse line amounts (normal or simplified)
                        line_amounts = None
                        amounts_normal = find_xml_elements_with_namespace_aware(
                            line_elem, "lineAmountsNormal"
                        )

                        if amounts_normal:
                            amounts_elem = amounts_normal[0]

                            # Parse net amount
                            net_amount = None
                            net_amount_huf = None
                            net_data = find_xml_elements_with_namespace_aware(
                                amounts_elem, "lineNetAmountData"
                            )
                            if net_data:
                                net_str = get_xml_element_value(
                                    net_data[0], "lineNetAmount", ""
                                )
                                net_amount = float(net_str) if net_str else None

                                net_huf_str = get_xml_element_value(
                                    net_data[0], "lineNetAmountHUF", ""
                                )
                                net_amount_huf = (
                                    float(net_huf_str) if net_huf_str else net_amount
                                )

                            # Parse VAT rate
                            vat_rate = None
                            vat_rate_data = find_xml_elements_with_namespace_aware(
                                amounts_elem, "lineVatRate"
                            )
                            if vat_rate_data:
                                vat_percentage_str = get_xml_element_value(
                                    vat_rate_data[0], "vatPercentage", ""
                                )
                                if vat_percentage_str:
                                    vat_rate = VatRate(
                                        vat_percentage=float(vat_percentage_str)
                                    )

                            # Parse VAT amount
                            vat_amount = None
                            vat_amount_huf = None
                            vat_data = find_xml_elements_with_namespace_aware(
                                amounts_elem, "lineVatData"
                            )
                            if vat_data:
                                vat_str = get_xml_element_value(
                                    vat_data[0], "lineVatAmount", ""
                                )
                                vat_amount = float(vat_str) if vat_str else None

                                vat_huf_str = get_xml_element_value(
                                    vat_data[0], "lineVatAmountHUF", ""
                                )
                                vat_amount_huf = (
                                    float(vat_huf_str) if vat_huf_str else vat_amount
                                )

                            # Parse gross amount
                            gross_amount = None
                            gross_amount_huf = None
                            gross_data = find_xml_elements_with_namespace_aware(
                                amounts_elem, "lineGrossAmountData"
                            )
                            if gross_data:
                                gross_str = get_xml_element_value(
                                    gross_data[0], "lineGrossAmountNormal", ""
                                )
                                gross_amount = float(gross_str) if gross_str else None

                                gross_huf_str = get_xml_element_value(
                                    gross_data[0], "lineGrossAmountNormalHUF", ""
                                )
                                gross_amount_huf = (
                                    float(gross_huf_str)
                                    if gross_huf_str
                                    else gross_amount
                                )

                            line_amounts = LineAmountsNormal(
                                line_net_amount=net_amount,
                                line_net_amount_huf=net_amount_huf or net_amount or 0.0,
                                line_vat_rate=vat_rate,
                                line_vat_amount=vat_amount,
                                line_vat_amount_huf=vat_amount_huf,
                                line_gross_amount=gross_amount,
                                line_gross_amount_huf=gross_amount_huf,
                            )

                        invoice_line = InvoiceLine(
                            line_number=line_number,
                            line_expression_indicator=line_expression_indicator,
                            line_description=line_description,
                            quantity=quantity,
                            unit_of_measure=unit_of_measure,
                            unit_price=unit_price,
                            line_amounts_normal=line_amounts,
                        )

                        parsed_lines.append(invoice_line)

                    except Exception as e:
                        logger.warning(f"Failed to parse invoice line: {e}")
                        continue

                if parsed_lines:
                    invoice_lines = InvoiceLines(
                        lines=parsed_lines,
                    )

            # Parse invoice summary
            invoice_summary = None
            summary_elements = find_xml_elements_with_namespace_aware(
                invoice_dom, "invoiceSummary"
            )
            if summary_elements:
                summary_elem = summary_elements[0]

                # Parse normal summary
                normal_summary = find_xml_elements_with_namespace_aware(
                    summary_elem, "summaryNormal"
                )
                if normal_summary:
                    normal_elem = normal_summary[0]

                    # Parse summary by VAT rate
                    vat_rate_summaries = []
                    vat_rate_elements = find_xml_elements_with_namespace_aware(
                        normal_elem, "summaryByVatRate"
                    )

                    for vat_elem in vat_rate_elements:
                        try:
                            # Parse VAT rate
                            vat_rate = None
                            rate_elements = find_xml_elements_with_namespace_aware(
                                vat_elem, "vatRate"
                            )
                            if rate_elements:
                                vat_percentage_str = get_xml_element_value(
                                    rate_elements[0], "vatPercentage", ""
                                )
                                if vat_percentage_str:
                                    vat_rate = VatRate(
                                        vat_percentage=float(vat_percentage_str)
                                    )

                            # Parse net amount for this VAT rate
                            net_amount = None
                            net_amount_huf = None
                            net_data = find_xml_elements_with_namespace_aware(
                                vat_elem, "vatRateNetData"
                            )
                            if net_data:
                                net_str = get_xml_element_value(
                                    net_data[0], "vatRateNetAmount", ""
                                )
                                net_amount = float(net_str) if net_str else None

                                net_huf_str = get_xml_element_value(
                                    net_data[0], "vatRateNetAmountHUF", ""
                                )
                                net_amount_huf = (
                                    float(net_huf_str) if net_huf_str else net_amount
                                )

                            # Parse VAT amount for this VAT rate
                            vat_amount = None
                            vat_amount_huf = None
                            vat_data = find_xml_elements_with_namespace_aware(
                                vat_elem, "vatRateVatData"
                            )
                            if vat_data:
                                vat_str = get_xml_element_value(
                                    vat_data[0], "vatRateVatAmount", ""
                                )
                                vat_amount = float(vat_str) if vat_str else None

                                vat_huf_str = get_xml_element_value(
                                    vat_data[0], "vatRateVatAmountHUF", ""
                                )
                                vat_amount_huf = (
                                    float(vat_huf_str) if vat_huf_str else vat_amount
                                )

                            # Parse gross amount for this VAT rate
                            gross_amount = None
                            gross_data = find_xml_elements_with_namespace_aware(
                                vat_elem, "vatRateGrossData"
                            )
                            if gross_data:
                                gross_str = get_xml_element_value(
                                    gross_data[0], "vatRateGrossAmount", ""
                                )
                                gross_amount = float(gross_str) if gross_str else None

                            vat_summary = SummaryByVatRate(
                                vat_rate=vat_rate,
                                vat_rate_net_amount=net_amount or 0.0,
                                vat_rate_net_amount_huf=net_amount_huf
                                or net_amount
                                or 0.0,
                                vat_rate_vat_amount=vat_amount or 0.0,
                                vat_rate_vat_amount_huf=vat_amount_huf
                                or vat_amount
                                or 0.0,
                            )

                            vat_rate_summaries.append(vat_summary)

                        except Exception as e:
                            logger.warning(f"Failed to parse VAT rate summary: {e}")
                            continue

                    # Parse total amounts
                    total_net_str = get_xml_element_value(
                        normal_elem, "invoiceNetAmount", ""
                    )
                    total_net = float(total_net_str) if total_net_str else None

                    total_net_huf_str = get_xml_element_value(
                        normal_elem, "invoiceNetAmountHUF", ""
                    )
                    total_net_huf = (
                        float(total_net_huf_str) if total_net_huf_str else total_net
                    )

                    total_vat_str = get_xml_element_value(
                        normal_elem, "invoiceVatAmount", ""
                    )
                    total_vat = float(total_vat_str) if total_vat_str else None

                    total_vat_huf_str = get_xml_element_value(
                        normal_elem, "invoiceVatAmountHUF", ""
                    )
                    total_vat_huf = (
                        float(total_vat_huf_str) if total_vat_huf_str else total_vat
                    )

                    # Parse gross total from summaryGrossData
                    total_gross = None
                    total_gross_huf = None
                    gross_summary = find_xml_elements_with_namespace_aware(
                        summary_elem, "summaryGrossData"
                    )
                    if gross_summary:
                        total_gross_str = get_xml_element_value(
                            gross_summary[0], "invoiceGrossAmount", ""
                        )
                        total_gross = (
                            float(total_gross_str) if total_gross_str else None
                        )

                        total_gross_huf_str = get_xml_element_value(
                            gross_summary[0], "invoiceGrossAmountHUF", ""
                        )
                        total_gross_huf = (
                            float(total_gross_huf_str)
                            if total_gross_huf_str
                            else total_gross
                        )

                    summary_normal = SummaryNormal(
                        summary_by_vat_rate=vat_rate_summaries,
                        invoice_net_amount=total_net or 0.0,
                        invoice_net_amount_huf=total_net_huf or total_net or 0.0,
                        invoice_vat_amount=total_vat or 0.0,
                        invoice_vat_amount_huf=total_vat_huf or total_vat or 0.0,
                    )

                    invoice_summary = InvoiceSummary(
                        summary_normal=summary_normal,
                        invoice_gross_amount=total_gross,
                        invoice_gross_amount_huf=total_gross_huf,
                    )

            # Create the invoice detail object
            detail = InvoiceDetail(
                invoice_number=invoice_number,
                issue_date=issue_date,
                completion_date=completion_date,
                completeness_indicator=completeness_indicator,
                currency_code=currency_code,
                exchange_rate=exchange_rate,
                payment_date=payment_date,
                payment_method=payment_method,
                invoice_delivery_date=invoice_delivery_date,
                invoice_category=invoice_category,
                invoice_appearance=invoice_appearance,
                periodical_settlement=periodical_settlement,
                small_business_indicator=small_business_indicator,
                supplier_info=supplier_info,
                customer_info=customer_info,
                invoice_net_amount=invoice_net_amount,
                invoice_vat_amount=invoice_vat_amount,
                invoice_gross_amount=invoice_gross_amount,
                invoice_lines=invoice_lines,
                invoice_summary=invoice_summary,
            )

            return detail

        except (NavInvoiceNotFoundException, NavApiException):
            raise
        except Exception as e:
            logger.error(f"Error parsing invoice detail response: {str(e)}")
            raise NavXmlParsingException(
                f"Failed to parse invoice detail response: {str(e)}"
            )

    # New methods using API-compliant request types

    def query_invoice_digest(
        self, credentials: NavCredentials, request: QueryInvoiceDigestRequest
    ) -> QueryInvoiceDigestResponseType:
        """
        Query invoice digests using the official API request structure.

        Args:
            credentials: NAV API credentials
            request: QueryInvoiceDigestRequest with proper API structure

        Returns:
            QueryInvoiceDigestResponseType: API-compliant response with invoice digests

        Raises:
            NavValidationException: If request validation fails
            NavApiException: If API call fails
        """
        try:
            # Validate credentials
            self.validate_credentials(credentials)

            # Build XML request
            xml_request = self._build_query_invoice_digest_request_xml(
                credentials, request
            )
            logger.debug(f"Sending QueryInvoiceDigest XML request: {xml_request}")

            # Make API call
            with self.http_client as client:
                response = client.post("/queryInvoiceDigest", xml_request)
                xml_response = response.text

            logger.debug(f"Received QueryInvoiceDigest XML response: {xml_response}")

            # Parse response
            return self._parse_api_compliant_invoice_digest_response(xml_response)

        except (NavValidationException, NavApiException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in query_invoice_digest: {str(e)}")
            raise NavApiException(f"Unexpected error: {str(e)}")

    def query_invoice_check(
        self, credentials: NavCredentials, request: QueryInvoiceCheckRequest
    ) -> QueryInvoiceCheckResponseType:
        """
        Check if an invoice exists using the official API request structure.

        Args:
            credentials: NAV API credentials
            request: QueryInvoiceCheckRequest with proper API structure

        Returns:
            QueryInvoiceCheckResponseType: API-compliant response with check results

        Raises:
            NavValidationException: If request validation fails
            NavApiException: If API call fails
        """
        try:
            # Validate credentials
            self.validate_credentials(credentials)

            # Build XML request
            xml_request = self._build_query_invoice_check_request_xml(
                credentials, request
            )

            # Make API call
            with self.http_client as client:
                xml_response = client.post("/queryInvoiceCheck", xml_request)

            # Parse response
            try:
                dom = parse_xml_safely(xml_response.text)
                result_elements = find_xml_elements_with_namespace_aware(
                    dom, "invoiceCheckResult"
                )

                if result_elements:
                    return result_elements[0].firstChild.nodeValue.lower() == "true"
                else:
                    return False

            except Exception as e:
                raise NavXmlParsingException(
                    f"Failed to parse invoice check response: {str(e)}"
                )

        except (NavValidationException, NavApiException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in query_invoice_check: {str(e)}")
            raise NavApiException(f"Unexpected error: {str(e)}")

    def query_invoice_data(
        self, credentials: NavCredentials, request: QueryInvoiceDataRequest
    ) -> Optional[InvoiceDetail]:
        """
        Get full invoice data using the official API request structure.

        Args:
            credentials: NAV API credentials
            request: QueryInvoiceDataRequest with proper API structure

        Returns:
            Optional[InvoiceDetail]: Invoice detail if found, None otherwise

        Raises:
            NavValidationException: If request validation fails
            NavApiException: If API call fails
        """
        try:
            # Validate credentials
            self.validate_credentials(credentials)

            # Build XML request
            xml_request = self._build_query_invoice_data_request_xml(
                credentials, request
            )

            # Make API call
            with self.http_client as client:
                response = client.post("/queryInvoiceData", xml_request)

            # Parse response
            return self._parse_invoice_detail_response(response.text)

        except NavInvoiceNotFoundException:
            return None
        except (NavValidationException, NavApiException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in query_invoice_data: {str(e)}")
            raise NavApiException(f"Unexpected error: {str(e)}")

    def query_invoice_chain_digest(
        self, credentials: NavCredentials, request: QueryInvoiceChainDigestRequest
    ) -> List[InvoiceDigest]:
        """
        Query invoice chain digests using the official API request structure.

        Args:
            credentials: NAV API credentials
            request: QueryInvoiceChainDigestRequest with proper API structure

        Returns:
            List[InvoiceDigest]: List of invoice chain elements

        Raises:
            NavValidationException: If request validation fails
            NavApiException: If API call fails
        """
        try:
            # Validate credentials
            self.validate_credentials(credentials)

            # Build XML request
            xml_request = self._build_query_invoice_chain_digest_request_xml(
                credentials, request
            )

            # Make API call
            with self.http_client as client:
                xml_response = client.post("/queryInvoiceChainDigest", xml_request)

            # Parse response (reusing the same parser as it's similar structure)
            return self._parse_invoice_digest_response(xml_response)

        except (NavValidationException, NavApiException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in query_invoice_chain_digest: {str(e)}")
            raise NavApiException(f"Unexpected error: {str(e)}")

    def get_all_invoice_data_for_date_range(
        self,
        credentials: NavCredentials,
        start_date: datetime,
        end_date: datetime,
        invoice_direction: InvoiceDirection = InvoiceDirection.OUTBOUND,
    ) -> List[InvoiceDetail]:
        """
        Get all invoice data for a given date range by first querying invoice digests
        and then fetching detailed data for each invoice.

        Args:
            credentials: NAV API credentials
            start_date: Start date for the query range
            end_date: End date for the query range
            invoice_direction: Invoice direction to query (default: OUTBOUND)

        Returns:
            List[InvoiceDetail]: List of detailed invoice data

        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API requests fail
        """
        self.validate_credentials(credentials)

        if start_date >= end_date:
            raise NavValidationException("Start date must be before end date")

        # Validate date range is not too large
        date_diff = (end_date - start_date).days
        if date_diff > MAX_DATE_RANGE_DAYS:
            raise NavValidationException(
                f"Date range too large. Maximum allowed: {MAX_DATE_RANGE_DAYS} days"
            )

        all_invoice_details = []
        processed_count = 0

        try:
            logger.info(
                f"Starting comprehensive invoice data retrieval for date range: {start_date.date()} to {end_date.date()}"
            )

            # Step 1: Query invoice digests to get all invoices in the date range
            page = 1
            total_found = 0

            while True:
                logger.info(f"Querying invoice digests - page {page}")

                # Create date range for the query
                date_range = DateRange(
                    date_from=start_date.strftime("%Y-%m-%d"),
                    date_to=end_date.strftime("%Y-%m-%d"),
                )

                # Create mandatory query params with date range
                mandatory_params = MandatoryQueryParams(invoice_issue_date=date_range)

                # Create invoice query params
                invoice_query_params = InvoiceQueryParams(
                    mandatory_query_params=mandatory_params
                )

                # Create the digest request
                digest_request = QueryInvoiceDigestRequest(
                    page=page,
                    invoice_direction=invoice_direction,
                    invoice_query_params=invoice_query_params,
                )

                # Query invoice digests
                digest_response = self.query_invoice_digest(credentials, digest_request)

                if not digest_response.invoice_digests:
                    logger.info(f"No more invoices found on page {page}")
                    break

                total_found += len(digest_response.invoice_digests)
                logger.info(
                    f"Found {len(digest_response.invoice_digests)} invoices on page {page} (total so far: {total_found})"
                )

                # Step 2: Get detailed data for each invoice digest
                for digest in digest_response.invoice_digests:
                    try:
                        logger.info(
                            f"Fetching details for invoice: {digest.invoice_number}"
                        )

                        # Create detailed data request
                        # For OUTBOUND invoices, don't include supplier_tax_number as it causes API error
                        # For INBOUND invoices, include supplier_tax_number if available
                        supplier_tax_for_request = None
                        if digest.invoice_direction == InvoiceDirection.INBOUND:
                            supplier_tax_for_request = digest.supplier_tax_number

                        data_request = QueryInvoiceDataRequest(
                            invoice_number=digest.invoice_number,
                            invoice_direction=digest.invoice_direction,
                            batch_index=digest.batch_index,
                            supplier_tax_number=supplier_tax_for_request,
                        )

                        # Get detailed invoice data
                        invoice_detail = self.query_invoice_data(
                            credentials, data_request
                        )

                        if invoice_detail:
                            all_invoice_details.append(invoice_detail)
                            processed_count += 1

                            if processed_count % 10 == 0:
                                logger.info(
                                    f"Processed {processed_count} invoices so far..."
                                )
                        else:
                            logger.warning(
                                f"No detail data found for invoice: {digest.invoice_number}"
                            )

                    except NavInvoiceNotFoundException:
                        logger.warning(
                            f"Invoice details not found for: {digest.invoice_number}"
                        )
                        continue
                    except Exception as e:
                        logger.error(
                            f"Error processing invoice {digest.invoice_number}: {str(e)}"
                        )
                        # Continue with next invoice rather than failing completely
                        continue

                # Check if there are more pages
                if (
                    digest_response.available_page is None
                    or page >= digest_response.available_page
                ):
                    logger.info("All pages processed")
                    break

                page += 1

            logger.info(
                f"Completed invoice data retrieval. Total processed: {processed_count} invoices"
            )
            return all_invoice_details

        except (NavValidationException, NavApiException):
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in get_all_invoice_data_for_date_range: {str(e)}"
            )
            raise NavApiException(
                f"Unexpected error during comprehensive data retrieval: {str(e)}"
            )

    def get_all_invoice_data_for_date_range_with_progress(
        self,
        credentials: NavCredentials,
        start_date: datetime,
        end_date: datetime,
        invoice_direction: InvoiceDirection = InvoiceDirection.OUTBOUND,
        max_invoices: Optional[int] = None,
        progress_callback: Optional[callable] = None,
    ) -> List[InvoiceDetail]:
        """
        Get all invoice data for a given date range with progress reporting.

        Args:
            credentials: NAV API credentials
            start_date: Start date for the query range
            end_date: End date for the query range
            invoice_direction: Invoice direction to query (default: BOTH)
            max_invoices: Optional maximum number of invoices to process
            progress_callback: Optional callback function for progress updates
                             Called with (current_count, total_estimated, current_invoice_number)

        Returns:
            List[InvoiceDetail]: List of detailed invoice data

        Raises:
            NavValidationException: If parameters are invalid
            NavApiException: If API requests fail
        """
        self.validate_credentials(credentials)

        if start_date >= end_date:
            raise NavValidationException("Start date must be before end date")

        all_invoice_details = []
        processed_count = 0
        total_estimated = 0

        try:
            # First pass: count total invoices for progress estimation
            logger.info("Estimating total invoice count...")
            page = 1

            while True:
                date_range = DateRange(
                    date_from=start_date.strftime("%Y-%m-%d"),
                    date_to=end_date.strftime("%Y-%m-%d"),
                )

                mandatory_params = MandatoryQueryParams(invoice_issue_date=date_range)

                invoice_query_params = InvoiceQueryParams(
                    mandatory_query_params=mandatory_params
                )

                digest_request = QueryInvoiceDigestRequest(
                    page=page,
                    invoice_direction=invoice_direction,
                    invoice_query_params=invoice_query_params,
                )

                digest_response = self.query_invoice_digest(credentials, digest_request)

                if not digest_response.invoice_digests:
                    break

                total_estimated += len(digest_response.invoice_digests)

                if (
                    digest_response.available_page is None
                    or page >= digest_response.available_page
                ):
                    break

                page += 1

            logger.info(f"Estimated total invoices: {total_estimated}")

            # Apply max_invoices limit to estimation
            if max_invoices:
                total_estimated = min(total_estimated, max_invoices)

            # Second pass: actual data retrieval with progress reporting
            page = 1

            while True:
                date_range = DateRange(
                    date_from=start_date.strftime("%Y-%m-%d"),
                    date_to=end_date.strftime("%Y-%m-%d"),
                )

                mandatory_params = MandatoryQueryParams(invoice_issue_date=date_range)

                invoice_query_params = InvoiceQueryParams(
                    mandatory_query_params=mandatory_params
                )

                digest_request = QueryInvoiceDigestRequest(
                    page=page,
                    invoice_direction=invoice_direction,
                    invoice_query_params=invoice_query_params,
                )

                digest_response = self.query_invoice_digest(credentials, digest_request)

                if not digest_response.invoice_digests:
                    break

                for digest in digest_response.invoice_digests:
                    if max_invoices and processed_count >= max_invoices:
                        return all_invoice_details

                    try:
                        # For OUTBOUND invoices, don't include supplier_tax_number as it causes API error
                        # For INBOUND invoices, include supplier_tax_number if available
                        supplier_tax_for_request = None
                        if digest.invoice_direction == InvoiceDirection.INBOUND:
                            supplier_tax_for_request = digest.supplier_tax_number

                        data_request = QueryInvoiceDataRequest(
                            invoice_number=digest.invoice_number,
                            invoice_direction=digest.invoice_direction,
                            batch_index=digest.batch_index,
                            supplier_tax_number=supplier_tax_for_request,
                        )

                        invoice_detail = self.query_invoice_data(
                            credentials, data_request
                        )

                        if invoice_detail:
                            all_invoice_details.append(invoice_detail)
                            processed_count += 1

                            # Report progress
                            if progress_callback:
                                progress_callback(
                                    processed_count,
                                    total_estimated,
                                    digest.invoice_number,
                                )

                    except Exception as e:
                        logger.error(
                            f"Error processing invoice {digest.invoice_number}: {str(e)}"
                        )
                        continue

                if (
                    digest_response.available_page is None
                    or page >= digest_response.available_page
                ):
                    break

                page += 1

            return all_invoice_details

        except (NavValidationException, NavApiException):
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in get_all_invoice_data_for_date_range_with_progress: {str(e)}"
            )
            raise NavApiException(
                f"Unexpected error during comprehensive data retrieval: {str(e)}"
            )

    def close(self):
        """Close the HTTP client."""
        self.http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
