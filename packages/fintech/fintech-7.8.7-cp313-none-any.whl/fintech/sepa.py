
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
        b'eJy8fQlck0f6/7y5uCGQcF9BzkAIpwp4cig3KCEeVYEAAWIRMCEqVlvPFsUjiBaQquAJ9UKx1Vat7kx/vbYHadqCbLe1u91e22612nbXPfqfmTfBINqt3d0/H53MOzPv'
        b'nM88832eeWbePwKrP67599Yq7OwBCqAFMUDLKBgfoOUs5hbZgXF/Cs5EhvVFmENUDjiUu5g/AUw0h0zB/yvxu+mcxYIJQMGzvKFmFttMAItHc5CAar5djVRwZ6m9Ytac'
        b'VMmy+kp9rVpSXyVprFFL5jQ11tTXSWZr6hrVFTWSBlXFo6pqtdzevrhGo7OkrVRXaerUOkmVvq6iUVNfp5Oo6iolFbUqnQ6HNtZLVtZrH5Ws1DTWSEgRcvuKcKvGkCY4'
        b'kPbfwU4JKGFKOCXcEl4Jv0RQYlNiW2JXYl/iUOJY4lTiXOJSIixxLXErEZWIS9xLPEo8S7xKvEt8SnxL/Er8SwJKAkskJUElE0qCS0JKQkvCSsL3AKWn0k/prQxShigD'
        b'lW5KH6Wt0kYpUTopeUoXpb1SpHRU2indlb5KoOQqhcoAZagyTClW8pXOSn+ll9JD6aCcoBQoOUpGGawMV7omRpCRWWpbF1Eccre366QBQBlx91kpveuXgNSIVGkICLpP'
        b'aBWYxg0EVYxdtZRTUGE9xvH4v4h0C4+SRTWQOhfU2mJ/tA8HXHrcHvvKHD+ZPAfoQ7D3cbjtUdSCthTmzUXNaHuhFG3PVs6B59yiBSB8Fg9dyUdXpFy9L046bSLckZst'
        b'y44OqEZb0LZ8PnBGW7kF8Gl4VO9OCkXPT8PxqYnZfMDjMfAAOoIu6v1Jo8Lh4Sj6Tn422i7N5gE31IbONXLhi7xlUg7NHe3EVcmNT8AJctGOQpyHS1A9fJ47pWyO3gfH'
        b'u3PhZhKdnc/GOqNTcFstN27OJJwBKQQdRk8l6Ug0LgdtYwDsQhvsszmwH+600QfjFKGOaJsDOuuCnoN9j+jgFnS+AZ1bDltcnADwC+bZwHUeUoYWBl+EbfAyasnLgVdw'
        b'K7ZxARe9xMAuQQxOICUJukPQuVx4MiI7Gm3NRdvglkJSLS90AW6PKYiWCkDmLJs1cEOqOUP0fGUKGsAVy0Mn0M5CPuCvYdBh+Bx6HifwIqMKd8CBqJxoWX60HFe9B3Y5'
        b'unPtM2bgaD8c3YR2zovKkkWiLXmkaegMfM4BGTi4Dw5zKxir0U+wjP7L2JkeX4IpAJMnD5OlAJOvLSZZgInXAROvEyZUF0y4rpi4RZhw3THJemLC9cak7otJ3x+TdCAm'
        b'+CBMxsF4EhDyDldGKKXKSGWUUqaMVsqVMcpYZZwyXpmgTExMMJM3U+xgRd4cTN6MFXlzxhAyk8qh5D0u9MHk7TeOvAtZ8h62swGOwLZMIClz9FL4ARpYl8EBPNCdzANl'
        b'ebVCGzZQlGkLhKCs2KaszHEqJ5wNRFw+sAWvFdnOLHPcF9YA+kAtmSqXHLx5t93AzHWhX4R/x3k+bl5YM1NLOOuJhg6m3wZIYqWLkj6Mnxl2ANDgT2bectntwkTckAiY'
        b'f3llrDkKRoA+GkeEoWOpeKK1xMyNiEBbY7Iw3cC+4ohp6EJOPtopk2dH5+QzoM7Fblo2ekmfit/IXBGna9SuWK7XofOoH51DZ9Hz6Ax6Dg242OofcbR3tnNygDthM9wW'
        b'H5sYPyluYgI8D/t5AL60yA6dhM2r9XmEUjvgPtiam5dTkJ2fi3biSb4NbcVzZAvajisTIYuUSxvQqegoeBr2whNFOIuzqB21oj3IgJ7Gs3T3fAA8Y53c4Euwawylkf73'
        b'JANRRSiNQxgwpjUG0xc/kWumBU4xz4oWuAFjRlrJHTPqnFQupYVxoaO0UHMvLfDG0QKvQEsGUxM2JYSvy8S+I4e7Byr2vyF80+vl19YxaV75PQebkoo3xfPiKrbuhTW9'
        b'OyTzPlz6nVdax+NXNw6fGX5L/EbZG7z331kv3flOnrvg7UbwzVrb5Oqvpfzb3ji3UlvMZVpw/+0kPIGXXA77GHgmAnXQ2AD0LLoYJUfNsB2dRltkDBDAHZzoyZNuk36C'
        b'G9GJNVHRePClWdEcHLWXE43OLGLjzsJ+TlQ02o55XF4cHwgeYdDJx7S3CVuFGxKd8ACilix4EgDOWmY23CSS8kY4EVKtEMffdXSkGyTr1q0bcZ9apa1fra6TVLHrr1yn'
        b'blBNH+HqNZVaN5yIQ1LPwc5f14EbszlA7NE+uXVyR2LbtOaMYZE7+3AgpTOla6pJFDEkkhtFcpMolkR6tqe0pnRoesUmkXxIFG8UxQ+JkoyiJJMoZdAx5RYZFq0NdqSC'
        b'Ebs61TK1Di/96hGeSlutG7EpLdXq60pLRxxKSytq1ao6fQMOuVt/AXbKyiS4CVpXEuhmcTJIbCJ27qwDP87iMIz/J86eLY+uc7jB4TPiaw5uLcmf8Fw25Q/bulyzFf31'
        b'JuavQsvTnVuEInYLQsBhhxhuBed+9FNDSJhrJmEeJWJBIm+UiPn/RSKuupeI7ccRsWsBXU+jUA+6osvjY97U55wE4DG0H3bqSceEBaL+XBzBSNXzAHrKT0/TwzZ0Gh5F'
        b'A3h1YfgK+CSAz7mX6Un3pc2GmGxJ+Kw5XgDt8c/Vi3HwzImw0wEv44wr2iUD8CK8DM/SCNSsXx5FIub6wUsAdcHdaAuNgF0Ktyi5ADCL/OApgI6hZ9BGPan8ZJts1DYX'
        b'e1bDi2kgH7VD9gUveBDtR214YGXwlB929qNuqR2NEk2CV6bg0UCb0fpk7MJdqIctZG8G3PMYiTkCr6zFbhO6QCMej0SH4EWcF2ZQfRnYXYPa9HT6nE/GiyuNOQ83wZ3k'
        b'Zx06Q+PQk2vRQXgRg2W0Dz0DN+Ef2ItLIrW2D5iNaMxleGEtcXfz2fZftoWb4UUX7Ot+Igc7sDeSdvwMOyd0CNfMAXWlAQd4xpFmg3ar4UUFzicc9i0E4bi/umm3w73T'
        b'8RC24dkQ24BOgNiSZL0HSf6iJAgz1nYcDndmow2gFPPeQ7SyDF74D6IBHRpY4a1gAAf1MiGBsJXlaStW7eTq3sS+wLm5aw2FDhtmCv/vwMUXPzswNSKj8avrPQrXT6Rf'
        b'fDjLtrrlVGrjbzlf+t52v/PS9k6v3rfUHb//+FLTpe1/2zAvoVjvcV0q8A7J2pXtIT2rmen8gi788ytvzjy+q/5K5LL3c46Frq75zu3QZ68PLV3ybptL9JSaA03GP/wt'
        b'9E/7psUf/7hw0ze2q2Ifc7n4/k7VoX07GBdFzZSBKWscn7tz07WyoMsYCVM9yten3VgWeOHkuYV3onX5S36IWjnB6dkpm19Tt738U2XF0ePP5Wx3eOZzX4e0oN3u5zFj'
        b'JfAHHoZn1kbJpWirDGDWeAIeWchJgDsibhPw1JAehJERas52Ry/kFfBJx3PwKLahM5Ttwp14qTqKWmQYOmLUKiiBbcGc4DWw83YQ6e1zqNOVLrxoK4aFaAs8keONWvlA'
        b'lMhFu+AuMS0iBKPBfgtnR51NhLljzg7PaqS293DZBzo6MkoSCWFfZgY24qCuq6ivVJcS9quVWBjvWyzj/WEOZrzuw55eBtth/6BecX/xVfFdj1/gTT7HM6g584YAuLq1'
        b'27TatNk1p37k4j0sdm/PbM3sSG/LMzDDHj4dqjbNsJf3AbtOu+6QXq7JS2ZIvcEFnr4dqj0a/HJA6IElnUv2l7baGXjk3ezW7I5KkzhiF3OTCwKirwt9h4ShRmFod1Wv'
        b'yiSMbU4dFtLielJNXskHUzuW9y7tCzzg2pNq9Eo2CVNwvEhMFoi25EFHv799xwXeKTpHMgyRduliWzhZgF12BbAZYXQj9nX1pTos0dWodVpC/VrP+/SczSjjN3N+icXJ'
        b'JtHJZs5fiDm/7w2AnYdl/3sEoeCIQ+wvYf8Ew/DHsP//JoYZh2fHYxg7Fs82+7qBkDXVOLjMLyksj0WpkSuygGHqVQxny3I0dRowm4bO4whxOfYC0FBW++fpCWzS2avs'
        b'gdjRzQYIy2Q78+YDypKmTId7EmJ5a2RkuQDla9Fuze/+sYevW4Hj3g9rHKjofEMIT7wshDVvvAYEv9k2L83RUTrV8Ys/5M1TeHm5rb/U+JnwFUlvwa2I+NjN776wLSjP'
        b'Z86Kg0mDfq9IqvLeD8qLbVMtVXRX2QzwEvqBnp/AGzgb+wVHjQHWgt1ead7X61QD35WVzVFdr2XApwku62y9pRyKcibCZxwxODIjoxxPTnQZOns7kEzg47Ab7ouSZ8si'
        b'pXKMlNEWgE5NBF4SXgm8BPuk/AdPSD5g8ZB5NrpW1KgrHi2t0KorNY312lIMhiIsc7KCnZM3GzlAKDIktKzqCGpZ06nrTuha1Tuha+2wp9+wm3u7tFXaFtWc/pGLR4fu'
        b'wOOdj/dWDwVOMgZOItH4tVRDmsGmI7ijvGN5R7hRGNScek0U0j3XJArvTTSKYgYdY7RkqC2zg1uhqRyxqajX1zVqmx5ickRYnEXWk0OHJ4cPmRw+DzE5tEQuHgfrKT1W'
        b'micFFSCtQT0zZkL8pwLeODzEHzchMtgJ4R2GJ0TNbhxfNvVTTw8z7ZcscgWSsld5hPa702pAsZ50WhoWjHYTWTgsMA7ELXGmST9VYBEvy4UBM8vynlIWszOCA/frEnBR'
        b'sBmdjgfxaMcUmnZiFBYci/HswYJjcHEumzYOnbRPwOSSiAYSQALsQRdo2gOTHIHXgq08MKes9p3FCkChQvQSmwQMSODxmEScvh0+Q0NXw/NZCbi74TnUPBFMfOIxmsHJ'
        b'GHcQUbaGiyu22Kk+GNAmLFyDWhNwY+fD1klg0poimtLfyw8kef0L4KL8fpg+ja0WXFfAScDwAz47YzKYDM/BF2naz6YEgZlz0vi4ZxZLFwSwaSej9eh4AoEeW8uTQFIi'
        b'fI6m/efSEJC1YA3pmvKCaSvYtFgGHJgKB0gJfXXJIHlNOE3b5iAFc2THCFGmcVyKzHXoShDDAdKPHdkpIAVtEdK0RzUysCDiPBfXN22iY4Q5bXME2k2EFSwCd6eBtKpp'
        b'NNgHQ591OoL7LojSQTp6MkqPERionx9MBAN0JiwDZISsYmtm8IdndLgfRfGzwCxkgP20d+ehXrSTzPr4ebPBbPi8lGaglC/S4d7xbMoEmTPhdhaynYTHg8jMgvvQU1kg'
        b'C3YvYau2YzlApMUr4f5skM1FR1hIugft0yDSPNQHu3JADnzxEYq5V6A98Awa4NAkR3NBLobg/bSEMvg02ogGSM13xuWBPPTUVNoj/NUC4FjcKMBEm/dRVQWgiZfDk3AT'
        b'GiCE0e6dj/HzDj5LsTMcgNirhId5eF6/NoHtvmzYHY8GiFiwua4AFPBhJ007eWUYyGt8j4MzLv9YF8imLQhi0ABu/KOwtRAUYtB0iqbduCoKFMcmY15XVl66dAZbCW+M'
        b'iw1owIbU2GkOmBOH1tPEVRO8QazjFBs83mvellaw5A0vu8DLRPuKtk+ZC+ZmLaBJA9LsgLBSzeCkjkemlbOEDJ8uWuBAuu6UqAgU1U2nKa8rXIDf4jkMiC1zTJvBZ2ub'
        b'2YCuOOC+zICnFEABO+F6FnXj2bLOAffkDF0xKFag4zSHDW4+IFHcxcdtWPzPCUFsDs7oiqcD7sYS9DzmWfAC6mf7JigQTLU9ysOlLf6httZcrzP59g64G0MC52HK2byY'
        b'psxZEQwyMt4j8z5tyaNlbM/wsWx0zoHMsGZ4Yj6ekevZ5s6QeALZ1IVc3OV+lUI7Nlv0QoS7A+nEQ54LwILkeTRl4gw5WCys4uAKTFjrsojNFg7Ayw2whbyzk7MQLITP'
        b'B9HEC8SJoCZDz8eTUfuHJXXscr7OPx5UJq7DlSgrusDzYQPl7nGgTLaXwVN8QlF4DJBy2OnRvaoUtuAuT2YeAY/AbfAls/SmXgNbCK2eg4ZFYBGeN9tq//rTTz+9L8OM'
        b'McONzH5ZXNh0Nu/+yEmglsdjcOPiP3YpAZqWzy8BXTru3CcKK/StrxdwUoVPHq/mu85ajja/z/ec5O4pfpm7xTPmHwlb7GzSyq9/+nLLzew1pT9pBHFxP3xy/PZ3ev18'
        b'/ZsxNz88uKpAsSVgzsnCVtdqEdJJYqO/zHzsSmbC1j9FvPTkk39KXnvrp4H6giVlyDvyQnPrcpnB7qUfOz6dsOtTt6dfF897TXn49Ykn2nyHQ86f6zL+5fkVK89dPP77'
        b'ad9Upbc3aUfefvRi9zcTcj6d7vxaul+r2q8tPCn0nTlBx3tb9RFn1+u+47RXiuZ/OrHutUXnXpvyoYuysGe7c8Czswv5GxZ0n43vr/7pg+///Ej88WWP7F86IfDJ1x57'
        b'ffKcZ5Nu3dkeP+Gl775+6e/nH3/pb6Z9rw72hczifJ/3feifulQv1hwJ2mWY+m3nfgfZOz9EP3ZnV53X55ffOruI7/1yVfJi7zO6pteX18uWJYRXuB9Yw53olj116+dY'
        b'7CGKTLR5sr8AXsGySwHR7O6UMVi4Oc5Bp3LhEaoYykcX0HmKi9Sw16w0gk9JbgeQ4dyQrsxF26PQQXQYbc+PzpFl84EbusBFT6XDy1SsykMb4HNYrNmWmw1PomcLsGyV'
        b'xPF+vPQ2UZjnOil18GQWPDm5IDqCaOfRTi5wRQYu5mAuv0LsGQUoI85moKWvKCXij5ZsSVCUNY/DoqwsrgVlxbUQbHVd5GHQdjCGye0zWmcMiUKMopBhT18rxIWxjLcz'
        b'gVhzb3CJz8u3w+yTBHebfRFRvWZfbEK/2Zc05UIR60vNuFrO+nLyX9OyPsW8wQWPsN7FpYOqCuq9TkvhEx8thfpoKdRHS6E+Wgr10VKoj5Ryk/poKdTHlkK9bCnES6Q6'
        b'MS7HhvV7+3WM+oNCuoss/sjo3nKLP2FSv9binzrjKmPxZzCZzGujT3lMITM4ZzSzYmY+Q4o3Py5hyhhSBfpoS6pQdMOO9fv4d5Rb/MFh3VqLXxbTz7lp9qdMvTrhO+Jv'
        b'zr7hCNw9mmfd4Dg6+X8YGNEr6lX0lvd6fRAY35ppSMVSbUdcu/66l3+371BQvDEovj/RFJR0AfumGb2m7eWTNgf0JvYEGr1i9/JvOgFJwg1n4D+hO60zx2A3LAroaDKK'
        b'pL2Kfre++SZR4rCvBMu04om4DmKvv97mA7H/LcA4+V/z9LvBxb93dJShRqa6pc8AaIZ9hiP3ZQcGuxZdJBcT44MhNlU8WiHseItDQDBVPP6NKB65DOP6sJJnmyAYHHKQ'
        b'c/8tyCZ7NMAKZHP/iyB707+XOm1YkC2MxFgWw8tZC8tkddVCM8g+swzjEFIRzzJZdUw2oMuJChpKsCxJJUm4DnWU56FLmnf+tIvBqzQADu8ODFR8c2o/lif9iOo9r6dR'
        b'rrM95DZnu7Q4P/bQHiE3fYKh/W0x9HvT782rnN1OVbZVVapB/hufx22KlcZtir/6/sCCptjY3tiGowz4+GO7Y8KnpQyVFQN84dao6KTUiFE9ugidlfLuy5wsKnGWMfmw'
        b'jEnXqNVXNOqxHFiqVVepteq6CrU2ycKkZgFWL57Gw7RGtN1tU5szrrm4GRJbmsz8aliI566hyGDbkdjN6XbtSDIKg39W2BOM8HS4qF9OgUkWZ4M1BabyGMbtYcQ78uIv'
        b'oLyx4t1/k/LG7dlwx1GeoICF5BtnoT0OWqKOPQEKMaqd9jilvT9KMRrC+d6YuFKreyIIzNZkTvsLo5uNo6K7f0c3d6CXhcKC5+z3VkzvMIqfzeVG7mrMfg1dFcLDvESX'
        b'MNGblRP5Ec6fHkl4KlbyW0xVzwPwfpPtznyOlHObDEsYPA1b8VJrD3eM0lWMN12mQ2AfMCsgJqErrA6CVUCcXyPl3juUpIWjFOd1j87hLr1Nt9Bbkpne5ljTG9lowWth'
        b'd+KQKMIoiuhL7+cdz77AOV6Aqe+aKLq30iRKGHRMGEtiFQ9FYtMtzhZrEiv8VST2S9RqfCXzP1OrjdMijGdwApbBfSt1IXvIXrFh2fPT1yxkse60mWTzF0hiq7au0abU'
        b's4EnnLk0m9gVjf7nZyYDjfincq6uHIc829VPNGWSVzFtvUyob51dnndQY8Cc6bt/4/NabnE56FO/ctAjxybhETvm/ZvM+3E2CV9q42I/jecufLNsbvf07rXbImf6wYMv'
        b'C9/kDaR62kQ067zX/t7bKykBiz2Oc7XNmCaJapvusGyCx/PyZRwAT6HnebkMPIt2NlHVNhxALxLNtgztiIEn1xTmo+0F2fAED3gW8SahDajzIXRjTnXqVY2llXp1aaWq'
        b'Ua3NsBDnI2biXMwDIs9rvrLe4tML+xaafCcbbDGJdqwi7C7jdGFfoUk27SpjkqUOS6S9qT1OhuxhT0l3XNvaYS//6yLP5ly8fHv5dWp6ma5ao2ekgYeXfJHnGHUYj5Q8'
        b'YlerVlXiSjQ9jLo4w+LsBFYasUWYlP2JRuxhdgtZjZjFtor8CSykVEfomcdaGmGK5igFVFlso7RNFJipmjtmr5AXMIZmlbwx9MtN5VGqHhf6YKq2G0fVfJaqU0TxFKtc'
        b'tVmrvRyUwhLwvEyWqq9XPu7oM80NaPZ9+ipPtxHHbNYvGajowozTw8w4A9Ij0oUJAU2vCOf9/bJTxJS5O9cH7XU/OmHTxA7jbjso57/LfyPIryfvxZklcpvBvEl5Cemd'
        b'J38A+Z8IznqlX9jttaEzr0du4v9O/Jbd5C6F3eEnuVXTO3YO7ZPcShtufWvjGVXVp2c2nWW5buCrbtf5S7EERMbXBrXBnQXwAN2hsQEceJBRpsyhsg/qROdQb262bCJa'
        b'f9ekaBErOG1Hhzm5aIsMv7e9kAG2qBd2o20cuMnuUfpysSsigk9zzFp0DHNzXj4DrzyGemmZgni0A52qQi358ARRAG5iMmFLnNThl0o895IjUYNYBKDRCeVYrbaaTwWW'
        b'+bTePJ8a8HzybZe1ytrkzenDIo/2pNaktpTmjM9c3D/09O+o6i43eUpbeQZm2C+0l+nMJ5iYJupY3jZt2DewB8+yQzKjr9yQ8amnzydC/47K7myTUE58FQdqOmu6lvYl'
        b'9xcfn2EMSDEJp9yy43s5N2dh0C72ay60mnZ2ZNrhuUaW0xFBhb6xvurBSwjbXDs6+8qs9rlo86jTaZl/f8fzrx7Pv9Dv8PwLfVjQ3CGIAL0OCWNB86himK4r/FHQTAyb'
        b'QCL/fwJfxm3XeIybgYHsDFSBN8CHE+RYsC3LrpHamS2NwiTgH5PxjGso83s3R88G7tTYgqn+waQTZaHh7mzge6H24BmpFJDdmr7Hy9lAGzcRyAsl/Vrm91ehLRt4epk/'
        b'MNTqiAp4cZ9axgZuyEgEjSXvAjCzzM273JMNjJtvA96M9wFE1Vjtas8GPjFNCj6d3U1KL6+zi2cD322aDjrS/onXujK3XEE6GwjSpoGQgpukILfemRlsoKY6BWREfEvq'
        b'6fajKo4N7Kv2Bhn2lSTPNWlCIRvo+0Q0WLD8OUBVv4Eu5srHuILi4kzSIbW5Tf5sYK9sJtg9ERAtlttbdmlsYIM9H7wmdCctcoxTZLKBhcAR9M+JJXk6Xg0pYwNb1L5g'
        b'zdw6UqXF8csEbKCicBI498SHpO3abwNWsoHX6+cCsX0GKSgnMN5c0MePVwJDzC6i/Ar73m4BGxhYUA0Sp3QR5VfY1yEaNvAzFw/wxbxHSJ5+t33NBQ3XOIMTScmk62RR'
        b'oebX/+7xGMhy/pLBVfIYSOSzgSd9EsB7nm+Q0XRbnF7CBv61KRh8sYgsW2XllyWZQJMr/R3QKTHdTzmt2d72QsHLscIn9yW9vVY+pBX3P7Il8mDOQNYlJm3kZtbviqKd'
        b'NE2uq0qrLr3dE5KVtPnVA5//9Or+kJivMr8oD258PwlueydnfsoTR79YYtejW2IMeX43U/CNvdG+IfVgr93GExqXqZ+FFT399yp3r4C2V9Y3zEWPyZMznyts3WQb+nl3'
        b'hbY8fdptySe1exVTwvf5hFaGzTsmOmevvZ2Upv5gurjxwNKk4BdfuVhWr5ix7g8Nn9a8DNFTczO9Ul/4+9GST99r2fZ3XkDC20s/7atY9g+P303bYpwZfehYhdeftcGS'
        b'r1cvqxMuGrnCnKp97njqo6978xK0029e8ZqycMULV095RJ5KLfhH1IX9f/1Y9oX4guj3Pm/Yve5Rp5sSfPkrzfthl7879e2jW7/86IPAna+EJr4tWVl6+6WAL859een0'
        b'T8Wm89+94fx6ydu6uG/8vk1O/+c3r/z9HzbTzkZe2/rFXx0q/zgvOuOqlEtVZxnwHOxlgdMoalrtRXGTJ9xJFxDeLHg6VxaRhbbn4uUFHudkI0OTLo8uIGVx6KUo/G4k'
        b'E1MDeHoGbUHr4IDU7VcuIL9kjXGzrDGWP6ulxpUsNeWqukdLa+prNZSdz7esN8VmjVsDH4g9DY1tyc0ZNwQAi69rTS4hw54h3cUYjQ0KI4k+yr2D2+pA9/8Nqo6gVnWH'
        b'qlXTnWp0J9YBva69c/vc+936fC5wjBEpRmoIIHQ1zO1wbVV2zG1d2B1nFIcYhSEkWGzQttphj6vIoGr1wFn5dGjpdih5o6jVpiOum9M5uXtu74Se+UZfWb9rf/kZT6NP'
        b'slGYPOat5rRhVzdDZUdx99zOhUaPsF5Xo0dkr8roHmN0jWEjy1uru11blxhdJ+BnN3FrOP5xcTWktay85k3WxNRubW9az0qTd0yr4BNLiMk70iC4aYtbbCjuiOtQmYSS'
        b'YaFHp3d3XJcfbiv2Wz9ew+2xJGP98R1ak3CCtZ90nyd+I77L3ygMY98e77e8sdwkDLopGF+8daq4jnKc6n7lWb99n5ok+JCV/maSdQLcq24iFm10p5rcQofF7p123UFd'
        b'jnjMDAyG5iKxJfZ9t9DrjuKdhVsKO1Lfcwwg/vwt+dsKr0+IbM7vCDE6Bg6LfMdACNsRXpNapf151HBXVVxmTbuUUKlzyoIciBC6kI+F0JvgISVRitytF2ue+fdWB7Ao'
        b'OxaTExJAy1EwWixzBgCFHbX24yRyFRyCH5YyWh45DaHg+gDLSQetgIbwrEJsaAjfKsSWhgisQuwW87GMwE3kKGxIzhaEobVX2GodlGAao3UMARhh2I/YpFZWatU63Zc/'
        b'khYIrFpga4Ebq4BFlraccsDoh5hzc6gMQk28E23NGEhQbG+FgWwwBhJYYSCbMWhHkGpDMdC40IfZoecX0H2nUtiOzivgtijsDwJBaP8E1nJt4ndSnm4vSfD0tWWFF505'
        b'cY463Vd/nhQ2TyCY5JECX/a8/a5dnCQorPEJ3U+5rkPFB99yu3ZG9PkfPPziNv6TubK6dt2m3kHx3/vPTunP3xR159hboui/RMX2JTV++JcTL6d/7C86U/eCaE/UwFef'
        b'Z0V+9bTTkaFtf/y48Pm2pSfudIlWlOk+/qzOjXNS07zs4HnX7W9nTTr72947a2eXfPduwL++Z27M8Ezc+KrUnnJ299rGXHhgtjXfb1ouoXspWA7vXzJq/BvTxFqIcRPZ'
        b'yO0qdDJKPhe2jJqwcRIYdIxGFpcl5cKDOeS0AJsrusiBWxoybtNNOcNiWZQ8cW40q3Q6zImdOItuzySgMzmwBe5EO3OjA+EGuBPutAEOHhz0FHragxWCmmNhK05yYGYh'
        b'XozQ9igpfJYHXOy4jbX5VH2wMhzuhS2F6DLchXbIYB8PCGw53hPgM7clZITQ3hWwJQbLSPJseqYCGuBR4IaOcNF6dAz1sGWsg1fQUZxMLs2B59D5/GgGOKAWDjofWP0f'
        b'S0zr1llLTDalpXXqlaWlIy7m6SA3B9CFjEAkIjitsgG+/gabj0Tew2Lf9oLWgu5J74kjPxL57m8c9g04kNSZ1L3gWEm/W3/x+UcuFA2GzDT5phoyLGkTj6X0pBya+p44'
        b'9iNRoCWQPH7o6dcxv7vC6Bnfn3DBxuQ508AbloQbeLudhv2D8I/9cJAU/zgPB4biH8dhT1+DgxUPdBjhVtTqtJGkHbwKTWPTiG1Dva6R7H6NCHSNWrW6ccRRX3dX8fxg'
        b'5QbpmzL6Z6XgICKPVoOdf5Ak5IjWvzCb1NswzEzmNiDuQzBKyob3CaLBSYeksSIWY5nZfnRmK0ERGP+HmdYmKVPQx4zYlpqNl6TMCE+nrq0iJhlAwg6n7dRa1bLyStX0'
        b'EaFlPC0hTox5LVgHejNO5z+bT3vyV9cEl84vJZ0uZbRa0j93a6HVEacRO8448Ja5TPFpn2d9/uMy7UotQ/xz5bpYlVt8uuTZkv+4XJtSlqB+rlShVQ8nnp767NTxpY5q'
        b'SIlGk5zfYHcC8HL1vxCkxy0i4/cBuAWanadOcXUTcMC/HGcMVOx9Qwi7X65pH9WwnrPnVvuAvCzOpbdOSRnKWx1Q/0TM4upirBgcXIfOSzlWU4owkFFFp0Zntf8z4m6h'
        b'zTHBlOOQrSYCnWtsgZdfR8aBnM4ck2f4oDDcat7z6RDcbzJTBavVWYZ1xCHaHzfmrrb9B5Xtw2EcSkm78Gp+0CGaK+Vpid2mdjlxmoizhtapgPxJnfD0LCUnMDBHtS8t'
        b'ZY9cYr9jaelyvarWHONSWlql0eoaazV16rr60lLKaTDz0tY3qLWNTZSjaR8lTi1xllmaMuJeivtL1aipKFU1Nmo15fpGtQ7n50ROdqh0ugp1bW1pqZSHZwkbYH3Q4+7W'
        b'3MxRDveIxSEYSEcQ4d+eBDfswUwmgxmOn/Qj18XJ7yYgzgTgGWgMTDZ5pDRnXhP5Gv0STKLE5oxrOFQyxeQ5tTnrmru/MWCyyT2pefZ1J/fvOVyniFtc4OzxA/HR0aNn'
        b'7spRxxO6vGwp3JyZEy0XAPuleHHNRk+OoVMH8++tr/G4TXcdiyAVHC3PGyzEEwW7Lvi/0PzrRH5jOYkc8/OY/wpusoBiz3CCPDGGsxzIE2IEx2dR6Cha5NNTuBhXKmwU'
        b'tskcjDzJsx1+tqfPtvTZAT870mc7+uyEn53psz19dsHPQvrsQJ9d8bMbfXakzyL8LKbPTvTZHT970GdnXEN7zBQ8Sb20Lndbq+DhUK9khrbAEeNn7zEoV0jz8fEBi4UK'
        b'X5wTV+s6pqdcFH7JHEUEfpsYW3MV/ve0242+H4DrEUjrIaLPEvwcRJ/FY3PD/23wf9tELnZ5ignJXIVUSerGHnok/eusdEm0UwTfU447zTcE5xtK8/VQhGk9q3mY2UZi'
        b'XF5BFziNNx771S725kf2hLI92XHTYLF7hEfm0v1mSkGFjRUlOVs43pOE4dqOPbGMma8dZr9cXFNm9HAm6RuM3TFdOJuZss0YZG8bMAa3K23HsF+bVFvKlMeFWm/OqpIx'
        b'r7PPrtM0alS1mtXk2HWNWqIyN1SDEYuqroKc205pUGlVyySkwSmSWRqcSkuTZqelFkjqtRKVJD66Ud9Qq8Yv0Yiqeu0ySX2VPVFWqNn0ESSxTJKWnS4lr0SkpqcXKguK'
        b'SwuU+WmzinBEakFuaXphxiypnL5WjLOpxewFv7pSU1srKVdLKurrVmDGpK4kx8NJMRX1Wsy/G+rrKjV11fQtWiOVvrF+GWFPqtraJrkktY4N1ugkdEMWv4/rJ1mB21yJ'
        b'gYPc0jwykim0XOKzHGa3dEdNfW2lWjua2Ax+2PTmB9xGRWF0QtykSZLUvDlZqZJ46T250DqyOUki6hvIuXdVrfRuprg65hyx7/41uN97FizCvmt5+uXvs5iCfZv1/4J3'
        b'x3DKUVl1dEV3LNCTfcoyRT3ZppE1+snJ4ezc+ag5l54fD4QHefBS8aNUE/rTjB3AjwFe3SGrC6TONkBPiHYBL59u08xBzUR2ikFbsK9QwWagzIInswryUZdHfnY+A+BW'
        b'dNAOPV8vpdkVZ5HjwEAYK2uUXVPXAz2Zn0EqdIaYw0XlkpNAeXOz7spNaJcU9gFFSkiqDWp/wos17F7B7gBfT1rj+FbIbFZju3ECj+6qNcQ+VttaJwR6OQ6EF1BPjHXO'
        b'qDkvB23DFY0pykJbtXBTngBkoiMCXP7mtewxsD64DbXolmOcsBCeQDtx/aehZzTb//gS0BGMENCwa23RbwtQrPCZqc9nP5N45NjWRwvXgNRem8d7ii4lL3+W99WRL51u'
        b'ctdw/hHje37FHy5cN+1YWbXig+9y/8ktOF/2fkbssfknAuShH+Vc/361y+FdX7ym/Sj47WM+/t++tH7jOwVhX7+cEjBpnfHFUwUrD6x/evbJV7yf2bLhwmd/iKv7Q+6r'
        b'ydO3BH/Jz/59mG3BRu+fSv7a8nTa0QuVm4xvFXylKcwLvDkn22PpwJVjt0M++r/ob51vfTow9Nar+y7GfePzxY2PX0744Z1dfY7eL/bveHvZoytOp/2lcX/svPOT+uuQ'
        b'b4P+jWXHNkrOJ0SlvtGTYfjtUZuqP/UceWqpywtiP6cZr/zDNHw0tvf24LsHwy5/NO/YlHeWLzO6/t9QjK0+8bUnvpG6sXaPA7Av3gH3szRfHx2JtsZwgDt6AXbDp3i2'
        b'FblUdobbHiu+x6gSnUOXOehUOjxPM0GGYHg6V56TL8uG29FOMlhc4KNxhed4dWUCKpnPmUeO5O7Lvmtm5Jh6m4BTdA6+NDMX7cjKRzvgDsvL7vAI2og2cdGF8nm0EuiA'
        b'h2zMsRXghcf5ODEb2RV5m1CNbHINphmcQxQi9wew+cXk4kbtYK0xM+FhGTxjQ5QAqOU2uSYhaA1cn1sYTe4b2IpJymEuWg+3cXD6djmNzw7RwRacuh2eYqvFR3sZ9CK6'
        b'jC5QtfYE7myiEdjqg47j17moi4E7stF+eggOHobt08jbAPawE5SPXuQwi1AXexDnIDqBemALbIZn71U4LEcv3iYnUuAej1SiU9gupdc9sJ2L84pE53F2UXCAjzajZniC'
        b'lpeOI/eQ2uxAz6MLeQyuzgEGGtDO6VQXU5cXiCPlaF1cPqnp8wzsguuSaSvhWbShDrb4ohfQznxi3UpMX52ruSnOWqr4cF4CL+CG9M4rxPCOYjvndNzw9lSWgDrhabQN'
        b'N2TrIjwwuMcLorN4wBn2cjNgr0Tq8t/U25MDCKN6DmttBwbnGrzqYsgsNMMKuSWESh+lDCt9lNgBr+DuRJNnhIH3kafvhz4h3SUmn8RBceI1kQdR6Hdo26Z/6hMyGJpm'
        b'8kkfFKd/JPLp1HVP7lrTu9wUGPshiZli8pk6KJ467OFj4F4TESW4sjexO29IFGcUxV339O1IbV3Z/kTrE0OeEUbPiOHAkKHAWGNgbL+4X3XG80LIheUvhJsC0zp510Mi'
        b'Ou06eB0Vw56+7atbV7etMfCGPf2GPMONnuG9vN6KIc94o2c8LTPF5DNlUDzlI5HHsI//AWmntCuqNX3Y3bu9tLW0u3jIPdLoHtmrH4rJxP+GfQIPRHdG9/JMPtGGdIvC'
        b'xS8Q/9hZnszKmLBIA+89YfCwn4RGmn8kISTymiR8WOx7TRzYzTOJQ8mvrUksJb8Ckzj8lh0/yI0ku+EIgkINvD1OVnKcKyvHbSfODuLcT+759wrue0efjHSZlTLHSvF9'
        b'iDiHsRNI5EFihvXTOvDjY1genPEjwA7ZN5/xsEqdw4JEcM5hxq9T6tSwSh1+KcF4D1Au3CVWiy5nwV39RkfxgUf2PkJ79U5o8Sg2JCgC4y4LjIjQqlWV0fV1tU1SOS6O'
        b'W1lf8auqW8VWl1darql4kCqkFzuLxlRw4d6FbAVDSAUxEv3Z+v2qilVb+pFAyJ+rWQkO1PaRJ1qjqJ+Hnf95xYj+SNuA/T9XKdWY7lqydwlbObk1xv219Yv9mfoVccaH'
        b'WXReHMwtVayehs7Jn6t/JZlOzqP171wy5B/zrn+MVRf/HK7+3zVB+yIwM5Ofq331+NonvOvPmnneifklyP5/0YJqqxYs+zctWDq+BXHv+sexLYj+99LFf0rkLFugdf25'
        b'ai4jc+88sMy92GIquuI6WSvpJWaik9TSa8oeWLf/v6rUailndbl9OhFjdRLNPdxLp1Yvo1enYVmZSrf25Po0s0iuwCIybuUsvbZeMkfVtExd16iTpOJWye0jcFNxg3HC'
        b'FZPk8fJY6VjZbtQG0mrLr1jKsLdv7IAXM6IKYEcUgVG8mQx8FnbA3ZqvRWd5uhScoD2vnFXmEjXurue8vNK8NnTEqdd9tbB/61nVVsE7zyUIEhbGPxX7meQ4Ku+y51an'
        b'AIfHBF+/eFzKo3DPEfbBF4qXEWg6Fq5NjblNNn1hxwz45DhAXoyOuFM8DntQG3tTRC86gaFjS16sTc7dS7284SGK91eiPagzl8Lq4FWcEiZmJjz+QDWyDdEXqxtUIy6W'
        b'BdEcQMEb2aAhm1U15Phm+7TWaUZRxHCIdCgk0RiS2F98fuGZhVd5r9r+xva1xsGQxMGQYkPG7nwCqta2rh0UhvwqBfPrxCHWRQ3WCuYlDg+5ib6BnTgEBP0Cq25ifcdg'
        b'Sv/fWHVvwpQ+316hbmS1UvraRs0yVaN5kdTrzEocevtgo1ZVp1NZ3SJY3mRP3kmhurqUsnwchl/FP6pqtbbsHtXF+M0Is13tv5ZSpcScU4llzqcTA4CeWCjAp7Cgt53q'
        b'JdKX/ZxmwlotAY/CNs3GVaFcHbFTfqS1lN618OX3cHfIO1eFsJtX2Rkfvy5VrrANjp/RYVxqz02fMJmbnljMixC056sdVfaqt9f/9nBCw1EuuPSq7becQCmHtQLfDNvg'
        b'S0QexnLpYSuZmMjDOGjdbYJl4QksIG8ZJ5qhYytYSY8VzWAvNPzMQRorkyOdurHUMh4U6Ix4WybCuCg6JSaap8QaMiWMouBrvmHdjSZfmSHjmqdPR2JbU3d82+MfBkQM'
        b'SmebAjIHvTIp1H9fGGxtI85Ohh0PmBEPMA5/hziD2FnNWBmHL8cTw4sYh3v9R9clPCQodB7bMz+3Qj1JgBi5HIospEP+se/6x1otor90LsgxByMXFmrJZQhjzNpHrThq'
        b'wV3Tkj2AmtMSxfldk9r/rlE7Wb6+vjup67Waak2dqhFXXlP5IFBQp15pXpri5HHSu9roCk0lq7Gk7bYcssEZySVF6uV6jdbcLZXYV9EoqVSXaxp1VAFLWATOUVe/zAJr'
        b'NXiFV9Xq6ukLbFZsT1aptbq76ll9BVtielo2xgqa5XryPoZjEQQXSLSWUnHe2Y0qghTs/825FNsCPVku0JGVVbkFeBKzdwQWRM/NkqOT6Tn5xMh9S0wRas6bm8UtksK+'
        b'bElJuVb7uKbEDqRVuyyzX6InYzsDthIlkZVuU56DLjlaXicqkz1KvILuYZaj52znw4PoKboJBvegLvQ0GnBkUC+uKeoFcD88BTfSKwhF8Fn0tM5ZPy+LGIgoUbNsHmom'
        b'xcC+4izZIhEpalt2HtrKYC53WLoKPh2CjhZzANoDzzvOSUZH6WWZHvVC64o1jOY3Z370PBsw5wkBfMkTHvZZpjk+9B2j20XI9eK8gYp9GDLsFr+MuSMnJHadYHfBp1Vl'
        b'zVVPbhEk7I1PW9C37Tg/KC/1RMcdcvBLYbvRbVDQ/WXtguK4npFd0ObcZlGdg8K2TT7Hc9eSN7NVZe1a1V73l1ukHm86mhzOr/f9P4FH5cDNOxuTN7l+4ZJ3a86SN33g'
        b'ts/Ku9/RDau+C3pzZoDNtva3r3YKwGO+Ho3Hfy+1ozqrFVy0CXN+i87JoY7TBI+jLtibcZtcp4r2wyNovUMkOZZNuKyFGQfCAR7sDEKn4QYFC0XOYJS0w3zjDdoOz1EF'
        b'4zLYRa1ucLd31uda6dgchVwMXdrc4bP+rPryoBPcN0YHugDuZ1k+PBLOmiTt0IvJDaajQOcEPAe7OFWsgnQ3ejptjHJSho7SI20r0ABVFD7h70hVc2a13ER0CBrQZgWN'
        b'q4fPy4hqzqyXS8DN6kKG1H933GjdPevH3alfqqkcu36MiaLrx1Hz+lHmCMSerTMIWFrTvubDgMjBqHmmgPmDXvNH9UyGdHJQSdEfcl52RjbkO8PoO4MuLOlXK4zSbFNA'
        b'zqBXzrDIA2fiG3gguTN5yDfG6BvTzxvynWj0nUiTFpgCCge9CsdkKe0NHvKVG33lNMXMqwnG0aXKrKoiP3vsrE0j2QVrlAE/eNWilpFjlq1PiPMH7GyxLFvkTEWhI8P4'
        b'EctIv4e1GmgXhINjDvH/kcEPrxRz3J9btHqIWNUPLGJVHJW377LlnxP6/kPFhpTWTv+zqqDDY2s35b58PF2Zfu+W3X3qKeWO8JZp1VUjAp2muk5dOWKHVxi9VotFqgqe'
        b'Ve0cLU0gphnT7SybvnSdtR3d+meUTvSSJY7SOdHRvOryiq22duv4AWPWVCV/zPrKS+XTVXdcqDWUVpFd7LsLL3tpNwuL6ZpnLUfeXWJJI9kVz5J29Ajr3b1D2gVsKpoE'
        b'dx8JUxEpWi5JV9URcVRljitfitdiugiTbWO8TioKkybFxtENY7LZW0k0BFhSHc1+tGdTJLNrVdWSlTVq8/YzrjCp890Ulkpasq+rx01J0apxRep0KZLUe+WBMnN15P9O'
        b'3LUv0BPcjl7MhIfHLtOo2bwaKLNwUBFedsmay8S7YVjeJkPn0EAuGsgBoeiwM9qLV4qX9FMB2aHCIkFfrjw6MgfzeOtMCvJsLNln5Sgj6MWHeQVYkEBH/B1RLzrswx6F'
        b'cckGBrAgybGsLLIjJgjoJwFyMdUxZMDvHqi4355pdE6+wlowaVHYoSvT0QCLP87DF+JRC07jN0ORRTelssnqHkVWfOsN0yxZTp48OzpSAFCL1HE53NOkJzcloItoD3cM'
        b'/pjmTdpDio7AywjamSuTRufwwWp0zA5unwL7pVz2auxN6ElcBCmZC3jT4VPwKAOP4/XRQKMVuBv3RbEZ5BPb2c7lsIPzmC88y976fckZbonKyTd3JANE4dPRBi7GNAfR'
        b'GU3R5GKO7jhOtiizdeCP5G4775fX2SV2N1LRKiEvscO42xXmqHlfVfzmUOH29czFrZJJB5dVpJ3drtwStMnpFZeq5/dylG/ZzX9rw+G90Zu8F15WJj+5dF7I+7KZzy0O'
        b'+vBoXs2pT8Cd9f4hNoqu3/KVv93UMw/0Ph3V7GuqP+rYcHlx0LbUSxeUZTdFuft9d0V5z5zOGfnNzt9tEu4oWzGtqmO/8G0/5w77r5f3wKvXOEB8OLB644sYaJBVwgPT'
        b'Ryu9WZyuwZxyJg4dT6ASn5KDTo2BGPC8ZBRloNP2Zewu1zm0Hw/KGKyCLqDnCAnCZvbWzfUp7rnZ+ZEYIHKALQaHLyRz4Hp/QLf7guilR7katGfMTiuVKl9CO6jKxBbD'
        b'yEts7jzeVBUDD8RMobWfxYmO4qMDaEshPZAsqOVMqEAv0HpNDEUD9OhNIXsnpwyPWQw8U8pFe9zhCQp/JuC2HyLantG644o/Tfb3JqdIHf+j/TjCj8dvxjkQzGFmHSMi'
        b'ayBiDqQQ5DpgIUi5E9HqJLUnfegTNhg+x+Qzd1A8lxzYn9o+tTvjWF5P3lDIZPyPRueafPIGxXlWm3UfWm3W4bc6p1A52CSS0YhMk0/WoDiLbNNVdVcMiSKNoshr/pG9'
        b'k0z+8YbZbHDNkCjGKIoZ9g8+sKhzUdcSw+xhkTdrodiVZxJF0IxmmnxSB8WpZFPMTzIcEDIUIDcGyE0BscNBkTdteFK3W4AXJKIbYvbAy699TeuawTHStgsLXv5MnK+J'
        b'8w34NZtgd/dBx26DmWHO34hDvuBwzLIP9g8Mc3KdGCaK7INFERE96mGxzgFBDDjtkPLrsY6UGDebx/7nEMVrY9XIQWQFxOsLXQ9HF0xrvbHUnlWjnybOZ8Sh1ptfEucY'
        b'oPvCZkWi9p8k7BxxTGQ4eMSqs49TgOs2W+qlJce4tZuIs5k4xKaMWNBX1leUlrKbi08Rh+xojnDLNRUP3NYcsbFsrVANItGWjDiN0VKwUPQuiP0bfcvcOm0zoPun/5NT'
        b'b673zFYrutlmcQiq0XWQ3fInwU0ex0n4nS1wdu9M6OH3VPSF9OkGAxMGfRJfSHide83Hv497Jv0ml3FOvp4weThl+o/cRKfQ7wF2bvFx4A0e9t2sZYDY75owfFg85Saf'
        b'I57WnHFTAES+14Rhw+IUHCKa2pyOQ8xpUkmadIYm8gy8JowcFmeQm3tnM82Z5lQxY1N5Sa4JE4bFs3CQVybTnIWDPAKuCeOGxek4yGMW0zz7bl6zSV5ZOK8fbG2dQr8T'
        b'06Z18zqijE5hP3DsnKKIYWv4DeK7KQb+odeEsYPx6WxW/jirfLY3RD3B+IUfOe5OkhsAO+a3sO+mzNK2TNK2bIY2zhw0lwQpcBCbS3CPri/xjO1gWPJvio1OOT9yApxC'
        b'fgDYIdnlMjfI883plqpPJlVPbslkDW6pWPs0Wu+oyytAO/Di1BZD12v71Ry0QwgPjbsTnfzdiseMd7rbeKNbBVfLV/C0gljMqxR8rS3+b6cQaO0VNlos9GsdvcFCPjUO'
        b'tTUb5TLUMFSosEvmKOIw3nZQChO5Cvt7jEGdFjuPGtM6JXO0LvTZGT+70GchfRbiZ1f6TExanRe7mQ9g2VDDTRela6Ktws3aGHY0fxFJP1o3oUKUTA+f0XddE/kK8X3f'
        b'Ei92Jga5d01WyTc8EjkKD2qS64FbwpjNcz0VXj5A60VMcbXexPhW62NO60vjfRV+OMyPGNtq/YlxrTZAKcBvB9LYQCXAfgn1SxRBODaIhkygIROI6aw22JxfCA0LUYTi'
        b'sFBzWBgNCzM/hdOncPNTBH2KMD9J6ZOU5h5J/ZHUH0X9UdQvo36Z0g77o6k/WmmL/XLqlyvi6cE3cnAvxnxwL0YRq42t5ttVSRNGBKnLqOXum8Ryd7U94ctsCGu8y35U'
        b'CAsf5PsI1VoVkTpYEaKiadTGVIuloFQtTrhM3aipkBCLeBW7wVDBSjQ4gAgt+F1WwVjbJKmvY8USi1gh5YwISleoavXqEbtSSwkj3FnKooI7U2saGxtSYmJWrlwpV1eU'
        b'y9V6bX2DCv/EEMt6XQx5rlqFxa27vuhKlaa2Sb5qWS250yw9b84IN0s5e4SbnVE0ws2Zs3CEm1s0f4SrzFwwu48zwmcLtrWUO0b/O2quOZ0YthOJlBNhjqrEKOn+yyO7'
        b'waMc/QiUgklZidO7E1BaxB2f3kKzozk7YyzOt8QqOEpONJa17n5iimialYzluY5RcJUMkU5UIbgERsFT8Gn5TJG1YbUlN+5orQSkCMtTNOYm0Tgg2onkWMjH+diwfrIt'
        b'e7c0JagdldxxaxzAuL9R6RvUjh7SrLbFgMFu9bfjbKjN5DbehJoOCissq9g0NMRKxcyOVgq1WlYURifGx022ps5KLFNnVxHZVqJrUFdoqjTqShmVeDWNRB7GuNViHU1z'
        b'tmgzWMofPa5B30ghjyllleoqFV7zRym0DAvZmooakpuGbRembXO+mHbl9l+Swb7jrqmjm8x3axceqgsfYeQjTOyXBDN/+RP+u8OVx8YWSG1GhPcWQ7ZRVbUNNaoR+3mk'
        b'prO02nrtCF/XUKtp1NricRnh6xvwLNPaMeSGKxaQigjmEjPj0QIZE6trKCkKGnFhx2HUuO4jAhfaAXsDvxgvxsOBwUOBicbAREMWAemr2qZ1p5pEob0LhqKnGaOnDUXP'
        b'MEbPoIh66oVVxlF87uXbMavL3sAfFnl0hLZNHRZ7dyi6U/u4vbNO5/blXuCaZFMvFBllM00RqcaQVKN/mlGc1jrrOk6mbC0wzLoWENqt7qrD8NthOEh6LKAnwBQUZ+Dt'
        b'cf71x8NqKG6l3fYg6y1LZ1iMt74fY+yzaO8iqx0ma9qkFNTUoJaUYUqpwMiwVp7B/paVybXH/5Ma9zHs4D4AZIcQYDemliV72SN0d3ypidn958eY6nAs1Sn4mer8HPcq'
        b'4o2Pi7QYm0i5lCJHbFW6UnoAYsRWvaqhvk5d98ATeqRRfyd06MM2qvLA0s6lQwFxxoA4U0DCUMBUI/7nz57Zu1NBzcL0y8rVWjIM5v6XNNSqKohNiqpRUqtW6Rol8VK5'
        b'RKlT05lertfUNkZr6vB4afEoVmK5C09cVeVSPU5IEozNZWx3jS4M9L4r29FPiIHRT4jZj540Z8ZsDf4XLgtUEaM4e2UDES1YPqpeVVGjqqtWS7Q0qFxF9jrrWYMWnEol'
        b'adDWr9AQ45XyJhJoT8xbGtR4hU7HQ6DFjUxT1T1KN/x0jfVY0KFcsu6+HNHMDS1FltIiy0i/6ikHZPkrYbyjG324X8kZE3u66mOgUFN/Fw3IJDoNZv3m10gyYlNkfTLF'
        b'UmfziynkS4gpZWYAUkbWDCvdZXl9PflokqTKWgmqp11VeU83Ud6+Uq3F03gFRgyqcmLcZFaH/puz/M4F9EQDugjX50VFZ2XLiJYpdz5RHKIdWWgbPOmUW6iMyJFl46V7'
        b'mZstupIKO/TkyD86hDah87AF9aPn5kbkRMvJXmFUAXwOHSyKRkc5IDGTH4N6qh1gF6v561kAW3T2hfL8HLRnpcANuMB2rhxuhIf0Mhw9t6Gc6BMLYy0axYiC6Mjc6CJL'
        b'zrl8UCm0hRfRXvgU+9W+i4mrdOxNxueggZivw50M6ocvPU6/MKiYkquA29FFPdqtRNvRHiVRJxYy6FyI52x2K/QS7BDqcG3gS5l8wIUdDFyHutAuvYREHoc70GZdFqto'
        b'zIWneMAVVzcdd8gJtBEd0dP7+rpQGzqqw51Tg/qycQXWMugkqXyxRuCzj68jjKLzd9Vr5+bncuOE+2rPBl577mSRMGP3I7zH/twXIBbXl/wQ//rVDeE93xdrb16PuflT'
        b'Sl+XJGRFTPZHlzp//OhrxS2nFRs4u95pfqtZfrVg7lHH3x3MMQ5u1h+dtP/tR7/aVpXaLz34bAnn/5p2fDusXl1Zaet23PX38beWuSVHNqyAK5Jyjxli1V92KgdfHQj+'
        b'l8MU9Lef9L/7y6LmlVMLOwv2jvRNvLCLV1JZNPE3N/1KDjwx4P2N/4tvTMr99vz3pzsuh21p71ysLJvzzxv8G29/mff5ezey39+XmXsp5YPn1v2L3/3HNvsC7T6ti+Jv'
        b'pXfuTK/74NFh0Q/Sm2Hf2D12p235V21OFzNnP//1mc//6fTjndhjM/z9excNhuUGzvggKkq9zkXqSvdEF2Wgl+hl1ajFDw7YAF40A0/CLWgdezphT1Fa1FL4VDTairbE'
        b'ZKHtXOA4mysIRuvZqxJPecMXYEsM+a7eZrSdAbwYBg54wVb2LrljaB8nKic/D7XB0zguiIH7JsNT9DrZVfCcimhBY9CVfBsg4HFsfeF6qh+VYjrankurBDfDzfg9TwYe'
        b'9LVhT4FcRs/xrNSwGQ1We73oNDr8CK22HHVlRskX5EsjI8xfzXRBZ7lN8KnptGJr0QvoRaLjnITOWe64exY9zapnr/ihPjZ31F6NYwsY2N+AI4l6VqwUEg1ptkwOt8RE'
        b'L0Wbs6iiVCLhoeeToIHaxeXA7ppcy7zNLYTbY8isnY4uCEAkusRHG7IXsMcpNjw+OTemnr0onJArAxwqOagLdk6j2ly0AT4DO3MLoxnAWcHAF1B3KtoVzXa7YbI2V4Ze'
        b'RJusr8xYC/ewH1/qypyRm5+bmy9HW2S5cHshriM6F84HkXAHH55eZUvbmbBiCmopgCdlcD26LAC8DAZehq3waanwv65QIs6YG5RGVcDuLCMtHcv7R/zMiOm+sVQrnMYe'
        b'1LhRLASunu0OrQ6DfhPfE04a9vBvr2+t7644VtNTY/KIGfJINHokmjwmGbjDQo92x1bHQf/4/vT3hEnXPLw7gttqcLinT/uq1lXdDiZPmfmwR9hg+AyTz8xB8cxhv5Ah'
        b'v2ijX3RvZf/kvmUXHjH5ZQ355Rv98k1+hQa74eDwY8k9yYemGLjvCSXDXr5DXpFGr0iMT70DDIJhHz+DzbCf5EBeZ16vxwd+sYYMDHu7c42BsRj1+k7oTuy16Zlm8o3D'
        b'4Z5+7U2tTd1eJs/I3kqTZ/xwUGiHYDgssiOitdByY0bSB2LZTSfgH3fDGYj9u7lDknijJN4kih+WxhvS3xOHkVMbs69JQrqVxx7peeTQ4g8k8YasYc/A9z3lw35BHYU4'
        b'072CmzYgKOGGLfAKMFifxXDQLgW/RtHM3pxx7zkLMjxa8tWCnyzb6OSCocdcGMaVXJzxMPd5a8kH7jCmI7LHGNvI0e1CakrFH/2OIJ/eDgqs7gflFAv+u/aRqnkEL6Wz'
        b'gMF8eJcF7gTw4fWeYIRRbGyGTQRD6cxSob1l5/QenHUPqpLcF1XJqWLlnjdVBHWMATkWjFJPwBDZBm4icMy+QlVRw5pKLVMvq9c20V3oKr2WxTU69nvR44TisajfyhK+'
        b'UaWtxhKqJeWYfd+60Y1fdj5b9n0tQJDAObXOWgv0C+y26D7sLS8ncmF6RGzVn4OqM4vZM6KvaPxAEgms+1vwUb2KDZwV9zxYhUdrMKpgeYcybRr9gMxEtLlI5+TEAWu9'
        b'GLSDfJfmPGrRk6+elcL1C6yYN0Vcli1mCwYpJhZU89FmDECa6YaxbNQiC68FqwOEKfDoWk2RspGnI9s4qwf4+tYz9jBW+GTMmaF5LbMctr476+XfHNm4caM7rzQof2ZD'
        b'5B9q5pdezRz88XufcpvT0t1Pf9j+7Yy/FHxikxjJfH3t4rfciV9lZRfs9ly39239uZ75/GdqZj4V+d1FX1XZn//150WPFsUd2z5ny8dzqxqHFiz9+lik6oWBPxW9rTy7'
        b'RrE2c9rLS7/6cc5T3qc9guMdT6jKOzs/7l/6Z11JfeVPu493r9n1Y9nlaXpu5kjJZXBBfnHK/u3uQd9/smKtZ7tyxuZzH0d3Du8YPPL57h1y6T9z06pmPXr1g7LDbzSl'
        b'/cRr7G//vUzwaOzun6Zcu3rje/57+oir35ZJnenKVbgCniFGVnlwneUQpxcysCtXuyRkRkiuFZ5zmcetlcAD9CAjuoBx6Gnc/3AAHblnAbWsnuhZeIguYG6oG+0232DL'
        b'Ra30ElvyOWqKE1bDPbAnN/8x2dhl0LIGwhNh7D1Qz8HW4NzseXyZ5a5baRndDJWhZ+CpqMJ8uHO65X5nB3iWg45Ph2cohPDJmEluuoVPou4Yy1W3cMCW/bDs+jB0EkMI'
        b'ZhqFHhRBeJkX5wwpumwFIVj8sBqdoRACbYQ9twkKx3DKYEflAGIwfGpi4Rg8wUFn4VamNMYWHkbPCmiXw93VSoLYpfAcg4sULOUEJGCMRjfr+9bKHXLhi+XjdpSd0Rba'
        b'WFvYC48q1FGyfLQtin6rEeMl2MbVBqHTUruHW+vtgNUlU2arfbNkNeJsXtbNz3QhDzMv5JWuwC/kwPTO6SbfKHLLtW9H44G1nWtNItmwb6Ahd9jLb8gryugVhddWj4D2'
        b'2tbatjoD9yNPv9GI3orTNX01x5eavJKG/QIP5HbmduX3ppr8ovuDz0ecibhQNBBN1uLszuyu3N6QocgpRvzPb8qFCpNf6rDYa0gsN4rl74ljcYYH7DupjsmTHCLonmUS'
        b'Sc2nBHpnmTzjqCHagsFFpUOLaoz4n7TGFKAZ9NLgJbY35HR0X7QxJMnol2SYRRqhN5GPqgR26zG6sLxYYZRWmAIqB70qySsRPYVGvwSc2sv/gHOnc3fjsdU9q/unmbxS'
        b'Dfxrnv4d6u4FJk/5oFBufX8wq5Oj6rhfcAEge3fwmBsAi8mr5MLTCI6VeXa+K8P4ffeQdm7aP4IHXXLUAR6s+lHe99wTVTt7ERX3XYU1TikYn3JU0SwgWi0F5+HS41Wc'
        b'W3CHE6q5wwuVx1dJebQzRxxL6+pLzWoa3QhXVa6jaqbxKqURYemo5ZR5p8HTovO8JyKH9DA5kbMOXDeTVMZQyERjyESTaCIm7sPB3ZXHlvYsPRRj9I0bFMdd9w06nN7L'
        b'O23fZ3+o0OibMChmT6KN2UcYvZOcaLWmc/YAVkNfzJ1o7lSL7l/1BNHhP2AA7hNKdhZUCx80PKO5+tFc+eNT3D/Xu3sLhbJFo7sICkbJmco4kx2J+75F47j3rz2N4yXY'
        b'3N3FwOlsx6erw+FUZ8gvWO0xCsmWaXR4iCpqKPhZzU2RhK+2CafaqvARJlzKZ6lBpFnWUKup0DSWshxLp6mvozNnxK64qYHVm7P0wR4YGuFT5Ddiy25a4cixpriS0XND'
        b'I86lDVpibqAuZV9xtxDPmOC5hHSIuQDmkMQIRd09b0gkM2KeiOWFx1sf7xWf9u/zN3lOwmQ05JuA/w2HSI/l9+T3h5yPPhNtCpnZOetPE6J+FzP5gviK/yX/1/jvOL/p'
        b'fIPLRC9gbgEmeCFzAzD+C5nrfkGEYWIm5OlncByvDB/VV83BznQMsxVMMTPh34z16Mjeh47YkU3gU3U0r2C1Ldv8iPDVvHAZHgxOuFRLruOQclhON3oSTHL3ID/uKC29'
        b't9Cy1cAGLOaYVbx/XQ+uxcT3J55POZNy6omrvFedXnYa9CwYFBaMb+DoUSQyT0nzHoZnJXLMPIXcW37HhvATSaiOrf94xmFDrvAiFXcerTh9LuWMqqbJRxwyjuX05PTz'
        b'zjudcRoMnm70nD4onM7W+77nw2YDM6dlxlWPbOExFrZQx9y/DUomhWPeHeAUjDD/j7nvAIjqysJ+bxpDFSnSYWjK0KsFRaUJSFMG7AoIiCgCzoBYY42iWLCDDdREwYpi'
        b'N5bcm92UdXcZJwlIkl2TzSbZbHYXExN33c3mv+e+N40iGrP//1vevPveffee28+95zvnjGkRKKGCuN7NNwIoKXONwBdFkptbCrYULHUlgeBcEuU7b64gusU5sTVC4ziC'
        b'LKqcDYOmRLWDvN1a/r8tkb+uRE8FY2KUZQOVpci4LCQ4r++yRBImQ1+WHM6Y8zPKcpHhJ2kq+swW9JqkR/U3cfY9+UUnM0wMq/vaCfao/dVCX0/he59+c+TeUjEL14lF'
        b'+jrroZumn9BI/RUtNqo/CC6ATp3K9DGBuXk2zmiY0Rx1fnTLaLXb8CdkHopjOz19T7oddWv1vRp8IVjtOZ7MVPbx7MOB6lknagIN6L3MNDZ6GsME6MpAWaZntHuZcbtD'
        b'sELAn2yQdnfxuO/g127t97/tqxt4rgRG39gBu2qx8bCDIERRLmZ5UNz/jM4z+plOMHbgMVVsXLcQrAZCl+gI7XMaBsQcrDMDrzI6NQmjqaqv9QIEOUbrBfdghYA39A5d'
        b'1MGll8nJvmuylCfwZeoyiKHQDjInTJP1JezUpkD7MfSLgBahflamLIrR0LRljYemtuxkxckvLDRacWj4FZjcwrmS9zFTc/sgMurgQJPuRE7OPjpb4xDRbh3Ru2Z0TTeU'
        b'eVYfM2g2TjlTufVZPQiWeY52g2WePlgPxFOkIkO1knauJBu1gebhX6TVzJ671YppqwUpa1+gpVRVc415AwhvhCGzvc+xrat3P77e/QeueWqSpG6geucoMah3+gA82VK3'
        b'j6TendzqxWDBCHa3Qe3WQc+oeTCA8sxtioRzrK6lsd/aF79A7QNMoMsqo7wyhfDxRWB4oajQYOyI+2qRPrl10i6LqkqN2oWGt0NlADq35/L2sYu83U7+Px9C8zjwyeGB'
        b'mpIj3qAp6YM90Kt2P3vFODFQu3kyLzeazJ/Z2ubP3drcyhnCjbXnb1nz3NxKZVVRYckSUkE2ugrSPdsv4BEsvRgYV1mHa4jaNaRV3KrSuI4meycXj8bohuhmsdolqN0u'
        b'6KGrDFaSZnu1a3Bd4gMXzyZfullzGdFuN+L/ZY0LnlnjgueucY6vDnnhKrcgbHVpebmSq3NbXZ3rHzbCsBqo0is1rmP0lW6vdglutwvWVrovifP/VaVLnlnpkheq9C7W'
        b'90Xr3ISaojaewCB8EqaAE31OAbo9/9fauqEo0WxRr7rxe766mak7v8rpE9uVw+rL+fxxq8hvhTe0G6m7vo79+Hg0RuizYkQKtEu2hPRCUj1kyabcVqsxyyXR13qXuHp+'
        b'eWkRqKEuyi8pKywyPPHhgZG6NjDLzeXSJc0wWNcM2kfnoc+DlZdn9fmlGtfxdYkfk27tc9L/qH9zkcYFbBJ+PiyoufD8gpYF13w1w8aDd5nEB65eTVFwGK1xHQn3o84v'
        b'allERgzZUbmO7WZY+7HPsE0fxwzEffv305eNeqp2+9gfT05dTxQbdUoavgZzrjNfFWTRrGxc3rC8fmFz5PmYlhiNw6h261EvRfwI8S9DfEW5yoh4Gr4JI+pan7sb3YjK'
        b'MiBxpi5GP0SxurcDbREoKnKGcWd9Bvn5c43Jp+Hb0A1ddXV/qIDraQfLmyvPr2pZpXGIabeO+aU2bsChKTcOQGZJWaURmTT8poDXU6JkOtdHwiKwe3W79dD/e7SZ0iUr'
        b'nzMmarCIwZO3jDaVrmCjsWGGpp9jBF2/aGJ4nQAyb0aTr/PNGYP+oRAYI/YVQoWIY4iDDEgv6+fEtc+zekG2RDc/CweeIWm1iDNAbY556kUxriVlxbKK8moOJRsWysHj'
        b'qyoqysFa+FNBaHAXG0bmUQ9tr+ySLq7KL6ssWV7E9U/OuFCXCUmpuKRS1SUsWlrRYy3TGxiSGeDMofopBUbVzz9524CB6LR1rp+8ezTFkqdonCe22018MASssRY0Jx1d'
        b'pHaP1AyJqhPyrDq/B45vddM4juubZSf9AaDTFPHdQtlvZyhIWF+6gUqW5ShVlZZXgjMGNwhb9UA7WRXNm1dUUFmyhHNbShik0nxVZS6H3+gS5VYpS5XTIUuwTmugZagb'
        b'5V1SncjKnAIuOGArh8Khkj7oRdxiNg8uYC5QWQ6XSrgAPkK5Ai6r4bIeLpvgAntz5U647INLA1xgs6Fsggs17NACl7NwaYPLFbjcgMstuNyFC4bLb+FCtRb/1w77eqku'
        b'8iJPE5a/gHaSahnL6S5KRJbW3WaMU2hNykMPn3YL1043j5qMTjdPcnHxqEnrtJ1ck9DpkkjuvIa1W3h8ZmnXkHjU+2hxu0vwdVu1ZcwTga1leDdDLqCPN7Ybgo/8GXu3'
        b'B9Z+nEagfSJbk8irIAZ02oWBCmIE1UCEJ2O6BeyQSewjsdAxC/QSzRgrh05LxycCX0v37xi4kGSd4OLQLSLBRxksue0iZBSoLb1AGzCkmyEXiOHNR4Nn40m0IY8EIstI'
        b'6oWjG+5+sDC1dPt+CGuZyX4rYS3HfSsRWPp/KxVYBvwgFVkGfGvBWsr1z76XspZ+30uElpHfmrEkqL0L/oFUWiREDvhBIrEc+YO1/mJiOfZ7G9Yy+nsJfxkLl2FwkT+R'
        b'iC0jHzPkovcGYolv+6vwVryN00uUOgqsLavQHZ9ecGn4893HLCC9eismUtNZwhxRpAg8yC2Q8v47RM6MQqyQ6Px3mJCwlIalBv48JDr/HZwKokTnv4Pz5yHR+e/g/HlI'
        b'dP47OH8eEp3/Ds6fB4StDPx5SKhKI4QdSNiRhjk/HU4k7EzDg2nYhYRdaZjzw+FGwu40zPnh8CBhGQ3b0bAnCXvRMOdPw5uEfWh4CA37kvBQGnag4WEk7EfDjjQsJ2F/'
        b'Gnai4QASDqRhZxoOIuFgGnah4RASDqVhVxoOI+FwGnaj4QgSjqRhdxqOIuHhNMwpOY7glRxHgpKjYhS5eimiQb1RMVrpUzyGLC4xXYPAQkq23pZaiZrM5fmTSMObaU2O'
        b'GbzlnYKQVwD1p3oFBfllsAjNLeKVwCpLKApOqx1AvVJo1cNAQYCDqxUVmvGQO2OlADhrNLDslgfLXD5nxaWwvKAKzpR0qZmVK7W4vZJKTgDMRdei4OJj07MT+K/yDHXU'
        b'Uubx2gr5srlULE0+40CEhlblArmktbTz6pCVyiIooFm+impWQsZU72AJ+Tq/tFRWBduS0mWwUBuZqDMzYpJg1QeA83dLhOBuHXgQ3f5Oyu3kYBRmS9PY/rmSmTq+o29k'
        b'gI5HESqYHGGpbo9HQyKjkNgoJDEKmRiFpEYhU6OQVqOZMQSAkufmRrEsjEKWRiErXUhIQoOM3lkbhQYbhWyMQrZGITujkL1RaIhRyMEo5GgUcjIKORuFXIxCrkYhN6OQ'
        b'u1HIQxcSkZBMF2JJyNMoppc2lCPISmJ6/dHWtS2TXMnv0RNzRFkpvWMqxNpeodNWlcDTHBEVj4gy5f18J+n5Xb4t/Y7Jmtg7NuANckRwjRCWiWama59Pi+x5mkF1ZTN1'
        b'uZgQOox0ZWdO1n+bI47i+7CMSV8CXqtkTLYp2VwIs3R1rv+TbdIrLxJ2AOSKkHLW0gzlr0k+T6O4iazXVPfsiY2KOSd0sbldgtzcp749v56fDypUeq0rqjMql3dZZIHC'
        b'9iJeCVTCAXQ5f2RCMBAnzq0qqlSCKXDOPkvXIM7psc4eFTWgwVnWoGYzqGUNam0DDGh0WfUwOGeSyyGlSYoVVUqyZS4iWVBG14TCpSrzuyS5i1TFNOuFYOtLnFvE/VDL'
        b'X5baz3Kpm0eT3IL5gCKm/vnyK6tUhNtWFgFWJ78UjOqXzSsnFNMKLZlXUkA1yQmDzU36utf5iyr1Beqyyy0tL8gv7WFpVUpyAqyzitBHJ2mSDP3l3DF2ueb2qHKyVSWT'
        b'MR9XTO4XqbrMCJHKShXowdP9QpcJaRdoE7LB1bYM1xImqqJKeCE344D5ME10SRZWExJUBgZZ+9gqcZwwTH16jQu9P8suhx5kav19/hH2TMDSkz3THxxc6iubYhuq24PH'
        b'3vcYSzUi5micc9vtcj92cAPkUVOBxsG/TgTYTNEeqc5dBPUI0TksANxF+OhcSsiMXEpovUYcNzXyLaH99fCmrj5lXoZuQPmH7l5UdZd/aPzjK4fvvbRR+R/wObHHShtH'
        b'S5iPH/x66sKBofAr52l76O5Ns/Hx5WJpY3vLT445OubE2J2pdQlw7jyuYVxzBGfGsNPDqym7YXmDqNPJrdGjwaPZrsMp+L5TcKd/0PnA04E3RO0eMfWij0HnQ2vNMLA9'
        b'KLt96kx10EyN+6x2x1kf27nUJzSLP7QLfjSI8Ql/ZM04ejX5nAw8Gtgq6XAYoXYY0W49ot1hhN4J6svoK/+J7V9f2bFnD9EqLtsIjYzj6i3Mj8mm+g1lC/Vm6gI587iV'
        b'5bydP9DjLCR8T8m8ZYTLMeBEXkKTmZ7RwNF9fyq/AtKn7YWMob+HocYuMkAJYVF5pd7oIPWW9hI+KJTnBqDHEehp1dFj7BGjNzngtu3nUUPPMNsGoMalj9ox9IbRgxze'
        b'F9vPp6diAHrcgR69aSd5Hw4wfmmS3hyAJE9jkj6KlXEe91RVc3mrJtRoA9DBqwLx/gueSS/VqOESoihh2IhUkM9gQ0HNrvfhESFYptA/m1dSBBnyuwCSOomgVxzSuweV'
        b'+fP15x9Ibksq6a/Wn4U/xbz6c84h/H++7wfl/QEq0Q8q8X1dJUb2tqbdT/+PjZsaG0IuiS9lpVT5ef/zHaUvwJi+MUYmVMGWddFcY2OqPemMz0pMCElIjMt+idFKCPzz'
        b'AHQGCw2tMsw6MIujN4v2JgN2j1dH01qQ6KGHFSxLoEa5Oa2x0ur8ZSrenKisrKg4H44if/4MSMj/YoBShBsPKX/tkNLqlBkUhOf2ZH6KKVNnvIR3EkLOlwNQFWU8Fw6j'
        b'i1p5+ULYOnNGVMmOuqKiHKwXEb67ijO7+lLd8qsBSBoJJNkJtCQNytZZl/n5WfO18ZcBsh4NWfuyRjPxIjLH5BcXGQyDivnLVKBvKJsUm5JB5qTSn0kUb5Tk6wGIGttH'
        b'E+mJKS0vNqZF5pealTjh5XrNXwcgKdaYJDqvF5UVBlWWB5EfPUMk80t8OVpI9XwzAC0JxrS49WlAWOaX/vMJ4fvt3wYgJMmYU9T7gvLkVFfJxqgMDKHwg5uzAT0pJ2vS'
        b'y82efx+ArInGw8mGzvJ0/8jbenmpzvtogNzTjVvHv+ecDbtR0ByCe7+4zMzUlIyk7MRpL7mifDsAVZOAKqGuTv7RkyrjvXOwbAKZBZOKCJ1llONX6U4u+/JDTKbtqSkT'
        b'ssG7cKAsaUp8oGxSVkp6bEZmdmygDMqWmjhdHki1cCZA55zPp9lfagmZ6WRsc8lNiE1PSZvO3Sty4gyD2VmxGYrY+OyUTBqX5EBPU6tLVKAJXVGaD04oOHPXL7PMfTdA'
        b'1U4xHgXB9904Jb6nXgYLHncUwQ2BfDph5KtIPb/M6PzHAHRNNx4Gw3s2OXeSEiyL1duhSsmYkEkaLyEjCVZB6Jwv1Sm7B6BwFlAo1y0+DtmU4+KOdUinKITeWP4zRyuP'
        b'O34yAAm5PdY/3gg6tc/GEVCkP6833M++zGLzeACi5hoPVjeuXrQTOxgfkIGQoY+FWAcyOMbqMNB9kKI7mrzQHyDFQO/Ekdc76Qug1Y+mlP5rMHfY39dlbLbAi5lm3RcY'
        b'gXzRh5qf9iA2hyk1jGnWO6aOepf+YvRdM6XiZ7/Psuz9jMS06v1Ue5gse+ZAfjo6izOkAGIdHf/ObTf0wqO+tyPBcqnyM+i6Arj08K9Kz2apeyYR9DahgRNWenIINalD'
        b'pJsXF1Xqjn5deh4MGbwsIp+pVjH0+BAUdlbtXwVnZCMbRna4xDTbnXdqcWpNuJp8IbndL6bDZeJdu7ed3nSqS3jgE9CccFV+QX4t+86s67M0PhN1TtlIAmFRV90uuNWL'
        b'Gi0bLN93DO60c9yfvjO9wy5CbRfRmtAROUEdOeF9u6QePtz6HoDQlfYyxdR+R0Y2pxTUe6QB7KH3AZhWV6QcJnTqVAWUDp4BNZrF9D/adR3Quj/cpFZ6YoiDDOkJTpIL'
        b'lP8CYkVwytyHnqGUP3/O7as43BsltBmv3Wbr0GHrQ/5RTdJAtUughgJqP3ZwqY/bvbRu0DNqNvt5Cjuk33HTxzzhA+0EUFcqENGWVEw7Wt8qlaVFZaSkfZxt0xfVUFBZ'
        b'PwXtcAlXu4S324V3OjhyCB8ZYJT1h/fcUKLDBrbn9OyULh9KsJHIiT5g4lb+ABfgQSnTxUlCYNNJ9xCcnOQh3AGjSLc6SjAFSbl6uh3jBChwVEF30JTLpkwGXS/psq78'
        b'FC4gWaF7xwy5b7+4I3rcT5FCXVY9RDZ0sNO5QT8tCFl+RuiyNJbYSHiBjQnPrSsTIUkJL6wRc7IaERXViEBSQ23Xd1kYiWkkvJRGRCUuVj3kMeaG4hgJL8eR6sU4nAjF'
        b'ylhMoxwr4MerMhHuUuBCAUbP7RBJ2cnyFwAZqJ6yPCTI1NL6yZBgS9duhlweFbKM+1BqKTzrkVjgns3WZOgNkY8BE+Njn22s3CAOb6R7HBjpjuVsldNH3QKRfcgjscQh'
        b'lDyz4iyKd9pNBHPiaWxNOonGPwIS3LK5R2C/XN4tYO1HPRILh0TXTHgk1WYwHjKI0xtDJ1TEABXjKBX0w047XzB8PozaPefRSkCXfSyHVur9Gf9kODwZafgkAp5E0Seu'
        b'PtTyOlghdx1Vk6bPzA8y86eZ8V8BjXZxnHV2WsHdAqH9ZPaRWOyeBXVswbh4P7Amk/5IEtEluiZVn1gaJJbBmWznUVVBgKoKoaiqPgrDNyAQ6h5Vk/E9Z9adtXT9ViK0'
        b'lH1vJrR04jBJ4E5MhLfgneZLLCss5BPx1oCMtGBq3XCHkMGHJP7zxag1b2kvR5bw5zuwjA8ATmN8kjMZV7MoYNNZN4krJfSJyOCJCX0iNngiVUjIt6Y5gkgWsEsLpEoz'
        b'hZQ8MQcj3JECwC+RZxb0PTWqrrQEDJPSSmGhHFRsSVY6qy7bHlNiWomqsmQVodjIYZJAO5ePpHP5NGs9FzVNVqqb9aeFlupm6xDgtXTLUzHPworovNZlmltYxaMZTUHT'
        b'IL+0pHJZl1dPESkQk2uIr1Fp1eRgVeiS6hKRatPQKszJDIwNu/aRqs7y8BqY+p24qd/Nc49Zp6d8jxV3Geqnd3X588UHHoL+JWl9UqaVpm0EXr6aYfpAir/gbiqvfxKU'
        b'xeTdJshp+UvlxO948wfIqab/nHS8UTDN6Xlx79q9kUCZABP83L4JgBWg335AeZ0tQp3eIvA0CZxOhcYhtN069JfCjPObOEpjP6hxukz1YqR5Simvsg0IBYiQFtrOCYw1'
        b'DiHt1iHPw9/OG5C/7aeiOB63DpowTrvFNDI6o9OxsGCfrS5VaAwRY42MtPSlAtVnF6BG7uXUhkHfO8w+dof0m0Ewa/W1S6TGbYA2PQDMAL5GUrTo/U3WoN7P9EqYMpj5'
        b'isGWUJDhCcoiMPk8V2/Be1iPGh9mHL2wvIgzcMwZpaFuErQWAinzQ/ZzeSw/LVL+SwkaBEoAEHHYeuhzhFOrqCgqK9RaozE3yIKL2q9+mDC/sLAX90y7BXmxG3okgFBo'
        b'j/RsCmhe3eEwTu0w7mNn73YfhcY5u90uu9PWvcPWW23r3VR5ctnRZRrb0E6XoR0uAWqXAF51xGVMp4v3yVVHyV0kReNna5xz2u1yOq3tOqy91dbeHdb+amv/5tEfWI94'
        b'xogEhJx+RPbU2DC09dBr7CVDJTn1VUq6szgE5bRk9CNv97J2a1lvUowMTxrPZLbMFFYlCCHZ2jLJjgxTPrhPXYw+uvMkQbozhyBTCcoMdHxVAu7JPJ1Cs1BVtUiZQQco'
        b'qytsF1tppPUrriyvJKxzn4WlrxqhsL4MNx86X0jQuIy6mNC8uDG5Ibkx41DGhQS1yyiNQ3S7dfS/7ruMosvuFo9QqVzUZWW8YtPVh9vNwOqQIbfuc0eiV1ugfVjfffXM'
        b'O+XlAStIG0q5UsfQC3uy8dAZdEz8HAF/Aa5GBVBBwsR/KxFZygkLaeeqdo3Q2EbWJDxw8FDLRmscxtQkG9x+K2ItwwCdHgqAeNcfJCaWIwHA7gnPRnM8IcxqdhFoj44l'
        b'lCzSM4W4DW8ODGaZBHzWJI1VGvGFWjDnd6BxMNa5J19I/grpX1GwWCkCpLrCRCFVmCrMFObgCkdhRe4GKawVgxU2wVZKcY4gR0y4PlvK6UlywA+8FBzf5NjkOEWacG5s'
        b'CBcp5ZDnOi7SlD4Z4swoHBSOFNsu1WHPHSm2XarDnjtSbLtUhz13pNh2qQ577kix7VId9tyRYtulOuw5hK05uiKFgD8nFA2m70NDmVmD9SDcBHY4qxxMYtroXNjYkNKx'
        b'vAMbW3rPua+xc2eo8yAhte0q0bnvtMyxIqW3puW3zbHLsc8ZkuOQ4xhpzzm6WcAq7Z2Y6SbU6c8Qhf8oVhEO+ZG6EnJubgxcEA3RxZQqgriYWqc3BrEcFCFKx+IAwnZF'
        b'dFnAyNKCuUuOC2EITupiM+XiLkFSXJcgJbFLkKggv9ldgvjkLmFcUkaXMCE1tUuYFDepS5iiIHfJWeQSnzyhS5iRSe4mpZEoWZnkokiEFzNSlZawXAuTUiYRTl4Ql9Ql'
        b'SEhVguULki5JOzmrS5CW0iXIyOwSTErrEmSRX0WichONED+DRMghxKT00pOkQG+Y0McKdA7IwWouQ3YSIp37cckv6H4cztx6bZnoHKqz7CrKqAIgMTqPDo+CkVaJN2cG'
        b'423p4KgzWef7k7rFDE6hdirTAlPSJyeT4TdRORqMfKIWETMWrxuELlWLSuI3xghVI0iCAesr2wrACaUdeojr3vntXevfvsOI33N4c+uJSUv8CyJt0yJr9rLCDaFvZp8K'
        b'rTjBMjaHxNO9FHIh9Zu4GG3EZ81RS2AybzkTn8QtzGB8Q4jOrkjlTJrW45PDcG0m3jIxPZitFjFSdFCwFF0s5nw+b1CGolq0A+9AJ1FjahDagXaYMOZDBHhTRCbZ7fR1'
        b'SiHipjdD1KadYXfTQjZhwleBhzjqH9GNsXOoD7xvO5Quy5ka50ntdpMM4Zpa2yjcImmix5UqwUpzX4YkqdYd7z9QT4zydZLxRaGBf+R8N5b1AJ+BHi/qM3CfZChzwjxM'
        b'WGDIrVlpOwfM/mNNtO5754jmiOdI5piQ3mpGequIzAHiHBMyL3AzgYQ69bKOtOJ7sDTb3KAHm5IeLDXowaZGfVUaa0p7cK+nuh48r2cP1jns0PVgjwzqDjYWHUU3UsHf'
        b'WgjnZDYoKBicylKfrNCTciZVow3JqFnI4O1on1WFOa57ZTnnDnbNKsNPSd/ODJrCGxmeiLeRFWdH6lQ/vHmqlAwQEYOuo4P56Ly55XLUQvUghCUSxmLlHSEjyyt91WIy'
        b'UwUEjgsdRG0do80lnLHjMm8a2VVoylhn/82ENHDgT15BTBXsdfDpTCtjf/bUUq8Vuqg1fGzCTFeYLEsNp64XXNENdDMVv7EqJT01EG+Ts4x5hgCfsJhZBXOMN95eEJAM'
        b'tpHx7ojQULQhL5UpWu6FLgvRbS/cVhUGGW5X4pqADDBuuy09h7OsTAvsFxzkh2tC8Bvotj84zi2XS3HbErynitrGvxhSnoprU9JCJPgGrmckDgKr5aNox6YGnvHZrKQA'
        b'qOsgiWAWI0E3BMNdh1J/FPgmuoVvB3DtYMLgS2i9dLHADNXhE1XQ9IMD8WmFMQkk+8l+1F/7JD8doSYMOjTYFe02m+qDmmk9o9dxA35DQWgYl+PH+OET6CJVcbPGN0Wq'
        b'JfiiiFCNXmdRA0Pmggv4aFUseTkcHbUm9b0tMBhvB4cfFSRith9p6trAwPScZLw9U2t+mvYKtBafoIpy+DWhBUmmUUT98Y4F5wupePuiSdR3Pd6SFiRhbJOE+DC+OZ9z'
        b'ArgVtY0MwMfRBm0JCLOZKkD70LkRnBuRqy5OCnDwgWtRS7au5OgKaoRJllDAMJnWJhXo0BCutCdHoc1492TCdo1nljPp+LUy2uZ4fT5qIEzRhTi0s3oJqd7N1fhipYSx'
        b'dBGghgVVVTAl462eaKuKPCZ9O3CK38Qg0nUCJ/LZ6KuYlAHtRmuV+JoZg27gjVWR8O2VkZkBUD+kvmpD8A6Fnx+ZmGtCMvjKmoSa0D7aTdEa1GLKoAPoThVoq6BjOTPN'
        b'8RV8SYWvLkbbqpUWi/EV8vggPuIQIUQbPCdy9G/PhZRT8TUl3poeFEzqXczYoL1CdI6sMA105BzOFZPh3yBhxueVrrJbxnU5tBYdxmtVi8VMEFpLmphBW7IKSr750FWk'
        b'ghP9dwt+szc7VYFCrf9wyW6Ge8nk8WK7TbvdV94bOSshZum3n43cXZp55JD60bpZP/r+N3fE3sC37PbMuR/y4JN/fJSkHHaHOVhwVxqwm9nyj8+L13ZI7rZNY9rnXvzn'
        b'alvHFus3ygW+/x38b5OA/5p+dEiQd+rUK5F7/7nirZlPqqO+ahUc+H61T+exrTa/OXn8r5lzv961+tiMn9qD3D7JSftd8h+3LH93346hJ87NGsd8bHbz37sErgfPFG7+'
        b'8IDpG5dWWW49u/3Lhd9cPRtnNUt8PTGhpO1g7awzLfHr7p+ND35v7l9ulE2z/I6J+OCHRaW/Ghd+T3n04MbCiYtzo60KzNtcPGNT9/zqwJzE07Mn3fT9puHywzKL2i1V'
        b'Kz+KUnX9NwK7nZtSv+lexL+OR+Tv/LTz067ZhR+qZ1/+csUXR4vCp0zd+3r4J79Z35LvZn/m3y4XVTevPblZ66iS2In/9OXty0GPb/zh3443//A07+ifDq386Ov2jvwV'
        b'Z7f/py29be1fAttWZEb97eEs6wUhO1fI/p40zn30kkERcWM8kqvzf2076a2vo5vf3ueikqX+3eaTc9/t2nrl97tWJJVXRI/Oyx721q27/kfZhe7Wzt9OT6vJ0bhcbdhh'
        b'P8c58uJXqKlge9Zxh0tH//5jcsA/Pm5a+uXE4tuPy6z+9nHnXse3f3jstutJee6Zwjmr3pd7U3PaM+bNJBwDPlahYxp4hgG1vMJ5/riGW0NwbXVBINoekhGUDLbFzwvw'
        b'6+hqEGU6cBPalW+eamivW4QPcU6g27I5P9OnUlWottrK0kyJ18zBl1X4SqWlhLFbLFTgWwnUwwq+jl/HrdR/SAquESxhYwtwM/WOYopPRuHaNPJ6DdnNCBkhvs2ig2gN'
        b'buPIuxMxHdfauQQSrkuOayh55wRk7rgUwhkUfxXtckK1g5bgK2RQnK3Al6tI1uYOgvl4bww1gG6L76BdYAE+SIC3odc5E/ALfWjt4Mb0KYSDC/SXB9M5lUy5Qxxlojlk'
        b'3qmjdAfi9YRRCk4no7++ULCMHUNYwp2U00LHpeDFGm9RBpB5ihAuGsWiC9l4DedtphFdx9dTyeQnYcgseU0whw0JwNcfc36V8IUS1RIy5O+Mq8JXB6EtaOsgqaUZbh20'
        b'hMwF+Er1YlKEdJEEXZ+p9QNzFG9EVwOC8La0MHbmMkYyncVn7NGrlEbfGeAxIBmdZRhH1CBYxU6YhLdR7y/oNTK3X0WEHaxFZ5LT8d65ZJrcEQxu1p3RZVE1Oh3LNeC6'
        b'BLQB1TJoYya4fSeLWRphC8cL8D7UiI5xUc76ktmrFl7qZiJUZz0kTWSJtgdRIs3RmlxUGwKrmZhFdxhJnsALn0ONj7mlLs6asJ4npobwU6qYMc8U4L15aPdjkHOQ+Won'
        b'eU8yIP0wE5gLkgtZ9CWMONIDvy7CbRnmHA+7T1LNR8O1NlyPtSL8SwJ6DV+hdBSTxa+R+gHalsYGovWMJEXgUIHPP5aRl5NNZlG34kHBGVF4bVom2oZ3pLGMMz4kWox3'
        b'oy2UWAd8bgWpNbLKtU3m2B+WsVII09GhyVxh1uONsag2qiQzOIiwRalCUvYthBtHV90pBfgNZi75fmJgCuFxmCC8XjpSMNcTn6LeAAbjbTHal6gmk0t/5ISUIAHj7yfG'
        b'a2d4UNv8Zal4DYmWEYg2h/CripjxRfUe+KpYjJpIWaFZPJfOJ5HQbncDJwY26JyQNPgbqPYxXeA2hIBbpEHG2xi0Ge0IkaM7ZUZSpQDSz7d5m6HGxasfh9KCoHp0pI+P'
        b'SZdvJAmQmaUmTS5h0hgTdBFtHPkYuKhodBKfpWviDrIxIgUkPW87mVxSSSm287KrK+hCErpgQjYg9aRaoLyoxQWdI60GroG1H0kYd+kQMiPcQevQuv+5rQZDj0CGthqo'
        b'XMe+x56HE+jQTc9dAd30PCp1Ay2pYc0jOhwi1A4RdOfD+4p86OAOtgk7HPzUDpxv9gka56R2u6QvHDyo98kQtUdIh0eE2iOiNelq2oW0uzZ3PdsjE+4WaTzSXsgr5RcO'
        b'bp0ew5qj1B6hHe4ZrYVXF11YdDdFPTyjw72gPaugLgmM3c5umN3hFqx2C26uPr+yZeW1uGuT20PG3XXQuKXUTXjo5Nbo1uDW4eSvdgKn807hdZI/OLhxHuXvDldrDZd0'
        b'eviCLaTmYa3hGo/hdRa8ZdzdK+tEnbYO9UuaihtWa2yDP3H20SimaqbntvvmaZzz2+3yH9o6ddj6qG19mnI6bAPUtgGkyKlXU2kGEzXOqe12qQ9dvcB0WtMKjWtEnekf'
        b'bF2bHE66HnVtntu8uN0z7JqTxjOOpPuRb0Bz9vnpLdNbl30QFNstZIfGgyVxlwSwJG5PrmQN8mgKJES0Vl9dcXUFzSHh7hK1b7rGOaPdLuMLW/em0e8PT9N4p/HFG632'
        b'zdA4Z7bbZT609WyapbENI4n4BYIbhOMrO4aNUA8b0TEsRj0sRjNsXF3CB3Y+D4cF1CW8T349fKmOn5dfs4vaK4rcD9LpC3JvtJp7vF4iZ3P44CwaxXvYyeij0SfHHh3b'
        b'4T1C7T1C4z0KIss6ZcNoZD4JXhdw6DBOO9EnhEvRwHsoL0mkuouQu8UDr6FNVR3DxqmHjesYln836e20N9M6EmaqE2a2z8rTJORrvObWifYOMtiLD+at4GiBViIQGijB'
        b'2LoSdOq7zAvyK3XqshJVwfyiRUXP6/3BYMTB0Mrj/+jGnX7AKe+RvK7Cvh5saP1ExteThWRjn8k+YeD6Lb2+wAaf+p14XRLFXDaPZYQvgawG5V5a5v7krMYzhVbA+k8j'
        b'mOtL6DY9Q+j5Pnn31BhO6wegTJ1xCI5wGe89QOanLMovDCovK10mfwnFR87icZd5Lq+QkVtS+CwCfzTGIQfdd+NMtT4N7Eupo0Slp96Q3JdRXPjsGbhWoBCOJQ0Ugtyz'
        b'qTYH6HLoFKxelhJOgg0K41WV5fPmPYsaocioQUOomkBVZRD5TAa68np9E6CQ6r2+NHkUSzBygJ4mAcL0mGR/ikkumceDkBcBhJy0XlEZWAAp/MWqzCLXYPp5FnmmQF6Y'
        b'rt6orgfgpIvBzZhOkeuXoErpN0CHsgBS9ADyYf17LTYmyDAvnbh7LqP11U6NDAn5A0Ym28CNXBnrTkg2OGBkjY4SmViWHjD2emrohnegI3JJRt8mD/OAPpa6DAYzO1on'
        b'wcJf1knw0x/NJhj6wDWGHKtkqvnlVaWFIPUmkx11jy7LL84HoLJZJW+5RxZfWpQPaheyBGq1AvoF7yCX6k3xXs95tYMSlRnv/DwvL1tZVUQWrRJu4PkvLC+rLCcza8FC'
        b'f1lpyVxlPkkIlFC0bnfNQJOistckQqJosY2cCzxOkWWZgX6ImZE397y8CfmlKpJzD8d0ur6qaxthRon1Z6PF1IPHbyYfaSs49J713SHI+q01ptmOI2cycrkgMOqsnOU8'
        b'dJIt2018BB3qxXxT1jtTSrq2tbZr8yJ60bziosouH6OVTlVQmktrgax5UFDV2GCIRVlk+B7kAqUyxlUGtgra7QyP/3mclTH/QCUPeVrwt/IfMJS7ycWaPFfB6du/1jDf'
        b'z5axrM2LnvPvlHgyR80DhX2b351PBxjvwVFMT/JZnSRKkC36Zb03PockKoaBU5pgdLTnnmoKPjka15BNsv/EQHQqmzsnhgeZaXBIjU6jzeajitGlkvjRcwWUj2ro/omT'
        b'P515k2E3h1tYeG6NtahnTni9enCt5wGnoc735r8nzX89fGOoH5u+LjzxUXy9sj7v1H2nkRqmdK7kx9kfyIXcxvDkEnzymXs8vAPVMNweDx+Np8cRtmg/bjUPx2/oXeYa'
        b'OcxFuwfTPbrK2hn6IjqA9/Xuj2hXxPNIqkgXVT1XF1XxXdSP66I/KGWMoxvZmfjGkH8fu/u3B0zUuKe2O6Y+GOrfHHV8YV3C3kwjyRXturbP4n95yZXeXqTyCXTmf5KL'
        b's8jA49li0pmdQHLl9CIez6Bm5YIqQGml+s1NpWdsK3GbaBCLTrqjY5wI4uaQ1akBGeRNJroiimBR20J8ouTA4n0iOpI6lp5vKzjynuxt6/cKkeM9v1/V/WqnSeGm8E0X'
        b'60NNItb+a+vgqte3vnlveZq/xaG/MIc+kaiv7uaKPwC82dBEpq7yu4b03Si0GXhzr50i6fczZNLBAU/shIPDu6WMp69ab/ZSm3e/FW6ct/JfUN1PyWWQdu6A/cRMUt2m'
        b'L1LT65j+7PzSRVlAFz0RWfYE/5Nlr5fUr/dsQSZ+08EZYhWcM/275GlbwQEy1pveskaOZOpPcxo10vOSmbDYnEmbJ+i65koWADggmoAuoWP9HBD1OB3Ce3z5A6L8XLnA'
        b'oMIFdOwZoAp7yogpnJC2sANX/Y/GezKOLn0gCrWN28eSoG9cAykwhev8F2xjGCwMP6x+wYXhGY2bx/zPOZrink3be00XZWSXXNl3lVHBeP7vN17Ka7Cs1/3unQcCxuQi'
        b'+96v/qCFWfZYrDmYZc/zKw5fSRvElGuQ7gmkQVxfcFWmMCmWdEQfw1U50fMFK/+R4P+nyu/t6ZeMK+a6LUvxDX+ewlCGCpAbnhaxaRaOshr7FE/FPbsJ8d+fCq2YR74Z'
        b'Kww99WeyVELdzccnYKH0wbWBcMYrGs+iy57THoN0PnXB0L7HnY9pz5HHDzv0Gq6hR8xZucnUxSpZNc+lB0kYKb4pQDuXhvbR/hSP3Ov8kgKRafvLuPZ/nAbtrwUjd7gO'
        b'V7sO17iONLBx/vzdguLoTEi3GGbYLVJ/VrcwBGO4alvmNegW9n2CMQCOZUWNsGoBWZIcWwrX0sGycpxynHNMclzIDorJcc1xy3GPdNUBNSx/QaBGr67VG6gxJqOKCozO'
        b'4Y1xPIqAkeD9aIeDwCrFjEMRQAvhVndrdCDTXIkv48uDQGhMRdnW6DUBvpGCt1UBF4FapF5Ulh2KzieT3pGJzjxbpo03LjVHl+eayyWUT0jImrsE16hAFs3gOhDUn8Wb'
        b'KHAA70TnUBu+7o/bqiQg32LQTnwHv0YREIF4H7qITovM8RUyOePLDDoqwvuq4FA9cvzs1OkqsOyMaxi0Edebc5iJs6gVn1mMTppDz8HnGVSPry3nZNcNOaPQBrRDBb65'
        b'8C4GbUG3F1BRd+NYE8aC6XZhZHkWQSGDGJpSEbodMAlfASk/pHScQfvwqVIKCyjM8Md13gal8V1BQTGr8XW8GarJc3bPysGtlUp8SZEcgLfgHZzUvw7Vm64KwjdpM4Um'
        b'4nMRuC4iVMSwuBEfyWXwmlloSxXI9ebhDVM4uAq6nckjVrTWhCdPmor3RkxUmDA5uF6CL5tPo7WDdqC6ERHkt3ElE8aEod0BHJ5hkz2+iXcLGRY1MSFMCLoQUfrPn376'
        b'KcIZZP1NYmZ8XuDH7u5MFaCv8SlSd5dSdTnhmuRAwOlsC5mY44c3ExIUfnK8Y2pySjqw5ungl/kKuo5fzYLiScosZ5MZhOI/HPGdZYBsmzoixyDyFCjEZrw5JJOvI0Pn'
        b'49CFTqObFvgiyfFOVT50b7QLr7UkX+y0RGtCpWK8JgcfkeDt2ZYTbJylY7IQgF6O4POJxUtN5zngnXj9YjP8hqRairaYZlqQbrEevxaKb62Qe+Ca0cH4gATtj5ejtrGR'
        b'uMER1VuTfgU6nngT3u8jxmtJVkyYVIhac9DFGXivBG3Gm9Bef7QB3yI7kO3ZLiWvoGa8xgXdWuDlgq6SHv0qujIvF11ZgTcIw/wIIds88IUE23TUPE8JnYz2tEozFzZS'
        b'MCnIyjovZnheEMMNrka0dxSuTUdnJuF1+AauIaMuNQRvnkTBVDrkBzqbnJGeTjdg5/BV84LA5TTJJItkpo4ZH26Zl2d2aPxYpgpO1NFuVIvPQTEaTBmZBbmZMmch2oXO'
        b'kOSPsmFoHX59tEtsBGmU3XnoMj6DD+QMw8dnEKrX2GejdUWophg34Wsm89Eb1stm4LNVoDI1F53Hl3g6jWhMDpootrEHbCJqkZN/MKjr0RZ82hRfxbWjsuUsRZ28MnJs'
        b'PtoEHYGsRHh7SiCZL0g7O0hFoXgNusDVxU4rs9SgiemKZLoFTAFcVQD0uq3jSnRwLfJd4MS04JQgf9JLtsgtSvDxcoqbQXX4kN0zgTMUNDMOXeBxM5fQJkIcDEA7sp08'
        b'ARAtFh3B+xkB2s7Gh+EtVQkwPS97JSCZ1N3WdG4chExMCcriUG69MFTJZMNcgS96oFcrp0zKCpoiYJZlD1oWmlKlgM51Am1DLalUNJsymce88Xvu5LRMWtjgyWME0iX4'
        b'yuTkiekZgUEZFFIHw06HnqLzM96aNRi9Hjufw+pMERLmojtGxOQFdk3KIMxaFRzRoINobXkqiJJzFoMwWYpbBagG7UfrqsDAqys6g84rMuXpZegy5zk+Z2ofQD6GdP1T'
        b'aA1p3l146ywZ2f1fQ68le6I7yZ4R6DwAvvBaG9SANw2nrYwuq0LJpNk2KM7TVIovDsJtlYurWMZOJcxE18ggo47ca+auUsC8RWYi0vmOkkTO5HAQLamFXao8CNegy76k'
        b'rTMITX49FRRny6Ski+KDtIxDSafcoEDbskmrn4rNIaND7M+iA+gNG5qTGemK+82XWLFVaBPJax+ZVQLwLbqpRWfm4I32jrg2jWXYkRSmaE3xfn6W6BLFJw5FlzgZvfkM'
        b'AT7nUUAXrCEF6Dj5RospicFnWHQQb7fn1pgL6MAKis4owxsZAGeg1wspIfPkNgC42pouZkTuHngri475oFqaXwQZmJu5TjF1eoAcnRIxFtZCe/tFVFFzaFU46dFyeqwR'
        b'mAKwAi6VoWj9KLRGPI/wdRsp6M8OXxvLzdZkPX2DszSP6wVo75hllHAySZ2aEkDGgw+6yEn9LYqFg6xV3EZ+O7o9NZV0AUKeCK2xYlGjdArHQNRNcse1QRkUziAZjM7N'
        b'FtgPR6e51XYrmQ0v4FqK/BANL8hnUcvwOTRBK7RbAQOZPHcPj2RJnW1Er9IE0R5PssDXcu/GluDdLDq9AO+posL6XTlJQKIrWQMJiaRXwrAVM55ot9gU3cbXKZySrNwb'
        b'osgY35yZgbeizSG66kFbXjGooQy01gTXob2oiZY/ENfhNQDKQVsi5WTeMR0lQK+noYvcUGlwJyxJGwDn2kwYAT6Lj8WyQfg6Wl9y9/FhsSqG8JwHTvttm5Ja3jXees64'
        b'UIngTc/Fae4b8pLvn3gtZcGu8V2ntvjnxHj+7XcTdypr6uaX//PDKTE/jLv009WC9Q4f3Wx/2ho4+o/3VkaMjvjh3+vHiW7seWdQ1OcRJ8JWNf3+iefa6Kiiew8+q35q'
        b'/kgy7Mm1xqUbxti/am8b03Vx3h+9Cpt++yQ3coo06q299veG292TtqXZfP1OyeX3lz5OGleXPt7r7wfDy+pq87Nknz/y3563w/pc22dfDX7yzm6Xe9t/0MwYetFmxMXJ'
        b'a4Qubui9d9+db/59W7R9hTL6lhW76UP7/wxx7Jr01rWdyfG7c647tf13e1r6jePjp9pGnrb3Oiy4FL3B4a2WqKdBYZ98Pm9s9NfvXXn0/u7MgrEO75wc/6TjgsP133+Y'
        b'NvtvAW9/aR3xJTZ1FR/LeDXmjY/9JnQrwiZ8MOndfy7O+vA/5fO9L80bGxk6YsqRTyNPX7/8vms5ntKluHHk7qCgD+v/VXA4Kq525qlSn6rkQVN/E2f+n6ob7ywf8Vv2'
        b'p+Ljf9xePtIFZ/g/nRI97wv/9pvyS8PmfhPy7TdnP/j+/o0wxY6oB3+YNPXjd18x+yitwySycYbp13N2f/09c+D606/uXzkUlv/oy9W/f1X+r7cfHxwjm9v4NDzu7KZ7'
        b'N76Vj3b9+ljXxR/bsz5699ejlzSlZ9ov2WGTdnBNwMiCHz6zUn46/mv3M5GdtYX/iHwzecfj6S7XGwf/Jf/t+FVfbP/k1V8dKRz8R6Z9c+Hpn47F2X6zfUOV9V/vqx7U'
        b'Ni+p/njW/PIvL/9p7N/M5xzOjjm05Ni93HeWfPCPwd2vfbXqw8O/L+++MPPM9cDAb726bu0JeksROvOTW2mr5vwm2sv8g2sZdjXt7iYL5/7lV7vG7/M58qlj24qA3zxI'
        b'WedYv/mk/d7lznec/vbVbJd9d/Mvj/3djYb1T3JPVocf2W43eU/TlrQRwr/tao2Ys/LDTvPmPz3NWuXiN2pqNTtxztHPz2bdT3p3xeufC3w99uzqePhw+btn//xj5r2v'
        b'/jsq49PxmTmvDn6yx2N+zR2BQ8fCe53r73/tUvYn5zWb/rpmf8WttUPPXQ24veL9j//e2T39phqFL1iVPV9++0/Xgm7b+7/hde14ZvOn71+9ULvd5Nc2sePkpXsGt30V'
        b'eS8+8W+HP1L/c/ITwY9n7jrs3715/83XHn8fYpH2q8dxS+W+j+nqsBEfRGcBOUaWd7zH0QAShg/i5sd23PC+xcJxIzplyQCkT4BredBcC95DZ1cZ3kxnV7xtNociu1aJ'
        b'LuWuNoYTcljCnfg0Rc6lFS2lCOzqRAoSk6LLgiXo1ij67hXv1XTCn1FlMN+PCaLb7DmuUw2m++LlZLbPw9c5DOH5UYgwRABwDMPHDTCOI8R0L11JJtrLdDdNMpTgjfjk'
        b'AoH7ZHyY06g4ivfggwH+wfKwJLwlkGFMp5P5yBG1UYpQ43C0OSAYDt0DybQbmIC2C4KqLei7UVPDUg1gWQVWg6YIS6ctoHA3wvE1k7m8lkKcd6iyMvX8toTxSBXhIx7T'
        b'OJjhWVLNNwKC5TRviR86j84IIubh3RzMcD16bSmHbWQk6NhogDYuwnfoET26gS+PU6Ft0sWW+KIKwM+9QYZ4m2s6viwhM3ZzHm133BJtGWAsBbJJQXvQeSFqws2TaCNm'
        b'4eMjU7Un/pkU4jgYb7J3EKKtQnyLq/F9+A0LRDi7LSFBMOWnmjCxywZlCue7WFHc5XDCh+wKyAzEW9CuVNgzkQjm+LYAX/UtpajQKWnLKUNEuPX1BizRJbyHdr3iOana'
        b'RTAPNZBFEF3wpxlHo6ZRhhoyAHY1tRais3IpTRcfIHzMDi04kDR2LTqeInBAjUsfB9LPj6XTE5lKVa8zGSOsmxJdo8KzcHR4AsVXjif81pnkdGN8Jd7o+NiXrs0k31oD'
        b'0J9AxsH+dKA/fEBM6RsjyCBtPZGTjogJ7xM8CK8RlqNdlfT16MRAwtiT6iL1d4pWgHmZAB/Mx0dptUSji0m6FXvcLLJgTx/L9ZPt6W56tsYRbSNsDTq/mmurw3h9LsfW'
        b'FC3UszVkG3aMEj9uKW7sh7O5hc8Ba4Pr7WnnKcMHSE1dkBESg4IzdNjKIXijyAavm0wPm9HudNza/2Ez2jOxj1Mvq+WPbei+/fSq1LQU1gptYwRZrP+QwXSIjMenFqUG'
        b'+iWTWm4mY42wU+i0YBm6OUju979DDP7fvVDplMzgT2+/Uj1Qi12DeniL4RTtdSeAPd7Sg8ARYu4gONuTkfk0rmxYyeESW02u2Wg8xgDCz33/iv0rOh28m1ZqHCI+dvdr'
        b'l6e9U/n7Fe+uUMtnaNxntjvOfOiX1m7n2+njdzLtaFqHT5TaJ6p1buvidp9RdemdvoEnZx2d1erVGtbuG1WX0engo3EYDk9zj+Z2+A5X+w6/FqyJnt3pG95aqPGNvvZK'
        b'++QczbgcmlHyO2PV8uka9xntjjMe2jo1JDVNOJipsQ3gEZBL1L6JGucJ7XYTHrjJmoYAWlDjFtzhFqV2i2ot0LhF15l12g6p99fY+nR6yPmCCTUeka1Zao+RdcmgYz1y'
        b'96qmxRoHP5rfpHbFbLV8tsZ9TrvjnE4HN8BvNg/t8I9R+8doHGLu+r0d/GZw++TsjrgcdRxHYkb75Kkdk/PU5J88T+Oe3+6Y/6mtW31xs7i5sGllh22k2jYS8hmxe6U2'
        b'n24B65bIficUeExguxmB0wQALYYMV9sF1GU0JT1wiWot63BJVLsk0gzmaNxz2x1zu4WM6wQWzM2Etpp0OIxUO4zslIfWW3V6+TSYPJQHkDvPkA7PKLVnlMZzRIdnjNoz'
        b'RuM5rs6q09mzMagh6GBInckDZ9+mYo1zMLmzHVJXvXtMk7fG1pdWprYeyfNXNLZDm220tZylcVa02ym+sHXgNdKbwne/QgmboHFPancE22cNK5ojryWoPWI1DrH0VarG'
        b'Pa3dMe3ZUEuH/WP3j20qPll+tLxj6Aj10BGdfFfz8Glc3bC6ufr8ipYVd0VvW75pWb/6Q4+Mj70C24Nmts8p6phToib/gko0XgvaXReQmpFlQhU6eTRaNVi1D5v5vuOs'
        b'H8Auz9Ho5vnXhB3eY9TeYx54BDQnn0+/xt71eTvgzQC1R8bO5Af2Hk3SZu8O+2C1ffADj8DmaQBqTQbvp/ObpR22YWrbsE6PYY2rGlYdXE2iO3k3JTcXdjhFqJ04pO9M'
        b'jfOsdrtZn2odQDZVn1x5dGVrdkfUxGuzO108myY0jGtOap3znZB1TGTrRKTQJOKYhjEa22FcH9Y4x7TbxTwEm2De5B+1CQYmC3YmfOrizjkebYloruwIiVOHxGkC4gHn'
        b'69ghj1bLo6+N1MgTSMqkW9QlAOzVcX/MzpimRI2tHLxiJHS6eTfNbZi5c8JDFy+AX3COIuoSPnUc1mnn863Q1snmUweXbjH5BfNOPt0m5K5bypD+4nrAtdsUQmaMk6zR'
        b'/IB5tzmELLTvLCFkRb5pzDyQ2T0IQtaMt3+H14j7XiO6B0OKNoyrV7ctvLFj3AI6XJNbre6atIckd7hOeWfqOxP/2W0PsYYwzl7dDhDLkXHxaAw5ENLtBM+dGWf3bhe4'
        b'c4U7N7hzhzsPuJMxXkHdnvCVFyMPOm/RYtHhF3ffL67bG976QM6+5K5O3B1IvulwClQ7BXY4haqdQlvtNE7DKbT5gRsJtC6966hxm1g3odN6yH6znWb1UU1+71sHdAaG'
        b'14k4kxBNCWpreae13X6LnRbaJ+Cow8G1zsJAPuLByUd+CyIQahkhEy4KCp0tWqrDrhlYHXgR3OwvtJ7Act0LfdsX+D0E8KSh5OIv4t1YUizuZE+WVVAsrvG1m15fBJcL'
        b'1k/aJLFC5k2heayVUM5SmwwZz4HNYXPEOUyO5H+EzSmWC/LlhAiz2HmVRUpZQX5pKXVbBpBU3i0bWUNLYPHMLzXyZsYZsi8s5DyO5MvKiqrNOFCkX17epEWVKWXzSKXP'
        b'LS0vWCgHqBl4i9Oi1apURfOqSgFatqy8SladX0aRX4UlS0oKi8yMMikpoy/mUQt0vGWWIhVnroXzciIDe+OykkJVsJlZdEW+Mn+RDAzjRctSKKqMdEJVCXhnI+kAwixf'
        b'VlClqixfxH2mIzWlMC9PDkaPzYDvABgbKQ8P8vSD25Iy2ZIRweGkKHGk2NVQ+Mr5+ZW63PVYPJoCTxt1CUfxqxw6jnwADuKMiqg1XFOsLK+qoO4kaAqkKJUlBVWl+UoO'
        b'x6eqKCrQ2e9TyfzASFcgKRLJhhqiXVZBgkWVBcFyWmk0DVURVEhlkbbe+HagcOMyQlMVqQiSHrT6Mm1rFJZTszgV4OQP0jCqsB6YvN4iZDNeztcc6UbFfNH4Dkj6HARW'
        b'+Cpu4+R8AOXBF/GWlD50Q/F59DrVDY2IrEqFeDskybz8QyYVgpDlxuJQvMfZPdk2apzv4lX4fBbZPJ2NR3tmxqVUotP4KGqVxmQEuuFDZEt7KAHd9FiOTlmHjkFr6dn0'
        b'Xt8Upi60U0KmBTN5/HSemJ1LWHpsqPADlaypuMYdbaGa3yaM1wIRPj2qgH5suoLs1P2yQDBVeqRwOlNSeiBCpDpF3hw+u5BDnLm+tcZ0XX3Yr9Y5rW9Ia5B9M2Zj3heT'
        b'JAtlAWHr2EKJ+Ynlln6H/d68a/1bqxGvipsPCBWXg12E6+XeGw6/54ikmsOCwg2tosUFX//pm9BXr+81qf33vxaf/n1ieMxk1/nRu23ipd73/p435bR8/OKmVep1FSPa'
        b'PG/eG/Lp8Lz5fqEi4Y+N2FThgkp/4+izrmRF6M3gEGF8mMLKIc3n8No2MfPO5iHT7l6Um9PdRInj6rwE/uDD4NRjad5jaM9lsXkUYBWJ9sGJB76FdlNJvlcauvo8EJpx'
        b'uF63qwk3pWg3sv+6g5tU6Owok+SMID/t6flgXCdErfjQBO4YYDs+HBqgU52zWEjPRXDbLO4UYkcK2ky1A/ERxzCWUw8cv5C+c8K70QlePRCfQUdBPxA3TqVnJviK63A4'
        b'PbAeQc8PDgiCyLZwJ1Wzm7wKH+5xTINPcyc1Vxmqx4YuV+KzOt1CfuNLdoB7+M3vnEU0WkVeXC9tN9Qs1+18k6UDgsj0mxpTMDXBWeA0BpHpntONDCiQwEZmjm/fG5lO'
        b'XreH8KsdDv7k3+fuw8jKJR/PdsZNAJbwkZCVZ4AukUcmLGlOmewXLh6EryKpES7s4EqtwlaU2iNK4zGiXkR44ob4JtHBlGbBwQzCzjXlapyj2u2iQLNnTHMkp8xDbUvd'
        b'J2zDYrW134e8sT8jGGHWs9iB3jDCcbA4jyeX44YwwnhflnWEhdjxhWGEbJcJWYFyyRLUt601uv6yOjstnJUWoc5Ki/gXtNIC6+81QoSZoqiM92Vk7Om0SsWtx0V0RibL'
        b'Q2JcSrzC0JMpv+gVzS0pUOUWlJaQr6IptFtrwXoeeE8pmB9MYwQnwjWeRjN0iMqnwtdLtAxw54E64Dn4FFMVUTLKlYXwgCw3dHngnbb2m0fwhJy0POptoKqitDy/UFsa'
        b'bQFpIuDwR+ctAFYmXttDVVVSyblW1WWqer5c4+Oz8wKfN2rOc0dNmfS8UWOnzXjuVBMSnj9q3PNGnZYY/vxRI/JkPOvzHJEj84Jp1JR5nO95jjEpKgyU+fPdx98Iz2+s'
        b'SEAhyRxn0Z+KwARlPnVnp+8T/WkIQDJTgRfkRsWSiOBQo95FNRQ4Z0tc9yMZLCnJf76SxmXnkCyiOUvJKm5Mcflw3bGksAc71Bv2ZJ9BGYfpSoD05AUwsrzAXJ90hkp8'
        b'8WG8LkBlTubCbDluYlAD3hFK5Zh2aJcnbgsNRTcyQ8WMIIXBR9BaOf2mEh2LDsgIRvXZLCNA+9hUMW6mL/x80asBGRNn4lcF5MU6duQKtIu+iBkWHJCRgm/iw/BFDUsY'
        b'oVC5iOYjSgf7A7htEFpfgC+KGaEzG+NtSoXAeFs5qifvWiuHDCYrISPAe1lPXIPOU2nqILRzlSpciS6vEjBsOYOu4itoKydKP4K3pqnwlUGzFygJ6fgE6x+C6zgB9wZ0'
        b'5xVA+2ShDRTtswEdoKnJ0BV7Dr30Cq6hAKZodEouoFLSqXgHOkdpxC3khydykpIT3Z4cji5RIv3n6Ig0mc1V7vYlk4GOERItHWElHGd6BLfMBeK3oRaeerQLH5cLKS1e'
        b'aN0Cml1FmjazaRWcSPZWCN5JM8Nnhuur5CS+QvPLng/2i03xHoFKxAhN2RAJKTakmGLhYW6pxKfRlkEMIwxkx5ESraF1JUcb8BkQ8prnjLZiGaEFOw5dmlGVTF5NxK8m'
        b'pQIDqqCaDoAeIUwpg4+hXSsJu7sVb0BvoD3oUDYJ7MFv4NfwLsLv7kFv2IgZvA+1WuDLCdMWoxNcm2zH+3CtgtQsKf0tdHkBkzKdt5Ozahq6jXdn45rJUrxVQehDm9nY'
        b'xbihxJ79SKByZMk22HkiYOatkTNlbEMJY7vOabrjt45xnbumOznGOa1rODPG0VH5IK4zssnf5jfk0bR101q/KroieM/3hHB64Ph3nO8NuXfubZu3trfYfOVulTZZMUF6'
        b'+G3H96RXf2s13znJesSUiKWhifFO6fUPvwhlP+guuGAy8csw4Y+eNXKPo6Vmlk72kuoJq1Mr/BKYTwR24m8t167MCB0n3p+57vqZ2DIH0aY9ocOv4o+b1/1GVNZqaW2b'
        b'8G74WpN3RYv/M/SfHm/nS0I6PX6dt3pi3nu4wHRubSRbfVH07q4/2471aXxnd5Fg3C7TLYUNa1w93oNr5+88Tv0zvWbKpr/a3D3yu0WO/3JcJ77wkWifrZlY8+vSUIXC'
        b'aZSGNTs81jOuQm7H2eU4j2+jN2bgvToLUry4juwfblHG1DkDhCJpE3Pd9GY/UvEWKucolqNGvCUwwMBkgEWg0GQ6vsHxrVfxHnyaMOKoEV1nqewRHw+gskd02SMWDCpJ'
        b'g5LFjAhtYPH6KQyVc1jYQn6A68PryPZKa7EDt6A2KgWMj8jUM9hS3OINHPZ0fJUS5EpGx+EAEOUB4yrFTSG4VoDW+uITNNcxlviIyhxfHm3LMmTDRHZ5qDGMI3W9PdqH'
        b'aiui4vEFMqrwJgbXzS7kJIsgi7oJ71Atvi0hL2sAkXUjkJIjQg2omb7cjlsg1c0M3lWAa6n8DJ0uIEUHKxjhdlqzLdQIRgBeQ7Ndgk6ZqZZY4Uswu7HoBIMPVvLIYQU6'
        b'4KJCW1EN3h8FFNUxJNZ5vJbbSVyKR/vJh+gaIqOcRScZMnz2FtBC5uIGWzJzWORmM+TNOTJNo3puH+GfjOpVSxZnkHmXvKkHvMkWdJF+lIZOTiOv4peSrNA+hlT/WnyM'
        b'7nuCSd23km1PMr48r/e+Z6cd4Ymf4yALeGJeIMLr/agIv9g12FjFhDyiGwMwrw8bg7Khuo1BqNojtNWm1bPdIxI2Bs47x3V6BDRXqj0i6pK+sHWuX8mbZVii8Yjp9PVv'
        b'Tez0kbdGkQ2CW/Qfo2Oue18rvFNyveRmcLeQsXf+wsG103voyZFHRzZnn5/ZMvOab3vgeI13bL2008O7cUXDioOr6kUkfX4/ItV4jGt3HPfIhHF065YyQ7yasjX28gd2'
        b'jp32nvQWnIks27ms3SdS4xCp/06k8Yhqd4wC/75ODU5N8zROgf2+LNI4BfR6SYh1Dnxo77R/+s7p7V7RGvtorZeTnjEf9kqX+6ppqMber9NlGG9VN0HjEtZuF/byL301'
        b'9sN6vfzzEI/OiBFXR18afVf0tulbpl0R47rFAs9YskMDzwLdjGBwHGuwm5JwJgwsDDl/JfWN1wO1LmG0JgW5DdU0iAMeqd7U4tbBouBqsqGSv/Beykb5ioDzB1K5tKRQ'
        b'xTnuAE8dXVaGvrqLlMo/c/EKysvmlRQrTSHeQ3pcnDuvZGlRIed53CK3RJVbWL6oSFVZUqD8Cah9AJHMqEdwVUV+QZFSwz3Qa1qJc2FnAH7Tq0oKtfohwHcpfw86y059'
        b'WcftEuVmpmSQzONzsrISM+JTEhWcpUWd1dwu84r8kjLeDIKynWaqV/7nTr519iKUv4cLtQ/xL2PrulRJgJ4v030srXtqYtf5/wOBK0z6A4hYlWsE/AUsrqpmcR47uq0Y'
        b'F/cmRavwWsTdArXtxBqQxzi4NkW1iq/lvOPbOcSl1+0jE5GLVU3qDxZCy4AnZmMtC0i/huuj8QLqdkL+nZB1CahJ/RScScg77caCx4nxnMcJZ68H1kGddnHkkXMCWzNR'
        b'79cjEtxuDKdeN3hPFYnwXRJr6GQD/F7Yx3F+KXgPF+Auw2UU9XDBu7MAtxuO42qSn0gHWUY+kjFOnmrHkKOjjo8mPzUpP4hYy1CwUOwKl2gyj8Wy8ewTYTVr6faE0V+/'
        b'o9dvlULGyr7BW23p/kTgYinvZsjlO/LMoxuC30bD22y1pdcPgtGWcSy88f6O3nL2j6nG8tkItMXYLOsUtJUwGM5JohK0Dq0x2ntozah/txEMH9uBKpGx6WOlCMwecyaP'
        b'g0W80WPuHkwfm5G/cA8mkMEAMvdcfz9YYaOwVdjRe3vFEN29g8KR3DvRe2eFi8JV4RZsrhTPkuRIIlmFOxyZ6Iz5muhM/rIKC3KF/1Ly30b7X+ExysSdcWcUcl7oIVTI'
        b'ehgEls6S6Ewhe48SKE31aZL/5uS/IFLAp2fL/1rDb6j+uQ2fN/zC92aRIoWPwpfP2x+MPkPuOaY5ljk2OXaRUs5csgEVZtQ0soQaQR0cKeFNKJsr/JQWOUwMq7SkRhMC'
        b'umxggY6nTo2pSfB5RcoS8Au33Nms9xvO76PZ02Cy3YwuUZVHqyoL6W94aGh4eDTsUqOXqgqjYVoKDg0NI//JfjdCLuwSZWRmpXeJklOSkrtEOVlJk1rYLkFCIrmaQja5'
        b'mRlp01tEStiodInpKUqXKeeiuoTciueV5herXiTbMMhWpFwIcxk4JFEuAmPMopQMBecF4QXTGiUX90hLWU0TVCRMiX0aN7+ysiI6JKS6ujpYVbI0CPbrSrAAElTAmzYI'
        b'LihfFFJYFNKDwmCyqw8NDyb5yQX69FsE1Fqzsp4a/ugyTcuMj03LJdv6p0OB6Pi4FEoh+Z2Uvwz4qiwQsagqSaLBoZHkStYWSKyFVW7kvE4sBlotFCkZSWmJuXGx2fHJ'
        b'z5lUmFzI0aUr8tMRPT6MV5arVHH0vME4jbTy4nRVMU0pDFIS6FMiBK6GtAb1qI+nzv0X6ql9n5UnNzdKBbqbcl0faY9SboCnPRIZRROJUK6Hd/1nHvY04AVK2mVSWDQv'
        b'v6q0klY/bcv/lyY6BlZo5aD4x9wk6MxywP5rgf/oUsmpqasEVNN1pGTpu68aa7r+9bf9aLp2SXOV5VWVpN9zTk2MJ5Fg7UsjpdflcsJ7v6B2I3hFUW4nlxixgXZjtfxn'
        b'aDe2mHDs0u/64JnatYyTkQqkmbYi1zBaWXgfKpAsVXgEe9TUEnWkmU690eKXVW/M30XqwCyFs5VSsrzI4KSec1nPiXRhEjc4mVdUVVSUK+FQs4K6v6WcpCrazCxI1mNQ'
        b'yfwSEuXGj2EQ9noySubnryoBee+SEcHD/fv4hBu3Mr/45N4v+fEILwNlPdPpf26Q+aVkPzNGmEGM5x3G8ElPIrRCCP5gmDtx5czJFBbNrQRf8LyzTW1MWMu4aD2boUJZ'
        b'Uq4sqVzGOYPx84cV0p9kCGukP3cu7g8rJTyDdcsfhBD+sOD4y4P1Iv/hweHBodF8FO4zPRoglL7iU9E/Hk4fc0lpCeUsYPGk9mHXiivfMBU1baUrHt1AcbIYnSiGdrq+'
        b'rU/xdn10eepNSHEZc/21p3UosMikA2gUclIdcl8FwiaQ29DzfQr+KMqvhAYlRC7raYwL4A0lnGwGZALku+p8JY8NMXCWSksnUxQVAe1VpUWy/ErCg8ytquSyjY/NTkzK'
        b'zJqeC37JMxWJueBKWkGp0OE4qKEila6Q3KDiyked0PPW37T1qj0c4aUVHCxCL7GgUibuC72Awb/HmPLXAUNoDVZw/VpFC90j7ih/jlptlJIy+h1v/opwW5xQA6AgZbLE'
        b'nCxeklImU1SXVC4vUpbSiqx8BjHcAOf7IulwKZX5pctoxP5HsL++T/B2uLgK05vngp7EV5nOVBcn9OMprORwKgbekoziGpln043SvqVEpHj8Eq7Sdo8e6XB1RhlUw56W'
        b'EhebIZtbVFpeVgxf9pC+mPZae60zuKP7G3g3ajPBR/DuVLwd1wkZAT7O+i3CWzkxwnp0xJ/TSR+5lMOqoKOIx6rQA/Sts/FOas+ftcbHqD3/hbiBqheyQhN0pBA2aWgr'
        b'vgoQF7RZxFjiDQJci84GVVFtkNdRc1hJlV5JIpthbPAxIQJ9411UhWyyT4FiQPv3i1aRtLbhq2amC8bLBZT0VWitwxj0KhUiaEUIm/EFynFkoVvLpqEN5pZKreBhMz5A'
        b'1XEtV6CT2vNqb7QlYLKBqrNO47LC0jIL3B74BWXk+PnhLXhrCN4SCHbqOTv+QXCSu9+WnY62TuAEKxfRCTFndJ9FN82ozf2p6DSVf+FUCdmgPhSYyPLSxjnNZKrGMNRY'
        b'9p1wQ0P8ycH4+ryJ6XgzKXZIFq5Jm5wszCLlgb/X0evLfBl0R2SO6/PwtpLxwgMi1QOSyolPv15Ud8FmXajFRkXgniufHXv7+tIvv/rs8wvNX9qOVIcutvr4L582nRm7'
        b'+R8L/Yd8PnGfz493fNIzvrb0HYmZDxLrvmwO+7W19x6/cPWpheP3qrq/kVvGL2tqvpDwue31x39Myxs6vf3Xlsejo1D3j+ZN0Qq7IfcymqcwRff/ol76yc7f3pXu+fAf'
        b'S3/d1eESv+iz8v0PmmoTbr2e+2QWe7BxiW/0N/f9sgep1cNrZ/+QdKJyRMPvk660n2srCHhv4Q3lbcejb6Zdv1Xw9cK/C7KvP/7g78OWt86+/48cTfayn5j/zPGa/MhK'
        b'bsnpNNzCJyMCgoOSg9Au3Aj4ldcEoaUjqPTBL2gK5+cEXLUEAg7HhPHFx62yhGF28fRAf04Ufh0dRDcNjvwpoqYplTMMvgcfwBt7wICWJQjwvukTKBBIgm4vpkggAdqR'
        b'B/KHM+Xcof6G4iJDrR/cEgtqP0NdOKnIoXi0yQJv7kMBatJQLuM7K/Ba3r41d66fhs/Ro/2UmMfDgAVDt43sZJ9FNXpb2ZylbLwLH+NsZTejLXPwziRjE+dg4BwdVdHj'
        b'edmq0lA3A70pFh1MWUXFBBkFaIfUiWQEg/cSeZnOTsBv4DpOTFBHaNhI5ow0qIDmSXPZMLwGr5FbvNSZG5zUGIJRDcwv98nP/x/23gMuqitt4L7TaENTeh+QNsDQURBQ'
        b'6b03sSBIV4owoFixKygKKgIKAioyWAKICNjAc1JMlckkGdTEuEk2ySYm0ZCNSTbR75xzZ3BQs7vZ3e993+/37a4Zbj33lOec+zznnuf/KEKYOfTM/g85jtQM/XF9e5G1'
        b'WNt72GDM+obSeHzKhE/wWN6Ngh9YjBkL8fJwY/N2kxaTeqUJI4uO2WIjfj0Hz8+/wONBx+DpQmoDq44iiYH7R+b2E95+oxpXNMDqByyGQxxZJxRP1gnFM+4ZmIxbuEgM'
        b'XPDiforhQJYUPUSXhZHLwsll4YzPTXgT9oJmdqvGhJNbM/s9Q/7nOobNoVJTgdhUIMqVmnqKTT3v4Q8Bpk1LGpZ0WHW4jevZ0KHLJXruw3NGfUd9FUHSD1iUXxhjXM9d'
        b'wZbRUFiJ/HcNjN9fcoQj0E1bJ6xA6MVR22KwBYTHLLIqOM0BU3l//KNsXgLl61Ryo/q5fv8amldGdl3O+v3wpy+SIDmctw6VorwHX0oAnc7/hNr8LDoXzzUlhQck3mYH'
        b'hwQm32YHJYYE85VftAq83A2bj9lkzj+7IKs8P1c4zcDTkpe5Fv3MU/ldxg0m3CinaCIDD5t6WoRlo50yw1Pr/xWSTR4y9W5gUy8gJwfpd4oLdeWqygvm7aaUTDWk7MzF'
        b'Ku3czKmvE5kvWAvjJFPxpqideGUwQXYqPjAbqYjLkeqM7PmninQFrsoKmZnwQoNJpmrTLfsCm4mOLU5fq/g4+jgvS8jLKyrNwlMISOkuREdKKouX55bLF2qhTMlNXKyt'
        b'yReZBZC7M6eeMs3wUHyM3OyoyK2itXJcKpo+WkyvUpYtO0bHCnOwivq0KFORyGV54tmjjJSTrBKV1Cox1NnZ2YovU47p5T9kiXoWbk1hRXlldkUlSu1pSs68UPnqM4Xz'
        b'5P6pa4gkVK4qypU3iWwpHtK+ceaRwl+MqoLcY58YEhqCvyeFLItNiQkMSXTiyW2Z5JCFyfyp+skla9Rx5eSW5AgqSgXoj0L57EtX0WvuFe6oepE5h47mluO1+Yrm3LTb'
        b'cbamrDtcI3/POOPJKa4yqSF3F5QWIXP+xXYbD5UqJDE2IPp5m41exv47dps8zjRdFLTHw3tEIGTthuUMmaqoXVADZWbGlpbgnqOwPr+q4mnq+GZ8FzIT8Jp53GGmRCOv'
        b'vLQYFTUnS7awvqiSnr7JL1ydWyKXJCTKOXiZmH12aYmwEBUX34kKXkiOolqZejB9m6IRz1fMNp2V0uUrcrMr6P5Cm0FJcd6zXd2IsKDKI/nDz3CS4b9l+SdWN5Zl1OnJ'
        b'fXmV5UQ2SW8ga/+f2nL0sDqXlySzrYS8NQWFyDzDrgNrUSpFyDjPzSqnLSz6YrpvCYWlyKSvkD2KXl1aXooEnSw2RVUhq3wkWLQY0YV/2oudebHIpstataqoMJss0MRG'
        b'L5FHRdcGWvaC6D6TJevkKHX8BuHZo1++Ew+/R3j2cSmJfFxZ+H3Csw8MiZXJrYOC78VsvoOawmq8gKmh55mAq4qrWv+BgWgRS0BU9tYsGZMsfDmx/+zKiWpBbJfN65Wp'
        b'In+k9PIyi9b68Sli7LDWIqvrCrhIW4XEJISXwXAoWQtW5Awuy3FcXtkYL9aeTNPFaoBo3hTCKxOcosBhpNeOJNOomhNGKdMtSXBER25MphsQd4i1sHUO3COLGIYj0iXL'
        b'eDRRAofUcKfIlOn2o3fg9AhqGPTVGzIDqbvD2cRItFgHB2nrMWIxbT/C7uLKFHSm2gmI/sCTnAh8SRYospzhmGA/hSjiK1FzXXVhHzzmR5vTHXngJWyW+oLdMsu0GR6v'
        b'xGHZwQ52URShtwki4zDdiE6Fg1T9HWo2RqBH7ak5uABuga3YBpgJdoCTyaAjJwHUBG4CR8BWcAb9/wT6u3NlFdLhTwUuzwC1geWFucyEhBUZ5TZLQMvKAm0K7vM3Ba3r'
        b'4WnSpIkWNlx4cZU6PAwvMykmvMJwQVbHFVIZqnAw83fzBWuMQM0C0LAciYRihnaAQWRdHYeH8D5et5epBXfxKHA2YYYhHAKHiaxYLgVXuKtVhbBGlV436ADaKzFnFZzK'
        b'SJ5aVMZPlaHaVlVWJsP6VRpa8ECyrNbDU8GRp/Y7Nttx68hpTnKmGdgCRCroOWxKE+7Wx4FruJXzsUh2gpdAP4HpoYtD576QpYdvTJ7WoHAQ7NIIWx1ZGYrTOAo6LKMU'
        b'44XWgbPxSGbQQ3euSkbpRhG6FBKmgxxhJKidiYS7Fh5MRNZVLQOOlmmEwSvRldG41MehqHh6Uh6gC6UW/jRWUuq0BMEOLjikawNP6YFu0KWvx6JAS8wM0KWzvHIeStAF'
        b'iUotKd70MjFhpzHsQPbvXnjBD7XPVrgdVTBZQwkOLKfgrkT1RK/iyjiKzA+dBYcUQkRGR/AjBc4vCqQnz5TG9P6C6qutMnL2TNAAu/0rU7HaiUS+R84MSgj/N9J2N1ai'
        b'EiN1wZUSeIEeZLagFm2D50PlczF4IkYXvkQWxJCFBepIcp+NEWkFBsFlcJkFrqnBYziafeEx+7Uc4WNkX7TrvtGYEhMHFmi3Hd70IIWrq/3KTwF+ohrzvabbv7wVrHPg'
        b'29mWluau67a9WvVQq+r7TyKqewe4iy9963w9Q8239O56D9/LVzVGt8xet+DMhYmhLfPt9hj4hVEXbmS/bfhe2L0vnErOPJxIke4OKWpoYn6+9siV47Za4de3vHe80SvB'
        b'5Oc3jv4cfvbaYEVCR8rSypcj1NJ+1E6QMB8Lk/J1bfQfKmUv4Vtui9nw+GiI+809hpWv1l03+97nS7f4n39581GdzS++GgzN6yffGVmSGJl5o09Z9GWer4TRvN3o4t5K'
        b'afI+4f1zou9fCYwOOpH0J6/WiPt6NVePfKriof6V+Nxw7ktC83131Y8wpH4ZJ0YaJerh3lVhV/aKzmmfWLwttu3rJZ9VPu7zLJ/bOHyu3PDXkMRl73u6+Uc/1JtoXZP8'
        b'lsRLeGr/w9q4W63Odi/B9NVva3bPO2627eNTn6WdCPtQuXm10baMkAHWOb38Eotqa4NlVJXDwm/tfnkSt+vOu+/cP9dz+Z2WR3Py7h5e13m5+oOeyusVK4u/7ZjlM976'
        b'4U/hS2f5WjlObp2jpZFYmnPwo/eO/sA+cLhg8uGxSk7pt7s/KGjbWSN9ZCB+rzvgk5vH1a+ObHvpk3uJcxd7vZM37+HZNYJfj134NElv1rcanVvMB+6EzD+Ys7/dpdpt'
        b'cIC364OYn9Tq8ktS9b6uqVbv2r+s63HF7dckfH0ykaSkBrYrTvhopcJ+c1aRFqgnUzB82E97SXWXPeNRBut16NB4TWAnPJVpSs8mrWYEgF3gKB1m7CocRkMdaAmcvoQW'
        b'1pTTTmEnYd96evKmAA7L52/g6TSyvjIQXCxA77PDsI+OzKcYlg+MAhF5hH3ODDxBNoKGrWnR/3LBAXo66nBKznOTVdxYtoo5GKbpIXXwILwgn0UzhGflE2lb15BpJAEU'
        b'pZMAp9VwUL4gFxyEw3QBWuFZUIMB8hHgLDt1PqVUxLQC++BOMsUWATfPqF5Ex9AjEKGuUJpRszsJh0ZTmCLTBCL0Th5kBYP94DJBzRtYzwJHfV8UTo6eIiuQRR/UB/sA'
        b'nvsGrVnkdSKnn9go0at3T5bMRGedQA/Y68Wm2E4McCm1jNSMyjK3Z6fV4HYVdgboh410ELiLYBhsJROUTHBGlZ6fBE0VP9iik6Y2sCsqOgLUTPkHgn4kBrI1sK5gWMlF'
        b'BzTSyBpRMVKP8Ewken3FIUVFM9hJyPKHW6zoOrwAm9bJIgPCJniIdv6DO1PpSdK+ReA02OMSI+Az4REOpeTP5BmBa3yD/401dThDvwMweepsftvqBRM1L6KVOLJojnie'
        b'AIddsxXZSg3cxAZut8xmdYSKgntjemIw9SP03osn9njW3eqd6lKem5jnRoAkPK96jQlLe4UwY/Wa96ztpdaeYmtPqbW32Np72ExiHTaubTmhY9Q0v2G+yGvcPWjcIVii'
        b'E3zPyq4hakLPqiNHoucg2jSmK3EJuWdl2xD1QImydhPPCqyPwuwNlxYXibGj1Di8T2lIq19rzEvsGl6v/IAnD1N2cc2HxtYPKIbtbDzDyB3hPmQxbINJTLMQEtMshEHD'
        b'HXwafDqUJDq2d02sZPOMAWR6MZBMLwYyPjeZJYspdsKvWeWneworb5/ekkpuSSO3pDHuGZij8zL4iQzm8oBFGfLRE/WNn95uYC67PYTcHkpuD2VgsIRvuy+NTpGYJ4wb'
        b'JsgnT1PGnfzHredJdOahpAxNmzY2bBQbuPal0TwPiVfMPZ6gT1fC8xq2ls6NQv8+iF9MAB8pEqvUcdNUHFgO3SPivGsg6HMc05UGJIoDEiXuieRhMiTM5wbmp9b3bZTM'
        b'SZ1QyEm0xDxm3DBmwnRWe1x7XJ/ykPqQuiz7gST7QST7QYx7prz26JZoqakr+teXPLSkf4nUKxT9e+HVD9RwI/g2+Ep1+GIdvshGquMq1nGdsLBtCL9nYVkf/pme8biJ'
        b'QFQh1gseS7uRN566dHxZ9kRI/HjiovElOZMshn4eo56JqsPCtp55iItraiq1cQe04SfW8btraY/kOKInYlhf4jT/loVVhyfdohIL1/rAQ+GEFILj6InUJTqeE/YeOBCd'
        b'zYSs1qMlKEPWjvXBh2LuGRjVqyrMC8/8XULF07nJctHzy6X/mT6OOU3PgyUUWBLX0U89RzGu21InBiOR8CMScS2j3z8yd4xt11NKs6mL3ADG9MljJblVi2PLz1Mi653o'
        b'xYnKKSoplKfS1Monzn925dO6BWqJuSU5ueXCfzQvSiaVZIY7nibJEvIWxkQ/Y52bU89a5/xYwmuGx0BPcNRTf/OEZ2G8e9JWBNs/R5KHreCchh66tJbEoobbwdFcudYL'
        b'tsFzCpov0npzwDViEBdXumG9GRyAjXLdeY47gQSkGINT+FSFM1IFziElwXk1+onEjjLWGZw5sAtuJeatAWyzx3o1bIAtKAlzCtRngS3kQ/RMZNJvlX+Eht069HdoeAV0'
        b'0TMN8SwqeAX5FhH9xdw59EwDsjzBCGFxU8YrKAY8RoFRJdhHuNoucKsT9qhDGx2LKBfQqUtuyQe9sIGrWg7r3TDRtgdPTlyFJ2jsam04bHfkO8Rw4CWwnWKvZSAzuh/s'
        b'oE9uQa/Zq1GuYADrQrHoParPVF8HGkiqQli3OAnWsQms7zwYxFTvS3AHKdgy0AbaaYQuSqMFY3SxF/4JcJle/NYEG8AB8iUa1KcQk19fhfgZBqMaaaW96oZQuum0V10c'
        b'aJZRJHgzaOe/85wZocQbD54EW2l3wlaNdDxbwgZdyRQqpsNSeIXctGAB6JF9EEcXbyGTGnpwOz3FchmZebuSkDZ3KAXWwSO6sBEzelXiGPACPLGGtML1sH1UxXo/JuWa'
        b'GfuKSTg9CdRqNItaoIk/VWQGaswIow9+mBdBvcfhMdBIsCI8WJ0+eFZbg6oqcqWo+Eyn0wHR9MEnhfrUPfOFeA5pg0OUA0Vnpl8HqbG4eJhMbARrFOHE3uZEmFigTYPM'
        b'SjDhtUp6UkIATpNTEVpwBJ0q02A5gV6KpcvwBQfAaTpjG5Woe5QZmbKK9F2G4+aQiZezSHIHSDNwc0kroHbcQwN326rACJ6HYMPmUDIPAeodSHWar4cnyU3KcAgep1i2'
        b'qA164CCfQWbOEoJBvzAWvORSzqaYXAYPbp5J7uIgG1TEXQ0vajFT4T6coDdS6E/SzzrAh3u45UhswYgDEhTQMh+JGD4j1AG74YA6vMjIU0YydBDJ0NpyGhU/BGpKMEMn'
        b'YQVspRJgPThCisSEtbO49g6OsD8aA/G6Z0UyFwlVCIAYnJkHauFAMtjhEgmH0GkO2MaAh1EHPF/YVd/EERaj4bk0e83b6b+tNA0xPHbnw0cZ5ct+Hra9WCM9efFwcsj+'
        b'i/z+QL7PScvcz1Oz9+zIXMF5U09VL7jWwv54h8pM3YatW3dv3RqewA8JDtYNnhHwa4Q2u/ph9apvV68uLfk4/6Kw8NcbLuvX/rix/YuW/W0tax59+4Ptyjpp+pkPwvu+'
        b'/TjjCfhg6auxjnvdGlS+bY+5sOLDrM/2d9vbtvLOvK10w1htQEkcuTN9X9PCaPY3C++8NrE3wp9VlcjY/2rDX1ZVxT54sukD85mFb609+SmP/13uX/zrys6/2fxe/dbv'
        b'W7rXHimJzLn9l9TBd4JnF5We8rptFJDR0ZIV/cHX/I9Ac9O5o7+cDHdr4FYF23YNfH5lie+o+9e5a1vyIi6omYa0RWi2D7aVvn+6qGf816WPV/s37W8ZuLPj/clJ+P2R'
        b'ef4zvhrZsGvH3QdfdZXkvfrmJP/LdXbB3YyvvjfqaFYRrpZctur9qP3Eoz+L7neKZse1vuM3o0Qr/VFD4I2jX75tICi94Pvp+Q0WDzzv630uOTJZtfO3zVkvm3ybHV74'
        b'+NeRd7S/WPfW2e9CBDYf7HP4Zq1x/qrFyW8pb77zCRi5Nu/q0v6PA7I11Lt22Bo2zjRqdL/fUFX621sBb37HFtz8XilEsHZjdcgnwzO9NV9SurZie2noz34FXycln4jc'
        b'2bAk+Wrl7vKChCGH32Zd/KXZ7aueBnUffYbHnh/b57D9zDgtzqO7jv9q+MrLBe8dPOXzfsoww/kv33qvavpzlG6j/wfsuY8So4/62n/KfuWXYz9mn/44dbPHxrf2n2nZ'
        b'4hn7auHZb1LUtobemlS1ffXA1WMXKj84X756dNBjTO1ju7Y6k1bOr1oLJ9u3/qoTsVHTv+BtpVevfaEz78mu5b98r/7K6fvXGjS+mH3xT8npwtZ+bvX3XsZ/rvth/92I'
        b'/JFXmx0bZ7f+GB7U5moSOwF2UWGH23d86VNr/Ov8QLc3U8oi6z49Ef/1BvXS3hiDjr+9Rp1uF2k5/FmjeeOMX/qLLotqzCLeZd1eN2TkYWDevfDLn5M/4zcnFVeB24JM'
        b'5cfMu3ZD29bkLnJfevzRwys6B3O+q33npO6tcz+U+Z+4Mp9z9U4rf8mTk2HJpuXfNr+7fHVldqL156e+9En4VhiXZJDl+NHjJ3dCbjb+NfjS2pDHzpWnl/S+3O71xZ42'
        b'7pnEyy+rlxl0nVk9sjSdz137itvpAz1VIUHFD/2Cl23+cg8leNj0lqDexwW2ptlHvrPx4Koh7/FvHs2s9tpnuWRPxraveHNMByw7fL65qTz8VWPx6RzB4zThRw/mn9Yo'
        b'+bVi9IzwPqdUZ4HTQzeN2F+fvJ3u26zxy+kK8NUP1d6n5n24qf1q2Z3tb/WyLrz8cYd9tWTuzPtfLv+8T2fo4mvHTMYcXBo/Pl4giv+k6S9LXR3vKr3Vd2xs78mmqF/N'
        b'jHf8GPP2mx5vvHl5nDv3Ty+nlbt9wVlfva3NQOkLzuSk/9hKY+5J/aQ7Ru4XBy96FBSNXBz44nJGcX7m7fLi/JtDg7ffGRt95fY7m+4Xr/Bl3RlNu3NVy1tJ9I36Y8GK'
        b'y1/7RVnER399+fJ7BdUqG2/P/3QB56e/2X8Q1fdjtfrVzW36Hlv17uvUL/7gkIvjnx3jf07avUlTfObi3VfefjnfaNPB09tKI3L//Mh498caK35w2XzGveYMtcMlIM/m'
        b'SM83IQF30/rXXh8cf/Jk79kLh+dPtp/vAt9bPHZxuTmq9M1b4Y2lmyMPV0clrLX9277jt9V/Nv9s7/uvN1l8OrS/4uMmruRRXbT1V8pfPmnfsLL2btON0163ap403N2T'
        b'zK7+eZnpnxx+PWq8dviT9zV+3Xbpvh9vuf4HocKTtrc8bhzdf21dlt/nGuI4XcmhT92rTy387rclFzLu1q67f8lVd+MKuFJ3//3id98Mbls7cjfpqz//5NIh+Gqu45rw'
        b'6qYNC//WuP7bUnfLt/kl8fwiMmlhAttmcx3Q67cPbH1hfLyadTQFdiNsUnRVbowgkOTDYBeZmTBQAV1kamJ1+vQ1PyOwg8zZJGyA16JgXRQ6u5cpu0DLlZW/CRwkCZTF'
        b'g0b5/Ao8FPXUu9gGthB6sVa1kJyPgC+9cHYFKVVNZKpGCBsr8ZUYGAt2gXqBc3g00p70o9kaSJG8RuZJrMEFUONoZzQFUcYI5bWwgbCG52fDfUJaw4UDYHcMmQTTgKOs'
        b'BUiFuUQWRIFTjkwh7AZtzigLgvJYPo6dNEAWfsEaFuUJzygleYEuMh1SLPRG+vJC+Wya0jKmAzgC9tBzPYfBGaTfRTswwYASxVzKmAOvgu30LMqxYG/HykRY44J0a5zD'
        b'/UybpfAkmX/hR4DthD5LyLO6cAuBz9aARnrBVxscgWe5cLcA9sO9USxK2RZtXGDGwYvwMj2b1VcFW+UXrAS7o+AAeiVrgN1Ip6mG/fRU0lVdsIXG9yfBoxR7NgNpcqOg'
        b'hWQgdRm4TN8viMChBDp81Jhp4CLsJG05jx2EXvwOEXDfKuL6vj9WmdIGfawKcG0ZSTsODGdFgR6whSCakIICrzJZ1XALyX4RuAiuQKT0no/jgh57Jbjfn1KFQ0zQVQiP'
        b'EFkE23JihJhOrYqaiAMa5lFqcB8T7pnlTx5fmgS34Myp8uEOuBn2kTrQAFdYOu5JZPbTd30ymR7kqJrLZgfZ8DR59np4OQE2gSO4LR2d+Wr2DqCHTc00ZMHN1uUk65l+'
        b'JlznKHgRaU244FfBKU3mYrA3gbCQBakJwlgcdqixGqtSIngNdJMKR5bQZrhZGQ6g4uI6J2xtDjVDnwVaNMEJco1+INgRFesEalzsc+EWOjQJhzIBW9ng1GrQQ54ODuoi'
        b'2XSOAL3qJmb2AgeK0lRizXcso0Hn5/LAfm6kILoMnHOF58KRaAr5DMoomR0GtnFJBjU2gj34GDIuUDauIZ1vvTdJ2Bge9orix4C6OJP5hPGsCQ6x/PQySWubg2OVhBC9'
        b'0lXGiCaAaOdMkibczZsnjHDgM+2ykYZ8iAHq8oxpCa4B2/VQTe7hIPWxH2zmUuBKFBwkTagJDvKfUho4yCyiQQ0742nh60L2zGYZPTo4kmKbM8BxL3iMtK8b2A7aomTf'
        b'4sBpNjjKpOnRqIrp2csh0JfJtUflL4vmM2epIvE4wgSXwUUHki8v2FyFixMjYFCqKfC0GxM0w5oS+sHbQaMy15nvgENXoHGuCJ4qZBbq5ZN0I0oNHFGroOo/Bc/SwSe0'
        b'QB1rub8x6cx58Fg113StvXNZLNZvuxmwHdRuIsk6uYN+rlsAH3UGUh8c2MyAgz7LSX64YBAeoGd82bOy6QlfcCCZXtp5CQdlQcKOymmEzDwWrMHxMg6Gkju94Tb3KPoj'
        b'ldJsuJXiRjJh9yIBGXBXgGZ3YTQfnicsdJSdMEpNnQk6QKsm3Ykug70RuN3Kwc6g6Fhn1P9dWCqgE14gfcQedq0nowIFT3HgMAVeigb76XWYNfCAOjKOyuEFlivYRjHB'
        b'NYZJeArd5DvBSK5saWf8QtnHgVVBRE5iosKwcYKGvF20ebIC7KbBEgNgJ4d8zgBdrKkvGqwi9EraRjeKKNSK5DTahQH2pFFqC5igpxqNZSQsyEiojhDj3HGfnbnUEc85'
        b'4HzrooEYNtmgZ/Ao/GGiAYff2sdXAy85xc1AI2FdDDyPLjPSZjuACzTpfFUmxuy4wnr5SU4qAw1gvXAnHXugMw0PS7XRxRvojwNghF5/GwFFQCT0B93wfMVqOMCm2DMY'
        b'GbAO9BGx2IjHRfzRMx6eU6IY4BgF96fSAoUsvm4hHHCBNfZM2IGMbhY8hi5IBW10b78It65CmbaPXOPApJRzqsFBpg+4RH+RAL2wLQgv2I5D7wfQhaz6GixAlBaTlcOT'
        b'vXThPvSES46yOEccuBVuJ4FdXMAhOgxzj66RkLy8QBfcgUZb2WBpCM6w3cBOOErP9h90DOaCYXsy3hPT7SgS7ZWA/prhmuIhGy1xlcFufdTbBpFMRAYROaqGmzFSBO6P'
        b'ToLbGRQzlSEIW0YzCEUcNyFqblVYEwMurkFbJHUdeJAF2ktQV8YCtRBcBb0kVowQXiHDwAm4FdBRGxaYI8tzjy9sJl8ayGcG2ITeXkQQz5qAem6lhiqSFGSjsiwZAfA0'
        b'3EfjWs7BHl8h3CuAfXNRjnQZs2D/RjKCVqA36SBdmgg0/DSWoYvwq7+HZRMOD9JV2jAnZiruGXoDJKOKx4F04FFVohlkwDYuKu4V9PbCUaZqY5z4ETFoTJdFevD2UwLH'
        b'lWVv0Wh43E32kUVlvuwzC8s/Ew1z2A2BwUcihD8yPxfK5ikPHzSYUinwJRUXeBCeIkXwjXYHe8BeLrlYUIbHZWoG6qmo3vaCU6QIQbDBBT0Wj76gFrTSBdFMYsUs0Cdi'
        b't8wZHkdSQbrbEtBKqYUwwekNSGPBFWtSAg7ik0wWPIeG+8MMsA9pBXW0OB+EjXAbuRVcNaTHFC+WqidSmrAGB3YagLppVP/14OhTsP9mTp5SPslglV10wWp5CfCzUAku'
        b'ssBJcHAlwTvisBVnkVSDBnDJ4flYQHDYk3S8mXxtLn5HZsIzqGMNMZAcdiOhJcPqRZ1lXFgrV5BUbIQUMwH1wFFSxrmgVx+9AyIZ8LwGuvMCDvt1EYrobncK1mvgIqpB'
        b'EdwZGYOlBaWgC7az4O7lSj/gSWfzPCsuHzVgpa4xhVSQc+r0Z802NIjrIQUB9rsgxYJ89tNewQK1JvAQyZQqPOUPB5ycnZnwGBChB7eglx5sh3vJl0k0kO+J5UbGLK1i'
        b'UUw+wxxcMqXHv2bURU4J0VsA1qiuhDuflsoQ1rPnzmCQutBZjJSpPaBWgItFKZkzdUAb7KLr4piwmIQQjBU4IIF28cfd9zDcGk2EIRLu8hK6OMC+cNQMykgjvgSuMMO9'
        b'55OelGueAwfi9ASx9JTORgZsjFehddDGFSw6JIMQNE2PymAQTIRlPdJ8dwqdIyv5aADgsEEXpcZkgkNgy1wiA3qB0TKFOmIBOKZlj4c2DTjC8kmi3zSVaDCdchTIBruJ'
        b'r4AP/aZJh0fBvijnGD7YhwbqtQw/cFqFnIj1xCrFvmjYaI86/nKGG9hXQb9h6lEnfIpaylYmpCV3TCv5XyWC4PbhPf8/xZgLSuVk2v+20Qs+YdKnyJfLdVz6y+UGVxIB'
        b'GRN+PjS2HbeLlBhHjetGYXKPSYuJ1MhFbOQy7hogMQqsV5rQN25a2bBSqu8k1ncSpUj0PepZE4am7dwWrtTQWWzoPO4yX2K4oJ4zYWgiNYzoYHdzO7lSnqeY59mXIuH5'
        b'omNjIS+r4vPmHdbdjp2OYkMB2qO/rUkNIkW5UueIYbbUO0LsHfEeP7Kefc+CV69+y8K2Y/XRarShy+vQ7bbotJDoutUzPtfRv2Vs0hzcHtUSJXNayJaYuve5iU29JMaz'
        b'64MmeLMaIu4Zm7Q7tDhMGBpJDR3Ehg4SQ6dJFtNEvz7ogRJlad0R0KlUH/GZuVV96MQsfrdfp9+JefXRE7o8sa5rffSHs9CTMUP/xCbJrNlPj0+Y2UrNBGIzgSirt6Cn'
        b'ACXertai1jG727fTV2LogvdVWlQ69I5q4U1UPx3B3ZGdkVJrn77ZUuvg4TSJYciEqUWrstQwsCOgO6IzQpTTt0TsHCCxDpQdD5Ydz+vbIHYOklgH3zMykxot6Eg9aYz+'
        b'YAT/ArHLgkeUppHxA/wzlvXaiusrJiytW9OkZn60l0Zfnpjv94himpmPWWKk7ATPulu1U1WUKuZ5SHnzhpWkvPAxW1QdQQxzVBvmVlIz747k7vTO9D5bsY03uXM4a7Rg'
        b'pGCCZ9nN7mQrnJTaBA2nSm1ixlZLeLEoifnmD7RRCu3pLekiW7GZq9Q0ri9raGX/SvRo6+vWY6uhk2R2HGqS1jCp6TIRW2rvLbb3RpvDCaOLRhbdYNxkv86+kSyNWSqO'
        b'WSoJz5D4L5s00QxjGD8wp4yM2zVaNFBLVPfpPaIYdlEMeX5S6bAd/mIb/+EVEpsICS/yEYtpF8y4Z2GDozZILeaILeYMq0ksgiY5LFRVKjgxpRalCVOz9uCWYCROpp2m'
        b'Ukt3saW7xNRjYuoTrNjU9RGlbGb+AP/0JQyl96dP8GylvFyRZ69fj5/UcZ7YcR7aHXN7zfu6943gm9GvR0ujl4mjl41nZo9nZY9H50iCcu/hWwrktywQOy5Au2MJr6Vd'
        b'T7uRfHPJ60ukMcvFMcvHs/PGc/LGY/IlIQXkKZEit945PXP6PIf8+v2kHsFij+CxpLHl4x4REsdIXHalTqWOCiyYUjtfsZ2vhOc3Ye1wUk3KyxtPSJEmLBUnLJUm5L6b'
        b'kCtxyUO/N3SHVPtVh62HhWPMYf4HrsHihFyxS96khvJs80mOOqoXY1wvSIZl9fLMM7zFdt4Sng9qZjNz0m1wI/qJGL2cHo4op7e4p1hi7zepykEJqeOEVFtUcUKoKlGD'
        b'S3lp6EqNHg0kD/n9+cM5o0UjRdJ5ceJ5cePxCeOJyePzUiSzUyX2aUjgLDMY9xxd6PryRf8esCgHVyk/pi9gKKw/bDh4NHokWuoXLfaLlnjGSPkF4wmJ0oRUcULqeNpi'
        b'aVq2OC1bmpYvTsuXJBT8NBEQ+Jr+dX2ZaCGhWiwJWDKpzDYzn2QpoaxqEx+sDp1HFJIMkWWvfY/9hJnlUwk2C+3LGyod40hNE2+EIrkzC2bgHqQl0pfyAvtmD83vn4+E'
        b'ytF4ciXDx0V/kvIxN6gP/WE1g7KwaWbieBnlhNQ8X5QlMXGZmO09tKJ/hdjUozm2J+yewK05dsLWvntF54q+GZ3FzWH3DM2JkGd1F3cW48oLawnDrYD7q1WvbY+thOeG'
        b'99U71UWJvWk9aVJByLCGhBdKBCZc5N7r3eONNoYZo0ojSsPlo1UjVRLvcFJc1Cjm1lKzSFHwWRX0Z1hX6hMp9ol8zyvyEaViZo5aQRq/SBy/aMLSptuo00iUJ7b0xG1h'
        b'NWw56jjiiCPpoKGoT19sPUdqHTgcKrWOHstDwuBrhYXBqlulU2XC2qY7uDOYHnfGZ4eK+aFSfvINz5s+r/tI+RnjCzMk1svQLZbkFhspz1XMc0WSgbrWov5FY4zX2NfZ'
        b'Y8nSkBRxSIpkQarEK21SSyUBDUszKTMeGYg6gul1MPSoNGPUeMQY14dapxrqLJ49nn1sqesCsesCiWOAhBeIHjUXi6qZeXtIS4j8Qvdenx4fqWOI2DHkhjvJWtRScdTS'
        b'DrVxXsYkSw3VlDFlZdttItJ5z1QgNQ3rsxyy77cfdh/1HfGVuIdNmJpLTT1QE0pNl6N65o5wxwJeC74efGOmNCJTHJEpCc6SeC9HV+FXUntcS9wjCtV+HwN3PlnbTdg4'
        b'di8TVUqtE1Hd2o3YjVnhgfk1l+sukrmJUuui8dQ0aepiceri8SUZ0iX54iX50iUrxUtWSlKLSO1Nsthu5g/UcLlCW0Llw2Bi9+LOxVIbL7GNl4Q3e4JnRb95PdA4j0Yx'
        b'VOf4B+VYdUQVjRNS63xROY5mI3UJELsEoF308ii4XnCjHIdRksZlieOyxpfnjmfnjsflSULz7+FbVshvCRK7BKFd1KuUX1cej0+Uxi8Wxy+WxueI43PGcwvG8wrG4wsl'
        b'4SvIg2JEZb1retb0lQ+t718vnRMmnhN2g3Vj5vicaIlLDJaZ0M5Q1Cq+Pb70iCqxnj9h73wSvSkLx1PSpCmZ4pRMaUrBuykFEo9C9HsjeSiiP2I4Z8xjLHC48APPcHFK'
        b'gdijEA1kPlZoICMNiKomsiVSVjXPPMNX7OgrsfaTV6UZqUoLWoPwQnqD1DSPlnlUIznXc5CQ+L7uK43KEUflSEJzJXPzcOOihpWaxqBmVepX6isbquivGA4cjRuJk6BS'
        b'ucbgvhveEj7Bc35EcS2t+tyGZvfPxtmI7oyesOf3snvYE06C3qieqAlXtyF2P7svdUAdZUjgjMRV4Ct1ChE7hYzlSJyipE5LSddMFcej4W2JJH4pGmL5Dqg38x3IyFsi'
        b'sfdH3cTGFvUSGyepdSjKk0a/xnC+xDV0Uo/raYVzMPuBPmVr153WmSZKk9h4TRppoPFvDSOCYWf8iIpgGJkgG8XC5mEAk7KY9SCPTc0wlmrzxNq8jhlIAwnvDJ/Q1WsK'
        b'awhDehYqt0TXCe9HNES0FB8tleg6y/aaczqWiM3dJLru8gN5HRvE5h4SXU98ILIhEitC7BZ2c3L7kpYlUjNnsZkz0ZRM29Vb1KWGfLEhX2Qlchs3FPTpDhn1G4kN5z6i'
        b'1IzMx7yurCUbsjfTLZ4l0h35nXxRcG90T7TUyV/s5D+8fLhs3ClAbBU4li22ipBapd4okFpljS/KQnVqY4slQFb1oiQ0bsoXV4WIvUKkgvQbujdNXzeVRqSLI9Il9osm'
        b'7B2l9ol97CH1fnV6SEG76KWdej31RghcioZ8G9tJZWUsQKqoKpU19PQnuTo2M3+gdGboPLSnZpg1J72nbTlhYNy0rmHdwQ3j2rN+/j6ITbnmM37+PpNJea5gCDWRDv6+'
        b'wCxggarzQxP0R9OVXhal+iL0z+/bA3jhUeY0/b/cjY1+3NGPqZKMx//zZupRpSuDMfN76g/SgU7RCK1leM0Upj3ylQjH6i8498mxsbF8Nvop78K8Lc0XYRzLGQxCREoK'
        b'Cg+JCUki4EaaXEScd9+Zgi+STGPuYnkNfoxeee3/lEWFzdYFv49XLGTJfjAXTrgHFefnndRDNlNDG/VCq0TGhJnXhCXSGhwfqnKscQwqcsx/wnLWs8dCyDGLqWN56Jhg'
        b'wlJAX+cwdd2zxyLRMVvyjLnomMvUMa9nji2m70XHnNGxBQx80FQwoe8+oS94WMjwMtTcHf6ghEFp6v/AxCREFtp6gLe+N8e4w7RxxzjxwsW3TCx6kkZ0rgsfshia0Yx7'
        b'oZETASGPWL4a2Gkc/05y8PEHbLz9cB2D0jW9pW03oRv8kMPUDWXsDv5ehaTWk9sfKsq4nv26lzghWZySLl60dDwyYzxk2S1jsx6PkVkj2detr1eN+8RPmHmgWzW9UD8N'
        b'ZaByRcQ9YoUxNYz/SuHfSWVyCm8+SmQHsjSsH1H49wH5pWmMZCrpss8iAmN0JoQKVb9lchcMJuW3SAnWgq3K09azcWV/J/MwkFHnnwAyspNUZdtqCttctK2epEG2NdG2'
        b'luy4tsK2DM7orDoFXtT7XfAi+4XgRX0Z/NBiCrxo8ELwoqExlWSUZPwfBC+a+CiRJ/OmsIsanpwk038AXDSTARfNFYCL2/mWt7UIEbmwPDe7Ijh3eWFF4Z/QGLXOQO2Z'
        b'w38QtehNY7rc+czb7KC4xJDbrED3wPIS3HNX4R+8mOmPpOWG0vpDoETZTd5/HIYofxzBBrlhGGL5eswPYBFsYfkGvBZdLTEkJi45hEAQrZ8BECYFByfmlk2Hd7mWb8IF'
        b'/mcudZsiBcoz8ovh76U6hQ+cnme+6rQ0cDuUB7AVGITyyikPwmN8ID71e89wK6/Fpf4/SA5kUs8uf+XQobTY4Bw8LHSB1+BFLXksA9jkSUc5OOExh7u6jEGg6pGusBV0'
        b'VBeu//oAU8hHZ1lB2RgpqA20Mbvf6Byj1crQcKaRkeG7LX1n4rPuRStTJ35h5/Hv8BlkSjJ5/mpHsBucJh+q5U4se/Fav2cRhOQNe9vwmU41HT2Ip64xejDHW3Ep/4QJ'
        b'T0771ub9K0DCSHRsprICkDDL+18AEpbvZ/0fBg5u5zOzyti/BxzMITWOiXHY4/yP0Abl3ecZ2qC8uz13xPt3aYPTe6icNvh7HVsBD/jCTkmf/zv0v2dZFrTbelYJ9kDH'
        b'iAoZsGHqMhyZ5TlC4LR6k1EB8WBOk//QgO7Ad/5ncX3yJ/09YF9h3n9Zff9zrD65RDr880S96UL8O0S9Fwr0/095epzYZOJUDU4a4UUlsM4pI2GK3SYHt8EDsC6adlkO'
        b'fxoUBYzCXVzYBXvgcOH3b9RyhEkonV2/ZQ58euQN7bcplqW6pWn//QVH+Ns9tgu2+2y32e6//f1D6qfMrM6Mab9lCBogO+1t3Zdf3czw7KhQm8MK8rSL9mx+/dAMEJkb'
        b'nY9fZe15qiK9AT6HfHwEDaDBydFZAPbFhwtk0DQb+os77Cld/Qw1TQg7lClMTZuTRT4Uli72UHC8dImRrQsEl+zoxOvB5XSaCgaGYD/+qqcCj9GJ72BXcXHknp7nyGcb'
        b'4Va+2r9gPuIX0wthYc+/fhVJYaH06/eHVT7UDP360o4KsbZXX/5wxVjqjZSJ2QFjs294Y05YCoNMltazD2nIglE/g9synPU/h9pKRJJmqKyI2ir2/pdQW+UdrGd0u38W'
        b'sZXPZ8SWH/87gK3nal1O1wpEGVega1n9zivnOaKW0t/3UMtWVsggd5qSwpmupKBSqcqUFKYMl6WBcVmeXJmSojxNSVFBSoqygpKiMk0dUQ5QIUrKc0enobK+Yf9DVJai'
        b'0fV/kpM1nSws0yxk8Kli9O7AVKL/orP+i876LzrrX0JnOU3pH0Vo5FOMhf2HSFoKXeg/SdL6D/OkZtImO9hs6wtbs2VMKTr69RF4gSYK4/lyUBcI6+hFq0nhsCZOALsK'
        b'UmXInkh0BoeeTsP0XQxeYlPgANijCi7Bcy6E34KUm30zuauTuC+iDsNm2CH39muDfVOAKndlvHypqxKP5uDAbM7UikJC/0Xq0EsvIAAz8QK7dlV4BQyFVAqwftPgb/+U'
        b'hAN3F8DOcCfaBxfujkGKIFnJvcxOJQCeXFPpjJ91BvYVR4FO2PGMhojZPk5wXwy9Hj+RqwzrDL2Iw28pvAh2wj2y5FLi0wSpaeFIn4qMiQY9yeHgXHiMsyAiBqXgwnSF'
        b'TeA81x3sSUyizEGrZhE4Cc8S51jYNl9L6F5OYjxmrQNDM5QIalkLHAt9Jm0M21mlss69HDN2CPCKTWWCPcqgEV4Au8hd8CCsA+1J8qthV4astZJXkdumir44Txl0hYBB'
        b'2u+1GewQcss1UT2ycuGBGQx/eMmZhvRcgJfJmv+hNUIWxcxcDkcZjrCRTdw3A7I4OJRowaWAzOi7m4ypQn6MmCPUQZqIYKVpW9LVEuCqPc+3/snmeO3AHZ2BZgtPx6Yv'
        b'GPN92UBV1e0k062hM6p9+6Nv3i9sPfVFql5G0Ucbq/Nv3flSyVBA+Ve4q64TfK0Ry6fmXmr6bCxt2+imH22++2JjRlLg6zvTGJdG8sU7LHysNgdl6rZGv9c9EH+V+UGF'
        b'Q/6h9wZyk3973/evl9VKzixQDXzndLDlprJHi0osv28WmmT8zMwMGy/WqHp/p+etsFc//u6n7lZYUnr7T8ovGws/GIh667s3dPat3SjRSZ+b93nXsZI3Zji8N1AxEPwo'
        b'P/eOm+S3Pw/n73s438zCOy87Izjiu0czkt9Nja3MjY/4Ib2y6q9ak6Gc9c2may5c/uHMcnXX4NH6W1KXqq33vmdU/Oz5SVEmX5te/dcEu2GfAqEGdprQS7qPwk5yhUVV'
        b'MFLqe8CBZ2Oew0Gwl6zVq4yDzXI8DaiHTQGwX4fYA5nwyCy4xwecdpqOj8lcSHtBnAJXDBTwMWC/j1zpNwU7aP+A3foqcI8fuDIlKNwSJjwK+tLodd5NXEqGGV6OHg32'
        b'ulXGkhWca+Eu0BwFhjKeDS95FPTTazEHrVjYmep5R6pwbdibCUZos+QAOLQUGzv78KpgWBPNgNvBcUoTXmZFB2TQK7+PlRXCPXjZM8UGrbB2HgP13Aa4i87fwArjKPdI'
        b'PJL0UkE2aMTp45A1karIABpxlE0YqqI+gucMA5i0y1BAgmMkvBYSQzcKyrqOHQsenbeQXv9YB4/DuhXwGI2OkXFjOuJoZ6cr4BrcFxWdB3cpwmOmgWPA0Cy+5n/oEx3+'
        b'2jid1qJAarF4VuN/EaZlPQ1mfhjs+y9gWjAwxKKpuqFaamAvNrAnFliQxDh4XDf4no45YabQa4HGciUeUeR0oMQ4aFw36IE6ZWKFgSv1yhhZgs/4S4znjevOm9AxbvJt'
        b'8u2YgxcM9lkPOfU7Sd0Dxe6BklmBZBmm/DoDc6mBndjATmrAFxvwyamE8eTF0uRMMfpnlykxzhrXzSLJNfiKdRxkZmJHRffazrV9IRI7nw/NHcYdQ24o31R/XV3smCwx'
        b'Txk3TJkws25f3L5YlNyb3pM+bCMRzCeXhd4wwF/CxY4pEvPUccPUeyZWUhMnsYmT1GROn77UJGB4dr3KPZNZ7f4dZfUqnxmYNi8T5YgNgsbCbqSOpywZz1g+ERw3npA+'
        b'vjh7ksUwzMWokhm5ilERNf8Z7Mc//vpNZGI64UMB71GAXvkh2FL1RYeeIEM1bC6DEUHoHhH/nqH6v4PzyOcz1/k/h/N4ke32L7I8eLGVC3DtgUsbX4jyAHXlUzSP32N5'
        b'gD47+lNsu63DU34d6KOWB/nDq/AQi0tZwbMsuB0esCfv35nmsEZGwdMGNQTmsbSCKEchoAtdhu5Gp3hgP4Z0xMBz5O17M4eJvwTxDjIyi16urqBISiHFczxgfQwY9HCl'
        b'ZBCOuaE0zWAfGq/PYw+S3hyKxLU+BkeJApJVHCUsAy3LsUPTPgrU+DJppeAlC7DDkQ92Mh1iODSAQyWBqI0oB5uinpI3wFU3dXAe0NCEOCojCdZpwLOYv4HZG+h1R0My'
        b'BPPBviTYaA1aPCJZMvIGPDuHYBPS5mZyV8NtzliJxIwMeMGAsBFSFyxPAnWgdQ7NwXgKwVi3mtTBBrv9lCmDyszwz4z1WrWQhlgsS7aigimqilLOZE6Yz6QP7q8Ip+op'
        b'KvzLwkyHuk2V9EFGsjqFxnjtwfRM9V90GbLbAwwoJ4qy32qZuWGRSTZVyaNwlN4WeGSKgSEHYLANMAID1sMRGkvSDUZiuPAiPA27yjRYhHUBRaCbJLvRC4eWoFY9cs4s'
        b'OuuqTvEZNDrkDOgA9dj7i00xQU0aZlP0ggFaPa8xBGdRvZyoxnwKAqcAIqQ14jddKngJwynKwSEWdumhQAtvI8mEH9xTSNgUyhQDnAObCZ0C7rAmTR2NBHg3F6n1NhSV'
        b'QCX4gVOkmpFScgkclvEp0DvtHKrlSOYidPEoyciyuUpwQIFOoZUPDxuDtsLlLt9whG+glvbX2Xd14d/2LA7RPfbhh0dzHpUcOHWryOLOuzYXLwwWvfJu/Jpcva+zpZ9c'
        b'qrSVOus3FFjofv0RSAwODtAN1tW9wJmxR0VNzaqrNnBxmXFtOOZUBCza/lj1MTd2trDU9tEGoW/N4smoA6Xv/PzOnO+En2/50OiDsx+kD3xwo6/x5r53DHw/8Vi9MGtv'
        b'TfR7mzwlZ8t2NWg9srdtveGYs7EqN7s3ur7l9eDaRZ/ujWmu+n7za3VrTf+049bnR+bqjBgKjzauHl27Zd2rszPG66619Y+dOfrJ33ib5n0y41j3wOdblzQvmzCuuhJ+'
        b'1XqRUu2BN6zDdnm9NWdlyuyvb7YdGuUGbEl76+6fxj957+Reo7yupV6vlFQ9HKttM/lsrcaKJcpiDUrwoI6XaPvjrejFIQErPw6882fT6PjkxfzY9V27O53LT25Tf+1K'
        b'2ZvOH5VeKLbJvsvx/Pn6eE5s0rF3+jRc97Khv7r5x7HnrC/pHL9MZbt98q63XfHVP9t/e8o+84qBq/5P5gO9WUV57z3+KMrf68zl91W+/fqExWa3W/t3mgijrz+OTjp0'
        b'Mz760JiKv8rgPPbgt8pl5p0LXy55ULV3+UdurW9fME898ZN3/Kn9P55YERu/l1Xotsg3efvaFbk37ZrtL3/UcCHlx5ON57vPNjLm9RTVBaS/7HL256P1o598tfLLei+T'
        b'5r+9FDs8+W2U0ZshtSm3JI/PC7UWrz5dVLK3v+u7n7NW6P10dWDNeMuym80uswS+nR/Hz1kPa9b/5HTvwU9C7eKE9zqerK1tMKu9eaLMa39Y1tls/pWP5rVt/moZW3Ts'
        b'9ftJDcu23o2K35/78SuLEipfVymY86eWQ4Orapf3f54/83Lm0a/g+cFFY5o/hFzpTtu2JmtPzrqWi59W2oW+fi7g5i9pm5fFrKx+f/aR4GXbRIMZsOpKrFvMxyb1v8XU'
        b'vnvfatGjVxOM//KbxT42p+Xo55/nZBjq36kMjf+stOX9mv7CtcaDOY/3fBP75k/dj9NFKvqH+3a8UfPm9d2WpRtNjn+34Ielm/V/Xp/327tfbPxykhESUTI3Mtbgt5er'
        b'gMOaI4nrlb9oPNOWULn+N8tM5+/3279xc9HirZNpZ4+W51zYz9j12vwtX3a73vXR/s5j88ZYt3PSZb/afevCyDtauolz/5PbpxpiJgx+lr5nnvPhx/GOra8sDz2us5/j'
        b'fW7wav0y8dbvvo6K/GIo3u6S8Jzey24ZX17989z1Hqvuf+v/t6rfPlr/2+TdLeu/88uBZ1g9MT1l6uZnFn1quFx9yacTkx+99Kqbqwbe0kj91PAn5bNl97+4e+pVt77f'
        b'qr3e4YyJw+qyx0sTPv0wz2VjmFvx/R9P33rM+OrCx5/y1MYfZZ8+/OXsSyqDm4s4Hlt17rs/EBQ23Oy5kZb5WTvvF4/g3tsrDL6ueWfmBp2PF5TuTQ35y1Wl+3O2Lvrr'
        b'3PgUq9W52n8yuJceu27FmvTPHq08veyHbx49bq/Xg7+eesf56F+/aJo7utXvicYPkoMJm5QT/B4rh+Rm/M0uZFDve4MH6Yvter971eCTok82GowyL6ueMYl/0rbBP/g7'
        b'pfO/lN/5cU7hnd/O5n/0UeIAN27w0pYTy2y+ieG92v3F2OXHtom+xd/a3flLz5lXEzOCHp9q1vd52+McU3riO3PPdV/dvWm7xrbnzoknNX+LWmHU6LXupcs620xHOb8c'
        b'vzb0xuI+oY65ZJOG2RODS8wdV/Zv5K8ifnQlvsVT1gpshyefQT9sgnuJ6WDIL5KTH8CJZDlrsw+2EUtugQ7scHQGHdHPhXsZBltpa/C8CWZY1cFrjlFTV2D2A9gG2mkP'
        b'4G35K4ir434l7A2oQGxYPp9kQckBtjsqwhrAOdgoAIM6tKszPOMuhDU+oEuuysh4DRW8H/DSC22wUw29b/YKaVoDP9K5LAI7eMtxDb5guxIYWAXP016MR8EFnygFXAOy'
        b'zuodwAUZe0EVnEVakCKWIRscsQFb1cnNnuAIPClDM3iDkxiDhNEMu+FRcvMKeBBunyIzuKmxKGUMZjAqoc3HHTGgH50Fl2AdfYUClwFZjSdo/2uRH9KX9jjDE7CfGIiY'
        b'zMC3pF11Rbn+ci4D2MtGj1djpsEWeIn2XdwK2jye5TLA7g0EzdBXRlueLWWgN0qBywBGfFhwxIW0kyWqCoxmALtnyekMMjRDpAFpiSykQZ4WOrOd5HAGGZkhH4qIKKwB'
        b'l/1Q/uBOeBHjGRTQDLCBdj5dCnavkQMWOPmoABivcBl009ja3ZuQDhmbC2sZtD4ggsfYpGhVoB1eeg6vALpTMWGhKotUnABZ0puReVwKtj1dUlO0iPYXFq1ez40VqPMx'
        b'LesEA/Y7w5ciQSNJ2yQcHMTfV5GmsAs7Wys4WiOpaiDOzOip2x1k9AY5uiFrHg1vQKJDtz4chafBVqGzVioGOEzhG8oKaWfsPnDVn+Ab4D5L0IMdf/k0wcGczQb9C2xJ'
        b'GrNW5UTxDUEHRjU8BTXAgw5E/IrA1mhH5+JMfqSjIqkBdDDpb6WtIfCaMDZoNfappZ13S+E+UgHp4JQx/owMROACh2JgVgMmXNP5PrHKMiraFu6cPu3ht5i0WCA8jw2F'
        b'qA2+5IEE1YDKcpHuTDvBWUfUmeznTUPdVsGtNFFhE2zg2sOaRBmrQUZqcAen6Qc3gRG4h2Y1pIPNDEoVsxoWgWZ60qINnIiWsxpi4DAamQqZhZQjkbT0ItDsiLpSL2h1'
        b'cY5QgDWgu67QfWUwCNRwFWgNjaAZthuCM7S37pky0M2dBmzwh1vgIDgGaG/dWeFwO4b4XgKjRBwItgE2o1GRTDFdQBe2CZ1hO2ghpabBDSzYThespxy+FBWtBGppeANN'
        b'buDAs/SAeYQDB4TRJvDcFL6BZjfAbrCX7qU94BA4LIzVsMNu2nJHa20X0spx6uAAGjjgTtCGuwlmN4BtVTQwQs8EafVwVymGN9DkBjSctZDbMtIy4J7oxBKFsFxwP03M'
        b'APuQoDfJ9fdroB4r8I3VpKT5KFvbopydZiniqFlFsNmJlFQXXl0pjEVvl0HaoZz2Ji8Gpwh9KBKecxMSknoPDXB4Bt8AtsTTwJqBNIac3vCU3ZBZjekNsF02Z3YSnrRD'
        b'aTxlN1inwlodT1KCeHAStMuwzvAI2InpDXWwldwYA9rDhQroBrAPnMuA5z3IkJNZYIDPKVGMjci0xOyGleAq/bzd8EIwshiiMRzbniljNwREk2Kz4TlKRm5AEnKCSSlj'
        b'dgPcnUQP9EdAvS1xIkc9Cs9XD6IMw62gyxD2sR21ZI7ZYAc4A67JDZaLObS9Ug6P0GPhSSQEvbJ5Sk8oWs5wS4mjh/lLYDs4z40FW+A1WfJYhNXAASY4W7WQ3O2UBfu5'
        b'Mid0ZN3OAC9ZWZmQYqGhl+Voz4eb5cMYBkZEgy6SdAk4qyok7080SDqoTgEjzHzZoGH9EiIQS5G4HeAqwiKWoG7RXo1KRWY/68AwPITbegmsl1EjZMgIsNOHSKIpHELj'
        b'xh7iMs4El8pSGQIzpCnwKBr/zxTCurmwF4MjnqFGVFnRRJpTlcwoQVY8eTtiZIQ93EU/uxHsUiFu5ScxJTtCge8A+yzo8HUj8NiSqc8xjuA8pvwQwMMgPEEw2hCTFDZj'
        b'bsMU32HhpmcIDylV5HUYWg276erCdYUUEVgzA25lVSiBzUT8wWVYAxqwzEbxVWEtP0LmuY/s8A4jsIUdVpJJD0YHYVcQfRkqLReIGEhvaGUGgP2ghb7gKtxshbPUFPx0'
        b'bhojHcDJGJITHdCH8huDBobN0+e8a3mkylcxkuEeAZL8GlJpeL55PRgit+bAQW0hem4cNxYpPmiM1l6bsJa1AQ3xw+TZpqgyjztir/r9UTFIQajDNdbCXI9e8ufoGfkR'
        b'P3hCiKNV1GBlExeRQc0wVNVjbbRAI547zn9zMejALQ7a0Vjzd4AXNO1iAdJMcWNFgxNQNB0UEatPoyKuBJM+NBdug23CCLBnk4Ns+MHsGNikTL9BOuAI3IZOX4CXHMgr'
        b'EeOLoiNJudHgDPYJI9AIfM5BPshiQk4NOE9wFnnRMY7P5RAMglNymkU10hiJdns+IHc6j8NYmRA5wOnlNB3KSVvGaEEvjVPP0CxM6ZEb9HrDTq496NHDagONs9BBtYeL'
        b'oZEOTk/RLMD+AhalQjETGKqy4JBIcxnlOqM+NYzZDzTPAhwxpPUWNITtQuPzZbgVjUbP4CzAfuMf8ISKpi3czeVbgcMUxcBEi5napFxzwfn06TQLcNoaAy2swAjJ10r0'
        b'poEDTt7gJWdnppxncQa0ySgsYC84x8XixtSCl/gMczM4QPJkCk66yHgWT2EWoD+A8CygyI2krQI2w3buFM4CjXWNOuCwTG8Ao3wtOdJiBRzEAomZFgE2tE6yD/PyZVAL'
        b'pBPvwKPzFWZ46ka6wuo2JcKBp0wLdMUl2LgE9tEVNpDjgzsSep0InGOnky3wgEy//Vu4xUJnjK6R4S1otoU93Ey/3/fOCcUVDepcMd9CAW4Bm2jqRgS8ZkfoFq3ZTyNh'
        b'IvWNDG9JCfBAlHMMepMVgQZMt9gMaK0iAV4ENTKKhQ7YzkTFxhgLl2i+/v8wtwIPKX8HWkH8v27rP/spRwFXYa1Gf8FJ9vt3cRUmUkPf58gU9ZwHShTP8j+ImnAUGzpK'
        b'DAX/PGriRYf+OcqE7lHN/xxlQvYQmRNrR0J3cmeyyPbEElRafAyVX8QgfpTk09EZLYmpt8xZvSO0O64zTmLq+ccYD0+hAZotmhjx0FkttZsvtps/piaxi5IYRuMc/RfY'
        b'8F9gA8qqJs4qFnl9iaE9lguNFg2F8sswBArOvsm9S3qWSAX+YoG/xH4ePqrao4q9r8N6wvpCz8Sh+uE7THI4NraTrCmHXhbXyHgygeGJkQ6eBOlQ9I+RDqK/i3Qo6Sz5'
        b'I0iHSQ4LNZvKv00+iGyJ7CjHX4KldgFiu4Cx8tfWXl8rDUsXh6U3R46bLpL1aJyYRqcGrrvwznCUlcU9i6WCBWLBApQhsSBEYh2Kz0V1RvUxh7j9XKlrkNg1SOoaKXaN'
        b'lLomiV2TxpMzJK7LJNaZ8uuUJdbek8ocXKW4T2pTZhb/DDnBzKJ9ccvi9mUty6Rmc/qCLig/ojioyAmj6SPpspq65yjArvy983vnI1GzE3SX9nGkNknDbqNzRuaMub/m'
        b'e933tfnX50t8k6Q2xeNpC6VpS8RpS8aXLpMuLRAvLZAuLRIvLZKkFf80sSDgNaXrSmNlr1Vcr7gRIwlbJFmwGNU8zjNnHmZm/Jex8F/Gwr/BWEhnzMWIhblywsIaBiYs'
        b'bGL9XyMs/H8brFDJosEKiTRYAcdvH9c0q+I5f0WZVdk4/0exCnfQz25lBaxCjN+/jFVgyIkKPijRv2ADkhAVWJio4IkO8XX/JyAIQmxAvIh/QJd6Dlv2gx21hYtegD9w'
        b'egH+wOkF+INnj+XRxwQTZiFTqIPwaekJfu8Yphq4YqpBAoNPqAapNNWApWEpoxqgre/VCIdANO/6rN9hGtgQpoGNAtMAbz+MnWIaeGOmwdw/jjTAj0lk3AuJmPCd/4g1'
        b'XyOX8T2Ff/FjEtFj8PajQGYRE9MM8O8D8kvTDLBNuQaKWIRmAGucImOcyyJiYK0Tg8qIsgejnGITnWmreTRlfyfPY5KB3os4BuWcKRoA9uvXIR7/qjISgOa0o7rT9tSe'
        b'7rmyPFlJbB9mkh3xYMH+K9ifRT1FI0UzRTtlZoqup3oS5xkugNIS9NQkJWMqSTlJxYdZrkL2VdG+GtlXJftctK9O9tXIvgba1yT7XLKvhfa1yb462Z+B9meSfQ2yr4P2'
        b'dcm+JtnXQ/v6ZF+L7BugfUOyr032jdC+MdmfQfZN0L4p2Z9J9s3QvjnZ1yH7FmifR/Z1yb4l2rci+3opHE9G0ixCO9An29Zk2yCFQrXEQnWklKKSwkV1pIXqaAapIxty'
        b'hWGSbblRPks1j29/Wz0oICY5WLaCq3COCkVl2aIRQg37DyieorEIU6vnK0pxKGkhfY2XuxP914MEasZbnmryVWFCZ16AgnOLzNeDeKHKPEjQ2YrcchIrunR1bjnaE6op'
        b'xop24uVmZRfwynNXlecKc0sUblPwmMEuVGq/t0zfWU0tthR7RUTkoRyShWxrcstzecLK5cWFxE+gsETBGZc4JqDTWei/ioLy3Fy14tyKgtIc4kOJ8lBatDqXrISrxFME'
        b'RWuxU8O04Na8kELiT2AfwJc5ehWtVcMOBzLfFrrSXGR1Jq8pJ559IJ8nuyyLJ8zFPh0Vuc9WKK5j+yA+9t7NUvBtkXmdlJYX5heWZBVhN1UZeRMVD7vUokIIhVn5xEk4'
        b'lw7Qjc7QJePl5K7KLUEFLKUzSJxW7GXnAnGrF5cKK9SyS4uLsYMakQG+s1osn3mbVVVcdFspO6u4wsszm/XM2EBW+m1CP/PUaY+0RorIpTLqv0zikUb3YS0ks9opDE9N'
        b'2RJGVrKCd1kJ25xKUSAspLCnLVZkBbDJEsbnjk5zml/BeIHT/DQBV/CXl3nToJLRjjQLY6JlniQkAjq57+myR1TzxHsJdQfaxck+l27+3+sbCs7kpNrmYp/k7CzUmzLR'
        b'IzNpDxf65qmbFMVEFjc+KyenkPZHkqXLUxQRLEBllbmy7iGsRLI91SVpp99pXld0eHgs8VmVFaXFWRWF2USIinPL8xWCwcvchctRL1hVWpKDa4TuN9ODu097SShTzy75'
        b'NI8V4qlH/zf3DogfOfJP739QwX+df3EP/4PzW4RU4UaVrid+9BuJeJacMQNDYAA2wCH80RbUwKEKPqzhg4tgDx8eBucBfRPoghdcSCzjZDoyVC/sBifAGQ5FbaIMwI5N'
        b'JSvIukALJ2aRiIW3MtUFGuoUuTgAtMPLYAANfb6UPej0XQR3F/305MmT92dzNiizkLayIDNaUriJogNIbQOdoI2ESIaHPFyZFMcH1MNjjPjyOXxmpQ1FJpRFfCGs1YQ1'
        b'a5xBexVZ6xEd66zqYM+g3OEhJcdIuJ/OZduGXK6DXQKGAMcw5oCD4DxKA3+Yq/KFZ+RJ4PvV8A8DHIqhrOZyrECjCYmTZgh3gKNc50QowmcpFryEY2OcgpdRKni9SXq6'
        b'kmIi5REOZbF82O8YEeVcYoIXnKTCZhVTXXicrDtE5SiBA/gkPpVvpOLFLIE7TfmsSvLxoMMHtOMY3ALY4AEPgZ2uXkxKfSNzJTy8kV7WWMeEB+QXgFNprngJ5iZm0SzQ'
        b'QFfcdtC1ZiqBJnDY1YtBqVczix2iSGZBd2EWHd87PDkcX5YQ/nRJMIMKhrvAYS1lg9RcoqqAs+AyaFkOj9IT9AkCeJFMz+uAfSzQHhNMhyA/AVvXKi4slgdHhzXRUVEC'
        b'Zpk/aDOFV0GtHjwPz0fp5miC2iiuGjwP9kQmJlG5edpzdMFhIji/JrEDb1JEFpxMZs+gKpfg9C/Gg0sofSRtjc8+AzsyuUSm2MOacLg3CbsQRaXAPizERIDJmua4CM5M'
        b'GzXUiF0cDhwJsQE9fCpkjS5sg9u0ULXjrxPzbYzggJaDcFU5khE4zLAFw+AgvcR4JxzO5KrA7pjy1ajt2QwH2JhfScdqgHvBPjigDi6AkTJy41mGNWgqpNe5XgoyE64C'
        b'jaCOfEZnqTMyUfe6RJ87AU6WC8uQIB6C59XxjZsZ1uoBSJzoQICo3YeF8GIAPEuSBVcY+vBkGr209oQQdONnblZ4pq0NLRqHYX3WVNPXxMhbngf2E8c3uBv1qHOKAd5j'
        b'BJFxKUQKbLPQPa5esmoFm+EABduLuEAEBkAb6SumsBEMP3czlc+jZq1nw0OOriTza7OoJFnTUNSctcqqDNTwZ2Bj4SqhPUcYiN5en+8OeT8t6v8h7jvgojq2/+/u0psg'
        b'KL3XrZSld6R3BQRBAUUQUSywNHtXFAuKBWyAioAFFrGABXAmiZiYyA2auxhjNGp60WhMMeU/M3exJHnv/d7v936/f+LncvfemTtn5pw50875ngXDofo5nz3sqXj/fOwt'
        b'z4f6bx+uPtZyKDHsi3ALyvZISteF3YLV+use6XumqwpsHFTUl3N/dX5jXS48kOkcUHH+qznmN8Lr1nzz+NrSj68tv/DVR4I/HC56RFetST7t4fBL9he5gzm79IMTxYd+'
        b'rX/T4yL99rPGxVsOxG3K3f1wx/Kl02y6LkZoxYZWLbO2502QzRk/Z66HcdYal1mfDS/d9Pl9DetQ8PXFpBozh4wzZ9zyXG6lBjXmxr0b0DHDx2nk6nJXjc3cvsqGK3En'
        b'Lu7UPTlwaLl/t1bvufhB26dP706o3dJR6T/uizP7Avw7sqvuHEx8mJU6L+xTF6ZDfOLqwc/14REvqx8m1H29c9r7DgeKTlRMs7soD1Ut3xU+W9173uyfDqbOG9AOsDJS'
        b'0yoyu5LX6f7sUObXR9f91mA70fqtXO+3Oj757YbFqk2deyPf/jZsPT9/wXCL4ZMOx0XdG236NTZda33y5naQ1TnXbZ/Zh19u7P3I5Mt2/nt7mxv7gk9b1Xz4gcLb86xY'
        b'etvwZvGmZe/omM8Jdv1u25uXTnZ95PXWgGm56K1l95f6wnrd5CclFVMsV1z+cpLOpqObNA8MmIYdeHf2kf1/DJtfas/60HqG6/oD7U8mZtU3ThHX7DzmPtGrzNfi/uQp'
        b'kW+5ZAQtXLC/+I/qH9eqRDm+pT/Xq3NB1tNV67tDh0prH9c4TrhT+In7yO+J1ebtZlFzOE+qf0iaMyPj3SjrouK9Vm/lGtdaMv1hFc5ez+sMTrnGC79ffjRqIObXddsX'
        b'8vZUeJm4ep1l1k879lW+W6lwoFVl3PmnWzJP3Km7GTFuoxYz9vdm2+Pt3k8rO6N+2TTCVPnW1G23cwv4/Peuabe+3CCt0X3reou6md5316r40smNiYXSdNOljO+EkeK2'
        b'ygPhi67M1Rw357Rd4eaLBw9VHE3ODvhK8w/69JOw+7Zn1oyEBSRP7pcetpwWvv70mpviGufb7/ZuK+wOmfSw0at673eV6SG//Gb1jXPuo98SLn4Q3RrWmCxoDcu9O9w5'
        b'p2KR3hc/L9T7Opr56dqcKL/K/Mj1c9Ovfxbs8lzs8uH9AhPz5EMbcu5uyUmtXN52dH1fiHl6gzwzaGvVuR3xX5+0evDTkV/CnvrcFHj3fJOzYsES1RWfPQ/5/JcPFn73'
        b'Bz+MnKhqoNH0hFAC1+okcpGSaOPEg6Pp5NAyRgxq0P+dWDkitQw3cSltcDEYnkHaAhyDneRYMSwG9gtjJboJ6ihzNScI7AS72APRHrQ+HbW+HA+r2WhZoMeMvJ2B1M9u'
        b'UONK3M7gcbiGUpvOtUsHZ8hBppojwPpho2uymDsbHqLUlnMFoAWsf4pnGSvGww6UExvrJUjAxmRidQiqXWNEAoxjogf74tWpXDTLOAnWerB2Dm1gQ6wyjNg2Z9j20pT0'
        b'pA2hZhnYbY3PVOEWsRoqeTellsO1BxdBPzmXTYU75sUni2NF2FRAG6npJhzFE8jhVtb2Y0uQH1JnPX+Osa6S4wPriSmDDFyIGQf6/xKdXkUDDV4dhIKAAFj9ImAC7Af9'
        b'5Gw5Ah4kb+PhNtA0eroMD81kgybADlv2kH9TGdgmjC1AjDyJJicqhRy4PgA2sJYve7VtwF4nbCSR+OrJsxncr1IC6+LZQ/UGcFS7MFUZuAdbfnFAIzE1KV4IjqC2jkuM'
        b'F+MD4iQ2dyE4QznAXaoB8BLsIjX09A6XwS1gm2UsZku8XpIYno7nUlZRKqDFVJW1ZziYizR4dyzcpone7pORBLqRXNg7JpvYFRuUw1VYIs7CPUliUeLL4igbdxXYwgW7'
        b'2VP61VH2LwJAUFpc0DsGB4DYmk3eloCtM0BNsiQuUaRVEJvIofRm83wBmjSwNPTMBxvZOQjsgjsKWUNSL5467Ilhj+B3oY9hw7LN8bBGHY05NZSaJlcHdueRhhqflSpL'
        b'gGfAWWzWwZvLWUp8OPF+oWkYH3aXZaq/tJCDa8FeNvZLL5TjkdAVXPB+xeQLPTw0aju0uZjYLWEbOrgJ9FGqcC8HzQs2ADacDehN0taWRKAWIwYRxxB3gBx0k1aD521L'
        b'ZsC+F7GM/mQKNwXuYy1Vt8FLITJ4ap5t2Wg0IXgMMY9UejuqaPeoLRs4CdeRUERgB6Vsk4AJ2EhoP9xELOF4cB82dtsBtrJ2EcdRg3ThcESb0UxZiAns5oBWcE6HNR7d'
        b'ChoRyb7KiF7EQrTOkfTySSE5oxH3VMEpG1Tr81yOHqglgUv0MpNkSUloitOhjErbmU4kbT6Wo5pkGWx76SdMjQUdPFhTAFvYSDVgDzxEIuQocYuqIzXAXi7YaONPmmz8'
        b'UrhfWxCn83cet7AT1sFzpMmywClnNMMuc1daYp7hgI4CuIrVKO2gXRW9JBNE0I/4ylej9PJ5kdpgz1NXtkvVg+OgprICntYteTmpxVBFrnBrTKI4CDaiPKmRGnrgKGus'
        b'4w9bJ8uEWmgBwOdQieHqy7ie8DRYRSSvdDE8JBOWskKfoaJewPWYl8L28O1jZYj151CFY7FBUbIQW2mrUuPgMRUD2BjJ8nDzWNCpjb9MPlAJT6uDY9wgA9DLiuhah9jR'
        b'/HB1iCvcqE7pJfFCx4DjpPQ0sNtMFucBN2DjdQ48x9EHe83IGzE4DI+gJdVmEroGm/mAY/PJN2e5whZZkvaUP8etAesSWXO7A7AjHfUUNvQdtsquCiecDy4KQxVaCvaI'
        b'lWGW6sKe4pVaqhhNHWuSUSeJRd2T6AbXGLgFiWMZZQ+PqvqAbXCl0rK/3UWWBHpEfKXFfjyH0rfkTYJ9AaQEcHK8vlMGiWhHotnBMzxSGc1MtEDll8N20kg8sI6z2GCs'
        b'Uq20wAvCOHG8WADORyYhvTKmkDdDBxxlXZ13S7Hl4SukYf/0jWCHDraE5Oeogn2otzc/FeG0jWhE3PqKYPh7vyIayd5osh0AOtSSkILYSDqQpplYiNaJddyX1udqgLWL'
        b'XwEvjdMm8RV3iGJGpdgAnueBk7NZM67FaKp+QUjGHbEaNdMMDfZcsB0eSCWiYzkBiUoPGn1rEv9ilYTerOWb/98aAP3j8wfM1b8xC/obRK1xr24VvQ6n1arKWgfNmYC0'
        b'o1X9zCYvxpBPG/IVZhaNTg1OQ7ZBPbKB8GGzmO3hd0cfBfbkDdgPm0XVho+MN623ry+rm1/LU1jb1ars1FFY2jRmNGQ0Zjdkt0mHLV3lHNrSg7H0pS19ewyHLYN68mjL'
        b'MJRQC4eLyGrIYq10UELyzNCYMRTT+J+XwtsfWwgw3rG0d+wgf9g77YZHWm3EDSPJXZsAhY2fwib8sbqK6dha1UdalJ1zq3mz+VHL7bG14Qo7p+3xteG3ja3qZYyxy7Cx'
        b'i8LaHpseMNaetLWnPJWx9qOt/RR8UX3E/rjbVo5NM4etXOt5t21d2gyHbb3q1UZMLB+Poexcn46lzB2HHP2HzQKGjAIUphaNZg1mtWpKcyPG3pO296xVuaFvo3AUtoU1'
        b'Z7ZOa57GOHrTjt74qZ3CQdDm3hzLOPjTDv6MQwjtEMI4ZA14D9pe9mPCJ9Phk5nwLDo8Cye2HbERt83qnN8+n5GEYTMjmwkEuszSnj3Rd6ct3RnLLHl6T1hXZs/SwVl0'
        b'SBrtNZnxyqK9stjmtG8Ka8hszGnIYc8vGUspbSllWx7l7IkacO+N7U/qTWICE+nARCYwhQ5MYQIn04GTmcAsOpD9ioVdk3tDbGNSQxJj4UpbuDIW/rSFP2MRTFsEMxbh'
        b'tEU4Y7FwoGJwxuVFV5ZfXs5EZ9HRWUx0AR1dwETPpaPnMtEL6eiF6Fuar1HkRoKCvKQIF3bX1rmN02zaatVsxdhKaVspY+tL2+JXegora/RH+0NL+9pIhblNo3+Df2NQ'
        b'Q1BtBD6S1WzQxAZPjElAm0Mnv53fKWoXMYIAWhAwoHJF67LWsHEcccmfMmyVOWSSqbB1ajU7YlavOmJuVV/euLxh+bC5RG5w09zjtp1kyHX2sF3RkEXRY1XKTvRIjRpn'
        b'uid+R3yztKm8dXHz4sMhtJHHnngkDVYOj/QpW2fMlBE7V7mavKRLU3kQ6xZNu0Uzbgm0W8Jg/rBdKkozhrBTntI+h5GE0JIQRhJFS6IYSTwtiR9MG7ZJwd+5a27bZNvg'
        b'1xi0PwhJrbHZnortFaOQBQLaWMAYu9LGrkPS2JvGsSNiqTwcWwWdS+hKGLC/4nzZedDpsuuwOKVe5YaJQGFuhduHMRfT5mL5+GFzH4WFDWMhed9CIrejLTxvWkhwJ1jR'
        b'uGJEEtAT3h/VG9Uf3xvPGhcxgTlDE1PZc3xmYiY9MZOZmENPzBmanj8sKUCdJJntEBb8R2MpgQT3QacH5vbNEW3j5dx2s06rdqthB98PzP3+SS3kITeNJ4xIUO87l9GV'
        b'gU+6B6RXfC77DHpfDhmWpOJKCP9BJVzft3CVe9AWXjctXHElljUuGxH59dj3O/U6YVMIxj+O9o9j/KcNzrw+6+qs60VXi67Pvzp/KCdvWDQTUZ+opN4fUS90xdQ7Kyyx'
        b'eGndMTRVYvYyxkLaWNgWxxj70MY+t62ch1wSh62ShkySRoxtm5zaHNhaKGydWy2bLQ9bN6iNWDq3qcmN5AVyHcYyiLYMUti5NJnUq31o7VjPG7ESIOWHlQrSio1VDVWM'
        b'tQdt7SH3Z6yDaevgj+yEg0bXTa+ZDqVlMGnThtOmDYmyh+1yhixyFF6+9SrEVFHaGtwcPGzi8b0mZeP0aAxlZPYKFoQBeyj/MT5jvqvyXz+e/xcjCh4xXsJC/GUcKXVA'
        b'g0WsBkoYgn49X0n9mDyBw+FYY3QIa3yUb/1vHOXL8J5kk5obJdcO4P3vQBq+PuyN4hmeRAW/gmfoPnpWSA7hRDYFhRIbAT7ZkLh5SUexV/8Kb/jfong2pljB/YcUlzqh'
        b'BpZj+m5xR+kzx/QpD79sivJfo+S/3WztnFsauTPZU8x/Rks3puXci7ayJbhsBLxslg3JjtH7/scUzUIU8Tm3dHNfnAfmFv1Tss5ispxfNJFTmE35/KKS8oK/AQP8D9Gm'
        b'kzt6HvUvSOvFpLm/IE2AW0xWhpqMnGy9ONT6T5G3FkuU6F9I1MXXJV6SugAjDc+ftYAALtrMyFtQXvYaUPF/iK6j1D+nq/91uszTXgfw/c8Q0fEviACYCPkLIsxeEjEh'
        b'Nvw/Iz+l3f+Chjdfa4jSM9T/BOTVhfPPCxvEheFlHlthl7S/gWceBQ39j7AAdR8tguuYi1EX/xlp7+CxBY8LK6n6tMbcvbmvCAaBbmSVz3+KKg2WqrIF/4ym915XgaZK'
        b'eM7/LCW6uXkzivHxfe6ChQXz/xk59OuqzxeTg/OwZ9nFrxqU/BmH9T8zdCBq9V5QO7N4gazgn5F7A5N7g3qNXJzpf0Tu/2U8i1l/jmfxoq1e2APwkoqe+YzjyfCe0sr5'
        b'wy9DU6SZ3DT1HebwdbhjlhvwOWQbJhg0h7+yDacB9jq5cDGGE1zzN+EoYhGjbxn9afVeXDBfuXjHaXAoiuIoDmVisWfJ9iVD+nb/ZvAJXERpAmIVgzsfbgUcfGJuFOe/'
        b'EX3i/xuX1v5rLqkkpRUFzepTIWGruNt3YzbVvjfYwKHUd3Oc13esFbFt9lcmbOD8zRZK3oIFxUouaCm5UEq48G82P/54abIqjvX1SvOX/M+bHxswYYF7spQaNWBCDFBR'
        b'GjBpTOYoQbVZEyZq8pgX5kvctFfgs+fzrF5r+FdNmRATuGE8wpq/PP3HHQibGUtfY411Ens4X7sArJSVgJ0BL0/uwR5QTyxZSnMIdqiNOGK6DqyKpgjamQnc7ynTC4d7'
        b'SzVx+kMcCdwHe4i1AxVA0rusDZ2ekFUVTpW7oWdwTbCIeAte0hayeJEYrXVzPLpJwgCuKRNTxOlcKidUHTTDHlhDUNngruz0+DhYB0gMbbD15cGPKiWYqQqOF8BVxJwh'
        b'UwLPyxY6wQMvrRKqg8uJl2IvOCl8NdQ9rB8L9mBP6MPgJDF4CA0yIYcVHeACPmShVMQccBK2g63Eymahi1jIBz0rXgCrzRCVY21TAE4WCuO4cA3eg03C+9BjCnkFYDdo'
        b'SyMWDbpwly7Z6BTHqlCa6twcLthqAFnjCz7ctzw+djroxQ7MKioc0FgOa8lX4Ra4Fq7HJ3d8sRql6QcPwFouaAHnTAiSmEYV6II1EteFLxBTVswldfBdBFfDGnES3JYA'
        b'jwDUsdSyueNQ2vZy7OvtClrhDozyIIcdsSIJdnKuIa3OQl8Kg1ThFvfJr4mw9qgIV2AR1npNhF8X4JdY8P9Z4S38s/Bq/0V4xUlEPoPnsfLpNl4v4eHCCoq0vwvsc8TY'
        b'BHBr8ChICDwBdpBmTHAxlsUK+JNg/wtnaR3SjONS4FGw0YXdWH/BVLg+gyCygfUFU2QJSZJFBuxh27w41g7rIujPkMGT87BjNleDY5muTUoBKwPN4uF6ioVryOG4ysB+'
        b'wmQPcAnKWaRmsAscH4WpACt1SF+0wP7rOML75kRt8SgSyQZQTSgE61NzMaqPbfirQCTBsIuYr5VjLefpBdoloAUHw7ClbB1M+Kpszkve6TinK6h9Nau3NQsefAzs1kOv'
        b'RaA9O1EJAwL64EZC8FTUs7qAXAirXwchcfQiebXmZmNwE9SluhLFSnQTJIX9bP9rCLUXogIlfEGihC+eWh6XyKHswDpVP7DHmJX5OthiF58QC9bALa/AiBTBFsLIIvc8'
        b'pds5B7cCpabBNQ6AciLYBWALPPPSfd0CdL/iY0+818EGeKEcnxxHWIBNBOoggT1NbRNgrYOe4RMGpwzVuU4VRE/FTofn8FH/P3HeTwKr1OE2cBDWRiEayaFiPepAsoVI'
        b'+YA9cDergGxUiOUbrIVnYAurgOxCRlUQ0j968BCLPFkDNy1FSg4ruP28v9FxcHcMy8D9YK8l1lRIS42Bp5WKKgr2EWmbMdMDZUucDaqVaBFw1RLSfgWFiDEYhBf2g0NK'
        b'UARwZi555wjrgpVqA/HbhmiNLHiONcm6WAX6kbKJSwRNCUptEw9PluOh09giIaACSTCH4vhScOvMCUStOcBqH2GimG9uyqVUZiBViQT5IJEQA3iSi4QrRgzPCUWJGHtr'
        b'N3epGF4ixnieYOsYJXAAe1JVCHa8wA2AfWrkC3qgaTZKpFH8CpwHXAfYYSJF0wZ9PVY0A/b+vXJLhWdHrdDOgzOgEdTMmg9PVahQHNhGwVZY50SqHAdakebfM0cGu9Tw'
        b'4ENh20zQw0J/7wqKAU3wCKxDr0SUqFRCxrqaAC0KNb+GW9RxLduMEBaW8ot5PDIFc3OCwo9cctiHDwNUWC3lZDR3j+4M9mFAoS5GtXRxS7fOqSyZzj68762JbQXd3Jw+'
        b'kqy2rXp9bsEb1YK+6GKPlCae2hlSMWMoaoFBEMdFmSyfixVqKlVB7VK1oRINsPq0QTrTh0fmBWitSqZJ3FtcidstToUMz6Zs2BXELc3AwoL5BVULS4NvBf759KqsoDQ3'
        b'VxJIVumyYAn5Tex4Xz57kbtAE02rcLt+gRaVQxHT35+SO5SadiVz0OGNTHT/M5mOrTY25RAYVzOw2g/b4KHuWSeWxBJ8j7hJE8XpYAfYGYPZ+yfegm6uFgcf2x7TmT4G'
        b'dhNrPs1ycB5pb76YBw7ATS8tJyiLySrgxDx4qqjnOVSRHUStqP5F4s0pc5MNw4wuXfhmd9/KCdY7Uz7PemC7yYbf1vaGvt3aie7SgPUmMx2+rzZwdnJY/iz50YWEXyPv'
        b'NLwnEUrF4fSY71d9cyfos9uy7y6e/Wgwcc0YY/2fIhVJ3/2qclf/RjXv1sfHzpc61x967xfOQLN6aPa376skf+38uL+mUlPtjZsjgVct9kZwrx0fRIvKvDp/7wiL5aq+'
        b'iiN37JaPT9jxfpfDvOqCHxTazm9fUJny+Mz5ReHX1koffGL1ZHWsx5GQ7dnwW4sTS6devqXtv7rXc9zPZl4PhCOLqm9eEH35jXTqmxLzrd8MWPzaeHjdnWHL71IuzZl+'
        b'c/7X52+VfPPRyi3BHu7W5ZaXU0WRR0/cPDVhnuZP1KmllpPWHrC8kdD91OtMz6Hxe+2H/QW3DT9ReOsZmdtI1ZLfSjg+p/Nx8yXtWjh3YlHcH4fGfL4s/TMTYdL2RQEO'
        b'79Y9j/qdF9B3x/xB8Nd7PiyFek+/lL8FrYYvt1o9K4rZLI1/f8anUXMffHftk/O3/X5PO9v47jpFsffJNwvCv674qsrhy4hPGsvt6GjnqBZXG6Fa1Dv6U7/6wrHzmYy3'
        b'qXCKk3/Qm/7X6i0iNU4ITOZWhHXpiDf5Z9wsskoQLz61d8exTzfarthdcPV886E7H/2QH6knfmfctoxd9xZ9HDeuJW17XOapGa1rN7u/WVX0bpvgrVkfz7+y68OSltM3'
        b'z6Uk8m/ufF/4lcDJaOaVvZMyNmfPfeuIGRPEu3/mQNyJWbkneXW3zOcmp75tSDd+f3tHqKeDXTR3zadTw78ekPhc7156euy+9+PDvxUerZN+/FVxT2DYhZ6lrVcePb3i'
        b'IwxWSL9qunruQN2zw+9lbt16p/Ld4BvS50PfdKtvmXWDeVTkeSg02OSprnTDmO57wZ8W9jgtO+P0m1/5lhXatyr0Vkwvq196eri18mD5lCt7sh7UcRidrx6um869MFHj'
        b'uy+e+vd9Ye1dm+v2w4FPJc9n52+qDLx6tLLg2czs+18uaS6b2iQdu2LOqgW5n8DAzzp+8mQ2Xqv+alxl9/clLR/ePHXiK9mPFkvf+D1/4zZHc83rhieFdt8tMvmu59L3'
        b'T10+cN33y495v536YkH8J5+pHPw0IuqxrsPmKXyjsI7x/rnhOZOmpt779aNcjS8f1HREfzdy/d7COx1O/j8u3/Mx5ycXc8dCtXeXX9fq3vsw83LN4Ge7FWOFUb3q8k9S'
        b'bhSWZOS37K7JnlLb3X5r7fSLD0Uzc8/u99qwx1T+febTijff/vgeeDIj4KPfb47cTLpX8skbV/f/qnbr/DegdiXfj5jklC2AJ/GkBbTBnXCrChmFLpaCBhZqbj04BNq1'
        b'CeJQLWzXdEFrCTRrNgCtPDRWroRbWPusjXpgpbaAD09hwwpiYaVhzk03jWThr/bDo+jTF+CpV6zN/OBpYgAjMMBAwmWl8DRsCR01o1oZQ96VaMM6YSw46QJ7wAalkRvY'
        b'G8waN+2yF2MDpI0uWotGzas8AYtyU6SVqpz6XYBbXyCUVfsQMx6JD1oTVYOdpE4lCa58NbSO2MxzQjP5LQStBxwAx4D8NeMqUJfxin2VKdhArDRcVMBemQE4zYJ+Efuq'
        b'HNjIoqdV4OhkrHFVNqwntlVZkAVlyXOB3dpwDZQTMBduGifYwJp8D+LZ4Ilc0StmU1J4hHxP22qRtoukMPQ17Lvw5Sw00V40NZVJ0GxTEDSKHgeawRmyHxPj4yhL4MN6'
        b'sPl1fLho2E7KLOHkEAhEEQXXjqXUwAmuFO6yJGV6g8ZsjE/pn40mSkp4ynLURng+uRy2yF5A3oFuV4J6B884gT2sPKCBYwELmAc2mrGYeWhCAA6RzPwsJGo1BFdycx5o'
        b'QOO4Hwe1fgfYSkgGPaAdHiZofe2wGSP2sXB9cP041nBpF6rOJhncFBsLuhFfz8VzKfUSrkALnmIlYxNXiqHQ0sEqAviFodDA+QWkrQpBX5AMbhZnJJXwif2WVgYXnDeY'
        b'zGbsK5ygDdoXYqiv8ChE9V4O7LRVWi6dLIUdsrkY2lFpopRqyrZ+twE4rB2XKERk96mhpc55DtgOT6gSY53CsXAnXs1oLgD7JfESLbykNAFnVHzgFtBP7NJAoxbcoYQw'
        b'whhpYKuuElZpCw9N2vejZHj+VgUaE2SIDUogM9DFfwXLDK6MZRvmEtgaq8T+umBDEhDsr3R4ge2HG0IkowalaM5+kLUozdFm0Yrq4foQIAeNLzBHX0EUNYJywrnxYzVJ'
        b'l4BbFr0Gx5ZBkUZyroL7tct1NbVhD+qStpwwW7CPlFxhC1ZhjDts/4nWyUco1UgO3OIVRUQwZgaGrhMLwImkUbiqOUjM8ITQCLYVGTi8tBZziWIZ1Qv3wW1KULoc1L3U'
        b'xnPtcnKJ6FmBfUIW4SoP9X6iiSjuJHhuGmtVeRKcFyPRiuNhUG8W4Goq6irYynB6OThOkPYwtpUb3P4KvBU85fAUT9vgyqV+2rP0CBIVn2MV4c7qyPNgNVC6uVhMfQWJ'
        b'isBQ2cJtLNE78pAiJTBUaM7UhaGoDNFcn+0v7ZFgC3YEQiJwGhxciCqsHs+1LVxBcpqAiz6wWyRBc7PJo+BYUlhNOJKMlrENoxbXc+B+1uIa6WAW7S0GnsBGzkmgxQYp'
        b'brhNxKG0UT9Gfe1QEpFQDBXZglNEIf2wmQ+rSZCUDi7euRnLaqXN4JSmEPTNQIsCnL6ZM5EDN5LMEaZgnTBZBGq5qDPjRZM6pQ37uGhx14mGDywRfHgiWRu2RAuwHuYm'
        b'cjz5kLV9Bo1xWrzCF2a5oza5sW6sfWMt3F+qNEM/N/NVS3QuPAHPF/Jt///bp/1XDA5sqb+CW/3Flo1dEGi9nObf4v+XVwRkgzYLLTN+wvP/pxExHErk1aSucBRhY63D'
        b'OU1chb1zm8dhf4VY2hSlEHk0R95V3jVFKgTurF1Rk/pde8emOa3B8oxzOedyFEKPnqiuEFoYzgijaGEUI4ynhfGMcCItnMgIlw6lTR0qmEtPm0unFTNpC+i0BUxaGZ1W'
        b'xqRV0mmVTNpSOm1pU4TCWdhW1rmofdGws6/CN0iuqhBJGVEgLQrsSR8o6M2hRQmMKIMWZTCiqbRoKiOaToum/0hR4qncofy5TH4ZnV82VL7kEUWt4ERwHyMdwv4p4ERy'
        b'f8R/JrK/JrK/0tlf6eyvqeyvqdwmbpNXs6ZC7NkzqyuXFkcy4hhaHMOIE2lxIiNOocUpjHj5UHr2UOE8OmcenT6fSS+h00uY9Ao6vYJJX0SnL2LSl9Ppy9GHvJu10Ifa'
        b'c0fxb8Jpcfjo92YORl9NZhJy6IQcJmEmnTBTmV7g3u7KCMJoQRhiipsPC28RRruFofd+zboKgQg9F0k7k08koyZzEWEQos4x8hTGOZh2DmacQ4edQxUurp167XrysnOL'
        b'uhZ94BL2WJUSBz5Wo9x9FSJJ26L2RAXfrdOy3ZLhB9D8AERiZ3Z7NiMOocUhCqGk07fdV/kFxiWAdglgXMJ6Sv/65JEqz8vpCcUTOf+oRrmIm8sPV/6ozhP5PFKjpD6P'
        b'dCgPv8fmeu52LN2PrCif4J7CQTU6OIn2Tma8U2nvVMY7nfZOZ7yn0t5TERd8wrhDubOGCucPlVTShZV0bhWTu4TOXYJeTeeEYQbhP+h7IbSNVOEd1LWA8Y6hvWMY72Ty'
        b'yTTaO43xzqC9MxjvabT3tNGUgTimTMHlZDowjQmcQgdOYQKn0oFTmcDpdCAWoKBILEBDxbKhiiV08RI6fymTv4LOX/EjKztKEWriDtn70jZ+d1HbWbdbM/xgmh/M8CfQ'
        b'/AkMf9JA4ZW5l+c2qd2x57fN6pzbOXdE6tdDrLEGKgZnXV4+LE0fysympdlNE5qqmhPuOkswtlaTisIngEXZYXwSaJ8Exid/aGLKUOpMemI+LlBK23gi/rC8YcQRtDgC'
        b'CeEgd9D7qtaogLl35mIRC6PFYS8fEdQlDFWlfCTx6JzTPqdzQfsCRpIwMHYg+rI5euPTrI0Tv+A+EvMBj4FZl/2VuUaxuAJpYSB65NmsgZNntmd25rTnKNO4SjsXty/u'
        b'XNG+Aj3wbda56xWIrdnO5XblMl6xtFcs45U/mMHCneXSiblMYj6diCrXFEzbeGBBtGq3alJTuHmwgoKUDUs821miaXE0I06gxQlNWnfsxQoHp6ZFzYmMgy/t4NtjxvjF'
        b'0n6xw37xNxwSFK5eLN5R1A3XqKbo11Ma91v0WjB+8bRf/LBf4gcOSY95lFs0jogr8eycdmIaUm2vpR+HcbFefP0DhwSUXuJ/z81Lntdj2jVv2C1CSS1LP8MPovlBqBY+'
        b'QbjLnVvetZzxyR4cO5QwjY7NfsFIe8chJ2/G3mfI3qfnFXPDoYnZNwKzH+lTru5D7mG0ZAIjiaElMYOGw5LEpuh7AnFb4XFRj8GwwH+0Y5fecPFHFAkl7JubAn8kUG0l'
        b'zYsZZz/a2Y+FhRtQH+Rc1mJCU+jQFCY0jQ5NQ9WdwInlDBpcNhvMGJqcfjVryCW4TV3OadeSR/eEdcWNoC9WHg/scR8WBiqk/ucCugK6g9oi0C0jjaSlkYw0Dv1TBIXJ'
        b'uXLvLq17zoI2n8NL5SVIY/emDhjjD1/IHZo4aThoEtJdPZwuLcZtAu02gXGLoN0iBo2HJqVcNWNip9KxU5nYbNQ0CnffHoMus57SYfewgYzBSZezmMgMOjKDicykIzNH'
        b'QiLoiOn0lNzhiOnDIdPbuEPCgPddAu+6SHArDPlMxe39EqdK2dxPeRx+Lmat0KNT0i5B6lLg3ilsF+IfjCCIFgQxgowB4yvml82ZsBQ6LIUJy6DDMkg6RuBPC/wZQQgt'
        b'CGlSv2Mv6ChU+IUOOA/5xqGOu4x28Lrn4jPkG0O7JA9OQJcm1btuPk2qR3QVTsIW7e9zeWgw/Zng4KyJcZhpzhkUprqhP7cto4LRH2XYqluaZVX5BWUzioplt9Rzy6ry'
        b'ZsgK/if2isoAVq9OEdij1B2q6FKHLjy85+ePHv2ykvoxPIbD4dhgE0Wbf+M89QneA92vJqJOaPvw+Dx27/swdnhgAf3BPksW058H1k9mg1fuUAfr4+N0J7Oedy9O+M3A'
        b'YRVQkwg2kxOAknyyztuGZpqxYrApOU4Ez6qQAAHWASpwJzgCOkc3iXeB8+AsW5o/rFGWliJjfccbVJbExwnAub8tTDehHHtVwKNgyxi0FAHtEfHgpEtMoiQ2cdJC7GJB'
        b'ophjwGUONX2chgNaarD+7Tvg0bz4pDxwiPVzfuHeDvaQk44V3mB7PNwiRuvyNPIdd69JMcr4Bv4OGONcjQpIIdEx7eBKfwz0Xw6OiZSR1NmSXV45WZgG9mqMgR1wA9lA'
        b'n4ZqfPb1tgG98NDLxvEFx8uxG1G4K6yX/eljk5VhK9ElOJ8sx2et0ED1WAnriRgW6S2y48kW8yhqezR9KeOd+cOhRpYBFZ84vPecdtL1NIkQNLVMKArjaGkfiVjt8v5m'
        b'9UijVdyHtkYX7z/m2HRNj61cyssd2Ho9LO+y8cLC4uT97x0pdbFLyS/89KAs9wpTd+nXw99n3ojaMJh9Jeb3tIkhXiuPb3AB50tD/H7SfL73wqbERSucexb731yYcufK'
        b'7otRp++YNMdyv33KPKRPOtZqrvKkvvi68M2tpo0Fhl9XeP7xe4Oab4DVt0fPGty23Kl/Y+eXPU3V7qalqQccAhaWH9fjur5ZlXNjt8Obm/oNywbFC/bu//jLn6q/D3nX'
        b'xvKqjWVVm9U7R6XeYzMbPH37x7Z+XXzU5+7vpy7mtVa9+aXW13MSggNOjFv46WqLvSuuG2+fdvWMZf7RvLlvznwyNhC+IXpbo/+LyvUPEkJ+War/W5Fq5ZIvPv8q7KnA'
        b'e5dZeYrGrwFab/gtelfatuq6qyVTslgU9XTKA9qkKvxsavqtI0eHHAIzbqz1qwo7e1/WsnZ85EQt+0fX3J1aZgpKY7vOtkyZe6XG2kOifsfoWs6Ob6QHqv1/pz48MvhT'
        b'wPN155Lv5m7p+z7X5EKXafLEGW/WLeOe7bD1T2+enHW4/PwEZnZNx7DHvErpkfcjOkWuZ0KDLny/t7A3cQP/91vv/zxFZF2pO5Teltt83zNQPchUvDN1Df/29OXhaz2b'
        b'33/j82XU0WuzB8XipeEG9w7miT/dN3FvVvq0I4Me4VK7w8m/FgkaYmiZ9sfpblf2u28+cz+3Jl5+Zf/2e9dkyQGzf+07vgC+bTkv48mpJwdaRr5o0L//gcWDjjKvvGHP'
        b'd3d8mW43oLh/PbX5gkFD4crlp/ga38l/63t0MG989rwc7aHnt3Z/K9uU9eHhmhtjG3xmTRK9NSHwZEzgyOCijuCA5lUp6puyPtrFDMZVa93/fK669c9PLzpPtQ7qnwjf'
        b'oafd7rgemDCt4k7Ts9OG327pT1LVdhPo3Xk76cqzj25e3ldV8+aVMMfv3jnO3Av4+dJsn+CA4b49rYsCd/9oEZHVXCqc/UhXpD1t2brDlgGUbkSZ3Myv3fgRryHz7l2H'
        b'K6ZPDIJWrLr26c9m0j76/N7tJqI61c/WVg5ozDENXve24qfm4lXW78y91+8wuNSw2Wflj5tyNu4+GDoutm58pnq92oavVVImdqUEZ96w4jeOge9oFIS9Oc/z7a65Dp+d'
        b'idH95tznQ8Ww//w914/7Gs2cfr1g/PmcT3p3L/9Z3fjSe6WHPuK7PRWgrigqHfNPXABNZ4mVHoBz5rAL4UNLMSqDEPYWvOJzWAiPs9tzYI9LPNIv2/NcQZtya1atgiy+'
        b'g+FacECWpHR3Owg2v3B5swBH2R2H3XlgozAW7Mx+6SMM96sSJ1+kOfriXwtAKgLNr3hECkAn2VOqAg1cWQLsq0qSaL62g1XIYSOMHgeXwKp4KVcZfzXME25i/Ysb4VEv'
        b'GURa/sWO2bxUdn+1rRjUja788SE5PJ3jwMYGgLtUcAgUeJrdCNzs4a4tELKBWlDdtA25qhFwDewFfaybaVsZ2IkdrEv4U9Q5lGolB+6PcSFk6YAWT6WvnxuO+terBbvJ'
        b'N3XHwlaZMqQNdrnUquTCYyrgeD7cQzIutI6W8c3NXjoDzgY1bEVPaszWBn1eEsQ+bgYnALSDDrai/aX+yh0qsB6uQVSBDfFkbybYBo0Z3UJQHzqKKcL6izrrEvLtCsAF'
        b'mcCWR0YAYj2xOhpuIbydFJWNY9/UwNq/bMUtYUHN4eZxLsq9PLhpOofdyrOAG9jtk/pZYMtfHfzAFh2VsXAnbCfSsVBjFrvjxO426YK9XFt4jMNuk+11c2G312xxFEa8'
        b'vQbk4AwRWLelQhniXA1YhxpxCw9R3s4B28DBbNYz+IwkRoZeHiYDMxJncJoDGuAqcJJULLYANmhLEkvx2IlasE+9DBVuYMSbA/vAMfYDq2BtFN6FZdtLQxduNebmg06w'
        b'nnVq7VULg93xr8UUmu8MWpLCCU4AXAeOSv4hUICnP9mjIjgBqnCb0j0ctMNmvCf8yo7wangMnI8uI/UdC7qdlbvCMaUc5a4wOAi3k5ZKg61gm3YcbClNFI7u/sbAJvLO'
        b'HhzNV0aHAucLSIAoAWz3Jw3ByQ75K8wCF9RI4IkINs4CvGQwBtbE51uznTeZg7psVwH7aiUHnBaC9rmTXvqHzvRkHcub4CrDP6MSpJmq5MCLoJ6EEDCEJ0GLLEE658XW'
        b'G0Hy51AmBSp2BaksjsNJcA7xtCZZOfvR8E2VcvPgmRg2JkmLPmqfmtG2xbMzTSmZn1mbqMBjHgYsdH0LF65jRRRxG4ct0Urgos7RDGqTHYkiEPFBLfoMxpABG18xyZgC'
        b't1BuWWqGYC+sJSoVbIB74P6/16qj3rMTp6gl5bLBl0sSYsk8az3iEjvXAtvUKb0snrtaGFF+qqDfIT5p7JI/F0wJYLUqUkC74FlWAZ2eE4C/tESSDDdicSLf4fFspxgS'
        b'BhvC45OVEBKgb6EaQZCYDI/+r+5Oavxv707+CfKTXXtEcv/OzZZsS5ItyAa0LPkZb0E+qoriUFZ2jdkHsmsjiWtii1m9qsLWBWOzH7aqV8PujiENIYy5K23uKvceNvdD'
        b'C+mGCIWl3UtPUHn6sGWAwt6hIeIBdmGMHnS87nrVlYnLodE/15xhu9whi9y7Ul8WTZ2RxtLSWEZaNJh+PQstgqfMHk4sqlcbsnalTdxGhO5yx3P8Lv45SZdkwPEK/zJ/'
        b'MIqekDosTBvKmEoLp9ar1VfRJi4KvoTdP2P4oTQ/lOGnD0RdibscN1gxHJGO0lQ06CkkUoyOzkjCe8oYcSEiSnxVzMRNo+OmDU2fRcfNQskW0yaCESHecTDvNe+36rVi'
        b'/BJoP+w3KUwdLcnOuVXcLGbsPGg7D8bOh7bzYexSerz6g3qDmIBEOiCRCUihA1Lq1Uf43vLKAZVhfiTDzxwcPzRxCh2bqaRF6Nbp1+73cj+HESYNqF7RvKx5Re+ynrKk'
        b'uzaOrXrNeiwQNWICX8LubgTS/ECGnzKghr1JB72HQ1OUH0XpCXC1G23jVq96x9qhTVVudM66y3rYJVThIMARBNoqhx186iMVAtf6yoYxiAfngruCGWkMLY1hpEm0NImR'
        b'TqKlkxhpOi1NH2XCXSQHiP2I+dZkz8Tapy/qro0TLuwlgQr2AVs6+4ix8aVtfP/0wp+28WdsQmibEPxCp1mndUzzGDZgA2MT36OKEcT79Xr1GN942jf+kaaqr1V9FN6y'
        b'sfD8UW8hx1T0jMLXR/k8ylHQmtScxDj40Q5+9ZojTvw2x05xu5gRBNKCQEaQdJk3EAv1hp2S67Xvmlsz5l7o34izsC3y8BLGOVI+dyCsa0FDzGM1ykXUFsuiIjOicFoU'
        b'zoiiaVE0I0ogu9x5Q9jlNJuemM1MzKMn5g07z6yP+dTc/q7EU56Bt/CyBkyvWF22YsIm02GTmbAsOiyrPqrJpyFZIZbKo9pzGPHUnkX9y3uXMyHpdEg6EzKVDpmKUng3'
        b'JI3YC9r8afv4gSh0qY8Y4YvaMo9bYc/vEQfUpG6PeFzHIIVv4KBQIXZ/rIp+3PUKIH/rIx9pUGLvA4kjljZNpvty2kqGLd0eOLi0myls+CibIJwz4u4lL+g2V4h8UA70'
        b'+25AGHvzhOI6RnAaIp+pUXbCew7SIc+IRxTHMYNzNWJoUvo78YrQ+Mc8/FuRPJm9QaWpUWKPA4lsjx62ixmyiMGRNRwaFzUsYqyltLVUHsdYh7xvHYIeO4sYJx/ayYdx'
        b'Cu3xqo9WWDs1LmtYxli7o39D1u4KV2mT6hEdhVfoDRuPu36h/da91oxfIu2XOFh5fdnVZUoQdd+8JtUbNl4Ke0FrUHMQY+9F23v1GOHNwGH7cIVA0iloF8gzzmV3ZTNe'
        b'0TT6J4hpCldI3DuLjxXTkoie9BuSiDbuiKuH3APDqN/2CB4KSR32SBsSpT3Sotw8GNdQ9A+/lx6v6rE9vvS294Sh8KnD3tOG3KY94lFugXfFrow4mBYH95TQ4rCBtCu5'
        b'l3OHxWkjIs+7AaH9wb3BTEAyHZD8QcCk9vi2CLmjwtWzfdmA3lBK+s3QdEV07JUll5cMpWbQ0VPkquf0uvR6yobdIh6rUoEpHCR2fMljW8o1kvPUiXINGAqYPCxJH3JJ'
        b'v2tlf0D7qQyxRvQ9j7IS/kyQr9dONZhmzPnQNBhd2Z0rfdZ8f5fqX2z4/7sDiv5fdq5eHT9Kr6CSPhp1r8V7V5XYDcAc712ZY/da83/HIeA5roLhLdXc3Jlenrc0cnNl'
        b'swsKymSl0bg6EfjSiVLcUsslnl6lIvxEEzsjBOO7MHxpxZQ9xs9GMHmn8U9X/MID+yuMy8WgojPL2IO2XIwgWjS/sDSPh96p51bNK16QN6f0OnZGMytdg7OuxZd1+LIe'
        b'Xzj4w+/gzxHf4g348h4up5B8QemdekvnVafQW9qvuGGWpuPUW3A+Lv7WVnxnhJ01NF94m91SV7p43dJ51cPqlu5rHkysEwxxxSCMqMZtN+7/7hgUL5P+Bkh8VDjuqCgv'
        b'GOBYtgaR+ROGEtfR1X9kQTnyh3RsP9E1anBs5tWbtxd0hfca9ZZfTu2Ze9WLTsmgp0wdmjSNzsmj84voOfOGZs4f8l0wJF5I65b8yM3l6Pr9SOHrY3LFGOClnEfk+eMI'
        b'3iiadzRG847lVEegLmVmN6IvVhhhVWkmrY5DT4ytR/QFCiOsAo39qqPREwuHEX1XhVEgemIRXJ2Anpjbj+hLFEah6In5BE51PHqk/HYE/nYU+23lI/xtIyl5Ymg+ou+k'
        b'MHJDTww9qsNfpsF61iiczWZiM6IvVBgFo0cmoZxqPN6Y2o7oi9gvmUqrY19S6YqpdH+VyiRM5UQOIdPScUTfjX1kiR4l/qDB0bX/QY2ja/Gj2lQexhzH1yfkyiK8ErSp'
        b'g0awSfb61LsI9KPpvilsUykogO2vGc++AJQtRpdgdeIXhfGuKaVjjqan+gsfKZX/TU82HerPPlKFSeUT0T1akMEaqZunh7e7lxQtdORlZaUVJa7gTLkMrVXk8DQ8Bc+i'
        b'ldEZ2D1GQ0dLT1NXGy2GqsFmuAPuSp0It8M96aoU7IC92tqgH6wn++NeoMedmNbWCF1x1N9tsIZXBnejNcIBHjzvA44Qv4HYvAhpAtyF7twpd9hYScz354LV4IIQrC/C'
        b'mVBOHlhdivJ1onyTcokteAToAG1SP7gdVcWD8jApYs3+m23wJkFEBVumMhsubhxoIcUtmR8nhSs9udicWQpa9VlfgJ0TTVApKMtJeBFl41BGjigPPJtB8sDj1lXSxbpq'
        b'FOVJecJ1AeUkHOJOiC3iwNGc0RryxqKyanC+jvmERnjYCh6UeoFVSBi8KC+3KLLnrgnbw4XOcAOpGs7GpYwMUa4MeIk4dsCmPLBaCvvgUaQpvSlvF3CB1A0cstNARa3B'
        b'sWWFrsqMHFzcKZQClzcFdJhKLUEz0qY+lE8G3E/KM4Sb+Eo2wBoVddCMmgT0onwhM1hHkla4AayTVsLDSE59Kd8JsI49/OhLgocJ14TqYnd7ZVmNcCVLZT08qAe6PWEv'
        b'+uFH+YH141kqN02QwhqMTkwqh9rDTsk4cDyLuAzowSNgLegGh8B6xDt/HGVwPOECaMoHe1lmJ1mV2nCVnCtEtSN0robHi2VwLTyPsk2gJsTAalI/HjjhwdYO5TwI6u1H'
        b'ubDWm/WfOQzaPWRw23LE83AqXAJYnyc7PdgpZMVyrQEPNAeyXICtVUqY4xTYJUuDfYjrEVQE3AV2sfXriwZrYE2mbFSy1fOUzTkf0UlM9o+COnhCluOJuB5JRcLD8ay8'
        b'nIZb4QUhPIw61DZl1rHKRj0fR/jn4siVgVbQjPgeRUXBFidy8pNtKFFWj21QXLku79FGrZ9GGhX1wHq4Wgb2myHmR1PRoAucKCfxTE/oANQj9MEGlA814SkkLRexBLSi'
        b'3FlerMtQIzwA1slAvz6SgBgqBuyFG9jM9WBVmhB0phGmsHkDR0teGcUKwmnQWAy7w0Ez7sxULGj0Jg3lJAXrYE12GaEcy1Cekp+orA1sseeQHPTDbrhvBeJoHBUHdkeR'
        b'GqsY57KtqxR0RHlq4ShXW+EJUq4VkFfBbtACjyG+xlPxxeAo4WuMCO4morAG0Xs0u1SZTxtsZbnTaO0Juy3NEFsTqARwCuUiMXJ74bloWGOPNwmFytqO9hNt0EToTYf7'
        b'MaggWAm2I9YmUomw15Y42+CQ4keE4EAWESeSN5DlbEkZW9M1oAfWwW47sAXxNolKAn1WpKY8sBm0o3qeslRWVx0cGmUOOAN3k5qaw75JsHsB2IFYm0wlwzZwihSbAHrG'
        b'CFmJQIr5gFDdVskauNaX1DWyBB6E3bagF7F1IjUxH7ay2q5/NmxmS3OYN+FFPwMbJxEpDARn3bXBSbAS3U+iJk3LJuyciIR6HRE+sAru9cWygAndhTK6Giq1pPlCbbA2'
        b'E/EyBf0/ne0uPWNBE2mUVd7gLM4VqCxOAC+Uj0Ep7BejQUMP6TIqlUr1nMPG9LABO5Qy/0K5gpWTlay0MyLNkuIJt2mDA7AHsTKNSgP7wD5y4AoPW6K+Nio/bK/BeJLn'
        b'leyEp2WE3gDQXqRtCPYhXqKR2FuLnMFKkDJhi1vjAHpKlf3z3BjSnhPQ2NKmHeKNeJhOpYNVSHbIfqkc7g1kqcxIRhUdHangOnCalbke2ATWa0vANsTBDCojPJx1ddo6'
        b'dxGryLXBETT18kF5smEvq362wS2m2g5gPWLdFKTYz8IdRIsgvbnXFo06ra7seIq06MXRIU5njFJzzXUBNUhhYQiDTCrTFLYQKhamwDOgBjRhBmVRWbDDg7DbDfTOBDU+'
        b'YxEDplJT4YUEtlevhjsyYR36/EpUWwklqQoljTatgg/rzMkQ40q56ojZ+q3Cx+Ops/AOpi1lC+qdWKlvgC1qSOzPYJs8ISVEaqWBfCQQyJenqoMdqOUdKcdcMSmxDInc'
        b'OVRiTSSqshvlZo4Sk6+cRQ+Pos/sAydZHyjLBYRwMTgOmlIn5iL6nCgnsNaKr0VEzhSsKxDCS3C364sWClSO5/0BbAeoDjKGNRzYpZyXjI7AU6xIG6vYYgtrN9A92pnZ'
        b'JsaiB07YEjFZCo8aEzGZosG14ShHjjq4k9X0e90isOyBwy8Udp5SkJpAPZtkTSaep2iBZqVyhKtf6NVqFpreAZyrYnXRYtRwq0gl8Dey4D5STetEN1TEadggHJ1b5Sm/'
        b'YIHkknRZuCYO1uiBNaPdSH2CUlJSQTdpCHfUafa80DxnZ4Qrqzlel88hCYwSjOPhRoxhfhwcixFzKQ3QyUWCv6b4MzKhrC0N5WsR77F2Ny5xPguNWyGakjGbdSnbbMP6'
        b'mQ04lheLZS7sQ1mEBvEzq9UoLP52SjH7UOQylsLiQ81fMO2b2eHsw9+jWQ/bR5MW6cxbsYx9uMRcj0K9zmRoxeLiGPdC9qHmdHU8udWf6L9ctKLAh304ZGKAZsSUrz61'
        b'WMd00Xz2YUiMNvGcexS5NMFseYTSc27KOMoFF1S52OIHbgn7sGY6W3qo31ydXmGQsqClrI/dgN6s4ufzUyniCRxeMR7JJaX/yLPC4mnuGIrPTYsiL86rsJ+ozcgTMcUz'
        b'2NTPFrO0Ti8o1VmuVkl9trcB/3c1hBRgXKhG3j4yKy+O8rGmPpOS/56EkJ6jOwZ1hRrNANT9FlALchez3a8b9EuEsGcO6jhVVNUs0MB65WJBm+mOZh018CTY8RdBM4L9'
        b'pMS1HsaE+qYpsmkHLZStLAxgW8TNad7Sq2Il51q5mZQccc4mdsFigb86qmdSUlHx8FFVmTf2bAvJWpeWnWE+2eiSLNbGYamDzs/rHUK/UfdaKa5+I+Xk7tVA40DQnqST'
        b'4yadTr50fG7B5D9WdgZ+OfMPzT/argf37v7ox6RZqxOHTngtee/Sj/uXPfP7Mf/bbb/Z3p3d5WTjXvqJzTrPEqOZb+i8tTHzQbVhvUPSjL310at8eXt8a+y61np0rRZ0'
        b'rfcv0XvyhtreN8aPr66Z4l9S/5lZ8N0v/efrL/hkfInpuY3WhxKnXRaU6FobfHdXUmJp/sa2rthfVaa+oRfseAd6Pw4Otl++Vf0N10eOj20rkvZbqm+T1wQtXdfZtY1X'
        b'9ZPaBt+sq9/63tIcPz5ySOfTZe4/fVhLP5+1YFm6/uqD9msOhsngxhN73m36olU9qHbWg89rf7sy9f238tWu50j/OO548OH62V9dKhfMFmt5cfsTO6esS+J1KHYtyb51'
        b'+PKOHzRuZdqCxg/TCkUuFsdPZ857KjhlsMlg5vEJhcU7N5tmd/lcqSvZ9dhZ/ebaC3FmTl53Pn17p/WVM2sZfbsrPgen/D4+89SD62Gfa9bZT8k/mPC1dfvFnT/Y/uYM'
        b'ZbC9Nc27ryb1mTCwtdK18WDwzjlxyRsWBPQ/Pv3WcP/JyUeO3XZ7V+MXM1O/e/PMktd+WDr1qH2Jk+PmL7eWPdTtuBg9adxTfX1+8xPBd8m5y1yfXht+0v7Y0yf/+DXn'
        b'ycvnPrf6OD3s4WTO9WJ17XeCnuV/6at6x9z24LhPLJYd/HFKv1Q63SqorszbuDHnyyL47ClIa5/l/+Djih19cYctrz8PKKTf+/Heum/Cj1fuc+4LmLIsZF/FyA+frPjh'
        b'sxWmswy+PFR68+vzRz5dISp0P1+Svfb9FjW/ssze5Ytq1UPaUn7946bj5NVfXou4uUjEe34eXEp9Z3LLuK7daY5fQNMzafPUP5qyvUCj97tjczxbK5IOVvZULp7+6+PD'
        b'D9v5Vzr12reUHNt96MuIzMjJ8gX3G+7LT759LM/07Qebbv7gdbNjyLN8nVOquHzRit/nLn57/ztub/r5dlQ+PPb53m/f80jN1uwPjigPeq/c4VJK2fPs9rrsX298Wpl4'
        b'vf1USIhDVlvvOx+vObI7Lzd2aHrkm4qZ2RUtV4dWdGh+1+nyXcfT3WOFCSdy7b96M9Oo+av+6scff8x5fo7uLlzFH0POzZwnJ+Mzx8SEZLgjUpVSXcrBgeF9ydlmfOxY'
        b'uHURrCEwv5RKDAdNAnYZsUfDW8ZDebx3FOrk24TxYgGH0ob7eFzYl0AOLaPhATRj3Y7mrd3o/3MyVYqnxXEHaxeTY3rDxaBbbaYQjd0n4lQplXwOuOhfovQXMp8TH2qY'
        b'LI6NFcWqUNoVXLgvBB5n37Xb+WEfKCPtlz5QywBrm2Ft7ovWz+fQJ10RKSrlHDRwXGI9NtBSom6qUAK3qMJOsJ/igm5OOuzxURp8gPMlYPPUUQ8opfuTtQrJaYweXhKq'
        b'xrDoCKqUjhoXXlrMnkTDvQlAXg72xRNfC1SkMUYtaIMdBOAYTcAaquKTxRwrsIpYYlRKSKvh1VEHyRELTsJtORSl5ss1BafgbnJMGwC2UqMw+XjoOwLPKHHy0fDNd/j/'
        b'70Tx39hvxGPr37tdvO59ofS8kM2cMT+3aN6MwoLSz9H8ihxojqiwoDdliRxq3AROdeQjrr6JnkLfvD71EQ/f2YnbZOydZ8iAIbm7S96q4jvyltyRt/jukRplYIHeq7P3'
        b'9hKUQnnvFcpBicgPDTaRJntPEinv2UTkhxabSJu9J4mU92wi8kOHTaTL3uNEj5X3bCLyQ49NNIa9J19S3rOJyA99NpEBe08SKe/ZROTHWDaRIXtPEinv2UTkhxGbaBx7'
        b'TxIp79lE5Md4NpExe08SKe/ZROSHCUn02JS9d5MOGCosbdpkr//53lofR4F8bKeEfsbR0RlDV9rQVTHefM+c7XOaDOsW1PIUY8ftEW4X1s9sc8QnQrXCobFe1eEKC2sc'
        b'SHZjYnWkYpzJnqnbp9ZlV0fdMzCqTa/P3549bGBfPeG2mWutGt41tq6vaJrRUNWm1q5JW7vL3eUze+y6ZjGmQbVhCjOL2vARS7smr4PT6jkKE3M2UntbZLuzPKxdSNt7'
        b'f2Di85hHWQkeCH3rxyhs7OpVFfbO9Rojtk7Nsjbp4Sq5bfPSD2w968MUdo7NTvXhn1pLFEKJ3KBd1u7brHFXKGnSUFjb7Vsh9x2WRuNDXBw1etKRMSjRIY27No5NeYc1'
        b'2yY167VoPjam7LxQeznw2w2afOs1FCY2OAz1/jEKe2FbeFtKUxAq1tquWdpUdThI7kHbew1be9er4LcRqLwoeYTca8jer17jjrXziIXDUzXK2q7JZd+8dpnc9/iyHhnt'
        b'OoG2Cq/nsaR7HV78ga0HIttZ1Fwlt29ezjgH9dgzzhEDhvWR+2JQne2kd61tGysbKpvK9y1H5ZhYKsmxsWtVb1ZvUz2shxrDzqFeXeHIR99LrI9QOInlnOa59dEKO/t6'
        b'DIatcBE0qSqcBK1FzUVy7Z7UYaewJp7C3qnN4LDPiANf4SxoUlG4CNvy2jVwOn5bWHNhE++Ok6CtvEvW49m9aNg1dCBt0HFo4qSrzpezh9IzhyMzFQJXuW07vylcIZTi'
        b'Q/YelZ7JA9KeMYNjh4UJrHOT7PAShYtYIXKXR7QnNEXimwntcU2Rz3Qp9PYffftmZOZjfcpRfFsoGVQdnDlYelVr2DX1ba0Bd7kqDqDdE3ZW76oW7coaKGTSwkzEXHsX'
        b'DJYrd+zR6HJl7CfQ9hMUQje5odyuzb+rrCe6e9mQMIJxiBhyiHjsTNk7P1WnHD2ehlAiv6ealFnwY3XK3O3RYrRws/n5e3XKLY0jQ0tL6p0A80Q7ffYoUOsWr2he4b91'
        b'Ckhgwaa/rkqJ+iSXC6Mm6jgUriyRw+EYPKHQ5d854buPZ/SvxizEJZINfYKXpP6nmIUaJPooi5lEeWq9iFWo9h+MVTj7z2cMf42eZ5H09yhxeZhmLosSN1nFk/t/gxPH'
        b'+wt9qklkdWNejuYdC28gVk0XbfYvpcqxnRU8Dc6hOUINPAsuwJoMFyWGmEtMbGoMnkHEqlI+S9Rc4DrjomBbSxUS6zi9akP3zL0YEfDabMc3Bmpd3h3QB1XDJm8MruQk'
        b'NJ/mhntKE0T1V42OeexyXxu2bpWUR31tqrpkxmo+l3VKPjYHrIqHW5fpw40YdEYtkGsMzsH9xJBRNxdues1IlVio+nJZG1XXbD73FYHE4/bomK49c3bBzLm5RfPzC6pu'
        b'WefiaJ25GBH2pQ/lKwnIgI9BXfCAP3si6ijjakvqvJSxt3fG3jZzGnIeRck3NqnVeAUDT/UWp+jv+g2afSq7B9szHuGegQScGqf1EgfvWeFE1DPG/DudYjXKyR5YdIFN'
        b'snjYVyxKwv4HKpSaGVcLNIJmAhMEVkaCi0K4I4lLcQ1Avw2HgttTCeNXmrJbF7VxM0UBVlUUn8Nuz9UElcUnkOAr/RgeSiOZK3OGF0mWrkp2F2Gl3QqRp5oNi8v4R/1P'
        b'qboLS3gUN537NYfS3MbChI1V7gHoLi6OnOROFeN42Ze1VKm0IgyoQ+mMTJFb/UHJ8Ep+TBqdar1ncvkPlTyKp8pxXNpFSrObwmL41M5aoZMeP571h1m4JeT+vXtcjLCj'
        b'PXCfpLupz+4suLlW6DznzmPTGdzJvZ9Yr4rhAfXmZMvwluv10IP3H3Kpo59QTpRJ/gbizpPYmr2qM3WyboXuwjQ0HxZzdj77Roa5+NHFTGI82e6CDZ0Nu5KTeA92Xyc7'
        b'DDLM9O+/mzg85qrIWOsq6gvqHK7HeWtSbi4wHp6Gg3LzKf4FS/JIfF9jWD8fNbWAEtx0IY9Mrm2pmdGC1EM2lZ2iSagLWB9RQ1PU10upT6h172SSZ7sjV9fQKtSEqdR9'
        b'an3dThbiakc5WtrUxKIpuia8BDdLUSOBGm4cPgopWhtzhifTRK2z4IfD5WnZcz90M7q04+FP9nGpDw9n+5zNP7rTY9bn4U/km7cGfVsgnDJWRW3NbnpL2FPPzxconqv9'
        b'5vh82YUd9kzDw7XT7Q4seY/uZRbvWXFvRaj17OWxjou0QlJ4Y3UmffJs3Mq96Sr+1o7pF26enHho03mN2KnVMK8/b+0f2/JPH/pBSzX85sVNF0R702Mryx96maS3cL75'
        b'KfH0w03xtTw1j8yPebdtksI5Hj8E726q8vq60If+bBIcLHPo9rjy0YFCKDL32Mz7pXeW1Wc3E070bH04VPp5/SrTz1c9+ErX37C+9SPzm0u81JZZ92Q/2D5zQ7BInDz2'
        b'g9u/Fu9PeNriv6s46PKtU8GyHq7pugKdqki1On5JX/j5ryt+eftm8ZvlzalewlDnvmMnhHODDBb+dOnw8AdV36UMOhy8/WD3zyV53mO8DZ5Lwx8cVOv5eLc45+sTQ72y'
        b'd9y1fbu3fvqR4OMvHN8LOPh55yf7cnWO3V/+YNzj5f0pUytntC56f/89n2dzVi9Iyr0z/NvF7Nb3vdI/uh2ePKf0aOq2K1epjw8YL/up9z2z3685Zl2ftt6w/MEdlYQv'
        b'/Eu+0nvy+NqcD+vMD8WWj70buLt7ffeYJxHv/eh2nVtfd/SJ9+HPsiMu2D/7ynRe9L6d35z0lPzev2bC4m8CZmeJz1d7b3A6d61jdmls8uNFWq73vDx/i7ptmQ24l0T3'
        b'hjccn82pdHj+bExz7fyxsY78/8fcd8BFdaV93ykMvQ+9DZ1h6KDSBBFEYCgqYMPCSBNF0AHsBRUVRGUQlRlRGSwwWEEsWDHnpG0SEyZjwugmbsomu5uqJtFNsnnznXPu'
        b'zDCIZpN93d/7bdbL3HvuPffcU57z1P9jRTsKHxpXKFwAW/g4qolDccqYgbAuhwiTloFAiuU+uMcR1GMoMCMgYVaBfaWEKpvAbauxj3ZWENrCwkvBIQY4DfaBQeJBDJrB'
        b'ZigjUmg6GABbsDndED3fydwIz8JW4iNsAutBf3XNypXmFmCPpSU8b7bCgLKHR8AgqGeBw67B5DWTYT1rRCQ3AXuRVA4lQEo71rfOWgObssBpjDpQnwFPMqbazCYlk0tD'
        b'BdOSMjRiMGcGkzsHbKd3k735a0bEY3gTAzwcjQTNtO/4NR7cLsgIhntcwTXyTmNTJmh1B+doJBpwBJ4S2qyATfxg7PTMKWR6O8EztLu9YpOxAJ4Fh2isFBooJRv2ETfh'
        b'TLAX9ExIxjU3pGeiPcwU9DHhYXhRA97iwVgrTM9CVPrGItLR85kloBVeo0eo2WO+sGoTTh2k3f1gMx0fwAjEhsHtUbAxJ5OPBi+OyU2B9XyH/wP3YYIw9hwnYY0QPbLH'
        b'ilkcjRB9gUlvc6XTGGxzJySe2jkhYcrSVmnpgRNTrG1ZK/dROfhL2PhsXcs6+QSVg0DCvuvAk3NbN0nYH1s7SX3kBnes/RReaq5jW3pLunRRR7msvH2pIrw3b3hcqnJc'
        b'qiR9iDtVwlDbciUzJCLJOOlUla33Xa6HnLkvB+3WOF9H62oJ+wMnV+l0OVte22mmcgqWcO7ae8o9u/07/RUBvakqrziVfTySBO0dpCxpksxAWiSpQKe29lLf1nh5krxI'
        b'4dlZokjuZfRMkWf3lqh84tTOnpJktbOb3ETpHCgxVDs6dRjKDOWGKscwiYHa1lEa3hpz19VfwThn2GPYy+qtUIZNvpWqChCqXDMlU9TOHpLk+w4uSG6Tz1V6hPb6KLGg'
        b'9c+PXD07kxWGxzKVrmGSKXedfeWi7tLOUgWSaqJVzjHoGVsHtQuSfKV50gmSFJzypaY9RsHqMVW6RElSMMuS1pImzZMV3OHy1TwfeU2nqSRJUiIplaTr+Bm1i0dLykeo'
        b'lnxpPJ2NROUSOuwyrjdCknLfgUdLoDxPIoGxFOU9lgP2Kt4kdM2FJ49oj1X7+HandqYqonrtVD4TBjyVPnHSKWovf1oa8/MnDc7rjVT5TcCCmI88V2Hdma+IlMf3jlN5'
        b'R6uRTKaVwh4aI3EFzQtfP3mJPBPV4sPvzurM6vUb8FH5JD77PLMzs9dR5ROLzqys2wxbDPcZP5nDoGz8H89lUFZc3eQZPaeemm+WXKUlD12T5kswprTa1qFB+KQM1/Ke'
        b'td9P1eaYa2GmGWeYs94wN8lwMaSZPbN77OWimsX32MWiGtE947KSmoU15TUVfyzcl3hj6mchoRlEvGjIgWuiEZ1wApISzCB6P0aik/cf4RIPIA6oiKknB+jEkFKKFkMI'
        b'1KwBEpmoKJYOWpb9AqFlx4hKBtRYyGrEfOINBZFbsFWYg4MxiP0NEcl4eMkGXGbBLWDr6vIPWyYxSLTC/6z5sr/oyM/tSNyQv2wFuMDxrcV/Og5uySwob2eWi+MGepxY'
        b'T3c5FoN0pMocj9sItTLWUivMGOJUYYtnkFRhxYpypW30kFm0HrfPEbPxMHHw4VlMP4fSOsDSg4rrJod8LdeP3V7LZqBBdfsj44m3oP/j8RzjXqdrgj5Q/Ln19Yxq7Jdw'
        b'90NDNFK6cVr8xssUx8Rsad0/zA6VU6GXWL4+U37XWFWPGisz7VhpkOEfVqKxMneQ1Ejz3jPzGjtQBr93oHDF5DBbf6CW4YFyfDEDtRgPFEszUAzaHzKK/V8ZqjFagLFL'
        b'zySbzkN+Ci0whTAoFUj1pMhFYDttE05xty83+KcRtfzjTatdQ/nk4i2xxia8caUZ5C6lbaVnwhhYqlwdtlS8iVq3lEaHhm1wn1MuOIN/1lOecD84Ao7DQ+SBx1a04Xd5'
        b'epnZK6mTabhzKOGKcoPhAUFaOst2JcWZw2TAAyHlbY//yaiWo/LbP0v6i2RoTjnTyoWakKVGTTZp5pFdBwtTcxXZjodfs7pt0mpeYlQaUbLlZHGpwZtfRP41fHvE4kn5'
        b'PnPD5SfLNveEGrxrkNm5K+mr2RUl5iXvlhQVGn3ystdr27/xMuD4/FzX9RPza/bBN3f/+TUTs+ivSixFBnebwmLqgxsMc+dbeXQ5hrFlPzglO7EceU637741SXRLAW7d'
        b'ZVLHk+y+WJ3NN9JoNMAV0CkIdgBNAdiLgAMOMoPBJRGd1ddkEs11I04QHJ5Dc92wDm4jnKTYyoh4ICDOO4eRBA5RRnAX4n3BOXiKDkg7B7eC3dgghc1RcCfYQ5uk1iMW'
        b'loznDtAdBE5lgBsmBL6wkYHTKHuVutD8b2cU6ENcKrgerWdcQoz6FsJvMqvBVYEt2J9GogbZExjg7EJ4iHxSIjyNFUA9s0eZrCal8g1/z4aHV6TG6EKvajNMgZcXly7E'
        b'u6nYQbuoj1MamwsmwI5tsS2xrfENKXet3KTFHUtlSxX+KvcIlVVkQ9JfrewlK6S+Kiue3Fpp5d2QpLa1a0i5b2P7Vwc3qQhv/y1sxBFacdtMW0ylefIk2exh1yCla5Bi'
        b'uso19I5V2BNDCrGLng+MKHPr5szGzF3ZajOrZmGjUGokj5JZ3jELQDW2TWiZ0Ba/N17OHrINkte8axvUkEIYBT06Yyj+En8Q+zdBP0gHaDZ8mtzgTyaHAu1mj8lNNSE3'
        b'D6g/SHMwuR213I01f7+LZyCaY76fmkeJGbmUmJnLELNymWK2EzUHUQ90NEP/DKOYuawYtHEQ/Snx0MY61CijXDamTVoaIzaYx/Gicg2cqVxOrmEMU2xIzo3QuTE5NyLn'
        b'JujclJwbk3MzdG5Ozk3IuQU6tyTnpuTcCp1bk3Mzcm6Dzm3JuTk556JzO3JuQc7t0bkDObck547o3ImcW5FzZ3TuQs6t0ddgPasr/gqxDSnlhVHzbEboZgpjPENsg+7D'
        b'GmRjRI3dyL22ue5ibpkHYmE87xlmiSpxiEX5UjRSa+1McqdMS+Ito6/xSEKXEBM+g+w2o+i+sZbk4hibBCM9bH9dD5PN2li3A3BeLPO1NtckvbK8plxUUb62pJpkPRrV'
        b'9vLK6hocIRJiYhK7XCQWLePhxRjLwxls8C9eTRVPRD8yLSWVV1pegW4dM81G7yru2bVYjRoJe+BOQdqmOYiQTEtD4mvwTA18CTgDG4JCGNRUhuEEJ3M6Z8UVRC8vmS5f'
        b'kQtuVKBS7a15Rlg5BxuyCEg14giLeEZm4NJ0Ggv+BpAXEMB1RIoWJmO4ddiVTZy4YsBhfwEGsW4WZjHcQC8ioTLmOtACb9IYMPVzKEFGFs4jDfoYJGjZ1p8F28HgSlKz'
        b'FbwUJYzIYIJtYDPFgOcoeBn0OJD9LBs0gR2IcmdiMNkuirmIEQ6PgYukLB02g25hSEZW4uIgnIHctIoJZe7GGqdkRDXbCE3HGIxNmWXwME5SDjtYk92gjGzEKTWwRQjO'
        b'pKGGpcOzoBcnG/ZmzZ5M58EAO5xgvZDWEWQxwE64D5H9y8x1Ux3JN1XCE2CnMD0rEJXjTL91RDUINhvArcR/Lzw0SZiZzl8BJCPI/4jub6H1yO2r3GmwXAyUiz1lSZ6E'
        b'wSDijxg+CRwQ4uQKlbCV5FcAstXksfXwYCydP8GAYsMdUOpO+yIoaL7iZIkDHfk+x2QkDYI5kBElsS9Hg9LOeWLm5G1D0T7dHWAfaIJ14IgmqQLaX2hWoUKTeWJ8+qZ2'
        b'i7lYYY39Fly4nnopDzKysIKqiU56sH4JedA9V4MQz6mNclgdRKvNYQton0jnYGBTbFA3DydhQO/eTUrz4H6eLgODwyxtDoaNXvSz9ZvgAM7CkBXMAFvQFCBZGJbAq7U4'
        b'VfVK2A5vCJ6Vy6AA9JA8CVA6ix7ODm9jPFeIrGMHt4cy0WSQs+aLl5Zb/tjLrO5GZPsfzptP5AmzYZjVRVv/ZQfr3/VYljRZYhckmT1kMPkTk/3/mtPHMGY3jXf4yNV1'
        b'zzgH0aF7e3KvZRnMKfaL/Pb2a6F/Knq0bfUM3pGHb3tNeq/2YvjffSdbhVonf1nx41vruFcczD90fMd+9adn+t1OL/YQPtmUZb32i7/Hw9hft6+53PvA1yYre1F00m3r'
        b'hm3ng9+Z1RWXY/pRhBfL2fjH2X8zOLph1Qz7OepK0/GXetNNLxWJ1t12uvHPs68WXP+eWvDJxyWGD9a6L7h/PneJqDkzL+GHAunFm7MLv8vemOzn8M+knzqmjdtSHh63'
        b'12TL18J1DnWrTnttzfjz0FvTVr0S1BYzft+qtf+QFb786k/tASx3h3Fl4uY3p81y+HhJ4UlO+1orl7l9tnYuMR/WllZEeL7zjytxt5ccvfHZD6KCrYcD43JXAocFh1O/'
        b'OrJ90P/GiqJpn935nwUhddeKPul5HHijrGvLwm8jj02wfvnvv+T+I8t5re3FmPB2dFjx/dlrexP/jq60bvp71uMvNnwZc2PZjYLLnLj8lV1fXbr/edS/Jt5YazurKnbl'
        b'irhLil+LnL7v+LJ71b71/2J+9k1V8wEF35lo+OI4BQIN2wQOg1bMOqE1eZj299kNzs8QZgaGWMF99D2mFUx43JVWw8ItqwUYfpU2r2V7IHLVxNwADyfQmtbt8CDYakpy'
        b'eWutX3ZgBxtuhXuMzHxo9NkrE6zG2MjSQIsGyGWhOeHgmA6oJgLVDw4RsokZfdgYQZBvoRTsg32gKRQRN3AW0StMOynTaiY8CK9W0unTG4ugDHsXMUuIcxFUhNKPNsPu'
        b'OPQkTVIJPbWHR9hJTrGoZA8NnXwiAuBM9YiqUqzZcysYM01mEn50EWxbQnKFZWIo3sNgD+xgAAnsg1dpOONW0FmOytFKQavpGryAieZiVrQn6CavDqXWkC/SkFUROJeJ'
        b'7rCZwAKdYOdc4tyUNwsiqpBDE1bQBc5h2myzjgUuT4U7SBvmwyNARhoBG6PGY/JKmU5H3x3jR4qdQLchKk3PAt3lhLxSpr5MKF8BBugmXgBbwKAgBLZb0Qi8GvjdPniJ'
        b'7p3BfIz5pcEv408FdZgWWhqzahD9OEwGZkU+miCoiVfdNUSJY8R0soPNNJrHRXAxA48LTZKi1mP9sQ08wYKbJ3nREsG2SLQZYsCTaHgBEybKFE0geBmemUfPr/MZFah6'
        b'RP4zgqfBRkT+LZJZqRQc+J6PS0/HwX5BdrA2CYsvOPYU7ZpUa2g9F1yjoVJ6CmbjHqe3ZNhniBpjUcaKRQT0CLkhOimDHi/UFStAM+kvm2gWuB4Ou0h/zIUSTKZD09Lx'
        b'AeyPI+vBxoIFumrADr7FC/L/wra20Si7esnirTQc3eg88TNZmjzxubTyR56iyRPv4iFJ0ShM3TomyCZg8ApFlMolDF+mryTIEhQ+NKDFB+4BQ/wElXvikGPiXZcABVfl'
        b'EiJJue/iQTJ2p6rcpw45TlW7ecr9ZPNwiua7HkGKvN6AngUqj3icXh47hvl3B3QGKOJUXhNwpm21Kw+7Icnz23NI1vHRpzgPd/G5xT2Le9eodFnV73qGKGrOre5ZPWCi'
        b'Ck1WeabglOPPvIjzTa+WrVYYqTzC8es/8vAmSe6d3DocZY7yAJWTQMIhaaR58lSVQ+DH/iE47XmqbIFiZu+UnvlDrnE4pfp4WTb+E6N0Df7OkB3gLGUfMntgQfFDFWuU'
        b'ATEDXsqAicMBycqA5FvJr1urAoRS87te/N6VA+XKCWlKr3SpoVoQ3stXCuKlhnccA9QB43oXoeekhofM1UExA57KIFLAVweG9TopA+MGkpSBCajUUh02QcruMJOZvecY'
        b'/O+bpncaq3QNwX+jkUz4nbmhpsVWODt6ZkvmMDdCyY3oHT8QqozMuMMVqoPQYOOCO1z+R56+pONcPDqiZdHyDJVLqMTovq0L7qE0lUPQx/wwtZuvvFTpFqxYPWDQs2nI'
        b'NVHt6iOfid6E/85RuoaiPgrEb8Rudvxw9EkBcQOTlQGJwwFTlAFTbhW9Hq4KyKL7aPUtY+WEDKWXEPdRZG+6UpDw7/ooojdGGThxQKQMnET6KCIG9ZGFzOI9x9Df0zj9'
        b'87lK1zD8dzbqLtRNmkaTbspuyR7mRim5Ub2zB6qU47LvcHMwoAK/h4+6ChXiLOS4q/Zb6EnLZjTiAPs5WrnfpTcfWdR6ibsnoBqX64vS83OxKP3DHxSlSW7Wg5xA6qTp'
        b'uP8sZzdJyevz/HzFI9RHm677Nmq2XpJgL5IOWyOjjaR7fjH5uTX5TQ0XVpeXVT4/M3YM6s0h3Cwuc1SztJmx8dOimlrxC8gPq2kRe+GiiEW/1RwVbk6vrpcCUitEZbzy'
        b'Ul55Da+8GsmpkyMm63rtxeRV/ox6fpph3KL3R7fIlWR+FZcUl9dUiV9IHnOSTF1g8NutuItbMZK9113TCjpx+YvpjcX0EBkvXFZVXF5a/tvT5gPcnpHky/4k27SouoZH'
        b'P1z0IhtWr21YyeqSotrfyPSOG/aX0Q3z0TWMfviFt8qQRt74zTZ9MnqNBWondY0eCUCzm67oha01w4XFJYvQJP2tln02umUeZPWTp1546mzjhdpV81sN+vvo4fMctdpe'
        b'fJO0uunfatKXo5vkq684wyOo1ZqNbpb+G0dnEMaerMx8ls4zlMrT0wBWMtxRs/U0goxRuj8qiUE0gmOuPt8cO9YzlPMcz1XSuv9ufuMyPnNtmAmZ/6sWl6DeE6MuRFNf'
        b'bxWIS+gk7jU8NOKVVTVPKSOfmbb626A7dNpqI2YYnbY6oJpOXB0dSfHNmVYfv8Rn0ILaedCK9U9Py7F53rGwP/8ZSZO/xYB4HtrNXNe4Ef/S0rKSmlFJrBfNYlCuBPtu'
        b'iBv4B7Mo47eJ56FJ962e9+gPBbP+oyzKv8eOjIbzv2RH/h0uymjkTpx5YFCNtWo1XyeM2JGL33j9qpDieO6KMQuTvI2t/ikc1oo9l9Ag8iiMfQHr4CA9iLCzUH8cY0En'
        b'2P/btmbxk387pNWaIbWhNMIiGlJ/gWLcsaWSlP05o8zPZExtGb/T/IxfLS5EVx/rm5/L8fg6/VHzM59JIsw9+YlCITy0EePysi0ZoHvhRFp1fpQPO4SCEiDNxiWRDNAP'
        b'DySVK2L5BtURqLz3kw7sz33zfd5rVm8UA8e3Al6RvNJiWLwjoj3MIHLzml3Wu156a21moNkhJ2oPm7Pq4Z+10/hZPDse05HP/Bod7lmP6WHSpy50n6rZRj/MnsVgWwse'
        b'WzCsIz7i+SgdIoesIkctmGd16dg3iUWoQ7/Rdiiq+/Ec3KHGLybrO1kwbEIV6YzNlM6a/2JpI7blBJskY3f1apo7QNRwtCmnmlddU15RwVspqigvfoowjnXT4GTnpRIF'
        b'+ecea6njtfY4i+lKddAV4/KzUfns6g2o5KUL02lLuw2illHyGhNvVnKs9zRz28pxjVvMeLmzHygoGWDnwe2v+Xn28l1TpFum7A72/sDVncMx4HwV8naRkWjmIqMSI1HE'
        b'0P2SyZEFdYwA95d397zG7WwLb3C4vD5ga4gDK9nKo2tnYekpfthwd6S4i0F53rd5cuUNvhGtW9u6nBLQiiKiJXIPsgCXWFPBedhDyqeD4+CE1tJTDrYwaEsPPAilRHWX'
        b'CHaA41qjSfgEBm0yAXIgp0FiQRNs44gEegSfGILgNkB7dQIp3Ax2ao0yWQwK1jtimwxQFNHo07vAFqiYk0dbp0iGcU94lBQtAR3ZAtiYkw7lE8BpNsWpYHpZm2iCTeHF'
        b'oOL5wnRwOohDsV0Z6HuaQT/f4PlyL/be0DOeG5VXLyQDPSJLaq+QhbSWnuwP1iLi5OjatqFtg9qFuFuua1snL+5e2r1U7YJd39o2tm1U+JwLPheMzj/iOrZltWQNc8Pk'
        b'ed0FnQUSxl1bbEp3HLYNVNoGYu9GjozTbiRJwn6YGS0ZrZnycCXXhy5W5Klsw+laR9nGn7GxPdM0rucbIK7AyoFl6PCzVp4nIURkq8Om8T+03xF6aCZOxHV+jmvPxL8I'
        b'FuAM/CsHH9LxIRUfvsL0Op9D3Fl11Ekcjy5oUvnaPR/pbwTkD3sEiL/CQ8VCUq0Y61nFtzGioJFWgrpnpBVZ7nFo7v4eh2av7xlpudp7RjoHia91/UKA+8z/9wpS7N/4'
        b'DCA+jBNEDtjYXW2vBeJjmls94lAWdrJIWY00UGnu+4Q5h2Hu9x1FjizKwu8BufBwJVOLXxeN8etiCXydvftdKz59xT62IXUE9Q4D2tlOYhDYO82lCHwpilzRANpFYUC7'
        b'8QTQToODNxHj4CUSGDzNlVh8JZ5c0bwMA/HZT2aQt2kujcOXJpArmscwop9jjH5FGBjVcWJD2mMjE/Ooh/aUk6fSMbQz5lgc+tOQ/oRtZe76HYUONDYeJhLONYhi9GOF'
        b'OJSGEUJgAvYwwTXQFTeKCtto/n6HdUMJTs90yeAQlwxH9I/KZcUwiauAeb5Nvm2UwR91xaCfRRycCXFooF0xnMOoecZPOT8Yj7w31zSGQbYyU/RGNnbc0HujyVP3GSBB'
        b'wHzUHaajvsAx1yKGmetCarMh9Vnhu5cwdPeb6e7XPYOdUTT/HHOtYzjulDuV65rPIPCBtMuEeb5FvlW+db5tvmOUGXYWGVWn+eg2aP4ZoX/GqC9sY1i5bsTJxYC4YJjm'
        b'm6HaLHH78rn5dvn2+Q6oVivscjKqVosxtWpqxG3NtSO1GmjqsyR12aN6jLGryqh6LPX60AH3IeoXJnZg0etFq1wnsXWZJRKI3O9ZaMg7+oND08stTClq7VcmSbzR1zEb'
        b'gP5W80SIA9DnC7DTh6iGJxJjReKK2nJEWExKkfBE7ilGp0U1WKgvr+HViEWV1aIirAWpDjExSa9B/ESVWFOlrjZRtU6mRYxIJU/EKytfWVKpqapKvAY9GhLCWyUSV5ZX'
        b'lsXGmphgEwwWi59qsI5fmTwlLymEl1JV6V/Dq60u4eHWLRdXFdeSpnia8Jm0rvg286lIUF3Y5XJ0SDDQRYIytRiTxLfGUBcDavACY0CxrPrTGN8aLS+2TPuNv8u9Rtd1'
        b'WOxF46Tf36T38OCRsSgO4aUTdWdxFXojkn95JavLq2vwlVW4Kxdp9H7oRu0LNWoR+p1jlCWrynEjUElpLXpcVFyMxlvzzspi9I8nWr68qrwSVaiv1nyKueRQTzOX5tm1'
        b'Ceh3kC08hD1etMmR0rTuDqFwL9ydSRIZzUgD1+FgZrY2uRMYhDtM4YmV8DBJg5RhhoNQn67CNhlXMiONGDRDONRKuMN4A9gNGmkPjcuFqM5WQXZwGjwN6tiUgT8DSteD'
        b'7UQkWguOwkZ4EnQKaOwgb3iThsM7hS4fzQ2GXfA8PBFBgX2wnhVCWcYzfeAVMEhyQ0GpXTFJfSvMQxRfExaL/ZumzQieyaQm8A1Ai20aQShaFw7kUCEWoElbTVXDbnCY'
        b'cNuyKKbGHcW2yqdCQNE5rM6DI2nCctit658ZsCFzOk4LEQT3ZNHZF6ZXGcI6fyHx5YE7wFFwonqFATbJwxOwmQI7wXawo9wg5BWDale0ZYft7Uo8uXvGm9h3xPXPa6Lz'
        b'uJ71gS93+tnYGEZ/viXPYj2VdumYu9WOjA3zeLNuMr75V6hpj+pCe4rPjK/mf/vVW2sfSTZCgen/fFAx/JnR6umeX6Z4fvFhhlXITxOyLy3vyYp+uzT+b7WTbnzpfkdh'
        b'+lme55cbtrl/8NCqIBJ6b3zon3yRk/Cn6WDK5tyjNid6u10/++Sbaze9t13b+M235h+aHRlcWxr96RWbiu0Pj1g2Di8bLz42s8Ndkfi3G0234pyir/09sTq2q8rX8m9f'
        b'3my9cv1Xyv7nTdPff/fMhsfvD8zecnRFw/WjihW3p8asrzD/m7RxubDpzTN7D826u/RI9dSk9NmNfQ+Ltgo++MZVvvNilNRm60uqLzOz+uxZdh21Uy79yLh6KmJZgzGf'
        b'S3skHAfXMoknF8VcNG8GI3wKuEZkhpT0ubSzRYSbvruFkWE5sdVvWjBHCJumaOcecaRC4nMPKXTPg13YCeQkYvG1/rPwDLxEm+El3GxhLpUZGKLnAgJ2wH7y2hXwogEN'
        b'B4PWQKPOv9YU1NOSUAPYDE4J4c5S2n+Oz6GMuUzQ6QRbiJeA0yZwGDYhJiQbzyFwkxWIuDVwgTUdDsK9RCAJZK8ShMKdQelp4LIBxQEKZpA52E1XvhmciIFNfCjXOqHQ'
        b'LiiGkM7gC9omOiAhaRUDdRbbk4FxH3cSScbeAVymU4fzwFZNRBzspYjfSkJJoCYnMdwXi74IJx4PRjwduMROAx0byPM24HylRriDzZGoAlumOezeRLJiQwnYChtxbhAh'
        b'aM7RNMsatCHhbg8LNMPT02iHhMMzzbFzA01C4H54HJERi1xWlgU89j12LgwnmJtNBDAIp1nZk5YF94A9oUJ4EFxGA4wIC2xmYYgcQ1RrK4OGGZLNhjuwSxxQTKe94kj6'
        b'+G3wCJ3XpCME7idBwqC1Ui/JCnsBD0mOPAonRx+cir4MtQot0cvxmtciThRVNQh3G/BN/gOWHYMfPIVcQ/szOIzeXUe7Ncxi0MJg6hwkDHpgEfADZ58h31SV89Qh7lS1'
        b'g3vbprZN5FKiynnSEHeS2sGpbVXLqrZNLZvkNSqHIAlb6+UQL4tXsBVlKpfxEiPtXRtbNsqLhx0ESgfEPdu3CVuEcvYdru9dJzfpYgXrjlNQL1Pt6NxhJDMa8ozonXW5'
        b'oK9A6TnpjmPSExblHDzkFPSRk0uHg8yhw13mrjAadgpXOoWT1kQPRCm1TfpYvzZ3XkeZrKy9vKNKVqVyDx12j1W6x6rc4wemK90TpSxS70fos3DkV5HKgU8cMhJV7pOG'
        b'HCep3Tyxz4Xak09M+Dx/4izh5SevHfZPVPonDvuLbk19LfOlzOGUAmVKwdC8QlWKSOW1SMLeb/nECVX8nlPQT09MND+qia+/wCM1iPWySVjqRNarQSapsYavTjSZaqqJ'
        b'FzPRs3djHuZ3GL1pWA2dmVvPxo0mEOViqhcbVj0bycSeGFbD84/auGUcPtVjGvWf2bg1diSD37KQjJmVWnN3PPoCPXN3pI4fGssA6TE/L9D+Lf7w+dZ5cQvq40TcQp1J'
        b'VZzLecq7fjSiB4u22uSzderyF2u3GRN29f+V3WYx4tC/Yj7VQc80xaQdnsEgppiEQav+opYN2BijMcWoKL4p0yL8PT6DJGcCrTjdk5Z+YuIJu2aN0E/E3118nj3G76lJ'
        b'V11UsZDgfPyGWWbG3P+lWUaGJkiyqZ5ZJnnuizPLjIoaI1rmfMZ/KWrsd8w0dnZtPEVAag+ZPL2rYr/9xszAjCBwMm9cKO3Ejy/lZGLdKTgFGk1jwBlGuev0vzKrJ6Na'
        b'7peJaR3z6ZcoRmOEmZnnriQzKdXlta19s+dBJz/ntxa/YSQ6EbE9LICRteVhslQsLTz5rtO1g9EFVEWdocvwIJ9Fcr7Z5fs8Y4uH16yFT+/wTHiAbNAJ9gE6j1kvM51n'
        b'Le0wGwWuEB4kBfFjW/SnIZmDoAH2k3loB/f/hs1jhHY/+b0TU2tc4tMT8/FsNDEd3eT5w74T0f+J/2CGyl045Ci86xf4DJuT4W/bnJ4TiUQsTx1oCmdptxZseZqFp7AT'
        b'Vrf+IfMTXr58Ju3OL7MGu23XC4U6+9PcXCKEGdtOh1tzhAKd9akqr/zlYxbM6ihUOPlfM7C1b4zpacd5aZhh5OYfd3VydOanf1CHPuQoj/1Vg8Pzb/TnI1/8Ix4Qx+cN'
        b'CBkCN0pni5o0l2FkLXjCZVlHPDCiPH3HWKMMnt/Zz3ixWI66erLpiE3qSdLcP2qTwhBAiAJiNfMooqGL8lxC0aYpTcgRJ5+Rb4i2AAMd2TB4gWQDm6dKTaaW1PBE2s1a'
        b'Xwk1ov9YJi4ppXURY9zbQkxixSU1teLK6lheEi+WhFXFFmqGqJBXtWhJSdHTBv+xdi2D7FpswPQCh3EOAE3c0JyS/GmzgmfOemYYEqiLMl6SZkAk8VS7pdqYjG6uTk8x'
        b'WhCfYWoId0+E9eW94l+Z1VXoKe/Hfv1FhzERe9kK2AB7tKNlyng17slGgvE/8koz+6ZxZIW5qUZCVuBe8NotHJ5qWWomUpYU1Z3KKDETzZj87v7XHN9wfHl7ecjQNtfZ'
        b'8+qmnMiPYSV7TRjKrhw4nGn058lO+XiLPLLSvN7lQz6Hll/rV9gJ0ij2SKDmfFcizE2LBa10NAHorR6R5eBpeIG4OYCBAj7cDerHRhQYpSPxhkaOApsna2VjcGMVI5wD'
        b'+zQ+EnAHEkO10tYJsBlJW6ZzmfAs2AKPE5o5cQPoGovXhegqrIfnEW3dNO6PRIzqwYuY4ohRzby55/zU4tUrI8t3Kb20HtZgCuojT1H4YL9UlUMUhoEYI7gQeWPyrTyl'
        b'b7rKOWOIm3HX2VPu0x4sMVTbOrfFtcTJfbqDOoPofH0q2wiCBjZR5ZwwxE1AApRE38HViKbBxAL023YvoxFCrCEPPVhKOInh/fUpcQkmD44P/2hMaNdzOYpiiuYKNXHo'
        b'lM7f6IXDP6ytJWShZqzvWFWpNrTwf08lkug6n0Mlnulc4priySJ4b3/ixtHYdVwcUD7ZMavz6BqzTrOkTGkg4kvfty6gdvNZ73q8xmcStiHPGLYRlAptCARaX7A93Bke'
        b'Zq+FUnCcBgOCV8B2M6DQxuNpYvFAG9z7bP8Tnc9CAt6YnjW3Nd1G5rYnPbcf5BUwKBePYedApXOgIkrlHIamKxJ70bwesvIdtT09b0bSCHUjzCx+vfgcmn/F2u0Jzb/H'
        b'Uwr+KAQC3seRWEDiog2rRStLFoqqs0dp73Va40pKu1ER7T29URkheYqK4vzXdPePdLMSWzOKNelMnzknk3QWlZIaEfYPFdGeaMuqVqJtDudf09bzeycwfY+mV2KxSp/Y'
        b'UIKwHn9ZbXUN1uPTC6a6pryS9pbF4jFRzNMi8ijfQmxKQZUV668N/G6xaBX9eajN/1Znb5Jdi/sLHq4FB3UbJ942QRPs+q2tEzQ4Eo13ejHaCzKYFCONCjSG+0HjFAKW'
        b'V/CNI42xx6bYMsb1yJr2i0QT/sUUA6o+EW1kkworPopaSuXR9lR8mA+OCAQ5qKYZFLw+Dh7cBM+Wd/tRjOq3UeGbrcm1kiwLwLPa5jFtscsx9071kk9AyLU73gOUc9Y8'
        b'2eIPx1XOW231reCXl/yCJ7/uHfkXs++iGywzJWC5rSBzVlLcGdHkhQv62j4sP52SdPXPl5o/sL+17dp1v+1/YyZ+kb0rbdn+rm/G7Ty4L2XbkTVrz/Sk9s/f9nLjydVv'
        b'LO1ivXb9dEL/3h7Zjk8rDx4s7/zcfdal1tS6zXFla+IaGw+98yVn8XVp2g7vUGHO1C/Wpu/6cF/Nh0fsVsLQuVeP2jTeFrr+Zd0BudevjV03iz55zcGplNf2+r/4RjRU'
        b'eBfoAKcFBuV6sAvmoIFoIjfBY7B/JDqQbObeVRvSNHrfbHhzjXYnXwLO6m3msJ1PV34MXkA9WlWRkaVV38LL8DSpPBaeShIEhmji1ozjmOAEOAA6YuB5osI1B/1JWh1u'
        b'I2zMX6mvwq2zp1OBTwKHYFOOxyhUCDRpTtGYaScNYS8YBA206lmjdw6a/79Rf/L0MccMNTAS9+yfQTTRdUIwVTTBfCgu+M+YATsMQca+Y+ersNFoQttjJClPWJS93wMO'
        b'znRcICtQOPUmqdzGt5jQOFN6ulMH57bVLavlbPl0+Qy5kcqBT+5oWSdh37d1xmrSMnmNvppUzj1kodFhukhMJTUS0yd26E3v2fn+9MQKXUb3khJa+/iSmXWyFQtE2CR7'
        b'sqCVSbK7IfQ0SQ7TaB+N9Uh/778Nuak2pvQUj/SWcA0/dR0dqvT1jgV4S/B89Af1juLpFHGMJHpQsjkY6+JIaA+XKux4w64QVZYVGerRKxstvcL5LxPM6N1iAWsBe4HB'
        b'Ag7aNbBjADammxHnAMt8K7SPWOdjVAdbJPzg3IPcKBvNbmKYZ6q3mxih3cRQbzcxGrVvGCYZkd1kzFX93URUiTY2k6TiYhyEUlmyarRjHrak0lZZ2khcVCUWl1Qvr6os'
        b'Lq8s04NVQNtArKimRhxbqJNDCwlpxxtVFa+wME9cW1JYGKQJd1lZIiZuRMS+byJ6ri2fVySqxBuKuAq7Gmn90mtEYrQ+eItElUtHdq1RtuKnuLVnWopDfs9+h/c3bKqu'
        b'Xl5SRFocRPcS2c1Ggpsqa5ctKhE/146tmyb0a0aij1YtLi9aPGrbJC2sFC0rIW+ookMptN+xuKqiGBEHvU33qUCLZSLx0pJi2gZezaNjpEJ4OdgdfVV5Nf0GxAksrirm'
        b'xZbWVhah4UL3aEWPQvKgtjVFoooK1OeLSkqrNHu2DjSEHpRaHNOBHR5E5Dn9MdR9uc4HLZb3dMDTiDu8tl6tW7zm2UURi8Y+pR8m9dT9eN0hhiQ3hzc+MiY4nJzXImqK'
        b'Jm1xibYrtc+iqUSPUghpfEpJqai2oqZaO8V0zz5zBPyreXRO3jVPcy2akcdNW46Ye/TrGTzUKGbGdgwz459N65+ujQPNEU7VEWLETFRR4HIBPENn2NrnC07MWW26cgWD'
        b'YsAGCh7ySOYzaO+BbXAr2AakYECAZFwk/4I9jGTYDg/WYuxiIAEnpqPHptOcUEBIcABsCA1Mz0JM0ck85vrl8HzNTNobAOwLNI42BYMEVBsc8Jozyo+BFgw0LgzG60M4'
        b'VNECI9BZGEeYIxMzOotUmN+PyVnMCoogqrCnz8UsgEALyI29Xq/YwWZhED84w4CaKODAg+A8OE08vC2gDAwKwOZ4uJdDMawpcAQOgAOk8um2Gszk0qjgPyWOo8G7RJUa'
        b'gI2Zh3NNJjLpi5+M14Bn+J0qOr02iMboAFeY8CI4x4LHaCRmeAl2EkRR8ggVTKe6CltpW1ZUG0LVTsSPnIL95gSpJTeN6GjT0SfsEmB2Uvc5qCANoJdkZIakBwdyKNjE'
        b'N1sBesHe2ijCp+yA0lFsKWZJd/ERSwN68ghDCnu8iFUcbIZXjMExZ49UvhHxlgDthfAGbPKbpMU3wZZcI9BMeM11bgK4xZqgmxBokzK4mWC5mMIueAQ25VZq0E0wsgno'
        b'MCRTxNrBFOOa4GyMu0eATcCVJeTJcVPDheASkGjhRTC2yGJwnE7Weg5sAU06cBFwEAxq4UXMZ9B4aad5oFkDL0IZL1iJwUXgYD7tfrIF8VjXdegigdH6Mfo0uMhR0Mo3'
        b'JRWBffGYbXQE12mAHAKPczme7pFePy8dPA5iKHeysNN0Mg0kk8WHR2iHaHAW3NRzip43nkYVb4bHXMGuXAyQowHHcaHT8NllxprDHVq1ESMctieQuRgEt84RhmSEhWSN'
        b'wOKUxdNZ4QYzkCQ9gopTXKMFxQG70QgRS3w/OLBU64EdDts0qDiglUUX94HdPjpYHMooGtQRF+/mcXQ2xnq4D5zVAa2AThMt0Aq4YkE6I2EibBqR08vn05L6thAaja4X'
        b'yfQ3bYpzoSSfSEdUJdi+nADYMCZpVsxK44XTl5hq0Ot2rgYn3MFO9EmtOWyKaYa+cBaLb0JjAO1dW1ptIa6FfWawzxLddDkJKGpQ7y5hpVsDKQGQgR3gZInmpmRwWXNf'
        b'NbxQa0A5wy4WPAxPGNfi3Dbh4Ji/fm2ralYYwwa+2NyCQwWw2GiybHEkXWDrD2WwvxZeqF6BVtRuS3Ei7K1lUbaurAlraona029hSfWKWj+434TUZAkvGsM+9Ep8u/bl'
        b'iQs4BvAAop9k2HYWrURPmIw0b74vuse2hJW0HnSTDwHdsA7uqIbn4VbtjbiFpHnu4CzbD5wGe0i3TITNa/QqqxEbobdeQA2cworNh3LyQjHYDlt1N62C5wPh9RoOZcVh'
        b'wrPxoWQiLAqvRbSoBrXGbIqxsbnYgDLfyAT9cHAxqWE9vDI1Nwu25GIfkVywvRLsxujpBxnwUgZsp6NiDoSBBtSE7txp0/BHbqVErrCZnkb714Ob2upnwzMj9c8DF+iR'
        b'l64GrdVgIB9eskRlTNjFCKwyIDI1qK/GuWgR0ROGZmXm5OP9YYZGlA7C5G9XOkBLOxPuRMQAbMk3ro6CF0mlYnBZLETS2zGcBosRS6G5fAwcIS0KyIKdsD8NEQNhcGIp'
        b'Wj3ZbMoaHGKBA1zQREixs4czhWinUZi7o3NdbC5Nn6OnCag8fJHRUmi22JqikxpS/0zU/AiYxGcTcX5FJRITjwgBtrOvodaA7k0kBWVaeSofDoJTaFtYS62dArrIVaCY'
        b'g0gz2KfxqVu3iU5DvB90FdTC67AJnZRT5ZVsIpOU3z0gNqj2QjxzxubkwzOX5dyZZHXk8dpVN+6bfr/6yuQbS2PCFJtNrZuNdjofSyqqH7hm/urP9cyHpr98Efqw7JHH'
        b'oQOXhs/3Z1nbHPgm/p34yP5r/T93/erwcsPmf33n4xS6kTJq/4dvwzsNs0tqnZK+S/l19psDi59sXvqd7M1rToeHLX6oeJshHZebMGHx4DXzup6VT37dv90x1+27kmsf'
        b'9R35dE2ioeOn9xzr295+9Op0j6Jg8cGYPT9/aR/T9KniwIHTb9wutzln4cm+dTWi9OCuis6XS08t67R/xXXxdbvgFOcChanHMefX7Su//vymem/c1K9ihnKXvvzhntRC'
        b'QcrKr7l/m9rA2Pz33nFg8MAjk/WzDh+z/MTaxeZI3Zol738Q17xJdfHWtyF2w1deDb4fGXF/t2Be3678GpXsWOK7lbNf/3r7fqOmuJf8F2VcgM6lk9V3/VrmB/9w+PDB'
        b'BUnrpg88efw/NusyF/sXLS6sWfCN2Z5P3nCpKLgtynlv/D++2uK4M+HzX3e9XrXj9XcCvltQ+coPF+wybNdkbz6+lrv7g1O71i9w+vFoxCN5xKOSkr+2xL/2s63tNf/8'
        b'xKsdfy6eX3GeM152Luvz0tY16pPSH9897vb+qXPz1IoFrV+dNvOY8afhuZbrFg41vPqL8xdnmvMrPjn7xtrV/T+5N9m1bfVb2OO/8OeLfxfE3uuLXSMozfC7saRxVv9H'
        b'72Ven5n4N/NXJko+PK5ue/2927XS7PWmipWu4aeGoiJvG35V06M68yjEI/N0r+/1ih0DK96J9fNaMeP2wJGlQBh495MvV/g6vPqd+7L8tb5XRAXRTiZLQ1wfz5yZfeN+'
        b'NJDdeHPJ0J6Z3+33+9C/uT73es7bK/8eKHqyzOnBwp2OiR7308Z/nLIJZg/x1xm+8vjJ+Q1m65dabnnf8OtJybteSXhDKodTP/j0w56Wf37h9U3Kq8ZtPy/+MaX466mh'
        b'/jdfem39d717JnS/ctMqdv79twcvL/pgVkZ3XbS31f64uS+pJnh1/eTauXrT8i37bySCI1vsrE7f/2XWm743O6e2fLPGKXbPhpn2Bq9+U/kS56u3Jh77bO6Tl5LbLf1f'
        b'/cfXK25vXbqMVfqX3I22IZcyHp09wNi4sPMN/rXtcdve/3bTq3Ov/iIt4ofQEEAHYwwEWht0rC9thbZJZwE5E3YSaKZpG1jwEMaH0zIyAgfaiW6fE+gUag3i8Bw8n0Nu'
        b'sYY7WDiXPThDXpCFs8PpGYTApfFaNVKQDQ1oen7cJmFmOtwO9+s5PgoXED3RpLxZWj+9RDAw4qrHAs3opdfooKczaUAiAAp4aEQPlQ3O056RF9BucEMQAg6b6UHrg1Nr'
        b'6JBOxUzYqaeGQnRUCI9o9VCTK2hcUyk4BK6CUxnjzfVRTxeC43Tzz6BvvymATbOzs+BuDsWOYoAeV9hBCsMQW39EECpYoaeiAufhIA17CrYtRY/B+lEKLssq4lPJzYbn'
        b'hLDJYuVItoBycJnWfO2gaoUCsAvsRX27S8ihOGuYPhXwMu0/2LxgA507QZs34Siin53MjYiBP0B3VyfY5iLwBlv0VIJg50RSFu8BTwpH3EAjIrAjaBqb7oddYBBeA4fB'
        b'DZzjNtQQCTBHGflABug0BNnwBjgnBF3WIwFr4Aw4Qmx7QrDVDjYFIcYUPbgGXoU7s4IQdxLKgvvBtUC63SegHEqEmdmgEW1KGp9tYv5bBiTELCmAV/2qQN8IFwi2L6Mh'
        b'0NoTwH7UpgML9PnwSriVtKs0CchhE9hVrcdvV4N95JNcEOd6AnPcRegePY67Mp4e2q3ovy3CyZQ+xx0FJcQS47hQNMJuX4/WcttwNzhJd3P9gmIduw335hB+u3UlcUIy'
        b'Q8x6vY7dXuk1ht1OZtHes+1hQIErIRbPyfAEKreEdayqAlpDugIeR2xQE+I+MZeag9GANzID4UHv7/1x86/DlmB4Ec0vPR5tBbxoDnsZEWALIwgeNTBmVRFfV8TmXgcX'
        b'0cQJpcfGCJxaBA8ywc5N8BxZiOXgJNyrgQYGjaHp4Mw6jwAG5ZKKIekuO9GurZvLwCABHx6H1g9l6Ar3wU6mkQsaCS4RteSgEzSgeaLZ5KHCkoy9D7xipoEJa4TXU2mI'
        b'dltvFk4ecoEs1DlIRttB3xKSBXcinvuGWQh6O5SywaFyuJN8gwGUlJJ7coKCUUUNRnGI0jiMYyfOgZdILZGVtXQd2dM8g9MQkWrGkVVokfjCDoPCyIV0T1zeBPdgmGTQ'
        b'FAB30mNiCnYjcjirVjPd4BY8pVD3ibLRfajTs5muYGcubQNvKkBM8Yi79CHYqPWXBhJH2q94/0oe7LdcCY85a0zYxrCHiRbLLiijV9p2MIDWS2gwP4BMnjrYWcYE5xET'
        b'xvd8MRhm/+UDsSM+Oynm01GB90xFxcXPtb3rlRF1u68BbZ/cOI9gOCe0JcjLNDGnBDltwrm4nriB3MH5t/KHJ+a+XiJNfN8lnzjppr0+4Z24P8Up+TNV7rOGHGfpOydr'
        b'ze22rkrbgJ7cXqdTCwZEquBE2ldY5RwzxI1R2zq0xN918pT7dId0hvT63HGaMBChptMLtq/p2CTbpPIIG/aIU3rEqTwmStl3PX3keQrPzlnHXKWcu16+nUUKH8WKHv9j'
        b'Fb3TlX7jVV4Thr0mKr0mDpSqvKZI2dLpMkOspMdJPhiHTHT6+m6nTidF1DGPO47hmmsjhTa48JjLHcfgJ5aUc/QDK8rVHVsQ5FEKhsJTHqNyCZakfGTrIIuT16hcglS2'
        b'QeSDpqqc04a4aXcdvEebKzSQ1AktCXKfYVt/pa3/GHOF2t69raKlorVSwvrIlad29x92n6xIPpfWk3YqYzhokjJokipo8rB7xq1itWeg2sUd45jFy+KHXQRKF4Haw6tj'
        b'g2xD+yY1z7vbvNP8mKWa56N29/6I54NTSg7zwpW8cAwZt162ftgjVOkRqh5V4u3fHd8ZP+w9Qek9YXSJTwBO2zHsE6P0iVF7+dH+FOOUXuPU/OBzrj2uw/xkJT/5obWx'
        b'p/0De8ozAD+q9vDrWCdbp+b5kzPvwO7EzkTtmY9g2CdK6ROl9uLj0Vbzw4b5CUp+AqrCw/4h393RRsJ+kEB5+o40QmKOZkhbfEv8sG0w+r86LOqyWZ/ZcFjGnbCMN7KG'
        b'fOZKsu56+yvY58x6zIYD4pUB8SrviUNWPHVU9OXMvszhqLQ7UWlDGXOHCuarMhYM+S9EZXIbpZXPXU9fNMerOqtUnuMlFuqImMuhF0JvJQzNyFMl5w/5zpRYSMVKK6+P'
        b'tN0TqfSOVPtGqAOCzhn3GA9FTFYFJKO+UwdFDgclKYOShoOm35r12ryX5uFvRk9oc1taqPwStZfQZws6BcNe43vt1J7eD+1M7W0kzMeOFNdNHTn+cnxf/C2T9yOFb8wZ'
        b'8pslmSxZ15Jz1965tVTCwgapDdLaYYcQBQfboBzwBIiVxbbHS1LUDi53vKN685TesSqHWLImU1/nKvlZKvfsIcfsByzKMe4Bh3L1JqEATIX1kItg2CVc6RKucol8+nE0'
        b'TaTsDxwCFFwleleNkra3kRwsres1yVn2rlM6BMhnoAO64OjSYSmzVLAVSwciBsQqx8kSA7WVbZtJi4k0Sh6hsD1n12PXa9Pj3Fs9UCwxUVol41LzFnNpiTxJtviOlT8+'
        b't2yxlLPvWPni3xYtFtIaeqqGKT3C7liFo6vDVp5KK0Qi8P32jm1lLWVtVS1V8mKVvQB3Dm0P3NCyQZ477MBXOvAfMNl2Xng5m8pM5cl3HANwgl4u3ao7VjjgXWL6ZBMT'
        b'Le73nSb8/P1KJuqe7ygmeoYmPHg9KXKHPcKVHuFqV8+HLIoX8YCFyn+qJmqhmMkJc9xY6hjrOaHUXTeTOUGGd0MFc91Y91wZ6KgNOid2PJ3hTHwDm+V0JjPxzf8ITu+Z'
        b'uwJW8hXS/xu9H9D2wIf4TY/QYSe2B2In3l/rqCfT5zEYjMmMJxQ+PibHPxKPgO2OCk40NWCaxGLxWfeMtC4ZI4H0RWxq5H86lT9Ot5dgpbUHEv8RQ4010FRjDWQSeyC2'
        b'BlIkMJeVbxdlq7EFsvP0LHuVBu6j/EbyDUZZ/dhJBsQWOOaqPqyNqJ9BUSb5yzXBC6NNgcSIJtIYlXReJyMGOO2V0RGiNRp7l94jQRqzV5GoktheFmEzI49kr8Z2kxGj'
        b'4n9in8MWS1JroPZ1gTwSBUpMO9r30IYz+pXYSomaUkkbs2jbGS+5qrgkMoa3SCQmxiO6weKS5eKS6hJS1297x5AP1pgin4YcfJZNEVVHXqy1iGntedjE9rSJ6d8ZlMaC'
        b'2ntk144nvLpjPGI6c0LgbiRFCqY/z6sUDK5nUGAP3xgJnZdm0ZajQbAZEtFYEIbFI9rogY0ZsCEnN4DWxtOWnLWw2xjs9uASpTo8l16D3WpgXwIjjYL7PUAPUeRZzCb5'
        b'OAMybAszl4fZ0rEMt0UbcT5Ozus4IyeDGm9Xm4KuJkXBeiR4Y9m5ATbnYqtLVibhqmfBhtxUncf+aJUkrY5k5ZvDrhC4jaj5YD88lwL7GfnlFJVFZfG8aAiZjqk/UVZM'
        b'ysk0rLBEunxFEq1KVMsm5ZHi3IUF1AcUNcWgsG7J6oKdKXRx6lEa2f1OzhLGHSY1Lc6rMO7jimyKvMgb9E2JZIeAXoqKoCLg0bzaVIrEyV5C0pKeGQ02BCMhoxUbjxA7'
        b'jqTRdI1hjmSqFU5PywjKIFlWkLwAm80zwBZ4lNiTQO8cJPU8bU96ahzBmWU6L6dc2Mhn1GKG2Qb0g120B6AC3tTlqqITVcE+cIqk6gwFl8Fx2saCNRO0nQXnINgCdpKU'
        b'B0kTVj/XnkXPhmmr8FNgM7hpvKGETTrrURYJHy4sMygMCrMq0mhvJy2hu3KT6SzqAhUdbTypbq3aOC9P/D7GOMElfAMyl8ARoMDuu0gGvky0umtcSXfPqUxBwh4ctCDy'
        b'HthjRq5WugULDEEbrCc63VnwBFHqhocmwiaKDc8SlS7ogqfoDAL1qOpLWMhFk6dpHptDscczwDm+H+kNUAeabYQhi7jaAGeNDQY2g4vk8Rz07HY6lYAv2KWR/+FhsLX8'
        b'9AZvZrU72vbe87fanfdmpWoS98bG11a4r5zhn2XbGmVgx77r22T/kv1M3u3D0736duZdfbPB3Mbj1vaJ6w2EG7e888mex2+5NC979cLLM1x/PrLu7Q2H/vTlx5YfFXE+'
        b'3xHzeZx71elrC3OaqyrXUh7XvfbYN89KmLT5p8UPM71t3/i271bxh67f7vjql4aOoM1l/1K+evbLrwr2bTi5yOCJZ9yinznj/SpeBT/vC/j2/tyzg7Y5eV/ePlszzusz'
        b'x8OT73KMmbOLH3UWFHeu+sV+0lyjLwIjHHovfl+/MffD+b8cv3Pt4GvnFKvm/CUvcJX3MlH/8c4D8u2O0oZ38t7rHnfpuL+r2XdOVjst23jzKkzLpow7c108+O4r02Id'
        b're+/km3+beGsAc79lyw+C7jefXmKU17Wkpn9Bee+Pr/oyBd/mid5tT6qJu+9DWknQtffPvjX059u53/vfih3cPrFb7YPnG/el5Vp//XFff5/PbCvY9zh88Aw4p+/5gZs'
        b'McwWAdVg9sd1XXaF9VsFcX95OEEJOmeJ1MNO2Wbbd2X9+uGxRdfyVn392S+7VkYVyWSw6OTCax05bb0/z1iT7cH6Nmhc/4X6Vz73M+364l70FPc9xQUXLp8V/3n8k55d'
        b'KfWfftD6fU5dd8S9X2Yo42bZ3Fv0N79v3595/VpH9Ev9gk1Jbn2mtr5gUUTMJ+nJbeXmK+7eUoIe5+i376wy/+W08fzk+KpJbN/JWQ9dF+z7H/nrZ27Uxbxi/+DVjU8e'
        b'7Y/cUSD410+G7726fGqygm9PHNcX+sKDBIQ/D57UesVPoJGcdqZZ0joz2AJP6cKnwV5wmnZsvw4OLhrtEl8DZbQj3dkwomhyAnvgJRJf1BqVroV0glu9yJutwQXYhxcz'
        b'uOGuUaxZjCMlXpnwqgAt7CXwgEbtCSTjvyc2sgEgg02jfOXBOXBYLw4pD+wiaqoseGQuoktpcHelPYtip2HAtm54if6ym758uBUrprBpXRgciOHf21lMd3iDvH9ZqBOd'
        b'XjUUduIMqwxwfbEb+SBv2E8Slu5J449kQo2CB0kh29BFgFqSDraD01hXaOzGBBLQWEArN7cj8ndIEBwAGqfq0lsZwS1ECQXPAkU5rUgEx5k6ZRVRJC6EnbTO7EZcHtZB'
        b'LQkFikyNwthyPGveJNhE662PwpveRA0Em7MQEUe7lWAWvMqhXEA7G3VRnz/pl7wphOjsyrKcnZljQHFcmWx4FMjoZuwE2+eRKuaCbTo6TRRW8BTqO8J7n+Ca6CusQgzg'
        b'Tq3CCsjn0/dchYNO+horNDrwhAlWWYFz8DAdrzgArwrJPRlVodljtVblcA9pb5i5mGiMImYSnRHWF4E2cI3v8X+vDXq+QIA74bd1RNqUXvquUPdcng6v0iskaqJXmLSa'
        b'qKKQQTk667wwFw87hCodQolaI/nWYqVvtso5Z4ibc9/BTe3m2TFXNrd9XkvqXTsPOUfBGrYLUtoF3XULVIxXuUVIUjFiWSmqwjZUaRuqdvPGnpnt8yWpalsnaUpHhiyj'
        b'PVNlG0DqnqRyThriJmHnzgB5yh07vmKGxrlTHt4eq3BQuoRJkrGPZ+DnDs73XXgk+m66yn3GkOMMtbNHR6AsUD5b5RwiSUYCsYt7h0AmkBepnAMlyWof/+60zrSWLMmU'
        b'j9y80MsdXKU1reuxsmmmora3tmeD0neiyjNBylHzfKQGak9f9MvBTc5u3XCX5y2fosjvndmzQOkTr+JN1BbjA+4Bd8+OJbIlCl+Fu8o9Wsr63MXjbkBEb+QpS5m5lC0t'
        b'u+/ipfby7Q7sDFTkHguVJn/k7KbXsPsOLuTThSrnzCFupp4sPkbP9HvcYt0FipSBFKV7Uosp1kw5SI3aEsZqozz9hz3DlZ7hKs9ICVsyu8Xivq29muvcltOSI09TFN/h'
        b'Rt7lYmmcG/zAnXJ0lZg+dKFcPNr9UD9yHchdSfIVCs873CA1Kk1SOzpJU2Um8nylYyA6c3CURrauUrvypAy1q5ssXcFRuoag3+hRnCm4SD5d4alYMTBZkq7kJuKrWS1Z'
        b'ct873ABt5Sk4SS76nd2SLY9SmCi9I3tTld5xd7jx6Oow11fJ9ZWjRgrwPRktGdKaO1wfWuRfwUBz4307/k8ElR742AmDWW8GmwjjNb639rTM/h2H0sODezFC+jPXKa55'
        b'rNQ+IrlbGuI7DbF7Gbo7EV36F5bcC5HkHogFd/rwR9x5AYsk7yQftwJ/ppjzlKCOe4aIUuvRIcFYT1BnIUGdqUmDRgvrFBbXo8x0ojnnBYrmOBTpY51cPpIITRfTQUI/'
        b'/mAkEn2PFsaPvu8ZeOIhvGTa3ZO8SuOWSgKVsLCOitJzc6LHh4Vj4XmZqAY7P1bXiMsry3SvoPEBR1w5n8ZFpsv/bXCkUTYRRVP4sFcne4Bd8/9dcORqWJdKfMoYm0KJ'
        b'I9byDBoME/thwXYmcb9JgAdgp54fFrhsDrqZ62C/XS2PIrKbDDEptKcXH9zAzl46Vy856Ch//MU+VjV2NknNKuz/FIeEn3zZClgDt5FoSn9tNOWYWMqPK24PaaMpc0k0'
        b'JbB5669QYpRn+5bVG45vnbbg/jDBSLRZ1qb40y0rYFEzTmgU+ta25TEWcleHNIvSBSFCI6FVnP3gSx+YXvSs5zfapTB/DCpMqLbyr5zPziw2aL917GWrl4yqO5nJsayy'
        b'WGrLPUeTfH++AW1DvADP+GlSP8WAQzToT+9KmjnbB6/mj47eAPXrmRvgMTNS7gEaczVcZ1Gqfijm2pW0oeoMD1yETdMYGrOsHisFBzWvv7ESbh4x9prCAUY+lFq84EQ6'
        b'Y3d7i1qymnT7vdtT+/3oYjoXPEXHYUwu/s/iMBx85Hkqh0C82bhIa9+19VH7CyQpUud3uT737dzuOnjKAxTJww5hSoewu95hvY4q71ipkdo/dNg/Rukfo/KPwzcrEf22'
        b'dVLa+qp98cOOLdlqbwFWqB9LGPaOQ6Rf5T0RbVRzlVY8knb0PSu+XiydpV5AhY7k/YdEvdpyLMWmSbUjJtVO6LBGn1RXFelI9YM/Sqp/xo1n3DNcW74cqwb/7wHA15ab'
        b'JImLFpev1EAMajIcjAIvRIQ4mdbnVawhCr/yZcsrSrBKsqTYU0ekNZ/0NK4euvysjJVjySI7uzYE/Y73DqVdMp7pXgwOwqvE3WKRg1E5bFxSvs29klWdhJ4LOtxIo5Nb'
        b'vVzn6Gm8RRr+ymRpppNnkLkizcuDlRwlyEyQhtent+3ezOgK3B9+0M2v7A3K9tNMFrXoDU7s+Ag+m47TaoU3wAHBppl6Hh/l8Cxt7h6ACnhdz+cDXIPnify6PY8IKX4i'
        b'eISmI+AsODYqqBvcgBe/xx8ImtagCvoxFemDu4JhQzqtxkzPWqG5Hx7hC8EpQ9ALTrn/m6TcViJ68LTru1qHmq6zCj91A6EAUTQFeDCphEFx7XWmTH8aQ5gGobrlr1vx'
        b'H9jzVfaCISvBWFx1Z8Nnr7sxuOqe+EYvdJCZ6eGqVxWjteTyh3GE2eJPGDhsaWFRadlCPLvEErz+RSxN68TvMLC6LTs7LzVbjFFw+Da/By54BB2KAESQMHASi0uir4jJ'
        b'hXBvhC6QDyIowE7/t4KhE/UUgvBYnnMVR3PAwKXVi7VowsbmVo/sMZqwd+cqpXnoE6abeRHjAYWPGEs47AG58DBBCyWcjqGEhQyCJawBBcbIvQ4xDVOfGFmaRz3kPYXT'
        b'+4k5V+atNHd/wjQ398BVejzAvx65k5eigu+ZRjRuMSpAvx5x6dZUK80FT5iO5q4PKXTA5UEP8OmjKFw+qyfyivddD+8ebl/yQxbDIuajSSnq+ElPWOsZ5q5PKHx8SI7f'
        b'GaDCB2z889F6Fn60qIfVl3uFe2XxUNRUpXnaE2YOeQQffyBH/K50xgNy/dE88ox3j21PXl/AUEDcSylK8/QnTHvzwMcUOuB7M9C96OejBHxnrtLc8wemiXkQLvH6Dv+i'
        b'42mxcqKAC7cTfGLYDRswzwcvYuYvE3siBfgbrAQ9gbXfock2HlwAW8FhsHdiFWwPswLb4WV4zW7CeFBXBM9xYhENbAF7jUAjPAy3eJgDCdyGOLfToDUlBXEdYC/YyXCB'
        b'N8FleNMcyGLhBbAHnBch5qUnzxzDQ2yF5ybGg5ugNw3cnIruaoY714DLoAecDlkPjmWCs/Hr4Q3YjcNFT6L/ro4DJ8Ax2FW2IsIXyoLswrF/TSU4AuthDzwP29dPBE2g'
        b'CzaCPoepK+Jz7EGTN6xL3rAkEu5GZPRyeTzcvnSqs4fIOTVWaDAnYl1IDjg2xzUYEdmL8eAKhmwEkkpwEragai6lgUsxywJhc8RCuMscdhXDXlvEycrBXngU/XcNHihM'
        b'hgenRS4Bu4vgGQ44Ai7B7VWgD7bAI7nwDOhdtQweBzc3IKLclgdanODRpQXwADg+wQ6eTQPXwsAu9PUtYI91CjiXC7b6C1EDLsGD0eDcBnhqOpAxYBfaXrbAfeAQ+tu8'
        b'GCjgQXB0lTvLFOwDF2BHRBA8Bi8tjjaJhxfBjiJXUDd1GagvRtW2ZYHr/KLUKo9UuKcc3oTtGXD/HEdwZnUSHADn0UD1TuQA6XR+PoYEAfvBNhO/PNjvCDvhUXR2OQvs'
        b'AIdmo87YD9qC4OXoBN+JPlxbeH4munBonX+BAMrgSStbuANKwMW8anS1xcLECw6iJ07CPnAONaeXgm2RJXFQNg+0R4DrNrDDYlEW2FNWkwDrZsA2d9C0cLwRHAQDrrZg'
        b'oAIMuoDtZejx08thI5SGu8KjxV4z504Mha1oJgyArmoRmnQH4ME8M6d5ayvj1sELrvPdwMFscNSpAJ5D/dMGFUboYy6gGXUQHp0EdxmBHVPg1TA0jAfAqRj0ladR+y6D'
        b'rbPRCDQHJ6LpsHM1OO/gAnei/rkG5RYbWfA6bJzqg2ZSX20TBoIDDRQ4PCMJ7EHT3gxcRzLL+klodLungDp3cAhKg82i4Fli3DnCmgK6ikTefCBZzAZNvE2h4ER07drF'
        b'logdbyS5jzvhruWFs8ANu9ng4CRwEPSB42CrCB4KhG0CP7SNXwWXWaDXGO5zgZdEBsvhYXAhf86qRNi+IbcCnILtqCNuBKCvQPMDnqkUxqEqjriCdrh52mxU997ZoG0C'
        b'kIIdi9DS28yMyYJ7QW8wuuc8VICTGwo22FrN3rQoamoZPGS9JsoansHe92gib0VrYss4tKwap3pk+qzxQ1OtGQlkp8PRFD+FpuYAbBDBvRXgOvqmKfAaaDSEJxLg3nWg'
        b'o1aYVI6muGypP9wRgKTDwfUTQjaB7QuMc8GAoztGw4Xd1tHsKjhYCM8zoWS1vWgKrAf9JmDXxjScPsF1KtgzB9TBbcWWoAMocnLzI4ps/JxgT9JUE65NSJiBS2Q+esHh'
        b'TNiQi0ZYCk86ggZEVupEsGs8xL6sW+A2FtybDVpgHw8eyoY7Z8OToJ9tjWbfTgdwFH0JpkzbFkbgzgUN8DS4sGq1E9jtTnxbB4BiNZoPO9ZaG6H10F8K98Er6yO4oBV1'
        b'Yz0anl5EuS4alVlkwA4nJLfJ586Ep9Cy2wYve8wHN7KEYBB0G/uAvdWIInSB7TElsH8ZbJwNboQ4Y6X9vBxw2QXNuVNw9wywV5hhPW8VvIje14XmwpECsBmtoEH0WZsj'
        b'4Clb/1wfuxywGfX5xTnwRAXqOkUOOM//f+V9B1SUWbbuX4FQ5JwRUFAyAkqQIIjkKKIE0SIVSWIRRBQFkZxBMgKSlCQZiXJ777lv+s709NNxeuymu6fn9tyZuZP64XT3'
        b'MKlfv/0X9vS9vWZuWOutNW+th65Tf9V//v8/Z5+9v/3tU3X2wTUp6EkyhQeRWkXvcNlvy0jTHpNGekALq5HU7HUrWC5yxYF4Pt12GO/mJMJwvjzZZffJCGuYUEkIhklP'
        b'aMRVEtYWdrO/mH0K9dSzRZgLhOpLZK5Vh3E7wNPTA3uCYDRFRQ6rSGPHSaeewN0j0GdcTCrczfWEreuMk20gdlwttKKGLMEEccZ62CDTaSeb60+6dDmHwGPEGvszSdqb'
        b'7JqUetLVKRiFLrwX70uguGOlHV14+QoMh1ILx7AVl83JNtpOH3YowUYNAaz/W40l++iK0KV2rFzDShvBbVjOkeDlPaXr0EtAOeEd4lRqkgzzYTduavGu+EODNlSkUsd2'
        b'6AYTbJJYJ0/S3x6ZbGiCh0LoUKQRnjRWhA4X7A2A4UKqUoFsT4ZwkHzSQyhX5mKlB0HIuKYMPHHBDZ2jpAuLsOGATzWu4WiO5nV+ehZdUpkPnWSy1XhPmWQ1Rj2cwC1Y'
        b'iqDxHFHF+ljDdNK2SlzwgjGS+lb8MXJNj2NLDEh7H2R7YGsCubBuC5i8RgbRaEujMeLtQDBXR3pJrjP+xNWT2GaeiY/KziiVUhsr2a9JSZ+X7I3NUxJhiRDniYIGduAG'
        b'VipgrR8MOkSRSsCD69SAOmwxhxUKAKahpRRHZPRNSc6bOOYXawdPcUDOz5I6UE0YOUx+u/8sLPmnRdJYLsGdglga0V7yh0OwWYoNxdBzWUaEXR6p/rYSn94SXEjuprqI'
        b'YKGV6nS5+2vHYDf0X4V6brEODJB+kxBJv2EwLpNdYIVDPLPcID+sy1HENlG0jOEVnNWDbla57MieR/xUsVW76AWr2ZtRZ1mkzZHwiy2cs8JVju+hBBiWwd5IOQ4ssOui'
        b'mslmeqC1EBYZQltTTSy3J/H2GNzAxzKwAWMif3Po84FpdTYXsC5Vb1bCAZlsg0zSmj5lssUeBwt8esE2APrP3cB7BtAYdMiZ/MATOZLMU2yQiYDJBNZYEjl58SwXup+D'
        b'c7h5OZrQgsXfGYIBIiC58DTHCfrVvawi1XAuFtoSzsIdX9hQwWH/25dIMsPON9Sh8XxILEya4fJtQ58EQo4pGpDpbBLLNPRfus7BLj9HWI86fkPJByugH3o8k8kz36FR'
        b'HtFRJXFX4xgPdlSx/YK2ih65vnoNaL0ckhhFxrvteO5UFplxRwx02EJliIadBj7KghkvMr/aTLh3FO/4cLBcKgI2Us5Ap18GLHmGwSbUnnH18b2lh72k/4SL4/S8Giab'
        b'nMAILkjDMBlCnRYZzCJJqwUHHGAbGnXJTgfMYLMMV/M9SWl7CICascs9H0e8CVPKU86VQLV/LhnAcBl0lWmSWq2kXMfJNB3sIRB8QEBR74ZN0apOSPreimP+RIxIo8eN'
        b'nakN9+lo1Mu5xF+F3OJZPVg6T2r4BJavnyCr38YpH2wksVWR0xtyPsQSMjE0phofY1UR2zROS9BghJpZDoMZ0JWkWlocigP0lGUyq25oz6DWTBIlqORCcxEJvlH3BnWv'
        b'nzzoNDnOghh4YIuDOKYTrnieHMXDTC18IMLOQBriCdyMh/sJ1MTHngS4Y1jrCneRtfJt7LpAt6i5kl7MuiCsyNbFpTx2F3esMvWLk8N5fXu/c4YMNhe1cdm1LYYapNfU'
        b'g79QCCtc42RjM1EIDxcreHIc5ovlj7nKiIl19PhdxPYz1BMY9qbx3aYHL4lJRqssBsUchmpH3PDASvtEuE8Pr4f5vBseCoeCKY6fS8IhqvaY4KP7thGUW12k8V7juxAW'
        b'dsG6pdNpnL5MJK0T10VEMJvJjU2Rh15BQrbK2zZ4T420tvbMZRgOwq5IL3KtrSIv6L1gSbRjDDZP0dOaiZAMw5YyWfd9eKCCkwHQbF+C7UqhRmnZhHUVMmQigzfkhDBv'
        b'dupsiI6HIqnYDHQq2RjySWr35dRccdnoqCzPD++YkCDLzdjc4qr65OGb6Z6z8Vh5Ge55AyGTJ/lBAidiCLghxAEcdMsnwOqEh+RNxojoz9M4cSJsLkKDWQ756X6YCcfK'
        b'OByJPwX1IdahJLlKqPPJ1A/3P8fSmPrLt2AiyQLvJEO5+g1j7CZ/1XYJV8WkO13ncDoBa22OQzeXFG0oBGu8Sb12CNVn0y5TUNJKyF2nq0MiXk7ADjesgaFcFxL9Iweo'
        b'9iStGcM2+1iNVCfX8CQYS8C13HiC5WE3ZTkzR2cNXUcLwvRlBaxTPxt2jLzhjhkMXKC7tiuSaj3NhvrIi2QjG/EwfBQmNFJwIYce2E/dvH+FLGH8kkiT8KcdZm1hTp6E'
        b'WY/daVBnBIuX865on4apLKpEDCyV4KGXl0mtKj9PCr/sCC0esH2M/O063r2tgU+ZLOy3IvLcBiNFL1mtrPSyY7WyIkeilNuklCU4LcJH12WJ9VSq3yABVhw1JIa7bHBc'
        b'DTtUiEpGR5YGQOttI7MbRVCdqBMhVIgkDz7K/oPKk4T8XQQjdJkHy5puqijCTAkN7AYOXTwtT65yFXaUE3AcezPJ2z6UwvIi7IwSwfaNHDrVn3SZqMxjCXsAYg+bsJ1B'
        b'2r+UpINVYiMcNyetGCHbmY7KwbabxgQOAyzdTacG1F45la0jT1e0EXB0kTQaQmOJ502VnS+LTi85rBCGxFhHcfwwQffDeM8SJRJuA7sQipz/Wk6epxqsKheSjVSIiVG0'
        b'xoQ5CkxxPikM70DXeaqyCndlcEpRhLXnrNgfY9yBmjzoU6Y45S4MluCikBR13k7BKohk25uh4pd53ZMipxFDMtA5dr2bvjmfZNl5nMhmq7YG3MsxNvIlS50xxHV/gq0m'
        b'Ck6WyR1v5Eiywbfnm+HEEQpup/BuGfSZ2xD6rcnQwypxwtFf5FhiEp9KNl5BtlBZRGbQJwft9th81RH7Q8zIEpbUVQuSCP22cCoOpy6T0YyZkAIOOGM5PHGEGlzLy4HR'
        b'QorAaylO1j6uQWjZfZogfsntCDW7NR2aiDBI4aML5CtrSU87PK/iygVdrOLDPZwT0XPZDFF9zJFrHnlxBVoRNL4Lhy3JWO5DW0ohDHiWQP0RrJOKx4ZM6HWnuouwTJSz'
        b'G+suko9oIFYyoBGiBENBR2+Hk37O4OPS2CyWKGZB93lPX2c2Npt2hXFvsWU8PCGtagmFhRsZGqmEQL3KpOHLNjh67qY/dvhZklI81j6MFXYhmRewWYUIlbQkDwHJk3Au'
        b'OFCq9BzDsWN/7XEXHkvOpOMidgZjE68UH71eNd11SvLjNX9rp2ArLt6zZDheDKukdyUfp0LjtWAbaZg+zXBO0+d5NpLV14Y02rXsFyscU+xlOEEMeYRp44M0DY9IUqRi'
        b'1hzyQHVszjMctKZgyZ9H5waxXJpE1YFNZBp9Xgok+blbckaXBNDlFqmcqE6eqc2WFGKEZNXJUvajeDfQLxSqMz21KBYlgYzrlrJblMBgoIr3JcLvVhhIwhaiLGTDOOTE'
        b'TrpQ8N1WYlvkA1NaLM0rg3FRItbIwwNxIhlOB+x4Qnn0OewMo9Gk82SOVb50OAYP2aX5NRfUiMP129Gg3XeIMyXdqzCkgGDBMpbu28KE0zOrRASqc+yOCDTaFONk3IRq'
        b'W3KvbVHQepREv0g6EUf8pe0ogdwstLtSoFRVKAyFp8Gk8GPkJhpItRYNKGiqpMCs1tXiJtQ4En/bIJyYJ38wDPMmxIYfQa+LyKWYhy0yImXsCbgKk064JrYywvUrOB0X'
        b'qAmTMjeLRKFiIWFoG4wJ2IkD6DHQxQoS7DTBUQXh40R8HN2rkeTZFatB4wrr1ITWk9TVCQ89uWgFHExOkERefTysdKBAppykMouEpDsO0MjD+VjLcIeoQqyKIWB74Ibz'
        b'R2noHzpaAbsjxyS0uhEjaqEelYu1i/jknFoLqBdjsH32EjHKDqi3hEEZnMnA1gDoPI3DFyiqaqTwZVtGExsSTJItfPRxRhY6E6BTTMaybaFUhJPJYjFO0L/2MkVqcJ3T'
        b'xRiKImcJjtsccdHH/6ZqagqsmCvCqhIOBZBx3XHGWbtAsu9JqEZ2cqdOmWL4ZajQgwEhYQF0nQ6IC7skjo7TJkpUS558XdsF74ntHAksFot5hBHjMGOjBTtF6TjtTNFA'
        b'q6U69mmzUE4er+b4bbLUlZPEF+vY6SiLsFTyqPDEDvoLSaVq4MklqMkhzR+DqbNkwLPBt2FWSEHfIA3qbNApyQzMFo/8zNClNAqoxqHFWVv/lhUxz+UwNpDAtlTYxJHj'
        b'VOzgtrEWdIkKrAt1iHJNe+LaFUWsUMQtDgxeIXZdm1H0iFyYyklS3W9MzZDhP/Y09lIuxhktab1r+CCFTKMiiYx1IeIS1gdpaHlT4LID3WISZbW8hlScMCSSMKDVUY8U'
        b'pwvmdHHCXifYxB2WblBAUBOjE26T7C1DXm3t3EXJHM1iuBE9pA86nEggW3LUgcUcwpcRsvjtdFwtglULmIMGdysyjAkcyKE3LcUnoI+8GgF8K6uoo7BgCY+P5xLVHzyF'
        b'iymXSMjVoRe1Wa6JhNTj0RxifFtk0hUGZD0L/uTkBvkG+NCKsHcJR9UvwqPDBKzN0O8lDiGWPZhG3LPSi8XXBagoyyJ6r+9FVGFUV5md2QrBh6VqPnIwlX2ZoLjxYBqg'
        b'IJn0v/WqmWQtZA0+uEXCXDcgM7h/DbdyyaM/DL3CZGLNmSzCnIErZ9LIOyzhgIga2V5IrriSLiJajveTU2AuK8IZl7VV4OmRONKFHg0c97ZlhWKJk9oiXM8gtWGJ/hQF'
        b'D1ti3L4i5a6Cvfr22B6eR5jWqI4jahSDddwgLlUOO/nEd5ZPw6RquPlpR1NywMPYGSuLD/xzSe795seKDllkaEX4q6nisPrtolOKUH2GG0YqP0X6VwcTtwgJHhRdDICG'
        b'S4Szd6xgTUNEVrlFZrFaFp1N/jIHmnm4QO9niOitJxYT2g543IzB8VgbgqU+nLaAzTNXYNbILJBQoYMdYxqHpwRsvYQOs6rUjW3cuRURQjcdOwnt2Zr+4fTsDX2Sx6YP'
        b'rHmzWxQIpQ6fLqQnrBb9kJ0/x3Fq2/3z2PCX+DaaTjZB9wkjNsSNjZTnwIoa1obBnLSNYjzMXpLWgkkkGFw+Sbow53oRt6HeNsOVtLRNMnEyddiGkIydqutVtYYqAjZS'
        b'02qYdyQq/vRauI0Fjdg0bnl6w6QB9Cob6JH8G2E5hex19LQ7A5O6hCxTZtDriuUmhHeLMBODQxeg3yGWgKcmEAZSYskrzF1kacoIPogVH5Pipbtjlx2Ol2CdLSweicLK'
        b'nOMwlnmGPMMYdfohcdcBP4IcWA/BeutY8h39lmTQd21MotNx3FkzToxPw0jlush7VJ3QkIWhzByYJ/wapCfMh8mQJezkhVPs3kYq0whjpdRp8ld6OGEHnUXkUbrDMkmh'
        b'KHTptlbMgSo541M465qBPUFa2bAFk0XY7wob3mLsJtm14PzFQ7ATxbjgXUVZ3OFRK6tDNWFdip0dGXWFiTStAOjy1ddzlazgr7PFWTfC8S3SijmyhCekCtv5FIDOqJPQ'
        b'e5OSWetJTTcnWG3ixnun5SvAyiWcyAwPy0i9QmR1UYma0Eced1oOF4OhIRm6L1ppA0UZd7ApUyERZ6KgRd0r4fINHAwKNbTHtuO4YJgej82OXJa8Eg5VUSA9hFshJTep'
        b'9w1JKuS9HuDTQ3wz6FKPxOrkGP8rZ0L9yMobPbCzwCUF1w8TJj2mIW2g8FBaSAAxIx9rIAEZFrfvkSB7kk/AAq4ctiDT7cHR62RxzTBvTiFQg6oMOcipvBhNemhDCm5H'
        b'5NPYNCHxg1YBrKq52RKqDV5Xv618jMyrlyDnqTXWCmHQOZusch16is7w2Ow5dcf/nWZTfLvK42rjI2zzUhbDmIZ05jFC3fvUmQXCxC57TlBUIBtAJeNaMi4pkmWtUN8f'
        b'WLspYatBnHKyIZ9UvI88eCPx+JlSknfniSjBBXjshH0xpN19BN4b8mxUDtMGF0jgFFtDsxZWnfdjyY863W5WaATjDjjra4nEaIIMSUYNh2HI1ohMtNMd+jVJOP0F5Hce'
        b'imAhxoD0vI8beUIfRnVdoTwJ6uyIAnsQJhpdsNAnqGhPx0oBLIjEt8l1VcJyrBO7Ka+IBfIGmcIIR5hUcCYht2CvjpDEtK6GI2ma+FjWvNTbPV8b7jvDXMhNUqtx8n1j'
        b'2KuLq4VBOKlGXKeF3OhmOvmDUjkfMY3iIN2k/bBLIYy58e1x9rQpPPKUwwFCEpXUyzowoaqSDx2a2BicRjeqgHvWMg6hNKJENEgsa3zj0Dwv58hMfHyYkGGSjGgg4TDu'
        b'+BF8dcP9QG8PhiyjnsySWDiBVzusyqdizUnyz6SjDT4wryfgEBQ8EcYT8I3ToKzRXatUNaPJjTfBqCzcTYdqV5y0IQ9Qe6sY2l3ikZ0oH2Fg6YqbPgHKBlRnHCNDe6gD'
        b'D2zIynvJJuYprh5IEOiexE1t6I5yCc7zJx/6CB7hLJ8uuQNLxhquFHiMwoQ3TEkZkC0NwI6Zpi6R2SZLbL2Jraxo6q7BIi/vqBt92uYOI8eicZ2cJXapmrqb4qAL9Ihi'
        b'SG9qsUtMnmm75BLOnXC/AJVZhYSL92wZJ5hILNFISiKpZ6XjJjQlwXw+0ec2om9NJK2FUwSrVaauFBiuY434VHCqB8FALdbfsCHhLipwSPOmFFhqTAPZm1JQUgZr4fR2'
        b'FPpCKEYfgrm8AHwcLfGLy7jpfskTus3JZ1IA7O+By0FE3+bkU+yJx/XEkm3syCQRWSs/DMvWRTyeJBsZRWGsIVUYa5M+s7a0jZtWhMU9pJ6rrrisQ3Q3BjvkMnxg2hT7'
        b'feygjUcubliRreGhkkFh49aNtIAAogSVQRdcjbG6NJco9jY+9CYFWIQhAW45yWSR35nm4IPzuGFWBuUUAHYe9VOWP49dKZLv12bZyf7bN+AebLCzWqOwHkm9JDuZYOeL'
        b'iOmOw0SAFvZejzwWZ0f968Qpd6y4jc24YkDusTYehi4Q4VqxkU7PddCB+QA5Mv0ZqtjkQKKtziIj2FbG4ctQRZRgnnxLsz226stQH8cFNvj4ZjpxwOqkErjrQX65GYZ5'
        b'uKgjwP6LOn46pDEz5lIqhrh2+gK0KnnJEmxuYLk/UZppFtRO4mOGPHgnthxXEkVA1aVgc5fCTDncVokuPUYIT7TcMzsCWvKww+E8RdYsEV1yTb9JClJ3DOZVTwWTET/Q'
        b'hg05WI25nmWJj8wIuJ5QbFd1BTdK5LDa9zwZRhUFJo8IdNooaDEhYXcfwvsKcrxUbWyIy8y4LHTEvmAljq8WXTcLbdLQrqpNBtcBTzIVAq3scPUQO/1JfrsctvTgCfsN'
        b'3kMDQwr6GpNOexB9HzxBsngAjw1tcqAt5AiZRTPFPgVF0HuCxqA6EFfc5YnAbxItGPAt1cYRhVtS1IN2P+hTF9wki2und22wY5WTcB0GTSikrFRzCYcVHRhQcfZQuIZ3'
        b'grDKQCiDD6OgPR0GYZqUqDkylp0yxYdF7JQXjfsmYe88OYlKHLPF2ltCE/LSRIIuUt37YdSZO9G4WmpLzAzGyV7Y3yfVyscmFcWRRQ4B60yIk445Ud92yuDeIWwXEe1e'
        b'ySdtmb2mQ0o1XYY1t6GOcJyIx50Ygqfhy0UfEFO6bWUtMQLWBLzYmamWaHLBhF+Zp40jlU2xldQ/2vQGnR7QJVqTlizQwTFdF1Ma3h18nAYzMgEJ9JRVYkjjXCdc1Ycd'
        b'fOicKU9dqsLhQmC/BK6Ic4d2PnTpEJZvXcPeYBjh0eEEbIjI2Ty6RdDYQsZ0jwajTe4QjgYRlE6T7Bux/SbuwKa7BtY5waYNjpiGYkMW+11XIDtblRJB0qk6SqBSp8DH'
        b'KZEe6f3ydWOy83X78FxSuDF1B2pb+3Et7DpiZIH9R32JMJBt+JA2bGuk44oC9rmZ4LgixY1V8VDpg+teMC0oIXzpYNMrETaPsotONqThvkEAdMtTkDB+XBkeeNtDryNx'
        b'hSqdKE18dOSEtDTWnvPBOnm84xNBUfGmLRGsGldcUM7DFTuFYAcYccQO71NeJJQl6OOT1Y8R2FeXJhirsMtB1wkI1qHCmHR9lkO07HaxPalbRyRUyUu0Yl1I+L1z9SjB'
        b'wQDW5JLUJlgYWDlO1KMjNR1GXUif2Un4DqzXxiUnimza0qBWGkbSjeERH+Y8T+EqG59j+TlCr+WQa2xGSUdpItaj0GiOldYkmDktGCmDbnZfx9rD7JfJUjelndKi6M73'
        b'3JWwi7iD9DWWAVWqn8yhgI8I/R1CiDaYUMfes9ol7A8rzpPk+mDjSrEZTNnAlh+MWkhBrwmxq/4YmLxKQc8sjNoIif+Q13Y6lXsCNoKO5eOIGfQEwYTVcV9ckiKX0h1o'
        b'QlHtfVy0Jwc3yZpI73m1s47Er6dtceeCKQFbd2SCkrAsSi+WFKcWy0+G0DN6jngYeZUxxC5rr+Kku6UF9/Xk0aBcAa4qQ6XqV+kAD2PzwZLeFlgMK3DQzf8qLa17kQXv'
        b'ILdqFeyEBltTaKjEcFwYas7KWcmJAvIoj4OxmbntxnCOMySn8uKD7JWkquwcVR2fLPIRw/Ghi0hCrZJ5rZOKacGBUonQdDBBFoX3qHFsC+RYah4cTqbTy3Ac6NR1h4MM'
        b'iE032XmbEKnTUMVwXCUtxc6DtJ/VMHSMnVSDNYuDSTW64et9nhJZS2+wkNJxYjjh7NKtOWw9WHBa72aJDaHSudgpmVlrO+J7IIEp3fhgK64s1h5MxMVjpQXnIGfg6rH4'
        b'4CCpaxEMx4ohGS+GHTy9JtRbMhN3Iu5gIo742oAFx0+yC6Fk8esYh10au6aowCSE5EX5MBY8ycefSzbcLT8vRR//0tPnIAliXzH74e9LFZmELO7RbCbMghtGt5Islc0Y'
        b'tW3mFrCbun3i8GnTvW/nvO+lUh1dFfW/tt8X21muWqz/44fiaLU0l2M8eX6AwT8wvN/fS26tefNPqS5x55pTzH5Y8fGfHb/8du+HZspPxvxLx48W/aLjlm6rt257om7b'
        b'Od2O/N7WwN72jN622N6O67GtvrHtoti2dz76uGTS8q0PN45ru9m+cTrvN1+ofBwcbm74gd5k2A/xPVvRRy2LPy6LTU7z0veLF2p+7P2PSe2TzuZ8IT7dd46Pf+Ps+39y'
        b'PXvlfz6Tr3jwq+npX7bO+MrGHnrBS+xP9P3e98I3en7vcSNQ+enIr8b8hc+/WGvcr9Y/7PvqX55M5dWdi/zetKfeodrd73R89zv/oGmxWeIVF5Ih+OxdPYv8340P1PO/'
        b'nVH/YiBcPHD3auRiiX9QkH1Qnk+cfvBYqcnsD+Ivxfh+/1LMt5REJ948btKvXVShJ/phXdvKyTd7v2iOOxnseGMKBtOlXtpXWIws21dKF09uerj/o/6v9QVvLm0+y1fe'
        b'MlzR6nr5696akOcL1Z+uDQdkfzByRbqxzB2sPv5AL9Dc4eGJt/NLSoNj7Gt+Mf6jwsbE7lTLpSWHd3QvDs5/EdX35Dufr9Q1H6mPR5V3/B59pHNtYOwdo7cGR3/hv/2p'
        b'XEJn8Zas41sDhg6zrXHeduGnKzkny77be7vf4udvrTl/PyKNPIveJ3deRCc0av5Z+7sBb7h3aF0xkbpf9s5zf0dbF0envJ/M/dPbe+0ZujEpu9//VuYf5nOGjH66cfzm'
        b'/Ftp0wpPXPx7L8Sj4Xe2Rt+qP9WSX3qkyz4s982pSDnLK8m5Up+Y53ws+M33N6bedHtx1e5nP/oHrsf+t37EO8JV/GTB9fnoR6/ejnxS8HbGoV+nDuqMfuGeGqdrVRL6'
        b'Fne5571Dabe05zn981LShcPy74caFido/y7B6EdvcL5dE7pfwCid//iXx97Z/HHtJ3KFP78VoLSj8a8fz/14ocww+vn22Ze3Amtbe1TzHN4p+6P0/ntR+3/Q/2B78pOG'
        b'Lzf/tCP95Uffsr78PeWiV8OKvzJx+bNly9O3ZQb7SgqlDn3JXOZ++cN/6bOQ++wggy2fNbQQdoXpigSEmmFdIPkRstAlkP2JcRgMfGPbKBhy+oxdGp/KTvl+Y+snJuYv'
        b'i1njAiT5va6ZmsqLFQWKxAkaKHRcgvIiBXLlT3iMQSlf1vJg82B9D82/VLqGq9fyoSJUUZrR8eKRD9m4dpA5rQerIwqKFfKLsMMRnyhDPTQqyyrK4bxysRRjocQnr3sf'
        b'myX7A8KgDlsVhjWo9r+vCk2SB9DdQ/nSFPE2qR8kEFvgqMhTFROiz5IbyuJDrp0MtEk2FSYZLUFPATTJhh7Jp1YWkHes+yt3xBVpitvaij9jEzhnYofO38jy5osbkkRv'
        b'UJloEfnNH9vK/j9U/N2Xo/59f/LMbiprbGzs9R/8/c1fRP/tv4Of1MsKhVm5iSlCodhWhmEkP5fn8xnmyy+//HM5s3eRwyhq7vFlBNrvKau1OjRc6zFpuNlbMOwwnPjg'
        b'ZH/po3P9txdM58VrJgtFa+cWSpZs3zj7phoGvHAI+UBHr8ehJ7H3ZL9gOOi5ju289nMdl2fuYc+1w55FRj27cPF5ZPQL7egPtIyH1TpynqmYslmeYjh7coyaRqt3m2bt'
        b'mT1pRtujVv5dTeNnR4KeawbVytEnOpYvtZ2fazvXKvzYxPGlydnnJmefyR6SHLs9N3Gj499J8wRu+3IqAsNXDBX7pjKC468YKvbVDAQ6++5SdKTEF5zYV5AV6LxiqNjX'
        b'UBEY/JYqG+wdZXT1axX3+X4cgcErhi33I7lGAvNXDBWtos/Yl72zHEZOZZ+byxW47jNfl58elDw6uSc5uZciRcfvCrT3ubd49EDm6/IzScnW1Tm4gM++3zsjyxgceiar'
        b'82OBsuSyNK5Ad59hy39blX2/F0X31tnnHha4fc5QITm/x77dD+LESQnYrEh/5eXzg5e9UjlJFy7LCEz3ma/L30rKYYNPJa+vu8Ie7nkpSy6IlGKrfl2+kpQ9WZ9KXl9f'
        b'wB7uZR48wUuarfrN8nVFyQd+CtEcgfGnDFvui7mnBTqfM1Tsn+FySIQMFb+T5giO7EsrssNFxZ6x5M5CLg0O83X5+p7s4d5ZKUmVC9IC633mm+WnB+VBdfZwz0vxmAx/'
        b'L4pzlMpIzsGxOZUXX39Cx68ypGmEuHsBshb0Ucy/q/SN8lWR9Fm+LPdVsGywrCH3mazupzEqjJpJrff7msdaOR9Yuq15P7f0XCt8bnn2ByomwybPVUyHz71QOfaKx2iZ'
        b'/0TT5D+rc/i/VsfgP6pDvdcy/K0yNev3ez6FHI4gkPOemtGYwjMbvxfG/i/UAp4pBBysMB72NghxYd5yUQ+Vf50V7KT4g/9op9f/jwrJup6/svL5v4i9EsSVFFZfofwf'
        b'ypn98xwOR4Vdb/e3i/9OljN2EN/gSXurM2+oy3sf4mX8JqKZX+BLQ7j50T+LWt8L4tlrVDteTR36RYjz+7tSmr+8E5Sh+VLmzXLt7C/lLQz2Ju6Ib+p/9NIk2zdL/OoL'
        b'E6FY6efXQ6R7U9pCldZN/+nIEFfOYqRHLchiVO+nURH39X7wZy35ZJOgV2bGP+t695LVje7U/1FtYDO6/oGz9s+MXn6Qt/aHD3929sU/x7/46cjIhSCz984fCv5pweXN'
        b'Yt1HrZc1F5bK9Ase9ebN9IrPO/7Ez/fhzOSA4oX58bInM9PSMqe+a+n8nlH9rZXppejVqP7Qsp93G77z0763vd87XzOQ86vPXSsrtHaP5zPyhu/+64iMjK20ThJfoOy/'
        b'l3+HSR74WMHk7fwKWXvb/KqrIa0J9RqOH/xYSzfzzXzZzRpu0Qc/4bSkD7vet4bm3++9e2X320mmFzs+/PVYScdOx/QfDWu7X66ULEonZf/5U4PfCH5z8xODL7+QCU0O'
        b'fzx918JIsmRWARZQEhKHh0uScMgwIabysMjFRzAD7QdpjLvwiU1wuA1FkVSLXQejiluF0MKDB4qxB0k/JrEmGBqgRZLw9xreDWXnj2UYJTXeITecOkg8PIBL2MvuHSGG'
        b'oVAZRprPlYUteCpJyI0j7FqTBjtphqPPP8/gaP5xyYJfj3BoscJRMTabs8lEGjmMwJYLfXR4T8K/vcKzJezZDLrYPMhhHJiHJg8JI425ZM+u3rEhZirh11KMEtbzwsQl'
        b'kguLcQvY1T3wOPqrzM4mr7MCYzd04eQBKQ8NxCaLQD6jhh2ljjzYgI6zB1u+zkY4BdvKBFmHnXTkMDLYzpUO0pDkuc21dgt2cKTLgg9SaSmbQOVNnpsGjkpOZ1IDt9kK'
        b'gaEH55Xwsak6z95OKFnVGGhkjg2WFER0+7B7cPPPcWATGjwlAlRyglZ2SXgo1sGANcPw7Tkwo4Brkgtj2a+irGywCfsj2Xzh2RxYwzqeJIQo5qlZsYmzQ7ARatmnhpJc'
        b'+Ix+GR/uYDP2HWT0qcdKXAlmm0X9ZiUNjdggb8HFVhiLOMjxOwJzRQX/poZPkVwgF+bp/Z3P2E02+HgPu+VxURlXoDujAOrwSR4u51PgosgwBkf4MhE4crBAs9sUmiTL'
        b'R63Y2zFMSZo89HFxBJuiJIPnjYPwgFochDSeX+e/lnH6jN3bB3uv3AqGWfNAG0kyY0me9/BAiilaockuzMZCmvH3lbmZlnmgd6swESiP87jM7l7UpotVDE5gt8nBKtK7'
        b'OabsqozQkGKsDif8ucnBsQvqkviMIpE+di8QyeJP3FC3s/xq4adeER+qvQ7GG+dwtMAqANds2O9LsS6EywiOcqHhiOPB09exK9wqyMY61IZNEPCUq6DJk7uB3Qcyb3PT'
        b'D6ahCbalK8l2qOHqjtipxMNBIfRIbE8TtyQ5mizZHV9I5LhuI4+tXMkCm+0D07mbWWgVJMVwdBKCGezBTRyyOP33iIT+7l7t/5JvZNeP/42Q5b/nJUe/KiTByXcZNjj5'
        b'3+XMpwaMlPq7ihovFQ89Vzw0UPJC0bzc712+XE1IRcgzVZMxlx/wrd/nK77PV32fr/wR3+E53+EjvhUdf/Vf6yO+7Yd8sw/5lntcaSnNPS5PoPuhgsnncoyU0Yd8E7p2'
        b'X/rcKSlf4s7/6cvvDl72Ugs5jIJGefjvP7tORyr6nxJ/pZvq7PHo9U//Iq9FH0hpvquiUS9FH0lp/rFAslGXvLSPHoN6Sj5WPDTn+NgyaMlhj6147LGtgo8HD905VB4w'
        b'MMtdXpYoR/w2u22vVGFRXpZol5+VUVC4y0/JSKYyN0+Us8srKBTvSiVdZ1dJ85Nyc7N2eRk5hbtSqRTu0Ys4MSdNtCuVkZNXVLjLS04X7/JyxSm70qkZWYUiepOdmLfL'
        b'K83I25VKLEjOyNjlpYtKqArdXi6jICOnoDAxJ1m0K51XlJSVkbyr4HuwQj408SpdrJAnFhUWZqReF5ZkZ+3KhuQmX/XLoEYKkhydRDlsZs5dxYyCXGFhRraIbpSdt8v3'
        b'izjrt6uYlyguEAnpFJuZZFc1OzfF1flgV0JhSkZaRuGuTGJysiivsGBXUdIxYWEuRa85abu8mNCQXfmC9IzUQqFILM4V7yoW5SSnJ2bkiFKEopLkXYFQWCAiUQmFu0o5'
        b'ucLcpNSigmTJLre7gq/eUHeKctjUnV9zW8nwJPwX/4yNv6GwbErPgosShaU/onbKHE6WFMvg/lr5maT8b1O7Q9LetswbtvLerrw/yqbSEIuS0213VYTC18evw/s/6r1+'
        b'b5yXmHyVTaDKpjZgz4lSwixkJWvDd2WEwsSsLKHwoAuSJeR/Yj+XzspNTswqEP+IJf7FLGuVLDuXLI8/mEVwp7EqyhJ5ikvpDIftdygVpOMczisun8PfU2DkFctlfssv'
        b'OsXR2MsrIgai+lJW/7msfk/QS9ljz2WPPbP2fOMomr+wDnpXVuU9Oa1n2o4v5E484594j1Fp1XmH0ZM87v8ATAZcuw=='
    ))))
