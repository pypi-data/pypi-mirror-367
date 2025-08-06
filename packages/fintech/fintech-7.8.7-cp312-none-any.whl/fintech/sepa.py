
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
        b'eJy8fQlA00f2/3xzcZ8JhJtwCeEIp4p4gYhyI4cXHhBIgCgCJkSFqvWqBPEA0QpaBTzBo+JtPaqdabu9tgtiV2DdXdvtXt3drlZ7+dtu/zPzTUIQtNrd/dOazPfNfOd8'
        b'8+bz3ryZ/AGY/HH13w+X4I89QAHyQSnIZxTMJpDPUXKXWIARfwrOCYYNqS0UXA5Q8k/oY1YAjcUCDqYIFDxDmg0MfjZTGt9hQA3folQqeLzEMjdpVoJkWaVCW66UVJZI'
        b'qsuUklk11WWVFZIZqopqZXGZpEpevFReqpRZWuaVqTSGtApliapCqZGUaCuKq1WVFRqJvEIhKS6XazSYWl0pWVmpXipZqaouk5AiZJbFgSbVD8L/rEiLv8MfdaCOqePU'
        b'cet4dfw6QZ1ZnXmdRZ1lnVWddZ1NnW2dXZ19nUOdY52wTlTnVOdcJ65zqXOtc6tzr/Oo86zzqvOuk9T51PnW+dX51wXUjakL3AN0Yp2HzlXno/PXeescdW46c52ZTqKz'
        b'0fF0djpLnVBnrbPQOencdUDH1dnrvHQBujE6kY6vs9V56lx0zjorna9OoOPoGJ2fLlDnUBKEx8J8TRAH1Psb+nmN1AJwwOogwzMOSw1hBqwNWivNBX6jUFeCVdz5YCVj'
        b'sUnKySw2HdMo/E9IOoVH2aAGSG0zy81xOLaKAwgtXlhRPtelEGj9SG7wDXQMNaD6rPRspEPbsqRoW8rsWWECsHJyYBIP3Vi8QsrVeuGUcBd8FTWmpYSmhKF6tDUDbUav'
        b'8IEt2sLNnIj2aEU4SeAiuJ4k4IM5STweA9ty0JtaTxyBWiQLQxwC6XsZKWibNIUHHFEzF14pgYekHJpmITqALqWhfWh9VDROkoa2Z+GM7Hy4E9fALVp3nMIRbYLX0jxC'
        b'cHxKBhtti17nRrrAKzgPkmIBuoxOakgkqeBWBlimWKJjHNjtm68dQ+qxKxUesEJn7dAFDaxHl6rQ+eWwwc4Gt+4a3ODhxzNDr6OtUkbrQhK/OaYSNaSnoq1c4I6OcdGb'
        b'DNyHWpfhaCnpj5Yc1J4GTwWlTIa7w9CWNLQV1meRasFt4ZlhUgGYmWS2Gu5IxOldSfr6hagOncMVS8/iA/gm7r3VDDocu9gQvwNtNQ9JDQvNCJMxwNoJbZjMtUR18A0c'
        b'T9o2eSFqDkkODUb16aRlVqgRba3h4PpuSi1mTMY/2jD+EH/sjqrDPIDZk4fZUoDZ1xyzLMDMa4WZ1wYzqh1mXAfM3ELMuE6YZcWYcV0xq7tj1vfELO2NGd4Hs7EfngSE'
        b'vQN1QTqpLlgXogvVhelkunBdhC5SF6WL1sWURFP2xkKi3srI3hzK3owJe3NMGJlZy9Gz9xPUp7O3xwj2zmLZ+85EM/BRFB44SWFopGo+oMQJZRzgEkEkX2H6770sWaJt'
        b'mTmIMPPHtMJyP8U0lvhmNA+IhI54ehSmr62aBLpAuSWZTXNceI8cQfx9P9/IrzgXIzP854Fykl9MVWvNNE6hHU4fdVftnDeBJY9Je5i4xCPImzPrHvNvl6xpAWAQaGU4'
        b'YhG8AjfgidYQnh0UhLaEJ2OWgV15QalL7DLQjlBZSlhqBgMq7CwwN6HL2umEAa+bwQuaavWK5XCvvVaDLqFudB6dRRfRGXQBnbMzt7a0tbCxgjugDm6NioiJGhc5Nhpe'
        b'gt08zF4LLNApX7RXm0wajKfFxbT01MyUjDS0A0/zrWgLniL1aBuuTlBosEwaFuI9HZ6GnfBkDs7gLNqDmtBuzGGvoma0ay4A4ggbx9K5w/iM9L+YDISC8BmHiF/MaQzm'
        b'Ln4Jl3ICXj7qeUZO4FoMG2cc5pqMOWctV88JT1CNnFD2JCfwRnACL1NNhlJVvkvJ15CGy37zi30fTNrv80pkQxPDrY56ffOWX382Kxs1vrNVesVtRqJWcUbu9tmc3A97'
        b'3n/tne3vVBx12/xJ+qwfPFq++u4j65J7H+EcbtgsmPVYyn9EJIJH9mQ8glvm4o7ZQaQCbwIDzyxHnY9cqWxBXatCUEueDHdwfSgDBHA7J0yETj4ivQQb56GtId5LwoKS'
        b'wzg4ai8nDJ1E22mcnSU8HGI/JQxtS4/kA0E+g07Bo7CZxuGB2oYZoiEZnsJ9toZZi07NmIG2SHmDnCCp2h6nGPrQkI6QrFu37rHTpBJ1Za2yQlLCrr4yjbJKPmWQq1Up'
        b'askHh6SehT++Wwfuz+AAkfOe8U3jW2KaJ+um9wud2Ie2uNa4fZP6hEF3hLJeoaxPGEEixXvimuJaVJ2iPqHsjjCqVxh1RxjbK4ztE8b1WMc9JAOjNsMfUsGgRYV8mVKD'
        b'F37lIE+uLtUMmhUUqLUVBQWDVgUFxeVKeYW2ClOG6i8g87RQgpugdiBEPBsBrS+ZDZoY/PF4HfgmicMwnp/aihuWrrO6z+EzogErx4YJn/LsNmX0m9sNmAu/e8AHfHvD'
        b'0+OHhCeaBX7gkJWMW8wZjYNKCAtz9SzMo0wsKOEZmZj/X2PikieZ2HIEEztk0rV0Jjwk1qTzMQd0ZaFuAI/BfZU0Au2CDVlpOIaR8qUALxCH4CtaJ/IGOiZB5/DawvDN'
        b'YDuAF+AltE9LMoc38ixQA4lJenk8QLvhei9Kd0Jn4EarDEx3EKFmAK/OLtM6kyIOwM1obwiJyIY7BQDtg/WwgZZeAS/CYyEyAWAWwHp/gI75oIM0Ap5Gm7Bcas4mYzYn'
        b'D2SgJkctGcDAFIjJeGhDQQC6HIoaM6UWNGKic/pEPBroFWBVhV6BJ+ApSq4ODX+JkI8AeApdQ0f8FtE6wZbJcDO8ivNBe4A53Ij2wG1oN9sj1+YtQDTmEohEbegSPOVL'
        b'I7LQJmt4FeNitB/UoFNoP6qrpA1fZYflGo24DlC9J7runE/LnrowCV61w+R2MC0MtcNXVWzbumEHFoeHOARuuqPtVuiCXEs4FF0cK8jF2QTi1TshEHWspgOBZcS6VagZ'
        b'z4IIgOFVdwS8hrazMVvQ1lJc9B4zst7HorOgwGkNBRszXeEmdE6Dzq1A22IYwEGdjD98DV1hBVrm9X9yNddxqK+gaE1jpC2MsE7yDMxwz58X8uXNyNqNr1cfD5j1izkb'
        b'Aiasy/Z/e928ywnhKZvik2LuvYNe/ve/v5n923Vfrzu5VJKQvFMUcFh6ZKt12Jfv8q8LI048+CRrb/NaYWmQ9zv7Dm74mnkc1Rg1zXn9O+Fzvrs1bc+/frcoIZdTjl4T'
        b'2v7h4znzXnvth3zm2CK3lG7FD02Fn7ROQFc2nCtfbsabGzYuYeWt1DlmLpt+dfJa+69mz3rttdf//ePVuJ7PJiznnXsZbFsffiy9DEtRMpJZ4ehSiEyKtoSCxBlYFJ7k'
        b'RKPWNY/cyGyIABgBFeC1SZeSnskHVvAMB4/adXidvhmyFvddQyhGh2ECm2lAsJjj54mOPfIhPVu/Mo2urmgLBn6oHp5M5QNhDBddhpfRTnS5nOYv9MdzAktwIr6d4Wm9'
        b'BMf5N0nNnxCmT/3QkBGRSIiU0supQStlRXGlQllApGyt6QOVs32snH0wC8tZp36xS6N5v6dPp6g776ZoKODh/YDPEfvoZt4XAAfHPWZNZs0WuoQBO9d+kdOemU0zWxKb'
        b'0xuZfme3FnmTqt/Ftc2i1aLdv5Pb5xLamHCfC8TuLfKdKvyyV0DbotZFBwqaLBp5jcXk7ZSmlBZFe2KfKKiJwSm9wu7Zu9+xD+i1D2gv6ZT32UfoEvrtaZEdCX0uEzoS'
        b'WpZ3OnQuOe6916E9oddlQp99HE4hFJFVoXlCj7XH919xgWucxprMDHeLRDwbA3j4kxX7ZoOMZtCyorJAg5W4MqVGTQZOLR6lH82M0l4v7iVEdJh2X4qJ2P82C4t99xcV'
        b'+7sE/uCwVfjziH2CXfjDxP5/D7uMEPsjsYsFi2JTFY7go/EZpGsmlTn4s9j0jSXJ4HO1D4O7K/V3vuPBDEr9QYq7cV48AFWF1raTxrBJryy0AmVeWDG2L7Ru02YAKr8m'
        b'YrWjOTqCh1oL8JA1gyK4oVb1m/g/cjXEVOC69eG+D6L2r6/vaH6jeflYP67L4YiS6MgIkeZQfZTyakSEKHIO552z7UXvFY7d9WXR3xXBjpzj8nfz+t7nlWmiT7mUZ1qm'
        b'WW4UcRtLkuW7izo5W+5suAtzELi0O2zBxvU+LevP8cHMd5x6r3KkHIppMuAZ2xC8jN0wBUNtXDpDK33R5RBZSmiwVIZRMaoH0VLgIuEt5thL+U+fknzAAh/9fHQoLlMW'
        b'Ly0oVisVqupKdQFGPSNJdG4W6udmNQfYCxujG1a1+GxZ3appj963qtN375p+sUe/o9MeaZO0OUSXOGDn3KJpW9u6trP0tvc4EoffSWic1mjW4tdS1LK8JbDX3gdPWqF/'
        b'e3afMLAzplcY3mMdriYDbZgc3GKVYtCsuFJbUa2ueYG5QUwdozRigekM0eAZ4vYCM0RNDAAjMD1lyyL9zKC64xCiZ4bNiv9Utyt9clbwR8yK6eys+HWOEGB9DUR43Vqi'
        b'WjRPPwE0QQ5AAkBsRMncscc9s0Ge1o7MIN+8fDVRgiNBZBDaTVNKpXyAvyURM7oXf2NpA7Skk3lwnd0Cd6z2gSgQBV9dTFP+2Y81kkSUjNekeCQAusxXc31RS2w0hyjX'
        b'0XAP2kKTNk+2AXjpDopwnig9GmfNJoWta4PhTvRmNIYjMSAmbSyLEw6iK6UySTTu67FgrBvaSTP41QoRMWFJIqZcnbJ29li2VrGwM8cPtkXjvhgHxhWU0pR8e08QS4ry'
        b'OlxasGocoGAFQ4sbK+B6eD4aI5DxYLyvmqb9PkIC4kmv2H4eetRGwKYdX4nOwb3aaMxXsSAWvQpfoWm/dA8AyaQGDtd8hJMWsWnDi2HzSzHwHA5OABPQenSOpn11ohRg'
        b'lSEigvlRqpy3BrDI8rBLMV5iD8JzuNPiQBzcPJkm/m1VKJhHKpzN07SLJukrfDEQL7xNpURPmQamwW1+LLkevR4EG+EVDe7gRJCYIdEPz6XcWLiJKAXTwXQmmy2vHb2a'
        b'Nh81aXBPJoEkuB3toHmgLqwF11fDo0QUzMD/5dXa8kUOVbUa3DczwUw7W3YcmtGx4oJMMr2SQfJaeJVmmhGAhdF2gr/wQwpIgZdiWVy5A15Pxah2MyKtSwWpc3AXkmyK'
        b'4JGxsMEcncMVTgNpSzm0Di+ViVALvIrO4Rqng3R4fRLtiqljzABeKu0jZlwXey60Y/sNnQiEZyuwkn0ONyQDS8S9U2jilCwrgIs2jxB8WlISvpxNPAmd810CjyIsR0Em'
        b'yIRdiB29MCYQF4RzTmhbVKcIABRiwnUWaB1ch/aic7jpWSAL9+xVdmmYGwzySN6R7yoiEsPZpQGtQ23wVXgBaw64U2aBWf6ojrWHTHXF8BUPt9f8zA+WT2dHEF1G9fPh'
        b'3hXE6JoNsG4QS9PqplsAe5IW437deAnLyOPh8eT4SivcczkgRwlP05SQY0csOC4RJU72D6cvZVPCvfPg9hWzrHBv5oLc8IV0Gs9dNWHRFCvclXkgLw5uoG8XjXPDkwq3'
        b'IPOOxZ+FmXquOo922Y1BnVa4J2eD2bCZR9P+IdILTCIlTfH3lgcHsyWVo+NLypyscD/OAXMcUDNNKXbwBUTBjIj8ZawVdzzb51GwIwFtRHVWuBPngrm4E4/SxBF5zliR'
        b'wX0ue2WhtMIf0LrOWDTWGb1mhTtwHphXkUETesplYCEp32EpL4YXr5+GcqzTrFsOG3B4PpiPbvjStL2+Y0EZmYYT4mOSMorYlTzNJgoQ00qEyty/eJILS3zdOhIUkskt'
        b'Ty6Ilq8GUg5lSDMH1J7KhQ24s/NBPmody/bMLgDXJ8NO2IB7dgFYMGZ5+Xc//vjjgZd4emHoVrlp4Uw2Y1f38aCctGvCqRXvLV8CVKdONfA18bhPv7qwWtv7fiYnwV5w'
        b'7/hfW9dnLy8AK83Gv73mLc/01RaO13+IdKhM3pBY61W4dXzRtVV/fDstP8Y6MvKbT/92+Oq/v6z++thj34aD0z9f0fIRuCGqX+Ixr8lqwwc5F248fKn68cMQsxWfz/nk'
        b'R6d/fhn91vrfFPk3iiZb16NZn5nnfBb07tvL03XNLY7HIv0+LspM31f+ruLcmImVZ63GXC07m/bbk3fPld8KGXN9ya2l99/x+PU7NuVbFmy36Hd+2O9g1e/0bXe417p3'
        b'Ej3qfxHrkLV8jPNy2eJ7OdegtuE3W93vHny07MIEf//Ebzq/fPuf4xaFlEq//PPkyX+q9wo92GO5++K98Yv+Wpmv+TxP+PL/Hf3kXuCXV3b/cpf/9+jOSWV44sbdGzL2'
        b'vjS2w3PC4MePKsJX/vk7u8mW5W1fvP/dI49PRLmvcE4kVB6fZvPNgbVg9mp5wfUYrPUQmyU67ULsf6GZxH67I/SlEAZrNyc46PXl6AJVbuDVmLUhQ4jIEurC0LZVj4jp'
        b'PdoMHUtD20LQtoyw1NAUPuosBo7oMhcr/13oDWp9gk0r0AGs2mxNSyGWIkEsh4s2uIbCbprB5IUKDTyVnBkWREzwaAcXnk8ADqiRC7vz4Js/Q/cxApNBWz0m0RYXENxe'
        b'+8QzRVlzOSzKSuYaUFbkFoKt7gmdG9UtTOP4PVObpt4W+veL3U3gFoYwrrYEYmXf55KQi3uLPiTxa9eHgkI69aGI6G59KHbi5Rw2lDD9ZhEbSs14T82Gcuf0zMtngwsL'
        b'euTFNHiPlsInIVoKDdFSaIiWQkO0FBqipdAQKeUBDdFSaIgthQbZUkiQqHYiXI4ZG3b1aDGGffzbcwzh4LDOIkM4ely32hCeNPUmYwhPZ2Yy7xmf0pkspmeWMbM8Zi5D'
        b'itc/LmIKGVIF+mhOqpBz34INu3m2FBnCfmPa1YZwaHg354E+HDfppu9XJKxLuW8NnJx1Sfc51jaed72DOoWduZ1FnS6/9o5qmomBcDVWblsid2rvuXi2u9/xier1ieqO'
        b'6fOJvYxDk3tdJrfySau92l07Yzq8e10i8LMNkETftwWevu3TWlMbLfqFXi01vUJpZ263Y9fcW8KYfncJVllFY3E9RC7fPeIDkedXgLHxHBB73Ofi78caigr8E6wSowCK'
        b'skicwkWTGfxpsEFyMSM+HWZTg6MJyiZ7Z09yMJHBFGJ/T2yPXIZxeFEldKfAFxy0CuP+JNQmmzTABGpz/2tQ+zmM52Ys1M6psmZR7ZzvY08nRuihduR8Ay6ZI+At0+OS'
        b'9JmuWKnE3b+hliiV6DxsUO0+s5ivycWRv1tRTEzvHX9waZ5AjO8nN99a9FG69f6t+z860bEkx+Vcq4vLFpeQ1rjW3JZcl8PrHue65LQccTm+7uwF6/hP0sdaV30SOuBm'
        b'bf2W9Wuu4O1NthGT/yllqKBEOqRTqFeZyMowALulvFEFlsEkzgorN3ZoNdVqbXG1FqtRBWpliVKtrChW1j4jjgqxJMCay6fxMCsSI3jzJN30ATvHxpiGGr0867fH07sx'
        b'p9G8Jaad0+7QEttr7/dMfVAwyNPgUp6fQWMJgz6jphtMmTWBxzCOL6IPkhefg0mH64P/PSYdsdfHHcGkAtY4jo6EYmim5uJlLwugk1jrilhJ+fTvlTEUSd18SaGGUxPA'
        b'DJXH/hV8TQKOWpR8ed8HHq9ilmyONDDk1viakvTvRe9+MmtR0l3MnOn7q9Za5l60mrXrzE7XoI/X2duV3EvnguULrIPbfiPlPCJlW8yHr4WEBfCGuG9VAl3hJ6Bj04eZ'
        b'LkCAgpgu0HF0Usp9cmRJ24x86fKEYj/ElU+NoTw5Vs+Ts0x5kuzR4PW0Pea2MKgrsZt3IuUy53gmZs8BYVinok8Y3WMdPZwHi1+IB6cQHnxqvepNOTDrZ3Hg89jq+Drm'
        b'f2Srew5RKWBFpesKW6LMzPt+XKH1l9OWsEB6vJSia/MjMwrTd8brDXgWMi7JxkXIFJb/YvJCoALXE/iaxTjmF7EqanxrJua3LsyZjPBkyaaeC1hQjrVWbk2yjNd+NO92'
        b'wl9F75aPEWz2/V3mn0RHg2WCzbKSM9ckDa6h735kEePnolt/8czhiLfSX+d8JnvXK/Bja6DtcxR+7ItZlkLL7a7oBjyRnhFqWcQBvDQGni2CNx5JyEzatxArdVvRFQxN'
        b'0fbwrAy0LTMFnuQBcQ5vHDpX9gJWN5sK5arqAoVWWaCQVytrhz9Sds3Xs+tCHhCKB9xDO/NOz++a3+c+vtEcM23Lql4sJKefzurK6gudfJO5FZrQL5F2JnTYNKb0iyXt'
        b'kTvX9Lt43hOKdWkYE7h4tKo6mX3lveLgRh7GEULxMDsbjxQ6aFGulCtw+TUvYoYmuuATtd8BTMxsC3gvtv/ImtkM3lnkT2DgqHLC1DzWcwmzNUcnoGZoM515iYCyNnfY'
        b'7iPPYhjj4jDPhIm5a3l61n6C+nSDm8UI1uazrP0rbTRWPr9ztAaFUcKoRSwXn+QS1p6VzIsvDN1u5g1Us+8sYTRkyeH8adK+D8ZhyRqml6wXrMdaz/9o1eeuE+c3PEqd'
        b'J/9s/0np1hOtkr+7SBZ9mPfh3fezUR7/85XLwS+LUMxg14nNEyZuXt+hu7q5CU+DkFdUY29Pnl34MC1W/sW6s6+N3brfI+LhW6uvvc5tvfP+9nKvrTbRh149sjmgZX20'
        b'J9jo7JEx01m/Q4/Oo4vudB/IDKA33TnwIDMbtaETj4hpxM57AeudxAuHx4l7EtoJX6dW5+oQuzRUH4pf3Ab3wmtZDDBHWzlw0+QQFnGcrYLdOFIXjkU+r7g2g4E35NnU'
        b'li2C59Ep1JABT2KVH72C32FmwjNzpVbPq1I9yY7EtGLQsIxTy7pUaTKzhj3RibVRP7Gq8MRy3xPaFNos0yX2C533xDbFNsfppn9q53RX7NlS0l7UJ5Y28RqZxsh+j4BO'
        b'pjWDYG6arGX5zsn97t4deMIdCu11lzVO/1zs9qm9Z4uiPaXPXkZCxW1lrWX7lnRN6M47MbXXK67PfuJDC76LrS4ZKwYiD12WyQy0IDMQT7sZpPqCYm11ZcnTlxi25dRL'
        b'Rz8T9VMxk0zFYc1tJSkn4I//wzOxEs/EgAcAf7woJN8jCATHrKKGQ3Kj+ZmuNXwjJCd+U6CE//8D8TiPmJDe7IQMnfUB2MUA+2DXQpVjYCw7IXssqKm36rK2cHXPFHeW'
        b'mB1KjXHxP1YWlveuWMUS/+VJ8bvLrz0Lrf+m1r+uSHQkVvWyjZaFq296jWeJ8jHU1Bzhu7DQ48PZKSxx01gKq8rSMgtzoucmsMQPlgiIYROckRSGWoqELBEGBRErcTJT'
        b'WMh56OfNEj3mTwWrsU7x/djCKFtfEUv8B5gMVuF6frSwMIqTzWOJoZKJoBqA2I/cCx2P8PVGrw+nsKZI7dLChXemKfREQRixMMdLFhf6xgtmsUR1nj3ZEYi30xSmc+19'
        b'WaKVRTxYB8AqzxWFOTuS4lni4SC6TNsvyyhMd10QyRIrlFT3iTg6p7B8zXwzlthS7E6Mji5H3QoXbvHxYInLKscRc1nEmIDCqIAaMUv8cXk2aCctqy1cklOiZIm7UhXg'
        b'Pfy9JaVQgCZMZ4l1i0vBR7ievw8pHOPs6soSe9PFxLQIyiSFkyZ4MSzRz5saTOctjigMfb8gjSVeXfwSeITH/U2HwhX2dkks0WwcEdnA5axdYc5nJcF6rzZLP2LbnBUt'
        b'KOSomCSgGt/9I9Bg+QbuH9u2rTktE8Vbb96fPuafpTUX1t0u7pa/b1PLtzo8p6iX3/DehJuSi7rEz3f296XkByT4zt/653M//j56+1enXr5pltt69NubU9q2qdK/Z2Yu'
        b'S+0rb/n7zZi/XJgSb/aXQ75lY8HxVzUu5peaVkw6f/W9r3aN9Xq3we397//+2nmfmZbCnJzEA6dSwmyCbqYfr/nlb/faLMmZ1z+vLbNHFSpt1J3/bd17335m+wfX9y/9'
        b'bveq3/zbYY4ox/8Bf1vrO7/26eD9DVndPPO51OmzgOnHa7V75+5585jsWNCE3F985+licSLSa8yyfzbGxX1c8DjuH1+c1H5uecj1jQPf/X5h3IQVV29+6Rz3enbGv9zv'
        b'pv/rn+JqN6vAH+ortn29SWR1qaalKfvri1+czf4+9uOxx1b/83HBlOsLsj0PfLd0mbQt6+u2/H8uTRtY/Mu/BXnfnXTP8odLzZ//8Z81zrMvbvz8a3HTyQ0+32dIuY+8'
        b'yeSrRi1DSMoDNZuAqQPwOGuquwiPZKeFBvmizmS0LQ2vNfAEp4aBR+kKBuvR+uIQZ7gJ5xHMAJ6WQfVwK1ovdfyZK8rzLDqOhkXH8Gey9jgQ8Vskr1haUFZZriJCvXYk'
        b'ia5C8/Rmvio+EIkbq5sn6KbfFwCsE6/ptfPvF/u352Gw1mMfTOxgTi3cJivqeNAob/FpUhK3hvaEXifiltDp0Jnd5dTt2OV2mdMbFNdL/Q/sHRqzWxyaZrdkN81vj+wV'
        b'+ffa+xOyqFHdZIEDDsJGeZMzzsqtRU23YckbOU1mLZHtnNbx7dmdvh1ze91Dux26i86Ie90m9NpPGPaWblq/g2OjoiWvPbt1fq/zmE6HXufgTnmvU3ivQzgbWdQS1VTa'
        b'7tC0qNfBF1McSdGBOGDn0Dhty8oBV7JWJrSrO6d1rOxzDW8SfGqg9LkGNwoemONWN+a1RLbI++wl/fbOra7tkfs8cHtx2PRxALfJkIwNR7Wo++x9TcOkC8X4jah9nr32'
        b'Y9i3R4YNbyzvs/d5IBhZvGmqyJYinGq08kzfHqUm0W4EATyINU2Ae9ZRyOKQ9oRbjgH9IqdWi3affdZ43BqJE4pQZIjtcwy4Zy3akVWf1ZJw29qLhDPqM7Zm3fMN1mW0'
        b'+Pdae/cL3YdBC/NBXo1Srn42mhgyVxeacrN6LkEUI/n3dQOswFrrt/P5WGu9D15QdaUo33Qt5+m/H24BBuOJkpzHAPkYNlgAhRn1M+RQU4pFPjl9wVNwNgHD6Yp8PqVw'
        b'TSgCSuGZUMwohW9CMVfysB7BLeEoBJvMDbAj30IHVjH5lrkA6wDmg2YJCoVaqdEUC0yqa26AHiuAQdM2HKfAOIj4jXOockJ9yUvMKRrCFaq3NKIhM4qGBCZoyMwE9wjW'
        b'munR0BPUp2veI/0B+HrnSIzct+ViYXkEbgI+wAc2wj2sp5yPwzquZjsOra3/ZN8Hkft99ne82tF8Lrl7sw91AVa/vnlLVFS1WhStPes8/0hESWRx9vvZb8376O2Cf7/X'
        b'yMnjFh+JfKv6TlTR+BubIxuccqvHbp3R/0v+Cp+Jzi+9YX88NfbewY/2l1//LH7vqc3yscLbNun7/z42/UF51diT8V533860ldh1tAnf+8OmqzulVD2Zs8j7gixFakk1'
        b'kDnS8LQs19AgE7mfn8duD7XCNngRNSxH11j3NL1vGjyJDrPrQpcXXKd3mwMCGTxM/OZWo9ce0fMVx/ESsSsNHVSR8whs5ugqB68l3fAiVWGW8ODOEFkYtVmh43nwMCcC'
        b'XgmjL8O6RWLYgHv0ItyBdqSFwR1whxmwcuagunlOdPuIT04ZwIYstH0ZrA9H20KkWH8CdhbcangNdVMNCm71ga/QJKGwiwcE8DLcac5xhYfW0BxQnTWuSoMTqgvHWpQs'
        b'hT294YiOcNH6yUVsD7QtgOdgAzyjCpdJUzPCyBGHBg66BJvRvv9YnVq3zlSdMisoqFCuLCiotdNPBJmeQJcxouwTZWqVGXD3bDQbELr2i9z3ZDZlto+7LQoeELq3Vve7'
        b'e7XFtsa2zzu4uNuxO+9s/uWcHv/4PveExumGtDHH4jriDk26LYoYEHobiOTxrtijZW57ca84qjv6slmfOL6R1y8JbOTtsun39MFflv0+Uvxl2+8dgL+s+8XujVYm0s9q'
        b'kFtcrlEHk3bwilXVNYPmVZWaarJTMSjQVKuVyupBa23FkHH46ZYP0jeF9M/E+lFKBOST/fIvknwi/vg3Fo9aM4aJZx4C8vkCApIK49cEoeCk1fjhehdjmOYedJqvBkvA'
        b'yD8susqkTGYXM2heoHefkjKDPI2yvIQ4gwAJO7Tmk8rly4oU8im19oY2GCg2jH5FWAc6p5/OOJ5Be/Vn1aQE1wSXzi8gAyBl1FWkf4ZqoV5OOnFEBWxxiof6CohOux13'
        b'+/kV2MRWwKLAMPbPXQk7k0rknV58fPHPr0QpWwmzApbtnrsK9iYDEXN60vFJI6tgtLkWAvZwCbvxgFe1/w97YyO3HbiZqqPZL3M0vpjw6E3hvg9iqLtkh9FeS3apcjvB'
        b'srU8L36GlGFtUZdEKfC02kQoYoEYgK5KOSZzkEgcowFVpTHZ1Kl1MvTbMDIVUWQtIUi7zBy4eLRMb0ttTe0TB/bYB5oICj4djdFmPzXcmhyzWENGafTSHJkha/7XcvMX'
        b'g0SUzZoEPqDDKpSLl27yh+WXORYq8mXKgoJBy4IC9hwoDlsXFCzXysvZGCqFsGBTV1Yp1dU1VNqpVeSDsKJ6qaHWgzbkIIkcIxlleXlBgZSHZwRLMD1XMrQTGG8Uc8QU'
        b'XWvAQd+S+BzSyk3gviWIZ6Yz/VHjvuXa2Xg88AVi717vCX3OcbqZWPb3ekT3CWN00wcwVTKxTzxJlzzg5NnrNb7PKVY3456N0yMO1yboIRfYOtMQHRCt3jS5M06TniJN'
        b'QNdSw2QCYLkEr7DqMcNYz0r//TAGj/NuhyHEqGAIQpwLurn4nx3+Z6//tiHfKk4JR/887N9Jzgk9xKOIM4DgTQzkDMf/7DGM422yMKJEHjkBTNCkQnDS7IR+G4aiTr7C'
        b'HFMtTKhmlGqJqVYmVHNKtcZUGxOqBaXaYqqdCdWSUu0x1cGEakWpjpgqNKFaU6oIU51MqDa4NZZYJjhvMs+3HeodBUa/J8UGRExbbI1RtosJHraj+bluAko7hRvOUW+d'
        b'z7cf1sd2J90NZSnG4HyIezhX4WHSYw40H09cLy+TejlSqjemSkyowuF5439m+J95CaHwTvoY6qAIxCCboz+qScbJVmdXYqHwNSlVRPP3w/n7m+TvVMPF60IQRvfFdIF8'
        b'HGhpqtLrqezh6mExZAtQhdWhQR6ZfaNNtsxiMxMmtQV6+bgJf+w2H37wGgtqCyyqubjqjPGMKek6oBNghrOlAtxsmN5gbjFMK8BhcxNRbbbWXC/An6Caetd/+j3uhWGN'
        b'In8pFapqlbxcVUvOkpcpJXJ9F6gwPJJXFJPD6E++ElclV8uXSUh3xEmSVPgtNX01ZVpCpqRSLZFLosKqtVXlSpwJjSipVC+TVJaMyIj8Kdn3g8jLoZJpKYlSkkVQQmJi'
        b'1uzMvILM2RnTknJwREJmWkFi1vQkqWzUbPJwMeXy6mqc1UpVebmkSCkprqxYgSWjUkHOyJNqFFeqsSSrqqxQqCpKR82FtkCura5cJq9WFcvLy2tkkoQKlqzSSOh+Ls4P'
        b't0eyAveZAiObkdXRdw/hkzhaLxIynPg3dC9WqhVK9VNf1qM39n39A+6j3Kyw6Mhx4yQJ6bOSEyRR0idyHbVNbEmSoMoqcnmAvHyUDjQUipujLxGHRq/x8+RjwFtsXoan'
        b'n58fC53Y3Njwz8hr2BJi1OON6MU6U0uc59GWaegi2eIKlZHz8WlzkS4Nbc3gA294UAP38+A137hyMs//EbBjWg83lgMiCmWhM7XjMakKbRfTXa5ZSEf0y3BUj0NZuWwW'
        b's5OJc2FGRkoGA+AWdBCtW2OBLtqjbmqD1vLNirZx2IPZi2UB7HFotFuF9hB/xZA0clwrPTsZbTdolminFHaB3ATY5maGE52D22g+6ydza+sYatJJfyVnEmvgfms1X/CQ'
        b'safHtueKxfrMj8HdaJNp7khHzvHj6obnJKMt6QKQBDfOREcE6EzgDNZteo+VjWY5OW65A12Tk1YcQdtVth8GcDQWeCGZtH7emp2TKzZF2L9itvH7yKnz9+4O+say6eKg'
        b'1ecuTWUng4oCLEv37W5PGf+o12tDWklE/9vr3972Q82Btt8XvrnFLOImeOcv6702xj9o+p0zp/FA1+raw1vnHlHcEYOvc/92Ov/RJ9l/+8cB69f3FNS++UXAo9yd5hOc'
        b'W66dafqlk3aGDG2Zs81uX6Ts3PGI8u8uZpYeWnLgQt1yz1UfNt04q/ok90L9v7/xiq0JfOl3+7/WvDnv2opP1gdP/O5X1+u+af0y65Jlq4u39iBvYE5H6uDLg2klmZnX'
        b'5XN+cfQW0/QPPr+p+3PhgIc6p8T2j7ZOtgOiR5sfffO4rWjMK0dvd9ztcQm9VPr1W8tDbX7rU/Oj4Kz6Sn9KTkeT1JHauWEj6oCdVrh3pRnasGC0JZwDnGAdOo028cwz'
        b'F7J2ha3oENrLurzOLyROrwaX16noOrUKwA1TUEPa9NWy1IzQFLgN7WAvW3CD53kV5kXUYoIOl6cMeXrNncEJQ/sn0hN/K9AlyzS0PTkDbSfHANhXndAmeDyViy6jjSK2'
        b'EtfRgajhXjkuEgDreYvhdr9HYThFtgfd28VZhCByfwObYXgabtV26isLZsIzuWirGdwR4ska8HcsGpOWFQbrM2KyKDNZZXPQdn/UTC0hqBHugVdgg6FKfLR3VgWDrljN'
        b'plqBMzwAqS2FvOgFj3DRPgZud9Sy795A56vIq+zE5KMrlrCRw8DjGY/IFRD5S9GrVJ0gM8VvqtEKg+omPSLXW/iugV2wAUdKiZsv3MXou5XNLQSe46NXkvNoSQVo/8s0'
        b'q3Q8ZTejg1zUxsBGuBnuY4+rX4QXtTheliEAk1ELF11k4L5xaloLuBftnk8qmUG9jS85kS1121JunE0ObaErPAb343cx1E31WEKQrm0id8bLC9iXGwMDyLuhuIszV5iF'
        b'JfOALezkTvdFTVK7/+aWBvHLN5p9TI0/WP1QYVxQUIAVU1bEygwUqlvlMqxutdgCuPi1x/SJgxp5A2L3u27+7Yv73GJ6RDEDQmeyu9Gi3jnlczf/noBpfW6JPaLEAaFb'
        b'q6Z9/L7VnctveUfcJTET+9wm9Ygm9Tu7NXIHhGQ3YHZnTHv6bWHkPbF7S0LTyj0vN718WxzU7+1/xzui1zuiW9QtPyO+7H95+RuBfd7TWnn3/INaLVp4LcX9Yvc9tU21'
        b'zasbef1ijzviwF5xYCevs/i2OIoWFdfnNrFHNBHXrd/Ns03aKt0X0pTY7+S6p6CpoD3vtlNwp/ZO+Mxb4TP73bzbwlrDOnl9bmGNiQabk4c3/rIwPOntUWOCG3m37f36'
        b'PSQ0Uv8l8SeRA5LAfpH7gMi7ndcnCiDf5n0iKfkW9IkCH1rwfRxJsvvWwCegkbfbxkQzdWA1Ux35IO5io6p3P23df3LEyegWmtizTKz+bYDaIZ4Ybm+i3BJvth/XgW9f'
        b'wsrt1G8B/iAOBVNf1LB1SBANzllN+XmGrRLWsMUvILDz6WYUffUNZpR5Q5aclry2/L35tIsfB+QZ4SoBEhjaGZBEkFopV4RVVpTXSGW4OK6isvhn233w+7yCIlXxc9d2'
        b'wbDazt87n62tP6ktRsbPrOzPNpHRTiUQ9bmruRinUB8i8bR6Ic/GuP95LYlNU12Bw89dQ/mwjly0dxFbU5kpmv65lY14RmWXcEbSDJZIDpaqctaWQufxczdGQaagrbEx'
        b'rYvueIbf8gw36fxnwfX/XXvU54FeGj13U0pHNiX6lifrafs4/Hm0hf9Fc8pMmrP0RZqzZGRzIm95RrLNCftpdeU/nRisTKQVf+46LyOT9wwwTN6IPKqo4wqa7odI9Iwq'
        b'Kac3zz21ov+fTdCPD45Q6xKJSq6RqJ6QjBqlchm9G69IyWrqI14k9+XpzRO5qopS3AdJWnWlZJa8ZpmyolojScBtHqlFBuGOwd2DX1wxThYli5A+W88cbXM2T8qw2tTG'
        b'AouQTALueOFwYzwGsOjGalX0vM08DTnBUDXj18SEzprPY/6yIkoRWSx5bwt39rlCJyUSZcgXovN7XY/6es0f6+y+0TW2D7h9Zeky0U7KY3cKd6AzzhREhqA6giONKLJE'
        b'8YiY6OEBe9REdAN4KuFJ9YDoBg1pFOSao1fRbsMNb9wxJfSCt5RpVO9Qwu6ENILRUQfaATiLmXD4quNTLfdmxGhOLv+wM7CknkARJdk4IxuKZVbES39y0+QeYVC/v/SO'
        b'f0yvf0x33qX5Z+bf5P3C/C3z96p7/GP6/PMap+/KIHhvTdOaHnv/n2XTfxvQbbzhtakyteYvsnpBB4e17FQkiO05XPSJ2ySDp8v/wkW/FE+XuhHcmausZs182vJq1TJ5'
        b'tX7h1mr0Vi16R2W1Wl6hkZvcNVlUMyIjkkccNZPGFWbgNDgr/CUvVaoLf8L2MnLnSO9PPb1mO/BggEtEac2sswoHQI0qsG6B/TCjyky48Zl2FQt0EZ0KUb1q2cfTTMUZ'
        b'nJz6N3J4oKO5K3t7fYcw+fTvnUsUYKNsjKTN4a0s+Ucr5IVBn8nWf7Xet+qNMe1XMv+06nJ6ALc0DiwJsS4VH5FyWC18c2iKXpNH+2HLkDbPM4cH4h+RmyfQFg5R6Qya'
        b'JVUr4dnY4ZqlO2x7xiEsE4cyjbK6wDBGFJ3VuhoYdUTUsGMuq8kE6hH6DbiPaa/ucw9tnD4gdmuJaa5pj9q59q5XUI90Rp/XzB6XmVRz+cTez/RIADt16p8yf55yFuAD'
        b'Mo2eXrtaw4Qi5wKW4wnl8h9dv/GCANx2eGWee5ncTBAkuXiMLO13PCNueUaYLOvPO3tkWBqSezDpXRvDjjcYV4YlYMiTaA+gftRka8PgS/1fP9zwaTozyi6AUS5UqlWl'
        b'qgp5NW6NSvE03FKhXKlfAiNlkaPYWp9uYFawVlzaUYZzUbggmSRHuVyrUuv7UYFDxdUShbJIVa0Z1ahNpBKugaZymQHQqzBOkZdrKmkGbNbsUJQo1Zqnm7y1xWyNEqel'
        b'YASkWq4l+WH4GUTQjkRtqBUuK6VaTvDPs4XbyHNQ5plaoj7jJfINeDItE23V32+ZGZadLEvNICcq6tEF2BKeg3Tp2cncHCnsSpEsLlKr16oWW4BppXbLXq7VEv5xRufg'
        b'eb3B9gys05uEDXmE5wB4Fu2ejdf83cxydMF8LtqcQh3BXNF1tA2ds2ZAmjVAnXjl93PXktN+6DhvlsZWOyeZeBrNRrrQOfCwFOkwdGiAXXnJocQuvDUlHW1hsGA9LF0F'
        b'X/VHR/M45HK8S9az0KFFWuKKjS6V+ZiakauMOc6aGzbHDMx6ORjtEcDDcCe6oPJvUHM1xKixyiNj3wdxRCz3HmoOwBBHtHxPBOqXbj3h6nNyzLuZR0PnpH9yoqNaLBQm'
        b'BvbktbeWz8uLTPhL0ZuOmZcH0venf/bp7PgLyeMixj8GX2vkX/zqs3dEafLNfw3904yo3fyBSddkJYIrLp2CCsuzv5k3sbX3ruDR/EkT099sdn3vD+seBBO4VCGQ1M9s'
        b'lVqwJrc3q2rxMkOMdaEptrCOD6wqOGgfPAD3PwogjWyCJ5Osgsn9AkS2G8y53vAcPIN28dBpuA11sD5o3XDXiiFrLDyEDnDCwlADtYrOR61T04xGfPs1PGBtz3WKQYfo'
        b'IlOJTgbSRQa+MdXUYozXmDOwib1AsyM8FaMxeHUGC8jY+3a70Q5qyPWHN2yIHdcKHTU15fIW4+qfY/0tdr9UQ0yadegKNWuyJs3VGv2h4dqZOHLsGmLRZM2ZcJfnT51u'
        b'W/fEqjUkQcidUsPWhWFRdNXar1+1Cq2JO/RUAuhW71x91yu4J2ROn9fcHpe5RktdYyI5DZfb7X8p9EzobfepdC1LvFncK03p80rtcUntFzrjHNy92ya0TrjjHt7rHt7N'
        b'u+0+lqbL7PPK6nHJGpaZtNPvtruMRsffjO41rot6Mx/52m1h6lPLro5Gef70JZLuvwxbI++OWCOH9UU9Y3JiJ8uaYTyIa63Hi/qRvCoYA45aRf5HnmO8Aiyln3uZ7CDa'
        b'5HFg0CYjqTViSK4/S/H9D81WUlpV7fMb1w4Pr+rEUaV+4uzEJzdVR6m0lDvIW6ZWlgwKNKrSCqVi0AKvV1q1GiuOxTyTqlob2lOLP3ZbGJwA6DJvbvQxYXQ29AIxjs62'
        b'xJou+jy86Bu3+tfwLYYt6TjMN1neeWv5+kX/CarpAapPW5+56LM307Monq6fprr00x0ASBewq6fhXeMJ56fv5dIOY9+ir+DOJjQ5sTvIJInyCqKyy/VxRUswDhgVABA3'
        b'A7wm52bFjouIpA4GZPNfQQwuWJt/avHGcYqTzCiXl0pWlin17gu4waTNQykMjXpa8RWV1aMUo1bihlRo4iQJT6pHhfrm/ASCMJ57NSIIy0xtIiCnkOGF2uEAAukyKmXs'
        b'mjU7GRNz9GiAiXKEzbAZnUtD51JBADpsi/ZitehV7SSSz8aKwjRZWHAqXoRIDob3DTnDI5rs5NTZQalh9IJRrFahI57WqBO1wE6qpx3KTQHVYf7kpkVLzbJxej1trzW8'
        b'OvruN2p1DEvNyDXV0xpyLdANeAqe1xK9H11a5IwaaBqyxahAG0JSCPQImUOu4TbZ/E4OTU2XpYQFCwBqkFovXwjPacltJHAH2kcOmMqsTFKTNpHyg/A6h3WwUGlYKh/U'
        b'omMWcJuQkXLpfbmhc81xuSvh7tQMLuBNYeAJ9AZq0lL7ycUA2BbCvpsBG9FB4i3eynkJd9FmLXXmPovOyUJSM/Q9yQChU3wgF+3zekk1x/IrnobYxwsHXPZ9EI1BTvST'
        b'AGdG+xLn0ONOZxpKzzhEtFrIozDKWRrovrUNvvYPzpwPLeZ+uOFzy3HtS0o2fVGuiblwMuhPZ6vVWvXpkg2Dv2JE8n9+vqHrL59tOF644YT9Xz7/4LN3q79fImixbV/y'
        b'bujiu8ERdz/e/JnX5sxx7RExNv+6/PVK9eHuX2Fw9NfPt/55XddNr4/fsn4tDISvDfMqmILxD+G2yQWQ/JpAOrlV93xJERMpWUU3kHOhbqER9qR7mQIfAnoOcllUckCL'
        b'NhrhEx+sVVP0ZDmRxi6KhY1pKRnBGKOiG1UcYA4bOHC9HzzJuuXvhRdm61Vri1pT0IPqJ7KYZRe6BN9MS0Hr0F56MpkcS65B7CZsYYI92ZJOQe2olZwiE5RzfMXwGj23'
        b'j7HXVvgGPWqWxd56G4qHCV5GN8K5aHfKPLrJKw6IMe7Tspu0lXAfNw5eGS+1/o82V4nwH7mzakXWfr1kqRWaAgI9kcKiQcDCoiIbYg2L3Rl7121MT+CsPrfsHlE2ubti'
        b'0s5J7dOPpXek3/Eff8t/PI1O63NL7xGlm+y83jXZecVvtU6kFoFbwlAaMbPPLblHlEz2XEvai28Lgwc8gzvH9XlGNc5gaWW3heH9nn5tC1oX7FvUOKNf6Mq60e5LvyUM'
        b'olnE97kl9IgSyD6nh6Tfy/+Ol6zXS9bnFdHvE/zAjCd1fAh4PkK6x2kJXDz2rG5a3TPM4mDHYqo/ko8/kY8/g5+zrzm0nT18Z1OPvh4RQDBaZx8z4K5/YdyVZsMwIWR3'
        b'M+RFcdcBgQy8bjXh529sSonHvr5Ozw1o3htuyfchSypecOgCa1yRTU33Uh7xLu7iZOLyZkid1S+Td9eRj/WAPfGhqCwuKKA7wWpyZQHdfh7kFqmKn7oHPWhm2NMi1lRq'
        b'Cxq0GWZyodjXBDU/om8ZGuvwvzms6fDE5DNhhs2AejWznelKGKCZeDNsAg94HBv7r8yBrVNrdAe/o7jLv0vT4x3d4xbzRvT73AE3zy7umcRHXMZ2wr3o8f1xU77lxtgE'
        b'PATkg4+J93k49KCcASKPAfvAftHER3yOaLJu+gMBELoP2I/pF8VhinCSLhFT9GkSSJpEhiYSew/YB/eLpmOSeAajm6lPFT48lYtkwD66X5SESS4zGV0yJjl7DdhH9osS'
        b'Mck5idHNGMprBskrGef1tbm5TcBXItq0dl5LyG2bMV9zLGxCiA924H0SeiACngED9hE9UYlsVp44qwy2N4QdfviFbzhONhL9Czj0INTQrJmkWSkMbZeelE1IuZjEZuDX'
        b'oemKOWPeM2bCW3m3bVK/5XjZ+D8C+INkl8bcJ88PphhqPZ7UekL9TNYtnLr8NFSoNemZaPuqJeF0rbWs5aDtcAu8OuJ3AgCdccQx3HG4Y7iCk89TcPP5KpAvUPDyzfA/'
        b'cwU/30IhyLdUmBGX6rmgm0+cjfWO4wx1OrY/aW50bw7HUN1KZ1/CVViYOBoTt2sbvZO3tdHR2JZSbTDV1oRqR6l2mGpvQiWl2Sod9OcGzahHsJ3OocRc4TDkjm0sz5Gk'
        b'NtbW/qSj0YmbqBDkfYcSvkI4yptCXLZo09CziPzKTQlH4bTJPN8Jt4uhTuLOCvEmkC9WuOBPF+L+ne+qT+eGY90U7pjirvDAnx7EqTvfUyfAb3rhOC8dwCFvHPJWSHCM'
        b'hD774GcfhS9+9tXn44cpfgp/TPHXUwIwJUAfHoPDY/ThQBwO1IeDcDiI5ijFISkNBeNQMA2F4FCIzgKHQnEoVGeOQ2E4FKaIoCcyyRFS2SaLfFkND0vcyEFBwjLq/318'
        b'GBonIpSNYF3A2V/VwooG+YmQUrWcaBiselBcY/QvfsKLd7hDuRpnsExZrSqWkGMacnZPpZjVcjCBKC44T9bgWV4jqaxgVZHRVAUpZ1BQsEJerlUOWhQYajHITZqdk/l4'
        b'Ull1dVVcePjKlStlyuIimVKrrqyS469wTbW8WhNOnktWYfVsKBSmkKvKa2SrlpWTKwAT02cNcpNnzxjkpkzPGeSmzpo/yE3LmTvInT1z3owuziCfLdjcUO4wY7bRnRYr'
        b'BWA31m9XczTWoy947C7XauPvoymYpVh90Niv5izhjkxtYFWNbTXfQFNwVnNqsZZk+otr9fzVjOF5DaPgrmZWALX/akbBU/BpecwSMzDiT8E11kJAgKrhqRYLklo+ueCI'
        b'5FaB81aYsWGyoT1U0mpQYNT2cf2twIg/Q/1xSuMx4hpzrJFbfFowmkb+pDO+nheHfPGffOFpei4dLVbLlrN5UMoz7ODssMZRd/fcrLCYqMjxpqyuwMp5SglReiWaKmWx'
        b'qkSlVISOqhqrqokijUGWwe2elmwwqrDTCuvqalWR9inKdRyJjitUKEvkGEkYWb0Qa+uq4jKSu4rtJzxh9OXgSTCybX8lHPXYSVVBPQCGWhMYoAkcZGSDTMRfiQj+64/4'
        b'7zFXFhGRKTUbtH+yWLJxLS+vKpMPWs4hLUlSqyvVg3xNVbmqWs3BozjI11bhqazmMuSmOBbQknOUanKW8UlgQthAYmIYpF53duw4G53ufkdQyS7A+liK8Jrf7+13xzum'
        b'1zumMZnA+1XNk9sTbgkDOufdCZvcGzb5dthUCscnXV7Va4T1Lu4tSfssG/n9QueWgKZJ/SLXltz2hC5uZ9LptK60y9y+0EmXc3pD4/uCEnr9E3o9p/WKpjUl3cPJZjdl'
        b'NiYNeAW0K/dVYOxu1e8jPebV4dXnE9nI2237889CUj8bhvbZ00CuoScMGPfrYY5cC/YuMNmEM2Vsyl41VUpJIWabYgw+y2XT2e/CQpn6yM+tMbuJyI7sc9b4u2E1XryX'
        b'PTv62J16HI4+sYZVjWOoWuYzqvYsWbmENzLOyngUlUtZc9BcrimgR3QGzZWrqiorlBVPPZr6ZAP/jzCnG9tARduS1iV3vCJ7vSL7vKLveE3qxf97smdVHxdTv0DtsiKl'
        b'mgyPflwkVeXyYuJTJK+WlCvlmmpJlFQmma1RUvFQpFWVV4epKvA4qnGpCqzM4dktVyzR4oQkwfBchnedcRmiV8aZG3/VDxh/1c9SfycDM2xX9T/1TCJnq74cTZzPriI6'
        b'DivKlauKy+QVpUqJmpKK5GTTuJJ1QMKp5JIqdeUKFXEuKqohxBGZEfekKiVGDol4sNS4C6bJK5bSjVBNdSXWwKjgrXguIasXsIYqFdAqFZJR0FKhyopwIuuNG6B4FMh5'
        b'qFH8QMgPlSqryyqHUEyoRKPCq5U+G/Ia8SgzPVX1tDbqM4ojP3UaV6gHWKM4lDzT7lpUWUl+N01SYmrg1dKhUDwxDKMuPyuVaixcVmB0JC8irnFPMfX+hKOXbaY2hMwh'
        b'6zUhYckpZJN3a9pcYgNF25NxMGt2UCr9nVABWOZojm4EoLNaol5P84ANsAF1owvZQalhMrobW4+Oh2TCC+hgThg6ygExM/mlBfA4NVPCV+FxtEcjy0hFu1cKHIEd+dkK'
        b'uIcrg68ka8nJDXQyGr5puj0blCXJDAtOC8sxZJ/Gx9qIObzqB7dTZSsQ7o/WwNYCeg06OWABdzC4PofQHhodKl6WC7ehXbPRNrR7dgZT6APMsxh0fuKcGexvkO2KQ5dJ'
        b'hfiAC1sYeCgIrkuR0F8vtbSH5zXJrME0Db4eNYUHHHBd4UnYAtdrib2HF1KtQe1IF0RucAf8NeRX/jpQQ57q+sQ0RmOG59g/toSumfVhKi/S/u8fK6KaW9dIrKCv5dpX'
        b'xE52/15fOpA26y/X3/isS/PAueXEdw7/13z0Toa94/g9/otmL1r0wycvJ7YIpy33+HLH7E3d7UcVm9ZXz88I/iK4/8E3n6lCDmyRn955YkPhhG8f3owvTupTCKK+fPfb'
        b'mhnV06ZEbj0femHr64us+vznxk2MvGCZlv/Djjp5dPzavpr3H23727W1/N9H3bqy80iWcCp8+EOlb+krf8m4O8P75Y3/Un+23f1K5+dR9W/99hvBvYw3ws/1Lt1ePu5S'
        b'zrK/frXLUl7bczP46OXgmrrtc3oyftf1aIfw488m3Tniu+wvWVdaFUXoH2ZfVn2hPHs1cY/KYf/Xwv493nGXpgiW/kPqQE2rtckv0fvsUYMZ4IUx6AzcAE9hnnjVcAjl'
        b'CLwcEoa2oPrwZLSNC6wdHWdwBegAjxpWJ/nDdbAhHMczgBfOoCvF8By6hPQ/qrjLG6vaqRnpOM6HwewG98M6dIg9+bIRXgzGIwhfS8kIzjADAh7HvACdpnHZ8JR7Gq0U'
        b'flHMoH3oGDwYtIL6HKJd6FXlKLvoq5ypOXk2ukpb5bHcL0QmDdYzILoYj9n6LLemejndpU6Ae+EZ/R2VPMYZvQbbVsH9tEHVM+CpED3b8jIZ9Aa6BLvhkTD2189en8oe'
        b'OUoJlcH6cDIpcRYSeFwq4aGLcO8YWkXX5aK0oUkKt5nBk+GpdJoGo2t8tCFSQ892LcAz4jW2mWSrop5cxHIOXVYQn4FmdJ3a1NGFFNiUlhXGAA5ssVnBJCy2YnvvspM2'
        b'zXi/TXQOueEmEl1ge+j1GXBvWkZaWoYM1YemTUQH4LYsWtFguJ0PT8eH6K9NAOgMasiEp0IFgDedGVMGr8NG2Cq1/69b0siHQeQNN2U7sTK1YPgyUuuhxwujxlLrdjJ7'
        b'euh+nj1wEO+xarLq8Rh7235cv7PnnsqmyvbiY2UdZX3O4XecY3qdY/qcxzVy++2d91g3Wfd4RnUn3raPHXB2bfFrLsN0sdueVU2r2q36xKH6E0hjegKn9rnF94ji+z38'
        b'73iE9XqEdSq6x3ctu5zf55F8xyOj1yOjzyOr0aLfL/DYhI4JhyY2cm/bS/pd3O+4BPe6BGPA7OrVKOh382g06/eQtKW3pnc6/9ojonE6BuHtab3eERiDu/u2x3SadUzu'
        b'c4/EdLHHnpqmmnaXPnFwp+KWOKrfJ6BFQNzrklqCmrIM99rEfiIKvW8DPCPv2wKRZzv3jiSqVxJ1SxjVL41qTLwtGkMOFs0YkPi3zz6W35F/aOGvJVGNyf1i7/aVt8Sy'
        b'fg+f9qCWLJx1q+C+GfCJvm8OXLwaTY8MWanLwM8xnrN33Dx5HGgSHqRnj+WPBuM5uQ/sJTuGcSD33bzIzf9q8kOYGHcSRWmYu6xxE5R6x/GNPzrKpxf/AuPVv8SYIPhv'
        b'usx++uvRcFwiC0T0B+RZtYPAUowLCLYwonk9nCPYTqNXeEfCBv3u8hN48An0NzraGwlC8kYiSzlBL8PAlgH7VBJQRrbWawhsHFkzeXEZ6+q2TLmsUl1DPQFKtGoWP2no'
        b'D9P/NBB70p4wXO8xOdlRLVeXYuXdkPKZe+kVxs10liENe+kGwEtgqlJjap37GX567C9kB5AfLHMp5c4qTL/FRLAHqP8+ltz3enMaf1ahR8LiZP2VqZMugVWYW9pj07N/'
        b't7jdnHXqfyVAobFBb+TbcACDtgN0CnV50t+XxgBqtzBtGP4b2rU3QKI84jI3F6OyhvBsE/87LP5rveyTveLsUKPqPffzQPMHnONb0dXapsnkd05f2X9eZeXkJFn/3RvA'
        b'z7089LV1XuuO5J5N0nWkit8uWvG2T23K3c6kaSlnp3/wf787V3yj2a690fq1vm++TWu/mafeM2si+GVk2PpH/Z+435x+9NPPN7v2zP2qRFbc8hHKTPrtX6wimyNyI9P2'
        b'64IXHv/si/QvvKInWJXOqtTMPfWLz3ecfDn1bd+/ly6Ctz5x/7KtzOkE94jXD8cbBtZP7Dvxm8czzb7JCbydcKPXLPruura/bfji7gq/xx+4iy6mPpibtMrxFW3Dx8su'
        b'373y13+3Fd/9Si7wiIjKe2mVVP7oX5xy87j5ZllSW3rQAJ6Wq4Zc6pahBk6Yjw17GLgLnUtKM/YfD6jhdbs53PL5WdRtLwqdGT9sOcdrOTweM7Sc4x5+gxaRO2Uh8X4o'
        b'KAw3A/RGbLgerntEvI+Rbgq8MrQkk/XYyntoRUan4TH9sg7XR2E0cAKdNO5SM2gnexqjA94IDTFeHD/eA1jBsxx0AkPzRhZtbRtPrpdHOil8k16gTa7PTpvA7q63FcIr'
        b'GNbAbgcDsoHd6DKsp0ikHOleIqimAJ4bDmwIqlkw/xF10axfxWohKbj2w7rDGh7koLNwC1MQbg4Pw33wTdobHHQcXgihm/J8IFjCded4Ka1ocVbwjMmZdngW3hjasJ+A'
        b'DtItfVd4sSokNAPrHPrfmEX74RY72MxVS+F1qcWL4Q8LYHI5nf4kiV4xrLXVL0/6ZwougvXgQuEAPPzbprRO6XMPIVfnu7dUt61pXXNLGNrv7t2Y1u/iccclpNclBK/3'
        b'zl57ypvKmysauQNiD2NEZ/Hpsq6yE0tuucT2e3i3pbWm7cvoTLjlEdbtdynoTNDlnLNhBB+ktKbsS+v0vxM8sRf/7zHxcvEtj4R+kcsdkaxXJLstisAZtlm2UkOcmBxs'
        b'aU+6JZTqT650JvWKI6kH4ryeBQV3FpT14v+lZX1eqh4XFVnykzr9T4d1hfX6x/Z6xDYmkWZob5EfgfJu1/aKQw2vFvdKi/u8FD0uCvaloI6sXo9onN7Fs8221ba9+lht'
        b'R2335D6XhEb+gNizRdk+r08s67GXmd5GzlouqdHyOa4NZW8iH3ZvaCaBDE+MSRBHDxKI93+GA8N4PHhBz0b1b8HTLj7bBZ5uIls96mm/FUDtomCGNhNwKsHIVMaNAAGx'
        b'Aio4L5beokTKzXzMCVA95gXIokqkPNqng9YFFZUFevOVZpArL9JQU9xIs9ugfYHRn43d76kVGwzET0Skkt6NA8QWd0/PXdPv+I/txf8Lx2I+P+zXrji2pGPJofBe98ge'
        b'UeQ9d5/DiZ2805Zdloeyet2je0Ts2cthuznGHzwwJ7s5nD2A3UGp5xo2LNUrVjNP6fJRqGR/R509+nCoPXBO/JH00XMa2uGpkFYb93MUzGrOPkbBGf2dfXQ36CkxvP1m'
        b'Q7tIOJX5yFRrMJ3aTvmZtc5GoLdMpcHDUFxGIVItN04SWGsWSG1xgYNMoJTPjrhQtayqXFWsqi5gJ4NGVVlBJ8mgRV5NFbuRwPIAe2ZtkE/x5KA5u1WII4d7WkuMR9cG'
        b'bQuq1EoMtZQF9JVaJwODDCNnE/YgbccCkbj0KNvn3MbyD+sra5vWdopOe3Z53hKPw3xyxz36lnt0v7/0WEZHRrf/pbAzYX3+8a1Jf/QNGQwff1l0w/Oq53v8X9l+aHuf'
        b'y4TNIxdb+s1n7gPGcz5zz8OHCEcsbMQejdYjdweMprF0/LEb43gFsb4yzx5i/YCOwjJkQPfz6ZDwMmvN2XYHBdbyAkPxKHACpWpr0qMcVpoZTyFKhm62wD2kpveaGjZd'
        b'WMJCjt6u/d16MBAe1R1zKe5M3KmXb/J+YYNsesSZPfaZIxtnPMxGJiFp2osIoxKOXmCQnzh4bEaEhSRAw9Z/pFQwKyB3DuKK2xorTp8LOEZ7PPkFmOnHUjtSu3mXbM7Y'
        b'9PhN6RVP6bGfwtZ71POIM4BehDIjqgdWMwrGMOfXMKO3YTWzlKPfKuFkDjKTujhqcosBy9b6QZjPGAZB3xRBQUE5uVzExtgS8liEkzz0YxtiXISTuqP7XMbjxZO92qMd'
        b'L5jSHnvp/7ZFbsYWPeZMmqwu/qm2KIe3BT+WjN6WmD6X2KG2zGaven9GWw4AowTGUqyeY5TAMU/hs1El3dIggDUVtSvzFD7Eb41CJW/lPm1xZdhY6onPMixvqH+eONU4'
        b'JLVwXymXD+sr8kgK1xAVabiU8vRpy2/N7xx7emLXxF7PcV9hYTON6fcJOObZ4dkdcEl2RtbrE4/FkVMic++nOtS4qUYqRZiDbYC1sQkUAT1jiCuGDzF5rOLoXQ7xELt7'
        b't49tndwjDuqxD/rfsuZ0/U4qmWxTfpIzS4fPMvJIkqiVjN5r8H9Wz4V6JESm0JSfnkKlw/uXPK4kFVUZKzqq1CU7JmRJ+ekFZWgz1+YnlgeyfTRseWAJL3H0vwFBuFTs'
        b'PuJC2dF7skJfwf+kL8nhEWrp4q4ma+Io27uGPIycEdLFHRLDFIwMm582zPD5aWg9XmLkCsWwJYY+ryXSLIZt+yiimVVw8Owj1lNWvcg7tqhjUZ84usc+emTvGIeP3Mf1'
        b'9L4xGTr2nhp17bO4iKzsbO1NVnZK2EiqTz1CAT1g1rS6Panvp0Tvf2XkLF9g5NgFNExd8wKjpdEWDQcE5HkzmTgvjTrDjT0fpO95q5/ue3r7zpqf6nm2JiY9TwnkR7Xp'
        b'r8/innf1bOGTq7zatX3isB77sGf0PbFjj6p4CP4fc98BEFV29f+mUgdQQDoMTRgYBhCwYKVKBwF1rYDMgCgCTgHr2hULih2sYAUr9r66937JbvJtEhA3ItlkNcmXnn9Y'
        b'191NTPvfc9+bBoNr2Xz/v+XNe/fdd995t55zz++cozVkLhh0MQPo1mvXOkVfC3odcqq16YRbV4HzD5XSZNyILLWERZ6ctMciXaVZe9Dr7VAJYKditr595iXrdJH9L40d'
        b'wk5u+rYWZGk3aUGasAc606pXLxcmXIp5c/m/0+Cxe2Uj271RI8PQimSH1us3qF1RkVatUykraknFDDVUjCFtP8wr2Ux/xsVb+tg7sss7skPUoen2HksEIy+/o/HN8W2i'
        b'Lq+ITpeIp95SWDvaXLu8FY0pT7z8W4JZWazba1Sny6j//Yrmv7Ki+W84h73kR75xTdsTjrmyulrNVrWzoaqNiUdhEL2yrrXd3uOMde3a5aXodFHo6zqY5Pn/oq7Fr6xr'
        b'8RuvF8FvWtVW1J+8+SwF16dhoDdYHOgGCf43xjoRkToRGuok9HXqRGvYZLL8bSt4xq97/byzaf+kfjKEtNYs7c9xeWkewavzlPH1dSsmHY9UDVmLKSu115yfEhtrvFdU'
        b'N7+6UgVWwItKKqqUKtONGw7waah/26IitlzSBEMMTaBPugjdHOxqBu3mS7q9JzWmfEZ6ctDpsNawNlW3F/jb/HVIRJvy4oL2BTeDu0MmQQiplKYxT7wDWuLYHeRu79Fw'
        b'NYZkWtS+iAwVIjl5T+hjeK4TXhFZIpH5Nv7abpDO3G+JffWmDI01U27WJ+n1TZhgPbnaIGuj9uiy5mVNC9tiL45vH9/tNqbTacw7EX9e9K3Ez38d4muqNWbE0+s7MKAO'
        b'WpRfDAMq34RErSHHIEQZUOffMjGsZ3GeBeb99RXkl8wzJ59efwA90dtQ94dK2f52sLpNe3Fl+8put/GdTuO/K9GM1rLuW8isqNKakUmvP+Rz1l6UTM+mWJj9d6/qdBr+'
        b'XYqNr6bNhi5UJay7XJOlC1L+y0xs9AYnpM0zuwfZKDD0ixaGs6MgEyjsr6ntjL1DyTfuWcNErBQohSzTu8yE8JWDbJ9a3G3nbxYbpmnB60yS3I747+H8ZQBF6lZUlUtr'
        b'qutYrG90FGspoKupqQYP/C/5UYpeXjSZSj31vbLXerGupEpbsUzF9k/W91SvFSmpvEKr6RWoltT0W8qM/qfYCdVY/ZQCs+rnUj6C6s9jq7/H2bNpyq6xFCmf3u2Z0emS'
        b'8WQY+BsubZvcuqjLN7Z7WFyjgOPIORk3qcOn233iYJx5O+WsXYH8yH7WlOqXHGmaymotRFpxh292MEfQkOuyMlWptqKWDdxL+KDKEo22iAVs9AqLdOpKdT7UwXQ4GO0y'
        b'DcO619qgUbKjCAkWQUvRO1TVoC6EA13A5sChGA7gUVQ9Hw4L4UBdQoLfOzXsN6tr4QCitvp9OKyFw3o4gAihBlcl6m1waIQD2E6qm+BwAA6HKZ1waIXDcTicg/r5T0fm'
        b'HGDsyekkAeq/jDP2+gTEnmoea+wpFkqc+mwZj6j69Kd+QZ323j0+fvU5PT7+5ODlV5/V4zylPrnHK4WcBYR02vv9UuLSnNIa2Fre6aW45fxIMv5rvrNkBBgwTuiDsy/C'
        b'GFefJ06hrPWkawqvPoUz1wzvcYkGc80Yaq0JKeP6+LxhebwXIoF7Pthw2jIObj0S92/4wRLf5ww5QLEecHDrE5LLL0hLOrj1EgpKH0kCwHwyEm4GcjnIZd8kkmPYF3yh'
        b'JJbG1emDs6/sbSQ+L4bxJLm852KeZOJzMV8S9tyaLwn/ylooCX9uz5PIjGkvrHmS0BdigST2uS2PXOrPFF+RqoqFzOFficWS0V85GQ9WkgkvhvIk8S/E3GECHELgIPtG'
        b'LJLE9jHkYIzv44zuoA4N3oYbInHDovfDeYy1O1+3LNpyTEjYRN8rMjfjpM7RBPXCMogDac1F4xGsZ5TCc6J+0XjEJNXKJNXKJEaPMdXaJEaPMdXGJEaPMdXWJEaPMdXO'
        b'JEaPMdXeJEaPMVViEqPHmOpAU4eRVDeTVDb+jjtJ9TBJdaKpniTVyySVjbHjTVJ9TFLZGDu+JNXPJNWZpkpJqr9JKhsvJ4CkBpqkutLUIJIabJI6jKYOJ6khJqluNDWU'
        b'pMpMUt1pahhJDTdJ9aCpcpIaYZLqSVMVJDXSJNWLpkaR1GiTVG+aOoKkxpik+tDUWJIaZ5LKGqaOpIapo8AwVTmaHP2VY8AodWk84ZjG9jqCE5xCo+++Zx28fkhAveM6'
        b'k0xcoKB+2cDogVpglJZUwTI4T8VZ8GkrKA5PbydBY8vobfvAVIIFvKnMoXkcINDcNAL2NU0cDRbDolvC+vFRVpfqYBfLULJZadVqfYEVWlbJzD6qx9clJWQXJnMlFA9i'
        b'eGh2kV7G2XmUSOdRlTgpjoVFmjpClLOv1H8rZwCrVaugQszKK9FQe1sgjlpf1JKSSiorpTqQqyqXApth5mHR7GEzdg/4F4AsfTmJMH57hcBNqa2AowJQ1WZrHW8wrkpr'
        b'4JssYxMMPJZAyawQFBlEVXolNLsSmV2Jza6szK6sza5szK70hu2MKdyVpNuZ5bI3u5KYXTkYrgTkytHsnpPZ1RCzq6FmV85mVy5mV65mV8PMrtzMrtzNrjzMrjzNrrzM'
        b'rrzNrnzMrnzNrvwMV4STLZIarnjkyt8sZ4D+agV/wWRmwB99XSczc1TcVoNwpWiFcEH6wLxKkb5faMRKkoeqbYRVAYPkFutzq4coQQzNGJjnIG+F8CDvsGClUJttoFOw'
        b'wrDtonHQ5hrKsyJvNLOK1k4xfWaFSB87jcdsKxdCT7JZIVhgqFPjn82GaGkafgbgYgRUprTOUZ8kZb+MY6e2ARPhq6c6qmBN7eUV9fKLil4G9396fgmYmxkt1qiJrkzW'
        b'a59P2LaKRZzNrZgF/bKBDwVFFcpeUZFOpVWDY33WnUevIxuy2uCHTH0MargdDhC+Wl0NB+ro/UcMhdGYueEjUiaL7iYl1ujURIxXkVdQXtyKAq60Jb3iokWacvrqheAB'
        b'TlSkYn+oPziJ/rEiGmvWqqh0PiCTafjPEq1OQwQCtQqQQCWVEMmiqqyaUEwrtKKsopR6ByAyALsMGG6XLNIaP6jXpaiyurSk0tytLcR7nQ94ag2hj07DpBj6y8aB7fUu'
        b'6lflRHwmUyyXV0TOF2l6bQmRaq0GfB5QaabXirQLtEmvQ4K+ZdiWsNKotHBDZsvaHMDg7xUvrCMkaEx8CFsQ31iOHSY0dsY2cuo0qK5bPzL1wXU/BznuCM+gfdW2JDTX'
        b'dSomdPlNoCYfc7s9izpdij5z8wFoU0tpt1tYoxCAnsI91oaALTQmS09IOARsCTIEdZGaBXXRx205bmMW3UX/6xdI4w1LA0xjEXOJvgHUWJpLNP8JlsHzAfqs3A9Efdnj'
        b'oM+jJywoFH79DdfyKPiVcbQ99Q2krwkKZnPpcwfKTo9rHXdqws7MxuSmYNgGn9g8sS3mkVdkj19AS2HzsmZhj4fPUb9mvzaXTz0UPWERF+Vn5LeEnX7jm4SfUYMWF+oO'
        b'U94ZUdg5fVZXxKxu39md7rM/c/FqSm4JahN96qLoc2SCRnzhxLgHtASdlrfKO8SP3EZ1Oo3qdBtljMH8Dl6Q1Ig3uKW1e/++obdIHiow89VsDMEwrpBaY1QtNDomlLPe'
        b'mrXVnN9HsHZVEl6nomwp4WBMOIt3sBqnG56tzFt8iauAMY2sMtw8TA3YOSyq1ho9U9KgiW/pQ5Nua7W9DZHuQKTRkaZ5dJqBNEJIx7cPb6E+/zYkelmoR9MINf1o5IIx'
        b'vj2RrwpOMyiRvkCk0X+XzEJwmu+QTtred96GTn9zOn+WIGWDe2p08zgnOdQtBxDHWUhxwUNe+RFUnGILolBmkH5qyGMgudAABRbCkSikBca0sgoVvJATJUjpJIPRfsrA'
        b'SmikYVylhsnJaYWW/urDzIRR0G4YG6Yl7B3CE33yNjUbCjX7Y0PNxg50LT/ImEpInJ4QSQ4p7xBRiVCL32a2DTcnepyZy19w3q6aZ+78tz/xSfkpyZHJKYmF7zBzEar/'
        b'622IVwhMvXPMPjCb/Yh82hlNGFLOyE/vVaSf9ZlCmkxd07O2dpV1JUs1nGNbaZWqvAT2c9+pXb73Np82wnyYhumHqd7czuTrOCZVGlowbfrMd2uF778NqXHm03MIXaar'
        b'qxeCcM86/iUyf01NNXjdIjKEjnUV/E5V+tHb0Dka6PxCr8J76Vho8Gb09vRwcJyP34aesUCPL89sxVhEpr2ScpXJeKuZv1QDlp/SvIT0HDJNVr4lpRxe8gdvQ+kECy1s'
        b'pLCyutycQGloZn5K6rtNZj98GzoTzOlk7WmrlBHa6gjyY2QbpaEpb08gF6brv9+GwGRzAn0setuWhma/PXXcQP7kbaibbM55G8PS+bOGyUTErAJnPdx8w/pYz5uan/du'
        b'Tf2jt6E1w3wwD6XrFhXPOSdF7zRKOt+GpGzzxg3rvwrBDgDYe8F5aGJubmZ6zuTClPfeceHsehtS84DUp4ba+0t/Us03MRTSVDKFT1YR4quoAKYxbBJbCgxPFqLp6amF'
        b'EN5dLp08LUkuzctPz07IyS1MkEvhgzNTZsjk1NgqFTr8fK7MwUpLzs0mMwtbXGpCdnrWDPa8YGqi6WVhfkJOQUJSYXouzUveQDeu6yo0YCZfU1kCEWZYf/LvMtU/fJv6'
        b'nmY+shQPfVhbzZcBJus6u1HEDqsSOl2VaEgZ7zK0fvw2xM4wH1oj+3cOdvNLIU0wOmtLz0nNJc2cnDMZFnvo2+9Uxz95G7JnA9kBBrLdCimzym7PkT6lhM5c/W7Twk/f'
        b'hq6ifss8F6mA+j5kqVIZ1S2mWxbvMit0vw2l88xnBR+2BvWrErjIkIJCyQITYoC6rOAZcPYW6NMctwxjWcIDQMUg2MBBjO2W8DT2gz1DPcLxV/Asw15IqgXTUP2G+gqm'
        b'yDSn7cCcai/L6Za/uUj06vsLJAPTSE6Hgal6ZQDvlcP+5dh81tEGKN4Mkg4rrRlVgJalOYXMWv0htP/f4TP7Raum++zgEVz9T3KQCUxCWtNdYKg/gzWDXblKq9/GX+bV'
        b'v8OZ3FSRxzSwPf3X1QwYfq3ctRJ2O0c3j37oNb7N5aJHu0dH8o20S2mdoeMfemU8cPnI40OPxuQnQeFtyR1BN2SXZDcL78++Nbs7KMMQQ5IUER13w+eST5PwqKRZ8shd'
        b'0ePivj97Z/Zjl5gul5iO5MexqV2xqY9cJvcLOWnWp+EP7dPQhfYzS2nM0pxC1rhs4NACnM3AoaW3N6qGBYDGVwKjlVeA2fKZwYe32skyMFev1zIF2pb3B73J+OoektIr'
        b'BE2BBYNUa06HUGTpI9g7amgrzgzS2e2xcxD4LgBzY3mXl7ybIrQ/c/NqSty9pNHxFXvHGa/6xGFvEut3KfXyw6qy9N8not3KssVtpaqKfJ8FrQS9UQefJx3k8x57jejy'
        b'GtHpMqLHzZ1+W44s0BJIjCo+KKyr16Gf8ooOFTqyjIPqHww3nnol5rorMae6suK4bXUKZBJzaisRq7USUqWVEHRWNOhCr72ZwkrM6auEVPfk0E8zZWeqmBJzGi1ro0KL'
        b'VSY5mCus1F58rq+rpXAWyKdw9UHBXOYhxdTXYZD0x2Z0gTYIXMNSIJeNxOmbYQqJ9xdKHuM7nPrCz38h4vsW8upzjK72x4ET/QmvdsdvkofzRT8RfNEnsN74aVIfX+ga'
        b'+UIkdosiaQ6sz/welwxwmJ/Fq88m2bgkIMGnkE0CD/2yPj7PdcwLkWBYfH3qF9b6F0yCFyQa3f0TKsYDFRMpFfTBHpdgcO0fQj37cxgzoMs1gcWYDXyMSxkJKaNNU2Ig'
        b'JY6meAfR2ALgbN97TH2W8WWh8LIw+jLuKaDRJZGNP0AruI8vcJ3CeyES+eZDHdszXoFPnMiUOZpk9IqvzzQWlgWF5bBBCTgsXARg4SIpFs7Cx3ANCIT6xtXnvGADF/Ak'
        b'3s/FAon0S1uBxIOFk4WQA74lw3vtaiU19mgXuibLwNvCc7IU4AAQ7xAwYfNFqAM34hsDws/Cny8hVC9gbI3osvXMTAGfUQGyzDAXzhTRFIFJipimCE1SrJQi8qx1Pb+M'
        b'pxSvt55po7Qi17bgeL6Mr7QmKXb0ng05swes2UzJUjvCutr3Ovfr2VkVGvMQYnz9HDiBnQN5ZtwGn1wZZkwA7RYZZr1y4EsMk/tSTsMmpNs5vTZFSh0HObUB84+Sygrt'
        b'0t6A/kpioKbIFGek0RsmhvEp9lRfiLW+DL2JotTEu7W3hVINrq5XwxTqx06hnB7UX0a1otzP8FBjlNq3V9D84xXcrUX6DHFggcMFq8O3J4ATUUbz35KETUBC3TuRwGlX'
        b'x7wtCfWDk2DgQxSUhNe1YtDXC1/tB6tCvGXKYMUYtP9QDmOLwGBhCpxEMmsn0+0W1ekU9V1aJxDiKI2D2ADQZW0A28pRSnmFBiAUIFN6Q4XHXoouL0W3W2SnU+Tr8JLr'
        b'v5WXHKSiWH6yEZrQh69vQlOHPwaLmX8xlm3eNKZAOZ4RYmTZcYTlhqdhHkLJE5YlNgtSF33Ckdp0WZC+qFshO60RAmcC4CNP2A98YoHjwDSjpSwP5sj14LkpwnTrYhE4'
        b'Hp9n9C8f0q+OQ8yzK6tVrONs1j0QDR+i9/hI2SMiL73H4yZQyqGpx8LZODhQ2wjoZYSXq6lRVSn1foHsTF7BZh3UvE9QolQO4FdpRyA3dkMfhPhNtA/6t4S3rXrkNvEz'
        b'z8DOoIJuz8JOl8IeZ9/HzoFdzoEt2tNLW5c+dI7q8Rr+2Cu8yyuctft56DWuxwvurmwl57HUmKKw23Nqp8vUHieXx06BXU6Bj53CupzC2sZ+6jTqFUMQIILGIdhvXjBz'
        b'yDFgsAXAYPOw9JGUlT8EnylhjENt99JOJ+lAUgxeRgHDZD51JTM7eKX8cqaUP8eddQJl0ZjGQl/eyd/mKSTPrTSxwS7l82hKnd44q1eg0S1SD4eWNHFH0cvTmllli7TV'
        b'2pJKyx9Kbx2FDwVGCCY/z0vJ3V5jLiW3LW5KOJrWnHY052BOR3KX15hut/hOp/i/PfQaQ1fnLT4K6xyZQ39RxGhcQrumsVcauHaWiU/jcw2gzuZTob4f/w7ta+DeR0JD'
        b'WeJxVgLlAIskHPxzsVAiI0yki3eXd0y3c2x98hM3vy7p2G63cfVpJqfPhTxJNJgWRIE1g/dXYivJaLA+8P+SXI5luULwdog2ooYxlCs05wjxFbxZruDNwnuZZHzeKguv'
        b'wffMWEM9aPXLX8KelKcpa0j+8ulfwSHRTAGElVGKlVZKa6WN0lZpp7RXSsiZg9JR6aQccshhprCeXy8irN9QwvCJCBsoqreGiE71Q+s9yqwgNhNlIq1oNCY9E2lNU1zX'
        b'M8ph59zMDBGsOCMANzNDBCvOCMDNzBDBijMCcDMzRLDijADczAwRrDgjADczQwQrzgjAmOrI0l8mUAYRyp1oHkUFGbgqJ/1Gwgnedt5MJ5JvKBfNaQj5fh6N5TSUnkEk'
        b'J2cbNoaWgHryFRsC4ErqHUjtONH6ca53qXetH1bvVu9e5qoMXW8DhgnTmQ4r8n/YOZkhYE8UvIvUpkAZbhKLy9WQ1/qc3DQvjQZlzDdsaRhZ1aN77aFr6uHuvby8Xl6u'
        b'TNTLn5zYy09P6eWnFJDfwl5+UlqvIHFyTq8gOTOzVzA5Ma9XkF5AztLyySEpLbVXkJNLzvKySJb8XHIoSIEbMzPV4LKePJGeJ3Po5SdO7uUnZ6rzYYbnp5Oy0/J7+Vnp'
        b'vfyc3F5+XlYvP5/8FqSop9EMSTNJhqmEmPQB5q0U1c46yWBjCu9nqGtkhkgZQuoYWWDmGFloY+b22DSaMI95X/C+kHOM3C/VNIJwzgAhis6cBve5whwd4KeHa1iBTIs3'
        b'5ypwQzbEmLXFrYbgslNoRFdFOvUNmiVPz56SRgZlBrhWRe1CZgJe64iupjIV679QCzRxpMBx5QcO/nAExInf3bqntf7O+p0823z36UlPsrcFZ0V1yactWSC27/yBsMDj'
        b'kwdP+EzjBOtxQ0pkAhpPHbXKo+1QuzyNczSPPsD3mCH4tgCdRwfnsC7yb6P7aCPemou3ZBSiXdkKHmONDvKXzEKHqCtTlwQB2op24B2ZEWgH+W1xtmLshvHxJnwUbSDC'
        b'kKUdDKiTfrBWF9N+pse0wvDSQFxEGunTh3Fxa5J3OQ+ny3Fut2dep0ueKZ5V766GXRqtjMBbNYQLsuSyk5pKcvEwv42YyzAhg4sfiEBe4sPj+b1pEMy94mDmpF2UoNSU'
        b'WXPQdxSIurjXSh8Be5Nwk2iTeJMV6be2pN8KySQgqrciEwM7FYhpKDunMgfal8nEuNnO0JdtaF+2NunLNia91vp9G64v90s1dfJt3pcNUWMMfdkvRwceS3EzvoaOZ0Lc'
        b'wUg2VnKEK9oXoYDoyDSyMHStqXl1aH0aahMweHuNHW7Ed/BeGtQYbcBn0Dbj06Sf50ZMw/Xodjz17pyBG8iytCNzeijePN2aDBkhg26hi3aSzGXUvfRDRzFjz4yW2EiL'
        b's7YUTWF0IDvg06Nwh0Yi4Q+35dxLzy+kuVUzrBkn5r3lwuJi+1Xz5YwOpDG8FTXjJtPgH/08TVuhW/nMjAKrpbgFn9PBeMhH29D6zPTsTLkfPoIbZDzGLoePT6F16JYO'
        b'bCVQBz61LDwNHFPj3TFRUWh9cSYTgK6T77omQB+4oWO6SHjzSQVaHZ4DfoYbsqeaOLUOVUSE4vrIMP5EiANdLbMmi/KmFTRwCD6eFrsCn8nEW9OzIsWM2I3vkISO0N5O'
        b'Y4MsR3vL5+Lt4VDrEeQ+us0fiQ7xqF0h3sSXh+PmJLZFrBjrxXxbsuA36UYDzcfRfdxWYEIBOpUERJDZJxTvkOPNeaEGUq0YdAjttp3O4C06kBfK0KHQAismfToTyoQm'
        b'jqeU4PV4+2xNLb4sHIGPMzzUzOAd6PYk3UR42c1lS0iNN8gVeDtEfKkh2QpDSVtvlcuzp6bh7bno9lS932995+Ax+ITAHu8YW66DqR3v8UP3M9lbMrwlK0KM9uIDjPNk'
        b'AT6MbvvowGRmyYQErn7RMXQ/eyrD2GXy0b6SqTTqDN45Kq+Axo7Zito1+FChvt7phEtezTC5TlY1aB/aoAMTnzDcNAvvBoORDHx2GZMd6K2DCTTQHl0hDXSprhZfRZvr'
        b'8GWtGDXkMhIvPmpO9aJxv/H+SrxNQ+6Qri2fBkHDd6BrcvL9GdybjFVLGg3txjdtGfSBShcDdUUIRJvDoXJIZW2NxDsKQkPJVF0fmUNrKp30nLmRpJsyaDVqt2HQ1bk6'
        b'8OpN+nQDPmOHr+OrGnxjMWqoU9svxtcZP7SXcYsRoPXoHDpLa/K9OHQSbyWdPztCQWpbhK+jg8xQtFeALqAbuIkOnWsJIjIHLJnjOKlY/rdhOQz1474UX8SbNYuJcKWY'
        b'gncwaAu+is9U/OibGyINqJqj8ir2Fo6vRlFO15z50X45fx0+adaj9jmN8brqVdZbT55J/UOj9NG0kvbb3ss/5X1h99fd9/Iqd8WfQEm7yj//+fK6337m9u/hw9bEj87r'
        b'naG8f6x37S48VFv313+1PE076L5w8tX9x++d2+O2terD3arughEaxzFnfnNBinyHtrpe8FhQxRTIUfPnx/l+TZUuob+WbVAV/6VNdnL35B0PkiveT/o4XDI+Iy/uJ135'
        b'NmnzhszYY12nQ3/47LN5xzS/Kk/+dca/t3w/dref4MiPIk8tHZI89ZHLlz/kF42sL8/2mnr/muP7WSnjf7AqHU/bcp73r422Dt5Hf/HT9OlTr2veW6ka8vWlMJ/uAM3B'
        b'A/8u63qo6ygdezf83NWG3pD23/353h+2/+6HH/ze+WdhzzdWZU72OeY2K3Oow86KxuMTfr75X5/nrPb6+sEc+72iP6T/zPHBj3q3Fv8kbsOpu1G3Cut+fXLptEfZfWUf'
        b'9C5vr7ffLjv2myGbS/r+2JW//Gngw8Oiu1difv69leeqxF9dVZU4zG9fvnrVh7Ehx7+88uifH3r89kf8hjP1WseWbfNPxO1waviqeWva2e97FHxy2nVCyO8yWk8Ls13Q'
        b'36auObAiKvDZnzy6nK8EfFPkefbgsV98rDmf87n13//B+/OYbcOFU2SBdLGfgdvQblOGAd9L5/iFyBjKLvDj8AEyktH2yBy8VhKRJmTs0EU+PonPz6Ichxo3CgzO0TnH'
        b'6G2oHpyjo7Xv0ywTV6ajrXUOEls1vqbB17USMuuvFjMuiwUF6P77NHCMoyM6CXFj5pOZhV/LS5iO2LA7eLNQirdmEaFGIPBhBPgDHjoYg27TYvEJfBffI7QRTkuG7uJD'
        b'uJ5Sd4GPj/tW0c9Dq5fI0FbHWjJuOvD1GnxNJxEzdm78+XgLPkw9zaNN1ugYWfbWGZ3t8yPwEbSROrF/j6xXdwjvJg+TKei0yTDuIalS4dxE1My66T8QEJapyBaT1eIa'
        b'w1/KG4fW43pab3ZoMzpLRvkWMiNtE+Dr0xjhGB66hO7hHS9g/kE7FkozyUwn9khk+HN5kbnTX0DwqgoyhW3R1Nov1uEbjmgL2uZoLbHFHY61qAEdFtXh63WLySdkC8Xo'
        b'Fn84Gxhnx5JotAu3hkfghqxoHiOewcPnJuIznCN9tBmfwVvT0Hlg/DYwRCRPxYdIDfoDDdvxhmWIcIJb0bm0bJJzhyIjuwIRxsgTXRPWLVhKKwGtxRvzINd2snYvxsdI'
        b'exCOcBIf7xsznG2ILbl4JzjkN846zDA7fC5LKMGb02g7Dlfhczb4LtoaCX1NxIiL+QG2eDutKUcye5IbdNLcNZHMmyLGLpeP98rRvRdB8P5GdAlDhLAdpBfmAgdBXkKW'
        b'dnHGTMYPnxTiK9MdWDo60BXyl2Y8Ox56LHRXB8KpJA9D92lloTuoUbdAS0NANWSRykrnu5F+tO2FFJ4ntVgDj5Pyc7JyUQPekaXO5TGe+JBwMW4ootSOr8YXSGVkkVm2'
        b'1bCWORQIsgPc6X18OgMfJBkUEXjztJG5mQLSE7bw8emp+D4N34D2zMGrCYN9a2RuhjydMDSM9Wj+PHwL3WE/tv39GPI0uTUfncbbUX0u+4500jfDQkV4zRB8nB1U+Hwc'
        b'yZgjR5sjuRVEFMEjFXJDJAqYz/b+hmoxpUQfKsJ+FVkJLghIr1zn/YIuZafxmUUwQMzEF9Jzd0RyGwnF+A63lxBO1rKGQFt0VG31AlgtwmgdgehS8LBbcv/HUTuuz5KJ'
        b'mSzGCl0W4bvsI3sn4XV05dtBZCHyZWnZ5BO3R2aiIyvJJ2xnlViT0SUrtMN/FG2TOWjbELZzIP0DYmYYbzyZC+6TpbTlP+5lQ2+x19/LBtXzuPaTK1gFD5VyrvLZWKaV'
        b'PmA6FtI26pFbDJVzuGClT918wTXkI7dQuqGY2u05udNl8jM3Pxr4NLLLL/KxX0yXX0zH5BtZl7IeDH3g3xmb/EDV7Zf1+gFRn7n59PiFtMV1+UU99M3pUN5YdGnRg/Su'
        b'kTkPfUs780sbJ4PH4TnNcx77KLp8FG11F1e0r7iZeHNKZ+TEB27dPumNqU89fI76NPs89gjr8ghrG9ntMaJR/MTNh75p0oORXXqvMj1+weCoqi2kY0S338hGe8498e4V'
        b'jcIeZ7em2pby5lVdzoqfewY9LJj+cEZRZ3Bxt2dJp0vJU2ePx85BXc5BLVMfOYeTj828nElLz+j2zOx0yXzqHQDe7FqWd3vHNNo8cfZucTvt3erdNq9tcad/9E2PLv9E'
        b'UmhvcHhb4cUZ7TM6lj6KSOgT8IYngcN2r2Rw2O5KjmS18Wshoqaio+7G8svL6RuSH9R2BWd3e+Z0uuQ8c/ZtGftoZFZXYBb3bWO7gnO6PXM7XXKfOvu3zO5yjiaFhMoh'
        b'qsTxFY9DRnWFjHocMr4rZHx3yMTG5E9dgp6GhDcmPyK/fsHU0jEgtM2rKyCOnDsarCbZO3r7Rc46k/X6fHA2zRIYcjq+Nf70hNYJjwNHdQWO6g4cA5mlPdIQmpkrgrOI'
        b'HB7C2mgGRbIlmkSt5fSI1IIT3m7/JGB4i+5xyMSukIkPQ0oeTP4o68Osx8mzupJndc4u7k4u6Q6Y1yjc62gicA/h/BPpLY2FoA5Qg2shdQzs19iVlmgNRsNiTel81SLV'
        b'6wbTMBllMJyKuT+Gsfatg+wGSO/g7+zfZJR9s5CI77m8bxg4fkGPbyDLa4AnPiGOZa7aTRS8A/QRbJ5pJQymcDT/EkP4XDMo6VvrW9VHX6HqtPzml+Yg1lDAMhp8abCf'
        b'IuWCOEhD1aoSZUR1VeVS2TvaiZKKsivibDiKKpRvRvI/zUHCEQ99WK+6L+WWLEMqNMbvMf2Ad8G3fvgKvbplmmED08RMybeQ2oOANYjBQOy7oE0GHbBUp60uK3sz+gRC'
        b's24QSc0EdNoIUpAUXBEYbViAZmpc/M4EU4iC6xv3WDGQasQJh1GccEUZBwxeBKhw0uaqKnCkovxuqCTVal9kMtO9GcE2QLCDXgfNGokAmrkcos0ZjNLelU46/v3fuGPa'
        b'A3FGNHjI4AG7zUk0fbtBk17MsOAizlmVgG5kgqrTEJ1wJY9uZDImG5k8ky1L5n0et5HZL9U06vS3bcqLcyx7xpwL1PFofGxwjKSPiG1QEHwnEbHBZaLF+MqppnGZzeHE'
        b'GqlmfrWuUgkadzLXVpRVgPFveQmAkC2WpeV8MkmTKlUlYKkhTaYeR6BDcYGbqU0XLJMVZLyy9gcVlgM/a1Q0rGNxcaFapyLLbwU70sMWVldpq8kCULowTFpZMU9dQgoH'
        b'WxZ9iGiLhYE9hnbA3EYe06M22VCLrI3MUhPTE4ulsdYzBgJTSyo1hMKBQQ6pEyTTTmEYNIZOIcipqF95g9GAfPbLpCUHfzj6sG5f627/rTxnYUxNGcOM/ZT/P1FyGY+K'
        b'HCPmofWmIkc52shKHSBzoBZHMsac9GOMgyAIy8pV2mVBZoNMU1pZRGuQDDeoEM0EBeSiwgE8DyqQSinjLQWvFZ0uppoODnFmzkVRJUuxHjyuBl+rr/dGJyGn5/jbaubF'
        b'HCmPN/RN9RyNYinTYhcusOw2uowOfC5gqYhqMnicTg4cOwu/s2Cl819LJzeenEf64qv95cxpuB5vzgqDaIiFsC+Od5VT3dzm3CzYmEdn0Wa7MegmPlORcC9bRAO4zXoZ'
        b'c1BxmOribqXd3R1N+ouLZn8U7pFtO+vhf2546vCNOS0K9/u7ZUdsTp3ZtSZGwpwrsJm5/T2Z4AXoBNDOmVPMyUCNjqzE21/cRevxHRp7UY7WOVmIF43XhtCA0ega3kXD'
        b'JqOTS6egrbgRdfQXjqlofBGffB1dHem5mtfquRqu54ayPfcLtZRx92mZ+jh4/MPg8Z/5hnWGZ3T7Zna6Zz4ZHtYWd3xhY/LeXDPdHe3RklcJB5zuzujmVI1er48T2jz1'
        b'fRxi7i0mfdzjTcLtQb3L+FTRgdaiM+hSZiba/B6EsRY68tDpiegie6+VtFlTZnhSZg7ciuGhK6gR36iI+vc8HtXcdvvcPfjDcYfX7G5dJ2uI3nBpw/FhH/+h+P+saypO'
        b'L80p4T93X+i+wL2g6bdRopiaUzzmsdTm4emP2Qr6Fni4qe9XQxUsG2a5amhD+bIN1SO0fjFTaj0k/GsXwZARfdaMf3Cbssvoz1X/9kEbxfztagxNMsh7HfWNQN779SzS'
        b'CDZv0ggATra8dhczrNqfxkNmyvj/gdV7gIp04NRCFpF/vbzM18DgK/rnyIM/jD28ZnPr7lY6LZwrW98Z/OBD+0O/ZxatFPqsuUDWEqoSXYc3orsmO2yoAZ0fuMvWf4sN'
        b'rcZ7ZXyTVuDTQWuCu+yv0aaAS9rwbtwIneTPuHtZwFzqW9zCEmNscRMF+uCv8zdZWL5a9YYLyyva+z/Oqw1YSJgBrS3MKax4mrlFpIFd/ru/+zTpG+AaWnftjPFhbFv5'
        b'7nUj9bjUfrwAi0vtv2fBAlJp+9iw7dOXStrH+w0X/VeUHWS6yqf4v2Fj3OX/P2uMAUNvYKBqMvRO/eFffIocqQ37E20JQMXEZ8R7XG5yj5o0LPxUzwJ3yadenzxodmA+'
        b'KxL5R/yErMGAHyictgxvlcP2+cx84SQeujYLraN73yMn4LZXbn2bDMpmfJcdmHPGspv4G2qHhmeiS3gdKL4ixIw1vsNHO9GxWgsdgiK6B2xiUSg37RBStkO8yIIOoYdz'
        b'P/Ye2eU9stt7tInP/9fvJ694ZYhpP8l8q35iinbx1jcWeB3c62oR7QKANwfqxVgPeRPXO1NAnAH4Vu9R71lvVe9FREem3rvep963zNuAhJF8Z0iYAQLkQCTMuBwWdrJ2'
        b'5YrMbHsTZMZQPgvMgPl/JL6G1tihPfi6Gl/D1xxBIQ9QAcYJneDj2+ickw6iY2Y54PUUKJBGukkuOkfRAhQpgK6OsQQWwBuX2KFrkei4TMyCPDagW/iABp0mHN11uG5k'
        b'0DZ0byxFjxDe4yg+hq/gkw46Maj6CL851oV9bh06hI7YESb4NL5O5nN8jTAvqC1IB9+qWIlOahICAPuL6wE6ejqAIiLiXKfaxWRDT8IXGdSEb4Wx8d2vL8DHNbgNN0F4'
        b'OryLQVvem0dhBKtLrRh7hnF6MEtX+ShaxeJ1wrMi8ZUUvANfgoKOM2ifuILShFaj+04aQtle46fgetRAMRXT3ptCK4rWz3m03QRNgTu0any1IC0cVKkspKIRNdmsJENy'
        b'M2XLgrwKY3BjTAm6HiVkeKQa8Gp0Dt+hqBwBDx8xooHwXl3WlDTOF3f4lLzpeG9MRoEVMxU3ifG1JHxYB6MH7Q2yj8HH0Q1yHs1EC9U0FW+rcsW7K+WEMYhkIpPx+sq/'
        b'/vvf/55iK4Q+JHWSVVcG5S1hdMkMsPCNuCXT8BpcnyYH4aMhMmNqKN4M7787qiBUhndMT0vPBjEgGxTY1/Ph28RVkjn4MDqqmwSUfKCKBwyhaT7oS0wl+ZbNkblcDZlC'
        b'nKATnUV37PHlfHRSB3ZTRWhXlYTk3ylBq6OsRXj1VHxEjLcXSlADvpE61NN6XD66g+6RerqYUr7EpsxtsS2+K66zRltscu1RB5niTkThe8tlfrh+rAIfEKP9STJ0ZUIs'
        b'bnZHTSlyXQF5hz8+jLeJ8Bq8RsJEWwtQx1R0eSbeK1wkRpvxJrQ3jIg39/AOtL3Qq+J91IZXe6F7CwK80A3Smzeg62XL8XpBdCjAr/zwpWTn7Ai8Qw09jHaz5LFevFg+'
        b'Yz1Jt9CnfaiUoUOLcEjnxXhrNjqXh+vTycdH4s15FKJmgNOg82k52dlUtrtAxusWfMOudDpaR8v8e1ka08gwUQ88V9nOkLkx9CtIv7qF74tI9deTT2m2YaT25JumzV2I'
        b'dpEOdRu38qLRWnxybAxpk93FRBI7hw9MDcHHZxLCV7sWorUqVF+OW/BNq/nortNS8p17dSAWWNVAJxxIapomJSJDNNQVgKCoXUb+AermrA2+ga96FMp4LPysHZ/BrXgr'
        b'ujGPHHZE4u3pcjJjkHZ2sxZGoVO4mdYHbkJrXTIjMrIL0qi8mQ54tfBpFHuqR8KRx+QZofIsRXpEGOkmW2T2Fc54sy4aHj+GTk22CEtaPNwATDLCkoZGEOroHHR/Km4F'
        b'VBaP4bvFo+28JHwXH9ABzN2dlLYvPI3U3LZsdhhEZqRHoD3ocD4LIzSHxwFMi0jmNTAL5OVHTOMzSwsdl6LruEU3DQYyGf3bM9F6tI/qw9OnsE+ncbJ9WlYu/WDFFOta'
        b'fH1KWkZ2jjwih2IWYeQZoGl0ksbb8oegk7gZbaV9oWQVn/IcLctWyKclLCc8HYWbobPO+G4mqPFBiW+d74g7+KgetUzUgQZMhA8WFeTKslFDNN6Wmy5Pnzod10f0R0oy'
        b'gL4gXXUz2oW3zZais+gmOpHmj+6n+cegi0IGX8ZrhqJmdDxaB1wA6Tv7yDi5gq842ljjy474inaxCO/X8RgXjSBXodUB74EvoNvoeAGZumBqyBCQKe8cg89l4K0sAvKW'
        b'HW7PlEXQ3Q58cUQOIS20v53oHKk16cnH0GnaiCmMVwFqKMQNU8lYEfkvD+OhA4nz6Ww+Au3k29U68MhLLlThfWRuSdPSG+hmBCBBIqyzyL3RDKne81JKnhu64shCQOfA'
        b'eA7nMXYz+YTmLTq6CuSiw2QpAUTPmTl4m4CD9ERX0aWGvAQfp6AYho+2oiNzeZEJcyiJVZJpFNSGd+Ez2SJG6MtDx5zzKH5zOLqKjnHQwclolwydETL2TgLXPHxLBxED'
        b'0WW0L4J0bRndUJGno+PAzLFgFRF5erWoDF8K1QEjg/ejE2iTYebmMdbJ+Dxu4qO9y2fSd+EOfBldC6dDgwy9M5E5Isa+XOCIrnjSWokKXJSZLp+B76UTGoU8dDQC3Wa3'
        b'Drbgg2F466KgiBy8A3Anc/iueI8DfahgvBJvVWTMX5EtYIQjeWTAbx/H1vH+MHsypH1Hww3yxcer0Hl2eW8kU8QaUvsZ+Hg23JzAQ2cJ2bQTSdExdCycG72oIRcGr4jx'
        b'n70I7RbZ+OEmXRQUfVKO95P+szk3B29DmyMN1YM+wDvTjdWTg9ZY4UalhjbPiGLUDGAoGZl8bGTuY/jopOx99vPuStSk217V+CThK1YMH5/nRaBNEyqifz2KpwFftY0l'
        b'H26Ylp37s0lOP7/m81H6x5ts3MdO+mvNX8M25GfYnT9z/UzjmSPL/+fmlkfZe9etC038Y2Y1bnUr/Gryer8nl0rH1tYmaXpGf/mLTz7wmHjxy/I/R67xDXm+6Y/qbVNO'
        b'NVz7gS6t5XuS5piXP9AmVKU9nbv/yjjBNx3K/3M4/eOmnAurpkyzlT0/YxthZxuxvtln6IK2eRPO2GX/bp0mce1vP174w7uLn/u4J7rF5kfETvP9U+mJIG1ZyvTjqRd2'
        b'b+nceubDn1rLOxZ4ejxdsXZFquRP88TP6x78JmLDgfX4Z1u2D8uPjX1vjnubLtT+g3PFPy0YvnDJkPvrx9amyLYeWPffHg3ZJZ/Ufs/n1ojUOWO2ZDgkb7444eStpxv3'
        b'3b4de1LXV+I28mXzb9f+qs25T3M4+Zvr+84u+u2yvotRkbF/WfnJAruYlNTD3qsudfzql1dr8/gTY2f8/Rd+C875HECFuqaXmy7+5KNE53+cVpeuDO8+/KvP/6bY/8u/'
        b'7/2L+lbL7bF/bhgztC541JBRzS1/F37+oy9LVYovfcf+fnzj8A8O/Gr5GsEvdKO+VzX/Q9XCpz+6ee6jUf9zSzjxX1+em9uee+Rp4Dl10fazT27W5W6fcOH0yu0O6h/e'
        b'+YNnzM8rn49vxiPzxcFPhXt7HjucUx35Ouoh77f7tsdm9Az/Q+/03/Vm/O2bH3fmLPiTMk6+rXLd7jEfp7v/twcWb/L7oS7GMR6fDCqXHZz055ehf5x35+nN8YVL5dML'
        b'jn7v6fB7fzs3aozdh5M/OuAcK986YtrYnV9WbZnwM9lff1P4GyudbtzVjeVfxn10evGOoz9Iu+1X+exPP1Yd+vOpbZd2/p8Tta4/2/p56LDAElHlT2+GP/uvP7eu+/J2'
        b'45N/HD626eNRuvlf/74OfZ3ytzWXBfOfvcwar0l2+PRIStAytw+mB0yuX5EX8FH9ivyAyAff/yq56UZsVOiQJb1fxd39VfzLn/+l4L/mrl33R9mPf3PlMgovebZMrLhw'
        b'MUX0eNTTZ8sm/Pbz1TM/EmVfXP73Sau6O7bM2L9F/r1/e5So/vLoQFvDmdG/2tjR59Hj+cfu0f8+9vG5xK+T5/0k7qsjaMv3z9WO+veZp/tPl29oez9w778m5p5wuBpw'
        b'UBZMwXW4fcJcPbZuEjpqxNZVoB1UfiVrxgF0AbCRDD9/ei0vAR/0ojfGLyrhpkp8A10iU2UIPkORYSXo5mg7fDu1Hyhzk9Aa70TtVH6NQOtq9Vh1EWONbqWga/xaMq2w'
        b'GDUinuDz7CQenGqcw3PRbRZxeGlVNEzhQ/EG4xSOtuRzkMtQIi6zgFF0DO8wIkbRyekvYC6vQBfR5fDJqyh9Ika8gO9bh3ZRmCC6OLE4PEwhw1vkDGODT8ybQeaYlHz6'
        b'1qUz8KVwVaYCFjY5mUHRdj5Z5FAja9RycgI+lDkJ3zGC3RjHaYLKaMxiCNPQ7lGA7AMWKtfITIsZP7QJ7cgU4iNDaygF4WhfJfBBOzkixOgcP2YMC2LEB2rx7nBP1GYC'
        b'Fa3C517AhJqKb/lryPK1CTVYL5bgyxqAjxuxmwbgJr4mRh9UoCYOw3cBn4J28CD1Z9zBH5ouQC0rAmn/EEfbkLUtrURJkXK5tMGH4E0CtC2mjgU9tqDjy8mn7cEtkaSl'
        b'I2Aaz7RiHHMF82PxNdokjmgN2h6eKycs1FbPGHrbDn8A3aYd72BBi4flM42sDmpCLSyzsxvvofDc6UwAWdcKE/XLGlorfQFgc3QiCR0H+DC+u0KPINabG21Eh9la60AH'
        b'Z6Kt06NNIJcTSAUA2hVdsFvK7sHg3fGvhBC6oKtUPeItg+1UM8QqWbPvZnOQVcLn36INjm/O9GBxlKYgSpdxehgl3kt6BlRwJDqLj4aL8EaFLIPVuYgYR7xaUB1H3gh1'
        b'M5ZIKWcJ+07qLZ2IJXJSB3ZVfHxwMhkNsCriu0wZXYqbpuuX4jnLWPDtBtIPKduCjubouRZ0BLWwplpHiIDQwTEuRCw+aeBc8BW05wVlXdbiC/NNWZcNRLTtx7q0qdiW'
        b'+MBjHKmUQzkm2FUeMwxvFA4l9XPnxUiSZwy6H91/x2vyvFduRM9EHbQDhLughsysdDIHlYTk88LQGfIRdCq4RSTHPZnyUDKTZBJ+KSoGneUvDc6Uhf7nYJn/uweq8TLV'
        b'NQ8Mu9YPGtrr2C9UEeulwLAT1+8u3QN0ELGbwoX+jDTo6IrmFSwEtMPq5tBuv3GAp/Tdv3zX8h63wJYVXW4xn/mGdsqyPtb+ZPkPlnfJZnb7zup0n/U0NKvTJbgnKPR0'
        b'VmvW46C4rqC4jnkdizuDxjRm9wTLT89und0R0BHdGRzXmNPjFtTm8NBtJKQXtRY9Ch55U9GZNacrfk5P8IgO5cPg+Jvvd06Z+nDiVPqqtI8ndMlmdPvO7HSf+dTZo3ly'
        b'S+rB3IfO4RzitLYrOKXbM7XTJfWJj7RlGAA0u30Uj33iunziOkq7feIbbXuchzWFdTkH9fjJuE8TdPvFduR3+Y1uTAOL9dG7V7YsfugWSt+X11kwp0s2p9t3bqf73B43'
        b'H0DKtg1/HDa+i/xzG/8g9CPFh4rOKYWPEln6cjqnTH88pbiL/JMVd/uWdLqXPHP2aSpvE7UpW1Y8co6FN4zavUL/hj4+zyeF96WA75fK62P4HqmAEI0c2eUS3pjTMvmJ'
        b'V1xH1SOvFFr03G7fok73omdupDEeuY3ukUU1OfQEBDVbPZWFkzP/yMf+cV3+cd3+ox77j+/yH9/tP7HRocfT/2hEc8TByEarJ57BLeXdngpy5jyssW73uJbAh87BtOL0'
        b'dUbS3+92Ht42VF+j+d2eBZ0uBc+c3Thb/pYRu96n1KR2+07udAeXbM3L22JvJj/yS3jolkBvZXb7ZnW6Z70ayeq2f8KuCS3lp6tbqx8NH9XD9Sq/oKOrmle11V1c3r78'
        b'gfAjyYeSplWP/HI+C5B3RszqnKt6PLeii/yLqOgOWNDpveCpu+9Rh2aHzpBZj9xnUy9HrfFt828KHgWOe+IX3pZ2Jvsm70HQR+EfhpNCdqY9cfVrsW4LfOSqeOInb3sP'
        b'8MFpEOh3fpv1I+foHr+QoyubVx5cRTJ6BLaktSkfebBA6VndnrM7XWY/04c4bak7vaJ1RUfhw7iMm3N6vPxbUpsntk3umPulgOeewmsUkq8jGcc1j+tyDmE7Zrfn+E6X'
        b'8U/BTxmp9EDqpwz8OuxMfubly4bWbY9p0z6OTOyKTOwOTwKwtPtjWXyXLP7m6G5ZMinZO5XXmAzwYff943eOb0l56CyDGCvJPT6BLfOaZ+1MfeoVAACOx16RXV6RjcnP'
        b'3EN6XIKeC5w9hj5z8+oTkV9wkBXUZ0XO+qwZ0jG8D3j32cCVLeMhPWp3wK7PDq7s9fckcOVAnjmaeyC3zxGunJjAsMcBox4GjOobAiUOZbwD+pzhjgvjE/7QO63D4YFV'
        b'Z2TaQ+9pH0//OOOvfa6QaxjjGdDnBrncGS+/o5EHIvs8IN2T8fTt84IzbzjzgTNfOPODMykTENHnD08FMLKIi/bt9o9DEx+GJvYFwt0geHMwOWsU9cnJM4895F0e8sce'
        b'UV0eUR0u3R4jKT78iQ+56FjywL3bJ6Mxtcdp2H7bnbZNcS2hj5zCe+QjGoWs14yW5C4nWY+Ty377nfb6FAj74ubdaG+i8fBjNR4HAEVHHUiEwCGcQpBVSwzAPBMHDm+C'
        b'P/6OlglYhAegmC0ZDnxlcPAz2IoQBiqaNIaDNk/x5/EKKLTZ/PgmAGdwGXNZnMBnPuTbJUgEMh71eJHzGngeXj04cxD/p/A8z57wLUDmEsq0KrW0tKSyksa+AxgvFwuQ'
        b'1FQFVFFJpVlIPDYqgVLJhrkpkVap6gYUykJEQ4uL8xZp06vKSCvNq6wuXShTcOEL9SA8nUZVpqsEJNzSap20rqSKAtCUFbUVyoFANTMiKqpoxjLqBpBzfqPSsB5x2NA7'
        b'UvD5Lq1QagbC2AYkxNeUqEsWScF7Ybw0nYLhSC/XVECIQPIeAMaVSEt1Gm31IrZYw6elK4uLZeAaelD8IKkffX3AaUWVtHaUYgSpikRSjXVQmdr5JVoDtUaIosUSuW+j'
        b'cQspXpgFApICIIqhWRXpfQuVq6t1NTR0icUSyadrK0p1lSVqFuqoqVGVGpwyaqSh4IFNTqqAvJZ63V1aQy5V2lKFjDbCIFBHqFCtSt8uXLtTiHgVoVlHKpKUD71uqb71'
        b'ldXUs1ENRLy0VKZZAwxs029Ra9vm0G01fH5oscEEfDna6cZ3GO9r1DUmFYzk7H6PoQ5T21/O8PfsKF0WyeZCJMADnApGai0ANc/txVF4j6dvmnPw4pX4Yj7agM4noT2z'
        b'EtO1RKBpRR3W43PkWQoffAi34kPJ6I7fMnTGKQofK6Db4r0z0plGZrVAWFycIZm1gtGBWBWOCeePtyqqYzKyC0LBFg9szMGo34oJWCDEZ3HjZPr0v1xAMZYXajWp2L4h'
        b'ai5TkbpxL19zmNz5e3YF695izFaeszK6dMvJqFNR58vWdiz0yG9a6P5D9y3/WP1yRtSnw9L3dOCvLjGf1hSfaZ9XWvzej6xLRkXXjhi2UHtZubj0zKx7wyQaZ8dhdc9/'
        b'Ne1zUeyVtG2bwWXGkLJc24XX7Tp1nwWvrXl8yf9O69pLTZt3+ovcw744FOV6+BPXbTMCmr4+0TH9ixFRQTHf03yYHOYxupsp0PpGr/+JzI5KzL74XpJ+V4ZuyaBT+DDd'
        b'lkEfzGMNP3fboFuwK5OKj1CLVdg0fkF9KFyO8BscV4DO4TMW5Cx8De+jchxeP3yeBjRXEaHcZj1aXUZE6kYB6hiKdtLtGfyBFG803b65RkS80/zakAy6vzKSIaKc3hjU'
        b'TQDmoKFoGyuLr41Ad1hrULwnjxqDEjn9A/oYPoJueeitYOcRofcAP0IZxgqXW/FJfIWz8sUNM033lFBrOcUj4na0bVF/W1IqlaOrvsI6dHQKK5dvxxuJ9GgmmU+oNTVw'
        b'XFr8rWA4o6hlA5486IDuB0ozpFPxCgIOgHg1N9iyeNXDmXgRvvqxW9hDt7Bf+4b0MTzZJF5PYiowsl8IeLIcMCnzywWTMo9c3jMvP8IWktIIE3lwhd5iL67LL67bb1ST'
        b'kPDuzUktwoPpbfwDOYQbbSnq9ozrdInrCQw5Nq4tlrXpot7DHhKuZ3GXU+hPOY+PZoDJsFdxMwMBkyLBAHSeoSKOm0Ikk4J5PPc3hkjyeq3I6lhElkfLzvQo58Az+Odh'
        b'vfMIDN55RN+Zd55ywjn8VWiBcyhQVXERucwDA+s0LCehonM5WXhSEtOTCkyC/Q62/KrmVZRqikorK0gp8RRXr3cXXgahekrnK2gORQock2i2wWIIm5TK1WI8NQyQGywD'
        b'IESfRkXJrFYrIYEsbBYXHi4m8qA0KFKnZhXT6BG6msrqEqX+6/UVYrFQCGZliAYBayJn96PRVWjZyMQGoiwvh99KVVJSYbH8bR+d+taPpue97aMJ781867cmJ7/9o4lv'
        b'++h7KSPe/tGYYukgTONrPBw7iG1GehnloTgWTqWUS8O47h9mZuBhboFCwd2Wea7B7EpS1SU02qWxD7+JCcl04NLZWaE2RhFlNlqo6Qsb84wdTuSFtRUlb1dTiYVTLZAQ'
        b'zzoa17BzDEsHO9wqlN/CWA7EsLnmUB5sSg2Lz4pKzS2dM9GRdfOCNqGtsRo7/sQg0B0AtPEC2sgCtK5E45v4SlRUlIjhpzOe+ABhCdaidSyTekAOGqMj+JyCx/DRPl4m'
        b'Xp1L4WQxeE9KeM5MXgafpK/ljUaH5rLQkIP4zvvkkYPTYNsY1fPG4evotEzI+hNaaxVKcQ74sogRePIm4Dvj0ZpgCrzAJ9ARvJrc7dDiG2RxwHt5M8f5owulLHotaLhm'
        b'BNoxQc1neNUMuoH3u1AClcvwFg2+7qgmxONTPHS2IExlx+K5js9B+7wL8G4WuqXxpvnL+StIdkJ9qx5WdwKtlvHZmriHz48zJW8F2j1+Ej5ByYstQgfMiCNM7z7/cnSP'
        b'Vc2fw0dxmykhHaIwdN+DrcSds9F+zYhpeJeeenRyqExAiw0kzzWZvpOwf+fG4+vxtFhHdExj9tIC1OGPTi2iVTLBL9Cu1kYjZAQ2PPW4SLQG72Cbej26GWYnUTsyjEDO'
        b'G5k+EZ1De1jHU/vnzQV9vZ0DjxHY8/Ch+In4+hId7DngC0tiMoGjLwDrmGDCLgIgiHD5gBHatYIIEdvwenQX7UGHCsnFHnwXn8C7iAyxB90dKmIIh9xh/141vk0pQ8eU'
        b'UQWkdmMjGWYBk05EhcP0Y5XpPLwbrHC2FRDa0GYeWheYgA+ggxVjC+YINeBCsDzqPthStO6Oo2JCCRETTkRlRD8aob0c1/FTcq5aGBWlvaS77Opae1l5qXjKTw4t+vGD'
        b'vD17EH/9OdnYuZWyP2neu9wT/SlvzoM1stsHhiQ+HvHTqJxieUbms49/+f0z+60Krm6MbrC5cNSmbaPf1r/l3d7n8btlCfKyqE+jLm7cmBgl+OR+Spaz+5cuq8flREX6'
        b'3vlZwU0imwjX/Ma2VBP9ierD0SuOIMlIrxNFe+T/HFf8z/I1L7/3g4c/sdPe883L4Rc4/Cmsgn/qsvIHu1SRfp99/lz5+99u+uP0oMyJAZ/tJdkEjy9uKVq1OX72DuZr'
        b'l3EHo1Oc7kRM8mj1lI7ZLymb6xxY7smka6YfLv6+zIWqkibF4guZRt9ZdrX4FmhkPZ1Ytr4tYDrnJYdqY73RVXRwyjRWWNg/uybcxNzIHp2dIRdYoSMaqtjBhyLx9szc'
        b'8bgDFMxEjhkVTRU7AUFEiGB9tQjReh5ag3bhdehwKL250pu0uN61Dfi1WYTPo0tTkukL00T4kJlwwkfN6GRtPLrNamrbU+zDQUULDL813sonkugtUnwjOs2q004p0VqN'
        b'3dIV+BqgjraSjwsOZwWUAwtS0daaBHQ3jowevIkM22m4jVZAYRk6Sm6NQPfixOQW6as78VVSIB3MHejAWHKTdNB7cVDkZgbvGktEKRD0piajfZxnmcicCHwhWe8wBh0g'
        b'9LI+2mpDNLWoJR1AUOgUgw8CVo5Vfh11tdWgbXboIqoHihoZfJVI4Vfod2TI0FlNrcTHQUQeO03qGe9Et1iC2okAtJtMEfFpZHbmoQsMPozOo92sXLmOiFHkfXdCFsP7'
        b'mogsN62QEoI6qtEZcmc1blhM3ob2MXjLEidWPmsLGWsuNLIS4xZCWcf0RCJMvMYGJggTsLYYTcM0hJleNsTc1ockUYkKgmaBRFU13CBRRXX5RXUM7fDv9IsFicqzcWKP'
        b'X3ibtssvpnHyM2fPphWcQ5Pah37je4LDOlJ6gmQdcUSy8on/PH78rcCbyvsVtyruKPoEjKvnL928ewKHnx7dOrqt8OKs9lk3gzvlk7oDE5qse/wCjy5vXn5wZZOQlM8J'
        b'ctY3g7r9Jna6T+xx9W8pfOgqe+Lirj+F+DVLdy7tDIrtcos1PiLs9ovrdI+DCOEezR4tZQ895IPeVD30CB9409Vj/4ydMzoD4rtc4/UxdfpnejrIUy3DH7qG9niFcI6m'
        b'k7u9ojtdot/9ZvBD15ABN/9nmF9PzKgbY6+MfSD8yAbbPImZ2Cfi+ycQgRYicfQx/CGJPBPhU8w6/rA3FX7UYsFAqwMxo/e2ycqfEN/ZQo/5UC96/n018/UqInrK3lT0'
        b'1BvbAFujPg+G7m79vDn3Coty03N67YqSpubnp+QkpacUsGFmDF6ee+1qSiqqOBcd6sOgPrA1uqFg1QsA7aTOTdSH4ECdmWBzb9DUOTRs4lNpm36yzPP/Az01zL3foplW'
        b'54LuwcwD8HFwozKdjSvT58B4+bYUdAhuxjwo7XLOqAfFl5t3S1yH6ObUj4N7hnkNOP3CSujlUJ/5lb1AEv6N7QRJKe85A8cvJvFphBTZlwKeV3h95jOIeyLrcZkAwVEm'
        b'scFRPAOeOEX0uCSSJM9kXn2GMQRNLESIGUkDxHBBVVLguck803gwEKLFNZENocIFY4HILl5jaDAWLvIKRIhxn1if9rW1oyT2Cynj4d/lHtk65vhY8lOf/pWQJ4kC99re'
        b'cIjvs2YSeEm8bwR1PInPN4zx+AU9PlcLGAfX5sBHEt+v+V4S8mmMg18fnD2PhxuFjyQBL/hjJYk8uBP4BT1lfXTDUjOBX9XPTTCP8ZwsDHOvcEK3zRh6vSP/L9eDU24X'
        b'sL0yuuWeKQCX3Kw77kNCziE3ew5uuW3IXzgH99zgnJtNN547KYcohyqd6bmL0tVwPkzpRs7d6bmH0lPppfQ+ZDdTqBLVi8t4Sp/1BpsbcOPNOZzmKe3I0R5cT5P/Q/X/'
        b'z/metWLz2pC/yhBOgyRQ+pm4o7biMyoR54w7wOB229pYNvkPpfPL+Fy5ztyvE/xWGNOHcjTArw35b1smVAaeCzKjIRSckwMV9Tb1kvqh9S5l1spgE2psqINuMfXEO6RM'
        b'TJ1429YzS3gz7WgwDFnvUBg0STTmN/XrXqZSvxxhJpcNzMBGCDXL9FJBhLz4Ck11vEarpL8joqJGjIgHWTF+iUYZD1OUIioqmvwnUmiMTNArzMnNz+4VpqVPTusVTs2f'
        b'nNfO6+Unp5CjDbyyKDcna0a7UA2QwF4R3ZvptWHDv1eQU1FZZUm55k1eGw2vFappoHYZHMIEMLum5xSwoTjesKwxMlG/stSxtMCC5GkJLxPna7U18ZGRdXV1Ck3FkgiQ'
        b'mtXgYSailPNuoSitXhSpVEX2o1BBZOuoEQryPhnfWH47n3oSV5dTxzK9Nlm5SQlZRUSYfjkciE5KTKcUkt+8kqUw/eWDCkmjJYUqomLJkSwxUFg7Tz2VDX0C0dN77QvS'
        b'cyZnpRQlJhQmpb1mUdEyAUuX4ZNfjur3YJK6WqNJpFK+eRlZ1eXZmnJaUjSUxDeWRAgcB2U59quPl56Df9RLV4uVJ7MzKwW6m3qihbLHqCFkdP9CxtBCYtST4N7gL49+'
        b'Gf4GX9prpVSVlegqtbT6aVv+v3Pn8u0mwlSW5tvPBAsJfBqvIzIAmEjgBny54ua/jgqp8fCTv/xBbzosYS5usG3hu9W1DWI83GtdpK7WaUm3ZwPrmM8nCv1NMzviZTLG'
        b'3ecN7UMhMPQr3zBeZGIlWid7CyvRdiuWozpoga06rOetzExJbfU1zIYpG8SUlEcNR8FxOnWZXmZrMBO1/87MRAGYsNbKgnohnfWpU7FMZaJkKKVVyOq5YdZ/hVKhQFdT'
        b'U62G/coaGmmZsqKa+IEZI6T9RqY0NDlF9upsMLK/NccYaWiYpgKU5rWjFCPDXqNIdrKQhialfXtmblKAzHLpt71n8AlLGppe+EZPRL/iidede6CI/kQPpr/h9qDZzVrW'
        b'3ZFSNU9brTYEiR3sSVig2cf6d5sadUW1ukK7lA26FBoGy34YIQgW/jDLW/phwA5AHlicw0B/EwaraphMYcR1jFSMUETFc1ksF2OEgETRrFypxuSRNJkterAPYx3PcZ9m'
        b'wXkcWz8hGuo/btDqoZrKeHN/WXSQWXbwxvm7GpQmo9c2ljB2vPZ3vwYOzgwoIAsgH/hD7ulAbwgqNarKoAgkVYkWOhT5qKX9PeQBBmYQp1ugDiHl1JWoOcCSSZBhWjvS'
        b'ApUKvlVXqZKWaAkjN0+ntUxWUkJhyuTc/BlFeVPz83ILUoogqnsBpdIAFqIOwCwgjrhKYichtn7yEtJz9I4f9e2mF+Q5RY5lbI1RuUMVhmwJRt1LWL85JWxQdBJtoRp2'
        b'nGpoJfZ7dkwY+3X6LBVVlj2Csd7rCAvM6oMAj1QlTZmaP4iSqkpaUFehXaZSV9KG076CeHZCHGQskQGTri2pXEofHHyGCxu8z3Ju99gGMXrjg57PNYnBMx+rLx7ki7Qs'
        b'2MokKpvZs2Y+HQedtWhJAxR4pHo4Pk2j7779yrXcJlQqMR0p6YkJOdJ5qsrqqnIo6VsUXTYDWDCnHFbpsnbOErw7E2/HjejSTAHDx8d5oV54C6tOuo3b0SV0Gu0yjbNh'
        b'jdazECvgk3LRyToIMYLPR3ExRtB5dJM1yV2LLuKTILirctE2fIP8vYI2CxkJXs/HW4VxNOYCOixENzMVEWHvo1bOEJ9hhuJjAvLEUbxOB8YX6MBQdLBggM2zMRrHBbyL'
        b'8wQBnrvxDVsbD9Qu47P6moa091h9DW7Gp6nOZmL+cGokmoKvogOg5Ml2pmqeifiollqz4434Gm7WKw3Qbnwj3DQYisFauUYiyYeALKEROVNDQ/EWvC0Sb5Gj9kIu2EsE'
        b'7Kjvd+bFocOpbG1vQUeSaSwQ8D/BBQOJQa1U51gzQ0x1jjXKhZVPy50YGlYmFzfMNI0QkqbIyMabyXdH5uP6rClpgny0GTwa4Fvo5NKFi4IZdF9oh5tKaypmL9gl0nxC'
        b'ivhcVbGoMdsWRTltKF/QG7vZNXnnMavFf07/TOlat0hW2Ntw0+PDkzdDj7Tsjz35wmrXk6CYz5fj0gnP7UTbUng/GHUjMjAleoPLTukvvlgT0Bhrf2iZTUNQxvxlvrc+'
        b's647Jbj3h7XPPm/5Kn3Hxp//mHmSsiluX+PhLcqAnZ93HftN0Mx/XHLY9ANB+u97bo+yuyHV3RhTPsonW/K31Mxd0ydUvFT4jv3vG0Gf/Hj3lIZZI8796eef/OI4796E'
        b'r2+MufnJ8Mzz4br0C8M27x6zUORa/1u/4/ciuxcoZRJWfbB+GWpB2/G+cEUEa092gh+FdgmpdVB2Kd7MhmGCMFJywI+h6yusGId8QfRUGdWkpKN21MRqWi6AkTunban1'
        b'R3fo/SSAdBlBbNOmcZaFeNdcqvqJr0MXAcGG9ipZBFt9BFXgxOOzaHWmoaeg09NZWzovb0pZMVqLrptHfMCH0EEKBqvUsjZpR9GRMqNaJa0A3+DUKrgRH6J2XMsi6rgM'
        b'QQpTn/6cR3+0HR1gPe0cq0w0D8BQPcpdKpzrM5atw03uZKxQ1VcGPqe3RVwmoDfn4Ks55CUwZq+GobPkbjYvNQJvYPVM10j1XSBzRhZPNJrhz+NFT8MHZPbvtAULG3em'
        b'2G8TJ9YWhS1Tf/F8VqHyQhnODBnWOSy0LajLafRNtwdBH4s786b2jEl+UPbx/BcC3pD3wFbF0/eoV7NXo7jHw69lZKeHrFEEahELdkPObka7BbeAlsoutxE/9w3tGT3u'
        b'vuSO5MPaPgEvLJfi2vIori2P99TNq5OU4RYJZjIML4xC4L4g2SbTbGk0WxrvmZe0JzSiSXhI0iOPbhI+cpc9c3ZvSn3sHdHlHdGmeuQd+xQ0MN77Z++c3RLQEt3pGtzm'
        b'ctGj3aPLdcTNUffH3h5r6va+T8CMm8zrdB1hIsdKTFD/rxQiB8fHQUBMM0z+azZINki/4xgOgD89DPyJf/WmXsWp58wWcRTTYTf27byKr2edZYuKQCIYzLOvpe/Q+/dt'
        b'IN+hBuwj699X8RpiR38v37ABWZCWkN8rTE5JLOwVJuWnJMusLNliqL/WB9HstSqdX6IuV2nMxHtH/VfXk8Ne60E9RYGfKKt6ByLeg6DvSD1COdUPKXP8z/iDetZmSdBP'
        b'UCoJ92mKXdczOha2eQ0s8sD9gjJpPDDw8cUGJ4nFFkBPco7hNPj/BfD8QFsD8nZTgkoJQzuPCA7VOq1RjNBCxWs5Ieu1xFdO8GD7xWtIsCWLjM+aksOmS0s00rLK6hLY'
        b'RCIiSAVJqdItmqeyzO3D66oMGybAO+rRlQm0NEtAKZYKM7HOlAy9UKdVLWFlFqgV1gfyIhb4PwiSn+SpUALDbawKtYqachDK2G+QhhJC1fTTKEMdkJ+qUCgCZIOIAixu'
        b'jFqllEBv0mjVulKtjpRuLFkhTdXDLk3uWyzP8AztmbqaSpW+C3CYViJ7wMcS8WgRqUqLZYTmp6SmgHo0pShnanZiSr5cqpccC1PeK5QNWt8qaoYCla2qUkZoqyPIj0n9'
        b'hFbXsGY5ryhhiSVhnKSq1GDOYyqMv7I4+GOQ1aGGXyVKG3xSc73aYmnzqyuVZNa0KHVLSa2k5OckZA2UsC1brrym1K3UqYrAioWtCnIlhSvaYbl+A+NCqyon/YJ0kOLi'
        b'nOoqmCleYdKzRGt8OxQGpRAhC8xoYIIwdN0ydfUiUlXKkkFsbyp17OZmeUWtqkrf88nQVAL+MbS0ukpTQaoLSiIVV0FTSS0PShhbjOmWkMz0M1lSq+ctUP1f9t4DLqpj'
        b'ffg/Z5e+VEF6WTpLL6I0pfcmXQEL0lGQbou9USygomADbICKNBVQFJzJjSUaWda4aBJjqqlGxWg0xXdmzoKL5Sb53fu5v/f//q/3Ztmdc8708syc5/k+qcXMfPDmTWhM'
        b'pMtkewfSuVHjkPLgPFiLvDyIykvOaPDYRJPiG+PJKCkkY42MdmJO9PadOLOIuXFjRDvfIu6irGy0mcbWSUtQKgsWoMGXUsjsf5mb3zy3FBUtTM0mjTC2D88vXIgGMtFK'
        b'R1Uramw0EJhu/+bKfDnL2XIj0I48JT9/QXYq0czGRyJkPIlbW7157Pgyc0aKaFJEqeP1nWuBPnnWXLzKcy0i46J5uDHwas+18PGPeMs4tBQzH5vMs/wLRm1jaq7eY1P9'
        b'K76y/5n6/J8cBxgwb2RCC0pHt/rwONyAt/uhYCORKsketUeL6MVa3DGZaz04xZw5AwAt8LgbPgSgwAlv0SHAAesARm9zLdzgXTSKLeShndkmd2VGU7QBnFmM/UWKYIcN'
        b'YDvYqQIOxpZg/2pB4CDow2cHYFM8KHv18MAM7C0JRXdFu+LNMfFbGYu9osaKcF2hNpbxQdYhcW86LbBFO0MxH5Nt/iqg0hVsYErSCQ9ZirQ7A2eRs4IVsKIkAV86BWod'
        b'35YYLJ/6lvReejCOshgDuvGkKDd7NdgOj2UylbTaHmwl2qbw3ExyEgG6ppcsQVf0DODOUMK6tAmJxCg4JhJJuA2ulzPVAi1yL7f/XnA13IsuHJgA1oNDsaAhLQqU+6wA'
        b'u9Gu8xj630H0d8N8tI1sWAyqwBGfebNBhU9hdlRUzuxC02RQNz9LmYJbpuqCvbA1ltGCrYyAPRx4Ol+elTuJYsE+2m6ucUkcRQCaq+DqN+QMHMxnMgfLtUC5F6ieB9aP'
        b'y9V6eADuwN+xQuxcJbiRS4HjUSqas8BBciijjXaXO4lOLjxVgNVy7ZbmlODOC07DqqgxRU5evIhqmV9SAreAHbGwKl9BCW6LFdW72HENPqXBjTOKvdskIkCC1aBZhij/'
        b'KsIyddgaXUp8ssKjqK4OvJk9KqJG4qdixZvTOAlvijcqBMavYDSBN8BacDZU3I/1ZnB8Ou41YBeqXRRxKMHwoe60XbIoBFRMQN27Am6PBpWggob9BQqBqKE2EvNElAQ8'
        b'MBoX2GM7Fl3Qy81//LgYwXoO2KFmCo9MBE3gsPpENgXqwlXA4Znckmm4JtumuL1Eho4ViwUb4Q6UykkPsD4YHgJr4DpUw0Q7GWybR8GN0fLRsGoKYfipoDHfJuauOCyY'
        b'F2JjO+rV1Rp17TZxDqkoXwrjRw2aY/aVTADVsFOZdKq5xlnovuMSDFotKujt0f+FqKND1ECfG6wmHdlKEuwlx26UZixz6Ab7A4hGHJlsQJlC2utuik+xwVpwEpyHZ5fz'
        b'WBGx2Z6GRRJFH6JN5MdPuJtj348AXmr76qY12qx/pEyXa2vs/ub2Ps+7Q0pcM1V1U8PEKmWnWd/kBSVre66pf1w6N+d7+a15ck/3Lrvf6/T0iftv3hIPy379eJaqyf6Z'
        b'qka2fokO0QaXE9Ndoh4OR6eqxRiNREssOW12/cMvDXMeT6/o7ZY2bUiY+oE0nN9XkpI/R6jnXOdgxtmreSPkWva79qfMhTKmtsY3VPrlv2PNc7ga9MTT+cKsBsvW7p9M'
        b'I3w2lcapyqm32p/0Ct46s+u+x1W+ZXF8Qtedzx6nGdRrulQH3FKdfd2bb2XxfH1f/hMwv2BZ90ici96P05XWPb/l+XOi99SGz77Ud1GS7FsxWOL7zWwHK953Aes97O43'
        b'LzHVuBY9scb6J03T66sWxf32xZaZS/2KJ13NPCB1fP+VEBmn0C2JpoHas3LOpXcv/O5nvw8PzP41UilvruyH6vO0ne58r2J+g7fvnpdgtdLDz+ia7dEJZzbf5C0qzVeK'
        b'+37n0ezTRuenl2WnPo7NMJVSil4WkmV36t6uCfcm3nm+dF239JyzZm0jUkp150onZ333YJXrwYwPpp3P82xbxunSvf/JgWnv5H7Up/pps3xvebTCx1/+erR+otuq3tLO'
        b'YG1JySN5X08Oq31cbZd6dYlPzUO7lMbaD/Lf56mTQ7NQ2ING0ksUFjiRTU7wckReUZtTKLGDQcwHEh0NFsNKcjRoDPd5EuSYNjhKjgZPTmU4URWOmmMDRh4eG4U7doIK'
        b'oqb+DtzkKlJEBwcjRadxmPzF2LbugkfA6fGuYOOURY5gtzgxeTuDluxzIn6YTRBoWzjmcLZRiQCbPL1Ax6sOZzdKLM2SmQyriTK4cbLDeP1zeG5aaY4Ec164ClS5MXrt'
        b'8LwpUW2Ha6WhyAK2QToLO+oIBsclqAWGUgtYRnCDM6OWXaMNNjC4tdmwHftr9YXMKesSuGO+2FGnBCjLZo46s4wZhtMZ0BIx6rwUbAt4/awT7kP1g0vmjpqtddQJNjgK'
        b'TnqJeFDlYDVBvqnJW6PL1qBFIseHkrCmwRmTMIYlVQt3e7zip5YroQGqZsMauJ4UbsE0Q9E5M2yGNeSsWR7uI1l0hEfh2tAwWO0fDMrtXmWF2oMeKTtwxp408IwgLdJz'
        b'0FIUaSMFdlCUoh97Kjw+jandM2AH2D9qe2wItxJftBxnxkihbgZsA5V24TY8lIdD06Wmsrhwz0Sexv+GsizO0KhQ+XZKh9EbztbeRG/COsDY5UKGDfb1adZsdkPD4Zae'
        b'cUNAs19beEs4BiAF3H3z+SzXpEm+UV7IdeBzHQidietcpTBsaCHm5LJK8a6JhdBkEt9kktDEhW/i0qMnMAkcVDYcVtXa5Vnt2ew86Og7aOnHV/W7a2ReHTo80aghbWii'
        b'ZfOKAbUhO/+7RmbVoQ+kKBOH9gi+sU9VKIYT2dXZCbSthrSD2qW6lTqUBpz59kFV0g+4o24yOxZ9rG3ygKLNJuOjYk4v5yGbNvMjPjX9iU9Nf5qB4rhWuzZIDama3dIx'
        b'Eh0Ye5NzYh9yTuxDf6ZjLPJpedCjTuaumAr7yyfiyRMJ5IkE+q6GProuAkGNoq3En9PQFz3nT54LIM8F0BjE477bneFHCfSjBjWjRk+/4watpw6aTOOrTkOZ1tTdtbx6'
        b'+aCGfXsCwzoacg6/y7VpVxviOveYCN1Ch9xC+dOTCPwoTmAUP6gbj72ZomeaJfkaNu1WA2pC72i+d/SQYzRJTMTF+kxDv3FZ+/JLikNT4ofF8hIm0A8f1Awf1jXGPJ92'
        b'6W75TnlRAXxIAXxJAXzpu7rc+rC6MKGu/ZCufXtsd3JHstA5YMg54I13P5DD1e9e7S5U5fFVec2mN1Tthw3MqoPuGhhWBX05UXtQx6a5mD/RbyDhUsZg/KzBOanD/tMH'
        b'oxMHk9NG2LR6Bl3FQrVhYFbF2sHBFTUW1aCl+w1Vj1uGFqj3BrcE96gPWXveMjBqmMS0osDAvspnRxChKmHHrc3yfNVJwxZO2Pmp6bCoxsP4KDcmVlV+O8LvamhVyYqd'
        b'6094K83n5QlyYdrrxgZ/ZVhjjP3rEJ6/N6KrJMUdi86ypuloQtyJph+Rz7/zCgBvUQ9LOVOnON7U+HcAUqOb1yz0USNFNBkZHWTpMpkyKkNqTKdR8t+p0/h87mt76uj0'
        b'vLT0wqI/O9wmJ2mi3Ts+u0kp4s4ID/uTLbo+9eoWnRdB9idBsMYi9KUmfNSr0PLKBIvXiIS58BjcC1oVJs73YN66rwKrXBmJN1fxFZn3fGw0kZmT7WEzIzP76TAysy3a'
        b'kGBxeYoUrMNXim2RDGFbij5CYHcmNkozmS05BTbakI1cNtzriaOWoKbCtbQ+2jL6TyARx872hdtDPdSxzoFI4WCOB8NNyWYTPdW7kqkLtqTMohglhMOgy9YJVoHayU72'
        b'GHS9nwL9oA92Ec8LgbDbCm4vcGMMVEE32MLsXHeELuTIFrKpifA4DVso2CoHRZ6otoC1sNWKtwJ0WmKw5BIarraCh8iRxGy4Fm23sYAUIemPJAEpdZY8bAeryIMGKKUY'
        b'uFkCG6EdpMApCmwF2+Aakkcb2ABaY2BNOtjlNIYVh+vhBlITBmB/IkcB1oWLzEk94SpTEuVSh3xsmRq+ZMw21RAJeV3kGjcI7Ty60K5wz+xRs9apSKwhEcZZw2pOaQg8'
        b'oJAvQaHkLJNBHzm/8IGbOfj4wl9ZZJ7qifbGzSXkxXI5qsI9MWAz3BGHNpQ1ceEJqJPLRNLwZC48Rao/dOYWSpemNKn0AttZ/k7MiQ+72JjCnhnmBiw3ep+7lAlcQQcz'
        b'PgDsi0Lu+0xlAq+lK6BnKQvl9NSw5KBAJjDCV4OyxkoNc4t177kkUYxmyP6F4OQ4VjtbuUCEaketU0PKUmq9kgNPoyo+ly/PYg4fwAYHpg3Xo37ejK5q2RYosCm2Gu0O'
        b'TsOdJMHfzBgtivaFmfIPlPOxczLilOTkVHCEo1DAHm2DfLCbXJjpIMkphQdMRUbAdqAd7mbsrGvQ7vco7OJMSVJA0y/bDNV/PegfpfcfB+vQ+IjAtNwIsJnFobmgJ4pc'
        b'0ncEBzilqJfsgqeVWDhSF3jYmPRWTbYLB3VKL1/UPdCeHGzVIuB30AQ3gbOwSx6elqbi4SYabsf95wzoJ6bAsNU7gAPKQCP6HkVFwU7QTnpdIRtVgoWlFewIoymwHZ6S'
        b'CWElYso/ibQU7FoCu/DQDKPhbrCdkgRrabhzFqzLPvlsP1XkhybryRGcczN/na8bp3Z+0ZNzXXuWf3muw+y22emKNVl71FU4p2P9shrXWARUbfLLM/n8yHvNThaSNUE3'
        b'ynZWlDVwDxxbo6YysdrIUu5A2d1PjX5Zm3n/A/Tv2X03wc0f7JyK7j87P/LJxY+XffBD729LUspby1tbtqg9786rl72/Lj/t+tL4vHBeaHv9lYI9qT9P3x+0+sq65kkd'
        b'nYZXCr86suB6cMxVlte9pVk+GYfyWyseOEboOy2QsQu18b/j841UY1dx6ze/pN/3veradPer7JOB++Y1n/G6nrquOd/vm5ji9F/dQnv8fa/nNGQe1r/NCwvsDcm7bNX2'
        b'Y1Hl0QtRaXqSbp8vLTv4/nc13Ue2lOst+1b5k49OtL53Lavt868/ueIUd+b9+jp549s5bt7vHk3KP6adlP9+jpTlp+zWroGcY67KMRtqz/V9yAu8fW+J+7WrrO6hpe2H'
        b'8n8I770/x8pw4/FfclOHMt2pA3HZhx6phEe90Fn1QmZzxA3PQJXfJ/Le+fhMQXjeFb1b6rt/Drij7dea/TicezI0J7ck6mmBt9PH8oGSn3137FfY0SKdKtAcnGadobFs'
        b'+sU+yWbbo2vLa24YheSs3pYRGfxTzsAWqWHX1jSHlgmZkz4w2DSS8sk9qOudK/xes/vwNzZ3yy/+mOa75SO665stG/fIfvEp3begZEfSh/s+/nrTP75QfbGpz1pqqFg3'
        b'y/Ko6schqYUaZUVTuv2/1jO8/9nk3/WvfefgJvv4F6fFsbt/iTA8/2TFtdLd3aaZBeuc7ny39cP8iU8VowrmzJu4an1s2LuxxTN/irz6nErbt8BfeCF63mT7lctLnod7'
        b'pOke3tjzY+3i3LRbiSrv3xyS2BdpfOirlPtfbZH/4L3vbz6J3Wl/J8j8Uo5b/PCu9FV2RwMbStYnKdw2+GoyjJh08F7mREfPyesOf7r2YuNN81UfXr+lXtJXUrZkwtGg'
        b'Yc/MK3V5HbOHzo8cKNgwpad1eUjb7SWtj759dykV43eh4NqTH2rmJu0xNdva/YXzFyeHXZXnSPbOvbfrE721i/evddu4r3nJLU/v43fX7WvM9Nx4WfJ6QkmRqhu9f8rT'
        b'E6lK05Y5C4/sdep+POUT4e+3/9F6rCujr+tiwo0TqW3S2deWKrT13sz/pmL5muTub2/K193jDD6fcDKPnj/r3IKbkbUJ3K/j8hQca28O5C3zen7H/ZL7YsGnq36jVD4I'
        b'NgOfPs6M/UknruhH39Y5ex5dnXXN1s4zs2+p77oS/Swlow/WWBdOKTp7R/7ZTw/KDeu+Ukl9svIr55/v3dVNm6Z0vORn9e6j3arL1ox8t733TvA/FvVdeib9xKPioWL3'
        b'BuuSn20XKmT+MnVA2inuKgzoOHHn3uxv9nIlc1vvspupfVf4H3+6+L5pgrLr06/D781eOrn9xDSJviMOAfwNsWypd00T2FLnd3zoVaierKD5gHds9ZfW2Udp9vem8ezL'
        b'97aiiz/cj2Ub0O9U5Aw0TPV2fmBg9SI17yD/TNz1r5umz3r0VDmfHVfvLfnJJ0+Kmqm9s2qlf7DRoE57P7xz4+H5VQ/Pr7vZ1vDznkMV++bXnpH6bfKK3C+/L/U99pv6'
        b'4h8lf/5okVfo2mfOvncqB/q1niqdD1b/8KnvuWXCK3e7Du1d+Wv98eGO7q1p65PiPVedVyv73XxgdqxnkVW6TX/+/LT3Vn7VGrtw08X+CJ3+z76WPn959/mP1efN7vf+'
        b'/cU9DZtY15hPbjz6feW9XLcXv/Nf9Pv+tFXjcIqn3B8dlHx2yS8/7+qy2ya8Lj3zic/uKwn3gOp7V14o5R20yHjh2dv6Qu9w0qLD5ZO+VLj27qeHFv+hPe1ihNK3bcLg'
        b'7hsrN3687TnnG8UTTd/Kb3uuu9SyMCHxmUZYRQQfuPEWEDqXH+yAW173PgqrQb0B4350nxo5YZoCz2e8PGTxhueJ5hnYAyvJScbMCXA9Po6QhavGnUjMVoHbyalJli84'
        b'GQo3h4ou2hhTlJI9OxPUgAYSga+hrdihCtwPz44qkNX6MRyxCp/C0VMV8SMVcMSAOVVJAZWMLtquYLAW34ndevRMR/cFhUVIUuphEgo6oI8cW1gg+eKglQgsH5vDoOWj'
        b'YQPJaXoOXFX0UlI1LKQpBdjP9gKbpYgiW+GEBUW2KG2bwiDjCJ4sklq7iMYeLGdTk+AxqRi/GHL+snKahuhoh86CVZTUHJYlaNBhzp26YDfsCA3DZ8kdcBVrFj3FHuwh'
        b'hyYTp4Iu1BZ2SDKmF2qgnG1lmcJzeQxevIkNOsbQ225wtQxmb7uDfuaobk8x2MaBZTYoyk2hbApucpGGJ1mRhqCHHMbxIuH6scuwK8wJbEElA2VIRgG1cDNDKlhLtFIr'
        b'beEJKmTUO4kNrCcXQ0HLMiYCm2Cagm2FMnKsBNilQHwoK4JWqsgSbAM9wXBLPiFFbI2QppRBO7sY1MEOBk2xATbBjaGEBEeBzaCZkoTnWOxUsJX0Af8QuA52hcLOSA5o'
        b'sZBCS/9mWdjNAocXoKbFRSyBh02LMKdfFjWOJBUCjsnBLSxYCU/Ik+t2iXk4g7I82I7KGOjNRuXrY6uilBh+wxRQDg5YgRYTs1HMBRKdm2A76TcaoGMubkpUhu1Wtjw5'
        b'C0vQIkFN0GTDVaBrJaObeHRqFsc2FJ7mwUoaH37VySiykmAjZGB7YDUNNxVF0FjW3ktkpWZYBXeSY04PGVQLXcGq2BNBB365hkohSamos0FdicNjvD9BY60e1odGWINy'
        b'O8bfTDvoxP5mdMAaCXDEP4gUIdfft8g2GLTJo1vmZaN6l2J7gh2gnTlPzAQnOSE2YQWgNQj10MgFRTya0oqVCKRBNzlPDAcHYSsOBEcLKXieAr06WkzJzlqhhsHejbBr'
        b'Ix8ZSdSgO9gecI+TqG8phFqN8fL1M0XEfNAKq5ijvjZD0F4UvHSGJQ+JjmAHjQT2s7CFpGm7RA5Va6UkFQj20RwK7YG2O5PubGAyS4xw4gR2M0fLO23IVRPQAHoxS796'
        b'MYHfE5Y+PAgOM1CRJidY9vLkVALVdiI+OVUCx0lNmMJ6uI9jgSqhIAyfPu6Fq+XgbhY4GwwZJoc/6ID7cJHCbVBLlqnJOrBArTHqiPjiQhrs49jyLFFLoXzD6liZbFa2'
        b'PxR5nlgrBcqsYJmdbTD2tBMIOlBtgM3sebHzyOBeoe+IEi6IoF29UQ9uolFOuuBRphp3JQZyeGho4PpAovFa1P9raXhqHmgj1RgAT4F6VCp1K3zkyxz4JqA5C0frDNvM'
        b'imwlIklp2bCcBgdBtRPJbn6xcyjzrkmKykTTeQgLder9oJa0rAvqd61FYTzYSRxFSFL6iXLyLNAgG0yeTciFnUXBlrzCsAhbdXAWzQh2bBlQ7skcgp8M10IzBeounfMo'
        b'2EOBE2CrI2kdsCMVbEE7ILgaHi+EJ9GGGJyndbSgyF/IKdCSByvDrEFNyEuHIYGe5FWDLNyvxOxA4JpkvANJMWdeBFSCMtj28iUGPAhPMXrI4Kw2idYZ7o5k8mpHY45V'
        b'm5wXC7TwSsi0rArrtYuw5z9UuY0eeISh8uK8q6GJGe5C25Y9ZKICDfE5RXALTw6csIan8Qt11Fc70X1ayhJo0BmR4oWCI4T5hFYAdMkxj5KMp2GFMaxmPLSsKQAVzLuB'
        b'BHP8agBUSpEMmiSBavyKshSipXOtDCWhQs8GPWAvM+lvQ0N6WxFxSGYoSYP9FNw6mRnUi8AxtGB12SmvhOUWaADB/egyrJjHzCobPRejDFuELLJkUYk50mA7yxWsm0Dq'
        b'bDo8kIn17CPxQUo56jQaoBfVGYudFj5K3ykHu8ChUe9QqDNv98L+q+A5uIeZdbbBjaCsiCxkaNaF7ajcB8n6oQmOSThoLyOxWGCuFJn6w2iwDuxGHXsP6tiowY4zPJo2'
        b'WANq8OyJJzZcm6isdXLwFOoWsKqYwdlsA9VoKq0kfipASzQrnrYpTSCZAIfQhZYi1Oyy3j6wfBH6QnaHqnA7G02K1Wqk2g0MQWWojVR8yKh3rCUiGNAEeIYres8Ae+Io'
        b'/J4B1IJdTFtV0Is4JXB9goIsqlhD2jsBTfdka12vAtYVwU14+J9XYKnRxh4ZjPzQbwabmaIEF6DraEO8CosALWxTsNmKdA9ltqOYz7AZqTLEZRg8IfvYHEfQDbrmEjCq'
        b'HawIV0ix5gWHozld5P3GxUMK+wSBp0nFTkAtf/7lC5ZgsE6KecFyMuMxtsZFM+xuRpp53XOXmNcu7PUzDp6QsUOrSx/z6q2/AG7nwM2g1QzdblMQjGdmFTRS8bQB68gk'
        b'qYekr4Mo8dFJOBN20ZRiDDvcF5xnBI7dvhzUNZgBhz18yvmzwNEwcJZUu8VKfJQAq2fxyKS/k0YzQieSB3GPVkSTJvNkhC0SBo6jCnRmy1qYMBWEVkJXlPJqqzeVhXg5'
        b'AVvBZqYcWybC1agcUnA/KUcEj5TjNBv1mTIktZAhfT476TX/Z2AL6DHEHtASZpC5THoG2M6xsNG1scS+Bbtp0LwINjGz8l5QAddyYMWo5AT2y8lQrCh4biUp5xx4CBzn'
        b'2MJ90bwQGj17ksYuXbxIZ9GGp2AVLqhDrlxIOO416Hk1sI6Nl+9AMt9lws3BHB5mdsXT2hRcj0RX5hXesRJwuihCEZ6BHXZI2iATu3IOG2VmPVhDhkyEDRYarGXdbG3x'
        b'rFCHVkAvsJqZmnuQCHmQg8cC2PYOi0frw5pMUhuF1mg8o+UAlssyRWrlMOMZVkm4yYJOZlJZg6bEeo4NWgBpBVBLSemzVPPhSbJizPDGxGd8FmtjSVNGbBk8jHeCk2jg'
        b'4EdXgk3Li+wsYXsQaomlAdKgjxUEezIYCxUk72yDXTYR5PimFmyjJJfTsAY2wE6mpY6h2WgdrERCOdiu8IrbGnhwOel1U1HT9RXZhpTwZGG5JBLh9smxWGBHgQKzTBxH'
        b'4s5JkcwdrGQBWuwmYQWrXrarijp53hYeWESsQM7CQ9gShDEDgdX+omkI5etQqG24FGUH97GW0B5IzhJ53jqqJ0vsQygHJDjPox1AlSOznh21BfvHGGbZRphiBlan2PG0'
        b'/ncJQLi0b1DSE3dNI1VITvuXar3hPQhzibzQzOcwLzTfsSc+5Hcs+VjbbNA8RKAdOqgWiqFYOnU6Qi07vpbdoL23QMunSmpYXXvX/Or5QnVrvrp1c5xA3amKPaypW8+p'
        b'4wg1bfmatoN2ngJNryrJYU2dIc3gBokmTiNHyJ3E505qjxNw3VHYgP+ALL6u32DSZNVoNahpg34xb96GNEKa04dsg3skhC7BfJfgQV5IlcRdA26V/C0Ds4bSPSvRFzVu'
        b'g1qTQaOBQM2hiv5MVf2Wtk6tX31oXajIJiVVoOvY7sDXdRZoT67yHeYaVwff1dapt6yzHNbUEmpa8jUtBZrWI2yWjnqV7wO0KJs0eDdKVQV/qW9UFTBszGvyaPQ4OK0q'
        b'bBglFMZXs68K+9gYpY19khxcITCeLH5lWM9MqGfD17NpTmnLaslCCdTL1ck1TG5yb3QXaNrh3zJ1Mg0T9yjhr6iOGvyaQhpDhkxc2ycPmfj1JAg0/Yd1DWqlhzR9Gryb'
        b'ghuDm9Pak/m23gITH1G4nyg8o/0dvq2vwMTvrpbekJZXQ3yDNvqDnZp48e28RihFLe2BlIs5F3KGDU1qE4b0PBgznPYMPs/jEcXS0x8wxIDrYa5Jk2yjbHM8n+s0xJ3W'
        b'IzXEDRowQ7XhS+ujytA3GtJzaYhtmtk4s92Mb+pCnuxJ6c/qzRrmGjZJNEqIXRwy9e2JHzINHygVcCNQFJ76D5RRDPUz62Y2m/H17Id0I9tTuud3zEdJm1wwGSiF1oLJ'
        b'kahFagOHdOc0SwgtXPgWLuhrT1R/Ym/iJfq6xGWJS7HC8Fn88FmCoNmCqXNGdBQDae0H+pSWdr1CnUJD6YGV7RMfUbR5KD2an3js2EhoOpVvOrUnR2AaLOCGPGKzzP3o'
        b'uwam2N2N0GAK32BKj5zAwHdEkq2l/UAGRyZVJzWsq1fvV+eHepNuo67Q0JFv6CjQdRoeezvL17UfoaT19Nujumd2zBzmmg1x05sntXm0eAitpvGtpqGfAw4XXS64XPK7'
        b'HnY5TBg2hx82Z3Bu6mBK6mBYmsA3/S5+JGv0ES++lRf6ORB1MeFCwqXY68mXk4Xh8/jh8wZTMwbTMgbDMwX+WSSVkGaHtiktU9ondXt0eAid/PhOfgMxA/MGnYIFViG4'
        b'2FKNUg3FuEMKzd355u4CrsewiWWD3BA3YzAqThg1ix81SxiVPhSVLrDL4EelX1Jrp7tlO2R7THqKBlg9vA/t/Qaj0vl2GSMK0pP1RyTlUaVo40pBfVdUKa+k4sI3dxFw'
        b'XVEb6+mTIYNb0KOZbpNskWxOa8ttyRVYeIzISqKI5HFEsnWyOCJUj6i1h7gJ6E6FFgXUGTI7MnvS+hf0LhBOi+RPixycHjUYHTs4LU4wOV5gkYB6m+Fs+q6VHVNj7kNW'
        b'7g/YlKX9EC+83bs7sCOwx68/rDdM6BHG9wgTTAof4mUNRkULo+L5UfGDCUnChFR+QqowIZOfkHkjKmvY2+ei+gV1UbdCHSpJ4J08Ii2hpz/ClkI5Vaa09XfrNKg+olCv'
        b'aDZss2ixGNYzfNl79QLaMzoXDkgO6UZfCkB9Ts8P9TmTA0rN6kNcn/bJ3Z4dnqhDWWmPzKdd7dRHKFd9jaqAx6U0ZWBay8KOhwoJM96zOWVIx254skt3TkcOX9epNqIl'
        b'8K6NQ23EsJlFU05jTrtKY25tIPa1hDt4SlNuYy6uu8C6QNwIeKwatZm1mAm4Dvi3fKN8c3RbQkvCkI1/j4KAG0B6TFCzY5tLiwv60kP3S/VK9RT2L+5dLHAJIsVFbaJv'
        b'MqQX0uzXLIP+9KgJXUP4riGDziGPKBk9fdQIwumJ/OmJw4amTVqNWs0ZfMNJuCmMegz7rXqtsKcxNAO1q/NNpgyZ+PQEDJmEDWSgvuBuhPuCUZNMo8ywiWmTX6MfM+cM'
        b'Tg4Y5AUM8WIvTbruetl1iDd7cMZsgckc9IghecRUyLXnc+1Rx0BjK7EjcYC+KHFBYiBW6B/H948TeMULnBNGlGSi0JQ0gdLjkkmowY9RjWFmJJV+7V5tXB9yjXJotExq'
        b'mdQuIbT34tt7Cay8BVwflJQb7ql6+vX+df6jNzq2uba4Cq38+Vb+lxxx1oShs/ihsxrkBNzZI2w5VFPalJHZAZ1m1UFdmyHdwHbDbosOix7Hfvded4Fj4LCuvlDXCTXh'
        b'kO48VM+cXs6A90W/C36XJgiD5/KD5wr8UgQu89BdeDWqj6yLfESh2mfGnqjthk2tDsxpLhkyiUZ1a95rPmCEJ+WLdhfsBG7RQyYLBuMThPFJ/PikweTZwuRMfnKmMHk+'
        b'P3m+IH4Bqb0RtoSD/gM5XK6AuoDRKTC6KakxSWjqzDd1FnAnD3ONmEXXCc3xaAZD7Uj3y/bKojliyCSzuRB7/xLaefPtvNFPtGZkXci6VIg9zAkjU/iRKYPz0gdT0wcj'
        b'MwQBmXfxIzmjj/jy7XzRTzSgpC9LD06PFk5P4k9PEk5P409PG0zPGszIGpyeLQjKIQmFNxe0LWpZ1F7YvaxjmXBKIH9K4CX2pQmDU8IEduG4uwQ0BqAGcW9xZ2ZTgYnn'
        b'sIVtA1obswfjEoRxc/lxc4VxWUNxWQKnbH5c1qVYNAUEdwT3pA04Dfj0ZH84KWgwLovvlI0mMVcjNImR1kP1ElIXIqqXV1Jx51u5C0w8RutRj9SjASM5OCN5YUg3g+nw'
        b'qE7SLqShHuJ+2V0YmsYPTRMEpAvcMnDLolYd0g1HbSrVIdVe0F3cUdzj0x/ZGylA5bIPxwM3qC5omGv7iOIYGrU7dE/umIyzEdYYNmzBa5NokRi2tmkLbQkdtnfoluiQ'
        b'aI/vkkcZsrFFfdXGXWjtz7f2H0gTWIcOWc8i4zKePx1NbcmC6bPQ9MqzREOZZ0lm3TyBxVQ0RkzN0BAxtR4yCUB5UuhQ6MkU2AeMTORMMsI5mPxAnTIzb0poTGhOEJg6'
        b'j2gpoMlvER1Mm2s/oYJpLZ1HKmi2euDNogyMH2RIUCraQmUuX5nboIKkjqDGoGG1ibsCqwORfIXKLVCzxr+Dq4PrcvcsFKjZin7VpjUk8/UdBGqOowEZDe/w9Z0EapNw'
        b'QEh1CBZ+JOokamPrk+uShXq2fD1bIh3p1svXyQs1eXxNXrNRswOSBNvVurU6tAY13R5Rclr6A849S8gX0ap0i2uIZEZeI6/Zry2sJUxoPZVvPbVnXk/BoLU338hnIJVv'
        b'FDxkFH8pa8goZTAxBdWpqRnuAaKqb45Bk+aowpU/39l/yGbmJbXrupd1hcEz+cEzBRaJwxZWQxbR7RLd8h3yzHyCfqIlO/5C/CV/OAvN96ZmI9LSuAPJoqqUVpioPsJR'
        b'NZ3wmFJVUX1oQano1cbcUDYc1tDetbR66fZ3BpWNnz3ylaDsM+lnj+ayqEk5NLEeHzLRWSxj+52VzmIFe0ZdSvZNOK+37wGwxtHccTJ/4X0M+3q7wK8rhR7DlIZnq6in'
        b'JfY0PeEh9Td5X8UsAo3FkLpvFVFMsRERETwJ9FGYgmF68q+gWgufUwR1FuMb5B/uH0PgrARJxrBa94wBVnHOC9fiWphYuO4/tYvC22mvtyNUTXFtvoEGSWG1sZU0qsZ1'
        b'1EMJloIyGpJG0fSwnvOwIZIfrB7KSppgt34kbOqwofGrYf4kzGAsLAOF2Qwb2jD3WY7d92pYCAozI2m4oTC7sTDnV8KSmGdRmC0K86JxoK7NsLrjsLrNw2zaWVOxLOhB'
        b'Hk0pqo+waAU9zDBVf4C/PdLHdNOEQatI/oykWzoGLTG9qheKHrNpxTD6bkDIsLf/E7a7QhA9IolDHkjg7w+X0pSa7i1l82E1v8eSLLUAuszvkQyJpyW9I6B59oXUy878'
        b'qFh+3Ex+4qzBkNmD/nNuaeu1OPUa96ZeMLmweNB1+rCeE3pU0RkN1wAalSg48ik7kKWgPUKRT2lyCX99Gi3hw1Yw+ZnCnwxwFas1OySCSoa4umMZAxyRHTWtYFEeiVKw'
        b'AnTDQ+P01TiivyNpmLyq+ifkVXaajOi7rNh3OfSdkyZPviug74qicCWx7yIK617ZMcKq2lsIq+w3ElYnjqOb6o0RVtVfI6xqrKPSNI9r/bsJq8e1j0mJ5UB/jK+qkCGZ'
        b'pvNPyKq6r5BVDW4rERxxdmF6arFf+rzs4ud2r2FVxa7+C0xVFwal58hj3ZbwjYz2v832cfQptMJzjA3+sGP/dbipC8OCcvxbRFTRQy5/n3o6mhxBTzlg6mmhC4aBsgmf'
        b'tNAVQ0rlov3DI2P9Ce3U5BXSaIyfX3R6wXjgnX2hOy7wX7nVYQwJOpqR55pvi3WMEzo+zzzZcXHgdij8Qxw2Olo5hVh5svAFvvS2NBwKA3Gp/7cRoZmvIkJZ1KvarpKM'
        b'QSrHHR4fdQmiAqrgEdoyDxwlOp4e9nATpxSz/rHXgspFcO80cDY72MiVXYTPxnmp+QQeut2wknZerHrIPmO+vb2aQ7xjyi6ljLth0tSNEMlz29t5NDmYNCwE5WNOG87A'
        b'XvJGOxfseh00yhBANV8ZXOMBo/i8HQNG01zEFf2HdbijQH1l7v8EO/rWRCdIizFHU1z+B8zRwlD2/7VMUeyyzFDqrzJF00j9YGgiNpP/dwJFR0ffnwBFR0fvn97h8peB'
        b'ouMnhLcBRd82r/wTwucb54g33/83gJ6vAlEY2/2UPGx2j7kmb6F0jD32Jr9Nr0FAx7WzCPyJ1yYG5onWJ8u3AzX+jLg5mpO/w9zMzvgvbvP/Hdzm6Ih7A20S//sr0Mvx'
        b'g/YvQi/fOID/i7z8tyAvJSNiS7wozKtwBZtgJegGJ98EVoTb4OYwxro86KVWFeiHGznwMNwEz2W723fQRREoJsE72/dccd7XuI6WctNyc116a7rV6kkx5pnmSeZF5qHm'
        b'y8y/zyktszb2lUs1D/RQTXaOUddhS1l8bfvZuo6Y2ngnnxnhm2rk92ZTi2Yr9Bpd5UkyL6R7dT1HuYbcldja1AW0kDe2s8H6rFfIhtKU4vxJ0WwHOpAoIoDDy0GbuE0t'
        b'pTgTHsHan3PzHmMLhCLQEc+8mWUtyZ1HO8TOIK+bpWR9xhkGy4AyxketpytP7n9wEoCFhzfC/F4XYcRJfgGM3PQ435VSUa9a2FDMV3Zuz+wpHoi/FDc82Xtg8iUXzPGL'
        b'o8mRd5XEDoVhDf1dy7Yte4WIp2n8n6PhvbVEmtLiKLxcl/8RCq8wmf2KlP5XEXiZPDqicDbj9+CN+LvXMj7KvvNBGRdj3xm9ZbV9jXcn9c8tE1OlxTLIGSddSo6XLpFs'
        b'KSuSLlkimJ0ChtllcIh0KT1OupQh0qW0mHQpIyZHSq+QEUmXr4SOSZfrkHS5/E3S5T8H2YlvrP+foNiNp7CLRDYR2i0XLXKYsfVfsN1/wXbc/4Lt/gu2+3OwnfVbBbsF'
        b'aN1gdlujDfE3OHf/ZMr4T3Lu/sN0tgkRxFaVqz1HDMS+lKfIgRUMit0Ny357wQ49BiETEwTLI22wNfg5LwK9CoGbsalPaALGlWMMlQTWIq6UBWfganiaGAjLx4ZzShVc'
        b'JPNfZ7Vz4SliEqsO2+FeUAX2ENibiPS2my5xQteQTHrCe0yX93VcusFcBpjOwpaq9bKwz0ujxBo9twIegKtfkqRgWZA1Y8UOy8KRXM4yD7YOlqTmmMt4L0otsUUP+GmA'
        b'c6GvCOtYgdUabgkn5jBUNEcaicC9qMgb04nJvHycPKzEsaG44qYn2MQnYLJXSHgYaIkNAq1B4bY2weEoEjsW6OQ4gsroGEof7FUEa+DhBeBULsNoO54pB3pgZZHjmPvk'
        b'Lu8SR3RFcyXYQaKXhxUvU8CsqnzHQgyoIsg4CWouqJQGNfAk3Fpih5vrvEx0zOidIjZZLH7CHXQyZSclT8qQBmjXEcJYAm/QNOQUKsLad1A9slXoqbYiG/kToBEVuAt2'
        b'L8oDtUXYqr6ftoKrXYhJtLmUJDVDEUn/XnMX+M20o7LZudESRS/QlffXPN+37XoFsFd+LzP6xxeWB8rKnv785YdfTHv3vM+MxjvRKtVPGrpVPCqU+Ls+jvoocVFne+37'
        b'6+w+XXg++JLpmTWsikvGTbH5c25VTdxYYyLZmyP8tvTEl0tu1+wOaM05QRXGXB/qPjrzpKz2B7yHHe4H7n/ZLulken1yzf0Tu6gj185E7lT1vaxW+0Xo7qcmhWGpwbXr'
        b'Z93b9U3wh18fP6I7qe6P0K+nT7h2NiwxduBO9eP7s550/7r58L0HucJr0p/OMyrRu5OZ1xT4U1PmyqarKw+/+yKsLuS64mafwcuKXUk/Tqz4LedTz2d7Zv54UNH0XuQJ'
        b'2xdPallyl5PXXI+b+fsHdjLxnlGfB65PceQpk00T8cjLQJ9MAxnsE7GWQBvDJkaR/Sg4i0bXS+4TYT6BLlgDd7paM86Am+lFcD0kVHiChF+5iGyscsAhFFw5th3DQCZb'
        b'sBMeXqFGos4GLYvwzgs0TB1PZZJBj21nbL3qijH5baxHcPJY2nFwD+ycQFK29M0LwZBAsqdDOzp43IQpVQPs1hN3fJzImoH6yAk0ZHcRFeLJpZbi9opUIpM4Y63oBPtI'
        b'/jigEZxm8h9qC/qwcQRKRxGeZYflwX7G1G1LAdwJK21CsEU8tiiYRoNjTuAEoyS8D+6QtQQnQh1D8IzRRsFuA9hNLnliaAI+c18YPWZDtiKOqfCNYPVcKzTGj8J+ZiJB'
        b'BVA1Z6NS18Iasks2glXLxOj/tsX2oFGH2DfqFlChYeI4pjTUTuJEpgC4maf4b3rljd/Zc8eBkMSQKQav7rDeREAqZOj1D/3c/y4BCRN5DHatrF55Q8OCbIB9Bdp+g2p+'
        b'd1X1CYmIUagbSB9yCiWXfQTavoNqvg/kKR0jjDGqksZAIHxlqkB72qDatGFV7V3u29wbpmBl23aTbusOa6GjD9/RZ8jYh6gxj96noS/UMOdrmN/Q4JHwqMHYJGHsXD76'
        b'v/lcgXbKoFoKiavafVDVUrRFbyhuWtK4pN1/yNz1Y33LQSv/S9LX5S/L861iBfpxg5pxw3om9Um7k5pj22a2zOwxHbLxJLcFXNLA6iR8qziBfvygZvxdHSOhjjVfx3pI'
        b'Z0q7+pCOd8/kKpm7Osa7pzYUVMl8qaFbO6c5ja/hOxB4KX4wLnlw9rxhv8jBqJmDSakjbFozHTOAVNLFXfYq/hWqzp8rkZCuMB6g8ze6gj8+LHBHt79YRT0NdKPpYPoJ'
        b'hT//pbOC/w1UDtpPP5/1p6icN22f/02cHG4EoVxmR1v9CSYnuPQ1UA5DyQGVJSXYEs4BtGi+5EKCdmqe71S2MyjnoNnnOBuuUwKbyEvKfLALbGJYOTSoYzkhYcgcdhKR'
        b'LT/QnoHg0Ppo6tpBgapZ5mRRZukyrJsHujnWRkYKFAM26Zyd7ASrnOzhySljqJvGiczavzZnLtwOq9xFqJt98CgJl58CThUV0NjAB9TlU6B8eiFDPDnsGWLFswwH+1VE'
        b'mJuQAIbxqwV3iCA3lJS6KahkycMGkTegDeAkOEQoNxh4WwZrKLAV7ltAgCJwDVgND8TAGqcQJbBqjHJTDatJeiaLswmvt2Ypw6SBe2EbESxBDegDa8XJM/CEiQg9k2BL'
        b'KuO0zVZCnrkbvFyxdVYOg45ZI2tEyDOrFLKMLs1UZQJ1jRnyzN3S1JChURzNZh+GPMNNXLYgQGsRE2hrxpBn5rrOTe6zn0sR8FESW5ZwZxRBzyh6Zgw8swHUkUZIRKvk'
        b'OQ48XaCARNMuBi9jDdeRSO8bE/6x8qoZRWHxijQlosFYgh1gN2OKycLQmgqaC9uXM6CY06AObOKUwtNKsCGawcFk+JIaCwKdEhgHg2oxGa7HPJgWPQaNXAm25IpwMDTc'
        b'DvbDTdgsdybDkAG9cRxwAJ6hCA2GAzpJrn1QQx0co8HIhEQoshLhbhciHk4DvbBqlAWDOTALsdHhTrQt+mPHz6yiw6i1nx39/tyMF5Uf+6ldT5tydtmvP59etOzHH2dG'
        b'DA7FR02vOLXml/UxUdN3qKs9Vs6N3fs5b1lO5D6LnCh1paXz4vysLS0+PKUWNV252gj9O8CtuNv/+fsLtl37arlZRM78FcGP6p5O+8np00+vfl8zRU+o9YH8MuPPvsk8'
        b'9XDx469czpfxNd5tN5+1cerQF7U/vTd7dczAsR2LZU1vvjvXu7bv2MDZvYvPntfY0RwhWGF64crjT02P5Z/Wfhq2wMNUyn1W4JINzQrKp7SX/Xrnnd3HDlh6l3zl89Vl'
        b'9adGJ9nFaT8rX6x1blZcFvpBwPKZ/EXhH6YJf9ALa9m2e+nuA1KmnXsvdxw/1nl0/vudR6/o3+ideGCEar08rcx0Qv2PfTfaDl/RWOL6M3yme7j6M7mL9Ymqxz47uz+/'
        b'LGPGZCuf0xyvk1KnQk0P83L72cNTWkos93zXvj1J5YzOAQ32e/FXaz7ve/fmnsQvorew3nufSg2fnfdkc+LnIVM/fZLvbnk2qHvoDiuRjoz/vnlv/g9rd7d93ty3O3WF'
        b'zkngPP37kunf/8z9YMLFeaVrL27WTVLVmdfe/NH9jAbzBbfmry//Sf3dKcOHb+V9lf7E+vwXi55vP30loSBpS4X78ThKPdphX5RDxicLry2lOkt//bYgv8lZ55v+crep'
        b'vifsTw/N0k0q3DJZ8YySq/QnX7kmpuoc+iov77D2nmVfxC1anlT3zpr3LG4bB+ZF70q/+9PlZYZLDQIVbv90T3NP5BcT53k/vc6uenZBd2ewgv6GRCV60lXqyXeLt3rV'
        b'BzbKvf/8WdJvddOOmf5oYae17BeHLQp5woOlG+N7c1ql7Q+rfdxwa7+LzgKryneLa3d94fDF9c6f69qORtL9s4/+pvVR1jop5VM352dtzXTdOfTUI21l9cF32rYEdnTU'
        b'7N7zYu2Ro1E3v7YxaPopvjb12E6PefH3ruvd9k/N0U76xJe/tnRw5rfPH783Oer0cFS47+Snjn4blZdLNtj05t2MnBbYeF0q8ODHuTtblT873s8zV7plfnXJ8K0PIsx+'
        b'Xqpg3/2lw5YrU47bXFj67PLNGyHP1Oc++vIj5eXSAVMVD5zntD913Xn0V+kX5b/6rrqVkW9AnzX5yKDG8YnNM4fuSEfh9j75zLW1G1ugDXVznva3pio/1Zuf3BkznXOb'
        b'3XpQXrE5K4I3ZWFgZ+bJW9UVXfvW6n0bc2nDMvWWa5dHFPQz997T+UXu62dPrF2uT/lF4+rIjzMrvnwmddMJfft1671nUp++ML/+Qv4XjUsjCrdtHv22UutZfdGmxPlb'
        b'71+za3D7dYlMz+qjdo1rHmq/mBhLPVl5lX1zZ9vqhXs+1xM8PL/6YYTv46SyFZnHhj9978apz/S++y3tE/3iU1d+Wh1nsPfqCirx9tUT2x/8IfOD+8xlt6e+d9Pzq8SL'
        b'P7339UrvWyPPl6VnHjz/R/KtqLhnTs2VgT/0U6WRf1yJuvLbii+yjl5cee/wjt6Fl+9c016oGVqn4/tO24wPZvxO/1z//lnLYrMjqkGeJ19s3zVVa0uTALTL+S/6eqAt'
        b'6/GD3z63W3ev4ZudT/u+OdR+LuhOQ6RK0Xvbf5uje9Ai49c+1XTN7EUdQa4jnTv2ef5wVetF5hN5lS1DM+PqrurGVa9kf8Jf5vmjh89P0zbGzIkJ/IP+BUokcgZ4+cRA'
        b'Haxasfx10grat4D2xRi0shcykAt4CKwGx8cBbd3hGlYpXLOC4VQogPOvkl/BFnBcYjY4DxjDXnXYWiIGW4EdUQxtBTbDg8Sq1gi0zxMhUl7yUdA25ZCEAlgD+pkNXAPc'
        b'M2kUkoIRKXAr6GTZqMC9zEZtHTxNiXFSktJFnBTYUvTYAt9w9h05ESiFF2JbEGwJOwzBmjFUijtYJwW6tEATsdl0hxtgxyguhZKag/atu1iWXJRdImA0TE4ehaJgJMpC'
        b'H5bpZFhF9nF6cG/CGBNFBhwzhNtYS+CpMBKtA6grFEOiSMOTKbCXFbnUkrFG3Yd2qx3iTBQ7egyJch5uITs2li2qiErbkPBpcqM8FLCb2UEezAWVL4EoMnJOiayEeFBD'
        b'4vaGaAdaZBmM6b27X+GhwG2oiskByJ58sEaEQ8EoFNALNrLYKvAA6QjF/svEaSizQDNDQ4mADO0DlM+FB8RwKDNDRTSUDXA/aUG56fC8GA/FQE3EQ8l0YWgotqDpJc1E'
        b'RlEetLCSguExYgtrgbbcGzHLBC3hKGEKNM8KJd0vSCsVdgVjignYiTbQ40gmM/VJxGGgCWwlamlSsHZ0j2wnYkOA1twlnAgbeR4qMaaRgD4anpgKGkitSaAna8YBDUAt'
        b'qGOIBuAorHtshGutCp4F7RiUsq5olJXykpMCykEjSYgTlDJGSgEbYxlUihRc/9gU56IZbgJrCSsFS9iwnAfLMRdFXwJVVZUE6ICNsIMZjlsXwiNjZBSwI0GERvEHJ0kr'
        b'oBhzXqJRQAM8L4KjLIYtDBtlFezxxibiQfDUqJ28ImAYzeCQ3lIGjkJzwCpQTyGZ8/gcJt1KcAL2ip2EgKM+BJCiXUr6ZeISTUxHQUlunyWio9goM0wBH1Q7YmgUcMQM'
        b'o1HAWtjM9Jsq2DrtJRsFnDVn0CiwFhwmuVIG1dGjaBRZB2XQg9Eo/qTHLoFNCi/JKDLZ8CCoZ2WDY/OZKWNTsftLMoq/kwiMYiCiC+kj0byOYaNgMgo4AxpoWO9myRBF'
        b'amFP8hgcBYNR5KbT8JTTUmak9HDAXgaFDc+li9Ao8ASoYOg17UhCr0VDARxdCfrG8Cg7QSXz8MZY0D1GSDGZxwBS1oM2op6Au+ACcUAK3OhGCCloZm5hnm/zxKQDhmaQ'
        b'AVYxMAPQ70VKFYjGWychjaBcgnqwA2NS6kXQj2X2SAzuKi6EJ5dbiiApM2AFA6ECx7ApPD74jlYZZaTkgTIRYmQF2h+JRHMHWEVzVdgi4rZ24UtGimUqc+Ynu5hcnANb'
        b'X/IaQL0swTXA+nfIAROog1Xg6CgiZRwfBfW6PWy4K2wxoXFwYJ8jJqSgjrtmjJIyhkhxhGdJWkbFYM8YIYWSjA8Np2GFIjxCTvd8wOp8BpDCmh0TT9stheuY3Nf7+IwC'
        b'UigJFQU0GGajXJ0iF3UNUBsSPAqmn9SBc8ThAdjFtEEZ3BSMNgOw3CIXnB9lpHiBWnLVyMt0DJEiDbajtutkuaLVro+svCiFGjyZ8dCEv5Unh0YUPqk+hbKtCdslrMAq'
        b'WMOM1E3wMKwW240kzmAlSk9kRmo7rAAdo+eVoDeDdlCBp8mkBY+hLrSPMxotQQZ1w11yYBsLHIfbTZi46+E5uIojwjxIqaNpl2U0NYWpld1ZKWKElk0hmNAC+kpI7HEe'
        b'sLKIWUBlMZ+FLGR67mhFKZcA1cFKpPxJWaWjeBaMZoFrsjCdpRluY0gT+9HW7KQ4nQUcoBk4y3LUGUnxToHd0iI2CyueDfppG3A2nowPP/0cQmYZz2UJsmKD+hwe6ay6'
        b'oAKeCbUJCVfSEZFZYjgk4STUxXeLoVTgaXkRSQVV9FoyWcmVwG1iLBUZWCsPujBMpUqFTNSesENtjKXyKkllAjwsBQ6ESZBJIDNZAdfTPFDLVBWax+AatNge8yGdYBqo'
        b'R5XXhYvQtIQnCyt4wSKpQAuslgiELWi9J/Pu5iTUkPg+HimrNNwLtoH9LO8kVaYyN6M+uVmMmoJiPcBgU8AqRuowmAPrxE6+Z9ty8lhwD+jyEvUETXgcHzyHw/ZA0bmz'
        b'I5ppcOK2cINnEUo3MgEcRB1qqxWan5WXsN/xEhFb0IRRb26FOiES3cJxbdXBM2A1axnq4VsYEM9GsGlJEXbwUp4DtuHc4TLSlMpE9vJlqL/ao3vYYN/yPyfK7AFbCFHG'
        b'gCENKYJtYRxyoxnsHIdhATvjRXA0Z6sxOhNsAPsJnQlJph2MDLdTUhFfhrtB9ygjzBjJd9rM4G4DO0YxVP6gR4ShOjGDNB3q5wpvQMVkG4pgMcqwnGHFnAdNIUwmUQ3v'
        b'HQe9WQF6mQpah5aC12AxhmD7guWSsvGOzGDoXQpOc7DY0DIGi5luSJo2HI3jfjFUjAwSOStYUdKipj2xBDag5THEZ8YoKAa2ImnNgFl1dyviyXkcJwbuYLFh2SR4gnFR'
        b'uxkJAacwLIbWht0hGBbTrEoangV2+BZFwA470BUynhVzdhFJmg3KQDXssra1lY8bZcUYgGqGPLUdLYWrCCuGxQOtoJLWl0RLMlkUsCPhrqKwYHgINr5ExozxYrBjXjKj'
        b'R6aD3QwuhpLSN5ZlqUZnMjKmOlzzEhYjA085TsKwmFWA4QDBanCMPUaLkQZ9ARmsIC94jvT2eWi9PDNKi6EklyOpaxOmxZwCneR66GxzgooZx4nRcZGYMLWUWRNWwX3S'
        b'L0Exc5QIJwbs1yIDVR9UYUTZS07McnhMBIqBB+czMscucBgcH/UYDKpnM6gYDkVaQwfUmxJODNpP7AWnaA8k7OxjhmE7Fj3GgDAySFbrhTUssBrtPXjq/2EIDG7hV8+a'
        b'X7MGVX/1IF+M/aIvx7zKifX419gvOkOa7q9hXqokH0hRXMN/I7fFiq9pJdC0+TvcljcH/jVki9oexX8fskWUiMg6vCGqKbYxttnsYDIqMQ5DddBMEwNl8jrpmJJA10WE'
        b'gGgIaIpsjBToTvp71JSXJA7FOsWG0qaVjSuF5p58c88BOYF5qEAzDOfovwiU/98jUBRxTnF3VxdoWuA+oVCnIFZ8EdhDzII+ti25JVloM5VvM1VgMQ2HyrbIYqRBYEtg'
        b'e8CxSFQ9PMsRSUlTsxH2mJU8m6OlPRJFT8KQlEkEkrLgX4Wk5DXm/R1IyogkG7WazL/MEgmpC2koxG+GhebefHPvgcKLSy4sEQbO5AfOrA0R6CaKRjOOTKFRAdddUGMQ'
        b'ykpSS5LQxotv4yW08efb+AtMAvC10MbQdlY3p4MjtPfl2/sK7UP49iFC+xi+fcxg7GyB/RyBydzR+6QFJi4j0pK4StF4fKBM6Rn8FRaJnkF9Ul1S/Zy6OUN6U9p926Uf'
        b'UZKoyFH9M3tnimrqrpUN5mO0eR71RD3N3ObAwnbJIdOYHof+Kb1TBhwvul9wv+h5wVPgHjNkmjuYMEOYkMxPSB6cNUc4K4s/K0s4awF/1oIbCbnDXt4XpS5IDRRcLL5Q'
        b'fClcEJgo8EpCFY+zLDkNQ2j+Cy35L7TkfwotmUm7YWaJ2yiyZBGNkSUr2P+3IUv+v00qKWEzpJLol6SSD+x1ijxsvzbRKaZt/62kkrfIpmXSYpiScI9/AVPyBGNK8G6H'
        b'YErYGFPyAFuYqP0nGCNF+ITkTXgRpgZGcA28SkT4DBNaIt6AFrF+A1rE+g1okVfDMpgwm2E9/zGMSNC4+GzeFoaJIfaYGBJF8wgxJJ4hhrAVDEXEEPTtkRwhfTRPu2D8'
        b'Fl6IqRgvBH9/GDHGC3HBvBC3v48LwQlE03f9g4fdPZ+yPRWwkhT+xMlEo2Tw96c+rAUsTArBnwwpBL9CUENb1n0EFWJgDMutQ8JtC4LDYYU1TVmAfsncKeDEOG0dRdHf'
        b'keeYEjLxVUZIosQYYwPTMlQJR0NWxNdQHBeqNu6X3Mtf2ewM9nH2KLUjzZQYEWETImxSJF+mUKZYplw2oUwtQz5NQoy2Icmi0qXSJNdRaVLHpceYH9IkVAaFyoqFypBQ'
        b'ORTKEQuVJaHyKFRBLFSOhCqiUCWxUA4JVUahKmKh8iR0AgpVFQtVIKFqKHSiWKgiCVVHoRpioUokVBOFaomFKpNQbRSqIxaqQkJ1UaieWOgEEqqPQg3EQlVJKBeFGoqF'
        b'qpVJZtBpRutkEieSb8bom3oZhWqcjepbqkymjIPqWwnVtwqpbxN0XWMJSzaDZ3Zb3tc7PNZPpPn12WnWKwZY2AJC/A4GXjKmv1+8ELuSL2LucXa0Zv46Ecfr+NukcZGN'
        b'KpgV2XK9xUyLRJYyxDhaZI+DrhanFxK/8AtL0wvRr/GmQeI+4q256SmpWdzC9PzC9KL0PLEoxGyXsKncuBjeZhwwXs1t3I+IhdgmJDgDlY7o0C1KL0znFpXMy80mVg7Z'
        b'eWI258TsAl1OQf8VZxWmj088N704a2EaMcNFeV64oDSdKOSV4FViwRJsviFeQFuufzaxhLDw5okMABeMtw/BZhQiCyOmIexE7TBa49ZcCx/e6G0p3KJ0bOlSnP7PGgm3'
        b'oYUvDxuqp4hZE4nseBYWZmdm56UswBbTInwUqgJsDf5KQYuKUjKJrXw6pg4swEZ1TOm5aen5aFks4i5kMk5MgixE13xwD8tdWDTeMiR1YW4uNnQkfe8V86MIHus2e3Hu'
        b'gttSqSm5xc6TUtmvTHdEOfEd9FEjz1g57qLI4JBGExKLWDkyk5ISGjjKZXSGItHJZLOo8jGLxeUSRCeTLaaTKSGmfcleISHSyXwldBxBA8+4f0rQGDfk3m6u8jYLJlQP'
        b'jPHSjPAwkfUNHgQpJN6XLYzakliooQH8ZrM2i3Sm471tdP8TsgNpBDdsoJ+aguaHuShLcxkrIiaysUjEO2lK3psNANPSshmbM1G64zop7s4FJemigV5Ugkbg2ETzZov2'
        b'cZZ5i7Ky0RN4nKaUFC/MTSnOTiXdOje9MFNkofRPbOML0fjNX5iXhmuYGf3jRu4/15mVpl7VmdWPKMLvJn7uNuniP7XiHS3mXeadruTd7FxdRGUvnxwuczj1d2bRt6Iw'
        b'El/WA3TBatiN34sX82A5Dzun5sGdoBOQJ8BB2CwDDudqEifrsYwCayNscAqH68AxSYpaQa2Ah2OITmVrIaMJay+1x3KqchHF3Hwg2QoeBRtBF1oZ3Cl30Oa54JcXL17c'
        b'V5Sk0ENc+wA3F7alBMX4zzunAsqIG0u4w8l+KdjPoiRd6enwoBuPVUIO5/fHBBXhl6rlixg9mrAIW1lLC5pyhDvAMbBNysqDUa6kzcFWVS8OvsQKp6csButQDMS7w2bY'
        b'GSEehRz+oCmjqZZukkaBcCOjuLnXP4XDXAD9sJkNz9CgBfajOYLYOmUbwQawadq4nARbFkTwYIdVcKgtVuaJh7UyutgNJVHq1AmLh13MJWPQyKZknFl5NqCHxy7Bp/r+'
        b'YCPsBAdmh0bgN4LVTvbOLEp+OWu+DNhFclNqZAz3LXl5VYqSX8FaoDmL1JkmPKYLNi1+eZWm5FeyckG5UQkPXXaA20AHNjvBVklws10Qvi8q6KWWEk35KUlrpGkQFV9r'
        b'Q7CJIeVH2cDT5KWHKtgCDyeyQX2Bfwk264eV07LF9bEtiELVdBRjWGioDatgKtinC8+BiomwE3aGqoGKULDPjCOHClgZEh1DpWcoT4mE/aTDXAkc7QNaWlc8F1ElSaRP'
        b'wkafVxNQm4iSwMZhdiFxFrA8CG6KwfZYoXGwfaznEmXwyGDJCaZycD04LCkJe/1NQQuP8l+kBvfB7WADqm7cGGqwHp6AXUr5hTQV5c6CPbQZOAV7iHVYribs4MgUltLY'
        b'K2gFW4K2LIBVRMl3UYku7JIvQM/ANYYseJw2Sc8kisFwnR1oL8pn/LecA2vZ8vTcQGVGZ7jVcVpRAeyUpykteJ4FV9EmKfAc6kT4VctEWAZ6i+BpEuVZsJYF+mh12AM3'
        b'kEcDVLDbACa9zhkkPVDDI90F7INrjEG756tNLgM6Slxwhg7BahpfZJodloUvgMdsQiLjgsYeELUaWAW7KFi/gAOa4eqJJfjtcg7YA6vHPYyfpChjNMB2LZOAO2AfOM2o'
        b'kR8BG/xiRM2vATah6UiWhufghvDsOyFP2UXmaAFNYy+/lnAtT+ClfKfkY5e8j0/mrdgtoWjzeSS3Ua5RnfbRtVTUtYwq8Gqe7rdL/bSFT3hzyEn1iVMSzhkprje/xM73'
        b'7VNou/Bu2sUTpcm5lZbVuvMiM84/y/j6o5+fh35lVTQjefNHD28MpFzOPKt+PeiDTVvvgvKP1oJPz/5e2rT7iwTlvJtKD8y/OK0p+EUlxjrvRMqheUPOUYcCuRrSBy0+'
        b'O/XonZBvvlBazlU9cDF8ppFjTfhHlPEWP+kj9+4kK35nciE3uYiz4ZL/yV3+XDO/r5IMP694377++oRl58GwZbFj4YE1liYJeZNuHsuJ/MeOY+6ffCV9Tbe0RHBE99qJ'
        b'73nmSa6b9fVONY3YFN6UTb6558JzM+dHmYqCvN29xpFLOsMfeCy8vUrrSfzEwJDaU1v+cX/eD/5nh2fdyX046bvOkvd2n99QM7jKre2W/3f7aR+267JHG5w/WnolPqyl'
        b'Y9o3rTXXJzStmXjHxPHahNNJNzepP7vM17D+/Zujg0sX3HFf96N+ytmFu4QHoj/apPSDo8/houfPh/tC1/3YWKKYzLv49eK0zRvnBy3OX2Tqv3H5ffMf5EzjOj8M/tLq'
        b'hUTI3vXPfnlxxGbJRyfRzDTS9fGy4z/51956FlL4j02rQuyoXwuGdXJykqc5TH2wZPK5Uzt++LZVfoXzPxatFtjuet/MZ014hpD/u+x7N/cVs6T7k2tZV79cKnVwdczK'
        b'HKPLmes2f5O0VJEq/vj9gG9W2D6vjGm4Pt/q0Yr0AK8XK31fvH/UWrI6dW37uY4voz/Sipivn7OHKs7W8F9W8bxq5ZHT6zetvLgtMvV7y+au/c1f6j3s/7Q+InbVcMPD'
        b'OEHb2b2fLAs7Zv2p6pLuH3s2xXM3e986XiORuXXb++9W6/887RurubMD96nkDH7v/WJ/o1vGB9P1Fjn90RR1UfFhf7z0vLVus3eveHHYLd/8UjP7+8XufTBzoW7ei1VX'
        b'nvupf37Vencir/37wKzcw2cLH5VOfE/wC/po/C3N6FvVP1YMt2ya913BfHih6x1DxSnPpvmtNRN6b6cXx8U2OPmvlov44MwyHjwTLlx+6R+u2r9WrVzkdL2b+nxRuF3Z'
        b'J06tcINBX+mtwF+e71lJGXSrPga//x/ivgMuqitt/06hF0FQkN5hZpihjPQuvXcQkCICil0p9h4VRRSsg6IMojKIyiAqYMVzkoib4lzQncGYjenZTTbBRNckm/I/59wB'
        b'Mcl+32Z3v/+a/IZ7zz39fU9/3ufwIpgLeBpBC9hjUi4QJbMpNpCxEoXeBGqwMb4I1INu3AGijhHujoM72JQeuI66Bb8ABh11qqhgroEgPkkLBaxjhcAT4AJzoHsatqBO'
        b'chJodaofWwgGVjPn+uc9wSlQ78EQ5mmWLCxhO/h7MuiEg8VwN+oEdnmkYtO8jXHgOJufrfsUj39xuQt0QlAwDHRMEoFdqQSwCeo84tz5hIVHiyreoA3Og9PqK7ei4N4l'
        b'yysmAXAZ9K0vlJNsxIKr8/GZNGwQalKaRXAPxXb0Ymw6wRF71M+nCuPdeTx4BHTjcl9iw+uwA+5hTAw7S8HBX6F/T4FD3KJs2Mh4aYc7l79Ei4MtM+HVKVxtLXiGuRRq'
        b'H9gFzquP5UEDvE6O5tlxM+AAqcZCsDtl8rn8FniCBQ/VgnZS+2t97QXx4DyabABZPnc+C+6Y5k6AmeCsNoq3Hu7LBXteOra3gC3cFUAOuxg4QnsCvgGIAczBnYsocCEe'
        b'tJEYglbroopOSE4U4rP1FHVwJzQo74CHNIJARwHBRFUBWXwKOFYFG+KxUBINU4TwUiKbsonhgtN2UA2FuQHlaBy8Fofhqvt01F4MotlwAG4BJ0h6hWhe1xoPz6FEU4Tu'
        b'yZPStPPiwtPgXAoDbbkJumDjONLANkiDIkgDeGwOA/voj6rwzgH1qaKEZPf4ZBZluIDjz1tDqtqTC/rM4U1mmqFGVhj4cLTAsXRGFIdLkaAxGmdPIqzXojR1UBV2svVB'
        b'lyEBIRSXgd4qNO9DMztwgLOItR5KwHEmVXkwPMJgCzlUdCjBFoLzM8m3RLDXiwHLsSm4mc+A5dKTmJs2wRHYQKBe5G42DXgUnqZY8Co8pYZ/uuRN1RMlilDIXbUceJYF'
        b'WlFNdDNIul2+8MRvQwiPgBMceMTEhOR6WjboSaqcAPNhIN85P/JlkfuqSQBAeMiRVZQdxDTBV+COeRjqhWGDfi4ceIyFmq+QwEjCYZ0ZLs8+AZsCe3w4sJcFOmzhCQJN'
        b'QTUsGgfRznWlwPUY5rq4jQmZ4xh3jCe9Cru92SxwRsR0IWemwfMOK8Yhliw7T7iVARGdJleiIWEK+QmWsFttWT0VXODA+jUsppm26gcQu2qM/1oIj2Pg+VE2EtwucJGB'
        b'KMv13F1hw2/C/bkozh6GvhOtPKS2aKrM3GC4PZEDL7PABSstonTaDvCGVQ3zlUz5NCnDMk40PGT8lBjit8Gz04C8GNSvqoWXDFa8mENigi0PuDcuWYiCZEZrG4JtcCep'
        b'YnEAOFgl0EWzeB68XMGitDawZ4rAZgaX3TxrWpVgJVZwNF+8qkFplbO9A8EO0iWX8n1ReTH+uSFVgMHsGmhCdxbs9uAaz69iEJiGkXo4XhQcXALXUHBwlh0Cb6wnFaYF'
        b'GmFTNOrx1ZEgzdSiDFM44XCfFSP8/XGgE1yB56oSMMafBftYRjaov8HyBRJdcJUBRc2Er6B6ilnKIPGa4cAqAorSdUPT73OTUFEW8CIzxpzMhlfUKHZ4NhJ1WLMrmKHg'
        b'BGrTN7LxpXP4Bjh8/RuoCyaQqFJUXX0oowkYcLqH6RA84mADh3JcEQrPaPjBUxtJkSty2FUpPGzYsH2DGmZnZM1Jz3AiSacAObiCIeUUvJmVRIEBMGBLiroaSqCsioEs'
        b'oeHjBgdsZ62NtGOAcFdgnQWUgwZBgjBRyE9BfcmU+Zy5afAGY1LRjFY3uyfyBnoyEhkMGxq3UjQoXhHGfu6EbU+FFAEqXkYyUqsHmkYffVlFUn3RTDoIXNBMcVB3++BY'
        b'HDylppMtw/BScj/qLfW9ujlAvkgPf6wRxsObjDobw6sccB4VSE50aGEMaqFk5BHOZ2lS2vAaGzQJYCvRoRIP01+jueCZEu5U2LCUZ/n/FzX1j49rcKf80h7Eb53aEAq1'
        b'aZO3nV5mhGvRYCBVC2ehztFGMk/qc9+Ep7KwanVpdlHYh/RXDUaOWMQ1RT4edwruLx10HLGIaYwcnT5D4iipPrC0kaOydWjkHtRXWdu15jbnthY2F8rEI9YechZt7a20'
        b'9qet/ftNRqxD+ktp6wjkURdfWpPfnM+gmpBH4mZipjQR0iZChYmPyjcQoyqUvvG0b/wQb8Q3S+Gd1Rh131T02C5IZRegsot8osWdMbVRY0yXcnDtsGyzPGPdFN8YKTFV'
        b'Obg0JaKH6Y/MbCRV0sgHZm4qW0eM2FDazqRtZ8oz79sGqHjukqiWhEc2ztJ5KKc2HhLOI3s3mYmsYsTeR6I5am49NoVy8Hg6lbJ0VjgHjlgEKUyDVDOsWi2aLRo11SAt'
        b'peNM2nFmI/e+kZ3KWSCLaMvrmNM2R+nsSzv7YlcHlRNf5tUWr3QKpJ0ClU5htFPYsFP+oO+Q/e0AZWQ2HZmtjMynI/OxZ/tRO6Gsontp51KlKAJDs+xmEfo9a0eMhFBa'
        b'e9HWXsPW+fKc/oievP71QxV0WBbtk630yad98pkqdZRGNOe1FjUXMWe/SmsxbS1mah+F7I8Z9BqIv5UykKIMTqaDk5XBGXRwhjI4mw7OVgbn08FMLFYOUq/m+NaU5hSl'
        b'lQdt5aG0CqStApVWobRVqNIqkraKHLZaPlg7NPf2mjsbb29UxubTsfnK2HI6tlwZu4iOXaSMXU7HLkdx6byUI0/a2nNyjnBij+1dZay2GR02bTZKezFtL1ba+9P2+JOh'
        b'ysYW/dF7x9qxMVpladca2BzYGtIc0hiFj7N1mnUwSGzYPEjm1M3r5HW7d7or+UE0P2iQe0f3tu6wWQKhNpg9YpOnMM9T2bt0WJyykGiMWtpIalo3Nm8csRTJjUcsvR85'
        b'iBQeC0YcKhVWlWMalIP7mCY1bcaRxP2JbWJpTcfatrXtYbSp9+FEpA02TmNGlL0rFsqog4dcU76iR4c5xFZ6xtKesUrPJNozaahsxCET+ZlCxCnP6FyoFIXRojClKIYW'
        b'xShFibQocShrxC4Dx/PY0l5q3xzQGtIS0hiJT7Vrm2oZ3gelGZ824yvNPGgzD4U4ftgsflQolkdiMFVfUk/SoOMd19uuQy63PUaEGRLufXO+ytIG14/SUkhbCjFtg5/K'
        b'yk5pJRq2EskdaKuZD6xEuBVsOrppVBTUH3krZiDmVuJAIoPJGg4uUqRlMhgIZVoenZanTCui04oUJWUjonLUUFKZBmHFG5tK8UW4Hbp8ZOnYFiWbLmd3WnTbdNqMOPn/'
        b'0TLgfyiFPGzYbNaoCDW/vtyeXIwSGBTf8bvtN+R7O2xElIkLIfgHhfAYtvKQe9NWPg+sPHAhNhzdMOoe0O94y2XABcNIlIEJdGDCcOCcoXn3Ku5W3Ku8W3lv6d2liqLS'
        b'Efd5KPfJ6twHotwLPHDuXVXWWL10R01mqAnDlWYC2kwgS7hv5vfIxlXhljxik6IwTxk1s5e6yJzum3mo7F07rNus222bNUetXWWaclN5uVz/vnWIysFNai7RfMfWWcIZ'
        b'teGrexPUIbaubl6ttPWmbb3lgfdtQ991EAyZ3pvxxgxFVq4ya85w1hyFe+GIQ5HCqkjl4y/hEkinuCO0LXTY3PuJDmXngvJsajGJR8OYATEcwyT0Ldx/Hs7wvwwjeJh4'
        b'Qanxzw4e8dooKOZ++vtm6nnqLBaLZfucQj8Y+WD7O5APVXjDsVXTg+rWC+T8Szycr/xvPJwvF2CchPM8SngSCafX+IEoOVF0tyufL7Lj48MOkaePeJyr+NecnP9Sjhfg'
        b'HJ9i/94cy3GOz7DHc2yJc6w+h7OrLHspb/8yoWkn66F28TzmwPb35a4X565noj7tCcUe4ZWrsCMRYqLIfzuPWNg81kOD4omDy+LK35nRKzij3IlqdImwq1lauaKm/DeY'
        b'J//d3C5gcqtfPH6Q9bszO4AzaziRWT6u1apqVK3kkGzifOw/lWHSlnR+t2Zef7ktiTKXYc7vpRXLCCOo3dzSZTXVL1GI/4dy2kb93pzeejmnli849Qn59X9E4itlvztb'
        b'AGfr7ES2LF5ka1Z85H8oV+d/d65ee6myVnZT/05/Z8/6vckP4eQdWOOV4pb1G4Tp42y6/6mORZcQhBZjus7fl9k38HiIx7LNlCSrtfho8SQFIyygTGf4H+mkebiTJvms'
        b'Xvb7cvn2y530DDW37H8obxOdc+ncxRjXULxsefnS35dB+uXO2R9nEMfCHMMvnoz6+SVt8X+sbg0n8j9v8bKq8t9XgPu4AG9TLxUAR/NvFeC/eHHQRN1NQBk4KZV98jIu'
        b'2X6ATzyO/cF/Qz1zC5AJV7z8DIcKus/+yLOZx2K2vo7Cg6B+YguSBc5OH9+CPAEafuP2H0fM5mb6iznn4vKl6v0K7Aff/LM4hkWZWx1Z17ROYeTwO+/6+cdJKHEr9qGY'
        b'e34WxbD+hYt+/kuCe+WXgqN+JThuSlaleeBqLrlGcOz7c+T2pv1NYgPKpF1Xyja7kshU4a9lUsv6jXVA6bJli9VC0VULZSURyu+Uxv8Q+cPJ4ljx74sDw8Ww2n6zlhqH'
        b'iyGBcNVwMe06lpoWnwGMUXVT1GAxNhLVBAH+Bo7OS4KYDBxDQmFv5KhF9QvXf9zGMGZd/JKobJnLuSJh7waMUwCnpuuzKIJTgAfnEJyOozWXWl9mTDhn6elCiqAkwheA'
        b'zVWGKx3gLh3s/SRLBLfnE0jHqnVc6pIT4z1ucRRFmH5hW4oOOR1JhHt0beEuwvO7JxE9pGDq34y0DGEOmyoK1wJtcHcqYeyb5giOJCZgFALYO3H65b00RYPiz9MAXfAw'
        b'3F/DEHPIwMmq5SlVUfhIAkMv4CHYzXDp9qXbTrajz7aDEjY4FFNawxBDnKkgbLGay/EhE1fIAufBZtBJypc8jy3g8cFFcDZZTbkHexcxkQ6AAQuyFQ3OruGn4J35KfM5'
        b'5evisxhMxA5NwOz3CuO5lE4IkGqxwV4gB30EQ2IJ5RGJ8e7ZoCEexctlgda85SQ360ArD59h8oSalI4TOBjABqfBNXiT4FWyN1Ziuh2U9IVkNeEO2A0vk4B6sB/TugpT'
        b'yPaxZiG7xmYa6vCOECzHiox1iXBvPL4ZJQnWk8pG9XFiBSZQFYRowAYohQMvKa7euOJWY8XVfUlxX1bb8Tsc/rMq+6veRe9XKitMIXqZ56ix+j3KCCuauzJznHbxFrwC'
        b'B6qIKT7cIWSYZRayGErEk7AX7K8iBvBwG9jO2NvPdGLk1gdv6jInDLAlbUKs8EocAbEtCoQdzJGjcQ05cTy8icizGpwBjVVJHsV+qBlos6zBNtBEAniCC1CK6T6iCjDh'
        b'B8ujKpWoTyXssWQITjgUrLNnGE7Q0NXPZFEKOsAuhsNGg4K7QwiHjWsYCVoDJFZImuyECRYbTGFTCjsJMq8Gd3ga4JJXJvprT03TtgebbXkapHDR4MZcFDINnHgpaCDc'
        b'TpqQR0ICQyPDpWDXRkIjI4T7CNJICPY7jrPXGIHDmBeA0NeAk8UkqJ9GFMOKk1WBeXHYQAI2Q3kNPtuYDtvBWQFKT8TjJ4t4woTkRRwW5QC2awSsimfqfCe8DG8mJpUa'
        b'qWloCAkNas9bmZa2FxwqZqgLhKz58BVKU5ttBs7BeqLaYCc8A479BgWCBpUHBwgHAm8eMWwAR2yEhCsjiZwo4w4HtR7cWgrDXHI1FiVo1WAKCHgJXozCcIf/gQEiCp5N'
        b'AVu0YCPssibld0Z9Rqsa+gW2leDuB2zNIlUHu1YkTvQ+SL22EiYP1P+E+5Jsrdd3n+jfTMGRiQN+dQe3Ch6oIZxih8AFzImjPguHu+F+pqu6Cm6RrqoQ7kvDRCMcCnVX'
        b'bYRqxIZFGgPsghddCasGh0qLJKQaoBtsJhkPBgOLx3sNP3ADdxzTQj2Yej+O2lAf4fdCccr9SH8De+BRBtHWDW/Ai0iFWRTLH9Q54vO63Q4kvdnxsF6QLMT8SYdhPXcu'
        b'7jV3g2YSKRd2hSMli8OIguOrMYPbYfZ6cB7WMZjM5ixw8RcMFEutCAeFhg7cB06T+J1R4fsFbrZ247QwmBNGc3kNviMSXp47a7yrg63gxKTubqKvuwBP8tiknUWilPeC'
        b'enixdhHYz6VYUEYhxeuxISXUsoC3qmCPJq57KBNQoBGgnoOASqeCRh94AH1xp2xhlzt6JGNe7ly9ojTKDVOUJu1YymFYSxPy2CkHWPipxD01NJFx/Kycu5bNYTqtZ6tc'
        b'GMeP4vSdzCmkg2kl+tbTqxjHrJk64bspO7xjuri8Yt3L0wvOeKfIRz+JqA/Fa41CNDnawFrPWs2qYrOoMuow6wiLRe3R56JO8zwH9a0VeHVMZkvsh2yR50NWbRWeVNkx'
        b'a42HOsHzy5eWr16+MnRt8C93YqvLVxYXo6UH3imoChWRdwJWfuE2EbpcB82lcPv+DE/VFFEl9OxiRWbWYDrIG3KCeejtOzIx22o0lVUTgVXqajxWGIgRHweEonhCEpOQ'
        b'niZEs4EzOXG/HsD2gV62Lgsr6ln9EnCLIhMGeBV2TUE9OE+Ij4MnwCNWSHht2VxwzhM2VYYe/YJbVYtqzy1g9YPcglSTCNMTo0u/On3wT9LTB/9weav9q+bzkiIVMxfe'
        b'N59Xl+6wsOwVT5/gxSYeZZ80HHFpeD/6O87N7J/b51/pdZZ3HON9W2p79Zr4vefHv2oJEY/8FBdqf7Blf8r5+JTSIL1X4oZ5VQnrW0/cTHjY6f3wrMkHrzQ7C6fvb4u0'
        b'vClcrasDhGG5D7d6X+Ou+qup3eIwUKlTMNt9Pfe57h3Hjfr77Ofp/KzKfVjU8Wq4x/Y9c/2ddujXL5+/o+NH8dLyxcZT0wwqI67MCNNsidZ8+2Lcq9eb9Y7/+eNS07dK'
        b'B4/V+95/dmtt2OPATwZqn3UYFY2qlu06wZtxcTDih5Ztu20dHR1A1+trdU73pZaZzvYJOxlfS9nNc/B10quf6t9y+KNvfgpYtqSvclVK1HcOU60ffPHnDVv3f7kj2X2Y'
        b'xz/CL1jeXybJfUX5VqP7a7npPxmIb+aySs41vK7qvZ607WwHHRW1ad8z8NC6/M8bzeQr5hpc/XHhu7PbzJ69uc676oJrz4NLe/cULnFO0ecbfX9nmnbhSXae0uB9P+PX'
        b'hWVf+P7F7uMvrw217KnvzzRb4X41c4uP9657u/zf6Exa+/0PX2TtAxfeu/63dVq7DhnpbDR7sidXmHSo6HZh6/IHVxuMv4t+y+PqD9z3PD/kzMsQ+zbMyDy6YlPUPue/'
        b'9pz67i3j78rf8lj0E2fenZGjT4Yk6fSeO6/vmfHjJycc9syv4DdWNhiOrF76xamzx6+P3fvDRzdnvXm1zum9WTOLHeZ1v1n6xsG4gKqE9wp/VO06pPuw617KBfs/Xflx'
        b'3vKbYMD+Drt979ylb7VUK5d8/MlbiqE/Dw79uSt6x/HKP448r9D8at9YX53vsOvKOXv2Kbb9+CBnpOv8HxW5z9bPOq6UPvtTUn3h38+ZH7M59pWDJMDDo3nL4o7o19dV'
        b'fCNU1Ryf0XSb/8b++Ydmrbmkl3Tl8es/fvbpume1V1iXPzv5N07alJCDHQOLOq/FbCpLL/Ton73y56pzW/++7f2rK8H67mU7X3ulD/7dO6cn9Gns338SvbnEYKHxwY9v'
        b'RAi38q9oysq3l8affvftNfe2nGv5S3lO2I61Phve/fLZ6PsJHaBg47Tad69/fn3p59u/v/fl3t0/XDuU1/Rxq9FbdO2iOXB53+GAx7YWpd84KK9E/WnX7pahr/IaP939'
        b'5fbOlMp9NuGf3PpsFV9vax24dtvDJP3b+FSes2vPlxeTbzaFtXnM3PiD2RfePpde7ecFMLCaARHYitn4gAyNmrc24gHmOrwSTWAxZdNBjx5motJxAzJNtEJAE2Jj0MEB'
        b'LRWZDMZr/2q4S4+Puen2JOajxqxtyc6Z668mVFpZMUE7JwUnMJfPJdBK4C2FaBJ+cxwbVsgi2LDAqQzyRQYlq9T4PbsaAt8DZ6wI/sPIBZ4aR43lY6pwjBqD3UCuJm7M'
        b'g/3j07mAlerZ3IkghkTvMmiC+0lZViTBTnjSg6dJGSCfLmCrLoHVoCKch12/jR3bacCBR0CjJUGIrYFHVmKImKXzOHYMnMticnCzfN04eAycA60U15hVFA0PEbyNYOVK'
        b'PTc0drfCg1yKncUKBVe0ST2thUfggQmSxQvhmGNxC7hK8DZs1HXe1HPzDRonQ2SYEEMBc4eFM5pGHyW0gkh2neC6mldQDvYQ7J6HH7hQlZQDGl5wBxLiwDmgi5SkElzL'
        b'J/SY7tSscEoTnGOLhckkT3GouFvVrKVUJuEtZa+Jm06UwghuhmcniBDBKXgZkyGy4OU18DBTDbIC2M3QKIKz6zGTIgu2RoMmIsOpzqgG6gnfKBITuFnKDWCBnhzQS4Ka'
        b'gosW4/SN6bAVMziyK4HMg4lXSoHeKrg7Ph72Jc7xY1NaK9h8UL+cqM2smGlqYjywH7yCyfHY+SsTGXTk1fngShXcYwDlwhUMUE03lw2uFvuSspaC07F6oHM5BlrpmqPs'
        b'HmXB7rJ4UkNF8FYKRmCVggMMCAu2w6vkSyw8UaSXkIzJ7XdmcMBVFmjSFzP41v2gF27GCxQdUaJIF0/czDPhYXCZ6wfrpxJ86Cx4vopBXL6gzDNFM9vNwRykCq2xDG1f'
        b'g1fGbxDboao7zwGtuiIG1oYWAhNkcKBXQPjg2BEsXTUrJZCuHAfKwr0CSmMDCx6yBQzjF9wOtsK6CXrZpXZE3xl6Wdhhy7SbY0sJGxhyaR8n52OY+eCWQHL1pTYnSq/G'
        b'QAfjHm059qwIlyRS6Z4oGKY8xKBW1PT6KI1oFmwAB0E/wyR2hVeJGcwoKgVeZRjMfFcxkLg9AWAcEucaiJRpHrjJwD7L4VE1P2HuSkpzOtsB7EElIeVsBY3LJ1jPAoww'
        b'7xk7HTRHkICJ5uCcHmEGWw3bGNazMHCI2ac8DLoMfkV6Zl3LgXVgSzqT0xvgOOhHokaLgzpMUMayCZvDwIlb0SReLcZJtGTgqA5mJkPTHqbhZxTAiwwz2VxvStOGbQJf'
        b'YThDQW9qCDZaQrqXAq/XINElsu3BKdBA1NIV7E0jfGlsqhjuYgjT2HAXaQmJuS9A5GjldQsDydnCFIYA0ADNnjthvbshuJGCumy4z51F6aH2Cy+guHcTqYI+1Pz6MNFx'
        b'exFaYPFgHblD5wIbtrvYk1JXo8XJQbzYhPJUzO7WxkrTsmX4B09aiQSpK8F2dwJIx+hyPWxN0ycUMCHhcQM9PprR94PjHGzuNRONIaTj8EQL/bPjQGM/+xdQ4y64hUFE'
        b'N+SCyxhaD+pmTqDrx6H1a4p59v99+N0/A62wp35NePYrqB4zzdd9MXlfy/un5/lk97UQLR6+JbP6p1FxLMrdR6qlcnbHWLT2Iilb5egq8z4ZqBKKpTEqd++26MfqJ2m0'
        b'iu/FwKakWo8dnaULT4bKc/uKLhapBN5y3/6YnjBaEKkUxNCCGKUgkRYkKgVptCBtWLBekVWgmFOqKF9Ez1lEZy1WZi2js5Yps6rprGpl1io6a5Uyaz2dtV4apXIVyKq7'
        b'13SuGXb1V/mH9NfKNWSaKnex0j2Ydg/uzxksHyii3ZOU7rm0e67SvYB2L1C6l9DuJV9TlLCArShbpCyrpsuqFTXrxihqEyuK/YSiapk/5axo9nP8J415S2Pecpi3HOat'
        b'gHkrYEvZUp82HZVwpjynv6KnmBZGK4VxtDBOKUymhclKYQYtzBgWblTkFCqKyhTzl9BFS+icpcqcFXTOCmVOLZ1Tq8xZQ+esUeZspHM2oth823RJbJ3F4zRJkbQwkol0'
        b'WDhvKFaRlX83VZlURCcVKZPm0Unz1IH4XnKXTg8lP4LmRyBJefoxdCgRtGcE8hHQZqDiuyN3d3F36rlUVIVu7piw6uwUeYbSNZR2DX3gGq5y8+g27DSUV/et6VnzwC1i'
        b'TIMSBj/RpLz8Ve4i2ZrOZBXPs9u601rJC6J5QSib3YWdhUphGC0MUwlE3f6d/uoYlG5BtFvQsFtE/8pfu4xpcHxcvqE47q7PNSk3YVtN+6qvtTjufmOalNhvTJ/yDnhq'
        b'aejlwGR6zIbyC+2fP6RJh6bQvqlK30zaN1Ppm0P75ih9C2jfAiRRvwi2orhCMX+pYsUqev4quni1sngdXbwOSaqEFYElhf+g+MJoO7HKNwQJapnSN472jVP6ppJIs2jf'
        b'LKVvLu2bq/SdQ/vOGfcbjK8jKr+dSgdnKYNn08GzlcEFdHCBMriEDsa6FBKNdUmxuEpRu45evI4uW68s20SXbXrOqJFam6RshaM/bRfwGNWebaetkhdK80KVvFk0b9Yw'
        b'L31w/p1FtxdJNUcdebKK7kVnF42KA/oJAG2wdqji9sYRcY4ir5AWF0pnSVe3JT12FWEWNilX5RfE0DIp/ZJov6RhvzJFWoYicx6dVoYTFNN2M5GEGOkohVG0MGpYmDHE'
        b'HvK9qzuuZl7dxVjNImhhxAsnQtCFWc3UTiLv7oWdC7uXdS4bFiUNTh2MvW2Jvvi16WHPE/IfFiYPeg9W3A5UhxpnbQumBcHIaWabNvae15nXXdRZpPbjIe5e27m2e1Pn'
        b'JuTg36b/2CcYA/j6inuKlT7xtE/8sE/ZUC5DjVdMJxcrk8voZFQ4aSht541V0abTRqqp8vRmVAV1QEzmmQYTSwtjlcIkWpgk1R11FKqcXKRr2pKVTv60k3+/hTIgng6I'
        b'HwlIvO+UpPLwYQiyYu57xEhjX/ZpdstqwEoZkEgHJI4EJD9wShnjUJ6x+CJr0czuOefmoO7uJf/TMIXaROwPnJKQf1Hg+54+8tL+GT1LRjyj1Lll8q/khdC8EFQKvxDc'
        b'6Po29mwc9iscmqpImkPHF04I0tFZ4eI74ujXPwleqUgrHA4uHDOiPLwUXhG0aJZSFEeL4oZMRkTJ0tj3+ULZ/C73fuNhfuB4u1553y3wCYcSiJgvI/xApE2yFW1rla4B'
        b'tGvAfdegQa0h1m1dZXgGHZ5xPzwLlXIWK541ZHzbYihXkZ1zN1/hFirTkrM6deWx/RE9CaMorlVdwf1ew4JglTiwL6gnqDdEFoUeleJoWhytFCcMixNUIRFytty3R/d9'
        b'V77Mr329fAXqtwcyB81wxNeKFWnpwyHpqMfqZ/XoKj1n0Z6z7ntGDZkp0jPuWijjC+j4gvvxhSov/37jHov+lcNeEYO5Q+m385XRuXR07v3ovNGwKJpsPI1ElYyElcjY'
        b'CgHqaoIfu4lwsRV+Bbh2X9CYqSv3KYfFK8aCFHh3izpFqG/ke3ULOgX4RckPofkhw/zcQbM7lrctlREZdESGMiKXjsgl/pT8QJofqOSH0fwwqdaoI79zviogfNBV4Z+A'
        b'mukG2snnfTc/hX8c7ZY6NAv9SDUee/pJNU4ZqFwEp/SeFHPQcPodIUbaFqdR4sEa0smwQH8eOsXooT/q+80e6lSvLiuvnlu5uOqhVnH16tK5VeX/DjhTfdPZ5FkCc1Sa'
        b'oIEWif/87ICDt/zwzaXfb6aeR8axWCw7fOeZ3e84Q/0Gb3oe0xRQXXq+HB6H7MROh9u1J10Fwc4D/Zy0dcymvmwW2JeotjqEl6Fs/NifsgDtXFDPzyabgmArOAn2ovnd'
        b'PjQnjReC3akJhvA8E6NtEBcedDJWbwmjNezBmMmJlcJmTj64zqT2CjgP28eTWzb9F4nBlkLCChAPJWjJgq2jzrvBprlxyaL45PTl2NYkPU7N1s2iSqZpO1nDQ8x5T8uU'
        b'BWoj7iUpE2bc1SU1LuijNzjJSoQNQrSCzyKRePmkx6kzGGgNGpw0qamgjtxACncCCT4ZgQ14pzQiAc1zc5l03SadK8wBR7WngAvgMFM1m43g9ZdqBg4ETaoZW9BQ44XV'
        b'A63LT1ehyMARcHByhNnqq05xyfBFIxWbtMFJCh4hulpZU1nProriUNQyG9GN3HcXjaSZ3vJLvnopOUxZsyi3L/DVBnsHB773jikcLRNbbnRZ+1blyVWKnWVJ1q5SB0lC'
        b'043Pwv/22TtjeT/M+6E4OL6q9+Cj/i7LL9tmfProva/Wtz5aL9ogW2KUYDhUcuLAR+9ZjN5bGvBKP1dbmfE0NS1VS/wo7i/7QEcX6+PRUyeOxc9ofyfxFdWMMxvOPcv9'
        b'mX1EZ0XgB9NrdZsepX2qglWx1U9/Dtrtn2jwfHdgdkL4h+W7ivNua1u8ceFxpuO2wJW59/s/dh2NMtm0DxzVX7guZnDZhT1Gl8VjQWbfBJl9/cfTVhbO+q21B860NP1R'
        b'8JVSb0Bvbsrb9lfsb7/t9nWeg+VQnv6PS34Msn39QVul1RIfQz+TVw8F/M0gz8BitcpqTb5uyPEDnrUHQ5YoZhrmxVaes8ovbLQTxX2giPjU7NCN+K86E8518LdMCSzO'
        b'+LDGwPMLb/P+zsMHHpb8rYuX0wXO3ttyuGtT3U/7o2rzHD6XrWn448I2H53eY8+ebXT1D7Nf9PNm91srdQtWPn3wM1id3PzEdHRPxdemViGF91899vQvfzqoHDtzI6/7'
        b'r2+t8+keeaP37vMzQU3D1soD3spXZyyba/te1t7bp366eUwj82n5/daAL74siN9TePubZMVrA8vrP5LcvLFDtn5TiOLY+ugP4NmoM99+qeNX37k2dLfjlDV/bwirTJ6a'
        b'/dZHfc7uu0dsk4VfNpgETPM7pIqQXAuQUL0dN8JH/b7fdXX7k+/D29YVSdPEPpIv0ysiDHXPbZToeE2XlNS0X/jze5afDuZ/F3T2RtWnEp484c6i+uzjgfdjWtJDz//k'
        b'IElJVKXESs2q36yf9YXLff+b75S0nk+8eKnpYE/llocdb4tb6q/dFbcHUZ8tNd59dtq7HX/jf6L4i0hX55ORv8QsKLva/fqppb0dbds/+2vbXrg4JClh1a4fEy+kz//b'
        b'ulHhXNeD37afOnw5OvZC0/nu1RetnmblZb26K3eVS22V8Js78b4dxtLEnr2v/nWux2v+R11XeL773P9j6/Wc0c/GWLPXZ3JlUzf48Uze0zK3/mSRyVdxS187P+vZ+dv5'
        b'aaPOhtbT6Sk6ltyC8KU6WzttRJ9/Wz7SVz21fpnv9NZn223Sdhd7wo6rP1/rOqD8aN0nzm+F/Gww/Q39b+1LeJ5PMYwC3JqN2Vn+kXEjuLRiwr6xAl4heyL+PHAa20vC'
        b'PaATb9kx5pSgF5wh+wHp4CzcSS5GOQpv4u1Yshe7ADBk5LDNagm+IqIb3iR3FU3Y82Vpk22G8rmz8K5pYbQbiyK7pvAIl+wj5S0wmGznyUuYbOmZDrczFqN1YP8sZs8K'
        b'7vMY37bCe1a52WSbJwi0gf3eoRMX8VYxuyO5mVGwA5yZZKV4FV4lFyPAA6awYXy1j8+5URJd8BJzPQQ8xAWXwPZcknYc3A4O6fEF+M4eUio9EzY+rd7mCC6RrRBTcBhe'
        b'wxbjK3gsSmMVC+z1gy2+S5ntmX1xUE7MGFEfCW9SYAA2G5Dajl+cWaW+12gV+q67il2AstqF6pfZlimxruLpeEVhM0di4gias0iMerAxFEigXE+ExMfOZQWBDnCM1MF6'
        b'H3iQ7Ez5V8JzeGfKkLlpqksUpDaDhQfg1hemsOBKlPoqX3hLVMWPj1mDO3SCg9gKpeAWswV1A+6KHt+Eq+IlTtqEMwLMDT1sbftJ1u4scEQHHnIER5hNvC2gG0VBDBd1'
        b'YPdk20Xu1JpMJv2T4HLC+E4Ti9LKSElk25sD5u4q15lw94trP9hw91wH0KC+9QrsXwvPVuErzuFpTWxhygGdLLAvaxr5yueAHXi/vAGeBrsxYIEDLuGLOtPGNeqsl54o'
        b'mapaif2AzmqUtLEpZ+FKuJUknDYP3sL7rkx9acPtAQbsMuMVzE5QO7gMLk++XQpfLbUB3gCnwU4oJfaj+fAK7PkHtAegnj2Z+cC4nMmSDLYYYVV9sQsMD8OT4Ko76GN2'
        b'iqVLeONbwWQjeBM4BbvBfnCOaEaMIbipl5CcwxdoUsyWLzy+mqmo6+B46aTrwdhQAlr5lSinuDQxScUvEUYwW1rgvAieg31gL2Nqfc4L35cEzqN6O4mbcCoLbp4N9qsv'
        b'+EFVfAZbvoL24IlbnedCxvjZFvSALYRzYQprEusCtwgeh3UkA9EGxuMtkWdJbhIj7cy8nOsAe0ELoyQ3DGAXNt1lph3atlx/dqkYaT5uzKHwEFKi+vEqTiXbe1uZ0tqa'
        b'c+FZeAQeZTaMT8I6fIk7Vlckd3yJjW4SG+6vAo1Rmxgb/aYVq1BUeKYFdjFoMjAQycyKPPM1TYAs6ymhw+qBx+b/dgfLmAbDLUh2FzRT/BYwLeEG3I/SVk+i4DnQjyZS'
        b'YJ8WZZjP8XJYS64OygF1PomTU0bJxgkxzAPWaYBLrsuZMmxfuAjHkwp3JYEOeEiE00TxcDj287lEIL7TUB/9giKDDRrhGUfkdO7/dI9S+/96j/IXNLDM8sOO/VvmYGT5'
        b'QTYim9Hy5DuyETm2OoZF2Ti0Fh4vbIwm9penLSQaKns3TNrfbiPRxDadYc1hSksP2tJD7jtsGYCWzs1RKmuHF+au8pxh6yCVo1Nz1EfYTjN2yPmex10PZUIRjf73KBpx'
        b'KFZYFT8W+zNc+0pxPC2OHxZXDuXcy0fr39kLRpIrJZoKWw/a3HNU4CV37uP18PpEPaJB5zu827yhGHpW5oggS5FbQAsKJJqS1bS5m4onYvbMlLxwmhc+zMsZjLmTcDth'
        b'qHYkKgf5qW02VInEmDl/WBTZXz0snI8yJbwrVCbMoRPmKEoq6IQK5G0tbc4fFeA9BssBy1s2AzbKgCQ6ABuHCjLHU3Jw7RC2CZUO3rSDt9LBj3bwG3bI6Pe5FTIQogxK'
        b'poOSlUEZdFCGRGuU5ytfNcgd4UUP8/KGpivSZtPxeeq8CDy7AzoDXuzgDAtSBjXu6NzWuWN421Cd0mM75w7DNkOGphwJgSdi9jOCaV7wMC9jUBObzA75joRnqCNF/gmt'
        b'uSdt5ynRGLV1kmnITftse2yH3cJVTnx8tYRs1YiTnyRaxfdAYVY1T0FS6AvtCVWK42hxnFKcQotTlOJ0WpyuFOfQ4pxxMTxGmoAUAInfFu+TDNv6DcQ8tnPByb3Ioopx'
        b'YNJnnJR2/rSd/y8+BNJ2gUq7MNouDH/Qb9PvmNI2hbnPY9gusV8DE8zfMhwwVPon0v6JYzoa/jaSGLxNYzXzueFy1gz3ZxT+HSvjUM78jpS2FKVTAO0UINEZdeHJnLuF'
        b'nUIlP5jmBw/zU25zBuOh4YhLqkTvsaWt0tJn2NJn1FUgi25fN+waLV80GNGzrDnuiSbl5i6LZ4izle6RtHuk0j2Wdo9VuifR7knD7qUKbFlbSKcVKtNK6bTSEdd5krj3'
        b'LR0fi2bKc/G2Xf7gjDs2t22UEdl0RLYyIp+OyJfESP2aU1VCsTyms2hYWNC/5tbGgY3KsBw6LEcZVkCHFSAfvs0po458WaB8De2YOBiDfiRRozx3WV6XDTZzH3VCleo5'
        b'xmE7h6j8g4cEKqHXEw308tgniPyVRI9pU0JfSfTx5FFrO+mMY0WyFcPWnh85uXVaqOx4KCA/kjXq5SMv77VUufuhMOj9cVAE8/ANxXaOYjVHo+I7CN53EitmRo1RLOdc'
        b'1t0oRXrOG4mq8MQnHPyuSs1mHlB6mpTQG6fHtOwRhziFVRy+fsWpdU3zGqWtmLYVyxMe2IYhN1d3pYsf7eI37BLe7yOJVdm6tG5o3qC09Rqx9VJ5iKUap/RVPuFSjft2'
        b'3o8Dwm/ZDtgqA5LpgOShVfc23N2g5tr3L8UefFSO/I6QthClow/t6NNvircAacdIFV/Uze/ky3P7CnsKlT6xNPqfHyeNVIkCZfO6F3cupkVR/Tn3RVEy9qiHt9z73KpH'
        b'3qGKsMwR7yyFe9aYLuXprfQIH/YIx1/FXav77c+uf+Q7SxFZMOI7R+E5RyX0UApDaWFo/wpaGDGYdaf4dvGwMEvlPvNxUPit0IFQZVAqHZT6x6D0zkRZlNxZ5TFTtmHQ'
        b'UJGRMxyeo4qNv7Pu9jpFZi4dO1uu0WfYY4g6Hs+oMQ0qOIOFKp0nGrOnPKJZT10ojyBFUPaIKEfhlvPYxrFF7+sqJBP3JxzKRvAdYUZ/Jc8gX4c1OtUP/TKbV0YMQj9J'
        b'41cw/X91QDH61ebVPzF+vDtuToy3qlZhpL8lNie2xObElr8H8/8MJ3Qe25qZr9yEnzfjny3453v083BaMaZNnVfN7JAVY47UyqXziaXzyq345xg2PnLkIK9aajvYh/qT'
        b'jU0f6k0y5lwpwr7rcLi/459d+MeQhWF7E3ZkD7XUploP9SfbRT00eMnKiBilEFsIUk28af//TinxhPY3WN/HpdbMRVJ7iU3aDwtrA8rqt5j0Xd/AaMyKcuYp9O0/MDBt'
        b'dm7jSCw7y3siB0wHam5n9i+660Nn5NKzCxTpc+iiUrqskl64RDFvqcJ/mUK4/L7BiufsYpZBwHMK/2Ke9pWsMeLyJIozzrsei3nX41l1UUjdLRxGjYQqUy/kZCGuS0Au'
        b'ZrajRnyVqR9yMQuoi0UuVk6jRh4q02DkYhVal4RcLB1HjUQq03DkYjmLVZeInNRxR+G4Y5i41U44blMxcTGxHDVyUZl6IhcT77rIF34isJ9IJpi53aiRQGUaipzMw1l1'
        b'eCCYYT9q5M7ENENcF/8ilx44l16Tc5mCc5nGItm0dh418mScrJFT8lNtloHjU02WgdVzzQKOgdNzCv+OkV+GLtYOT9jP57pU/WJyjJktZdxQjfJAcPQlkOoENy02gjuk'
        b'RUySMJs4pbaB0anQmjBP4v7HzJMqfsvm5WXzpPkpNSnoeXEq6BZ7zvT29fIRgz4gr65eWbuipgqtIeQYC46XehCtB6dYAZm2vq6hjoEe2IdWSnvQlP9QZhpsgkdyNCh4'
        b'AQ7o6QH5AqZ+DoKGZQTJWi+occTcXGgZW8+hTOBxDrw6M5GAiIEExXMOw3e9wEkLymtxfA1ZS2wGx4KJf/TDQav1luyVKGA3CgilcBsJilY6LYliVBBveDYV/RxbRkhb'
        b'YRtsWUkS9SBBQWfASnWas+F2EjIWLdn3iVF7F4MLMZTYGzaQDejlc1xQagIP6xoUkEWZOuPUTsFDJEx8Ijgs1qQotFrPQD+3AAPsB01gzxp1IXF6zpFTUWL1KKQQ9NXg'
        b'ljxT6CVGmuADBxLQTzvcy7CW1oEtpUwBcbDYajZlaoJCgbOLiMlELtwDpGI0PPiCLWg56LsKvsJwArdCuQeTGg5ntR6FY6FwQYtIYmhduCdXjLpRP9gbT/lNLyaw+alg'
        b'73J1Hk3BcS3QhioEDKBQNvAcU5VHXeFOMdJR/3nwHOWvCa4xNgmdcFslk0ktR8oUdBjgpOBpuJOEcoB9s0AveggAl6dSASKwmRHAQf/q8fpANQGa1jmoRQd2gl3EUgSt'
        b'ZbfNBL1IdoHwGuxAv6e8SLVUwMM5aomfh1dxn8xIDnQJSEB4GLSCrRgxPQsp5A78u5FA6nPB1mCSKArsSJmIpxMZwNYkUi1Ixw57YHx35MIgKnIdOETClIGGOAGjls1T'
        b'OaAtmBHB/PUkzOww2IYGcioKHoK7qaiZfozcWtcHMlWJC6jlJixVV6UDl6nJC/BoLTbiiwYHjKloO9DJ2D80wVv5pCZJsCJYP5WRm+50Uq454Bror0LijgFXwHkqBm4D'
        b'54kxgE54hLpY8JQ9U6NMGyL1eRMeJqYusDkorQpJPdYWHKJijWpJ+4O94EYk8Y5q8yK8CK7D42FY8h046G5bJr/7oLSsCkk+LiOAioN94AZpf2zYC4+pBUGCJuUHjyfa'
        b'Dq4zTXcXuLkYYvnHbwA7qXjtBCL+fHB50XiWkd7Ay7NL1UKEZ+F5otzgdAToxwR/VAJoKKISrGA/g1rvyAI7x2sXnAkmOs4UF0sTXIKXGLOLFngTboaYQzsRVbgE0xmC'
        b'o0xFn4JNFiTj2+BFVNhqeIsJ2+ROpBpcPgf2IqkmRcCDVJIV0mRSVZfnqGUzXuQ2eH28kfjAVqZtnQuAx2Evkm1yaSiV7JROigtuwUvTGC1iQm6FR4IZ2cL9Jkx2TyBd'
        b'7Ya9GhhstwN0Uymo9O0ktDEmzhxXJy1wMhXcmpDQ5WxGQmcdQD3sRdJN9QOnqdTShUxBW2BLslqjQsErAi17tXziPYglDNgGGiGqZCTaNLAfNFFpVfCM2roLSE2ZBOEe'
        b'zVkTbSyosmYK7iyMYrCZWXotuEKlb7Ig2XSeARoYTdoCWguwRuBcHsK5lMArTBO7PANu1kMizQBtyVSGhhnTj/ethc2karaAg2gwQSGDx7WhH5xh9KgHyOAZPSTMzBkh'
        b'VCYPdBNyc9TUm6aoZYIKcHmii1VrAzwIWpgKugKO8fWQTLPgHniSyvKPIMpkkou6kHFd2gb3kK6dBCdSBcfBJSZ5ORpRGvWQWLMDQSOVXeWlPgItRWHIELJtJWVqB/qx'
        b'SKNsGVU4Bvrc9TTwftbNTVTOdBYzFrTBM6CJySXXFhV5fMhCSVwhdWsVDXfpIUnmLq+gcheZMQldroQHmN4czbw84Q0/3AeBOrUN2xEnPSTC2fpu1Gw9cJNRGtDEU7cv'
        b'DupJr4NzFeMjHOhdw4xwhuAMqEcPeaB7NpUHd9kzSnEddWavgHoubqY7wXEq3wbcIh3QTLDfANSz8ZXM+9B4U4DG5ZtMj9sK6pzhAVRWEeiETZRomXpAXJsJpPAAKowH'
        b'3A1uUR4Vlkx1dsHj04nZnS7qn+1ZoJEUhK0LdsADKH5BgTclMJtLqrE0BGzLRBXvPAVIsPVYAIlh8aJQeEALWw22wX7KkwNPkYwUghOgnbE3AkeQbrqDrQYkFha4BQ5l'
        b'ogy6pIZQLu5wgKfLjEONsKlmfBBC1QSbQWcwM6pvhF2kKWyMzGfERVT0YNX4ILw/iYmhnx/2ok8A1x0gbp1E+zioyyLg5XnziZLAATHbjsUEtwFtzFjR4540PgyiQF6C'
        b'UqZf8EMDJdGX68vBtRcd5daSxRN97OkKkj9t0Ay2MzlwWAy3gOvqnmVNKJPAoU2l5CujC66cUnX45EKmbzqWB46oE8BJrAOyWeOK0jOfjIFevkj71d1PJGWCumJcOhNw'
        b'hsdikpAmwL2JcBemRz8RFYcvswXdbLAlDUg/JTPKxpXhPF1ipFWjxaauOxMQhftpE7WN1yGWPqVd7IvNuZJyIywZx+f+OpS80AUvWN3LrYwYRxEaGg56xOPgc2KncxnH'
        b'Wh0NihvKGFB3hFszjo99p1DVJf5IQ0oWt1pNYxwfGmlSp2agItmV6D9ZsJhxfGu6MbVZJwJN7UqSrlTkM45Umi710SoBNlDTT0wsZRwvz5xGcdPScEJz3lmzhHF04GlQ'
        b'n2VMxY5J1/1MGMeVa9kUd7k+KeYe7RqK2N8GsKZT5zbNxqlb3XLYRPHYWTHkg/5qLuXEJzZuSXr6RoxvMzctymmOJfa9+LVwA+rTo834390wksCOUC2qJNIaf3UviJpP'
        b'fSom/74JI9ruGr0Gj4jUMnA6i1rmiwYwY6YTk8E2AWo1q5PzqNU8f8YMFmtZ4gI0VL5QMnADtI6rmV0xSfDezOmUIqcIJ7jeKzyDKebn6dOo5Z65OONW093VZnzHtfKo'
        b'p3plLCS4tawcZ1TMlJRK7uyd7Co+yhLbOmX7wbtVltGmr18r2H/+rcNla2bmLxa8zWZNvdK4/Rz32AOjodLlcabTNxwa7OdrBWSvyOpObTl4lD89d7eesuXN4lcPCbJ/'
        b'0Fs/0p6eFbf57Cd+N64/f6bsXve07G9mGkserNLV7AxpmOn9kX7FXfeVZTYaF+sCVto4X9yjO7CZP6C979xt188XNCZfGnJ2PyBYcEBLnmDzalvIWzWGH2qvu/f+mq/d'
        b'iuyKX038yMvKtfh1wUddqxvWW7sO+S3fH7x95KMZ1+NPvBbwdbCo0WzFrvV6R+729cRc+PB4yI9ZHxZe3/n8CSv0Vc1QcKd/a+rYn1d80v1dx8OF7Zpd2/5WEpB24NYG'
        b'k1ur+C2pyW9Pefj3wKUhS6c8jKjwZs+oeDtp78+1PnRt8+jdunda+l4/418g+WDxt1cqvw+z4835XMxfMU/cf/PCxpnHqxbf8/zAyHHp028S7u4p+/7pjMs9u+598Kef'
        b'li8Tzd8e0Pv84FtXgw8suND19tT5K/cbfOLyY1x+xWtR+fs/730v7d6jBdMunJoW2nH1yx/iG4If6KVdMT8/+Km07IBK9bHq6BHzMNe85nrTv17/aN2A7E7/+/wr1e8N'
        b'XRfevW7alyp4sCiuUpV/EMzs7n/y5gxx/fs6vJJFyi+OxnyxOeDdLGXLfI/rLTkt2WnJ5W9kGCb8vHF6lkD8dYXpjOO738lbc6nXY87pAyZn4/L4/R/zc3j6D1ZVf/vN'
        b'tj/IzrQ/2uT27t63A9d+AWRbt5fVnqs90VVof+G4++JvYv76lxO07vHCGyY3vorqXdoamvrZG9LAj8ti/3DlD2vX/nz555+zZ796+Nkpfv0qgx9/fH/mjW/dz+9MLngj'
        b'HX6fYfBDvPV658sfdfX4dM4VP0xP3Rkrn/v5F5v+Wm2x+LXdPp3PlybABx1HVy8PyP2szfg9n1WfHP9ru1Xhhyo/US8vcEHSqE7vqdFTd5r2Xb3f8/7FZz/CDxLf/fjv'
        b'WQmP7q/7KWvKa5021f3TN4bVaq3/k+y8S+o3O3OUjzILR+ZuX5KYpTj6Qfehc2MHdG7MbP/rAu67oT/v/GL/t7e/PpjknPjhe4vvJeac+Wbak/1Prp15Y534pzm5739V'
        b'uXH0/eJTOrnWHmceOL5qfOVZ2sc3f7RsuWgccOwj3hQGUtAO92MzLLgnOSlVAw32feDCehY85QJOkVOuTLRKRNNXTC7sDLs4FDeOBXrRyLyTObi+BE6BY4lwL+bUFfLR'
        b'3Oo0i9KDxzhsFGsnsbzQBS1o2tWL/uurWoVS4OiyvNanM8eNp1G/LkDrxXMJsMcL9bJlLHDdCe4mH9ehyVcdppmPd49fN4dL6dWy4THYEMWctfaDujhsm5TEI1AnYpsE'
        b'B2AfOVUuRE+XUbwe/A3VLIpbw4K7YKfa6qwIHgBNAhFs0KDYoJeFuhC0uO1mTn5lKEO3xg2TSstQYbFdEjyVTDJkkAq2qCmP0Vxwqwalr8mGNzSKGEM3CZQaJRJbiIxa'
        b'lKYZC5yEF1wZGu8TYMtqNWgiERxhRQCpCylFGVrcXidh4tGCi9Lkw35/9gy4aw1zlrkbtsLWXzD0w0vwOmc+WoVc4Dn9980c/oUtRzyt/m3DiJftI9S2EVXz5i4trlwy'
        b'd3752knP5MzxYy5DPVOdzKKmzWLVRY+xjcwNVUaWkswxDn5yEMqqmKeZYYMm5Okx+aqBn8hX8kS+4qcxTcrYCn3XYp4dRciH+tknnIU8kRdtxpMO80w8qZ8ZT+RFl/Gk'
        b'xzwTT+pnxhN50Wc8GTDP2NMT9TPjibwYMp6mMM8kJvUz44m8GDGejJln4kn9zHgiL1MZTybMM/GkfmY8kRdTxtM05pl4Uj8znsjLdMaTGfNMPKmfGU/kxZx4ejKDefYU'
        b'D5qorO1kVS//+drWCF/Y+cRBTUGNL7a/b+Khmm55ZGHTQqnJgWWNHNXUaUcETQLJPJkzPqxpFIxM9amLVFnZ4ouAdyXXRTf6qqaZHyloKjhQWBfzvrFpY46krKlwxNix'
        b'btYjC49GTbx3bCuplc5tXi3TlK3s1KFtveRe8nn9Dj0VyhkhjREqC6vGyFFrB6nPiTkSlsrcklCy+srsZdGdrvKITgHt6PvA3G+MQ9nwPxL4S6ao7BwkGipHV4n2qL1L'
        b'W5VM3L5abt+2/o/2MyURKgdn6dw2F0nk+7YilUAkWyE37qzq9G/TfiwQSbVVtg7SBUc3yf37Vw+LY/GJK77/O/3UFOQVebFzlpa268jS2wxP6YyZUQ4+qOqceJ3GUn+J'
        b'tsrcDl8o3jJF5SiQRcoypCEoeVuHNrF0dXuI3Jt29Bmx9ZVw8dcolGaMPEruo3AMwJ5cVVZOTzUplLbbsSWdVXL/rg39VbTHLNomUsJhiuDTvvaP9t4o+67uKPnVcse2'
        b'jcOuIf2Ow65RgyaSaKn90ThUfgfxY1v71lXNq6Q1xzaitMyt1Vmyc+jQatOSabQboopxcJJoqZx5KM5kSZTKRShntS2SxKocHCWRKgcXlRtfqqFy4XdUtlXK9fozR1wi'
        b'pByVo4vM+KSfyomncuVLuSo3gay0Uxv748ki2uZLOaMufFlNT1X/zN41wx7hg1lDzoq09LuutwsVOXnD0XkqvofcvpMnjVQJxPhUvJ/bnz0o7p8yNHVEkMSYI1WdXKdy'
        b'E6rcveRRnUnSaPwwqzNBGv3EgEJf/1HcI9F5qBk5Cx8JREMaQ/OGVt7VHfHIvKs76CXXwNeh90dcNhzSpT0YREEeLchDQnZ0w3S+cud+7R6P+46zVAJPuYncQRbYU90f'
        b'27tBIYhSOkUpnKLGXClH16+1KGfvr8Mo94CvdSiL0DEtytJzbC1ax9l9hz55ZrHwDiD1hrF5kpsRc3Kn+5BTuWT+7zq0I0RdJS/3riuPYlD5pG712jhqHN9mXJXMYrGM'
        b'v6bQz+85hXsXBX/pokacMNnuJwRGWr+4qFGb3CHLkBhRFboTFzRq/scuaPzV+cOvr+izSvlt6rYSnGM2Q91Wx61g/x+Qty34Ze44v8qdRgpZ97xqz87wYxP6Ev1Lfkso'
        b'cpcc2OkKt+KVc64bprbZlZTuFhefGQfrQf9UuCdeg/Jbp+mGb0ap7NL6nF3lh4Ic/rLk2B9mYtq+7V7Hdm1pi7t6wKu+icU5t2N4j77zm549pmcepB1K3nNc/7Z+i/Bm'
        b'LpVqqC08fILHVl8jM1WcOH6Xgzk4ohnMNjOH/QTUBY7EQLmeE5D8oxtFpME89iSVxKP4+ECvN29B+bxFxZVLy8pXr7UtxreZFmMa2RfGDZM8kOEf3zWBh/8FaaipTGtc'
        b'sd9HfZn6wfhHFi4K13HqfjPzRu1JvHQaD1mVv9Vy8MY300CYtnESt43/LSPTdF+w1D2bn4YazJTf01Y2opBk/20paIVbEt3BdrAnBWMWuZSmBVs3MItsmMHGUnhCAPen'
        b'oIU2m2IbsyhwrJyoxIeL8fWOQwYcqsR9++L5FI/h1coGe2FdYlJKilAETwk1Ke1UdhU4D26QMEPJepQp5TlLy6gkaUyzkqFVTN5AZxo0nV++gkOxc1jU/dfIFsEqQy6l'
        b'Tc2u1Q0vSXo0I4lajC9HXxeC5I7+Pva00h8132e4karCG2ZfGodnZtd8UPNsFYfiaLCcs/cy+xwsHIVEQy+8RF9RGcHYt0gdf/iQTX28mdKj9ArjiL+WcC1Kn3JLM7Qr'
        b'0c/LN2L8La4L+1CD2r+MMqQMj+dV4c3LIc0/ffgxEr+LajdlfqiNmOdkSh5kZhvUGgzB5VloEi1kHbTIqCI0Wq82E0RkpxsGMpu4XOvhfJTyZ7IrUYUV4l7emyNT7rrf'
        b'jZ9WqUFpsdje7wyQdIuvnB2hqEQfikfxamyJk3nMNyNcqjyV4lP8mljilLv6q3oWNXsvVUgVrt5Bcncz4Yt6Gv39YO5uantFKnFLzpTU06gtf/jtNmrHg0CypRYEGkA7'
        b'rI8n5DlicD0HVRKoZydY61fG+Nlzq56j3ujRWHBNVnLqO+FGxwvfefK9o5OLzkHpWS1/u/uJU7JTb0h/4qQ8is2qcTI8w3c7GmKXzbdccTbrieOb+774wuWY+eKgr2+L'
        b'l713fY14dNOfW3+YYfPc5ptFuz7oG94s3c6zefutU6aKtUnpy052AdNyRYz0kb2TZMU33E1T3mJpXp4TG7rtcEVOzJLp+8sf7f3jzZihjqygn6c+sIzuevSRtr+E83q9'
        b'B3Vof/jmPywyLvna+/Nu6bZWuCTWXkPinvn20urPFRe9oKz954Oz9n3zoLps5W7PXivTtyKmLNj83Qd7ahoKK/rfPmd8bs29j532Wq28fslqxaqQ3aueXXLY/v7WW2d7'
        b'N25/c/bs1w2Pry9yPSML/f7s6/a5r72l07OtIqHnTmDywszTn52ddfa1ZQMe/R9yBxKP57/+7sa0WX/427Li416fn9rmI108WvJRwPSDgacDnhveyXnr3Ia372WPbazy'
        b'uxyd6b3za7ntOo+lpzfb1o4877rVf+/n+tAw1+4fq6vS6pcF7yx+98vH1Z8aViSO/ck1ZOkHe/YL131gNWeZyfPNWkvha28NRlt/8Of7q2Qau76WbXti1FHweuibQS03'
        b'gNWqkr1XRi7/dH2Z49E/vdM6/1Jv19trtGKWLT10gd9QsH1ZT82ZKUuiDmx7NXJonf2Fj53veLzPDb19vv/DyqIV2azU4q+2CfpN7j7/+cf0llc+e8QzIijjeJ05iTxw'
        b'NRZbG2lSmvPZfHhzPVmkeoPj8AheFGJKrhV+mLirkb0M3gKnmYVxHz5HwljrXfBEsjsazLxY4JwXvEm+biqOIGvUeIiPUnY7aKHQbeyNtlEEGBsOL4DDVdW1tQaGYO+U'
        b'KfCi/opSvOs+HZ7ggONgn58a5iyAN/CiHS3r0cJdvWoH7c7MWre10BHWJ4NzYZqYMuAVVmxGAbNAPkbBPkECaCwnC14WpZnBNq1OJCvr7CBcnnpwoZp8IYtnIAfHSXpC'
        b'eMkfLbvJLgEX7tagdPTY4EA6vEGW8/FgRzAKWraYJ8SIZc0StiM4W0ZS5GQKBaIE+ArhNmGYTUAdkDE7D68sMseR1sUXRiahkUwP9LDh8excUvn2s7IS45Nx/RbAdlTB'
        b'hexyEzETrCcN1KOaX53GDIB49INHwWVm+2AzPAHwJZ27YGNIahIPyS2IbQpPw/M8s/8C5LcK18E/APaqF9cvRre1k57J6HqLzQxqFWksrsEMtGydNqMuWjXFRDHFFt+b'
        b'sbZprdRpxMy1kYvf1jWtk/qNmAkauaNmdlLTA5saue8bz5A4STXuG7vIHFSm5kfim+Ilpa2VzZXHFsm85FlKnxjaJ6YxfsQ0tpGlMjFtzGic2+gjiR02cRw1tZWyD6ai'
        b'cRtfJ3JgdSP30QwrSbqUK61p0x+ZIWzUHJ1uL7XvcG1zlbnJY0YcgkamB6NF4nQzCUcS0awhmde4GL2aTJc47w+WRkjnyezbymWRclZntDRFXj7sFKSysG+MVFlYS3Vp'
        b'C36jlsp8RqtWs5ZUSzZ9xNyzUUNlYi7x2h8wauUqY3VrdWrJOfLFtOeswZgRt8QRq6TGaJWFLVotmlnipVw+beshd6JtfZu5j63s2yJlWu1JtJVnY/SoBVoFdlS0Vcgy'
        b'5c4jLv4jFgEokImZyhItiiVZEr/GKHwpTfWxABlHVt6pR1vObIzCM5i4pjhJljSqueC+KU9l5yStbtNrjGgsb6xojJ+Y4KgsbZuiHqOYsqViSTBza8qIpcewpY/cG8Vr'
        b'ZsesT+3syZqMI6vsnNI/fcQuHLlZ2km9jwaqnJw7YtpiZDPl00ac/PrtaacgSbTKwZVZn7m4koxnycUjLn54aeYkzZQZt2XLxNJguc+woz9epY2vy8Z00BoGKYizixRV'
        b'szQJxePE60huS5a79DuNOIX99ntSW5LcfMQpEL0ZGR/RatI6qPM8j0VNdX2Sz6KMTCf06GX1+oXqTTFVTLFDbpLsRswFrTIxq0t8Ph/HojB2+b7KACnybSrWL17MuSvW'
        b'iA/WYmaA+g+5y+dWL3jILZtbPfehzvzy6uLqyurFv89ul2AqJ9+dwswaL5EV1Yu2ZKqrXlHhu1LK8QTR8RlaUTn+nlliMopzHnvSEmFifVJGMesTQgmrgVZSVAVnggKW'
        b'+39HATuRgUkE02juiTeEc+H5iMRUIdiFGZvIkR1ahEwFfRy4lQf+H3NfAhbVdfZ/Z2HfYdi3YWcYdlABAUUQkVUFFHFjRxDZEURRXNkEBhCZEZEBFQZFATdwN+dka5qk'
        b'jJACqWkSm7Zp2rSazSRtvv7POXcGB8VE+9nn++vDMJx777lnfc+7/N737cxxcHJnEhWg7cRk5zuBXfvqetp62gbairT+kOt47itlT9WsT6JZVOxy9t9++xo9XaynRx5L'
        b'SLM0TAtP3xMyNvdPQsnwqYTTnG1dQ9KcZUhyJg38xjX9FGQC5eIrGAQ7+hwkLJG/UxRkg+t4lue+KlEuCfxYTX2XvQZNtOXLzDE+XP5/n2NWbI6bnjM9fTuKmudM34Kl'
        b'Zw1YJp7eCd6FVykq/E/sg6s5LzR9JXOnr+SZ6ZNFfX+Uj6ZPy1hQKkz4QNP22bm7+qJzd4vM3Zz3JCnO3XY8dyavZu6y8NyxZHPHoJGWWez/wuw9o+NQemb21GOJMBkK'
        b'mpKiXJGQaekjFzM3bSQi2FS4NdOC+h9VqvDTvX7MKUdS+N0qLGFShTNqKdEhmTI79XQOagubKtTbkbrlnaRoOgB5NKyBjfHYjEHBg4H6GHB0poTcfnerMsZ8LjWxS4m+'
        b'UxEpiws9Bm8FxbvpucNj/IiVLEp5PZMBT2bkvJn3PqvkBLrhV53BVEPnO95dPW0LZOqJTYPRml2uSxe8K8xdY7IutAx8nnxYf60wTytUfSLXURKZtXI4LyDULV0rtIVX'
        b'72IkPGviKDie3Gf2pusO16sjv/VMHPHyzChKa0kPLVezG//M9k2rePH6+2NVKgmHPnL/LnatYJPqRHXP3WNvHBjwbtCJH2zz7xo5XKT3h+SrwYK9pgdM/SaoC/02xi3J'
        b'PDpoHw/Uwza+m3MEEHrhhMzgONPNClyjXfluLfBBXLqeN+HT5Vz6TX/iW6YLLsPhKFhXAU67Yl49DkciPoK4ZSiEtBOiLU6MGeUKT/iQ8HtyA9dtIMuNfBw2mYJzkZiV'
        b'BtfAMViH+Ok9TFvQk0XzqaeWr5eZqpQoTUPQgi1V4BpFq3BOwx54FR7ewI8gRiX2Iga4YJxI5/ZsQ1ULtxOklSw8H7GBZfB5Ki9yKuItKbPh0BtcE1PJwoysLfjIrZzz'
        b'F9nefZTMiIOps0lHQEtAW2Bt2IyupTCje5tom8Rpwsp7QtenNuQzXSNBkdBhQpcr1pPq2tWGTBsYohv1DT4zthSmYmahhS1gCLymdTkdGi0aiIUKESVNWbhKLVwlqycs'
        b'PCZ1Pb9SoQw4D1UpLb3m6LroI7HTmrrNUXVRQlWxr0hnUtN52sBa4N2xqGVRR2BLoJg9buAqLr1n4FobRhgLBZqjUvxH3Df2z0b7IGMhYxBo0vM2Jj1zhmCDAuV5XPLS'
        b'lAcr3eZsezXZ76+xN0G7VgeVSSUzMqhkZgYjmcWk1lHDLPSjiX5UspiDzHMyrWctRbSwBAOONbFZqhmsg6pyWpPMZlKZShnsg1SG0qDyORmlS1YmpSqoVFWhVIWUqqFS'
        b'dYVSVVKqgUo1FUrVSKkWKtVWKFUnpTqoVFehVIOU6qFSfYVSTVJqgEo5CqVapNQQlRoplGqTUmNUaqJQqkNKTVGpmUKpLhoNrO81P6iarEfusMI0L1NPPianGU2MZD10'
        b'F9ZiqyGaboHu1N9pqbaVZ/2hSkxqPnb8+NFNXVH+il++KoS7nb7EJflf3Odc5zHIUTbnKFGT0/FC9NGuqhD9f3ayCEugNnuoKL+yQyWbx/zxwJwW4n8r83NKc1Lzcioz'
        b'S0gapjm9yskvKcWOLe7qzzwXUJhanLqdi1d9ABenxsHfuKUF3FS6ilVh4dysnLxM92eefGaFzz3YrGLLcNBt0LB2FSFoqyKQAH4atMS5rZXFQ8FRzV3dGdQKhsoiO3iL'
        b'JMDYCOs0NQqL4tEV+W0Jqju0ChNgbQwJd41odig4kM5V1YRXMskJZ862hw1uULQZaxNJ8HYL2EAAbKA5neANomFzVAwqxORcxNxl7EaQ7yx4CfbzI2Nwrm7inmGgA8ac'
        b'WLDTD+4jZ+E22ASqo7wjwXEwxKQYcIiCoyHwAA197DcC7egMibY3ZFDMNIYX6N5F3mkBrhaAixui5OncNQqYUAQPwj4aNXgMtgaSowVHf2yIRjeYgBpt2M1a5gIu0nHs'
        b'j8MGcCkKnI9ALcM1mMGLOnasJCCBh4gaORO2OchU/TFZifgIGmXusoaniQrTCtzwj1oZ44Jj9w+ZM4n+EgNzZZk+DMFF0KwJRFHRipkEAgEdst6XjW5siPbyI2F66SC9'
        b'Ng4EeOleqouTNKjAs3SWhuBgUl8svAUPYdf4PlBHAv+TPAzloI40xtV+AzqxDsp872fTKYBGK6LHPpighPXYaYylKa7RXg4UjRFt1QGH4rGHSBJlQ9k4gEu0lSUY3yuI'
        b'0lyakvfTBhOsUuei4iQ0Vofn5E7QA82y5AloekXkWTd1zBZRu5SpFM13OQtp1f56eBIKUMuCfUg+B5LMAe5DM4+7VWi+Rp7MATMJOckkl4OrDNcJT62EXXQ2B3umPJtD'
        b'WwBBJoPRooD5ci2AS84UybUAbmkQ6B2sBo2ueJUQYcyDiZ4EbdpQzNoEjqrmZOnw2CUn0DFw+ndXziTeyAeenCsGTrqtS/etEre7lP2tenLoL8ffSHt4V7C23cXf8rro'
        b'1hcrxj2+uK/zl7JhS2Pz/R9qXnv/0Xc8/8efGry966t9THv9lrrfuy99L3G57Tm95b/L+5qrrHnNWGNTdMbim1u2X7I7+/nRL7yqvsg5mtZ4O/XzCx9fzH3dwcfrXXFm'
        b'cRg8866oo09fEn+37vUFBt+l3/qNnvm1TdK3H3y3eGzkjZiAsaCGxd9/dKrj46ndUR0ne6ICr/9N86O7p369OCvS7e/j4q9yJnvyNr1hsW6L75+/N00cGt/yupdl5G+4'
        b'TRkbVYavr3p7rMjHN/F3AcI/FTfHftb1UWVubE7Px18HVEeO/Hb3+9GLei68BovzilX+OVgd4/q3Nanx/Sq34oVdqz7725tfDpz4ywd/+vvNGZv3EzdKxvLet9/xm9e3'
        b'tJ3fqHlx48wdA80P7Sx/8+3ZRztTvb+vur3QKcpv4PZr2Wm7HXPXpmU55K598P3939rsfSiq2O3474eiE9/88PuS3Jrg8ve1iy48WPZGaPd7ou+3VVY5XvjNYOHOFX2e'
        b'/97w8L23f31mT2XIr35U2flA1KP0Os+MqDpjwD43fgS4tfEJ17ZEFuQZnCiFEsQK9kdFu7jTXJ1GHhOe3gZFRIcaUhYEGxDXj1W/FlCCljhsYFaFwBOEHV1SBYc0SEb0'
        b'MjDsIzPZGYIatmowbCSaYcR4HkzQeMqsZ6ctN+xpVtGMZQ/sBN041D/JcKG8PglJF+XxdDiFNiWcWwScAQ0eMkKJaFYJEx7PALV0zN8+cDYjKs7Nn00Hl4Fn0MtpQuW7'
        b'Bz2FCSis3iSjoUbwJDuAUiYDo78CXgMNceAQPOMdyaRYeYy1laCD5mevwQt+6Np2tEmbohmI1nQzgADUg1t0TA0x7C1El+VEFB7fq72V5acaQoPb9m2CEpK5QIGM6vtn'
        b'LGKBnrXL6W41g+se+N2zVFQfHFDfxQKjcL8necW2bQtN0HGEs6ARSop6vRr1Oi+U1hnXrvdGhAtdpmkpk9JwYELxHnCZbt+xvaBNHuQXCRh1oBMH+U1wIQPDtQei2fRq'
        b'hOrBwRQdNVYpPF5GxIAkIK4iNxDSowxuwWuqTFPDUvK0ShI4iyfjCfnRt7GGZ1hwn00OaVs5GPVcqEKCqyAKhGF9DUw4Ck6DqzRw8CbsAbhjchJPwQPaoazwvbDpG5wA'
        b'RAWMFvJj3WC/53NytywtU9ELtSKvWroeTQoa6Nmjdwls185mBRh50Svg1mYbepbkREzfCZz0Y4GbPA16ptrAAdiKmhqxEn+QDaAPDi/SZoG+3DU87VeEXcNmP0WM2pxk'
        b'yboyrm82TzKRb5D8TNQXufG09kkcNmnAmza3FoTJdLiW3YtEi3BADInvhLknLqZLgkXBEvtJc4/7Vs7jvOAJqyXjJktmzJ0lnAlzd6w6tiZ5zsMnrFaMm6yYtrQRO4o2'
        b'ksTW1q6ShGHngc0T1oHob02MY3Pqd+5xliyesF2E85NPW3AxcEqc2BlHcrXP/RNnL88Y2jqwdXjnxGwu+hkbd0npUMVAxZj6hEfohE0YTtQ+byHO0l0hqpCoTlh74dd/'
        b'Ym2Hf02bWnabiEzEzhOmfIEySb7NFYdLjV0+dXLHyeLDRZsla4eXD2wat1iME9EvFMXiX/5SC7evVdjOZkL2Cc2H2hTPQ7JT6uw/Zit1DppyDpU6h94NfVtvwjlKqDVj'
        b'yxveMZYjXRQxabtSqDLN9xrmSfmBQpVJE+dp5wXDaeg5ocoJrWlX/zEbqSu5wJt28Rw2lbosHguRugSjqzrTnouE7G5NkeYHJm6/3DSFPwOkFu74tx+SN7/WUpG1WBfn'
        b'lI9uiZ7ieEs5OLKyh9QncpITNe2KZhpfmOTwPrFxIANnbt3tJ/ITR06YewhUZwzM8QhFSI1dP+V5Tls6iLOklm6SijGlgb3jFkumLezFa9Gb8O/1UgsPNEYu+I0YFcjz'
        b'Ql1yXjy2TOq8ZMp5udR5+d30t70mnGPoMaq4qyZdFDlpG4XHyGd4pZQf/Etj5D3sL3UJGkuVuiwlY+Ttj8ZIW6T9gYnHizRO8e9kqYUn/p2EhgsNk6zRZJhiW2KnOL5S'
        b'ju9w0liBdEHsJCcOR2fgDfDQUKGLOHc7Hqp2bQVJXJOOYXDlP4phINPhP9nOP7ebC+WafCyqb4rHovo31MvJ6yRJrEiZRw1o+P5nCc9JOl3GzyRpnm22PCnpe6jZClmP'
        b'bUnmcJm09iTr9atJbp5FJ1FV2VKSk53//CTiz7RxHLfxEWNOG+X5w3FVqaVlxa8ufy57S5p32gu3bQK37Ul6ZufwvNRsbk4WN6eUm1OCZNdl3stmx/PVZLb+mHqJ6f3t'
        b'3OZZkJyzxZkZOaUFxa8sM3zxn9gv0aQZ3KQniYatZE2is8C/mnGSLTS1LdsLMnKycl5iqd3HjXuSWNqJZNtOLSnl0jWl/1damVmRmV5W+hKt/HhuK+1nW0nX9OqamC3f'
        b'sSQQyYs38MHcHesi3xWlCtQFbQ+61lfYzIzMNLSwX7iZf5zbTGtCWEgVry57+Owsy7fdC7fu87mzbDNn776y9mXL2yfXOb9w+/46t30Oiko7PNFyjd3cNiq+fm4OZAz6'
        b'ZdayZDBaiknVzeomqxhEV0kp6CoZClpJag9Dpqt8qvRlYLTKzwH5/tfzM6O2/Zj0jFYT/yPbpnxrJhrNYjSkaMcobJ7iTDrjfSkXLYf8gtJnFaPPKEfnzdgduf/PdMbu'
        b'wXfXk7zP8nzdVwdXUdTiRyzGG+/wGHTEzX3g3EqZqE3kbHh5p0zUBvth/zzpoW/guE7W8pUz2+QnYNms7MzSOdm709YxKAsSAXCc4/KS+aJf6G3/UMDkfrNh3X+UOfpF'
        b'LPFULeO/Yol/gaWMZjVTNYxZgqNyvik0fmKJz1lgxzIp9X7T5+5SB1a2BpXxJXt47ae3NskyssMxcG0XPb+rst0UNSmgHt78eVN9MfjFwS+RTbU+JZN50VQ78SULTm0T'
        b'hLXHzbHZk7nWYrygzf6FXv2dohU/B8+76cta8XlMGnDdRpVHReGAFdhnj63DAP2bwmmN7FHYBiRR/EWwOxZf8mGAS0WgMyf5ox6qBAcQit55oPMdq3jfrn1tPQd4jV6H'
        b'Rg6dMnr7i5TY9MhU5kXTbSa5JvHCP3sq+RT2sajX6tSWU9/Ll/98Agqe8SfDgJ3dK/WeGQYy5pb0mE+zVb9JWsdg6/G/1WboeX/CtZdkSI19xnV95my1+Qb9hd71d/kg'
        b'o3d9ux4Pstr/Ki373M3FJlSYzm1NyYASr5YWH0S0OOYZQhqKEf0lNAODKO9ck1YJt6Q0Jy+PuyM1LyfjF6xTz4JmlGMTwmnnfu9dlCrquq5Gb1GS/RveOQORf2WXFOP9'
        b'PbyOxjk4ILrM8VnrzcwUembWV1Q/cE163ZQvqvbOS3r3gVJ9ySeT+5b37R8R1rQwbvxU2HRFM1qz690Fml3R53ouLmcu0Fx/X+iyDpaVemc9enBsKFXyIC3l7QcwoQWc'
        b'+JJZlO1ghwiC4QGT5ChXnirR4FnDatjBB40pClozbXCVtWI3g1aednuZyqxaOaAtRmbVAr1wP1FO7lkIW+T2IdAVIzMQhYHzRGenHwgu8yPhhRQFuxc2esFamW5zaZFS'
        b'FOgFJ5+oTrH1CXaHEgwuB95YRKsC2fH5OC07uAwbyXPrYQc8w4d1cSvBIBvjSJqU85i2oMPsGzzyu7wdotAFV2WKHbTXggEuFunylJ6vAcA4GQW0gmpOyRYyz0+4IXkJ'
        b'2WXl9Mp/WIkom4lFR1Vr1bQ5wcPuat0lzujf1rtt2hwDEjv2tO6R2A+5nXVDf3/CMemIaYm5x/EUJ/Rv6NkgYMwYYMiCyaSBC8aeKouUO1UFIRglG9kS2RYt9pJy7KcM'
        b'XKQGLpKEewZedJVz4AfzHJXzog8UkBjFFsqKTJ68W/9UOC0fl7z0aYmppiyFscF8QRcVoitiyETxn/Aos5AAXoy9l4r3KuFBl0txH6rKJaUPlWnR4UNlml3/UFXOGH+o'
        b'KudjCYkiveJp/e9VuxgrOk8ExF9jyIbcnr8Nj5WRPPghU0v3K2VK21DkIyoVukxqOTxmrmdoOX5F4U8czdDxISl4tIMpjxzohyMHBpDAgUZWM7o8usQooDb8SbxBHErQ'
        b'YCmDBByUFXnjIl9SIgsl6ItDCS4koQRlEQiDcATCJSQAoawkAJcEkhLZy3AIRKNlDPI2WdECXLSIlMgew7EUTfwVK1qMS4JqI75VVdfyfWREmdpITTx6/E8tRr9qVz5m'
        b'62pZPKTQBx2VEO/9JDAKDsNLWJsPaoPILlYHTUxwA7QGzaGX+rLfXwej7dVuOg9eRRn9mKAfapApR2cQ8INWrX6tQZbSf45ToWtBHJzaQVUZPsWEYDxU52A8VJ+0YlB9'
        b'Fi+DjygN9H52hobC+9XmvVcJCRWaCnepz+mXyaCWvE0ZpqRWfVKvzkG12Sc0Zp+g5E9hBI/sx2RQ95wyfaca+p9hVssgUR1pcIhWrXatbq1erUGtSZZmhp5CrZpz2yH7'
        b'UUU/almsQf1zMh/ODHOCDVIicBONWk1Unw5uYy2n1rDWqNYY1aubYaBQr9Yz9crqxO0d5CjUqySrUYfUZoRqUsswVKhJW2E8jZ6MJxofZoaxwojq7NRGXLPFh9qyfYp+'
        b'pWZnFn/qix6Zc16HcOfegQ959LuEm4rOd8VTH0NbUku5qcVYSVpUloOIz5yKspBIRu7PQJfSS7FSIaeUW1qcml+Smo71MyVPIWBWliIuoqBY9qrZt6SWzErRiP3I56Zy'
        b's3N2ZObLqi0o3vlUNe7u3PLU4vyc/OyAgGchNlhAf6qDs9zLsuUJIe7csIJ8p1JuWUkm6UFhcUFGGWmuzVwgEpNWqB9nPuXKO+s5m48+2pVmXXmZ8gCiBIukMuvEq/TK'
        b'nHizecxPk5+eTjKwT8GR5GzbdvkA/EeIpNnxx9I5WgSKkzavGI5XCpngDHfuSqIdzihALUJiOzezIqekFJeU43lIkylDM+dhJWUNkql+6DY9oxAqz8GNRFeyylB1qRkZ'
        b'aFE9p035GeiHm1pYWJCTj16oqBj+BT5WmXqaj9WKLQtG3+PARXhdntYKJ7WKmDXKwlbYGI2TT4GRcI81EdGx8kwY4A6s0YBn4KXVZZ6oiiB4AAcEm1OFBjgvqwU9KDMn'
        b'74A1alWwPZAghuKQ5HUMtvFj3SLYlJJT7nIGFOrzSVS3beBQCF+FWuJOVVAV8MICcgLtgE3gaLwb7DMH/TgojTfFcqd0Apn2vrC3DFun18OGUJLie9ZtGkPHVq1xW8sE'
        b'AmVqEU8JtMBGNTqw1cVAOMhnUkHLqBKqxBbsIwx9xmoMjb4bpk6l5L2rG02RhGMpvLgnWJs1PmisaqNX45wfrrAphk6qsbpABVajERDSkffGQD9oLClC+w3egZdhM4VE'
        b'8Tp4M+cj9X5WiT5a8j3nXTrfCUbigT8WD0o6POE078g5U5tBx3BxrhHzrEiQcCl7JPXs+9ujH7zO+etn1X/54sHdngbzzgucP30QrbvDjaVddfP7PP4O5hcP3urf34I1'
        b'BecP2xxSymrjYbB0+jFu3wXO2r/1rFcqNQY3OZ4HRW++LZjaD/8IhGkLCkvqfxCAE+fbWDNNjuGSzhnpfdf6nAe5wu0PKj6zL/r1mcJq+22i8apDQfZfiC6+Z2pSL5jQ'
        b'cFpT+ennnx2peWudFkvwlsofyrxZOx8KmT82n2lbEMWYOKz+pm3O8JeRwuL1Z4VpvI2e/0z1HbeqeHudt7OPiTfH55iPl3cYs+qNt8cNNr5m8atV79fabFbT+3M0i/q3'
        b'W/jHDp/wOERE0IY3XLD8MeYcTUPj4HF4h46cU62bJAO0zKJZOmAfRrSAIThEp5i/Huk9i05buI7g0xaxCI5FC9aBLj64maCAj14AzxGZaB0cBbefoGzUAgjOBgknV4hw'
        b'4gzP2aEd0BA0Bz2tDGrIVYfkmCgajBgFL/GUKTUOE/TAQdhGAypOujBgA2KaCvmxeAW5IO4SXGat1gZdBM2xGrTBJr4HrMf8lDKQ2IB9TNcFsIZGAPWAfW5yjA84ErpS'
        b'hvEpg0dJdzOApIoP9zlHxqDBYtswQBc8CwWku7n+sFeWAR57SbqBU0yftXCY5I0KgF0rZfgTtCpx+ng3xISCATAErrIjorbTWPcanvKsAKlssB0OMbXwrqJ1Tn2uFjjT'
        b'SxROpdJAYhIkbtMDHSzQDAVFNLzjJqhJx0CSAPNZoqEdz4pB/GIvnWarCTZjrDuOMgXrOJ5xsCkiBu3wJg8ccwoRERxScwUYUQHN4DiD9HfTEjQPJpxoBYRhMrhKXpe7'
        b'F+wnfuFP8uTAozpc9mY2bKZzeveh7vWiHqHWgDrZyxDLDM8koaruhIHbPPX/QMTAgTC4T/mLEVuz8dxDey6AZDWDFjnD1yOR0xoLmvfN7McdwifMVoxzVkwbW3Xsbd1L'
        b'ipZMmC0d5yydNjbtKG8p79jbsldcOmHsKmDLISWBokAJW5I9Yb5QoCq/a0/LHnHGpDFi8406olqixOxJjsOMqaVwq4Q1aeo6zJw2MetWFamO23gPrxvdMLJBarN00iTk'
        b'MYsycxs3df3E1LzbWGTcbSWykqhOmnqRdviN+UrljflUsSorbne2KLszp7tAVDBh5TFlFSC1CpiwChxbLbVaImSRSj9BHcL+fun3jHkE+rJkwmrpuMnSaUsbjG6ZtuER'
        b'sATXicBSbB3FZVNOS6ROS+45pd5d8Vb0a9FTYRukYRvGN6ZMhKVO2KYJ2O06j03p1v74WF32pYSQXgvrcH0WXOgZbsV6U18p3FzlTSulcCeZl6C6ArIAM0IvAC+gY6zM'
        b'AgpeYIbNNRTcA0uSkPRtgwOu2LwsqECo7ExJNHz+M1CBzIKl9LPWoad7IDcSBWrMwRf4zPJRzzJOCkzSKwIcEHv5wM/AIZ7X6iUaijbqYrbyU34UcyPAsGjDVS1bpu9/'
        b'taarZzzv/j8yXWUhUWCM+dTgzGtl2qXazyBWpuIQ5TlWpj4WtXiSmUV95vqIxyDkFeJcdTeeJq+JoI0ywuR1GbzyPEOT41PTWZKet4VEY/kZe9Oa5P+lvekFXxqqoWB2'
        b'Ck1+dWanOU6ERDNey/ivOBFm//JCZMeWLcYzOJKdP3scyyYQe1HURbswwIlIV3A2gfapwGVx0Vi3C86BOg3/MHbO5o+uskr8USUqqVG02vtaxM02r1netiBNzt06Ho4V'
        b'u5vcaeOdVOs727rvkhI1WKRWEa3NYxGmIM7b+ek2EIYgFd55mic4BVsJjLkC7ot7GsXMpJjlNIrZALaTu8AReMr92dMfsTmGaHlmgP0/Y6x5QvfBi64dudWMRy/YR0lo'
        b'wZpYihOnHILuOQQRlGfkhFXUuEkUjoD2rDFN5eeNac/xRXuZ5sVoPLGsPV6X/LKWNeylxmPSUeiFQeBGVFRcBbgst6ylIYEMc/P+sNErih8btU5uV4MtsCFn5dGf2OTV'
        b'JUsOETPnXLPa31NWpsemMr9qyjNRMK1dpaipYLWHPgWyiE+/oP5/MigQD4rJ8waFzJI1NWtnW5rMUNXjf8dh6Xk/VKVsHOaxtCk9f0Ze6tXLNJ6Y3b4LSX5ZsxuOM4Vo'
        b'KtbAz6Exs17CWyna+ibzLlOuZdSqoCNFaZbKKL0yKoMtcH3PaB9WZJZyU+XMgaIm7vl6m+3FmVm0juQZPOM8qpXizNKy4vySAG4IN4D43gWkyAY7hVuQlpuZPg++4hdM'
        b'e0qxZb6YGB4twdF0ZND1xFXr3Naui0Akaa77mS8YckdUsNpXLRee31SGc5caBRlFPaU9maspWKOhgjbBBdiYDQdzcnY1MkswHzQy6dv5TgAx+F9rO9PmhijnYNb+8Sua'
        b'XYPTn10Ser2Ra7LWZ1nSG7sdBj2lnDdjj7ksVB7baGA3vtnx4IfJb5q96boweqL67w/upnkYtc/8SVNz+X2H+4XmIt0dH3gq+xT6DKMTO/uswYlKTZ4ykVpZoB108uEF'
        b'cEJBHkbNqqWNhCerwEW54JkDj8kFT20VGlJyApwHtxWEcTCaLvcuWQQuEFnNCdaAJiTJ28FquSR/Vea4kqcDr0c9USVpJDPBYQd4ocKZcBI7loObT9FzcBBcng04t2Lx'
        b'y3gtK0TG0cBOurJlVWn21K5UuEZIwlYZ4S7FhNteHCaxx6DlCWNfHK9krpRF5KNldxOkDisnzCLHOZEzZjZi+043gcq0gVnH4pbFYvt+1x5XOjXkPQNvEsguaMIseJwT'
        b'jEQ9gSL0WZWm+8Ss9vOmQNUnxF9GbRKxLfBn+pUgl0swxc/E9Mbk4UuCnYtLn8vRpFE02yoLi0DJEGGvPKDFj1fmpTOlz6IAC7Lkbqj/fbITQr/zBcnOvOCf/WqDLMIv'
        b'aOWb0rEceQ33g1sYrFLvC4frf+s96ZnhlXoWh1JRoX7rqXSguYXHJLtRNRgOkegstKsNbDEixjkz2MWuhLe2kS0Xow/FUStXgMMyhyTasxM2BMyPD5pFjJgzn7OmZINM'
        b'9ooNvVceJmxgUObWU2YuUjMXie+EmSfaAUjyR/tkXNdhzgH6vEVOx2t8wqv/0uszFJiYb5dveFlXe0zpkTBE/P5VSlJ3ZG5JLYmdYxyZ1ZnnUfLDlBhH6MNUFUmQVJby'
        b'f8E0ghb6p2nzmUbkax1bmDJk+fteaKWHzFrDMktTMdI4lcYjbi/YgU5nnNhQXu+r2ib0M7JhDcAWFGIHc8Vmk+1lJaXYbEJv25LSnHwapI21DPPaPWjNwxyEKjaDocrn'
        b's7nM7lDc1uLUcnq4UJ9f2kSiHlvmjb6Dq6DG7Tn8QHL4HId0wg4sDiL+yNvAaQM+PG8XyaQYERRs57iTGJX//h+l+AXlOLxlIZtiixil9yyJ9aGyGPspUxXhy1I0+5P0'
        b'qQTa+k4cKTsjl/L54HocqmkNdvOuBqdyVhrfZpW8jq5yOA7b40LUgafuiY98cxok5UMPWIHf68cpNb8Wmp8cwlPbP1q97pHeT6djtnE+tD+odenSJR+Pb5Vh9uYf76W8'
        b'dacy2ersgd/EV9n1CZdHwaHNGzPCFuyccf5Xpc4X37lovFf0lnaTqyjw0wcbLLcdNHdSLV/4x6NDh963/fPd1PfV+O+6vnZU2myQLNppG9N/ZgR0Z8/U95X/oeFrx9MP'
        b'D72/gndMzaHJ7GCR9q//+T/nR5bHrHNMsIysOJnfC9rfrPhEu+ur7xk1vu5/rL3BU6UjEZ6FPbDmSRQT2A/qwAVQHUEYk4VQALpgQywckTm+yhgTm53yzAV1UYp8yT62'
        b'nC/JANdonbkjEPHlCvM9cD/oQpLkZVrlfZGpxc8ER1zkvplqi5mgO6mSVJ2xw2quzhz27SVq86vsCJYz3fRhb3h4ToyVTQFgREue6v0aPJs4q+lfABqBhOkKDoDu/43e'
        b'masY+k9FFoWk0mgeionKCbGW0sT6UfGG/4CxMcTx/9iThg4SfZn+udNfEPaYRRk5PlTGCcI3iDZITIdDJiwXtqgL2IIMDJtS0Fkbm3VUtFSI2eLV4jVi1QljHon+Jsxo'
        b'2SVgzxiYYR11trhUUUct5pzQlumQzQUaglKBxmND9LZxQ4cfH+vKi2nV72sqeqGqLOCiH8phQVWlUD0VyFEKtZKpftUUDp0Nyr/IXqlRClpf+jDKxvzVc4a2QFHnuwEf'
        b'RDaPXlLnW7yaIihaopcmR5LarJ8UDYuyVMbxafJS87PTVRSIlr6caB3BZ5QmfUbVsGrYNUo1yuiswpgRHKdKk+BGdGp10emlV6uPzi4DJBbibKGcLH1yhqmgM0xj9gxT'
        b'JWeYisIZpqpwWqnsUZWdYU+VKuoZP93DnucMC8nIwF5W+Znlc1GZ2LZN29Fps396QXFxZklhQX5GTn72z8QSQSdLQGppaXFAyqxsnUJOB3xWFnBTUhKKyzJTUlxl/l07'
        b'MosJMo3AQZ6pLPW58A9uemo+PrOKCzCaTe4wUZpajNYANy01f9vzD8451v+n2NR5bf/PPU5/7gjGA4HBCSWFmemkh670KM97oD7xE8wv256WWfzCSIbZRUk344kvX/nW'
        b'nPStc0520qP81O2Z87aggHYtko/D1oK8DLShFPiEpxyPtqcWb3sKsjM7aSVc2j3RnRuH/S7Kc0roFiBmZ2tBBjcgqyw/HS0PdI9cGkqZtyJ569NT8/LQHKdlZhXI2I7Z'
        b'GD/0IijDPlAYb5M6bz2Ka+i5IzkLwA7gPu2B+MRPRP7e5/mLyOpK8057thZFP8ZfeB5TFcSjxcdxF/r4u3mRv8sQhUObMCNTPlXyutDSp1fJ/O4rYZlZqWV5pSXyLTJb'
        b'17wz7lTCJX9iXNQzjZvDyMlWJu5KIZK60LcXYEPn8HcGz/B3TrG0DrMXHAW3SryLEXtVgIOp9YHRbQxyCR6FjeCwxo4iBsWAtVTlKnhiLxziMYjvwG54BR7nx8ImBsUE'
        b'TQx4akMoqAHVZVgmgQfCYB96bjWtMnJ2d3OGtR4uK2MQr3gWHoQXEgrhxdK1BJ5CgaMuan7wpgsBnICOEO4cMA0dR4KG0ayAxzG6IX2zKuhZCFoI46gZqsk2Y3jiZHia'
        b'3caGVBmOow9bY3G64idoGBr17cpzi1SigvhAnKMMj9vAZsJfWvLBRXirgg9blSmGHgVOJsErpOp4PZWtaSwTkjROpJNJBwtsC2IztZm6JHtezpJoulAjiWn7bzqXQfRb'
        b'TkUUgdmsz9sGT6ETTYMCzbBHY6kHCXxM7v/nGlXbvRQXn7OaRXu1qLJAwuCJbGGDW2RMfAQxA6xEbT/Cx1o31I9I2Ep3BV2LcI2Mdl/p5qJMwQaeZhE4DBrL/HCv94Pj'
        b'4OAzrPoRHuL5wECCjE2H5+FRnjKFROBrauAU+n8tnKdKh32SaLNhgw9sUEQZADEUkMWQBzvheRzLiAQyApcNPGAtuEODfvaDejPE/w3Bhqgn0Yy2FJBsh4agEV58KpTR'
        b'8mBDMAwHyVthZ/YGeBJei5KF9SARhcAx2ECAT5pAANrlMYWCYnBYDxJTCAkBN8i7U+B+uJ8vC+kBr0eQqEJw0Jpk+jU1iJ4vqBCJKKRtnFVhzNOgez4Aj8GBNDTCDW6z'
        b'0bDAAVhNR5bC+Inj/NkwL+AovEVcB6Aol87+2p4OD5GIWFV7FH0DnDzITjED/XBfFA7lQmJhSXTgKBTKQkeB26DfLYrEcmGmMeAAEHqBS0x6YC4sAhcV42Hthi1QBC9s'
        b'Jo1aA6+tfxIQK94Mx3Ih8bAC4QD9+PkUTVk0rEDbWXeEYXCVNDkWDZIoajaGCzznTrwd4FgwuVxoDLpkylzQFUf0JiTGkrE3qTsUXNCLkkd4gS0etE7FDy0H4lU0sAWM'
        b'xUNBIv7ehWPK3MkHNdYkdpVXONvRj94+moeDd1E0nRmCPUiWgW1xbIqpSVmAJnjHNZinTucRPgovgmMl2sVlcEQTjuiAejhaygCSvZRBLmtlinEZ9hqD+5bA+rn3lMDL'
        b'ZVgV1McCvagZoC6FBJoq0oTHyY2XOfJ7y0uL1Iq1tJUpZxYb7t8LDpM0uwvMcapfdF9JEdpjjTrFZaxKMEgZWLAWwV4gItQKyWuHdpYUlamTenTgFTU4Ai+rw5oy/Ii8'
        b'DUs2KytV6JMFiWhfPRDNPiG7Q1ODMshkhYCToL+MWJRH4W0+H+6fvW+2hVbgAtsRCGQJ3SU2bgpVlRbDy6xtYIQyWM4KAOeV6HtqCqOeVAMu2SK6q0zpKjPhBVALz5Ol'
        b'xDaN1IBXS1FjQAto11TTQrK41h4muAT2byHR17angaH4GNgSDxthO5JKO+JBI07xcJwBr2puIVO4Hbc5ftUqQvwpNHKHU+EVE0IA8gtAv7z+kzEK1Vdl0cvlbADoTgaC'
        b'EnhVB11iwj6GC6gvJcoH8y3bYQMihFEeMdFxifi8WCOzQrhi0n5kZTSsN4UtiCqA/YlqJaBNla6yBq2ZfrAPHIuCjSyKEYBWEWjnkgBiHuBaArwUgchCFDhd7oa2Tyyb'
        b'0gMnWOCYMR05VrjBbFUWcytOZrrxuwgrmmR/vMvFIpEpwYVMnZydFJ2plfp+ieyL81Iena3cGx7VA1gu2IlI5pmd4GiSLPAdHLYF59DpW4kICDhdCS8Y0amWu9fBmyTL'
        b'KMUBAxUe8ASdDrmeDwchTjecQ2n45yiZE1kux+SHAHaJKYuixk6mda39aNvkUt2P36tyuHb/yrU9f3TfXlJpOFAr+X71672qa5afjtBzu+2+/3ejG0fO2EuqfrfmdeNH'
        b'PV92fl/809S/rE+cXun+5fuHJ/lTn2Xt/fqf772b7/j1pa8bapfHftb87zXTG0P/di7t2FTG4iajrk1fbDvqeT2qRpq4+PwR/fvjM/mn/da+8dPjLw4e+Xzmp2ClI+7p'
        b'h9+ziHOr+e72e7lhpYc6Pkyq0vD9V+DtFnhjy7+Ze/S/SH3HJTruD7fjlunr/r7V69Rn7zip/zbv2+SIUxWsd464m/7ZMjflS1j+9wfqPo+L73x/9F2LrX/J/eyfftf1'
        b'gw9kTEUX+S5710a1oVxvz/Efu74u/8B/je2ffmCCsLH+78wuXfre4yON7z8CD35cJvrVh7fe/UeM6K6he0Jh8thA5l8/PdTm6RWsVn1Cz/3EgWD91b0Wa7k6GV06gvsu'
        b'vNGP3+fFqj8GP5x8MKX7xmdma20cdU72L5cUtW9ZZ/fDxUq3ndp1SbqWbz9Ubn0txv5Arl72I5e/dZxfdd3hd5yIwdFP3v7dmZbyKLt/tIcHOzdu5DXutv9d0p+TavJr'
        b'P9D5B1yYbGx+fl/jn7adujaz1eqqS9bCsvua2/5Y7j7YMVT3j2NvWa3OUvrWrnKN2l8fXn7MOfn27xz/+k7jV/3qk30HlDv/8uZjp/bPg794Y8T7x9hfJ5Tubk4LD3pL'
        b'0u21+UHdBX5A5XfhB/MP/N2uVLfhbBwnLdH5L6J7DrHF9+5krW94z7KzxybwjsZP2Yary9bskRhFM4q6NH8b5bKk5dvE+ONr7g/zLPau9/tX3budP1r6gZk9xzMnjqz5'
        b'V/RP7Rtruo2bfF/jipbV+FZ+tuSy79VC7swhg590zt91OR66LMquuuJw2KVv6thvFvzYxaz5Vfeva++mNbybfn71gk9zGfkxb6p1fJv6R6VeabOj8Y5Dm4Isj7Tm6P8+'
        b'13HvIcmVJJ8l374+NiX80P/1gP3OH5W/73UrJO1so169fwrr0Tt/qh4+/7CyoeJK/FDqW7WTvzdMfVC7hJMT+vrflU0FizMiyj+5XLD/UKv1B3DJjfaYi6EqGf+s+uJK'
        b'2O44UWrRYKm1UGdqx9um5x49ss7zYF/ekcZzJ0hPdH53gH4+DXrYmiOHPeivZAEx4leuE++6MHhLc5al8YCDHguCaUhPMxDAQ1EyFIYIkZKmOHKbHqxhgSObgYBES1sG'
        b'L6+eVbmBtoVPAs3BowFEr7YGcUVHFINGGiFes985h1gvDNNyZUhS0AfOytGkNJbUDd4kUeSWg/5lfhv4CjDX+r10SGSxBkVQrmAE3pDnA4kHTaTmbbB5wRyVHTi5Ikqu'
        b'sovcQ5Ry6rqwRhZy2TZTHnAZtoFaoisshvuMwM3NGLnbqEyxfRlgYBO4Smc+aQIjq4k2D95h0NBdputOfxrze1Qf9MCGZU+FW0YtOUqe3QXOJkchrtVNDZ35svwmqfAa'
        b'adBOxCYNRPHBBUTYDy2PUqaUdzLt0dg0kbFGfOigQrIXFRyQ+wjJ9gL7gwh+ettuHdCvqxgEGhwPI2OlaVskwykjxncvuELjlM8k0lH+6sFVOlu3hwqSZHoZ/KpEN1BP'
        b'd/UmmvpT1rBJ5rqJHTcd4CkalN0FziTBBleIlkZDfgIajxhXxPd5sNARuR80y+Lx+SEWbo6913cTvBAXQeeW2bccp76R8X6JoMMryJS8NioRtqqozeXDC8FZ0hc0MQvs'
        b'ERuhyGnD4/AcrYatXWf5FKudBW4ZmibQaWnWQTE8tXUuo30NDJDxTQE3YI2c0YbnwPAsq20MRmjL+DCoByfkrDZmdgirjTjZbwgL1hQIGp7LbVuDc1ll4CJpJc9FDdfC'
        b'h3X8neQGHVjNKoDibHphi6CoCGed8YhDe3gIByLfw3Tx3/KNI77YCM+nK3JlRfCKFhxmeIP9DFfYq6RXrAaH0+lQhkLE4gjRipHNDBgD9arwOBPUp4BGMoOFC4Nwyl3Y'
        b'GAXqPFaC886MFaCTMg9ngy5QI1uUyyjMQzTFrVyAtg5lCw+pwB6m6nbYR+hHVTw4Lz/Tb8B9laBan0YJVMN9cJgf64YqzoE35XkjDOxYiKSgrUDWzx14YAd9i3sMrEfS'
        b'A0MfSChzKGSDE9GxpA82sGUbuSXOFTEqhvAMmh8mZbyAvUQdjBJKZYf2djtdS6xbBDiCN10U3h4OsFvJIyDFXoNUtKJEhSScr6dnRAM0MkE72gM9SF6kcwyDhlB4guAe'
        b'6rTUXNGgxzItwL4tBGHuCY+Ba0SuxEB+eKhkFsu/dxm97i56bYCXdHbIEGhqcIDpYA3OWwaSqwWIOx1G8+DGc8Y5g33UspngIrgMx3g2ryaQ4X/5g1h5n9KtVD/zT4a0'
        b'SM3IeC7SQuEaMUgYK9HW4z0bSbD44NZgcbbM6ZpEUFw0tHhg8Vj89U13E+8Fxb+dKVwyaZ5IUOQRby/6zeJfLZby1k5YrRs3WaeIm5fjKwwsxg2cB+KHTc9tHku957aE'
        b'BrNPmPmPc/ynDYwFgTOmNmL7fvce92H7SdNFY97TdCbUzp3de0V7J6w9p6wXS60XT1gHCdkzNvbiBIlNz7pTFkLlGVuHnnSJvaRowOlU3vBqqePCCdtFU7ZBUtugsawJ'
        b'2+VCtnC1SAVbMXAaIsYJ9VmDRr9pj6nE95T1pImXrOzJRX188ZT5pInbYx3KzO+hLmVhhc0sYl8JQ2Ij9p8wdxOEfWJgLFosLp0wd71n4Eo6tGLCLGKcEzFjbDfXoGNg'
        b'SCLfB7cEi+0nDZyeMehMG1l15LXkteULWJ9YcKetnO5ZLZOEDkUMRJyLnHJdKnVdOuG67J5V5N2MaRuXaXMrHM8wUBQ4Zc6XmvOnrW27q0RVnXunuXb9Wj1ap3SmufbT'
        b'VnafcO1x+tsprpeU64VDR+4W7Z6y9pBae0zPuWLn1B/YEzhlt0hqt2juFXtnnEpoyt5fau8/betIo2cWSG0XTPPchiwGLKZ4oVJe6CM9NRujh0aUjTN+dNrasXuXaNc0'
        b'14n8ZefSv6Rnifwve/6Uva/U3nfaloeneprnOcULlvKCURXWRo94Vib6AvbDYMrG4UkjBFpoeeCcAVMGbvcM3KY9fUc1RzSnPCMnPCN/FTNunyyImbFzkrCHNAc0p5wD'
        b'pc6BE3ZB47rcaV+/0eiR6CnfiAnfiPHI5PENm+5Fbh532oKuifWluvYzNg5ogRf0FEzYLBRoT3v7j3pc8rgbPL4m4V5o4rjDWoG2sFiqa/uJfHh8pHY+0w7e086uQ2oD'
        b'auPeyyacQ9HYTbv6TLmGSF1D7rmuvrvurY2vbcR9Rk/Ic/BqTzgukRehbvN7+PdsFw4bTtvYPTLUMNIXMB+ZUBzLaZ+Fo4EjgXfVP/CJ+tX6ccd1gmWCXS1xM0ZmbVkC'
        b'1rSxWWuVsOyesbtEGVvojPECCBAFdAYKwqaNzSftfIcTpHYBUuMAsiHD3+ZIeTETVrHjJrGfmNsS3xSmRG/cnD9l7iU195ow93n6ObQ+hOz7xs4SjhS9pFRK2yFJQqi2'
        b'3firraAU+45IjZ3Fa9AHKjIx79YR6UjYkm1j3mPFEybLBErTugYd6i3qQl+xt8RgyHDAcFh/wGy4ZCxDoD6pG4qvarVoCTPFIaKtk7pO+G+dFh0xe1LXAX/XbtEWltKr'
        b'1FNq7Tmp64VKp3RtpLqINOD7jUw6sluyOwpaCsQZE0Z8PC60pbSqpUocP2nMe8hkG9riPawh0hCHTpo443ziHLpJk7o40oNA4/FeJtrRUtNF//xmB5OysPuKYqJnaGqD'
        b'95EkftLaa9rC5hGL4no/ZKGLPxJgKjBfFrwuiDVlqpekTk0FKSWpqEyrOyR5s6a9GOiTtm4a0tbNWdth8VZs4py1Ghbn/KLF84XPAcxlptD/5p4AtJW0az4UmgLNr8eW'
        b'0mXozn9XU49Xb2QwGMsYjyn8+S35fBkvGWyk7VdeRI1qhDBZPNaHqnJEzJO4FOls6sm/WfV/Lfpo15VbSgmeR0VmJ9WQ2UmZxFKK7aQU8WRn1RpmGRArKZtJ1c3aPKuU'
        b'1ObgeNB3JQV7KHuPksxK+lTpHCtpPHMeK2lioczBZq6RlJgLU2XmrlkI0PNNj/I75npDl8osdwpVuMoMeOmp+fNaddKwgZZLUkpjC8zzzbH/iaUS237nfauLvHkuXOLx'
        b'TIxK8nbQJkK6Sdjei5qeT5vl5rcSckMLMjJ9/LlpqcXErEV3uDizsDizJJPU/XLQJjKAMqPu06FN57PGournj/cms/XJLZ3YuPhLxrCXNX2pUk+bvqxjy3DqaOdKcBOx'
        b'xXHusBGJufzVz8E6uzNiYQ0Se3lYaB0FZ2mY9OW12FzwxMYUgU0usDYufo6xqRL2q8Gj4BQSXG7oEH1fhQqo42NbgHcFxkWBVg2iX/xSWX3hZ5Qz1i9G/8rDgnb4ubfr'
        b'ZLxWoR1Tlsc4wbdsBSpdhBj3c3wgwbJ9LWyOxxaimGjC+a+jvVYUXFYUFKVIAmElasFroAn2gdpVtFqyHl6A++ElBkXFUPBUXkwsOCgL8BT5I6WbXMimPFMyhX6ns2g9'
        b'57RoaQK5vFErmbpvUaxEpVTnjmV/FEZfDu9dSq7aaGzLPklJlChuivm4ehJtENsBT8IGHzQJ3pQH6PVmbyhbjlvQBO7g3B1PbH6w1i0yBrZhUxeSZFfKjIgRJM/q6ohI'
        b'10g6vDschc1alXAkshDeIVOyCt5M/1ngej28MQeqth7ckaX5yzSHVwiQlM7xB09rzKb5A9ejiEkE9AFhicwIBNvz5OGjdOE1GiZ3FJxkPtf2htbEFm25+WgfuK1WFZRF'
        b'Bqp1ETO6hqKzoI9FxcrUyktz6WG8smYtddnzHRVqaXWlScxMQHEtdt/EV3hK9PTh4AVtMnWzHTy4Uxd20Bdugw607mjZ1BfUV8ZAAa1uPmSfRmub0ZI8WQHbnMoM6Iqu'
        b'VcjUzfAk6M5RLyW9ZoCGEJIC9oglHIMNyhR7IQMMgRZ4kI5LACRgTDEbB7YS6VZuAifBbaKJz4UkwAJag+D8Yrm+gmWe8wGIYZeoIuLvc+iDxraYgklP3cNf+n0802z/'
        b'u9IbH/WpJqrqOmnf9/tKxy/xgd+DTyItWiOX8zfwbdw3F32y/3u9v7RYv+234c+sGhD+oX1b9u93Bln9O+kn+9z36n76w7tNA5d73uqvLPqryHlV+993L3t31COhvazP'
        b'KHDY8HjNP3v+ddQ/rEuyZtPC973WHjLxjz8j9T+q8/pFuzWJX33ulXja+vyur7UTW/eV95c3fhCbqP5uwq5Qe72DTlfNxhw1bnYaH4xQD9vi2NYadH7vwM6u++/fsNg7'
        b'3u2/5cOzVeVn7CxOxkxqhYflG1iP78u4d2hV5f6QyQuL3mo/f1BjJGXxxvfe/+tj9V9FeEcIdqQuFJu+e2ibVDNL2JMzlNxzAAQU7+AKC5cE3IpLnOyQjOltit4VyLln'
        b'vKe9583KtK6GvTvS/M963peWjv95f8Hf7ucnq3/TPrCsK+69OzNRpv/69w+6r332w12zP3y9r6xEb2lxd6fLl7cPeevbDF7+Y65w71fZwSf3f/nx1JkFv/9i8fnIstei'
        b'OhN4AV9mGX6Ut5wLgnvrHwcE+NS3qr/TPR2w6vNzqY46sZmuD26dy876+P3j0WHMv+64kOY3UeB34Ptv/TZExP/P5G8/Wpy87nXhjWtLCnafav6mPabh7dI+h5Mxg6Mm'
        b'er9x8l02/cVteOh/rKUe/Z/rPcrdr1q5rPzr+puOC26VOF97U9Xh466CH7J3xPx96zffLvr8z50fGbzPMyJKPHAQHA7gR7gu2DCrxYt3pSMCHIV3YJNMjwfGKHm8gUyZ'
        b'Y34oaFxPK2NhNzxRppj2YxWoo2MkHIwO4lfulMdaw3HWYGMGuQT7I23RxjUA7XI9HxgD10iTtOAVdX5kDBjZKdfBboH9tGfd9eKAp/w1cuG5WXcN5yBawdjpCM4gAhSx'
        b'ZhU2RrEjGOAS6OQTnVqOzY4oYuyPcnNhUBpgGHbCThbTAB4kj/paQwlOTT1oDLtnM1Nf9CNalVwgCJLlkQYnrCJleaSd4VlaESveCbv5aAhWusLLsAZ1Ss2SCQSgRabf'
        b'BY0psI7vDwfcnCPkuf4c82jl9y1wDg22TLOJtWdwCLTLdZugBlYTlZIKaIY4k5MHkETLVNc6C1ngOLURjCURFbzu1kyimYLNMYhmo+OJr2wMxJQ56GSDLji0nm7oddCM'
        b'ca3gNjoE0DEWp0QpWzDZqLiNjJBl5AZavUUozJqNcjXamhgy6zaaoGmuEq0yTKZDg9diiaItGIjgEK1FA61QjDVps2o0F7R4cJ+9QPOWebVozntgt1IKaNxM5mN7YRat'
        b'x4IC2OTGoIgmK4zPs/6/V1I9X2rBY6DIGz2rupLnNlQEiVWaP+28p3CRaK/eYNLaq7wUBmViNguf3Tpp7EG0LaF3t0odYifM4sY5cTPGltOWNt3JouTOjS3hM4bWYmUJ'
        b'a9LQdcbSRbJwwtJbEI5jCGahhw08pi3tMJi2c5MgfNrAVBjWHSmK7Iy+Z+BMal06YRYyzgnBeFxncdikIU+yRobHFXt1BkiMpeaeglAMy3X51NhsxpxLHE5XT1itGTdZ'
        b'M21m3e0ichEnTZi5C0IfKlPmVt18EV+cPmHmIgidtnfqj+iJaIkRLBcu/MTSFr3e2EJY2robK7/WSsqGywaqpA5BEzbBQuVprr1QadrGAX0zthSzW6tmuHbi5ZLE4bUD'
        b'm6X2gRPcIPll/IF7b2XTnSvKlTgMK0usJqz8hKxPza1nnL2Hfc7piLSEbGH2jLnttK1Dv0uPiyT+lIcw9BMzS4XGzRibk+5HTZhFj3OiFfQEz2i+fhHKbMWXhI2FTVqF'
        b'tGgI2ILMaQNjoWpr8LMaMhunKRsvqY3XhI0Pui+pRXvGwGiaY9YR1xInjpBkTHJ8Zjg2YnsJe5Lj9tCKMrEQaDwyp8ytOx3RYHKMyX0h4iKJzSTHdRpdDZk2MRWGi9TF'
        b'iVITF/SXsYnQp7V82oIrZExbWIqVRCslylILd/QXehgnWE8Xr5bYSIqGQ8aWCVZOcpbg8piWGLHDJMdZ/oIwnFYcfY9tiRX7StSldj7D4VK7xZOcQFQ6xXGQchzQMHD4'
        b'+J7Ilkhh6STHnlZKFDHQIpEa8n4keTOAjmGkL+sdX6XIYBls2ohWLJxUphSCPb4aTcK8+xTX/Kxq4Yl64QZWL/zcrlTXxH7F6NZ/Yf1CCoPBcMHqBZfv8MdL+deySKJj'
        b'0mlr3H2u8lPqBDxiRKSqRB/tagrqBFatSi1TlsuRVilQWKmQpTmrQFB+ZQoEHEUtZD5XIbkC4UlCx1nPH+Iw9Iq94uhn5ME+6efmyW/gzg2lEbSkKc9BBhMnOqxlQLeu'
        b'jI/zW+jphaX67amlGP9ZUlqck5/93CbQUUafoGGfjsFOX39pz2DV2DIcDBp0RKz9RcdgLFud20DEK094J5xg9LapqsiQaDHwlByKBvZl0DhSzS2IiwBX98igaASHlsEl'
        b'Yhm4qkfcSmQoN3jOYhbm5grHcg4v28EswQFpLvyw81CTlz7w1GRnbojNU725/1PDwLdCP90PljL+wDm9uPLwis/aVPf3RJhMJpW3vr9r299Pqxlpfx3xhy++fXiVvWRB'
        b'c9bfMr/4YPzLDpUN98WfvG9YNWqU1dW699w/8s/dDbHmJe67qJ5l9/t8rVj+zLnXkjjHPntdtO/Xf2x/beRkikfgP3w/bzhk9IZHZu+/q752+k2wwcHeX/Wqd/Qa/PAl'
        b'67ev241LuDwl2sS2H7E6AtBrpWijtikjbBAHdIDrmOe6HjjHuwcMphI+JwFcz5HntOtWUWRu4SXYS1vIr2zJlnNte6BQ0SC92JMwfVGgGsnADYjZOu4gM3Ynbn3V6cSe'
        b'5Su0y8h2nOUsLJ+iYXMvE95imKJddZZl/AeuOsb24oQJYxdsBDIXlkkN7Ked+IIwodk9jv2MoeWMsY3YWRI6aew5Y+c5bDJhFyBUnXbymHLylzr5TzgtxndK0RlhYDpu'
        b'4DDtgJ80aYmdtuNjc8Kp4Cm7xeh4mbALQkdislSXS1I7i8M+0OUpuHnqKHjczBLQ//DoKNF59lygD4TX8YHw84O5U1PmnIOPhIL02SPhZU6Db3GPGB+qVOYUYq3n/3Uy'
        b'gR8HnvWqKU7fmrNDFoxUlqRlTvjTeQh9KK14zNtJNJU52wvzMrGuNTPD5rmHgmwAng6uiYpfJNPvs2SVHUviJmSHBEbZbiSb/jmQbSTqphmr5oBOeCGnxGmYUYLh4vdb'
        b'/oUjiNCBiTK80uvLvM9nHRyu/z4yKbWXd6QrOjFPU9PzmuOb+juEfza8n6ssNMnWoP72plr7di6PTaAWnrBzGx+egDWKmBkJOEgErzIo3j6LmoEnLWhpG5yDdNQ5eGAh'
        b'3Icp0moDxbCEiCDlOX/jgclRrR44i3PJQiz8whF4xA3WrqQ1rStjimRPRIFzKmA4Hg79fLaGD3VT6TmWL+yS2fwJs4aWp24gdMSLpiMPl2YyKI7RrEXYadLAhY4xd9dp'
        b'lm7cN+JNGPHHdfnPZnZ44znb95nMDu8pK2R2eF7LRJoKmR0KMtCmNH/ZGOWkdcXnGVgRGBubEB5b/ANuru4vxCx/Ev0Nx2chYROIozlx8CP2K8JlEspC+sIz/b+VXU2p'
        b'p8KYP8sWO+AhfypUsja2tK2TRzZX09L9yghHNrfrKZ/U8njMtNRKZ+CI5p4PyddHwfKA5itxQPMoBoloLgtNjuOHG/vXrvhOVUfL9xH3qWjhD7Q4IrtJLavvmFpa1rhK'
        b'64f421dW5HXowtdMVTp6OrqAvn3FodtRMqnFf8w00bLAl1wf4m9f+eJL6wZ8rtnNWNsNcEZCv2ExtP0/WRo2Hbj0MWs3Q8viMYU/v1ZCxQ/Z+OtXu1n4ofQB1kj8Nc61'
        b'reO+Kya1Ih4z48jN+PNr+hPdtpLxkJR/tZE8YzdgMJAw4jzuvPi1sEmtlY+ZRlou31DoA98bie5FX78KxnfGT2rZfMNU13LFV2wf4W+0czYXfeTAxoV0ZPSVmdmuK+EV'
        b'/DU6zo1JOTsp7di0sewrtLxCWUAEukBrUAHs9NQFh+EovGG4aCGoTodDygGwFrSAVlVQB7vgfmstjLwEYjAI2sLCQK8GaAX1DHN4G4zC21pAFAAvgyZwMRVcgQMJWhjF'
        b'fgAOBQWC22A4Atxege5qhvU7wSgYAIPuu8GpaHAhcDe8BftV4DA4i/5fXwDOgFOwL7vI2wGKvGA17MkHJ+FBOAAvws7dQaAB9ME6MGK8oigwzgg02MHq0KpcH9gIb4HR'
        b'nEB4eNsKM+tUs/CAKKX13rvc48Cp9RZuoA1eCQTXYD+4BAT5iOy1oGquRoCr/ttdYLP3FnhEC/ZlwGED2ATFoBX2ov834LGUUHh8lU8uaEyH55XBSXAVHi4AI7AFnoyH'
        b'58Fw+XZ4GtyuAjdgRwJoMYW92zbAY+D0IkN4IQLc8ARHUN9bQJNeGBiKBwecolADrsLjfmCoCp5bDUQM2AeOw/3wKDiBfjdvBRJ4HPSWW7E0wFFwGXZ7u8JT8OpWP/VA'
        b'eAXUpFuA6hXbwcEMVG1HDLjJSw8vsA6HTTnwNuyMjKyA7etNwPmKEDgGLqKJGg5SBsLVvETU8wbQDg6pOybASyawB/aiv0ZjQA04kYSGox10uMJRv2CHIHuOAby4FhWc'
        b'2OW0gY9OhbO6BrAGCsCVhBJU2qKtbgvvoCfOwhEwhBo0TMEOn8zFULQRdHqDm/qwWzstBjRllwbD6jWwwwo0bFmoCu+AMQsDMJYH7piDw9no8cFCWAeFXhawN8N2bXKQ'
        b'B2xDK2EM9JWkokV3DB5P0DTdWJm/eBe8bLHJEhyPBb2mG+AQGqEOKFFFnbmMVtRx2LsUY0trlsPrnmgij4Fz/qiXg6h9o+BAEpqDZrclaEHUV4CLxuawHo3QDSjW3sPC'
        b'SL8V9vAGuFh2BC37gAob0LUmBDShVa8JbsJLhruXountXw6qrcAJKHTT9CXGtxFwkrUc9KWn2vGAYCsbNHD3eoAzfmWVW3VgO1qLvVCCBvZIYco6cMswCRxfCo6DEXAa'
        b'HEiFJ1xgB98RjsHrYJQFhtXgUXN4NVWpEHaBy4nry5fAzqr4PHRmd6JxuOWMOoEWCDyfH7UYVXHSAjEU+1Ylobpbk0DHIiAENWlo5+1j+sfAVjDshu65CCXgbNWGKgPd'
        b'pL1pviuy4Qm9nb568DzqaQNayQfQpti/AO2quhXW0fY7HdFaawYiOOiF1vg5tDbHYG0qbM0DN1GflqNxqVOBZ4Jh6y7QXRYVkgPP40hJ1yqckfx4Z/ci973g8Ga1eDBm'
        b'YoUjWcN+PT92AbyTAi8yoaDCKHU5PAguqYMjeyKAEO6zWAGa1oNqeChDB3QDSVx8one6vqMpHAhZoc7Rd/dUMvdJRJuoKxrWIu4CPXHWBNQiqlKdCvsWopm8AfbDQyzY'
        b'Ggta4AgXnoiF9UnwLLjE1kOLr94Y9KKeYMJ0aIs3HlxQCwfB5fIKU9Bohd53Hq0pSQVaDjWVeqpoO1zKgkfhtd3eHNCGhvEgmp5hRLiuqGZrR8JuU3ABipPXwnNo3x2C'
        b'o9abwK2YKHAH9KvZg9YSiK2xh/0z4aXtsC4J3HI3w9aEjXFg1BwtuXOwcQ1ojYrU21gOr6D39aG1cHID2Ic20B3UrX3e8JyBU7y9YRzYh8b8ynp4Jg8NnSQOXOTBMSUg'
        b'TLMHPfAsvFY2ycSQU3DOAi3JINCMlyRq9zU+uFzmD09sZKN6xfBgfioQF2mgfdlhrblglSvo002JAgPB4Ai8isbrJuwwR4vpNqhHnbsIhlaCwxvQhj1kC29FBAcHQWEk'
        b'OJWhqw4PoUV7Bi2rUXDQDhzn7kCruIMZDG7upBa6r4Rt20r5aOIugT7EXdYjqfcGbEW7rjNtw6Z8RD56XWFnLhrwG9hnpx4t17PgFDgGj25cjgjjHb7xutJNm4E4BrXx'
        b'NBTAy85oe7QssfWugEc4auCa4qJFW+TYKlPUjivl8ICb2l5wOZ/QzKPaO9F5dA32hUQvrLRJB8Oxu3YbsTavAA3GYF8W6tgdVEEfIk0HFgajJSxU2Q4aQf8W0KaFJnmA'
        b'qwXa/KAoAohL0S37IO5JNzyJTqV+UK3DhAeCEBE5Y6gCRv3gdRNHtBwuguve8DanHJ7KN9zJ3poHq0E79pCCR3XQQJ1G3euDN8GlVWg+e/Vg/XrLrWi1HYAjS8FpNOQ3'
        b'Nzqhs+nC+goLtHp7tgdBQQo6wTp4YKAcbYgj7mgqekO8EZWrQ+sSnZwbfbctgC3OuVBStUy7EjXwAJL6m9F6vuTFdc5IBZcQxRnV5MA2eB0e0IS14eCkdwJaEaBnJ2pA'
        b'HWx2Blcwnw+aK2Gvirk9GuQb8HT4eg9wG55QD3dBHT6MSKQYHdudYeDSiuw1aCIvgf0l69F0itCB2A1uVMKGHUC4SSUTHgvKWuFOjvTmqFJ03hwuQ2RBgO45FrjCOAl2'
        b'gM5toJ65wwScQOsbjSBa3+Bkci5q5R3YzXIoiAyHdflasCVznYrlZnjeDHTgleWB9nNvuB7iJDrKJvDCPgaPVWFam08YjJtwiA+vMpZbpQCxChStUWeAEew31oR2jRAI'
        b'SsFFCtFbe0NY7YUGWGixC15QAdfB6cwVzuB4KDhngE6D46bo9iZteEJlu0UuWjTHddBuFHrz4O1E9wjQuXoXPGoBjkRaLUIHwag6GpvbsEFlFRhIwXsllVG4EbNCXflw'
        b'CN7YtA7RC0yBBxEhQBxIwULQabCUv0YfDq0HLSlhYP9ycF0Xilfs3YAGRrxolwE4Eh+9Hgw4wMt7LUNTEOE4i+bj3HY0KudA54adDHgs3AdcS/DcpR0K94FOIAxOR+fy'
        b'fjTJvSZ6aLQPw9MscEcPtiYa65qhg6+eAwSbolMT0Ma95bM6IA9t4bYk0OYODkRzPDhQkgcGl6KtV5sLjjrC/aEMWK20ClzPWAbaw3PApeBYcAPULvMPXb7HDIrQ2kdk'
        b'8Qx6Xw21HZ0BvXBEGYjRJqgzQpvlIhqqZnjCG9wCR0zRHj3hAG5UwatFwWjNCtFJ1wSPBRbB3hBET6ozVleAwysK0PoXV4FjVYZoVV3J2AkHsk2gENHAHkQk6hfDxnV6'
        b'CyFa7gJ4egVijNCCPsNdBDE/uQ+eWrqoAnRprtBFB2OYGbgUjxbiKLi80xdt+lvwbCg8gkbuEDr2uhdZYZ6sGBzJ4jrhxQhbOEsIMehFLa0GJ3PAsTS9yh0x8AR60WW0'
        b'sTpAaw5q0ADiCQ4wQVMZGvsjprtQDzvRGfr/yvsSqKiya+0qqhiKeR4UZBCUWWWeB1FkRpFZpZgKAZGhoBQVFUQmUUZllkEGQUCZZBIkvXdiJ53uBNOD3XQ6nXTmqR+2'
        b'dpuXzuv8+1TZ6Zf8nbxkrX+t/Gs9dJ26de+5596zz97f/vape/YlFO0uToQBR+zFIcNotcPkKm7n6uOACG+E0hCP4IOjcDOV7vKuH4XUQ1jrCZeR2fkqtsVREzUp2aeY'
        b'E8KKk0Y4W0j4MoNVlsHJyji1dU/wIRP9M5ImOfZQfi7J7GYM9eAvJMIOF7knsYFIhK+HHSzshqlTKjs9FcVEYTuC47FlL/UE+gNpiFfpwrNiEtM8g6BEC6h2xso9aXCT'
        b'rnwFpgrP+apuC4dVvJeOfVTnLqFH+0VTKLeLp/Fe5HsQDrbBkq2bP44fI4p2A5dERDAbyIuxuP4+EqpVXnRgS376SD2OQX8YtsUEkGdtEsHNsADojLMl4jEED7zYL/dE'
        b'SfphRYPs+yYMaOJYCDTsKcUW9UjT4ycJ7SoUyUR6zykLYcrKa1+Eoa8aadkE3FB3MOGT1G4qa3vinOkOJV4wXjInQZZbkeYPa20lH99AbU4excpjcD0QCJv82M+8ZO4V'
        b'xrgsxB7s9S4iyLoBt8mZDBHXn6Jx4h50iId6q3zy1N0wEY2VyXjrqBdcibCPJMlVQl1Q7tboA4cYkbly7AKMpNvgpQwo1zlnhu3krpqP4LyYdKftEI6nYq3DbmiXI0Xr'
        b'i8CaQFKvNcL1yePHKCppIuyuMzIkKc+lYqs38Z2+Ag+S/qgTVPuR1gxh854k3Sw3z+h0GErFxYKjBMz93hrKVs7uukbONoTqc6pYp7Mvaic5wzUr6ImjVlvUSLUenoQr'
        b'MfFkJstHoX8HjOhm4nQ+XbCbunkzhSxh+IhIj/CnBSYd4Z4KCfMKth+HOlOYOVaYYuAPd/Ko0iR0ZhFCdPJy6a7KD5PCzzlDoy+s7iR3u4SXL+riQ7b2344M10XyHlPK'
        b'CgfSC1LKinypTq6STpbiuAhHzygR7anUOUfyq9hhQhR3zni3NrZqEpdMiDkbAk0XTa3OSaA6zfCgUDWG/Pcg+weVrgT9bQQkdJovo01lmmowUUrjuox98f4q5CvnYU0j'
        b'FYexM5d87W15LJfgDQLah7EiWD2XT4e7048Rnbkr5Q9A/OEBrOaQAcymG2KV2BSHrUkxbpH5jMfmY3OZGeFDD+O82XQTtSleJw1V6Ixmwo42Ekh9ZBKRvTvnD59PyC61'
        b'UI1Coq2DOGxB6H37qF+pOntaDZjxNsFifqGfNsxrlJBEKsTEKZoSo5wFljiVHoWXoO0wVZmHy4p4R02EtYfs2KMil6CmELo0KFa5DL2lOCMkXZ3apWoXRgDVmaMZnHvG'
        b'j6KnWybsEQmCm/qt1nyS543dxDibDHTher6Z6X6y1wkTXDpAyHWNApQ58snL+WylI7YUWeHIdgpw7+Dl89Bl7UAAuKhIF6vEEecDIudS86NZZOkVZA6VErKELmVo2YMN'
        b'J5yxO8KKjGFWR6s4nQBwBe8k451jZDdD5qSDPe5EWhacoQYXC/NhsISi8FqKlg126xJgtvsT0M96b6fbbsqGa8Qa5HE0jtxlLalqq98JvB9nhFV8uI73RHTdm6RuXZzt'
        b'p30Lk4v1D9IYT1vYsjeUQHNmCfT4lcKV7VgnfxTrc6HTh+rOwByRznasiydPUU/UpEc3Qh36wnZcjCYVncC7Z5PyiCq2H/bb786Cs3FPGA4U2x6FBVKrxkiYPpejm0UI'
        b'1KlBGj7ngIOHyg5ga7AtacRdAwus2BWRG4cNu2HMRkH66Bx0amFreKg8hwsTXrvYE5LTrrJV5f0k5x7ZinJ1rJQuKl/Ch9LH6qJxOiHcTo7DTbIN4BDNqImVtTXpDO1s'
        b'5SU30NGf9sMSDEgP2JU4sB9iWGKVhvAwDlFeHJFexJPMZhXr7dmRDnwYwp7G64YhSTCPzTQ6kpha8RqZRleAKkn93gVl0yMCaPOO0UjTIcfU7EjKcIvkdIMR9h14OTQ4'
        b'Eqpz/fRtCGsWcNjoLHmnAegN1Qw8QgjeBD3p2EiGRDaMfW5s0oWC7+ZSR0kQ3NFnPO88DIvSsEYFBsRpZDStsOYH5QmH8EYUjSQdJ3Os2k+bQ3CbQwBbE6dNJK57Fw3Y'
        b'TadkS9K7ChMKB6Ztk6jdRpLSfawSEabeIw/cSiNNQU5OGVQ7svTYsdC0gyKFGdKHZGIwzTtIXJPQ4kmRUlWJMBIehpOyD5GXqCe1mjGmqKmSIrNaT5syqHEm+rZMODFF'
        b'7qAfpsyJDo9Cp4fI4xQPGxVFGtgRcgLG3HBRbGeKSyk4nhyqB2OKZRJRpFhIENoMQwI2cQAdxkZYQYIdJziqIHgcOZpMbV0lebYl6eaSyS7RLTS5UldHfLcoJ6hib0aq'
        b'NPTq4mGlE4Ux5SSVSSQgXXOCqzycSrKNdsKqRIK1AW+c2kFmc9vZDtjy2DFo8ibv3kj9KRcbSPjkmZqKqQ9DsLrvCNHJVrhiC72KOJGDTSFwwx/74yiiukqhy6qiHtan'
        b'mmfYBG3FCSW4kQo3xGQmqzbqEhzLEItxhP61nFej261zi0+kIHKStKrZGWeCDpRpZWXCfWs1mFfHvhAyq0vuOLkrlCx7jOg0m9qp06AQfg4qtkCPkFAA2vxDkqOOiBOS'
        b'DYgP1ZIbXzLwwOviXc4EEzOneIQOwzDhoA9rkmwcd6dgoMlWB7sMGJCTu6vZfZFs9L4r8cU6Nh1lE5VF7hQWdkF3CUt3CAtHoCafPPgQ3NlH1jsZfhEmhRTw9dKQToZ5'
        b'SedfVnjkZfqOHKdgahga3Q22XrAj5jkXxeIIbM6CB3hrNxVruGqmD22iYvsSf7xvSJRr3A8XU9SwQg1XuNCbcvGIK9RLRlnE0IMLx/92dobM+66fWYDGKZzQV9hyGgcy'
        b'yTgq0gmYpw8ewSthuvqBFLusQbuYxFmtoiufLIyIIRBoct5CqtMG94xwZI9huLkPzJ6jiKAm0TDaISNQkfza4qF46TTNTDR7SW0XWys+gSvK1ImZfEIltoJ3NRvnJTBv'
        b'A/eg3seOTGMEe/LpS+MpF+gin0bw3sRUdRCmbeHu7gKi+71eOJN5hARdHRlvwMgmEk4PJ3CJ8q2QUVcYk/1MHyAX18s3xtt2hLyzOKgTD6MWBKsN0B0gjiCM6T1O5LMy'
        b'gKHrNFSczyOKvzWAuMKgkQab24rA22e1g5ThzsljBMRXZdMAxRlkAU0nrOi2yJ/hwAVCgiVjMoSbFOXCbRdYjkzh5GLN3jxCnZ6UvcfJN8xij4husqWEHHElnUS8HG9m'
        b'ZMK9vIPuOGegCQ+3J5M+dOjicKAjE4otjhmIcCmHVIeR/TsUQKyIcTVF3kcTO7fuwZboQkK1qzp4S5uCsNZzRKbKYa2ICM+cP4xpRVv7O1uS++3HG0lKOHCggOTebb1T'
        b'ss0mR//gAW0t7Ne5KPFSg+q9clHIXh81Sho6coGwYEASHwL1RwhpL9nBoq6ILHOFTGP+fMJJ8pb50MDDafo+QUxvKe0U4W2Pb1kiDic5EDB14bgNPNibApOmVqGEC61s'
        b'jFnOcIK2TsKHSS3qxiquXTgYQY0OuULLSb0D0XTt5a0kjwdBsBhIIFwjlLfwL4FJfcnbpKxa8JBY+2ECitupf4lwE+j616DdxZQFuUkxKly4r421UXBPwQEmjyjowxgS'
        b'Ds65kirc84zHVbjimONJStosnTe5Y+FAUMYm6zq17KGKkI20tBqmKELAh6ejHWxowMZxxS8QxoyhU8N4C4n/KsxlkskO+vtwYMyIwOWOFXR6Yrk5Ad4MTCRiXxx0OyUR'
        b'9tSEQk9mErmFe/GMo9zCgSTxTnletg+27cLhUqxzhJntsViZvxuGcveSaxiiPt8m7toTTKgDSxF4xT6JnEe3Ldn0ZQfzhGwcdtdLFuPDKNK4NnIfVS66StCXmw9TBGG9'
        b'dIWpKEUyhLXCaIrdm0ljrrIUK6vU7NoWHNkFNyTkUtqjckmfKHppt1fLhyplMy+c9MzBjjD9k7ACYxLs9oTlQDG2k+wacSp+G6zFcjzwspoSrvHoLqsj9WBJns2PDHrC'
        b'yHH9EGjbv3WLJ0vqQ13CSW8aoRVSintkCAukCatFFIBO6JDQO9MzmPFkZVsTsl6TOxp4vEgV7h/BkdzoqJysFGKqM+p0C13kcseVcSYc6jOgPd7OACjKuITXclXTcCIW'
        b'GnUCUo+dw96wSJM92Lwbp02yj2KDsxxjrgRDVRRL9+FKRGkZ9b4+XZPc1wA+3Ma3gjadGKzOSDyQsjcymIz8qi/eKPbIxCULgqS7NKT1FB4qCAkfJlSSjKUYw6D7Ogmy'
        b'I8MFpvG+hQ1ZbgcOniGDa4ApawqB6rUUyUPeKUzUo4vWZ+LqwSIam2tIBKFJAPPa3o4Ear1ndC5q7CTr6mT5geyxVgi97ifJKActJUE8aS6JEVupan+p1xTfzvPkDHAU'
        b'mwM0xDCkq5C7k0D3JnVmmiCxbQ83LDaUBVAZuJiBs2pkWPep7wP23urYZJxswicF7yIHfpUo/MRZkvYNl1hBHNx1w65E0u0uQu5lFRaTw7hxHImbImto0Meqw8GM++hQ'
        b'Y5NCUxh2wsn9tkiEJsyEJFRvAX2OpmSfN3ygW49E011Mjue2CKYTjUnLu+RiXLbCoJEnlKdD3S5iv74EiKZxNlsJJ1qysVIA0yLxRfJdlTCX5EZOZVbEULxeseSgM4yp'
        b'upOIG7HTUEhCWtLGW8f18K6S9dlAnyIDuOkO9yLKSKmGyfkNYacRzpeE4Zg2UR2WNuRBNjmDs8pBYhrDXmqkxcKjBIa8+Xtw0t8SRv2UsacEJzSzjhnCiJZmEbTq4dXw'
        b'49RQBVy3V3SKpPEkpkFiWeSbRRYGuMfk4l0LwoUxMqGeVAtcCybsaoeboYG+HLKLK2SURMAJuVpgXiULa1zJQZOG1gfB1BYBl4BgQXiUUG+YhmSRWq3S0ksgP34NBpXg'
        b'cjZUswfOCf5rL5yCFo+jyCbKb3FgNsU7Fqa3EqIsQ3XOTrK024Yw4EBm3klGMUWBdU+qwMgVHxhAe6xHeOEB8qGjMIqTfDrlEsya6XpS2DEII4FwR96YjKkH1qz0jIjO'
        b'XrPFpjJsYtKpOw0zvMId3rS32Qdu7UzAJXKW2KZl6WOJvR7QIUok1anFNjF5ptXSI3jPxScOKvNKCBivO3LcYCStVDc9nQSfl40P4Fo6TBURgW4mCneNBDbtRbhaZelJ'
        b'YeES1oi9wrN8CQdq8co5B5LvjCqXlO+OKiPHNJadmcWl52ExmmUXga4ICtL74F5hCN5NkPrFOXzgc8QP2q3JZ1IIfMAX58KIwt1TydxDXK4jiYxjTTGdCFu5xakTEi7Z'
        b'kdF5CrbIjCpIm5kdreIDO8LhDlLOeU+cMySum4ityjlBMG6J3UG7oJlH3q1fjdXw1cyheHHl3PGQEGIDlWFxnmZYfbaA+PUq3g6k4Z+BPgGuuCnmkccZ5+LAYVy2Og8U'
        b'CsGNHcEaKoexLVP649okm+e/eA6uwzKb0RqEpRjqIFnJCJsuIqI7DCMh+th5JmZn8i7q2g2844MVF7EB7xuzdGRHoS+OuNZ9B4XsAidDmApRJrOfoIrXnEiq1XlkAqsa'
        b'2H8MqogNTJFfadiDTVsVqY/DAge8W5ZNFLA6vRQu+5JLboB+Hs4YCrA73jDYkJRlwlpe0wQX/eOgST1AiSBzGcsPEJsZZ4DmindZKr4b2LhbXXQQqo6EW3uU5CrjqmbC'
        b'2Z2E7sTK/U4ehMZCbHU6TCE146GzntllpBt1O2FKyyucTHjAAJaVYT7xTJ4tjloRaC1gN1Sl4HKpMlbvP0xmUUVRyShBTjNFLOYk7PZteFNVmZdlgPXJuTnHhM7YFa7O'
        b'3a+/y4/OnIRmBWjRMiCDa4WFXNVQu104v43Nf5LXLoeVLbDAfsG7bWxCMd/VdH9f4u+9LiytB9w1cciH5ojtZBMNFPoUS6DThUahOhTv+6gQg39ApKBn/1kDvKV6QZ76'
        b'0BIMXTqCMjK3FvrWDGt2+alnoNecIspKbY9oIC7do+nuq3oaL4VhlbFQEW/HQks29MI4e4lnTBKbMMXbEjbhRSP/gLB3ilxEJQ45Yu0FoTn5aGJA8VT3ZhR15lICzp91'
        b'JFoGw2QsreSma1WS0iXJZI59wFwJEdIhN+rb2nm4vg1bRMS57xeRvkyeNiS1Gj+PNRehjnCcaMelRPYT85LkA+JJltgeILUCJYIsxm/Z5FRjAlt7Bu25/mYxGpbYREaQ'
        b'YHmODvcYHc8QGOKQkYcljfAa3j0OE4ohqXSZeSJIw3JuOL8V1vC2e64K9akK+0uA/QhckewDLXxoMyQwXzmNneFwi0ebI7AsIm8zeoGwkb2h6zqNRrPyNhwMIywdJ+Ff'
        b'xZYyXIMHPrpY5wYPHPCWZSTW57FfukLZTFXmQRJP1Q6ClDpVPt4RbSHVnztjRla+tCe6gHRuSMeJ7q1ltz62bTe1we4d+4kvkHkEkTqs6mbjfVXs8jbHYTWKHKuOQmUQ'
        b'LgXAuKCU0KWVyM8NAudBDmn9sgLcNA6BdhUKEYZ3a8BA4B7odCaqUGUYq4ej210UFLD2UBDWqeCloIMUFT9wJH5V44nTGoV4f5dquBPccsbWQK8AEsosdPHJ8IcI7avP'
        b'ppppslWpS4QFS1BhRuo+ySVWdvHUHtK31hioUpGqxZKQ0HvtxA5ChB6sKSCpjTAkuL+bmEdrVjYMepBCszn4VrxigLNuFNc0H4daBbiVbQajfLjn54XzLD7H8kMEYHMR'
        b'p8mfP3RWIFo9CFetsdKeBHNPH26dh3Yt0staC/ZrsnyZgtvxWGr5uo86thF1UDjNCFCljms+hXtE5y8RSDTDiA527jMoZY9WHCbJdcFyyikruOMAK8EwaCMPneZErroT'
        b'YewEhTyTMOggJPpDbtvNq4CinrCdRXjLCjrCYMRu936clSeH0h5qzuZLcWYPubcxZiOdh7X3ORO9HnfEtThLwrb2mFR14fnYLUmkOLVY7hpB1+jY7msacJ5ljKw9gWMS'
        b'Sxs56XvFhAp4RZYpEW5kyJIl5vvL5pqq0vO/TON7hjjxAkyl2vCkqzuF5Eb6w9mcEkVHHhxsy7GQNoaViiwlUAOHw82D8d0cktPIOWljGqZsCRjW8Tncs9gaRKe4JMsW'
        b'lk5kSmSTY41wnc2OpeN9ujXp0tIeKD8ezl7ToBXpREdOe8umusKIYtRHsFMqTntyiKRMqMnSftbh2inZdBrJuZfNp7kCa0x6nSFNCsnqbei0/ZnRHCSVW5GdxSLJTqyP'
        b'VKDT+nT8Odi8heg9O0fX0EU6B4fXsZrNwhFG3HqZrZhgg/h3eBi7i3bosOOQnMdB9qo2P7pQx8vZOGgpZLNxmmIbbrD0PaKyVbpn5DiqB6WvQ80L2Z/KseFJd3sG8Dij'
        b'fqrS3a9E5ssSRT48wOMc3M6ehU6171EM4UTZyEVRU9JVuzlWFk/4xf9BUHVn+zerYr8T836ArvH7M3nvlS68ouJW/17C7L20D9stjYu/XXEnIcxqySp2r7U49JBrtPKT'
        b'WMc/VVx0ckjS5mdsBg5//GL507NZPhezMgNsnazjjFrSxr5Te/U1N6PWos6m0M6WnM7mpM7W388E/UIUqC8KPfXazMSf9NYUXX9i8Khlz8EXgs8PPPy+yt6yD3Knfrar'
        b'/Fku94Fb/caJheDXUH18b6DBex/8XEVR8Phnt1Pkn6oeS/qPn9j1fZD2edJrux7Xl49bvvH2nz7J6W30DDjknMoffUO8+6ePnu+Mc/mv7+ltNu8s1Sv7k8Dv9aCykc9t'
        b'Tum42c19v+jHC2fLP3Lv6hzk9VtdeGNFvocTVfQNCAgtOb6SrGytcv3+iZx+FxO5hWeCQoXXtE24Txb5wQP2HQ2NYH+p+2cW369Qi1FfPrX2roEx319B9Hlkh9fVN5dn'
        b'nbLW35X85p230OeRzfe+MfDIs/fnZyJmXz9S9s3bZ698sq7/my+qZz4ectXLeJI46xv78Ud+H58uy/WptNmibrfyPcVCz3fejL0c/uvp+l+OXNDMguLY3e2vCXoPtEX9'
        b'6jUHycmGW2/80UIcv/7B2y4nXi/6/UfWXhkdLmnf73rk5e502uzT/3rrlPhuqnv9W2qvbnvy+KrXb0feHXuQVBwTfXbJIK/R5P2fRHw/ZtfzuO2/ubvi3vrZt20+6Wnt'
        b'HfD7w3P/n+g8PRXzc80ffHru14/O/GYt4v2VgnM/z+akVEaO636U8ts5jy5f331BHgdulrwet7nd57X6Hye8ovHTt6yKoMaj7pmfXGzhjw4MWL8pWOcXpPs/Ovjdc6GV'
        b'Gk5RRdwP35t7J7nxsceOruwu69/ZnNt95G3v8Wu+38WfXHjilncvyvGZubGKi+DVjYxX+y6NZHdlZbf9IrtX/+PY5CGr5BG95OEEt5QHz/pOzM1v/9HFoLXGd562vdr9'
        b'Z4vff/HmvfOfqc2n+ZrOPvkizqeg/kr/G22vTRpcf9/hhvcu69NHbF/0JvwoxfajmlHlPonB2pLS8nndooL1z7ufO21Glb3I+aO/dUbSTHWkjbJslW0DmVk5gQGztFov'
        b'D7ajM1n2PPE1by/ZAgdoU/yr54nzdaRLNH2w5fz//bJLttJ2FyPQNVgpXZNLjDJYRYxtuWoCNaIH9RpiiSo59AUex/gsX+kMdMrWuI4WnVMRv6xyGudPF6kpcAwDeETY'
        b'r5K7aYQqaU47V78txadUiyS4oAFX4KqGkpoyTmlgdc4peY6NOp+87z2cf84e4j6XuFda05Gw7q8qn4JrX7YfyVeAJeI4V2V57gZPkw+mSoUOrBpb73FbbteJLdKHp08c'
        b'gcpiuKZUpLaPQuqZYvKRdV/TIN5XoOvd3vt8J3tYFmvjX6bGw9Wkr8uOxzJRNNrE/O2Ttkr/HxX/9uWy/97nnWM40rW6Af/g7+8+Dv33/2SP0CsJhXkFaZlC4dm/bEmf'
        b'kf8txY9//vOf/1TO2YznctT0NvmKAoP3NLSbnOpPd5hfKess7nfqTxtw7T47eqjr4rTllHjRfFqyeGi6dNbxlX3f1saQHzhF/NBwS4dTR1qna7egP+yxoeOUwWNDj3Wf'
        b'qMcGUesxsetx8Y9jEn5gkPBDfbN+7db8dU3LTR7HMJG7qczR1m0KbNar3bupwDHwrVV5V89sfXvYY72wWmXaY2j7xMD9sYF7reqPzZ2fmO97bL5vXWmbdNv7sbk3bX+q'
        b'wBN4v1DWFJi8sFQU7P5M21hg+JmPPG2p8wUuL1SVBIYvdDUFxpscVuzgGG2tVXvBD+ayPax8ESNnKrDe5FDRJHrOPjb3cTnKmi/kCuQEni84X5WfSMtnPDq4KT24mSlP'
        b'2+8KDF7IXeDRtThflc9kJdU1lJ3AZ9839ypxjLetKxn+WKAhPe24nMDoMw4r/3tV9n0zlto2fCFnIfB+zqFCenyTfX0Rxk2WF7DMUV/z8Vz2sXlWWdqFY4oCyxecr8qn'
        b'0rLf+Jn082VX2OZmgIb0hBh5VvWrclNaduQ9k36+PEF6IFd2hQAFVvWr8jNp+bKidHewagJXYPYJh5UvxHL+AsNnHCo+2yvHFXh+qsAVbH+hoCYw3DSTtieUoyHhsPIz'
        b'afmyJba5uU9eWiVOQWD/gvO35SfS8mV1trkZoLZTkb8Zy91BZQxXtm1NZfzLPbT9NEeBxkVuM0TJhnYl/lWlvymfShT28ZXknoYrhSuZyK0rGT1L1ORom9cGvq+3s4n7'
        b'Q1vvxcDHtn6LJY9t972lad5v/ljTsv/QDzR3kp7rW/9Uz/x/qmPxz9Ux/kd1nlIdk6cadFt/2Awq4XIFodz3tE2HVNcdgt80O/Cmdsi6aohstXN/oGGEMud1ZZ0Ik5dp'
        b'1FzFD/7RG5f/FxXSpTmpX5sn4Z/BWfG7bEHKXyDW7ktY/89yzovDXC5Xky3A+9qCrdPW/FeSwLGRfEVOIVCb84q2SqAJL6fk6VtyxeE0jr97Gidq+k4YL1Cz+tw7vQ6d'
        b'mS2d37TM32fuOMo3OPojqPzZNsuQF/vlnva7D3yhm/Ktmk0rE29B7a/9yi6+KZQYfOppVp8n/rZVY1mL7sEQrW9dP1h153rMtd9cP1TZdf3wU6tH7yRaP92R8q3W7e+8'
        b'89ax4YITgVG/+E7rUfdXPzN9krKevPKx+O31n76+/svg0AOhDus/9lznhpuI31y8e6Xk9YdR7x55J97DbUL8rd0/h6lHZ0Kj35Y8asufyigTukq+1/ydmdfla9qUvnus'
        b'l/f2D07Ov3Fs1Gv5u5LW7W+/2d3j+Of3P9piP7defU3N41ff2G/gW7o5fc3kd3stAkzNP9NKK+cZWzzSamjuv6TT85FqUGxRg67B4jf1cke3o+uW7I8UFhaDGj4q8mj4'
        b'kHfqlx+v/qr+14WuS75P7dtvXl9t+OarGLHisX3P7BdJa8+0HnVMXC38hCfvkbvP/aCNqZSfHtU9wuLh6GhpbhBFjgrMnNSUw1G4hGvSFbqWsOgWXoTL0Q44zeqxNTBa'
        b'uMKDAbgBt6RVLGDgDNRDoywxsnTauDlVkaOuzduGfWayF/FdhUvQw96tEanIiYYmBb6cEtTCiCxh9CXoKsL6XQocW1XuYQ4O4kSONBdMOq562GGDtYMkiLFjLkfgKAdd'
        b'hnBd1ua1vboy1izP3oxwlR/FhSk3vCztV6ArTLH13A7SChQzV8tz1PEKL8oJh6Xpb8woNr8ry3+9w1+WGafaRbrg2BMvYaVdSLD0zMhQvGYTyudoYysPlm0NpeeqFsNq'
        b'eJh9VGSOqzOXo4gtcgpKmrJk0nXWUeGwZu7kTOeFyxJ6aZjzvAPVZdHA7KGj4VBrRYdDI2VH1fEubw/cf9mnWIsorLdlqXN4bN6hkX+ICw9soUJ6MB3n1dmq8Uh7klmz'
        b'BX8PFyZgAVdk6XgqoA9v2TngNYpCPPAm/yQXFs/GSTPW7IA1bLRj+cUj2EUjQ+2xE0eoV1vP8+FS9Alpt4tgBCfC2W0xgZGwVWygZq8cNuF9vCJLVVRnjjeL/1sN5VBc'
        b'U5WDqbxTz9nb4/lYo6yCMxp4vxjqcKEQ54ooUFHjcJJwxng7XxHnXKTt2LNn26U5z+1YYxxSuq5DEXJ4yyRXll58GW8f/jJNONRgryxVuI7ac+lLkC5LSNFg0jr0Is45'
        b'SFM/Q1006xdc2xXlYKPAObBfsSzERhaNTJjDgoo1xTNTOMeePWrm4Ag2HJVdpwqGvdiaDGl6HpzDMfkyLg5liGQpeAxC2TEH9oYn6bJOuOlMkdkWCR+qd+6WJfmZLbIi'
        b'iV/BulRcwLoIOY5ghxz74QhkectJcnM2dmEO9pEOjlyOqp4xlPOUoQJXZZm82/JhIDxPTAMT7kjKRvZDN6/jzMPew2pSbYIWHCu0C7G3ZWkC2Ihgk5ynHN49eFFmN2OZ'
        b'sGQXJs+Bfk9uOMsMXnPYxv/fEfz8253b/yMXybKM/J0o5V9zlmxtKnOWOfk5JS/jke9yWDzyRTnnmTFHXuddNd0natseq23rKX1Tzbo8+F2+ck1ERcS6lvmQx1t8+/f5'
        b'au/ztd7na3zId3rMd/qQb0fbX/7X/5Dv+AHf6gO+7aacgrzephxPYPSBqvmnyhx50w/45nTuC4VDXvL7iT3/jx+fyj42s0pIQXXLo//w/AxtaW79hMNljRpu8ujz85+p'
        b'6NMOeb13NXWvyNMueb0/FtsyDVRRCDLioJFakA0Pd8gF2XPQmsu2bXhs214lyIuHnlwqZWzMdoOXJ8oXd5NANuRLJIV5og1+Xk5xyQY/MyeDyoJCUf4Gr7hEvCGffqZE'
        b'VLzBTy8oyNvg5eSXbMhnEfOgD3Fa/nHRhnxOfqGkZIOXkS3e4BWIMzcUsnLySkT05WRa4QbvbE7hhnxacUZOzgYvW1RKVah55ZzinPzikrT8DNGGQqEkPS8nY0N1v2yB'
        b'fGTaCTpZtVAsKinJyTojLD2Zt6EUUZBxIjiHblKQ7uwmymcZRjfUcooLhCU5J0XU0MnCDX7wwX3BG2qFaeJikZAOscQmG1onCzI93WXvrRRm5hzPKdlQTMvIEBWWFG+o'
        b'STsmLCkgIpV/fIOXGBmxoVKcnZNVIhSJxQXiDTVJfkZ2Wk6+KFMoKs3YEAiFxSISlVC4oZ5fICxIz5IUZ0hfrbwh+PILdUeSz1KMfsVzpcOT+k/+mZl9pbXSgqXhLY6X'
        b'Kiz9EcPT4HLz5Bmb+7rymbT8lxmeiUKgA+cVB5VAD94flbJoiEUZ2Y4bmkLhy+2XTPOPW15+NytMyzjBEsOyzAbsmCgzykZJuhZ8Q1EoTMvLEwplXZCuFt8gvrihkFeQ'
        b'kZZXLF5lQYAZ6aBshbl0Jbxs9sCHxkqSJ/ITWyqytAzU7zAqSMe53KdyfC5/U5Wjolau+Alf4sXV3SyUEAnReqK09bHS1o6wt5R2rtv7vbIDrR/bh72rpPmesv66gfOb'
        b'yi7rfJf3OJpNhm9ztkiv9X8Avv+htQ=='
    ))))
