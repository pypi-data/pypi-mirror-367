
###########################################################################
#
# LICENSE AGREEMENT
#
# Copyright (c) 2014-2024 joonis new media, Thimo Kraemer
#
# 1. Recitals
#
# joonis new media, Inh. Thimo Kraemer ("Licensor"), provides you
# ("Licensee") the program "PyFinTech" and associated documentation files
# (collectively, the "Software"). The Software is protected by German
# copyright laws and international treaties.
#
# 2. Public License
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this Software, to install and use the Software, copy, publish
# and distribute copies of the Software at any time, provided that this
# License Agreement is included in all copies or substantial portions of
# the Software, subject to the terms and conditions hereinafter set forth.
#
# 3. Temporary Multi-User/Multi-CPU License
#
# Licensor hereby grants to Licensee a temporary, non-exclusive license to
# install and use this Software according to the purpose agreed on up to
# an unlimited number of computers in its possession, subject to the terms
# and conditions hereinafter set forth. As consideration for this temporary
# license to use the Software granted to Licensee herein, Licensee shall
# pay to Licensor the agreed license fee.
#
# 4. Restrictions
#
# You may not use this Software in a way other than allowed in this
# license. You may not:
#
# - modify or adapt the Software or merge it into another program,
# - reverse engineer, disassemble, decompile or make any attempt to
#   discover the source code of the Software,
# - sublicense, rent, lease or lend any portion of the Software,
# - publish or distribute the associated license keycode.
#
# 5. Warranty and Remedy
#
# To the extent permitted by law, THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF QUALITY, TITLE, NONINFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, regardless of
# whether Licensor knows or had reason to know of Licensee particular
# needs. No employee, agent, or distributor of Licensor is authorized
# to modify this warranty, nor to make any additional warranties.
#
# IN NO EVENT WILL LICENSOR BE LIABLE TO LICENSEE FOR ANY DAMAGES,
# INCLUDING ANY LOST PROFITS, LOST SAVINGS, OR OTHER INCIDENTAL OR
# CONSEQUENTIAL DAMAGES ARISING FROM THE USE OR THE INABILITY TO USE THE
# SOFTWARE, EVEN IF LICENSOR OR AN AUTHORIZED DEALER OR DISTRIBUTOR HAS
# BEEN ADVISED OF THE POSSIBILITY OF THESE DAMAGES, OR FOR ANY CLAIM BY
# ANY OTHER PARTY. This does not apply if liability is mandatory due to
# intent or gross negligence.


"""
SEPA module of the Python Fintech package.

This module defines functions and classes to work with SEPA.
"""

__all__ = ['Account', 'Amount', 'SEPATransaction', 'SEPACreditTransfer', 'SEPADirectDebit', 'CAMTDocument', 'Mandate', 'MandateManager']

class Account:
    """Account class"""

    def __init__(self, iban, name, country=None, city=None, postcode=None, street=None):
        """
        Initializes the account instance.

        :param iban: Either the IBAN or a 2-tuple in the form of
            either (IBAN, BIC) or (ACCOUNT_NUMBER, BANK_CODE).
            The latter will be converted to the corresponding
            IBAN automatically. An IBAN is checked for validity.
        :param name: The name of the account holder.
        :param country: The country (ISO-3166 ALPHA 2) of the account
            holder (optional).
        :param city: The city of the account holder (optional).
        :param postcode: The postcode of the account holder (optional).
        :param street: The street of the account holder (optional).
        """
        ...

    @property
    def iban(self):
        """The IBAN of this account (read-only)."""
        ...

    @property
    def bic(self):
        """The BIC of this account (read-only)."""
        ...

    @property
    def name(self):
        """The name of the account holder (read-only)."""
        ...

    @property
    def country(self):
        """The country of the account holder (read-only)."""
        ...

    @property
    def city(self):
        """The city of the account holder (read-only)."""
        ...

    @property
    def postcode(self):
        """The postcode of the account holder (read-only)."""
        ...

    @property
    def street(self):
        """The street of the account holder (read-only)."""
        ...

    @property
    def address(self):
        """Tuple of unstructured address lines (read-only)."""
        ...

    def is_sepa(self):
        """
        Checks if this account seems to be valid
        within the Single Euro Payments Area.
        (added in v6.2.0)
        """
        ...

    def set_ultimate_name(self, name):
        """
        Sets the ultimate name used for SEPA transactions and by
        the :class:`MandateManager`.
        """
        ...

    @property
    def ultimate_name(self):
        """The ultimate name used for SEPA transactions."""
        ...

    def set_originator_id(self, cid=None, cuc=None):
        """
        Sets the originator id of the account holder (new in v6.1.1).

        :param cid: The SEPA creditor id. Required for direct debits
            and in some countries also for credit transfers.
        :param cuc: The CBI unique code (only required in Italy).
        """
        ...

    @property
    def cid(self):
        """The creditor id of the account holder (readonly)."""
        ...

    @property
    def cuc(self):
        """The CBI unique code (CUC) of the account holder (readonly)."""
        ...

    def set_mandate(self, mref, signed, recurrent=False):
        """
        Sets the SEPA mandate for this account.

        :param mref: The mandate reference.
        :param signed: The date of signature. Can be a date object
            or an ISO8601 formatted string.
        :param recurrent: Flag whether this is a recurrent mandate
            or not.
        :returns: A :class:`Mandate` object.
        """
        ...

    @property
    def mandate(self):
        """The assigned mandate (read-only)."""
        ...


class Amount:
    """
    The Amount class with an integrated currency converter.

    Arithmetic operations can be performed directly on this object.
    """

    default_currency = 'EUR'

    exchange_rates = {}

    implicit_conversion = False

    def __init__(self, value, currency=None):
        """
        Initializes the Amount instance.

        :param value: The amount value.
        :param currency: An ISO-4217 currency code. If not specified,
            it is set to the value of the class attribute
            :attr:`default_currency` which is initially set to EUR.
        """
        ...

    @property
    def value(self):
        """The amount value of type ``decimal.Decimal``."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code."""
        ...

    @property
    def decimals(self):
        """The number of decimal places (at least 2). Use the built-in ``round`` to adjust the decimal places."""
        ...

    @classmethod
    def update_exchange_rates(cls):
        """
        Updates the exchange rates based on the data provided by the
        European Central Bank and stores it in the class attribute
        :attr:`exchange_rates`. Usually it is not required to call
        this method directly, since it is called automatically by the
        method :func:`convert`.

        :returns: A boolean flag whether updated exchange rates
            were available or not.
        """
        ...

    def convert(self, currency):
        """
        Converts the amount to another currency on the bases of the
        current exchange rates provided by the European Central Bank.
        The exchange rates are automatically updated once a day and
        cached in memory for further usage.

        :param currency: The ISO-4217 code of the target currency.
        :returns: An :class:`Amount` object in the requested currency.
        """
        ...


class SEPATransaction:
    """
    The SEPATransaction class

    This class cannot be instantiated directly. An instance is returned
    by the method :func:`add_transaction` of a SEPA document instance
    or by the iterator of a :class:`CAMTDocument` instance.

    If it is a batch of other transactions, the instance can be treated
    as an iterable over all underlying transactions.
    """

    @property
    def bank_reference(self):
        """The bank reference, used to uniquely identify a transaction."""
        ...

    @property
    def iban(self):
        """The IBAN of the remote account (IBAN)."""
        ...

    @property
    def bic(self):
        """The BIC of the remote account (BIC)."""
        ...

    @property
    def name(self):
        """The name of the remote account holder."""
        ...

    @property
    def country(self):
        """The country of the remote account holder."""
        ...

    @property
    def address(self):
        """A tuple subclass which holds the address of the remote account holder. The tuple values represent the unstructured address. Structured fields can be accessed by the attributes *country*, *city*, *postcode* and *street*."""
        ...

    @property
    def ultimate_name(self):
        """The ultimate name of the remote account (ABWA/ABWE)."""
        ...

    @property
    def originator_id(self):
        """The creditor or debtor id of the remote account (CRED/DEBT)."""
        ...

    @property
    def amount(self):
        """The transaction amount of type :class:`Amount`. Debits are always signed negative."""
        ...

    @property
    def purpose(self):
        """A tuple of the transaction purpose (SVWZ)."""
        ...

    @property
    def date(self):
        """The booking date or appointed due date."""
        ...

    @property
    def valuta(self):
        """The value date."""
        ...

    @property
    def msgid(self):
        """The message id of the physical PAIN file."""
        ...

    @property
    def kref(self):
        """The id of the logical PAIN file (KREF)."""
        ...

    @property
    def eref(self):
        """The end-to-end reference (EREF)."""
        ...

    @property
    def mref(self):
        """The mandate reference (MREF)."""
        ...

    @property
    def purpose_code(self):
        """The external purpose code (PURP)."""
        ...

    @property
    def cheque(self):
        """The cheque number."""
        ...

    @property
    def info(self):
        """The transaction information (BOOKINGTEXT)."""
        ...

    @property
    def classification(self):
        """The transaction classification. For German banks it is a tuple in the form of (SWIFTCODE, GVC, PRIMANOTA, TEXTKEY), for French banks a tuple in the form of (DOMAINCODE, FAMILYCODE, SUBFAMILYCODE, TRANSACTIONCODE), otherwise a plain string."""
        ...

    @property
    def return_info(self):
        """A tuple of return code and reason."""
        ...

    @property
    def status(self):
        """The transaction status. A value of INFO, PDNG or BOOK."""
        ...

    @property
    def reversal(self):
        """The reversal indicator."""
        ...

    @property
    def batch(self):
        """Flag which indicates a batch transaction."""
        ...

    @property
    def camt_reference(self):
        """The reference to a CAMT file."""
        ...

    def get_account(self):
        """Returns an :class:`Account` instance of the remote account."""
        ...


class SEPACreditTransfer:
    """SEPACreditTransfer class"""

    def __init__(self, account, type='NORM', cutoff=14, batch=True, cat_purpose=None, scheme=None, currency=None):
        """
        Initializes the SEPA credit transfer instance.

        Supported pain schemes:

        - pain.001.003.03 (DE)
        - pain.001.001.03
        - pain.001.001.09 (*since v7.6*)
        - pain.001.001.03.ch.02 (CH)
        - pain.001.001.09.ch.03 (CH, *since v7.6*)
        - CBIPaymentRequest.00.04.00 (IT)
        - CBIPaymentRequest.00.04.01 (IT)
        - CBICrossBorderPaymentRequestLogMsg.00.01.01 (IT, *since v7.6*)

        :param account: The local debtor account.
        :param type: The credit transfer priority type (*NORM*, *HIGH*,
            *URGP*, *INST* or *SDVA*). (new in v6.2.0: *INST*,
            new in v7.0.0: *URGP*, new in v7.6.0: *SDVA*)
        :param cutoff: The cut-off time of the debtor's bank.
        :param batch: Flag whether SEPA batch mode is enabled or not.
        :param cat_purpose: The SEPA category purpose code. This code
            is used for special treatments by the local bank and is
            not forwarded to the remote bank. See module attribute
            CATEGORY_PURPOSE_CODES for possible values.
        :param scheme: The PAIN scheme of the document. If not
            specified, the scheme is set to *pain.001.001.03* for
            SEPA payments and *pain.001.001.09* for payments in
            currencies other than EUR.
            In Switzerland it is set to *pain.001.001.03.ch.02*,
            in Italy to *CBIPaymentRequest.00.04.00*.
        :param currency: The ISO-4217 code of the currency to use.
            It must match with the currency of the local account.
            If not specified, it defaults to the currency of the
            country the local IBAN belongs to.
        """
        ...

    @property
    def type(self):
        """The credit transfer priority type (read-only)."""
        ...

    def add_transaction(self, account, amount, purpose, eref=None, ext_purpose=None, due_date=None, charges='SHAR'):
        """
        Adds a transaction to the SEPACreditTransfer document.
        If :attr:`scl_check` is set to ``True``, it is verified that
        the transaction can be routed to the target bank.

        :param account: The remote creditor account.
        :param amount: The transaction amount as floating point number
            or an instance of :class:`Amount`.
        :param purpose: The transaction purpose text. If the value matches
            a valid ISO creditor reference number (starting with "RF..."),
            it is added as a structured reference. For other structured
            references a tuple can be passed in the form of
            (REFERENCE_NUMBER, PURPOSE_TEXT).
        :param eref: The end-to-end reference (optional).
        :param ext_purpose: The SEPA external purpose code (optional).
            This code is forwarded to the remote bank and the account
            holder. See module attribute EXTERNAL_PURPOSE_CODES for
            possible values.
        :param due_date: The due date. If it is an integer or ``None``,
            the next possible date is calculated starting from today
            plus the given number of days (considering holidays and
            the given cut-off time). If it is a date object or an
            ISO8601 formatted string, this date is used without
            further validation.
        :param charges: Specifies which party will bear the charges
            associated with the processing of an international
            transaction. Not applicable for SEPA transactions.
            Can be a value of SHAR (SHA), DEBT (OUR) or CRED (BEN).
            *(new in v7.6)*

        :returns: A :class:`SEPATransaction` instance.
        """
        ...

    def render(self):
        """Renders the SEPACreditTransfer document and returns it as XML."""
        ...

    @property
    def scheme(self):
        """The document scheme version (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id of this document (read-only)."""
        ...

    @property
    def account(self):
        """The local account (read-only)."""
        ...

    @property
    def cutoff(self):
        """The cut-off time of the local bank (read-only)."""
        ...

    @property
    def batch(self):
        """Flag if batch mode is enabled (read-only)."""
        ...

    @property
    def cat_purpose(self):
        """The category purpose (read-only)."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def new_batch(self, kref=None):
        """
        After calling this method additional transactions are added to a new
        batch (``PmtInf`` block). This could be useful if you want to divide
        transactions into different batches with unique KREF ids.

        :param kref: It is possible to set a custom KREF (``PmtInfId``) for
            the new batch (new in v7.2). Be aware that KREF ids should be
            unique over time and that all transactions must be grouped by
            particular SEPA specifications (date, sequence type, etc.) into
            separate batches. This is done automatically if you do not pass
            a custom KREF.
        """
        ...

    def send(self, ebics_client, use_ful=None):
        """
        Sends the SEPA document using the passed EBICS instance.

        :param ebics_client: The :class:`fintech.ebics.EbicsClient` instance.
        :param use_ful: Flag, whether to use the order type
            :func:`fintech.ebics.EbicsClient.FUL` for uploading the document
            or otherwise one of the suitable order types
            :func:`fintech.ebics.EbicsClient.CCT`,
            :func:`fintech.ebics.EbicsClient.CCU`,
            :func:`fintech.ebics.EbicsClient.CIP`,
            :func:`fintech.ebics.EbicsClient.AXZ`,
            :func:`fintech.ebics.EbicsClient.CDD`,
            :func:`fintech.ebics.EbicsClient.CDB`,
            :func:`fintech.ebics.EbicsClient.XE2`,
            :func:`fintech.ebics.EbicsClient.XE3` or
            :func:`fintech.ebics.EbicsClient.XE4`.
            If not specified, *use_ful* is set to ``True`` if the local
            account is originated in France, otherwise it is set to ``False``.
            With EBICS v3.0 the document is always uploaded via
            :func:`fintech.ebics.EbicsClient.BTU`.
        :returns: The EBICS order id.
        """
        ...


class SEPADirectDebit:
    """SEPADirectDebit class"""

    def __init__(self, account, type='CORE', cutoff=36, batch=True, cat_purpose=None, scheme=None, currency=None):
        """
        Initializes the SEPA direct debit instance.

        Supported pain schemes:

        - pain.008.003.02 (DE)
        - pain.008.001.02
        - pain.008.001.08 (*since v7.6*)
        - pain.008.001.02.ch.01 (CH)
        - CBISDDReqLogMsg.00.01.00 (IT)
        - CBISDDReqLogMsg.00.01.01 (IT)

        :param account: The local creditor account with an appointed
            creditor id.
        :param type: The direct debit type (*CORE* or *B2B*).
        :param cutoff: The cut-off time of the creditor's bank.
        :param batch: Flag if SEPA batch mode is enabled or not.
        :param cat_purpose: The SEPA category purpose code. This code
            is used for special treatments by the local bank and is
            not forwarded to the remote bank. See module attribute
            CATEGORY_PURPOSE_CODES for possible values.
        :param scheme: The PAIN scheme of the document. If not
            specified, the scheme is set to *pain.008.001.02*.
            In Switzerland it is set to *pain.008.001.02.ch.01*,
            in Italy to *CBISDDReqLogMsg.00.01.00*.
        :param currency: The ISO-4217 code of the currency to use.
            It must match with the currency of the local account.
            If not specified, it defaults to the currency of the
            country the local IBAN belongs to.
        """
        ...

    @property
    def type(self):
        """The direct debit type (read-only)."""
        ...

    def add_transaction(self, account, amount, purpose, eref=None, ext_purpose=None, due_date=None):
        """
        Adds a transaction to the SEPADirectDebit document.
        If :attr:`scl_check` is set to ``True``, it is verified that
        the transaction can be routed to the target bank.

        :param account: The remote debtor account with a valid mandate.
        :param amount: The transaction amount as floating point number
            or an instance of :class:`Amount`.
        :param purpose: The transaction purpose text. If the value matches
            a valid ISO creditor reference number (starting with "RF..."),
            it is added as a structured reference. For other structured
            references a tuple can be passed in the form of
            (REFERENCE_NUMBER, PURPOSE_TEXT).
        :param eref: The end-to-end reference (optional).
        :param ext_purpose: The SEPA external purpose code (optional).
            This code is forwarded to the remote bank and the account
            holder. See module attribute EXTERNAL_PURPOSE_CODES for
            possible values.
        :param due_date: The due date. If it is an integer or ``None``,
            the next possible date is calculated starting from today
            plus the given number of days (considering holidays, the
            lead time and the given cut-off time). If it is a date object
            or an ISO8601 formatted string, this date is used without
            further validation.

        :returns: A :class:`SEPATransaction` instance.
        """
        ...

    def render(self):
        """Renders the SEPADirectDebit document and returns it as XML."""
        ...

    @property
    def scheme(self):
        """The document scheme version (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id of this document (read-only)."""
        ...

    @property
    def account(self):
        """The local account (read-only)."""
        ...

    @property
    def cutoff(self):
        """The cut-off time of the local bank (read-only)."""
        ...

    @property
    def batch(self):
        """Flag if batch mode is enabled (read-only)."""
        ...

    @property
    def cat_purpose(self):
        """The category purpose (read-only)."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def new_batch(self, kref=None):
        """
        After calling this method additional transactions are added to a new
        batch (``PmtInf`` block). This could be useful if you want to divide
        transactions into different batches with unique KREF ids.

        :param kref: It is possible to set a custom KREF (``PmtInfId``) for
            the new batch (new in v7.2). Be aware that KREF ids should be
            unique over time and that all transactions must be grouped by
            particular SEPA specifications (date, sequence type, etc.) into
            separate batches. This is done automatically if you do not pass
            a custom KREF.
        """
        ...

    def send(self, ebics_client, use_ful=None):
        """
        Sends the SEPA document using the passed EBICS instance.

        :param ebics_client: The :class:`fintech.ebics.EbicsClient` instance.
        :param use_ful: Flag, whether to use the order type
            :func:`fintech.ebics.EbicsClient.FUL` for uploading the document
            or otherwise one of the suitable order types
            :func:`fintech.ebics.EbicsClient.CCT`,
            :func:`fintech.ebics.EbicsClient.CCU`,
            :func:`fintech.ebics.EbicsClient.CIP`,
            :func:`fintech.ebics.EbicsClient.AXZ`,
            :func:`fintech.ebics.EbicsClient.CDD`,
            :func:`fintech.ebics.EbicsClient.CDB`,
            :func:`fintech.ebics.EbicsClient.XE2`,
            :func:`fintech.ebics.EbicsClient.XE3` or
            :func:`fintech.ebics.EbicsClient.XE4`.
            If not specified, *use_ful* is set to ``True`` if the local
            account is originated in France, otherwise it is set to ``False``.
            With EBICS v3.0 the document is always uploaded via
            :func:`fintech.ebics.EbicsClient.BTU`.
        :returns: The EBICS order id.
        """
        ...


class CAMTDocument:
    """
    The CAMTDocument class is used to parse CAMT52, CAMT53 or CAMT54
    documents. An instance can be treated as an iterable over its
    transactions, each represented as an instance of type
    :class:`SEPATransaction`.

    Note: If orders were submitted in batch mode, there are three
    methods to resolve the underlying transactions. Either (A) directly
    within the CAMT52/CAMT53 document, (B) within a separate CAMT54
    document or (C) by a reference to the originally transfered PAIN
    message. The applied method depends on the bank (method B is most
    commonly used).
    """

    def __init__(self, xml, camt54=None):
        """
        Initializes the CAMTDocument instance.

        :param xml: The XML string of a CAMT document to be parsed
            (either CAMT52, CAMT53 or CAMT54).
        :param camt54: In case `xml` is a CAMT52 or CAMT53 document, an
            additional CAMT54 document or a sequence of such documents
            can be passed which are automatically merged with the
            corresponding batch transactions.
        """
        ...

    @property
    def type(self):
        """The CAMT type, eg. *camt.053.001.02* (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id (read-only)."""
        ...

    @property
    def created(self):
        """The date of creation (read-only)."""
        ...

    @property
    def reference_id(self):
        """A unique reference number (read-only)."""
        ...

    @property
    def sequence_id(self):
        """The statement sequence number (read-only)."""
        ...

    @property
    def info(self):
        """Some info text about the document (read-only)."""
        ...

    @property
    def iban(self):
        """The local IBAN (read-only)."""
        ...

    @property
    def bic(self):
        """The local BIC (read-only)."""
        ...

    @property
    def name(self):
        """The name of the account holder (read-only)."""
        ...

    @property
    def currency(self):
        """The currency of the account (read-only)."""
        ...

    @property
    def date_from(self):
        """The start date (read-only)."""
        ...

    @property
    def date_to(self):
        """The end date (read-only)."""
        ...

    @property
    def balance_open(self):
        """The opening balance of type :class:`Amount` (read-only)."""
        ...

    @property
    def balance_close(self):
        """The closing balance of type :class:`Amount` (read-only)."""
        ...


class Mandate:
    """SEPA mandate class."""

    def __init__(self, path):
        """
        Initializes the SEPA mandate instance.

        :param path: The path to a SEPA PDF file.
        """
        ...

    @property
    def mref(self):
        """The mandate reference (read-only)."""
        ...

    @property
    def signed(self):
        """The date of signature (read-only)."""
        ...

    @property
    def b2b(self):
        """Flag if it is a B2B mandate (read-only)."""
        ...

    @property
    def cid(self):
        """The creditor id (read-only)."""
        ...

    @property
    def created(self):
        """The creation date (read-only)."""
        ...

    @property
    def modified(self):
        """The last modification date (read-only)."""
        ...

    @property
    def executed(self):
        """The last execution date (read-only)."""
        ...

    @property
    def closed(self):
        """Flag if the mandate is closed (read-only)."""
        ...

    @property
    def debtor(self):
        """The debtor account (read-only)."""
        ...

    @property
    def creditor(self):
        """The creditor account (read-only)."""
        ...

    @property
    def pdf_path(self):
        """The path to the PDF file (read-only)."""
        ...

    @property
    def recurrent(self):
        """Flag whether this mandate is recurrent or not."""
        ...

    def is_valid(self):
        """Checks if this SEPA mandate is still valid."""
        ...


class MandateManager:
    """
    A MandateManager manages all SEPA mandates that are required
    for SEPA direct debit transactions.

    It stores all mandates as PDF files in a given directory.

    .. warning::

        The MandateManager is still BETA. Don't use for production!
    """

    def __init__(self, path, account):
        """
        Initializes the mandate manager instance.

        :param path: The path to a directory where all mandates
            are stored. If it does not exist it will be created.
        :param account: The creditor account with the full address
            and an appointed creditor id.
        """
        ...

    @property
    def path(self):
        """The path where all mandates are stored (read-only)."""
        ...

    @property
    def account(self):
        """The creditor account (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def get_mandate(self, mref):
        """
        Get a stored SEPA mandate.

        :param mref: The mandate reference.
        :returns: A :class:`Mandate` object.
        """
        ...

    def get_account(self, mref):
        """
        Get the debtor account of a SEPA mandate.

        :param mref: The mandate reference.
        :returns: A :class:`Account` object.
        """
        ...

    def get_pdf(self, mref, save_as=None):
        """
        Get the PDF document of a SEPA mandate.

        All SEPA meta data is removed from the PDF.

        :param mref: The mandate reference.
        :param save_as: If given, it must be the destination path
            where the PDF file is saved.
        :returns: The raw PDF data.
        """
        ...

    def add_mandate(self, account, mref=None, signature=None, recurrent=True, b2b=False, lang=None):
        """
        Adds a new SEPA mandate and creates the corresponding PDF file.
        If :attr:`scl_check` is set to ``True``, it is verified that
        a direct debit transaction can be routed to the target bank.

        :param account: The debtor account with the full address.
        :param mref: The mandate reference. If not specified, a new
            reference number will be created.
        :param signature: The signature which must be the full name
            of the account holder. If given, the mandate is marked
            as signed. Otherwise the method :func:`sign_mandate`
            must be called before the mandate can be used for a
            direct debit.
        :param recurrent: Flag if it is a recurrent mandate or not.
        :param b2b: Flag if it is a B2B mandate or not.
        :param lang: ISO 639-1 language code of the mandate to create.
            Defaults to the language of the account holder's country.
        :returns: The created or passed mandate reference.
        """
        ...

    def sign_mandate(self, document, mref=None, signed=None):
        """
        Updates a SEPA mandate with a signed document.

        :param document: The path to the signed document, which can
            be an image or PDF file.
        :param mref: The mandate reference. If not specified and
            *document* points to an image, the image is scanned for
            a Code39 barcode which represents the mandate reference.
        :param signed: The date of signature. If not specified, the
            current date is used.
        :returns: The mandate reference.
        """
        ...

    def update_mandate(self, mref, executed=None, closed=None):
        """
        Updates the SEPA meta data of a mandate.

        :param mref: The mandate reference.
        :param executed: The last execution date. Can be a date
            object or an ISO8601 formatted string.
        :param closed: Flag if this mandate is closed.
        """
        ...

    def archive_mandates(self, zipfile):
        """
        Archives all closed SEPA mandates.

        Currently not implemented!

        :param zipfile: The path to a zip file.
        """
        ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJy0fQlcVNe5+F1mYxgWERH3EUUZGAbEfYmKiLKDgBsaZwbuAKPD4iyiBvdlQMQV9924xmhU3Nf0nDYvyWvTpNtr57WvSZfUNm26t4lp4/87594ZZmAgmvf++uPOOfee'
        b'e76zfOfbzne++0um0z8e/qbDn2MKXASmjKliyliBFbjNTBln4U/KBP4Ua48SZBb5JmYF4+i7iLMoBPkmdiNrUVq4TSzLCIoSJqRap3y6VF2SWZSurakTXDaLtq5S66y2'
        b'aItWOavrarWzrLVOS0W1tt5cscxcZTGo1aXVVoe3rGCptNZaHNpKV22F01pX69CaawVthc3scMBdZ522oc6+TNtgdVZrCQiDumKkXx8S4S8B/kJJPzbCxc24WTfn5t0y'
        b't9ytcCvdKneIW+0OdWvcYe5wd4Q70t3LHeXu7Y5293HHuPu6Y9393P3dA9wD3YPcg91D3Fr3UHece5h7uDvePcI9sjKBjohqTUKTbBOzRrc6pDFhEzOfadRtYlhmbcJa'
        b'XYlfuoEJ2azjCyr8h5mFvzT4602aKKNDXcLoIgpsKkifHMQxsrxjCoYxaRTLVzGu4XBzrgZfwy24uTBvDm6qqMathTrcmj23KFnBjMyU4ceoBV/U8a4BUBS9ipozc7P1'
        b'2XWhybgZb8+XM+F4G18wBzW7+sBzfK9mIXksZ4ahGzIZi06ge2NcA8mbm+rnJ9mS6Ev52bhVly1jovBeHt2bslTHufqTl++iq7Nyc5Rpo+F5Lt5RCNVEDOUnD1zoGkRq'
        b'OIMfobZc/Bo+BCWy88UC4fgKP0o3GKoYTMrswifQfgd5CHDwdpZRo9fwlmwOXUUPFrrioEgx3rs8FF+PwDf7zXOgZny7Ht9Yjloiwhhm4DCZEj1ap2Nd/Uhdtybjbbgl'
        b'Lwdv5xl8fi2PH7HoyDj8GjzXkecPX8ZXctHlhOxkvC0Xb0fNhaRJqDWlIFmnYGZn4g34vrJxfrZUX34i2orboVl50IVrhXJG3sjiM+jMYul5EXo9PyknWZ+fbGAZDb6E'
        b't/fh1WgzaoLnpP944wT0WlKWPhE355GeheLL+AbexeErUWh3BdtppY32osBBgqWBOMr8b7HUneDWuRPdSW69O9ltcKe4U92j3GmVoyXcZZtCAHc5wF2W4i5H8ZVdy5X4'
        b'pRvISu6Eu6ThA7rg7hIRd02hSkbDMLG9400afWYeQ28ejQWEhjW5TGHStEyuFW9qK0OYSIbJKrOZbJq6CPHmWU7OwG/CoRkmzfxBC5iLjE0Ntx9qYmV/i2Km/2m0bvRf'
        b'uFujIk3fYm0h8KDulYPsVSUz3TDTlPZT+7bxv2Xo7Vuhf41oi2AnLDd+yH4ZGz2hgvEwLj1pasgiWEQtKXMSEvC2lCzACXSxNCEnH+/UG7KT4fdhEsvURoS8pETnXTPJ'
        b'fD6OQXsdTvuK5S4Hvo2vwmRex7dgKd7E7RGoFd9TadThIWGhaCdqQtvTUsekjRs1djS6ja7KGPRoUQi+HMe6ZkNFc1QVuXk5Bdn5uXgnbsLbAWt3wDprhcYk6BMNuuQk'
        b'9Aa6gF4vhnev4wN4N96Hd+H9eC9um88kapm+qWFRiTgQhcjgK+GvL5mJCV5Cx1fy0hRzTTCRa3iYYo5OMU+nlVvLl/iluyNPsi5TLCuwk7m3DpsbJ3dMhNRfPDm55sVv'
        b'vv+Nq7uu7R8qf/s184I370S+vejNG7tO7T+1yco6lBVheMY5fcyurFS+ahKTUxN24vaA/WE6uZPQEnTAuQqmYxuMCKxe2UQWH8T70TU7vuKMJWN/eVpEkgEGq1mPmvqy'
        b'jALt4JJN+IwzGh4unjY4KTkhK7kWv8rBk8NcsnIxfWtCJT6alIxb80ahI4vkjKKMhSX4CF1xxlDqVbgGt2ShywzD9UYH1rCz0A10X8d6uASdjreTrvpdOLg87TOl0l63'
        b'2lKrrRRZlsFhqTdP9fAuq0CeO4BMM+qMKDaKtSu8L+lknpBac43FAezN4pGZ7VUOj9JotLtqjUZPqNFYYbOYa131RqOO6wAHabIE7GRG7XJyIfURJHSQDkc+UnAcq2DJ'
        b'VcYqviRXF3mQ169fEnSXRVcWMRw6yGaMwZdnVXBB8IRO5ySCJxzFFFmlzIcp/HNhSmUwYqDugim9C1zkxnDcyjjyoCv44nB8hkHnKybQ+2nYHZ4L91kdehjCYHcG2kcZ'
        b'UyG6jNfjdqC6rBy3ZzPo5kT8mD5BjzEsMNxCHmUi90IG7xtWQHuPLjjxkVBgcWwvI77LwGSiR/QBPpeGTiWRB3PwhrEMPoK2ysS6muvxliSDgmEXJaPtwDRQC7pAXxmK'
        b'bsKS3jsHkqsn4stM/kx8jTYYXcDHLXgvzIeeKUAP9BrcpAsRK3sdt6Otk2G08RaGhfZvKcAHRC67G72OrrxCnpxl0Ibx+CxqHUVre3ndMnQf6sIHGHwJPcQHxjAugpyo'
        b'tQDoAX1yG15fSunNWbGXe9XAHO/DaONjTDk+io/xcyiUdHS/GNP7D5nJ+AJ+iHahyxRKZUoFuh8BD04y6Do6gU+ujRf7cn5mH7JmQDyCtXc/FG+PcUExRm9C7hKoaCSj'
        b'GD+yarYIdttKdAvvBdxJZdAVdCAVPU4Wu33fha4CbToAj9DOFJhc49ho2gl8sozB7Q7cviJhOMtw+AI7fAi6TQlHAO3i/EkMIQZVTCPzMrClRrYJBEs718ju5pZzRJSk'
        b'S4peLnIezpDqYSsush0rlK4Vj3qKzepwVtTV1E9dQKokT2IZFxFj0Z2UlFxJWKGMPwu3oXYgvs2FBXi7Dt3i09JQSy7aA+0Oxa8z6AG+FxqrQVdno3PWcctH8o5mqGVg'
        b'0s6xrZPDUWrkzIb/UPwicur4k+c+jLmbXvZkVlHG8MTzXPN3BiX813/+/sjGTU8qjx+v1Dwc75wR/+TJxF8eDZ2nef3n5siMPfpheXVf7Ln77UkbWz8y9J4zzrh12icN'
        b'c6Ku37C/tjPWOX356VnRv1mdemDg/HFjr+xd987Cux/9Y2G/slXVC5+tWRFlGLLEnjAelqDc2Y+SMuAPR9HrsiSDDm8D5qZAr3OjC1GLSFrb5/UDOQU3ZecVyPtomFB0'
        b'jcPHgBLuoHSQnYm39sUXcYsepDgQIRVLuGFVnHMYPKqFoTlGmSTeBsIZbkav58iZ3mN4fBpEoz0g/512DhCXEbrkpd7o8AxKwNE1Ik91oaQ6WWfS2mn2Qi21FXWCxUho'
        b'K6WqRAiUZclYFfwHqvelipexakhrWNWzSD4cfmMhZ4/0o7isw6OurTM6QEuotjjsRA6wE9LUtTWcPYqke/kILakm20too+4GIbRa0mM33otaJUyakSPhkozpj/fIGjgQ'
        b'73qmuZQ3B9Dc5+POVc/HnUNEAWw+9G04k2pQMqaBgwfFimLV8bBsZhfTJFeYTGpF8mBmFr0bqY1ktMyf8sPqTbZhSSZJLAtXM9HMhWplpMmWZRorUibgwZfw7tGpMmYp'
        b'3g3EiClHB/Cr1rywRaxjITxPzmv4xPQ7U3VlnvnblQkf/3b91UPXF277rPjgpn6TYmNS9cIT4YlJv0dxvd/k2L5pMbkZQvGC4tiyQ8PT9Se+2Bo9LzL3KBEY7ioEbtG4'
        b'EioqRMX3GdVnsY5zEuEGaOcpdIDwe3x/ZbLE76viKR7iI6sbkgzZ+kSdAaQ4DEsVn8mL1cqWDC7Wsc+Hfb0qqi0Vy4wVdotgddbZjRJnDyckpIzgYDigQCzgnL23H77x'
        b'FVbBo6yoc9U67at6RjeCVvY+PnQjtSzyodv5IOhG1Fe5EbsB07JATUI7Cqt5A4inzdDBFARLLo9lXkJHFPjccmUXrcKHdlQkZAHxOkRCliLd15D6ScNVXZBupoh0yZbe'
        b'UYe4LEiZGuPtKRJ+fTemV+KP2OkMU2/S/HHOTKbURZZdP3RrANF7RgHnLRmFDuNLtPARVjZ8LgcLcbpJE18/j6FlG9HxpNEyoioDtT6bhg6toGXf0HIyWP4EnCZUXcG4'
        b'yPpNmF8ymiMqVUrBaHQI7xZXQ07YmOtcKuhtJs1v5uWJtWbg4+j8aGCzY5hS9GDMELTRRUgB3jJl8WgYy7HMYnRuLHp9Oq1hzohoJoMtIu0auGpSOkOLqvGOwaNhRMYx'
        b'+NGMcQ34Ki16e+ggvcDUE2BTQqIbGMpuQcXGu0bDtIxn8NG88fgaekQLP0scuvplbj0ZnMWPitQM5cH4yLIxo2H6JjA5+gnz+tKCS8LiI3fC6oUGcDm5g8Vax6MjwNTb'
        b'ITWRicOHJqIdvWnhAdN12sXsSRgY04zWl5eIhVm0FV1G7TCOk5jR6MqkMrSTFr41PlmdwFwl7Y07vraSEcWmm8BWmsgMz2CgsUdmxOMTotywC79hI2w1g0H70ZGMLHSC'
        b'jnsl3raECMEzQTOfuQi9KtZyA8SiDQ4YzUwQxPDNTHwijY796JWoxQEjNws4FN41C786RSy/BV9TOWCUZjPoCD4wGxSBNlq71TDbAQOSxShHZKHz2C02pSV3CW6nNBvf'
        b'nZWNNuJWWjlqm1yEST9zQD7Eh3PW2aiwshwdQ1dwOzQ9l0GX0M1ckJPu0vF2rh2E26HteQzXP8+YSEdloUIxTgWiA6M1aQY1lIgTzuJ2gAjdyWcG5Ofj10Tc+KUydEkI'
        b'C2s10qTvVbZExMO0Xq/gduhhAYzMvoLY+bTkL3qPXPsD7iCptHzo7EKx0rrcBNwOfS5kEtDGQrR/Ji2aOSZx5U72Aqk07n3DMnEK8cWV6D5uh5EoYirwlSJ0dQItnJrW'
        b'T7jGmMh8Lz49sVBsQRjevIzYvuaARNlvztpptGR6P1X1OU5LSmqGzhwjTjaI1c2oORRGrBjmo28x3oqO0dI/DYlYUsAD/Ug15S1aVSqhxj7UOiQUhrGEASV1awl2S+Jx'
        b'MnKj9aEwjqUgGKLmUrS/SCQAhQMUa5lq0pWBSxultYPvoebyUBjKuSCU7Jk7NI8Wzc0dnNaPWUkADkx7aYLYEVg6D1eEwljOY0aGz7OV0ZLfHD5sMOKayOKPO9qQKVZa'
        b'gI5OC4WhnM/0w5vn4/sqWnRVYcykJGYBGfWBafwAsdJhtfh8KAzkAmaxcQE+JKclcX5K1jb+DgEfdzcuRaQT0fjSONRCUIKBgWle2Ceflt1gGZv4PfZ9siDTLLEDRLap'
        b'j0kb6OTfJq2yT3NZxJtN/UelZnJvkjUe94eM5cAJxFFfr0BNqAVGvQwGEp8qywJ0JOOYg2+9jFo4whzwCXRtUTneYfvs2bNnK5bL9DZepI0XKiaIlRePHT/pv9kfk84V'
        b'h400MVZXVDTrGAoDe2OH5aX338nh06O3fPTKpbL8o62ec8fGvtc+q7W9VyPfN+7Jp/ro+W+tT/jhJe2NyUMX9W3e1fAntjG18L9m9J/6JHGtuqA86rLubx/MS0udvydB'
        b'9o+fzfzernNTfhN5piqs5l33VJXn/SXzndqM9idnXr5648K7A1660XfNjSH8GHf6pM3m/uWbP14z4PMVP7hd8WjQP/+wuW7k9/f/Me/z1Z7/Gv3oeOaG98zHDabdBvOh'
        b'K6Z9V8zHak17a9N/O25Fda/7zogvbmzmVzcNW719771b0ecn4M8PWK36t7/5dN7r/R9Pn/jyyXMH7Acej73WfHl0wubiz1cczsKT/rt08ebiPQtOTD02afm4p89y636h'
        b'7dV35m+P/zrrzqffvXnmi2JD/6yxK/89N/vxgHVfxv3ki2lHNOVrf3gcJGhiq+PwPhdIwGj7wgJirdupZwEjL3H4ClCsS06q5rxahe8RsSNnqlfqWJNKpQ6+EZ0CSRAU'
        b'7/zkksgcYkyNwnd47C4ZQOXvSHQXbwLpeHtuNhGeiMFBMYHrV4XcziGk4o34UowDXc4qSE5INBJ7K97JM73wLh7UvLMzdPKgEossmHjhJ8eES3KMq8JIpGkqxNyAi0aQ'
        b'sZGcjIrSMpZ79lx/HPdl8D9ZYJ7n/v1cfzLuXx1/MvhT/Uum4KgYH82F8yo2EoQggCvTfEl+7THevul4ELVcFT1JWKy9r3cQ6HsC4zWaHA8iXI2gaxDvwI86xCtDPlxE'
        b'Y7UOr0cneTnau8j+FaIVMdcyfqIV+1yiVRcbSnB5XimKVv90aIAZrR+tLDLlKaa6JNGqLiMUpHTtK+pIk2b+KF5kEpkNIE21pRIxncrojei09c65IbwjAx7GnSr6xFT2'
        b'5tVdp/Ze3HRq08VDo7aMOnKqaeQWXezYH7yday4wV1v2yK7FFh9M1y/fWrY1/K3+ipOT9ttO9n9vDPOdP4btOfMjHUuFcbYCH6amN1gR+PVlZFGg1/Ehr7DdA372F/HT'
        b'4bS7KpwukLaNdkulxQ66n4irGjIa61Scxitux/rhgMwBhXtGgn4+JCAvkp0fB8EGZkPksyBokAJP6quG+XAgxaBLzDfoknPyUXNKTn5ucg5oegVyBu1G28wz1HjD5LKv'
        b'xIdAUfv58KGLqO2tPBAfFAWiKvYY31wYauej0QHIvM6gQ+geOkGRQmcdS5itNjXk00GDl+Qys6x80y8Zx3h41GtzzCemxR/k0/m/tmk5W6H+5Yy34r4MPxf+VuVb0eds'
        b'++O+Ef2xaWu4InLawQ2jw5jQz0KVy9eC+kVh7sd3VyVVoc3SrJMpn5PtJDtGGfhib9C+0CN8108DI+qXo680c93jQ2wnvSsQG9QiNoTEsIRy2fv740LFV+LCAB8ukBeb'
        b'/XDhsyC4QPbi0JGKPD+C0KFt+SPDKnQRXRVCgKZfRae+UuHnOxlZn0/hD0oguiKEsqCUTvunKyOYd1lRVhvaXyZKB4/kshE7RJFBfyWjRLw5XsWP+Bkv6k0zKwYy1l4Z'
        b'7/KOPMgfSHrvl399B5T035veLq+ufN3yxHTBnFCh3/OpacGbd3YN3aI7wr5dmWPeb3oicN/Ta6eOLJqbGtmQej51/Ohto51p0Wn2Wwwz5UnEzTk3AGkI71xL7LqX8vL1'
        b'HCPLZRcuQdd7oS1Osv83vWEFcMZLeJ8e70gpzMetBdnodRnTt1g2jkPHn1dpD6u1rHQaBZfFKJidIsZEU4zhItRstGQ4knGaZ9xT+0Af7sg8MlLcE2KzmAV4c9VXGIqI'
        b'nGAf7MMlUtHODlyK+ksQXCK7tdEDyK4k2XdEzYW6fNRaiA6ji3TPNR5fl5fhE/hyBe83xXJ/7JkqYo+M7gjK3YpKhYRBPDXTywCDeIpBMoo1/FpZiV86mMmIVK/ogkFy'
        b'kcWMeGl0zAWWyq5pu1PtIq60LZMPT5UQqHUQz1hv/ddTmcMMT+bzBwdtHxq1PvUP39HIUrKTVqbXPNucOW9DRWLvuTM/y/xcd+i1Y0f+e+H55gjFt85oJ37q+ckH1X/6'
        b'xlsjDO/K30gomHP3Ly/vmzJ+cCn64zsltn4DF4d999GjXvLcwyts343QX4v9PH89iGd0++fGKHyKGiKVDIdeQ+3oNDs3Cb9KsQufRS3TxU3sELyebmJb+1KKhLag9cty'
        b'ydptwa2FuEXBMiq8nUObe+M2yr/QtnQQ8VpwUwrQsgXLZfkseoy2lFOYaC96lIlb8tHrIB7W4u1oMzsbdNkHPQlkim4fdUZZTZWlE8b2F2lcPxVgajhgrBq4HsepuCgO'
        b'JCSFfYgPb+UEbwFZCSp6FBUuZ12lPwEMulgAn4eStDYQh0mlhzpwOOZJEBwm7+F7RrwrtzAZNcM07BSxmA74EHRaho+s6ts9NyRWd99mNlMpf0GO2GU/Mgz++nRB3yEi'
        b'+v6m8V2mjZ0wIyTSFPITWFT05hPVUGY602RV1ZsW/2OxVrz5/VSy5XwnlDeZ9GuWRYo3v1tLDJ4fvqQBUQoZJewvGNWbGc6oRikY05S4rBHizdNZA5kJzGcGVZFpyoch'
        b'Y8SbllmE6aamhUw3RdW7GsSbE4eQXfD3X2K1Js2WPhL03AEJoL2/Pws08LhvZw8Wb2ZGTWMamTfD1ammqPvTpf3y3w16CVRh0yxFkck+YZJE0dvUkxknMyEnNNJUnCyb'
        b'KN68W9uPSWVWxqlMpoGywUPEm9dMetBuI2URRaY4w6i+4s3ds3sxWubtuRH1Js33bNJ2+57w6cx6pr6AqzelNSxeJN5Uy8ke/IQ13HRT3quLqsWbl2eHgRj6oUEOYuhL'
        b'aRXizR2yAcwY5mAJNGkgfqVevPn2mnGMjZmwhNOa7CV108SbY+1zmJNMfV8AlPiROVu8+cfFFuZt5sPEsOmmygl5SVI3zVXMt5nPpvNa0yxOuU68eULfl9EzBxsitKYp'
        b'GSPWijd//Eo4M5B528kB39OtLBZvtqa+wvyN0TYoI00xr2S6xJu6iNGAMbusGsZUPG2yU7z5h3FxzExGO4NnTOUTX3Iy1j9F/w9H9edVpaFzd+cX41TNll//+PPlv9hz'
        b'bvPwsQO3LPqbuv8C59bMSThniaWi9oOB2/n6UOGXle++9eXx48MfZzd+/MO4R23zlzQi24M//U418k/qLXLlwVPDn7C/Vl3Q/+nQ7JdT98WMqOcuPXtp8S8vX1DWR419'
        b'Z3DW1ZL2eWeuXnvzfHNV73vZv3jvL/9SGf5DWTys6L3Fpv+8+IOfX2r789YVqvu5tot7Mk7a7/1229xv/fvwmE+/u/TRZ7uWyMd+I+7lf8/55rbhg0p/FX4/s/gP8fNa'
        b'PpS5flX70dEPpsmmfW/Y/gF/t36s+1tm/3H9b/8kxHL4yZ8Ojvj9xx8fjG9Aa07/7GfLvjvg2hdr6/N/t/Kj32/9dp95X75XNfHZrrvxj94wPrp4V512KfLNtsuRn/5p'
        b'vvHzqRvWfiGv27n07+r3dDyltJoy1DamGDToLmx8Zh1VgvEDfAw9zNUnZI3Gh0B+AkoM+vUqdGqASMMfv1SQBO8m4pM2lpG5WNzM8rqwryCnX33pgVj7G/0JMS431y4z'
        b'VtfZrIS4Uoq8QKTIE1Wgkar44VSSiGS1dMMpkkoVUayGU8vUIF2ovf/5Tr80JfuNZqAG3tM8UwNFV4H+bY/z0XOQYVdZzHY/Et4Dh2Htw3zUm1RxpYN6R38/CPVOhifo'
        b'Ot6LrlDyXZiDtw9bglvQDup6shM358FM6RXMS/iaAt9Bh/t2UT9k0q9jKSFxxAWQKeNC2BBWCKUbChxoOZzAbw4p4y0yQSbINzOb2DI5pBVSWgFppZRWQlolpVUWGeEM'
        b'lZwQIqg3q+BOiBvAlalLiNii8SjTBcFucTgKKhR+7VExfrsPMwh3EV2kfC5TlSqJxyiaVMBjlMBjFJTHKClfUaxVlvilg4lIPBNMC5cXUFPgJHQBH8EPe5VAeigz1ICu'
        b'iq4wc/dd5B12SH2roHTQtlFkd1j2xx9dG9R3TNYPnI1NyvcXnGkd+K4js/27V9e9u6Vy3uTD+fdSb5anNZ5/LXVw39M/uxRu+ekbfb659tLKiqX/1T560MGbR/9S53jl'
        b'Tsi3f/OFPnpryiwh9dCTD8tXxqND/Y4l7W2PPV58a8ixiYNvOMt0anEb9jDaqclFx/ERWGYdawy70Sbx+U50ei5IO7uBiXc42qBrRfgBlXgEvB4fQEdDA3aRY/Fr1EKG'
        b'jqArgES4rR/xoBNrx/c51IwOoLuianihN76Dr9YkGZJF1fAMlxo3nZKHEXLcilrQTrwzNxlasVPJhMZwhagJu+PstPaJuBVvQC2FQAJwa5JuJWDoazImIoR3ovu9RAJy'
        b'Fp9HbnSvlpbSo4syRqHi+qGW4bSCteVzUMtidC0FZDlDtmi9icJnebwhCz+mFZimwypoAc0+Jz+ZOOO1cPhoCL6N3fquwr7quYlMBxFRGo21lgajkZKOwZR0yNaIO9Ux'
        b'dNdQDeRCIf2XsasjJOw2SO+JxEDl4StsDrpBCKqt1bnKo6qvI84MgsWjcDjtFovTo3HVdthNetJZFHbiC2snRi5xy5HsJdqJL6Q90UdF4uHyrw4q0n9LVyrSpa0B4h4r'
        b'/ZEF4SArs5FZylC/X7bgIutRGaV9UUjLHBZbZYcPhzhwqik2c025YJ4aBrX8ldxXMKsjvRC9D58L5GYAqWM9ciMZOXuyD44PmJ1YesLhVXsq08kLpaduQJ0hRu88dFtv'
        b'xAvVWynWqzSKs9ptrZFBaw2QsccxosUJKOn/gb2JYzpTPr7Auuy1wzIHMar1Uk/+xPTE9O3y6kpN5YfArKMnHwrnPsz+pY6lRKQR2Mr1gDWKb2j7WdaI6M0FXTphVoef'
        b'JdDnSsesY9apY1b38aJCQCnRCYi3G0gtHWvAH0CybxzHwCUKhs8RS3Gc2RD+aRAsDw4I6D75pwsFTDYSTz6j0aM2GkX3dEhrjMblLrNNfEJXEyxZe129xQ4oSFcdXYQd'
        b'S28M7TLx/DM7HBUWm8279juv34sE68RiUIR2hBgU/slI9g0Vw8k5NuqZpheVLUBbjGVd1EdiSxxqduRl63KSE/saFIx6KYfdgq7LTIdKv45dbAdrF9gyvo1vi2iLhL+w'
        b'tggrV8lBSvovcK2KED6EF/SE9ft5JUcC2yXMPwTYuMwiB+av3MwAqw9p5UAAkAtqmg+leSXkNTQfRvMqyIfTfATNh0A+kuZ70bwa8lE035vmQyEfTfN9aF4D+Ria70vz'
        b'YdAyNSyGWKHfZlVZOOmNQMSM/q0sbbMGRJYBwkAqckTAu4PIu5YIYTC8zZdF0t5HCENaOSFZsrrwglYYSvvWC8rHUVjDKKwoyA+n+Xia7y2+3aZsU1XybTJhRCsvGKhw'
        b'Ip41IKMV7o6oDBESBB2tMRpqSKQ1JNEa+gg8JQ8pIABVUNr5dKRa6/dPuiseggh4olN4ZFYQZD0ygo7BsK+gQumHAGTdhHuXewGhIqIkFUIGUJpYrxt6eGW4RF2UVK5S'
        b'AXVRUuqiohRFuVZV4pcWjZcffQ6YHdBE8i+71uq0mm3W1eQER7VFa5Y6ZAW+Zq6tIEdAOr8yqd5sN9doSecmaTOt8Jadvpo9I71AW2fXmrVpyU5Xvc0CldAHlXX2Gm1d'
        b'ZZeKyD+L+H4CeVmvnZGdoSNVJKRnZBTOLSg1FszNn5FZDA/SC3KNGYUzM3WGoNWUAhib2emEqhqsNpu23KKtqKtdAQvfIpCTKaQZFXV2ICn1dbWCtbYqaC20B2aXs67G'
        b'7LRWmG22VQZteq142+rQUrs41Af90a6AMROAs3VtjjQ8ZNYn0XaRlPecjXd4QbkB7tXtyxKbFt+XMjBGJYXJo0eNG6dNzyvKStem6TrVGrRPIiRtQl09ObJjtgUZQC9Q'
        b'6I4EEVLBW/w89XiZs1iXN/f16xOZslibmP4adXWx3He1u2oKqJF4EWpdSIyUegM5CIMvoH2583FTLj2wQ2xs6EHjSmqqmJm+gxnIMrGpDefjv5iTxLjI9gLajm6D7E5s'
        b'lUW4iQjnKbgZUoUlYh1zs9BlfG9SVkF+fnY+y6Bt+HQIvoWv4Fui3eolelAjMnXW1eg9+TLxeMQYBb5LNq2TconjZ96cLEk0B7kc79Ghu8XoIlOSrsQHeNxGa/nzdJ4q'
        b'Takr+ioGxK0SLStpA+ghDm3qrPryMwtfFqseqsMP/KvGTeTMDrQ1pTjLPBVvy1Mws/FZBb6G3ZzoYnwWVIdLjuVjjcSBfCfpwIERVvuTEt7xHjxOsayJ3zm5FqdGzjzw'
        b'q99l/OT6IG3r5BPDMgt2vXeZPa8tXrA+dNLZn27WzbodWXd46PcfyH+uVy6Y8JkQE/Es9lH8QWGt5t4vNh4b8+h7d39nm/LBotXHFk/5YPy3lKvUZQmz/mYc95PPwsP+'
        b'MGfe3vhHpxYm//xnc76sudXyP31Wf/SraS+/vD/zbub40Wsar95Oedj+zb/q49e9u+ZXlb0bx/2593cuJy+eXD3uLH9k2bTQdwa8ze7/6ebyW/sqfn3FHmH+9M3J75yy'
        b'H8lLTHbf+3PUr/Rf/jNi59RLfWd/6bHookS3gM3L8NbQXHQVbcHbdfmu5ES8LYVj+iC3TIW3jaVKzxq8sRS36P1cFrajh6LbwvaXnVoy1EvG5Bpy8vXZqBVtAJVvp3g6'
        b'qj+6IatFj/AWqrih9dnodlLHhh5ueznZMp16ABfnoOO5eAd6FW8TN8O8NfTBm3nQ9u6i+3QfJwq9jq4mGezo9exOe38wiyecREjDNxsiYdahhiRMTl5JO6250DGC8jtd'
        b'8TwzG11Tgn54HO0SFdYt5MyLaLigaBFagffN4fCOYWXi88d400zU4m2THB9m8VW0Ht+bs0j0iz6NNlWDLDonm77N4yMs2oGOoQeiRnkA3R5F3haXmRzf49LGs+gWPkW7'
        b'hI/F2tBevL9DK/WqpLAwzjoJW8VXaspApTTG41YdPShHxtlbXxJql+MtsPDOi20BtRzvhMqGGfGOPBYac4JFu/A5Oz3CMsSggUeqbEM+aeYtFh1ZNl103t6hmo4us6SZ'
        b'+cSDhBjdw6v4SX3miSNwh2zIJhrgZSrugbAXnsHPwofwVYpF+CEstQcwJJtIDXoYb+qmHI4u8DPxlXzvBlv4/9rQ1lmkB1nZClxeUoezJGleNUomOm5zxH4mA7VYw8VA'
        b'jt6jKnIk/Ck6/edYzpv+l1oBqqFIgQ1eEKL0HCKqAtPIZTrj1Xg7yd4disJzq/g6pVhJn8DaaZ0GX8VUOifWqCH+asaIj4KoGV3a/9zq4kWi2hIRqFtlcYFXWeyA4lWg'
        b'n8aX+uQlwslAtvCysgS7xSwk19XaVukMAIMX6ipeRMOXGcutFd02aZG3SU+HkwaAtNUj/OfW8+lgUDG3O8hLfJCTehaJvl4D7EmMV8kMAtzsA27wl6f+N/DVEvylrNd8'
        b'wME6M4tKq4ik3bVG8JpWVNJg9CRtvXhjqI2Esxf6FkZ37agio1JERiXleeS0F29JlV9LdD21ZKmvJclfLeN9PfwUW9FdA2p8CJJaShUXgO1v2NNKE6u10fPv3bbh/8YS'
        b'tFnHPz3dRYDNIMqHQ2vttF4dFksNPXsPGg/VSbq8SM7jS4pYCSg+0LtMl71OW2ReVWOpdTq06dCbrvJyAnQZOg4vrhhnSDOk6nqWqMk/OdPVTF+qY6l/lMqCzyaRI17t'
        b'+FUZI5vOoteq0ENrTE2DzEG8fI607/jE9O3yLHOCJSHqient8t9Djiv/OPqt6HNLPg5/a6VCu7NozdCDG0bzDOZDRibE62TUnI23x6G2JLy+K0+1TKZiE9qOz6L7Pg8i'
        b'fBtdDRSc+k4VD7NcGtwonlifgZp4RjyxXu2SzOlow4pcKrhwS1jUhg+n4KPRPZnRlMRu5T01JbpMMevUK2KAAa2O8LIDqYz42tjOlXWYzObDpT7AZLYrqGE4sFoQKKZD'
        b'8a/whiImBcbNvrA3FEFSdxecKLE4RTOCy+a0ghItUXqXQ9KaaeQJp91c6zD7RZAoX9WlIlLHJGpUmWTKhzJQFfyYqyx201foduRfV7Op5FOzK3cnUdlM46eYDJ8uCWFc'
        b'xEEQPUDbFvassRF1bQF67Kex5aID1i9fbZdTF8OfDTr2iSkHcFcf9TvTE9PSyt8LvzPJPtBt/4k+c0a8Rjf9fp8VvYvObJp4fNQWwOF2OTMyPHTv8hIdR8VbNbqOjobm'
        b'dtItCvBdUC8uFjsJ7QzFm1EbyLeSdIv2owdBJFwTOiv5U33VLqvD4jR654hyboqokRKignQoyoYgAa7u58WrLu94YVHRi+Baz05btITBh9XkhNpqf6yO2hoEq7uH/iLS'
        b'SXinhnfHCLb6GAHlRM+LxQbvYTJCSLp3IKP+N9T3hhghff43L+A+9hFoK11teL5VV2e3VllrzU5oo1XojoHWWhoksj7KMCqIpaR785Ag2mBo973eoQDIoC22LHdZ7dLo'
        b'CJCqcGoFS7nV6QhqkiJrHlrgqKvxCmNW4Kpmm6OOViBWLQ5wpcXu6N5g5aoQW5QxIxv4tXW5i9QHIkwC4c1au7dVACvbaSbc+qtJR1eHTlUBNezElaDduQWgHYuBKgqS'
        b'52T5nFGLcVOejpmTxRfr0MVs7ZJyu32tFcjLjKqImph4FzlXp0Ib0T2fpaUV9FZiyOmogXgG7JsLXGwfuxzfVM2PROKhqvjEV3C7BmZ93Tp8gUHHh6HNrnRCtPagI1mO'
        b'cNe8LLLBOhc36efhphUj8U7cgi6WZukJlO3ZeXgbCwTrjG4l2j8cnyvlyGmh25qipfiyi2w7RkCn/M0/9VBheoxYZdH85HlKpmidAp0ZjdqsrtlK3lEP72y2vZ/87fth'
        b'61M1mXPWocK/jcl7U6ZBzJgYefwGedZff8yN+5b6L6Vj9v/61WVNH3xj0c6r3/vRp7ajnwlvJ0e8zG28U73nx3/8hux7c1Z854dP5v307G/x8vqIE7+e99GiX0x4+nD9'
        b'l8fWHUm68F1P9enKVezwo0O+UfC5LkRUr2/k42PJ5PSGT/kOreXwkb54v5N4X+C95vGhiTCye5aKkXK8pHQIapfhN9Dt3pLujy7jR0mz0WE/r2m8AZ8QvRSPTUG3cXP/'
        b'XD8zgyaS74N24jPUzAOSwEl8TaTVWaUBlqCVK0VTxv50/CoRJJaTgDVeQQJdxA9pN7Ias+ixWPxwbqBt5mo63bNLQBfQY2rnUKL7PtvEtDwqo+T3BhGmpdAweo7PNoEv'
        b'YInmP597DSGjHWTCe6Y2roPw91awIvHXSCxAzCm6sIKAWrxNoOTdRwp74ge8X7EOprAELs2s1wVzA/kf/Y+vYgsBLXkxbRmIWrfM4JSPGYyialoHxetJN3kB1UTazpaR'
        b'o0HdtuKMrxWTg5K6jLkZnfcBgrSHeDbV2C2VHoXDWlVrETwhQKRddjtoALMqZH5tJWZxjZcG5ogMqyM2F+MOlZx7NJUaiX3JmuTAvuTAvmSUfckpy5KtlZf4pSX2dahH'
        b'9iXGJROlPcoJ/DWd7jeiSL9EPuB913diofs9BToK4lv0FRhBcs9M9D2DNsNcSxQqs/SsfClwtKCsjGx3AXcpKZwwLnUU3egim1AC0WFB1+oWvG/wJ2ln2cxV2oZqi7SN'
        b'Bh0mfe4o4e1Ud+Br65xBwNgt0JFaxyRtemcx2iR15zl4YVeFTl3gIoY19AjfHhXIDHGTRJbnZsGtYomzsWlRaC/ai9tzB2Xj9hwmHp8Jx4dRe4TrJahmJDmxnGtITswB'
        b'Wutfg6/mrJy5CTl4C94phswA8RufHaQBInzJReX5YzOyuWe8FiR6U+KeiCTGRZRuoQC/1kmcxw/wUUmkT87JL5EkeirOt5SE4MdlaBtl8pH4wADcQosQ6/hafDcpmzDS'
        b'pHkkOJTf/kuWPifPkJ2cqGBwi06zvFJJmTwol8fVATs1pDsEbgLekQeyun7FKl1yjpxZjc+HoFbg9md0PN1WmY33lVLAPCObig4ILLoUU+Sivu87DCuT6Nvobq/cfOLq'
        b'dYh7JXs0jQyXCc16mJSTL40hy/QeiVsieXxEjh9b/zWxTOYgJ3Kbd+8Z9F5SFE7VyIre+fkCyze+dfbUtx7OiIgs37X84IiRF5pXu7kvzu3Lj3lw6GcLs+UTlhy89gtl'
        b'fB/8ydvlq+aOLXm4edtPju/444H/rC2LnPy3G/8q+uv3P+l/dNdPX/so/3TRt1LyRyUWnvp48oVdptBBzk/OPkx95eSyH5QrF9r/9ZPXpv3D8mBlxqQvX/oyMXXw68DJ'
        b'Cc1XDKD6ODA3rnwSPsaO6oc3i6r6kRB0h/DwLgwcXc8mPHxPb8oj+6AbjYFiQHIYPtKvUjwrsLkBteRm5yf2fwXkKg4ErxYObUibRDWt/uhYYqCihXehTZR9r4JGkJlw'
        b'WPAjsV6ZzEJ4N/Df12nNBfj4XLJfQv1pFTYO350aB03bI/rk3WJnU5/bQjFEix7mIiUTXePxvjVmyvnX9kd3fHsHGeg17/ZBDt4hck/N/5G9P5TwRIlqUO5u8HF3xRgS'
        b'NUPl4+1q6U9Dj+Vw1MCv/rdCvrq3P3+V6hJbqRC5tUAuFnKpDGT0IS/mFCwTa6r0iQEWH/erhsv5QFkg7sdBZIFgbX0R/qvydbA7Hvy2jwcPJQwDyCllHz5+428Q1MmI'
        b'i9JFrgCqnqWLsROKZCeH/ezEUkBcE4W6CqORblDYSbg2upHh4YndfjrJBtkr8Si9lmViCqKasycsUKMlgpOfRFVN3wqYuF7/RxtL3eGdnZD0fmS+1jLEuC3jomUKVvaM'
        b'g7ka/Iwbp6ARgzj+6/2GyzTqKJZTi3GH1LJolosJLBEl07LcEIrBX1LiWIIPZDvyCqgoj06iNiCP6tUcSNDn8e4uvE4t/Tq+7OR/JXBlMoEvk1uZMoUgK1PCn0qQl4UI'
        b'ijK1oCwLbZO3qdoi29hKvi1SULVyQiFISKHuyEqeulITryKNJUwIFTTUxyq8lSsLh3wEzUfSfATke9F8FM1HtoVbeolhiUDyIo4/Ee5elSqhtxBN/KSgxqi2cIAbKfRp'
        b'pW7ftFyvSuJ51Vcq0RvqJD5XxLk7GsoQH6z+woDNqrI+0DZWGCgMgnSMMFgYspkp60t9qpiyWCFOGAa//aQ3hgvxUKq/MEIYCXcHUD8ppmygkCgkwe8gtwJq0gvJUGaw'
        b'm4G0QUiB9BAhVRgFz7X0XpowGu4NFcYIY+FenFTzOGE83B0mTBAmwt3h0t1JwmS4Gy/lpggvQW6ElJsqTIPcSCk3XUiHXAKFMEPIgLSOpmcKmZBOpOlZwmxIJ7lDIJ0l'
        b'ZENa71ZBOkfIhXSyUCQZYnghXyjYHFJmEGR022KOR5FeQ529XgsQksjaFx+I/l5iqFuQ/0gIwiq7mQh+otRWscrnftTJySfQe8wOFdRYnNYKLXFSNIsm0QpR+IQbRJ6E'
        b'OkWLim2Vtq5WlBCDSXA6zqMwrjDbXBZPiNHbCg+fObe44OmUaqezflJKSkNDg8FSUW6wuOx19Wb4SXE4zU5HCslXrgSpuSOVLJittlWGlTU2ncLDZ+QVefisubM8fPbM'
        b'Yg+fU7TQw+cWz/fwc2cvmHWR88hFwCov3AAbWMCuSCMhv5xDTkjwGq6JbeQ2sQK7jHdENHIn2VOMo4+TE7hGLoYhwYubuEZA5jWswDeyKxh7ciNLHBvhLfYkT0IeC4p+'
        b'UC6WiWbGM2vYWhk8V5JUE0Pea2SMMqhVfgoIvlEhqKg9MOQjYzAlpLMfnDTPHW5wnV/oTrSnIyEqFmaxDnqnByOWOGSTqKdZSWHymLRR4/3RSAB9JLuSyPlaR72lwlpp'
        b'tQj6oNqA1Ul0B+CCXo83CtmrHIooC+qJ3Vru6kafmEQeTzIJlkozsBcfGplAQbFWVJPareI4ATJKcADBuvbtt2TOn/ax1tItqY7ejIx3jPSwBg+b+lvCN377DP495Q2p'
        b'qQU6pSeyM1iyi2K21VebPep5pCeZdnud3SN31NusTruDcDi5qx6Wid3JUIMClR8I87GvY3o84k6Z7/+wku+uTK1goyVTh5ZVcWoQkVZHiAjw4o4BOpY2rVtZ4u8+twAv'
        b'CJ9XQHJnpKFTt6reojXBlFQAt7cZZoq/JpPBPot5Aff2iywdpW6b9ZlPxBlAfROCI2IXcJwXXKQEjqzhpVyoT7zi6YR4VGaHkfqEelSWlfV1taDYdtuUL1gpUGQ487SC'
        b'egu4aspBOYbBkEZBW28zV5CNWLNTa7OYHU5tms6gneuwUEQvd1ltzmRrLYyaHcZSMJkInpqFpS4oSAoE1tJ1CzfwSBNLA0j4YpT7jjSx1Gz/XIFFPvo0GMmZW0+EM5Hc'
        b'WFZWVJtrqyxaO71VbiZ7DXXiri2UMmvr7XUrrGRHtnwVudmlMrKnW28BzpFBhhY6N8Ncu4xa2h3OOhAdKXGofS5CIBEBb5OMtEkmMr4uuvBFMkPokc/CDuNL3GWDbOOR'
        b'6PEWZ3VdBxfTax1WoKhSNeQ1ssHu73TbXR+liiaR+POTTBKDDbIf2KM5pLyujoT51Vb6211cdCqETtMQlEQ2WOywSFcAdzSXE0+BbiwwAQImQaiuh9jCC2iwE3zdjk8m'
        b'JWdl64nWmzufGCfwjix8Hh+EbOHchBx9drKCqYlS4cfokIra7dHpefgBKJNX8c05CTnJJBrzziR0F10sQDfx6eJkfI5jxsyWV5XrqCSM90bgjQ5Dfg46go/jfQ2KKCYC'
        b'HeANaAfaSd1A0YEU1t9ukVCQnJibXJyQM7ZRrDxXDsKqCt2fgQ+LAd7PodsD0WmNI0EKZS9HO1l8dXW5GG7+Bto5vwS14rbClXNxK943l9gtCll8A18bPos6BNSjwzZo'
        b'Eb6DbuTIGR4dZNH6KRk0oCd+iHeji44sAwjtrdSwkYuuyJhe0GL0Oj4bL0blbZ4wad4YRwKN8SRfQ6JJ70ZHSq0Tfx4ld3wLCvzzgqlP60vFM8yazL1/PPAfJdfWtG75'
        b'ZP2OPtV/+PGl94UfsP3f/2CE9cw7aXuOHX7j/t5XPm2ex8+YLavZenjHOx9c37R+XlJb7JRMt2Z8tOlqzk/m7PrzJ5/fn3P3oyFLb72X5WKXHrf1+eTMz0Yo892uCVXv'
        b'/OBs4/rSWfdf3ffLwf9zfOuWc/IzupllKb+c/RvbP3868O6Jv/x9S6Vu4PjaRR8ujXg1/c7vJ2xp6P3NL7Lc3/nwxjf/8QGO+sfC/uOvTFv570GfDNL8wv7xX9Tf/820'
        b'x/94qeHoUF0vavcfia7F0ahVJvK1ASUjS2bR5UkldL8hFl9Em5KS8TbcPKkgJQu38oxmFq9ATSH01WS8eS1qSUkeiW7hbSwjS2FROz5no24Ncag1PSknH7fjg3nwaCiL'
        b'jqHTSaLHw9mqdWgv3kMMKflKRiHjVOiSGMkb1Kfbw3JJc9A9dDwXXuzLotPjdNSEsxZvY/wtOGp8PmAXph09EHdzto9HN5MMuokViV4MisDX+VV4e4KTrBLl2oLcbL2p'
        b'kJphWHRiCdpHt2/Q/gnoGq0cubXwkqyARVfxAfSYutiyyfgyMbFk6w2oOSU5a9ZkasjRamX4FiyMw04aY+qaEt/JlRYZLDDUmgJIhHbhdlhlifiBHG+0os3idtAD40Da'
        b'01y8D79KLIHNLBMqcPiILo42E59JjkQP0P3cwmSW4Vaw6YyMjvo4BW7O9Z38DMUt5PCntZE2csCyZbn5ubn5Btysz6XBG8zoPLQyEe2Qozd6TxajYbThIxxuKUCX8aEM'
        b'vYKRzWTRwxnqF3CV/DrnJvuIdNAYSPqpDWk6oWPrxP/q8EjJekRcSKOpm6iMupASS1I4KzqWineJcyn55dbL2NUDJYknKBjvwSt6RPLrOIey4qtUjmiDyzMiR5BpFG1H'
        b'zIb+QeJN9dwmqJOIkt370NCYMDTgGMgHrF9MGI5+g+S5ogp99KNg0kGGyN6kUzmiUEjEGOA2hGP55DJJSCASg0MS9bsyI2kroZOU0UmmCC5DdGVtpV3lFTPhiQEs3MtR'
        b'6wirJ/soq4gw0rVl5opqcYe+xlJTZ19Ft30qXXaRKzvoN2i+mr131qQCJVg/p0an2V4Faou3ZI8bJ7W+nRMRQ7wbJ14xigg/Foe/zv8VUkDwo+wq0TOpIZJE8mBMmrmm'
        b'vDNFNvHIRvsCEtqESVg319SYtyxUCi5ivs2sZBntA+X05QvG4sViWPsTqGWQIyyMY1i8Ywi+yeDLypEu4uuNH2fhs37kjsoT3k0aL3ctLTJmz0+eNx9YPdl16fAeALq0'
        b'enDkpDx0yJo76CO54wLU+Jt9tfmt4qH6f74XHskNmjFzysa4nSdfzc7dolf/dGHT77636+PPtvy7xPb9979zpfLmu71Chsyb94X2u6dKJseNLizqnY9mbqx/t7XPtvyN'
        b's2PTkqMG/vuza87f18TeaL5UeusP7Hs/eOstF7fvypHfbWr/n825Q7/Rgj6/e3Xu8vzsV779txFmneHvE+K+WPyHI3bXGz/89bS9r/z++siBt3+drlu+JP0v9o97/eHf'
        b'oa5fjLP97VVduBiw6BK6NysJbwD63rHjPwrdEn3637Cjc7m+cZAV6ZiIebytAB1wkrNAqBXddXXhFRKf0OFjeOOUdZRfKvH50b6gSKfxPQU7l0d3qGMC2jRtZSeCL1H7'
        b'KHQZvRGBz4lsFXhvx84Di44DKzuRhE/R3YWlaBPellSIr+Pdvogeoeg6B307wdHX8+eiR97oSbJ8Ft8yocfklD59GI/XS04RlGOOBUZ8FSS4DU4aUOhAb/RGB9dEe2cT'
        b'WdTLNpPwFSdR1HA72o72ETG1Fm8inmeFAaPC4etoG2tMUaEzeMcAcdx344fo1SR8H9CP7LjIGcVSbnDRBMpZ16KmoQEbMYWDRS8K1LqYFpiyoiZJnw8SqRjpPhW3gsi6'
        b'l7eja2hvsNP1z8vilJLaQJlamh9TU40j7EwhnYWIYaMo4yJRQ8IpYxNdIsKJG0S4xDKkqgLc4NYFcq8ewodwYtkO34f9cEngOvGsmB8F4VmdGtBFKyeUhmrlRFcgWjn8'
        b'EftZmMA6OUjzm9gYKCBw/jl6Av0pF299Kos3pFVCh0j7PBpjbZ1R0pgdHt5c7hBNLEG0d0+k0bcDLpoiczjp/LiGg1HkVvf1WlU6letiL/RtPZMweE306xObOPuwRpb2'
        b'hVnG27WkT/Y+jexJ0gfmFLuGrQ118gLbSPOkZCUvWhEhLSNfsKB95AqejvQxzxqrA5pRUU3ZTjxQfWKgolozScDs0SHoba2pt1krrE6jOOAOa10tnS1PSOmqetEsRQdF'
        b'skF55JRHe1SiUbfO3o2TcLix3k78fy1GWn4OGSwS1kRN/W3CSZg8VgEyCz0PLw1cwBtBJ54OGw23SsygMBTEELqUreRiRIdIGIAosbYE0km92FX7Gt+khge2UmU0Aky7'
        b'0biYk+wy0f7mMfFZ9ygYRVviRUKpFVWkFUqCZjDqfqA74ZPSSA7/G+nJJXpkIrID96VHAaIZScu8gGkEBOYkYILAnuLW0EFoZJf5BoGdcpGzn2IkkyGk6Uo8EaQZCqPR'
        b'5jQay0krSPVEtl0d5msHefbCzWC9zeCmvGQnXNV+sRvIFqOxEu7YL8ENf6iWIFB982/wXza9vAtiGVcXKcJfyi4jdip6n6ToYQ1xIkg7ukFYaI5ludG4lJOc2tVUzOee'
        b'qTm/hpESXRrmsxNq6HAQoBrf4R2uh+7XQjfrvdMfMOy1wQbgq4Zd5kU+dmqPo14Fc+oIMupVX2eu5dQGS+Z6as9zDWqHsSEYVEuQFeZzcidD6l3pHdbeDiLddT0TG5jR'
        b'SD6CZL/K+FmivU8Cehggtg4P2sO+ZCuHoYSX28T5hjjpIt+xwCgp9QYJOeG726lxsOLNgmA0riVTThkHDb7ot+rp46CI74dfpIGnvGeQYDDudTfohLjRGjcFGQx7V1jP'
        b'MRixnQdDpDbJ9jsE6t3gnXa4yo3GraQN90kb/IgcedB9d8NpE0IDO2x/0FN3aY0tXlquCaDlXaHxjB9VIfq1j6oonQylIJCP7txl0fTvCS+oc2YD77SQk0YWoQMP6DB0'
        b'd3TGaKxxARLu4KRdDDU9jRqABLTAcyOB6OdhRz2NCq2xLRgSdIUVgAQT/Mcksis6DPCN0oDgiJHSgRjdjEio0ei0uyyCdYXReIAsjA7aqwYRYXWUr7G+Yl+/vf197e3f'
        b'dVYJDUv56gZrgGXZ6urstCknyKC+RQa1t6+dHU+/fkNjfA2NCT6w8V/ZTiWNHWQ0nvc10Q/F6jqvfZl/6wLk0l7+rXOS9pF9a2hJR3oxt4Zbw0ut5DeR9vJiqpKT2INH'
        b'ASMCYEHyplTzPxl/0ulVMAjp9MgbqutsFuLEW2O21gqW7iRMtdEo1mk0vsFJ5EJNFZlIjqg2smere/l67C3ZvVRJZDmR04TSod8UKDkE4zY0FFuV0XiHDPG5wCGmD54H'
        b'mroDWuVXQauvcxiN94NAow+6hxZNoTlFSKwfKtFNzMMBc9EdbFCOjMZHXmklKoBtlQeD3h0Pp2N6swdI1loQRL7hI1cdcOiD54azuUc4IXShmqHCb/ogRfqvYfLIvoUJ'
        b'YiD1rRNy5omsjGWMXeUEjZN6dbACL8gI2+gLzVhDVgTR4rgm7pS4RqSVQQdCXvBbUunTOLqXa62t0tbXNYi7waNSRa8IV319HQn085RLNXjYUbBStnmny6Na7jLXOq2r'
        b'Lf6LyKOEmqqsTtBnLSvrvapbtzYDGAcK3Gj8D6/kq6LxR8kH7/xGRCp0kXIbMiy6lE7uf3abVJ/DVuckkcSIe64nPNDoDPnKSkuF07pCDEkN5NRmdjiNoknVIzO67DY7'
        b'CRVtP0YuHY6EPvz0qHwKeyi1YYo7p9QqThVX+xFyoVTmVXI5Sy6vkctlciGRTO1vkMt1ciEfKyGB5BlRjnpILo/J5U1yoWwVkwvZdrOTgOX2d8mFxIOxf5dc3ieXD8jl'
        b'++TyA3L5qXeMdVH/fxwTO7l8LIfLt8mOAHGDUDEyXiaXcTK2438kF81yfbrxQpRz7GCWG6liY1lOq2bDFZpQFQ//ZeEylYL8amQaXiUnf+G8ShHOh6vIf02Ihhf/x4gf'
        b'AX8ZbcW7HeQEWAr111bFoo34IufqhR90H+31x51cEr3xVStlNNqrigZ5o9FeSag3KcgbjewqhNC8kgZ9k9Ogb0opyJuG5sNoPoQGfZPToG9KKchbJM33ovlQGvRNToO+'
        b'KaUgb9E034fmw2jQNzkN+qakDo5yIZbm+9E8CezWn+YH0Hwk5AfS/CCaJ4HcBtP8EJongdy0ND+U5nvTQG9yGuiN5KNpoDc5DfRG8n0gP4LmR9J8DOQTaF5H831pWDc5'
        b'DetG8rGQ19N8Ms33g7yB5lNovj/kU2l+FM0PgHwazY+m+YGQH0PzY2l+EOTH0fx4mhedIYlrI3GGJE6NTJmWujMyZUOpIyNTFidMpwQ43RNBzr2Udhwn/ehq5/0g76lL'
        b'v0JSxLlOxYhDBfXuqDDXEtJYbpE82JxWuhvj9cGgYc28vm3EDUPc9rAEbtBI20KBbhdEJ/I7+2oihNgsHt0R6ipcRNL31RxQW53dW6HVKZrFxFe9uywZ6fmlM6UaTN04'
        b'3gVksislHxKztpwa8aA6cXPM/2yuXgTp7avkXOm0W8iABNRndlBfTtI46tmxAmoy22xaFxGwbKsI6wk49BvwcgDLJYorITok7I+jjCUc0K4iXLAf08S5WLvGywmd1Hp5'
        b'il3DC8D1jOJVRq9yelXQq5JeVfQaQq9qkDvJbyjNaeg1jF7DBR6uETQdSa+96DWKXnvTazS99qHXGHrtS6+x9NqPXvvT6wB6HUivg+h1ML0OAf7NG7UCC9eh9E5cI3dy'
        b'2ClmJvNyEsi6sjXyRtlJWKOnWMdmAdJ9mTWyWg29pzjF2ncJSuDx8Y0yYhBcI3OOAJ4v28Q5jjhHCqpGmWi3dSaQu43yTTzLLF/RBP1aGt4EYqDjtRxmI0Cm8kFIgf2H'
        b'RD4YKyJ+l2XS80KgDGKWhzV6OKPxqdwY74h3PI3vXEm1mfg7dbhMiSZTnUdTDIzfWiM5JirE/UEx7ihvtAoeudFlcdpJYBjxhIInQgxt7jufZp9JWBP5xq2dKBR24osj'
        b'hipZRAWDwKONIPiJG8FQY73LDgKtBUBQoUBJ7ehOs0dhrHFUUdDLyHE/udEi/tDDf2He1+iHyOClimqyiUkD35qdLgdIJnYLMXCbbSS6UW1lHbSYjqu10lpB3ZNBGBFp'
        b'he+xucbZ0SFPtNFWV2G2BZ63J4GHq8nWqwPaR9cqVEN/xYDEnoHGTkMOgiysQ6msHNI1Do8aGml3OojTNRWrPEqYFzInnvB078yIM6F0WJzkgU4hugQQK4JHsayBfPHd'
        b'L1rBWuarQyXQ2fw5EfvKGGJ/VgUJiqXqcqfb/xy5Rkrh6MOpWSMc8jJ2dd9OI/BC8Z0lx9M/M0z3Hp5RoOqIjqexnUH5PFCnlFJXgtplHUco9WLcA2eddOyUOAAKQKKt'
        b'lauA8PoRxBdwSCUGGXtGT43t423s0xGBobLIvntNnbPjrCuNHPoioaKyeoIb64MbGCGrK1gSqvT5oFKVNbcnqAMCe+sfHasTWClu6PPD7TEw1mAfXF2QwFj/W9ClPYEe'
        b'6gP93+laMVqsw1UuHaugzuYEnuT9IkVf6rFdVEgSK6JbikSmqYfXiDxCI9IEiedk0JZ03Ku0WghASUCA2qFAh2+Mj/Y7tInSOCXqIWl10l9v9KxEunmYKIawSny+waLK'
        b'fllPg5XgG6wxXcOSdIOf6TPmp6fAJfMFsBRIyF96akeSrx1TAk7Ek6gflvLAs/Gd25NRnDkzZWbmjNIXa89fe2qPwdeeYjr7fixb8pjyOtB3cuUxaGfS8CSi45KtwbzK'
        b'IR0J19ZaqsxE9X6RI/z2v/XUyjRfKxO9qO51R/JrsMSZtQkl8+aXPecYVYnQ/94T9LE+6CMpca+rW0YkWfFgOwi49fV15PgSiEQu8Sj8C03PP3oCPcEHOqLUdxrl+UFI'
        b'vftnTyAmB1KwGliz5iqLHxrWV69yEJc0bVF6dgGscdtzApfCxn3WE/CpgUPbAdRWVxUIU5uQW5w568Vm9fOeQKf7QIvueLVCsrMuGX46GLc2IfP5YUqbhk97gjnTB3NQ'
        b'0GAL2oT85wcofh7C/kVPAGf7AA4VfQ5BJKwl5zakpSIGwCiaW1z0YiP7r56A5viARlEaRyVk6QjKC43ls56g5HfQhM6Ui8jVxDmGpBNmFBbmZhfMLs1c8IJ0kzzrFnqR'
        b'D/ofO0MPlPYN2llAI2ZboD21VC50+FTuYBHegXjNz55VSuK067Wz52XotUXF2fnpBYWl6Xot6UNu5kKdnjrbzCIoUy3V2V1tMwvzYQWJ1c1Kz8/OWyimS+bO8M+WFqcX'
        b'lKRnlGYX0rIAgZoBGqwO4npabzOTYFNiQI4XwU22pyGc5xvCOD+iLqpGImKa6WI0O2AUXwQ5/90T2iz0QR3XeeJEDc6gTe84OpZdMKsQpmBmwWxC6QkqvVBLvuypJYt9'
        b'LelbSrm9qDbCFAoEd+qec61I+/Pynoba2EHjpWAp9CyiCMjSYf7x10VehHlzPQEvDyR6HcSO+GJric0qCFPxOoXQHZB5EkDHSOqxpqE7gtQVqj6cpMXTqmTHA/5km+Bq'
        b'JOXl1MONnpM10utJBVyVpwArO5r/dHKx6K9MLFc+GUcUuTpsaMFFMoNOZf8T6WYNuXSK1UxtECTOgL2OodunHQGdO20ShZIPtklVWnhpj1HBxdIvLBEdV8GuHtBZ4fR7'
        b'p/uZIlY0weu0VyqCDDZNZGeijpc23UCT7qLe+txauj29GCvNkV1JdnJPMWTntqpjKw76r2TJV6CIUSKop5pKMlgYyQfIaMvFMFrBGiMW7L7f0X6NEUPp+kaBmrq8rZGL'
        b'ekg3jnM2S63R2ODfmuBGBlquQDcs2E4VNX7QvSVPeCfD1TQf5nQgTa0XXzxhgXYrhWS2Ukqcm36/16OQTFZy0WIlowYrGbFX0ZggHk2AsUoh2apk1O4U3skqFepvlFJI'
        b'1ixVhzFLNCSFBxqr7HpWQh97CkmNYqVBfK5YavZfw+UDYhn6ESPuKEWFcmkvGN1C2c192f8uWka3v4rnK6eRqdQqXiN3kTNdo+ZHha4Iq9focvD2pII8A3Ekxzv5+aiF'
        b'SayWo6vo5JSgYRTJP8dKxn/vSuA2M/TbhLwg832bUC6lFfQ7hWJaKSgFFZRVublKVvwmYVmIGESjTE0D1nIkmAbcDaUlIoRISGuEXkIUlAgTetOVG+3p3Qnh86ygp8v8'
        b'GirzJwMkRBAhxUbqpmFkyUa0kasi4QN4wScZyKhW4AnxfTMYkjV1gtlGPhEX19mSSSAa/XdMHF5Pjgks3an1VqLy1tGZvpEN3vW8xLpEO6KaXT0wCJwXP61uH9AT89vq'
        b'MxkGhfZC34OTmO3MnuC5vfBeREzJ7KnGpm5r9E06cYnwun100HsDqXVWt1XDg22k6qvdDk63dL47XwxpgDpgBjJaSp1afTA7s1QJJqXmz8FSK7+ape4isJLZ7vsnMdXO'
        b'rvs+jxryESuvi5QjxAmAJWd86sC1jHf0hzR1h6JpkpIt4+2DnXJxcwzyipNK4sPHMtLq4wueJvsLvTXkSH95R5yEkZ1aOjKwuFBnEQ+ui07/NHyL92wc5RAgEh1npKUp'
        b'fmR+NkllkQv1KSGzA+ysvh5Uba+3f6gfCFq0G2cs3iwIe70Sklo6UKKmjiRdGDMdYijfPfaoJezp8BfqmM1OmJMKLx7lJYdPkEn6BQMWXBjzuVRG01UiUvBGZiaziZWQ'
        b'li/oIvr6XiKnEAj1fFlBjl8QWWY3t5x6VYlslrOPISO7VkyT9eBhnZ1xMQIuJ72tj2ZWJwdrvbPOabYBQSJ7T46pkCB0vq6mfqqO9fAOV01QKUlO3zpB8Px7ZE0FHRda'
        b'pkAX3lk+6nC7ocjSgScdogSVLPJZaQbsRT7xoofIJBlQaA0vjZ2KASasoKFYOQ2v4sN54lDiIjb9RejkNODKI9DuzowZt+NmPZCvmfiyMg9tQI+7MOcY6dfRxgYwZ5hc'
        b'+p8/Ki/jiUMJcSch3w0U1IT1ki8ECuGE1Qq9joaXkQ8Gy4ENRwm9gfXK6QlYFYlU5Y5y96tUCtFCH7ivsChpVCrxI8NKIZakhX5Cf+p2ohQG0PxAmldDfhDND6b5UMgP'
        b'oXktzWsgP5Tm42g+DPLDaH44zYdDPp7mR9B8hNiiSl4YKSRAWyLh+UQrY4ncxJxhd7BlkfA8CnqgExLhaS/oDSskCXpIR9F0smCAdO+QFGGSFI2LxADp+M5iOPQ2kva3'
        b'tzva3ccd4+7rjq3sQ6NfhZRFtynbYoS0VlaYTODAmPA0BhaJCNaHfJNQGCc+A0jjhQn0fowwmhLnKR4NwUWvO4SHLfKwhTq5h5s9w8NlZ3q4zBL4LfVwGVkefsbsAg8/'
        b'MzfXw8+eUeThs0sglVUMl4ysWR6+oBBSRXlQpLgQLiWZ5EFZrn0lJUmzs4t04R5uxmwPNzPXXkqoG5cNdWcVe7i8bA9XUOjhivI8XDH8lmTaF9ACGWVQYC40Jjtg6Xtj'
        b'nVOvB+njAmKALZkv0rnseSOdd/0WatfI3LICesJ1atwIIp86cXOhAbfic+h0Pokn2hFFlMbuNGTTw4R5+uz8OVmwQnLIeUzyWdSpeGMEurEEHbBeuPwrxkHi7cW9e/YT'
        b'0+9MCZaEXzzBCeYss63SVq43L37zB9+4sWsUDeBf9R9K+cF3dDw90o8v4x3oQSi6qM/yxpXshe/xmagNXUaX8HYa8mAd3osf4ZZCvA1Aswy6G6ZCR7iV6CHaK37k6sLi'
        b'COnDzNPQhY5vM2M3rOkt3kOGX71ZzXnJtfdko3S+cQKN5h/tj1eB3zuWd2yW28n3f4N/yhWIFy0xwlfMB/k67w0lvcH/f9Q7QY4wBm1HhcpvvgngwA9iqig6qaWPi4tr'
        b'UIzK0/FBTFVTCKBYCKCYiqJYCEUr1dqQEr90sM/tkr51/SbgwAIXIfmL8F3UlCvFEiShapOTQ/AGA4lPS6O7kpmfW9SANmehCzyDd9SH4l3oZjmNcouPo7tDO94F3CtM'
        b'nicdtM4BfD2MdgHh3pk7PwE3z1cBIssAN9AboWHkE+D0xHdbrILRyFawjNakb2fHMuKHZe+ibeg4bld5T30DFobgI/QFz+gQJtJWqGBMJtu65cUM5RguNd4fEJvW7/Q3'
        b'PoFO03DvC0uUq6b0dtGj0Qcc6HBudn7uQoset+pYJrSAg8W1Db1Bo7SMQo+nJmU50FVyVBzvHZ2aijabcpk4dJNHj/B5pYvIRujy6olJBeSYcGtqbD4NKS+dMU8wJCfg'
        b'ppREEoO3TqcCpnUrjfbLjA/gi/bUXNySnZeiYBR9uXC0C12jKEojv0T3rV6NtiWRIU+G5+geNw5fWCPGJT6Cz6qSxMnoBOoCviGCm5NAo64XJYjNQluyeGYw2hKGbqMr'
        b'aI8Y3OY0uoG24X1hjhX4uoxh0SEGluBRvI1G3jeiDfhOxwcic+fXQ6nSBJjJFr0+f64YPF88X59nRm9I884y+AyvwTvRRTHIDXKvwCe9YebxI3QNb8uD7vSezeNj+DV8'
        b'gH6ZBF/OLpWGDwaPYo0Y3x+6VGaRxm8OgcWhbRyDbqLHoWPx+lfolwPw2Yx4vHdOLyI/rWby8Ua0hUKeYo2H0b7WsALfQM14CzrYgK87FUzYAA4dQifwIxrJeA06JnfA'
        b'/XnkwwIJOcn6kKXQ4RwRWHFCR5sUDNqL76gZ22j6HmqdW5NEhgKGpoVUnoJ3liQkAFFsSimY6/9hAbQeXQxh8BGli1AMBd5iRpfzQvEtfMOBby9H/4+99wCL6treh885'
        b'MwxlaCIqIipiY+jFir2gdJRiLyBNFAFnKPaChQ5KEVBEFBCwUgQLqMlauaa3m268N970Xm6SG2OK3977zAxtMJpbnu/5Pz+RYWbOObuXtdZe633z05XGm5FIUEM8JbDf'
        b'HgoZkNHcNdiEuZTyxNllKlb4BATpcRZQKoELkVFs5O+y0OMMpKdk3OyIhNeFAVwqXQhJs51epdrsFqanpqy0hqL4v36wRaqiHFjVV1aFL+4Ikrib/3D7xphPOjpPPO04'
        b'e6G32azZhfOPxXo/5W30qYvfgNXWdrWBC4v//pL+h/r3pv7LxUzx4tsbX36h4K2wUbbNRY2zBho43pMJ8qDaFyvmL399jVet7ZIlA58aYRQ2y8Oi4fiq7R8WXxZ+GOew'
        b'0/blI8t+euaaxdYZi9cH3p874vPsgKq3a/I+8tkxIypG8c/P77gP/HK96Se3nrTw8Hnv7RfHt6Y//8SGCVZTrpZY3s4Z+MUhMHbLe8qmSKE6a1m0tezpr998+ui+6Cd3'
        b'Bly7+8v9Z+ufHB52uujF5bK/zBz28cRnI56XVSjJvpg27hO7dzxmBVx+4TMb1eGgtNq4cLfFb359r9P/fvWng3Jmnbl9dODmGcEBTza4hy87N9Rt0tTds577YnCc2YJN'
        b'7w/N89KrWRmRdPGT1SfqX5v1s7H9WwvD1nXaPrslW3LL8a95b/06cvvfX1xYgJsLLtc22Lz3G9S/8N6L32fbPPB6707NlkG/3xt5Z2327t1zFKPZLjgUrjmrN0oL+66t'
        b'Es47q3kkM7A6jcwkKHCVQAdjc5LDRQHrTHeKBAx16SmUinNnHyZOqNol3lExZCd0roTcdFMTIyW2qbA9xUTGWW6WhG4exiCeQ6CMzLg6vKqF7YFzKxnsTvRkPZEDSsJZ'
        b'wnWRumEmXmRQEWukixjBZ57jAgVmsXJdELAGrkYwwILhuBeyINcsDdsNiVCObakkU/kQYT0ekTCICF9nqIJzO7uRezpDzVS29UPhdrjk6KKH1b0pO6EWm1IGkFtM7AdY'
        b'TPOnnJTCVn46WW9FOKS2dFJgzCHLAikynlovncpDM9QOYvWEsqV4FtrxsJa6ytXDI4XuBaN2uqjSjDen4mUzsqDnmRmYGGGTWRqZdTsgH9vTN5OyB0plcHX2GNYuy6yg'
        b'A25Cs6Mz5gcQ3Ua2nMdzS+eLuZyDIvm0wZjrA+eJ9LGTXwBnt4iUHDV43XDCVspmkQvnfALJclPoQiHOraFNmk6WvANqlCXFPMZ4QcmMyJqYG0DkntkC2a2K7Jl4BY1k'
        b'RzlEISqgiN5AZz+b+oMDpCZLoYl1z1zYg/vJPnYWcl3p+NLjZBGCHemUEnFc7XW2J1fIwsWTkpK1S4+TBwtYCpf8U6jsAlkKzB02WU0jFkx3ZJIL2Sdl3Eisk9IVE6+w'
        b'lIbBBX/1balwpBvh2AA7EVKk0YzIbuehjsJukeYireUrDCEdcUqE2ziKReOgagCDAnd2CQoIpixO5C5rrJRuxtoBLJP0ILJe5wYHBEE2r9lATEMlgaZwTIQbr9XDg5QK'
        b'xBnK5ESi8JeQ4ZgjYD1pgTaxGG1QDsfILX5OvkQgIYkaTBHWkR3yAEM2CcLm4ZqLKeaQpSZW9SVD08FejzTbEbjOaEsnrMebeIG0XXCQE2S7qpdyPdIql/X0ZOmsNL5Y'
        b'lMIK4+Dnho1qvDYLuCAhm7h1CuPYKsROuzlkzScTRCuqUzEdsqHQtacC60j2lPzRRmQvOuvNsEfWjQ1kz5EqXe3zLDRS8h0ZF8DpQ4sf1qYwTL1SsplnPYziNiRJQ3GL'
        b'p2eIHVPvSx7KdXWnuxtonpERbVmCNyEDqnRL3/95wlZmWmBSPKXb6SnFG80wYBytUsGKYZZKhcG8FW8sSHm1lYA3583JdSPyPY2aNXhgKiFXBHrNQiITZEKX+6p4ONf1'
        b'ib6O4LcN6iWZdyN2bTRSh09p/Jml1OqmpK2nnENVQ3lUZIrWNVmmilofsymmNySK/iM0RqOBUsmrE1Wm0BeWCMsolX5kBnQV373FLuvWPsY9pUP70F3Hxzixpi7TYu36'
        b'BVTV2s57ZvbYRnNl+sMM3Pe159P2jMtEE4Ihls5WjVbSA6H+0f101exp8rVqv6q1D2HL+U1bECddnljxqq6y/VkOT3Za3V/+VIET8x8RxlywqAPWn2a1VVMD6K+NSk1J'
        b'io3tN1eJNldGokrudia329KggC5nMFoS5lT9p4qhtH9Y/8u0BXBgzhHxsWpviE3UB4W0ekwijWaJfvy8xeOV28Zru83pfothqC0Gc9WijhlxFM5N69X4uLmzw6mCh3W4'
        b'sTbL8f0jFvfMuFu+bIHVwvjRLUoLBi8aEjgaYbOT32a4g2OGBJ4ZD7hdfGi397psVRoLeG+Yt/6ZYiew3GP5x+SJpdCBdDHUCVPbg1aop+OHyla1Pik1IZpRxsYoGaC4'
        b'bWRcJHUX0ZmWlptpXkJMJHWjsp3PwmdoB6vxb5kXohobXO2AFK8bP1cNGx4REaZMjYmIEAltY2wdNiYlpiRFUZJbB9uE+HXKSJI4dTTTIO32yySY0me2U4R8tf+BiC0o'
        b'OrBt7eYX9sf46RERCyITVKSEfVH9WLwX1+sf36fLJUHxhyVhUhUVks9cM/oi4pl1BrF3DzoESDiDLL7t6yMKngkeE+PgGuRCK1a46pA8wqBWNM/xvc+TpLFxMQzH7Hsa'
        b'Kd9TTuB2y0ZsG9Nj41FFJaxl7dt1TEITEBOk7LPisVEX7SwlwzSXqnFOem6q3F7jz/tuq6ne5D47rIcqeU8hDw87dq8ZHiGVzSaXiTKlIPpJsb+/Yi5VxYhyf9nEbQXc'
        b'+C+R1uq0K2tP1LrblWnYuucOIvX3EiGpCSY7wMHPCc6EidYl+kVwAB4n4iOlkzoL2fKpO+ziZy8vEFR0mUpdOOCLCJf3KZ+x/cdOkQHMlvxlxKcRibFfRuTE+UUaxAaO'
        b'vPsCx5VYGvCDFigkKRSVjihb1VBDBNxLDxNitSLsNaxm8LvYQpqzoDeF0lR3Df4utiwTMQmpWfoGFuEpUSfqPejCrR/J3kyGoEo9BAfrGIJGoyjb0CMMQ5V6GDZKu2H4'
        b'988dqMHq2qUdqllkqFr3N1Qt7uoYqjTwzkuy+3EHqqMlFgXRkdo8zGQ6VmGNQmBGycmelv7MmgAtWC0146Eeq+AUg+ZcRXqw3d+RPgXtjlJPHlrj5PGDJxlL2MLfphA+'
        b'OHQgen2cT1QAGR0b/tGg1/Lu0Hcr/loeWh66bM+OW9YHrW9Zvjk14EnjSmfu1lOGBzusNaen3Y3y/aMXaFuc6RTU1U3ge3eV8SBzIyPptsG6u0rsHOEhXdJtb84jfWHW'
        b'X1+Yf6FDGu8n1/8OtfqjLABk5Z6ldJKqqInl7XGLvoj4dO14Mn/XxxrH3iWr98BvBVgVSVZvWo7pC+F6v1ptjp5OxXaypE8P9nL0YF2la1k3su9zdMJ8PrqW8X5IxGmq'
        b'o/rrFtN3HuGIpq9vyX9CiulzEEP/9d1MpUFh8YMLXxJU9Ou4f0T4R5K+SOA5qXdTNL9A78suCbHPRsnO4fvdJ6WOfbRB0bGl/42Rpjem341RF2Cn7hz+N23ZVxYlw/tB'
        b'1gg9FTXd/N75puOo4shPiXCy6olLh05WiMebYwZLzV47TTYjuoJtMoPLZBErnexEzUPS2Ty0jTBKob4PmA3103qPfrIf/YFdpy5MtMk17iZ3+mMeFONeRaCzjDPADgEO'
        b'Q75fPz3p+rCpYerSV68XfXL77Uma3vh+e/K1R7EcaL1+uT6nlzaalt/AsdNL6jlgzNQMje+AkDmACTM9PAgy9TKHslNN68xhmTaxNtqTTfkjnWzG9h4Ext1HlnYQTA9i'
        b'x21wBktmi4dtcBUKxQM3qY943GZLu/gg2dIK5UpswzYzei7DTovMIw2gVsBrQz0ZbyYeG7+NHRf5kI0yGM6JZ0b0xAgzcL+uUyM8uEUObfpShUxN5wDlC1T0vIebMwoP'
        b'cZCHDbiXnd7MddmNrakyirHchCc4OBwOlazoSrwG9XJsJz1pgEexjYOTeAIvsIegFgpnqKjlKBqaMYuDg95W4oWLkLVOTpvBjMhWFzkol3my4zJ7KBumouCL83A/FnGQ'
        b'E7eDnSiNmqPPWvC4U4TTX4ami2eQZqZwmpqESTLQ6oc1HByRwBGxQW/ACagTq4KXMIdVJmkTO8+bgs30eIu0k6Z5xKbBjFEh2JSixEuhPo7Umi8erB2CcsOdeBiaGXQM'
        b'tBI14ZwnUJn0kKeblONJa+AesvtcYTwiG/DKWna+K8UzWqJSNdDM4kVLsdTTL1SfC8dyGba54/VUeqqAZ+C4sScXToQCd84dWy1S6cTCWrywC4slm+M4zpVzxX0zE+49'
        b'ePBAOVDKmEy+nxNhbJe6hEulEdwboAmb/bX5YJaPExRgFZWT8139wu0xmxQi1F6BhUt9fKlIlRfIZKkQWkNZosnqHWPFo9sGOMostrnkPp7CXKtvpUOKymCuweph1P3c'
        b'mg6ks9BhjC1RC1IjOMqGcW6KCbn9sAnscTPQwz3hWCXDgjCTBRbWBtNDoAOuE6ntonfcFsNYKIXSIZuNsFOWbgA5hsHGpCr7sNYNr29XjMSsaS54VAZl8xTQOnMCVlhB'
        b'OZwWUmlQM9ZxdGffi3tNOHcDCTSFQ8sKLJVBNmZCqQPsx+tYCAVhw+J3QQPuGQbXN8DpdXbD4DLkwQFoj92O+yXu9qQg+SOxef7AQKhdwlYQNuDek1jzEwQueeuQiOHS'
        b'FWlcKl1ox8KVqF6ctozPVnO0CllQE96d1vYCXpZH4UEnluTSrT7cIY5bdGtjhANOHc+l0vCOKeaYSStRYcjZ4mksNSYflqzZCEVwjugTJ3l3yMC6aRTVvDgC2vAcHg0f'
        b'jzUrSKn3DAqDjBjIisNqvKK/HjrNt/KDGPUutCVRhhJ1OQPCu5XUx9lPz2IQdbmBRgX5T2YYnjXEy3jNPUzBp7JjsI6JYXQEkJ0DC3ydyGpB+neIDC8aSN2WLUulXAt4'
        b'lGjKzf5ahl4d9Lx4BPf1oujNURjHwz4sTaWqVTIeG6Q9onaFClLdhx5RT4sjxWMzOxMujab6AaXm4TkBCvh5cdDItF5stktx9CFJ5QWK08DVz9c5RPQL6eXwMMeWDGSi'
        b'PibTdWBRiPMSgdsaZrYVGlamUiPYCmhbJfoF+C5We4moVU+fgGBWWZfFBmnYvtjHLzDIyTmIJB9mSYmNuzkksCUa80IGQB0Zk5VsDLw5WUI1afNSkwjj2KlhZHNlqwqe'
        b'S8A9/i7O4hmSAZkgpdgkkOHUbpG6mF7fJ2BTaLAiEPIjfSl0ffhS6v3Sy/WFrN9kKdlDercI81bZEi34CtT6jIKbPqM84aKU6KW41wIqiGzQLHo/VOCZxWQBbTUzNMAW'
        b'Myidia0pm1N5zlIlCTbA84z5eO1kOBkK7UQ4IEuXhCx350hpt2JWKt2/t+EJP3+FMxmtmUwlDyIls+8VocCttjWAjEWYz7pvYZJeKOSHYT4lI9LzxJsOPByVOYvbT/5q'
        b'zJCnmWK5A08yOkJWFT3cJ24Y1XAkGnMDyPdRcHwKhwVDtzNfBNi/ACvUfj03ScPTIzr5CgEvLMUK5kYikNneToZZPZSKR8riebJhBFMLly+FOnoui8Wx4tEsnCGNM4Tt'
        b'Epk8mQRVKn8RsH8ED6cmQz1jViLj9hzkq/1GoB5OK+CMlDM2lwyaA3tT6UGmA16FMjq+ywwVzAZAwfrpySpNaxzs0Yu1wRqRpekMueugfzcwstR1WC6QAXAVD7MaLEZ6'
        b'5sumBtl36amfcZzEbCxUsZZZhsVO/nIo0FIWnPBYyjpuxRyyjuY6B2FhgDtc5DnZamEQaaJ8samr4cpuzPUOYifB0kk8NEbDPtGl6QRZLkv9cc98kQibVLxmGxSz5oLy'
        b'YS6YuwvL1RzZPJxNWiwKKHuwaggppIenuBLmB9MprMeNgmI9w8WYwRyRbPAYk2GZKg/Zdnqkxn2bJwj26uOh3YGsNGSlg2xHF18nBVmFDHGP+1QB6mz9xZLm7EjD1kiy'
        b'ppDtvFWfE/A87xwRHz/8u02CqpIIEV8tetM79PnEge6WbTMKA8ZVjHlxY9GNtZ0nZ28d3NzwVPu09qaOMLfDpzaEpMb4Zw3464unBoWkN1UcXjb6xp6JI58Y3DjylcK7'
        b'W4pyXpzxr++uPv3WW5PMLA77F9UaxUg7so9+WVzzl2yf7U+bXp3uc+fGMx+O9606XL41Ozjj15c32Odl/P7ghVf9po0e/7e4yRct7f72RsGRb995K8dhdOmNV0z1Rt/D'
        b'y2eOVzhud7J/4UOfWv27G7988edR230PPdvp9+Nc6zK7r+D59ZPNFA5jJjbVPL3pq5iiXw8fKzj0t9e/Lt0o1Neuid2yNXpGiMT7+QsvTJTbfG+Xbhp++q9Jdz6+kqL8'
        b'q+eng/28f10wdLe1yvuXisodeu+1/3rl1o3w+vemTpqZevq7ZYufvnf75Zq5H+bPtTr3rrty4xLDyp/TF3/meu8HvwftP9bNvPLe3feLztYPeeXNT34d+e2+oWb1Xibx'
        b'34WdvCX/1n/syLqybzJthk8Ojt5mmFhR8/NnMt8vcgNWtnaU51vondvsubwpyv72JaVRooWd6g1l653mp//WOW/jgZKMeR8av3r20MqKF9/7+OBHBUvih5uuvj0l/LVk'
        b'myM5kY1v/2PmBwvqPS+sUG63+XjGDx/4DV2W9s/PrwQfi2nz/zbnq43ve3Warc9t/8r/rtXwfwZ6L22aOaX5ky25Ky6+GDzlqV+Pew/MG6YqHPX+unFXM4eXfbptlOdb'
        b'0o+WJ+UljB3pW+6w/fVPcxonpzV/omwRFrSo7GcZXGt0/KQosTl3y7tLpJ1R2yWd8lV6f5dc4NP3fPHEL1+OmvnKzF93r7/z26g0r/uGJXdHKrOu5FpP2lOYsude+RdZ'
        b'wSmDvlMszHr5uZsxf6t67e9XpxePk7ZW+A+/+9tbKSa/3X/eT//TNa4qp+Kk+Dz52AMXlp83XWP0bv2OlUu//Ntn37Y13HigP+w7s9sRloqxotNJO+PwUjteQIF9l+MF'
        b'XJExeiuoGDzUP9g5FvaLbjLYtosxuDuFYBVdu8xgv7h24YWxoqfGZSzF+p4M64OIhHqSOugsgUbmmYDtYeM0Xm16ZMvJwgJoE9KwOIj5tOARCZaI66r+qq5VddIgxiqS'
        b'Onk4KfZ17LGkTsHjolfEcZu1ou9QENzAq13OQ5gFB0Res4yVcNmRlQ/PBImUJAEOLF9TOIAHHR1cFJjjxHGGgtVyMt+xCItZvh5zjBwpE162E5YB2f1lUCA4p8AJsUa5'
        b'eBzLutHIGKcwGpnpu5lvCWbA3vHU34PcV+sFhcFdgrCMG+kvJQtN3maWixW2wVVHVgQ858eRXM4Jnrh/Liu7P5ZOYd5DG/GG2oFIhfUpFDMsUAhVQb7BZhNsUVG3vgW7'
        b'u7n0aPx5sE0GN9bPFz2WD5COatAaO+FYnGj9tfCVQHUUnmAjJG5Umr/G6BxBme2pF9EAzJRAXjSeYb47ZAktWw2U8d7VmdEX6hvCJc4sWLJ+kCB2SWWE3DHYiSg1ucFk'
        b'dJAbODkpPpH7qqFSdP8pwcuMg0ctgswkA5NKIETKusFG29jFZKdMxbNd+8xyK+aaMprc2ax2JiNK16Hu7mR4ZRFr0QTsIBur6IkDncNFZxwfLGVuIluIMFkjmi/IeMl7'
        b'qGvJaKxlpvOYQNzfzaNpOJU0upya8DocFpmDGqFgBZCxeE30senrYeMZKPrpnPPAatLlfmqCnqFLOTPcI0nyXCw2cN3OoUSgJg3ni+exiDaBPFEgu9lJaBJ5g4qgmpQG'
        b'byi7dkbswL1syEBBItndcncpuokSC0Ywl67QeTvUYsQ2TitEuEwVKfLabPECkSHIdlzWjxABmSNEr/Vy3zWkfN0dmQbbSfGg1ILoS1XMQoptgcMfye/H2k1rITocIJY/'
        b'CwqgyT/ANw1PkCUohHcg4+I4u5TqtbCLYW8EufGssFVurDD+d3xwFDb/RSjaf8Mj6LZZL9RNZgOTUvNhbxuYh0wwYNQx5oy1SMYLD2iAmegDROHrTJmn0GDKakS+EciP'
        b'9IGBhMaqkzsllAGJ0s6IfEfir/iZPkvTsBAo5Z8pZf2QWEgGq+8yYn8tBAopbiyIPkqm4icJ80MSBGpLeyAVhN+lEuE3mVT4VaYn/CKTCfdl+sLPMgPhntRQ+MnSSNgj'
        b'/EsqF36UGQs/SE2E76Wmwj+lZsJ3UnPhW4MBwjdSC+nXxoNl6uA5Y0bh18Mm16upREui6LgkOhWxmLOJ9GUq81mK2dLl39AVxtV11jHof9bjCoNuJVyoKaHykLZQE7W+'
        b'T8x8WUg+OvRnvpz7ii62w4c1lYJnsWxBf3D6Ss9feYY+/Hinr+sVkn+8I+jwV5gTm0IZDSMTEhjGajfOYFLAeFqyyIQe0KsibFd0tIhLGGmbGJPeJ1HRC8Y+ImLRphTf'
        b'xNiICNt1CUlRGxUuaphcjQdEqiomNjWBuiFsTUq1TY8UaRaj4ykzYl8+4+6FiE9kN8YyNAF1AGmMSowqFbESbSnqk218tOrRSQwpCIKXrS/zRCAjUhVPoWhJPtQrIdI2'
        b'KlWVkrRJTFZbNd/oiAgFBc3p13mDtI+mPejb+ETbtMkulDJ7LmnGdNqYKesjU7Sl7fIP0Zmium4MH5c5OoleGCQBipbbo4k08blxyqTUZAampzNFUvWU+KjUhEil6Gei'
        b'5rkXsR1UtvY0Pt6JNAHJlkGvbE0mH2NSolwUrBP68TOhDZoSo+kXdb8zP7TE3myV6t6PTmLRwckUWVlXmj064A/YHnlOF9ujURDTkJOJkr7HH3MXQGZXlMtBuCGa3amY'
        b'MQEzsKJnOIQHnumKiJi4KZVCSo72xatqS6StgYSaO69tdsMS6xE+A8du3okXQ+AAnJ8HJSvn+qYQuYAIDQYzgpyGYyWexMr50DEyaPI2OGPuhmU2zEr01Txf7hC3ZYVx'
        b'RIRRmNE8LpWKA3gGKkZjLpFyoGB7KOXrLaShNTRoSZ+z2yDFs3AVmtjzb6UTiZ7ziZfMjjDuSHfn4mWrX9VTpZIr4+4vHvvcNNN9buber06O+v6r4iI927rYUU57Pg4P'
        b'Gjg1y2HCbPd3DlwPPfTphYIL8bMtjCZ+YXRt5OCnXpqwfscLBb87PHjK5ZjVjeNX5YfCovd7hA/dbbUuqewbeP+rqFlvOX3z/fd2AfW3Xh996ZzM/vQRq1dtxq+osv56'
        b'qZtCzoRQe6yM03qY50IeXtBqOp3jRSf2SmO45I/V2KEJCVgPe5nnMrZA6co+4os7XnvYCZcEKpiYvRCbrFXUKutsr7FJDcBDFnBMAk1EJ9nHJMDRUDS4uz7URpSARiEt'
        b'hVymgo4Vls92dMYDU7u53if7i6U+sQU6MXeLUut6Pw8PMOlOPmwUeaYI9nQLNijCEiZSeq2ZrNbQQjGrewSFLWQzuXoqXNLrJuKODuou4a4bwuTbibvhvMZ/vJdsi1fW'
        b'0iGZoac+v/tDLxJDGvzHpimTayhpYW+5hkg2UxiRsCBlUoSphHk58xa9vQe0SWkcWLRQGw/xXlAI4h1dO2sR+VgjVVMe9d5Zub0Wug55+ykIdSMlm8xassv0wErQhMv2'
        b'54AoyZI8UrAs3VbvSXVsq6ExiWoA1Z7o7KkqcZuNYQsdWZW95/rOC+2GuN7f3hSzLj5KtTYqIZ6kIpLsaiCnYimEZNR6F3aHizd9ncdu6w/IvVuq6rbxYi6LTlqfRQo4'
        b'rIphxUxSRtMvyKqvc1VWA9P3WwaXBeEBEQx0LjU5ISkyWlN7TYPoTJSimmpB5OiGofbmVaXGp4jw8NpC6d4r/rBU8+aFRTj92UfD//Sjvov+7KNzlq3407nOn//nH537'
        b'Zx9d5u3x5x/1jLDtR6J6hIcn9OM16hsrMtaI8k1MtJOtg3r4O/RwPe3pG8v85HQLJP15vC5QRjLs7q4x/DjOrUupCCuuCmmeLm49ZgtzyhURc8XpRDJMi4/8cy01Nyxc'
        b'RxG6SLjpGiOWQ5xu8dF/IHVJuW7csVqpa6DIsX1eSY/yp/gY20Y4vbp7EsfO/fWhJFklJ5sFVhuP5aACLsWIQcAVcAiOYqubmxu0e+lxgi+N5O7ABnaKgZfgDF7fYuwY'
        b'5EJPAo/w/uRiBUuQ7LPN07dHOQb5CeRKBj/F2p09MmEL1MBxrHQM8qWPZPHTsQOuKaTs4tpAT3Ychi0qOKrHSaz5GdBpxwqCpdFYTy42peBlqCBCn4Cl/Kgh0CESf1fi'
        b'oaF4c5HKg2x4fBK1wF5IEc8orsckqbDdTAkNUEfKj6d5h81Ywk74/eYQUadYQuSTo/SEfzq2s8QGwXUztefCIW+8wUEeFM5TCGJyGdIAdRGVkCsWEauTWRGn49kh6hJG'
        b'QrG6hFiudoDclZTAyrFkoLoUeEB9ZfIMc6iHkm5l74QKhUQMPz+sB+fVGeJFPKjOMQsrWYO5L0xW5+jJqzOMhlKW6ojF2CRPM1ThTdwj5SSGvCten8ceGuqPLXITpRk2'
        b'QAnHSZz4WaQfC9hDnlCD+STFS3LTxaN4TmLMz0oPSl1GC3IwBur9qbQbyrx96akxEX85PAVFO4h4nYf7oRNKoDKMfCjBTqzFItIrJdBpoYel+rh3nZ4Jlq4LhAOYN912'
        b'IJEQLcygIYGP/zocedU/SA7PHvxp9cv+G2G2uf63Fe/c89nhfWDuTR/JX4JfOXu9PcN46nzDK2+vuXb1ksG7xXFP4sfH/jXytXmHrr/w+8d/2eLSsKk1YuxHxdNDvNeU'
        b'zHzmdEFY2j8d1yR83Gg+cVqUZ/63226/9eREo1uqAW+sao76pRZfwZvfTBlSvsV031GHDxTGx6eEPn/0uU3T3rjw3OT57qcCPecVB7e4NuTNeKvz9LH8QzsPjB0+DP8e'
        b'WfPmc58cC3pl5+wJ7ds/HPfgR8vTx19SeN2MaC14MWL8sm2XfzQ+9t6m608MPj+87OiksklTF17dWj3y94+nPJB4uS/Z/2OLwlKMzD0GrZDvHxAE5ZCpiWpkxn0sFa21'
        b'sNdvhRiACxciNdZ96DAUTaGXSKNWO/o7w6UFWgdoYyeJ/kw8yo4rNsBVbMZrK7RhvaOsRSviMek4hgqArbv0OCns53HfaA/mgob7oAAbNSG0RCg/KuFYDK23PTsU8CfT'
        b'vEgjnMNNZyafC2mDTZnkngbN9o7U5O/rjJemC5wB5gqwF4/hHlE8v4StG/SmquTYRk+VczlsGDdJrOceKB4O+6EKcpMnUvSGTDLjMGcNk92xPRROjTCml2TkUhZlUs/C'
        b'm+wanEsaTJaRm/QiTTObw6Il0MnqYrM+XR2XKgaleqpYWCqZbbmsOG6L4Rhes1almZIn4TTpDiyYKJ5flE0nfdAC7Soy47NoeQ7R1s7DMjW5/U0ohDI8Th7VI4/Wk1XH'
        b'IIpdip8LDbMxm8xvY6LywgUOj0NZKOuNUKhfylmp0jbT3Mo5zFviKtb9BFkqb66Bq+QSyQqOcKTxL2IuGyKxi2Q99CVsnsRUJqIvbUjuJwDzIb7PUhWRgZlSEa1TqTCP'
        b'oIZOU5EH7AE1gVLDKTVoCr8ZSAXG9tH1Q4mOGSW8YMT3/JESZUQg12UPtg3o6cxM8tegq7DQSePuQrSyuIdewrwTSXWOaHWRYm2EYyl592T/Con5FR0KSX9F4ZmzkfJv'
        b'9P2QXrhWt6Vrg32DbsvXzgsPCfEOmufrHSqigGrxrm7LkyPjEzXhjzQA6bZRt/hAZsDURoR2C97M64mLxWCyqAGT6VqsfmLprP//ZHlXLqaKoEQ9gAw4c30jCYVsk/1m'
        b'KrPSE2YTjfSBIPw5ME5zqbm5qUDJ4QTppAcGWy15g+GWvOjTsB9PTKexCbuhrpvVgeesF0rjp0JhHydfY/VflQffkyuOwnmJUF6VUjWYl/ieQnoZkh/6nkJ7UWAv8fuu'
        b'9+YUTzN6IHtvGT1I+35w9BDy3oq9HxptHT0s2qZSTlnoMmWxfPTw6BH7DSieZ4l+CR8tLzEuMSixoD/RI/P1De0MR0e7Z1K4MBlRdcdEj2XAV/qMwW38fi7aPlpBGero'
        b'syXyEiFWIE8OJL/mJRbx4icLkqJFiWGJUaw02iHakaQ52tAp2oPCkdFUMw0zTTItMi1jDRiAF03dkDnZypjT7YBYWbRrtNt+A4ojKuVWyFmoo+dtCzpZ5jFGCwYBFxuj'
        b'vO/RQ9jse4OahK37TfddiOTqFa9K8lKlRLO/Hm5uHh5eVAD22qKK9qKTx8XNzZ38EtHaUyG5LQ0KDgm8LfXxXehzWxoesnBRI39bmO9NXg1plmuDgwKWN0qV1FZwW48p'
        b'nLcNRejfePJWL5aozarHydadZitVVtEZd4K+VNM5LPUNChURIR8zralkaeuZlvIMSzB0/pI59+euT0lJ9nJ1TU9Pd1HFb3GmqoCSBsM6R6mDCV2ikja5Rse49iqhC1EY'
        b'3DxcSH4KoSv9RoFhkCnjKcwiaaCA4HlzAtYSDeH+OFroeXN9WQnJ30WRW+myF0KNxqoUkqiL2wTyShY/mlgjr1wqIjXW0rIah/oGLQzwXjt3Ttg8n0dMyp2s1FU9qnx/'
        b'cq8H5ymTVKq5THXpmUZAUlygKo6l5E5TErpSIgVsoWmZ9WqP+9b9V+r+IJ2Np5D3SIUON2WbjrSnKi/Tb3slMpUl4qlsp9f6z9z9vuNj1PS2fnRMbGRqQgprftaX//Eo'
        b'CJ1BProiSpgXW9yi7XKsEoUi5vgHnZL41XfSpSzSxGfjTX+PeTTWJECfk9rzim8aHxJpctuAcsCmkEHNZA5dMXEs5GShCN/aczFx0Tzbf7jCDVKLGeSdyl6nEMDtNe7Q'
        b'IQY8LK9GfXHDVunYtVO1WzcdnJ/RsoQF9QlyMNI0LEUVYEEOnIafVARnizXSBjAYPWoAwz8y9HUYNH3F+OL4bTHdzJoiCZF47ESX5IeYMUM1RMG2yYwSgkkwKq++Nzrb'
        b'9po2tvbzvRUPv41Ouz+8Y6qtvYMqnp5hpU12meTwCEmKM9nWfp7PH9+snrH0ZifbP8qn/9XE1t437LGecH/IE4+6MNAkehe6P4ux2uolmofE0G81/ZSG2qC/J+nuKT7W'
        b'e9gkK+OTlPEpW0UcYXsHuidTYi+6KzvoNiI60L2a3kN3TgdqMXagW56DwqXrmHWSi4eLm5f6Ft3JdJ3IurFb1al2fT2JfS0m3V/FRJgKddV0gFCI7TNexXAo+m0edl7h'
        b'1RM7gE0y3ZAS6tj/fsvUhRvhpaWw7QsNQWEatIfyOs7c6T9yjbEQUiM+M54yh4CYyBQ6oFQajrZuSBv0SLofAAJqgCXppEcq1f4D3agxWOvYhsbE0LqmJnSjfdOZ1Lw5'
        b'Yd4Lg0OWr6UcRMGh3msp/UwoK6X27F4ko+u3kcRFSGwfRhelBm7R9JtGe1ObjnUfdXeZk9kRhZhCl7XXodea4tCvswDroWRxnqpEKrteS4yDWDvNLfGJutERRAwOIp9q'
        b'GHnXRybaeoeH9GMWT7QNTY9P2RajTGAdl/KQwosLYj9ziUwY35TIhK3swf5XOIf+x6waPETskC5METry1V2ixRcRT6j6qVGK6PvQDWi8x7M9sGH6XbVYSn2ODEjzqIUo'
        b'lWb49kpXd5+o2R278mWsmutiEpIS42hKf2Bap1KJYR8pykwMI1yDOTFY7I8F03bgIQknYA1vj/meYtxM3kg4RM/dawy1zg7jIU/0daCpyXcsV5msh31aHNMdq1NFqDQP'
        b'PEu1YMjDy+SnFUvwNGRLORPcL2CuwUQWxY9NMtjr3z0obElviNFemJ+BenAUmvwEbiLsM8X9kG2jEJgdezy2QA0zAsM1aDcVzcBwEPaIIQhZY6FWbqKEYwlmovU4FqpT'
        b'F9Er9Ukx3RBeu8qiDZVJNjEJofiu9s5B4fb2mIN5rpjjRJE8RbTSUDjvTI19ZQN5POyxQIyUyIjEelVaUHwXCOkmrGYnGaPjZLGzBSuOs40w/npcPMfwKow8sLo7LqmP'
        b'i18gZsM1bCd1dw3BrIDFPpIQyKbRdHgV6raO5eCmVI7l3nA0fnn6cxLVKZLKV9VJY/ObTTNmGx98d0SyjduxexYvFSTceufF8isTjt5Nsxi3bMy4m0l80obgzEk/32jf'
        b'vV04WRkTaSAYTYn+9pmlL3887ectMff2np6f+GzY6+c9mhdfeAf/suT7w/o5HTdesVt+71jC+o+HjB6raFh963qg3/6bwz57Z8PsrT/eXGM98m5Z9RvPfdeQYuezVBH/'
        b'25FN95evhHdWfd+5LKjY469LziQ/EC595FL9bqHChJkzZ25PcnTBdixyFl0cagW3hAGiT+oVyFoqQilTCGgn6qmhz5mGSKb5uevNZnZdZ7wOLWq77irsDFTbdRNSRZfk'
        b'Ujg6HHKnQJXGZ0TjLzI5lOVtgJeW+QfjAbiiAZBshNOiQTkHm4VunuDUDxxPpyfgWX+WdNAy2NPNPx6rtmu8L3bYMQvocjyzoIcZlxpxTTFrPmbAPuZ6gbX6oX1wCqEC'
        b'OrVYhdY8S8oqBvfSABY1pGTFSC2qZBt2MlvsBDiDGdTgDoXpXe70virWRlPIyG8iGZGptwbq8RK5HMgvgE4Fs/xOIVOxhEx4yIHLAaQR1vHuflDZA5TC6N+yvGlR8Ob2'
        b'o0ZZ7KDWN5mE+rQaUUw8apd7YCBIedHTlOLZmQpSwZp6sz7QrQZ1R7dTbuZ1WZPTeqDMBT5M/Rpx9lHVr8dBnFOjsOmtZWB7/cFh5ZN3It6crgy1DM8ujyD89saKozaq'
        b'UJ85IbellL/1tpRSuSr0dTnTiq6q1HP1tr6a8Vv5F15HaLyZZiNZxGlD40W90VitOZqIwN6ZZrFmjx8A/48GXfrjnOhoVU/Oas3+qcO0p5W8+qqhsbZeVC70itBClUTo'
        b'OL13UssxWogt6iLZ16O0N/+iSD9M1fMu6TSFtmSKWnZ/JK1ILc9qGXr/SDESCbrEZ3XQ6EaqbGMTkiKpxcCW8cWqCTH7c52JTOxBPtebfbe/UvTQFnSR46bEbBFF4RQt'
        b'n+wm0b2zH39Nck98NJXjupqii8JPrIOtPeOVp1VjcppdyAIXFxc7RT8SpugAwXyPI+lo6sYqrU1ZpM0UJd+u6zrT0z7TxYKpHgJq56yenJg607AP8V7gTQ9rvNcGhQfO'
        b'9Q5xstUoJCJxaL8OXczZuH8C2aRk0fn6ISls0aXj9cPU+pDk6D+tCkhb+GEamhb2TT2qdaamoQXXpczZklbxDgmaE9BXcdPtn/yIypyGy0tsCi2hMh2w6nFD5wXRf2MY'
        b'Z3ZERFBSIl0pHuK4vSWlK3dGt0vbKDKBOkvTBUI7dGOVSZtIU0VH9uNhnZAq2szi4tNiEjUjn0zNaOrIYx+VlKiKJ81FUyINF8++Ja3cb8HEZLpbGhTdq6mml163ISYq'
        b'RVwPdOs2ocFTJrm524qEt2J9aBmc1ICh6voy1Z/OTbIo6kwnNlXJ5hqb7SJxbb8KnrgredmGqhUqDd089UHfSnJJSCCTL1IpqlXizbrXFpUqKSqedYJWvUtWJlHWeNqK'
        b'pGnVnU0mgjjsdTdmNzJG2yCi6EUmJyfERzEXQ6pps/nU3ade99yZp2at7yJ/pRu2rT15VTjZ0m3b1j44PERBO4Nu37b2c72D+pmHDt2CBCYpHB4hdEHrrzVHu9T3olJ6'
        b'mB9oDy3TQKeWOTJI9Lo6E4eXbWFfd3KIKHMmCDG1KGeDvjSKE9WiO/P9RaIMOLoccylJxhjIUOuXcAnzF7CLAUQTzNS4PAXDEQo8Uwal7Jo/NkKpGuUFa+yhnIMj2/BU'
        b'GNNNoRXr47vrpkQvxYNQr9ZNg+amBnIUVKaGcUUw1gY4DnvCKMFHmBqowN/ZYYmPk194/4qqiANz0XsA5NrvZk2wGiocsX2F6KkkKqhboCOVUrVCyUgaZqmmiOiWEVyB'
        b'zodk1kWPs9heC2GhkHFebpbYBFdwjwYoqNMLbkIpdaAS1V+4AKdSKY/QpF1EA2cQP85+wVQFFtPRwyI8YDR2KDQadWmds3EvVlLkQQs4ALVhUB29GLLn7iL9kAFnyU8N'
        b'+Xtw4xY4BKfnYoPpujWQM1cZv3jxhjXKsaugYuN6cw4LZthA5QaoZQWz8IHjWIXNcmxPNhY4ATt511gsZkgtU7AGmvstGWYPhezZcHgdHFAXCXNniKU6gKewhJaQunhF'
        b'mGGmLQfnFg+wmqrBF8pKNArCK9TNTHQxC4TOVDqQsWhdktYUoFiihvNJTk0Nw0NESzuZbGKGRWHqlu9mKaAGAto9GsgPDeYN7IUGA5YL0QEHk6FbaZhKuVeneOjpBlxS'
        b'o+TQZ8K6dSdexSIZh22QabIQ64Yz7B7Smx07/LvTJOXDuUVs4JBk/Rn8CBlNxXoqP8ixwNZd7pCDxSFEs87h8eZmk4VcGkOSgWvYhnV9EvLpAtFf0iM9OCCHEsuxeHoQ'
        b'1EPd4EESS7jCQUXgAKgjSm4LA3pZROZNkw6oJAFPYgnJ6NL0cC/SPRm4nzQw87aDonUcZoYYh1hCFpt8nh52mp7AK2aOi30CfBV+zi5aSpNuraUpmUnP2Uka7HiqBRze'
        b'iJ2pS2nnHrTHMxoUCZKe1uLTPWVoDH/ExEP8LKETWxyZEWyiP8/oZkwHqG09xonMTUf0B8leB0ccfdRUO8On9yDbgSZryuYYPy7ymJ6qnGhbm+aeCFx8PfFdN/NxisWX'
        b'nJ8tOH5iku/Tp7b/NHP2T9yafCHzdBM/pNrCdYZzasaqI9Ur7hbabhrxq3TrvqChHrHfHn36mYUL+JZDP/1257uv7SW+3ucDS3Pnhr0w4L2DKycfnFDx5utG9hX1tfZX'
        b'Jz195s1/jhja0O5+buXq8UUvDaqr/HWC41c3i86/9lHWxBj5BzebRw1J/Hxv4PLW5eVepbXPrvjxl182jrPy37nE8aP6hLOfHajhP/+p4PUVD97Iul9Sc8t1/azqQYdT'
        b'37ga/WJ1+OXEn8du89tiVWVUFfnDMmtniwf6W1zvfjTm/q1v/9b84+S7418te+H7z03X39z+zSbrj77ZaxRSdjvpnYNWP7b/LWHY3b8mTTnf/syMT5XylrJnPmh60eLr'
        b'7esz58yLm7YlfbN+9nt/Wfpg3ozPt1nd16+s+XzAncwLKyJOvD/jTNrdWWk7Lr5T88GSX+KaU9snpITEDYna2zLpxfnfji7yD77//pSNq796quXYV+lb68//Xv/bfueX'
        b'ft2k2ns45OCLc3LP406r+/XBjnofTQjwdPwg5eILnzTlL3/y64AfL67hjlTUzt/urRgswt5dxCNmahMRl6YxEiVgBx5hJiIbrDZg0Upw0bOH8QkbpSIsQ6sJNlInR49Y'
        b'ZnyaC4Wi7akigKcj/hQ09fCunAZlogMl3aYOwHlo1pCciPYezINqkQLhMNbTgHjGnAL7wnuQp5D8M0Q3zutkBtYxnIVt2ObajaNloTrsCVrhFOarzVxkl7jePcpoI9SL'
        b'zXBZDyp7xj3lQ5WQloQnmG0qAMonQz6cdxTZPES3zV1QJRKfnLDFmxugnOLi+sI5KSdLEOzI5MhkDeQYHscoT5ZjgwhPsXe12ACVMnOtbS22i7kD9uNFhtSwDorwovoO'
        b'rPfURQNywUJshIteUMsC6M9gM11gNSH0ZAU7zsqP52InkKQOkpucKM+c1ImHaxaQJ8Ii5EHGFtE2ZzOqO+ELZkExMzHiWSt3Q7zu6NJl3hwVljKe7fNwkaxsvpDdLfyM'
        b'usmKHrFucEXmiiXmIrpAFVn8OtloIrvLKLdgIk+YzpfMGGgtYm3kUBDbSjzYg9glEfYz4AU8b7ljxDzIdQ10VpAizBBsozcqDB45mNnsv+ORV6jBgCyh8qIOuyC322im'
        b'MW8qmAumvDH5lQnm5NdAYsEbm1NHT9kDI4mUxbUb8MIeI4G+p/Hqgvp7FkEvWEpYpDv5NRdk6kh4GnNmrEej0CwE0fZoSi19D4xpVL1AY9LptW12OgxwjxmV3mVIUz7T'
        b'M3bt0du/ezD5MzoiynUEkx/S08Tf6bBucnvtP9Fh33yE2vbv4kO3emb2E51FuFiZ1tlH8kjOPnEKyf2IPipFSEwi0WZVf2TbY4YEtfJCVddIle2ywIA/0FAobuKIPhqK'
        b'UxATy6I98Ya/6LAJx0xEHspeOHW5S+37RI1iJZw3GRQ3mKkWfhzmavd6stPnbuvOrNcBmaIuVDZ0exc/3ZixWEjE/OPiudm5Wbb0UooLWXVdtkNVGvnrR4Mzx6zRm4wH'
        b'l7DjLIc4uEkzIAmM4PBEPBxKhgYWneyLjWbsME99lLcLW3h7PD5D5BYcKnANq6i/aYSxDbmdPYHtWDHck8JSckTFqiI7UAORLl3E472Bxvo01oRzJUU8RV6zoYTJ0HJ3'
        b'yJMbKimyWyOHLRPxfKSdOtSEKEtZjgoHClmyFU558LgXbg5k1fYbJPWn+wrF7hkMjasFyqkn6muhUIJVcBqbQjFfSkFMOCicjxWsgAYxsC9UiyPnhtdII5Els1M82Gu0'
        b'WK7RaqB9Cj+LbJMVLLeZcwLVUSYsxsRyJT8KG1LE9r+aEqEOT6GhKXNt+RlyOM2ia4J9N8sZj6OEs3XgHXg8JUYU1ZLine/S3EhxG4gSVSWk0qDbiVg9KhTysSScrNil'
        b'FKPOIJgMi1M8XiIiXgNr+9pJBZzNiikC5xaRqHQLEZXesrmjObeQQtoh65aEWotfbt3gy325xJbnIiKMrqy04/pwNGtnIN2vGUeznMw5rprbwUdz0fwBYSh3UsPWTMnC'
        b'P6MHAZT3Zk60MiA+MaZRzdcsTSAfehNOU+v+ahnHfS+wucKOaQfiGdjP4NZpHPleG8x2MtTIwljEoij4kElTiZ6SDdlT8UDa7AWxm32VuxJh73Buh4c5NE92Z1X7NM2E'
        b'mzB3ElERIoxfWj1drK80YAiXMmEF1fyn744fxrF5sFhBRBU1yOAJKMQWs24og3ASy9WhXIFY1KU8Qqsf0eZ2ipduStzIlc0mRFKyhLN4mp+GlRtZhtVu+lz57GE0wwAL'
        b'6wROjQOPV2biDe1YOu9DxlIjNomj7FIo1mgURsiBY7yrzXB2ZStSyL1W8pg+Jxk3QsnPgLqRCl48BL5CqStVQVRKFOQ8FCtt4bTHv9Wd60l3Kp+ni/8L9OUlnuvDGE47'
        b'8DzpQOUr5KKaQ3GziTwN280EUvoNcJafsimIFV6FJcpgOC2nygqeo8iOp6CdzccJcMwFW42xXZ/MuWJuPmbiOW/MZMCz2/HqCDntIjwazC1WYhmbpbFkeuTJ7R0csTmA'
        b'58whw8BPWIF5Q9n0cVqTiq2ufkhPG/VgH5FA83gik2aax195eRCvmkqmvMuGyTHh/nmW4ZY7vwl/0FHfEVkdt83KauZXL+xZayWb/92sz+8Nnf+k2TMNzwy6lBUaODEy'
        b'cs2mLxcb1ZzOy75W4zDu6wnfFVulPhkU9X6GyXaTxJSN61Zd+fbOyjdiZYMvf3FH9XXHN+nffOE2ZPD9a0u9zvr89OMxL6crXpOiLYY3GE97QjJTP+Hcv7zen1YSvOd8'
        b'Y+MTJwXVJ2F78hJfejdG9feg6umXpg/aN7eh8fW35rhPiHD/RC+m7ab56VbLxsr1Du2D7PzaLUvKzpzM8W9SnrL4xzKT577LiowM8o79bsOi5tIrRQ3VG+Tt15bqHWgN'
        b'd2vb7/l6wqtvPjFo09QRcwu8zkU6Jnq+Ontjg917beVb3/4mtK0joG3+ytWhf//l7luvHjrfHnZrh3HsjDc2BZbv+OZU+MQ3Op6Z9v2uzDeLGpLuFi764JKk9v3F3x2t'
        b'z38waGLH2tesh/48b3BU54kBrx3MN7F6sHBDyu5TbdlBl5Ix61pGlomNN77w/PSlJws+WPqXYa3ffXBu7NQtx859/lv88Aeudw2/TFN1Hniz+fZvcXX6qY4Jw26l3RkW'
        b'faNg2tD4b7i3FWf33Np/bHDt+181Lsx582bM7R1GNqripmnSxnu3Xp8XsNH7hZn28XdeXLQgRO+O82eVNuEfXDnw/ee1pxdvcC2bfzXV9HL5hwP3vf1uxLTIjvkVQyul'
        b'C45zHcO+dJpScEfy7sbU2t8m70nM/Mr/6VesNvl8ElSdNmvAv0yf2vnE2R/em/PhccX4bdLdD55Y6wAduW/N/sz3+19/9vlpXdWzv4x47m/7Vs6/4Do16hu5Y/kku3fT'
        b'bb7a7X9MuvTO9kMnc3JGtAwKa1ljnLGtvDX1p7/fOG347OaK61Hj1ktfrLNrrH7yRtju10x9Z7yn3zHyX1zJ1Kmv6u8dAca7v3X46MsHsu/ddp98yfNWp6nlB181f+r7'
        b'++m/KQxSpzdE3Ktx3DjFY1fu0cOfFSQPv3jmzoufuN0+EW28M6c9+sdpBTatb73RsG+g5993nH75+cq3biX/vnDuRzNzBs36eKbLzdZLP84YXZ94beGHX+enV748/HPh'
        b'3rXt3AtfRFTdvRa7NrHx6xFPOQ/7ZnVTsN+miOiXV3z5ytqPpwWPTv7k9PMTm3bfjftii8PzaYc65t8ofuZfK98ce+uXVVfiF9wZ23j5jH9euu/bw/Ou+IckhZdZfTPk'
        b'a4vFFz4rSnnpnH/eT2dTnp1EPi9Je/bknLIsj+I3FB+g1c+uJfUP3nvxHwHbxymn74o88dGwiFnv/qRqHzD198Tq0U01TZ9EPv3h2M+feVv2u2HyOKv3+A6f4uX6NyKG'
        b'5SUMNLr4sfe70bOU1+7ku2bXD+xssx607eO/VtRsOVE4MP3t55sGNghFgzotvH77wfies8ulkBcuJrvj+Ivbn4xNThu4I+3boJMuw7/xPHb22ckzhn28dGH7oMCTN4Y/'
        b'2HT0lvXLr/1rzsWakOEP5mXvGvTcwow1H5Tp/zxz+LezO7dn/vT25F+fv3wyvPzyvfrXnjuybvLizLCfX9/90UvThmw5oNjI9F9oMN7cjTwFrm5WK64ie0rYJKY0WcTj'
        b'sS691cmAeY6QrbqN6ZjpI6DL6SIIOrqoPNtGMr1XNX2ZP9nstDSfZm5EKKyTxIXAHnZ9nMOA3v4fuAdPS+YvUTKOFyibv7uH+0ckHuqhog4yZF4wW/AaiwdU82VSHnIN'
        b'Z2YkljLtcAzuG6lGNWSIhtAABwSiCWIVq4rRtI2q7sFHJngzADMls7EYM5gnSshYKFW5kLydlUEKupu3Mn8bzJZwE/BsOicLHWYr6pkNsBcq/TVWCdnazXBNcJiLp8U4'
        b'yWxsH+cf4CDjhNVEmMXGyWMgk+nQTmZK0heuRHim5StMwRZhLDQS0YsJnRV43FWLAbcdywwoBtwS0Y0GW7AID8sxy5mo53n+Eg6Pe+jjJSEYb8BVZqQYjyd9tNexlewq'
        b'JpCFbXiYCAHU9iLGWxbgBVK8XDVY7VJbnmR/cKjoJVSPHdghJuHsy1NMxUsGRsJSLIUDYhnOJtuoHCj7JgsvLZw2M0if7GpNkhSom8uSX+MEHf4MQ4Xj9PA6ZEOGINko'
        b'hqZCVTTUYas/tgTLR3lDoz1Fob0sQJ1xvGjt6fCPU1GoSMMxi0kX6XFGWCBgLhEhy0UvqCNEBzlEi2eowCbWBibQOQMOSwbCBYXYgqeIznChy8CyUcnjPrxqy6q3AE94'
        b'0Q51dFEY2TvA/lhqxLCwkuAed1P2dHoEVspd/LFdgbk8NxdOGpgKKzE3jplgkuEMn+ytCuJFqaDBEU6LJqZDYXAKW0mNabtTqMvjcABz9LgBgyVQAYc3MASaOTPS/Rnd'
        b'KB5N1jKODoMMKZyGo3BWJHzFwyqViy9cNCZ3cJypjEhRByWzbGAfa/xllnBZ7uccsBmOE3H+vA8ZpSoFzw0Nky4cH8HMG8lEzzg0D/Lp1xyNdr8aFMZSjiZqVrk/hbwO'
        b'ZpiTplCyMlAyHc7NYIM5dPG4bniNFK1xHJ6RJEUOYH5RtngYm1W+DgoiKEGJcjQP+e5YJ4KPlo2YsgPaKauUHsfLOeiEc9AgdmblFtQSzMPVLtvdlAWsrXfDEagSma8p'
        b'jKMnNvJwCmrXs/IOxHpf9dzCo+O6LFHlEnbZC48SRcueNMBmO/cAUi4jPCpARyC0iEM8B3JH0QoFOvNcPF4xdBeg3HaNGBh8ArN2y10UDhTVXY+oeXKDeCGejGW1QfHg'
        b'ZG9H0jkuviLkshnkw0nolKybgyfEmb1PEUFy3hxERbb6FUN5PCF1U/vJ+WKuXEGSYq2hh+V4YwZPpl+2GAQ9Cs4Gd1nO5uMeHq5B1SjWAdNmwkEy8mk9JaQTTsBlnkIr'
        b'QDFrZaLi+VN7vAWednaRcXI/AetXeYrjfb8HnKd9owyguA0mrnh2osRAFcXKOn/jACynIdsBdDhc4eAClM0SuxTOJRDNQUld4AQyNurG8cOiZrEUhcVkmnUZUxclUHNq'
        b'LdSJJrwjeCxdK7r7Q4Et1G1gtadEvRU9vQSdnSQJeB6Os3afRN1QWUHxGDQEuPKc0WyBrDynp7ItwA4y8ISKwveKE5T0LLSygluStRfL4NoKNtmEzQkqLFAYkao0Y7ET'
        b'0dLJSt5CbhtqLnXAw2qzMBST5a6KpKS+qLdkErTxmANlWCmO21zMstZySEMOHnTdSHYAtrBfISs5PaZJw1bSUQMwCzL5NYZ4gXXieLiQpmJg9DxUkeE/hejqLSjilgqD'
        b'6ExwxWx7MlGwKhBPknugzl5c+85AIRSSstv7pTsIpABQrg/FwlRnMmbp+gBHiCrdQp1dg6lhJZsNEzMBasZIondiLstA4jpahC7fDtUa6HI4TapEW8YIDkKLim5acAIP'
        b'+clJ24pLpBWclbpj1QyxGEXYBkfFFZ5pHcdWwVEyhjFvsgihXIPX8Lx6kZwSzlrPCNvoGCmGWnEGZOEpCd2GqY/kEh4OpztPsRJXwvNJWKYi/W+I2enkD5Y6sFwGYrEE'
        b'TqwmU4wuUtsFaPBXw6FjZwQZ6DbJLOEU7BjcZZr1wQ7B1smAXVkDVS7yVBND0q6jyGp5kJ9jju3syhSoJfpaHvVZteSd4NhoUulytlpOWJ8mVsN3M7tugo1wEeokY/Em'
        b'WbzoKDHHs+O7YcXD5ZkGDCwe9uKpFAWt6eWh9OwgmPKZ5AQ6KXwDyfrNjgD0uCnT6VmdjKz8dVDNmnbMBjJN1GZp0ShNNoL9khnD8KRIgFdHxC+GmayGbO8N2E6mQA1b'
        b'DcPxgoEr5i1Sl/KEhZzd6bzZ18F4i4LiAV+S0OVhO5tZErwpZcTaXazacDZREmi7UbSXZ1lhDRkXCmUonmTzzluAM0QGaGYzYYQ9ZNKrdG0/EoJ7eShwJ5foTBiKZeon'
        b'xbVlIjSFSgxdsVBE1C2EEqljH8x5Iow0axB1vWGvOKgOwgU/TR2CFHAJDrJatEug1sSEiS56cMbIUcP8kY+V0u6Q91CazCZfxBhPOdsZJXgZ2uACT+TIetjPqhkHh/Xl'
        b'mKORjeAwlhiQtQzaPMRZnYsXcB9Z9/148vSlqZhN5iZZnC6ysTIRr6fTihr5BWLrDEOWgiXpO3p0MUs8OLjgHQUnoFROxgVvTQSjeZDNumcCEYTOq4Kw2ZWIFIqwVLqE'
        b'm2+QkCXl6AY2aY0Hw0VsdXJxoYtCBWbCYbrP7QtkycIx5SY5nQqCgsdCqxG4B26w9vB0g1oVWfMxewq2G3bVywoPSb2wJl5EASmGSrwsd2a1ko2AwiHCwElyVt/ZvkGM'
        b'OSfI2YGn0mi9AZ3ER9JnsMYiOxeWqFwdsMmHdEQs7teHToEebrezdh5rHYCtzkGiXWInkTqLeCw12cTquwprYrrQkaeMF/GRKTrypkgR+y9tvcrFL1UB17GGrANEiBME'
        b'KCFS2VXW1KroBWqZ2tfMnq5xJnh1MmnqqXTgiGAhNzHTQ3TSFj20l8XwCxzsxG64Nhnr/V0CybK9lZ8NNdOhxYhdGAENzmRzFd22U9a7QykeFvf7/QZwUo1oInArLNSA'
        b'JschTzHgv4N4K/uD62qsChZdK1Mysz47/FmhA/xY82PgYMDggSnMMYUIlDKoQClZ8+jxjIwBHlOHcfFQh14zIHfRH0tyjzkvPKDAxsIDKwMbXvje2MycIX8Iv0ul9KBn'
        b'DD9GsCZPkmv3yXcmlHqdPiH8KpVJyVWZMO6BsMeUF34THpgbjKDp/S573miauUDp2ikUMgVENuetyB02MnPekqKOSGxofhLhZwtDc/aZfmtlYkWhnHl78p58p9d/7sID'
        b'Gz0rnqbLkEwYmLMlKZGBTPjZ1FD2LwO58IPRX4R7RqFGDDSZwiYb87bkdRxP8yZl+Z2WV/hN9ouBpQG/baiOQx2x9bsRDf5B33ULXH6V9JaNjHQbBavXfbbE7R18W8fp'
        b'Uv8FIdmzoPkneBqXHBSkkJIX5m3eaNwL1ESZwLHg7NB5Pt6B3qEMxoQFU4uoJiotFAktp5KCHIvnc5b/E7CRadpmOkYHNT2CO8hRTzipIMgEEaL7V0H/P/dO9oIw2ZQ3'
        b'MDNg4CUCb/lAmCFCklhJTel9vwsSgR/xgNs9wogBwEI11MJFjfG+u+Ve4KavcLGVEWGxYFufmHsj9V+VxcNBSSTRBur3ht3eG5H38mhj9t6EvDdVf2/W7b0aoKTSUAs+'
        b'Yhk9qBv4iKQb+MjgfH3DoYbW0eO04CPDom204CMUtISLHhlt+xjgI6PyZYbWJMXxWugRk1i9aLvo0TpBRyjUSU/QEfvbZgyhh5Fpz49ZF59y37UP4ki3q/8G3MgUMZDd'
        b'QyHcls4LDvG+LZnrMVd5kg73GvpSxz867scUMRLT47HAQtQPTXl8QBBNdizw050CgigviIE6FLpDeZEBEIV4BwaHeTMgkDG9QDhC588PidncM9zcTdlMK/wot7pr0TI0'
        b'Bblv1V+qWgiNnmVWGPZIg/aD8r3uOByaxlH+g9boLr3UXx7uyuv0nv8xekZfilw9EcjaJwBqVEQ+ukYB/jTwfnvwooiEeHHhYjnF/5LMYjBmlVs3xwd/PUeqourPs4c/'
        b'p4zoPpEvxDqsC440iv10p4r7Z8bQKa9xU82lZ/c3KHims7hixWxHc9fuTkCGo/qhB72hcQ2hCNr9SQfMQcSWEh1ss+o1wR4RgsOCtLHK7SE7GYPieF/HbtZ/hjdph75F'
        b'cTaoYfV/hrMxSvaoOBvRrNQUSID6+P8nQTY0c+IPQDY0c+oP75jyyCAbPadpfyAb/c32h6Be6Jy5uu9/DJCL3tFcYuBBZCKNGaBBWf2EGGkf04We2gcYo0c/q8Ew6I4h'
        b'AlyQXcOh/2igP0Kh0JTkcXAo4mP/D4Li/x0ICs2M04HAQP89ChBEz0n7iEAQOifw/8FA/AkYCPqvb4COXlAYwyDwwc61fTEIKP4AFmF+gIFMzeHbZX+Dm5gpxzqsXhWf'
        b'UR+qp6KBCdlxnY6Rn0Z8end97Ion7n399pOvP/nOk28+eefJvz759yevHTp+eNSB5n2jqxr3KXKvLju1f+yBxormbPcDoxh1+Z4kk6kfFSn0RNP1dbiIGaIT7cJY0Y02'
        b'aBGzs3nYQ1kfkADMjDcNkbjb2ImmuBI4g+d7nMbCXmxjPsNL3JkpJd1tsMaSAg1YyLvDfgkzUeNlbMAmuT+UDunJhpcpNcACrQPofyRCXjdjQrdI+QWityr1Y5U+0CGF'
        b'PHYYvNWjiEAj7jySCPQ4sfCxCj5ICbxGJNMRBz+XlEyMg++TkzYI3q6fja5P4Lvs4b65Ufq9JoVcMzF8qJCm30tMk1NBLVauFtP0mZhmQMQ0fSamGTDRTH+XQWi392p+'
        b'h526xLSHh7N31xv/n4hl7wnxpZZ91AHem8huQSNt/y+8/f/C223/L7z9/8Lb/zi83alfCSmB7ALdic0eK9r9IUvG/zLa/b8aoy3RKQJaiBYhLIHmnTRAmwh2hzVB2omQ'
        b'JcJ9Ucs71pjaiT4ToT6YHayB6/Lxw3zGKbaUAmXRKFQpZM+g/Ka5hnANi+CySB1/eTlc7wq8No1kodfqsOslcJw5JYeuhUM05JvGe8MZOQ35PjM01ZNcsYB9kdpjbN1Q'
        b'XR54hT4KxXjCEDtnhjC++WkD4FwXxBdm+TiJsRyYxbhZnXz14Cac49aON5gza2gqFUSgjXoC+fcUgFlsrBMWBIo+XyFyfbiCbZgf6Zs6hzbNBT/IYHSvy7GMphq+aKnz'
        b'kqU0yNcvMAAaw3zgvE+gi7NvIEnIVYAWuQfkhoRyI6DSNIGkdFK0ux2ZATfUpBrLh5AWUy1PdSffr7N0VFPJktzP4XExcRq0muyhpGGqLHJcykVArj6UJuFBRp2+Dq7o'
        b'hWpuVHdVmPhAII24c2G151bG6kPd6s2s+aMnwkm50tSEHuKegbMD+BnpWCb6x1+GfBpFdzldJeGEbSvwJu8Ymcg86kdslNLo/2UhCyKMZ/pKufjXDv3Cq/5CrizdkBBe'
        b'OMMiY7bxgeLVR9YeeAnkb28Ttm3ceM3yJb+9HT56+RO+G5wc2jraJPCfRd9cf2F/aIFV7Edy2eKrg34zGT7E22dD+MCmNT8Y/X5nYW3cr7beo43vutgst/3+9a/txpju'
        b'b5s4sODTiy2+EDt/WIdX2NWKt5fdST0Rcj/Of1x6kkfc+88EN401yph8bZL9Wz5fz776ofV3g7afSJp8xh1WOf7QVLPwp1NRnzRUWh5LrP584/2iw98vdx608edJH5QP'
        b'nFSzonhadOFIkwHew+F5hbnobFOImdgNrk46e5sY/VkDhezI1xYPYl0XWZ0Y+zkTr+ARaNQXj3WrsXiBmuMC87bwcwZiI0vbjWggDWr+a01QpgrbSXI5kUyfGbMdT9Ko'
        b'TNwPZ3qrJG1rmF/GDMiVaQeJyDV8whuPQTUcYObYeMzBsxqNZwhc5N0HQpPoLJMNnZDh36XZyVcIdqZ4wQOKGHHyskio7HKuhY4tqT2ca1V4SdS5DkwbINaBFjQ7gMeS'
        b'GZwpdkgC8CbsE90TqrFxKOaKXjFwA+oZ5/FVKBM9bhoTl/t7+NG5fxGvhNAh1xLOnhtLlopWjbcjFgUzYzLW4lXRI60Gry1x9AukXTN5JKvBwPESPBYI10U/uVJDL6JI'
        b'wgno0EZkeuAx5pDlPX5274BMFozpxYvhmLF4ti/pnPw/GAsZ8AcaoFEyjYikPL80qlEmo0fEluzw25QdRpuyX3KHOrJx28jeypPOAEbDRwlg7Ipd1Ov/nF+/f+ZbHXGK'
        b'3o+iftpe1KF+/lG9/suhiqv/MFRRl972p+IU6cFF3zjF0WKcIpQ42vh3+Xbj/uDHiFMcPSZ1LEvDFc9rAhWxcKqnGzRx6+bNkMg5OzwnIYvMCWwRA/qa4GySKs0Jb3RB'
        b'WVprUDVbHKKx2BNy14iRiHAoHLLZhjBrgjDGhafvIozf9vXlUtWe5J1Q2xVqGDyPWpAuQCXb+ZZTWnQx2JAitNS6Gi9kmaTD8WQVtWuQOh7YTF189sNBsWg5ZNts0cYa'
        b'1gfzuHcAXmKblc2I7ZpYQ8iCw7LBgjFcnCjSbpVEemnCDKFWSZf1DDGrTTMNuwINZ9twZKPtWCGGcp1N8tXEBcJ1aOUdSLt2MqFmF9l667ui/+AgZogRgDxeIm1ewNrj'
        b'H6aF4+5KxOi/Fd4zxMC3swl2I2ZJsmgjrSsaMFX8UhHmu2QpL0b/+Wxd/u9F/z1iuNg1andh4WLU9oH1C1fJ08h6e5XRpjqRZXWzbyDmOOFhDWFSEemgbNG7TwHtEg8i'
        b'yfhDEbaq5HiOm4dZZmFzoI1V580JJrP382404s9p/Xp/sY6rzIZEvyJZxiL+XgweI+JkwFG4HK4J+dOE+8XCJTHib98QEbulDm8aasP6wtbw0xYGsCRfsZMlm6nhgw6t'
        b'ceYUPLt/5WA4oArCli1qR15ba6z4t1p0/6O1qMRA06Js9LSQehVoQ/CgJo2fssKdFVAfypPV8XdzFlLiulKoY89YQPl2bDWeaKOJwcNzu3APi1HdiJ1wkUXgcVi2arEL'
        b'HBCnw1mo0ZPbw3mZOgiPRuBtHMUke6h3m6SNwJttowf7eDyyAffGz2z5QaraS/JPiUlKDfMNHjTH/OuvKy5/J7vDbd1zyu59lwsNV/b9csM1a6Ojl73EbOKIbdPvTSjQ'
        b'L/5kpJvnuKqA6fdcf5WMq5q+9cf1E1596uKZT4a+sqXhs/s3zhxd8/kXBXfsVx4e+PP2uc/n7HCqOecaVRduN+/wfdMd8dGv3Hr7VZemv1a8kl27YNOnC4wGXLY7IR/9'
        b'/DC7lWWvXp3/eYCv7egoj8i0S1bZU+TPj7WLLDgVOek506wz1teGfBzg8tJ4uxeGPf3hdu9PuSF75Lcm6kW8Ff2B1+uv7Z5e/P0XAw0vzvlk6/9H3HvARXls/8PP82xh'
        b'YelNBUGKKMtSVFQUUBRF6SDNLkWKKH0Bu1KVLggqIIggICBNEVFBSGZSTDOamKKJSUyPSW6q1xSN75TdBSy5Se79/179ADv7PNPPzJwz53zPqdu3+uSR3esnGl/LUH37'
        b'68KPFv4y6eKmH1+ziDHNrmlfEGwm/MN2lWWn1yfJr87WAyOxJ88LHA+9ceedj9b+YJC6tvYt79WF4utlQ/N/WHer/O2MZz433zg8Ylbhmil0e8ZutsUvz5wXnyiYsDpc'
        b'vODbdptrzh7fF15IKrHYkLD7uZMPC/eyI3m/tnwUt8r0/VkuWp9F9H/YUHg06PXrfcc+rQlfmLVhas1Sc5kgwSrBYPmOTa+dhR3qRs90CweFk2O687scz9i8sv77t+Hc'
        b'd41utR395lXVpo0PXv23RXLxs3tfrrpwLW3yd7wPQuCJ+cdfOyu89er0Ta93Brz+earPxYtd/bbd771w+ttek3NrC723LPiy/cqnxy3np8+2XdYt+c1FGjRQYt35qXlj'
        b'sc3P4LdrdYaNy6v7VybfWbViMOJBL7s08yfbnR99+3xH+I+/6X/rtm3Jg8+v3YntEAZ+9t2St/Y8ZPa+8+UbYueR3N4lvTDiwC/LH2y8//ATifNMr5nTvQZUk4yjTs54'
        b'fXnKSS+PvAtLQnL1jv2yJv7VS0HsrVbH9xtmB/3hEef2w1tXh0dWqCTkuXxf6RwIH371zI30YcvmNaYuM18//pbdUNLnFy9bfrtm9urBgnfnX3zJ8gH6OFLwjblA9qmD'
        b'4L35XTkVW7PnvO9t9PnlaI2GU/HVlgsytb5pWP4Zb6n9/Ruv/Tp7bsHljb0T2rfmvblba1JPx8vffbQ+Z/2+9dnrPzvSWLplwVDet/OWGwxxO/1e9/ruxYxPTrvf0dku'
        b'7tSIDw59692dx41fsOmv9iy8UqJ14N4nBoPtjgUaMGmx28B2wZ5PQ76ZdLX4s+bv9C6FJt05cP+npp8/+mbNl99k/ctVO3T6poE4922bl3l9eeG8Rsf94K0RiSM/D615'
        b'2Jh4ct1H3wyGxr166tacj3ODSvcvH8zclGzw/Fat9eUWwGXDsx/4TjP1e85rxcQ/NCwsP3Pf0SZJJqx24EwB4rTzlymRbOM4bdgLacA4LBrAk1J/cABUjHHDwmXaJJLn'
        b'e0A5KB/jQJgA2Rwl/A1pFIHkZAZbFFA20GYlR7Px4uA5b8LKL4f1YP8YCBqFn8HanXwN0OlEmOqVmsuUALQoeEQIyji7BZAi6dYtAyMK/NleYwUCjbcIdoKidBtydsNB'
        b'eFpmDxpsCQZN4o0OGQxVUYDQXECeEPSBfD8iGEwH3elKCFrkVGE4Z+OrQb3JNIMza5VAM5ilJwQHOKsN4CJFKsAjJj628y3lQDOCMkMdvkQsZn1AA0aRTQNKo2OCMpsL'
        b'uihQYQSNYaUSZuamogCacXBoJxKMiGBxYJe+EmG2DbUAtKPNvpIi9ECfGcqNg+/JUWYEYbYfDFIl0wFQBgrHYsziwDkFyMwsjBQfCMrnKTBmoAUcEMBLHG9HLJVGy0CF'
        b'uRxjhhFmTqvkGDMJHCEvGNnAUxRkhiFm8Aw8p4CZNS2nGLfOoIlKjNkxrEujODOeHtiXTE3qW0F9qtgedEQqoGIEJ3YSNhOgWBDIA1VynFhaAAPaIq0IPIKPmKCjY4Fi'
        b'iJAuKIFi7qCOioLnwD7vUQAbonks0uFoiWReT4L+mWJ/O3UJenP/agE4wSJW8Tw4S5ouNERFKiEk8Px6OYqEF43OUPJGCGxaS3FoChDafA85DM2d+hGHJQYachDafBxM'
        b'HePQeG6TYS4RCxG/Ww7zxd52MNfONxXz17BQQnFopnw+OO0JKkgpUeDcZjneDNYzcsgZzzXWjArWF0CRhxxxBk67KkBnvOSdC2kvOxCjna2EJcCGTSymCthKNaCdcRsV'
        b'iLMgMMCAIVgFu8nM2IJGm1F5PX0nRZyhJZtP6N4I1JqOQs7AEdDCgiZDuaU4KFJVAjoxEgsenE5AZ/6zyONlsBocoJgzXwnHh8Ny0NkaalKPeNpjoFpqD86pU9wZAZ0h'
        b'xqyG9DgRtWGf2B4x6fkK6BnGnYFi0EmhjQ1ICBhQIM/g0GQ5+IwXhVOE6l0MteTAM3gcFAjASRY2pIACUnw4KFo7Cj0DVakCWM3CfsSPVpEhk4LDjqPYM6cNLHZwF0zN'
        b'7bvh0cRR7NmaaRiQA6tpp9rhhUU+1BWcEGR7U+gZaJaPNjw/CZ6hABEkpVygIBGeKjxFd6cVsCBUgT2TgGYGdMOqHaROY1VmDPpsHhhijWE9bKOFnoGt4OgYBNoiPRwx'
        b'tQ800quiUomWzH87rFSwrsbgEFnXejpAgT8Dw7Bu1AlZPdrXCGFXSWENba0Dq7qL4mAQcVHCzggCjePwZwrwGWiMx/izbHiATNR2wUY5AG0UfCa1ofCzMyyhMi9w0WgU'
        b'e7ZqpiCMhUUTYDaZiRAkPbX6IBmtEAxS9JkDqBaTUTHzg8NK4Jk3OMPXYTfAoxrk2VQ0TR3o4RbYocCeHZgB9pHJn4m6WDUGeAb2gRyMbikAp+iheACOgHOo1eiYGaHw'
        b'MwI9SwENBGuC+nhkHYG/oIWDr0D7fVlQbcxMhL18Kej0p0vyIixYgdjoyrVj2GhECafJlhfog9EXO0Ct3G/+dLQV4u3GPmKDWFEookwkVO9j1MBBDnQulSPxdEEO6Bdb'
        b'2xD6M4fVSCS1cM8g9MPZeCsgQYJATYJ2225IW3zePU0mcYb55HhUVULdTFz4oGINaCEtjmRgpRLothUcFoCjaMWsQmRGdnkk5CKCpEA3PFGgTyRHurlspdick26IqtFZ'
        b'r72CIt3s1kQQXgRmqcK6sTA3OcYNXgK5PNAALgjord1heChRAXRLXIyWFdwfS864RHgCjYkcnAbK8XUDBajxrEAOWhhkq3LC2LSoXQp0GoWmqQelY0/92+BxdEw8GZhm'
        b'AavmuQpBE9oVL5KFMWkPkkApI6GKdp4K0I5BZTm8dCmoJqMZAI4ymF59JKqwSOJFD310dDGTQDZ/OUthPYthgS1+ad0EHwnpsAqs4xbDWkDvOGEvGs4KBQwNZIN8ORSN'
        b'5zcZney4BA3PoNFrWBFsITexaKHDLtLhoGh0zMlvQBeic/EovgE9BXIoCZd7wRwZqjgAkdMBKexYhE4G7e28XRMSSNmpsM5AisY0BxzxRcwZvmiANdxOeNSEtu4EOBom'
        b'w35DCzEDiTqoAboQ46NjwNu9JCZ9BjnTMyePA+f5gc7HwG0KbJ6rHGMIyyItR3FtMN9fCWuDB1bQ3awKHttJ8bkOLGi0kqNey9FxTkTgPJGHElmdAC6woNQdUjA4qEZ0'
        b'0U6zaq2j4F6eCAwg+iAAhrKZzgr0Hdqmh8c1kqDvwAFIz3zQoI0NkhQQQpinqsQQyqIIQfIk4KTUWgr6FQC8seg70yBCzgGwdKoSfacbxII20GZKZm4DrFsnhkXBugp+'
        b'EQPvMmGtPDYymsZOJfBuITiCt6ZuF1KvOugEtUrgnQJ2h2arhgcL5keSrUUAB+dT1J0ObMMeCQqSCVmLQc5SJe5uvrESdwdK0LZGhr4DNknGIO9a4EWMvLsAhqnLyUp4'
        b'CvaIvc1mUfid6bp51GNGNtgXSKF3o7i7reAEhd7h63GyOZzQiJMD79QihKac3nIwQOFvUY74FEHzVEfBdxR4B05R1hHW7AGXZA7otMuVo+8o9K7ZmOxZO1DvLymxdw6w'
        b'T7CbhYfQaU2dUGaboHWlBN8poHeTkAykCy+A05QmaxB1tREIHobfYfAhheChTYeqBdZaBykhePE+ChAeb74p7CRTZr4QR+Mexd+ZmbHL0EKvJsO2FhQm+yDWN4Fi8FxB'
        b'/3rScm/YMkPqDQ+ukSPtKM7OHJRINP/vcXUE9US0CGF/AqqTQ+smUWidNsvnPQ1UJ3oEVMcn2gU1DFm7ry3kk/xmrBk3Ef01+gsgOpEKXw5rU5dD27g/MOSNeyh8V23u'
        b'o7A67g9dvjaBv/FJzVjLgUuZKDLEWgDOlpaLSuAL/0tA3XXuF7WlYwF1E58OqDN8VO/wX6LpCrAGBAOl/0wDwmQbfv0EHchT2oJagAEIaZ8pAHU8DKh7g5VfTEr0/u+A'
        b'cNdRpbcxXjCJ+V8B4YTvclJNViQYA3qbPgp6o99NfGi6OAMzLeBI+EYCdxt7dc2Cw7aMNRgRJIJa78dsYjXlf2U5j4Hd1vCrVKpUq/RiOfy7SlP+WV/+V43+jefF8qJ5'
        b'pVy0jVLLhKPiqO/X2K+5X5tEtFbHoDkCLhPECKOF0Sp5DI7oXcqtUUFpNZIWk7QIpdVJWoOkVVFak6S1SFoNpbVJWoekxSitS9J6JK2O0vokbUDSGihtSNITSFoTpSeS'
        b'9CSS1kJpI5I2JmltlJ5M0iYkrYPSpiQ9haR1UdqMpM1JWg+lLUjakqT19wtiWTlkzoB8xtHBRWsMiTklj2jgRPvFaGy00NjokLGxjpagNyZEU5eF0pvqSxb7hSyVq9Bu'
        b'n+MeMaHENkxj36DoOqUFTnoyDgkho+/MmWVL/zqSAAr40+xxhSk0dTJ7s8VjjAPltm4EJyC3qENP02PSSHyH5EwcrzZ9vHHf2FgPtmYxkRs3maXFpKTFyGKSxhQxxvoQ'
        b'm66OK+Fp5j3j9YXjEv7J2KrLK9aMBGqVmW2NSYsxk2VEJcYTO6X4pDHwC2I4hR5Hop/0TWkx4ytPjEnflBxNLNJRm5MTMmOIZjMDbzAJ27EB1rhgFmYe8cSWyXqxRG6Q'
        b'mzDewgsbQsltBOlEOMjnQTHitmbW7hLFa5Fmshhsq5Ye82eThOfQeokEYzYix9gDyi3xktPi4+KTIhMweECOOEZDgIERj3RUJouMI7CRGBq0A71Fe28WHZOCdlSZWTJt'
        b'ODHqs5Y/c8cUlpgsG2/btTE5MREbHhPae8SAEPHJN3nbEhNuCjdGJqbPmb2RN2bbEci3HqJ78ke/5IAwlf2KsFpisoWwaBPhYjXlKmtegTCX2c3fobqLR1TWfKKm5u3h'
        b'B4/5LLc9/o39CxCxcQvp6WZkT7MsRL2jRoWr/HzlVnEkggopd3Te0AwRy1G0LJ9sbmodQ8npaWv2T6BLZGidMQJlYyRa9RGoSRHUuo8WpixkLOk9Ja5NZHR0PLUFldc7'
        b'jvQwkaZmxMiXrywDrSvl9vFkyMY4i1kargavvsiM9OTEyPT4jYRYE2PS4sYEo3kK+CMNrcqU5KRoPMJ0Tf95cJlx55yGnODGmxSY+MswK63d2Nx37Z5U0pEu+eTllyTn'
        b'iiVvn8mWMfG7RS3D037C2TMw+j8NNJmCPlgBB/C9YboENGrBQglAAroEHgZnAM2CrwLhOcKjhhDNPqwQwj4kHF2ahxqwh9kTDg4Sne1325EEjP5mrd2eEKExh3ocnoOK'
        b'rwR9YTAXbfoujAvMX5fwy8OHDwURAmxiZpZivzehN8SFySBOrCp5SE4inparwWlY5TiDYwTz2UBYhNrFEXbAWRAng0WasHArdnYXmGyHfbyo2lizzCxYJZSCrIVUsdyz'
        b'PUFsYw2PghqW4fxYp2TYgUrAwojFZk9UwkJwTlGInRr+xTIWzgKLVSA3A4s7uqj7eaAI9onpMx6Wwdpx9ApUCh47F1iBr6aULbFL87KZAcqxNH1a6uVjj3UeYbBaNHkH'
        b'uJhBbgIqg0AW7KPPYDUsRuLmHC4J7EfCHo/YU2wHpaASh+6wgxWOM+asX8sx6ru5LeGxdGyGYPXO0ach4IKQUd/DJSCJrIo02dILdI4+hzlwP8uo7+US3TNIg0EJ7MFC'
        b'GDUa9MQvqoGsFZ5jvQou1VKZABtgcwa+e1iqq0mlyRV28BwRcfVAGRLxeKDBHLZmYFBGpD04NcZ0RRHFBjTOQMX6+vjYcakLQP1keAkUGcAz8IyPPijyEavBM6DYOyiY'
        b'iYnVdoqBtYR4bPcQk0Ozj6TxCVs95zIkjI4WqAdnUQX2mx+tAttuOniHWsNCT1gSjO0lfUJhLyVjRCvEaCbAS6BrpQbzQYtAAC94WIF2CeOxVR/W+7mgESe3GM2gbLrQ'
        b'GvZppaQhMoHn2WkisI/YjuiB/eBAHGgQizDcBgkwNvCgF7WqzQFDoDAFuydTTyXZOtmpSbCdZJu2GsmrTbNlKcTVGE+djYCHTQlFzjYI2gAuylLhGXWcJ4ud6rsL0RJ+'
        b'tGi1dAr2P3WOFAeGWEPdSGqQU+u/dyLIHltRxmZKDc3wIhgcnW5EOmfpdIcbZGAZxnUVGrkxYWD87LwDQj2V78vHEVMkAxvU3RLEoC3FkBCKaUjkoxknB4QG2oXRLAw8'
        b'yETD8yIGEVNz/JWhr1kZlklWzO9IPOiSrLdY+8Wt996+N/zKe4VLsrRNhdyzqh+5fqOtNtVbbY371LOzXl5z5mOVkEGNdzpdVoaY3TLQL8h5nZmzICdg0aTCfQdv3H3+'
        b'2UWpOx0f/vr6leR7/jdsgsLcnSt+DH5uhqXNy517rqf5Js10ftXgy85y7UJ+0LOsYUHl9ajMfTXB7toXtLdbrT9R7Wjz0Wy76OmnX7sqvn5jTge8r77/YlRfVr5t1A/G'
        b'PlHZwU5LtK7+8bKeReHZPEGyjXhBgNni7H9dTf89J/r8oEPBB782T6sonH20dMWpq3veFb+7NCc8/oVAZ3Bb50DjRvd3aw8F1CbYvN66fVfzj9teCIk9pLJA5uo/I9qj'
        b'4Itnf8r8MrKyKXDpR29dyR/q4e+0z/nikym/1uy68oanyyuv//DTR7+5ttoav5NfcQ44GH32hueFhB+lr2b32yacb9H4Sm1lQMWx71/9dMr3V6b/2NL61vx/rY8J/lxz'
        b'3R4N56ivpMt/ub8j50Z6pWaKSu7GZS433UIX6TgsMRlS/WAp36TqvQ/zNX4Ku22/b7LTL36mX7sx1+ec2LHs0pwg6QWZyeffXl7E35X74edbjy/8XffZpa3am7Zu71w5'
        b'd6V76ym1G9O2Fflxx5bva3l5KNFvRf6bnRop9ya9Kv7F8MPPf2CmLJjzw9uS0j/u8N7fEPPbSMe/M6uOvtk1fd6zD6++alyr9bClvfTa0NzZ/XWtwtkGx7e7LfvpXw61'
        b'3v5vzpzdv+TS24eGfwi/OnL0twRzWL77zq2NVrsfvhwWsthhU7i+371Z1092PdPWrWa8dOXFcIPdZb+HrJj32hl1A8PInBhr8KbJ4Iu9nzQda3xLKLH46cGSwDvH3++B'
        b'7e99OHFHyc+fzNnDS0wT7X5XTbKY3Ou4goE5Uns/2DGRQ2unjfUJDqLXYSfBKVNQDHrwVuEFK9E2BYs4RgyG0DpCm2F1Ora9mRPrJ/XynaOvgvIWsAtglxHVA/eq6Y7x'
        b'xnopHSvD/eyo3qlYLRwUy70gCGHTrAjOApZupZeGFc5oSRXjcFHYLlXfbg9ng86g1nR8YyCFF/koI1bh+tqDwgBvWy92FSwDBQ6etjYEo6nChKPztgv2QxqXBe2+l8Y4'
        b'qIUX4VGq1reeRZtZ7mWMb8NgqZ2QES5mN3CWaN/vpRd2R0A2qPUJsPPy0LTF+kgxOMvBIS1AXZJawmMg+1GDAm+Yy98A+kA5qd3OP3RMeGRqnTyFzxctgAdoZ1tAJTgk'
        b'98aVkC6/EYylep/F62WjrrjARR98HQjOa5DL43AwCI/AjslSL9CFDm5+HAv36apTJX110HysCk4gwV5GbwuNYB0/VcQnF7qTPNAIy9Vz6BTuYkC32gTiBBdUasN2NMSw'
        b'xdXbz8cOW7f5ywuYCg8JXEANLKMXkhdBra0M0QWeDB9Nfzt41id2JceYLuODlkC5+TMqqhzkYr33AVXyhmUcx2h4cPACaANNVKu8H228F1GN/na2fsradsFhljGbyYct'
        b'sEuVXDKuANlp+GYT1vEkY3yL5bhRJUGWPqwGxQH23n62Xn44EBfLaG7izQN9UjqVrRYB9Cgml7oatjysrlQxh8VUP3gRnjYnKoASH1iswgi1o1Q59TiQTS98O8L8diNW'
        b'hbjC421hdzFgP5khFhZJYA32/KhUaLLGPntokc3wuBPoSxmjnMO334edSHsMAKqKOFIkqk5B5AZYy8KLiIZJwWviUce7jcX2PuQCu4MFDfAU7Cercic44/xEbeVkOx48'
        b'MkWuKA8CZZOwQjFmnkJlCAYVl+P7sNZp1M0lbOLpsBtAI2wmdcfDwUxXB6xhwi4yeVgZU+aB6JkoJoqXIc5jXybu1AEpblofC07CPFhDFYVdaFqVHmHBMCjBCvpjoFFh'
        b'6H58kcKARsAItNTgRY6F5yPpntCHmngS+xeFWeAk1e96gXpy3x9uPx+2W+HpHfUxqgu6ebA40JMaFZwCZ+BxgjPAKjNnV2zYUsuBwmWqRG1n6+o7xhM2WYvgIMhW2hAd'
        b'UaUeVQ/vcAU5GxCLKVeJ97OoOaXG8ut7hxD6hPBHGTpCRjOa5wHPT0/HABlLUAdzQfHWTHhWI1XJ0IEL8KIUg7EdYJmnn51EyAR7iDQ9IbXFgedBn41MqoYYYFSsH8uo'
        b'7OZmwzI1skaXa6XKpGmY1kF1nIBRieFmmc2kq6p+Eg6p5YXVPgEkJJ+AMYAdMD+Sr7N9Lyl5PWK9y8W4XJTfRYCygw5uga6YqAk8NsI2RX4cwOQoHFRhNP15i8BZUEzq'
        b'TkLfdcgQae6GDSwi8wFW206H7PZgaLIJVcmAitUMzOd20ybtB/vmwl5wWqmWGVXKVK2jOtHSbRlyyxg4lMGANsR298l9GQZnYEeeoBU0EWeelrAYZJGJM9MKRC3VtkRN'
        b'8UJrk2wODp6wlId231aBUxLcTy1/itAoHPKeLvOXyG2mfFhG24S3QhsOkCVsGwIVnpHDQRk2QumNInVvTEW0kz9XRvcUHshnd0SCITrhWdtgodTbzsfOxt8PtoJmltGK'
        b'40WC/GiihRPCRtCEGjfatAB40g4dQoXYP6tkgwCNYb0sXYpetUqOUFLGYbQilOw+poyAuXNYxgV0C/1BM2otWUf9sGYDOAL3jYsWBs7NIcRuG7tHN06MnyhOFR14kQe6'
        b'/OApktvdK0RKDh07GTgmZERwkAMViPILyFAFORg8rkaC/dP4uqvVJBr/varmf6TyeZJjAIB+/blCh9mrFqPNanJqrJCdzKpTFQpHLswfaAtERLkhZNWIIoT7XaSCP2uy'
        b'RuhnMjuVncbqysNjidiJROmjTVQlhug7Q/Rfk9PFv9F/EWuKFSm/CUWGT/hOiOrQJP4YcQlCOTAF+2Lk3+Wr7DAYe7003luBREChId9gNcW34+Em6v/VtPBocaOlK4fW'
        b'SyR3r/Xnuhcme1r7E7QvT+7M/8j7QRe2GSfeD8ZXo3R9MFNx7U3ujW3NYuLszWzw5Zf9jDmOCucsj3tC+EvNi8PN2/FnzetVNO83Y9wO+R2qWXz0uBr/UmWbUGXt7E1R'
        b'+EZ6uf7UOvuUdZoT2DLB6saakWwYfP+3a8bdlLA3NcKVV8fh8U+v/pyy+mmLzTKS4lMzYp6A0f8nvUdtUA9XXCX+WRMuKJtgg0dAlo6GgFxGKu8h/2kzCEFa/NmMDynr'
        b'tg9Oxi6BkmKTiZ8Ds8io5Iz0cR6G/n79ebh+7DHmqfWPjKe4MR5v/llnPf+sMqCszGi0MnevJf+MxtJ8/qyu5xV1peFYt3+ZaNLK/qzQy8oOWIc8wU+RwvfGP5onRK5q'
        b'xH1AOAbzP7UJr4yfMOIBgC7afzRhErxFkFrTk59a5xVlnZPk3iL+YY15iq0hKjIBa0DCk1Nikp5a7TVltfNwtfhdei2fMFa396h7kX+8YWkqW7UxIVkW89RmXR/fLPzy'
        b'f9Ws/4VXyrgneaVkmUdVETz/+K+36AtkmHtW3W/89S82EZejRLEf+fIYUQHb78uTsNTspxdUIjlbIf2wMC9ULv5ogYGnOJecqbCSwUL/f2KqmL3CuB36j5z0CTFJCh9L'
        b'T3ItiSt4B7MW2Hnxf2ItmGz12icwF0+s8v+v2eD7h8RvvtTFyfDX9z16fCLfblMnk8GfzlpvmzVKfI+P9jmGjnZaGfsYMxMeHpWcnPBnQ4lz3/wbQ3nkL/BptM5xY4nb'
        b'jGsmYZ2I8nXUH6fC/RNVwLL7NZTKV65AgEaZh0aZI6PMIyPL7eEFj/lMla/jRxlLkzjoouO4UTbzl4cXXLRrzEU/s22qGswlWq+bUYK5iZw2wyyKUBdnxjAU6JcNDsN+'
        b'mWaaKn6/iQUjy+2RWEbUIlo7+SFq8gxbUhcyGXgz2Lsa1JD7EwrLx44sSnzQB3/s2yIoMMgujGM2LFLxg3mgETTAwxnkbqwDnAFFPt74Zh+UOSjvxwSMzUYBbHAHp6Zq'
        b'09afAlk7RhUYabMiYJ4hUTqAS6Ab9I9GnjAOllv3aoFOigiuA0fm4tsdcg/Ft2NB0STQBQ6tokDdCpPVCnQvCw+JYbYqOEfyLXMGpXJZFaN+kKBqDrNiQOOqEPLYwgrW'
        b'EaHQzosP94EaRlWFA2WwPJUqcYaSQCt1kcDns3A/vAgaDCOoqqZ8PsjDl5wSO2EYrGBU53OgZS0YoflOQCx4K9A+7JpdoN3biuY7tgMJncV2/kTEFK7nuIUGoAgcI1jr'
        b'ZP1JPrDMC7vV84XFZNBptGfpAgE4DUZgKcza8hhtihW06TlKm+Mpk1W6I/urVBn7KFXibqk+RpX2/oT2eHP4q1x5hJQSzgoDaLRY0CCBp2X+oA0UyjErGLByxIcOQz3o'
        b'gvUyL1A2Q27py4JSkJVAHi5TBwfonGnCMsW0xUjDqW+RXFRigcwXZnsqrh3BcQuqPT43C5TIkPze4IDIXcSaqKylnlL6V8EqH1jksleOLpgzk6g1QTNsgZfQQMNhzbGB'
        b'0s87kMUD+sGxibDYJwoMydExLGiauYbQzbo4WDYGF4NBMesdDXaBJqLMpq3pNYPD+JA2ZyaAEnN4HO6TCIi+1ggeBYceyW0J6gzgkCkduXZnC/RYFeSNhhSHZ2BTBjnU'
        b'joRtVmBiwBF4aBQUUwuLSXYzWA06FaGeVGABQd3A3iiienVcBM5JYWkUg16w8bOX2Hn7sYwFyBfMh82ghOQ3RsvsqALhQuAtlfPhSR8vstKmhPmIERm2J0qI8loo4iYs'
        b'NaaOAtrhsPHjwU+w6bXuWmx8DUdgF9kvVMDZKcRM35dcLOOtBRSR9TDNKW2lYAtohbkZ2OoRrcjuVVjnAeth/ZMDxJAK/EG2CixHjyuI0jMmMkSWkixU6klR7xtJ9F2I'
        b'9hgcqn00vk017JQHuCkFHcQKYBfIlj26lcFjavLdDJzSjiPEsWp6GrFpzkUjo9iRuhw2kgHEhsXdPnaoT8UU6YBxDsOggNDvbnAJNqINALTOpHb9LDiVvpCMrfemCegB'
        b'LF6o3BwMZu6i+1sOqJmK9hMtN/mOAtq3rCAI7wm+4JxHPKJhlmHnMbBs6R7SPD7aLvZL/dCGVYxDB/EjWZhtCnIoXTdN4hB5edrZoqFzAhdF4DC3S3sFCaYL8lFV/VLr'
        b'KclPMnuHxXsJ9eux8KIShoJBKGhYs7XAyBQyvQGwBxQ8uo/ZOil3Mlg6MVEeSDfJAC3mYnhGVzWTz7DYlv0kKBGRSTQ1x66ZUmTwtBD1/xADyp1DyIMtiBhKYCX61pbx'
        b'AIds0ersIAeaQYTY+gzPmmG0I2y7Vs2jDgTi7Xii1xjqXmLiVCn98u0MgfcgS4++NOFs+qVVmIZuqdz/wHwmkX4Zt1OUcoExQ7kjbLe66D/uY4HwivgHbyjZ2COAym52'
        b'F5uiEs2Eoe00lYtWCpWEBZIHVGYzH+HJb6q6xsUkxWxLSVsYoyrfYrksQ2qsAKviwGlZ5oSUcXfoUlhBPZvaeiFaQx+OjPO1gC1e+kClrg846KgdNRe2g/btoN1A4JGJ'
        b'yH6FAeyLResduzvZbIBWEsZIHoCVdvZeBI3ivSLQLszzCWcR6OPUWLR9ww51FvZGWGynZNMnm412bIkdLELTeRxxBgqN0eRQPujcrhLvafGNQPYS6m7lt2kxwYNJeov1'
        b'62vu3hzcMDLFa+539yrjdE3zDVo8l+eXa/stffay+UZJWkJ2XvrJRY3v7rts8m330iW51r+oTV2Y5Xb8c/F5WVzfvObee3Wy13e/Wn/rnq2N6emKeaabDT+LOjzjNcuA'
        b'H49NnN1y1d355vxXbo8s+pwJXvdF1ivrLu/zufzcR0yaWbPLS+6tkw8FJ+39rvbgiw2n1qecyLH5ueRD1rx3VuhPV2umn+wpqv79Zze7QPtMafq7pfa3jq6/+tXq6Zut'
        b'Qpe9c7TqkORO3LWiK0s2hHrZZb6r+qbg037LzHVvmW6r3i7JPX+s99np1s9pnJha1/eTddQ0y+gvk6IyN/RXSX1Sja/xY3dXsE1eS8NjrhqoOs357UOr3BzbvbNv2cQK'
        b'VwsWV74n2VsiyXxjzdz2E61n3nzrzXVxtvfuVUfJjL+Msgl5c3PrQ5VrJf9+dsoPi0133d/yWW3ccxpc+NwlmeYWPTFXrjd1rl6f11TrOLzH5K3MTVGJRa9VOhfvyrmu'
        b'GlK8OXuHv+6Gqa4e2wrf33l5Sdr+ZvvKHVm7aq/HB620Tt73vc3t1WBL3hdtv1+8efz9jeCofs3Jy4c1/X27BNHZN8Nc7hgOp1pZ31794aQF0dtyrWR6n2u+JDNOvtj5'
        b'ymp9p60GU36QlR5z+bQtuuzlOS/GfPreZUGAi2PGysQ7qM3zRxqHPePWfTOjeHnU9/xP7n1funrHlklf/bD7Ql3K+uJ1betTLrwBNXPDA4uNZ8148MLd2wFtL4W+esPP'
        b'V6B1w+jMpdRYE/fquBd7+6+Elt491ju8bcrIzzt2nIr6cvGtDza9/covmhqO/X9I4re+992Mb4ePni4tf+mZeft/P7z+eYvwpJe7tOa9phN2ouv2his51lPcyt/LlGYa'
        b'F8LX5uYnLVqyoDmx6A8x2Pb1xcIvdRauvfqcfc/x/LcCGlW7up+5b+KaXVBn7/Z8/d7Pj6wbyF78+2cbN7nF/fLA+eCCjX98PfJL3MwXI+5J5lPtXWMaqEe7Hdq5Sh1A'
        b'G5/szkOgyJ9Ct8/CGtgqhkUyX4mXqjXipO2EjA44yQN1APHmtISBBFgstpGgIx6bQlnriIy5MHAUXCCKmJWxsBJxnkNjIxZW7CGao1AvD9iXDocTR5Wsa+dSOPA5kKUn'
        b'9doTMqoFh/UmtLbcZeAk7HOwQsfTqP41GeYSbWNAGuJTin290sfwQ6vl0Fb35TgOapHEK9U3HGQ5SISMBnppGsjZSCGAPaArarwCtkgwJlyh9nqq2u+cArtl8AzoAfVK'
        b'2OYSeJw8NIEtGfhZC6hQxBpkN4C8LbRTB2AjuCS2RjvZGcwXcSHsQg93qolutoH9BlZjYm5GptLajjmpKwHKBJ3sbwsGE6hqNXYaI7NH05ClAPriAJP9M6jmrITbgeYM'
        b'zQna9nwEjJo6Bxp2guNok6UxY2F/CqyR2mtgi8YiW4YRgk7O0TKOasiOg9P2ypi18MwC4k0AcbxVVCl/cTkcEktcwcExgTFxVMxaE9JoGZKGhsTW84MUITVxMMJ8cJaW'
        b'XQ9GkIRSDIsyNPAui9iB+Sw67bsZqjodBtni0VieSzkMqZ4EOkib58MDM2SwyMsLDvhwDKixV0nlbGR2ZHSjQf1qZVB2AejBWFY3cxoAtAjsN8KKyFSs4BUyais5iEM3'
        b'XoRZrlTNPACKF+HoihfAyRQC3BTgCIo9K8FxOnMnPDFStwQdSqdpWEJLUB9FJ6jDG9aIvcF5xMhJhUgQuMgi+ehkOkXpdcATiB3DZpj2Psmx9mqY+5kI+vlObqCWWEnM'
        b'R4NRIUemEcjrYdgpx8yV8tDCKYNFZB2ugwUBY+CpTpFjgjDuAgNUV3setJA4j6VyOCcq6jiFdNbDEWoV02MZDPvsJoJqRSQ4JG26q1MAbt4KMKD0AQHak8Y4gUAcXx0Z'
        b'ygRx4Bh8LQHXmoNyMIxmtYzYHE1h4QlxhtsWGtiRXQz6VtE4fzJ0xiKOv8TPGp5FkyfwYGEpX0Spv8srXmxtZyEHIrKgzX8XBYb3gHZwIXb3aIBeW3Oyc2iBWpAltvae'
        b'T/XRGGCc4kPmw98SNI+JGegwn0QM7NpO9a91ViBHbI+2iDo5dhGbbuTCSjLG8d6gXAlcBB1oOkZjBgpgG1GTW22PE3snw0tyfGEorKB7RyHMN1MCDNG0Z40L7mcMs0iz'
        b'w0AzOCi2M5fIo/txetNBPxkeUz1HbDEL2lOwL4C8zSo+nPkCkEWobxc4rQn7bGGdrhz2iMQ4/wTaoXrQEie13wnbR8Njc3ZGoJJMVpR7ICy29UebNuKxWEaMFjHaNAtg'
        b'twNsJ/RpNwdRBn6jRAILiCvGboyfPwdPqIHzZAaWwhx/JK1thUcdsFzQyAba29ODoRdtLSelAbb4noDYZ4nhMIdY3k44kIwajjO7opVwTGwDSzRgGQ+bGs9O3UX2gPCY'
        b'dKXRTvdk6oxjDk8FlC+j9mlnwcAGhX3aGOM0kIUExk4LkCsx/H8N8npEy/rfO0G8qYYBNeHEmJ3w3B8TBvk/39Aye9X0saKZTxCM+LcmN42oum1ZG9aUqL75RN2tznJZ'
        b'5H4Qv0mV4X/wedwDjscJ1X6apmXITmO1OU12IivksNqbhh40lAchNCIKcnX0W5dgBNW4iVhNjt6cyGqKsOpd8+FkzoinKUdNmqFv+A/xz2QOl6hOfPcbsnLkJSfkUJsr'
        b'dkge1SPjUQi3dyVaJ9lC+9FRofIF/6Zq+rbomPTI+ATZTZXw9G1RkbKYMdryfxCLAMksaDNi0kSc4uJVBX3iYSkFh937zxevTLbZt49fvWZgb5agKgI0yjL/kVyDqLse'
        b'yTbMXFijZesCc+W27qBZAlvHhFvnLMAJHjq4D5ArgM2zA+kzUBAAa3YqHAUZgRN8ULzAkkgztm7rxjTADQ4HyEub4sKHVTAvCUmv5DToZpePrWgVuMibB86SeuZvAQ3K'
        b'inTUx9cTKyXehtHmcQI2SbHhVpe1p5+9l9+KFDwUJHoGdmLAMhEGItBiPBV0xdAbqxOwQTRqmk3MsueGJoJW/QzsAwFW2gPsq8nOGrSHkKJmzlnhSVuITthzjPNUIfZW'
        b'RD0XNwng8NgoHrRu6zHXt+tArQj0WWnhcSYjsx52bBozNBNixo2MFqwh1zZScBhUyx4pLZQ6FQa54CjpHuaMYveKQBNsAC2EduN/14zkZIfRx0bzSqWMWN9/77OVpv5z'
        b'VV/Pc5oqSHz56rXs8nLdC5NWR1nMN3YxK5qkuqp5vVH0ipO9Vl9++Svvy+BnJgS2LrKwynHcWpq39PbdW7LXF9x736XPYfWNqwn7S3/9IOAV9TfrPg5+5ZWbS31rDPZt'
        b'CfB5/t7zKR6FTglXa8xNyzOssvnLh3+Unn0l7Y8iy+74mltzooJW9kuc3N86t/qrs5zdreC3gg8XH7Sb8WlOotB26fO7O0TtFlNnGy0I+eaj08VXHW9OuPzc1aLs55zZ'
        b'w59qbtEevF3+TVZT6+G3ea/LSiZbfXPhk+butZXVdreEjic9uUSdm9dkYUbtX1TsXL7h5qctpZ3XxYE/l7rVTZyydu1z96cUvFmTtj/3nZr29LsH31SZtdzznbfX1Z25'
        b'tjLY+OOTRyTf/fHm3iaDora5LotNPB7U+D8rXrEt3/a+hW1T04rephsHrg+t2WbyrvPd9f2LJz3zldGdvVWNqmnHZMbg2wu3vzuTFH2lL3xaSFr4zU1XGd0vf/otx+XQ'
        b'zNcthszdPaKbZk75QKbXcl7rxqxZE27d75t0Wgc4iRqmT3ax0eM9P7yNe2HnH4ffO/9jxMcftLwhfbBwZaGqX6fhgUuTLGdme+04orLWQO8K3/k7065K3R5XmHpvVYhB'
        b'yhH1j+JeXb665Vc3lY66EKukzw8OVrz7zAufFq05lna9PnLlytt/5FecizRKsv/ZNXegeavGHwc/yDjuNMPgs9+4y6/Z7LvSFffq6fUhkZI+vzevD7x1YUT2Xe8lk/fA'
        b'0q737/7OnyDZPcFut8p34eXxb3R2fxcXvXJdpvbgUI7pLXutC5Uz3e5v0r00/0btx9Jba28anEt0aT3xbvD5ibtXnmr12+O/YjA+xaYsMcWw7f4LkxIjSndMPzAxbv+1'
        b'xpBvWPHve5niyeJA3xHJjHRsJgRawZGFjxk0PmrMGAbzRZqggzqKgW1L4Lmx1pMw1xF0zwaHCMs1exa+9VfKjm2wCcmPR0AxYa2x9XYFNt9DDNE4C751k6gMGAz7R42d'
        b'8ZWpEJYSLmAbPL17jCfmatfx/uGmSgkLs1cHHpAz2KDHewyHjQSJk9QpRB/s3Ct3RG0KDrGL14ZSpr5xIsxTxBlHG9lxxNT3O1Jj6SYkkOQrWBTpDtiCeo5EYeKPBh7i'
        b'g7NT/EnvtoMha7GNlHr/8vEDJYjL0uNgrgloJkOjJoZt2FA8VYJ47a0syNKCdSS6O+FuT8TtlUlYcAHkYrmHARd2eVD5qjTaTUYdpflvlYDS7YjR3sqBU7A1hrR8u7Pl'
        b'GLtG2AGP7PAEZwh/KpoGy5D0JGS4lfNjWBdzeJB8zV/ui3jorRZyLjoQ1BE+zHwhHBlj+koMX91Am4fTejpC7evWEK9tDNF+eMGzIEc/Qu62YlKiUlYYFRSOwpNwCJ1V'
        b'56ksVywDhWOiTrNTMuEhJMoSBjITCVsj4y0Wg0AjDTsNOwWkfWsRu3pOyRejDbicwYyxMZK8Me2s1zBReBlCEkAMaLcADaGk5oUqm2TYSz82KOWBdjYInbgH4Knl1Nh5'
        b'CAxHY0G/FEvhPHCWDcXuSYDcCYkUNaxObO+X5kjwCuildMST6+jzNmcGkdXgB3JAA5IWU8iYgTp4mBFpcNHqBmTytuxeO+qqDvSkCuW+6mD/GrL84BlwIfIRrMNjSIfF'
        b'8JwIdIHTc0mRJkg+LVHKr7NkRIIFF9GglVCROgcescINUoquAVNgD5LHD5BpTNPmxN4K4RTWmYAKUIXESjJD+9AcnFC6GxSGc5tDbGyQsEgEwjJ4UGMcG57hrkSJ7Edz'
        b'THiIBpA9FRb70BUcwK4NgVmpYB+VTobBoW1jTF3XIvrIRStL7tSkBZ4CWeNwFrMcmYlm/A0mSH7GO0A0yPMcNe73Avk+xKEMy0yM4Vvgex5SSwiS5fuwvS45yTfDM4xo'
        b'HhcFylcRAdt4m4PiGSiA++BZhTEFM2UiHy2dXJhPZt1r5R5KqWjK+31nwBa05nw5JNqeRkNF9oS8GYiNKMZMnB0oVGhWQOUSzGjMWCPUA8U7qb/H0iUBT95esUUwqmCE'
        b'WgXv3Uu93U8BBePYRRVGcw0PtPjOhFVIjiJ+gTrQlNX4jK+ZKHSQYApqdyN5qQTU0kFtg2VzcXEBSOqzp9HCNHm8UNBvrrmELJotcMR3FBizgVusY7k8VaL7/1B4+l85'
        b'ixnrDMZBYeby0V8Uo9QT1YloIiQ/2pwhNxmJPkasPvqPhSAs6FA389j5PBZnRJwaicsuum+qIkrTR7y/LmvEE3ITkbiji54Qxx0P+TQSNSf8Q4QddGCb5IdC+Xdqfwh5'
        b'6lhieIhkh4cinojT5Knz1IiApstpE9thXJ9IoEnskXWReKdLYrvzs/gsfp/J5lr5Dx83xiVClFxgora/RML5XxkVywUm+3HDfeuvW6pMq/orFsW0E7dwhROfGArdIByD'
        b'7DemU/kwHCPqcRBaEg2dBEcnIdFr0a+bKnL72pvqY81db4rHGp664rexW/m0RPxrEf61F9ejqrT3u6kiN8K7qT7WNu6mxnibNGwDRax3yMDQeTD4v7uSGLU/uoOqd8Lz'
        b'ksVQDzR8TVtuGstFUZ8xHO//5q86X503jUeUp1gfXUdkJzgIDqaOhVBPgm38GOwM6+mWXnhOiOcURhkvWEVp9cX9s8jQ+ARVZx61+trsn4EtUkHj4jmOM2bPmjtzjiM6'
        b'ZXvT09MyUzNkaJe+pAJ7Ect3BjG+p9FR2qclUlfTVNUQgwNovy6BB+Gh4EBYAY+ECbC7zQti8cQEgqHfuT6RKCOLpRhKhYPV8Bg9JCmftOTBi6B7CtF6w6OITS7Gtigh'
        b'sHMmMzM4jRhWGE9IITnQLx7ISWP8NuvBHpQNFmzI0EbPZ8PuTY6oC85xs5hZcMiImB6lCuwU1ZFMYHA7qg/lQkwHySXWnOLIESdoJxwZx7061B5pn5UeqkbqEI06cYDH'
        b'MvpWKIsu6KMWJ8P+4KgjlrW7Qc9sVG+BgFhfBKLRyB3tHk+XcdHUQz1ETcyD/Rk66BU+OrUdWcwxNsxh5iDWmVS312sr7RnOxTFztujroUzq8CAZjumgNc1RQICZBXOZ'
        b'uQwopH4BDs8Bl2hdNBvMWazPonwbttBWVoFsD0cecfxY7MQ4iWElMTEBbSbYmITkDASnVEBjGqMHLqCMnvAwHf8DNu6OKljPFDePmQc6QQO5EPGCLdNpM1UsGZi1gFSm'
        b'7kZGMQmeUAF9eJKE85n5eyeQWxLQjQihVzEcaCAsGHOWzhnicwrIgMw0htVIYmGYCF1nxhkMBVCDsWIkB3TTiUYE1ZVmxjF02kw3kWxoofTOwvQKSm3cGXfXOeQCxSgT'
        b'XCDVoYyWiHrhATr8E8QkkxtqTJEMTbb+rCXMkl3wGL11ObxkpZQSY7sbDzS6MmT0Y2EHrWlAYIZ4SmYRLF3KLIV9c8kgGoFyeIwOIu6dShSzg08H0QDWkEEE+2DjQrwF'
        b'a8d4MB6IRTlMatOLNSZjSHLpMnFghAzjIpQL18Yzhy0yNNdz7ZYxy8BxMEhWzUzYBarlHaNDSddNT7g5yjtNvmp64eldMjzfjanLmeWw15IQ5UpwOoy8D3KwJwUwlMZs'
        b'StUDJ/EkDMygtkzViJltkOEZz93myXjuhcMka+aOVXQKaEZXRgQOyJfcIdBO2qtji3gqPO/hsMuL8UpcRKYvPnG6vLWYWKKYWVI6eWh1HCfZ4JmgKVgByMChBG/Ge/ky'
        b'YpwDy/Tg4dFBdVBsD8WwJBk3t8OYjmy3ITgC+9A8hmn5MD6TYAkZ2RWI2OpJe3PhmTRErd108o23ygNqYSwZ7ENTyW33ZXxB01rSyXDhBAXJ4I6mMdqwgM4kOAoL6Pgc'
        b'1JgJ+1jMzmf6MX5IHBqmK6nMbAalHJLVFTG34AyZTndYR/q5MDod9qHpnAdP+TP+sH4LqRIMOLoqu6kCmtIYWD5ZPiW1S2gfT4L6CbAPzaYfrA5gAuypIWVGOsySkw8s'
        b'N5eqmDPy+chB1EqpDpzADibQXNquC2QC46aTvQJRUnMirW4ivOSuXE08UEmWr+pCWIENDdV2rGBWhEBKdWiNnedR0slGHPhpTAV4qziEK2yAvfKxAT3zxXghVkwNYoLg'
        b'MKwifYQnQRuoIEOTDSt0cF5XeaWgS0oGxwKx3WI0iynwXDATjCQ6cgnJxYNBJfHIt0RMAyFwH8obDttptUVolk+L8R5cKQlhQkBPBDVWrYL5c5RjS1cL9j+CkdeduO4q'
        b'RC24ciks0RejKY2APaFMKCyOoPv+UVBqSc+KXHRWlKeR2QTdq+hW0AFOmIvxTlwVGsaETZRQk71qkB0r3+I6IlB30xSTUgAO0ZVZwbqI0VQ6gYKVzEpYDs8Qs68QvW10'
        b'6+Yx8JCrvhNeyiZ0Fk/NNBHj5ZgPB1cxq8C+rWRoZiG58rB8ZHjY320aNgGukK+tSthMWmkJeixAMdnGV61mVq+Jo8a5zdigFxTjmRoEDWuYNXCfAe1VJ08fFKN52Dln'
        b'LbPWCJWiKx9gH1gpwAaHTfaMvfMkQiiesMOVxObRnOvAOHi7kHdZULEZm0Kug23mjDlsBmXk3SVwyA1WooKnGUgZKatC/et0uoPGYLyWcmGlFWOFDqdL5G0jc2dYqYJ5'
        b'Do0ZzAzHmaRtGYFoYWFjsLVJtowtrNhE6pOtAJ3BAnwTXTKNmYbE23aJGl1Y3VjUkx82eIBcmcAt5OhGsvVhOsPVG8KU3Ac6NOPUyG6/dzI1IcTqut7R3QAPsbct3UcE'
        b'aDbxMTjHDh4iJKKxkzNj6WGxGvZQWmjwhV2K4w7limJmgmxCQ0HyPcMf/VXujDDHlZlhLqeWBrRyiD6+PElGW7ACzX827gSlwvOwS9HIDnCckjfpaRSTvkZeSCXMJdWE'
        b'67CjS0jFHc35cvniy0XrDG+X9i4LFDvQEkRGAbSTiPE6J2Epf9G1Ctb4kLiHW0A/DpcmAj0c2go6DL4grGN52iKJGrGja2M5hh+yA32KSBBl2lDjOmdfDWbiqukCJjBC'
        b'/Z15hvTLhdtFjLZ6ppCJiPCdqbmafskF6jFTl76NV+Ou7ag35MuJMwWMiF+ggq2OEw3s6ZfpmzWZya43VJgZEb5fua6iX96eqsKomy0XMmYRCd4iJ/qlsZsOY+Z6H+0u'
        b'EQnNomX0SwdVNUZfewsP2xAWTvenX+brGDDWi/yxueDktduj6ZeC6bj2YWJDWLIhSB6uyAN1c8aHuJ3qZcbxDLGOvj9/AmObsJpFta8T+AQh8TBkGXkQxaAiEhIFuAPO'
        b'DtPp21t8hIx69Ahuq62PMJP5orYG/3vJjVQgE6KnKTNI8KK4VcHMF47k309udEkWu2J7ErT4PHcmM8mzwRn69fEZ4KIUrZyVvG3MNlgFj8tdbuEV4QNq5KSioLcMcErO'
        b'gl0UkUprtxgyttp9uNJdhj5atKvtW9GgTBbg/u96w130uGWk0oUYviiLk1tG0lhJozGS5LiQm4L4pOiYbWn4hHlSkCQtJJRjtowxZIjJIhwGZaBV6u9PnUXAEj/fAMRx'
        b'/EmoqdnbQA+sFS9Gi2+AtF8atJrpNcvmEJ05XwpxQ7Pi7x/f66UpkLWjispsWksPvuSvv0J/33ddd07Xth5tXa4dt7Ru+nOsivbyOtaDLfxRrKMbxXN5ff2cF6Iip0ae'
        b'8spQXzvwr3d/FA5nS6c80/XQTnQxfcWHl+7VPSyRfBlzd9mz2YMdOourSsz9p5VPXdB8Wdj80rLoy7a1lyfXvuSqFq1jdaZE7UZOWJrKzcv173r86wXTNId/d21++8aB'
        b'zGHN47muBf4/amtWLk+pct33yaeqdVMDbs/eLlz/6er0yi9Sjg1lFUdr2VccSc0fKtpwRuudy3vWhb+1xcgpRW8gxXjrjKzB8/t/35a1v+HSnMSqKXfXh7/eNmFpbV/v'
        b'p18v+j1pvcPgsMsnZt6Dxcun1H9vMklWMrfsO+G1i7O6p+ioHFgb6ndUJPz9rSLTKbNXuPl/HbjaK8Rie2jYxBf0dp660Nj0znOthwqDW7ZcDC896ef+8WLfdYWFV6Re'
        b'VSEeb/WHvfXdNqNl6dVTLV2tK3/8ZI/vx3MSf9p/rb518cdvBK6YZvfSrw3/LjM/+uzsK/MPzi09ePh6p8vDtUYD/g4FkZc/P+kU+sDcdFnT9Y1tay90LM83FNz9ILKs'
        b'JDpn2/oVRxu/vdH62oHe/eo7tx0bqIyzslxdcuanhM0umz0czq50MtQLG2gx3RLa9fLsfL1t/a/dOPrupbjBI62r/Z0/LP7B4ME5LYfO/v2HN0+YltO8LSMx7Zv3+y4l'
        b'rK2dGfXjwcrPJfsvhLVffu+GnylsLW++om81ofn7ILWMF/Wbs273vnz/fRf1at0Pe9rsfzq7QiC5NmAf8+8jp74KvHDlm5jBLf+K2/X2jZ83HrxT1Hb82R0tUXEv8KVV'
        b'zXnZgXczuv2Kgpq6PR/EHnp4efj7Qr0A+2kL2yQaH90Nci96//eCrqs931yZERrS6lG0+ObKN6Ie6n3+692Vn7kc7PlK8uLtY388EH5r/2zy2YsrHoQ9yPlq8aG6P3je'
        b'xeK5mi9LNKlbEyPE4PWRdSBgVgYJdrGw2UnucChLA4moxdQ7BN8zWcaiddKkQm7GJ5ng0B84IqAP9ssNDoESMTzK42C3LbnfliJOKx9HWoMDSObgqcEDO9mZNqCAXpu3'
        b'IenykhSWgU5vAZJbYaUGC4ZgO2ykll1NYNgbOwnysvXiM/yN4kwOHo2BF+nV9kHf1dhADmTZjYbbQSJQF21yDotRCmUOqE38jFhLFhZiBQB9NgBKwUkpCVRTL2I40MeG'
        b'gRO+VM9WzM3ElnEKuzgNAbaMq4E98sgdaNPIl4OBBIwOGFAXcvAS2J9KCl4ER8B5H2KMg2qdsMCZBU2eIJ/owOJgvRVWgWminYTLZBfDllCqaWoUehMvSiAfDiicHWEv'
        b'Sk62EuP/Wxubp99GqvzNy+GbarKNkUnh8YmRcTHkjnjRf3QYrvjP98NXleRWl/5w3B/KHx73QPnD5+4rfwTc78ofIfcbX8j/jfxV4X5V/oi4X5Q/qtw95Y8a92/lj5i7'
        b'q/xR5//MV6eGPKIf1HXUiGtybJ6jxlrwqBNv6vQbOw7nc/jmGb+B75XpPbc2q8viyzl9njZrRvKqEeff2JCII5/UyF9sWjSNhFnFaZL6jS+yQPmnsvxvUf9+5W6jPjqn'
        b'GXKKm07eTV58YtyYy+a/OEETlPY3uKxBbH/jjA/bv2B/w2RPPPsECxzCEZ9ctGr8QSpgDDeAXniJL3JLeswLrZriVMf+IsbAIFk53IyLVVN6n+X/Ve+z4y8c8WWjiHn0'
        b'wtHU/+nXnvjyG7WBi+X+JsT1sctO/I97rG6BP2EZXmWwF1LrCAETYXs83ZbJwMolVsUS88grrTGsqM8GgyatPb2CPfFG4iVgnHYKrUFnevw77EKeDPu8OT0r7esIz8hX'
        b'Y60//ipi3TO95dkVjXkz89trTheezjWvznbUYJJGhFvmXTGxl3BkV/OA++FBH4UDHaErtxJ2TYDloJ+YTkavA9mP+nCiOn7QCZphj8skBfDkCRfgN8UbN8Vs3BJOuC+y'
        b'1km43b+01pm9ImtqWLdjSjh2yByOvT6MWqaNKVlB92z8GKrnxhH3JCVxT0SfDDC/5/qXiZvJ1rzxBPJejMn7lCY8QbyoeYISOSrlMYMyH3A8FJtuwDIhKAItoDkMI1In'
        b'imG9+Rwi0VnD4z4+tjhqTwmfEXpPNuLUQCGsJRimeUhyrJTCg/6wVp1jOB0Wu3DKIwSzBUk9ZvMwUxvhm+JjgEONEtPxTqmrj6+/P4bXiXaDjgBOBg4DmiVwmZjhb3Ag'
        b'IKbMmO2MDAu501r7gjVSUnkMN9E+jGXMvyKSAhcmYGZYGGIO3FfbRMwk4LENSOLj2KZMhJa6+o1VrVOeYWRYBNj3/NfBoRl3t/IYXvZzAtZKcy+pzVtDwPy8SY8U8cYk'
        b'Z0aGeW+zcIdP0ByIUe3il/5F3huIVGEi3CcRsYPxE9H3ft1v8AmaMc1THzCaMW/LMJ+ut1/3kyOHPsMSPTORM5Rhed58/frgUI1MjZQQwWGGEdqxVdeHZHjgvsiaTbTX'
        b'7dbY6ERvbttp3qe3N5FziGDJI2HNm1ov2b6EVpGKsQrLzUr/nNTbXfftm5hoFmxgJJmHQ8h3mi9//CaiJJuQasbmXy+Trxxe4RWjHWO9ejOzvuMSad6Lxr8Xr9O9hj59'
        b'zOQvX0O+a/iorPjSg2so8yfMvsoacgVgFTQfFnsRxJMjH/EmFYtAMecdCfLiJ3V8KZCdQsXuT3veI+i1pOuL1M/FfRw9bfDW4QYbyYLv1SeXzwsZWioNfd/PalW8gH3u'
        b'eZn3tSum2rvzPl1w/sepQ5yT/buVh6566n199PUGN5cPBhe8P39Z5j1zdgnwVQ9POf/qa/yaWNfAVtUbR9penn1zguyVt77cc9/P/sV7/u9/Ghfxxnnjgx//Nui2KMwu'
        b'afiC+KPeu1DKllk2faz3Wvn9L2q9XAcWlNiHRm2D0vZYp6gmdfehf92dmx/i89r0tU5Ddr+0ug0b3g2Gv3ammGaUGwUffKEqqPyZs/nmDr+9vO39Z0/vG26pjn/XYXuN'
        b'87yrSZbmKvHLQloCz+Rc1/Xed3pvR+7llrTNst54z6qrS7TiW76x3hBm8urbEq9TF4+bVu2NWfOtepvsmrPTPp/Z9fFz4P7w7/Rfu8vTjLu/9OGzH//7q4/P/awzcOhS'
        b'reVCp+VD9qb9xat2pU1fceH0vLM3DDL+lfHb3szo6h8/efHDh9Lp+nVv73r2i9qB514/7/LC9F3zN6aemfnOwJ3BNxx35K3fxWr98tWvK79944pxb9Jbt1755sDvi2tH'
        b'Enwd6+3XTt20s6XzHedJQ7J3amUaP/wxpX5vnbbKPYk2BWyUw1M8Hwm2jhQyQnDIIo6ziYAHKTt6Bg64YUaOgh1FC9aCci45EZwjTxeDAnAKm7L42TIMHx4DJ2ayoDMV'
        b'niNsZSQsNSVsoxcsxYg3kZ4jaOT2wAEnagXSr7pQlp6ZCGozNTRBmZYWPKOeio5YeIwH6pdBCsxwh2fdlYx0AmiKxoz0iC5h7UM5cAQW+4FOU3gG25DnscvnwBPEFkED'
        b'dsyTestZVqHzvCBOP8KOGqZ0o8bkK7lZsM9kAmJnzUSUER7QBH2ID5ZXqAo73cTY9Lxum5yLhkMmKKvEDlsuCeFZeDaCswwHJaSpC+BRGYYvEMyLJ8zDsBcpKCc5RfA0'
        b'7MEFF3j5+s+1EzBicJqD9ToTSJsmwSrY4OPlJx9jkBe9nosBR3RJsZuN1o0ecajU067cBJDjTjJuTlqNQcABvhI8cR1gvwunD06gBv53Wvp/Ygo9jk0ePfXI0Xnsbxyd'
        b'mtP5xO0aZUoNiUM1EYmgg9lNPmFBMVNJ4+FwWeqIPeUTtlSTvCtk9XE0HsLWahOWVB29jRlQ7r66QJ2wp2qs6XWhHa1FjRzUaUZKJlRwk58Smb7pJj86Mj3ypmpcTHp4'
        b'enx6QszfZUt5aZNxmSb4l7HyDMf16P/dM9z05hPOcLyEloIeUPXIGa7CGPrBqtV8fQYc38iN4d5wq5SMIbaFINpwNpan9IDA/SUPCE9kDfnM495PJJSPhseEsBKUbkBi'
        b'Ikap40tRROW6YIAHcxYuj6+J0GdlWGT8ffcvX0d8GXEn9KsI38hvYtSIpxTjcl7QK7pjPKXwnmqzcFMDz9V4yrP5G5SnvinNVEkFfDpnJuONX8ZyZtyjU4szh/7dqdWu'
        b'ecLUEi+3I6ET6IjJJxftdUXyCbZaIgiB2Xb/T2b3ib5teI/NLs8/PqJqj4BEPjD9ZDuZuIiE2Khoz0jsbyhkFo+ZcoPn2Rb/F6dO9l9NneaWtCmPTt3kP5u6yeOnDmde'
        b'9ben7vBTpg60I8qW+o+ZO0Mwopg62CCIsNr09KnDgut+PHnsfn4s/79dmnjiHo9YoeYv12zCo+Cgjy3ogTkKDh7z712wm/C2H0ZO4ZoTHoiYlNt7z6+6v4De7s/iGP7U'
        b'THKRz9cLp1fefRsRP6++QI1BE3jE2Jch7P8eeGxCMOjCtJwHmkMZcAxWwy76/mYVRn1TP+aafY9siqNuUWAtGACHgu3gYamnlzCQxwhXc6wTGIk//OGzfNlW9MZ3v/SY'
        b'lLhocjPVl8bVPSgQd55d/pHz1aA1RWetEuJXxvvCSbr+3u5OOwKS3W2MPtBVbw+Za+jsP7NN/9pZWHF7tmvPXmeD7QXw+VWVV6YZ32n2+doqclti/esau7VGlt2DS50P'
        b'b9SINhoZuu146cWF21+0eshovGi6RLVVIkqXt68TFErtkIBZZI11OkJQy9lZuMk9f/PAOQWfpAPb8TGOGCVfubtZWACqeEQhhAMubwRVONRfCWJZNGAlKXwFPLtIjosF'
        b'Q2sVUbaPe8tDSMODyeCUN2wBpwmMuBAxNXs4i83Tad3V4Iip8vZO3Qhcwrd3iKfYT53l1i81AHWIr/Ekl3B8JxZ0e6mQnKyWA+jHTNTozSC+FzwM6x9brGhZ/anF2E11'
        b'vPumRMeG49OT3o79jRUsStJkNTkSso5Dh/sDbPOID3lsvaJc19G4Hv4juK3HGsqlmeM80YqWkSLW/t3VrVv5hNWNrxVsYClx8Q4KE2Czg6cXOn7pwE6BeXzYCtriHts+'
        b'VeV/ZUaPxEar4lWpV6nEctFcKUuuirhR30SxomheND9PlMuu4ccIogXRwjwmWiVaVMqtEaK0KkmrkbQKSotJWp2kRSitQdKaJK2K0lokrU3SaiitQ9K6JC1GaT2S1idp'
        b'dZQ2IGlDktZA6QkkPZGkNVF6EkkbkbQWShuT9GSS1sbx21CvTKJN80RrdNBTi3gmRieXaWbL2DU66Cm+GlNF29uUaDP0hm60OXEFYnlTxS8yCRtK/mY3LhIPDuVllkgf'
        b'0Thl4yP1IO4Tb+aP7aqqiq1vKSN3AEVM/8gQ48NRVbm/8v/q/vpb7n8MBjWutaPBoJ4WegmvFxr9CX/CQZ4iaRGBS5eZxcYnPCGO1DgKwzT+pFtBAnybygaRdR+IY87Y'
        b'hVGomWdGJNrkC2ztWWY5q+KEQ3QT2J2eRqQ4JTUYPVG8GCLC1xM4InOJjyXIJQ6/NpqJ1EGPmPqcGrCcSOPwwrII6rIHHJhPtvMd4JyrFLtIoRF2w+eTGLvVS+WGdB5B'
        b'oAHLWn7UQ7uUZfSm89B5lAfqKYSwiIFdPrO8OYb1Bh2wB1UFc2EeqXU5HAToOC3DkZZXgrYodia4BAspxjEHZINOH+rVH3sYSBQnc7BGkC43cpjmSnZgjFwu9kUvaMJW'
        b'2AMbeO4BYJAUsHVvqg/o8kTNwvm1YDaotuStAgXmtPiWFSBHLo7hXlkgoWuA28muo2r/GlizDslxNugxx4gMcYABDmTDfNBO+uSainYOhfsoe3CcBEjfu4b0KQwOrZTH'
        b'MWenyv1LiMOJ3YcI5IJqH+Jcn5vsvYF1mA36SHkLnHbIA9SD4wupFy6YA86TlkYswmEsRj1pbSfh6VfADnJDNsMIHVDaKfh6y/aZJGeGWIz4h8O6YHKWTTJnzBeBI+Ss'
        b'ZibxGZFIlcO6+KgVwfiqjhgoNq4AnVJU+jhvWaWe2GGWJ7xEslYlIl5hU5MKtm2YIl1P2QK9HVPkweXRwB+mPrzWr6IMSeNeUKdw4UXcdy0SEwdeJaqkTyHgPGIO5P67'
        b'VEE96CQOvPrcqJutPm/7x71sIUI/pAxyfJ5P7DccQVM8JhEii6CZ0vTA1nW89fwl8Xd3fcbJAtA2fWh20+6DC5LgDPV8r5pC3enxf+hJBc53bRYs1ir32JStblJnVjl0'
        b'Xeyo/6XONxdOflXqPfOO1tW54gemfne+cnz1ucN+iS/XJQpM/f8dD+tNZl8+93xlaGLTB8maNS8aNVQ4npsTph2xd6dZcpRD1uuTU5Lfu929KS3wxLxrpXfr5945dqf7'
        b'zvDmU85f/BTS43Fr0tQPA/ZU7zp23/PWoq09u16dvCXu3ah89pWtbmrb8n4sNT8+kna6zMR14nb/636fZdb8q3HK/O8dVV577vUHTXMORfre+kwcdmO7c/R78TNS/a/7'
        b'Xvd+y9Xv2C2LyzWDP2RKwr93P3O9/233U5WD6Z+s/zip7+CVFxYXW6/bcXONqthqyNBd7eeiz+pnvKGz9JanYbxhi+0btr812S596OHlZv2VhdWDJlvdz0ZeCnpnjbir'
        b'ocrjfQPv39RKWv8/3r4Drsvz2v+32HsIqCi42SoogoqCgz1UQEEc7CWCMmQ5QKYs2XvIliUbBEGSc5q06U3SkTRt0iQ3aZu0TUzTdOTem9sm//O874+lmBh7+w+fKP5+'
        b'7/s+z/s8Z3zPeM5596O05n/c+Mv7qffzvv6t3K3U6pNTPzNew51MiwvcycMQrIzikcgeH85BYmbi5+ZuYsFrUriHI0oxIuzA9nAeAOWIMZurJ8DHDuRhdBcWiq5dX8Wj'
        b'qzovC75rShRkL2mcIpE/sZE7q6MF2XIrhQL6I/luDm2Qyxd5SYpiwR5zV5iAWg8xB4eNoImLaJ73wEHW5mReoh27opQgwnqcpXuZ6PVzxTb+MCB0J14ROkRgJ3cMJ13d'
        b'i24jOYeTMDov63SwWbIXGnGYW5X10K4MhV4k7PYeFohjhCcdYYAvH9JAlnMnV6fVnRWUGCXB0CKE0otYxEdZRzYStp5vYkLSDO6nsB4mFcg3a4fS46fwVgwXwFoi9DT3'
        b'iKEVMmCcW72dAVjOOXK9FuWeZroYJsOgnh+lyZobZUHsyXkrHadXP4zN/PJPxUE3aw8hFXzQ6Ka0RYR3YACKeeRcBCVufGsfN6X5WhI47cLXk8k/Cz0LpWg5WaUWr6Yg'
        b'ToRCJb4VPNxkgQovJjQKMIsdrZOVF62GukP8O44F0Oy6WHugJZJDEzvFTHZjP0deysGK3Mk4TnIYYqkSUQ9OBkEd/wLdtGK5rB+9VDazyEjDYbHjcSxM3CZgWa87eHtu'
        b'hRp7JEsE9klyGjhix5dmqafXKWNLPt++nh6X7xYh3ou1cdIKF4dh0ItVoPNaIoQ0bcSsnCJ0clNyw15DdRhh4HIRYWqqiqErwt5Y5uleJ4XnPfDBzr5wqP0+k/nPiNoF'
        b'NxQVWeEIZS42LM+557iCEWK+STb7USYIrch9IxKp8kUk/qktpyp1vrG/Fz7nf75Sl5fn7pFd+t133sO+SVOX4sfHmiRIjzKtXe4SkH9m56aIv9Vi2WpdYiYFy7l6VpNC'
        b'kKn/zxWOLz0x52cvZr7+20rPv0bz43shLIyw0AZhI9d+QApRF8vxP3/fA2PhO3LnE6IiYr+lE8FP5yfEDz/fiYDdFZSYFP/89cYl54Mtg5867BsLwxo5xgRFGEaFG0Yl'
        b'8q1ND1keWliF56uHf17wLTvw1sLI+lwl8fiw0KjEuPjn6vfAjfaXb9vvtxdGWy8djW/w8HxvJ+2woHD+YlxoVHjUt2zruwvjbuOq/gclJBryN4X8KxPInp9AWEpYSNK3'
        b'dbj4z4UJbF6YAH/Tvzy6HH8u7+lj/2ZhbJN54kpcwlpEZfwDnrt6v9z50LBgIpqnzuCjhRkYcFzFXf38rQrC55d9nlqfOvAfFgbesIy6n3voiPmh571ITx3604Whtyy1'
        b'm9nKzxvNy4dfMjqn5R5PkBEuJMgI8gVZgmvCNIWrAs4VIOTMf8F1ofeS31dKzmGPfdJPLv8tyTnPX33+K78V2xtzFJgcGcb1gE6MZI22F+kwPoxvZ8H1YI6NS3zSq/CE'
        b'Z2F+s55w/Q8fOSjhmgxgYfqnrMXAT1vDP4ghe7hL+IbOp/NNBjLhIaEy7YPblxj5PPAdXfOUsve586evmap9dhQiuCErl2Ywr+UW3nQx5SY8Iizx6eXy2aifK857LJ9Z'
        b'mwsylVfQ50nMg7/a2BBHpfgPqxa9HJBzAMsez7HhrAaYlVWC2ZNO//+COk9mc9HOXrn7AwkX1JketGBBnejwR4Fjd4si+LCOWLBxQtz5C4/5HW5zgXHeuDHHzH1Lt9hc'
        b'5btiPvH5z7vXqkrfvtcJ83tdIHwsvYulvSwO/uXzbLn6lytsOZd5P+LJStmssOmYg+VP7joZFGzXTZTw1mV4KC37rIk9QVgHpTxNSNSE0C2CYv4U0vBpvLM+kL9PYiWE'
        b'UbiXFNWV80gmgZWW+kL10W9DIyOcQ9yD3IOiP7wrM/Lr1W/Unqj19svY//Ka3DUv/7hf+y1b9xeVG/8oGJGV/89k5Sey31bOhIsPl9IKJ69Ewu+zU8oiVTlFUZrGE7vF'
        b'P7748f1ZPuifnmd/VL9eAWI/OYGnS2UuAMf3ChAsBOC+R9rkVx5PCNbDLOEvgccGJImX+4cTDBMSo2JiDK8ExUSFfoerVyhYScfIevo4cv42x4T04A8F6rSKhldqw+I8'
        b'o240bhAmMIha/7+bPw18Pdgo3CNIOfwP9JvZb2TL3Y/OGLsHHkgYNioNNdbM+Yu/Yod97xvrolfvrY3W26vXUFfgE62nM2QRKijYYRYY8KNjaPhi6UvN0PjaiQ61n4st'
        b'a0ZlBCPquj12XxnLc64OqIJOGDBdYrGqwoQ4GHOcYAZGeF9CAdTvW+IWxjoR3JNJx1qye7kSOKegcol/FSZFF8PTIQu6+EKkXQ5QaepKBnbrY35j7JVWgYXBJLy51IO7'
        b'SYxTWn77YIZLDMI2rEuTNq7Q95cIoUUCE1yYLBIzoNeUONQF+iW7DgpkY0QbjTZw/ouTxL0P3OhzM1mBBOegUl8IIxvhjlR/fWdoTD4q4Ty3vRwbHfm+qk1LwlVi5P4X'
        b'cWVEhJJlhuP84xc13FOmtKjy9tKl//s8/KX5xbeZsPMzkdZ011qp+saSMhtcjC6MLZGYWXDMFxbPjrW+Iz9vdbwjPw//35HlkfQ7sjzEfUd+HnG+I78AGMPn340f/1/v'
        b'TrlEJG2kXy+wJWODsJIYymJ9oSjg31P4QlWirqQj4rziXpgFJfOKRR0LiHQVoUQEDxyNntDpmtK/EwoejzTKVupVCkJFxSz2JpenkqeZpxUu8+wRRv4uAh5KocrZ8lyE'
        b'cXOUIExeGtOTZ88PVSkWcmnvSvRsSahqqBr3bIWF72QI66qHanCfKnIz0gvVLBaFbuHu0eTu0g5dla1A3yvR9wJ2RaUc/eiF6hTLKmgpaIVu5ap4yEj7t6jkqeap52nk'
        b'aeXphSuHrg5dw92rzD+bfuQrFWjOa4vFodu46KoMF/pjHYlU89TYiHnaeavydPJ06X71UP3Qddz9KtL7ubsr5ULXc/fLSO9U4+7SoTsUuPglu0OVe8cN7B3pLUShG0M3'
        b'cW+pFqrF2dJG76hKWYT+CooIi/9wF23QMmHvYLj8CqYh6O8EwyBSDktVBgsyBiUaBsUzz83lpCjigmUPCid8z10fSl+FJDKLMCrRMDE+KDYhKISZxAmPxSJdEkkFxcVL'
        b'h1oYJShhwZgi3RVrGGQYEXUlLFb62Lj41MceY2FhmBwUz1q47d37ZLCT2WmPveCC6jt01MfBwvBIXOy2RMOkhDDuDS7Fx4UmcdPdsDzUK/XFxdP6PXEGY3m5l4VSL2zr'
        b'F8q9iPPFz3T6gjDzh6cf3yRuuR4L985r8ovzr/VcEd+FVWUGHG3t0q1Y0VJj+89tW6iFoQvn0gqNoxmRZWcYlhKVkMg+SWarGyz1BYWtgC6kE5Ka7PycnjDkk6PYJOmb'
        b'8CR6XFBoKJHKU+YUG0r/GwZduhQXFUsDLnV5fQe0EQtWimKreHLYOn0HXzFvviCr84LfnJB1sftxaMEKVjv1hLO753wVNpjDPCXs3IqjSTsZLhiCNlbVVYitKz2H7pT6'
        b'/q9gnsK1NCjk471VMLIdKwhzO0sEUAJjMtuEWLsDq/nj/5VeOMaODydqs+PDRRH8IfQSfJDibY5dOIKdlgKxhUBNFvr2izZDmVUSiyakQA1NYkkvMSMGluIkx/guYnuM'
        b'ZaBMT9qxB2fgAdabilgYZChBkABNMMJhvUvJYoHkWCatVKBZoquNIIkdoWFlPNYsRjZPYD7XqKzYDEs8+HK0x9W3xclhxoZtfPg+g1V3SLgsw+LtpnibtcVuNI56TcdH'
        b'JuEX9L2TiVpY6b5osYNy7o3X8MGnp2LklG0dX0gyMXihFO7HW/1Cov8jvUfBE690HXv3d4pWe8bDTQ6ra3615QuX/A816q1s1/yhQe9czpSRb9UXe1dP1F2/+Jp5QPfo'
        b'J8d/cTcRqj2iXR0D13346p2vdeyOug6MAq7pnMzL0li768M3H26cOdtx+pHh9Xd8gnXDrB+Fzg398u4e7fBNr/qGlVj9/MjVzP31H76j+7dPDH55MP4/vr574G+/9K09'
        b'+5H/+nURGpq/P/MbLS3Tuf+eeeWR5cC7Nv+xrePrR38u+dPvVc/ucYh55QtjbR4JlkOuOZdEgPckAlGwcCfWHufN2hys0+bjiQvBRMc1LJwINad4kFmJY9C62AkKcqGN'
        b'xfI3qvDlLYvUoMp0Z/yShKtY5Atj0obfg7HFUKcSPPBikc6EtRw89gOuMo4K3lyWkYU9cIuDx/Yxpm4nYZDP3jCWFShoi6CVvs/ggkbHMXszFhJQ8GQEYMLiWG04AmPi'
        b'4xv5jPldOOxtuh0LGPyFwTBZuCsyM7/ETSzSYjcWwqDcYoyVBVihEbL5MwIPsUzG9AbOuXq4k/m5QUiE2A3tHDwOwDaYms98h1lVruFDJEF2FuwS6VvzkT92aIR1jDCX'
        b'Fej6QDFMSJxx6CJ/IHYUZnQWbAYLzJDVEqng+CoO8291YdE/aDf28nRj1Qf52WlAjRhuh+zlF7UUb1mw8N0C86u6qXuLPc7G83Vp7wSG0m3sMC8rNskdZ4KS7W5ypuZc'
        b'YUxW5sQJhuXgNk5AA/dEeyxlpVAKoMJ9af+zAezgtsnAFceX1ZcU6GmZGkrOYd4G7uhZBI6zOrXbaT4wP6KsQAce+NGT5jAX7z6ZtvYsSeUrxetOM+n5fcwJW3muw7gy'
        b'V9idFXnXFOp/wxLplbmEe/1vFEXy0riavjBNd7nSXrn7+IJGXhJd+5YgpZi/doWY2lql5zBJ9H62gknytHl/n+CHzLd7ofcrSb3QTwy2EGezWlDyT2r1JRr8OQNvXAzw'
        b'2rfFhA7OTzF+N8uPW6pwl7nBOd8il4C44Ft8Vkf4Ew0R/785wrOJkHKEj73W/Ho94dk0tVjFN8ZtO9D0acdpvjHuqwQ6CoSTliJjIVcYdiM2QvPjjAt1CQIdxrhyeP87'
        b'/Nbxeaxd69bHyCEhJOY8d+jz+zikDz8PKyj3rOCdZPQEt/fi1KJ3cpz94u5ljuWmS18Vq1f0Teutdzqgagfj4d+Rts75zPKE3ztt/QkSmiejx0+UJNnR79gLHdgrFejh'
        b'LgsineUs3nI3cTWDXh8+fZF94OXOvEDQB7eUbDdjS9Q/zh4WJTDWiFGz/jTQ4jfmLz4KfDXY6GOzIPegmPCY4EeBfwiMDX8UWBDhGsQTSKW2vFBjm7E4kesN0HgUpldQ'
        b'Jn5Msz2mTaDEgCvwexFGFRayjzATOzyWFxzHWeD7xGBD/KontEZCAEd7OG03n8vw7Yph3q0ef+tZSXG5v/wJj/1yp7nH85ClZsvTyHLIVPY5qJLzgesd2gojqi6Ql2ws'
        b'4rDywVBs4gk2GUs437m/mPtCSRam+Xv2q/Ke87mAqL1mtiJO8hypFzzhOf913c9rvZnv/CrnO1/wnIeMvtytEDVj8aTv/FsCHUXC53egn1RXVJSk6T1tF5f40b9jAoee'
        b'Z9/Ue1fQrE+dDIlF5tB7upBg+fcsNZyEhAyJCZkFMSF+5uzrriesSKewRDKfpXp0qZ/k6fb3xfiwcN7WfSIFZgUTOT4sMSk+NmGvocNCz3fpCgQaxgVHk9X+HabtygpR'
        b'xpNrCeIf4UuQ/TCM8zzge+yU+clTy5K151O1IWOXQjQUO3M9SqINsIAMPeiEiWWW8HJr74SSHBZDAUxFZQb/jyDBi2589efvfBr4KPCTwFeCI8N7w1gswO8FPxwqHfa7'
        b'm20sY7Tp5Z+++qsf/OrFY+KOC4Nfrb6gN1qbGe0/UjtaV6jt5uddaz+yu4hjheL/0Dj6pqWxLJfBuHq3oSk0uSwxePbY82YFZsPD+czNIJl5uyICKjmLZTtW71HaEbXc'
        b'1uIsrRk7LqtSFvIU+EzvIxc4G61zPw/5szArwc3dM+LCPORXOi3Ce/5Yl8jlAudiH7bOC90sbH6sAgQOQof9Mv59OlxdWhSCnXGR0oxoXu19L36+pMydX1Xly0OseYyV'
        b'ljyeG7VHmrjG+ckXofWKKqBHxF+2CKid6RE+z8P22rUrsP23zPXpHP9EesWzQoJI4vXxFXk98ckkl7jw+SMT/37Wd+DHfEbWXzlgR2h0n2+RMIHpfPvJ4k8Dz/w+/4Wf'
        b'vkg8WN2au6FwZ22m1TrBdpCky7xjLOKQwYYUUm3szNGSrNKjOLAGmyRp2BnKh9bm6Oehm4sH5NpITyBwxw+gwnU+ULVyrNVsXj9Zfk9qFtxgSZorUoZ0a/hRXETzENdV'
        b'tHTQ0OchTtX8ZyRO6RSMeb54Ry4h6ErY+aAEz6d7jZmrUaqdZDlbSPZ7+oyJaj8MXslnPE+4zKEeKq1U/0xk67Dg/A9LDGK5bEF8Ls/FuCuk7lhl+fnn/l/RPH+PdLH2'
        b'Mtcy5/Y3Y/7ki0kJicyfzPNgQmJULJ/hxyzcFR3CvNW7LC+Lef3p4Ss5oxfYjc01PiiZXy565+/gMkbPT/qOFT2TGODCYRPCjIUe365fsS1iXsWG4zRXJzc8FcdN2fkj'
        b'Z7KeFLEK76tz1VcMbL7iy7ZIBJI64a6hRIv3OI9sF/EV/W2YsSnGrGLVEYFP/OdEChwA1YNyrDX1omedEKTGYz3exO6oz5V6xAmt9O2ZP77k+9pORZGDssxPW0Lf8lVX'
        b'+vRtpZeUfpVebX7kp443X9LRuRdYEaWfnXgu6OOu108bt3Q4f3Awr2KPnabT/b/9KNRol9nn/b8bO9S2zXZtpdbc78uKRrSPvH9YI7pc/d4b63I/y5IPUU0qSjj2s2P/'
        b'/aOy9trfOTYcOp5Yvu3kwQLduB3nijzeGv8ZfvYo6UJA50unoovdLv5zvGifz2d/G0yqPXug9k/G46rN0gOw0EIrVjF/jBQaQpmex+pt3JcqodpLD2iw/Pr7ptdk1/OG'
        b'TSGOQbfSE2oecwLlocSId5o+0A0x5b2L0GXOORgnkS8zAjex0sLUxELailJhn0heFVogz4t7uKIg7kkPI0xINI1om5F3UZ5wCF5yyBVnrzGv6hFprxoYgzt4h/OLbmSC'
        b'lXOLYrbZynrWWPZZfXTvyEmPxHLC9dj3Fq7K6nwDRUWh/jfqYq5jiFDCf/KNRKT+tUSUprOC3KMBlznnOFTgLvpuBEEmxOK1izDCk/4ZxyT1oe8pqQWZOv9YQVY/Zc60'
        b'rpxXkBPWCgtJ4XxIfx9LCpDEBMVG+DiGyC1hffZKmvOsf5LJb3a6k3myFLlgLQsQi/LU8tTzxHka0nigZrimVK7L5SuQXJcnuS7HyXV5TpbLXZf3XvK7NBZ4XbKCXHcI'
        b'DWV55LFhycuzelggjA+68THCkLj4+LCES3GxoVGxEd9ysJOk7d6gxMT4vYELVlUgJzGZ/ogzDAz0iU8KCww0k2awXwmL57IkuIjwEw8LemoE2DAkKJbJ8fg4llkxnzqb'
        b'GBRPe2EYHBR74enKZFmo8DEctmKg8Kkq5tvUElsIFslMuBQWwr2hGb/KKyqZxfMLsUkXg8PinznsuUBk/DQWDyIkR0aFRC7TdtwbxQZdDFtxBnF81vf8OkTGxYQSYS/R'
        b'nY/lhF8Mir/wWNR+YdMSDPljFBaGXiyPNzkqgZ8BAYDIuFDDveFJsSFEHnTNPPwOXPFB87MPCYqJoT0ODguPk6rihYPUPBEksfR0FnIPWvE5S2noqSu5kFe31/DxMxaL'
        b'ecfz4z4t/1j6rGDL4CefsvSkxnfcz6QE4RZvL0NrK1vzndy/k0jSEBOGhs1v1fyziPR5Klk5HfpIWHhQUkxiwjyLLDxrxR3flmDIo97U7wI3Uspkr3KJzAr67Rmg2TLM'
        b'oyYVessxj5EnB120FLFnvUmCJekBYZwAJuPwIXdgWBUGoBYKcUrpymWhQIj5AmzEARNjId8YoE5Pb8MV5npjhxhLhIejTyWxTjLWgdhCNxzn8ZKRhbkR5m83cfEg6NTr'
        b'cwlHEk/ygWuoNIF7ygo2OHkgiWtIl8t1V1gat+ePCPLBdhjjgqch5+ShFdqDOAxVfEpZsGMVDXos0N1lr7eAO8O+GvO5opEsXA5ZMVzEnM8gNDM2d5UR2JnKEqSq4p2A'
        b'rLqXiimWywqEGgJ1gh3NW/dxj45aKyf4lbUBV6mvyWkTX7jkikgi+MFmTa7M3yc73fgPD54UC0LD2QIHxnR5RQj4HhgtWEjmVzspIqUEnBMoBWtxFa+4O9T3yQs6DLYI'
        b'WGn23qMqgiTm6TqmC4Pc2XhvZ85d7EKzr2Kt9UwZ8lwI/tOXzmau7hYu5iayAla66zI2bUxiUQETwpx5y5ErdNgSeC0yJpwEPT7OC3FgyMQpBWi/CP2OxvJcaD8ueAc7'
        b'Tq52cDF8eQlv81H/oRPQsAG7pEfKzwm306tl8V+NbpfhjpQLoz1k+BPlMOzNpUJcu5qw9Dw5Yeq77ES5rQF3pNoPW9kDS8yggX56JPy5bpiCLv68fw3c3yQ92X0XqqWn'
        b'u7mz3W0B3OPd4B4UmFoYQzlk8ee72dnufdjP9aYIhGFWSnL56UtJMjt/yR/t3gNjxnxJAuj2ZFVSzF1DIc9DzNckiLvBn89vwUksYdmnxpi1mICaro4ZfOucoZgTBEG3'
        b'Qs0TyaV3uBxsbN+XrLCJr0rAlSSAIhzhR63RxhocsJFWJeBLEtzkRvVH2pzFigRT+IArSYCzyLc1wBEsV56vSrAax+YLE7SIDwWFcIu7DwrhLp/TGgyZ82mtfkIs51+r'
        b'G+5DMZc1i20pC4mz6fLYxr3WKuy+yCeFQAXOSo+8s/PuOL2Wz3IpsA12c/FYDdNL/QbroJmniW5sNvJOgF5z7DpB2FocJtynFchNTBUL9nmTIVXqe4y+gBFXWXMhNMMc'
        b'FnBVBnzDJAKjKK4OZ8zAlQjeFjoZ5RTElZyp8JIIRMoCnFtjYazIlTPDZhm8laAan4TD2KeojMNqUICTibQL0WIX6AvmsmdgThNK+Yvmr0ggRinHsSQZwRrsEmMT5EMj'
        b'XxKgkAyU5gRthSWXJydeVohXUZUVGIkleBNybLlNWAUzLFMIxxIuH7qsfBmK1eKTxAItffEeFezjimPArA5kJVxOUuSeoobjazBLgSY6lsQuZ5NgEzh4TlYmHUa5Egne'
        b'WHydv0Fjs3Se7BKtMLEDbX8p15cEs/GWAV2EBVqKy6e3Hu5JtoY7cHUrnHAaavhHeQbyixKPYzS/o+K9emHcC4SrQNnC7JJJKMsK1GVF14nO7+3S5sggDMYxW4lMqjjo'
        b'prkoK6gQvle5LoLRMH+uYkdEMjTTbh47xjZTHR7K4JQQygTufBW3UgMbbw8so5dS24NV3lDM6n/WC3ECayCDm4I1bUMnGwAqVJYPkAZVHP9s2X01ASfU1uMgfSPCLqGJ'
        b'GoxwVnpsANzHQhKRbts93L18SaFAd+rJE1IT3YzJyiIXdy75FW76KiSQSdjEM149dOq7sQruwr0Cou88VvfoLLf+MrQ7zTjqjMWBUGnsZk7s5SkRaECjmCRQpTYnuZ01'
        b'1gi07WNZVdkznwil5aw2bDMR1BoMsg83xly4IOB7dgj++6D0FyN7YwmvMbN98B700W+pV6BWkAoP+YZJ0di/FvpIK6dhHozSnxnOfHOabMghsUIGTIrHZkEK3o3n21B0'
        b'6EETsr4zUVjnLYjaFMi3/b5h5iRMYL8WT2ZdPPFK7Jv26gMTdr+99nLdZqvLX1bZld1v+7Pcu+qGf+p0tonUThUJ3/xYXelNW8nH4vhLm/70Zzf5A1niwV9rbd4c6jvV'
        b'+/6nn3Q2f6Lr8/GPjSUz5222noh9O+TyzyPy3nOLKG+ZflT3VWn0ZQv11AqPN/da/0ftuVt/sT9q0ieTfLtnuH+/4OMAM6HjR05bfOb+cOnYvhaDk5t7/hgdfdXvTo+m'
        b'SflN1J81dXqt54O9v42U/Gf2z38Gb6q+9uP8EPPsW8Ge9UcUzcNTe11KXRvW/+bhVu9rju7rH76zapfqn9743Wurez9OV/3tm/2/z083aNT/R+GRLb3t5af1H3yknfyH'
        b'X+9LPP6Zrv9nPvdcC/vrKu7pfKT7QZ1r+Pbf7Ba/+wOxlemcy2DdD9/T2dV0NeKE3UfB/wzeeWTd+FtWXzQOlPTrvrXdvyVgLuafBX/ve2vwiw9MXvj17UfZ+kNN8OrF'
        b'1ROigBx/1Z+cf8m3+zO/pF+PfxR3LnLT23bxudlpMQlqg3/6a/CD0b+l1la86JHo/IFNtUZG5nuhf9ZVM3v//b4L2z688OqvG4NMPL+M+H3AiPOdl/4+lWn3gUb3TOIq'
        b'39Yfd7Vd/YHt+6FNNS/+OObz0lM/bYju3fjRzS+yX5vunjn9ksmRr0/kvJbbVXgsp7vB8vU/7v7zX/S0/L2D9pV98cKj/FOqr8V8g9d/8qnu6BmHi74btdqd/7p9IuVz'
        b'Gc8vfK9q/qg9PGDrzIsNjdGDrmE+j+x/GfDfn//lrfyUhuSU/xoRqzi+1uxu+/rAl6XvHXvFbPptz5Dq98rXafnvfs86ujfN+uGm9DURDf9I+/3hHyZ7hO/avz4lMS3O'
        b'5P2vY8b/V+2/fmg7tl8nouvzh3+U2Z/q/uHPDH6i9FVYwyvGFrzjphybzRkiDIbxJTFpTRcx3NGHLi72A91nrkCx1iKagAfmfGWGSpJUfaSXnHfHc1FyL+4SDcwTQ5EF'
        b'DvO1F2Y3rH/SMaSDA/LyVpxfSDbZfSHRDvq2cDVzwkO4AY57H+f65o5C5xOpYVgGk1yeXzL2xZBSX4cD84lrOKzNl3Ptg0lsMMWs7fNVW1niGjQK+dm3wp3jKzqWYhKd'
        b'ccyDcx3ts4VO6NuFLa5L67Ltu8Y/vxKr4Z6pp8dZvIvFsgLJLiH0kKro4m413oWDpjgB3dJ8PM7rBNmp/K11pz15h1Vy8mIW4Ahk8742yIWHbpB9faEUbaBokxgmuEy9'
        b'raeRVqMY60xJ9xW5yQpkU0WbnVW4xdaAHOjmat9GGc0X5eVK8tbTpNi4cnRPDfPw3aalmQ/l0cP4lsy7d8a6Mch5Qm4x+RCL9Hj3XVXyfpLF91n64nY5sh/ahL6bIvlM'
        b'yxp1HCQIe+00O3XDztzgzXP8eZ5yzDqGhWaEG7GU9o+WwsOM1P12MVZt4kvUQRlW2LktZvaZGXCBPpwN5fMSbxNgbIMav0XghdVYy8cIu64yoOHuSkZOwZIsvkIxd6sa'
        b'1kIlB3a3wp15tHtYg7vV7xK0LkO7JVDK0K6KAz/qlKsMB3arTRewbiytP9OCljSlTh7qrqFhlyDdcmzhC/KVywQT0iWEuAh0L6VyhUZwCBscnyhilAfZi0iX5jzLFxpp'
        b'wHJoYuWQTI2xjLuBRsIMcRyOnuI7gtRrnMDCUOghVOfFChZeF5lAhyXf+rkRWu2liIfDO5dxXIUUOw4JLeGm0AzbZBS2r+XI7TR2uRDRbPc9x2+PPNaLoOCQN1/FeRBm'
        b'IvjKhaeJ2eHWdheuY/daRwlxWucFnslLCe2WstqIWKXrspt4SCCHrSJ5AuSFiSyT2us6dvEKMziN1GVxEE8e96HV09TTXBvyllSO1dokxpLDeI+7JEHRhq/MQhbGrIUH'
        b'Frh6WNDgWCuBRtPjXE4XrcwE7SO7ysuMQABtjUigu1sCYzh2kEB7B1ciCAdwKGRZ0U4sCpFbrNkJrWl8cnAGtMZwlRwLuPIvAhUsUIJiEbZKIJd3J99RYS0ccwVmnnQZ'
        b'rbqnSB8HoIS7/QDkR0pTdGGYuIVP02Upuo6Yx9f8ycWBABxVuyIVh1B1VgF7RDBgsJmn6g4YsKHdoJlClbERI6AIEYzAxHZjtX/9uNOiM/jf2Lh7aUQ9KDR0WUT9Kwaw'
        b'vp+b3FpPqMqltGov1IpWFq7n6j/L0//6/6MpryySF/LOdFaGRpNrsc2nuHK/iWSXFpMRSv5bosRO2C35+W/ZR/IG8tyTWYMUHc6lLc9Vl5ZwbnnW5ET2S1llHdYEnJsN'
        b'S68VfaMpVhXy7VFYMZw1XPEaVS7tVpXuUOV+uEbe3yiKVwhkLlke3qmvwHvmF1zl8V7MW7/gJI8/ttzR/68VApfjx1l8MDciN5jFwthckMCHfit4viCBxYfPENBdsg7G'
        b'4nfk52OoiycIQySCxf9kBUucY34CAX8SiI8MKEgjA0IuNsAiA6I8jTzNPHGeVriWNC4gyZfNElyTSVNg0d1TgqsyXCxAcl3Ge8nv0nivt2iFuIDvJWmK7/KwAOcgD5I6'
        b'eBcCwU93ts9fsfywUKLUV73kEWZSl3VIUOyKfsxgFpIw5BoXMZ/j0wMQz+ObZ9GOFUc1mZ+eiSF3IIhzo87Pg3eK81NiEQ6aeizviF7ZL254OC40zMrWMDgonnPk8i8c'
        b'H3YpPiwhjHv29wtwcwsoDWM8XolopfgDPX7lihlS7/a8b5+507/L/ft9nb0rN/4x8ExiJ2t3ncYRt8V26Me/JYOsxBgGoUsBBzFvD5d9dh5G9eZdq3hrd4L7cWfmasR8'
        b'L+9lLtY07FaAYhiAMd4PNibkzmGPsOanQmcCf5eRP5b0laOSQPvMkIRMZ/c0d2e+S0v3u10X35T2aTkpFOi/xuV+hqlgqyncZeC6jqByPt72Zn5RD3eukP2pJ7J5l3sB'
        b'xL4q2IUditxBrBOHDnFNhje6sR7DE1DHn4cfO/sVOw2v98LuG2F+Z+/G8eb7r+rsfbivX7EJELwrEOw4pp0bbXNcIZn/2rHNnm94mXBB+Kbsj8UCw8B9uSGxfIlMfGDs'
        b'xfqkwy0bS4FlIFYnMXmXes6W93J7EUgv4Sdv7uqBFcy5SxjSReo657zYbsedXc1ceVyIk3hbxRXGPDh/L97XIUyycqYCVEP1k9mA2LdfWo4Tb8VD0bIK+zB+VVpkH1v9'
        b'+O46s2nqy47eb/ETpXtu4gjBKmLnEyNzbmY1Qrg+Rgt3QSY8VLgG92GOW6Tf+bIKnx0CVg3cV0FX6imxj+aXsOLSKcGYQGD454isND2HHZfjNZm+YF5zYxnOT2IDE5DF'
        b'+U+gzTdVkGorPViHnbv3c3Dwwh6Cg8dhiP90blsw852cgyZ23G4ynXOeJPppcK6TA9AeJYhip/M5n+Zp4boIrocry7kuJOPLWki0P4etvMs09wx/Ti7Xb6EIKPOIHoNe'
        b'vvrsQCh2eO6TVleVOsKHrkWtcREIE9qI0iIfydod3xe7LfDX9upNb5+9frLjQGXovoL3ulTf7X5d5oxEeEZV0150plT07qvWQQXHN2yWuzTcH1/Q+GLNnx0s3axeznjh'
        b'0cxk3H/udx3Py/+N7KNP2jd8ZtH6QwMjj0kNrc8E3R+/6GZc3J/+xvvO5h63u8Mb/Zqulm6d/sHP//qjg/e/bDepOx62taTy7xdWZ2wI7/j82JUdwjlB5hufmMPhVKX3'
        b'fu90xPnvvgdfjlV/9KcS24/aVV/emKqc62HWk/LZl1+/L1mrX7UhxO3c+QOuL5aExwwG9aUbfZzV6XrZafw3B1dN7orY82F19Eeb91/4Se/AnrevWbmcv/pfmxPesvvT'
        b'a6/kNf71S5fVq8zfv2q27X2D95J3f/W34bfMZkJ/Ezac9372oZez/e2Sb1T9Mr9F8/WpOwVvRbQHVL6Y4NKwbuwnP3774eV6GwPDDS27Kr48evLyBs9x5ZtmUx+MeDXN'
        b'iTPXiyxf3nK2Y82uU9PKVs3Dvz70400+Z372ixf/+fJbP3+QGNyXv7XV7N3BX3Wk/3gw0unzn6R+pTQcdPCDXw18dGPy+MFf7rvTsM69wrzGO7nsy6tJv5v7Rmw0WpWU'
        b'ut1YhzO2Npwk4/uB99Li5zgZxiHty1qQ57bkKB02QSmzaG/hEGdbkD1L2H6Jb0IDh6XpqXEwyT1dD6fOzdeMEMj6JMaINmJ1RCJfpLgVMzavk9aaYFYvjEMz5zHxj5T3'
        b'3GO6eJKOrL4S7qTANiyDHj5rdQRuPdG3jOR2kzVnp++DTuZn91vsXsmy2vuQr4GBFbtUFptXYiPcFHDNK6MTuZsdoY4EzwTkLXaoFMIMZLlz5stha7i5pAUO3Rgngoqr'
        b'hrxx0muDHaY0Ie6tFNZhJmSJoBSzMJc3bedUdpia89XxyTrtYhXy3ZV5V9LtINYe2owZgVJD3wHmeFs/EBu5x28l2/khs7vhrpeju9Sfo2YtPiMbyxlpUEs83MlZaXjb'
        b'g6QoaQpTWcFaaDgChWRv2uMcb/j2ap5hd3M9+2TTsF9fJMHRcN5gvYND0CAt58mLSlrsAd6s9CSzkk3W9Ri085cstSm3+pFVSa81w5ly+uuxbJlViYNunGF5UBcruO0k'
        b'879lu9SmhLL1y5q0cEalJWRw720BGdDBbDqpPUciq5lsOqyFiX8RwWv9G624x0w55aU5CZwtd48pg+9ly5E1Z6HMWVN8Y0m+2w8rJar/jUTElxdVFCsKJSJ5rruPRDj/'
        b't0TIWlVK7xXx7Sd5i09d+hvfmlKiJvtX1fnf6U8dbixN7k+yO9Y+frhhyTvxBpgsb/r4LphDzPpYYnGp/18vsbFkyWAWCyNyZtdpZnwozxeV+V5mlyBzxwcrGF7ftgDz'
        b'CWJ2bDoHRCsYXQyociDVVcAlfsuQmcUX3BdxhpeYmV7hygtmluSZzSyHldJq582sxar7C1myXHLt/3E6OH/PfEEa/r4Vqk1aGB7mM2u4qTwlY4jLHme2GF3q4u1lY71j'
        b'J7N9LgYlsryQhMT4qNiIp06Br4SzmCXzeK0//vvnOpYi78lhUT8oJ0X59KxZzMOcx06mFKo6csgL2yHTUlqB6UbKfLB6H9bwtddPYQZf4An6ZRdC1QQre/hEgSro8F8s'
        b'0W+zdSEWfg2bo1KiXhYmZNJlf/rhS+YFGzRhh/aR5Bs/P+SQ+cJvjjtLJj9Q/FqxLqhLpHHXzSOkOmDzni2v+nz2MNXLczZX4+3wSKu2Ha1/ufYPvztfaVnq/rh7wirs'
        b'xa0/SLAPvpQ8ozqS4rvtjQMBM5Gm//GP+v7709aHXvhByhst10J0zg9/de8Li/Ga4oH0wJSvBZafbFJ+4RNjGU7RiElhDXPYIgGqpfBiP3Txnusxwg+5fFKs0bHFM/Xx'
        b'WzkV4wW51xbBRQnz9i8cfrmJw5yKiSS1nMPrTLmQ5e5xqw3cBFKhYwsWpkDPotcdW2B42dGWf0mDLBHwqkkcuy0T8Z7PIeJJyK/hXXF87+B5MS/PNXFLW/eYBFo+6jIh'
        b'vFwaLRHC368MNklY7n675WKWk7Bn6LNUZWlb3+8rYQWZG/+8goz99jdkRV/Toi4x/8y/qxjkVz1PZrLGh0RGXZHWAJLWrF1WdWgFIXqYd33EpHK+kqiLl2LCmLcnLHTD'
        b'UwWu9MUer35DHz9LqxPBiiJL4smlm0F2+h6+3eS8uBrVWCFVKlhXPiodR6P2nXlFkmBG9ymeGmA1TK3f8HvhVy+OlQ7nd2cby/xIMyQyPCbYLCg2PDL4dzFCQc7f5X48'
        b'0m4s4eM/7XDrkqkjTiy1KoqlELlnF1S6LavQ0aAKrfCQxAL7/ug682XxzthAnum34x2uWgXWRofiKGP2YSxiDSM5tw4+INzr4nFZag24QZ8cDK3Gxu/srKYexG/sPHUl'
        b'iObJ5znY1laZnfcxeNw3+9gIy2qun13OmMvLTS5ewfHaefqt7vl5Tf2nK/DaM002/j02HxlPTx9Hz/gLAg7FfXvlusWKF+xwLXfUjjvSxGXLc95wDptx4oN7L35RVv+7'
        b'4fgzyvL4Q/Sr6vzxK1bMTlFJRygyWF6ETl2iri4v0hbKq6kKFRV1hPJrZFmkgpZ36zea1y2EmrGGQnkDbSGXyWQJN08+eZRbJDDadsNR5gqU2CR9QWO647Q2NEG5XRw2'
        b'7FCHXDJEH6zaYw0ZITgouxfzoQzK5cm6a8KbBipkWObAHeiHiiNHoE2JIEmBcC0+hEl8qAJ1e3EMSmAkCMaxx0dFhPcgCwft9hOjDTnDQye66jYWpMIk9EC/xVVodyfV'
        b'fBVnsVuODMBe+pneTVZ0O3ZFXLbcgnU7MQNbY6EZs7EHR7Dhqh0UQhfegmFdp8v7vXSgcBNmHL4WbUXMOAuTUfsx94LTGoOgNY573WT8LdMtvKDdX98cKnB8P0xhN9nj'
        b'pbHQSxZ9IUw4w4TtRRO8bXkei1SwKxSHtEjl34FybKOfB1gdeBjrj1lFQ3EIDsiSaT+BuXEwjGXY7I0DMJR8ETvg4TV4gDU+ULYa2y4EYDV07FmF95zhwQ4ooncvgxKN'
        b'IzDoDVnb3GgCE1hvA4PXsO841AmRLHG8iZXQSH/fjoS7WA9tyevFSlAJY9hiaYbtOBFpo7gfxyEvRB8ynC5Cdig9tsYDZoxDHOMMHLEkCh9igytW+evBQMqBIw54n0zU'
        b'Jhyyk4Xa48a+9OaFBN9yFLf64KgetmIb/WvSA/Kg0Y+WowpqzHDS5sAWu83aWjhykj5oTN8WYIp12KuuRXiyFMZ9EujTMlXFjThHd/TiMAzShIYEWGMVtg/rzkCDJcxo'
        b'YotqsAeURCQewIwTWLMeCs9by+Mc3NfXgvsxMLcWciPo9v5LZJXX7tTHttCNJ0/bbccKooT70JUQRERXjfU+yqvPpMXuS8cx/bProN4T2lYH4CCtUA3elaeXGSOKqsc2'
        b'eyySh7yjOL2DNrIa+mzpLftpfpOQ5Ud7cNv8IBFEQQqM6K4le/8hbeYd1etinMFbTptP4v2kIhErWbHzKjSdcIASonplmMHRVVftaXu7j0LGemjEWnPlXXiPNmgYmsVH'
        b'oSskaJMxlEZKoNAQK0/d2A6dNklpkWpYReTYhndpbYsuBZ6C2VV+UG8P9TAMHZAVhI0mWGO6Fe/jNEyKYUgBK9fiRJDMJWyCMV//5IPYcM07BvpYW3aYNaL3IBrBgVi3'
        b'ffSIZn1owMxjLI+33A9q9kAt5AUT82WKbD2wHIbM6ZoRvAu91wKuaan73Qje5RSBjRqpuzRwgF62kIg5i/ji5m5irFtOBu6bU7cSud2GOuzfSWTeR+R5H/ODsDyGMG2h'
        b'4VFSaLfksPMAlqdDS5KbQxQObMM8I7Iu5q7usbgBuecUvOG+3npWJw27NWwkcTgXiCMiLE3RCTqK2TCqCEXXnaEWM/WdoMQfMjAnVA1a4K6Xt69liObW1djj4KSorWmx'
        b'Q2atlS8xUZM75nvTBtdirx7kk1TJCMIua9rJB4S3c8RY7gllOGyIjZ5Y4Ie9MCrRIOIr0IU2eg0mmHLOW7KVhXzsh7HklNVQvJ7GGyCauptC5JCXpiFP7DAajpU4ddVS'
        b'GypoDbNpb4ZIcI3LR6i6Ystqwgl3Tp/EPuK7HJw0OAuzHm4wB90Km6E8gURCF+TahuHoRbzlB7MWa5gL8IwXTK4lkuvD4hNQ7uaqcSYZx2m8LiKE5gDIJAaao9fKtMQ+'
        b'rW3em1d5kTFVjuP+2BlDS3fXC0aM8b4M1AZvhlZXmEv6ORGkKBgaiCDt4DYjSJr1lCmMJdli4xkJPfUOZscGwZ3LSsSVNbuPmUGXeqAb9ByAIpygtZrBmrVERQ+hgF5s'
        b'BAZdIDeAmDVnI846Hzhgh7Wu0B6qrog5RK2dRE+TkL0J6g2vEPnWiA7ATKrA2sIFKy4kmtKmjUIXYaUCmCbGKSeOawgOOBtLoqPNDBuiabEfCJClkdXThrSztM0zR0ko'
        b'zpnqnko8ew7ueNAMO7AUx4yIL8oObrRMwSJtBZhaSq3EG9XHVtM8xpMxy1zhBozFcvKyUjUV6khQdjm4W6dtCIEhz/SrOuJzTlCoC5nh9GJz9IAuEktZ1geIdmvlLkIx'
        b'dJ9nya2V2GOoAhU2WOcMdxLpkkxkb9KCzaSRuiFDTYRZdiRAOlfJwaQNTuttJVIYgWlLfKidjO2xq1IlkTGYAVXEq7lYqUYL1UGv14UzMHqM9rJNAwv810VC/sYkzMJh'
        b'e+igRZ85s4000z3/FH2i3daLdlgaSPqrxhh6kokdiixYIpSDJcm4W0SVpDfP7LqwG8uMovHutUOqaTTFLMggSm6D0Z2GRqFBMEryZlJZGytwGrOUMd8Rmi19iCKgNZWm'
        b'cAtvG8E44dY+uJ2GbXJrN9MyP8AOR//t8BAbFR1N6JVzSUDeIaXdcARGnSJO0FaOws0Ef9rQOlKHLfAgDQuvQO1ZuTCstgt3suAU+m23RNI2uUkkEUrpmur9Trp+WAMN'
        b'F6BAdEUPGom6aQ2JuqH5dDTNco6s/y1xro54K1YFy8JOya07hwNroIbR1nbi5jZHDexazZE1zK3zZXI2lgMXM1yCnfDo+kC4I4d1JxSFMMwyikuIY2qhNBFGBCRrN6/C'
        b'jJ20vLX66XhPDqahI8zJCOoPQ58WaYL61XR5iSo2yl3UjyaiqVcjTqy1NMaHvhbO0HA8HSv1och1/R5SApOKtDIPsVDuGPQEMl4JEl46w5BQUywO4oOzp0hWMNHbT0KA'
        b'0EecNTRo2Zue0MRBfygLPAI3j8K0Ot5xuhFAy3JnT7oWFHm7+0PPFhy7se5wIAmNXtqNvou0Jn3QEJAqxGpHK5jy2ZGuehgziaFrD4SQTr5JW9ymp0FrnYsdYpjTwHJf'
        b'XfU1pPQKtKH0rHuQDzHurNXxvTHEwhV+UGEBWe7a27Xxbgz02xPr5UdD5VboS8Gbh4WYIXMMpkMPQZVjFIwe8IQHkH/I9vDR62uwjsifpGInDZknuEjyvw2HZeEO8cEt'
        b'HeKXEVqt29hoCbNQtJrYtHELPLiGE5cPENHWkqIrwer9l7HNgURKRujxFMh1iiMWuHMNqq+tIrIaD03Fngg9rCUR2EpyomAfFp/SsEai91LscCJcRBTdabiH5tBEv7Xb'
        b'70lxUieNeGQNjHoTGU7CWOouYvpZ7D2MRbRyOaTvWvasZ3gsHorCDbcxUsQy7YOcMGijaWZAcxRUB2ukXfHARhpljNiqBsqjaDY9hAeyRFCSRGtftDqdXq+BlGcf6cwE'
        b'P2i1wGbs0PNS8SY10R2tg61hWOVCW9yFD85AUyBN8d4BuEdMnG8L2cj4fBarfekReecirzAFhJkXV+PoJZIvI5iz2fG0Ig6t3el4fJ2BZVI5gw9ElDSFphP0CgsIwhTv'
        b'Cy9iCSEIOxtTmNwBQ1eUttnKxRN+rXU8ieWH6FXgjgPt8SzdPRpPizTBZJDfRsi1wqydQdBEQxfA0KV0O+X1bjCLg8HYQtfcI+FRc8MAMkxP0m7fl9iQIKyGKRPrg9h3'
        b'lvBZFU6FEbosIRXWS9p5HEmsZd0wx0pNItv8Q2fhjitWn7AntVoaZg91viaENzrgwV4arYSQyB2YUSPeboJWdexxhpKdKViu6mEQcZEkXaYcMUhzuuJ5GNqy94i7np0K'
        b'EVg/VKmar4OGoxJatiZFTVscM9gqL3bEmxtoJTO2EOl3aqxlGXb02IEzmHUWKh2ARNMBUoMknQgg4PR5bMTmfZdJYlVBN2mTDgL6Q7RRwmPmJ6FwSyyp6Qbo98Ks09h2'
        b'Zi8UuJt50Mplwa3D0Wu9nI4zCFNw9jp0BRvjzRDI0Eo3xBrW1SEAJ+KJeKqPY18g5pvvgBoRUVqLO+Y5EH3NkWAfiDhLJkkpie5bq/VolccCsWIf5kFLnA2t/l1LyD1A'
        b'ZNOBZTv9tcOtbb2CoSMQ78edIbl8Z5+a4harPdqrrYxJqI8p4y2tI57bSBvObYFGX3pquQrR1sOLUHDiJDHJ9Bm4sxW6tENxOJYGbKDXbDpHrNAZELaKBFA5DFjAoBKt'
        b'ZwHWRMAtAxg5e+mc7kHojaGLBqAunEREnTiaZpXhTeQ2ZgW37WB2G+nbKcy+oY0PBTEsXboaqy4lvcWkbZfPWUaUmbEcTc4STaZgXxjeTZUnzJOlxer2Z25dR/h2TH+H'
        b'JlaoE4o8dSLNGUpvGGxJT4LcIL1j55VPsDaP7AeydpPkryYxQrfZMcx0VV0F+lNoX6ex5eRBJVKWEzCnFoidWBdNyrZbBjOSsMonDGbTY1npzuCzhGTuceABCDw8gNko'
        b'Iv7RYD3MiTfATiNWppVYp88nFsuuGpJwaGRIN5ImkH9u70U9JbqjjARHNS1GoYc/obzea97XTkWmbFT2RAKr7di5kUR395kDKaq0toXAOLcU7sdeOqAJE2qJxCWZ8QQo'
        b'Sv08rRQ241CwJ96Eam+6ZAKy5bBXJQzzj7OWqfRx3iWoVyMjJRuaU3DkPAtKblc2dSXpVBel7hideoDMprZ1xKKDLKV6rZGE1rJqB0HNUl1tqIw1NDhKvNq/DqecSGwV'
        b'k2UyRup4OpZVTcPyy1uwaxNZtr2YfQ3qjcxJ+t2Xo8GysMvKKcwqZcOZcOLyTGKFrCTignpFKN+JJRessMF9CzHCqJZGQjBJvxnsPY29Z4lnOjYQ/TXuIcQyaQV5eP9S'
        b'LLQnkvmdT2ay7g5tkpY1B0nEj2523LeJJl4aCcUEGWTwri9py3wi1IoDF3DcdzXmSKASB8No5CYitnrBpmS7S6cTdI7RDg9vNCFuaYKy0ERoPJACBZvwlswZLIyGuv10'
        b'7QiMEeaswVsngZWDbYVGbXdVaHHdesOLCLQf76X5xxBSrPE+cHQPs8v6bKHTId7kDEwSUd32gOH0KO1wEkF1akTfY+bYfvyqE1Y4mhBN3NPdiJnb3aN9ST5lpBjLcsfU'
        b'yEQeknFzkREIt0PfVgEW7IJp/sBRKxk809ITR9h8mvDpEcjm7jmFZPC6mYoEQns7GBRgXQiWcHkuFqT169jxAeHBGzL0uStkcHlUEQa0J4VYKGRNjuvsBcwyu8FltYiC'
        b'7LHQjD53hqFQATZH7UxyErPSxLT81bRKFVhMfFFvr0zLPnhd0SBAAar3nVAL0iK1VGZB1NBGy1TF4PpWzHZx9IDc6AM6xiRoJrFzdRrpplZodlF3CCDxXQqNwXib8Aox'
        b'MLZYM3cLmd1lKRZJh6FXh2G8a9AZFoR5StAaH0RcUwFzByDj1HGs8qSNpO+JF3OOssgNdAtIuub5ahKAa6B1wybL05uJ8DLXkTEwbOJPz70t8KIxc8JIoA6S/q2gjSbz'
        b'Juoq5FqQbi3zgdKtZCeMEDmcJvxStpUE3ACU25KNlJN43oMdeyimcRqI+x7CiD7ZS1mkHfNtja9CnhWBt2kSEkOkC+7A0AaCwnehzibM5ooYb8uFqWGt8wXoscb78aYG'
        b'OHUO+067rIIeuatJYR7x50l+lkGHAnMZQK3+asykhe0jWZRJsrHrzGl6VhGtZ7W/djTx7BRNoXQ3vWqX3RrFU8rYHBLIGV31YsyyJCMmg1ZlQNYUSY7OWUKRGIf8Tbws'
        b'MYdF1Vr34dBW4pxuK1NgJzx6oHQfwaHb9EYZ8bpJElJMpQn0Fh0weySA4GQFFJhAsxz2R2GpM1QdxDu+7NwpmS6zcquwMHBDiPHhtdgvD1WBUBVPfDJrrJqEPSHx8dhF'
        b'P+XXVGjCt6xP+pEBOUCyuMwKRw47XdUID4VxIxWYUMUWZ+Krm3twYLsLUVcP5CJz69xSI9t9DDLXQON5EgRQfdD5tGdA/KnTuoSH8kmRT+naYGX8diuSFCNXxCQgOqHf'
        b'XIcMzEjs20OmQKmJFtbrMjlO2i5vxw1i0vHdBBZvMVeUsWc4aVOY3A4NiURSeTAZAHmxpMA7oPcIUfiA2w0YOE8GXzNt6oDrXs73MiMmJdMSEEHGVCfc3qO79ropwc4x'
        b'T2ZFYFk4PMC2HfTHHM4a6kB1WIJZoh7hrb4DeP+cCmaq4IwQms/dCLBNSrpL6uv4iTOP+2RIht47YGivdgX7dWTXJGNrKDFGZjBJ5WEyizOPBWCBq7aOA9ktc1ATT4uZ'
        b'q6Qtc/q8+wmSPKVWa4h0qmFwNXbt1HPbsB9G08keyPPT8zIPcZAjpXb/+EnOOzPiZUAD1UOFNS3JjCK9wkgsCaU21kw4EieSYIKlaRbuNyXW6MLGWPrH7Su7oJ6UGsn3'
        b'Ukaq7TBsAvd2xBHYb96LI6EBtMy5Hid1GdREEtSdp4SE92aIqTP1iX+GnUjHNUv0sduUBO8otmudhLsb2WFoaLCPdyeQ3RxB0DPLngnXYci8FkPofq09AYX21WrMq+WO'
        b'3WmahxWh9+JZksNFvBMgIYQ4oPTCFpoWKTRsvU6SYEqfGKGJbFzo9jgniMa8QzEkchrPHYogvTCKjWE0w/JEUsNZdAdBcmwKCYXBmGN7cExXHR5uOk2kUKuNnQ4WbEVM'
        b'sEc3DKeiiGoYyO8lw2EmHmfPyexXx7q1O7Hc6xKJtCItbNMk+6sinWBUBsxdJqgzdhB6NLyMDlptJuV7B6v85bHVKY4WvcFoW9J64yidY06aGnhH60bSXhXIPSTyJIrv'
        b'JfK7BV3XSRC0Jp10hsIAErM3TeG+dhgx5QxxxcS1UxdJV8ZCiRiH6d/9JI+ngq6QsG20u+qHnf7mJJXqsc8YHhw6BwMGW1xIKFSwDaZNeEhyrY6Ew4AGvcYszl0/5k4P'
        b'7dgN5RdXOXnR2NNraT0eHIb7DiSB887LbDyYSEudnfQmEetWj3Bo8sbCBcv2FA1eDDW7DJhx639CSQjjmpjvCYOy5jAQIKsDPUgScGw3EcGg7UmchQKLKFsizzLOX9K7'
        b'0ZyEGPPO1WmYQQ7JNKLPXBgiwwAfJnuZG9Nu9eHMAQfo0Yc6Nf01tPZFMBZKrNp+cL8AelaTUOndAnW2mLGBzP0R6PfDFl9osPQnmZPnAo2h/qQQBk8yeNKGrf7x22TE'
        b'kfuxejt2prBi7SObfDArdgd0RB8ipdBBL9xNkLXRkaQNTLljgZk/qY0GE+LlbPMNpyKxc8+q0/H40JNorZoUR84ubXloiY6FIRJdzdC2h4l9TznigrlLXmS2lxHFFEFH'
        b'GiutC3NrsGs7VCWRPqnxjCZ6IrulxkwlFnIUDffigG0U1rrqXIQZ6EnCBluYdojHGlq+2zh0cj3M+QhsMFtFHufENNFcj1UwJcMcI+220BWh4wzVR9eusSWbq4DeCgf2'
        b'kRSfIaIYJC6YJEqYvUy2Z78WrXtdcAjjnPBIIxKqxaIzDhGXlWE8ALuivTyjws8RTh1RpSnUk77tU8QRNygMgZqTprpA9sVNLI5WDsJ+H7itZR94Nh2bXT3W7cSyHTi8'
        b'LvIMlliJGG4lGZRDNnQLzrinXKW3LwxWJ93Vig/XS7ZAtdYJzA3xczp3yMOROLzIDqsSbEJxaiMt3D3a1UIyDGXPk3DoV/LX5wQMk9qVtJC1IbtI+o1vNCbOrcX2VGK4'
        b'EhgyIuOnUEOO1GPvJb9VrDhGKM4eu0zbU4yEDkoVYEJznwVJtOZUrRtq24i7WM7hQzPMPw/Ney4SSqlak3SUIZpaKxJiS0mbLNsJsUiXBG6ZvVo8dGjLRm8jidtELzNM'
        b'8rB6p9DVx4WZTiF4PwRHVYixxundW832qWKp/ul1EqLxetLeRQTg+9Notat2+Sj4wj1rrPcj8q4nsT2txMxx6NP3ZW2/6X1KdDDH25EBHy162MB5A+i0xIGjJkhoxnUd'
        b'rVDhRmixMCD+rNoPDatoaRoSSOd0h8Gwnz4Rer3oxK610L7aFjKC4dZ2Qr52JA0NfI3Xkpwoj8QsBRgOi79BaisLxvytSauMhjERXiiXeMwKepT30BLfxjq987RIU5rY'
        b'FrEK78kbpTnsv6wLTXtg0P0qEVUn6b0OrFuNE4mu2KNJOOc2qdAHkaQJ0hQPx9MeNtNDyjfaJELHPslOHDi4Ge4eUMTGROxXDz+rB10a6pehYhUWuUXQgzKh0kzO0oP2'
        b'k0AGLct9iaHHJfs9J6Lx3kYSDT3EQo2BG3HOkWRXDTS5ONgJiC8KiC8JfJPkKocJpXDM2026mVV5OQxDaxSEJAsmz58hqddJW3KfnpqjseoUqfBiaJeH7EjItcUecxL/'
        b'+devQLnNGWT+8TYBjJ7bt5YkyjTkRm0jNuvWg1ZzYvM64oghsqcbAxVW78YHulDjY+N2yYm0513C5wMSuuUmjBpq25K90Q5dDtAro0+c1AhzW1atJiBbbIKlV7GULc2t'
        b'ZBgRX9q6jz4t2w9t207hFKlJrNbYvH8zNttAbZgf0U0+VseTWppNCcDBXft9ISsmkQRjpYXAGrqCiDzKU7SDg2nlYyLxARQHw9Blgs9lBN+KacWG95JszdlsS1bhFObF'
        b'73ULJyuAkF5Bujkt8IiykKivV5lBY9rMutCElGtw34t10YB6d7LPW2DwkjPeO8UpxjF8sD/gANQYkdIk69fJDsdcCb4NKoXuJBxX60/cMScXTGAtY+NR7E6SECdt8SNZ'
        b'S4yUSfTMOGkWH5iSMK4l8pywxTE9grp+WKEYdRj6NmPD4e1QJib9dkeFXWGnHkX24kx6hLMzgYEsV19bQ8xNiyN4PYvdDkQAI9CigDPWcjGkdvqE2OqN01uuQQZZflVb'
        b'HdWUvLE6lIuqDTAn/410qIRp5s5qh6kT9IbEJ13MVUQotxO6nHWwLvXEttPb6d2qsHc/Zt4gy2tcn3Rj/hlo8SW4NW4uGxlnqUebXwv3nRWJ+fvp4mJLWtrcGGKEWTW8'
        b'cxZyCBMM0UuX7MTStXKs+6CCOd67GkkYMDc4BbLtSDGXwB0xjugpYMNJPUc9opp+Ixn1dXj/oC+UqtrLk+CcxgwnAjR9TKztxnsCUuFVeHuHatgxyAlwM7JJjFbEWfVT'
        b'adtIxhMsP3DxGNy+hBWW3mRWMyA6aht5lYjk1jYY0tjrRozcqgvTijDhlxpjgne3kOiaxAbIOYfTKYqYe9SbmCOHDJO7JHjKyGjZQAtesx6blBXF4bpYeDo66ux5K6x3'
        b'UxUe1aH7BqBMFso1dInpKmAyWtnFdDtOrGe+T1LeGTCzBiZZ5K5bfx0ZfUXBB+0IvjfvorVohXvrzGOhzH0TsUYJ2T4JSVC3i/Yh1wXH9ysRgH9A2KDxaJoutilfl6E3'
        b'KHeEei2Fq8R15fSvMpgzjQ1MheYNJKyzNG28YFwPGtX32Ckn401XzNE/L4fdPlAeCc3QR4RUcsKf+UuJGJm7i/b+AcnfIXbCGzssMP/6+Q2sQA48PEnXNnnSy9w8hRNp'
        b'FgTNoJP4pYJUdb6Sf3DSaeLKFmDqhBBphzW929w1qFyP5WEEuscvE8UMJOsRYfVdw7wbcItkOaGPm340chY0JP0n80vdC7BeYAR75pi6fYrUMEmx6IOGJ9Q2YykxwanN'
        b'6fR14+qIEAU97Fhts5l2dw7vRUC/nHMgDTJBKKlTZI0Ta2EOu/dEK9Eb5eCdRGDR38zT+6FcAtV6JM5nkrHODdrErEklTIeRvrl7naTjbeKnStqLMsX12O5K0rSPlr4I'
        b'y6/iHDzYr423rOGBObZt9sDCGBbmcmGeqtBjtDg5W0mm3FKWYG/YGiL7sVRDYvOpnV5xRG8dWpas1s0OHazeZGCMDVuPEmIg1jhMxDCrHYnjyli/bwN2qpDZmHMGsg7j'
        b'lD30KaSQeKkg+FNF4rldQBQ/LbufeKpJ3xlqlMhI6NyhBq0OO6HOivBCjp7PKry7aZesLOYfP4y3lPDm4WNkFz+wICSXZ4vDapdwfLuymyW0WWGFw157WpdRqJew7jgk'
        b'8nPTAg3V2bGuKRIHU5BpSNQ+ICRoduPKTiK4ihOQo8TRxdR5kuJzF7aSUGjEvDhauC4mDMZ3EPyoCI+Edht2QptoqgILdHHUmiybsgjIl4W2SEO4K4HBA3txglnomHGc'
        b'ZNiYezIp9YdWsoSt26HICLPMaG0GdaDtGtRoEHnkb2SRZJmrstYRPvTkyv2qWE34QTaZoaAsrd2xZPQRpr9JMqIMurSw7ohuCkur8KbFq4fpc1e2QK85zDhCu7EM1G0g'
        b'hNXgBz0XyOgZgHbz88CKS01Z743bBdOu2y5j2xaodYUu0x1HcVSGFEuNywbmucGRnaTmehiT1HlrHrEimN1ngXO+m0m01ZwIVD1/zWeNP9FOPmbsdqcxajfZGdhfY3WC'
        b'8i9gD+GoRmmrYKdd0MGK6fCVdAJgRmgSCA+5rwxJp2ew6m/QlMQXgCNpUWks5jxLN65AoxvzLNlYw6gAq1fv4VxUW5TEbqyUhHCHUF1A3JKHk5xPS3bdUXaISiIQHr4I'
        b'rXQ9jkVxX6zFvD28f8wBJllfVzIfaGrsWWehONCNVbu1tMVu+kpG2sJY4sAO/LvTPba0H3UCQiu303lvW/txHJT61CQyLORbEyjt6rBnL+v9Zkw3eaVbs/6to9jA35Pj'
        b'l4aFHsyppoTlAtq0KUdumHBavDHeDUcip0pA0LPR31jIvX2QItxyc6WHmR7CZgGt6QHuvJeQZFDOvCcuktXFIyALfcZCR64TEHeaLXa/iOVgppgpB7qfFV8UGIu5j2v1'
        b'xdzHb4kDYzKCL/IVhM7G8NeuEQTGmNjtF3gaizzpUdzZt6j1ua3ihH4SVA5N969VnPJa66CdE5H8ns6OX7z8K3ujl33Wun8++0vt8tK2/X57LV1LN275wluy3b/jQUP3'
        b'PwTXY14vObX14w0jM++nv/7P8Ne1v1n/lX+i7rv9IS/cH77+u38m10a99M7P/x417vijX77rnb3uvVPHxx86H9pQfyL/4v+s+d/Y/s9fKhD+euf11ac+6bto9M1vm33d'
        b'd9nkDp70317o6HX+kylFD+OPdk97n+8/kf+TS8YQMaZd0Xim0uMHP7tq8NfpL06u6WmsMR9r++z9L9+5/FKaw8m7Y+1ZrqNG54Oa7MvdL7z2+ZGCpLWfWn+WvOG1aZnP'
        b'7yb+aGeV8rTtId33vY2ddcfV037qZv6Ff6pxb6rLK8p/39Hcejvxh62aFV/p/fG68rs/3PFBs011xPS+dxTeWFu9M6r65IhMVE1UXVjz0bcrD9saTwap+5/w/2Gi8k8u'
        b'Jb/rG1/9tx9lKMvGOBQ0jrqav1L/qGK/yWSIvG25bcvmC2dNB40/UHk9xqXiVcvf73D81W7NxLffmfznz2pTtEP+9vLf3lWp/7RM7z3Z19/t+H3sh+d8E7bV/mNnjuf2'
        b'9/Y3KL+888XjW/XfKPyj79q9NwaP3PzH/7yj+PGu2YG3C+NFqdrOOu/Whux06Cgp+fq2RXKgpndot8h6zaPJLRs+Nuj/yKDmlek3A0a6/2dzQe3WgwO/XF9+4BvlrNff'
        b'i9e2qv3oj11fOHz1x6If3X31Df8uq7zU9/Ns4oI9fzNTp+QX+t5qHze/rTUvOr2lNfKi3bkXTf4ZOmT915b/19z1B0Vx3fG93b3j+HHHL38gEk1EDXjgjyARDSY4QeJ5'
        b'HCRDM9Go3RzHAQvH3XF7d6JAo4jioQfEH60BNURjVFAEVMCftO+1ptNOy0xNlFmTxppOnNSkaUbTFKfWvu/bI2bUf9rpDJ2b+9zu27dv996+3ff93n0/n++r5uVP37z2'
        b't+96Ez6Iv/J2yZqboSGfDO3pHPQ1dNxsmf5tVcyt1nxTjj5jefzk4T8ntf0raW3YquFLel9PQ21CZrZra2LCZ/zhjMvfjmxa2Vt58fDzX/1x0sB15z9/f2y4X3P/1tDl'
        b'jru+8q6jL3zeP/fHH47MeecfxvMdt8nHwvNdtz/N/ObmSHr77N219yYOfZS3uXlNcpii5bIRHQ0j9zA8P8iji9x2TZVRVOMDBWrQmUeUfKrVvLY6nSZFw3WxL1BuG3rL'
        b'8jhqW9d6KtehI8Z7uFsXqiPT+rZItxdfnBRBZuN+jklYz2s5PKg0NkC8lj6ol+SiNdfivrWVOg0Tl8WRieIEaqIqJwtRY77ki6gkJky7F/dHoka0PVKrC8PdkT41k6zn'
        b'8bHF+IIHwoBrfOi45MMHFkdUPlwTBUZbN/MadGahVtHb76nIDFdqkNmszwfh/YfZOWS620cDecH1bJCID1KmrSSnKJFV/2NaxKc16OKziR5QuixGO4wPa7IogixkXt6g'
        b'iLKQnjrwaPa4tLENLB1zSE6gz9b/F1DSfguC3WkpEgQacv0h/KtjYNn5qidBMOS+ho1QaVme06o0nIbVsHouRh0TExUaNSUqJEYzLoyPHcfGGdlp81XMm2waq8qgiYN4'
        b'DsJvp0CZIU6VPQPKWCEzmFSItS6iS+xroyVxmviVUUtI2xwblQJ7JWaP1k1kZ7HJ5G1gk5mNfCct07AptIS8SNkhiKrWjIyGf2ujtKo41Q/f/H1+xP3G99HNnPsL+PIP'
        b'or2fGfuBMWYDUqV0Bo22hi6C/KwS2C2uq49JhkUZsj8j/jaECxOzCPsXsfm5yI+aQxj9JO4JdHaVeGndECNNUDFM+J6B9IAxD2dFLe1c3NwTe82/MytL6zduiPuVK2LC'
        b'1gvqtr8eS1ma3b3tTkG/dsGhy3Ef3bj3h85PP9m6ZXrt5YkV2eX3tE1Xv7nkSNmXuuR3VxbtjT/78YI7Ve2iSRj5snPD4vFui+OJSUf3rNndfdlb0BRRvTeuePWkz1eX'
        b'ne09ocntuD44mLmyo/HFnbX7GhK0r1/5bdbXGxOOtm5uf631sP70Z0ORS67N+1q8nSP1DMvDw30n7zjvrEl6uuw3Z77Idr/0lfvEraEMzrI1mi9bEYcv8QUZrnl4yt//'
        b'9IsPVGzCtF9GN1XWaQ9nvLidvznw8xldLTc0iz++of/u1y0Hm8OPhUS8fD06vyrH/5d7Z/1tReO7L/QJSavvsel7Vl1NLEyeSlnbqG06/J6J/fn5lGwbwoQTrwb1svhI'
        b'Gm5RqMgH0EncbFr+XH4q7oGKEKcejc9z9L/ddjoNof2xNO8ouRYm1EhMyO1m+JGHXI0Ybgo5wC7Kd56JW4n3ZzTPIjX7zSGMhme1RYLCQX43nEo2EPu0gHiaR4A0ch41'
        b'K3pYR3H9BANuSgLi8HYVEzqb2NUNLPFXTi2iO2sXoq2GoKQX2o0DfJ4KdT9VoOh+7cJ7p0KQfQYOpAbr6HEjl0f8pkOUX55uylBo58Sx7KHU87IV9LhSutnArqD7mI04'
        b'kGzkmRi8k0NnS1CdkmmhnXjRh0zLU/LS01RMCN6B/FZWg1sFRfvqvUJ8zkQclUPPpJHdTUFxs6e457LQAD1ACTrHmojXW08qGM3Kdj3u4uZ50GmFmt6Gu4nDuQ0Yb80c'
        b'WSV+9CsqdG7+eGXz8WXwwzIOmCGV7H6ycZ4KfGDUrvSpX7fekIoDxPwwoHf4ChXxN0/jtxVed+dMNGgAUbtcOK6ZdADPTK7lc3E7qpuI6+icnRqLN5ngxEgPQMeH45Or'
        b'k1nib+8Kkne6f4TrpR9UCJtRZmRRN4cOUkZ3ZQlIqPZGQmAwOiIhP+534VOVxFDRMUxCIh+C/QtoV5HZG9VTNpIBWiP3bCzx01tZfGBFMCXF9DeIl7dNSS+biwYVbbqJ'
        b'eIAaAtXE/zpuQseTjKlUZ4xqL+YbUWBOXmqyhnlp6SJ3SE0NPkYHoVOYFo678SlQ9H5LIA4+fh+3+pTr2Yrfr4YQanNubVy+mlHXqPB7ZHO7InF4Hh8hg+Ek5RnNmTVK'
        b'Lor38sa5aIudpV0STfzhLaTTG0EEMZdlQmfitjQWbVPjk4rcWQeq9xqWp6aYU2ermAhyroHxXNjkcHqnob5yn6kAHyTXxTSbNEDuJnL6sWkc3o+aUSDY5z7WsCxlFhA+'
        b'4ZLE4hbcAnSOHTMVfcleD+4ygM9mwi1TGbynFv90NKFR0tg/6P9H08WEMbBQHiQR9sEzRx8WpGGCklpUcEnRPIugOmnBpfv8BtBTY+9DymCtysH950yy0Rc/V+FUUfNh'
        b'lszZbQ63RGY4We3xuuw2mbeLkkfmi0QrQafL5pA5yeOW1YXrPDZJ5gudTrvMiQ6PrC4mphb5IFNXiU1Wiw6X1yNz1lK3zDndRbKmWLR7bGSlwuKSufWiS1ZbJKsoylyp'
        b'rYpUIc2HiZLokDwWh9Uma1zeQrtolSOWKoxGs6Wc7Bzhcts8HrF4nVBVYZe1uU5reY5ITjK0MO1ZmwNEqWSdKDkFj1hhIw1VuGQ+5+XsHFnnsrglm0A2Actbjq5wFi1c'
        b'oCT3EIrEEtEjh1isVpvLI8k6+sUEj5NYjo4SmVthzpXDpVKx2CPY3G6nW9Z5HdZSi+iwFQm2KqscKgiSjXSVIMh6h1NwFhZ7JSvNySSHjq6Qr+N1gCrVA8NM6e8k91ow'
        b'3WoA1gFsBKgHeJPS2wDWA5QClABsAKigPFkAJ0AZAPAK3XYAEcALUA1gAQAiq9sF8BOAzQBbADwAQCV2OwBqAaoAfADlAHVU4A6gkB4IWHabYKkBoPJ79iAMpNBRI+v1'
        b'kUeNLFrjrraYjBebtXS2HCUIweWgnX43Prj+pMtiLQdhMuC1wjZbUV6ylnIA5RBBsNjtgqAMXMoSDIURq1Hyqbq/hBL/qE38UFJmWZtJrr7XbnseMsNJyxig9fIaLfvf'
        b'30LjXmUpf/rffiBHGw=='
    ))))
