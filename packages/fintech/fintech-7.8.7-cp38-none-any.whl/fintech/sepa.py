
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
        b'eJy0fQlcVNe5+L13FgYYBmQT93FnYAYQXHGJgCIwbLK4oHEYuAOMDgzMImLQqKijIGLcd8Wocd93jabntEnal+SlfW1fMulrkqZNkyZ96d7Gps3/O+feGWbY1Pb94cfl'
        b'nruc7zvnfOfbzne++wnT7UcCf7Phzz4DDjxTxlQzZSzP8txGpowzSY5LeUknaxvDS02yFmaF3J6whDPJeVkLu4E1BZi4FpZleHkxE1ijCXi8PKh4bmGautbKOy0mtbVK'
        b'7agxqQubHDXWOnWmuc5hqqxR1xsrVxirTQlBQSU1ZrvnWd5UZa4z2dVVzrpKh9laZ1cb63h1pcVot8NVh1XdaLWtUDeaHTVqAiIhqHK8Txvi4C8W/oJJO9bCwcW4WBfn'
        b'krikLplL7gpwKVyBriBXsEvpCnGpXKGuMNcAV7grwhXpinJFuwa6YlyDXINdQ1xDXcNcw10jXGrXSNco12jXGNdY1zjX+KpY2iOKNbFbpC3MGs3qoObYFmYhc4IrZpo1'
        b'LQzLrI1dq1kE/Qc9Ua2R5Ff6djELf8nwF0HQk9JuLmY0ofkWBZyPrZUwUubNdAVTro0aN5txjoGLRfiVZtyGtwbi9QW58/EW3F6gwe3ZpYU6OTN+rhQ/GoofaSTOYfAo'
        b'uo1u4/v6bG22Dm/F2/JkDG6NUeFWSf4EdMIZTZ7owGdr9Nl4Z4E2W8ZIpSw6NhifdY6AWxa8B+2Pp+/lZeN2dL1Kky1lwvEuCbqH1sdqOAoCt/N4tz45BZ7Q4+3ZqLUA'
        b'6gkdKZkOKG5yDiEElDqb3M/Ow9vxA7yV3FfhS5IJ49BlqGMQPLGgLNlOb2/Lw9tYJih3ejaHruBrS53jCIpX8V10LhhfC8U37Wgrvl2PbzSgNgW+GxrCMENHSwPwffyK'
        b'hnXGwMPSeRW4LbcI7c3B2ySMBD9k0SG8E1+G24QI0MHljXp0MRb6o1WPt6GtBXh7QTZqT8zXaeTMvLlqfCmgORq/BI8TxFBnGtqNrwNeuQUyJgTtkTWz+GQgPgX3B8L9'
        b'UQk18Tk6bZ4ugWWU6KgmShKEbqLL4tvhE1bFZ2nj8NZc0qrgcHQD7+DwJfWUSrbbHEvxEMBuQp/+1Mn8u/TpinVpXHGueJfWpXMluBJdSa4JruSqFJFq2S2BQLUcUC3r'
        b'pVqOUi27lhOptqY71RKkh/SgWoNAtTH2AEbJMGHHxzUp982zMfTistmElBmmvLZc+0DhFC5+kKdgwhgmKaymUftW4EDh4rA6KQP/1bPzGizzoqOZs4wlCC5PGzxI+qdw'
        b'ZvbvIprYD6K/mLB+UTlrCYQbf55+gL0SwNT8NK88+WfJgYtWMvTyihl/DN0dyiZ9XPoR+88YNCKYcTPOJEKxh4C2rgJ5tiXOj43FrYlZQAzobElsTh7u0CZk63LyWKYO'
        b'nca3QwNn4h0NzkxCCZenop121IkfOmwrG5x2fBtfwTfwNXwLqrqJr4cqlEGqwJBg1IG2oG3JSROTJ0+YlALz74qUQQ+XBOKL6CS+68yBqqrxvqX63Jz87Dw97oDpuw23'
        b'Aulvxe2AUKw2LkGji0eX0Rl0oQhev4b34ZfwHrwD7x2F2vEuvHshwwxMCgmHybnOj45I5wbAH6FL+0QPn5NUScRx5rbAqK6RwDhz3nGW0HHm1kr6GmdWrNh/nKX5NkIA'
        b'5vH/cVxqnwZn7Yf+rjcufe3d71zZcXXvSNmb54yLXrsT9uaS127s6Nzb2WJm7V+dDqgMwemntdE7spIk1alMTm3IkKb7GpmDkJENv4Iv4zbgKzegMzrI1JVOY9FVBh1y'
        b'kJmkQg8U8QnQV1u1LLCwQXK0ndOhl9HLDtJa3FY9Pl4Xm6XjGGAw1+XoINw8t8xB+AHeMhZfi9fh9twJMga9grbJy1h8cUilI4oMatuQUbgtC11kQqYz3Bo2E21CWzWs'
        b'm4vVaCQ20lyfAweHx1EzqmzW1aY6dZUgsRLspnrjLLfEaebJfbucdFpGEBvO2uSelzRSd2CdsdZkB+lmckuNtmq7O8BgsDnrDAZ3sMFQaTEZ65z1BoOG6wIH52Qu2MiI'
        b'2mTkQOqbQ2CoCIyHYZyc5dggenSSxuDz6PSoeGgoiw5KGQ7tZzNiwjMruV5IhI7mZEIiHCUSaZXUSySSJxJJDxFGaCGoB5FE5Dsj4XxSlsqeCw3AZ4msOYlewbusFF/0'
        b'IB636eEWq2HQeeDSrih8gr6CWwcPwNeB4bIwZNsV6CY+uMoZDjdmhszDbeT6XEZphklxM57WVDsLtQaDbGMHMOg+fgR/D1GnM4L2SVJ4PLkznynBx/ChQrxRkHovwzx9'
        b'OT5BzrBLGAwTE+jvtp3ewoeBG+Bd8+F0NYMOowN5+Ca6J+DlioAm7IKB0DKo3apFZ/BpTSC9NWYB2j0duhpvgneG4E1QxWmhlbvsIS+QG6cAGXwAn8IP0GkB0CXUEYfu'
        b'Q214H5MIImwf3LxIX6pDnZGY3rnNDAKecxttwluowNHi3egQug89jo8w6Bi8cQTdRw9o74Th0wymt15lxk3Frw5PEeiiE9+rQfdD4ew4gzuW4eNSvJf2DtS8HbXglzmi'
        b'HC0oDMatk2lF+NwMdLcYKhrPTMDXx4fgk/QyOoVapuBdQEBJTGVd0mQYLYISOoDuglKA9wUQbQLAoZ2GJfgylcboPAzFNXzdjq+vZBlOzuAz7Bh0awRlH37ci/NlNIMJ'
        b'l2SamefD1rDN7BbQLG3SZvYlrkEK5LeRTip6OMu5uYQkN1t5lu2ao3S2uINmWMx2R6W1tn7WIs/ElAMUBeOcBafL0T18Rk9VFlH8Z0HPXgcuvLUgH2/ToFuS5GTUpkc7'
        b'8fUAfMUejC8AweJ7wehKKbpnfu4XY1m7C+qx7vlqbPv0cJQUltH4q7BwxbEN1+s37HZ0bszPyJDdWDm3atGH69FDTcNnY14dNBOfn6BMH/vZoobvHNRPttx9fCtNmX0t'
        b'fMyc/bMKxtqPTNpw5ONl/9l27dDkOTO2Lwu/9ifbzKVhE48XXh6eMvOQfvuQQ0Nun338Zt7dT9Ye/ubVBze/+Wdty41PQk++M946wg1slDLCVycNj2eWJ2hwqxaaiy5w'
        b'KWgHanOQ/kQ7n58Ougrekp2bL2OC0VUOn0jGR2ajDoFPHrAOxG1l+IIWFDlQJOXLuNHoMN7pUJObmyJBCBGBiVtBQ8Nb0YUcGRPxnHqiBO/MwBcFAC9XokfwkId/4211'
        b'hIWjHVU9eKlG2p25dhu9YFNdpZU3GQh3pXyV6IFMlpSVsgqWY+gvy/1TLlHAlSC4puLCWBWrZGNYW5gP32Xt7qA6q8EOpkKNyW4jaoGNcKqeGHE2QuK2AV52S6rJ9rLb'
        b'u+G+7HYU6ZNToJXe8ichKYNPhA3GO6WNMFeOPoH1Uunsx3qfLJ+rnk4+Bwp6mKkinBnDFM5nmfKlv89cImhX3yZnMTuYdxcqy8tzvleygMmkV+MHD2DUTHkGV19uaZTJ'
        b'hUeLyoOYSKY+nQ0r177gUDKU00XijXhbShLAygVFahdTUYceml+t/oqzL4a7Jwfe/6L8N+U1VbnGt6pi93627sqBa4tb+aL9LYNSY6KTtPxn/Gfl2mTJtUHTYwYmRx9K'
        b'44sWFcWUHRiTpt0cuUD3eZj+MFEY7sp5bsnkYlAU5Mzo96I2DH9JwzkI05yEbwWKol6OD48hkn44bqc6wvD0mviEbG2cJgG0OLwV1FBLkVq6zDJJwz4d0Q2orDFVrjBU'
        b'2ky82WG1GUSRTse/LIaSngqOQGIRPiQmqTTz7oBKq7POYWvqn8JI99mivBRGalnihfCKH4VpyIS6OXElEFdW3vgk4NPbCxJAP90KLUtEMMVyWWYmOiTHpxV4fw9zwkto'
        b'VA1kgdS61ECWkln/6n4PCU/wHduDzEYJZLZ/Yviy17ksOCufEdY0Q6SoJSPDJjZKZjNMfbl2cWM5U0Kv6qfJZp1lYW7NLrdkZi4X6CwcGn2MI2fl2rPm54WLIwYop34M'
        b'koYpLFe2TpsgXMxbEbnsKFtIXm+2TNcIF3dNGpZjYevJk0tzB4p1GkaqtSfYdQT8jJJhA4SLrySOGfyJZAd5nftDinjxQpAm51v2OAAvHzV5ijhLzk/TrjrIXCF1pg8J'
        b'e064KAmWDx3NAbdUl2vnRU0RLr4/I2hwJAu2JUySzgqDcDGqYNyi28x+8mT6jdEJwsWDQ+PCOpkz5ElOv/gF4WL08zFzEiXlBPoMzQuZwsUjekXZXyVqclE7aWi4eLE6'
        b'dFEYOxWkb3nuqInzhYtxq4fUv8zUkDqXumrF15eWj0hycavIk82F6VLhYtOAUZk3uS2kk0eNMeQKF8/URC9rgFEHPGdoxo0XLr4alRjWyt4hr1eU5SUKF+clTNL+nH2X'
        b'dF34vhyVcPHl4GRuB/cmqTO50xIqXPxl2YSsd5jXSM9zdamjGM0YJ+Gl6Oi4CcTMncDENk8womtUpZiCd6DNKVLiAcF7cpKt2CUoIPuT8PUUjtjFqeh4CtqdJ2hzrU3o'
        b'bgpI8okgkfDtiXNAy6NVH2LSUmAOTGK0kybhDWpBuTkHlvu5FKDcyYyjZjK6g7YLde9S4mMpMEumgP40e8oCvN1JmH4gCP+jKTBxpjIj0MtTX9RTZleOHqE2dB3OpoH2'
        b'lDgN1Jz79Aa6COr2IXQdUE8FHRW7UgfJaPUluB3dIFMknWnCrnR8J8oJmhezcK7NDu3JYELQgYyx0RQkupOC1hHFZA6Thy7OWdBAG1OMXXijHVozl5m0dm5YjID0Wbwx'
        b'zw5tyWSeR7cy0flJQoe8vARvtUNb5jF4q2Mefgm1CpraNXxzABjhTBaD7i3IwkeWCUjvnosPYtKabOZF1JaNN4h9MnTac5g0JYdBG/H5HNA6afUltfg0vg5o60FZDdQD'
        b'438kdO29RNCDrwPmuYwCnczFx+YK6FweC7r6dcA9j0HXTXnogZlWnzgOXr0O2OfDUKXkG8UuxzcHNeHrgH0BM3ZFATq0RKj8NrrvBKULph4z11CILuA22i956OZI4sKb'
        b'D82QzNfH0irseE9ZMCBexKBXI4rQkQwKbxTuWBkMaBcz5XhXMej9F4VOfCVyeTAgXUKsxEcl+N5wAY2z+OVpwYB0KbMAXylNGSHQ1DYbuh4MOC9gGsoW6PIF3LZDlx0K'
        b'BpQXgto7eiE+MIk+XFg8LxgQXsSgHdMXDcEtQm/vHdWM2uBkMehe6OBifA1d8dDOSXQatQHeZcxAdRk6gk5STKrxbbwetXFELDRGLFGMs/zt22+//dlq2dRLAstUfjpG'
        b'ZITHMifHnZS8RyZueIohhDFPnv2mxP5DuPPJ1nG1HdPzJWlhc85XR7eExPxxScjNmFkrfyHZ0cDWzS7foX7hwNgx0fNqxiVnZbzOKlZ+9dr6qfKR2ySjSuY/Up1btvL9'
        b'vZvfXpOCno8fgh7dO77gyNHTJZtu/vTztxe9/Ebq0ZDHyvf4tt+++P6OYZlfXntjVkCM68dDG3I/2lj8ztRv94/7of4vb6GLg9841WBeeO/RHfv3x44Yhsverr5x4afz'
        b'Phy0q2xfzl/+NlwX9/h3jXsKzl2riPrBPxvevfz2f+d+r/q0696PThwMPWgt/v5vWz88s//PhrXML36QWvwfaaDbUlfmGbw+G7dp84k7rUPLggp7Hm1XcfjSCLyX6gYw'
        b'41/KI8pBdhJRD6gX4OUKx1AiDdCDUlDVwDrO04XOyiGuznB8RwJTbScnKK8nUDsPyus2ffbzYBpeBO15KjcIH8YvOUbC7RQ1Om9HF7PydbFgML1KfKK4Q8IMwDsk6Ara'
        b'jV7RyHpVLqS9aQI+KodKVDmclQai71J9w0IELq9kpaDSgs7Biequ7y/7L1z7Ri6XgmYRAzVGSlSgy4SB4kz+26I9OGkkoM04K/tTYljbQA/y9D2e8egvR/0cEsTXiu+g'
        b'jUOJAgOT5lyeoMLkwYHoyzJGg9fJ0C7o67tPUF+IL5TxUV/YZ/dW9q4lBwjqy9B8JQMyXfHBovLcj4bkierLnZhg0H2Z+v8aUZ57sniyoPuuxLea8KUaqv0S1ReMotvm'
        b'O9bJrD0D7tY5P/2ivOy1Kzs6d51t6Ww5e2DCpgmHOrNi8ahNmpg39cZ8Y41pp/RqTNH+NG3D5rLNqtcHy4+n7rUcH/xONPPugJAHxToNSyk5BV/BD0U1V7eIUvJs3OHR'
        b'Y/uhp8ECPdkdNmelwwmKrMFmqjLZwJoSaEtJeuNFhlOAqUQ12RifsZfa4eH+B3+Qd/DJixu8g7/Ob/CTKRvHG5dR7ZUMfGKCJi5vIDqfoNHl5KGtiTl5el0OmE5giSIQ'
        b'WkF4vX3uE8nAX4t9Mhn0MJY8FfuTgVzg7fhSHdoYTBwTYOovWYAOLF1NCeFw40SmpqQoANiv7Ui8hck0f7W5jbVPgVsrFh/4onwpHfCrLQ1sZdAn//h1+uuj7qpOq16v'
        b'ej3ytGXvqFORn5ZvVsnDntu/PmUYo2oPjn38GzBlCDEVB1JmpUtGJ0RuVVJOnaGxFfhRN0tGLU3PXYYuJohD1TcBxHSzYfyHP0gY/kAFGw3DbxvsO/iVTxz8Id7BJy9u'
        b'JRWG0cFnvu4x/NOM+L539L2Wy1p0HIwX39FvQmcD8Rb0CLc/0VqWdHNU/ove7N4IgA50dpxqzkYJ1a+1fwltEOQsP1I28VtOEL468zLhom2NxGFiBXvlwouzGLPiR1ms'
        b'XQ/lhD8t+qL8y/I3K2qqLpg+Kz9jfLMqMfmz8kWv3dkxEpgB+2ZVjnFn+WcRj3juR2+p13Y+H5ARYA8qTnl5asb4jJGFBWDwDmYKC8PM8k9FgxdE1NWF6HxunpZjcEe8'
        b'VM+ia81RDrI+14DWDQKBiLcnFuTh9nx0W5aNLkiZgUXSyegqOvC0Zm9InWmVw8A7TQbe6BDoJEygk7AgNhIEhAIGVcXahnqpReqWkkfdgRaTkYe3mp7gWSHi2zbcSz2k'
        b'og4f6vmjn+U7mjCPO/jUANymn462o4uxaGuBJg+1F2QTsT0WX5OVpaIblRKfcZX5kkuqQC5Suowmc8mr5CLJSKhvWwokI/GSjJSSjGSttC+SIVXLe5CMTCCZC4oUKgHV'
        b'+TU2Z0WIaOblCMtXV2pXaDeMGcqYP/nBPdZeAXfeHnpx2LarIeuSlNIPVxYlpf30+6obu88ez9D8Ni6yqu2KZsG5//qi4NcTf/+d4/sjx7zxs+HPT58+OGTWe+99d+7d'
        b'j6K+p4lb+PD8zl+/3pLzt5lNrbqWlvMfv//fU06UZ//X9t9+zc5sGDSt7jegKxGiMeODaB311wUwHDqRPY0txa+OolynCJ1K1+fjq9ne5d5ByVRFwltXJOnJLG3D7QUs'
        b'vjmeUeBtHNqIjqEO6lxMw7eH4bZc0Hy2JIJckuax6FED2iR4D9cX4VO4LQ9dYBjyzit4FzsPmHp/apG8z1vdKVRZbepGoIMFAh0ExMlJqRYTxCo5jlNw4d9I5bYRXlKV'
        b'EVIF+iTU55ZXOh3WKl8u1+vcABImOp9N7U+2pNIDPmT7ebQv2ZLnItDJgfoCnS+91g0Fc/KEFB8q6Ue+TWVENYcs+TJVsmeQcT08NSHwF9WDXkcI9Hqn4QfMbhaoc5g9'
        b'8FtZukCvafPVJMZj6ruBDTOS5qwSLo4tERZmP1pkUb6Xuki4GFRMdSLFR3q7tlXFCxcfjyJORoYJW7lq6NrwccLFT6KGgiHNxK4ra2o+LDGK3pfxk4inQv3awKZkm7Ja'
        b'uKiA2UXWit8dv8pSMFh0PG62acD6A0Yc4+RmzK0SLo5/7jmmGWThlcim5OOyJNEp8sIMZhUA+mgWnzxvtFa4OPX5VMYBVR+vqCz6paNRdMlMGES8SUnlMuOMj9QiSqfn'
        b'a8FqY2KvDF47asVgvXBx+MgwRk0cAWU12gNpZcLFgufTYMyZqVdM9cn25Arh4sqpwlR/TbVa2xTmEC7WwRjAnIjdsbZRO14fJlxsnjuYATVGUW60zxg0KlC4KJNMYUDb'
        b'Dyuc0hyO5yiEi4xiPnMcAJUvdMQFjBXNvXeW8cybAOijtcbMo0niwCmrq5i34PWw4DXyk+qpwsXW/GhGCxevZK5obn5utXDRIVUxMMdjdmgqcy3mWEZUbF5g/kQGoLl2'
        b'8p3SZuHiD6NEjlbbGJ6dNk24+Bt2NF15vOJ8kbspfY4xX98cL7OPBXpufvuvpS/lFeEk5aZfvfd1wy92nt44btLQTUv+FDR4Eb950LW9C9/f/3zHu0vX7apXvbPe8jOl'
        b'5ZdffZ39h0PfrV6m+0VG06++V/LWywOXHflIuazzykdMym7pzONDmT2yS00/lhWbjdLxVx5/iBsfRP15wOE5edcCwr/88YUojUVbP+nq5M5DY/5X+5+hH9kejJ7E/Oot'
        b'2a3DOf94mDPIWtNhbNyqiyrZPuX5q+fuGHa9/o+Tn1pH/Oj88cxFJ89/mPvgpZMtrT8z3s469+p3lw84fHz7z3SHUx67Ppp37w3by7PenrHxYdYb7ZtrV845MC51xqnA'
        b'+3enVX1/WMOxmr/++uYb7e+tmXlnnHNGw8oM1ZVPg+Jf/HX2su9+M/fTve8faFv17clP4968kM4U30qfir9t/vSPyse/Cli5zXw+cK9GQg3YItQ2iYprI74hSGyvuJ40'
        b'lxqhFik+ptfGZoFqxOLbaD2jQOe5JnQAX6UObrQfX8Vn4uejcyDy41hG6mTBEL2Pr2pCnsBKn3zoh1H7esgJI64w1q0w1FgtZsJYKTdeIHDjaQoJ8GP4G0PVhjBWTRdk'
        b'wqgKEc4ppUHApYFhCr+Sbv+Fs19LhyqBn4NtCrwcbNNRXk4OKmqTyWjzYd79yBbWNtrLt0kVl3z49o8jffl2AlzDN/DZHMq48RlZQQ5IuDa0nYZmdOCtuTBKWjkzE1+V'
        b'E4MWt/QwKWTif3sVHEwkQI4p4/hg6nfnwGLheMnGwDKJScpLedlGpoUtk8G5XDyXw3mAeB4A5wrxXGGSEplQxfGBfNBGBVwJdIFeXBZElkA1SndAGs/bTHZ7fqXcBxeF'
        b'+EfZP1noFEOIvCFFVQpRusi3KEC6BIB0kXulSwCVLvK1Af2t9Pc0pGWiBbUbHx2Id6FNxVAYyYzEV1OFMJH7d8KkdmDIzKK3c4a1Xh2AksKk3xbs3Vjs+u6cyDTZO7Hr'
        b'5lS+Mjztb61Zl5Rni38+5gX79Pv6iNP39js+7Izb9lX844j5I+beTx5+m/vFnYGWGPefvsydvvmbD5YunLL+6+ZjW9Hv5nYox0lCDisvz5ma8vIf0S8PhxQcuD3izUsj'
        b'JumiNEF0buGb6D566J1dN/BtYXaNUggKzKvBqbgtB+/xCz9RxNGb6KICrY8fhtf5LqziDWvprLSNRVdpRBmpV4rOg9p0n0Nbi2qEem+r8YN4dGlCgo6uWaGTXBJ+gA8K'
        b'y6qv4L1gH7WhDtyh16EO1BHABAMRHo7msEuHtwp+r3NoF9qN2gpg0uP2eE3qCnROyoQGShzo6iSKweKJqB214XX4FDyjRWeljFzBDcrE56mVALbV3kWo7UVbIuhtCdmC'
        b'8yUcn5Lg9QDqBu2c4nrcgdrASM/J0xHH2gErbuOAA20I76nOK56ar3TxjQCDoc7UaDBQbjFc4BZrpOLSbTRdVSMhM3Lxd3WoSNsJ4nsCB1C4JZUWO11AA3PV7GhyK+qt'
        b'ZI2fN7nldofNZHK4lc66LudHf1aJ3EZiRG1kXVlYkiMeKxtZdrPFeVkHWfL6xod1bB7swzp6YOmn4LHiH5kLdqoBMMsZOnXZ/LOsW2EQVwzhXGo3Waq6ghqELlPMsBhr'
        b'K3jjrBCo5Y+kxtVhHnieW08FsAoAali3zEB6zKbzQvGCsiXCQQWv2khw3FPVWS3UGWjw9H+f9YY+U70irgEGYTT7rDWs11r9dGrihCA+I+CfT69Nb+zNY8Qx3fmdJN/8'
        b'5Z2vZHYy+WYVrPyi/LPyl26/BTa/suqjXAkT8TsOLZyoYenktI/BN+jkhYmJjg4U5iY+jPYLNM31Ol9CzHYfH15XYNmL8Bu9OspDB35PCQExEhsRaD6E7wtA5+1E4lEL'
        b'h76zhwuEvY75ncqXtHsHAYye/GiCgXwNJKLNYHAHGQxClDacKw2GBqfRItyhkwdmqM1ab7IB5dFJRudc10ybSBtLIuCMdnulyWLxTPXu0/UsITbhMXiENoHYHH8lPUOs'
        b'WoWM0tO34QOULP3lOCFAdwi6WGvPzdYE4j05ugQ5E7QcWGt5SI9BDhb/27exPjKcLZPsluwO3R0GfyG7Q81cFQdn4i/Ptct5LZHxPuG5YSBfiZQPBHktNclAygdsZECm'
        b'B7ZzIOllfBAtB9NyAJSVtBxCywooq2g5lJYDoRxGywNoOQjK4bQcQcvBUI6k5ShaVkI5mpYH0nIIYBYE9B/DD9qoKFORlvBEnxjczlKclaCbDOGHUt0iFN4dRt41hfLD'
        b'4W1JWRhteSg/op3jdaInRcKr+ZG0bQPg+VEU1mgKKxzKY2h5LC1HCG/vDtitqJLslvLj2iV8AtVChHB70lsqV2hVIB/La2iNkVBDHK0hntYQxUsoR0gETaeSMsvH44PU'
        b'Pj/iVWEfgN8djdwtNYOa6pYSUuyN8vIrA3wGn8wWlWeWkwhdUWUKJB0oDqwnHltVpRIZSgBVoBTAUAK8DEVBGUrAWgUwFAF96cdfA0X7oUd+suvMDrPRYl5NNjDUmNRG'
        b'sTFmEF/GukqyA6L7K6n1RpuxVk0alqqea4a3bPTV7PS0fLXVpjaqk3UOZ73FBJXQG1VWW63aWtWjIvJjEt6PJS9r1enZGRpSRWxaRkZBaX6JIb80L31uEdxIy9cbMgrm'
        b'zNUk9FpNCYCxGB0OqKrRbLGoK0zqSmvdSpjwJp5szCBoVFptwErqrXW8ua6611poC4xOh7XW6DBXGi2WpgR1Wp1w2WxXU5c21AftUa+EPuNBkPVER+weMuKpFC9y5tlm'
        b'4uleMFtAWPX5siiThffFAvRRcYEuZcLkyeq03MKsNHWyplutvbZJgKSOtdaTHStGSy8d6AEKzREhwlnvGD9NPR5ZLNTlKf3r9QkyWKhNOP8X6urhfu/pS1Xm010t6JgM'
        b'DNw23K5NIBtBUmX6hXiLnu5ZIR409GAyuke9EalsBzOUfXeiIqlclTtlAeMk7rPZ+Aw6Qh2QhXgLUcUT8VY4KygW6ijNIou3eXnZeRHoNMugVnwiEN/KRFcF385A4oNK'
        b'KlSpy7XrJk1knKDjM3Vr7GQ9OF5P4x03jcidnyVq4KB/450adJYpTgvA+9Bx/IoQCJRNNji8lx3KlGtnL4sTXCevZ8rAHtuxnJtdrv3BjKmMYG+erkondeNOfFion2zj'
        b'yQXDE9BNLMrCrblyZh4+JcdXi/FtuvJY9gJ+ZG8gYdQdGUqC/2V81Pzzu8Wc/V242/hfJ8Z2TK9LnxA2942/POj4euOcEyPjywd9uX5y0eD4lzbMMcbmtRz6+8odf7hr'
        b'HLa47FKePXNWY/Op9S3/WfWH3+37bemG739al1Rywj3wy+xPjr4zqfqT9T//0Rff/55kzcI1Ow4dd1W0//4/qoZETPzT9AN5L62aO2XJQ9eRGbVXdx2d91nA+G8//7I1'
        b'9we6TeNO7zP8ZfvNKdnNY85+nffOVz/7ckPiuH92/v3z+F+zZbm/fe0P9tz0P8htrD4hY9L5152f6D+Ro5+tb9zZ9nrp5Lu3Htxqv62e9/sPv/317pzxx7dqwqlZMjN+'
        b'VDB0jybPqYvDrYkcE4VcU1dIFWlVdJ1sbIDDGw+wFN0XQgI4fKkCnaMe7biEIH1CTp42G7Xjjly6H2gwuiF9obhu1SwhYOBugpwuwaGLaeISXBra6aDRnfcbwSbzLGB5'
        b'Xo/CG9HNQRJ8pwnfEZzmB9ErqLP7Yl3ACumy6U0OoqnOGoxvwVBDDfF4awHofVu8S6J6aNR2IY5gHroagDoy8C7B4tuITzQIfmSwRltwO1BD8HyOxGqjR0K0wnmFHCw+'
        b'ilWVTsLI8EEW30MPcBv11A+dlwMqp3IZpSMJPsQiAqeTGqQpA8rJm2RSVOFXZfDqPY6difbR5gRV4wddliaxM9EJdIjYmksXOYjcxHtU+CFYiuiGEbdr6NYwoXuFiRqP'
        b'rsvwJnQKvSrYzccmzIHqAtBBvD2XBUyOsWhHFtpDFWO8H11vgLuoQ5eQR9C8RXZqXQI0aR/cQvusBNE8EpJB1irC0E5VtSQVHUFHaOXR+O4SeB10O6rYTaxXZUgyM/Ex'
        b'+rqEw3fI21roZxqXi+6gXSp0RjIH3VV4FsZU/7bXrLveDmqxGQS7aOhmeVT2CQoaPKrkFNQZJmVVnJKN5ohbTMkKEcwkGEPe7ZeDX3r2jVwOxp/AdBM8IPIFTTlQUPif'
        b'I4fZjMeY7aZnd5kDT229awKESqL8a6d1Jngrppp4OhxG+BkTn4zzNSZ6oP4shrLMQBSePi3BRR5LsAuKxzp+PLbEqx0RuQWahEdwxdpMRl5nrbM0aRIAhoS3Vj4LTlJD'
        b'hbmyT5SWeFB6PIYgALpVv/CfrTOoQtsX5GVeyPH9K0D/GgK2eMZjRPYC3OgFnuCrPf078INE+MtZj8+BgylmFExTgTz7wob374r+NKtnR4W6KThbgXdC9IVFtReLxKfR'
        b'yZ4dk40+mGj6w2S5FxPdk/W5ZyWOGkqdAhZ9IVDrRSCphBopANvXV6cWh1VtoVu9+8Th33PySCi20scneiiqGcTIsKvN3Waq3WSqpVvMwbKhtkePF8m2c9HgKgYDB1o2'
        b'12mzqguNTbWmOoddnQYt6akXx0JzodHw4srJCckJSZr+NWfyI2N6+t1LNOLev61417h4Kumks9kpanQOXVOZM6QRUtpHhSmFX5S/VZFlfPPT2KLPyt+s+LL8LfuaCq7i'
        b'08jXI08v+1T1+iq5umMkjVH67unAiXEvaaRUIYjHlzP95CiRobXolTn4fDDVkyLwUaJhb89Kwfu6q0qgJ+nQesH7fgrfWYvbcr2bsvHtYHQI3QVdgKA/cS2rJ8oKKAD3'
        b'GG4Zm4iOoUP9OcgCiF/KszdIjGp6kVkZxEYTt6woCMRnBEFpm9S9ti5vGFm/qvcTYDtV/o5e/xpBgZgNDz4hYol4DBgX+9QRSx7adPUghWKTQ/ASOC0OM9jIImt32kWj'
        b'mOZVcNiMdXajT36EiqYeFZE6Uqm/JLU8D56BquCfsdpkK3+C6UZ+ejpCxTCYxXHbwSJjYo5bKhKco82CRTZjxGA/eww0uoN92GRegwzdwwfMz424JKMhERPe/fKL8hyg'
        b'WW3R5+WflS+v+pL/Tbn0h5pt72vnxo1VamavjCg82TLtwsajEzYR2g1h4r4M3vdRgIYTVlce4cN4Ww8DQor2NijQJtDziQBZgK6gG6DQ4vYsa5/67LU8Me7pScujdpPD'
        b'4BkjKqp9o6nIL+vR+VYP8tBUj3fyPcComkUIrf/oKvpEgpeYyW7H1X7EvMU3vqofwM/A690q/1f7ZPub/eXO0xJwgme3FDFn+g71ooEzNGiGuBa9gTNPCvSSUMkp/Rhs'
        b'kp6eOe9ks9rM1eY6owPwM/N9ico6U6PIxCckTOjF/9G304cXPCu06Z5wTQCUoC4yNTjNNrFneDirdKh5U4XZYe/V0USmOmBgt9Z6lC4zyE+jxW6lFQhVC51bZbLZ+3ZD'
        b'OSsFjDLSs0EymxucpD5QVmKJFFbbPFgBrGyHkcjlJ3OMnrGWinwnic9LDxmizyfr7DQHQ75uflZCTmi9uL2tCG/JnZ8lKdKgs9nqZRU221rzskAmvTq0Fh0Z4SR7iGah'
        b'7RME5wy6gc8KDpQs7/a4IrL/ZU8pyK09bAO+qViIj6FbdMt1Ckzt7eiIDl9XwtDjMww6ascHnWQG4Y4J6Ihd5VyQRVZIS/EW7QK6/t+GzjYtKcnSEjfNtuxc3MoCrzqp'
        b'WYX2jsGnSziwiNFtZWF8MfUZoYf4zPwur1Hu/HqhQuxSQ52FC3ULApjCF+Xo5CC8yTz1hQdSex289aOf/kX31n0SFjh3/ovIymYaw2LWvR6VpVFEhLW+EX1Fs+D4Ve2I'
        b'5zO2/bRuSFi0+/GR9pQRyru/6tTPDhv49s7NM/fPXh136VRr3U+ePzTrcGbnl3/93WJz1ENT/g+/ivrTV9988LPZa25lRjh/Hbzkl+rrzX/VBFLJjvai++GEQXeifR4T'
        b'O7iOw4fw5ReELQ8xy4LjyJYJwhQ9/HOAfQS6LsWXoaF3hPDUXasHxetiQ5OzvFsuDuOzgpNi3xpEYoDnLfV6E5RhkqgwfJoiUIi2D/AyZ4vDy54VWegBdRCsRcfwCY/O'
        b'EISOCblcUGsUfT0MH3/B63dB5/BFT6D0soEvCs6d9vmF1JcBs3z8cMH3sOx5IZIR7YBmtxUQvwNaXya4HqY3ihGDTxUIQ5hnF4PwbBUd1cXpIxRguQvcXinyfKEk78aC'
        b'/WrJ9+BA+bmXA/YnACQ+j3VJgefhsJUVV8eoFFjHfB3ZpxzwQ+Kpl4CpKQycrE/u3+nl/hOoFdbF5vozPZ7R8tBQLJx9G+QnvVhM75W/ZZRmdHfp94IPCUCqtZmq3HK7'
        b'ubrOxLsDgTM7bTZQ8jMrpT64Eg+30sP4MgUJ1ZVlinEFi8E4yiqlKK+kW2Qgr2Qgr6ReeSWj8kq6VuYjrw70K6+E7FqCVkdZv68h0/d6EmmTwPg973r3DPS9NEB7QHiL'
        b'vgK9R64ZiSmXoM4w1hF7ySjeq1gOIqxX2UVWrUCcFBdMnZw0ga5XkbUknpinYEr1Cd7b8anqTIuxWt1YYxJXw6DBpM1dT3ga1Rf4OqujFzA2EzSkzp6qTuuuLpeLzXkK'
        b'4dfTXgvKd6YRznRwSLyv9FNodPPxFtHRWZoFF4tEYcYmh6NdaBe+rsfXc5ix+KQKH8SbljunE857qvF5fYIuLgeYq+/r3oqzckpjxXwPRMPeSfKLDFPiM9NnUKU9x5zN'
        b'7GCYpKTS4OBTqxcyTrIYr8Hn8blellHUs0Fp1+XkFfvq7G3FgfhRMUexGW3Em3EbfYI6u7OJuIwnItQrC+FGljYnNyFbFydncJsGPVqqbCjE2+l+kSXD8Ua6JLIBnfK+'
        b'QNpD7IVYYOKgkms1uhwZsxq/EojaBw7WSOgCPz6Ss5YCljD4JdQuncWi83hdlJNanYdGSOLpu/Xoqh5QVuAD3AuoBa13Uuf9LXRxYTx6FV3LyRM7kmUixkvwoTm55qW3'
        b'3FI72eOysBoPe+d+CE5SSguLDG1s8ibXm2Gf/+iD9nWMLSLsqDrnO1/uSHdP3H0wfni9a1fJusvjqy78LTP7e79LvbZoWenbJYmdFbdcn3zw+bVD0d9VzdR++JNvJo4f'
        b's2/5ql2xJb/XF2/7gf7M16q4Me+lB/zP45rEt4Z/Nvjme2l7h7546zcdawYlDt9x9MU/Fe05FD93wW0Q3IScXsicpseX51O5xlWwE0bj2w4S7BiCH0b7CexCfIcKVVFi'
        b'P8LbhSWL22gdGSuvYx3vQxep5NfXU7k7ZRJap8/Oi8N30CugTXGMArVxaH3pdAeJ3JqWjW7621Qgfo9TwY23LxIkbxvejXYJlZcNpHsM8tFVQSfYi4/SpRD0cm4BDX+V'
        b'W7hRqB1do277WegmaCNt4Su1oIQJ2Ua0MCSJErxn9UIB+wP40IvofL3f0gBdFziWKchO5f+RLz+YyEWRe1DhntAl3CfKaS4IhVe0B4l/SrpZhrjtuX8EyVZH+MpYsS5R'
        b'xMsFYU24ho0EXNtM/nI+8NnCd6VCTSavFsB7RWA1HF7ppgp8MMpXFegNzWeJ11J4XupTBL/pFcEjicwAjkoliFfk+Lr7NFIaZMTBH5upibYRZ4qNbLezEXOPxBLy1kqD'
        b'gS472EjyMbo84ZYQn/xsUuxlBcQd4PEaE18PtZHdIf4WLNGYfFSpavqWp110yAb8H60X9UVytplwGERGajOcKDipNFLYwPutlGOE4fh2+GRKXP+US/7F/1JVkJIND4KS'
        b'kEFHGsRGRnd/JpxVjxDOBT7akYUf2HPz8XZdUiLlkkGrOWDzF17sIfSCxP/2f3aLo+K5MikvKZOZmTI5Ly0LgD8FLysL5OVlQXxAWfBu2W7F7rDdbJVkdxivaOf4AlCT'
        b'gl1hVRIa/0wihJSmED6YV9J4KVU7V6aCcigth9FyKJQH0HI4LYftVpkGCEl2QP0iQTyhrgFVCj6CjyQxT1Bj+G4VwA3jo9pprDZ9bkAViaIaKD4RAXWS+CkSkR0Jz5B4'
        b'qsH8kI2KsijAjeWH8sPgPJofzo/YCMyOxkcxZTH8KH40/B8kvjGGHwtPDebH8ePh6hAa88SUDeXj+Hj4P8wlh5q0vA6eGe5i4DyBT4TzEXwSPwHuq+m1ZD4Fro3kJ/KT'
        b'4NoosebJ/BS4Opqfyk+Dq2PEq6n8dLg6VizN4GdCaZxYmsU/B6XxYmk2nwalWAohnc+Acw09n8PPhfM4ep7Jz4PzeFcgnGfx2XCudSngPIfXw7mOLxTdLxI+j8/fGFiW'
        b'wNM0XZr5bnlaLQ3cOuenLREOINwQYreEzK2gCJKUetU2I9EABfWtsskbTtQtaMc/EswGFdSaHOZKNQk2NAo+0EpBC4ULRLGEOgVfiqVJba0TVMXeVDkN55YbVhotTpM7'
        b'0ODBwi2ZW1qU/3hGjcNRn5qY2NjYmGCqrEgwOW3WeiP8S7Q7jA57IilXrQL1uetMxxvNlqaEVbUWjdwtycgtdEuySjPdkuw5RW5JTuFit0RftNAtKZ23KPMs55YJgBUe'
        b'uH6eL7+Vj2bChDl7EGHEa7gtbDPXwvLsCol9eDN3nO1k7HEOjueauWiG5OLdwjUDMa9heUkzu0JuK2tmSZAivMUel5AMvrx8EDwXw0QyU5g1bJ0C7geQsy0Mea+ZMUih'
        b'VlknsH2DnFdQuyvwY0Nv1kj3uDZxnLvC2rq/0JeOT3tCsDCMQh30Sj/uK6HLUmnkWHGBbmLyhCm+ZMSDYZJdRRR+tb3eVGmuMpt4ba9mgdlBjAiQhZ4INgrZYyEKJAt2'
        b'is1c4ezDsEglt1PLeVOVEYSMl4zKwVIxV9aQ2s1CPwExinCAwHq27XMy5o+jzHV06amrNePH2se72QQ3m/Q5kR6ffws/jyUJSUn5mgB3WHewZLXEaKmvMbqDFpCWzLXZ'
        b'rDa3zF5vMTtsDUTOyZz1ME1sNob6E6j+QAjMtobpd7c5FcE/96oWQVIQGZGiq0PNEY1odahAAM+29C+El1PU+tQo/uxd+PeA8K7767oTDR26pnqTuhyGpBJkviVhjvC/'
        b'vDzBRkz0p9Z2zrK0l/pE629eRWcIjT7onRB7gOM84MJEcGQOL+eCvT4OCR0Qt8JoN9AYT7fCtKreWgcWbp+o/N2LSiWNBnDWVoCNDF0h9oG63mKsJEutRofaYjLaHepk'
        b'TYK61G6iZF7hNFscOnMd9JkNepIvLydUauSXO+FB8oB/LT0Xaf13IbE0f4M34bZ3FxJLXfX9L9gS18f/9sZsSuuJciYwGtOqyhpjXbVJbaOXKoxkbcEqrMvCU0Z1vc26'
        b'0kzWXCuayMUelZFV23oTyIwM0qnQsHRj3QrqXbc7rKA6UrZQ91QsQJz+HpQMFKVy0rdOOuUFBkM4kderDn1LAl97WbEjadBNjhprl/zSqu1m4KViNeQ1snzuGz7bVxvF'
        b'ilJJIvXUclG09rL0169HpMJqJQlr1VW+rhcnHQq+2zD0yhwbTTaYnitBLhorSBxAH04YP9WSEJOU6e5PUeU7CaHjVnwPP4rXZWVrie2rX0icFCTtzDZ9Ad5dUBqbo83W'
        b'yZnacAV+hM/Mo7lp5uM7E8GGvIJvzo/N0ZHMwh3x+egmPlGkw6c5ZuI8WXFD9TJ8meq/E9BJtMGOz0xLyMvBexrl4Uwo2idJQFuHOcnkwy+NBLvWx+sfm6+Ly0M79Loi'
        b'T916GSipCnR/9hiaGHwRvpxnjxUzsg+ZLkMdLL6CWvB5mncdd0zSFaN2vLsUt+M9pcRvUYDWoYcsvgHWcWsm9XvMRi3oth0QkjEStB+9lMOidavxbboPHW8OabBnCS4N'
        b'vQO3oktSZgBgjC6gDnRSSNrqCkMueyzNhIRP462yNSy+OCq7xPzm1jLWTjK6fYlLo9qn16XPV8757d9/lRZ+ZsfPl2W9oTozerD+pXRZ9qYv5UVlE1YNurX7VzyrDfiw'
        b'7pfT7Bd+su7dAWmHOk9f/mXN+2mzz0flKI+eyNg8PShp0akvY9/826vfmkv+d1XG2z8ddPad2W/v0lUcufHBL49/fkf565xkp+aYes8Pl9V8fMfV8T9X3p3YMnFT1n80'
        b'ffPZ4d/uOTT6r8UPv/lhTtAb7R+o7rg/qAl7Z2H+x88H/P65HzXMnKq7+j+rFqGHe15v/+KsYXjlP1QtU5+7M7T88Rouuei5Qzn/0AwQPA+ttegsTfCE2wIYqQ6dQodY'
        b'dBFtW0SdHgXoEd4SXzOV5P7dmpiF2yWMMlMiLx1BYw1L8X4YgLZEuMsy0kR8LY1F18fhl+hqAjqIz8yMz8nLhVsj8Q18kEVHkvFdem80vjKZ+FLyAhh0Gp+RSzkFvuZ5'
        b'7yo+OlNPUYI3B8rsLDqBNghhFen4EWoNjpsMVNBtBUbw5izKo1jPem5mfIImzkNJofgaah8vaZqWSlM9LNLN04tpHtC5hSw6NhkdoM0Z89ziePEVaT6M/hYWXYEptF2I'
        b'fH0JX2eJewXdQLuztUDliWRmQTVqtRTfmoXOUXdTNToyVt81zwy4HbUnChMtDj+Q4Q3LMqhLBx+2LtbjvWiDkFyLTBCWCebJQtPpQdShhdaX4536giqjjmW4lWwa2lZE'
        b'sUzDbQM8+zWZjPnCXuh1aAvFMgXtxtf0eXp9XgLeqkUPZ+s9CULi0HYZuhy4gLqiBs/LxG356KJWzkjnzMYPWPRqKD72DFGQ/8puxyiBGRr8+T/nkYWiD+lFRkXCPgXv'
        b'EQkPjaQhoGRXpOBZUglBo+JVEjhK90YOFdWdXoHke7ZP0X2N/0rYJyu8SrWInXD4tpvnqMVvC2S/yEBdRIHsO0yGZmqh6b1AL2B9MrVw9EMa/YfKEK3gp71pBRmCWBP3'
        b'1QhqIFFdQMoQSeXVxETlgGgKdlG57ymExFWEbtpFN12id92hp0gr6amnGIks9BPdHklqJSKeLKE0ESWkJ2bGyhphNb7WVGu1NdEVnyqnTZDGdvoRlSeL9e62k7/O6hOq'
        b'6DDaqsFQ8TzZ75pJnXfRRKAOz5qJR30iSo/J7mvlP0H6977rXCEEH72QStO3Me6i8txNManCtouyFTT/SJimuHxoSvUC4eLVolsMb/8dkOPshvfgeSF3vAbtshfiyyEh'
        b'HMPi7Qy+qEdnnPPgzoDZ5NzL4aga4VmdEUQrulRC1vQXgoQn6y0kRqDyRSFKABjR6uFhqUvwRnNV9myZ/QxU+MvrV/Lap6tQUtic6v9WjWxOjRzQcOFPJQta71yPnRJS'
        b'qA0Zf/yK9Tvs1Jhb5s9+vu3nNbtHhw+/cGHluP/sXDh9VEpiYUQeSt9Q/057VGvehnn7ky+GD/3HqrphLwwZV/uL1D21jRtTbl5t2DX71AcJf/7OYis6v+O12x83vX/3'
        b'9MnhU+7tvBK5T354x5pLf5l3995XvxkS8Ydj35eo3o/Y/vc/HN899bK6qemTAf/zj+BVJ6a+3/S2RiUs7b9swsc9uZbRwcFzOd1AvJkK00J8tFGfsGqMpxukTOgCiQVv'
        b'RcccYwhHP4Dv2Xy6TpQMgUEe2YA2jqIicAQ+J8Nt6Bi+60lVxJbiY6to+FadboyXv4vMHZ8u8/D3rBDhAw6usiVExqE76JGYzmhFkxDf4MKvoo3xnjwbpkVSJhhd4/B5'
        b'9GghbV5uID4JMmkLCPV9C8V0RvVOemulbqggH2eQrKXSfBCP6NQSKndQewOIZpCOXsmIro/1Ckdo+C4HCQRxNKPbVCHNBsz9OoIDGd3KGhIVaIMO1Mpb6CWhs0+kQGfT'
        b'dRUZI19uRw+54Xnj6DYXtKFprLjiwhT7xLEpKsfQFRl8BLXY4rXoEN6YBzqomJw9FO2S2NCGyN52vj+tIAsQLQQqumb4iq7JgtCS090Lym85LuifHKf4JycJ+wcnJYIq'
        b'iCaXVHkjIFTsapUoK8RK/cPc1vjLq35Se3DCs12hDuSTObFQlz26S0qtY9y+2Zm6w+5hfxMOQ+1vUi2xv+GPeMoG86yDg3NJCxsND/CcX8mTZPAxN9b8WDo2IbkKmkOw'
        b'cysNdVaDaCHb3RJjhV1wqPRiq7vDDN6Fb8HxmMN59ntz0HHc6oEeH0q353p4B70rzrlw2EK/nNDC2TKbWdoeZoXENpu0yxbXzB4n7WA62TVsXbRDwrPNtEyerJIIPkM4'
        b'l5KvL9A2cvmPx3sFZ63ZDmhU1lCRMxY4PnFHUUuZnMDY0S6IMNfWW8yVZodB6HS72VpHx8odWNJULzihaKeIHie3jMpnt0Jw4VptfYT+qgz1NhPILZOBPj+f84Q6khRg'
        b'QHkqjlCkHMZ9dZSn4/ze6HXwabfRhKbE6QldQdyey9kqLlrY/QAdEC7UFksaqRWaanvBO6gqfywVBgPAtBkMSwl+VAPydYYJ9/omw3CKiYcQfbEIIGQGve4Duhs9BRjI'
        b'ln0D3YTkgazyQqa3/FQyci71AI6h9H8cKIFnO7k1tBOa2RWCHwrAszPOcrZjjOgghHM6D4/0gobcYLA4DIYKTpTZDIzO6hAvHuTeM6PhJUZuxkzbKQLqdB+QTQZDVV+Q'
        b'Tb1A9tJAgu/UGeWZFCs4q1rAAdgC0UbpdXJGnZXCYBBc+iBaQMnUYDAs5zzh6pRYg4Bx+iBGnuiBmNczqKRdQoAqPV5BAUAfXVAHzaz3IYEuOHW9dcCTul7q6Xp2Vr89'
        b'Xw3jau+j56v/lTGX0T4mYz6r/zEHs8PQ2BdkUy+zzRvPTrrWM+u7/LxdDLvn3CY+MIPhhV7ntnDPr51+CuyYXts5kCzjMJQNcy2cp81s/FlJ13SjjNWT4uOI92o39GD+'
        b'G3neYFjrFSPUiPThAfR2r1PAh9IIgp2ePUbQHTf76nrC6miNLb2zup7QnqI7Yrp3B2V+rM5GstfbbvTebLuzwmDY3Gez6e2+m62iiAR3NZxOsVv9NZvW2NZ7s3tCkzA+'
        b'fIZY2V4+o3IwlKdAObJ7w2mMhcStyrc6skGimsiuIhPfRQ+0M/raJmMw1DqBGLdz4koGQ9U2v16hDzw1MYhLMw/66xVa4+7ee6UnND9imOHbK+qeZDHE209DuvUT75WQ'
        b'bGIXkfTRL8EGg8PmNPHmlQbDvm48mYPeCfci7H3sX8d5sBfnwX3izCU+GWkliDSL1Wqj6BzrBesIL9Zdz/3raEd70Y7uDW1BGxj7RKwDaH4gg+GVXhD2IUJrdx4h9cW1'
        b'kPEXyl24Ogi2ZHUb8Oo6X8qt4dZIRJwlLQR7iXBW5Yu/Ww59BKBBa6c89ruML6P1mCaE0bpljTVWi4nE/NYazXW8qS/tNMhgEOo0GC5znuzotMVKjuzxDvp29QBvqz1P'
        b'9q2REj1QkEzBdDBa/DWO3qQTzbVWbTDc6VX9o7eeBl5QF7yqJ8Grt9oNhvu9wqO3+oYXSeE5BFisl+eJS577/cajL+hgXBkMD3uFTm89tdyn/P5KP5DMdaDAfKdXSPTW'
        b'U0Oq7hdSIJ3ARqjwuz6wwnxnN7lpa2F6ca76zW8yS1YwtjAHWK40DoTlJbyUCJmBgMgaMjuIJcht4TqF+SLOEsqWZPmfk0ofj6Lrv+a6anW9tVFYQZ6QJMRROOvrrSTV'
        b'z2MuKcHNToAZs8UzZG5Fg9NY5zCvNvlOJncA1FRtdoBNbFpV7zH/+nRAQE9Q4AbDG13sQ0Fzi6p8e0R8SJBNpFs0id3CBm3LxfrsFquD5BAjIXZulb/DGspVVaZKh3ml'
        b'kGoaWK7FaHcYBJesW2pw2iy2faS2Q+SQTg7T/GjUrfAa/cHUByqsuFJPOjV+bSSDtMBtOsnhZXJ4hRzOksM5cjhPDhfJ4TI5XCUHqn3dJoe75HCPHKgQfpUcHpHDd8gB'
        b'k8Mb5EDW8GzfJ4cfkMN/kMNb5PBjTx9rwv//BDR2CxKxwuEtsopAAicUEqlMyklZn1/gi5FRfUQrykgw7fDxHAx5jJpjg+SqYKVEIVFIFVKVXPivlChlCvpHrqgU9DcQ'
        b'roq/9BPU6EoAvm3H23A7jV/EryQwihjOidvwrh4hjFLxv/29biGMniSqVVKa0lVBE7zRlK4kzZuY4I2mb+UDaTmAJnyT0YRvAWKCNyUth9ByIE34JqMJ3wLEBG9htDyA'
        b'loNpwjcZTfgWICZ4i6TlKFoOoQnfZDThWwANiJTxMbQ8iJZJUrfBtDyElsOgPJSWh9EySeI2nJZH0DJJ4qam5ZG0HEGTvMlokjdSjqRJ3mQ0yRspR0F5HC2Pp+VoKMfS'
        b'soaWB9KUbjKa0o2UY6CspWUdLQ+CcgItJ9LyYCgn0fIEWh4C5WRaTqHloVCeSMuTaHkYlCfT8hRaFoInSSgkCZ4kQZBMmZqGPzJlI2ngI1M2ip9NWX2aO5RsmCnp2nT6'
        b'8ZXuq0me/Zk+D4nZ5ro9RsIwaExIpbGOMMYKkxjx5jDTtRxP5AZNa+aJhSPBG8Kiicl/eUdcVPIP1iBWlM8O2XLCho3Cnh/eWukkVoG3Zr/arDZPhWaH4FgTXvWs0WSk'
        b'5ZXMEWso7yNQz6+QXSVGnhjVFdQNCNUJS2u+O3i1AkhPW8VgTIfNRDrErz6jncZ+EuRoPMhKqMlosaidRM2yNBHB47c12O9lP5FLrD7CckgQhb2CpCdnbWFEBg5itnAr'
        b'Am0xHjnooP7PTnaNhAeZZxCOUnqU0aOcHgPoUUGPgfQYBBoo+R9MS0p6DKFHFS+BYyg9D6PHAfQYTo8R9BhJj1H0GE2PA+kxhh4H0eNgehxCj0PpcRg9DqfHESC9JQY1'
        b'z8JxJL0yqpk7PrqTmcM8vxS0XukaWbP0OMzRTnYHawfe0ywdyKyR1g2mV+Xkqm0MHwBSfmyzlLgV10gd40DqS1s4eH6GYzyvaJYK/l9HLLneLGuRsEzDl1ugdctVW1j6'
        b'3FKHZgNgQBWZwHzb20RLmCRMgB7Tpf8JQcVEpps1uDmD4bHMMNY+1v54bPdKaowkWqor4Epwvsa5lUUg/s21YkCjXFhlFPKOSgxm3i0zOE0OG0kZI+xvcIcKycu9G9xs'
        b'c4iAIl95tRGXuY0s3QhpTMqoeuC/LxJUQGE5GWqsd9pAtTUBCKoaBFCPvMPolhtq7dUU9AqyV1BmMAn/6M7BEM9r9GNf8FJlDVkKpflujQ6nHfQTm4m4yo0WkveorsoK'
        b'GNN+NVeZK2lYM6gkAs/w3jbWOroa5I40WKyVRov/7nySbbiGLODaAT86Z6Ea+l/IQuweaujW5aDQwnwUn5XBea3dHQRI2hx2EqxNlSt3AIwLGRO3Ks0zMsJIBNhNDvGG'
        b'3W6ykQrpDY1cCC4gngi3fEUj+RK6T5aDZubJORbo6H5IlMEyqgyG0fCJ7pmzFD2u9PHLCf/DqKtISb8gTI7h7OqB3XrkmZI8C9tSbZ8xTN+RouFgBAkBrDHdQXkjWWeU'
        b'0ACFuhVdezK1QtYEh1Xcw0rCCXlg3eaqJmDIPozyGQNbbRn9IRvlQfbxOP+kWmQ1v9bq6No4SzOKPsPuXVtWf3BjvHD9c2n1BEtSmD4dVGp86fuDOsS/tb55tLqBFfOJ'
        b'/h+l0BruhavpJYXWvwGaNrm4P9AjvaA/SFMLWWTtzgpxewYNWifwxJgaMVNTv3hR5UmoiC5WEl2nHl4jegpNZdNL7qcEdXHXtSqziQAUFQeoHR7oirjxygK7Ok7spzgt'
        b'nJod9L8n01YcXZaME9JdxT1dZ9HZsLi/zor1dtbEnklN+qDPtPSFaYlwmPsMVAos5PP+8Ij34jHDb3s9yRtiqvDfaN8dn4yiuXMS58xNL3mGBHCAz2/6wyfBi08RHX0f'
        b'ES7GYXkC8bsFCCWo59AEJ0I4lKXR2GQX95ir60zVRmKQP0s+ANsX/WGZ7MUyzkPqniAnH4RFSa2OLV6wsOyZshHYvuwP+iQv9PGUuVutK4iGK+yUB8W3vt5KtkGBiuQU'
        b'9tY/0/D8tj/QU72gQ0u8u1qeHoRIkf/bH4jp/hysFuassdrkQ4b1NU12EuimLkzLzoc5bnmG9p1lbV/1B3yWf9d2AbVYq/1hqmP1RXMzn43yf9cf6DQvaCHIr47XOaw6'
        b'+NcluNWxc58NJjT39/3BnOOFOazX7A3q2LynByiS7h/6AzjPC3CkEMkIKmId2QEiThUhm0ZhaVHhs/XsH/sDmuMFGk55HNWYxc0sz5Sd8C/9Qcnr4gndORfRs0nYDTmP'
        b'TS8o0GfnzyuZu+hp+aY4a/7aH/RCL/SvukP31/4T1JnAI+aZAJ86qhfavaZ4b5nfgXktzM4sIfnbtep5CzK06sKi7Ly0/IKSNK2atEE/d7FGS8N4MgnJ1Ih19lXbnII8'
        b'mEFCdZlpedm5i4Xz4tJ032JJUVp+cVpGSXYBfRYgUPdAo9lOAlrrLUaSrkrI8PEMu8xtf+uvCxd4u3CUD1MXTCWBMI10Mhrt0IvPAvVP/UFd7IU6ufvACRZdgjqtawta'
        b'dn5mAQzBnPx5hNMTUnqmufnn/jBZ6sVkYAmV9oIZCUPIE9qxPoOOCnPlm/5AGbp4vJh9he5pFACZutxCvrbIs7Tz6/6AV/gzvS5mRyK81cSX1YtQ8YSZ0HWRBSJAez6N'
        b'hYuha4Y0yKp+KDkXdr2SdRD4k7bA0UCel9HYORl500CPx+VwDOhkWR/0H08vEqKgiUfLq+MIKleXb613lSxBo7D9mjRzBTl0y+dMfRIka4GtlqFLrV1Jn7stHgWTT7SJ'
        b'VZoknhVIsHNj6AeWSFTm6iHdDU6fd/oeKeJd41lxxbpEANnbMJH1Cquka+Gqh3nrDZHpcxdkjDhGNhVZ6+1kyNpuddciHbT/n6StUuKk6DUGTiE6MAzkA2RiNAhxC/SG'
        b'jPBg3+2O9EFGSLvr7QXq+vJgIxPskD5C8iymOoOhsRs2vTgZ6HP5mtG9rV9R5wddcXKrujmynvNSThfRWDz04g7x92PJRTdWgCi56Qd63XLRhSUTPFhS6sCSEv8VzS3i'
        b'Vvo5r+Si70pK/VCqbl6qYF8nlVz0bim6nFuCY0nl77yyjWFF8rGNI2exrNiJT5WTzfYzOPyQeIbIApdCIg0OT37G3BgBfeXM+DdzbvT1X/60OTuUQQqJQuYkzjO8GW8e'
        b'HrwGHVkZUq/U5OBt8fm5CSRYnXxHIK5Ghq7gPXhrr5kYyY99FeO7qMVzGxn6ZUIJL/V+mVAmnsvpVwqF8wA+gFfAswoXV8UKXyQsCxSycZQF0TS3HMnKAVeD6ROhfBic'
        b'K/kBfDg8EcJHUFUo0h3RjeJzzWCoS30QlfryARLeTnixgUZyGFiyPm3gqkkeAgnvFdJSaha4A72fCIbTWitvtJBPxI3q7tokEA2+Syl2T6BHIksXcD2VKDx1dGdwZN13'
        b'ncQbUSV+s25oL3Cefdu7LYLtR/pt9voMe4X2TN+FE6Xt9P7guTzwnkWdn9FfjVv6rNE76CRWwhMR4s37biNfm7XN7Ktqwi9afWROX4PRO6vvL0wDGtQF1V/WUgbV7gO1'
        b'u1wVoVKW/n8jV3c8uY2ibO2+N8AbcpPPdMVS2cMdAFqM9qdxXysk9olwTuOm6Dk5k66Q2GY4ZMLaGZTlxwNIOCDb9dG8xzpf3beW5Aio6Eq7ML4bpuP9H+etJmE3vLCr'
        b'gGaD8Wy8o4ICNKPDjDhBhY/JzyJnz5EDDTghIwRSrb4eLG7PdoJgHxD00T4itiRGnt8l8dlEoBAjs8l2ll5kNO1meKdvKgoSqagr1KdrTLtR0Hh48bDPmA7qDVjvepk3'
        b'QjOSzheBlzczc5gWVoxiluT30IK9L5GtDoSPPq8kezyIWvMS10BivKsFicvZ4knvNgvnZF64WUd3igyFw3GJGHEtBwCrdb3h77A6jBZgTmRhyj4LTgjPt9bWz9Kwbond'
        b'WduryiSjbx17Ut/Qp/I1qu7qUldsDiWaLnrp0iyoojGHFUfBNs+rbfST8CQVHlojETsdZLJc+NigQkKiUkjUiZN8PHQgejgm2F8+z0ObiIjG1/FWbQLLzMEXA3IXohs9'
        b'5HS0+N++nfWT0zC69FdyWFYmIUEnJOSEfFeQDyJSmHxBkFcRqcsPOKwqI18OloFEDucjQArL6P5aBcl+5Qp3DaoK4CP5KLguNwXQTFfC14YD+Bhyzg/iB9PQlAB+CC0P'
        b'peUgKA+j5eG0HAzlEbSspmUllEfS8ihaDoHyaFoeQ8sqKI+l5XG0HCpgVCXhx/OxgEuYKaCKMYW1MNvZsjC4Fw7Ya/g4uDMAWsLy8bwWzsPpuY5PgPMIfpqY24vkFOn6'
        b'AqMK2hlGWxrhinRFuaJdA10xVVE0l1ZgWeTugN3RfHI7y6cSKNAbEppRi+QXiyJfK+Qnw73pFM4Ufiq9Hs2nUHk5w60kJOgJlnCzhW62QCNzc/PS3Vz2XDc3txj+l7i5'
        b'jCy3JH1evlsyR693S+alF7ol2cVwllUEh4ysTLckvwDOCnPhkaICOBTPJTfK9LaVlCPNyy7UqNxc+jw3N0dv0xPmxmVD3VlFbi43283lF7i5wlw3VwT/i+faCugDGWXw'
        b'QCkgk+036z350mlMhPhdAiFdl9SbLV3ab7Z0prcPQTNMb9m9pflOsrCGtuMb+DCZAQ68tSABt+fRHKUtxV3JSWli0IRsul8xV5udNz8LJkYO2exJvl88C28IRTfwMbTd'
        b'XL/lBGcnKfw+H9rxRflvyn/ykzc/jQ2PNWYZLVWWCq1x6Ws//s6NHRNo+v+aQfLffv91jYRuAM1Bp9D6YHRWm+XUxS0eJaSvxvck6OLQFUJGiC2D0H3cVoBbc/ToeB7M'
        b'SgU6xK1agi7TbZXoCtoXI36bGR2xeT7PTD7NPAnd82xefPJiNefh0d7Nk8LvVBLHuDrSl6L8P3cs61ost8kIc+r1o67AregT47yPeSFfI4yKdIV3U6Tw+67f9wB6xaBS'
        b'4TPOBKT/5zEVlISCxG+KC/NOyOzT9XlMxZZAIKtAICuFl6wCKVkp1gb2RVaCIOlOVkPzneTrHZOnLNKTJISJQsZbnS6B5LilCWLJMOPtL5YWNqKNWeiMhMHb64PxDhV6'
        b'mWanRXdlQ+mr6BK+Sl8HcivQLRA3bufgdrCgOvQLY/HWhQogWym8gS4Hh1jQXbpzfOJi8oFApvBXmnJLW4ODocnk8c6J4+3itnF0H21i8MUX8Sn6vDVZwYQxTL3VWJ5b'
        b'rH6OoWlq0FF8HD/0zRPTtY8cn8dXS4T88IuLA5qQC90VMi/ealLos/P0WtyuYZkyfCc4n8On8SnU4lSTKk8unRCfRVLt4l0pSUloY3lZqZ4ZhW5K0EO0G58Q4F5AO9Pi'
        b'8/Hp0WQXcnteqc+e9dgEXSzekhhH8vlaNQp8vXEk/dxg8OxIPW7Lzk2UM8n4uHwgp1o8nFIlTV+DN6LbaF086XSdnDGi03J0j5uMOpOdJL8FzP3Tz9Gb/pBKAzyw5sfS'
        b'T+UVxuZTjNCmLAkzHG0KQbeb44TP2Zx+scS+El+TMiw6gA8uZ3CHaQbNnQygH+LOrs9E6hfWx+Ij8GhJLAxim1abVyok8Bc26nvIhWXwSYkSd0iHOunX5c6XoKN68TN3'
        b'uDUXWhExb2SkBB9B+4PpBwrWLMLH4vM9HabzfgugpKvH5hMQHGrlGHQTPcIt6FjwpAJ83zkAXi8btxrvmm/FRMdYzeQZJtDEPug2voUOgw5wtXElvoG2NuJrDjkTMiS4'
        b'iEMH5BWUyFFLMD5khxsLyCcIYnN0MPTAGCmwItJhpWiPiJScQbvwnSBmxQSaQhlvtyfH4/YR+CL94GBbIu4ojo3VxQG2+WKnCBSG1qGzgQx+ONQ5kvDJ5LxgfAvfsOPb'
        b'Dai90aZswLdAhUkZjTZL0MbpeL+Aehv0QAtuI99F0SVAv8qYcLQHd0ZL0KVUtJdS/dGJ5FuXzKJxc8q1w1baGEpJ6LIZX7I3zMYtMpLZiEGtzUXmnPQjrH0FMKt7K66U'
        b'FumLWmaHHRkeozj2zZsDv/2UGf6dCP7UC9c//5GidDn7q+XXJpT95P0GadVXL83IVJVnzCp9f8ZnTcf+13w8mt16862X09UXPg5WxCWNOhYVbio+/83RDd89Z9kwp3P2'
        b'F/Ne52pHT2mdUbRi9p6yryVnf2D8MOLvQ4sqf7jqHw/GbFoZd31DylJH5e//H3vvARfVlb4B33tnGAaGJmJvY2fo2FGxIQoMRSmiRgWkKEpRhiKoERRFqkhRQUUFVFAU'
        b'FQE78X3T12TTNpuYmL5pmzXFbDYxxe+cc2eGAQY12d3/9/2+34YIA/fec08/b32eb/PPVDacfn2+87RX3z/ys2zJ0ZEP/jZpzy8rq3e9uGCEZHR4GZyKfXpc/SLJrvM+'
        b'd77a05po/sK2fXl3K/OGSd7e9/OPP+376a77yeeGOSVWlt457B91PGnrs7dn/TQwLKfNYqjtxqOxX7rNXhO0dN6sNXe+cRvx9i2nF1xuBzxbdrnP25s/2/T1LyfS/+I+'
        b'6os374Wc+/y6x1szJ7v98NOU8ktnR9/wPXfr7kCb5Bj3BLs62XMzZncEbAovj365Yt02f6uPB/k+qzk0YVXpS5teiFhz8mrWmW/vH392yIXnA5LUPw3/y4wPEp/Z9YCP'
        b'i7MfvrP9F1PV4ZIZmKAaLeLxtDv46U5F3ZnoBxfJsTgZ9okHXxMeopO9kztxOx5QQLOAx/G4O7tFQiZMgyEKNJke9VpUgg3rGXzDRrJwz0NhhpWleQq2asjEP2eVainj'
        b'7DZKQvAqeRWD/tkxCbPVQQz4Z4bAz4V6Jwb9MxB2QasBXVRWDGV+KJ/NDvYheMCa8X4WqXA3rV61RAFnBayD02oRI7oZapyg0DpVmo5tG7A1jbxWMUBYi7vhsgi2sC9z'
        b'rhbYAg4uEVkrrkxmz05YjVcM6Txxp5nIKoGlG1mVTci0V1PiCCETqwfyM6EsgFXZFneHknVXQHqO1Fnq4ZDOw3kscmEwFZhtu5QRXHHCqtGQzbtiJeamUrXHzLEf2egK'
        b'PS02pmG7NRRAkbXc0hzPWaeTtYhtGRtJ3QOkMriM+6CRvWgWNEOxozMW+7vz3AZoli3jsYmHw+xFUyZgIxb6wBkid2yF6q38grl4kAFX9INSZ0qHUQhNPgFATjsX0qMX'
        b'KGz6YGiVZuCVQSJsRpFHH8aaQSmQCv2JwAMHFXME8vbaxeLsOIiVo3UMomwngFNwyYTr7y+1TBPxv/EwJ1COUDLJTLjVcEEWKYwa4cawLAK2wQVySbuxmpCBvqIIErAS'
        b'Li5OpRIMbJ8C9VrCsSB6JpNXkJNSxo0gk2/3fCm2QDVWiRU5AyVzGU7VUTrcBvxk8zFvBesNyZIABtpV7E/OzqkyX2EAbjcREUqaoI4IeIXsBYH+QVCMdeRrD7lxMB6S'
        b'biRr4CTrjxXkZC6jHKajO48SqxBJAO4kPc6Okl0z8BTlEnEmEoWaCB5XZynImYAn4Si2iPgdR7Cc0Y34OfliCVEbp5EFdURYjYXLWJtJM2ugRXcddmvpV33J7HSwXwaH'
        b'TDBnAx4TKa1y4zaRGwOdIN9Vu7ObkK5pd4AyE5Px2MiIW2AHFihZjfToLLZwFo7jBQkZ/UO4O5WqydgIlaR3rEUhXWGtE9MhH/a4drUrO5KDpni0ORyBG2kM3WTKEoX+'
        b'yS7PQSPu9lfJqOxc68+ZwoVJJqkMUQNbBxmw4DIGXDPoMEaCawaFrKmeQ54UJwroHsCOKBnRjyXYQWZurnHZ+z/P6cosCUyGp+kr3WR4T3NeTmlcBSk/kCKfkp/9+YGC'
        b'BQVFYXSvFryNYEOum/ODyd8ETv5ALrFlqYAWgrmEyOGCzCB8lTrnZAa/Mbtyv27yuWhQZhVsNNcmVenim6XU3JZCJ0HKNKoUKqKjUvWhyjJN9NrYxNjuUCumj9EdjfKU'
        b'eF5baAo9t8VC2IsS6K/Mfr6ON+yz9l60jz914YY13rrfw0RmGqFtV6+QrHqjedeX/W5reUrSwyzb9/WeaXtGi6JLyhBrp9QioHRBun/8CF0t/6siQhtRFfEQ0p1f9RVx'
        b'MhaDFa/prNsf5KEV/dS9vZ8qceL7h4ey4CsaevWHmW+1DD+mEdFpqclxcb2+VaJ/K6NaJXc7k9uVND2gMwyM1oSFU//uajAzrvJh4y/TV8CBhUXEx2njIBJp9Anp9dgk'
        b'mt8S84e7wCLCYDX3Wg0zfTVYkBYNyVhD4eH08Yy/9+0sHLboYQNuoX/l+N4xj7u+2OC9bHPVQwJSEho9nLxoSOBozs1WPst8C6c3JPDMkMA9yS/t9EH0KNQY+1zvXLJu'
        b'7M1x/O9gkl2jkn6YxhuBIKT/dWEm6hrqoVFq1ianJcQwUtnYFAZFroxaE0UDRIyWpad38kqIjaKBU8r5LIGGDqwWP5fFHWpRxbUhR/HG8Xe1gOORkaEpabGRkSLlbazS'
        b'YX1yUmpyNKXBdVAmxK9OiSKF09AyHVJvr+yDqT1WOcXW10YciBiFYshapkEk2KOR1yMjF0QlaEgNe6IDsswvrtt/fI/hlgTGF4z8E6+hsuCYsLC/Rz6/Wh73wS0ighX8'
        b'HMO3f/KGimcSk5k3VHYXNs7Cda20kYIFokGO7+46ksatiWXgaPeY72hbt6/hWWO6HDia6IQI1r+dvhBagAE/rege6iSm3UraZCPVOsK7naPZ3HcWBidpGj1LhsE5WTez'
        b'K+517NKufdBCpLr8IKo+QRuWq5n6RaTyKjyH7ZZuI/DSf5jXtlf7sd5hZmg/pua6MCxa1l1cpBaYfH8HPyc4FSpalOgfgvDoEH9GRnUa8hUeyQvj1e7bTDR0V8o/6/n3'
        b'SBfbLyNvrbbv7/BOdJQ/sxh/Ffl5ZFLcV5EFa/yiyGTwl3D7zOV9nt2rkjBJdbSrafc3d5FSsQFqtZIqFIaIkIAVUGjRgyoRLs3VYvVOdWICLdR4JXWbZLIxeFmcY0/i'
        b'mceyKJMpp9FOuf7GptxI6r58jGlHChElSKkB2n/vJIM6nK8t+pm5jczMwb3OzM9tu89MzA7Bi793ajoGkqmJObALzw+xnAk1a1VCGlWBiSJ/AfLEmYtVQ6TWPJwkBVUy'
        b's2wfaA4Tn4TDWC+dyJNSL0rjf+jrJ7DTZeHLs9av8Yn2J/Nh3YcNsWvXrF2TsMYvOjAqMIr/btD6gesGhiz9zM1k4oYTEu7Kl884mkVWDtL5RA2t7r2DFug7nKkNRsep'
        b'v4W5jTSrv/FxEkdGeMh4GBzAO8hAWPc6EPdsDIXtXt73H+RX/x1rnWzOPw/3lmqoQfltp8l/j/zc152s1bVxFnEfEJ3Czkr4gM8kGzTdc9ZMGk4VTj8o76lz9qarXlrZ'
        b'Y9S6hW6w4TG6c9v38IqwGI7OjboXInFa6sheB+NDq4f5XXpGifw74kmvA9HzlJQGhsZXnvmU09A/3203U0dZsENSumyLinfYl9gp8vU4AZkPvfcD0LGHeicGp/R+4NHy'
        b'xvTage9ZPEx1NBJU+u/2YNzjuT3JVH7tRB6vofagl+dqHKM+J5LGiqculh6rcj+QVJ/TYsKN6S+1XlZHDhm2fx0g8/MUFjqZCNTKI53DQyv5S3EqDViAaqi2MWJewWYo'
        b'esh0b5aL9rtiKIXtjmo4DK3UPOss4+R4VYC96dCLFMMiInpfCi49VXQxsLbXMaTlje91DN956Bh2Bu1yPVyQQ3X9HscxFyR1+VswXUHn9Bfy+jDppIvrP88kbxBzTQ7O'
        b'G5I3NG6o3j2peKR7cm334adxMHY9ht8pkDmtFNOmM58Z1GOFq4yjTjMTJ9FppqQj07YlQzEPS1KwFVutqauFeX9soF7AK1CWydxOcB1bFzPvjw8ZvSBo6nQB4aVVBl4g'
        b'vQsId21SQGvYPJWMuVvMxi7XwNVg6sLhsJSDIk+sZcciNME5PI4teCIuTUauHeFgr3yWSKF5EI9gnmIaZmMbddK0cnAMSzWsUVCMO8w1IdieytNzl4Nd/aBedH+2mEOT'
        b'wg4P0I7AZg4OQAlcTKOTyG+gjWbBPIrFiGUcFAzFE8w/RGcr6UGbp+TRCaajHTh2lsNOuCbDFmgejedpQXWUmboEtqfRPh6G1bM1XgM6WxPumkbPg1kqyNZgJebRnurm'
        b'I8NzqSl4McTHkdriRS9ZKRww27pkFPNdTsE6yJ8I58golU50k3I86QnMdoezzIdGGn4YjnTx0epAYxZDNRYtCsfKiX4hppQRQoatWdDA3H1eIU9OxDNAkYfcOXeyLFk3'
        b'hMLxKVg+DEvIdHblXENgV8KPDx48kJowN5nSZu16/0a3KI7Rj0OTVYrae5P+ZbjbhxGQF7v6hdljPqlFiL0K94T7+FJJqSiAiUjBtHWyJMuVcUnMORozCxpoeIXhXXQi'
        b'UanKNUjbP4bg5bRzDjviabhqgRdUpNOjaFXKoDzGkjyz1xKy3eQmmB2GNTIsCbWEq9iwwHawfGYwXCUztQabvddsMosbsNEcr8ky5FBgFmRBZtkOrHfD65tVI3D3DBes'
        b'lsF+LxW0zJqEVQPJJCnzT6MmBlslXjDBHMyx5NzlEjgXBheWY6WM7HN5UOkAuXgd90BJ6JD4J0mbsofA9XWjhkA72QJ3QlvcZsyV4JXN7vakDsUj8Pz8vgF4w5ptG2ym'
        b'RYQO4ScJnDw7cdPK98N4jq0t3D6MslD04LY1cJIakNueXQo12K6IJrU4w8oMCPRhfLnZ6cnmRYPGcmnBtK9K8SRepO2oMuOUFuTDklXrSQc24RU8xruT9x2fMZGiDEWS'
        b'7bgJq8PG43ky8+qWk4pn9wuF7bGwew0exUuma+GaTSZ1VtEt1TKJTG5a05VPdqurj7OfiW0/GiUDjSryP1leeNoM2/FKcqiKF+ljCoMssTBhDBaS4wJLfJ3IbkEGeoBc'
        b'6gbNUMY0rPWBUKt+GFvvGijtRthboLKIxwvQljaRvqODCNcNjtTlPm/MYzibl8NRUju62SzAfaLcz3MCmWPtUMJ74S6BIe5jmxcecPQhvVckRgztdvXzdQ5m0R1h3QMW'
        b'FvsQTXAD3QAW+dsEOy8RuMxQ60yog1NpoXRkjqjwuLrPOOZM8V2sjfTQ6pI+/kGsxS6L5enYttjHLyDQyTmQhZLQNacPLWA7NBYF94HjuBdPsXng4CQwpfiVwHj/c4uS'
        b'OW271LO3qHU+IPlSbMZzAuz2XCHOkiNEtz4dEqQKILs+HKNQ9mHhPQNYwjgy+09BNhndMixaoSQ67SWo9xkJHT4jJ0KzlMMLmGMLVRbQyk6UWZAD+8mO3mJtJscL1uRT'
        b'9YrUjWlEdtZIgpzhBtumXTkyMphtQvctCdntmjhsmpuZRt04RK86OUutcmaadSCpkz0TLrLgtEFKwUqlHLarvdlenYxleCkEikOxmLISmazq58BDdXyseMA0Zg1WpFvx'
        b'NBwmFfdxZFc5iJXsObe5rmSH37GYBhm0mJJxP8M7k5dfUfURoz2a8Fo4Fo4mtSBPT+OwJBMq2GYN1/hRYshPHN5gvjfFcgHPRk0QOYx2+ZG1FQNH9X5iHg7OcWc78qgx'
        b'cq3DNW3gKt41eC6rSDocCSCrMRcuq0X2m+GUc6cimMXajNwUqg0JccCzKjgl5SxsJP3IiXCFJV6sJBJbPZ3xrZirYpo+BfcX/aAm3DjINonj4ZgYH9PQ11ytBxvj5HEq'
        b'PCBApXUWq7ZNCLY4sqWCHVbUgWexRmI9MZZ1hTMZ0F1q3O+g5e3h4cjUePbUGNyzEAudA3HPdNxP+km2UugHBWrW9XIspRv/UEcX6s+VTuHJ7tAsRtLAZXu1Gi+lM4Js'
        b'2tw6b7wuhha1k0VcTTaJQqwQrzLq7HNwnk2ukAQ45ahd0FAcRFe0CTcSS8n5WG5i5uUuMm+1ziObV6Gos0M+aa5hz9iEin0TCDmmWCqHDvHAz8ZysuW4+DqpyK5khnkr'
        b'PAQ4LrOJ7zPxnKChkMp9Fr/gHXI56Z05NndW1tTOf/tN7xcXOo3w2Hu7crbSu0DpO6h+cIOSv3k01IUfOX/7Yo53CLmk3KZMmzV6w97pEaXWGyrbHT1U9Ycz77138M7b'
        b'Y09WNYz1DS52MLlaVe36wquj/lU4QJG3InBixhiHn3zLwv1iVn1arnzQMrgwOOfBbM3F1wLv2qnT/360j0n8QvWPbXecWmuV4c/Mm2H36Td5yeoZT4T/sHRR6Asr7N7P'
        b'bn/7nQ+jf7hwriytcHqx08qCVkXz5n+82eeZ4nqX6Vnvvr5q7At/vvPRgDc239664aUPKtKa4HT0x4vf3XE+2WHGy/z4Lc//2njqjQX9//rux09neTw/7oPhS5d8N7fy'
        b'N4cP5/xc+e7zP20OzToxQf32VPNz728Ivv9GxNiJ++8fb/51etL8O4nzzXblH0se4vJm4v65d+f9y2SV1zvH17wbH/PqE0fzvWc8f/fo57+c/nWO8503P3jrmPuws5V3'
        b'vh3msLDNdvTP+O1qV2t/6S8HPr5T9XrCtrqC0/+wTKzzj9r6wua3c/Jvfv7qC4Pf+sX8xYWyd9at6WP95azDU4LNS45m7jRbcC1i0K8L7w7+6lPngA/cjra0LvduyYkt'
        b'cq77oM/HNeF7n1neP7rky5En7j1lYTm9Y2XR5+/e/UG+Kj8z+kDulZ8CB6TGv2c6/sC+CNn0OZ4vbZ3269OrRnwdOG3Bb+80xU6b8V5m0bfblvoOr/24j2d8zN/2HfP8'
        b'++srEg+tnl+bcH7hnZylmS02nnta+irLhqVu/MfwW6nv3vL/xK7DbPPtvO9anx0W9OHGHeFuldO8qw9/UTrjyjPnf1017vuimubNxxsP/TU4b9OfE++8N+1ec9NTRZuW'
        b'esgaXSd9tMD32Du7TuP6qMClEV8+5b9y4dfz198fcH6/yc+RY1RjRaf+vsnD9FEQu+gpRyMhaBhECHSkUtkOS4bhBTFyZY51Oj9XNZlRbrmQuX1Ku/EsjCAbDx7JYnqZ'
        b'd3/sUGwd2IU4nYXLQI0Vi0btR3b7c476wAi5gNnQKqRDgyVj+hpGZFRt8OON4Z07oakZuwpnx5GtmazDAYZbIdYnsKLxwqhAbThPWCINkhCDeaBgBSNh2Uak/92MekSK'
        b'1xn7iDB8Kx5jERTKwWGODi4qLCDnhdmqmcvISrX3YTpstJenI6W2yycrvdKJ7EdQIjgPgoss5GEZVkGjGo97unRjiKmdnEojU0ctwcs0+IKKKEGdsqqMG0HO72tqKdbA'
        b'js0iSVo5KWqvI61CRAKphAyahInx6ezaCiIkddA4nphJIkWN4Ax78XIqE+RP4nnM08B1OAjF8o2WeEFDI+6MBNdgqwxuuML1VCY7kaNBrrdKQrETM9Nytr4SOApFvsyQ'
        b'60oEuA61zjashBtBbLz7YJ4EiiR4kM0gG9L9p6EQduJ+VzLYzoyY0JSzDpKsTV4vzrFSuAwVjkFORE8phMbV7LoCbwjYPm6BGKDcsgryO4UKcycmU5CvKrFrzrnBJTUp'
        b'prbzsMAdg0ROmHoiRO3TxnnhiXUOBuHPKznx8RMei8TomHWwmx4ovsIAOJiR6iYqi6fIic2MEFAPzb3FebAYDym2aalxYmhIjUGI0aQFLvoAI6iCSjb2ZED2kEIKk4YZ'
        b'DXihsvTVMDaL8Jqpt2MynnZR+TnqGe6yJclyOCHO6+NQR9dmACWWm+pBO0GRJOBBqyjWQDxvDrVYaBfZebpBK5mgrPFlnkSkK/R1MJADsH6M2O17cZ9OEsBriXpJYMBq'
        b'Vn+8BnvhMhEEIuF0L3JAfzFUSrLQhvTFfuiMMaLxRf1xl9TWFo8yw+awJBejkTS+WNqbpScc61gg2hInzFX7+1Ixesf8YN4Brsew6q+Cswo9bZ4cj0IFI85rxdMqi38n'
        b'JEY19L+IFvv7v3Xa2627QWMyWxbFKephy5pADbByxhBjw7iJZA8E+k+Q/cb+SSwEms9DMeVEJLj+5F56p8ALD6QSijRHcculvIxyzDAgYivxHymXfrIln2hojy2j87Oh'
        b'IT6kDAstjR/5Sa7QPClSmmChDR2yYmFBUgkNGjIX5AJFvKVfnQi5AilLYD/FLxkv3JX1p1w3FtpyxVxAvR2tW4eIdj8xVkiM42G5XU70mxsLE4rd1BlY0Jkq1el/6Pd/'
        b'Nq4quUENZ+lqmJKnr5STPtyIGRt3kV8dejU2vjWvC1nhwzpJxbNMscBHOD+p+5NnEMCP5/zUMRW+LRgJE5gbl0oJCaMSEhjIqQHVL6lcPK1VVEIX7FMRHysmRgQAjFIm'
        b'xWb0KFQMOrGPjFyUmOqbFBcZqVydkBy9XuWixanVBR6kaWLj0hKo9z8zOU2ZESWyJMbEU2LDnjTEhpWIT2I3xrG0fW2KZqxGzNsUQQmVFF5JGR+jeXwOQoo2MF3pywIA'
        b'yDzUxFMsWPIeGgwQpYxO06QmJ4rF6pvmGxMZqaLoNL3GTJD+0fUH/RifpEyf6kJZrueRbsygnZm6NipVX9vOsAyjJWrbxgBqWVyRGPxACqBwtV26SJcBuyYlOW0DQ60z'
        b'WiJpemp8dFpCVIoY3qElphdBFDRKe5qH7kS6gLyWYZxkbiC/xqZGu6jYIPQS3kE7NDVWNy7acWdhX0ndySa1ox+TzPJvN1BoY2NldhmAR5A18pwxskbzQKbFWuEBbNZl'
        b'lsgGLHUXrPASnBSt5GPo6XqZHJPbFdg22apnSoIEcrEC89ICyI1roRIqtQZEpVxCjZRXNtotcsOKwcN9+o7duBWbg2EnnPGCiifm+aYSzfYYnJN7BjoNw0N4DA/Nh6sj'
        b'suCUjRtR8DuYYWem0pfzCR/Pc5GR6950X86lUZpbl37QgoVEjAmhJLt7aDILzRQy5Uatk8L2bXh6zmj28PtTTbinJ5Amzon0j1k9l4sXcgsFDU3nW/Dh/rEvXrfc4Wbn'
        b'/eHPNcU/DVJ6xeRMSuD7Wb7Ub6eqX3ypV9WkY5kJUcmDx1ypC3pu0ijFzuXfK65Yv1ma9XrDF5dn3D/9iyTvl6e/ufvS304pd60YcMit/lWX2bl/+fL1S1Mt/nU5IPeL'
        b'd6uzni75p6Lg8mjZxT+N2DVzyOGwb1QKJgyk+6Z3jeZWu7Fg7sIlTIaw9ycCZlAKtOiod086pFL7o8XcycYDfJlMstbciP/pXBYToNeF4CENNaM6J2Cpvc6I1AdLJUQ2'
        b'bB3JhC/3cDjsGBifqNd1qKLjkcjUCiIm7p6ri26XLQvDFh6boEykbMT8xUSsLfQZDmfFCHd+AbaZiy61fLwKrZ1slVlQJjjj3mhRqm/Aq7MV6pV4w4j6hU2MzxhP2hFR'
        b'jUmvV/z0MfKd8fF1UCJGqB+gVtKu0doS7OgivxZ5aL1sjwznMKPZdmyhMqnFwZjUso2bxmQVipr/gHyXUJmEyiLd/Pn6oroyK7p2Pcp70EEK4h2dR2o++bWOHqlKY0dq'
        b'Nve+be8xBfo60JBNcsJEkCOmCxSBLh21t2A/yW7JQ5NRJcwtJ/3wR6mR8zQkNkkLUdoVFz1NI56vsWyHI9ux9zxfrxADrPPeDqXY1fHRmojohHhSikiOqwN1iqMgjdFr'
        b'XdgdLt70uxe7rTcIdYNStf0ynYUIOuljBCmkryaWVTM5JYb+gWz3RrdjLSR8r3VwWRDmH8lg3dI2JCRHxehar+sQo4VS3FA9TBs9KbRRs5q0+FQRmF1fKeOHxCNr5eUV'
        b'Gun0Rx8N+8OP+i76o4/OXbr8D791/vw//ui8P/roUu8Jf/zRiZHKXkSpx3h4Ui9Rmr5xIlOMKNjExjgpHbTT36FLqGfXWFQWp2ZcEuktwnRBShRDx+6cw78nmDScyq7i'
        b'rpA+0cWty2phQbAiJq24nMgL0+Oj/lhPzQsNM1KFTvJsuseI9RCXW3zMI8QtKWfA+6oXt/qK3NhTFpkyj3vk2mSnjy2cOOZUx+tYKdcoNi+i/vmj5MRdlCi6CnYnQDO2'
        b'uC3l3dxMOMGXw5ptASyoYBGeyHAMdOHneXMC7OPVUIjnmOMhFWvwkmOgn0CO7WxybTs/DaueZG+ZZw87HAN9eY9+5O+7+Zl4bYBKKkbvXYK6LdRthWdxuzVeMOEkg3nP'
        b'4CzR41MNx0eSS+cm4L5UbCeHPFbyI53wEKtIFhzCMs2EFAHrzTg+mYN2ZTiru9pxlAbbAuGqNTnDBDzBO0RhFbtiBwehActhH+wT3fDYChXsSrgH1JKHhgBl1GHRBTMx'
        b'VyWI1diDl9JZHRtgt76OmD2RSbHuGz1pFbFhUmcV4cpk8clLcBVLSLkRUKWvDJFa9ojZsNuhcCFtwGbyQtYATZRKIjqNSklnHmDvrMbr+ncuGcK8NcFxUETfCafgrMFL'
        b'z2IN6223cDyvSB83xoxMAYkZ75oMR1gbJ+Nlb4UlXMFiCtYiceJnQ+lGMXyj1ou8sQUvOvorrHhOYsHPtoQbaeHkUsS2dDXmp1KpMYSF2VL/LpF8yTNQtoUI1UWYC9eg'
        b'Ag6Fkl8q8BrWYxmRqivgmq0JVq42sSTfAijgyUxlXyIf2lqTEbg0Px7+/IKJhoK9rj/zj7BXPAOfdrMx+aBq45SDXyVzZvklBSEbCicNjawYteryOXv7oeY2ZV/Y26sO'
        b'lXgpHdats3pK1bDJt+2tyoPfTv1z9Nt7n1i3zPcnX5eGOnu/tm/254Q2zVTbfT2qtfbZwV9Pwur4s/fanaqeT3xT81zOr4GFk3CW9bty/1EnM4MO51cUKG++lPV9cPnP'
        b'NSfuz/jXzlPz/+lx65WdL/3qWBb7Sc36wYn5d2ckbIx0fMs0waPq6oi04tc7Gpb8Znr9n7OC4luC7hQ1FlcO+G7bN/+4+bRzxVaTMyVf71o1N6gkOW+VV9D4656vr9t0'
        b'7xXLNw5osj4x/SU2IPae9a7ilddfO6OyE8OzGonucQlKw9Wd6YTMkL8C9jNL/lA8MpVI6nARKwws+VC6TLR4HsYi08nUSd+ZNmfhJDEdO1BkQ29aBPupU2IS7BDl+WtY'
        b'w0Ruf9xHniJvL3ajSZlSyOVxR9+BTHQejwUKmrnqL+hyV2nmau468Y1HHaYYeCWgVY0lQjrsxXLR8XBkEtxwpCZ+Kv3KsbDPZAFysGAtk9eHYQeUaBTYyi/cyPFYSAXx'
        b'Rgmr0Ewii9dC4YbJgivWkWt5dP4fUTInytY1SnpFtnYOuUBm3V6aHcqUA9LgpfQSD9V4nlzM57AsGa+zrvWZh9e1maM0FXTJE7pk0D1Ecqe940h2gVpNuhU/K4Xj4QSH'
        b'B2G7Havn+nUeGiiC3UIEjQcq5fAitEArq+dWbB9HnjHB7XiYPHWSI/O8QFvg6JFk+WKbBbfal1w6S0dnj5LpVfMd4bgmfSO/vB+5cIDDoswkcYB2wmkvckHA8wHkyj4O'
        b'Cwb2ZSoKZK/0EfUmojRFw2FDvQkPBfSS7fiQKGSphgjDTKlYbVypiKRKBDU/0rxE4YGMKBdSZhgVjZoCUzF0XxYsG9Fc0Bkc9f/IE+TeB8KDrD5dg4vJ2wN1OCYsSdHC'
        b'UJhOKeiilbAQQtKaYr0mUqDPJSwin24+RB252SXEuWctiCpGFRCWQxWoGtANKOq2NCLIN/C2IsIrLDjYO9DL1ztERNnUA0jdVmyIik/SJRnSbMfb5gZZeMxaqc+4NEiO'
        b'3NEVaIrhTlFrJdOvWKvE7hn8/yVjeooPVf4kWpxIuamNROC0X3yPT7/KZFYmA+dQE7pU+IMQmFIbGwvBihK1SbkHUzLlvN0wOZ9G3UlYTBZafreUAR4aYA83eKE0Hi5O'
        b'6xGZa6H9qXHguzK3UeAsETTrkFQLmyV+puBZZuSLfqYgWhRCS/x752cbCmIZ05d9tovpp//cP2YA+TyQfR4UMzhmSMzQQwrKCZcni+NjhsUMz5VTEM0K0wo+RlFhUSGv'
        b'sKVfMSOKTWPc8ygol4yovWNixjKQKVPGpTY+l4uxj1FRrjj6XIWiQogTyFN9yT+bCtt48TdbUppthVmFeZw0xiHGkZQ3gQJ+0RLzzPIs82zz7OLkDCaLlmzGYmJlLEa2'
        b'T5wsxjXGLVdOQTul3HIFC3KeeNuWLhsvxh/BENbiYlPuT+giePa8QUuFZnjTfRcixU6P1yRP16TGsJ8T3NwmTJhOheHpmzQx0+lScnFzcyf/iJg9USW5LQ0MCg64LfXx'
        b'XehzWxoWvHBRI39bmO9NvpvRV0YEBfova5SmUJvBbROmfN42E4F248lHkziiQmt+z2vd6WulKZV0/e2j3/bTFS31DQwRoRd/Z1keZHvrWlbKMVZgyPwlc+/PW5uaumG6'
        b'q2tGRoaLJn6TM1ULUmgCqnO0NpHPJTo50TUm1rVbDV2I8uA2wYW8TyV0lt8oMKyvlEiKZkg6yD/Ia65/BNEW7o+jlfaa58tqSH4uisqkG2AwtRxrUkmhLm6TyHeyF9LC'
        b'GvmUQBEQ8SCtq0WIb+BCf++IeXNDvXwesyh3sltXdmny/andHvRKSdZo5jE1pmsZ/slrAjRrWEnutCShsyRSwUZalnW3/rg/uPdG3e9ntPNUii6l0OmW0mSkbI+Us/Sv'
        b'3QrxYIVMTDlDr/X+cvf7jr+jpbdNY2LjotISUln3s7H8fyfhQwzYuw57pmPNfG3QHovY27EwXrjmLLBUkE+jclgqSMLaZJ6TevMLcuQPSQW5LacsrKlkSvee9US/Fooo'
        b'qV23Ehfds71nFbSSdniST5pRxsWAbO6ZLpkFD3tLo6l4bK8zcnYn6A9wOim/oLUIDeyRi2Cu61QqJrBcBE7HDioCocWZ6/MMzB+aZ6BzEG43NWLQ9BXzeeOzYg3MmiLN'
        b'j+hvotvwQ8yYITqCXuUGRrrAZBjN9J43Oiu7LRWl/Xxv1cNvo0vtkXd4KO0dNPHUeZU+1WWKw2MUKa5epb2Xz6Nv1q5SerOT8lHv6X0HUdr7hv6uJ9wf8sTjbga0iO6V'
        b'7s1irLV6ieYhMdVaS/CkIw/o7Ul6YoqPdZ82G1Lik1PiUzNFiF57B3oOU+osehI7GDciOtDzmd5DT0sHajF2oMecg8ql0786xWWCi9t07S3Gi+l0xbqxW7Wldv55Cvuz'
        b'WHRvDRPhILRNMwL2IPbPeA3De+i1e5ivYnrXXH22yIxDN2hz7XutUyc+w3Q9eWxPCAYKh6D3xhtxttP/yDXG80eN+Mx4yiIBYqNS6YTS6FjQDBAtqC+6l4R/aoAl5WRE'
        b'pWgDBwzIJ1jvKENiY2lb0xIMiNWMFuU1N9R7YVDwsgjK8hMU4h1BCV5CWC31TnuR7q3XThI3IbF/GCGTFiBFN2463U1rOjbu4+40JzMXhVhCp7XXodue4tBrlAAboQ3i'
        b'OtWIZHHdthgHsXW6W+KTjKMRiFgXRCbVceGujUpSeocF92IWT1KGZMSnZhGFkg1c6kMqL26IvawlsmB8U6MSMtmDve9wDr3PWS1IhzggndgddOZrh0SP4yF6qHppUaoY'
        b'9GCA4d3l2S4YLL3uWqykHi4D0j1awUmjm77dyjU+Jlr+xM73Mt7K1bEJyUlraEmPMK1TWcSsh/RkHcis2Aun4+Gp67BcjSVYKuEErOPt8TAcFWPcd2GdDQ1zkMBxf20u'
        b'IOZBvhjnQMtLGrZZg+dGaOFDOTwTEM6SdwZirhnVeaEI28lXC+RLlXCSs8RcAQuXLkujLJ1mWIbb1QZpXHjQSYdlapAf0xVkM8DET+Amww4rzA2Dcp2ZewfkQKMKqWn5'
        b'os4MDI1Qw4zVWAu7BqQMU1jqbMdjsThtMb1wmjxW1InFapBSRrNaYMdQltiywdIymCKq2jsHhtnbYwEWuWKBE8XQFMFBnWWk7fv78jMsFoh5iC3pCg004Bkd8ieHeybA'
        b'DebJWDDZlLOIaZBwykinK9YzOBHW9SBexiOGYKA+Ln4BmE+a7RqMu/0X+0iCIR/zHUdhPl6G45ljOeiQKvDAaFX8vPtbpZojpJCZsGpssdoc5tjMP7m57KcxyxRJ18ue'
        b'uBkwuiz7+TF/kt9UVszYU7pi5PiLC6daft0vzHPgwNyqAcJouFmbvfByVvD7372juJlxd+8LLjvPvVU5oj7U79W3J/l6BH/2WvyGjy7s7Pjm5Vvfj5n/atyV9bY2D5Im'
        b'/Tqmz4dfbZtqn/yNumLd8e8vD3sqceyCLwd8fe+55T8fvHIi1vn91OMvKFaXjFvVoUpw/efKn1WWzES5Gmtxv6OLM150FSMc6gW3pExmOpwCpzaJOMVYBNUmNNI7n0IV'
        b'WwVL3FfiVWY5nUPzgrvYcSMThXTfeWKw8EHI12jDRLB9tboz2h3O4An2ejgDjXhNTV7SGKSNFUmB7cwEbOWDNXQypg80jPSGxoEsynkpHsdrCrUfXO8RejGgD7PbxuEZ'
        b'iqDBDLdqPGQA42fjzrD68CQUenTDBFzpoEMFlGJLINSI7SjZDEWOLpPwRCd+owjeCIewVDRn10EN7syaboAtSc3rHdqQamEj1kBdBnkZXXwXyfUAfkF6ELNKw+EJmK+G'
        b'stVY4k96YDXv3m98F0gI83/L8KaHmZvfm+a0xVY0vD2QSsQoVor1IeXlD2QC/SnQ2BDGaWwlCPzgXjQgLcCaFnNmLW/MiJzYBcct4KFKV+vwRypdv5cCpZG/bRLBgOx6'
        b'A5wqNuG0iG7GXqhnT3Z5DLG3OxobtUiF+MwNvi2l3Ki3pZQmVWVqLGpWjEmlIaq3TbXs2inXeCN569a6I8Sf0+eti9qihVZftBShs/Os46wfMztdpzU2GNMa58bEaLpy'
        b'QetOTSNGPL281VP5jFNOp9Lg9Eg9UkikEZ+9k1Z60QNZ0YjIngGk3XkNRVpfqpB3yqSptBdTtRL7Y+lCWilWz3z7KHVIJL4SnzVCTxulUcYlJEdRG4GS8bBqiSZ7C5iJ'
        b'SupC6tad1ba3WnTREYyRzqbGbhIF4FQ9T2uiGM3ZS3gmuSc+hkpvnV3RSY0ntkFpz/jbadOYdDYqeIGLi8soVS9ypRj2wEKNo+hsMmBr1pcs0lGK8m7ndaPl6Z/pZJfU'
        b'TgFtSFZXrkmjZdgHey/wpk4a74jAsIB53sFOSp0aIhJy9hrGxWKLeydmTd4gxlo/pIRNxjS7XhhQH1Ic/U+v+NEefphepgdX085qo6Xp6LaNqXBK0ivewYFz/Xuqa8bD'
        b'kR9ThdNRZIldoScqphNWO2/ouiBabyzjoo6MDExOojvFQ+K0N6V2vp3R2NI+ikqgsdF0g9BP3biU5ETSVTFRvQRUJ6SJlrI18emxSbqZT5ZmDA3fsY9OTtLEk+6iJZGO'
        b'i2d/Jb3ca8XEYgztCyrDZmppm1evi41OFfcD4xpNSNC0KW7uSpFIVmwPrYOTFo5T216m8NO1STZFo+XEpaWwtcZWu0gI26taJ55I05UhWjVKR+NOQ84zyVsSEsjii0oR'
        b'lSnxZuN7i0aTHB3PBkGv1G1ISaZs7LQXSddqB5ssBHHaG+9MA5JDZSBR76I2bEiIj2aBhVS/ZuvJMITe+Nrx0rLBd5Kq0sNaaU++q5yU9MhW2geFBavoYNCjW2k/zzuw'
        b'l3XoYJATMEXl8BiZCvoorbn6rb4bJ9HDoj+76JZyo7rliECmeI1MnEKVR+Uine64TQvew1ShETFiUJdyYaRTyur1Isw+Hls+SDMFazsVSs8JC5iZPw4uzNX4Y1sniAoc'
        b'gEvskoYIw9spJIxZJ/ZKpiyU0QLAJbwY300TxaPxWk1UBocZ0wteWj8CC8cEa8kRKHdGqIgiEKh2dlji4+QX1rtGKoKzNHv3IdrLGQvRJ7F3FFHpRGV0BWxn+ui4AWlh'
        b'5NLw1JFY2OM9cAV3P+xdnTwzi+31wBIqGTfdzQ7P9ZezICknaIczTMsdvkmMkWrAQ2kZ5IrfWqrFuwbbO/sFUUVXLMKE6N87zccOgkZzql2KuuUczMFD5EKtLeyE+nFQ'
        b'GgpHYxZD/rwnoRq2w2nyVUd+7lq/CUrhxLzVq6BgXkr84sXrVqWMXQFV69faEP3Fcygcggv2ojbcDi3xCmzbYCFg0yZOwGu8K1zcKoJbtMvwQK81w/xBkD8H9q6GymGw'
        b'06BWoeS3Wqygn2kcV6Q15ik5aFrcZ2AoFIoxgNc2xCnSzTRSaAtlgWSwA+rTKOASXoEjWK/X+VVLtAA7G9LSQrF0g6U1lhG9vhyviv1uYBKgZgA6ODoIDh0cDeRAg5y+'
        b'i7PC3f2JFngYLzACkQw826cnBpK9gwHID30utMuAYivkWS7EKxlpPrS2p0hvl6sN6YaKoWkRmzekVDXDAyGTqdyETLZyjR8U2JIZXoDlwWQuFvDYsdFyIVzFIpHO6JgJ'
        b'bu9e1pSIRT6dAPVLuhQKOxVQYTcWT/SDk3C8fz8JB1UBfeD4lqg0qlERLboG6zV0GfbELxLwGFaQV12cSUZpO+aSTmaRdUTx5DAv2CIYS6GRZcAIsGexetHcTiuMv6/K'
        b'z9nFGG+IrmKWXdcn6bXDabawdw5cZ4F/ZHLk4k4dnsNinz9e9GwJKTzYzw6uzcBWEayjZgZ0aOAU7jew7rj5sdgcFu/RF45AjiOpwr4uhDY6Ohusd6f0iPF9fEMEzXGi'
        b'Z6U/dzZg8fXAd+fYvDds8/UfDm99it9fOl9lf89mJh/22mdjJvl9WOmyN2Dv6juf2MYfvbLw3Gbz4fzx2nkzub+p9tgs/vQdz9HHv731r4kfVy2r8nFYF/CPeXYXLix4'
        b'sl/t3fzJr885LPh9WdFvfMfn89OW/7ZQ+pfvP/nn0avzX1u+8cty108SNDdPqMO/vv7prcX37vR9x8bD9ODmf7yweL/fa2t23L/ydth29xWb/nbh02cP/vDpsKdf+076'
        b'672dy/8+YvCymyHfb8r9YcjyQcvemeXzZpAsLTZ8RN3J7Z8Nqpn9za3a576pUVd3PPUz3zxr/vs5dcVJgddvZlglDr/u63nn8x/sftzwy9//FDhoy1+fGusYrmy+bvb8'
        b'WPc9m0dd5cJ3fh7yfeOrn639KuTCxszPP8Sdp5dmWP467fOogvQh69u+nT73Tsnr70LrwJMHczq83pVss/7tL29tPTnzGae1T6xtXuj89b9+innllSPPpL7t8LepK9Mz'
        b'la+8+cafTVzHh7xw3ObvLTfTlxS1/wnPf+fs0OjxXO4bh66vmOYW/ELT7MHfTN8wIu/wj8POzn/ps3MfXiiY8fWB5A+X/Om1d4JO/fiTdf+IC3aqhar+zOwyH6vnqOGk'
        b'V3c4gAMTRSqHmvSRUBhEJnm1QaoSM0DlYD7DW0iE7dFqaB2msz6t0bCCt/TFHLU/5IZ0jaaEHVJmz4kaM1Br6YGLm3TGnuMaZjZLhGLKykAJSnB/sshRoiMoeRL2iRno'
        b'BXjeEwudVkbo+CW00AmXhjHrVhLmpiigcHVPWIcIuMqsYx5Q7+mohorALslOiVgppqhf8MU6RpVkgmeitGGZrhvYk3gFr62iKLQS3OMLTVJOliCMIhvHCfakF9ZCBeko'
        b'aNfSipCtugyPsFpbJFIODVuo0gdDag1qVmtYqpMTOZcKcbunUZYNKbYswp2sc8fFQ50aSwIT2IavB8TZAY1iBQuhxIVcd4JG6Vi4wkmdeHIaX4M8Von1ULvUMQGvuHS3'
        b'xSVNFhO2ilOAGjTJPr1Db9GEfUOYyS/UFDrU88b4+0K+a3eOYze4JHMdSaYFM2A34HU1FM5UBTGsqiAiUFjNl3hmLRK7t3FRFs0lgyooFfPJeGzqayvmku3GK+Oh0DUA'
        b'L8xxVpH3ewrKhBSV/LETla3/OwF4u3RojPuomGjMDriNm2XOWwgsM12w4GlOu40gk8h5WxuaQy59IJPQHHVKSiFmq9M8cxq6KdNmnNtIBgoDyU/6rz/LYqcUFXa83MSK'
        b'ZpkJBnZGmp3+gNoYpYKVIGacy4SsUUasbt3SqQMflXTeaT5L6eiaofb4Q2CYK95hJGHcSK54KbVm0ilm1JqZzX1nb2jPfIyG9h7AQzHnmJlPDAnh4mT6UB7JI6Hlc1XS'
        b'+5E9VIjg2CSivWoeZctjhgOtskJV1SiNcmmA/yM0EoqaNbyHRuIUmEap5dMnyNUGVI7dUeMKw7UnP15aYZAaiofgjGW/aMhhB/xwLMcLXdnqyBZ8SXfAD8V6JoKOJULq'
        b'GasJGgMxIdyL5eLCPrxsSf+e6kI25may2bqkk29+NPR8zCqTqXjUX1Sf0gPh7CD6DlLAcA5KZ+EJ5u4ygxaF3mMHJ7Ccee1WYhPTq14JFMxfYIpZpL/jgkUiyR9U9Rs9'
        b'kSJFctyo5TzWcNAxEgsYvOMqOIYnsZxllWDHNteIMK0XCxrIVtxkqzBLoYBrjUQXm467Wdsy8MJoR5UDOQaISFchzeQxZ4Aze2qqo5+aniKBeAqPmHCy/oIFtOB1ER8t'
        b'H8/DrhAsTl1HxgVaiQA5RExEScUqOBoiQrtB23QR3S18gSjKN4ztI7rusBR3UrVGSQaCiWLtc21oLgnLI8HGNJZKsnKEWPtGPEJ2cQoqRzNQEubRHJTUKNbgyGHuCkaO'
        b'GColDXOAEyKeGeZAxXidA9HNlqpseAOq0kSSJswND4FirAjDYqwkB3oZRY6TB/F4ccFW1u2e8j3zBG6awLlFWo1xHC3quC/bjxq4SqDczpHCn1dliH+8vM138E5eyRK0'
        b'f/MawfVgN9YvPSWnZTfuTxYbd5TbwsdwMfxOYRB3TM9zTKTJL6jFn1LIzI1J8Y9Pim3UMh1LE8gv3amaqRl/pcyA7DjNmzawjRwvDSxKWXQ9mulEYCxjeRF88BQPotLm'
        b'Q74H7kyfsyBuo2/Kk0mQk/HEMG7LBBs4DweXstZ9NN5y3iqezLNFkf4as35ik4PHDEhZQfYEThm5xW1GkIgkiwfxkr0h7h8D/cOqYRT3D5pnioO8P2iQqD2SMR0hao+1'
        b'sJNN6gVYRldC20ZLCSX2K5XY8TPMM9kLVYmmVoMkA+kLnT4esJJTCWxJCVC7TJxMsBdP0smUtFi0O5zIhBymMXKDIqnCaIJVbLKER6iwhTxiysUEScbxnpHTVTy7kIkl'
        b'C1TBmkAqBAoKXhka/W+NIyVNTwG60SP99gzP9SDZpiN3psvI0fWRAqUpinRssxa4J6CQVH0atCrZlUAvqFKkEGWdcluTJUXEh52xrFNVuH2pSQa2WGCbKVna5eQq7MCa'
        b'NBvaExdt4aqCfFjMLUtdbDGSPSDDa1ihsHdwxPP+7kPIxPcTlsNeiQjAV45nBWxx9cN2/1FQynMmsIOGYUJ5/CnHLF6zgFR3zcr42DD1HrswuxvtNb9W392Vs2v4rkED'
        b'n416aupo6z7P/bWhoa5k++hROwrC36iOSQoJ2O3evuKVuv5m4/pFF7k/HfqP3Rs/hH7q6BXfDPnFJNdkPcLXh04lnYzaePXln240//ly2l2P9tXjf8i68M41+4qvXvjT'
        b'hB+EquUvvhgzxvydXXeeG/bWvr33p/3cljLxrWdP5T+/ZHjU6VW5u3PqKjd+77HUZVr4T3sHqMO+fOH5Pc5Hn8/0Hjjot6GfLdsS9nL9d+8IBWUq7789837rEqfXbJd4'
        b'9B0U/fSCv731hE3+1ZTxpw74LX9hfujkmsbh/fdmnDev37c4t/rbAMsDyS9+IV/9xvnBJ2wnTTRbX37qG83ECXvGTWhqWDdqxuSwP9XvnbzXx9MkvXCw+1/2DYzMy04M'
        b'SwuJvhUQk/GqfPWVwu/3LXp3V21YQ4fQFjB5SWKb95XDv356aueWiFPjvhvU2ri73G75hvsZa99ZGv0g+sPmU/yvyes04ya+8KP9+uR57Tsurqs4MOqes/2zP6leO+xd'
        b'v/Gjiabv5R4b9v7k9NU7A34sb3jxbGr77XkFT39ZlPj9zZCxPygh9RvusxqrOFv1A8tU11HL7jtFtyTkp0bcVR1rezKxtTGw/vKtz59sm38/8u7c128fvSz7dGTccFmL'
        b'85psz7LPxoQVp27b6viyunVl61/Vt2Zeyb738ru3tv/g3vTceSu3iVMb8o9/TQSEz+dG1te3zEyIWZ3X91xJpGfVg4XFjcMyk0Lx7qG47+1Tp63/5WWvn0JL+l3z2fPP'
        b'Xyd/eeFkvLVDc/sn91qv8rGvdWRXjTh0atiq47vvJFu8s2587crRaT+WV0detZ25Qx72/W+7G49+dqZyW13WVweyvkkIOuVbsrH82sQlb+yuXp82tlb208zxARPh8IOh'
        b'b95b6pq97IOCG/K/j425pL769PChd4TvJnjeHD5+SGZi3JOTDqzK+lRzq3/WllfeKZnl+cY7gZeK3kuffrKhPW965l9Pmf5g+/YHHYuuFq4avrBoxN2/hw7pp/m+eHvH'
        b'TY+v/7Lol/DVfa4VDOvo7/Td13Mn//PwM2EZ0x988/aMmZX3IiNMV1m/57MiQPPNuH9O/mmL3z8jzU5+te7UG0+8O+RS9JWQA7ZTZ85ZU+O44dOkvKwPlr7v+sO36X0S'
        b'80/kHpm4O/3qAdvw5olT1P0DfO9aBuSfbp545YhTddm7Q6ptwx/4hsAtz5Cyz5xOPP2X9k1+P7xS4day0S/w+5O5VZdrg16YVbVpy73rEzcdLDdpt/jU/pWML6TPu773'
        b'c0X8mFU/ejb961zDgPeem44Zr0160J6TLFu3/UHenPA3/N1z1gTscHpdqun3m+kJ3yc/SvvG22d2TFDcpb1jT3wC/1Rs+2DcA5+fPng5amuRy6JrO4JWX93/1+y765sr'
        b'30kN+nnn1t9uDEmwaj1Yf/vmz3Zbv/i7+tm5d765td7rx3MXnN9Y9X37iOHBLfnve9T+8M81ww5/madu+s3i1oQnjrz+0o5Nh2dZFb733omMr5Z9rz450vurwVv6Hnc7'
        b'Pun5p80Wr3pg/c6d+Sfd7qnWM71vNrTi7qlwogdXiY6oBM8wvW8I7EzXxYoQhXOXVml1hiNiDuNhX6w05MicBHWiardEzbTixVRBVpOzj14PxP1M9bN2k6zBS3CMFaEc'
        b'g836XD08J9NrqHI4zRTAGVA+HGsoTFxvSmqCVDQdlMwc0ZWN8jgeFNkoKQMoC8YqhItKEavQaRp2aKEKrdzEmJHC8f4anWRbA0eZDcESOyRzyOfzDPDNjjTnmMaFvNw5'
        b'JVBFz/cWagokrQpNlXCT8LQsRCYVtdEW6MA2LXTcphHkTRGCA1yHayz5bxDRjS8OwtNqfwdyCK3kp2IdnmIdHort2EhGxJVI1EPoSSCDPcJYaCQP0uN63FrYoUV0U3lQ'
        b'lvLTQmZQNHuyb7qbAnc743ksUhPhqkLCmeJFIWg4XGb9vBoalumvW5PDxp80DnYTaWDIUlan5QmULZjBnNhBM0OOXS3mWk4aslB80tkXL00ibzUXwvE4XmYjvFweonHw'
        b'xZINWAD7cT/uIeNsytnAOUmq01ix048tXKEWIVL2wBGOM8HrggQOyFmtXd2IgNyyQKrGC0EKaLSnMLDtAhyXaylGz2ApFGmgCdso7qMZGRsTzhxLBCyMgnzRxDFmLa2d'
        b'mQrPJUAFaZyEtOuapC9WBrMu857tKppVuAl4UjSrQJUV65OYJ1gmdZGji8ocz8bbO1DCeduBEswetkm0TOzOgDqFixrbVFgYEE6abiU8gbW2LApoBVyFGk2gH5bzomzQ'
        b'4GHGOKRiJ+BFbCHtpX3tSBpQTetuwvXpL4Eq3AslDDtyJVRDvrorfyfuXzoEtkvhBOwcw6bRFjyYqnHxhWYL++VQ7+zAcVYyyWwssxRxI3fKsV7h5+y/Ec74kEmpUfHc'
        b'FCgYFCpdOGISq+PQTHONiryyllbxBgeX8ZxoroISvIR1agpDHeSLOU4UMdGKTJqZ0AFNrHNM4XyQo4i3uILMZT3kIh6FPaxzBpARr9T4OqgEDoomSqCCJzrccShgsykp'
        b'I5X0bCF1dphwvIKDa+ZwVsRUPLcBWtVQnNUt7Vm1TEQEgu2cyC1tQqbCGRGWuVic4rPhzEz1E7O0bge9FaqaLA56eVIcXFBgcZA96YqN/qRa5lgtwFUzIhUzI9VpbJxK'
        b'WxTgjB1ePGfmLsABuEaUH1EEGwF7FS4qBzJohWS+1ZCtLl6Ih6oENsvkeANbHMkouZBxJfWgEMjWUCxZvUKkKV62GAsU9i4bA/tBIRXfTvJIeT0q2MNDsXarQkWWBumR'
        b'iVBiQpbAAR5byeSrEzeLZrKLlGrtZ9wMou1S+9kcqBItj21EE8vRuLAGk9XSKMF8HuqIblwqmq8uJSepV5qJdnkZp/AT8GS8E2vUk1CKeXSIUvzxaHqgC1nyrhI57oFC'
        b'Njsm4b5NZCPAPIFOj0scnA0aIVrLmjOhhnRbCg18g44QAW7wQzyiWUvHQTvZgrVBc3DGWjSlhpqxEkkbS/tlOHSK9Fi6jdVEGh6vDVOlZtdOs+9Zb9YDctjjrCHaYxGr'
        b'qyvPmc8RyKbXPoGdVhGRcFhDmRjExUpeTypdBmT/tsN8Cdl0Ltmz+6AJ9tI7S1RksjmRfiMb+QWyz5FPlwbZSB3g2ibWo7MsgOIdsKtkT2ohA7aExwKsAxFPc2WITxbU'
        b'qvXmVLyaJu5kJxzwLHVHpWOLs6eUk/bhV8EhOCRevEHUhHLMeVLDoOJ5qCG9AdcD2cWABB8i3mO+vUAmw2EJ1pDLcBqzWW9n+lD0iRJ7vwyHKUsFsvDKBY/1cEPk6L4x'
        b'1Y9GtQZRC0v+omg2Q6wFSQxpa7M4eU6RFVnguGCifhehIOJYEM5M295kU96pYWcV2V7xHNsfhy0bCKel7olkerIVeSOkv7jB+w8VlY+DZPZiNhaJW0WBGeniFmgxYzsl'
        b'61FzbCVzAvakiTOwhGj0FRYSevrSgMglvDO2WYoMxBdh90ANOa7MMD+D/CDvgMNkfPtiuQSOmGEN2y22zPRWM2hW2AfnGTQ5dmxgE0o92JpaZp1VMf1FwyxUzWKPjJkB'
        b'RYo0SzOi02bjPslIfi4etGCPhED7JCzsr8Ei6iCw40fjfhs27MFYFy7OIN+N0+ewy5ZkNY2FshDW0Ew8CVV6sPaRWExBUylaO17Hkwzxa6YPWXcUGMwVCwKcVL4BZPNm'
        b'Bn8o22rCTZspI3vVmWGsU50mQTkLpPVx8oNjdjpztBuZYu7MWGAfzWCPe+ClQzMcMkCRDcOzcvI2pTgbSshm16pg9zpvtJ/GNt8+ZJFCncUgcRurHSUlr2V7q/ccPUf1'
        b'k1DJ5qHCZr0Gm5SBKu0q8xbI9NkFu8RVv5fUqINMFlLozFkS2MdDiRzL2bWAubhXwx5zX8H2kckSMzkeFtF+zzwhOHbFexfr7jGWYeDGzWUHylgXPKmruutG9pY+2CaB'
        b'erwhESmtD8LhdXhK3RNrnuLMmywTcRP2zklV2NOTEK4vl2A7Dw2Lh7LhJf2AhQosEEUcUotdEk7OCYt98KjYvO3uWEx2eD+yIdTjCQleJItw8GS2TNZiNRyk7TP3C6BT'
        b'RN2P+hfsIFdCZMVj45jfacy2TIVquA/H8YM53Ekd5+Ly2ENW/RVNIJ53NbdfutmBbdM26yRQAI0btMDVs3Eftji5uAhEDKuTYBU50wY8KYYSX4GTaT7QqKCzX1Dxw6FR'
        b'hG1ei9eSNGRPx3wzXZMknMXcgVgqnW6WIS67djhronAmLXLLJILicKEv5pHjl24KStzrxKhrAklXFnvSiUwW7L7xi9nVNeRShcbVAc/5qPzUdMe5JlAPtrihYDnsphtc'
        b'ILb7T4EDZD/YylN73UQRnaICTi0kwlAnjjFkz9NCGQfCdTbLBifba+TOLn5pKrLqibwmCEQwayaHHZ2ha+QxWqnZ13pCuD3dzyzxssTDxytVNMxegKLOqGvM9aCB19Ci'
        b'YaNPjogCbMJzWWqXALI3Z/IzY/G4eKVGgCNQmajWx2TjkbGs+0eGclpYEjw0nCGTCJATsVHV57+DWit7xHURg0JMlJWlMCs+c/IsoaYv406ebZyDnAEHi0DE5rwtw9qg'
        b'iBt2DAxQRiGJWRC4XAtGTD/3J1fthMGUj/yBIOnPD34gyAfzynuCtQ1v80AqmP8mSCl4sRU/RhjDDyafht4XfhMsKdCwBXnC9hdBRj+PEWQP7HmrXwXyvA0/nLf5TfiT'
        b'bIY5gzdmQMUUrpi34Qf+KsiGkp/0bVJ+KPk+8CfBzJa8i/5O/mo5kNSFoozYPyBlmTzk3eTqUHIvLVcEPpaTMuxIfeSkRKsfZAr598IzFmodIonIsq4k38fRN/MDfxNo'
        b'bX8VfpbZyfmsQUZ8N2LPGxCuPmrgDBKQnyNDNZRaEemZ0Iv3KJv7tL+h/6j3OpAXs6T3dp7mFwcGqqTkG4sfb7ToBlGSso5j6dUhXj7eAd4hDJSEpUOLGCXr9MAitIYp'
        b'1Osk+t7s/k+gQ2boO6iMzmUTredSLkhlWrzqX6Sm/8FPt2RTBd7KWq4DISFTmhPtxw/sPHWgIgPZVXPymXoqxKvDt3HmjMhlJJzDdmMWe2Ey5HEzl8uICIiHe+TRm2t/'
        b'aswfDi4iiZFrP5sZfDYnnxUxFuyzJflspf27tcFnLdDIITM9iIhdTD8DEBGJAYhI/2LTmHF6EJEhMUP1ICIUeISLGRGj/B0gIiOLZTHj9RAilnEmMaNiRhsFD6FwJV3B'
        b'Q+xvWzPMHUZIPT92dXzqfdceyCEGV/8N2JBpYnL6BJVwW+oVFOx9WzJvwryUA3TaV9Nvh/jHx++YJmZXTvhdoB/ah6b9fmAP3etYMqc7BfZIOS4m31AIjpQTDFYo2Dsg'
        b'KNSbAXqM6QamETJ/fnDsxq4p5G4pDbTBj3Orux71QleR+wN7K1UPhdG1ziqzLmXQcUj5iyGehq5zUv5KW/QmvdTbO9xTLtJ7/jsoGEZJO3vyz5qIKBhWi/CqBtusU0xm'
        b'QoEWre9SFMvRTLFSKbA8JX0jL+KQHRq2Mr751XheQ3WcB1NPUz5xn6hbcQ4fqaPM4z7nvts+aPET017nPRKkLdJnVbwoB+5MXKSN8Ckw00b4bMWGXrg4W3XRHyzhqjfB'
        b'gH4p6SGZNbDb4npMIA1bUx3YcG/nGP36pgugRu+vaqPD+BJFy2CxO/8XaBkjZY+LlhHDakzhAGjM/n8SKkO3Ch4BlaFbRY+8Y9pjQ2V0XZi9QWX0tr4fgl1hdK0av/93'
        b'QFV0z84SEwmikmgOAE2y6iVlSP+YMQzUHvAWXcZZC2lBzwgRpoKcEw69Z/c8CktCV5PfgyYRH/c/IIn//wBJ6FacERwF+t/jwDl0XbSPCedgdAH/D8zhD4A50P96JtyY'
        b'BIYy5lysgMtQYxRJAE5RGtUyLPbX8ud2ujCgA/MUeBw7cG/8qtNmgoaiM4x/ZTUlAP/8g4+fWhu3/Km3br5x8+2bb9589+ZrN9+7eaX08N6RO8/vGF3TuENVePmto7lj'
        b'dzZWnc933znyQM5ECZdz1XLynI9VJsyiEocNWOjo4uzjjE0LtRGyWAeNot3sxlh7qNqgS/zvkvUPHVDJzFSzQuE6HIZCA1xUraMVWpeL9rEda+Cq1nxCqQ9W8+5QBbnM'
        b'GkVeiPsV3WObV+MpqXwz5OkCPP+dYFd90rvTo8SdBYbJ7zJj0sjvz2wf+FhS0JfDHy4F/Z709jgVH5hymdfJY0ZS2+eZctrU9h5v0ue1j+rlvOuRyy57eOBttGm3taHQ'
        b'rY/5VE4z7SapKaisFqfQSmqmTFKTE0nNVC+pyZmkZvqkXCuprSGS2lZjktrDM9QNlcX/X6Snd8Xq0oo/2pztRHJg0OTZ/2Ws/y9jXfm/jPX/Zaw/OmPdqVchKYGcAIbU'
        b'ZL8rgf0hW8b/ZQL7fzXtWmJUCrQNFBkYjshgu46cDEpxF4PtaoJmEbaLWtbNsATOiXEQIT6YH6SD3fLxw2JGDBZOAa/kLEoeypSwBwrN4Arshd0sqToRj+AVBV5f1zWv'
        b'WptUDS2zWEz1ODhmp7G0FPCAuzaXe2t8GjXlwEHcD5V6Z/XiOZu7IW/pYLcEypt7xAyvwQ0hzZE8mTwamzrxunC3GefjJCZu4G5Gn0pDgSLGy+fKZ7H7Yb+aV+uxtETp'
        b'l+a9OmFJAA3q4rhghamvLRZrFjL5uT9eMNcSsTr5hi0Kd14STpN3/QL8oTHUB874BLg4+wZgLV4mxbgKcEExAQqDQ7jhcMgqAU/AYdbwBXiFp+QYbnhZJMeAGg1rOJ4g'
        b'Ly8l4nkzNHR5CU1I3TAhhWahssxwKRcJhaZQiVXYnEZd7j54EmtCwp1lcEa8WzteoeJT+rY/EWcKx7EUtrMIcGs4CrkKKORSrEhfSvrwnolQw4K2oRqOxmELtpKRbM/Q'
        b'UOC3Dt4RzuNRFj4PWVKaQbL0eZ9Ii3CvbVz8t7JRJppX6WyrCwvbc94S3Gy8/5z+1dO+ypV+JyJLJjnN2Vi7YUzuoYpAr+q62O0x1uN8i+2rclp2564t33v3xte/Phgb'
        b'ssDspv3V6uywu0vf/6h/+fyclH2S0uo3LO7cCFpU/JGDm9krg99f9BGXdnoLPj1/3otfzJW+OuynsmfVNi//aDM+48TL52Z8PyguYsqyu9fvvXNhdHNUgJ38zD/Vob/d'
        b'vGyrednzrfBftny28pM7F1K+GPDp3yL+/OzsjZrMD9NL612Tm5KuvF92dEtFiHfBg/UvLPKb/ryHZ7bnVm77Ob/kWeNVNiL8FxQP6MSik04aykJ8ZkO+GLtQOH1cVwK6'
        b'OQLU4kVK7pItunD34QE4SkkrIH8KS+3EAjF0AC7h/n5a3mpd6uVWrCf6VnkCK3yr6zxFJO41wqm9H8RI1rlQv1k/LRk78Dqsw4NP4Anx3ReCoIgpP3hpBnMfS+AQa9Wg'
        b'zLFdGTqW9MezZEtoZPEt6/CQeY8g2lFztWG0Ltq2ZwzDw2L16YrN9+efCOas8KrEn0wdkVwCdg/DauqWN6QobrYR/fwniB7WoJ7gJ8SYkV2gmTr+86yYXugHJ/CUI+xN'
        b'EyMcRZsy7prDem1QFpx1hAPL/ALEQSHV7zteggfhLIhBHcnb4BBTKskmcQEaRK0ydyALu02E8ni1sazLNKgWEy8nDO3JIKf4D2Y9LnqUIriB5T5K5IxLVy6TUTcxb6fl'
        b'4qUOafplJVgJcn0eY9aI7qqU8WRFs8dJVuzMUzTp3d1v2juJrZGcRO/H0kOvKw310Ec16b+UlrhWJb2/8pFpicYUuD+Uk0hdFz1zEkcHsjNnPOxb3y0pEY7NMp6X2CMp'
        b'EY7hKTGp8AAWeXVmJcI5brWXZ3iWRMGNwiYJ5uL1EOYnWtffzSAl8RLd0cZqSZZiV9NcQl224TFydpQumsiOA/UagfNZSNXqSCebyckcywkaMQAuaVMKaULhXKyHDoEI'
        b'CH3YjjQzVUwpHBXOuSaBiJ0Qjsdgn2YjjddsJdtfCQf5SHE52B5ynvwm5hRKM3k45og55Gobq/PY6fFiUqEJB9dwH00qtMAi5ttSm8PBECwmfbpmEsso9LcSaaHqrKZp'
        b'EwppNiHkJ2CTZwRr5lA4gvliAiC5mAI7HeC8tZjlV4VVE3RZftMTsFKf44fnoZj1xCnvEi5b6kGz/AKzVzuL2W3HloziQqcU0u4Z9Y/kIPGPG3x9OP+YMTTLz29bxJh/'
        b'L8sv7vGyw66YGmaH+TIBKIUyajHyESeyl24k0kuBE+7VBRWVQQuFMQnCG3g6kHQxtEkmEJFGTQPbNQrSc1642zoUC1azNn2qtOTc1k6guX1OLz25Xmxo/Mj+3CubVrLc'
        b'vm9VKhEFgxxdh8Z2ze2DXDLUPEeT+7CB7PosIO7MEhpXxzL4JHa8LebPWLaelfqqh4ybuXAoLTVhzAwNp+LFHNJaaE3QR+hidZQSW5f/2wmUj9G1Erlh1zL+uZwBydrE'
        b'O4kZPzRr2pw1Yh7pOayCHAWNlIIczGGJd2rIZ6K5YzJcMEi7gxY4ik14DHewlEKohMtwhuXebX6SWww73UV02xxo8hKT78gdh/y16XcHHNnV0bi9rzb7judcsEjMvsMr'
        b'ynjLxlReQ9nivMbeTQtVa/p52929+0XVz9W53/g8b2kzZ05F3oL5tdtfHG1/dIFNZfhHLSaHPjj8p6dT/tLy4faSJcsmqwfYTb630Cm8Qj1gn2JJ08ofJfaF3804+fPy'
        b'/H2Fms+2fDbjs/QjsyIyjhWuVe5/7obtAqtPnJfNz2+qWNx6a+e/JD++9uL3Nh8/tTYyFmba189NPKswWWD9SQa8+NWCD7+c93rDcbOrwqBjlvcapi7e7bB98rrFmqK3'
        b'ZjrUeiz+8pmFmTjlVJzzdycsEzRLPuE3KC7Ftiby64eEJb6REXk+cczo1typ66p/Wbkj7LkL7/uffnA1/q9vJTu9NtsmYv30No+RWz5xnf9m1Vtt9sI2zwRJwrsfvD9t'
        b'3tWhz21L/H6TrWPayjTV6yGRJ350PBUwS1MwYb3lxUGXnzgVP/HL9e3QNjJ683fznX+6Wheqir178fvkDI+2Qs/Fnl+U9ol7adhfjg8LefnPQ++8VNNQkyL3iHZMGZ6d'
        b'WV3lGfnmdNn560kBL8LdsFM3+oUfX7bmzfeTJrQkW73eiMtHZsz+atBbLbduLTJ9t8VPdX9oralN3a3PokzPOIW1cV+bvDUyPHrKgY3t6ZZtD0YvXLP3X57pjRMKbw1Y'
        b'eetebVb87s11c1xfH35LeuTkjJsYN3rbnh/vXJ9w66Mr4VX/D2/fAVfVsfx/zrmFcmkiCKIoYoFLVxQLdkWBS1OwYQGUIoogXIodFFTgUqSoIE2UDqIUQUAxmU1MNz0x'
        b'prdfimlGE1/6f8u9FEte8vL+L34CnLZldnZ3Zme+M3v1k1974fzqfrcjcLOLj2h8cu/u+pe6isaO8XTtqXnWKjBjVNC4zyZeWTHx+xKX5vgnutZteSrMJlQZ6ve93Xm0'
        b'96zez1q7U3V/0/pCaD7Y7+fVbHqw6ROTJj+bqH/dS/vi94Wf3ZvyleONtzOv23w7KeqnP17cffcb3TTT38ptJr95KfWD99CcBRN+nB+d7eKfuS3yudCf1lQe96t//MBj'
        b'd+Jzrm8u33/h1/ra/vGvisem63z+u4lvaOYfUYLZr3vu1IT9/s1jc67u0r91d0ve19b50796yQ7/7bY8pWi5RfLW40eS9uRPf/75q9O/euOuxRtf7H/jO5PoktLjFv2z'
        b'XnNxdW3V+tG5urD36q/+M0/OTanVC+y9Mx3FQ/+3HmNOhr2Rfm/CVxPNf7inc9W07JLbtbcvjf7MvO5O5oFtXf/65XZp7roJE0NbRWMUN4Mibvxh8bnyVvHNxtqMOXHz'
        b'L/+k/97F5iniFP1ky59/OpRyzOTxxyr4K2EHU9s+/+GV90J+fvGXaekdZTUdot42k+Mr9lyr0Pnw9dEbw+rix5xp2dF1YsUCt7eP3DnadTbGJipVJ/LF71pXzK0Yc+3D'
        b'FW/yP7gF7LvnIpHrXv5KdDcSNa1R3TmT9HXc2G1fPPfex/I4KqvyRqjx4Ug2OIW3yfNwAmUw19YCuLBYjWebYKsJwZKKLlF5eT6qnWk/PEgJ9ERYiTch1Uj6AhbEL2Ll'
        b'mcLZpFitzh+As40eTZ1jHSdD/TAImoQbBcWo3kesj7cJ5m2PzmH9tEkNQuM5AS5TENpcrIhQNakeeqaqYWj7Ua/vIAoNHZ+WKCdvnID6UApCm4IaHRPk3nhHIqgVBkQT'
        b'ce6QIYWO8dDJYAkXUim0RG2mKkshQLQRqJA+TPaDXjXYDD/rs6RgMy/UwIjVvdqYYc1QH97O1Giz6aiZYShwP05oAGVwGettasCZxzpGqwt60ZrHkXqKIXgzhSlz5M7e'
        b'FKnGm4nd+Nm+0AjlJqziLnfoUiPOUrW9GOAMcuAINUXF60ZoAGdDwGbQbpiIjgNLcaiPTsxjiDOOc9OmeDNUiz+n9L04Ba/1w+BmKM1RgFroRIcZDrAak/KochjebBmq'
        b'FrB2dhi100IOGM5lmDNowpvRhSGgsyNwkBnTCiHThyHHVimRiiHH5sRRR3JoHKurJA5Pi1IobMx3BnWjR41wGIt0A8CxAdAYKgzGYlUR1hTJmCVCGpy2H9T3dmMGS3eD'
        b'Alrtgm1jZX6OenISvg2aJXCWR61SdJr2awTuY5UGS+KHCjD7acAkoXCVwe2yzFYNhaShFl3MwgySFqXF2LfYBaUzSBochku2Gkya93bWiatBVhSRRiOIZ8kZKG2cWAxN'
        b'SAVtY6GCco8LOh3GwGeYm9u9BtBn5ugEG4OT6BAqofAzPC7n6LzW4M86fRmFM3dDGgMrEKgCqvCGvMlY2aeScAEqxzTsQCoJFtLPHyD4M+jSY2iXlkR0fphGj0onCKg1'
        b'nmNseWy0hQZ/Jh7HB3rBGS8xw2GplkCFYhj4zH+NyBQdQVWs4CPycNlQ7BlULxegzx7qaZtsUb8XRZ/tR92OavSZCJopx2+2j1BDz5qhhjSaQs8uoqO0YLfxUMOgZ55b'
        b'GSCCIs+gawNtsdxYhyLPeE6BLjDk2dxY+mEEuuSswZ3hYVzHYGcoDTXSDwWRSIM5EzvwDgL0oqu6tD2+WqhZDTgjYDO8Jp2Hs9AM6bQnq/d7KQbRZpgZBVSPuibSLx2w'
        b'0pNOgSJyuOyjQYp44BrpuJxKgCy6FBBP/mYKOduL0ihfzzMjEDsGOSN4M8wcYzC/sthZm9Ap3OyhkdoLIQ/KRruzkPTZJDzeoEh7BaVZ+S5lg1KHejl6KCVxGxJuTIpq'
        b'abkW+qhFOYiGwRtFpQBNe9ERiiczwHx3+n7gGRa/ocub4c7SvOn+g8esGK7chzuDE0DESYo7a0CXaR/34llRpEGeEUwwxZ3ND2Ir9Wl0FnoGUGd4f7jqjKcsA+64YIqo'
        b'kWdiDvVDBcGeGaBuBgHrdEdXhsDOssnehOrwpjeGTYYW1KiBnxHsmS2ooBJh3ZQOytL9cJrBz6ajPDs1/myaLp2H0Z4WFBWDZws5Ib24fDtutjm6ILZHneq0qMGodRGT'
        b'rC0EjVydBVmUwyTQDpkDiIxFkDnVAD9hiQZmoNMyTbGEPXWxvtQ+X4CWIJRFR3VSkAsul6EeK7ZgjdUaLqgBJnhaQa79EMBbDPSJDM1nUXcIA1Q2Qsl2RZ1ByJu7GJW7'
        b'YlK0O7E9pn0ZVKpBbzxmr/MM9BY2k3HNqU1T1MBgDdxt+0bMlLIANlKXUAUeqwG0G14CWhwVqJRWD5U6s4YD3gja7cxECnizQp0UYTg13oIB3vASMw/lwtnNkXTXdJ9D'
        b'RopC1Fa5xA9C1LAMk8621YwtJGwRO/bfAvn2GoxaImRSiFpUPDo5CFGDfuUQlJoaooYqEmhZEeg8Ug1SiuOM0CHRHExiKF7BFvO6bdBF2FUh10HZci+61aehVkzP0XBQ'
        b'vFzHhTJYKLRsZG/hF3KpEqWFyoVFS6GbUjOJBIpjmDTt6c4DmDS4YsfW1ZN4ARl6MgtpTgIqg1y8YxNTwK7xa5BKcyoqd8HLUP9E9mHWhoVKXKc/5qN8e7zmGu0WbYTs'
        b'fUvxLkCRqjoozR4zH5bHYqCUnEOgUmGvB0dFNVSUlKgkIUOziNxI4FU8N8JUhNKhYT+c8KAgPS17vMg8ANKD3HH34dwoRg/acHfpJlofDgNAtwGYm9U4vErU4lGkuPJ+'
        b'dAyVKAfBrtYhAjSGsRTE0LsRuhmumoCqbTHxcj0dKNeKoBtO0M+gGzX4aAC9o7VodAK8oGZveRCIh/mhCDeSQvFSZ7AmXoFz6zRNHAARzoRTcBad2E7Z2HU6Ov9QIB5K'
        b'i9BBPTq0qcss4RID4xEkHjqWAg0W6DyTEw5jTqnQwPEgzUbB0Hj8drZ7X3XAn1IwHgHioRpDqHQFtvlH6KPzQ7F4Is4keiaD4rWhasoTUW7oogxLOTxkQCuF49XJ2czN'
        b'2iNSY/EGkHgm1pC9N4JWS3CtzWooHsHheW6FM5ARRuck3plq/TQ4PGH3OLgkpUf8Hni08oZD8dDRKbhVFIsXj65SUqxFx/GC5kh7BNWoisDx9q1lfNqDtYJWNRxv5GI7'
        b'DRoPVS5ia1E5uoBHnOLx/M3kGjxexlL61AbLdxlqOB4u+qQpheNNxos3GaZFeIdoGQbH47HKcUiHwPHQRSxtMR1gJ+pXDsHjBe0WoNjMh1I7GJ1ArRpEHpSvNByE5Mlw'
        b'JXR/yV2cOiwRCt7iCpahYi8mMVXgreaMBpCnBx1z4/C+RHeeSrwNtrNzMiySO2rAdxtRptzgfw+3o6goZlr4M6wd+zdag7gzEj0aa6c9gLUzpv/EvAFvhK+tfhWkRvzf'
        b'xNZpaauxbmKKZ9P+A7//B/13Q+r2ANrud0HMkHUm9AsDYvigCD1zfhQvxqU68Qbke+k/RNm9pjd3OMrO/FEou1H32yH+KcQuU0vjDvhnxpA07udhQLtHNAPXTXAJCW9r'
        b'UHYigrJ7mlefUspH/u/Qcc/iSj8k8MF93H8JHXdDai/wBpKHIuFs7kPCaZ79Yb6IOiIkQZGbzN/h/vNtnrOFq5IdULn4Ad9ZA/Vv5aEH4G/B4mKtYp3ikZEC+VlsoP7b'
        b'RP1bl/2OFkWKwkW5QrjdgPWJZMLRO6p/1OCoEc1ZrUdgdBR2JomQhkvDtTI4kqs7VwjWwte69FpGr7XxtR691qfXOvjagF4b0mtdfG1Er0fQaxm+NqbXI+m1Hr42odem'
        b'9FofX4+i12b02gBfm9Pr0fTaEF9b0Osx9NoIX4+l15b0egS+Hkevx9NrY3xtRa8n0OuR+NqaXk+k1yZHJZG8GkxnSv8mub+1g0dRf0sRtcxpH5Vh2hhi2oygtLENl+M3'
        b'zMIFevhuf1NvySLfIE2q+w+7hPv8LImj09A3GO5uwE0nMY6kglCyd2ZMc2C/XWniBPLX9GGFaax4SierRUM8CNUOcRRPoHa7w08TIxJoXoe4ZJKdNnG4B+DQHA8OVhFh'
        b'W7ZaJUTsTIhQRsQOKWKIiyLxbR1WwqN8gIbbEodd+MUR1y+vSCuallVplRKREGGlTNq8I5o6M0XHDoFpUO8q/DgM/5+4NSFieOU7IhK3xoVTz3Xc5riY5Ahq9Uwiq03M'
        b'buKlNSyJhZVHNHV4sl0kV3vsxgx3AyPeUmpHQjYQzupx0FDcwcp2sVzzWpiVMoI4tCVG/NkgkTG0XSIn2I6wIU6Dane9uIToqOjYsBgCMlBjkjEJCIDivo4qlWFRFF4S'
        b'wZJ14LdY763CI3bi5VVpFccaTj3/bNXPFhMO2xGnHO4AtiVuxw7imUx57z4vQz+5cFO0a0fMTemWsB2JM6ZvEQ1ZdiTqpYdapbzxDzVoTOuoJpWWjC4hPF5EhEgDtSlb'
        b'lClN5/aL9+juEw2YssXUlC06IFabsiPl4g9/5v8CjGzYJHq0n9mjXA9xz5jX4VpfH7XbHM2aQssdHDM8OtS1FE/Jh/uj2kYwVnrUfP0TeBMl6xyCUtkShmd8KG5SKHP/'
        b'Y4UNFDKU7R6RyyYsPDyaOYuq6x3GdoRB45Mi1FNXmYTn1MDS8XBYxzCXWpaihsy8sKTEuB1hidFbKKPuiEiIGpKA5hEAkQQ8I3fGxYYTCrP5/OcJZYbtcfpqZhvuamDp'
        b'pyRHv4ETx3a8fM9ePnVVU6L8GXmXSv5G+0ElF71fu/Z3N+qun0QO6aFgvDV0oALUbS9fEAj4XZQlhy5QycmBJ7AvoNbJhoqnQdQaCj1wfC/WsEjILO4AdwCKE6kdt1yJ'
        b'VV/828XtvOPzums4aujcAo075SOgA6/17pw7ViBUMf/6448/3A5QrzMrl8gmWYW5J5dEFP0N0AuFqAiaUK+riwsqdnUROMlsPgBdRnVygfo+OEHhWiXKNkBZKZujWYA7'
        b'rF7q2Nny3DRULLVH51bTNvpCuqXMbgPqxw8EX36mDpzAJRA5Ih41TFKX4ASHg0gRuuQHz1nPkVjvhyKaDhUdRT2CDAr2sUci1MtDIzqeLGfOieP3GuIyoGQZLYY2w8sO'
        b'K9Gozd5L4USsG6tRifZYVADdrLhe81mogzwbA6fIY+0ZQiy66i8XJREFZBHUmJFsHY6owNXFBx2eIXB6+4Xt6Ayqoi58cajBYuA5qneaIeX0DggxW1EzpdtirDp3DTxP'
        b'hJoZPKeXKuwgh3t0lFElNEWyVCCeQeZw0pO8u8Jz0BOF55Yaaplt96K+Eej4dHSBKZIrHLEKlTNfB2uRIyFPBFUTXJKWk1f6oPWA2pMFpRtRZxZ1+hpcqo9C4SjEz4OK'
        b'segKZJuidtSuMIFshUwXt0jlvTKQi4g0monOySjbrE1Us8KyPdaKPX5c0lqOhPxKVwz1lBnMjZPr7L3KFmV5opxA4kKpWIUukGPuxJFiwrrUhcbfS2I8WRcr27USCerx'
        b'mAyNcs4jxQRVrIjABKdnF2WQEY46pm003JlAYESX+CnoiA11O5ChBsiTCTbaCcl43MW8HdYac9hHF1biwetwR7V68fSrFn6S52J1eOIGdEwZAOk76eGuSI8PRd3xzEeg'
        b'dT1SKRM2xqN2PfJRGj8J07Rdk86WqKsZSqhMQV20ULjMj4JczDakLXuhzB11rB41WN9IdJByxBZjKBkYcahfpx5xOLiTOv0iEjfsoiYBDNRZkxwwvo7e/qs8NR/NUNMU'
        b'0lAHh6piZNAA59HlJEdK/UYH/HHrvsEEMvTjAMfV7CMOFXLh6JI2x0Nb9FvfPy5WHsIT/NVlu3YUuceNXGT0VMq9Nz5zf/+nwllZI8uM3suI8tw1S8fNwKOf3xFwqmDE'
        b'dpMnDVecfvfI2Ruetr3Z2fDmxPncmTOnz9QsLi4OGuH9wlc/f1Sy/MMfnk/9vePO2z8E9/U2VJQkNfe6WC08+MXmL78yS5lY5v7Y0Z5llglTA5caW34V4CUeM+uDOpPv'
        b'TQ8VHC0ImTqjVfS4Vs/dWckHO698I2v+v+pjr7wUtEHbKsN6aZylx2TLXfK3rPO7u0o3P1tgcEB5/NYvhZ55iVpdfVbrvPeOn+TqPv5Nk7aCMKX8i33fjr0rKsn8QoHM'
        b'my4/rzqTeWHL4t4jq3xuxtg9523t/fkm+XN1O3Ys++XGDPszJZtXX9t1vffUEjOfZzeUnn5712cd13W/WX/RyTzQL+LVUctuRrfZXl/7/q0FnR1vpMTWVJiZtSTE12xo'
        b'/yni6Y97J228fC7q2aLK0rP7voh69WpYsa+pbIdN9btVv9m7RHyLRq5p277CNHHTqCculixufOHl+My86I89t34WoFWeOTnxtHvd9oyCismvLfA2+2zTU2Wjv3/HaKZH'
        b'+CZx03Orfzi3Z3tNa/j1VeU/bZBMM+p+0jLe7Jbrjplh756Y0vDuyIJ1YV2LY9bod8y4W/y23rxvHX31f9VHK5Cro03LPdPPJJs3xnyQ9dZ7ZmPOV70UUHjhuuGvnY9d'
        b'7gz+o//Haf2vl1y7O75y9nPKuyGVP5vnv7ojuHLPtcDllcef+OJx8/yO7t/MXtT9flbF/O/Hrqv8ObDDbbr/rjd/XTBOT9elauU7v/le1TG94751jTL33YYrr+67UFq4'
        b'v399V1M9GuV6/D2bF6pe2t86u7K+erFvhHmg6bPfhT/1nvM7bdsizS8++ewT/elWzxodl9oZjjnyleux5U+k/jBmRumITfIw+SIW3i87HGXbO6Hzib5Yl4QGXrFrCYMg'
        b'dq8MB1U0lGJWzyT+7/4oW+BkcBlPLmiDNHagjze+QnsvdAYqfbTw55n8PJS3mp4wLUON6LzaJr7ZTh2XFQpQIT21S0H56CConInRU5vET5SGCtYRLHKgC+ozJmmKnP0d'
        b'URNqFjjpAcEOHYKWROJZGYAK5uIP8cKgIuZUHyfI8mehSDOdPR3sKL5TiwvBW/E5pApTR8aENj9NyFoHdDhsIGRtOsqiZ4zRcAkayGkZynWEdOiXctJNwkQ841nsrVjU'
        b'ukIxWcff0cuBHP7KoFNAl+EE9NLiPVeHDfoY4F35uCYZCl5YWODN9SPXDEFaopOoQOPMvNWfnSceF1AuOy5ErdA0cGCYBaXsuK8XshLUJ4amOzTxu4q2sYPXU1Cy2B4u'
        b'zPeCc3gPF0cR60X5bnrSiaWI6vXkwHvwOHEM8VbmLFC5ON4Wbwa0hKKI0agDj2qtjyZsJFxFh6klbDPUW2B6e/sqHKEf2snJn5/6VHISOi5xh3o4xmLG1WFpp0+Jcr3I'
        b'uCgM/ByJQWmnQuDGLRNDLfQupKS23GdBDOL5OuT59mT8WN9DQD3+uClkR52/aweuzc/RwVdTkSIKV2U1VYxq51vQEqwsQpUoDY7cF42sAXWxo82ieCdQ+Tt5EyxDyzZf'
        b'njPYKpoF7c6U0mK4jM6zHZsc+0bHEjv/DJGWHA5RSjtusKD2gRySfud0khYn1RH0QuAqo1MaaoZ2pQQV0oN60XZ+HypBl9mR71E4jdm7Y5rVoMFzDFxEV+iJqp7xCtQR'
        b'u2vQYAeVSTL63VZ0aBq1O3mjnBmQLuIk6BSPel2C6QSzQCdQvsxX7KSgx9tNPFRBL4tJuxG1e95nyRyHVD6aCJq6ElaxAtqUWJao3zsQwXI3M07iDzMnqQ2QS0gKImJ/'
        b'nIlqNJbLfAWooMXLn1ovRaiMh7wRLNicHjptjis9CVecUb49aVcHD/V70Ena5OmQjy6hjq0Eca0OFBurtkvOMF+v8aWZHEpipvYKPFItYYbFFKhW+uFenNQEGoWsCXTI'
        b'tq2IJeM5mF0qfJMxtIqQymskfR6GV6dGikNwRrlwRocY0OCUAFmjE1jAyrKYRff5Evmh9oHA2KMCaKcCUJ8Md6qM2J2Ylfwij6fB4Z1sCTkDOQuwWCpncj/KXCCXcgbh'
        b'Ig+UA+WJ5ERzfVQgqFLgkHUy6tSPH5THCHDbGeV5+jriLwI9tA1GoAZG/zOYu7uU9rpYLtY3l/Oc1n5hOpz1ZA/rsKKRrrRPkOs4HSA8rhUhTJsEVWxpLvFGZbjDXsQg'
        b'5G+PshOjUL6EM0VN4hFwHF1iJZyUbZbhovEUqZtOS4AmYd6GKLogeaI0HU0BzmFQh7K0OAM/0UIabZCMhgWUipXeYRbEi4hH3bwR1KBOumEkYZZrkDmtlWuiJlbg/lAS'
        b'paHsbcMMNahkPo2aaIRO00+norJkJdRM89NEV56Gepm94dBekqErh1ji1BE+4w2o7RNdhTN4aVf549lBPL+P2bJFwdkT5Yq4iahOMnO3OqgpqsdLWL7ST672nVLwnPts'
        b'I0vRCtSKmZrUPwcrajnKoFD5QOjkGqU6Uxd+p0yJyneyBUUEh/k9sdbMdlfv5mXv7ahwtPNLtMOLiWGUKMyJS7TBj1ajHlSLGToXmtTtUzDDGt67/CScfJMEynShhLp4'
        b'pUKGLuaPhzCHv9tCZyyTukOr1G8KYoGYoREyZ9mjTqOhIBDo2MNMfYfh+CwZeaLxi8M9aR+BekVwzjOQMnMg1ECFPYtjWufrKOW0UZ8ABfqJlFJ7Z2M1cYiBCWqVPup4'
        b'jzYecv1/bsH5L1mCHhZLgOQ5/Td2nlQuQpc3EghgRMqP5fWIbUWgh+q/SSVG1LpDkl0RC4hU0KZ/GeD3DPhx/BTeljcWjEgyLfxvLH3XiFpIpPwofhQu0xj/NsD/tPHb'
        b'uoJUGHX/HZ78M6CWJvKtVA1eMeH3mA49a7ovpIFcwmAjHxHrxcfDoSh6/2gsRKy4wdIH6OlFnLfJ/X9jjEnjeqYMNcc8vB9/KURCxr8NkXBOm1OHSBhezUB8hKmao296'
        b'duxgFRHlZGVHDsGcXGa4agK5PBgu4a83L/7PmndB07yfx5B2qM9RraLDh9X4lyqLwpU18je1Q7awA/ZH1tkxUOcEim+moN5IK/oZQen/RzXL+Zv6IQPHxyHRj66+a6D6'
        b'KYuskmKj45MiHgLm/7ttyGBt0AvRHCn+WRN6BppgRyigTMQkoIeSA+eR/6QZCRZ/NuKXB+p2Cowj4YNiI+NoQASrsM1xSYnDohH9h/WTwDKPrP/qcI4bEh3nP6vM888q'
        b'g4HKLAYrW+y15D+sS/FndT2pqSuB5Lv9y4ybkPNnhT490AHboIfENNIE6fhP2VWXxhkIIaj/RzbhueEDRkMFsEn7n05UbVZrYtwj67w+UOdodViJ/7DGSM3SsDkshlhC'
        b'QuJ2RsQ+stqXB6qdRaol77Lj+Zih9r3745D8x9Q3GGjVlpg4ZcQjm/Xa8GaRl/9Rs/5pzMqtD4tZyXP3myNEftGL33xVpCQS8ZulRYFzSQhK7cgPnuc47Wy+uyFZzlP9'
        b'd/Ja6NSoO/ZQ669Rd/Zuf0TcSVuNkwzR5/+t8JTKRe0xuW+Lj4mIDQl5dNRJUsGb2mri/FtpIo1rHhZ78qGV/f8PGvrgAIj9gqKXfTJJUJLbH6yUKsL0Ij+I8dThObEH'
        b'vyx//yCvPUjjNo7ROOEw/4DsEhKyOS4u5s8ISL6++TcI2KD3ZwIZq20YBUlrSZ1EX2aW1sEAnZpgUMzayh/VH7C0CpkSTFsRpq0wQFsRpa1wQPQo5iamLJJo0XUYbcez'
        b'gKwoMzlUGY/aoWex5og/EC5TO5efodq4sTpjRtjsRI5ag6AEzmKlziABCtAxHfLFGd4J+tdRc0i3reaLqd6/zJdyNCYEXIWLI+mRCAPmk8gWOQr8hx8JdrEyYKUjdKL6'
        b'1QK3aaEWVEPfriQyKyAzAvoV3uQQH/LoYRc5bECHIBcrcnZbJNBsuYlGsYiJgm7lTj9o3quxXowZTw1T0KqDDio2QK8mgIfGjVc/iJovViSjUnJao0DV4UilxYkdeTiH'
        b'KqGdwSY7Fm+3l9ttm8yQvujgYhmLSNGGKvzV6ic0kGRIVAONWLYpiJpMTA297eclEUXP0UvM6WgJkAfZ0EDLjN6krfBy8HH0wkWKeahClcaMpkWeUGUvhUInLwc51g11'
        b'ZgtQO0mNOEYXLUgsDidv1AfNDMgDjXN86eCNn4KuIpWjH8r3SYUKnpNuFEw3OSQRR9WNWuiyAuV5kQB7PkhFiY0JUYkHIl/E2c+ToNz91g9wpEzDkUsHOXI4P/IDIcn+'
        b'Ci9m3M+LpNU6D/Cikx9luMk7JZy2SbmIWxjqUO2zkmNhYk6tA5IWAxP+shqHAnmoBuoYHvvI3tVKLztUN1btygu5mJvKGAO0wblJ6qGiw4ROLcIjBT1QzUC67agBLil9'
        b'/ESOmrPDjmnU8OuHin2VxGsYa6OQttNSkUrHz3/OqgHoQMpYZyiCo8wQVj9zLgVOdKDcAfBEGWpdSUd3JypGlyjcZU4YA7zAGVSC20gexqGOtcPxLiKruabu06nJmmHU'
        b'+0LQRbL/QkPkBG5CnINcwhixMGXffV/OW2eKalF/EktLdAQ1EegJOouy1fAT6IWjcJmaXaExFh3V5FqicBcxpilBvBTrMKvviZVQwDI5MSBNIeqGkgNcEjmv2KGD+u1x'
        b'xU5yO18nuaO3L89Zw2HJUlQ4e6sP/XzCXFSkGJou6exEVB8Dx1jZFZuhWe0azXNT0WWptmCGsqWUcXnUNu4hmU5MSLYo6l+Np2gPjSyPTqOSydQJ34eeD5PlBLLxXEDZ'
        b'4Tw3ZY1kO2ShFmoU9LBdTwwYAy7mMVoPZlLxg4Na6JgRKmDT7gwcQ9l4YYmYoVlXoBudY8SrHInXpuHLylQSKwiK3SmsfCL0hJG1KyJl2OqlWbmmo0xKhwOoWsxWoAzL'
        b'gRVoPGLRecJRmR/+bAWcZhAGOLtGoGy7Zbw58dWHw2JNEJO9qJUuB2OgYK56OeA56NhHloN1y+lHOvsX0TWkAC5p1hDRdnXi4th19JSan0WOrWpRXgzqpOw+0gadsPd1'
        b'nLAbTy1xGF4CdSNpNXtFhGU9HR0ouPOEACe99hmuoqs27s0llPVQn3YC1deBSnSWsqcOXIaLQ9ElIuhCGYYWmENsOWrjrkOnyPqFh7D5vjVMs35tgWy5QFs0C5UrQYXa'
        b'k8WYfRo4W3NUD5cN2NqqQgehR4napMSow6G6FDgGeKiYN0hVABxHRVLic3HegXMYj6rpPqbcJeNMTMKknFGo3hydZSyAwKFdmAx632GxJ1QvcNF0drM3EO94C48LeMnS'
        b'63Zfym6GO+tz5kE9YpJbeI62mN1cuESHM9KOxV+HOhyZKXkw0AIVCMn/pNn7uI0G+/l9/E69cG41XlPjhfCBiJZU3lHnTuaT75O3b+rMjYqIjdi1M2F+hI56jRWTWADr'
        b'8B8bdFC18r4TT5KRiAQ1dfByxBtVPmZjFmqBhVlARSLUAUXGCih0NdrshhqhcTc0mko8krEksMIUjqzFi97Z8KT5uPTVcCKEmNzxZCxydPKiYBPvFQGOqz0f3IfyoUPQ'
        b'5fFKgJr01keGGqFqmmsZmj2t7b33znCUO+JVS2P20eLGrhJDiwJORs8MreCU13Bvs6syIwJ7Yt9eaFSxsbDQ9sv+mGe/d3z/+qflh7NNnF7R0n7FPHrUtAuCXql0pbjj'
        b'uCjdw/hz0YaABSM+GZOzb2HTa4u+3Lcw8mjn5qcOr/zj6XvvXS59q6L6o48m+Lxz9n3p5pkH5eYjzIrNn2k4X1Pw7NTrXgcrC0vSTx+OX2E7M6Pj5BPhd/mNxc+WpRt1'
        b'nt34de7rjpOXL3hx1+dP7q4Yv+5q+spDXs2mT5duqT+vKi77tV5y82zsT/w7XyQkdctmyxqLOgudim6tufbs2B+iXs5+JsxvzTpHgw/MfSp3fW2U93NdmuRr3ycu1R+q'
        b'mX84K9OuxN9idYXuol87jdNfkB1MOBU0sX79zcDaGt8G1BO3auGuvLaVjwf4eQRvHyt/7LJdaleF/Y9zm7IL4x63mbI8YYnixY1lFW+/fKej742OmM9W//jimOBT71qN'
        b'/zwg5QfhyT+MNrnM/3nk6B9eqh+75ymwvrvKNUM52iz4xwOO12+VWo/64cwPuYaeO466vfF/N4ybz2emrP36WPBrz72TlHdb9+Pd15q/OuA/Nzzl6S8tmqsyU9Z93d57'
        b'fbcs55ecvTkzzZ0T7vleebJnTU737PYnCixHjn07+LknhCvN9+7O358+2cG33DN4nvhm1DOxT8QWz7u39d7GwEqP6OQ3b2cpgye9uD85KDLvWcenDnxVX6AsSJL+tjCu'
        b'zG71T+XXd/n8rPt+fAQnr7z08uQnx7/yZsecZ6dumbe75o06eG2z4fbPFp/Lb1hyV3+71xLJuquKlsb5sw3ruryP3pC2PTVz3ZfHfh1347NrXHt22cTSnwtt7uafj+pL'
        b'fHHOWv97s27F7Dc78VbwH8Ute29+a33rgMuW9RMaHpvzot/KZEvV/ovnkue/Em3QaPFidl38K1nKZwIvll23rnj8tRHJR16ZfqG66rbeu7fXXOvc/uqku+XvOcasPPnt'
        b'jTNfLriQda763e/Gvbvw2vVjX6aOqMtN+zrF+cJvUnF5r+6m9AW/ysbGugUfNpLPZiaNFpvpZC+PwtJLg5guz5dnTqQYqhg4vkBGgGE6tlhkRpegFQuII6BeBOV4pvUw'
        b'QE4umbkyOzmWaAiUR3uMMBMKV0OmJy19ORyGy2pE6CUsT0I3tO5eSc0aGwLkFA/aQKKEaUyk2WrrUALkbLH3gnOzV2mM2JO9mGX18FwsdxKwI7qI+gbspyvn0Or0JAlE'
        b'GNoN7YOy0JqttLpJUZtoX+J9nOVSTj8sGL8xZROoGKgvf1HsEPNp4FQNFJRaTyM3MXRrC2qD2kEcJhyajfJ3zGHNasJL+/kBBKc+VBIDKjq7kJm0WqF8pYwCb4Qg3gSV'
        b'zg9EZ2k/o6EhQI1jlnGj9eHyfmijBU4hrkXDM11WrYe+5ATamTnaqJcg2LtQlwbEC2e3QyfDEPY6wkWlDxkRvNwpJJyunoB6sYh1eq6UWbiaPfEGSAzzDlhpQGlSaBFc'
        b'xyqZE0fMdnUCWhYQANrlu5elsHJ7tsoH4cZ4cyxRA44LcbcpOBgrC/1qrDI6D13qNJk98xlaKAcVQTUmMhaTrElKTCwLzOaxaN2sUKfUXY/aNRk6KUQaVc2KRlnM9u04'
        b'EvcJZXt5oW6S0SxekC+3i45h3bmMCrepM69TgKpoS7AL9NJKPeCogmQKjCdOblJOd40AXVAHvcmolj5fMRpqZNC4k0Ix4TCJDXOKx23vhAKWv+0Uh84OpBqEzL0T/Vh4'
        b'gyj8crPM29fawV6Khf9eHgqWbqcWuZR5UKX0QRmQ5eek46Rw0iWQM3O4KJ5J7LTMEePwdC014gwal0ONGsRqgoVgVITqUBv1oViDxecjg1BTPHlKNXBTgjVF5auYu0iZ'
        b'c6QGnqmGZuKx6VxkA2mMrgWWeIQGAGbZkEkdRtavYzjJesjfPZhYmIZxGO1CAzmQcaBzfHzwzPvQsgIcWwH9+03p0CixHNsjS9KPQQd18HwkqRqb4AwdmmVweSfBHqNO'
        b'PGijlkg8eNyP4yztsDUmcoPM1nE9HFYDDKEBT7CzlLx44vkq1aZhEm0Tq7v9cymMz2TpCg1seL4lQQ0H6NNGitDRmbLBVHranLAWLq/AxFRbwA9hqboes9c0lK4GJUIl'
        b'nJIwa3WLT4IakejspcEkMkRipoTGdPDmHDXQQXQydBwctqfUGzvVBQ91KWTdl8iPQgfDtlEWGr/RTI0bnL2dJvHLhVq2dJ6Hq1BNfGoxA+K+aikEuDBxAipgIH3D6aiH'
        b'QBmxNpevhjPCGeiAOoa/rJ8JmQNRRvDMaqQ+VSLEsvAqtE2QysGPLNv5+LkMz+Qdiag1AF1luRShwpk+z5GjTBpwsVWYjCs6u2oKcwTDesIVoqIRLHY1v8s6IGYNXQN0'
        b'sELZau/vgCexivpWyVC/sG8H1s/wUkcnTP0cC5kdyhMR9+GYKdOhBPLplz7oOBwf9LUhnjao23mGSCsZTrLdBlXsxeLg/Q5mM/HkaIEzEfJR/78RXPfZSv95rMObugQg'
        b'E0Id1KmE/R6Rt//9kWsqZ8Lwh2KKSCQ/Dfgp1EbtwNsRyzLF6unyxrwRL/DMykywe3q/64kEqXBH19CWH8XbCsa8AW8uUGu1Orcg+60nWBBbtEAs38bEoo3lYXPeSCA5'
        b'Bc21DQRiwR4rsqCWa9wSwYrX/UNM/hd0f6f/i0ipUk5KY/SPYkhKgRxD7pHfbw8mFAhxmkutR8r5ToMUYbqE+KZO4q7wiMSw6BjlTa2QxF2bw5QRQ+zd/0HWAayf/E6M'
        b'eL8NGLh/xX+JiEYyjQzAvz9RTeP+GBqCMYmYrqDaTvc/0F/mEng2VWE4N1Rq6IA/aZCLqPYbMt2FRbGZNVOdNX0zdFJVJFULVapTqmf6b7bXhDKxgLNiUK2FchY/7ihU'
        b'LwGVvfNAC/zVMXHGu4tRMRQqsIZK98fciTNYaXPHqCtCKjhHC1kIp1H6QFWo2mN4XdCoz4IEZwcBOXVRwDlbT18nL98VOwkpaJoMlO27ch9eY0JNtSehCo4ef6ErUrg8'
        b'6Hnf5a3xsz6/hh6frPWbo8DzugjlOmKpKIgWNnXGCk91B+ZMIsEbI+jxyUTox9vXkHQdrGZbzcFGpBbW4TfAKW1DdGE6RSpA7v71oFoZ9wi65BomEbtQMjoF3crhZckW'
        b'+K1SRw0mHSMyUGSqNpyJgqroLzKuSZSnMc9+f9UqIrAvduQik4pSy/MpX/9gb+juB/YLd2ktrdD1eM3T0yQzVCc3Z/qJnC31p0uiXV5x8u00rfEMm1mcOS3kMbOA73Vs'
        b'zyQ/2ZOy0erllvwXe+69o4xK7jhlqmVtaGC2aVbY5I/f3xT5oc8Lh9f43Xxs20Stbb/eaPDffKkjXHDRWpYePe6kT2Po25vtFnh+8NKXBfHbVrt9uGFOBOwvKFgTPmOe'
        b'b499nd3I7UJwp/NjT37+r+ctp6Y88fzqKSG5u+5VGEWulup6m25a5bKqLE1R98Trl3qXPf+52dne1+cv3LjQ9Kys6YtXOuescYt59csNeYuvWexL/+nExts3o/ue/dLp'
        b's+iEyimJO978IDihdkNeVe/K1R23RJJfc24FK70stq1XnO/6+qWxLvbPd+73vGSfMHt2yoQ5tzvHbFhy9d3Ul6acvT7NpoL7+PdXHI83eqcH1ddO97OPdjSNvhIytTny'
        b'6y2fPDd3/3PL12U8//ZX39moNk4/HvjFlk/6i5vjXe3d5x3vsZjs5Lbn9P6ISzpO7Se/Nu2V2/b9SyujNbv59GfFXUsOzNgjfGpX8VRCSLnRHefSkIhxUcYvnJhskLf/'
        b'nZez7r5und78Y2vEotVfKtKfad32xotCfX+Ax0fWJ+8mHzmv8q5ZWfLzx/+a0/e09dRXul4Mevlg+DPfFagSZvTYzv3j/MHm8De147YdfS+g/LHct3w7pp7c7bLug87k'
        b'O6FBKTff3JCb/Gz6beGtwvccP1Hs6X78vceXtYSdrEnpfuy7npnajacCHk86fL6v98r7Zp13Ds6ae1s/5tWSV1rueb70aVxN2PgP/pAXz/nWy/XqoncnJd2Y8u5jqvfb'
        b'0jrnztrzsXHfzL2znjLbe+me9091cT0nRqRr+y144cT2hBPKu9/Mfke6yv0dfs6Lk+eZfXJw9NvlVrsn1MwKnq2bu8vpo+5UPinBaLf5brlLIuFvG+iH08OdzGJQ5UOd'
        b'EKEPVVMhKcwdHSV+jctR7aDX4w71w+WoXUwURTgBGQOa4ni4xNwud20e5mxnZImaxaIVWD3pYFpm21g4SBS6EMjRaHThqVQYlkIzOijzsX5ogDd0Pt6A+bkVg2qh0oeK'
        b'1KgRXRkqVmfsoTJjNJRBmQIdgXR/Iq4n84scUBWtfRs6hS4pUQnqHkwaXqBHPZpNfCFbiQXtIrVkQg60USeLKYOOi6EzEJqp/MKnonQZ1jHySKBTqKe9lI0UUDpSRTM5'
        b'vAqvqjSJTrwcMlERz0lSeFSO5ega2rw5VBbOh8wBj0NPYGHrsMqop1SHO0sOSsHPdVMEaFZYMve/LlS/VinXQZdXD7gjovOogPbMGGtUrTI4CWec8GAKa3h3KIAcFla6'
        b'ZxJ0KjEXXB5wsYQCFiNLkiQedF8V482Kua9C1xTaHrxmtivtvDAhjpNlk5o9DmEhv40SYiWUcEMUhk1TBiK/HdhAK945VqZWN8zQObV7+obxVM+2RVkThjkbXoQGjbch'
        b'CajEdOl8faRSwiXDoZLxBKzCMqn5AiZ+MVMB8LCeE3M0dFA1ZLFRKIDqBCVRGWbAReIWKoJGHvJxZYyL0ZFFs4imn7t/AVHHRYD1gFLokdGP+fVeMiffBPIYGhNxxSNM'
        b'0DEoFW1bvIMNxcVENxlUTSTYPKpPausL4VDqSBsmg95QdeQ5vXma2HMC1G4QEsk+Nh7vdvWgch7EKSSGPwKpcN6Z0mGSFzrHdNcZWI3RqK+9eoa0LTYpfmrFFY7twlRm'
        b'euv52SwYmW8MVlfgIDQNaKfoKNYcyIc+0JiqNt4sgSYSpUqwg3JMXTLNTIQDgzL4gllDYB5YfO+jwytBh0YjFZYE/N3JTPbnUdoIOM/okw2NKIsEr9MZOeCpuhSVUOLa'
        b'copBZIQDlA4AI7o5ug4YwSHUNqggwMXJCqqK8Zx5hNh6IWKxTmxm4F6p8PrUrNnVtWcJm2WJVGMeqwPHQeXj5T8g0KilmfHmYqyTXkLNbC05jlpJHCbCo3jOZriji0St'
        b'9cFaLdQm0dBgtoZGoCJynCNkOTujE0PMKC7B0pGYV1WJJI63ezzUgcom9OG+vBpPXmhHZcwtuXn/0qEiY6MlTeQVLJoKWZ60C257TRTqajV1LoF0Yr3Bqih0OqE+WlAI'
        b'KofDpCR/rOJhbto9kRYkEk3YCel0uVk2c5sawyK3YggW6FkoN/7/qDD9t0K+DA3pMkXjrfLGX1OddujRBOlEscH/C0bCKH4sVlAsSKp0otxgFcechnMhao0xlu6J0kMU'
        b'K5NftbXGJWAFCF+biCywFsWSmesSV+E/BBJbg+SYFkikDW3eAKtl5K5UfU9XJMXKlPAHuSsVaQvaIgORHnU5lgpESWNhY7QlLHK9MS/Gd0mLdPG7D7rQUpVJrR4xX93f'
        b'/5tOwGr1yGkYkd/9Gw4ntX/uAUybT5y0zB+a3tw0hEDjtyQyLTCE4OBJalma4ZwmPKdpzgvwj5taam/Ym3pDnVNvyoa6ibqStxeQ77aTHwvJj/2kHp0B77ybWmqXuZt6'
        b'Qz3ZbuoP9yAjjkvU+YYShNHf9H936DDoPvQBrn4mGY8DHA0gYyAWHPgpm9WBXkT/o99iPZGeiGmaHahywv26Lz8R0rnRqEEcMQeuPtpBay7HsTgn3EAGYK0BZy3h3zpr'
        b'Rd3vxEF2Ekfufmet5X5JxG/UCtUrXV2mT3ObOsMVuuFCYmJCcnySEq/yF7BM14668MZyEXUYauvpGujoy7BYkAk5WLs8HhiACtDJ1RJUNIHDe0OPTBYwinpA7IQrc125'
        b'sUqOm8pNxQt2epIRWcZr4OpcV/GYRRw3jZumvYMadAOwAFjqKkAllu04V84VypPpy4tTUbOrFF3ZxXHTuekJccyz4iLUojZXfjSm7wxuhvMsZhM+horRQVcJXsPxTsC5'
        b'oRKXJBJZfcbiia4iuJCE2YKbqUyhJUCOGTrhqqUI5LhZ3KwJqJPFR29dawIdHOo24LjZ3Gw3VEMN+qgoFcqJOF25Hgui3BzUApm0cVA1W08p3glpuJ3c4ngdWvQoOepS'
        b'CnHoPMct4ZZMRsyDCFOvGF1RSuMhg+OWckuhIJlWudjWXMljiuCZ48F5oCsoh7WkCfqNlBLURx4s45YtXMS62Ih3306lKCwWaxTcciy3XWYNOaUzQ6kVgg5xnCfnOcaZ'
        b'NTsbiwkXUAc33gtLpZwXaocMVvjRNZMR7k7ndHI06z1O7bcgR71YJOwQUAUq4TgFp0AN5qzt5yANlaIOqfFeLABxPiJQMSKWeEAd6uCX4OXJl/NdPp/eXb4iDHVIUA2e'
        b'gn7ENWMMa3nZNhKoTTTbgeP8OX/ogmpWRrnnaNShtcMeswBmgozJrMZiJ7gs47CY0cpxK7gVoFpF+2mK+lGZTLwTs85KbqVoM31ZB0tcjTIB0uAY8XcNRGcnsUL6cO+b'
        b'ZVJoCue4IC4IsvZRfkCH4iQyfvNajlvFrVofQ+/p662WSaSg4rjV3Oppy9j3WaFQLxPBJcCNWMOt8YSjjH/zuD0yrX0om+PWcmvDLdnLGTNRJf4encKVrePWQZUJpbW/'
        b'gAdJJSaxjLlgLngG5hxyG9WPRiWgEhbhRX09tx4dMmYuHUegCrJRkQRPtwsc58Q5QeM4RifVxihUJJqL1zlnztkGqVgxlajejmSHKuC4CdwEdGQ+I/ZVOByLirDQD1c4'
        b'zp6zHzuLFpKImsMCeWvy9mRuMqp3YbOpHCq8UJGWXgDHuXAuMj1aRkgIOWKS4iJOc5wD52CFDlFKmcyyCpRswhvFFG4K1HvIHZLI8bMUKo2oB4HK3hnlz9tmT9JMibiR'
        b'qEKEeldvps430/X86W38Q4T6neBQAn5+njyHviQWg7kGHdaUIcLkzGDvkDK2zKLeJxti5uHP6XMSarYPMifjh1jyrGYJNlrnwdnBdkBuosgYF6Ai71wKZL5l3SEjWDPw'
        b'C6hZIhI4k5HkectsWoP9zjD2OXl8dAV5zOPH6ATrhM3unerytbCqhMvOh0rowS+sw5OL6B0mBPloPwsV0Tq0JrLPd0EDi3JREbhL0zosPLejsyJrNRV2o9OsgeWo1ZPQ'
        b'CHfeSuBGQu1sSgFzVMXc6i7wukg1BlSMkhPV/VsyjZ0dnkZlSYREpIDquZhGF1AP6d+yWNaAksg1rAOkEcZwWGszroJ0ADfnEiuiFy4TF7N89s4aJy1j1ond29gJYd5W'
        b'rBCy6u2dfbH6T98UqfsxYxw9hV2JahX0NlZM2vG/anQVLmOCQT0h9ll32podRAhnfSUvWWFV/PJcdTk2pqzBV8aTSKy0NvxDAe2kxZQiFnCKNsgIT5/BPmFV1VnDfYQw'
        b'6LQZ9SeaFQ+Z9rwxqSwdtSeon4oXU/5FF5OgQl0Lbgy0xtBXKGGUkEPpsgvf79GQ9pCnC2qfy+gyz4361qXCuSUDzdBaCGVwRtNfK306dBOCl2jIqjWBG6kfTjsah9cV'
        b'wnnLoFPGni0m465jSTuJ2eEi5Txn1LCZEfQgoRUu2loXjpMO9i+iL6DT+oxv6HNMRii3pUU4oBN0SFIWosoBShKHr5F0IqkpMVHJ8vycwIOgGugH5u/zIerXKDW2YT6n'
        b'RwHdJIClvbeTM6VoAiNFAGuKjwFmbTaN4SAhQhWWgkhfITuIOXedQvmu9qhFj0wzkYgzmYkfmqJ8OuTrrHl1I0VwZh5coHxDe4LlkDRKa7z/n4YzbBbhl8wmE74xoWtB'
        b'PYtusxuVRrIm4JImQsvAPO9wocTwEmjWaDXv4VlykVVDWSYH1TJXzQI4vJ52Q7Ai/gy9eqQIlI76aB37/WdppjJSBQaLNjMiYN2yiDImOor72aBhXS10CgrQIQ1/44VK'
        b'7ZRYF5CiXhUP0m5gaaqclOMCJ5lvVR6cwR1WMd7D87QftYk2q4txQAfV8wS14XmrGVz7mIlai9VUg2PerDeHoCsCqdbgTZuy2RJ1d42C5DxrCV4xoUVBkxmSvGfa60nM'
        b'CgEz1CWHz6gAeSxhoVyXesWlyWncpYU2+qE+LboezFXupcX6HB7eha2bQvXOOG5jNyeu1Obwvqkdvj3U4culm9jNWu+R3CSOs600CN2wYeQadtMglXqh77rkHepzytGd'
        b'3Ry/15DDjQvwmhfqMGPXGHaz315KPONdNk0JjYkI82Y3+6KMOEyvWf0poT5mgTJ2M2+GjMPSjfa2kaE+TxiZsJvvxZpwtriiH5eEzv3NU92kmZ4SUvvOO36hMZti1KmX'
        b'XuFoN9fe1gqNGalvyVF357fczfCWyGlnWIfuG7FcDyuFQcvog3VOtAirpxaH+ryatI29vXUXbat2hDxU7+tYCffZqVLy3zMLaAW3VmuRp2uDJ4Y6lG4bxX3mSv+7s4Du'
        b'wm5G8WSIDkMmx8VxcVjePsGETOIJaa9lFoQ7gRemzrnM7ZhMjRF6ZBPVsFy/6SDH7UXFtMrbyaNI89f+4hS6732bcNbRHGdGklLP0H3f7pU+6OU4EPSLzN8otZ8jy3k0'
        b'mEZKDem4KYmODY/YlUC80h+W7MhQd2iyIxL8M9oN1dr7ES9f6jvo6+OPjg+zB9K0USjLezBzFBb7TskWOfjR5us4rOOwxORiFRUafCEoCg+Jn1/0OlGdSLkKV33bIc53'
        b'5XOxIxcZfVW68dubt6LKL76Z/53uiwu1P1ho7ClIf9XqmfB8Y3iN2OPGMweXvBi9KMbA83fO4JZ9VYFryGMHRVUHA5a+KF03dpl74MbXX98Y3DDy0BGR2exd3xUs5/ls'
        b'2+oc3aaGMD7JwXqpyHfp1upcg961INnwxOQN10wdPrZr/XBO7AdTYsMk3fFazZdUF883Hync8NGkbVWb99+dsKLRu7x0Trxx1Nq3QzZIUnZ+q7r+3jfbdxS/nFX0f5Hh'
        b'5U9E5P6yMft4/O3QhYHzyk9t+Eh2c/uIz27oN3qsfWrJXlVFzu3ru+Ke+ResbLN46cKW77+qH+f+VZtu1p0RF6PrTHJTP1pRd2OaZIXYKtDn1ye2LFjdlVp3IML7K2Wj'
        b'b93zhxtPfXXDbE/X0caxvRvcTJ2Utx8rsLg07aqk8Whl0ohlty9c490SziyKKxp7s7rRwlln2Wn/4Dmrek797GqcvOrCC0qH+IgTTc+3m94Ub9vwqcW456QXP9owY9Xy'
        b'+o87Pr786W9bFnyx8uTzi7u8jKqiLjisFyfLNs0y+vaZuBj/139ZcKNtq9sLzl/VSQwin30t4sfHrk9bPqotbHHrnY88FZu2fa5j0zm6xOhW3cGNr36yJ/iJwNjnO6N3'
        b'im59dMYmrm7P5SOmI3W+97nh+FPwqvSJjT/2TB75xpbj8b+8cjUi8GROl+Hd3Zb7w7pLXyk8l/B2bO7G25mzwPvaHNP88e984lniuyJ8/iHfT+7m36mKrvlurPP8/+uR'
        b'PxN7w0DU3vhBRJHP0bLo2RO+ubHA+k55h/ELYS3LghXGf1TNa6/4OvLjjtv3bs/U+7HB5WfZN0teydCvl7MskysSQ7DId0jNtRJOso/oc5Vq76riiVZItW0xC7Ig9uQx'
        b'T5+CRnrkPXYUKlGQTCD2Cke46m/HczJUJhL2AUs/g+Wq+pGoI0CKS+9WSjiRLj8VzqAydlacBuc8sDB0HOVBi7eEE4fzePEvTWI+S/nurgp/Ry8vBzxF8rzEnCxZQGVe'
        b'6rQ2fgp0bIiT2klHkrhmFjCLCLqESy6wHxeA8pxxg8RJPMqaacjc8ArilfY05YuAxb8r0MGv1ttMO7IZVOuRKhFra8QKM+CZlov6WUfOTYtjYA50cClxGZcKeLM6NpES'
        b'KAEdc1egFhvqEIMrNKNuOubUbWgEKnNXUGvU1I3J/CJLqKJH4XGbAwYjEGWRoHnNNASRKeqSj/nfurk8+phQ62+e1d7UVW4Jiw2J3hEWFUGPbP9F1t2/4u2SyvmKBRrY'
        b'mP+v/7wtHcFiL+hSfxddkbU6yjWLiW2C70rpca4JjQBhoj4+NuKNySmYyAT/ZUUjgOvSKNzavFgQ02gONJ42/jeFJiXVpVckgrc1/mIanyATNEeIopui6B1RQ05v/yJh'
        b'9QTNfkPK6iPuK9MJRf+K+0oa95T5UAcWquCicpvh+5MEK/Dd3KhNYm3I9nggFquuZrckJ7ND8IG8GpElROoOxGAV/2kM1oeiLgmE4MH83JZ+jz5KJM47uH4hUvincFvh'
        b'gXolbA9eEiJQkfCWEKr3+swt6lifxW5ORNxcY6sGEdp6egV6kunuJeFm7pVCMeq1RWdQTbTVkp85JfGX+eyj87dCPcOej7Qt/Dx0w2MXjh0sOPZqdcbUw42lbVlt6RNK'
        b'DrqKuLjXpe+U2cgFumxFjnBXaGLFSKXozFzBDHrk6gg/voEPTX8mE4nReUtXDSjjIUfJN2VbtkZs2R5CZRk6KV3++qRM5WxZAPw940NIMOIQEu1g0JNrSMkaRuejh7C5'
        b'MIybDQa4WR//ZUqkJ7e/zs1p3NcGQ/mZJIVF7aEkcRnJGI2FSobW0HhgJaOuAScsghfyRXlSyIZaqFlNsmOYy1BF1HSGQW2ZOV3h4Kc7i1hgxZzUQtCFIkd1lkpjaLFH'
        b'hX4CcUHNEkbwJObXScooZ+zUMVuTWw/UBSaQ3Jt0U8s7AJcUPlAPDX5+BH6m7S8ofVAV/SbTTZfK8S7JDftGT3LmlEQMLr02PVB/Z7yIK6kTVvNcoS8VuCeNUoNZRz2d'
        b'UBcVw8UQst5zkGDVJM1CiifPW2unbMrllGSPkZ46F7gqye2FH1JEnEjCT3aS0tqyYiXqSLFTEiRuuzklEWInqFYnHv9YIGBLWVsrfe+ttVR6N3IZ9czSVg9/9t7pl/2f'
        b'C/xYQmDCBqvalUTg3fVW+8ef4i+nBC3mzH84oCTnrWkdX5yoDlyln6y/E4vxUke++MYVJaFq7JVb1NbbaEu8NJQWI9tEnzyvonsFxVO/xeW9anh6zzMOz+AppMUL0+Zo'
        b'0XoPfSKEVb9KOIaTTzGgt+6lNXB2r2Ja23F2oxfRW+98tHq3kwqvExu5jRVLaOvGXmtUkdzrHx09wx3Wzaf3fin9SPUy/vDjmP3ckbm36fnF7vXEc9ULundTLJArJjOo'
        b'BO9lm6INVj7NKWtxoS/VZnqsXOT37kK9i1HTnvH5XStYd0H1l6N7Fx4yPbl1XfGM9mPeNU1LHeatrA2YmrqiQKLl6fRSkZXfqx4nL9qEfDlly7wFCxa4H5iev3OL9jNz'
        b'/6UtHlE08fPFqZVNOoVl8bcKy47F5GV/It0/9fUgvcgn6q++XLNz+w2fZGmCsVnQ7+3rPc8se91fKXzi/vY9PRPp0sdtZi7pvDd5dldQt0vJ2gsfmZ67VPJC2suTQ5ff'
        b'Wt3fZKRwij7v+pvi2r23N7o1j7f1i5v22Q5R28rJrUHyPT9+Mse87X0HywzljcdaVeFbPP3a6xU7EvRj3u02/Kros20LV9zpua58Zv6bDr+O/2hiwDfjb32SZD/2RvdL'
        b'izfoLLjw6SpRx/Vbl0Y9JY0wsoGrARf3SIu/9qx/P1sZUBE9Q/Xity+GSPw/3fpz/l2/36999NPW2+Wf6WysXpfk8dSX2W+8VX/9zI0j6S5LkhvGPP/la4mr9/0x+oWN'
        b'12qtc3bd+/lq6tJr0b6OloofjKteijT79uVfRneU7f/hd8n1D0buO2Jf6nd5g01fn8zm+U9XNn0R2jNu2RWbsHefm/LdtQ3eL0zOOJqa01olWjpebsTSuudHQr5CjtdG'
        b'L0dbKSeNEuyiGNwDamPRRSxkBYxTMBygNhwT4lzt2MN+OApXiZuHL9Yig7TFU3loQVmjGU7hTBSqw2uJziQSxSuXQMC0oVo4AHkL6XJsbIPalYnJyfoGkGdoiNr14iWc'
        b'cdIoVCmCCmhCR6lQKMXbhb1astVeSWVbLMle0oRoLF6KVL7QwnGO0CRABr8cFe9hkmY6So+y90aqTcB8H6QrBZNwlEkfjp4OuQq1mAnHoI+KmpZQRJudiC5DG/7ykJuj'
        b'ul4dmQBFuJun6QZDPC6a8Nfy6csdiduENFSYmLSGVVqpjdrsneQb1lJECIWDQB7kMX+bfAtbaFiAxV+U6UUyXsqgTUAV3qiFFrsxYJfC6wC0+qqpvFGIgJLFtFhtdJyj'
        b'e1ogqqPbGtnTLkELA9NkpE6isNjFKMdHjofOXTBZAQX/0LT9n3gLDxNhBzc6ulue+Du7pY2BhKaSoaKmAT+KN1KH+zKiQqRYHQaMJHQhIqceDQimp/YO0OZJ+DDixm1E'
        b'xVWxQNy1xcxdm35nTMOHsWQt2nyC4YCAKbkp3hmWuPWmODwsMeymTlREYkhidGJMxN8VOUUJI0iZxuSH0cB2Teox+dvb9Tfjhm7X9My9Hp1Emfft11qofS03yldsgiqj'
        b'tghDJDTSoAHBj4i91ILMR4oGAgAIfz8AgKbg+wN94M2bHDv5QI42VtYISJscH06xwfxsDN0idMgHjkYLvx4QKclE07rzxq3Qz0O/DPUJ+ypCN/KDGJ4b03rsjmin7p4h'
        b'MUFEjzTv39QnIzScz+z+Dp9tTRg5MPZiNlJ0zB4uegn3Dyj5eNXfHtBzRvcPaLIPalT4T1xPCDZsTLnJSyRBs9HF//qAPjRyi+iBARX5RX9dt1xMw/kfbFjLBismcnO4'
        b'Z5g2Ha7xp7+8J4rM/vEvDpfynw3X9gST+4drxJ8N14jhw0U+Xvu3h6tp2HARl3solsB5ez9Ujo49ZMRQlSQUCqDx0WNGqj9KRo0/Ko4U/5NpSEbswfwLun5M6G5zNoTC'
        b'pVgkHxTIUZ43FVXvaI0T9onNA2U7P0z914LRy+jNn/cKoSd48ldozHwvA3YUHL2AD/4RS9/czrAFn++bzVHvgM2oH10JhHMcZzGKQxkcVM6xpm9vNNOarsfjLcsqVG+U'
        b'mR9HDdn2Zqg30BGdsPf0EnGSKdJ1Ar/ILTp83I+8Mgk/Ngg2tHze3QBcjDI+LI0f95Hg+U7ax1Yvr2y9En6o2GBpT+s7DvrLF/7o+3HNbwdeyLCz6Nc9Ypebe3j0+Nk+'
        b'Hiecnt5l/ertfss5JvOKCz5teWbZm6OTLjT+MPl2b7LlmMyz11++9U3BG9EVIllF6m8/LngvPtit5qRlvVAr12bO1BfmuSR42jvaEguHFE4JjnBSvVujfjjkTs6W2HYM'
        b'1Qeo3IPK/BmEM4eHNmodIXmCeW4ZytFGOVgCQVeMmWTUhhr8Bs7WUqCOJoVOXksLl8M5dHSaJzR7U6hsFk+CcVvjhb2dfduUFEBOyRJQtaOd5pQsENWzhydQrqm9J2qB'
        b'fppVWzyTBNRtT6bHfevhArX5ZEOJ1ZDzNx/+gXmJZ9DD9q/B2apHFted4ZEhZEukk3X+35msscS3z4Ac7tAdnOzexnyC6ZAJTFj5pvg+lNIDzRQSRpFvtmjaRYtY/7en'
        b'cb3x0GlMfbFK0DnUx7YpTy+8nXoScsqncuNRhhjVQUn0Ayukjvq3ctR9+byKRcV6xVqRQriQy9ODHWEw2E6kdrgoXJyhnc4HiyMk4ZJwaQYXrhWunSsES/G1Dr3Wpdda'
        b'+FpGr/XotTa+1qfXBvRaB18b0msjeq2Lr0fQa2N6LcPXI+m1Cb3Ww9em9HoUvdbH12b02pxeG+Dr0fTagl4b4usx9HosvTYiOcdwryzDx2VoB4+IkERyESPSuTw+eAR+'
        b'Qg6xdPACNj7cCj81Dp9ANxbrm1q+YbHETfBnx2HZY0jqKasd7BHLqzU8uwwWH8la/cC6OXC0tZBTRzOizm+UvGTf0xlYQcV/uoKq8xf9nP5vkxcNa+lg8qJHpQoi84Nl'
        b'KyJ/kaREYayIgKXLrCKjYx6S92gYZxGu1n5gFR/nl0Q2R0gLwRqFpzqvib8jTS8C/eik8wpPvIhkOjjx3HJea6bnborFwkzd7iHbGR+In6xWA7CCtMmpAkkfTBPHLkZt'
        b'Em6LlbYeyg9SB8lJxhq8OnGsDuolwWigypP5f7TbQYU6NSzJCxuM+khqWFSGapifwUkoRn323r4sjrg9z42MhwYbESrzW0sX/3VwZJ5imrfA8agCTqPzHOqevomaLeOU'
        b'7uqEx/zYzfzUuAm0MeaeexQsxnz7LlyhLE5ApdAooY3ZtMCDrrYEi6vyIRHotS1RlWhxINTQ5754Hy5XwDlP3BovElN6ORyaKFoLR3Fj6ZKuCrNQHw3SHLeVW6Eb90UF'
        b'3WqTOMo2VXj52uEXSALOJnQMSBLOeDfaMmN0HLJYNCTeSR0Pqd7Dn5XcMFk8kHQbD0s+jZcAx6GZWm6X+W5Sh5xChd6beOe9iOX4sYYj6MpADnV0bCqNKlU7i5H2FJyF'
        b'iwPBoepQnzpAlOn4kfRoK36TmNNOXKNFotYcjpzLAk2ZoirURgJNrXebwE0wRk10X24ywgql9mM8fjWmfelGcsjGQl6PQjn3h4DaeQAOS2aPhtP0yy8nCpw4xgxLGqEO'
        b'psvFLHxcKsqHvIGM6KhuL4lKhSrH0FGYByddhsWkQl0OJCbVONTGnEVq0RmjgZhUqC+A5Hd3hxLqcWKZNGNI2KhZWoOBnVjUKMynjDhdBBhEOIVqGHi8DJYJ6LRoozVq'
        b'iH5mnJ+IZi5ti8vaX9i3ErkYeaR8mvvprG+7JVcLDE/X1J+NP1ut7Wri592zf+7jJt58kf+FMf1Fry+bG5k2vXlvSnJS0twfP7m4JrfpxKY3Qz9sqOrq704fdeWb7xo8'
        b'mk/fe3vJ5rbHo+5mvan/xgehqXutmhe/eNBX718tX/1UPGP01mOWt1a/vcksccoc03fNznl89vvc40m27umf//Ky4dkXz47PGvP0NzeOPJ+VeMTyjc+/y3i9z3L2Pp91'
        b'7+7dufWpKa9lHdR68rOgd3JCSp52ulnAu898ye9rcHJfZZ/f1rfnyTmz/ftqymeb/t/aF9ad83D86JO3HC3f7ykrtv8926ywJ7Zm1Er9q5P143T6vj7lvkY6Z2lk0dtu'
        b'i9dpfzojsPBsUdN7JYUlK1fNLPco9JiqmqTqt5W9kbriFUPvXk+vq7Yqz5/ipr2Z+9riL20iRiSXFvbLU3reOXnnasnxa2B5N2Q+92NaibFNsdyCnhW5rUAZdEnCC/SW'
        b'yVT8yJ/Lzj/SVlsofOycPB1SU8ljWYyAaiA7kgo9U1ZMp0h5dtyvDZdQC1IJ+/ejqxSIEQt1RkPSeSwI0CTzwC9eYGmbz6I8/iHn9+gKdFKEG2qCs1QMkqMMvGyoUD5d'
        b'1LDGTIXfq+gcw47kLEFnSLITuqxZoEtkoVEK6BTqQh3U2rgTpUUwa6MHdCXziyZuYcj7PSKas4Mtdh4oz54grirFc7zgCDuQykBpy0HlTxY8kiH7aAy/GtK0mCW2GmXg'
        b'GU0ijOJFTxSGKlEVD8eM1tCnzk5JmuwaZGFDF222imahPCiliH5Ij1JQY9OQxc8YKlHbTBFUW+xnieJLUC404EIGF0BjKNHaK4JuVLOKjoDREhdaP1kBXVE36fYK3O31'
        b'6CTtnhsUoSySv4AsgegkKsfElU3G00oHsYQtu12geDBSwnFiCsgTHI2gjH4eHOQ0ED+VRpUwhPNQpSNKnIolV3pSlTldSt+g60Z4jFRbGA350xLVhxrF0EMGZXDlMI7F'
        b'Ta0lnlCVcI5WATkb8N5EoF944l/Y7EjM5CoBdaOzKIcy4A6eJnXXxKwzgJP+S0TL4kQ0sYAVFsX/H3PvAZflefWPP4O9lwKKghtkiKAoIIiiyAYZIi7mw5I9HOBgyJC9'
        b'NyhDZIhskCXJOR1p3jS/zjRNm7ZJ0zRputP2TdOR37nu+3kQFDPs+/5///CJ4vPc9zXP+J5xncvc11J2PfnKynEX9pOIcclS1MZJCdeTrRtzsWDV8m3rGpiHpbFiB5je'
        b'w1e6mIUla37LZCJIZxd0HBTDgsEVnswWvCwZrFzGlrQfDw5oiKFPhA1m8s93Hym/6HGH5XL+jxiu+LJI/aZARYUrjcCf+FES8r43du6Gu9aZ+2ElCdgpHBWRiJC8glDh'
        b'XwqKetwZHBWu0P/y5/zPpwpKWlxA+Ku+oyLM1pLix6dr+UtP8GitNvmVvrR7UsS/arVquVK/siVRa7TyzM4zg/3yZbzXf1599G/TuPiC/cs9LNfq38rVyJfi0yc141+s'
        b'OL+0GLZiWEZ8bPLnlMv/jmxAfPeycvnsrYjMrPQXL8MtFxZpE/ncbr+/3K2pW2JErEl8jEl8Jn8P51Gbo8ur8EKdp18QfM4OvLHcsxFX7jpdEh2fmZL+wpcSpP/68/b7'
        b'x8u9bZb2xt9C8GKzk1b2Vg5LSomOj4n/nG396XK/u7jS9BEZmSb8S1H/yQBiZQOQXJFEZX3eNQw/Xx7A9uUB8C+9eO9xMprmjqM9v+93l/veLSOuzBWsRVTGN/DCBd8V'
        b'w6IlkUQ0zx3Br5ZHYMxxFff0f1xPXzlMRq3P7fiD5Y63rKLuF+46Rta1zGX03K4/Wu56x0qjma28zGJe3f2K3jn19nQei3A5j0VQIigQXBdmq1wTLPsAhJwPQHBD+Lw8'
        b'Ftbks75vpc/Jn/mKtdLF3M7IfXp6zTt4Ocq7HCfhLirOjGM3QT+hv3QJf9cCd1Fwckrms66EZ9wJsk16xpXv8oMRIVcF/6f71j+pgZ/xiFXB/5u+mZADLdfksBiGVVbA'
        b'XBnG3QvVzynSfl12tJi79ebLw46bAsVsY5l2W57pk7yYmFhJpu/zq7uzbv/A1Dc7Eful1XeuoG5llfcsdqwyirBnDU5IsR42PPFnYM1RzH2qFpEXZxnAooIqLJ6J+h+P'
        b'zXzJPCva0B/ZviPmYjO/nFRisZmEmN+Gl8dysRlvsWDrtNjE8V7yn6Ubewk73WS7qg0TKzb2LEx8Uegm/eYLb7Hq529xhiST7yZP+FTqVb5wZed/e4GNLl8VunESsCwH'
        b'c6h6zkbruT69z2QrsH3erUofz+MdM75ys18W3N2ID3gqkNMUsnCsCX9ZbgqMZGML/56crRAmMqEy3mr8DyJOUskf/dnFWPco7wjviIR3+iVxsXGx3lGeEb4Rwj8bXDRI'
        b'KP3IIPD0r63lbVP7hILRNqUf9qY8k4+2dm5aukRKIXxVrq+yO2I1RQ1RtvYzO8Q3fuvpPVnd5e9fYE/qV2afrdHx84UuFzbji9kLlsNmX0b0xpHo9XlGbrqypLsMXuWT'
        b'oF3t880wyciMT0w0uRSRGB/9Be5boWAt9aHgG8RH1X66LkegRM9oXdyV1Gy23Sz+Zb/fy2eE0TcRPxz66OWT4a9Hmr7vGaEW8wH9ZqEjrvU+HmDmHe6cMba+Otrse/l/'
        b'DlXxdhlMMHRoTjBwMGhrKT2UYLB+1CpaUGptEX72FX80ebn6653Q/u0APcXviW2abMWC731gcERsYabEGbLZWAtL5mSE3jq4bIdqwLT4hBX0SMs9tmK11MV7Huc5z2iL'
        b'KAc6TnEWtb+SldRnemIz+45zmS4inyqTBQ9wjmOi4+Yy/y9z/uIAf/vjITeoYQ7Z/dAm88luE5+2wyneWzLsC82cdb0DG6WXKVRDPp8s8xAGYNzcFe8RR3qwezQVEkVb'
        b'cU56ZSiUYJexF31uoQB1igI5IyGM74AWqW76wtiWUnxGGLe3HNcc+6pco8sXCeT+Z6nQXB0MuRXGoKz5FdrrOWN6os720KP/eAGOKtZZ0x5dHoKZ7lrFI1ZUieBCa9Fs'
        b'WcTMEuOKBjNx8paSzHp4S0kG499S4BHxWwo8VH1LSYYc31JaBn4S2XR4+fWf33y4Qu7o068X2SqxASuJ5MRqQqOz/1t1GzRU1UT8Ybh+TZnewBGo4RxCKlApgnmNnc/o'
        b'ah3p3xn5T0cJFeoN6gXRogoWO1MsVi/WKdaNkf/y0UH+LQITqtFqt5RYdDBGIFHi4nFKrO1o9Qohl1yuSu3KRWtEa3LtKi9/J0+QVStam/tUhRuNQbROhSh6O/eODveW'
        b'XvS6W8r0vSp9L2BP1CvSj0H0+gqF6B1c/Ql56SUi6sUaxVrF2sW6xQYxatGG0Ru499T4dulHqV6ZxrqxQhy9k4uIynMhO3YZjkaxJuutWK94XfH6Yn16XyvaKHoT9766'
        b'9H3u7XrF6M30/i6uT/amJvfWenpDmYs7sjc0uPltYfOjGYiit0Zv42aoGa3LSX/TtzSkTEF/RcRK0t/ZRxuzSqgfMVn9BNME9HeGSQQpgZWqgQUIIzJNItKZ4yUtK56I'
        b'f1VDMQTTueej6auoTGbQxWeaZKZHJGdERDGLNuOpOKJHJqmalHRpV8u9RGQs20Kko5JNIkxi4y9JkqXNpqRffaoZKyuTyxHp7JowB4dnA5XMzHpqgssq7ujxoCNWJsdS'
        b'kndlmmRlSLgZpKanRGdxw92yOkQrdaHF0/o9c8phdaGS5SIlbOuXC5WIS8Sfe75BzLkO5N458/QGcUv1VJhWpq2TZFN6oUjt8ooyG4y2deU2rGlssb3ntizaysSD80ZF'
        b'p9CIyDgzkVyJz8hkn1xmKxspdeNI1kAQ0gFJrW1+TM/Y4Jfj2SDpm5gsai4iOprI5DljSo6m/00iUlNT4pOpw5Xeqi+AL2wbnz09ou7LnQyAViyEuytrhrov+7uxFiu8'
        b'ufKeATiD4+7evrIaYbCExarsDhKs4oLSO02i124iwF3mqL9EVmcJ5Clf34Z3+CuBbkOhJdYxd33xJXc5gfwuITZbmnJFN7KP4GNzRcGFk+y86w5c5GOZA9BiFWiJfTiO'
        b'92wEYisBLkKR5iHRduiAGf6qmQal87IrrCDvEn8AhUXW/QMsT4kEB8zkoUZNhQujukB1qrlI4BghyBBkQAu0clgO0tihlj+KFQXhagNG5wVcWVWoIPMgTxqKdIhi08IS'
        b'7n6sCgus9OFLq51MUcRcfBTMF2NpuBybkSbPzJE9N1ipt2G8Hb/zp/vEGd+gb/+e5H68iuVDqRXdvO/TdehVr0G5dzcknhNV51bsCKxx6S7/UKQWk2e+/UfvWLcLd6kW'
        b'WH5249q04brfvOtZ9PvMbW73fjNrui74zA4rye8+HIh6ENr2tSGFk5KugDD7rGEt7YNj1h+eX/yvIovZ6e+C623/n0TkrXvjzV9OVnx/tuHav2rPg5n23zoaa76jAxY6'
        b'Dpsfmr/xsfXvzDb89b7cePA33/uz9tHX924e+WH7pk/Xv6uqceOlrw1u6Fz6nmN61Pf/9Oee93YpbHyvyvi//+twxr5XzPT4ItYdCtgpDfNHugQI92LuXi6ipUQUMS0N'
        b'95HddVcay+MCfidgWJrpBDN7+Yg71msth9w38KcTSw0PyoKQB8ywRggPcdacj0IuYl8WH4bctnM5DGmtwgFLO+yGWb52Pp8eBXc2CWFMByc5YGl9ENq8+MQKMwWBsp6Z'
        b'lQi6tLw4KO24EzuwjECAL9vq3QoCaMnWgEnxyXAo5F7eq4Vt5nuw1AKb0wghKEC/yOISNnH2dwKL7K+Mf2IZlGK16DoOwQAXVk2EnhuEpWmp5LbgXUchdFyTXnOPi1Y2'
        b'3C0DkRJZVnmiPBc2O4ylF6QRObxNYLyVu6jAUkGgD9Ny7gnQzC9IXqY+B/4vwyJbDwVdkTrWwS0+8vYIWp1YiT4vVgOPH5w2NEGFvpgwzwjwZfLwDnFWPgutLbM5jmtp'
        b'BIp90gixMy5PgVwaQBl3iJVVHefOCkHlHnbWs5K/8OcEjNFHdxShSpM/W3AAWvcs503g41M4z9ImRk5xyx0fh+18ncObOdLznVyZQ2jHSq7CH3SFsJqBe2hEcNsPehyl'
        b'55ME66mxJayCyWfTyb5M/vZaEbUgJiu/io1gz3LMFbhMdQ0u61yNuzSbZatv5iwGPuqVrb9aMT/nAutltbsi8vU5EUQx/+wa8a6NqjQZBzaZL29h5Ap+vfIM5HOH/FX8'
        b'xPKf7yM+pCr1ET/T2XIUzHZZjz+ruFco6f8gLJae+XkRm8OyIabvZmlrK3XqKif1Ph4OMRgk/gpu6meSff8/cVPHkJl6TfjUdGTr9IwD0qj8W7xH+bN/WDKP8kIn73pU'
        b'KhFOPfyjmZCT9DcvrVvmURmDGuMEz6NNWl/gU06/wS7+3PkUEWREJYZxpya/krPY9YVof2mVu5gRkNcxktxSJ6IjDnrgFPvd288Sa81XzhMb1/QcG2zWcIL2iC9IEOf8'
        b'XMXCr5Qg/kyNPxndPH1Og3OGwuOLW1fJa6iCPho2yxu87b3b0wIGg/gUQvaBnzdz38AQ3Fa1x8LI+IGuEGEGdzf0VNpH4VY6vwl/LdJ0/e4I74jEmMTI34Z/EJ4c89vw'
        b'0lhP5o7OL/dWFDSqKuk4l5mJuSK+CRk2pACLL3yBuiBVkQE1nJ5KhBroV71w5jnVra30uDNlrjiJA6voTdlhWSUcgAVZKsHni32Zuzs998tS32o/9jOe9NXObJ8XIsQp'
        b'nacJURsLHGSEiHlZX4EQORe1wVENDxi6KL1+zxZr/b28cOrqsl+bS5xk7O1sjb1e5vg4edmxDb0u8QFvVIs46Ta+2/Rpx3ZirGeUb8SJCubcNrxokLDs2hYLvm6uHB6q'
        b'/qxr+3OiDwXCF/Vvh6ipaMllGzxvA1e4ub+g+6MvtGUvrYxAPH8YJP4Y2z5fIjC3HcvFJokgTzJBflkmiL8w5ZnM6U/7njEBT0gyyfaVasiVDo7nG89J6ZIY3lB9JvVk'
        b'Dfs2XZKZlZ6c4WByZPlCcOnsw01SIhPI5P4Cu3RtdSfvm8UoDvOdoISD4sx9HOzvqx5ieSrkSYL0iuRoyN2nnAD9mM/nR5divpnXUzYsb6pVRC1bawGqilgB89gS//Kr'
        b'QnGGH2OBqVMfhf82/Dfh34qMixmUMGf96ZdO42j12Ol7t8zkTbd94zuvvfm1N1/2F/deJIKfaM5LCB1vnmgpa/c8velPgc0u4/vLX1Zr/1BQZ6F95dyvzPj7w7TIFJlY'
        b'tmKEW7AAHh4ntM7dFRVAg11lL4SxdEkc2cWl+7mRPVmkehwrn6RMyuwnLEvljK894ihmemEPtjDzS7g3h0Qpl4o4FCbx8j7wBMqrnhHhQ5xP4wr5491wnGBpltAAt9YS'
        b'tTAcsIpznw9EV9ZPYMdJpJTD8bLDV+XlVD4fTYkrHpK94SlmWtE8DwMGpPlinHv7CWpeU/QPiPjHnmBlJ2oi6IV4/qHeSp7/nGE+n92fyWv4IuUvC3NNrcnomc9mlqTE'
        b'yA4p/O/z/RG+zy/J92uH0whs/nnHuCCDAUqfmpSPws+99J2Xifkag7/fVbSlbG9znu0mwR6Qy6l8bCbiYGd4kj93tmdFCucG7IAJCzkWEVvkzM+DZFg/Sfgn1HCT1bfr'
        b'uiQLI60d+tz+wtropoDlN65FEtJ9kQJYZ5EMwB4Wrew1+oUIslPjiwhS2rsZzwVvKWZEXJKERWT4Pt/HywYhVUcKnGmj8BU9vJFreXhlxMpc39HSOuhfilSPLLvpJZkR'
        b'LGksgk+eSUq5RPqNVS6Xtfs/Ref8O9KFcmCOYM5Bb8G8v0lZGZnM+8vzXUZmfDKfSseM1TXdt7wBuyoBivnnqfG1XMfLLMbGmh5xmV8umvMXcBYj42c9vSq+Wewa9wsm'
        b'Rrw+hYZMTqV+gUK9DdWcL1bZ9aY5O93jnpYhwIZ9OVxRkhvtr/G1TOQEci1uSsJMZwfOf3rVU05wxZIQpUu4WuY+b0EQZz/zZYoHdQzN/aihALmzAmzFIuyOdy4dF2aU'
        b'0ZdW3zXzec1S4+gRLfEvfH/9LzlXf61DIb8wyRXktd96z8Pl9Q1223/5x/6328bvWq9L+lT+aPed6hYth66SnleTMu57vKITulkn08A27OPt73xiddxcp+rNyGIn39TG'
        b'138w96qtbt1c488+3e2RZFow8/U/vrfh59/4cC7hDx88/ENcfFSg/uGszFPa/5xXfM3K2CVsBxz4mezgaMteP05vm8M96RFMvLed09sm2GW/Wm+LcER0fYf0XpCLSjCk'
        b'+rTOTsdFUtukabnGTVWgnTkCTaCY+QKF0AGNUMVf9aqbbb5bloGv7HiVXdx9B+5b8XevDsMt+WVv4ApPoAI2yrlnHOV0fzBW2cjcn4HYJCvQVrCT92DaH+EdmIvnZA5M'
        b'GIGmtbWmmcKX9aO9pSg9TMrJTfevLje1ZNUbdERaXAUHJS76rifMXr+GPKOOVrvPOOV+RPTFQIDMgCfPPkEDrvTPlBcSvnXrVwrf5wyWFpLz13HSV3k5pZoPpFuzULxc'
        b'YkRybJBblOIKfmZT0ZHxcwATyOxQJPM0qXCxUhafFRVrFmsVi4u1peE4nRgdqaBWLFEmQa1EglpxWVArcYJa8YbSE2/QOzfk1hDUR6KjWQZ2suTy6sQZFofiY158iC4q'
        b'JT1dkpGakhwdnxz7OechSXw6RGRmpjuEL9tE4ZwIZAohxSQ8PCg9SxIebiHN/b4kSefyErhg7DONRTw3+GoSFZHMBHN6CstlkCWdZkak0z6YREYkX3y+dlgVqXsKTK0Z'
        b'p3uuzvg8PcMWggUSM1IlUdwMLfhVXlNrPMn8T85KipSkf+mo4zKB8cN4ksJ/mWRe3Cr1xc0oOSJJsuYIUvh8adk6xKUkRhNRr1CGT2VTJ0WkX3wqYL68aRkm/AEEKxM/'
        b'lgl7OT6DHwFp9LiUaBOHmKzkKCIPekaGn8PXbEg2+qiIxETa40hJTIpUty6fPeaJIIsldrNod8Sa7aykoeeu5HLamoPJ06cTnmTuyvp9XgavtK1Im8hnW1l5xuEL3mcS'
        b'goBIoJ+Jna295V7u31kkZYgJoyWyrZK1RaTPU8naCcXHJDERWYmZGTIWWW5rzR3flWHC/ZNlJTwzuFVoRUqZbCqpZBvQb18Ca60CMZpSgbcaxOzy5fxUNrgAtRk26SIr'
        b'mBUIUwQwg23KfDh5ATqxVPVSmhBaME8gxBIBtu8yNBPyVy00njnIHGbCTZYCEVQKXbELejlHA/RjA5TTe6pYe5IHQqZWlqZYsme3hw9hosGgVBzPPMUHkKF+t/JBjb1Z'
        b'TG9gq5gM9JVRbw+swRrO1ngS9o66oARd2KjIoaOf32AFs8O91f3D1b6/a5Mgy5S1UxNziCEJc1nFRC5RzwZ7vCzMLD3lBU7mCth6BBu5wPJNXIS75lirIBBq49JWAXQG'
        b'ruOadtnAStMdPCQ2CU80uBnLl/YICGF17axT5V3CvfcLdvAf/tqIhbhNTosF4YlNG1MEHMgTWUVjj0iQgKOs3J3InavzxD2eZqcs0BL0b1cJD1fbb6ssyGIKEtvPx3Ln'
        b'ybH2QKA75+H1oNGXmzMouTwT+sLdwtPbysNyt4IAy8zU0sQpHBQ9vkmIZTdgZNm7w0PRcjOCRDAQ5L4cnSVbbVYZerAq1M1MiTtb7LA5c0U4EaYPs3BiPTzkVgceQk8E'
        b'dw470UQguiDcg8UHOOIwhPLry6ewN+dsYWVnJ6GCO9ntnCXvhYMwuOJYIzuCvRdH+cPM3fjAcPkkNMEmXBTCXHgyf3j+1qH1K09CG+CcJjsJnY693MueHti5fBB6L9z3'
        b'E0EzNkJPFvPC7IMSa/4oNOQdWHlUcfksdL+Lmaq0ViLWbJId4HeGO55CGMJCeMCfaq8+zm4qWD7Bjy0mJqIcbMAKfowTUJa86vz+rgg3MbbZQSfHGjug5yY7v68DFcQ1'
        b'7Pg+5h7i6z3OwMARLrSPBZDL+ZewypcbUAwMQp+XfLLsOCt3ih8H5fhEja4EeLz6HD8s+Guwg/xYkMaN2VJitOIYP+3bCEsbhWkaEzfmMezD3BUn+WFmH0yKchKwnXs9'
        b'FUuVVx4Nx7s5Guxs+DlnrnIhlOxyWmn1Y70Cmf2mtCkcsh/EBYvAJHtL7Asg9CyWCB1xIZN/cdLgbOBFIVlE1cH+9J2CpZCkyi2Y4I7jtx1k7PSJuapLuEXTli0CjrQ8'
        b'k3Ce5lrnJwcdWC0QqQlwKRD6zVS4OlmSEJzI0EjPwjE1HNOEUpzJpA1IEIcbepxMzGJHVvE2bRV7hERZ4ZPHMnAyi/kz+sTYAeXYxdclGsa7UL6yvcuZaZZYo5yurqEg'
        b'MBXLYT4WeHMVbFmZgQc4kYWTGWlqaVChmZ4lFugaiXHO/YAWPOLyWrAMeuB+RlqWCteWJk4p08JPZqlFOtIbsjEcvqAgHwYlXB2rkPNYvPy87AFdiRjvwfQRmMc6afky'
        b'PWhefoyGyI9vMzxUghK5nRExPJVMXt28oq3MdJykER4Xb452wJYQbhLb3bFb+gjWQjO1RaJYQaClIMKHMOzCX6AyjOPBqjidScNRU1YnNK9+Q89XBBMaNtz+nMBJn0Bf'
        b'fctT/v5sR+VxVgg1m524IUTBNDYG+mBNIFZgQyBUyAkwz0WJXQ85fcqLv2jhPj6AoqfaX4c11IEm1HH0JMqEogyc1qSvRES2U0eFux1hMWsvM3wvncCyhESSjV57fLz9'
        b'gpkWCZBa2xZMSpZ7eGMpKz6UH6ycgflZHEdiDRQd8mIlxIUOREoCrL8IMxw52Zl64YQ7yQwvS2ItXzmBNrTT2t8XQ+PJQE5c/+LCRsE+gYGbvFa4UcL+OF6GQ465IEgw'
        b'ekNJK1z07+zjAv52B8Enh6W/mLqYyfE2eh+MmcEQ8xA7Cq4KrqrgIJcspW+lDkNyAm9sFWQLsqFSnn+6HDuw0lxREEOEzy4mWIjm7ilyx0msRzLrDXcJ4gXxUOAUv9N8'
        b'uzAjkeycKyKLpADH5J+4aHWcD3g3rPtm7YdLid/8+wG3782+oq2zy8XopV+9pGTqomUa8vL4mFb4+Te/KzxXbX+s1CT2lZMBvZ4tM14OwSoaP38tx9HR0XbuTmDaA4lV'
        b'+OK5Db0dkWVfzyze4Xgg/dK1D0cvvituLTMXvvf6hS1vjF14dZ9Gacam32RaPXLse9eoPXbWoD3sn989+t8fa/wj4++SM7Xdg2cDf/XOxxd3F2o0/MLE9fcBv9nxu5/n'
        b'GGlEDLl860zzm7ftDdODVCP8v5a2zvxk2Rt+CTq9dYOKPx351rGff98r2/V+plu7gWXxT/9hYZv6o7HKrBPfzNh7aX33B13vPh5+VHblsN+vxzMza+//sDY9Qfh1VdOA'
        b'TTObUockQb8/2pbvGJw8lf+jB29Man3/svfc/U3Rof+lGK6VZKG758cffOdMxO/mplqmNr6RfGZe8ju7PT//+wf//R3f40ctuxr8PT/YHjT+3T++ej7oUmu5ZMa+7NUb'
        b'f0ooCP7voxpK3tHX9Rf/dmV49uzVQ6+88keFDq1939t9zTT1zp8/+9PjX7U1ZSV9trgh0C7Y4r2/ZJ19Z07yzzM/DdGw+vWWXQs39BuF2TvLzr7+nYZNP8vdPTUr/tmx'
        b'5NZAwwTF0tJvz44sBLs55H4WqPjDZJ8f5WlY/XdQ/XffdP3LgffHhwtirOpcM7Z9atRs9pnftx1/NDwyFiV5EDlR/P6dKit/HBZoDF1ftyfzY6s/pAXMS7rhn4K2Q/BZ'
        b'9QnXd687/wLbNKatHmzuv9XzWvLGhW2bZj6IsC17I6fXQeHHFdmJdoO/Df3nsb+Onn/9t9/c9ckPA3/ZMtxhNJv590Qjq/Z3502O/O5bOX+dMf/URfdqjM3hAz9+6Zsp'
        b'Zp98om9q/k8nK38zKy6xSckfasxXZyfoeERvEsNdK2jJZIScFQzVHGxwceVhw5Qx52HG+3ZyXrK4tR9X30Ubi7HJSAzlMHiZ8/ZomeFDqbfnIsyvCtK0YiF/Se8MgY0O'
        b'r7iTMlDIZblFYQMX9Y6AJRx5NjtLDwrE3KV77bJS/ZU6styxaAHzGN3Dej73K3+TkjlhoGKWPybLHtOiqbEMKiw8TuBsOX9sBsdX5Y+RXuZroTX5bYMhwtCtq+qV7cB7'
        b'XHqa4iacMff1wQoFgdy+vcZCGEjAZs6dZI8LJ83D4BFzKcn8SaogvQogF6tDVybinTsmhLGr5/liqNhp52VsRbBwucQq3Hbl2sxZz4rK5oaZw0MaKmnhq6LteCeCO4+y'
        b'F4vXc3Vdn5SbJTH0UHQj255rdpMaDC+H22DajZUu6cnii9V2QUX8ysw/WotCEXR5QB5/4qQaerGZVS/fowhFSWQndAuDLS5y37mRHujlYwxycnAXpoRwJwMq+fS6Xu5O'
        b'IAuCgPQqlvpYkIrfg+XQJSYQ1o2LHBEcwTEnr6vPROTKLfgsyqWNxziktQHu8kCr7gj3WirM4tIKxIvTroR4seYCv23zMI5DT5BtIg4yxd8OXfwFzyUwqedlxaqqrMK2'
        b'2fiY29aLWoefIFtH7CNge8qSe9PgJkytBLZYqscB23Mwyb3pfA0XnwBbFzvCta4e3G3AttB6iEe1eqfXArVxwDPFtl3AQWM+/CgvyAnQxFxxynUfbr2TFVhS8kkTQnB+'
        b'rHDfDdFuqIXBTA4FjV8LXYls0tglTVPqOCq0gXyhBXbLK8MDM76aSBsZd1Ney9tCPBkJ+SIohbl0bu+whdhHWsMPbu/xgGFToWCjG2HsReKwx9DINbMOBmCOKxO4n5hG'
        b'oIhdBJ0qRUrEgrOZzF41vWnO9GNyNFOPV8/wNyfPQtMWaTESxnu0irrbWE0RMVaq+HG9bz4JTfwTVj5YShCd+sZmOewndN1OI5/kGkrTSeMe8rMg2s0lxU/7IhLo75c7'
        b'TORVxHH5bmc37hEi3odrlau085NWNLGDBi+cDmEDKuU3RRUqRNjljjwP4JizJjUyAO0WvvQQrbyvyMgxlHvbFYrJ6liZHXttF5ccS5xYwa3T+hNHcYLskgrNS1JBqIwD'
        b'Ihp1Pm0da97Rypj2wtLMlJFNrOo5EYwTfxabaf7nB4ieOHj/F+9tXhntjoiOXhXt/jNDUl/N522nxt2brMBdiyGrf8xnj7IqxwZCHZHGcn6pkkgkXM9uWJbmldJvIgXh'
        b'qp9P5FTlhKt+PpH7rYKxEtcef5EH76xWov/VuCowcuzW5r8pqCkIWUVlLW4sGkINkY5Qg/O/8xd8bOBqumhwOa4aQhE3Tg2uhswz0cYVyyL10CvzbvZl/3f6MeZ6X/Z8'
        b'px9f7bX/z6paK/L9PGmY65HrzGq5b87j70G/lapKT7N8JY9/ruATq88LuK5YAjPxW0qyOOeTY3hRcoIn/ykIVvi7WBIy58jnHf3KUke/kHP1M0e/qFi7WKdYXKwboyt1'
        b'88uVKBQIrstnq7AorNTNL8+5+eVuyD+pTfBOoGgNN39wqjSbdrWXn/N3R0j9tcuB2uf7zmVPrD56kyl1Pa9owkLqgY6KSF7TLRnJIgwm3L04zIX4/HjCi7jaWfBizV53'
        b'y4a324Q7XsN5RWXj4H3c/JBYwIKGnsz7ldd2c5u4pkRLbO1NIiPSOb8sP+F0SWq6JEPCtf3VAtDcAkqjEk+X5FkrnEDNr11CQuqslrnqmXf8i7y5X9V3u/ZFNca+nNOQ'
        b'oEoDNnk9uRb75HNC0NCF5SwMXWmmjCMEWvs4pyGB03JWT26Ff5H5DrHEL5B3mUr9pdlwxxrvK0PF0UTeKTh24wAXwI7GAXdW02wA+bM+38zh7wq0VrA+eWynFn/HyKD6'
        b'Zv6OEdEp4bUTglyXrOP06Q3IMzOHfhZzLcGqQObk9PHmVGzIM6m0Kwx7aE8krS8OVsc+sqo523gf9pExMWCGE0LuGmWTnfwh8qZj/xBo7T4lFliHSwyER4N5y/zNFpcg'
        b'7uvP4s4KfmoRJCcIz024otAex3/t1u3CfdureVH4A5FAa9TpkpGPgj9fwhnaoFwOuqHeVo67ehvqsTuLHRA4COOnVvqtsYQ5cuuYu5ZQoofUCc5d2uN10t3TwpOATyTW'
        b'MhQ4g1Xqnhujslj+NcHlXOxheGBMvNqP+7yUAjeolZalJEwAEyvqx8uqx89vwPxAY84Vl+SLjVKnpgCnZGfWs3GR63wX1niwayFuQcfaPmTTZX8o5MFj5etwC/lyl0XO'
        b'3LVFAuuYk7YHTBSlvhCXBH4lXT1OCSat0xQELrnZBqZG29MVmb5gznAzeX7/CPyPBmQwHwlzkBzDev5C6DYcssHqQIYCGQaMwQfZGgZR4vMu5orcpY1px/mDYQ8IVraq'
        b'GDLvCPON4DTUcw7VvZtZLiDDwlhGRpadcNtOGMGmbZyPKxyndJbdndgQwYphMnfnfnzAu4eb5dnJI5kVIIR6E+i2w7vxDaO/FGV0EqVt3PaJU7VThu4RtaJ7by9WLX78'
        b'I/smLd2EwUlrvfqgzO3HA6L79+n9zbs0wzMJT75y/KXjKq8uLkHVL+73Vv7NujNpMtvYY2T7XzdsLd2YmvPvcPce2w/+5Og5cd1851vCS9/+V4BnfPSP235f4N37YdqP'
        b'yg2HWv7P9441mf6r6p/fyAqbqjOcD3rXfSAsSVDUXPN6V2KU6GcvOX4iCklVLc/56WP9nzo7vVdfFWxQ9p6pgd1Y77vfMQib/NvlnW/+ol/N8OyfHX49ovfb/sgc4fDc'
        b'qW8rek39pnLn4OGh5PhXf3/3bKtp3V8Sq87fe3uq8e0DdTtLQoybbCRZN2IvOb/Xbp41EOQz0dP295p/9Z61clty9v2L6ILNn2zOuqYc3fLL86GL5j82+3HJ4XN2v85P'
        b'OOO84e37ap1eDqF5vp8OB+X0th7cZBJv/E3VrJvR2rHvTvYcqbbXP/e3DW9/pvfBFpOo9u/HZxccvzvhn/b1h4WZbf4ZPiN2ySkOdz/+S9RQ6YXjZuf2vNnr8KuLZ777'
        b'0TeNsiIT39Q86Ob1d+OO/jtl677Tts7IxrKp+IN9vxt8/Z/7PzHeM6DUtE59wGw9f+fe0DHPJ6mip/cQNC50yJT6w1tDpKarN97irFd21fgM8PUurxhBO++EgHm4tSpV'
        b'NNyV90EM4DiLEtyGJbUV1RZGErieo0lAyaxb4QGyH+9sJtOH8zvU3sR8md9BuMGX+G0RZjhLLwdbsV1arPMytjyTRJqD/Nk06HTDdpIGsksRseAYTITjPb7Kei/kacvu'
        b'ReQvRcQqe7EIp7GfezswB4fNV9x7OEoibQHup/JprmXQGs2uW6HvhTtk97icx27uVTvLGHMaj4cFNGEPzU15kwiqsdOFM0U24mKyuSX2Zq2oDN9BLzLxpINF7Ibspyx6'
        b'sZMy2WQz1znL2y9ElRXuhX5vJidTElgZXDvxObyvyFl2x/aH8AZZlQ/JT1IU2Ac95gqCjdAmBx36NHluU8pduOBBObRgH3edpIKRSE4H63lrbTQExp82IMUKl5kzaifn'
        b'n9rjiQMr7cfDkCs1IaEdSrV5E3geem7y9mNAsMVK6/FELLeNWHXKim9k1e1g1ZeltmMWVHCr6WkCVbzxRvuezxlwZL4d0vkPAbvu/6K19pTJprYyt4Cz2QaZ7P9qNttN'
        b'gZUaZzupSK86VJJaSQbcjTT0iZi+EbHftKQXH/J/s3ts2B02rFqmCmdnySw7Lc6uUuNuuGFHkXjLS4X7cz3Xjw73Z/bGp48XrJiP1NhS4M0cz2XTh9kbK6wrrf/p9TWT'
        b'W9GZ1XKPnInlx0wONdm9Al/NxCIjy3qlkfV5c5fldNmwgdiK1jCwGDDlQCk7VMOfsZCWmBdxRpaYmVkxassmldwXmlQsc+rIWimuMpPqSZ355YxVLtH1fzgdm39HVr2F'
        b'f2+NEotWJq58Ugw3lOck+3DZ28zuokc9Av0O2lnvZXZOUkQmS+nIyEyPT4597hD4sjFPElyeLnTHf/9CZ0KUfLNYJrb3xg0rToQ8D2vuh0c83MR7e9z4UuKlJPVql+PN'
        b'WdjFVymCIhzh8FNaBjasCjZD80ZRjuQYF4S8Ab1QtzKaDY/gMSvgzMLZfXLxb51aEGbk0oNdUU6WpWPqYK137A9h7Vqu/0dQslfL6yWB3kMd5S2uH+5rfvdN+Jnetntz'
        b'Odl+HQp/V25RnWzxt+h66+NPIq3Vc6Jz2s4lzDcbHKz6k1G1Reaun2pGLgzoT/1XeUhF5PSer3/vh1Paohhj408nLiZ+PfjB45QFn99Jznxk9cc7i0XGyUe2/d0n3Uye'
        b'0+Vivz3LIEIL7wrh4Rlo49SNYTpOrc5bVb8mug5LWry/cjwaW1bmrcKSDEP4QGsmHy9tOf+so3sIesXYYBfJ4YUrMIOdvA+dOdC3BwiDdaF11WGS/0hfrBDnGlkcp60S'
        b'6L4vItBvCjbIDp7wd9fKhDoT3dmbnhI8q3tdLXZXS6EVYverFXwmmcq9b7NasHIy9SR9dvWFZertrStl6udPjVU3zY5PZf6X/9ESiLKjLAPPJp2mR8XFX5JWypEWZl1V'
        b'm2cNoenKuzUSr3J+kPik1EQJ8+RIorc8V8BKJ/V0nRj6+Mtc5iFYU0TJ+XIBf6zFFrjPB6iek9YEzbhAAD5SXyk+Grri7d8+KMed4/6dxTp2wvr0S2++PFk95t59y0z+'
        b'FZ3MnVFxMYmRFhHJMXGR3lzdR0XB/Xal1DcNzeR4j33DNWhjDF/p8OSuoMfHeXzZehA6pGaDurrMasDhUJ7hS7AYGldw/DpjGcN7EwRlJOcFoyk4wZh9DMvZpYa848YD'
        b'Otf5pEnBvhcMKRIqL4eBL7weTCuC32AZhWVwPHvwxXjWnnHscunJZd/rUz2sriwesJorV9ddfPIEx2hB9FuLmvRWmq/MaLmCD1edDP2icbKaCfK+vkFuvmYiX/5/rS+o'
        b'6vakYgQ7vsqdZ+POEHG57Jx7mwNgnMTgZsMvheH/NuD+kvI7/QD9qqEqxWRKIjlVFeF646cLtGlpqYmUhHqaSkINFfp+gxJ/XflnciIBXxXhs503dIRWyTpCE2Ml6e2J'
        b'nb6x3Jlp3WNcDVDZkWmRwHSX/CUVWMz6WMRuRtGAQeiAWqcUbLPWIiwwg/PrDthBbhSOKDhgCdRArRJZcB2Yb6xOdmMh3IUHUHfsGHSrQi2UCjfiY1J2j9WhxQEnoRLG'
        b'I2AKB4LURWlQjw+hAEecDsFjGHWHxyfowSosvUrIYgAeWF2DHm94eOgaLpK9iKM0jkGY2w/3oAf7YtNsdmDLXszFrmSWe8YMd2y75kSmbh9Z72P6J9IO+a2Hsm2Y63o9'
        b'wRYrmD0efwiLLp7YYByxwc3BSz7UJsfKD3pCjSwJuEwdglm8DxNQnQyDWEPNTLvDtH3SbqyyCcNydeyLxlFdAj93oRa76WceG8NdsdXfNgEqonBYATphGotSYAxrsDMQ'
        b'h2H0chJZ7Y+vwzw2BUGNIXZfPIuN0HtgHT50h3lrEgUF1FGl9jEYCYSCXV40gGkmikau49BJaBGSLUwWJNaTkdqKVXHQj63QfXmzWBXqYRLv2FhgD07HHVQ5hFNQHGUE'
        b'uSeS4FY0NdvkAwtmUW4pxm5YGY+Psc0TG0INYPjKEXwE47RTo04K0HzSLJgBNmiAQpWdQThhgF3YTf+a8YFiaD9Ni9EATRY4c9B5h9N2PV0cP0UftOfsOmvOUhi1dLEY'
        b'q2EqKIM+rdFQ2YpL9MYgjsEIDWdUgE22EkdsOQdtNrCgg3c0In2gMjbTGXMDsGkzlIXZKeESPDLShUeJsLQRimLp9QephECb9xphd/TWU2ec9mAd0cEj6MuIIKprxNYg'
        b'NcNz2cmOOThpdH4TtPpCt+FZHKH1acJ+JZrMJNFTK3a7YLkSFB/HOWvaxkYYsqdZPqDxzUDBadqBKsvDRA6lV2BcfyNh3se0lXc1bohxAW+f2O4HTVnlRPem6s7QEXAE'
        b'Konq1WABJ9Zdc6G9vX8ccjdDOzZbqu3Dh7Q7Y9ApPg59URHbzKA6Tg7KTG7ugXsHs7LjNLGBCLEb+2ldy1PDQ2Bx3WlodYFWGCOoXBCB7buxyXwnPsI5mBHDqDLWb8Tp'
        b'CPlU7IDJ4NDLh7HtemAiDGEbLcOiKc2BqAOHk70cqYlOI2jDPP/T1HbtaWg6AM1QHEmclyey98FaGLWkZ8ZZgPz62eu6WqdvRu47EYvt2lf3aeMwTbSMyLiAOCJ/P7HU'
        b'7RPG3tuv7qRZDRGxVUELPthLRD5ExPkISyKwNhEWaF7HcR5uK+I9Z6zNgTtZXkficXgXFpuSWbF07YDVTSi6oBwIjww2s8pieF/7oFwKLoXjuAirr6yPOM7SQ1Wg/IY7'
        b'KfY8oxNQGQq5WBitCXeg3y8w2CZKZ6chDhw5oaKnY2Utv9E2mFiowxtLAmmDm3HQAEpIrORGYJ8d7eQ85GOhGGt9oQbHTLDdF0tP4yBMyGkT8ZXqQzeXElQDhWE2bHVJ'
        b'hT+AyctXDKFiM/U3TDTVf4XIoThbW4nYYSIG63H2mo0e1NE63qL9GSXJNaUUq+GJdwzhId49c4rgez0U4ozxeVj08YIluK+8HWozSCD0QZG9BCeS8PZpWLTawHzT5/xg'
        b'ZiOR3BBWBECtl6f2uctkUsyQZOrHzrOQRwzEkpnybHBId1fg9nV+kEcLPhWK9xJp6fr9YNwMH8lDc+R26ILbG7J+wARxFbvpuCPACaoYSdKwZ81hMsse28/JUbN38VZy'
        b'BNxNU2WJV/v9LaBPK9wLBpyhHKdpsRawaSOR0mMopZmNw4gHFJ0lbi3ciovuzs5O2OwJPdFaKlhIJHuPiGoGbm2DVpNLLBQlcoaFqwI7Kw+su5hpTrs2AX0Elkphjjin'
        b'lliuLRI6rc+eTybx0W2BbQm04PMCIqVSotdB6IFGrD93nMTikrl+SOb5C3DXhwbZi9U4aUr8UXN4q80VLNdThtmVVEs80uhvSEOZuowFlso3YTKZk5j1GlehhURl3xFv'
        b'u+wtUTDqm3NtvfjCCSjTh7wYmtsSNdBHoqnAzpnot1kxCSrgfhjUqdMmD5ioQ91BbHGHu5n0SB6yydzBTlJL9yFXU4QFTiRE7q1ThJmDOGewk8hhHOZs8LHeZexJXndV'
        b'Li4Rc6GBeLYI6zVprXppen24ABP+tJ/d2lgauimOqK0Ax1ygl1Z94dwu0kwPQ68YEfV2JTlhdTjpryYzGLhMDFFuRbvRfcSGpNxtoktSnef2XdyPNaYJ2H/9qEY2DbAA'
        b'comWu2Fir4lpdARMkMiZUdPDOpzDAjUscYNOmyAiCei6SgO4jVWmMEU0MwRV2dituHE7LfI89rqF7oHH2K7itpvVSiAReZf0dtsxmDgRG0B7OQH5GaG0oy2kDu/AfDaW'
        b'XYLm84oSbHSKOWHF6fQqr0zSNkVZJBOq6ZnGQyf0T2MTtF2EUtElA2gn+qYVJPqGzjMJNMolMvt3pHi64e1kdayRhChuuoDDG6CJEdce4uduN22cV+AImxZ0IJPJ2mQO'
        b'YCzgiDlOC49vDoe7itgSoCKEMZYLXElM0wzVmTAuIHm7fR3m7qX1bTbKwYeKMAe9khOm0OoKQ7qkDFoN6fFKDWxXTDJKIJpp1SRmbLYxw8fBVu7QdjIH642g3HPzAdID'
        b'Myq0NI+xTNEfBsIZt0QIU88xMNSRjCM4fz6ExAWTwA9IDhD8SLGDNl0X8wAdHAmFmvBjkH8c5rTw7ombZ2ld7h7I0YXyQO9QGNiBkzc3uYaT3Bik7RhKokUZgrazV4XY'
        b'6GYLs0HWORqumAdt0OwcRWo5n/a420AbqqNoiYqwVwxL2lgbrK+1gVRfqR5Un/eOCCLuXbQ96ZBIfFx3GuqsoMBbb48e9ifCAxdivpIEqN+J+a5CzJX3h7noo9DgFg8T'
        b'zr4wDyVH7V2P39iALUT9JBjvUZfFgiRSA904xpLIJuD2emKXcVqtKmy3gUUoNyQubd8B89dxOs2ZqLaZlF0lNh5Kw+4jJFRyo09egaITKcQBd69D4/V1RFdT0VdxINYA'
        b'm0kKdpGkKHXEihBtOySCr8beEwSMiKTvmRygMXTQbz0uB66c0CLFeGwDTAQSHc7A5NV9xPOLOOiK5bRyhaT27hzYzABZOpTHmOxitIg1eoc5WdBNw8yFznhojNTOvuSD'
        b'7dTLJPFVE9TG02gGCBIUiKCS1VUsN8yh6bWRDh0i1ZlxGrqssBN7DfzUA0lT3E9Yj10SbPCgLe7D+XPQEU5DfOhMNmIvltjDLWRsvoiNwdRE8YW4S0wHYV6SIU6kkngZ'
        b'x8LtbmdUcHTjXreTm8h0zaogwvY6bkVkzVLgZBjCHB8Jk7CSMITTQXOYsYbRS6q77BXTCb42u53C2qM0Ebh7hLZ3kfqdSKclmmYC6PRWKLLFgr0R0EEdl8Joao6T2mYv'
        b'WMSRSLxDzzwk2dF00xhyzU/RXj+SO0hSsBFmd9sdxqHzBNAacFZC4LKSdNggqecpJJlWcNMS63WIaEuOnoe7ntgY4EJ6tVriAi3Bu9m9ljDvQL1VsusqYUGTWLsDurRw'
        b'wB0q917BWg0f49gkEnR5isQenTkqYTC6w+GYt4GTOpHXA2jQsNwkRyvWoaJjj5PGO5XEbpi/hRYxdwdR/T3tjaTeK6nN4XNYcB7qjwCJJWdSgiSZCB7gXBi2Y6djGkmr'
        b'BrhPeqSXQP4o7ZHQ3/IUlO1IJiXdBg/8sOAMdp9zgFJvCx9atgK47Zqw0e/ESQZgSs/fgL5IM8yPglzdHBNsImVVcxan04luGk/iUDiWWFpDk4iI7I43Fh8h0loikT4c'
        b'e57MkWoS27cNDWiJJ8OxzhGL4U7KQVr6fhsociaK6cWavaF6MXb2fpHQG46PUs6RTL7rqKmyw/aAnrWboa0ZifRJNbyte8x3F2nCpR3QHkzt1qoTYT1OgtKAU8Qhc+fg'
        b'7k7o04vGsWTqso0m2nGB+ODeWck6kj61MGwFI6q0nKXYFAu3jWH8fOoF/cMwmEgPDUNLDAmHFnECjSs3kMh90haqnGBxF+naWbx1Uw8fCxKxzRwb9Uyy3uQwBDF4HSPK'
        b'vGSOJheJJq/gkAT7ryoR6CnQzaElzNu5ibDgpJG1DtZpEZQMCch2h+qbxjtysqAowsA/TC2AtHcP+4GC/ST4G0mI0GtODDRd01KHB1doa+fwzqnDqqQpp2FJMxzvYUsC'
        b'adr78pibhQ1BEljMSaav2iLPE5J5yCEHIOQwD4vxRPwTkQZYmG6M90yJLrqJdYaCkrHmmgmJhnYGd+NoACUXHJIMVOmNGhIbjbQaZT6hBPMGrwdeD4m7slXNFwmt9uC9'
        b'rSS4759zvqJBi1sGjG+r4VFyqrMOTGtmEpfkpROaqD7ta6u8HUcjfTEfGgPpkWm4pYiD6hIsOckuBiW9W+0PxanQqkmGyi3ovILjYUSto3vUzD1JPLXEa7klXHUm06l7'
        b'E3HpCAmbso2mcrScDdaE26r19aA+2cT4OLHrg004e4LkVgVZJ5OkkOeSWdI91qbtwL5tZNsO4q3r0GpqSeLvkSJ1VoB9ticktle2nIshRs8jhijIIl5oVYHavVh50Rbb'
        b'vHcQO0zoamdEkvhbwMEzOHieOKd3C9Fg+wFSsDO2UIyPUpOhJ5Ns8BIylPWt9UhcNh0mGT/huI2GXR0HFQQZ5LE/mJRlCZFqnfNFnAo2xEI5MtRHJNRvB5Fbq2DbZafU'
        b'Mxnr/WmLx7buJo7pgJroTGh3vgKl2/C2/DksS4CWQ6wWMkwS6GzC26fYfY+ES9r1vDXgjufOm35Eog/wYXZoIuHEpkDn4weYZTZkD/eOpO8+BzNEVVU+MJYTrxdDMqhF'
        b'kyh80hJ7Tl47gXVuu4koHupvxbw93gnBWBmjY6bAZZcQWeR5ecj74ZBAuEfAXPNz3EGhM9dhgZ0TIvVZJBA6EDS1xXHujZtWuORlLnIIEwhdBAQwRrCAPyU7TvS04GWp'
        b'QAqyQyA8zL4j0csf96twdGSeeyFJsHmB0FNAKqF8J398thnKMrDMQgh9SgKhuwA7jXA2y13MMhPWkYjuIIVUQbzR6qJG6z5yQ8X4rDI0OgZoRuiSYqqxInLoppVqYJB9'
        b'J97ycPOBogTn9WYkb2bwnmE2aacu6PTQOnKWRHg1tEdiFSEWYmK8Y8ecLmR711yxynKFwfUM5l2He5IILFaFrvQI4pw6WHKG3JCT2OBLe0nfEz8WHqdfe+E+u3ayOFiH'
        b'MFzbHtqyDpsz24ny8jaxs3a7Q6ndKoEf9VkoIbk6QmKkjvaabJz4a1BkRdq1Jgiqd5KtME4UcYbgS81OknLDUGtPhlJhZpgPPPYicu8lTVFGhDVuREZTARlmJfZm16DY'
        b'luDbHAmKUVrQuzC6hdBwP7QclBy8JMYqRYkmNrtfhAE7fJRuboyzF3DojMc6GFC8liXxSQ8jIVoDvcrMbwDNRoaYRws7RPIojwRk37kz1FY5rWdjqF4CMe0sDaF6P021'
        b'z2mDSogadkaFc5ZXqxgLbMiQyaVVGUYSpUs2UC7G0dDdfjZYeJrkWpcjju4kxrlvaw7spMYAVDsSHKqi+eSm62fJkXaqzqA59MLisbMEJ+ugdDd0KuKDeKx2h4bDeDeY'
        b'bKpyslwWFddhWfiWKDPXjfhACRrCoSGdGGXRTCMLB6LS07GPfmqvq9Nwb9udOk025DBJ4xqiWNcT17RjomHKVB2mNfCOOzFW/gEc3uNBvD0ARcg8O7c1yXyfhLwN0B5G'
        b'cgAaD7ufCcJc37PpIWf0CRKVkDaf1T+I9el7bElWjF8Sk4i4Bw8s18NSVhwOHSBzoHq3LrbqM2FOWq/Y+iYx6tR+wou3mTvKzDeGtCrM7IG2TKKpYpg5C8XJpMh7YfAY'
        b'sfCw100YDiOTr5N2ddjTgfPALIhJ09w5G0v8cQ+qDuhvvGFOjDXpyywJrImBeey2pj+WcNFkPTRKMiwyDQhyDTnjowvqmKeOC0LovHDzbDyWZfWRGtOHWdOnnTMkRx86'
        b'm7hoXsIH6xU2XMauaOKNvEiSzGP+Z7HUU2/9EbJclqApnVazCG/rq+rJnwnzDiDxU227gYinEUYMsW+vgdeWQzCRQzZB8WkDP8uoI4qk2h6dPMU5asb9jKmfVqizozVZ'
        b'UKE5jCeTZOomzbIYh9NZMG0GI1B2yJyYow/bk+kfVZf2QSupNhLx1YxYe2BsNzy0TiHA3+mA49FnaZ2LfE7pM7iJJKvvhQgJ9bEczjwj4qCxE6TpOuWM8L45Sd8J7NE9'
        b'Bf1bSbRWQptLujcB7c5Ygp8FLkzCjkHe9URC+BtdCC/0GGoy55Y33s/WcVWBwaTzJIzLeVdARhTxQPXFHTSsfCKerhskC2aNiBU6yMyF+z4XBAlYfDSRhE77haOxpBwm'
        b'sF1CI6zNJGVcQG8QLMeOqGgYSfQ/gJP6WvB42xmihWY9vHfEiq3IbhzQl+BsPJENA/qDLJqTjosX5A9pYcvGvVjrl0pCrVwXu3XIBqvLITyVC0tphHgmD8OAtp/pYdvt'
        b'pILvYkOoEnadSKFFbzPdlbXZLH69/wkdbbyrezPLQR2Kjop8ieoHif5uQ98NEgVdWafcoewsCdp8c3ikJyHGXCDOmL4ekkTqMhkqxThG/35AYG824hKJ23ana6fxXqgl'
        b'yaVWHDKD+aMXYNh4hweJhTq2wbQJj0mytbCjtNo0jUVcuuHvTY327ofapHUn/KjvuY20HvOu8OgIyeDiMPmthzMdIrPeYMZt30USRx2BWLZs3YZQ5xXQtM+YGbihAapC'
        b'mNLBEl8YUbCE4bMK62EASQZO7iciGLE/hYtQahVvT+RZw7lMBrdakhhjTroWbQsoJKlG9FkEo2Qe4OPLfpZm3OmTBecjMGAELZpGG2jty2Eymni15/AhAQwYkmAZ3AEt'
        b'9pi7hR0KJr2xpH0a7wRDm00oiZ5iD2iPDiWtMHKKgZRu7ApN3yUvjjuEjXvw3hW8bQXj24KwINkaehOOkmbopTnfJ/Da7kZCB2a9sdQilHRH227i51uWW0Li8N6BdWfS'
        b'8bEvkVsjaY/CfXpKcCchGUZJgnVSD6O+isQFS6l+ZLrXEMWUQ282zZv01Qbs2wMNWcSwTb4JRE9kvTRZqCdDoYqJAw7bx2Oz5/okWICBLGyzh7kj6dhEy1eFo6c2w1KQ'
        b'4CDeUlfCJTGNsshnHczKM+9Ijz30xa53h8bjGzfYk+VVSlPCYVLptDmFxLF5BCeJn9PI/nygS+veEhnFOCcmzpQEa4Xo3JHYNDWYOot9CX6+8TEXCK2Oa7ATgaRxh1Rw'
        b'3AvKoqDplLk+kKGRjxUJahH4IAiqdF3Cz+dgp6fPpr1YY41jm+LOYaWtiKFXkkGFZEffwQXvK9do9mWRWqS9uvDxZrkd0KgbgEVRp09cOOrjRhxe7oQNGQejcXYryaOH'
        b'3AmrudMKYSQcHqiGGnEChontelrI5qh9MIZTW82Ic5ux5yoxXCWMmpIVVKatSApyMPX0Ouq0LBoX/dNobyqQ8EG1MkzrOFqRROu8qntTcxdxVwuJm8cWWBIGnQeSYFoN'
        b'u7JcCNL4aO1eRdhk3U6LRfrYjzUumunQq6eQsItEbgdNZYykYeNeoWeQB7OgovBRFE6oE1tN0cy7LBw1sNrozCY5ovBW0t7lBOIfZNNaN+wLUg6Gh3bYepqIu5Xk9pwq'
        b'M8hhyCiYFpvsaqhcj4WBbgz46FJjw2HGcM8Gh4/vRkIznptofcq2wh12mAobDkHbOlqYtgxSOfclMHbaiGi8VRSwbyP0GNpDbiTc3kPg14lkoXGw2UaSErVxWKAMY5L0'
        b'm6S1CmAy1I5UyoSECfAyxUx/WxhQO0ALXIUtBmG0RLM62B27Dh8qmWYfOZSmDx0HYMT7GpHUPVJ7vdhiiNOZnjigQzinijTofBzpgWwV13TawU5qpHbrwUzodZTbi8Mn'
        b'9Q5vh35nFWzPxAdaMecNoE9bKw3q1mG5Vyw1lQf1Foo2PrSfBDRoYR7JmfikuhwISMCHW0k0DBALtYdvxSU3kl1N0OFxxElAfFFKTEkInCRXLUyrxmDxflLORKFlrjC6'
        b'QVlIsmAm7BxJvXu0KY+o1ULtdSGkwyugRwluxUGRPQ5YkvgvuXEJag+eQ+Ym7xbAxAXHjSRR5qAofhex2X0D6LIkHm8hjhglw7o9XNlwP87rQ1PQQa/UE6Q9+6Efh+Xo'
        b'lXyYMNGzJ6OjB/qOwKC8EXFSOyztWGdIIqliN1Zfw2q2OLcvw7g4dacjfVpzCLp3heAsqUls1N5+aDt2HoRmyWminBJsTCe1tHjlLI7sOxQMBYmZJBjrrQR20BdxRS8y'
        b'ktY9MQ7noSISRtMIPNcQfKug1RpzILlauN2e7MJZLE538IpxIiFQgqU5lrS442pCor1BNQaMaStbojOuXIdHfvTPHmj1JnvhDoykuuPDEE4pTuL8obPO0GRKCpPs3xNO'
        b'OOlJ8G1ENXov4bjmUOKNJcVIAmu5W019soTERO4wFs+4KI+ImbHRIs6bkxBuJtqctsdJA8K5p7FOJd4VhrZjm+seqBGTarurzp5w0oona3EhJ9bdnXBAgWewvQkWZacQ'
        b'tl7E+0do78fhjjIu2CkmksYZEmJXIM7tuA65ZPc17HTTVA3ExmgurjbMvPw3c6Ae5pg3qwdmA2iCxCR9zFdEIPce9Lmvx5arAbvO7KGpNeDgIcy7iZU4ZURqseQc3Akm'
        b'oDVlqRCXYmMAo+4qxPUP6MEKG1rVokTigEVNvHueLKA8HCWlUrkXqzcq0hzvKVviw2txhP2KIq/ALSfSx5VwV4zjBsrYdsrAzYCI5YGpvNYmfHQ4GKo1XJRIXs5h7gnC'
        b'MUNMmu3HhwLS3A1YZa0h8YfCs16mBzMTVHBRKyR7F4l2QuTOSf5QlYp1NoFkUDMAOmEfd41o4/YuGNV28CIO7tKHORWYPn01cTf27yCZNUMmXeEFnLuigkXHA4knCski'
        b'6SeJU0PWyhZa7KbN2KGmIo7Rx7IzCfHnw2yx1UtDeHw9vTcMNQpQq61PvFYHMwlqHuZ7cHozc3uSzs6FhQ0ww2J39402kbVXHnnYiZB75z5aiy54uMkyGWq8txFHVJLR'
        b'k5EFLftoD4o8cOqQKgH3eYIE7cez9bFb7YY8zaDWDVp1la8Rs9XSv2pgyTw5/Cp0biFbskDnoB9MGUC71gEntcuY74mFRmGKeD8IauOgE4aIiCoDQpmrFO9nMXcXsDLP'
        b'D0glU1PYa4UlmThwI2wLaWjCP6fo8Q5fmk9+CE5nWxEoY0d6iT0WoUQ1NDLrDPHjHWCKhLBorx1Nb+k61G/GWgkh7qk0IpjhywZEV0PXsfgm3CY5Trgj/zQ0bU3J+oWI'
        b'3YHTTpOQsYEL80tVhZD+JfGVcNgkQHM7VhMLhGzPoa/bDWOjlA2w1/DgdtrfJXwYCw8U3cOpj2mCR/dEdji9EZbw/oEEVZpTId7NBBb9zTtzCGrloNGAJPnCZWzxgm4x'
        b'/doHcxJSNf03SCxWETfV027UqGzGHk8So0O0+OVYew2XYP6QHhFKGd62g3lL7N7ug2WJLMzlwZxV0f60PoU7SajcVpPDQckGIv7JqybE57N7/VKI6np1bWh8tdbrsXGb'
        b'sRm27TxOcIEYxJVIYlEvDqfUsNVxC95jd9EUnoMCV5x1gSHlKyRf6gj7NJBs7hEQ3c8pQIeROzSpknlwz1oTuo7shRZbQgqFBkHrsH/bPgUFLDnpirdVMd/Vn13WakXw'
        b'qtgexzRTcWqPmpcNdNti3REHF1qYCWiVI9bvJWFflB1uosXObc2SNJiFPBMi+GEhgbKbl/YSzdUFQKEqRxqzYSS/ly7uJJnQjsUptHJ9TBZMWRPwqIuJg56DRNTMA1+H'
        b'pfo4YUc2TU0slChAd5wJ9MvBiLMDTjPrHHNPkgib9L7MsrBsFQhV90C5KRZY0MKMrIfu69CkTbRZspWFkuWvKdjFBlHL9Yc0sJGwg8Jlhn8KdPcnk7VHaD6fxEQN9Oli'
        b'yzH9KyyrIpBWrhXmLlzaAYOWsOAGPWby0LKFsFXbaRi4SObOMPRYhhH6Ib1t55CyD+Y8d6Vh9w5o9oQ+c+vjOCFPKqXJYwuZtB04vpcU3ADjk5ZAnWO2BLCHrHApeDtJ'
        b't6aAcI2w60EbQol4SjB3vzf10bzNydjluoCwZclFZpkbmIn4o2YtoQqsAo68O18DR7jbI5F3KZXTGFm5NqKHer5eG+SlmYm5ojKWimleFkJzfYHwoAAbXXCEf2UKimO8'
        b'sFJA/fYLhNbURggMSutRhRD+I1qVS0gRCF3pJcKvbVxb2yTbvTzk4fZ53kF2IYFGxo5r6aQ6e/mJvGBRILRhecC15zg3GAl7WvUyb3nasnKB0F7ACjiQnctcZ45nxMyn'
        b'Rmt/h/epXQ+U3p8QSuJlGsvM5K/CmEDox0qDTaB0aEXQooVlPgq0rYWcX60GHptyQzBIgiovc9HpBN4VB3MKZkJ+1eZIePZ7ecrvwmKB0FyAJXKu3Beb9InPmSMORsx4'
        b'P5y7j5nQjbtWhzulZrtLzGVhjnrmJP5ErCowE3MfN2TwH5tEhScmHRbytX9edeLPu6UaXkrUUNgoYLllblxr3LG2ePP/fk8+Y4Rk1by34fW6EL+NR/QKYy+/Ha+QeO6D'
        b'xdaf5fxBS6dWYKbjfsJNWcfzT4Fye0Lr59vu/1NwI/H1ypCd728ZX/hZzuv/inld77Pff5r2obdjx7Twl9/49MbvF/E10zcaH2qW7hd1vm9kEvfR4/zdfy3UUXmn/mj0'
        b'D7//5uWo6/MWBiVvfcPvl95v96n/6no75t9uTrrym8K5io5/bHvU0Z/a0OPfEpBcaPvnH8+p/NFwQeVPho9L3WeMfu0T1PXplnft3h0O8rd/9WxJz9+2/OaNd8r/Ovla'
        b'4ICrU0PCyU5wyNvecuVbKS6lWZYfnfnd/ZqI8wUZu/86fmJHmVtl9TfkG9p7B+S/cysm4bbfqz4nN9XWlwdqdssP9350ub75B//wmOn615b8S7E/nz73/dAf+VZfqPqL'
        b'19TXvvV+r+83ovOvxkQfvxR9OKxMI7P2N5M+P0lVj3071CTWo27Sq/j/vB9dn7F+IDS03rJ2/u8OmV1t0TMnaqceNpz98GOF2OnegJ3NE4qLv/3NX+e736rK7tmbZvzp'
        b'h3/9aDaq9WKt0tsGsQ9/kPGj1JHSWV3vf9cfvd/k1umzXmzwnmnB9IdufxlU71gKPXrj313fU9m5f7Hvx7+8JnJ9peY1e+2fROb7G276t3HHyDet3V6p/CTxzZ+neIle'
        b'+/nJVw+boGQgRBL4sUd5ZPk/my/kuJxZtP2L44E/R5RH5d9ve9kxvuf75tdtjsdWvr6974rx4B87s9elvL8v5vSBT35o8f4rN3ZK/pT317sWGVW/HnM5/OHIt/8ZG4zf'
        b'e+nvjYuLr4VEaHu9NtH7sdy/fr/+/QTzt7vetd/u4dTxtdr3bWsbkiprX7Y5dfDV0gOvLsLuN0Yr1RMjVX9SteW34fo5b35TqJF1/S9xF46nTQ44/3vuQOprP//tYmjJ'
        b'zwz/+c2lV/rf/UnHbP+/5R5/Iy3g/aVr71e9G9xy89PXDr/8kc1n37b9THVJuz9w3eK/VR8vnJzPNTVT4Ur3WMKMKzGy8DCUcnKkUjudT25tIlYbXVWG2SmcT25Nhx7+'
        b'4FObqY3q03fNYFW29Pga4Zpuvr5Ls69INZ1Y8qG6sjrp9zLN9Cw1UsozYoFRtpxSeBRXmjlNG6tU06VPXMbpy2nqLPy8IDBwEcNDw51c6RKs0sGeDJjVvqSWloUzmlAK'
        b'5ZpK6io4qnlJXmCmIYcP/OEBd32OKdNYGc8+d3jTJaiQti/wkVOAWSFU8xcql5kqq9JDUBLHt6eE90V7CHHlcbe36ZNO7M6ACqU0GmIGabjb0hZtsW1lkzilAI+3OGfu'
        b'4vJ/yySkTwfwwYpyK0/VWnGD3GcvYbP9f5tk+v/8DzMjTrr+/+UP/krssLDElIjosDAu6/o7LHnWXCQSCfcJN38mErHjZzoiJbGcUEmsIKIfsYa8jo6OstZmLUUtBR0V'
        b'PV05kZ6HwVZ6/qbAlpUhOciysMVyIvb7/y3u2mOjKML4Pu7Vlh6lIJQWgbZU216vlSLKS7RKKeV6rbyhD5br3V5vr9e77e4etDzkIVJLqQXx0aBSLAgEBEotYqwanYka'
        b'EzQmRIHRPyQo8fGH0ZgYIVHnm20L8T+NCdnc7253Zic7M991vu86v983eStti0/LWQDXJIGfZ+7R9gv8HHhfNXLFlrYmvSRFdIqpKQJfsJXLFvgFZkm2kC/k0ZeL4jbu'
        b'dQurLRSwK3Bs445aYF/1TduIZLiDiaTcemkrRnY5i9o30PFbe72L77xR3DFj5M3BYLuuYYhcYACQfYK7pN6ecYqlgWyjoR+NLLqoS9ReVYHaUZedezTZOVG821+rHLXH'
        b'BT0DsilpF2Z2llWKJSmlJ+8t2zTv2n3OtJ17Fwk7E7ImPWntm/LBjmhRwZmCy5lbLrkvdM5ytB06NnF5x++eM4/m5D/7W8nPA2M8P3nUd555cL38QyThRPgnNfy99vHn'
        b'12ovvvDer1dW8Zvyv0UX5hQvnT6Y7zt2xTu7ONJcf/n6Qd9Hdd5V65d/diTxz5vffXL6x+ZQ/xm9Ryw5eSX/4pap9hOBzO/3XR/b9gI+H/rFfbxQXzLYcKCm6lxRxl8X'
        b'W25s2Fj8XPbM6xcipVrvmzu+fOuL2m4tY+d8W0quz+fIyN5z9f0Px311ebt9yqCjry3l5qz3M7MmXU2bnvryN+MaZpXtThpQ2121hztH3f311LLtNV9fnVz329rgitqc'
        b'Hv6rxpvb0SXJdaKu9dNo3hRG35XwQDk4q1VVjFJr55LwQXwW9Qv4eDDAWN2Fi1GPp8qNz0IlwQk71Mfgd0T0am6RmeAEfjA2pwKo/fCrjp1Db2Q6U8XJiehFxvbagPrH'
        b'g9Sp104952U2i+DAz1Qb4HeuDIdwR5GN45ehfh+HD09awzghkg0BnzoXmMB7eC6hMCNFoGHDoSoz68FTQgldDzkanjEtgUoe9ektjP8bqcuC7fTuIb2u+9c58W6xcqXG'
        b'luH5kUc85anqEIMcwo/1poLeOeqxHzZXWG857nwMvZdXbuFS8X4RvZ0ZZgyWRWhHjmdxQeXMGTxnx8/SEOusYBtbanKgD+Jt+JCneAa9lwYFaHcWqJGNzhTnotOaqerW'
        b'g196CCqUe2nQgI9BuROfFqdPSzcJ5t2QgQl35NNAHDbbdVEfeQmPBmlQ8zTr8tgaGs904M4t6LC3gOMs03n0+hLJ5M/sgl0LLjcN/7txJ1Dgm3jYeuk2tcN20bC+1wU6'
        b'dCloXwXIg3npAFm4jC0WtKMVD7I2yic0eODR6ADAeCe50ak8Ae+dOIE9faAS9eq3FSdGaOgtoL4W9DzzUcKoe1ES7h+Nz+moHZ9X8UAz6piD+kcnc9ykbIs9DfWzdiaE'
        b'pzHSkYuNApiaiA4IuNeFTCp8EX3sXuonrcXbh5XkePRSaJ2RBx05Cv9N9qBTuXR2QRaMKSVWlaPOokp3no0rK1260b4ZdftNOv9u9IovCffhAZ7jaZjzLmqjLSxPY4X6'
        b'ChohvQHqKFVWLoz3WzfzwPBvZiplD6N9uAdK3TTYPgQK28McovS4Be3Cx5aZjPUevBe9QkcdaJvtFQKXcE/WGgF1gPQ3m7HUANrjWuwu8LoLeW5UDT55l5gYncvcPvwW'
        b'OlLtoXPiKaQ3d6HXnLiL9mDsDBEfrHaYBnHKGO9aVJAPbE6YELSfx3tBiu8I3sVsmUb5AyWuxVaO96CeHGpA9RXD6YJy7/wf8/9pSRh/BzyQW7l2VVh7nA7Ge3ewYxxT'
        b'PHMMkS6B2gVuBaiMpQ7pjtGaYvTf08SGj/tM5hRzDvKJGJGjWpiuY8RqxNWITCwRRTeIJaD4KcZUOUpE3dCItb7VkHViqY/FIkRUogaxBqkTRd80X7RBJlYlqsYNIvpD'
        b'GhFjWoDYgkrEkOlJk08l4kZFJVaf7lcUIobkFlqFNp+o6MOJ7IlNjddHFD8ZVWrSFr2+RnrzKFWTDUMJtkotTRHiqIj5Gxcq9CET6mc8IEdBVYokK3pMMpQmmTbUpBLL'
        b'wscXLCTJqk/TZYkWAXWbjGmKBWY/aCbbkAJKg2IQu8/vl1VDJ8msY5IRoz5htIGIq70VJEkPKUFDkjUtppHkeNQf8ilROSDJLX6SIEm6TIdKkogzGpNi9cG47mdJj0jC'
        b'8AntTjwKslK33C5zvHM1kP7VmgGiAOsBWgEMgAaAGEAdQC1AHKAeYA1AAAA8Vy0E4ANYCxAGUAFWAqxm2nIAQC7UNgJsYkQ5gGpGqAWAB9OaABoB1gFsAKgBWMVaBi5d'
        b'C3zaDBAcYQaCISWMuFB/VN/mQrGyG44gtRTZHyokKZI09HnI976RPnQ+VfX5G0FTDGirUCYHKvMcjONH7JLki0QkyTRZxgIEthuxmclItWtw5YlhX/cfqYuJYx6d93hE'
        b'ng8EOUaus4Bf8N+/OivGMcnAvwEgnE3b'
    ))))
