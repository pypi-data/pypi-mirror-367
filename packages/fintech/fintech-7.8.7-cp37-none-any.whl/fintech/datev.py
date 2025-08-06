
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
DATEV module of the Python Fintech package.

This module defines functions and classes
to create DATEV data exchange files.
"""

__all__ = ['DatevCSV', 'DatevKNE']

class DatevCSV:
    """DatevCSV format class"""

    def __init__(self, adviser_id, client_id, account_length=4, currency='EUR', initials=None, version=510, first_month=1):
        """
        Initializes the DatevCSV instance.

        :param adviser_id: DATEV number of the accountant
            (Beraternummer). A numeric value up to 7 digits.
        :param client_id: DATEV number of the client
            (Mandantennummer). A numeric value up to 5 digits.
        :param account_length: Length of G/L account numbers
            (Sachkonten). Therefore subledger account numbers
            (Personenkonten) are one digit longer. It must be
            a value between 4 (default) and 8.
        :param currency: Currency code (Währungskennzeichen)
        :param initials: Initials of the creator (Namenskürzel)
        :param version: Version of DATEV format (eg. 510, 710)
        :param first_month: First month of financial year (*new in v6.4.1*).
        """
        ...

    @property
    def adviser_id(self):
        """DATEV adviser number (read-only)"""
        ...

    @property
    def client_id(self):
        """DATEV client number (read-only)"""
        ...

    @property
    def account_length(self):
        """Length of G/L account numbers (read-only)"""
        ...

    @property
    def currency(self):
        """Base currency (read-only)"""
        ...

    @property
    def initials(self):
        """Initials of the creator (read-only)"""
        ...

    @property
    def version(self):
        """Version of DATEV format (read-only)"""
        ...

    @property
    def first_month(self):
        """First month of financial year (read-only)"""
        ...

    def add_entity(self, account, name, street=None, postcode=None, city=None, country=None, vat_id=None, customer_id=None, tag=None, other=None):
        """
        Adds a new debtor or creditor entity.

        There are a huge number of possible fields to set. Only
        the most important fields can be set directly by the
        available parameters. Additional fields must be set
        by using the parameter *other*.

        Fields that can be set directly
        (targeted DATEV field names in square brackets):

        :param account: Account number [Konto]
        :param name: Name [Name (Adressatentyp keine Angabe)]
        :param street: Street [Straße]
        :param postcode: Postal code [Postleitzahl]
        :param city: City [Ort]
        :param country: Country code, ISO-3166 [Land]
        :param vat_id: VAT-ID [EU-Land]+[EU-USt-IdNr.]
        :param customer_id: Customer ID [Kundennummer]
        :param tag: Short description of the dataset. Also used
            in the final file name. Defaults to "Stammdaten".
        :param other: An optional dictionary with extra fields.
            Note that the method arguments take precedence over
            the field values in this dictionary. For possible
            field names and type declarations see
            `DATEV documentation <https://www.datev.de/dnlexom/client/app/index.html#/document/1003221/D18014404834105739>`_.
        """
        ...

    def add_accounting(self, debitaccount, creditaccount, amount, date, reference=None, postingtext=None, vat_id=None, tag=None, other=None):
        """
        Adds a new accounting record.

        Each record is added to a DATEV data file, grouped by a
        combination of *tag* name and the corresponding financial
        year.

        There are a huge number of possible fields to set. Only
        the most important fields can be set directly by the
        available parameters. Additional fields must be set
        by using the parameter *other*.

        Fields that can be set directly
        (targeted DATEV field names in square brackets):

        :param debitaccount: The debit account [Konto]
        :param creditaccount: The credit account
            [Gegenkonto (ohne BU-Schlüssel)]
        :param amount: The posting amount with not more than
            two decimals.
            [Umsatz (ohne Soll/Haben-Kz)]+[Soll/Haben-Kennzeichen]
        :param date: The booking date. Must be a date object or
            an ISO8601 formatted string [Belegdatum]
        :param reference: Usually the invoice number [Belegfeld 1]
        :param postingtext: The posting text [Buchungstext]
        :param vat_id: The VAT-ID [EU-Land u. USt-IdNr.]
        :param tag: Short description of the dataset. Also used
            in the final file name. Defaults to "Bewegungsdaten".
        :param other: An optional dictionary with extra fields.
            Note that the method arguments take precedence over
            the field values in this dictionary. For possible
            field names and type declarations see
            `DATEV documentation <https://www.datev.de/dnlexom/client/app/index.html#/document/1003221/D36028803343536651>`_.
    
        """
        ...

    def as_dict(self):
        """
        Generates the DATEV files and returns them as a dictionary.

        The keys represent the file names and the values the
        corresponding file data as bytes.
        """
        ...

    def save(self, path):
        """
        Generates and saves all DATEV files.

        :param path: If *path* ends with the extension *.zip*, all files are
            stored in this archive. Otherwise the files are saved in a folder.
        """
        ...


class DatevKNE:
    """
    The DatevKNE class (Postversanddateien)

    *This format is obsolete and not longer accepted by DATEV*.
    """

    def __init__(self, adviserid, advisername, clientid, dfv='', kne=4, mediumid=1, password=''):
        """
        Initializes the DatevKNE instance.

        :param adviserid: DATEV number of the accountant (Beraternummer).
            A numeric value up to 7 digits.
        :param advisername: DATEV name of the accountant (Beratername).
            An alpha-numeric value up to 9 characters.
        :param clientid: DATEV number of the client (Mandantennummer).
            A numeric value up to 5 digits.
        :param dfv: The DFV label (DFV-Kennzeichen). Usually the initials
            of the client name (2 characters).
        :param kne: Length of G/L account numbers (Sachkonten). Therefore
            subledger account numbers (Personenkonten) are one digit longer.
            It must be a value between 4 (default) and 8.
        :param mediumid: The medium id up to 3 digits.
        :param password: The password registered at DATEV, usually unused.
        """
        ...

    @property
    def adviserid(self):
        """Datev adviser number (read-only)"""
        ...

    @property
    def advisername(self):
        """Datev adviser name (read-only)"""
        ...

    @property
    def clientid(self):
        """Datev client number (read-only)"""
        ...

    @property
    def dfv(self):
        """Datev DFV label (read-only)"""
        ...

    @property
    def kne(self):
        """Length of accounting numbers (read-only)"""
        ...

    @property
    def mediumid(self):
        """Data medium id (read-only)"""
        ...

    @property
    def password(self):
        """Datev password (read-only)"""
        ...

    def add(self, inputinfo='', accountingno=None, **data):
        """
        Adds a new accounting entry.

        Each entry is added to a DATEV data file, grouped by a combination
        of *inputinfo*, *accountingno*, year of booking date and entry type.

        :param inputinfo: Some information string about the passed entry.
            For each different value of *inputinfo* a new file is generated.
            It can be an alpha-numeric value up to 16 characters (optional).
        :param accountingno: The accounting number (Abrechnungsnummer) this
            entry is assigned to. For accounting records it can be an integer
            between 1 and 69 (default is 1), for debtor and creditor core
            data it is set to 189.

        Fields for accounting entries:

        :param debitaccount: The debit account (Sollkonto) **mandatory**
        :param creditaccount: The credit account (Gegen-/Habenkonto) **mandatory**
        :param amount: The posting amount **mandatory**
        :param date: The booking date. Must be a date object or an
            ISO8601 formatted string. **mandatory**
        :param voucherfield1: Usually the invoice number (Belegfeld1) [12]
        :param voucherfield2: The due date in form of DDMMYY or the
            payment term id, mostly unused (Belegfeld2) [12]
        :param postingtext: The posting text. Usually the debtor/creditor
            name (Buchungstext) [30]
        :param accountingkey: DATEV accounting key consisting of
            adjustment key and tax key.
    
            Adjustment keys (Berichtigungsschlüssel):
    
            - 1: Steuerschlüssel bei Buchungen mit EU-Tatbestand
            - 2: Generalumkehr
            - 3: Generalumkehr bei aufzuteilender Vorsteuer
            - 4: Aufhebung der Automatik
            - 5: Individueller Umsatzsteuerschlüssel
            - 6: Generalumkehr bei Buchungen mit EU-Tatbestand
            - 7: Generalumkehr bei individuellem Umsatzsteuerschlüssel
            - 8: Generalumkehr bei Aufhebung der Automatik
            - 9: Aufzuteilende Vorsteuer
    
            Tax keys (Steuerschlüssel):
    
            - 1: Umsatzsteuerfrei (mit Vorsteuerabzug)
            - 2: Umsatzsteuer 7%
            - 3: Umsatzsteuer 19%
            - 4: n/a
            - 5: Umsatzsteuer 16%
            - 6: n/a
            - 7: Vorsteuer 16%
            - 8: Vorsteuer 7%
            - 9: Vorsteuer 19%

        :param discount: Discount for early payment (Skonto)
        :param costcenter1: Cost center 1 (Kostenstelle 1) [8]
        :param costcenter2: Cost center 2 (Kostenstelle 2) [8]
        :param vatid: The VAT-ID (USt-ID) [15]
        :param eutaxrate: The EU tax rate (EU-Steuersatz)
        :param currency: Currency, default is EUR (Währung) [4]
        :param exchangerate: Currency exchange rate (Währungskurs)

        Fields for debtor and creditor core data:

        :param account: Account number **mandatory**
        :param name1: Name1 [20] **mandatory**
        :param name2: Name2 [20]
        :param customerid: The customer id [15]
        :param title: Title [1]

            - 1: Herrn/Frau/Frl./Firma
            - 2: Herrn
            - 3: Frau
            - 4: Frl.
            - 5: Firma
            - 6: Eheleute
            - 7: Herrn und Frau

        :param street: Street [36]
        :param postbox: Post office box [10]
        :param postcode: Postal code [10]
        :param city: City [30]
        :param country: Country code, ISO-3166 [2]
        :param phone: Phone [20]
        :param fax: Fax [20]
        :param email: Email [60]
        :param vatid: VAT-ID [15]
        :param bankname: Bank name [27]
        :param bankaccount: Bank account number [10]
        :param bankcode: Bank code [8]
        :param iban: IBAN [34]
        :param bic: BIC [11]
        """
        ...

    def as_dict(self):
        """
        Generates the DATEV files and returns them as a dictionary.

        The keys represent the file names and the values the
        corresponding file data as bytes.
        """
        ...

    def save(self, path):
        """
        Generates and saves all DATEV files.

        :param path: If *path* ends with the extension *.zip*, all files are
            stored in this archive. Otherwise the files are saved in a folder.
        """
        ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzsfQdYm9fZ6Pk+DQQIDBjvJccLARJ7GGzH24BYNuCB7SCBJJAtBNbABu8JGPAC7733ntjYbs5J2zRN24yOlKR/M9okTtL+Tdu0+dM0ve85nyQkI4jT2/s89z7PZXzS'
        b'2eN9z7vOe873AfL4EcH/ZPi3TYCHHhWjclTM6Tk9vwkV8wbRMbFedJyzjtaLDZKNaKnUpl7IG6R6yUZuA2fwM/AbOQ7ppQXIv1zp99XqgOlTCmfMVVRW6R1mg6LKqLBX'
        b'GBT5tfaKKotipsliN5RVKKp1ZUt15QZ1QEBhhcnmyqs3GE0Wg01hdFjK7KYqi02hs+gVZWadzWawBdirFGVWg85uUAgN6HV2ncKwoqxCZyk3KIwms8GmDigb6hzSCPgf'
        b'Bv+BdFh6eNSjeq6erxfVi+sl9dJ6v3pZvX99QH1gvbw+qD64vk99SH1ofVh93/rw+n71/esH1A+sH1Q/uH5I/VDjMDYVstXDGtBGtHp4nXTVsI2oAK0avhFxaM2wNcPn'
        b'w6TB8CuUotwy15zy8D8Y/vvSDojZvBYgZWCuWQbfPxzAI3F0KeTRyi/YU5FjHESSi6QVbyRNpDEvezZpIC15StKSWZSPH6erpGjcDDF5jO+RfUrOMQRy42Ohy2yZOWQb'
        b'afbHu3NIM4cCMnl8DXdkKHlHf8ixCK8jVzSZ0VPJg0wJEos5fHQU3uCgnSrCDw2QkqkijaQ5R4KCx44nW0W5fXELlKXTZiYH8AXcRLZGV5MmYxpphhoC8E0e35pI7jlG'
        b'095uXECOQo4bcrK9DjcsX+YgN5fJlzk4NIBsF+FmfIoch66OgawDIdtJ3IS3x2hUkdDhFnyGNJPtNMYPDRktxhsVeF8Z54GMQ1wTp6WQE+CGvhvkjEOcUOMaAGlX8wA1'
        b'jkGNZ1Dj1vBOqJV7Qo023r8b1EYIUEuVS5EcoYjo57TmtnlRiEX+LleEIKP2x2Kt/B3rfCFyFvJHITDwugpt9CvThguRdr0Ywafi8QyteV1BFDqPzAEQbR0+SPzXMDT5'
        b'T31rubfnq0RvRj7Hmf0h4auB+7hrfkgRW5usfic+UDQLsehh5j/3aevDRfyp+rOQb+aPN5hRJ3JEUYwriQLkaYqZHRFBtsbUFGWoyFZ8vjAiK4dsj1ZnqrJyOGTp4z+R'
        b'nJnoNdmBrvFOFibbe4kgOtXGQPdk8r1OpvHpJSDtNpnyXCtt1dGPInE72TGvYI6qZvFcHvEiRA6H4MOOMEgJIU3hBVABvktuj0Kj8J65QoEN5BbZXYA3SeZAYgWaQdbj'
        b'vawAuSkjp0grVE0ux8agmEq1IxSiZWHPk1YYbWCRCqnITXLMMZBWswmfJTcKcmaTk2Q/aZEgfiU3lJzPckTQxLP4MtkEU9kcpQE8bcyeHYHPR+OjERlF+bAQ1eS8hHYj'
        b'lNUfshZWyk0YZcQLE9AE8tDPNDtsg9h2ApJ2lM9Z/JORwXhyyOb39pvu/mbG3L+GD+UaXxoZ++7YTeJfnOGvJ12qfefEweqQDR/mm0eOXPDO6N/+I+Gc7oXXRL/97PdJ'
        b'r626/ORPb/04Y9TKuWlvrzkv/9Q0Y/HGVxIW7Vhz8v3aUtWt5jfmfDi2HdcG187bsG2XvERz+/XIrDvv/W556r7az38VuDXvX9lHZ3z65ZvH85u+v+hW+JevLL45ylHg'
        b'P6RW88e/Sldlpp2ZM0gpsdPFPhKFaEhLFGnJUWVFR5ELsNbDyD0RqYcJXWcfBDkKyWG8cejkqCwVacjMzpWgQHydJ4efX2Cn1GScCDdFqZVZUU5q0ofsySTrRFVBCruC'
        b'zud2fAvfDYQ5zHDA+t9KNkfH8CiU3BfBPB/HJ+2MnO0iLeQKTPpWsp1cxVdJMyyr8Ry+PrGfku/kI5RWikDKQPbxbzwoLn7Vf4LRWlVnsAC3YHxIDTzEUDOpM8hqsOgN'
        b'1hKroazKqqdZbbTjaJKMC+NkXAD89of/YPiln2HwGcKHc1apq2alqFMqFO70KymxOiwlJZ2BJSVlZoPO4qguKfm3+63krH70u4Q+aHPP084F084RBS/leE7Kno7nKJSA'
        b'6m6LyiItmkwV3hoD635bzHBLFofG4OuSEnyYHHYvTfojdn7aKuBhoBwfuL2eKxbBv9iEiiXwKdXzxX764Hpk5PRivWSTf7GMfZfq/TbJiv3Zd5neH74HCAzWKNIH6AMh'
        b'HAhhoCQQluuDICzXc4zY9umUzmEzlctm7sk3sDjLRM6u0GH6uShGLHJxbahEID+iBhGQHzGQHxEjP2JGfkRrxD1xYFE38iMWaPnUfEqMXyv2n6w1B2TORKYZ9y+KbHmQ'
        b'4t8391Ptq6Ufa3fpG3SfaJvLLxk+hnDx9xaRazviNs8+dHxP6Et5unM6s+QCd0H7inhn9DD5DPWw5sD56es+GThozsANg1Lf5Krfjnw5ZM0LCUopw+9V6mFRGhU5Q3ZS'
        b'DgjcL0qK+uAzorox2WyFTa7OjBK4I6SJkHyOf7TID1/Hh1lpFT5PbmpIUzYIBEopkuEG0oC38ivwXTVbgfjWNLKTUiyNFF/JxJeB7qbyg8hDfIlVjjeVAp1sysschW9E'
        b'Z4qRhBziyP0Acp2lLiQtC6NUGSAOSKDmK5nkFg/0sRnfVfIeiCjytaIYXnbKSkpMFpO9pIStHDmd++IQjv5KOTFX10eAt9qVS1gxkk6xzWA2doqpHNfpV2Ow2kDks1LY'
        b'WP0FzHe2S7HdGkQffdxLgTay0L0UzoZ4LIVu7ZXxHgjvxi61E7uMvBO3eMbaRIBbPMMtEcMtfo3IiVubPHEL9YBbDiV8j9SQ64FAzpoAmk0xZHtBBoOcjjRmzs6fowJW'
        b'9zw5Lg2dO940+qM/CHhedTH9Uy1Fs5eNMWFR8hu6bN1n2pCyCqO5VLw1TqX9o3b+ywNf/d5+KTr6WFa7cItSbB9Am8anJ84weiIGIEV6tJ1SA9KBr5HdwPIagaJuV6uq'
        b'Ke2NCZLzaPAaMd6MdwYLqLOZXCVtgBzk0eTMLuQYA8gRxjCvHe+RVWjyVBzia7gphYUC+HifmAA0r9xgN9kNlU5koCQLlQZwcq4uzA0WdxahKjEDbqfYoqs0dIc/bw11'
        b'w5+BHuQqVOYG/dFgT9D7aOM/RlvKnwn+kXRKbzuKveCfgu8IKOAFf7J7mWmfNImzxUOZd2d2bA/xQAEPBPhMy2+Nd8S+FXsqVpxQfUaELi+Rlez7SCliq3dZId7XhQD5'
        b'eB/DAT3eaR8JqcOexwc8UcBI7lMscOHAHRVDo0jSMZGSh2V5XQigItedrK3nhQ/gtnUHd/lT4LZ5g1siwJJCtVNSozM7fABd5AH0vm7IU3yscEP+QIhvyLub873u4wXI'
        b'UyGXM4qfce17wZ5zVukNe0mug5IUfGcCuU9Vq0LSoFKpZ2dkFZGGvAIqQWYUZfiTPSBPqjlkJw/9pSsWMnkzaJLDB7XwRJUsvDl05WDTrIenkW02lNA0Aov6BJDFbIzs'
        b'H6nL0JkBTS7lf6Kt1jXsvjDyfcM53cfan5a+aozZFaHL0l3QhZShHw3I2rTxpf0Drtljo/V6fYZOZnw32w+tLgnZaZ0DgqCCdv463usvCGrkErmnElDFKaltJ22MYEwi'
        b'O9Z6Uxzchq+uIMfKGdnBJ2rxJjuM5SnC40S5CHKBoS25ugQfwydGU7TrQjq8ZzlrYxgQrgdunkQZ0im8A28iZ5JcGCLuUcoTUFPqqKbCXRdHMgc4JbkQri7IiSxCHk8q'
        b'JDCbLnx8GvmBHHWxI4aU4fCodCPl7jBPpPRux0vp8qZETL91UyKugetVyfLiRGKf2CjKNVWq48RMoPnbl5M0uozyzwBfXimtMIbrzhnOvcbfGDQgVqWnCNOou2C4ZOB/'
        b'NLBdrb2iW/Ty/B8vIoUkn5hJfkTfn7724nzRz/sB6+FQzj9CzJU/A9ZDjSzkaADer8F7yHlv7oP3kmMChI/gXZkMvCNAH3BBeCXZJIgkD8hh0kqaojNJy/O4HvQq6Qv8'
        b'qChyj8Gf3MZNkUyeyQzGW1zyDN4DMolPwPdGpEAgt9mtTgJFFW5kD+HCgUQBkQruoho0i4vgBX0LEnAe8KdaqcMN/xYvovRU9Uo+10qVbWUQFZkouwM1IaCkRDB/wXd5'
        b'Sckyh84spAgUUlYGmFNeZa3tlDlFJBsTgzqlRpPBrLcxSYjxREYeGTqyPrmIba8akTAEOikFdAi0sIwXc85fPlgml8glITKmek+pXh3IVApQKGRyvnKJFj8a7VuhoITQ'
        b'S6Hgi8V6EVUgDvHFkjaklx4DBeI4t5ED5ULG6Kt/p3SGBQh37Vfh0w2lJnsVqGQxGqtBL3x9EsIW3xPaxFdhcw3WOke5rVrnsJVV6MwGRQIk0aF8Jc822OvsBsVMq8lm'
        b'h0iqXTz5AQz1i/0wPZoqi70qPRemVxExRW812GwwuRZ7bbWiCPRBq8VQUWmwKNM9ArZyQzk87TqL3mc5i85OOqxmtSIfgFMFZedWWS3Pks9XZUsNJotBMcVSris1KNO9'
        b'0tI1DmtdqaHOYCqrsDgs5ekzilTZtFPwWVRgV2WCOqVOn2KBCTOkFwL/M8dMWarTqxWzrDo9VGUw2yhXNLN2LbaaKivUXOdqw2pPL7BbdeSoIT2/ymY36soq2BezwWSv'
        b'01WY0/MgB2sOZt4Gn3UOj+KuQOly2juqSSucHYEotaLYYYOGzR6dV8T1mBKfrjFYLHVqhabKCnVXV0Ftljoda8fgbM+gmEU6zHZTuaKmytItrtRkSy80mA1GSJtqAIly'
        b'Ka03whmldKUpZhkAd8gpo91GR0mntHtuxaxsZfoMVY7OZPZMFWKU6ZkCntg901xxyvSZuhWeCRBUphfA8oVOGjwTXHHK9Kk6y1LXlMMc0aD3rNGYpRSHVbmOSqgAorLJ'
        b'KWq6WEpnTZh+iMycOiWXphkMViMQCfhaMC9zZqFqWhXAxjn5bC2YLBWAa7Qe57Rn6BzVdhVtB6hNqdrZpvO717z7iqdz7zWI+G6DiO8+iHhfg4gXBhHfNYh4z0HE+xhE'
        b'fE+DiPfobHwPg4jveRAJ3QaR0H0QCb4GkSAMIqFrEAmeg0jwMYiEngaR4NHZhB4GkdDzIBK7DSKx+yASfQ0iURhEYtcgEj0HkehjEIk9DSLRo7OJPQwisedBJHUbRFL3'
        b'QST5GkSSMIikrkEkeQ4iyccgknoaRJJHZ5N6GESS1yC6FiKsJ6vJYNQJ9HGW1UGOGquslUCYNQ5K6ixsDECNDaAWuQLVViDIQP0stmqroayiGui1BeKBFtutBjvNAeml'
        b'Bp21FCYKgtNNVFQwqAR2N8VhowylDsSF9HnkVIUV5s1mYw1QqifwWLOp0mRXRDhZrzK9GKab5iuFREs5zTeTnDKbTeXAo+wKk0VRqAO+6FGggMGApuQzE6tnZV1sXFUM'
        b'vQCCEUGLeyU4y0PSmO4F4nsuEO+zQIJiqtVhh+Tu5Vh6Ys8VJvqsMKnnAkmsQI5O4MtszkEuAfmExdkNK+zuL0CJ3F8TPLPa3NkEQEw1ADsu94gYk15ssgA0KPxZOzSp'
        b'DqIo6wUq7RWM9w4C+dHZ7MDtrCajnWKNUVcB/YdMFr0OOmMpBbR1Q9xuJafKAYkyLXpTjVoxU+AfnqF4r1CCVyjRK5TkFUr2CqV4hVK9QuO9W4/1Dnr3Js67O3He/Ynz'
        b'7lBckg8xRRExxzmrNqegoewSjHwlOmUlX0ku8amnNDcp85Ge57s1Knf5ivcSxXoeQy/pPUln3yVzfM8te8lpz5INSKWvbF4sILkbC0juzgKSfbGAZIEFJHdR42RPFpDs'
        b'gwUk98QCkj1IfXIPLCC5Zz6W0m0QKd0HkeJrECnCIFK6BpHiOYgUH4NI6WkQKR6dTelhECk9DyK12yBSuw8i1dcgUoVBpHYNItVzEKk+BpHa0yBSPTqb2sMgUnsexPhu'
        b'gxjffRDjfQ1ivDCI8V2DGO85iPE+BjG+p0GM9+js+B4GMb7nQQCB7KYrxPpQFmJ9aguxTnUh1kNMifVSGGJ9aQyxPaoMsZ66QWxPSkOs13icXZxpNVTqbbVAZSqBbtuq'
        b'zDUgSaQXzMifomLcym6zGozABC2U5/mMjvcdneA7OtF3dJLv6GTf0Sm+o1N9R4/vYTixlKAvtZCOaqPdYFPk5ecVOAU4ysxt1QbQhwVhsouZe8S62LdH1CxDKemgnP4p'
        b'saFciHdKDa5QvFcoIT3faVzxKNzN7BLXPSq+exSoOWaqFOvsVC5VFDigOl2lAdiozu6wUbFWGI2iUmdxAHtRlBsENAV26MsMoPQoYqLM3aRnxb41s4/6fTAl33V3z8hM'
        b'TF2zowDhW+EUedlUGmm6c5KF7/Ee36lO2GWp+opLz1XKrNTzyEo3ZKzUSUXYA6HGUiu1iXZKbNVmk906xG3c45425FG77GqXLZIZ8kQ8J+N5XhznoPWMt5HzNurp0RiN'
        b'z4uRLJknh9RryINh/yEzXoXSvzNgSllZlcNiB7WhM3gqwFpQN3TVBvOTfoIRj9q+vxo8HaBfCSIFNZAqBIUHcNcEFAeyULtrp5iKPl5GvA6IL6oUBJqqCotBUVBlNsdk'
        b'AEWyqDR11L7SFeyicenzNMUKoRi1o1HqaTPZHEIETfMMC2tuFjX7CfK90NDUIlVBWYWZdADszSCTeAbTpxrMhnI9HY/w1Wl06foe79SP0l0TwuR9KhAanEvbpbQpBKHI'
        b'qfp1GamcSh8T1am6B5lhcdmZWuCsgTVnNkEG9s1kMVYpVIopVrurK86YTAst+VQkzRbvK1t8t2wJvrIldMuW6CtbYrdsSb6yJXXLluwrW3K3bCm+sqV0y5bqKxvIGHkF'
        b'hXEQoREAQ2VdA4uM7xYJAUWOAeilyxKrcKgVXZZYiBRQ2mUaVSuovO7SugWTaxcYFdlR2ekzHZalzO3VYC0HAlVHiQqNn1qkSBwvsFmjKws1CfuKd+KNkOSjwvRipg7Q'
        b'gVsrdTTRjSK+Utyo0lOx+N6K+U4UUKiXYr4TBZTqpZjvRAHFeinmO1FAuV6K+U4UULCXYr4TBZTspZjvRFpsfG/FfCcycMf2Cm/fqaxg74jSM6bE9YoqPaSygr0iSw+p'
        b'rGCv6NJDKivYK8L0kMoK9ooyPaSygr0iTQ+prGCvaNNDKivYK+L0kMpWfK+YA6kFdtJRthRY13JgvnYmmC43mGyG9JnA6buoH5BDncWso7ZF2xJdhRVqLTdADouBCkVd'
        b'xkYn56QEb4rDSM1ibiLn4qWQRClvF0NWREyx1AkCMd3PA2KcY7IDazToQRDR2Z9KfooOdy/cRcmfTrOayR2bU0zwSslguztGO0glbrWKcRIVE3t86gDOkTq5ObB+4DRU'
        b'hDYy4bmSMni7wQTTYnfbiTNB0rWbjKalOk/qX8zUQLf92FPMEJRHj31ETzFppkHQLAymUpqUDVCjG2M2QbLpWV7ztA1Dv6FlndlRudRQ4TJkMyZImaR1LMh13yrpWulp'
        b'iN7kXOo10+FTzh3kGA5Ry8hBqS07l2yLYcIuadb4zSOHUb9SsRw/5L2EXblL2F3CeQu7bdK2wLZAPd/Wt62vIPS2+Omj6yX1QfV9jSJ9oF6+yR8EX7FBog/SB29C+j76'
        b'kBa+WArhUBYOY2E/CPdl4XAWlkG4Hwv3Z2F/CA9g4YEsHADhQSw8mIUDITyEhYeysJz2wMjrh+mHb5IVB7Fe9n3q118/oiVAr6rnnb0V6xX6kay3wcKo2gLaOCMdmR97'
        b'uko91+KvVzOvOAk7WxECZf30o/SjWdk++hhIk9TL2MmLMJY2Rj92k39xCMSGQp/G6SOgT6HQRl+9ssV1kCC4vo9Roo/UR22SQS1hzv3+2E7ZdOp8Pa1g7lcxAQqPH1e0'
        b'QiAvwvkfrxxKiZUe77FSB7cnzAebHn94IhO0C7e2oJQ/oR43T5ibMfW56SplTXSVsibRh4pmoW4QT6h/xhOKFEq/zgCdvgYIl7XEpO/0LwPyYbHTr8E6QcMpMYP8Z6/o'
        b'lJU5YGVZymo7ZdTh1KQzO100Ao0mEPlKKmFVV7C2O0Uziubksh5aUyFcJnNiX4DznznxTEJPnVbyr5fWB9T7GQOc/kGyBtlGtNq/TrpKxvyD/Jl/kGyN/3ykFzE1TPwF'
        b'PQjhNWn0J1PonqnOYGOnstxTbWIuDmUGdbci3SLSQBPRVSq6pibNeR4LqA01DDkPfDnnSGexd6uB/kRMBSJhd5EopVoxhZYHclKmYC6BCke1AohqikJvKjfZbd375eyG'
        b'Gyq+eyEk++6Be/vjW/qQ9G198EaHNEU2+6RdmBWT7Up1dszmuy+UBVHiD6xDrSisAHYAyG9Q2BylZoO+HMbzTLUIviWC3go1KXRQBYSF/ivMVcCarGpFpl1R6QDtpdTg'
        b'sxadc/ClBvtyA93+VUToDUadw2xXsuN4qT3DwrkM0hTTnN8UZdR+GOHedfSwOyp7qsW1hNJc2GpzA5Oe/quyKiIEH5alpMNaB7p4TxU53aXSmOJFhRSoRsARJ2GJMJSr'
        b'FUlxsdGKlLjYHqvxWMNpipk0oGABWp3RZIFVA31U1Bp00LFIi2E53QKtSVYnquMild2n6lsciOXC4YR5g0Ij+4omI1StjU6SzUKOiYj606XFkqYcfCmfNGSSFk0Macyn'
        b'rqUZ2SJyUUmaonNVeCvZnj07A1/OyM3JyczhENmJj8mr8HELq/YGkg9cz8UilK+VP0mbJlSL90wM81kt2UYasweSVmChuPHpejfVylEy3smqbRzkP/NtkQIhrTYblTuQ'
        b'gzJ54Lr7ZnieocpQqyLp0RR8RYySF8Xhw1LbgkHsJBir5MBiafJ4HoQBhTZ6mkyDHJQK4sf4uPipzuGH2ax/pAHqbYqGqkmzcq5H33C7NRDf0OFrphPtn3O2Oqhn0keD'
        b'hr36tv+6WPnm987cvXV/S+u9DSLZG34xMc/lHlMMmpbyRWJ48Pr/Prtr86xRm8Y07tpk6Zh68Pn7b/Zf+eaM0uO5v7iQVtHniwt//OLolND8Pw1+V2f7oXj7J7qju8cH'
        b'Pp495JdbXh/99efHftRZqHn/eu355Sff7p+wb8K/jkUp79fNUsoFZ8ldeEsUbhLOP1ZTiYQe8ugzRmRMldkpZ5iF90pxU162BxwXruHQYLJRXJeD25l3LjlBWvDDQA3Z'
        b'Sg7DmHMcTr/afrheLJORO6wicl+PL0NNL0Qw+LmAx6H+I8WBfYfaqQmurBJ3RKkiMlQ8kuIDEXN51VJykJUuIdumQGG1Ct/v44ZWGL4iIk24Ge8UPDdb8H78IEqtJFuj'
        b'EVRwiWwI4xNGk2vM4ZzsNpNm3ES2U+hos53wkaKwGhF+SK6TBruS9ZKcwifpgJ1CGu0kBTBeR04AkBGKJZul6slj7fT8aBC+iOnxFZibSDXNSVrI9iiaS2GTkMOSIHKG'
        b'7GLOxyvIJsAQyAli3xm8mTTS9lXQOt4rIptxBzks+CjvJWcKPFpnIuJA3OqHBuN7YtykGy8IngH/5kGzrjMqzOmUHpdFa9EqKSflQjiZ80nPk8nYmTIZT1OkXF2oiyG7'
        b'z67kujrCHE7pmrDSE2DWyfQxhT6mItfBmGmod69VmVCqq5Ip7lKsEh9HbJ7Q7lPXS7QO7R/u6dravatu92bO+c9cSml/VqElwuEsLlfJdQaWdMkOLk9a3mvmOmUTzLrK'
        b'Ur1uUijU8xdap0d7rrSvnNTcWZuL80cAl9CrqizmWiU0JtJXlX1rx4xCxwJK3NKE735ZM+ARToW3TPjy1QihfaGQj+afdUL6lHhLEL00PsDduLJXKeM7dWOT0A3/EhcD'
        b'76UDg90dGDRVZzO4ef6/16CL1/fS4DB3g6N6lAe+Q9PlQtOyEqd00EvLiq6We5QgvnvL8hIPgaKX1kd1QfpbhA4fffA6YMAOuvH1yH3Q7duOFzzDQSdRrql45D0ROyXb'
        b'su4d4dxShfEzNOzY680/aX5f/qL80CA06aT4bfyBkmesZRTekOWkzE6qnEfanYRZja/ZR0EefDwPP2J0GT+s8dTenXR5LLnU2+kzvxK6gjyPIq2F33F1IR60imXowc+f'
        b'78HFfz48xsLc2qiHPVDCdegdr1Nn3epXBnT6OVek4MUvtdmtBoO9U1ZdZbNTobhTXGay13b6CXlqO6U1OqZbBpaBaF5VKeicIruuvFNSBbhuLQt0woL2KtgFj5kUtIFu'
        b'XTHIfXA/WLgjwRjsBHlggxxALgeQBzKQyxnIA9fInRrjJtAYfyPxoTFO0ettoBJQuVZvKKWrDf7KnD5wCgPz2H8GpZGpNEwf0SkqHOUGDzUNZsRmAjVHIZxnoBqXzWBX'
        b'K/IAo7vVQ5d9Jd16MVVWV1mpdukqVqazgMpCi4K6YzWU2c21itJaWqBbJboancmso00yCZ96UNrUdKQmakSDdeWs0qkl0Tq71QFVO2wmSznrkbsaRSQDVuQzzMhM52gr'
        b'qIWje9+75Y+w66zl0IbeRYFoeQU1C9qoxmFb5qCzW2rVlS012G3KtGdX5AU8TVNM8WIhioVsI3RxT8Voy2kKdoph4beeZeixFmFZpCkK2KdiodOzrsf8ruWTpqBGTQAV'
        b'UzAXenrW9ViWLjhQTeGpWJhntfecT1iSkFX4wtqIVmQW5KkS4pKTFQupIbPH0sI6BqVzSqEqc7pioXN3cHHUQs+TGj033rX8qRotBBS0Ik//4B6LA8GAyayApQHL1VZm'
        b'NVXbnXyL4ik9ac3W1hSzrQrw16D3aQEAdKK5KZ8xs3t1GLDViumCGYAt0ecK7LrKSnqqzfJcjwYBthgAsaAD1c6lpTexm310MK3LTcDPDCsA4s4F170e+pNbZTcIy4Qt'
        b'foO9okoPlKTcUQmIBn3RLYUFCIvGALNTZlBUAWP3WY8wJLpomH3DJgzTZPPokloxE4iaiyD5rMVz2VFrCKA6vbeozAwDFq4sshl8l9Q6by2qKmM9F/ZNJlTY7dW2tJiY'
        b'5cuXC5dRqPWGGL3FbFhRVRkjSJYxuurqGBMAf4W6wl5pHhXjqiImLjY2IT4+LmZ6XGpsXGJibGJqQmJcbFJKwvhJ2pJebA+U+3U/MhiWy2znNeI+tmxllkqdG51ZSTqo'
        b'bnYe9LzRBZKK6Xi3g5Yhm3AzeZAA3+KKyB4UF4Y3MR3+uf4S1GEGdWGyNrp2RQhyjIfICnzXT+NStGaTBnrNSJZqTv4cUOIeqObOiaDHROeBNg8fwOjxLnzVn+wmx/uy'
        b'W47GTiAbyM1Asg+0Wary+SEJ2c/LST2+zMwMs8k9cojcxBfJRjW994Keo4UW6FUmPBqBT4vJ/Zn4HDMmkA4LaaO3KDTnFJEd1a4xkpapVjrEfNKQCwWbNUXV8MjLziK7'
        b'xYhsxRsCyalQsof5z5RJyMlAsj5PrczCHfhoAPLP4snROrKTpeL1WYQetn5AdmZCFRwS4b0cXheNhPuStpPz0wLxPXyWNMSoSSM0HI3PZ4Ga3MAhxSyJGIo76AG8OtKB'
        b'd5GbfSUxkRziM7jk0fgmm94OTopeKhlCTSTZQ0eJkHAN1Cn8sNoWRHYbyElyW2hXtoifZcf32J0gyfgGPmybTbZBlqAgNdlJbmeT61FklwgNqBXhS1PqHMxscGiOOJCc'
        b'xbfVUAXMXiadGBHqR9rFfeR4i+n6nSES2wHImKhJUP00JwDHhkjeTcn86rcf5z756cZ7fw54QTf52hCl+u2ci7Fnd/SfcC5GcfPLFe/F9d3Yb+5vrt/zH1WYFvGVNfW8'
        b'5on8x5eSF6SaG78a9VXsoiO5G3/ENb1aio0/MB4b/xPTlCHFc/Kiit84cOYnQS3khyemvn330zf+sO+/bhV9/Zdt7atXOZ4//faaoJPvXGtPGnK98U9H5xVeHZFp/cAe'
        b'tfzAq0opu8wGZhffFkwtL7iv06CWFpifA0z7t8ZaNf7Kpy0PzOoQlSAh2+Pn2IczcKZODsTnyQlNN2OLH7nNZNpakFbbcNMSk6dY65RptaSD9QdfxtelUYn4SK4qMzNH'
        b'E01alBzqTzrE8aRlDjvsmgQovlUzlbRFR2RARwB++CJfi/eSdi+JNPjfvfqmx5OxATq9vkSQ4ZjIPNYlMmfQw7Eyrj97ev6K2a0eMq6ur1vk7arDaasIEiTnBci1r1dM'
        b'H/SyDusi+lhMHy/QRwl9aOlD5y2I+z7jGyjU2VVJibsJnbuJIHeLWnc7TIgvY1K9pxD/67GeQryvESn9O+V66tLnFJI6gwTR1xWU6irZJ73DxNDp79zILTN0BlJBBcRD'
        b'6uYl9ME9zLIAJxWm9pUQFxXOopJ8gJcsHwzSfB+nPB9C5XljiFOaD2DSfCBI8wFMmg9k0nzAmkCnNG8EaX67X+/SvM7tpacQLi56Bpl1Bj3YIORWAOOEeQJxFIQBneeN'
        b'fFRgiFaUW6sc1ZAKcrKuOyOqqiw1WXQu0SQSpJZIxlMFlkpVe7cnJ+2gW+PtVhPVgP+/+vH/svrhubzSKKCEGLdB61vUEK/1KJQXolwV+JTFFn6Le2ePzQnrXWjHucSd'
        b'cYI4a6mihhorE1gtvsXQ5VVUXjRV6sw9CLwLe3FwBTXCt4trjz2mlEnob2lV1VLaXxqjVuQ4sUvHwoqq0iUAeFDufe8JWqj6k5ocG+e0fFFEAN2NVrewy/m1x064CWOa'
        b'osjm0JnNbGUA4tRUmcrcq3Ghh+9srxqgk7B6g4Edqlvo6V/7rToaLf6Unublxfl/gZo11bDcUO70wfn/qtb/BapWQnJsfGpqbEJCYkJSQnJyUpxPVYv+9Kx/SXzqXwph'
        b'7/fFULF8KC8oUQusKchBXVVSSsgZTWYO2Rqd6Val6PVAXtpTBd4GCtRa/NA/Ea/Dmxx04xFvxicmgE7iqT2R9lw5Po8bHFSDM8fUadRZOSC89lIz1cuaSJN/7mh8Nn6y'
        b'YzKt+A6+i2/a8nJA9FXUscuLaAvzyA4osp00gBoVABoHVAnh9oJF+BA+gE/6I9DU9gTmZi9xKKCSEdHkhi2LtGSCfteQk6ehtx7FitHAqSLSjNvxGQfbUVwHMnaHLTKH'
        b'bIsg14qoqK7OxJcjODSiXCLBJ0ewqsjj6bGB5C7eNkdGWlS50SnkID7Po7AEET4O5W8zbXEgvpMMk9G1Jw1qDr49h97qGYebJCPI4xXksZ21Ogtvx7tY33LyMqOV5Ajo'
        b'ji0SFE5OisgDULq2M2BNGSxaNI6n37TZd4KnInYT6XDycFqgFKFChM/g9sIpZL8jhSmA+Co+GkgnCuZ0J7mbATpmC2klt3Op5giKK74IH9lkWwZVvRYNks0CRXuPg8qI'
        b'WWEp5CZ8ZqJJ+HGm2izceHqqQsOUcARDbI/zJ4eY/rgGmtnHLkKNQen4Rgw+SraYv/zXv/51eZZk5vscw6zs0CXOS2n/WC5dUsOxfXf5ocFDkIPalMkF0o6v00lqcWrt'
        b'GdFz6Y3EMVlFgBcZpLkgQgnYkSHcP5wDChK+MwdvI3foVEotQYvJCXKEXUJMDo7QFZDdCVkixKU/Ty4hcokcUwsODU0rcUsggxY+P6cLcWQ+pghfIbvECNcX+ZMDExbg'
        b'1rHssi1yKhDfosqvoPnOjiC7C9T4hMxbz32+nzQYXyU3HHSLgTyCobXbslR5OTEUlXKdmq5yON5A9knwLeMEplfPJw14f5Rw341SigLxY3JKxpObuNGf3cK7QZXLvyT9'
        b'cqV/ta7v2/On1PYTPBbI1ilzyE2njUNwowBMI40xeTm4nrTOjnDW6OmwQA7js3Kyo4RsZPBbHZsdpc6MBuVfirfzSQkxeE8Mm0pYQDv6aJiGiI+M5a1cKj6I65UiZpNZ'
        b'O6DGo5SiLqYqidVmJNdqnWWOjmRlGquZtWIEOUT2eQ1wfh8Y3+i1pgU7xBLbJFCV/rrv+uIdE3PJ5JDN5TW/qjm09ptdA3G/c8o51X6Dg2OfmxM9Uj/nuIMkb5weOrsg'
        b'VTXr2PuLzq/46f0Tv97/9w/ffPvXRW8cCU4Jz8458CSj9Xvr37v2p0NZ835jbhmYYwz/siXp89E1/TL/sX0VevLzmlOS/euGHjtzbvXP5Y57pnET7efThkkKVldcUf/p'
        b'QcHf31CMmpVs3/vB5L9PGTKorfCfL4fU3Tpx9khzmV+n2HIo+2+LbmZP3GtyvPaqrfVl+8+scxSZudff456UP9L815lXrFfOFK3f6Vh/6UfbLp7OPWbMt7T+Qlr+j2m1'
        b'mft+UzeqQ3Hvg2HP//ZHHYaO2lu3v+hf+Dh7yuq7h+9KfhG8MnXB0JSIV8Q3f/WHyeoHe8e3R3687x+D+v1XUvrSczWaL4O/qSp8fd7dse3f3EjqWEG2ltZtLPl1Qutr'
        b'E3//6fN/vGY9faVQGcRsBLgRH01yuX64rRHkBtltJLdJu53ahoLr8E6Nb4OECFGTBL4/jdkkUvH6nMAuewS5hw+6bBIGfJZdFUraybXlGg9nmz5zRfjGFDPelWGnvrbk'
        b'avWKqEjqvdGX7IlGyH8Bj0+TvXbhFt6GXHwrSk2pfjTFpG082Ut2qfBOcpTdBkkeBMg12ZFSWHlL+cVcSv94dn9gGL4MDOVidk40j8T4Cj6u4fCNNeMF15dDeAPeDQzC'
        b'5bMhXcUDM2gfV0t2MHPMWvwAlqTg3TFpdDf/jqCZGuYEQnbhXfgB2xwcjh/52ByETm9jM76CtEfYoEe7hmTkqiJczjahZIcIX8MPg9ks4CPFZJuGGVxm6d0ml7tFvVyY'
        b'pQz5DxlgfJligqnRoUsnZ+aYQiorrGW/vNxpjOkyydCr7ASDDAvx1JVkOKSGc1LmUEKdS8IgTK8rlvHBzN0kgKfhugFepo6uVp0GHLlgRNHTh4E+jPRRTh/09kWryW1Y'
        b'cRs1PGw3fs9yq3GAUKfBXbHeXZPJ3U6Qu4kuK85SeBR7WXHORXpacXoaWpnEKXvRbXHvC88l9X71iO2XcvUBzPYSWC92X3guaZBuRKulddJVEmZrkTJbi2SN1NddfLTy'
        b'EehpwS5YEOzOjmIXxWcs6qONnr64ChWy2NUTJfRS+Oq4qdpoHJUgXIu+PAw323CLbJmI3F2NRMFAtdunMSty6oLkAtxSSFqKcmaT2/nkdlFQcmwsmkZa0bABIrwepJ7t'
        b'guDXEPV8AWkpTIolWxNjxTHkAJIt48gxkAx3CVegNwYNLVBLnJVxSBLJAYO5Fs5ECxB+Gsl1fFOaNB+hCWhCVBRjJtGZGnKSHCZ7yGnAlLEgTx2NZayJI1fwOs20eerY'
        b'xPgkHknXcPjI0gLGZ4Jrkr2uDSdHcQtPDq9BpriJkznbHyDLo+KaGXkPc0Vx8jutmj+endxUOHJH5PU/K7IvybPNc6MWjwk5nPbWm6rhtZv0H4SuQGPPbFs99NCnRS//'
        b'+aNVJZPebizdIOeLTYoO0eYX/zD81pPZr73WOGrcN5Uv5oeTE+tW1BT/fU3gg3Ez/3xXkbFb+WbbpOyk3Ntzf7ZjcMAgv9Gpm/9n4Y9zJ874QXzVHyzaiLOD/vH3mC86'
        b'5+ctrrv6YvPaIcvLrxxuV2f/c2TVl5rvLxv4eUXK3o+G/ev6o71LRGGpp6JaFgXtCz0eu+SNVXUfPbf9kzWn3wt9YW/YrOU//vx337y0/ReB+Qc/ND+f+aufvx79oLwi'
        b'Ze1H/Wfffn2KMoz54MUoV7HL+v1WTkU8PsEVkUt4g0Cgd8NknhKoKb5tRWJKTE2khRFo3SgAjBctBdno3DjcgC8LVHKrghzx5SoHomQrI6e4fqhglz7Yz+rFlgAzHjJD'
        b'Ob4jY5T7hWF4iyY3GmS87TH4grgE70fB+JGoBESoAwIRfZhcQ5rohooEHxiNxMM5fAK608LqX06OkkteV1pHk1bcJvIDYr9VuORx+1K8y+Pe+FULUR96bbxFzzwJQXXZ'
        b'BWwR35rp6RXJof74sngIfoybmVOkCPhLvcbb11GKt6CwJSJ8KR94Inuzxlm8W+FksHtAlPRl9Z8Mkj+bl4sgOz6gnqtu71LprFzUZ7johakRrN9zivFuDwb7PHlIeax5'
        b'MX7AZiW7iBzW4L2Dvaz5FtzGnCfHkKsgZwq33DeLyPoRwiX35QUC794GqsolzRhAAa87NevIdWHGDldOA2EOQb1kWx67rnsHX4XPk53PRnb/t27Pd/nYCHflMw6l7+JQ'
        b'MZT/MDdG5swoptyJ5+FT4FZyIM7Cr5jxLGEjgYYE10eZO931K+XFfDDfnw8AjubpYSM0L3Aqvy4e0eknGKZtnRKbXWe1d4og33dlSxJrFf1e6eY+FjcLYtzHDI/LnPOi'
        b'TMZ91qFfKHpwBRI6+h/wyRIxnyzxV7/vZlEQzlrZXac5nJZZs9NgYjXYHVYLS6tU6Kjh38P+8kxGc8VSQ60N6qm2GmzUx1Ew7DgtVTa3td5p5fFl7H7akG8WzGO0O6W1'
        b'doMPQ5SbmUo9J8zDQ5696yQQN5B6kPn24O2wWDtAyL4OAuKNefgGvo4vzsYNEmBO60Qr40kDY2hLC6pJqwTkv8MIqZGanBUxq4GthlxijBY3zVORPRq1WoTCw5fiRhHI'
        b'szvJIcaiO1fzlHEPnCbRmh/N1ji3czdWZNGSlQpWVvoc2V2KH5JT5EQ8ikySpJIt5JGDysZkA5DzzeTBMg/1LGZsLeONowx4T4EnBybHQMsrwtcZU80C/eCuoLuB4gYa'
        b'w8VUfCCcJWUOHgfMvUhNNkM5HrdwQ4Gu3DCVrPhGbAOChi4Gi3NeHRlMqMN7efqv5yYnnt/7ln9Ak0aalWacUfzr+et/srFmy+/ONJ1Zd33cxHct//xt4LayV26dzP9+'
        b'80ery8Z91IyzXplZtKgw21L9o8KXXr5340U9/sf9998qHlb38FbailvHdJtaf7D2hyeOzGw791FWZcmalefa7j9MSb/90bTFJXMHDh/4xoBRW8eN/qhcKWVUugK0+1Oe'
        b'3n/kyBD3Tilpy2VaBN5Qh7dNcwh3AjsvBMaP8hi7xBf64dYodQ4Poz3HhZGdmtX4NqOJiUvIVuBj1FIzT5Op4lGggQcx5yJ5xFwKSTMqftrTGzQG0loiKA2PcbtAeu+R'
        b'ByIPZrSUUnXKjcoGKaXfQjZ68EbU2Urogut6nYhAKc1iUTiTzsPhk9I9utkaBpTOg3g4i+Z+R0fFZfD43VP06UgProrOJpRcp7haZ6/wfVl6MnJeTk23IenLEqTuC9PF'
        b'PV6Y7qRX74k4H1uQXSSLUg+broZ+M5s9idezH0KjHU9TZBoVkfRbpAIork0wdlOyZFhBj71S22+kus5UHRnNGnLSR6tv07GNXu2ndxusddayClONQa3Io/b15SabwU0D'
        b'WR1sACy7TmGsMgO974WgURC5D/m5CZos10FPH+Jb+CDeGpUBiyM/A2SOLJB2Ludk4/OFGfgyaYhWgyyQQbb4VeP9ZDMzfg3EZy0aWE1ZOWrSCAIarid7C0EJboqZDYKH'
        b'KoLe8KIhd/zwHnKRXGS0qFzTD2Swi+zghsjM4aNkO96QP5+9yCgTb42L8kPLxqMVoEEfAS2B9hN3lOGrUeSYKo9H3BxEDgRUm6YMaJHYqDVy9YfhE1vSg/k4+fQf5vaf'
        b'v+bEW6JqafDk70uQf8S6yBPHJr9fYN6Z0VD5zuuz01PGLBh9//NXv2zZl9D20sz7RX1qfv5a0+iVZ74wlv78m8Ks9pxA1XP8S0vGTX3w01N/VTa+d+lY3PpPztf/7bn+'
        b'qYUrg4c2j1NNXNl3f/XExb+37PzjGvF7N0x3pbXvfZO5kFySffF13r5/ynClbfQvbfp5iV8fEX96eVvfpNXm9669FJC+KOnTpFfeHHDxhfG7P+iv7GNnVsk2bjqba8D3'
        b'FI7cJY34Sq6VSWhZ2pVU2qQCIBWw7ECfmvjVQ8hGRiYs80D6vUluLXe6g/jjs8ZKHp/EFxNZxXOeS2elG6NBC8odks8PJWfwIyZYlgKHaYIEdSZLDSTXSDtp5UkH2YJ3'
        b'CSdr2oL7aaLxtjzhHQGBk0lHOE/2OUYx8qicQI7QCmLy6LmdNRLczkdWknqBep0iW2SUVRhHKtVkOxtYn1hR+WIQxin5LMfX4jzoav4kftQqk2CeuUruhkbFgEB6NyQ6'
        b'U6VW8kD2jorw5lhyTbjG/RHZT04yCTsGNDjphCK8gR+AT8cJbw851W+xxo2g/jARDeE8Po53DhA0hNsV46m64pyQqcvJdX7gCrxDGO4RKVTukoWpIEwOGPF1TbZQ8640'
        b'vJl2jL4CQIrPAZO/x0fjjeRWbzaabyHVHuRZTJeut9sL/fUXrCwydjQH6DJIqYLVJAxi64Lc5JOWzvV6c4DVm0b30kleyNtFt+3w+NdTdHtjf683CXg17DoAPR0eudYZ'
        b'9Cs9Tgy0xPmjlAgfPPz3feqwPXWT11eVlZSwEz6dsmprVbXBaq99ltNF1BOeedIwQwyThxnTYSMQZiP8P24l6xWOVvo+jw+Q04VGJhbz1DCGuPDRvFOt+NYnHyySA7AR'
        b'118t58L5ofmDU4KHsNckkp3maht9TaItOFgEVHQ3ChrGk+N4f7aw5/SQ7PEPxOfslFgE0r2Q/HyygW6BDI0Xj5KY/0+9eKj73qFfLpNy55ItkoIJZD2i73QbCd17LDgm'
        b'bgCd+5FGja/FJkFpvBNfJXe4ZQsUzFLUj5zE7W4TzQh8wvlyN3IPPxJmoYUcnkaaMqOpZJQgBqWziU/DZ7I0KaYR1XESG8U/rfb9T7WLvndtx/HWuM3LuDK/D/gzm+WB'
        b'g9KnRH8Yfib8w83Z2mRNQOD8tuMvn9kYt/n4xuO7M3dxv5k0uu+r39sfjJZMDl14dLBSwgjdUnyBXHOfLySbluNLfIIxlxGUkBHlHhSjEq+n2vNsvJklatPJZg/j9Xqy'
        b'EW/jVVXVrNYB5LpG46U4xyyvqhoikKkTZHsR3V8V0hbzZGOAIY5c7O2wiRyUIpBCDCXU1YDRkf6edGQ0tblSuiGGp3W5e3mIO8W0QKdUOOvl631HtTRqhRvBadmRvKv+'
        b'dc7f9zzFOubpiU8OIVejIrJUGdFZuCUmE6jyXfwwgkMKskcSTu6TS15I1M/5afuz58UXUfTyB8BMXi/a5F8sMojZW98Qfd9bC18sgbCMhf1ZWArhABYOZGE/CMtZOIiF'
        b'ZRAOZuE+LOwP4RAWDmXhAGjND1oL0/elb4zTR8Oq4PT99P2hbbkzbYB+IL3oQq9iaYP1QyAtWK+GVCk74iLWD9UPgzh6PQVXL4YSI/QKeilFW0Ab3yYyitrEbRL6qx9k'
        b'5CGOforcn0Ks8BQLOTye4qe/60ce6gN1BXTV83QZ/XPd4/69p37Uob760Yf44lBDmCFUP2YQOtb3ONrIsdBYV4jlCGdOg8LhHxnMiZ/zKo5+zJ3Qj82TRK/UR0Jcf/0g'
        b'5wUc/iXAVHQzQZZlx7C9TOTeGoDglChl7/OTug3jkl4N48ZvP0UWIBjGf9yPvRd1KjdZG91o0Qr70jWoGQ3kPq4Kytfm3ui7UIgMG7ma+5L/MikwVjfkgi0AOYBAIA70'
        b'Rq+D5l66HlCKJj9UUD56hSykZr5wun7VKDQdfYnkSDv1D+X56CNXD9l5O9Ngxw94G+153ljdsObrQeti5eLf5k7Viu8ce3W4fHKZcsb974mnZxiXmg88WPvki6zBfSpe'
        b'S5ywc4y87njIktSUhLtvNY2/9dqPvx/m95tT1xz5/TPqVnzR//uvfrp/TW78oJu/++TqTe0P5zx/7sigBcE/U/oz2kSOjcG7hTchqURIVogb7bx9tEAN8RkVaAZNQLKP'
        b'DmUbbNJxfKhUwYS3mYUTPHYDY2I5514gvoSvCObgdtI08Gn1l2zXkWN0VsYMklSQvRnC4fLNcpNwbDsqQiVkayJ3V/uhAUPFE0aQLSxTIrkyXOgmbmGm5Wa6r3YQHwoQ'
        b'4eNz8RbhEN8V0gaU150tB19CkGs37iCNInwS5N3HguR5pJgcAM0d5MpM+vZiGejxJ9X01YMdL9jZa9Tu1OH9uGk51FObyHgs1Ie35wH5b8wj29RSNF4jxXvm4sMCaX1m'
        b'2a/rZPZwT5IdL+UCJDJuIDuh7TRmcnVh7lXy1AsMBeNjp4T5EnWKqStqp7xrx8lS1elvslQ77OyeLN+6u8S6hn5fRR9rkUskXO3Vz5hupP9NL8nQR/+e9QCupIR2updD'
        b'qFN456LwbMV9/npo102f3Y6iqqFWDSUqz3gsNqjEc+Z66dJ0V5e+Gu7RfPfD1+pnnYSAEjeUeml2lrvZYZmu7C4PyO/Uarnr7DNFm5JKU28nkLPcjfan4r/CaK2q/G6t'
        b'VXi3plvRS2s57tbCWWvUN/bfaEtaYq+y68y9NJTvbmhQIc3q8qD12dr/3lHmbqIzj7q/t48xhR0WHr3DXg+mlf+sSCLwG81iP7RowTB24uYXqeHIpDvzC85GL7D44dd+'
        b'n8oatK+WZuja9BEfanRy48faj9GfDw4q2PfSIPoCWKS9LXny/dNKzk7t1UBwH4QKtMxJyS4t8kXMyKYFvQidTP9ihIu9bMxFuOZSKbMu1JMQ/LvHnAu6UZurXvbD7o08'
        b'+Rf8/Ic0nYpv13Sc4Hq5VsIOT0xOjq6ZOvfxKDYhD/qjMrRwLkVP7r1Y08CjF0Q2elXci79pFN7ou0M//3v7ZubhffjWjvOiV+/qhLcgitCSDun69lAlb6cCBbmDryzw'
        b'gpU3oIaTywKsduJ7zlfh4QZ8i1wnR6l9JlKlptrHBj6B3CHnelMh+pQw519TnaGk1FxVtrTrDXUuyC6qG+Qx4d65vV6eKmFeq760iW3Iy9TQAo/53YB8wQvIPbfpXpYu'
        b'OLOX0DpfpioCSIv+HZ2WQ753ehikjWP+xn1WsFOM8rUjFi6sEFwsp62qwBfFdGOX3K1DdXhPIvOboF6L+By+COOzk80r0Upyhmxmnp+Z+D5olU1erp/4dlxmYUSuikOJ'
        b'uFEaXIoPMDfJnRIQRxOlPHXA7aNLQczdb+7kvLk/FTcEIebu9+eYIOFwY9gs6hcr3E/kdPrDW8ldwfHPiTBedxMdJ/sDyIEMOaN/TDknewaLXcp1ZY1Tvc7Cl0JNExMW'
        b'czYKvg0bx475iSqYjwsXv1t79flrwbP+Fvby9xXtHL95pb9/0dtX5r+edMm049Cxh0rVp2P3/0/8X1Le2/rD8inTU5uTZ7+UNTW3vmD6lurjsdMbrK/06dv4wpOcxrDH'
        b'87NL7h5MPTHo+btn6j5968en9H8vsf1Sssl4Y+fq46qmuI8/rfqD/c4b/dKmvbfh9f8aee/4ym/QKxdGfb1rltKPmRwn4bP4HlWouwyOaQXM5HiTmTsL8Ib5gU8dnbsT'
        b'Q6XTVWQrW2cLSQeu72WdjSe38Fm20LYVCHs568muisBIpxzrrncEvinGzeQWuRqpYYJjDkc2MR8IKsUCtPElUIjzyCmyw1m5FMXiC9Kha5YLDhenKoIFVzD8OMS1YR+I'
        b'dwpb7vvJFXLRaTggp6a6Nt1TJna9q7ZHG6O0ZLnV5HwJqZeoWUIpNs8NB1FzsNOjS87VhXisO1bQ+/3IOmu5rQcyzlt3eC/z7fBY1G2Zn/F6O2W35nLLxM4V6bX36nxj'
        b'LjuX5n5jrphtAElggYvZApewBS5eI+mJlEu6LXBpLtt4qKzGHZi6K49ApHXwiNQUpo2ybc70ooVRs1X4GLk6V0VdGf1C+eF9a03/XTBWZIuDdPX6NdTqtAO/9eI7L17b'
        b'0d7avrF9fvRm5b6Rm9s3nv9tyMbxLZnNI/etTxiGLg2TLRLdBW7MTCW7q8ljUD2oGzluDMA38wR/Cw4NqRDjhrXkhmvme7chS0vYIQUG3xBP+JqDmZ+D1xSzrC5Npcu3'
        b'jb3emJl8uhFvsRD/VF4G353wMHWD7/6wnuDLGvcNXmo5rpcAgKXMVkCB7PeMQH4GHV+SK4CTLjQDuZJWwOMDKoDmHg6JyAMuB2/FbSbHpfMSGzU1zwr/6NMsrVaje/nD'
        b'iPczBaFK+6nWZIzc86n2iXap8TP9p1p+a2xyguPG6VjHtZprp+Ma44S3YtvnyL9cUdslcD6Ty4fXy6ypYc4DouGeELXKBJ8W6j/Zz2Niu8o8G2h9H23tBdK74FHVDdKt'
        b'Az0h7btDT/RQwDfME4UlLXEuasl/blG74E1Zm5Jc0heoyKElc8nuhAwRkvhx1BRNHplmzjmHbPTswoEh5k+1+8sz3QDP0H2iVes+1n4GQP9MG6KrMGaXhZWBlPYqQuc4'
        b'v68+7gdrmIoAmkxyn7ki84u5F9JTHGTrs7/xtjO4xHnTpwe4vUTqOgruuoEe8+pVwDesO6VGXZm9ytoDkRZbd/cE5DZ4LO8G5KZwTyD32BllH8GHtsullgK+M6hLo15q'
        b'qO0MqqlylFUYrKxInHcwvjOwjN6sYqAvL43zDMR3yvQmm3AlCvXMpW9st9PrcA0Ou24Fu8KV7hN1yg0ryip09IJRiFLK2HaUlUpI1jT68HHxLt2YWsBqpM5EcZ0BrqtP'
        b'THqPw+LFLIfdZDcbOmX05Rc0c2cg/eY6hM2i2Z1KrKZ46yFaxo+eCyytWsFOindKqiuqLIZOkVG3olNiqNSZzJ1iE5TrFJWaypR8p9+UadPyinILO8XT8ubMsF6iTV9G'
        b'HuYLCkAKVSr52OiQnFfzSpnzMFcvM8r+HR1H5KzSew2VCZLvsQGruC95rd0/VrfwJ3EqxDbko+r62cidPta1MgniyRkuMmmGg4pbuXgX2WGz10AauR3IIXKQnPYjB/hg'
        b'XA8icDqiW7Xk8pIo6rN4OSIjR423k1uZObNJQy6+HE22x2TNzojOigEZFsQrepqHbmOR1oXyaSPILkG4PoePpJDW2fBtH96I6lDOCHyWpeCT5E4e2Y/bExJjxYgbh3Dr'
        b'4nFMTh9Azs9O4EGjItdQAkrA2wcKBfba8A58dzLk5xEXgXBbKbkmuC2fxNuy3UchOFSCtwQW8yCCncWnmAsDyIjn8N3+5BqUlSJOCbycRjH+QlqXzSBNIzGV+nKS6BvH'
        b'r3OklQ9is1kWF4kK0b0RASFa/sW6EYIe4R+qU7OqQGOMRHjPCI1DOEHQPEqjVqnp2bccFdmaDfN5kdwZgE+JJ5PzalZfpU2BJqNzGXy1dlF7YZogsJDmGWRHFb4BNYoQ'
        b'F43wPnIN72YHilKWBkXRmz8yhU2mILyuD24RlZJDTi+z6xkDUDSqmMgptKtahpUK/cs3DiwMg8r8EKdCeD/e+QKbhNn4HNkOAmk0Pj8LtBVxNAfqzZ3xAtaMm4RWoQoj'
        b'itVad41ZK/QLbyxfgi+qEhLxNVC31PQoUSM+KegfjbgN38MX11DnpxxQhvzjeFCQ7wijPBCRhdrQu5NQiHZJsXKcUFvJ6BgY2HVaG4A7BuGD5Cq+zUCwRrUgaj5pYU5e'
        b'bN9+Cz8KnyW3WWUxidTX/V1/6WStGacXITaWlfg62Y534X0JicmIzdluUOIOM2wIyVZp6A0pTWQb8zJGUrIhGG8STcK3RazGv4aPR9VoxWCRVhs/MVUseM/ju+TojJkr'
        b'oD6ejXUv1NcmHP66FEMahRoDSEduF5oNxm1ikETqyVHm5y4mzfjxClIPVUjZAPctj2VAtJfiJqF8rgBG0mgKrhal4tOjWH/yh4Wh0Wjy6mCkHXqVcwhLdlA82TF6UUI8'
        b'xVcY3p5F5AwbXQ45QtbB2FrJaYawPCDsDY60wey3soHwoLJsw1cXJySBhs3FQ1F8NUhYBQ/wroVR5IxdQ53pOCQ18YNqyElhnd7OzdDgloQUWigV+g7gOSDcFdNC9lqd'
        b'SLgVX6VX4qyRTxCFDCPHBSxpJg3PG/AZKAozlwZYQk7gxwyuAfiKSCPMlhJfEKPaBHmIqB9KYqP+S5kMhaC3lsi02ug9S7MFKJCDc8l9fLx/QgqQfFrZfnyLE7ajD/uv'
        b'ioL1D63RI38aAGsZP6QUZoWWW0p24dOz/aEY4FY6xdRDQGboPNbN6E/O4zaNhm4o8FXc5JAxLH4+eShbOxkKQKcnADKuJG2snWXkOtmoKaMbFTkAsmaYpr68P9mXzjod'
        b'6FeH/ooGrgB6UPMko1iQWHAbeYgvweraim/GArZyUxE+Si7hvSw1Gl+OAUWBwn87viECAfYRhw/Gki2swg2rZqJm9CcFr9BmDQwQOQnChtVxweQBrQ0IwjSEj+FN5CYb'
        b'aIw1GZ8nezVAXkCIeYGLIR1kN6vpE9sgFItkA6Ra7ariynnORSclxzSgKgeQ6xIkFlPnrb3kluCktQHvXkRaJSgLb6XerfjEfAfVgxcNrGbHCMge8nhOBmi+qrmCfxhp'
        b'yIkGOgTydpjfENIO88tuzjmfAhr3VXzEffCTbsrs42FB7kddNzV39KHnWM7NCUJa+S9HDhVwHB9MI9tIqxQl4XYgY9HkboCDbkAtw+0LNF27T/j+KLYBBTxHjMbgCxIH'
        b'2eIk3iPJQbyNNIXgbbPpmRWgamHcYpcrbALo5oeLV2kKSQtgBdmPyDVyM4Vte5ML4/At9xFmGz7iXtRj8iQmAP5OtqSHifEecjAQLcXrEH4Ef1GwyKhEMm32iiiYkxyy'
        b'LUOVRY5oBU0wTozGFkri8X5yjg16kGQISkTvLpCHaBc90s9CrM6xc/FectAPBRKo8DG9rfpejrAVv7EGd3jUetbsrJVHY4skCcXkKisPXDOGHNBqZgOr5ejR2IfieWw2'
        b'ZxSrCoA1tzxfAUx+JTeU7MlnBRIrslNsmiJhEk4jcisKbxEI2znSMRQ6c+qpQ+IcGoGbxOROJhZmoYYCmxwMQiuLEO6AP3xYLNz/dHBOOV3farKtNDMXSmaq4sVoCD4g'
        b'NuPT0F2Gy4fIyThyUISKyT2EH8IfbgDyQFEnjhwgB1j5SpurOA/FD4or7RWsZUD1dpBAmmBwMFITMs0hV1jRyeRBNXVjdPcYqFRrn76iJUC4rghFd5GGidRCAGxqHxoB'
        b'Q2rrJ0zzLnKvgtEz8kjD9ixjhIPhQ/FtMaVwc4UD0ZOAeR8EWr2OAJAewF9ZsXDKqW08Pk6aeJQ2GS1FS+XQI2rymYsfaTQqVSa+FJEVnbkI35egvpNFpG3lBIG9HC4I'
        b'IgflQPprEL4Ff+QeXi/Q14fk7nDPo5ew2s/ToyGpAuEjF2B17cXwtAUFAbGCFUguk5Okg6FYyYQAFI7yCwHFov+aNkRYV0Dw6leTJhFKhKFXoSqYeuZ6VErW2ckRKchy'
        b'GfS8eLMmT5VFHeUUQ8TkWii5xIyWjxeO5l6DdatYbhkaaT4ad0UQKrRjgPlfFEPbFpDi6lR4venS9yaJbP8AYdd4asziN35k6TslRPruJ0e+vyzs7b59m+sPX/vv9PWj'
        b'B/K63/r/wxg8Zoc5fMGe7R8E9p9zdMf3+2Y/5vuQUX8a+nXBH5tnDo1+8Oj8FeW8vf7pL124+I+iXz5seDgyqM1/TqXpVPZbn4dtPZ85bfe5NUvfvfmzKYNHv3JBemTt'
        b'PP/rf/zk+if/StYNfr/g/R2auT++qjyZ873fD9yfeyb0Zy+9dPOXrfc2pOQs+0XklfGN0z9UOMYtnP7hyIWHE6ffmXIgt3TnH3YMy63Z+tmGz2puzNJXHf/zpJ2Sl9eM'
        b'85sePDU5/eOdE0Zb7732XujOk5vTfjh927Tc1PFK64X8j269vH/DoX7j/cb/9+82vDzj5THjmp7bO3LepfKP+rX84gcjPtBt1cTtfyPi4Ncl036wN5Psu/fNtB+27an9'
        b'9YWd32Tuv/ra70zlg1PS3vziB/fzNi544UeWkDlT3rEnhTr8P8fGd65878KO0xNOdn4RevX3g4o2trx38dcT+9xcGdy+W/rllTEHrmberuqY8MuHQY+OVJin/u3o3Msb'
        b'tv/PFvujA4crFTf/3rRwVYG5svRc389V421DbPdGtTZ+eeXlh41/+mdmzJOhz7+c3Doia/OszQHbx/wrc82vQp/vV7tH03K06dLbP7oz8+up7+/9nw9nfP3J48pzny/d'
        b'mfI/+++GPf7g73P/4rf3L7M/65t7+/VPP7oaemP31JJJjk8aXxid84e0N9N2P/5aFNnnn5V/kin7Ci4DDaNxs+fN7FtDPBwpqMvAPHLYTnEzCe+NRvYoakDn8QEup5hc'
        b'Zz6wFQFUrKFqRd9FUiSezsG6aHiOnV+OxJczcVOfanlAkhV4TUufmiB/KQrHR0VVFnyc2Y2XJCwPxOejMwTrLr5C1vEolNwX4ctJ5BAzyfbPBVLudAKrovSIHaHCp6EC'
        b'ugonkE0ZIFucwk0xTu9RGTnJ46Zx+Bwz94aR41FaWIhNbqOfLIfXzx5tZ7RmK7kc3A9vg/UEo6rhpiTiQ4Kz6k18BF+J6kcOeJ6OVqWp2JDxMRDqGK/VVvLCiT013iL4'
        b'b1yLhrJNlrH4qtt9A19Ts42jONKR6W0jn0MOMg+OcWvZGbjZ+CJ54O1xAd3YzLwuRPj4sAGC70bbcHzDy+ECXw5nPhci0Kdu97XTHRB8ZzC5TT086PWIDzKYWkNdjZ1z'
        b'EDVegu9MLWP1PYdPLhGso/hBVARu9LaOmnUMCn3J3UUe5yVAv2HHJfDBZQwKC8gxfwdITl7+HTwIP4dqfd1M/539PjtFOr1gt6Gup267zVqkpo66Yi6Mud4FMAfeMNcv'
        b'H8Z1+4W4wX4h3Gh6TJobCCXov5yT8YM5BRfMSoRwwSxnCMsdwoXT2vm6oC6DDPTFyxeYGtq+6+EzXijVZcO/Ao8L1ChEsdZtFFqH3hrs5Rns1Qvf++bM3Ce8jwnVS9zm'
        b'Po6ZKp5x95xWrEBPmyrGCaaKT1axI1LV96Ta7IuF0wRpkVn3X8A3anGrZEIcQsPR8GH4GrvPJGEoiF9oynIQrNCgWWQd40s20pacIMY3SCtC8Sge3y9ndR+V+NOt3vlm'
        b'i1buF25DbJNu6SqqcqCMep02u9GeJkimK5OowQQhdbxuyGRRhJOD3l49KSFRTBqXULs/KsN3Elhrhln4cEKiFB8QUXsEMhRPY3U85qT0Zr7JX6i18o/NnFDx6cEhdOyp'
        b'M5dro9/KHyp0Yc/gUBoZ62fTmi2jSoSc75rlCMAV++PZ2uyUBXYh5+fSIBq5Yslsrbk9NkjIOaqUsnu0IqGf1nxpdpqQ8/4UFjk5cZg2+9OyZCGyKtqPdmn+jHHa6DP9'
        b'DEhwym0lhwKZkFgEsvS8SCSpoUaA0/iBoFWTnXh/Akik52KpSWY0vVd1I7nMWibcc2g6jOaffbSlcaFJgiyLz+AjoMVfFOPbQIXpnuqFOuGWme2zQ8jBgCVSSkLgr2IA'
        b'k4KMeD3QwYNSKLebqtzwl7KYFYiATKSVw0eyEVIhFbkgTGxKIDvonn9mmja7MKyfMIqZOhAqW8lu+gva1kigD1sQvj0Bn2fIM6u/EbdylWQXyO9oGD4bIIhRG9aO6HJH'
        b'nu/cMR2Ij7COhaXhqwX4JDnNdow4spMLmzCGId1zI8jDKL/hBBTfFWjFCBVDj2yo5Qi+iMiWWQjVotpivJllHlICc3mRtyTDXKKV8+ewDVsGjk2lzF1x8ofTtPLvj5YL'
        b'huNff/lGGVoyiLkeaIaYNBN4iS0Rlsy7S1ZW7kynV6hsKX9xRs0HHYfq/2KNfS/Ib/LPXxup3hH19ZzRZ68vmmYY2f5qaM3Kl7iI0LMNqdz7Ic2/yr0W8pOffv3bP3bU'
        b'WH/q+MG7t7NE58b8Pm3sqMGvRFQkvuv/+jKyoqJ4ZuBfL514v6jvH27n/vfrmcNf+8nulb/YcFT55paqXz/5X+1dCVxTx7o/WQhhj4gVUWvcQXZQFJcKFFB2FXHDFgIE'
        b'iIbFhOBKVURUZHHBpcUFxRXEBVpRsXo7c9vX1tbe3t7b2rTa2u3a1fq89qrd3nwzJyGBJMXevt97v997RiY558yZM2fOnG++b+b7f//a6Hsjmi/X/XXJ3GsR105n1Qyb'
        b'+0qU6ECT173BOxZ6/nr8YcDTb/0z+MyeVRHfPphzMfLlqYt/cnrns/SS9z+Xrf161lcOQ9/Y81z44U8/njv8Q+W14hU1Dyq3Dxz0pyc/e/jOnenP1BbP++cPU7FwmnSu'
        b'05Xc6uwrc84kKkZlXjmct+n4nM+TrnmM1lytqGzr7/6wPPX4z1Xt5fP7zeo35eXlU9wCEoPXfvjE+Snlt+NXnm/v82z4yQ9Lo6//dbj/8faHgq/Grcu7/IqPJ+WIeaYY'
        b'HbW6Opy81OAws7EPHW/ScD2gpnE10UfGCMgweZgMOC8I0U5uIh1qA9E5wNsbXcdJ962masMufJEO4c6DKEKRumDiRn9OOltYMieRLhfi/XgDPgpjZxJYmWT8rHfBNYkC'
        b'zj1SRBSUC7iSRZ49SXT5StQCkVvjKYB8E9ESnhEOwydwC43zkhuP9vT0xiR6FTqRTFUrP8SQ9UFoDTF2SG18YZahBR/AJwWocXQUHXlXo3ry1hB95oipswk6hA6ygDNN'
        b'pMhjXWRCMH3pitZyj80TD0SnGbYet+HmkaAB8bh5X7SBziO5jxShE7gTX6K1CE4lEmEzOrncRHUhzbyZKR1NqHWeiWqyc57RH5RoJrpsFk9mJy63N9ESpsxnoMpRRFWE'
        b'Qkb2x/VdZaAWucFZFBxFz+Jm2q5DUac90SOm+wUE4LpJqwPjST3xcRHejtaiE4w9ydG7u++qPXksF6nz6vw05uO/w11CM9Um2HFiATosJCIK78qk2p0YV6BKIzogdxlb'
        b'41+F11F/AtwpDbLgT8D7EiTFM28CtIVkh+czuBC3G5VPojPy+mckqqLBCBIzwauV6mGghGlwSw89DO9AO5hn0YVw0OwMOhRaG25Qo45nMpTUKWKF72bxfPyItUhMShrQ'
        b'xzPTsIjcq/UwMbjeUW0q01yb0jgLxEIDeN+D6lIe5PMY+XiSD2y7UiC/B83hzv/BxxCWxlnoKJALYenUWSil4KoVrl06C1zYip+aDQSVqdsaEefcdxbUpHqz1bNulyQl'
        b'iFhB1fQrmf7XbIeN/t3ZScENV1MKCXXNpT674K6rlxqcOA2/YHmJuj8ypBQ4W1FXDLpeT5dy6VKf3jljRuSsyKSM2fNnxKTqRVpliV4MWHu9E38gNWZ2KlUA6e2xBvr3'
        b'ozdogAzND9oK7kEqkvXpFTzKzlXs6uIq8ZDK7A1xGiT08UrMPo4i9tjZlrDbUcNHZucq8BB5RtNg80NxI8i5pVp01ijn7TjZbNEC1IwOmy01GwhQaGQyM6JWcb0bJTJ1'
        b'M3znCI2/RDX2OSOI4gsYCLdccY59jtRI2+qQ40iRK848basL3Xal20Db6ka3ZXRbSmldHSmtqzNP29qXbnvQbUdK6+pIaV2dedrW/nTbk24714tzOahVzoA9wnoJYFMW'
        b'ueR4DeAaXQHFwW8PNGz3J3+7hLWCnJE8+tqeBihy2uC2QZbrQMlfKSUrOeZACVbFFPUiXSCD1sgZWiPYwBR+5w0uRN0fljOckq/2yRlEVyBH8eSrCckxD3eaAZZnG1hB'
        b'ySHGvCr3BnYNoEtSFOZAL1d1J2802xgzG3DTPD8S+VWUpS1SA6UzwL0hPC6joYTwvMriEhYhmmK/u0UtNuV47cbW6mOvd+BJv4Axh/9JF4alLI4ncOfk5JbqRYsLyb4C'
        b'ZY5KV0D2SYvJ/Swt0uRouthge9CwmgeHMoTjdiCmkyO/3utkDA7VCyLWm3d6TcQKTf67iVh/m4e1B+eqRQD87+RhNXkIxnpAQG8btSCHrdWhUK5QF+cr/C1VJVyenU8u'
        b'mU3DZtumhbXNCmuBAfYRWuQ3WWFJ/2MRhqNj58jViixgJSc/TYM2+wR0C4fM+M0s1sK86rRtvUNMmsJC5fmKkHfgNzhprfHPWo6QYI2Ttpf8sxYL7eKk/Tf4Zw3vOWt2'
        b'tiVX5fAPLPS3HphBOPBhpfktuUaZp9KSFiaiikg02p385Dr+sekKIbzzI9O8urFZk1+z+nDy6e8JueJMdfzYXI65aVSVoErLPK9Gfd6EinUQ2s3h9RHOMlyeQQu9PsqD'
        b'806MgCivC8tjEzgarZeo9OfxOtulUmIU07Ck+5fFFjsTo+gMbqMlt8x14TxzvhYAfez9UgWnm0x2qp+caJ09lto4C9ABM+5YMuBvdEIHBuILtNToEHvOOeKSHSfPVF/W'
        b'KDkdiHhHO4gMYKHYON9UKAptRQ2G4tbgOge0A2/Kp8XVuDlwsmitHZeZqRZ5zODb9FzKPEvF4Y0Gg65mgU/3Sp51Qk1zPGmhZ8c4ch4Ls+05WaZzUaKCL3RHX9RoqVRv'
        b'ZqkE4uNT4s3KvIBanPBGT9SqGvfqPzktaJ5J4yL93+h0EUY6x8xc+cvT3uuibimc5Ge2lL4m6xckDhB5NXos+qRm3AHdd+3+O6snLg07v6Xf9sG7/tP/eorbu3958FqY'
        b'37mb70on4W0fXNtwvu5G9NgBNQd9bvx56UPZ5M68Zesvf/zmFFy1uvlu6j33XY6vB75+7OHLV8Kmjlt64h7360t1uENx8PltC3+12zRBcdvDx5GaW4H42DDeesT7lvAG'
        b'JLUeiRHELMwjaGs8m7fGp3CnGTUKai1jLrYVhW58KWq0y9jB7LgheLcYn8pCdYxwVk1aZXPKeHy0q8MY7NBncDmbQX9+8li8K8SEcVYYik8q6bEMdDnFaCcfJvY32Mlc'
        b'LJuyfw43Te8y+dDhudTkOzCfmp4a9Dw6DkejJxk7gcGkRw34OLvTzauATzYQ73bjH6rR+MQVeGtJILxbbQ6kKDpR4Y/b8VktTFSQ63SAWZtIVVp/CZeEKuzRXnzA+w/T'
        b'5Y0gRtCOTEy21VwUJZUVSLoIZhnZLI0KatwycLgStcMK3ex5SC5A0gnJRUhehOQSJJc57rcdW6W9KcTF7J58iLzUgm1rYsut4d43C7PWs+a9h/sZFSYbELU0UgcGfOy6'
        b'kgnvLOyyyTvbO+xjhYES1ER7slGpeYZKPXy8Ww2oNvDoxLMOGQY9ycZV041XHcKu+vv5bnmeXXEG0Y1sXPFp4xUHsiuaaFCPfpPiDKIA2biawng17y4lSdEdWvpojLrG'
        b'9jWoJDaun2O8vhfMUJjoLb/riga9xcYV88yuSNrXqOuY9mEhQyTTyQ6jP2xytoivCLiTw9tKHWLBdZ+uLUFQBiFvrDrSSLrOuc5G53I7q87lBtYiO/desxYpgZuxt6RF'
        b'NPOjcBaZchT1KBI4i4yg4TF+8jGm2GWyTcHQJJMp4wrVXVk1gMii9/ad8UIT5alFBWAlMOMa4prxAGRFVpGuhKcC0hJ91FrbwD+g3VBCk+SocikpSwmvb5vfFN/eNGAj'
        b'abY8PmqbBVUX/sUZSYQUtky34DATg0XubWAqsW66mLYrU8t7vJhy78gsjTI7vxBIUng7jsZus1jRrn6g1aryCmlXYFQkPfiwtHKV6V2piEmTZ4XvxGCqBNOHHBZutFjg'
        b'SsE+fjAdYqDPhRxG/txsa0YW7ZUqej7QMkHbTQjvPa1TrvkNwV2rlNo/jpTJG0iIKH2Sj3zMmAIwo8ntLB8z5nfTNMm9KSWTP2M2epSibVAy9er8RyVIklshdrJGkBTQ'
        b'u2qYoTNs0iR5G2mSgn3k6cEh1mmOTBEe/GPUKdntqAppRSmjeXRS0vz5cGeWArjCv2LF8gIa/lWpgYHJj3KgGa1fkwqF2K6QTe4m87kQ9rYEGt4Ui9Viao8p4xO5fGiQ'
        b'dfIuUzyMYWbI5DUhe8kbWahVsUoV5VrmwspZRHoGbQ84gcbAVSyD372kAYJ/kWaFaOmkmCo7v0RFuZ60XUxkPd9Zq2X6y4OBSFmpI8LVWADpwSo530REQhWQNy4mzX+2'
        b'oiRLCRONlpmp/OWku7BAnWpdwWJlvuX295eHdstGr6bQ5a7QlSjJyAHxj+VzijRaWikrZYydKI/U5eYrs3Tw6pETInUlRTC+LbZywriJ8rjCHFWpinRmtZqcwPjStN3u'
        b'3MrZYZaq/OgNNN5SMSqTahU8WrUmWCrv0dolnDZkV9P/Rstb3Dmb9WSYEexW70fuiaa3n6shd+MNbWuskyJrhS7Px3r3Mz1dPn6k9Q5oljE43FpO0s0KA3tSUbKD47oX'
        b'E2atmDBbxZBOYbw/G2VMMM1m9dbCzQqzcF9WBzQer0ckHP+L6gNEJyWy1SDKvVPZGGt1wO6CAwIROhkK2RbRcbwTyKaykPyRbi6HMWiCDS51I5DQvJiQbsWE2CyGYg7N'
        b'+Pq8KUlfNIw346yeZsQoslNj0qikhh1yb/KS812cPHbrzaDTAG8hkMHzv/zkJrpdTNosufdcfChfQ15SUpex1qtiAo/sKsy4m6+UoSjtYp1G27NSttQ9a+olVSV7r/kZ'
        b'VbRIs8n93ukwFMg5UZ4MX/L0kKCnen9aCDsthJ5m/WkYEKK8Cslvg7Fsqx9Q+Cg5Bb5Ixp75rEux6UqNpjAwVqPQkUQdEBirItqddalFs1uXVVCOdfkEF7AuoGxdmUil'
        b'mHyihBHZb1000boRnS3HcjWsNR7RYpXKEtAs4JsoWGE29busomUT5bBiTPSnXNBayQ7S5tYfKpwE6F12lkIthw2bZ2SrSuCFJKlNdY+BliEn+0EL9gM93T80OCyM9DTr'
        b'dQK0MKkQfNnskbkKcrexRKjYykTxxuQJwZc8Pcx6Rl7MGShJbfRoAxJ6ojyK/GKacHrIeJv5ja82PcV88c5mexvw1fyZ7PlYF9aAqyYqWlRkMnk81iViliqbFBj3JLm0'
        b'hTfSDCHdM2g6T6n0TbSIE0+fZsdxmX5Nk6ZxDMa2DR3DFeYYNrwdNwrRjtVTGPQvUMxJi8/YAxHibPdChkNFW4f5Ar4OwHX4IK4XoP3oKN5LT3hjVn/OL3G/mJNnDrqY'
        b'PZLBaHJXoVMAuuPwSVQZwAWMkzMQULUd2m+CYAb48toYfBJ3jqdlFRasEtwPyeC4IMXKjblDOBr9fRk6j6p9SX7g40sBl0B0Ij5ppqsEGCpnc/gM2jyLWzbWIQ/V4hco'
        b'tmdEDPAPctz3pYq+H3jetm9ly3H40Dx0pFtEIrZwRsqZzhYj5gRkmS7z1aBnnX3QBXRE9e6e22LtTVLKLPX+9bVJ8aKZsoqWh29efLBpcdwPJ8unveqAfD50jP3Xm/IB'
        b'np+FN7xa7WR/oN1hX4T79+pPgle9Fb6m4cjx5l8uVKc8vbyxKu5rvPfO8uPfRdwd9Vxr5r0RN1/Zs2PnW1VRd5fOvym+l5esif7r+N3XB08rmbvgp7ejDo1bEPvcpNeW'
        b'//D6DdW4OzWi6p3jCj+LaCmdn14xxPevYTO/noPm7v962Mh/JaxLS3qj7EhRcHDxOv8LusobHbr7o2KHPh2gDp5+4dqRnTNX7lg5uXGzdnX4Ry9XxvTtfPy16HP7HIY4'
        b'f/3rgKr02XWX75yf9t37V32kdIXIrS+6zAIG4514mwHTgTctYlE51+PKxw2sdgmoDu0SoLaSMuZNeB7XoVZfvCklDp3wRCfEnEQtHBabSFEu6AW0pozHdUTFmK2OVaHm'
        b'Enjg+HRfZfc1oxRVYM8VI9SOm1jwo8Zh+BwLfnRkUo/4R/gUecz04pIg3KSFx2tGfZceAOR3HX1o6IxVodKExDhBopwTzhKMwSfQsZ6QDOc/KDw3+LDRVSqILm62SrWa'
        b'S5FSBjuxwFUwgkZBgt/gJOjIr1AJqYuhF/l+TOAuWOFsXItR5OQkm8Xg6JqrBm9sk2Uph0equI/YpJCuiJzGO1lkcW1q9zDTtSmzWlrGY9CISuBWxG0QGyMq/RYFUMX/'
        b'PQogeCQ9+fRGMuE/eQWR4h4ZdhCn7dW4MCbF/VFFnFY3c1z6qiBAyZL3QlCGGkqpw9cK19FPck7k19zkudzciKkM1LomHVWmjstcHsRQtZ0cft4ukV5AZEcktWsHSOpJ'
        b'X3gqGJykANeibXMeCx0rYbARP/QsxU+MR7tScCvuDB0rZjiTvqiDllIplnDOyz4RkLHD70p4PAN/3JXJOPnCYAl4fvw0pZABC7yGkp2yKI7sTPy72oOPgzzNmfOUvQJO'
        b'F+oJEnuW8+8uZOe8L4Ww033AFJbz20WOnMegCwJwUogpC2c5Z7mTnfOIDJBlqp99ZijbeT+eVGlCBVRJvdhBwSPVL0xHzakzyEBwccYMjhNEc2htoILFBbg0A68LDZrh'
        b'GwQhBfAhCMS2zpOddQbtXJI6gwMI4BF8LpMcQh3zKKDbHrUPpACV8QsBosIAKrgznEUHqJrweCiDpqzELwKS9yA6yIAoR/F6dAnWt/DxNIhifwS10pafiraj2lBo3Ra0'
        b'JYQLicDn6X5HMrbW4u0CODDAn/SA9YsYuRJqFgO2JFnFo0sotMQRVdKKl+H1w1Nn4A68QQ4AoPZ+EnRgtoCCUtxDSXUoviRrhTHgfTyuRxcZCAQaO3UZgJIiwM3Eeb4u'
        b'mrXr98FSTraq0Z7s9MOjR/DRKNYP8U2FFuXwOnQOb+cU6BLz1Gkn9+s9IUxMOvDkY8Mn8mpIbSiqSp0RTC7X6MNxE8uc8AFX3MKeQ9sQvEfrUjg6lDScEEArL+J1S1W3'
        b'vhwu1E4g9z+34euCrTxf77ul7v+YGrxk+n0njz3l26p2Ch0cHA6Mnl/xioPLyxfatiz8Qto5vkpm3/iFdPYb+pcObvSb/8xHJ//x5sXlR6rdX1+Gi/61fsE2RcJ7z9/c'
        b'0JDY71Da1VO7WuZd8s77vj4kxbfpRL73ty+XxDxXY//W/e/7TNDdPfj3kIhPY1qHvJ24/y9j5n0VJvvi9bF9FhxdMCr6g5CJjUvHDR9aMPSpoS8OvrNwx571P6x3/eXt'
        b'5LjDrpX9Wn8+63l4iOd7D51mPvRvXrxiwumFd4dED0wue/vnr8Tb2/5D8FBZdzX4WG6dQ98/735dO2+ZJs/bR3btwXfDdysqlod0qGMntKmfVfX7qE9tzakY5YmRH9w7'
        b'eiXhl8FXRoz+pHRBUnn7lPfPXR3m9/rVx9CnYz6//uNk1c/LVe/Xqj+PCovq8Bh1+W+aUmVKm48HjUeIatLteozJhhF5frjJmLw3jqfjc0HlEFDS53G8I4kcluJOIdqa'
        b'jhgOFm2T4P2+8agJb0pKFHDioQK0V7qY4SK2zkQdNObgGnSpiyUQQp9QxcSlEHzAcFUO2mIkR0FnklADw6O0ZKG2BAthzuUx6gw7B1eipUDPmzMvG21OQR1C5h0DnjFp'
        b'WuYZsyd4JoQqjcLbTKKVPks0DQAdZIXhRhP4SEu+0QFIMpwqPyGoSoda4iOmmYJcgvBR6leDqtMpfthIybi5qMulB+1OYupTDblfolrhRk+mXRHNCl3GW6jTDW5HB9Ex'
        b'0MVxZ1lXoHFXtE4Uhc4WMxWrHa3D+wBZgvfiWgMGlWJL+uFaxolT6Y53QSllo4xhyF3LRNH5aA+D62zySjbCSpY+bgIrWYfWMnBFK5EfHeAj5L+U+RCBAxFqRU3sAvtR'
        b'Bd7HUCNEbK4zEjL6P8MQMluf6mcCGgonw0OXh1EFKmfR0hvn4RdNwTpGLynNaDJ6oXp0wGrMONua1xKD5lXYU/MqBk2LZx8TyoTM01/GQ2UB3CEjmhfoXTKiiXVxMsr4'
        b'P+bnD+wWEqGYB33IeI9/8DjiacaoDmSbyczyrfXgNAO1a1B3tWsNt8883mH3i5JygGjnD6Y2q/h/arMeipplajP7ZB0A+Xz8JjJeM7SjiFKbWaI1I3rDeh0TLltnpqC1'
        b'Zjxl5WPRYQoIxdXo/Exfe/LWDAQMZ34aHWKDR6Id+Hl8yNdAUoaO4bOqjSvT7bSnyeGUL4YATRkKkkXnvecqe+Zm1MGPuY3btolmLBFExHs3amPWejROV4yvyPLN9/m2'
        b'IWu0+/X0b98YOLP/MvfBty7V/3nP/bPun6dNcys4dmB03BftnP3bl/p//GPlpx07r42L/4v3tHsIuQnPTngr5ZtrPglPdKjTMqPS6jf+K2hNsb++dWbnj7Xpn0ZXrLg7'
        b'/sSkdcUNezaeHXTtVuXU0KOtP7yTX1PjLpn0zZLoe0mrIn55KBBeI5le9XGj4hs/J5pVGtrFUoZOqtFORlF7mrRNPWMpK8C7GFEZsJShZnyGnjs1iz8OtFtTciTJwkER'
        b'CfTcQRBTCr/o0Y2KTIgvTkYtVLTiy4/hJiLCX+jGcyZETRGYSb6MUXgXqphuxlUmxLvxUVRNLecgvJeOX4yrDFW5kgFijEcUG/q24fPuZnGDp8YAVdliMn5QjfLZKfig'
        b'kavMVQQskN6BDA3XNjyYMYJRnjK0HzUzrjIJ3k3PLRyEmo1MZWUBksnC/ujsEjriaIO9GE8ZPp1MqcqApiwJHabj4SI/fLyLpgxGFkmU0LMPsajh1P7cEyNdzXjK0BnS'
        b'4XazSYJW0jsNNGVD7CXomNAvBTf8IRxllFWLivAxPUX4as5/mG2aMpCEfzhN2RCxIZbxmm6fTy0QlhmqQC5uDrlh6Dsh/Ur2ce+OuNNxnCnsrhc+pMBHqLdTlSgLtAw3'
        b'142WrM+/NZ/Ri2dF7ERuqIif6JBKxEIynAof8+49Cxk8RU+BfKn7JDqPmE2sllNaozJql/IU5+IlJGKxodRHkKxq8ORE2oFkGKr7U0RM7XmGMH+v9JPhG769v1H78WTH'
        b'wW4Rkbdm/dS2Zdhhbvz0Q4rhNW+mhi4+0VhQeulB3QOHqSlP3bCLjdy7t67p5yfnjmgPfePeR87vtZ2szJM8lbD0+ojhiQnlv+Y/e+vq1R+Pp215o+he1K4Xhv144cmW'
        b'Pl7KL32fQp/u/ov95Jsb+1/8bHfq00tesbt9vnBY9O7rP91YOez90Uj7g5eb1q/wicdiM+LC3GqQ+5kt9zdXv9OydeT09YdFTYW+9Yem3akvi2twK3jt2q67z/ne+L52'
        b'yo3xA+a8+ueGAQV/Sxt6O9funtek2hEdEcudVsz9z+c/++mjPdrXTp4bfmLmpi8qOkMuLK18+oNb1XtfO+YfXTDp5Zc2jHpJkn5HvSHWZcWRj7/tH/1ybpDXAR8RlQpB'
        b'M4iOuDlRgKpQI0TEIwJiMz9ZNvDJ+WbxV4gqdp6fqTuJLlItzmeOplvI8cloo3HWTRPfc+ps4H9PV3vkhAgakeFVs5hQ6K80I0NdpMjJyKCCBugSOC+hUCgYK5ATwSIR'
        b'uAulXnIPrzEeUz1GTwaxM0UqcnUatZor1bxjfLtEemFGholU8fpfcPcCzd+MLyfUFDR6FuT3VoQpdxo1OQ67xKLNqI5I+E0piWgTqrMn9kY5qhogGoz2rlC1fj5DoAUg'
        b'b2HZiMGb4hxRhIfdr7fPZ88Wjy4vx1svRvVdWHJ74ahJNx8U9Sla9E1a2sxNfZVeqsZNGV9dGe42+ctDuXMTv1xdcz/eV3Hk6sllBx4muo6s8o9cWNDQ0CZLW3BTHxB4'
        b'Jd65r9TZrka6TuLvN+jda5mbB/8w4ePTv250fXz0nj7FL/Ub/+GPAQ88bkT+c9pU7ydWS2d76+OGEFWBwhRq0X7SP8mAmwKLB9vmUZJjJ9QmxMdE6IJhUrozJiHFfwWE'
        b'7oSMMDT3wRdF6IAdsUWgqxPD6wU1awawQsD+hWY4hY65ix7HFU8xq3Y/OpKdgE/ihrikMUn2HJF00rJ+NHgS2FlVeHOghBOMwHtTOdzkMpgeiMXNuN43HuZgNqI1CRze'
        b'7cS0EQlqDqK8e8SObMAXkiBOkJOPEG9B21EHHfNRe0mxls+xD1fSHI5xQnQaN5exDNvR6bwEKieZEejq7oerRMm4E21i4f1b8VG8k+RAl1bGGUIn7sfbmK25Jhdvpprm'
        b'dPJdAVEhSB7nvkKiT+5DzB5Fh3BTNDHkqvyKSZ6LaC/N44jahej5EbiZRnbAL+I2J5KnzRkdHow2Ll2iw+1LnJfoBFx/XCdC1Xg93sd0t1MJaQk0TkUcPgeBKWuBzPw5'
        b'IT6oRSepdV8aMRieQWACkTW1DiNosMnN8CQGjhAT1aQFHzeLKj34f/5V6/7mOfyG3LEghrrQLJSN1UXKgjBRKxPsUmfRE93VnxFMQaDyZ4hepFYW6sXgWq23K9EVq5V6'
        b'sVqlLdGLwRDUi4uKyWGRtkSjt6OTznpxVlGRWi9SFZbo7XKJACRfGvDEACaVYl2JXpSdr9GLijQ5egkxiUqUZKNAUawXEWtLb6fQZqtUelG+chnJQop3VGkNwF29pFiX'
        b'pVZl6+0Zwlmrd9Lmq3JLMpQaTZFG70KsO60yQ6UtAmdRvYuuMDtfoSpU5mQol2XrHTIytEpS+4wMvYQ5V3bJVHajgzXfw+9vIAHeOs11SD6E5BNI3ofkM0g+guQWJLCi'
        b'p7kByVeQ/B2Sa5B8DsmXkOghARZVzXeQfA3Jx5B8C8kHkLwHybuQ3IbkDiRfmD0+R6OAvR9tImDpsYfSXPCgzs4P0MsyMvjf/MDz0IvfJkZv9mJFnpLHiStylDnJPlKq'
        b'DAJpLTFxedJaqi7qHUmLa0q0YBTrJeqibIVaq3eeBc6cBcoYaG3NXUO7dYNB6KWTC4pydGrlEwBjoDMLYiGRY9272HgPOtHxX1FyCYo='
    ))))
