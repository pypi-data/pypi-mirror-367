
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
        b'eJzsfQdYW9fZ8LlXA7Exxjbe8kaAxB423hMQwxi87SCBJJAtBNbANt4GGwzGCzzx3njive3mnLRf0iZtRr+mocnXNEmTOM5q2oymbfy/51xJCCM5Tv/v+5//f57fmMs9'
        b'e73nXed9z30fPfFPBL/j4dc6Gh46NA+VoHmcjtPxNWgerxcdFutERzhLqE6sl1SjSmTtNZ/XS3WSam49p/fR89Uch3TSfORbovD5fpXf5AkFU2bJy8p1dpNeXm6Q20r1'
        b'8unLbaXlZvlUo9mmLy6VV2iLF2tL9Co/v4JSo9WZV6c3GM16q9xgNxfbjOVmq1xr1smLTVqrVW/1s5XLiy16rU0vFxrQaW1auX5ZcanWXKKXG4wmvVXlV9zPbVgD4bc/'
        b'/PrToZngUYtquVq+VlQrrpXUSmt9amW1vrV+tf61AbWBtUG1wbUhtd1qQ2u714bV9qjtWdurNry2d22f2r61/Qz92XTIVvWvQ9Vo1YAq35X9q9FstHJANeLQ6v6rB+S7'
        b'vS9FvjUKUU6x+xzz8NsHfrvTzojZPOcjhX+OSQbv1UEiROPerarM2hs9CNmH0pxkE95LGsim3Kw8UkcacxWkMWPmdKWdPJCiEVPE5EF+qYKzD4CseLedtFkzsskWsjmb'
        b'bOaQH9lGajN43EYu4o0K3t4DMklwXZE6IzrDB9+UILGYw4fI3TV2OmFkUyJuo0lKsgkqwNdyJCiI1Ity8H1/KEznEW8l92y4gdRHV0CXNmdIoIm6fHyFx1dxPa61D6J5'
        b'WlYvgiyXA3Dd0iV2cmVJwBJ7YjKHepGtIryZXDFAb4fQ5jYv64Yb8NYYtTKSbFmCq8lmspVG+KC+Q8W4eiC5W8w9AZ59nVNXStdRWEX009bR0NexhlwdgPEqHtaQY2vI'
        b's3XjVvP5bu+whoYn15B2pGeXNRworOGpGCmKXQqrIddk/Vo0BrHIL8JEaGVFILxpAhQ9AoXIMbG+SDxnBMRpAmpWZgmR32WL0emSENiImujPp6WgVmTyg2jDoN7JA/w/'
        b'HobQn0Z8xV+PMy8JQCZfSCjN3Mu1+RxeCPnj37bMzn0sRK9TfRXcHHypxH/6u9wP4bYqG2pH9hg66TtxDTkCa9cQU7ggLyKC1MekK0k9bi2IyMwmW6NVGcrMbA6Zg33H'
        b'kBZc02UB/J3jThcWoPMmQnT6Df6uCeafaYI9bhJplwkOyLHQHjAgnjiZ7MqfoZzFI75SI0LkAN6F99hDKfTtwDfIjXx+YBJCQ9CQInyRRUeTQ/3zZ/CkIRjmDE3BZ0fZ'
        b'w+h0HIfpaCFNor74IEIxKIacrbDTZsmG7riVNHFpuBohJVJOh3powxWLU/Oz80ijBPG98c0VXD9yAR+xj6Al6vDJxXRTLJkUpQZQ3pSVF4Fbo9Nhq0qRirRK8HqyEe9k'
        b'zfbH13ATviLFR4cjNBqNxlfJVeMfLv+ds+6G1F/cty18JS4IxwZs0I5L+f1AY/fKKlHQz34t7TX+nDw8uvLM5RP+2tgbpeZMPnTGntErv9h9Lb/XXyxDdt459sbfX+ye'
        b'LQu5/UZb2Gn/q0da3kgev+oD7bB+sZP6xG1aceZtQ+HZ4Dp7SfOF/WX/uLZgvrH77L66P56dPb/nmjGL//ow5u8J6t2rRyW/Z8urPzh4QMi4vnZfn69+k7LNlnxQoVRI'
        b'bAxL3BswTk0a/SqjSGO2MjMacEAouSkitWTPGJYBb8/GZ6IylaQuIytHgi/ho8gfX+LJAXJpnI1u4ElkX1iUSpEZxdCMhNzLRsFkrag8Cq+1UTSWje+Tq/64Na8gOt0O'
        b'uKE+hkfdyG0RPo/P4VpWBT49LBfmup5sJZsBZ8J0HhrJQVMt5JKCb+cjFBYKNgp/9uffeFAI/L7naIOlvEpvBqrC6JUKaI2+cmx7oEVv1ukthRZ9cblFR7Na5fCQjQ3h'
        b'ZJwf/PSE3yD4oX9D4W8IF8L7cRaps2aFqF0qFG73KSy02M2Fhe3+hYXFJr3WbK8oLPy3+63gLD70XUIftLlxtHMU4uREyvOclKNPMSf9gT7ttNf4VEZCVCZpVGcocX0M'
        b'4IAtMZkcGjZsLr4kKcTnZnfamPSf2PGXoWA95RCAO9Bx80TwKzaieRL4K9Xx83x0QbXIwOnEOkmN7zwZe5fqfGpk83zZu0znC+9+AjE2iHR+On8I+0MYcAqEA3SBEA7Q'
        b'cfkUBQe3S2ewGcthM/jwB0BMxSK3btEh+zhxRipyUnmoSEBGojoRICMxICMRQ0ZihoBEq8X5bu9LKfPiARmJuiAjsYDtf5MgRjJUtzBwvCbrraQFyNhcNkZsnQ4p64PX'
        b'PdK8XPSxZoeuTvuJZnPJOf3HEJ73swWkbVvchrz9R3Z1eyFXe1prkpzhzmh+Kd4e3T9gSmT/zcc/95+TtvaT8N4zwtc/v+eKBF0e1C3+2O8VUmFz7QlIjGIEk1LLKCnq'
        b'SbYG45OiqmF4M9sZOnwEV0OOvH6OPCIUEC3ygc3SZAunFdR3C1OThizSONgvQyFFMlzPL5sI26o3AwZgNi5TJKbOwOcBCafyKrK3t6i7rRedYosKN+QCfyBGErKfI3sW'
        b'kNtk4wKh2lrcWhilTM/IxucpSpCRqzyuMSkUvBt0ijxtMwas7bLCQqPZaCssZNspCB4h82DbAMSKYQOJH1cFC8uvcuYTNpKkXWzVmwztYsoGtvtU6i1W4BgtdGkslA62'
        b'cs6WaZUWSoEtwa4dEgCP+c4dEnKq6w7p0mox/8ROcIFcsgPkDLwD4HhG/UQAcDwDOBEDMn61KN/tHQCu9EmAQ14Azh4F72VAlZv9SSOs0Rag4WTr/CH56Ww5M/KmM4I4'
        b'jhyRdsMn8W3juBgiscZCoamBqY80FPoiiqPfU2mztJ9qQopLDaYi8fFh9XFKzeeaOS+Gv/yzvRw6lCizm7QKMQMlsovUkEMCsACo2MoEYCFX8BXbYEgfjNdqyRVA4luB'
        b'b2vVq5QVDmTdZ7UYb8C3yG0GVNGkGVczwMHbkp2wcxs3WRhQkX3kMmlT42N4W66SA3LOTSDH8HZheXmPsAKoskRvM9r0ZQ5woZjOryiAC+CqQl0L5soiVCVmi98uNmvL'
        b'9B3wYQkRmgl1QQcDjG7wKHYCRtAhD4DhoZ3/EXTUhTd6KnSQjb0GuIAjHfA52eoROhpJk3HMZT+JNR4KXUyPEaBj5rdPwsenGr4+3h77+9jjseKEipMcOveqbI7PHYXI'
        b'RmUYvF+JbzjAoxdpdSITIz7JwAPXkrtLnPDRCTjIuhS8YQE5IOCcxiSxA60Mxlcd0AEgs9dBKr3jDIADa1c4KAkAhOG2PtbOcCARlpkueLukUmuyd4EGkRs0hLlAgs53'
        b'qQtX7HsqSLia9I4uRgkgQdlnziD+iSijC1Bwjuo7A4Ukx053P74PP9fJ8XIq2hWQOqVSlZeeOZPU5eYLDGo68KoqDtnIPV/pc6SRQZIv8KoP3PGMC47mkPvuoHRzhfGH'
        b'rW/y1hw6SYYFjzSfACyZDJEfRmvTtSYGQxXauj+f15/Wfqz5dVF0cfSOCG2m9ow2pBi91NMimrK3V5stNlqn06VrZYZ3X7n0MkJxccHVD7OB36QiJ2CDG3i9P+1pJ2Zw'
        b'J2nC51cXMOozEd+PB0Akp7UCqhIA0VBoY/LoLQXZSeEwY1QXSAQ0ddnEwJAcnkY2u5O3efgKYKk7k4XU3WQ/Xh+ljMtOz+ggb/jARIWDwIi9spECrErtFZR7dFE3P5OM'
        b'MYsBHP84hK8KdMCOkMsdYwmEywWiXfYDIK8O0sYglYopZU5IDd3pAVI7t9ZFxuuMt5iI7cJbXB3378l0Yo8gKsoxHhyi4qyZEDH47ni1Nr3kU4CfXxaVfhpmCNOellwK'
        b'7xWr1FEIatCe0Z/T8y8pNRe0C16c86sFpIBMJyYy/cU/PD9H9NtuQL+kSBwWXHC2EegXhYq4ZQVO4tWT3HYAxRByQ2BYjpKzHLle0ImjuS0OYonkJK6eMrWKNERnkEYQ'
        b'36TP8UNAumgQBKCTIGHuIndBoHFnlHoDCVvvGQ6ehsRAALDaLA4ERkX9EFsoQIUfQEdVUAdGoVlYqVaRsNTeIQJ4ng5goHoKuwttNXoAhicaUfA5FirkKwIpT0apJQgn'
        b'foWFgnIO3gMKC5fYtSYhRcCjsmIAo5Jyy/J2mYMDszIuq11qMOpNOitjtBhRZWiUQSjrmRMlP1UOEwZCpyafDoSWkyExL+aEnyA+QBYgCZGEyeyUn8CNuC3Zn8kx+fgO'
        b'iDKyAF5jGOJdjFGhJ8QYfp5YJ6Jiy35+nqQZ6aSHQWw5wlVzINLI8ilo+7ZLp5gBxS//PmyyvshoKweBMEZt0euE14cCU/GQNvF96Cy9pcpeYq3Q2q3FpVqTXp4ASXRI'
        b'3wdk6W1VNr18qsVotbXybNof/gKG/PVemFZ1udlWnpYD0yyPmKCz6K1WmGSzbXmFfCZIoxazvrRMb1akuQWsJfoSeNq0Zp3Hcmatjdy1mFTy6bBI5VB2VrnF/Cz5PFW2'
        b'WG806+UTzCXaIr0irVNamtpuqSrSV+mNxaVmu7kkbcpMZRbtFPydmW9TZoAQp0qbYIYJ06cVAKU0xUxYrNWp5NMsWh1UpTdZKf00sXbN1spyC9Rc5WzDYkvLt1m05JA+'
        b'bXq51WbQFpeyF5PeaKvSlprSciEHaw5m3gp/q+xuxZ2BoqW0d1SOlzs6AlEq+Ty7FRo2uXVeHuc1JT5NrTebq1RydbkF6q4oh9rMVVrWjt7Rnl4+jdw12Ywl8spyc5e4'
        b'IqM1rUBv0hsgbaIeGNPFtN4IR5TCmSafpgfYIccNNisdJZ3Srrnl07IUaVOU2VqjyT1ViFGkZQhwYnNPc8Yp0qZql7knQFCRlg/bGDqpd09wxinSJmrNi51TDnNEg51n'
        b'jcYspjCszLGXQQUQlUWOU8XJYjprwvRDZMbECTk0Ta+3GABZwGv+7IypBcpJ5bA2jslne8FoLgVYo/U4pj1da6+wKWk7gHWKVI42He+d5t1TPJ37ToOI7zKI+K6DiPc0'
        b'iHhhEPEdg4h3H0S8h0HEextEvFtn470MIt77IBK6DCKh6yASPA0iQRhEQscgEtwHkeBhEAneBpHg1tkEL4NI8D6IxC6DSOw6iERPg0gUBpHYMYhE90EkehhEordBJLp1'
        b'NtHLIBK9DyKpyyCSug4iydMgkoRBJHUMIsl9EEkeBpHkbRBJbp1N8jKIpE6D6NiIsJ8sRr1BK+DHaRY7OWQot5QBYlbbKaozszEANtaDEOUMVFgAIQP2M1srLPri0grA'
        b'12aIB1xss+htNAekF+m1liKYKAhONlKWQa8UyN0Eu5USlCpgG9Jmk+OlFpg3q5U1QLGeQGNNxjKjTR7hIL2KtHkw3TRfESSaS2i+qeS4yWQsARplkxvN8gIt0EW3Avls'
        b'DWjKdKbgda+sg4wr50EvAGFE0OKdEhzlIWlY1wLx3gvEeyyQIJ9osdsguWs5lp7ovcJEjxUmeS+QxApkawW6zOYc+BLgT1icTb/M5noBTOR6TXDPanVlExZioh7IcYlb'
        b'xLC0eUYzrAZdf9YOTaqCKEp6AUt3CsZ3DgL60VptQO0sRoONQo1BWwr9h0xmnRY6Yy4CsHWtuM1CjpcAEGWYdcZKlXyqQD/cQ/GdQgmdQomdQkmdQsmdQimdQqmdQiM7'
        b'tx7bOdi5N3GduxPXuT9xnTsUl+SBTZFHzHDMqtXBaCg6GCNPiQ5eyVOSk33yluZCZR7Scz23RvkuT/GdWDHvY3hKujfu7Kdkjvfecic+7VmyAar0lK0TCUjuQgKSu5KA'
        b'ZE8kIFkgAckd2DjZnQQkeyAByd5IQLIbqk/2QgKSvdOxlC6DSOk6iBRPg0gRBpHSMYgU90GkeBhEirdBpLh1NsXLIFK8DyK1yyBSuw4i1dMgUoVBpHYMItV9EKkeBpHq'
        b'bRCpbp1N9TKIVO+DGNllECO7DmKkp0GMFAYxsmMQI90HMdLDIEZ6G8RIt86O9DKIkd4HAQiyi6wQ60FYiPUoLcQ6xIVYNzYltpPAEOtJYoj1KjLEussGsd6EhthO43F0'
        b'capFX6azLgcsUwZ421puqgROIi1/yvQJSkatbFaL3gBE0ExpnsfoeM/RCZ6jEz1HJ3mOTvYcneI5OtVz9Egvw4mlCH2xmdytMNj0Vnnu9Nx8BwNHibm1Qg/ysMBMdhBz'
        b't1gn+XaLmqYvIncppX+CbSgR4h1cgzMU3ymUkDbdoVxxK9xF7RLXNSq+axSIOSYqFGttlC+V59uhOm2ZHsio1ma3UrZWGI28TGu2A3mRl+gFMAVy6EkNoHArYqTE3ahj'
        b'xX40s4f6PRAlz3V3zchUTB2zIwfmW+5gedlUGmi6Y5KF93i3dyoTdmiqvufSclplFqoWt9BjIAs9KxTOTKh61EJt7dol1gqT0WYZ4FLihXRW51HN/iqnXlJQ5/EinpP+'
        b'i5fwvDRO9oqd6WHr8G4/K2mMIpuiCzJxqxjJkvnVs0f9N2rzShW+7X4TiovL7WYbSA/tQRNhyQWpQ1uhNz3sIejyqE78+z6TAQjKgLOg+lK5IPcACBsB8UAWqoxtF1MO'
        b'yDIcXr++CxEzywSGprzUrJfnl5tMMemAkcxKdRXVr3QEO3Bc2mz1PLlQjOrRKPa0Gq12IYKmuYeFPTeNqv0E/l5oaOJMZX5xqYnchbU3AU/iHkybqDfpS3R0IMKrQ+nS'
        b'8R7vkI/SnDPB+H3KEOodW9sptMkFpsgh+nUoqRxCH2PVqbgHmWFz2ZhY4KiBNWcyQgb2ZjQbyuVK+QSLzdkVR0yGmZZ8IpJmi/eULb5LtgRP2RK6ZEv0lC2xS7YkT9mS'
        b'umRL9pQtuUu2FE/ZUrpkS/WUDXiM3PyCOIhQCwtDeV09i4zvEgkBebYe8KVTEyu3q+QdmliIFGDZqRpVySm/7pS6BZVrxzLKs6Ky0qbazYuZca7eUgIIqooiFRo/caY8'
        b'caRAZg3OLFQl7CneATdCkocK0+YxcYAO3FKmpYkuEPGU4gIVb8Xin1bMc6IAQk8p5jlRAKmnFPOcKIDYU4p5ThRA7inFPCcKIPiUYp4TBZB8SjHPibTYyKcV85zIljv2'
        b'qevtOZUVfDqgeIeUuKeCipdUVvCpwOIllRV8Krh4SWUFnwowXlJZwaeCjJdUVvCpQOMllRV8Kth4SWUFnwo4XlLZjn8q5EBqvo3cLV4MpGspEF8bY0yX6o1WfdpUIPEd'
        b'2A/QodZs0lLdonWRttQCtZboIYdZT5miDmWjg3JShDfBbqBqMReSc9JSSKKYt4MgyyMmmKsEhpie5wEyzjbagDTqdcCBaG1PJD+Bh7sW7sDkT6ZZTOS61cEmdEpJZ6c7'
        b'BhtwJS6xilESJeN3PMoAjpE6qDmQfqA0lIU2MOa5jBJ4m94I02Jz6YkzgNO1GQ3GxVp37D+PiYEu/bE7myEIj27niO5s0lS9IFnojUU0KQtWjR6MWQXOxjuj5q4bhn5D'
        b'y1qTvWyxvtSpyGZEkHFxCuDiciyR3ljYaHjc9crC9pb92U45YbwtNNOalUO2xNhtjJElm9U+qEeROACvy+vCxwY4+Vgb15mPbZY2+zf76/jm7s3dBX620cdX6uuni66V'
        b'1AbWdjeIdP66gBpf4GvFeokuUBdUg3TBupBGfp4Uwt1YOJSFfSDcnYXDWFgG4R4s3JOFfSHci4XDWdgPwr1ZuA8L+0O4Lwv3Y+EA2gMDr+uvG1AjmxfIetr9iR9f3cBG'
        b'P1+Zr0ynrOUdPRbr5LpBrMdBwuia/Zo5Ax2hD3s6Sw5u9IVyKmZAJ2G+HSFQ2kc3RDeUlQ7WxUCapFbGPD9CWdow3fAa33khENsNejZCFwE96watdNcpGp1OC0G1wQaJ'
        b'LlIXVSODWkKZNGBQxLbLJlMz70n5s76P8ZO7/XNGywVUIngkdcrRKrFQwzcLddt5yKy9qcvFQ2aqQUUCRcBDamvzkFkwU0ubjuyWFGd2C7W6scTRLNTm4SGzCqBwofBp'
        b'99PqKgE7WQqNunbfYsARZht9DdIK8kuhCZg8W2m7rNgO28dcvLxdRs1WjVqTwx7D32AEvq6wDLZuKWu7XTRl5gzB4MMyEh7FMjdg9HP8MpOdqegJxynfWmmtX62Pwc9h'
        b'GSSrk1WjVb5VvitlzDLIl1kDyVb75ru9C+40XzfB4DvNHP2XIXTVWKW3Mmcx13wbmU1DsV7VpUiXiFEgemjL5B3TNMrhJgbohWqCHH5ojvnSmm1daqD/IiYCVrA5cZJC'
        b'JZ9AywP+KJYzi0G5vUIOWDRFrjOWGG3Wrv1ydMO1Qp57ISR77oHrvONH+pD0Y33oDBqj5FnsL+3CtJgsZ6qjY1bPfaE0h2J7oBUqeUEp4H/YAXq51V5k0utKYDzPVItg'
        b'TCIIqlCTXAtVQFjov9xUDrTIopJn2ORldhBXivQea9E6Bl+kty3V0/NeeYROb9DaTTYF8xJM9b4Wji0xSj7J8SYvpgrDCNcxo5uiUeGtFud2GuWEVqtrMalTYrlFHiEY'
        b'rSwmdy1VIHx7q8hhJzWKSVqUK4FqBBhxYJcIfYlKnhQXGy1PiYv1Wo3bfh4ln0oDchag1RmMZtg10Ef5cr0WOhZp1i+lZ56VyapEVVykoutUPYOhcYDg92CZE4Lk6NXe'
        b'XIUmi3BlyD4GItPJYXKKNGTjcwWB00ldBmlUx5BN06mhaXqWgjRE5yhxPdmalZeOz6fnZGdnZHOIbMeHA8oz8VlWrbhPAApH4eX+0zWmbwerkH0sVQKdwIdkrNonKiX3'
        b'V6aTLWRTFtBVvOnJimuWB6AwfJvVq1kpQ9DhdLFGE62wpyP7MEpr+RJqwIfPLHP6a6WrlJHUFQZfEKPkBVIrvpLIXM5YHZtEPkCex8cHyTWmEbZ8YcjkYuYgj12rgxob'
        b'omnfNitmuXUL37KQS3P88WV8vcqYWLxXYl0N1ey6PrD/y7/6rcl3bWzIlNeyVjd9/Oug6AltInUbSpkwPWXwrMMtiklpX48UDxB9FPoSbuqGd0zOmJjy3JFXBr5ibLj3'
        b'cPCl6acWzex/dUPVzG+/e/OwLGJZ4Jdtt45VT/u67dsNh04HLialoT+Ev6orW61+79Lyv3+ReUNlSFz+AyrWRLxDzigCmNuVklwiF3FDjMu7RISAW7kXPExkKCI1gint'
        b'lbDeuCE3Cx/E+9wWlEN9SLW4Kp3stVGWhxwlNcgf5lSxxp7ttNntgWvFski8l9Uza/Q8qIauHbnHLDSF9eNQz0Fif9JCTjArzIFkDzkcpcQX8KmIdCWPpHgfrxxAGplZ'
        b'cCA+gluhEteS4RpyWIxC8QURaVgosVEzQXJ6ZGCUKhTfUJB64Nak+Byf0ENvk0PSJLwTn8cN1H/MtU6lEVIUWinC9/COTBul16Mky+loleQY5d8cvXQsM0KxZINUhetm'
        b'2igwkQ34ILlFB9UQHami+Ugj2Qrs3uSZCMmtEtrdc8wsfjmpJfU0I9NqQstKfAkfg5bxbhHUco202ph37L3lACTQOjk809G6g3fsg2+KcUMfvE2wnvT7N93bOlxgmOkp'
        b'ZULQGulKKUe92IQn9WKTMU82iOGlEOvHVXVz0uUnXHH8BKtT6nFmGU8fE+hjIn1MQk63m8no6cbMMqFURyUTXaVYJR4ceB4ih1EoWjdgjwf71q797WTwzDl+mW0p7dlK'
        b'tAgxTpDLUXDt/oUdvIQl3DV3bo5Lo03asiKddmw3qOWvgueqW5vO1O8d2N1Rm5MTiACqoVOWm03LFa1cu0hXXvxMnasROudX6OIwPPXNQn10w6C8JQNevh8o9EAo4qED'
        b'P2Vaggs78xVem+/lal7xVM7jJ3fEMQW+hU7C7rULfVxd6D1Ra9W7OIF/v0kXU+2tyf6uJod45RN+YuMlQuOyQqePm7e25R1te+Ut/r2BBxS6iw/e2h/SseI/wpB46UUn'
        b'FwTmVsfXIpdb3bM6IDyjW50ox1hhvM0zB96F0l8JjlClhk/Ra5tf2fxewPMB+41zxWjsEfFb03wUvODXdIOcx+d8SV0nJO5E4GQb2cUQ+DSyR0/x95PIex3ZwxA4uVT6'
        b'NCc3n0K6tdwcm9AatCZsRFWIGzpjGYQyvZ6sKdy1KHPhMRwm2Eqj0Dq0LqjdA5rsUq/Cr93HsUkFK3+p1WbR623tsopyq43yzu3iYqNtebuPkGd5u7RSy8RR/2Lg4MvL'
        b'BDFVZNOWtEvKAfQtxf5uS0ExeZBzOajzUK2/S7wMdF0qECTc6WAIcqy+f10ArH4ArL4/W/0AtuL+qwPy3d6F1f/6HYkHIXOCTmcFKYKywjp9Ed2I8L/YYScn1zOr/meQ'
        b'M5kUxEQYrbzUXqJ3k+xgdqxGkIzkgu8DFdKseptKnguA3qUeihHK6PGMsayi3EIFUmexYq0ZpBxaFCQki77YZlouL1pOC3SpRFupNZq0tEkmFFArS6uKjtRIFW2w3RxV'
        b'OgQrWmeXOqBqu9VoLmE9clUjj2QLF/kMMzLVMdpSqhnp2vcu+SNsWksJtKFzoiZaXk5Vh1YqpFiX2OnsFlm0xYv1Nqti1LPL/gLMjpJP6ERh5PPZYelCb8Voy6PkzNNh'
        b'/o/6O3itRdgio+T57K98vsP6zmt+51YaJaeKT1gqJpPOd7e+81qWbj6QZuEpn59rsXnPJ2xPyCq8sDai5Rn5ucqEuORk+Xyq7PRaWtjTIKdOKFBmTJbPd5wgLoya7+7N'
        b'4b3xDlRAJW8hIKcVudsQey0OyAMmsxS2BmxXa7HFWGFzEDQKp9Tpm+2tCSZrOcCvXudRaQDgRHNT8mNiNwSxxVbJJwuaA7ZFB+fbtGVl1B3OPNirDoFtBgAs6ECFY2vp'
        b'jOyOIi1M61IjkDn9Mlhxx4brWg/9l1Nu0wvbhG1+va20XAeYpMReBoAGfdEuhg0Im0YPs1Osl5cDvfdYjzAkummYSsQqDNNodeuSSj4VkJoTIXmsxX3bUQUKgDq9ganY'
        b'BAMWLl+y6j2X1DjuXyovZj0XzlZGl9psFdZRMTFLly4VrstQ6fQxOrNJv6y8LEZgPWO0FRUxRlj8ZapSW5lpSIyzipi42NiE+Pi4mMlxqbFxiYmxiakJiXGxSSkJI8dq'
        b'Cn9EXUGpYFf/wtAcpoRPlK6yZikylaoc6tAXhVtBGhyaL5EXlYrwFjt1TIvCp0oTQOqqxrUoDsV1781k/l/3lCAZConwGa8xBfVIR3aqmyX3KslGtZOu55E6ehFKpnIG'
        b'9YqdEUHdnWeD+A9/gNzjHfhioMWX7MR7+rI7lnBzf3yMXAHRlwqHPngjOYQkZC8fQC77Mq0EblmMD5ErKnojB2nEd3EraYAG6F0rPBqIT4jJ7fARdiogpYLEu4FcATk7'
        b'eybZVtFpfPFkXfR0UpcDBTerZ1bAIzcrk+wUIxA91/uT43KyR+jOvhJ8wl+lyISGDpF9ZL0f8s3kySHcRrYydzpyOJsc9MkgVzKgDg6J8G4Or43LZjdTlZMDpNqf1MWo'
        b'yKYMXL2YNEbj1kwQqOs4JJ8mEeO1eCu7NCeLbBlIrsREcognx/PSuWRynVxmE7zFIkUBKDbVX64xRehTkZ1d7tJI7i+zBpKd5FoGaQtmDcsW8NOCYK1ou/gEOSCn6YGB'
        b'KpjME2Q7uZZFLkWRHSLUa7kIn8OHTGzZw/Euu78Keg6zt8CaQedGhHqQW+Lg58g94/WVf0DWvZCt7f4J5a+z/XBsiOTdFOPrfyxYqFhYFfyF/OMeUvE76a13Kot7fBj+'
        b'WfYqbu/P/8N/697wc22fbHkrO/zI6xP+MvFB/u7XfXueS9470rTJ4DN65Zp++6uaxhiWN/i2rMvOte57Y33y1eO9z5dmLJy/eF9yytXPfvO7yMTVC3ebbzzMPvbeoZSX'
        b'/7L8tc+azSUNA/+88T+V2hci8Zrn8latDr4beWrTY4WU3cOgSh73hFqmmmykapngsUxNEZhHLrngkako8EF8zqmmiEqQkK34VCXT8eCj5OoEpprJttvnuatmcCPeyDQj'
        b'GvyAbAut8szc3sFbmOt/CGk1R+UoMzKyg2aoo0mjgkM9yV1xvCmFaW7Gj8QX1NER6dAHOb4Hq4fP8st7koudbgMJ+ncv5/HqS+un1ekKBR6Osc3DHWxzQHoAJ+N6cvTp'
        b'/iOmN/PA33CuqruL/e2oQ2DPAwWlwzzkNHKjN4ZYFtDHQvp4jj4K6UNDH1r6KEKd1ByenYL9hTo7KtG4mihyNRHoalHraodx9TpahTtXP/xND1y9p2EpfNsDdNT2z8Ep'
        b'tQcK/K8zKNWWsb/0ThV9u6/jxLdY3+5PuRXgEak9mNAT12CL/dxQMdXKhDhR8QzK2vt1Yu6DgL0PdjD4IZTBN4Q42Hs/xt77A3vvx9h7f8bS+632z3d7d5whbfV5Onuv'
        b'ddn0yYW7lp6BiZ1CvSGE3HKgpDBnwJ8Cd6B1v2yQchDR8hJLub0CUoFx1nalTOVlRUaz1smrRAIbE8mIrEBjqRrAZf5JO+iSjLvURCXl/y+P/L8sj7hvtVF0oYQYlwLs'
        b'R+SSTntTKC9EOSvwyJzN/xGbUK/NCXtfaMex3R1xAn9rLqcKHQvjYM2e+dKl5ZSBNJZpTV444PlPsYoFucKzXazXHlMsJfS3qLx8Me0vjVHJsx3QpWVheXnRIlh4kPY9'
        b'nyuaqTyUmhwb59CRUUAAYY5WN7/DYtZrJ1xIcpR8ptWuNZnYzgDAqSw3Frt243w3g9unioQOJNt5GZgn3nx3o9wfFdpo8ScEt06mn/8XyF0T9Uv1JQ7Dnf8ve/1fIHsl'
        b'JMfGp6bGJiQkJiQlJCcnxXmUvei/pwtkEo8CmVw4PxbbqGCF5LHDl8omdl+K7FTPiw+swIfUGdmkPjoD2NmbZL9DxPIkWa3B93wT8W18jIkM3RPw7g6pCkmUwP+CUIWv'
        b'4uN2almDt+J6u1qVmQ0MbUYWOV6S85SqcQNp8MWncNtwOz10IkfxRdxmzc3OdVyHtJWeUEI7s8k2KLOV1IGE5QfSCNQJ4Vv5C/B+vA8f80X4LNnlD7HL7VRvTHbhreSB'
        b'NZM0ZpBW8iA7V02vU4oVo/CJIuDrm8kB4ULGw+R+D2tkNtkSwVj4UzmqDHw+gkMDSyQS3DaW3cM7E68jx/zJDbxlhow0KnNmykH04lFogggfycOX7ZTzxXcX4n0wKZud'
        b'x9sD8Al6exG+NoNeSRqHGyTLiuew6kizH8c6lp2bEb2UnFbQC07DyDERuQOyw0a2ZFqlcDlxbGWoZKGkG2LXpFbkklrIccxfilABKgAp8qg9kVZ4kZxenD/Dn83WJhDQ'
        b'bqSD/NlImsg1KpM24LMQArEwnUpkC3rLpi0g69k9rZn4wSwbWU+uwHsGyhiDdzLxfDzZouHIZpDQqXQeiXeza1TxZryDnMW1+CChFkUxKCZkgem7x48fP0gTC+CVfKB/'
        b'YoVJOMD/1EQP8FFIbM+lPX+/bARiizsUXx1Np6fRIcunR8+ilyzHZM4EoEgnm/MjFAAa6fROZYCwG+xeZQW+zmZQag5cSFqH29ldaBcRvpNPdiZkihBHzpHz+CaCP3tA'
        b'AmV2Ag/GJPrThYJlmgFgsw7WzwE6Mg9zhC+QHWKEa2f6zp1PLtuppWGxtadTJN5MTuar8yLIznxZoMpd+B3XQxpE1uKL7HrlWNKmsWYqc7NhZGroytaYHIcErCB7JLAz'
        b'zuWyrTOTXBsXJdz7mYWPK6TIHz/gyRW8i+xmVwmjRTmhRFoXiCq03f8QnpW3W7B8wE3k2DJyxaH7IHUKfD43P50CGtkUk5udFyFU2cn4gRzApwLIth7xTCuAj1eRnVGq'
        b'jOhIDkl7WPBWPmagAFVTBuCzsDlA7OctHEfOpPabohDZ6RkvPmTIcBYh+4bRMqQliCWR27h5mKsUOUZaUrX4NHMjWt5T5BjhJKVrgBa82/hiSLrEmgpSVLdo08JtY3JE'
        b'EwI2fNa7PLklO/079eV/vr12yPGTU4+evDI+c2jNrrpFJ7URWc9LQtJfUn7c+qesu6+YpyR88dZf/7b8F1N/d2NR6J927GjQ3WqMVu8P7z/r4GuZn7zV3nrFlLnp0FuX'
        b'x3/Sq+z1x+rn5IoP7xyfFj/pcs03h0WlQf1VLS1jF/zmhakv/efuWXuGru7R9B9RsX5teUv7Tahae/UNy5SvG4Pytva0xdx+c9Txhe81frzsV9vtod9t+qR0+bvZJ5uU'
        b'j1ZLdgx4d0O3v5FXt785pnhM/JsFm54fJV284MFb4av9Yn41etT+V1b7vbw6OGd5zsefjVn5yblbwZ//btrA0aGirH+VJX5Xf1Rz/+OVKbfm6b9+8/Zvmz4fd/RUj3Xf'
        b'vlP1T/1ta8nMKz8/9Ltj84vGWaZV/fCnIVXKFROUS6vHmPZmPNxXv3tcqMls8ClQBLIrsXzwerJlDj7aWU1BVRR5zwnmEReee85NRTEsxc2OQlBQPCBXWFX6YfiUQ0EB'
        b'NdUs79BQJM1l2pC0gGJymNxVu9nqBM8SmfBNvImpJkhNP3wxKlIl2HzATjriO5fHJ/BBqXC119XAqigVxfXRAEMZeryFV5LjuNZGAQ+34Puj1FmRUsQv5CyTUrTkLLuk'
        b'Uobvk5v4bFZ2NI/E6v7kAYcv45oK1l7SHHIWyIJg7UGNTE7HruRH4IP4GjsG7Eeuk2Z3uxBdiSsvtQtZhe+zGcIHx+JDwnnhHdh7XQ0+8AbHtZukLYecstJdpaSEazOM'
        b'/AKd7m5kmwi3kU1Y6LPvqnSHCgY23pluTAWDj+c85bYtRch/k0bGk24miCogOmRypp+ZRdHLGqah4QXtTIeOxo9dgSZm+hkakvFB3ABIDYM4ao1C84WwXDRHAO/HSvJr'
        b'6VsoV9Wrk+Kjo11BpxMg6FX09GGgjxL6oNc7Woz0scila/GkzvF5lpuY/YQ6Da6K9a6aFrnaCXQ10aHYoV8omOeu2Ik86UGx4218xRI3Foyeone+sF1S61OL2JkqV+vH'
        b'1DH+tWLXhe2SOmk1WiWt8l0pYeoXKVO5SFZL893ePd2ITxvqemF7kMDrpSziGePQ1rcka4RvOCpgsbVhAgdYsXJV9L0+lYgRdNEqctGKG7sPli0RIVEQl4rIIUHlu0s5'
        b'OB83FpDGmdl55Np0cm1mYHJs7GxSj1D/XiK8zobXMzo8KSUlnzQWJMWS+sTYCHIV+IAlHDmcjE/Z2T2Ot4alOevBl3w4JInkgEm6lswoEjk/Bp/HV/Blelsgu5f9Hq4W'
        b'aNU+3DADaMoJAJ/h+Dw5jsKRntGWcUDL16pVsYnxSfhQFI+kqzl8sAifZb0Z1TvLeRE6PocvSBwXofcll40nt6s566eQ5/c/LC7bOiFTHBcy5eyOnFEP86ZNmBz8bvbo'
        b'dRcWzk19dUi9SFXzy19U5v3h/gQL+qJ02JjNdaqvHn300V8yfA0R28aPWlIzWx67951bNd26n9mne3HoP/qFLzo6r3v6rsa/HXsHf75v+6fDhr6N7AmL5l2zN37+7j+f'
        b'//qT6ElBH/jlpA55/gvTgmOBlx5Oz/hqwb1Vib2mG78+2/ut+6Prdh5W/uv1oy81Df9wxPYjr0377LNGU8sXV9uM48Y1p/7wj9rHv1YeN4teuvSrEe/dammTT7yX9+Kj'
        b'f1WeOnHiPfO7Y4f/8fcvrtYWPoj4MOnRf/19s3ReD6vPX/7a95MUzbH3fRWhwpWvrbgZH2UfIUjBR3wQj49yM8l1vFm4EXg3bk0HZIvr5gj4liLb1sUCcr9Jtk1wYduB'
        b'ZDPAHWBb0iwVkOgpctPXgxEe3ouvOszwrvUXFOGn8fG+7uQKsgsUi5yEfrB7HvcNLVXnRAPrtzUGn4E+rxejIHxfVEhqJayjZj2QkQY1qbHQa+yReACHj07BjYxKzceb'
        b'cF3HRd3iUcI13Pi0w0ZyWS9yreMOfHKIHJAIl+ADN7ub6eFxDdmBt6sFw1kT2eM0teyJz4v7TsLVzAqyIM+s7mQCy6FQcj9mkQjkn3O4ntGLUaZV6iz7IE8mjIz0Rq5m'
        b'M1KId+Cd1CDWZQ+Jb5EtUhQ8QPRcrC+b/eF4DzneQXj99QLpJeesbD7mzyabHCQnd4RD6Y+3C0WzUmGbNZB6XJ/huLOf3dd/jLQyiCgF0eiu87JOfKbMcVln8CI2mVJ8'
        b'cQXl7MiWXBCd8H7AHHgbXw5AtOHZkPH/1ncAnPY4wq3/jHAddxEuWUwQRc0MPdO7yinR4unPYzHP/yAT8f+Sifl/yiT8PwKk/Pe8D/93XsZ/x/vy3/J+/Ddif/5rcQD/'
        b't5BA/q/iIP6rkGD+LyEh/Jd8N/4LcSj/ubQ7/5k0jP9U2oN/JOvJf8L34h/y4fzHfG/+I74P/yHfl/8z34//gO/Pv88P4N/jB0r/JB4UxPeERkIoGXSz6hG6L9A/nw7K'
        b'0+4j6Lut7RKrTWuxtYsg308ldhJLBX03u2hauYuwMZpGr6M9T2laHwdNQ+vkrz/dCEno7v+AYViJQvT9n7uoLgRPMJvT9cShAjY5NDMWvc1uMbO0MrmWnjC4KXqeSTsv'
        b'X6xfboV6Kix6KzW/FDRIDpWY1XUs4FAnedKqP3liYBL0cLQ7Rctteg8ar04kWuo+eW7m/Ey4xOfN9PJjqqEA/FAHrOYlQD6XZwPivYTP5uE6CQrHa0UrILyDiend7Xgz'
        b'aYK1TcC3VEiF68qYzIkbq8g6IOCyJbhhtpLsUqtUIhQGVd4nB0WAQVvwHkb8RwB5F9vehW5oohck9EFMP8L117qKSgeTnUVAfY/4kOPkaDyKTJKkrq4SiPTaAvwgSjU+'
        b'Q5ACqQi4tI8gg9f3JQed1J1DJeS0QN1vxDOpMpXc5AX5EDf5goiYmhogHHFfW0zuAtPQcyotxeNGrh+9utz4afpDzloNGaLG7c9+eVAQHh+y4U/fGioV99DxAaT/treR'
        b'v3nG66P+ufniewF3fH30k2a9u/qva/z5vrPDZi34S+p/DQu/fKTutRfmJv32t1+vfbVxygHVzH4Xet3dWHly9cE/7B284nLioNK///FL0x3fYX+Y/lbV40eXLJ9/3v72'
        b'Xv/Ra74zvJm7ZWl631981Ev18bAtK3UKqWB/f4mcBmGlIXc8Odn1dFZCdjI8LE7B1YDEw/CRjtuLOSAYVJEy12CMUmXzaNBMHp/m1BP7MQS7JITKKDHCZ0B45K/HTZk8'
        b'OYyP4x1MiFlCb0v2ZMx4k5yMANkkh1xkNISch5Vuo3QNCN0Jx/ddBLqWRbYrpD+CRrxYQmqthXS7Mcw72IV5xaZQETVMD+VCRRTnBrAf6b/CJWLeDZE4Cv+olaQFHh90'
        b'RlFBLU9FUY6aW7l2cYXWVur9rvexyHGNNj3ypJ+IkLruexc/033vgLL+JOI8HHd2YC2KQKzaSvpmMrnjr2d3mqODGCXPMMgj6VukHBCwVVCsU8ykX0b9cqmeOVJVZayI'
        b'jGYNOVCkxbOa2krvHtS5lONaS3GpsVKvkudSXf5So1XvQoOsDjYAll0rN5SbAP3/CE6jC+fbBafJcuzUZ5e0AA90MCo9elUl2TQ9HfiZzOws3FqQDux7XbRKIUXpZKNP'
        b'Bb48gF14LyL15KIadtSSsMxsFdkELF8BZe9i8oCfUUbQu2fU5LoP3mULYOqm3qIk0oTPkvogf8CgIhOH15PmBQw5jiM1pihY/WWIbPNdBpzNDkFbeYicwhejcnnEjZw2'
        b'A9hLRE4YpxgieOsNSL305rEx2XF+/ISArMsrqpZWffO7b9bHtF263HYpZMId5eTJqbltb5W9PfxA4Ys//PZTv3jxjr0vB7REyS5nf1d66IPY9/qOtJ6ssCYXrWk5U/Db'
        b'zDNi7ve/jFi3+UCePdP/lX1/ip6UyI1JP6ARffTN5HXr/xLROKI8dNDf1PfaxbKgb6bvGz5yze8XvZFYLlvz+L2PSiLX9J+fu2lBj4dvSB6dfzkx/3HwPn2P1+RvP+oR'
        b'cGP35d7TDqze3bLvV71e8UntWfCFIphpVUZTlS7MNVCRaspYilM4fAHvHCIw7afxyecoF+v4ZJys/zzSwK/qjncKtiSTV5Ir5OpS5YBUwR7FF5/i8TE72cSqtuCdGlZ4'
        b'EwgDUnKB7Mrh+ynwVsZGF+JbEfTbeNGqRXh7BsviT9p4chffxTeFD+ZsGzteHY235GJoQ/jQgf94nuwhp8gW4SsnN0gt8LUNVG1JnYzITrJjNR+JL+L1rHsDcB2ppnRD'
        b'oSJbo+nggmNFvWJLom2CLHMB38FtHTfFz8H3AN2S60WCK9SVOfhAVAw90VCqFDygwkMicg1X4w3zyW7mo+TfbRnj4GNyJEiahJtH871G4xus6sEKfF7tglZf8iAujMdH'
        b'kkiNoMi6IBlAJSHHxOBz3Sfy4THkGCMBiqR5wuexssZ0MNsPLKzFKeRwrNAlaNE0Gp/mo8X44tP0Qj+Ct91wtZhuYYaoo12IGq0J8KWaHRnzJQrgQtiT6mlCmL6n32N+'
        b'rfhxVaALsdI6hLvuHZ9AsKFO+hfvPW3lhbwd999XwuMxRev9XGgdrev52NNHETq1r3C4ck9B9A4Al380IBfHP4VE+MPDb/cnLsOixvu68uLCQuag1C6rsJRX6C225c/i'
        b'HEWt9ZlxD1MEMc6Z0SY2EoF7D/tvV9M9dVEt9EDnfeT44he96MBPDKLOYx5mL+wxP0wKxBfmUPTT/gaJA0R+jlp6Pg6ICaHvon6P++QFpcj69uEEju4Qvp1FDfeUePMK'
        b'a1CQCAX258mRlWQvOypbvUzuj0/bKFrpi7f400Oa6fRgpl+8eAipxjv+B77W1OXzYM6qO9Mgnxw7tYCagm/n5IsA0yM0CA0qm8o0RlN5EPdv4m1qFW6LTYLS5Dq3BJ+L'
        b'FK6LaMDngEhkKkkbSOPsC3oOpRFuiWbnNYNTyQPSkBFNmSv69THcEIe385nAn900fvjL7SIrBdnv6h480iz4Wdu2I01xG5ZwxT5H7O/zJzcE+PdOmxD9YdjJsA83ZGmS'
        b'1X7+c5qPpF+ojttwpPrIzowd3NDuL//sLR6VDuk2L32/QsIQzWxyNCKMbIxSuXlRAmk9yrBjMD48NgdfdfsWH0M19wFJ0T2xEtDXgUnkfIfGnenbd6kEFHZ46HynXM9k'
        b'eqUSpPpqx9eF6qgymx4HC6kLyT4Lryc7yOWnuc0EgIAF7Iy+kNpHMETU0w0RyYYG8fTbGmJAO2LOssK1pcTtYlqgXepwZ+vygSh6V51lpWtL0JKD+CfQStA7Hr6xR9n2'
        b'kfgiuRIVkalM74uvRWfixhjhRFdOdknCQOQ63AWiQhx/raN4t3tARtMbMABkeZ2oxneeSC9mH9dD9LN6jfw8CYRlLOzLwlII+7GwPwv7QDiAhQNZWAbhIBYOZmFfCIew'
        b'cDcW9oPWfKC1UF13+mE+3RjYLpyuh64ntB3gSOulC6d3fujGsrQ+ur6QFkRDwOlSvx2xrp+uP8QF68ZBnBhKDNTJ6c0czX7NfLPIIGoWN0voj663gYc4+lfk+ivECk+x'
        b'kMPtKX7yXTdof7AR6QY3S5o43ZBmP3gOddYF78OEvPA23PU2wvUWoVPAM9IVjnK9RbvelK43lestxvUW63qLc73Fu94SnG/uY9Al7udPcLqk/fy8bvpQfTddcm90uPsR'
        b'VM2xUIozxHKEMQNKwTNKBnPro0vVjYTZ78FMK33YfEt0o3RpENdT15v5DI5v9y0EuqadCjw2c2Xvcj7QWUoRjDSl7BOMUtepgOSZTgU8osauHnd+wqnAn9ZIULgxjH7o'
        b'NuvPk4cJR/QvKTejtZVxPJquyclQpQiRnGYlt9/3WwmK1aZV540UvmObhC9WUbzvct2noilssyaXeAroqMEH5ZfIQvDGElbR9fIhaPz4LfCmKWpaOhJ95OzkX+nDeDI6'
        b'jLPSAxrTf4T03/x84NrYANGBxBNtope59Hfque8mv/daoZb3m/H7fc2/OaCcmxz/lub5okebRh95zb96xvNxd26lv/L59ImvjDibePvFdx9pzr363Zevt5SW/HPkx+9m'
        b'7fvmh1GRs7K+9WlS9x5ODApfQdPdWiYRvj+kBA70ugjJCnjb5AgBNzbEAd/cgC+yQ0fpCD4OX+xWRBoZU1u4eJHjjJTs8XG34p6A65ki3IyPkztMYJfCpGx5YlKG9ZaU'
        b'xpLjgkphLd6DDwue8FERSineJGSEbL36iUejOJaLbMNn8Dahr7hRsoxp1jfTM8cWET6Ca0YKudrwbnzDmQtEgnNkazY+hyDbThE+VhovMNzXyD4NbogBnjcD5IWWWRyS'
        b'kXoe18zNsVFJDLfk9sANS6EORtmhJrw1F8jLplyyRSVFI9VSch+4811h+JKAvJ+ZPe3wdh/gRhSk8X6cTBLOvN6dylz6JUHXxnnC0V1QnrZLmIlVu5ha6LYHdJzAmcvb'
        b'fY3mCruN3TnWwbW6m75LLFSvZFlHHzXIybCu79TPmCfJS8/feProXNdePpNLb6ng0isppN336ss7AYLMl9e9HZdLe7+Oa1O7ePSqLGqKbX6Cd3Fgofsceu3SZGeXvh/g'
        b'1nxXb3bVT3Ok71gxbw1PczXcP8OZ2Wki+pPbLXG6klMgKiwzenfnznQ125MKKHKDpbzsp7dX2rk97TKv7WW72gtj7VED4p/amuOSAGmhrdymNXltarqrqd4FNKPT0Nhr'
        b'e/+DnuE86vr1REY0PotnZm+aX/OarPIlgwSSdG4BdVtCsugoTVb0mn7IGPv2V2IrvS/OVNZIP/vbsDtd26yLMORqAwwfaz5GX7X0zt/zQu/1vVPf4DRDJO9XL1BwArJr'
        b'7YO3M2yHjwZ5RXh4F76U8RS2l0mNrm8LOhGb3yz67dyqbu4o4tldxvO7sLdnPd2u0aXyh4/h3/+p7+R2lbwcy3YrRDL5LSSHt7Wm8MFvV7CJmZk6q5iB7EkVV3rOeChZ'
        b'KrZGQMTfTv1K+FbzNt2cny2p3QMU8eq2VtHLN7Tsm5QvI7TovrR6wa8UvI2uMVnbY9BwIM1PpVF415R4RuRx9fDeVLsUqVRR8Wc9b8f7E/LGPU2ICS5kNtPGKn1hkam8'
        b'eLHr24DOle23oKq328R3zt3pe7cSZuzbVZ5pQp3UJDvgMafLgnsyPPHebqet6lxzOgPO79+KYNVF/x2fOvV0jsVW/UDKN9ynIhQSW6AZeFs9CzHb0bH4NjA5Z8UhAHpV'
        b'qMqiYaI5blwzAp/lA7MQWoFWlM21j6Are4ScAKbFna+k30yNyFFyKJHcR3iTNGgqqWY2pt9amAFLetpETUDPRXbEjCWLknP5F6Ro2avqou5/mFM77DGyU7XRc/ED6S1R'
        b'a8lGdlOUy2iSWkw6gKbTJVFHyF4/sg/fHGBZC6WZpybZ24fcdJf7+5BzuAHk/tvkgXHkz14XWTdCrmxl+bBX4kLXx4aJX33nkPgDflSFf5S/8mvx7yrXRGdNmdi7j9Gy'
        b'+YOXRp5cb0u78g9DwufLxhiGvlDZ/HLNhszy9+OOjD8RH+S76K4vmXzN/8HLL3/Vzf6v2+/83LfF983zc1e9P2z/iGOfrVH+fFZIiyIneOeKWR+9evHBidcufMVX952a'
        b'N/q1e2vseFDN628ofBiXOnOxyl1vilvIYao7LSHN5CyzXjDiB/hEh7FfPQj8J5ycbCm5wxDkMpCPLwlbzZfs9b7bSMsQwdJwLblK6v0jSWMxtYqlJ1DOK6gG4itichFg'
        b'4RarmRxFvZmtCGV3YbHxucyFIEM0OmuWolh8RtoPWNr7Are+PXWBy6JOpp3CzBvuTWV6Djm5anPTZJBtqdRAQQwjc32A3KvOVFq41GJ0fBpW7rbJZYVijucGAF/ax2EV'
        b'FwBv4m+qQty2ICva+QvXWkuJ1QvfyVt2dt73zfBY8OS+Dznq6dzryUZzisVu27LT8bLj48bM38/1cWMxO+ySwI4Xsx0vYbtcvFqS7/buTYyUdNnx0hzhUKUOrxuMqfX3'
        b'QGpefG8gPmRlgi47Kw7xMUXlKWcpqZEoPlzg040fYMowts1/DVnpBZtnRqmolmwb/v3zbz/ftu1W063qW3vSNtxKVOwZtOFWdWv1yMaMzYP2rEsIRGfVsukL/IBoMwvM'
        b'B1Px7aHzQYahehwMwMIMVzjUt1QMHdpHNVXoWT4KXMhcQNjKh7itfJBJzFRUnSadZRXU4lI3w0H2hWqmneqM41vFQuwTOdmq76J778lV9/il4C4d8L7o4xGzL0S1UqaN'
        b'oEvv8xOXvotdIf3XVYMgyRFWmG7KEA2+kU9XeIsf3sUhEbnDZZOdWuO/xi/nrVS/fnxy+iONWhuhjyhSC8yY5pHGaIj88AvNQ81iw6e638Y+0vD1sckJ9ssnYu1tlW0n'
        b'4jbFiRMqDAgtuR7w4f7KDtb1mYxhOn2gnCoV3RY5zH17WwRrIWq4WtXDbZ47yghV7fYOSntcS0r92MufXNLwrR6W1HNTD+mRg/fFHS3saIljT0v+Z/a0c2GZ+veKGl+G'
        b'lSU7E9JFaCG+IfGhR6yH8H5j+t/2iq3UFeTuLP0jTYZrbdV307WfaFTajzWfwgp/qgnRlhqyikOLBRbuVJPPN9M52MEUMfTBbfig09CbbJyXgs/gxmf/GnF7UKHjMla3'
        b'xXVnvWVVYupVHu42150KOBUXnXdnu9SgLbaVW7xgb7Flv7cd3QKPpU8uf1ith+X32iVFsGCn3GG2TC2W2wM7pPLF+uXtgZXl9uJSvYUViescjG/3L6b32ejpZ2Xj3APx'
        b'7TKd0SpcREOtn9sllVobvcNYb7eBLErv2qV7tT1Av6y4VEtvgqVR81hOaiAV1+7nvEjGqHPzvZ/PctiMNpNeIWMHdBZKeyxp9MHO74bSh+tu5Zx2Gf0oCa2y3Z++OX3e'
        b'WTS704q1F285Rmv2oa6XReXLmHt+u6SitNysbxcZtMvaJfoy+lVdvl1shJLtoiJjMQR8JkyalDszp6BdPCl3xhQL9WGyXEVPqEHoUtL1paowhqEc9ylLmWk2VyszyP53'
        b'z6REjuo7765igUeOHrhqyjj0JVOnXlHEIHYmRf2oVljJdXoQHgwgxZOTXOQQvJdtRRk+mmm1VZLrwZNWkGv+HPIh+/ggvA5vZvehrBaHRlF70PMR6dmqjOw8UpeDz0eT'
        b'rTGZeenRmTHA65LGKMFnijQGSxFpmh8wiaxLYsx5ZPcM0pRHbtAPwFehbLVgB96bXBiVkJhELsaKETeC+hpdjmEJpIVsI+cTANITUAF5kIA34mssIYqcJa0JiXJNLI+4'
        b'CISb8UWTcJnIXbxxmMP15Dq+CV3hkP88nlxYtEhgIO53syUkktYFsVLEKRDeifeMZgVDyCGqLaXXq+BN/ZLoF+IvcaSJ7CfCXbWNEyPHfsqfpiRo4u0pOsSsQmxkA6mH'
        b'nuMDsRziIhHwpftxCzvZK1iFj6pVShV1MsxWkvosbXcO9cLHxePxzlWsxq2Zg2bd5NYiVKHpV5gpFWokZ1bhTQmJMtwcK0JcNALZdCeuF0SCfeSuKorev5JBtpDmPMp6'
        b'BuNGUVEPvItVGGTulVnEzwH2VDPaErxQmFt8j6zFdQmJxZpYH8QpEd47diwjpf3x+gHAwIbhy9HU2kUczYHgtEkAml9MHBtv475DKFYTv2QZJ7hpFcdNTkiMicNtIJWp'
        b'EN4XgPexigzkQH6UKhFTixsQnHzjeLzHSs4Lln9j1Dm9RBEczJqfT1iVwKZBl3bKEhL95uE2WO8YkBT0eKdgm9cwkRfM3Obhu9ReAW/kh8ydwqq6Mlec6kdPysZrTOtX'
        b'jxSqmozP6QAMyB0Q9uhs7QQx6gyb/8Hkylw1vZ2mgWxRK0Yzy7QgXCMai7fje6zC92Qjw9ahdxHSaGYYe1kd89+ELxkBQC7immSejXP3MnyXHT+TK2agUqzKnKwcg03Q'
        b's3NAXJrFuN7iJ4ytGtcsSUisIDuSpWxsewz4HAMwcklKWh3FyZYVK+nyBVWIUnFjH9ad3/l2D/9ERBVlmgUDV48TxkeuZJJzCfHkGKmhAAsj3JUUKrg2NOGzBgFe5+cn'
        b'8QCulznSjKsXsrWaTC4NTEhawsXCtMRDIXysD5tgEDrJrig1lSqvdcvikNTI98aNsaxMr0iyLyEljGyghVKh50H5DO4Ck/B2Aexgc60Dse0iQgGjRSHkGm4SduldXN89'
        b'IQVXL6G7cRSARrZwdo3v4JPkmlqYqG68Ap8Ro4AQUQ+yNk/YU1pZPBLJ6QpEK57TCWCWEzQmIcVANiYiVtfefriWoSXSHImvQD+YI+VNfF4N4FHM940jmxwuGzLSBJ1o'
        b'wjcTAarSICJSybo3AsTOjWp1YD96NMGXc+PxGRsz3OqHb5bDgBcmQq9HAxTOniWwIkdAsjihpohssx/eQDbDNHXnffH6RazT3+ateC6X+5iC9Kx38mYIu0yL9wNwxI4h'
        b'GxIliJuI8KG5oQzT8mRbOIgLanI4kx6giMh9DgTj3YJe8YeRU2Nr+HAONmzmN+mJAotLbk61QFX4EKlOBBQwiXoI78N3WDMZeBvZqSb1U/HdLOBlnuNiFg5mNe0v7f1c'
        b'OdLQmeznMydOgOVVIBzvVGcMI+ep7Y9YzOFD4xwGvUlkJ1RLLXpVKJ2sUw222ZW07XUgF7cxz7cZ6fB6AJ/NVc4S7OJIXXY0IB6EpoX69CXrcAMDQ6M0AECwxF/wqKVH'
        b'O3t4wFjVmo6btKtSRKpvGQ3UBOyJKhVWOTYVbyFNwHRG0zvBT0eLyRW7IM/n4Xp1J8NTshUIjBnvF6Nh+IzETs75C/CwCfBINWnIS4rFV8ykHlBYKLcQwPOW4DraUEX2'
        b'qAuyMkgjgAPZi0jbYnyJnc8X6/Ael3O4009iG77BoWG5EuNSclFAnJcsJtLiT0kGeo7U4PvTiIAH/PDOsCiYkWyyJV2ZKciCcd3NYjS8QBLvR7ayQW8I7FO5HJVScrEy'
        b'wNpdgJJpZCOuIS3AZuMHyIZv4Adz+7EecbAcrV3qzOzFo+EzJQlk7wQG4pMm4QPqPLJlkVJKnY4RuScml4XBHgasdjs/u1d4HnXl5ldw/dbgOpYUSQ7i++qZ5JRMmIgT'
        b'iFzlDIKHejUBcVqdga+tcjrhO1DaQNwgJterJKyGCHIA1qElkBJX1I+sByxwkBy00zO12Utm0t2tysghjUPJnqgMZbwY9cX7xCZ8m1wSkMMOcttIWkQU7aP5+DK+F84z'
        b'J/QQfETtKoy34ju0NA+lW8Rl88g5BqZ5+Ay5QhoonKGJ8UZyfaJACW/ifX7UeJN1+MYK1ufg7qJFZJecQRc5Tk7D9Ap6Any0dGBGLDNYJ1fxLVmUcIUZhaz15KzDNqMf'
        b'viYm9ROJcINZIDkKe6dFQlEYIntGAiJrDmc1B+N79L4A4EgWo4yKxeQWviwgjb3BJrUy06DMwOciMul+6z5eRJrJuZGswimxgaQlALJdBV4FCPJVchzvZggi2T7I4WKD'
        b'L/Zyubfa0tjkpZJLKdZA3FQcCCgK9h45H96DgdfxSj8VJ4qg4JVVuBz2FDNEXTmbNMCQy2Gh/MtBxDnKlhmvN02gdoUb8Z506oK/WZ2rZD2U9xWTNnrMy3SZi6xDuVeh'
        b'tHx2vO6d1OUj/i7A7HLgwOrxWTHl12D1zlWtIQ3GyJKfS6zfApv7G/6XC1+fW/7G+BCfL9+69v7QsqabR2pu9zvy9rf/OXHdrl0T539+5e3Zy75T79yxO+KXx/46seZq'
        b'7umBz//j/Hd9VqKhv3j/vP4vIcP++tdPl11OGP5xaEFu8C9f/Zff3W6BOxXD2l+fs/fwo5+HvRbdWHBO+tmR4IEnjodFnZ33z3/W1vvu+80PyRNCvzy1GenP/nn2z0vz'
        b'Jya9N3pE9365U2sUjzIWvP9twfQbfoEjjryYqH7jpbHbe+/6V868wT5zDAcmD7ZG+xzoFzryZcsLGfM/KD3y1d0X43a9n5NTt1/31qMvm198OLG2ZPKve36yv/vI31ie'
        b'f2nKdvWGUbunXAj74MyLSbskIxoGvznXnDo39NZLll9VVU7tVtqy+T9uLEsbnD/g0fMDJ/1i9woDd+Tv+dOaCy6Z/nPO46O/nR2xov3Au8acb+4+/8c/hc16/a0lC/4w'
        b's/rM2f/I25p64YufH+gz/4Be9ZvT367c8oflU9/58sK7OaPezxv1PjqbselB30u/2Fcw/2dfXfgk5j3zueX+rz++Yu7xj+GfZ/zx0cO3epZ8c6Ot/h9FffcuORDSYjE0'
        b'fPHuurcz62oHb41//v1zu3V9cl8/kDT3hfzWL89N/9OtDx68+FG/9068eHZBn2XKy2VXsgP/MvW9G3//3YZl3/5xeOKXz30wafWHx1449OVbi1YuGVn48/t/aQ369vtV'
        b'Iz4wnbgZc+j2K3Nitp/MSTiwyP7RwE9f/n6w6pGiO7uJDp8vZ1YCT6Br0rAUVwtmB2SPw0kBryV78cmoHHLAqqReF/u4bNg7pwVN69lVfsAU4R2RIEhIkXgyB5uscSTT'
        b'GZNdeMNzuCG4IsACm7dx6ILgykBfKQrDh0TleEsoc0PIx80p/rh1NqmLTncqf7uR2yJ8Hl/Hjcy6rDtICE3Uag3hi26Ga+RqJlNdq/FRvJbaKFzHrQ5TWRk5xsNOX9dL'
        b'MPttGsK+hEC5N0H3J8vmdSWkifmRjyMbtercVAsdWSU3AW/A24VS9eTyNMEWDhhClznciTRh2E0pE4HUMgHB5fh4f5BQ8hbZFyiYg5SR9YJFSDdqFChMygF/ctRNkR6D'
        b'N4x26NHJdnKa5ZkwBPZ2Q24yOSlYZ3Sy4Mj0E+p5QE5rqU782lhHJjfzjVljmYI9j544UHuRpXPoOQaVZPAWlwY0aqQEX7dOY+YgI/LyOlSkeDtITu5qUnI6jk31FBjV'
        b'bacr5PoRHR4juGGsYC9yJJ6jS3FSKliMOM1FFpBGTx8Q+Mn2re0irU7Q4CyDh1ODg9aEqnpyYi6UeaFTn3LqUOf64UO5Lj8QJ/skqP9Qx52CfuyXau778HIuiKVT22ea'
        b'N4SW50O4MHjnOdmnoT2rAjsUM9Afd5W+harhfqpLHi+U6lD1X4PHGd5p+7LO+dPnDU+20J364v0MnqkFhe9poVqJSy3IMcXFj5/Eezzck6MnFRcjBBk0bhXzI0//faAm'
        b'+l/Z+UjQFVI6N5qc8MdNEi1ei9AANIDcKGGkuQdptOAm4JH3IdQb9cb7SRvLrpiKbyaIqe08QvEoHm9TsvrvB9KPxCCZpURjOriyFLFTvuCeLFL+XzpNwADtWIGBDfFb'
        b'yX3Ho9IJcdoVWxLGOeTqkyvxjgR8OQOkDZA7UTG5ESWIbC34fkRCMG5JBO4W70Z6cpe0sHoWDGE30pT+bpAm+uqYGULl85fQT+ug0inLNVm9fEVCN/KXdqORsncrNAGL'
        b'58wScsbaAhFwDCEvzNFErwgwOjq8lEXKvirURJ8ZskTI+SLvj6CPsku9NQEvTCkWcoZI/GgkWtBNk1U3JFSI/NsUZtmAXldoTHPDIhHj6YfjzVPzs4GTnJlLzuDzYiSp'
        b'5PDtHHJLGN9N/aiE2FgxtdY+zg2ld96eS2LN/jN5CJoMXP5zEs3ENZYVwmLhC3NmA/swFTheehxLNksFDm1/xAjS4qdIgxzX4T+5LBOkn9vsIqgWKfUGpJfvw//l+J5Q'
        b'5tQMYJ6aOHymHCElUs7FgpLh1Fh2/U+4KUuT9Ubicw6F8p7gENJEdtIfEMlGk9NkI8LXyJ1Soa7WYnICN3EDgcPtj/rj06SaiaxTcY3ceewKIth+weSa/1/NXQlcE0fb'
        b'32xCCBBOERE84gESDkFQVDxBQLkRUFFUDCRAJFw5FLWIKOINRfEWEcWDihbxvmo70/q1fe1h29fW1L5tbbWtbb2K1p5+M7ObCxLEtu/v+8iPye5mdmZ2do7nmXn+zz8W'
        b'tMwir10jTU0l+0upoJ4Dazku/pDRqOC2RRI/a3gyCgOBSsFaVGZSW/WgGUlihynYANYgaQrJU+dKGIX1CGyG1eAwDWvASrIrDTankA1g8mbEC8l+88RrMfPiRysjmPXm'
        b'1x57ZlMz9+Cew1mwSz51KWWlwl5BW1tCCmoTEmGQ08pxCz7wTij/IDTG5tbpW+7Fa3dT7U2xzROnDk5/zTfibZt5+f1tpo9z6HGwyTkr+73ffti+6HFaWvPGiWNmlr7o'
        b'ObU5Pu/ai7MiXqv4V6SsesHVkMrxr5+P/z5jXOmYaS1ffJMv9JUXPXKuS1kiEM78UXXtxePRBVve5l+5fMXb+vZHJ2OzPILrF+TNE38Mfkj6eEl11eLKs42/c9pu1fTZ'
        b'4Ph7M2xwvhXY4rm1R+U1r5+zBzpl9MzY33b/UO2JnuNb35xQQvdqfnSgTfx0x6vyH78vr/J690XF1qp24TdV6wcvrdi9Qjii1ln9woe7Yyrt5mbn2CRFumaeuXKpZFq4'
        b'X/6gHiVvriv+7MiyzUfLfvpuZ32/b49e//jSEt92euQC75bCNw5/Iij/jfvzw6V3w2eI3cle8BQ00b/UhUFHDqgmu8xW8DAzJ+2Hm3sTO4HEgPnwZV88J52kwRZQxSPi'
        b'RRk8iV6mwSjeBzRh8cIXHmdm82qk87cwhpIu8FQAY/kJdnmTWTgD/bwOz7CBzglYJ8XenzGwP5wLjsK1iSQDMVwbCrb6YT9aGLK/BokSS+mB8Dy4RCZpH9TIaswJYtYU'
        b'rAvAgthYuFHNaIqaYFwQPy7FXewCj3LAnkywg5RyKawvB02gzcR6JcQaNpBSDgTL0lAhz4GtSSy5F5IEOJRbOs8T6bQMz1MIasq1KHWwDRWAdVOAQvQsXlzQ4ga2MKLg'
        b'S/NcRnkY27o6455AchEmB+H79/c2I7QsZEEG8HRAusGXglVMBiM/pMSRMhQUIvELiTQXwZ7OMg2SVg+QfAah2eEUljLOwpNT/IcOxcvX2JdCMxduSodHSRwXNLKtBetS'
        b'clhbWRND2VGTybP0WALJq4PVcVYUr7wfzQG7QX0u+a1AJmRtBMCOnjGsE4MENzVBYG+FlYQ/ClTPMLZI6GSOABtnkxbYF0XA/pawdBoNDuoF1BnwoBrbNCnhEfTu1mH3'
        b'F52FNLBrEJbTYB2oIa1p0Sy4jLXIVYMWg4iVO4DYIrvDl+BOxqWSL6xBxSUelXqW6owburVlxsNWfUTMyjERs4RKHkdIE58JSBzCQpYr+rihjzv64HMHFNLknybikgvj'
        b'YQF9eLf4fXhf2/YV0LYcW9qVI3hqy8VmEgIaA86QIONgEGRw9kaGb12U2WAHdwoFdzvLTK7m9lU7ZIXqBssn6KuWfCWiI4wDEvfqABYjxr7KxTggBsDEMhgbBWsFOuNQ'
        b'3RHeeGJMKglKDBttEQsOsqFPtoDJRqBWmJkcnhKekJk2MzkqVctVydRaHvY/oLVjf0iNSkslAiF5QkbW/Ps+MpSYys4fV9cZCu9xOXFp5+cFhTlYoX97V76TQGDNvGM+'
        b'MX3hd/jwHtDOPNbLhq2Rlw0Bn/6VZ03/IhDQTwQ29M8CW/qxwI5+JBDS7QJ7+ieBA/1Q4Eg/EDjR9wXO9D2+C0rtR/5dB18HlL+7lXskWcdCDf6Ct/F8YEUlwB1OadxZ'
        b'aORf32krW0dso5rYkbaXV+dI6Gwddd9SWn/E3WBtw5MORuIzBm845vCk1lKBnsLXRmpLoDtClsLXnpw7kHNM4etIzp3IuYBQ/NoSil8hS+Hbg5y7knNbQvFrSyh+hSyF'
        b'by9y7k7OhXU8qRcul7T3LrqOj8E58+2lHr2pPQ4YfsKee+rOe6H/Jk41R+rNwtqtiUspu1WOq5xybAgRMCHmRb/ZEJpdHoH9CGY54fqQDtjAWcWoDcJV9khpGCgdRCh4'
        b'naV9iPHwEJaCNy4x6tctJgjwNB0tLPqJ4d8V+WCuFMyJJSmU4l4i78jeaXLim4aB6CwNFjoqylIVKTCJN8bPY9/GDA8p9q0sK1Yz7r0JmL6Dy2klNmMVW2ttWD43zHrE'
        b'HpLNZQHjbhXzH0lzFmi5+YXoWoFMKtcUoGuCYlTyhUVKqdJAAmyWfdfUeZfOg7oNUrds2R1jO73zru7y7+aJuV8+6Db/Lq7ov8y/+2z63U5Uu2b9CPxF+l2jF6IvB/bB'
        b'3kUp0M+WylAokiiK8yQB5ooyWpSdh7LMJp7Ou2YD7poM2Azx73PUyDPJgFFbZJxCR0ZPFykkWZh9Hh0a+9kWD+3gwZqhrzNbCtOik7r1CTaqCjOFZwuC+sMzqIgt0Q6b'
        b'dzRhiYq4m7TDZhM1UBH/DdphXZ9nqp05E8ml7AsLedYL0w0UrCdw9kyklOXKVaiG0QCFxjHSnPxFGva1aQqxR+6/xO7ryKy0jOrhTF3xjMCGCEKbiBSKuFD2d/Mwx3Q7'
        b'xSD8WxebEPCunCh08gomCfZY6kq5DkjDW/VjBwYGUZqJWAKcgFcEu0qRUNtMASeRCG1ItqFYCJvACcAQyGwcY0+1JAZTVPI8/3cHj2cZg2sje5tN2UgHMS4qOANXgYtg'
        b'tR1ohAcdSLpzF1pTg0v6YdMJ4c0QLqUZgS5OmQ/WmE03xi/VkBxSiWrw8naNDdgMllmR5Mq4NtRg4QCyse3FW8QW8yJ80dY8e7BB7zMtJ1gGtoNTdmBf8ASS7jvlttSh'
        b'6QF420fRuySA0mDzJ7gVbio3l66PTrMxSfTcEF9w2A6uhhcWyZesf4enWo+l3kPtAVfO29PhwqipS/6cu/rQMg+fCjdB6I3XaU7vvbR3Se/3xUUtNkdUDQXHpB+dPf5W'
        b'9PT4fmfqGr7TlB6verf/qXELJa/Zn47+xHnLjcvjr5S1e+99Ky8xb+3IBzuX8t6723vul7mlqvdabzbc+T3t4uv7lyujzpZev33wdvXJu1+MfLL0Sdk2nzlTjpZvvRP6'
        b'x5e5YnZxegPcihfljdVNL7ifaJwFcBtZTPZy5Bovg9NJ8DSzDD4SHiDa4KB0WKlPghfLNjIrzDXMgy/HgzaSVRTc2YslKCbNpYFjrLVuIlrnKHAEnDYGxYMKWQhqRaeJ'
        b'rhcPD2D1i9Gr4fYQoliP9ibqVPw0uMGgI8LNxVhJnAU2MxjKKvgy3Id/1rWBC0jP1Ov/80RMXZybgq3iA5kXCqrgNoO6Og+sIyrlfD8nRoINgMfhKRVZ0YjJBY3YAToW'
        b'aQP4VAKotAb1GlD9j6kAeoQldhphUPKococIBxZhqWMUtmV5hY3P9PzCSO4wzy/8Kg5ewwHAAcTB6zh4AweXKerZxDuC7iRib/JIYq7OOL/C8BGZWzrvXPznAyLqRSeL'
        b'sLlpqCwMKNOQlxHNML7UBc1w93GZuTrWVyM5ymKh0nWF+rVfhxIQqeAvk/uyMpPFfDP0+fZn8v179MYsTpKXiSQli3nO1efpyeRpJE39tQflZSKByGJ+En1+PgaRSdIR'
        b'/Pr8FMp6UKhOSLFYAqm+BB54kcNIjvmL/NE2mXoVyFKeuSZ5olrWSz9GeYppBj9NFk309raJ2VyjomBDdtyHicEttjMlu1XYQwXNKq62xA+yMEeoN2u36i5e4ZGVS7dp'
        b'qGSYfbO7LFQk8vOQUBmTTnVKEpNQ6SHOvv4iX2OsNTon8G0UyZhCh0i2TDEwM0n3tT99RmGi1KICrEMwCjd2HscCpiVZRRo1y+2kQtKqpbrBf5hHRYarRCrPISw7alYa'
        b'N30otr6JY0xUbbmsazwzgjD+i9GzQkm6UuyGhRqpMyIfHfWMZcXGuF4Zob1TRxX5hGcpZdl5hZj1htXyiIM8swU1tAOVSp5bSJoCwy3TieBMJZIbP5UcKTy5FghsdIrM'
        b'MPKSQ0fr9Rmc0zCxP14i0REk4xh6huRsSyoYaZVycj/m2cJ1N2p093m6ckwfCD+1XKb651i2fDCrFOHDEot8fQuwko0eZ5Gv71/m3RL5EI6tAIaq6nmS7oJjq1v3Py/j'
        b'lcgCU5clxquh3SuGCRKkS94rHz3v1TCxKGNYsGXeKmM0CfsaNTLmceSFpKCEzD4yIWHmTPxk5hzl4r9iyaIC4mZXpsTTlD8htdPrxkYFCu66QF2ScZmulDC9JVDXU8wW'
        b'ixGGjCm8UPYhQZbZ2IyxN7p1I6Nugq6iHlmokjOFKsoxT24mnY9aBqkPfAPxNSwpxcfd5HXCf+EmiajIkpk8O08tJ+RdKgO1XOc+azHNANEwTJUt06DBVZ8AasFyEVtF'
        b'aIQqQD0ualpAmkSdJcPLkOapxgJEqLkw3lAVmoJ8WZ75+g8QhXSIRnKTaHIWa9QyNHNgn9Oi6UVKFSmUhTSGh4nCNTl5siwN7nrohnCNugjPb/kWbhgRJooplMoXyFFj'
        b'VijQDQwBnqrDk1u4O9RckZ+/gkaaS0ZuVKyC5yvWKHPpPV+9jCYVaaj6Z9S82YtpTEvG64Udyv3cLdH48XOU6Gl8cN3qyyTJWqzJFVtufsa3i0Z6WW6AJhGHjbYUEzWz'
        b'wsDO3KLMjyM6JhNqKZnQrpJBjUL/fF2kMco4msVHG22SmJnnsjihsdhANMKxR0QeQDIpGlt1Q7lPKjPHWpywDdBDTHWPpkLmDMk4PnHoVFaI/lEzF+E5aJRlvk0DaNE0'
        b'meAOyQR3mQzBN5oQMPoQ1sVIPN+MsHibHg/J3Bo1jYzU+ILIB3Vytomj1265GjRKTESJZotJ7JG/yEi2i5qWIvKZAZvylKiTorIMt1wUIyimITH9ZbZQuqRU+RqlqnOh'
        b'uhL3LImXRJTsvuSnF9HCTZb+uyfDEHBpmCgRf4kygoPmdP+2YOa2YHKb5behQ62yIiR7jlXnrtoBgbSiW/AXitg5nuVRbIpMqSwMjFZKNChQDA2MliPpzvKoRaJbHqtw'
        b'OpbHJ5yB5QGqq5zRqBSVh4QwNPZbHppI2ZDMJjVfDEuVh6RYmUyNJQv8jQSs0C7lu6yi0jAR3kVG8lMOllrRBVTnll8qvgljhZm7JAoRPunyjmy5GndIFHYp7jEAaRyT'
        b'OSAJ+2M5PSBkWGgoammWy4SxyahA+KvLFpkjQU8bjQaVriIRdDN6Q/hLlBFqOSI7zOk4Zrto0TrcdZgoAh0xknBG8Mgu4+u7NrnFdGuvy/rWobnZO5n3Y3mwxhhuJKJF'
        b'hCei12N5RMySZ6MEYyahrM30yE4IbLyBb3Z7LS6Tpnh5eSjOvPiawhiK2JmWzHKLA9XZOipKPXCuGTSTm/L8eJQg7RaHmjhP2GuyHcuXBTcXxsUQMF86XIHxfA5LSew7'
        b'Q3tR/ulpPIz8TbJeyEDswArVWALxmwNWDqWGwi1wGzHv9ZODHRhht3mGDu5FANJTM0hSpYoXOE8i1ltTQRJPX5mIYghDUMF8/VBcTKuYhA0LQUtsAvaWBA8OiEmj4DGw'
        b'LoUqHW6T209CwEQnkpLotIANDItkeq8sR0qDQfrw7FjYoNuqMnaLFKOGW/xj0qYwOxUmJJIbwHahWDCHLBfKY6bZcVVadGQT8x9N9WuJYJ5TZe7jp5+mTMy+8IDaNXZx'
        b'8Jfi+1/YKYZHLG8KddpxbcW/pWfbe7/6ZE/hd9c/vfvuyOPZN/i3an29x7guvPxzc9WggBFXR63YkCG+7aaQvlU8Ne9hQMiuPd9tP6L+9p6d8M5a+9DTO+Z80G/sj3Mn'
        b'73ZLVPY7kc5/J2NpW9XVm6q89A8fTrtx7JNZ15ICNAWXLmzJmukd9t1bd96e98s61YTZ4OnoVFXFEEXhwLfb70cPj0i76n2y3eHRH5Me39h3rl9e0Zbv2v+d8WfboM8O'
        b'l77+xmd/3Hv30p/U8c0Rfyz5H7GA8Yd8ETQO8Rs6F6wydqUMzsGNjL/Qmtlgu46icBisxuARuA1UECNPuG1yqR9cUxaVFANaeBRfQQ8EjXYMZUcFqIPnjDbNBoLlOh9M'
        b'TiVqzKQwsWA83kiK9DDdSuq0j+QiI2Qh8LwYbsYOmFjvS+CQqQOm8fA4Q8G1VcjR0xiCtniGNJJhMYwOJ246hoAG0BgXH8Oh6BS4Clzi+E6G6zqDPoT/kKNzbBFHNq+i'
        b'cR8uN/4IkjAMBPvTG0wgHYyDHmJ3SDauaI4H+RYso5/SdB/98WKhfo9Gj+pg3X4YFq6xJbfRrpXNc5VfzDNKhKRpivmYb27rauBGM1tXJkW1DPog3p2wHRK1iqf37tRd'
        b'54uV6O2VoARMRkv8GP07jZZezGjpFaujis5Kf7l/AYNI4JbAteWwWaWZOiIIw1hRs+KUgfPwgAEUApbPGDkG7rdDF2ZQM8BpWMl4uqifD7alMneBLSoOPE/BE/ngNMnr'
        b'kXsZBnaktyYcCFpND2CGzQx4Ah4sgatDdPiN2dbEdcVguC7DLSBEB/cYuJhJYi7LMpyzIcojnsvgL+YmEEzHqKDpjz1KF1sxBv0N+ezFBZm2LvN8mZiyWQS+4RPkDfiD'
        b'BY5MTNul7EX+Q1GhTSoTMz+ZwDcEQaETwsSiECZmZhZ70XtmzP3hZcxFXzs+S3ycl/wo3Z/x+AFPoaFjbWpycjJFjYO1nEgKVIAWuJLMK9HFY0KCgoIoauoSDmxCY4Qt'
        b'WM94Q6gH6+GZ1GRqOryAUXsH0G+ePgy2f2UM3APWixigiB4lAneBSgbesCs5ECUKzsp5FIMS2QCOkoqUwUbQUOqJt4qwl3w0XuD3J4IvwWPwlfIQHkHplMHtJDLYA/al'
        b'jB0PN3EI5GNuIONL4ZWoOAO4AyNQOATdMQtuYZ52G2hxSE0WcQlH4FlwvCcfNI6Dy8mP3iOXgvN5pj716dixYxjsBa7r+R42GAUUFDR9vP+QyOFMtdrMFjAXF5RHDk9N'
        b'YOfYs/6lqFLhMczvCVdQkj5iksKmAT0pH9yK58oXCWJtmFYcAHaC/anJYI8Yw4fAtrAyO9gIt4NdjGuGlbNgo8o+JIhH2cCVNIaMXIRH5spXT5lKq7zQ438fyS2oPd0e'
        b'h2EeVbm7mhJ+jZ+144OHvj98yfM/y8lfMCHSdcB+ycqvW9e8qBRm3Mzr0/RVU6S/b9y13xt++OWbB7FesjTlkVPSTz7gjvuj7iXvI75/rl5YG5k2rDRm/8HNU6cPr3uc'
        b'cm7IO5dX5L7wRNDn6nzPPT8fWJvR/tOYypP/0k5KE384WVpvm1BZIROGfz4/KoIfER1x2frmWf+edvWC+j/3warYfq8H/Pj77tqvA7dpfu370wWnEcHZu9LvPjl4P3Dq'
        b'pi3ZV9NGvdHU/P4vVgXfiCUVrnGjD54cUpS1nVNR//2w5T1dWo6flG364kqb7MCcStVX+WvirqX9fi7mrUvb24sHJG4tcDwTFtxzxr/77Dzw0ob7J+rvffnKu2BC/4Al'
        b'tWU33hz6be1ehWNFRAn9fqzYVY0dGcTBSy+gSQy94PMxz5jG0hcT+44cDVjVG7b6kZkR/SiA52lQC/aMJQjPoXLwIhJ+4jlUbDlvAAfUq+eSmTYMXhyboTC4CcROAgPT'
        b'GT7Jo2nglAETAhrgToYsoQpcYkw/KqTcjp4O4LrxrtaUKMrKJgu0MnJAGzyhYC1LMDqDS0xLwHFwkMgBw+CFIgzY0IAqA2YDntcQsxHs76HByILmAtymB22I4Q4G2tIa'
        b'BirB4VhHuM0YWgL2go1k2n7BDxw02MZwU4wAHfDkEjJtl3viFIgoEjaWwFj9YTUz56+QoCGkVhFnAudwACu4EfDoWJJ/5hSwwxNVrgHQwcA55oGXGUqdemxgBdbA5jhj'
        b'PIdDGTcyPJJ5ysPgNOpOjHUMWA/2GIM5HAaR95TgNVxvgjMtmYctcOTwMMNFCfeBkzmg0oSZgi5ySSC0nO5gHYY468xzdoF9xvAcThpxEOgFtmA4UZKJJVsQaNDZGc2Z'
        b'asE05RkeAwkTDJFQFnSSUHjFPFYSEXKcaAGZ3p1Y0CpGUzgRPAVNSJNp/ceArCB4itt8T/4t2z5IuqEZpIUTscDH1vm8JwIbwc88W5YBjYgJnbjVzJe/A8saV8fjVmH8'
        b'cdlqkW3NOC8VFh7+q1RrSk1H+cQ8z5h1ooZ4A97NccTMV2uSbeBWizRjeaCBDPmoWZyL4jkw1GE64jBwATaRyQ1W9oSVhDoM7i6lSqclMx4zViCJ/wghDkuBe5MpuMPJ'
        b'W37tUJ2VChs7vLfSfVzCGFsw0an+vehNeTy7pHm5uQV+bqfcBuadjmp1yuLt/OxywYGfbM+P1IRyFgkvbF/U/8sxka6bWjNjb9f9ovLqs0gamD3sC+v9q6Nox6ybg8N3'
        b'zfrgXuJH+TNFrZOtj8W3rsoo80ra3ffy27VfRQo+iz4dxlm+socw4Xjjoz0JP11x+vPPR9/28lBvcJ+8psWmveBCiffQ4amPct8JXvuqoEZpV/bbtfzLUQfH3OaqD7z0'
        b'B8fhTGifhw/EjqQTjuuDpJCavqT2WM6wOZDB5/vB87bGlGFIwXwZNNFl9ipG2zkTBA7pWcF8evET6T5orGogA21/uMOaIQWDZ3sbk4LBTWVkFOoDK8EuhnMMLAOXjFnH'
        b'wDYFGWXAUSROVBLisNlgrzFv2BrYSgofkrlYTxoWTPMxZdhWwJD7gjZQD1cS37fwAFhtxBuWmxjHlL8eHE3Sk4ZlwGbM0QgvxpPbS5DUtJkwdMFGKwNvGFgJXwFVxLpw'
        b'mg+8qGcNg+vBPv5YuldQbwYNdwqecTOiDXOdkkqDRrB1AjN7tMLzKCE9b9h8sJYfQbuD/e7M4L8KvZFjoMWpA6EPrCtmyl0N68BLOvawSfF8zB62AFb+I+xhhOKKjG5B'
        b'nUY3qnxgQLcIxPBYoScQUy6kuoZ6lZrk3R9dUw3uNDJRFW6fWiQM0+WHhj5TMAdzynr5xseJYpeO0K9FFGWM/3qVeqZZ4jmKOPVWywpUDICrAzeY899Shbvxjl5BwQA8'
        b'gqdTDBmYE19IqLvcntLiv0YFJuTheYb3lPdUxHVZKBjDkn8VLwUnCPdXqJCIa1aUvQcNN7mCC2JOovxWXyQF90JScHNpZVT1mMIVE5EM3Kv1tU/cgxyzf/iC23Tf+YNb'
        b'lFhZkTl8S8rgtKk3pLV85Z0rWXV5O+uL/vyf31vGB04az4sOn1NfM/m3VUen5GR/kbtj52/Cj9saK3K950wuPxcVnb6F9/St4Ktz6n+OOyja/vmdzf+hox7bf5OYLavb'
        b'v/Ce+/3lk6pL/zXs4IWv1tuNL/mwSnDs7h9Xl3hfHwJUj2c5ekZerHnzW8+3bjdO+2Sgm0t5bUn0iOO85lZ11vCPImIWuwZe33rinY+2XCkbfe/sTW7/61+l7pSsir+w'
        b'/Wr0Z64PJXPeP1TydbLSrq4s6NzGg17fPL29K27BG32zamJvbL66L+SRNjr3bnxOwYD5n4odxp+2cTj0RmrSBo/2iPDf7OgZ0h53i8VcIqfOn4+UqHVIPOFkzhqFu+/Z'
        b'3mSMiYAbNcyiTw7SgowpZMbBVcwyThsSblaw6ziqrE5+tGfD7Z1XYjz/O83vuQM06HD1fdBcQCCpgsxMRZFEmplJBp2hePTxoOnhHBFe4HnKp/ECj8jDw9XV13UCPSSM'
        b'QxaCxjpwve2ocnrBKI7yE32/42rpzEyjNRyP/wd1wFFe13dbXFLcqYgL4onfmiEqw61iEmh0RPJtDRr51yTFgzXoqHm8NeXQm9vXdZK8rc8UjqoGRet3QNp3zWgHEORq'
        b'9fTnu04TpyjWTswa7TKjNeV6X9kHUYt/z6jc6TL7nfXeJXvjB9kP/ymjbNHXFbn1H91cK/7j5TsbnTPlXv4fXe8ZmNbwVmPkMa/VhwtUqdP3xvrN/vSW5vpqCV3RuMdZ'
        b'8v6elSuh25gfSl51HrLr6mtfLfejC898VZH7uVcDcI0sb193s50rKPZ5vGQHkiaw2P8CbIbYpc+aJLwgjfmJ7WBlBGij4SGkL+xg2EBrnJ3jkgJQn0CxkgKcwQHsGegC'
        b'9oAzgfQLtTtq9aQGiONPpCG6j0EV4MLtBzYFkx41SB4QF5OMfvRNsKb4PFqgzlcTKa0ebp4G1wVaocmc4qRScJ/LNDVxBNHmC2v9YnuEWVGcOApumx1IptrBSBncROjt'
        b'UFoYcm2nsBbT8EW4PYLRc6oDYJXK6HdbNHMvj6FB60R4lKQQNhbUxBFtFqtJ8HCmFeUA13IT4Xk5s+p70hkewBHgJYp199cTiUhYApqOpvETRASdwkpYaIwd14OGJ5Dg'
        b's4JZGH4F6Vg7kaaz1r+YjWPbYxw4ToMTcIOceBkAJ8F+EqVNCFYvLNHA4yXCEo0S7uFQvWANF6ley5FOhROzAadS44i/BPxAFIXXOZrADhruha3gCBlv8sFR7OCoJjAO'
        b'DTPV6NdleEEYX7GmPAfzwIre40y8Iff9v+9hHTuczTMGHTNjkAEwgf1nCext9a7+se4m5IzndpSDeIMZiYEMO/21XIWsUMvDBrpaK7WmWCHT8hRylVrLw9qSlldUjH7m'
        b'qtRKrRVhidfysoqKFFquvFCttcpBox/6UuL9fMwUUqxRa7nZeUott0gp1fJz5Aq1DJ0USIq13MXyYq2VRJUtl2u5ebJSFAUlbytX6cChWn6xJkshz9ZaM9hZldZOlSfP'
        b'UWfKlMoipda+WKJUyTLlqiJscqi11xRm50nkhTJppqw0W2uTmamSodJnZmr5jImekTd7mnnbj/DxAxz8gIObOPgSB5jGTfkfHHyHg69x8CMObuMAE5cq7+EA7xIpP8PB'
        b'HRzcxcHnOPgWB5gDTnkfB7dw8BAHX+DgBg4+xUE7Dh7j4HuT12erG1cjn3QeV0mMXwU52Bo3O2+o1ikzkz1m555fPdhzUbEkO1+SK2NxyBKpTJooFhAZERPKShQKllCW'
        b'SJFaW1TvSrUKE3Rr+YqibIlCpRWmYMPAAlkUrnPlE13tdTCv1wrGFhRJNQrZeLzGT3wb8CietYDu2NRcR9KkKf4vVCIbQw=='
    ))))
