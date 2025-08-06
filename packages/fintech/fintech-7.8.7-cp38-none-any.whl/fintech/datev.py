
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
        b'eJzsvQdYW9f5MH7v1UCA2B7gKW8ESGwMxnaMjW1ALBuv4AFCEiBbSFgD23jENmDAgBd4722898Zuzkkz+ms60pGWjF+zZ5O26UjcNPnec64kJEtykrbP8//+z/NZ5kpn'
        b'r/e867zvue8wj/0TwN8U+LNMhIeWKWWqmFJWy2q5RqaU0wmOCLWCo6x5tFaoEzUwy8QW5UJOJ9aKGtiNrM5PxzWwLKMVlzD+jXK/R2sDsrPmTJ8nqzFpbQadzFQps1br'
        b'ZMWrrNUmo2yG3mjVaapltWrNMnWVThkQMKdab3Hk1eoq9UadRVZpM2qsepPRIlMbtTKNQW2x6CwBVpNMY9aprToZ34BWbVXLdCs11WpjlU5WqTfoLMoAzRCXYQ2Hv6Hw'
        b'F0iGVg2PZqaZbeaaBc3CZlGzuNmvWdLs3xzQHNgsbQ5qDm4OaQ5tDmsOb45o7tfcv3lA88DmyOao5kHNg5uHVA6l0yFZO7SFaWDWDqsPWDO0gZnPHONKmDXDGhiWWTd0'
        b'3bAFMHkwDdVyQaHGdX45+BsEfxGkI0I6xyWMPLDQIIHfLWqOmZgQAr/KpW1D/RnbGPiJH6Bjk3Ebbi3Kn4VbcEcRvjdajjty5xYrxMy46UL8EN0NlrM2MtwR+CbqseQW'
        b'4C24vQC3s3GrmIBcDl3GLeiGnLMNhCzoOL6MT6py43JFjFCIWpNYdNiID9gGk6ZOmmeSFAVuhfIiJhhvRndQk6DQvwpKk/nLz12H2vDmuFroUHuuqAgdZwLQNQ5dR+vR'
        b'etsoyCGGMvfN+ApkuypFLSuW2/C15dLlNpYZiLcKUDu6tQg6OxJyTgoVoDa0NV6liCH9xVtR2yo/tNWPGTxaiBpg2Hc07GOQOdgxc1qyhPwCMj9sCSsH25ePbQEIXsvB'
        b'8rHO5ePo8rHrOPvyVT2+fKQTAzyWbzi/fDdKxIwUtk/RqPL8vy5cztDIlMkcAxmjzUy5IaOolo+cGOHPhDJM+lemculN6Uw+siVPxMB3jt+McunEiqFMN2MIgOiPJ0YJ'
        b'/xrOTPnTtEHRf+FuJmaNe44x+EOCcu5e9rIfI/tT4Nqk15OWcMF89InpX4R0hbDRv9D9i/1mwY0APdPL2BRk5W/iphJYt7b4WdHReHN8jgKWqntOdF4B3hqnzI3ChxR5'
        b'BSxjDPGfFJvhMfWBjlFn81PvvnMYMvGVgc6p5b5zar3uDLHH1EoLzaR1Wz94RCbgrSWzFfM4ZhE+zQkYfHB+iY1kR8fQDdxaAjWgA+JRzKjV6KwtDOLj8L5B+JyyZDak'
        b'VDPTw6fSWLx3Tg7uhFozV8cz8VWo1RZOYrf0R6dxJww7ZKWCUaAHE21koaPQDtRRUjALd4iYQHyQW80OEaIHtrGkxCZ8sozsg1gVQG9r/qxo1B0XmZ1DN6YSd4vQRgna'
        b'T3u+AJ/Eh9A1GB7a4TeRmYi24LP64pcvcpb9ZHAZBxa/nBiMEqRN6tdyS5u7S0KejYrcu+BpddaAwJJzWz6aGqM1/rJ2x7AO4egTSau+fDN+2YUhf34psVnQda/5C/Ox'
        b'sBnS6Np31sWeGVLut/j43Cl/2/6oofhHUT9uKfg1+sniv7c9Wr/8jaebYnWr1yheLTybfS6o8pnu+fMHPDOp+6u/qr7Jn336cPCMBeNPVo94e+i9GV8bdkYMe7bI9NGI'
        b'jKB5i+Ui6wgywbfQJXRHhTticUeBIo/gDnwYXQzHtwW4GR1GPVayM5WoC7fF5ilwSy7ajM7kF8KUoSscPhg5nabj3dX4YKxSnofP9ou1o5gQvF5gkkZYCfaaOgQfCYQ5'
        b'zLEBRtgczzFJwWH4rgBdWImPWwnSRN016CTM+Ga8FbcLmJg0YQaLruANqFvO9XLRcjMBG3kg/fo3HgQCHw2YWGk21euMQEYogVICcdHVTe4NMuuMWp25zKzTmMxaktUi'
        b'I2A7WcKGshI2AD4D4C8YPuQ7HL5DuXDWLHbULBf0ivnCvX5lZWabsaysN7CsTGPQqY222rKyf7vfctbsR36LyIM09xTpXDDpHJZxYpZjA+jTRlYyKQ+dj83DHapcBdoc'
        b'D1t/SwZqjc9jmTHoiqhsJrrhtifJP6H9m5JNHeEGgBPQsqUC+BPqmVIRfIu1XKmfNriZqWS1Qq2o0b9UQn+LtX6NklJ/+lui9YffATzhrRRoA7SBEA6EMKASCEu1QRCW'
        b'alnKPYT0imfTySqkk/fRN7AxNQKXbpHR+jnQRQrjoOhQEY+DBC0CwEFCwEECJw4SUhwkWCe046BKbzhI4IGDhDx6f9oE+FnykpiZUh5XG1nI6EuPNQstRZCy5dMRn5T/'
        b'tOLD8h3aFvXH5e1V53UfQrj0R4vw5W2JTbMOHN0V9lyR+ozaIDrLni3/iXB73FDpdOXQ9sAFmeuzWz+OjJoduTEq/VdM7Quha08UysXW4RQjoUtPxwJ1BJg/zFPIWDET'
        b'gk4J6vFpdJNuqVLcivbFOiloP7xDwEjjBH71eJc1CtLXWfAeFW7LB35BLmYkaHMa3sStRPvyrZQXOMbhhwSDqXLRBYYJKxSnc1Gp6+heM6Fr6aitCLgBIYOvoYMifIDF'
        b'd1EjvswXPSPpF6vIoWyEBF8fgzdzqHFdjZxzgUuBtw1GwbRXUlamN+qtZWV0I0nJ3JeGsuQjZoVsfQi/9kpHLn4DiXqFFp2hsldI+L1evzqd2QKsoZmsjZlQvm7W0S4B'
        b'fnMQeYQ4dwZpZKFzZ5wOddkZHu1puMc2gBPSkuyQVsnZ4YyjtE4AcMY54UxA4YxbJ/DFRjA+4MwWA79HrMOXA3EHrMsWoNVA8nL4BZxVTGnfU6gHEo+Kw1Ln6W8ssgks'
        b'CVBmw8Z9n5QTmHuxMj48Vp2v/rT81T+EaqorDRXCzYmK8s/KF7wY+dMf7RUzhx9KVi39s1zII9QH+ECxC3zgHdFoM7dSAdBFOLRpY1LwNYCwo3gjYNytSkWtHTEPWidE'
        b'TbgHd1Eg045DFxygMhOfs0PKJXzRSggr2lhjURUpsnA3y3B1bFZqBr+anFfAAIxYpbPqrboaO2wQhMZUBLBStj7cuUrOLHxVQrrWvUKjukbXBw7mUL6ZcCcwUDggLIDG'
        b'CQeHg13hwEsL/3Wk48H4PBEYlq5Bu54EDPiocp44DNjl4/pN4e+xFD6RUPM4MIS+1kqB4dNybnOSLeF3CScShMm1pwTMhaWSsooP5AK6kEK0Dd9wQxcm3MqtrAuj+Khq'
        b'YgaBBgckDMc3XYBhzQRaA25ToRsOWCCAYEM7ABa6VtlJoG+MAAtv8Vz4qscW3uK+8CJ+XckK94rq1Aabx/ILXJa/nxMGyFRXO2FgX6h3GHA25hsdpPEwQJhhtlL4A1CC'
        b'B+lh7VW7Q4Go0Ea2N7reH98lktkc3KJQKGfl5M3FLUUlhOHMmZsDvKeSBcnqPmPFPf5ivHeSTQ6FZqP2tU8GncE54jB80ay/aGlnLYVkun+R9En5xwA7hsqYATHqHLWB'
        b'wkytumXnWd0Z9YflP6v4KYWpPPVZdaiGeWnAZnb63oGXrQlxWq12w9YctaTyDz9lmNSKkIPndwPzSOnY9jq8x5Wvw6fmMDxjB+LqFoqI5CJ8zQ3wZOgM0KlG1GIlQiVu'
        b'QgfQdif04Su43R0XjR5Ewc8fdaCHAH6Q4IRAfHcIumyNhNQV6PQIF5qlRJuAZqG2QXI73RD65Ap5EBXbagkz2EeyDAHA+Uko11cfZAcbPo8rXuKpkRMuPTYBoKg+ekXB'
        b'sz88apzguTPcFTzd2/EQ09yxE5WPndiJbWG/UyxrfBwuhV7hUlCoH5AiEljyIKLlwiWVOqfqUwCbn1RUV/ZTnxFdiRyYoNASsLn6Uav6rO68jntJUX5RvejFBf+zCM/B'
        b'xdiAi6N/8+wCwa/DgCoFM+LnQ2rHMg6qdBHvwBfc8VAxtxJfU1OeBx1eiW47cAw6gXfaCc4FdI0CAWrBHVrcFpeLO0AQA7nringJNwqfkfBCyFG0Bx/sY3rwxXmE6wHY'
        b'OuYdAJ6EtICRt1jNdoRFhHXGGgqsvxRAoj64D4+QLLRUt4BfZd/AADxMHxwQAdTmhIMONzT1WPVyrtBMRHR5EOGtCCEE8SKgrIzXp8FvaVnZcpvawKfwGFOiAQiqMplX'
        b'9UrsvJSF8ku94kq9zqC1UJaJ0kuKMClY0j45kO8TJSl+CGRSSsgQCPKVcELW/uGCJVKRVBQqoVL2kEq8P5AII/F5xcUsI5Fy5eh2gW9RRMk8JopwpUKtgIgeB7hSURej'
        b'FR8B0eMo28CCWCKhYO3fK55uBHy+6lG/bF2F3moCeS5eZdZp+Z8f8czCR6SJR+HzdOZ6W5WlVm2zaKrVBp0sGZLIeB5J83XWeqtONsOst1i7OTrnHz0P4/3bXphTlclo'
        b'NWUWwhzLorO0Zp3FAjNstK6qlc0FYdJs1FXX6IzyTJeApUpXBU+r2qj1Ws6otuL7ZoNSVgwrZIKy80xm4/fJ562yZTq9USfLMlapK3TyTLe0TJXNXF+hq9fpNdVGm7Eq'
        b'c/pcRT7pFHzPLbEqckEQU2ZmGWHCdJlzgCwa4rOWqbVK2UyzWgtV6QwWQiwNtF2jpc5khprrHW2YrZklVrMaH9ZlFpss1kq1ppr+MOj01np1tSGzCHLQ5mDmLfBdb3Mp'
        b'7ghUrCC9I2K4zN4RiFLKSm0WaNjg0nlZos+UpEyVzmisV8pUJjPUXWuC2oz1atqOzt6eTjYT3zdY9VWyOpPRI65Cb8mcozPoKiFtqg4YzmWk3mh7lNyRJpupA9jBJyqt'
        b'FjJKMqWeuWUz8+WZ0xUFar3BNZWPkWfm8nBidU1zxMkzZ6hXuiZAUJ5ZAnsYOqlzTXDEyTOnqo3LHFMOc0SC7rNGYpYRGFYU2mqgAojKxyeI3mMZmTV++iEyd2pWIUnT'
        b'6cyVgCngZ8n83BlzFNNMsDb2yad7QW+sBlgj9dinPUdtq7UqSDuAciqU9jbtv93m3Vs8mXu3QSR5DCLJcxBJ3gaRxA8iqW8QSa6DSPIyiCRfg0hy6WySj0Ek+R5Esscg'
        b'kj0HkextEMn8IJL7BpHsOohkL4NI9jWIZJfOJvsYRLLvQaR4DCLFcxAp3gaRwg8ipW8QKa6DSPEyiBRfg0hx6WyKj0Gk+B5EqscgUj0HkeptEKn8IFL7BpHqOohUL4NI'
        b'9TWIVJfOpvoYRKrbIPo2Iuwns15Xqebx40yzDR+uNJlrADGrbATVGekYABvrQFZyBGrNgJAB+xkttWadproW8LUR4gEXW806K8kB6RU6tbkCJgqC2XrCL+gUPLnLslkI'
        b'QakHniFzPj5RbYZ5s1hoAwTr8TTWoK/RW2XRdtIrzyyF6Sb5KiDRWEXyzcAnDAZ9FdAoq0xvlM1RA110KVBC14CkFFP9rGtlfWRcUQq9AIQRTYq7JdjLQ9IYzwJJvgsk'
        b'eS2QLJtqtlkh2bMcTU/xXWGK1wpTfRdIpQUK1DxdpnMOfAnwJzTOqltpdf4ATOT8meya1eLMxi/EVB2Q4yqXiDGZpXojrAZZf9oOSaqHKEJ6AUu7BZPcg4B+1BYrUDuz'
        b'vtJKoKZSXQ39h0xGrRo6Y6wAsHWuuNWMT1QBEOUatfo6pWwGTz9cQ0luoWS3UIpbKNUtlOYWGu8WSncLZbi3nuAedO9Nont3Et37k+jeocRUL2yKLHq2fVYtdkZD3scY'
        b'eUu080rekhzsk680Jyrzkl7kvTXCd3mLd2PFfI/hCem+uLMfkjnJd8tufNr3yQao0ls2NxKQ5kEC0jxJQJo3EpDGk4C0Pmyc5koC0ryQgDRfJCDNBdWn+SABab7p2HiP'
        b'QYz3HMR4b4MYzw9ifN8gxrsOYryXQYz3NYjxLp0d72MQ430PIt1jEOmeg0j3Noh0fhDpfYNIdx1EupdBpPsaRLpLZ9N9DCLd9yAyPAaR4TmIDG+DyOAHkdE3iAzXQWR4'
        b'GUSGr0FkuHQ2w8cgMnwPAhCkh6yQ4EVYSPAqLSTYxYUEFzYlwU1gSPAmMST4FBkSXGWDBF9CQ4LbeOxdnGHW1WgtqwDL1ADetpgMdcBJZJZML85SUGpltZh1lUAEjYTm'
        b'eY1O8h6d7D06xXt0qvfoNO/R471Hp3uPzvAxnASC0JcZ8f3aSqvOIisqLiqxM3CEmFtqdSAP88xkHzF3iXWQb5eomboKfJ9Q+sfYhio+3s41OEJJbqHkzGK7csWlsIfa'
        b'JdEzKskzCsQcAxGK1VbCl8pKbFCdukYHZFRttVkIW8uPRlajNtqAvMiqdDyYAjn0pgaQuxTRE+Ku19Ji35nZS/1eiJL3uj0zUhVT3+zIgPmW2VleOpWVJN0+yfzvJJff'
        b'RCbs01Q9YjMLuyVmoh41ExWrmahC+aMRYnlhJrZdvSJLrUFvNQ9zavBC3XV5RJm/1k2XJ+BY7l9iEcdx33DJ3Ms2UnUQ2oeaLcRUpDUOdaM96JKQkaRx66pU/0V9XqXc'
        b'vzcgS6Mx2YxWkB96g6fCovNyh7pWZ/ioP6/NI9rwR4OyAQxqgLcg6lIZL/kAEOsB9UAWooXtFRIeyEyMev52HyLm1vAsjanaqJOVmAyG+BzASUaFqp5oWPqCfVguc76q'
        b'VMYXI5o0gj8teouNjyBprmF+180kij+ew+cbmjpXUaKpNuD7sPoG4Epcg5lTdQZdlZYMhP9pV7v0/U6yS0iZjpmgHD9hCXX2ze0Q22Q8W2QX/vrUVHaxjzLrROCDzLC9'
        b'rFQwsNdAmzPoIQP9pTdWmmQKWZbZ6uiKPSbXSEo+FkmyJXnLluSRLdlbtmSPbCnesqV4ZEv1li3VI1uat2xpHtnGe8s23iNburdswGUUlcxJhAgVvzCE29XRyCSPSAjI'
        b'CnSAMR26WJlNKevTxUIkD8sO5ahSRjh2h9zNK137llGWH5ufOcNmXEbNaXXmKkBR9QStkPipc2UpGTyhrXRkIUphb/F2uOGTvFSYWUoFAjJwc42aJDpBxFuKE1R8FUt6'
        b'UjHviTwIPaGY90QepJ5QzHsiD2JPKOY9kQe5JxTznsiD4BOKeU/kQfIJxbwnkmIZTyrmPZEud8IT19t7Ki34ZEDxDSmJTwQVH6m04BOBxUcqLfhEcPGRSgs+EWB8pNKC'
        b'TwQZH6m04BOBxkcqLfhEsPGRSgs+EXB8pNId/0TIgdQSK76vWQakawUQXytlTVfo9BZd5gwg8X3YD9Ch2mhQE+2iZam62gy1Vukgh1FH2KI+daOdchKEl2WrJIoxJ5Jz'
        b'0FJIIpi3jyDLorOM9TxLTE70ABkX6K1AGnVa4EDU1seSH8PDnoX7MPnjaWYDvmmxswluKTn0fKfSClyJU7CilERB+R2vUoB9pHZqDqQfKA1hoisp+1xDCLxVp4dpsTo1'
        b'xbnA61r1lfplalfsX0oFQacG2ZXN4MVHl5NEVzZpho6XLXT6CpKUD6tGjsYsPGfjm1Fz1Q5Dv6FltcFWs0xX7VBlUyJIuThi+lJojvHFxMbB475PJnYw956NsLmoFXXh'
        b'o5b8QrwlnrKyuF3lx/SvmFgklKKueA9OVurgZJey7pxsl7grsCtQy3VFdEXwHG2HnzauWdQc1BxRKdAGaqWN/sDVCnUibZA2uJHRhmhDO7hSMYTDaDichv0gHEHD/WhY'
        b'AuH+NDyAhv0hPJCGI2k4AMJRNDyIhgMhPJiGh9CwlPSgktMO1Q5rlJQG0V5GPPbx1w7vCNAqmjl7b4VamXYE7W0wP6qugC62kozMjz4dpUZ2+GuV1DBORF0xQqGsn3aU'
        b'djQtG6KNhzRRs4Q6aoTTtDHasY3+paEQGwZ9GqeNhj6FQRsRWnmHw9MguDmkUqSN0cY2SqCWcCoFVMkTeiXZxD57Wsm8R/EBMpd/jmgZj0J43yG3HN0iMzFyNI8mR/jU'
        b'TDue/KK2GUQUkEs/ItY1H1H7Y2Jb05fdPN6R3ZxOHokkCzF1+IjaAxBokPv1Bqi1dYCVzGV6ba+/BnCD0Up+Bqt5uaXMAMydtbpXorHBtjFqVvVKiPWpXm2wm2EEVuqB'
        b'nyurgS1bTdvuFUyfO5u38zBnwEMjcQHBAPsfNdSZyjzm4uTfLG4OaParDLDbAklaJA3MWv/6gDUSpy2QP7UFkqzzX8BoBdRSUfg34ifhNmvkXy7fTX29zkJdupxzraeW'
        b'DBqd0qOIR8QEEDfUNbK+KZpgd+YClEL0P3ZvMftcqY1WjxrIv+ipgAmsDjwkV8qySHnAGRoZNQeU2WplgDnHy7T6Kr3V4tkvezecq+O9F3yy9x44Tzm+ow+p39UHd7CY'
        b'IMun36QLM+PzHan2jlm894XQGYLhgT4oZXOqAecD9OtkFluFQaetgvF8r1p4ExJeOIWaZGqoAsJ8/2UGE9Afs1KWa5XV2EBEqdB5rUVtH3yFzrpCR055ZdFaXaXaZrDK'
        b'qS9fuu+1sG+HCbJp9l8yDVETRjsPF13Ui3JftTi20gQHtFqci0lcB01mWTRvqrIM3zfXg8DtqyK7adQEKl0RTgSq4WHEjlmidVVKWWpiQpxsfGKCz2pc9vIE2QwSkNEA'
        b'qa5Sb4RdA32UrdKpoWMxRt0KctJZl6ZMUSbGyD2n6nsYEEt5rwVWEcaUG6cxTG25wbjKytgmE/J2Ft9HTbitAJ0vxi25uEMVj1uL/cYTo9KcfDluiytUoM14a/6sHHQh'
        b'p7CgILeAZfB2dERqwg8CaL2Sp4KYv8YlM0xxuaFs5HzGNgki84ahzsdrpXXiLbg1HwgpaiWV4k1u9TaukjJoYzKt9q0af2Zl6CiGKS+P+0O2jaGeVlZ8Y7Sro1WOUhGT'
        b'hzsyUI8KXRQyaYvElmfQeuooRit5Tu/HfLo4imFk5fk9zAi+b09Nwse89Q23QKVtcVDvdOh8u3yeS9fQHXMgujoR3dEfaznIWFZDNSO+HDL0p6/5r0+QNr116tb1u5te'
        b'L+u8vVEgecUvPn5k4ZGRUdPG/y0yoPlH/yh5CfWEoR3ZuVPHLTn6Y9PLxrZJH8muFJ9eOnfo9ab6uf/48tUjkuiVwX+6fLtm/cy/Xd7SdPhM0DJcHf7N7V9qa9ap3r6y'
        b'6tHnebeUp5K/esQcmSn/rWiaXErdpCJQB96B2vr8JgVMyJikYYJK9EBrJcq7iOplqK3IdRlZZqZwEG4Q1s/GD61E1zc2fXWgCrdkwXgLHN5W/VGzUAKLvNUqgxzhGtRD'
        b'LGkvznRbO5YZMEIYmILarcRub8qsqbGKaHwQd+QoOEaM9nEK/GAYLY/OoIdoO9QAa4V3ofvE54gsVji6KMBtKwupF8moBfhkrFIeiI/jzcCYidF5Lhndr6Bmw0vQTbQT'
        b'tRFXLxgIt5h0ol0uZsLrBKhnQa01GvLgI/h2MBkr8GloExdv76V9eRkmATeJlfh6mpUQbfnT6DgZUVtcjJLkwh14ayzJVYVOySyiILQZbaZdx134QAXJSRi/+kUENBTQ'
        b'LtotwE34LOqmmQYLV9gbdmEQF4YOQreFqG0EbuRtJAP+TTe0PpcValpKus88w6wRs2LqbSa2+5wFw5N4nEk4kiJm68McpNjpylLo6Ag1KyWuYeYp5JFFHoRNME9jHH4y'
        b'xLXzSYbKEr5UXyVTnaVoJV48bj4i3ScsOLOe2TvM1YDVs6tuxsys/Y8aj5I+rWGW8obzbKGc7Q0s6+MczJHOaXPxMJpoUNdUaNWTw6CWL0iNLi060h7ZMbm9LgfVjwYK'
        b'oVWYjIZV8m62V6A1ab5X1xr5rgWUObkJbz0z58CjH5Q358KPR8P5HvBFvHTge7VcxbccUubOQ/hsfqCzefkTuYwf3JFqviP+ZQ4i7rMLg5xdiJqqtuicVP8HN1npaNLJ'
        b'PPtqcqizyVE+eYJ/r3FJmcMZzVfbsr62ffIR/95cS8tcxQRf7Y/qW/HvYD589MLNuYB6wXHNjNML7vu4Fni4vDiq9XAtOL5rmIh612b2/Jj3ZKqu/JT5ZfvL7W9Ln5Ue'
        b'iGImH/99j/C1vZvknJWX1vG+pRRhL5xJjp1cEXYpOsa7kDzAm/FFF5RdobEjbR5lD8V3n+SX5ldG9pSra9Iz8BlXH+qCxWgGvszAx2uKdK7G0/AYCzNrIadvgBXXM6+7'
        b'+aB51CgP6PWz70vebl9ssZp1OmuvpNZksRLWuFeo0VtX9frxeVb1iuvUVNIM1ACDbqrhJVCBVV3VKzIBtJs1gS4rQJB2sGMViD9Hc6BTcgxyOvkH87crVAbbFzywRQoL'
        b'LoUFD3QuuJQueOA6qV1+bAT58Q2RF/kxS6u1gIBAuFytroLsO/ivsRu+yXTUTP97iJBUwKHSiVpWbavSuQhtMDMWPQg9Mt6TgchfFp1VKSsCuPaohyCAGnLaoq+pNZmJ'
        b'rOkoplEbQYAhRUH4Mes0VsMqWcUqUsCjEnWdWm9QkyYpv0/MJi1KMlI90ZvB7rJXaZeZSJ0edUDVNoveWEV75KxGFkMXLeZ7zMgM+2iricLDs+8e+aOtanMVtKF1YCJS'
        b'XkY0gRYif1iW28jsVpjVmmU6q0U+4fuL9Ty8TpBluREU2UJ69rnYVzHS8gQZdV1Y+J0ODD5r4bfHBFkJ/ZYttJvT+czv2EYTZESPCUtFxc2FruZ0PsuSjQeCKjxlC4vM'
        b'Vt/5+K0JWfkftI04WW5JkSI5MS1NtpDoLn2W5vcziKBZcxS52bKF9gPBxbELXd0zfDfehwaIUM0HZKQiV6Ngn8UBccBkVsPWgO1q0Zj1tVY7/SJwSpyx6d7KMlhMAL86'
        b'rVd9AIATyU2ojYFe0UMXWynL5pUCdIuOLLGqa2qIX5txpE/1AN0MAFjQgVr71tLq6SVBapjWFXqgarqVsOL2DedZD/lXaLLq+G1CN7/OWm3SAiapstUAoEFf1MtgA8Km'
        b'0cHsaHQyE5B3r/XwQyKbhmo7LPww9RaXLillMwCpORCS11pctx3RjQCokyuQNAYYMH/7kUXnvWS5/QIkk4b2nD8qmVhttdZaJsTHr1ixgr++QqnVxWuNBt1KU008z2nG'
        b'q2tr4/Ww+CuV1dYaw6h4RxXxiQkJyUlJifHZiekJiSkpCSnpySmJCanjkzMml5d9hyaC0D5PZ8HwQnrfDz6KWvBOS74c3c/NUygLiYNeLOoGuW90iagaXcLr6fUsaDfe'
        b'GJAMPwavTGQS8eF5VKT/x2RyOc4ucvmCYccMK2Mj+k+8Dx9A3So7RTehxthZuIVcUZKnmE2cXGdHE4fR+SDhwxdQerQDXfLHO4fX08uS0Bm8B13H10C+JXIg3jXSjxHh'
        b'vZwUb0uzEYkrGiTCJnxNCdIk3j4ql7jSQuXkBhSOGY5OCvHdyU/biDAE4uslfJt4sLYXzMXbavPlruMrxi2FUKxdNbcWBFi8U1WUn4d3Chm8GW0MxCcW51CzGbQrFZ0I'
        b'VMrz0H10OIDxz1sUyeHDuAdvoNc2+aOmGnwtF2phQV59KEC7WbR+/BLaT3wfWJtNgbglXhkF42iFduNQdx7IzS0sI5spEuKeLHpPTthIqPFafAxrRGcYLodNG7iMTu4D'
        b'ox8jnRPJEn3JI+VMhl4Ghe6hq6jZEjQ/AO/EN/iWJYu4mfgsSy96mjuQsQThnUGoCR0PUuLt+EY+vhJLLqAYuEqAzqNduJFeGTW4YGygEm9FO6AKmLtcMi0Cpj++Iwyp'
        b'MehHjuzPX4KzbfCPFD9TBaApocJffPzSu8lffVj40s8abv8lYMnREeVp4YvGLj68Xzr18NTwPx357fq/vj1r2i8niWMVE0Pf2BgVM6mfJnXxr09am96btz87eOGx30cd'
        b'P2yMP/3mu43R5/Zc3nvtI31WYOkrm+alHN8w7/opvWXavY80B6e+duuTX/1R2aM/9+UHAss/v/54ee6tay//PKl8xcLJmoFvPfW5BIfkzo0tnbxULqZ6l/7o1jCqdlHh'
        b'3S6aF0El7lxjJTd1PQ3r7wDGmWi/uyoiNlmEt+ITFdQJdd4ieaDKT+ChfZmKdlMNjngA6kZt+FI4r4NwY2hj6qgGZ8laAPdC3GNR5OYWqOJwh5xlBuD7wiR0ETdQ5Ur/'
        b'AnREFRedAz2AlUPnQtB+bhWT7nZFR/C/e1eOT5fYALVWW8azcJRXHuvglXOkrJSVsAPo0/UjpPd+SNj6CCfn21eHXX0RxOsWShmH1Rq5ycO8iDwWk8cS8igjj3LyUJNH'
        b'BeOmzfDu3BvI19lXSbmziQpnE0HOFtXOdigvT64hk7vx8r8f68rLexuR3L9XqiVmfHYeqTeI53wdQbG6hn6TW050vf72o1uNrjeQ8CnAHRLDLr4PzmFqAlyQMFG7hDqQ'
        b'MPHqp5ei9bH0wcDUh9jZ+lDC1leG2pn6AMrUBwJTH+Bk6gMpUx+wLtDO1FcBU7/V78lMvdppmCfjbzz6HqzrdOLUwOeWAf2E+QKuFHgCtesdf4RviJNVmU22WkgFdlnt'
        b'SY9MNRV6o9rBocQA8xJDSStPWYms77TiJB10ir8eNRFx+P9JIf9/lkJct9kEslB8jFPL9R3SiNu+5MvzUY4KvLJkC7/DsNNnc/y+59uxb3V7HM/VGk1Ea2OmfKvROze6'
        b'wkTYRn2N2uCD7134BNNWkCa8G7f67DHBUHx/K0ymZaS/JEYpK7BDl5qGZaaKpbDwION7Pyg0EikoPS0h0a4II4AAIhypbmGf2avPTjgR5ATZXItNbTDQnQGAU2fSa5y7'
        b'caGL1ewTBUE7gnVfBupQt9DVsvY7RTVS/DFxzc1+8/8CaWuqboWuym598/8krv8LJK7ktISk9PSE5OSU5NTktLTURK8SF/n3ZDFM5FUMk/EHwuNUosKlHDAIU8qlKVox'
        b'YyOyFjqxDsSX3AK8OS7XoSAl9wStwB0eUtQzqMc/xVRPpZY1eGuFU4IC8SkH7yUSlBDftqVCciQ+sEilzCsAFtat2nmzl6x9XDZrw23+6DRuXWUjh0xZQfiBpaigyH5/'
        b'Eal+Pt4GubfiFhCkQCYJgvogfKdkETqAevA1tA8d92fQObwrsHAEbqOyR7ot2pKHO3IL0Gl0qUhFLj9KEDKRU4HzfsaP3oeI29AOiSWmAG+JJpy6MhckuSZ0IZplhleJ'
        b'RDXoPJ/rQBG+iK6rAvEttGW2BHcoCkHC4pjwZAE6io+gPfSYep0YnYXJcB5TK4PJXUPoxmxyIWgiahOtRHfxZRth8PGu2Wh7Eb7M964oN05OLhjth48L8D3FU3SdzhcK'
        b'KhIF5Fe5tJ/fBIa/6bR1fmqgmGHmMHg/2jEH96AuG7npZwBej3YEkomC6dyOb+WAiNmBO/ENInm2oXMQysdbovCuHCJ8LYqSzJTPsBEmcd4zInwNvnOZqZpcdDyV3oUK'
        b'sgI+R8AikckcnIiuoyt89Pl5sBjEIiiemYzvxauyDF9+++23d4YLp9wSUIDK/+M4HX8EPznIT3qVjSRH8HEv509jbOSosDDFj0xNBwUD3JITN49caByfNxdgIQe3l6Ad'
        b'M6PlABQ5zhuM5egmnT2xMWgxyMKHbESPHgxjOlSCdybnpeJmAcPi8ww+j+7V2sid1cXDkwPt6zO7D2AkfVODNi93zg65aUjIoOa5/k9Dvw7aiHEgurqkigi2vMw7Kxrv'
        b'LJHgs3i9u4z7VH9xcOIAKgjHoi25ljxFETpdVBBPgKjQLuPK8R4Ruo4fomNUoB7VD12P5S+5kYuZQPSQW4ROALzsQBfoxb0Ppxdxz4mZlZdzg/S/jXzOv95uq7EJ38rD'
        b'1+xqDd6aop2I+fFFBbOi+frG4gdudgv4IDothdEfyLcRT5hp48bFKnPjYlhGHJSEtnLx0O4FejHtatyTrUIPyJVJICRyZjY92iIX0Dt58gFu9jiK2YposcMFNAldw4fx'
        b'LlUuOuQslow3U4QAYHnxGfdR5kbia3Lcqf9F42iBZTJIS0OvRi3eNqkQTwltqqp7te7AM9/siET9z8hn1/oNCk7g+qkke+dUv3H5Zdms7F/3K/yfsDPp82MOXbtYXfd+'
        b'z1d/ravbef00ThWVdFZOeGV0bXl63MTTr8ydP3jUjM4o0TpNwcTWxdNf+WbU51Mm3Biqzxor8zsjXzo8ddrQi6/lhiw+Wzjz2TnD950L/PqzX/ekvPji9qA33kv/xdpf'
        b'zBCPmftUUuOwCx92j3vndxvSNgwe1zn01biSn+tK/5j6xeujk964MqR/Tkz/HRrD7ZmPWj/fMb776oGz+rnl2oMjll19b2l3xJmoroVVN579/TfFS8IrX31TEi/5bOX/'
        b'/Hx8kinK9FlNTY/oN/Elxf9b80FN1g08rHBAc9DmpGc/tSVv++IzXaEyYMK762Y0rXg5+I3wBw3fDp77199M2rZo3e8HLbmvnp7Y8+ylT/fkfrjrLy889dkV86nLN+VB'
        b'9JarwXm5DhuQiMI+XUS9xEpQ0ZJsvJ2qIlADavUwi6C6iDnoENVFDCzQaVYEqjx0EXq8njZUgm/oVLzBzVolNeEImScwcGgnvVMtAj+cFBujlKOt6Ai14fB/mkMn1RH0'
        b'Iq8kfAA1xCoJjo8DIJqIG9EWTgFbb4OVAF8G3oj3qtBxfX6MmOEWs+ProUsUvu6IUAs6l18QF4yucYxQxaKrq6Oo2gNtxrfwUUBDDuMNMd6M76zhxqFLaBfVwqBbcRWP'
        b'm3nA/Dyguamdx3W0j95qHFucbT8PzEcnXKw4+ANBdMx+uNgzC1+0kL2FNq5TEKpFJzsMbxOgy6EL+CvHrqLbuIcoWxilQ93CrUKtA55wSZY89L+ke/GmhQkm+oY+MZxq'
        b'YuYQ1uAZ+uGkdj1MnzaGXGDM62JoiCOGJcMgtR8rpuYlxNSEv9ksHMLB1PgkgKM3nQ1003L0tWrX3Uh5/YmOPCrJo4o8yPWLZj15LHXqVLypbfy+zw3IAXydlc6Kdc6a'
        b'ljrbCXI20afAMcCj1E2BcybGVYHja2gakQu7RY7F3a9HFzX7NTP0xJRtDqBql8BmofN6dFGLuIFZK64PWCNyqlnEVM0iWif2dUsoaWQ48zhPF8zzdCM0gn6bWcorxD0/'
        b'O4SZQ2MHhQvzj/CcnuHj/k/xl6j7KdA+C+qQLC9bKmAEwWz6SGAhCMpAp6JQawnqmIM75hbMwjeK8Y25QWn4JtqakAA4e6AAbRiKN1HNOZDOB+NLcMec1AS8OakoBXgq'
        b'yXIW+KB7qIVS6EkLlzpqYhlRTBbqYNE+fMVGe4BOqoDyksvQJzJAjvdORHsFlEyJ16zDx/FJ4NUaAHDGMpFQZjdPVY6hLnxPpUxISUrlGPE61Iq2sOhQAjpBk5dMxJv4'
        b'e8cdd45zwJYdHIRb9Xlvtgss70OeIXlXpxdlFgoTpTfeyX3/2o+U4VOnTPufrDPV3R+dnz5odOjC135TfPtdSe4LYelM//5jXnh278H+V78+8I+/GMZtigqIXqDZ/udw'
        b'6anL964Yv3o+e/oLRzY0vPLFjCMxW+ayY/x/u+WvwnuZWacCi999fqfuJ5G79+3qHeT/7hbNs/5Rf3/rmzctCW+PXvBBDc7I/9v18PqvEq7+bHVv7ztf/2pVeu3g123v'
        b'fjyw853x81/4efvDdZY1v/vz8NeW1QzLOv7cmorcff6BI+c8v3hJ/Oevdz19Y2VgSNW+SlO8/vO1L7wa+9kXpV8P/KrLb8nO2pB/vTb8yJ+K32PS5eFWMpOoscAPWOAE'
        b'3Bbvx3DoGDu3P3rA39vcvSKPYlYbPmLHrMA6XuHvXdyM75IL7TskKgdyJYh1NzpCLShgNVrQtsdRa3aOE7EmrOQR5lX0gFha8MQJbcUP+sgTOlRHdemoyYA2qArjgNHb'
        b'ig/hxnh0VsgEoweCMslU2s+FYUNxGzlPEeAdIkY4jEXHgE05QSnWM+jo0FgX60dpnADA9KyfDnfxNOLYQHSZ3DMPPUNXVX33zENLF2mO4HV6lat9JDq5gGUGoAvCwbip'
        b'H6UNYiBdXSre9PEwvt5n/hi+VIDOF6AG6zgCl7twIz7n0Pm7Elm8ebKdzrK4nbaZNUpAbFh5U1PcjO5Ra8aQYYIlCegcnX8ZalHZKW0wPuoktU+hLXRKxgWjS676fK6Y'
        b'W4UfTuRv7oWRNjhuxsc94wUMvRo/MYumpg0Z73abJtqCz3Mrx+FzlITj7vmzVeSMa0sRuRgVbcNbZ3Cm2eXfD/X+R7ftO2xr+Lv1KZWq7KNS8YQGUcNGat4oJBSK4+Cb'
        b'p1hSQND8R0jpFn+OQEK8MaTEme78vCUcIeSCuQEcoWWuljZ8B3h65ddHKXr9eI20pVdksarN1l4B5PuhxElkriW/jU4aZHISIkqDyE2vF1i7RxKlQeuZ38h8mATxHf0v'
        b'WmbZdfqP3vNQKfBuVlaHj4ddNWuwa0zMOqvNbKRpNTI10fy7KGC+l9Zctky3ygL11Jp1FmL7yGt27Koqi1Ndb1fzeNN2P67JN/D6MdKdilVWnRdNlBtJFbtOnIvdvI1s'
        b'7bIFKtSGdwFf24qugIx2dT7gtSvo3CzUIlo3F2jTesFqJWrkpfJOfBqk006RXyHDKIEFbPajXmTGxCWU1KK2+QqQl5RKAdOvHhjVVgHqxruLKJGeliAgupoFO/3L858a'
        b'VsjQo/IJi/BGZ0nxSLyzAvXgE/hYEhMzyZAqSq9YTg+FcWM6PhOrRBvwHl5MI0JabYCN7Pls1IRO2olw/jxKhoEGB+E7lNSGoiMqFUUk+JSCyG/4NEiphPcuwDDaEp5y'
        b'cxw+DqR7SPogvVoZIbJsgPSuXl3BT0cET00MbXxr7xsDVopz/6J81n+bpJ840PiF5OdvrVjbv6ralDctprYz/5vPm6a8tfknm5KHvXBPOC3gbGTBgYJpBYtDJIrzHy/o'
        b'turfrp30Vs/nukHv3dgtvzpOlbxx17dBP7+5d9a1msH/fPNff//1bemKP372yuGQ5jXLX0+Y9PC6fvQH5Yvsb0dImDCYkKIm9NDziBQd5SjGxNfqQHpui0NHE/jLgMlF'
        b'wCGjrXTNuqahfbHKAo4Jj+bQGVYVGE6xIWqpikJtU0vj+ZdkcEygjsNHwqZTE3J0XAIUzcPsexA6GcPLDJvQforsx+C9eL+dBBH6Y0YH7SToNrojF38HxvBhgqi2lJE9'
        b'RtHkyD40aRAKwnn2HL4J0iMHrdJ/iUX9OBfMYS9c+J32iWZ4vPsYOjrkw0LRXmk32yusVVurfd+TPoGx30ZNjh3J6xPEzrvShU+8K91uR/iWgPVy5NiHoQiysKjryC+D'
        b'wRVXfX9PNDKACbLcSlkM+RUjA0Rr4ZXbBAvpVhIHV6LrjVHW62tj4mhDdnRo9q4qtpBr/LROBbXarKnW1+mUsiKiT1+ht+icKI/WQQdAs6tllSYDoPnvwF9kuZwef078'
        b'JSm0xRJQPYgOoEuxObAxinOA1cgryEfdc3LQBdwSp5SLaycwOXiTXy0wag9sSppfk6yCfZRXoMStwI7NAam9LX4WcBuKaNQtRNuBy1Phm35oFz6DOymXr0bnDZVoL+5E'
        b'56joLzCwaCM++Az/lqWr9TNi/Ri0Ht1lVjIrk/tT7IKP4K3oQmwRWo+bOYadTUx4Noj1j2xThJYzkB53wjSpICMYJYQeWJw55Xb29t3Zb/utWV88JWxC20ZOPkU//sTv'
        b'g1t3LP1XyZCZx/avfm7R0dFpr/TUXz1+aMnohsqr89pmZR57N2ShuS5QMZJ77uPRU0//bPSrqt7aeb/YP2XYhLbfvbXoxpD0yKLS+r+PTTq6LGL/zFBjwTdPSz/ZWvTo'
        b'6eCWP5le1SxM/2BexaSZddN//nnB5Tc/nqA49XXYwk9/+YfGzz6pnbLqK/aV+vHzvgmWh1BFBXBbW9DVvEF0mgHkx7PookJB8YhqXT3hL+l70tC9ZeTG+TZubY2NogcD'
        b'vlSOr+HrKxTA1l7nlS7+6DSHjo8BXpx/TdvsYlq+NQ4EnsIY3MANQZdXUP43J7qavA8uTpmDT+XSDIH4Mofvm/Em/oL0HWGAluLQliJ0TkJfDsAETuHwHj90m2f4DuWN'
        b'IRXEFymoMHVfysUAS8irg2CFWmcR0iBX4q10VAPxtpAEQVXxFNoxdSY+6bxcXbzkKbyfG9XP3nAoPpMZG0/OEBRKOcdocWsIPixATTH4CC0bsxDYWsJTx4OYJp44fiU3'
        b'EJjrY7wK5VbNdJUdOkPxZjHj3w+EOLR/Gt+rc/gE2k1kE/uMTFWjS1wkvgvMNRUQO/R4Vy2+1PdyKMr/ousBdJ2yUXcE3zFoF51BWyO5uDUjnqSc+Q4U7YKWhWTbupu6'
        b'kI8/r16RUA8dKTCmDnVJKMTWBzlRKCnNI+Vu++sCrIybAsR3J7s5Pm/fhfF18Pj2MdzdMMDt9QFuDcvtLtDTGeIz7/QrBhxi/ycX8V8c/EU8dn0UsYnXmjRlZdTRp1dS'
        b'azbV6szWVd/HyYgYwVPrGaqBoSwwJTx0BDwb3u+/rh574jqayTHKO2QZdzD0YgBhAMsx8PlWyDEOdvvbfmM4kCy4b8SCH/gtDBZI+foerxNqHRAvZcWMS2rfO2e+HTJr'
        b'0PjgwRKWf3njxRUFltzSibDBLMHBAiZoKIePckb+jOohOq8IRGesBOUEkhOU4mIFPosaxMyQJOGo9Lz/8kuNvLpzeJ46+hXSc6aZ+BpXQg9oRjAj0O1R/HDO4UuTVUp0'
        b'2bYsIZUIsTfZ5fhBMdUxDUJ3UDtR6mxH7S6KHXwQ7bfY7O8u2oov4LbcOMJiJQuZcUUS1MblDQ7VT1nyscBCYLr14qZPyhf96PK2o52JTctZjd873KkmaWBUZlbc+/1O'
        b'9Xu/qSwzvzxNFRC4oOvoi6caEpuONhzdmbuDHR1B35W09Kmw0oNL5SIeax6DtluApwt9us9ZMQVf5/UZu9BtfB9fsz6GgPAB3MSzlZfwvWKiCs8o4ZXhRBOOdqko7lsE'
        b'JHVLnwiegbtBCudM04ZQ5JVTupyczNIkdG2BZDGnwx3Ln+SsIgWRCpgaXRmxVKCoidTjRE2jif6WoCIhPM2rnTtO2CskBXrFdu8xjzcpkcvfzGucO4a6w3KO2tfbP2+5'
        b'8oo2GRkAvoIuxkbnKXLi8lBHfC66EK0oZBkZ3iXqh5vwLg8o6m//tvzF9TaNWHKjBIAopxU0+pcKdEL6qjmGvGSugysVQVhCw/40LIZwAA0H0rAfhKU0HETDEggH03AI'
        b'DftDOJSGw2g4AFrzg9bCtRHkNXXaONgerLa/dgC0LbWnDdRGktsztAqaNkg7GNKCtUpIFVNnGaF2iHYoxJE7L9hmIZQYrpWRmy66Arq4LkGloEvYJSIfbVQlB3HkW+D8'
        b'5mP5p5DP4fIUPv5bO+JACNQV0FfP42W0Iz3j/r2ndtSBCO3oA1xpmC5cF6YdE8UciTjKNLA0NNYRojn6UbtD3o1IAnPiZ7/foz+1SPSj8yTSyrUxEDdAG0URS0KvfxnQ'
        b'KfUMYI2pV7eHut1dsOBtG8X0RYJip5Jd9J1Kdo+X3ZB/nh5pAbySvd9QoSTcbjixeVIif85dEt8+Wi5I4JjicmNwjT8fuXfSmswL3J9ETIJ69cesjbGRm0LQ9SCTmxO7'
        b'mxAJOKPNjwF5He+tkoTiK/m0Iv9+I9eEClrgV/lU/6eymQ8cnaSufPrmT/ZxFjKA3otdQ9uvvDg8aH2CVPi/W6aVC28e+ekw6RRN68jF5Ry34/eDmt//rKy+Z/tL4sAB'
        b'C4ve9e9YEtkVsOXHL09fWtccvnTy0yd/OV1c5qdper75gzezM9/5eZZf1SvX//HqrCsVd586cy+q7vC/5P48b3kTr0et/Nt3FAJ0DV1lJHM4K76EeGViID6OboIgfCl/'
        b'Jn5YQDi1cVwYvj2cmjWHogvonuOoETJ2uxw3rp1IJWy8I3/J4wI2mRszfuDHjIkSVa/CD6n8rx+7hncOj41W4NZaYFshI0zhwCHCiejsfJrHho6jvaituJj0FnVQhXU7'
        b'ObrbL0BHA8upH/covEUOFd3PceQpQOcZyLJTgI7j8+go7ThuzEDtqC0eONdc3M6ibnwb+HnyykOgUpusRN7C3fjIUNS2IhdfJ+yxlWf8O9DWIiAIrUV4i1LMZKjEaJfI'
        b'yGPb781h9rmBD3PF4kliNkAkYSOpO7hdT8rWhzs3zmMvT+S1mr0iap3UKyTGrb3SvgMto6nXX2+stVnpnVt93KersbjIvJH8Xk8eDYyD8dzg1s94D3rwKzf+00v/foij'
        b'raiMdNynl2sWZ98aru04nb2H9F0Y6uHrqjSrCJ75Ac7WQWWus+ezS9mOLj0a5tK8p5+38odMQ0BZ31r5anims+GhuY7MDrvKf7dd/zICPmU1et+OznnOZgcQUUNWaTbV'
        b'/MftqVf6bK/A2V4/2h6xuv2hrdlXVFxmNVnVBp9NFTubippDMjqsc32295/7THt9cyjHeL4mkJILLUt1yUzC2PbKSVExPDGyzfMjLgGhCeKZC8LXjmD0UxemsRZyS9p2'
        b'v0Ty2tocdZd24d+j31eppZUfln/I/GV/VMme56LoC2nLb4g+Mh+Xs1aSHx1JqgNUebp4Re6TEFxt2hN4Uyr5UWRG32nmQGbzCDNaH+aKHL6/N3WJB8655Kav9Kz2o2/h'
        b'3/838pB9qf4WJ6ROGlPG3jX9rvg3yXQ61h84/2exhgIpK5il/ypmG2ch15xsXd7Jv194m3bBj/agPej6tm7BT2+tW6mmL1zM92OW9og3Dr0r5+itKCOHjca3qgktetIy'
        b'pa+jBHsxvgaCSxtujVEoiViyEW16mktO6Pck+SKkjBoW6+t1ZRUGk2ZZ3+vvHOu5qD7KZdLdc7u9s1VELWI9RQ0ihLsoNrbDY4HHMp91W2bfLbptSsdKE6ByvMNVAGst'
        b'+E9e6Msy3o+S6FpvXfsP9nraG37AIz7zZW0+Q/Wj+hBghs5B1vqn8pj6SHSEismrh1jQORjnatkgZjU6U8H79+2cp3HjHMmLQKPRBWmhgmVSUKs4OKiaWmKOyBPCng+j'
        b'lpiTM5IYalY4yb+Qey6pKYSpVUe8tmDBiDGMLZNU2o4bxjruQ0LNaLObgaEdVNzuQjqK9wbgfUW4g+JAKoNHlIx0CuDo2AAhQyVwtA8f0tcXHmEsrZAnOXzxmJczg1FC'
        b'pKA8c+vUgfN+nZkwr0L9rvincR8OD927b86dqPyPpu5uKRk9fszR/WP+2Rlx8fYzA7MbsTZ81LyAg/6nW6SzmtTtoX+8Prxq89NfqStmx4+pO/NawZBftj9z69Sjn8m/'
        b'3XPj02+W7Sxgf5l/82r861cXtB395v3CRyg5Rbmn/Q+bvvlK8L/bRrbfny73o7rXAWg7vuqm4AxJQA06QRWwtc28/cCewfiCq0WceZCdSa3DW63kZknYMQ+HwAaLsj5x'
        b'i43FV+l7lPEZbWpgjJ2dRdvHOg3thqNrQnxpFGrjWcjruIuj9hWEl4WlRudBXoZKV+BjtF4xk4DOioegG1Po1g1H+8faDQKs+JbD6GzrbJ5Rv40b0TaHUmGmjZ7scyZ0'
        b'FV+WO9+T7VOpKS5bYdbbX3XqxnWWERsxjh0GXOcgu+2YlK0Pddl6tKD7e5nV5iqLD56SM3e57/ROeCzy2Omn3N596dFcoUboshndznXtb+ilzm/ON/QK6amTCPa40LnH'
        b'RXSPC9eJnoTPRR57XFxIj4DDS/EN1IlPoSMCYqc1HPVMoJIrPYutxVfRudhZItymmKcgZh1+Ydww9ACd0vf2nyKykNsj37n3IdFUbUO/e3bwvtefvbztTuedhjsL4prk'
        b'e0Y03WnobsjoyG0fsWfDNRFzfoJk1chWoMkEtNApdANQfbwum6hVEEAJtfNgmcHVQtSCL6OjjqV4shZbXEZdIuiCh7ouuCGYmle4zTnNyuusxS5mdfT9ylRH5I7Ou4V8'
        b'7GM56XLvJKjQY7n3hvtabtq079UmCsZmEay3mCoXyJr7/adr7qkQEBXya0s24Vq8BV8pIeu6i2Wk/QX4HluAutB2/Zd7vhHSezj/d+7NT8pV6hffj377iw25PJNV/km5'
        b'vjJm1yflH5Uvq/xU+0k5tzkhLdl29WSC7XLd5ZOJrYnk9dwsY50l/Ud6TB8z+r0sTtzeqk00ei5r2891bc0S3qiGGHH2d5nkvjJ8Vbt8Q9Bu50rugYfJYyU7I11X0nsj'
        b'H5GDAN9rms7vYJF9D4v++3vYdT0j0NVyWE68Mxltm5QjYER+5FCzJ1m/PXWC0EKcIuJ+MvCT8ly6nmQ1c9QflyvVH5Z/el0Fa/ppeai6ujJfE67h34R9hvV7NOtZ2Kxk'
        b'4nEnPpqqyh+GL9kNnnGT+vu/S7c3uMx+r6jLerpx0fVkPesjXSbZrYBD7+C+D3vFlWqN1WT2gaCF5v2+9u4+eKzwWPG2fq4r7rMz8hDeUrfPcJfY7PYG9QnVy3SreoPq'
        b'TDZNtc5MiyS6B5N6AzXk5hYdeSNqomsgqVei1Vv4K1eI/S95N7yVXMKrs1lBlCQXxpKN2SvVrdRUq8l1phAll9CzLzPRKJoJh+Ttul9yClZKayRGSom9AY6rVfRaF2/0'
        b'hTSHVW816Hol5H0aJHNvIPnl8PKm0fTuJlpTkvkYKeNHHA4rTCupK3qvqLbaZNT1CirVK3tFuhq13tAr1EO5XkGFXiPnev2ypk0rmls4p1c4rWj2dPNV0jTx5fFgd8nK'
        b'Ep7AQvxJ7BcCi6mJMtssqZT8J4yvwF61+4bS8Ixv0di1Y+YyVA86+AVlGkMPfcbg3bjZgm+uxddDAI44fIqNwUdr+Cs5zqOrIyzWOnwzBN8IZBk/vI/Dneh0cCQ6ZSML'
        b'swB349OoPS2W3CZ5ITqnQJlbMAu3FKILcXhrfN6snLi8eOBjgdVyeA7hzoXSaWFQnG7AsxF5uHMW/KpHt1E7U7AEH6b2UPgeupuWnJJQGCNk2HEMIiYNV/nrSC6jw5nJ'
        b'AOXJTOaC5Gy8j5L7iEn9IXc+vs8xbDSDuvD+RIo95ovXOa1BWSawlAuaiS8monO00HK8Bx+GYokFYoaVM2ingHeiQ53h+Co+RcQwYqyaSt5bf4XFnRGhdBZzC2PSfyY4'
        b'AyJ8+cir2dn8LOK7eB9qhsrwFnQaxMUYBu3C24PoLKrrjSqlQkkc69DlcQUKvDmfZQaiE8Ipa8bSGk8ukWVf5NaTO2GHLJ6TztApWIfuSKE+YN7vCxg2DrjgWLSVOi5Z'
        b'VgXEkstFcqGto/g2OYcKQR2CCtS5lla3f+FA7W2AEEZWPjFsiJr3VBsbGgW1DcCH/RhWwaC9+Fg87XicP7oGLGkpuh6HuoWMMI5Fd3HzRFrR+4GTY45xXzJMQrlZqEzh'
        b'+6WG2d2dnALrcLcMBC0lg/bN6UcnG7itq2HEyKpAMQ5tYxn/RA7twXdSaV1xxrwcIRfNwqzlcc9oGd5xaUMEXk/qwodRI6x0PIP2j59NeTS004Tu45ZS3paM2gls4kbp'
        b'UQ+tTZYiTHuJpbr/uE8qIu1r8AA3ocbklLQRqIWhU7YTBKlN9MwL7UNn8H4VuYSlDW9RoSvx1Aw5GDUKJuP76BCt9bYqvZZj/kAuu02a/YyVHy8Awt0lUKkYb+PocHej'
        b'm2tonSw6j8/xVRY6gSx0HDMIdQnR5vkWWlwVhDdCaXxlmpiObw++iXdTZ0i0NR/vsxfHW2agW2Qhg2sF6WgnPkH7k6iJGLKUIaqu8onhlf68wwA+mQGDTErQ4fViOshd'
        b'hkr+gphNFnwbONsTdrDlAGyvsrhLh9opBEROWJqcmgCbFXqeRMDzlInONHToBD6ETy6LVRGrPZYR67ko4u9DS+GbqauSxyfMWwWl0qH7E/FWnodOfcoOhJvRJYaRThSk'
        b'4wOh6FAub1d0OmkilIL+nIRJm0Bs1a/g63w39+Bby1T8bMmJmbk0VICOK/qrED/onSv9uU2MjN443KiV8INejBv8ksenKADxk9r24vXoMoU51C5D18OXQleIa6EKwETD'
        b'DUZdCbSUEDcnQym8LQdgKxM6sRCdpt1LxZvwcZUK0NsDdJNhOBM7ZTC+TNcL3cSH8XZSqnMWdH0iQCQTwzs9nMZd6G4Nuq0iGK0dt8NMRXD+uL2S9jtl/urRceyHBMAH'
        b'3E2q5futH4qb0bWElBR0XcSwUxl0eOE4vt9d+OoAkA3m44Y8cgYiwA9YtH8Wjw82LpxRfEZA7/8J0OeW8XsFn5+kJFWhi4Dk2WkMOoLPAbak22jjANSgArSC1qMrwMks'
        b'YePxPn9a1emkqPIAQTmZzSHyVck8SJu1uEGViy5Jif2NUMiiw8vwTYpdC5atwJ0iYjRrxBeUYajTRsRrP9SkoE4Ks3NA7lXM403RcEtBHH6IDgMaYpiZ4X6D0f4lPEBd'
        b'1uqdfqWhFhCE8R4O7TQU9d0I/XKmwBzBO9Ma9i0KZXh/1puSxbgTeM04JoCgo/vpVN0SijfE4K6hqsfOoIDGCJkx6KzIpsOXaLvrMiDpPlCKtlnEEQaQWTi7GN9EzXTQ'
        b'a5fgHtUc3LEA7QZowHuhm3Xh1GEU78N30UV8GTc+7hvNMmOKRHrcvYwuZlQmISyBxNSBwQ+t6EECvsPfpHVLi09PGxYLs1KAt+Qo8nihL1HIjJ0jSkIX8H066DcnDFp0'
        b'g60mhGPNkUUj7UjrHm5YgvcDd40eMug6gORDIEstfL03Mgfga6jTo2KOGTtXlIxvRvF4dzu6hK6oZilQi0jMu9/2ALB20/1bJVeUFKzETbOIQzO3mh0SVM0X2o8fDlDN'
        b'xR1Po41kPk4SdcdedIg2LLfGPeZ8DtviFgtidJsQ0MVdO/lGXTNhN+8HXhTdZ/DREeh+WRlFbfME/mSHK3MLoWiuIklYWsMMRvuEBujWbboas/HDSXi/gLjzMSn4EuoB'
        b'tHWIGmnDCu5KdSvNAXbaAeX3C2tWyymYlpUR93Syvxi8d7V+QTrvBrVeTDZnaxzpM9o/mC5gSIRgKT7NL2DyZNiNnVQhABxF13DUju7xE30Zb0LbKD6j0EVtItgBlcwQ'
        b'dEOIN4fi0xRA5w6FaRORq7iY6nXoHjpSzqPINrQjAbcBT7KMmVezDMhgD0+ncSM+qlIoctH56Dyy1SKWFE0RABI5nsiXa0Z3xXi/lJxFM4ZZAPJxFNEMQAcq7X4neeis'
        b'0+8En/enU6fBN1ZbgoLMaCfgJ9h7+MIUtIkC2EFzwMr9gmgCYIZTUUae8OOuCQW4DQZtIm9RuWHiYPGofdId1DwZmLYcACwYcpECuliNG0SMbLAQXw7Cu6i28mT2aPYX'
        b'ZNsWqoxvpK/JCbBv1T1Aart5fSkTm11vsOlvJg0TWf4JrO6Qrx4ufuUlY0RWqPgPHx/68fLw1yIi2psPXv48c8PoSE79v/7/rAwes8HQ7+ldW98JHDD78LYfR+Q/5ELw'
        b'qD8N+brks/YZQ+LuPei+KJ+/2z/zubPn/jn3tz0tPSOCuvxn1+hP5P/uz+Gbu3On7Tyzbtkfrv08a9Don5wVH3pmvv+Vzz6+8vG3aepBb5e8vU01738uyY8X/Oi9yL2F'
        b'p8J+/hfBc89d+23n7Y3jC5b/JuZiRmv2+zLbuIXZ749YeDAl+2bWvsKK7X/cNrSwbvOnGz+tuzpTazr6l8nbRS+uG+eXHTw1LXPiaPPtX7wVtv1404QXsrdMK0zPkJvP'
        b'Fn9w/cW9Gw/0z/DL+PzdjS9Of3HMuLaRu0fMP1/1Qf+O3zw//B31ZlXi3lei939dNu353bl4z+1vpr3QtWvV789u/yZ376VfvKuvGjR+wq/+9vzdooanl7xkDJ2d9bo1'
        b'Nczm/2dU+frFH53ddnLi8d6/hV16L2puQ8db534/KeTa6uA7O8VfXhyz71LuDdP9ib/tCXpwqNow9e+H513YuPWrTdYH+w7WyK79o23hmhJDTcWZiD8rMiyDLbdHdbZ+'
        b'efHFntY//Ss3/qMhT72Y1jk8r2lmU8DWMd/mrns17Kn+q3apOg63nX/tpZszvp769u6v3p/+9ccPa878edn28V/tvRX+8J1/zPvCb/cXsz6NKLzxy08+iA+7unNq2WTb'
        b'x61LRhf8ccKvJux8+I0gJuxfpl8r5RHU5RffBrraUzPPm+EAbzUwCm2kjnGyp9DD2EIF2oM2sQyH9rEFaHsqVaYuw9eAU2srHIE2gDAhZoTZLOrBW5T8ZfaX0fYJqC2k'
        b'VmrG11FHSF2QP7nrYQfTDx0WmBLmUCMBdAcdCAtE3XE5DvVuGD61GN8VoAtiaJ4g3+TBS4iB2EDc4GIjtlbPK2zvzIZm2uKpmSq+MZFYDB/nUJsGH+JNXK+nJ1HlMMHI'
        b'JtwFZK6A06I7+C7VLYC4Mw82FT6KbsLI6tisifgaX26fBHBdV2KfHzZ1wt6IWqh1mc7IAqnFreHEWIP6A6JL+DxNWjARH8cbV1BrDocpx5piqiK34VND7RpyvH+kq9v4'
        b'ONRIbS/w3ZnhvJmIi+HFBHSS2l4sVdM86fjkpL48dsOLS/gCNb5Qm6gn+2igTu3E0uPpcnJCQYQZtMWp5YzNEKGbk/AD3kHxGDqFz8IUuqtCQWo5y6tDTZHUWC8fX1hl'
        b'981YjA70uQcCUThPp8wvYK7T2KMIbWQdth6d073dif+DTU17BWotr71ZCQ+n9uYZRhnODmCFbDg1zSOO1qHwZ/9w4azHh8R9LBkayo4mTtlsJJQhf1JWwg1iZWwwLUMs'
        b'j0neUJo/lO0HIe5TyYD6oD7VDPTHVWNvJrq3H+rmxvGl+jT51+FxlqiHyPZyqofWM78b5GaQ7NYL38fnVAvIvwyKaRY5tYAsVVr8wIvHSSMy5nGlxTheaRFfSw/RV0ax'
        b'5XHa0CEMrxrkXYaKgaJ1ivAuSB/GDMOby3i25Oo8vAd1Mui2CZg2Jgqvxw8o1cKngeYmC0PnMEwSk4T2olu0hWv5/uTsd8H+inLDw0X9GHp2t2ORhERW/2Npef64dTk8'
        b'21qYvZb9EqbwnWT14NQxQXw35qAriuQUYQg+R6RWRoNO1tH4aVUTk1PEaAc+Qi5RZXSoKYlWcmI0NQCILBlbLv2jfixf84TIMDIFkc8vL4/TZw3h+/DZKhqZLl9RHscE'
        b'TuZzPhshZWAFI9PmlEsrRw/gcy4bH0QiizWl5dJtObV8zpHTAhiYj4S5A8sNDVERfM4tYwJJZOTEoeVxtRHD+Mi3RohJl4rXKcoNe1M0/GHiENyMD5cUzAJxdBvumEvY'
        b'bVEdi+4WPE0nc01SUMaY5IQEYB5Hk5tcr4fRRqOLRjLZ0GgqW84dzA7kD1cj0tBWYBaiUDPhF+ptZl7U2jQZUPr+AHx5LsGX8B/tGUVXkI0ahPeLo4gYj27Bf8A3h3hm'
        b'pkXSD3ey+JqBYRSMAmSg7fzlPPVColVLn51dHqeYEcwPQJi7FHfinXhnKTCQO0H+wpsYdAM47MM8+HSMqkNQ10nghoYyQ4GdOcuLL5fS0VFyjFo4zW7JTE9Rs/rxYthO'
        b'dBc1p2lK6MERi7ez4SNwIz0snhG7NtYvHW1liIPNRMz7IgahBnQInWNWog0Ms4pZhZv8eQ6qw5yGznEitIlhVjOr8TYLPcalyzFqEh1N6I5p5fmK6gBeq5y1vFPDDGyg'
        b'xghvpustf9dzlhTYOY2LCmu2Z5LbWzZV1b0z+me/yh3iF/FmLZMdNPRt7g6KH5HR8d6gs+vfTZr5uz+G+R3JzhC9LWyZlrAk89mpKZlfPHPvi96XMl6NFcfPHTBFEf2q'
        b'f9Qvi2dkHWeLWgoHPT/tV0mlR6r6D7y0rzreVhf4VM+0cfM/mxv4xs6kGqsi84+qOUXHHt2LPmhtDGoMiv1ttPnCgmqZdc7xxTPHDHz+mbMP2l5NXptfrIw7PfjM0G//'
        b'T3NXAtfU0e1vbkII+yLiWo0KNmFVURR3LCgYNgX3BQMJEA1bFhGXIiIiCm5YwQWRxRXrbl0Q+3XGtl9ba63Pr0va2qrVWlt9tnaxdvHNchMSSBBt3+89I5Pce+fOPXfu'
        b'3JlzZs7//N2zE374oPuTcVUvrw1q6tk3Z87EUX1W7k9M3Kvz/GN+xGfOCy4FDZylXVw8atHqOQXDu73zgccva6/9lV51k/nwz8+Pdbt5+diUgMQqh080385IOTAlv5P3'
        b'jahL+y9H/TJuXHJOwMnk3MkDGvseqHtpx0cPv7ro1enf9+o/6/doz4lvZvWo2HodZE64OmTU5RV/7O19d3LRyrPnpV2JA40XXO7Sxi0D1Ae29hB0IMMUPOWkIsv+aHCs'
        b'iAv0w8PQSRZsAY1gK3EbdwdHQqi/OVgva3E53+dLjsLK0ZA4asLzYuyrSf00l8MVRFmZC2s641E11mECtkBxWGMMbg/nI8P01EwyCoYnReHAUUgCpD/UwlKkObzM9gVb'
        b'4RmKhawCNRE2NS5QGZYhWEJBUuWgeSQWJFrujyceDvHALv40Guil2sGe+p4kqKj3CRuycDLRMCbORsYpKn0G2EWB+mQW03u6oEc2rCRK2ZgUJAJSiNYh07KUUhSR6SRP'
        b'Xz44CA9MpbCiCrgR6w9YhQFnu3JaDNjgSjWGangG2SVINmRgt3URBdtBHakKLeoqSs3gnMnTqMbAJFFd5xVfpIKiUsaChjZOpN7daZ5C1CnUI7Uiig9qAoKC8HQ1khXu'
        b'58MKF7CBBB3oAwuxvyrWDcVIT8WOreZereUC+mAP+Q0nmZBeA2pkdoyA5aFX/oSYqnu1PNBAlv2L7UyIfjZ7KajSBTIkYsEeZD+2cjLYDQ8SRwMLL4PDQ2mBJUlqrJa6'
        b'gToKoKJqKVzehehnoDGnE5bGf3S4DfUMVXId1XDXj+5E9CpYmkn8aDm9CtbEEO14ntTN3y8I7FBLWyIJgUK50V2hQ2tkAuyLR3SrDEvdSuPME7DGkAFeRLPyQh9v9OmK'
        b'PnjblYQP8CI5PLk/8rkl7Ml+LXwBB8VxZh15XozgiYiP102dWRFBeS12bdFisABmbmvtSN3ixXYSJfetqEqbLdbSWl0E1QtWTdDXBvIVR/5rtuKNLq2wWsQ3V7MYJ8Rf'
        b'lzjyYh9eg8jo0Wn8hRebqB8kAWlhzyvilEGW6skqL1n4MzgnJ4RPDo9NTpqREJlo4GuVOoMAI/oNTtyBxMikRKIEktuj+uXfjxaheRklAawRp8V393hmJJadq8DVxVXo'
        b'JXK3N8aIEBJPFqHl5weBJz5m3M+2Pm783BPcF/q58lz/Etp1jSDzUfCsHzJEtoWbd/Z2jHsSfyYsn9ZmQdrIxkKCo1mQxwo2uxFyVTfjt4I1/eKX2yt8kD6MIRRuaQKF'
        b'vUJkopJ1UDgS4IszRyXrQrZdyTamknUj2+5kW0SoZh0J1awzRyXbiWx7kW1HQjXrSKhmnTkq2S5kuyvZdt4sSGOwVIpuO9jNQgxtme+i6N6N2eWKQSDcdg/jdhf0V8mu'
        b'4yl8OTy4PYmT5FTiVuKe5kAIaQlNLDrmQEhfBQQ0I5rpjmtD0aecV0LtAOcSF2QF9FX0I4SwHoqeJGpSf44QVhYX+XiLBXw6yUhUig5RNlixBFN8YOYmeZYCN35Vaz5J'
        b'iw2/JIzi5sia0K/sFG22GlNJY/A5Ds5LmTFxcGBljo7GpyZI9FYxkzXYJUlqb3DgWMcwUQ/3k6wTi2i8UEzZo0hbaOAvyEL7MpUKlT4T7RPlIMnzsjUKTQslrVUuWMuI'
        b'VMbw3w7IfnLkln+dTBGpOsIGmyYVXP+hw2ywuJKfmw326WSwbYhfrQLwn5MM1uxhmOTAAcTbkQIdtiVDlliuzsmQB1oTJUycmoEumUrCdLfPTds+Na0VGtpnqJGnUtOi'
        b'dkgjGkeMnypWy1Mw/zn6aR4kWhrUKvwyJVizKoWl6KRuJYPMqsKK8Jwg6F14CjGuLRJc6xEabBHjdpAE12qhLcS4f4ME1/i+02qnW2KVgntgIU97YMZOggtjzW2JNcp0'
        b'lRbVMOqcUB9GmlOAWM89Nn0WDif9XFyzbnTq5P0oDyZKFo79CpwPzJ7DEJcNsKmP3Jx3NWaOiRU2xqTZW/DBFo91dod7wCZS5pUBnZmLLkl45X3p3USOv3YhbGas8szG'
        b'5CwwlknIWMyLrclxhg3gGKwn5W6WOzM6TNydMC9mgCieoUQu25H5c7xdBlvigG3mFX0arAYrwW4nUOvYlRQc4S1kHnj2IuSzSXwxQwIhw/L+4AyocLBadLR/onmJy+F6'
        b'B/AKWGdPivt0lAPj5deHLE/XafPo/cNmIYaZWSOzjTWZc63EfA02uTiBerByIim3ItyJeZQSSNZuHEJ9GYLNBmfgeXjAWsGSKM5msSj1LGjU2TnB1XA3rFN9BRv42jJU'
        b'ys/hTODFJhc23Dly0pK/5kqKxt2RO4mPrlz4jnvnAYIgfvddXvNvlA+p1d8/HrilbHhe6JkNnSteqPwx8It4t48u//ZOaMDp6x+JRsBNn31Scmb9tYjB3crrpNcu5D12'
        b'H9mUvqj49a/eHwXXFBx4mPjzrWOelY7vBr/75nuhY4bkHfyZefLGenhKXndi0+wndmuGpYiLpI7UpbtyFKifO7CFFtdkTcJj/tTeRIbKHrAqyUokVO0g4mrr0hnsIgWM'
        b'gEVmbcyO6Q2rBPAwPDuZGHHIaNyDZ5BeAqvizRoNZ5cuhKuJraNJA1v84SZwJkjagiYf4UENvDXwVbAc25PIXoZHQTO1mWdNJ2cmgVXY7sX2H7L9fBcT6y/MjzqabxBg'
        b'qxk0wUPIBm1j2BfDchqhb489Lh+W6IKjWpmi4DR8XYfjwcAdwfAs0V91oCg6EL0Vr2nJfAVSaGOIQhsoZGLBSntQ3QvU/2PavQnriJEZZuZbATOOEN3yhC2kt5QAl8Qm'
        b'NW0ZeWWR/mGDAvd1nPwLJ2/gBOAE4uQCTt5kmKeTxog6UoiLxT1JUaepxeaYmXW3nPnUIsxbW8mfhQfUMdmkPdlEsE1BUlB8ZMu1zLhw8a52uHA7DpE0UZOaqVI2hZpu'
        b'FOpxr1YSEMXguRloObXJ5nVnma7bm17373HwcpBFQTJSlmxec67pmj3oNc0Uque9HtKJbF5PbrqepEVrkrfGoT47z2+6sZaNeopNCRQmCbrj2QszVea5r2mygGxdM93i'
        b'mqiWTQqQ2TWlLAUxk6kQk+9sXCrfTBTsh47fXuJdMR4lZPUJh3dgObvVkcT2dU5zNnml27XrlW6kULLz7DCFkhLzRXaUQYlkfhYCJXPCpDZFYgIlE9LYL0DsZw55RtsE'
        b'RY0ymdO/EMWWioFZNTpu/JkuNFycmJ2JTQhqa+OgaxxuWZ6SrddxvERapKzaqhv8D3OAKHGVKFRphCFGxynjljfF1TcJHomqLZ0LKWdFD8b/ok2MRvL27LqBoWbWjFhi'
        b'pE2xbdeY1yvV2du8pGJJeIpGmZqRhRlbOCOPBJazKmhLO9BqVelZpClQXpQ25Fxascr8rlTI3km3Qb5itGMGkoccGmYyZ/CVBkoD8OyIkdIX5zBx+qbassBIq1SR8zFH'
        b'FK67YWEd55hKs7whfNcqpfafY4iSYEYkwuUkFfv5ZWIbG91Ovp/fc3NGiSWEHyqQ0iw9S9Ht8EN16PxnZWsS22CZssXWFNQxMSwQHe1yNklMnE0DpeJZAwfZ5lwyR4Vw'
        b'j1GvpLejyiKCErb1iNjYGTPwnVkLJov/5cjzM0koWqUGD1EBhJDNZBqbCTSofYHaJZKynCihb0uw8U2xKhZVhMzpp9DlQwbYZhIzx9AYp43MXhO0F72RWVoVFSo7zTox'
        b'l2I+ahmkPvAJJB6vfBH+3UFOIvwv3KIQLZkxU6Vm6FSEeErbQovW9p21WWageCAmd1bqUedqKgC1YJWYqyLUQ2WiNy5ySmCSXJeixLOQ1mmyAsWoudAoomp95gJlhvX6'
        b'DxSHtMpGribXpy3W65Ro5MAxmcVTszVaIpSNMgYPF4fr0zKUKXr86qETwvW6bDy+LbBxwpDh4ugshWqhCjVmtRqdQMnbtK3u3MbZodZEfvYKGmqtGJWZWJnPJtYwa+U9'
        b'W72EkYpsqfqn1LzVnUm0JePpwlZyP3NLNL/9NA26GwmuW5NM8pTF+nSp7eZnfrp4qK/tBmiRcWCYrZyomWUFt+XFpAeHtC4m1FYxoe0VgxqF6f7aKWOYeTabtxZmUZiV'
        b'+7I5oHEYP9TDcb+IPoB0UtS3GrtySSIdY20O2C0QQkzOjoZCuoV0HIkMbSqz0B9q5mI8Bg1rh9/dBD60LGZQq2IGtVsMwSlakAdKCGNgBB5vhtg8zYRrpKdGTiE9Nd4h'
        b'lqCXnGvi6LHbrga9BpMoYoJ67leA2Ey3i5wyWSyZBhsyNOglRbIMti2KGaSypTDTbk4oY1HaBXqNtq1Q7al7ttRLokp2XPMzqWjhFjP/HdNhCPhzuDgOf4lnDRowp+On'
        b'DaKnDSKn2X4aRlQpp0Jy29hsbq8dEMgpOgV/oYxt89nuxaKUGk1W8HiNXI8SdVDweBXS7mz3WiS77b4Kl2O7f8IXsN1BtXdl1CtFZiAlDPX9trsmIhvS2RTWxbBVeUiL'
        b'VSp1WLPA30jBCm1Xv0vJXjRcjBeQkf6UhrVWtAPVue2Hik/CiF96llwtxhvtnpGq0uEXEqXtqnsU6Ixz0h+k4ACspweGDAwNRS3NtkwYYYwEwl/ttsg0Obrb8ahTaS8T'
        b'wSijJ4S/xLNCbWfkujkjP2o7LdqInh4uHod+UU141qCh7eY3vdrkFMuVvXbr24jJ5s6kz8d2Z42x2EhFGxcehx6P7R4xRZWKCox+CV3ayhvZBk3dNqI7R/L041jsmPzg'
        b'RUdmXkxUby+GYJBcpJ1N0Dce3EHiEmLwG9gBKAhsuBP27TyicRw7L6ZYMJ/CBGXg2FBZdEC0XTxYTgF5ngKSO6trFyaAkTi5iOf1rF0YwiFAX4WV8AjG6Q2TYXoLUAGW'
        b'E8ARPK+GJ2TR8JAF5BkegmeHkdJSlyzlPWJFy9wGyHsELUESYw80cC4d7PRHmTFJYDx2GAQHJ8bioEawIi86CS94rJ3MLBrskA62hRNM0DZ5HCt2XeNCIxj9EmagEYw8'
        b'FLAZroX759LVKvP4RThAUhRdpLCgRSwHW52l8ESOqvHTAjvtDVTIuKC7xetiJ/Inua9sfPx+wWzZsbzOn599z+Fzx9L72z0GDfi3diosc7KvPe6wc6znvz+9kPpop5YZ'
        b'GvtfU37Wd0sedKvQr3/s7VNvfbz7LD8w5EOFXWP/H369ffCI7rxk8J8bOsdd/v5i9LrVv7qk6T/wuFd+u2Bw74yT3oW34zQ7T9ZpZ8Yt/Yap9z3ZI+zyu8uufP3X2z+e'
        b'jr16wKPg28lzItJfHzx9hv2X0/7w7skf+kntnBfvHNvz45cXJBEFSt+ua8NTUkqaLms3D82/0Mkw4Pfvwrp0v62/s9in3/WF/ZdeOfwkXdIrYfQT9hozYWNBlVRElo3G'
        b'g5Og2QID4rYocGIYjekeDOsJ3pKF6xI5UqhSuI8ccwZr8/xhaXw0OChghGoWbsvtCxqGEg/V6eBAgcV62Xy4hy6ZDR1EFpFyZsCTYC0shpXYD6rdRaQkcIIGAF0PzuaY'
        b'giXFwmp4xDJakjfcRtw/58EdoJ7w8plI+cAOWMIR801woqiYKrgSlMtionkMOxkczub5DRnUFsPh/A+FEMfObmTxCq/RWixeFTDxIkKvJ+C58nxI4CT8G/sPOnILVyzx'
        b'QuyOvr0xOZGzaYFGrlDEWYTuaJm2xn7aZqtVDs8kuFRgVkhLPE/Tncy3umRV1dd8ycpCStvgDRKECbsfMSUCUxCmjjATrURC5uKexLyXxMK3pcLzpb3kIZkdIxK8ao+R'
        b'+q+K3alnfig8DF7T6jFMt1zACEAp2AoP85bBshSK7iCEFSsC4T4nPo7SIp/GTFPG0xDlW1z7JQ4ZAJqG4jN5sAnDVivppaLzl/Eeze3FMAPkI36Ll3AhBraAKlUIWAnK'
        b'BgspDgPug5spAKAGrIgLCRw5WMABNyrCqcijMBoihngMlOSNp2CKK9M90PYpHpMzT/166kDqqH9xDto5/WMW72QmBdCcMdNdmK4JXXlMwjx1us8EmnNzNtqpviXEOytl'
        b'ITTnsIWOjFfSA5Zxn+ccrVhMc5YscmK8vO6RnQm+kXSnQ4E946zOEyAR1A+mpFIYdzgsh6cTExLASscEhuFFMKBw0SIK7j0LmvNDBgyAhXDfAHQINjCwcCZcQ05zBY1g'
        b'd2ICqmAextztQYdkNOZCv6TUxNhJRqwHLAX7Md4D1LI0EMImeKYAF1rWk8N8SAEFPuRqffHiUBrY3ofpEw+LKdhml4s6RIABY4cw2OYM2E0eq1vQi7ACNcw0WBTIBMLd'
        b'+XTkqo8AxylYA6wIMgNrHO5FHvtssBrWJCaIU0dhyPDxzkJQCxpRT4QbUw+4G9SbxZ0XzeyP8Rr9QQ1FVBDodaiIcY9BL8C8eTEPB8popTIuaOfIXkLsytE7YjwHsz8P'
        b'd6JeNyEhn3iJFzFytF1HCklL7cxIMmqx68vI33Jj6EMYC7cKEhPArjH9pGhwX+YEa4eBMnJkpAdo0LqEZIJXBwhQPTcysLnnRJW8xyW+Fg3MTN5Wz8yNHOvuRw6lD3uX'
        b'DPP5o3hH0aYVO7337VwtimXvnT22YbZm5Re/i+PGvu+wzyP7nvukCP8ZI2rOPbx2Ln9zzJZNKvnUG1ffe+Xct1/o0xyP9v+48s3+12M1xXE+aw/mvnV81dFJfpUp/4lc'
        b'PdtlyFX+0bQpb79RkX8+MnXZ+jSPx73El8oXiH+pnX+2a+DhjJfmvp8UNdPnhU33t0TUyg41jLry1xhDkPT3eQkfVl8bseo7N5+mx53qf+7SuO67G5e/W1dQ8eTI3Sk9'
        b'b16R926+Ir/cOK1i74qBk2MWrVuz+olzVeHYorujV0hXVQWmz/3C/e25zQfUnjtOb7s1KvG92d9umvGDEkjj9uunxhY+HHVGkNzvoixZ++OJiYt+b54e+mRzAHqxAw6d'
        b'Ou1yZuOj6126JOm+/GyO1IvE4wOlfWKoB287I9fk8aC6j4RiDdahh1nhTwZEdFSU7AGbWLCxVwGBnjrBlXys85xeEsNjBH14oBq+TvlcQBk4DM+1UPtpQROJ5LcZnKce'
        b'+HtAESqbIj1OTzEhPdwZAmLoBfeDrbKYOHHfNkAMcaSdA1gNKikO46A+HjuVoLJNOAyfAjLIuzgkwbUzUZs3RQFlQ3oCGmg7CJaBPWAtKOrdxncGNIBScucTsaM+aEwD'
        b'ewlexIgVGSoiIzVsgmdmE6TGsD6t/WFAHXiNSLcM7ldgHQRummQEokpgE1EzErxdZRY4UtepWlDEHwc2gO2kAu17ompvQWcwbt3gHgzPUMDj5PgsCdwjM0eZusKGYcv4'
        b'EQGwnIBhkpwwr2VwlAocaeUOg72sCDw4cwx6BhR0sTnZiLmAezNJ9bHwVH8zBsW8MIy4WBZDb/4IPDqBIG1gVUQbj5wTg6nSsxN1e/uxc1EP8LrUinMR2JZuwxflKYH9'
        b'CKsK0UkWt9VJcgQc4S+LNBF3VkRc3N051ClGRrgTbASLvh3NaBTduT/yuS3swd4S9XTkCVkBh5pw51zl2UdCB/ZXFv2JHDnSMKIptGUis34TrTjJsDrSs7U6spzZaRkr'
        b'sPVlNFqsPtgM9ft3ick0+tbaiXVWLvs4PQ7NC07lwiPmpFwO8y1ouSgplzaCDEJJCb5DwBpLei1Q04XoEpNBDVzhby8CJwn6D71ie8n+buO0/vGYWWspOMrAbeAwOKf6'
        b'pXCcQHsAHYxf9caochyK1T0i/WNX95frvhJs3hz1+XIn9w27ll+aGF7oFaUa2jDjQ3Huip9jcz1L75cvvLauqsfmC+MXH2pQZv121Lt+z17D8Pl3IjepvD3EU+09hut2'
        b'HDrp83G38FQ2/44kpeS7H0Fh0Q8NZ9Kz+3Y6kDrxpgg031nY/4vbI+7FzOr7x73YbKe85q3TP9hYnfnouOijWdV71+8vAN5LvIbVPx7ec0PlmLAvM/cNif9qu9SNsmCd'
        b'kKC37Cg8ZU6wpfHjek14uJuJYovwa8ENvuwyUO1Ge+N6UONDKbTmgkOERYvtCZfDsxSsfwIU2VMWLSOF1ka0iWm0YOkg4hHIpsOtlKTLSNC1C5wmJF0JYD3t9uDBiYRn'
        b'iyPZmsFimi1XuJuC2xrnw/2UZyujL2HaYv1mjCayTwJVaJgoRw+31jwMLT99VBbpbcLgeUJcGA3Ll4K9HHEh2OVOusN8F1jtHwzXwRUmpi1KswV39CW1tlQOD1Gareng'
        b'JGHaYrvAikQicipsAM0yU3Nz8IqFtSyonTOHMgAfBq+6cSxbqBsvJkxbbNdRgPJ3ZYyeArfxW1Hc5Kgowc1xeAQ0EJItWDyU8myxAf7O/wjJFqGFIr2YX9terIAJ7Ns+'
        b'zxbuDlp4tjR5TPu4rEUWl+0tMMbAXd7qc9MKs5bxUqhnsMRnUKwWS77ipJ6t8Vn5DGMO0uqAf+EZhoTP1ikztRRl1Yo/y+NvGbUdeCbNKOmDO+UUhhBmCd0JwZXQnMDq'
        b'ibf0eQmznPFI8kSAyhLneY4Q8Siw6pVJ8Lg2egwaqDmlzI5x6c6igXotPCblxamubbjIaLthHFXy3ch1Z7KKMEy5y5GwpcztAaNX9Pad00scuePSm8HdZUGeByRZx6L4'
        b'+Xcvem7O2F6d/VfqebheVvNr4aSEad/8qX5yufM735dp/xwBTx48fH3rpI+v1GRt8bjt+0bBiRjdtG/uXfGLul25uPazqRuX/bn/P6LyYz+9knU9f2JXdmfuBf+52ovS'
        b'7GE3V6yfPdSjb8Dwggc7o34pfbCj+S3o2Xjp7XfvjHjnduObtZOm9/P2LNiUKxxyVLD/iE5x9b+LN/0k2Xk8WPXe0cCtjzXXNG+OGH3k7bf7Q+HWRSH15Wf9v/6zblf4'
        b'zX9t/Npb0jQvxzdedunJ+2GV368ZAbxfOe1fb5/+/cnyS1e3xhjGXX0tsefS+Z7fH+nywcvqq7vSHc/2Hp+fFrvvlJRPZkYWgVVOcC1SRHjDeLCWges6IU2HVPHxCeFt'
        b'nKB5MwUiWAPLKPK3FtaDLS1zNDQfPJBknKJRgJNtJ1l6/O+0x2dOUK/DN76PVhOCIxUlJ6uz5YrkZNLr4LkspjvLsrzBvF5PWNS/CHmerKi72Ku7n9cYrxdZ3nDcD40U'
        b'8V2d+hcwC1me5mPTi8g3sMnJZrM03f8f1AFP84npPcaSEpAziSV7Z6w5fRceb3xkYCPS/9ejPr80PgaUgvX2jGu3xGD+C5IXVeJDSwTa9SjX3lmZL5Ri5k4vuye/3ndf'
        b'veETr8ILGp9D83YfG/Fuw0uL/5i1crvn7PfL+ufWxXQqH/xQtiz/xsb06qs31kj/POyRrPINuPpp5+CkmndqI476rm7M1CZOrZvoP/uzW/pPV8vZwtpdHvLLu4qLXyoJ'
        b'XPjJzeX94u5czxXee8uON+3znLdT71TEX38houCnihsP+KLJkk86rUIKBG7ME+DBIXgIjscTzWUy+8TOjBM4xsJ9sBDuofp5GWiCjThyThNsQKoGyoppMT3gOT6o9YYn'
        b'SDFzQQUaN0kdYK0cG4KoDjzzfPi9lFFksB+/FC6XRcf6xdozQgGqrxWsCG4aQg5lwnNgDXHKXxssZHiJDKxPBCU6PJGxbMkI/5H+E+0YnoyBVSOzyfguA82wmjC+4fnP'
        b'Mt7EVMZJysINYBs8Q3QXJTgI92hbMsBqWM04RrPgCLqHYop32IDsHxmxXKlJ5ErG7Bp+nAwWEv5jlb2SrAAwAoEr2MYDNcw0GvumIIbom3T63K6ThHHuxCIzaAsN/AMa'
        b'R5Ep3TUBOTQDKFIzjuA4C06o+1AMwikxOOo7HeU55gxW5+Xq4fFc51w9j+mCZ2jLgkEdLegEUuBWyUiAA3wrTF90m2AbC+siQRWN6rQFNqNqQ7UeLEM9zDo8xYtKPd0b'
        b'V34PHwEogk25FrGKX/i/f7Nav2gOT+lsrPQ9LRgIQijqIqIhfUikfWycOfNHt1aAfKjqQLqb3ga+WpllEGDnW4OdTp+jVhoEapVWZxBge8ggyM5Bh/lancZgR1jSDYKU'
        b'7Gy1ga/K0hns0lCvh740eK0ek3Pk6HUGfmqGxsDP1igMwjSVWqdEG5nyHAN/sSrHYCfXpqpUBn6GchHKgop3VGmNuE+DMEefolalGuwpJFZrcNJmqNJ0yUqNJltjcMmR'
        b'a7TKZJU2G7sTGlz0WakZclWWUpGsXJRqcEhO1iqR9MnJBiF1vzOLKs/Sp/0T/v0AJ9/h5DpOvsLJbZx8gZM7OMG0nprvcXILJ3jdR3MfJ5/i5HOcfIuTezi5hhNMtKb5'
        b'ESf/jZOvcfIDTr7EyWc4MeDkIU5+xsldi8fnaOpPH0WY9afk2GNRGvaxTc0IMrgnJ3O/udHmcXduW5wjT10gT1dywGK5QqmIk4qImoh5V+VqNce7ShRJgyOqcY1Oi+mq'
        b'DUJ1dqpcrTU4T8bufpnKSFzbml+N9dbKYd4gGpmZrdCrlRh8Tg1sgb2AFbVuYkO9CBT+fwAYOThz'
    ))))
