
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
        b'eJy0vQlAFEe6OF7dc3INiKh4jzcDDCDeeERUkBsE8UDjzEAPMAozOIcHQaOiDoh4xDtGxfu+7yMmqdpNzG5eNpvs7svOHkk2723O3Zfs7tvduEf+X1X3DDMwIsn7/UWK'
        b'ru7q+ur46rvqq68/Rn7/ZPA7HX4dUyARUBmqQmWcwAn8RlTGm2VtckF2lLMPF+RmRSNapnQkLeLNSkHRyG3gzCoz38hxSFCWoJBqnerx0tCSjKJ0ba1NcNWYtbZKrbPa'
        b'rC1a7ay2WbWZFqvTXFGtrTNVLDNVmZNCQ+dWWxzesoK50mI1O7SVLmuF02KzOrQmq6CtqDE5HHDXadOutNmXaVdanNVaCiIptGKU1P54+I2D3zDah3pI3MjNuXm3zC13'
        b'K9xKt8qtdoe4Q91h7nB3hFvjjnRHuXu4o9093THuXu7e7j7uWHdfdz93f/cA90D3IPdgt9Y9xD3UPcw93D3CPdI9qjKOjYZ6TVyTvBGt0dUrG+IaUQlq0DUiDq2NW6tb'
        b'AOMGI1CpkxVUeIeVg99U+O1JmyVnQ1uCdJEFNWq4jpgsQ3AvZRNvrBkhjEKu4XATt2STNtJCmgvz5pAm0lqoI63ZpUV6pS0bjcqQk1eewWd0MtcgKEpuTyCtudmJ2XrS'
        b'TLbmK8gpcgxpyBZZAb5PjrliaZGb9eQhLaLAF/BeJJdz+Ah+QK67BtOHB8i9mgT2bn42adVlyxvMKJrskuF7+A7erONd/aDUKgU+lps6Bgrkkm2F2YrCOhQ5RDZ5NLns'
        b'GgiPnXgXaaTPs/PZ43DSBG24JBtNTpNtUhXLI3s76GOydQG+mE+2cig0m8dXluAzrmHwOBe34dNh5FokuenAzeR2HXkpk9xYjlsiIxAaMEyuypTrOFdfOjjbIvBO0pKX'
        b'Q7bKJk5GMvKQwwfJSXIEntPZx3vJpmm5+GIcDMmWXETOkK24uZC2C7cmF+h1SjQ7Q9UQuwSKs9HZqodWXof+5xUqhiQhRQNHTgjkrgQtl9xcnJCjT8zHR0mrPolD4b1k'
        b'ofgm2QTPB7Dxxy18QlZiPGl2Tsmj3QojO3hyCW8leyo4v4U1xosBOyhiBqIl+r8ipjvOrXPHuxPciW69O8md7E5xj3anVo6R0JVrCgF05QFdOYauPENXbi0voWuVP7rS'
        b'xvbvhK4GEV2NghKFI1T0kdaY90OjgNjNogkMh7P+yhnzLszRizdH9w9BUQipj5cb8+T5z4k3e6yVI/ibZZ5hDDfqI9BZVBMKt/eO7iv/S/SZ1Qh9NOpP/K3R/7FsPqoJ'
        b'oaDH7OeuqFBU4yxj6q/t/90rVLz9VvafIndHctP3F3/I/Tt2C9qMPMiVSOufZodl05I8Jy6ObEnOAgTAZ+fG5ZDmyHyyPTEpW5+TzyFrZMhUclbrmgUvTIVpbXY47SuW'
        b'uxzkNrlCbpBr5Ba5Sm6S65FDyTp1eKgmJCIMb8dNeGtqytjU8aPHjcG38RU5wg8XhZCL+O4kVybFk0lzc/NyCrLzc8l2WLJbyRZA9WbSCo2JS4xP0un52Qn4Mj6DLxTD'
        b'69fIPrKT7CE7yF6yi+yej1CflIjozEwfxtBxV8FvHzoJKV5SJquUSTPKN8EcrpHBjPJsRmVsRvm1MmlGN3YkQPJOMyovsNOpttz6plHmmARXdZof5poWv/rOa1d2XN07'
        b'RPHonGnBq3eiHi169caOo3uPNlo4h6oigsw4ldh7h7MwK0VWlYZyaiP6r2/VKZwUYaaSTWvJdnwYZmALDMJWQIpJHL4Kvd7spP3orawlL5NzCUkwPs2JHFLibbw+dyl7'
        b'hu/kkh0Kcj5BH5el5+HRi7w+HZZUb7rEWvGdRQl5CXrSmjdagZRlHLlYP4o9SlyJ75EWfBLfycIXEeLXcJnkTLSO8/BxOp3MTvvql/CQPO41pdJuqzdbtZUiF0pymOtM'
        b'0zwyl0Wgzx1KOmIzQ7lozq70vqSTe0KsplqzAziW2SM32ascHpXBYHdZDQZPmMFQUWM2WV11BoOObwcH1xTl7XQa7Qqa0Poo0jk0FMbDKF7J8ZySpS7W0ZsxtgToJKfG'
        b'NxCP93Mz8R58PrOC74AUbB4pRwEiQtFCXin3oYWsS7So7rjQQzuhRc8CVy86IVfwRex25CmKyD1o2VmET1tTXLQo3oUbycncPEVKP8TpEHHP0bpi6P3jZeQOuV6owJtn'
        b'Ik6B8M3x/Vi31tYDSW4pVJAHwJq4DAR4/wp5RYRytGxZWL4C3yBbEdcDAcvagV9gUOaa8IUEYGdnyEnEzUHkYN9QBoVcJidTEpKUM/B5xC1C5LScvOyKhgfl5NyzZNcc'
        b'NANGqB7lk1NRrB5YyuvwBrJLiayTUSJKLMAPdCFiP14g6ydN5hE5shCRTfA/NI21aXwDPvMcj/CL5DAC4OQk3oFPirDdpGklvq9EenwfkX3wf/EqkYccAyR/hcAT/BLZ'
        b'DjyBsoXzZJP41mbFPHxfhiaRNkQOwf8a6Dxr2pFB4QQe5IxE5GX4j5umsvvPrcLH8f1IhG+oEH2nrd88VpEDHwc2dxya9jJpBSEnDB9bXK9R6WpKZEg3B41Co3qtdvVg'
        b'fV4K/H2XCtnrUQpKqSx20SVG7oFMcRvIzT6VGZ+C/m9HBtKiZM9GDgY6eN1Brq/gEE/OcGRf5nCyQ80IhI8m8f5khLL0KtSAno1awzVwTSAO2uUN3E5+uZxSH7ZqxKXD'
        b'e/ikFA9XoePaFyFbDo9Dp9RYHM4KW23dtAW0SvpEiVzTaFtvkdbncyVpg7HtLLIbXweC2lxYQLbq8C1ZaioGASk5F6bxuiOMXEDQ5Xth+MoifNtyfNd15NhD6cNfBo3Y'
        b'9rJmQ1FM408+y5D/8Mhrr/30ja+4/a0hsuafXjQtj+6j3D/26680mn0T9rQs+lWDZdmqkZtnnJEPHPZ2rOPtjbo+H2zdeKNn4770+v2/+KTt7oAbs69XVd55438tb+3+'
        b'5f5jb3y8IMdR/cOKHYut9xPS/hDVNG9R3g9Oxjh+u9y86xPP7MFnd/e3fvDx9sVL+j3+9vymEz+P/NCmG/f7x0AuKZ7x0yMSknRkC4oBzqXEF/gxa0iTk8ocCxeTvSBz'
        b'kKbsvAJFAtkAM32VJ4fG9HcyZLtIzo8kLYkgjCWQm3olUi7hh03Cd51D2PKYksY4INkCMhZpxhdy8B5ySIF6jpWRF/DF55x04uYA1dwTQKafxSfwVQ1+sRPR1Mk7UtHA'
        b'WfSEma0VNsFsoGSUEVAqlaIsOSfn1NKPnAuFnyg+moviwrlYzq7xI6ycwxNqtRkcIN9Xmx12yt7tlCp1bglvj6LXkT56SqvJ9tHTu9H+9JQOBr6/llwKxCI56kdekOOT'
        b'ypV4G77WBWVl7DaAsv6fGW6IKEKlZUUjKuS/miJMuR0zSBSM5NpsBIJhSlFZzdLKqcNQJrs7RdsDaRGaaKypTPyvwaVi0YOuUATkQD29z7Ka/qWLkUjM1qcVjkl5Dt+V'
        b'UwKNyjPJdcvnpX9WOBZSnmNd+YXxc2N1ZZ7prcq4vZ+uu3Lg2sItQvH+xr5psb1TEoVPhU+Niamya30nx/ZJ7X1/2cF0oXhBcWzZgeHpiZtj5kXlvkQFgLtKgV80vgQY'
        b'vxINe7/XhqxCHS9h5FS8VeTc+CC+JXJvOz7BpIJSvKMhISk7MV6XBCIYaY7CbQjFauVL0uIlkvBUFOtRUW2uWGaosJsFi9NmN0icms16WSxDNA2kgFg9/BBLVmERPKoK'
        b'm8vqtK/uGq8o/7D39OEVrWWRD8LpALyiOuZCfHw64FQWaDN4W2FSTj65yYFEA9QIw4rK40CqPKgERWzDygANwIdgTJ7jAMXa5TmOodeTJfQAhZI2ckQn9Boqotes+J6A'
        b'XuvSQVZfnDovWcIkVVQUYFKcOrTOmPdpcTyay+6+qVWAON6UpppuTAyfEy/i1y9mUmm+LU6FjHlvjRgm3mwzhqNY9KlBU2QMv7NawsSPuRjQt5ssEdONDb8ZWS/e/G3K'
        b'QDQR3akJLzIOmCErFG8O7qVF09GHeajOOGXZyhTxZu384SgLGQ3y6cYZ221zxZtv6uJQEWpLlxuNQ6+ajOJNtSoRLUDVMeoiY/kvEiaIN99Lo6rIjud5rbHmb1m9xJvH'
        b'E8NgcUSFy6OMecsMCeLN13qOQnmorVimNZb/OPRZ8eZba2EU0DtTZVHGcvlwp3jzS1MscMymsSFG4+LcftLr84apQZN5ZIowGhPTBg0Xb15foEED0DtyZYoxb2ndTPFm'
        b'zDP90Fj0975clHFxa1GteHNt3GA0Ba0LDUkxLj6+FG5SPNg/fxiIgm3TI5GRj6hj5Z6d1QcElB0pnNbY8GpNlvhywcAktBjV5USkGMvjV0pNX2gZh6rRjgrZdGP0a2uW'
        b'iDdfTx0DeJD1bAgy2q1RfcWbeUtHIyOqrpHVGcufG7oC6YYzWYm8NIO8CAppLXmARqPR+GE2u92rDLeOkYPEQ66iVJSqJ5fE0udAGDw2hgeR9CiosWOc0S5KiPGpJTVj'
        b'lKjvSOjy2DpyiJXF2+sXjeEQqFFb0Dg0Dm8OZxJJBXbj62MUKB4fROPR+AkCq6FwVsEYGeqdgiagCfgIdrOi+AR5mD4GxigP0Ggi2a5kss8KUMha8XVoMt6EJqFJeCM5'
        b'LkqdB8mRInwdWn1nIUpDaeQavi62+i5IDIdgeTSAEDcDzXiuv0goL5FL5CTIGuQAaUIz0UyLgrUllbyCH4DwvzQL5mXWILNYx068fqyDQ7gpE2WgDHzKITbxRWc/hwIt'
        b'7okyUSbocZtZ4RiQGDc6ZAgEv5fRbDR7idlFWZUKvxjtUKEhcYDrWY5w1ogUfH0hgc6QE3JgYNnkAd7KKo6wDCW0K/ssKAflrMRnWelpa6iMA2Lf4SUoF+WCnNPCuh5J'
        b'7tvJdZA5d5BrMFp5oFfuEsdkF7kBFXFUVG9C+Sg/HQaLdX6LCtSz6yCbHypCBaighJxlTV9QD5rodRkahDeiQlRYj8+z4kmFoKheByG0BW+DRVmURw6L8uUrhdTGhg9G'
        b'oDkgS5zoz0awn5VcDJOjzDJUjIqfJW2sqJUcyQyDpp9NABJVMgmLWEL2kyNrw6Dl18h6WIRzE0NZYacK7wyDVreMQ6XAN85Viih1Ad+ZGaYAwTkSzUPzLNBmCo4HOWhn'
        b'mAzpBTQfza+YIorUd8meWWHQ4lbyIlCMBfi+eH9hHdmFW6CuY7gVLUQLy/EBUTbfRm5m4BY5KgO0KoO0EV8TxxzfAbgtPBpFjgAvWIRP9az5+7fffosSqAHjq7UaoJgn'
        b'kueIq+zXueNRDZo+NVRrjG6snYosz8f+XOF4D57cmhBXu32qlR8dO+uT6wPVzwyJeqScyUeost5Q3OEUMdkTZuzcseP9onXCfPWbN34Wc3/fo/UTFeaUY7NK/uNg+V82'
        b'hF7rhZp/tPi069zoDVE/m2zeOeSN/1k38lqe/ctNkYlXsv5j9t4FlZtKp/3GPG7a9beVhveFFjx/ZEPFwb0DV3zz9vaPX21UJB/8Zf2N4v/8yZJ//vpH6g+OGH6UcPlQ'
        b'uT798SfDte8VfILXbhjyIDGyYMBLt26PX3/f+lv5xIrjM3/yu3LnlsyeiWXKhDHJp6vS806UzLr+7k+eUR1MO3rusKTsa5PHgAxaQJrzgKtzIKGe58neXFhblwYwmQBU'
        b'ud3kqqTOJ5HzTCaYjM84qdHxGdKcnkvF19Z8fU5iNj6E7ypQNLkjAw1rF97MhGAjXkfWg4y6NTebqvbkSJ1yIt8XH3E4qYDpTLM68MWsAn0cNV2S7cvJZRnqQXbI8JVq'
        b'ckWnCCpRyIOxfz85QyPJGa4KAxVpmZBB+T0Swjk5H0UFDT6Goz/RvByEgX40L4sC8SOKiSBKzh7jE0BkIIC4KrqSOzh7L5/IEcO4uFfkOBxgGqCsHm9IKdaS235SRz4k'
        b'zNiKdGSdAu9Kwju6kDaotRH5SRtc96WN4MKsSpQ2PiyMqPuxDECAXHBBmCBJG6W9wmZkUVN8lLFmlX4iEqnS4efxKXJGNyZFklEr8CuW/W9j5JgJT2sqK74wlr16ZcfR'
        b'XWcbjzY2Xzp7YPSm0QePZg3dpIt9lGsqMFWbX5BfjS3en564fHPZZs3r/ZRtaXtr2vq9HY5+8r8RbVHjdByzCa3tXe61IpFGG0U7cp6c9MqaXUx/P3H6HU67q8LpAmHT'
        b'YDdXmu2g34ioEE5H43nEq0GJYdJmb7/JljugcNez3cc32/TFDb7ZXhcw26PhThY+NsA31clJKyfq4vOTdPqcfNycnJOfq88BnaYAqPhOvCWUrMfrbV3OfKCc2fXMB1iC'
        b'vRUGzryygE2nHl8gZ8PsMsVqWJygfR8gZ/uzyV++gkonSJvSd2NOSyLwSIts5WW5YwI8arUt+MK4mE3y1cblXEXoxzNeH3p38VuaU5rXK1+POVWzd+jJmN8bN2uUUc/s'
        b'Xw98SnMuLOO1u6Bm0BHrMVLrMw9eXUwnFsj1caeW4tZJcpjcBTWDbCQHfKqGqGfgo2SPNEtPnvvYDipG4MyHijMfouZ6w8zbY/3nveKp897XN+/0xWZaYRSbd/RNp5lX'
        b'peKTAarFkjSvZuE/86vx2RDSRO4+RYWVdTAOfkcVNtjcsyleHUmF32qLIsUYfl29VOSCVhNVJhb0BG2gxjQqV7z5bhpVJuJmhSFjDZrUG1myn63mHAXw5Et3z/N1nxq/'
        b'ND4qr668YP7UeMb0qDI59XPjglfv7BgCS597VJljesH4qcCvXPLuW9q1qKhU5QgtGXN84sxRM4eUTNwx+K1XD2jQocE9hu75o4Qia3CrCp/Hx/GGvPxEHslzOXxtQV8n'
        b'3aMiJ3NLgGORbcmF+aS1IHtqNL4gR32K5ePxkcXd1UQjrOZVToPgMhsEk1PEjWgRNyJ5LhQYAzV38MAO7P18OCL3yGlhT0iN2STAe6ufYuSg3NU+wIcztKLtfjjz505m'
        b'juyZz5EWuuFFXpyOmwt1+bi1kO72oRHkmqKMXAqpkEmTqvDHkfEijsjZXpTCraxUSngiY0ZkOeCJjOGJnOGJbK08GI2gVSo74YlCxJPRMalIWNUDyhiLq3IkneSPcYAn'
        b'eSDPAp6sCx2OLFO+SZI7yuHJB71WDtx6NWJdSrj8gxXFKem/eFNzY/fZtpm6P8THbHhc2XJFN+/ce18UfjL269fa9scMf+PZyZP7RUx7//0fZNz9sNcPdfHzH55/4ZPX'
        b'G3P+PnX1Fn1j4/mPfvmfE44Zs9/b9odvuKnL+05aGQnCC0WTrPQVzEimQkAc9vL4GFcagg8xqxxuC3fRvVKybapC3Co1kXNOOh0lU/GNXLoYW0hrIUipZ8eryVYeb8TN'
        b'uJXtYSyZDFJ0C2lK1gMC7gDsy+fwK30GMIj4WHY9acnHFxCa2B9e4mYDLzzUlZyifOKjjkgZXmXugJOxIk72BWwEQUUDOBnKhfM8r+Z78/aBPsxUUMwEdKS98ygrXE5b'
        b'pT8pC7oYAGOpBGcfFIiltNIDflj6We+OWKokRxS5hXrcTDbjo35IOhgfk5ODsWRXcB42FknSC90rRZWKbvKxAFoWAb+9OuHoYGkDvvpHA0JRnAxkFcvv0hUiju5O1YZ+'
        b'y61DqM64eFDVePFmpjJE+QynBWQ2JmY+GyXezCgIC8cyJuqEayZXizd7Lo9Oep/Lgitjw4+X5UglkwfEGrg6Kio1HB0kmVBOPj92xkXuHQSLIdqWKtkW+kUqna9wMIla'
        b'Y/gJNFi8+V8rdPxLXBuFzh+LzZBKFj9Ttk/2d9AojdH7akrEmztmTYmWy76igFKjuTTx5ijr5AEu9CltZ+o7hQbxpmF17NBnkJHWOYXrsVi8edmaOOtL2RX6+oz+FZXi'
        b'zY1jo6pfo84hdca8nFGSteQLc3rsKg4Gvs6Y+kqcZCl616EIH0x3fmF5PyyQTCgFieHT3+OZmFhzoW8/8eavRvULPcdX0yZNMc21iDfz5ePLrqP3ad+jZctWiTevqOfM'
        b'WCybTgGFVmaME29eXWiOfY/fwQEg5ebVkvEqcV5Vfb5sPwevV/51tDSbU3V9tHGAGXBz8ZGeseLNbWUa6z/4iXToEt0jpR55Mp6Ly+E+5aBJvX89Ui7e3DUnNa4f/4jO'
        b'ZrG7bLr0etSwoiyuid6cUfRsL2TRtA2WO0ATQkf+Nq1059RikhK1af7ef17+cGLsoh4xAzYuOvFIsWIzHvPWh1vKSw/McE6aYZcV4NETVQkfrWpbuKbw0vu2lf/7+l+b'
        b'51//e9GS1aMrd32Nz08d8GpCTO8Bxg0vtMl2y9quvTquNa3iR/rYOr7l26kNbyy6+uVrsIZWTN9waMvNoZtuKi6l/SLNuesHrf/9Dbd4y4QTyrbdk8jmkrMfzNd9FJE/'
        b'eMUn7xdl3r37+YbS1/41Ys+dgT//yx9m1vfavX7hvc8z3uifbS7auaimKnvPvgVvbeg5d+evDjgyn+/zz6zb+y//TD9m5dHk4lfevfJ2v90/ntXyDzO+ZN3y5u/6/Trp'
        b'xjd/9vwr58tp/7P4ZeeUuhX/+mvW4/A+/373+JTmz1r+Mu7me6O+frxafu4nG/6S0TT9TQXu++/Peh5RxX3wPBqasvSBJVcnY+LbWPIiueHPnEXWDJq+fDzIty8z8mrK'
        b'ImdyE+uWxGWBDMQhNWicq4HlsWfkJnlxaQK8Hj8Sb+KQ3MWRZrwzVRfxFCL69KQLEu1voaYkuNxkXWaottVYKFFldHiuSIcnqWVAieF3OJMQojgt2waJYtJCNB8up9sj'
        b'PNskgR9Zh7/sSiMLh/LRXCjQcDVn1/poOEigq80mux/Z7oKncPYhPopNq7jkR7F/FtPRzE1umEWKXZgDKnYL3ka284NA6twOSj/MUKISTSVXleTOxCUBGoNC+uuohMRM'
        b'PchQGS+EMYM3D4oIL8g2hpTJzHJBLig2okauTAHXSulaCdcq6VoF12rpWm2WUzZQyQshQuhGNdwJcYNkWRbKiH24R5UuCHazw1FQoZTgq6VfRvXTKBsRXW18rjeVaomZ'
        b'KJvUwExUwEyUjJmoGDNRrlU9ade8szqsKBANbLfIvSklcDEEVBJ8bgi+WSU6WdxTz5E7XHBVuOJnA7dc7YFTouTfFu4VTm/8wayYdMXbca82K99+p3i7tiEjanHf4tMP'
        b'sv/6+xV/1eXv//zNE//QlJoaDjXXJ3j2LH8lJuofNz9cfzR/+9s3Kh698h8uV8/92/92OC588F8eAWF/9c0rI/CBvofG7HKM/rX5m3+jR28NLrF+oAtlNpk++CZ+OTeR'
        b'LaA0QVpCE/EuJt48g++TS949QbIR3/K6b2zH+0SLzpVyfDkhaYhVR7Z4dyzJHXyFmYPwbvzCUOZ0BXXjRnIfaif3edysLWfyzyK8b3hCErmQphf1txN8CrlXzoxBeKsB'
        b'X8YteDvZnqsHaNtVKKz3KPyAJ25ohpuZe8gFeHwOtxTCEietCZHkZR0+J0eRITInuTCQ7WniA8MzoAC+hveTbYn4rBwp1XxfTM1JFOlDoeZNuCUZxDPQErcVZpM75Cw1'
        b'Op2UAYU5ju+yQcCv1JNjUCpJl5Ovp65cLeTGHJ7cxi8Sd2dZXd1tStJOKVQGg9W80mBo3yp9HmRttkVKtUsNu4rmlNJPfaSE10nSe+KqV3tkFTUOtmUFGqjFudqjrrPR'
        b'vXTB7FE6nHaz2ekJd1nbTRldqRxKO7Uw2emepLgJNpIm1KnSHucjF9RH759+5GJzPz9y0amVPlmOk37pmnDQ1diAlooWJq5Ax3nUBml/Dq7lDnNNZbvjgDhc6ik1ptpy'
        b'wTQtAmr5M62xPsoLy/voqcA2isAUBjpSQATjfTB8gOwJkGjgZTt1I+tujSEG76h3UWtkt2utEmtVGcQZ7KLOqE51BgjNSUg0/AC1/B7iMv3Ho44UTlZguX+Z5xzUmqG5'
        b'ZfvC+KnxLdDcwys/PBz1FhT+E/+Dx8d1nLghvKEPcbPVKi3EGHKb72urlTxCgqvWFoef6a3dFet5+Old38s76QGlvGYdNkztGM4HsLx438hRe1g059XZ18HPVxp/LA4O'
        b'BGg7/acLA2w1UC8wg8ETajCI3spwHW4wLHeZasQnbJ3AYrTb6sx252pxPY0IXFQprLvUa8zkcFSYa2q8q7qz7QgwTCwGRVgXhkLyNyRZDtUKxEVHhXPsh2eeSNiNby93'
        b'5GUnR+ty9ElKFLoUyGgZ3hQwuWHSX8dWzo9Dc2UgY+6O3B0FvxG7Iy18JQ9X0o/AtyqFRMrB/RxVo4CDUh4eAtxYblYAD1dtRMCxQ1p54OMKIZTlw1heBflwlo9geTXk'
        b'NSwfyfIhkI9i+R4sHwr5aJbvyfJhkI9h+V4sHw753izfh+UjoGWhgO+xQt+N6jIN7YlApYV+rRxrczhIHv2FAUxyiIR3B9J3zZHCIHhbVhbFeh4pDG7lBb1kDpEJWmEI'
        b'61sPKD+UwRrGYEVDfjjLj2D5nuLbu1W71ZWy3XJhZKtMSGJyhuhxTkdL446sDBHiBB2rMQZqiGc1JLAaegkyRhSTQY6pYCTx8ahQrd8/6a7oBh/wRKf0yC0genrkFAOD'
        b'IVxBhUqacLpENN6VTb1WJYEohA6eNKler2RNpUYiHiomHqmBeKgY8VAz4qFaqwbiIWPEQ/7RN4DAAc2i/7KtFqfFVGOpp3771WatSeqEBRiTyVpBHf87vpJWZ7KbarW0'
        b'Q2naDAu8ZWevZs9IL9Da7FqTNlXvdNXVmKES9qDSZq/V2io7VUT/mcX34+jLidoZ2TN1tIq49JkzC0sL5hoKSvNnZBTDg/SCXMPMwlkZuqSg1cwFMDUmpxOqWmmpqdGW'
        b'm7UVNusKWN9mgZ5HoM2osNmBctTZrILFWhW0FtYDk8tpqzU5LRWmmprVSdp0q3jb4tAy+zPUB/3RroAxE4BVdW6ONDx0ptNYu+iV93SFd3hBBRHM9ie+LHFc8X0pA2NU'
        b'UqgfM3r8eG16XlFWujZV16HWoH0SIWnjbHX0oIapJsgAeoFCdySIcBW8xd2px8tvxbq8ue9fn8hpxdrE6+9RV4DRvLMxNLyAHeqYhg/hQ9R4mJhET0HkzidNueTMQnpo'
        b'gxnB8IOQJNEzJXybppSbyKMUY9JHa59DLrp10qMKdAtqQCwiTSBjk/2RucmkGTKFJbSerfmlWXQ/ND8/O59DeAs5FkJu9SMPWYWTEpRRFbxoT8qqXCS6ypObFfg43V9N'
        b'yM1YQF0F8+ZkidI1Fa3JCzp8FpWkq8i+BWS36EuSw+d5OHYIIG/y/NmiGWT8M4pZj0RrT2LDsgrk0sPNlETyilizWC9pooc1oJ1kZ1JycRbZkqdEs8lJJbmK91UxF2F8'
        b'gRxxOpYrEG7G+xHZDj2oxG2WH7z8gHO8A8/ls8+M2D7ZOmN0VMYbf32w/ZuNs44NSTD2/XL9+OJ+CTs3zDLF5Tce/MeKHX+6axq4sOxSviNz2sqGk+sbf1L5p6/2/aF0'
        b'w5u/t6bM7fNl9seH3x5X9fH63777xZs/lK2Zv2bHwTZ3eevXP67s33PsXyYfyN+5KmPCoofuQ1Nqr+46PPtT1ahvP/tyS96P9JtGntpn+Ou2mxOyG4af/Sb/7f/59Zcb'
        b'kkf+++g/Pkv4hCvL+0P9wFf/5Mib8SelnctNmjnu/Ouuj3M/VuJfr1/5QsvrpePv3npwq/W2dvbXH3z7ye6cUcU7ddFsTyIEH4kIg0HSkU2j8136eLIlmUe9sFuunofv'
        b'sBJFoJO1ShvteC+5377Zfmn6MqYazV49MjcpJz8xG7eS7exQDFqG9/bDN+RWfFMlOtc/mIofSFtn+MQAthW/hpxiehF2P0dusR2nCHyPbjp5K+lFNsrInWnjmF5Erlbj'
        b'LdSLb3FC4OYaObXYSaVNBXl5KUw5vJ2Ar5PDhB64kbYvc6Ff2+gevQzNxldVePvCYqawkUNjZonmhWTcxnAiDFStbZHEzTRKsglvjcEt3ubgU/0V5EWO3MOb+7HXq/A+'
        b'coPKmFvyyAH8khLJyEEOb3ORW+zxEFhtV+jruWyB4R1hCnKP56rIfTau857Ft3zqJKjqe3z6JL46zEnVniXkJXyUKoytOryZXGAnpMRBFmuEfirIpkyd2JfzZCd0llaY'
        b'R47XcNCYIxzeQW6uZvJwGnkZn4WnSfn4YTFt6S0OHxyF74u67WW8Du+jTc2nzg65+Ag1i2uqZGnkLj7Eqh/zLL4Pr+dl63Lo0SMq2GlmyjLJJcQ6g19Y3Ie+nwijXUAe'
        b'zKRurhp8RjYLn8N3vVtbmv+zKayjxA7isAU4vKTLZnqF9dFq5pEZzotuEXJOw4dzvXlq6wqXnIGj4FfZ4Yencjj8hPOg4Ym0N8kLoECUj0NEWZ6eVbFTg05Q6bpdDei2'
        b'eq5TiZX0DKyd1Rnvq5jJ3/Rk5OAAFeLjkf4qRKemP1Xpq/Yqp1Tm6ULlW+BV+dpheBXgxyPm+kQkyrxAnPByrzi72STobdaa1bokgCITbBXd1c3lhnJLRRcNWuRt0OPh'
        b'FDyIV11C776WTmWaLuAu8cFN6FoC+m7gxXmw61C70hgEuMkHPMlffPq+8EMl+Es57wDwsKxMohrKkLKLtgiBA9GVYPXdGsIQgLdneBdBF22o8rUhuTsC2fdvx6iu27HU'
        b'1w7900W574IW4mJgbegCfK0PfMpcpp0AZH/zm1aaUm0NO9octAXf34IjY7Yj+eNjnSTTmVSrcGgtHdalw2yuZUepQZVhykanF+nxaknDKgGNBnqU4bLbtEWm1bVmq9Oh'
        b'TYcedBaE46Cb0Fl4ccX4pNSkFN2TRWX6T4E6m9Hn6sSzcPgaeYlcSCjQZ6nmyZF8OofPPYePWqJXEY55t2zc+PoXxrfKs0yPfh9X/KnxUfmXkOPLfx/zesypJb/XvL5K'
        b'qd0+pOVf+9ePGYh+cCpk7J84nZzJFStHR5DzMT526eOV5OpsJzXe4FfqyEUQiKrIJlGACRSIQBK4Idqb15PrkGHnkPFFQSYdRMZH+jppn0aS++bcOfgcE2z4JVzy3OKu'
        b'rF8qanLynqCR3I2eRytCud7UuCrRe6lMwXc0e+VCUhfAs17QBBpvA+uHlyn/68KziNoIkJvrlmeRjNFW+WN3J1woMTtFu4CrxmkBrVii5S6HpAazAAJOu8nqMPkFAihf'
        b'3akiWkcas4ykGfOhDFQFf0xVZruxC2WN/uts5pQ8V3763Pbhy0QdzHokU4Zc4+DmTHq2yqeCPUX/WlMCGlgBWW95VfYs55gIr//2vaNfGHMAYROLPzN+alxa+aXwuVH+'
        b'04W9dVt/mZgRPyJcN31Fz6ITjZMOj940BBBXhuL/GHYg4z0dz2Twvvj+7MFRTF0I1BUySJuTsoq5s+pEeXUeqIrBxVV+suST9LT9TIfZafBOC2PIDDGjvIj5POK88lx9'
        b'Xy/6dHqnwAuM4WJaILYG8XxiJdrxNh+S+gC8bfL3feoCcHdFHE3ga10Q+M2B/KW7GJvkPVxE3U+Cu2ExBxfm3EIthj4Hl66csLxGtzwuiNHNt6psdkuVxWpyQrsswpNY'
        b'odW8UiLXo5NGBzFtPNmeI4hGE9Zlr9skAErSFpuXuyx2aUQEuKpwagVzucXpCGpDomsaWuCw1XrFKQtwSFONw8YqEKsWB7XSbHc82cLkqhBbNHNGNvBey3IXrQ9EkTjK'
        b'Z7V2b6sAVrbTRDlv16Shs/OjusBFxX+8OcmcW0B3xFmggQL9nCx6BIx5aRaTprw5WXgDOSsr1uGz2dol5Xb7WsuSEDSjKrJW2Z/5eK4pH+RvHfF7G2+lB62vkT2lwJ/2'
        b'cMvJTfV8NbktMsQ75Hw0uR4Oc54JbOgMwoczyW4X9Z0mp6bj+w6Na14W3dgsJU2J89g2fQs+OzcrkYI5Sg6Srdl5ZAsHpOmEbhXeO5ycmssjsgffDi8ibbyLIjnetBDD'
        b'W/N7tTeuzldr0Xz9PBUqel6JT/THLZZxJRMUDiu8FPULon/rPnXay5jzPLZxmaao2HWvHwNKauLfnXJrXf5VvtX8zaf9ym+4/rHuyru/HVzz0jfCI33ks/yGO9V7xw54'
        b'Tf5uyXJ9qfP8Hz1/+ejhzbH33D/JOf+V3rFl7eW25z/54PfKz6+Pe/HMoiWLXtfu2f+pLoQx396WCqDEVF2mUU1OL0ZhVp4cxJvxReZPEhFiDtOFxNMTBpQOeqnlYHxd'
        b'Ti6TS1NFl7yjZA/vdSgePIcaRULwHUZqI0Cbp6dGvdawFfg+Co+S9cLN+BorYC/HR0RKjM+6Aojx6nHs9AI+nELP6ZBzoaLwIEUpaTMxlX8ZOUbOs0OR5BxpDvRWPm5h'
        b'FZA2B3kZt+DDa6hNwWdQeFjN2l7xnA6eXZ1RmJTvNSeQu2GSV1+3HFYozWynEN4jlUPbCXxPNSjjIpEPl0i9mFN2oLwBtRR428AIqY/0dUX3ZX7F2on/HEiaKfGP8RL/'
        b'deibmCeS/4BGdFfnlhuAjHVB9I/6iP5opmC1U7muNItuKhZVvja4utKyT/jaMDkocZtZOrOjqT5Ia6ibUK3dXOlROixVVrPgCQGy7LLbQZbPrJBLLaWW63Av1ZshsqX2'
        b'oEnIHSa5zoRXhktMSt6kACalACYlZ0xKwZiUfK2iXe776ECXTEoMEiXKbIze++spT94fon0Rqb33XZ/D/pNN/azn4lvsFRg1es9ENbQk7UyTlapDJulZ+VLgW0EZFt2F'
        b'Ah5SUjhxfMpotv9E94YEqnOCpvRE8L4BT9Nm1piqtCurzdLuFnSY9rm9hLdTTwJvtTmDgLGboSNWR5o2vaMwbJS68xSO11kdCy1wpVNadDI5K5DjkSaJ+JbOy8+Cm8US'
        b'E+NSo/EuvItczyXXc9AIckJDXlyAz7uoZDcwhbTkJunjc4CoShXY42kVWb6qs3JK46S4ByBFk5MDw8mZxeSw6Ooako2c8mEcMhrjLWtWIBf1Xwcaux6fDy6U63PyS6hM'
        b'Ll/tlcpbQCR/pZhsY2x8JF5H7pMW/QB8lBZkputsaMjWBMo827kz2ZaVmJOXlK2PVyLSogtfnoofuGgwp1XkCDlPGflKfNtXmvaHgo+jhuDtuYk6fY4C1ZPTISCJn8/X'
        b'ycRN+tZkfBFA40PVOfkyJJ/G4fP4OjnBAk4NcZKNCextJ96Qm0/9qA7wzy3Bu1i4L1Awj5KTCTn5dCBXk3swlhzqOUoG/P0Y3mv556C1cgc9YfJiq2Xg2/cjSEq4vKjY'
        b'0MKlbnI/ivrs3V+1rkP2nlGHtTmvfbljhmfs7hcTBtW5d81dd3lU5YW/Z2b/8Ku0awuWlP7H3OSj5bfcH//qs2sHe/97yw80UxM/+Pk/x44avm/pql1xc7/OLdn6o9wz'
        b'32jih78/Q/Wbx9XJbw36tN/N99P3Dnj+1ufb1/RNHrTj8PN7DiZknOKBYTO3+sv4Dn6Qy1gZX544ihtNbqcyXj2xKi4sGKd2Tqa8en+qqGzvI60LfRx/rVUhMnyyP5/p'
        b'9HZyCJ/Nzc6PH0rDOcH7atzC4/X4Kjklnv24FoEfBmpOMxoYu8b3k1n7yCmyl5zMzQ4Po8Z35vdvXcxs94vJi5W4mYf2FTK3VGUNPxS/gG8xOWDOs07mtlrIIm4kOvIT'
        b'YTaSZSBWHZnLCiwkewWfaV+060eTc7I08iI5JrLK8P9H1vgwygYlwsF4eWI7Lx+rZOcT1T5OHir9hrPjKrxodu/pz1ClmiR+rhT50zyazKfJgkCmHvLdfGrlYk0LfCx/'
        b'vo/nlUFyugPf/9VQf74frJnd9zeTXuiC4z7ycdwhlFUAIWWMw8dpAkzqcuYaxMMvl6nrbafivZ2aSOyUQlBnP8FWYTCwbQM71fTY9oJHVm6peOIOhkfltf9Sww3Tgj0R'
        b'AXoqE478pKYy9pbUPnHCevw/2u15ErrZ6Z50XzpPS+BCLZfzMYBQiBs0jmdiY7dTXhM6KIynoiUfysX09n8SzWkH0ytGFkvJuqWOvAJyMFUUyzkUWs+TbVOsASwsVPrr'
        b'+HcHzyaBL5MLsjKFBZUpBXmZCn7VgqIsRFCWhQqqsrDdit3q3VG7uUrZ7ihB3coLhSDshLmjKmXM35j67ISbI4QwIZx5MGla+TIN5CNZPorlIyHfg+WjWT5qt8bcQ4wi'
        b'A0IUda2JdPeoVAs9hRjqhQQ1Ru/WANwooVcr841m5XpUUr+mPlKJnlAn9WiiHtAxUIZ6OPUT+m9Ul/WCtnHCAGEgXPcWBgmDN6KyPsxjCZXFCkOFYfC3r/TGcGEElOon'
        b'jBRGwd3+zAsJlQ0Q4oUE+DvQrYSaEgU9lBnkRnCdJCTD9WAhRRgNz7XsXqowBu4NEcYK4+DeUKnm8cIEuDtMmChMgrvDpbtpwmS4O0LKTRGmQm6klJsmPAO5UVJuupAO'
        b'uTgGYYYwE6517HqWkAHX8ew6U5gN1wnuELjOErLhOtGthuscIReu9UKRZDmRCflCwcaQsiRBzhb8HI8yvZa5Up0LkHvoohYfiN5UYihREOloPLgqu4nKcqIgVrHa5+jT'
        b'wZ0m0DfLDhXUmp2WCi31+jOJtsoKUZ6EG1REhDpFU0jNaq3NKgp9wYQyHe9RGlaYalxmT4jB2wqPLKO0uODxlGqnsy4tOXnlypVJ5oryJLPLbqszwZ9kh9PkdCTTfOUq'
        b'EITbr/SCyVKzOmlVbY1O6ZHNzCvyyLJKMz2y7FnFHllO0UKPLLd4vkdWOntBJkBWiIDVXrg+g1XA1kQDpaq8I5RS1jV8E9fAN3ICt0zmGNTAt3FHkSPeyQt8A98b0cCw'
        b'TXwDIPIaTpA1cMuU9rIGjroMwltcm4yGkxWUfaFcLIpBE9AazqqG5yp61YToew3IIIdaFUeBjhuUgpoZvkI+MgTTKTp6m0lz3O5s1vGFJ0nqbBREPcEk1sHudGF5Eocr'
        b'jflzlRTqx6aOnuCPQgKoF9mVVGzXOurMFZZKi1lIDCrcW5xUFQDG5vUrY5C9+p2IrqBt2C3lrieoB2n0cZpRMFeagGf4UMgI+oaloprWbhHHCRBRggPI1blvn9E5f9zL'
        b'YmX7Q+29GTXCMcrDJXm4lM8oM/jsW/j3WJaUklKgU3miOoKl+xqmmrpqkyd0Hu1Jht1us3sUjroai9MuULalcNXBErGbUfuOBrUq2W2oywPbjKP+1icnhMqBT8RIRgot'
        b'T4Wb+kgRAbq/Ey9t9dFmdSEe/K9vH94LwLcNr++IMmziVteZtUaYkApg4DVJs8S/RmMSwHgGdcMrXNqYNnfdrL/7pJb+zBkgOBoGAOO9wKIkYHT1LuXDfNYJGZsKj9rk'
        b'MDCfS4/avKrOZgUNtYuG/MPXkAq2Pe+qLQctFwZCGgFtXY2pgu6BmpzaGrPJ4dSm6pK0pQ4zQ/Fyl6XGqbdYYcTsMI6C0Ugx1CQsdUFBWiCwlsDd08DTPhwLfeCL/Ow7'
        b'7cMxy3qXO6kf/TEYgSmto/KVSFzMqyqqTdYqs9bObpWb6BaATdwwhVImbZ3dtsJCN0PLV9ObnSqj26l1ZuARM2E47dChGSbrMmYMdzhtIP0xUmDt1rKXlry3SQbWJCMd'
        b'Uxdb5iJRodTHZwSHMaUuqEF20mgcbrOz2tbOrxK1DgvQT6ka+hrdz/Z3ZH1SH6WK0mgk7zSjxEqDbMl1acsot9lodFVtpb/RxMWmQugwDUEJ4kqzHRblCuCDpnK6Mf8E'
        b'84lPjGTR+FBHS4imwJUM1/jmWnwmQQ9qPlVXc+dT+wLZlkW2CuRKbmFpXE5itl6JaqPV5BXcRLazY3RhoJzuAR3wCrk5ZwS+F5ejpwFwtycU4JvkWLGenOLR2NmKqijc'
        b'yOJk9yWHKhxJ+TnkUDzZs1IZjSLxPlkS3kSOsxZAxTfTyQt4j/8WQlyBPj5XX+ytOlcBMimotqTJxqokW8g6csPBQuXklxYpkAJv56A9ZyazEOBroKq75AC+UoJbye5S'
        b'0kr2lFK7QyFHbpArcZlSEHF8Ct+mDVOgTHxChvdzeJ1AropWiR0DhzmyqEkCv6ChB8AuyVEPaDa+QFpwk7h9cWU6fslBBwifrIUWrOHIRd3MuZb/un6Gc/wUCmxcnNSr'
        b'dXLxhvSojc/99c3I+Mx5/+rzYcz+Hgf6xS4cXpKxZ1Yb91oN/+agipFfTzm87vrEg67//fiLw73yMjcu2V3/99DMfhERU5f9Tnvlw74h1p9p33nrp2d2vvO3P56uu/fT'
        b'PfU/i//BamWfsHtfuT4tHTUz8h8nx8zX22s/W7c32Tbj8athxwdOu91I3ts6L22x/pOvi0d8fjxmWM2Bs2+s+vd/l+b+7vBu/fAv3stSj/pmnbzq8st/nvCztVNf3Jdf'
        b'+PD58aO+IbkJxcMHf/HNNPXl2EPv/eb2ZwPf+2hw0aL0trVbdD1E18CdpE0KZERaVAjfJXfkeg5f7NGH2fkV02Ym6GGCmsnlZ5KzSKsMhWfKlP3xdnEb4VwpPo9bkqEE'
        b'h8hmckiezOHrDikwMn5ItpOdCTn5eRyKJKflQzh8aPUCMWby1efJAWoRyScbe6mQUs6ryWmdWOcJvB+wlbWIQ3i9Rd6Hw8fqyW4ntf7jnf3a7THkRs8OmycGvFP0znxo'
        b'1uL1OQlJungRrRTQgmuy1c+RM8yeonZ5DR7kgRRx/sQgcTw2l+ObCdI7+BLeIS/g8BVykaxj8PNgLO5Ti0l2YhJuxrdNyXS1QT1arZzcwkfJFealMY+sH5jrXXy5hbg1'
        b'WVx65MS4ePJAQTYsbhCdK8/hLeSC2Fl8N5Ma+Jo5FCbw5GABPu2kwkPGs+RSbqGeBr5twXdXcOm4sUA8xXS+D0zcoRTpxKR0XnJJiZN6c5Ojq8i23Pzc3Pwk0pyY641m'
        b'QB7i1ni8TUHjAc9m/c3Et8gd0lKALyYqaSjr0/JZHH6Z7MLHvoOD4vc5adhLJJKGQL7ATEM0xK5kGnoeaUJZWFYqM1G/zRjmm0lPJEYxA5FGiq8p3o3mxG2h+gGS8BMU'
        b'iM9DhY7U9/LI5MRXmVTRCMm3HUxCjQHHD7tsDNRFhcng7iwsCAoLjgVyAucXBIVnX3h4sktLJUgJvwgmJcwU2Zx04kUUBqkIA1yHci6fPCYJC1RycEgCfmemJO0HdJA2'
        b'OsgWwWWJzixubme5xUR5YwAr93JWG2X5dDNkNRVKOrfMVFEtbqbXmmtt9tVs76bSZRe5s4N91ePpbL6j/hQoufr5ETpN9ipQVrwlu9z9sPq2P0Ss8O5+eMUpKgSZHf5a'
        b'fhfSQPDT3mrRSejzLBoUFcWlzMucqJkgRSB19h+AJtKb0/qP+FfsPPHmmuW30Cruq74RaPry/ao0Ows0Pmok3uCIiOARR7bhszpELkbjW64cRlzwVT5XS+62UzgmW5RK'
        b'ey1sEwW47Fy6KT8fWD7dO2Eb/WyTH+hQ/aCoNPwKuWM58aN4znEa6nwm40p+62RNsQ6nRM2q+k/NkIa0mB7LL/xl7rwtd67HTYiw7N3cs+j92x+iAeG/Guu0ZdrG/qhH'
        b'SOS8eZN3ffLO+YE7D/Q50zzSNCT9zu9fD/3hyNeG5R0YH7Jt7ZTb216O2DV++cEf3ZpMDnjev5Pb9u4f9j3+8MKEj0qzPvzVVw8GLi4p3r7nj8MTf3iS6yMcOf+vOZf+'
        b'eP/eP6v+tK7krxs/vjolbsTbCVlLLk05dvDhqo0T7+94T6cRt79Pg4Rzu/1rAED6G3k93qVklNmUWYR3rsz1jYMcRc6T1VT3dlIjKt5AroIMxIYO3zQG8geROeCbUSID'
        b'3Z1F94BYJCAeH8P38rnSwuWMD5E96fg0pe/41vJAEi+S975KxjwEgRykfK4/2SdtG6x8RuzA9szUhML8JYO94SzC8DWenI+eJbKWSypyWIoV9EqGFCooAl9hxzXmkXsg'
        b'HorC2gKolfJHI94kHpY/trjExx3bWePYycAcQ/BtJ1W8FORwCZVR8XV8nLqAFQbwSZ5cw1s4Q7Ian8glexhAAzmJtyWw7REFUi4FEeUCP2hluHjyo2mqle2cNNgDvc7w'
        b'/QxWoCfUt7kGH01IzAeBlEUcB1kA75LZ5zUEO2veXfalkvQFxrBS/RnWeJFVKcXDBVxviSnRUBkatssh+ixouHqNxBekqgL90WyBvKmLsBm8WLbdOWETJHFQl6N3O0da'
        b'hzz+MY86wg7QvClVYZo3dfOlmjf8UutYP4Fz8nAta+R6QwGBD8h5D2o/5kdYHstHJKUCD2It84QbrDaDpBk7PDJTuYNp7sG1dE+UwbdpLZoac3jvYWseho2v7+O1nHQo'
        b'F2AP9O0W50HSxL4B0MjbMxs41hu0TGafTntlj2/g2mgv0FFuDWft7ZQJXAPL05KVMtFKCNdy+h0B1kO+4PEoH5ustTigCRXVjMGMAPpODVBMT6YXMGtsAHpaautqLBUW'
        b'p0EcbofFZmWz5AmZu7pONDuJQyLamDwKxo09atFga7M/wS1XY6izm4FLmQ2s/Bze6wRJA2oBzml4OQvWUN/LO2QB5TtNOhswijQCNXDCIFAT51Kuku8tGqCg69FiTXG0'
        b'e4liJ6Fx7TYxcU47fU2BnsYB0HaDYTEvfUsB+dvAxGfBsTCaNciLh1JjqmljVBTLYNiDtKAjVqkM9My8gZ0G8oLX+MCzRz4RjP6Ve6HHsjXQBvggcEf5NWxAGrhlohUK'
        b'2sBNAej0o0niBPIi9G1BmqA0GGqcBkM5L/FqBHNUH+FrA332nZrAeeeEnzL1u7TBbDBUPqkN5g5t8GFFkv8yGupdIMt4m1ZsDRAIvkQkFuxKNNH5z4tfq56AztA483KD'
        b'YSkvWRhFNA5oIH0e0ECflTCcDRIFHu49ruP1aO9qNKzQ4zo/nGgHZe04Fk+bD7mXPHDTvsN0VMG0O54wHVXfFSUU3pXBT/suKAG6iGHlk9pg7rAufU7pdMS9ZMJ3QMqf'
        b'sgelAtRgZjA8F5QKiM98PQ6QbocH7XEfuseDGMXmG3nvguASgJD6Ou811rePgDVo44BEmATBYFjr4zcwEqH+ZII97rQ+/NCPNu+o32AcfcrYU6rIKm0MThUDAXZjPGI7'
        b'jodIo/TfczwcrnKDYfMTx4M9Dj4eGta8sPYRqe7+iLBqW4KPSCBIGfIjUVS69pEojRMxcgT5mM44QncPPJoCmzMbGLOZnhkyC12NzRNOxRgMtS5A2G3+BEseOESsQLdQ'
        b'Rhqg090YIFbp7uADFAgwAGWm+A+QtjPy9PcNWf8OQyb4WC6X3A1UCj5cYQaD0+4yC5YVBsM+3nuQiNH4UB4GLdrXCV+x79ePfr5+9AvWD7Yk+OTv35FwYKA1NpudNfFI'
        b'kJ709PWkvdz360pvX1d6B+uKSO1GfO+eqFigIIPhdJBO+OGwzZ8Kyf3bX4QCxYL29jtpD+juOrS1/Xoxv4ZfI5P6IWukPZKJV5X+ffIoYcwALGgQrGOXA3snb++dR7Gy'
        b'2lZjph7DtSaLVTA/SVYONRjEOg2Gy7w3XLooYPD0wHd9D19/veWCy8dUHBXZXhibGkZSNnaUdp7EAVmAtSqD4U5QOZQ9ehrY0HawnYSsLsDW2RwGw/2gYNmj4GBjGFin'
        b'CJLzkdCN4gZsc+C8dAEdlD6D4WFQ6OxRt0SMym6IGCq6oQ5y02tBYbFH3YJV3Q1YIWyBm6DKH/hBi/Jf/fShnUZWDL5+6PqnK2YZskc5QaNmPimcIBPklG/1gaasoSuF'
        b'6qh8E39UXDvSimGNVBR8Rit9PJTtR1usVdo620pxR3t0iujT4aqrs9FgQI/5lCQPNxpWT7132jzq5S6T1WmpN/svLI8KaqqyOEFXN6+q8yqmTzSFwCgw4AbDG+1kRM0i'
        b'iWr8R0MqJI4rHRJdcgePRPuzUn2OGpuTBhVbRfOaQIM55CsrzRVOywoxpDSQ4xqTw2kQTcMeucFlr7HTyLf2rTRp92304alH7TNGhDFbrLgTzCz5TC23b6EJozwv0GQ3'
        b'TfbSZD9NaCRp+4s0eYkmh2lyhCZUuLEfo8kJmpykCeXn9jM0OUeTCzShgU3t12hynSY3aHKTJrdocpsmr3jHWBf9/4+vZAeHlXJI3uKksKhqlZyT83LO7wdoZEyvTu6R'
        b'Mp7TxsHvkHCVJixcppap5Wq5Rin+DZeFK9Tsl97RqNlPCNyVflwsMueVBRYH2Upak8k26kadwCF1LO/Ch/GWANdJufTX8X4H10lvwNRKOQvdqmah3ljoVhrwTQr1xsK0'
        b'CiEsr2Kh3xQs9JtKCvUWzvIRLB/CQr8pWOg3lRTqLYrle7B8GAv9pmCh31RSqLcYlu/F8hEs9JuChX5TMUdMhRDL8n1ZnoZ368fy/Vk+CvIDWH4gy9NwboNYfjDL03Bu'
        b'WpYfwvI9Wbg3BQv3RvMxLNybgoV7o/lekB/J8qNYvjfk41hex/J9WHA3BQvuRvOxkE9keT3L94V8Essns3w/yKew/GiW7w/5VJYfw/IDID+W5cex/EDIj2f5CSwvOm1S'
        b'F0zqtEmdL1GZlrldorIhzOESlQ0VpjNqlu6JpEdu5rafUf3oSsddLO+xTr9CUty5DsWoOwjzTakwWSkhLDdL3nZOC9tD8nqQsEBnXj886kQibtaYA7eVpM2sQKcRqp/5'
        b'Hag1UrJrEk8NCbYKF1UsfDUH1Gazeyu0OEUTn/iqd29oZnr+3FlSDcYnOAkGZLIrJQ8Yk7acGSShOnFLz//Ab6II0ttXyQnUaTfTAQmoz+RgPqe0ccwvZQXUZKqp0bqo'
        b'iFWzmjKagJPEAS/7GCzVGil5oXsDjkqO8jp7FOV3fVETvyzEHuvleU5mhT3KrZEJwN8MYipnqYKlSpaqWKpmaQhLQ0HypH/DWC6cpREs1QgySCPZdRRLe7A0mqU9WRrD'
        b'0l4s7c3SPiyNZWlflvZjaX+WDmDpQJYOYulg4NQyg1bgIB3C7gxdVd3Atw07imahZxeDvCtfo2iQt8EKPcrt4BxAaRrkfdAaubUfu6ukd+0jBRXw9BENcmrdXCN3jgQe'
        b'L2/kofw05yhB3SAX7dDOOHq/QdEo49DyP85HTdDDpZomjpU0OnUboBVMTAopsN+hUsE4cQF0Wi5dLwjGFjI9nMHDGwyPFYYRjhGOxyM6VlJtol5b7Y5fojE43hNeDOze'
        b'Uis5UyrF3U0x8KjMYBE8CoPL7LTTODLiQQlPpBia3HdEzj6VMqTpNJlBExrzRoyyUsDEgcDTlCDwidvYUGOdyw6irBlAMFFAxfYFnCaP0lDrqGKgl9FThgqDWfzDzhxG'
        b'eF9jX9WClyqq6RYsi3NrcrocII/YzdRob6qhYZCslTZoMRtXS6WlgrlTgwgi0gzfY1Ots71DnhhDja3CVBN4nJ9GF66mG8cOaB9bs1AN+ytGHfYMMHQYchBfYT1KZRVw'
        b'XevwhEIj7U4HdRJnwpRHBfNC58SjSffOjDgTKofZKT1wOMx2WiF7oFOKzgzsAwPKZSvp58P9QiJY0dMDMrDZ/YAKf2VM+Iti7hodQ2ipO915wg8v/o1m5ia6U0aNwDS8'
        b'fH2fDiPS7YDOkj2OfvSuC+fQaFB7ROfZ2I6AfF60U+YytwjrsvYznYliiAWnTTr7Sp0aBSDclsrVQI79yGS3nWql5k7turm9vM19PDIwwhb1Iqi1OduP3LIYo90+9cvW'
        b'XhdwY31wA0NrdQZLg5p2G+qMrqH2D+ytf2CtDmClCKPdhfuUmFqDfHB1QWJqfU/Q3YvbNMQH+lfpWjGurMNVLh0LYQ7zFJ7kyyOFcOqyXUx4EitiW6ZU1qmD16icwkLd'
        b'BAkKlaQtab9XaTFTgJLgALVDgXZPHx8vcGjjpXGKT4RLi5P99YbfimcbpPFiFKz4bs9TQdeDFecbrLGdY6A8AT/TZ8xPT4Yko/tY+rOuW5Hga8WUgEP5NNiIuTzweH7H'
        b'1swszpiVPCtjxtzux4P7edetSfK1ppjNvB/7lny/vEcAOjglJWlnsZgoogtWzUrTaod0Ql1rNVeZqPLd7Tb+ous2pvraGO9Fcq9blV9zJR6tjSuZN7+s++Pzn13DHueD'
        b'PYqRdZttGZVsxTP2IPDW1dnosSsQjVziqfxuo8n7XQOe6AMcOdd3jqZ7ACTS8cuuAUwOpFq1sE5NVWY/5KurXu2gTnXaovTsAljXNd0H7eka9LTAQW0HWWOrCoSojcst'
        b'zsjs/mz+qmvA6T7AojOhVdA7bXr4086qtXEZ3wnir7uGOMsHcWDQaA/auPzvBO43XYOb7QM3RPSWBHHQSk+bSItDjLlRVFpc1H2Qv+0aZI4PZDSjZ0w2lo7NdBthPuoa'
        b'Rn47BehIpag8TZ186HXcjMLC3OyC2XMzFnwHCvm7rmEX+WD/T0fYgTJ+kjYTKMJsM7TGyuQ/h0/hDhbxHQjV/OzMuTRue6J29ryZidqi4uz89ILCuemJWtqD3IyFukTm'
        b'NpRJUaVaqvNJtc0qzIdVI1aXmZ6fnbdQvC4pneGfnVucXlCSPnNudiErCxCYEWClxUHdZetqTDSWlRgJpLsD+HHXAzjPN4BD/ci3qA6JCGliC9DkgDHsLswPuoa50Adz'
        b'fMdJE3W2JG16+xG37ILMQhj+WQWzKU2nSNTdaK/2D7tux2JfO/rMZfxcVBNh8gSKNbZurBCpw590DcjQTs2l6CzstKQIxtxu9PHXNboL+r+6Bl0eSOLaSRv1GtdSO1UH'
        b'5kFf9+1vzJPAOQqYt10s2wdkXlx1A+i1eJKW7mfAr7wRUgMtr2DeeQr6poGlbUpIVUc5zo/NPp5cLHpVU0uVT34Rhal2m1lwYStJp7a/S7tI4wN0DNnMbA00sIHdiNo3'
        b'4yehYFtAYfTTalKlZpnk+IBAg41lnnfU57O+f0dl0u+d4LNE7WYCJ+1VzxX3AYJPEd13sMnaN586Ka4+r5qgZytjpfmxa+je7VFE92qr/DbbeDvdXvLIqeHhCZ51asks'
        b'YaCfEpP8RNgZjCBNEQsG73OMX1PECLsCJ3kdMGOWty0KNm5PdvOrMVsNhpUd2hLEcMDKFeiGBduDYgYNtmvk0XQwTk3yYU07whi8uOKJCLRNKSXTlEri0OzruR6lZJZS'
        b'iFYpOTNKyalNigUe8YQHGKSUkj1KzmxLmg6WpzB/w5NSslip2w1WorFIE2iQsodxEurY6Yer7OwbUAzJuhOdzf4GJD+l1h661aUOl/PRqd0IpaHoHFzjOwbj6JzKuw7e'
        b'ER6qlqkVLjqZ1ZPJnrAVEXXhuhyyNaEgL4kdINsuIy15KL5aga/07dEpviL956BbkO37TQK/EbGPA8oEue/jgArpWsk+FCheqwSVoIayajdfyYkfBSwLEQN0lIWy6LQ8'
        b'DdQBd8NYiUghCq7DhR5CNJSIEHoyJhTj6dkBcfMsoEN7N8Pk/kuZniejpNTAnCsMHN0mNvBVNDSBTPDxNDmT3j0hvi/ywmWtTTDV0K+0De1ocaTQDP47HA6v70Vvju2j'
        b'eitRe+voSJ/o9us6mc8/Svps3IAgcLp/Er6qW2rIZp8xLyi0bn+eTWKTQ7kuobm90Lpb37Cu62sKWp9vsqmzgtcpw1snb6fRN+3Dn1wxXexb/JjFk6ahM5V+ikeGH8xO'
        b'LJJRl1Y/qB3ZoQSV0eOnsMON3WGHO57eQ4kl+h8Y8Hm8UDOT16XJEe0EwNIRAOaStUzmGAvXzH2JXdMr+TKZfYpTIW5lQV7ZpqJOfZzfoQi9v5BaS8MFlLfHXxjVoZWj'
        b'AosLNrN4QF48asACwnjP3jH6DsJMq3dRih9oH0GvRtKE+XrQ+QFmVFcHyrD3jEGYHwhW9AmOUzKTIOzySTZSXK5w9rcTW2XDC+WD406ohDuNnLSI/WeyM97Q7x2+5DeX'
        b'fYMB6yxE+fwrY9gaEWl2A5qFGjnJT1lWECCs+l6gJx8ovXw2nB72oDLITn459equ8nqS08/zef3p6GfqPJyz0xqDpM3baiWq1wdrtdPmNNUACaK7Qo5pcEGpuq22bhr9'
        b'CIbDVfsE6UbB3jvytDFhpQp0mo6STbsrDEOUdhxpFwKYTJDASaNvT/IJBl3EOhkChdbIpAEHhqsUP/inllGHEOrw4aIW9rrE0iD8NxPvINdJcyIAmkUuqvIU5EgAG+4t'
        b'/XVs4wLYMEwq+5G9pCiTUXcP6uxBv+0nhFImS7/iJ2goUxV6vKQpo9/mVQDDjRZ6ApNVsNO0ahrvyh3t7lupEmKEXnBfaVax2Fbi93xVQiy9FvoK/ZhTiEroz/IDWD4U'
        b'8gNZfhDLh0F+MMtrWT4c8kNYfijLR0B+GMsPZ3kN5Eew/EiWjxRbVCkTRglx0JYos6oSmaMa0TauLAqeRUPrdUI8POkBPeGEBCERrqPZtV5IguuewiQpmheNKNL+FUQN'
        b'9DOK9bSnO8bdy93b3ccdW9mLRc8KKYvZrdrdW0ht5YQ0CgVGQ8ZiaNGIYr3oFwOF8fBsMoMzQZjI7vcWxrBlNMUTTrHP66bg4Yo8XKFO4eFnz/Dw2RkePqME/s718DOz'
        b'PLIZsws8slm5uR7Z7BlFHll2CVxlFUMyMyvTIysohKuiPChSXAhJSQZ9UJZrtzACNDu7SKfx8DNme/hZufZUSsv4bKg7q9jD52V7+IJCD1+U5+GL4W9Jhn08KzCzDAqU'
        b'QmOyfYvdG9iceSNIXwoQg3PJfWHN5U8May7aszp8iLRzGG55gWs2XCcPUVB0d5LmwiTSmk+DirYHEmURPJOy2YHEvMTs/DlZsARy8pPCGkgz/SLpNLIhEt8gL5Pzlr2o'
        b'h8xB18/kdd/eX/GF8XPjo9/HRceZskw1lTXliabFr/7stRs7Ru9ff12Bqieowiat08mkry6tzArDZxOzXCNIq3Qysge5J8MXyVaTGLVyHdlPv95VSB5OJFsAPA0hcJBf'
        b'9YycxSYYi1vGBn73mNwjL4T1ph8+bunlPav49H1h3kuLfSckxZ+J1EWwPsYfhQK/Iqxo35e2f0WT4N+SkIklhvuK+SBfo0SJHgL1nYEUf94JiNMftAUVammCKbjAb1Kq'
        b'Gc6ESp/pFheZGMSn/ZuU6qYQwKMQwCM1w6MQhkfqtSHB8EiOgn2Wb0AB+7AeeWAgjbl5BWJYQcAcvT6JBqKlUVzz+8TRCS4tWok3ZuEzMkS21YWRHcSNj7GQtkvJCU37'
        b'q4Bjhfp50mnsHJj4ZpjZ+XGkeX4ROaoGXJUjfBdfDovAp+PYqfBnpqtQnW0w/S5foiNFjVzsY233yGG803suHJHTS8jFQrKTvcCHhaC6XkMRMhrDL8Qoxa/tkRv4Oj4f'
        b'GFE+4IC4Ci0sUeGDc1bjF4awWC6Wvk68ISI3Oz83kbTqOBRWwJNTZPsK1xAK/zzeOjohi54lJ7vGpKTgjdDoU8ZcNBTflOGH2Qtd9Pu1fcjp6oQCeqq4Nb/U7xR6XJI+'
        b'jjQlx5OzJhpy16ZTk+v4Gn7oovhZ0XdeLmnJxk18XrISKfvwmtphDBNZhEcDh68mwHCTe7gxSw/P8T1+PAz2STEG8U28A99PYNMx3BoEIizyOBZHvShObBfelCVDg/Cm'
        b'CHybnMNNbHCNZJPZsYJckyMOH0B47wiyHd/Be110Z5zscQ7yfZ5xI1CHrbnz66Ds3Dj2Bb7E/FIxEL54Bt876xwiJ2ThUM0B8qKLkoUwvHOON3Q82ZIHHek5W0aD6hzC'
        b'67Jd9Dsghufr2odO3x6qPy6JHDD5OkPB8HgLj/BN/ErYOHK8JwsagE+R3XgX2YVh1mkY0HqUP2qUS0vbf5ZsmQO8/urKFYASzSvJNacSRfTnF5E9+ABHdrJPmCSQs3i/'
        b'Ax7No18JiMvRAwYAYWTQ8PGI4rj2hikRwLkTilIL2YzjpimmBDoSMDotyWR7SVwcEL2m5IJS7/cB+jspruF1+GwIKlztGkrb5A7tGUZukRsOcns5bl1pD19ObgH2jJHh'
        b'B/PxxkFkGxszfDKBnCQt9Esl+iQYWgWKxntkKybhS2TLCob5WeVy9JW6J/3OZN6BNC1i+IRPjUx24K0rliuQ+M1IvLnE0jzyW7ljGXCkR/OzS4uzC8j0qJcG2b6OfmHi'
        b'+V++KVvFJz8K+eN/vRv62l70y96jPpkx/fNf/3PjgcmFv+u7Gk19e+h/F68o1P/mvfE31VkXzD328aYIw/S26S3lZTm78/8QExlzau+1kGKVouyZ1B7Vy+4ufzSqKuJT'
        b'Yd7XWdvsv/zbW9P2vbSz+kH6nF2NK0b++YUxU/4S/fXXzRf3pPzc8v+x9x5gUZ3Z//idQh2agKioiJ2hY8VeEKWjgDUiHUQRkAEUO016UUHFiogoitJBECWek2RTTLLZ'
        b'dBNTN72XTTHt/5aZYaia7O73+T3/Z0McLnPvfXs557znfD7hk11dXjurY7lm5ZJvnoldqHWjRb+sSHRww7VJ7pcvPD6l6pK40PRQ2s/jtr5hvqqhNOfLp/823fDno79I'
        b'Hz/683MuF58ZW/f05fHdiyrg6fmKJ+5aaY280tA0Y4xpY8hTd6L2PXHm0sHwJzpvhy1sqliSt/5wcNvJwskKt6Yfn3vhrZ99t6XUuN91+S7Q9atbHa/Ntwv9/JttT+TV'
        b'RtzydP3KLCFy4WZz1F4xb1F3Udra9yOeyypcNP7YN6cmva/lN9Lpqeiu9+qbXwzutuxKc9npbZH2SbDD2xHNkrfWVP08LjQ6/z3Pnwr2y08WzznuJp/INrTwBdjNd0SN'
        b'7XAtXCA7YjGWMPwCzIZsaMLzdMFS8y/JoF6MFyh0M4ccuDhsowZYcwKeVmEOaIUzyGio9SETrmCHkaF+ErYqsA2ysDnZUFsw3y4JhKtBHHH6jBkocX1SRXACry8Jw1MM'
        b'miFOnMBpm5S0DKVQBCchHbtY7uOh1hDqLBjnZqEcc1n5rolJkQ9u4/t+9mKogALjVGxLHIVl2JpCcpaNEG+GQ3iMgULEwvGVdg42yWuU4BVihzm+HI2oFc5gEyN+YKQP'
        b'WyFbxfugA6fZu8Z7sNKbsjqI00RwDG/Mx/xdDHFpLpwIJpMvnywWpODSOSIyY45DI1zCGvZicDxmeavYpvDoRid/PMGoObdY4BFFqsH2FKywwHZjMksKjXUN9bHBOJXM'
        b'SGzbsZ2U31eqTZb5MrIG0rZbthkK7BywyC3Gx0UkaK8XYZ29NUPMMPPCbCzwgKtkM9orwsM7lpMa1bBeIVsG1FAKzAKo8/AFsvk5GptRfHNLaJXuGLuB920lXp+n2MqY'
        b'Mik1UYGPjiBbLMajcmzkdKbupJGUtJ10LYBz0EXWAwsfqaExnOfQGm1wyAzIelULR4lY56ElaIeKJ0DVFp5DJtlBj2PLQvKEcjHTEmT+Yiw39GY0SWZY7ayk//KnWzTJ'
        b'hmya2sI4vCD1h3qyX5XCMT7OGsl616yiCiMNn99DFwZ1eIgjbRWNdaUIXXuwGot8SGt5ikeEz+CD/eAoRwb+7eDo5+MPRfGLsIQ8YYmnpNuhczIH0urcR8SJAn+6nyzF'
        b'K3xLMQqU+EptWGUjF09M06HUoQ5EuvCWkLGYL8aLeljPwbTaHIzJTS97T6yAViIuCLqu4nDswgMMpAq64LCJ8n4x5NI2z0ikWXiSgWlro4XpO/mMGr3MhTzmZw95TspV'
        b'XYu0R7sW3ArUooOddc1ia2xkJVGjrpjCNYk+XiI9XrkymUIpjYbM2XRq9JLLyVCofQRKnHorpnZkfymaqA9nd4qSGbReOV6Bm/1fzsZzkEfehlrM9ZFrCz6CDjTNXc6G'
        b'ti7cIhOC084OQDm7PryHdBYvJPA+7Qwm0gAbGsDfWET6vFibKMIS7J4jHlji/s+zpzJbAZPc4/tL7gv0RbqUMFUsFY2ksKbkt4VopNhAJOWKP/XWFJswyGxLCsolNmUx'
        b'dgZifQmRvMXaGr6h9HxMW+MvZh0e3kci52ZhrhToKyOUVM7DUmpAS6LDOYkSn96VRYQlq/2AtRURm6O2RfXFUtF5OEwzf5Ey0aRV9IMlwjIKoH8y+8xKkWZ7tQ+ibzzT'
        b'i4N14No9LP+oTgiv01BYq2rDd++sHtrirbSvBw5tob6vPhi2YZwlqngHXj5rJcxJH4rXh3N/VZLPyEKUbkshQ/Lg/KYuiP1Ark6xip6y/RVuTXpMPETuVH3juVsFMR8n'
        b'6uH0lxhmY1Q9HJGSnBAdPUSeEnWejNaUPO9AXrCmXvc9vla0HMxP+S8U4kH+CNrqAtgyf4TYaKUDwjbq8EFaPCqeho1E/pUGv2sQojGHhyiEnroQzBuKekLEUKw3tavg'
        b'X6j3A2CMDdRZTh0cxrh3xsp82WKqxvWjGosaF56bDAQayLJXtEt7j8BMBiJmMhD2idapou81TAYqs3Vf3LeB2VrtWW7RoofkaqXYgSmiAbAD6X+9yIF6+1QorBWbE1Li'
        b'Ihlta1QSwxG3DosJo54YA6alZlhyi4sKoz5J1stYBArtRCUQLnPkU0KCKz16YgcG0lWihYeGBiWlRIWGclLZKGvbrQnxyQkRlGjW1jouNjwpjCROvbZUkLuDsv4l95vN'
        b'FBRfebzPwQW5N1iahpPVg2HTQ0OXh8UpSAn7w/qx0ClB4z9Rvy6W+MV+0pwlUVAxuGrdh5+FPhmu+/L46Hd8JIJurqhVeFYuSuaQtwlLe4kR8TZqKWLXHNW5S5+THml0'
        b'TBQHNGOUlvv7/FjtmtRrP1FExIWwhu05yKAJDMb/KlJBZ/YAlVGgfBOp8uy6z6Z5QPjWQGPbTKG2t1WQgYf6mFXxkF1PLYlYdRSaiQSX50/VI6geA214xJvpWdiA7YbO'
        b'2GjzH2KO7TcpVROznz2YhnFgdTIpQB9ZkBpX8nxsvRyg3R4uB3GLEf3O34cxQl2BPNmcMGyKXay4IFZQMbTdNPWzUEfTT0PvhNtY2Ib5hMVFj9kSF/556Meh8dGfh+bH'
        b'eIXpktGgIxyV6ZqK8uWSZLrUxONZbB9MELXAE8wTQiWJZmI7l86P4/U1A3IfQTcUSbFeDyqTqUkOjzti9SbDXsNNPdjIu+ceylZMRp9COfosBhp949mB44NHIElElV8P'
        b'XP+QvK49j7FBGUoGpeWgg/Jj076DEg444+E/MSj3EwGfDko7PzooG0cbzod0KJKLGQ41UV/L8eROfz5kpcYiuCiGDA5RnTEdS6LgKn9ROl0EzSuxPtZUt1XCWFp3lXRu'
        b'jfGI8CGDYsu7l6I2x2ye2hITF+MV4RfmFyb6dtTWkVtGBq77yFlremKNRHjcTi808wXVuaamNX3QDtJTN/fgvWRhoG8i3WUxcC+pchu8NzS22zDSDcaDdsN3Jpoi9SD5'
        b'/Qe4ywc89Ok/ycmyvC5KJlZQlTjs6aDPyHTc++id8M3RBmxpNvtaDPNdyNJMrfJwFW9g+QBqKNUijwQMoobCBTzWr7f6OFkMvnTb9DvlYN4Wg6zUgzF10zzGD9ol7xoN'
        b'darS27vjr4onKneKB+ySUr+g2CXnHpMq6Nefu1d7h5F+uEMW/EMiuch2/eoe0a6/18FZYaiGtOunvnFXkoff82j6kwZtxLcMhlIV+3hy/jutGPPgk0wyqB/ZdF+qoFbF'
        b'6aJv7MI+br1I5I2Nj7aUnqtwYQzgE+9LvjvnTHYZtkDVYj3Fq7Wn5hvpYtFMc2h12J9MzxSgEc7uGnjIa453TyzVHPKNGxn+6ygoG8XhXx20d1DCwRtiOLR/zSD9Zzjk'
        b'RHDsr35z39WH7j+a/tRB+++NIfuvx09W6HXAOEbV9uECO2Ckp/cGTD9Qnd+Lc4Yx4aTXKX6OVs4odvBomTM6Z0z0GPXho2zIw8deQgv15zLv1/X2fuw0Z7MXZtIjMeV5'
        b'WCycMDJfx4/E6PGJNXTAGVkStmKrMT0+YUc6JlAtxizowk44tZYzUh8YB+XsUMeDdKI/1PU92el9rINn4AYe3CmDViyMl2uzvW8SXpqqoEczApZSXoEqKIS8eexcDk9B'
        b'PRFtmlO0yfVZgWTdAIegBKpZDZbgzQ0ybKMnMK0CXAyBc1gykt0xwpN4S5EsohjCAjSYwkE9OMYyk8yGUhltC6ynyeURQegm5vE9+CIUb1NQqEQ8LBBZqQzy8WoiOwKy'
        b'3aNNG9Nk8cwtPpVLkgSWiTY2TKZnXjSx8wJcsoOjk6P4Rt8ZgtXqKrmS1ipchy3sEGzjGLzAmqtPK2FDchK2BHrYUSs7aSrI2UGmSikc19s7bDFnwWiB7lnTsXS6s1QQ'
        b'kcaYuBwPYCacZNQcjnAc6PlY4bqkHvZQBrxSZLdq5Vosn+4VqCOsxuPa2ArH0lLo/FmEF/Ds9FWsmC6CC5xazE62grHbBo9AJx4iQ9lJcCIpl8b99Mcff5wfqUUZSqyF'
        b'6Sn2zw5TCCnLaKOVcHLNQgWWKLPDXA9GAl7k5LXaBvNIOQJt5Fiy1sOTSkuFvlR2bwugo0E73jAYM/azQ1aSzYll1INC8zk6qKhs5eTvu2qGcz8EcjqgrsANA2zajbUp'
        b'YTSV01hqbkheOWRIRDddLTywGs9oY3GQ4XJTS935AXADbuIZrHeP2am3BiuiR2zXxy7tHbqQr+dvAA1EPq52xpu75eMwd54jntCGY25yaF44AytGkpFSBmUp1LaA1yEb'
        b'j2phOqYbCi66EmhYDU0bsFwb8jAHym0hiwyqEigOGh27Dy7hgdE2E+DmlgmjoZ0M7Wxoi96NWRIXG1KQonHYuMzMV+LJ1g1ONmtmKZohFnQbpscseMN1o8BO+4mEUAO5'
        b'/chmb25nhK/q01C46qEinL2G7bIIvKnP0vzOxkMoFQRnwT5J/29pgUIKPb7FbuiMp5Wo0BOsDcjFmk1b4TDUYSeeE7kQbewCVkL9vOmkU46EkglbhydWT8XzG0ixDwwP'
        b'gowoyI2hZyo6m6HLJG0yHGI+DTpQ5TMQKa4HXNNx8NIyHU69YKBWTlHnyQS7ooft0IgVQXIRI4TBs8Oxgg4Dsntgsac9WTtIL4/QlZJWczZYxBojcTpc93YYjDlXNqI/'
        b'd26+3CAWjuG1FOo0NwGzrAY8TYaruqs1Cef5cfLIUFI0Rp17ahqW2vlBN9ZisUgQQ7HIDerIukJdgsjac83SzoO0XqEvnwROXp4OAdyHo5e3AGRsYmfsRCdMpAvBygCH'
        b'NWIhLcg4DQ7aseEF1esD+TG+5yqlSwdXNYYvXOPh48+q67hKNxXbVnl4+frZO/it5rTDSgcC6jzAlmssDBgGF6ATTrBRoOMtZmpx6OTouLdC/cnWl0I3JyD9VOytOuTR'
        b'xQYx5pK1MBeIapMSQCUmkmNpoL/cl8PQr17by1GFV1EgQ/8yHCCdexgLN+J1zLUmGu51qPYYD90e46dDvVTAJkw3hYpEOMi6OhJOkVW2GZuN9XSxSW+MMTYnb08RCeYK'
        b'if8qqGMbwBRDSA+kq5eErHl19FSsmIzDKricQiV9rMarcMtbTuZ7sQNTt/1I8Wz6RAEIwda6kKG/kyU4EeoeCYSiICyiPENatqKRkAEnsGQWX7gL4OZ0WSqmhxmJSIZH'
        b'yfIyhuTFdqm9c0hZWxTYrEMa5KoIW8c72FvJh3HPiGo4uRsLfMhLrgKcJwsOFIzgjVupgwe9ezw2yH52VbZBjNfwgDkfVTVYu0XzTDhEH05i0xi2Fu/AtlRvzJ8Gdfxs'
        b'lewT19lbI/3xCHda0BKkVqJlZIupIvP2CMuTlLOeER4zRxC4TFr+lKWBiWQ4pk9Nodq/OZw12oTVZBLImfpPkfr5sacW5abWisbLoYy9yRnK13qr9hEqnR0Xr/eG8iAo'
        b'YY1pLYcrdupDOzwOxQYxEuOdcJ45vGAhEfOucSYeSk9wJQTO2mI2K3+8tR4WOPixM0ntYDHp147hmIGl3A3pOF6ywQJHRlA9S+RGGZYXkQWedoM9ZrvRuS+h1cbDcAvO'
        b'O+FZdmvcWD+SporVupnsjVeg2oc5Fq0jA/KYqqRkFJNJrodZpFzj4YiWHlzfxjbRCfFkOSugmrwWaV0ihDgN1EB+kK6DpfOxkjXBCrzKT9XlZJnSmyPGdicy4zLxdGyC'
        b'a5WgoFDIa5/Y7x7YEf/GYpN7wWeqlr3+ivvTK+zHzTl0t3yRtXu+teeoastL1qLblUGOovHLMlYJItvA69b7rVMWTkw8NDek1DixvN1ujrz6dNp3b5289/rkixWXJnsG'
        b'FNlq3ag44fTUCxN+LBghy9noN33HJNufPQ+v9Yrc9OER6z+aLQsC0v9YpGj5h9+X5t6pn1UO04pd4f2TfWuV9drHl84z//DrnATveY+s/WHdyqCnNpq/faD99Tfejfih'
        b'qeFwSsHcIvvg/FZZ/e4vXhn2eFG149xdb764afJTz997b8RLu+/uTXz2nbKUOrgS8f6qNzMbE2znPSeauufJ32ovv7Tc4tU3339s15wnp7xjtW7Nt0vKf7d9d/Ev5W8+'
        b'+fPuoF0107xfn63f8HZiwP2XQiZPP3b/Qv1vc+OX3du2TO9g3rmE0Y6vbDu25MulP2ptcnvjQsybsZEvPFKZ5z7vyS8rP/71ym+LHe698s5r51zGXiu/981Y2xVtphN/'
        b'wW/CnYx9pL8ef/9exYtx+8/nX/nCcNt5n7C9T+1+PT3v9scvPGX52q/6T6/QfmNLzDDjTxeenhWgX1yZlq23vCtk1G8rvrT8/EMH33ecK5tbN7g3p0cVOpx/Z9j7Z9Ye'
        b'enyDRUTxp+NrvnvUwHBud3Dhx29++YPupry0iONZnT/7jUiOfUtn6vGjIdpzFy94dq/rb49tGveVn+vy39+oi3Kd91Za4Tf7Te6u87Sqen/YgtjID46eW/DZixu3nQpf'
        b'VhXXuOJe+rq0ZpMFJc1m1ofHJm//wupO8pt3fP5p3q23+27Ot61PjPV/d3vmWudyV/cTpz8pndf5eONvm6Z8X3imfveF2lOvBuTsfH7bvbdcv6uve7Rw57o52rVOM95b'
        b'7nnujYNXcGuY37qQTx/1CV7x1bKt90c0HtP65VFr+WSlVwuW7uvl9zAshnk+4EED5sCB53XghLe/ji93WVlCdrMC5o0xFoqgg6xAO3yVCxC2YSFzMNiJHXilN6859ZMh'
        b'C9EVXXvyNp3lC2fE2an9IHShVQyX5KnYvJV5H5BtqajX0mhtxRZGK7jM/AviIVNXc10ku0chWRkzoYk5J+yaFaLhxkPkPe7JI9vAKuQ9A6p6WEXEi9dYTd7Nc71qDpl2'
        b'to5yzCdKtd56MVn8L5EZS3YvVmT9UVhsR5ns8uzJygTF4pV4wEEH29jL0/ZjrTcex8w+7C8u2MmIW3bt1KM+F1R48VcLsdAyT64tjPOW4pm1q1nRt2MXtNopi6ANdWLI'
        b'dZlOFK3rrARrsQFP97DPiInKU+gQiS3JVHaBCsiCYgUU6W43xCYFdbZTOtQIeFLTpwZbteGWC15kBwZb8eBsu972W1NPSSJ0QSWcnM79RYqwOs1bZTz2Z848wzBHYrOH'
        b'iKytoWwYWbmTshSYeziR3nZgJIQ6grG/ZDOW4QHOdX9kV4ydvz3zi6A3kcjBMrxFFkVsX8kqt2mRWS9JAzqMqFg7kt0kIuctyO/ZMLLhIJxdgSX80OMUnBvTz8NLIHvD'
        b'1bF4i9koguDWQkZYp/SFecR0BBZPYkZyvGhJxluPjQLOEyFOwzSn6eABOXCI277b7X3VTkVppLWoX5Haq2gTFDCfHiwZLu/l56Lh5BJFxkA6tEIud8GqJepJuR0p8lFH'
        b'uZedmrvugCQBqjZzt+2WwJVEelYR2EGmryxejCeHYx13+Kk3sOrZ4zx2whWy6ecwQ8pWPLxAQyLANjuosiKjho7beXgMMjXlAaJlt1OBYM2mZEr7jplSou9V4tEhJIIy'
        b'qOGVOLh5GCmh0q2IbeAWeFAKFSNN4ezsZBpBG4qnRQ+2B2kYg7CISAp1eCx5GNWQY3Z6+ywM9SQrUYDINgYPsrEhJ/P0Vi82vAWYlzZ6q9zg3/GJkY/5L+Kv/vmPHnO8'
        b'cR/wSWb0+jv56Gf0mkYts7qMDcaEMRCZUEo9MUdV01Xiq1mQ+/QuNV5R9DaKAS4l11IlbbER/0dSolem5IqmYcoo+UyoZw9JwYDFhlHMNl1yx4j9pn5CRiRt6h2kL6Yx'
        b'v/ynB1tWTFIQs9/8h8b1UvYaA2VaPIhPbUbrU21NtyDussOCtMzoxwjmERS1U+1NoBHz1GPkG/5/1nsqpyJTdfgVLSHj4eGFMlN7FnFQXvKn7aC2xteW9iIZHKqR5CIW'
        b'8uU3xNEnPfwUMRjdBx99qrwEXhcP4CWwJDqZEgmGxcUxkFANyl5SqFhamrC4XtihHGMqMpJD6IVZx0ft6Jco9y6xCQ1duS3ZMz46NNQ6PC4hYqvcUYnzqvI7SFFERafE'
        b'0cP/tIQU6x1hnN0wMpYSEvanE9YsRGw8ezCahcgr4yqjFDzYksP6WVOwIuvYSMXDcwfSyP651p7s/J+MP0UsxVIl+VBfgDDriBRFcsI2nqy6ap6RoaFyivsyqMsEaR9V'
        b'e9DL2Hjr1NmOlKV6KWnGHbQxkzeHJatL2+OVMWCKyroxgFfmQMR9H0gCFO61VxOpwlZjkhJSEhnq24Apkqonx0akxIUlce8OJak8ByxQWNvQgHF70gQkW4YjkpZI/oxK'
        b'jnCUs04YxLuDNmhylKpflP3OfLvi+5JEKns/MoEFzSZSaOCB0uzVAUOQLIqEgUgW9bmJHIsjdVMoV53aSm5kYM9N5DQEaelozFNFGGDu6D5BBllEjT2UQhnKlpliltJY'
        b'aK0roSbJzu3OWGZp5WE2efterA8gks5VNyh7ZKnneL1ksqefgwbdBX72Y/EUnsNTy+DGuF1w2cQZbmAhM+T8aykz54U+Fx3q9U10Ki+NzHUS1ZmhcKNvIOXFLaFBKjQM'
        b'SEeYsEWKV/CqFnt5chIz45rYe4XGOYfbCbHNOou0FKnkTsavhpOfvmmY6Wzu/u4vZ4p+HmXtFpk+I0403PDZ8lKfzDFPV+s9GyHTi9j9ovULY/fOrRm23ualqpC/7204'
        b'+NLJ5b7P33sh5INxrv+cenBHguNaLZd/dr6TNb4o9efxdWvOPnEz7Prz2yb4fPTKSxNT60JW3hnrUhn8+8EFo8+0bJPLmHAZCM1ExOvRUWKwWume/chkrqO0wiW4yo7O'
        b'p8JVqqXIY5KZxdHft7e04Q3lDxA4aAQLc8kdGwKXFdRq6mCjshYNw1JJBGQSUTcH8rhQdhoPxfdWZEZBRyrULmSSVyycnQXnpdRpXe2y7gOlvNAtWDNe6bQ+LVW8V7Q8'
        b'zYkzIV+dhreI4HxGQ9J3gGbMZ0KWszlWUd2KyOeVvfUr3SlE1qbCqV4kHu7t8a6STKELD+0IMmTC6fztowaTTfEIVhHhtALKVCdhD3Li0KPRc2yOMnHEZiBxZL/gSkUI'
        b'KloQEUNCxQ4qcPQ5xVcn1JsW0aL33j2AO4dF7z00ivx5nu6h1gPtoQeEt00H9yRQl4G6ZZKtJYTsLWrQAFU06WAOfZJcyaCxpKoN9CfpABtoYFS8EtOzN5B4ioJvqFFs'
        b'SSPrr/tST7dADXDwwXahqPDYCEVIRFwsSYWz2KrQkqIpumHEZkf2hKM7/XRjjw2GOa6RqrI95jKXQHu1TyBFwVVEsWImJEXSL8j6PuD6q8RQH7QMjstX+4QyhLSUxLiE'
        b'sEhV7VUNMmCiFGpTjXhGtwalP6wiJTaZI5mrCzXwrvDAUrm5BYXa/9VXV//lVz1X/tVXl6zb8JdzXbbsr7+69K++us592l9/dXqo9SCy00O8PGMQr0zPaE6lwiWZqEh7'
        b'a1vl8Lft5drZ2/eU+aQNLHoM5lG6PCmMAUr3jOE/4zy6lgqrfFVIne7o3Gu2MKdXDuTKpxPJMDU27K+11NKg1QMUoYflmq4xvBx8usVGDiFfSQUNula1fGXGSax/FPNj'
        b'9VDPJIPvY8P4sTqUyLEEz8UpZPQkvlKACinWMwP/QjiUgs3Ozs5aAp6zE3sKeCYET/NwzAPe2GU3ycXPkR7MHRV5b4EWfqh/Bc7r2mERXPHzEpNbGSLXJdjN3sFq7Jhv'
        b'J8JGP2prgFzR/LWb5FJWBq3QEexgCptIVsdsJZaiBaP92ImIrYLstc3YkIzt9IQDy8VYLhoP3dDGy5HlEqWQ4LFpZF8TJQjQTsrHUnRdFKPANmOybcHJ9WKsEdlCiRV/'
        b'pWAMduMRIvYd5QfueEmHH4PciIVcPOzR4xtRiJnYKhfzc6Ny25k9ZczaQMsIV0kxaK3XbvJUF3IxVrAyeoxmBxaz8AbUKYuCt+AWKwt2wUlWmD2WQYqpcEJdfDgBHXIJ'
        b'e5GIQ2Vu6hxt8SDLsRpyuXfCoYWT1Vmu1uOtchDO8U5ogPMTZal6ZABg6wiJnsgJW5VnPaRG3VAqM0wypr6mkC6xFy2Cq2PZvaWLIJueucmMRIIBZEgMRDRe6mzKOvre'
        b'kTUbvKl4G8icaulJLpF3BayCw3uIOF1IvVSgDE4FkT/KsGsEXCDdfZgI1GXQZaqF5eFahuTDl2RQON/ajIiFpsZwyR86Yx/96ZpY8T3J4aXfZav/vsDvMWcTrXcqts86'
        b'+XmCxaRJc239bjv8I/HAC/qPP5nt3pjtJlo6bazW5OwXt+suc/d9VuSqNdzpKYsbSdN//zDNfl6Sm6GdfNFTc1rN3Z+y+H1CaX55TN57wdXLX1r3/unodWbPptw/Otms'
        b'46m58XMaul+e4NvwvCRBa8qhF1vOv7LMy700dG7tU3tLAn97bu8521V7f5ieHK1oK/wjP3JUx/sntE+e/8Xo5NjXxD+ITpZ8+KVO8HvfO13O/mNJQsfzgRu+CHzVbUvU'
        b'B9m/jtuz13m7YVTIkivv3zh37O/PfvPF3+0+furSjosb/pXw5Y30tg8LrX4W7V8fmPad8cGS4O5V4+XmTOBNwCpzDcO8zAUKqWU+FDqY7DoaO+GEyjRvh/kskvUklCZy'
        b'C/uNVXjCThkGRwVqg2BssJforAJ+pACdkEt0qvl4UBkgu8QMLnD7bzo2WrIwezI0TydLIUuEmUl4nIcbXoIz0NoThRo2XzpHBI1joYvL6NWObkxEN8KjaimdBqOX89sF'
        b'1CfDjhrtt0AGlYB1sUAM6dP2spwXw0XoVOBJLJdhKz35LSD5+cBpZnQdTcpbShIoCk+cSYERcshc9HXnyWbAOXK3AM9DS+JMbXKTDMFDZBxfZ2/GDIfLUDAHMxJn0kTz'
        b'BDzsghncVH7VKkoV3enn4BGPZcrgTjJAb7F2Sk3DSgWem5tKj6KhRsCTOpjLkt2XCocUbmTOFkIuLVApUTMe2ZBsxmaaZYRCzz3VSIu8c1HAU3u8WGIRY0MUeE2MbWS5'
        b'FcE10rzhcJi94R/lrYBsq9TtNJfjZEmTrmeay+j9jgq8qp26neQARwXMHw481haPGHkq8OaC/loTmeZleH2QKMYhfI+lCiIUM5VizcAqRShVIqilkTJeS5V2TYoDyGyZ'
        b'yh8DFmGoL1ZZFtX/iCqiK9o1rLcbMcnRT4VEwoIODTQF6aTo3pqISFWHWLX+Ea2ODtxMrm4PoYTc7uXO3L8cJHUJy8SP/j+iD7DTXWmIv6ffXVmI2+qAAHc/N0/3QA5g'
        b'qQZ8uitLDIuNV4YOsvjFu/o9sXXKSEf6cJ9wx7DewFAMJ4oaJZlWxWrFG8jy/yXLeJITVfkkSig3XR0TCe17I4mR1sjFYnL10OiSYhMTA7ER5SqTztqpKzIfqytirgLR'
        b'WAuXqMc/tO3WOL4QCZYrpLHYDod7OdYaKH8rbEW9mcsofBWHrjolVYJX8WsKYaVHfug1hbKiQFb8+55rE4oUGWnGrs0jh6uvLSJHkOuR7HpUpGXk6Mgxp2SUEy1HO1oU'
        b'OTbSKkuXIlWW6ZSJImVlBmW6Zab0J3JckU6kSw6FxtImGuykyMkM6kmHcYlNzRIibSLllCuNvlcmKxNHi8lbZuSfSZlpLP/LlKRmWqZXph8tjbSNtCPpTaOwWzTFHL0c'
        b'wxzTHPNoXQZWRVPWY+6s2sy9dVi0dqRTpHOWLkXGlAobZMzLe/pdUzoP3BiDAoM4i45Kuj+tlxzZ/wElFZjmQ/cdiVA6N1aRMFeRHMl+T3N2njZtLpVt5+5URM6lc8PR'
        b'2dmF/CNS83S55K7Uzz/A967Uw3OFx13p6oAVK+Wiu+Jl7uRTj2YZ4u/ns54sYlT9v6vFdMm7epzwIpZcakUTjVjxZ7J1odlKk7bTCZVEPxR0iko9/QI52uGfTGsOWbF6'
        b'p5W0iyUYuGzNkvtLNycnJ851ctqxY4ejInanA5Xyk2ikqEOEMg7PMSJhm1NklFOfEjoSXcB5miPJTy7uSZ9cU8StpBUsXPiuno+/2xKfECL8359CC+221JOVkPxeGZZG'
        b'V7QAavlVJJNEHZ1nkE+yuG3nocYzeXI0+PCuQaCn3wof95ClS4LcPB4yKRey/G7vVeX7s/u86JaUoFAsZVpJ7zR8EmJ8FTEsJReakrgnJVKyAzQt4z7tcd9y8ErdHz5g'
        b'48llvVKhw61/sn2+mDNIWn2/nsO+HrpUg99zuW/3J5rnrk5kVHRYSlwy6zM2AP7vgju4TnR4OpTLiOTjM0nphieeErt/XqmIBX2EO8uVQR+LTgpSucg25a0hgj7u6lJy'
        b'0mQy8gePbKI/Kzh2ae8Vx1H17sPHEJSQWi0gV4oJA4sDB4THe8URDJWrXIdv3ysH2MMD1Bs5HcufUByzIL9ekQf6quZdKCgjDwQVoSYHNYvWV0cV6A8aVaAyZ2boDGDO'
        b'9OTRu7G7ojSMmpwXhx8v0VV7CCNmoIq/1jqRsRcwGUYxt/+DDtZ9Zpa1DVmyh36MzqYHPjHH2sZWEUvPqlJnO86yfYgk+QS1tnHzePDDymlLH7a3flA+g09taxvPoD/1'
        b'hssQbzzsMkCT6FvowezFSpsXNw7xwGolI5IKk3+wN+kGy1/rO2wSk2ITkmKT0ziMro0t3bYp0xTduG0HNiHa0u2cPkM3V1tqL7alu6Kt3LHnOHWW4zRH57nKRwZOpufk'
        b'1Zk9qky15+tZ7Gue9GAV40APyqoNAOLA22eqguE4DNo87IRibu/IfDbJBoZkUEbWD1qmHuyFuWqu1f7gChToQH34PsDZOv2P3GPEeNSEz0yn7OA/KiyZDiiFijRMA6mC'
        b'Hj0PEt5Pza8knR1hSUo/AQ1OB9Y61oFRUbSuKXEaPGQDJuW2JMh9hX/A+hBKlOMf6B5CmVICWSnVZ/ScHW3QRuKLEG8fxmakBD1R9ZtKd1Majgc+0u4xJrMDCp5Cj63X'
        b'ts+aYjuoUwDroUQ+TxWcW63PEmPLa6d6JDZ+YOwBjmJBRFgVdezmsHhr99UBgxjF460Dd8Qm74pKimMdlzxE4fmCOMhcIhPGMzksLo29OPgKZzv4mFXCb/AO6UHloCNf'
        b'2SVqhA5+PjVIjZK5j4MGznavd3thqwy6arGU+h0YkOZRikwK1fDtk+7AfaKkG+zJl9E8hkfFJcTH0JSGMKxTeUSvn/xk7Mfj5hpXQjoe8cZGOIHFWCoRxHheZDMumdmi'
        b'faaIlS4NcnPm1ACn4Dh3a6C3Q82xVWE4Dq6qYECvBmEOx+es371WlorXMZ+ox4XUqxObIU8qGGKWGAuwYlHKYvLUFLhu5e2o7akRp7XmAXiZvlpeYmEmZBphlnScXMxj'
        b'H8ziqfF3y2pq/qW2XxOo5lCeUI+5MsO01dRmTO3F46GRxalgYSp2aGCi9kSKqQNWEg0NAygqqo2D32obG8zHQifMt6cAmBxs1YHa8I6RDA6aiSDHbzkzX3uaY6EiNYnU'
        b'tomDd2KJAx5hJxhPbdYRDJzPiwTr0LgvE8cJKfNoM512Ga5G8yz0Xuvh6OWLeaS6TgGY67PKQxIAeTSqDTvgQtpkAbqhaapUhsf3wOXYJN/3tBTUHjPq87cmFy3Qz1xs'
        b'kr0jOmX/S3NLZ631Gu0xfZ1NVsMG2yyPdy48M+z7ezf0zzg3e07/em/Jj9EznHVl9dLlWZnuopKk76pvvd8+IuOre6eeupbd8FpRTIDthY+37fKYs+qrf0Qlv9eUnfBz'
        b'qMUu06rN0+/N1MvdP7vi3fHD3v10/2ybr77eWrbl/Pcdpx8Nnrz80xHjvvvbhl9udEa/lnLhKVn4c1PaQuRbnL5z/ZfckPk+ROIZaLBzdPBwEPv7C9pQLXbGLmjnhsJj'
        b'CyCPgwxj4RZqMbanPhk6glGAxMUBy7jNtzIcSuz8gs00vStSvY2YKXmx4xhNr3U4D53cJcTagFk18RrUYqO3P56FNqUtWWrKDLMWUAPHvMkAwLxHND21l0m5Q3wxFtnK'
        b'vE3d+7qv6yaGcfNsF1TgcaWBFs55OvWg7xkoGIKGfNoj9DYUwa2B0PyweRe2sKKIdznZOQbhFRXwogp1cWkodwTpwCPYSapng209uJAn9y5nNdy2Q5fk0i5bRQZfC7nn'
        b'K1o+jlt0R42EfG/qXjzPh9Q8XOQCpzCjV3S//r9lZ1NjxM0dTGHaYyrSV/qeUvgOKbPJStk/yvNrJBaLLAdRb5S4aH79/TuH1nSG8A35C5BuvkNqaa1WD9TSHhbejbOC'
        b'3NUKoZLsEAhUReSKg7sNlJ2apdjxIaTl/sBs1PIV6LEk4K6UspDelVJCUpV+2durlvusUhfWuzpKFuukMlGfsHZj1d7jIajD2rl6aaBUMA05bnaOcbTxQwSvq9TMSwOp'
        b'mUsiIxW92ZZV2+wARkK1gNZfW422nkvFx7mhahiR0AGO+O2V4o4a54p6TPZ3MO3LKMhpc6nm3iPEJtPWS1aK+A+lPCnFXjW37IP0J05Cxd8dgAI2TGEdHZcQRo0J1ozv'
        b'VEnvOJh/TVh8L3K1vsyxg5Wil1IxELVrctROLjEnqxlRt3Fvz0HcN8kzsZFU3Otpih56Ol4HaxvGj06rxsS5CQHLHR0dJ8gHEUS5lwRzRQ6jo0mDDVmdMieC5AJyz/0B'
        b'01O/08PrqBwCSg+u3iyPA6ZhE+C+3J2e6riH+K32XeoeYG+t0ls4EeagXl/M93hwItSERO6LPUQKOwdSBQdhHR0iOfqfWlOkLTyUIqfGXlOO6gFTU9FZD6TzWZNWcQ/w'
        b'W+LTX78b2F35IXU+FdcVbwo1ITAdsMpxQ+cFUZOjGNtzaKhfQjxdKYbw496Z3JM7I46lbRQWR32n6QKhHrrRSQnbSFNFhg3icB2Xwk1rMbGpUfGqkU+mZiT19rGJSIhX'
        b'xJLmoimRhotl35JWHrRgPBlNg4Rcs5pKeuTwLVERyXw9GFgFCvR3neXsYs0JXHl9aBnslZicyvoyCwGdm2RRHDCd6JQkNtfYbOdUrIPqgXwnmmsdqNS7VDTp1CU9jeQS'
        b'F0cmX1gS1774wwOvLQpFQkQs6wS1FpiYlEDZzmkrkqZVdjaZCHzYD9yYGoSD1n5EHwxLTIyLjWB+iFQhZ/NJ08V+4LnjpmRb76E0pZu0tQ35lNtb063a2sZ/dYCcdgbd'
        b'sq1tlrr7DTIPbTViBmbJbR8ikkHt1LVEvdT3IR0ayllUrYzqDqiMjvNjbjz78fx6Ir9jJVxQu9Fjjg2TfZgS9bI/UaISZ1IuirjX5KM5FwVmTMLTCkNDSPdQqaFYBS3L'
        b'mQroNh1zFDOwu8czynUDU9X2QidRT5uDXdSwLEf9ITOIEwKcheNYKUs1FCIG0F6hDVpSvMljadgyFVkUp18aUQwpeUaQElLA28F2jYe91+rB9VjOXVDvPoxI7eUTWZFm'
        b'YOZI5sWEheOVmixWpqaspeJhEl7mWbGM4CA2PExmPQwzq2zUiBNybWGuszk2RMNx1kTOAWtkhklwDS8oteQgbEihXv6QNTLUmwHzOHj5Uz2Zp6GFhzFbf/IoqNXv0U4X'
        b'YzqeIjeqTCEbqoOgMnIV5C3dBycgA67M8aLOdeTq4NadUAo1S8M3Qf7SpNhVq7ZsSpq8ESq2bjYhmtaCMXDKfjgr07RtIhm2JW5ONBALYuwSOUFjVMpqquvjJUwftFCY'
        b'NwryFsOhcMjWLA1egKvkmyoso39Tt69QY8yxFqBu1bCReFKJzHALCoNlqXpmYjIumefZDaxIoQMXDkti1MYC+Rol8k5iSkoQliYaGuPhIGVze0Dh/B5TArUg0G5RAXOo'
        b'8GkgHS7pMhc3I8y1IIP1JranULnbYStcHxIgib4V1KsjsRVyDBPx5gqsSE6hhLVwFssDvDUphoqgbiUbmiRVb4YSQobRES2FF+SbkmGdj0cCIJ0CyEO+CLu3G66wXJVC'
        b'PSagIByaaUrQMalXYh49GuyaXmlCtgzKzCdjzXC4CBcshksEqPClsCLnoZahXxpj6YgBII3EeA7LSIlbgkLmk/7JwCzSwMz/Dg6HC5gTYBAwC/I5Es05aDfVMNz4eMq9'
        b'HBw1aULwBNaroZKUBTPsPTNJs51OMYVDZJ25nEIdibAWsjZxPAcsXOUxVPI9SU+jZCADph7gZQ5dUqXz5Y2p0E3JXEgdO1U2ITLwmCMPAzdZGRbVi8jGAS+peWwgO4JS'
        b'HcbOMXbUUlwgitXecW/4rroZ/9Jik7fG7r75w+m9xzYenphu4+5llTHVQ2vBVPeJpV3/SP/cXP6K4dRqz8u7pTf8b0+0trV9TFI9/xtdm8lvfznHtCjm1tlRz995elnA'
        b'qtFbjlWVls/89oZJin9dhfan5isDLta5/uwVc/nFbxdNuFQztV7n3uTDr+QHnt1jHXNy66zgzltfn5i+4tmrU9vGJxnN+vHukfOO5dXPa/8r9ka9NOL6109HPZs5+wss'
        b'+kDv/kferS+EzGjKuPjxN6PvGm+Oitz2i3fTvmmX5t3YN3rB8Pn+X/+aHmOx4OBHjrG/i8dJu/aN3ZtT3NbZ8b3221ot7t9P+VfylTe83znvXvdN/fPzor6+JzlWtzG9'
        b'64cp1scem/9l3ueWG4dX+b9wcfnZ9xv9n3rig3M5xiOuhd9b8P2Ryhz53eC61x//TJoy2+87w2sfuN4z+HXHY3N+OvtOSOG9H5+OuJPRlpk6d0va/kdjMg/+PqnmmVfk'
        b'3Z83nXRLbzu3b/zOORVejtnrzhq2NYd3BY8tKq9f6fns8CnVHz77XbZkYvmd+++L6iU/er6W9/z2yVveyjFcu/rNtOf3GLVvKH/rVuDjf9tvsbTxx5fa5RbMdOSFt6DT'
        b'WxMAABqxaY0kDg7PYw8kwE3Sxb1IJlIdGNjCoSXJFHdLtGukt78DnE3mFivsCGaWMG28FKnpdLl2BvW5lAVz3onLUmYk8oqAnB4jkQuUseD9pHV4lXGSwCmsVPKSqDhJ'
        b'AqCOmaEs9claqcF7sgwrGGDCNgUzeKVtwXoNNIfAqSqDGDZgKXfAbEqerxkEdciOWuqgBdJ5CfM3YR7jUMpy8NASuPMm5kMlqxxeM8eLNOL9OHb5e0KdVNCOE08IsmOu'
        b'hknY7kjpQyj6CkeZWMKBjhfATbyh4SVJLXDVeIhxYByXMTOcL7ZgLnvEiqzAA9nhtLgtEQrGjNYMgTeAM1BkIhmehtXclbOUrJY3yBP2ZEdroURtUnsRdEIdh9CAI1gP'
        b'GvQpW2JUdrxRLrz+x6Aj3s6RlLjZgQd0UVvoDTjCijlsHJR4+3hCnlNfcCLncAe4ru2EWVN5Mc5I9rDBQ/YYfyJLGG2E9GWSBXpYx+yteAvrJ9s5GDlpxJph6T7exmTU'
        b'WUCBExYY+TrISQkWiK3hFl6U6z50CLPxf8dnL1wF25g7mC1xv7BQX2QgZlHqYgMRjWk3EWtLdEWmJjy2nMarU04K1ZUu8/TUVsagm0hGikeS3/SfBYtopwwV5iJdLSMa'
        b'iiZmlkqxkciUpU6jz7XFuyYMYGPrE1o9gIFyMFNZ0rHeLqMP3+iacePHBggeHyBuvJRaLicNZrk8IHxro2m7fIiKDuzfQ2lVmEmP+4sI0dpqTx/JkCjzm+XS+6H91IWA'
        b'qHiiqSoeZLdjRgKlYkLV0jCF9TpfnyG0D4oaYdVP+7D349RqRfpk6mkyNfYBjStY2wcwDE6k2mlT6MmrhsMptQ1nOGsgy0Jrry2d7ufWEWxHtxGYqO+yDS4oUqE5uOeg'
        b'CLu0mPLhqQ8NVGBIdsR8J8dU8uHlSVbHE2SlmLRJazacHMcjJZrW0GCQ6VAmozCPVmRZWgUF7ExvNylCDj3TK46Fc+ojPehy5Hx+0yXCYzqUnzbUfpxPMC/PCPkkChgJ'
        b'B/c6k20HzwjQPRxvMfBHqISaXUipf512OghOIdDEI567nTxkelDhlEQB12qp0nXEl90JlJHlT27rjO0UYCRNhOlkn+Ga2sk9Kd506/DTErQtxESRqjbAS7tZCXzhMJwO'
        b'xCKqjGX5QSvF1ewSmAxlBafWU2g38s1xJbwb1mkr41BSoXQ1UV+WwFGl9gLp0SnKWNxiKthiQ3LiThprwiJNMItIkixmpmrbKh6j0h5Cw1RYjEqWGQd3O0c2DwrmbQ03'
        b'EokyIIhsk7GcR6+0U/WPaWmu0KrS0i4lpNCdI3bR9kAowrLVWBQFWVhOgeN0/UXYskuXNf21qBKh0nKRWHAOjddaNZzrtI9NnShYhxfT/gi/HTqNf7koxUP42m2KSAgN'
        b'3TJj436hF1OxetbR4caYii3IPBMqhT2iSCFSlC0eJZxTcxYT+fETik9OY1eXRCb5xMZHqViLpXH0j/7QueQjWFtNXczmhigulGGb8/NJPZWwi4dZoIQoYNYc7MC87bsg'
        b'bw5mpy5eHr3dM2lfPKSPFfZMM4HGVXCaVUt3lIGwbtQMIvSGGvxN4szrWiYfIXg4baBK/fxyNz0uFY82pCB6zfuhgWH+aSL+wSWsVgLiTYYjVE2Ea2YqPZEIIVWsD+dh'
        b'90hyb7sTUZCIFGQumoc1eIVluClNW3jMwooxWt4ynSnIxUpOSzizgQwlMntaVGOpiIwyFi1RH7aS6IYuM5S64TaSC/1+xAJ3bJYZjoOGJB1BMkW0IElPLmLTxiFqs8Jv'
        b'mjaV+8QykTVkLPvLfUjpzpNOcA/UkyI163TSKdGAyMfk46pG99EpKcPr2rJUbNuNrcZiWgHX4XiNTZ+l0DhGRpURfainsIkVUdjFWmPjBLK8NBus341tOmTKHSFTjghQ'
        b'Vdzp8jwNbaNlWKXAUmEV0Z+usR7Rw5yNMhtbO2yE1igfMvi9xBvIwtDIlqXwUXgSm528sJ3c0YJM0Vq4hkfHY3fsNv9UsWIVqcc7FguiVnsrzFeb32o/+93TdxYvtTYx'
        b'tXLJyjUuzM2oCl/22FrzGQsP5+6SfhF0IcfKoizlZNW0S0UXVt8MjVq1pn3Ro09D9tY1R2Ujftd+9WjUKseNP59+ccH49MdPL/zol1sLf/wh7U3PU4999kn8L00T7r14'
        b'Ze434tPrIz+Yu+bCNvzyfaO4Zz7+uuWnWR1z4iJmBsUd+dtrTSMmhr+TFXnq64h1jq7Hfn3N23bGjNW75v5gJrP5oetcYfEt//zgPZc/PPHrMC33x4Pe+/TpxKom/TUz'
        b'13aE3nni5ZduZMyOXv2p4++jX/VxuPKB7bXRz79Ucvm1Gxt1/vHkHC/8qUZ0Z/bLccL2E+scAmV3Ow62Zm/59s38ezqBY2fWnvnU76Rlx6zOcwFj/TLGVokCx6357DWX'
        b'0DcuxVpmdNR++dyox312FHeb53efG+n48pVH2wK3vm7xSNS8xxKcHnntK9vWxrdn3g14omP9ltvZi9zmZbR+52jx2zKHj1/dvPWawuGnys37c+JHbI0trUj6qLtyZPnF'
        b'p1OPHVpe8fzYnRHLL6xZO2pea9X4n95/8ukzcU6GjRNa50aM3vv1Lw0/TIRlXx/4fMEwn5o1P43+u2SM5+X5w3zyLjRlZq/Ib9sbW5R4Zt135ZUvhtd+fhsyo3dmTpEo'
        b'PI7nPBrnNDLUeMTupsu3O0O614yY8UXloc+Gh1lVuN9UzG6v3Gv+mfMrEXCn7qPH9L8S9o75eFho3R7xZ5deqB37zY8L8v4V9I3RF9XBj7/15MF7602/H5l8aeY+/6Vp'
        b'XY96bYry//G34V82xfxkEPTPR7z3fvGl/lfmv+t++Niu1V/YfJB7L6HwtZbRL0xbs6J9s8/nG762n/DSC39Iavc+7jLz+5utP4W86TPmRYMzn8VaHnPd39Ae+vjV6zf/'
        b'MWl4+2vH0mJPij75/aPGn/7pdKCivO6W7mdBnyaPWSh/7t2siMWb3pv62otxEQmPHB9nUHP87OPzC7IXhnyVsMJ2f3v36c16v32R/Jxif8KnHy54xuq1K3GZ3ct3P7PP'
        b'yr3wkR9TrhTVzXn3i8PdDrvfuvLuT05TbV0zzbpNu2y7V2x+e8fRyLc++VX+rx3Vv0999JZ216iuM51hkidHv/nG594XTtweY/vFwZgDt+S/pe+umVfkuX3imd/ezxan'
        b'7Jh38fqXe7vn/+2RqJY5Z8zT/CbcPZ0U8ObXj9yuee09T3mX75H3Dm7N8Gt+/EjAzpNTHi9/fd6kOwuOBHy+3i9/9O8TjzSdnep+vOhIUtsiOdwpu/n0Dx0vyS7e7rr5'
        b'+8yPvL4c6/ym+3cbRT8889W+V1sCSr769vMFdT82Lnx0Q+nu2KVvbXu3WzLn9i8hQnD1U0n6x3wKHF7UVpj9nlPz7L5PU3auea7gouLNpy2PJMVu2xR8P2rTu8v/yN3z'
        b'9ZspZyvNPPy+iQ3/MX/+1ze/MBwx6+1X98WGXP9qysklvz8xZ//XjlWzf0t82fXJ006zfwj7eUfn9fVzqj4Wdr1Z4vePoE93RH8Suv/DF67ua7H+9PlHzX9876M9kvFn'
        b'Pnm/wVUya3/M8++FXMtdk7f16z8ulddGLrn23OVP//WHaOWrK2rMi+VbGQTGVOs9fShMAqCTs5hIsX42dHDOzA4ohjyl5opn4azKyQQyIZPrdnnQNLNHtWOKHTQOJ7rd'
        b'+AlMdwyhZlBvsiXKHUN0lE8YO0tigqCW3V8bFqRmaszfr0HUeCiQaX+BcCCgH+0jtGGjWknduo8ltNs1SpOAkpJPukKTj9RwWxJXMpuhYVcveELMTXbYRoQh+vYENw8F'
        b'F3SlUh6zZIjdEmrDPcFg3hbjebyscCR5OyT5yel230wtiqQ6EmEGXtGGCxaBUOrLYgxd8dxkb5UtQjtEHA43bOfvZeo60Y6P4S1vn7F4zJao68Gi2WvGM911B55aSTrD'
        b'icjWtHAlYjgHNyeTvfsUS1IbDwRyBLcIPSWGW9qi1exNa6xLlWGuAzZiYRypv0TQwRaxPxHZODjhZcydq7o/ibZPM9lsDCGXCAfQtZpD43VgB2RQBBxxEMeNhdpdsazV'
        b'9BLwBn/bgbTuIU+St7547S44wxK3wHpjha0nFiey0NISODbOT0cwgQZJMnTjaa6Vn4d06PRmOCqCoIU3xXAAKiTQGMKGmBOehzps9sYmfxnU7sQMG22yabaL4cIMuMaH'
        b'WMv2cAVFfNRzhLx5WKQl6GMxPXW4BTms75ZMw8u0jHpyTF9OmqyQtIEhdEnMpq1nyv0s8mw2M69UwQG1fWW4O8t/xGoX2pV2jnJ9G1votqDWC9OREjyAnVDHbQPn7DFL'
        b'5uiNbfK4TVhAWsBI/AjmT2cGqaQRMxR+ROowhGwqLFxaHsusL9HzKTwzqTFtdZL2RqJ25GsJwywkUGEayt2kTttv8/ab2Zu8czRkSKFmQQpruVVx2Khw9IR6A6jEEvKM'
        b'IBhpSxZhQzBPoE3PV+YVg+kOPtvhqgcZmgq5SBgVJF0BjTJWuJXBQfQrYY0Z3iJzOR5vsT6d6QF53gyROt6dQSUaQZlkvgVWsObW3YRn7CjGIpRjhibOog1kc8+xzh14'
        b'XOFpO2KjnEhOUCaCopWL+ei+AKf2k9Ys0BJEc4xlAnRNjOL2r/PrZqvsc/Oxg5roGI5zi4yNPyOD4Qx+MWgOB2CEKjiLl/jotpqgtjzdHMaMTyaS4ZCJx7kH2EU4ayKz'
        b'IXXf7rNwFSmPPp4Qw41Ru/mUP4TX4RCtjK8rHHIQCXouYjjuTWYGE5br4aCjzFFui43rzGmZdWPFsYuhlUNmHoNWbLMjvUI6IIdIesX+pKGMoUgSjkWWyVwJ64YrJO/t'
        b'flR4uyjyHYtnsRpKuJfcTagbI6NoDKw5tPC4CG5CDbbughZetmtkWtQzm1l3rNpkFgAneL1qiK5EB/2pfbTOEswTkXl0XHkXs8gS2OjNbPHukOmoLci8xHhxXRizcyVC'
        b'7gbSPfIke0sfiulg6CTRhYZIbgOrJVpYB1sCiL5sgtcFuAanovk4P4G5cJCoFUkic+owJ4ZbotF74Sh7ceFCyKc21NljekyoaaQqrNtPWEKRws+XTC+lbD/PiZPkNsOx'
        b'RGbv1ZJqOBJiHTTw0hybFc5K6rPM20kk6C8WQy3UxHCWrTK8SinPC8gyy+YnGYq02OZwcxZZdPHYVORsv4Z4eY2CTLSOxXJ9uGaPbdRW0USeHGUitcX6aNZiu7fAUZKM'
        b'8o7WGlEC6at87NLlYfXHoQDavDF/hFgF1Xt9F2+T65i/kx7QpGIz6aJhIjzms0mKPMo8PghvknuRfsnaggjOCFiyEZXR+PWbyJRtdsK8YF0bMknwDLkPZd6s1l7YMJ8U'
        b'2MZrh7abrVjQgSPiOVDvzzfcrFRn6v7qT/YBaNAjWxUdGsZiSeR2qORtSsdNrhKPm7RJN1k1KHI4njPnRLkl2LBG4QfV0Eq3KbKmKlfEkXBF6uKrYOWbZ72CL+pM7zgp'
        b'gmor0h4tXhyltMYPy5VrIjZBE5wlT+ljKxkPe0iP0wlrMZLMD7LZWsBN6kG5RuQAjZDP8l9rBRkK0tmk7DvIL5aF2TqowCMSOGsIB3jHN62CCm8HL2iz4mjkcJ6Mvgvs'
        b'3pgRZOUtcFKZYbEILlrjQV0WcD9nb5osxXAbZOqRRh0vWhINpcphTbb1wwosHI9HqDOruWgiqcAZbrw+bGLFa+OZ4L4dCx3o1l4rmYyX4tj9rTq7VTDtZM86q4Rqh3Iz'
        b'LE6eQt+/6jKJgYUR+cTXXu7pS9ZrJTqy63ztiZBFVquMGDbKxmPXEqUBOglOcxv0MskCx7RkGpK+Go/CdYZxzE7VBoJIx6N4hKS7Gq/pOkH7MjYkZpNttVXGHnXY7mk7'
        b'dpGcwve2SOB8PFkEWQ3PJgtKKmoT7OqhonbDi3wtukwWjGqFn5xMNCiDdDrV3MVwGRrIwKbdKYNTy8htc6xhK/pRERRj8QxWpYVbsZi9GQsH+WoyU6KH1djCINKgAlqh'
        b'flDkW/1F0aOgm5Vx/9JEVR385A7DWR3aJFA9Gpr4sD2xFE/0RpnfgkdUKPO7klg3B2try2wciKRSTLZCCbaL4BKWYRYb0hHzoESG+UzMWQ/ZFCNZEK/yMmLjRmvLbrLQ'
        b'x8d6ichrLWQuWtgz+WUtHsNKWj19L186Rshb5tAOpZAlwVyzKQxT10JPXyYXBJHFbksBs/VJedn+0EBXY4UfNjoRuUEObSvpOm2yRQL5enCSrx1F0ELEU3vHhXDDkS4C'
        b'FWRjw7IgtjUH65O9w2uRQIa/WC4iA3QOK5A71sQofByg2ZM0lZ6yOnTyYql07vC1HBfvzHotmQPZ1IigaCWeDafNQjj0iBlmkx2vgBqiHELcbelAJpP26Ao4rdxTiBBy'
        b'XeFkiw0eDnBMTpeeLrFHYDJfsjIjR2Gzgx+3RewVxZI9thw6jVmxEqEzpC9wcRK040GpKfnsUMKEYKu5wtErRa5H1r6jmEfkNLEYymZFcWnlxj4iU3Gh2RMqnY1t6Mpm'
        b'iB2SObvW8fIdheNrqcc2tkPXTpXLNuZLWReKAxd6O0ITFvuSFTpNNH8kkd7Z5pMBTTZkG92OmUpn7r18mV0fs4CZ4jyX+6shS6Bjt3zYfwfBVvsB9zlQBY+q1U5i1nx2'
        b'rKNLbWADH+vsF2x1GXAwhyHWF5kyOA4KymHOUQLFFNiDP6PLAD10yXPmInOxpWikyEJsIRqjYymaIDZRkpEbiIxEk8STRJbkylqLQgwbic3F9Pck8WKpichKNFJqxOCL'
        b'Wdr08EhkIrKUjCGfFuQ7K7Gl2JSVwsJgJMmBgorYSwZK14S8M5K9z6GM9cUWYn2yLFtKVYAjnBTdmnxOISmMEU3R1hXtGjXAaQtvq8HIUx/c7D2nP6dJU4+hdkC6rA9y'
        b'+nNA+NBC8/xn8BKRrFkgfKmIBg/7+cml5IP5essN+uCQJAULLJY60M3D3dc9kCGPsFhnDkSyUo0eQkuYRKmueG3N/y/wQUgTzVI3UTwdjfSALJr81pVKpUrkacm/81tX'
        b'YmJCh6ggMp/P8UNGMnZ7QWS1X9BLoViYZMqfg+z+BnWog8PeZPrO36CN+eMhr1cIvL7yt0J/aAARSaSu8lpP41qfXMsiDdi1Ibk2Un5vrHGtBBM5pacGCjGPHK4BFCLR'
        b'AAqxKNKJnKIGChkdOUYNFELBRYTIcZHWfwIoZHyRduRUNUyIYbRW5ITIiQMChFBIEk2AkGi5zV1jBpTDOKOXRYXHJt936ocOonH334AGceUR5dPk4rtSN/8A97uSpdOW'
        b'khGVzA3xFLBCCQeSlErH9g76sVP08MAdrjxOctqfQvtQvuT65xE9VNmxsEwXJaJHD4qHhNUoaR/DCQpw9/UPcmeAHpP6gGkELlsWELW9d0y4sxLH46EedlFjXahKdH/k'
        b'YOmq4S56F16u1ysN2kv9EzXu22IDpzVE5oPdcUkqZovZfxQF4yFopbX8+KlkJTbOoVB9RIxpJWsbhw08FMhOwlyhDmtlqdu9oUvEccdO6eCZ2IuPHZEoqHF0Q+IrlEDc'
        b'I+xOtO3Mee95h+lHfyx8mzHK9UVhzlZp0yRPuYhLeAfw3DBqWIIqb7VdyRnaBmHgLFG5crC4qcH2fPpjTffNXSP7zNO/CKhhqkMxloba8ujP172ANQbN+uFQNaooqgbV'
        b'4v9rqBoxcum747UfFlUjktWEwgZQV/3/JKSGamo9AFJDNZ0e+ITrQ0Nq9J6hg0FqDDZvh8C4GHA2D/z8n4C06BuUxeMHwuKp6z+NrRokUkj92kBIqf1gMHr1sxL6gm5L'
        b'HM6CbE22gwf1PAhzQlWSP4M6ERv9P8CJ//8ATqhm3AB4C/S/h4F96D1pHxL2YcAJ/D/Qhz8J+kD/6x9no+UXxBzxF89YwGAHsAQP9YMewMNY5MO93D006Ci7MUeGF7zx'
        b'euzoVw+LFG4kmU8io+zCPg79+J3N0Rsefe32S7dfv/3K7Tdv/+P2W7c7S08fGp/dmDnxTG2mvKDjtcqsydm1FY15Ltnjj6dPNxTSOwxf/n26LFKuxYzLOzfYR2MBhwfg'
        b'DrFwZiIzxkCun68KGqAHFwDO45kAiUugKzdPnZmIJ3t7/+6DanauegKymEElemm8NxZHwkGl2QSPTOTWwoNaWNSLnM55JXdn3rBN5dL57zi0qoPjpzxIClrOg+S1BxJH'
        b'/t+Igh/5UKLVp1ZDi1YPGwqfxULhkw6LeoS8AQLhl5Iy8UD4fjmpo+AnDLJZDhD5rj20626EjsbUkqmm12Iq3un0EfBkVMSLlikFPB0m4OkSAU+HCXi6TMDT2aerEc++'
        b'dyABb+h4dk219v8Xwey9ocCUUpMywnsb2WdoqO3/4tv/F99u/b/49v/Ftz84vt1+UNkqjqz9mkRnfyrcfYgl4/8y3P2/FqQtGVB4NOVUZ9sNMd97WYgG0xlUpHFMMFfy'
        b'YYXpkM4h/wM9MM9fhejl4YVFjGRsLUXVogGpUgEOr50LBXrQiTm7GWyYC5yMh0qoZqja/WHDLugzg9YGPIJH4+GGwlCNO7YFC1OoXd8YDmOTmodcCeyVu7k/tpeYxmmd'
        b'1cMubMWqFAcqRB4juV3oiS3FXA97HvWBuSqa1aWjhZCpukv2B7I3tlKWAe8+cjMNkrXHYl/mALZzrBAg0yEVP72LRfjCdS2sVrO2rl651mHNWhrs6+XrA7VBHnA1GVo9'
        b'fB0dPH1JOk5iaJJNg4KAQBoBYRS3dStzLN+/BS9OWq9QE2+Y6qfQo5cxaZRMt1fKmGuPZVC7JnFaEg2FZcHjUiEUCnSgXIKdKfTYBi+5YGcgfxov0UBXZXcF8bfUBLOP'
        b'ROvAhe1wgoevYNVOWZKRoRjPwTVBMky0ACrxADNFEmE9DJuxfYdCgrmQLoixW2Q3C1qY5/3n5oxRTtfCJzRumd1SIfbtf92UKF4gdyb8NGl1SaMhOJu4P5/6+WOe1sFe'
        b'NaHFM+wXbzc9PHH8P6uTLf8xxsFs0m5nzy3LnjI45T5pmeLHvV/94VQxzUt3+esvS+uS/nbfov34JP2y5jEHXqqO/viHvRlbzNemex545aeDpjqXHvlg9JQppgF+xhNe'
        b'0Mv98sljMzZlJD6R49oxPeXgvXPPO//S9FTSV6ffPjo2zXBr1eLNV0OqvjV+rvy44svbt977aN5XE746Wu7d7ez0x65Zv+edfEbWnjlpb1pEyou/HZV+cP6UbcCvId4H'
        b'A/6x5LlPRJ9/Islo9Eo8f05uws6JJZsmaISAYokt8wmCGijgzgxdprqaEaD+EzlsGRYHs/PeaOiCesyO9FYxYJjiGe5jdhizRD1RmmOnCJzVWncydzA4jhewrD/pNmTp'
        b'6ZIxcYRnfoaNYFUXQ7aVwDiEp8F1dmqfGAZFqSFEbVLqTOap7LWZUEdKq9YMMQNruIPbbu7DCvW7IV/T3Rba8SgvAve3HYXFTG3zdLHjNaATNs9HBEfxqGCENyQ+WAnZ'
        b'3FfzGmRu4zzGcGA2pTKGK0Fz2K1hoVgHbXjde5oXXQXqBWwPwkruIHM5AIs5PYg9Nist1UaL+cl8N3YS3bBqhZ2XL+8YotyaTZUQBbJ1FmvzsMWudmMxX0MXjZ/L/D9m'
        b'YvMqjdDMVUs1gzNpaCbchIv9NS3ZfzAs0utBWmQiC46U6DLqXV1tbQazZq6k7tVnlL80cNJITO/vGtdXZxo4qlHvYaIae3RNrcFPX3UGZ74dIHjR/aEUzpvWmgrng6r0'
        b'X4hfDH5g/OJAetqfDl6kuN39gxcn+qUsEVhQchke7BW96JP6oPhFdfCiIZ5KoVNXsQ4yeyIXoUEId1sgkcFxaBImYJ0EszDHma3yoyBjGQ1SZMGLcAsO0ADGq9DMw+ey'
        b'NuIZmgCNSzQJomVLh2a2AUh8xUKhiF6FGizxDxJYYNA4KMPToXiJRiCqww/xMLTxQMNmbMBrPABRwDMTnOAInOdBWeVTbRTUKwGLR3sIkIdlFiw8KZlsdEfMk+3ktqoA'
        b'xJD9rGATtxPRRSP+sMLbAOpH8DLnyiby6EOyJFZglQAlUOvGAgnJinEU6uAgHKBBiOoAxHmQy3FDKpDUb4aOjIk0NFZwNxxOobal6Q4jVeGAWI5dS9ThgJixnrVGeECJ'
        b'xwcSVxYPuGqcMvQvznLi/DYRjX8OnVCyw41/meLv6RovsabxgLa+5qF/PR5w85+OJevU6YklW0GboygJL8s4iao9WUO3e/pivj0e4u5HDqTfminQCXX6k0ObZBqRYLyJ'
        b'VNYcoaWQkYZzw1zjoCTMZtU6t8BAfErsTOMBfZbMlPG6vjdvRGommV+CdejGJYv1BRZVmwSn8QqL16ThgNt0ewUElkKjMqYTa4LxEqTTwD9l1J8FnGepztmtPfcFYSQL'
        b'+iucJCeV5b13jNRH4cddefGUqcgaKk3+D1tXots7Ug+vT4ObxphNo/WUoXqbgtgINYZzESxSj2x7xVBPvRHLoIWHutZDIdlkmw2UsXoLsJE+dQqupVCfPjyANaNYtJ4w'
        b'd8sqLyxVIv9iJh7j0XosVA8uQod4Q5AxC2WFLDKf6nuF60VCNh6NgZpYo+V/lyhOk5JcO3QkJchbMdzd/Msv097crZg6fr5pEtp1javKOiANWjy5skucYTKsav4JwezO'
        b'xin2TR/XNl1faRQU+6xTZfS6b7xtjh61KyjfOuJa8P3TL+6tlT79eMXCt39+ruLLhb+lfLTPKvWfe/5wOxe1YuHhtJHPBMSufsrH9e1MpyIfI+cfWozrkkvTOl669Oyv'
        b'G9O/mfdtrfO0m2ff6Fwc+f6rtrWZRxcvD82wPzX6jvso2FJ+yXV5nIXF7aVlOWZVujWr10xvbdqUVxc/P3DciAqdN4X4kW/POLDX7OiCn1aYWVRsePMRz517O597f9qd'
        b'N8/+Xjv6i9mdF+HExEO/Zv6UdG/Gv5aETcz2MQ+3S460NM/sNm3Tn1X5zaLiv2/Q+br9ZSPjsGuvvHHf0xnn5ycVPTOm5s7TOhsK3kz5YNe9j7bMfnR5aaPLW0GeVrNH'
        b'2J4LjnP5vn3EmDeePmPTvr46e9MPy1o3P1v2Xf75N143+8CooPTFbpuPnJznVbyuFd0RZfLLo895rl930+vT7txRtWs/Li/57M7nZx4dtXqJe/DPJj8MizOefr5F8laz'
        b'1w8TO0e84PKYjWJcXPehbK8E+GVk6qOvfLx616PPBadvW/TRx67f6tcFXCgpTfv7E2OcnnYLnv+qzvd6V5cYJy3aprPo5Stpv965+mXi7ILPip13mP/QsaDbq+Ou7tzP'
        b'5C+Bd2DmrZe+/66u4peaUftfOLRr85rhmyyHddY02Xx2+rMXJ0Tc6fx85oK6Fqewv4WahRZ/5zP1nb2rd34xsWt5ttXOpwzsMpZfqblwefHqX2de9nvi4k/zah7pDjD2'
        b'x+cefW7C3FFnC57/7o/u7R/DBMPgSQvWXs9759bj8+uH3VjWOeHOxWX/H2/fARfVlf3/5s1Qhy4ioiJiY2iigIgVOx0FewOkKEoRBrChAipSpAsCFgRFigjSiyjZc1I3'
        b'vW9MN800k2x6Mf5vmaGocZPs/n/yceDOu+/2ctr3HNcPjrrdzXj+6YDk1GvPbAsfvWDckrvXfj6Umx5cG3RFz/8fcXFVQbdu3nU/qnB7d9KnZU88W/aJYW3Ygiz3zpK5'
        b'L7Us9Un8Ymp/fOKcvRfCckpv/StgS1Fe+d7lTyT7kzw/n0ma6zs7MrIlr//zz8rKV17V+qHZdOGiq3d//zK2adZt2zLjJc0vvmGc/OvZmSuNL8i/Pph6R/uqwdV/fPWY'
        b'RVPu195NS8cfPvLxtfrXe+YkPL2ksWCLk+LKzAsBq2VfVqbFjrn0WuTkya/8/N5Xim/ee+PEI3K389Kvd4fsrqra35c968fZnYbfVey9/VH12md2//7F/q+esfnFbckd'
        b'ae+CMWahN39ZtCdqmc+t77uNQ2dfcDMN3b8uP9FVOHDsU/Ntd2Ufh/z43Mq5PS/k4vkz+9v7827OySwusH5izrv/+N13xXOrb1Zvn/u7YdRrnz/VskgRxziBRHPsvAf7'
        b'xgnxg9MIKT5rJSOYU1Lih0WtluF1MVmu4MqVS9gUdg/mzQr6MFu2ZRmc5TT1tSgs4qg3zIej0DyAe4OTs1mOkRM87oWr+epAiUwferCCNQFyrfHcMMCaTYKD3nTG7Ci9'
        b'lqngan5WYUPgak1iooI8jsLCQyqwmsKb3Ee21IwYc7DQlwHW5sARTXIndUMWN/3NllIRwSBgLWG8LXZBAbfKzfSE3uHItBaXyUuglgMJ3JUclsZBadCAOeJeODNK5dZl'
        b'q4saecZhabvnigHQvEvl4hovYvXAc6waikzDCwd4/MAd0DQf8ik0TQ1M2wJXWemBkB+mQqYxVBqZgNPi2jFQyoZXNhouDUWm+WvthXqOTNNbwYbXIsZpKCgNzxlLyQi1'
        b'8RmuhSKoGkClUUiaN1xlqDQ8bMYq0PHEEhUqjUHSoIHctRSWhq3Yzwu5hl02KlzaFWyHvEFgGpYFsTZsh1QLjizjuLLoIHEjFoYy/Vw0FC5m0DJsXGgnQB1c3MvUfzph'
        b'cH4otAyzNSBnIYeWzYMrKpdH6/EansazqoiQKo9CHSJTLbr4+sv9HfTIQtGA85IDAYSW7N3OmuyPJynMh+NPMGsW5A7gTyyxnPPRp6zJbHPUWrTDcNwaGbQezke3xEIO'
        b'h67ZYAeUDUDXGncnUuMndyyBNrm3g288JcgxS8Gxa5YyI7gmgxZjbGDFmM6GOg5U81Ji4QBSjdzy3WwOtMgOamFYNcyCjkmDUDWsgAa2foJ08DzkTqUm/mpkgzscZkzt'
        b'FOy2VmHV5D4jBeiDlkRWqzvUYv1Qb1JQYkGZ+V2Yy3dEo/sYqIR6BlkbAKydwpMcrZjtRPGuQ50l9c+kkLVMUKE1qnfjCRVkjQLWNuAxhlmzBA7GgAbneAZZY3g105ki'
        b'lOGldVzEURio4IA1DleDZuwXo0gPC1jJ47HdniPWMM9xxyBerVg1GNAZZTMEr7ZVCyv3QhfvU7HSajhaba49mbjKFexFpZ3+zLEMqjbg2ukypPOz4wp0zpcvIDthCE6t'
        b'GEp4qf1j7DlKjULUqD89ClPbiafZ4t+HZ2dwUIp/ghpZogfZbHL0PaGFo9SwOwguCNAkl7CXdoqQBSUUE5aYMABS2zRShQKyxCuRkeroqhyk5mbGdhOWGcxTE7VLl0us'
        b'dqhCo/qRXdKlkkdh2owBjJqTH+tejAV28DZS0MxcbKa4GazVYxjqQ1Dr8wCAGmZNAMIZnowUWa7YWVCnxDwOTmvHjuEAtUV4nLVDJw5KhgHUVpGc2YTJ6mHjsRtaPKmb'
        b'L4pOg8tKyTRs38P7fIKUWTIUoeYxYYuwKJHHfE6DFvqIwdMwczdhSWPmsJlZvAbObyXnL4WoDQLUijCT9drGEM5yhBrHp+G16aI7lBvxA6AVqg4yzIw/9JuS/Zvphx2k'
        b'zeZ4RWY3H3lIWayGQiwbQkqTXueJG6DUgp1ATmQtnFGL0RygWDIda6PZ9gkiG0XuryqVrkXdBaTCIhEaPUK5zeUZyIYKOcXckAVHeNaQRGvSQo4ywlS4Ymw3gKbVg1Q4'
        b'Q7FxRWS10rbrbpyt5BeizgAubtwcd6yRQSE5YXtZ2+MTsGgYOm4y1mEleVzHj/UKbCU8rBofR7FxcDqIweOgJIB1bz1W76WXO8PGLcVrEof1kMkObw/sGH0fOg6LD6ZI'
        b'yYlybQSb61FWh0Ss9nHwVkPjoM+F9W5PIFmsHMkWH79xEMkGLSM5clcJPQOSfgZjgyo4IUJJMBYzEDvWmC0dBmXTJUfpUDQbucK6yRqglU1b5Dg4VGT9lQtGmC5NJLvk'
        b'sOoIbxpNF6yPQoes03yoUXip7vnRkCZbnggcoGsB9TN5NtZXLTytkIgLdbCGI5w3Ya0KuTaNIvbUyLUUBXs8xiByUBgryDEd+qk0Fq4cZOtbFgW1K7GWC0O5JBSbfLkR'
        b'Sw70blSSOgPIYsq3U4jrsUow2itNMYccfkNWeQTZkQVIKDAqg8ByvGwk7g8mlxyDYfY7RympS9EsSibSbkmWYZ1gPFJ64JBr4jSao8BB514s3wzpfSg4huSTYAdr1JwY'
        b'PD0IglOIzotVIDhoM2CNGrsR+zgelp42ZAddpIhYzFzMumsFZXZuPIMad70YeCQQrJkPrfxNzSVqzO8BbOIgvcuQCxcfBNLzsGYwvchRWM273RkZOIg0VIiRcEYFNZxC'
        b'usBsj4qnOg9H6XGIHpSZaejscedo2mtWuv5YIGeAdY7Sc+QO+mzIFDfIB1Ft2mQ3bxNXrsZu3ov2FLKBa7BPzsBtHKmH5dM5udhBGPCz92L1jsDhCVSrcnUTr7oa2qGX'
        b'wfUs9lAfYkc3k1udLmd9b+UgWK9BZgdXOVjPAM+wc9R3yYJ5hCRus3ccgOpBKvbyUtvJEObJvRlWLxKuSizhgi072wlV1z5K6cvAejuh8x68XizW8jO6H9N1BhF70L5x'
        b'BFk4/MQanwxXVJA9DtjD1BARSuG0Kl71FCjdwiF7HK+3wU/03GLBb9dqPLt3KGQPu2SErmpcxY4pD30aNWY4ZA8zLCNkJlBDyCd2WnYvW8oBewysBwXYTgF7cJzsXUu2'
        b'4DqXqxF7hnBScxCxRziaLNY1N8jWw5pojtpTQ/aclnNkXrklNPs4MryeO56TzMWCA6xeZyzFdJVwjCHzSIvICZ8mg+sKg/97OB5DXTFdgvgwLB7/Ga1G5BlJ/wiLpz2A'
        b'xTMhP6YsuIsRSVMc3n/A4Em1VXg5GcPHmWvfi8YzYfg7U5bDgKL6ZOYSM4lMXPZfofDMh6PwzO5VGPxvIXiZWirgx0N1GKnCL8OAeH/QKFI7BRsktKlReFL68UAAXsJZ'
        b'mvHPYu9G/F/C7ipJ3e9TZCINxfV3YXfaUiNNFcxuihpmZ0JS5h5JNOg5dOHJzfdJqSVTIEuwgX6NGCjfM8xW1kD1W5l+H7pug+yE1gmdEyMiRfp5wkD1t6nqty7/HSWN'
        b'lIZLc8Vw2wE9Eg10o3dM/5jBMSMW9lqPovQYqk0jQjNcM1zriEDDfeeKG7RIWpel5SytTdJ6LK3P0jokbcDShiytS9JGLG3M0nKSNmHpESytR9KmLD2SpfVJ2oylR7G0'
        b'AUmbs/RoljYkaQuWHsPSRiQ9lqXHsbQxSVuy9HiWNiFpK5aewNIjSNqapSeytOkxjUiJCqs3kv1Nw4drbzBjBpJSpmPTPiYnY2NIxsaYjY1NuILkGBUuMnNIuxt6ixf6'
        b'rVqiUpa93yneYxxJrZOG5uCwvgHbmsQ4Gu1ByfO4zrDnv51ZbAT6l8uwwtQ6OaWj1cIhZn8qKzaGHVDZypGniREJLHRDXDKNWJs43GxvaBgHe6uI0LDtVgkRuxIilBGx'
        b'Q4oYYldITVGHlfBHhjvDNYPDEv5x1F7LK9KKhWpVWu2OSIiwUiZtjYliFkhRsUMgGcwkijwOJf8TtydEDK88JiJxe1w4s1InbY6LTo5gOswkevhE76WmVcPiVFgtjWJW'
        b'SjYLFSoD2+jhtlvUxEll/ccnYppqHtQjbm9ls0ihzhZqpYygVmiJEQ+bJDqHNosVFMcROsTST2VjF5cQtS0qNjSaAgpUEGYyBBQscU9HlcrQbQxKEsHjcZBcvPdW4RG7'
        b'yGmrtIrjDWfmejaqZ4voCouJUw632gqLi4mhhsRs7d1jGuivEG9I98RE39AMC41JdHUJk6qOGg3VscOUS9RFpwoYpnVMHSVLzo4PCTlAxEgDlUJamql5WDgg26eZImUK'
        b'aRlTSEsPyoZAxX6R/Amo2LDN88dGYX9kJ0h6xE0E1/n5qmzcWEAUVu7gXJFZYXagZCs+2HjUJoIvoT/apw+BMLHhnE2RKGGhZKeHkCaFcFs9XthAIUOX2x+EqQkND4/i'
        b'lp2qeoctN7ow45MiVFtWmUT20sCR8WDoxjD7Vx59hu640KTEuJjQxKgwtkBjIhK2DYkt8wcgkASyE3fFxYbTEeb7+OGxYgbuNX3VIhtuMDDOX0m5n+nSX9pe/NFO0ZCo'
        b'eErRGftZjuK11jSlEHVAu+bfZsyiPona18td4RjhFAqxi8r3Egnpr4BOyB8POQoshVbgrwDhyJoZjbmK2ai5ryQMzCUNqIDDgnBQOGi3iulgM2YRxpUQ607aIfaj1m4R'
        b'mBY/HjIIx9YmYvocwjQKc7DCJPqnu3fvtmnKqK3YrG7vED3XSeEC13R2QL6SeVXGE85OoqAxGavcJSvGYZNCTKLsnwYegZNKJJxO1m6uEvDFPjju76hjayMRZuAJTbt9'
        b'vkwrumrCYjn9TvSTeC11wwuTSQlW5PvV60zZ+3VSdRG69EMiWM/WsCZMAgfcntyIx+Tkey/CklDmrVcC9XDVi5RBhw5OHcDiYa3wsiVMMLbYefk4Up3EGizTJnzK2bEa'
        b'+kwZOwby8AK2qR9ru4qBkBU7HZoV0iQ6W1T42UyDcThgobOTq4jl0CXoHRB3YjWUMoXtaijChsEcmpiqK+gdFKO34jk+cvVKj8HHEky1FvQOiTETMZfN80YsgOs8zIfn'
        b'Kk+ab6XngDEJtBrbSYQlhlqjyELoTWJyof6FkzkruNIBOxkXOALypEprqMTq5UlLSJZlc8YNtUdRx0jBLF8fHwcxfh6cGYvXIHsktmKrjylk+8h1sRVyvAODwrBGiIg0'
        b'cvOczpbNuDFsJdj0eIZEm++YLyRR+pYMWDmevL8CrBlFw97kTvNebYNZnng8iJo++qzGKwMLmNnCEFbeZLIuHoUaDQ3sWToZ6hXC0t2meAbqoJKMOhOblELmFGwz3EX2'
        b'QFkCWSrYTSjIbihmC3f2phly7YRAzE8mC0AmsU3CE9wKoSqcqlb04h2gnb3UKJlkjle5ev/6YhvlLn9rvEhFr1I9SchyOMf9effO2aOMx1YPKNSjL6VKJi3AXrKe6EP/'
        b'raISO+OhBDpoidAnMcM+a15bD1YraW0bDqorg3TI43NeZw5dQyZ9Glxlkz53EzPVXUr6d2ZorBg/B+9QOB6w2nPgFdWgQiq2CVgZLYc6TPVOcqQ96RqDl+95OWD1Coc1'
        b'/A0Bi4Rw7NYmA1wh7NeIevfmAZkyjxBx8zQxpvjp2Jc9TDM+MXsib9yPZ2fWnJjj0PVSgtdGk3OLNrc0HFky81zssirfC7bxrVdeeEbTZ3tv/W+C/RcnQ9LWfS00rmtZ'
        b'NFd82tHdOWlxT/Tjn/z2yQLl9dFv3nhxtd8Ik2c/986Y9fGStcp9K942jPF3n/Oc662+E0ZHJ730u2OpZ8HxhKlP9G1abtRjtDcpKOzGKHu7j6a24MrXc99Z1/GMnbuB'
        b'72PvzzfcU3Lsq3r4Rpnl7Lb8zVsfFY9aYrx08tGpQTVVUwvDHzl54/fsSe6WKUWPfnEgMOjJZRnPvbHwTntuxvzxPl9vXDy6rtU+p0G7Ksx3dsaa429GVz85ZWnZzXcS'
        b'C/3euNH+w7mdy47oZDRqftOYFDPu6k/d9pqPvGrUnbu76VYjXv/2tVfda04rLjocb2/buvJ023Vc0P7ta7tDL2w2PdmYsPfCppafV2/JSFLk1Uh/fDWoKfHZSR95NZfd'
        b'HVe9tWndrZdMly849nQKvOXZp3d75wtddba99nY396X/HH4y7RPtuUGPF9/8feWYd4wXb9WZ+17A17Ott+/Wsa1803O2013Nt16Y/rpfvM+Rj98Ukh5rOLs6Lv+VV3/a'
        b'/P7mw08V/rtm2u3MqzctZ1286u9d7Tnxhds5LzSmXMyLDpa2Jn39Sq9s7niHlYf3n8qokWzb6PXUe1q+3z2W8a8jxcXvuI2J++3jNxYqPl0e8+izbq9nGh4zbN9o1DR5'
        b'1j/ufv2MaJj75KG9FbV7tn/3yr9d5GenfN14MfGFOY8t3r//0DeNouGXxem1P99odHg20Mxv0V1shE8S9PZvw+V9se8cTXZ5+QX5Da1nW59wnx3yq+ul3tm3jIJGp7z4'
        b'xcj5Id90Ru46W6rrUrowfbXV4RfPRqeGPL/X+bG6cYGLfzDU8YhKa311Rniw/hvOH355R3zllkn266mKhdzMdiGm2jn6iWRr1Umw0cPHAs5zOdwZvLgNcmgcaWq+HoDZ'
        b'oiBPwAroIzstES6ztx2xM9DOy1eLvJ0pwYaV8+ZiB4+kgunmUAPVw9TaDtCJdVzlfXSf6ww4BTnTuN5SM0S0nqx211hJjsWLeMSRhiWaRn06aR4UbSelJNK9B9fwGGSS'
        b'96g+1NcRsgKYahcyp3na2zI4p5YQfEAbr2nD5VVeTAolQgF2qVX0dH86YgXT0HvG8PrIY6g1wi4q/sJcB01Bc4s40Ya7FBVHrfcJcPCyp2pFORRpQruIfTuwhYtRL2En'
        b'nLzXQEDmJN2yHU4xyZotnl3xAFPkHjt6OrRwd1qdkIHnhor+RAl0e8KVUK7L6w2YKp81TPpXMm8ztxA+Eu9l5wWXzaGMXOaybRLMgIydXHdTlxAnw2YquB4mGbTA07J4'
        b'LI9k72/E87pq3ZuAffbQRCa7kxkyU40U1pFh9jbCXj8fByrD81eVMQlLNOZMxj5W0Vy3BCXmetHZ8DHwd8B2H1GwXCbTwvNk9stJF6k8PAn7yRJq88J8HZ5FB7sE/aUi'
        b'9ngHMh1D5FrMIZX5O9j7DanIaroMCwhtUIMnJ/OhyoSOdUMFmUehjAoyt4VwMedVvEyusJwAR28/ey8/iRUhwQy2S2fpwnGV/fMErOE3N5fejiP91neVakELVvIK6uYs'
        b'wQpyQ1GB/3EfzNESNHVEPajfxge8H64YKn39sTTIkVx8OyUp5Crm6lEsw3Q3qquMwtQBdeUUyGcPjb01mQIOelIGdXBnoZC3unmxAhv3MDUSU2dqYIWE+qSFNFbpAa+R'
        b'ckcfMjPZTGDdIIFKqNqRSCU9s/dpPlAtKSV3VQaeJMNzism1TYLh8oB6UIhdQ4XSyazw5XB9pgk0DlUrbhlnyqXOp+ACM9DPxnaZryap+pQE8uDEOLaB7Tbupl3Kn0vW'
        b'P21WmwRqyVXMqtPYTQk6rnDnDp/6kj3V2hpCYkDmTLVFDFVB94rUK+R5LoFPJ8dFt1p/K5m5xWo+HmELbQxcpus5QI0oKI2leUygSUoKbUBuJ4DN2LSfgQpUmjGoEGNI'
        b'C7IIIVfOnTyexW5IfaBVkAyayenSTNYQN8vBksA5hC5VKMkOZSrvDgk0WQu8onLSwZP0qYqw0lwO9YJBuHSpLjYzvRH2QLsB5OxOxnb9+EFSjYK4p2Gep5+DQlMIWqoN'
        b'/X4GkEammvW+dP1UpZ0uoZwVEkHrgBgR7ZI0irUlGlvMlXYJfN1rRYj7oGNGDOZz3USROaaTTntRhU8Ai9CnIYzEBpkJVBlDPV5k06kvYJaclsyLgAYxGo7NE6GI9+eS'
        b'HlxSl0FWqtYaaBQM/KUemEr2MBuNNjtoU3pT2yAJVfVcHGsEF8i2Ye3uIaPHlTHUfiWPnG2t1rzcHszbMKCPmQipA84ToZTDPIIj3FTGLwK1BIC6zdDPIBjRKVOVTPUp'
        b'mkr8LScqyawwiEVN0FbSUO99eB6Pe5FNyk6LaZ6YKxUm4kUNt0PQzA/nXEIzHlX6K1RWUXOg0EciGI2TrvRW+Tdel7iHeU2mPpNLyCrtwXbo5p6PM+B8ilKhs2oGHSwp'
        b'HJXsi4piw2BlC0123g4+Drb+fpLARYLhNmkoZGqypkXhFVfatAVwfKBpFN+SRVXUii0acMp9TyIVkbuSxw9eGgEzXSXCHGjS1Iz2JweJKurWabxEthn1a52KNQNWPnB6'
        b'KXf8nQXFG+X0HmWLWQ6XplGnm71SsmPK8TK/49qWx9mxe4hcb9p4VYT81VCooclGKngxlNyvQZJB+xKT2RoK/f9eAv4/0vU8yLdAO/n4D5qcQ0KErsRIpBgQTclYiR7F'
        b'gohMjk5xIkw7osm0JJqiNvvLgOQykFhKpkhsJCaiEftOm3xHZe5G5IkF+cZMYkaemJDfBhKqDbIkpWkyOfywbyT0x4C9SREovCSqz9k3cqgQ6l43Bxpck9JLNRVXhyNM'
        b'9P6rmZDy4gZLHxhNL2qNTSms/6CsSRV6pgxV1zy4H//RxcG2P+Xi4DJ5g7s4GF7NgH+D6WpZOBMm21tFbHO0sqXSMUcnV2e1F5cHuTv4sz4YVj+8gVfUDfxlDG2JSrRq'
        b'FRU+rM4/WdkN7eAwLm9/SI1tAzVOYChlBs2NtGIvUqz9X6p3O69XP3hAlhwc9bDKOwcqn7LQKik2Kj4p4gGA/L/SgkjeAr1gtZTx4Q3oGWiALe29MpF0n0kqB4SUf6cR'
        b'qsX4vvDQue4bqNsxKI76DYqNjGMuDaxCt8YlJQ5zQ/R3piFh3sPr7x++1oa4xfk7nfV4eGUwUJnFYGWLvBb/rboWPbyuxwbqsqN1xYYOunVSe8Pg7gD+1qhGPLzyJwcq'
        b't1n1AKdH6gb8nUWty7wJBFNs/0Ma8PTwaWUuAfi2/jtbWZvXmRj3kBqfG6hxtMp5xN+oL1J9dGwNjabqk+C4XRGxD6n0xYFKZ9FKaW4u1Y8eqg6819fI32qTwUCbwqLj'
        b'lBEPadQrwxtFs//tRv1P3V1KhHt1F1L/qJ8nHdFQUvJUM28tdVupHfmer5agfTM8S9JZOkYhYXT+QbMJagbIJEjFAkGWBA7/ga9KQ7VNDKVg/yMldUjYts/0nhs/OiI2'
        b'OPjPe6qkFb5OiQ0nWuF/IjZShUvD/FU+sPL/yRwc+c9zIPNfFWVzs15QMlfzra99ctknVI9MglSQTZXYHF03uMTuH+dK4a+N8477KKutcXHRf2WgaY03/sJA1+k9jK7j'
        b'tQ+MNK2NanCpBINrcAede6o9QnEtruSY/oAGV8zUIHMgJXMgsjmQsjkQD0oftA8oE6hH/jsPm4Px/kz2H+YOrUoapi8eW9VKAzwWydRnzk7M1YKV0zK7lYtnBfIwn5qY'
        b'iZ3KPTYGCTo0e7XEkbD1pUzJEqYjU+W3lj3rtENg3iE2QhkwN/Z2HKJPvVsc9yF/+FOHF4ErAh1WwbU1orDFQwuq8CKUMh0c5EMTtPngxSBvqh6AvGneaumZhmAbpkGY'
        b'7Gv2HH3ZtBI6lCu27PJXq0OgYhvDzmLbDKgYat5LzehooAoPqGQaOHM4BdcwZ9pElYhK5iAhrF5jAA802gMnPe12Y/UgBJhwjz1MqQMnsXCfinuFpmWUlyf8a8QMYRXT'
        b'mcyADkxlXKKDl0zQwRJo1xIhDy56cgXORWj29hHXMhtdmUwCleMhncOEywnH30HloAoHGtSpaIE7BdAchetcv9PjCZcwJxZrB8E9wbM49rh6+zzMcfBnTKfmZhGPrx7p'
        b'KjAzplXr4IyPwhPzvOwdqf1uDht57nLAbp4G5gZuHrYa5erVuGRwNQ5fi5IBn2TqdajL1+FasrTuW4uRQ9cibavOfWvR0Z+tNx8pX2+pU7b7vhg5ka+3pZN3cTAKGcbD'
        b'qlAbpa58iqqgOp5b92LTEm7gi327ud4qG69vVE0RHh+F2XyKbPACXzVVmLtdyeJzHII6JoFsNOaxavuxZJOS2hOLQRHaknELI/nYn7SHWhWgwAhObJFMgzrgIWmX2sAR'
        b'NYQC+105iiLajq+UPshYp8a9QB9WMezLOszjysHszcso8kXn0AD2xUg6EkutmB6cAdHxPFk4x4Kgm9Y0QZhAlt4FhQbH17bvxiMMOFPoMvR9qJzIh6cVj9KVzVEovqsZ'
        b'DuWgwN7F40o4poa+BHj5JamhL10RrLtu4TM5pAZO4RVVGKg4J76tLvsdsCP1OSpsZ870c1Q4ePtJBGs4quFuPZn1aiScwGbq5CINr6iQLBTFsnIM61DAokD5egduM02W'
        b'qrY4apoD92ifji2Qw6yu0+hJ8YDwKJHYia1sUS90SWZG+bPhqi8TMdPDhMw5Xf5T1mrs3ALZSVR6ON4cT1L1xwPjx+hBFi/bH9K0sEAXulgL16/QVfLTBHrW0AMFm7cm'
        b'qcKyp2PtwImyGvPVoW8SdnOLwesbnX3UB5YtNNx7Zi0CHsYUKqF0MxU4s2NnPV5hJ88+rOLnQyp1A8ThDEt3MkDDPm02K2PJ0lAZ75PVd4EZ8Icms0dRKUz33m88eAaM'
        b'dBrDy+skJ6IKEGi4kUMCeZBiKDywk6xciSCZBTnYI2AeVmM3X3cX4Ji3HYspFBklCyWn33R3dmjG7IJzZE15Otj7bfWiSM9SMQXrMZeF3I3YvFtl7B4IzcPs3TV0RsMZ'
        b'VkBQkgXJgx1SNeZkm9SQhuri536v/QEf1VFFNnzOA46rLXsVIuvXfIOlpNWtyTJBkoxdWCdg7UwZ69d4MhJXlNiiSYXPplupZop8kWREryOlGxavwQ7yyF6wD97CLq5a'
        b'S12BdFp71/xwvRylAfch8LybyM5DD8+tvv7uy/iXGYdUV9yKrfZzPPz4lyuX6lGvADbnXGJ9nZZM518una8jkAqdHjkUYr9o0YTh7hYYAUP/0wFJETYbHJCkSHbphQtr'
        b'yNkZL4arZRmcSFHFWpYk30N6/6Izd1tEbMSeXQnzI3RUPgBkQtIGOo5nyQJpUN4jGcVC7gbV3ssBsskfJ5mfhfpNA64WsFiKbVBs4gNFzkZbZ2I91O+F+pEaS5MFKFs5'
        b'EtsOxDAnVM56eJEq7THfeg4WOzh6MciJ98oVDmsedNFAm6groYrQBr0QPE22GRW3+0I69tjt0vN2UDhg9hBN0djVMmjUwvNRB7+bKSo/IL36YcKPEavmxL28wnT+9c4R'
        b'c56b47+htub5dr8gmxVnG2Z8rGU14cX69PcbLseuKLnoc+T2ZaOIr8V/P/LKU4XmZUb956XS/tSs+n5h+q7bLWM2zH709+tfpXwS/1WLyRsT7Z753qo1+ZCd9mXzx88d'
        b'f+H9ZZX6b55WPO4XYTn7p/AnfXVgRalL98hH4g1Hjznr6TMjNmChAKalV7S0Xj+h93t0hM+cZ7Kjg3/1e8q87kLF4ef03DcX4lvP3406e6VlY6fcrTel/w2NM/43lzhM'
        b'073V67k+rfr2pA2rRpcbTw5Ubv6XVsm4mOrA2/+I9XF/yTg5XK+0e9Tax41GLw6O/KBhzRMZab89+W6aUWKsULYaZ49+X37qkw9mV2tG9N+0vKmA5p6uJx5fFhjzdcbh'
        b'Z/4NWm9fq9t2c/JTtya5uM6+vunFojeeLn7Db/o897jJz85sjrjbWz35jdXfpWkvCXom5DfDm6M/8nbbiqWJ07XeraoqTNzrkBpkNvv6/MqAvW22U5U3S3/Q71x5WWv2'
        b'mtp/ja1/vsCt+ZpnzLmKEd++kpT9tfh+FOR8OH+hZcEcq6SsVwKePHVhptfmi32jwQHajqzVfrf69qWtuQmHjGKDwvOsP//nm693fFy4t3rizEdjfjP4dsb4cjz9mvSR'
        b'3I+/X/ad//JLH/Ye/jWuASblde3+NNP32vcr5QdOfWjrv+mxnU0xv818a1LyjgsjUrvtbjRM8nFpdt+T84t4JqlKrpPX+L7b8XexeXtL5YRl+1Iqp+Xqr7Z89minfaVF'
        b'Sk/+5oxPWseu7Tn5w2+90tZnNt56x+Jz73Hhdk9aborIOvzi1UuVdps9dzb9sP5mzvibCzwmv30p6a3CkvDa4ndu7L5Y3vR9gNfVqXeee+n2xhGdZsKP7d/+tBkcw6qe'
        b'fjPlzjz/l3FHYvCeicdynUYsuHnmw/lF+81PZVxffrGh1dby5XkbDiuhe/fqxd/J3r3eGHqy8qUnPhvVOuXOvIyfx+wRzSr2r7t7vuozk/A7HwWtPyTRHOs+55H33bu1'
        b'DkneLZ73aOVKhTvX5zcol9ArHepkQpg1Pav7yA18nCv92qEoQI7ZCi8dGx8LQkETGtEYaqVweuRart+46oelclsFufiP+9hAj1TQHiOuIbdWDtMQBa4n15dKTb0Z2gnl'
        b'HDOZB6czWa5Gh2LhXqZxxVOGTN8xDsrhCtWN25D9W4CXmXIca3k8R8iFlkNqRKS7kutjJ0EH13NdSNFUU0VLHDlRBCd0GG9tvxhzWUfifacp1kKrpqBPsk0xHs+0sS7Q'
        b'QsiTB+lj7XSk5MyqxkymXJqH+UEqbWzKKhZN0AQKOJjyJCGTmpR40XeoPha6sZBBWw32eMkZNEfUxnOrJPMDIYubCBxLppwQV7hOVlLirYk8YvRSDTmtKuQ2jpF2ahgy'
        b'wyCnqDTD2jHOKkSvHGs4qPdAIuvrQhvsVvoqRumQWSGHoY+GoKsnwjnJKj6EvZpJdtgK+VTxTxhtTWgUnaF7GQ8lZwklKmcBi6BdFcSWjEq2SiUIZwzk5FBNHQZDxg5y'
        b'qHNfA4TezMF6eaDPIIQZK0fARf4w39yTPKZYf0q3XneXuUugJXwtf1iyHK6pgdNOK3ikzyi1Gu2KNh5VYraXF3b5QMV8UdCKF22hF5t54Evom6jCsUKvuSqA+xVNPozH'
        b'sQyzqTpyAXTHM32voLtWhN4l/uzd+BVkgdeNgfpdTGOpARUSbB6nYMs3gjpdU2kybVNMJRO1sIKNvWmkndzbz05TmAP5UuiVQOE2vMSsRoJJo9KU5KrrJJS+jqOPoy6l'
        b'gcyhQ+Y2GU8xiwkXqIBLKkDaAMLVlKzsU3BWisWHIJXD+C7owqkH4FBXakqh0s9JFbN137QB5CapNIuhN8WFy3az1RUBvduwLVIy1ADF7iBXsTbiYatBxw5tvhob1X4d'
        b'XAxYT7yxgSxpuh2gf40aRauC0GIRK59c3+7yJH0dkZB1eJ4GeyTXdyof9kqos1LiWTyNeTbMtERjqYRakgDH6/mEQhNHH07CKxyAuHoWt9RoGLdXpVbGa5BByc5yPMle'
        b'Msd6NzlcCRsEFluPMOOI/vRpmDGAWsQO7OKxBckBxgMEQyZcg1MctIjNmzhuEbI8eDTNYsjCnPtwi3bhUsxcM4YH9CMnyWYOL7SIocEA66GBGTdY2G5SQiOc9X1QNMCF'
        b'eIX1ae4oOCePhYoBfOEIaIF+fmi1QO1IanRLVqD/hCVkAn3ECS4rOQC25CA0qPCOpANZHPM4BQ/zLh3FE1Psto0ZZqZ1iJwOdGWsjSVktr3/CCNyaBPqi3pIuESj+eYG'
        b's/EyglIL+hwvYzMhwzDTkxwj0CTieR1HNtSLMEuDMmuEcBw9GaokKwinowKgdo2HMrsAezwHddR5J7PbkuN1Ebtk2zmo8BSUwRW5LeaR0doU5Cdx8eegwoRNlkNseOAY'
        b'dEiZEQ+2e3HYdmHsOm62lmQ+aLjGrNagc4zC7P8z3Otejet/7wLxhi7F3QQz+3dGgP+TkuP/WYJ4SDDlOEUZwy3STwPJFKbptpfYSiyZ5puiAil6UZRwXTVHCYqaeqKN'
        b'xExiI5pIDCTmItN3q6IT8t96ogVDnlHdOc1jQf6ykBiJNC4hRzMaScZKLZjuW5fks5KMJT+0JCNWGsNWilTiuE9xrwaZ9jbYcS7TOSnnOw72nrMVshs6iXvCIxJDo6KV'
        b'N7SCE/dsDVVGDBGF/o2oBYRVeY1qw18dUIm/Qv6SUuaEQgv/hPA0VbjLfTHqss8kX4H6veiG/D/Hy3BGZjv0D+dlhJlYbkitPi4opFw8VAoX4PRQdzZaeF1KLqdrjDdZ'
        b'DBmY6aOyiBywgsJLOyzgvAxyLLcn0bsDqjSwf0grArx1x/ICx8+R4Qm4PIZwqjxQtD45dYdUFotNUuj34qWUkUIK7qtszB5e1xhoZ9b1IzGTil18CCnm6efo5bdyFx0Q'
        b'FmMDs/1WG5NTJWSk9iRohX5Wp8/swAGzbax0c5Uws+1Fq7msJR9TzX0w14GQQatoQYS6Sdef7rrSU9XI2ZM0ySk7lSMReqKmsVAfqjAfvGIbtXDjwCjCxG+CCm1DJzjH'
        b'XUBCERQMGxc4CYVDRsYdW5OoMJ2Md6GXcnhx/qtV3oMxB1K1pzFHSZGHtKEasiZFrZ91TVR2k9W7ZIFtRNDV2BELTc+cfP3q5x3X/MdOTQa7vuAMixrfo0aLFoGpuc/2'
        b'8AstEWPnHM0pn7LsRk1W5/msAr+FXmeKrF3f9fiH1oqlpqany5PSlrTt/+Qt5fPzfnwudkpk/IY14ZXh1XZ6T/30Rf6U7JvPXO3X87umsdEEXVZv0vHSiv63Z6thePvV'
        b'RbMKpgYKWYby1oLz+jNql5u21D66p+6Naptrk1/13bd/UseG6yY/KHL8ZmxT1I/48Ld5or3HY1PXGndnP1L1/neXJn3lH3Pk7PupE4LS1+h4ei19pLrnsX/mbe588qfa'
        b'HFtvcwPLruPf9HzkEtOVHbZmdeOSZU+MHCVfr/ne6mOvv1JhvKEu6WTMnAUt346YOG3VuAaNzU/e+rDeMeTQGGnGTzUfvFr6ysePXL7cbrHj5R8krR8XZHwT/dak0WcO'
        b'vmxp+82qjXlh7z57qLo0Z+ba+V9qbnoruH6yS6hOwJJAz/RJvv/U8bK9s6Lp6V/2v2u6+ceYD2rnz/1q1tF3o87dcT8TNOKRH48e9+t8qdpMWdESv1krUO+IznKHkOu9'
        b'dY5vnFp0MXeE9aqjs5c8C/5ad6N/My9/Onn8pb0tE471x//Uiy1tLi+t+OKDvLx6xUeWifW7J38UVRUQcUG6uWjM1E1t+aXGUcHLr7394uenddbqbe4fvyXJ1mW3Xlfu'
        b'iNK1j6x32Vd357jf88pn77qvqPF/9YmTvVH9K6Lfu3Gz960NL/n6zov+fNnjT+g7+K4/+aVvedmer82+j4XgV65qfDdzSoL7Mybf3/5weuJtg7lPd67Mc82qf+b6reze'
        b'16cmf3bgpXkzVz8T9FjTz99pW1bcnlbf8OusQ8su3pwycnTlaes3W99YiR9PfuWttY/HOH6ghW+czVu1/5uQrAVdbx58zDd6R++Upx459pphz+Wwn94vdl7V5Rr7aKvr'
        b'bUnHtnH/fub6sXHpjnOeW/xd+oqEFz4rOHxl8aS9/uldhyTPSU2O/vRPhRM3aizDEgsdGkX9P9k1GhCaLZuRLRqOIdi2BI7aKQatKCfYMLLFwB1O+eA1PxXjyNjGkZDG'
        b'iIv9kAbnuPUeHLPhrjmY9Z4I3HdNHNlvh+0csItzeZzDy8IjqqDyOpg21MoTa7B9qCPmaSQjJUQCLOGMciiVjZfGMUKbvFfHAzgHBBAiqXbADbXvOm7zWDwb+0dB9oCN'
        b'4kQ5nmN8IDkAzkapSRTaa2iIxHbuggZLZNAetIbT3adnYo+cMBx52DIxivVPPkLEwymWbHBcE6GPmo7HKwjRvVuC7TZ4WqEKyz4Wr2sp4SicVZsv9mAP9rFxmwuXIVWp'
        b'8oWG51yoKanubhEuYXs0e1dvargSz0A3NwRlto2TsIR1dd3ICdBmROhbTUFcK5kTglcZKWa8aIUyGnrVVpp1cA65XfdGcmrnDxrB4iVoJ69SK9iY8Zy67MDru5SEjO+3'
        b'Zaco04Okz0/kAINOcpu1DWEfFJJBt3CHoYdbIXdDRuxQ63dP0rESK+zh7M0paNo61HRxJ1xSWS+a+EEbKyGK+uBV08aEMiZEcyGhjs1Wcc4Nj8OFIU6GduA564Mqo0m8'
        b'FDhfCVedqO9+al4qhXoJ5FtO4dxkGuaOVOpTXjSX8uRSwukSHiMfSrlXnV0pcke/BPa0htAB9YmkbmNT6Y4ZeirfYnOj5KRFnJfUhnMG+mI4FhG+n4lMzgC1Jmde6Sys'
        b'uV867pQuzZHDIPoDZsIJ7PuPQAiyGvKlrMb9mLqPLtZ4BaSuGORgDV1YX5dBvod8KP8aGY3NhlDA1vpS6MIz8tnzGbfKWVXdIFboIrgERUM9CmIVXreF1kMchVAC9YpB'
        b'CAnh704PocZHRPM10gBHdMk4NW314Rs5QEIInqYoVvNOqD9gNyZsqHO7KM5ZwhHIDx2EXmhCqgp9sYVc2pmsenOsIFthkFdgTJlEGG1hHiGzxr6tXHhyaZMvNdrl17y2'
        b'1shZ4tbZrvwQ6cXyhepnjMQJJOPNejreXEY4W2rCTw8RD8JlpvJFSjpSBBeZnyxdXxEKpnizog5C4fRYSvpROs8BsoaqhZ02aI7AAnLaMKKlGc7tGnq8ygiddb95sD/0'
        b'wWG1B8N2wyFEyzw4x8KEbZBO3wZnmIG4R9I6H0gLvr9mW8zUgHZBjzPbWQd0aDkBhNkjy2mzFStGKp2QvJtNxYJJ1kMBMhbYN3H2IYXJ/0fW6X/lImaoCxh9tblL959j'
        b'omIoI6PNTITJf9GIhlon7IsFDb5OWR3C8JgzBzCUyTFh7I02Y7HGSi0TCDNEUqZSC2YabM7c0IvUAFik/5mbF1KmHk2L2lIDqR4zUdYkTBc1M2ZlanDn9SYSmchr1JZq'
        b'i/cb3TKWScUecROQ1/6XZsMq9sh22DC+/RdsS2oebjPMmk+Nt8wfGFB9ZDBF2Yclci4wmELqaXBc5teFuXlhzl1iyMcNLZUF7Q29oSatN+RDzEsTLGhud/reFvoxm37Q'
        b'EHA3dAbs9W5oqczobugNtW+7oT/MsozZMjE7GzYgfPxH/t8JGAati7pJ9W50PraSlLaBTJSJ9pIpW5l3GMn/9FPUk+pJGbMJuYQ5YlzQvhVDKEFywGKdLALbpA82y6Lw'
        b'W+YJRRiIBaw1YKIl/nkTLXpmOQj3mmgt909aQf7e7wZXnJ1cZsyc7uoMXXAlMZGQrr0JyfFJSnJGXyHkWCt2kkuhA9sMtfV0DXT05ZAPmXCcXMElQSuwEE+u0RCwiRBo'
        b'cryMNQz1TE93KKHLcjphfc8J09f4MdMLzNWc4UxaMMMHKoUZJE8PQ9lD47axziL1gpU5U3C2xjT2rSsWwzVnTUFwGTNWcJFABc/b7bzXmQyX6xboFFxd8RK36egi9WQ7'
        b'kxmemTxSmJkAZdwI5Cq5+LudpdQr13loEtxIO1vZC/uxQeGsReNe5+B5YZamOlrAxThyX7SRv9yd1gvucBHyWXZzKDAj1DBhm03hijAbK3S40/TrB+AYHVKq/11E2F7e'
        b'y7yp0EN1tYuxNU5Y7AEd7OvpzpCnJN0hFP4sYQnpfD4fqzbIhmtKGsmCEPJ9wlLNzUyPvTh2lZL0Z9kybUJyXMdOVsZiyBunJN1ZHoutwnJog36WV2G8UUk644mlW8jH'
        b'JSc+Jp3kkupD2hmv7dqC19R4Vl9YOJ6jChPBG7qxlHwWrGDZNwXsxzbSaB9ymWcJPhugmpkJwDV3Mq1tmlSd247Zgq82nmT550HbLKQ+pvywxlbwi4IqblZQ5kbXCmm5'
        b'/wQy4v5k6TSx/LMcoJIsdcJIQK4v+cjby4ZwrtkybCNtX5EMR4QVy7CYfesyCzqYM3qshzJh5YEo1vS1ZDYvyUnTA/WgRwgktARvSiIUY6qctD0I25zJR0cSXyqHZ2KN'
        b'nLR81eqtwioXrOZz1ggn98pJu1cb2wurd8J1NoLQtnq5nDR6jQLOCGtGOrKsznAcCuRSWnFmpLB2qzOrTYmN+nLS4nVYBafIZ5ktn/XzUJ0MOeSv9ZC9UFi/cg8fvwwp'
        b'XoAc0ugN86BV2IAXydpkrSuYPw5yROZVYa+wcf0BvgC74OheLCYtcZwCpwXHREhnpWuvInQTC2+hbSNMgx5I5aN9nXBcldS6dwI0UDOMdNVoy/EIXMZiUrydlYtgh5mL'
        b'2Nd7sRdOB5HOTyY8RY8wWWrBei8LtMFi0iUnLE8RnII3sAbOhIwILKZmFB6agv0czOHLtQgbo4M0qBu+ugBhCp6EcoU9s43BXqzyZzYDOXbTMN+OxZI6g6ekwgg8I8Ve'
        b'RzzKvEIokozYM/IhhXRCrJ1KIDmaSQ5Cdl5nniwWwenx6nJInnlwOEFVCHQe5OK9HlOsIiXYrYcSmkkimE4mj5eQfcwUFFd2Y99gW6Rah0xIATkkx4r1zDzKFy968Faw'
        b'Kg7vFgXTEeRxBFZx06vD0OvFX6cZVmAZySAhGYL1WScIB3eO+tmkPyl4xE4LqkgToYc2Md2BN7EGT5qwOpZjmZ3WRP4+VW+yPsZGb1E3jzTMCRqtVaNAxiyXm3D1YwmW'
        b'0mEaZQPpCVaiegy6w1knl2A64eRoGXAGMki2iao+QnYEs0Jy36hBhygilHaxai7vIVRCI2tApOkG3n7aCC2sxNStqh5gWiA3BCsjHAzrAcuyAa6Y8E744Hkm2fTDVrKp'
        b'c9hc8o5QfaSRVN2TsmBmNLSe7NtW+ozMJXXkAX06/nS0amme3sUsDx5GwqXzNcHzuHvPVZVDZ5W2eOlu5hkyh0+cVhye2aoakulQyRpEVtvuwU6xFpHbqk+qHpjUkaxj'
        b'W6EIK1hdxeTeOIytCeoMeRLm34UM0hV/VVWsQZugQD2/5HgrZqWsJRfjdTu20nmjm0Lm8vGZpODVrDQeaIwWVI+3V3d6KZ5mGdaR0/ECH+CT1Hu2ndYEVZfN5/MlcB5r'
        b'97L3jV20Fg2sAKyGE2zUDMaTiWcDm0M44TQ6cLQOGrkNz+JVXkaX8RjaRKx25Tnmqkpx2MT6qo35ywdGlS9IHyxUD9m6zYyECZLHDHRFNde1WCBVL/m0hdzsrddxBXt2'
        b'FBqkdNOy0RgJ7awhOyPociXP2xzoiKWpt70v9HJzxnrzuWTSosmk5EulgqkbLfkqn5BoZjLI2yiFanKv9boNnAnFcIqtj4lT1MuQZym1nMuPBSrEZzmA+pzPHzigpI4G'
        b'qn0P5dDJOordhKRpHZx4Ukwz5Aysj2MuTPYugz45LQMyLKWilURVxlEDNqsrdpOtn6PeD9LRWLJVtfdP67NWeEwnV6l6FWP6AVG90Amrnsa3NmRs5Dla4LgUCV2gWlnQ'
        b'7cHOHwtvqOZTwbobRph09SF6FYtYLfTv9sFp1YKuCYtUI+acwg+5TCyL55O6D1rttBarehkDvQoJPwFO4NmJPphlD6Vk2WfRYGfa0CxCWgzWfMKIy4IED4Uus4f7VUMq'
        b'hE/kYZvGrFrLjeQ+XqMvpMQ40+A90Y8tX8W/TPHUEQpmTCYZQ/SMw5z4l5GaJkK0lz99fZOz8w7+5febZcIqV3LveIToHd6oz78cvctAKNMkbIlTiG/B9g38y/ilWsKe'
        b'OEsWuid5qQn/Mj/GWPAVPARhV4je+vWT+JdPx8kF8202gmAU4lsR66PKKTMVrFauoBWNbdAS+ZddwRrCOro0PUKiYw5u5F/675MKP2lQt1khvsc9NgvMsHnK9FGC/T4e'
        b'jmhdsBvhA1ctYw8cgmTC18ZmtAhfrZQxPPcNc00h0W8szR0dtsFK+KSinP57agGroHellpAYOo4+9f3AVl/4xJn9+3YBu8Fl2EVN2gklEOfvKsTBsfmc2DuKZ23syBW+'
        b'h3R3D6G/M7iFMZP9XTZhh4t6vWG2iXrBYR12sUo9ncwEj6XBrANPzwrgXf3JwVS4kMIGZVOmwmS4heOA0zC6H7apbBx5yKOBUEfbVBCPGxpRseERe9SRjvSEP4p0ZKg7'
        b'GOloPm16hxNk2UFHij8172UWhH6+ATRUwgPDR7HgUdCMFfKF5F66zjqx13+dYG+4lUbF2lc9bgOZGn//qNp1SyTKRFKR37j2pYFP+5uuNLq8f3/kvoufPPXCt49Otc22'
        b'/uzce9IU/02jF8NWk4mN/i94LBprdXHxZ00WYW1OnxqGvFjc/fHOTd0JUZvawiPefvy9amXc6jOzV3/yVsZsq+2znrTKGbvpw5Wpx6y9bc6n2+4wXzzug69f9Bjh0P7i'
        b'wlEjZh37tjs1p/vI02WPjtz0mKvv+7NjQyzc4uXO3blv4OjFK2cmWHcs3B1R9Y6OdUndk6PrpVMTZoY3fDjurZ8vvjzr2y1jIhI/nPSG8eip/7zy+Ns6uiVPPTp7Flyb'
        b'/9i+768+5Z1o3hP4ZUdW2+lv6v3K8MB++RnTjm0J45/s/seJ91bV/dJ+w3VvcvHYOafDPhrxycZXqgoDXX5zLsh7z9Xywpmci1ZnLJ80PXz5ydyELzL+6e+9/p1yk6ub'
        b'PitQKCeseTMu5sjZj2aUXNY76Xf06U1vJV74odxum9u0p6q21epUd68OM/x2/acL49LGbriwTn+b1qT14oEXYfVHO27meX69+imH0x9XH48OKomx/OW1Eou1PRnLq2vW'
        b'zP08+9XnAkIvffGxw7/H//6NzK9gtHxfveW0uUnhge171sjzY7L//eXss4/+Upy/9JTf7tmjjUqLxP0TIz6r/kfbmDMRj0+P+22dhnvTtz/1mj0+YuHPr+l/EPacS/q7'
        b'62b4NU1dOvejxz1Pabo5nXzuxsYpvqdKH31e9nbpy8mu6flvFX02vSvi+X11gV+0fN31pTwzOGDm91Hjntd4N9Tbu/Of4y6N95lx/jEH39q64Kcf9YvVaVL8lOjfeKzl'
        b'wJfv34j93e6yXd8jT9+Z6/bYB3uffmHq5/pbXJ9K7Ck/MfFm0x2fIzFfLrB96YtjOzY3X/BVvHsq7ftLM869b/hz3qNdv+uO/OGuuD7gnWddtBUGTJwb5j6Kyln9RkG6'
        b'b4CGoJEiwQtYjTzkhZg8CXO4rwaZp2QUZkFboMpDvAsVZ/uwsH0+DrYboUtCqP1TUlGM5gaGPdTLdxsNr0r4R6muBM+J0wP3c1F8FmEK+uwwDxq9NQRZuIRwnEegbwSU'
        b'slcDjaGc+vDxsvfCFiuZIE8W8VSkCRfxd+z38LG3McfjA6FtxL2Yxu0L8bwf5JFip9lKBFmSxIFwjFmLlMwUzzhhqh0LByPGz4E2yRo8JuNNOQsFYwbN06htWjFmQMuy'
        b'nVzq37cejqvQHeOgRUPQ0xTx2iaoZg2Ng7o4H2YLQ+obJcFjruS+P7Kfi6nb4XgY10HhMcxIlizEi3iWCW7t4Po+lXujLCuVFyIWgKh6smLM/621yx9LELX+oqD2hq4y'
        b'LDQ2OComdFsEk9depyf0nzF6OST4yVSOFx78oytyZwy6zHzFQDqFudimpirUSMaMuW0wYO6+qUsIau7CHT+YUPMYqSn5bc3cOFBn20bMvEZkZjO67Dc1uLFhgUfVsl4Z'
        b'yW8kcZQkfDAgI5TekEbFbBsinv2Tw/PhgH0KLesqtU+h8s8/IYClP0+YDxHCMmIKs6ZAs92QW2jRPLppzbbItC0thnlr1VXfi/T+GoL0k6jwVWKk7oCXVtkfemm9D+NH'
        b'78z7w22P83+w6JBqvkidYqT4dzGd4n11afhz8mkp888pOJmVuTfbLxC4uUnvgRRKRq61UWEAbTxN8ZxXEFX6HffSENz2a9pABTREfZ20UFRSaxefyDufh3iG3lj0TKRN'
        b'0a2QTY9cKUgrrDoy/Wh9eUtWy+EJZWnO44S4VzTfLAtRiOwECsQGBkzhXmI05ybjEXEU1MYwzU3SLGhkWmwL7fu8FWHzAahWAy0eIBO+IQ/bHhG2M5jRKGwLOf35LXRI'
        b'sOHe7feND6aOiYOps4NBk6whJasXtCRqyHIWh63ajwdW7Ufkr5G6qqCzf3LVpgpfGgxdt4vYiY9XoIZ5DBsL/Z5wXAXCGGZNRU2pKOLHD/M0IZtkv7CGCv7M5XjG+CDj'
        b'd7ygNNDHngahOS6j4MgjmhairjZWMCmrPnTAaTss8hd1oFEQjSUCnFrM1kpUAkfYvDd9T3SUcxKNp8muqHMjYnx8/f3nQCEFj2kHiErCipxgr6CgQupsP2Qf6b9RUFJR'
        b'1I2aOUH6u+K/nygVxDUSIX0PI6OPRnA0YYH7weh/+C8UoumwfmYto1AdoxIdQe+NdQs2jheUlD6+XHE+aHXS97ulwqhbUg3J5E9DWW0vWnG0T4gy3tfLMFxQUqRuLb7w'
        b'QXKgSIGS8td1WL7xM7XoDjR6wWufnvHciTzf7ZXmH7S9rUHhvQarXlYakq9i//nRuQUffETenSKYz9yvpDK6zS8GB63WT9bfterbGELYOkhOzPhZyYJ17nShatnpi2zr'
        b'bahBxYgW6YcR1exkZ7jpiuKylw2fsn9v5FNkB2lJxBm/3mH1YkTty3IaD10hKKb8xr7a8NKPL5+vIkNtK9gaeLCvHCW5OX0pZBltFjbv+oy17urGEf/amkPfvCkctQ5i'
        b'34WWvSXZmPMiefUDIWO+BeMLKeC3EnO8yAXpCI143JkMEuSI3nB9Q5TNkx1SZQMpNs1z19LAObFveehN3uby0vHkO089Yef+5AS9UU0pmY9unKVlZeYlk2UZyRxnpUom'
        b'fx0dukc+3qM3zbDI+pjXR7Yfbk9zsbj5zTffFN4803M4d8Kkb19ebpVZNnbhqF9yVuUWvHVk48m3MsOVqya53cqpv7jVaU7KnrwpR5/PeHb7VKup8Qs/uvb2IhPXhoPl'
        b'QVbvvnF92zknK935vTrVd7YUhfkkyQ9nadhteTE95yk9881icnv0R5d0Wz4sMpj98t3nfgq9+nzk9xMf+3SWcouLkd3qm94l1dsCmg6P++FSz+FdW2Ze+cr6DfOi4i9+'
        b'3nRqk3Tjjx85/Pphj8WKV1Kavt3U+ryr8901KbJ/3gk70xd7VPqr2YZM+ftanX3bQ17aO+71ar2bS3462bAmILV13KffXZil9eroUcU//fbLT15fr7rte2hZ84dxz5wN'
        b'fv7st3Or7FwuNd1asvnFGb+eWB/7nHPvTau3CuZ9ZtA23/XMyE8OvRuxyhYM+u/0ZNw1sJ6R57Pj0/RNSxo++enEml9/Sn3Ht+zO2IZfd35z17LpvcPPTI21eeNOxKzQ'
        b'57oCc5d/e8fps6U6nx/7QnSLdHDdqT3+ruTZA5UJq70URpyCu5KA530U1CZQU9CALM1toi3kQwkjx6wxG/oobYR5oVgYwHB/BWIctOkxgmu2GUUz5vrZYyGcJUzodAlZ'
        b'FxeWMarKex+eYcSYFxTBFcylCC9tqBIPrnXiXtfyTKBKmZicvBku6BtAnqEhturFk7sTz0rhDBaO58bXRRpYzClTLJ7DidM+Qh2WsPqN8DL0Yo4fOV80sE4Q4YhkOVzc'
        b'xvo1EWuh085bRQ7O3a8ZKJrCUWjl9t4dCf6cUvTBRkYsQrUD5HB7iovzDxASE/NIzYwg1pGLUGw8l7+YDde3kzcVDsyoETM1Q8SJ06z4SNbZxtup8Bzu2MYhHVchgwez'
        b'a8KrvrTYTC9ffzhlpyHIoUXEM9i/jNGncXP1fLzISQuXd7Fh3ixGQMMKVq6PSEVvqgsOe1M055ILrh24Ufs+aAlnQFdfhaYg1dOcI5qOhSP/pbr671gAD6M9B+88dnGW'
        b'/ZWLc6qBBgsYw+hLA0JPGqlC0FNLAitGIVJakYZ2oXSmHnMLxh2L0ZyU4tRklCWlUSltSY2uRfKUmV1zmwFV+ZQKTfhkgKrUuCHbFZq4/YYsPDQx9IbOtojE4MSoxOiI'
        b'v0pnShM+pWV+Rj9uDdzdtB7Tv3x337YcenezjXMJ+seyq1t1bwfAaYafNPOTmWItZoaJKmJNNpT2o8QLUxpLIqUDKH7xod4k7qP+ZPdRfzJ/hUo0Xi+DTMJfUbB1Frkh'
        b'vKieUUMwgS4ppkP6mKiJ8xykSroTaiYt/zzkVshnIb6hX0ToRr4XLRHGNEmrDHYtvz3E/4f0D3X1N/TpxAxfYLZ/ZYFtT/h8YMplfII+G27sMZT8Eu+dR/ry6r88j5eN'
        b'hs4jA40XGeEFNmJecYOTyWZy8mKNVdgNzf+zmbzPP470vpmU+keZPWooYQ7+186r+Dzk69F0kqIjt4Z7hmqzaRr/ozRy7e4/OUnK/26SdiZ8ce8kffqwSfp0+CTRl9f9'
        b'5UlqGDZJVHMUNiLFzp9MERxecu8cYaVGyGRIffAcUQOcY3SWJMdkkbK/M0t0hu6PwKDrr/LODsdHqClvLIM0gVLeWAH9jC79Zt14MUUm7Hkv+NahWRoh4ezLr/0p1e0Z'
        b'KhFC9N6ODuKy3IilEvLtlSDJrtDxr2h587AK8+ZAcRBctvegp80RAc5K3Di5u5CSu7tsJVYh0eUpMdxPh83kaUEO2lCNpXaeXlJBc70oMceMqIbodwTlfvL8l1Qc98wc'
        b'A3AyXfJiefz8f2oW/GtR6Y1wqYafd47npx6mps+XKCz1fTx+8J8e9dWLxy+du+lQe8mpdYbz+xMWr1qjt3xSo2fKcxm/Rn21+bXqI5PCdFrcxq3onfVK5+TYbzUu/zjy'
        b'0dvn3e7mHIv517InSh5vnv/ly3se/+4XiWKGJXyYqNDmF3qnBFvtHGw8HUQ8AYWCJlSIDli9lT1cu5H5tjaj3gcG6ZuzUo6yOr0OOnwwC9KwxZ5F+6WOH44TOgNbrHhs'
        b'ZazECh/7RMiyGSIAG4nN/NI/7wtVcIkRIZglwVLspb64rTHHX2W6iZnYYbdRyiVaKnHWFpXErgJasX7ZCDtPJpGSuUkIDVEXw+gyuQ72YOqy4YKyFiiB9Pv2JNk9D7qo'
        b'BneqHj1Od4VHBtO7j23U+X9lo8ZSEY2BCh1lzi5qE0nCl0M27xpai+wekNF9zRQTbtN31qjbxYrY+Je3cK3JveesCNexn52zkGoxzdOLXJ18RMfjERlepOqPYUejjuq3'
        b'0uyecF4npCf0TmhFiuFiroRJbsRB3ziR2uHScNkR7cOSDbIIjXCNcM0jQrhWuHauuEGTpHVYWpeltUhaztJ6LK1N0vosbcDSOiRtyNJGLK1L0sYsbcLScpIewdKmLK1H'
        b'0iNZ2oyl9Ul6FEubs7QBSY9maQuWNiTpMSw9lqWNaMgx0qtx4ZZHtDcYR2hEChHGh4U8yQZj8oRKqXTICTY+3Io8NQmfwM4p6xtafqGx1MTvF4dhQWRo5CmrGP6Ih9Ua'
        b'HmSGkIn0kB52aA7Ir6g9InM8xKza2NDSS05n4PiU/eHxqQpf9Mvh/xi7aFgLB2MX/VGkILopeLAi+heNSRTKi1ixZJlVZFT0A8IeDawmuoy17zvCLf0ZrgvqZmIO29sr'
        b'CIPUTyOmOKxRQaDgMmbaO0qE5RItNyiPYJipGXB2nXxXfBB5wrJhGzTRgCvaVIRAgwCrgr+GWWnrYR2eZiIVe8yfyR3HQBZe55Ffo6GI3SEScnSdGhLZFXIdsFzcj/mL'
        b'mWhz33i8Cj14wc7bj7sMt5MII6ZK8RS2Yxa3MkqLjPGZ4Z08UyRlNQvYZY/XuTHQBajcQ4MWu4yjYYsl093msdZYQa+Oj8q3vCCf4x0nYvlaLOf0Yy0W4lF2xlKwbB8W'
        b'Y44vyWaAldJFmDOeX3uHsR6KfOCyp58jlPo70HIMJ0rXWfswOwONGfNVfBLrTwM0Qpe4H04ZcuOfymRoJTyWLclA9dXlVGgrkqO9AWrZTbYfU4MGg3B7WVLnRaETmSxL'
        b'tnikyqfB3GWqcNkRa9mTA1ijQ91DQRlm0JjTkmlQ78CEYwvgyFSVByhM8+TBz8lh08B6smPmiuGhz3vwmpF0pBkUMhnWs8kywWoD0w/rvRK9RuDK3EzIT2ZGXViyWZgA'
        b'x5ayW/nnpRpC5jae12HhTkFFkI8n3GsZ9ddECPFiR4XtMI9NW5ETChPcROGWKd2AIb5bHGYIrOGQ5bFT5T0KU11UYczPQzEP3lMH16m3JuZBqhrS+a3JfEi5I3ev5mSN'
        b'fQNx2bF/NfUhBTV4Kon5jz8NFTJViN1WbHyQs6dZeIlPWG44FtP1gll7sNaeTZsBnpNudofGqNC02xIlNVt+dcQ3B4quxqKT3lKv8paxn9zpvPHuk1qJX7xzOWdUlUbg'
        b'ucPFK7d8tnT0hg9HfFHz7vrsleM93rR/5Zqs/lLYv4pf3+LasGHf5sNHzx9855d3DDZ814vnzS6nvxNnmPWYZvALUwN+2+K27vDhO1+mNerO05o5/b221k+CXgs/tzC5'
        b'cWPM/s0vlN9alRjcbnbm129XvVb1hV71V8sXHJ+ff3BSrNXVsDEzpr40OnndeRyx5qvkD79WRCR99Y+qcadWTNW0NK0Minc+GGp9dftyzS/e8pjTIb/6xarLcx+//dnI'
        b'zz+c+2VRwserysJct3WYdWQWb+tKTPkkNrDpJ7stnh/3Fm7wdP2t1KVv8hedO29vGn3LqNwv9k3tiAknXvf1yvNv2BfmvdV79du7zLzMHrMvsv+l2n7d3aVeC2w+tZ58'
        b'p9re+qP+pza5BcrrK08s/VeE9y8X3/ooIfi5u1vXWMh3v3DoN+GHsJPff3dBYaHC7uAxzOS0B5nxHk5/KMK4li5HW+rja+vI71E59GNLtEh2/VWR+wG4DJWQz5DtXM6v'
        b'jelbMEc8gBnWDHOxBXqgS66glPQ9kT20sX4xh77kuM+hkvsJ0++PM4DNhrqMRJJDF56mmpdNUMO8Y1EqWOHB4RgZcAzPULyJ+oSTb/RSiljhP4VpIO11GSZtIpZwWBoe'
        b'dWI0n2QrZEOOOV6bNuTgM8OzstlQoMHgXDsi8AjkBMzwFiN3CNJoyRq4yFW3C8mZxHyH+ko8sZKcE5USKICzE9nDzdZbeGQNC2hhByCNrIEVE1hvEyEDjptgGtMi8ROQ'
        b'nX4mblJCQKZzbxFYuAjzzVnd7ARkx5/JfikZhIZENvAmWIRHWQtUh6AciuauJH2GrsV8UPKtNGmUAtUhKCenVuZkEc+FYicPZ7F0tJ3jhHVDfRlg2x4OqSqWYJHaMyqe'
        b'CuMHl6GONHGPGVsUIqGTs0iGALymcj2nqS2OJgQWD4i9C67CKcjbQWdE7X5Og7S4RoppcVDBEX0Z2GjIIFns8JDHU+MuEbtmTGFDuMk/hcZA91IImMkOaYPF0mV4TmQx'
        b'AaBjFjQyXk3l7a0Za+45XTyStIwj4SgbCb/dh1hwF7oGMzCNXZ0G26SzU6CTL4N540Vy7LEZYwINMlwms6TQB4VQz/1VlO8js3tqJKUnB4lKEwMpXMQ8DYXGH8uHdP4u'
        b'SmHAa/+Vv0KhHxJ0dRl9rsdUsdoSLl6jcBkWn5n9UE8Cuky5S0VlmhI9mSkDzugyf/7qb/mPnmjElLx/Jb+uZJ+RimS811m/CnBzazh7r/2nJY8if9V22DDt+sucQ9HY'
        b'oRCb+xr7J50nJ7wlPNRd9rOkXdwj/0ANA874rZkLfBVpOugW/u9431d5ctYKVkZti32oP/wX1A3i1av94dP3QhOTEv6eV2tZ8NYZWx9S6csDldosiw7dZhUVaRWVyONv'
        b'/j/m3gOu6vvqH7+DvZeIioKTjQouEEQc7KEMERdcNoigF1DBAYhs2bL3lr1BBKQ5p02bNm3SnaZJ23Q82R1p8rRJOn7n8/1elqIZfZ7/84+vKNz7/X7mGe9zPudzzhGb'
        b'I4tr8DVqAEj9nr/+P1vs2ZDLWC2NjIhNTpR+5YoDsszs888vb/CLxd42yXrjiwx83dm9rhxyKTEiNir2uVv6xmKvJlzueUlSsjH/WvjX7T56ofvI65HhKc+vsPDrxe63'
        b'LXbPv/b1+o5ZoGXuztjzev7tYs/mC2SVvIyliL74Jr7W3BVDIiLDiFSe0/8fFvs34niJe/4/SoGvHLJAoc/p9p3FbjevoOn/rOMFl9BzOn5/sePtyy1ktuYL5vHKzmV9'
        b'c0rsyagU4WJUiiBPQIa+kAx9AWfoCzlDX3BbuJqflDX1tDdb6RkRMF8hp7mY4zq5z06vWluXo69rMZFcAeLkGFbZeYnKpJF8GQSuAHBCYvLTPoIVfoKF7XjKIa8S/7kc'
        b'l7Be8o+xhYT1YsHRBqU84USJn5mQR9vdDMosodUzOxbw6h3nZ+RSD1m4xMvVq/nyOCJdoJhmtKC2Fie5FNYSFR2Z7PPlE6yzYfxJRXal8Uvr6QxBxfJE6yms6ocnzMME'
        b'jsmcIFi55LTAsicjWrggQHY3ZE5BFeYSoOF/77zs6Wgp2lT3b/9IwJ2yqCfnsYOwuKgPQu9Fc2csXoqCLWo+U+Kulndpc7kg7Ts4DoXLthcLrRbsEXwc90XHMNLQr73T'
        b'qs/f6aTI5BXoLWHlbq88nFl6YnFQ//019v3eiuMZhoOADDzs/pIbT8YBbXwVGYVz5qqYbwV5ZiL+dl23kwpPFgGn5DSF0L3tJh+QlHEF5vjX9uM9OVshtdgL/bGbUg+J'
        b'uROeT05FX4x2C/eSeEni3noQWbExJjom2ivcQ+IjEX5kcNEgzsD/9Nu75G0vRwkEw41KP1eafCrebPXYM+lpGfXw6bO+yr6J1RQ1RGnaT+3dQs+r7tETPf/xa2zO/eVB'
        b'Zqv0v7o85s7J+FzzgsVzsi+SyszR6/2USD3KYuqSeJ1PMnilnzfJOCk5Nj7e+KokPjbiOS5boWA1baLgE+DC+cs+i0gT5JmvodUyvloT0BcR63PxNUFSCH0T/TD4/dAf'
        b'hJn+l4dELeod+slSR1zuddzPDLK8Qg8ljeiXRpj96M5HwSpeh3vj1tnXxBnYG9TXFjjEGegPW0cICnZZhp79zgk0fqH0W03Q8H0/PcUfiW2qx+QFP5YzOK/10EyJt98n'
        b'Nt7ERzEWywxODZgUu0K1BXcc5Qh5yCKuMc9zwa3LfLqHrvJv53kfYQ7SZuxZdJJOiW6Q3T7POxgaYApLlzt8YcaO8/lKoZZr//p1aPKEbs8l/wNzv97GQv7EKpddSeLd'
        b'0C4OXIUD+iiD8ywchftQuvWEBTGkO/TLCRTiRVvOHuTDxHM1TTzpQ0sFAQwryxkKYRTmzBYUxhcdXynFJoVwu8qxy7Gvyi66fMo+7n8urpnlopBbZv8tNP8svbbq+Fao'
        b'OUV68fOvwVG5OqsapIsDMtNdLdnDsqwO3FlaEFskMZljUuZDlr7GkjwoLRgRryst4PnXFXho/LoCj1pfV1qAka8rLSBBTjZw0+HX4j+vbLhM7vyJBnaRrRLL/KdExGN6'
        b'7j/PtaChqibiA7WL9WCa0xPYfImnUBUoFsEMNGPLCp2tI/s36c6Tx38K9w3uCyJERexQTDFXPVcnVzdK/ssf+/FvEZhQjVC7q8SO/aIEkUrcQZsSaztCvUjIhYWrUrty'
        b'ERoRmly7yovfyRNs1YrQ5j5V4UZjEKFTJIrYxr2jw72lF7HmrjJ9r0rfC9gT9xXpj0GEfpFCxHYua4S8rJiHeq5Grlaudq5urkGUWsS6iPXce2p8u/RH6b4yjXVDkThi'
        b'B3fUKc+dx7GCNBq5mqy3XL3cNbn6uWvpfa0Iw4iN3Pvqsve5t+8rRmyi9024Ptmbmtxb+vSGMnegyN7Q4Oa3mc2PZiCK2BKxlZuhZoQuB/VNX9eQUT79I4mOlL61hzZm'
        b'hQR3Nl75BBP79G+SsYQk/nI9wE4AJcnGEilzr1xJiSUKX9FQFMF17vkI+io8mRlwscnGyVJJQpIknFmvSU8cFLonk15JlMq6WuxFkrRo/5BCSjCWGEfHXo1MkDWbKE19'
        b'ohlra+NrEimr52Vv//RJJDOtnpjgoj47cjzA2dr4WGKCSbJxSlIkN4PL0sSIFG64m1eevcocZb7sAHb53YSVqUUW04qwbV9MLSLOEz/zVoKY2yi5t848uTHcEj1x/rqg'
        b'ki8tTOVrHcEuriSzwWg7ly//qsYW23NuqyKsjd05b1NEIo2IjDPjyOuxScnsk2tsRcNkbprIVWCCbEAyu5of01PW9rVYNkj6JiqFmpNERBB5PGNMCRH0v7Hk8uXE2ATq'
        b'cLk36jkYhW3d03c+1H04SyhcGr08Z6fbovua1Rbx4tKG+rmRVs7x8lnIOgbzmKuKndh7kSvcRBggD1qWN3IdS5fa8XNbOCK9irnKt5whm7803A912IoVhJbd5HAe6gXy'
        b'JkKsIawxyuWSCDLX4e+hYkvqdehP4V4yO3Ld3wq7cBQ7baBWQyC2Fmg6iLaxs98UM9ZozRqG7pdqSJly5+Un/KxOQRbUiAT7zeShbCe0cJkpHN0gw0LECmzYQ1eSC8xw'
        b'kC3TSXR4l4i7fxy/fu8RQQpTzGeN1nouzQjzuOpURZZY7M2nMTuZGGijiBn60MxXUqlWgrGkK/LsAAUeYKsACk55xb4YsVeU9C36uuJljeMlLMRJLSe9W/1SqlOHh3Ex'
        b'bBcov3Z6S86WNb9LyrfpUrWMyrTY9vO3djUITVSzrP59++bkujV1bxWpOb7jc89jr+dJ895xj3Pfff3H/t8+PbYvP8iq7b27Hkm/+0nk5i2XwyQ/yk2rtgqWTv8Qjuaf'
        b'+CWGFqlrPLh25dFweeKFUc8D2+Fx2hrlWi39slc/uew48jj3pbdjftqs851TjRXvuyodnz2V9PaBYS2n3//G1au/9y9/sJjT3b/3/E4nj9tRw8evfCY0AqexIQMzPe5Y'
        b'DOftD7Kje+7g3hmadyeYc9jRS22DKn9apypdfl6nh3f4m3m5AtHS4bkHjG4WYTeU4DQH8WwvYvtiHNM6LBfCIFS7cWc+jtB7dtlZYjxWXGFHiVOEKVm7CYa3l0c5kQWW'
        b'xSKd7vIxUoZBtwiLpkMZi5cwUxAo64mgNVCLG/HuyypYSArfx5sVdK+2NFcgrDwuPgkV53i02o7F7LZ+AYGB69AqUIAHIssD7sl8Ja9JDyy03AEFS0eYhaJbvtjFvaoZ'
        b'iY8IJtMiyW3GOmgQQiPekaXVpJkV47QsDlx/kyyz/6Qal3UeBmDwkAWfK5xgd5EBVxrASkGwFibl3GjavXyUeSdMEUPJIP6GWwIFXZF64hoOpMvf2say4HmyRHMsrKxU'
        b'iUanDdViKDkbx5+i9TsJ2TkZY3CFCxyLa/iLvZOgmM9BOoD91vQquynKsntzF3ygeKenlc4JLvEhq7jjCiOKtHtzWMlN6loS2c2yog5ifIydMUKo3wAVnAPKKdaVzyNo'
        b'CyXWsvuTXB7BTsznZ10nhWwWsUz95PueJcjFXyoS6FNj87Qm954OB/sygdarnYwFfFUDwI6hRQUuqFyDCw9X42pcs8DyTZw5wJ9hpa1dqYKfUXF6UcEusxCecxIo5p9d'
        b'5fxqgypNxv6rGQwZgreX31B85pC/rMdd/ov8vw6qMv/vU10tnmnZLurtpxX1MqX8HxxySX8keO4ZjNPCIL+Md3xBx65wUO/iYRGDQ+Iv6aKO+v/MRc2AV8pqwIv9t8JL'
        b'LY28lJi8WJGXEGRMYkp8BAM8VyOlnDloLImWMDy2aluLwXNH4yMlUlbm9dgiCJO5uTlAFMsDPuZqSWGel1UbS4pMZkAuNDRAmhIZGrpwUmN+MTEhOZG7HWluHB8bJpVQ'
        b'4+xY8KokNl4SFh/5TByVvFhkeWFf6bVEaWx0bALDcgyFu0ZKifJSLY0T2XJci01avTX+IHJxgC6S+CQa4dd14f/7jff4mrOb5cs4F76SFufEZy789J+aCXkBWQmF0kUB'
        b'uUw6QhHO4LwuNv2PO/JD0nY8wbJJ4fEh3Mr/R/78o19Lbs2v8OizcqgwCTnGS47dCfaDl68VlltcxK7l64RVqzr4DTZpON40f05wPudyzBV+6eD8L+Hcl/NJOcj6Sdu7'
        b'XL3CGIyzgbKozXwvcw9L6A3g4zzZB75ezIsGfZCvaidNj536xWvCJKalPQ6Nvx9qrfNe6MuHe8NM9c0lXpL4qPiwD0LfCU2I+iC0INpDdmBQpaqkc6HZTMylNb66lgsN'
        b'fVq1r1Ds/jANJTDszdGeI7aqL0/0vRRm5Y13cOg2jHHX9RJhHKeWkSiOMR/gohJXCF44DXi+nl48j/jKfu0wpou/FNF+wdHEKpHnq5xPeH8tOp5YEX1+jN72Tj23KhWH'
        b'Xno+EXOnDgZHNNw98ZGZiItPTSLjI5unbjlNHewQQjeUC7mQS0PMxnr+HTlbyGGptAkoQ1NsXr65mEtxEJX14+VHFeygIj5a/i8e4T7cYcW6ZYcVXULBt8yVQ642P31Y'
        b'8ZyTJsnX3tkgNRUtuTSDZ+3s0wcXXzCKI19r676x/HDp2aMhgcfcqqsLFrbQLJqeBIs8iRb5RdEifm7gOjtl7npKv7iSBpIswKPlXqxne0ouSSOjeK/EU1FEqzgzpJHJ'
        b'KdKEJHtj58UC7bJZhxonhsWRan+OE2J1TCPvk7JXwFVZacVMzvryxLqdRPqBJ4KsTgWtGuQOGXuU43DqJFe3dTM0eUAj1Hk+4bdYaZ77qSpiEbbCVGzy+m+LknzpxfiC'
        b'z98P/SC0xPe90JfCYqJ6I9kZzOlvnMbh0pHTnXfN5E23vvjqy69987UXTog7LhK5j9VkxgWP1ozVFjZ4nPavOTy6994Lag3rBBVW2qnT3mYKvI3YilVXFg3X81jNDNeO'
        b'W3xAZDXZoTWyKNdB4ZKVKIFS/uw2B3NhgrOaoUvyRJjr0C2+CkIlqYeHnMGtmsLFysP4Dv7mc38EieY4zyU/jeoZEQ7uv8bVSIAe7LbixLbR+lXiY6EY+lcw7rNtkOUJ'
        b'L9hNIBnlcKxs/1VZ+TIfUqjElS1KW/8EEy1rfmXo36mVEnr1IxUR/9gS3FhLTQR8LV4f1FvO688Z5ups/lTAyvOww8KB5cSqDJ78dJhQYtTCFZP/fX535vv8Evy++sEo'
        b'AVzPIwaiJEbuO98Mfz/03DdefYE4rqrV7cc5mwt312Taqgt2viCXtmGDmYhPt5+JHR7cbSw++JY7ilmvr4KNcmlXEjnKN4VmeLzsokah6FoivXZ/ywLmXP3gWvVrK6B0'
        b'AQtPXY0MZHvyXGoVPoM82XgivhZ5Nml8EXnKxiXr9HXFJMnVyBBJks/qbn0WBitTSgqcFavwFZz6YavZlguky045ImR56L8U4TovnshEJktYLKCEj5e6lHiVtBzLHL/Q'
        b'7v8U1fPvyBbInvn+ubMYS2bnXUpJSmb2L8+FScnMVmQxisxfsaq9x/swVsS3MVuRGl/ttGCR4dhYpZJr/HLRnJ/DZ4yWnnbuq8j06ih2XefV6qo6VQPvP6FWG2CEC3HZ'
        b'fXW7hYdIIHQT3IYmrCQNMc4lk5mYmeKz0MhF7xHI1QqTZ/h7wXZOfBKdXfu0fZRVPQQBnAeFj5bJh3sGFr7UmJ/A2BfrsPdirMllJ3FSPsNFG3/o/fKAhshZS/wbn7dv'
        b'39lsqtS090drRXJKv1eS6pSO5Xx/++/+/ODN/ZHOEvPXP1a9e8xps+3m5CParpWf/9G5onTvqMP2d3ZFPa5yP1dwaltT6Gu/y7Bt6LSdGPwIvtkx2Dn12MNvw3d/c2n3'
        b'y2/89pcHzu//cOObH260uhT/3nvdxT8wv5P+t7xvfSIO7N+x+S1T2d1fzIEHmxYUOLbiCHeLtm4377PuMI1YuqWiqMOrbwOY5iVVoYmlzOVthYPQv0x7H4QR7iaIGPKt'
        b'ZX5gO/PNQmjchU1ct2KVoxbmspKQMGAqUD4ogmYNGOIue+xK3LjoAsZ8eMwVH13wAUNZJI88xuLclzm+LSPZBd94K+47J2yP3cLltGW+a95xvRcznqE3Fb6sE/V1RdlN'
        b'YE6Kun11KaqlJsuxocMF/OtwVw3UhHrCNP1VZBh1tNJ3ysnPdaIvAQXEy55dErgb6NfEryVwK/SXC9xnDJYW0nfhhvLryovx8XxQhJKI3XGOlyREB7iEK8p4mU1DZ4GX'
        b'WQpb7lIrcySqcMfh7AhelKuZq5UrztWWnbrqROnIhLNinjIJZyUSzoqccFbihLPibaUlUPHWbblVhLNzRAQLpE+IvLYyCIq5yfijTf4kNjxRKo1MupyYEMGcec++z0oi'
        b'016SnCy1D120gkJXuMh4H56lzHO26ExkZ+1PNSZ55tm6cbgkgQljaSKLR1mII06WSGn9jcMkCRefrRFWHMg+AadWPY59pp54nm5hC8HOi5MuR4ZzM7TkV3lVTbF0fSMh'
        b'5VJYpPRLHy4vEhY/jKV7GNdiYsNjVqgsbkYJkkur+zETeZfqwjrEJMZHEDEvU4BPhMZfkkgvPhEPsbhpScb8PRJrY98F3yn/emRyTGKEsX1USkI4kQc9s4CcQ1dtaGH0'
        b'4ZL4+Ejmeo5KlOnTxTvjPBGksCh9FswgWbWd5TT0zJVcDD20N37ykslSgPZCv88K1Ja1FWYT9nQry6+qfMH7TDIQ+PD3Nd5na2e1m/s9haQLMWFE5MJWLbRFpM9TyepO'
        b'52ORUZKU+OSkBRZZbGvVHTdJMuZ+ZUEnTw1uBUKRUSabymWyDuinL4GvFoGLpkzQrQQuJj58xZWxeGhOsiFxL1SC/EQBTEVhFY8mHkY4qF69IhQIU+UwT4AN3iIzIefu'
        b'wmJCKrUWZP4KBaL1O6BYeFQV7qQwdL/FYiu9c5IHPabWVqaYt9Pc3fukG/QGXIbsfTiafIoFCYgEcN9c+cAJmE9hlW5wLt5kRXAEb2P4YRU0L0Y1hF9QgtZgGOVgUN9h'
        b'NZY20DRjV4rlVrGcLKtlk5kOgwyLQQn8DVNLMysPeSFMChwtFLDODrL5GOLuQ5hvgeUKUAE5AqG2gCY1hjlc65qy9IGl/vGWv0lM4JGXoqMs96AgxWt7/EFZvvQgPrtm'
        b'6eUwtarEOB6IxUZBDbZDPTbySQmNoITLwcW98cJtJYEWYY1vWMZ6BV5XFnCe6TNQbcOlA/B343zE7jSBexYMPC5Ohr5ws/Twsna3MlcQYKGZmqbWFQIoBSnMt5WAXVj6'
        b'FP68x25rHvaCngAZ+DRTYGbetDK074JOFzMlvgjAINxVWDxDhopE7hY9jjjwERZ3cMCC3aNXEIi0sJ9do5814BZwA45ArewevUAOMg6ze/Qep7hb9OtoFsXGULviKr2W'
        b'eI2qPvdqOs5FyS6yC+QcsZ1dZLfBTC70JA56L1lcPbnsKip3hx1KoI6nvpEjey2szUJP8NfY2R32HTjIJRRxCMVS2Q32p2+vO6yNcsFJM1V+8+fd8DGff4GG/vg6S78A'
        b'2fLc2E/jfZhk6RcU4dGyUN2TkM+Nb62taEXmBeiS55Iv1EA7t2AxZ7DN04ZBettELvkCzGE2lyZgzXY7WQCHkX2YcDfWhHFj0YXS/Wuwdyn/Asu+oGzJRUde9GcVNPwX'
        b'sy8sZV7YA2N85oUhKDzqeZ3IbUXkL7aF8kWHd8lxmRdw6tRSXPEZ5KsWbJHiqCfMpiy7Sctd48cKGjEH0tsUsY4Mfr+gJZMfMo9G8F/2khEzzMKE/AgjwwjMiSOFB6Pi'
        b'+C/n9gQnY7k/GUClgSdYYT0rITRpp3FJFP4t5G2YlluparsJr/OSqMT4JM2zwldOIPJ0UWPVVKqtzVT4YiP3sTI1SUOagiNqOKIJBTiVsjGZFj9O7A41W/j8BTUpkLvy'
        b'mSQcT5EXrMcuMc4QezRugByuHPLhg9iw+OR+zKaHryVfUZaqaygITMVyeAcG4vicCll+TjiWguNJV9SuQJGm9Aw8SBELdA3F+3HQNYW5m3yIs+aTrqSocH1q4oQyjlC3'
        b'MHKIvbEwBqcLCvLQBJ180ZN2HL+5+Ar3CEzDDD2mGyl2xsfQyk16r9/JxYcsLRcHuAkG5XbgXW8+OUc1VgQuaypZCvMkxcZpjMfF9vHbuW0ODIeOxWeukQhWiDcTaCmI'
        b'cFDNmJvmARiGAlWcTKaxqCmrE2hXx25suS2CMRXiOi5Mdx5biJSrYIC29MQJtqPyOC2EMvpikt+jRmiEIn+dcG8s88cirPSHIpaHtE6Ik1AezHUkIaZrWdkR8d0E62g9'
        b'VPGcWXgA25NwUpO+FNG+38EuoXmAVQoLoyYybtqHhSQcPXd6e/kGMk3ix+samHB3s2SS8p67FxaQ0IA7gcpJOuk8aTXBBHR4YpEYhm0FQnuip8RbfFmgurPsepIbCQ1P'
        b'K2IwHzmBtp8vNIih6ii28sUvtDcISMQqvSpJcOjXkFXE+EGghSCAPtzleymsduNNAV9bQ/B3J9kPpofN5DieX+9GUrLvFHbSz6mCVKgVchpCW7iVJp6HnaQ70gRp2I98'
        b'YbDz2OJlsTmAi8e7bgqTvAgeh152cDkBxUy5CGJhGmdjVV2/LUy6SAqmI1X7kt/BBD1nrYE/1r756Z+K02c2/fLvJZ+a6LeKiwUKylvtLINjTo2eCjdxc8wPcvvwG1Ga'
        b'vwmtO6pl/INvnFTKU0p903bHlpq6oE8uBAUFVW6qCtgYF6zyWst9/dih10N3vxnx0q+KZg/Mfvza1F+0v//NSsFHOy9s/lnShR/sye/13/j+zR0PnVrf0zv3m4d6507/'
        b'84dHNL+3Kdf208gzFW1diQ+U/5ydE9cavv2AeelMVZpz7t82fTv8tR1+P1LacHDUJNznnpb+9oZ9PTouybej3Ep/UCf886ulRY9NuvYne5l8s/an0pezXhkVXGt8L+Bv'
        b'yfa6uonWvcJtFeabHhV8nqf5vZs7LvpGR/7K0vQVJdMLR8reH38/49eWbVKj1w3fGPmofvts1C9ePef1693vZv53aWSnYabz+ITX7G/awqOzx/p+oP+DQbuZP36QM6Z5'
        b'/S/Wx+a/nWCuE6c8cNfviElr+UBO9R/LH/08qv/zD4MD/ruw+mz/Z9HSY6E6b3/+Tso3LD580/w3J52rpt7Jaynz0T6S+XnA30s0N/76cf+fPjMy8PrFqd3VP/75+ey+'
        b'YuWih0OG514K/8H1T6wHt37sdWrqXItF/axC4B+lrrPFb+xpt//ZJj31XyaFpLb7JMv9u7u4zuroz8uKracC/V7ddvjj/f/10WHXD8/94G8fFr2TFNH9D6e9iReuPX6x'
        b'+Kc9Hh9uej19OilnfYL85Tc+6L0/db3e9nc/ry34nmP8Rxr/+nzWdsev/uD4q/l3Je//9r9av3vA7I3JFw6+Gpu7aWLsndlv90aX/fKBydX29zLR96eCX/7h/D/+Ljef'
        b'GuU4M/G24qHzh5q/mTT0mbXbiWsfXfjnhwWHXp12GKkNeS3+Nz+e0rv1D9WR6n9ctCg0s+bOT6LDod1iZUiEjjs2uIuhBWogmzs/IUAyuVWGG3AGygg4uF3i800EcoV1'
        b'+RNwX+4JbRKiM5grhnu2SpyLZx10Y6Xq8iQkmLebd/FAuYUsnM/dGgv2LwttFJHQmnHgc9hmQtX65dF4LBQPh6CaC8fDKh1ujC6QeUHmJbLAZuYmSsF2zpFjkYBDCxlj'
        b'IUufCxXEykvcuTw2QRn0LXMUcU6ijTAs8xO1xvDHRAOK3ksZ5gTBkM8lmBs/znuRSL4SyvDxxiIFgZyaZI8QesJgUuYawxzbBR+SJd7l3Eg4q87FEBIGiFzmfoJWaGMO'
        b'KOyT8J6zJqxSWUyDSy+yNLjwAKq5XiVBkO9pAYM0YtLYBVCtkCratsZWVrQb7qRxqXf9NNyXZQVeb8IFikZi69UFdx0JbeatgxE+gUqMF5R5MoApgJ6lYM/15/jUINjD'
        b'qhqRjFYUiGBOBdqEgQQbu3giyU7AFv6kQQ4az7B7Sb42fJaZORxmVXkJAdKrWOBtSdqe6OjeTjFWQsNmPovf8BFs2AoNTx7FwSMhf3/pDmbBYxnmgtqD7BAvw5/PCBON'
        b'uYuYVxVKOcwL+af5CW1UW8K1d+AhA7Y0oPvcOhkdZLUrFJ9Etjhry5NlA2H/x4vgNiSUYVtlmu8GXpLn4LBFys4n0W3qeZ5mKmAOxojw1mHrEry9Bve5Usv07aPAZ+Jb'
        b'yImNUj7BRaI6ueGkBTzAPGszDz56hLrBDHEilskIAauxYBPLTrzT10ok0NpHpGluAjnJzIqCTEOcXY56ruCEOg4LbaJocHeEltgmr4yzUMvPqBInxEQ1O6Ewkd8lJawT'
        b'QcFZbOb38Q7UKXlacjkYIX+nOwyEQoupULDBhTYc8tO50URheQjL8mgU4b6XWEigiK0iJcF5rnI7dJARmAd9grW8qjwQx53xHkuBQVlOGS6pLWGnWKJHMRavO8VHbvVh'
        b'D1Twj1h7Y4GHNy1IjzX1jDVy0ID5Im6p3D0YF9JDvpak/2lbiFuKBWv3yjlhjie36uFwH3v5dp7OM5oChaF7MJs/dh6C0SPrsJuV38ICfmNUoUiErc6G3DRj4NEpzqud'
        b'byliBQsfK/iIDG86cevogvPQioW79GVx0YtB0cdkNawzInScsAPHNK/KzpOVsUcEAylYym9o1+bTtAtWYWTimDLCiRbB6KZjZpr/+U2wJe/u/2JJ7OWH3ZKIiBWH3e8x'
        b'RPXVHN771Lii1ApcuZKFJNV83DBLRW0g1BFpLEYWK4lEXCJqkSyimH56osyKilhOuPyPhliJa4n1oiLkfdRKXEJrOc61rsJl4WHprrW4MWgINUQ6XBmWhZIr67mcPBpc'
        b'VLMGlwRbizuaX+W4c9lyyNzyyrxvfdHpLTVk/vZFd7d040pX/X+WclyR72epYa5HrjPzxb45N/9m+qlAVZYu8iu5+TMEf7d+3snqsiUwE7+utHCwuXSPMlyOx90CBcEy'
        b'Zxerl8x573nvvrLMuy/k/PvMuy/K1c7VyRXn6kbpynz7cnkKWYJb8mkK7MjVX3BTnvPty92WX4oIestftIpvP/CyLHJ6pWufc3JLZE7axRPZZzvMF55Yea0qWeZvXtaE'
        b'pcztHC5JWNUXGcaOFYy5KkPMb/jsQ4Sv419nJxar9mq+MDxzY+7qFOcKXRgH79jmh8ROKWjoCbwzeXXftvHRxIhIWzvjMImUc8byE5ZGXpZGJkVybX+1k2ZuAWVHEU8m'
        b'U1rtDIGaXz22WOahXvDPM5f4F7lwv4rDdvXSQUY+nKfv7NZ4z6WS5CePaTwnfqvYTBmHjKCQc80a2m9b7ht1Y35CzPP1X+4kFUCJSxp2KxOyKIIsPrdl+9GzsgNqHDmM'
        b'lQ7pnAGcHq3KlX1psbjqZWuxli/78uNsff+CBPXLV/iyL3dTuYDhrQr+BEYYUs7DEn/m0vT24pRoEOnAyqdib1ea8eJAdbIk8rGRG4wEaqJwbDfWsDhQgbcFDPC3///l'
        b'8pn0sNBYTrArNNLA3+kGb4W/Vns4gPva2easwgfih0JBaEbcgYhZNf5rl7bD3LdnVeKEPyEQVKoXfeO4uhef0tN9P3bZwhjU0frbCGyUsZKbC7ZBIxfIu+iqxjwrD2+s'
        b'oFXPCeYgobvM+82VUvI86eZh6cEDPZzCEnUPLIVZzpnhhA/dOY/tWchaPWhgZcQAFCwkEL2JnWRByTL6J0Itj3/4hP7U/EPOq2srwHLmxIQp1WVOTC3CdaxzA7xvwnUe'
        b'ZP+kw5i5i00XUzNCJjxWvoXt2MGt1ZptvLtbcCVMzUx5n8zvcTiOX0nFc6di2gQxQsHhjLTXIo5aL1Yc5bzfZvL8ucLMNZiAvmicFnAuERyx4et8Z8RrQp/OBR7m6RO0'
        b'4ap0z+tghgVWQyXvE7kYwFNlKTy4hYUXLgh4h0huKucMDYEWAqSF2JzCUC8Wkmm1TwhDDjjPV5O9Cw/Sibp2POXwLMQZztWyy4NZQLNhMvDPgL/d+VinxlJRUiPR3LbU'
        b'IMdSxyS93Wo523/5+Vtvfv5RpK70bp353qPO7scV9U5EPNijlrS/Imxn5xvDRYNK55yd3/2nxT+Ubqvs/Uj6xsOyTw6VX3B/3Wqb3v7f/uuzF0pdgnb9Juj+cLr1jl9o'
        b'a7x122pCLlizK93MVlm8Ce6P1KVu3Tzt9W76b68N/ruj8eWfdGq7etz605ZdHXeSNdYc1P2LWGs2+9qftQ1KHqZvfvjvv5zwswuU9I62x7zWUdeb/sOf/bo2pr3dXj/+'
        b'pfcbfu030p7zoXrye2f2GllN9B6s6/mXa4pn0lWTN3/kVdu/1vWDDR8OTnxwqN7Befazh5V2fX89mPTnkd/79ZztPHOm4U3LVz64+KZ076efxHat/bNfXvW39BV0LWr/'
        b'+N33zr904SXjfyX/otwiLvafMcnN9mmD74aJ7d/t9nuzViX20JGfXfBe+176S+ZW34x1zTL2HHy4ac+jf+/YdfjYi+Md3/uHS+HhoJG3cs4rVkZ+um/kD1VNH7zxw48P'
        b'//zTb59aM1fg9/D8yEsp350ab+0u2f7eN/VeKzlw/OKnRucfNNervzqm3mCz8efd79j8qfcH/7jx55B/iQQh1aZndMz0udAPbNVwtlDSWZab3XQzB5EvQ8UBzkyVaC5Z'
        b'qXYGvL+AMD6Wqz6V9RRKYFoJH8IIZ08KnVkN83xfGLVZTJVx5DIfLjobe9DTiEQWZ8tyCTbmVXlrvp64Z9gC72rK7iUKyfBphhrOSlEIhq7lMf7wQLI8WtQNsvgaifmC'
        b'GKLLuxaLFSZhzFnMNe8jb7VYW5IvLBkTLIIya94YbUvWt4BHxBNLFSRn8c4m3qQYgyFvCw8raMZM2fdcQR3sPsA7BMos4a4FjQab5LlpKW8UEd8VQiZvu5e4eVtYmSph'
        b'O6syzKXuT9/GOXiwH+ZsFm13qMY6mf3ObPfdHnxGkxZsdvLchzkkM+GBl8xFo7lPfC4R+znL0dE0irO6sMSbJGgJdLqS8lIQbIB6shz1sIzb06vWJPLoXW+st2D1/RQM'
        b'RXJQFMTv6QztadeCkUjWVYXMUGRWIszTnnIe4BKJ3zIr0TLSe8lG7JDyxQa65bF0pZHILERs3OPkpsUF/bqpwrTMRMQJwdPVKNxldTA3+l1nRtqVNUs2Gk7jf1oUSPd/'
        b'0Sx7wjZTWx5JwBlnvUzEfzXjLF1grcaZSiqyapNKMrPIgKsPRJ+I6RsR+0mLM7cW/mVVhVhFIZbcVIUzrBZMOC3OkFLj6g2xG0sasrqVclyNIRUu5on9nbbhyesDy+Yj'
        b's64UeLtmy6KtwwyMZeaU1v/0+prJLevMfLFHzqYyZbaG2kLph69mU5FVtWu5VfW8uS9EbqmwgaiKnrCoGCLl0OgRARdgLU82FF8IQMRZVWJmV0WpLdpQcs+1oaLIhnJe'
        b'LXh1wYZaqgawGIvKhbD+D4dd8+8s5Nnh31slJ6a18VE+9IUbyjNCergobWZo0aPu/r4H9u3azQybS5JkFriRlMyuZT5zCHyCn6UwliezFvLff+U7H0o+/KlZjq/pM0JT'
        b'jY1WufAxCxkuHJoiBdEiL8sotebgwskyPIRpDmFqEMKq5NP6q7svni2bwSSfI376zNmlY+sog8WD61Csjm2ZNxUnZdBT/z3yrlXBiDqrQfOnkAato68I8nZreX5DoDeo'
        b'o7z56Lt7anxf/u1r8Cu9rZ2PbqT5Nip8qlyrOl57wrL19b/+PWyX+o2IG/Xn4mZqDA6U/MWw1DLZ5A3NsNmetRPfuxdUFDa581s/+umEtijKyOizsYvx3wrsf5w46/1h'
        b'5Jn3rf/cbJTgvPVTkx+ZyfM6ehwroYhzb2PpHhlskMM67ktzHajjg1FvXVu6SyIy43XdPTuoPIB5T0MHJbgDnZwiggLoh3leIUaTQlv0Z3O+7Hao4HX8I2/spBXripD5'
        b'ytuEgdbqK+6K/EdqYpkU10jhGG2FHPf5OnI8XbB+4V4JXzV4QZYziZ228Ql5s7LXldJ2pfBZJm2/WkpuEqXc+yor5SknSs3ps9SvLUrztywXpc+fGstJmxZ7mflb/kdS'
        b'WC7cVOl5OqJUGh4Te1WW5UiWQndFXqVVZOVR3n0Rn8r5O2IvXY6PZB6byIjNz5Srssk8meuHPv6iSiuCVSWTnA8X9nXyOPZwJ06mkPWUDboUshS2Vik25Gas5oseQm7l'
        b'eqRp7ML26W+89sJ46Yhb210z+e/ohMdExccfC7OUJETFhHmxK7gvCwTdjUpX3iw3k+MZrOIWNBKPR/ovWgbh0M5D4U7Iw3HOOMBp/SXrAGt573sUNB9+msPl1yvtD09m'
        b'mQzOu5rjGOPrEbzHCkligx3vn3H3viJ7wRP6FGF4fdAX1mfTkvB7ukBMSRx7Hvh67GnHmHMxX+iiO/WJHlbeorFYyYCrJAy1WHT5EvIX1DKeOvx1eCpD8O6Ku51fNE6W'
        b'VULexyfAxcdM5MP/r/UFmfaW0n5I2F9rOQnDfmIx6ZzHmoNYnHDgZsMvxbr/bUj9JUW1VJN+1FCVXW1TUpUTGRsvT6OnpaUmMtTSV1UR6q9nElgg3HFLR2idoCM0NuJq'
        b'UsIANGw3dXv6prNIYGoif1WSlvKxiKsd045zZJeWOyZi/S4tyMEpnFmzfx9khOOQgj3mQRmUK5HuasQ7RupQitnQQkqt4tgxaFOFcigQbsDHMIWP1aHWHsehGEYlMIE9'
        b'AersODYLhxwd4DEMu8FjV3qqBAtSYQp6oN/6JqvENuhwE+ewWxGHoZf+PNoLnTSerugrNtuxdjdmYGsCNOFd7MFRrL/pSCZoFxl0I2tdrzj46kPhVsw4eivOFotoClOx'
        b'Dphz0XW9kWS9i72nfLDNDWtfaA82tCK7dsIBprEbxqA0AXqxjJqZdINJu0vmWGITgvfUmeod1iVA0wLl2EZ/ZrAq9CjWnbCNg6JwHFCAJpjEnEQYwTJs8scBGL52CTvg'
        b'8S2YweoAKFuHbRfPYhV07F+Dg24wswvu0dzLoFj7GAz5Q5aJJw1gEusOwNAt7DsJtULsImxxB++z4jtYEgMPsA7arm0Sq8J9GMdmG0tsx8mYAyoOOAG54YaQ4XoJ7kZQ'
        b's9XeMGsW7pJo5ILFsfgY6z2wMtgABq4740MyKhtx2FEBak6aBdK8C6ESslV2BOCYAbZiG/025Q250HCaFqMSqi1x6sCh7Y7b9HRx9NRGrKfPGm6YnLXAWuzV0sVcLIWJ'
        b'gCT6tExDZQvO00u9OAJDNKJhAVbbRh7E2nNQbwOzOtisEeYNxdHJhzDDD6s3QWHIPiWch4eGuvAwHuY3QE40vd5/mWBWzW5DbIvYcuqM406sIFJ4CF1JEqK6KqwLUFt3'
        b'Li3h4A0cNzy/Eep8oG3dWRyiJarGB0o0n3EiqTpsO4z3lCD3OD7aRTtZBX12NNF+Gt8UZJ2mTSixciKKKLgOo2s3YAEt0Qy2aNwW4yzmu27D6uiUe0T4WCpQg0Y/Zygm'
        b'sleDWRxbc/Mw7W/3ccjYBA1YY6W2Bwdph0agSXwcusIlW82gNEYOCo3Td0LngZS0GE2sJGJswwe0tvcuhwbB3JrTUHcY6mAEOiBLgg3mWG2xAx/iI5gSw7Ay3t+AkxL5'
        b'y9gI44HB15yw/pZ/PPRhPTv9J6RONFaHAwmeB6mJJkOox8wTp6nt8tNQvR9qIDeMWC9TZOeN5TBsxdUifAC9t87e0tU6nR62xzUaG7RT92jjAM20kEg5i7jizl5iq3xX'
        b'I69tqTuI2EqgFvt3E5H3EXE+xDwJlsfDLM3pOM5AviJ2HsLyG9Cc4ukciwMmmGtKanH+5n7rdMi5oOwPDw02sdRv2K19QC4R50NxVISl1/Ulx/EuCxi8d9sNajDT0BWK'
        b'gyEDsyM0oRke+PoH2oTr7FiHPc6uKno61rvkN9gGEgs1emGeP+1uDfYaQB7JlAwJdu2jbZxxJEvkDmaLsdwHynDEGBt8sOA09sKYnDYRX8FaaKOZMMmUHWLDFpd0eD+M'
        b'X7u+Doo2UZcDRFMPrhM55KZpKxFHjEXhfZy+aaMHFbSMd2l7hklyTShFa3hg8zoYxJYzp7CPGC8bp4zOw5w3y13erbwNypNIJnRBjl0kjl3C/NMwZ81d7T7nC1MbiOT6'
        b'sMgPyj09tM9dwwnqr4tooeksZBIDzdPMMm2wT9fEf9saX8ikNZ8Ixs54Wr0HvjBqhg/loSZsG7Suh9qUnzJJnLmBptXo5wgljCJp2NMWMJ5ihw3n5KjZFrybIIGWK6rE'
        b'ltV7T1hCl1aoJ/Qcgns4SYs1i9UbiJIek8VRDqMw5A45Z4lbs7fgnNuhQ45Y4wHtEVoqmE0U20k0NQV3t0Kd8VUi4WrRIZhNFeyzdseKi8kWtHFj0EWAqAAeEeeUE8vV'
        b'h509n0Dio80S6+NotWcEREoF7Joh2TBVeP/ccRKL8xZrg5LPX4AWbxphB5biuCnxRpnTFpvreE9PGaaXUyzxR9WJdTSOiWuYZaWcDuMJnMS8r5EKtSQqu5y99qVtDodh'
        b'nxs39cUXXKFwLWRG0cTmqYEukktZ+w4R/dYoXoIi6A6BCnXa4R5jdag4gLVu0JJMj2Qim0kzNpFO6oYMTRFmOZIE6VyjCFMH8JHBDqKFURZ9/ljvGrYnrEmVi4nHDKgk'
        b'fs3B+5q0UB00vS6ixbETtJlt2lgQvDGGSC0LRw5DBy357DkT0kyDwdcNiXpbLzliaSjpr2oz6LlGDHHPmraizdmGRFw+ESXpzXN7Lu7FMtM4fHDriEYaZG6ilcqCDKLl'
        b'NhjbbWwaIYExkjhTanpYgY8wSw3zXKDJJoBIAlpTaQz5WGIKE6x+KZSkYZvihm20zjPY4RK8Ex5jg4qLOc05h0RkC+nt+mMw5hrtR3s5BneSgmlHa0kjNsNMGhZehZrz'
        b'ipFY5Rjlas3p9BLPZFI4OSkkFkrpmSoH17WnsRrqL0KB6KoBNBB90yISfUPTmTga5TwZ9NsTPVwwP0EdyyKDFDdewIH1UM2IayexdJuLNtCOpPyYKHsvlPkxUZvAAYxZ'
        b'HLLASeHxTaEkzRo2K2Ktn4oQRlg0bzHxTQ2UJsOogCTutjWYsZtWucbwBg4qwiPoiHQ1hbqj0KfLPMvcRQMNbFC8ZBhHlFOnSfxYY2OGjwOt3aD+5A28bwj3PDbtJ1Uw'
        b'pUKr8xgLFU9ATyhjGInw8jmGhxoTcAhnzgeRxGAyuJ9EAYGQxH1Qr3vYwk8Hh4KhLPQY3DkOj7SwxTX9LC1Ny/4bunDP3ysYerbjePrGo6EkOnppR/ou0br0Qf3ZVCFW'
        b'udjCdMCuGxpHMRPqoeZQOCnnO7TNbQbatN452CGGeW0sD1yrtZ5UX4EelJ73kgQQ987ZnrSPJz6uOA0V1pDlpbdTDx/EQ/9h4r+8OLi/A+8cFWKG/Al4FHEEKl1iYeyQ'
        b'D8xA3hG7o8dvr8daYgASjJ3UX67gEmmBNhxRgBbihHx94phRWqoSbLCBObi3jsivYTvM3MLJK4eIcGtI1xVjlcMVbHMmoZIRcfI65LgmEhO03IKqW2uIriYiUrEn2gBr'
        b'SAq2kqQoOIhFQdr7kGi+FDtcCRsR23Ua76cxNNJP7Yf3X3fVIr14bD2M+RMdTsF46h5i+znsPYr3aNmySes179/EMJkU7kUZmzBaxDI9J04ctNEwM6ApFqrCtNOuemMD'
        b'9TJOrFUN5bE0mh6CBFkiKE6hhb+37gZNr55UaB9pzqTT0GqNTdhh4KvuT5qiO04fWyOx0p32twtnzkFjKA1x8BBLHYJ5dnAXGafPYVUgNZF7IeYqU0OYeWkdjl0mCTOK'
        b'2dtczqjg8IbdLic3QveNlHIGIeoTsZgIm6awCCIs8KHwEhYTiHA8YAFTu2D4qqqJnaKUMGyNyyksP0JTgRYW6j9HPY9JaZEmmRQ6vQVybDFrtwQaqesCGL58w1FtkyfM'
        b'4VAYNtMzgyRAqtONIMPiFO32Q7kDJAqrYNp8nxP2nSeIVonTkYQwi5GgC2myXtLTE0jCLSvdCu/rEN3mHTkPLR5Y5XeYVH1p5GGoDTQn5NEBM/bUYzFhkhaY1SQGb4RW'
        b'Lexxg+Ld17Fcw9so+hJJvExF4pCmGyohMLzd/piXgaM6EVk/VGpYbZSjdWtU0bHDcaMdSmIXvLOZljJjOxF+p/YG0vPF1ObAOcw6D/edgYTTIVKFJJ8IJ+CjEBpu08Er'
        b'JLMqoZsUSgeh/WHaKeEJq1NQuD2BVHU99Pti1hlsO2cPBV6W3rR0WZB/NG6Dr+tJhmQKzt+GrjAzvBMOGbo3jLGaVFbZWZyUEvVUncS+UMyz2gXVIiK1Zi/MdSYCmyfZ'
        b'PhB9nuySUpZ2f50BLfN4KFYcxFxoTjxAy//ABnIOEd10YNnuYL2ofXa+YdARig8Tz5FkbjmoqbLddr/eOlszkuzjapive8zHhBTi/HZoCKRWy9WJuB5fggK/U8Qlj85B'
        b'yw7o0ovAkQTqsJ6m2XiBeKHzbOQaEj/lMGANQ6q0mAWETSHfCEbPX76w1gl64+mhAaiNIgFRK46jUWX4E8mP20KJI8yZkMqdxrvpevhYEM+KxlZBrU/KawxI5AYaM6rM'
        b'TOCIco6I8jr2ReKDVCXCPVm6N2j9MndsJIw7brhLByu0CEwG+aW5QWm60fYbKZAjMTgRouZHOryd/YGsvST7q0iO0GuODDfd1FKH/uu0r4+w+ZSTKunLSZjXhAlxKHZi'
        b'bRyp3G55zEjByoBImLuRQN/Wh50nPDPIQQggCDEDc7Es3jXMALOlRthpSnTRRuzTF5CAZTeNSUA0MMwbQ2PIu2B/yUCV3igD7hIKFHoHE9jrveV/Kyjm+hY1HyTY2o6d'
        b'W0h2d587dF2DlrcQGPeWwsOEy4d0YFIzmRYnU0qwovS0j63yNhwO88E7UOVPj0zCXUXsVY/EvJOsMCt9nHsZ6jTJVrkLTddxNIRIdXinmoUHSajaWC2XuNRDZEC1bSQ2'
        b'HSJ5U7jBVI7FsuwixFm6Vg/uJxgbHSd+7d+I064kuorIQBknnfwogcXMY/mV7di1lSzcXrx7C+pMrUgCPlSkzrKwy9Y10vb65nNRxOmZxA1ZKcQIdSpQvhuLL9pivdd2'
        b'4oUxXe2kMJKAs9h7BnvPE9t0bCYSbNhPuGXKFnLx4eUEaE8mMzyPzOW1u/RIYlY7kZgfO7iVhl0aA0WEGuTxQSApyzyi1IpDF3EicB1my5G2HoqkfhuJ2uoEW685Xj6T'
        b'pH+CtnhkizmxSyOURSRDw6HrULAV8+XPYWEc1DrQs6MwTrizGvNPkZ4oJGjSoOelAc0eO9J9iUL7cTAtOJ7QYrX/oeP7mXHWZwedzlLzczBFVFXiDSM3YvWiSADVahKB'
        b'j1th+8mbrljhYk4UMbh2C2bu9IoLpLXrwDYzBb6S8R0c96YBe7rLC4Q7BVjgcY4L4JDGsqsEduyuD3/RhwzqIq4oMozsxZkzMOBpIRIIDwuIN+ec+ViSXBP/uCiW50Ho'
        b'xD7OSeWLKFeHbLZLY5HrQoHQg8T8RajgLiASNGJGR7UzFloKubioJui+leImZmEEO4Fdg6rAImKMusNqtOhDt1WMzipD1UE/TYkuKaYya6KFNlqmSgbZd+BddxdvyIk7'
        b'pG9GzU5h57o00k6t0OSu5XyWhHcpNIRhCcEV4mBsPnZuH3O7kPVddt065Sj06jOgdws6IyWYqwqtUglL9Q3zhyAj6CRW+tBW0vfEi9nH6ccO6GYXD3IDdQjF1e+kHWu0'
        b'ObONCC9zI5kEI+bB1G6JwJd6zY4kmTpEOriCtpqsnNibkGNN+rUsAEp3kLUwSgRxhgBM2Q5asAEotyNTKTs5xBseexK1d5CWKCS6GjUksymLTLM8O7ObkGtL6O0RyYlh'
        b'UgctMLyZIPEDqD0QeeCqGEsUIzWxxu0i9OzDh1ILI5y+gH1n3NdAj+LNlEhvaQiJ0DLoUGaeA6gxXIeZtLR9JI4ySTx2nTtDbd2jFa0K1osjnp2mIZTupal2Oa5XCVLD'
        b'pvBQzvaqE2OWDZkyGbQqA0iCdN4G7olxONjc1wazT5NYaz2IwzuIb7ptLYDdsuiB0oMEiEpoPhnStSlypJlKk2gOHTB37CyhyQooMIcmReyPxVI3qHTClkCyqu6R+TKn'
        b'uAYLQzeHmx3dgP1KUBkKlVJk9VM0UrAnXCrFLvpTfkudhpu/79RpsiIHSBiX2eLoUdeb2lERMGGqDpMa2OxGfHVnPw7sdCfW7oEcZO6dfE2y4cchcz00hJAYgContzM+'
        b'Z6VBZ9YSIsojNT699gDel+60JTkxelVM4qET+q30YT4lBvv2kzVQaq6LdWuZICd1l7srnZh0Yi/BxXzmkDLziSJ1ClM7oT6ZCCoXps5CbgJp8A7oPUbsO+CZDgMhZPQ1'
        b'0ZYOeNhzDphZMWmZ5rPRrKY0lOxfu+G2BQHPcR9mSGBZFMxg2y76ax7njPWhKjLJMtmAEFffIXx4QR0z1XFWCE0X0s/S4tanPCANpuVPjPCEb4aE6OAh48OaV7FfX2H9'
        b'NWyNIN7IDCOxPHLiLAkBPX1nYs95qJbSWuao6smfCfHyI8FTarue6KYKhtZh124Dz80OMHaDrIHc0wa+VuHOiqTUHp48xTlpRn2NqJM6qNhHKzKrQjMYTSCZ1EYKZS4G'
        b'J1Ng0oxduXWwIL7owoYE+qXk6h6oI41GAqqU0Wk7jJjD4K5EgvpN9jgacZZWOcf71FqGNZGkdGeQkADfLPF0piExz4grKbgmOUPstiC5O4btuqfgwRYSqsVQf1jqRSi7'
        b'KZqwZ9ZhJltHIPNWPMH7DYcJKLSv02SeLS/sTtM5qgK9l86TGL7H+wGSwon8Sy9up2GRNsPW2yQGpg2JCxrJzIVu7wuCOMw9Es/qNF84Ek1qYQwbImmE5cmkg7PoDVby'
        b'vTE8AobiT+zH8bVa8HjrGaKEGj3sdLZmK2KOPWsjcTqWiKaRK9Zeg7NSnLsg76CFtRt2EwCbxEHfyyTV7ulimw5ZYBU3SIJnwPwVgjvjTtCj7WvqZLuNtG8LVgYrYatr'
        b'Ii18valJyiazWP0Trjra2KKbnmKvDjlHRD5E9L1EgfnQdZskQWvKKTcoPEuS9o4FPNSLJL6cJcaYvBV0iZRlAhSLcYQrY54N05KrJG8bHG+exs5gKxJLddhnBjNHLsCA'
        b'0XZ3kgoVbJNpIx6TYKsl6TCgTVOZw/nbJ1i5+469UH5pjasv9f1oAwsUPAoPnUkE54bIb3FKxq7TKT9hcKtquw80+mPhonkbRJ0XQfUeI7JwFYP9VIUwoYN5PjCkYAUD'
        b'ZxX0oQdJBI7vJUIYsjuFc1BgHWtHJFrGuU16t1hxuWBrsVbbErJJqBGN5sAwWQf4+JqvlRnkxhPV9+HsIWfoMYRaTcP1tAX3YDyCGLbdyUEAPetItPRuh1o7zNhM4m4U'
        b'+k9jcyDU2wST5Ml1h4aIYFIKQ6cYRGnD1mCpibw4xgGrdmLndcy3htGtAZiVsAs64o6QYuigOXcTcm1wIZkD015YYBlMqqPenDj6rtXmoBjs3L/mjBQf+xDJVZHyyN6j'
        b'pwTNcQkwTAKsiXoY9lEkTpi/7EuGexlRzT3oSKN5k7paj107oTKFFEq1TxzRFBku1ZbqCZCtYmyPA3axWOOhfwlmoScF6+3gkbMUq2n5SnD41CaYDxAcwLvqSjgvplHm'
        b'eK+BaXnmHmm3g65ofTeoOr5hvR0ZXgU0JRw4SIJ8lohiiDhhiihh7goZoP26tO61YeGMe6JiTEmuFonOOUdfUYOJs9gV5+sTG3WBgOqoBg2hjhRunwq7N18YDtWnLNYC'
        b'2Rh3sChOTYL9AVCiezj0/A1s8vDeuBvLduHIxphzWGwrYsCV5FA2GdLNOOt1/SbNvjBMi5RXKz7eJLcdqnT9MCf8tOuFI94uxOX3HLEy6UAETm8hmTRIW1pI1qFCCAmI'
        b'ftVgQ07IMMF9nxayJnwPjODEFjPi3hpsTyWGK4ZhU+K/Qm1F0o+9l0+voU4LI3DuxBXamyIkeFCqDJM6B61JqjWl6qZrmhB31ZLIeWyJeSHQtP8STMZqpxwTcxcVyUxa'
        b'Qdpk3k6KRWvxAZYd1pRCh55CnAlJ3UaazAjJxKrdQo8Ad2Y+hePDcBxTJ8aaoLm3Wh7UwFLDMxvliMbrSH3fIwTfn0arXbknQDkQBvdh3Wki7zoS3Y9UmU0OfYaBtNxk'
        b'WEOxPmb7uzDko0uNDYQYQacNDhw3R4IzHhtphQq3QLO1EfFnpQPUr6GlqU8itdMdCSOnDYnK60R+ezZA+zo7yAiD/J0Efh1JIhoFmm0gOVEeg1nKMBIpTSfNlQXjwftI'
        b'q4xFMjFeqJh8whZ61PbTEpdgrUEILdK0DrZFr8FBJdM0Z4cra6FxPwx53SSi6iTV14G163Ay2QN7dAjolJAWnYkhbZCmclRKe9hEjZRvOZAMHQflduOA0zZ4cEgFG5Kx'
        b'XyvqvAF0aWtdgYo1eM8zmhrKhPuWijbetJ+EM2hZHsoZe18+vN8vDge3kGjoIRZqCN2C8y60P9XQ6O7syFKfFhBTEv4myVUOk6pRmLuX1DOLkjwKw+uVhSQIpkLOkdTr'
        b'pC15SK1ma68JIi1eBO1KcDcGcuywx4pUQN7tq1B+4BwyP3mbAMYuHNxA4uQR5MSaEJt1G0CrFfF4LXHEMNnUDaHK6wher4XqgAOel11Jgz6ABzggR6/cgTFjPTsyOdqh'
        b'yxl65Q2JkxpgfvuadYRki8yx9CaWsqXJvwaj4ss7DtKnZQ7QZhK06xJOk7LEKu1tDtuw6QDURJ5m9USwSkrKae76WRza4xAIWfHJJBrvWwv2QZfkul5YGK17fAzOQFEY'
        b'DF8h/FxG+K2I1mvEniRr9jY7MgqnMVdq7xnlSGIgDwtuWNHyjqoJifZ61Rgypq2sjUi6fgse+tKv7VDnRRZ6MwxddsPBIE41juOMw9lDUG1KapPsX1dHHPcg/DakGrGb'
        b'gFxNMPHGvGIYobWMLfLQkiJHjOR1hcQssVEmUTPjozmcsSA5XEPEOWmH4waEdE9jhUrsUejbhvVHd0KZmLRbizp7wlErlszF2RvRbm4EB7I8Au2MMSctkdD1HHY70/aP'
        b'QrMyzu5TjCel0yfEVn98tP0WZJDhV7nDRZNkTb2qP1ZFcOdrA8zbn34D7sMj5tVqh2k/miVxShfzFhHU7YQuN32sTfUzObOT5leJvQ6YmY7FOGFI2jHvHDQHkuqZsFKI'
        b'SbQxgGE3FWL9fnqwyIaWNiee2GBOE1vOQzahgmGadPFuLN2gSPPsVLbCwZsxBAJzwq7DXUdSy8XQIsZRA2WsP2XgYkA0028qr7URHzoFQqnGYSUSm48ww5UgTR8Tantx'
        b'UEAKvBJLdmlEnoDss56mB5LjVHBOKyjNhCQ84fJDl05AyWWssPEnq5oh0TG7mJtEIPkmMKxt70ls3LoWHqnA5OnUeHN8sJ0E1xTWQ/YFfHRdBXOO+xNrZJNd8oDEThnZ'
        b'LJtpwas3YaOaijhqLRaeiYs9H2KLdZ4awuP69N4AlClAufZaYrkKmIpTc7fYiZObmPuTVHcGzK6HKXaE1224kay+e2FOjoTfm/bQWrTC4EarBCjz2kqMUUymT1IK1O6h'
        b'PchxxwkHVULwM4QMGo6nrcU2tdvyNINyF6jTVb5JPFdOv5XBvEVCaCo0bSabMkvngC9MGECD1n5HtWt4xwOzDUMUsTsAymOgCfqIkIr9gpnLFLtTmMOL9n2GpO8wKYks'
        b'7LDGvNshm0lLEwY6Rc82+tBk7gThZJo1ATPoJH6pIEWdpxoclnKGOLIZmDIhTNqxj+Y2fwvub8LySFbp9wpRy8A1AyKqvluYmw75JMkJeNw5TQKqFAZS3mIO00KilfFF'
        b'VjjMnFMlQaSGSYrFORn7aW7DUmKDoG036OuGddHhygbYse7ANtrfeRyMhn5Ft1DqZpJQUqdoH05ugHns3h+nSnPKxpZkYKfAmWccoFwOqgxInM9eg3rinlpPaBPTr13w'
        b'KJK6f3CbJGQJfX6fdqRMZRO2e5BE7aMNuIflN3EeZhz0MH8fzFhh2zZvLIxnJ17uzF0VcYKWKHsHSZZ8NTnsjVxPxD+eakzMPr3bN5GorkPXhsZXvksfq7YamWH9juOE'
        b'GohBjhJJzOnF4IQa1h3cjJ3qZD1mn4Osozh9GPqUr5OQqSAIVEkiul1AdP9IARoN3aBalSyFzl2a0Oq8G2ptCTBkGwSswQdb9ygoYN7Jo5ivineOniDLeMaaUFauHY5o'
        b'XsaJnWqeNtBmixXO9odpYdhVJmL9DpL5OWmhxlrsRtY0SYNpyDQmgh8QEjZLv7qbaK7CD7JVOdKYDiExPn9xB8mEBsxNpFXrYrJgYhfhj4qoGGg/QETNPPEVWLAWx/aR'
        b'eVMWDXkK0BZjDA/kYOiQPU4yGx0zTpIYG/e6Rlr9sa0Cget2uGeKWZa0MEP60HYLqrWJNvO2sFNl+ZsK+6IDqOX7DhpYRQBC4RqDQVm6exPI6iNQf4fERBl06WLtsbXX'
        b'WYCFP61cHTy6cHU79FrBrAu0m8lD7WYm9k5Dz0WyfAag3SqEQBAp7332iXvgkYfJFWzbDjUe0GWx6ziOyZNeqXbfTLZtI47uJj3Xw/ik1l/nmC2B7D5rnA/cRtKt2i9U'
        b'I+RWwPpgIpw8zNjrRX3UbHU0OnxLQBAz7yL2YKuLmYhLgQR5qUSJrTC9mM2mS2gO1eacd8mBrGeWdk0NWgRClnYN22LNxJxr67g3jSHfw5M5lw4IaESdPtwrp3EkAiqt'
        b'PVliB+EuAYNPblzKHFravFsn2dEW5ssJhEfZO72QzfnDxIQjemmNhhcdZVjqRAPk7lbVHziPWcaeLGOsDX2zQYfr50xMGM0/Hwu96A07ASGWISs+NU8vafEqY5he5l17'
        b'BE3UGncfJPdqHFFUExaa0Xu+Amy7gT1cgzfwfgI0GmOhN+9iK8OcRN4lVwkt24nJKxZ9cqn+ZnyCHPo0B+tOmHp6UGMWAszTOyjzyq0J8gtZ5pUj49lM6MLVG+LuoPVe'
        b'5W6oGQxphMb/yyxAYCbmPh5OE7GPd72mGBq//shpPosPCPjbbJ/Rsw5qXgIWUubCtcZdWIt9MHxbPukFEll/MLt2qyLId4OzXnb0tTffDQ2PN/447Bsf/+pGrl65gc6W'
        b'zOTf623r2OagpdxhWph87a/3ux1a//Gzho1DXi8fjYid+Nsbf33TznbsX7/49MOXa5Pt48UvZn/yyWs3cmv9+q3O/2lNnJzD939x9NWfPbYI/Dj7typvdRyJ+MWP35kZ'
        b'ftxwfl3e6y9qbu223qD2h382/NNCd/cv//wT3ZR1B//b5OFG06TK9hNNAQm1th+/ZK/553UOmn9Zd6jErdrwv7wDWj6y/u2+307cP2n3nbMPXL5//icDx4s/6XjZr+f4'
        b'xkqPk01gXyxX+17Y/Cb3n+3tv5g8LzT7WeCBLj+TgwE/ivn9XYWGEy95iCcEda96Wf3r5LR7r7j8/sn3nB2cVd99ZLV9xydq754af/P4q//1wetVF+37HulGDJ218TP7'
        b'acSYn8VWmxcd/Ee3nR2tH3I+aO+W8lrXpYc5Y++9XDbW4f56x5vRYzYv71X9yfjL31N46cObVvY/PD76va0vnflT5dk//lUhaLLj3Is1Yxsckz/5++CDP7rOxXq9Uah2'
        b'Y93cVa8kbx3J/hcrv/fJ64EOfUf+eKDCqePVdzvLrlW4GH1m1/nrfW/m/Wqi9a/7Pb/zitOJN1542BW050ZNSbgguDzYJOysl5Z5K/67/a8pBt/U+sXmZvXP377knvHp'
        b'Lws//TxieNsno/0XD2VK7pUa/fCGplvhtdzHSVZhpkYvmr54fcZstuzU1bSOoB2v1UqiDXX/scn8z1Vp8vMvu3uNDP6tL/blUs/f3U+Zt/zoXvTub9+GX9d/+sqgQmfT'
        b'+1Zp0bVD33DQr4l2flv5sz+avPzTM//IUflbqfEnl3VV63zdz+yz25593PLKd8v3/+GUZJ3F6W+t/9lI5vc/15ocLtr4QZjm548OPdz/SvvP0y8PD/7qn4/3Dv7yynem'
        b'Ph5IXTO3++9D6XV+2VMbki78U+Vm8dt6jq94OLxilNo18fbx/LffKXs74MaFqusXHD+6+UrqK6d9nDf2vJM7/5ffBO3Y22amwtcQrNi4RjuNOJsXLcVHcYy/BNUHpXsW'
        b'A1zJaF+KYnfCPu6mmgM0iLmbaizc/em6BkbQxOcouUvmYqmqVF0ZhvXUSfUXakpT1EhZT4kFhmlySmTMTPJB8blHsJM9h/2nueeu4eS1K+oKAoPDYtISc7pccxcJa/cm'
        b'XVW7koJTmlAA9zSV1FVwWPOqvCBRbKYhh/22acksAXYwNJiu9lwYKb6ihaa95RRg+swlLqRXQoowQ1VJnezQUVmLStgt2gkDO/hifPOpUJcERUpXaHQsQ1v+QpOe6sta'
        b'xAkFeHwJa5O30zuRUBKyWuIUuBOQIMubckfn6TI3tv+3wab/53+ZGXLi9v8vf/HFy0NC4hMlESEhXPR1F/0lsBCJRMI9QmPumpmOSEksJ1QSK4joj1hDXkdHR1lrk5ai'
        b'loKOip6unEjP3WDLvnTBHpHQnsVhy8nRu8bpAsv1O46x30P2CZX4CO3wPfxPQYf43xUNgtc7a4k1xDpa1umCbS78p54iM5G5yIL+tlDYzf3E/VGTZ5fa1i/7X2q9GMMs'
        b'ln6PTWcpktvm/36r/89ITMgvBhdTzZaIRe0nabBt/fnl5ZWhjAXsBjHzoxcS6i1hZcAgH0oUr5LlqbFOvJHEycPYoQ+1REmGQoHAR+f3e4tcfcTOWsf7TFxvOPxul4bB'
        b'3VI30V3lLYZZ8sNGL9xJ2GmZaPmCxrszCZKEbzofkHP8fsuZ2ZC0NeYnyzo007qLTp8JufO7lNkRC89oz5H2E4Fnc/2PVh/M2fR23eTHla88VnnNf/P/K+5aY6Mo4vje'
        b'7d6r1x4UCkJtKMaIbe+uT1paoEjpi+NeLVoxBNhcr3vtyr28vZO3Aayh9ChYWqqg0oJSEShpa0FeQjITITHBLySmDCQCHwyJhvjBhIeJcf6zLRi/aUzIJb/b2ZnZx8zs'
        b'zv9/N7/f/4XAj93dnTebTIuuh7/v9iWn47KHqSUP3r4w+nlsXtNvPxV4323aV92z7bM/soyrr7958AFf0fCKuWrf/P7ysazLtclIVeJgklTeuL35xLabj/qv3rhyo+dI'
        b'1ldFrQHr/ulnvhv6GfXemvt70falJnP1+CxfqiF/cPyqZfGj8drtle3j1zSW9LvGax3dd4Qvy3HFyjUDHzjX3M0Mtdy/o69IuX3P8vD+0YfFJ+/lPU4dX3drSsblP7W5'
        b'v67dUHo6N5uRZxV+C9ilXi/8UUMduD1OA2dGo1p8XML9ajSeMTRgc3rteASKee3aZWiIS8eXeOojf40GVJrV+XQ0onYJUPPh9xwD9dxon0zj58R0qtrXXmqNDkN4ErdB'
        b'wh9xekFrrNnC5r2pS+pxsoBan69z6FI1dT6umJlkE2pHfehbK96bA7zePRrq37zPmfK16NC6OSqBuh9T+3lCQwsPujjBo0HD/tWsdhWsB4dF9faJ/B78BWfBnbxnQ7PK'
        b'OGmn/uIJpm+Gh2SVFr4qm91QBnW9TqnHdTtwV65DiOCz3DTcw1M/Bn/CqheYqpwrbJ7SEg36YCtnwPu1ehudPRl9+kIZancWl9CqTqYugQfQSW7KS/yiUjSoxn4FKguU'
        b'cLhZgQA6T6/tNF80FR1j9G7qCg+U4yTEn9vHox1ohBMaNehiAh9jJy9Eh6mvkMRdbhtX5uGEIg069d58lvVqMx602nGXS4N2eDkhpEHnrHhMDc3Quxb1WUE9zkXPutbr'
        b'cNObF7gXtwlopxRnE+/CLLTLCRdFPf4DXjdtdc6cq4XFnD61T87gZIqiFqiwsfwUhxYNU09rhM2y2Q48ZMajU/AZhXop30Spd3MRj71DLY00jst6WTBQf+gsO1RiNupg'
        b'/CKrYxbuc4PjZEaHtPhoJtrN9NZmo144HZOBwwcsEEEXpI/3FKpCaLvnLHeioRzav51OPOigFwyCh14H6irw2HP1XH2tYSvuT2cjpYW+GXaa8TAe08y0cRrczeFBasdc'
        b'YpnFsAoS1ky7XV5do57TbdXQcXWkRtUTvOhBfZBpxx2waHJn3iRnKDMhUC9oe5Eqdtcxo5K2eicoDrq0sKqEM83TouQMNMp6pRrtD1lX2G3u+qX2fA2XOoNPweeyWTus'
        b'ikSdtFOc+bQufYJy9bMs3PQSHh9Gu2yqdNlxWLthXW7Lw7vjHhfrE/yhFp/Gn1riIM7hKkW9VnDFnFxUwR83RiaD6+Q8/3f7/zRDzHwOZsaz6MhRmIosRkZjN7JPBlMq'
        b'M06QKYHHBQploBI2bUI3jJbkw/+eEzb5KVRpUsxWyCN8UArHGuicRnTxRDQoESEoK3EitMh+ipGoFCa8Eo8RXfOmuKQQoTkSCRJeDseJLkAtJfoV84VbJaKTw9FEnPD+'
        b'thjhI7EWog/IwbhEEyFflPCb5SjR+RS/LBO+TdpIi9DDp8gKBLf1hf0S0UcTzUHZT1JrVVqi27eeVk6NxujrQw5sEjeGgsToivjX18n0Ik3NJWVSGNShSJqsRMS4HJLo'
        b'gUJRItQ11NSRtKgvpkgizQJGNkkPRVoqFqiRMsQWuVWOE4PP75eicYWksRsT4xFq+IVbCf+W20XMSpsciItSLBaJkbRE2N/mk8NSiyht9BOTKCoSbSpRJJZwRIw0BxKK'
        b'n0UpIqbJBL2dRBjkoZ5ZYWp758RqwU5bAVAP4AVYCeAGWAqwHKAMoBTAA7AIoBigEqAcoApgIcACgGoAB0ABQBHAEgAXAIiXxd4AWAZQArAYwAlQB1ADUAHQADAfoJAl'
        b'gTjXCFtNAK89pQHCQDI9tager/6bRcXynhgDdKRI/rZ8MlUUJ7YnDOwnmRPpuVGffz1ogwEtFfKkFk+ukRH6iEEUfcGgKKpDllH+foH9ejW2aOwH2LNq0vT9R7BpYlxM'
        b'+z0RlJZASgEdJ0FLjYP//ug0ZTDBv78Aogv+BA=='
    ))))
