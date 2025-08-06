
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
        b'eJy0vQlAFEfWOF7dPRcwHCIgisd4wsAwIN5nREXuAQGPEM0w0AOMDodziBo8IiQDIp54xfuMGjXeGjVXVTab3S/Jnr9sdvbIZrObTTZ7n4nJbv6vqnuG4VTzfX+Rpqu6'
        b'uupV1at31avXH6Fu/wT4nQO/zplwEVEpqkKlnMiJfDMq5a3CMYUoHOccY0SFVdmEViOn8QneqhKVTdxmzqq28k0ch0RVMQqq1KvvrwguzihM19XUiW67VVdXqXNVW3WF'
        b'a13VdbW6BbZal7WiWldvqVhpqbIag4NLqm1OX1nRWmmrtTp1le7aCpetrtaps9SKugq7xemEXFedrqHOsVLXYHNV62gTxuCK+IA+JMJvAvyG0H48CxcP8nAe3iN4FB6l'
        b'R+VRezSeIE+wJ8Sj9YR6wjzhngjPAE+kZ6AnyhPtifEM8sR6BnuGeOI8Qz3DPMM9Izw6z0jPKM9ozxjPWM84T3xlAhsRzfqEFkUTWq9fF9mY0ISWoEZ9E+LQhoQN+uKA'
        b'+1QYRzYigqkicKg5+E2D34EUTAUb7mKkDzfZNXQOKgSkQFlrglCZYS+ajdxjIRM/jZ8jV0gbbtpIWgvyFpIW0l6gJ+3ZiwqTVSg+Q0FeLUvUC+4hUJbsCYrOzTaU4dbs'
        b'ZNJKtuYrURjZIpiGT3NHw2PVKmduPN6VbchWIoWCw0fxCfy0ezht5NyCiUnJ5GX2Un42addnK1Ak2S3gOzV4m553D6W13xHJyVzy8oa0CVAil2wrgHrCRwozoshZVgDv'
        b'Iqcn5uI7uAlKZOdLBcLIJWF8WpRcxygD2emkj6AdspVDweQ67sjm8WWyz+oeAwWeImfwmRByNZzccI4bh1vJrXpyfRVuCw9FaOhohZq8gG/rOXcshWd3JTlF2simsLwc'
        b'slVAAnmFwwe1o+FxEoXmOG7HL+TiiwkwGFtyyVbcWkBBIufIedyeYkrWq1BmhrqxEDfDG3T48DbSTvaTawBbXoESKdeqGjlyCt8me6AAG0B8cFlSTrIhP9nIIe2wkmgh'
        b'eGISPIujLx9WkmNJWYZE0ppHexaC8EtkB08uubIruG6LbYIPAw5RRO2Kpuh/i6ieBI/ek+hJ8hg8yR6jJ8WT6hnvSaucIKMv1xIE6MsD+nIMfXmGstwGvjjgXkbf6u7o'
        b'S4GP64G+Zgl9g0tUSItS14TryrS/zVQjlrmliuL0bUDVMsPPV5ZJmX9bpEERCNkUZWXaxyeOlTJXWhVIgxLUmjlleWmlJnQO2YMh++yw2MYDQZ/AUvgw/m/8zfFLXNuQ'
        b'PQgeFNoOcJeTUsPRnLK0n6cNj3dJ2VGRfw/vCH9jMF/4K+6/sZMM95EXuVMoumwid8lmwJe2lIVLHAkJZEtKFiAGPleSkJNPthuM2ck5+RyqDQ+aRS7g6+75dFIPBi90'
        b'uhyrV7md5Ba5TK6Tq+QmrMYb5Fq4RhscFhQagreTE3gbbsFb01Inpk0eP2kCvoUvKxB+5YkgcpHcK3Ln0sb3kcPkXu6CmrwcU3Z+LtkOy3gr2QLroBVwri0lwZBo1Ccn'
        b'4RfxWXyhCGq4Cm/sJHvIDrKX7CYdSxAalBoaSW7jZ7pgE50DNfwO8pFvRvaESkGebb4F5nS9ALPNs9kW2AzzG4TigHt5tqt6I1aKHrOtMDkoGthu2OfyzmlwZzrxQa5l'
        b'2Wvff/3yjit7RyrfOm9Z+trtiLeeeO36juN7jzfZOKe6IpTMPWP/nSFmR1aqUDUd5dSExm15Xa90sZXzyggYhzYYje10GStgaC5P4/AVjtxxsWW5IxrfSzJCdquBgzW4'
        b'TUE6+GTcQq66YujQvjoJ705KTshK5uHhc1w6PGvmXXRECuNJB5C19rzxSqQqJZsaOHIRb0plz/B1ckwgbVn4IkI86ViznlsAww4r3csn6PWCg/Y34MLD5X70zEpH3Tpr'
        b'ra5S4mRGp7XeMtsruG0ife5U0VGbF8xFcg6V7yW9whtUa6mxOoHrWb0Ki6PK6VWbzQ53rdnsDTGbK+xWS6273mzW853NwT1dEg46tQ4lvdD6KEY6KRVFr0TwKo7nVOzK'
        b'f8XzMFcc+i9NuemY1CauToJuc4jHh8g2vJ+bR27iqwsq+F5Qh83ubIo6PEMeRaXCjzzCQyNPD05HcSS4B/IMNLlpBjm1ROHMg449jveRcwg/75wuE9gd+PlceMDhM+S4'
        b'HhFPCT7AekSey6wl14Aqc0DIX1EifAPfJSfcUfTRlYXkNGmjz5aR/RnABZGVPQhbg4+G5NPKXiX7BiB8N4FcdrO5P4Kfw2eS2KOXye2FiBwke/HLDIQIvHdeklEFTy6R'
        b'rU8g8jw+j3e7I+GJNQlW4u6FlARmrEP5U/ENNxAxlKSfSXarovHzCBmQYQSnD2JdjFpOLs3gqxsAvmfgPzCDw6yWOAf2PMVnwtCQ0/D/MXKDNUtZ8WR8V4XPLqfUAv5P'
        b'wuelJxcFC7mrAspzFJ7cgv9xZC/rH96CT4zDdwUHuQlPDsP/rAXsFXLISS6Qu8KKEXD/Mvwnz5FtbBhxM3lpCb4bnoXPwKNj8B+W3llWm30MkLeTPL5JjlMxKoS8iG+7'
        b'B8CDRVDopWIBNy1FKB7FF6xn/SAn8srJbvUoE0KpKJW8im+y7LI1E2CU9gFizZ2LtyOzY6J7MC39Ag/r95qTXHPjnasBL8lZbgw+h48wWtKFpPGBVIeu/yrUiJZHrOca'
        b'uRaQPh2KRm4nv0pB2RNbYOxyjvfyxlQvV3GO61yvbOV4g2fabU5XRV1N/WzoAPo7bcNN8T2CtNhzZUGGCQRZpANfA4LcWmAiW/X4ppCWhs+RY7gtFySba84QcgHhe+RO'
        b'CL78FN5uu/FkvIJJmj/f8I+x7ePDcGrUvK8bgicWJghVHyqG/fS7moPfCsvKe2f+2A1/fm3HzzvG2W8e/U3VmveeffKsYtjSmUnG27/ZMmnWT8wj3ogY+x3Fj76tr6rd'
        b'ZSqrWJP9eMc79yz4P1Oz5u8yXfKEbFaJ0z/ZNPd7H5/46L2cj4yLR7ykf+JP3/7pB9954u9//uC9thEbz5yPd139ORBTitopdnI9yagnWwx0NV1IJKf5CbgFMUJLTuNm'
        b'3AICDEzFrfjsPJMSheArPDm8sc5FBaos0txA2gwg3AG7Vj1JjpDj/GjSJrioiPgYfjGVMc8V2WQLyG6kFV/IUaKBEwWyK1p0sUm+hA8vlwj5+kZGyikZx/fiepBTvaI7'
        b'fe02aSHW2oo60WqmBJaRVh2dtiwFp+A08MP/VyVo4D4Y7sP4CC6M03KxnGNAANHlnN7g2jqzE/SHaqvTQUUDB6VHPWHhHRTVHJF+WkuryfbT2pci+6a1sL5QJtm3visa'
        b'KdAQsr+B7FI04NtLH0BzGbvuQnMfnmE3PxzDDpLEM/u6SDQGRQEjKRv6cbEsnj1WmIV25P1EQGVlwR3zo9AClvv3dQOQruS6CtWXadWJy6Win7pDUNSan6hQRFle6Sob'
        b'kmjvgTHWCanQFN6NpuHj5eQK3mJbcm0153wcnn5yIu6zst+XVVfmWd6uTNj7yabLB64+vkUs2t80eHpsTKpB/ET8pMyQJlwdPCN2UFrMwXSxaGlRbOmBMemGZ6MWR+Qe'
        b'ovLDSyqRf2JyMcgNIWj0P6I3TzzyxU4976KtW1LX+hg/OTAWP8cnh6xiyGrDR8jLScZsQ6LeSK4JIN2RVoRidYoniYe8ouceDgkHVFRbK1aaKxxW0eaqc5hlLh9Gh7o0'
        b'lqFiGFwB8aICEE+osIledUWdu9blWNs/3lFa7Yjx4x2t5Qk/3j3fD95R/aaEHMUHAOuyQJvC2wqMOXgvacoHGYm0pmBYgsD9Z+GDKnJGtbSHAuLHQSYycoCFnSIjxzDw'
        b'4RSEHiIj7cfYHhg4SsLAkSsBA+sVAEDZsn9VGWVkOysCstljOEA2A0wkKmG57w9QIs2yP6pBujccFKNkFUHLI0WqB+otMzyfslTKXBqjRbFLD3OosCzPE6qTMj+cEo0S'
        b'smKV8PrMX1RHSpk5o4aiqQmPq6Dksl9BqyzzN4qRaM6cvwnQ/LLSwYlSZsn0MSir8XugkpeVRzeukTJPDU5AhXkvqmGtjLqzdImUOSPTgJYuXaiGOsv/mJ0jKz1jQRNa'
        b'U4AQaELvrymSMsdMCUZR2lS6fgz7SoKlzOqZ8Shv6RQeSo6aofIBb0hEJdVxtOTc8txcKfOnmliUugyWd1nZ0IQx5VLmF3pQpMZ8RJev9ksULWV+zxWGhopzgS+XaT+y'
        b'xEmZvy6NQxMnfipAnUOrG0OlzFWmEWimfQ0HJZdxFfVSpsc2Gs0fQ4WzsrlHjI9JmTdVMchQv18NcC7Tmp+UMn9VkYKWza+mDZXPD58uZWZrJ6HqhF/SiYs8myn36FfZ'
        b'aUhs3EnrdHxcJM9m/FPjUVl9khpGvvyvEych/RgmTxWAWHONashFY8aj8WM1TKyoA6ZyeQJM/KKRaSgNd4BUSKl0YRrkwrqbTM5MQBOi8AuSaHLkSXJigoqKmeTWRDRx'
        b'5ihJXNr9JL43AZYCiIMHJqFJ+EVyRSp/qwC3TwDg1pIzk6GubbUs+wl8MXkCICvemzEFTSG3yW4GH764dNgEWEDrEqeiqeTwIFa2EO/Bz+NrcBdHzk9D0yoKJTn3NO5o'
        b'wNcA7g1jpqPpIIbtZfn4WfwCuU4XSDB+dS6au54cZPnTQQK55OSpUoOPzEPz8FYFqz4iKpQqF+QsaZ2P5pMdeBfrPjccX3ZCh4z4YAbKwNsnS5Vf3AiVKKnMTPYvQAvI'
        b'3rkM8AVk3zon9GcePpmJMmNCWabWbXZCZ1Lw6SyUhY/nspHKqMcHCO0M3ozvZKNs0EUvSCO1PSea0O7gVlMOysGvLmJwjMXNenINwF5RlotycccTrGrXzEHkGkCNLzfm'
        b'obyQFFbDhiQQZK/RSTgRlI/y8eVQlp0xGETwawDzsNkmZMKncKs0fnuirUC/4eZZEPABNZ5NZwCOxE9jKK+mA0VuFqJC0jyZ1YOP472DqQ0QlPKjC9HCmMEMlKWPqUMA'
        b'6hXkmSJURI49IZU9RJ7eGEIH+/zqYlRM2rWsM6CoH8e7QwDw6CUlqGR9jNTzbRvIqyEAd0HoIrQItIZ9DMCVxIMvhNCxbsN3F6PFuLWEVfKUDl8PAbhd+OUlQERBtwiH'
        b'3Cm180IAZnxv0VK0dHicxEFvkev4Am6jY0OaHkePa/Ax1uKcGHwRtwHUpBmfKQWGo5e0EPJyCW4DqPGeUU8AjnaI9s+//vrra0EKpBnzT0rwDIlzRkkr7M8hU5B9fiSl'
        b'Q2nTzHHI9lTqp8j5fXgy/+DImu0zTEJ6xPwXqlRxfx+vehv/7crAEa8dSHktVGMY89aTzzY3r+Kfa9X+cMcqtPkXM+p1pnTtR5s0i378YtP5fctv7rE0bBj/mvrEcn0c'
        b'fvVOaXvpLJPmmUnv/f6d94/NG/S9cbNuvl/p+cXGx4/OUv3B+drIeVtHJ26bdvzjjgnvvvT5/jE/yP7X2z+8GJd5epV1353Dv7z9m13bt204/a2q6xfezPxgyEc5E8Y+'
        b'tWZ7TPT6/zTsKQh+fPyPrV+ffe/Fd36y7FtVl760fD9t5vqDOZd+4jr/6//31BfcyqXTXtoZL5sSJizWggBroia47UG43cCBgAuax6UEstvFFCNPlqPTVMAb5ic/ibe5'
        b'KLtdg18eBlIcaM35yTnUQBpJbguF+CLxhDQw4ZicSZoEsu3W3GxqMVBN5Ufgk4PxdquLyoD4RVgw5534YpYpOYEaUcl2AQ0gO4SJS/DlhMF6Za+ShqI3sSBA/giT5Q93'
        b'hZkKw0z4MFAuK2o5BUi9IIDwURz90X6lUilAMIilOUIYCCYRIBtr4a9jkK9OvQCiibuiP4mEc8T6hZFBjHn7hJEj/RgcqNk9BZ/BmwOEkXy4wN0B8gq1AevJJiXeTa7i'
        b'5x8giVBDKAqQRLiHlkR6tbT3lIXVkiSyjg9F0NU1c8xl9k/Uy2VJxJ4BEi6IiSuHl2mzhRQkUdM7K6InpIaTVknILbfji7bfD/QIznnw8IO19s/KSl+7vOP47nNNx5vO'
        b'HRj/zPiDx7NGPaOPfSvXYrJUW3cprsQW7U83rHq29NmwN4f867rq2PS99mND3o1B3x8Qem9qlJ6TrFivTMT7ATUN5DkfdiaXa3ySaj9IMkRCEqfL4a5wuUFUNTuslVYH'
        b'6E8SwmjpYGxEvAbQgcmqgwMQQuGEwv1jxBA/RtAXN/sxYlM/GJHGuBDeXD5inR8nUoz6xHyjPjknH7em5OTnJueAzgQaKN6JtwSTp/PJpQfiRlcp9eFxo4eU6mugK26o'
        b'TJLx5AJuJ80hDhCqcAeiOv+BwcMZflS5J6JqtFFFRZu1WXPRAtsf2p4TnFPg0Y/Q2s/KljFEuNK0iqsI/mjum6NeCjsT9mblm1Fn7Nuf2TvqdNTHZc+GqSIe2//0hFAU'
        b'tjUkfkQm6DGsye1J2T6ylF5Opx6fWeEaRkfx9ghy1qfISFoM2R7BFJmX1smz2DduxHZTYLpiRrCEGUEaLgYwwxEXiBcVD8SLoX68oC+20gqHM7xAX/SDGeNpn3bWZgbq'
        b'LVRnwddJE9NbAlFjLT4XRFr0sx6oQgvdzJYPr0L32OHg+kANhgDOIpCsgUCkqi6rJqzJl5jsgRrQVIDFpo5rWNgRvkLKDBkuMEhTVzfZzrpWI9vbpUd4J90J2F4Q/FnZ'
        b'H8reKq+uvGD9pGzGz89aEioMaZ+ULX3t9o6RQD64typzLLvKPhH5H76t23B8uXqe2hlcPOHk1Hnx80YWFjD7+UJrRJ3rhl6ycpPt5GVyEr+Ql29wloKClMvhq6Q5hinC'
        b'g6JGAkMk21IK8km7KRtfUCCyFV8YVKSYjF/QP6wiHFprXeMyi26rWbS4JOSJkJAnIhi4D7PIgCrsGOZHIYVXQYt6g+xWiwhvrX2ABYbC6hjhRyla0fYAlPp7P7rwKDoE'
        b'L4QOJ210rw+3FugN+Go+bi9g+5xjyVVlKbkaXCEETLIyEIfmSjikYPtwSo+qUiXjkcDM3wrAI4HhkYLhjrBBURxw3xce0SZUPfBIKeHR5HFp6FcT3oG7skjM1UgoMzNJ'
        b'iXTRkVTnzIve6Ea2pM81Cmc5PAlfoh+29UroplSt4oPVRanp730n7HrHzh3H2oq8i4Zcy3g/qu33/7j/o2nJ91ITYpTf+cFnZZknv6OOO3g7IejKoJknbs//7bsvJ66t'
        b'nXmu+bFdz7+fNu3zKTO//PqdhKU/vF4x47FZJYOHfvceiE9sp2UP3o13MSufGvHkOjmFT3CL8NPkMiNTheSV/NxsQyE+79tABr1L2sLZTFrIK7mwkB+PgdfbCzikIVt5'
        b'3DxyPBOeMsaSG5DfkoK3kYtA5RT51Ca/P4i1Snbj0yAzteXjC3Qr5hDoQM1cJm7G2/qTm1R9PuqOvdoqazfkHSIh72BAXF7BUXEJhCWe5zV85FcKlUPnR2MlRWPAXYqZ'
        b'XlWF21VXGUgWe103gN4UJR0ju6I0rfRAAEp/GtM3So+mo/KcmlzILUimCE224Ct+jB6BTyhAWfKQzX0zzDlIFqborjKqVH4DptkDo0PhN7oHRo+QMPr7cd91/QolUPNC'
        b'0F/tayWM1hbqYmdzmxAo+ENVT0yVLY5jgyZ+IsBolJVpFaOekjJ/6A5O9VL/jYgyQ2rFSinz97MGVp5EWXSVLPtolmw0GL9mWNFJVA/IWDbzfxaNlE0rGyaNGit8ny6d'
        b'tP+6ZJvD+kT1qIlUytOV2Y+kysR6OUqITOaP0dbLwxpkuxAf/lhqqPA5tWNE1i6zSpkvhMxEhdxfaEOOhsgwKXN45vT5+egTCmfaYFWdlLl2zuC5/+bKaJ2NxolzpMwr'
        b'C5NLTqDL9PVRNRvkLW5jUkSWh5tDB8SuLdNKmYcT59RupHNfD61vnCRlWpKV5du4CNojw5x5pVJmR02osQWl0joNI1bL3VxVGTf170I1BWlmqsYuZe5PnFz0HPc+7Xvk'
        b'yqENUmZo8cLIYGEObSj4gw3jpUy9ybpGJ+zgoKHKc41yyR8sqpx+gNvPwesLNjhlQ1lIUYwrXlhK6xz66yzZfvVHd/ic/fxUOnR5X6WnSJmvP7nOPgJ9wgFIqzU58sQt'
        b'HTthWYvwFp3Noscei5CnWDe60Ma10Ew+PTEY2bQXtymd4wCvl/3Wu2hnem1TakTGt99XaE1BeuW3/7hwXdsyyynDqIzEtktvJk3+kzFTM+iT7HXbjpys2Hds9YQNH2ys'
        b'/Eo5MmRF5IjEs7pfWq6nK9ybRiuewU+r3y6MdG1yoJKw2x9n1+0PVsfce+1vG8M/+OviH89a0/qcqB7z/rmlSUVLZ/xqRdHFiinZP59+ZMRrv/t8zgr03QNT3q9P/OeX'
        b'idZ7xz/96E98nLfQ8uc74iLHq+Pa714b8uq8vBdPXE3NNi/Pu7Pz1Mmcn5fPyD6/+Q1H5KFjOT83HZrwxZefxK97o/x07YG1W9a33t/zrPu9E8vGlc40DKx1O9+O+cmv'
        b'a4//8ehPjiwp77j+7+v//ucP/4p/Gnog7u2vDn/vb4lvpqT9++1fLvvWz+L/35T0yhh+/9XBvx789e+SjmZ+//kRG/9uu1I8SC8wKTETH4jrzuZH4GuUy4+bwwjwqHJ8'
        b'JteQkAWCFQeq7AQNqMVrI0D3ZeLn5RkTk8i25FkpiRxSuDnSivcN1Yc+gMA++NIP+Q60slPyXG6pXWmurrPbKLllNHqxRKOnaQSg0vA7hgkaEZyObfVEMKEjktcqgoF2'
        b'81yw9CN0+yvd/U4xVAtUHlRioPCgEo/203eQdNdaLY4Akt4Px+EcY/zUnFZxKYCa/ziqb2pOnU8KgJnelqh5DtlK2oAPdpCrzA1kO2nNgxkzqNAsckVFbpPD+MUe2opS'
        b'/uushIuVuuehUl4MYaZ7HpQiXhSag0oFq0JUiMpm1MSVKuFeJd+r4F4t36vhXiPfa6wKyiUqeTFIDG7WQE6QB8TW0mCmNGm96nRRdFidTlOFKgAWjfzLGMECymkkvyW/'
        b'H1OlRuY3qhYN8Bs18BsV4zdqxmNUG9TFAfd9KWmUofVU4JUmZknD9+pd+iXFcDcSjRzxlOSR8tOKrxVOF9z9Mts0bMuVATg1QvF1wd7mYs8b86PSle8mbJpf8fzw9M+3'
        b'ZF3Sniv+ZenAMU85Z9zNHXjmzn7XB8cTt/45aeGIjLtpw2/xv749yB7r/ccf8mY8+9XPli2Z8vQXjUdb8V8ytmvHCaGHtC/Onzrh5N/xbw6FFhy4NeKtSyMmzfhSHywJ'
        b'M5vIq/iUtNTwHbIHlhtba0+OYI8XkUMr/K4u+B45J+2REo/IrABl5PT4JGMF2ezfwOUnFC5hK3jelMeYLxtpH/w4rZTc5XEreXYmW8F6fFeZZMR7YpMl48EpPlVbxixT'
        b'ZAfejq/hNrydbM9NxkfIPkhvV6OQGJ548jIZ+ZiGb+FzuK0A6AdpT9JnmfB5BQoPElzkFbJP6tUxhK9CCRDUXiXbDPicAqk0/GBy3sUaUZMTZD9uSwEBzzgqJFty/Isk'
        b'pwXyNL6NL0lVnFjugiJGfY6DHMtP5lAIaePJrUb8TE99QPPQZKaTjKjN5lprg9nM+1flRhDe5T3iGLZRRx1zVPLPunAZt43yexJB0HiFCruT7cmBEmxzrfVq6uuo94Bo'
        b'9aqcLofV6vJq3bWd1pb+1BqVg5rGHNRNVdrl09ML9VR1JPkpyTi4fBVASZ4d0icl6QFzFwGQk3/ponDS9dmIVkiWMc50jvNqzPKWJNwrnFZ7ZafzhDSAmpl2S025aJkd'
        b'CrU4qH63LsLXnu/RQzVYBQ3qOa/STMfPYfS34m/KASIMCvO18ih1Bpl9s9FnveGPVG+lVK/aLM1tn7VG9FprF5l7OpKMVEBN/w+kbfqPR92pn2Cy5bxuUDipKS7vu9M/'
        b'K/uk7O3yhh9XV2orf5WnRgP/ypPoF/QcMwssnCUt2b3TAlYsmijhOd/rGgq1OQMMiZ0ubRvhJ2ZdtA8bupSS3G8EB+VyAYshsAGjfygnwiWS87lzbIKfv4T1je69Nwgs'
        b'gP7ThwBKm6lnndnsDTabJS9yuNeazavcFrv0hC0vWMOOunqrA7CRLUO2KjvX4kTWdeqJZ3E6K6x2u48YdF/Q5ygCSsWgCOsQ3ev+Nx0nujWjUQLoX0cO0HLsh+d9bsV4'
        b'C2525pJzedn6nGSjCgWvAOI7HR/qMeMh8l/nVi6AzXOlQofQEd4RAb+hHeE2vpKHO/lH5NtVooGKAQFuwxHAgqkgEAQsXWFVgiCgbkbA9oPaeRAGlGIwS4ewtBrSWpYO'
        b'ZWkNpMNYOpylgyAdwdIDWDoY0pEsPZClQyAdxdLRLK2FdAxLD2LpUIAsGBZFrDi4WVMaRnsiUpFjSDvHYNaC+BInDmXiRzi8O4y+aw0Xh8PbQmkE63m4OKKdF5NlA40g'
        b'6sSRrG8DoPwo1tZo1lYkpMew9FiWHii93aHu0FQKHQpxXLsgGpmgIp0HoKMV5gmvDBITRD2rMQpqSGQ1JLEaokWBkZ8UEIYqGAW9Hx+sC/gn50oHFbo80au8ChsItl4F'
        b'xcXeUM9UoQ6YfLp4wnxLvohSE0mqCqIDKE+sz088rDJMpjJqJmNpgMqoGZXRMMqi3qApDrgHKiMwKqP48AtA7S5g0n/ZtTaXzWK3raMnLaqtOovcKRtwOkttBT2q0f2V'
        b'6fUWh6VGRzs4XZdhg7cc7NXsuekmXZ1DZ9GlJbvc9XYrVMIeVNY5anR1lT0qov+s0vsJ9GWDbm72PD2tIiF93ryCRaYSs2lR/tyMIniQbso1zyuYn6E39lpNCTRjt7hc'
        b'UFWDzW7XlVt1FXW1q2HlW0V6goSCUVHnAJpSX1cr2mqreq2F9cDidtXVWFy2CovdvtaoS6+Vsm1OHbOpQ33QH91qGDMRuFxPcOThoTM/ncFF73znYXzDCwoP5WR9vSwz'
        b'bOl9OQFjVFyQPGH85Mm69LzCrHRdmr5brb32SWpJl1BXT4/WWOy9DKCvUeiO3CLc9Q7xw9TjY9RSXb7UN69PYtBSbdL9N6irh6m/p4lWa2IW5RUbmCEzDRQzIz2tkruE'
        b'tOSyEzXU/obv5cYyA8aoUdvKMJrKo9Qy46qaVchNN4MaakFKpubMQtJCT8qkkNZCshnUvZaCYqmWRVl0qzg/PzufQ3gLORFEbk6MkCxhVaqJRoFZrfJuPBGB3JRO1E6O'
        b'p1vPSbnU7TJvYZYsqIOYTnbp8TnUWFScrib7yKFhrI6PE4QN7zEVrcw+YKlTMrV8Hq5oTOeZRUk7Xh+D3MmQGVoFIn5AzaSFHqUBIFOKssiWPBWKwLsyyWkVufIUPsW2'
        b'Q7WPVThXKVEZvoLIdgr7Na3twshrPPMqyGz699jtM2rnjo/I+Pa/7m3/oll3emRS2eA/PD25aEhSxo4E7Wlb+ZYvV+/420vfmb50yE9MzgWzGxpPP900a9f3Kv/2l323'
        b'XlDsfmf764XLL8e3PzX9J4fa1etyX4wfFP6P5f9Mr908fMukN1MO1uR9//t/Fidn/Dr6F/Yvhq/+W13b4X/MnPvY1C8KqpaIRbX6ieNf/upqw4WXs39t3vXcB7/56t13'
        b'jJ+X/1r4RYN5Wvj3y1eo9x6tiNw1ZUfIUsfg849PuhRnHjIl4uOwe7uXTbx09Ts3fnujxt409FsfHP3dlZz5R/+jj5R0qGtCYwiMkD7fnZxItqTwCMasORp7FBq6q80s'
        b'4KZKctHvemBQhfo8D3DzRBcVdvBe4hmba8zJN2TjdrKdnVgiB3AHGoKvK2qLIpiOh28uwy345dUBLgrJ+C655aK2ZBcf6t81kytA+CjZE02aBXJ7ANnDdDlyirTiPV13'
        b'DPHtSLpjGBrropJYCj4dDPBDHUmEnoiSt2dzoWvbJMcFcmN6Jr6iBpVxUxqDq2ByuWS7AJwYNEiFQhbyZNtafFnyKj5TG0p2kFdwmw8qJXmOI3fI+ZmS48TtmfFUuZTQ'
        b'6bxADnJ423zSzrTC4XrSTO7i5+jL0vJSkjs8R/ZkM6+MBeTOMr9iOgIf0Ps1052rXZSX4stPkN1U82zXs7Nr0uhKNZGXZiXha0ryzAYYQTa8z0ROYrXlcQj04CMCOcrh'
        b'HcWrmQqdFZENz4z5KkQ6qgVyk8MHMyqlIb2Nr62mAOYz749N+BI1w4dVCdNJ82PM8XkOPku2wNtUviPP5VERL2yesGDoRNaJanM4fdsAg2wil4Oof3AYPivMx7fIed8O'
        b'XNj/2tjWXZYH4dgGXF1WiLN8Yvx4DfNb1fIaZkNTcGG8lovhqTVNy0ku1dR1RNXth6cyOv35SqUCtVCiuEZfEyZJXg6SlIDH6GUO8im93aTtThXhobV8vVqqJKZr7azO'
        b'FH/FTB6nm3kjuigYH43rW8Ho0ZGH0hmrJYVaaaayT58a49IALVpuxadF3x9b4heUKAsDocLHwxIcVouYXFdrX6s3QhuCWFfxUDA1SzApzOW2ij5BesIH0v0xFAAQs/pt'
        b'/9EGg8m4fbX8pL/lpP5loUcHgPbcQb2i+mzc4m/cGChI/W/aD5bbX8HJEOh5WHAWSV2VkLUvaMSuQ9GfkPVNQXEU+JdHX1BU+aFIeRjx7NEhqQyAJLE/SFb4IUl+sGj3'
        b'TZDjHCdB0RcANX4AUkuYvgJtB1r4dPK06uzseHqfMPzfGINkNe3+iR6y6zyqdzh1tm4r1mm11rDj8aDsMHWkx4v0yLysgxWDzgM9zHA76nSFlrU11lqXU5cOPeopKidA'
        b't6Hz8OLqycY0Y6q+f2Ga/lOintb6Evno9JSw9CRyiWxix2MUczh8nsdbbEeXf6hwUm+xz4/lflb2dnmWJcGaUPRJ2Vvlf4AUX/5x1JtRaPiZJz8Oe3ONSrd9JHOdeuOv'
        b'QZN+u1OvkJjzDfdkH3clR8gFUyd7PVrqYgfoT5Lz5FQP0YmJTefIaXKbvIqvMDaO70zH10hbSErgeXJ8Gz/vor1ygbB7IJeKMWGFiH+SSxlS2J8tTU2NVr7TS7Kr1Ua0'
        b'OpiLoXZcmSPIZST+6ZjUvbZOwxndDavvwtd29WM4614/SBlz4LUH+FFR2wLycI/sR+VDWU8PDCm2uiR7gtvusoE2LVN+t1NWn1moCJfDUuu0BIR8KF/boyJax3RmYZle'
        b'lg9loCr4Y6myOsoeoOTRfz3tqLIfzoIJ29BQ7mw5l1pmOr5mInJPhsw1a/CFHtpbSwE+kNq38jYgzaZf+7XCORXeD/po32dlOYDIhqJPyz4pW1H5B/H3NzLKFD/Qb/2p'
        b'ISNxrFY/Z/XAwlNN046Mf4YitICSTCEH/xWq5xlCzyF7VAHKRhDZBPoG0zXIvXAX3Usg+1YUAsofGNqr1CuJvPhiqeyI9aDdV6fVZfZND2Pige5d9IfzyYbrBvvQqsc7'
        b'Jl9jTByjuNa/uxcrkeLHbnouc10X7G7p2+GrHzAeRVQK6/pqn+zh2a786WEx2eg73kUVj76dz+hASE461Crpd9R5WNczgXFaxYeg0PQ06vlXX53DVmWrtbgATpvYF2ut'
        b'tTbIxH68cXwvppO+7UWiZJRhQ+BzNYWGjLoi6yq3zSGPkAh3FS6daC23uZy92qjo2gcInHU1PiHNBvzWYnfWsQqkqqVBrrQ6nH1bsNwVEkTz5mYDJ7etctP6QLhJoFxb'
        b'5/BBBW1luyyUjz+YhPR0CdWY3FQVIcfJrpm5JrqnTwNLJJiSF2ZJLq2kNaWItOQtzBKK9Phctu7Jcodjg408S04+GYTmVoXX4G34JnOVpnFW9nQx8HTWgPBVsmcRLPc9'
        b'HD5FdqwiNzRLnlAwljoJd+AOck0LyuzJXETOInzE/Jg7HZ5EkksKZ5h7cRbdiV1EWgyLAcwjzNegDZ8ryTLQdrZm55EtHBCwU/o1eO8YcqaER2QPvqUtRNlSAJVbWUkM'
        b'KrJJKwNW76+0cEnyYjUq3KgCqPYOst2rWSI4aylJPV6e/PZd6quYsXAjruMWWCJit5za9GZ0RjAfErHl2zGX9YuPXTGMWD5v6+on1c3PvLeh4qO31fNq134SGfFGxrVT'
        b'lpBxO45sWXnuxBPun5wJf/4HsxoXlz5Td6D4H08p/zPj68lTCo9e/MH8X3zBL1+juxW/UR/ETBCNieQgkGyyNQjfzWVOciG1PGSdxNck08mChpBEeriDEkvJhoN3YA9P'
        b'nWQU5MXMkWzzvca8nhpe8F1812d8QfgcU+HJZXIAxmBbCt4DQy6Z3pA2QogmF0czqp1B7nJdTUT2LMlAdBufkrx0z6smk7a8peRQgHBR75CqP4FP5Xaz2ZyYQm02mnT2'
        b'co5xLG4rcAGWUNuFZLdIwscZ2Pjw6uXUqtGylBovJMvFqGDZf/GhHHAoHe2kEb5jrqM6WcBADaj+EhvQysxASqm6UeMutZh8MDBC7yeG/XEGIaBYJ3tYDpdWzgfSJvbz'
        b'Rd8ON/2A9NB7zUyXBtLWJ1s47mcL45ka10n3+tNdHkF1kXe8FfT4T59QnPJDMaNXgjdv0bzu2wO9wEPdoGoc1kqvymmrqrWK3iAg1W6HA7SDBRWKAFiptVzro4QmiXV1'
        b'htZCnhDZB0hbqZUZmaJFCYxMCYxMwRiZkjEvxQZlccB9ACM70C8jk0KLSfIf4wmBmlDfe1S0bxJH8L3rPwjR93YDGwnpLfYKjCLNs1Cd0KibZ6mlCpdFfla+Anhbr0yN'
        b'7oQBnykumDo5dTzbA6P7UyLVc0EX67N5/wRM1y2wW6p0DdVWeYcNOkz73FnC16m+mq+tc/XSjMMKHal1Tteldxesy+TuPARX7KnwBZvcGZQmNSfh6125Imlh5lND9qIs'
        b'yCqSWRxHbpAX0yLxbrybXMsl13LQWHIqjDxH6AFLqkRHx4bmGh1TkxNzgOwGVuKvPCtnUQINaZGdZwKBnJwepiVnyQlyUXKELc9GO+YYOVRWlvNry3DkpjrW8MjVfgEf'
        b'mPDhTiEfJPzknPziQAG/rTgIFMS9E9z0EBK+hPeNIm2sjAafYEb0bMpLkxbTgE4BGzRZhpw8Y3ZyogqRNr12Fd6rks6+HBiU0IXT075Aww18cQLQdhDiDfrkHCVaR54P'
        b'wu01ZLdekGKdbY0jHdAw8cTl5AtIMZvDL+AmcpKFs3Eb8cEk6e38glTqG3aAf8qcxsKSkWvhrqScfKM0gBwaiNtmxQuUN6ptJ8b8m3fSkztfrygd9u7dUJKqVRQWmdu4'
        b'tGc8b0V8+sOftW9CjoERR3Q5r/9hx1zvxI7nkobXe3aXbHoxvvLC5wuyv/WX6VeXPrnonZKU4+U3PR/97NOrB2N+cOaNsFmGD/7fVxPjx+xbsWZ3Qslfc4u3fjf37Bdh'
        b'iWPen6v+xf3qlLeHfzLkxvvpe4duvPn77esHpwzfcWTjnoNJGT/QAj+nZ2L1+BBpAnab5xrDIb6cG+8mt9kuSj1+XuzOyfOX+Pi4plzakHiaNC1m4gDFlOVrfNLAeXJM'
        b'ClPyMj5ryc3OTwT5asR6HmlwG4+fJrdrGCdXrMJ3Q3LxSXwskJszXu6qZDsFuAnfKcnNRo3+OHou7GFsetECfJluqlAH3LXTkMrOj6I7QKxeM76KX2ROugWAtWRLvgEm'
        b'I2JmigD63ngGd8xUfEveZiCHF0lyDNtluCsFutFr/4+2BkIoX5SpBmP1xk5WP1HFolpo/Iw+WP7VskM+dBeA/0+wct3AQB4r1yUzfJXEuim1cIj0Yu3K9YMezYlYIdXE'
        b'Kknx18lYYBVcnu8mGPxsVN+CQW9AP4qbmMb3Up8M+S0/Qx5JOQfQVcZH/Iwn0HqoVzA/Jh5+uQX6GAc1Pjjo/rGDmhGoQ6NYV2E2sz0NBw20xvY+vAI18c+hyV62V7xq'
        b'nxGaWoyYYu0N7aroUmkqQMyqYm/5+sUmcMD/0WZUXwjomAWXwXTeGuFGwysUUZzqawWdqa+HT2Yo9l+V8A3/KsKCtVxkMC9FCVIEc1Ex3UtEcroR0r3kn9WyAV9z4qcn'
        b'5ZmkjUYOBa/jyTbLoB4ML1j+6/xvN/8skS9ViEKp0oZKVaKiVA2/GlFZGiSqSoNFdWlIh7JD0xHRwVUKHRGipp0XC0BUCvFEVArM9Zp6HmmtoWKIqGV+WGHtfGkYpMNZ'
        b'OoKlwyE9gKUjWTqiI8w6QIoeBCIYdQ4K9wyo1IgDxSjqSwU1RnaEQbsRYnQ7cxNn5QZUUu+sQXKJgVAn9cuizuBRUIb6aQ0R45o1pdEAGycOFYfBfYw4XBzRjEoHMb8r'
        b'VBorjhJHw9/B8htjxLFQaog4ToyH3DjmS4VKh4qJYhL8HeZRQU0GMRnKDPcguDeKKXA/QkwVx8NzHctLEydA3khxojgJ8kbJNU8Wp0DuaHGqOA1yx8i508UZkDtWTs0U'
        b'Z0FqnJyaLT4GqXg5NUdMh1QCa2GuOA/u9ex+vpgB94nsfoGYCfdJniC4zxKz4d7g0cB9jpgL98lioWybEcR80dQcVGoUFUw8X+hVpdcwh7DzXSQluu6lB5JPmBSyFoRA'
        b'GjOwymGh0p8kulWs9bsndXMC6uph5oAKaqwuW4WOejFaJEtphSSBQgYVKqFOycBiX6urq5XExN7EOD3vVZlXW+xuqzfI7IPCK2QsKjLdn1ntctVPT0lpaGgwWivKjVa3'
        b'o67eAn9SnC6Ly5lC05VrQHTuvEsWLTb7WuOaGrte5RXm5RV6haxFC7xC9vwir5BT+LhXyC1a4hUWZS5dcI73KqWGNb52u5jFumyfULrQyDuDKfldz7dwjXwTJ3IrBefw'
        b'Rv4Ydxw5E128yDfyMYgGIW7hGwGZ13Oi0MitRo7SRo46P8Jb3DGBhi4WVYOhXCyKQlPQeq5WA8/V9K4F0fcakVkBtSqPA7E3q0QNMxEGfWjuTRPp7icnz3Onm1z3F/qS'
        b'79lISNqFRaqD5fRj05KGbDrzRCsuSJ6YNn5KIBqJoJRkV1JhX+est1bYKm1W0dCrSmBzUQUCOKDPI4617NMSJZQFHcVhK3f3oVRMp4+nl4nWSguwFj8alYGWYquoprXb'
        b'pHECZJTbAQTr2bdP6Zzfj7bVsn2rzt7Ej3XGezmjl0v9lPKMT7+Gf/cFY2qqSa/2RnRvlu60WOz11RZv8GLakwyHo87hVTrr7TaXYxXlbkp3PSwThwMxCwOTISiCOdaj'
        b'fo/PM8b7S8qmohjtVwDLiJKNHzqeSkXrwiUEeHT/AT3HQOtTjvin33vA14TfeSC5O9KwqVtbb9WVwZRUAKe3G+dLf8vKjA56QOdR9kod/YH1uV+8iWMuDL0jYo/meF9z'
        b'EXJzdA2v4EP8opXAJsSrsTjNzGfUq7Guqa+rBe22T1C+9INSwVwK3DXloB/DUMhjoKu3Wyrofq3FpbNbLU6XLk1v1C1yWhmal7ttdleyrRbGzAEjKZaVUSy1iCvcUJAW'
        b'6FpLz53ergegOBadwh9p3H8AimN2/Ifb9W3WKz78U29EZ1E9Fc0kgmNdU1Ftqa2y6hwsq9xCNyDqpM1dKGXR1TvqVtvoxm35WprZozK69VtvBd4xjw4udHCupXYlM707'
        b'XXUgODLyUPtQpEAmAz6QzAykMjrGbrb0JUJDKZLf5A5jTB1qe9nfo3Hgra7quk4+ZtA5bUBT5Wroa3QvPtAtt68+yhVNp5Hkp5fJLLaXjcJ+rSLldXU0Mq+uMtD84mZT'
        b'IXabhl6JZIPVAct0NfBHSzl1KujDENNFxKRIpUDdbSphJnaEEF/HL5HdSclZ2Qaq/eYuoVYKsi2LbMWnVuQWLErIMWQnq1BNpIa8uhS/wBxH58Xia+vIZtAqL5MbCxNy'
        b'kmkU5e1JJnyDnChKJmd4NDFTWUWa8A4WpTXaSXY7jfk5c8PIngZVJArH+wQjuUa2s/0Aix7vD7RdJJiSE3OTi3y15ipBUtXUVeK7+RVutjW/BXfg/U4aD+lZckpy7sPb'
        b'OQDlVbKHRYMfPye7GLeTjkWknexZlM8hTQEXgg+Q6+TYk1IkW7y5jmynICmfCEMC3s/hTRVL2burysh5vH+MM0sybeTiSwo0AODFFzbo2avW2S5nQk5FNFWjletp5Odm'
        b'fK7ENqH0fcFJjyGnV++Mbp9RO3ehdv4fv/wtF1SSVZdyqkL945Y3I4uK0k9E7fxF85v/c/m0IT6kbNrnq0d/70DFRVXzNo1XO+nl+Mz/CeNLLxaW/yVqWNrPF276Vu3r'
        b'idbM9De/R5acdHzb/GP74Z2/1/545k9HvZd9Nz/suXf/p/7SmOJ9Du7c1ptnnvmIM31pOW5T2YJ37v375z+Y9rOQKZl/GvHFvzKT9EOn1D71qxUvnky//d/64D+Pa/l6'
        b'57sHX7e1/vE9EvmvwxNrl73613/FfjYl9o1/vv5bzY9+G5R27rGmCZ/rB0hulidIWwMLUEXa1LgDECmZwxczF0kmkW3T8c2kZLKFtOJX+ZQs0i4g7QJBNZjck14+SI5H'
        b'47YUKMEFkRNIkcLha/jGEmaNSdePTsrJz+PIzrlIMZLDh/GeOGYIMUfhU7nZ+fiePjFfjVQKXiPgu2xPoiEMH8xlwHBRoUgxiMMn8OkithcTNwM/F2jCmS1bWCQTDn62'
        b'mMUtwbfITnwtyahPTJA/ZBBOrgpk75K1+Ba+wFpfuBjfYUYScjRNMsOQe4VSLKVDM/Ol6pXk4DCkMHH4coHTRY0EgFzHk6mRJdtgxK0pyVl4B7nFLC06nYLGyA5zjaHF'
        b'ruLdibm+9ZVbgNtT2Ooa2YgSyT0l2TwNH2I7Ny68I1bqKNmNr1FTYCuHQkSeHFzXyKAswWdw+2jSlFuQzCF+NZcOy1gao1n41OhcQ8KoMulQNjslWrLRxWI/7ImPyc3P'
        b'zc03klZDrhz4gbyAN6FEvE2JX0wnLzFLVhA5js+QNhO+aFDhFvISUsynAa2bhj+Cb+U3OWsZLdFBc1fSz0xJ1JNENiVtRGHUmVQyIlGn0yjmWErPZEoGpjDJFVXOpe6o'
        b'7GTmUFni6bURk+9oFjtV+U2cSTnpVSZI7ILL190MSE39HMDsFzSomUqUfXvZsEgzLMQZCApcQKQZnn1S5OE8bapATHivNzFhnsTn5AM8knxIZRpgO5R1+UU0WVqgooNT'
        b'lvp7ciV5a6GbuNFNuOhdmOjJ40p6Ci4Wyhy78HIfa62jPJ/uq6ylUklPyCwV1dLefY21ps6xlm0DVbodEnt2ss/KPJjPd1equgqzAY6QLoujCjQYX8l+N1Jq/TspEpb4'
        b'NlJ88hSVgqzOQPX/AeJA7yfgNZLvEoliIewSUhf/c1pulBx4dn72UDSVZj75DPpFXoUcyWTCLbQGMObYmleq9y+asEqKp38cuHCzs5IcCw0FDCfbELkYGerOYdQHbyMX'
        b'AqgfEy182zY+bltCPQCWAOOnWzA+hwK8W0u2ADFdNzxiOn4pzpb+x9288xzUObjqvfz2GWE4NWJ+1U/CImYP29IydfG6xCTlnwzzb9g03/phPR/8ZczQTU2Wg8/+6Z1P'
        b'2hdMG/Xh699d8b3fTHOtUIsfB604kb0/K8L00pW5V7L/oqk4k7H55Iij+7a9HHpy8qo9370567UD3vdvm479sObM/V9dmPLhoqz603+5Z19eXOQ5UDvG8K3TwzPFoy/8'
        b'Z+GlP92981WVY/v6fzV/dOnij2YmjH03KevJd2cee3kj99SZqR99W9CHSZvqHnx4mu8YxjB8jjoDmDcwXjoZn+Ny5WEgd8kRKniELxbs+MxQxjtM5Hl8NJdsc/RkHzLz'
        b'GFArsalNIzANBdE+SYq3RGMtFQxhbCpLlZSLL+AD3XmATP9xayjjzNGN7txocqbzgz4JZLPkUHATXxyUVDA13R8OJARf5ckLICR0MIY/snIstHyLOoWk+OIx4dtkJ3tY'
        b'mkBuJZEDU2TOy/gnvkxOSbzpaAZpxm1Q/EonFw3goEfJZXbMhLSPxBeYtJoNwLOxILvwVd948OQq3sKZUzT4FL6EJaDIdrKfHE9ibhRKpNKWrOCHkwP4AJMIyNN4hykE'
        b'WHdHbo+NmVD/QY3mzCRDPnVZaYXhayLXc0BwwLsFR1J+b8fzH5bfqWUdgnG4mYEcbrLE21Ts6IT2a54P/i/Pa/7LCxH/4RWUn9EgJGGM30neE2HcujCZiciVdvWdW9+V'
        b'rfUTjoSXyna6SYDMhxKgLueYTma2CXn7jjPVHZIeejslQExvpxNK9Xb4pRa2ISLn4uFeaOJioIDId0n5wnHe58fa7ivGGtMqoXMUVq/WXFtnljVrp1ewlDslQ0wvOr43'
        b'wuzfLJcMljm87zg6D8PIrxvks710K9fDqujfpc6DSwv7jEQT71jQyLH+oJWCYw7tlyOxkTtG+4GOc+u52hiXIHKNLE1LVgqSrRHuFfRTFIwT86b78X6+WmNzAhgV1Ywj'
        b'jQWGQM1YTLOmNzCTbAgG2mrq7bYKm8ssDbrTVlfLZs4bVLK2XjJesUGRLVVeJWPfXo1k+q1z9OFuHGaud1iBrVnNrPxCXj6TjlgcWBUMGMVPigXron0D1+WNXiefDRul'
        b'VSI1lsJQUHPpCq6Sj0G+AYiUakugnTRIXXU85Z/UsK5QasxmaNNhNi+j8DFBKdCIJj3rGw0jGSQ+RJShqKRQqCmawagHNN0Nn9RmGkPAzM5D+VoO87fMHnWR3Oi9wtdw'
        b'LMP/Y4AJInecX88GoZFbKVnzoHlu5jnecRTJhkW4Z6vycC9gqMxmu8tsLudllo5gdtaF+uGgzx4ZDM4HBj9zluM0bepMHy1bzebKvlq29tKyHweMgUtnlG9RrOTrdBIM'
        b'K7iV1KbF8umddCznKR8sfSAtgGRdZTav4H0u8gxZg4GMBgBGS/QAzG9R1LIhoY1qfdZEqYE+hqAWulkfgAKd7dT2NgAPGnqFHwNm9zvyVTCvzj5GvuqbzLnSt/742f3P'
        b'OWgn5oa+Wrb2str83vJ0aH2r3u8WF0Cwe65tajMzm5/qdW1Lz7r0s4t8O6bXfg6i2z+IkWG+iff1mUs6J3QuN0ZYfRFIDvtzu4EH698iimbzBj8bYZpnAA1gj3tdAgGY'
        b'RgE8znWay2/0NfSU1LEam3ondT1be4jhiO19OJIdNFi/43rv3Xa6y83mZ/vsNnvcd7fDGCAhnR2n2xeOm/11m9XY1nu3e7YmoAA6Q8O1+OlMmAsxmgLpqJ4dp9sG3jBT'
        b'nSsbOKqVHmWyip34wAajr6M5ZnONG5BxGy/vgCAmxHUZFVbgkZAB1P97/Y0Kq7Gj91Hp2VoXZJgZOCq6nmgR5x+nuG7jJHayqJROJOljXELMZpfDbRVtq83mfd1oMg+j'
        b'E+kH2F/sm8M8xA/zkN5gbma0LeXBQGuBpdnr6hwMnKO9QD3QD3VnuW8Odowf7JjewGbCCDf2gVCrWcAis/n5XgAOQMK67jRCEQhrIerKlDthdVFo6a44wNV5v4xfz68X'
        b'ZJiFJgq9IN1VBqKKVwVjBE2D1M5o7BsokND6FBVKaL3Khuo6u5X6C9dYbLWitS/pNNhsluo0m1/kZaIi9VjL0+PmwV+vG+Dvta9k3xIplQMlzhTCJsNPEfqWPFl4uCqz'
        b'+Xav4h979DDtBXe2V/2g9urrnGbz3V7bY4/6bi+KteeS2uL8NE/eKt3fZT76ah2UK7P5lV5bZ48eie87LvfTkq0WBJjXe22JPXrolqr7bSmILWALVPhGQFsRgaubPnQ0'
        b'oV5ssF3WN10lK5EjwgWaK/Mf4URBVFAmMwgAWU9XB9UE+Rb+uLRe5FXCQFSaPqWV3h/F9o1ttVW6+roGaed5fKrkf+Gur6+jIYfu86lGLzceVkyLb8q8mlVuS63Lts4a'
        b'uJi8aqipyuYCndi6pt6n/vVpjoCRYI2bzd/uJB8aFh01LHBE5EISb6LDok/p5mToWCHX57TXuWhQM/o9Q29YV7s2pCsrrRUu22ophDaQXLvF6TJLFluvwux22B37aG0H'
        b'6YVauSV3RT+OejV+pT+EmUilHVpmfmfKr4NGxpaozXF6OUkvz9MLNR46ztPLC/RykV5epJcr9MKkr1v08hK93KEXxoRfppdX6eV1eiH08m16oTt/ju/Qy3fp5X/o5W16'
        b'+bFvjPWR//+4P3ZzLqmDy9t064E6XGgEhVLBK7iAH6CLUdF9+DgqqSPu8Hjq4xir47lgVViIVtAIGoVGEaaS/moFrVLDfmlOmIb9BEGu/MMcx+PwuSFqk5NsJe2S36Mm'
        b'lnePzu/h9qiQ/zrf7+b26Iv5WqlgEWg1LNgci0BLQ87JweZYtFkxiKXVLPickgWfU8vB5rQsHcrSQSz4nJIFn1PLweYiWHoAS4ew4HNKFnxOLQebi2LpaJYOZcHnlCz4'
        b'nJo5USrFWJYezNI0wNwQlo5j6QhID2XpYSxNA8oNZ+kRLE0DyulYeiRLD2QB55Qs4BxNR7GAc0oWcI6moyE9jqXjWToG0gksrWfpQSy8nJKFl6PpWEgbWDqZpQdD2sjS'
        b'KSw9BNKpLD2epeMgncbSE1h6KKQnsvQklh4G6cksPYWlJYdL6j5JHS6p4yQq1TGXSVQ6kjlLotJR4hwmcKV7w+kBm5LOU6wfXu6+0eQ76BlQSI58160Yddlg/iMVllpK'
        b'FMutspecy8a2eXxeHiy0ms9/jjp6SPsp1q47P/J+U1fHDqpBBRy5LaMk2CKdERLrKtxUI/DX3KW2OoevQptLMqpJr/q2b+al55fMl2so68O5r0siu1L2UrHoypkJEKqT'
        b'dt0CjwQbpCZ9fZUdOF0OKx2QLvVZnMxflALHfEdWQ00Wu13npiKWfS1lOl3OGnd5uQu7pRofJTc0jJWznKO8zxFB+d9g1MK7OUesjwe6mO3zOLdeEIHfmaWrgl2V7Kpi'
        b'VzW7atg1iF2DQfqkf0NYSsuuoewaJgpwDWf3Eew6gF0j2XUgu0axazS7xrDrIHaNZdfB7DqEXePYdSi7DmPX4ew6Aji3YNaJHFxHspxRjfyx0cfRfLR8GUi8ivXKRsUx'
        b'WKPHuR2cE2hPo2IQWq+oHcJyVTTXMUZUA4cf26igJsX1Ctc44PiKJh7Kz3TFi5pGhWT7dSXQ/EZlk8ChVX9ogd6tCGvhWLllOWgzQMDEpSCTg37a4/4kaQH0WC79LwjG'
        b'IhZ4ObOXN5vvK81jnWOd98d2r6TaQj2rOp2zJMOr3qstAtZvq5GdIFXSBqQUBFUw20Sv0uy2uhw0Vo10EsIbLoVe9x+Ic8ynzIl+/dZBzeUOGiVOip9SykSDrucpQfyT'
        b'dpqhxnq3A8RaKzTBxAI1s8a7LF6VucZZxZpeSc8YKs1W6Q87cRjqe4194Qxeqqimu6QsIK/F5XaCbOKwUjO5xU4DLtVW1gHEbFxtlbYK5goN4ohEM/yPLTWuzg55o8z2'
        b'ugqLvetxfxoOuZru7ToBPrZmoRr2VwqT7B1q7jbkIMzCepTLKuG+xukNBiAdLid18GaClVcN80LnxBuW7psZaSbUTquLPtCrJO8DanXwqlY20M/BBwRNaEQPDtnAZvMD'
        b'KviVMsEvgvlXdA/YpemR08cPL/2NYGYhLfuSMr1GcusGdRuBR4o6LVtEPkGob2/SSFB4JCfX2O5N+b1dZ5YwX4XalZ1nNg1S2AVXnXzWlboaikCqbZVrgQAHEMZHdH51'
        b'zOsP2GgfsPfHdY3eRTf2a+pcnQdsWRTTRwif5cjqr91Yf7tdg3b1bJaGTX2EVnP7azWua28DA3Z1a1aOYfrQx6j6j9U13N+uvpdYXf+LptkEF/fX9Eh/0z9L10mRa53u'
        b'cvkIB3Nsp+3J7jVySKh+4WLCklQR25iksk09vEblEhYUp5cgU0ZdcWdepc1KG5QFBagdCnQ63/hpv1OXKI9TogFubS721xfSK5FtQSZKcbUSH/7suePx/gYrwT9YE3tG'
        b'RekDP9PnLklPgUvGI52Ad3zaHxxJfjhmdjmGTwOOWMu7HsjvDs+8ooz5KfMz5pY8QjAxgOf3/cFj9MNTxGY/gGXLLlk+Z/1uvkJG3XwWGUXyjLI3WNY65TPoulprlYUq'
        b'3w+/tgHKz/qDMs0PZaIP1X3+TgEAy5xZl1C8eEnpo83ZH/prfZK/9XhG3OvqVlKJVjpJD4JufX0dPSoFIpFbOnv/8MQFmv5jf01P9TcdXuI/+fLwTcgY8Kf+mpjRlYLV'
        b'wJq1VFkD0LC+eq2T+rzpCtOzTbDG7Y/Qv3Oc48/9NT6769B2Nmqvq+rapi4htyhjwaNh/l/6azrd37Tk71crJrvqkuFPJ+PWJWQ8fJtyd//aX5vz/W0O6zW6gy4h/+Eb'
        b'lFH3b/01mOlvcKTk1AgiYS09JSIvFSnqRuGiosJH6CU0+vf+Gs3xNxrJaByTkOUDLw/fNRjLf/XXSn4nTehOuahcTV1s6H3C3IKC3GxTZknG0oelm3If/91f64X+1v/c'
        b'vfWu0r5RtwBoRKYV4KllcqHTr3r3Fm0eiNeS7AUlNGa8QZe5eJ5BV1iUnZ9uKihJN+hoH3IzHtcbmMvOAooy1XKdfdU2vyAfVpBU3YL0/Oy8x6X74kVzA5MlRemm4vR5'
        b'JdkFrCy0wMwBDTYn9W2tt1tonCspAsijDOHn/Q3hYv8Qjgog6pJqJCGmhS1GixNG8VGW/T/6a/Vxf6uTu0+cpMEZdemdx9SyTQsKYArmmzIppaeo9Ehr85/9QbLMD8mg'
        b'EsbtJbURplCkuFP3kGtFCmjr+Kq/psydNF6OzsLOPUoNWTvNQIG6yKMw7y/6a7y8K9HrJHbU2VtHbVe9MBWfSwnbA1ksN+g0Mb+3WLY/yByq6ofSe+lkLN3zgF9FE1zN'
        b'tLyS+ckp6Ztmdj2mgqv6OMcFgH9/RpHkEE0tWH4ZRxK5Om1pvYtkRr3G8TvazZX00i2MNLNB0HgGjhrEtlU7Y0132ygKoR+Uk6u0Cr7dRtBzY9n3n6g/5rq47gpnwDt9'
        b'zxS1pok+b6sSqcneponuTdQJnZtUPdRbvztMnyclY+U5coTRfd3jiO7jVknbZHKQ3//SviqoUaJXfzeNbLAw02+jyZ4f1CzQGzBSwb77HRUAjBTfV+TkPXpm6vJBo5T0'
        b'kD7c7+zWWrO5oRs0vRgZWDmTfnRve1XM+MF2l7xh3QxXj/kxpxNp7D588YZ2tVupZLOVWubc7APEXpVsslJKFisFM1gpqL2KxSDxarsYq1SyrUrB7E5h3axSIYFGKZVs'
        b'zdJ0GrMkQ1JYV2OVYzQno49jLL2L5+RBfKhIbo6fw+UH1DJEN7M0giIkMu0Ro2eo+4qq8b+MytHXX9XDRvXQBmsEjdLNAvpuJodiQ1aHpoTUa/U5ZGuSKc9IXdXppwsS'
        b'q5X4MjmGN/UawZH+c65BgXtYIt+M2HcTBVHh/26iUr5XsW8oSvdqUS1qoKzGw1dy0vcSS4OkgB2lwSxuLk8Dd0BuCCsRLkbAvVYcIEZCiVBxIGNjUd6B3RA+zwZ6uiIA'
        b'UEUgGaBoSUmxmTltmDm6FW3mq2ioAkH082gF0wq8Qf6vHMNtTZ1osdMP2I3qbsmkLZoDd06cPp8OI8f2an2VaHx1dKdvdIt3k+B3npK/qDe0l3Ye7WQ8sw/R74P1HY3V'
        b'bzLstbVv8J06x/T+2vP42nsU9j2jvxpb+qzRP+nULcLn/OGrlXeMobXO7KtqSi62BLCcviajd0rfn+8HdKiz1a6sltGn9oBWu7NVuVVG0R+CrVY+mK3ueHAfZdba/RiA'
        b'37uGBi70uU05I13QtOzYz1y8VgrOiXDPXKTYPb1TrBQcM11KaasM0qpjaur5x3V+vO9+cqDoW0PDCJR3RmaI7wZpfNfiYp1VOigvHSBgAWN8R/AYnwDB6BCSFyhjVY5Z'
        b'9G42vTDfEjpDwNTq60Hh9p0cCAloghXtwzlLsIjibiHgvIBGdsKm51h6YdFsmOGdvrEoWMaiTv+hzjnthkH0W8+HAuZ0cG+N9S6W+Z0xo9h6kWh5I5qPmqR1Q8+g9BCC'
        b'/S9R+YDS0eVaepyDSjU7+VXUnbtZYri8I5GObqN0T9eFl3N1x0j6KdpjfpKU3BvsrjqXxQ6Eie5BOWfDDaX3dTX1s/WcV3C6a3qVlpTsraMPGhdWyqQP6y4pdbrgMITp'
        b'xJVOoYLJGPM4eQYcC/yCRj/xUKZBofWCPODAjlXSZw41AnU+oc4lLObAaHxxFHBnxptv6APZM7lGWg0A0XxyUZ23jPT8ynGM/Ne5i+vCo2Fm2Y9wSFkqUP8S6l1CP2co'
        b'BlMOTD9cKIZRjisOOBRWSr9prARuHCkOBA6sZKdtNTQ4lifSM7hSLUaJ0ZCvsqpZICzpO8hqMZbei4PFIcwLRS3GsfRQlg6G9DCWHs7SIZAewdI6ltZCeiRLj2LpUEiP'
        b'ZukxLB0G6bEsPY6lwyWIKgUxXkwAWCKs6kpkQ9aIJnSK28aVRsDzSOiBXkyEpwOgN5yYJBrgPpLdJ4tGuB8oTpPDf9GwI50ffwyDvkaw3g70RHmiPTGeQZ7YymgWbiuo'
        b'NKpD3REjprVz4nTaCoyIwIJu0RBk0fRDieJkeDaDtTNFnMryY8QJbCHP9GopGvp8I7xcoZcr0Cu9fOZcL5+d4eUziuFviZefl+UV5maavML83FyvkDm30CtkF8NdVhFc'
        b'5mUt8AqmArgrzIMiRQVwKc6gD0pzHasZRcrMLtSHefm5mV5+fq4jhxI3Phvqziry8nnZXt5U4OUL87x8EfwtznCYWIF5pVBgEQCT3WXV++KtMxcI+UMHUkQvhT/auuKh'
        b'oq37DrY9RHRwhYkdpS3GL+HrdDG4SGuBkbTn0yCmnaFLWcxQYzbZGk6eTSKteYbs/IVZsEZy6KFP+snW2WRzOL5OLuHNtuENSzknjfP3/NNrtp78rOz3ZQnWhMgES5bF'
        b'XmkvN1iWvfbj16/vGM++kFG9UPVnckkvsIOTU/DBkSH4nCHLd2RyALmDX8FnBXxxHTnGDl4Oi1tH6Be6oF0aiOAgOWHn18wn19n72eQ2OYDb0vEN+RvSnd+PxscX+g4v'
        b'PnjLmveRav/hSelnKvVcXBcViFhdv8ms7Nwydygoner1K7NAuFiJeH8xf8tXKc2ipMl/KFL6+X4/HxnoFZ4KTcCkUwC6fq5Tw/AqWP4MurQYpYhAnZ/r1LQEAa4FAa5p'
        b'GK4FMfzSbAgqDrjvC9doP3t+sXCoiX11MAlvm5rrC2EIqJWcbKSxcfEh8hKNbJtAUWBRYQNuzoK5R2RbfQjZQc7ES3Ftm8ipGZ0vAw4WJC+Wz3bjl3FLDmkHEr49d0kC'
        b'aV2iAXxWIMDsF0NCybal0pc0dCoaGTr2T/qyvHXx0xGLwEKu4UPjnOx8+bgidsIcHxzAip8arUH0U4TfqimzB82uRFKAmx3kHrnUGWGG3MNXaSz8LifO1ejxYvVaGi+G'
        b'xW4kZ9PNufi0Pjs/10Da9RwKMfHkDP0soVsHj6t1lUlZ9Gg62T0hNRU3k2Z8pCwXjcI3BPyKitxh7S4mF8ntJBM9q92ev6hwSY3Ff7A9wZicQFpSEmkk4Dq9hlxbSjqk'
        b'rm1KUeSStuy8FBVusSHVID5ME87QVQLrKrmBn02iQ56sIh34CFLhO/zkBeQQ+2jAWnxrWJI0H9Alct7Ro7mFCSwOfGGCBBZ+JktAw/EzofgWbq5jvpug5h4ud64mVxWI'
        b'S8bt+AAi2/HlKW7K+1PI83gf/Xyl79uV9VCuJAFGrc1gyF8kRfCXzvP75rwUH+YQOSVogU0fwvtYAJ+lDcW58qcmybnFZEtesgoNzBTIYdxKTrPozOQ6zOmuzrFjSCN9'
        b'ZCCgL7QlHm/hEb5BDsXhV0MmJa2URvECuQFIuHtN0kJIrUP5MFQ73JTozJ7nBGnhSsNqch234r3klQZy1aVCoXE8PqBe5aafbMabXCOckLuYft8gIScZ5h8I50Lcxtor'
        b'SugESoXwbnI7GCknuSfAi2kqcjOJjgWMTVsK2V6coMMXEoA4tqSYFgV+3QBvwueCED6AL7BPgpKDeLcYQm6S605yaxVub3BoV5GbCA1aS16ZIODmsJFs1PC94g2kjX6M'
        b'JdlIDifCCCtRJN4j4Etkh4Jhv36ckoZ6iv0wq0ybqAhHbunbj2Qz2e7EF/G9VUokf1yzhVy02YJfRc6VQNC+1xq9qCi3qGlOxOHhqsjZX+xM+e873MzN8W/l/LvyR9ZR'
        b'54pCEhbvbv/B+Xe3jU59avtvxjtQ3N/Offfj9O996SoQJgVl2cUhlbxFMM8p3Dzg04m7Ez7zmkZ8Z/vFogFvTA6+vkEcUzj4pRvfGfuUUP3ihX+0/uGHlg9Cvhx6NfPE'
        b'v9bZ0ief35OX9m512ejIo9Mm/3/svQdYVFnyPnw70IQmiYhZMY00WUyIWUHJKMGsgCRRBKQBxQyIJEFEQFBURERBRBQBFZGxavI4aZ3oJGd2ct7J4wS/E7qb1G2Y/e0+'
        b'3/N/VgQufe89OVTVqXrfN6rrX+zfcsf928RvBi/L3PvjoVurvv85doh31oi7CxrH6UXdytk4J11mPPrA/O+fvm2l91HHcxG//OPJ1vTIp3dcS356+6cltz42LWs18hzx'
        b'Ym1T0pkXl709xgz/8UZZesTon1tu6v0w8WepXs3vfhNfNyn84cDaaC/bDa8N9vlkb43pi6/c+M3v3MWN7u/UfTJ+13s7NjftXB/21b82PrU4JHt7/13vjX/vme2L7PZO'
        b'Lvx5586hPzQ+dbrSMOSvnGFPyYv3HXINvzb6yS0vhMacb087+13q4g+GL38151v5b/2WTL+z0WPvPVF0rc2xrPZf9edWFwYdGakYw4g/J8FhrFPtnXgQrmj2T7J3boJy'
        b'DrVQNVEPGRwCI3ik9FNyOC/GU3JIZ3gR3it3dmOGGOCqBi2YjFkM0xrzoHoEVGAd5G82NTFKwhYltiabyATLTZKgMXCcIT1g23po5xhC2BGaKpo7Eqo5Z1U1FpuQ/K9a'
        b'9CCtKl7C8u4/k9zzx1p7InIoMIeVrVGMJ/tDFiu8K16MhnyzVGxNxJYUExlUQpMgHyhe54qdDKNCPBTSOQwGVsEFTorR7zGGtrBGgNwuzgqoS6a0FZSzAi9Ac3I/8kQs'
        b'7l3tQ0kpxNP900QzdqWyMsGFONpgDWSdyCPfpMzSaSK4APvwPKvqbMiBIsazJYhH48E1Iiez/gxRAhq3kbZJNd6Ugm1mkAf7oD7GzMDECJvMUslsxNbNm0ir+UllcGUI'
        b'ZjB6UciGS/Z2DljgO4HiVuUJsuUisuicxWKO5F2ROADzPeEcqWgS1u4QLcBGbwbiEQhVFF6MFIvIRaSwnn5kzdvvSLHXh0CLdDOchosshwVb3CE/bUoAhYInG4IvkYzm'
        b'iLEM23ayRrLwm62mNnVw9PQlu0ILWQ6sfKUm0JnGMMNH4WEsgnwnOsr0sFQuyMLEowPGsaYy84NWyIcjfk6qxUxPkAeIsRSPjeXUZqTNdqjYzwLoBk2XnFzScCPdR+Ep'
        b'KVlBy8kCyQZZOXnrgoaGlIxSrME6TpRG1rUMVhRP/cUMA6zAV4Rn0gSZl3ggHISzTAo0TcLzc2wZPLmDo79vACOxFQlDsFK6aeYqVlppLGRRElQ1inIKnBJMgyR+uFvC'
        b'7o8kokgT5I/zCnB0IAKGj4QMxjwxniZF4QwpxbKV5H1vey8iKwgGwVDjKl47YAavadsmPEByz5Lz+5CjIoX1chALtjZ6mI4l81lNN8KF7SQVf3vIdVIt6pSz+QJmY5ue'
        b'XsQE9lAqEEGA0r1S2SKbNA7Hj7OARgnp7b0RyVShXr9Mn84NIrxDvX+X/E72o/1OPe3OdmSHKRhjBMehNjKZ+rf5WpBNMh8rvM16yv7sXajDHF+FTPAV9OGisV8ylUF8'
        b'4RR09GTlXUTWhF7EvJyVV4YnGUgMVmEH7iM9RhocVEy+x7djoYzo0RLshJJd2uXy/3uyWWZwYPJ9IhVTe8r3M41EBpRfViwVDaL4qeS3lWiQ2JgCpjAeWmORudic3DcS'
        b'DaFRuPcMJBYsLNBYbCQhErpY1s29lR7eybr9xQzPA3rJ6tzizIpXZ6QKsFL7O0upPS6JNl/SVKo1yiPCkzWuyzJlxLqojVG9QVj0H6Ix6gyS1olUiSYxTkuWCMuIbt7c'
        b'wB4r6t5ibTr0kufvQ1mrva6P4FFDXat5LXWCvGoMWj0zeyTjOvO33Hg/Q/hdzTm2DSNZUYds8NJZq7BReiDmPyqY7W15qMr/KvQ+VD5/agpir81jK1bZVbZHJiBVed6w'
        b'U21d+VO1juc/Ipi5alFHrb9NyKviDdIPjUhJToiO1pmrRJMrY4AlTzuQx61p8ECX0xgtCXO+fuRisKOckffrf5mmALbMiSI2WuU1sZH6qpBWj4qn0S+Rfy9v0gTGod3m'
        b'ts5iGGqKwVy6qANHDMWV03g//q2a77tfhxtrshyvG0W5Z8bd8mULrQZTkGrvGoB6bmIQaETODtFWi+0CMzGImFlB2CkK6natMjHE9DYxqG3kvTHndFPdurISRIv+BtEt'
        b'ZXxKEWnBMqT/evAe9XQUUVor1yWkxEUyztuoJAZ2bh0eE07dS7SmpSGPmh8XFU7drqzdWbgN7WgVMi/zWlThlqsclmK1I/uqIM3DwoKTUqLCwjgjb5S17YaE+OSECMrS'
        b'a2sdF7s2KZwkTh3T1BjAOkkPk/vMeorer/JX4GCH3OEtrZsf2YOx3cPCFoTHKUkJ+8IMsjgxodc/UZ9ul/jHnj4rlSiprDziTNaXL34e9sxag+g7N4l4lidqe8FKIeKS'
        b'SKYVkV+6BBG4huWUbVctiZxfwi15ot5HT9LomCiGqvYDO3va1etrxNaxPXYgZURcKGvgrvMUmkA3+lx+vNTFm7udVMqcZKqkUlmvbXa38L2xzo2W01hl+cO5XuZbPGA3'
        b'AzO7iVyFWAbNRA7MDaBKFlHjD/owRQ2bsM3EecGY/xDrLt/ltBijNadw3Y3RlHEF60mR9vcUMrGQWmxyfW2V2O5tD/XB3BBFPwvwZfxXZyFXPm17ROyiwjg9JRVilp05'
        b'+KPnl2GOFl+E3VxrY2Ub7sss0F+FfRYWH/1VWF6MdzgZIkQRKpMbWPxwRyFhyls/zJL1yNp8tp928RbO434mpC/pZ9yb60ksLNrJgYIN4TSDEw62hIPY7tFTClYPPLwK'
        b'lQ9loCYDUakaiFbaBuIoeij6EIORJMLFTmk3mgHdfIdqoLDtmvG6k4zXITrH62e6DdYpCwWm7mZDad8Bmwj77z9g7fzpgL0w1GQG+bNYIWYQobOgYiAfylIzzMDdIjjt'
        b'AvtTmDniylp7/pJ04mJbETTPhPbYnRmVIiW1zDk+b7YhxjPCl4yM9R+ciVoXsy4mLsY7wj/cP1z0/eANg9YPClr2qbPexMTRbrUi4Ulbw9Dl36gPXbvb83UDIGjanikd'
        b'WrvMytjIXLrVSnuX8U4S36drum3ZGaRPzHT2yQ/muoV1Hbn/B2jj1W4ID7EakEW97K9XxUpqPfpDJnxJ5u3NtZ7r1kUbR9+JEwmWpuI7bk+RhZ2qwGaPYQuzD9Va9dVj'
        b'dejA0zz79GUvjxHWaVoXfJs+5y7MdaRrfddBj05THaWziz64D1W61vz+z4UdnYt13z1X6h8ca3D3Q6mSfjx+modPOO+X4eOkHqIFafpdAmWf7ZQd6uveTe36KI/cU0b3'
        b'7knTG6uzWd/TvXvqyOk/0q59RFh14n2G/dpvX5EoqVUuZ5KrXfhnRJZZ9filohMV9ND0zi0TYcyvkn9dmUc2LMYSuBf2r8N8ey8HaIJisSCdI4IWzMKWZHbwsQ/2kxU1'
        b'X5t9p9e8gL1DNeahamxjB65wyns+x7l1wKbxMsEA28VwYG6Mjn4dd99J49jXKMAdf3X2K01vvM5+ffsR+rXLxVjoczg6TN0HlBdaxRFrzHQVtY+COLsfk396eCpk62UP'
        b'ZoemQ7KHZg+LHqY5OJU/9MFpn5WQuu9Y9hkS9v7s5MUH6rCNH+YRKbZVxk7zsP0xfpxHhYwpcNVAnoQt2GJGz33YUZQ51IjhJGTgVQM4ljKdPOUeB2fYgZQn6dgAaOg6'
        b'lcICXz8tp1K4d4ucjKkcPKmQ8fOwA3BMoqRnSgIWCZtEsG8tZnAejAOpRC5qTpFRAGZhw3Q4gG2x/J12P385ttIjoxYBjkfBCbiylJ0Q4n6ogsvKZNLZmCNAfSTshQYo'
        b'Zm/ZYzFekdOmwPPCYKyFcjjow3PKM8ArSooYicXCiBjIw6PQyI6tmlLZGa+5MEppP9zDSuDHkJ1QF06P6mhSJwWsIxtGmesKRieC9ZCNtZr6YD6ZAfvgEqaz87sdswXW'
        b'Wl1Hd6yFsCk5CS8FedrR0wHSTAleZPYUQbnhjji8wg9Xc6AISydi0URnqSAizYHFNrib1PV0CguYJkU6MRLaetCsqiFuFi9aSl71DtIXQrBchi3zYHcKPaqAc3Bo6UQ4'
        b'Q23NE4QJc8QpdKrhdQm248HpkEUGuJPg5Lcr7td79+6tIQo8aRDrx53D7Dc5TBFS5rO+m41HfTT5YI6nPRWtC5y8Q2wwlxQgyEaB+5d6elEBbJ8fk7wCE/E8HQiyeJPV'
        b'w6AghSoEs/vPps4h3R+kA4rKa04BflPnL+6Dw05H0lloN8aLisiUcLa6+MN+E/LGARPY7Wygh7tD8JgMC4NNFlgMMZgRCO3QgcfwvEfMFsPogZuM8JpsMx7TN4A8wwBj'
        b'aMJMrHHGjm2KkZgz3REPy+DQfAU0z5qEFYPIOGnC4hRq88CqGbCbGt7TTYQJBhJoCoGLK7BUBrlIhFBb2INHl2IHGYSFwUNjd8IZ3D0UOtaPHgptZBBkQWv0NtwjmWBD'
        b'ClIwEi+49/czcmDrCBtrVcOHiCaJBYPHR6+bWRbZX0ihGwS2SLFUw9zbjbXXRnN6y4h73ZWcurcR2+QRcGk+SzF+oJdQJAjOzook74TVoULKItbtZgG0ChWGgrUxuViy'
        b'ZgMUQwNexROiCWRun5o+kXTGwTAySxvwcMh4PLmClHf3gGDIiIKcGKzCy/rrsDESrpmnQTpUpVCnOyjBY4K2YgJ51dPBW89iAPXugToF+U9Pec8aYhvkQ1OwQsS8FvCi'
        b'N+TQQUA2Eyz0sidLBunjgQbSNNzjLIV2ttrA0ZAxPoyIWBsLcTIZt32IiPMUxrHk8xrGROyAB0x7noLzRoRGQdspeMBUUji6PszeBO3TzeiRv0gQQ6FoPtkTr6W4kzvz'
        b'x+jZeZLG2+fHJ4CTt5dDIHc7GU4+7u3h4Em0zUS6ACwKdFgiFtKCzdL8N6RQRwA8NWgWdzzwWqxyQuGKi+PSJZ6+AaymjosNUrF1sae3n7+9g38I527u5vDA1mjcF9gP'
        b'Tm2QswHgZCdh6rf5mO2+l+aNJtssW/39LOGSj6MDHB/Kz6QMsEkMOUP5+IjFC9gcFKDw4/j7IUs1bjVdLjUCGfD1sFtYRDq1GPetsiYq82Wo8RwFnZ6jJsJ5KfUGSbeA'
        b'CiifwhwE4rabkQWz2czQdLEBXiTXyZtSiNytlAS4YCVne650w9ogulBJyALXQBqEdFOD63BGw9RvOO6ZPcVH4cAUd39SKpveURCrrQ0gw5MsKIz759QoLA2CgmAoN8UC'
        b'yrKkRzS2w2TIdbIOnbUKL8AFPCZPNSX7PJaRxURpxYqxa/1jpKCXlNisL4jxnMgZDjiQLDoV/ZgSOBBLbTHfl7zkSsbWIiIO1SezdR+Oj8XL3Jto82aGKyZfIcbG8YvY'
        b'3TVrlpK3ug6rz0A9HIErUMe3nxN4CSuW417VCfAakdPI5dxBot12FPer0BOkI0izQAdUS7GEV/JajNpXBRtGKqBeKhibSwbgITzOYkawESpH4NUkMuIVzJ5AWQn4uaye'
        b'8BhZx6LxvANPqTbckC3jq7FBBYqG5WIoTYRLfFPbHTHSjk0VOAxn6eGicYzEDEtGsDaxNrH1UdMx4GV/suHVj+NtcpGMgnbMd/DH/b5rgeiUstXiATPIZGZbdQEcx4OY'
        b'zw6YpVNEI42gbhEe4kwdBVg2nc50Ca32FrxMpI5K1Q6fF4ZHGB05pwSvXwZnffAqW0RipsM1O9W6SEYvNsfROa0njIKDeoZQtY3tlXiR5EvXAGYLgFynvs2zAFr0BH9I'
        b'18ei+DTWETKysJ60c/Sajpn2CrIwGU4Tw6nxeDR219rnxMpdRHIYp/D1CGqPf3uO+bXpIxR5FlErnQJ3PvH9mICa1I/NPA+M9gyU1VktmCPKmGvYWLi73+gbtruFUsWq'
        b'otlFbsf7XfY86vSd/uXn3vHyN/o8PiYmOuGXwsro6uKxXq/VmzdMnNz+2Es5dgc6y7fVTHvhx0Ul3zeP7SzK+cPeeu6NgZMtssT3dn00OOpa7qHQ5sYhLc88u2UBfHrb'
        b'Zr1v8KypI7L6/0qkpmstdr/b29h+7P7R++ltb75/Z8zPzU0lIQdvt9hPenIBfvneZ7bVl8tenetxvP0pp3F6/Y/e27v1+c/03zD2X/624g/b1hG/zRz09pTmD75KhPZ3'
        b'2hedWvHsH5Xtla5OZq8Memf4096zzoxeNvYd57mKpUk/j6hofME3yLRB/NXUSkvRT1bPBgedN/Bd9GTLGbcWm8ebtn22siw/ZfWp2a+8vCPrjcdDPl+xeYjbj7J1H748'
        b'pXqlze17SbMP+LwxzbU11r3d52P/7fk3jz3/RM43rscSVr/V/K7o/U+33FIe3ng+eGfr9RM/OQYtC/1+SWvEL2HJn4cZxqXKPh6Tf67lVs7vIftNNyj0Fr58DaRj3nM8'
        b'99eYzfapv5U9lfjZrVcCHapj35+woPDAD0WbXsp/Jtwve8LC14RbaWF7rY6+ezM7+Sv/dv3zT1yf4Dtv9V9V/d1avs3s72tnM6Q2ffvWqN9/zWqe9V6y67w/nm70cH33'
        b'/S37vutc6T2i6sMRM+ui6vJf/ulucvWSNbPGLp701mn/UPs/YnMO//6WyPzZEfXrNsumDz/6Vu6wD6dGvy9ddH3K5X/Kt6z6cMAqz+QD0Qsf+6g1Numr64cmzDz56fPx'
        b'4ROfLp006j3l85eWvPfVUDvnMSNKjnnU98/cca7G2eH5yR9caRq+5HRt+On46vOSzdW/fe50L002NHWngntPLB1iR703qGNGv1FdrhlkrTvNfWoK4NpIqBA01FzmmM2J'
        b'Wdoxcz5mWHYtQXAAjjOPICIdpMN+eR8KkoFTDIgQfYC5hOCRNXCRbpDboZ47bRhAizh1NBRwp45tcIUvjsZwtWt1JPJSJnODmGg9sfv6uJosc0cwcz33nan2HU10UurC'
        b'4QEVXb5G0LKAObQMCMXLXK+EvW56gmy9eMTmIM6tUqGEQ3a2jn5wUYF5RO8zXE5mbfIqdrP/DMi2oyR+ufbyXWRlgkKxA9n2C5iPEJHVmkgTzofqbkx7lPBmIVYzRpiR'
        b'eJA5uVB5JYBLrVi3jgquMmGkjxSP7VBwb5v9q6PtHGnu8ll0FWkQTxyXzNXho0QdOc78jHAPUT2Ym9FkvMBcI6AW8uCYEgoMNpngRSV1CFR5/dgM6e73gy0yuC4x5mQx'
        b'h6Bqll13m6dyoUyw8JJAFZZ5MuuyNx6nHHXsJvWeyfMlK7xM6IfZEtg3Cpp4e5fsjKG+OWecSE87MNpFfcEsQLIuZSZ3/qrd4GwXYE9Ulfw5UMruyvG6GNtEmMPds0pG'
        b'4hkiXqRYdZcu8PRa1iJb3PCcZruYM46sxZmQxxIeJp3dzWcbi4ao3c4wdyprMmNohlyVt44bHBcxbx3co59MAdsge6Yvt01g5bD7up/4wF52guNO1LI2la8T7sGK3v5O'
        b'wX7MDWc61E1Su+j0ccHJtCOSdC3m8x7IhUJsogJmsaPC205D4rdbkjAb9rPGjZlHtNh8Mk58vKBzMm0FebyY7GeFUM2mYdIEcbe97RIRss7OIdOQjeZD7hO6yQJQuxmq'
        b'yTjhTl8bsWWyShbwwgyNLOCJ9ayqk+3C3cj+pVMQMI5m4wOODqQ7cg9vJyvcKyWbZZ0FXrJNpj7XA7ZAwUMZgfrtVNuAsBqak6kdIpw8dxQ6J/n4epHlJ1BkG7WO+6yV'
        b'4Glo9bG3gfy53agB+0OFwvjfcddRDPsP4to++o8ua75ZLyBPZun6SBD6WrpcqCHXgHHZmDNOJdk9Mf0Wy/5i3xJjMQ1Jooh4HMfOijxLnxSLxPekEoqTRxHWpSIZZcNh'
        b'kMmm/JukS68syBV1PLJgbIXm1AGJpGGsYikkv8kdo3tSsbHKpcmU/iWhrkxGYgMxReWlX10ovmKSipj95l8ykfgbmRXl4zFWpciDGDUWtV5Nwe2B3IeJ+xexoDQ75lDE'
        b'3JeitnS5OHTFeXWdawz4r/WowqBbCWeqS5i0V1MoO40bFDNCZpE/bXUaId+cdx8Wxvs1mULEgt78H3DsSg9eRQy4+NGOXdUUjG+JtbgtzI1OpkyL4XFxDKK1G6kxKWQs'
        b'LV14XA/kVo72FRnJ4QzDreOjNvdJlDvF2ISFLdqY7BUfHRZmvTYuIWKDwlGFsqt2hEhRRkWnxFFvhLSEFOvN4Zz+MTKWMjb2JVzuXojYePZgNAMhUEWcRil5GCqHWLSm'
        b'YFHWsZHKhydXpNgJbtZezCGBjE5lLEWyJflQ54Rw64gUZXLCRp6spmpekWFhCoq1o9OHg7SPuj3oZWy8depUR8rrPY8042bamMnrwpM1pe1yE9GaoqpuDF6X+T1xZwyS'
        b'AAXb7dFE6oDemKSElESGwac1RVL15NiIlLjwJO5uokyMitBAQiitbWhYvT1pApItQ2xJSyR/RiVHOCpYJ+hwN6ENmhyl7hdVvzO3tPjeLJqq3o9MYOHEiRSYWVuaPTrg'
        b'ASyUIkEbC6WRP9N3HWZGcMt5PB7lhvNJ07ndnG61/bdDW1fAxAWyg3cFTdCIiYVzUyjILB5eslllSLQ2kFBr5dVNzlgyZIRn/3GbduD5QCKCnpsPJSvneSXDWTwBZ/tD'
        b'k8FMf/vhWIknsNId2kduhXpzZywfwEw9H5t7Ct+NHSMSwsKMimy8hBQaBYbnsJka1YhQE0RJhfcPn0rDbmhYk74wer0Uz0ID1LD3G1bpCZcnkfrNCTPeb75CiP3D1FRP'
        b'SUMTmz5+ctxzHSaZzpYeH/x+7IVvhcGj5S836QXHrotP9+0/zWbApJevxYUnDBl79WTA05OsDbMOp+i/u9dpbcKQSbOWLtxVuutOyXzj4++tsnWZV1G/b6TxpkvPB4Rf'
        b'+NW1cfLzv28/eqrT4FbdhJ8MHM6a5tWNk036YWTO2KE1l2IVciYZSAJi1QoNU2fSoJ5pNJMWMX1GBJexhSszlnCe6DPUCZ0e/6SsFz+UkCI20RxUnVrH1B2iCZ3G9hV+'
        b'SmpXdbBR25f6YZEEmqY7cHmlDHN34P5ZdhofdabuLIALXLY/h+Ue3AUf8saJuAf+EqI6UAFYjHVUYuQe+ImYv0O0YOccVpnkEVuZPjAQOlX6gL4HkxpFkVE91a8h01k4'
        b'BTav5NTNh6ADr/R128di6OSu+x1p3KW8AC+PNrXUKc6mQwkcV53FPdB/xJDGB7IJyqQXW23Syy7BlcksFOf/HvkpobIJlUl6+QlokurJDOnYc2PvQ2cp5k90bbA55M+T'
        b'dIN11LbB7hbev0/4o44SUcdSss+Eko2mB76COsZWl0uiJEfyUBG2EnZOLv3gV6mW3TUoKl4Fv9oT4z1FyXfbKLbekcXZY57X/KBuuO26tqiotbERytCIuFiSCucAVgNW'
        b'RVMAyoh1juwJRw/6cz57TBccfLdUVe3jxhwY7TUejBSuWBnFipmQFEk/IIu/1sVZBW+vswyOC0J8wxhkXUpiXEJ4pLr26gbRmijFRNVA0NF9Q+Xjq0yJTeYg85pCad8y'
        b'Hliq+fODw+z/7qshf/tVr0V/99W5y1b87Vzd3f/+q/P+7qvLPFz+/qsTw6x1CFYP8fIkHT6kXtGc8YaLOVGR9ta2quFv28MRtaenLHOX0y6X6PJ/XZAUzpC/u8bwo7i6'
        b'LqWSLF8VUic6OveYLcxFl+Pt8ulEMkyNDf97LTUvOERLEbo4wukaw8vBp1ts5AOEL6nQjb9WI3z15xTgFoPYgfwWkzFhxqOipquCrhsxy0Eph8qJ9Ai/SoAKazzAZDWR'
        b'hIhgzc62E5yd9QSxl4DHIvXYDcXCXXb+jvQ4r0wE6bY+UIqHWVppC6HAzt9bTO5kiGbDBVe4joXsFe84OGPnTw0XkCOCc6tnhGOmQsoOJYxcoJOeb0GLtRle1BMkQ0Qz'
        b'saQfOzqwhBM25F5T/PpkbKPbf6loFFRCDUsT2qywVOlCNj1RgmASDm1waQ4/5siyhGIlti4NMyM7mxhrRbb0PJEd0VvOJqU9KJFgCzuhx7J17NDEJQyo4wFmAKUIwiIB'
        b'9oXDdZVjo+968g4p4Whs0ZQw2Jgd0+jBQRNaQGzB2q4i4pGEFNoD/mOiSKI7x2mKMdqRFcJ+2Bp1uddsgDY8OUAhYTlBhucKmhPpAU1OcQp2a9JqVoimZWO68nE042+l'
        b'YxYUyFPn4B5D0ukSQ5HTXLjKHS+Lw/GU3MQ+hELPSOxFs1PhDGsjDz+8SA/r8BQUyk1FgsRYNBv3T0mhiInKdVt8qJwbxBx76XEvEXwFrIbi7USy3od74BqRdSqDyR8l'
        b'eA1rsJjI1SVwzQJroUwPS9fqmZAffpCF+2ZY9yeCk4UZnJmAjbEu3jYSJQXlPPfp0yEvd/ijs7n+d+3Kuwd21nrUP/HUE0HfWS3fsjtob833YXNfuxEuhLgMlYzJbP6X'
        b'eU5uRYX+HUX5r+M/f/m553/bvOt4lL5jXeS4jzNXBfrNLfnm2dVpgXUfLc9wHXrGcnLppiX9G9JNU34sc+9/2XdI41vNb3/hato0cquj9LH0f545cVuaF+H03qTig39+'
        b'c/pqx5/zSqvvxsV8FrnwmwHPTkrEaSlTPH4ZPmXahcFfSaZ8/cKsZLenPw8NnvhL5nt/lJ++7Fp7qyS+/dXq4oFJu777+NknxpWslr3w4rd718xf+mnb/ISqL9d86zhp'
        b'w/vvpM4cED0/4I+czpsKh79EReNXP/t2scKShXguIxJnlgY7AY9As9qifxwruBX5PJ7EciKyYxuUd4/SrZrBjL1roRMO2GkcoeH8DIlgbC/RJ+PgGj+pyMYmT/UxBZ5c'
        b'NHc1HOPCdftErLKDugiotffUE6SwR4SZy8nQZbbn1kTqcp03dnG3MFtsgIvs1cnWUEFE9ixFD6l93TDu/HZ99gI774HjsMCHisMGmC+m7g1wnJ1QwAVIH6aUYws9L84X'
        b'sIyU78y2ocxoO34QqXh+4mQyGTBbcFBiEWmRIv7a0XVwmd6TkXs5wlAy8g44qZK0SMUOeoummEsPzBux2Any+JlLMyn2KXrCQGb9AU2UNY9drVzCWkhvPJ5SsgNsqBVW'
        b'jcAjnriHB5Vmh0GLEvZBDi1RkbBLhpeGQQ1voDa4iifJa3rktdMCHsWrWAkVWM5tzFfgJFwl892YqlaNQr9xeBROYik/yygibXpEmbqJ5lgueFvivlmD2Z1QKNtOPie5'
        b'QZngjJmYh03JzCQOFwbbEUUq2LavKgWlYh2xmvfxgpYqiUDM1I0w7epGGFUvqJGSKRzkW8oMp9zoKWaqh/rLmMVSGonVZknNN3mDPHtPfG9rv57OzCRvfzU+CwuxNO4u'
        b'Tifl9tBWmAMiqcs+jYaSq4mEzCdXN+6jpty4j4N13zIRhY0qJiwCzF8xsBcy1m1paICX/2156PyQwEAP//leHkEcUVSDmHVbnhgeG68OkaSRm7eNusUQMgunJnq0W6Bn'
        b'Rk9kLQa0lSVSaWGsjryxhvz/yfSetJCqiDQKdS35y0DfXELHgsGfMpmp3qA51LQuFf9NYE+pubm52JRSzUmFe1PSDESWww24d9NQKziqClHAy3hYbZAQCUMWSmOhzrCP'
        b'L6+x6rfSVtSTfY4ignE0sEqpCg+MX1NUMEPyRa8pOhjFBuOfd12bU2TOyP7s2jJygObaKnIguR7ErgdHDokcGjmsUk557bJl0aLI4ZEj9hhQZNAS/RJRpLzEuMSgxIJ+'
        b'RY4s0I+ckE3RxmRE7R0bOY4hZ+kzPrjxe4RIm0gF5buj75XIS8TRYvJWf/JtXmIRy/+yIKlZlBiWGEVLI20j7Uh6LhTJjKaYbZhtkm2RbRltwLC/aMqGzHNWxjxp+0XL'
        b'Ip0infcYUCRSqbBCztToibct6PSYzzgxGHRcdFTSXZceAmffB1R0bt0fuutIpFe3WGWCmzI5kv12cXZ2cXGjQrDbFmWkG50yjs7OE8g3Ea8nKiS3pf4BgX63pZ5eCz1v'
        b'S0MCFy6qE90Wu3uQn4Y0y9AAf9/lddIkajO4rceUztuGHDw4llzqRRPVWfko2U6g2UqTSug8K6U/yujMlXr5B3E8yUdMaxpZ1HqmlVTFEgxyXzL37rx1ycmJbk5Omzdv'
        b'dlTGbnGg6kASDZN1iFCFFzpGJGx0ioxy6lVCR6I0OLs4kvwU4q7068QMwCwplEI0kgbyDZg/1zeUaAl3H6OFnj/Pi5WQ/F4UnkYXukBqP1Ymk0QdnSeRn2TNo4nViZL8'
        b'OMrjYVpW4yAv/4W+HqHz5gbP93zIpCaQNbqkR5XvTu314vykBKVyHlNfeqbhmxDjp4xhKU2gKYm7UiIFPEPTMuvVHneH6K7U3QFaG08h75EKHW5JZ7WkPS3pHP20VyLT'
        b'WCITkxroPd2ZT7hr9wg1va0fGRUdnhKXzJqf9eV/JNBBK/SctgASppOMs46lHn0bVql8+mQpsbueXcXDSiaef5WFlfhKXh8tSMeLbIJu3Ces5LYBZZJNJsNad7QV/VrI'
        b'4V97LieO6nd1RyNcInWYSa6UztoFgN3Ck/eJSLhfnnX6fMOO1bJrb9Bs3XSYfk7LFOzfJ4bBSN28FM2PxTAIas5TDu0WbaSJTzB6qPgECYtPkH6Qoa/FxOnF449jt0Z1'
        b'M3RyUiN+HkUX6PsYNoPU1MPWiYxigkkxSre+DzpY95pE1jbuHor7P0Yn4QOfmGZtY6uMpYdbqVMdp9g+RJJ8XlvbzPd88MOq+Usftrd+UD661xZrG6/gR3pjwn3eeNhl'
        b'gibRu9C6bMgqOxg3GPHQcBWdlZoqQdebdC/lr/UeNolJsQlJsclpHJHYxpbu0JQojO7RttrNirZ056bP0H3UltqQbekGaKtw7Dp/neLo4ujspnpEezJdR7XO7FFVql0f'
        b'T2Ef86R1VYzDWaiqpgWsgrfPeCXDq9DZPOwUw60ntgCbZNqhJ1TYADrL1IUv4aahxu0LIUHhHDSn9VoO4+k/co+xGlKzPjOnMk+BqPBkOqCUas63bogc9KxaB0ABNcmS'
        b'dDaHJ6kcC7pRbbDWsQ6KiqJ1TYnrRiOnNan5c4M9FgYELg+lnEYBQR6hlM4miJVSc6jPye10NhJfhHj7MPopFcCLut/U2pvKmKz9DLzLwMwOLXgKXfZf215riq1OLwLW'
        b'Q4l8nio5NV6vJcaW1079SGy8dvQEjtVBpFU10++68Hhrj5BAHYbyeOugzbHJW6OS4ljHJd+n8HxB1DGXyITxSg6PS2Mv6l7hbHWPWRXICO+QLuwROvJVXaLBIeFnVjpq'
        b'lMydIrpBlvd4tweGjM5Vi6XU5xCBNI9KpFKqh2+vdLX3iYotsitfxtK5NiouIT6GpvQAYzuVUAz7yFNm/izqDIqxCE/gQR8sxCLJXDwpiPGkyCYZTnEv/T2QjxdVkKCC'
        b'bGCYi9g0MYy7QjDjVxbWQIHSxATq3KkliqKhxmI5c5OA3bB3G+6GOqoWwz5sI1/NkCsVTHCPGPPNsJBFmCmmw0Wf7nFfS3Sghg6FM2rgUD89b7EwGTJNSfnO4xWVAXwB'
        b'NC2mxmK5qQguT+G24mMmzOQ/GU7DJblJkpkAp/AcMzGPnchiYVxXWXdDiFWXowkOkLJowmISTUwCKUasjYN/iI0N5uE+J8yzp3CgHO7Ugdr+DvUXwbF+C5hBW89NSUFM'
        b'w6VSQcQwTPF8GjvcyPLRZ9GGdxKijN+JtBcYTi2epdwe3ZFNPR29/TCXVBrKxU6BmOO72FMSCLk0XA6vwKm0cQJ0SuVYbr4z9oMdt8XKKpLKW0VzxhVMMMqcY+4Rk/ra'
        b'uyFfzrm9SrHR+oWwcOs9IQ2WYy1+/TxJ2pEx/mbcP4yv/fLbrq3iG07RUYOklk3P3ClKKHyt7ZOv93wgO2zx1uT+Y1In9rf7uPjduMpxI9OqtnwuVxRnbbiZbrXTJWPd'
        b'xFmT/mWwa2rgVJ/dN1/rvPr+T89Nf2dIzTuuO78ZX95qWfxFVOHnEaf+XL363a+vBp7WOzEx6xO581PO+v5jFSbMlJqwGovtHB08HagDRE3ABrEzDbxgJlG9XRRJzxzP'
        b'U0hmiiZtT/059AXTQMkEbJ/CrJtGuBdPdnfKOLWBWnidlzGbs/EYqFA5k4gWdgcurIN85p4KTau2+wQ4eFFzNnWOl+I1bjS9sGi+D2Rs7eUMLkzhNs76UUFyaIrv4yBv'
        b'AKXYwB/ZjYegA/LXk1G+v5c192IK8yh3f2wlgyocDId6AxsyWEMomcRM79AJx6HMDhqNNDiUahDKgYNVDtpwgJ54MH96MnrOqEzv2AhXmZV3hDd1o2ZT7pJkhq0g8RMt'
        b'wHIoYj3gh2Vwmkx43+FYQ1phrWgCNMChHigVRv+W/U2DmzdHl1K13YJa4STc7ZWikEhFBvdkYvpbTJ1IGIWzqVgsGqJDFVIhxKkwcmJE2mzKcT1g6fzuq4u1jHhEXexR'
        b'IOpUsG16oQylTxd+VgG54gB12jLUUEc7PoQU3BtcjpqugjznBt6WUmLY21LKEavQ1+Z6yx1bqZ/rbX0VlXhSu0hLGLyZekcJFjRh8FyJNFapkSYcIzzbLNrsEYPd1SBa'
        b'Z7Qpk3MjI5U9CbHVm6kWq59GDOurk0Zbu1Eh0S1MA2ASpuVw314l1GjwuKgjZV+/097kjpzbmOrrXaJqMm3NZJUg/1Aqkkq41dD/PkhL4uxf/F0tHL3hSuvouIRwakKw'
        b'ZmS0KrZNXZ414fE9mO16U/vqKkUP1UEb825y1BYuFydryGo3cidQHV6d5JnYSCrUdTVFFz8gr4O1DSOtp1VjQtvowAWOjo6jFTrETe4fwTyUw+lo6kZZrUmZc3JyMbjr'
        b'vtb0NO90UWyqhoDKd6sn4abWNGwCPRZ40NMbj1D/EL95HoH21mrthLOS6vT3Yi7JutlpExK5i/Z9UtiiTeHTQQN7n+ToP40+SFv4fuqaBiNONaq1pqbmHNem2VmTVvEI'
        b'9J/r21eL0+7F/JCanZoojDeFhq2ZDljVuKHzgijDUYyQOyzMPyGerhT3ce/ektyVO+PypW0UHkddqukCoRm60UkJG0lTRYbr8MOOS+EGtJjY1Kh49cgnUzOS+vnYRCTE'
        b'K2NJc9GUSMPFsk9JK+ssGE+mu9lB0b2aKu7qteujIpL5eqBd0QkKcJ3iPMGas+ny+tAy2KtQRlX1ZXYAOjfJoqg1neiUJDbX2GznrLg6tT2+M7lZB6m0KzWXPfVUTyO5'
        b'xMWRyReexHUs/rD2tUWpTIiIZZ2g0fUSkxIoJT1tRdK0qs4mE4EPe+2N2Y3p0dqfaH3hiYlxsRHMA5Gq3Ww+dfe81z535vM1I7yLWZZu2tY25KfC3ppu3dY2ASGBCtoZ'
        b'dAu3tpnn4a9jHtp2CyWYorB9iAAHjTvXXM1S34ud6X5uoj1UTgOtKudIf6amRUZCHRHNoQwuqbRKsWnkQiYMcZCMIA7IcscpwfhGiELgup0eNgVDO6fdUJFuQPkCdm8J'
        b'pmO2Go8lZRjFD2+E61x/3b1QrIFxgYPBApTtxKvBHI/i6vhBPVVTPIbX1Opp2rwUP/rQ6Q1+mK8if6AUIcEqWAIfB9slnvbeIT3V1DmQ2Y3fQsXScN6jH5HFz6swasbg'
        b'ya1cS8WjqdyjacTilBByZ93s2Q/IyhVP9abS0JDt2C220cBUKGSCm7MlUaYubuWuVzVj8TJVfyHbljtYQTNcS9lMbx31cfNhGD4O3gFUB+ap6GExZhmNGwx1Rl1q5xzS'
        b'0JXkRrUFZEFNMFRFLobceTvhMGTAWfJ1kvzeu2ELFEHtvLVr4Kgh5M1Lil28eP2apHGroGLDOnMBC2cOg0phpgp0AOqgQI6ticbQimfEghiviZzg+NwUSjzjghenspIN'
        b'jtJWNswdDLlz4MBayOpRqCysxhJ6Td3Awsww21qAhsX9BmHxZt4WteOxRZ5qqMTSYdwLDdvhKkOYwb1ekKOxBiiWqNB6ElNSgrEo0cQMi4NVrd4NqIbaBmjvUKuFy2Kn'
        b'xV2oNpAOZwxSqa+bKeZY4bmV/ilz2bjD9FjtiEp+MizlSDj0veAeHYotkG2yEGsgJ4WK9ENhPylrd86lAmhYRIYNFi1IDCYp+zCQETKcDuopvSHPggzwPDwYCPmQJ8LO'
        b'TSYLSfE6+Bg/DscceyV1cQBJzbNLR13SI0XIkkOJ5TisHQCn4ZTVAIkAFX794JQXHGJoPw5kCGRogUES44kRplhCcro0g/RQBu4hDcyc8qB4rYDZgcaBU7CJY9hUrcZT'
        b'3Swzvl4KbwdHNSsKaYaWHvBKqoKZ9Jw2pNWOplhQXdkthdJDOwRikxoWYrGnrsR1JzweL3VLO9DbEq5NwH3cEnYWi7A1bKGKu4YT1zSbM7cdttwkwHGphrXHAPdS4h4N'
        b'ac8MKKUkkbELhqaJlKeIvnXRrsZvcYf/O3PM3xu+reP69N93S0wNFhs9N0MaMGfAVv95Y4xWXnWfUmX55WMDa9K/GHHjG8X3Bjl5Rh+LbALS9uQUJ/yyz/2fFd/GPDWx'
        b'2aVk2asZX9TZRC5P/+P1he9abKgtHKJnOWCCXWH8Z3Mmr5g1OmP9iqSrt/zGbjrhmvqK3uovv6j06/9Sp+sLXl6vBSyM2/GRZdwXl04WH15WPeXzV3/5+KrFvg/Sg96o'
        b'v7q59nrnpRnu95Lrre4eWjDlTr+tf2T9bOAgbzh3fFxs9tGrLT8k3DiIPxi9NHvLUzcitpzcV3/v8SMjXuqUvb/Ey2f18GmZ30pvj91ycu2lV3/q913qvTd+OWq5ffPj'
        b'g8/aFVxLfOqki1Ham/3fmnb5nYUDTwakz5q+4/i+F0I+++CPrB8Wbdbf8caXO/O2Dli/5AO3Nat/uvVH+obbAVNl93ZfFv1l+Mea93ecu7bn5ga7db93lL30QuuR7S//'
        b'VhH65KRnZ3wS4Jd0ZdzLVq/6S53Gj/GKsn593NGNDYNiYt7e8fEo2zq3G3uCh3eGvjmx+PnL737+nVvit3eP/jqx0f21ivcTy7KPvnHTbNfZ5Z98VTfkj52SKfkXJ0wN'
        b'VVhxa0wDXsJj3WyYuJtbjxZDGfOUxLLl0AD5i4b15tNwncjc/KAQOsUz8aAGskGJDTzls1CP6T4JMg37hMoHcx8c5R6N1WuhituBUuGA2gMzGjuZTao/dOK1vvwrBtgi'
        b'CdolZramBYyHKB9bsaQX0QuecWRPYM5AVENDQIdbd+PXUGNeiAzM36o2ya0dr/K5lGA+94/c7xPFWKGgRab25YTWYO5veDJ8rB3mWk4K8IIGqSCLE4/292FNYoOFsMcK'
        b'0rvAKpb58eIcXUSJRTQ2NsjGcyo7W6Q+C5XaAUfHYukmrQQi3M6Wv4N3S/p8qPfBE0aq9V4dUj8HVSQ0lyEHKnyw0B7qYiFLKkjtRXAV2rdy99dmfajnTDH6Qd1tdLae'
        b'HLTCGZvsHPvDYbWpU+zsuI2FaA3dClU+vl6Q2ytSDWqNJYIzXJY5pcFxlgcNHzzB7JlkhwlwwAt4ViaYuktmjo9nljw4BEfN7RymOzMqGB6ENt2P+3lWu0E9BXk4Dp1+'
        b'DgpSgplia7jmpjB46Mhns/+Md16WGvaxmIqK2qyDu4RZRiJjMQtyFxuLaHi8uVgmMRBZmBtzr08JDXen3Bs88J2GrVMvT5kqgN1cMkg8iPym31YsIJ4ycViKDPRMaaCa'
        b'WGV9FJvSAHqRwT2p2FTMw9dl4q2jtVjfekVj+z8ogr3LjJZ0vWeA28M3f/fA8+taos+1BJ4XURunC21WbTbO3cL3NrqtnA9Rbd3+P9TAyox/3H9EiJZpPIEkj4Kbfzes'
        b'j2IRGBVPdFrlgyx8zJygUmGoAhuutF7m5/sAPYViJI7oo6fY+zM6u0VBY3xUkaVKIl8yAsGemHT5S236oAVjJZwzGYCdDgxiE6/PxCs9uPr4lo9Vq8iub4SZLH4kjAhl'
        b'bVRwgObhGtnhAGQyuWGsAurovWRHsvA6plKJdCPFoBMLY9foTTXmR19wGavhKs0CT44lSYwQoGhDNIfoagzcPBI71Ed8/HwPSvEqU7bsDDh8XJVkl/3nFrEq0rajeoth'
        b'LxQyMEqB6FvH6JlE6ybmgWWMBWQdOmjtyMEjsXESK0EQNGOG3DBpIOZTdLc6qqGlS1h8yaB1eNpQZqewpbAmaSJMDxvOlbN2i3gfurH46wkyKzg8SGwMVR48NiYf6+Fy'
        b'EBaQspHWat9OthE8IuUwciWrIWMG7u6OJNfgip08kqRx9LZtUMuO+piiswIv8ma4qg97oHwuDU7pFqWTp8Ixq8OLa7FxIkOwU4e0wFEiINMKjFvYD7Mi5YwgkmRoi4UD'
        b'eatfgFPrfDFLdejIdLkB4SksxDgdivFaEBRgSQildQzxW4vHRIJBgAgvSfASa/u66EJhmEgYNGdMvP8384dy7bdxzBjBnfx+3EY57/Hh/fmHS/pzlMew6Dhv14BhQh/+'
        b'Z81EpCOG8T9bkaknVAnbRZFCpChLPFg4oWaCjiGS5udUhaCsOXMjk3xj46PqVFzQ0jjyR28ya2rqXy1THU6wM1v71XiaOTvzY0pDtVCMxXZUBBIFTpmGVzCXyBb7TKdh'
        b'VuqcBdGbvJJ2xkP6cGG7izlcCJ7F6uUywkQgXWpT5BZmL9iu5JVN07cS7In+//jiratGefpw6Xk1tsF+3jvtWGnYC2FQYsDHbROeIA1/WZ+plCp1chhe5V2cjVV4iUgF'
        b'neTuJhMiK1mKppMyZrBMTym50aFqYpz9OsVcQSFmwykMryXCHq+u4QSHVrMhAbWe+muwVp6qDmVKdGRDYgUZrbtj8Do2k3f0BcljZBgd26UQsdTM8AicVfpDY8hIqSCW'
        b'i6yhKPLf6sp1pCuTbtB9AOiPJ0RCHyZy2nnnNJ3HA1Yw14Uo9XXyVGw1E9PSu0KZlFfrklOwnOosRKbNSSVaXdxkrqk3kBXpJDYbY+s8rNQnk+4g+SwKq1NoshFwYop8'
        b'AzaTy8XC4mFxPJsr8sfkNrZ2eMEXjqeSoe8tXjEIcnlHZcJVA2x28sY2X5GgB5m7TEVYljI29r0hGyVKDzLpV1wvjQrx2W8ZYnm97difh7/Zm7538N7Bg54Kf3zqGLN+'
        b'T79x5szJwowxozPzFr48umJ9/bNPlK90XPeqy42atfsm7C2vHz7BcdXltbH75DszO3c3hW1c9uvRoNfGSPLfTnnxlx0pL55TvnTlqGvuG290/OzhcfW80+dPyJOjD5R+'
        b'uay01WTb7ulNDifx5Idvf/RJU8Friy74jYg4a7vgiccNn3X9YPAyR9dDf7zpMynkrtvP/eU2STvP7ivc6Z9nPytE6fdXTkb1WttNKacOnmnICHkhxHFQ86bJ//ok5AvH'
        b'9ws31Ja9ljTgjYKYL/RDvlrdIIn9aNiJ8O23hE+OrJ+yZ5BfQ1md3ter8PacyWnx7p98ELxwcv3pq29XLWgsiD8TnH0wbOorRXWbXx2SKrwZvf7w3rD4+m3yBRNurbxz'
        b'fs+HVpZHA/8c1+TwqltC/rmL5z5se2nlM7/otRx46eW9Lv4r1t/I6pw/PWPy3dlWf3o7fLbrZMGVF1vuYHWH6N0pr//DeWLUJ0cW7Xs2KOrt5z0jbn5qem0TTr8e8dWr'
        b'ebe/G7+odPhb/refyHv1i8L3vs781PureXvq7oienTnA9/SSX6e+/G5OZNZpvSP9fKK2Ge233PjXc0M+cLvwSXHVticD38rM0vf71PGFEGczwx+cyx30JF8dGD3+7JCG'
        b'378cmrLk1pIhV1b1++SVtMrN33xidWl/+MzCloDyt1oOL/tgY1WA8K7ZvtLtZfoF/l+vG/b6qIbx+ZvXlbQOuLLYpH1b4Mv48gcN/5qu/3GQ3pLvbae7fLf08vPHPpm5'
        b'aHGCw6cbfhG/aPmXODr+6+CvPzNa+NWOjU/Ufp2TWvraKwGTHFMdtsj6ffHZn6OC5r+08vl7T73wxIQX7rx1vdYwd1NmR9CSd/LetvML3JS/o+Jg6+DiF3eZfpnWMPDx'
        b'mz4eoXt+snB554PVa8383xR97zL7xoiooWkbw3dOKl+z00ppb7V1+7m2o999dPW91OpxP7bemnmjo6Px4OaGD79eV7rxu+O3Xrx46Gnzf2b/7vbagicrv9v6bOihyl/W'
        b'u/5ll2u05snCULnVR5tn++2M8Xrt6Dezk34u9P142JtvpE/NnBo49aNpWw7+fnjHtFPRTTlBqfMbX135j6GXI7YeLLeYevvpmDU2iZ/EH9p255nHnX75V+rgjQdOux+7'
        b'lZN6ttJi6jX7N41XzhiX1Rbv/c53h6u2vfWhQnEtJejDvbu+LzFQvlRiOe15xSY84jKufYv3nivbvAtNat3L37oY8NasY1uTfuho/nny0z7xhjfDq7793rApdOcvhre8'
        b'Oz7btuzb8E1O1/aneH9To0hry7pn/Kr024VzDsVerXz8Vu2TZbGZV8T3JLeiZ/909deFz8yyDPj08oHJtR9Bi3zXncfu5WxPjGmatWBg0Vd3Dj7xzcDJd36//aXllPdv'
        b'7Yw93vGt7IjH149dTv3uxRNOfya+5mqSZtUSvr0jyf2V+B/bRg6vqnj12xHVMzOXLzx995XqM7P1mse+HrP9B+s1m3fjh1/sON/229Dfre59H7uu9LLsXu6KCm+rj74o'
        b'rz/2u5nFFfeKn/0VG5i+heehHDp6k67gYSgRC5x2JRSq1LSjjdCqVmVDbVWq7Iy5HNktFCrtertkOEnXrMKDTDUdjLuh3Yfsf6r7uA/SyaLvLIkR4Wn2hONcsgN06a4T'
        b'4bRKdSUFrGTKawrmbO6ruVpAplp5xSNh3DRwyHRrdw5Oxr850k9qAqejmW640VGkAj9k0IdDt4gdgrCWFSMVqzFH2YWaEoKtIsEEOyVz4JJPMqUax1KyTSgdSd4OSf4K'
        b'ur83M38czJUIk/CsFFplQZAfrQKGDIdSH7V9QhaKWVAmtiU1Osc8bmKU9j6+tmTzziB6/GrR1Ol4nbWmJxyBy6RDnIg8TUu4H47BafE4LIOTTIFdD51Y42NvQ8HioiBT'
        b'hRdnP5WjN9YsxZNyzKEq8T4frIFyiaCPl8QB4aroyiGwG+q7Hmj2VeiRKkIOEQlgN/LITTzvClUh1H6iBqiFujRs4SGoWf0j+esOXlg5leRuJF6KGZEs8Ug8COm4e57S'
        b'1gsLExnf635/fcEcmiTJhrCPDaUUIvod8lGxfuphh5g0igTPYRar/DTs8MRmH7wYIIc676U2MsEQ28RwCg6O4VaOTNIO55QUVtLQEQpIkQv0BCMsFGO+pxn3N9oTjkdo'
        b'CQ0V2ESqOJvSn5vANUl/ogscYhaIObGrzCTM9KK2u2CRHUs+0AfSt8MB2ql2jgojG1uokwoWgyS42wlO8QY+g51wQu7og60KIoynwynSBKbilWRAtbJuxfOTvZU0KAQb'
        b'nOnjM6GGtc3KQSvSoAKbSb1p0zNkTD2hn5UEKqiJlJVdEYWtPv72CZDRnc10KGRIoXb1NNb+sWOhWunoBeeNyX046ikIpjLJ7KVWnPb1FJbgRbm3A+Zb+m6Cc55knCoV'
        b'ImFwsHQhVEMrN6rtsYQq+ilRwuD0eiKPiJawpMcmQL6PGvt60WA9MgNLJDPiFrHBPAgPzLXTQDtikVKF7jhsJRsy4/HiTEtsU3rZKojgBCUi0sun8CzL0GWwQKGY9ASR'
        b'HE7PFeBaMh7hUEKX1sapLdlE81Ib8SLwPF90GrFKidmW3ZEfq8lKlMe6Khrq4IqGr7yAjAWVlYqoLE0s+WlYayi3IU2wydfclBTLCA+LoR3OQwY3BGUON6Y18nPAViDz'
        b'3HCCGMq3QSd7NxA7oF3uqLAlfZW/EkrJghcrjsU82MsXmYr+Vnakdxy9KMoy0YfqSXNAgWStIVzgZT+WhDUk803+VIw7jTVYLsLj0BnKTWQF66FRrsD9vF30sNzCWIQt'
        b'0AEHktVk705xcJmb2FT2NX2BLV/DHYdgKbaQKUArLMFcEZy038Zfy0kZ7MNM9kNDHWWC3FuMp0NJgehrayZ40s5J8vV3dMcyMuWdJAb9RvHpfngOGZPNvnREXCa6YAlp'
        b'ecicz+91wJHJ2OFCdIokoqAJYrguGmql4NmdjofyyLU90L2P9Eths0A+HNOpQG8VxQV6LLPgpsUck5AugzDutucGYdJ7V3i7ZVPjIi+pPbQ5iQSjOWKoS+jPsDzn+ukr'
        b'Kc8Dn59kJNJCW5Lf1/GoBA9ZQyYjCXPpB7lKLFSsw2wjaLTHVrqaXySPDjaX2sI53Mf6Xy+SYlOo7ugtWQ77RWTFquV4VDNXJVMLK5lOedzKSsY2X/8OBuJJeoKTis2k'
        b'Y/pNwWzRGqjxZgvLtDS8Ru9Fp8gEERwTcL8hHmP1kuJJvIxHY4lsj7k2ZIoQpReOYX4sT/TCAKgkJbbx3mzrM1ws6MNB8TRzzGSLghWcj6AusAHUvpJLxoMD7XgzsYSs'
        b'tmSDZRMpFxpgnwr+G65ijQqmfK0TG62xI8cq/RVxG8l2Jaezg6yKEmEQnJVOmLmRlc4NLifxRZ1pHUe8Q8lgJavDedZnm+D8ZNWKiBcjjMgjRthCBsJQSOdjpNAM9tEt'
        b'13ceGY2CeInIAS6Suc9WpExHfyXpa0PM3Ux+sQz6k13iAlyXwPHZcpbAgOG4h3RLrQb1HE7CXpVPJlzAQkPId1KZai1DxdYS5FBjpFFKMBtyiOKaYmJI2nSUaC5eJcst'
        b'Q2bHCmcl7nMYOJ3io4nGkPqk8/3hxAI8w6vjtYk8QN7YTTf5Osk4bDDnm0yHCKo03B5kwyxXo8LDsYBkG7ZykeHFQMecMM/PXuHlRxZsdhSgJ7jOIPO4UUYWqgP+XA64'
        b'Oimiy1YN6aO5qdoKypOpe2PcErjK8JQ5KHs7lmoFZtcTQrDRwClyMEdquwiHveEM1MrZkw6b2MLbj0xRoo2emcprSjoFSrpRdMO+YSJO0V0Bh/gJRaUzHCFjg8w2H6ih'
        b's81DDPUBUMYm8fzHXGe707t0SS8TQWF8GOsT25AJ/B1/Rzy8hjTeZInhzngmUiaQpatUK9guHvFkeLvz4QgrXdxkrIYMvKSuAMumH7ZKoGY5EQaYo/xF8npld1R7utiW'
        b'T1Kh2q8i45MOnyVEpCocj2Vy8qBAZlabiGzS55SsgvNmS+SYpxJ26qBGIhgI4sV4lqMqQyGcIIvp7hSy0nuLyKuX6KS8uIIP3SoiR9J6Gnn70fFC5owl7FkOGRLMgQNQ'
        b'y6E6OqADr8sVgiAaMmuCQES8Ihe+QzTjyZCxq5T+eMGJyBFssTZfL4E8yNrBSi32TSEzsROb7R0d6XpQQTa3SFJxJkMcWZIoJ7k2UsgIsUI0YpSSNYgFGSetSl8v2GNK'
        b'2sxQXTEymbFI6gaHkTcIZOM1vCJ3YJWSjRiO1eL+UGnAy3V5GJlqlCvH38F2KZygI5tM5jIyJK6zFhu/g2zuTrbY5Kkgy0onXYyuiT2hLIgnfRXbjbHZwZ8bKHYsWy/C'
        b'0lmr1GDphY59IZTFcFVq4YBH+c53cRCcUDp6pygMoWgV5hLhTSwmg7SaTHcmXp1dbqwSqb3MbIjYuYD6nVyRTPMk+xibTA1kbakf56tx4uYu3KVkY2b7zrRAH0e/4XiM'
        b'rNppohmUFoitzMshayH17CY9Xspdu62wg8ujawcx25yXgx2cUWOfkL34kqLffwY3V/aA+xzRgofiypKYkZ+dCi2hBjHtp0K7BFsDBlrMQZCNRBYMx4OieVgyAEJ6qmPA'
        b'/MkNVEDI9NqK3LUUD6E87ffEEivRkHtigyEi6x/EZuYi83tSsdFfYikFTjYVjRWPFQ0hV8Puiv8Sm1CoY2PyhsUfYhm9HiuW3bMRmf4pJu+bi0aIzP8SPy+bbsSglRlU'
        b'MgVMFpmLBv0plg0jv2luUtEw8nPQb2JDC5IX/Zt8ajKIlIXil9jcI2np3SdvcncYeZamy6GXDUgalqQ8BiRF059lcoMfxU8a+6jRTjj7vDX5+RjNWTToLzEt7Z/i32WW'
        b'BqKtg7Uc8fCW78Y1+6CO6xbi/BTpqmEy0meU+ErHkdNu4RMr3YdOuktEisEC7YnEKgT7+/srpOQHc0WvM+4Ff5K0XmDh3EHzPT38PIIY4AkLv+b4J7Ea0BJa3iTKc8eP'
        b'7yz/K7Ak0zXNdYCObHpCt4f8NhBLZSr87D+k+v+HVzdlU8UiUzMDdqxJGvqe5Uw1eAkddOK/pBL66YhdghEDkIUSU7KsZJhqs+eLhRkrZERabA3sE6FvpPqtNLo/fIkk'
        b'0kB1bdjt2ohcyyON2bUJuTZVfW7W7VoFZVJpqIEpsYwc0A2mRNINpsSqQD/yMQ1MydDIYRqYEgptIkSOjLR+BJiSUQWyyPEakBKTaL3I0ZFjtMKTUECUnvAkNrfNGHoP'
        b'I+J2j1obm3zXqQ82Sbe7/wYwiSsPcndRiG9L5wcEetyWzHOZl3SIDvIK+uOI6OERQlx5lKbLI8GKqF5yfXToEHV2LCh0AoUOSarhMTwU5CPpFAMoCvTwCwj2YJAhY3vB'
        b'dQS5uwdGbeoZiu6cdJpW+GEenaDB1VAX5O4gXalqwDZ6lllh2CMN2g9Jr3ZH7FA3TtLrtEav0Vu68piQ1Eyf+c/ibGglFO3Lo6vnz7xUTYmooMTWNVM0oICrkIeEQgvu'
        b'pbRam0RbAxjiGVaOhEuxb76+S09JtdIFhe98GfbMWs/wExduRtt+6BNuFP2Z8H3GYNdbomlx0uaWtQqRih1lNJTYQd2QqC77FFGLj+sgC72k9hqhAqJO+YB+WdO9cuug'
        b'XvPsIRE7LPRVraxzO6Nf390HuUN3xi20f29SWA5q6f2vwXJQXP9RsoeF5YhkJae4AzQK4P8Sk0M9TR6AyaGeZg98wvWhMTl6zlxdmBy6FoD7gGRonczan38ETIze8V48'
        b'NCE8nkYV0LAtHUFImte0wa/2wdHo0c8q7Ay6iXA8DLKR2OqOF3oQaIW6JI8CWxEb/T/Eiv93ECvUM04LYAP99zC4ET0n7UPiRmidwP9DjfgbqBH0X98QHj3/YObgv24c'
        b'ZZHqg1cgglLMdaLOcr4qQt8ux2XoxGw5nsJD2BwbcHuVWEkdiaQ3zlHK8s/urIte8fibN1698daN12+8c+MfN967cbXo6IFRWRee1c8cc6wuU5F/5c2qPeOy6iou5E7I'
        b'GlWe3qwnpL9hsni9sUKPWT5mxUJFF6zA+u1iZ+i05Ba4IZgD+QxS4MKgXqgCM/hxm8N4rGSnrpZ4smfo/mGoZ8njdTwwjlpWRCNWM7sKHocsZsoJSR3clzgPS4cbQFWM'
        b'2k3033GX1QTT2zxI8FmgDqqXaZNCHj1iftBDyUJf3CdyXmcpHipsPloh8k+6LFLLaFpC5ufpqxyb+uakiZcfrWO36xMjL7u/I2+Efq+ZIVfPDkr2kq3fS16TU4ktWq6S'
        b'1/SZvGZA5DV9Jq8ZMBlNf6dBULfrbpHvO7TJa/ePfO+uU/4/EfbeExpMJQSpYsE3km2DBuX+LxL+f5Hw1v+LhP9fJPyDI+HtdYpKcWQn6M6U9kiB8fdZMv6bgfH/0XBu'
        b'iVZZ0MKf+fIaQvXQLoAwMVTCOVM4Dsc4SBi1xfsFeXHniSBPzA1wWAIFRExkGF+e3ljAqMqWUnQtA+ZgD8WQbwhX8TQeYTBieC5cjjXYrB1FDLPgGqfGwAbYC22wr1uI'
        b'eLBbykRyK3Em5miOuRd3C93l+F5OcIFDfIkFOIjHDfHajIAUyje7GI6t6YpAxRxPex70gTl+uM9QyiluQ8cbzIVKzGdvpEILHvIhsjAc92bwXSpZmIbU2mOhH/cGC5Tr'
        b'Y8GqyJQ5AvVya5Co2GLtvUIWLcXTcMhhyVIaGezt5wt1wZ5wztPP0cHLjyTiJIaLchfIDwwSRkClaRxWWDC/8kGmkD8Iz6rJOqDNFOtYzbFI6Y9VUN49B5I6jXNNdEmi'
        b'wa0s2lxKI1D0oRSO46UUGlEUA9nQEUQfHWlBH1b1VjB/SZWWnrAyWp+6rE1nFsPhWOaPbWHyJFPSkJJ+opnYgKe48/g1H1Kt43Aam7Fts5KGoHSK7MZiI/O8/8JYTzBY'
        b'lC4R5oTFeRi5CLGP/VQmVr5M7nx7OzZk/0xTcDbO+rrm89nJER9ZVmZmyZ23zJk7L2RF+T+yHKM/fjZF+vVMV6+YJ54ZnOg+7om1nb9u+9brg5Ixe9dMtpMtvjJgh3yo'
        b'vofn+uDhTSN+NHihtsDzly0eeTNWPb5x2sU5n5x5d4nnMIMNG9x+fPOrj4v35C8cOn1kbfJjU6zaEoK8O+OeqfnF8VvfYb8ZfeI+N3HBVL2PRxTbKQ69M3/7ky9tXqH/'
        b'nu/EpfEWa/76yf6dg1Y/5ZcdXRvUWXe1IvXZZ9LO781r+WPqP8v7T1lT8KzpRdTPvu29JfuuwpydLU+W21HXICG6O9CY+yamTJhi+0oVfpmUYnRpIkVT8Bw7iJ+PZ6eR'
        b'Hq3RhIp643F+opxuLuIc2nhhS7cwTmiGUu7zF71GpaeIMb17FCeZOBn80DrTsj8fKdiJlV5d1MXF/blH3fUQKN+0kWlBXAc6uZadLSvwuDubKKmzuwWpJsIlBnu2csYK'
        b'PIHVvf1v1b63mImdzJ2JKGCF0MjrAGS80CmbS3IibSLxJbcyWOtNCMYSPA9Hu3Eon90MrcxhI46sKyXTNvi4eNMV4LxAlooL2MYdrtpxr94wLO3hDgnFWMdqPgz3b4cr'
        b'kXbefnxxIFXoP16CR9yBk5dD+Wy/LuWSLjs5znAkhLmCpK2Zri2YUyI4z8WjNJiTlDa9L6+d/P8wkNL3QZphIgunlBgwpl8DmYweJIssVUzB9MiafpmKTcUGLDRy68je'
        b'2pT2+EfDh4l/7Ap91NPtDKCvm2RXS5ijx0Mpph3WuhXTB1XwvxDpuPqBkY7aNLq/FeZIzzn6hjmO8Wc70FboiPDp8gV/+CBHdzwzAE8HpahYJxshVxPomAjVztAkrJ0/'
        b'UyIXRiPZ4vZsgnK+T0+AMmUq5K/ugknYihk8HvBAElwmb0MWZDqrghhXzWSbxM9TxIJUWOYnFsKM62cbcUyYITPxRFeI4nasFqDTMokFKZriJT88KBGMsJkFKR61ZRvl'
        b'JgOsVm6iDqCFZLXZLUDu2jXsxkosTVYHKPrGiTAdsnaxGyFrsFMVo+ixWZBZiY1nr1GFN23G45oAxYNYKcD+gVjMK3LZcExXdOLi8TR8KiMwhTPsQA2eV4cSes8S2UK2'
        b'WQpdn0e6YGv3eEGRANVQwwIGV6eyRhiybL8wTGRjJHUO8z+xYw6PljMfPlpwF3Zby4Uw8S696fxD5+WeQpFQNEwSFmZUuHDzvx8v+BBBZlfVtpiUhbSeWYF4XcWHYu89'
        b'APP8HDd5+WGePR5QuSFhMTRToBTqDaiAVokLEWx8yIrcrJRjA9nncsyCDbxZbf7YRqMEzbeJF4X5zlhsxqt4cTCNErwjl1iHzQBFhMDCbaFNCR0sSlAdIUhEszJ1lKAB'
        b'nOHdU28HRzRBgFiFeaLpjktZqh8tpWGAi+zl1mHG9qsHCAoRhyzCs4uIJHUR9tH9mkXuXcfy/0bonsRA3ap09GzHw7M1UXu22CRytYHLLHAv6rEFqrg9yIQMASoi5nHZ'
        b'q4g60DUb4+7l2KqO2yO7bC4P9yvAsjFy8tQlIpcuFhbPwEYen3cC0ifLbfD8eha/x4P3cI+SJblyNJaqY/coZxaN3xNh2aqdsdFf24mUZaQUpuenpAR7HRzgYd5Y3/hN'
        b'20/G6ILXRLIiv36b3CNXmS+XvfW03tTIBau8hw3d/udnE1xDQrdbn+u34MdXJHOT7/XD/h+8kvnBjYMxpn8JaP2ry9kRE05+MCr000Ohn5x97rnz9S97TCp6PiJUPkb/'
        b'+6HL3XMbSha33Mz6RfLrP5770fyfj68Li4IZNjVzNzbK9RaYfbQZnvtq6wdfzLt15pRhu3jwCZMfzkxdnGObMXn9YuW+N2fYVk9b/MWTnT/s3Rj8woqP/Ia++UnDM5I7'
        b'VonPr39b/PqU+ttnvn187dueC9YbJrw66bd22dnCqM6KJfc232q88P6yGjPz0A1urdNGbf9opPvrFW+22oh3zYyTxL1z533Xee3Dnt618cctFnYpq1MUt26F1f5qV+83'
        b'S5nnssHk0uArK+tjJ36xoQ1aR0Vs+97d4bfsf7WfDFZEfXPpx4TN01rzZy7+OvUZg+ZPWr/4R6Hi05jCb8IDggPc9lReGDBt1+60vIqOsNfdZBdOv3u4JOvds8Hv9lt6'
        b'annM6++vd2lOML1VhytG/TL4zZ1vNt+8uUj/nWZvxd1h1frmJ29+Gq5/zj6kVfhW781RSyOmlG9qSzVpvTdmYcyBX2am1rnk3xy4+uYP1Vtjc7adnPP/8XYdcFEdW//e'
        b'u7u0pYmA2AEVWboiioi90DuIYgGkidKXYld6E5QiTVSwgCAgglIteXPSTDG9mWpiYnpvL81vyu4Clrwk7/u+8Asy986dPmfOmXP+59i/NO0Z8YnWRf8KfWbNH9N+HN6d'
        b'UfdYhlvdbp3Ml589v/bq/AJ0s4+PaXts987W5/uqpkx2d9zpc2R5i4btWdcbbrtOrbk9J3LtB0WJvY+Xg+8jHz3SeDtkc2FWu/Yv6jv3a/2u/olwLvuqr8c5o+z22/Pa'
        b'b8yM+/dPBz75Y9mdLN3MaZn8C/++XXbb54+7/a67dufvs6us3P7W0pSvIo6d0N9dO2913exVTr0x3b9ZP+fZ+lLEux/823lN3JwbS9b98XTgu3rxQvm/xOn7SywcHr3r'
        b'mP3T77u+Ox35x5ePuFzbofPZ91HlX5gfmvf581b4b2O3nw67TcrceqQgY9ehec88c23e569+P+nVT/a++rVhfF39kUl/RJyNjI3dqPd5+IpZGXdvfZBkt/PLtIkt6Xfi'
        b'Cz7I2/tu6Xw76FD/asbrRiY//KR5zejowPzH3xyYeMek5buifdv6fv71m/qy9WYzImoOlM1KbJ/7+bviX95yOZO5TdZ8Y/L+d342/upmyPicX4U+8e97ri9yL4l478aB'
        b'd7ofubbu+13xX4X/+tyvc3N7j57uFQ3tC6oO2PXqMc1br0zcFNmSOvlkR2JfTcDS+W8WfFfYdyphdtx+SexXX3cFuB6b/PitgNf4H+b77/nJQSLTuvy56PtYaA8tLT15'
        b'6XuN6RM/ecHgA1kyCyU9AJezpFab4dKDGXKUA3WUZ163lnhanrVhTCg91IHKqMAxKVabgeHQEKoc7f9kE2pmEkn9XnRwFByOkBtUROBwYgOqmBHBCVcVhA0uoX4ljE2s'
        b'gyr9me17DyqZroSxJYcSIJtgi0q3MT/JvdMXjkKx4QOzcj1FscEAak8ntm1RNjCkQLHJPGWm+AgiQBclkG0RylNDvc4zKIsfmYaqlCA2OOnMqYULVg6olrYCy7x2SqSa'
        b'xnSCVRNmYTJ7kb6cjmqdvGyg0Zki1RQwtUg4R1/ytmpSKMpaqDRgphg1TLjpAGnAwNbREDWei45kEDWXzVTpxMNhOxU4bZ7AozYDaGBIiAMwvAN/iwahgGLUGEDNBUs7'
        b'5OzB/EspNxqdBjlQoUSoobINtG2pcBk1KBBqq+EQBamJMB2nEpGTZbAKn6ZEp10zRWcWoGE2uX2oGw0pAGoqcFquK5Qu2c+EyRMpu0fB03DX0VkKT/NyYQJZ5Tx0UGqH'
        b'imCAYcwYvmxeOLVvnuQA1xToslUwwKGzVnOp7bWwNHU0tAx1Ooygy06jDtovq0B0cUTMg4pwAnwjL+nAHYMWK6mvrbaMRAo9hc+uUzx0wVV0mS2pbtQxewwKRcxBwy6C'
        b'QtkbzKTUPmO8Yn1tlMg1yF40Al5DpJxJlP/sg0Mq/BoxVbck+DUol9FCnNKWST0J22jrnUrYbSiWMQTbNLEYXYBrVsyG/RoqhiMqqJqEC0FnKVbNDU8CBXAcglNwaQSu'
        b'JuEEdJjC1Uyhk65qGwKqVEEbUPYiHpVDfkI64ZEN/E2UeDWtvRy67M0C30+HCqnXGH9TbqgKuiYoAmwa7MbMggqpNgMd4tFJuIKOsRafSIMWr7HulKAFSowkUMJwUZdj'
        b'0REFWE0JVcuHbjRsGM6Mwo7GQ7m1nSY0EsCaAqymha6wuWuHiyuldoboKMOrMbAaJj/9tHLi0+DCCFpNwiVDPwWrQbuYXg8ExYQyqBr0WhC0Gg8nNHDRdDlX6qM6FVIN'
        b'hlAzQasRrFpvPF2u46EYlY/g1FAlwf4NmcEJhi/phTwYGMGqoWYpj04JMMQ6fQkKYZgh1pR4NStohX7UxIBFF7anK4EmPAddvgRoohNH71zsUPt2JWYN860c6pq5hymk'
        b'jywyHIVWm5rFT949jjZmQRrUjAKrwXHI4dFRLQXQCA6iRuKEYjVUKXlZNeiiH7rCcZnXKAf4M90pZq1pCW0lr6/LGsngM75eqB1VYzJHN8Ulr+QRxJquyyjMmghq0QVD'
        b'SpVQ7QRfgldTgdVidqvgatAD+bQR+6BFpMKrQbYJJ1nLQ4kYGLzPGx2E815QgkWjIoVfMC84xhBUR+HcDiVibeUUTjyO32zL0Bx+Pmr4BRY4htOVgDUCW2KTc3w+DI6C'
        b'q0EBFOIsWG44z06gg8H7cKNdIZ+g1hSYNV9opeQoNoPA/2QyLbxdyL3oJXu4hDtkAt1ia6g0pgVoYhpxWmopQf2jeGlUnU5n0RaGPPCqQpfhoPJOrdeKUaKTU0ylymLJ'
        b'WtdClcJGfOpgBt+CzWS5N7oiZZibsKlENjVHTfqsUy2YHh6wVkFrteNEVnBFD7XgFUPPh0uT4bRcFpPhSY5ETRVYbuoiMarwRDlsu5VbuCrRctCLDhHEHMHLlSxjDRyI'
        b'RBdVeDkFWk7sg0lgLrSxdV0LtXNogNuKfd4MMAfZcJytmJMwvFCFmDsnHwWaE6ETiZh80UVeHwxHlXA5n5V4T+nhI5mCcOpxo4+NwrfhjVOMmii+zV9x+Bo4LcV0yj6I'
        b'XfwrsW3caopwXwvDVipkG25Wzr3oNjV00g8u0pEI0eblMjZUcHolasNSN+SI0o3gKB3N+WsTyIr1kmlCicwDLsxCfXQ0J6JssRvK16Treokz5qtwLr1FXjLaU3VoFJbD'
        b'OUM6Ya5wEWWPgrDx3AwbgmBD9fG0BdOgz191iU+vZVFePBzdDOxUg3pUgE6rrkTxWi/i0TloAAWM9xjKRwVyXK8fXlKHrOfCOUx89XeK9myZRb+PQ9VbrfEyvBDrjQ83'
        b'HzJU9cJudAbvJjLYye7Ev+5BH7yrMcdIGKgTmDnguXFGor0wlJE+h0zIcdQybxS+T4XtQwUT7of3mUIz7XeKw5QRYNxe1KHCxnnPo0vIdw86y1CyDCK7CHJQm2cwXf8z'
        b'ocJeBcRGvdN4VGaH2MrbGe2oRAETgiojKGAJyqb3tbHorKsKuQdNmFEY1TgK3QtGFQxYOAx50SPAwyx0SIU93APVDLp3BlfdaW2JidyJMfA9BXbPQY2t4x7PbSrY3lQ4'
        b'zKOz40PoyKfBtRlSKJkBbUoWkQD30CFUz7ZQXxjqUaH2CBwP0ybNFLoBNzijUwy3l4paR0H3RFC0aFs6cW2mgY4YMcxe/HoO8nkrhqk8h7nGZhVibzo+7ZSgPXJPxc7h'
        b'AR5zZirMnjGpF5Pc3Qy21wY9Nph/OZzqw2B78UvoPtCB/FQ5PuWUkD3eZxRoLw9vFkq1qiEfTjHQ3nrMeapNE8YvcWaH8EkdTIrxKYJaSRBvWyslaM8SL3OyhzQDUIfc'
        b'Php1UdieErLXhtcSafPCDLwFFJA9aMvkJHt5OILyLSm9wbSoGOoVqD0LqBoF3BMboCJUTGcjOBKdYag9BWQvHnOG1XiST9EGGmNSXj8atifmNI0pbE86ni5nPTgNNaMh'
        b'e9AOR/g1eJXVsugzOcF4pdlJoc6HAfeMxLRjIhJQ29ozeNmYyORBcECm+/+PxqMwKapX8P8zKB77magE5OmLHg7F01BB8Qzoj5jX5fVx2vQ3QU2f/5vQO3UNBRROTOFu'
        b'Gndx/rv053W1+feB8f4QxAx4Z0i/0CVaDwrgM+GNeTEu1Y7XJd+r/ZcgvJe1XceC8EweBsIzvlf18N8i8IqINoSg2v5UG3KA++VPcHgPaRRuCcErpN1UgvBEBIT3BK+4'
        b'ppSN//8Dz13Hld4iWMME7n8JPPe6mrXA60pGAeVmjwLKKZ6ZLM8gOky8qw9CrjRTBzUuYVfayvtsnrNE1ySJsaH3Wc/qKv6V59yHkAsTV6tXa1aPjxXI72pdxd+Gin+1'
        b'2L/xolhRtKhMiLZSKZxIlB3tQp1C3UJ9GjhbmyDtKDJNEqMWrRatnseRgOFlQpg6TmvRtJSmNXBam6Z1aFoTp3VpWo+mtXBan6bH0bQUpw1oejxNa+O0IU0b0bQOThvT'
        b'9ASa1sVpE5qeSNN6OD2JpifTtD5OT6HpqTQ9Dqen0fR0mjbAaVOaNqPp8ThtTtMzaNqwUBLLK/B2RvRvEoBcI8yY2lyKqDJOo1CKx0YPj804OjaW0TKcY0K0QJF51je1'
        b'Vy73CV6l0KTd6hPusbEkRk6jczBonspEJz2ZhJeQszxOc23Yv440GAP5a96YwpQKO7md6fJR1oMKYziKKFCY3OG36TFpNFZEciYJhJs+1vpvdNwIG9OYyKitpmkxKWkx'
        b'8pikUUWMMk8k9q1jSniY/c9YteGYhG8yMfvyiDWlEWDlplkxaTGm8owtifHUkCk+aRRQg1pW4deR+P/0rWkxYytPjEnfmhxNbddxm5MTMmOogjOD0JeEncRCa0xgDNPV'
        b'8dTYyXK5TGG1mzDWBIxYSimMCNlE2CvmQTniNqaWK2TKbJGm8hhizJYe82eTRObQcqWMoDsiRxkMKkz1ktPi4+KTIhMIzEABUsZDQCAU93RULo+MowCTGBYABOdivTeN'
        b'jknBBFVumswaTq3+LBXvVpAVlpgsH2v8FZWcmEisk+nau8fC0Fcm3BTtSEy4qRYVmZjuNC9KNIrsSBSkhyqiSBwFBXxMvVAZpktKSQiPiYgQq6vQXouK1HK5veJdBntE'
        b'VHstphpr0T5x0Ki/Rxko/8L/BUDZmM30cFuzh5kf4h4yy8N1Pt4K0zkakYWWOzJ3eJaoeSnemg+2SbWMYUvqYfv2T4BOdHhdCF4lKhLv/AjcpAhmAsgKUxUyevk9JE5O'
        b'ZHR0PDMYVdQ7ZvmRhZqaEaPYwvIMvLdUJOTBAI8xZrUs/A3ZgZEZ6cmJkenxUXTBJsakxY0KbvMQqEga3pkpyUnRZITZvv7zYDVjzjodxaIba10w1VdOhJTvYHPvCz9Z'
        b'y9rTZddlfaW3vGWv9mTLufi9GmfCm5li05qcryVQsgD1QgX0k4vDdCxDyFAfKk0wleGjtwexTzAjXuJDGdVgqr4UoWuzUNN0dA5Xv4/bh1oUTo371JlTY4f5BQavLjPn'
        b'MogwtCtqz2Id1IuJ/iJuESrDZf989+7dxbvEJFqNqYNFh+uVzHlcBr27PgSH4SJ12AzVjg6QvV7gJAt5fzgRIBMyqA6lRLRJDiW6UJzF1AtYcC/eYKdpZclzc6FazdoL'
        b'Gmmt81ZtkVpZbkvlOcGHXwC9drgAIo+EwUl0WlnCtCRShhb5xXPmLhLzVFTBtLfHUR/0oYEAKXsngiEetS2HTlwKGbZoOLFhTDM8rKygE4vScMHaw8uOKDnWQp3GFBtU'
        b'z9wqX946DnrZq4xkLGs6CUmoZbtMxGLBdqSgmhRoIaFAbKHC0cFJ4LT3CttXzWGvWyEHCjUWjrxW47T3CQmRwRlT2KCdQkUzpoy85jnt/UIiuoJyMrAQymU5Y+mIRhhx'
        b'XxEX7E6yBbiPVt+s0lOfgHOfySDCty507mDCZIAtsPuU8ah8u60IndBHBdTGAMpmEOXBiOmKMjgLFHt7edkKqYvRsSlwBZUYQQ/0eBmiEq80dEaqBT2o1DMwiIuJ1V+A'
        b'TjFzgue3S9g6mH9C7QlPEy4jDD9c4wl1DyifWHPae4ZYQrE7HAwiRpReIdCtWrfUaMbPQ2IwC1Xoa0E+OiORwODqWahNxq3OMoRjs9EZPOLkXsBnNSpNQ53Qq5eShlcI'
        b'DPAWZosUgYsyoBn1QL5UI41ECRITAPYQ/Wj2UpeM6dCrnUo/6eBnonxURt9oQHswqt4kT/El17cibT4CXdRjCv1qdAxOe6IGeSr0aJPvDvAzZShXETkXS7V9y+CQtRz6'
        b'aKnoMm9ssoEawBigI4Hz00dXN1WSwS5O58El1Ci5b747UzKIf45dqAoOj44q42Pr6TchMcRdlV8xnugA9HJwIkGKzgZaUjNauIi659/7qV5iiL/tWvYJB5V47Q9ocKbo'
        b'aPxml7cFeQ7e1/MmeiVWLZKPn6P/xKxje65+d8y+uMo5VeOWz46CvMKqiCr/25OfL/DojVKrv/7zaq0125y1Ygqub1y9+tZnE5dwK1cvX+3xmH9gYEzdyx23S6Om5X/4'
        b'9rU/hn+tstkeOuHS+N4bjXbfa/pHDNW5/PrY209+pPv18q6Awo3PGFasUl8UbPCvX3QHZPl78iNuR94OfWbaa9nv/b5x15ThZcerbkjPfdR8+MXnPx/QX6axuugdlxLP'
        b'mz8F9qyelpzo+Fj1jKm/fWT12nezKqZ8opuQsbynOnOpe6zL9K9kW2bAR4Ev/vHOko8lDsYv1RbMCd5ZP2H1uMjH6tJ1zpn0v7Gq5siq6ufXyp62+OKd6h8vbAtbNeex'
        b'joPfHMxI1N7oYCePyUn64NizVtavZ90Yili18IjP0enbWh/LcY7ae/7u8zfC3h1szty8sfupx5rTrn9Ua3bos5Pp3/Qdl/ntii3/9swJn7sFAfNDnllwLC9z349dj+Rd'
        b'0fPb+Fi7JOT5nev1X9uidcbC7QkzF4uyGc1frJyaYm78QvaXdV0GazKNA+5abmrcPTU59hH5yrcMK3aOO2u3/pX+TzubhxoXhqZ8dFwr2jSpdNH7dl/6fVGRlzGpoSnT'
        b'b1Vs/idaF0JCnln7QlDS3O8v988L+fo1HTej5y5Wd38Z2jihyOlC+ezYTvv5mxftXNLc/PqV30VLdRzsO28On79yMHlWy5zfC+Me/3bK77Wt89EH6fNt/Gw/aDN7Lu39'
        b'9Mi8J+IT7z7We9DVd7jQ1a2m9ceXOzKeHf/OnLuH1H8XnmkxHL72SeKyx37TvfnKxiinbV/N+yq5JfrEVzWdn37S/a9nfH+q+sjv4yWvTXkuKLS5Ze7BNq2YHS9e+FW6'
        b'6Eb9xDWJ3XMvfGW66kz5UzBk9qv27XHfhP+u5vHFuG1PnpAtp0obAV2AKms7nyWcgP8+y3t5Qiu9IZuzEA2gUnSeUBBMV6AEtUOBwEnRZbyz0AEDekmUyC209vB2R53q'
        b'+OMifrEd6lfofDE96LJGB1NHuXUVbKHIml4VroS6GFQaYmvPVJ9qEYI50ccwJcZZaESXoBSdsiKRqYgZ6z7BSrIvnew2W6jCm7DUnuhyve1QsZ+njce6VVCOiuzdbawo'
        b'vlOdC8enbyeJZ0Ovm2umrdRZPEa1T9T6cNqQXfHV8p5QunGfjQeU2apxapuFGahAk92kY1J+mMRftpHJlkET6fpFAS5DaTTTEBXilnTe62MXtaEr4s2oHg3Sa1nBAdru'
        b'Q1zi/uWJNYhehRrnHVllpHDuFbFdcU8IrR5M8VwEBeE02luryr0XD0eWyumX9vjkb7eCXGsP1InPcnEcDwWodhW9OF0GdZtQqZMW9co74vtrEjSKU9GgQG9656DhEJW+'
        b'7iBuP+raY8HMLkpDzPEoe/p42RLHeUTJ5qsoYSYckSwivslo/6BsiY4cyjzIfHjp+trCRa+UJQI3bY0YnVmxlw7jhCmLUOtaogk/pEkzCJzOagEGQ6ewW+lSZ7zKSu19'
        b'bW18VNXsglyeM50jhjOm0ENHIhIVL1DedvpRHT7xUQYF65l+px2PaQvmvtpQqZ+dp4+Nhw/P6W4VOaMOhRthdBHOoibTCeyYVlxf6ziJ1KEIHWFLthW1k9h3LQkknrcX'
        b'lKpzapqCNjTZsYvknJlyk/1yeksv2s7vgUMz2a13qfMs1GU3xhlnrMIoZfkkPFCX5t7jYLIQhmiFtuiQBa6vyw13mCpAJdDAwxD0+NHZsYDhPZM3SO286LV2O49O+EMO'
        b'vR9Osrd6oMtNVDJVBLU70TWm5y3GbFs+UTJCg0SlSuxXxAuCHHR1pZzYIYz4zeQ3a6Aq2ikzMRqANk2icyIhjURwlEfle5awL7umknhFp0mvDlmTtvXyqHUBXs109x61'
        b'xi+VrmVz0BkOXYZ2XAflVYcJV4ZKvVGFUokhgSGBh9MsDNE6PH9HiYtSaIIBpu9du5LpAYpwMTWu0Ermd0Tra4C6RHg/jqNTbLoO808Ej0CUUvgD6oa5QSDRA+ASW2tD'
        b'eqjpXtv+RXoq6/4CX9pD26V4LV3Bre61VijJL/GoCw0xd87z4fJq1DOTvaRMlBqnGy1aDTXQTWnUTk1Ui0qzMuGiTqqKISOOAK0Jltseyt19bPE3Qas1dF1XsUErCECH'
        b'5NZamDWWYR6sgOfU9wrzxDJKoeZD32q5dRpZ+C5QK+HUY4S5Gu5MsdhjiLnuUmJwgcr8aABACWcE7f4+4nHqilWGrjiiGikpGReAihDeOuqoXVic5M7UbWfWLJqOcpWF'
        b'4IWqzun6ipZhEt/Pwl5ViObI8fJ0RkM8x0M/rw9NtnRHZEzEBVONjRxhpih/PWpklh59eGO2ouwJ9ztaNNlDlxfeMHBGYTIDp1El8eDcCINMNV6HKtyJl1A4Zc7chKJm'
        b'VE6pUiQ6Q4yF/HBriHXTBkYs7N2hTMTNgBbJAjiaqfBoGzEOekzkvjKFEZUXz+lPFQXMU/QpAxfUrXC3bIRKODQYC6dpy+biKcpGdbPlTKsiQvn8rmAoYSZmM9B51J9l'
        b'7WnrZWvliwmMXpwoElrgAEWOrEEX96vaRlrmx6vh86iYqLRlmyXo6HK7dCIG+eI9d1a5PNAgDI/w7GR5+M3HrOki1KXm6xJFx2NXbAjUc2OgIIG4sWTuEqPQMZedUvJK'
        b'ebqMgyER6kxVbsbO5ajRmh4/thHaapjnHhZQhdsCOk2To/zudwwJFdpiA3QiUKbz36tx/pfUQQ9yL0DCp/4HZc9+LkaL1xcIZESNn8JrEwWLQO/Sf1eT6FMVD4miRdQg'
        b'aoIG/UsX59Plp/EWvCVvIOiTCF34ZwrNq0/VJGq8MW+MyzTA/+riHw2cW0tQE4zvfcKTH12qbiLfqingK4b8LqPRF033eDqQSRh45BZRWrw/FpCi/V/NhYgVN1K6ajw9'
        b'sCQpdyXj+ecamQPcoMXDdTIP7tVf8pyw9T96TuhU2pXfU43KbcIc5W04vU62MY2JszO1Ivdhdg5OjkrvLvd7UfhLzcsjzUv5s+Z1K5v3y2TSDsXVqml89Jga/7IXiTb+'
        b'pkZ4FLtzf2idvao6zSjcmWJ8Y03pZwS0/7drJrMg42/qhKtulMPjH159n6p6i+WmGUnxqRkxD8D2/5Pe4zZohytvF/+sCYOqJliREZCn4yGg95Oqq8l/2ow4MuMT/2zG'
        b'L6vqtgtKJj6FkmKTqX8E08gtyRnpY1wU/bOpSCMOZx5a/7WxK26Uy5y/XRld3u5/VhlSVTZppLIVHiv/4cB6/VldjynrSiOxfv/6aB38s0KfVHXAMvgBjo6UPjv+6XLV'
        b'om4HwokTgIc24emxE0Y9B7BN+48mTEZIBK01Pfmhdd5Q1TlR4WXiH9YYqyQNWyITiFIkPDklJumh1b6gqtaZVEvyspv6hNEqv3vdkvzjcdBVtSoqIVke89BmvTy2WSTz'
        b'f9Ws/1NPlzx3r4ZC5Bs/Y1WASE641w9SjnwW8eSXFls0Yt/zFnEaRfyl/LsynnL7sbHUNE9hmGduq5CA0AWzh7iqnK20nyEM9n9kqfZzcbsM7znqE2KSwsMf7qiSVPAa'
        b'4TGIK67/yGMc4M79ibvKB1b9fzItW//atIh9g+MndT3KycnjtfuXekVq4znRchFx4tm8pUHUyEq8f+QvcGzk0/L4+zib8PAtyckJfzas5Oubf2NYz/7JsD647jHjStpO'
        b'WkCkK6aoHfH0qfQnxZS1fKGOSlErFEnwiIvwiAt0xEV0lIV9oqBRfz9sxGn8Tvy/45gRn+5LlUO7RFiAgyboH6Ui0EXDVE3m66JQk6kVZRlMlygCCRbYo1NyVK6tm6ZJ'
        b'8p/k7aAX1VN9ygxrhT5F7Uth1o4wLoPaiJ5GtUvpDQvD9huhSuIa46AX/tuXeMsI9A+0XStwm5epo2a4CmepqmyXxzYvT6ILQOX09sxzszm51JJwVlESdM4aZVMVhhN0'
        b'GuDWbxql+xiGIYqsRcXr0FnqAAT1odbRtsBQlsp6Uhg4FUqDtRR3VGJbHnX6QTfDSHZL9ltvmDASvXSlJv1mSspmhdgKJ6NICCssusbM2BTMdGXNc9Fl2ssL0CCz9RBz'
        b'muoCKof2ROZDdzgB9XjtTKbGvGIxj05ABaqgr+bvhwJrO4+56TYyWzVOcyEJClWTTl/thO6FULoHekfCVcGlRBbcshSyoQina6HU1pdKnmqbBCMduwxi6zwPy+ZtXlDu'
        b'Qdz1eUMpHmxn6FP6KbBeLMEjUw1N961OqXJ1eo+szrFrk1d5OPs76zL23nVJeqd537q086Vr70tBHLFbwOfMsgibZbPnMew3j9rdGa4FKgNZ1I6JaJANblNkMrMLhhPo'
        b'HAvStGIRHSb/UNTBJs0FFfoqJw16N1FVVyacgwPsNhIVmZELSYMAugT4fShXTiyQBT90TYOfCseX0OezodJREaAcVa3czNs7ZCqWU6yeEoHB6bGAQXB+Cn3nNgnylPgZ'
        b'qEW5NNrTRHOqUjPQQ40K9MxOdE4VjxxlQzfVetNgm9CkOYcc3GZc3EozVBkqk9AVNxNl+yq+Rc0jsczhsJRWO24iOqSEr6hBK4tkftSaafIOoKOhSuDMJnSAWC9T4Izb'
        b'ZDagV2AgjYWQ8jVXYHL0sqiWFs6aSqxxlSSCVM8UHzuZracPz5mjfMnCKChiW6EBDkMuRb+gU3BShYBJ38Ren4R66FJYWeNVCy3orIYwAWqNqaJ9Lirc/8A4K+gSukyt'
        b'tV10qQcCN6hBB6g1vze9aybkBJXQnTArziJUsh2Oos4MwraEoGt7oPReM/UU1DqmfF+UrY4b3gl9dPycedSl0KtS215CXypQNTMXGLAl8AWFg6EV6KSSvCxcT/uwIxp1'
        b'qyiYO7RRIjaKhKEu1E0rCYQcOEZuoSkVWsHoUIItXZwrE2wZEMJdSiMHwXlUyXT6FdDhqTD9h1w/6hAF+kyY2rdsa9wIQYCTcZgmoEE4yKa1IHWHAl2IV1g/pSe+frTM'
        b'fegyURfhkcQ7i+OdOQpR6aANQfkzULk1jVPkvEMciQmiyJdtSTN0CS8xd1sbnywvghatEfZkbafRe9GQhasCjQLnHO+xkZ+OLjEadiRgOsuE56VKAVvR2w/n6fyuQTWz'
        b'lCQMcg0ZFRtLwoo9ZALrdi0cX4dJYk+mmOOXozw4y0GrL3TRTesLnVFyuLBoiRoLc3g4bB19vgsuE7UdfmrDwbC2zTpopCfZxFSps4PIkuP0IxJmankyc4HsfcLmPoH8'
        b'FaHdvi2GPfxuq2TfcyJKqLwvb1L4KUjcq40/x+vOP8LmkpUve5hpprniCx6PTESE9/Pipff7Z6DsI/mfdGcPt0l3L7+HT9GO5tZiSpoqRKvETMoHKYI385n3cOk3NV3j'
        b'YpJidqSkLYnRVPDqGevxryhog0b52Nt0a3wEUS+pNh62qAT/UTvGPwNUifDhXmXghSod9bfMh7bJu1HbTtRmJFmdyaG6ACPoNYHD1KMIHI2VEs093odVtnYeFLTiGeBv'
        b'u9Ydymeg3lGnEJs/1Cto8Rxe+e3aEdCAV6c5nY5hdAbTapktlCwgSgiVBmlKiBh1oObE+EkbywT5s7i34u93xQQNJr25TP/YpspKy0+vJjzVY/vmt19svLH+rPst870H'
        b'TMsqYiNnWz/SFP/I6u4NCx3Wzcxe8ohEcntyzp7cCj33Iy4h7XuWxcbFP1Yurfjqyk7H3kUrZz222GT412tOM5O0xj9vI9OY//43y1KezT917JSwZOFct+zomyHeA2aN'
        b'rm6Pf/DTUyEbdzjq56Sftr7i/pZ/2s/fXWy9PNP+uxkfZBneaUq8JLjIb38fM07+0t2Ly3a9brs0b8Mmu+Ss5XH/cgmwvj53aF9Mh3fA/kmdHzc+dd2q7TGzKTk3Zpz/'
        b'4l9/LJsQvHxXlPEPqw6/OtshNnX1hy8VBMw+aLa0a2bEtyseabR49cnrNd+vkiXO+NT/y+3jTI+b2axKeWT2M6+WbOGt7J864X2nZOGhs1a+/U3jT8240vKG/LWWO5m3'
        b'P/++6webNwcrfv+uIbZ38seiiU91NcLP0x+V3wz9o+6JxR9G6V4dH3v429WOeY7HDcM+2mf71GefnLR6aucHpZkBiYUWr7a8LrTZH85y/6IprLr05YyClBNf29yalXbC'
        b'XO/61Moh70/dbm8KHD7d5f/OlFv8rWm3QtB3L+/16Qr6ctYtnRIb/+gg9cKWV817liVdTxzMfTfC48jjvs+UTRO+7I2ev2W+5/FFA7922fmdch4+9/PrC+1O3rFbaBXk'
        b'9mFB1OxvEm8fjDm2/J2qyUPt7em+s0v8v3pp6q8ru3d8/vgEk2uHwp97sS3mdKveo9/mfRL2ftvNieOtZ3yuvz/o0kWznI5389uLeZes2RbncxOM3oDPnnFxvlL40aBL'
        b'Xsf7N4s2hP+icfebHxJqv/Rwe+WLaa3Hyr56yyHosxOVGf2/3+j9cjiob1qOxsHvbj/Zc27d+6U6FzJC/s379Ra+snWtc9kp30qv6aW2i6SLcovhGe3BpLMFe1Y4pp86'
        b'n5f62lDxx7KrG9qLN109Z7z2bnNDe0bE/MtlC94rlj/yzq3T17qf8+43Ovvj0bj237VMpgwLm3Pu/mg/4ZcF8sClMhYAc6kOyiXnOTor5tABDUKdLxOUCMPv5aDjUCkl'
        b'cDNNSyiAZsxAY25xHGoVoUZoncYwPK2o1EVqJYMevHF0bbFUO1lYq64I34latAyh19sqiWqqOdRls5WpN2ogf45S8ZqCGqnuFTXOZy+Pe8FZhWZcEw4z5XglGmI6984A'
        b'TqmVDUMDTDHr7cYMBlpQIVQrWSIoUWc80WY4oMBgQrMF7U2qNxrOsJepcTo4owXK2UH1QDAADR73qmch11EJMPVAB6heZ1Y8aiPKWTWO34KPe6KcjYEWNhiXUS5cGglo'
        b'uGbiOH7zOnSGIqHX2atJKZpHgC79YH5JkBZVaTnC4FSidkWFaJCoXnEhUx2plihLHVUyFDP0o8veI0E3BzGvTloyHnVMVcCB4fw8Fr1S2Mq05g1EPyX3JvNSDI2Y4ziI'
        b'T0stbQE1eTBgZ6DfQho21Ybj1FDJZNQhOMahq0wzjpsiUwTFnRipcDYQvJxpJSuNV4wKtimJpQBmvGaK2Ket08YrI3UucKLoZ8xD9NN32qt24dElngLw9Nj4ixfy6IIX'
        b'sCCduz0WKAOEogqiLCWga9cQVmaFR6AcSjw8oN8LqnwETj1VsPI2ZyOevQe1KgPAt1krfMgcCaMDuBmOJRCFZKoM83HHqL5XK1TALOlFxPy1hU1BtVLUlkKRnZI1JA4g'
        b'j5vbvIQa2KSrmcjpG2EmNJKoh3V4Y5Ch24e70C719LFW41J2itAQj5m0Bl+Fdzs1KCPcvaad7jovOy3C95igS+IFUVupBUAIaklUoNcUeFi8as8TRF2ZCKpQUwbNNVEM'
        b'5WMDPeJZP6PErfrABYZkK4Mm1MNAoTgLHEGHFIDP8SyEqTbKdx0JL7c+lELVjrhT+w8tNLhW5RZiHd6QxBSB+YWwg+NMw9xqrIreu9tchb5FVyF7Al26S7Hoc5aFi8xA'
        b'h2jEyGIW2HNtOpSQEJzUaESCD93Lq3koc/dXRKGU8gyn6Ak1LMIgatpOCUb6+MVyXzS0lCqYOfy8yIlORZD5HAUGmVObifqMBfMka4VhAipZrApKiCqmKaCNR1EvHQKH'
        b'tWsYsBFK0CVFSMJ8OMjoW6F83uiQhNAFl5TYRpyti5kZdcApVCcl8yhsgiEZPw0dRO1Uie+qhaoUcxmvc0/4wFR0ng7RAmiHZmXwwIU204TxmO+na286akcVxKwWrz/f'
        b'WSQ2trqXYIZK7dmaH8LynwIaiUoyWUTDGBv6borOplExt6sxBS4XbNXi6bS6YCG/HkptfDGtRoexaHEIZ5Li/QtdWYgtm9kxmK8nOQ7KAmOhiPpw7BJwL08rwjA6RPsR'
        b'OQ3zh+OWoGbeH1VBJ8OCRuO14GeDt3ApweZSky0pXBWwrHLehxH8YbG31ArK8WDx+j78vC3oEK3TVStDab+DeayLKhsevBdP0HbHQu3iEZs1fVTtByVKkzWJicz4/xoC'
        b'do/W9b/3m3hTi+BtwqmdO+Wz3yJc93++pt3PGTI4o5gCHMlvXd6CartteCuio6bQPy3egNcn14L0h0ABtf/QFglqwndaepa8MW8pGPC6vIlA9d6KSIbsX21hEtFqC0SH'
        b'bkB045gtNuH1BRLB0ERDVyC68CmiSVQHjlsimPJad8Xkf0HrD/q/iJSqTUMAGDNYpqCPn+yS3atJJv0Pt3Oleif5EruR8WDyhPimZvqO6Jj0yPgE+U318PQdWyLlMaP0'
        b'5v8goAGWUX4n6r/fVIryX/FfIlymnIgMf+G29QB39+EOHTPIDRV0r0ZX/5FUg+qgi0o23Hyo17OB7oUyETPAP4T33pAHFI2O5C6CbI6KtSI7Jy+8aQboO1SkVBFwk9Ap'
        b'MSrNSlZcTLRhBoLFn8iBy7QdforSpi8SY7aoE2qw4Er5pBP4ACwOQ81jq6vFTBF1mnB+qj3mwLIeXB+UrMzALANnHgLN1sSYq9PS3QeT1Do7D5+AFDIsNCYHCeTLcxFG'
        b'GjMXogJaq0k6nFVZcW9ARxWG3NASSAMEEiYUM35ltnFxmEkKpiXNcQpwVzTRZaYatxldpIbbcejk+FFhQaBveSir2HLUncdG1KChh4440y5FL92gGJvDwv1Dswedp1c2'
        b'e6FirvyegkIUTokxW3IB9dlT30ux+zXQSTg8IT7o+CAnP40Xs+dX02KCnk56aZnhsdqpb14YPzvxpRbb88KtTfqfdfk/NkmzWGIe7Vjy6Cot38B1z7oXBfe8Ebz5wqfm'
        b'Ffrb1xbFvLZn5TXe7FH1lNgpM2fOv/7DwjvHd3+5Y+PMkimVgd/XmzVYljT8tH9y2M/SvpkF8e0DBpXlr3/fHD39yR3J+SmmhYGcxyHXT0K2Fj7zye6Sm6HmVQ22214M'
        b'D3z29P5lWp8ZWUbuj+n0+qjD9DPxxpRlB/I//vljlxWvjXOZ17C35vYPEzZExs7bEvHp1+2itnMm61z7173/cvHqHnmoU7XDFJckozf0zn1yM16nNaE9uLgy9uo5ydct'
        b'sKE9Mc9427MXFtfOztgZ+PWKTnjlpc0erYcuhc7cFvWo/1KHzalDr1aG6d589alzp+Z/McU0sTD9YPJndrJPPj/64wvF4Zc+nPfjtV/9Ln3R/myI726ha1rXW2kNvY13'
        b'zH/61uHQtzNn74wyue40uG9KXcPRq1E55ss+2nTn616NDIdW+bYVt6/698SHvXyx7qXKmAu6Z0w0x5f1Z0s+PTkU/a5h3bTj/s3WL47b5ftF5pPP9bhF2L353bovSsen'
        b'/SwvPL9wStzaRyeVr/xRq8Tv+7yGXUdWvqYeqrV5x0qrOZte+/BxWbhsy9SPd3Qv2LdeVnEw8tufTp27Uby2rWJA/lS77unSJ/TS/XveOP/Ud/t1NrbJdVI2LPjC9jHZ'
        b'xg0bazd4hZXUXzl6pTIu0db75PjhUFmL9hvv/0vndqn6gux30NryyXNN+89NWpL1jsG5vpD8jOL4jwuGFs3c/9OSmb+Pf+nRNT6NzieurCzp+nVtw6fTjk+ImJQUGvDt'
        b'J6Hdb9ZMzbKxv3Xny0n9G6/P9nxi2/7U/cX2/dfu5tS/fDHdq3LBz5lxd9LcWp+E1riP335th/Xazm/snt+5piIddajHfj4k/sZxxfXTi7+ZtdMTfbD0oq1u8uZ/yxyo'
        b'FRtqmBZPjNj81oylYPdZOKaYUGYjcztqxkf96fjRFpXaU5kwVm2BN4S1gUKAZNLjJQsmjNVOQs3Mji9Eb5Ql3/o59FOfJBiyRtno6CgLaDi/kBl7HhznT2w9UTEMPsh1'
        b'3BRHJuL0ozprObRHUm57NK/tifkVyrvVoWyo9/KzRfVzmR9rzAX2sVDTV2NQOeHutaGNGStKtJgBdQMUQi1mVuYvoewK6baCYZkKR8ToYiYqpvybd+haKRY7qJMwp7W4'
        b'd9LxAuRuRHm0fzsgW98CXSYW5KkyzHxn8dCYAA2Mt8tBXdAil/FQg7pIUzg0GIpOKrxToOOT5Mydmm/WuED8rVaWgM4R0sU8U+8NlcNZdHKUmSMep+O0UxqoAw1idncq'
        b'dKtxQii/KBqqKFsWnoXOyn15fdSk4KvlepR7nolalMayxB522UKFRSw6tYVWNh61B8nxuVJlRakl1YDkzFhJObbta6B8lF+51HEq+QHVKF1OndNxgsP7R0W4xgLI9nQ6'
        b'exHzPYkR4zQoH2vHKDaAo87MhP4Elg0Ig5yFaTfmkRmDHIrymXWlA9T4oOMqqQCLBMuxoE0+3DEPdcr3w0ni859YmIpQG48OofIMujB3obNQIddBNeQIIeK4CGGpoD4W'
        b'NTAb2KZ4VCi180kjryejXNSWjmseZyjahlrmsvuJ3tm457hFi7cxG2INHSEauvawz4thIFHl0y7dSOnV7gy0Y/abWPGtX4GFsFJ7O3QEukdhIR6EhEA5cIANxaH0eCbI'
        b'QrGWpVKMDYA+2qN961EH5KPTI5IsFWODoE4BU/BFZVJoWUAFViauyuGYwjvfMTe8R2qUPgmpQ0LU58Y22PCOLaNwJDNnjbDkK1azVb4MywalriZebBP78XAANcIhdlFw'
        b'FHWJrfGD4tEWsNCoiFgPhagSCq3tPCB7yxgchnjzTDjNvKkUQ22sHPNT50dM/6nUwXMmMWLzZcwkea7fMmK966XPTnQNZ2ELqsbCGy2hzAILiPit3q57mJnpJmJod0pj'
        b'TamT4D1OFyme9Evoqg+RdL0FdBhPfwMlSWnjIVe8D5dEGBhUbD+K0XAIUxuPGsenY3GWWz7XkdBWvMKG7qeuIwbCoQp7a3R+tv8ovjEWsxgkYliYaA5qcqF3Uq7z0JDX'
        b'mDob7BQ6HSiSoIvQzKKPQbYTAWMc8sNiH15QqAAGaFEikRlU2TCCPIhnZBjaNhO3MirIDCZ2FTKD/0NJ6n/Ltcxo1zGzlKYvL/81mSpRm8ZpJxIP/h9LK8b8FCy7TCIR'
        b'24nUg2UfE+o2hsg7BpjxJ9IQkbgMf9NQn5aGJSOcNhRNwuIVialO8mHR4K6A5S4By0TEl4cGr4ulNfJMTfFMS6SGZSzhLnmqJtIQNES6Im1q06wmENmN2BTj+iTMOb4B'
        b'L8ZPSXu0cN77rXKpLKWQm5gx8O//m1bGCrnJfswQv/03rFTO/B0TY9oZYgVm8sAY60bhBIYflc6ExXCCuSeBbWmYdRp1ncZaP4x/3VRXmNve1B5t/XpTOtoOdS7JvZR8'
        b't538WkZ+7SX1aKrM/26qK2zybmqPNpW7qTPWRI1YRFH7HTo8bDaM/v9uJkYskN7F1S8gs7OPo25qdMWCDW+xReFYRvT/9K9YW6QtovKVHvRpKUViLIheHkFbT4Sz4ph9'
        b'Vg839VrFccy1CqcKP6yuMvsS/rk1HmFvbLl7zb7cfDN88d9ZcA0ddXSYN3f+HCdHzEd2p6enZaZmyPEB0I2ZvR7ow4fNJejV09DW0tXUkWLuoQgdNMZnWyUcCfKHCqhd'
        b'K+GgCwal0s2BNBYA5Egh2xGfq/jvOdwcM7hK7SjQGUtXxx0zcQPmcnOhfgaF68fAgcmO6KSDQGxRHDehaloCKrYxcsQnTrkax83j5mFKTzOjAlmQI7o2B4+gE+eEKhcx'
        b'e6HT8UsdcUN78XqYz82HU6g7g3hyN1y2xTFejkd4AbcgFnppCTMw93HBEU7J8aA7c84xMfQpZsUSUG84wcwv5BbqwEXWiEsaE1EvaojCLXbhXBzhMs08cZ5c7oSu4Ycr'
        b'uBXEySWtzM3VSh7sjnuxklsJjTtYAVfxEjgmz4BO3I1V3CrDXTTrbutYeXI0iarBrUYHrGhWL7gKZ+SoXYr7sIZbswLqFKp/OEwuVlEe7oYb5wZNqIDZpPSi3AD5bH/c'
        b'DXfO3cWY5p6GyvEHvXAEGnDKg8P8hJSN0FnU64lftBJAGufJeW5l7hxQf2I4fpwP+bjhXrgR7TvZBFajovnQuzcZt9ub83ZHR9nj+h3EpeJUR9x2H85nL54sWkoBOmcM'
        b'vWvRRdx4X843GhpZ95uhFA3i/Ctw4/04v4AQmh2zZzUkZsDcTNx4fw6f+qks+zm4sEIaRsh4ABeArsEx2tNNTuulULgOtzuQC4Q2M1qGDrqEx4q4sRWIUW0QXIykczML'
        b'r9bLUgGacMODueANqbSI9M2rpVASi1sdwoWgC+6sujxcRq4UXduKW72WW7t+HOvMEcySHpX6olO40aFcKLriSUtehar2SyEXncWNXsetWxpLc7vi+T+NSqF9E06s59bP'
        b'UgxJemgkfnoFdeNmh3FheBLz2Xz2o8OYHSn1Q3W44Ru4DYHQz140ocoYqJqC+nBr7Dg7PETlbMzL0VE4BVVbtXB77Dn7DRas9e1aUBMk3cERsyQzvBpO03oXwGE4AFVw'
        b'bDYu3pqzRt1TaOvjJIFBs+E8HoFZeIzq0HH6FI83cYlsw+M+OXAOWX6sKQfgvBpU7YUL1DLDBl2AFjZxOahGLQiK0FncRgvOAmpnymzotRx0ma5ZYUMtEEqtCaCSRLkS'
        b'cePhmAiGwqCQWi6hy3hBNKFGD/oW/xKhnDSc5zzOM2k+yzKA6qA1GE+ioiBFFlLMDAt2P9gVCq34Y2uHZPKe5wxn4ZdoIJJZR/XLp2pi6VnVEpEB/rwU58AP85nXjGuQ'
        b'p+GGulkrSBaBMxxPysjPYhnORdqimkBWguI9T963w7UMBljEm7WW1aGJTliro2bcSDRI8rSia9SeJ9wbdeIatk3HhajPUBRwMZhaR8KlzADUYa1sIm6euWIYHFAO7aSt'
        b'HwyRAYIrTngATAXFEGzQYtZjp0VYCMFfoxw1kmuGoovoUAK9XdTHNK6SDNGSZDKCza6K/lVupgcUpo8DeDQu4pVeqhwo9S3KDtTDBVpJCioyQCfj6CjRHAasE5CfSUvR'
        b'DbDYxbyLkJrsWTaRoh+oBZMpMlS8PTRYmNJXmHL0QA+6TIaqldaEO0uH8woUW6M6P7YiWCZXRUFbURudk+RgOLYTjzurjozpFsWYbB9HjVdQ3UK4bLh+pEf2yiVIR6Yd'
        b'HaZDY+m5DH+PhmQilAs9acrXZ1E/bcp2aIc2uMJGV9ke5dwGJDPbs8u8JEJuTRc5fe/KBkYDWukS3I3ad03AQqiyJeropLLL86CUTWCrBaqi/bBdQHKYKYetdy+d/v3h'
        b'xvTTIMhXX6GafahaTxtpRqgJHVInTMGyyYCRCo6wRV5Pl1gQ9Owi7XMkobBIDldFISgPH4T0ZrsmK9oFD4JyRBV7QblbDvNsbs7vd9qYquoLm2mRYkCC9jLbr25TNWt7'
        b'Tagn45GbpljruePpxKWKMEXCRaMyGXmdrdzwmOlopRslCg5swIU286RgEWe4AL/0xaSfDOUqQ1N0gpwijJ6gk3T10H5swQSPbvij0DLTAOoVG4lkcVWQBCynM3vHgZlb'
        b'13MqwqTa7oNWbCByJ+IdcRwPkmrGWTV0HNrRZdpJp6noKCmAxGkRCaY8K8OCpzVYiF3DM5SbGX+3hY3BLuhhg3jQ3IO4XFGtXchRrm9MqrvphGmifBKJDWdYDiUiyKbd'
        b'oANZAAdZTwehKYXcZJRaKwnsFlUp8xhh6YTaONfEkRlVX6EYLiOooivPGbeCXPaU2kEHeb9S0U85ypfxNMfmJXDRi0RS7ImAYhJ+TQOdF1A2Oo8a71Bm8nDaMpkWtamL'
        b'tGVOn1JsdidsXruEGdr5CSR0EGd52D7ee0OAD3t4R1eTwwexQ/fMVG1PcSx7ODdzPEduGTm1tD3WsWL2sN6CWbGbSvbaZNosZA9XWOpyeDGZpEzfrX3bLUzxuZU6sazX'
        b'998Y5z1ugjN7WM6N4/CB5NztvjdBbmag8DSUpcXhg00jRbRH+3zyAvZQusOQs8QV6ccn7zFTi2MPQzax2lNkCTbjLJYrTAfXsm42xcV5L1jixlET6eqACfhs5PRNPXbt'
        b'mTjVDEuNwWvoi+w1rIgmy0Tv8xs3s9xemqytprJ0m8TNW7g7DfXkv+tLaQVOmezt4alZ2msWbuXuONL/vltKT/pVocRbB+ShaswAJHPJ24wZn3IRtcBJa8yh1+LTewe3'
        b'QxTKLJbJJNptgo7FPg9Yb5uSWATI6az1nGmia7ZvCOvnuTgjNiKr4/Z8YW16v4mkyuUY2RBxCiNJFmxJFWQpT4ETuSmJT4qO2ZFGDNofFGVJDwvqzDpyMVm4uWhwrvWS'
        b'db7EQJjaHfp4+2E+7E/CVaHz0CBdjk4pHJDVrlrPdeMVZmqx3cU1dBeeD1/feNi9QJCH4Irj/G/4BD6dNH65/uf1l678+MvEuCufue3IjzMVp5hqHj7A312eVJRiJZEt'
        b'H5eZ9t7z8pumFuoz93OFPxx57sl6+/ceyX5umeXJuFwb3VPH2ro+/dTO9mXN5bBSd6fhe6eKDITqgOVGTi+/8MiUhjq3ImPzR7eeyrXbte4RycZHZ2183MjmfauuWy5J'
        b'71kkRWr2p6o/PVB65PzTBQnv7Fr7RcBJvaVhR6w+83mlOO7K4lSjt+CKvcvuO+9sPXWwb3PDicpvEsqdvvzJMsCiUH1lw8fHiq9vCH9+31Hn5wYP38wLcU3vf/Rpk698'
        b'bk2dGL7OKmDlzU8azH+Nz15s161VXDonY2u7Ydm+9wNaXneYFSA2Deq7att9wvK1pUHX5hv9OPiiWdCHL64qW/C2dO9r8LJu2kYnp660ne9WTRqYPyyJ5/feMT/47fJc'
        b'UceHq3P/cNl50WO8U5j+wWUnLqa3yxf/0Drz86GIz+7UPXvdJqM+Zka65ryBGzquNTqTPqzfdlLXzy3ObfUTvz6x78VT0+oHE6pMFz4XEdCn8Zaxa7/9Ox+8u8MlYPof'
        b'ES81vzHvWveRGuc6q5eq3xAteFq7/okGzcHr3w2HfRu4SHIrz040fssrF7tjzJNaYlw/eDX4qHF/t5Xdrt8yT7pZr5t7wfS5/Ldrzgddcq759MCbcyMdAyZmmf7+pl3G'
        b'9Y8/ubrkfJTp57pBYakhXw50Xpg1bc4T655a1/r+N7kzyvMnFpt/Ny7BJi4l+DfvYS37r78deHL1toqZwx+5aF8/kxM6rt7OLf4Vg6y3p1fsvLFurbzu7KbOWcV3n5s/'
        b'eCOp94U3Pv7148kFbwa7/CH9MvLFk0nvyHTpXWIAnAmnHqpzYRCvWgkn2cNjxqhDEf3BTYwwN0vdO4Qt5MTuPOoNQp3sorILs/bZWJBu9qIRAL2I/20pHBURnEwNc1PS'
        b'7oDP9F4SxlUuwfJEASfS4uc4oBJ63StKQA3EiXyHp2Q75HLiaB7z2Nlz2ZXzecyDdPsbE9c/HjYeYk6aSQKL5iDm1AXVoTZ3LxvLdFQxKogOKptOG21taIPLtbcid9iH'
        b'OHEGj/fhUR/mWH0AXZ1kbQdlm1EriX7Sy6/1WkSL3OwD51U2bVnoGEeN2jSgkLZVLRFVzDZS4HcknLaagPmsk1JanRGcMPGiVvh8cgwnnkACnJzhWQTUc6hvIe7DQgum'
        b'tEKdKJu5ir8GLVO80HGc9V6nSM3oimzy/6+RzMNvE9X/5oXuTS15VGRSeHxiZFwMvde9SsjvX7GV2c/5iBU+Gx78I/5GbRzz5KBFbV60ROYKx9nMzbYhfqpG724NqT8J'
        b'Q8VNsT5vQC65RIb4L1PqVFyLOvbW4MWCmPqGoC668Y8FDXKqRVPEKbg5/mIun6YlKG8IRTdF8Ylxo65q/+LwSAXl4UHKGtZUhAX9C5ex5OcJk4ebsVC/PEMiNIhKNlqP'
        b'OX8knPFmscZyOH2fs1ct5UHoyamcvapRr8gMpyXEaqmcvIr/kpNXhi6459qOQAw0uPvdfD78ApH4JMftEGKF/y20qHBf/RJfeuAaTlZ4/FxTm/DHuhiOwt5moSsZhLsM'
        b'tWRwwwBLd48gd7KzPSTcgt1QkaBmKYbhePEPeyVyooE3D3v7swj3yGdiLSs/jtj4SPfh7IrmvDn5bfUXii/kmtUVZ2c7irjkV9TeemNAJjCDyYtwwtJL6ZNGbW2KqzDB'
        b'cQJVEGEutcVxjGOkFVhQH9GVm6F2JXrjARfJN6VRW2OitodTvoXuPIe/vvP2c5bM5f6u6eHE/XE4caYwYu41qmTlPuDjR+0CYcxi11Etdm38l5GW4mb4Ly72A9wXug9f'
        b'7mTXwIAjFoiJszL3peg0OqjAedxnqEWgRT5QroZK0Bl0ei2R1E2kcGwbFpYJRbdG+RIvG1RNQ/EcFHNqkwStVLhEmdad05ytodJX4HwkwjieC0GVdNEY7SJBZS11NLmI'
        b'hKkLdEiwT2rEiToneXn7+tqiarhsp8Zp+AlydFlKP7EwlWLm/Wsvdf0IGw9tT05OLq4Sfs4I0kkp+zxVRGLccDNSKJc9ZTWBzNbN0lkW4T1PSOASyAAfnyPB8ojzOlyW'
        b'9hvrCoOe5eSkgdvVe4JCMssyfsgScSIJPyvvJ1qbwQzCvX+8SboswubR/TM5OWFdP/F7+wOBCxzmpJx0bzbN125HWPb3duiaRminOm9l+X6zcvtAwm3W43Q5Xduf5ITN'
        b'7ev79YMP8SR+GmHBmThMkpMjLXvuK0EhOpk6KcE+0fhctOWr374uJ0u7zD6SOuJrs/T81ccHS9kXRLdv5dKjgUKzn9vT+5LedZvrN0/h3aTOC3Pfv0brff/0Uy9x3JZv'
        b'ORkna3+VPircLXpJzGW0c1ac1S+76aPhD+SlPOe7gdvEbco0o617Myy/9AX876Kl73P5nXX02cyvzpe+gBfiew0fcAWpi5iRXL1TFpR6UPAQKsKbDI8zKhU8t8+O9/n+'
        b'G15+EROk+h8nrQ70SXplmXZf3Nzr3u98ppd/9XSRo2nEv9rdPu4qLbkSEmAeMs/WQHooz9D/jplZz3vcdYmzxysvpRy4WTW72b34hzfevfNc+VfPLt44acXcd/eKc4qu'
        b'j9vzrz/2tlu4Jz3e6ZW0omehVeXk70vbWrY4nPp34kmPW1WRjm9MfNJjo/+/n04yK54UsvQZzcNfJbzr6G+iLznxlvYL7xy5/Xrg2yhiy79KQi++v2W+aE3tgamdG3ae'
        b'W2EzePrKje/1Jr6bnPVGx74m56kfNcTpPOp5ZCDwzMdvVH0W8ei+3vTDDafUMjfNnLwyrXJvf0rV9ojPusIv+B0/x69+Nu74ncq9H9n88O6jbk1vLX31+mdrnbuTm/MH'
        b'Kn95pCZU5xmX8x+EVS9vdP+9rf0Vx6YEN5ffQxpzP/U+t37Pvj/ks3ZYub10reXOtwuMn7M3fm7n8eeNGkJC0zu6th7b+6lNSaKze8yTuhm5zy9ef6zhRslX+08NXh9w'
        b'QEULDt391S268dWXX7zQXftz3vzhHYc236h7+/NzP0lTw590XJf32al+h4Y3exfkfPYdnx6b+rPTG29fcr5l/1OQj/rTPnM+PeLxit8bepsb5LcaV/78szgoqyl9jbpM'
        b'n5nKmKJ6L9ncvVBma6nGqcUJVkZZzKD8GBzRJk4nodwPrqzxIBDDw0IyFj0rFbFyoN+S2Ib4aM3D4qR4Do86tkI+c+sFtXCFMnUeUIaJdisBkmmgZmGfqSGj1legArXL'
        b'0zMzdbD4166LyvX0oEc7FR+7cFyEjvnAAVZJzVQLyuTKINtTwphcKJjJjJraUO0yKPVBHRwX7ymgPN4N6oMoNxqMLrpbe6IaVMcYS04tUDDE7C9reTI66EQbhwon43eU'
        b'5QxEh2iv90AL6sGMKqkTXUrFdWpKBVQFhdDHYBaX4BqqIcA4ApUr54jjzxlQtkJh5pM5F3PHB2yUaJIOwXELqqZNmgKNHCm3yMPb1x2qJZwUXRDgmHUM/XKFKxR5eWB6'
        b'6xcKw2SoNwkx6MxEWuXeGVRGQPWoWXHu4VMPuhbRD83RSX+CrrVCQ37eMjyBiwRDHXTpv9SC/xOL4zFs7Mg5SA/Tmr9zmM7WldDYNpRR1eWNeX2F6zF9yoKKFS7JSIQZ'
        b'wrBqU+dk2tSQgOQkrsyIIbg+ZXbFAjH4FjODb/qdJXVlxqLHaPBpuir2VHJTnBKZvvWmODoyPfKmZlxMenh6fHpCzN9lWEVp+qTMceSXnuo0J/UY/u3T/Mtp/4F5rU0X'
        b'oUoCPSMHuuo0V+eMfcSGu9yihFHcHGmcilkk7tKorpmPFalcCgj/3NWFsoJ7nYvgQ55Ku9Uz3Lz8YqCT2O+QC8ZivMgNUL8IcvCmiXfd+RInJ9vv8P7BzyI+jvg0wjvy'
        b'8xit2GM73vNW5yZXiIKOHh7liET0UIOAmzpk2sYuPqu/s/i2phmoFoSYTR+dyAeza8K9s0w+Dvnbs9yp//BZJtRyPlwWE+NNvPtt8Vx3jZ7oWSslwZGo+f9sph/o3Ud0'
        b'30yLfONnL78hpkEI/ojOY5OYkGIauyXaPZJ4+VHnpt8UeZSu/IvTKP/vpnF72vh7p1H/z6ZRf+w0ko/X/e1pbP8P0wiD4enWvmwa5+ATavQswglJBAzbPnwaiflRIZlI'
        b'vlAcK/4HE3mfhEkm8f5AElrMOw10xG3xshlh7lF5ohaq2EL53+ue04Q94jpL9ZRb+3+e0JlKH35uLjB9wPZE7V3G09it8sZ0njzdcVi6belzOl7Ml8gM6DcPQp24jmE4'
        b'zUEeh447oU6a/4Xp7DL8+f37vPM32rP80LbZM8gWaqzdPUScjofaeoFHhXx8h3GkIM/E70+77Zv6zLCOMEc/71b9N4tXidzTly3UCERGszepmX+/xrcmb1KC1WNZn/y0'
        b'3SL4ha8DHILjE2zSLx+JtOpJz4nKdvwg440My6Gnbz3Vcf3xjhnbLT6NCPrM6/2dX7rM19997NRrz87ofMlF3Tj2jx2PZe2+rVP4xPR3o6f+rhUu02A2sMOLUaO1rSVR'
        b'lqihBgG67G2hAF1g13B1S1cqOChM7hAWWykLBRVrGKywD5PuWqpvISGQeVyYowYcxJxMYBwt3CEYyhXoUx6fT/SWDnpQLzNjbCKKaHTOkwJ1i3niY1x7jfkG6GV3fAWo'
        b'GnVAv2jsrRufRnmnVdAAJdbu9NpMvGDSKh51CUjxIQG1DYzgU8ULE2fz6IL/uPv2K95ZDzoER3axNiHGKdGx4eRcFZSr+C9v4iRiS6hL7pcoG8C8j6YZjtrYZD3fFN8D'
        b'l7qvmUKaEfkmStkuWsSGv729Ww0evr2pLrEXNa9hZNp9J+rzwGcyG+DpkCeGlm3G95FRTcW/8kn3hCyrFlVrV6vHCtFCGU+vloQRJ0CxGtGiaHGeRi4fJo6RREui1fK4'
        b'aPVojTIhTA2nNWlai6bVcVpK09o0rYHTOjStS9OaOK1H0/o0rYXT42jagKalOD2epg1pWhunjWjamKZ1cHoCTZvQtC5OT6TpSTSth9OTaXoKTeuTsGq4V1Ojp+VphI2L'
        b'kcRy8VzMuFzuNF/Oh43Db8lVmiYmb9OjTXEOg2gz6r7I/Ka6T2QSsUz8xXZMcBwSYcs0kb1i4cPGBs/BTCkh6vdRVU0l2SNuI6mnJWpwR4eYHJSaKvoq/kv0VUTpq/iX'
        b'3P8Yo2lMi0diND0sIhLZOCwoE/mLxF6KZEX4r1pjGhuf8IDwTmNWGVnu998iTvPNsMR/r9weQkmAvzvKhkYo9rNdqwB5oU4osrHjOTdefUHAsgzisw3lmPtLU1KD8At0'
        b'Xl2ZMViDXGWQoMmKULlRphraUL+NnSF5qAEdglItQREol0fnEtFZdqtwbS3BtJR7o4uRo2LguqN8ZiRRBk3h1p4+drZW+6DUk1pQjp8tgqNrAumZsG0NDHjN9VwKuXgX'
        b'wnniJKgHOplutHRLPKa43k5xigjPx4OpEt/TD7q87Dx9XKCZ+taXJgtQvxauUeX5CrgAJygVhmLiK4X43kdnfOGEaMX4BcwwqB9ds/FCne64TeRzPXw0Hp4hWoeKIZs1'
        b'uQHOy+jdJCqS2hPn2hqoX9iNRdBeZomQC0NiIuNd8yRRIQR6i0J06xNoj7Q8xMRp0xyzkaDl0G5Fx9E2FVVDaaCDKsY4TwzYdai9FnR7Qz1xipWhyeJz74RyZphRtwlO'
        b'4R5VUl9sNHo8FnOn+tK27kWNWN6kEIBEqBvlvqpxCr1M+2QRFkGn7BJxyyK0txjjc5i6bUCdqIm4wsLnwkkzzmzFDKYhd8B53W3VSd4BLw9yrUclkyZ0eg7xVYUOLrOT'
        b'WY3xVQUlRvTTj+PwqtjYgRdphE27szlH7V9CYAhOe6HTeEKV4d95NKSDDjCvRSc3GowOOq+3OJm4znKyYOY5pXiUc4g3h3YYHIloj2ogh4JDsex+POJ+/1boilwZjBjO'
        b'M9MVNIQuzyfLhQoreLZ0J6FuaBJtgoLwePVMjqfRWpNRzN7K4UBw0F+d9aHPbeev+iXXKvSaTreeSj0VaTLB0LfAMynllKHDv8XDtxatT3w0Ss29dygrLjT0iSi/zbtf'
        b'Obvtwwwd4/Jf4u/snnXx44xCN9swyZV3pxqU6lxt8ruc1K2m/uubovVGu3QTtjzSuvq5n9ZXZau9cSHp0hcZy1tP/npS/eSlj5850fqibkycye+mJTd/Cfh+/fdRqSvf'
        b'OPb64YVHbpyFSVOPd+/qjyp87pFP38lduWhOs6+Oq+WSuPc/+g2tynyhXOf1/OzM2NrMV9rCdh58+wfrV6/vvDnrsbfaHJ7Y9q9tM7ZNnP1c0oc/30gL6/i39Wb3j4aO'
        b'NHg5/Vazb4fX64kL3hqc+7zZ3KNv9Rk9tdHyfH3llGPBPzxe/Wh1+9Atm0qbkvUz13+/ur73j9LKff4vrvb8ZXW921P7qwaTznwUuFT2XffT1d/7rI9NC3/87pYwE2mW'
        b'w47fOFF2HWd4XDaJQbs2onJr6ERnlQwKQdqhehZyAs6hci9vK7vZmeytNEEAslguKMAdW6CZgPr9Vio0DyS479450MW0rsSs4KgynAnKn66KaCLWCN9IoTKW8+AA0SME'
        b'z3oQ5A46rBiXlIMO7ybaIltUiA4S8kZuwKfBRXqLZAbl0fj4x1RoLmpl5E0qF6BhJ7Qx0F0rajLHrMJk4suCaDYXo2am2DwRJqdRSzDhgw44xyifMRwXu2SiK0rQ3OBc'
        b'GvS4zG+up8CJEvi1hqiHvgtVhxJUGhjlh2sm4ctO8OgwatzHfP/DxfgxoUWgc6vIeSM6RhE4rlGrqe6LEsBFnowEGiwQoWbUJqF9Cg4zIKarhADaQCGlgQa7Rah/MWY4'
        b'qTN+qSJ2BSaA3XCKUkBpAO40LvcgbYHZXnSCRGnw8WKBcQROOkuAJhdDxklnwzkX4s4hRDQSbccCGhgasBOuOam8wlJ6pednqilK3wBVbD6uroqh7+VQw7zuaQgToREV'
        b'UQcVmBRqkPmgdKMHU2pKOwzgDDG2amZB2VOWYxJPw/IcTqWkQ4oXDvSj9n3MaU79FjhAQsZ7yCiF1pWhYytFa1APaqSIJziEGlEtE+8e5EBvGRxSz1AfN0sR436nkQkZ'
        b'b9W5qesfESdyQdfQeboO3PFoVLHZwiXVuDAaZOAsQpdRjTYd73GowoewmITPRG06bDMY/A9z7wFX5Xk9jt97uew9VBBUnMhWcIGC4GAPZYi42FOWDEEQBRHZyN5bNrI3'
        b'iLTnNE1HmubbtGlGm6RJm6ZJOtKRpiPf/M7zvhcERZPYX/+/f/hE8d73fcZ5zj7nOUdFCrpx8IKh9NP9U/LPe9liuXfBDFMtvq4Wf1OgoMBVb+DvHskJeeceuwPENbLm'
        b'flhpV3YjSEEkIi1fRijzhYysFncfSIHrarD8Of/zTxk5NS5e/U3fURCmq0lUyccbF0huE6mudhPIfW3/p4h/1XwVuBK+sZVRoff0+0NPLP3r1yxf96xi8D9aysd6NMNy'
        b'Y4JtXEMAicL6qED+83ciMBS+KRuQFBUR94zeAK8sLYiffqk3AHsrKDkl8TkqgEfwM4sDgi2Cnzrtq8vT7naICYrQjwrXj0rm+48eszi2DIXnKj+eeEnwjBN4bXlmPa62'
        b'd2JYaFRyfOJzdWDgysl/8KzzfmN5ts2S2fiWC/9RcXX5gNj40KjwqGcc6y+W5zXg6vAHJSXr8y+F/CcLiFxaQFhaWEjKs3pOvLO8gB3LC+Bf+o+3L8tfjXv63O8tz220'
        b'hFzJK0iLsIwf4D9YQWhYMCHNU1fwm+UVbOGoinv6+ZsHLIN9CVufOvGHyxNvXYXd/2nfAvll59JTp/54eeqdK61oBvklE3r19Ctm54Td4+k1wuX0GkG+IEeQKUzXuC7g'
        b'nANCziEguCH0XvH705yvbOgnvehyz0jvec5S8FIc8xP/8+yavYg5TEyNDOMaNidHss7Yj/AxMYxvNME1TI6LT37S1/CEv2Hp0J4IDoBXnZAr/X/0f698HPg9Vvg/5s08'
        b'spG7ha/+/oKhkNd+b2PBLqbODGIBpwKvUH+NvZ5ShP760h1ohgLfQCu5KZBN37Ik7pa3+ihtJzwiLNnj6dXr2bR/ZNKdCb+vLd2zBJVPr2KfwkI1emFYhuMSvRCrjSVw'
        b'6FDkiys9lqRDNoRQAAsyirCA9f7/tSDQExXEl1D4iXO+dNuZDwJtlfuYBYGiwz8JLI5wCopp5ls9bJuS6trTR+fNnlG5ZLlk7CyfNOQfFlvT3qq+KkaUeOO5D17x2Qef'
        b'FJbMT5MlfCxfLFu4cvLPnuP4i58RI2IcBmp97J48/sPOa54+WRvs9I0UsUB/qRgzduzFQoYXUArVQoFYVQg9UA9NfA3q/hQcYq/thlb6zlII46FQGHX19stSSRb0/WH3'
        b'P16OcApxC3ILik5q/lVvWGREZIRbiEuQR5Dwz9qXtaO1vc/+do+0ZUK3lGCkSe418zNP5NStnV+XGCZBGG6ab3RYUkqyKqJ09ScOjB885/EjWj3lH57jiKqenkG3xjKe'
        b'zrC5iB1fxV+wHLH7JmybeZTdn+C5x1k6YRKvPhCTXu1QTtJPSo6KidG/GhQTFfoVvmGhYC0RJOPh48A550JtMgRyQlZd2+Dq65ZipaixrFyppAD6Zv+PBz4OfDl49wcu'
        b'QUrhH9JvJhpSFW4nvQzdAm2TRteXhRr+5Naf/RXc7PqjdazrorWttRvrC49Ea68fMQsVjOsX7jEJPP+9U6j/7bIXWqDpR15asj+Rsqgdlxa8Kta++O8fGspxFr3uLih1'
        b'PGbs9CiOogJTUo6OkhK34wpc+rvbsvMYHuK0KCPJm/cXTNBPjSRTlHfFHsExUQa0wRxnzsdrHJHQFoxg+SP/shFW8Ln383j7hNmplQ5f5uztNeXz4DvMNF2dnWFkuaEE'
        b'DJ3i84NmoAppYQWeaj7OcF8skIkRbcPsa5x7Rgx5W1ydIRtuwX0TGYFYTwhjh7FbItO+MpwmF5UUwB0sR0gnvikhafLlEbn/WQI4V+hDvMKqXBp+hdR7ypoeiUEzevRf'
        b'z0FkeU8Ppq2xIEPNtepjrCiEwcX2QhmQpJiBx84o8UtWF0NuySh5U27JOnhThle035ThNeA35ZYU0jfllvXJsKXN8QzuP+8luYIxradfLzOYsQXLicRSSkK98/+t0hQq'
        b'imoizjeufxDu4PhGHFr2OSlAqQjmbaD9CdGuIfk76c7jgUmZKu0qQaiohIXqZPOU8zTyNMOlv35Akn+LdBDFUKXbciwgyYUA5SQhQDk2fqhyiZDLqlekscWhKqGq3Njy'
        b'y99JkxKsFqrOfarArUg7VKNEFLqDe0eDe0srdN1tefpekb4XsCeqZOlHO3R9iUzoTq7MhrSkp4pynkqeWp56nmaedrhSqE7oRu49JX5c+pGrkqf16pZIhe7iArHSXJSQ'
        b'9QlSyVNls+Vp5a3LW5+3gd5XC9UL3cS9ryx5n3u7SjZ0M71vwM3J3lTl3lpPb8hzoU72hgq3v61sf7QDUei20O3cDlVDNTkNbPebKhK6oL+CIsISf7WPDmcVi7fXX/0E'
        b'kwv0d5J+EImElYKCxSKDkvWDEplL50pKFOH/qoHCSeHnng+lr0KSmakYlayfnBgUlxQUwmzlpMdCls7JJHjiEyVTLc8SlLRsZZHEitMP0o+IuhoWJxk2PvHaY8OYmemn'
        b'BiWybmvW1k/GRJkB99gGlwXesZM+9mb6J+LjDJL1U5LCuB0kJMaHpnDL3bo6Kixx1UUS/J643rG6HstyLRZ29Mv1WKTypb7WxQ6J7fWrc48fFAeyxyLDSzI8dmlrzxUc'
        b'XoYss+roeFcex5rmG8MB7uhCzfSdOX9XaDytiMw9/bC0qKRk9kkqg3CwxFEUtoZeIVmQxJ7n1/SElZ8axRZJ34Sn0HBBoaGELk9ZU1wo/a8flJAQHxVHE670h32FUsOO'
        b'88mAt7IHf9M02+Dginqpfk7L8T2swBK30zLYxUq2ejm5eSyVR4NFzFPELm8c56LgmVsVHg0ADVorx6DXJLGBq5gnn3kdsvhAbA1kBVjJYiWp3U5igbSBkJVPB747yjaY'
        b'hFpjWXyIFdw9XqjcxIcfs7AXb3ubpuEUduMYdlkIpMwEqkdEO6TtU1ilGj1rnFjR2uv0btJs8rhgPt/T66ChNJRjI5TwBWMmYVzHWKSnyNqcJO0K5xS8SHv+Eo+eXGBM'
        b'z8YtAm6Dx2EQGh/FPb0w3431DCsxwVJ3vq4c9F84HS+LWVC9VKamGLOkk65g+2lpFgYRQGGwUlTH/DvipLfp21mXd9zL3KOl9irltv67MvQnH0yrnfuwo2hz24JzW1GF'
        b'74E7WVKaGqm/eyP5wEf9Nreaj//GdpO+lX3Y8K2yV94v8BzT2Rz0z5Ol6f/cdcfvV/5V/T9Ia1Z6y+3o1Gc1g6/6p/RGn2r6VsxPRpLFr6m//NeP/t51zynq1/f/NHLs'
        b'U9tfBe5Idz906R3193R7v+sw9rfq10/UK0e8Yf7Juh8o/37OK+9Y5uBPrzjMVT74ccI9g+SPan7xcu712Z21ih1vfvyqb697ZvVvvn1VY2vKD7perjv7j39s2bQ5LL28'
        b'Jq7pNwe/cy3hc7vxf8l+GXhiRsrKUIvXB5ugF7ojccCVC7yxtINLBpyJ65t5Q9EVmnCGjziuCDd6YDavyeZjm5XrEuqQATzKBf8h7zg39MmAnZI8rUy4w0VCCRn4F5tx'
        b'VppFQvmvSeG9z8VC9/BVIz30uQIPkiyunabchUxmC/IKcr0MDrvyeR6GUAxzMgJ5LRG0Yy5U8iX5FmDGAIvcjzhhsQfDBiMZUsAnpE5jEVRzExwMIU12EGeNzbGQqRMy'
        b'0CsygQKY5hRhWS9WicXEg4vCmh+VxGEjAvgYJuGjH+nfBCt8CFXirUJo9sI8/o7XbIwB3Il91JLhvsjSS5+rUw91cWnGZtB5mqv5zmxhomJTGcEGmBI7QX04N7bxBkXs'
        b'VV42GmQ0RcrwAFv5Qvcd2pdZ7UJXuOsZxBX6YBFidaiVgrvQgYN81l7pVS16SINQf5kNqHhLuXvocmUrfQ+zO73cnV3S8vlbUlBq7mrKVawkaI9JSwkcYVSWhhyRFDpN'
        b'9JBe6sbhlCxpUNaO9zlAy6dAnbEZwf2O82PlH7HdJpmvQ415McwttoCztCJYmlVGsF4ghYsZEU+mvH2dRPW1Ins+jId+E6PCiiXTy3Ap+Spcer2ScA/7nQwMC87E4KNv'
        b'6RtWC+6ndA1fFssrInDPiGRK8c+uEXfTVZQkd30DkyRL8NunXxV96ga+iatc+tm+6iOKEl/1E5MtR+Msl6X9k+J9hSh/zvAcFylMelbk6OjSEhMNWV7dSsm7ylnO+Ru5'
        b'xMVlf+M3cZc/kXT+/6m7PJKs3gzhY9tbgtsTHs8z3/2Cb2o7dfmExLP9Uoc6aSGFwulKa0MhX391BLv82SUNjnwhe8cqCr6KrV/h3E7MZB1Wdz2GFkkhMQHc7dJv5LU+'
        b'/ly0sfgMv7WzgDk+aGt3H7kuJ9kvbp6mWGG8kmdhzeNOTOac5NzY2ptVbHZAy1ekwHPutDzhc6XAf003ttiD88TLwgD0PM7pWeJjgZuRiwn0b5Ly4bMg2UeebsxHRG8U'
        b'KFoJcTaqx6JUnMR4UvzE9MeBZhofBb4UvHu9UZBbUEx4TPAngR8Gxn3/R+GfBBZGuATxnvEaBTl1PyVDqWR2Wlgl3Lu2kEkjfbCUb8MnETKFttyVugTsjVp1/1mStTSm'
        b'xicu1UM7h4rR0E0ydwkVaayepBWoiMP+S+kQzxYZS973xJtfFzNXu9WfcOxnr/Ktuz8Xkk4+I0WbcUHfOFbl+xujKLZgF+dr1z6m4qyVYCjinOn6OAttroGOHPJyfna8'
        b'hw/5rMxm6Be66mVwL3Fu9ni/qKS37ksn7aNvTy28sOxll/jYYyJcQjw4L7sO87J7lT/ys79gLB/4zoYn/ezPiIzcEj6vs91PSUFNnK79tNNc4XP/iumPPdf5fevp0ZGn'
        b'L4q4JiPqp/MNOwHniGd8Q5o4h/Qy55D62sndJBL+2f2E5ekYlkwmt0TkrvSvPN1mj00MC+ft4ydyatYwqxPDklMS45Ks9e2X27pLoBCoHx8cTZb+V5jDa8tNaY8U1vpX'
        b'jphHJ6n4PDn4nvIzPePntJwGfhKaVmSCQ9Y++ehDKlzHk+AkfdfHLOcVJmKxFbMSvRRlseQA9kVZjnmIkzzpLeUm548DPwn8KPD7wZHh/WEsbnD2W2dxpGz0bNdtQ+nd'
        b'27/7ykuvf2dTwOvfPiXVeZnIYLwuO9p/rG68vqjJ5ax3nd3Y/uJvKzVFCSqN1VM/jDeU4UvEzBg5G++LXJEo6reH0+KF0HVm2f7grQ+YxIbMDF3O/rmWBpMsDRSKTj9m'
        b'l61z5gYOJ4uufNmcg6ate0X7eLPr3kaoc5WYBpFCMg4Uz4lwSA9u883zbm3JWIsNj4vNyAwchgdQvIqMn67erqxOwS7SSBCGI2zrb0rYCXy2nRxXuSV942O0tGJ4Xnno'
        b'k2TDcX71R7r4mkKhT8Q/9kgDP0JD+DwXAxjSejoDeMain077T2RtfF19YYnqJ9ek+uQn82fiw5fuZvz3mYA9P+fXZAJrB/pIda34NEwqieXHpnh/8XFg7xcXvvXKt4ke'
        b'a9rvbC3aW5c9Li0wf0dc53XCUMRpDqHQhzncBacViasbSdYV4ENxOlY6c/SxB0a2uTpjFfS5r7rnkBOxFOdaO1y7/bmF1k0By+tcCz0kZyNRiG1ESwqxrWjlrKHPhaot'
        b'zwgTP2Mthjy1vCmbFHQ1LCAoyePpHmhmyEqklgxnSsk8h//5tqH4V8Fr+Z+X0Jg56EMlNem/FhLbLwcTwpKDWNJcEJ8sFBt/lcQgqyK/NO7/LQrg35EAzJq5qbkwggnz'
        b'TcemJCUz3zRPkUnJUXF8KiEzktd0LvOG86oEMBZFoMHXcmwvEx9ba2JQKg8u2vNX0BxD7if90AoeKcwqw3msfIbkXSV2g7xI8OJDSTdtzMOyk8ZQ6exC6OYkwOqUTK46'
        b'zPaBXL6sjFgg9hmtFyaP6nI+Xhl/sWC3txaL4ptYnN8v8OHLLnI+y4m9WGWMQ9DsSWN5sftLJTFR31f/sTCphb4+tPDXsBJjFZG92omB+YjUnOOfvqon+EP2cTWNUNlR'
        b'0be3ZShpVly9EPTB+kiP746UvpZZ5lLd6/KRVdOD35Ufgi7HXcfbgzJDdvboaPzy+2+0NX0+mx9a1aX/Z2HhqerbCfVxez850Hb6xej39Xz2adle+fXuXbP/031KKzbp'
        b'csrpI2kF8SExFsN3Nw/FD/dd3Dno4BVxIf9PL6Z/MfZZXdPRsJ8b/uZXrxvKcc7RXVBywdhVd4X0h/s7OC60wQ7qV4n/ARHzP0KtHHchAHIhG/uW7oGQjMb72LSkAdxU'
        b'5xyRhvG4YAz3wzk3JeeihNtQzTk35aEGq42NlnpPyqcYHxZBa5Qq72Rsw1kckTSmlDgpVUVLbsoM/raDG85sxSKYU310zVYIoxkavIpxi76aeORXHYJZ5lv1xMW1JbCh'
        b'zNf19L0pK7mSy3Fap2/OadWWCmnsEqlx3TrkuISC3cL09WvwPJpotYOPUxTsRF+tVJB98ejZFb49+mf8c7HryvVPZ9dPWTqBlfMvcvxafjn5nM8NIGQRvCmOCYqL8HEI'
        b'kV1B+WxjGkuUf46xcHavlPnCFLjYL4s3i/JU89TypPLUJeFFjXANCWuXzZcn1i5HrF2WY+1yHDuXvSHnveL3FaHFG+I1WLt9aCjLWY8LS12dHsTianwMjw85hsQnJoYl'
        b'JcTHhUbFRTzjSikxXOug5ORE68BloyuQY5pMhMTrBwb6JKaEBQaaSLLlr4YlcikXXJD5icGCnhpU1g8JimOsPDGepWkspekmByXSeegHB8Vdfro8WRV5fEwxWzPu+FQp'
        b'8yzJxADBAqNJCWEh3A5NeCivKWce3ZWIS4kNDkv82lHUZUTjl/Ho0kNqZFRI5CqBx+0oLig2bM0VxPMZ5ktwiIyPCSXkXiE+H8s/jw1KvPxYIsDyoSXp81c2zPQ9Wa5w'
        b'alQSvwLSASLjQ/Wtw1PiQgg96JklnTxwzYGWVh8SFBNDZxwcFh4vkcbL17h5JEhhqfAsih+05jgrceipkFxO0rPWf/w+x6Pc5qV5n5bjLBkr2CL4yVFW3gr5ivcZpyDV'
        b'xdtT/4Cllele7t8pxG2ICEPDlo5qaSxCfR5L1k65PhEWHpQSk5y0RCLLY6154gZJ+tw/WbbFE4tbpd9IMJNtJYHsDPrta2hnq9QeVQnjW632GHhwGkdaKkwmWZA8wFsn'
        b'hfHsRnUHNHL+shifU4pXrwgF6jApxHwBkqG801DIV//ovgH3mH9OKFgfIoJS4XEchQnOf6FzKojeOs2rTLvNTHdjvrmRsztpT/0+CTiWfIaFwqELykQCqDKSPwQ52pz/'
        b'YrfbHiwyhfwViQDOnK3yKIIfckmOlZ7HWk6L+qW+ElfWXJAREaO2V0/A3SUWBa1jysVyAJ7PRTQxNE3b5yItsDGWwYYtqtzurLS8jbEzAStkBEJ1AbRAA/Rw43pd4sud'
        b'BG7OjPFy38TXTNmawNcQF8RcNvnwxnb+Q90dfKy+LDJUyc79LH8hO8yG9MJ7XO0aRYEiFEAjV4KLe+Hz63Jc0fUy+5tKTqHHBFxysVBfjjbu4u7txHmWnWnlxcZM5Vze'
        b'BX3hZOLiZuZsaiQjoO3NY6uh0hXVnSnMKJN2UntCZy02JPUI+nwkGquhjCABSkm3mpWHewlqDoZyXA7EbrvYpfgni35iM+k3jdCjzCui8zjtwa6wsxmj2B12K2jhL3vX'
        b'hJIyVbR8f5205kHouAijXI6EOTThtKRfH45iy/Itdjd6gL2+DiYxy/XRLXIcwnGYww577j5+LDxwMbbxW3mXnN0khxJnPo+6AO5AvrEZ7Q869ZZukm/Q5Xr0wgSBq/bJ'
        b'i+TcLfKGZO4i+T1fQ0V+pC56vIIDPFcEQc8FBqAcb3N3+y/rm0myWH3w1lIVhOMWfI2EezcSjFdkx2saSAWTatloJM3BDaZ8I13ZDWA9zOFrIJyFSQ7hTC6l854rmMFu'
        b'lowAPf58jYIhfAilzHlngjVYsVwGAW4LuTII+o4stp2OvasKIbAqCBbQLwFLpowr5mxcnRerz7dngfaIAEnO7bYDywUQqnCBm1wN8oxc9betvFPPXaifwhq+QMIsnZYr'
        b'R4mQDfeWPQf6kjqUCzCEud6m2O1FujQ2Yp9UmPAwVGMW//U4PjTxJgOqzBcase0Ua+tnKoSWeDWuosGIjJijKrujoSYXAjYLOODH4gQhXxFWeooFML5epCTARSwPM1Tg'
        b'67m0e0MNjTWRpJKYgqNKOKoKhTidTAcRLeWsAQ84NnBCB+6ufiAJJ1KkBRvlkYAvRag+DsN8Y+eJMKhffvQyTNHTqclX5BOVVWQEu6XEeAsGcIQvntB+1hNroADHU2j6'
        b'K0pXoEQ1MUVKoKkndRCGI7jmz1iiAveSrqQoED8ss6CxVHFSnuhgIoU9vrSMo5dkpDGLb7CjjLessfMq/86KpWqGSdlfjuQ7qQwF4OLyA6nJN5Ik69sMQ+JdUAg9fBeZ'
        b'ShjbjnetVwyVnIgTtMCTUtaQB/McgSqc2pW0EwaXRyOWLCNQkxHhkJUW94CuDg4p4lQyLURJXpk0fOUb9OVmGMfqy3w9h0J4KE+HeuoU9tmyI5XGWSHRzn0o4XZ0LgLH'
        b'vN313LHcG0uw2htKWHHSBiHrIQS9fOU5lgU1+vgskXCfZmkySeH7gkIljiXhlCp9KcJuIXbLGom1ORlD4qYFi4hTupq7u3n6MoniJbHRTRjPLHZ2w0LiHSlYArd85ZPC'
        b'IY8jQU1oPOEKFf6s7arQWoBVPtDErUdRHsZw3IlYh6spkZiHmIRek1QGjkHNeSjgePe/9HUF+1jLitik6512djxDH9pmJPChD98VhG5zCHIQ8P04BJ8flfyy285QzLkI'
        b'pIizthCHqURmxl8TXLsh5nLAgvdDCQyImRhJF6Qf28aJkDPmZKni3Em+iwTWYSX3sbWqARZpQDb9GiWIIoCXR422bBcnZZKoufCGdqyXK2unMPgHnbf+MvniP16v//fR'
        b'D1S9vmet+FqMv36niau6244fbpTd0bFZPswu2lxka7fe0uvlrEPSit9RPyQ0eDflbs7t2w7eF33/mJKS+rNXF4r/vN3UUvjW9zs/naiMH6uLGQ/9rYvH3Zc3XXW/Ydc1'
        b'o/WnX/zO8tfnDrjUvV347xOy1obS0z/efVT42uhZcfEH2/4Y3Z7hX7TgdWN2t9Ppnw31ffTu36ONbqtUBR49+bdjHz38LG67yp2R6uFQU7c/vP6J0qH7uXsufe/0OsPT'
        b'RSf1fr7D6UXfDTeGd1VmOruZPfyJ+j6Plp/89e9bD32QkdsaMt4q9YcbFYafjzs5lvvOdd3zarKa+ZvcHz98I3Wi/I9hzoaKji/6e/2t2ltxT0tO+YeR/7Nh+hxcvpCg'
        b'GThcfd70/Vzj/dZ7vl+X7He4d6xBOUv/rbO7/vDWJ6+cC/p9w2Tf5MevxZ2dj/r9evOLGXXwyssut0y/XR3o8qcdZ8d+9ac/p5ydaCg8Of/G4drZHxqXDL/Zk2hnd0x3'
        b'/sObeX6N4755soY6v0h7UVw6oaSq1NTzYHEm4tMPwmIPV3qUvNF4/qXf/Dr5Cu4vSpucWbAaUT3y67qfD+WA449Db6Dh3NiPPg7cOTX1Y91e953rsq9+6/MfhL9z8G2T'
        b'Y7/f/r9dX0T3dNcPf/GXi+u6/+rxUvMv8MLUxDsvhR2xMOj48cP6P3/5+gOb89/ZOGe8bZ1ObMP+tw53HZx5oeRzEzXZnz0sTMtLtRr65bYz9lcFJX8M2vTp22Vprapp'
        b'yT+7tTHno9JCK7dBBfVf/ux/YP7nL4Wo/9LP9H1/X5s9/UZzr93snTtVZ/nFteyZ9NBt9z749Htdf3kx6bdf3HV44cuExYBjPwu5FvmR7d7JLEfz7335uazA6Yvz3/qJ'
        b'oRnnvomGNhaRXZULpeEshQ1O0HYABrgAjvwRFr9hWkUyjDGtIgQK+SyyLDFXk42PqXtyj6hjnhSOEIEUXzrEO3HmiKkVK1rAgOsTmXvYCk180YlOqLXjUvegIeZR2Z57'
        b'57ghDPbByFKy2YpMM30sh7t4B6v4nsSz0O5svOxiaoRKaMZZRc5HZIC1B5bS4MywgcuEww7s5kAQvAMajM9DpdlauXDn9PhLLA9g9sKKCnF4y17mhmibUIevn1uDkyeN'
        b'PdyxREYg3ic85QB9wVjL32JZhEmZJf+TAeZwqX3XcZjPj5u/RIrVivpwpHzEwSgMq/N90q1gxhWL+Oq4WjjECuTCrSvcuH7QHepqTHK82FVGoAVTMtdEO4hx3+Zrs8zA'
        b'ODQuVQ3G7BPLRYOhkx5hS06CaY/lqnVCfCAHQ9DkxE2r4o91knzG0AOGkmxGj3jOTXjET8QK05vLkkDJFEGH0BfrLnADJhib82EMsVhIykAutGIOtvCXUctuumORCat+'
        b'XESQcDchuW8uRbrJNFZvTeG2I3KT5gOBJwlZSpYigVpRXKtxxfVKEiUsB+aZEnZFj3fuFRkx3++KYk49mAONRlAmKb+3Z9tKlXcCbrMuFzDIF2W+R8c9K1F65YKWVV6o'
        b'3cztxwcWE1dqvHc9YO7ofr4h932WcwnjFo9rvDgMfJaiLpY7cAqvHHYuKby7CPJMeZHCNpheW+HFh85M4YVe7ODW6I/dO42VsJ9G4oOgNA9mScVjviUHNR+uTWERaYCe'
        b'piKBdzihpBHZgreTWV7zTpKOOSvUHpyEW6pXcFIZR4QWcEtogh3S8tBEBMhXEdtxwpU/HgMcNWHqc4MICs9DI+/lLcB8p6NykhKKUGDuzLXn1nUQE5HdjeXgnakbyNVn'
        b'3O9CysaUWCCL7SI5KKZtc8XE2nbTxgcOYTMvNo2giwNmLLRukdR6kRSz1dwu5WNNDKWQ3uRUuF5DnEq9xD9k5o6FpMjT1FgnJrOl9xJfU6bXVM5YZz17xNOEtAE6GZFg'
        b'w37x0UjP5B0cA5g5tVQwdHW10DkCU6t0IBSe5HG1gfWm5ypJFroK4SEHdEUoEWH7NuCL72ADdsMo5xIvMBHR0FkyHiI9HLzCAzIrQRWL1qW6P5bsqxnLRcs9gwkHx1Wv'
        b'mhpBTQDHCOWxT0TUNgB8a/ULMB9F52BquHv7GYY6ESJaYLeSoep/fm/qkUv4v9ide2WsPSg0dFWs/c9MvfpmXvIDrK+KCpcXq8VXu2E1boSbuZLUckIToYZIZTlnVk4k'
        b'Eq5nTmlJriz99ngnl8/FimLhqp/PxZ/IbJHjxuN7uPDubTn6X4mrsCNmvbk/k1GSEbJy2GrcWlSEKiINoQrnsZfj6u5s5OrlqHB5uypCVi9HhcsQWCOeugIsEp++PO+Y'
        b'X/aRJx5nzvpl73jiidV+/v+sJLksP8+jgbkZ+cmW5+ZiBKwPb6GipEHLN4oRZAk+N/v6Qd0VADGUelNuKYb66C4iax28/J+MYIVn7IJAwN8s4kMD8pLQgJALDrDQgChP'
        b'PU8jTypPM1xTEhgQ58vkCDKl0zVYhNdPcF2aCwaIb0h7r/h9RczXW7RGYMA3QZIpvDouwHnIgyQe3uVg8NO97UtPrL58lCxxVq8YwkTisw4JilvTkRnMYhL6XLsj5nR8'
        b'egTieZzzLNyx5qxGS8sz0ucuGHF+1KV18F5xfkksxEFLj+M90Ws7xvWPx4eGWVrpBwclcp5cfsOJYQmJYUlh3NjfLMjNAVASx3i87NFaAQgafu2yHBL39pJzn/nTv8r/'
        b'+029vWv3KNrikcIu65IK1xtKIolvgd6oQwrL6WcEuksN5XHYhU9ME0HxwZW+VSfmcMR8T2+YFT/ys7pIC9KxR56U9n5c4FoaR2ueMOYC4/sVWKW/29Gc5Wx9lu8AKUi8'
        b'bnJXLYhvIjPaJOOtnHBFStABrInMj/+U4ihguSudeMsYepk+nY93vZlr1N2Nk7t+jxJ/fZ50AEC7ubRAyleZZCxZEZwdfgULFXAcGjCHb5iNUx78xfqBzH8K9mUaiAV7'
        b'AsPOCg5F8Ab86/V2PtzXRtrnBGkb5oSCwKzoNNPd7vzXDh123Ld9MpeFPxUJ1N49mnG4Vfsk7wiGinQlyx3wQMw3V2+HDq7VzzFL7F553Q3zTV3csZI5eUl9dJY4zrkO'
        b'Ta6nnVxMXJge5Aud0qyc6l1lF5W9nNsXxuONN274etkKLFehM1VS9P8SDMJtviAyFmzHvJVV/532cB5D0Z59S5f4sXTJ/UlaXxuPQnk4JCYLqeSpbufdyxUAIBseymdi'
        b'C1RycDI8x5cjf0U5ySQ6eKPEXWIXzUNxztZPEGoXIxTYZaXXSdfqJ8ow6cGc54bSfOPtCavzMIDZMCDgfCjSu/gO2zHeMECK7n1eGyQc6+avwLU64YwxFEO+xJFShnPc'
        b'OIbYcYO5oliAOEoQhTOunLMyEys1mQZM+FMkw2qNlokPCGEYOjP4lrKhto8SLMnU7Ze4Sk8c4B3mrZE2SyaC/TWuruv2y1FmJ0vFSYOEa0YfHLMpXyx91U7tuxE///io'
        b'7uGbTT/MVcxTW7c/WcvHb5u1gtj6dMluDcPcpN/E5Bju0pDNM/q73Melhb/9lU6awsP9W8/5NzT/4/cvHWydfNtr30cySTNz48WR7gv/CJ6wOeKnO55d+vsbfdVTc5/E'
        b'/t1FNzYjKeZFtzsv6cbec9X6w/bFpF8aJI+F1BZYy/zt/Sj99jrLDxIejn/7gcGuvFcj7nxWVJv8+We3XkqzfVfzL4Eq8T/Tu/H2ugvFzW4mlT8IfOG7hT+8+T+vvfNm'
        b'mfSLvt/bGXL3jZsTWi9qfn8oKtf91F+2vr8x5cUfvWxTNyQs/9TnFwXfmxFW5+v9LOLDuz9/z/atfcdtqn7xoc/Ijwdt/nnKSfiRjM+Pxsdb/lH/Rf4vN9wL3qL7+Xv7'
        b'/YbHTf92oMp6zvSUqpf91EeeNzZ4Jf7ohxlFJf3vdr1XpBz0E/NTA5Y/++7v7Po+S/9r778Giw5555W+VvZyV1W/48SXQz/13hP8XpP5qzrvWg7jiV3vnan6hfzkT/8t'
        b'V/p63I/8frdLxyhBuuoNs+90p757+e0/vf+vbV9Uv1645SVt07/dTBba/Fz3PQNd67AzXs0dP5wwrvpH6q8X/1d63776sYVrhut5g3sOa09JLFushXb+ol+2Fae6rxdC'
        b'7fJVvVm8KzFunU9ISoZir5ri414KKMIesdzho5z9m3wtNRUn2U2C5ZIUVw7w7odsIq8B3gTGYhjhallc0uJtn2LdY7xnwlzMpb/EX+V79zyIgv7lFNckaH+iRKoWN/aJ'
        b'QGVJ70sBMYIurvvlIZyRFK93J3Odb3ypf3K59aUZlPNfj0Apjkm6Wwq24kO+u2UL5HEAcTsYJWnR40K8f1rSo+cQ9PL+iVvQDnnGtCLalr4qfbtJxMqgknnKuT3yFVK3'
        b'QNmKmv2m4ZIiqEehJXDZ5D9w8JHRXw3D1nzJ/gUcNGXmN/S6cY6KnVpk3R6QuqAOlZzJRsb8Q6jkjDaWJJlFh+bC5IexjEAXGpndWZQpSQBqUYShaDYI125QRk/EIgDz'
        b'vK1eIjZeMi8vYvOyhUlbHo/hnEtK0OkpsS2hCLpW25cHoY23Qbut4KHx4+YlDCmIjxKvGkhm8QuYxjLttY3MVmmYgtzAOBziD2XqPOEaZ+SZbof2JSuvGuv+Q9Ve879o'
        b'1z1m3CmtzFDgrLt+Jhe+mXV3U2CmxFlZCpJ+mHKSXpkmXOMh+kSKvhGJORtLzD3H/83aFbFWRaxmqQJnkS3ZgGqcBabENTJiF614G02B+3M9N48G92e67uO3IFbsR2KW'
        b'yfAGkfOykcRskRV2mNr/bfgaildMZr48I2eMeTAzhPTEJDcG529mjJE5tufp5tizILGUPbaXLctCtIYpxlRXTm31EHAJ4tJkfPEdAEScOSbFDLJwpWXjS/y1ja9IMr7s'
        b'10q4XTK+HrUBWM6f5dJu/y+njfPvLBW94d9bo+Clmf5xPuGGW8pTEom4LHNmodGjzt6ehw7s2cssotigZJYukpScGBUX8dQl8NV2HiXPPF5mkP/+uS6yyHlwGuqGC8yh'
        b'uIZ+6ou311JRQ+UdUnifGDRrL5d4svfjg9nYb8h/Oys64QGDq4pIiTIuQDUXu3SAmj0rGwbAqLkkVO6yO0ppZFqclEVPff6vMNPCUWXYo3Xij63Ndm0Rgu9o5+8MFCi4'
        b'OhmqWXQmNcxYTY0cfMGp7w8tb1d6Dwed+EAp1kHLtfcz20xtty+Eb6yv9IyN0JQy+I6r3djftrz7ctrmF9L8DKJbdeLfLHzjoVbRwOXtYrf1Af8cj495we/+w8sPXH8f'
        b'du7jIe3NR+Pdtr+b856hNKcAwAI2yaTEGa9IlE0x5IVlnq8Vlt587KZMZhw28T75yRDIXq1cHIEiLgpylIQxJ6ta4qBNW7SGq7zaYB9f7bxcR5nzv1uclxVw7ncD71V3'
        b'YP4j8bGCu6ukcCS2ir97PA9/vynYuHRfhu93vMTjGUdP3/QY51k962ouvJoNreDC36wKN7FY7v29q/ksx2JP0WfXnpvFFmx7Oot99kZZydn0qATmsPmvFJ5cuoHT92R+'
        b'a2JIZNRVSbEhSdXcVeWN1uChx3l/SMw1zoESFZsQE8ZcQGGhW5/KbyWbe7zEDn38dVqvCNbkWGIPvptKvyM28KGup2VSyZ+VEQRvkIuCPr2of2cs8B2JT6vmsjvmZ49f'
        b'/Nbr354oG3XquG0o/T2NkMjwmGCToLjwyGA3Sbe1nia5hIFRQzFfW38AKqCPI3+sMV9Klc/eyn1peZno+qrrcgIXZ1yk4BhfBuRuAoytZgDY78wxgBvOySwP5XgSvTnO'
        b'CH8Ui1l/S+buKTF2dr/CPe8LBSKBKwzIwkgEtH1l4ze1IP5sl5AsiSPiQ89HxFaMhJdrfS77bR+bYXX999OryXR1ZctHT3CUx3ys9UpLTOabUl6W4HfPuO76VatmFSWk'
        b'PTx8HDwMRR78/2pfUSTvUXUNdkOXu6XH3X/isuo5tzmnrnEMhdsbDxid/7Z6/jXZe+IB+lVFUVIIQE4kVlQQrt/yeL07NTU1kZxQS1VOqKJA32+UE8p8KWaA/XLXDQ2h'
        b'WZyGUH+LHN+PbyPWYt7j18H1cIyFJXcbSF9VxvKUT2lOj8woaIYKm3hs3KMGd3Aa59cdPABZITgsY435UA4VcmTuNeOtLcpQhrnQBveh8sQJ6FAksisU6pJJOI0PlaHe'
        b'GiegFMaCYBL7fJRFOAQ5OGxzBB7CiBM8dKSn7mLhNZiGPrhvdh3uucHQketkc/bIkkXcTz9z+6EL7mF3xBWLnVi/l9Se9jhoIS2nD8ew8boN2YLdWACjGxyvHPFcD0Xb'
        b'Met4ZrQlluACTEcdwTuXHTduCdroYO0q7W+RYeYJ9/z1TKESJ4/ALPbAOJTFkUVdTsNMOcGUVawR3rUIwGJl7A7FEU3ShNqgAjvoZx5rAo9jwynLaCgJwUEZss2n8E48'
        b'jGI5tnjjIIykxmInPMyEeaz1gXId7Lh8Hmug8+A6HHKC+T1kgObQRKXqJ2DYG3IMXGkBU9hwCIYzceA01AuxGxrwFlZBE/19NxJ6SVvrSN0spQhVrA28hQnew6nIQwpH'
        b'cBLyQvQgyzEWbofSsLXu8MAwxCF+iwOWRuFDbHTBan9tGEyzxxmyV5txxEYG6k4b+tK+i6AachV2+eC4NrZjB/1r2h3yoOksAaMaak1w+pDtTpsdWpo4doY+aMowOG+M'
        b'9divpsluYsGkTxJ9Wq6isA0X6Y1+HIVhWs6IAGstww5j/QVotIAHGtiqEuwOpRHJtpjlhbWboSjggBwuwoyeJszEwKIu3Img1+8nEHuu26uHHaHbzpyzMcdKwoMZ6E4K'
        b'IpSrwQYfJZ0L6XGHM3BC7+ImaPCADp3zOMzajmCvHG1mgvCpATvssPgE1shB3kmc20MnWQMDVrTR+7TEacg5S4dw1/QoYURhGoxt0MVCAtE8tqnckMIHWOC4QxlvpxQT'
        b'1mOOBuRDs5c9lBLeK8EDHF933Y4OuOckZG2GJqwzVdqHQ3REo9AidRK6Q4K2G0JZpBiK9G+aQ9ehlPRIVawmbOzAXgJucUKgHyysOwsNdtAAo9AJOUHYZIS1xrtwBudg'
        b'WgpG5LFKF6eCpBOwGSZ8/VOPYmOmdwwMYCPBYmE37YJQBAfjXA/TEC160IjZp87S2BVnofYg1EFeMNFetsjKHStgxJSeGcNe6M88n6mpdvZm8D7HCGxSv7ZPHQdpq0WE'
        b'yzlEFrf2E10VOG5x23FtF2HbXajH+3sJywcIO2cwPwgrYuAB7ekkzkOBLHbZYkUGtKa42kfhoAHm7SYDY/H6QbObcOeSvDfMaG9mZdmwR/2QOB4XA3FMhGVp64NO4m0Y'
        b'V4DiG05Qh9l6jlDqD1mYG6oKrdDr6e1rEaKxSwf77B0VtDTM9kjrWvoSDTW7Yb43nXAd9mvTWdyHrCDsPkDnOA+3MFcKKzygHEf1sckDC8lsgXGxOmFf4QbooG3ku0Ml'
        b'sabcAAsGXMjH+zCRmqYDJZtpykHCq940woe8dHU5lqMajlU4e91Ci96pg9t0PCPEuiblIlRcsFUHhrDt3BlSIqogF6e3XIQFd1dYhB75HVCRREyhG+5YheF4LBachQWz'
        b'jcwteMETpnUJ5wawxAsqXF3UL6TiJM3XTbjQch6yiYgWaWfZFjigaeC9Y50nZBPMJ/2xK4ag1+sJY4Y4Iw11wTugfZ9/yk8IITftu0ToaAN3GTqy4mfGMJFihU0XxDRm'
        b'G96OC4K2K4pEl7X7T5lAt1qgK/TZQjFOEbAeYK0uodFDKKRtjcGwM9w5T+Sauw0XnGxtbbDOBe6FqilgLqFrFyHUNNzeDg36Vwl/a0W28OCa4ICZM1ZeTjamUxuHblJ5'
        b'CmGO6KaCaK4x+PzFOGIeHSbYGE2gnhcQHhUSovbDPajBqgsniSkuGm/wS754CdrcaYWdWIYTu4kwyo9us0jDYi15mF2JrkQcNad0aB2TqZhjKn8TJuI4flmlcg3qiVF2'
        b'27sdSN8aAiMeGdfXS11yhKINkB1OG1ukAbqJMeUcsCXkrZONhRLoCYBKZTrePn1lqDyE9U7QlkyPZCPbSSu2kETqgSxVEebYEAvpWicL04dwTnsXIcIYzFngQ61UvBe3'
        b'7po4Moar+jfDktdUCVCdtL1ufADjp+gkO9Sx0H9TJOFZDo7aQSeB/MEFA5JLQ/5peoS67bE2WBZI0qvWEPpSiRqKzegoOuwtiMcVEEaS1Lyw7/J+LN8djb2Zx1TSaYE5'
        b'kMXqssH4Xv3doUEwTrxmWkkLK3EOc5Qw3wFaLHwIH6D9Gi2gAO/uhklohwG4m44dsro7CMjz2Ongbw4PsUnBwYg2fIcYZBuJ7MYTMO4Y4UXLnzcnqXcryZ9OtJ7kYSvM'
        b'p2PRVai7KBuGNTbhjmacRL/rmkzi5k4K8YQyeqbmiOOGs1gLjZehUHRVG5oIuQmIhNzQci6aFrqIrVI7410csCCOtIgwP9lNl3BwI9Qy5DIneu5wUMdhq5RXCa3PYSPB'
        b'kfhsHKdePMBhY5wSntwcCG2yWO+lIIRRlnFcShRTB2XJMCYgXrtjHWbtJRDX6WXgkCzMQWeY425oOA4DmiQNGnTo8VIVbJKN1YsmtGlQJUqsszDEh75mTtB4OgOr9KDY'
        b'ZfNBkgLTCgSdh1gkewr6Ahm1BAkTLjBdqDkOh3H+oh8rCEnc9z4xAdI/4g9Ao6adsZcGDvtDeeAJuHUS5tSwzfHmeYJL28EMTSj2dvOHvp04cXPT8UBiGv10IgOxBJQB'
        b'aDx/TYg1DpYw67MnQ+U4ZkMj1NmGkFy+Rcfcoa1OwL6DnVKwqI4VvhvUNpLgK9SCsotuQT5EuguWp61jmH/9LFSaQY6blrkW9sbAfTsivvxoqNqFt44LMUv6FMyFHoNq'
        b'hygYt/WAecg/ZnX85I2NWE/YTyyxi+bLE8QS/+/AURloIzIoWE/kMkaguotNFrAAxTpEpU07YT4Tp67YEtbWkZQrxZojV7DDnjhKVujpNLjjGE8n15YJNZnrCK8mQ69h'
        b'X4Q21hH/ayc2UXgYS/zUDyAhfBl2OpJaRCjdpX+Q1tBMv92zO5jmqEYS8cRGGPcmJJyGiWv7iOYXsP84FhPYcknetR7czNSxRCgO1zdgiIjlWkc5XtBBy8yCliioCVZP'
        b'94Cxq+7YRBNNEGnVQkUULaiPdIIcEZSmEOyLdTJoh40kPwdIbCadhXYzbMFObU9lb5IsPdHrsT0Mq53piIkkLkBzIK1yyJaMxE7Mt4LbyCh9AWt8aYi8S5FXmQzC7Fgd'
        b'HE8gDjOGuTsczingiO5eh9ObVK+nlDP9oR7vBrGyjkWPFAhjnBHGYikpEDaHjGF6D4xcVTSwkk0kBbbO4QxWHKPNQJs9HfECTTyeSGCaYkzo7Da4Y4k5e+m5UhqTZi+E'
        b'kYQMG6XNrrCAw8HYSs8NEQ+pvbkFsozP0JnPiA8RN6yBWaMDR3HgIqlp1TgbRipmKUmxfpLRk0i8LeemKVZpEObmH7sIbS5Y42VHwrUszA7qfY1I6+iEeWuarZT0kTZ4'
        b'oEr03QztatjnBKV707BCxX1LRCwxvGxZopGWDIUAGNlpfcJN20aZ0Ow+VKuYbhIT2JoVNKxwYssuOSkHvLWVIJm1k1C/S12XZHwpjTl4AXMuQpU9EHuyJTFIHIp0BJwL'
        b'wCZsOXyFuFY19JA86SRVf4QOSnjK9AwU7WRJt41w3xNzzmHHBWsodDNxJ9DlQMHxaF1Px9NMiym8eAO6gw3xVghkaWbok8VTgeXncSqR8KfmNA4EYr7pHqgVEbK1umGe'
        b'PaHYIrH2wYiLZJSUEfsu0NEmEE8EYuVhzIPW+EME+l4LuGNLaNOJ5Xv9tcIPWHkGQ2cgzsRfIN7cdlhVYaflQS0dS0Ni7BNKWKB5wsOA5OHiTmjypVErlFmx/lgo9DpD'
        b'dDJ3Adp2QbdWKI7G0YSNtM3mS0QNXefD1hEDqoBBMxhWJGAWYm0EFGyBsYsJlzYchf4YemgQ6sOJRdRLRdOqsrwJ4ycs4a4NLBiQxJ3F2ze18KEgBhuNsWZdRsrrhJUb'
        b'XC4znMyO41BygVAyDQfCsPeaHGk8OZoZBL3sXZtIu53Q26OBlWqkRvp5pTtB2c0tOzNS4E6Q9qkAJS8S4PfYD+TsJ8ZfQ3yEXrNhGtN1NWW4n0anOoetZ44qkrCcgkXV'
        b'QOzC+mgStj3SmJWC1T5hsJARR181Bl8kTWaIUx6AlId5WIgi3B8P1sbcxC3YtZtQooMoZ8AnDsuv6xN3aGKqbiQtIP+Sday2Ir1RTpyjhkBR5O5POl5/pnemX2TaNiUP'
        b'JG31HnZtI8bdc8E2TYUgWwSMbstgJi7BVgOmVJOJQLITSaEoO+thKb8DR4I98BbUeNMjU3BbFvuVwzD/NOviSh/nJUCDKpkpt6ElDccCCEtHzJWMXYg91UepOURfsyXD'
        b'qWMTUecwcZoi3d1igmX1HlI0yzZoQVWc/paTRKb3N+GsI/GtEjJMJkggz8WxJH6suLITu7eTZduPtzOhYbcpsb8ZWZosB7stHcMs07ZeCGceKyKEnBSigQYFqNiLpZct'
        b'sdFtJ5HBuKZ6UjDxvgfYfw77LxLFdG4l7Gs6SBrLtCXk4UxCHNxLJvM7n8zkDXu0iFfWHmXW/+HttOyySCghlUEae31JUuYTklbaXsZJXx3MFUMVDofRvM2EaA2C7ak2'
        b'CeeS1p+i8x3dxm6qNUN5aDI02aZB4XYskL6ARdFQf4T1I4YJ0jhrseAMCYki0kuatAi7h91UoNVl101PQtD7OJTuH0O6Yq237cmDzDAbsIIu+0SjCzBNaHXXHUYzorTC'
        b'if/UqxJ+T5jivdPXHbHSwYiwYmjDNsw2d4v2JfgNQ46hDJegYgUjNpvxjquztEBoLqCXamX4xi+5IZrEPIddl+8j0dIHuFe8cSpWFmpcjUUCoR3j2kXKfKmRLkMSJdlC'
        b'dqlAeJS+cIzja9vdCnZ3DmT+fKFA6MIu4k1v4dNS2gygZyftuMhEyBUnacHGnSnOUqxN7gghdTOJoxKijAY7JQL88A2FLefloeawl2qQJomlcjPChw4CVTVT2HfhbWcH'
        b'd7gTbbvekBjNNHbppJNsaocWZzX788S7y6ApGO+SvkIkjK0HmMOFTO/yNLOU49C/nul5mdAVFoR5itCeGER0UwmLtpDldxqrPegw6XuixtyT9Gsn9LCofZ6vBmlwjeZ0'
        b'Zs0W53YQ6mVvInNg1Mifxr0r8KQ5c8OIoQ6TCK6kwybzJuo63DEj2VruA2W7yFIYI5Q4R/pL+S5icINQYUU2Um5ygDs8dCV87yQRUUSYNaZH9lIO2WT5VobXIc+SlLc5'
        b'YhMjJAvaYGQrqcO9UH8o7NBVKbwrG6aKdU6Xoe8AziQab8HZSzhwznkdNkhBn+z1lDD3xABioeXQKc88B1Cnp4PZBNsBYkjZxB67L5yj4YoJpDX+WtFEuLO0irL9tNtu'
        b'm40KfkrYEhLI2V0NUphjQZZMFgFmEImRLlpAsRSO+Bt5WmDuWWJs7YdxZBcRT4+lMbCrH31QdphUoru0pazEDSlikkxlSbSNTlg4cZ70yUooNIIWWbwfhWVOUH0U23zJ'
        b'qCom62VBdh0WBW4NMTyui/floDoQqhOJWBYMVVKwLyQxEbvppyJTmZZbcODMWbIgB4kdl1vi2HHH6+rhoTC5WxmmVLDViVDt1kEcNHcm+u6DO8h8OwWqZL9PQPZGaAog'
        b'XgA1R53OeZxP9Du3gRSifBLjsxsOYVWiuSUxi7GrUsQjuuC+6XpYTInEgYNk2JUZaWLDBsbKSdzl7blJVDq5nxTGAuaNMvQIJ3EK0+bQmEw4lQfT5yEvjiR4J/SfIPod'
        b'dL0JgwFk87XQqQ66WHPelwdSJGdaz0eQPdUFdw9u0L1hTKrnhAezI7A8HOaxYw/9sYgL+uuhJizJJFmbFK4BW5y5pIzZyvhACC2Xbp4nflub0iNixWcK0x73yxAnHbLV'
        b't1O9ivfXy2xMxfZQIo7sYOLNo6fOY6GL1np7MlwWoTaRYHlHUUv6XICbF3GeMsuNhDc1MKyD3Xu1XbcegfEMsgfyzmp7mobYy5JYmzl9hnPQjHluoUkaoPIAQeSBAu1g'
        b'LI74SwdJlYVInEqBKUPiQ0VHjIk0urEpjv5x9+o+aCCxRhyqjOHpPRg1gqE98aTst1jjWOh5gvId9zMbmKqJxKq7/ISk8D0gos7WI/oZdSQp1yLWwx5jYr7jeE/zDPRu'
        b'I85aCo12iW6kZ7dEsNsidozBjkJ2Zgwp+Lp2pCjc02FldR66YU+6xnEF6I+9SLy4mHcDJIUQ+pdd3knLIpGG7TeIE8zqERU0k5ULPe6XBNGYdyyGWE7TpWMRJBvGsSmM'
        b'VliRTII4h94grRybQ0JhOObUQZzYoAYPt58jTKjTwi57MwYRI+zbEIazUYQ0TM/vJ9vhQSIuXJI+oob1unuxwjOBWFqxJnZokP1VmUFqVBYsXiFVZ+Io9Kl77j5quYPE'
        b'bxtW+8thu2M8Ab1xt0HKZsOo9accNdSxTfNmirUy3Dkm8iCE7yfsK4DuG8QF2lPOOEHReWKzt4xhRiuMaPIBEcVUpl8sScs4KJXCUfr3fdLxZoOuErNtsrl+Frv8TYkr'
        b'NeCAIcwfuwSDW3Y6E0eoZAdMh/CQ+Fr9NqKcIRhUp50s4OKNU240bud+qIhd5+hJ08/pskoBx2HGnphwXoD0tqPJqng75efMCKglMrkFzd5YtGze+tEKSqB23xZm4fp7'
        b'KQphUgPzPWBYxhQGz8ushz4kNjixnzBh2OoMLkChWZQV4Wg55zbp32ZKbIx56erVTSCXuBoh6R0YIfMAH6Z6mhrSkQ3gA1t76NODelW9jXQAxTARSuu4d/SIAPp0iLH0'
        b'74R6K8zaSsxuDO6fxVZfaLTwJ76T5wxNof4kFYbPMC2lA9v9Ew2kpSKPYI05dqVhgRmMbffBnLg90Bl9jCRDJ225h/TWJgfiODDrhoUm/iQ7Go2Inm+bbvWLxK6D684l'
        b'4kMPQrgakh65+7TkoDU6DkYINi00w4iHLNHBYoInGe7lhDPF0JlOmyZ5tRG7zaE6hSRKrUc0YRSZLbUmynGQq6BvjYNWUVjnsj4WHkBfCjZawZx9ItYS7O7iyJnNsLgH'
        b'Fn0Eh/C2shwuStFC77ivg1lp5iG5ZwXdEeudoOak7kYrUgoKaVc4eJg4+QPCjGEihWlCh4UrZIPe1yS41weHMPIJj9xNjLVEdME+4ooSTJ7H7mhPj6jwSyTZx1RoFQ0k'
        b'dAcUcMwVikKg9ozxBiAj4xaWRCsF4X0fuKtpF3gxA1tc3DftxfI9OLop8gKWWoqY+kqMKJds6VZ84JZ2nQBQFKxG0qsdH24W74QaTS+8E3LW8dIxdwci82IbrE46FIqz'
        b'24gpDbFe72QeygQQh7iv6K/HcRnGuasIlnUh+2AUJ7cZEvnW4b1rRHWlMLKb1WJQlyUB2Z9wdh3LaAvFhVNX6HhKkFSEMnmY0jhsRmyt5ZrmTVUDIrF64jkPTTA/AFoO'
        b'xhJlzmqnHCOtRgOqDq3CbDJvp6REG7AXy+1UE6FTSybagLhuM+1llHhizV6hi48zM59CcCYEx5WJuCZp6+0mh1WwTO/cJjGheAOJ72JS4++nE7Cr9/nI+8LQAWw4S9jd'
        b'QKx7TpGZ5DCg50vQJsMaStdjrrcDU340abDBgC3QZYGDJ42QNBqXTQSgom3QaraFCLT6CDSuI8g0JpHY6QmD0bN6hOcNIq99unBPxwqygqHAnDRgG+KIYXh7i6+hLrGL'
        b'ikjMkYfRsMSbJLxyYML/AAmW8TDGyYtkk09ZQp/SQQLyXazXDiAwzWpgR8Q6HJLbnW5/5MoGaD4Iw27XCa26SPp1Yr0OTiW7YJ8GqTt3SZDOR5JASFc4nkin2EKDVGw7'
        b'lAydh8V7cfDoDui1VcCmZLyvFn5RG7rV1a5A5Tosdo2ggbKhykTWwp1OlFQNgsyMWN89we6gVzQObSPm0Ed01BS4DRcdiIXVQrOzvQ1Lqy0kyiQ9nLhXBUwphmPefpLQ'
        b'rNjacRjZKC8kbjAdcIGYXxedygyNmqu+zo8EeQnck4PbkXDHCvtMSQrk37gKFYcuIHOTdwhg/NJhXeIpc3AnyoAIrUcb2k2J0OuJJkbIrG4KlNfZj/MboNbnkGuCIwnR'
        b'XujFQTG9cgvG9bWsyPS4B9320C+tR7TUBIs71+mQPltihGXXsYyBpiAVxqQSdh2mT8uPQIeBH86StMQa9R1HdmDLIagLO0uok481iSSdFtLO4/C+I76QE5NMrLHKTHAA'
        b'uoPStIKDCeoxkTgPJcEwcoU06HJS4EoIWqPWxFlzd1iRaTiLeYnWruE2xAbysTDDlIA7piQk5OtXYtoxHWR9aFJaJsx40j/vQYMbmeitMJzghEN+nGycwPkj522hdjfJ'
        b'TTKBHW1wwoUUuGHF0L2kydX5E3EsygaTupa1zc8hRSzFiYhF4uhESNmEz4ySFnDemHhxHaHnlBVOaNueJW33LFYqRB2HgR3YeNwcyqVIyrUps2ds1KLIbnyQEeHkRCpB'
        b'jouvlT7eSY8nJXsBe+zp/MegVR4fHJCNIbkzIMR2b5zbmQlZZAFW73JQVfTGmlAuvjbInP03M6AK5phT6x7MetEmiVK6mbeIVN0u6HZaj/XXvAzOmbMaFdh/BLNvYilO'
        b'6pF4zL8Arb6kcE2aykTGW2jDiJMCkT4rM1FiQZC9E0M0sKCKbRe52oMjJF1K92KZriztskveFIeuR5ISeCc4DW7bkGguhTYpHNOWx8Yz2g7a7MrBbmm1TThz1BfKVOzk'
        b'iGvOYZYjqTQDjKftxyEBCfFqvLtHJewU5J533X0oOVoBF9T80g2IwZNebht7Cu4mYKWFN5nWTBMdt4q8TvhRYAAj6tauRMPtG2BOAabOXosxwt6dxLimsRFyL+FcmgLe'
        b'OelNdJFLpkkvsZ1yMlu2ErBrN2OzkoJU+AYsOhcddTHAEhtcVYQn19N7g1AuAxXqG4jeKmE6WsnZ2BynNjMHKEnuLHiwEaZZ+K5HbxOrpRN81Ib095Z9BIt2GNpkGgfl'
        b'btuJKkrJ+klKgfp9dAZ3nHHyiCJp8POkGDSdTN+AHUo3pGkHFQ7QoCl/nQiugv5VDovGcYHXoGUrGZU5Goc8YVIbmtQO2iil4i0XzNULkMUeH6iIlBTJKPXyZx5T7Elh'
        b'Di8693niviMkI3Kw0wzzbwRsJQQlPegMPdvsQZu55YdT6WaknEEXkUsliep8Rf/glHNEkK3AZAnppJ0HaG+LmVC1GSvC2GX6K4Qtg6nahFQDmZh3EwqIk5PqcesszVwK'
        b'+Slvk64ERUnblsnAjjmn7vqRDCYGFn1U30t1B5YRAfjtyKCvm3QiQuS1sVPn0A463UUcioD7sk6BNMkUqUhdogM4pQuL2HMwWpF2lIttycACwNnnjkCFGGq0iZM/SMV6'
        b'V+iQol+7YS6MpE3vDWKMd4mWqugsyhU24z0XYqQDBPpirLhORDp/RAsLDsC8KXbscMeiGBbqcmbeqtBTBJzcXcRSCpTE2B+2kdB+4po+UfnsXs94wrdOTQtaW8We9Viz'
        b'fYshNu46SeoCkcZxQoYFrUicVMKGw1uxS5nsxtwLkHMcZ+1gQD6NuEslqT/VxJnvsTsSczLQrOcEtYpkI3TtUYV2+71Qb8m6Fmn7rMPe7ftkZDD/9HEsUMRbx0+RTTxv'
        b'RhpWnhWOqibgpLmSqwV0WGKlvbUdAWUcGsRE9J1+pDTMEMsI1FdjN79miRXMQrY+YfugkFSzm1f3EsJVekGuIocXswHEwBcv7yKG0IR58QS4bsYIJvfQMJXhkXDvEGE0'
        b'88JXYuEGHD9Atk15BOTLQEekPvSKYdjWGqeYgY5Zp4l/Tbilkkh/aClDqvU9KN6NOSYEm+H10JEJteqEHvnbWDhZ+rrMgQgfGrnqiArWkPYgk8pUoBzN/XFk8pFWf4t4'
        b'RDl0a2L9iQ1pLLXCm4DXAHOXru6EflN44AD3DKWhfiupV43ETy+T2TMI90wDSAEisX3AOn4fzLkYXMGOnVDnAt3Ge07iuDTJlFrnrWTYNuPYXpJwfYxI6r01TliSjj1g'
        b'hou+O4i11XoFqgRk+mz056oTZO13oznqtttsscsUsPzby4QHYymS9sRQroylSYSmOVC3VG7HCHPtOJeTHYzEcwXihLGqrD5cCHYbSvE33Oqs5a55uDLH0iEBrafmAn/v'
        b'as5gg/oZV1ZpQrhHQHDKxza+atzwRjqOfFt2yUosEB5nxS5mDnBD2Ry/4ZTxyEFGGhgtjX0RCZOZfjjtysrhWtBXrsHcHEow7bKVeGGRG71iJSAKGRLzkz/co3MmbYVH'
        b'LQsXaSjOFTZ65CLmh2ORIb3jKSB+Pg89XK0hTeIabUT5D7DInferlRMuN/ObzLJ33xG67IiD8mOGQt7lNmtEhJEH9a4uNJ6xAPPPuHPbdCKqatwbv9IZ9xBHDYUOXL8h'
        b'7qrb5hOsclyknrQg0CQ18YjAUIr7WC+Fffy9UBX6eOrcQb7G0Nhp9uG7MbKCQKWjAakCllbmwI3G3Y2LavMTipPGiFU1/8g2s9LPU9deKzci9aIwJ1bpuzLH9m5y++NC'
        b'qpy8c5aWfOd2R3kNl0+9xeb+VfONPf8W3Ih5udRv1wdbxx68nfHyF+Eva335h39e+Z3bYau3sq7EZh79+9tB4VqXXX8u27VR6JmkojaREnC6+l/HDHMTzm0d+yjqk/mp'
        b'hxfXK5+Ifb/nSndcg9JvMpuwo8DorT/9VDHFe/9Hd9/94NTvjRzbdw3+Ijri1+Mp6961TFv3nuX1deVxVmZ1+e2f2b534P0SH28ro7P5269sSak8FGJj+hefit4eL+Mf'
        b'eJ/tecVu16XPdMvDmwObX7mhaXH/4wSPrkuf9Yb+z0vqDQn2O83dfyqKtDee/KnBb7r7VJzPfbdP9lOl2M6PU6vqfvov5+l779veUol4Z+rCq/4/9yi7dPevroPf+f4H'
        b'Ow1DLL59xHJs2+GxAKc2TSsvq7cmlH+e8FqzdGLNhFNe8j9jLjlYRRQ0VJ98Y9vseacOxV/umLepuP+307P7beMTwl2jQ29ZZbzyw6FLi8b9X/Qe3Kj59/bWS4st8y5J'
        b'phrt51+ov/zXX6T8YsDrD1qVR7tf+V1XfUTlCwIZqx+0xc6pL0Qf/218dVnrzd4Ht5zdh6M+mykDtT/v+IvHd6bq9H3s87503PDR3mL1se22up/9/a0KwV9Sa/6i+r2E'
        b'kx/5vvHT61IOex1uuA3b6Me+rfPPZt3cPd/d++1Xf/Tu4MSrv6u2re+wdIzQ8H6guvfBvc3v/6jpu0ofOyw2vKA3a/L2+OaqsD98emT9hwc/v2z5pf/PRvYlPgyLN1fc'
        b'axJccK0mucXkaNs7XxTPvvnD1N5kFeXOzZ7Bzn/R+f4PDjh+P1DHWC/sBd3feAStu3z2RZkDo7m/z1O7OlJk88n7grw52/Q9wx2H3vTZcuOXOoc+iP/sZROHeOX/fb81'
        b'wud3v3/tgs9NUcD7h/r+FHDkU8dPx+Bo5nut7/rmfvnPgi9z35H7aV/h219Kb7x2eiQjwlCBb9TXxrj7uSCiZp6VlGLxef5mV07k9t2xT9yjE8v5QBd37U0Fcm8s33oj'
        b'66v1sWtv0L0jmZVQOwi3zygmKssrE5UXpeKcamKKEvG7aSmBXrpYjlSah9zdrL2BnpKnSMZXsSenUq8oywi07aRg6HQaV3QFBzVhJOmq0pUUnFaFQihW3Yq5csoKOKJ6'
        b'VVpgqCImjbYxjOtKF02q1cSqRyXPQcnSyCynyl0sQ7p2wUku93/9YVggexIbloeUwx6RORRcSt7L2NE0NDklQYncFWVWHW0CCp4ckzWZd8dJGTLDmncm76a3pI+Tns/q'
        b't5Bl1SQpXfdE/ZZqaH6yZ53l/9s80//nfxjqcVz2/y9/8C3HAwJi4oNCAwK4NOxX6A+BsUgkEu4Tbv5SJGL31TREclJioZyUjIh+pFSkNTQ05NU2q8mqyWgoaGmKRVrO'
        b'2tvo+ZsCS1bh5BBLy5YSi9jvm2/SWELtnSfYZwEi4RE+aTtEJLRmf/stfyKj7b/RXk1KRUpDTSQ0uSnYLhKe4L/5P8VdbWwURRjeu9327rj2aIsgiFKaYu317lqupQgi'
        b'VCsUjuu1ftQPEF2v12279m5v2d0r5UsKpkU4PgRMraCgpRalLRYEpETAzEQNUYu/xExiIDFq1MT+kPiBf5x39grEhB8aE7K5p7u3s3Mzs7Mz77ud53nzrUVWN/14KLZz'
        b'AwJLbfWyb2Br5/oEWGj9V/o1/XLgcEy+4aPVXVvozGuXoeLXF3+X3vpOccs6o8VsDLbwGprIAx0ABkruonrzIFvT6XnqgbzmoP7GTmoqbS6A0GhoC9pp41xT+LvoGNQt'
        b'J6ZPTdMnWzhubXBS+fa5NfyDWYv6m7QDl6IXvo9lpOfNmG1pnPiZ3571pz3bmKfVO0t7R093DGf9cHnylVkvFrWdu/LTqos9BYHcKzVTjw6dFT79uS1ysWuk683TR12r'
        b'Mp4ZyZg/Uh770XNg/cShQ5XFnw/m5098vz+nlSib83HxPZ3zf5nat+L506WPzd1T9MdoSW3X4QtvnT87wruEwcb+utGNdx7Odj54YdZ7dy7f9uqlTXv9o/KvlXrLV19v'
        b'PFox+PaGg6OVy951HOqbcN534otvTlZ8N83OZ+TN3NThj9Z1f7Qx6W4dco5f8FvWc7l5LvWl/IVzPnHUz5jz8ZSRlRtdR778uFxRk9MebTj10A7r720f5S+9Ipb8fKpm'
        b'AX/y4m8TOuLnelauqJzvdeeyKek+1PEwGLC1tYyUa+Oc/vvRMSt+R8EHTXbWVh9+O+jHr9b68FFIByvXs/GHPHprCdpr6th14/0wFrO7cbYERAPgnQ+9Gzn8NLxjDaNE'
        b'l+bgLSC8GrKxYAOdgtWOdpkT5sI86gMmS6ipSn2UxzjqopxBnYw2EvL6Pcp4vKMQmMXbLJyj2Ep9it4qU23qjXJ00IPOVKcEwIQaC3We+nGvqXvVOWl+MOCFdxcBXyqF'
        b'C2/layymKtsyfDAXyDEdY9Js6ADqqWLTZkUF3udBPaXsqlAAb3cHBC4H7+Gpd0I9UTO67EApfilY8NBSb015mYWz4d3WdPSK32TL78d9aCCYgwZKywJMBpDpoOXx81AH'
        b'6jJL9yE+xAXRIZ6mCITMBC58hPe701j2j8RxD05ab4d4rzupwfyIhVr3u10m0aYbnSrDSZsFbw95OU7wW6jbvTlVLgc14Yc9uLfJh7eD3l/Mgk6hnSIrVxE1II55ICRt'
        b'NfxiiNacbxa4qesFtCnXbVJx3kTHs4NQIlp1aHEnPoHfc1up2z3oTQX1rSvQb0gwDrejdwJWNGTBZ0wb5ukXnPjYeHxCp/1lH9qCP1Dx8ZUoOT6TegT5gg0dWccyursC'
        b'n2XsJA/kxnHOFtpp9lqpH3N4sVnP/a11OIk6cf8NOnb7FsWZhhs6ibbRBhwspDd3K8TYApHG2oBOMymp8bnTucWLbOuoDTDMepgLJXOceAgfp6MI3lUc4nDf7A1mJzpe'
        b'6YHF1Iwfn0aHlT3rLLgXd5WZ4m7dchTO+kD12+QaRWUrd0dCQJ3oRGtK9Cz/CU9ggw/+x4G3VFs5R4GV2iXHIqwS0+7FH3iW+rwhX7GFunkDePdEfhxKFrHs4UX/4SB6'
        b'GZ+mdyVYTK+nTxAt+4QyHu93FJrP3yB1uDZ7lniLgAQKd4R28mH8shUfWYvaGffxgeluDzhtaDcaDsLTeA69PhYHqfDWD/P/02Qx6RbYJteDFqswK7nsjEJvZ9ttTGbN'
        b'niJsAgsMDA7Yy0kFKaYpeeXfM8rGtpkmrYqZDUWEj0qKJtMJjaQZCTUqESEq6wYRGuQIxbgqKYTXDY2k1a82JJ0I9fF4lPCyYpC0Rmpe0T9aWGmSSJqsqAmD8JFmjfBx'
        b'rYGkN8pRQ6IHsbBK+DWyStLCekSWCd8stdEkNPtxsi4ruhFWIhJJVxP1UTlCMhaZ5MZQuIVenKFqkmHIjavFtliU2KvjkZYqmRbSUV82W1JAtIpkynpcNOSYRDOKqUSo'
        b'enhhFclUw5ouifQU8L1JdizeMPdeM/qH2CA3yQaxhSMRSTV0kskqJhpxai0qTYR/KlRNnHqz3GiIkqbFNZKZUCLNYVmRGkSpLUIcoqhLtKlEkbiUuBivb0zoERa3iTjG'
        b'Dmh1EgqoVl03yMz2LtRawGRTAWIACYA2AGALahDbRlMAVgA8DWAAhAGeYgxagGcBmgCeA3gGQAaIAzwO8CRAAwD8tLYaYA1j0QEsA6gHWAkQBXgeAKxlrRVgOcATLGcg'
        b'2q2CvbVMJe8aiRA6kuOacfXn8psaVyzlVXsj7TdSpLmYZIliaj9lo1+9I3U8XQ1HWkDADKiucE5qqHHbGR2Q2EQxHI2KotmBGWEQAsSRdDNOq/YtfLN+zCb+RwxoYr+f'
        b'9oJEVFoAMeV0CKkqpFNr4b8/SI/fxlQL/wYqJWQh'
    ))))
