
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
        b'eJy0vQlAVMf9OD7v7Qm7LIiI4Ll4shwLgneMEQ/uS8QLjbsLb4FVYHEPD8Qjoi6IoFG8jVe8o4m3JkZtZtIk7TdNejfdNE3Spv3mapOeaUzb/D8z7+2yC0hIft+/yPBm'
        b'3ntzfuZzz+f9HgX84+F3Bvw6p0EioDJUhco4gRP4LaiMt8qWywVZE2cfIcitiia0Quk0LuGtSkHRxG3mrCor38RxSFDOQyGVBtWD5aHz5hRn6GvtgrvGqrdX6l3VVn3x'
        b'Wle1vU6faatzWSuq9fWWihWWKqsxNLS02ub0PStYK211Vqe+0l1X4bLZ65x6S52gr6ixOJ1Q6rLrV9sdK/Srba5qPW3CGFoxVup/AvzGw6+GjqEBEg/ycB7eI/PIPQqP'
        b'0qPyqD0hnlCPxqP1hHl0nnBPhKefJ9LT3xPlGeCJ9gz0xHhiPYM8gz1DPEM9wzzDPXpPnGeEZ6RnlGe0Z4xnbGU8mw31+vhmeRNab2hQNsY3oXmo0dCEOLQhfoNhEcwb'
        b'zECVQVZY4ZtWTprW/rRbcja185AhvLBGDdcvuHkkX7pWhpC55lq5DLnHQOGj5A78tJKWovy5pJm0FRlIW8784mQlGjtHTvbiJnKfXBhokLlj4OGs5Oy8nKScZNJCdhQo'
        b'kG7jArJdVljrcA+Am+RgfiW9q0ByOYf3P4KPkef07uFwB+8gTxYkspcKckibIUeOIskemQ6/gF+IxAcMvHsIfWoz8YzPS0uHJ/JIexHUEx4ns5Ejj5BL69kDpIPsIYfo'
        b'EzkF4gM68qxs/oZxGeSYVMdGcpMcdY7At+kT0BzZwaHQHB5fJnvL3XHwwPoxZJ+GXA0nN5y4hdyqJ9cbx67EreFhCA0ZKVfFNhg4dyxtq3VgNWnNzyU7ZEhG7nFz8V58'
        b'GHfg3XDfAPfz8Ivkdh6+FA+TsT2P7MAtRaQdH8Sni3JwW0phskGJsuaoGovD4Xk6c1EDyHFyDXqUX6RACnwUb2nkyCnHKrg9EG4vJzvXJA7lcpOTCpKNHNIOkIWSg2Qz'
        b'3GUzc8ZuSCT7cWt2UgJpyaeD0pBdPHlWS/ZVcNLSw7KidN/S76IQGQyP6P8VIj3xHoMnwZPoSfIke4yeFE+qZ5wnrTJdglOuOQTglAc45Ric8gxOuQ28BKfVgXBKOxvX'
        b'DU5tIpwaXCqkRZfrQ/TmpB8Mz0GssDZRhuTIPIkH4PXmGcVCfagaRSD9dJXZnL9kygax8Pp8BVKj1OmyGeakdsVoVBMKhQ2aWHnSpM9GI/T+2L/yN8f9I/QLVBMCN558'
        b'7AB3ucgSjmaY037j2FRbKRZ/te6v4R2rfx3LF7/H/Tfm0yFfIi9yJ1PAuDsO9kQraU2ZGx9Ptqdkw/rj86XxuWvxEwVkZ5IxJzm3gEN14SGPbhjsnknHmUy2OV2OZWT7'
        b'qpVuJ7lFLpPr5CoA6hVyg1wLV2tDdSFhGrwTN+Mdaanj0yaOm5COb+HLcoTvLQkhl2ZGuXOgmoG1+F5efm5hTkEe2Qk7dQfZDiDeQtpIK34mISU+KcFoSE7Ez+Fz+GIJ'
        b'vH+V7CdPkr1kF9kH26ZjIdSQGhZJrlv9EEPnnc4NBUBnqg+HySpl0oryzbCG62WwojxbURlbUX6D7GGYR9ZtReWFDorpbb87/C+ZczJc7U57J8/yevmH5urKi9Zs7ury'
        b'mP/529WYw0+8mHSmclvZNt2ZpD/qXhm0rfJMUvSu7FRZ1SAU/bJmRM3HBoVrELxeHYH3w+RvTyMXYBJgb8qncPgKLMhVVzRFfdVzEslVmxGmpyWJQ0rczicPH+SiA8Tb'
        b'yMH4RLwHn0mOz07m4d4hPlmY62Kb/dqIUYlkN76ZTNryxymQsowjl8hdfNtFty7xkJv4HmnNxpfwDXwJaNd6LnMk2WngvHy8wSBz0GF3JufRgwHTKh32BmudvlKkPkan'
        b'td4y3Stz2wQ6G04lnbBZoVwk56CXDjpdBrk3pM5Sa3UCpbJ65RZHldOrMpkc7jqTyasxmSpqrJY6d73JZOA724JrCvEOFU0UNKH1zaZt6Ggb9yJ4JcdzSpYyJJ2e60iE'
        b'QXKIn02u4gPcLHIJX82s4LuABFvFNAoSPAMKeaXcDxSyXoFiS9dt7q/ODxT9C910scbDCp535kO3yXmkJTfwWXyW7HD3g1vWfigPbnAGFJ5NPOvIeZHAeExTyDXAn5wC'
        b'4efIbViN7Xp3FNxZis+TM6SV3pqDVGOAbB1McEdSqCTX12qAUnH9oJFafEehYcVkW87MRFo8Fzmmk8Nx5JqbdhHvDcMnEo1KxC1B5TZyllwYwLozdgRA2J65FI2gcbUF'
        b'xuXi05vmk4t1sI/3wKQnoSQtPmEIYdgcAOUY2QZ779ojMLFkK/wnh/Busek97my82byO3jgN/6c0ipMB1GgTeVGF70BlZD/8BxqxmQ0b78O7yfOjphF26xb8x9cGsZca'
        b'8M1M2OOH8R2YaPIU/MdPk72sGcXcencBYeV34f9acocVrxlUktCI74RD8XH4n4q3ikO5gU8W4gNV5GmesjQafGMgKx9AduEbpG3oPKhnLBpLPPgIqyYU7yXbLHBrD0Be'
        b'Kko1rRPHvZWcxicB2+yHYrwTkeenmQbjDtbXoYmZ5JqTXFsFoFcP+/McNwo/uZ5hBz9C4iUIZOBCt3sVakSPR6znGrlmYAId8kbuSX6lnLJ9bM+IG4f38sZUL1dh4MSN'
        b'Ifdthgeh02psTleFvbZ++iJaJa1fidwzaFcP4xcG5kmcBm6DzX4PqHY26cDXAKe2FBWSHQZ8U5aWhlvzYPqvOTXkIgKa/4IGX8a3yQHbm4+fRM4OqCm18BYfPbr9rm5z'
        b'cVTTm4bm4/9Knzz5Qcx0dG2cRT/uhQna/TlLY27/bMJfPtdNv7hpyduNthVrTm8rOScf+crS1Pd3G9KfvXdwYNMevSz/7U9OPa+bevyRtEnjc9bFplunn4n5fNrCnz7V'
        b'sFJd8trv6z0Ld7Z8eOPV/N8kXHltzm/e+vR591+ylv+h/asv/vX0ruPzvt54o+Pif7lUzZi9X4cCtqTrQS7p8L5Eo4FsT4KB4yMOfJFPH1/pGgz3VpDN+GxibjJpzskv'
        b'VKCy9Rp8hSdPkQN4G8N6I5fJSGsS8GLACSrxAbx1GT8SZumGizF0T09CjAaS7cBikRZ8MVeB+uMbjeNlZPeaRoaqycFheBfF1RKirtVRVA3geqUbyjTIuxR0WUivxlpX'
        b'YResJopHGQYdRsElW87JObX0I+dC4SeCj+QiOC0Xwzl0AZiVc3pD6+wmJzD21VangxJ4B8VL3XvCOyLodbgfodJqcvwI9fnIQIRKOZg1y3BHJxxRGJIDSjiABpHd8tUw'
        b'9NO94FZGboNwa+8Et7IrwfVvFj9uDRFZqH8u6V/9dy4brsxL+wHRYYVT8nISrsv0HDKbQ9uHZ6NMVvpGYj/jLhnsiXqzduojoeKjoydrxqRzIOBEmJP+XFOMRNR1ttCZ'
        b'ngpN4T0JBahcSTbbJuZX8c4lcO+HC7M+MX8MVD3f8npl/L4PN10+eHXxdqHkQFPs1JirMYdip8Jf2bTWpE01r+heqcwctm2EpnlpaF7orMQ9o5q/vwuHlrek/zzNlfqr'
        b'Ta+b/6cytPK9fBkalBb1v+M/NfAuigaLcQtuTvQT78lmPjl0uosCAjlATpP2RGNOUoIB2IP9RmDDSAtCMXr5sgokoYVvhLF+FdXWihWmCodVsLnsDpNEq9myl8UwSIuA'
        b'FCCrXwBkySpsgldVYXfXuRxrewcsOoWO/n7AorUs8bdwNgiwEukeO0+a8DMAV9kgyuD2olh81JhbAHwNaUnBsKmAhj+KDyvJmUGLg2QAP4gxjo4DIOvk6DgGYA/n0YOI'
        b'N+3l6G4ANlIEsPCq/mjU0uEwRebGB1NWSrC0aUo/pEfxCoClJCW3AJWyUt0wOVKnVgN7Zq75zDJPhLDZdSCMyn8HhMKsdS6Si4X9k8NQzPh9clRszv/EpZee5Aag+Kgf'
        b'c/D6tKPz1WLh2oahaHL2Fh6enGaZuFgC8HVxaEZ2Iw/ND1HlG8TC5xNHo+yl1fT1mQ1FQ8TCzBEGVDzkCRAmzHz/5Hqx8GxDMlqU/QEHdZbPcMaLhedSQRiZdh9kDXPN'
        b'9wfFioVaYyiKmv0y3R7aI1kZYuHCoWNQftQaHp7kP4BZY4XHhyeiUnObHJ7kPStTxcJ1M2NRajWvgtaXls4tEQu3rwlBEY2xMiis+UKlFAv/VKhDQ0bd5FCqOelXNknA'
        b'GbBxEBo/LVwBdU7T8SPEwnr7cDRtKez4VPOQcm2pWLgidwSaveg+8A3mmadiosTCvy0dCMxKnhz6ufSNRptYuHVtCloahVXw+og/PJItFrZnj0fVQ35CF65Eu1hqvZpL'
        b'R0L1DFqnI3a49PoX88eBXLZaCTPPf7WiEBlGMYwxELeSE1QoHUlujEPjashhkd24GU/uplNE8iK5lYbSyGm9m6LdmeSQPJ0yRk3V6Sg9o4IxX3mT8b50aA1YsIPj0fgV'
        b'LjdFzgPI/eh0APuGdRPQhHX1jAvEL9SS2+mUn7yFd05EE4Fxv86qwJsX29MpK3QldxKaRK5Ws84Z8G18Mh0AsA7vm4wmh5ErrBhfwB35+Bq9Ov3YFDRlWgGrnGxeAYLe'
        b'Neg0aek3FU0FRHNGHMzlgeQG3R8g3h+ZiWauIs1iPYfr8GnKcuQ+NgvNAm51K+vLmkn4AhUAYq2z0WxyEp9iw8F7H8txwnCq+s9Bc2ZWsdkgd2aGOGE0quxMlImf0Yq1'
        b'PpVJ7jphLI+RM1koCx9ZJT7bpChxqug8n89G2dMc7NkRZDd5htCRDMenc1DOzFL2bOij4YSOg8fP5qLcung2CtL8KL5FrvF0PGV5KG8NaWfd1eEtPLkG/ZXX5qN8fJkX'
        b'e3Fp4WRyDfo7Y1gBKgDuYC+rJNKJnyXXoMs8uV6ICoHLuyw+3pIILDZ0OmFtESrCO8ldVveKmInkGuUU26qLAb3vWy7y/njbVKpVm4+B4547HaqmpUsX4U0aOVMlnSpB'
        b'JQvSWGlcZq6Gdnn7iHloHj5HnmWl42Bt7mugzxs3lqJS/MIgVpoIvOweDfRZTY7NR/PLEJuMsgp8VgM9Dh+zAC0gV4ziZGzBOwdroL/A6e1diBZuIAcbdCMXT9VAZ2VZ'
        b'i9CiQfPZy+408gRupXXPXIwWT17IAGU2iKbHcSvt635TGSrD1/AxkY+/hDeDkNlKAfw+vroELYkh59juGbdhEqpZM4nuyLSnXCGo5l9ff/31lUQFUicNoXir5usQp1iY'
        b'PgVQafGbCijUfp4lR7bv//5DmfPnUMeBr4/W7ny0cGZG1NY3n4r9coC8Y2wTH520qT3ssiw0/vIjV9aMGjU9Xn/w/LAxs7IuPu7ROGJLP5ubtmX3kY833Jr8v5qEbGPH'
        b'6TcGlc6Tx5273zFn+5BP4gqE8x9MVn+2yPzkodH7Flv2fnHxHcE9/fJLY5Y0ftB/a+2YxkrPvsfvfb737rETKs2yVcPf/kHm41NVV9L3h/w2S/OHvb8qvHJU/5U7ctfy'
        b's28mfhXyyud//fJPL79kW3e3sn7/sUncG299+HnlyokPWjPTL0Y2tS1e0P5a4eYDr/1vc90f/vPYT1RTFzxXC2zsULYRYNW3kNY8bVIhVX/tBNFeg5/hybPk1jAXnXMV'
        b'OZBbEZ0YINm7KkTWAGQw/CLwZyD0FiTnUuVkJLktw3vLiIfTMkZ3A96ycmoqMKo78nKodK+czMeSdnLCRbk7gJkXyB4nvpRdmBxPFZhkpwz1I7tkCSBAXI4jHoOiR7ZC'
        b'1hMPEMBs6CRmw11hoowt4zSoShkJWk7OUz5DzUdx9CeSlwNHMIjmZRGMB6G/Ss4R5edCZMCFuCt6Yz44xwA/3xHFKLmP7zgapCGg5J5cyFrSyXUYCyBhytYG3IEMZJMC'
        b'71GS/b1wHFTniAI4Dq5XjqMPLK1K5DiuZoRNPMhDE8AbNCXKJI4jtD60up0XGdXfrStAbKtn4tvZlFF12oBVReUha2yl65oVzllw69//+OwT8w/Lqys/FD42f2heLvKr'
        b'u7Mtocq/lhyYF1N2cFRG0raoyoi8Iyf2nWi6so07d3lz++jB57YBAXnxibD89PcNHBOuHifX8Ys+kAvFHgp1ZOt8H7vZy+IPEhff6XK4K1xu4DdNDmul1QEyjggIWjoX'
        b'GxGvBkGGMZzRAUstd8LDva/1QP9a0xc3+9d6U9Baj6co6RlyHm/yr3aK0ZBQYDQk5xbglpRc8lxZQV5yLsg2IB/iJ/H2UPIEeWJgr0sfzGz2vvRBCmH6j++29MpCplcg'
        b'FzLJVg0dHrmIj5M9CB/EW/FJBgCCDXgUdGAB5VE+mzsBZdr+e/YDuXMS3Lpzc9kn5tfZWn8Kf/MtK2bWVH5giV/wofljdLXkAAgopaKAMuPfZuUbWvT1r0J3uyMkeWNM'
        b'mGIS2RGIU/ClYhdVx88inkRR2uiUNObhE/JlM/AuaZkevvgxXcSM4KUPFZc+RM1RicMRE7jwFd+48LH+hacvttAKI9jCoy+Dln4clGlAMA+QLgJEC254Sm7nwq/F50NI'
        b'cw5p6VWOlXXREfYux275ZsWxUtz0HyBddohsMuVqa96aoBOZzT9mKmrcfASTJ4bIzGLhqTjZsq9l9MqsPWXYgGzNb5fJnfmQV6f87Zn6D82fml8rp0rnD83nLK9VpqTx'
        b'f409HFsScy12U82ZjY1RY0K2FY7R/0gLEsl8d+rZ1Anp29NdaVFpW2VfvqQ9Eot2/D3izXcXAWxQgHyMHBuDn8kvSMJPkmdAjsnj8NVS3MJ0I1nkHtlKWpNIe0pRAWkr'
        b'jCXnc/BFORpYIp9IWhb0VRwNq7OucZkEt9UkWFwicESKwBHOc6FAGKjSgwdS4BjkBxK5V04f9obUWC0CvLf2G1QdVA/kGOIHGlrRzgCg+VuQTDqK4os7+BY+A5QYX4rH'
        b'LUWGAtymHlnEbH6jyVVFGdmB91TIpIVVBMLJRBFO5MwopfAoK5USrMiYPlkOsCJjsCJnsCLbIH+YSKrsBisKEVZeXJlOCVvE5nBzyX9jlotgMXcGMEzwN36WOf9B9Bpk'
        b'G/9+ssxpgpIfvYiG7jDovpeqla8fdTzltdV/9fwUb7pgnXu8Lf/m/WcHjC/7U/X3whVr35sS++gR4cef5s1ommVcuXLrofEPxodNWP/Jp6+cm7V5yYNnjn/wy10f1B0v'
        b'3/ikImVB4dQ/D/9iUEzc8T/6VHCnyQmetIaRJtKaogKe+yQ3H5/rzzAMud4wDh+Z2GkzPUaekTOOp4pcJvfz6IZsxa34CGkr4oBt3cHjLfjkcNEocZk8MQBvTgC+pTkF'
        b'EJS8gMP3V+LLzAxiI8eHwY1nphbgi5TP38Jl5eKjvbEqyofe6gqX2iprF7CMEcEyFgASeBUdgGUop+V5Xs1H846hfuBUUOAEiKTw5lVWuF32ykB01uN+AKClW8oxLBhQ'
        b'aaUHAwD1o+hAQNVTuKubm1eULIGoCKDDYS6v4pNychiIWc9EjJJEv80UVSq+CyELg98B3UB0uAiityf8EHVw/5quijAbPhgpqeXORMehGWhTrKbePGRiY4pYiHlq2Sxe'
        b'rTab85+2SebO2goNikLvDQoFZmdFsUwsfNbVH41CP87QIvO0303RiIX2BUPQZBQRFVJsnvZa9HqxMKRuApDK5gLVDLPjzpq1YqFVr0RatGaBTm/WNs3gxMIflcejYqSP'
        b'UprN5QuFVWLhadd01Ij0qSGpZsfBRJNYWBHzKFqD/iXwxea0jAWPioUkZypyoZixughzZJOuWiycsygWpaJF4VDnUkVUvljomZSMFqGYNE2xmT9YOUgs/JmRapEONMrr'
        b'zVrFjLGSHiY7A1baPI+rN6fdGSCpcS646e7OrtPNMOf/0i5pQt5ZG4Zi0AGTChhFnc98vGnaIDQe1ZcrIsxDBmZJs/TI8omoBp0L4fTmkv9kSeqRt3TF6DjKjkP15uVf'
        b'TGwUC783V0CvodvVihnmzD/2k7RVP7ZVodfR8Ui53qy8N0N6ckpcNEpCn1sVevPS7SOl+TwyUoeGoOZSWao5f2PxIrFwVfk69HekHgzAMLF9vaRd+UFkGkBMc5UGmSN/'
        b'P3CoWPhy/5FoNlLTJeaLhw1GtllFv5Q74wGG9x/71/wnCwpJasTWV6/87bPdZ7a8MiFpsvrWhycHxoT8PDtb+H75i3995dOGqEI8brKqYk/m5diNb9or/92xJSk+ZXbE'
        b'9NLijPzv12xWf4yy1KFbFaoDJ0bFoD+ozyXV/2iP8UCuRnnkex9vDH/3LwsufvHeqF+OUulfKiRlT+Jf8gufWj74Ts7vXvnrv9XGVweXjCx+Y6n51fM//+yZjr9sqxu+'
        b'ev9bczNOP//x9vnf/8+EX9x+6uf/HlreMGAvl/L43y78rO3U1AsvP/rPZSX9Ry1YVr95zMrPplT9dfVPilytf8glac6BX0X+aeGgXy1uchz88C+X89/6xY/GLVna9PbW'
        b'iRuX3TG1vPO/T63Y365649l3h+cce+lv+49+MOd106nnzj91r/nWm/2L10WfuhvxZFr4X3Z8/feWN0f+POWx/06wnWo9ZpAxvDqzzsAo8zhyRiTOfspciXeLeHX3hIV5'
        b'SfHZwPxw+EI/pAY5cy15aqNoQ24iZ8iZRKDsCRySuzl8I4O0LEo2hH0D9vzmpBfcHKiipri33FK3wlRtr7FRbMoQcKmIgKeoZYCC4XcU4w4iOD0zhEQwTiGS18qpgYRn'
        b'ZhL4kXX5y650Mi08H8mFAvJWcw69H3kD+7nWanEE4OteiAnniPOjalrFswGo+udRgag6CVG9zLEcEVfngnjdWg1oup05OOwEWR/WJ0mJHiVXlOQ22RUbJC4opL/OSorG'
        b'qPsYKuMFDVN58yCF8IJsS0iZzCoX5IJiC2riyhRwrZSulXCtkq5VcK2WrtVWOSUBlbwQIoRuUUNJiAdY3rJQJqxqvaoMQXBYnc7CCqXUvjqQhEylSE10t/G731SqJUKi'
        b'bFYDIVEBIVEyQqJihES5QdWTQ4UM9cQXKwpFU8yhON08+PN0HYpDceQmvi36Wfxk/N85pxOuvnrrp0O3j9Px47TyP/1o9PtlucsThr2k+XANKng553zhEz89/5tPr/3l'
        b'J68vz7r2g6h9Kyd+dOXZhNePacb9ueBO2me/Upbfn/Di+1NXhfzjw/xHlv63dujO1JZ/rHl3K/7gw4M/eHncS9//PGH25TRVUdJLv/i8w/0VN+XW0OmHtxpC2Q7Ch2GT'
        b'3Bf3UN2iPE7cQkNmM0+LeryPGgUnkr1+uyC1ClqHsrv4NL5PWqnBcvcCyWZ5kU9fiu+LBsWbUBFzuYKNO5BWTO7wuAUfX8KYHpBZCxONyXPTRXntFJ9KDpMXRXPldmjv'
        b'HnBSO8nOvGRI78ThnSqkieaJZx7ZzFBDGPRrN26lXlynzSmkLdGAL8hReIjMtZq8ILZ/FD9BnmaPkN1CEj4vR0o1H7sMnxcbaZ8I7FlrCvBjxhzRPW0BORhJTsvIE6n4'
        b'HDO6kudl+CY8YzTkFkSTm8nUj6uVJ7eKydPd+XN1nzFIJ4ZQmUx11tUmU6eRdCMw18w4quaigTmjV5GcUvppCJeg2Si9J+52tVdWUeNktioQO22utV51vZ0a0gWrV+l0'
        b'OaxWl1frrutUYPQmZigdVKvkoOKDaP2iXocO6kfpiPejiZGQ/DsATWwbFIAmuvXSz71x0u88+irdh41ouahV4goNnFdtkgxzcC13WmsCvAbE6VJPq7HUlguW6WFQC902'
        b'qCHC15bvVl8bU5joTAHyS/C34W/IQQ16Ol8b31jjFrHGEJNv1nupNbzPtVaLtapM4gr2UmdEtzqD2GQjEnU9gCP7xiBv+WZNj6zQZtt1SOakaKCs7P1PzB9Szc2rVyq1'
        b'le/VcChKx79XPsTAMTQxzU7OwzbEzeQiaffvQ3xovOQP0rM8bXMGaNw63bA2wk90wwDfqgc95VPmsHnqBHE+iNYl+KcuBZJIzieob4Kfz3WBYNxzI4DS6T+DBsDVRD3A'
        b'TCZvqMkkeijDtdZkWum21Ih32EaB3eiw11sdrrXihhodvKtS2HCpx5jF6ayw1tT4tnV3jRGAmPgYPMKGMAKSL5CkMFQrEBcZoeXYD880ccoxU535OYbcZKOSWlFClwMG'
        b'xRd0QYurkf46d3ABdJkrk3XIOsI7IuA3rCPcxlfycCX9CHybUkiidDvARTUC6Cal3CFAg+VWBVBu1RYEdDqkjQfqrRBCWV7D8irIa1k+jOXVkNexfDjLh0A+guX7sXwo'
        b'5CNZvj/LayAfxfIDWF4L+WiWH8jyYdCzUID3GCF2i7pMR0ciUB5hUBvH+qwFfmOwMITxC+Hw7lD6rjVcGAZvy8oi2MjDheFtvJAs6T9kgl6IY2PrB8+PYG2NZG1FQn4U'
        b'y49m+f7i2x2qDnWlrEMujGmTCUbGXYhO5nS2dJ7wyhAhXjCwGqOghgRWQyKrYYAgY/s/BbiXCoYSH4wN1Qf8k0pFz/egOwalV24DltMrpwDYE7wVVqikBac7ROfb2ZkU'
        b'SYhsUAidPGlRff7IukqdhDxUjClSA/JQMeShZshDtUENyEPGmCL5+1/Cfg3qFv2XU2dz2Sw1tgbqql9t1VukQdiAMFnqKqivf9dXptZbHJZaPR3QVP0cG7zlYK/mzMwo'
        b'1Nsdeos+Ldnlrq+xQiXsRqXdUau3V3ariP6ziu/H05eT9DNzZhloFfEZs2YVzS8sNRXOL5g5pwRuZBTmmWYVzZ5jMPZYTSk0U2NxuaCq1baaGn25VV9hr1sF29sq0CMI'
        b'tBsVdgcgjnp7nWCrq+qxFjYCi9tlr7W4bBWWmpq1Rn1GnVhsc+qZ0hnqg/HoV8GcCUCqundHmh660lNZv+iV70CFb3pB9BCsjoe+LFFc8X0pA3M0ryg5fdzEifqM/OLs'
        b'DH2aoUutPY5JbEkfb6+nZzMsNT1MoK9RGI7UIlz13OO+1OOjt2Jdvtx3r0+ktGJt4vV3qCtIU95d+6ktZKrZ9eT2CNJK2pKMuNVIzz7kLSTNeeyYxnB8Uo5fnISfY8qE'
        b'WxU70RAOxaQObFl6dFQ+clNTCd66Fh8lrQX4YjFV9rflpZAWuCqaJ9Yxvz+5lE2NoAUFOQUc5adPhpCbhYmswnwz1SChiNRVRQOPVS1Fbsof4CvkVhw1qibmUQfB/LnZ'
        b'IDVLXDXZbcDn0bwM8izerSL7yaZhrJ778TJmW0iNXrBg03hJObZgNtPf6lOjSfEZ43DEREZ8uiIysG7STA9qQF9TSrLJ9nx8oEGJsshpJbmSP0700bg0cJJzJfUM2Vlt'
        b'h+6n4gu2N1ackzl/SFHWsh+M3vlIOz8uYvbbq97c+dhPx9Tz7S8NzX4yO2lzxojULWNO7Dk0+NOQfw5ZN/6HY9buM+3Pq5Nr/3iGI7//X8NPDq57xPX9OVPtG3/mOq75'
        b'xZeuU1/8vUHzUfa7UcP/MLr6xKKT9xv+ZphVcWfPTw6eGnvoJ3/77Z8+WPGjoobPTlQdbTxbkXqww7C1snD4/U//lGff9/f9p183Od5N//Xs/xr+k/72glXFztOyv+Ud'
        b'2/qB7gPt0SOvlkfv/Z8fzv/DILwWfTGqaq/GuaBs4oQrbY7d7z/gTlRnef+mN0Qyozc+o8C7NTA3hgJ3cgLZnsKjAdiz4nG5Gl/A25i0I5DnF5LWLub0Q/hF8qxAzjBx'
        b'hpzIHpxnzC1Iot6xO+dGiUdhBuHr8jp60IWJXMP74wM+Axm5gp+hRrLcTBdlIvB2fMjpNy+RneLrA8gW6gAqI7fnuJlANL4An+9qSrMmy5dtIDddlI8hR8kT5BqsNVSR'
        b'SOgZG8lSmQcDaxfN8Vn4ygxyUoV3FsxldWoW4RZRoQCwoESauTw5TvbB08fXiEJY+3p8BLf6+qQgd4eRQxx5YTQ5KqqAXsB3yTYq523PX9BfiWTkMIfb3bVMCOyH2/A9'
        b'+rK4tRRkZyp5gefUZBeb+o1lAM9N+DaTEoOkSHKF7HdRoumMWEGlxDYDOw8lTi+tjBytV6BEfE1BtpL9U8VzCac34KusqvxsvIWDnhzjQEzdVsruzsJnqXmgyFhAT4HQ'
        b'ft7k8OECcpKNEh+onhJNmmlXC6hrA1WB66pkU1PwTvZ2ITlijcH74X2Jn0O6WbJMfHS16HJxltwYiY+F0teTYLqpWyvS4XOy2ZPwLp8JS/f/rPbqyqQDB2wDqi7Jr5k+'
        b'/nycmrlfannR/UHO6XgtF81TvZZWcv2NgF9llx+est7wo+VBqhPxrdHXQKHIEoeI7Ds9meKYgnwSaheGupPz77NIblCJlfQPrp3VmeCvmLHcj9CNFCQ1/H5MoNTQret9'
        b'FR8VJsrn9CLmLQoQeqU2fELvg9GlfraIEixgIXwUK95htQjJ9rqatQYjtCIT7BV97ZHcVG6r6KVDS3wdejCKNg8sVa+tf2OzVb6JoHxML+0u87eb2DvX8+2aFxUDDnpc'
        b'sJfGLf7GjYEs03dtP1RqfznnE/l52FYWUfJkQNlLX4TgieiNmfp2HWErwTtm+zZBL32o8vchpS9M2Lfrx5aAfoztvR/L/f1I/mb27TuAxezem6/1N59ayiQSaDlQ5aaX'
        b'llRfw04w99iD7661kQSvBye7caOzqCTh1Nu67Eun1VrLTkyD+MIEjG4v0lPUklQ1D6QYGNEct8OuL7asrbXWuZz6DBhBd+Y3HoYJg4UXV000phlTDQ9nj+k/BequMC+V'
        b'ztjSk4O4OZGRMvkMsrWIA3bo3Epb5k/VCubH8siGw9RfKNvy2h/jSz40v1ZOvYb48j9GvRJ1Ztkfda+8tH+NUr8z7sAT6WHo5dMh6eVvGOSM1ubhtpApuu60kjTNZ16E'
        b'WXhLuZ8XAnp/JoAfAl5oyFDGTeXjm7MCjhxvXAXUXJ/FPAXGzsO78hg3wy/jynBLCjmIz/em7VJRFZPvsIzkVLQRrQrloqk2VUL20jOF31LNlQtJfRDB2q0L1tYG1w8v'
        b'U+LXi/8QVQogD9cn/yFRkyF/4OkGCPOsLlER4K5x2UAMlhC52ynJvSxIgMthqXNaAg77l6/tVhGtYypThUw1F8AzUBX8sVRZHeZepDP6r7teU/JN+TinfcRR2WQepZp1'
        b'1nmJyE39YfAh0hHbVeiKDQsQu7rLXGELbVmfz+bYWdp3fjTnE3MuQGtSyUfMl/FT4WOz/Cdh1w07fp00J2G01jBjVf/iU01Tjo7bKkJtwqea/W+bDLwoJjxPzuNdPjnB'
        b'nO6XFORqcjfSRclWNL6P7/bIrSoS8D6JW8U3yW3J/+ib7JdOq8vkWx1GlBl8RvjgcyPifDxdQ6wPirq9U+hrjIHklGCg7cHLiT3RCb7UJawhCHybA/2cemm4r5YAXfBr'
        b'vSD5bcE0pq+Aa/SdJqK4oWd/K+bKwtxYqKbQ78rSm7eVjNFH+fv5XA/KNv/msjtsVbY6iwv6ZRMeRg7rrKsllD3OOK4HlcbD9TiCqCxhQ/b5SEJDRn2JdaXb5pBmRICr'
        b'CpdesJbbXM4edUd0a0MPnPZaH0tlAyppqXHaWQVi1eKkVlodzodrltwVYo9mzcwB+mtb6ab1ATsST2mt3uHrFbSV47JQ6ts7huhu0VUXuh9j2P85ciKvkJrAWWyBwuS5'
        b'2dQp8ymQnpljZglpzp+bLSsx4PM5+mXlDscG27IQNLMqvJZsxlvcFJHi5lr8TKBiBB/GF7P9rp0lCF8le+cDndrLrSQ31AvrprCjueRsP3wAH9KTa1pYenIO4aNz8G12'
        b'TDZlWJxT516QzU43ttbPJ81JC5hpvhWfL81Oos3syMkn2zlAT6cMa/C+UeRMKY/IXnxLWxyKm0V1zSZyd05gt+p9Vc4vXpg8xLFAhYo3KvEpspecsKHlabxzBbyluvte'
        b'8o47YZtSI2Z91n+DRujQ8rIfL31icwd/YNP4yhWFT7xy9d9/147znh0ZJ0z93fdf2WvfJpz/u1r9u9nPHPkodMyu7LYV17ZfM/7S9cWZvW/+eu2/FjkH/LYx5d7qH7/7'
        b't1vuTQ3tmZqCtzUDfzz88JljhhAmEg+L2wi9PKbzy8uaOp4cJruWuqjVRakk9zUJpCWeHiagyNCnWxmOr8nJc9iD74lG7ItkZ7pfK3KXbGeuw8/hDuY7DOtzhOzOK18S'
        b'oB7QRsgG4BP4IpO8p0AX9g3TdFPfyNX98XnmhTIRb9UE8AlzJwGfMIPsEo3QV/G+yeQQOdRVqSJfhq8Q0cVlGdkG7APTKjCVwoAEDu/CtxWi9f4CebKUKRWYQiEaH4fa'
        b'8dE4yYevT14qFHF2ognfQcoRnVi+vxqkchHTayV8L+aUXdBvUC2Fvj4wbOrHf70hf1nAY50UoBiSFop5o3wUYBP6MuqhNCCoE321sspNgMt6wfwn/Jh/HJO0OlFdbyLG'
        b't5N75fR8SS99OOXvwyM9YrhZ82d11dP30BvqG1TrsFZ6lU5bVZ1V8IYAbnY7HMDUZ1bIpZ5StbXWh/pmirSpM0gS8mgkbxltpVaiVPJmBVAqBVAqOaNUCkap5BsUnTzg'
        b'+wd7pVRiUCiRf2NIP1BgebhxiI5FRPm+d/0u+g/X87ORi2+xV2DWaJmFimpG/SxLHZWLLNK98uVAvHqkWtQEBYRkXtHkianjmPGJGoYEKnyCyPTQ5v0TPlWfWWOp0q+u'
        b'tkqmLRgwHXPnE75BPaz5Orurh2YcVhhInXOqPqMrY2yWhvMNZK+7XBZa6M5A9LTcE40R5cF0jzRLGHh+NhSVSASMS4vEe/Aeci2PXMtFo8kpHTmkwU+5qf4sdx7KMyaT'
        b'ZtyWkAtYNbAGf83ZufPjpXAHwE6T00O15Bx+wSo6WGbmoF0Ipaa6764xKpYhRk1n11kCmPPBRQE2keTcgnmBvHnrvBByv98wNw1mpkFAM1qTc8nz+Bg8xTTXOZROJlLK'
        b'GWgPyU7KzTfmJCcoEWk1aFeSg5Pc9KwsaZKzPnc+SgdCG44HlA3sd5IhOVdRoEIN5GwIbsOH8F4pPBe5V9+PNo2P4Z0FMiSfzuFn8GHygnsQYw7wC0sSxRoKOHJ/EFKT'
        b'g/y6HJhCpvFtHwsdzS0wJrMp5FD/sfh4rAzG0oFP2b4KHyJ3bqOL+HLF0DfuhPEZWnnxuvu3Mk9uT9w84rXX4hY//l7eLvcAM/8zMqB19Z6Qo+OfvvKK/leOD2WPJGz4'
        b'8SDV4ixHxy8m5P9oQdS63+z5TfvPf3a9fOWHw/7w531nR4+8U73r7PyR3x9eEGK0j3wj1Ci8NuelW/d+m3hNdS9z6YCaj/6x4+PHlv3Pmr9suvkfruafCdn/+BUQbHau'
        b'9N5IfR4jY3y5MYEbt6SA2R7ItVkLgVJLZDo8OphQkz1kD1Pl4834KR2sMIOUmigfvefwGclMIOBjeTkFQPJTeHKabENq3MrjJ/B2vSg+7ZHjK0FkeiO5IVLqWNzGjiWW'
        b'WqhzP95HOnwO/qHimcM0fNtFzRnM/RSI73FlDT9iDtkqVnwFH8S3mJ9qkRhiIwlWIyWkQEb2akeyvsUATb7TqdpfSl6QtPtFZpFIav+PFPIaSgAllMGoeFInFR9PabhO'
        b'ot9a5vYv/mrZyRRe1Lz3DySlUk0SJVeKlGk+TRbQZGEwOQ/5di60crGmhX5iv8BP7RZDcrYLxX97RCDF76mbfXczk17ohda+5qe1cZRIAAplJMNPY4K06nLmEMTDL5dp'
        b'iHbQs3UOembLQdES9fET7BUmE7McOCjGYBYGr6zcVvFQI4ZX5VMBU/UNE4K9YUFiKmOLAvilxewtqX/igvX7PzL4PAzcHFQrEktnahlcqOVyPgoACnHDJvCMYexzyutC'
        b'h2l4ylTyoVxUdOCdSE4/nF4xnLiQ7BvnzC8UeXHOjHeh0AaetKvJ7SDqFSr9df63i0eTML9MLsjLFDZUphQUZSr4VQvKshBhQVmoEFam6VB0qDsiOrhKWUeEoGvjhYXA'
        b'52g8EZUyIVyIYL46WmuY0E+IZJ5IUW18mQ7yA1g+muXDIT+Q5WNYPqJDZ+0nxo0B/om61IR7+lWqhVhhEPU+ghojO3TQboQwuI15QrPn+lUqhCHCUOmJ/lDnMGE483eO'
        b'gmeoZxP1RlKXDYC+ccIIYSRcRwujhNFbUNlAYYwwFv7GMP8iVBYrvZEgJMJTg4QkIRlKBwtGIQX+DhFShXHwd6hHCTWlCenwzDAPguvxwgS4Hi5MFCbBfT0rmyxMgTIQ'
        b'4IRHoGyEVPM04VEoHSlMFx6D0lFS6QwhA0pHS7mZwizIjZFys4U5kBsr5TKFLMjFsxayhRy4NrDrXCEPrhPYdb5QANeJnhC4LhSK4DrJo4brYmEuXCcLiyTNiUyYJ5Ru'
        b'CSkzCgqmH1nsVWbUMheqC0EsD93V4g3Ri0qMGgrcHA0BV+WwUDZO5MEq1vodfLq40QT7ZDmgglqry1ahp85+FlFlWSGyklBAuUOoU1SF1KzV2+tEfq8nfsyrNK2y1Lit'
        b'3hCTrw9e2Zz5JYUPplW7XPVTU1JWr15ttFaUG61uh73eAn9SnC6Ly5lC85VrgAPuvEoWLLaatcY1tTVe2az8Yq8se36mV5Yzu8Qryy1e7JXllSz0yuZnLco08F6F2Kza'
        b'16pfWUX/+n1ZNlCUyjtDKVpdzzdzjXwTJ3ArZE59I7+cawLJwZHk4gW+kY9GNAJsM98IYLyeE2SN3AqlY2kjRx0F4T1uuYzGjRVCYuG5GBSFJqH1XJ0a7qvoVTOi7zUi'
        b'kxzqBYECrpSCmi1r6PumnoSJrj5m0gp3uph1feFhLDqbB1FAsIh1sJJe9E7ihE1lXlzzipLHp42bFAhAAsgVOZWUX9c7660VtkqbVUjqkau3uagMAHTN503GWvYJdiKw'
        b'gpjhsJW7HyIXTKW3p5oFa6UFSIYfhMwgaNgqqmntNnGeAAyldgC4uo/tI7rqDwbY6piFqHM0Y0c7x3o5o5dL/YgyGR9RWvtAZkxNLfzoa/hnUHkjurZNLRyWmvpqizd0'
        b'AR3OHIfD7vAqnPU1NpeDIm+vwl0Pu8RBQx34bBu1NKlDvR7QZlT1t35eIVQOtCJaUlHoecrgNISLUNB3g7yoE2Dd6oVF+IffHO9rwG+NT+4KN2z11tZb9WZYlQog4jXG'
        b'2eJfs9kIbUxHfXAIlwyRQu/d+pefcxnMfAJ6hsWeG4tAPttrE1rOa/yNythSeNUWp4m5W3rV1jX19jqQT3vpyFf+jlQwK727thxkXJgIaQb09TWWCmoKtbj0NVaL06VP'
        b'Mxj1851WBuflbluNK9lWBzPmgHkUzGYKphZhuRsepA8E1/IQIyo73sOxQAf+OM/+4z0cU64/3KBKlet/7gnLzK+nPJaIYaxrKqotdVVWvYMVlVuoFcAu2k3hKYu+3mFf'
        b'ZaM20fK1tLBbZdSqWm8FMjELptMBA5ppqVvB9OFOlx04QIYP6vq096V97+uSiXXJTOfUzfa6iFkoCvLrwWFOqfdpDzY1GnXb6qq2d5KsJL3TBkhUqoa+Rs3agT6sDxuj'
        b'VNFUGrd7qlmipj0Y53rVZJTb7TSmqr4yUGXiZkshdFmGHrHiaqsDNuUqIIaWcmqff4jyxM9J0p3XPbqJrpCFFV6CjzQkJoOkT2XWvIVUuUDas9dg6shZND8+NyknWYlq'
        b'I9Xk/iJ8mkWgJmfX0LNE5DK5MTc+N9nI1PLHkhIL8Q1ysiSZnOHR+CxF1eiFovR/KIfsdhoLcivxNbJ3tTISheP9MuMM3OqmfnaT8LXVgSqH+MLkhLzkEl+9efgYvqJA'
        b'QoQaxM5nyBVWZe5SfNoZj0+Qg1I4cAXeyZHLGfgOC1qdGIoPz8NtpGM+aSN75xfMxXc5pC7iyPVhqZnM7gCDa19C+6RAFrJHhg9weNOGSqaNiCZP9ndmU10EPjKMtOXh'
        b'Z+WoH3QYX8RH1SzMkgvBeOJRJovpo1jPkUuTZpball29Lne+Cbf/7Pzp0LZH62ZmvPVAu+XVr/6nadSp7X837po3I2vvxDkXml8pGTUvo6R4zeED5UV47WSuqmXS3qyj'
        b'B+0N0amx/Rr6fZyx+cnZs2a9uXtyfNLtrA3nM+IOPp1Y8uC3/4kqzLz/86dLR7+RfnvRrq23Zj2XFtvwVspTzy9/ckWeqfrLf58ZFf5iqvd9Z/rkaT+qPk1+4RiWOP/p'
        b'acvH/bSh+Wzic2UlX9t+PePatDBP/c/Dq+v/6U2/deKfnzw57f4/P/hPFfka5yWWjR/+8UfT1Ut2vP6XP7/z9/aP/qq6/eqjP3r/ZUM/pjcw1qxngYpIqwqRtmJ5Mocv'
        b'4RO4g+kzwp1xiclkO2mJw0dSskmbDGkzZUq8hZxl7gWKR2Nwawo8wKGVi+UpHMDBIXyU6SkWD3Ik5hbkcwjfJ8fkcRx+amAIu4G34OPVeTnm9QUJBSqklPNqvZY5JMgM'
        b'+Ewe6wqsaaF8IIdPWupcLETEFrKJbMZPDOzUwHQxlNycwwwdBfjGo4lGQwILq1RAzpE2BQonV2Vr8XVyUbSkHCFb8R3RFENOkSfEEAnnySVRfbMD3yxOlECPtOB2eSGH'
        b'L5MX8A7RAXUvPgo/z6+japKcJCNuSaHbC6rS6+XkppocY1adRbLIPHGvkR2pGXlFuC1F3GsJ5EUF2Uwu4oOiO2wbzM1NccjknIMq9Fo4pBGogegIOSLOFsznBNgu9/KK'
        b'kjnEr+Iy1PGiL+Yd/CK+IR0rzsLPSWciYVMdYZ0gT+PbZFdeQV5egbEmkrQk5fmCFiTgdgV+Lg3fEoNJ3LQrSGshvpSkRMuJRz6bw3fJ+Unfwi3xu5wpHCDiRFMwGWDa'
        b'IMpmSNqgjUgXykKvUhaJemtGMY9MevYwgumEdKxUJ5VGcqINqGGIxOv02IjfNYWdHvwufpic+CpjIpog+bqLFqgp6KBhr52Buijv2LMfC4tvwkJfAVvABcQ34dnnGx7u'
        b'y0KPt/yyJ6ZglkjVpLMtIu9HORYgMpRQ+dkviTegjIJTYuq70yBJ+d+FuejCSvTMOnSnaKXd2RQLJYVBlNtHSO2UwlPLx1rKg3TvmaWiWjSf11pr7Y61zFBT6XaIxNjJ'
        b'PtnxzVS9q8wUzKgGeA+6LI4qEFB8T/Zq6qjz2zpEqPCZOnzcE+V5rM5Aub4X4i9DPdv+mflh31otAvQenzoxSXNp1STx5EOocSiaTAunK8e8nypF5AzPvNV4W/Y5gOCM'
        b'lW/VROWJgQX348PrnWFhPOKK80g7IpfwmenuLEQjQB4Z70dvEh8hGlXIuUHZoqofaGtp8cLkBQsBc1EzSadRH/BPw7CIqRsW2YZ3vIycZ6HCUZt+XdA2TodTI+RfvKGL'
        b'i5ga1e8vFxs34ZlPvhObe/YHE7Je1axRh7/3+FvRinc+Xb7gmU/j1ly+Wlb0xO+Pr5pZuez4K4NfmhnyaN3+3/x69r1+8pen/CzzvQ9fvfR78+8vtr2bu3j12MnzBv/i'
        b'9U9W8wnvbDg//A1lf9PWyJmDj33x2wmjwyLKDCsTjG2TR3619E87He53f/GHx/ZkDbm2/63hP2zaXb8s7g+nP9/y5weKLPvE9utfGnSiJ/9TCnJINMXTYPdiFK9B+A6z'
        b'xJOtGfjFPN8cPIfvUh4jfIGshlxc6KLKU3w1qj5g8nyUgVwiz0nUYRU+wPCyvJRcYEYmFeIN5BiN8UMO4F0uPdyr3xgiIvYAtF61UULsdvwso82V5B4QF3rLic9IoYCe'
        b'GipGMDxErloSyXn8QmfACg2+ypNngOZtZW/b8al+UhygKHJSDAUUYWMkdMlifFuikfhpfASJNHI/bmJ9w5tSUHfy+CjeRSnkIrLNRcWugfhFcl/Alxl3mgMjCJoSOrHb'
        b'OVOKGp/KMPk+l3CObE9khhHF7KlIuZwfhvfgzWzSqx/Dzd1dG0oT1QvILvHgwQW8S5OYVACsKA0rPodsBu4wHO+ROYgnuafD5X2lYipJSmB0Ky2Qbk0UKZaSUSQdCPsi'
        b'baIxMXTMviH6Kei4Bp1EHqSqgh3R6oJJVC/xMXjx2U6HhK2QxEPHnNGdhGkT8gZGNeradpC8TWtl8jb18aXyNvxSxdgggXPxcC1r4qLhAYEPyvnCLz7gR9seyEcb0yph'
        b'KLRnXq2pzm6S5GGnV2YpdzJ5vWfZ3Bth8huqRS1jLu87XM3DtPENA336ki7PBSkD/RZiappoZhH/m3hHZiPHRoNWyBwz6KgcCVBCR4GoArAu2iUTuEaWp09WykQFIVzL'
        b'6VcD2Aj5wgdj/dSy1uaELlRUMzozGtA81T0x6ZhewKqxCehvq62vsVXYXCZxup02ex1bJW9I6dp6UdkkTomoWfIqGFH2qkVNrd3xELdcnaneYQViZTWx5+fyPu9HGjKL'
        b'Qh8vZ9EZGgb4pizo+W6LziaMAo1AdZtsUugkVfLRohsIDD1SrCmeDi9JHCR0rlMTJq5pt28n0KM40LTDZFrKS19OQIGaL/Fez1AYyTrkg8PAzqgolMG099CDrlClMtEz'
        b'8iZ2FMjXvM7fPLvl58T4wNZjfHuAE7gmfj2bkEZuhXgMBfrATYPW6feRxAXkxdbbe+iC0mSqcZlM5bxEshGsUUOYvw/03rfqgh8c+WmPfps+WE2myof1wdpDH/zu/v5t'
        b'NMK3QVbwdr3YG0AQ/Dypl/TKd0Sjc10CevUQcIbOWVeaTMt5Sa8ognFQB+n9oA7yvknSskmijWt9OlKfR3tvs1EHI64PgInOpup6move1kPuA0tu+rdYjipYdudDlqPq'
        b'24KEgo2cgsT0bwMSIJKYVj+sD9Yu+9LvlE5n3Icm/F5igZi9RyxA1WQm07oesYB4zz/iICZ3VI8jHkgNPIhhbL6J9+/JRECk/sH7VPSdM1DbY+cARVgEwWTa4Kc3MBOh'
        b'gWiC3e4N/JYzi1DnZJz4hrmnWJFV2tQzVgxusA/zEdN1Phg0cMnfcT6c7nKTadtD54Pd7nk+dKx7ms4Z2dL3GWHVtvY8I8FNBs0IdU7woyidCzF0BPmornPCFkfm1RXa'
        b'XTlAmK30wJBV6G1uHnIqxmSqdQPAtgciLHnwFLEH+gQy0gSd7cMEsUo7ep6g4AaDJmha4ATpuwPPYP+UDe4yZVJcSgpKKX0ApZ6nS2MyuRxuq2BbZTLt530HiRiOD+Vh'
        b'0iL9g/A/9t3GMcg/jkE9jUOkmSnffSBaIKA1druDdfFYDyPp7x9J53PfbSjR/qFE9zQUEduN/s4jUbHAQCbT2R4GEQDD9kAsJEcBdodi1J0tEPvvoiOghnXoa+f1Un49'
        b'v14mjUPWREckE68qA5fHq4Q5g2ZBgmADey54dPLO0XkVq6vtNVbqJVxrsdUJ1ofxyqEmk1inyfQcL+0+icHg6Wnvhn7+8fqe65k/puyoSPY0bGmaeuR2HkYBWUS1KpPp'
        b'do98KLv1Tc2Gdja75Vs0W293mkx3emyW3eq52SjWrEtskuuCQh0twevSS+sg9JlM93psnd3qE4uxpQ8shoqa0YFveqnHttit/zN2JoRtcAtU+XJAaxGBu5/edLhQFz2v'
        b'f//Q/U93zArkiHCBRM3cUThBJsgp3RpIpVK6U6iMSk8xintH2jFsrygKP6KVPhjBrNC2uip9vX21aMcelyq6c7jr6+00+s8DPtXo5cbB7mnwLZtXvdJtqXPZGqyBG8ur'
        b'gpqqbC6Q1a1r6n2C6UNVITALrHGT6dVONKJmIUN1gbMhPQTwStWYop+A0lFFr6tpYqPJcprQ8zqOGjbldA3o9BlSuvgtOpZKbTtr7C4acGwNzeuCdeyQr6y0Vrhsq8QA'
        b'04C6ayxOl0nUJnvlJrejxtFMa9tBk04PSD9Me9V+xYWGqW9FWzFT/jMR3rGdJgxL7aYJ/YafYx9NDtCExpV2HKLJEZocpckxmlBGyHGSJqdocpomlPY7ztHkAk0u0oRG'
        b'O3VcpQn98o7jOk1u0OQmTW7R5L5vPQyR//94VHZxabFA8jo1fNBIqWqVnJPzci7gB/Bp1IBuTpQyntPHw2+cVqXTaGVqmVquluuU4l+tTKtQs19aolOznxAolX6YhZi0'
        b'k1vkoJPsIG3kwGrmY4nUMbx77CNB7pW+QyLOt7q4V/pCqFbKWTBXNQsDx4K50mBwUhg4FrhVCGF5FQsLp2Bh4VRSGDgty4exfAgLC6dgYeFUUhi4CJbvx/IaFhZOwZwx'
        b'VVIYuCiWH8DyYSwsnIKFhVMxZ02FEMPysSxPQ78NYvnBLB9hpW6XND+U5Wmot2EsP5zlaag3PcvHsXx/FgpOwULB0XwUCwWnYKHgaH4A5Mew/FiWj4Z8PMsbWH4gC/ym'
        b'YIHfaD4G8kksn8zysZA3snwKyw+CfCrLj2P5wZBPY/l0lh8C+fEsP4Hlh0J+IstPYvlhAU6cwyUnTj1z30RlcZL75ghhBsPOGd5weiKntPMc6/uXu9q9fEc/Ax6SYtJ1'
        b'eYz6izDnlQpLHcWZ5VbJJ89lY1Ynn4sJC4Lm89ajXiaieccabIiSzF/BXiVUlAs4dGumGNoiHioS7BVuKoP4aw6qze7wVWhzidpA8VWfNWlWRkHpbKkG80NcCYMyOZWS'
        b'i4xFX850l1CdaAQMPBScJDbpG6vkKOpyWOmEBNVncTK/VNo55riyCmqy1NTo3ZQbq1lLaVLQaeOgl/20mAqYFLtQ67izmqNkUQtcDyWOsaiZXxHiGOQjkC6msgXSKBOA'
        b'GJrEVM5SBUuVLFWxVM3SEJaGAptK/2pYTsvSMJbqKmkazq4jWNqPpZEs7c/SKJYOYGk0SweyNIalsSwdxNLBLB3C0qEsHcbS4YIMUr3AQRrHSkasqW7kl49sQrPR40uB'
        b'OZavVzTKl48S5E3cLs6pAzZAPhCtl9cNYqUKWuqIF5TAAIxulFNV6Hq5awwwBPImHp6f4YJ93CgXldaueFreqGiScWjl5wtRM7S9XNfMsSfLXYbN0AvGU6kLHbcpCzFB'
        b'3ALdNkzvWyLTy5m8vMn0QGEa7RztfDC66/vVFurT1ekWJiqNE7zaEmALbLWSq6VSNIaKAUllJpvgVZjcVpeDBpsRj1J4w8VY5f7jcw7KPDnoYWcHPfrFAuOIoVgKGCsQ'
        b'fNISGEPR6g011rsdwPJaoQnGBqiY/cBl8SpNtc4q1vQKegJRYbKKf9h5xDDfa+wTW/BSRTW12LIAuBaX2wm8iMNKlfuWGhorqa7SDj1mU2qrtFUwf2tgP0SE4b9tqXV1'
        b'DsgbZaqxV1hqgs/707DD1dTO7IT+sQ0L1bC/Yjhi7xBTlykHNhc2o/SsAq5rnd5Q6KTD5aRe5IyR8qpgXeiaeHUZvpURV0LltLqkG06n1UErZDeAV2O+D1TR4VWuWE0/'
        b'KR4QM6EWfXPEBra671ImsYwxiZHMu6NrnC11t5KH/PDi30imlqIWNaospvHmGwZ2mZE+R3qWXGt/hnr1YY2U+VxrY7o25PexnVbKvCjqVnSe90wSYzC47NK5WOryKADW'
        b'tlWuBVwcgCP77HIrCUTTeu/uAF93H4wJDsNFnQ5q7a7O47gs+GgfTgRL0/RY7+3G+NsNjr/VvVka7fSbW5VGm9F7q4ODRxsYfatLs1Lo0f+jwFvD/O0aegi89f/W9Oze'
        b'm47zN/12hl4MOOt0l0vnRphPPW1Pcv2R4jz12i/GOYkVMdMqZXTq4TXKpLCQOD1EjjLq53WWVdqstEGJa4Da4YFOxyA/LXDqE6R5SkiCS5uL/fXF6EpghtQEMVRWQp+h'
        b'sqD3yYr3T9b47kFSHgKfGTMXZqRAMqfPp+UdP++9F4n+XkwLOrBPo5FYy4OP7nftzaySObNTZs+ZWdr3nfqL3ntj9PemhK18APmWXMV8BwS6+DAZ9bNZ0BTRY6tmtWWt'
        b'Uzq9rq+zVlmo4N3nff3L3vuY5u9jgg/IfV5YAd2VaLQ+ft6ChWV9xym/6r3tCf62xzK0brevoGyteP4euN36ejs9lwVckVs8sd9nMHmr94Yn+xsOL/UftelbA9LIft17'
        b'A48EY61a2KeWKmsA8NVXr3VSHzx9cUZOIezrmr437e296enBk9rZZI29KrhFfXxeyZzMvu+9t3tvOMPfsOh7WCcku+zJ8KeTVOvj5/StRWl//ab3Fmf7WxzaYyQIfXxB'
        b'35qTZvad3pvL8jcXJzpXAjtYR8+iSJtDjMdRPL+kuO/xBX/be5O5/iYjGT5jvLF0qKbP6/Z+720UdGKArliK8tPUGYhex88sKsrLKcwqnbOoLxhSmtLf9d52sb/tz7q2'
        b'HczjG/WZgBGyrNCbOsb/Of3Sdk+h4AFRLczJLKUB3ZP0WQtmJemLS3IKMgqLSjOS9HQEeXMWG5KYe1EmBZVqqc6H1Ta7qAB2jVhdZkZBTv5i8Xre/JmB2dKSjMJ5GbNK'
        b'c4rYs9AC0wCstjmpd219jYUGuxKjhPR1C/y+9wlc4J/AEQHoWxSHRIC0sA1occIc9hUo3+29zcX+Nid2XTRRZjPqMzoPwOUUZhbB9M8uzKI4nQJRnwH3vd77sdTfj4Gl'
        b'jJ6LYiIsnkChxt6HHSJB6f/23pCpE5tLkVvYgUqxGWunxidQ1ujr+n7Qe9PlwSiuE7VRJ3M9VVJ1IR7UHuK3gyyQmnMWMq+8GGYvZN5e9UPotXjYlto94FfeBKmJPq9g'
        b'XnwK+qaJpcupakTVxHEBC/TgkRLRCZuqqfz8i8hMdSrMema2jAa146d0iI/TpEtcZ6ZroP6FDvoBUJ/RfjLqyVSkod9akyq1yiQHCQQSbAzz0KO+oQ2DuwqTAe/0vEpU'
        b'aSZwkt9RqWgD6HmJqM3BLus0UnUTXP3eN12NY0H+Rg4dM5AhatOtCjDK8Q5qhvLKqeLhIR54akktYaJTI/mTsCMbPXRFfLDnMUcFdYWG4RU4yRTO9Fi+vijYvD3cHbDG'
        b'Wmcyre7Slx4UB+y5QsPInuxPTKHBLEZeXRfl1GQ/1HQCzDIfrHjDgnVTSkk1pZIoNPuUrlcpqaUUolZKzpRScqqTYqFJvNoghZRS0kfJmW5J10XzpAlUPCkljZW6U2El'
        b'Kot0wQoph4aTQMdBv2jloB+H6nvkNserkPyEanuomUutlfORaX0ItqHoHn7jW4br6J7Kew/voQ1Vy9QK9rn6xAp8SrMqrIHsqtcacsmOxMJ8I3V4p18GSKhW4Mv4abIp'
        b'yNzk8zp2UgNkp7lJ4Lcg9rVAmSD3fy1QIV0r2ZcDxWuVoBLU8Kzaw1dy4lcCy0IEjaCFslAWx5YXwgQdlGrYEzTSh7pMK0b5KAsT+jPgj/L27wK6+TaQon22MHngZqbn'
        b'ACgyNTE3DBNHDcomvorGL5AJfowvZ/y7N8T/dV64rLULlhr6AbcRXXWOtDVToIHD6fPSiOaYFdVXidpXR1cMRY2vm2R+Tyrpi3JDemjn24au/yZBZJtfnddja33+cptE'
        b'KEdwvbbm8bXW196P7L2+5h7rC/Iy87lvdDqq0MicjlEPr5hu9+0B5OJhy9AdT3+DP0VAm92IJMMvbQGtdiWIUqsMI38DQazsC0Hc9c0jlIiib5MHOW8Vok7nJ2ekCxqW'
        b'Dgsw560VMud46XCBjF3TK/kKmWOaSyHasSCvXK6i7n9c54ftHiQHsqm1NJxAeWd8hrFdejk2+HHBbhUP0IuHEljMGN9hPYbhgZ1p821K8Xvto+nVGJowrxC6PkCO6utB'
        b'HPadRtAENMEefYiLlcwiCHv8vI0Uu0vL/nYjrGx64fmeYSdUgp0mTuL1A1eyO9zQTyEeCVjL2J4a685G+b2pxQPgIs5uRLNRk2+vyAqD2FX/C/SMBMWXj2vpsRDKhTzJ'
        b'r2T+3z6fc/rhPp/nHf2CnZdzddtjkBz39VqJGpJ76rXL7rLUAAqidiHndLigWN1eWz+dfivD6a59CH+jYO8d+6Y5YU8VGnRdeZtORxgGKJ0w0skGMK4gkZNm32H0swa9'
        b'xEKJg4fWy6QJB5KrFD8FqJZRdxDq7sEiERSTp6cBCa7X4j0zgkkwuUZakqCl2eSSKr9xSRAZjpb+Otu5IDIMi8p+ZEcUZTLq7UF9Pehn/4RQSmTpB/4EHSWqQr8jujL6'
        b'sV4FENxIoT8QWQU7fqumIbE8kZ7YSpUQJQyAcqVVJUQLA6UP/KqEGHpNQ2YxnxCVMJjlh7B8KOSHsvwwltdAfjjL61leC/k4lh/B8mGQH8nyo1heB/nRLD+G5cPFHlXK'
        b'hLFCPPQlwqqqRNaIJtTOlUXAvUjovUFIgDv9YCSckCgkwXUku04WjHDdX5giBfyiEUc6P5Cog3FGsJH290R5BniiPQM9MZUDWACukLKoDlVHtJDWxglTaSswGzIWgosG'
        b'HRtAPyYoTIR7j7B2JgmTWXm0kM620TSvlkKfz0vByxV7uSKDwstnzfTyOXO8/Jx58LfUy8/K9spmZhV6ZbPz8ryyrJnFXlnOPLjKLoFkVnamV1ZYBFfF+fBISREk8+bQ'
        b'G2V5zIMM3sgpNui8/MwsLz87z5FGcRmfA3Vnl3j5/BwvX1jk5YvzvXwJ/J03xzGRPTCrDB6YD53J8W92X+xz5owgfVNAjN8l90c+lz808rnIC3zjN0rlhe5suCZbLADO'
        b'wynEu0hLkZG0FdCYo52RRlmYT2MOO8KYn5RTMDcbdkEuPQFKv1U6nWwOx9cN5IStMb2Ad9INlLV1+ifmj82v/TE+Mt6SbamprClf1Zxkeb38Y/Ny6QOo1irlrXffNcjY'
        b'KcoyOW7R4PNJ2b5DlP3ICzJ83okv1VjFyAk3o6oJ/YAVtMqhyfhJNT7MryEXhrMzltEr8PbOjyGzLyETzxL6MWSy8zERJ/TFLsz7MLH/JKX4M5m6EjZEBQJQ8OeFFZ12'
        b'acfnNOn5mxMy8YlR/sf8LV+lKIlOBNoU9PPjoED+PfagQi0tL20u+GOVagYxodJXu8UtJob46fxYpbo5BKAoBKBIzaAohEGRekNIT1+6laOeAt8OLnRTAbOQ7MZP5Umx'
        b'B/EpcopGrU1ONtI4tSzWK13f+cWr8ZZsfE6GSHu9huzCR8hO9vb0frjJ93Iiha+i5AXS+e1c0kZ2mAD/7sxbGE9aFqoBTuUIP4+f04RViufNf7tc2ZjGxSCkN2t/OTMV'
        b'iVHgr+CT+Cg9Rj5wEuLYMXJyP0L8wl+oOmKmTI+Q2ZzvzquTPsJ31wDdCQxTG3yeXDUSt6PF81Rrcdsq5g1YFEfu5eUU5CWRtsWkycAhTSFPzuAr+KqbBex4kTyDLyVm'
        b'09PnZE96Ko+vpOIt5jw0At+Q4Xvk9Bo3pXfDaIj2xEJ8+lF6CLmtYH7A2fV4Y3I8aU5JoDF57QY1uYY95Ko4uOtryJ480pqTn6Lk1iLlQF6HX9zAPgszBd/DpxLpbCcr'
        b'ZfgSUuIX+IkxA9zT2Rj7RyeKC+FvZWhdQDtz41mE9eL4QtYbvDVbhobhrWH4FnlWEL86cwQGts+5ilyV48OzEIcPIrJzQiaLrj/BFCJ+slH8XiM+Slrq4cHSeFjC1qSk'
        b'gvlikHwxCrI/TCUip2RashPvGctC5Tw+g5zNo1GRxYDyZHt+shL1z5KRp/rh6yw6Mn6OXF+bWOibr+TOCP4BA6GN8Hg7n0pOI3wD39dMoLGDWaidusdqyJ65cNGAyA3y'
        b'dAG5Rc6542jFT+K7UHKN3B5ArqxeRa7jltXkqkuJwgbz+CBumeGeQOf+wlhy2Qnl0G5SxZQF8bnJAAKAEFmbJfGdHVMivIfcDkVkz0K21smjyxJhKvY0sg8AtqaQnfPi'
        b'4wHlNacUzvd/P2CBCuFN+HwIGkFuMkAiR/BJclRDbpLrTnJrJW5b7dCuJDeRajwamC7DW5LXuvX0sRYnuQgV3yfP0A+aJBthhhUoEu+V4WfJYXKbQX7dFEV+BheB0Axz'
        b'0t6VBUiMt/ACZ5C+JgnX5DzeTjYvso391WCFsw4I0sfGA/NLcgrJjIhPY+0tf9q1tUa37rffO1i0a93k6/yO0ZG/7ve795bGxLlH6fqFv58z7QlV/clPk0qME372zvxf'
        b'vFORV9Cx6xdrq3IuXmxYeHLH1Y6d+w+5B6z78qnZr4wzJgzr/8jwqXGrLi1bVxIfPvDNhH+WjD3WXNWYN84aXvzgd/84X+L5cv+aT89MXbc173sZM1snPXvp3I72RzWv'
        b'X9Gt/vLHF/YmlP437NYLW5bcmhm7n8SuSUy+cn5x2auRA7c/veWn+q+4gVe2pN/9rO7j31xe/t/W6Zb8wT/87/emTFkz4SffNxxp+2Hdzv+PvfeAi+pK+8fvnRnq0EXE'
        b'PnaGjg3FiojSUZpdKQOIIm0YFCwUQbogUkQFGzZEBRFsoMnzbLJ5E7PJpsf0bNb0/m42MYn5n3PuzNAGNNnd9/P7/D8bIgzce889/Tz1+52a+tLxu7lvVVW+NdV+zIUf'
        b'Lr0tT//s1MLcqfsckiIbvzprPaK+4Ppzy/5+ZfFFh6+C3norYdHpqCDH+rgbBUtffq30hVfX2EWOnvePg9O/ijy22Tg58lr0/9p/kfyP66bfRO/d+8IKv90TF6ZMHrXj'
        b'6ciAF57S2/i+w7bMuhembFxQu8Npv+R+3KmPT303/Js4r9Jsvsbt5QWvHnvIT5lX/Pb97fJJAkxC8S5olwZhyYBj8SLcmC0APtyGY3CKLCzG0eSU5UOBFC6L8HQ8HhXK'
        b'KPLFyxp0giXQ2JsQpyKGMTnhZfKG61C63czUOA07lNiZbqrPWcO5EaniUDgD7QyX2swS6ykGUMI0hgKElfMYMoIoiWwFpXB4kpa7gYcja6BYAD44DHVkNVFOzjI5Fi2D'
        b'Lla/SyI85eMqoAgdx2pPKDXPwM4U7FCR90pHiCbv2pyFBQyFAup3QZGAdrFULGBd4DW4w54dhh36akoInuzrPawQvtMF6KJWqLD2dw7Uh/IpnCiTn78E61ih0Zjvh6UL'
        b'M7CEbBmk0pK5PLR5j06nZ1qwh4KRUs3KorRULqRxZek07RiryNnWoswwSVXhNXMia5SZG5oaY6t5BlmL2Lk9lVQ9UKKfhAfhhtKWCSy7yHZx0cEJywPceOwK4PTX8NgC'
        b'V7CWvQguzpyJpT5kcxZv40S7+WUSJzYacNF8DyWyKIUWn0AgJ56zX6CYG7U5HjokFM6slY27B3YlMboLylxU6oGdAUTgWSzCWj3sEmAwrkMRHNeQejqRHjrJ9gKbAIkp'
        b'tMMNBrIhhRZyPpa60PmlNy2V048UTTQWJpaYnGLHyCVhIyObSkOgHicNFmHNBheG7+SfRYk2GTtYMD2YyTvIganvuJwbj6cl2O4KVcIcOGUGNwfQiGXA7aVwY6Ug2B2B'
        b'Aj8G41UewMPlFE7fVzQC8+CQ0JCro1cwVHAn56CAYErVFMBzo4igV4lHJanrQ9hLIIdskIco76f2QDELFUP5tEBvKGKTJXM5NFAKECciVkRhs7+YNL5EhGcxZyerhAse'
        b'h0pyg5+jLxETRC6c4RxRNJwjHUUzOr3hHB7RXIUigQd1CdY7+DqJOHs7PcyF83iOYXRNh/Zp5M4gRyh2Ue/retiMhaRbrunpwTE8wZqF1WRG3YHSdNwbrJUxJGSrviTG'
        b'Un04nu7O+s4ukC6OPkI5FEOFS1+V1EEf8r05KJ9kTMYsd1g6A9/jsUP3s6SqRQFQ4ynX5wI4AzIhDy1iU3w9lLr3ZqV1wGqdxLQGpAzMFQanLHOdMEkoM+1+TzxNn9An'
        b'erAY7xhgg26Z+99PsspsBUx2Txoouy8w5g0pr6pIwttS2FPy04a3FZnwEkHxp/GaImsGqz2KoniRzzQbz0RkLCayt0i/V3Qo9ZDp9/qNWYeH95PJBbOwoBYYq3OZNOHD'
        b'EmpAS6MaXRrlR70njYlK10YC6ytjNsdui+2PumLweCBowby60LSV9BsrhL0ohP7K7DMr+N79dW0QjeO5PlStulv3uOyoBpuENg2Fxao1fPd91WNbvNVu+NChLdQPtK5h'
        b'O8Zookl3EOonUwOi9GOC/T2Ys/ekm9SBS5uGZMn5VVsRR13BTgnKnrr9LgpOteGfOoqHeDtV4IS3jwtjUU40xukPEdFqRzhGlZ4cFzfEO8XadzL2U3K/E3lARuPue6Kt'
        b'aD1YpPIfqMSjIhL0tRWwZxEJCXHqEIRtNOSD9HhsEs0aUfyRDr9nsqnXGh6iEkbaSrB4KBoLEU/B4bTBgn9gsBVDt9tE+8ppg8Mc932x+r1sM9UCAVLDrBY6XjAacDSL'
        b'ZTefpb+LOeIpOjDP7eH28Kt7QJj6FKZ1WGiNBoY9dm1x77c5srfF8Y9J6UpJk1S8DrBB+l8f6qC+URVKmXJzsipRwdhdY9MY2LgsKj6KxmLoLEvLv+SVGBtFo5JkS1n6'
        b'CR1ENVAuC+VT44arY3oSdAPtqiHFIyPD0lSxkZEC92yszH5rclJ6cgzlo7WXJSZEp0WRwmnclgaSd1BiwPQBq5ni5qsd/AIaoRAPltkrzOrR2OqRkcuiEpWkhgNxAFnm'
        b'FNfrP37AEIuDEvZm+4iVVMO8+uFzn0c+E20Y936AgcsHnGEx3/nnE3KeaSl68alUjIgZoxYkekkRWLFb43fp5+mRxMXHCtBnjPUyu9/XuKzJfc4TZUziJtaxPY4MWsBg'
        b'TLG8BmuzB9KMoulbSNS+636HZg73nUmvY1NFw3KwdumkfhZVPEBtFjs2aFuJtdBOhLjiYKoiQSce9GdAq9iK10xdpZj/b2KY5TSepN7jpdMaTNHA7cZG9RYEaT2pfaU4'
        b'wN5kh58jNIcJpin6p+AARhZ1AYqlc6HRK+Hj5FEiJbVzjA23+3ypPNLZ6tPIu9HvR9lZyaMCmBX4i8hPIpPivogsifeLMmR24CNvGC7cdlIuZnIrHhPDid5vj1w2mBRq'
        b'rhRQcVsnwaEByLzzl2q4kc7HC4C0d2A/5QjUSqt4Gst6T7SGx7MTk3mnVM87G13zbgKjen303COFaN7XA+Q/JOlrz21sOkaS6Thq0On4idWA6ViXtVbndMTuzCHmo0MQ'
        b'nY9to03nr4EauYiRckE1nIG9dKpCPpzkOYk5D2fxuESwDubjvo30sWFwiVyawRN98wBUJ2Q1fiJiHK6d43ZsjfeJ6f4xgEyJLR+ci90cvzk+Md4vJigqKIr/buRW2y22'
        b'oas/dtWbkXJGzD3lYBRZvE/j0uxtSh90hIy0/T34MNmYGFtIsmx0D5PmbYMPR+9MdDIO5oOOw/cWvaXpQd73b2A3f8wVTnbk4znlYiXVeYPCsz8ni/FutPf3m6lLJsCA'
        b'G/atCFunkl2ZGuSxwB/LH6V/wk2xoIJq9M9iODtgsPqFVwy+adsN8HCwOItB9ujB2LzpOyYMOiIfmA3lUekb1/FHBROd3reB56MkKCxh+J9HiJX0z6+NM/OPEjxjksK9'
        b'3vyypu96hLqB8QbHuKE60mGA4iYEkTz+aUfLnzxoJ75rMpSS2C+K81/pxfzHmtO3bxhIlNQS9OG42Q5RlOf+bvSWODqrD0yhHTrBWHxr1bvkiKEb1ByohDYsdaTGG7gk'
        b'kyzmoWMKnkuneNfkTNvroWPOb83WYXVRT/lNI5gJyThpjoM/Ns+ntlYnfc4Qb4ngABbB1UEG0HTIleA8UPMWAlcfewBp+dMGHcC3hhxA9bto9fp4F8doOj+aY95F6rg3'
        b'YaqBxnUvKrRkkkkfB36hXuFI5nUcVTi6cEzcGK3nUTqk57HPfkZDuawHjP30IIEl8hwem6f2heFhqGbeMH0oVVELiNwpQpqGHdhhTh0n1JkDV8I4C2gS4U1s9WYMl5i7'
        b'EwqZQ8eHjF8wtDgO7tOBa9ZkfHHfDil0wEXMZw4lvLlrohI7OTixlfxSyUHZrqlC1Y7ARUrxqdKHcuikAg4HBzyxiPnwPEllb0ixUw9K8CC51kGeV6xiBUIznp+rTOdX'
        b'jqazkoN9cMpWQzFxFHKlSglcZuVd5uCQ8W6VFXtXQopyu2ieJTVYc1AycyLz+KybqJ/1vJj5RgN+iZ0p+EaT4DQcwXZskxjhPmpr5KDWQqWiIcMLoAkvss6w88NavN2n'
        b'H7A1PQ2vhvo4UPO54OCqhENGu7E2Xjj+70hGzoBSEVbOcJVwPGku5uCt3cz5BSeh2qaPf5XiqDB/74pVWDPDL9SAg8s+4XhIn4zXTSxW0dHG+rHQTAOB3LgEPOYG5+Go'
        b'0OWNeAauII32cuGg0NYlAytZe+2T9PwCOObhSvwkOoZTeZE/jliPdf7a12GRj+NMaKNibbmLX7gdFpOqhNrJsWKVjy+Vg8oCmQAUQhuon2S6Ac9BuYqy/MK5RLp7YGnv'
        b'G+msoWKTS7C6l3o7jmkXNWXgBbhlglecsEFFFw90wVU8bkoeOmAKOa6GepgTjo36uD/MdJnVKMP5IXALukkLL3vH7zCKG5FqjF362w2hxCjYxBgOQSvuxSZX7N4pH49F'
        b'85zxsD7UecmhfeFMrLeFQ0jOYRU1GmAL7tuih7mYa8q5GYqhNRyurMUafSjGQqixJ7JaN1a4+cL+sNEJe+Ac5oyG7i0TR8M1KIMC6IzbifliNztSj/Lx2LZ0WKAZtLBd'
        b'gfVzMD96Qia3WcJZRG6otlnLqajR2i15TC+KWS3BbI+TE6pgfy+e2Ut4TRqz1oEV+Pwun+mvimQ8Fxnp12Y3j1PR6EY8HG9CW1BvxMnoh4iNW0kRLWR6nODdIA9Pz5tB'
        b'huNgJHSQxh4On4an1pL65gwPg7xYKIrH43jdYDN0WQQGZmJHsuC+bZwMjUItd+3pW08fJz89q+E0rAXOy8n/ZBXhBSO8lrE8TM4zD7EP7MODdAJQO/h+X0eyLTjpQ60j'
        b'N8JQ4oqnoYRFM/jKbf3xeipj1X08vtwSuUnCOjjI+HJJW9qggzqKiSZkk/xIP/FyvEhqR5f1no1wmQr1RGbPgTYR7Oe9yBiyIJ+xHlji4EN6rixQWAIufr5OIUJQBtXo'
        b'KOtK74CDlT5E1Uuh28CKEKcIEZcZZp6JJdCsCiOFUS9/o+Cg912pDtNQq4o+AcGsrc4rDTOwE1v3rPTxCwxydAoKF5iGe6IDUphnHctCLOG0GZxhcyDaSxTmw4iFIgMm'
        b'j5CSM03FvEQdsN/an/lv/MXkcG0VTYdcKFo7SRVMrm4NNAoNlgcKWPThq7RRJ6thb0/gCUcmfTPkkLGtwrL1MqK0Xocmnwlwx2fCDLgs4fAK5lpRp50jC0JYA1cCyf7Y'
        b'nm5ibmSIV8zJp1QVz1krxcF+29hWZw/nw0PXK+nGJSY7XQtZbVCE3SqWie+IOf5yJ6Y2B5E62fUP5MdbWzbIDCEvbAqLJInBspGhUB6G5eFkVejZ80TDOguHodKH+ee3'
        b'GGKjNMOMjOpNfx5rObwwBU6wjiEnyJXZ2C6yoqEB7QacCC/yTmSFXZNbst1zKeSSLTeAN7Pk+Dkc7p8HNSrqEUuEaqzUButcWu7Ac9K1IrxkgGWM64icbMegjoxyBd7u'
        b'7dwlbbwpbL/N6QHMV8pN8WC+0kK4xKZgJF5WkdnU7OfPeGwk43g4GTONHYYBcHKmJqojfTg0SzgTC/HwmDAVjYhamI1nHFKJ0lkuZ5o8ReYX/Jd63FTI0YvDdmNWdbL8'
        b'D6/W7uU8mQ2HRNC2GmpMx7BxiVotdhDWCjZtDNLjTOLF5rtIs1nUzHlLLPRfDHWMGIDREsA1J1a57dhKtplSpyDqY8QqX05/g2g4Ns8TVN42aHUirTqJZcwjK5nNw3ms'
        b'MWMvXAJXoMgfDi52YpdIg0/hFTjGrllhPlaTbiyxEC5SAutAqGbxGuOhbo9QU6id4BJEpi9d2XrcBDioZyTDKsZj5QV7gVRL0Mmh2EVX98CtkCDINcDKbKkgdJzHchPq'
        b'HJeTw8dorgi74RScnjRZrs+GLircksoqcdPUogrcxFo2zWw8yclCRJVtMWpBBSvhJLuClY7LmaDSGaKWU7B8mBA6ciMNC4mgYmqhEVQqsY1diSLVOE0EFTsoU8speNGJ'
        b'XQmz3ErkFLIVHVFLKlgH+Yk//vbbb8PGSFxXi4TolFmy2Rz7Y1KWnt3zQshK4qdpHlyC/y6RnjKLHETm7x/2Dr2RNNrNYsqNwogLG9bVTrn40aSFyrmr6uwLLvyyOESS'
        b'+8GW43lSu6f9prh7n+NOLckpkYV/Jnuvcvp7HwQ/Y9B0d1JHkLFz/LtdmTgyLbOpoHbyNGhem3Lu1UTPZ4umX3K+z+vNf+mDFat/8n2pfS2UpgfkvfTCFscteg+zXVyf'
        b'lcSucMrpbHnmT4nRokknrrqWeJx+4OrOF5x+dmlHTkZcXvn05Y52165Yv+r+/roxs348NKlh9fm3rm6LHRvyen5sV2345iUNIa/7Ze2/afnPAMk8J/zM5qcFw9799DOz'
        b'iNc+Wuqx3eMv+ltf9x79rtmIrj/fGhY7/OTlG38ueF36/g35/y64cL30uRBVl+P12Oiz028tU7w/8WXLPzuLv/jn+lfcTOuemtkUNfbI6o8jPnFy2OJ6tPyX/X+Lfi9M'
        b'/qxF5tbN5btqGkPPti2/I37n+836X9uMfPPOGy5/+sHdzS4ufXGhw9+Dv4hLeWF52o7sOceS65zi+UUfdn2a2XRra/iGpK+a26x/qOu6uP2o6bKK/aueiKt7Zn7qG1O3'
        b'H07b9PVL52tCUg5P2PmDzYyAG1sb8u47Bb3+2f3Dfzn+17Pf16w98/Lt+LIFf5tkPvcpk5CKjgU/FIQueGLXV4eKveIX3fe6+fULt8wvQrf73SXv/NJk8L8vdg9zdr18'
        b'Pane5sNJb1/97tdFW7LG4G9f/uBRP27mqJhdbuHjjn+4cEHnS/tUH97qtnvV41yQ7yvb9n/ivcnxVELeYYMHFkUfceFLsvXdj614Dz3A4/4zf3pmV3zKc8M2v70+qu6T'
        b'6KbgAKhPUH71W0NM1pLgVd33vIM6Zu54R/Xn9Nee/MLBwTV03BtPTHhwd8463yiP/VurVoHq3AuBzz3/TlPy0p3fjVg2RjSjbId8ihB6UIrNO3pCMbAzQhOKYYlHWOTM'
        b'/IkSZtP1wks0cmYutLAAEDxnv0HYPqWj6PYZQG6nmtryEVDSh04EK7FaHbFzeQ6jCVsMJ4drYt/0OEPoEJEFfCID6hezy7EucFuzsWNRqmZjx+IsFrIT5qUk9Tw6uc+m'
        b'3ornBQayKxNnacKJ4ISXNp5oeyyLqZm6y1LNghIAjYwGZbMN06nt3LDKwd5ZjiVEvzdaI3IiSs9px7lMMcbWhXjOgZLuFTvyZIdt4/Rhv8hpriV7o51nmn+vCAjzCDGc'
        b'xZOJlniCca/NwZwsGv9Bxa1gPDe2R+bW58b7S7AR8iJYMIs5NkCbg1CD9G3kFS2iGTvcWIsTyc6jpsy5AKVCGBE5Zk6ysAe4vpBXQrlhqileUdJwPx2BPdihvxMOwm2L'
        b'yWzM3YlMWeUQ1MdZId9s5SuG48NlbBDlxu7+whUaHkMHOQzowSOGMmw3YxEpznic7CcuZISdGD+iAWceLJ48a/NovCxEblUYjXcIdiRaFtGXiH7b6E9jmm+L8BqRbq+w'
        b'di23ntVHIsL944n8UbeIDZUIirL9sWBOzzk3YSoL7VkId8b2ibRevFodVHZ0DhtLJ6wy08bjVKWzeBxo8WHm+U14fcQQYSVEqejUxJUkJAjm+RxSp2Nkhawh4le/qCYa'
        b'0zQnkI3zbGiY1z/CBjrDeyJsHPG4EPJ2YAPuJePsp+HJM8ccMVasTYbaeDbdUueuIaI96VFfR8hbQRovTaKMdvvGsT7bAPs2kR49gZd6jmO4CnuFmXocSuAOPazNe8ku'
        b'2GXBZmoov1Qju6RivkZ4gSNwlAUJYRWUGzsQrenAoAKMF95mzHtwHVvGk0r2immaBR2cDe6TWMGlyHSqhMM13/hBjK9EAbmt2xQFVW4ClyEROar9A3x5bhQWi0J4e6qX'
        b'CBF1bZbYqabtEzj7MoZlbhonN/lXInHkY/6DmK//QlzQPfN+iJfM3vYi+TbA3jadWoUNGVuNBWNIsqKYbiIBzc1Yjes2ilynV6ndjKLGUYxyCfksUZMpmwn/RPrqEgxZ'
        b'HJEVYw60EBmLrdW0ywJWnCG5YsZ+0ugkM1I2jUkyFtFcY+GrB89WREoQsZ/CF80npuw6JuqyhNRBrQWvX7N7ByMJgUIsNWwY/TaCxSHF7tDGMPTKtOqxLw7/Pxs9TSiT'
        b'lTbpi9aQ8QQJlRqmjWdiZs5o8qv9oGbON5b04UIcqpPkPEs0CxrC5UqdrjzD7n20y1XMoiAkH7wp0hGb4BmXTvkOoxITGTJpLyJhUqkEWpuoxD6ApQK2lUIhQPdFyZJi'
        b'tw8oVIhpsYuMXLEt3TcpLjJSFp2YHLNV7qwGl9VEO6iUsXGqRBpykJmskm2PEkgYFQmUN3EgyXHvSiQksRvjWGq+OpszVimkeApwgjIKkiRLUCgfn+KQIgp4yHxZ1AGZ'
        b'f8oECuBK3kMjEKJkMSplevI2oVht03wVkZFyijczaKAG6R9Nf9CPCUmyDHdnyp29hHTjdtqZ6Zuj0rW17YkF0Vmium0MVZaFLQkRF6QAijHbp4s0ybLxacmqFIY2p7NE'
        b'0vT0hBhVYlSaEFOi5rsXgBKUMjuapu5IuoC8luGXZKaQX2PTY5zlbBAGiSmhHZoeqxkX9biziLKk/lyW6tFXJLNU3RSKR6yrzD4DMAQXpCaVta913ihIMAk3wDm8xczz'
        b'a2Jc9JlxPgyaWGZDBLbNkLpA3oDUBiGxIRGKVP70cC2dOF1txpQZiqmt9GaqK1aPGuczbErqbrwcQs7di15QvW6JbzpcwBPQarggyHEsHiUn/dGlXADcGp8FzRau0XCA'
        b'WZleWuzDVXKc6zfLdtmvNIjiVDREwHLjWCx1xxtEOAmlFL4VNDuGJh0ZcBO3SIjs2DGDPbx8koQaqGSyOXtMcizSuIRbbbslShppdfVsyJRn3cz2upos++C9IJ8JBp9M'
        b'uL54RBI/TFr66pNrmp8w9H/+/Xdv+iQGH2tsX+L7ienfxDDPr3lve9qX0p3XZB80/5j/17oxn7/vOXrv1N22e1Je+R8X96rV0Q2dEYd//uWu6OPTyv0vOn6q93SV3qSb'
        b'35vPNRh1071SLmUy6XZDcyImX8QrGk1Eo4ZAB5YICkcr1MNhf26thsk3bTSLMo5OhDYmaIyEpkcGGqvlDGxZwAKA9eEQVCqpNdfJTmPYssRK6EoTQ6sIzjKRaxOeWaBV'
        b'V6QSprBkOEK1wP/bYoq5LEp+CTa68UKU/NilTKSHks1UVTnlSsPkWZA83sAaJuD4J0IeFelnuxL5UBDozxgLClm3Y0Yf/WmTJt+hGPYLUcuX9VP8DXUE2bMQ+0ITJo8a'
        b'ZcRQcRRK4XpvkbRHHh2BBzVet0dFjBjRND22KJn8YadL/sjm5lCZgcoSRKYQUzmDShj9Iga0BfXlabTpe1jriB2x6XtoxpJfT9FDU6br0Mzh3rMaPGpBWwca/UnOkk3k'
        b'MNFiE2iSVgeLGxQXiQdNWdWcmD9KdJyYobFJavDQvnDlKqVwgsayPYxsuN5LfL1Ce0GQD3bsxEYnxCg3xSQmkFIEdl0NLFMchVGM2ezM7nD2pt+92G2DIZv3KlXdHx4s'
        b'8tBRG3pI4XaVsayayWkK+geyoevccNVI7YPWwXlZeEAkg2JTpSQmRyk0rdd0iM5CKaanFlqNngXqsFulKiFdwEvXVkr3MfDIWnl5hUU6/tFHw//wo74r/uijnqvX/uG3'
        b'Ll36xx9d8kcfXe09/Y8/OiNSNoiw9BgPzxwk+NM3TuB2EUSXWIWjzF49/e37RJD2DXFlAXC6ZY3BAleXpUUx5OqeOfx7YlRXUelU2BUyZji79lktLLZWQIwVlhN5YUZC'
        b'1B/rqSVh4Tqq0MO+TfcYoR7CcktQDCFQSThdidY2QrLzqbH6NB7C4kVVVkCbfSonBAw0QMsSpVREzRjcqEyox6olTPwa6UPEr3ZXV1e9ybCXE/ly2Ai52Co4cW4Pw0qH'
        b'IGciEUAtD9Wb/e22sgvzyJnX4hDkJyIX8njLeXP2QBu7sHhkmkOQL72/iA+Ba/OxE07KJYLXoRg6PKnLzByv6GET1nLiUfwCh+WCENgc7E6utabjNW4OdnAirOEnJI1l'
        b'Zc6gYRDK6Wkijk/mnGfDNQM8KMQ6tIRAnRI7zdP0oMGYPHOGt/ecqLIkl7Y4z8SDWLOcef9djKCElbRmtzX1bDC/RjiRCcss8Rx7PZZMwGZN3aBkOqtaajar9yiozNJU'
        b'bbxYqBkRbI4Kjp8WFexTV6HdVqgC5MAJ5lwbBTfxiqbi65fDtZglgk/k5BRjaYaRUgIl6zmxEe+CRPRiFVwbjjVS0zRzbjc2cmJHftEmuMweEZGOPEVqcVVqxo+M5cQm'
        b'/CKDxarVVBSBRqj3p4JoKAu6pWnDRDLl8CRU7aJtxHzogmo4GkZ+qcYu0vNVRPCthi4rPayJVmGbnin5GQgFWDZfNoyIcFbmcG52klwkOBAv4vVsbc/UZ7GegWYoZX5J'
        b'd6zBWk3nkPLr1d1z0E8uFga9AW+t0TyegG3s8c3QwXp9z2Zf7bN50Co8G+TFGhxshyeFPrqQwfoIbuC+hML3r4uU35LLrvGB4S8uCEJXa4Nv/tn48szc2jMX8//09J/k'
        b'171tzL4Jm3Dru0g31zljt0yoL889IE4x/NOf7t7l5+gNS1vz2+SxazMzH3a7vFnvtCYiZE+Vw2d2pVUXQDV5+LQXqqb8GBDxypxhXTZzhjmpHkSsPvimTfG8/WM6175p'
        b'9FXsR+VPSL6duTL+xXXexVN9/R/uPDpq3K8jTo76a/wir1WXTC6fa5kxLSmhdeSVr1vbJx3BhZEfn/rpneNb03+beLhg/Ef3C7OujChsvnViywcfFcD4Xakz23LTNh9/'
        b'/tOkT0zTM2+OzZJuKH/Q+lrsb/cXjk4gqty347LfDNn9m/m9YWsqv2iUWzO78IiQXf5kYl/qSWVk1nuohL2Chb52RBaR7qnxHm5hhcaAfxOPssfxrBnedMBTWNgrXtrE'
        b'UWwwZQozC9tg8Uh/tQYwA4o84SrkM0FcSmbRPgYMoDcWmjkJ5PO410ImpOle2mlMraIsXxZysFnImYVC7GDXV0ERFvX1SOD1kRmkUnns+na4jQccqImfis+GWEouYy7Z'
        b'hE74MUF/BN6Co0opdvAcj6WcF97Bc3oTBR3gSgapYmnKLLLEsJCLNcFKHvaxGnuS8pvoJX1yqYhLXI4HoBuKhaTSajgGR+hFWmQxh6ehlayKVhdmW4fr2GgLpdvxUL+8'
        b'1KVwEGqZgoHXoYhTUo87D2eIllqFRwymsAHANjIWd5RQBkW0TpU0vuk2Xg2Go6zCokmwlzynR547y+FhK7ISm+E2U4R8yFoqJFsJ2bp5uET9rk3YYIjdgmG2dgrWKzNS'
        b'6QsP0SCvSiyDwpVCJ9Q4whFyjbwPajmyl5wgOt0U1hTr0ZsF/SsCunurYET/grzFgyRgDhE7LVESQZupKRG61ZRIqphQcyWl9abGUsHsKWLqiubLhCVHGos05kntP6Le'
        b'GPJZln3DoMkbgzQwKixf0qS3cJ4W11e74TVtSNDqNHHaxEZK2vPkEIrNk33CsQfWg5Qu4tScb0HyEf0wqe5JNgX7Bt2TbvIKDwnxDvLy9Q4V0De1WFX3pClRCUnqrEeW'
        b'ennPuCctUJ2kSW/ul6kZ1RfTikFcUcsm09RYq4QOGvX/knk9zYWqkWI1Cp2hgYWYjr2Z2EzPdrGIfHpsaEyRhYWJyIySrElm7zDkrccaCqFWcBoO4Il+SQs8N4pzXy5J'
        b'wCpo7xMZbKL+qbTn+3KuKUQKZ4WLwlVheFSiMFK4xXGK6eyzVDEjjiO/0c+mFElKMVv9d3fKAMY+W1IOMMV89tlasYAygLHPwxWLFZ6KJeyzjWKEwlYx8qiUsrkV6sfx'
        b'ilGK0fmGFGSz2qCaV3hVm1QbVlvRL8WYcgPF0kKK6qVPtGKZYgJDqTJgLGmTGOLWFMryRp+rllaL4kTkqWHkn0W1VYLwmxUpzaraqNo4TqLwVshJecsoYhgtsdCo0LTQ'
        b'qtA6zlBhr3BgJRuxcFx9Fp5rGaevcFQ45RtSUE8Jt1bKgmyX37Oi68CL0T8wdLa42LQH0/vIpgNvUJOY9b7pgTMRdD0SlMkeynQF+znd1XX6dA8qL3vsUCo86NpwdnV1'
        b'I/+IJD7jniQoOCTwnsTHd7nPPUl4yPIV90RLve8Z0ZdtCg4KWEO2LwOOIclRzfSekcDTkUA+6sUR/Vr5e17oxl7oGxQa9jufmntPEro0wvPBks3p6SkeLi7bt293Vibs'
        b'cKJ6QBpNWXWKUScEOsckb3NRxLr0e6sz0RZcpzuTkhnYV9pyuisYBQR7eQZsIurAg6m0Ol5LfNm7yc8VUZl0Pwqhxl9lOinE2XUm+Z42iz5nEuobtDzAe9MSzzAvn8d8'
        b'1O2Be7/7vNKSlcolTA3p+0hAcnygMp496EYfNO/XlgejBq/gg+E6Gy6X9imFDvzAYvv9Ye4gZfX/81z256FrNfg1twcOv6Mv7hkoYuOiVInpbCDYUP7f5YkwbWOW5TYW'
        b'A8hj7RYfDi9A9daEo67viFj6yK11W2j6yKvfsAQSb37Z3U+HSB+5Z0ipUNPJpB08RYp+LRfwT/sufWfNs4+fjFBBGrWAfFJO1H0u53BP9UlIGOqtcgPhHF2h4zAN0Zyo'
        b'n1IgtLCgPtkL2hGiaf0se4HT0HEKqGhxxtrMBONBMxM0Scd5BjrMlL5C8m9CVmwvY6VArCP4iejOOYRxMlRDlCtLYfQHTI5Qegy80UnWb03J7JZ6y4e+ja6jR94xV2Zn'
        b'r0ygTqcMd+fZ9o9RpLA0ZXZePo++Wb1g6c2Oske9Z/BFLbPzDftdT7gN8cTjbgC0iP6VHswOrLZlCUYfIS9bTamkAfUf7El61AmP9Z82KWkJyWkJ6ZkCCq+dPT08KVUV'
        b'PT7tdZsG7emhSu+h5549tQPb07PMXu7c4xed7Tzd2dVDfYvuYnpcqK7sVnWpPX+ezf4sFD1YwwScCHXTdGBACP0zTclgIAbtHuZ58Oib2M8WmW5EB3Vi/qB16oFu8NAy'
        b'tQ7EZqA4CVovug4nOf2PXGPMetQ0z0yizIMfG5VOJ5RSwzrWC+iC+pAHQQegZlVSzvaoNLXDvxcpBOsdWWhsLG2rKrEXkZnOorw8w7yXB4es2USZdoJDvTdRqpVQVkut'
        b's12gVxu0k4RNSOgfRoekxkzRjJtGf1IbhHX7pnuMxMzxIJTQY8O177en2A/q3WcjlCKsU6VAztZvi7EXWqe5JSFJN3SBAIJBhEkN8ezmqCSZd3jIIMbuJFno9oT0rNi0'
        b'RDZw6UNUXtgQB1lLZMH4pkclZrIHB9/h7Aefs2r0DmFAekA96MxXD4kW4EPwOw3SonQhWKEXTHefZ/tAswy6a7GSBjgCSPeohSWlZvr2K1f3mKj5Cnvey3gio2MTk5Pi'
        b'aUlDGMypHGM4QHKyCGJWTCs4L6ZgmfvxJLRiJbXxnuLtoAQa1TlrmXBHSB/Eak4IUMjGbsG+2cjjRQohii3YpQYRhW48y1ILMXe2CVVPoQyvka92KJZwppgfbSLCUsxb'
        b'zRLP8Ig00r93OhhLOrPuC+7ZD3QzUM9PxM2CvWaYj2VYJNhpT0MBnmAWYmjgiRhITcRwFWpYE+LwDpZLTdPgMF4x55hlmQiIBaoVVO7B2vW9kVXbMnuqo02VSTE1DaHY'
        b'qnZOQeF2dliCZS5Y4kgBNQWwUCdqZasbxuOx9csEG/cBlzUMA3T3BDUEKFRmM/dEwiIDooxfT9KXRSbOVyzihAzLzknYyKBBV0ClOv/Hx9kvEItJu11CsChgpY84BIpp'
        b'Gh3egNOZU2gqoRQPQaVELmLeAD9oghusA+wU6vb7Y5fglbCUsMZv1bS9FFoSpIfzeSVlu39JfG9KebcxLLbI3/511c++0Q5v/LysM+/5qg9FE+OfNXzSy3be+KnmnzTO'
        b'lr7nfveLAFlSeX60FcrgyZO5y9fNvxB8/8uCD6b985widFJcU/S4lldKGhI3nl6zI+2n+fMSLhSMf77ReNHIlRmH355pVJR97cXdNUUp394ZXe3+o/Vph6OLXp8U8Fl+'
        b'U3a9169vbM0OdTepdn9n5Gf7Xiz+8Ec9k0oXk9oSuSkz8lntggsOzk4+TvZ4ncY0NIlc52E7ixedBF0UzY3CG+tFUUhmRxqcYcCZhYjdfLCZGRenuWzXWmANyCxlURZ4'
        b'eoQQFFG7AfLJmDb3RKpr4kOWilh0yDhsxmvUMJycxoJDpmEnM6SuhNphZPbGQHvvEO3EVcGsYsOwO6VPsAV0w2V1uMVB2C8YW8uxAfMYBCAeDuxjbZ2ILQybY14IlOsA'
        b'ExzmoAYTnApHhdjftkCsVGM+CoCPG70Z5ONqaGF9ONd2IbWNz47vCW2H2qmsfwzx/EryDrpMu9fiVXI5kF9mha3M2msFuVBMtocAHi5hGyeK5t2iRX3wBYz/JUOZFp/O'
        b'YzBFa5cVb6yOQKVcBRJmVJWwf5Rl2Ewk4scMohapMdmCBkZ5DqkhDRUw8gfg5AKH1O46xj1Su3tcaDmBxOOe3iYqBg+BflWupwGW0/U6LUey82OI2gNB4e5JQn08Q+5J'
        b'KAPqPQklQ9VopX0ja4W4VRrGes9AzaDdRyU115xYPpw2oV5QSk3UaqmpANddaB5n/hhp8xrl9Jwu5dRToWCkfb3IOtSHsw7znlasG6jjxsk8qNDpEakFMInU4fB3VAtJ'
        b'WnAtGjA5ML60P5GhwNZLVf0e0Teddly6WjF4LJVLLSxrKW0fpXUJ3FfCszqYZ6OUsrjE5ChqfZAxmlU1q+Rg0TZRSX043foT1g5Wiz6qiC5G2fTYHYKcna4lYt0mBHsO'
        b'Er1J7klQUCGxpyt6WPGENsjsGC07bRoTAieGLHN2dp4oH0R8FWImWCRyFJ1NvUiYtSUL/JOCWN1zXWd52md66CTVU0Adz9WXXFJnGXYh3su8qT/Ge1NQeOAS7xBHmUbb'
        b'Efg3B40BY6HHg/OvJqcIodhDlLBDlwI5CNnpEMXR/7T6Je3hodQ/LeCbelbrLE3Doq1LU5SRXvEOCfIMGKgV6o5WfkxNUUOwJXSFloeYTlj1vKHrgijXsYxkOjIyKDmJ'
        b'7hRDhHHvSO95O+OrpX0UlUhDp+kGoZ26cWnJ20hXKaIGibdOVAkGufiEjNgkzcwnS1NBY3/sYpKTlAmku2hJpOMS2F9JLw9aMaGY3mYMee9mqlmZo7fExqQL+4FuxSk0'
        b'eM5sVzeZwBsrtIfWwVENBKpuL7Mr0LVJNkWd5cSp0thaY6tdYIAdVHsUDiEPWahaW9Ows9OI9EzylsREsvii0gSdTbhZ996iVCbHJLBB0OqOKWnJlGSd9iLpWvVgk4Ug'
        b'THvdndmL51AWRLTIqJSUxIQYFpVI1Xi2nnpH2OteO15qkvceJlV6PsvsyHe5o4ye0jK74PAQOR0MelrL7JZ4Bw2yDu17pQzMlts/RiKDNsTLU7vV92M6Gip0VKvCGupU'
        b'YccHMQ0n3NGHaagWVuoIerzuybSt+Gyqbb2RxcsiHT0i3QU8f9wHV1dRrZVqrGNG0SCfi26C3rYEy/GkNkhqHdZDWdRopl8tsZnCAGEENJgyqIFaXzwZJlAL1OOZ9T2q'
        b'7mKZVtklqm4snmBR+rB/lwuWqokYKElHmBr2wN/JPsLH0S/cLgpzBtV5BTCZy96WUOqTxnRvF2xiQVs0JoqI85exjKh8abiPIVDMyYgf6l1YFhk+UL/u4bFZaaeFwpDr'
        b'cx6u1tjqbs86iN+gDtHixMOgnCqTbVCnyqRdDfuC/BkYkJNfMNWlhTL0sAoLjKeMhPPGPfrrYszFo+TCSSsogKYwOK5YCcVL9sBhyIML5OsU+blv6w6ohDNLojdCCR2W'
        b'fWkJK1du2Zg2ZT3Ub91sweH+BWPgKFF5hBC2vXBdKsXOFBMRJzIhymAX7+IGN1QhtOe7l0l118xvLakbFo+E4sVwIBoK+lSqAE9iNf1MA8kizbFQxkHLSktbuGAjAArd'
        b'WePBYrQ4caK3Ee+SFqVS0D/nS3pxtcgj1GBAKSpVGFammJpjVZi6v3vh4FADA50DGrAQDWAOUb3OGWaEwSH6GjMsssGLUA3HGZtIEqlfhy5Ypmi4pUUkMiQVDOszmkRZ'
        b'LjRdPgcqGPChCPeF+WuZjPh51PwCLSvYnCHF+jP4EjKRDuop/aDEikzsEjwYQtTtEh7vpJoux05Sm0DayTmroaOnpOmYoy7Kp0dpjehTIhRIodp6Cp4ZDmfhtM1wMQf1'
        b'gZZwmujxzCgS4QlH1UBLTqvNesEsifAEVpMXXZ1PBicPqe7OIvqgKprDwhCTkAl+DBwHGkxMepl2Anzlfk7OlJSkH3wVFsHpEE2tTPuuFtJfDSorOCDOUK2iRdYHZ2vg'
        b'Jlb69JQN9Xho0PIHLzvEzxq6wrBTMKZdhkuJzGhETUZ4B2o4+lAAC7oRQj4aVy3qIczZjDV9CHNOwWnKqUj/JbiPvyhWHieaVYBzcuDKBRWvuFp0jJ0XlHGw++u/m1nM'
        b'+vDsixNPfB6x5JTTmITkmvWebgmtlfdv/lL1M/9K0ah3go83vXEsZ8cP9y3K4+93u7/Q2Ob4p5KSuNWlS16TfGQu/yzSJ3lluXG4paN8+qbny0d1/LJpZKuz7WsrKwre'
        b'OH7u/eitHu9lT5x3753Rr33k8XJ2nFdsyUe5ES1vpsdd/cb+1M0j+xsWjwlvuXklW/H6uYffvhtaPrq5o+RB6bJlKyNeFjkHf7Hv6/drR/4Dg+U4sdngzs+HZgXGT331'
        b't9zP3MO2Rcxdq3qq6edri4Osruys6zj7oii28PtRb6+JGBE199MJCS98fOTYNIcTR1a4N90c9VPjhuYr/3w458umrw1XH5m47scvPlC6/TxTccs+M+We8sjPU7+pKw4O'
        b'PbWwtSHmXmjImPsjdu/9bsueD4wfLrIIzlnEb3rBfUz9prn+b/Nvl9ZfAPmG5Qvq3y0a/VzD6SNtXYuGpfw1X/nk+GdD7M8/pRz56ydPtb23/m6Di/LjbXtOj3z3t7dm'
        b'uSbEDnee9NDowYWZI7vhUsD4l44emR380GPS0dmdCW9kr/jHDy7PWV0u64iR2zDjDRRCC9z0d3aaPLePKYnsgzcEqogyzHXtZ6DSh70irDXGAiEo7xocgRZ1+CLc1Oc9'
        b'oV4qhD1W4eWp/r1jJuHsIhFe8oA6IWhv3x68qg6bJCfJObJPU+PQFGxlNqowsugbtRQoWDhWw4KSKg5dnS2YsU6TdxzSYCMIwAhQsE6Ep6ERz7BbFq2AcxprGHbi+V5k'
        b'Kwo4x8xpNnB8vtZMh3V4TLDTpU9h7du9wE2IwOQkUJjCIjCz7IT2dcM5zKOIuL5kMzgKLRJOP1E0kdT1CgvrJOd9qxpOQrQxEg/zLgmOguWvGY9R7gqyHSft6mN824g5'
        b'6VPYuGBpWG/rW8gKtf1NbX2DS3hbCAOtw7PzNSnwQv67DdwRD4fqDaz6LvNtyFVHyggnSfN35OHmeqxk3R+ht1httlsPNb2oWtZLhPjGw1tHU9MnaWWNk9r2GePGsurh'
        b'UtB2/wBfKFanouElaO4BUXKF6/ouSXiMvSR90i42e6BgEzlngokwYbZUvACvkunFArmLIRcbWKoZEX40qWZhKqEGedOHQalLoNM2uCgnNVggkpniGbnhY2ctm/9nIuyi'
        b'NSCRRVRA1GU4zOYWGvMmIpaYLjLhaRq7hUhfbMhbWZixdHKaok7JL4xZejmluaCf9NVp5xZiW5Et+Un/jWJJ7BbkkzVvqGdGk9FEzCwpMuOtWek04VxflDVRh0GtXza1'
        b'DmvkYJaxtLq+AZ6P3+m9U8XrdOSL60gVr6RWQZrgp9NMmcN9Z9fbUPkYDdUdA0SxRJkZT4gs4eL0tdFA4iHh7PPlkgeRA1SEkNgkop0qH2WrY4YBtTJCVdEopWx1YMAQ'
        b'GgdNpLAZoHE4Bak86ZooIMd1FU08OB3WQwnZD8yudJXdgBxRsj9dNB2eomSKQ7gxXtMc6FYeM1z7nOdXoIxpHo7Y7i6IBXB4heBMwhs7BOqzvKXQSK+lO2N+GNlRnTPI'
        b'Nz8aSD55o547XjRiwrEIz3lQiUHC4UE8wY/joBIpIBnddF3hJFEkmPuvUjwa6gTvH+7dzfSn4hAxJ+He95VwkY53Rs/kWHHheGTmDAphyW21IipUIwd3iAB2hYVhJRr6'
        b'UdBJIq/X0NQTcmUfe4bmJxdJjcjUHA2neDxPHYVFkMt0ilifYAe5faAeOTNqOUkmj7nLQHgKjhjZ+vtTYs398iA9Tt9GZIJnSInMxVa7dkwoltN4ZmiHDg4qwrGDXTGI'
        b'2hnKcOfw9Bg19Jy3r6Al5KZBBVNfsBZvCc6wDjwsgOhdkkG5JiEDc+CWkJCxyJE5SaEqAg5oE0EqoFnIBOnAatbsqW5QQxVACXb4ksnO228Yoc7uHgUdaiWN1PwQ88vx'
        b'qxmGHlxaZRBKXlkNR/B4OO0xim5nGMzj1dkbWO/fXlXBjeHPGRm4RpqdWq8SgCWviSdxS7lPVhlzkRNnzBkr/PHLLF+uktvhahYZ6Zdou4Xrw4qsr5nEdMoxVmQbstS4'
        b'LdwuXsEp+ALRSG6vhh+Z0nJ/SukxaQKrpyItICEpVsOQLEmkvwzE6iXfNuhraZJV3rRtF+EYXmbByZ5iwZFppJF7sYplO/Ahs+fiDSyG4rlYkLF4WVyqb9qeJMgdy+2a'
        b'bgFtmCtmLftzhClny/24x3xFZEDJokihubYSG86R4/ZIZZG7Xlwl41RMwoAjfmyE+iESwn6L4PGL2MzwmgRnBSVx/UgyvERHXAylwkCdMGVgs6mm4jQs4MTW/Dy4hnfY'
        b'21ZHUiNCymyRLDKxanqkmhQwD+qhlOl/7lDNcnRGxQpFHcJcmq1E5pkBHCHa4VR+wRS8IOeFpLIiy83KICrfYc5okZSXTYJDf3i08slopR0WyH2O8Fou67SjvE5QZfLt'
        b'Yq+BYmd7Dh4LlGZgp7mIznvSjDlwYSeb09A1GxqktJCJ68gigvq0Yax9szfgTWw3wU4DDs+M5vEgWV/m0MkSz3i8gIekFPduNLeSW+khE9LEbm6Ag1I7ewdsg2psCyCz'
        b'3E+01muUoPZcMMjGdhe/8diI18glPdjLY23qHrmI9fPSpXCCrVgiheWwFQs1G4SerLLGYjYAmLuRDUB8UkLHs5fEyuWkze5OT8eG+yutw61vXzv2/bN3F8Ni2WSRW77l'
        b'eFtLPe+nioou223eNdnyH4ZZoTXjslaveG1bid+pztqIf+TVeK+pXvTEs1CwNaJWOuKh/uu1sSud1//U8PKCCbl+DZ8qb3/9uTL5PeVfAu/Hejb//KV/SXrzKpWN7bYx'
        b'aSEN517a/oF5ivntGFW6X3TdL9a3VaPsU+WRiXN9Kv+6w3KNywPDRvO/nHU1mh44vGtsnNmKlp86rng8XOgQYXT+8Bbj5cOth6/zbXZoCKg3bjlca9vuO8vc+W/la2p+'
        b'Lv1t6qx1MzrCpqhGv/HAskZS99niUd8tw32dvOPV8Bn58wNXSxPnvfpN54rAxnVtD1Iu/W3qq8p3toZOejXCPezSKXnrpJmKz8d27B+r11l+uHPCoWOfPzwafvd/P/7R'
        b'/8SPo0uCzm/U62xY+9ylH5/9ovJ69xeR3Q6vPJ21KsG//uOs83ojfjX50i7x47GOD4vXvnj5r69Zh1vtWn31jte10o6ZdwNufLdpRdn/hNa/E3vG7X6o+V+v/5gffuPl'
        b'Va8937BD8q0k6O8L2wuXrT4wr/vbcrcfu1t3P+Oa8FVdx7Tnw75aeod/54X6pmcPxq2dH2tmbSm/90MB/sP6+bq8jKdC7+dOzDvT7qkcdtczapykvTsyZ0FYy/8063++'
        b'51e/htev7l12OTw/c4fNzVeCx24enzs2b4H93bsP6uf8ddvxCn6BSVlNBe5f3XDLLfu9Ya3TSrdvnval/WtPJ1zvnuJZsaRw7d/+Kan+s3HLRzWZWywup9QteH7n8Q+7'
        b'Ol55/cvL3/j9tSJy/+VVr5Yr//LGb0+XBN868OXUC38bPdN5z/Pz95qo0r9f8dXGHxJNd3/t+LBu5owXZj/ffuiQ0f98b7BcGvSS3z2HwBDf0pj6us6xVV9lmz09L3vc'
        b'3Zajn0m/Cbq/8YW/NUSP3zjT7CPvPXkLnlr4WkbBT09Gl/y05m77jk++/8fDH5q+2/7grdK6F9/b+PWYf/7zTNJXzgaRl1vNH9p/Kf8502Ru0tsvX3QOer40qeYXpzXf'
        b'J5l+nG2UMWrenje7Jt4pTPh6+/6jXa//HPrZ176/VuzdPXzHy121P68UP/P522+N8T99OM6s5odTLy9+r/LhEwte/jo65JdD8b+tPrH4nV/f9b30s8z5n9/G1W/bP827'
        b'MfSZjFtHrRc9iGhN+GFHSMnml5t+/Ovh4xs0n6fvNCi4sTWkZNZzvt+eylaE/PBtk2F7ashfTKZ6H6q/surNRUcMVo64u+7zTcrOj97Vxw0zXxj+/vVfvtqe6GD+o7P7'
        b'1/Du3m7zdZU7E0Le3fZBtsFfJF9nm6UfOPOsfP0Vpx8SR99V/Wn8G7P/nPni39bMnXYgKNVha8CzT3Vkqr6tyywY/auX8ZPK13eXBcnefGpa/RGbj5/4Z8aL8l23L+NL'
        b'i7JfCJy99/sj73/vlc53j1x24TV8syAtZnzVb0EjZjssH/7l8orCb40O/wXfdRxre3f+zVllI5b+Kj/04cZfypJlH7WLx4w7lvPce8WLHnp7X31217oPvr46PCZEtSz8'
        b'8q/m5usmfWFlL9/KEC+wEQ5Ct5pIBUrn9HCpaJhUji8UMhCJrg0dai0WLgWrM/4yjBIFjbNhD9xg2t4GqNTEaTBtzxDzBGX80OTd/uR4jMc87XVzV3F8rLWAfHckGTqF'
        b'eJE8qz4qK5EhjzKd1RjKoUujswZP7BUzotFZy6CUFWZMsZzVNJhEUW9Xc+JSHsxAyGeKIZ7MXEbhCaEAblGIQgGeMEEkVKYjCKqVRO+G23Bam4FkinfEi/FUKFNRF0HR'
        b'eKWzM1aSfnNKC5JTKaCdRelgsZibiRf0Q6HYnGnIFrOhiSrQ6+NYMfqbRPb+dun0VBk2Ocw/wF6fC5gi2sC7z8RqZi4Y64VFpFQXvINdROamVasQTZmItSxlcMMSAwHJ'
        b'jYhdd9Robpkzp7I+Npg6T4pFTtiGZXACL/iLOQO8KgoeAdcZBorjcsxj17vwOL3HH9vJuWQKRURiwAKoZh1DgeYOYCkFR8HDeFbAvLXGMiHDss0Ba4VXOEG5pS95vbFo'
        b'1VTcx8rfQeTH60p7X9yfgsehnqWOVgQZcBbQKk6fDadYERvxFF7393MkR2Y7pd0kEnS3SJyO5wV7Ue1sIma0+9tG45VgKZy30+eM8JoITmN7NrthwSKsUzrjWWiWY4kR'
        b'GRs9zhj308i7ffMEg1InHppKqzhlpZEcW0krxaSJXeJhcAzOCI04j8fIVGY2F9tQddIrUSCaWHTTCiiFo3QoHZzlFlhtbGdPTRtWtmIiOhN5VyCTwIJIqbM/dspXLMNS'
        b'0glmonWbYC8zKmDjNDymDOIpTk4zFS/OYTe2CfyfDfbQhLTVtPfTgxhwpR5naSMmnXWADBKzhTbj9QT/PlSiRLXIk0CXEeXlVQMiQhne2q509sVreBgum5A7Oc5MX7wI'
        b'LsAxNoXThuMdqZ9TQCpc9CFrRCnnuZFhErgqWg45cFYNFnkTaugFInFk4W0i21iuZ9MoCq8t95cHYpGpgK2tRxZitXh+OJ5lFiHVerxIq94BN/rgMSb7jWAzyAHaYL/S'
        b'114u8qSpylDNk4V7FCvZSzdOWEE6t1SP4xXYJqWI+MWb2aiIbPGSf8DIoH4Z0A1eAmLQVawnKkUpw1V0XSlgNJqmC1vTrT0T/FnWc04vI5V4uMxIiB8rNyfilB0U0wjE'
        b'4tQAuYjMmMMiuAXHOMHMtg+74SRFlwzELrjlxHNGbiI4RPSbCuHd3RwZbbk9ttmOpTU3TBAl4I31wrMVfmMdyCCl4FkyGAzH2RzKxdFp0CpsMy0h06R2ztAEZ1KDqAx4'
        b'lsdj2Gwo1OwqnpBK5VhB1wTrFD08xBPFrYvMJfp0Gu5lWwe1rk0lUqyEmtdWkQ2VVssf9qUpnWlroVvEibGYh1NwPIF15go4AF3+ATsgh9nu9Tmpn4isZTgoVDoHDtmR'
        b'ASLLoEaeFkCBIExdxES5gKtsjNzGTmU7AxcOrXid6HNwzJXN7S3OpkT9SMOrYuigYBC3+dHboFngV56gNbXCJTt1GJ6/YOGEm0mZgmoA+VBAdQNoW8SGTg63LP2dnVbb'
        b'9DEOYwveYu9butpV6QsnEu1JLV14znixCM5vsWMIo2RvqrJWMphUslYtUxyoJYJWmsjOYqwjmzlbzdsxV64kSrYxXHIkOwPZya+Qe0ZaSGbH2++GJtZZO1YTZaGdXDNO'
        b'Y1f1IngsgUqySpj5uQZvRApG1iU8gzy/gw2CbbGRukWpJ8cCSjKwXcJJLPmNUxewxxwchikFoPvubB4aaaBswWzBoHoYzkEB0Qyw2E4EZ2Ev6axGcsskEA7KGKxzJ1W2'
        b'89uOBdhkL+IM4KBoLraSg4vub4nQFkgjaoOhI4ZaZIqZ6dVcJFYshH3CCwqgPsXBjmy+lzQbCAVDh0pSb1qC9QKiqNEDi+yv6g3SFi5INsJ1t02r1OC9eCaZ7qGjljOt'
        b'Rg+OkGmbiS3C3tNNpift9ZHRdBugXWaMHWQ2YOsm1vbs4RRJgpE2Q90yUQTvtAUPs13JZU+Skgy0EfWW8tvJJ1b8MDwohmNj7FhMqhTrl/tTmFbfSAFUfdpMNhfEmEeh'
        b'cwOhBC86qa21KQ7C/Oo0XSdVmRqJIA8vc+IJvOdw9QSCveQQuqnEMrKo071F1vwkqCB7+DhBk7/CAovLHMjWctPZN5XdZYrnxVMSgllHZo0x0gDO74FLGsz5GmyGdiaQ'
        b'LB9rxwDFsAVaXbAk0FHuG0i2bQErmZszXx9OBhqxMc2Gbpng5LgY2stMDSXSdJpsjvXr5jO8Yx1w72RZa/Fkw/GSocsyvM2GYXj4BCm7z4lsX92pdL/lLOnSPJWymt2g'
        b'hFsjKT02XsHq3hTZgQ5kzbKNsxSPwFllENbFy9UrzFsEzfOxWmM7P7+dzBS5CHPZRl7Lw368MkPY2Bp3BpJrkJOp2UFmiY1W4jEW2htrRLoLy1fpDwKJC1e2sNVJjvGu'
        b'4epGQC3eTqUvI43oFEPTdKgXDs3OWTsFuPwAyO8Pl2+n3mbhJHTbSekpCO3QRebKNZ6cuw072NY0DItnSLGEiUWBWRQ2mROt3DZHmCBHpijI3u7H4xEj8thVsg6xgWfL'
        b'ZK7UkzbeWIaNfpQTgq4Ta8gXE5nxkoMArnfIWk8q5zg+Gm+P4ogEdWmiIIKU4FHWr20uxiuD7OzZiWSxRQwlMuxir1VtC8d2R2dnUdJE8tZ6ijd8iDSFyoSbN0yTUmC6'
        b'WeEiOT8OD25kUsEMOIh7lQG+pKeM1E2hyxYrJdgR4eFNFiRdCK5TZ0uJRFwN50iLOP1xomHOZETYUVNAJn49Y+EJciLTsNCezmayaGt3GAqbRiuehBaliz22+kDpCjnd'
        b'drpEPmQjLGI9bLWFyLdOQZhP9kpmzdjNY403tLBxNMGbkQKyMVydoSVsF5CNT2iccafhlq/SeSJ2+ankZAMgcptIBNVE1RA2lebtdFOkErRbsqOvuR3d1UzxhnjujLnq'
        b'Xc0eatWx3FfFFGCDBXPDAdJCGrUwMn6uv3OgPtlxkkSZ/PwNah+ZiRI7WYw3OW0n0BBvzB3D9jgVto8X0EmgYK4aoARy4XCA3PI/A3Gr/4jrAgiFkKirn8Zs/8wJZEiN'
        b'aLqdQNmcvSFDFqZfNrwxb8WgNijghrWAKiiioB3CPYYMrMOQ3GfNW4tGUV50kQ0/xmAUP1FkwVszjnQT3oyfLJrMjyKfZHoUg9hMZC2iPyeLFkss+HG8rcSM4Ruzsqmr'
        b'ibfgR4nHkO825G/jRKNEVqwWNia25A3UGeUo1lWuBXnGlj0vYB0bi2xExmSDHiXRgIkIXO0y8n0qKWEMP1XfkM8aqcM3I/TVYJyuj+72Hl9RA+nqMdSQSDW8QXxFOdx9'
        b'm97eosFrROqSSn1RafSbUrBcpgs/KHexXNLvclpWr4t6ui6m7RJsodpL5LMWXYA8uecxLvPsMvkxS7iBvi0th2ddl9q/KgPuEfXco7nMC1eGqLC+cKmSp8nZQUHkRdX0'
        b'9xr6rZb1BPkr+5vcpB/4Stp6juWth3r5eAd6hzK4FZZXLqCvrNBCptChS6NEo8I0sP6/AEWhPaCdO0l0mVI/Yxz5aSiRSNSY3eJ/5aeh2MKCrl2Ot54vgKbQNaVPfh+X'
        b'zRkxAp0l7lHSDFOizVSnpPdzSIi4+Wv1sSTWvQ/SgLH6p9J4IGLKNIWdQq4wOCpRGCrs4ziFA/tspHAkn53YZ2M1qgr9bK5wU0xXzGCfLdVIKvSzlWKYwlox/KiRFhnF'
        b'RjGiFzKKey9kFNtyA8UcLTLKGMVYLTLKOMX4fI5ipfwOZJSJ5fqKuVpcFNM4PcUkxWSdiChTFFP7IKLEyT3umTNkIMbvvTQ2OiH9gcsAOJReV/8FLJQ5Qvr+9HsSr+AQ'
        b'73viJdOXsJ1Bsy9Q/JO0DPqH7fTbDvLt9xTtRkEzft/9c34/0onmTSzx1a0v0gnbau4Zh3gHBod5M7yTyf3ASEKXLg2JTe2bbC+gnTzWrT0gJdoG2w5WqhY/pG+N5UZ9'
        b'yqDjMbBQ8/7dpLusIV4+2BW3tP20o/7DsCIDiVP1ggT/2KlNwwWAw0A8LQAc4uWxggfw5rZ50gy8A20Ul4xiDh61Uib8tv0NTklF0e9mhVJOd5+ou3H2H/qP3RNlHPcJ'
        b'913eyDkzuLnbJFdNnpbzTMZNt50i2NjwRKDayBaFTYPwolZoQl5YMtlg0g79klGJIcu232L8g+gkVgYUOWqow55+fdMHpWTQVz8eRAnds/+jECUT9B8XokTBGkExGGgG'
        b'w78Tn0SzoB6BT6JZRI+8Y85j45P0XZeD4ZMMtlqHAAzRuYZ13/878EH656oJaRVRSTQjgqacDZJApX1MF5zsAEyRPuOsxhGhB4+ADUIOH/vBc50eBeChqcnvgfBIiPsv'
        b'esf/f9A7NCtOB3gF/e9xMDT6LtrHxNDQuYD/i6DxOxE06H8D04/0gsJU9DCCk3BkFcNvGADegFVYHqDmPdaGYEOFGw2aK5Ti6Z1wMiFPaipRUjiMhc5PUIb2T97fHPds'
        b'9BeRn73/ReTnkV9Ffhr5deS2uHiFT9QX7xfFfxb5bPTTY51n20X5Rm2JS4wOiDKMez/AgEvPM3nfyUyuJ7jX9qdvcXB2isdOH03QMO5NYxbdmVOgQsBL0KIlrMQzAmCC'
        b'9SxmZZoTs1TtQKYOZqzDvWoncyaUC6bkQjgLxwSDkSiaTx/hZgA3BQPVuQW+Un84kNoL+EAI85at14S9/lvQAqY+SgJaJqAG6OsSRf7fgAWwfSyx6rNxQ4tVj4sNsJlh'
        b'A6RV8T0Cng5kgCUGGmSAAW/SwgJMHOS0HAgFINcfOrw5xkBdadqxUs36WkzlO4N+Ep6UynhxUrWEZ8AkPEMi4RkwCc+QSXgGewzVEl48kfB265Lwhs7z7623/v8iyb8v'
        b'sJpabFJnvm8jBw1NQf5v3v9/8/5l/837/2/e/6Pz/h0HFa4Syd7fm//td8EADLFl/F/CAPzHktfFOqVHS4EBzmkVHhfw1fS5TbCfpq/DFTypomkyMVg2QQgXCfXB4mAG'
        b'j0YThP2wnJGvraKoZDRZV8JB1bhFUGoENyf4C0npx2ODdMCvieZAFZaOxasC43vBdmjVpMJzK+AaXnSHgyrqPvAY5q2lkV/poxsUTcRZQi4cxGNG2GUOBSrKgivzCfPH'
        b'8mRtbiwW+TgKyTBYJDDP+upxm6YZekI7dKsoy7A4C8/69xKYiWR8iArNNIHYEfcHOrL4txCpAZaPg2OqBeQRM7jgqSGy9Q1fscopYhVNgvYLDIDzYT5w0SfQ2ck3cBZP'
        b'ynARwRXpdCgNCeXGwVGzxPRUFj2+B65Ao4adxBvz4JrZNhV1pcBhUyzsVzbN6U2ZnkYTeVlOvYSLhFKDGVgPNRI4yZjoJ4yGm6Gae9WjFCY8oy5qrEyPWxdnAKcpUB2r'
        b'w0ysWChNMyPdKLbkl8CpBdvhjhAwXxS/Etvx2nYlReO7wwdBnQNN7mPpCF62eoxhLzIxMaBKkckl/GPEb7zyLrkysrQ7vGKBGbiaFDQ0+R552Ka6b3H0lHREZKttiNGJ'
        b'qzE3K5/aMDe44qWRbmmSMeeton0b3/v5l8mhniM9q2OWP9Gc3lL3v9JpK9dnHs6tDrV8+uXqE2UfTlihZ1v2tVyZ8+bxXS8UBxkdzLLxLBuRETDmvbS8lKcL/zct/iuT'
        b'l6PsXd+b8Vx3cKP0tViDW+smmLyW7PtTzT+3XO26Nn3Vw+tvuf191o/bpjW9d+jcw8OjfoMHD5+Oq236enziiAUdk8+VvTTW59unak3+3rS37KeRX/xDOiLI175ws9xC'
        b'UCdq4LLYPwIP9aXBTsQjcEDw2F+BdmmfxFjXGIbdFgB7WfQBHInI0JB6ZA3zhH1whjnaNy2EW70yVmOxQmDzznAWXnxrZqCQr2rs0EeNgQtjhOiwE1gIR7UTRY/bEiSQ'
        b'KR9enC4M7sUMrYKEeTvcoHUxe3DjaKjvlY0LObhP4CA/MYmFbEmwaqU60rh/mHEd5OLlGesFnuQCqAnG0ixspW2gS7WYvMsMb4kDyNS5weqQtjoISzVczuZT4EIW7GMX'
        b'9EhRxf7T/ei6v8ztDsBrMe5Mb9THCnttmm0+H7EM92ZiuRCucR1OQ46DX6AwFKTqw6aJx5B6H4G9CvbwbLyJbQymT8QtgRNM61zgnj6N1vYMWVT5PcmqXniqJy1OnauK'
        b'3ZKBapX035gn6vcolTGFZYuKDRn9sKG+PgOZs1bTF1MXvgVvxZuJzET0etb4/gqS7jRPo8dJ8+xRLPUG96MaDM7+qyOb0/uxtMtuWW/t8lFN+jcndBIt7cGGRyZ06lLK'
        b'fnc2J4U8H5jNOSlItYRO7Wt4E6779/BoDJ7KieehfEA657ApLB0TigPdtfgMu9e6QisX7bVALOUmYosY8+H4AiHjqYvccEeN9JCFDSyl0wXzBa9SwWJDIVeTHw2NLFXz'
        b'SALb9++tEXNXmUIf6XhstSfHytq+evsMrITjcGqGK6dOxqTZ+CyDywE6yOeDZKxc4Lwf56LCCiEN8gY5xHKVNNqANPM6NJOaY5knkwiMsDTbQZ6CZfaU4p0mY5KN7iZ7'
        b'1xTyVBNNx5TvhHZ1OiachGrBUXZkAp4R8jHJW/MWcVABOUvZJdWWlFCsgQsLZ/iJ1fmYY6GC1RBrUrdKM3bgbSrB0LxJ1XwV3X134gl9lhvZKy8yYTWPV6FsFuuMlQEV'
        b'3Cdj5ok410gz491GQlrgpLiJ3CvDi2kPiUpNPIQ/vrjGh7P1nMxzkZF+01N8/3hq5ObfnWx306An2Y5iGEI+lu5WM7Y4kn001TcQSxy17E+UtIXivtDgRjl0iqcTqcWf'
        b'SGvtSinttA646IVF5mFp4axdHrwJt9h1FsetiEzMVe0QGus0xYYz9FtDpYP1e8N91LAhbVBHhnFAaiRcxValOHjFbjZKFtgILVLshMsJqaZilgGZDFWs1LwUA+6Q91ha'
        b'qmOaZxCnTmVMxlMBQryyCC7iMSkvW+v3LyWe/r7eFRv29C5dOUHYBtelGXZ4h2YzslTGmXI2y8Kc5rNjBFtm4B0O6k2J4MkY2LADu9WpjPzWeSyT0RY6VBa0ulgzh1Zg'
        b'ZRQ2cCuD09kr5i/CFiGPMSB1o5DFGBMj5AcXQtcEmsaI17KnarMYyeqrSVj45E9i5QHy+gM+3aowf+Vwb+uvvsp8e6dy2gTequqbkipDe7+yXJl90bLM5XqzTi4d1+mW'
        b'IVPWX3/m5NmSkyfGXHzp8KZKPYc9xX9/KS22Le1LmOV/W3nTpWbxjTkvfzzvvbkvv3P2zlf2l0Kmrfo523qtR+aqiPMHliX8XSHPG/9kXcT95bbLPfQjPOSn/La8Upt6'
        b'+gnZg/bWK9fX/HRzqfvRV/6naPGy6IPTN4xszveNMh0R/afahIaW2HAPh88UnjWmb7kGTnv2THmiclm1ZYr0emzMW6L927ZkfVMx21H8+ueTuxa+81GqNO4rl4evXfzL'
        b'pHf+1no/4KPfJiw8/lbn3Mm7mmpvLEm88JfE0uhvrj3ZifqzHv7Zcu3nsoedk96Pujvru6t7zO7aVcAXJvWnqj+NPr7hmXe2/fDJ7RW3RszeVzbibmnQd9cvR8z9Mvrt'
        b'l94bl5KYtyBq43c+0u6/3z75Vepfvh7zzguNrgbzlwT9tu9o9hNdd+86ROrP3/vGhT1Bz8Jn4e/+4uvo1x2efOt1xf33Hb9b/+E5h8tPbiwcGx1XlfHEzoifZp5MlnkU'
        b'2MbeNjrSeSXiKdMdhVHLd5W/e8ng17fNEuMbTs145kKbX/jb3vdXjv//ePsOuKqO5f9zz73USxMBURHByqVJERXFhg24FKXZpTelX7CiggrSlaIgAhYQBOlNqr7svLQX'
        b'U02T9MSSGFNNYmJezH/LAUGNL8l7/1/8BNhTdvfMzu7O7Mx3RtpvE5f8ndvk12w3HDT+dN99rUuNO7792XPdB30fWDYteOV9tXf3PPh3uXrn+KS3fS50Hu4S7a1L/7Ft'
        b'87NdMZ7OJ+Cl+vzs3Nf0/cLDvnE7ZTA95O2w5q+Czg1o/8rNkd5cVvnF1J21t88ryt85/9pBs4DQFa99/lbHen3f5Al+EVfWP/D8oiCg7vCtwFtB43Qq7Cef9Jp392qq'
        b'dexrr01/ox08JPfG3/xF3Pqq69pDvxSfD6/J95/83a5nfxG1BHw7ftcM64zXfo/8sdXv25NJ6pXPyP5ZkTA/3frBKZ9S7bsvF+Tvev/wrgfq8/MV0Kr2vcvzxjFvJJT/'
        b'/tzrv10vyF84WP3ZvP0u88Nvjp/0q+PB/M/+7fX2d2ZflJ7Im/+g7UJI+IzfjN+9vGmm41cPLtT29Rh1Nz+Ta7o7/ZX8+HfvHXj5dvW6g/c075jfmXBn/uVxC3rmgEWP'
        b'dK97Ytm9jA8nff3CxTkh6T8ckF2rSe2cvrd+/hfvi+6/sruzq6J49a2v9t969quAm0pbuldUpP5u3CXR/O0fF2z8rqdM/twhB720onmd0b9v3PrwhOsPcaX3VZIUjo1X'
        b'nX5I//Zm7pgz9z5eWf1sy4cbayvWLHz7Le6HCgOf8r3SK69/XVG1c1/rxMOrFhz5+SfZg0+nVZ//9pWrD6KD/cu7p22Qe3HVV5/7KspbFsfAfefRyahhiRsdgP5HwX3t'
        b'MQwRlSE1HgpQA8dXCtA+uKzNPOULx0L7qADMnKHJWFQh2YLFYhaFZZUOOkPAfSOQfcmQI44wVKE1+KEM3L4AyBsG48Fxc4kmVC+g/sUp49BhgseDrDXozBAcbwXKp5rF'
        b'9l3rFCNzgWnipfBUkHjJdsiiQniI81SCxcuySpS54c3HnLhHC0g8yAlegA4p4w0oQ5l+qy86hHJZPBu8D3cIgDy4ZMPc2rNRux0B37nqQtUw9s5nH4NFZJtFMuydHJ2F'
        b'LAF7hzqVmMJWtRQdG4LfyTejcgF9Bx1wmVJhhQU6N3x/CHoHBXCJh/49Lsy6Vey7BHKscRfzqHJDsHfRzmyMKqAwSYDeuU4bw5B3cAIEL/kKC1QhQO8ewu7OQj2B3kHH'
        b'BmrcCo1ZJXezdN2yZhh2F4IqqQq0HV2EImi3REXyR3B3fqiJjnAMhyU76JBZPwK7229MbzvuiCV9G4m4Qx324rEaOixEN6raywBzmCviGGDOO4FqbKgS9fpTvBw0TNzE'
        b'ofMcKmafdADSZgyj5YawcuZwmsLlyh3ZkBzFm1EzVuzWLB1S7eAgObqhozkdlW6Relpp4E5VyfAnkwgdTc4oi+qZBqgpngJpRqJo4CAUiENRAVQyMF4V6kKHHkXjQeFc'
        b'AsirgQo75tp+JslYYe36EIcXiBrEi7GAm0H1XnQuHp2gWDzIj0QDBOYhY4g8Y4kEtULNElpLJOa9ArnMYwTmbiuqFTvtW8vU4los6uQRlNoIzB3ubp4YiyvQxJBqR1zG'
        b'KDzhGDQQHAUDbMShg+xeyRLqYE+gd1LUCwUEe9cup1T0sfeUo2JU8kj6UbVdjPP68afWEexdH15DSMsUfWe0md6dC/Upchv3UQGixPpQvoYBM9JmxklnBJqNRt6Nmcgq'
        b'zkenUDYF3lmNUxJgd1gWz2KIA1SylcHu8KVMdIIB7+YzgJuB6lICuxuBuZthJQ5eh9JZWs0DW3ZLzawTUuDiMOhuI1Sz440TqGM9Ad1BO+qMegi680BVtFkepS0naMJC'
        b'VM2CWhHMXQA6LeBf0ekAhfV4VE2/lIHusOZ0kVV9EfPLKXkAlLuPhN1BJmJh9UkGzzCCKRlCzGihNrGaJ6QyKMo5Bz8Gu4NuJxggsLszUMaoeAgdgdNYvLUcT8B3DHm3'
        b'XABWYE2lYxLkuE9D59xGRMA/DANsRWtD1ZAviLPQj4qxOAvnhIV1HNR4yEedQEElVIujt0Ab6/GhydCogBJTz5EAIdQXwTB4pSsShyF4IwF4mJcGxFCSMpFOZBtM8iNP'
        b'AuFN1ZGYx0EO7Yk96sZc1k5vQuXyIRgeZrkmetq1GB1PFEKdTUUnt4hmGZixoe6cCDkEabd97aYhCJ4JnpBDWZyzGApPBKfRUQbDqzZgZOvA/S3Fki2qtCZIPAGFBz0M'
        b'xIr64NAaBsMzDzAVQHioazP9otl4KpZRcBCeMOQctBP315Dm6WiRWMzewibcZRhwFIRq6RImVK+BPCG3K96QcoRTNDgWHSyyRefmMux5K+rXkcJZfqhqwqLqqJBHDaja'
        b'k9V8CdX44JplYYsJF2J1dQrUwGl6Lx5dCrSYvcFsJPIvFIroamYINdMUdIecBO3masPov0kLJKgAb4YM3gvFqAXahI0qbcYw/A+yjGgH16FsPETtqA51sWX5IQBQD+9G'
        b'tIONuO8FAgSQ34zq/EVWqMZfCKlnNE/AAI4EABp5itGpiTvpPoVFAbgktwpQ0D2QYABRgQfLORxhznjtIVpvnpeYBLAtZSvxsfj9w4f76GzyEGTPTkxB+5jvK7ZRyN4s'
        b'VGzzZMSez152KHgIyrUYsQilsBqJP7cLDoiTUHU4A6+dn2dPGFYuU4NsmasAyRpvZI3SJKvEkxhoqX8G3v7pQ/hD0UU3EZYJyvml6MRsVkcj3q3aCEhvBEAPj8pZsQfq'
        b'RGw8UJoJnIccDTxVh05k6XnsPpRNeWnMIsx4OVYzoV04D0UX4KA7/YjxeHI2KnDTXlJPOGKB118d1ATnd4lTUMsaOsHNd+ywwFyIJTMPvKm2E3qd4PeoCXBNVKqHMhUk'
        b'wmoWESLJF4q4MWui9MV7oXN/ErMq4O3h8JPBi9uhxvUR8OJslEqFpR3QsVgA/g2B/pq8Ke5vyWTGhdXQvxXPP3TWdST6F5VDA52ffqgf0hWuZAM0p3sdQZlD3lQmFaRD'
        b'UZiCvsjAzfS0XdXWj6ITIV0HnbIY6mVS7GPwxB0J7OtL8L9DQ71k+EpUsIlCLCf7UwLbbw5k2MRZfqqPQBNXRdN+rkE9qF9qhvoXEdGAARNRMzDYovbCDUPARDkH/QyZ'
        b'6IDq2MqWro/ypdZQibIImo+BExesol0Lh875dP0ZiUyEVCsxZEbhBZOBYm1QKkUnTnDG/AvpeO86whiq2QbqGTpxCJs4y4GgE8cGscXpaMBuLAtC81Jra16AJ87cTlfh'
        b'7egydFN4Ij9lM4EndnvQBXGBAXQ/jk5U4BX9qGT+RqihPZorhmKpFV4wOuCoAE90iGM9Ook65AI40VwHtQ1hE1HtPraHnTFH1QybKIuA4wI20XsrW2zOJ3pTaOJFG/ch'
        b'YKIDXvQJnWKwNMuAiSNRiXhNPSXR5Xi2DxwJhFKsNE6wHoVLjMdDRBjVOUQhxPV4iEmELAexI/RwlFqLplgTVKJWAMUlUkziDsimoq0IT4zzFJTISyB9l8gJ5U6h/BmE'
        b'jmgLZ2PoCDeMPbzgJ9P6vwcbUugUNSPw5IzraWaE/dz4IbyhjviPkIaqw0hDXfxPj2a10cFlgjL8DwhDsaqABpRQ9J+h6qNYQ12KLtSjT5DwlBoSQ5GBSMKv/K8whoaj'
        b'MYYGj9oK/rcAw0wVAdfxVPNFKnd/FMzwDzol4xPPEgtJ1ePwwtF3/sylkWhBMQP9ERxPYu3j7zr8Ya1/dEeZ/d0+DAIkP54I90usJA/+WaTf2P9LkN8p3PYnBCBKwq//'
        b'XZCfqlhHWQD1zRgC9enikuGSZLI9oXrPhdLtmtA4YfRxuogzQ5eVYtBxSB/lvasl/FYceAzPt0FSrFKsVjw2nCc/i7WEv/WE3+rsd5Q4XBwqzuNDzYdtXSQjkcZhzcNa'
        b'h3VoZnGNUEmoEsXRKYUphyqHqhziQlVD1fL4DSq4rE7LUlpWxWUNWtakZTVc1qJlbVpWx2UdWh5Dy1Jc1qXlsbSsgct6tKxPy5q4bEDL42hZC5cNaXk8LWvj8gRankjL'
        b'OrhsRMuTaHkMLhvT8mRa1sVlE1o2peWxuDyFlqfSst5hpXARycd+SHWDPv17RuhM/LcB9dgUUzug6mEppo02ps0YShuzUBl+YlwoT4/7LQY1li318F0uGPQ+6eIf8dYk'
        b'7lIjn2BAwmFnn6Q4kpZDwZ5xsLNkv+1pEgvy1+xRlQ3ZDRXWJktH+CEKbnUUzSA47+G7SWGJNMdG3HaSkDhptB/hyHwbliZhQSGRJolh8YlhirDYEVWMcHQkvrGjavgj'
        b'T6LR1stRBc844kDmGm5CM/EqTHaEJYaZKJKDY6KoS1RU7AiQCPXRwreD8P9JkYlhoxuPCUuKjAulfvO4z3HR28OonTWZrJLRu4iv16iEIiYroqjblNlSmeDxGz3amYz4'
        b'XAnuiGwgZgnjMERxSxMzZ9nQY0EmijDiFpcU9rRBImNotkxGkCVBI1wPBae/uMSoiKjYoGgCcRCQ5JgEBL7xyIcqFEERFNwSxhKn4KfY15uEhsXjbUFhEsc6Tv0HzYR7'
        b'zoTDYuIUo93IQuJiYohnM+W9R3wVPWX8oHhnTPSgckhQTJLD7BCxsNQoCcsOtYGRoKoCVE3l8FA6MyldPkR4AeHDtQSjuThT+SC3V7JbOUVMjeYSajQX75MIRvNwmeST'
        b'+6I/AV4bNXn+2EvtjxwX8Rcxn8V1Hu6C0x3NXEPrfThWeFSoYyqeik/2ZjULYyz0R/P0KaAqSs75BBsTEoRneiDuUiBzHmSVDVcykt3+IJ9QUGhoFHM1FdodxW6EMROS'
        b'w4Qpq0jGc2l4yXgymGSUQy5LE0RmXFByUlxMUFJUCGXQmLDEiBFJgP4AlpKIZ2J8XGwooTCbx09P6jO8r2kKTDbaqcHCU0GUroYLFu2v37OQ1SfJXuzQknXlyN5uS1Nw'
        b'UXtVz70dfJe8nkwkLlvUa4XaoQAukmPJJHLkOklGYgzK4DjWudkb6BzKC6CysC+z23ejsxuxAl22Gje/j9sXgtqopXjtBBIvGotscyM11nnM4NjDqTEoH7VPSsLvL+AW'
        b'oFLIoA/DBglzZEuIiEYpERwzpKZG7YQiPdRgb2MDxfY2PKfkKFqNGiCL7vrQa2yvgGwtyNpBLRlwIIAor2rmZiLODoqVLVStmTtCEZyETqm5GToWJuJ4D9Fc1At11DFy'
        b'H5TwCjhhPqIWdfJDxE2ZrzQlfBU1DRtNRx1SdlUMvSLU7EmUw7ZkIpBCjgk0jexEoqs51s6h1cJVjovLiUnDH0pVjXzhEg0tPRXqsO7TbuGqCu3kCazAOvCxUCmWiZOJ'
        b'XjcWpUOXHGumzZ6QawUF9jYOPKexl9/mM5/eh1JUZSmHMmgcvq/Maezjo9dvpo4Z4wKnyjWgevimiNPYz8e4zUqWEUq0J+9jOVlcfF3wI0YpVmtcRlqJlmurjMPadw31'
        b'FQiGJnQRq6iQDamYFdaQXA1ESR2L8sXoFJTaJLuSOlvXE0PWQ3eZoYw2kOUul1vxCQtRhRHQw1WUrQ9t0CbXQ9lyqTq0oRw3bx8uLFxnLjTCkeT1RHScO47WtRAP0ajq'
        b'iAPoLDc/M8hygVwf4nwp94OWITaVUb8cL1cl3enqWG0/p6QEPSumozoZt2KHHlSg1gAh+DA6IYJ27fhEcobYLXKHohlQieppDp8gJRWpKgkhgNWahajVfK8SHf0pWDVP'
        b'h3aNBPpOgwgr6GXTdNbRVya7Gyvi6TGxWEMUuSDQVYl50tbBhWhFArRpkFdSRX6oZlqCmAWEbt6KOhTQRWtD/aLxqNDADzIou0OF/1I5HIX8RwZv9vxkkg4VnUWF0PQw'
        b'rQ5keqC0/VZuXn4uwy8I1CLB2Tg4FS1F5yEP2qlTKipKRhWj3iavrrbyZ69wc1EZFHKh0K1Kjloron/+/ffftdYw91KTTdEavIcW1k6SSRAvOOUMDSOZfjKkjZ55EdDA'
        b'PJhKUBW04akXpsFmHlSjfFwLOQqfaAXnFO6o/slzD3VCPSXmOhiYMGL2LYE+VDdvK66DTD/UsMvqj2cfKkOHhemHzirY9DkWAi1k+sEBdGLE/MuAPvrFVlL2xfF+CRqy'
        b'rU5YqaPD5o6a4NQIxkHtMTNQYSD7xjPc/mHGQSfQWXPo3UOdYvbv2zeCcYJR77T1S2krzmNYKy3TdmuAnjNHL/7kLBB7a4LlO3sWc0Iy5y0od+EIhkmAFgN03oLW77pr'
        b'zIj6wxymQZobrerESraaxiv2W040lHJR4g/v8Yp8vOZmG1fEFL0UO9ZWLyPmiP2JaUVLrs45+savVjf8kVWMa6p68rP1urrXUntb+XIXP7sXgw/d0Tx+tL3upmjdt3qW'
        b'OlLjVH0L/8xVgdemP//17OKXnnO8tfj3736J9sqNy37uqmWZ7S6TA+rh2YMT9bXl1vcki1/UvD2l6sSUwlIkOiYx3Ine8Q29IKniqtLrGxN8OK3xeyf8eiDp4OedPu1T'
        b'mqMiLS6t05MHr3fvv6uXd8pNPW3Gnuu/VEW4295w1d7f8y8NRaFLfkrWl6/Ka774uCh0+zdXy6ZYtyU9WPTFzBg7y8y2mjjLsPNtdtIVZkHPO36xYPCu9UmXdrti3cGT'
        b'bu2ua0/aOd4pyyisKfWzufTxpr6Z1rYye/0DsV8OlG73T/ho/K3b5Wusz10Nf37Q6AocuDvptzNW8z96Y93GDP3ahvxjDiXNOZZNnfOOL/pwrZeSXUuRr+fNN375yNbt'
        b'Fop+Rx75g6LbtOZO3j8nfn4pd+9d87g2O+21336QuDm/Uu1eyA/uG72cf30+JmWq5+kM4x+29a4wdDwfdENx0mXyrYBnJ87/pFf5nTOhlzV951b0fvrmxJBO48seA3MT'
        b'EqvV27iLH895f+nzW9/xWqc3/sDgZrNrfr4X/vmjg817zq+6l5y5VTV1a2bnpJfe+AdmxuhvxTMNAidu//Z6w72Xn33v8q6fXNH9NSdVf33Z4dOqTxaONXmpN+x136v7'
        b'd2594bMVdy47vWzvtOWHd7+b/WzGZ1FTvBZ+pzyAL3xzI8Ap+fp39y1vRF1q2/bSt4dWhd25rL3L9oLs69/2/bzkyrWLNpc+Ud6z5tfAeU5vhv5T28JT0/3doC67n4N/'
        b'ls7/9LvKT3ZWHlfXPHamxrz4k51ei0y6b/VXBL+ldUHnnrbamqgzbe+1hQZYXRtb+OW/+c7ntH92f0O2lJ27ntZDRyysPaAeFfGYy8+L5JJZzKBdMhcvRjkkbi9qJlsA'
        b'3hsgm+ekqB+zvMZ8esIaFoKqLFzdF+5Vwe9mihZCzgR2BJqpDN3MQYJ5Rzia8lY6cIndLEZntFDOLObfrByoBXn8FNS8jFmyTmkvJ6m9ZnkRwOw+KB7Hm6PLkJdEQA3T'
        b'UdEq/CIxrrtboywvN4JJQJmzXCzNKeDXHJ1S4QKwnNQIJzczV48ZnBx1OY929hBHoLQUehprCxf2kcNSyLNS5pS3oGxUwU8NS2HWxPaVenIPVOpl5WpJzvylqINEHm5d'
        b'zgzcBUuBhJCGApQ7ytVEsgWTK4seFK8YIyG+66jb4REM7pyltHMbUTEUKWaZo6ax5KxYOChGR6CWdiABytBBdlZMT4r3QroIjqE0lSTBfTVrvIUrasQLvyRChA6vgQzU'
        b'ik6ywTszx55YOUadJU+ActQPeZKEUA964BtjgvKJDVTNgkiSHF5n++Yyk8MB6CUxMVGe+yw3D7kVOfv1FCqZBseUFhhwlAZroR7yFZDnGmhPhkSu5WkFHXKeM14pQefc'
        b'99ET6flQpwXtZqjOFY6oCfc1V/DQMx0uUDOf7TJ0Eo+pZwKqtbL0GNGSia0EzqlANzOV5Zuh0wpojht97g11dmysTkG1Lcqxmepl7eZh6eoh4rQixfO80RFq91CHXqhU'
        b'OEMaPfMXzvs1HcQq6ABqpe8bBRtSo1CuHHJUOGU1dIbnNSAPFVJCrYTznILaZsTbRFA5NQWqNtIxmAqVk4QQs9TKvR91TSTOsbTOACy9nxYCp1JzrY86qsQ74BF61269'
        b'I7U4UiO4EpSJUK8IU/3ABDotl02BHKm1nBo06kXjFqFTqFOHjg0xBDtTMzaWrUseNWWLoUQ5ltljKtElyCPm5HlwQJljQV032dK2Z2yEC9QIzUzQeD6Wi7bg3nSwGZht'
        b'6kOsjsR6LYaTIih2wnrD8RX01T378ZzG33TEgnStHfMjCcqpDQdY9NlzRlBOvTZ8ZnMiEi95NyYhxXEcwsxcNuRURbwYelGPGy/CnzHAsoNlwinUQAz/pmslHIm6u2gi'
        b's2u1oSoSKt1r2PA/YZqE00VNYshxmcmMImkoQ0TBJxNWMbOkKirjUdaMOcyjpQzPmlziWeYofwKao3lhIv20jdrQicUTwVWiUwQN0IXnxKFZLGR8FaRb4U87AfXDkq8y'
        b'pxUqXqGLjiYRKQ+/fQKrCDk7tkOHZsJDqZwg+2dBvouHlSwRr4uczwpVLVTPGAiqUEOKwkIdDmNWydohE3Eqe/nZ0UvoEG7aAM0Ki0RLKGQcrxLG26GW7eyb8gLhNP5k'
        b'V3QQHSAmQS+a31KJ04d6PKINqJ1WIZu0U4rrnRcl1IDq+YUGUM88wDqTcLM5NtBFPHhQHmZUFU7LU7wEVUxgLNSNSqUKzKCoAuWQ2EoXRTqo2JMu/OsmLJfKiFf8UU5E'
        b'gonqQikzEZ9GBejYCHMd6oIGIZyoKpxlUKAMV1+FpyhwEnGiIhHHD5kw7jmEMlaT6LdwVo7lKj3RVFs4Tb9210SisazX9sKdccWTlC4Rs1wgT4ynYI3S3PkL6HqboAxp'
        b'Ck+Z4FInVyPBznUmiddA+jYWAbXCGXoUMpH9ROKVwKGe8UuYCbHNEBUrGInEKF0kQQO7Z09hrNUPReiARQqUuFnJrcw98cqiHSEOQoXLkszI7Sass9fgcXjYMQKByiK+'
        b'DLItSnuwTHoSNaPiJILpRyf2wVHCHyhN9XEW8ZqDdY4FqEnZkxdcZXRQNSocgQLC2lUvHEQD6ADbgTJR+gYpuc3YGdUpE8N0rxjvfgPoGOUvywBzCzzhtNEpmQfe4VSh'
        b'j0cFTug8cxdr8kYnib0Rc23maJujRBevM+Uyzf/eHvE/MhE+KfREB8f9JwPgfi5MXaTDE9SQsshIpEHQQzy1ahBkETWqKVPjmjKvSv/Swk9piYxFM0RmIl1eh15TxdeI'
        b'BUQH35mArxiIDHiCQDLAZWJENMa1KVOryKgrIvJPi75JMEusJmIG3K0/8kjw0SgYSswA10vsRn2jMUka/9VIiFl1D2sfpqYrceEnEND/YONL5XpmjLTyPfk7/mMEjPA/'
        b'FQGjUXUoAsboZobDX9gOWSbo0b6lSViEtYk5Oau0tnGwH4ry86RoGH+2g35P72DLUAfvTyQ9EQ66TaJCR7X5Hxs7RBsbVA0IYdaPp7TYPtyiKQWxU+R2uAl9kYRi+Evt'
        b'RrB2NQOGT/YDop7WeNdw4zOWmiTHRiUkhz0hXsNf6QEj86BGwNCZ79M70DPcAXPy9Yok/Pn03Hj4yPjvdIKRIfET7qlj3T/ctrVPHIkrFRseRyNemAQFxyUnjQpT9bfa'
        b'd3p6+5dH89qIsEl/g+KJi5/eGBpubMLDxpxdl/21toQ4N0uf3tazw21ZkLZigx6G/RoKlsKiRfydSZUY+vTGXxhu3Mz3CUGxhjrwd5hanQabCCChH57SgZdGDyuNGMGm'
        b'9d8gNV5CaJtJcU9p8ZXhFscLsUX+RnvDS0dwUDQxZgXExYfFPqXR14cbnUcaJU8zG0v0SOPso6Fo/hbdtYb7FBIdpwh7SqfeHN0p8vjf7tQoGO5/GwRVxD1qSRJ7Rm37'
        b'2UlJQYTk+K9eJfFMWawx1SyR91dds/H4Ux1lLKRhmZ3mF+6HkyM1ocVw9A9CmWoPuVMRCM5/lKb2cxG79R7Z9aPDYgMC/nwgU9LgO4T2xJfmPwocqdyFUeFMn9j4/2Qc'
        b'Dv3ncZB4+kYZy+LECnL5lwN35UG+pzXCP77CcRKZyPxt/4ds9jidT3F/jc5bH5OuguPiov8KoUmLg3+B0Oc1nibbsdaHKU16QWzqRO1iNvWHAWCHgoYxu7rosOawTZ3P'
        b'VMJjIMZjwNMxENMx4PeJnzQGxMqjgf+3HzUGkz3pyf92D9Q/ysxTPM1Zn5ozPxHTs3ydF1cFRpu6OQn5NesgdZlCK1GNPH5WhHp2WatAWTLx5MJKfhfJEwq5Fix6Awl4'
        b'kivHf3iSOCjeq72t/HlnVMttWaKCzqBKQ2oAVRjAgNyNWHRQ/sMzMiXOPETJcRm6QLJNUaPr+vE7H5qplqwONETlzL7aCZemD/t+M8fvpLXomAczRUIjdMwghzz0PEpi'
        b'JYI+SMV63XFUzcxc2ZqogGbrpeDwqjhIC0DHmCmrDzWHWzBtFXJF6NxGorGGoVoXX/qq+Uo/8qEyK1cJp6bCo+6VKN89gd5a5o26mMu2RCJagtLRKVSLzlIrjNNecp7r'
        b'ainDWqSaI78T5aBzcCqC3tuGLuiyFGwEAgbFEkztbDjOCF/Po8uQE+dh5Ul1S+XNvL7BFhoKXscczsgh35UEa3SHHEpuFobCYqESqreDPNsVo/hNOsRvyx/y22huEw0H'
        b'phviNHXGaWsx8zyd20hnVR/jNhtPylO1uP2kcZghlwRG52mvZZh/G1S6UeEJLdD0EL6EFe8syp+bUWG4wnUsan7o7q0aQV/TQDl+D4cHjw0c8ReHuUkou3io2SjcoQ4d'
        b'Fw4bUyZPo9bObRZGCvdZi1Zi9lUVTYImdJhFEMiEE6iKAE30IU2Zo/me+iCHJVIuH08oj++UjwDaQL0LHRcbdMAacuR2yx4ipKBMiTKQObTBcbmAkFo8dxgj1aBKPQ8o'
        b'LFs5TotswKbEO5wz1RTLlCjbbkf1KH3o1bWoY+jdIKhmRuCTysR1Oh8aVzxEK8EhUxpsAFrcdB5BSaFz6Iw4GKXtYV97dpLn1LEMgDWU9awBDdAszkpWShYUb2buYS2z'
        b'cvOAiz4ibgpKV3KEhlBGjxYX6JNTqJMj1AyhnVajYtazI2jAS3CeF3ELFiir8uNQEWQwo2vLSpRuMSLLEXPA10SdQz74+6CVPXkEFRGszCw8JPQ4mSwhKBuOGI7HzD9j'
        b'rdI2lL45mSzIK9BFXFvOYzAE1I5aRrr4e6I0FTg6eROzd14ca6qIR3k7h1aUQKjbTL8/GC9NPajD/pElBR1DR/EMJivWNEeU9+iKtQmdFRYtdGE+NDA6pUIXFFGcVLP1'
        b'0PKDGlers/mMCS6S4wu9w2iXeVBHb7lCbgLkWMFR3WFkx3woZ2nHV0AZvsWWAHQeisgyoGdFv8mZwHLx8qGiN4whlXvQO2vwR0EnCfWE3xLN47BY07hPiBhwEAYsPKAU'
        b'uklyLUmQCNJ04TTt/y4o9ILCZMxlLlaWNO/ncT4Fr6ctyeTQzHX7DgECMQSAGA/nBAzEQiEXOx7AfD3hqVVQLMCSZqCDyfTILw33qvmxhasFCocXL8iLwZsLW/4Wb0A5'
        b'0LYdOpwlnAjOc1A7Zzb9OihF6VGBYxTQqkxs4xw66gln6GR336DAFOI4yzVwiLPEw9pEF6HbdupcQ8osvHAGupsk72eRJtAuTLMoIgcERseY8+xihEKTa1gwh8akWMxZ'
        b'sIvyParcCxqYSQMDowttJaMDcFDJhPxPwc3cZq29ohRRvEYo54+XzAQ+dEjCZtKHkIhctP0Rufq+mlNEWGzYzvjERWFqQlQICZe8gYyYCspUPHIwTjBXJP6tpasVysZ/'
        b'lIyKu4Ga4QIUiaEdFenKUaG9TvAcvDDW7UJ1+kortnOodI0+3rQLxSzyb4VjOHGuwMxSZGU9WeRKsUdua1Zb+bs8YYtB7by6iIMKqNcIhBIf5tKU5QJdeGGWWUH2CFuQ'
        b'EbRCr58ENXihU9TAH7hIwpWqGJC9wH2cg82Qr0BiNDnbxSM9cdPQQAfiVZqMNP69Bl2IHDHSXuhSVIuFsVjxASbRNgcuzLcvduxSvYoTH3TuGNi356vQiplZRfNeEat6'
        b'rbD+TeTiUp192nD66w7ZRrWtr7kfWpcds2Tj6nM1p51TVqmrX0rNNg9INetWvGOrJuvf80rPrUU3X/lXln3bZ5uOTP/pQdzLwRPX/XP2kc0918ZBl94GF/nG560XKdnJ'
        b'bT8e9N80aLrgK9OxYB9mYVohM7Br+YdyRHzSshc/fvX1/MRPLUN/fS5OZlrqeaHn8ytHrx40urnvgdfdZ56JvWbd99aNX7+y/jzJZ+bWXWanv0y8oq7344zXz75yXqPY'
        b'5eXka6ZXr70+x/yG8XtxUWt7Pp6W0jJt7/nllp/AkrAzW9/MVFyf+YxxzokXNceHv9XiqczHhxrfzpxQ/Jvb/cxa1cvHH6Rl7twQ8+1Ku2PH0rVr9rx+ZZrc7TXXyK1J'
        b'KT0159pLZrZvtFnoGBdWHvPBCw+SPeTtFz4P0XEeG27zQOW73J+KSzKD5LtKD35TOrHaab10/bTguTa3pGZx/rd8tW7mxrXkbF04u3X+szdd92b0L90qfsvIcvU7MpRz'
        b'qFbtI9N7478/+r5pnbx6n/OH0zpdb9vdeFkndkzl9H7nnfm9zWjCjQcm79e84LTi7c79kVutTO6eEU9syfooaMuNsdtK7ed/XVP//c2VVyry/V/sTL/30ZvprkYXd9xw'
        b'sVR8WWVwv+tFv/Lu7Lmb+n6O2Rll+elnaobvp3dZ1+m+vE3zw7OXXCI232nTm/nTtxOf++aTtR1vvaozddLXL93I/PL7yEXbfR0/bXvreWuQ+mXU//D8wstf2/odt/j8'
        b'wyz3c1p2+XeeST4+XzLQd/PFvuhNis5Z3pOd/rk/9V8/b/nqan599Y75X8Sk3Mo4seH34oR7Dec6Pvql+9dXDjWmu99/btd967C1re8WxfQ8MK79IshhcFzs9e4xER8X'
        b'3Kn+1eWezvr376z5vL4ehQxWLew2yb3XtC2z8uMFqx3ufO+jtO4377d8401s9ou9TIK/5L7cf723qbT+ckr97VmGETO/Ni6643g3/wGvt2vO9V+zZI7UtBOLqhzwkqln'
        b'NAudl9BFvj9mK7NU50ERypASTKKaGRa6sXw5BsudJ1CtGJXLUQ21RC2auR6qPKTmMiyaENut6kTen0f5NJOavsHmcbZDSGQONW1nAQjUUdVeaE/C0nDRQxAyyoIShsI6'
        b'pwTHLFy94OCQ/RwyoEkIL9FgQMLRzIIzJiOQtjPRAQbWO2KuileSvXB4pFRVCZXUZDMxZB79lAT3WTJlThNyx0G6eAbKRC3MeHvEdiUcQtVPhCGTPKDnbAXILNRAFzHR'
        b'hk4fst1uRxdZ6lLUsnbYeIvaZARCDCdXsYAMrdA5TWqG5e+j7hKO9xUtQo3oAnP0qEpCJyBz3BCmnkP948cwOFs2KvCVMsx7BDQ+TDjb7kYrNUStaxXWCigfASLX2kdf'
        b'jViMuhXuZFTIsnrZUa7EqWvw6DSqC6LmJ9HEKTQSgiWx9EGbMmrg7VEJKmLxHZaO8Q4RAlQIwSlkHLVMhqI0aGegd9JZ1OosZJotEcxacBkOoBqCmfckSTsjGGY+bgqz'
        b'a9ai7CWYwNmoGZWQdRzvkI4i1Ir6UT8bwsuoyBoyNgzB9RlUHx20oEOYgIezGjLCFJDt6goX5TynksCbo8NQwKzjbSa47fQ5AlSaAaXnwgCr+WDsEmLATMCynCQKc4D6'
        b'Wh4LuJkiejd8PSqVorp4igX2h34lVCaCZji7kZLZC8+DKvKyLZxh1k+S5pkZYrNRapjUbRzke1goY22iV4QKoGQS/dpIvEtmE+cENWu5tToRoQztHFGnZC5qj2ATrHEs'
        b'XAzZJOAdh1HUeihPjFtMsxQeQnmzPMY/AeksxpOx1JHZQk+hw2qmpsMAYQEdDKVutJdhRh7Dzir+LhTYiPuWxmDipbtR1WPRRBJRBQ/9SxYxc+YxVIq/uF1AaaNa+cNM'
        b'refhHHUSWDB+kTTZCaVrqvE0cSoBrdNR2ZdiRNDv1LsEtaELSitEkIfOajPy9SyAo1IzTagZAWq97EVNwinTocEuUAjoQUTTam86GjPVUK1UwJvaoHYKWk9jSZQ1oRIV'
        b'wnl0SfoQPEqQsJCawiZh6pR9Umss1F9+CIS1W8J8GXqnpaDWbY9hYcWQqQ19zAjehDpgQOrmgWpm4FVLJjJGtSzSZIwTFD2OWp2mQkCrqCGJLRxHUd14glrFLWOR+yxB'
        b'rW4SEgevgTrM+e3oFPHaxGyIv1lFzpvqTaXtLg2eC+2Wkdsegmhd0CnG8RkmKGfYlwsd2UuD3ey1oUeOS+AMVEGOpSdeuuHIDnQMPyLFUxmaoIqljdaEU+gofSJXBpmm'
        b'WCyX4CeaeKhSm8lyXu6CYqL3rbQm4SzOiFbzcILyW9RUdNnCyxKyyWrp6ClX4aQk+szFaAfa4xh0EC5KzbFWcB4OiImL6+yZ2+gI+aHLBorRvj7opKVYxRV1Um5H3a6Y'
        b'A3KG3dr0UOZDzzYjKJAZ/H9G6T1qmv3vo2sOqhO4VACFLVBh/l9EtP/Px4z7OT2Gg5VQXCz5qSWaQU3iliJzkTE1kRPUKUHH8iJm1GYoVF5ZgzcTGYjMeF2RlsiQp4Zx'
        b'Ibcn+63BT6CAQWJkJ89MwH9NEOnwJKsnQ8vqiIzEE6iRXB0/ZyIywv9ITTq0Nord5cmx5G7Zo6Zm8rUB1k7UOKVYZP3w65mKIhlUS9oZGpYUFBWtGFQJSNoZHKQIG3Fe'
        b'+jeyX2C15x1iNn972Hb+Fv5LTBQdAgb9EyesqdzvLMynOv2ZLCcDhedk0x9oRnmmf6QcjVSMuDlwQtvSFKplYqpujFefJ/cQubFwzTRuEjocQE/cUKkLqpQLTpO4kiav'
        b'oTAOE1CVBGsv5ZBHH4SLUEOcP4e1M+ppOaBPapy8QALF0LwN6z3M03MyapJvRU0jG+RRDgt52OWOeoYbPK/zSHvbgyn0JURrnQVx7Go0c/GwdvVYE0+oQXO1kJgXItyZ'
        b'y1ygvuq0rfpUPZcp5PKHbvroApRQV/0VE5NJ0AxUuAra5JBnhaUgX1qTrcMaF6Fz86cpj1uFxYs86pY/DW+++SPTxbCGzR4e56KTrtwmVKaqjVqgh2qJLpjsmY8QZj8c'
        b'HibMfsiiwbStphkpHqnNTwhHTb6LSDzh+1WhYS86C9XWVLHcFUE9x22+dg2M9rZz5qIuL5KLFG14Nof82BTmszDu6hJD9dP7vknxjH7+l61XOzxfWvvLA/XMMcl3MnV0'
        b'dQt0TF+SgZLSO18c/aQ/8NDL3rtC6kpXrwrPyNeo+EXzN7VMke237zuKdXN+u7+r8l7PrYEFJcHXLMqyf6rTC5n1rMK1TA8u2j840Xa2ZudK2Tvujm4ucz57MaTnbsHN'
        b'Pot/ir5fnmhSsWxttvpXPs99aPumw/RP55Zd6E2yr+lJunfeZkulnZvX21P+tXPpQn7tR1MDF81f9J7Wq9t3GmgaBEwf+C3cvOGLV+eVcls0TTT1+W2hytLG3qijP7/v'
        b'bzXdW2X+82afBqwce+KtMv9r/pOmuxlcjLZKvWj5od+2utecGzduj7zbEVM5Z+eZ3fHJnRO9XzR4tSNn0vul3xVOn9XYVmQLzh+s7/nxrZr1ai7vTPmtI/x2Zu6y7ze/'
        b'U1872GaOlZA65a7BTWELV1xurLW4XH7DaUdiQV/PKZVd9rX9DprXyzbt/+Zcct+D7bf1jRO/WXd4cXpza5/LF1N/SS+cuWDF5pzcY04fvnHpun2B8l2Rjddm35IrUWm7'
        b'Ds3y/Vw9KbVyVvilzH84KSmu3Xlxa/CdwmdrDQIuzvupUdXBqHZe7dTjc+o1em17vOelLwhrO7P3g6MDIavueq0cs9XrcNEHv3zpluVrdOHBvP6tm9cdM4yam7/rrbTQ'
        b'T/595ie3Sz9v3vWgOc2ivck4dttH73vf+YdD8ubY4N2tqi0b57rNNI4smJN89Ypv9rQlXfGJY39BL1qdvmhbcMNGPq/H561vexZcGN9ZZ255tqPT6XWr5Di38Nt7J0w+'
        b'F3PlYJ/v/BztF1rCfi/u6j3yzVgbqwV1ZhXX9aJD39310beFq0K/ORHS/YZjZsme+b7LfjSBjxYYX/o0auZXt5uqT6g0Kxxfm3Q9odA+SdvB81/nHV5RGYiYujv8w+8y'
        b'W/7V9bLOJZOVKgfHTJJMLfyh/N9fBBh1arfpectsksgsgB50mQSM+WOXSOj1lTGXSDc7IZ6PKnSPcsPMxotHE5YNmR6zVmUfOWAW1Mip6AzqDw6h4sK+rT4jnP+o5x9q'
        b'18dSTzjLNu604qG39ILJkEFEIRZ4sFjb/JFI37iDJ4b9Q1E6HGNRdopXOzJRm6waQ+I2EbYd4TSVZdSmo9NyL1SKSlik86WoK4G5Hp52gw4s3YftsWLCfZBxEjkwDoCT'
        b'6NiQrEI+GjqwJpUB1STQERyToA5U7EMJ45ykhirnSLHWkS98oHQsCQDXhHVkInZOgePa0vmQLYfcBJmIU9ohgnL91Uz3O4kOoVQSwo24PfpvRT27sUxIaLYaeqFgF5b7'
        b'WRQ+4oCqvoNHF3aFUdFvEmqA1BGOkXB4y26sVTH9DepMUIHUGjWgNDyE/FrRgl2omAXJq4dKzyGZGga2o/PG+lQWdESVu9nYMv9Z1IMyqA/tTvwmFdWPjVlH4wJy1KCC'
        b'R74WHTBgoeBnoiaNUSqE/SaiRGANQs+FaYXHNaZC+17UNewxT1SQTgWT+Wo98FL7WHAVCVZRenRhwIp+0jwjx1HC8XoD0/DJQypYo4M0HrUJOgFRCLYhFqONeihnKUgm'
        b'COKRKkZ1IjgLheiIZgjt14Z9HFH484jFQ4w6RGM2Yk38HMqjKgFWCFGG1NojkT2RhBseoydGZfZb8ZZfxvSubDifRBRH5nOsqsmjDCgMjYU6plQUoc7VmE4l0P5oOERD'
        b'yKLzUBe6NzwFNwGnUZFcAE54QjrTouuhNBmdnTekzg4rs2fQYapOaE4l0YZStYYUWqbNWiPmRG4Fx1E51mKG9NVivGcWoMb57ITlAhZmWuVQHDgkD5CglpbQyFyID8+B'
        b'ck2C1XwC7mRyEvPVDoESyJGz6ewlwivGKUjFneuljS9HFdA10nH2tBqeKGd16Wip7t75aHRQiV3SFihHJ6mvsTIezoqhGekN6ZTZ6HwzDJNMgQYhaJgpnlKVxPGXSRaq'
        b'83gjcfBuNzqp8ZysJv0fojMTe9C5HfhLJxtKoB414tWMjl0lpn85arVgmjPmARKbTd2dR0dR5k5aWRTqWI6rwmxynkg9KGukudlmg/JYdBydSKKIvEbUverJi+2wc/F8'
        b'KPEkoULpeiaN3DvqBF4FLqEBTmuD2BZOz6LESIQW1CB/vF1zyFRaH4E6PJjjiTPmISouemE10Jo0qIJO6nBaYrFpSgzj4Vx01AN/XippTEDb8FOxyJkp0/3/qFj9rwIU'
        b'jQxApDnkMdP951SsGKLmqFJPY/w/r8MbYCXHACtCevgfVoSwOmRI8xsQFUgXawa6vCpVwIzExolYVcIlPfEE6mFsSPMf8MSPmCf/0yBDuE4NUuZVxVpiDerprIxVMuKt'
        b'rEvqVGJZE3RFEp61qCpW5R/33aUKlaA8MS+Sd/6X3seC8mQ+iowf/AX3lHNPdz2m3Sc+YIZPCtIzqB9AQieEJDEdMYDESSDpl2mwHhq7h0bsicE/BlUER9xBjZGesYPS'
        b'EV6qiRPI0/PIe5vJD0fygyQaHFQbdvsbVBG88QY1RrrJDWqOclCj7lDUVYcShNFf///u+OGhg1I3bn4uGY9gskhqSXgJbymaEUxD/oj+pz95DbGGmGVqaLGFY48qvyJu'
        b'PJCzwPOSsN0rn+zaRShP49twwzmnVYbdvPinunmFj3T6IPuBFfeom5e3Z7IX/jtlHzpsbzPbbo6tgz26iFqSkhK3JyQr4CIJBAstWFBrgy5y4g7t2qoa6lpqmlJ0BCuH'
        b'uVAIx3xWQwGU+CvhvQB6pNIEqKR+E+jsgljCbr4yW84WWtbSi/OgZL09bt1wlx1nB1USagR2QGdD7fEyA2VYL+PsHaAoeQwhA8pcba+MNVn/2dxsLGPU0RqgO8rbHlNq'
        b'pYYDfrFnDn10H6bhAXs8ttuT5nBzUIkSrXcGVGrYi8mS3TqXm0sSULCO9aNeM3sVjrNMmMfNG7OWPku8eKAIteM/V89y5BxXbWNeCHivhSosGnPcKiibz82HGqwdkyZX'
        b'hioIGVHWRmfOGR1GhRQrjbfxPFRGrMEoDUqWccsgbwOtP4TboFAmj0P+cm459MBFenkPVNgqRCSyH6pfwa1AJw1oFxVYLG5U4O9xXreSW6mlzrpYlox6FGJCWahexa3a'
        b'a8CaPAfpKgoVYm6FbhestWPVm/YQWndGAPmgRFTsyrlqmtKrWLYwIuYUzlHHjXNDJ2OpM85WVILqoJ2nEW175ZzcU4O12ZiADkM77nnSZHfOHZ3ZT9uciYlVRYJScpao'
        b'3IPzQE1wlo3OOVsZtOOOL0nw5Dwd/VglvXCZ4PcIX8d4cV4mNrQSaLcjgc5VqAtY4WosoJdr0EpiFkARsbpbT1/DrYkU6I1OLForxd323eDNeeP3zrBAH62oZZyUp4Q9'
        b'5MP5+MAR2mQoagyTEhN0ur4v54ulymPs8Vw8QNVS3G+nzX6cHxZY8uh1PSjTkioRWqIaf84fslAf7UlCFKqR4m5DkfJabq13PCN4J1QpSXG3Sdawddw6dAl10UZRni85'
        b'zcJ/rdiznluvD6fp5bFOqBXlSEjkzMUbuA2bEesLOm5hjXJI1/NQ9kZuox4qYf5PaAAVQpESCdJRZM1Zyx1Yq5fgCBqgqVXCsHzLzYKBHcna5HmoVicOSjrzTTnTxNX0'
        b'4U34Q0qhCFceBKcsOAsso7eyoaiaJPYh/NZuM52bjqmXzfpSqoO5p4gMRTfk23A25lrsev0iLH8TBw1o22HJWe6ES4yO9RtEPkokLgm6MAPPsx7UL7Okx2DrUPcK6p2Q'
        b'YzEL6whp6hbEqUXMjYUKMfRKIZ26puD3uqCa3Kq3x0/CETE6kIifacbPYNEpmdpR+pWgmFZ1AOpJZcIzpJ7dYno85jApGfV74tfpbRGnNx3fw+tXPktHdwavS2dpDaV4'
        b'paIdEuviGnLwU8pwknqAxRjCBVxBtJNwn+f0xpJKzk+lXl7LzWWkAjXShHBbhG/jVaCE+iLpT0JtyXiqsy9WQWdwD1EPqaAZGlkojgpUOJ8SwUJlKufgSd9fHMdcH3tM'
        b'YsmLSRGUWDniKQINpikxN7Fs1DdzH2YU9vEmvPD5UA6nmANkuTfWBHIYCadyi1Au+7odY2nvIA0PZzNW/88TGpFKzjix73ODC4zIjQtCaOdriDMdoYFKsPAF+lBF21Ax'
        b'RORddEJZeECX0WBLAqWyDV5eWQcsZkmoETKHjTf5DsgwoOONjkPTBHLDaxX+EBKdBfUTStWSZ0pd6DPW0B9J6FQIp4efcRqqp9yDftAyVDKZDai9QNJggSSo3JZ2x3G6'
        b'JhsM0lVUZDBriP0IWRZCF6N7qgGUUHochLZErAZdYvf3Qi9jz3xHYsfB//rNGO3JY4wsY/AyTPX75egYvhcO/UNPOAm8cUCVsd8xOEyCpmNez9ET2OPs8EenWTP6V2KV'
        b'qBLOowoLRjkLFVPhm1GJG2OCOnTcHrNTK7vtPMwFZugw/RpUtjpy6V5KdsyJbayrx/ADgXOFNuI9UQfU0X7SB5yGiNaFMtlpeTOm9gVhHMmvEKik00EgHKpBlVSKweph'
        b'3bRhAsMRTXRIeI4SxwWvm/QwBdpC2JQ9mIg353RGmD5D+kHo4ngSeh36hSmH0oamflg4c0rrx8pZFZtwYg6lu+vNJX3oHcOYutFPgt90Nqcji85STmKf02xMn0AVCYgs'
        b'CfXUt4k948QWBwtP5pJ8xHEbrkMVDs5iE0OY9r57WBO50OyO7+91EYaWtUEoMTFYSEyVrY4LbMkwEQmLRiNzUHTcAZh7LPZA9ixhOgQLrNGAdwpCguX+eMvLsZjqzJgY'
        b'DgwxegIeEBqfCUpmo2Oons1sSKMfQKoImUCbcEHtnvjeuEm0+7QFYab0QRbzEsWiSy1+RG3OEGM5C2SKhRZK5mUz3IbWrWV4xJrZB1qiepmI9kEfLi2Frh1ymiSTJNhT'
        b'Rc0kGG41qr1FRcqjiUuou92H8TwnSdmMd5tA98Txgg/ee9s0OcP4FGXimDdn6kx20chQldNZd03MBQa6dy91ZhctE3W5aZFkrQxMSXWbwi7uxZK6qsSI55YEathKFOyi'
        b'NEibM5IsVeFsAi23bVjLLoqDlTkNl9MqnEmgRmS88PpHtjqcidmnKlx8oOWSqEnsYslydU7PbLIS8Sr80mMvu3hMRZ8zMxsrwQ1t2mSrxS62aRhwlvF7SJ0pP2Ktynfl'
        b'rbIT5L8XF9+yp//dXUylEiNdVE3WF26+RxwXJ8NrPt0ey1DnSgsVcsBybie3Ew7CQeZPTKdrpscUTPOJSx4de/cZo/wUiYxOhXXCbxGCpyJLZfUwhZWAwBhUiooNDds5'
        b'lMFKg/ujDFba6g8zWJGspqgPVUCTjrGFpyfLAwO5Hu5ecOxpacHwYlEmXToOdTGiJqzjWlQ3KuMh3f3Nmq2cTJ1e/kwN80T0PiXirLlCYysja/MMzBO+/xIRnlhpHcEu'
        b'Jq7EPKFXKSHOmoEG3uzivxMwTyx/FtMj0ClMKYVdlJlhnjDxUcFDZZmhJWRgi5mGeSKpmvCEe/IaoaGf4lQ4jdlFNH3Y9KWr2MXnzMdwJikLlTFPuBvExrKL+kqYJ2bj'
        b'GYx54mqA0NBLcj3ObNrbyoQnCqzdWOCkTtVxnOXyW8ok0VnNlG1YzfddSW8EmeNuLcHSOu7WFe297OktVpgrzW5ISNLU3Gh/dlFvHX4yPpb61h+Vb2cXE7QlnKrG7yLi'
        b'ZHnLcAK7mCrBT66zJZ+q4aCxADfm6RmlOl0sVpCQdl/7vr3Quy927Bqdij3v/DT4ZUT5j4P5YNGvq3rUZH2Byadj3HcedpFZmk45N88ucuqKea6tz76/dWm0erW+w9nq'
        b'5Ska+vr6n4q9TdVvxq7OfmvAXvHKiROKcbdTT39icthJPX7NcjXjf50/nT3hdmQg7+GOVklFg5+fzpH9YJM3dl6Wz7w8+9Jn1pfDrk3/WHFl+vpgrZL48Xe7D1w4dVNz'
        b'+i//dPV1af0w57pv1tgL4pkJzl+Ytx7cNjnJ4NaWrVW5xzcumvHZNMe3132+psHd+q3X5zoZrq6fe7m0f/mpsWvrf9NKqFQsSlbN2RkZ11p05l29LQUJVeufqVunGakY'
        b'1LumKb0Tn3bMa1O0z9oO/XOzHyzU8+zIXjV+x7XiQ1+muTsOur5f/Y/Yhuhm91vpdS0vHbM+YV7i3dkXO/WHxrK6r653b9266cb3XVM7M7c9P3eW5em4X9XO9l8N1D5y'
        b'Fy3dn2W0ocY3b1zGtPX8wNWzfrd2f/7ctJ97r1ca3Sgsd/cpiYr95e0S5Xd60qZfq1mzKPzc1m8On3f4Kcfgl8n7+1YttBv7+o/Rk2ct+j505fbv7lg7tVqd/OZ+d9Ht'
        b'uaKvB6PnXP3INGi65fqMqH9pVVZ8Ps8+q/Y5Lz/fj2d45XeYPRhTHPeBzSIDD4v76fpj4+0tPzO+GByz4X0U/HbOO2qKGqvvPJbuuN7R4P9D2XveC6/nX7mW65exUO+3'
        b'/L2i7758pWtR/WcZH/e5Bz3r37Pt3vPZP0QqJirG3741P+EfMc8oHXj1fvXuf79+6aed2y7/XLlSXfz+/o3XlzjtC9dXDh14ZuuS8OyDLWU6Xtd+X/5ml92bZSuml/22'
        b'Lu+HlTXFXzRqNgbkmeZdfumeX8qeS0vPvb54+kvvv6QXItNibl8H0ClVckiMlwklbrpYKUUE1Vh2zKQnxXpKqAFyWLQKOeqVuIjwQnJyDjtl7/FE5XKschVgqeuIhdzK'
        b'XMRJ4aSY3w2t9CjbAjrgEMkZCBfxZJqPRRh1kS3UW7Nzbl1osMAvN7gpYSXTTRIqwmp8HvQyV6B0b6iUey02sHJ1tXSVcNLtPJycFsQ63KSLiuP40c53KEvIvROMVSCs'
        b'h+TPwp0x4CXJIrzsdaMMaiFRNoZUW5Jfi+RU4lG7yH+3kE4G9W1OIF53zOMOi4pZzOuuApWyQ/9qdZRr4bYBcin2RYnTUOZhwBgdotarKLxL0Jj6uDdoYIFknAidjVib'
        b'RLYTGxiYLDccyh28VDqPUm43HImlObycUNaoyE5noVQ28f/Wf+ePTz1V/uLh8qC6IiQoNiAqJigijJ4xXyI7359x49nPeUiEmBNP/qfOszgU6tQhR0s8gwalJ9EuiNuP'
        b'AY1YoUUD5JNoGMSBh8W80CUOP2I9/HsKjWBBwtPrUIchnjoCqdPfxIXITDjFZufTEvy8jshalHh9+FxTPCiOiokYcaT8J8lzY9jjhtTVRzxuSET1P+Vxk8o9bzji4JgK'
        b'/z4hoXhvRyUoZ8T+rsQZbJGoQpfFqLjBw0eOBGUwAuEoElBnfLj6cLxgyR/GC34MbaYh/D/64NHY88nHncSEh9vkw/k/iWWNeBTLyj/WlhJDtj2XgEUSs+8kREx1F8s4'
        b'Fqu0HtXOIkLwWjMBEmnm4urjQqanqxI3F9VC1R5lM1QgijrTWMMrCJo6JcTwy717A12CroSbFX4eeCU4Mjww1CzIPWhreHTwnUAGV45KVT78/nYZTxevBVjbuSgXguXY'
        b'RXLKTvw46IGDzCR/0RmlS3l07MkJuJuhAjqGsChPOMwelIZEhoVsC6ACIJ1HNn9+Hu3nzFhSiN2TA0iY7AAS7OGhp9mImoe4WhQ1gqf5Uax7a5h1b+K/9NWFNM1/knVT'
        b'ua+0RjIvSZK8BPKwapxD0qWjXAGm8ph3GKarOhxy8YB8ZZSNzqFqfzyqA4ZSqJgC/cxv6yzKXia3JGmbciUcnIY65Qm8+gQnCmYRoRNQYAGFnjwa0Of4MSJyrFdLGWa7'
        b'r9hyE0/TH7tryqaRJLRkX1gNuQvk7p6eJI2Yqhe6GM0rHNfSFx4oq/suEpkR2JLGv8K9OQVZ0yVXfHw04xOgWszx/rj2G/TRUGuJdQCnQ0XBa4FbuGhCVb0VShzusMlK'
        b'CadxzbBm50lOQQ7tBvbG+vgl/7hDzC06IFYSTW/NUBA8cuTi+5/xBCpaHSb99Rda62Vb5XnLaBWBGjdDIjn63IIi/8+UCIQ5f7JW4TQFOTPc8+vgZzfwuzMuqHGGz4cq'
        b'yJnhlz49Pn6a2zXj7//sizc/K1Fxy4CCUMjirDuxIt9fbF5nRrxAxraKr1e/SRdyig7Xqq29qv2i5Yt4vqiIdNfyds8103b7BuyvEs7gzDVl0WPopZTWCVcxI5lzdb7m'
        b'6nvopS3dpjmYXTZz6403j9WnvSsT7cl5Hf/+9OJvXHrC1/TaJwev5byOX/3s6AUuw16LafGZi1AB5LhSpJM9lqJRzrjFvBvk+VMZ+juFksYFMSWx+/OrIplgHRAgMfpA'
        b'RC9auu+bwkV5vhsnUZDsEY6pL6wo9PK8YaPx3FfVUUWLjDX2bwzUsg1+JnuZDfBagWmR0yVvRf4TFRzlp8Sl7ZRqoaXr4g39G55ztXjX9+2IX+++Gmv81tRyC2fve2+L'
        b'056PVN091+i5+oORvLX77EmFr6yxlRluMz+w4dO7tWtfT872qxUfLeg+/b3rLJPsiX7aW8e98NNuQ8NIXPrwBLfld6sXW2p600+nPOPaHPncpxNeO6ka/ULn9x5al64X'
        b'+u926A/b+6HntTuXypI2vOSweMK3fomfmjvueum4u7bcaPtzat7tH/5j9oq2D1dMvXawdW6ZssHN2zPfi+xRN4udc2+99bWbla0PPOcZ3fjlUv6czemT3jPY8K193Y6G'
        b'XW8v+fCdeKtXTKZ57y9+/zZn9k6Ba7NrRElK73qdV74skb8e0uMLswaPXra1i8u/suvUb5dcri1fsTEre9PN4s2x2m29L3tu3RzuPvfKg46r20x/n/dKfVL39A/7T6G5'
        b'aauei02fMFj4tW1s1J7sW7nrOizem1n51vL95v++/Il2+Yv7nJet2T9w7Jcf/OtjY940vJpTWL8/Ueq0duYbCv7rTxent5VeX7pdpsM8cepNPOUy4vOozEGVg3IEb65r'
        b'xISuS7t2ECmJIWpVsVSWZ8vHQQbLRueEyhYRtxMPS8i0w5PSVoQl1T5DKs5pwYExVCBzxetNjgp+9ww6ic7z+3S2sGx6tdAYp0javh0vxWc0tVC+tja0aSTgXRQqxVh/'
        b'rrFnPjlN8aiNyahWKFeJYzLqwdlMRD3mSY58PFADFzwJS5OHRKtQC9RTgXCTipmFmyAQwsFYZW9eDzrkLBbkwHiUxYRFkjNWxFFpERpQH/1m/zm8hZuVIBarSaEDVfCo'
        b'CC460nq3r16MX5VZEacNN+hQDuSnQq83QxntXDCEVkHtKIuiVaBjFpOYizSXk1ozXd23zMXCqxS18lDhiNLYV1ajihi5q4dA5s3QZ86H7YRKIbqck9bQPsehXBey0Wmz'
        b'PXCH2VQKAXaXKZN07c3KC/BXtkLmf2lr/zvOzaOE0If7Hl3QSv/K5jlTS4nmWqKCphYWLHXoZkqyKumITKioSIRGkhWJCJwaNDQaC65GniSipzIVMYmwSoRM4k/O47vU'
        b'o5w5PAj1E3E08fNh8VJpUBIflBQ5KAkNSgoaVIsISwpIikqKDvurAqc48Tap80vy44vh/Zu0o/eX9++vjUfu38QYBJXo7BSyf2P559CIPVyFM/CQ6PEoL4QXhDbJSBmQ'
        b'CDDU4C0KFw/HOOD/fDSNoQofjWiC929yMroUupZhFYsA0cnJJuZiXXRRrGsPBxagtqj+yTUSBVkV5vDRXwZ+HhgbcDvQPehOmDoNfjKxUOy7eAQWGBPwj7wMBjXJqIzm'
        b'LvO/wl2RiXeGx1vCRufL0W4qI+Uv/tFBJC/7/eVBbNQZOYjUNnAeWhMZvZgc1ghnhsdx+jIlXxXI/5+N42MRgsSPjaPYM+rL6hyeJpwweHkLGaPbgdHhwaEuQap0jCZn'
        b'tr4ndpPl/slRUvx3o7Qt8atHR+n200bp9uhRIi+v+8ujVD9qlKgf3mWUbmvhOTxKc1D3w0GCU0qB6BiqefIwEc+hw2SgRIcl4ZI/OVCj1C7xEwdK3ZPFBWg2lAjCN8pN'
        b'knBE9l7pQsXVU5aT+RQJt/PbgImRO42mTaEX61eKeTsxk7oLTDzYiayVCxd5lQS7iQ+avF0jeCjSjSmk+eCKD6BGQoJDHKocY8oi48iUlU+JqCAcvVp5MotiAvVQtdXH'
        b'Co5buLiKOWX84qn1vCh6XdSLqtZixQ78xHmnWZNy+zT5NRqSd379euqEJWfTLVR4Xecvj5anqareeSHL1Sxtw64dg9Er21csGrvsUyg8m+X2k9KWJLOiQU/V98d8v8Xo'
        b'1buvHL6el3Y6x2FSxap3T1/1Vzd+Sb/iiNozX9+6vc/+rei2npbsl4589OCLxGeCfhOXqhk1fNMkUxUSQcsTLKzMXLD0AAU8p4zKeCtjqKCCwIrl0D1CujFHBegoH4cK'
        b'4QRzJW+ALFRBTTUkcbaIUw1aBrlYzHD1olWbLIDTI47Aug3IKZjPMrbfd6N+XXSBSiCQNS1ZxCnv46cko0bWqe6pqFkI4kIOshQryVGWLRXGDNApkYWLpUsUOZGSzBWh'
        b'JuhaS7tr4I9qhBOyUiw+DeFSXVHjY3MRz5qnemsNapB1ND40PIDseHSCLvorEzSWnNBoCXAvQ7o964oSvx4xaf1IK5JHUFOPdZNP/Ia84zfUL1rFxr88dWt1H90ld+/d'
        b'wpZXF1e8V7rQ473JUAUDcEgCNXaoc9SCqCb8Vhg8klSuWFysUawSzofyeSJ6asM/jBYUrhoqDpUcUj0o2iAJUwpVClU+xIWqhKrm8RuUcVmNltVpWQWXpbSsQcuquKxJ'
        b'y1q0rIbL2rSsQ8vquDyGlnVpWYrLY2lZj5Y1cFmflg1oWROXx9GyIS1r4fJ4Wp5Ay9q4PJGWjWhZhyS+w181KdT4kOqGMWFK4VzYmINcvmjDGHyHnFCp4UVrcqgJvqsb'
        b'akqXpimDKh5BscQn8b7VqFRGJP+ZSQy7xZK7jU51hEVDsjQ/eZ0kcStpKCbqhUdJS7Y2teEVU/KHK6aYbm2S+wf/YwatUT18mEHrj/JVkSnBUmaRv0hmrCBWxerlK03C'
        b'o6KfkHxrmJsIE6s+tmqbeiaTQ64lWD26ZOEipNjxsiKZb7rQRYrqQo2QaWkt4laJVOY6wTka4yccHYBKaXyCD77lD9URAgDMV3W7ZrwvyZYtJEgOMVHVgIvoNFvA24wN'
        b'IMeKHCroQzkNo4NOTWAuGs1QjGqHMiCLONSBemkG5PGW9P5O1Ods4ebBAqVbiLgdqHDsTDGcnIiOMce9yzNRvtzOjefcd4igmcD8MvSocXaV6TSW3tseKnmS3jtfhXYm'
        b'Fvoc5fOWDgXVl8bxcCJkBz1EdUF96CBdWAn0NwdO67iTsPtwSuzsgZqFkEvLNshRowvuETqCskkN2lPF64Kd6F0jaCdoFaoY4TsuqqroIr/HEYQwZhdQiSVWqczxbZ5D'
        b'xXNVEck6C1VxrOqmXdAsT5o5OnV9LzpJN7VFSpjyOSy2/kI4zoI07ENt9JsCYcCN5WZH51EbiZkF3VDONsOSGaiDZDonkZdUUCqNi6WGUmmPFJDlLJej00J4q6HYVgHo'
        b'Mt1dy0yU/I+zkxXL2imzOebOl4Z6bWmkLBKrq90UL/yXZEN6ADRajYpZhQc0A5XSoFXoEuTSWr/Q51WviujGr/GWsTvb4x0gyw8TjobQ8pPQIFrroZuygDY6Yz8URAs1'
        b'bhHiaImDoX8d87zqM4T6oRBaMVIaRAsObKXi0hjos388ypUQ4gqKlMLxpniROZM0o3Y4LMdsQTbXi7Z0jLTgtHjzNpRBj5Qqxktm/5tn1FgsGcfOmW5ZSVLeFUjUZLOD'
        b'XVSaouT9I7sYfWXxfHbx31uV7HqEk8DBJJ6LsgzG0gjx0d4tLd1buMAbbHQydoQ921Zx771Pk7ONUgsr8597WetK6Xj1mefe/3ilLDBR/ZUXt041WaZc9uO9bdO+2jdh'
        b'z1d5ayu2GnzYsaRl7qyJH00yu3BmZdz89ycG6e/suzb90KRLZ72cY5955qfYWtd0B5Xidd+uf+uurL3rNdOZNwdXe80b65muCJq66efPmhqWvfhb6d1SFdtxttrTf0xf'
        b'pbc7PyzsH/ZnQDxn8uykn8vtFu6Md5k68fa7qOrTb5a/UTzT/brlG6/xmzecnzm7dn3thhu2TdYftnjk92329qg4a3Fm/FXvSOMdxlfRdxU/dm/43uLB1RNfut3esPXF'
        b'9uqg4/FdW77L1vzm8J0ZFxufbdN7Sdr1pudk37uvHC+z8lO8NNDxwxutJce33H+vLVTLZ8vvbW/OPH7/n9/fvPL/ePsOuCqzK/H3ePTeFFBUrHREsIGgKApIVcCClQc8'
        b'mjQpiihKUar0XhWk966ASHJONjvJTLKbmWSSTNpONmUyKZtkk00y2Wz+597v8QRFZ8bs/sMvI7z3fbece/o595zgB2H13/j9v3z9wpngbwcv2r2dUm//xwrZxbeyVf5e'
        b'GibT+M3mO58oP/lyjYW+kfU67qQ4CxOHbAUxe82Iay3wEAQ1KgRqcMiPSO+ev42D8IhWghJ23cZ67sSwiWUVz0iZFcIDaw+z/tDZutf5zZBkDyjV4g3rlxz48EyT90Ah'
        b'chRqotTh0H6tl/z8rDia4Os3ERpaJMGiOwvWcM6oivVQQTqzdwKf5RY+IEorJX50d6eCO2qlKWEztJ4VrsA1QTfm8iAi5qWyOKIHFvIrOLFQwm4n7VzGN7ETH63FdmXX'
        b'rRcFD85jfBQHpUGMc2Y5SBLEpyFnqRxM30l+04czz3CWxvZADJWGMC7ceumBzjWsdQXxT5pkcqkxSUo0v5OWTNr/JA9AyZko46Cm0Gq4TwIdMLePry+GtT4pDRLYKBsA'
        b'p2De8KYEHtMi2vkJqarS9kpx9lCQgptqnaTN45TQFwFmoRJH6IlnR4KWOKrWdiV8aGcpuK+mtC8+b9azJY3Vd6CljQt1Oe5FQxffIWN70AgtnPXpaUjScZxQgAFI33Ez'
        b'f4JzJFV8lK2uZGZzhzcZ0CNW1kjgXVbYDx9BuyF2swyufCwS2oPk7qSzKiXVvXunnDlpERaRgGr1Fnx+TVipSnMwfg+9GxnL1/WUeMGobzqPWNXb4bBg6eHEntV4mEeG'
        b'mgF2HOHwcPRnS8IKLoBvGDERrBsjccVnmCPc82zStBFOjTtDCFpXHQ33S+ApNOETDpQ07Mc2ppg+105hHh8Z6krIoMQca5VXe5c03vSChqLvwdjn0fTviDQ1uZ6vzSO6'
        b'6mLBOcduCvHG6PyHlVjQ5DFi5mhTFWsrG/M7Q5q8I8LSp8KPtpI+jxV/nuc1xVn6cuXzxXYH8rtGv1jpHlD/zH5LJeFVmxVgSvncFki1+fLbRS8t9rNWO/++6LUFx7+m'
        b'udTTQDGDop3BFt5EQK7kPi+s/yb9C+QtBdQup8XFJL22o8C/Li1ImH6powB7T5qekfo564LL51W+HOEU8ZpJ31NMauWVII2xiIu2iEsX+skecTqigMGbFHw/+Xr4v6+Y'
        b'2ZzX/E6VRcWlJ6e+Yc+G1C+8vkHEdxWzbZTPJrRp+Py7kxc317icmBwVFx332iP9vmJWS169X5qWbiG8FvkPTy/LlEVmvL5HxY8U029TTC+89mZzK3CZX5d73cw/Vsxs'
        b's4RW6ctIivBLGOIN54+SRRCqvGb+nyrm38RpiT//Zk0E7i4BfAlDXzPtR4ppN6/A6TeaOGZp4iXX0msm/qVi4u3LbW0G8yVDe+Xk8rm5EHsxt0WsyG0RFYnyRdniLNVb'
        b'Iu4yEHOXgei2eLULfGyol52s6q/Io/kcFeGXnBNnV+0VzfHreqyMN9ROj2Wdyp9jWapMaCTBG1onJae/7G1Y4XFYOo6XHPrSuEURL/m/I9nll+Fv/eEpL/ovEakXiae/'
        b'RFYkV5yCRfuh9Ao2LldfueoKpY6vqER/een+Mu/489n1iDsitaxNS2JLscnniTHRMbL0wM9enp4t4z805Zc5P7OczhHVLC9Tn8GkPXaprMdJuTcF62xT8akCGlj1YmYM'
        b'twFgQVULFjZL/+9iNC9nXNGRTid5S3iMpnD7dhajiY/+Vfj9GB6j8VcTbXks+dZfe37jK+/mkHAepgS75GbkyqN9Ak2fFsJJDX/jU9Z6/SmnydJXaG6JK096ZWDn+ROK'
        b'Rf3XG5z5/RWhHeZzhAZoT1p+6A66rzlzsgzYmdtoYTE8XSOv2AuPNVQYNlxk9RaV9cTQS1bBIHfbXIYxX/YSth6gr5zFMBkdHPel7/1BhceFthVsuhLjE+kvPbXBXxr/'
        b'YZ8sNiY2xj/SVxooFf/e9IppvGnI2Z87qjin9EhEY63q72fXvpSqtnraWuoZOeIIBcU+z6FJtNV0lbIMXjq4pZlXPaAXZv7NG5xM7fL8tFXmX50R8+iaUMBfpIiufRo7'
        b'jiF2HPASL/Vk6XhpgrAn5rvSVZxmkZYel5BgcU2aEBf1Gq+vWLSaGFENDPUSKm+fvilSp2f0D9hFnY/+Unjcky+MqaSxtyMN0n8Z/vUIq5/5SrWjP6LffiK1qhe963/M'
        b'ydo/3CB6Y8EWd4uvBXeprZFaj4n6h2QfhQ9IPwpPiLb5fb/0rYjEaFGJY5531Pge5286+jhGjfc6xkwab8/9Q847P0sQi/4t2uSnH3zXWl3oPzkE3biQCn22y2xOXZiR'
        b'eEdirhDuavSBmmXO4V6o4M7hUOzhVr5JOk4/d7dujeXuVqhYK5i8OdosogXPoOe5IOHO4/M4JXg6SndB3w0Y9XvuiWDO3DVCjU1sxWl85Hc8IkLePgIeEBmWCLVz8nyi'
        b'bYkcjyfgCAwpi1QTlLZEYQX3y2TIzvsdh3Fa7JCdqkjZXAwTUSlL4uLTgmDqcWmX+dFymjn6eWnGSJWnQPP/8+RodVYkY5n1tzT8q6TaqutbIeTUaWV/fQOyKjRc1RxV'
        b'LMjaaLUqF8vKWfCI3GkGJAkZY6ksYzL1u6y6hfqSCfGB+pI2/4GqoBh/oCrorB+oLymRH6gv6YGcQfDtCLD4xztDLmM+v6WFXWFQ8qe/1Al5rC7840UmdLW0lYSrlWU4'
        b'bq0QFSowcUWkCeWswPFd4xUi21D+b1rei1FE1VrTWlGUUhmLrakV6hQaFhpFq3z26KHwFukSWlHad9VZ9DBaJFPn8Tp1NnaUTpmYZ5Zr0bjKUbpRenxcDcV3KqSz6kcZ'
        b'8E81+WpMowzLlKK28XcM+VvGUWvuatD3WvS9iD1Rq0Y/plFry1SjtvNiGSryLik6hbqF+oUGhUaFptHaUWZR6/h72sK49KNeq0FrXV8midrBI6YqPKzHevnoFuqx2QqN'
        b'C9cUri00off1o8yjNvD3deTv87dr1aI20vuWfE72ph5/ay29ocHjkuwNXb6/zWx/tAOlqC1RW/kO9aKMuEZl9YGuHPHpH2mMLPXD3XQwK7j4YYuVTzDWT/+mWUiJ6y+X'
        b'BSyQKE23kKYy38rVjDhC8BUDRZOuzp+Poq8i05n1FpdukZ4qTUqTRjLTNe2FeOPxdJItyanyqRSzSNMUxg8JpSQLqUVM3DVZknzY5NQbLwzj4GBxXZrK2qG5ur4c0GR2'
        b'1QsbVMi0I8dCDztYHE1Osky3yEiT8R2kpCZHZfDlbl4ZwpV7yYJYHFciR/MV1xt4RRVFNRV27IqKKpIiySsvNsjl8ofnXjwYDqIXwrhLYjlxaStvFMlVQJIZYHScy8G/'
        b'qqXFzpwfVZSDxXHuaopKphWRZWYhy4xLS2efXGcQjZD7aGSrqAryBcmNamFNL5na1+PYIumb6AwaThoVRejxijUlRdH/LaQpKclxSTThclfUa/SUFUqUQk/RCeQ9MHbD'
        b'AuYuL2fqo3BgYzWW+Z+EqUxWfDTYxz9wqe4aLGKhFnZfh05etZTEcL3l6kPQWx7J8mDrNSzUyI7ZIQ+ZKvtgDXO990Chj7JIxVKMjelQJ4Q/WyGXNBayY+rURKJMUaYq'
        b'FPNY6g0dixCow0p77MEJ7HYSSRxEem5K2w4qZViydVTgGDQv78llxaPuvBfXlm2ifdYqUCXZxkt93LqE07Y+a5SYMyLN+gpX2DwPKHGL7reyLP87ZoEiXmZW5qXl93w7'
        b'WMQafbnAPG0WywOEKm4nk9UwZ32scF+57pg07aoKll5lRf9FUHJoXVzIWzuV075IX8517TlW4aILjvrH/r7/6l6LBEPDokcpGh5KrutKwefwltpAo32ekj/92LE1d3x9'
        b'ycEHZn879PZkofQb7+s5/aTfsuDUr8+1ljhMFweE3cz6uG/PlZrMb22es0v/oPAjNyslS90df/x44aO3quzvr924Vn1hq/bMdz68+zP9x36Wf/yv7ckalu/84ZsJWzab'
        b'gI2hjd6BStOsxojiwL9Z5/7qm3tm79w98eUfxX/961vVvrKn0C06Qmb5ePSdwF+/E3opqfaT74dX/P73Eqm+25Wqv1gb87KUtx0t/e5s58ErFvYnA6iTq4MX4x1Z1O4s'
        b'dDwP3PGoHeZgn1AVvB6HvM8f9lsRgIenUkEbbIP+PfJwovI+sWscjMAclsjV1JM3WdKz38poIh2E8P0J0nNLnl8kVHYRy6AUxnk1RK5NdsWr+gnZFqShG4g0jJWgw+G6'
        b'UCIyiFEADF8iYR/ITtpGlXTkKcnJWCgUInnDIThnuxNL7A6vJT1VFfqU7NwMhBBUK8zQphSBTFuoFfFIph9UCHXdqyNIv/YNIFgpbxaTwtsLbddihT11Qj084cnjpKf3'
        b'2LFL7qzVQQGUy7uin3JjATbbMI59LDjlZ68qMoEZZR+4Zyxko0F7BFfsDXGEQUXVSEnHe6mrenV0OJQGBfq5k4JeESSPtBpAg4T0d9oaD/It7DsIpeFYEPScvHVDJAFb'
        b'YJ63p3dXZTVoyllthOIgVnsVy6F8p5+9UAGyQgLT2CXyhnE1qIBG6FiqetmsspRIwbIoLoRCi9pGPl8o1B6xdTguI1iuqKV46aIGj+tiIZaxUsk7AwmremmypVlVRWtp'
        b'rEV4evrlfLLPkp+9Wkgs9PPq/i5MUVTluei6PKtcm7cHZ/noG7klIASvskxWit9XNOtWCNdlxsFrQoAS4dlVAlfrtWgzrp/PVsgR/Xz5DcdXLvmztpFV+TTHr5vWUhTr'
        b'xakUwSxnhcx+WUgvE8hvFN2Sh9reFb02+HJI63O4xZfk6wrPtKOgEjFVSPIZfdN3/3/6pj/MWE3pYv9b4Z5OlSUmpyuaGZP2GJuckRDFlJ1rslRuCVpIY6RMF1t1LEX+'
        b'nWeCTJrKOuQeVShgcv82V4biBGWPuVoymOdl1cHSZOlMiQsPD03NkIWHL4VobK4kJ6Un84uVNhYJcRGpUhqcxQOvSeMSpBEJslfqUOmK/tRL50qvJafGxcQlMT2OaeDe'
        b'slTCvBt2FskMHNfj0lYfTYhAKhboJU1IoxW+qe9evyVQmfvu4Svvydv1vkOmbUnrf4ofa1tai4UrVIXwBO+vg0HOJF9mkB0X/tc9+JezdrxAsmmRCZc55P8hR77nG/Gt'
        b'xRWufNZFFqbF8PS5W3ea/eIfZI/VtgoAQZkZwQjrV/Xrm27Udb8qeU1KP3c5Foo/c0r/Z/DrKwfyKETAfqh5UcCyBNFifxtfOxgIFZI/2Qf6UBPkz/xndPLFWi77I+IS'
        b'/cJV0pgv51s9v/9luIPhL8Lfifg3qZWhtdRfmsAvUH8UnhT9q/CSGF+pEARqMcufU7eQfNFawoU7FGOby2vFu8h7K85y6e4Pj4Q71tWQgw9ezrzaBGWZwiXrXj2ewuOr'
        b'suVlDCWY13MsncH8pXjA64W1IiLxuZ3bESxz5TNh7qcEJ1bJX18lQhHwRsg8bfgiMrP+hWGvR2Z9yFkVmXnAwvSI7nGnAGslodTh2HUYjTkioDmPVmgqC62AH6nh6EXo'
        b'Et7hwQosuxEHP3JQ4lUSYrPbhGiFIlbxtTUxCTG+kYE8XmG2LF4xIxL9k49Gdknby/GK10SapG98rme0NfWVs0xfda4vxy4+ZRVH3ujgvrA8uPTq1RDPY07V1XkLAzTL'
        b'ySfeokLcRUXBXSSvTX+/a638Sc9LIsabhJB0SUNa7sR6taMkMVUWLTglXsogWsWXkSpLz0hNSnO1OKxoby/fdbhFckQ8SffX+CBWV2tUAjP2MCxth/IbWCpH+VNY4Hvi'
        b'jP3pM4ps+eWZ8pCzWyMea6A3g+k+jtiBOX7LPBaXbJjPghWAf26fB2upYdn5fXEhJ98SpwXQWy7+p34Z/qvwj8O/EhEbPSBjEZi3IoaksdF2p62lvuKvFom/G3B/g7bF'
        b'+Lkvr/uyXfTD7oZz9XY/S/jZll7D9413VCboRDpKYrREuVKDw0m3rVV594LgaIlguuKCg3CBZ+c5wcIaxTzvZZmuzDqUbMqGRZwTirnP4pMrzGyG3AsvmM2Qa8XtbWfb'
        b'q35L1rZp5C6cIeOMl9S8jT1+z+22a1ChdY710KrGZs6ryTjLhb7VePWkMmvUg6M3XFfQ66utj+VVMtglIjnCcAp2/bwUnCJkEarzFk5Z616gnWXDr8z2O7WSLa8eR1ES'
        b'HnuuaJjSGkPfiMRHjJeT+GuWuTp1v5Sj8jqtQcJzVJQ/mV6VrtNfzgxKjraQ/v8i88PCnJ+BzMWr6jqk2o7uiJGkMafEO5npvyQ95aPw2MS/Rg/J+qRvRWjzPAabT5Qt'
        b'Az+2VuI5znpW5/hFLnm2LYsOQh/eW4dtylms1C53JmWLk5euesDcBpH8qsfM4SV1c/WYtdYbC547IpaSuhoeyA/ltegqfgV+svVEvRF+tut+Gn7K1yWf9AO1NOk12WVp'
        b'WuDq3nyW+ioXRqrcgFX9jL58QtwPI1YzK5dwlwU3ouRl9z8T5h5WBGJk6VKW/ycVcqQSk6+RdGOF8pfG/d9Ce+EdOYBcmcufh2DsmImXmJGWzkxfgQzT0pmZyPISmati'
        b'VVNPcF+syGljZiINvlqQQEFxbK2p0usCuGjPryE0hmj6LxGaZmAG0ylg3A4mnsvT1YWpofJzcTqC49x7HbYfmm1x7JSvkkjsI8K6JHzM69KMhzmE9H+Jl7RRFik3idMz'
        b'B4SW4eEqou94GgklYC7oiEJTFwgNhLLhd1xsoUI1iEYKZlU8K4/GnXz7Z5K0e/Td7bG8gPsdukdOanvO/2bB21FZ5Yv/6Zkjym1tVv7JiLTynQ//cs7Byv+9P3T1ngh+'
        b'tPW7Jz5O0ei68Hhfc+1Q1qLfrnD/Z2sDjlwwKvM2vfadf7/7UK9n77Z/SUhY9/GjMuuAxN9bu+5ym/3idY2Ckb/OFzz84O35rA+Gzjcc+qVd45Y//2mj451bovEb247Z'
        b'WcpvCpM100/yUe51ToRxJrqvO/HrA+FQoU9SexZmVkjv7PNmQvvTCpzHRi3sSVpxVUUQ3f04KviO53Bgo9z/uxuGNotZldDjQpmVJzBhYXsDa2yWblFoHFCCB8FHuV4g'
        b'k1nYwpya8NUL3l+19ULNEg9WCEXh88a50+xmsBeMCu70MaiSMa/1jqt2S15reLD1FXJT9bO6Tz9Qk18i5kzU5/MzUX1teVEOQ57jb8hvF2iLjcVZa1dhYTTRSq8pZ5/r'
        b'lD6DKiBZ9uxzfmtOfya/Eb+tWbuc375isQTIoKXLzR9oKFLihUwIDSV2PTpBmhQT6hWpJidltg3DJVIOZDyY3YhlLkRNHgRngXelQr1C/UJJoYE81moYbSjnzWpFGsSb'
        b'1Yk3q3HerM55s9pt9WVx1tvKq/Dmw1FRLHc+SXZ9ZfoTc5AJAU0h/hqZnJoqS0tJTopibrxXX4YljukqTU9PdQ1XGD/hK5xjgvfOTu4zU7gRWYT9pcGkr4yoW0RKkxgv'
        b'Tk1mSShLqcPp0lSCv0WENOnKqwXCijDsC+rUqkHYV4qJ14kWBggWJU5LkUXyHdoJUF5VUDy/sZGUkRghS/3MIWUFYgnLeH714npsXGTsConFd5QkTVzdg5ksOFOX4BCb'
        b'nBBFyLxM/r2QDZ8oTb3yQhaE4tDSLISrIw4WQUteU+F1WXpscpSFa3RGUiShBz2zpDmHrzrQ0uojpQkJMuZ0jk6Wi1PFhXMBCTJYYj5LYZCuOs5yHHolJBVJh64WL94r'
        b'eZ6TvTTvq3Kz5WNFOEW8PMry2ymf8j7jDKR7hARZ7HV2sd/F/84g7kJEGCVbOqqlsQj1BSxZ3d18VBYtzUhIT1siEcVYq564ZZoF/5Olmry0uBUKihwz2VZSyDqg3z6D'
        b'eqXQW1jsfd1LeotNIPdWSWHCLA3uY5NTKqkNySJ4vCaY6yX+9lu1Ei5cuyoWibFIhK3eOCGvIBgG81a2WeZkA5N1DOViT+yFuQwnPlhpoNa1qycFlcfKwd4Ki3baHA8g'
        b'7WcgNAUnsCoi/TRPDRBBrY3GfqPb/La+1NlmRSqDYGAE+0AFVC9FrSMvqUNHqqdQXV1fm1UJzAw/H649dP2OKMOKPtyazHorPE9DENIr7aztfVVE7rbYB2Oq2IwVR7kr'
        b'LhamYfIElNhitapIbMC6uzXDBB/88SU1VvAz82eW4XZVR8KFAi4zuqx6i2j/xOFw7RbzLOHDrQYSphN6GOiG+394xU+4R+6Bi+74SAkesqIuWiItKIA+XrCLv1KvrM5U'
        b'yBNaieH+XdvWijKYQJQdseRlBEJ8uFf4OG3gvi1TGxWboS987Hz9HY7b20AB5qiKsNRa+6pncgbPIIRm6QuKJ86k+JB6RBoQ9If6LIXgWVOfWQ145G7iZa0upISU62xY'
        b'FjT2xGoxtEC+DUeAYOgw9pNe5Pfv+d371kQhG3sA711eunqvvDH0lBg6lYV+I9imgTl+gm8E28MUN+9DsI/faVe6cXDpNryyHQ6Q2jcHTVDFk/+ioB9abUlHNlZcPxXu'
        b'wzfDIke77duggN2HV1dhl075ffib2/l1eA1o3bTKdXgchkrhSnw0FIVZa/FRXPDJCXnRBuWDmlqsZsNUJM90ub0Vx4WkXDHOs7xcnpMLdfiUf22Pw7LlJRuMLA9iiQRb'
        b'UjfycXEaCn39Nl9lN4/lFRsaz3GM2APFrn7w0FGRu5GERRwamzfhQ+ZHs8ORzYqaDbF7+L39CCw7x2hiIyw8v3DMSzbYwbxQiH92O9aw9IoJqFie5gt5NkJZhmEozxKy'
        b'iEWeLI9YyCJewFZ5jYSa034O4pDnN2d5VQCY3M6rNrj5QiMz9KEpjn8pGPpW2MJXbnQKc0PsYcYGe4JJP5bIxAewHvKEspaNhlgbQmZP5Sk1bD/B+gfai4m+CjcJcOo7'
        b'koKlaxywJkhZpKTNKj+VrbHW5JvOur4jTTc1A8e1cVwPSvBxOoEZhk3iJcdP7ec9owkZ+pNXPpOGUxmYA/0qonXYI8E2YkgcKZzgHnan6V5MfP7w9fSrGqk6uqoiK4ky'
        b'5rGKhHxa52BCnMkMnEq7qn0VyvRSMyQioxMway7Zp3mEuzy36EFd2tUMTT6KHk5r4DjNyh6m+R2gl/5QER26pKoihgFeMkJKRFKieENYpIrICGtgXCY5jPMHeY+VxNMH'
        b'FM9cPw3dS8vbCCPKO7BXgz9kEQn3lo2UnopTrK/JHLYdk7hChbrQJKXRKmSb7fPBcCJdVaSvqoQjMAJ9/BGous46GM2k02q0NXRIMde5fQeeKMEk8cJqoVRHE5bF0tGd'
        b'OAH3brKTU8FZMVRlCV1wJI44ExKAHTexKgTLsC4EyljR0mYxzmA75nAijov1e2EKGLJmU9yFCY45uBgM/Wk4o0dfKmEPDqmKbTZDu2BCN51ifWuI//ntDPAPOsUExVVY'
        b'CJYb0HaMGd4/7o8lzDOVd0ojDXp2cJzKgDmWeVTmxwq3i11FWGuIFULpjlksgkWc9CHu4GdPhBSoLDKAVqj3k0A9dOFDzpUNs9aJaAEpm/TDzcsMLwmsOuGKjShUJPLx'
        b'3xiuNKh7QyQ0DRH9+ZD8FysPa2WhUdlDNSiGQdHe/SLRDdGNI9ZCN61cGL0Ig8qJZJRkibLWYTdvyXWZLMQGW7WTwTzJ7uZZ/qwbdOzFUpEZ1hMERXEwd5KX1pg8z4WO'
        b'1Qce4f7OdvuEeht/usY/9Cj1D/c/fUZermP4Dv/Q55RnuPZmjyPCh0cP8w9TdnqFa1+kB+Iq85MkaawE1X9/738Sgw8krd+lvyH1zLu3u/8YNJHw3fq//2Wvl6+Jy5Ef'
        b'KxdJnpjvF6mof/RH+KBMnBS5RXTxO98QX1B2OVpiEfPWyeAu3ybv3wz4jU/+58/cdQudI2+WfNXIti7n11a/cFtfu3XtZGK9+fffHqz5ZY6nyX/UGDxWupT5x3Xj9d4q'
        b'721z2JkQobX1iXvH75Uu/HOa2ZO+/75y79f9a729bjed6jo+rdOv++ytE9sTOlX+2fMnI10XJ76hdNUp59R4vdeT7/QfaEqJv5ty6atNX51y7Pzi7ObDe89c/LO7p8Mn'
        b'uY0/fNeszejngW9rXD/k1/BXh8mmxO++U3Tc0URmsuZPt/4p8Us3BxwnNCsHT/i5OiqVnDlhvPeKq/6ALHTjkfM5B97rOPfFK6d1vvZPv3Kv+fUHorD3Qzdpd07Lfrx9'
        b'04ZM26cX/3Tto18XPG75YfnTH/z4p/+s/reNf+736ds+Zeir0XbX9/11l274D55uG4//dszJ7yZfGs7+wbPabKWaLPPOb2+4NPgf7284aFr97x9uaDfc/a7tFquUB+V/'
        b'7vtw60HVy4tDv/5rhcsjrb4Ih5jkZs1vuxuZjfeZt/744M/dMv0HTN1rfioZfWT7Pbe7A7+djfyhR9KRy0brPX5X94PZ5Kdh3XtV/0cWOR35kcPM7/54ttezOV3/b/mz'
        b'9xMu/Iss69+Sjj6I3PfTv/ff+OXIF9ceOC1zTbv50d/nG/o+PPyFoG+2fz2z5fr+fdI6yX9E1vzznzf9NtPj6ds3n975Eby//eMTP2/V/duMeMNs2e9/eNW9VNX9G/Y/'
        b'/0tZ1sd7Bz7O+nvTbyLm8wYf7NM9dP2txF//warrlyY1URtrDylrxAc6fPNHyb/YGvDT2bf/+12Z5MHCoz+/dyjg3d/9U9hVawehLsV94soFtivD0obHt2ODBB7Ga/Hb'
        b'Jetg/LIf5GGLQt2A9k08wTHFlQVihCh5EP/WAAv3mErgPtw9yfMBrdRuirBe62WH0BqYkJehPYHlPP8xCeee1yAqgmE+w6WMdJ6ytyJfzwKaJFARa8RXdwDroGgpofAi'
        b'PhFDm/ZJ7vDZA1NRtg7QbCdUo+XJhEexmkfjjdVgBvKhz3ZVf5I3VvLF6WI+MaRBX2JT7UINO6GCnc9VwVc2FnnBNjAAy1RFyrtxSF0M/TiNefy7yy7Jtjuz8R5NrXA2'
        b'VYGQ9amqu2F5aibWHhTDeDAKfSOw45whL8sLI0J9XVZcd+Mh4fbQHHRZ+9nCBHTCCK2X5PcNpW1p8mbTO4lp9gnVhjVwUFFwWOk2Nh8Tsk0fQwd0KDJKsT2T1dUb2cS/'
        b'PEP6p5ARum8/U0h5Rijm+fJFbcIcMQ1cT5+U7lQjy6JTfAp7r/EDWG+Hj4WQhLJyNM6I4QFMbuMOQT+sI7W+1I40RnoNSwLsSGfYeQ7mJHRmD+Eeh7FDuIUQsyNRPcq1'
        b'Nx60U4XGdMZ/tfRInY0wUyhohh4CJNqioWKZenwFekg9doU2vhexDUt+XdKCMQf7SQ8Wy6OE4ed4xXyuBy/AE4UifB2ESsN3XO2WKcKj8Iw04d2J3AeJ/SRNZmxZEao1'
        b'L2jCQ1jHoZFA6j/ThC84KDTh84E8+rjrAravognbuy7pwYUotJN3giJ4YOuw7qi1rxCnpDkwR5LsdEI4xQotbGO5vyegfWeQvRLDSJstWJTOcr713LF7ub50Fad1cEzs'
        b'BHlnYFZsh50qGvgMOvg8B+ARdPnxk7ljy85GHZuVoMQXivhmNaHooLywIxTvPM67hK/3wjovZWiLy+SnEIl9O3ndyCxo2kOEI1LDDiV1exjiLUd2nl1PQlYXprmUxTKB'
        b'Z6hBLQ7Ii8zIi+QabT2+T4LlltDAJ76410z43iEAS0irp2mx2AYblaH1IHTxQQyxSHYN7/LHguxIeSBbVklkskf50AUYE7qH9+HDdcuqlspLlsJs5FLV0nICGb+0t0i0'
        b'VskLXJb42XhweGtBmRJ2QPsavs0DOO3G0HgA7gbSYwTxQCVzUhYG+Ps22I/PWP3tqvAX8qWxz02erH3oOE7qXbO3cbTmHFAD+5VgGOZpN0KTmWgPOgZ76ys7rBjSxCgR'
        b'hU9lWev949fDnnt//w8bhC8PhkujolYEwz9m+tjnc4jv1eYtulV5I5SlqtdCRjGrbW0qNlTSVeQcqysp8crWSvJcY/rthQYumhJl8fIfXYk6H4nNoikWfNjqvEK2Mne9'
        b'a/LCPKx+tj5fg65YV8mQ33Bcauayjpfp0eX5zrq8qrY+D92vEg1dBg65215D8L0rnOKpG5g/XuEOT9240pX/j9UwV5PnUysG5jPyyWwUc/MwwBb6rURLXovyc4UBckR/'
        b'dnhd4HUZCKwlH6gvxT2fX66MVBa0dpGqSHCEcWfYCZFIuEkleP815N5/Mff/M++/UqFBoWGhpNAo2kju+1cuUs0XZatkqbKIbIjolgr3/SvfVlmW7huitIrv/1SKPKd6'
        b'peufO8GlcieuImD7aof60hMrL1uly/3Ry4awk7ulI6VJq/oqI1jYwYL3L2J+xVcHGd7E/84iGqvOarO0PBsLfqGKu0qX1iE4voUlsSgGLT1JcDav7vu28EyOkjm7WERI'
        b'U7mzVthwqiwlVZYm42N/vkA0B6A8VPFifaXVYgw0/OpZx3IP9pL/nrnMP83F+3kcuqwfkZ7oRYfupsCMfYzRl7mRsvu8SfvJF0PRzvhwWWpXubUGjsZgE7fAL5OYWVzu'
        b'RfXhuWFFQSEr3KlZ2KuBD6Gc1IvSM0LOY1H6VlsewXbCXBFpXjQ8t6I3Z2l65SvxnjL+eaHKQk+Z8EqNEB2dvSlXhZ4yv16XwUKapLrmYZst9DFNuQgrQpgHNMCfC9Uz'
        b'L6XnKtwBQFoW8whITulgDxkai9ykDsFiZ97hO0C0zzQAJrFBKBCQKvpEZGGyXVnkGC5rPGqxSTDmv9PkEcq/nr12XmRqsCAWhefEP9lldkX42qtT6BRaeuqK+C9KfSoi'
        b'i/CbC4fWCUH3O1CFw6wpvJMoHQadMCeCN//xMZMt92ljkb1vANYwTy4phcflHnLeqMnvpI+vnS+Wy2CK19x7jBU6vvjMjTt3b55MWO7bxRGceG2WnioOW4uFpsWFW2BG'
        b'0ShgPcwpegVgHkwI/l9oCBU/r0Ogjk2aoUo3r2IXR4aj0BW1fG5rmOdTL/mVrZ4XMMiFZxrZOIydHEzfPyeJf8Br84YnrHXLlntOPOIFIMKN06L94nixyCMn62xovJ+i'
        b'GSv3kluryJurY4UUBkXMowI1MHUDnuzn0L4djwWk8DFtD4t9s5zxHvfBHM1eY8vvLZ6BwUyykKa4B3szlMYja2geJ8IC8zh8DDV82ykpOvxe2w3CoFKyq/aKYZRw9q7g'
        b'V+22c5VnN4acX+YY7cV87v5ed/Qkqf0BvBcZ0/xJ64fya3G3f9uhktbArqN75bhXuqcZ79Iu2P69v374g7/+XmaUerfZZo/n4ePHvIO3HSvwRcdnTcY3rX+qum9uS4qK'
        b'ymLhpi8GdXhdKl+/b+KH3u/aHt+0ufPJ/fm3LT3XXfT48qiV9E/n/KfM/uvDq/bDymExzs/qmu7e/6ujbCj6oE/RyIlPHvx5eP2hOEvnjF98qSr4R4XK2uNb2jy/9f62'
        b'p5K8ihTJn76wtj/zCz9Y/8UfVPQ2f9yvGRlivh13zHzTfOvfw6sDyj8IHd8+mnabFGzXmTOOfVe+dWvim4O/ie35ZNO37L/23Q0Zfs6ykksbUn411fv+xF8Tvqr8u4//'
        b'/dzPhhbVJv/U/7Nz/Ve6s861ft8u6Fc3f5C65y9/vNpj8tvg4oZjdxOCt753MWzB1sXG7Eubdp5P83QfflD2m/d2/It9W6KH5d9C4/ef3Px1Z+Nf/yC943cNQz8+0npt'
        b't/rETwq+Z+h+2+ityspdDr94+jTB4KMtGd8fX//w+zv++P33SocPNBp8NPHf3xnoPHNS899LAvpDnvXqLNwaOWn55S8c/Hfj4Z/eSe+5PbLXY3RvyjvaH//4cvqla6di'
        b'/mftfzcsDllWNv582notN7ykWL3G1gcnwuyeF33v9hCuFU5j7nXFfUWyTckumyX7lM53Wijs0QeNsS+5GeKwUlk9fg8fXWnDBl4+Q1474wh2bDmIxUJOSrNOjN9xeBb7'
        b'vOpGIZnq3CXee3GLrS88dJdfWIQ2yNvAzTkdCyzhqaRQSM+v0lxtGAcEU7WYiLqMmVkVkMf7V/LmlfaZfGdbYRya/HhwyY+M5SFF78o9IBQcITuhINSWtSJI4L145L1/'
        b'bgilUScCkpe36YEG6Gdterqj+NTOUOhkS2vi1rnGBuxYq8RqmOKiYHa06MEw7wogdAS4huX2m6BSqDjrhFXLLHey8wTjnSz3EGv+hBfZq+XMjoY+Vrh6zJ97Z/T2Si5g'
        b'92Zu/uuQFTPITTCsWGseQHyU6NJWVbQeWsiE3JglbK8a6twYq+XNA1XNyV4+ouwNc8Kp1sLgFYWtCM985eYiGYs+anyOvTihLX9gAGeXGYzMWtSGh3yYWCyD2ZdsxQ2O'
        b'yodwxIUfpr8X1q8wFrXw7vIWFzgCkxyi29ZhFzfVBEPNF1qUWGoZlP2DirrR/6F19oKJpr084YDbaAOMy38+G+2OyEGbW0ya8naW6nLryJT3HaJPJPSNEvtNn1tdS/+y'
        b'bkWsUxEre6rJ7aslS06f21PavI8Ru9KkK2+Mqcx7F2ny1Cj236z1L14uWLYfuZGlKpg3WxUmD7MzlllV+v/b8LVWXjaZjWJGblpZM5NDe6m5xOczrci4clxuXL1u70sJ'
        b'XlpsIdpKLxhWikaZTAMSbljImw0oceNKwsyraG2FKaX8WlOKpbgeXi3FdcmUet5xQJGxyhNd/5ezs4V3lmrwCO+tUi3TwcJTyJDhS3lF5g9P5mb2Fj16PCRo/17HXcy+'
        b'SZSms/yOtHR2b/OVSxCK/zzPdnmxnqHw/ee+EaIuz2BtXnP8FQmspnDvZVWTRECTlxD2f0z8fnKp3FQ81C6Fosv8ub5lcStOUc6K9KhSIRQdosyjr2tCWQ96RV3tG5C7'
        b'FOmGabO4wtEepbRsemzmSa19yS5Wx0H5P94PLOqI+v3PxUUxFger3HKgM2XbXe3u937S/NNvX+hKd57HL7T3F0kNNpYYJ0Z8Mnu7qu5v371x6suJ52vfaizM+pd3dxe2'
        b'PHU4mj22NdPpm8US6SeSk3m/1tn+duvHLS3e1+2/EfX3A3+KTHPqu/6o6+ebNv18S+nuImsVoa7AgBvm2/rYQW+kQnvYfJSLWDsoCHl+4QTGoFtIW4UZLOUOx2swDXlL'
        b'ygNWQvmyOEXqen7LFJpxARZe8mXjU1hgzuwqaBFqgD92u03SYJFZago/+Tg2rLhV8g9JimWMXDeD09oKVh74Jqz8jmjd0g0UoTPxEjtnTDtrwwssZ+WsKxnuSv6zjOF+'
        b'vnrdxE35+1orWapwLZ0+u/HG3LR4y3Ju+vqtsYK1WXEpzPPyv1Lhcqkaav/LuaepkbFx1+RVkOT1dVfUXVqFXXoKjoyEG9zzEZeYkiBjvhtZ1OZXslb5Zl6sBUQff1pD'
        b'F9GqzEk5MINdm2Xu87NC3ImzJpzcfWa1FKcIE/W461gd97u6bOU09mLy1mvsWvdbEb8Kj//rgWi7aiupr3jiS6bNZi2mfo0tZs2mIaZ5ZvvfE7fVqpv/4pm1spAmXgmP'
        b'oeJ5XRQYwkYY2YVDwvWyrhB4sMxSIM1tgkWynHCM64InxRu1sI8Hh14sylK6I92entgQrkImLtH4ON5nrSoFV83xgKvyh/1gUA1zaNNjyTDwqU3g9KXC2S4hVRon0/1v'
        b'RqYujEgVhUUVDtYXZlh57cZuJSGuUlnUTuEEdqDfmhhtebwJbeWIfrHiEuinrZNVoFAJDAz1CrRWChT+r/8pBfmelwiRsv+YcibBfmNZ7NyHzbUtziT4bgRQmP1fa9ef'
        b'kWWn6tOSdLXkl+HUtZSVLCyWV9vT19dWMtdfq6UpXruOcWKReEe2odghyVBssSmDi6Ecwsp7L9+GVordLbKyVLl2+WTGH2iKDZDjTJZqtTvOYXEytjjqQwEpAvNr9u2F'
        b'nEgcVXXFIpJZ1ersxjvmbdIhq/AePIQhqDl6FDq1yCgrEa/HZ/AYn+lAkytOQTlMSMkK7w/VYYlL+Tjq7gbPYMwHnnnTUxVYcoOosh+GHG7BI38YcbuFC9irxoJk9DO3'
        b'B7rhEfbEXHXajk27iHo6kqCdTKx+nMCWW+5QCj1YDOMm3lfdgtZC6VbM8cyOd8YyErqP49yw4Ir3uk3SdV6ufiphTjcdguBRmLk96TjTbjCLvTAJlUkwgFU0zIwPzLgk'
        b'2mCF02W8r4M9UThmROrNQ6jGTvqZx/pwT2w+4RwPZZE4rArtpAQUJMM4WbvtITgMY9cTsQueZcM8NoRClRl2XjmP9dC1bw2O+MC8I9ynvVdBucFRGA2BfEs/WsAMNu+H'
        b'0WwcPAlNYuwhVSEPa6GV/q2IhT5shs7rGyVaZMtO4QMnO3yEM7H7Nd1YUmKkOeR4J8LdKBq2IQCeWkd6JW/ywvI4fIYtvlgXZgrDmYfxCZmYbTjmrgqNJ61PsQIJUAf3'
        b'NHeE4qQpdmAn/fU4AAqh9SwBow4a7PDx/oPb3bcZG+HEafqg9ableVtswgF9Iywk/WY6NI0+rdLV3EJ6Si9BbhxGaTljImxwlh3ApgvQ4gRPDfGBbkQAlMekH8ScYGzY'
        b'CKWX96rjIjwxN4InCbC4Hgpi6PWhFDKpG3eZY2fUltPn3HdiDeHBE+hJkxLK1WNzqLbZhaykAzdxyvziBmgOhE6z8zhK8GnAPnXazBThUzN2euB9dSg8hnOOdIz1MOhC'
        b'uxyi9T2G/LOsT439IUKHkkyYMFmPJQSfeXyoe1uCT7HYexv2QWVGuRLPfy3fD23Bh6GcsF6bVcFYc8uDjrf3GC3yIeRshFZstNfeTUpxHm27XXIMeiKlW62hMlYZSi3u'
        b'7ITu/RlZsXpYR/jYSYKiA++nhJ+BhTVnodkDmmEcuiBfiq022GC7A5/gHDyWwJgG1q7HGalKCrbB1Kmw64ewJTskAQaxhaCxYEVbISTB4SS/AzREuzm0YO6JszR29Vlo'
        b'2AeNUBhB1Jer5BKA1TBmT89M0JYGss9nG+mfvROx2zsGWw1u7DbAYdpvKe0jnwgjbw9RVrH3Jv9tN3YQvlVAEw7tIjwfJPx8gkVSrE6Ap7SnYzgPxWrYfRCrb8KDDL/D'
        b'cThsiYVWWISLt/Y53IGCSxoh8MR0I6sUh70G+5WTcTEcJ5SwMnOt9BjehUlNuH/bBxox19wbysOICd2L0oMH0BcUcsop0nCHGfYf9tY0NnRwVFnvfIqoqM0fi0LojBtx'
        b'wBSKiK3kSLFnLx3mPOThPQlWB0IVjltgayCWnMUBmFQ2IPwrMYFO2gbjTPcuOzHIQhEOwdT1TDMo20jzDRNa9WUSRhRmGagTRUxGYy3O3nIyhhqC4V06mzHiXNPqMbq+'
        b'+MAMRvDhudM4SIR3Dx9vuggLAX6wCL0a26A6jXhCDxS4yHAyEYvPwoLDOubCuxAEj9cT1g1iWTBU+/kaXLiO0zRfDyFC+3nIJRpapG3lOuGgkWXItjVBkEsAnw7D7gQC'
        b'XV8QTFjjExVojNgGHTuxOONdQsldOlcIId2hgiEkLXrWFqYyXLD1gjJLUcC7SVJ4eFWL6LJhzwk76NEP94P+g3AfZwhUT7FhPSHRMyihfU3A6HEoOM9SvLfggs/Bg+7Y'
        b'6AuPovQ1SSIUQzeh02O4uxWaLa4R9jYoHYSnN0R7HY5jzZV0WzqzSeghtagE5oh0qonmWiLOX0wi5tFphy3xBOt5EWFRCaHpADyCeqy9cIyY4qKtyZn0i5fgYQCtsAsr'
        b'ccqKyKLq0BanTLxvrAGzy5GVSKP+hBmtY/o65ttr3IGpJM4va3VvQBMxyp7D/nuzNkfCWODNW2sldGDDl7yh1ARyo2lzizRIDzGn/L0HCX0b1RKhDHovQ40OnXG/hQ7U'
        b'7McmH3iYTo/kItvNA2wnqdQLOXpKmO9ObKR7jRo83o9zpjsIGyZgzgmfGV/HR0lrbijHJmAO1BG5FmCtHgGri7bYQ8bb5Ak6zk4DLAnbEEvIlo/jHmTxPsWnFyxJNo2E'
        b'ZZoT8nYkumNlOEmwBmvov070cN+BjqPzsBOwdKAHQJLzwu4re7DKKh77so/oZtEC8yGHULkTJndZWEVJYZK4zWNtY6whgZyvjUVe0O4USjgBHTdoAcVYYUUmaAcMQkUW'
        b'dqqt30aAnscur7Cd8AxbNb1saMMFxCQfkthuOQqT3jHBdJiTkJcWRkfaRALxAcxnYek1aLyoJsN692hvBy7SK/zSSd4UZBBLqKRn6t28Tc5iA7RcgRKla6bQSuhNECT0'
        b'hvZz8bTKRbLttyf7emFxkg5Wyc6obbiEw+uggWHXTiLnTi8DdeeMbzJOu0go1cRYbRLXL57iqC3OiI9tDIeHatgUrMlT2oqIzppIPa9MhwkRsdptazBnF8G30fwmjqjB'
        b'HHTJvK2g2RMGjUgcNJvR4+W62KqWaB5PeNOsx3R7J2t8dsrBB1pO3sRac7jvu3EfSYLHmgSaZ1iqdgL6wxm5SMUpF5g+1JaEozh/8QxxC8Z8h4gNkAKSvBdajDxsgw1x'
        b'NAyqwo9C3jGY08eH3nfOE1we7rtpBPdD/MOgfztO3dngGU5sY4COYzCRgDIILedviLHeyxlmQx1v6npiLrRA48FIEsx5dMadpgYE7ALsksCiAVafMtFfR5KvxBgqL/of'
        b'95OGEvUuOJ90TSA6rjkLNQ6Q72+80xj7EmDIg+ivKB5qd2CepxhzVE7AXNQRqPOKg8mDgTAPRUdcPI/dXodNhPzEFrtpxkJRIgmAThxXhYdEBcVriVomCFgV2OoEC3Df'
        b'jAi1dTvMZ+PM1YOEtI0k5sqx3u0qdh4mppITdTITCryTiQAeZkN99hpCq+moG9gfY4qNxAM76FhLDmDZGYO9SPheiV3epBkRRndb7GPnzZpHeuzL9NYnkXh0HUyGEBo+'
        b'hqkbu4nsF3DAk+yiAeaRggf7NjKNLBXuR1tYMlTEKuNDnB100jJzoD0O6iMMsq4FYCvNMkVk1QDVcbSaftIJ8pWgPINAf9/sJm2vhaTnIAnNtLPQ4YDt2GUapBNCcqI3'
        b'fi12yLDuOJ1wD85fgLZwWuLIQRghIi5ygbvIqHwB60/REIWXYq8xCYS5iWY4mULcZQLvbfM6p4lj63d5ndxwGqszKgmxdcREWm3BtAOFCmGLT8SJWH4Mctz328JjRxi7'
        b'pmXpopZKCmyjF713hHYCDw/T+S7QxJOprOoCY0Bnt0CBM+bvkkIbzVwCYyk33bU3+sECjkbgA3pmhHhHw51NkGN7mg77ifJ+4oL1MGuz9xAOXiQVrQ5nZaRelpMIGyDp'
        b'PI3E0/Lv2GOtISFt0ZGL8NAX64M9SKxWyjyg6ZQN6RtdMO9Ks5WTJvIQnuoRabdBhz72+0D5rkys1g3YFJNIjC5Xjcij/abmZRjb7nrU39Rdh/BrCOp07TcoE8jaNA1d'
        b'cGrTDnWJF+ZtJijmbCes7zZYz66u0JjDFzD/ItQeBmJLB0kGEmci7QDnLmMrth+4StyqDnpJlnSRmj9GhyQ+YX8aSrcnkYxugaEgzD+HnRdcocTfLoDAlk8ssBwGPePX'
        b'B3mfZDpMycXb0BNhjXmRkGN00wIbSGJVnceZVFYj9CQOhmORvSM0KBGmPfDHwsOEX4vE1odjLpJRUkmsu9jMlMA8FY41B7AQHiTvJ/D3OUHBQUKbLqzaFWYcvdclKAK6'
        b'wvFJ8gXiyw8P6Glud95nbOZsTUx9ShuLjY4GWpI8XNwOrado1Godwq1niVASfJqIZO4CPNwBPcZROJ5EE7bQVtsuESl0n5etIf5TDcMOMKpFAC3Bhhgo3gQTF1MumRyC'
        b'gQR6aBiaoolDNEniaVU5IYTxU85Q4Q4LliRxZ/HuHWN8JkrAFlusP5id8V0lljhCmFLI0DI3iWPlAmFlJg7KsO+GOmk9+UY3CYi5OzaQejtl7miINfqkR54JzvKByjub'
        b'tt/MgAKp6YnL2sEkwx+xH8jfQ6y/nvgIvebOtKZb+jowlEmHO4cPTh/SIlk5A4t64diNTfEka3tVMCcD60JlsHAzib5qibhIyswI1x+A9Id5WIgj9J+MMMV7qZuw24ow'
        b'o5OIZzA0CatuWRB3aGW6biwtoOiSa6KpFr1RRZyjnqBRGhBGet5Adkj2mdjMLdqBSOrqI+zeQqy798LBTF2WRAyMdCvhSVLKQUOY0UsnOslNJZ2i8mygs8Y2HIsIxDyo'
        b'D6FHZuCuGg7oyLDoJGsMSx8XpkCzHlkqd6E9EycuE7KO7dS29SX21BSn7xV/4yCBtnMDEekoMZvS9VbKBMs6R1I2K02MoTbJYtMxotahDTjrTXyrjMyTKZLHc0ksZx6r'
        b'r27Hnq1k3A7g3WxotrIn9vdEjSbLxx5nb5lz5uYL0UTnuUQP+RlECs2aUL0Ly684Y4v/dqKGSSODtAhif09x4BwOXCTC6dpMCNi6jxSWx85QiE9SkuBROlngRWQpmzga'
        b'E7tsOEQ8fvLAVlp2ZSyUkcaggn2nSFYWEZ7WHLyC06fM8J4y1OKojOZtI1xrFm297p5yLm3tCTrf8S02rKc7VEWlQ+vBTCjZisUqF7A0Hprc6NkJmCKlswGLT5OQKCW1'
        b'pNXYXxce+O64E0T4OYQjWWEJpCo2hBw8to9MMzfiRYMu0H041eYCPCasqgiA8ZtxxtHEhZr0CMOn7PHRyVveWONlQ0gxYrIFc3f6x58i8N2LslblqSOYszPB77gK1HuJ'
        b'xDtFWGJ0XajKNki6Qyu7OpSF9cLtIXvs5W+Ib3j52SqdYB97iLCJBJiQ7NTvjxN+9qpiLBWJD9EXl0H4IgbuxZLpVCrebSYS+4qw5SoUClcmGwlEY1hqJ/bGGV7mo/0c'
        b'5mV4S0QiJZg+Q2CqIeorx2YPbYL66G3NTec1oP5AsJ7UiMRSlQMhQyfBqY4p7Dvw7nGvACiIP7jWmhjNY+w2yyLZ1AHtx/UPnyf+XQmtEVhB6grRLz7YyxwuZHpXZTpk'
        b'eMLAWqbjZUO3TIqFWtCRKiWiqYHFg5Bz5iTWBdIy6XsixXvH6Ncu6BURhy08ZUgKXMtOOrA2p3PbCO9yN5A5MG4TRuNWiIJoznsyYqijJH9r6KTJvom7BQUOJFurQqFy'
        b'B1kKE4QP50h9qdpBDG4Yql1ItbuXfjkAnvkRsneRmCgltJowJ4Mpn4yyIhfrW1DoTLrbHPGIMZIHD2FsM6nCfdC0X7b/mgQr1GR62OhzBfr34pNU2004ewkHzx1fA/1q'
        b'tzJkAamXiX9WQZcGcxtAo7kZ5hJgB4kV5RJv7Llwjsa6T/CsDzOOJ5KdpSVU7qGt9riv0zyjje2R4dzqapZgvhOZMTkElWEkLrroBPclOBZmE+SE984SS+s4gGM7iGx6'
        b'nW2BXbfoh8oDpAxV0H5yUk0ylEk0VabRHrpg4eh50iVroMQG2tVwKA4rfaDuED48RRbVfTJdFtTWYGn45khrz/U4pA514VCXSmSyYK2bgf2RqanYQz/V2Tq03OK9p88S'
        b'2g4TI65yJtjmXvf0vmUQHQXTVjowo4sPfIiy8vbh8M7jRNz9UIDMt1OsR9b7FOSug9bLxAig/pDPucDzqWfOmZBCVESifNZkP9am7nQmTjFxTUIMohuG7NfCYkYsDu4j'
        b'haXSxgibTRgfJ3FX6HiHyHR6D2mLxcwbZR0YTeIUHu+ElnTCqUJ4fB4Kk0iKd8HAUWKkw353YPgy2XztdKrDvq7cAfNUQkLmwfkYoo9uqNhnsv62LemdU4HMjMCqaJjH'
        b'Tkf6zyIuWKyFelmaXbopKVyDB/HJJR3M1cGnYmi/dOc8Vqhn9JEEU0vTeNEvQ0x05KCFh941HFqruu46dkQRaeRGEFseP3EeS3yN1x4mq2URGlIJmAVaxirnLvsHE+Op'
        b'dF5HiFMPo2bYs8vUb7MbTN4kY6DwrGmQfeRhNZJoT06e5s6ZiaBNNEkz1OwleDzVpPVPJBFD6iSBshCLMxkwYw2jUOpmS4TRg61J9EfFNTq7nN3QTFKNOFQlQ9ZHMG4D'
        b'I47JpO23u+JE1HmCc0HAaROmbCJx6u4zYlL5nhJZ55oTBY17k5BrVzbHXlvivZP4yOg09G0hxloOLR6p/qRmt8eQ8pnvwfjrOORmJ5B+v96DVIVHZnrMt+WPvVmGnpow'
        b'kHiRWPF9wRGQFkk0UHllOy2LJBp23CZeMGtOpNBGNi70BlwSxWPhkQRiOq2XjsSQaJjEVhmtsDqd5HA+vUFKObZFRsFowol9OGWiD8+2niNcaDTG7sMODCo22G8iw9k4'
        b'Qhum5g+Q6fA0FRcuqbjpY9P6XVgdlEJM7b4RdhqSAVZzkxSpHFi8SsrO1CHoNwiyOuS8jaTvQ6wLU8cO72QCfIuVZcZG67i1J7wNDfCh0Z0MVx0oOKIUSCg/QPhXDD23'
        b'iRV0ZJz2gdLzxGjzbOGJsYwI8ymRxUz2mUQSlklQLsFx+nuItLxZ6TVit63ut85id5g98aVmHLSG+SOXYHjT9uPEFmrYIdMhPCPO1kTsYdiAtrGAi7dP+NOgXXugOnGN'
        b'dxDNPbee4DHvCU8OEw8uvKyy5VA6AXo2431m3ObBMwdoC8FShXF7hqYvg4bdm5h9GxasJYZpQywKhFFVexg+r7oW+pG44NQeQoNRl9O4ACUOcS6EpFXcazKwxZ4YGXPR'
        b'NRnYwT3ia4SlBTBG1gE+ux5kb03nNYhPDx6GfnNo0jNfR9C/D1NRRK2PDrmRVDMj1jKwHZpcMGczv1c+dBYfnIIWpzDiPIXHoTUqjITC6GmmoXRiR1iqpYok1g3rd2J3'
        b'JhY7wMTWUMxPcoSu+CMkGLpoy72ktrZ6EcOBWX8ssQsj0dFiQ+R8137zmVjs3rfmXCo+CyRsqyfhcW+3sTo8iE8iQdlAXKITxwLViAgWU4LIbK8ihLkPXVm0aRJX67Bn'
        b'J9RlkEBpCIwndCLLpcFOJwnuaVq44rBLHDb6rk2EpySWscUF5g6nYgPBrgLHTm+ExVDRfryro46LElplQcAamFVhnpFHLtATs9YH6o+tX+dCVlcJbQmHDxAjf0o4MUpE'
        b'8JgF6K+S8TlkREBviohkhBMda0VMtUzpwuGYq9owfR574oMC46IvkZ46oUtLaGb5qpqkL0BpJDSctjUBMjDysCxeW4pDoVBh5BF+8Sa2+wZs2IVVjji+IfYCljsrMb2V'
        b'2NA9MqIf4FP/zFu0+9IIfRJeHfhso/J2qDcKxoLIs96XjgR4EYHfd8e6tP1ROLuFWNIIHWkpmYaql4k3DGmFmXP+wrh2LQGyMXI3jOP0Fmsi3EacOIOPbhDJlcOYFRlA'
        b'pQZqJCIHUs6uoXlLo3DhxFU6njIkDaFSA2YMDzgQX2u/YXRHz5Loq4kYzjM7LLoM7fsSYeYodGd4SViXcmLnRStwm+zbGYmSCfZhlYdeKnQZq8ZbEuNtow2NE1us3yX2'
        b'DT3O7KdIfBKJkzpEW9NYS1r0DHTYHdDFSvNzG5QJ0ZtJjN8nRX4oiyap2x2qcQpG9mLzWcLxZuLgc1rMLodB81MEdrKuoXwt3gvxYhqQEQ04fHkTdDvh8DEbJLXGdwNB'
        b'qnQLPHBglUPq3KBlDYGoJY1kT68Mxs+aE7Y3KwXvXg+PzFwgJwKKd5IO7E5McdMp6/XELqpjMV8DxmWpd2i/+TAVtpeEy6SMcfJStfQTztCvvY9AXYFNppcJUrOG2Bmz'
        b'BkfUrbIOu101gbZ9MOp/i5Crm+RfFzaZ4Uy6L/YbksJTQaJ0PpYEQpamZyqdZTsNUr1lfzp0HVDehcOHtkHfQU1sTcch/eiLptBjoH8Vatbgfb8YGigXau3UnALoBEjf'
        b'ILA8UbYISPHYFxyPI1uIP/QTKbWGb8FFL2JhDdB2/LC7iOijhIiT1HBiYNUwoxWNhXtIRhOmlnrC2DoNMTGEx5cvsLbvhJZPaNR7BmvOkCgvg0fqcDcWClyw356kQNHt'
        b'a1C9/wIyT3mnCCYvHVhPbGUOCuIsidx6TaHDnmi9iShjjAzr1nANsz04bwINofv9UrxZzxLow2FleiUPJi2MXcjyeAQ9h2FAxZwoqhUWt68xI422zAYrb2ElA03xdZiQ'
        b'pOw4QJ9WuUGn5RmcJWmJ9Qbb3LZh+35olJ0lvCnC+lSSTguZ53F0t9spyE9IJ+5Y6yDaCz3STOOICIJ6QizOQ1kEjF0lHbqKtLgygta4KzHXe9tcyDKcxcJUV79od2IG'
        b'RVhy056AO6EtJswb0Gb6MR1kU1RaZjY8CaI/H0GzPxnpD2A0xQdHznDZOIXzbucPQoMVyU2ygL3dccqXNIFRrahdzAoJI+pYVIsghS1nC07oZihJeF+efitGSbmEzIyU'
        b'FnDeltgxMyhmXHDKlBTes1ijGecJg9uwxXMnVElIxj3UYU+468eR0fj0ZoyPDykE+b6nXCywICuZlOwF7D1Mpz8BDzTw6V61BBI8g2LsCMG57dmQQ5PW7fDSi76gFYL1'
        b'UTzCNszc/XduQi3MMbfWI5gNpk0SmfQwnxHpu93Q47OWbKRgy3M7aXt1LFcq9w6W47Q5SciiC/DgFCld0/aqsclOpjDmo0m0P8QKYDsRZAsSiAYW9PDhRbhHWsEYCZjy'
        b'XVi5Xo122a1hjyO3YkkNLIjIhLvuJJrL4aEEJ0w1sOW0qZcpIcyQlYr+Bnxy6BRU6nqoE++cwxxvkrSDjK3twRERCfE6rHDUlZ2Ae+f9rPanx2vigv6ZLEti86ScH0w8'
        b'ARUpWOMUQpY100UnXWJvEX4UW8KYgasf0XCHCcxpwszZGwk22LedpYdgC9y7hHOZmlhwLITo4h4ZJ33Ec6rIcNlM4G7YiG3ampJoEyw9Fx938bIzNvvpio+tpfeGoUoV'
        b'qg1MiN5q4HG89nHbnTizkfk/SXjnwNN18JiF73rNN5Dhdz/ikDtp8O27CRYdMLLBPgmq/LcSVZST/ZOWAU276QwKjuO0mxbp8POkG7QeyzLBTu3bKrSDai9oNtK4RQRX'
        b'TX9VwaJtUvgNaN/MisEb7g+CaVNo1d/nrn0d83zxnvllNewNhepYaIdBQqPy4DDmMyVzmLm86NznifWOkZjIxy4HLLp9eTOJatKDTtOzbYG0mbwzOJPlQMoZdBO51JC0'
        b'LtIKi8g4RwT5AJg4IZ20ay/tbTEbajditYxU7+mrhC3D100JqQazsfAOFLM6JROQd5a4U5FHxg9ZPoMqHcoSFXgw11TFGRLExL/iD1kE623DSqKAM9tu0tetZjGRGqbY'
        b'ZbZ/Gx3uIo7EwJCaTzjNMUNKUrfSXpxZD4vYuy9eizZ0Dx+mAwsC555zg2plqDclRv70Ojb5QaeEfu2BORlJmr7bxBcriJhq6SiqNDfiI1/io4ME+ftYfQsXYd7NGIv3'
        b'wrw9dm4LwNIEFus6znxVUScINvd2EEcp1lbGAdk6wvqpGxZE5LO7gpIJ3bqMnGht1Y5rsX7rJmts2XGMdAaiDE/ChQXjWJzWxuYDm7Fbh2zHexcg3xNnPWBQI5OYSw0p'
        b'QOyq1SNW8XJOFdrMfaBBi0yEbkc96Di8C5qcSV24Zxq6Bvu27lZVxaKTnlishXmeJ8gunncgHavQBcf1UnB6p7afE3Q6Y81hVw8CyiQ0KxPNdxGnL8gKt9Bnl7JmiQ3M'
        b'Qq4FYfqwmDSzO9d2EbLVBMM9LY4Ts5eJeS9e2UHMoBULkwlqPYwJTDuS9lETHQuP9hM2Mx98DZaY4OResmuqYqBIFTpjLaBPGUYPupK0Jwsdc04S95ryv06y/JmzKmnW'
        b'j+C+FebbEWBG10JnNjQYEFIWbWGhZJVbqntjQmnkWjddrCfVQfU6U4LyjfYkkclHGn0e8Ycq6DHCpqMmmSyxIoQg1wxzl65thwF7eOoFj6xVoGkzKVgtZ6H/Cpk8w/DI'
        b'/jLpPySy97om74Y5X8ur2LkdGn2hx9bxGE6qYNE+Qq2G45vJsm3DiV0k4PoZjTSFGB51Ji170AEXT20jztYQHK57OTt0XRjhThHm7PGnaRq3um/yyBaRjll0Bfux5Ia1'
        b'klAbZ8AFnwm1cSDnHCuPI7aJxofcFbXNBkrSeIm2g8GsSNtJD/7KOTqTQfkrg+rCKzhzQ6i0NHILHgvvnHdl7xBiNAjf3E2HBj87McGmSyTeL8L6Q9jCPVg3T2OnH5aL'
        b'3KFVJHYU4f2NMCPcFOuHDlV2aUqZQDooEnvSS7SVHr44rXRrv+MqV7FYcKwdgnl+KetEDDz2C1LapCsSO9HHHnHC5O0+LOHXX8UPykRiFxFWHMJyoY9b45pQ5odT0RDc'
        b'cBpwl79xDAt3YSkd0swRkTiItfCqwA7+xm7sXIelAao7oIB74qpuxfMFOWBhpJ+t0iksEzx3HhZ8d/Ewn+nnq8LyeURiWxEWiaFR8OhVGl3hjjuoviJ47o5GW4u9ePsi'
        b'fmntp1dYqTf9IF1RuP/xPTEiawn/2F6Lfdynqy0K1y6yVBUKBwUnsA8tpOxDh936IpZ15sVHE264yXtaT2VAjnByWy8KB5cCnQIc5o5rCeemeYydG/YGWEv4N3sPwSCd'
        b'm6ubcGpk3S3wz9OuwTg7Npi2FY7tmJaAUbWk8XfwY4OyFOHUJFC71Kji7togOh/iXtPCCWF+kLC2PKg5xY6I1cUSzgju3l56qwdawvlx5PkJx7HeVfhigqjgPjuOzRLh'
        b'NC6fsxYLXz27QAhHkH94QQC8EXTE/adBi0raMwKJp71Vds0/JxsdNv2nmOs/eC/RsrztN3/44fx7Nzer6fvmKEdk2uX5VOWY59X6qHt/cs3l6o+Nf/f499eepqbovvVu'
        b'7OKfFn70TsuPH1z80dfbzHonw7/wZOxZe+aPHN8rme7+ZX5EWU6vi9pe76DF4O2XHfv1fa3vnnEve6b1y7f/Upfr88U/S80H3/byvHHo57/96tGp8MyPtTLMDvwuJuWA'
        b'QVrdoxNVwUn3nD/5ylfV9qv+5+byD28dnfvpW3tPFg/MF33v7pngwz8tTuxQnb5+cl95yPvOEx7duldtvtXpdi9D6bjTdPdt93Vnvz0+8t7fjNeFffvf7vse+a++rqoP'
        b'tcsyA2Rn1/Wr/Ovd6PivVHw14OSG6lr/E3qdKsNdRgd8/T/+W9f3/vW2yeH5yctjF94L+3abxU33d3d+K9jv2tkfOznUvONsazux9a/XNrhWbq+zb1TBPa0ZMVWt27/2'
        b'7uawBxvqd42Edf1sm+X5bdd/vd/1G8cm3t76lXObas//4j9Vz8x0Be9omlzvnv7HP4/0/cZ74buNT0yyf/XH/9fctQdFceTh2ZnZF48FUSxERAXLCAvIAgKKIiqgsOz6'
        b'iARRyWRZBhlddpd9CHpGc2hUwBV8ICiKmniIEgGVhzyMXnfpxcdp0KqQTJ0mxrpccli5K41eiUm87hlQK8k/d3VVXk35MbPd08x0z05/Lb/v+33XbjywZp+iR9O88kR/'
        b'871sX/sb+3+c+L5+qq63zmNQczFb5tYwtq8n1vHzaOXTp9vSE2pv/XAgv/LBJJkm2fZJ2aiwyYrqvnvP+9aS0G9iwtdnDc97w5WRmzr2bkpKvbqk5WrDNwOacs1D4/p/'
        b'SLhH339abP7csMNY2ll3eSy36njWYN6BQ+vWTtZc+tei9+1/z9yw/3at4c5XWWdrg2vm1D8+EvZox99OX9x4/kLco8M5rgVU/4onN241gyDb9T2315V+3FPdxWstjSVe'
        b'j48FmnPTHnFXPoldlWZUXjvIflH317cM0qZlcEZsa9mpZ94dpzfnPDCMl3cn9sY96huYXdJz4sbGL/37s3vvZ33zWW/5Xb8f+2frmr7ud+1/8wJ5eM+fygP3rqu/NX32'
        b'w+vczWdRN68E3zzx5HO2vqZy5peV5zVrPzpSf+LbO8zpx1mb+66FuAm5KGBNCpqwKzIk4Ji78O3cOcUp5ppoToG9Qq6JLYW/iAbOAReEBHzrwWHnb2SMQGu+XYLM7x3Q'
        b'LtSbjDhHnbvNU+mJ6FEFWkafRC90D8RrOikiYD2tgKXugvEQrJ1X8KJaMewoLvKUEYh0w6YkCjST8JxD8NJrAvtZ+1qPIifs9ALl6G3eIfVSeLrBVq+1UiJERSMWsnuC'
        b'Axt0FquDUcVxBS+qDtcDruHmdbQMdC0Dh4QA6WAbuuXhphDJ30Yo4HFyKvwAVjtw8K0VVkjtwKVAdGBnEbpKOyILZb/RJmyXoUn1HC3o5zyMiH5i2xlN+q+MZ0TXGWfh'
        b'r/MGRb/esNzXDiEBwqzz/wJiNniGMVkMeQwjxKk3ICDUJElKYiQTBG2eD6mgaImCkpFoo1RSHx8fpXegt9xb5uM2aiRNjkrzC4rdRMSQkhk4Yp2m0bkTNhFh/pOT8TET'
        b'K1GIsezGGHEvK1E8lvtl+8/xplSUj3fEJmJSqviplgwhQ0k1QrVMI+wJm4cUKwH9X/lnm/oi2puyXcO38zLmPer1D/Vre8QkYmcI0ee4i/Arw67Cw9pvfTXVlmBLsDu9'
        b'BC24KtHLrWxhBigDlXJChdYRH46hxs2D9dzA9Sba7i8hiPF3O6e55uupOd4pTW/M/93M+5Eqvy1VC8gtyqCAzdLW8esM3edbe0/T6qqPB9YGbJn36W2Pk5ee/SHrqI9v'
        b'2uCR4uXb2x+HxN+97N5zxtFBZ7Y746c5uozfFjVzWubpg6b3ZvnaDPnjxpyozaluvf2gIWBMR7zGZL8Zeb+5QZ0QumqJ9PlPD/Myn2Y9jo/5or/r5u+P/Nm057vEKirz'
        b'jPcPGdfK5g3cW9E2OHppTVfjHXX4qRq+xvWcm/lTwqwxV3f52/M7gqYvTvjL6oiMLs+54ynF3tbILa4Rl61f5ZbnPPjj5sp36fik7fMC7vmN0FvL/ZQ3rDvdVwZd8l1+'
        b'7rKnuS91q+r7qg8vzgr85/aI9Y+yfbOuZF188tnGD6w/u8dVrbwRMClkvCA52wgPmhG127YCdeRCwSVDTriDMyRs1M0Rc9F2B8J92oXh8DSugV28RsBeCi3sG8BRJWgU'
        b'vfmOgZZscTywURj+Ly88HtURPlRgKNgvpEIC597RYy9YnZyQeYTQpMJjnKBbB63hKlgxVaaApwjJmwRapXWAnYJEzRy3TI0mQKyD3iEhlBGkeTJaVh1PFh3t2kbCLcOm'
        b'Y7ReAg6HgdYklaA1X+k0Y81B+FCpyk0Dyyk9PAfbRQFem9pr2AZOAvaCRuwDFyneSKkZlQrn6dKgKySNJnzgHgp2p4Du1WjGE5Rz20D1bG16mH5atISQw90k/ouUTCnq'
        b'2EGL1xRtVDQ6VzvkuTaRmluYEJwolGalvI0L03RimQo2U6A0QsMWiw3X5UfBCpzArxJx/8WSRFAPesDWpcJFh8EzOixw1IURBK2R0BT4CHa/LZCGPOlqdTh0Ydl/oSQq'
        b'Ba2225UiaXCBfe5q6EqLR5QC/0odumuaGPsuDUojdcLwx46ALTjMqwdfE3Y7Rj3tHkLCqii4VfQcO+SLJtlOcOGVCm5pJGjFkb7CjKoGFSXu8IwXbLeDMthpRbPwaXiy'
        b'CFELT4IICKbloDVUfJKOwhZwTKvH9qxwhxo3iFZ94ACJZvRa2CH23wHQlflqBmKc8LgOlscIDAIeBDsoLTg1BY1tOSZD2AkSrdq3LUwDrqn68BAZMT9FvgHuQa3hHo0G'
        b'dTZ32Ioj/tqwA/kuAjaA7eCg6Of4HqhDK42zQ4J+tEwJ2SCBx5JAm6DXt2WCclwIumFbODYgH1ZV+TtpsHWjXPRL64bHvVDnl2NbxgySUE4mweEFoGIiKBWtHIrkagfY'
        b'lR4epguPkBAevpTbBHBUGJxkPTijRYOjjUDnoi8OuvaR0RTcK4X142GN6CXRCKqD1KmLF4SFYlkrHhpYhUUtHVC0HARbF8AWdbo0MIeQaBFhi4obTlY05fW/0P9H08Lo'
        b'18AtXiaatuL5R6UQBP8KYRslWLsphjSnWOaGLd2wrZrPkNEaqkmZ/3PJ3PAWKarIBIIQylMm1mxbhGYyXupwWk0sT5s4u4On8zgjQouVNfOU3WHjpbnrHKydp3MtFhNP'
        b'cWYHL81H9Aj9sBnMq1heypmtTgdPGQtsPGWx5fGyfM7kYNFBocHKU+s5Ky812I0cx1MFbAmqgpp34+w4T7DBbGR5mdWZa+KMvEeKqN7UGdagkz2sNtbh4PLXMSWFJl6R'
        b'YTGuSeXQRSpzo2NZM7bT4j05u4VxcIUsaqjQytOpi5JTeU+rwWZnGVSEtev8iEJL3vQ4MfUIk8et4hy83GA0slaHnfcUboxxWBDbM6/iqWW6DN7dXsDlOxjWZrPYeE+n'
        b'2Vhg4MxsHsOWGHklw9hZ1FUMw6vMFsaSm++0G4WsT7xy+ADdjtOM/bReUi+xv6fYUjE502JYgGERBuzEZtNjmIMhDUMchlgMCzHMxBCNIRHDdAxzMSRgiMeQjCEdQySG'
        b'KAyzMegwLBUExBjmYYjBMAtDBob5GFIwzMCwGMM0DBrhIrGucAneewtD0guVJH6QlC9o1NPlr9AooWxQkY+eFNZYEMF7M8zQ/hCrHvQfOp5gNRjXYDM1rN7FZWyePkQh'
        b'6B15OcMYTCaGER9ZQRE5gD+XiRlabTfwJ8uG+e4v8nbziplo3J0mNhEf2XEKVZpExOC//+pkjhIcEv8NNN6Vfw=='
    ))))
