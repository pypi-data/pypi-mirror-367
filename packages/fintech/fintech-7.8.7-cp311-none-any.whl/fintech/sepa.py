
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
        b'eJzMvQlAk0f6P/6+uSCcgYT7CopCIAmniogHAnKDIHgrBBIgioAJ8UC0alWCoAZFDYqKN954U1trd6bb7bX9ETetKf22q7vd7bG7Ld26u123/+1/Zt6E29b2293fD8Iw'
        b'mZl35pn78zzzPPP+nhryw7b+/3oHcg5SSmoxVUEtppX0NmoxS8Xu5FBj/ChZZ2iKukDbvmuclGwWpeKeQf4LA6nWUFqnJSwUzlNyhqffSqNQO9WIXGhKyZ1H8cslvCcr'
        b'HOalzk0Sr6pR6qpU4ppycV2lSjx3fV1lTbV4jrq6TlVWKa5VlK1UVKjkDg6FlWqtLa1SVa6uVmnF5brqsjp1TbVWrKhWisuqFFotCq2rEa+t0awUr1XXVYpxEXKHstAh'
        b'FQtDf464NQSIqkaqkW5kNbIbOY3cRl6jXaN9I7/RodGx0anRudGl0bVR0OjW6N4obBQ1ejR6Nno1ejf6NPo2+jX6NwY0BjYGNYobgxvHNY5vDGmc0DixMfQgpffS++t9'
        b'9MH6EH2Q3l3vq7fX2+nFemc9R++qd9AL9U56vt5D76en9Gy9QB+on6CfqBfpuXoXfYDeW++pd9SP0/P0LD2tH68P1buVh6F+st8YxqKaQoa3/UYJn2JRDWHDQ1GIZHgI'
        b'TW0K2ySZR41/atxaah17EbWW5ldKWLllQ0dBDPoT4sbiWYfOPErikltlj76drmZReOREzTFlvuFGU7oQ9GWiN2iCzbAprwjczs6HergrTwJ3ZRTNlfGo0FQOvAfOOEnY'
        b'ugCUFB6Cp8G9rAxphgw2wRa4H1zK4VIucCc7N2myToRSAEORGsWvTsjgUhwODY7Bm1JdEI7YDq4nRpCn9PBmTk4G3CXJ4FDucB8b3KnOkbBIAeAk3AlvZcXEgo4ilCIL'
        b'7s5DGbkGs6dNB/d0fpiEk+DUWpRgMuzKyMhh4l3gZXb0xBBrHjL4IngRngC7tTgetuTAFppyyGCBbri7XjcO53GGv8kRXnOFN7Wo6rerwJFaeGM1aHZ1pij/8Ry7suck'
        b'tM4bJdQFw/OwOTtTAntgC5tiw5dpcDgW7EfREkztUXgJXs8Cl8JWL0QtsjMLtoCmPEwT2BWZK5PwqLRUuwYfeNyaXQzoQhW8jkjKzqst51LcBhqeeg5eRdGeKFoEdgOD'
        b'ThiRKZPmyOQ05eTBdkiejiL9Mc3nqp5Drbk1Il0aDpuycZ0coYEFL2eAK2X0kO6PtXV/H3L2xzSiIYBGLQeNVh4a1fZoJFNoTDuiMe2Mxq8rGs9uaMwL0Xj2QCPZC41n'
        b'HzQD/NCMCEAjPQjNg2A0usejuYFHfag+TC/Rh+sj9FK9TC/XR+qj9NH6GH2sPq48lox6tIY0OY4Y9Swy6ulRo541amTTm1jWUT9m3MCo3zZy1PuPMernMqM+RWZHOVGU'
        b'gIqtrdpix6JIoHgNMxUor6pszqpUJjCmyB4lo6Lm+m/MnrSQwwQmi7gU+i+eW78p+1qKI3WOqnLABEX5cB77JkygqEehf2Xdil45sYyq4qOIyIVGuttOsIGaVRLzPzFT'
        b'Kv7BBPu4/NW1zfUNkePch/S/F14IcqP6KJ0MRcyIrEfTrzkyPywM7oxMl8FT4CzcCc4VhmXmwD1SeYYsM4emql3508HZPF0qM+5egs3aOs2a1TotvA274Q14Dd6CV+FN'
        b'eN3V3snBhe/sCPYAPWiJiYpzgy/FTI6eFAtug24OBV5ewoeX3OBWXSbO6TgNj2VlZ+Zm5GTBPWhmtqCSu8BONG+a4C5EVJg0XC6RRYArKPRiAcriGjwIW+F+aIAH4D7Y'
        b'tgA1YJSzu8/UYWMQN6wX7owGPAZZeMVGo5BGI49bziajBO0/TZwRo4TNH6PfUQh71EhgbWJbR8mYcQOjpGLkKOGMMUo4uRrczep/L/sLR5uPfBu8Jhx+8zVj4pHg7atp'
        b'9uTeN3paWrcoJo1vKW6ep3KGrDlVv3tr87pJWxtL+1gTQcIKn4R2r6gynd88ZxjTyb/w6IzyqqFUE8WucKSOtbi3tv9Gwn3si/KFzeBIEOrqnail0WrCmQrOTqfB1Ui4'
        b'77EPjj4XBu5GyFF0J+qIJilN8cBulqzC8TFeO+DuRcAYIQNnncPSZSwUdYglgx1g32O8coCmioAI2XPwAtyVHc2leItpeMl78WMPPM7BzQDYnA4uieAp1Job6TmBsFnC'
        b'6WOFSTRoqFODjhY3jnjz5s1PPBLLNTX1qmpxObOny7WqWsWMPrZOrazHDgunXoacbzZT/XNYlMjz4JS9U4xxrdPbputTLEIP5uuxhEMJ7YkdiSZhmFkY9kAovy+Um4RR'
        b'ZmEUTuR1MGFvglHdJTIJ5Wb8iXkgjL8vjDcJE8zChF6nhK9xh2nskCPh9fGrFatUWoQtVH0chaZC22dXXKzRVRcX9zkWF5dVqRTVuloUMlgZ3MElJWJUH40bDnRHDiE+'
        b'BceuxsR/g8lPZdF0QD/1fc5DFy+9umlly8rNjv0sLi2yOLrrpzRNbZn6kOO6OWtLzraczTkWe1eLvVDv+E0/WtYFw0M35zG/X+NhdoAvpS66JLDnlLHGGpeb8IRhWycM'
        b'h0wZXjlnYMpw/+NTZtTC6jDGlHHP1eGgJbDNJXW+NpuLBy8FzsrBPgIC4HE+uJI8NQtF0BIKNsIboF2HB2MUuAgaFRDtgXkoikuBm27wFnkkBW4HBhfQA5txTCoF98cH'
        b'6HDHiUIcguBhRwQzaDcKvFiVTUqGnTnZdd4RODSfgofBCdjFlPwivFMEjk6PkPMoegkFz04CrWRvjYZ7wWFEyUW4D0/xeioHHoXnCFFosu0BOyYBPdyHqiilpGA3vC3h'
        b'6/CIWQbugMvL+dNQX8Ht6JO1jhRTgWZxdznYsQGHn0YfcGQtKcYHHAQH4DFwEryI8oIH0Qd2TyFR4Ca8C1q94VlIom6jDziygQFNB+ChAvBiHXgRwX54BH2yeIQ0sH0c'
        b'vAevr4Yk4i76eMJWQljuUnhvvjN40RW3BfqEZJBgtHc057itgSdZGDA7wl2FTAHbMUXgNDwwD2UUSoW6gQ4mfTc4kxI3Du5D0yyKioIvzye0Zrur0JbSgxb4gygC7KGK'
        b'Ufe8oMNL+iIH2AGva+H1NTTFgl0bYSMdAnbkkyV01B5Axk0gHtJoOFdQDdQyhA8a6CbWGuoKr4FuZbXwEWexjUxyZqaz+1jyqD66jJnEmAtCU5jM4CcOiVVqbV1Zzara'
        b'GfVBquqyGqWqGC9M8sSqmjJFlXaGfDDBQvx0ILNC9XpPZT7G1V1uXSu6grqCjG7Y7QrSYALVPTP+xtJeRL7vWvcffjPmyPF9N43n9k0yBm+P3i7ZPnX7hO2Ttsu2T98+'
        b'fnvs9pUuFbK5m9Cu0O2kXwDXL7t4RJr6Wo/5TG1kGed8eUpX7qPPlLKysL2sz0tePf+8XVcjH32W/R/el7PP+e7gZlsed955fXvw/ARe1+UDVw/wD8omtUzK/vTW49fr'
        b'rslKXvt84ke5852mfCUr+cWZW89P3RW9/d72k/ve5f562afBSUu/4cXWlqN6hUX+IfUe2lNwTzklcdGoPhwhl8CdUgptCxdZsR5pjwlSviwFLQhMQn1Gdi6XcgSHK8FV'
        b'FjwCmuVkv9GC58F2eDQZNksR1EZgn7ecNR5t81ceE7x+0Q+NF4xL4E6EoGETuJjJpYRxfnI23BtMkz0JtBX4Dt3PSsEptJ9NFErsRmwtYzlaO9K5eMNhOrjPcUin1g/9'
        b'Qvabb637zVy033igddnZx+LlbbC3BAR3iboLXxENevyD+rksr+B+Cjn6tH4e5eZ+0G6vXSu/ja9Psrj69FNsZ5lF5HEwbW+aMbk1uy3bQFs8fY0Kg9qgtnj7HOMf4neG'
        b'dLFN3lKzt9SQ1M+mvPyYWJRZ4IRjyw4tay/uKMZESIjTyjdwDGU4y4y9GUZlZ7JJFGYWhRlolLHA74Fgwn3BhM7yLoVJEGUWRCEiBISigZGJPp1JyDF5TzUjV5BgFiSg'
        b'VEIR3khbp7ZN7XXyJ2OVmSR2fbS2z6G6pliL+OdKlVaDR4LG6yltzOyC1m0QM3zD2jYDJ1tD2bbDPLQd+uFd7wecn3VPPMiXUZdcprGfYUvEKJI7bEv8fwRF8hle49Ec'
        b'oUsZKx03+9LwVYsZDqJJkhEWQItp1BWZB2ctp+aQ0C/5As9OahZF1ZZIVRtqmKSp/o6J/8byDkFJVWHZAorsdmD/9JjYKA5VDA5RYB9VuhZeVZt5HrS2DkWuvXgcL1pb'
        b'mo7ve2Hfap/xbLhCvGOz6LWqqGVv7yk6IDnMTfGKPh1lF1sXIy95hXeA/mpF/JXmq/vOpft3HXA73Jc7sdBv5/GJZ7tPBZmjbsRkjDNHn4k61T2uuZBeLXvdVTrJqfKy'
        b'8q1ylukXTh1qan+Ib9PWMgmLLD6FmfDlCBnGo/C4moGk4PaCx5gVkweBaxHyDCm40xAukSM2BjZRlLeYs5wPbku4T18UuBSDQa1LgltZpapsZXGZRqVU19VoihEAHR1E'
        b'locm6/JQx6IEQr3WENu0rmWdMXhng77BqDVqO2Pb13Ws6xp3aKNxo8XL36CzuHsclOyVtEa0ReiTLa6eeB4HGLXHNh3a1FVhCppsDppMgpjEAqEhyTDbMLvNzjjeWGpc'
        b'bSztCDUJgvEcDekVhnTmm4ShZmFoV9x9YWSvU+SwucouUyv77MpqdNV1mvU/YqpK8VQdXdslwyesFk1YXzwlf8D5uSasBsvlxt7o660TlQgcBlk9eoxJ+l8QCHDHmKQp'
        b'zCSFs9wpvBBGLc/1umBfYZ2Pr88TUGKKio8qD42udsmgCgn+BBenrk4D57FUJRqhyJ5ikvbThRwiE4haU5TaFxdHkaSeCPzp4Zb5sRwshItxCSFJH8+wytx4nJmHaxdT'
        b'DCDbB7d4wyvwfCwLS2xi4R3YRFK/tdiJQltrWFS5U3zXdC5FUNp09wT4Atwfi2oSR8Uhru+WzhX3wvQkATDEor6YRE2Sscjzt1UivHqIo+RfpreJ8q2ldcN74BQ84hyL'
        b'GmUyNRkawC6SujoogIrHpcnlUe/YVVD1LnmlDutFsQh3TaGmhFaRREU1wXiVio/KfZmnE02ndHi4JsA91RsrYtGgjafiwY0YkrI2cgKVjguP7k3+aJOCaRUxOCGFh0vB'
        b'deSfSk31SCJJtz8noeaiRolKiq+5xQpj6unxHNgBr4LL4DpqsAQqwcOXpN2iklELMZXR9skOk7OYbBMQaL5UocFM62xq9kzYTnKoAlfrQY9Ci1o1mUqGO8BFphPP5eWC'
        b'nRzMFKZQKaAxmrTfItAliFmrRe2XSqXOLiVhkkUqcEuGl6E51Jz8teTptcle4ChoxGg0jUorgJdJC2zyDN00Fc/adCod7AN7Sfkax/wQaIS4rhlUBjwPzpHgcLAfnPX0'
        b'gbhemVQm7GG4GHCgEJ5Dv23wOiI4i8paRDPhxxbmgpeBAV5HBGdT2Q3wOGkIuRMjyIqarPd9lZ9EER5hGbwMLsJb4Aa8jmqSgxibM+AcSb4rwpFC3W8fNZmWa8pmMO0G'
        b'WvNTHDFTgaqYS+V6zSBJf7NiIioI5Rz8x+r32T5Md6A+A1eKZsHrqOJ5VB44GkbS3poTQRXibIPXL3xpwXhmi4JXc8pBD+q+66hF5lJzVyBWDSe+MtEbMRaon3MFTtn5'
        b'662Jz8eCl8AhMRbp51P54Bg4QxI/58wn4reoyUnsr9fIGIKnIS6kEb7Y4IjaroAqiF1EkvqWuWKRn3fUmkPrctMmMUlD1Yg3OQr1jqg151HzoqJIaYmgBbwATrMcUWMW'
        b'UoXwEDhPsrgZ64umE6qHfItyxopZDGlScAsaYBc86Igas4gqAjtcSOKvo4OoRFxedWj+zNwIigyW+oXwxlKxI2rJ+eh3BUnoMm8chUUMUavpDfroGdYN/AY8OAs0pjii'
        b'llxALYDHwW2m2ed5IoYTNfvyyKpJK8qZXHPzQVuwyhG140JqoS6TJHzVPZJaiot3m2n3gE5neh62wia4FS0letCMhzO1CB7yI8n7OZOoSjwR+asSZycVMtDi/dBYtAoi'
        b'yhbJ5r5ht5QJLF0fTZXgyR1sLzosq6EkLIYv3LoBXGuoBs2o0RdTi8HRWFKiB1qG9KiFtoBm1MRLqCXwNNRXffPdd99Ni2GEpFFzLIt9nxtnFaeqJ1NVuHrqaLdS/nOU'
        b'OqDgAq3NRy376Z+Xb9+bkQfmCn5V8dFKx66unpM9W3siH75c9rsp/Sknbj9X2tJkF/ILw98/Pf6aX/TyxNotjsX3P0uW+QqL/7rp1396+8pv3nlcdK913MzfTcuZuOKN'
        b'6sj+Iy6XJ3B1GS+zt24qeONK1LufXXm37cMnM6Z/qQtbuGXJJ99pjx1ZstX57Gt6cXjL8SyLs+zPSUstzTMUM90B7eTQGCX1/0VX7ds9Gb/f7bcW9Eh+n+u7Nrz29Ds3'
        b'rla0TF/556mntvu87Xh9oUBemtHT4vEo/L1tf7IIqrdun/rx9iUWzy9KFvQ0bnxEu2xPi7+8+vnVW+d13L3A27Ct61fR4R88+sfho54JG55oWV51R14sSDn61xsXDJcT'
        b'Yna1vfXysgfP/e03796buC7Q+92exC3F1+Qv7nV778lLx9a+cOSTRS//ZbFi6UeXBUcTvtv+r5RDb5q6q3dkes5r3bpwe6CuNdz/7elrvqbvLqjoNN9B7CCGXSsWoeHQ'
        b'LM3FJwR7pDx4jEZ83wUWvLwKniWQbRXcAc9gzAbPeNvEiDM3PiaHO03gDGzJgrsi4K4cWaY0g0u5w57AADZsTBAwAsw74EVwFnF8LVkZYEscuIQYzniWD3h5HWEZeame'
        b'WnApPVcWRo559rApN2hwAEfZaP/ZBrZJ7J+BK2SwEBHQi8WDYKjPxYqDdGXFmHWpH/GdQMAuFgMB09lDIWD0zo16BvI9FHoaNEbaoGmbcnDm3pkmYYhZGIJBnr/Fy89Q'
        b'NwwRIozk44JhX34/G/u8/YxWn3h8p9UXFtFl9UXFdlt98dN6ChhfUsorpYwvM+d1DeObN7934WLGu7S4V1FGvA9JKVzsI6UQHymF+EgpxEdKIT5SCvGRUrCvn8JfSVEk'
        b'gimKeJmiSCLEC4tQYXaM38ffOOAPDukssPnDZV2lNn/s5G6NzZ848xXa5k+h0+jXB75l03l079yBzArpBTQu3vp1GV1CYxLIV3tMQkE/n/H7BhhLbf7xEzs1Nr80spvF'
        b'+CkmICHxlXFDArCjz+h3ojw89an9LCfngA+DwrqEXfO6SrvmXfQ2BcWYg2L6KZ5bNHFa0xB+r7N4eRujW3XoYY/oh94BnX4PgmPuB8d0x5mC483B8T0xpuDpJu/pRq6R'
        b'i1snsNOnK+5UkMk7CodY/IM7Z7dnGvgWYaBxvVko6ZrX7X5xwX1hXK8wzuInNk7qZ1OiSd/8QehPGIdBhww+g66fjfwItD8UehnitGRbmJIkTvGlXvV1SAljvxpKI9cm'
        b'72ajkf10XoEIt4ewCpPxZjRiSuClXltLYT4Bi7nZNO2GGYGnOz8rS7+fH0FdcJnK/kFOAR9MUkM4BfZ/nFN4JnbejuEUds10JnC8JKo+++SyBiunMHmaAwOsSjdJKWUt'
        b'xch3t2IRNmbTKQfYg9l02AxeUKd6tnC1mGfL/4I+/GbikeP71g9KD9/OdjrScuTtt7y3nGiJ2RZlIlz7q21A5BSHBY/H92e4X3YMAwbQIi3gvnrTadZ14wrv3rdL32DY'
        b'cRkV952b8a1/SWhy1JMKu90jIutlgwdEoIkr4Yy5wtrOepjV1ZcZOto6ja6sTod4zWKNqlylUVWXqeq/J46suosoZtWdzaFE3vhMpzWxLVGfYnF1R0twXNP6lvVDlmCL'
        b'AC0/hgJDQZu9Ma6T1enWyeqINwnGPwMjzevjaFHJzz4pEvGk+B7qtw6bIEkcmnbH8+Dpzs/GQiOW64dZaM4IFvo/PzFGsdDsMSYGL5ewlFwPeM9Rw06HdxAsuEiB9mB4'
        b'lMyNKZOs0NPnvMs57ynUHHWWfzhLi8WM5bpcZgasHpwBLbN0LRbz6Sg5e+eVHW95fBUbXRejO9F0Jkp1fbOqvcD4vM/mcO/eIk5s7S2KEu1fa++aZ3STsB7jAVAA2+H1'
        b'CNtwP7CJjPjWSY+x3B9cQ8z4DiyBGhA/gS3wMBFBcaok7JGDB1d1YDp4jxC6DE6Gp8aQqZBjnQpzR0wFoRfGG51xzEEo2RO6kruSuznnMi5m9LDO53blMrNDKOsVyrqU'
        b'JmGsWRjb6xQ7fPiX/ajhPxsP/6fS2zRs8Of9twf/swh6uXr6vyzoHTUBxt4ZCslA13m6Ui95oEUmqiQ7wi+Z4Xii5nCozkr0yKwS6ZqyACYw2J9F1XGwr8RpwRRHSv2X'
        b'oH9SWjX6rsgsJrLbfVh6e25fdDPNOxAdE3WxfNtXK3wSfFZ6v+ndfKGtMMHH65XU1l/EiJc7f3I6SvX8Z+OO5v5R9MdwOW+HvFzczA1/0/ir375hf6N1wnafd4+Gi78o'
        b'/fPqL5VO5Q+z7ahPckU3PLDAlgD4W+AC7AIXsnOkLIqDuOITWTS4Bi/BrY/FFDk9PQ7bEP8Ad0fm5cBduRngIofyAjfB+QLOZG3DjxDcOler1tUVK3WqYqWiTlU//CuZ'
        b'LKusk2Uph+ccYfGT9vpJuwovLjL5TTH7TTHYo0ljXNcrDEWfrpQreefzTNLpZun0V+j70qReaZJFLOlKOu5syLB4iTuj9240bLR4I6DlZ1Qb1V10e1VHlckr3MDpd0aZ'
        b'97ug6ajPGiaU5WA6+vhVKoUSkbT+xxyhYOH+iArtoYbJZJdwflCn4GdVLGBksjaVUfzDsw3cbXhOcRiVSTSrWHoeOUKx09uX88jMYo+hVcDhjzFXUAhn1Oxhb+JYZ9aY'
        b'cQMzq3zkzOKPMbO4DOY6pMNyCgubQ5W4H42zTqxXq7B8obbQeVZJ9j3fMkq9d/s0rhaLPT5O+/PhNyejXWXVwK5y02mSk6N309xfWd5YrFwIdhq+XKRQ5iiWvsYphBxh'
        b'E31tRfuK9mlTVxjPb/5Wvtt3h7TcWOWsnbxwrVux83hhcugCh9/EdN698GjNgi2rJI9SLFThLxdByxtbVjgubAub8nzVZ8pf3eAWcd59vPiA74ES3jtx1JYZ4+oqahET'
        b'jnHYVNAKmsnRqR3FAieK+HRRQyWjp9NSD05h9UmsHLkwFatHdsBWwrkXVMN7WbBJip7blUdT9rBlCbjNAtvAdXCY7HbgyEoWitRHot2Ok4M2Xhrco+DLTNzdUDSNm3PA'
        b'RdRP6JlbPDqtDl6QOD4rxz1y0GPJnI0BH5jTThWqIVN62DeG/7bO6FoOJfQ7KN0rbZW3yfXJFqHnwfi98a0JbQn6lIeuHv0UxznyQ68AY3lnqclLYvaStHIMtCHa4j8B'
        b'zdwczGB5tsUbV++dbphu8QvqlHTiqS49JTX5yQ0pf/DyfSgIMDgblZ0ZJoHcLJAzX8uOVR6qbF/RsaJratfU7sJzMy/ONAUmmATTzIJpX/G53i6PKeTo0xHLKPLX5w1Z'
        b'DPh4MUArANaH6+OV6epqyp++zTLNwydrQsmQw2tNAV4VhrVJO065hVkUcLPUoFVhAp73z+z8rBzZIX4U1e0yYzhHNnBIQvZe7gBHhlVFqXLu/03w6TnGChHErBBb5r9F'
        b'tU16Ex+Sqj9IrWdWiK8FYmpW4lk2VVuSeFlezQRySu0pwaxUFuqtKpZTDBNoDEPsW91aDno8OzBEwgTOXuVOhcwtRIWVJDpkWFedLREBVHzVPjtqbknDgYmOTGBcHUK4'
        b'hV9z0B6vWaWYzAS+XMCjnPyL7ChxiVNYUD4TuEEcRs0Na8RjpfQNrzVM4OfVM6gG5ccchBs0JQ65TGADnUit8z7JQwW5Lw2PZgLXBSdQdcoIO0Snu+u4ZUzg4+U+VFTU'
        b'DlyjpY+rVEzghDgptdB/K3681Gm2lAnc5uVGiak5PNQgVZrKlUxghmsStdlplR0KjLmwOIIJPIrYQXvB13aoRk4HAqqYwL25TpR34Rs4z6rf0jOtMuQgPypO1MNDJCU2'
        b'LVtvbRCPKVRVQxsP1d199XghE1g5JZ/q9E7CpTscmunFBL5UpaRej3+E4RFvuYDLBC7KLKfentuEH59z38GfqsKzsj3Ni5Iu7WWjwIZNZSRdxXIXyj+llocaTvpyeBHz'
        b'8HvSDdRjUSuNCJq8VRHCBK7ZgHaQxHVoUSrRuMaEMYFPosZRKd75OJD1lfM4St0W8huOdimaDd5Js/fPm1YNo5xOT3jrudD8J1l970xNrWmNEPxF0Jm8w4W3kdJF3il/'
        b'c+/pNOm5sKTfvxkWniz4W+A/01v7G//J4VZ//ucZdHz/jMtr/3Tx8Eu/uFUrrDgY6v3eQ+nHuyceYX1Ke6zY+g7V+YURFtbWtG+u+PeBDS/9zshprmyp3bn/LXlZVlnG'
        b'4oawr2bsT5uXedWzZsbh2vfOVt631H/gH/Gpc26YR3PLvYrXaz52+sQ3Y/1fzlX+69upuZKTS/8cVPmLhY88MsNX38o47bjkrekrU3Oivvpg5RdHZ+jOXVn+wcPj5/w1'
        b'Wx59uTdYUb5waS64d9nhf0oyCxbMPez6LmvT9n/abwr49aavpyWXVKe1v2g679l18n2Z/OT7X6btdzrfdZ9Vkf9SwF9+Be1n9K5v/8ffFv1pdRTccSjg1feO/uNRQ/Ld'
        b'r6I/8JhU9vW/rrz3YOfny9y/PvvHgun03wufi2g+9u0f8k7kXzne8G/e/vf3BUdekrAZdqx1HLzFAMvMCUOgJYKV4LqUYFNwGlxeCDej/VEalg53ZaE9EFxgrefAHczW'
        b'+ULD0gj0ePgcgHqbo6NhEzw6XuL+E3e4Z9kE3W2boO1nyF7ohlf6UkX1yuLKmio13j/qRweRXfF9q1S6lkuJvAyxhjqsz6NP6UdzSGTY2Osagj4Wr5DOQrNXeK8gHIto'
        b'PYzsVkeiJWRQGINbVUZFq7ozyeQxwSSY0OXWlX/Oo9v9nG8PyxSGNjisKCRwM+Qb3VqLjPmtizqjTaIQkyAEB4sMmlas8+QmNChaPVFWvkYNo7aAnihotTNGd7Lap3Tm'
        b'd407vsDkJ+126y696mXynWoSTB32lH62xc3doDQWdua3LzJ5TuxyM3mGdylMHpEmt0gmstQY01rR6da6zOQ2DoW446JDkcfVzTB751r9WotPgFGENu2kTk3X7ONrTT6R'
        b'Zp9IA8/AezgYYfIJN/uEG3hYRuxh4BgKjdFGhUkgNgvEFoGn0cfo0xnd7t/hj5oBfR8dJBr5DBMQgys9ziwYNyoAN7YXySSmPaAjwCSYaMv06d9tWaxGDWkWBJP+GpvW'
        b'kc9EG0uZZ76HsFG5fg/xsb4E0MSPSor6zl1oA2CdSffdJ/S6T7CIPIx8I78zuN2pwwkNEQPdz6aEopHJHjqJ9uTtzDMmmZwCzU6BvU6BOCRnZ05TXkuePu/huHB9jjHE'
        b'5BRkEfoNg1H2fZz1KoXm+5HT4PFOydDppMEC0jEm0GWcup6ySikWcX9QSvEfkFcQ3mooMLGZ3n2N8S4jrFNh0zxqMUJFfEppT7S2WeVsJWsbfzE2wOMo2duo4UZ1i7kk'
        b'nDMqnEfCuaPC7Ug4b1S4vYqDuDp2OUtpt81+OMJazNdT6+jFDvMofiVCuXZJSqVGpdXmlvGG1MbeBrN2Uzbpi824DmFBbC7EIhwjMSEqtyeIENHY5DACEdoRRMgbhQjt'
        b'RqE+3iY7KyIcM+7HSWO4jCY63AzvwbZ52Hc8KJgKDoPXGKOO1akKlvYAJvB+u253tAuIckpdtSDjyBdL9RG11IGdl4sU2S4P73DZ4veyF2kyloZkL+FmXX2897uvv9tX'
        b'HJXE4r8lmb3jvfQw+7lfvWUP1rrf7kh721LX33Iy/L2NJ+9Oe3SvQ9+++B+pef+f6epb/eqPJm1wSvvb+Krl075KFV44Xf7g21+mWf7knhH02ec5j9rqx88vPdmpPNcq'
        b'F5yZUsWZ4NySKHEg/Bvs9vNmtj14Nsi28/GDmX3xFOjkweaV+YN6tjS4CnpgN3nUGxwH+4j6L+ywt2kAu4YRDWBwAXGPO7F9WgbcFQ7v4JzhiyzQ5NjAsI3XYvMj5LJ0'
        b'eB2eJDLUU6yo9eA8o/97GW4DbfBANmgGe+CeLBnYA/bYUY6eLNi4AO3JmGfNnQM7QHMe2pXhrggJOM+hXLWufHYdvAHPEdp57uAWSSBFT18H5zgUz57lAwzwBEEFHNAV'
        b'ApojEU8rz2As+eBuuTs8zYZbSuBVpvbdC+C9DBlKJZdk5siw0VszC96Gd4P+18zt5s1DmVu74uJq1dri4npX6zSRWwPIJv4axWzi6+wovwCDnUXogxYZtwiLyO9g7t7c'
        b'zskmUbhZFN4rCkerYj/Fcos21pF/Fr/AY/GH4jsXdi7vdu8u7F7cU9AbMsvkl2T2SzKk2B6PO5twIuF44qlEkyjKLIrqFUVZhEG4gGhbisGYD738jQs6y0xe4QgvPPCK'
        b'ue8V0x3bY2fymmX2mmXgWMShBk6bsyUgGP1zsARL0D8XS9AE9M8Jn3I7DlmxHfvYZVVajRxXn1OmrlvfZ19bgxXolao+nrZOo1LV9TnpqgfPTp4uJMNNWkJ+hgjKViJn'
        b'VHNiNW7tIYrhihnGWGdH07NovGr/79yfa8kn7P0x/iTqpksSezi/TNuWIHeyBDVQKwaiiIk0nXuO7rMvtip7Sug+jlZVVY5VzCgxY8Vgn1ilWFWqVMyoF9haxhbiTFv3'
        b'xs1UV8rFnM0U6asfUX4lKh+VyS3GnSmhNVg9eEjZGh3ukFHFuqAUX1uLFV30/fHFbmOK5RfbRs8zF+06pOjCi8t/ctF2xcxwfeaCBUOaOu5i4lgFD+w26yjGhpE5k0Mb'
        b'7f/Fo+qxTuTYuepHX+bQ2okoiGeIP/xmHFEGP46PEy4tHDhQ2OoTH0vVfMD55UdsCU1YqghfB9CshXvI+mxdmxOfk7CGzGu8+A2I9NXaIeeo9R62Nh0WTFZLbBuCJ3al'
        b'PeXtb6gzpnRkmrxCzV6hvYLQIesPl3TWWIsKOU0YYryHpWhPKdAd9yReachSorD/b2BCMmTb+OHUeZd4NoIg+AetpvZoiVOsUhUX9zkUFzP3HiC/U3Hxap2iiokhayJa'
        b'ZjU1tSpN3Xqy9mrwSYimGjs1tsr2OWOrRoVWW6aqqioulnDQ7GIChho5Dh7lzxpYdJfjprJBvX/g+NetjWP77XegZtEptCVmcj/b1dm/n/phZxzlFWSo7A2aij4mzwSz'
        b'Z4I+De10hvhe/1j0MQnjzMI4fYoFpVrXK56GPiavRLNXoj7d4hFgWNgbOAV9TB7xZo94/ZyHzh79LLZzGDbDGel8xaZcPFsWPjWejB4dtl7ihINWbXaGJFMm51EOK1he'
        b'CBQ0Yk3SYfPF0fr/661oYO53G0TqShoj8zZ2m2ubAP05t7mqWeUs5LP+XmSdQVPswgBSJsh+Isb1CBHbzOcFCA9ztvFHoG4OvnIDI3gl76LdGVTuhYHTToLuuUp7FMcf'
        b'FWdH4hxQnOOoOHsS54TinEfF8UmcC4pzHRXnQOIEKM5tVJwjiXNHccJRcU4kToTiPEbFOaM2cEDLoOc2+8UuTBsqEf9x0Ws4Z0JayglxQd6j+BJXkrvPNkrlqvRF+aNV'
        b'7cLA6dVigbVfXC/6DS9ZGYryxMY/bKX/qFZ3I3kGIIoDR1HsTuKCUJx4VJzQVlqbXZt9ObuNczF4OD3KMMT9sKxXJ+B+d9G7lvOV40dRICKlhKBSJowqxUPJJruVBHFh'
        b'ZQQdPAl1GCpasoYyN6IMi8En/2rEFfdx8BIy1oqRW2ZHDf64UNYtogM5++2H35aC9jA+2sXYqCL0wA0QuFEpPQ8NZxeyt9mNwd7Z88dg2FCI/aj9y26TvXVvGzNu6JHg'
        b'o3+iFhpWWfyTUa2uUyuq1PX4YphKlVhhbRo1QqKK6jJ8s8zIRxJqFRrFKjFupgRxqho9pSGPZsxOyhXXaMQKcYysTldbpUKZkIjyGs0qcU35qIzwj4p5Pgw/LBXPzkiW'
        b'4CzCkpKT84pyC4tzi3JmpxagiKTcrOLkvJRUiXzMbApRMVWKujqU1Vp1VZW4VCUuq6leg5Z9lRJfeIPJKKvRoGW6tqZaqa6uGDMXUgOFrq5mlaJOXaaoqlovFydVM8Fq'
        b'rZiod6D8UH3Ea1CbKRHwG02OtXnw+EkgdGGf7foeW/NW1lQp0fB62sNWSMs8b/2C2mheniw2evJkcVL23PQkcYxkRK5j1okpSRxWU4tvAlJUjdGAtkJRdawlIt/YFD9L'
        b'PjZgyuRl+/bT82PQJpMb4/8JeQ3bqAbEMEOAnVOubgL6BvfCg+ASuFWJj4alcnylTdYCqM+CLTlcKgic4ICX7GTkiOP/K9xN+dOUN296SfUBiROlm4ICl9SC/eRoeC7U'
        b'Z7i4w11ZkbAJ+fPmMXkUpWOd7ZycjByaAjvhCT68BW9Y7YM+1PCwwUn8B9IS6fPsxZQOrz4o/mg0VgKPyMJ2wdn56UQAAA6CM0QIAPdKwDlqXpIdPDgRXGYOwnRsjKfF'
        b'Ua4l0pBp85kDGf/xxGSAckgpqYpZ/xyTOQe+JBqaN9RnZ8IWRGpkQTq8BrfBndk8Kg2e5sGrYN86ongJd8DjsEu7mkvlwm0U3INqsRG0quPKttJab7QdRQa8tWsvOd7Z'
        b'oX7jr8kZHXWvCzo/3Sv82OHu7AesRduc+IakzyojP/z07qefv9EcuejN7R7zBAZ7wZ/3fJznPu6588WCzZLPZ9Den/772PyTL1+6l8g2bktrCD0VMfuI20HzRtmDN+c2'
        b'339515NXyu43t3xa1DWlt+dlbeFCxXr3u+J7xm//HrD/jTXLf/trzYd5eWv7lf8w6sZ5pr3w1w87ytvXfzh/mcf5vEf/9t35549/f+fSiTvql6oDPnadWNC9dduVguc/'
        b'fK8/+13eZbvP8345LueNr/sWvP1O+1nZ3w7/6l9/SPgHqyfRU/hgVuGTypxT0zNObP/ylVS5zyXvopb3hKY5veW7/iVdF3lyldvVSz2XzmY4bfJt2wDD7/7PZ+w3fxP0'
        b'hL9A2E9J3IkQJgQ0Uo6otSWwa2aOThYOd0ayKA/QyLEHF+AuYhmwZBYwDFoV0OBmiNWqABrBHkZadE2ZmCXPzJFmgF1wT3amnwxLqnzBDU412Ar2EWlTNDyYbrUWfUlq'
        b'vcCkFXY9DkZxSTrYnAV3p+eEgBNwN9iN88A5eMBtbNgTDg8TUpPAFXgS6/TBbfLhVqXwELzyGI8fcHvDYjR+UAYREF/FlJ6Ds4uEPfBQFqrbbsYuIQ1ctQN7SvhExJQO'
        b'72qz8mT45iY0uILBPsoxn4WGNNhJKg+aoUGFHIYisBfeoLjwEA3vgOvwOOGjvOqWguY8J3CGDE42PEyD3Y6+pM72aCDiZ8lkza9CT95h0V7ZRHoGrpesRs+Ng+eHCtD4'
        b'7Dpv0PQY33gGrs6E57F8bJcEG1RYGzcLngglUz8CXOfC7XCXiBGUnXCCZ1B29fA63J1NIzKO0cCAHjhNdFICQ4AexZbPkedgEm/R4HCVN0NGCwsYMY3g1KIcbNmBtVNc'
        b'KtgJcE8lyTkysxA9CVrhFRvcdklmz0FP3CHRsgUL8NOhcIcUNXSuLJ1DuYAudkrwKonrz3kah02jBmR2QyV3iO1SI8hQXIzYfGb1ldtCCDf6Ns1wo8v5lPd4w4bOOJNX'
        b'mNkrzMCxeGFbdrdJH/qGdC43+caZfeN6RXEWoaftlM6o2TvDMOMPviG9E2abfJPNvsm9omSLEBvUuk0nVsVT2hs6GrpW3w+K6g2K+hAnnGbyTTT7JvaKEi2evga2RRhg'
        b'SDAqO4u64jqzTcJoszC6n+K6SR56+RmT2tYefG7vcww5iL3xkFiCQh4ERaHcukXdihtePSE9q18KNQXNNgfNNnKMnIchYe185ClDlB+s31vf2tDWgKvh/8Ar9L5XaBen'
        b'q8zkFWP2isEEJhJyEky+08y+03pF01C9UBlucotvwDHJIUl7REeEIdmQbPHwOVi8t7iz0OQRbvYIx0/Ku3TmyDTis/gGHZMdknVxTL4ys68MJbcKFv2D0D++7ZtV6Dgx'
        b'3MAxC8Zb/MUk0vpPHEIixaGddhaRn0UUZMjq5JhEE8yiCcwXe5NIYhZJmC88kyjULAr9is8Ndn9MIQc/3O9EBWMRprMB/Q6RILgxEoQW7OzCzlj89A8fSI0canhYlQwR'
        b'Zw45qDpJEXHSiHEWhIUQl6gBoSYebhvsaXomFjv87M7PKuc8w0+kXnJJcvgxcs4KRs7JLcaA++kyN2sj2WRuCweFfcbCjsVWmduTCYUDQB1DKARqbRgqTKNSKGU11VXr'
        b'JXJUHFtZU/bjhbGc4lJ12TPTuGQYjYtsNIZgGhEn8L0k/khBLWlADMSfmbjlKIXmLI4nREV8P5L/qbRhkapGg2fXs9KlGNZoy2yNJh/KKfxUEv1HkbiCHkIs7mQJC20B'
        b'CkbgReb+MxOupK1HFwzh5oDIzUPb9vt4jp+HcE0PZV2qnpnmipE0x9pojnwW3uZ/S3flELprfgzdK0bSHW2jW/bDXNRPG8nMMkVofWYyV+E5dpOyzbGoQiI1QGQNPQcT'
        b'W0ebuIrcaftU8v5fOELYJmE9OTGK90zGcgOtWD1iOdOqVKvIbbylKkacMOpBfEOvVYYyT11dgdomVaepEc9VrF+lqq7TipNQW4xmdcNQg6FmQw+umSyPkUdJvp8ZHuvq'
        b'Dm5uoYQmpkcz3MHNiFzZ5PkIaXJm0eB8FuhWf73zFqWdhmJdNc2H34xbceMIOf/g+Zqn+XhGxZTQs4qy06vKvadtX+38mxhxzaTY2ZMDF3l1BLz9SjuP6pjm8Hl/j4TD'
        b'AP5truAshrSDeFYKzmFIC04vZriV+DmYWYFNwJAzmluBV/PI7Vjj2OBFfHksvCkevDwWHih9TBQWzjpXZhF+gbWchjsLIt1TnnrwYocPPPCdWK620WoNIPAW236SwxZH'
        b'SuTdNr1XGGYJkTwIibsfEtddeGPRK5xX7V+v6w2JM4UUmkMKDSltOQg9tm3sFYT8pKMYfJowipDaYYcwyxz/K4o5W5l5jXHfM9gTYZ1mGs29/7I90ZPGUUN9nqqOEWzq'
        b'qurUqxR11k1cp7XK8cgV23UaRbVWMeSq7NL1ozLCeSQQgXFCSQ5Kg7JC/xQVKk3JD0ibxjpGtFpfhGTvITKkqNA3nfqL7CgdHl9h8EW4gxEiFaRCfcazCJHWhqkDFGyO'
        b'Fl+GkTN7PnOx3rn8fU3HhemRZcqShc6vCnp/yRGpUrxyFG+X06bUbyfURneGHTo/sfPl3D+u2ybfUcJ7p44y1GhqXdQT8iQsImmAL/jCA0ReMSisgJdXEnnFFnCPMM5s'
        b'eLNqDL65BTHI7QOMM+hY9T22sUM0PbWqumJbVxHAVu9jG/6josiMzLDOyAY8I3uF4y1+E43TOutMflKzn9SQYvHyNWiNca3r29Z3xuzdZNj0YWBYr2SOKTDNHJjW651m'
        b'Y6N6yWeo1RIzSXc9ZaY+xVzpHTxhn05xPT3MdGk1mrveeJ7+gPOfu07qmVC9y/BKPPP2vgNDVcz2YBRiDogahkGedT7K0UqNL27WYPHqMLOrgY1rKzWoTHeQIuYU+BDJ'
        b'ZlLxXzO6epRNj3HCMrAC1WjUFepqRR2qpVr5NPBVrVpr3bmj5dFjyLGfLrxXMhJy0oA2E1RUkFxcoFqtU2us7atEvrI6sVJVqq7TjnlggNc/RIG2ZpWNoVAj2KWo0taQ'
        b'DJismS4qV2m0Tz9O0JUxFCXPzkCATr1ah/NDYDkMgzexxkYVKiujToHh3Pcvo2MpJNrn6magb4XgeGxWLlpymJu9c2X56fLMHGzf1RRZAPXZ+ensAgk4BzfDlgzx8lKN'
        b'ZpN6OZ+aXeG6Cl4Cp3VRKAvHccHDpOzk+bRxJAcKXIP7ixBI2U+vhjftF8CdYBe5oafOuwxeB5fhHifU8bALXxV+a4YO2wLDaxUVWhfd/HSsaVcE9dL5+OJb2AzOFTrA'
        b'8+lSXExLRjbcSaMF/JRkHTgQAs8Usii4H9x2mgsOgpvktnJwDXThSg0SVjuQ6dwFsvl2FDgRPPc5HjglhHfVi8zdXO1B9NikU0cPv5mAdwDT7X0TEDDb+U2W8ZH/DtFr'
        b'qhYnpws+im8nvpZ7hpvttPCVmGu92NBVFx0dXcf6Ne+Q05RVPnN/u6Lno9Lj7rkhG4wJ7ectm1f0riqrbmEd+oWDcNErO379hai8cOMvvw0rv15yKLMtyLhlE3U+Ndbv'
        b'3Q8vHnl74YfOj9cnTmv57RtOH69+5W9RHHKL6jtbQxfsfkfCJ1ehxsCdqWh7s0o/wYXZlGM1Cx7OrX+MXxcAWuALlY7h+GKcpnJ4Hu0otp0nCFznwCtqMaPEuQfeXBAh'
        b'C4HXh1zA8LyYCEmfgzdWZw2KeXPBRcpJwPaAF2ZaFSHvlQ/Z0+AZ2GoTwsNT4xj57oVweIfASYwlwfPgDMGTbLCXMbC4MwUcHTR3B6ecbKJxcB2cJnjUx2E90cUkwuHG'
        b'HEY+3AGPERl2ymQPFEmEw57FRDyMyLj3Qwa/m0dsk4PrCb6pcdimMyyKbJMm6zZZ4oQNI2ZiVNqA9haPhfSHgeG9EfNNgQvMgQt6vRcMk1haLYXndYfckJr8Zpr9sEzM'
        b'I4smm2jyK2UmSYYpMNMcmNnrnYlFuTMtfkEdUx/4Rd73i+zmmPwmmf0m4SfmMk/kmgLzzIF5vd55I0qRGGd0jTf5yc1+cpw8nUk+65VY09Ct2ioGZf4Z0O9QhXhmux7Y'
        b'KZ6+ZxN9+GGb9sNRm/aw9mvCm3YDNWBamOdE0/jWmWdyflYtqHZ+JHXFZfpP0JLkFKMN4pk37uOYL8fmAMx+HU3kM4NbyvcJDn6SBExCCNQ9u+Tw1HACp425zSQXJY88'
        b'IR+DVAm7j7NKoyrv42nVFdUqZR8fbZA6jQYx2HPKhr74x8lWjb0UvnHHpupBAIf9gJ4SrXcm93Gy9C7lTgR+cBD8GKHKsZHLHwNQoBDuKIjB2cS1wo8x44ZyP4/avxd+'
        b'MC8TYjgXspMPFUY8Xc0Dtw2zj9ueHbjW4ukn9qQlmafII6gXcJgCC3Tk4mRFNZZ5KKxxpSsQIhkTimBlEoQO5uXFT46KJmokWMVDieVX6uqKpxY/0IEJ4jlVigrx2kqV'
        b'VUkFVRjXeTCFrVJPK766pm6MYjQqVJFqbYI4aSRLWGKtzg9gmYEbA4ZgGYdcghymjYNXh2MZqLfulUXpKKjACm3oGHiwyB3sA/vg9Sx4PZOaAE+5wEPrgFGXgIdY1KIs'
        b'uSw8E+2B1gzAtTSSx0De6ZlFYdYLyxEjCU8HOMGuAGAkjOnfgzIoA0VVvqguWfHLeWmUbhIK5K5wHdBtGMaUysrBncyceUPZ0uZ5fHgPngXndVhOFC2Hx2CzDKchp8UZ'
        b'MngUI6AIDIuGqjakSzOz5RmycB4FmyVOq4FhoQ6/YckBvgRfgM15rCGJcWVw8WFok0UMp1Qiy+RS9fAsH+zyALskbPISoDC4FRXYLAPHwN3MHDbFmUGDCxWgibzdqIo5'
        b'ucaPg1OwJysHW2y0szaAPb5E6zFlVUFEZg5uxVqUclcETQlD2fCwN0+d6FVBE3upFzzubm+djg1dth+Jn5mz81XwXtlq6kB6+l92xNOH33dzTD4rvRsS2HeGn3RTKbn1'
        b'0T+qIq5Av9f/1v3qX9b96uZm8QnK+GrBm6/O5Kz8w/m/3Cra81yi8rPgLXHtL/nVzo390+SLT9prjK/tDewGn7+5NPVo3+vT8j7beeBfBxoub3qySOb4t6Zvu467t2q3'
        b'vhobMef6lYsfrQp/ke1zdNU/As7x//78C+wXsvZ99NmDdx5eLg6KnmxX2oIAGJbp6cD+lKxJ1qNrVikdnQ93MVeSdKxIs0IvBnctdRuCvJInEzuXkDK43wrf4GF4Ch9g'
        b'E/wGr1QT5OM2DdzKysgJ94UHEHhmUfagmQW2JLiT8+/18GzhcHnCJNBFoJckhOC6eStBV1YGOAO2SgdeanUW3mAuVDngCLdgTYMMcBG0ghMcilfFGgevwCYirIgAV2Ej'
        b'MXvNIxfpw1tpOVLUZ5FsuH8BPE6IT4cXQRMWN4bBzcPO3wt1Eqf/1Yk53h5GH5c7YjRhXWPqhUMhhjWQgDOZ9dC81BlLFePxYXAB/aHvxN7QuSbffLNvfq8o3yL0akvE'
        b'MTl0Z8qpbHPIFOYLSZZl8s02+2b3irJHHah/OPJA3cs4bVBAcl8o7RVKSZo0k2+62Te9V5TOHKOXd5aZhOFmITmljrUEhBuXdU02BcSYA2IMc2xJKk3CSLMwkrHPCRh/'
        b'bMmhJe3LOpbhBD7GlGOZhzLbszuy7wvDeoVhpJRZJt8ks29SryiJOaP2F1sCQx4Eyu8Hyk2BUebAKEtweL8dR+LeTyHnK4oTLHyMHXIw7UB5+7c1DJfTuDLA7zPsfI6d'
        b'P1E/5Rh6UO1h+EG0FSJ+g2HIWP13FoPDTsp6GI36MMuZpiMw9PuZnJ8NQGJBzHH+FOq2SxL3xyJICbazsdb4mUHa68NPd4IxGkB7JcEGA2Bi6HGOhIN1+8+xclF5cySe'
        b'mufxs/hOHc12ijEaU9aUFRcTtQANflUj0UXoY5eqy56qkNBnZzusxLJ0Ip/rcx4mziLwfwjj8A15ylZZt/+MtbvbiNViyFDbSRGbAqYxffDwKmKT5WHApIDDchb0U9ix'
        b'p1w89AuMsZ3czrKukC5tb1Bsr29cT+zrbMRgdbG7k/vZtMvUryjkPMbOw9gploQZ/ew45wn91E9yvuLa8urn4LAqmhL5G+ItAmxuYhFN6+eyRNO/opDzGDvE9F7oZwiz'
        b'CCb2CiZaRAkogTARJRAmPsaOPhklGJpDEs4hmcZZJNOPiUsywTYRFgE22reIUvArR+bgNMh9TFzy6hEmn8heQeTT8/EWG9ZZBLG9gliLKBWl8U7DaZD7mLj6dJTGM9Cw'
        b'0CKI7hVEW0TJKI1nKk6D3MfE1c8ZQc8cTE86oSed0JOO6bG3x232NEdk6zqOMaLXeaLJeaLZeWI/i++Mpv1THGyvETqQSkQFTDCmWwRRvegTk8xQGkAoDSCUIlefYxsi'
        b'ws7xQ0rxcBb3U9/nDBaFQ6TDujANd2EGLge5j4lLenFomnycZh5JM4+kmYfTWGkZ36ntiuu275049ZXCXudMk3Om2TmznxXoHNJP/XQHk5xFD+Q0Y1gPTcE9NBV30FTc'
        b'P1P1afiXMXCx2v32rNBm5zJSI5pyqGclZMDdYFf+qNdz4Z+vc7GFi/twCxclazFHyV7MVVOLeUrOYjv0Z6/kLuYreYsdlHbYAqSN22bfJmijy9ltgov2I+wtohDv6KgX'
        b'lLOV/FHWDthCxNlqreI0wtrBhcQ5oziXUXGuJM4VxQlGxQnaXFRuVltzO2Ke4Kp3K7dXuo20IBlBi3ubC6mJ4KL7CBsUzPXivNzKuUrhD+QiRHSJto0MFeHXZZazlB7b'
        b'7Bd7oLagid2Lp9JrG7XYS+mNXG9sybLYx5rOF8X6Kv1QiJ/SH7n+2CZlcYCeh54MRHGBegr5gpAvSClGMWLyPRh9D1aOQ9/HWfMZj0LGY2uSxSHWkAkoZILVPxH5J1r9'
        b'ocgfavWHIX8YyVGCfBLiC0e+cOKLQL4IPR/5pMgn1dsjnwz5ZMpoYuOP7yyI3MZfLFdyiKpHTB8vaRUxVjk/jHnE2yYTwdirMO/tRXwxfl1ghUaBGWKGmy1bP2D0MMK0'
        b'YLj1iwZlsEpVpy4TY8M4BXPsWcYw5SgA89koT+akoGq9uKaa4ZzH4mwlrD5e8RpFlU7Vxy+2UdHHTi0qyH2SWFlXV5sQGbl27Vq5qqxUrtJpamoV6F+ktk5Rp43E38vX'
        b'aVTlgz6ZUqGuWi9ft6oK38qcnD23j51eNKePnZFS0MfOnLuoj51VsKCPXZS2cM45Vh+XKdjeVu6w06EBHX986dB+NoI1LK3dUGjDHEs3jHj/spJeSXLRihpYnUNB0lMG'
        b'sta9jjsYp2Q1sOoRTz/6Tc9N3AZ6eOhGWsluoNcg1NJAKzlKLqGG7hxah8F82SOo5PkM0jMsph4tUfVcfGciLqEalaq0Y/xYAWYkDQ1U8YCIC9V3SE2eVl/0xICZntKe'
        b'ueziUfFYgqeRlkXWMTxoWDTygaeJc0gvM8IkBZMHCfmegydmOCQQ2515ebK4mOgpQ6eIUiUXZ5Rj2Y5YW6sqU5erVUrpmBIgdR2WFyG4b7MhIiXbhIrMdFTU1WnUpbqn'
        b'yJAScHRCiVJVrkCoc2CKlIjXVqrLKnHuaqad0ESzloMmz+i6fYbHxRMPdTXRFBqsTegEbegTWt5HR32Gl/bPvkM/T9jyqKhciV2fYGSxWLtFUVVbqehzmI9rkqrR1Gj6'
        b'uNraKnWdhod6sY+rq0VLgMaOxrfgMqyVG8bx2PJ3JIjFA0E8RI5O1HVdmX4e0Nb9CCPYX1AMgytC8ItogVuCxpuD4gzpDLu6Dr/LtDPpvnBCr3BC18IHsun3ZdNNsplm'
        b'2UwUQPjGxJ51pqEsqrefkW1MbXfocDBwUSbGCYZEQ6JF5GOc15nUxUa/qVeyzmf1sE3SRLM0safALJ1lCksyhyWZQpJMAbNNotmGVEPqQ/RAUWuuIdUSOMFY0alqr+6o'
        b'RpymoyVYcjbwRKApONocHI0vdTCg3x9rLs8wTqRZn8Yz2RrLxjL9bZhy55JhB+ZDxz4ZgetrVeISNLLKEC9TJU9h/peUyDXnfhydVs09ux9B5zfD6LRdJfDEj2gXjz3j'
        b'hhHEshE0exRBz7LorhhAMY4DRwhsMk777BXaYmJ82GevWldbU62qfuo9BSMr9S88Un2ZSik7VjwIjL4fGG0KjDXjT2JvgO3igidlRBdYt6pUpcEdYe0BcW2VogwrKCrq'
        b'xFUqhbZOHCORi4u0KrJWlOrUVXUydTXqMQ0qVVlSgqe6QrlChxLiBMNzGd5cA3sZuWDWfuAt49TAW8YdrJcF0WPoOvz8ao6VEtajL8Za84tqMdPMrPeqdWWViuoKlVhD'
        b'gkoVWMWjhtFmRKkU4lpNzRo11lQsXY8DR2WGdR1rVQiWJKNO1KCmma2oXknUE7R1NYilJ6tz9TOtxNZV2EZSMSGpBPeOjqy8zDqPN4QBtQTUO9gCdAw9MJQSoafKmkGI'
        b'JBVr1WhLs2aDH8Nqq0PtSJ9WR2tGCeW66rKEEit6G0Oh7HvPIEpravA7mcXlQw87dKQrlCO6Ycw9aq1Kg5aXNQh6KUqx/u1Tjj1+UGvUJZcxWeyAW5ZFyNIzpFiMnLUA'
        b'HwtgBc6WrLyisExphmyqP49a5W4P78Hj8J5Ogh4B+vUrQDPshjfzwzJlcqwrEZELbsITBTKI2Ja4NC4Kaq1YXUnk9mDbKrBLK8/JhPvXgu2+PHfKFRxky2EP3KbD7/Fb'
        b'AA/lwsZhVpNhubLwLFmBLfMsLuKI7MGLVZPIKUF4kk5LXqOTw+XDaxQX7KFhN3hhoo5Y2x2CrfAYMJbOA7tgWxHcBfcX4ZOCPBregFdWziGaIHEF0YSgva5cig2MNNgM'
        b'98t0YgpfEXUM3tGmM2cxWeAyh3JDxIKr4DS4CI6DRsaq8qjIRYvbhjtlBcXdSMNL8AXQUah+HBjD1eKXY11785td+VdzYZSo4f9cPRKf4Tf/39zJM6hXW+4sFO+/JD7z'
        b'yfZfFyx49ckZ6T8z/rzzVV13imzRtby1n2z45Mof/b7dcfyGdLd91KOGtP4lr7n/5vaG6GNa5wUT/u399/GxN/5naba4mc/5hXfH2V8GJG2ecqP+lzR94UTyzdJxjz7o'
        b'f3lq2esdXzW9/Ps7H6dWvqu7/1mizxSv7PBvX/njc0dr1q5K+PLF1OL3+97wqt1p+NfePav+qv7i4Wcz3qnKyfyi7tNu/sLD3UVZk4oa3stffEo78d0rZ4Nm2H8wNSMp'
        b'7cnE3+28ffBTt92uIaAFtnz7pF3/hWfcnUbzxtd1RX/99b/+9ZukT+LUBUHr5kY/+ssbX1r2NXC+/pb9+28yDv99l8SNeYH7SWc00PDbkWBzCNhhR3FkNLi0BG5njgru'
        b'wtuBETK4EzZFplfA/XAXm3Kaw+YlVzDvd98Dbm8CzZEoAegYR1OcSBpcdwRG5qKu/aAVXI3IzMmWwAMoLpgGR0rhZmLZB27Al+BJfLyRY6d2pXgclj03iNAzHTbC3VkM'
        b'QccC0WNeNDiBRsyFx/jlh/AC7ABXh5ytwOfBrmF6LfRSckACX46eCfbKIuSScOuIpFzhNfZ6NFnuEQpgE2hZgc8tnOyt5yPgxjpSKUdwt4HJHTTzUVwuDbrBJXDm8XhM'
        b'eAu4DU/ik48MqRw0RcpAOzCmk+MPsZgDb4G7TiQduzYmi8xXD7CNTFmwKxLPWR4VDl/iwq3ToYFRgdHD3eAsU98MNMe2gVuwiaYclSx42CmNaLnAa+A6OJGVJ6Mp1hoa'
        b'3FEmga2ghxzDLIPn4YWBq0fRMtBDLmEDZ0ErUQKCF1FjZeVkZQGDKkcOm6RZYFceITYc7OaCKzHOpITJq+Bh2JwLLknVE3kUJ4UGd2Ngs0Tws4trsWNbBocf8Hgw62zx'
        b'8K2l3t+KLcaMJWc++61nPoUCys3roONex17/SSbBZLNgcq9gssUz4GDN3prOslOVJs9Is2fkA8+4+55xJs/JZs/JBrZF4HnQaa9Tb0BMd7JJEG8WxPcK4i2ePoYy4/jW'
        b'yrZKlMLL9+C6ves6HU1eUrOXdMD8Mok5L5pp8p1l9p3VK5pl8Q954C+77y/rUnZPubiqZ7HJP93sn/7AP+e+f47JP8/sn2fgW8aHnp16YurxaaemGdj4zk1vP7N3OALe'
        b'PoEGnsXX34DPcY5lH8ru8jT5R5n9o/BroGTEMaQgqN+ZZQ6KQmDfb5xxSmdcl92p6Sa/aLNfNFbP9T+4fu/6Tm/mirUu5X2vmF6vGEvwBCMPq+amGsNa82z3ssWbRFKz'
        b'SNpLPhahfyfbLI65L4zpFcZYJDGGZLNoIraRnGMRh3RyOovOLj6x+PjSU0tN4hiUDptjTiQOIsQrqHNtr5ccffCLpsKMeaTAbyxeAcMsHh01VdRPOUxibmgbac04C/X4'
        b'9w+M72jbu3WJTaPrD75F6qnOz6YxXEQRrgCzf8P0/gc0GIjyLdeq988h7xGxQ8DU9sYDLGQZcU/lf0D3HwPS98YCpMkMorLebcJwUBh3I4CDQdIAi2LFpRikaq3s/Wj8'
        b'Y1UZGQFsR8DYsWHraDRVOBoiKzAMG4YabSCuBqNLrC+zHuPf0ZQpyioZTdpVqlU1mvVEvadcp2GAoFZR8SOkLYPSk+HM3BAztzqFpkJVN5DyexVkqgc0ZJiBb1OQsSF3'
        b'jLdV2qEyzJ+kBkyUVk6XOSe8yY6i8CXqElprvVV+k3/hb+haHLg0XGm9lD5/3C1qHRovnfFvO7wf8dlUYurEmu+jdXZmUTTcDZucKXgJHEnQpeG97gDsycsagWJtyjg2'
        b'XFeI9XErpy9A8BLr1gxq+KJNqz5QkLBsg3qh+H1Ki8+oX65XbS94EWuN1P3PnT8Ee27b5v1PNm/NjK1b9h8Xfjju1bmnHUujp5X+2nx6ZpNf62Tx3HETdua9PO2Dv47f'
        b'wNq3vfhs6wd/Nx0xxs+UBB203PWd+tvnH376lW/89YylV+bzHucbz6W1XBNtYX+y/4t37d5453fvb6//5MuWhD9M33la++6SwPfzl6ae9//Xc5PcNv31j5Hxt/fFF+sc'
        b'5gW96/3O1fSsKbK7/Hy21+mDn7zbubAh+97ej/ya+gJfCH+eBzq2LM05EvG35SsnfhL1nabz3h1RV/7Z8t53NukC17ypHr/B5PLiFvsO73MfC38Lv/k76/lvZ31Rv0Hi'
        b'QsARuAuPToiQhcGD8PiAui5qoCsEDZQhNNxi1VZCoL+DoGTX+eyqupmP8T1708FVBNkH259AErgF6AdhCbjhTRDBNHBSOvgykHVATxfBrkyCbKaBvXAfxhSDgALhk/OD'
        b'oGJCEjEWs0uIyMqodx1QPwEXYwmVigWB4EBRxOB96o7gGgteQBDvJIFf48E9fJmKHvTAS8xrQ2hwDximEkwZCQ/BlxA4AzeYm2QIOAtYRrRupHX1Q3CZDZMhgHiYg2+H'
        b'cXscgVtwTy7cTJiqDET5sLaAV9UshLV20sWR9uCUcw1piBLYtBEzPw6gWYLK461gBYKXZARihoDtxQM6OAjmDd5BkuLBWP3cAR1gc4Q0B/FPsEkAjoCLmQiGgn1sDTwC'
        b'b0j4Pw488akhN8BajeysnG69i3U7tH4nyCjXioyUbpR/yLEZh2aY/CLMfhH4LUV+xrqOjYzOisUvyJBl8fY3e0cgIOIZeLBqb1VrdVs1xj7+/RTHLZqJ7Cq7Unm+8tyK'
        b'iyvue8f3esdb/IOOZR3Kas/pyOlKQrin11/WPf5GWE/BNVm3DMOYjEMZ7VkdWV0h5vBpJv9pPWX3/ZN6/ZMsIu8HIvl9kXzw2lhvf0b66NU2vTP1vlDSK5QQa7+u1F6v'
        b'aPQhSswLe5cUm5dUmiSVpkC1OVDd663GmCO1K+SizBwSb/KPN6Tiiunuk3fyYWii6/WSoo/t8TKTpMwUqDQHKnu9/3/q3gQgquveH793NvZFtgEGGFZhYFgUcUFRkX0b'
        b'VMDdADKgKALOMKKIa1xQXFAxjopxNBhxScTdmGjMOWmbpmk7Q6dPQps+2762eW3eK2lsX57vvfZ/vufODDPDoNGX9vf+cXK4955zz/2e/fs95/v9fpTcu3G9pYaQVPJi'
        b'YOgZz5Oeupbetv4MQ2CmMTCTEES4mPXaWt0igzjJSJgc7yRr/BVuT5du534D5+Ec9oqN9/D5wMbYtVscaTj1NsZs11Qy7gU0pL9VNWnVL5mxPIu2M/Zbje1W1tbrSU0o'
        b'WeuzHBJrOYuxO2MRwb6pkvciqV3qZHzFU15M/VNBTNLEOpmANsGQe2VjU6Vp6089xK9eoabbmKO3LIe8Ky36r9yBW5vYvNNuF1EIjQHAb9uYx7RvZhuj0/S+8COD5nyU'
        b'Ttm7+mxybzLhwfV+Ex5LIs5n9QmuuJ4tJZ1Kkqr344DwbA7TLABSQwzYVh9nuMOqvXzbM2XVsnbWpnot19yhmirHuspVknZWZ81TOnzT/tCsMarFygGfkm3nnWKVPOs3'
        b'TtGDNZt7wWkn+yM5ksJy9LWZ3NGNcKGiLcDCE66tV5NqrVlFuak2fnp4bJtTLN1/jH3KxsqEXAv61q9tbqivqW+p5MaCur6pkY6RIZfyjc3cCQvXppzZ75CQsp5DztzZ'
        b'K4m0tfIIt1j/DnlWNqtqCVdWW0lfafM3N7jNYwBZUe9h6JzJqeXV6hYYfOVGX/kw4zQujkyH3Vv6/K6EDogn68WTSRcwSlLJBBm0mB2Mll0oOVfSH30z0RA92xg9W5uj'
        b'zflNZIJONpg8pW9D34a7fu+F3iX/PhJ+4vkR+TfMZxMXsV8ybNRi9gkNyegNXcw+DonoKSLTkTiky330MYllrxBstY4ROUEJ29Ts2K1salHre/5pIR1EAkWbM1cNcbFt'
        b'glg5aRRerEwFLoZlPG5us5h0h4/4LCIVpqLuxs2HU9yDZVB30YxJvWoweWKfun/SzfSLW69s7SP/Hgo+9HhI/unFCr23YnTBLJa9wKVAscaaXep4plmACCqKp04wA4TH'
        b'qDmqRw91p0pwuUvI9bSQS+/Bw5IaJm1Cqjhcl91b2C+46aGPmmkQz9R7z+Toc2icnctwc5+OcfRfO6tkbQfyZtaa+nZ2Df1Lhwihn51xkaeCM1+uX5uqfTlrrnZTMUSV'
        b'lQ3gKMrDUgq4XUGSfBXNFSIw5FFgwgBZo3P6Uw2BU4yBU2D1knS3keVULNN7y/6eRWKti8SbkaFa+bzC1NoWhtzWOS7MJEPgVGPgVHNhKgYo2MwzCgPfNE2rZOray7Ob'
        b'VsNt+pXV1LaGpmnysi3ayDUXX2a76rHmp/SEkuuEgpFi29lmj0xHpApq19lUAdzCWZzZCHvU9MMbl8UOhkb0LOlLuzJ9IHQyzBZz2MGImN7Q/pibSQMRs8mM4p/FPn52'
        b'PVmOC83nl+YyuJu9pHDMzTMar9G28eC2mWfS+CWES6S6tJMZenGc3jvu79npBJaah3E087l9bqXtAIJbSKKqZ01qtX8nOoUmOnfSwTHz+YNjpW39wm0rELrWQuiYEyes'
        b'CM9eDyxOnGwmHEfzPByF2czz3INN0NSwew6dVCxx5CXdcUWuMtH38lUJgDp0F4zfDmuaJZ3tW5YukXCRPzK1Ug7DZmyOY23HprnoZMmoViptlgx6vwUmqKmmgjucbkGI'
        b'0VUY6HauSXAo711uEKcaxaAkO7puLG0HZ33PqplRbcjZIqq2PKsrwVrNlcRqraYPXoWiwD4NbcLj7UfadTncrvGz59ZvoQldv2ET0tWdTVRtfoFmU2tW2K70cL8bhs5W'
        b'h2PcUv0ppup3e7EGUG1/XvVzFFlVP33QacV8BIVqheBMUacxiBON4kS9d+IzGmAF80yZwanF6qUyxq7qhd+46kEHZMhT0dRSQBjyWnCQVKu0GkVCR83hkO0mjbJW02DT'
        b'KPT+INRABuN4pWPHxX8mken9ZP/IAcVBkKg6n9eiXHGsWpQ+6IZO9uqzF5LuZ7dd+P9iULk5aG23b9jaHBuazA20b96ybpWVLSpNrbJ+PakOH0t1WJ4dhylm8RgtLBw3'
        b'dTAk/FFI8kBIcr+wX20ImW4MmU6EHom0J71PaJAk6v0SH4eE9xT2+RtCkiAiQjtZFwOiF4ezrfeb8v+mqnkOqpr3IssSL/mF69qdcMcNTU0qrrJ9LZU98vAMjKdvWNst'
        b'hpAZxpAZ5tr2N0iS9H5JXG3HGEKS/y/VtshBbYteiAmIedHKdqIQKLZTFtxfgCF+2OEQtwjln4/UhJDUhMCuJhJepCZarDaNrMvZztqX9JumXEb7KfXhI6B1N7LLZpOO'
        b'xvPHjq/jmdbnIRHpfKRyyPpM+awTtsyWaKTOh4Stq5oaasEhwNrq+kZlrfVWjUn31dICrpWVXL6kEcZZGsH86Kplf9RBVxeNm2nd1TcYQmYbQ2Z35XwmidBF98b31Rok'
        b'k4wS8Jb8m9jEPuWV1XdjDLGzjbGzAVcyRzttMCRSm6tLgw1lQ8hUY8hU7sE0knQtN2yIkBUyExxrzHwG8tIkxjEr7mbTl0f12J0WGXIstpyCva206Zz0/i7MthJTpdCV'
        b'sqWnTbumb9KVDIN4mlE8Te897SXodf0W6G1uUtvQS+/fhcF0xqE8YxlMxVZEtVilsCHJZhl/zjpHNVsX2vbRZxBevcKWcHr/AHqf1KqiT9dAxzrR1NPU13Jls0GcYRRn'
        b'6L0zvg05jbKYG59DZX1jiw2V9P4DoNLXTCX12taTfnhr91a99/h/DGUudHWq5pybW61X8ORDGwkypEsDXpU5Z+LmLQMVGGs6nmMvMSYbFDJncntpKi/r7qHkObIYUfKV'
        b'Ao4FbhtVoM02G6RjbKPz9orsZmj+8+ZJWlFCBZhTM08jqapyfePK8OamVk7ZeUIKZzehaW5uAnCVp7yUpCF2AplNw8yddMh5naa6saW+rZbrrpwnvSEnktPK+hb1EL92'
        b'Q7PdejbiTY+bU0cahFJg0yCmJ9+DBnnF1CC+wdp5R6Z3TaemAgWG4EJjcKHer3AwILRrpVapq+nLO7vWEDbJEJBmDEjr4lMe3SQLZ/WHGgJnGQNnPYNdv0jZbGheWbKd'
        b'VbLqryZC1Q1NLYAXFgI14Gmr10Pu6+pqa1rq19dWgkIHYY4aqtUtlZx6x5CgUqNqUC2AGgGX2Fb2zZYxP+RsOSRyo/oUnOIw1Smipw0qcPjNrWjVEIC3ZdUqCBogaIJg'
        b'HQTQ7VStEIAzQiqMq3ZAAN76VB0QgDyhOgBBFwTdEByHoAeC1yE4S+mE4DwEYAWv6of6+XtDhI8ymjadSgpYOGnjOglgEKhjBbZG0yIBGE1D4MoEpXQUPJZG691DBkOl'
        b'HYrB0AgSSKQdxYO+8zqyByU55CoyVu8ufezh17FQm6OL0q3US5Lu+uo9MgweGUaPjGGer8fEYeZZAdijzrQkjWf8Q7vyB71htuBMdf2pqa4/NdUlYUeOxTg5Qe+dMOg3'
        b'AYyTU8E2ORVMk1OpZTKXYIbee8Ywjw2Yyw4L+YHzST4QPqEhSebKeIoHPQKHeTEeYcPMiwZAd9D+pfBHvH/xsACeK1iaJVRGjd4j0uARafSIBDvbZDC9fU4AOUWR9JYc'
        b'IYJ0XM+AYZ7AYxI0yiQLFB08cHfxCAWDZ8dBAOtRCsdOjkMR6wE+ysyBiOcRD6bypsCZB6bUlsBZAFdjBe6shwxyMQXPyYoF0DwHgYgPRXQQuLLwriV4VjpwimYOROYq'
        b'cxi422Uq8phKGMwxAu//TayTB+Eoxwp8WI90oGBUIHpGBHCoowMSEQtXowKRbfNYNZQQauMFghGcw2L8Kn5bjffjA8n4AL7oksAyzoE8TTzrGJP8rzzQfbS1AqeuR/kd'
        b'gjqBkrfT2YRPyN/JKAVXhA7xCUUkzmlUnJMVdqF9nLMVdqF9nIsVdqF9nKsVdqF9nJsVdqF9nLsVdqF9nIcVdqF9nCeNCyBx4lFxHCphIIkLGhXnTeOCSZxkVByHPBhC'
        b'4kJHxXHIg2EkTjoqzpfGhZO4iFFxHJZgJImLGhXnb4UzaB8XQOPGk7jYUXFiGhdH4mSj4gJpXDyJSxgVF0Tj5CQucVRcMI1LInHJo+IkNC6FxE0YFRdC4yaSuNRRcaE0'
        b'bhKJSxsVx1nPT6bW81PAel45lYQRymlgOa9MpwL19CEvcCxXPuKx95fAB4yyYLdLZIJetEsGxlPUkqumuhG4zBW1JnPhlnqqBmu2t6KofGZDYjC54vRNa201Y036uLYm'
        b'VnCUYOVeuAp42mrON56yqUYD28aWnG1ya1KZM6xv4RQ3uFfN6q1ZmSXl2aYcqsawcra5Kagz2YtVh6+gaiYkO04r2dr9sZz7pLmsJiv9FlUtVIhNftVq6hQAiKNWXOtJ'
        b'TtUNDeEa2Llo2AhcvI1fZZuXbWQr2NsAcfGrdiIkHBOA2KJyBdFlxOh8r7OGfZ4I02IllIyl52Mn1PCVTDu/cgQNFO4ENndCmzuRzZ2TzZ2zzZ2LzZ3ZjwczWjudxLrZ'
        b'pHW3ufOwufO03PHJnZdNnLfN3TibOx+bO1+bOz+bO3+buwCbO7HNXaDNXZDNXbDNncTmLsTmLtTmLszmTmq5IyJkZbjljiV3ETYpI8137TxdFOPgP9s6z2aWt9CNPsFm'
        b'YbtAF+3oDaXQtq+oRUqSlp6uChojxnxLZPuWyp28xayOMd+fYtsFp9jT/M2ClpKRt4iAbLcNqvZpKbXK1Yl82YGbh5Z5tnm0C23RbVlmv4b0OJd2/mpLz9lrh16r5hWC'
        b'dhqfCuLOCtVFkv/TNG5aHDWJPnuapEoRuUNs5RCvsvJpjP3bq6rB5HXEapb6EpDJhtznExmqfq3JOYCI09fnsLT5lfXKIWGlprZFBTBAnI+qIa/KFdWNayotfkFV0Loq'
        b'QOhSXYdADQEFsQEvxEOetu51h5wqOcMMkmOzRtXcpK4ln6CCsRNVaGypHhJVrlWvpJ9eA65ahZW13B/quNXD/FolGCmQl2pWgVEBxamvbtGoiXSuqgXNvOoGQNFqrGsi'
        b'FNMKra+rr6HuT4hAzi0hlujqtS0jBRryq2xoqqlusPWDT+glQr5qJZHvRZV0CifZ0L+VXL2EVNpVeWUlTM+mtEJyvVY95EqIVLWowakL3VoYciLtAm0y5JlpbhmuJZzU'
        b'tS0QIXPlzJJgahgSrWklJKitwAoc7Kxw4jNMetxsPyI2Q6u2ie3IpBu0rZWV/wxbLL9nzVoTcMhZxWpbdJk9rfqkmXop/Kg52SuG4EpjcKXer/IzcejxLUe26Gq4k/ku'
        b'AahpC7qdLdh1HDxdbAKALkRb8O3CbfDtRiDszrr0utiA3Zn/SqPIY/fB8Egaa3rR9DAskrpwMD20/RMjg/cjzUlNfyjcnac5jZm46Dj4G2G5l6fAX5mJvsdhUfQz0TFc'
        b'KnPqKNmFGedmnJ3ZC6LQuGQaHC7qytbGkKo4M+vkrL5UgyTZKEkGDMKZg9JIXfmJNsAbHAwKPSM9Ke3zMwQlGYOoH2xuz34wPvGKvE9+V3BXoJdmaAWfSSJ1k0gyi7vs'
        b'5exnYXJ9Yrl+4VJD4lJD2DJj2DJ94LLP/CTabF10n9Dgl2T0g/My8hsUR3S16aJ75f0ig3iKUTxF701/4imgF+P2kj4uvsuO7Tsi0L53mf0t+PBt4CEsEFUzyqklVuOa'
        b'EU/Dcg4goqXJ5OEZTPaVhNGqr9tI2CcrtuaFnV9Q5bHzzEuQ789nrAHixtsi64Fl09qmlhHP0xTh+oU8Y9MN6ysvQ1ogkDbiHtsWUG80ZYC6/aKAeqprL0OYxEGdWYPq'
        b'2VFmQsl+0Tp7Fp7emKSFAWkj3iplDvD0/tfUwXGO6v2XoS7ClrqfZYZzCOtqzQqTUzDqTghIMtk6mkDTnkk6lcy4jKjlAAhSzeQ1EIIoZpIDGLak8LKRZ3X1tfBBk1RC'
        b'cicJRiwhLZyFOjzeVJXxcnJZ30L/mtHz4qlOfTwHShf/wh1R/zL1GQf1OWCpz0mjEWnGGCuZcxZmJpMg54XB8QiN33uZaTLBltQZNs74AdGldoWtW357krPm52QnZ+fM'
        b'KX/hQU5o/ehlSE7iW7sHWmae2OfT7mbFgZoMcs3OjOwsRZPCsylKDWcX29BavVFt8iwf3li7shpOU150aiAl+f7LFGii7fCLNw8/s0GsVZlMvGh4XNmChUteppN8/DIE'
        b'ptlOrLF0CW1qWgNSP+dlXxVe3dzcBD4DiYCg4fzyv0R/+MHLUDcVqPuz+eT8qVe5xZPai1JhqqNPXoaK6UBFJGszw68lE1b1ylqr0dO8aqMarK/D52YWKMgE1/DC9F1k'
        b'VT98GfpmOmjDEboamlbakhUeVzQ/J/eFOQpC1o9ehrpMW+o4+/VGZWJLUyL5M8KqhcflvChZO7lK+/HLkJVtS1aoQ6CK8LiSF6XJ1NH0L0NTni1ja8G5jeBs/okI2AiO'
        b'vkwTBQdWMrdi/tyXwE1RGV6GwELb8ehDlxQqNJvcmr1opyKtZ3wZQkpsWy/efoEAaRxsG+E6bk5paVGBIq88Z9GLrWSmXv/TlyFwLhD4L5aa+qM9gbbbCEnhuWSezasl'
        b'JDdSCUZt2eLl1guT0wMoFIzruLKFBbnlWaXZOfLwvAVZ8vC58wtKMhWl5ZnycChmUc5imZyaH+ZCP15lynOs3LJLS8jkwGWXm1lSULyYuy6rmGN9Wz4/U1GWmVVeUErT'
        b'ki/QbefWejX4mGhuqAb0Nw5h5cUHzD+9TC0vsB0wSeYBE2m1znL7M9xoqaYTTrWaZPHi/WDgZShcbDtiJtv3A26nKSk8c8Q/Y4Eit5S0aLYiDxZf6LwvMbx/8jLELgNi'
        b'x1uIFZdTppDbASOdRgm9temFxrjJ+mboZaiptFt2TZA81PspR0vtyBmItSj/4k376GXoW2E7xEO52jKvHOAsJhzOdhywAhb1LqCOMzEZoUrdZGPr7Gmj5GpjGtosso6j'
        b'Lhx57ay1iha5tpyC2O4otzOVjFUqy+mIapz1nTVdlQ6f6iwnKdb/kRSWMxXbvW7WQQ95On0+5/YFzqEsvDwnhYyciDmWUpJkzqrvQBv8DYgHWAcrRAe6dQzIDSoWGpjP'
        b'bXbSRHRjE2rDYlLjtrK2xbwz3Saxb3SryFrymhrOD77exoD94WZQOs9nQcF8ql6S0ed3Jag/+2a+Pi5DLyl86PdhUFf2YHSCLq8vuz/6puxu+XvLDNGFxuhCC8gzbMXN'
        b'GpyQdjNUK+jxMAYmDfoFdpc88ksd8EvtzzZOyjX45Rn98vR+eTaY0I67OUhPYFFs0gkv5wwcR/dtUOIa3bfNdm9NMLHCmyazt2foUS5i7MeVym8s1W/b0xtbZe6VozUv'
        b'd3Iw9j8nz4YEsAPuwObZ2bQ3XumoMFyMChosniuMr9joGw0b0smkvR5J5AMSObcfqvdL+kws0c45vKF7Q5fXMyrYbGxjVV5367vVViWwNAM9jTEXRUi7kWP77YbaRlIU'
        b'BxvrNKIVShJmV5JUapkvN0om6v0mDooDu9ZR6hWyKEcqh3TnnioJDnnanb7QgUHH0cgQgnLT0TPkYXv4IjKdvTiZ2FEVmPIOiUznLkLu2EVAT10EcOhCgXaG3G1OXESm'
        b'AxcBPTzxtDtacbM+WRGZjmScR05kuNMQT9sTF5WUZ+rcqmi4iuVRe4gxVQNt8TFV92BU2CsmGOA44ws7LBWRC6gFQhCQ5BEyzDw/ULJM2HitBR9k/rCQF1YOqnwkfELD'
        b'DoUdpskMwCKZCVAkMwGJZOaLo6I4zMEa4GIWAFxkUgiSTApBkslBooykGeYJ/JOHhSJxypcMCZ5AQJJ4WsGIDPoVAoZIMcUQKaYYIsWAISKySQMlDqUlDqUlJiFNw6Gm'
        b'gNn+MI/1nzYs5Aekf8mQ4AkEHbnDzjYUzwaK51CK51CK51iDuHDFzoBiz4Jiz4Jiz6LFHvnOoF8MoLPEAjhLLGCzxFJoFmtNS6gXf1ov/rReSEg1LZ/7FesEkyHBVEgw'
        b'FRJMHZUgFRKkQYI0SJBGE4REay1oNIA/EgL4IyGAPxIyraPYriBxUJB4KEg8FCSeFsT6E1BdfrS6/Gh1kZB+ZaQvDvP4/vPYYaEwDDRCIXxCQ9Id3RlJlJb0NnAGNOg3'
        b'lWQlIU1DgicQdBTZEVMMxCgo5o2CYt4oOMwba/XURFBPTQb11GRQT02m6qnfpOatBw/UWxjUWxjUW1gaIXVM1Bw/FkagJRDxAarGErjyPYLgyj7gdPtAN2ALOlrjtt6j'
        b'2V1WiPfjbfhagqI4Cdyl4kN8Jn6VEPW3TLNR8zMvahzgJ99azW8ns4TPY2pBxc9uuVsipM/5o56L6HPBqOdOSiHJzbmDV8cqRTudl7gonci9K0CE1PGUzuSJG41zIVfu'
        b'oPS3xEPpRuUt9yFfuxmuuF7dYoNZyjOvdrO51Y614Rd55M5CCBgFVFq40JXAWVrp4Zg3AAV0a2vIpVKpMamyu4ClWXVDfcvGoUj7826gp9Ja3UpttopO4lGddnMmzuY8'
        b'zPbR4VaIAiEOcrXAC2yDpTSGW0pN57cRMnqaa/oznp7LRunp70WPN6mxENTiWFKFQ9rMksVukCw2MIwDg6FvJPzNeNkP74EPb3qJD5vkqIyX/XDH2B+2MJpy+uFvZhxl'
        b'7nY8VRRwATMd0wUcwpi9hLKO+/gm26JtDHCH2caQZIM4xSiGBe3bsC0yNRilbwzrIsrCjBJITFRSrvAA32RhP2IARRhagzjZKIZF5NsSFsaoKE5g6IIGjOCZG9DaB5jF'
        b'8M7KYNSB6azaViuQdeB3a2TOsWp4E+yOhMRby8l8u3g3agQqsH2q8mqx6Ow50kQkb1jkW52V97CR/+yN61luztsJTtsSrTd61gJew4oRAI5Yu9qMtU2ubKrlcAU4T2IU'
        b'usnsR5YyvkTuBYAiOiFS3ls1C65mQ0AtqqBPES69ubm2UWl2IeZm9Qku6ZiWwfxqpXKUHEKbnEQc5VuZpVLFkIS+rQbxLKMYzCfGVbCfBUfpo8sMweXG4HK9X/mgb5jR'
        b'N0rX0rtxwDdF75syKBlvlCSADeGAZIZeMmNQApHkZpJeMonaYpUbgiuMwRV6v4pBbz8yDT/yjh/wju+bbvCeYvQ26554T3nGGAT1xJEx6HDk2Tj/GTXuxsO4C3JUA1R+'
        b'6+Gb4BhHRt3hjd0b9d7hz7A9nczYz2HAE7Qz2XaisYPZjKdwXM44miWsu8s9wR+dI0n0MG+/F4xxc4HjoelNLnGgnobYFmvfDyoQMdsSHRW9pamluoFM26DVpp5JLoBz'
        b'aFrbPBPwp9SQ1zZGL5nG/frWaTN78nsUlge0ZmTsEF+tWetA/hXS3B3XOY06wzcZpMJ0HMzl2Z9NAoNkmpGE4nSjOF3vnW4SgD3tBeARAzk6bEZGjEVW5ETHYp6p/VXz'
        b'eXTjyE5qhMq3yIzp0E8ccVSbgdqfM6PMyWRgcmMK3Cmvrg9JJT+D7ySj76SO7EEi7WzQh08nP4N4hlE8oyPfwaNhAesxAVhaUyBiPVLgalQgsuN/ncAUZ6zAh/WIgHSj'
        b'ApLLdLiyDzg+GXZX5qJtWYRPxtdqOFZ5hE3GN/BeeRLLZOO3nIrxtlU23LJZNfkr6JTHgq25ZfKPR//xe4RL+IB1phQpnZTOShelq9JN6a70IFeeSi+lt3Jcj+cSQQev'
        b'Q0h4Xx/C8QoJHyzscAZowg6fjqA6JwAWpLy0E4UPtOWlnelz/52MMuCK2IFhjJPJ4MQ+zpXGcQYn9nFuNI4zOLGPc6dxnMGJfZwHjeMMTuzjPGkcZ3BiH+fFlbeOr4wm'
        b'JfWmKZPryfRX6207t/SyB9kl3iS1jwmucBypNZaCFfrQK4Aq9HXhgCX51DW7CJCCOtwo2KMnqVNvWqu+HX4d/h0BHeKOwDp/pWynCxjEdDt1B1yJt0OdmwBfI63AV8pH'
        b'QVT603ecrySOfofQkjQqfYAygUoxE4fcYcyZTSeG2LlDbKlMOMTLmzPEK8gZ4uWUkb/lQ7ys/CH+nDzFED+7qGiInzdn7hC/oIxc5c8nQVZ+7hBfUUqu5haTJPNLSVCW'
        b'AxFLilQAoELeKJgr8xzizckb4mUXqRbCssorIHnnzx/iFRcM8RSlQ7y5xUO8+eRvWY5qKU2QtYQkqCDEFIxaCKiFxDYGeCHwfr+HcETU+z1DxDUB9X3Pd+D7XuDiwJs9'
        b'eSIY5d+ev0Vg8n3vMM7i+x44vlFyK11SrDykCxTUk3lILroNMnAL3luahA+U4AMJ86Sp+QoyusFp9jzcQcZ7UgH1+1wsLyiZl09GfCE4zEYXBcxMvMML3cSX4+t/kjHE'
        b'UhezH15cf+rjiafPHr149Gz32Y73dx5mPecHHmc3Xv5lyKnIkv0xxc6fCvMbBJ8r5/zU95OHn/KYtCsuH2RUyPhPwNIA7ZXh7W7oojzfDAc/Du0Zh+/x0VtSFfWqHYb3'
        b'b8CdpXgfoYJlnNEpXg3SbZi6iHv93RWTUCc6hA8VJaJD6JAT4xaAdqXx8B6sXUlETUc7hdB0dvrPftYd0Kz8DCNSPZExAbOHMn5irVzvO578KFNUagieawyeq/eba6fy'
        b'bHZGxq3RTiOq2qpfwZLkwOcytXs3gY4/j6rrsBa1MhzcOCGsOpRlpeBB+TnBt4YiDqKG1iWJedtzBr/GYmJD/vM097rXYUg4cUNiD3+PYI9wj2iPExkcrmRwCMjcI+xw'
        b'IvMRNwOJKGisd50nHTBk/t7rZjdgXOiAcR41YFxGDQrnLS6mAeMwzjJgdtoPGAu8mtWAkSo0gAaOTuLOaUXFmxeZkIHJCElMTJqXX1iBO0rL4qDnVsxtRTvzUR+fwQeb'
        b'3XAXvoT2aaaTd3EfPu5cZMYUhqFUmrjABA9QiA+QNfVQ0cI4vHch2rHKmQxKAYPeQVfdPGbh9ylIweJaJ8adYZq/iqwq/vnmZIYCTanRzSSKUuAxncUHGfwW+XeCJv/Z'
        b'MmeGdKcNH62tavBfEMNowG08fuCGj5iBsCqlAIVlB1ngxCwuc9o4F+moASzqQifR60WBWwpKiuT4gIxl3BQ8/ObkVk0ExJ5JL0rIB2ADfAUdxEdTU1LQzqoiJhLd4qMH'
        b'a9ARDcCoox0JwgRS6vzCMDLFVMBHTKgIcUmJcbgjOb6ghGWaZM74xub5Goq4dAWdTivCnWjn7ILiZBEjEvM8y3A3HUKULKzF91QJ6OIidFaen0gSoHu8yWgbPk7rBB3d'
        b'4J3ANYUTM3G98zqeqypSAzw66g9HXWULI8bbf39eHD4kx3vnxgGdlEonBvWgo64LY9ExDeyNzFOllzmhI4h0ozgmDm1Hb1KkrvF4e7V6Pb4uYDzQMRadYAhbdMlXM5tE'
        b'TcPdZHbsxAfkSfggAJ81k3TlcaSlO+Xykop8fLDUjBrRJhyBmsa9fHd8aDx6m6KN4dv4XawtwgdR1xqIl+F9xaTAvnl8fLod9XK10Vk7PSF+hZl0hnEr4qHXkHYKbXLU'
        b'54vfKgOUM1KhF8stZd6yFKZz8nWGKfV2asZv4MO0oLXt6BY+Oo9hqvGrTBtTssBHA3IDvpcWTxi+a+i1wNb1+Cba24qvt4gYDwkPndhYSAcHfp/QekiNr6MD+FQL6dry'
        b'BXGFiaTbkCWD+9RI9ZIyoKP4rivjs1ADsyruTg5NgKrBB0MR6aHJ+FBZXBxZBDqSFaaq4non2oYuujDL0SXaA3OnRLgBKIIa31mHDrSq3Nfh22QpThWn8tFOrMO3Ke0Z'
        b'aFc27izC+/AtvL8kMSm/WCFkfNAxPnrbFR2nowVJBDDuA1/NqypemezLUASQBWSMqNcJmSKsI+3KoH2NeHd9dMBxvhr0wGLnfnisO6MJpXjv/redsz/J83ngov/x3ls1'
        b'e/66769MQFFf5urL2wIv9Zf/vvmLij2uMl+3rdedKpLWNV+ukn3++tft//HgNr7w1XfcRZp+3c3UwJ/9+qvpAf9+JDX4yB+7/vLkt6df9V/5259cwytLd1ZcKfb/de++'
        b'RcUPPT75l5JlAz8VJOjijxR8hYd/cnLaZ5LtW4LDjYqBk9JN8vTwX6nYzxJzWoM+lLydPu+P8rDZHw3892BGg+6o61sXe4Mr37n5SD5904Mfd/ymPV34+2mXfpV26Mdv'
        b'bPjRCSbvd/JfPd13PX7NpYO32Fca/qD6aehnGx7nLPunsryEsL/4JXoMP3in5eEHla1rTv/7evnNkzPSUr/45cwFvh9/9rCu+sJbP//FicNBv/jbpjnj00/GfTaUlxz6'
        b'6YE198IOX/zL17/92fxXznyR8919u2auf/to7J/d/+tpqmB6yPb7IW+e6CtdPo1Zemf+0++93qrfH3q68c9K/pS9+37Ob77wis+shb1oXN7qN6P3bFm/vHOF18WSnZXo'
        b'ZtbrnieW72rrXvyR19ufX1g3+8tPZzr5Lc1XCi/lt8TPzQ0+/ItxA9rfNvS6Rc7r/2Otz6zQz+PPfrr9bV+09fuuxh2ndlb+9xef/fXXRZLLU3JirmwpOvHF4b2ferl9'
        b'pbt/96+yKIpkhrf7hBAWBL2Za8WFUBYE70K9FE0O3Y0gfb1zwkI5OpisSMwH7I+rPHw+dyJlQ0LRafweRdRoxOdLzHlQRA1eJfeNB/W4B3W2enq4qvAtNTrkjm+3eIgY'
        b'v3X8smkFT6DvofszvShWmhR18tazmWQZOUWxUxYhLXoXdxaHBRFhjM/w8QMWncLn0EGaM5miAAYPXUiWEy5OhjsocW/zyPC+ji9T8gghSIc6vRrQzvX4djO+pSFfdhPz'
        b'VpHX7lGwEM/SuQmJ6Dw6H2cBZ5mAr1CwkER0E/UTllA+D70WL0uisyYZNuGCV5JCOTw6mCOOFyWViBj8Nj7M28jOaE+ir6Ib6Ay+Q0b4Ptw3nsxGhHjBNBZdw8fQjScw'
        b'85TV4PtkkBaLmCyW9wqb3BD1BDaHt64tVK93X6fBd7zQPrTfy9nDFfd7rQ8lNXigFd9uXUfILxGI0DvT8GkOXeamdCqh/wjehQ8UT2AZ0WIWX8HH8FlauHZ1AO7MR2+R'
        b'dOfQTd5mNhefwbs4mLm76UpEmMtOdCW/BJH1uB7vSCos4TPB6JagFZ/Fxzm0Ov901BlEFnwyrR8iy1Qx4TNn8/BrQnyeVjB+v1ANCC6kB4SIzdNNQLHAAx1ANykN6Obq'
        b'JagzeQXqg2VKyIiqeJEeKpo5OluXiDprq5JNU6WQcSvlEeKv4L0UtmZaGFlWSOak65UCy0DyJ6u4iJkgk+LzAnxjCtpBa7uJRQ8gHUz6lm7qSdiS7EVRHObh+Zk1hAZ3'
        b'vCuRVBOppQKemDSNjmLQLEYX8uBtkruiuFSB3yBT+iGSKBj3CNY5o31cOTulE0l1oQvo9sjy5VnGL0GH0QlamJXBU1CnN3qjNCmRcDtFfNIV9/HwBfQe3klhcCo9BSSD'
        b'QnkBYV2gVpyn8lagI/W0oAux1sMciaCuIX98NKWAdMn4OCHerm55AksA7lhOuI/OUoUc7U02rRhCBt1GHVJ8Ryj0aKMYNnJ0kdR4aQnaYYW86YPe5pP62Y62P0mH75/G'
        b'5/FOMjJm47O2QhHaiw4l225+JJAF7ECUKzqD3kXvPAHnu3hbEVkXO73sXyU9fhd5HV3EHcUyEVNMxuh1svbteZJMXtqkwZdh0SMZkndIk5eQ0h5MLiLlOMgdRZLBfS0P'
        b'XXNCh2aT4QklnkQoPkGajtR5DrqMzK+JmAAyG7yPLy/+u3tdMhuN2ntdoudz/naCCncwR+WnKk7bYrghlAmM7GrTxfZN4TxrwfZyAbe9PALq/VgcBl6FOa9qkCKfpZvI'
        b'uYbgPGMwKE49FoM4M66EpfjhyY+kqQPS1P68m8UPfR5GPPQxTsp+WGuQFhulxS8PLf5YHAqO6wvJN2L70gakKfowRb/y5tqHBcbJCn1YjX5+TVceOLVf/ig0aSA0qa/1'
        b'SvvdOXfn3Z1jTJ71UGwILTCGFnTlPg4K7Ql9FBQ/EBTfN9kQNNEYNLFLNAh5s+OKuHLNfjjZYO2tTBpzpu1kW19s/0SDdLJROrnL/bFYcrztSNvh9u72LsGgr1i7Xrey'
        b'Z6veN4n8SBbaeH3ZQtNvcaXpF1NlCK42Blfr/aof+wY98o0e8I3WVRh8E4y+4BVoXDFLKqyIu6JkFBqCi4zBRXq/oschkWcKTxbqNhlCUo0hqV0ug74hUBfZrE7cG9K3'
        b'om9d3wpjxIS7QfqIOeRHKRiMSdAt0C3oK7+6+NLi/o2GxExjYqY+MXOYz47PAqgQSTZAhZAQ9ONISFY9qU7OlaG/9eYmrij6mOyH6w0xJYZghTFYofdTPPYNAxrnsrrp'
        b'P51crI+Cn6nWphtiFIbgUmNwqd6v9LFvhG6Z3ncC+ZGs4+QX2s61nW3vbTfGTnkUmzEQm2GInWWMndWVbfSL1vtFP45NoJePpTHU9Dcyrk9ijEwj114WM2IuxmzQazJH'
        b'Do04s+TkkhPLepbRRFGxvem9Mx9FTRmImmKImmaMmgapwwfDY2lqUx4mG+HxsZzVcnQyl6U9urz5kHpQGsERNV4XrdMQqvWx1Q/zPix+lL10IHupflmVIbvamF1tiFxh'
        b'jFwBJHd5mXTcuN2GcSZPe2bDfAEcUanKIX4KbGe51VS3WGzsReqaVbVra78pFJTVjABDv8r0n2VeeO6EcAe2Lh4y3NbF16b9izWhLEt9d/0Dwm9rD4SCYl1wyWDue2a6'
        b'8V/YzgX8EtCaH+uE3bb6zEfrX9tooL+oDkPvM070HX/vqa3GexyoRVs85HAFCDfBHYXHqWqrlYlNjQ0bZS9sgM2Zjwy5VZpMsSrrlS9G6P/YGg8kbjNRLHdk31WvHimE'
        b'NdUvbu/ynWfomjsmFHaNrYwIw8qpVRfYdFlMNV+eIhn0qxpNS1Nd3YtRxRfYtHMytQXStCSSjMLBC8iI/RlQSs3yX5JMav0c9MIdUQQEjtgPxFP7gfo6k8HAWrAHIa1a'
        b'2whej5T/G9pIFbpXWs2QL0amC5DpY9ac4Gy9wLZhJeCxWoxCX76BVTEv3OHcgaQRO5BYW0BXM8wZZ39mTZgVXSNH3qDHBEpwJu92fLphC6fydji+m1m6YcuM2rBlR23K'
        b'MltY04atwzhrdN/nn3CIFI6P6tcD3ewekox6MwOqwcLC7gRmM8/FAR2jUYoJZewWnolqh3E2mMQa1gEmMfxnMoKppf6+bE0h1OHqVU2aBiVomZAJtr6uHozvV1aDAYXD'
        b'vFpM7tXCsxpqq8FsKzybOgCCjtekAu0TztAfluF6MoY5C6V6tcPM1LUUILmqqlylqSXLez03+uPXNDW2NJFZv2ZNfHhD/QpVNckcDNvWV9c3wMhzmBnYabWMmuXIa2Yd'
        b'dA60mDOY22hlh+YwN86UzkJgbnWDmlA4Gi6Y+jOz7i6WwWXVXfiK+vrkLxk1bO/897mfnfp46uk1fmePRnSyoh1BU3/Cjt/H+5cQg4yl0nEivhbDyV8m4asAv2GRv9C7'
        b'sWRYepuHpUnvRlC3sralLdpmXKprGippFY4oXkAqKinB8QmVlMKZkPCeWXo/61Mkk9KkLZNGT7KqzHYvqoegvvCNvudNXlTXMSaU8eXhLOsDDJJ98K0eGR11kTEXPafw'
        b'HYMxbIExyjdhiAvpoRBrOkMF0AS788+/A374Nz1DBfQX9IYUXbcX4eFcZ29xfKEcXVqKbpZzxw3wrLQYDjtAanebFoPer3f1bOKrZ5FsXHh87uT0nfwrRyeQbrfvP4u0'
        b'8mm/DNnt993a/e7ul4Oq/3t87vjdCl1YuUHx5obxdz13V4l+NImJzXD913XZMj7dTmCdUM+zthPQe7iDz3DbCei98dyu16HmiV6L3OJhe2Uv3m/ZsJSiGwJ8Fe3AO2in'
        b'R/fwefy6TbfHB3NzTL2+kv9NzlfJMFB/o2GgNg2DGaZhoApnAkFU9i9mdRXGmAzu8rOweH1CoSGsyBhWpA8sGhwfr1P2pZ1d07umK7u7tIv8szl6pYNm3LPEG9PR64jL'
        b'cdX3vtkwIvQGwzBaz5gxb9eRcRQEA+c5wbeGdBsLheTRA7B1+GZVEd08Fnjx5rDoAtqPd2vopt8B/AZ6pyhBAXGpzegui27gN9HuevmBCQJ1Gkmx4uOWUx/POL3p9vaj'
        b'Z1+VHZiw69quNwI++n3Vv1cV1CiqeX8KXBO4OrBM+7sUYWozmTQeRboYt5oUTJ9jj2PtyN1Sh20BjuuWtn4Z1/qDAufhJeHO4xKGGQeBH3/cxGHmmYEzExHTp9SLU/Uj'
        b'PtzNJI/ZFWxJVn0EHWEMYr2g6ZtMXXUpaXgXaNqxg2+tzXcwY2kkUvaMR9kcAWF0eP9ARmfUebqjyZOstzlFc4RqUKkOa9l56uNJp7fvPXv0LEx9c6eLXpswMeVK3c4v'
        b'6drbNCT4sPARWXvpEe6RzUrbTdYJ856zQ1uNTsh4Vi3Lo1OSlRa2vWoFVb+mPTDI1KizI5hAiUMNbHM/crAij/QjK12OsT8YAb1oDWNah7eOtQ5/q4vxM3rQ/0tGWfFc'
        b'fk2gKK9Py9UK1FDbA6f+Exi2iJvKXRO0228IGc+f89SxfzGrvdvxYpzau/2mFKfvThvdzdTouaTRQ0xGst+c8XpG7tE2nFZOxN+7cQFC5f9Y446aHCwk2U4O7947w6jB'
        b'VPWtiM3QtmdBkyw96Prj94TF7oseTgx/5cBjtuLq7j841z0udmIiPv338yLdsTTCBlEFEi06XoI75XBWJPCJm82iW6gPXacTiDd+U+rglGaM6aPZnUwgG9Bd7sjs9RXL'
        b'QXFGVpIoQq9PZpzxuzx0uK7NQR+jNiijNj6p8QntY1FcH/tzMfQxaoDyKGTyQMhkDrHJFu/om/e9Z3w11qbvFf1D+p4KWH0brbAQc2vfgw7o71ArDPRRPanbfLNGqqjD'
        b'l+qrWvRSO4I6gjucOiQdfCIahHSEdoTVhVg0xjz+b2iMzVBQjgsdQLvx9SLcWVCc7Iw6OWUmf3yMU2aCo0mFxt1NhW/hW16gwoJuoHNUs8Yb9fLwvcoSDRxNajbiN9Xk'
        b'8YJ80vtK0RWLZo2Idahbg3dvcEO3iDB6Syaiqixy3Il2VM9Xg3oMg7sYtD9IQhWYUDfS4hvNa/ENDSEen2HQYXw6jVPDege9Px3tQ+fd8G2yiuFbDDqLD8+iLCbePak+'
        b'EfWpweYBdzBoN7qHjtMvrfQqRGeIeANdE18lQ3GdKWIDfhtpUwvUgAOMjzBoH35XTXVvBMWg2Dab5xFe1dCauomhdOHDa1FPSSSoE0BGbzDoNbxnMo1qRyfQmXYAZrAU'
        b'Bl3dpJkGNzsIP3uT1pSd6hF+lbRDf4sK3yzLT8D78CFOB6kLaV02B+P9tMDLy9G+VNy1VZyaImBYUhd4Gz6OjmhAslqMd6NXzZpzVG/OBAuRMG/uQnwstRDpWsucmAqs'
        b'FeFbC8I1MDrJrHLDP5Vh6oqZCcyELVG0GjaRGt2Gj/KJEBjGJDPJZK660fD13/72t69kQtKRmkPcZlcV57bFM5osKNB+rHUtsnwKd+TLQbY8kFxYEYf3EhrK4mT40ML8'
        b'gpJZYSDilZD+gW7Ph7KJGj2W4+v4gSYTSDnri98BpV5Iak4IvYlMdnuTS0vQthlcPVmrA0JHuozedcfXK1o1YCiKbrVqPMgbhz3QthRnId5WgV8X4YPlHrk+wc4z5qN3'
        b'0X38Or6as3KDS514nSt+T9TqjPZNxQddSt1RP34V96bg+5tkUtwxPQmfFKHjWTJ0Y+YkfCKQdML7xRo4mlqCrhUL8Xb8/jy83YOZ4MxH/RXo+hJ8TIT24j3oWDzaie8T'
        b'SfZguaR+C+rD2yTo/upICbpDesEudLtuE97JnxBHyDggxdeyfUtQJ9pGJyLa16Ijg9lJvPAAnnfV8sI20tdAcU2M7+B7uLMEXZmLOwpI4ZPx3rlUoZPTJ4hvVlTko7fy'
        b'FSUlVHp/G99xqxHPpRmuY/OZLoapcK+qKtzNUzCauXTkbCqDMpxwYcLdycWCV9agI+gK+chZdgKRqM9PTyVtcbSKDNEr+GRFLH5jCSF4m3852lGLOlZiHb7rtAq9542v'
        b'oPMbU9E7VHlxpnoCvjrDEZn5iYVCH39QykYXZeQHY+uyCynUaby9XMZqqJR/OANdgA5AFjp8sEBO+sAJ1AXKk2JnQQqp/jtUSXUROlaDzwmLEgtLyvLpPkIB6HcmLKCq'
        b'4JaufzBfXlicVJAYT3rIPpl7PTqL7msAgQ+/gy7iM/jBQpMy33M1+eajG4RCOuKvxaMHCQr0Vjw+yDI8dJDNQufiNNkkKmJJXEJ+/nJSg/tLuGGQXFiQOJ/Ttx2ly5mP'
        b'LpU3wxQwd37iAh6zsdxroxzt1lRAwxzEt/GlIqpMUjDPpHxr2rLJLy6lRU2al4LfcF6Pb8/LLyxRyBMVVLcXBp1FkZNO0Hj//HHo/Cq0g/aDt8oJq8FUNXkwVe6/rt5C'
        b'+E4Np69+xrnIrP2CLhQ4434e6hClaMA1PBkve7LKSmUl+ATWogOlBfKCioUONIrJRIIvkUljLzqC9y8LR5fRXdSbH4Hez49IRVcFDBnl233Qifm1VNtxJT7QRqbNG14u'
        b'zvi6F77Rsk5D+uxNiZ+aX6pex83sO2qnlOFj6DQ6lVrIJ1PdFQZf8SqlEx0+QvK/WCRLpFtYCkJSnDVjRNan26CWsjzcGe1Ar6s1VCGuV1VVhg6U4wMVMD4uxgvjWXQS'
        b'X0Ov08+JSI/Y57Z+Pj7ryZKPvUZmFdI7uulCIptOWrUbk65ZTOKmMvgg2tOuoZpQ9+rQYaovXd7G6Ra5LeGRNeRVtIfTTe5ORdvJa4W4z0oTbhp+UwNLcXDTRlD4vI8O'
        b'FIsY0CZzldLvleIbZJ4r8leSriRkBGEsOieupN8LRCfWcT0D3whKkKFLAsbdm++Pr6O7GhBTt6D76Dp6q4b0bBndKJMXgFZUEc1oPNomrMNn0S0NVXU7I1psmbRJhZzD'
        b'bzpjLQ8dK0Hv0b6ePd0/gYyJxQynreS+ku+Fr/O4YXAI33EpKhDh1+QFhEABi87gnXNpZyrCZzfhzkQFPlSMTuP3WUa0nOe/CffTgsVMc8adSbg3BBTWBJNZMrjQKa61'
        b'e9ADcVEi7lHSKFLkNwhncJfG1VTjd0mW+F4RjZvJostkXtijCQdK7qMzcxPi8O1KbvSSHgrDV8hEoKNCl4pNGtB6WlGG3iQDfS8p+4VSBekfe5Md1Y8CbXfCXfi+L6eh'
        b'/WZRDigRysj0kz/VZRoPnVdn0SJmbIDqxzfxbYEa33BiePgtNhFpXes/8i/lqaP5DDMh7daBBUVNQ7O9X5mV8tsDEYG+zi4TCp7mPy3+Se6lp7GXftG2LOI7+QuUkZ6G'
        b'p/Nv7fmlvqj8z7/3Ff8pajr7xRdJEv+iT7/45EdTUv+Z3Gxt2+rizj+yZW+un/SnfTMfuSz+/OL48XO9Jtajvg8+6s7+t1Mz9kw03DhReCcgQv3kwUeR/61flfRP+vHH'
        b'V/MSsM/q/xmYfuLqou9tKL0aXLzyu4MbtHniuaV35WHvT/tr4kTZxBMfTPrknR+3nJQmv5MdkNp3/2RpMO84L7Xc/aHBpbt+nvHQwnHZXjHN5WHeWwWKqpWLXf9QkPmd'
        b'na/lXB7s9a+LPC5LPXrOZ964cTc/rkjeM+3JYsX1/u++uSPnwInfpwvOl6ON007XKC7Ij5ffro7QlJ7+j//M/s1fHu6pGZQWfBa0eWOV4K+iNyr2GHdO/ZFI/Lfpbfve'
        b'OnHolZOf+DyKjbwX8QYWnQtWfRHntKXB8NtPvDRD+xPrLq6J/Muq+f/zfknD9vcPXI05dbvn0fx3F188/edfdC5bui/08x/8+ezbPj/7Rd/1O7+IaUp4787eyj99uep3'
        b'Wxb+fPNvklqnDJ/uczt96q9v/LD8aNt9p9Daq16vtsXnLFz6i8n//PV/Tby3s/FXfXPf8/9ufe9X/5Vx+NfZMxI2h134eFrDB5kD5Tm9/3XurdyHBz7+wY3fzClNX5ho'
        b'/OOOTW8Z+J80xv6gMXzohz/vv/+X5uiNcWf/6r3sottntzRFB50aB+bXJv75tmT9o7D1vek/bfzR1Lf37POcmTn+38rx+xMfR5Se8Vz4H5O/HvzXr7cefut7G1/Lu3L8'
        b'47J3fnfQ7/TR5e8e/mHRtdDXf/COvHJ3df+pdQHvfcCs+UnFT3eHdb6mnlHa+UXowbUPrn7+/ae/uSHb6/ZY//vEB99NjZXXxLRdrOg/ftZNWyFcHfVv+/Qr5VsvGH43'
        b'93tfCiundVf+KXTvn2Qfb1bMzNp45mjl2faH37/6wQdfetwYPv1dSWNv5R+mru7b5JZ08I9d39l2Y+uPG0J+/AH+kp/weAMbGjLL9f3kr53PfP6b039Z2tm5ap329z99'
        b'f6s28f6dmAUny/t9Kupqfuzx2w2/lrtvSfvy5w+ObdkXftrvQL+P9MynZ77/p39ZufyY+7HX//Sni7Xfudo7/JX0q5bkBzVtshiqA5oTgN4AfVayjC9E3VaaquidjU98'
        b'OXZZm1dUqvFMJAvuejZzAZGRYVYgE+c9fJDMn97oimn6JNzjHaphTOYb/D7VboaTgsW1I8rNZN3opwq4+eH4YIJFf1WBDzijW7z13riLUoVfI7P9DTqx41dDrGf2A7Wc'
        b'mK2rgROVYvSOxGpiz0jktIgvo1OIMGug01q80kr5Gr3qxenWHlOv4oR0F3RAyIhW88ImoUM0Y9SDX0fHE+KTZHifnGFeUbosJjNPRrhJ6XlWQhKsefJZRN4ToYO8RLwr'
        b'jOp7F6ObyUVWeqNNTV4L+A1ECjn5JJqy+THBoCyrmgHcVekIfy1ipEUCwtidRF00HyJM7MDXEujnCRfbT1ZGdIWXirWbuF2LkwJ8PSExLj8RHWk26V3j+zOpcinqXTFF'
        b'jQ44r/PA19VgfmFWgx7Rgcan0dESfEuEHuADwbSp0CFvtC9BkYXPWx3ZiBifAj7S1bhQLVvCgR7C28G+5Cp6wJ0WlVIV7HF4Dx/tJyvzaU7X9xhZd28gws3tS06E2b2I'
        b'MHBXVV6l/FWTJtCGccJvKBJK5aTrXK0FOYkkcMMPePjOBnSZ02zegbenjvBCF/M4XogsRQ9oAxBRoxfdKyooibYsfNHoCC2IJgIdAJ38jtE6+YfwEfp2IroxnpAHuswq'
        b'qUmb+VYhVSDPmppBN3za8NVRez42WrmlaDutFHyUxe/aKIJTLfBW3EEVwUkF76ANLxOQTmuvoox2yy0qyp74LmeYeIaw4mdJwxdyR2xCBr9b74W38ZskpPC0a7xdSbiE'
        b'TtJrijIIawo14NbIw6eKedyAvFFKehhZ+tFOyzqNTsbSuOgFwNYXraDcsZmlQftoowSRQnZwTE0Q0lkxNa+hU0+AqSEv3feNwj1jMzXoNrpEVajJ2Ni9kpBIVcJJon21'
        b'VCU8AO8W+OC3wp6A/Wc5OljNba6h99G2b6hBXUjqAGajUhm6U1SMD0YVkNloPhufjN/mhu3hGHS0SB5HppMilgkeRyYa3kZ0qEoW9/dTc/7HBmrw9mCtrzAa1tZO1XrI'
        b'yw65jvPjYtn2s4ule45bRdy+dnkEEx7d0/5ImjwgTe53uutjkM4wSmeAenFY96ZhxnXcUnZQHKVr507MPguL08uKP2r5ZJNBtsQQttQYtlQfuPRxXLHeL2YwOq632Bid'
        b'1r+if13/CmP0tK6SwRh577L+yP4J/ZHGmLQuxaA4us9zQDxZL55Moi5Unqs0xEw2xkwe5jOBUwbT8/XFy/Xp8BuMmdivHIhJ18ek392in1cxMKtCP6uCfj3/o5kG2WJD'
        b'2BJj2BJ94JLHvkHaPG2eLvdEaU/pgG+C3jfBpLm93hCTYwjONQbn6v1yB0PDtWW6gN4QQ2iSMTTpUWjaQGhaf40hNN0Ymt7lOugboI3X+0aT36BUZqoNvkE6ySid1D/f'
        b'KJ3alc85AJl6eHP3Zt26AXGcXhxH6ZmrL1tukC03hL1iDHtFH/jKoDi0e2vfeGN8hl4Mv4dx30tCSfp55YY5FcY5FeQJfU2hn7fQOK/KIKsyhFUbw6r1gdWPfUO70rUr'
        b'+4R9Sl075ylimPEYJ+e+PAU0va2+PMxjQ3PYL/k8aS64UCPhMMMLygUl6uTJBr+ELoUub1CSppek9TcaJDlGSQ4clFex9OuvGMIqjWGV+sDKYT48BAduKXox6QEG8VSj'
        b'eOowI/CXD8pStJ6DkdFaJ63TY1kCuY5IfhSRNhCRZoiYYoyY8igiYyAiwxAxyxgxq8tzMDjiTOLJxBPJPcldToPBMdoE3UpDcJIxOIncUn371sMzumfoojh9e9pIVu1D'
        b'U2wx+I43+o7v87FqyPmG4DJjcJner+yxr5jQBRr+I75YdBOPbOnaQsuUawjLM4bl6QPBh6p2k3ZT36S72XpppkGaaZRmDogz9eJMmrDIEFZsDCvWBxZ/c0VycfdM8AG7'
        b'nNWtvNB0rskwfopx/BTuySA3UgT+5FIafWbrya19rVc2PRR86KHdapAqjFIF+UbQGvazSLk+can+lVrjK/WGxHpD5Gpj5Gp9yGrSAiSWtECQ9IznSU997FJD4DJjIMA0'
        b'Ub96cG49RZeuS+9bdZdviJphjJpBHw1KE7Ttffl9JXfZh9EfJuilCu5rXfmks/pLu5bonPuiDP5JRn9AgoL0cu3mvkUm+4H8QdrbVvU5G3wnGH0nQJZQgNgzm09uPrG1'
        b'ZyvNJihKG6zL71MaglKNQdQyYzlnmbHUELzMGLxM77fsMdcYPem61t72/nJ9WuHd5YOSCDIgZ/Xl9b/yJZ8NBBxrCLsEpCJJ0hl631jy48apITjDGJyh98t4DO5Oo6CF'
        b'c1nq7zShK7sr+7EkTJuqbelp60sl/1qMyXMMCVnGhCywwAh8JEsfkKXfnWqQZRtl2eRTITAWIOyibhgDuzN0OQO+Mr2vDMDGsgdDo3QrTiztyu3KfSyJ7JlllCSTLwTG'
        b'ar0G/aKH+b5BPsOMOXgMTnGHhXArYkKjtXnDTnDtzARH9IRoQ4Zd4M6VCQrvcdO6DbvBnbs5zgPuPMlbPaXa0mEvuPNmouKNkVP0kVOGx8G9DxMSqZ087AvXfkxogj4k'
        b'v9/zoZM+OV8fsuCjhR8Vfj3sD3EBTHCkNnBYDNeBjETak6xNHg6Cu2AmOEzrNyyB6xDuOhSuw7hrKVyHM5GJOslwBFxHMrLEK+7GuDn6uDnDUfAkmqMhhlx3CYfl5D1j'
        b'kPxRUMpAUEq/nyFosjFospVdymBoij6URPRveBhoCC00hhZ25Q56Bxx3PeKqTdPFGbwTjJz/R/lEarGgyzZ4ywa9/brdH3lHDZjujZwbSXFIl7vVeZaUO886A+dE1HFR'
        b'AgTJ1C6hdoNF69bKm8+LGCV8S+sy8D2jTBscWT49tficG2sJjocDOD/W1t5hXgTLllF7hP9/ht+aDQWcud9yyXRjPnDzzAziy1jqyknxDfQD2Q5wCiT6h+oH7pTxfvkp'
        b'z4Eub2ZdS60qvKa6oYHi64J9gQlvmPSGeugG1Q02sLscmJFSyaHZVYc31raOypTTbI+rqpq7tqWgsY70xBUNTTVrZEkmiGSzdrBGXVunaQAV3Y1NmvDW6kaqGausX1+v'
        b'HK1Ba0NEfSNNWEe9LZs80dWqOfd0HMJeOIDLhNcr1aP1a0c9SG+uVlWvDQcn0enhBVRLl4xkdT3AEJPvgMZudXiNRt3StJbL1lK0AmVVlQwALMZUbCb1Y64PuKxvDF8/'
        b'JWkiqYo5pBpboTJbVlW3WKgd0Z12mKOpbBQbmRo3cBrKJANASrapIrOjv5WqJk0zxTRzmCMpekt9jaahWsXpYKuba2ssvq/V4XHg3lROqoB8lsIJbGwmt7UtNUky2ghj'
        b'6GBDhbbUmtvF1O7UdqWR0KwhFUnyh1630dz6yibqZrAZULUd5WnTAKPb9LkqGq4KzkPCKny5CHcqMix+OqpncyfbdHPh6OYM6p4BvYvO27po4Bw0bC/WAMwuuofOBMB5'
        b'2XYPJtyZD8eK99al4O7gsHzfmHWb8dX5aBd6Kwt1L51T0IIu47Oo3zlDsQlp5aG4B5/FPdnoXWkbuuSdgk9xp3IXsump3IaddVXxvGx3hm7g421KfBF3Elm+LA5Mp8EL'
        b'CThdcWIi8Z0lqwX4MrqBb9H3+4OoO4gNMwuq3EOdS5j61PQ6ofociXnrJzGcnu60TlYUkDKxipXtlxX/QBsYuCD1g+zVQfO1awI/Dtz33vZ7vzyX86uYL/LvLdqmkqe8'
        b'4i/h44m6f738y8mTJqyfGLCm9bq86jt1v5sY/orH72qvfbD8o1f9FIs0Yv2/RE4bv1vxpiK3fHrZohsfJMX/KnlctkomefMHroFl2yJ8f+zi+wfl21Wf/GrHH6qu/qq2'
        b'Kr9uX15HioAqY+a3RkYNTZO50e0WfGHy/NRFpu0/q72/KnSOOhjAl1LQ/aLSxEwfbu8PX8GdVEFmy1SkfZ6CDOrNsxHho1upjnAQOuWnhoPSxDj8ANzDcSbM43AXH/Ur'
        b'UD+31XEkcDXsDuLT+HVuh5BuD6JdCrqRs0SCtQmJbVlWtvvoxBrqW2Ar7pdT2/3aBjKBg+X+bnyLxnjWBiQkom3SEYcFDD5Ody2E6B18ELYri9Atma0zBnwHXeQ2wc6h'
        b'V0kPs9/wwZdaTZb/HZNousSV+fbbPfi1ggTLdg+6VvNcJdgRCd4FPDjRIW2nV2p5TqX2TxhOan8lZgypfXDE4pUIQUZxPCDJlrK/CYsla7RsNjs4J/fDBMIny8CDNyst'
        b'BW5ZSo0gg0rZxxIpJJ9K+N3waDA3PtHe005NqdMGpGkG6RSjdIpWQKUwdtxkbZY2Syc4UdBT0Mc7qdAqCDevqzQEpxmD0/R+aYNRsboZfZM4w1dvP713FHCE6wzgADzK'
        b'1ueyjUp20rOYu9Eq2a78UZq4lhp7w1YJOyuGZQOBU3lO8O0qYbNDTmQpriRrsWOHuZR9YS1O4jgXcXyLizjh391FHJgifS1wwL6U1Taa8ELp4mUxjdSoOXamli4oZPXL'
        b'mVOQVWbBcElyHYsHqF1RX6OurGmoJ7mkU6sjMxBMHUAP1qxKoimSciDMosmqrLIdI1dT7aZTsym5xW4K4IDVtZTMJpUSHpDV1eHql16naax5Bg1JuRXFVRRoS9Pc0FSt'
        b'NJfeXCEOMwX4TQtwFizMJktJtaa+BUyirIhyvCY/l6qsrPIq+cu+WvHSrxbMfdlXMxcteemvZme//KtzXvbVRTkTX/7V1KrwMTjXb/DypDEs1wrqKCNn4iNrlfLweFP3'
        b'j7cxf7O1z6OGKY4Zv7Gs7nJV1RRZe6QPv4iB3UIQFbhZYX1qUorNaKGGgRxeKzecyAfX11e/XE3NKa9wQEI6Byqj5uYYjg5uuNUrn8PdOtLd9FdQLvB3RSLGG3RWw6uK'
        b'M3PaGU6bYg/hEl5Xu4EWo64YvcmgE3gnvkd1N2agTnQQ30hJSREy41N4BQx+Hd0vpSoPm/DrsgRFEjqzFHSbXmOL8H3EaapMqUPvJigKU/ARHonZwU6t2kodsXkl8xMU'
        b'BehgFrzQwc5IC5AJOH9vt/EFyl7d8MLXhUwcww9mM/BlfJDSsNmjkUT1t+A7DFM0l4ePsREN6Bbl1tFr+HKleqLKvZbHsE0MurMZvWNyuNfmoca3vVRChrCB13j4TTbe'
        b'Fx+j5OGzLuhd0Fdkkgk/d5FJnr6KZoaPt4SaNTDxjXQG7V/fJONxOq930UGBhT50cgUQiN7bQHWF8PvTGQuB+Do6QkkEP3m0nuIIK/amiRZFE6VkwXhKSIJ4PqE9aKWJ'
        b'dvweviXjc5pAV9AFvM/yQQ8P+r0L6CCNbUfX8DsjXzyPtfSL0e00VzeRwm29i1rArEd3+C5s8mpSbKqismsS2uXmofIilw8UfDk7awLWchqz76J7raCj4ubJMpOm893Z'
        b'WYR5pf5UE+sLi0CkKKPGfqD8RmQMBp9DR9oJf7kf70TvoW7UU05uugn9vfiIMpdIMN3oPR9S86+hfvdF6AHWcRq2l0iqO2WYiDHManQ4iilYid7ljLi2zV2Gj4JR4f4y'
        b'hpEwfLSXzfTFt+sX5B7lqwNZhvHeHg9GXGePphEh5Xpg9RW/3X7fXTC+4G5xYlbsUv5SjyzXssm+Hf/8nX/6/oLyge8f+Y7g0Qc9P3Q/1zmxbNG2rrRdibs2e/6AVyeS'
        b'M6ti3fbfd1/1u9V379/an7Y/p1EW4rZo3ec1r15bE/gTrf7JRM31pKrvvdkU5H019+td7xytZZ0ma9KK0z75wbaZSzz+oyIFC747Q7Pz/U7ttvaN4Wd8Pz6U95ci14VB'
        b'eUNZh+P0LYov3s7TNKUUTu1tzioR/OvvIrNmeR3Z0virJ7/7tzkTtos/b8vSOXsVCxoCkg83Vi9+mLf78n92Lfth6e4tW6L/h6f8PM9TkznxSdSee97rnhYZx12X8T6q'
        b'b5tcsy/8+r/OfjDXo6vnB7tX5/pGrUxn1CEr3vSdJfOjB4rFeE9AUbFiwxyz0yqqfjBnM5U/ZvnOpUpl+/mM31JO9QB18KhIVY3fDksoSkS78G6LeyZ3Od+Jh69zJ9gX'
        b'wS8kkanI+LzPSVW1+Cx3tr9/S2YC5+wL7UbXBWgni19Vl3AKEXvJwLxGHaNRr2jobbSPekZbhzuoPgU+7lZo1qdgBWZ56TrmvNHh1/D14ATQTShInI2v8hhn3MlD2/F7'
        b'0zltit3odfSq2g3fcvcG7btOBvehW+gapbg0D11Fnc1pqAddIOMK7yGD2VnCFWZnA+6COHx1tohEkX58OCmIO43ehV6V0teOot2Q514i1CVmc0fdr+ctMfkns/gcw8dR'
        b'Fz8bX59MZTURvrdZvd4TXxKQV8n8iU+hfT5cvns34D412o86KlcDNV0MvrmQlBLICV+K95K3PNElIXnrAkOGzTl0i6vbbWgHeovMGe7LMgmvi95miGh5yYdKuapV69Xr'
        b'15Xhc/AtLYP3z0KXueJdbUwkMQH4FPkSeo3B+9Bt/Bp30N2bvNksxb7maivELkaXiNjyDXaOQWyBtWbE9FVNmOu2cbYWhOQRFfLieJyQ1zieCnlGaUq/T39Ev49ROgkE'
        b'vOCuWYPShL6WAWlqV95j3+BhJmTcRC1Jltq/fkCaoZdmDMbE9+cMRsv604b5bGg6kWpC0/85PeNe1F3le/XvJL2XNMxn/IMfi0NA2iMyYdT4C1PPTe0rv7L0boxePtsQ'
        b'lWmMytQ6D0qjzmw6uenE5p7NWgH5pEnadL4bbZDOMkpn6QNnfekEGQw7MwGRuvIBf5neX/apX+Cgf4T5DtAMN+qjJ+nF8BvJRGCQphmlafrAtMGg0J4gXd1AkFwfJB87'
        b'Qe1AUII+KMFRAlKaYPlj/6DuxfrIdL0//EyYi3z/yY5eeOzoK/C+bvyAf5zeP25QEvtIkjAgSejLNkgmGCUT9H4Tvq0EMQP+sXr/WEcJfhMg7aofTJ1yc3o/+fdQ8KHL'
        b'Q/JvMHVWP0C8RWTa4KGB7605rJUALeIcPLlbi1kqN/5oMyERY3YpzcnQUSBDj+6LH4D4rGIs7qS3EvlZBhLy2MG3KjqbLfaA+VJdAwcnYjushyFBZWmBYsitMqti/vwc'
        b'RVZBThkHfWjBgBhya66ubzT5VFKdg/Mk1xFfQtx5k8UFluosBNTl1Ue2WBEUOgJOdeh+A60wWfD/AU0RmPGfoxuiKofDKBs3+m+As60NdliHnowkTFfWz7+b+rBG71tI'
        b'fhyMYIgurV94t+KjmMEAyajLYSeBxHOYIUFH0bA73yMBYNUcB64zPWpIn/1fhLN5JqA6OED8ks9KEsB1XEJH0WP/0BF4upkATzebwtPNpvB0szl4OjhEHfRO1HsnDvrN'
        b'IWmCsyFNMPifg7Cj0A4zcRIgEE6GATcZxttkCj9ojYOXAx/Kox/Kox/KY0cBDAIunz/F5fOnw5aEFObOGnAP0P8kgP4nAfQ/yTQKuGcNpgcIhIGAQBgICISBszryh529'
        b'PCYNM88MwpmgCK2zPjCZ/HTTdNPOTu+dzt11FACsiGMcEUdgIlawIqwHLCajA2cmk81ih/mtrEfoMPN/MlTxGU//joXaKL1HmMEjzOgRNsyTAELLs4IvyUtSS9J0Lody'
        b'vUekwSPS6BE5zJvuAROx4xBejnKYisNTAV3GlFjcw2EunN8wsr/OMsF5gvoqHxvR1N3096t2MiMd8wNz3REUlSV8QFDh0FN6BCb8FO4aUFRcyD+4BjQVwFLhno9ceyvH'
        b'KX2UvvTaT+lvuQ5Qisl1IL0OUgYrJcqQHrclglphh6iOVYbutLOjBOyVbqduVunW7d7t3O0D/66EvUnm8csWYC0X8k8pNx3T8pVRo7A/nHhMrVAZvZNRxlwZb4d/4szl'
        b'3+3Wzavjkdx9yf/e3T713J0P+apPt0u3a51AGXslzsF3EwE9Br7c4dLh0eHT4VfnrIwfRYELRUQRUQyCcXUiZcJOZ8Bc3MAu4bAVk4Z8YDrNUtUq61soHlBdrerpRJud'
        b'hdEJwulep02ip0kaVWN6vbopXd2ipH8npqRMnJgOux3pG9TKdFi8klJSJpD/U5NSUmX8IYGidH7JkCC/IC9/SFAxP2/uRXaIl51DQhf4ZGWponjxRYEKuN0hId1dHHKh'
        b'ezyqenIprGuoXql+kc9OgM8KVImw7CVBkMyHdbdAUcb5+XjBvKbJhHZ5qabRDMuyF2Q+nbOqpaU5PTm5tbU1SV2/IRH2fVTgVS6xxuS9KqmmaW2ysjbZjsKkmlVJKROT'
        b'yPdkvJH8L/IoUIuqgbqVG3IpLs3KLK6cU5D1dDwQnTWngFJI/s6t3ggL43w4iVW3kEyTUiaRkDAfkNn/x957wEV1rA//Z3dZOojS+4K0pXcQUKSXpVc7HUVRlAUVO1aK'
        b'IiIKIuqKqEhRFFTEApkxUXO9yS733Mg15ZKbxCSmwY25SYyJ78ycXYpCyu/m5v973/9VPsOy55w5U555ZuaZme9zjlW4gHHe54bTqpoYERMWFZIWGJAUFP4ro3Lhc5h0'
        b'jWb5qdcLDwYVFgiFgcRONTGOqIKl0cKlJCYXHBN7LCaUwAAc17QXyuOpwdSZeqo9aeHxVSbEgsWtMHiSuGcVhuJvX4hkFonErTAEX5v65S5P7X5DTh8qZOfkZhTnF5Hi'
        b'J3X5vwxg8BIaanI6BWNW22YIb4BTC1XWjp57AxXgTN4S+CGXgCuGLxO4gdkotiL2KlvY4TkFuOKhYlphQXERahOM38iJysZRdnECw2IDn9Izri7+jRyBWI7MN+UU75jN'
        b'HU8TWMf/I2gC5xSYwbtokhF80+gwHjeUTzE9LSlmAnlAWVZNhynZ5qFJyAMswhnA/miIJ5pc5VGqgOofQRV4f7vCJKtyEQyoL29Dzri1uSxSMcweFdzV/MxaXGLx6tUF'
        b'hdjMj1uwFNYq9Hn5RgfeC+qAZxMcwv/527A6+cU7ZvFsbIV5eMPLWi9HT9tfESWjoXg2QeG/fLNUE+Gb7Xm/9J6ptSTPJiLpNz3h8jNP/FqFh6N4MdFTLXtKl26YNQ6G'
        b'oZidk1lUUCi7MuWCKR4VMI+9KDarC/MKCvOKShjvpTa2eKxhixKERxu2k6+E2eIxCL4Hjwhs8bKnLe7KbfmOY3uyPB1dHZ19pLdMHs3Y9i1ncqs01rGvPcnXTNRTZYwh'
        b'3EqzNgmllikfayEB1U5ZPGTrgM9ECCdpZJMzZaUQzSnTNIaMZRLGtNcX2a+Yszq6g2+SDXr4H7pWjJfb8Uo0WQEkuwdzMoqwQKFMlbyI4sX716YgeeJVRBTPuoxC6WZD'
        b'/KgUNUpKh5eYk4PzWpyfw8soQqPHzOKiyZMVFJAUEhabMD8tLjkhLjYxJC0oNjgkkaRydKMfoYpOsltQWkiMEmLKJy4gIkaGkJbVm8wqJV3/nHxf3NiaKFlnZ2IYW7K0'
        b'fUGn2E65s5DU0GqmnQpJIb7w7CxbJneyW/JWTY4ZZSC6aNzNLKPivYSreCHJCVOs7a7iJa7LK9qQU5hPKq7oZxLPKMQp2hJqMBFFGfkl5MGpNZzt1DIrpf8yFTIGBcaS'
        b'L62SUUAws81iihwVMRslx7k3nvDsBHj0lFqLxPTSujcqHungUCgT3xfinbxOyFRofEuJCAyI4WXm5BesWopj+oX1YaVJxncaMcxC7E5wais8KIBVsJoDj/hTbHiKZQN2'
        b'cMg6oRxsAq0M+CfPhdkcqQZuMrsjyWpHH9wPdgrV4O4wNbzagb23hYGr5Oh9eDD2uboa7AUnZsCr6H8XKJej1OBONj5iCuuIJSFNAVaSY6ngAmxnkC0UNQM2ccBeF9Be'
        b'jGmO4CKohzsTGdBFVtDPODzDpCJ4VVkJtKTy2czotRrugT3ShU5YvpDCK52OQmbxd5tQnSyOwiPzKbw4qgUaCNLCB54B58Y5uSOnZitBJZO8UbbFajW1BOzqzsYhJtnG'
        b'BlbAvU74TOy5JKkLPQe84lSnySrmh5LF0LU5UcK1bvAidrTGeFnzAS1kjX6rnwJ131WPrNG7R8RSxRgZCqrA4QKZ6zXvLZjZEe4YGQ3LUZadEmBZVHw4JwGUY/YNvAZO'
        b'l1hSoE9OBdbDXWBf3qsqM9nChyiW3FXbV8bdVAbOGrdud+fVpMTFiT8eUdtE1cGAq1eKNBbL7RHqKkxv7P2uZomK0j53jbsf/XDv248yTsSpKFZa/C2Fvel03/eqYlbs'
        b'gVN7Z0Teq17lYdd9R656ttyP74p4f+k/ff2YXKrHo4oZ1iOf6b7SajH0eNC31jDqjabSwsW6nGKfD2/JLXd1Gklx8Pput05qgLrbW2/M7DBbF8n66drSljPL7n0ZeH3L'
        b'689uf7f9/p29V9ZcXMiffuWZUMFQb9v30ee3b//ad+ujnYJHj7ac/9Px3Pj3/uGf9/G7K7ues/bIe8Zv+IGvRhbO5uVY2Dk6hDtgqAbeNtnMdkYCc5wsSuoVzmBcaWJf'
        b'oI7G9ngDqAKlnsBxcSwgy46+cJuCdFESbofHZNs4YbkVObK7EGxDzePgjJc3oILj8CTj4uos2FYkiIUn7KXHz+ENW+aM9x7GhxSWnY4A6aFrcuR6VwhzGvmkdg5zBF0f'
        b'VkzY0wna5zBrqs0LVsuWIUEfrBpzf7QohNnzeQv0mL7kSCk7JEqeYhwpWbozr6rQge2YVWGLHTlO8Hjl7MossB6Ex1ylS8YRsFF6XD2skFlmPLI4Gr0FN+FuzlwfihPN'
        b'Cs1yJ9k3hrvSkOqYHR6Fcp/JcgGXwGm+6r+1OIANhuOPqYxzwjHpbG68b55YFkOky7ajpuuIdWxaLCQaTrSG0wMN7wEN7x7dfou78uK45MFZwf25d5eNcFjT5+GdpCgc'
        b'ZkJ5ysCk0bBaflDfVOQp1udXcwdNZ056zFRTd9wZLV1zUb5Y1xX9vGtiU7980NvvhloP+t+/tn/tMIdlG0t2rcaRXatxZNdqHGtI11Bs6iTWxT/4WCTFsiX7XFGqbMPI'
        b'/eHk/nByfzhryJA3TLG1XQdtHOrlGtUG7V3q5Wg9/pCmHj56Fs6qD31g5DBg5NCSIzFyp43cmW+HtPSqgwe1jWoXicxFLiJzWtuyRatdX6ztin56vG74ol8vOCQa5lA6'
        b'bswN6GfcrFtt3Gmnn5/ATrkRVo164SzSr6zdaDxXb6EmHjxKtf3f61CFeO84pTSLuqYeoPA/cKjCTcOTmal8I0xWVDIPCftQURWexbcSDwmOv2LG9KKrE2ywTQwPSHgo'
        b'FxwSmPRQLighJJivMNkxt8IfZM7qHypkLcsoXJojLFzKeQGYOE2WYREKDilOCUzEuESFMvUyeWLAmEbAiBpl03On/YFYxKV89vstkxkwArKz0ah6/Hka2QBuEpv56ND/'
        b'ZTtILs8HT0x80kfJy+mT7IG0lw6kR50l4AM9L59/Qm8fn6AsNFDPRBOiguKiselREa6VIunk8VdNy6UTKkZofsXMPGPl2LPjk8N8z8sQ8nLzCzKwyQ1NrfLQN6uKV2bm'
        b'TD6Lwa9bNWoIwmNi2WbrABLbZPsmmVRMmK6OT4ZsslqUs56Zi+FSYRxGrGQOI01xugjdk5eNJxJjRVGYQ46XoZQxeeDZoIQWkqyRiYJ5Qqijo6M5f4opDrONlJyUy8DS'
        b'JCwqLM4qKkaxj8XsyAuV7cIed33S+EafIZJZvDo/RyYC0i3uaE6FM4umfStRUU4ah01CSGgI3oUQkhaTHB0YkmDPk82Ik0LmJfGnLO8ccjQOF3bOqmyHogIH9Gtc+dgU'
        b'rGaOCv5MDOsnMzKgb3MK8RHD8UaGn40O/xu1QeAS/jkTwagDD6lUTxrbsoL8bKRSJ7Um8FCphCTEBES9bDmY/DTdr7QmZBfnpOGTdUxRoL94+C8isFK5we2iKGcpkgsk'
        b'IOnpMQWrsKb4mWOG64vG3o4jw7GgySM+2ocVxKjo5hYWrERFlZ0xxXnA/GLGaLs0b23OKpnko6aZjbdD22QVrBLmoeLCMaGCyyPfolKeMmFMNONNXfzx2WSSWpC5PCer'
        b'iNEHk0+uE2O9PZ1diHCjyiH5wWmwl7rEkuaX2J5w20RKcdJ4cosLSVsjrZ0ccZzawsD0cD68ROmMXshbtywvaxk5MVmC3pKfjxpfRiEzr2dunly3CIUFWXmkEkbtC6sL'
        b'C1BDJodUUNFKKxs1BEbsJy/MMS3nyIspQKp29er8vCxyUAObekh7Gn8CdPK2E8TojAypUkRvx50/zwaFfHseHgLwbGKTE/i4MvBQgGcTGBIzRTu0HXek1ZNv+ysO2o7u'
        b'eg8YVfU43Uljyf650zS/aOYwjSGGDKWoAjR9g4fgldFTnqDbnYxryRQ8Vkt+C80hU3D7OTP8GMf07usNhGrFsGnUtIE3Pocy29CvrISdQqOFY/jehVYM+rB2nhB2ccHu'
        b'MeYv2KmYRDx9y4MdaxmTCGMPUYLXx5lEToGaYgGOYddiNSj1epukiG5PsoHXfZlziwIH25Rw+8jkn/P6jpHAF0Kmg8q5tiRF00HvGmIBgWXO6ixiAYHtPsWpOBdd8Az7'
        b'hXf90osIRNUxAgXxNuEymik/C16Qp3yctWAnLA2X8hHNQIWKWqEprEEDQGxfAae8itehK+HgUpGA4J4dImOxhcUmPBpW46i4sAbuUrbUB+eUxywbc2EpbEQXmmaAXaA5'
        b'CYiy40F54BbQALaDNvT/FPq9e8V6UA3OBGYuARWBhXnx8cuXFFouAkdWLNOg0PTUCDQWOjLb7MtBD+hUgVdWg4vgkiqbYsMbLCd4cRbh9oJbAdNeSNlYsmC5PiifCw5k'
        b'gl0T0lML69E3TbAW/403yadPg3t4FGiPn663GRxg9tvvBSdBmcpapSWwWihH4U364ML8Yiy9sBXegodGzU38FCnaeXVxcRKsXq02DdYkSYs+3NFhZpaMbIzNT7iGZADY'
        b'UQpyKWhRJKcB1GGZDpLZY57F2DkPHxyZOyl+W0aXxg8ljatS+aAwCl4Ge9TC4GmwrzgEZ2NnOEsQg60pUl9A+0B7HBEbFKmAsGiRLB3kCiNBxQzYBSrgwQRwC7SCSlDB'
        b'gn1r1MI0ISPkxvCYzksxhY85g06ZECHYpQJqtSzhGW1wFpzW8QrX5lDgSPR0cBremlc8B5diV0nRJMhsNjwJa9Fbuv1Q3WyHO1HJkqMK4PB6UJNJwT0JqgnG4HhxLGm5'
        b'YB/YNc7uFxXBj3RwTIFlLxWVLF1qOOug03+s0WCEXfEMcGDrdNLADMEBSNCiGCuKYvzVcXvDU9Lox8edEKmF0n5dk8iUBqyD3cK11lZjBsVicI3sOyVMdvQerh2Wi73w'
        b'oJuzM9iZBGvTBZQ5uMwBt7JX8tkxSXnzt9KU8CGaXmbVhOxKuh4DnbWKG9cddN9s4eBQxpJPD/xHau9FLbO2IDsu38G42m3b7fS1txv4gq01b1ut+cftlQ4hr28+Jty0'
        b'+Yu059Mybsvfz0nZPf3hK3UXik2f6Xy3I+fTwMzX3pxzpjbl9R+/CdHa/mqrXMChBQsE+5aaN235QOlClNajxrLMuZJYYaIlp9j3vHP8kYVf7FqWtHioY0ZbcGy3TbOy'
        b'S4pC4+CZ+vpX+yLtywySTnp/a2EgTAh6re6Vqx+8tTAs2661ODOxO2Rk5+PPRl67UNzK8b0U+RlHL/ibNOXbK49/ofX0S9Yd3dXvpBzrU5/n9UXjg2cfhAWnjygfvq4j'
        b'uPrqP6ZvLfZ+MO/+5x5up6xLT6WtcbdVcFBf+mltStCbcQMdtg0nPCqWDhULvvqY89fP1p78qXeOUmqVxrevr9977q10NYt2o/2ffGVzPKGjyuyLuMHg0lV97Ad/ynj8'
        b'z4qPNTeaRjylP2qN7nw281BW+U+PV6XonR/y373WLOADzWP/qs4+UD5Ps+2+YK/iQTQ4W9XmJ29tdmvmp3N33zFaf3F3+52n98+G5gbumv/ajIMldOO0ki9LiuvUivc7'
        b'n6p6svud/hX6l+IN7q6+vdAqc3tT55myWOVr20s8vv2L27fL11ydvkfp+HXtt1T/VrnVdPaZD987z9ch5z4UTUDNeP7jtBQOvAn35INdCoyNsAeUek8wdMJmeI0YOwtT'
        b'yJkH0KsBLgpi4QVYJrV1BsNz5GzHAvt1gjHv6XGgmpxFsQEHGdtiHTwZhm2LKuwxEibs8yXnFMBOJOinQeU6dXgoT025EF4WwitFavKU1hpO4kzGlLoZqYXdDC2TmECn'
        b'ww4Gl7kK1hI7rQ685TRK80RNvAqckdlSi+FhYukFfaBrs9TUuxHcGj2wv6OYpFEeXoRH8NkWKOKGcynmaAvYvZKYmKNAb7Qd5gXA3bERoF2Oks9nm1u5Ed7f7ERYI4AV'
        b'OfOliFEgmk7SHOyLuq4XjpBwNsHTweCQ3RNLXGZrXF+y3KJBw7VR2y04DkUMBGE/uAkPCKTdA6YfwipFDEBcO485OtLhAW+gy/bG8eCcHCVnzwK9LHCdPLsQqXNi+GWM'
        b'vtfTZHZfo60MQKHGyMDOMdTegWEONLOdPT0JFhK2mcA6QVQEKH+BeMihnEGPfIyT0wxHhoh5CtQvI3KDOqNYNPZQD+ZkworZsIwiqdsUnm3nAC8bjEchbIN7mZRfB+dh'
        b'L6h0MkmJduCjBMxm85bAW3zd/y82peMEyUaVU+ORzCexvE3GKfxY6iU+14HxEm/VYiXRdaF1XbCh2XfQeGZ9iii0Jbg9WkryCx2aws7Ms2hWpXkuUhghz6NabdDMZpzj'
        b'8mr1IQsb2sL9gYX3gIV3j7HEIoy2CBNrmA1q6tf6t3iIXYPEtsFiTfwzZG5dLagWDGqbi7IHtG3F2rYtW/q1BpxCxE4hQ+ZW+NqwPGXh0hkzMDMQ3WdgdsKpwUliYEcb'
        b'2IkNwjvlu6f1eww4h1crDPMmeDxn/J2jrFl5Ytu3ygiHZRVMHKUThBoKMcMvhMWwzWaJ5Ac0rcSaVoOG5sNkd7nU/h1AzN6BxOwdSMzegawhw5n4WefBmdZnfZp8Tvo1'
        b'+9Urfjc08dAKiSZVFk0KiSaVRJNKokllDemaoNvH6IdjEEjMcOTjTfIG42LUNcExhspiDCExEkYb4RWy9ENZGMTmi5OWwKAJ4yQm8bRJvFgvnlkbSBbbzxZbzBFr4h+8'
        b'N96odrNY17kzFRP2BjyixR7RQzyHTq0BnoeY59FjQfsI0G9x3EIUEuRessQ8hTZPERulDOFjQS1csa4D+um069eiAxIGXBPErgnkzeOgkjjditODWKKNzO/OzXfVB7xS'
        b'xF4pg7LkxjDJjZKYRNMm0WK96EGjmY2xOLvodoVuVeaTNOOBJONBJONBJONBrCEjXmMUbeQsfSSpexHtEfqLTw0r46r3faDJH9Dkt1hKNJ1pTWcM7zMfNLXCzL4hU7Pq'
        b'8I+0DcSGDi1FEm13Wtv9gXbwgHZwf+rdXHHKYnFa1mBInDhhgXhRNpIvnVwcPQqr2ahwURTsWhVc8NI3iG19JZp+tKYfPm/kgprMMAf/tnduj+jRGbD3F9v7D5qa1wtF'
        b'7jKpkpg606bO1YG14QToZ9GiKtZ0Rz+DNm7VwbSW5SCp1SixpjP6GbSwqw6ujR7S1a9WGrdCMmNKHtyYobxw+ctnm36NfsKrBS9j3H6baqrGyyivUROXURbbs1gJZPnj'
        b'jwp/10WWFqU51C31ANWJiyzyMlPANhQckiebbJnt8QplimVUrvzodtsXUSW//3bbpXz20/SXLBcJOauycwqFv7SEQOyVUhsJtpBlCHnzoqN+wRBiQr1sCLGLKQ7EfW4D'
        b'KDcUjB3aiH/RQ0plKp5x3ADHXuAcw0bQoaY9Ex4mpgwdeBQenTC7wFMLedBCZhewVpFMUdy5oFS4Fl7i4REnM0UB+3KLLckAA03rD+KLRY6wwslxLZpBn0IfIjGJyGIJ'
        b'1wtN2BifS0Xg5gz8Dm14E0ViQoFqwQrmiH47vGkm27pC9q3MS7PRg7uIQeekIjvyBht/Ss8/pBQi3a5SAVqj3WC1mzOqJHic8piJxoWnQ6Vn1ZeBLoYRQEERuOmEhqXd'
        b'jCXjAGwAHSpKhTqzsZ+RcxTsSFFkUnAIdvDs+LYYWV3CgnVoZFOKYjzDXOxCk88jAjwujeFS8jqWhWxV0AMOSgkMoHxpItwnR4gGO8FlCuyfD0+QByM0rBKxNybGqQno'
        b'hocxPgpeJ2f9wd7Fs5kj/Rx7lhmo9FdUZQwbjfAKikmGCMB4AA+hmTGKklilzubCPaNwAY4BSyN7tnYMiRAP6A9jq5QchV4YqIO0N5PCNtC8RoYI4KiywEFnf3NQS3yD'
        b'qKmD44lgH6xNhvvgIewvRTGWVQgPwG7b5aT0gX+Vxnm2N5tyTlcPi9ZjbGynZ5unv8Uqw1VifsxUgfnyiUu4/CYWj4V0m/LdBUYTt8oryOQ4CrdiVh21lNpELTbdzCpn'
        b'i6jJ/m1iZVPZrF1s/dFvzqD42kbjPMDeyyPO59kxn4ZS+IzEQ4WA7MKovFU5fE4hztpDuXz0B6NyMflodD85blMbHCbRsYWkIY850vXLzxMWZRWsXD1nMWp+XztQZCQo'
        b'dsplfu5qdbKuKl1S6rHoEfaze4Q3+BLnYNo5ePQG0p+Qsnk/TFVewkayGpce1Vqyhfnym1U6fmfY87Cl0kjs6kYxbk5uIRE9+pLHHC0hZ3lB7FoplmJeghE2fEmNXvA8'
        b'3Oak70XqWs8JtKFLa9TQ9EyLhRppky/YAY6T9+1zVWA/pRjL6H3FFdg/L5YoPXgYdI0KYgHo8wcXwDFGcnZ4IqkhJiiOEguUgYNO2EDGXKvVwulEDypQHCsWOL5uNmwC'
        b'nXxG5uAx1NZ2CGPQtOCwjxzFVmHx4DW4/Q+RCaSlYwrLcd9cgY+oMNJQuJcj63//XWHoGC8MbnnMz92kzoCrEZcierL73foD+91u5Encw2n38NEbmDN3xMnQIrhdZS28'
        b'Mo2NS9UDnPIG3ZlEQbrBk6BVpRAl0FsbK4wjJbCUFKc1POAJu1SRYjgALyogbXKQgu2sOYTMIicH9+MDFvEUOAgr4+GlIEaNHOFuUbGxtYMXo1jYNyQ4GcleAGulGJK5'
        b'qkhZdDlFwqvoKhfsgGWgnAUPG63N64hOZQufI20WanX55rz5BW+HaixJmMGPV7BMq8i8E6bum3esedaG02EDb0V/5XbT8Nt3XlNSq9+u9d3Jebe0+Au0S+4KJKksrpzW'
        b'Y0Hps6M/7fypvEpL+Orp3MO17yZte//9zzf93ev6h2+of9/2TeIXXrmX3sg/+56b3mfw7zvS3r7psPK1npNVP6UXPT5+43GD6vdrEl+Vs+daacJmyb3XnM84P+Ny6wLW'
        b'zNL++Ciwv8iDHTZr67jze954vWX73ac7yhZ9woqqeruU2+b96tcXF+UPxwR1a2+gR9KWg2UdQVHR9x6Efu3QMm+V14fzojyc/hmQ8XH+2bf+nBU15JT+k8mzbzwa418V'
        b'ic8VdG5849GCIcWzn1l8zQ3JKP/Htzmd7W9/E68lEmguTZxxxUbtWn78J4fL56co9lV+v+uD5DUec2lnuXWv/eNM3Ku9XsYPHQ7qHpV3OheeUVufpvBMtTVxd3HXP+ZH'
        b'3LevONf/dG9W4cqwfs23r5yK7Xw+rfN+hn3QvuKyQ99WXn8bvvvhBeqRhsvb8UXFb79ztFg7d7Hhn87ofWAS+oNu6fVXqk2/m2a9vDfhL9w/64n4yW5r7zT1fDr7G4+4'
        b'IyeCj8V+5r57xXpWrU7gtPZlHRuzwfcR3TFtCsWtTiu0Ox0y87dfjj6Qd2z3iGXROyOHg65f3x4yrL9Y58+vBejzuk7pKT+7E7f1XV+Th+8pbXcz6DJY8NPf+6/tXqP8'
        b'6ESqs7Vlrrbz2RlfV480jvzNNLp1wf5P/Zo+8WtomflBwNKYNrehhbEf+hq/3/aXTf3FVgcE54V+dQFfPL22Fg7t+fJD7dt/Ez8sO0HFXXh6Kfeb9Av/yvGnrvntfpTw'
        b'2fGZzz7WFPZt+7jq8y/lhxdbfGdiPe8f3/sHfPi9xaM959+fsXd2SPpxq8KAR68ZPnPevD/rh96O1YuUO97SfmWBQPRDVNP527frdVk/fr5F4ruj4kejCqsv/U88SIl/'
        b'98c3Liv8+JF++pbjd9c9s7i0W/vBTs28k5+WGT3zH+gWhS6x0qpcnXz7zvZLq0Vfvb7yPWXbHbcWJ92wW2+R9k6iU2jW+R1Oq3c8rvrT+1uLgj/9srUpam2yk8ZPukrP'
        b'BfWmtV7DN1gjrqU9Bg9Xn39zf/LVnLL1ljdMvryXqmSir71w3Sf5T/+5mKX3VaXR51/20av+/nzH48MmKSeKRKuW5dVd/rxF4bs6zQ1Nz08lxj94OHzBtrfunseWed/f'
        b'Tn3mEfhR8f1pb9KGJ7+4Wb7ho1nDH1cs+OGDb07n3XXjdjj3P9Up7VhfsOdfw2/cDLrP+uJk07KV3Pb1X70+/17F5wWsrzbuNNmye/YngfeEnAcRG1c1B1j7sb7S7DqZ'
        b'UtAcViSKjHpdPemV5k/mjnz3IfpwGn/4cZ1I+e8s37hNx+6pP/nk2I3tgwUKG9T+lDOgnnTPIlmhteS1OYoOz40+2Rz+4YFnfoLjch/tb35P9HRT1Ccni30qYgbrTojW'
        b'Xy02fW2Opbv/zGcnNH/67OCHb+zPe/Cq5a2FJvs3b21k/RTt/s9gcB3q6kX2+NS2qH9zK/hAsvGlWf2bDymfXXJoqHXnfn2x5L13b338zmxL5XcvuKxateOx16Did30h'
        b'Pxbv/2D5tu/Ug+b6zz71w+OW7+cs3bd1xV82HemSfGJ4+/OfjjqZnPKas96t7K2ksofKXyx+9G2wju0HXyW9+/CHlJvaAWfFevM3Ja/tXSEuP9745M9q720SVDz6s3i5'
        b'jvbzDnFF34Uf/uS9pOu5a++Pos8eZWY1fA312j9vvHvn21131822t/5m1s3XlL2ec0OeLOSW5vBXMC5JRGj8fE3FFu4D1bCBcZgi2+NpCrrkkBo9K3WoAxq1vMccDSnC'
        b'y5lkC2oXrGL835xHmn6cCQ/b72ArPMCTW4K6ScZAWOOhIoD7BKM3THPmzIA7ly6DZcS0O0Mj9yVTJBqjnw4Ge8FRspE00h4lGN+ShTrjcQbJUWOk/QoSUyFo3YDvw65V'
        b'HBzDo9C4Vgc2zYySU4Nn1BjMTxW87i71QUQ8EGWBfWyHJFDHgHVqwUXQJhx/ZFwN9nFAjcncsJmk4NLRDdVCR/Ruh8IYvpLzZjQX6cLLRChjHModtsknBoIOxluO1jKB'
        b'zOYsn2ZizrbFy7PErGnqC48LomzhCXhOnmIvZnmB1mJicfSIghdQbTih6Q5O3f51wWxLUOvNVEQrPASqRn20KArTiI+WOlDDIIpuwbNLVGCZA7wI9wo4lMJCfdjNjkVj'
        b'eFJPuuAkPD96GXahDlINlLGdk+ANY3iRQQPtU3Ul6F7i2y4GHAPnYCXsZYzk2yPgLeZxhwj08oWwS5mdOoP7xIxchM3wrNA2AlatJoCl/TFpsEaB0gCdnCLQB0+R8rA3'
        b'QC8mYFeK4sKbW1ezOeqo3IkQ3QCnVGGXAF6KVQHnbOQpJXgVlIIeNjgdjxKAhUiQBG8JsVcnJVQ1XEoZVunOxEvD3UjIyGbkWjkjnD4lPuwk+VcDNziwXkcT7NvE+Kza'
        b'v8pHSofC5nNwSAB3rN9InlUFVYG4Fu0c+co2tuDcTCRT1Aw9DtymG0ikBlzUBRdVHAXwCh9WotyDHtiuzl44z5XU5tYocFQYg530bs/F45sWIFpAsuUGz8+DXSjDuMyJ'
        b'S6q1XC41XYcDjvBBBbO+UBqWJIixB+VOUvedXMoQbJdzLARn0PSxiTFhH54BOoSOEeCCKrqJotTlOaAjxB9cB6fIa+BFsBNcU4l0iFoDOsKRaAr5LEo/SU7FPcwFnGDW'
        b'Rk5rB+BvKbgbdsBbFLjmBg8zkXfDg/kCfjTjGpOLGl8thwsv+kUguSGNtxXuVRzvVQm7VAK75ha42DObr9tzwD5hhC0fDftALWtLBNgHSpl1CXClAO5C5VqJaVLXeSq4'
        b'mvtkiwYie/NxazIqC9AU8gYbnudDqRvwbejWHbBSMOpv6VYBaArIIqIeqgz6xq83qGqY+nO0YQ9oJrVVBDqdVGxQOayJQqlShg1GxWxwHZUN8+bLaOJcjnMU7cBCgrYT'
        b'HHNhg3pwGLQzdb0dzRmPqTjybTEvDGk8K3gwj523yZ4Rs/OwapEdqijHCMZP4zSwj+Oom4kaAOOXDdxKQXVh47gmBo9Az4ITLizUzPeBY+RxM6QCrqnwURMhxcKF9fC8'
        b'IQslqQqeJcVpMnctXiqRLpQYeYJe0ATPk0tyi2ahBoDzy4HlrOAAcApnhZS06apFAmbFVp5SiVwDD7CR+t615qG2YqoJrpvCqBhH1N6dOCmzFW3diNBm+C8gSoCCRzbD'
        b'HqTGg2Abo2aqAF6G7sJunDkUG9xi2cHDhuAIuMXISznYD6tl9Da8WIa9Nh/FVSvllsEmWE+mSAfw5hE8R0qHu0nZWILe5BfW+AyX52fBPeTJjVGLmLQ6sSjlucvhdjY4'
        b'B84ueUI869bCMnshdnnGtFMkizjxWjxUkuUcWJcynbCx4UUDBSGs4iuD8/bwClbhl9Bd+hpyqxyx8mUqWBflEJe/9Co3JVeNBStAWyppKfAyOOEmgBVRsCeIWTKbBk4z'
        b'XccRsEMNr+Gjzg/VznTU1lhLUP1cZgT2WH4ovoi0dJc8kvfj2JZUA88x3rVuFaK0dznBchvUTOBxlim4BI57apF8+6TqozTbRK6zZVMKJUjtHWTPAkfnEXmZ7xaFj9jE'
        b'YvNXOZGKaWwOSmx7tvxSEvNMqyV2o5pDdWkMuMKZhhR3B1EuBXCbnRD1UvxIpFWlalEPtMllA5HLItQVEXk9CW9uYBQ7mTMdTYLnkMT65hHVshKJWK9UNZLSUoaXl4HT'
        b'SCpAGWrJpMDq4YVA3OlGgW2uLIqdwnLgFTC10QfPbRKiulaC5evQL/IGTRUleJADTqSBa4xarvHIxp6QidNU2LQKnELzvTYmaafhTVgHKp2ki2+w1JaN59sHmPfWwSuL'
        b'VIrVlFCJmrFgzewA0JopXQheBq8L4V4HE3gZJUiLNdMRHGA0ZRuq3p1MfiLWoDtw/36Ow8q0RDLRR+Q7z37jOK+yimC/DnEqi8S5jQwALGELl1DMnWBFtD0/wgDcikba'
        b'm6zucilvP3nQFA0uMU2lD3aBshfWHsGlotmJusTfIDw1DU198UaN8vFeXR39X3ARlwzPKzqBLl1miFIakKtC7nNYg1pLNqzGbvq6OeCUg7RGV/vLo3eO6Vb1RA5oL4ku'
        b'XsAU6m5QCU4iqZA2tJCNSDm2GsNWpvXWwWZQiq9idX6YBfbagSpvRtTALhtUrORBok08OFtslbRAOVmP9Y2Dtxj/dkWoR5nMb+/BLJJ+j83wrCz9KC7Ythan/woHNMOr'
        b'BkRsWKiGqpFQw9qsSVzi6vIZsTkLGxRUSHfIgVdZHJStlnQ+yeESHmxRgRWycZBiYAjFjoc7YR95MA0NVlBXzo9koQe7WTHx4Di8qEZevB5WghM4g8qR0VhG0MNaQrgD'
        b'7OTAMnAcySu2s3jZB6nwUSJXrzdAum5VLrM5YedGa2EMvOiEhg9IQ8PDoEqO0ljOARWgKo0UrKM17grtHR1x+z/C8kP9W9Nq1GUQ+muXoYlKZDS4mYn0LZ9lAq6XkGEV'
        b'qNmgK0RqHZYrjWVHD1bLgevhPqgdXGCqpRyI4BkVB5IleRMkyJfYmvBqHnPKq84rBmtNuxgHW2wv2QZr4GU26usuww5m1LgDj8+ETrawMxzVuQJ3LuqGw9FY8iYRYRe4'
        b'B1yDXQ4xjEVlM+rKLrDQMLQFHpE2KA3ck436KyTOCt1RD7BbboYFl+kxr6NSOCV0jCzmIz2ARm5slPRzbFALj/GZbJbDU6BBOoqOmGaDtZwavMZBsRyahXUd05iugW14'
        b'I4b0mBc+5GUMykNBK7jOFOIRuCNK4Bi9qARp7RKW33rUX5HiaQInYAPqU6NQfPuZU2CoZ6oiomJjA65KqZ5sSjEWFQWmevJANV/vP7OSr/iLtwhxol/atjp3vFtCecaI'
        b't0F/SvseWeL3UZWiQzY5U3qGMsdueH0/ivWugZXYOlJiIKANBGItAWZBGj7QdxrQdxI7B0j0A2n9wGr5QR2D2hUPdOwHdOxbkiU6brSOWzVnUM+oUeWBnuOAnqPYyV+i'
        b'N5fWm1vNHdQzFOtFiOSaVR7w3Ad47p3JEp4vzfNFX/aH9CvhG0xEFs12Yj0H9BkvF4t1I1tyxI4RPXK0d4SYH1ktN2TKq1YdNLWqXydaSxylqQ5q8aqjRFrNphItF1rL'
        b'pZo1pKkzTClMtx40MKw3qw9uFEiPlGVJjFxpI9dOF9rIQ2LgSRt4VgcN8mZWR1RHDBkYnrBtsB3U03+gZzugZyvRs6f17Ec4bEMdzIXTqQ4alqfMLEQBzfLoZhPzYSqe'
        b'Pd1whITVoYMz+Wf9mvxOzmmeUx2FkiOKkmg5V0e9O9NKtPbspqZNJ7c0b5HM9KRneo6/PGhs9cDYYcDYoSXjwrLWZejdJ5QblEWezb4SPSdazwl/odigKNI+Mq1xGv5D'
        b'pUFFFNwcKbaY1ekptgjuSZXohdB6IYNGpvUKYr1AUcDZiKaIluzORRLHAIlFIG0RKL0ULL2U27lJ4hgksQimLYKH9I3F+nNFKSID9At7dps7TKnrG/Rn3FkOlg+aWdSn'
        b'io398CG7ztwBPl5/NjbpN7tjB+wGeRbNSi0pAzw3MW9Oj7yYF95vhQoqiGWCSgqFqKBMzMXG3qKk5vmdVgOW3uTZnoy+Zb3LBnlmZ+Wa5EYviS2DelLEltH9ayW8GJoX'
        b'g+Lxx9H4mwxroFga57dYDRg7i41iOzOurri0AiXAAlj0r33F/ra9xDOW9oxF1VcfJjZKa5GjbbzR7574vgW9C+6y3pR7Xe5uEh29WBK+hA5fIpmdRs9OGzFUD2MZPKFw'
        b'OGxC6RucUGtQE60Vbe3URvJuLWDJkpfSnPbAcvaA5eye5RLLCNoyQsKLpHmRwxy2dTBryNSycesDU68BU68eZYlpEG0aNMLl6KN4UTCsiKOVb5AfNDI+EdwQjMTSiDZz'
        b'lRi50UZug6NbDhSMTTrjr86/NH+QZyXm5bS4t/vRdnPQp36XO97A+27w/Sg6Kk2cniXOyEIhHZUtCcqhg3KG8O3LmNvnok/98XdSQerdpPuL6OhMcVauODsXhXT0UknI'
        b'MjpkGYk9ssXlglerV6d7tx/tFtyf2J/Zn0i7RUjsImm7SJxj+SZ5UVHzJtraV8Lzo3l+gxa2ImUxL3d0KQf/xCfT8Yvp+Bz0WeKUSzvljqgpeKKqQsEIVxXnHgXDBjj3'
        b'SIiluZ8Qu7eEN4vmzUJVbIyr2NiEtChce34trAvcVm5LdvtKiY0fbeM3osTFMaJgWBXHqNSghGOMaohC9S3mpaL71VrVkEwsvbS0J/tGPj0nVhwXL05IEscl0XOSJZ4p'
        b'tGeKxCaVtklFwme2hDVk54SLzHeYw+IvZrXoiPnRnQFXwy6F9QTfiKL9oiTu0bR7tJi/TByf8CA+ZSA+RZy6kE7NolOXSuKX0fHLvhsMCLyjA3SkkoXEaiEdvlASsIgO'
        b'WDSiIIdzhIIRjjxONwqQ+BqY1BuKNIexVLSYXbBptRk0NpMJtHFoZ25nQT9XbJRwNxQTgoOR7FmIpqGU8QI7Pbv9kUTZYYmyMxhZwZrlhJQQCkaoWSa6T3BQHTq8lkWZ'
        b'WiI1xNLGagiF9WzGWWNh44Yj/o3+LRkDhk5iQ6dBT+/u5Uj+6mNawlrChhxc6mMGrWyal3dOb15ZHzakZ0IaQcbZlU0rcRmHNYThWlNqUmoxb7eS8Fxongv+QrVJtSWh'
        b'PVXsENKjJuGF0rxQIlzhLa7t3uhXD6tPvle+p/DGeol3OO0dPlYmqAZNLMTGkS3BLYroV48WPStS7BE5TCkam6BKexC3YCBuwaCZZbN+S+6AmTuuL/Mesz67Xjvs0Tai'
        b'U2fAwktsEdgTKraI6s9F0uNrjqTH1xxLj/lZxSbFQQvLs8FNweQ8sGeomI9+ku66358l5i8Rz1sisUijLdLQY2b4MTPymCXNc0ZShFrggksL+ll35IBcfxIdkiyZm0LP'
        b'TZF4pNIeqSPTFOOxRsPh8AzKmEe0mAhpTndGn03vM+g1wCWj3KSMWph7q3unHO08V2IXQNsFSHiBNC8QvdUHi7oPFnVjkxMhDSGyB1zbZ9F2IXdd78+iBYtFyhLeEpq3'
        b'ZISjjAsNBaghmVuJDFs0xUYOYqOwTrOrNpdselxv+Epcw2jXsEEjE6ROxEaZqNhVelX6A+4Eg+C7M+iIdElwBh2cIfHOpL0z0V2NArwnCtUCs1grrchBSztRWkux2CIB'
        b'FbR1r3W/+W27204SnwTaJ0FskS9OSX2QsnAgZaF40RJ60VJ60QpJSj6dkj9WiCMcORdcuy4mw8o4Y6ENoTLVmdC8kLb0kPA8aZ7nIM+8WYXmuSF9h+qU1afUq4R0i9hi'
        b'aUth+0baKQB9Qt3NMrDsbuH9jXRshjgzR5yVg0I6NlcSupQOXTqEb1/O3B6EPqHmp/C6gjgugY5bSMdli3OWiXOXoZCOy5OEL6fDl5P4o1vWXFjXuq6zsHsj7RV2l3N3'
        b'xl0O7RUlcYqmnaKxuIQ2haIa8EUqV2LhT1v4D9o4ilC3mje6Xol/klPp5HQ6eRn6LHHLo93ykMabhfKPAqTxcEWpkopC+Y9siJTmf0LsvhILP9rCb0K5yVoFKjfTRgEa'
        b'iIiNchlxR0WRDbKRSPjSgmxJaA4dmiPxyaV9cnE9xoqNolEdyl+S71xztehSUU/gjViJVxTOlXM07RyNm254Q/ggz3GYUjEz73S56nnJEycmqilq0IZ/Qa5VbtDe4YKg'
        b'VTDo7HJV7pJcZ8pF1W5VlDQHR5Q0B0ckoQ6+D+xDBuxD+rMl9gLaXiC2X0waaMpAHFKHiyRxi+m4xUg1822RaubboobNtyV6e5XEZjZtMxs1GUsr1GIsrVCDsbQXW4Si'
        b'FKtdUutZKnEOpZ1DR7RV3FE5oACn0XNYh7KyPpvalNqSKrH0QEIzoq+GSwcFI+tYESxrpP9wOIJCfcMnJBwmIfPNyHSs9YZz0cTQ4IEGb0CDJ5qOxjnhTeGDWtp1YTVh'
        b'aOQXK9Gyp7Xs8RcRNRH1K+tXHiloLJBoOdJajrIvs0WLJCYuEi1XWstV9l2uaJPExE2i5U5ruePvImsi8QBMrkGuPqlxEW3sKBuhGTWq0nr8FvMWlxZzWs+hU6tbX6zn'
        b'M0wp65v0e/SUkA9jnaGIhUa3/Jbg9ijafnZPZs+ankzaPoA2D+zPGjCPEJun3F0mNs8QL8hAtWFphQVJWnctiUjxMnsUQ8QO8+9q3TeiI+ZLbBbQNgsGbezENgmdct2q'
        b'SP2gT2hMkAJS7oa8svj2YtSN4CpBwYiCAhZCBSyESriYUTCioKaNehYUjKhoWs54QqFghNKcrvkEB8MksKGmG1er1idKNMxoDTO8IVfXoG5DzQbsDnuiCzGlyWiGU09g'
        b'8Ka30R2AzHaEHzDrcOrpipE89pxOSacrxc5TkA6nDH43BGIJmwDfCQg0noP5hjExfDkUEGjAOdUXQOmFP1GEGJkYFB4SHZJI0OiE68iQ0kWjeHOc/8I9uCy1C8v+E/PK'
        b'yeoBm8LmTg0wt8V1Mglxl8J7MFvZTGWMcszl2GoaqHtEgSplnsAaNPYYNEPjHrthJa4FqgQcqDMXZg+azZz0Qgi5YDrxQi664DBo5sA8YYsv2I4+MemFSHTBirzcB11w'
        b'whecRi94THZhIRMVuuCILszFQkNCdcrIYVDHdVDHYTiP5aGnPkyhoCx8eBWLUtcZZhPI9YQAo6d19s5jLpkw2OpUsV2seN7CQUPTlsQezX4hGoiqR+H9xSh8QsKh0MjB'
        b'gJBhjq9aOAFV/1I4wh17dliOfL+BRWkZVXsPaliLNawHtYKHuWytUMw/1yI+6lFYFowmKEyCWnI6Q1uW9Gfd9RDHJ4mT54sXLBZHLhGHpA0aGLe49czsyeq36F8vnhU3'
        b'aOyGIlL3QPGoezzBAdJOoSxUjhGxw5wwtprBMPXvhiMKY3GTbxPkAjlqFsPU7xkym5Dwrk0OPJFAwN8MiUpJejZtJjztwKb8FsjDihJYO2Erqor099eLMP9b8xf435xs'
        b'RelnpXGfldFnlWxV8lkNfVaXfj9t3GcpC7xRaZTzrTUl55szjvOtPQlv22yU820wBefbcCeVbdRu/D/lfLebnEEquU1+wlvNRynfarncbNNf5HvzJvC9l/FnPpxG3CXk'
        b'FeZkFQXnZOYVPXV6Ce497uq/Qfb2Ztiqrnz2Q7mg2ISQh5xA18BCZ6yFXXHgzvn1iG1vBg7o+pu43NKHvH87e1v2OsIidMHs7cLZzH4/TMkunINR2coJIdGxSSGEuW3x'
        b'Au86MTg4IWfNRAKqc+FcnOFfc6vLKJhalpCnelPFOkqrnphmvtKEOHA9FCrLjUNeywqnUBV9W6iCL031DpfCKJzr/2tA1Wzq5Y3t3BjGo9h+eJmcHpyW7V3IpYjXNbAH'
        b'djL7n5ttwEkV7+S1a1iMG6hGcBlezWPZenGF2GnL/I59R2MtXvc+dvKgWSVLPkGv68jcoumJyonOFVHOnKUG1NF+7l/7TPgsZi2yRgGcIacFt4Hzo8cFc+xexl0zFGq9'
        b'F1reRMw1j2KOimV7v3A4ilfvwfgh0uD9T9jXU751hsJ48HWG9x8Bvi6Mw3LGRsn8FC9n/V8HtsZcKDP5Xwu2zialjsm9mGnye1KtZS3+F6jWMo3xi3d4/2qq9UQlNBXV'
        b'eipd9jOY6Un10uT3/waq9Iv0Kga0krEKM1IwhGoKpNLoY5P53HyJRD2hnqX0adwfMkRp1CfaTk0/+iXssywlvwX8nJf7X+bz/zvMZ1mLmwR5jP/9GvLyxEb7K8nLkzbg'
        b'/3KXfyfuMjcmiRBLwPlg2Cjj+8K9AnASVI8j/MIauC+KIYKEj+01AX1wjwo87WWf19CWzhamoXheWfLG0dc9jp3ceYCl7qPvM+uwi4tze+72cvu5NSEJd+h7f7v31r13'
        b'fky4N3DvvXu9e41bdhhb3blbDQbvTX9zZ9zRV1WzdL+uW20eFZGxQN59s8c7u61e09qdLv+GDjWjSuPPtmV8LrNxpW01OG8HGhQcx1ABmqCS2Yd0ClSvGAPtSjG7oBSc'
        b'x6hdm2yyhUMA6uClCduQNeAhArN1hBeYbUVXwUGwxxaewZsJmI0Es1XJLohA2ABvjAM8OIGzmjJW7hnUTfwPjDd4xDEpY/blUdN4wGweM1b7ZvUsarpOdYGoSKJhT2vY'
        b'P9DwGNDw6FzaU9Sfcjd50DOg3/OuN8bLJhO8bDLByyazyBJKtVyt2qCuSe1G/F046yX4Kv6SufTHoVenzLSewiTc1ZXe/3u5q4WZnBdmMb+MWy3MZnwSTYpafaloZJzV'
        b'QFQ04zir5lOMB15iq8r//PHwLIVxaVeZMC7mThwXo1GxknRczJYyU9UwMzVXhYyLFSYZFyuScbHCS+NixZfGvgpbFKXj4kmvTRgXb55sXPzzvNTxZoj/J2CpE52YSAeb'
        b'UoLoStQ9Y5Tjf/mp/+Wn8v7LT/0vP/WX+an2Uw5J81F/wswTZRXxG3CqP6My/kic6h8OAZ3B+LLjwO1QhL2ZwO2bRymgbV6MOxMfPJI9Cm7C08zhi8RwWB7rkCLFK0bC'
        b'ffhUnCAVe/xQ5MNOAkwANaBSCfRaw2pyCh/0xVoxfE9fxRc9nsB2WE7OcZtsThOqSYmi62Ep7AAH4KliT3RFEdaArtHN8VK/I/sE+bD0BbcjbHxm+4QSvAFugKpiJ/Ro'
        b'diC4MUYuhGXh9gzKA5ZFo6kFOXiUZq0ITkNRAErIOfIMOBsFDwhemHBgEqM9rML7y3fL45NkCSoKKOsVcCeBSGrFLIGVKEqwA3bhaJPjUh1SUjFRMjI6CpxLCgcd4dGO'
        b'DhHRKCInNrik4goqExIpE9Conu8JROS4+kawH/QJXQtRERRQ8KQZuOrDL3YlxZcKTpDoBRGgCbbKoseQxNWuhZiMSEClclQ6qFQAh0xZxY7oMYMY3UTZbdLaSoKN4CLz'
        b'yGj+F+YqgNOsrYR5EREHTqsUqquxp6VSnOms2fNBF2ND7sDn8Lrg1XVCDujKo9iwj2UXA3YSEIKPF3eLHwuNpeemR1Voe1J5hie60HgRDRi/4ZYcqpmtApw1djvlRfc5'
        b'xGwfMv/J/EeVI4/NO7zDjbXqPnM8f6z3SeyGLRbRy7mzFf+88ebGLy3vefSyFPaKg86+Tzl0pGppvu5bG+t6iH29acOzrMi/+hTszq55e3HY3HjfoMtqHSlt5u9y5e/k'
        b'LUtoO3vsSJFgMGhO0IWvrcOOWs+6ujGkTzfEc2DLvHsbum5s2XzP9WTSLXftY9vO/mtxyvV6vaTnBxcYJvYdh3STnPvspMdzNRVumAtCI4+lnHld90PPt5qHvxh4FPZ8'
        b'uHLOgWkaH5iWlf/rbs6lnMJNH37yF6+OZ+/eyDpZWf5jw2MteTb35tt6HFWJU0mQF/144YKg1dc4/8yN1akY5muQPeRWsCbrhfNH4Jp1PtgBtpPrJbGwcwwx6Az2y9yp'
        b'hC9jDh1UgUZYKohl8IJ4L3rAUumpMh/QbCJDAIIDpmj6yCAAwZG5ZIpoAcpg2/gpInshl5khwl1gF7NR/haKvV4qX/bzQDUSCpVVbHjUBjRJD/EZa43OPUEdqHUBvYlk'
        b'H3v8ckrWumCDLTlPx4bnt8LTzOGpFhtYh8/6TnLO98waeMHeisyArdAE9wKTB9zIy9F71OF1DiyfHaWsQibZSaAtHlbiwzqxoJuSm8MCbeAK6Cbnyaw3zxa4RmK1cYEy'
        b'QJm9mgBayWLEBqQL9jMHL+EeE+lahDO4yJxmuQrOuttFoiapCPbhekFp17TmwKPwDNxN3skDffCKnaODFtwxOrEPAFcY/zLbLNSnZgD6Bzs56/HVf6fdFNjdJW8CeW8c'
        b'2sr0xUnYZMi9Xsb5y3Cw77+H3MOsNtO6rTVbJbo2tC4Gmk0PYabpQRKDYNogWKwVPKRpMkq/8+z2788ZcBOI3QTkrkCJQRBtECTWChpWpQzNG52qFQhPjjXdn1yfLTGY'
        b'QxvMEWvNGdQ0qPUlF0Rezb6dFt32tGvgwMxA8cxAcoBg3J26Jg90rQd0rSW6fFqXj5/JZA4ZxIuTFtJJ6RLrdIlBBm2QIdbKINGKNW2lVgaOdipLVNRc0hkyYD1LbD3r'
        b'XRNbsV3IXYX7qhK7JIlJMm2SLNZLHjS2aFyI+XCprJak9vk9lgMO/mIHf3Jz6F3d+0YSu2SJSQptkiLWSxkyNKcN7cWGXp06YsOAHs9qxSHDmfWzRWuqFT/SNapPa8mW'
        b'6LrRum4PdIMGdIP6w+6miJMXiZdkDgbHiuPnixdmjXBYejnYNoJCnJmc8cYO9V9DUfvl3VJEpCYC036DSIVgy0cHNWb5QJIV5sNiRRCDxe8d/ufMH/+bQGi5fPbTxb8I'
        b'QpvMNvC7UdDMpRS0G6hT2vPLGLRxSm8FvDlKQYPNboSCNsfFbpSBNm2dM+ikMoNmc1Qoc9jOgTvBzkAy4InbGiVcm2g3hmlWBB1kVdoLlG7FZDNw0VlKNoM34CEy2Ljv'
        b'zqHQOCdElUrPD1npQRWTo8OlzrDHDaW9cwxhBvrAOdhA3pOLXnkJE8wWg2rKiXJCOv4MuaAEL9oJ17B8wF4MaMAHwpp1GBrTQXgA7LbbAPaMMsxKF8IeMk419QAVMniZ'
        b'7hx5HbaqITjBPNUMTsF6DC+DJ1ahPzG7zABckRLRwI3NiYqwZQxgBtvj4HaSjihQaqACd7vLYGO2i+EBgqpGnTHsIUCxhaB0PFMMduOzfqRE/sraTxmxBpPlnNNXxbuE'
        b'MzCsI1HmVDClMVeZSg8s99JkvuxbHU5VU3MXqaen2w4Zh/wxSLFlvxkfZfuiBpqaHdWLbY37OFJbI8lkXboapUe1hE6LS1c1cZfC1Pbb6VL21Lal6rz0RSO8eVQx6cVP'
        b'oVnGFcIGA8dh/Qt8MHyq8DqRxsAMcEYF9CKpkYHAfMEhexLvG8YKFJJEa2Veur2+gSbFZ5FhdHAqOCaMycjFYz18Dn0BvPyHlPXO/2RZc1CGC/fLypqUzEJwGFxX0YRl'
        b'o/gtb2uwn8HxdS/zUinkWK3EpAYKHIF7lBiSWQ0hv3epBk6DV2ToLV4CeQYe04FHsWkX7qLiqXg0GKsjdK1cP3ByjL0VyQalsGcB2AYryNX1bqgxyNhbKkDEBTtY8HAW'
        b'bMurLAiXE26Qo6irLk9vzpsvNAzReG9xXvH6VDvTipXfa1l439YLzI8RDq7Zey9A3fn9vbMUOCuyrmVXKCz/1y5XbtOzoTqtaTfyk1ufNPk9+nvPd07dO9fd6Hp8/F2P'
        b'kEWnC9vO9l3YGOr7l79//uM7BW+caDjpoXD00OHzeSu/e/bD1dSf4gcbXisqeaJ7c/6aV73+Lq72z72rFyvYdi/Y2efBZ8lKdQFr/qb4RvqZutKSQ/MdXWu4Bf7OuZz9'
        b'fj/tgd+8ZnTbOyFF888NdRfvt1dcDE85eHTJqo8z/zIi1NP87uv6Pu6JK9vdGiV/8rBre5ix5oO7f/r6RlrZx18r+0EV/7r+16mmeir+w/lLPje/5Pfxt9OFFxX79n1f'
        b'8p7D+25yO3eYzTtpfX5vbnvPj6XvOs9bk7p0s2vNZ1dSTFnPqIY72/96L6RtRn2AVhZ8+iSdt0GxQzxit/O56utLako2XlI9m7HjG/1XjmxYH+bi96ww2Uiy+BR3yFTF'
        b'75tZ6fqx84/NbWtd8UrMqsp3VfM1gzsOln4RmzH9fvn8HXlNTw3if9Qs/WJOxOrdWW/Ip/yo6P3mSaH48dczHvFLj7DuR+Ubmx/Pa3/WFnAsZXbJG4KS41V/nvkPs9g+'
        b'19g9XwXa/z2/rGDbI875pZnXbvuErfj088d/PxZ9TO1LXYvbi9I7Qt/M+kR5pUR/gVjysKktwOHNpsvePwl3Ps/M/+LNDy7P3HhBeVOd4q2S7ZYLnrPjP1apN+19ZL73'
        b'Znj6EvPlAY9e2z1v10/7Piq4vnHGnT+V/nXeowVZBv+8NeNoarr5/cRtW77p/uTY19uWBEtuf/XmGzZven9z74nB697vaH67oaGi/7n8+7Eebnk331NtP/7wsOIbOfcv'
        b'fLnjnwcbMxcHnOheuen+Zx+UxKU+eq19afET16vv/Gm9heHfHj9aNe/9+o1DX+df6E7MHfb3M8/rmfHVzOS/Kr/fF/hdqot/9haVC4YaK+T+8UW/PFd7c8zpy/KXb1kV'
        b'/2i565/fb6XnFsWkls9arJL/rc9j7bMfQsnxgyPy8d/77nxuFQ8dDnxxpfPLarcSL+6fNpYWR3Z0VTWZP77GXXfxSs/+kN7qj26ZDi7+Yp1uVjOdqNfxefH7f6vsWu/0'
        b'ly9Kt7J+UAhOubHnZP4+7fNf6L8j+kGpSvAwtkZkKvT/vvpuUmXHibjehKjA03YZM2wW+81Z8mlkj1yk7n7/mwOHvvvp1MCrD44k9f71x+07vTsGflRss+wYOGQb0Vyk'
        b'/ebgndLkPrnv55g9bnn1LbP1ma5bbf9Z/EbvxuA53V27JC4/FHJefXtfmPO/9A98LQTPue8/d43+Ij/qmqPnyOGCRVVtqdue27kXmj+q+qfH7n9cSThV2/u9XsXex5FK'
        b'195+ZfNBReutXUNHd+3/VMSf9ki9UmHr14195WvcNC9tqdy37bkvnbam704XC7yqIVqmkPSVgXbBXddP3nZ8/O48nX3vmeemBv2Y9/f2xnfsA47ueTOp7KH65ye68zue'
        b'ch7f9tlieMMYWKb7Xxz8cGRff3qiSHT2L/8q7Fn4dsIbpuwVDyILr7OTl8CRimN18V/IfaQmMEksUr/ZdSnonb1fKq566jsv+p+avee1vZ6znhRYpi76lF9AJoxIQ3Us'
        b'e2EmnAl3jEGvyucxDJQbsMJ6HPQKXGbDK4vXgv0WZDK/JRLWTkBeoc5rF8HWozl8DXMwvh5N5hsw9QrugDXjyVdLXdG0HA8qdEHLpomwKtS5NVE6mFZVA3aSib17EGwe'
        b'pVXBS6BJHlSxHZxANTE6mLrpYFYVrNKagKuaCzuFT/g4G7fgFTcprIof6YjGUjvXRGCsjYxX5Qt2yoOuLcsZXM8pQ/4osAoe5cmnsW1LQCW5tnoFaBrlUkVFyoP9bMsQ'
        b'eJwprFJYC7aPcalAGztKpQReBl0MYaBjhuJ4LBXsZsMDYbHBcD/DjtoHLyaT62fBzYlsKjTY7IG7iOXFDFybDit9Q2VwKnAOldUJYl9Is04Zx6VSZgNRRio4Ca8z1XAC'
        b'7redAKZSoKy3EC6VDTxH0mcE9oFTMi4V2AUuceFNNgd0oxogForTSatGyVTo/3aGTsUGp+GeWQz8oR7szpGiqWYhyWHoVNhjUgW8yeCtekGpBU4kaCycwKfSRAJ5jhTw'
        b'+lVR4/hS6mxz2LQQdGgStEFMCdgujGHBxgimE2/Z6sVkrtR160S8FJdKgZcJX2pVKkM/uOgPz9npwLYx8BUGWhiSi0bgZLFKjIMqEhVTUMUFp1jwPDgOdjBgqh6wB/QQ'
        b'+Iw5ODKBP5MNd7ozhqUaK9CJ6VXHYfuLBCtwBhyDDFIFNICjBZhf1YXKb4xh5Q/bIkg068Bu2ErwVXiOA8v5sFxoac5nUSZycuAi6ABHSDRLkXy0YVLVHpvxsCo/0CdP'
        b'isMBlf0FVAyoZg5NoFUVgEuggZTyDDSYvCIEV5zGACdVsGwDKeX14OJMQmWaY0exMKtqrjmRj42wGtbKrGucOJlxDdTPJYXIVQPbUVUfgkfGUFVNuWAXeVaXgntkoCqU'
        b'oB0MrIqjvWyBFCaFirtOiqoKhBcZWhUbXIeVAsbgeFEubpRU5cKeBupAva4ZU7N98IzNOEpVHjs9Pw9W5JGimr/BBjOq4L6M8ZiqTHAVNpOHQ2EtbJRCqmLgbi44y4In'
        b'psNyonPU4XV4boxRJdjMhfUsJFY+zHu7AmG5YD08PEapAr2q8BhJb4I/2C0sWT1GqcJUmhoSay7cA64wkCqwR45wqtjwLLyeQq6uhRVAJIzhgyrHMbyMEizLYBhjZaAj'
        b'E6sF2LEae4KhwPm1QERqNN0mFXYVw51jtCpDsB9UMZrnIqx3RBJ8EtaP0arAUXje4Anea2EFzpYIYxyWyWYHCkx9K2CErMDRIQl2jTcU56erkheu5PgyDBwfDsHnsEEr'
        b'uAJ7Gack5fAa3PUSpgrV2gFKi3Cq7FIY5MkF0I73glfxYf3ql2BVtkt8SKE4eywZw1R5wBvcFMypaoYVDP/oxiZ4TYC+KHOT+nbxgleZ4rpWEjjKqUK6X246a0nBEoZh'
        b'dRO1y150EXalFo1iqppBB7kahJ3TdCF9vmuMVAWOK8EqIlRL4G6cORmpChxkgw54dhaaGncxWq7LphgVTeYmvjJqLHhl4zJKtx7slLNTQ/JBupgbW7zGzyCWgm0LdMBR'
        b'xrrdqboYo9J3w+3S3VVQ5Mmool2pcJuKLE5wRoDFUhnUsFEhHgB1zJb304WgR4XQd+QosCdGXodtDq4hzaFHpGt3iJSSBS/bEFAWZxoozWNir0E9nxB1j6hrVGIwWXLa'
        b'SD8b+8qBA8qUtIuziBtlZFnCai44ihoMuAIukx7ABV4AolFKljE4z4CykDTC7d5MQz4KLjgQ1NMJjSgGkqUFzzKycDwRvX8iJcsOHqc0CSYLHpnJlM5+noFgLjggI2WB'
        b'U65SFzrgMtyVQV6+SXk81MpSP4pBAF3ejJT0OKQV4VkZg0OGqHfCRCsXrZQxoBXYASv5ES8SrcD1dFIOxrB81lhRUZShiQbczinygLdIVjxACx9LrAAcVucrwQp+hLTT'
        b'1welcmFgxxYGwLcPVsiR2/ikPBVgIxucWh8A9kSTl2SBGuzRPgreUB/PsIrWzmAAVnsDZ8kWSfTcR9dI4HYiYUawF+m2SjtdpqDwEgWS6CMk4pmWjkL0ylgkSvvtkK7V'
        b'DdIo4WxC09t2IiWe8BjoscOgoP0CbN2BR9jq/I2bFEkphs7gCrHfuXI8dsSZYlEbUqdrczbDxqAnLjhXnUjuXmJ5jSdhwV0+ozCvvfACkRzDBPtxMCw2GinABikNqyaK'
        b'UWJNKJZKBowHTzsRNh4bi2kq06B3o16lQoiKc/cogxHsW4/6H9IqjqoYoUdBOWwfYwAqBq+TulACZ0ztZMl0W/sSsssCHiUNWx92549DjrEpeCWOQY6BTlhGGhG8yvGT'
        b'cegYXpd6mozYZQkPkjbgtWmDSgpsHGV2gRaUgm6pWlqnOR7ZhZq/azxogJcYrXFkJaxVkQMnRqld4HgobCQvzvGANycgu8Bh1Ha0GGZXlzPp2UFnoZIKn1oJ6ikWhnYl'
        b'owThOo0FTabjqF1yVBCsINAueESdvHgtuLwedlmWjGK7QBM8gsatpEFeBrdSVCJBz4JoKbXrBNxDJhmhSATrhVERaNR37GV2lw/SvSdIeVgagHoptgs0zpc3YWvCJlQe'
        b'pM0eQUq4bTy46zIbuxY8DLfbMlLRCiuVx6hdGJ0piglHIzZGlDXgAeVRahdsYnE3s+AhfaRwcHWus0fiNwHZBXrtKR2M7ALnl5KM2+loMMAuM9DKMLvYoDZtNinxmWBv'
        b'OAPrgrtg73hg1yw0vGM6e1BujAZulWA7uDaO1xUaZs8U3U5QB/sEjtjTZTRD6/KwYLJVla83xuPCMK5Ds0Ap2ANv8LX/OAIXTuNEs/14/BZzmF1ncoMdWej7UVl6dCnJ'
        b'73cFbxmK9XxfRmxVc4flKZ7ZfxidZTegZyfRc6D1HH4OnbWZhdFZOJwSnTXV178SmaV1RL1R/XdHZklfJ2VtiOLPJjUltVidXNS8iCkdfEHQIGhhEWRDUvv8c9Pap0mM'
        b'vGkjbylaRxTaHCsxcqeN3H8buOoFHpJ6g7pobfPWB9b+A9b+/coSawFtLZDoRdF6UTiN/8VP/f8eP6WO041bgo5Ez4bWs8FiodagNq5gpOSkcYyRpPZFtMNsic0c2mYO'
        b'/k6pVQkzY8JawzpDz8W2x6Kiw+gXFIxwuRgrgoIRziRYEY4KTgYKRuJZ7phd5Y7ZVe6YXeVO2FX5DLsqkLCrAv99dtWqplW/jV01wuXgxKJgWPH3YTtFNkSKCptLaOuA'
        b'/sLbJXTY/PpIidEC2miBVCng2NSa1HCRhzeFo+QspB3m0g4hEotQ2iIUfy1oEnSyu1Vo5yDaOfKBc+KAc6I4aYnEOY12TpNYpNMW6bK7FCQW3rSF94gCF5c9F5e9As4O'
        b'CoY1KGPTX8OGMjZtXNiYJjb26gzqVBimuCjX8X3ze+dLy2vIzqHdt90fCazlIpYoV1TQyRVbJva49Hn1evW73va97S/xTaR9E8WWK8Wp8x6kLhpIXSRenEYvXkYvzpek'
        b'rqRTV343ODfgjjyQ719zpwgU3Y2WhC2gwxb8H/a+OyCqK+37zgxDr4LSex2GGcrQe5eOFEFAQQREBEQYUOxdUSzYR0QdEHVQ1BFQUYmy57AbkpjNjLkbJ26y0fTNJgYT'
        b'0zbtO+fcAUHNvuub/d73++OL5My99/TneU655z7P71FGF9HRRYj+uOkc3HRuJGo6CtBY+/9QUv8fSuo/DSVVwArFSFKhGEgqFONIhWIYqVCMIoUDEzz9jCX9vwoi9f+x'
        b'o14EO+o3ttstWpOBo9LD/7eBozB+QIOphho4ioOBo37CGgBm/xOoT2KswvI8wCeGjr9iOj6NwPIAI2/N+y/Bnrx+C+zJ67fAnp4bsZCJEKhsE6ZiOiVNqUOAIwT/MgID'
        b'N/lg4KYsFg8DN/EIcFMeA9zEMXAco6YEE8BN+IHuOE5S5LDzvwHb5EqAmf7rcCpsE3meMRW2KRjDNoVi1KZQDNoU+t/BbMLtzCbtzCZ1ZbPuJySrwtB6HmWAVRVfLMRt'
        b'Hi9nTIM8j2XXsDGu0n8yZDRV8Amhw2pAfDk2wu1eKYnwarqwPjkd7vBiUR7gFrc2btoUBTlD9e/X0UhCD05/GpmpUIPgGekcMF3IxuEBQ/W1mfpXl/mt4izk9HKmYiGV'
        b'uxKzRGyUiI0U9VsMWgxbjFumtZgt1C/XeAbbiMumKjTLuZupcs1eradQlbRInDaK03kmTpvE6aI4vWfidEicPoozeCZOl8QZojijZ+L0SJwxijN5Jk6fxE1DcabPxBmQ'
        b'ODMUN/2ZOEMSNwPFmT8TZ0TiLFCc5TNxxiTOCsVZPxNnQuJsUJztM3HTSJwdirN/Js6UxDmgOMdn4sxauAtZ5U6btQunkytndDWjhUK85CBOarZot+ghThohTpoQTrqg'
        b'ePNyNtHJcrunHxeTnhuvVtl8cIX9lFkotsuanIIBoJqwKmqsc1ha2iBm0gT4eTG/ImyfRK78pxQ2rhkqFjrETDJ4VNvvEbAJtZUgim2saMAQGA51yyoa0N1Ug8VJSr9i'
        b'L4eK0rJFDg0VSxsqxBVLJhUxyaISG/ZOKeG3TJam6qdOucmow5ZqyQtR74jy6/KKhgoHcdOC2ipie1W1ZBKGBzEGQ9Gl6P/GRQ0VUyuvrWhcVFdOYA1Qm+tqllUQTdom'
        b'vH7XrMBGZZM7KHRIqCL2WR4xPLW5cs1UqzVs3KW2e2QY4a3mwzjFvRw8YnnjyUodxBXY/q6x4l8xCfPQI46HgT9KJ9k4qq0L6xqqKquWlNZgBAo1SCIiAUbXeKqjYnFp'
        b'JcEeqcAoLjXY1JfpvUN5xVK0YRE71DENJ4aKHuq4WCxhtXXiqfZqZXW1tdgsm8jeU0aRGTz2PU5zbc09zbLS2sYA/zLOU5MmUWo8gIKD+oxN9mGKDA8tNNmxiU02M+EZ'
        b'oaFj3MJaaEiUrDlsavtT1tRrNIiSNecZJWuNZxSpOWs11ErWz42bYpH9T9a/gVQ0ZSj+tnHdb9lbIvowppZz0tPUtoJ4cJSScp9wHvGY2NOigf18I1yPCkYgf2vU/wsE'
        b'HcKcUAyEUlaK5o35qEnzGZtHprCJQiYLb+mS55srl5dXMRay6nqnCC8W8/qmCvUEIG5CI3NiAno+csgUO+Lli6pQDjx+S5sa62pLG6vKiLjXVjRUqu0p/wUGSQMa10vr'
        b'lpRjCjOzwpQR/a+V4Cd0cCcpwdtliPHHsQPO9/uV3/F5Zxt5Ppav8K608t7q2yCmqtZon3qk3lNgLac54HIY6Id74VXsDayRN4cFt/PAFdDKg4dAH2BygFNpK8nZfy7x'
        b'Lls1HbSAc1yKWkuB86BlbVEV0SOe5sp2G+QQp9xpZ3UaKZJWD/aB46AfrRZhFOi1DFu6sub7X3/9dbspd8kDxtyuRidzGUUcT8MdYBPYRzyOwwMiHzbFTQXXQ1izwEG4'
        b'jccm6s7wJccSMdxhCLcvx5pZi1ME+MucjqcHi/KDBzT5y2Evo4V7WHcJvApv6eEYdjoryGsaKgHry7ADwalJJQh0ccCinEJnAynXCVwCUkbVfS/cDK/qCcN1SDQHXmeB'
        b'HjtwCZXihaJDwEkDeAmcnVxSQ7JnfQYPXuInpwqxflgelGjbQHkYUfCFHbkmcCvog/3j0doB7CXgJnrRacLfdecBOTiVmgF3CuBeEewP9AlgU/pr2NVB4ABjHXAQXBOM'
        b'x+eCVp8ATUp/LbsmoKqJsaDrhFvGo8F1jk8Ai9Jfx64F182bPCniZ+rQGtjK2E8m4XRZSZMdNcbDgzONtMzB7miisg8koGcB4z0nSwCv1BWSL3CmYDcHnMgAO5tmYtmr'
        b'Bz2TbSw8iJbeLHARDKGi01JTBez6CHDMBr4EdkyHfbAv1QzsSNXTxUAxKdk5VMVC4yB4K4WIDjudq/+R2vrSxHYV1VSEHuqnZDynfGzD6p0y2wNuT4I7c7DVaOpsKEfC'
        b'uwW0YgFG4kssPDKTudNcdeEWcIrLhdcSXEEPj0pYbgaPgX7QgohOdD1eErtgxfnuhKUNSEzgIMuNB48SA4mVSHra9bTBdm7DMsR+DZYnC5xnDCROgU4z2K+vB2/Wk1y9'
        b'LBfYvYbEceEBeEy8NBpT6YIGdqw+H3SBXYzS+EUk20fE9dElsE8f51vPcjEFF9Qet9NjwDYxvALbQCspFQyxZkT5MaLYA8+5owqBDGyeqBF0z2NcOh+rF4/zPQUOjPNd'
        b'a3lTEK5zn54LjmU4D1vSBSmZs5PUyX0C1DQF62E/BU9wwmv0UB3nwFXytuEF5PD4M5kpynlViZYGPFAewMj1LX2wQeSRo+YOEgsdFuJ4R3lVs30CW8xCi2tF6Y+X84qq'
        b'TWPMjr+b3netZn/NnbntZ3cdzhsq8r6cnfCHX1gmj//42aZNf+Qd2Be/10/vj1d5MSfi5borXk21/3nT8d6Hbx95O/kqd96cYNHXx75cLf7z22//UPhLYo3TZ13OZ8uO'
        b'tsU1/xr+0pVFu1r+3jnjckLl59S97R9/G/bX8z3N2xbua24pNLFtn31Sc7Opcm1tQlmGxYVdNguaFy3R/zTusfShTfKj0Wq7LSrOgsoFRzsjXm2X/GnMLuPr1xO+Lc4v'
        b'bdjVvuOsWx3Yqj8QHxEa91pUx/D7b3mcuFBxrKZmaPNt7rL7S90H/GKWzdrzqGNsZ94j9x1/7uLpXp19bM3hv351c89u40//sfIb8Yy3LxiWGBRmL/RcPJI54/HmbXbC'
        b'5W+n+S/4aJSdPn3n/v2rNs7etWid7vVD8V9+b3X6+Aj1QU153JmgmArn7dnLNSPTcx/05U279eYs5zc933gYezipsJz7BW9VbM6rCS8bn1+lf2sF7Oh9kHt265uLjsVU'
        b'P4hfnKY/72R7f8/iP3c2/W10qePBUuWnV83eprco/yjh3qTfiDn+SfrbBrpD83vTpn+c4/eGz9dFD3iqc/rHu+bG/jySf7DycJfJokL9HYqr/UOjwpn993oK/vqqRfM/'
        b'Qr9cmjwQVai/3KYv5VLuT8LVr9V9HhwFvSy8w7V+uO60Iujy7ZKEfxT6Gf3zV+7gheq5XOe7u8rq391Zk/5mQ3mM2y0t1+IFV5d+EVi4XN93YVTb3+w8jrJO3HilacWh'
        b'wPdbdCr4+16OiOv4OK/l4Wz4mUP7jGXVpdy8BcKtlv/w3hbCvzS7fOjEh1sfHjA5lzySNXtDVPTa5uiDEfp/+yDRfXb1otmw5txL3bsz5m5/K+rsSPuHe4t14stc30LZ'
        b'f/7Wnr/BtztFunX5fiUn/seXSqSflfoHvme5qOi8RofFhoHQMycsHqyhzQO+WHbH+JdP924veemHz3/86y8lW7dKVlWf81oz8/ujb930Xv3pNvMNWqN+3+VyN7z80v6H'
        b'Pbekn/c4V3403PW13wcbvhHtD14TMTY8xP5nfXmm27Y3eCsS3epKvw6687nN3a15vBhGjUnqDVrQRNzOF6az0QiXsVJB6wyiFhDC8kez10U8t2GV5B1stG52gANYM6HX'
        b'CRwlihhLwYWkGkN+cpoWytvCirCGtxidwp75M5745HVqwDrO8Cq4zugSbDJDo7HVm9Fg1QSDovlsJ7SuH2R03baZAoxStt07E1sHl+atZXtyFz7GdvfwODyuA06EoLxY'
        b'NzZNCLZnEjVf0OKd5OVJQM20qBK0NzgfDHYwCpm3sFvDcV/FC0smdLbh3mZGFeVaJcQ20slwl0CT0lwAbhaznWcxekugGw42pWYKkr2wJo8e7BaCATYcWgXOkLIXl8PB'
        b'CaVx2L2WcZXsoFEMricTXSBPRJ0nFuLHSomRNgMidryWUY/YhnJuyQG3pmh+JMFbDkz0LngYdj3x1uZYidU+wAXUALweJIGtFD85OwScRxsKjUoW3ArPxhCANP3FcD1o'
        b'hSfnErfKTzy5WcEOjfpCuJlkF64tqAFX1T5DsQomWq83EUWiMrAHtCMqp6SnCrDyRoY6uwuqvAf0cMNAnzGpp2AB6AmAV8RwVzLmSKphhgAOpLIpu0QNcApurWAUro9n'
        b'GmGt5j06KLYfykgKgwQ2vKYNbhBRa2Y5mUNcYYbAK31SfQ6+GvBUUhKhRXYq7J3kc84AdGIVFiQSpxgFm1PwJtohtGYKU9K94MCK5HQWZbiIEwywMT7RqrsB9sM+Zv8A'
        b'L5mUMirbARwtdwZiNwWujyDqXjtTYasWpVmcqsPWBxdWElIJ7OFRcRo45441rjjVrNXgHNzBsEiGdqrnYH8jPObzRGMVroeMijOK7MH+9rzh8fJJGphgMzhEsnPywXri'
        b'apOos3LBIHaDyILXG5YTG/wQrTw9YWx6KtFWOssCJyLhZaJhXQKPlk9RSwU73BkHqkQrFV73U2vZ7woDJxqx7uiEbuhutd/sXXA/2PPE++kiMGTCKgYH5pNhYVJai2iJ'
        b'hGA/GmeaqPKjLJRRhxnce0TwJdylzWVwDx+3rJ8FzmTMYiYUNEIuwGuIHYybYKx3Hb6CqfF4Jtgwbh/Bpbj1JfA6mwXaDQmJXWF3tCO4Js4Y195F+9JNRL0phrsK8/UJ'
        b'ysO0VHAIXODAVnAI7mVE7CS4Aq8VVxOsh3FHn+1ssB2eh7uIJmPg/Lnw1PzfwEy46AdOMFNTLziMqNfPL4Q31CrPl1nggosTo+fYFpeP4sg7CdppoV2dJmVYzknQAhse'
        b'C1B8daUr6AwGrcuXwQGD+ifbRAxP6A13J6ULUIacBG1D0AUPqn3Mwqu1eVZivi7asPNYlNYatj96fWHsLEAb6EWjZY+lmN/ASL1WBdsPbILHydgrAtvRTIjV5sGuTD7a'
        b'4nZjgwguNR2e1TCphYze1krYngEOxOrh4pkiwFl2RDg8xAyaQdi/dLwMeAvu84bbtSjDDE60oyPDzSHQzkcjp0Wcgu1EWPAqy9hA8zH+/JDm4iq2I44zsQbefDQcMIlW'
        b'r3KcooBnnA73EgW8IR1Gc+8qZzUcMmKca2PLB1tHIuhoqqqJAkfERNkVO3iFkmgi6KVw/xrUQlR9MhqZZGLwToK7OJQzPG3ozg1aGUnqdXRKE2fw1LYwqSzKGNG8zZaT'
        b'pQmOk/JjLdC7zI4MxmM29pZdDDuJoIeDC2jHzXMEVwl5OGALayU4t44Z23I0dDv4KYJUgScY1MtAU4pRJae0ANwis2Q52oyemNI2DDSyPawKW0zwirngaJjlY/xiBrsq'
        b'4OYEMPB8ycgMRPvjMHBBMwN7WmZG2CkoWctHU+1R7hMjDwuwn9HK3uxSpIfXznERNqlDzbzOQXIjh30kf65TVgZYzydLD1rVtOENNtiLVjYm/0lXoyfagoutGBefWFkQ'
        b'noatPOv/CVcm/87HL8zWKacMz/sGRsAkp08+WJoKn/kGl4HoWByLpka7tlBJmTRAacqjTXljFMdkJktlZXPCrd1N4RgxKB6OU1ol0VZJbXFtcffHn4cPLhh2Vlol0laJ'
        b'bXGqGZZtZRJnSePeJQeWtHFU9k5tGgf0VbYOHfkn5rXPk4mUtt60rbecRdv63bUNvmMbPGiqtI2gbSMGF9C2MSixLvYsV8goxjGJyUNTc9pUoDANUAWGDiy+G5h8JzB5'
        b'lKcMzKUDcxV+uW3xtJnwvkOYyiFE5RA3pqVhOW2MQkEbd0yXcnI/Y91l3WnbbTtG6ZiEk2BvclucxEzl5LY3FV3MeNfcTiKWxo2ji3Cn26nsnTtW3rX3v2PvL89R2ofQ'
        b'9iFjFMtSoOJ5SeI7Ut61c5WWod7YedN23hLOu44eMlPZQqVjAO0YINFUWdhKuGN6qJhvDClrV4VrqNIqjLYKU5iFqSxtOqzaNFXOvO5w2tm/TYM2dlC58mUx3QXdc2nX'
        b'QPzASeXiKfPtTqZdQmmXKIVL4XDgqONICB03m44rxAkcVQ4CqYFsYe8SWqhW4SEQprbOHSW0ra/CtlCeNxgzUDC4enShMiqXDphNBxQytHWWxnQUdBTTtkLaVkTbBqO0'
        b'g4nDvkPJQxl0eDodnk2Hz6bDmcQ2TlLfjuSODNrGm7YJpW0iaZs4hc3S4WWjpSMrRtbSWAemgp5ZTc9citLrTCrchykcl3Lf0V3G6rbstqMdRbQjfmSosrNHP3ooPVbP'
        b'FJGgLUFl7dAR2hHRFo91CHQ6DBUWYTKXXl6vF+0ZNqwxonvHPEVhnkLAT+Yo7QpouwKFRYHK0a3baoxiT1/MYkIJV0WUr5o61iqthbS1UG5yx9pPYe33rpNQ4b1I6VRF'
        b'O1UpbKrGOJSN6L6ZRVvqgVSpCP1r6l7ZGdUdpTTzw4/aUlUOboSmTt5SgVxTXj+gQ/tE0z4zaZ+00XKlUw7tlIPijdSckGf3LqaFUbQwkRamjuYqHbJph2yc/761o9Sx'
        b'I6QjAoudkARolJhbHVhGm7vT5p60ubdClKwwx38qgUiWJ48bmDmQNuw84j7qNuKtFGTTgmyJBm3hifrVEUFbC+Qz7lgHKayDVDYOChshbSOUOylt/JlLLLXrsJwuZKmE'
        b'YbLawbihxKFUOjxNEV6smJVDz8qjZxXQs4oV88uVwgpaWIE1QhhpNaAsUlhjxpSnEA8mt4+snaXx0njZDDm716rXjlHSUlqH0NYhuBPeJHi6J/IohXks+lMJ/RFJcgby'
        b'B+YOi0aCRgNHopTCHFqYgzvCf25HkIR5y/2UWO8HX+KOrMEdKWepvEJk6YPOQ25DfDo0RRE6d7Ts9sLbVbeXKIoXKL3KaK8y1In0iU7E4U7wvXEn3FW29szkYTlG6ZmE'
        b'EM8Nd835d8z5shSleRBtHoTRdTJZ79q5KzzSlXYZtF2GwiJDZe5IsIpclObeqFcYrsdT5eh+xrbLttO+216iiUa4rbukUKYpN5NXyPWZCQwX5aly8pBaoGisEagxPYQE'
        b'Eo7KzlNS82S2QLNiR/Nde7879n7yUKV9JG0fibtawnrXiS/ljZrdthxF/xS5+XTuXAX685qndCqmnYoVNsWqgGCJRoeuVNQdqbTwU1j4jZmjjpHejRmOVzhJF8WE0UWR'
        b'YSWNHo1/Xyvlv1h58MryBMLn311vkrWxmy2Kwe9BS05mLIvFssdaKf/x4D+l5UK0c7p0gqlBwxhNzguAGC/6r0CMp5JoHMH4PEa6eIJg7Dv+fZZ84PRyqKgUOnjibyxC'
        b'nwDROBT9s4DGL9DOStzOHvaLtlOO24k/UjPttMbtVH8MdKgqn9KiF2jMQtSYHtY97ZIy5lvxi7WpH7fp8gTtHAnmKAHaXOhACsTIuf/NlmEy8Vj3DEomvpSWVL1g867g'
        b'5mlPkMwtxqFpSVV9U8VzAHh/Vxv1S8a/i71wE6/hJk6baKInpqC4EZGQfHOb+Nz2+5pJ4L0NXljihqaODGFOHXbQsGRhHQFBdihdUNfUOMXfw+8RwoZT1Iu279bU9lnn'
        b'TvVP8Hsa0/vCjQG4MRcmGmP1pDGxyXG/R74aLr1wW/44hTAN/dSLz0+urBetdBRX6sYaJ4BH7nO8VowDg/83ybGIGW66BOG4BOMNv1gTX8OrIf6Mtp6S5HaUrJ8sOATG'
        b'mJm8fl/rtJnWNda9WNv+PHUqtVRDYv+uFk1MoQtKa7BaQ0nd0oolL9Ys5dQpNBg3C5fCfIWvmawM9DTG+u+ko+FEq8tq6sQVL9ZsGjf7DjWl2biY39Xs/31PcIue9gQ3'
        b'QclJeg2cjKr98//AEpPTIvr9o4w/t1OqVpbmRstgEeXWyv6I48ljMWfBh6DE9qkTymp4EWwPyHiOHzd3jBlp9tROs6Ziifpgw4hiDjZqElmUhc2BVQpjpxd02fbbFdzF'
        b'Y7eSUithVyey/if8tf0/xv7N/w77NTJyq27u/VVDjGn8t1RPzH/HLb6SDSIOZTg8I5udf34Rw5Bn+buS9Zw3iQV1dTVqBuurGdxAGNzW+ILc/RfF35vC3vr/BfZijTY8'
        b'Ir7eR41rtCEGa6g12rRbWGo/I4xOG9VipNZnYyPWP+VLZA1H5znMfFbDDbGXvZajZv1z437bByRmhegp1ttnEBUJsN/QVVw/rjwB17uxXCrgEaJOZGSsQWnPOqWF9Ucy'
        b'0mypJjVcRw/sFhs26OAMXVAGu1lC0ArbiMpJtgOX0m6ezsFZPpjpQjX5UASDZL0j+czDgDhjxPSdqegiA4OoZ4Nt4PKsbEEemyqO1gKdTsFEJykIbAYXU1OwogTY/eQ7'
        b'HpfyLDMEm7jgnFERo8dxiAc6xUvVmiFgAJxizYdn4C6i++QOD/lOxZmAR9ewwUG4F15m1Ee2JszHH6HIFzMNQSHsY4Hzq7SZuNPwKLjOV8N8rvNnwQ2gBdxiUM+vzVyH'
        b'j9WT4RmBZwb+smBUyalYpJNLctY5m5Cja0GyBqWjhT9kssHuCD1GO+YYGMpl4NU1NJYh4oETdeAoyaYHrxjgz7E8gSalExIM5GxwCuz3Y/RjrsE+0A5b1WhT4JYLC/Q0'
        b'2JPGpINbcD9sFWTgg3B4uJrSnMeeDm94N2EoDbCDC6+mwt3J2GdWGmwlRGcQqfkRYIcfF+5yge1ThFtvXLh3YuHWnSLcU0V73HHO/4xYPzOj6T5HrAUZRHbTPJEgosU/'
        b'eqW4Zm6+JUXUjxyaSsQZPNhh8QRpadM0Qt4icAW0YVgKWdIEYgW4GMIo0LV6glY+vAD2ke8oE9xGC98egtEKb66Cu8RpGRls9bfVWnia1Af2rkWy1j9dnOaNBos2yxae'
        b'gGeZUXccHged4FByKvk6iaFyVoLtRCcNDZQzRdifAuiweYIQhAbJUUby+urWwVYkXeBg/Di2E+rHBSbvWX9waBzdCZwVgA4G3MlZTBQNm/DECru04LEc2IvdBzhSjksC'
        b'eFyi7GYKzgqfZF0ELzNZ4U2wjRlom7SWpGKEpX3gyATK0nKwvongfnXDS+A8vxRrW3hPAXiCp8FxRvDPwytrJ5CjrNm+bCDR8CWKcVCWF8VH9QrRWBPywGlwQpCSzqKc'
        b'wBZuCJCZEw5VwptomBKwJmGOpRqrSceexK2EB5z1QIcHAwjCojS12eZGoI+434ZHQDs4w38G+gTRLnU2wRRZDNvIjBNSOJsgzqSRT+h4agI7yKclJAoH3PK51S5c4jzB'
        b'aZEAa3f8JqbK2eWo7AywQQu2waHFDLtvGcGdaJKqBHvGNdjgGTEhO9y3OHTKFHUFbiRwOJx4ojCmaRX2zCzoBvaRiRDNgmUWjMLaRthLlE52pvobMXMZmsjgeUcioOBU'
        b'VgrKWdE4DtQD9qodAA+aB2D0fLgJHBvHpkHz7k3SaLekDFTgDniDmVjIrGK8lkRFuy7FUxFYD9vGwe9iwHlSV2A5Rv+CW+E1lIUVTMHdc9xJnuLUAH66ABwCL6ERplGK'
        b'ZlPYBQaZNWXICG5GspUk8MLQhmiePQcOsVdXmREKwFuFlpOAXIB8FiNeBMkF7IVDTFdaQN/K8WSxyQygErzc3IQ/dIZVFT9nCrxgyMyCaAqE683UKoP64JQOqxAtaH3L'
        b'NCgWlFHwDLhpznBxkxfoEsMzq+AlNOHAgxRomwZ3NuG9C7yw0A3ud1mGnntRXmW2ZDGsXqxLIZJojzlX6x9fYc/gDZ9x4JDNoXxdY1qBvgvz8GysBpmtFMtXeC1L0WYe'
        b'uhjoU6hnHoqKtfpFceqHrwTqUKhCn/kGTV6q4IypuxL2+HzogIJUNH3i16V5aMO5mrWUVU7lUYdZLGqnTvnEyQXZjLEJFvA91jIxzu/AvC/9Uye8smJJRfPShsiV4U+f'
        b'FjdWNJSUPAECJvdEy3oSOPB47godtFfD/qI/Rf/WU4r4+fgvJ3c4a7hg1EV9O+mPUaLGgOOwEx5C/7dCrNOyXyBMJvhKKVmzBHlJz1nPQD9bFw6CjSysk3BWfz44ydh3'
        b'gc7cJfxM2Jki4AngjkkKMjazNUCvBrxS9ffdRyjxHA5as2z9X8pPzfxrtHFx2KVjIytuOWzYPKZ98VBk59Loz7bEue4+2LYyOqJR7/zeWR8lRUjfLTK6nFIknJ6dGZJ7'
        b'rXvbLyO7TVd90eQ2P6sn6f7bR+o+/nHZsiHHqNtxXW3V7zcajh5c+9NB0zNvu6veoNZuW/DH6WfSD4r+crl219m5p3SOB2eCkul5OoleCfP3p3W+snX0C0vj2T8f/Hmj'
        b'65GUy3pyzs6DxnnZc9rr1ix6b99J58i9rwecDhG8Nnb3b8J9Xn+IDsmPmffqHlarXWmyHn+TZ+vR2oyFcSd2rvnuhxNh7CHeiaADx6bnGZZ6JSi0NT87vff6ivfeD33z'
        b'PLv9cP3XGTpBVNbjn7U+bD58Zo5nd2znwlvxbfYrir9wE/2zQt/8QuD6I7Y7rs0e/eh4Ssf1c26zjFZ6tix492zGyqorJXEhTecity/7jr3XMryh69XP3v/c6itt0dpP'
        b'NGdVWTxcsna158AwPTryzuqPZ/trRf3g1PDVHz5/XfcfV17x0jm/PWzRro/vF77mbLhAR/oXs7c6ZLJ+xY4zBfeKS/8u3f3uxqojOqtmfT6nPY/9kPWOKK7+y5Av9GpH'
        b'5n0z+EnCR/qvzRGUz9SUVncmbz54+K/HN15I/fSf2scuzVDY3W5WGlod+6arNUdiNS0HxnmnxwS5Nr4Z533ytri4kbvrz6uUQqvaFT8XTFcGxGdlxfaePHiv+JTBey+/'
        b'nnP3ls9XR986PXrdvffH/QebD1V8IQjy/nT4wCqe9ScGe/42Z98+wXsbV4mPfrLg0sfs88sf3HqHxTVy+dtqr7/9dOsrcOOqg+gVi/q8kZWf/rix/2NuXnQlPPbWbv/z'
        b'x9Z8adl80exH9w+j2m+fabV/91Nzy/fW7fyiTfjKjhUm3/q/vKPvsPDEruNLvzN7VJwtunfs6Gc/bQhtdO3+QidP9FXVP2c0XO/sOOPbYPiRzZFvdn124buXf7nwY3zA'
        b'xZW/nmsq/fKvV8VfTVsb9K1/3ldfQt5Lll+vtpsJU844rNor/NPfR88lmX/Q+EvIh73cENrm6+/a+6Lyzm/98c+KbzIVX2+yfs973Wdv3O344RfDvCNL7n/t/cbPVOSD'
        b'be/nFDs++JI1dPvVt0RZrFtnoPaHxz+eHv250y+e5x7n5l02yCv9i+n03NqVlVH/8M848J3068NfpT8ISJzzxTfHZ5WEOd3dwX5vp/BWzlf7ut/7mfuTZfDIx0W8EKLU'
        b'4QGG4CW8xVgBO4BMg6wbQ/BiKdHkiQf7/fXgDh7cUJCs44FeDtAm2ASc4YCO1Gi1LiPYAQ7refJgH4PIlQTPWLPzkqGU6OWk20TAfnBSOKELyJvGKERdqgL9sL+xAWxA'
        b'G/oJ9bbDZgwAWORafjJaKFtXTyggHgbHSGsN4PWlWEds+1K4e0LtrRpcIychYiAH14nTqwtoh/dklyYBEtKbtdEYGH4/uIoR5+rTvHmaqLydHLRGwC1E9Qb0ggONT8Ey'
        b'QimBVVQrwN2MIHo/WWaR4FTzZP23ej5pemgkbBHD7akT+m8mrOJ8BtqvGu6DV9E+bVCPAGGxc1mRJqBDDcSYXAn7XfGsqtZtAxvAFUbTdBsY1FUjf/KWgMPjyJ+IfINE'
        b'02g1dgEhFvL8K59gaa4DMkKQtGi4T5yGeYMm41RHeJ5L6eqzgTQfMFqGiBa78vnwHOzEapZeaF8Detki9KJ2mnBpMXqTbJ+E13uJDc6xV4CWOaTwaiADQ3qlcHACAZTB'
        b'/0yFt0jDykH/cj0v0M6ghzLQoXDfcsYL726XOWQbsyfWFjNKI4QFLpky+nx+jk2T4ErRK8DRKnYVvAZ3EAGIEi8Twx3Jyej1iU1prYMn69me4BjYy+iVtZfUPoGNNIpL'
        b'YReKYReDgXscbgTbsSJYPbabQBvjdk1KN58NrqN9ehtDjS3rovTA4ALQs5Toi3FBOwteRJ1jHAwBGeyAm91B9yRtsv3gJKm4FGxcopeSbtLE10TvKddZaAO0H15jEO8u'
        b'g1ugQwy3wQ5sviNMFerit0ULcFkjqAHsJo3zRe0kGqRqXEmqDA0lM7RRh/u54DxRy0tCkr1nCvqjx3zUSTX448ZE0oNmtLmVTUZMNAGnYQc7pqScUTy7Ci7BW7B/8Ypx'
        b'zV+i97sfnmcQliXoteKIHlyP2q6GYZ4EscwHOxmB7AdHZ0xgWKZBydpxDEtdOzXCJuyFR/SaDFCiTTpojDqyYuB1cJxEJsC+dHEEOIlGL9HX5Saw4C4ztY52Ntg+X89D'
        b'AE9ZTyD/AUkEo+DXmzBXLKyd0O9LhOuZkbNTuFwP3ARStWIghvN0SiRVVYNbvpOxAuHpEIqdNb2QMNPZFOxHUobe0q5NQAWCTWWMJttFQ9NJUIHNqwgzMFAg4reMNMey'
        b'HJ5vqtRLUUP6IWnqIVzyQF0Rm85mePk0nt8GsI+opGbAgwV6sBsMMZh+GNBPtIQwaDHoAL3YzgqJIOqq1gooS2U7wqPgFhkZJZ5ADvvRFqsf9E8ADaIXs8uMfF6fm8XP'
        b'BWcm9OOxdrwBo5xXDU/ZwlavDDSDY8fVl+Ax7HrhHNap7QQXmWPkPWWwnaTZyYMtSVZLsWeyC2x4ck06mfL8m2M1vDFYMNrRgk7WLIzJyyjJ7imCm/mZXmg0kzOblula'
        b'lB68yYZX4YUABsevDbzEhkeD9Dzhbg42UfOHrbNIj8LWOYmBVFOtPT2hO52hR6hZCHtA6xRjAXhwOhs1C9sK1KOJx/F/X5/w31H8IIAGz/3vaUWQe7pPtu0ref/2Dp+c'
        b'7Caj94bvmf38WHwSi/IKGKPqWLZej0go1VK5ep2Z2zW3s7i7WMpWObvL/LpCpaEqgUiaqPLykyZIE+5PXKs8fWnPMKnWfWdX6eLuyDE0iBNZ8vyBYuZKxfeTBw4mXoqi'
        b'+XE0P5Hmp9L8WQr+akVukWLuAkVFtXJuNZ1bQ+fW0bmNdO5yOne1NF7lzpc19q644x6scA9WBUcMLpNzZZoqLxHtFT6YN1xxrZj2SqO98mmvItpr/hhFCYrYivJqurxR'
        b'0bQK3a5jxbMfUdQy9POYoipYCczPLOYnj/kpYkvZ0oBOHZXAX543uPBSCS1IoAVJtCCdFmQrBGsVefMUxeWKylplcS2dt4TOq6fzltF5K+i8tShjYKcuydhbQqC54lBO'
        b'haBsdKYit/B2Jp1WTKeVqVN5+srder1pzxhEV58gDJ4Tg2JCOg1UnpjUXqLeTAz8FstiQtR7D69eHZmRPPuue+Qd90ilezTtHj1GsVxjWSoP74uGZw3ljQMrlB4xtEeM'
        b'wiPme1SqHJUjlK3oTVfxfHptaV4YalvvPFoQpeILLwafDUb5eg1pjzCUfLBhys0YlxPg9ojieLk/xsF3mpSHoKupc3n38jEtjlfQmCYlChrTp/xCxqwNfZ0eUSh4jAOm'
        b'C2N2aAc2WDmqqYzMoAMz6cAcGuPZFSEeBMWwFSULFZVLFPXLlZXL6ZJmumQVIvx8VgwmfJTSQaQKjBhcOFBHByaRvLl0YD4dOHc8Mhw7Uav4QyYdnkuHz6HDi+hwzOqI'
        b'BMxqRY1YsWyVsmYVXb6aLl+n5rKUrXDG0H33ERXsaV4kzYtV8LKGK0eqpVgjFNHQsZglW9hbzVypRCFINt2G+MPLRheOrFWK8mhRnqJgnlI0Txorbe5Mu+8u7F4t1VAF'
        b'hdFBM+mgNEVQuWJWtiKnjJ5VjusSKR38EaURnWlBvEKQPcoeDbytOy4dvlg2Yp7cFdGCCPWd0K93cW+dQpg2PG145og1ehrUqYfTYJ4pBOnDfsMLR0LViRk8wHB059+p'
        b'jRMV9Baro7xFvSt716Gb4E79+wHhA3MHSuiAZEVA+Wg+hlksodNRO6WRSgc/LBh2iAo+fgzn0ADGDUJyO5MWpEl1Vc4CTJR0lsrFTbqiO/2uS/Adl+BBq7shyXdCkpUh'
        b'qXRIqtIljXZJU7ikqbwDMDJaIs5BvNmjUDpzak7zIZu7Ial3UK6QdDokXemSQbtkKMgfrnsuUxsTollkSt7pQ8+vF1ftEyDnyhcMWg7UKn3iaZ94dXdw92heBOphUMTA'
        b'ioG1iqB5o9MUaXPp5HkTnHJ2VbgF0s5BjyhrxxLWoFpzc9Y8Rfg8Zfi8MWPK21fhG0MLY+8Kk+4Ik0ZNlcJ0WpgunXnfUyBzllX2ePV6DZrc8QxVeIaOj8QGpUco7RGq'
        b'8Agd41B84dPJkATJ6rtX3nUPueMeonQPo93DxigtNJKHtUZZI7p3o7PvRGcro3Pp6FzmORpwsaxk1qjJiNVovmJ23u1ChUekTEvO6tGVzxyMuZSCRrRMJFveE94bPuh7'
        b'hx+u4IerRKFXw/rCLkUMRMji0Q0tSqBFKYi0AjRjRMTI2fLAS7r33T2lYllQ5+ru1fJ6ZmYdzBnMGTbHVV0rGSpRzMq6E5GliMhC88kga0D3rk/sHZ9Yhsiob5HZLFXy'
        b'LEVW9m2ru8lFd5KLlMnzEHGZmPu+wYMmA1aDDXd8YxAJh/NHs0YK7ybk30nIVyYU0AkF6KEqKn6wSX1MNKcEhcr4+TQKo+bTUfNlbAU/TOkRrvAIv+8hxJRVBBVhVhIk'
        b'PTUjH3FYvBIMLYTCMSbUpPh+vUI0jXr69vJ7hbRnhMIzf9h8xJqOyaZj8kkE7RlKe0ahS2dPLG6pLFkl86sKiR52VwSnoMG+RukScN8jSGakCE5SeGSiv9FY5lfKve8T'
        b'JOV2G6jc+FI9/K9Tb6yEgxdKZtGc7MXxnk5jc3lFY2lVjfieVklj84JSccXvUQlV+3OcvPozH1fzuBT1Aqs+Bx/itVNEMxSt+XFJLBbLAX9i/f3Bf+ob7ddYE/S4jj81'
        b'YBjD5vA45GCZjfaZXWpHKvAm7KOIIxVvMMh4eeuC5xNS1faXE0oNVuAQ2ApOaoBW2GJBwA3ATf1AtDfcg/azyQKwI1PtmMU+jL9aAx4A1+AeHpt8h1gKjs8fr61rOVPZ'
        b'dNjGGP+f9Vn7bF12jaSm8miCf7DSAW7kYxOx8x5J6cLk9Kyl2NomKwm2FuEcO9LRXnv+dG0XeAxcJZ+mysCtWMZOvRMMEeNzNUDBZriZAFGgi22wLRXuEniAnlxSnG9A'
        b'VpK6B6EuteCUJvZ4O0TqF9RzsHcVfLKKNsj5TO0e+KsDvBGh/vw6F7RrG4F+E0IZeDaQ+1zK+ILjiDTL4D7iNrsWnDYSPymMlDRb7Xcaf3LB7/wL14H1jtqgaw3oIoOh'
        b'SvPS65TYjkNRvfCtY3npdW9GG7/bZPNyyXbToKp2t9rCm52KXzbY8evvt2zeHP8X3fMbrx+M/TA3IvcfHNk0w7OzjKTFK0dZ9X+3f7A12PkXPdOXb3z7p6MOcrOK5eFf'
        b'vn77aMFfSzztf6rUPsn3/yx75GJEY8+Xv+qaxJmlXrF3tDu/M6B78OYfvkz8PHZXaeH9sLNfT//Dy76hHsZfnHzvvSMfzDYuDm1uyujwN+Sd9a3U/JB6+28tO98rG/P/'
        b'6vim0Df/5DrbYKTNUpK4c973dxUyw7kLj/OrXU/lndX8cJ1zo9UPlX+UvP7OsQW961599dWKCtfwwKsGARv/trIgNTF91Vm3+x3d7QFjZu3Z+RvqP9KlijIWHDJ/oDn7'
        b'lZP7vtPWq/8J1GyOqZrmPNt42UGXLvc5Z3e07P6ws3KseOPF7TdujsZWhs7Llr/+ZWzA3S2Lb19883rXq058TUM+6Fm8tMjvzV3XTBY3bNbRiu/56OycGedOz+EdYPWe'
        b'mM918nd7K/ejB9ULNbbdlvL1jvR9V/Trg2tnH8+VrAlP1otYGXrRp3DHZ1nOhbvbs8I+i393dE/gysCC0CC4r3tu0afzgdmF2C9Dd4wGvlMtynn4p7Q6r08/t3qPG+lQ'
        b'mHZ4jWbCQpOfgz82+OKXvM/L7jSZXOLn7XDXu325p++ND0tFYc2iI/sGzkg7koM0sn2PLTg7f+sn75ud2fRGeG7fn1Nuf141c/6PO6IeKLKq/tSxKf3m1h93ZfVv2/6a'
        b'18dt/2xyjLl+u/zhHwQP70bl+m7Y/eab4h8/7EmyCP7AS56yRnGz/nx62e1FH3979UjI3A8sfzYwsFzAi8tcaS9442bTfL+HY+9+L8ye280rEz6Sc8QrMxvZogiv/r6z'
        b'yw8H+0THfXd/bTv/c7uWeUcib5+k50YYtO2Z8WN0QNHqNTs2fvn2S1Z7M3LnbDCc/WlZ1vJtb7xmd+9Xm5X1ZyIKWjt7H6Y8PPZQ6Q6uWotyG/qnfTJtNO18wem1otcS'
        b'HvvX/b3Hdl21xvfvu4r/Hnh19/K29/fd2iD90658n8ulAb2X7oUd6+377O8f/vDlqXAv8S99P3lFVpofbV52757DaEjEO+af6pZ9H3rje51b72lEzHzrB/s5awz30t/x'
        b'fIjlpkujy2+YbYIbSZMtN+EGcJqcZxQvXsKYghIbUYdVLHABtjNOBhLgDXgdH9Qyp7TgeAwLDDllM369V8DNUw0VbZOLOVn+mqTQOLgXDuETVXKcCjYmsODWDDE58zEy'
        b'fL7xahmUasCL4Bxjsw864VFwQTz1/OooBx9hoXlZwriZuYIm0d1qn+dggwYrpgL0keorjMGm8TMz0AE2sZzBAOglB66JqNxj48bTuNtwgBwC2MKD4KqvBhjQg9fJqVMM'
        b'kIJrep58NAcOLVT3Uc+UDTcthR2EOhVwoxE2iq/nsRzANYq7nAU7QG84aZq+O9ivNtEE1wyx1sYNcJM5zNqTzRMzDr/gvtIMbCuru5wNzqHm3GCMi6Vr4RExb9yIE6Ip'
        b'nLUSdMO2e8bmhq56QsQ/dr6XByssIIj4CoI73HXUVqimaA6X1WSRgx2DpSEMW3XAEMFtYSx8gdySOTLrbQJdxPsYhVUgEHkOssBGTYqcrzSDVq7aL9pp56lncpYzmOyX'
        b'm/jj1vzlGupTvU4wwJzq7QZ98ITaMhPsgJvHjfaJbaYHYCyGwTY7zqSDp1S0VLAdg2APOe0KqitUe8wJCiMnbDUuzCn+S2ssxIhUe7DhLAf0wCEtFtgDjkcxZs2noATu'
        b'xqfpu/B5NwcMpIKbLHAEbMpiTmQPmMBNesL0BiZFI6rXxAyxeRNnMdiezhRxHHSBzXqoUQzNtA3Abld2ObgOTqmd58FtdozTNbhXgNI98bl2FO54TNScDoLuqOciO8AW'
        b'sG0qugMijFTtWeamNTkqXgv2MjUzJ8VdwYRYC6AcV0ZOiYtC1OfEboiShCinEaPa9FLSmaNguAWf0u01AnuZg28p2iacHPeexwqgsPM827nkuAvuL7EaP+0CZ1eMo2OQ'
        b'0y4kuduZI+6eabNgayozljPD0VBenwUOM+fXPeAEkPMnPLhpgSssuAl1sJM54NsAb1UzwBJaJuN+BjGuxPIljM/D9WAQ8evJWRzxk8KiLFzhhgoNJ8TeW8wp8mEHe2ye'
        b'zOwqtIPBTnCRvQDRdDPphbux83jspD2VvYWdjwY8CzZFkjLibDiMwNZgv1vY/ZNuGhu08eDJx65kg+QWiwrBuhy74BYB2D5Z1cynUNMUnEQD2IMIkcXif23/7BWkmbHM'
        b'i6HAcUN39cYoyARvjcAeLcqwkONrmUCGyqqGKrJvm1qfJ2zJduJiM2t9Mh7tQL8+LiUTbk+EA1imSDEcjmMe3MyMx52r0EBTg3+AFtBLaRaznfWX/V89r/yv/ZX8zvPK'
        b'pxCDmVcWF/bzDNfIKws5lJymiV9P1KeSzYksys6pY94YVcgxcXlEwrYEtTVqAWc6eoRDCVfl6HHGpsum067bTqKJTVyjaGtveeAd6xCFdQh645fES+JVtk7Ebleed8c2'
        b'TGEbpnJ2wY8/wharM0ddb3vTKcVK72KlUwntVKKwKbkvCqZF8bQoWSGqGs17o/DVQsWcRcr0Kjq9SqKpsPdWWvio+L6yQLnrAG9AOOw6whtNpGNzlPxcmp+ryC9S8osk'
        b'mpJmpYWHiiekeWE0L1rByxtOfDkFpIwuU8bn0fF5KMGyI4Yqoai3ViGMG2xUCCpRSwR0ylzF/IV3Uhai+JVKC08VP1gWMTh9yHrIjg7BhrH8HJqfM166k3u3gHbyo52C'
        b'FE7ZgwFDEXRYOh2WLdFS8QJltvLlwxpKXgLNS1DwCkZnKGbNoZML1PXyfXpDyKmSgp8xzB3RGTFUl3nfwbXbkHYQIcryhPhIJVzByx7WfFkX6I4GKqOz6ehsdREooR7t'
        b'4IMS2rtg88pgGVduNmB/xyNa4RGtcvE8k9KVIluudAmiXYIkCSpPb5Rv+REjRNyBSFqURIsyaFEWLcobJ+l9xFwbYtqJT2nsg8YoTUu7wUTyc9/BrVuPtEuFr1C16JJ2'
        b'CH5yF0o7ROE7/W4j2sFf4ZA6yB3SGzKkg1PHdLjBdpJEfAZk4z9muJRliV7c/6NhOYdy9ezOoF1CJDoqN560TObaK6A9wxWeGcMc9C/5D4Yjhkq3TNotU6J339qetg7A'
        b'1vPlLJU7X9ooS+hc1b1K4Z4grx6O6auTJEmSxjQpDy8Uk0x7RdBecbTXTNorTeG1QIGNi+fRsxYo3cto9zJJ0n1r5zHK3DKZdV/oL8/HJ4qFw5YjdnTMbDqmUJIoDTqS'
        b'qRKI5Im9xQpB0eCKobV0VB4dVYRiAo9kqJw9pUGyUPkKhXMq+htOZH7ReOF5yUxlBT12vXbYFl/lIpJmqhx8xjhs1whVcPgoXyXwHeOimzEKBfcDwp7cSBLGtClBoCSh'
        b'I12SrrJ1kORILY8UdxTL6u/Y+ihsfT5y8ZBZyaxUDjxUmmccS+UbgG18L1kPWKu8glA56BkqCIX3w2Im3z5CpcezHpNQkoCq0aSc+GOUFu47bp/CPx4fkeezRuNH4xVZ'
        b'ea+k3k5VRadinxT5LCZGlTl78i0pQ+DHNJWZC5ROSbRTksIGM8DBpWPFXXvRHXuRPEVpH0XbRz2i7Czz8ZGTuxftFqRwix4MkMxU2bt1rKHtfR9RVraoCm+RlNutrwqI'
        b'lnJpB7/7IdFD9nRI+ujy22uwn4ngBfhxACJ8dwTtHDBoNmSlcI5DfypPYa+nPH9gHh0wk/ZMksaphKGyst4ahTAe/Q3mMb9jlClpPQ5lbJW3n0ws9+tZ3rscH4bNZr3r'
        b'F6mIylH65dJ+uQqv3DFdyseP9o5GosYLYBKLepp7mwcdz66WrX43MFYRV6QMnEsHzlX4zB3jUD7h9wXetCBysJ4WxAznjpTcEeQqBLkqL//7YdFDkXfDMu+EZSrDsuiw'
        b'LMQSXgGLCXtSZfFyV5W3v2zNsKEiO08Rjf9UM5NHVily8umZc+TcAcPBRqVP/PcqD4GM+40m5R2mCJutFObRwjyFR959O2eJHv53RO+RWBPP6mMcPN0zU/+k0zVjxuhg'
        b'DvcZy4P/7upl/Mzp2r+xWL2LjRd6Js7SlmPrBWt8FPYfD/5j5g8/4C5dwkZ+Fg2b8PVmHGzBwS8ouDe9BIPZljUyh4UlGLm2akklMTVv2IoDKbYJ8+CgpFpq0+F7+pMt'
        b'de/pTbKJbfDDqbHuecOvONiFg2mo9ns6E6Z897TUdnP39Cebq90zmGIGRiyEiCEJYch/zGHbvyEa+GXwOX4PxuXjtAaSjynY30FYLND7KDXF64E+9nqAAxvKlafQd7xv'
        b'YNaSL3GVciTWsgp53KDZYNNwzmD1aIAiO18xp0iRNVdRvEBRXqVYXKsoW6IIrlMIlioM6pUG9bRB/Ri7hGUQMkb93wqxS4MG1pOK4jlTfA3MxL4GkvFMjMLHJGyJR9Oh'
        b'lZPEQmUsUBgLVGZ4XbASoSRWosc4aElBCczt2xapjD0Vxp4qMzzHm4egBOYhj3HQMhMlsHGRoFq8FcbeKrNwlMAmEiWwiXyMg5Y0lMDaWeKhMhYqjIUqs2iUwDoWNwOF'
        b'j0nYkorSTG5qPG5qImlqImlqItPUyWlwU81wU81wU81EJIGpdRuqyE1h7KYy80EJTP1QAlO/xzhoiXuqBLxAmZGlCYWPSUgKsXBoa1YZ8xXGfJVZJEpjEY3ToPAxCVvw'
        b'8mLpKNFWGXspjL2YlljilljilliKWpKfIpo3JpovJpovJprvM0TLwESbhWtB4WMSErrZukqSVMY+CmMfJo0tSWNL0qCwJX1Mm2WAthDPCTRZBjb46plAs4iDnTD8T4SM'
        b'LjF+45wLXlonZl7droCrkzF6LaFMowL2gn1TNKknIKA3ouCgFjHfw3D+lNq+S2eh1oQpn8b/dVO+59pzPW3KV5XRlIHujDTNRT7+foG+ASJwFcgbGxuWWcIj9U1ieBXK'
        b'4QDsg1fQK/dl2G+kra9rqGOgB/ag98adcB88mDML7oWH87gUxr/Tw/hwkiYHVORs2GVE1LBb+d5wDx9sWwT3wFYOZQqPceD1LBdiVhIDh1B9R32x/rkv5btsVhNxRL9b'
        b'ax4fp0YBB2xsoEyDbeFFDnZHCgcIpvQarHCJKtwqQlOiH+XnCK8RixJwDAw0jtfJZHUqJRUCKdzahK1HzYxX6JeK2FjnXQRvrWIQnc/ANngJ1UaysWA7GnKuKFO5P2ml'
        b'p58v2AV6RIhu/pQ/vO5Cvs0shC+Bo096yJmGuoZb2Ioy+gM5Y8tzGO4Cl8FGeECEBCWACgCtsJ2x4Diwwp3pI87Lpsz4uqa4h+tBBwHrBr2LVsP18JoIbTwCqUADcIq0'
        b'NDsfHmJqVGeLrWChbNWoPmKmc2ydVqiLCC0IQVQQOAKvk0xNc7TV7dQCnQ1VOpQpuIYyzYKbSVXB8Mo8uB92iZD8BlPBPqCNIYo81JJpoZYz7AbXKTNcE2yBG0hV4qoE'
        b'RGuALf9DqJAKeJCwLsMwaJwgiBBOiCSnnRjWHQN7SG3m4gXwpD7oR4wLpULBEDhBPkqBgTlAqua3Axush1vVkgKu6JH6IuFWcMaoENt7xlKxcLOAIWO3ThqpEOV0ToKn'
        b'USZMfySa60lt8WAD7IkAR7CVQhwV14goQk5aLoEbYDNmOK6xM1ysR5lh8i8GWxnblw3g3HK4A2wRI57HU/HwPNxEBIxfAI8xtMSd1FpAma6Axwk1wTWwkwiYvqY9dy02'
        b'eU2gEsApd1LfulooJbQkuaZRZj7gAqHmVU3SzHJwEZyLARfEiNuJVKIdPE2sEHR8LdWdwwQFNxfjOzyEMEXBJbiNmJHwncChBC8xYvpMaiaQ8ElD8+dWk8RI9vpgHxhC'
        b'IwFsBDJwBuUMiieVpjlg/TV4Roz4nkQlgQvLGausXZWJDCOYnOGUKdeZ4eE5uId00cur0bgJYtYnU8kGiwkDXcCu8cZikUGUKS0hDIQvRZIxqz0H3gRduljrmEqhUsB2'
        b'KGUsdQ6CE2lPaOqt5z8+UWBOZsFLhCP18Ag2TcLuydnYTCXVB1xhBKcL3AJXSIM3wb4G2A171FlnzmN4KYdH4Q3Y1gz7ETPTqDQDMMB09CyQGo4LD+4tolETOEW4aWNL'
        b'2mxE8WAH6ID9iJ3pVDqa8zYxlV7SiRyXHpQxnDIDR/QIQ6XhZODDq0I4iOq9APsRSzOoDHga3CS18mZhHfCJ8diFKuWiORDzpQkMEoaWzgNnCkthP+JoJpU5o4SZ2npQ'
        b'voFxIdJyBFvmjAtCJ9jA9PQgkK4BvfmwH3F0FjULTd1biPhhqPWrTL5YB7YNaFGPrVi1IZIlvGoNNkRiE84sKitRj1RYCjemMSK0AQtCA5KFDiREB1E+DXCDSJAb2KkZ'
        b'CTr1EEezqWwkTcfIzLEUXCkgpCEZw+3445N+HMnFzgT7wWl4Q4+NwRhyHMBBsmBgazTxhAShnwRtPMepmcnWIAwBh+tALzy9Vg+xMpfKBVvQvIg/1BjCDWi2HCcr5sxN'
        b'uJHJTviJbtXzalsFWss2B+khjs6mZlfAHvIRPtOumFkyNjXgL0bMXDdvNZl5wDY0K28Jq9VDnMyj8iJmkpkOHAX7QNf4SrOhARvTqhmyVEyqCvMIhF3ggB5iYz6Vj5p9'
        b'lbFbO4gmvUFmAucsaqTMgjAPNyBWkQ80HaAnSgR79RAL51BzYJ8uETjzEkM1YThI4MlobmcRoua5MbzfDK7VoRX6KGhFdwVUAdy1gPDWp9x6DmpGK+JRIVWYEcXUcs2j'
        b'DvR5glbEgiKqCMgd1T0Vw5tsE7gf9VRICeMsydMMD3hDCA7C/agj3pS3UR1jv4pkFm5Ew6UthyI2ofmwjySf4V3kuRLuRyXzKT48ALoZunfD/rlgy7IcRHdXyjUVniSJ'
        b'9XNTqrAhMuqtD+VTgNZowuUr4FR1LaL7fsY0bh4SEZw63QKecwEXc1Dz3JDwbbXi6TKrgDwnQL3kYOqg4ejvgtfvCDTmsECmmmHlX7IPYVbNbAM824PtMxkti0Ef7Jt+'
        b'fDQT8jaipZusJIMxREB00Xw1wKzVDqwaE2a5MNAlosAHB2DH+KKHci2gzOaCHViC0sFmZqo5qAsuTMyNcCOaU9GW8iSRlpnuhMMzF2Bf6LgNcAPqApAsZYQQXFBPVyFg'
        b'N5CphXsPqcXUAXQyM4BkDjNHtMK+JU8GkFYsquYoPEjkpCCLIdXGrLrxyScOHioeXzC7QD+PReQzAQ6wUuF2L7g9ScCevobSBhfZYAMXyD8hu8i2hmieLrEqfCOcMUr0'
        b'WXhf4JORxJgaKi0Z+0OfPKuEKmMx83CmUJvYH/osuzPvuN0c5uG7tdMoPHR9DF1D1wSsYR6mJDAW2D7LzomczTjMw4+jjShEIgufxJ9i3p+prqjbWxPvaI19AssNNRea'
        b'Mw/fKDSm0FwS7DNDmTw/oIF5WFqmRywqfTSPany6toZ5GBo+nfLAFS3528x5MfXMQ80wxqLSR3Ne5XcJQczDLEd1N5f5W63geVPEUry3aAYSTFS7YVH9H2ydKR47N5FE'
        b'uFupO5BXk/jdtGQmdXWSlrqt+tP6msuoT9qP4P9eiSIVBC0Zj5UWuFs5UZ+IyH9fM0MV7CjIAiec8IpI1VF1jvA4eRwO9xuDval8NHCaqWYkMnK1VxgsB8bwQMFUaQM3'
        b'0QxIROWsG2NmWq3uQLFW7fe2YUxXW+rNGKJE7op9I6ppqp0oGnTM60M4hcFJDlOV2E7UfA1rO1tKPe8/9DaD8p+bKGMve6cFtiFVQ4Pc41YtKa9o5nGIJWkDHkjMKQh2'
        b'AjUB6IG7s9JOXFa6pKSqFnulemIsWlMlbiyrq10aaaSLcuEXtu/XUwrvHOZv2FfOvarXpzcYc8lwwHDiMXm7I53Ncyug5FgoDb7Jucl3QSzMyKi6tet9DTEfteBO29xd'
        b'uX9dkjPT7Jjly/Wra17e/kF1h2Rp1WvnZ+kKDjS4fzTjVYGOxo4YunXANTv3SKRD9RtFJhbXnLI3Nz/4Q7iL9+lpUcO3xtwbfwhetrrjzRbn1786cuSlu4WiVfa3dCNe'
        b'u5Wn8P5qnYeFxqGAfxq7fOscbxMt+dQhdqdTok18R/Dm0gVs5xGX7BF/vxGvhpGsD7eXWbjPkG8J3nB+pFZ1s7enn1Oy9FvXm04PR4TvL/nc8eEf746sUWX+pKnV8t77'
        b'Do+Mbzqv3QNHnL/f0GwWNW3Pg+BHGhnTMh/4P9L/8zT3R2/2FSuDt309uL51cDNv7p/eGNx4bvDbPxUo8yxnH5PNOFu2J/fHgoCUgLRV3wbPtj1X/dHXuXrn5tY1flts'
        b'dnbL9Uet8W0/bfj283ebLsaKvswqWbXs8D/yiuIuSO3ves48Kepn/fM9J80gT5OHK35SRaZlnnXNqVE5nLziu/j0+x6uMX8/13bjh90F79S8nvf3i8pHn378c9mP63IC'
        b'P/x4sfd33Z5LrnKmnf3uxxUH1j9uXdL3avSWr9+5vsqoNe+y7eBHi1+/53PZxsO66rP6moNtQdc/WrtpDz/Q03H7hWqVZPNrD61E4Z8tW6pMum2Ykuak97DgNa7l50OV'
        b'f3wUZbRw5Zr9rtlhjoYfH5e4u92dXrCdN1v3wG3fPy/Ot+yUHl+WoBoc+Ydj1PS6ih6Tyoe1dUv67z18d2TVw493F8XV/bzNRRj3/R/Pw1nlm1pfvv7tg4sPmn4uzig5'
        b'duP1yGrDsHd6Ptu6/4Ndb8/qNON/2JiftNX8nff6Yh5l7lr1+rzvbt4ZLDH68d30i1vT5Xl//uSd9ytFu+f/2c3V0fnrrbY9rYYB+84b9iXfvpcrmRso2L5yZI+RkctH'
        b'P1+oTcmWzAvrKf6phXf0wasXhWWH6gQPD5S/WvHK9aAjYysLXxMoZ1/5y8/zjuXNXXrwVdE7/GtpIVnfyL4sOOJ97eE/P1i75+7Ocp/Lf5KZf5dU6CesbP+89mXLtYKj'
        b'P+ys+/jrn9O+qF1+NeKNN6rvf8lK7n/tk+svpX9Ly89w7PO+33UvK/lu2drK8x9XPP71l7pXP7D+S/Px+uSVH3yc/sqiv0Scnv3Fm/suJBxO+2LGy6m71/lGnQe3ftV6'
        b'z8IFesbwGP0f0BLvjD/Jp6dlcsPBLYq7mgW7rfhE6aAI+9uBrQyEuQZsKU9igX60ezrFqFFcj9FNhbvRwpYq8GRhfxtR8CiHjVbiFkbJ5QTotEBF98Or6AWJMwNe1mX5'
        b'gjMolmgPCW34cDfoTcFKBYPopZ0FhoRCEqXLApuwI4tkr2QNSs/bchkbHtVwYZQRTsJttuO2g/DMSrTMYdvBdnCEfCJfBnfBXlSsN2qPBmwD+5pYaItwax0pdh7sLeSD'
        b'60ZCuItLsUE/Kw9t7hjNjPICtLMlhoPEbBBuA53YdBCt7Yx6xQbYLWCQ1TO4lL6uWJMNX+I1klLNZ5emEgslVCPonGHOAl2LUGvwfKWhE5oKDoNWRnmJFQOO+ZNP/Tw7'
        b'uHHcyYcXSnB63M0H2mzs4Tn/75sWvdCnfzKFP98OacoHfrUl0pM1YeWka/JVX0tTjfLUmM6ipseyWhLG2MYWhipja0nOGAdfOQlkYubKP2rYlFzdJ7FcfEViyRWJxVdj'
        b'mpSJDYrXYq6dhSiF+jogmoUSkRttJpEOc00Sqa+ZRORGl0mkx1yTROprJhG50WcSGTDXJBG5ppgHTEryxJBJacRck5TqayYRuTFmEpkw1ySR+ppJRG6mMYlMmWuSSH3N'
        b'JCI3Zkyi6cw1SaS+ZhKRmxlMInPmmiRSXzOJyI0Fk8hyolsWlI9o2FRl6yATT/0Zs59Ig4OWpDGnCVj77jClqTdt6o3Pid1UM6wPL963WGq6t+5AXRtHNW36Yf4+vgR/'
        b'G/ds4yunBdDTAlriVDb2HUnb01sS2gJV0y0OF+0r2jvvwLyWxPsmZm2mbXmS8r3zlCbOtIlzS6zKChUcbpDAekTCNk386cFeMl2yTFp6pFmmKWvo0VHa+8p95WWDTpcW'
        b'Ki0jaMuIMSrEBOfAYVuMysqmLU5l6ySZLQ04MrcD26BMDyaBhKWysD6h264rDZQ5yhJ63OUxPXzaOVBpEURbBCnIn4qP0gZMx8XhUGKkcnCScFXO7hJtlaObdLpULBXL'
        b'RJ3N3c1yx87VSkd/2tF/jNKz9CaBJEbl5Cot7XaTxN23F45RHFtvbMpRLzfpEfcGS7Wl2vf5Qqm2yt5Juqh9nWSdPHiw+Y5opkI0U+Xgeka/S1+W1WnUbSQ1UuFkKLWD'
        b'q3SBVEeq062DYgzxVSf6X+XsITPB/7qDUbMsHE4YtBscMeowQq115sviZNmyuO4ICa5GIia47M2dEd0Rcj+lc4DSPpC2D5Ro4ITxqFmJ8nh5gCyNdg7B6d2xjoerysbl'
        b'G00KtdHjSG1HrUwsE8uDe9b0rhkUK71jlXZxEs4TUgR0ruxeqXT0ox39cN4EFhMiQrh7ybIQlZy71ircIwadFe7xw6aSBKnjkSRJksre8cTy9uXSpiNrO9aixljYTuqC'
        b'g9MZrS4tGbfTsNsQkd7JRaKlcuXJAqTpY9QMS8wZHEriVW4COauzWjJT5eQsiRtjm9omsFQenlKuys3zTFVXlVxvMEfpFkO7xUg5Kmc3mUlXkDRI5cJTuXtKNVQefNmC'
        b'Hm2cmCeL6axESdw8xyhtR4GsSS6Wiwf9L60YWHHHO1rhHT2cO+qqmJX1ivvIPEVewZ2EAkVCgcrTW+7Yw5PGqfiii+Fnwwc1BmcPiwYL/g917wEQ1bH9j98t9A4LLH3p'
        b'LL0K0hFFYCkqYMEG0kQRlAV7rwiWBVEXBFkQdVVUFAuWqJmJiWlm19zoxsTEvJdmYhJ8Mf29l9/M3GWpJuYl733/f1kv7J25c+fOnXLmfM75nKsmt8yVPmm0Txrj4Sju'
        b'WCVbpfLyU/kGdY8/liabgP8YdyxVNqHPiPL0+QN3RHOHu98DH3+NaI0+t7RuFdyqvFXwhj76ogzIogM0BkozlD4zUE9z9Toa2xHb7d6rey5A6TqOdh2H3WJQQ/kEdlt0'
        b'u3RbdEV2V3VX9U48s+bcGoXPeIXbMz99nriFn+hS7t5PTMiLiCMDRQ+Pu74qFsUTSKIHQfn69zmli0r+EIovxmRhA1g9syU5it1gBi05V7CfC8a1yZIjTmexWGYYSv9j'
        b'h78Md/8I1WRIIF39/o0bYWbTGRZIV5fED2fY2ahifU0AXe3/egDdEVSjo4VQdcgYnSFzOX4WNsOQWcMtZv9fcmRyRqm3VgbZZL4ewWaUBx7hs48k+VOEXa8gzwcrYMCJ'
        b'6mleanJDr+SUrGQs/aVoUeGrtL08QGup3u2nbDHebNdnBxx4LRRTrG4JOsDi1jZG2VgH5nFeX788rOWVW5PADsn3LaL83Jd1G4s2PznAj7LZaBPxNutjSz2p7G0hm7H6'
        b'vQp2m2IZe3tAhhY4Bhop7Wi2NTw4nxiWgvq1cLvazt4qckSYqBkrhexBYwKLWP1SmEHB/KKChXPJTn6l01wco3ou5u8e2KYPykBksyCKIficPwkNUEvJkoYwSZiKZ7l/'
        b'YsPE+pTGFEnKA1sPheeg2CrWfInuoFGsdZ9VOtoYxtAJM1SZUXoaj9Lfq5El1hyUUeqhWzIJDV0TPBpHPfxlIxTDwwQlmK4zX+SbgU28uZS2LQt0s/XNQhjeu+3gOtjl'
        b'Axsy2BTbDGxGgn8o2EG6VIQvp5hmYvv6mrOrKSGL4Rk7BhrSRWkZGX7+2nBvIqWbyRaHCskV9gYGuo5sL4oyzSsbu6aYifTwVtyDrA+4RouXcCj2VBYlvE80VUdXa2Uo'
        b'sK4uPq8sZIIfVYYd5Bav0aKWO+IXRxm+O90/eh0lJrihSCcrp/q7ZRyKozU5luVelkXudmGW1mo5mxSR1mRbxLgT3nq07e9sTBK5M9zg65cZZZNQx/cgC222BHlpSRlT'
        b'mXxFgod/18JMqauuGc+6S+h+X6q1+PsnbKzx3X6E/2mgGCufr7Rczcox8lu31GhxNkVp+7EaT3wjxq0Q9NFUn7RvsBH5MS/sBmJxhvNxXCrZgYhxH/rU3/9tk1d9X0XD'
        b'bA6lw2IHF9mT+8YeTH0b9y7qaYjwSV82OVf2+dm30dj1pl6d7r3kn+TUg2q3OjQdzabed5otf5FUb+Xs3XVK9PtvlMPhLbCHnNv900d1SnTp36mWr7ZOe53ooPnwchWs'
        b'SyG8YyFceGoi2nHWsVOhtLR0G3ysJcZoyJ1vt23JPlP+XqCpu/BVF/d3d5m/sujy0vI6ww9+tn7U8C9TWVgeL3U97+UlupKOdmXY58dfrQv5LOvnmJg7UwtSs30T1let'
        b'XPbN1w8cnHrm3nT6PnCl1ylu36pjNoFvpq8ID/EMM5h9ZJb45TFXf5qz90jXCl29jp28N+yr//VqZGhWzd2NjzvOvCW1+vSc1Vfy78dNnuj8S/PBNw3WlWVcv/nmvayz'
        b'Hm1vrruek6+fF/ij8Pac6DuXfpn7yUZnzqOS15qEX3wceHpX+dZV3i/xN+QWb/7HF2+f+URWU+rlUsj/ZXmcdauUbXFr0ay07xcqOPbxQcvWvkO3b51JW331TtT9j7g7'
        b'Wj9U3klK/uUsONe6d5+X88ErP3zx9kLLyU/vJMVNsr759muNe8vOBt1emOMfK+tMacr7YlXvjk92zdjaNPnaa6U/XZNM0Y+urir+6f63tfqH31HGRnpmWH68I3DuUun8'
        b'jalvzMrRepRU1vZgVeuWeT9m3SwNSdly/a7FO2sPVq9V/RL164Lw73pXbi24/82/HVs3r/z4su9n5fuPvxLbmn9nY9hdm3+4L1x5fOUvnKxsv9hPLp9pLT89dXnPe5Ou'
        b'8SM2J/76b1XOBPHH1WYfrzLYYzU37nvDI6zHgTVr7jX7nPjWa/PjpXc/iDUpqftnTFTJvScnfzSbfXbm7XfdZ3xlmBPS/MaSPjfjkrtjtz+qctomeSC99c285ty17v6f'
        b'f6OV9cOv1ORlvXkrJwpNyby9FF4GV0RC7IqpTWmXgDNgA9sbdINWRolxfCH2LtkpItyGyV6oS0nYFWA3lDHahtbceFjHBYfgznRftHYGsUAX3FBBVAdwPzgNrxOFQwrc'
        b'Cet0gsAFdHk7ey3ct4w4SoBtbHBcXLV0qZEx2KVVYGICzxou0aKs4EEOaIUHIpkaSGeDVh/YBXv6VTBY/QIuQTlDf7MJ7o2CdemgC7OybJ49ljXRHSXhua8EvJDpk6pW'
        b'eGhPCVrK5sXFkGdeXgpOY3VHbb82BKtCwFFwlnGSOBYINvmk+jH3g51wH6VnwAZ7wLFMRlnUAmTwJHowoR/2/9DOA9LlbNcqyASehFfBSbDfZ4BOygbuZ4egFrvMaKJ2'
        b'gINrcOEdq2BNSlqGFmUAzrBhK6yJYdyQOlJhhyglnbR3zDJKdza7CJwCcmaNPQ97QG//IosW2EnwIts6F2wil86IhocIA2iaEL3JKEyjxOZNgbuF1v8HbhWEufsZzhNq'
        b'9crAyrly0N9kCX+Ro14wiyexuEY2fdSzDvqUpU3NBJWJhcLESWVtt39lw0qZmxIHlvKUcPGJVQ2rZOFKax/a2gefEEhWyHj16xrXSbgPzWwkfKmbTEtp5kGbefRRvka2'
        b'chcVj78/pSFFOq+ttLm0aWHLQnlQdzYdliRJUfIm0ryJEpbKgieZIsmXTGkMk068Y+GqsHBV8ZwkIhm7PrMxU5KJxIn9SxuW1i9vXC7hPrCxl06WcWXV7YZKGz/axk+i'
        b'rbJyliyUOR/17PCUe3UnKV2iaJcopVU0bRUt4aisrKUcaUKTlrRAqtdYhk5YWEndG6Il0bIEWYHcub1IntjNOjZBtrAzo7vojluUwi1KZeuMtv+2DjJ9pa23REfFt2nT'
        b'adaR6citlPxAmh8o0VJZ8KVBDWMlY1X2nlKRnHVa57hON6e7TBk47kaS0ktEe4mU9mm0fZpkgsrWCYfnwpa6luF4156rdArodlPiHfSPD+2dZYmyRLlOe1pnmtI+EGd3'
        b'l/rI8o8WdxTLs7rdlR4RtEeE0nYsbTsWFWNh3UdZm0Wp7OylWdJsaXZLuGQ8E2etqmlsy1g5R150zEBpF4rOIvksuSFZmi0b3zRTyRPSPKGCJ1QJ3GRV7QaSBEmRpFhS'
        b'XJ8yRIxT2TlJxkvGP0Sl58hCpDNaou/Z+d2x81PaBdB2AQq7sO5gVLC1oI8ytoxilBoCZ7LR5shLj5n0WikF8bQgHod+E8iCmyOlkSo396NJHUny0G5LxsGj11npFiWd'
        b'oHLxxNttroO/ysOTPGt2d4jSI5z2CMcbbTdZltysPUceIpvRGd0ddsc1QuEagbfd/RvtPj10Keqr7h4y9P5kpZ1pqEw34dH0jvRuj143pVsc7Rb3zFNpHWndfCUO6heJ'
        b'Tpia7ddp0KnXa9ST6PXNYKFOS3ouOTzBh6fUkHOjHX788cdR03JZlCmvj+IYeQ0ZKaOMo+EjzYSnMBGg09IcCY6YgN58jYiIQy8ap4SJTDivm3BFFjqvW7HQkZGyDe9z'
        b'F+dXzb/PLcyvyr+vV1JUNbeqtKrsj/FKEDL/wRHFGMn8RbJ/HphTeFgI30dpIogVYTEcG4T+ucNfJq7PQPUtYA/a72k2oaspZhNKqM610EaaKuZoqM2HW3j+D6jNNRUb'
        b'EqwBbRAwwlo2Z4UoE/sOuicSdB+JwObgIgduhAf9Sucut+MQwt2pm1IOvBbdumF7+572Pcf2LDH6e7CH9tZ34g1ZLxq22FCLZ2vt+3jfLDOml3CGv3C8E9YsIUa41wys'
        b'IkO/koUEV4vsBaeow5QWyksVFhFKiwjaIkJhGDFo26ddCbALxkvP8MPAdnpqrwqmk72CO9nQW+bgflZJ9ftQlExB3cwBd5VnH/6yPoQlgP//9iFORmnngjdYYkwOMtYl'
        b'd0gHsbHgPPgCLhBspZK28rbmad82pBb7a2Woip6ri4iHdhHxiC7ipO4i5aiLGFnXpEqqpNlKQxfa0EXR/xnZS+Dz9pLXSC8ZctfpQ3vJItxL+LgzPPvwP+gla3Ev4ah7'
        b'CYuxKS/m/g/7yQhlncYcZFA/0WcI4vNBbYDINyMXXu1XbbD1wQtwC9n2F9g4sldzqeV9mR8U/2jCtSQni7XZk35lEZ1GmrlVBmOg0VtMGadhaxr0Zmoj4xmVSQmoA7uy'
        b'FgnASfQFbqbAwWS4kWS/46I967Ban5CSFUkxsQ0OzQZtWWA/lPnBfT7JKRxKewabBerBptL2zae0xPiZf1wkWTMpSh8G8t5e9e/Nju0XX7W5f77ghuRMlff3rPfbZz5a'
        b'ELn81QbX74tqNm2auenFs50/bJ7z88755rmer7fqr+Qn0R2H9y2V+f6a9dEC3uKQA3cLHr4BxEtOuI45mSjYvfD6t593fnRf/NEEO1XWlDfHv/ztA3ZK+IxfAgJevXZp'
        b'/6tHPjm5yuyr09zZoaKN/yp7pNy19GbBxWsdlR8/SvSM3q/9+Y5Nv7A7jnqujftVqEu2TdNZ4LSPn9dEKE32Y6MNTDPbLzCA2Zu0+c8TTZvQvxtU7wVbxxMiCT+PeSLY'
        b'Cnbimb8O7szEMQN2oB0ZPAE3kp1aTsB4kQ7YM0Cme4K9YpU1s8eToc3KdXACbdZWF2N1JdqvrWW7hIAaZs/Ui7Zi9RjURrunFgbYxrA2PKdLSg4G5+J9kok3P9qKBoSz'
        b'wKlg0Mvs1TrAVnhpEF7OX4DRcmsfoc7ziBd4yKtJKpnpxBDP94sLi+di2WXlkG9kMqHVk0kVXm/4+yMbIuujG6NrxqtMHSRG0sK2hc0L5Z5Kx2DaMVhpGkKbhtQkfGJq'
        b'JVkidVeaCmhTgcyMNnWtSVBZWKJrzC2wLBb0ibWDNJ+Rxeq5EpYkSGXK22/QYICE5YSm6ffsfe/Y+8onK0kAXKVpIE0cY/p0KAsiygX16VJGZrvTatO2Z+zIqMlQGZru'
        b'FtWKpLqy0CYTpaEXbeilMPRSWThJghvDG6NlXIWFr6wKHZgPqgaW5QbNgDqVj3BLcH+TBIy0nFouYybCd/BEOKTBZuJ5cJlmHhQ/xzz4106GWBoZMuPoqX9/+zILTYZG'
        b'+6kiKpdVSOWyC1m5HDbVyGk0bNQpZnexh5qd1VAE4SAOOBjlKNYt5GzWHTrZ5XLZVJFWIXczVajVpX0EdZYTmmk4V5uk6aA03RFpOiRND6Xpj0jTJWkGKM1wRJoeSTNC'
        b'acYj0vRJmglKMx2RZkDSzFCa+Yg0Q5JmgdJ4I9KMSJolSrMakWZM0qxRGn9EmglJs0FptiPSTFGrYuTFbrNurhnJ51iKFpIis6Ft28naxco1Q3kx3qSHFi17lN+80IFE'
        b'DXW6r5OeX47dMn/20x+skMiaMClBsIhJEpDwef5D0oUsstQPWS1xByFLUg067NUdFIJI8/KJfKWnWTeHg1z/Ffnq501Dao7/pZSXVpXml5WuLBKTqJVDnra0XFyF3VH9'
        b'9UdcF7k4vzJ/kQCPz0gBjjiI/xJUVQjymSImjU8SFJeWFfmPuHLESBq+djtmVPugb6ARnEsg0/WkZLg9028qZlwD9XB/wORkcBLW+PqzqIksnfC5oJ6E6bLyBscNFi/J'
        b'QilT1eRs2bpYLQ+74HVYk07Cb6DVqECgawi3wK2MW9Q2a1scQQaHgVm6GsePgeemk/U6LBZu8IG70kAtkMPdonS8TjWxV8HdJozfxWXs3+GTmu7v551KPPEsxtp4cuCB'
        b'EiAlVulaieCAKDh1FaxjUyx4moIXlxYxZrR7/GzQwphWPYdFseexgqauYULgXBZaivxT031T0K0MKthwPZIVmmaBXeR2gVboGfByiXmp69LSWePBOcoYtnHGzWJspU3B'
        b'FbBXBE4mowqhEoLCKBNXznQgX0vkIBMbsIWoA71sAzLwo4CL7FUr4FXypHEZ4CjWJG4Brd5wewCbwAFgAzy+kjSRb3yuOm4RiVoUXA2PFk5gfJdqUDtKSRgBHEJgNlpp'
        b'SRSBE+A0uTLJA27BAaJAD6hlgkTBTcGkPr55YDuJAoVDQOnBwzgKFFp4NzItcSDaYCCSEwnjZAu3WFpzCS7ENiaW0fEH0vMMLUxKmKBQhX5QnkWBK1nE/t8eHiZyWEoE'
        b'sYCOv5GWZyiKtMX4lACXfxBsr8DxmuAJUMvEbBqI1wSvhTMG2CUELl3sY5xX9lXkCoqJYra5MI7EkMLxo2CDJQ4h5QiPkVY0ATKuz0D0KHjWlwkglZNJQDEbWBvh4y8c'
        b'V8DEj8LRo8xQM2Gz8yUTcpj4TuDqhGEhnkiAJ7AfnGAieZ32MsJdhGyaA9igtQR1ARlnNpDCY6Ul+09xxXit+XzznJPZMZkw0DQmKuO9c8aPlmWZxm398IbJrXnOdHti'
        b'QtrX4NMM35qwLJvXdn+sX/uVqNljY+7xqrc++2H1sjW3Vz1l2acVdj76euwN1rrrCy1sL2lpRV26nbYupyzx9sOXgit3/6Jz4L0U8NGiiMxXxfeKLA+9O21r9fevtfh9'
        b'7hrwj+VX33hbtvHwlbDbwCXpJqt4y+tT/A9+xTuz9f0Tt68EdC1eubMlY4tFWOVly4y27yfDLyfPmVCkSHVfMKn+ZPbPRt5LzO55G3q3+ByI6uic3P5YcORdu/c6ve8+'
        b'1hrTNn2dvOly5cH4xoinN8xMUpZ+/JNn/Fc3Tvg/uX3z6xbbKxFOB7vEHUeeTigfe/due+TcninhrJMTdd699fL71y1DCgJCPJtS0t95StM3Pea8m9Ezw+zkN/8OTx9v'
        b'sHHKxn0fvP+k1fHxzO8++3ravrc+emnc4S8vB1CJsY8WTR4fVy46mdT6Xnnqr7sV7AdL68ot7i7a+MbExk9db61+acbFwx9cer03PbQ3fRa9qOP8e2VHLS/+a0VzjRX3'
        b'MPerrFbxzC/mTZux872XVlw8+Xhaa9Wjpe4flGjx3k98+qPRlyWnrY3DhLZELjWCHcEaubQNXsKCqa0/I/FugDXgoCjN259JNyhj6+nDzqlwHwNBbB0XgJno12GbVgLZ'
        b'66L5Zg1oBgcI7VcVPAhPYbI3YXq1nx9sYLB0S7CNq+sB9z4lHJgbjbQw4I4dhEaQ23Hh6fmFRKb3hxdhL44+ROZKbV+4E22l1sHzDJbRrYdmj7oAHNGITJUGYvZ4X9is'
        b'FcFQvbXBzQmiTL9sLmM0mhvL0OFL4HEuuorMofPjmFnUCh7kRlqBZgY2OrYUHgZ1mcGpOKjdSd0y1lQk4x9iWuYwGibXSTTXNBbFwVVvY6Eid6UyEMjxaXAnSlXPqCwv'
        b'yng+JwLsdmVCTTROgw0kltLAjEqZ64Dz4dgH04kJbrAxHLajEjRzKmUOjgL5Kg64CLaEkDqEgEZ4iVQBAy34uSezy1bC5kxmuzIObAhGqSnpzLRq4M62QdWXwdNTydNZ'
        b'gXOLfTQxCOb54SgEVWCTOlQAepRtmli1eB6cz6JM9DhVieAFcnWQYSlJJpORdjna47Bt5sIdDGC2Gy2ejfiFDESzM4+HLfAwB25wgvtJ32FjwkTC90amJAPUcWBPObwI'
        b'mo0Yxr8GuMkL3UI996PJcjdlnMhJAjXg2FOsf4F1ibDOJ8NvtChyaO6Kr9aBpyaZgYtjSHOiasALuMn7F2J4AaIlrIQTiea3c8xDnwVXyCsdmOMocyooggOuZvHIexOg'
        b'ZXcrqnNyCj6QEWEOjlUYc8ARuBXWC43/IvoLjLATYWUY7wWmBFlpqpYTMSUKkp7U/F1fMdwXfQuy+jWIsvFKCyFtIeyj9MySWQSF0EARDi3hbXHNcfJQpV0gbReIU/Cp'
        b'2OZYuRuDS2BgJZ71wNFLIYxVOsbRjnEKfpzKzksaI+cp7fxpO39SHM6WjLJ5K3ySlI4TaceJCv5ElYOzzKNlloTbqK9y8pWukWd3e3XNUTpF007R6KQhNhv2POrV4SWP'
        b'UrqE0y7h6KSJyl7QltycLMtpymzJRCf0Rp4Q+MmM5IWn5x+f371C6Z9A+ycoBeNowTiUaKRy9pc5yKtOLz++vFdfGZBIByQqncfTzuNRovFvJzq5ti1vXi7XVToF0U5B'
        b'uIIPnVzxL5WNQxu/mS/zUtr40DY+Em2Vhc0Tys4sSGUtkCUprL3R56Gnv2yZysFVltQyRz61e0LXbIV9lMreRTamJQP/Gkvb+z3R4XrZPqXQQcptMewzpoQB8hW019he'
        b'F9or5p5X4h2vxBuJt8wYhEtqpHIRyjy7l/aW0uHJCpcUpUsK7ZIi1VH5BHULaZ9oqQ7N91J5hXXPQ0VIdVqMVL5je51pX5IgVHkHdtvQ3lG9CbR3LEo1UQWG47vSfD8F'
        b'3+95ajvoayRt749/R9D2vk+MdPBD6KgfwpSytGlMu8cLvsPDISYC6JBUJU9E80QKnkjli3pUYxrNEz50didNbOfUFtEcIUtl+pZEV2VhhxsyFDdkssLaF30eCgPl1ioH'
        b'd1kx7eAnX96r1bVOYR+nsneTTUV3x79n0PYBqCm9cVN641pg025hEHpcr6jecbRX3D2vCXe8JtwouBWk9EqnvdL7m3L5DT06PFXhIlK6iGgXEW7KkO4U2if295oyuHss'
        b'7R3Tm097x5OmDB6L70rzAxT8gOer7+DvubR9IP49HbUqak38HDrq5yCtmXGPF3qHF9o9vbeCDstQ8jJpXqaCl4nZqYSoPTNonqeKaU8J+hmk6jBkqJnAf0TNpMamBuaa'
        b'35pqFmNdiITq14XMznpOXch/XUkixju5Fr1g6qxxAsUZYimpCdxtTvZ4q6kFmiS08y7BgRy12CRE96hB7zVt0B/v/k19bPqK00m8exe8++zfsWpYmYZEtq/EfFV/sE5C'
        b'1n2dueLSkvKiwueumQLX7DvWkJqRalUUC3BR+VXVlUNr9scrxZ07L3jec9fobVyjU5q28koqyy8RlBYLSqsEpWK0Vx8XPE7Tdn+iXpV/p/7AC7w7tFL2uJkKKosKS6sq'
        b'KgWlhf9pRTbjinzL/QMVeRdX5LymIo7qiuRXlVaUC/5Mm8xn3pXe3EUVhaXFpX+gC72Pq+Sh6UKeuEpl+eIqAVNSwZ+vW3F/3YqWFxVUV/2Bun04tG5umroxJf3Zim3u'
        b'H3WE/Oz5q/W3oaPOu7+PVw2aF1BnZ0r9k6NPZ25h0TzUTZ+7cp8MrZwTmRJIEYL8goKK6vKqP/0e+4fOc9fp86Hv0XnI+PuTtSrpr1W/9v65a/Xl0Fq5D1Yq4lfZr1Ec'
        b'WrNBFRvAKJdSGMneT9Wwazhqg3yKTW0fpk1dwyI6VmqEjpU1Qo9KrWWpdayjpj0bmxzNIF/7GY4EpNYsxpGgmPW/dSP4efoIPS3+R4bSsvlFqP0r0UtAo2jQgKpEg74S'
        b'LbZVAtRtyiuqRqp6R6h7NX1nKKS/JHE7V4x3zHPe7j7wWkRrvkX7Huc6lvZGm4iZlMdRDmvmbiGL2SIeBVcngbo54HTAINUrozSYi7qaaX9XU0tRNzCRpVN/V9PUeMAE'
        b'v7ikqIrs37C1NBap5k1jUfaCljgFz3uQhMdlJLyhwh1mgCKG/n/gXt9gAa6EUpstzpyG5DdzLIgNP/xl4NWL7Oe096BqWP+39h6jjRXUOT4/spgtxoDA/B3X++098q+2'
        b'7ym1ceVga4/1GS8v5+9x3uIs3RBiRDUItOSBbv29ZS/Hvl/BlIrj5Wg6iwl84bcNQipf+d23KVb3HFt1z1mAeo6nj6xQHta+sHMh2jBkStDPEJsQ0onMWM9rOfQ8Vfh+'
        b'qJVIKe5RNrgLPfvwl1qJCNkMkHJhNagXkaAWXBPWwiQ0ULvmkJQ8cBxKRD4ZOCWEBV8oAz3x1aX3Zu1jizHZ3o2OTw68FvqjduuGPe2bhDuDtpzZcsjq1hd5GQWp+eyz'
        b'Ngv5C/hZ0s8CtUIWH+FQL27Xm/BBb/+QHG0zhXv3QAt+iQ4rzUa0IHlt6cxrU3F1+6ZPY3HNfPqoUQ7GLDPsvjn64aHATV6osA7BH9OQIdPFaO/3uer2NX6fC9VdagZ+'
        b'm3r4pY16+GsniVEXJTJJcMmixCW4KaU29vnfLE1oQf05fcS6koj9psSMjIcWoqGYpVggriotKxMszS8rLfwd+HE0EzPtjOwkAgGFZq6idFGj5K0Zu1SadqiidOOun1hi'
        b'PISbQfOB14Jb2/e4o0WqtmkKf1OCy47Aepelgt16t3G/fT0EVi9mr/Dl/2NxPXtM4dsLbKT8yKaF6P8+1puzdgZO69yaz/LhWHUb1kwLETxdFuyf59p1amv7r6/X1m1w'
        b'rnN4OTP/dnFCr8nHE29bUfHn7PTm7hfqEq3smOkOUAqu+AzSgBqDC5yJcJ9aF+8Lt4BNPmpNfAE43o9brvdmbHMkbH+1Y0B6qYUaCcwEB4hKuBQc8h0CaU51xZAmWA8a'
        b'SNkTKuBFeBUcHMAZCcpYCa8zPhanYe1CUQrFwzArl8sCbaAWniHa6jj0F4YXMlNAF5fSdpxSxnaBdRVMoI5zQJokSokE3aDLV5vi2rPAWXaJUOvZGhNs8TXI2Ea3VDyX'
        b'vO0BobL/DBnpzerRtBJN0Hz7xjV47ApUdk7SUJW1XeMq/NVZVti5kPyhshNIw/D5teSr3K3Lb+D8Qx6/MV3BC5Rld87EFv4OkkhpvoyvtPCmLbyZbHybNu1m7SbdFl1J'
        b'AnYSSG1IrU9rTJMFKXluKJM8+45FkMIiqP82kqohJjOjSBmjWswMsjWqFGoPFqf7n/wXPI8spfp9gZ8paPy35A7c2TKYx7IYjXV7EL02thOq/AK/Sc684HmVOB5UZZ0W'
        b'frH92+f7uv2b1fvazD7uvjazi7qv279zua/bv+UgUytpFqHRn8cCjKhhVNhMq6uwnVK/ychC3Ni57GHs12zMfo0P2pSxZc007M4g9VYYuSuN3Gkj9z72DJaRRx/1nx8x'
        b'YbXHQElL2UPomSMwPXMkZmeOxOTMkYSb2cpRMl1lKlSYCpkMVjiDFc5gFVmTNIwBGpM3WxDyZgtC3oyOhAR6cJ5gnCcUZwnFOUJJhsHkzaGYvHkMJm8eg8mbxxDy5sEU'
        b'0TGYIjoOM0THYYLoOMIPPThDJM4QjTNE4wzRJMPgB8GU2FaEEtuKUGKjI3mWwXnCcJ5wnCUc5wgnGQbfBTNz8zEzNx8zc/PHjqgGDvPAj8EZYnCGGJRBV98otI961sGK'
        b'sFwriLJaNlY2tj2qM4r5VpPSxzXFhNJ/4MCQQRNgrg7Nwjthj8aiRR/sYoNTLHAlxX7I6mau/v0tFnj22owwU9Nu5DdSXeyhxlTERsmoxrzGoljrrzRPY8pFOwy9zbpq'
        b'gzRbYqSlO4qRli5Tuy79YQZ0WAQxQDXjFhqMqJneM67RQntpwxG59dXPz+8yGlrTQjtyD3NyF5PNesOuMyDXUfjKRh30w+8yPYImmhPa/Tn00E+hfQ2L8G0zll5GNcY1'
        b'pjVmNRY1/GLDQosRZRr21wX96DbqFXO6eEjWpU5oqBMKHYjhoBaxHTOoMUTlmeAa1vBqLGusaqxRuaaFliPKNdKUS0pt1OmyGlGulrpEE1KaFSpJr9B6REnG6rblD29b'
        b'1ErsQpsRrWtSaEx0QY73jdUzJPqVX1JU+VEouniITJYgGJoDC3Lot1iQj2S4wZIdtk/LrxLkV2It/5LqUjTtDymouKKSyV+IkgqqsJattEpQVZlfLs4vwMpJ8TAztpQq'
        b'JClWVKpvpblLvlijakIiZrkgX1BSurSoXF1sReWKYcX4+wuW5VeWl5aXREaOtJPDWqxhD6iRUMdNyE7wF4yvKPesElSLi8gTLK6sKKwm1XUeamXIZuClNvYwTg0NVQVe'
        b'SvdqaTg12P1U78TQUEfDpqH1v2DT+Ch3+GsmDT7M1rBfZF/U3zD/kbmh5r1gRRXqHINf5qgaKdyDyIsv9BekECiksALVqLwCK7JLxVX4zDL8fuap0YCiUbYR6gqptaVM'
        b'nUboUJeV4kqilOJqVFx+YSHqbM+oU3kh+i/IX7y4orQc3XAwHvI7exhtauQexiijOhZ9Aw2wY1w6bBwcFTdZY1wBG+DONBLBdkpyWkZ//DlwHW4zgIfhOXsS+1YP7oCX'
        b'h18Pzq1kikAXqi0Dl8JtemuWLiG2btpj7OEetOFP5oLTjpSWJwvtWDZyiKFeviiGIQoFe0DtcnB1FVnRDGC9OMsPHoFn4eHg1XAXxfGnTKLZbmAbbK4mweuawKYZmNLP'
        b'R8NSgu1CJ03xm8qm4P5F4UItUL8Y9hDOXngJdNn6oHEipuBlcE6sA8+Q/dwiO45VKENXUVbrUU6RmMGRoAPIBozqpsCatMk4rGC5vS/clc5E7ptcoQPXw31ChhF4Lzzm'
        b'IV6ihUNianlToFZPULr1zia22BR1eS/V0r1TzmTAQN7VEs8zb7O3BFd/asD/0Vyb3n6Tk+ou0Z1ilrqvvHhiV5NL5z/dMi0v/GzruvFQcuxnXz+4Yr1Omrl8tnPXyicd'
        b'rusPHVy/gf2BmfidgFlhf2v2XvtNsNu+i1O+Ld/ikbmw5etL25y/V46T1wozvmsNb20Cbl4/dmx4vfNLo9wF8p5jtv5xLY/sllXNevsrpxn1fRHXQdgXZSfmfGc706Xr'
        b'p8a3ro8HwZ+8a7+CFj1Zpl/xyprHn3seSCk+cHj1yrXbai7/xL396of2JdOWfHj81/TPFt/def9xVtzrV2bs+vrId5/8qzR7g3JG/JyQXO5LFq+tntOq889z866Pl9dJ'
        b'FzW99mnxnUyXU2ttmnon/NRntNgg64LvNiHvKbaFXQbOa2GTV3gErGeMXg3diYIuHR4JUpunRcNGv0HmafD0JLIldQVd8IwIHoUHB9mgoq8H4EGyeVwDt8/3SZ4C9zHm'
        b'c9h0LhJsYEInVsBNojLQNth4DnaCVrUbfPZ82IsdPoxhl9rnA3t8uESRxHEceEXEWBkLi8q0KT0eG7RPBBsZxoKG8dWwDolfGajXLAWtvt5IwAfnOJPRSDlFamWJutBV'
        b'nwBYi8QzHewcI2f7VomJYdoYKEUduc43gxjsrTNTm+wtDSEtle+6xCdVB1xLT2NRXGcWaIW7ddSRS8FJBzVbAHaBwYwB7JCUHGIWFWQzQW1IBrcb8bEllsgPSeHgAjcZ'
        b'Xaemrrw8HRzq1xmAnSJK24JthMYVE4sSHAcSbxxIUoTDNTKmhGZzEsF+DtgND4NaRp26XwvswBZheLIAHbCeTBjGWZz0ZCB76k8Rk76NK9HlmEETbfbXFuPQvTjabYDI'
        b'jwQQxTzoE8EZHVRqRyXRDPjAXeXY/i6VMSImFsSwP6pp/ay5TBxO2GM+OBBnpAUTB/QMlGODsQBUIbA909yWuR2S/FFB1w2LhPr/wX4Pk1QJhjkKE2MM66Hr+FDzrwRm'
        b'89eXNINF8Z0YpUIy64Gtm8I9SWk7kbadqOBNVFk7Nq7DKQlMSpzSNp62jVfw4lXWNo3L9q9rWCerUlr70ta+Ei5jERbdHC3nykuUdmNouzESXSbf2oa1skLGyRptNVBp'
        b'Kp7VflGDSMZV8txpnruC566ycZDypPPlHKWNL41D9bEsx7G62Sq+bZtus67CObh72rmZSud4JT+B5ico+Al9HJyDycccn5DjU2r4+Wcdibf4M5Ie2ti1WLc5NjvKdZU2'
        b'QbRNUB+l3d8KEb2hykFN8XBkzeNxzR0FbSXNJU2lLaVtFc0VSscA2jHgnmPkHcdIpWM07RjdO5l2jJNy8HPEs5irmOMTcnxKDT//rKP6OUZLeohe4CpZwR1rocJaSGzz'
        b'4pSO8bRjvIIfr3JwJgZ3zkJicSXwJFZxLh4yN1k17Rmn8My/MfGltHvjZ94ZP1MxK085Pp8en690mUe7zMPmdxL0I8bm4MDRMVGXA3W5iYY60ISFji8Zxk2w5ty05k6w'
        b'07npyEJHNY3cILMjLBc+h+0RQyOnsTZ6jt5tZ4Cu2kZpfOLF01ksljPWFf2xw19maIQX8AN6QdQZ47g/Ymekhsu1fhOUHt4I/dh0tMEQk6MQjQQ6UuQcJF7+KRskbEJS'
        b'eeo37KKeVdc4g8FGLZVm2sOc14YS13EYlLyGq8b+/jc4+XNhf/+fw8lL0CbsBfaw5nwGpH3xfCwDaX/nYXngtYgX81o1kPbblMd29t8F7kIWQ3nXBS+P16xh6HByxqBF'
        b'DMrLngVrewzrAOKCsrmEUe430O0puX8K3X7OWyYaDAa5E3P/D0HuIe7qBL+qYf1P3dVHBD8bratzM6pjcFfoSMSyYb/4xEgz2Jlte5p3qi84ns34teETmaAlKA0DMOAE'
        b'2G4wFuzUL53he1BLHIeK8bpQwsBTl5K79gRhiOonkfQj+628l4t2GBqesMn/p0fSDkOPrRkyx2xlxpHlHr3GmC6hivKM1f+i6bGQ8xTvjOYsShlelQE5bjVYPyDKrbB7'
        b'ihcuJGp2Wam5G4e5kYAucAmeNoRy4nIyBR6DtYN6PCr6Ojik6fJG4OxvgLsDy9Yrz9sj+4H6GPUgmI4GAR/TalimsWQ5NI7di/8kRvSpSkcR7ShS8EUqD+/fwPJ1fhvL'
        b'f4Zz8x+pcrrBELfnabm/D+z/teg+dnsWsonjmxvaA3Rp0H14HG2ijsKrCWRDHMC206D7uvAK6FlXXLr7GzeWOAwlrmxPIzYbA9i+UyVG97/OSynIyGf/gz8U37/nrPd2'
        b'zX41vebv4H8DrXoLtyr/Wa1KXn02pQH743NZuhjdH+XA42Bg/zcPupSz++iYv9az+8Efqu84/N4Xq7tqQu5vGgD8tVYAmA0ULTYYjhsymWoINtZTjDGA2ptZu4ZVo4PW'
        b'YC3NdDpcufhfYf/4+cgIhdjEoipBfr/UNVhp/GxV4qLKomJGbTfCdnwUbV9lUVV1Zbk4UpAgiCQ+4JF56veXJ6iYt6CoYBTrt9+1NNDKqMYWMPDYbC2iTsBoTs6kaX5T'
        b'pyWjGXQnR+3zPMjfGawP1VsANlhVk812DbgEjoiG6fOw8qpfdcURo8nWQAfuBGcDSs8WR2uJy9F1uY+3HngtkthRXdpzeI8fWiD2BQUFdhVvfLLAJnKGWaUB36Z7ve3W'
        b'ovgn7yy+NK/dfOrmMv0CT1HlFUs7TnOzR5LszbTPIxfaLOT3SPOjZSem55Vtnj9GmvPSXLCzUMfi8qOwHS8atpRSK29bPYhPFWoztgG74Ln01UDa7+eIFTWWBUS1UT0X'
        b'ntcoRByXqRUilQmMrqVJD0oMRCW+jA/jIA0ROC5gzAdOTwQHsHYJbAa7GO0SXC9k9Ad7QT2QivqVm9PgZRZlkMuGpzK8n+IQD6C+OHf4ggU2wZ39vo9gW+Qf4f8YRFpo'
        b'gAks1B1rpe2woT4ojUxOy9WDvQqvS26S1bLxcrcuodI6lLYOxSRqI7b8LDMRs3UedyNb6Z6itE2lbVMVvFSVrbPUU+bW5NfiJ9FRWdg2RsncOn1pl+A7FsEKi2DCZxyj'
        b'tI2lbWMVvFiVteMQLxZdZkkjaPxvmyDoDqxr6iltHrZB+I3nzMaT2mrNYlaU+0f8Vv6yCW7FM8XElRSzp1CzGlFqq+H/GaPRz+dHndOqRlqLVxT3Uyz896e4BOaezznF'
        b'PcN+8xdnuZYYC5QpDTcZ8vBSFmeM4tWSrt4d9Rvyw1x3zH19EpRofYZFABb1/l3t2fOnCtmMWvIEPAHlhCxuwHGUsoWtYH0Gd2UEmxnlDXPAVpHay9YUXlfzF4DLoGF0'
        b'G0+NCZ4T+xm9Vt3YZHS6qEdn9kwWZed0z9b7jq23PFRpG0jbBqJRZu3YuFZh6j5EEHjWOGKYwQf2VL93/0I8ahZpRs2Emb85av6yYRKBn4LN0PfoiPOXFs3NF2cMAR01'
        b'mBO26WEkAgI6MhKBbg0bjSDt/yHkuFnI/mjeaJBj/yDCiG6hOlT9cw2hBA36XFSVj91a8hmT90UVS5GIUVxZsai/3L9q/DHXqJs7EiOTBHf2xXDkompxFYYjmflAXFVa'
        b'zvgBYR3UqHgio5ca4jaBYWdU+GhYpmbo47pW5i9jmgs9838APepnVIfiQXk0eN5woQbsSdEQuYwQaiRQSrYTbg5gl08qm2Ilg92z8Qq+MZIQhKpCJ2Xl/LvUaKnRYi7F'
        b'bWJVXStn4hoYcqn3PS0wybvvrrl2VDZjKIMPq4wn+2SikqZkgB0UbIYdYF/phX13KPEbKPFJWO3eSUHGINAwOir9fu3OnU3WgYF9xkdSd9iYcjgTvI83aG13Nonvarr8'
        b'dE9n8qK93gYXglX7r+z55mRsXu8bKdPmBE59Jf6tvxd+9A+bbzePt6nK/zBz+gvXXrd55+PCE90/ftv5sMsw9JW1q6YHfzzhtaMGp9s8Xk163TbxldWg+vxN4+q7fYnZ'
        b'82smbfF7sfutKcdzP/e9G/FEVr7FbI6HTfC1m/onr6Z6WJwLm3O1qWJ6oJGd8t+nltz8KrDwb/qtniGv7jG29zH/d/onNf/4p5be92NUfWfUjGxgUzbc45M8JmZAxBI5'
        b'MDwR+9iY3cyXDzZkDCaKgBcmMVwHh6B0hhqImwS2DhazXMBpEvkLygRlPqmsTA0yZebCFH3GE2718Yab4bF+LgO9KDZog82WZAqPiHTXYFN8HLt+EDgFDgI5gepiwEVQ'
        b'g8E4sNNhEBjnBaUMdnUyBkdVrYXbwQm8ABA8DQm/HX8G4BEMJpnWUROOrbQaZTZG58lKsJHFrASVM/+snGZpI8mWusm4Skt32tIdZ3SXm6vsHNrCm8Mx47FkfB8HnSMJ'
        b'5PAEH55SQ86NdmCwi5Fp2pSjS9vM5plym+4EpcMY2mFMvb6EKynEDL1DUSdr2/3LG5bLuLLJsimyKZ26SmshbS0kXL7SwvpV6A8L2z6KbebJIEwl6FINTuOpAZhkvCbj'
        b'FmOpMUZjPEkSOWAoxvMpNeTcaAc1BDP89ENrO4kBAUleNLBM8OW86MtNCNR5MYSFjtDSKjGcA8O5iVE6MJaFjsxqrDdoNZ6v/buirR41CB9hVukqLNs+o19U4BV6I6VB'
        b'R2bO/MPoyF+2bOdQxMeEIEFk7dbT+BwzFrHe2piPryy/vCQ7qUBn0Dxu3j+Pd+Ll3JBZzrdxtnG3aW3TRss6NmPDVJ+GxJTNpMYULfRmNeZombeo4dZQNZwaXrE5We51'
        b'0HJvMGy51yXLvc6I5V53xJKus1ZXvdyPmjZYEf/RWu4oy31CYSH2ai4vWjbUKQCb1zCmPIzlUUFFZWWReHFFeWFpeclvcJWhRTgyv6qqMjJPo57JIwspFisqBHl52ZXV'
        b'RXl5vmp/6qVFlcRcmViqjSgs/5mWaYKC/HK8vFdWYBPnfofHqvxK1MsE8/LLFz5bxhhigDRsqzCq+dEzJY/fklZwQ2D7KPHiogLyhL5MK48qewz44JdXL5pXVPncxlSa'
        b'7spUY8Bjftn80oL5Q4Qg8kTl+YuKRq1BBeP8298O8yvKCtGQHSRSDXMNXpRfuXCYNaHmpYkFDAmAvyATe0EuKxUzNUBy4fyKQkFkcXV5AeoeKE//Xjdv1IL6a1+QX1aG'
        b'3vG8ouIKtYSm4RZkOkE19lLGpoD5o5YzuA89syU13kSRguEe/wNem/33fZb3prqsecHzRpYymDfgd67H8w0SZ7MyBWNCxvoFke/VaA5Fg7CwqP9V9ZeFuj7TS0Z3Jh1f'
        b'VJxfXVYl7h8imrJGfeOeYgH5ik02R1RuiMyr7pn4URajnS/66zkk9iGisMUoorBnBmECBNcTEiZbi4MrkShaQSFJ5wq4TjzjAsH++Uag1WDpEhbFgjUUbBHCo0IWSYOb'
        b'wQ6WEJzxyYBYqQV2sRLTjKqDcXEy1lh0yWRGivaCJ3z9/bxgTYB3SjqSqY9nL4Znq6YylnGg0VsvwnAWoVMU68KjQ+z4mA3zlGQ+2NtvWlUwRxe0T7clcrV5khEOn774'
        b'zuw83zhrQ6oaUz5ZhpOI7QNmeIyfETwEW3yFfqlaVIyPNhK068yJHeAceB1egWfSfGCDNpJCMPHeEXCNlH6FR2Kme33lmmd4cZ4fQ7N8iEWo/SJOp+eVibXtmJPnYknQ'
        b'8/ld+nmGJjHljGQP14MrU+EhNuycjEM5GcAuUxJ/hKl5tB6JG/VqeZ7hphJnqjoKnfROg62E6DErmWBaKegBdvjgrYjmYVBCsm9qmn+KH1oo4WYnWCc0XOIEG4mSNgzU'
        b'R41Q0u4QgsvC1PQ0cCxbvZsRamPKtkt64FCMR5JQl/AZLq0sZTgSwQbQ02/ihDpBHekd8IA5OAHOL8ZEiQxJYgmHYC7wADhXxpAkFvC1KC7mSAQXA0iRM5fFDmFIBFdM'
        b'TTmW4KQPYVesgPXpDE0h3JCDNkuYphB0gvOEtBFuXDTJB9Zw4QYNNRjhKZwNDjG33ReSA7em+6hpwQhTYQVoIeHi5oDNYLfPaGRfQAo2ErJC2JklNGDCgJ2yRpsC3OSx'
        b'0egVYm7NGfCiuoJNUc4iHw1dHPFQ84VXiTHo5ADYOuCEBo8FsCgL7IWG3t8RMjSyEhbC4/CMCLPCMcyaBeAMuaUbqtdesDlARDjhsCYY9MIWcsv0dLBhgF4TSEBdBRs2'
        b'FRlWM37CoCMND445OgN0cIRdcya4RBo8C56rFIGToAl0DvZ8y9CrVrP0XfVOgPtFGiI44lYHG4oYnszWHLBT5G9TMUBrRngb3VHdcHo0GhgbwVHQ26/EUmuwJsJ28sBL'
        b'QK8vOBybBSVYxIOtVHkY2EHIMN/KIiNm8dj0PMMavg/DUjkfbIHnk6vR8+zJ5FJsQ2wveBBcEepXE+q7raC2SmxcWQ3PGMIzzhEmoBZerEJtvICTshD1EWKCtNWPq8lC'
        b'MojhuWotCtb72MIjHNgKDpiTDgE74bllOGceGurqzMuqluhVGhlrU14cLtyIWUWr8RYzAB4dC3uq4TnxEsMl4BS4CnaaVFZzKAt7TvhUEbHFBfsEsEu8pFqflGMCz+tl'
        b'wrPwDLo1umJnfyXi5mhrVcRUY9MJPTRLrtdcUA229uexKOIkwAughuQaVw4PkkwnyodW0BGc4nqAa/rVWMUHtoBacF5TGNwIzqF2qYTnUBUncCKjULm4+dA29YITkA/K'
        b'uQzNt9qUqTYbnprJxLeIEoA6A3ihCtXGUM+oEnRYa1FGa9mgZy28QvrbmjjYkJUO6sNhfRbcCfdmgZ3oPYJmFrywcAmzZtQ5VoPTVNakSbiVN1H580AzuXSJIzw6qGzY'
        b'Ak6oC58Kz5Pe4mgOO8TwgkllGhrabHiE5Q1O2ROdjHb4fFiHJj5RQHpaZg5eIqag+e8K2pRjdYwvngZ3pKTBWnQd2JijJ0bb8QamNsfhC06gWVuEg6azIinYGMQmrVGK'
        b'Wm0D7ElGU4LID40cHEHwAJcyAy0csG+RJ5mO315rR+G7n+DlrS5NtWfm6NtrfKhs1HHfMM+b1zRGl/qMWUV/jFP/4RUv5DJ+5Rtg51JwgkLVXE9RK6gVaIDvJmvA1Oxs'
        b'cAKHFNuFtmfUSvAC2FWNt3AVXmjV1HEPwlbmy0GHCyHdNR4HG2AdWooxW38pVeqXQnaHpX09lSyxNYeiHpvOPzlVVPF2vOkH1favnHar/rlm5mfKMYejvY0FLPNxuk+s'
        b'exW/pNZkH/e+uGBykWjSdvj9+l6Bsd8dx0n+j3YXttz57lSIR+xDr+0x//70wCu3bz/efTsT6BRULrt5ekXgkX880pproZ3gb3kz6syLn5sVvZy+iP35MTri64OhlQ7F'
        b'x3M/s3K2WN6c+qrWlh+O0IsWXv5u7OO+128IVreafBf+RmTvd7PvVbzxaOKHjz7bf6Ob++Se++27rsuTpjSY5uePld5Y5t02/hD75Tk7UkqtcsY19Rx0Df0wi2N6oO+r'
        b'fxvcfP/bsU2LA3/Z3n4o+O60d+PM/LeWHNx11OZOYv21vsl12SXxPzZLDx4Upi7PPDdprcv9uu/qpr77+NDpOPdtH9REO7/yadOTYxcyb3u5/yLQqurxHfPp2bvTDpXN'
        b'9nd1fPH+yb7k/U702Q/HvXOhLseg+UT0xtrZDY+br5fu/OEfy1ziY7oedS2Z2HPpJdeqCv8645enyudYXLV7+cp24T7rQzdfm2f41BL8cpUTdPqDV19eGGzVoz8xjNe1'
        b'Vjbj0QcPSqfUpiZmX96VGj6pdHPqKvm5gDVfz3pPESbOfOeavdccrdqADX9LkKmMeAs3lG/ym7uq1GF3xPnFH/6N2j938qeedy3/lSPyk39mZOT+y7r2z8L6rrLvpd7J'
        b'O/FT+evLQ1Luvlj8OEF49GRx0cuFbwW9ezHN/Z2SvUt7wdUNs9sLn97y7tp5NeCTHoPV7guNrxTtDJvxw/10B9W2NfJ/sl5+ZVyrSce2lMg6Vb7dOvE9/8eLpmX87PXd'
        b'cn7cZ+38eY+/drv8QdEtuCc81XfOwb9n5X4eG+M478Fnfcdsgx5nT/yq+9cXDTZ9FyD68NvA65n/eul08JdZHwq2x33QEPvNarft3x5Ye+jGw9pFO5yfvLveaIaYbRm1'
        b'N+fAGFYc6Iued2B71Af1Y8b0NL11QfX9m/PZJc3Hou/dSKu+GUMX71lR1LPgyPm6mUmSHya73Q8x/UpHvuw7lykHKkwmt4LVopnNt12zjx7+0v569dm3b86x9G0x+z7p'
        b'44/X7FI5P5E9LA078ZSdYb3tU5tLMQvjpzpO225aNuGbmm8/Mkmocdl1dprQn+FL7XZc6zPIXGcXPA02a1PmKRwgWwSbiPYR1oFGhxy4aUCQWQ5Pkqsng12Gon4LokyU'
        b'bAvqtCkzuI0DdoAD+gTndQA9cN90cKWfrHaQBlLszBjOg6NVA0TUQAa6iCOAZAZjCl6f5jLEfh3sc9RCExExYD8PzpEq5ujYIckiDW4RqXWYaD3fRUBkm8ByYlxfBdcz'
        b'0fjYIXDTOgaDQrKCCG4ZsLAfosIcy1QObHdCa+wJEkVwkqg/MIUj6GAUsx2lHJ+MdLizAuzWprihLHAsIYRg3wmgA24jjgIZSRrF5mVwkGhF58J2uLs/JsV8jVZ0NZST'
        b'a/WBHF4g4QWno8YjEQbZrrDTl/HzvzBpqcgHnII7zJBcoU1pr2C7gX3wNCnYxXbsFFg7KOQiE2/REm4g1S2NzSYw/XK4X61GBo1phH0AiXmH0QbmmotII+4Szwh4Fe5R'
        b'g/HhNmCnM94lBOigbUsHKwdcDGSaqBvlu4TFZ3AWHlETBMCTcBuD86MHXQ7rfJFEii6Ftem+GUVIKAngwL06CYyi+WwJbBUNOCoZuIK9GMsHPSyioJ67CLyQDdYPyH65'
        b'FHnYibClSi1/14EjGheDi6CZNJTdQlDPSNmwER7tl7M3WpLn1QI7wcWhkva2XCxpN4JLTDNvc5zGiNqom2xTy9pLwGGGQbcHHMpCsvYCcG2orA1PMU0yNwNuAs1g3xBh'
        b'G/aC80/dKcJT3mE3qrQN65cxzOA7XJnG6wQvrED9Uw5bhamMMQO6E1zPqYAbpzAadCm8pI+DPgZkTgKbcbyWtWxvcAaefepJdqjwBf0B4WynCTgTtQSeN4LdrGCwkeUL'
        b'O7T0tIGUQVtfcIYHBbBBpH5NWHpvZoNaR/ACGS6e8EyOiAneAraDw84BKeCkF4uyS+KCVvSyWpgKn0cNdhjvcUmImDA0kigd2M7WRUPs7FO8igfOmo9Wd2E4WdtjwAYG'
        b'ptjiC3rVjMMkcNiiTCTruXLQvNIONpEslnCTGZPDP30lH9aijQS6OZRyQUsilJKbu4D9oMEKnCXZMn2R3IJ2z2zKOowblzuWWDKCzV7EgQ2VkuGXDHbg8SfCwwRKwAvu'
        b'sE0rr3QZuRtq8c3goAhXppZ5NQZIJD4BdrJhu3A2w2G9BTbHEPOW7XC9ri9q+Qy2vZs96SDjYZszjkl6xJzxJdI4EiGxkulBh1An2AJ7TJaqJ0Q90FAEj7HBST8d5r2e'
        b'go1aJkCGXoaf0At3oRI2OEuB80Lnv4YK+b98EGMBfZheZf2If2qbmvzCwmfa1AxKI1iNhzaD1aydhQPsNMZiyGI6S1aCWT7wXyo7ASFgDu+K6s3qnX0jRxGTdatIGqe0'
        b'y6HtcjDaMJ0hX06+Ff5GlFI4Vek4jXacpuBP0zjxxBFoZ5A9jYW9wsJLniXP6rY5NqdrTm/+Hb84hR+TTR3sUsEbq7Kwro9W2ThL+TK3Tv9uN6VNOG0T3kfpWPr3Bquc'
        b'nNuWNS9rWtGyom1d8zqlUyDtFHjPKeqOU5TSKYZ2ipFyVc5uMgtZtty5c1q7fae9VFvl4i5zlRXICuRu8iVdnu1lnWXdk5UeYxhq53suMXdcYnqLlS4TaJcJUq50cpMO'
        b'Bmlw6E9Wk36LvlRfg9kctemwkYe2O3U6KflBND9IwQ9Spw3NaI4zttt12in5fgyvcZ8Jqj55BnJ4gg9PqSHnRjsQnGeUNFPK3hFjYbJQOUvuLOd0jlXa+dF2fpLxDy2s'
        b'pVHSKFmV0s6XtvO9Q4IPkRaeqLRNpm2TFbxklbXrCHDOwrIxfH9sQ6zMTWnhSVt4/gY4Z+W4v6yhrL68sVzCeWgvUDl6KhzHyRNPJx9PPpbalXrPN/6Ob7zSdxztO07h'
        b'mHqjUOXsrbJzVNk5tUTTdj4qJ5e2Nc1rmta1rFMJXI8adRi1m3SaqARuKkfXhwK3TkNaEKRycm1ZTTsFqPq/u3p2RtOu4Zrvbl6dabTbWJWLBzbfClMJ/brsaWFin5me'
        b's1UfhQ9WlLNXp6HKyaNllUrgif5y9e6MY/5y86HdQlUuwk5/lTCQFsaiq5zwVeggdOSb91HoIOH2xVLO7uRuEiPUJRujaQtCdDOTpQoMPWdIB6YqyOdW+q10hVuuJB1V'
        b'Er0Obpch7RWtdI2hXWMUpgJVaMS5NDo0WcF8UnMVM2fTqXMU6OM5F6XLzJWmbipndxkPDb0KpfMY2nmMxFgVPPZcQDf6uRGrmJJNJ+Yo0Md9qsRYWqk0dXnItEaIyj1Y'
        b'5eV7Wu+4niJ4nNIrkfZKRHVQ+YbQvgkK38k3pr00Cz91tMrD+2hpR2m3sdIjjvaIY86hx/dRuIzptlQ5u/ZZGlihx0YHCbuPT/Gw6TeeAkLGXIw+G31DXxkiokNECvK5'
        b'NePWDIXHNMk4yar6TJWVraSwvrixWMJRWdtK1kirFdb+cm3cnaxRRzVzw7zakc2RTdEt0TiErN07rqHd2bRrpMIaf8j8kXSLpxSmKx0zaMcMBT+jj0Pxo/q0KXvXlmg5'
        b'W24mZ6M+c88u6I5dkNIuhLYLGaUc1F2k3AfWXnIejW5fpUabSWjV+tWNq/EXF0lV4yqFtRf6yKYwv9Fpvl2bSbOJnCtf2BvcW6nkj6P54yRaKlOL/foN+tJQWbDcosuy'
        b'2/yYbbe4t1CirzRNpE0TFaaJOIdRg5G0SJbQMl9p6kkzlDLorEmDiYyrNHWnTd0Vpu74jHGDsbQK9+ZApWkQbRqkMA1Cp++ZOt8xdUaDTXOxFb+xZH9FQ4WsUGnlQ1v5'
        b'4CbFgPmahjWyLAZk7qO0zFz62FxLFzzRGDQbyBKVfC+a76Ugnx8f2Lmgydty0AFNly3L8HCTZzHk8ejN2rio7J37OOg3+dLHQfnwPIN2HDzmuZkQarj3EjyZyFpmiWFJ'
        b'5pyXzblJVjov27DQ8a6x5VQ36q6b+zRDzj0DFjoygLIlAyhrYNbKaowqawDWyqW/CzI/9+JI6POYf0OXRQaYPj6a0eWghbAWg9MqigGn1QD15FksFou4Zf4fHv8yX0D0'
        b'gNRxvQSKepEyTjDmCDn3dfutvAZYpQq41MA/DU4jQ4e9pv1QN7Fd01ED3QZqoJtNoG4MdFOEHYVTY1lsQWBuLpvaPgyiXqOlN4qdGjqjNQLK5q7VUsPco6YNIdLIYo8C'
        b'c+csVrsaDkW5Cd6br8YrNeZuz8aO+3MMZdSoUkOvg4rwVSOwBfnlo8Jy8zDCLihdRJC4yt/A0/8TqBmD96Pe1bu/et4CwppBUMH+ejAYL1MlDNijqpczuOroMK8gsaKw'
        b'KGSsYF5+JcElmQeuLFpcWSQuImX/MTM+0oBqVH44A/xocDoqfnT6XDVY2w9VY3T499DMP4pd6lIjsUunjOpwvL84IhqHtjeZ/nBnOtoDT2aAr0rYO6oh3y6hHjwNZGA/'
        b'gcySwG7wAoMWGtirITYMnsGazCw1cMiAhivhUT200e6F54iu1ssctBELQJ2kZArunQhPE5VxTK7B6p9ZXhRlmmf4NGgJJcZzYMN4XpbR4iUcim17ZCqLSrlWnUxhDsTD'
        b'YLMPkGNlTQ3cnYVRvvQ0soubNtKb7gI8NlT5zckxgkdwgDKiZ14xBVyDPSyKSke7fdCRbgI2MvyQLwp+oUxj12pRgXlF00V7DRnVtaopPpskm9jMpN5fPlabylu/ICJq'
        b'zSwmOakjnqSOK1hgPYGSa1GCPLt9OVFMGLMouA9cCUHTVTC1BLQFO8+tTkRnHeAWo8HILazxS02HezBeGQB3pqiB4GTc0uAcWzQ5OdU3lVE2wItwt1EqOMclwDE8oh1U'
        b'Fj/S0+QZFpnwao46XvfalWZMvO6BaN2ta0nAbv9kAkpgjhjQOgjPAxvgCxjTA2dgD4EeQI2302JwcBQElYFPvTTXgg3gmt4acBUwbz1/MXv1GCYer+Fba8LUQEH8AqYV'
        b'Xy2bSp3zXcSm4tevVPGsoysbsS88ThFqkb6UXAwwWQZGDtxg/Qq4rZJgBD4TJ4ITXKxbALtNViYKyIueAlrgFoadJhn0LIdS0EzKgBvW2ME6CuMGcPO60hVwJwH9XEDz'
        b'fKxRQQ9fp01x4T7HMSxwGu3X2xiWthfgflg7KFwbwfwmmM+eD3YzQKsc7eg1QfBgayhWPE30Lt3pCthiKzTtr1Ee2dn4Qvl7gaavpEw+e61MdObNiIwO/wQnWeLFaxOO'
        b'Ug4mfhLKphOHH3mU9M2EaRm5LeGP7np+MbnbL+vauX15qo8f/Lrs/s+v/L113e11QT2r8355pTIp+kjZknWrusN6PpNfZId/svIl6TffbjpwvL54gdaEsic9MV1j3nk7'
        b'OK843/vbU0YK88d+1bt+mXbkH+8eWPDZbMOrS97a+tlLiV/NaIpZeu5y3207w8zad2c1m29ue3PikaZ53yeveEl3jfb43a0Z4ryvv0tpiflk2WPOQrD/4ZXekoCWnlXv'
        b'f5L25NPdTaE3v/24Jiby0vbtO4/5bv3hOMdStfmN8NjvVif/cCJAeswqcvP4ianxl080v3T5jRzdJvMvW85Uhz42y+7Mjd913PTlg6k3xm+pkHN3TH6UPfmFl3aEeBe4'
        b'Z/8Yxi9eVPit408+Yd29FmWdjscm+9VL94RJD84+ubHmyx8mraiceGeX8K5MPLvaf0fovX+98fMLHX//9a2e2l/HvnXr6Kc2rm9lG/705Ru7VQ/WdmTtvbG6WkbHihNC'
        b'lszZHfnDyayof3j+8OaXUeKFRxtB4/LjL9J5L4d7T3311dB/Jb2u2t1+6W8XZLcED9772/WbU58a9tJNr3VPdL238FRW9anK6V9fjtjkczGprmdZ645/v78vm2vZq5v8'
        b'ev53Kx/Ma71wKNb8uH9yzhfTer5tqT9fv/mzlkKPxW9/6Pz+99f1wEYP04MNT3dsO5i0tvjRxeta3hfL/vmL0IrRtvc4FPT7UsW7YR2tH+ghKqFxoBbUDtLPxkRhDW0s'
        b'fIHRKNUHZQ/TsceAQ1jNvriCIZppNAbHYeeCAbLWMrYLaPQnyqzlYC9oZpwwuCJwjFC87gG7CHXN2ih/rFxnob68aQFWrrvDM0yEuf06jtjLarrzaPHl4BEoJWWDQ8lu'
        b'aBZKxhgjFzTCfcks0MNmwuDlAOlSsN5UREw3RH7eOFzZAQ7bH55Vs8teBg1o+gFdqbhi8wtZ4KovbGf0lc3geLxPqp86VQ/sgZcM2KjWbd6kuYxh41wfVB/yUHrgdIQD'
        b'G0gwKRR5qGKvpWPLfPy8NCGu3aCcYBr6QAplQ/TVLMoCbqvCCmtwLJO09QLYQcw0gDxNbXRtMoYDjpbNQieIrjQstYRoGeHudDRlo+XJR5uyAwcWgwNc0LoctpAXYu2E'
        b'FqP2ClxCelqmFqVtz+bCc/AYuUUm6AHXB2tEtSiLCRFYIxpsyKhjLeGpfn3ogDYUdoA6LmgBNcZMGx1fWzlcG2q+LIwbV7qCvEGPYsvRtKGgs4AoQ8ERPdKUOeAS7B7Q'
        b'RArNsC4SrAenhU7/95rGZ++ySGC5Qf9G6h/7g3oPtvJbaTfcgXdQIlFBfqGOCFeWx6L4tmrb8PlK6wDaGkd3M5vEqJ8Sb8xXumcobTNpWxJtytoBexqHqByc23Kbc5tm'
        b'tcySJEmSVJZOklyZtpyjtPSlLbG1Nc7iLZ0tH6N0CKYdglEWQkdcjG5hEUBbkFv4qBxcsdl30+yW2TiDjXR8W2pzalNaS9odCy+FhRepQbzSNoG2TVDwEhjDdC/ZeKWl'
        b'kLYU4iKC5VPUhumyoKbIlki59R27QEkitk8fxISO7dODnz6LJ33goLZPH0Gkbm3bR9mi6toJsOo1i/HFn6x0nEI7TlHwp6hsndq8m71l05W2/rStvwSTzNo5tvk0+8gK'
        b'lLbetK23JFHl5tmZXJ8umSAd89DBBT2ttb20qmG1ZDWjMJ0qr+6uPrZG6R6jdI6lnWOl2iqBm1RL5eyO/rJ2kHEb1kjWqASuMo5sgjyne+qxOUq3aKUghhbE9OdSZ8U1'
        b'HKtydG5b0LxA7t6tLXdUOkbQjhFSzkMcj49jGazyCpbrd4ccM+kyaTKScqUlKjuijAhWubgf9e7wlme1B3QGSBMf2joMewZrO9we6UzPEClt02jbNAUvbZi2Z6R68w/4'
        b'Hjj6SBfJx/eOVzgmKB0TaMeEegMJV1KksrCW6mI9+TMvdPa85xx0xzlI6RxCO4ega6bXG6ssrPooUzN3Fc92f2ZDpixZXqjkhdC8EAUvRMVzlqTL3ORcJc+P5vkpyOeh'
        b'raPUrcmjxQM9LM+aXJMgWyJ3VvJ8aZ6vguer4ttLElR8G2lSk74sR8n3Rt+s+dKQhmWSZSp7gZSlsneQaTWlyLWV9v7oGyokpSFFWiCbLHeWL+lO6B0nSVHy4mhenIIX'
        b'h1PTG9Jl7kqeF83zUvC8+m86XskT0jyhgifEZzIaMmShcn3aNaQ7iXaNUvKi/1973wFXZXbtew7n0DkU6YIUBWnSlaJUkd4UUQELXYo0KYqIiiJFQKr0ItJ770Vm1srL'
        b'TQ/OMxlDMslkknvv3JIbnOvLzM28vPvW/o5lxmm5uXOTvMI5v30+zre//e299lr/tdY+317rsZrLppoLnXtbzfgtNWOiq5rFYzWLTTULVj+gPqAllwX0VjPaVDMSLyNx'
        b'uZ2td3qpC1Bd6KUtjbp8KsVrRhriNSMWJfbVusTXs0j0uZDGWv7sqtGrlaNvsZWjLwMwOQVq5Ru850tHbN0ohs/nsxDnf8bia9sZcZuQ2Ewgpvw+NgeWUq8tC7EcfJwL'
        b'XE9Fo+wnloUE5dLlEs+TtouXhnhscei8wsuFoNdTt3/9C0Fse6Pn521vfLEQ9Cpz+8vditwmx695i7D4mheh2MXXfU4CMCsDL/Gj7FxXvuARfW5HMVstoqr+x0OdHGxs'
        b'2epMemwuexA7Jzc7JSPpC7sgjgH/6rH011MTic//CSEZZMQhGc66QvOnfVWctPsSX/k0lPtwz4mKVOJYcoTTWP6Jp0RhHtbEfjLZoviQe0oUqqDt1ZOiUI8zXG5ysr6a'
        b'sIHL9A6d+ODTD6PCmihF9fu/lchhjBLe/PHdEFvFWx7Ky087Dv1OWaijH1dYtLEtfyoyottBSk70/Sc6Px1N/qhvVEX29hHHn8Sdv5T0d13uMZ5/c/sniu/s10hOLzO3'
        b'+c18jI2t8c6//enkpQi9s5MF+Gvd+NycA226Ne4WXk9/d3v370zv1jh85zdv34vrf9teThMveQ/8zw673GVZ4yPHg3XeWfjtH/y7152ivD/wOVb7i40bv19t7r30vUBv'
        b'/BcpvdN9/0N14B8smi4MmklyhqwfWdXP4z+Qp10nfrLkNFm5nAk6egDH2M/kGVwEpJc7FI9ihfgJpIkTgcxvIYdj8bXng/AWjHF1jkIplGOn/utmObPJo2GJM+jVVC5w'
        b'D6coWTx/PAWndn/NaYM/azgq5nFy+tJ03PUa8n76NGc8fsATG4+HE/6zew01jWqvdYc/0jR/rGnOfrnSacnbVDWi9xMTi9ojLTsfiXWYOmd2ujzRNKwt6DYd8nqkafNY'
        b'04bZOoee7LHpdp3SerTn4OM9B1tknphYv23i/JaJ8yOTQ49NDj1vg4zLTVXjJ8asTa26kCd7LAZdelweuPW5vb3n0FukU7mfDMlqiHqkbPBEeVetiMuQrGz2mIvQL35/'
        b'Yhe90if27b3E7D9RZXLhz17Th2JF+Igpwi+fjitMFT74hCrMjP+aVeHXpuf+jRGOvyVdkJLF1t//KtN+sWAXw5/duJcdn5xy6Xko9ueZGj8V/P1zVJiXeGk87Qq3lp6S'
        b'npWWyH4NSEww/EJ195wwr4cQp6+/4AeLr1QYwhAuFk/iaawVP0934ig0eH16cfPV3pA4TZmUTGxJudTcIplzmK77/pljLD6WODagho1dDL8z6LtF743+Mtv7sPGYzE/U'
        b'vhkyYO4gJRV+oO7nwVXG/yxz4LtF+QcEh6vtd/F+HCbf98/fMROKH0QbgqEXC0K22CN+au/h8zUQaIFq1RdLQtiNG88f24NGbfFzVYtsYeX5spAx/5Pg6o73xZF9q6AL'
        b'7+Fsii/D1WmsssRyf/GPAv7BF59fEQij0jCF1UFfnlttSzlWPN0vRCznZZazl79ivlaBw0S355jokcjnqWk8f57D5FXynecA6P6GyScB8B0NM/EvzpvKFp9NxvbWF6DK'
        b'Z5KxbUl9IhnbF3WzVeFTydgyEwgpmEf3JcXXmnCHG1r2NJ+tf4eEhPuEZP+BjVX5KxLwvIogy0KTccF8uNgk3NZn7mdmzmPg0JIjhJn2X3bJRpv3Wk6ez7o4dmy+Xss+'
        b'och+EG8UvJamR5al6WGFhjhNz57uy5si60ci68ci622JXaJ4/jbvjy1ZSh6bV9e5fSojjz/LyBPI8tRQ+YwruaQ8n0yXw9LQaLI0NJosDY2mc7nvtowSyyjzpYXBl6Sa'
        b'eVekxga1KdJ7JNJ7LNLblhCJ9Ld5X1awUei/rKr3nCyfaEGGpSD6VPHqEvaN2gtK5myKLB6JLB6LLLYltFgmm68sWEP7XtbfL27o1JD90p4n+nuG1KbYypMiEYiKZ6x4'
        b'1+PIExePbUEhnzXwX1U+lXxxv20h922hQNyz+CHB1PEltaXkzf2+myK/RyK/xyK/bYlQ7so/d8lo589/1YEzzzu5Z0h1KHzKdNP00BtHNkX+j0T+j0X+2xIaIoLNP71g'
        b'dwvgv2zJTXyv45siw0ciw8ciw20JOdE+lgrp9YJduPuzFcSBW9jTOFiDw+T8vMhwhPPsICgUGpMsJXimJpKXYBpb8z4ghMIKaCOvqhPqXTOx3UaZbQHDVXVHByiKx0kp'
        b'3SMHsRzqoF4G7mAn3tIXQS2WsL0D0HDkCPTIQz1U8HXwIWnAhyJoPYhzUA0zsTCPw+Ei9nB5MU66usBDmPKDh75UqwYrrsAiDMOYVSH0BsGESyGu46A0TsEIvVYOQD/0'
        b'4kDSRTtjbLXFInyQQYrzNo1nBtsLXdkj6OT8TWv6XnQJ1YDKPVjkdS3VHu/iOiymuGDpBd+d+rE7fQ4GSkbaXbUKhd5IXUtowHkXWMZBmIXaDHIh66iZBT9YcE43xxq7'
        b'aKwS4UACTqmSFu9mOT/otYpNMV7YdtQ+Fe7G47gUdMEClmYS4eqw6ziOw9TldOyDh9dgFZvDoU4bey6cxiboc1THCT9YtSGFX0w3qlY5ApPHodgkkDqwgG1OMHkNR49B'
        b'Kx8HiPS38B500GdNMgzRPPRc1hPIwz2Yw/t2+7AXF5Kd5FxwHsridaHINx1uJ1CzzcGwZhbvk6nvg9Up+BDbA7AxUgvG8z1xCWZomqZcpaDlmNkJGnclNEKJ3N5wnNUi'
        b'huih/xaDoQw6IogYjdC8Dxed3IxdjdRUceYkfdFx1eS0BbbiiLIqlmEtzIfn0Ld1inK7cYOuGMFpmKTuTPGw2T7xELaegXY7WNuB9xXjgqE6KdcNi8KwWQ8qox1kcAOW'
        b'dFVhKQ02dKA0iS4fyyL3vMVWF3sSdp+McrXGBuKDJRjIiSWma8K2cAXtMwUZh67inO7ZXdAWAj3ap3GS6NOMQzI0mDnipzbs8cAqGSjzxhUbmsYmGHWmUY5R/xahOIJm'
        b'oMbSndihIh9mNHWwguizit2K1wW4hnd8jXZ451US2/vjxG7oDPOEamJ6BVjDWfVCD5rbQW8o0iPnusVSYT9O0OxMQ5fAGwbiY/eYQW2yECoNblhDv1NeQbISNhIj9uAQ'
        b'0bUqK+YUrKtHQJsHtME09EFxLHaYY7PFXlzCFVgUwJQs3tPBhVjJLOyEuRORl92x/drxNBjFdiLDuimNgbgDxzMCD1ETXbrQjjePRlDb9RHQ7EgGaFkcid1NCedgrIcp'
        b'S6ozg0Mwcu30NVXliBtx+32TsEPlyn4VHKeBVhIbF5NE3DpAInXHVz/I6MpeYrQaaMUxW2LwUWLMJSyPxfo0WKMxeeMq3JHGyqvY74b1V+F+XqBnCo6bYJkpluNGoaPV'
        b'DSg9J3sclrT0WBYZHFRxEmbiRgzOSGBtvkasN96GWTmouu4HLXhT1xeqI6EISxKU4D4MhR4/YRe/Y682Dnv6yqntsLKR1LE/QRLUGYTlx2l+W3BEC8oJUopiccCB7XmH'
        b'W1giwPoQqMNpA+wIwYoIHIFZoQrxXoUm9NBIGCqVRNsx4kI5jsHc5XxtuKtH9xsnlhrKJ24oK1CRIWmYPU9293KhnRo0EBlv0/RMEWrNyyQpBuB9bZjA7qiTOEpCV4KL'
        b'+mdhPTgQNmBQ1gjqcwgPBqDUORFn0/FOBKxb7WQ/wJ4JhUUd4rhRvBsG9YEBKmcu4zzdb4B4oes03CT52aBh3bTDUVWT40bqoXCTaD4fif1pRLqhUJgxwyVJaIkzgge5'
        b'6nmPiR8F2ELI2RnmCjWMIanXyxYwl+eMHWeE1Go33s6Ihe6L8iSUzQeO7oMB5ZhAGHaDKlwgWq1hsw4x0kOooIHNwKQ/lJ4mWS3Zjet+bm6u2BIAvQnKclhCDNtPLLUI'
        b't/dAm8El4uBmCTdYu8JzsPLHhgu5FjRpszBAjk4FrJDc1JPAtcedPptByNGzD9tTWfAFHnFSBbHqCPRCE947402IuGGheSr37DnoDqYe9mEtzpmy/Cbuu+3ysUpNFpY/'
        b'ybAkHk1Htakf85ex2FL2BsxlcGB5T/EKtBJKDngGORQYxsNUyNVCDcE5X6jUhJvnaWAb1MAAoVKxgxuxb4t0OtyFwWhoENEEDxuIoMEJW/2gO5eq3EQ2kvvYRepoEIqU'
        b'JLDYlfCjX10aFp1wRWsvscIMrNjhQ7XL2JuhfkWYnIZF0EjiWor3lIhQfTS8AVyD2aM0lz0qWBG5K5k4rRinPaCPSL52xoSU0kRkvi5x7oN0V6yNIdXVbAbDl9m+HCst'
        b'7KXZ6PG0I4y7Q2xJWvPM/gsHsM40FYeuHVYsoD4WQxGxcg/M2hqYJsTCLAHOooIaNuAKFitguQ902YUTS8CDK9SHO1hjCvPkdI5CTQH2SOsYEZ1Xsc8n0poc1Q45H3Ma'
        b'cykBZDep7PYjMOubFEZzOQu3ciJpRltJGd6H1QKsvAQtZ6UTscn1vK8Vp85rAnNJ15TmESrUUp0mF1/NCGyG9gtQIXFJCzqIvYmIxN7QFZVKvdzA+wLjzAAfvJMhwrrE'
        b'U9K7zuH4TmhmzGVN4tzjo2IDS3n/nRg7+BDZFgS0GZxxsYaTFrjA99aLgW5pbA2T48M020JdTSLTArW5MMMjsDVSxyJbonCL7lWckGahFxJ9TaHNC0ZVSRO0aVP1akXs'
        b'kE7XTSWuaVMiUWyxM8OHJ6z8oP3YVbynC1UBeo6kBBbliDIPsVL6KAzHMGGJ5WedYdZQZwZO4urZUwQWDH7HCAXI9sh0gHZVD4uwHTgZCXUxR+CWN6woY7fvjdNElm7H'
        b'q6pQdTwoEoaNce7GLq8YQo0Rmo3RdKLJKLSfvsLHJh97WA63uarohTehHVrc4kkn36Ip7tFSIVqXYp8ANlSw/oSm8k5SehVqUHs2KDacJHfd/tjBNJLhhghosILiIDVr'
        b'NRxKgzEPkr3yVLi3F2958bFI8iisJByGRp8UmHULgVUoP+zs5X19J7YS8xMm9tP9ynjppAB6cFoKukkK7miQtMwQqWqwww7WoUqbhLTDGFav4cJFN2LaFlJz1djkchF7'
        b'2K7/ooRj+VDqm0kC0H0Nmq6pE0/NJ+CAxBUcTtIipLqDDwgoKg7h3VMqDkgsX4t9vmQVEUf3GzhSNzrpqNfDMd9XmbTikZ0we5zYcBHmruwnqV/HES+sIsqVkM6776jH'
        b'rLFsqDpvYMJYEevU3Dk06KGeFkFXCjTFqRRcCsYOusscSVYz1KdQh4bJHiiWgOo8on2V9lUaYTsp0FHSmzkR8MAKu7BPK1R0nPTEYKoGPkjERn+a4gFcPQOdMdTFCTeY'
        b'IDkud4bbyAR9HZtOUBNl55IvcVFXbqZr42wWAcwMlhj5RMnhlI6tz7FdOC+TV0d8DbdMiWs6w2gIL00IC1zip2M1mRCuThawaANTl+RNnKWzyXpt8TmJ9YdpKNDtSXO8'
        b'TneezSYiLTAQitgNpfZYbBsLnXTrCpjKuuqqoBcI6zgZh/epzgSBR/MNfSiyOEkTviR0IiRsgmVzB3ccPUv2WSMuJ5JtWU06bITU8zwSrhXfsMR7O4htyw+fhe4AbArz'
        b'IL1am+gBrSfMyebog9WDdLdqska6YU2JZLsTHijjsB9U2+ZjvWKwflI6gd1NaRKQrqty0TBlfPBIkJariHhsDBoVLXcJiWadcjuccU5/r4zAB28ZEhmLjInv+1V0SL1X'
        b'U5vjZ7D4LNzzBMIlN1KCBE1kHuBKNHZg16GLBFeNMEi6pI9s/CmaJf5Ry5NQaZxBSrodxkKxOAp7zhyEiqB9wUS2YrjjlaoT6nuM2TAVZ6/DQJwZ3oqHItWrBthM2qru'
        b'NC5kszCVx3A0BsstbaBZgtjsfhCWeRJzbRCsjyedJW+klqD7jrYWkXguBhsOYRncz3Qi0g/ZQakb8Uwf1tlGqp13cA6Nw6ZU6IvBpcwzhMvdh5TkjO0d1bTtzQjU5xTw'
        b'juqREBNShxvG0HGCGq5nKcEepkNF2EkSkpUz0L0XBtQScDqD7tlOI+08R6LQfzpRnQCoHsatYFKe6FmBzUlsC/TM2axzmu4wkkaVxqH1PEFEqyCVOlZ0nDh+zh5qXGHd'
        b'hBTuMt6+oYYPeWnYboFNJ/Fm3o+IK33zUxlP3szgWHId16SJK/NxNBGHrsiQ2VOsepWIeHPvLjJx53RtdmCDMtmSp8IK/KD2hr7x1TwojdU6Gq0QRjq8l72g+ABhfxNh'
        b'CV3mysymQmURjOXT5K7g/ZPu8qQvF2BDKQb7sTWV9O2gJBblYWN4IqxfzaBT7XFnyZiZ4OwHIPthFdZTiP1n47SwJFsf+02JM3pIeEbDM7Cu0IDgoYPZu8nUgfJzB9O1'
        b'5OmKOoKOJiJHZXAkGXoj145fO5Wcv1shBMlk7cX+3QTeg2fc8hVZ4CRgslsLSxlZbjtgQSmX5ORmNtkUtREh9rJGOBUXgreg6ThVWYDb0jgiSsTyYxYsTs4tKMuCNiVy'
        b'U25DVz7ORBOzTlkrWAQQPrWmKPukXnFjjy/vIiGdJLSp1DEVEi0bSdFBraYa3Msw0PcmaR3bhcu+BFx3yTeZI4W8ksF2/WP9RWMc2EOe7QjevgZtppaEf0vSdLNiHLD3'
        b'TbTPNzxznuT8JslDcR6JQpsc1Nti9QV7bA8yJmmYVVXJiSP8W8ORKBw5S4LTZ0gc2OFIRsuiPZThUlYG9OaSEVlObrKmjRrhZbM74fzsoT3U7dpkuEsmgyQOnSBtWU6M'
        b'2uB2AedPaGMJe1RwMpHu20nM1sbbc9k1KypH4yjN7/RucxKYTqhLyIUOt3yo2IN3JM9gZSq0ulDdGZgjo7MZ75xkefHILulQC1KE+wF7b4QSg47hREFkGpmKzcfdvB2Z'
        b'XzbqDP2e2eZnYJFYqiYYpq+mqJ0nCGpVIv6es8TeY4W+2OBjThwxobkbb1oHpZ7A6jMyZlJcbCKSvg22l3wBWv0leXxrHlbsJvjnwgOQw4QlgVAe/DK+yh4J7pFk2R3Q'
        b'F4gPsy0keHwPHrZexS7xFcyYqQ/UwAZLKR7fnc6cwzruNv67oJTYqO8aVvJ5/AAe557NcaeyCLDbsTIEKvbRKT8eGZcjuJLnL+DxThK2NhGpGvAuiUabhwJRfvK6nP5p'
        b'WWg6FKYUq0q6qc6KGKKHaNXIjPa9eNvfJxhKU900zAhwFrFfu4AU1APo8lf2PE0YXgsdcVhDRss6Qfp9B7biQr53Xb5VnheMaDBD7xr0J8ZimTw8yI4lwWmADTcoOnUM'
        b'G0NoNuk8iWOJNx32wSCPULbsxA6y4tqtadI67aKMiPdu7iKXYNo8ktqt4YXSPUsSCVgnSQk30GyTk5NSCKVWpGDrwqF2L3kLM8QTUWTE1O0llBuHemfylEpyo4PhYSAx'
        b'fB+pikpirRld8pqKyTMrdzYrhDJ7suBWCCemSCd0w5Qh2cND0OqU6HRJgDXSiUrY4ncBhh1wKdtCH5fP4WiUvzoMSxfmJQZnRxOI1kGfLFs3gBZdbbxJhB0lOLpJADlw'
        b'JoraqiJ6NkWqpZLYLlMXag/QUAdcd8qdUsCu+BjO9WoTYLEduTJFRJVxJCjdsIMqAU5FmofaYUkEwdqDQzi1l0Rn0N4CWLyIYag9REZRDY2nKFszT0j8VZtDY+iD9SOn'
        b'yaJsgApz6JLGsRSs9YNGd+w+QV5VFbkv69LqWBljGG/mhdM4qoNjMtAYA43ZJC7rZop5OByfnY0D9Kq/JqIu33E4GUGO5Dj7Qd8eZ7x8C1XOJ8C8qQgWFPG+H4nXLUcc'
        b't/YnCR8mxmSrO3eUyI2fg5s7oSOa0ACa3P2iQk5nn4rSJLOonPT5sqYT3su2tie4mLkkYEEEYMxSAzbyknHUkTyCWnNVbNNkYE56r8zmBsnq/AEyG++w9SizkPOkV2HR'
        b'GtpzianKYPE0lGWQtPTByBGS4vHAGzAeTY5fF03reMBBbglmTUDK5v7pJC68RY2jps51CzJA50KYM4F152EVe2yo2MB1Aw1oSszZl6tFZteoGy6dE+FNEa7xoescGdmV'
        b'knkjzLhaJ9v95uvrMwSmE24GHkqXcExDaudlfJBA4nEzjuB5+uhprAhQ0/Ak92UDmrOJmKXyapJR0UFhBEC19juJeZpgUhsHbLUCDV1g9iq5BWURWqGW8Z7SpNmWjp3k'
        b'FmpmQvXpJm3Q4EAkWZOjIcxkEDb1kGJZT8aFPFgwg0modLEg4RjAjgz6p+bSfmgjzUYgX8uYtRemzWHCJpNs/q6DOJNwmshcGnxSk1mcSGjdf4rPgp2RWN/UJQma9iVF'
        b'1yXUxUELwt9Z7FU9CUO7CVyrod0jO4hs7a4kskCLPRjGTsPNa2lk5+t4kL3Qq63EFreCcLBgh5ccjKSfJTiuEi8G5MSTDNReMKZukVbDB9cJC5Z1SRQ6ydeFweBzvFQs'
        b'O5xGoNNx7nASqYdZ7EikHtbnki4upivIMsfO+ASYTDvqiHOayvBwTxSxQosa9ntaMYqY47BmIi6nENcwW3+EXIi1bFw/J+mijK06tlgfmkWgVqWKPTtoKhuukkFVBBsX'
        b'yeKZc4dhlVBTd3sj0sDd2Bgpgw98M4no7aYmeXpmKRpuUHrUd4cKdqveyDsogtLDEiHE9CPEgXdg4DqhwYO8k35QeZqw9pYFLKklkmyukWAsXDuVTjozA6oFJHkzNIMl'
        b'sBx7iRC3w7UwAvsjLQma2nDUDFYPn4NxfWN/QoYGNsc0Dw8J3FoJIcZVaCTruHH9aBA12ncA6tPVfUPp3is6RJJVL1jyJBgui5bc7Z5LF41xizceJ1lCp+NY+dLJPUV3'
        b'vwvN+/WZnxsZJs+H+R1YHgKTUpYwflpKA4aRcHDuADHCpPNJXIcKqxRnYtE6bu1kZLclQRlbrGtV2QclhGzEo6UwRT4CPrwcamlGMzaKa26eMKwLrUq6O+n2VTCXQOLa'
        b'6+7Cg2FtApYRY2h1xiJDArwZGIvA+yeg3S6ScKfMHzoSIkktTJ5kdkoPPojMNpEUJLtgkzX25+MdK5jZE47FGTbQl3qYVEMfjXiQrNcOH0IcWA7Cin2RpDzazUmeb1sa'
        b'nkrGfkf1qGx8GEL81kTqo2S/mgzcT82AKYKvLrrDVIg0icFGVii573XEMlXQV0CDJoW1EwesoTGPVEpzSCoxFCnU5n2iDCiRMziI484p2BKgkQ5rMJyH7c6w4pmNzUS7'
        b'Gpw6qQcb4TwnvC2SwQ0B9bI0WB2WJdkCSa8zDCRp+EGTt85OZ/K9KmhIOH6IoHyNWGKSxGCR+GD9IvmgY6pE9Na4eCY655NNCVXvSpzxTLqoAPOncSA1NCTl/DmyVmfk'
        b'DyhSJ9pI6Y7K4UwgVMZD80kLTSBn4xbeTVWIxbFwqFH1iDlLBkZA8C5brLPB6V3JZ7DaXoLZrwRDJeRQ38e1oPxClgM4TpkU2AN8qCc0hibVMCyNj/A9dzjYh4S8yhUb'
        b'c5wScHk3QdIETWoluYhS0YQPY/KRuhzGMOC+R6Rsid8P0zi/24yEtwV7r5DMVcOUKQvVpiJNCDqSFaFON61MwPWjF2l27iKZCLWysLDjkBWBWtcV1RtKJiRdrYQ4D/dh'
        b'eTR0OaaTXBbp53kJWMjBoSufYmxycRcEEpo4hHUeStnQpyaVakKY20ljmSZEbLLlB4T7MzcqHpficVZEIjJPQ3+w75Ai1qbDqm7ULiExeRsp8Soy5ccKiOKN+8NlT8CE'
        b'A7ZFEH+3EXavyDPXHEZ1TxDByb+Gag0sOe7D7B9Vam88Wh/67XDc2xzJqAnYRTSq3A33rfRJQhtdoF2diNOeQ4pnMBGmI3TZjhuJsP060KvtDEVxcMearGBXgkT9E2Y6'
        b'hBT1yVgsC9OJ2TdIdxXDXKQDqZXZRIbjldK5R+1hWMGRiFyDrVrRRKblHdiTpI4TMqYFni4XNaHTESaDComx+kn59WGrNi7kBuDwDjJ3akiPriaTOiiQ88qmWeyiRup3'
        b'O+VC3yGhLY67G8GQmxwLrjSmfP6sFgyoKF+EBnWsCkyihm7CvX3SdsE0o2RtEFmWhAbBWR6OYansl4saEoIl6IjZjRs+hF7N0Onv6coj2aggwSRDnLCrHhbkz2PZAVLQ'
        b'xKOVXjC1U5ZPYLAYfYZwr59mZYlaLVFRP0V6/C70ysDtZCh1xmFL0gHl1y9BvdMZZIvlPTyYPXdIhyBlBUpTTEjUBrXggSXJeSvJxBS51x0xstoHcFUTmsOdArN8SYUO'
        b'wRCOC+mSWzBroOZMvkcvDHjCiKQuSVMHbBira5M9e9ccawuxlpHmzmWYEWTtPUTf1rlAj8kpXCZdiU0qRi5G2OUELYkRxDfl2JRNumk9/zRO7nc5AcVpuYSM96x4DjAQ'
        b'm68WF0dUT0smU/xuHExdJAu6jmy4u0St6YMErCVGzuQbLmNZ9sHA864EBOVYcdWSiDujwCfOG1Fg1jFNZGtCTv41WAqlf3uhLYj89PswmeWHE6c4zTiHqy6n3aDZlLQm'
        b'+cC+rjgXQPbbpHyCLRlyLZEso7Z0HFlrRbuhLSpPQsAlGptyYIJ0k5iZSdI6rlqwfVvEmwvOOKdF5m4ENsileMGoEbZ7WUOdgNRbt4jVcFVOIbdx7WqSnx+ZA8UBJ5wN'
        b'sLQgk0zsdRz0pNmfgfuyuOYgnUZKZ5SPD47jivE1KCIHsHGvj5L8cWxK4H5eG2fL/Teuwj1YYetavbAcRkMkIRlga0ZcmvIBPw1svRJmEmVNg2vEERe8eQOrcV6XVGP5'
        b'Gbh/goyteUup5Ew7LZjykyPBH6OKd+2IrqVpJAHrSth9lgtpOUWqpdoWa3WkaYz9spY4UZhMFmBpXD7cdiWdXA3dApzRksX2k1o+WsQuY6aSyrtwyf0E1Cp6yBBmrmCR'
        b'L5kzowzRDuAEj7R3I9bYKCYehZLTgaZOualyuK58qsCEAJ4Mc7f0o1CThQ12x8mzZmborHNyIXHHHROYUjkYSBL8QBNW5GAh4kqaOQ4ZE2wtYjuUnMOVfDks9T5OUlHC'
        b'HgIjxKkjp8WQiN2sh50KcoLzmlgZlZpyNtoe2wIV+d4adN041ElBvYomSVsDLKYq+FtY44IeWwAltV0Eazthkf2EN6i7i5y+qjh3VzLeu/YTLR7AxC7LDKgL2kMyUU2+'
        b'T04etO6nOSj1x3kXeTLfV8kq6PAu0MQeheuSNIJ6H2hTlS0kcaun/+pgwyIj5gp0GZJLWbzDKRTmtaBD2dFV4TLeCsAS3WhpHAyH+mQWTo+YqDoski2a4mAeW/aieV8l'
        b'4J0iDVGMfVZYfj3akJQ0GUAnqW5nCNTm03huncKFAiuyzaCf5KWBVHW5fGRcXhRJ5H1gyoRM0j4HGt7GNbinh/WJZHXPXySGGb+sRXw1eg3LbsAdwnEyPW5FQPPlK3m/'
        b'YM8alIeRk/RCDDzYAlXNKdLCBGCp7gZhSkZYSyJwyugqne7QToqX1cI+bScjmt8NnEiCMWm/GLrHAllI/RIOuKADGzjomCpPYyrB7lxgPwLfjHKBeiE0aRGSr13G1kDo'
        b'EdDhAKwkkqoZuk7AWEPSdI9mo05OD3sDCEhHifhVWF+IG7DqooZ3HGDVEnuMgrEyjf3c5c+WqxKOEnlK9hKk3FEQ4kjiTmL8uSsGJOXLtqGZxHF9qnbUt3obDWzao2+G'
        b'7Xu9yVwg4fAidlhXS8Z5BWw7ZIj9InIdS85AsRcue8CobD6hSwNZP42EzL084vkVKejU9YNmefIQ+m2U4IGnLbTak6VQohWujkN79ktJYfkxL7wjj7e8jpJbvGrFIiA6'
        b'47RSFs5bKwTaQY89Nnge9GBhz6BNSGLfR1BfWhBjoMw29C8TEizDTQNi9nE+mWU3LtkSvzWEQYk8xxbL0YTeGxf2Eh50YFkmUW2A4cC8DRkeDeeTodeJGJqtwzdghSbO'
        b'OpBbU5cE5VLQk2wAQ0KYdDuIC9CTSQO7iUXHCMHmgi6zRyntpciw7oUqUyzeR7SZ1ICea9CsQqxZvpv9oixZKOWQFE6N33NRxCayHqQuMxOoWPVABjl8ZNDfIpSogwFV'
        b'bD2imc+erThO92iDlXOXjGHEEtZ8oNdMEloNWUzMCBi+QE7POPRaRpMBRGrb4WDmflgJMLmIPcbQEgADFjbeOCtJOqXZ35D82k6csSUNN8zEpPX4jiP2LHWaFW6cMCJw'
        b'aw6LUYy+Fr4zkninHIsOBNE9Wva46ntc45GBWX4Bh3dDtZkEFyj7OtGtnMUPJgwqy34eQdgemrit8PHB0MEFsj9gyIWyj3U0E3CRC9JNsS7QxoAtLDnxsCnsoDhu8NwJ'
        b'KAnUMGDBKfk2PKxygyVxdPsGqLDBSlVTvCPk8b3oinMwwq142WC5diCMOb5YI4N6NzPxWhinr1oDDUNZSic7OpXg/rwt0j+kg5dppugiZx7WHDXiOnXK6nKgRPrLNbUI'
        b'Z2qJWz0rMSUtV7kbieA8figPe3AynjujZoMs7APUBouX1erIXlvm2pLI8wsUur5Yh8NWNzM+N0RrslgmA+GhfAA1ZUEYYYcl4pushiRipT+B/ouFOBPoNuP7cGnoxZHt'
        b'C7jI9jyeWUxa6O4MnpmA+9raQ/y1R9TlIFlvZ3G85KNHJbgvp0zj08ouyfJCzCRCqCku1EFK3eUHghw+KeqylfTGe3+TqXpM+Zv3L7/jUP2rrich/6w26PTOP6x/KHWk'
        b'wylran+U0E87WveNHaYBVqZvtZ/N9varzbH6N5N/u7Q+Fh94sbzf8hdrrb+49+GP3ZP6zNffMvmDnUFxWIOlndHpxIiFb5dXfael6ru3g75zL615l52lvZ3FocTm7337'
        b'f1o/jfdTrbBpqnrzUI3yh0sj7h8Uho//fXN2XuO9720YP3p3+GDX4Hbhsd/6//xvevZFf/Cjn+qGTL8XdTu57Sc3fomuWbHr0tYuCx8WV534+d/7eY8/9RtNKvwwWeT8'
        b'vTdDl29tR6g/HPtI78jCY1+H7IfDmd84pVQS9KOjwz8a+Xaa/YD70vJ3z5k2n/qdl+QZ9V/vvv9PciWTxee7FJdFv2+cCPt1lP3xXOH8Ny5sHntfa7SptOLNQ7+c+G8P'
        b'6o/6X7Xkqw/Gv3/JrSRk90xDSHfgz2Qrm8Omctc0z2ss+P/gA90xt1TfM6u7FYUfx+h7JfxNXu1b3/zJroPLl1dtr32z61eJP3L7Xrzur4ROxiFP9/2wdyDx538X7/bf'
        b'4+/xDa8OGpy7OFj2Tw8dciank8Z+6uJ+Ocddyel7O37YPWGeXuL4kfI3VF1DOg0uHdjjsP2H397WvpiTf2z+/h6Xmus5Bn973zM1T2v85ImWEMf3rrb9TuNS9qUcmWOx'
        b'uRrTVyvjB0f+9R/f+Ebq2a3jv3L5gVdTgedvRwfbDZM+OHf1pOuY82xb7uB8TMOl9B8sd/VJmP7BZ+i6tM7I451Dlt8fKrgl9YZu4a2fvNel4i69+XHRTz92Cv1R3hpK'
        b'Ozh6e72r0f4D+zeu/fjbue99+D94ol9979IjM80Y/V8eO3f7mvrvVDq2TR8O7PZ9mn73cGLHh7ZHfv2+QuqtxanKX0UErqpuu75/rcL+W7OJv6nQG5ANd/zJ3Ep34D94'
        b'd0p++E9D/5K7c27rXObWz6x+8FTlfW3zm24/qrpunNx2Prnp75K7NJKf/jg0cC7IYi7gwlzGP9093T/26JsT+R9//B2v9nyNiXsBP/MuD/xh8b///fjWx/Fuzd8x/xfH'
        b'P8z9QXjh77XH3jGJuPrDmN+4v3nwoxs//r7+jsmSgX+X/O52hsfqr8zkuOAIJPNk85B5NxMkBqRqcxgQP+leBWWn5EPlPhtlmFR7M7fZ/ZIpzj5PChtEiuv1eAUw6cht'
        b'rE84KpDPFsmKyEaoVMq+iJ15CqTbFwU83QJqrJ3P3U5aO4qrdFmSVbuMC5cviqR4Wh4C0ihVJ7jYq9hL2rM255LCxTxcVIIKqFKSEcnhlNIlSZ5ZGswpCkkPN8c+s6a6'
        b'RrZwN4eUzd3PqQ13XzQfLJRi6y9YyW0MiIPqG/IvW5TBQYlofGC93/yZDSNH6wFcyMF5HtyVuUhDySF9eedzWsR5KdIrqwXiHt/2JqX/KlqsJq4pvR4tNgnvm4W9/ui2'
        b'zF9R8RcPO/CXfYA+jMfFPPD4kr8vfL7+i//EuztkoqPTMmMToqMLXh5x2zfuy7+KRPe5f0W87ZN8nkh9Wygtq/lEaUd5Tq3dnctVl1sMKwrLC1tyWnK67bpj+w60FnQU'
        b'DB1ru9FyY8qIXtlLhnN5S8fm8qet5qzeOPLGkW/teNPvG35v2QVt2gW9o7Wzxa4ltuNAq2yHbHfAIy2rKc1HWk6bLiGPNEM2w8I3T5x8HHbqLc1Tm5qn3tEw6N7B4n5u'
        b'KhuxOI0R/G053g61Ws976uWHyw9/tC3Nl/XnP9mhX2vZr7Bp6fPIwPexge+jHX6Pd/htKvix2AZyPE3Xcvkn6gabewIeqQeUy22TuJs/1nQsV3iXbZs/simjxx0cooNt'
        b'KYHsoW3eFxVyyrK7tnlfXRhJy9ps87662KErq7XN+9LCRZJV/tJCUSi7f5v3pYWCDGvvqws1ZVldNoQ/qtjL09YpF20Lffjsm/9gGSahL2u6zfvjitrEp+zj2atvj/B5'
        b'csrbEpkSss7bvL98+ZQrn4mPBdS1Ko3nnUuQpP+eyGpuS1wXsNn4aymfcuUz8TH1WKtK70XHhVytwzI8Xb1NGa13ZZW47idJyGpv8/708ilXPhMfv3ZDrlY4UUprW2I3'
        b'E7Y/rnjKimfckbhB8dUB/ChJWRbY8v/Sj6fij2efPlcgx0nEWWlZo23eX2PZrfuU+3zGlS+lhKvgocR1PkySVf7rKlvSnnKfz7jyZbe5CqlimntIscp/veVTrnwmPn4x'
        b'AO60j8IpvqzBNu8/UWZLuDPt8acVhyX4DEK/tJDiy+5hR59fSIlYW19dGHAzFS3BFNCfr3zKlc/Exy8oz50+Isl16ISU7L5t3v955VOufCY+fjEw7rSHyERauB3O30tl'
        b'GF98bErlyeffsOMUKVIxEpwiktj2kzGjryI+VfX1Mk/qiFCGLuDKQJlAmV30Dys3ZbS3I5R5OwyZ/eLNF5flnk+49MQi9gUra/nvmB9a8nxs7raU+9j8yI+UDbsNHysb'
        b'dR97JN4Hqm74X1hb9z9Qe1vAVVV6NZYcFgen29P9sBkPzHZ6CZ6HvD6QvcH//G3S/68VOQeoiPncGHF/jG+U/bdsV/JLt4jLyxnDsooz3+c4n89XZnvC/3/xovjaAoUz'
        b'vn5TUtZTh/emjqKnmSDlwtozYc4xIn1L+Ifp1f6hEp7KJatJvyiK1dLgL3bLWh3zOvPeB9YuF006Bpy1VF3e/36fXp7jOecrT0O3FkwN38r76Fz/L0ZHFt38Z761t+zM'
        b'B98aLDpcYTpwOyB8QK4/vL8q9d7xzp2/jTPy7fnXnylbvxf5vf6If9Xr7P9fm9U/dNc0mU3ImPxu1Vjjvf7jP840ueFw8IxDrrP9s6WBFM2HHzgf5X9s/uuf5XfuDrO9'
        b'ah57uc7yYlrE39XHluiUmr194J2eEbumkW8uPL3qPfGPutq/ufDOu0crjjb/S3HPcFSav+23r753cWrtSqjLR5Xpv79huvcH4S4/8bJtbPjn+//6sdX0P7717ankUcVT'
        b'37839P5I8MS+vRkX5e7sjZqa4uukO73fLa+ptzBdfPYjmU2v8mtH3v8Vr6z84u14I9NfCgedkJfY0XtL/sx7cmYj38q6uzP7Z+9qXB7qtdWreu/tos7WHGt4qrkdlSY1'
        b'+zMzfS5kp9vuc0L20NGd0FAuYKQ0Tx5mJHBov604k9TMUevAUMuYszjNqoRaSvBUcE0AD/COtzihVw1uQCtUQo046xHcPY1lUCPNU9wh0NsDveJ0U7OwYsSyZgbDg53S'
        b'PCmhhIwmTnBrgMop2IeV1lJQdIPHP84y6ZRBLRcNQz8N71lgtSkU4yoLd1nF58laSUAbLkZxK2bBkbDGRSrFeWxgsXlD+DAFQxe55EEwAcNZbFMydyX0wBDVUMQKQQis'
        b'hov7VBYNLM2VDvT4P89ydQkfcIN2vnica1hbPTjYH++a+Qt5O7BBACtQKb7WHRbsAgP2OUeGHLDn86SxXkIKe5y44JrhhZcD7ewd1Oi6wOeppAwFh/JxWUzOKVhMpPPB'
        b'O/39g8WnFXFCYIvz0MZNB/RiA3uuxhyrsR/bsEbAEx7jw2qhLUetOFtjFnQq+ErWPh5PaMuHMazJEecuW3GGWxaWeDc7iMV2TefDkroJt7iZBmsuFix9WBC7YTDRRMjT'
        b'uSaU1oZbIVAk7la/LTRlwGgg6xRLsUW0ljeTwNo0qOQqRNOcVsAQLud8ooacvwRM7VLmVmO9cSJLHmeUcD4H7uDinpNZOHcRKpVEPJ7uHqH0YVwR32jO3wR6d3EhWCxY'
        b'UzxitzYJ7MF2cfCp66dhnmUB06KRVb1IAiaE4memjNdmoNYmEMZN3aCDJpalcuIy3YX6w13rEEszKZ6vt3Shsak4j1kZe2hKHqdwjqVt7rqEdTwcgN4T3H1ScAHq2B7T'
        b'4KBQJaglSCrkY98Nay5AledB4upZLnaKtfmLoCk784QHNaEUpm3EE1UC1aeI3hXYeoDlmguS4MnulYDKg4fFp6fP4yQ2Yb9FgOW+YEsrPk9BXSBHzdZxUuONiwqBbFL6'
        b'8FagFV1P0kPdV7UXIEu+LA4ai5VR2EmEsfDbZ84ijLFJwVoJnJDANi6VGt47iMUWAZKwYs3jB/KwxdnSzP0vsYb7F9f3X5PV4E7FFyy2/sfsBxazhdkPKRkpuc+XVXUF'
        b'X7isSkaFLk9StSiEvZ6I1N4W6b0l0uvMfyQyfSwyLfJ5IpQrC7oVtKli2O/0SLjvsXDfpnDfE6GoyJ+9nghVioLZ6wlTtuz1RGi3+cXvJ0KLzc97f+Lyzx5obL54PxFa'
        b'bX7e+4nQePPT7ydC881Pv7clpCTVtyUEstpPFAw3P/P+6B2lncyB035VPFHQKg968SJDWFabo9jfymvQaWrrZfFEWa1ckr2okqQ6VXlXqLf56fcToeHmp98vabgtdeyg'
        b'JLOu///Hn/vjfC5hoxrZfjYMNtWlDuvyQId/2JYHuoqHLQVgLsGO9/HZsaWAHdsqePEE4M6nUuz3mG8J0hIzsrtJzrYkc/Oy0hK3hGkpOblbwoSUeCozsxIztgQ5udlb'
        b'knFXchNztoRxmZlpW4KUjNwtyfNk49NHdmxGUuKWZEpGVl7uliA+OXtLkJmdsCV1PiUtN5H+SY/N2hIUpGRtScbmxKekbAmSE/OpCjUvl5KTkpGTG5sRn7gllZUXl5YS'
        b'v6XgLQ5yFhx7gS5WyMpOzM1NOX8lOj89bUsmKDP+gk8KdVI2zt4hMYPlMdkSpeRkRuempCdSQ+lZW0Kfo0d8tkRZsdk5idF0ioXd3FJJz0xwdoyOT06MvxCdkJKUkrsl'
        b'HRsfn5iVm7Ml4gYWnZtJLktG0pYgIjhoSz4nOeV8bnRidnZm9pYoLyM+OTYlIzEhOjE/fks2OjonkUgVHb2lmJEZnRl3Pi8nPpaFBt2SffEPDScvgyUyeeVR5pjzXqY6'
        b'+so/A4NXYMgVsqyFAv5X/Lz0aWBU4vPTJJmT8f92+fV6WAayng68Nx0UDwsFv5c5T2KQGJ9staUcHf38+Lnf+/udz/83yIqNv8BS9LAIfuxcYkKImQwXnmxLOjo6Ni0t'
        b'Olo8zVwAs5/TFG9JpWXGx6blZL/JliQsSU7FQc+4yG6MLX4v40L8nJeW6JZtK83CDxJvXKeC8JvP35YQ8oXbPFYo8ORFRdLbwryDfLVt3ifKrDxyCFTeltF5S0anJeCR'
        b'jMljGZNtngT/wOY+tzf2vrH3TdNvmG7uC6D3ExnlJ3Ia5fs2Ne0fye1/LLd/U7j/CU95k6dcq/WIt/Mxb+fmizfXv/8N3ZY69Q=='
    ))))
