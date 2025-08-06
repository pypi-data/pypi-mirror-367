
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
        b'eJzsvXlc00feOP7JCSQcAQIEEAgCQoCEK9yKAorcqCHWegABAkRDwByerVWrLYoHeFTwBE+oWrWo9aramd5Pt0vKtiDrdu2x7bd7PGtbe2yfPb4z80lCIsFuu/vb5/fH'
        b'l5dO5v7M8Z73NTPv+YSy+2NZfr9ehZy9lILSUwmUnqFgBFF65mLWPDdq3J+CmcqgfTGWGBUfxbIWcyZTqZaYbPS/HpXNZy7mTqYUbGsJNWOxy2Rqsa0GMdXIcWuQcH94'
        b'kjczt3LWfHFzS71Jqxa3NIiNTWrxnNXGphaduECjM6rrmsStqrplqka1jMerbNIYrHnr1Q0andogbjDp6oyaFp1BrNLVi+u0KoNBbeAZW8R1erXKqBbTH6hXGVVi9aq6'
        b'JpWuUS1u0GjVBhmvbpJd/0LQfz4ekneRU0VVMaqYVawqdhWnilvlUuVa5VbFq+JXuVd5VHlWeVUJqryrfKp8q4RVflX+VQFVoqrAqqCq4KpJeyllsDJA6aN0VbooPZRs'
        b'pZeSp/RVuivdlH5KSslSCpRCJUfpqQxU+iv5SpGSq2QqGcog5SSltzwET8BSV11IZfDYoOpCQyllyFhYGTrmF1O5IbmhkVS4k9gGahorjGpgoIFmltfZT2UQ+u+Lu8om'
        b's99ISXjlWlfkFz7FonBcYsHL67TZhZQpCgXWsQSwHW6pKJ0L2+D2CgncXqScI+VS0bPYcC88Bm/BPnhKwjAFo7zgeOCThqIyuANuK4PbGBRoy+AVMcF5EcrBNPmjHJwF'
        b'4HJJUXwRh2KzGeAK2AyOTAIHTHgm4FlPuAmnSeEWuG0WvFnGoTzhVlb5TLAZlQ7DWfYsg7dAO9wa34ratA3VEgwHeGCACS6Cl+FRUyTKo4XX4GmU50V30LYSPFe73AQH'
        b'lrsvNzGoALiTBbaBzXADai7uGtgEtupBO9iZUCKNxY2GO3HIhQqOZMN9sBc8LYVX6xh2QxdsHbo9yMkJqkLDh+aUjWaUQjPpgmbdDc03H823B5pjLzTb3ggWfNGc+6H5'
        b'DkDzHYjmOlg5SR5smWtGpYvdXDPRXDPs5prpMKuMXCaZ63GxtrlufHiuA8bNdQg919+s5FLuFCUQ++ncR7xdKRLpFcCkAcBLE8/xnUdHblvkRglQnGBtq7ts5jQ6MmwN'
        b'h0K/4sH5a7QV8Qaqn9LyUPRL3ED2A582dzb1UfRXzMtJHwjSKS3GJv0ruxjnXShxYqBn6qf6VsF6OvqTOV977fFixNynfqu+I1o/73VqlDLFo4SGXHhdDQfQLLcnzI2J'
        b'gVsTCqVwK+ivjCkugzvjZUXS4jIGpfNym6ZSOswQ39phI54hvmWGOA6zQ+H5kfNtM8D+N87ApodnwGXcDLiX6/EQmvwI0COAvQwOK+ZJ5zMpJouChybNMPnglMOLwHle'
        b'loJJURFUBDwO++noqzlyxTwmlQ4OU03ULLBlikmIQfkQOAv3JsMbcDdC7glUAtzrRhJy4CHYDg6DjXA3GiYpJRWAi2QlwmfA/oAl4JqibC7czqGYaxmT4KVppikoSQbO'
        b'LcXrK64ELYktpQ2r58aA/vhCsuxlsJ8DNoJT4GVS/fSZKMtz4BgY4FLUVGoq6stpzd24QbbhfZQau+GH5s7rPJAo2lzxXslowfKYDNeNwtyA9PYDA+0lMkW09yuzWpd/'
        b'K7n7ZNCRV95IulQWf7J7nf7dv/w9/8XfefVdXP928cY/X61XZvcaDtR9x9UJr/iU7XDvmKkO4h/70+zXu4WDM7/clfZ3dUlG6bbdSyczV83mJl/8u3Jxy7LVwW/UhbY0'
        b'yauWXe4ucdu31W+JIiHzbxXfrthar92944mVn94+9pmH8oLszh++NW6aM2vab15P3N+25ofEnd8wYz97MNPj2oE/rLz49ZbWd8SKzh/u/vaXtb95t/Pw9Ftvxcg+nS/h'
        b'PMDoChwpjSyB2+Pg9jJpMUJo7vAG5QOvsOCzrhI6wxlwcIkWdMYVS2FbUWk5h+KDC0w0HTdA1wOCLc/4B4KL8HicTFIch3EeQnhecD2rZSHzASZHhWA9vMDHI29C6Glr'
        b'AlPlTnnDayxwVgGOPwjENawHG9YEN6O52gp3wm0Ie2cywAVwtEDiMcqMkejRsqV+pmPwwLAtXj/2N+o/tUHfskatQ/STUGYZoqrqFTmjHnq1rl6tr9ar61r09XoMpUxc'
        b'AxMB3PfrqS+fYFD+QV1Tdi9uK7g7Kaqn4YNJ0k7XDsaIr6hz2oh4ckdBV9Luojt+YT2cHsOwX5zZL25EPKXP71xIf8h5w5WZQ5JcszjXSa474oieWcd4dil9nL6Vg9Hp'
        b'w34ZZr8MS/KwONksTj6fcoU1JJ5qX4tx2C/e7BePsvXm93GOFR/zsq+J3ddkq2lEHHXKs9ezb8WQOI3O82lQxGBk6lX2FeV1vjkyfyho5qBw5pchVIjsfiglDNiX0ZnR'
        b'VTDkGzHoHvE1RgJ6jAUknqNceoxGXaqr9SZddfUov7q6TqtW6UytKOZnzpQncmocpkrvjRN9rM50nCsTOX9ZT323lsFgCL+jkPORZ0D7svX8+0wOQ3iH79Oe+RHba1PZ'
        b'iKvXHVff77/kUByBNfSDASOsA9w46jQ/jeWA3mysJMG3nL3UYsxIIjZSwdCzFEw9G/3nJFJ6Lvp1UbD0rgqekpIzFGyMe5cy9G4kxMEhPZ3CJX6MpRlKppylcCFhd8I9'
        b'sVHYlYQ9FG56z0amW5OEP8qdR0b1CwVqQjkZ6jqWXRPZVgzchJvIoJm7vbh6inyAJgOsSjtOVsdGZIBlRwbYDgiflcsmZGBc7MRMF2scGWDThHi2H7s2noUmckaNe25a'
        b'HKWZm3+AY1ChlMdvlQzUHX5bACa9ut4tb8GCDfUS347XDkJX31+w+hteqQx5dYfE/+0a3vsB7/Tx3/uvtiUtifkxEfw3RVz/KV1tjDaXxwLBcYY6irdhse+r21+7VJp4'
        b'XSh6b0NHCot6vN397F9YEu4DzFWBTvj84jgbCxTHpbzASRY8BF5cg5DJ1QeYXwTtqdqxLCzKPQk+G89ygdtnPBDhnsF2txLYXoqYQ5dGCZdyBVuZq3iwg2ApuG/OKkxO'
        b'SorAWYriwovwbAYzELzEJ0XXhEwF7RWI7WNTnBi4ER5kwGvgEjhFEhkh6+KkhUXx8CQ4ibg9V3iRiZi2dr6EM/Fy4FgRF1kFo67V1RqdxojWmhcNJjJrBEFSNRRBUveN'
        b'TCo+8dy0/mlXAsxxuWZBTAd7j3vX0hGhaF9JZ8mwMMosjOpZOiRMOp9rFqYi7BU6+ciy7mV9k/uSulpQXv5ISBj64X3oG2Ap08N+Xxh1n0UJRXpfGwrgjrINam3DKBtL'
        b'JKMuK9R6AxJe9JgV0PvbusDFK7oGr2l6JU/GTgRyFuFUOXL+B61khGAZ4T9hEX+NwW0vN4o6wU9k1TGdrZB62wqh14ecaVkdTAcmiRXqwALZrxS0Dpi5LLI6xsXaVkfT'
        b'w6vD1gC71UH4QETh9sBzfLgdAdAOxAvCnYpCGs7mzkEsEzzowaSmw16uNzgg07yYt4pjyEOl/tsnYKBuP1o5AiBCa+dMYKDI5y8i0dFu1eRXtoW7X9O6u5/cJlgXGzEn'
        b'mn/yXfGK0guCKzI/7rtyXRv15l+5+l8kStiERMObCaDdAtgSeMTdAtmwH558gOcDHAUXEGs2gKj3TrhTJm2lCTWSlA5QQevYYHOsK4HjGasNViCHG+BBDoFyb3D5Ae50'
        b'IXgJ7kwLKamQMijmCkYu3DpFwrQDaDxTVmhG9KJRbdQY1c0IoH1sAG2LIzCdZoHpmRj4uoxH1navHfKNvRsUNTgl60qleUruUFDeoDBvJCB435rONfvWda7rqR8KiBsU'
        b'xNlBKkePpalRtk7VrH4YPjkEPm3gKcNOAnLqrOD5w3rq23wWgyH6qeC5mxtBHePLWP/rCHwcH+8UROMwjNxwgfsmhFB3sNcKoZ1MDTi8i0UgNL5nF43bnULoOu0YjNa5'
        b'+s5J4J/8UMA1ibvfvd3NoBY0c0/+4SsJi0AW7FqTZAXQUJMFPkHPJILZV6yMtofNmjUEOmnIjEMolvCQ/eD4OgtwwpvwMkUDZ1ihhPUwZmURQByDRIMTSDQ4QGKSBRLL'
        b'fwQSIxC63cfr5HXJ3xOI7dElAUJ9Iv4gZ4VKaxoHig+jynTsZCCnibJDlWUIFsN+AizqozE0O0WRBAZZNhSJJUtKzv7PoEnOOBjklJvw6gMdrelYdVIJ26RS2dzCYiVC'
        b'QRfg1goFLbkVIjFOxqCM8GU3bpO7SYqLHHsMdEwItkwK7oanaLh9GmzXfFq6jGNoQcXu7soZqOtGgHvmVQS6oP7tVylukGBr+OYDG8L3e7+tcm2Qb35REZgv2hw4VRgo'
        b'+kqUF5i3YGOXKHF96pxm3py7jwmbuHF33T/68OQc7pI0LndT0V13nth3JLHM9eNXhfwN13M3hB/akBJCCY7w/1C1DwlbmP14Kn+BvSBENXjSglBxPlkEzWD3Kusi4FLw'
        b'JIesgpqIB2KUWB0Or9mvAvhsrt0yWLaOfMBvPtyEFwF4Hu4mrAhZBPAS6H+AVSjhGXMIH4J4EHjNQLMhlXDbj7IhNmZ8lGtqxeLSqIdlpdBBskgW0ovkywUsSjS5J7KP'
        b'PRwgNQdI72IZY/pQ0IxB4YxfTxJ3zET4ukd+Krs3+/0A2d1QyWBszm2hOXbWUGjBoKgAwW9I+H0u5e2H19GwINwsCO+JfF8QbbeaXOjVhFVfDy0ju3a7UBbcbhUjcrGD'
        b'cVYzZREjEHb/7jGM3e9TPw3F08vKXl3jyHmwiLqGqNNsaJ1Ryfo3qmf+Cc6DVa5ZUsLnGHCLjnb9haDpd3p+KQJHEcT7I2RdGhh+URbHyg8t9PA9uV88P/6HnouJTz/L'
        b'Y+VL5jy2QbAieONI0mt5gapvP0uaHbMp+TTr8ZtL3d0RmLuHnyl27231z1nZn9jaQFElYn7WW58hVoOoP7eAXQUl8DzYaANkGpdvgwcIkIMbCzwRiIKb2qIxCAXnS+nE'
        b'XeD8fNgeD08EF8HtUi7FrWJGgD0raRQ/AC6ZMAcO2uBGCxeOOPBMI4KIf0K+xBAhFtux1Eh6NRj1CO17jqF9HCbQvJiG5vtNLCo4rMu/N6Kn/tSy3mVDk5PNgckd3JGI'
        b'6FNZvVnDESnmiJQPIlI7SxBgiyYd4Xfzh0USs0jSFzkkSujIRTI3FrQR/ESmfcmlRFE984cC4gcF8eOpw4SgTGiDHSQXYacYOSbKQhuwQNyIINnnpwAxJmoS1iinmvDw'
        b'3AaNWltv0GPFGQKuL/6OwFvihcUOzDmhQeJVV9N7FsjvXl293KTSWlK8qqsbNHqDUavRqXUt1dU0nXOtQ4ihsUW/etTVIh7QletLKasoQBiudNvixP0a9cOToDJq6qpV'
        b'RqNeU2syqg3V1T+GoezUBSKrg8VoQxaexmeoe74BbRjxtBWOBAQixz+obfaIX0BbwXdsrseUbwQsj/hveCwPyXc8rkfMdwKOh/QrCjlkkkwYc4JOcAJe5ReXwR0JxYwc'
        b'BeXqzqwxCMeRNfz3NcaEOQwnOgSWnqNgKzgKroyp5wZSj1OTKYXLPC9q3J/C1brJZP3Vuyrc9G6NPLdGrCmYpUPsyeovnkQJPwhnqms1xha9WpdQolfX094vBGQev8Do'
        b'4Aef+Wr9GlOjoVVlMtQ1qbRqcQpKws39wb1UbVxjVIsL9BqDsZ+pL0ORX7yOVsA33T5oZbfojC3Z5WiaxTG59Xq1wYDmVGdc3SpW6oxqvU7d1KzWSbLtAoZGdSNyjSpd'
        b'vdNyOpUR3tBrZeI5CCZaUNn5LXrdP5PPWWXL1AjixLm6RlWtWpLtkJZdYtKvqVWvUWvqmnQmXWP2LKW0FDcK/SoVRmlRfblelp2rQwOmzq5ErJ42IXeZql4mnq1X1aOq'
        b'1FoDZgC15Ls6w4oWPap5jfUbemO2wqhXwSPq7DktBmODqq6JeLRqjXGNqkmbXYFykM+hkTeg3zUmu+LWQO1K3DqsdBRbGoKiZOKFJgP6sNau8eKkCVOSs0vUOt0ambik'
        b'RY/qbm1BtenWqMh31JbvqcWz4Q2tUdMoXtGiGxdXqzFkV6q16gaUlqdGQtIyXG+MJUpiTRPPViPYgccbjAbcSzyk43OLZ5dKsmdJy1QarX0qHSPJLqLhxGifZo2TZBeo'
        b'VtknoKAkW4GwBmqk2j7BGifJzlPpllmHHI0RDjqOGo5ZhmFYWm5qRhWgqFJ4HGt5l+FRo4cfRRbl5ZbjNLVa34CwIPIqHisqqJTmt6C5sQw+WQsaXROCNVyPZdgLVaZW'
        b'oxR/ByG5Wpnlmxa/w7g7i8dj79CJ5HGdSB7fiWRnnUimO5E81olk+04kO+lE8kSdSLZrbPIEnUieuBMp4zqRMr4TKc46kUJ3ImWsEyn2nUhx0omUiTqRYtfYlAk6kTJx'
        b'J+TjOiEf3wm5s07I6U7Ixzoht++E3Ekn5BN1Qm7XWPkEnZBP3InUcZ1IHd+JVGedSKU7kTrWiVT7TqQ66UTqRJ1ItWts6gSdSHXoxNhCROtJr1E3qGj8OFtvgkcaWvTN'
        b'CDGXmDCq05E+IGysRjK1NdCqRwgZYT+doVWvrmtqRfhah+IRLjbq1UacA6XXqlX6WjRQKDhTgzkUtZQmd7kmAyYoaxA/lP0YPN6kR+NmMJAPYKxH01itplljFMdYSK8k'
        b'eyEabpyvFiXqGnG+Anhcq9U0IhplFGt04koVoot2BRRkDnDKHLIbZV/ZGBmXLkStQAgjBhd3SLCUR0lR4wskT1wg2WmBFHGe3mREyePLkXT5xBXKnVaYOnGBVFKgTEXT'
        b'ZTLmiC9B/AmJM6pXGW0ehIls3hT7rAZbNnoi8tSIHDfaRURlL9To0Gzg+SffwUlrUBQmvQhLOwSTHYMI/agMRkTt9JoGI4aaBlUTaj/KpKtXocboahHY2mbcqIfHGxEQ'
        b'FenqNStk4gKaftiHkh1CKQ4huUMo1SGU5hBKdwhlOIQyHb+e6Bh0bE2SY3OSHNuT5NigpFQnbIo4Zp5lVA0WRkMyxhg5S7TwSs6SrOzTRGk2VOYkvcL51zDf5SzegRWb'
        b'uA+PSJ+IO/spmZMn/rIDn/bPZEOo0lk2BxKQNo4EpI0nAWnOSEAaTQLSxrBxmj0JSHNCAtImIgFpdqg+bQISkDYxHUsf14n08Z1Id9aJdLoT6WOdSLfvRLqTTqRP1Il0'
        b'u8amT9CJ9Ik7kTGuExnjO5HhrBMZdCcyxjqRYd+JDCedyJioExl2jc2YoBMZE3cic1wnMsd3ItNZJzLpTmSOdSLTvhOZTjqROVEnMu0amzlBJzIn7gRCkONkhUQnwkKi'
        b'U2kh0SIuJNqxKYkOAkOiM4khcUKRIdFeNkicSGhIdOiPpYkFenVzvWE1wjLNCG8bWrQrECeRrZg1J1dKqJXRoFc3ICKowzTPaXSy8+gU59Fy59GpzqPTnEenO4/OcB6d'
        b'OUF3EjFCX6aDN1objGqDuGJOhcLCwGFibmhVI3mYZibHiLldrJV820XNVtfCG5jSP8Q2NNLxFq7BGkp2CKVkz7EoV+wKj1O7JI2PSh4fhcQcLRaKVUbMl4oVJlSdqlmN'
        b'yKjKaDJgtpbujbhZpTMh8iJuVNNgisihMzWAxK6IBhN3TT0p9qOZndTvhCg5r3t8RqJiGhsdMWK+xRaWlwxlA063DDLtT7bzY5lwTFM1ysgmutPyfp6+HGvHKrAzBztz'
        b'KctOm34edrAWcJRjaNVqjLTmsRIrxhi06hDr1ixqw/lWB+vUDNlWtaEEqw0D2wrvcyn/hBG/mC9d2CLPtsKveJR/8H12onc+47taBuUl3KLuyG9f+nUjI8U/qL2A1hvi'
        b'DRm4DfbyDfh83ZZ40M8Gz+dSrmnMdWD3/5bqkJdbV9di0hmRlPLFDTw2nnkIvmgRR9Wq1n7hRysO8ej+EDQTQVwzYmOwdlxMC1lovWgQlkNZ8MnXUTZmt/RVyPvNDRSh'
        b'bKa5p5YmnVqsaNFqEwoR+tNJS9ZgZc5YcAyhZj9WslBMF8NKO4yqDRqDiY7AafZheoHPxjpGWpigP5SnlCrqmrTwBgI0LWKA7IPZeWqturEed4T2WjQ8Y/5kizCWbR0J'
        b'Ilxg7lNtwSNWCVFMc2AWOXNMI2aRMIlcgGVLlBmtZCORQSw1kM9pNSgD8Wl0DS1iqThXb7Q2xRJTpMMlH4rE2ZKdZUsely3FWbaUcdnkzrLJx2VLdZYtdVy2NGfZ0sZl'
        b'S3eWLX1ctgxn2RBDU6GoTEIRJfTEYMZaTSKTx0WigLhMjZCzVe0rNsnEY2pfFEnDslUPKxNj4cAq4tP63bFpFJfGlWYXmHTLyAUNtb4RYcM1GIPh+DylWJ5J0/QGaxas'
        b'f3YWb4EbOslJhdkLieyBO65vVuFEG4g4S7GBykTFkh9VzHkiDUKPKOY8kQapRxRznkiD2COKOU+kQe4RxZwn0iD4iGLOE2mQfEQx54m4WOajijlPJNOd+Mj5dp5KCj4a'
        b'UCaGlKRHgsoEqaTgI4FlglRS8JHgMkEqKfhIgJkglRR8JMhMkEoKPhJoJkglBR8JNhOkkoKPBJwJUsmKfyTkoFSFEd6oW4ZI10pEfI2EC16p1hjU2QWIxI9hP4QOVTqt'
        b'CisyDUtVTXpUa6Ma5dCpMQc2ptm0UE6M8HJNDVgHZ0NyVlqKkjDmHSPI4phc3Rqa+8abhwgZl2mMiDSq6xEHojI+lPwQHh5feAyTP5ym18LLBgub4JBSSLaSGoyIK7HJ'
        b'cISSSAm/41TgsPTUQs0R6UeUBvPrDYRTb8YE3qjWoGEx2pTSRYitNmoaNMtU9th/IZE5bcpqezaDllTtNi3t2aQCNS3GqDW1OKkUzRrehTPQnM3EjJq9Ihq1G31ZpTU1'
        b'L1M3WbXmhAgSLg6f1qbZan2tcy5ZbXUw62jIsHLJEXZccvqIn9iRSxZ5T/0ueYxHTg8eY5FDkRMfDAYMpeVwRwJikxfAI/gKSYkL5VfLdocX8xzYZA8rm/wxalOOcDyb'
        b'jBhj7mQKuXz8X8FCri/+T7POmS6hVCilmKzkKD2UvtYz+EsZ1kM2eg658OkWRCl4Cn4mU+9Cwu4o7EHCriTsicJeJOxGwgIU9iZhHgn7oLAvCfNJWIjCfiTsTsL+KBxA'
        b'wh64JXKmQkTuAng6tN73R/67KQIzeaQ/EUqmpUdsRdBDPfJyHBH0n4f+M+RMSy0uNp9j3cGZbqjmSCV9NhDfAxSg+l0Ukx6qX6CIQnk4SldyW9CH5Amx3InwRvHeqHeh'
        b'pHc+tpb4KsIyGZb7hp5KLzlHIcY5bHX6KsL1wkYXtybJlFHXmfhyTr5i/hefoKQ1ATxrWEzjN/qqLK+fo8eSkx6f2vkCn5fRa7APH8UlsonE/QsMxV/goz1f4POfY9n1'
        b'emt2vQE7y3AWfAnwC3wH7wt3XNpllKeqX4HQpL5aUz/qVoeQlc6IvZ4qWpqq1iJu09g06lpnQutYV7d61BUfzteotPShl1E+OSFT3YxwSFN5nasdTONPkZNb6ynriUz7'
        b'O7vk3h8DzTBb6YLGi771x5XzLMfKXCt5dsfK0JwpXe2Olbk5HCBzzXUjx8rGxdpf9zAdQ2PEK6Ibr1mjNpC7zLZR15CzHXX4GnMWknpUzeKxgcmy3FJGmA1rvCzXoC0j'
        b'pNIZefj0VUweQkBGK/qTyMS5OD9CVXVicjBWbGoVI4SdLq7XNGqMBpn1M7Yxd/4VOpn+gm2f5ke+kfrwNxwnM0tcSn7xJ2YnlFpTLR820N/C5AkTBkRWZOLKJkQqEFyq'
        b'xQZTrVZd34ja57QUfaiFlmFRSbEKFUFhuj1ibQsiU3qZuMgobjYhSaZWTUqpLI2vVRtXqvE+szimXt2gMmmNEnJpPGNsrCxAmCXOt/jEdVgxGWPbzrRTaEqspawAmyW2'
        b'zL7BNrj4DnqLXhxDH4ZZBm/o1yA521rQcrwriwhRmOFAxeg5sqzRGHWjTJyalBgvTk9KtBWzWxFZ4gIcEJMALt6g0SEoQ20Qr1ar0IdjdeqVeK90RZpMLkuKlch4P3Kg'
        b'2J2+lfR4swDBOBXz/vIabW7rUso0FUVmwDOIxrSXgTNzYFsR3F6SALcgnzGlQlFYKoHt8eVSsBXuLJ1bCM4WlpeVFZUxKNgJetxbHptPamVXuVMiiprxubKmNHylN12r'
        b'AWwJG18pqhLugFtK4fba+XFgy8O1blrtTsFnZpNa/1Luii8oi4NUNfF6eSJ9bT1LkWd3hXVuoUwaW4wqBy+wuauotMVcA9wON5B7uKSOjhpyHbopLbymdDBvFt0yOdiU'
        b'4KxlsA1V2h6PW7dNMt/SrAoX3DBwVc8HL04DGzS3Dr/HMZxAtcR8yx/4BF9GCQSHIcUK3zYjNOLgGydfFQDGq9tOzkkShbzTlLp5Q3gnPkHtdzKry23KgbdFgC1/NhBO'
        b'muJu6LrQBTfWexoE0Sxu4ubu/zrMGuZcfnpaG799adeSM//zYP7vRCsuhN95bel/9TH8KlS1NXNqXBu8Pn5tWXb2/j89sUr7+e2PFeWRv879bPntX9QxvrqXk069tbz3'
        b'/hXVDSP3XXfqTGnYb1NWS9zJldNQuAEcAu1j9+FZ8+DTlFcUqwHccCenqaULwEugvaI0E7bbzTiDCoJPs9fAzeWkmjJ4UcpHIy8psx7Y9gPPsuEL4LBraRjJEWRagGqx'
        b'zDA9vwzKP5zt8iQ/yoUcuVbCfrg/ThpTKGVmgQ0UF+xnSsEG2QPM+cD+PG9U3DanGUlsyge8wILt4ADoos+87gHn4IY4mQRujafA4WZUwRlmylp48EE4Tn0W7ADXQTu+'
        b'NWubyZhoLuWzggVeZsEDDzDxMeWB07ivFhYLtfKUF9xpgQSKSoSbubKS1eQikO+cWtyf9rXgUnysDPcHwdfOOJxNbOB4gHPgJdJvL/fpOB9Ra6KvSnPgJfRRsI8FN1Pe'
        b'9JWiHfBSA/6qAp6wfNjC2AWBK2zQvhK1lPczbolicvnwDVF8mHTU20qjHC/GmSn6HO8KFyocX4bzGImQdrB/JRDf8fXvNHRl7X5qyDe6L3zIN+5uUORgVOFQUNGgsGhk'
        b'chzK60Xnydy9bsh3Sp83ufKB8sweCiocFBaOhEtOhfaGDoUnoayeKGuHEd9Bwllt1aUPBWUMCjNGJseekvXVDoenm8PTh8IzxxWw1V0wFDR7UDj7XnQqbmTkSGQC/g0f'
        b'CY/AZUYiojrY7ztcLfGgDw+vwc5a7DyBHazE1q/DDjly+xT1qPPFmKuusfzZHTMmR3R3YB4IZ8KI5B9oIL+rcGEw6hjfUtj9qVdve7lJ1AX+VJbD2XmGFXlPIshbSc2j'
        b'xv9FUm6NEka5hDHKrx7jOJCEgntPJBSx5Z7kVK2qubZelWMHENYob4YVgKiuyuEQ6Xsh9AnfHyzkylKxlbWIQWSvXtqi066W9DNGWfUtdT+r3Q10u3nVNhZmfLP1ndjZ'
        b'hRwhiiRXyHAbj1Tvr6ZbGEa3kK7CSQP/lRH1qnZkfB7VvADHIUx6LySJbqDkkczSv6upbtVW3uZRjQxyGMOq/VV0EwPzVAa1jTn6l5vUZG2SlXF6VJNCUKT+CA6RpkRM'
        b'yGL9i42yAJtrtYUpe1SbxHgubcO0ZP8SS9smZOP+PQPmXm3H+T2qfRF4GsdgTfZeiMwCaz/CLU7QTtsdGazcyGFaLumMXQ7+37iic/P925QhFo9PxkVy1/eZFNDzKn2b'
        b'sjQwXF7J8dX5XZtxBty+w6TefZ29+NiQhEmYB/A8ODLTgQhzEydbaPDipwgNzsyHZ8DzHna034EEg5exPaMJbui6VGNsUF09KrCjqySGkFXMm+LLXsVulCi4S34kpztn'
        b'KCC2X3FeOJyUa07KHZLmmQPyBgV5467iOqND9E1cTHtoEDiHnfPImcIYu+HybZHbT7vhQlDALu5k6ihfypLwRl0sSIm+n8I1GPVqtXHUtbXFYMTi0Si7TmNcPepC51k9'
        b'yl2hIjI+vw4JYS3NtOzPMqoaRzktaMnq6/h2k+tpnVxMMHPYzi1vIXjzsNy1dFV6IZmeh+FPKUASvpvSRe5pgUN+pacdHLojOOTbwaG7A8Txc90JHI6LdZDppyGQ4+XW'
        b'1xuQEIklqXp1LUY26F+d5XimWE1ulBDrZEiIJRKpStxkalTbCdpopAwaJNiK6btCWIY2qI0ycQVaajyMxZrxxpumubVFj+V9a7Y6lQ4JrTgrEnD16jqjdrW4djVGezzV'
        b'CpVGq8JVEpkQH841IHG9HrUJYSC0oC1VWORgXAcPFTUZNLpGgjdtxcSxZFJiUQ8KLK1rwuqh8d/mxRhV+kZUpt6K3nB+MVbiGrCMaVhuwr2v1avqlqmNBkkW7yH9QJY4'
        b'14G6iReRbekl1my4piwxubCy6EevrdhK0eCYJVaQX/Eiy6FJW7oVTLPEWGWMhoaI9IvsD0na8mJARsI/csWLKvTGsXgatFES7SF1xIuLFBXSlKS0NPEirAa25abhH4n1'
        b'uZXSopniRZa91CVxi+wv0YxVPrZMsOKBDohxQfuj2rbsaCGhzjYhUEHgaKjTa1qNFqKD5xXfSSOwlas1tKD5VtcTHQiaHpyKEb6W2L8jgy0Tz6QVIQQkJyuMquZmfC1V'
        b'N9mmEiHAgSYOfaDVAlr1GmJxT4WGYaUGERL1KjTiFoCTka+VtxjVNBgR4FYbm1rq0cpoNDWjiUTfUi1DAIiASo16V6cWtyCaS8rRTcRARTQ2BrrZGoPdJ2XiArTorAuK'
        b'lLIHQ6zPQaCC7QPWaVEHaNOABjWds8ZiDbCljrSE3uWZ2mQ0thqyEhJWrlxJmzSS1asT6nVa9aqW5gSacUxQtbYmaNBkrJI1GZu1EQnWKhKSEhNTkpOTEmYmZSQmyeWJ'
        b'8owUeVJianpKZk5N9Y9qW3zKTUQcfQ7sKjGUSoqlsvL4Iixq9scjygbOlys4TXA93GLC2D0TPJeYgn6Tlk2ikuBmcJNoLv5axaFuPCUk9mOu5MVSJnxzD1wNh2dLSstV'
        b'qDChX3NhG7ZUVSydh293z4vB16Efg234B5E1sAucc4N7IaJrxI5fGdhaDwfgjgywkQixLhQHdjPd4TW4lyhXMsCLLDggQ4JwEb5AjmrGVrCYVBjsBFvACTbKuMnblINy'
        b'roZb4U04UAK3SWFbmRJ2tDr2cg5sK0elt5UoW5FTUVoM97IpuBVs5MPjOTr6JNCNSHiQL5MUgxvgCI9ym7qsmAmP4E+QC4aT81vhQBHctggeLGFQLLCPAdYXg5eJLcAa'
        b'2ANO8GFbggxuQR+MB/3FSN5vY1BicA22zeaw4SEPYlVNEJAHBxJiGRQzMbqQkZYJnyVjG8lyoX4ViOR2cY12km8tZSKahU3gRL7BA+71qIWX0IfRV10XM2dn+pgw6wBf'
        b'kMMXSKqHDHbCS6XwQhzcxaICQMf01SxwBrycTjZvuFrURxkqjkauKL4oD6yH21mUH7zK9ioGuzWaigK24TbK1yjtae4o89mY6L556Dnm706tYr++XSd6THvQnD/4ov61'
        b'vmNx5ce++8ZbEHAppfnmPnnR0MCTu/ct+ur1z0M2n947ENIfHS3/P1vhW0V/6nli413moku1by2I//1b5w8rPN79pL3p/MyAl3+IOLf/+31PBlT1PvtZaFJMQ3Gum8Kt'
        b'uFv+ZqK6Z5uE+bvS99d9kaid8rs3/czykszZSz5qu6Rurvh47T+eGR7+9Pm5NbsyDh5P6T0X8Oynq75549pfK544dO6kS/fnLvFdodr0P0i4hOnSu4JrFr3SRfC81YoQ'
        b'VizB0/DCAwxUMtgPd5TYKVtoTcvyAqxEiUvhwJ2gN58oUZJgX5qdeikCtFk0TK7wRCnRUoFT8BzoJ0yePzhk4/MsXF5wM61F2jYNDMSVS4uKykri4fbZ4IqEQfnDG+xk'
        b'eAVepu22gC15JfExhaghaJbhJbgLnGauTpBJBP+KbTWn+hnsOBjxsl235qnq66tpNmPU18ZUjkUSvvL/WPjKUh4VJO7h9BhPPdn75FBgagd3xDewK8HsG2v2TR6RJXUU'
        b'dE03C+NoBU367ieGfCN7jMPRWeborCtzzdE5Q745RJ+Sf7vRHFU2FFQ+KCwfmSzp4Has7PQakciRZ51ZMGUkJ6+DOxiQZRZkj0TGosjVZqxsiUG+FZ2eI5Ikaz5xJPKZ'
        b'Oj0+9A0ciZH16c8z+rDFtkyzMGpEmnI+93xe30IUzjELY0f8A4f9JV2LO1gjAuE+z07PYYHELJD0RfTphwTJw4JMsyDzypT3Bbl2rLE3zRq/SFnPLg5g5yJ2LmHnMnZe'
        b'ws4V7FzFzrUJmGm7ycDjXjP2Jx4z5KCH2HkVfxuz2Nguwj+whZEKN6zX+Y5od776yToefCKwj5tBXeHnslgSt1H3eny+08I2jXrQzKY1yFU1k182MSjhZtlor1OP8jGr'
        b'gxg8fAyP7rStv3U8OzoksNKhDsxzuzjjufcSG5mIv8b7ZwxiydRN6Y34b2zplFi3lQssXDfPgevmI67bbmfNngNH/DUvl0+47nGxDlx3C8eR61bZTl6Kaft5iFedhe++'
        b'0CExYhDQakBsKWJiVPYWfzGjEy9u1LeYWlEq4n9VvLqW5lqNTmVlmWIRNxVLeAeadcAaBdvhXvxBm4jMwyLy/2PzH8Xm2wNtFt7Uo2NsOq2H2H0HqKbz01HWAoRnW/Qj'
        b'h1Zt1dGrgq7HshAscTSbqmvBmg89YUx1NLu5sgXziZpmldbCuC56xDFcxL47P4hrawFej/T3a1taluHv4xiZuMwyOyoSFrfULkUDjYRIendSh8WIjLTEJIu6CA88kmlw'
        b'8UVjR3BtH7Et9yyx0mBSabUEUtDErGjR1NmgcZHdiV0HSciCHhyHidwTXGR/inecLIOzPyTPOJwN/Q+IJ3nqlepGy8md/yei/AwRJSUtMTkjIzElRZ6SmpKWlppERBT8'
        b'VUc5hTtOThHTu8LePGL1uXVSfk1pp38wZUrGUk2CrqSoDG6NL7LybsSC1NTVD0sZT4GX3eTgJbiNyBiID7wGbmEpY0zEWL4ACRkvuJqwaZPycHi+RFZchng3VDG2gmNX'
        b'+TgBph22u4FT68AuEzZ2unQ16DBUlFVYrFvh+h+DHSj3TtiGJA0e4s61XNRYFHNVsRgcBPvBMTcKnIbP8cvh7gATZjLDfLiGYri9qKyiBBvFSmRTojxwOYwFtzWCCybM'
        b'ZK5VgV5DbBkPXIA7YjCrKisCZ2MYVFgjh4PizhKT5aAvGZ5Hte6FL4Ed81zhdmk5EkOYlE8KC/SmhRN7y0hmem4uGomx3Wq5H5IJwKV52OJyEmjnrHIDl8k34Qu+4IwB'
        b'HgZ76bYVxUuw9WYhPMaC18HTk8k0SXi0GW+zS028y+I6iog4XuCZRD4XbETEv5KqBFfhThO2EwgPgKPZfDxIaCg74UuFpcWgfykauN3wEpbM2sFp9KVSuKMQyyeLA11n'
        b'IzZ9r4nYLYQ31HCAAifBLYoqoooM8AUipy6A6yenULlgI+LUqaQgeIzkNsJToB/uZq2DncRAtR+4pP3+H//4h0pHYEpgml1Tet/Ep7fjXWeQ7fgZnybUxHNWL6BMmM+K'
        b'AC+CQyUUkv2Q0GQRagvj52Oz9AnFSgQRhXCbIkaC4KLQZoNeAi6TQeTqPJaYmojAyJYGK+DelGJWIrhKMeAZCiKhDE0p3qiDl+Ep+BLfMkvzMMzktdBQ4+owRvQAgRfg'
        b'LjYFnlW6PR4bSRtiewncXIzFP3AVPE2Lh3Nj4F6Fq6M0ON2P6wmOFxKJsR4MgKuGYmlF2XxwLgHDUXkRFo9ZlAR2ccDFPHCYyJ2q5eB0XHHZch22pCPhUnxwi4mAZr83'
        b'saQuKi9nvsqlVs3QP+H76wW3lr9MH2EoBLtK4YBF9KdPVSAIg1sSKsrmxtBGeSRI2p9vf7biEDjlDjt8k2gz4Zta4OU4WVE8Eo65YCczg5ngDnqI7W8ZkrBOo8VRkh6J'
        b'BGc9I2MV3CthkTGGz9TCE2Ol4EASMyEU7CXFolbAK7gUEs7pYgWwj3494CY4KEQ9BGcDHboIbkg0F/L9OIYtiON+P+yHE/PKKsAMwaE/fecfc0LoPd0nr/C+eE0nv+Bc'
        b'aNm169HlkUEV3z72ve/9337/ycFDK06r/1DkM/KntSlfh7b80LVu44MAsYu+cv3f7mS8//jGP9Ypn/ntKrj0hZwLQxeyOYs++fO31PkKasW6p7OTq1ym/+Zc6eu8Tdff'
        b'272t4EGFR0XB7CDvpd8f7/xY2vNrQctHz+8PHRnq3N72p94IWcru15S/+HPEpz6/CDy0UnZVVf3VcxHl/zjdP1X/xty4KWfnPLgc+G5B1QPvkKYHdwK2XB06OPjA/0bE'
        b'3l5VyZR5r/33peE/xC55bWvV7NlLs14tXKQ7/OIO7RtbL/3mz9xndr/CnCmDv72Raf7Hpr9+Xrbu5rq8v25qrYq8PPBe7tRLy+8uaDi2Z1K50vNmYJJpZ9iCAe+7v530'
        b'6sVFRZkrdV/EBpTsj/48rSQwp1PncnpxSMUXc8HhjGZ1xq/XqRJO3jywf83yD0Zfjn73yU9yBouaNn178/j/cC48m5WU13bo3qK3WnIXf3jlxKkbt258sfCT57tMlfKq'
        b'z+9z//pJcP/InIPvrJF4EFncVIvA1/7ACEIo12nB/rLXA2zvDW6cDbfQcj3C+PvtZfsxyX7PCmIEzaR9nF9SN+7kiCsqdpQc6/AqdisZO8oDzpdTXvNZWtCTSptrPQSu'
        b'e8fF0oc+KDf4PGx/nAlOwPXwGfpQyGYmOBQnw2QjHgPmDj64yJSCQ8kPsDiIluwR8FJJaSy4tYRLMZcw0mFHOkmBncJp4HRpWTwzWkaxSxjgxbXwBDmlovEAVxCNsZ71'
        b'4D7B0jGjXWaRXaSlXmAjORSiBNucHQqB7Y/RJz7OoQYNON1smjUZbzddURN9hQaN06GadANeqlJMAIkOxRt2sMD5Yi7poAjsmDGmr0BU8TDWV8BjKyR+/26FxcSaDDxi'
        b'YovBOCfqDE+suRgT6UYDHFQaYwlErZHLpNUa6/hUUGTPrD45NtE8FJjZwaU1GFOHAmKGfCV9M4fjp5vjp98ON8fnD/nmExVG7u1Sc9ScoaC5g8K5I5NltAqDLjZtKEAy'
        b'5BvbVzksnWGWzridZJbOHPKdSYrl3V5ijpo3FKQYFCpGphZhNUeGWZA5EoN1Gk+aBVF2WpDoOKxmQaEnzILIO74hXfU9+cO+MWbfmDvBMX3CoWBZx8wPA4LpIy1XI67U'
        b'X5eYoyzm4lFhS0GsocndnTWSntVRMBic8p5Qfs/iNQvld0LEPf4HFg2HJJhDEs6zhkLkHbwRX/+u2CHfyH7fvoXD0mlm6bQrdUPSvNvJZmnBkGT2m+FDkhLyzdI315ij'
        b'Hh8KWjgoXHg3I/vq7NsFb85/pWJoauVQhhL3TG4WpGLVTGo2/l6SWZh8LzzqVGBvYIfniG/AvqzOrB72sDjJLE4a8k0aiUo5rzJHpXeUjwQEDQfIBkNl59kvuV1wu5Iz'
        b'6F/cwcLNihwOijUHocbFjoROHg6VmUNlfQZzaErH7DsBQV3pPZnmYOlQgOx81FBA+t3Q6MGY0qHQskFR2b2A4K7GnkaUHaWOxCV0ufS4vCeKGQkM6XHp4/R6DgXKRiRS'
        b'FMvp9vz+Xkz8+crbtebQoo7ZI/EpHTOHhZFmYWSPwiyUjAgCutzMgskW5dGU9wVJdvoiX1pf9Bp2XsfOG9h5EztvYedtyqov+idVRQ8DP/7Uw4ojm+5oFDu/Rs5Cm+4I'
        b'29JczmMwNER3pGE8IO5P1R31czOpq/xcNqvOeiEW/9neQsFHm+z1PHsppYvSTckmr6EwlbRtfQ8lw/YmCqfS7jS0jhtKKe1sKyu5DtobTi6X6HTGxU5sS3m8gOFJCxj7'
        b'HiMvELnO86qJ/2OCiKoksW8FEBZxxpcFNfHnyqMtL6ecLE0ygO2uy1kUy5MBX4DHM6pdiNZ/FRIJFGA77Ad7K+F2ZdlceGkOvKT0SEtMpKiQABbYEBVFXhyqK4AXFXB7'
        b'ZWoi3CpPZMNeLuW6nAF7YB+4biLGlQ8sBM+jqnA1xjTEG3FiGWC/Jpsw1IEu8DkwgLibZvrlk15/Eu0Nt0fDYzEr4AmEuqZQotRUwkdp4BlhiSxRnhy3LpVJcdcx8Jss'
        b'ObQk1B2DqJLllZDHwUHrQyGRcLumd9IBypCCoOXIg3vbK0vKYaIgJHvLgbAN/uy+9W08fpoyfXts+Cv7PY5+NeJyj5nDeezezdLieb3vHJfvUv/u5e70lqnPVbe3tPYr'
        b'b988+WvWlVrGCzP3Dh45IP8h4Knff//L4LyKs5/xcr1D+VcKQo7uvOqS2d6ayc/79NLpMx/98ettBztyzyUu/Ozs27zED2O3lq+Wf7Rketr0N59zuVNc/zVnjoviXdV7'
        b'xs/v/nnR5qdnrWs8ulSd8PrzvV8W5+y9VLX/1vsxv58370tz++gvv+b1PDN/38loU9JHS7Z92vjGZ9e/ePfX39z68NZs4+ntnW3PHxvUf/7Ci4b+D1qD3hvtEpwTR+Zc'
        b'WLkYHhp88Inq2dQ3zV2ja3OP3apO/fzKi3G//Gj7NbeGV82BmclT//w3/56mipjdU7//25JLXhv/PKn97yGrNv3xDy4jH80cuLVN4kObRn0xmtDo9gQXigmOMsBB2KEE'
        b'+0MJ/XYHp8EOmrRjwl4OroMX4UAaKVjnAs8hBsLHjrozo8H2YHI2FGyET5cT6u6EtCO54JwHeBYeoR+C2UXBHY480nY5YZHmB9KmXw+FgJsl5fFIatmZAJ5nS70oT3CT'
        b'VQ02w+ceECb8uZpG2F5CXohhhzJUoA8cpSjSyOXwss/YwwzsChblHs9yobxIxbXgBTe712XAJdBGvzADTq8kBsLhpkJ4vYQHu0odDvP6g7Ps4EBwgrAdq9Ngb8lDJ3V9'
        b'lrJqnwRnQL+YbN2ktiJBwH7nBmxIcmTwvMEO+vDNdfhcJT6YbTt1y2XD/ZRXKKtqLjxIejRvWaAdixfIIRxeCjxJ5iszfi7N34ATOYTFwezNpRr6nYlDkwSOT+G0LQQX'
        b'suDzJNUN9oVZbEQn1lmN68Jn4Rli/xmeWhyDhRK4owIeB1fwWxOgg9kyC/RKfP4/ZJV8rKzS+OdbRl2q6Xd17A8S0TGEMzpCc0b3F3hQAWH7tJ3a3boOFmZBGntU3Uv7'
        b'Yod9U82+qSPB4iNZ3VkdM0cmhR8p6S7pmDUSFNqZfy849EhGdwaODjtS1F1EojvyR3xFXfLh4HhzcPyQb/xIcFhPOM50nykO8hkRBt1nod97QtG+ss6y+xzkv8+l/CZ1'
        b'5XYWDwujzcLo+y44ztUSt6+is+K+G47h2XJNMQun3OejuC/dKT9RF+uIe7f7YFTakCh9SJhx3wNn9qT8Au97YZ8A+7yxzwf7fLFPiH1+2OePfOQTATgkwqHyzvL7gbjy'
        b'IFw5r6ces4XTzPHTBqNyzKKcIeH0+8E48ySU2dLiEBwORdmHhZnd+T0c8s7PqiFxxtCkzPthOFFMEtNRIuuUe69734IhcdrQpPT74ThxMkq8H4F9kbgBeFyicGgKit9X'
        b'1JV7PxqHYqwhCQ7FWkNxOBRPqpd0zTxS1l12X4qjZLiPCdiXiH1J2JeMfSnYJ8e+VOxLw7507MvAvkzsy8K+bOybin3TsC8H+b6cjnwd3Pt5DCowuINzT+C3z73TvXtJ'
        b'X9pQSPKvBCmWiC7FkQXdC3oa+1S9S4enpJunpA+FZPxKkPlJaFRHwYgwcF9pZ2mvb8/8Y8EfCKVfsqiwKfcCQvat7Vzbk4o46uGARHNA4nnRlcyhgFmDgll2fJcnzXdd'
        b'JYBNb9sYRjkGo0pvHGUhoP5pTJanlcl6iL+6j50vkXOWYTFV/jdsqtyDwYjH3FX8Tz0Dd4SbQJ3jZ7H+F09DIt7ph708+vqp0XqpzLIto7Vok/Vqo0mvI2nNYhXeNbNT'
        b'RpMdK/Ey9WoDyteqVxvwOWhai21RsxtsW18WlTbeeXp4F0xL6+5x9bWrjeT5THuOztUJR2eSIL+/Ap5FcuhzYCfYAi7AXeDFx8CL4AI4PRe0cShRJDgL1rPWToHriZIw'
        b'shKegbs5+FkLuF9GyeCetUSLqgBH1xBmD7Q/JoXPlchkLEoItrBWg5dBf0E84RJL4xHSl/ujBtSUvidYQBHeSoWfSLOUdKHY4AQD3EoC++DTYGCUUU0YyckcHzv9Fmpn'
        b'V0LUWvqkxzGPaAv3R3g/eMIdsX8z4CGix1oMb8CLJUTSZuofX8nIgC82kU6UxKkQV1lqwIWYYDtjUmsjrUq7CZ/PhbtL4AvVuP2sXMZa2L5WMyV3mG3AG9hvHdmMT7LW'
        b'3O54QwBCX13vtrHLc3vSa6W92Lo8g5Uv8WXlb5jjukgQd/LtmtdrTs4pUPQFrn7nlXd637mmFfsPpq0o/cY772TpHP+BrI4HqbU19xrmUFe3P13/UlTubz4LetvnHaZ+'
        b'cWhdYlzSf19UfVrn2sBXezS4SDw+fv3oYbjHu9e/b5fvqWJZ/d5X7r6urbk1oHq+stZVLVfJqf2fgabXXb95ivfqP3rdY90PaqhfDgRHv7TY8oDUWt0qu/O0iH8+M3bW'
        b'AqyfTQg3A/SDW4jo26zTwx3FEWkptOLl5afAgThZGRMNV98yxKKVwIPxhGhXhhsQ44RZgSIpk+KrKdDDRPX3sh7gSxYhYDM45/yQrivmuBoXkUrieAmYCZpf4PDIXhBo'
        b'l7j+04Ta1UaobeRZZajGy8yOPFtiCHn+FUWT53leBOEiShklOVXeWz4cmWGOzPggMquzFNHbsPAjK7pXDE5Ju8K6ohgKy+0oHAmL71tlDktHvimxp7S92vMpQ1NmdMza'
        b'XfGlCxWVfd8d1TMcKTdHyocjs8yRWR9ETiU1BYV0qbqnIMouCjrC7eYOhiWc9z1f94Eoa0QU1uNiFsUMi5LMoqTzMe+LsnEUEqOHRQlmUcJ57gei9PsubLF/RyGi1NFx'
        b'p7RH0UfNU/KuRCOHfNmLipqGiLAopMP9Zx1Lxifd9QzkfGp/LHmW1080vH8BFexnjLJbVcYmh8dZbPKkFqNkjuVxFnxNGj/6id+x4toeaOH+Gx9oaUDIecAOOWM8alCt'
        b'wD6t1h5Nj936xW3PEhc1iGOxL1aMaJ+B3qPECFi9Cts0wFt+sbI1mtbYeFKRBdPr6R1CAzYKW2/bd1Tp65o0K9QycQXeBl2pMaht2J2UIQ0i2VXihhYtYh8fQt3jHyh1'
        b'pVE3ODSpKq4Qreg5hYhPLy4rBf2VheAsbIuXkVdWYF8hfMalVedOXupSwxOGEoQAistkcAuSYiphG367FbHq0hjQz6bgAKsEXnYBz0WAHQS7zgYHguBucJroamPBBpaW'
        b'ATaCm/AAEaM95XBvHGpaNehcRa1CosbTBIeCNtABno2rCIbdTIoxj4L7wV5wQfPx7CSO4RuUvsfP49DcsmVghvDgb54YkQs7ey7vqT0a4FVlOOMy9/7H6vRFvGl+o6v4'
        b'VX+V/P23OWX+rF+e/fi/VWEtz6z+uuHzjxivPc2c/vYnL09+e9aSsgPvrnR/guM/DD6+BXpHrxalQrPS+Czrjv5+X+0LHektsxb+/q3tp2VvXHzj5Lk3FRlTpH8KyP2w'
        b'fr4b6/3TDwzLohd4rX+ZvcI3ohJ0H9m9+APl1l+kCIZK3rm5KOW1D77Znf/hJ5l/f1Defeuvb0R5DX+7cOTlre+O/O7zb95zj/jT61nn9878XXD1y8tvfvnu4QdfXP5q'
        b'4QermztVKz7c+f2J0qTJmzLCbl9Pz5Mc/cqrkxm9OCha4kWkRHAp3ZPMF0WtWMxOZyApdBM4Q0uYFxFd68UiHnk3eelc/JZeO/NJNIkbac35fnAtHg7AiysjZlgU727g'
        b'FBMce2whQd/suGhcej6ieVuQqMwtZ06Ch8EzRHbyDEvCL0THg41TZUUkmQ/PM+ENbh6tdD/qAneVxIMd85kV9DNE/BlM2DU7nUh7jWvgJVw6YQ24WCHFmhFmLGrrM2Rz'
        b'ATwDjxZjEisBO+EOGdxJOueVyGqE15eRdrkELSNEpQs8Z3v2BG4uo98s3A+OV8YlIPhKiC2SyiRMhPiPsMDmuhBa5LuOhmcPkWy5YFdCOYfiTmUGoNYcJzWvdJtTYgH2'
        b'YLibS7kJmaA3I5CueQDcwg+qbC8HJ2voAcljitDwnSKDKQcHyNPFFkkUHoWX6YdZe1JJ1YgUHluIG1bbiF8U4oI+ZjzYK5Xwf64YyaccNO40gWLjhT/qYaNOOEhIkxf9'
        b'Luv9YgEl9N+X3pm+L6czpydy2Dfa7Bt9Nyh8cLL19qWvH0me1jmtRzjsO8XsO6Uv+VxWf9b5+uG4bHNctkNm0SQszR3w7OBYNMe7p9Kq8D7/Yd9Es2/inaDwnsg+Vt/i'
        b'oaAsRLGmxOF3YU42d/O62COiYFy4p/IDUSISK6Ll94QB+4o6i/aW3AsOOZLenY7vyfRFDgcnmIMTRhCJc+127REe9HSo5E5IeM/kU9G90afie+P7jOcrhyZnXZn5q5Dc'
        b'2/NGJoUeKewu7Kk8WP4diwrNY5hDcr/C3/ltSO4HIbk/GLC1itcEPrMSOK8l8GbluNEUzo2mcCzGP6UFJppYm0xCUz5/XBTf/fuHVSLBCt+1iPKJvvqJjycRiWQfN5o6'
        b'xU9moaYdoMgrbGMbJnp8nE+/DzuHcZobfT5Uozbo+3DkUeycoCk3tuIxypqlnFdOXi7R49dbEd63/Ek49A8T/fdzZicS33Kqb6mrrqavELu26lta1Xrj6n/mOi25o0RO'
        b'URJ1+H0bg0DGiliZFP5H9qkwE//wFtXYzLVYHWw/xfAkg1js+ZLN9BB85Up5+vWy+g23s82PL74TGt6XOZhX9SWL4VnDuDerYGTuvO9YER5T7lPI+ZqDY++zkffLYgYV'
        b'NPmOQDoiTPuSwwzKaCv+kksFht8RxI8IU1FMYHpbEYoJnXJHkDQinI5iQnMZbeX49SPxHUHciDABRYmS2grHYjJxTDaJCQi7I4ilYwKy22ajmOCIOwIZXVEwqqjkW1eG'
        b'Rz7jKy5qfbei13Ah5RXft1LuhIj7fa9GvJLyVj3uQSXj3lzlyILF37GkHnmMLyns4j5Uoj5g/1dVDNz5iAuKV6Lecrkddic4tNvYFXuBhepSmOc/blapcTWNDMTwVuMD'
        b'sawKhkfyAwq7uB6UwMb+72qZqR4FjG8o7H6rYwR6hHyVhhsWYfYI/Y7p7xF3n0LO1yxEXb7GQdrsEaFle/B2qaEUXCmKL5IaPD1ZlEcIE/aCI+B5+jbFbtgNX+BrpoE+'
        b'IyZ3fHwaZA4+BTIpmR0Btlf///3tU5dyEwZQZg3sx1ZYi3nhVDjcrSRbEgtXgBMlMnA+MZUCe8opNrzMWA4Pwr3kqkTBNHCGbCSAUwb7F8dPzqBH7jx8UQHbi7CQti2F'
        b'jTeImfA03FS8Cu7R/Pm+hG3AF1A/bNDQj6eKXn1zPaO01yirS6wTpJycOicgTrfk5LbE38ww/bHr9xu7N3aXdXf8al1ua+1cuLGe9zS3Ut7pV78yMd+VxV9wisdqzKJ+'
        b'sZaflP8/Eg4he7GI2ztuscgwfQVtkGEZ3EQzCRfRtD7roL2tXwMuPDWd0Nt58AXYY923B8fBdbx3z5Q+BU/Sit/TLQKL8taiuE0C/S2wdwWdegEiIREfUaOTlzBb1Grw'
        b'LDg04RVO91a9GnHr6mpykDqKYXnPHBu5xXRzhjclFNEErm3mPV9/8tr3zCPF3cUHSoeI4VtE/7I7s7tW9rkN+SaPhVcN+ca0zfzQy28kILhrdtf8jic72CitrcReqBpl'
        b'46+Ocukr5T/y8ipuG3HCmXYvrz4lYDCCfuqLZg4wKbD8fv0hqjeH/5C9sCR8FxMtD6bFXhV7MWcypWAFUdhaWCZTzyVhLgq7kLALCbuisBsJu5IwD4X5JOxGwrS1MA6x'
        b'BsaxWQvDYT76ngv6noB+CVyRrGTIGQpvy9c9LKk+tC0wRQpJFVpSvXBYyVW6KXlytsLPEitQyFEsG5Xyt9rcslj4wla9WHJs/wzbRONY/yt8ib0vnsXPeshvTbf+sq35'
        b'H/p9OJ6EFQEyr0RKIcLlqxmKQJyOfoPsv4HCwdZyyD/Jzh9i5w9VhCFXbBcTbuefbOePsPNH2vmj7PxT7PzRdv4YO79kzP9wfxWxMuYshiJOxtT7LPadTC32UcRj+J0n'
        b'ocb9WZGl1fSyJb/0n81PvuJnsfdF3xPmyV0UMgIT/sQamwuBAY4igcQFKBL1okZft02SVMQoISZZVYAkZg1i5SmHPXSbagFbO8PaXrs9dGxfjI2+hF8h5tp2zl3+jTvn'
        b'44jF+GfkefTO+UwZ3iO/J8LXAM1l3vQxSg1jGyVi9K1lzKmRFTCr6cjQ5U8yvmeKVvITVYte1HEoE743A88tLXCwl+SgU0My9wWEl9tdKEWjqwBeAr2kpoInJ1MzKVE6'
        b'j6qpPapZSX1ubSXBZ5oPnq7jGDAvOMP40UDdAUxRwC5sAemdYvfwMye3zQkt8YzY6s4qnRLwpmfDRZ/amsKPVNSF7jMnLxxOTIzkbbzzzvzfzUhLZ+XL40pXJvJLG2Pr'
        b'XN9c3HDlaukr7q+ciRcn+V9ZKtjpt/kN7ucXGKv/2Bp6PefNv01KXJeFSc8rMUK37Y0SN3oD9cxy/MbxchNmGViUayXTCK40EAFUhm3zgHZwrrQsHhwDJ5AsF830Dski'
        b'cnNUwxzLRbMqcN3+QNoiuJPsfM4E1/JpDeQWcNluxOjRigrkNIGeSHIlDd6CB+ppi0NxMdLHY+lsKFPAJPbUCrCftkt0DTyHDTDh15jBdrKpvA0f8TrACgGnQG9hAtlE'
        b'dYeH9GN5ysAZfOpgLwueqQfHAluJCPokOBkA2hPqEPHbklAEt+Hba1uZYBM8FPoAP1othjdWg0Mq0L4S1UK4JFQX2FmB6O+WCiRqc6nMEi6SqXeBHRLuj/DReImMsyrk'
        b'Y1tTjmaFVlM0EV3sTYVFdrD38PH5JuGBx5GX9yWPEkf0TB0KS+xwH/EN6wkf8o3ocz+vH4rJvKJ9s24oZy451JQ9FDR1UDh1JCoJm/iZPDI5ri+/b16PDBseGgmPIvZ+'
        b'LD+hYvyJkfDIHk4He6+HHZ2lRbtRDjlNP8rGl3tG3cdkKV3LqJtG12oyEnuwzlSctLBn2YOyM/yThjBSAtNu+2mRN4ORgYW9jJ8q7O3nxlLP81N/ntUfi9EQTjXu2gTW'
        b'QuxnyWrrB5+4GzNusnD/Qtp0yKQx8/fjjIXI9Huoh971/Ymt9Ki2H/qJbJvkoIiZTAc7OgnvhSTQDQy1a+B4Mz+yn9W6TVYLRDZQeFTTZqOm6bsoC/r7IaTIWsh6neff'
        b'1R43/PKsurpZM6GVGtycYtycMcs5/lgRJG7QtzT/6+1ocGyHatWj2lHm2A4haQe+zPWvtsJi2ohbbWwxqrSPasIcB5hetH+Rxa5RJS5ovSQ2YXv+sxu+jT9O8jk0yX9a'
        b'R1/zEGeti//zYy00db+2xgXfnBDcFi8vbZw7j9Kce+Mu24C/dW7bC1a5br3bxsDHNxzn7tkH3rzd8a4I9GzKvySJeLe8MmC3rKNSda+URf1dzkl5JkvCIOQC3oBPh9oR'
        b'C3Bd5JRegJ1uE0lVRO8z6m1PFsas4mAOD1OFeh9KNGnfk51P9swdDogeCZ6ED43Kj0zrxgd2+3LNAdJBgfTnW8aZh6ZVwbTbgqrz+RlbUP+r6oNx4DFefWABjxoBB8lx'
        b'mN6u144UhS8gpyZ83mrtO4TLMyjG1M2ab95bzjFg/u9/Dj43Bhx5ogUb6pHEX5pYl7hb4lvp5/ny72eI9iYf2pDCor4DHI7ygIT5ABtfqqkCRzBYwN1Vj2IjwDUNkeNn'
        b'gF5wE2v7Y8EmsVSGd9w3MlPAenBkQlncq5pcCtSsUVfXalvqlo0G2kGQYxKBpFgLJLX6UDHx+HD2eaU5Ons4OtccnXs74vbKoeiKDvY+j06PLvV7gshxoDTKIVfofkTs'
        b'fgyL3QuQs8Be7G5GwBT4k8XuhzEN1pR83UBZhY29tCFpSs76z4DT+N1Ai0XYSNa3jD+yqFZddc30p1cIKFpFpa4Bp9lw0zSKWkOtmbOAnH+YAc+6gdNMeAxcpqi11NoA'
        b'sN9ELoJ0aeEmByEDoZPKmHIpg5KDLVx4FXZ7gvVscitstw858pthqKiJ1yGsQO44fSyk7zj1cPW+v15w/vEPaGMn893hBquZVoebTlvhQXCJBkT7C06gF3bz4H54IJ1W'
        b'KpK7R5vZ4Ky9aixMDdqZxeA03K7pvjzANLyMMi0waQbqDqNFEvPOveW7NoTvDN+T+zSDOa9LJHpitUiU17Vn/dGT2wTmmoLTkhmZgdyeBYJK90B2yiuV4Bfe7H6Phsux'
        b'jTWFnzbUtDU8c1q9ob9Mzb7jAya9uvG1mfPni90UW34ftORKu88hsT78ndZ9Xd+/+PisGc31zx54bUd9hEEQfbL55JyFjGeXbbxy4UoHqyFWtuSVM5dLL5eKn6Lytwe0'
        b'T42+O3vGndrPaqeYxL/+Ts5ipQ++Y+S+K6dy/mvSh0u+lriQLTV4dCbcSrbULNtpaJqu0FtqnT70mdCeUnDGzrwGOA522OxrHGwg6x7c8pVPLDv4JFuW/SZ4mYg1Qnhx'
        b'Kj8Wbmfw6SMY1rs9YWCADc/BZ6R0pc97wQ5ypBZLRghCwJlicL0KbLfWzKUSwfPcSfGryKmR8MKYsasui6bgk6CtAiL8gBNwy0x7heB60IdPc8LzqyVspyIMIaO2nTNu'
        b'9Uq9xqgeFdihGhJDMMwAjWG+XuFDhYR3zPwwOOyOSEzo1O7VPSm7n+oznnuy/8kriuGEXHNC7u36N+vgsruhMYOS7KHQqYOiqTaS1ueDz1kGSC+wzs8ccDMHZF7JHwqY'
        b'fic4tMt4ILOPMxQsvTtZNphQPjS5YnBSxYho0rAo3iyK/5VIhvfaPLo96HCf4leipBH6VGbP5CFhVJ/wXHB/8PkFQ5IcszDnfWHUV36opXaojkujOrZK32hwSju5VnRn'
        b'wXcYSenrkbPYDt99Z/L5GRtYe7iR1HF+Aqu8ju2MiJEDHAyrloXoWDACZMrZFvTHdjjAwUHozw4d2utaEKJj53II+hsXa3+Ao/xHTDS5lJNLrYlSeAvsZlGS2VQYFcYD'
        b'm4jtaJIE93itjkNoZT88S5koU3EpwYLwKLi1CCFHqhFexshRCTo0q577iGnIRYl/fNZtoK7bqmPfGJjflS8q7RB1h99Y/JmgwaOvlDfHlKVINLju9ogIy3dNaXNv+L/N'
        b'vQdclEf+P/482+h9gZW69N6RqkiXXgQsMQJLX0XAXUDEGnsXxAJiZFETFyt27DpjemOzuQCb3u4uuSSH0cRccnf+Z+bZBhrvcnff3+ufMuw8z8w8Uz5TPp/5fN6fsJpC'
        b'dC4zoEwCDUJoA3QuI/KCIUdzxOZnglPu4b4AzRGi30xTjnUcsBnug7ueQu9r9Oid2KdPoHfyhNB7KEPv4wU21BTnEYGvQuArtxu0HeIpBTM6uB/bO406Oo+zKYHz5x7e'
        b'J7jD9sHDlsF6xGag0/yUYJZY4vP4barUgGKYae0OuxAnWoQCsYaV/jsGWbGhae9xxEp7/55tVoCKmUBt2j2OyPQ4etRmgOgNy/OMCM0Z/J/Q3GPWME86wTHUReioHwxU'
        b'gi7UhnB41ZlyBv2l4qUP5tNSfC3rW1d+vrIP0dG+N8dfVh/lOVWbBrvDw9Y8x1tfkfFZebmhiH6tJzw5VTKW3H174RTRwufcT0ZtX5EYZjnlzao3GYDMsV+MXmmp0AzY'
        b'v3F3akBp704ZGjIhlyVqQrLVIyTdY0JN8WpqetaG4k/pnI5oZ8zeTeYltxmxD0LH+zEnVxm3N6sjbUzgKSuRpysFER1clZfvCa9h+9Bhy1A9wjL+NwhrcrWNdXSmFVc1'
        b'4GyNKGjUJ7X5mNTu/15Si59Matr1pIHSFx+Thc1AvbRx/9+Q2eMnOw2Z4SPnfCtwuigIvNAyG+6NyGBTXAMarA0UiD/P62VJ8Snrhzfaz1deUDyPiG33m4TU3uQDJ7Oq'
        b'pETDI9YFL/NftxANV1eXr7mX0908JhAUC2KU9OdRXChwQmsV0fK8DLbD9dk5/jyKC68S81q5ETp2/yaNcTU0prYbLVP7olATmUCPyCa8IXQWqKazei2djdq7yiJOsgfS'
        b'Br1O5AxFKQKTlL7Jw+4pCvuUYcsUPcIynERYKl6NqLK5UfLErdJQj6IYesISCEkzCpbq09MiTE/3fic9kdK7eb6U3CSC7WfB2CkSi0Viu4itGFVmOsnZouplKrPWxpbK'
        b'umoJ6YmwidFwlUklBsOsbmiuloTpR8JVhlViKYNyiU0gVdxWUTP22FLd0ixqI35HsCqHyrS6rbJOhL1s4EfnSEqsQh6mMtagWIqr9OC3zpMUzeLm+mrUrVjJRNKCg1Yc'
        b'PMGTTJ7KEPuCxEWqTPAvDeYVeUzAZsn3wiUraKyFggFsKhrbCMyXittU19hQrWLXiNpU3OrFInG9H0vFEaOcKnaFuBJFDJJSUvJL8opVnJT8WWmS7XikdtCTmDDc5/gU'
        b'eb+J0lhN7qXInRJWJsU7A1ViHGn4/4Ydc3xs0laq73uyVtI/8y6wqFDR/PsuFcwkhr1GcIcUXrKQcCkWfJGem+aP+O1TjJVhJ+gGt6TNreg1vGhCUwbwAAvuWmLe5EqA'
        b'QJxrDAKwydUp34zcrJXBmbmFcHMeOBUId4VkFWYEZoUgzgruCNAAasCu+aYpGZaMKeY5dPa5BLsKKScrzAjmYuNLoiOPnna0RESGcijahz0fa2ZcsiBnpiLQERPBYvAy'
        b'IqiIVatIcuGyRJSYRdG+8Ci4SIE98GwZUWzwNgBDWgMzmjJ5htUC98PTcCiPVOAZeHkWysijaL/pYD0F9sLDcC1Rl5iX74QN59bCTsR2TOWglecsDbtKVpM+jIgPoIr5'
        b'pWzKstxdaufN7Ldmi1NRUTRF+0dHYWDOI+AkA+SCagT2ZwcHBWPMmdwguDWHhvuqKXtwlJO4KpcUWOcopBLrDrOopnIna6cCilH734UynkZlsik6EDwPN1Kge3UkUchw'
        b'BOvgyQCMT5nJsCoWYKgd7GBXgOtepMA7DnZU4LTvOZSwfJpq8TLG8hVsXAY3ofIMKDoIdntToAccdmO0Yw/AAzMR14M95lKcQDpCDK6W55OSVJIEakXgRQ4VWi65abeY'
        b'qRo4Ds6DCxGRYJCi6OACeB2VkJ5ISKk8AFzBWvO5QTTYDbdRRmEs0B1STsryrcqi9phaclC/+S9NXMXQXiBcBztxUWisQ8Bp0EGB3qnwClH1TUC92IlZv52zEctJVB43'
        b'sjzawGlSHJuF+G3qfR6VWJ7TFVlFEVKod4dHIiIRYdKB1nAIDSk40kqAM8GRWXBTNsbx3AZ3MiaR5uBWIVjPToBbpaTAPpNYqinxrzy0MEuWpPCZArnwpAAViIgrOARu'
        b'pcD+WLCb4K+AteC0CVNgntaG8UIbTTmAPRyA2d8NpNtXwE1wJyqBh9t3HZNn97x4Moy0I1+dnxlFc3ASDDaxY+AGeJFUaHmKNeWZWI1WmfIVq4N9GEKzyUejGI6JNjAO'
        b'XEWk5mzGiCIutKKNEhHtYXAVEy0LVf0cDffAS1IyaDawD+yPmIqO5XQ4vOmKMsJuuIaZbusKEgOyvbAUI4emeGLWFIkTeQGu5oNtEdE4T8ySuajmQO5BRgYeAJfq1BS4'
        b'FZyhKNNpbHu+ZV0VQ7r7wMlYlA11WhzohuewSu2NONJmsHcmvJrN9JYfOM6hTC3ZxXCTLbwAd5E2/xJlRFk6fWOABqFeWcllBgHc8BBFRCMGko7zgvsR5YbDs0w9esDN'
        b'aagey9gYpSkbUUglyxEtApvUljNGiLaiIxFpxTeCAVyNF8BVdYnzZmRn4ytQVmMiXEcnwgFPZpZszYK7UB5U92nwLJ51vRH+ZDExgr2zsuEOeApezkWjhnYBng3LCF6D'
        b'J0nFTQraqQf1+TSi7tkfOzQxc24uOAH3gvOhkVyKTjZMp0DfMtDPwNMOgX5wFDFeWfiqlg1v0nCbD+iFF6NJaaXL06ntzW9gCNmsealNzNAXwI0sXBhaEVKmLKWAzCCW'
        b'fCURPg9OZaOVhUexSoGslA6BF1cywlzUS6GW6/BZw+nwnCT1cn+gAXRlZ2IdYg6HBjvBFtCXAW6RfomB52AXMaVaBLYHU8HgeXC5BYvy6+ENuJ5YPM/KgFvyg2Yzevpw'
        b'c24gWoQoaqa1AewUOsIXYC9DjqemmWdrEJfoPLRGGMJuFthrALt07pO4M9kUp62Zh22vHjbOZ4SDYLOZJdacpqjWQCrw2UgG62ozuAiv6YyFz4Bb6gtztNlwKC9wnNti'
        b'2kTW7go4VAW3FcKtcDu20EcrmjW9oA2eIS/BQXCiMrsY7kA0gYjnCI21254DVwhKFuhqB1c04GFTYY9u5/DK54rb0pgFoQ1shL0mqBuv4l2IAjfN6oj+YGRGRQDqkly4'
        b'MyMI9EZnMUx1GIfyLuaGozm9kZGHNjpQkYZ/w5vHsymSeoa+4YnZ3rAXnSJBrxW4RYFbpWAj2T1cZvJ0ZV5u0pTJorxLuBFF88noC8D5huxCtLfS8CQ4I6TgjURwkQx0'
        b'BDjiUYQ25B1oW1+O9i94wgkOwJskl6i5KruE6YYX0JhfpuCFumTSC2VogzyjgWaznKvtA1ewjQMvhQSTGnvaOMBeMwwshjoBrf/X/eAFBmlsK7xqhCd4cGYeypYZFA42'
        b'gLMctGcd4NTDvdnMzn88xAf2sikqBM2OG2gygoNwO4FPAzfT7SfkhifrWChzL2dxJQOUEL0ItWEbTnrFX0yJi+ARsr7DdbnwFDYk0dbXAi89NuyFoAORMD48eHq4Y1EM'
        b'Wp6qXClXeNyfUfu8WQIvBjBgz4igsFDEFx5eRFNO4CIHzalE0l4/eNYA9qJpYV0IrmFz9I2QgaVKjAQ74TZ0JIEHwd5FaNZcRkcIPAFotEseyg4KyoRrPMBJ3yw83WwS'
        b'2XBPZgSzAj0fOxP2mmL9xl3gAtFktCcrQ9PsRXqG7JRFKNyNsYpeQERKrABkUAY3Sc3M0AoFd8LL5hRakdY6MtN9uTHFn/suDxGX6fsu3mri2l8GjsFtuOFrwI5GqnEZ'
        b'XM9gTl+3hFvQyS0Do7Rtz0Z75Zr8IFJPoSMHDoLDcBuRn1MzPWm5/zFEnokNH8UoWWNMucXgAvr3BAerycAdWI4PO8TLgSlXiq9ULnWH7d03v0hZYPlKtLjogDtXtXWt'
        b'kHv80xc+D5LfsSu80jZyMFXRXpn+1Yavt1nc/HXKg1/brSVRU94O9ml9sevrtx89+uAjpfKjn06sdmtmD5eBH5bSpQ/a38/6ZdknvLp1g+dfvXwkQ2y4brdkwx9uK+Yd'
        b'an9m4HUz/6v+a0dVp2jTU75vxBuENp09fq5pbSFY5Nd6efdXf2tIO1ex2qL8lY8fPf+ls/JGeFzegzIrj0MrDx92iNt2rvKzuCsfmx468N6ul9uXvB7wvNypqzY28+5f'
        b'/LsE0ZbeAuBp7cBL7nK70NGkSuyuMKztaHo/sbvGMCIjplb4Zvj6WM+D0ZZ/nJJ8bTwzOHR9mmfgFEPnjU200YuOLZ1ugfY3CwNMP5v1mXToTcvTws+OPzdcbThi3Af9'
        b'U4ZKu5vWuX2YCoLYn0WljHcM1gg/FBku7WzKt7r+vuK8mYHl7N09X70S4XtyQLxBecnjiNeAoLNx5tfr/176hmXklvq/vPKnj59JLtv59UB83dcJY8o9Lj+ufs34y2bX'
        b'HI9Hq6LeeKE2/WH5V28Fepx64Dir5I0T5kscM16pF0X1P3hU923cuTde2/Lwh/kVdcprGQ8GvvO+eL898txLGxtt4tsXfKCwcHd8aL1yUVRJdewz0+8l5Fz+sObmP9ve'
        b'WDjvl88Lj69c8WxA/FzhuYawP9R/4fzxa/8w9gXBKW2Hbe4WXe/MXv/FvJul96Z992XanbzS8Jbr7n+KT2t7y/LjDs7nCZvXuBl+fsuoJOnVnz0kHxStv/zookju8nHY'
        b'+htrp1+v/bvr3cTYl2ammPUJXq799nOTjwfOnLCZO++X+uyGd4zj4tzOXfsh+pEyoV7+Kj004590nv/AQa7Iz4aB1jgJjlnozDrBBnh6slIV3Bv4AJNuBuwPDsAXSCx0'
        b'9D0UQaO1rpXoGseAsy7oPIb4Fx7FSaWdEItyowrIyAVHTSRaSbZZNJlK4AWww6LVzAjuT+RRfNDHbgTrQ0iaanAWHDQBA4EZYAAc09xXWMGrbHCqFR5jrJO2w814bukj'
        b'TvQAGTgLb4FO5iJiHdpqN4FtIdgIKZO70ArtnUdYYFsd2EtUk+NDQ8h9BxHagqOBlGEuqwp2gTOkcR7c6Ox83LZW0AEP0UlADtcSlbVwsB5cDQgGR1t1SGasoHnGDFbZ'
        b'C/D8Ah2iybPzwLmA2SQbPDMLLQbbwJlwG/IW67mBjeA0A1KyyXDKBJd9lkDO3PkkLyeiZrjXwpsonQG54yTdNHQAGgDPk35bgM9/JJnYaaJ2GjgCXyx+4ItLOgp6TLEm'
        b'HL6sw3wU2KkVXAfEcsEudLq+lAr2EBtfxKDcXMyIuHUCbrAHdKuF3BmLSE8HgefADj2oE8qi4Vls5esK+xkDuC3p1agUtTIc+kSPWiHOFr74X9tdTcTtYIuqqlRmOuEU'
        b'ihKJ1B2O2iLYlnJxV8N5RSico0ack4ZQkHd7Xofxh3z7bl6fSY9Jr5mS7y3nj/jFKvxih/wVfmkKfloH/bEN/0MHj2HP9Ff570x5bcpwUfEbTgrPEqXD7GH+7FEbZ5nd'
        b'ezY++C4ouzMbXxKhkmRp8gilIEQbG4iQtw6KFSGJyoAkpSBZlypq0GdgxlCyUjBD7xmx9qpXBqTcnqUUZEx+sRCVcTtcKUif/KJGGTB9SDKxePKiThkw47a1UpA6+UWt'
        b'MiDhNo1yfPrvfmOxMiD1doVSkPnEWoUpBWlP/AZLKUj5t1+IlQGJt92fUBR54fZb7XhSUdXKgGlDqLpJv5ljcst/sxO1Rf0Y5Ghrdy+OErjLvOV2/cGDHiP2UQr7qDG/'
        b'oAHpYMQQb6j1ivlt6aus4ZjskZhCRUzh8KwSZcxsZcicYb+53bzu1h7zUXvn7prOVSP2/gp7f3nVmYUDC5X2MeTCMkHpMmMYkYOja19CX4J89mD6QOlQ1a2GKw3KoJxR'
        b'v5BB3oBLN+eg+b9MMObsLouS+yo8IjB8XbqaQGWsYwb9Bp/ie80AhSBAnj5YOJA1EpgwFDESmHbb43arUpA3KnDpM+4xls1QCiJGBKVDBnc8bte8WqZIX6BMLlXElI4I'
        b'qoYrqkYFzv1sWbp8hsIzXimcphBMI6Wqr6rsLjucdRjKV4blvIo6rXD0aa+cZTxZa7/5iDBaIYwe4imFMxR4PjDFJyg845TCeAW2oJ9cRq4yLOvVJFLj33yla2qK+lWW'
        b'MmwmM6+elAfNxfzHGzJTGaal+0nFZSvDMjQvJuTJepWrDMsbLihUCmY9ni1PGZb96hyloGRU4DjuZ+tnd5+ydbN/QNnaCjA+zZT92buzZVEKvt8+fUsVE0ZMjneq34fe'
        b'glfNx6BbjmBZ7FEUHNdIzfEVc6EtTTtgSLzfY85CpOY9PD9qwCRyou6s9jamjmJwAsg9DBbtUiUG2nsYeoJI93+uzyekJot0fRiRbrwB1ufr5llQ5YGNnrMo5nIGd1lB'
        b'7VyAWPl2EeVCubDBNsIF8cHJaNCFtradi6gp1JTFqwlXBdchLkIewaFsYBcVToUXp5OyNy7BPpLLuebl5fX788MpomRTJcYPO6aYlJfnbF+xmGHlz/lh84CO6Sahovgl'
        b'Hny1yHGTuzAikoPFPogZu0VVIg51PxFlFIJbThGRiMkH++F5W3Ru2ricFPPVIoLg7GUgLA88b7SQKbtvnhVq/qfLzJvK69fMj2JqMS8fu5r+cxi3qdz04fISJmVGhBkl'
        b'oMr9TAvKc96TsJiUB2PwwwK2eUG56aHWRHWZc0woPjVoYW5ZnlM+P4BJ6RaG+CeqLdYEPbw9o4l5WFaAqySjucJy07MVxYziD0THu2WEty4Bp+AxNw7FbaXBVfRYRtq3'
        b'ynDeAngwIhSLsD2xo6QexpX1+Vps+2DowqHK3W9McWa6qQR1wknMSYHDiBtGnBTYDHuZDrxUBW/AXmNKglnES+g/2BVNPuC3OB/28igB3EKBy+g/eGYewx6DCyLYRVPo'
        b'mHWLCqKCrNLIdx18sGJUUxGdWF7/3BxvtUuiI1ObYBfci//lIm5yoxNYS4GL9AyGb1wLDjvjG2TYDbdT+Ap5j5Bp+xm4Bp7Taj2txuw9tgnMWrWI4VDXzYLrwCC4URSE'
        b'GVgadtLWYEjIKD2c908PMKBsa6k2qg1eR72Fn66Ga+eBE1guEEUto5aZxDFi5j2IbDrBCRb27HQIq4Sh+BBZSsjAXOaQNpkbJpYHBhouY/CdcisuoGnjKcSaiu9uEK86'
        b'NURJW9Fkfrdr+o0SDADNX3HtguFaQ8PNdmdnb3eYenCo488zxs+d8S7NzBla9uP+n1d/tO/7WefPr3/57sdxEY0f16r2j/fO6ilwCOR8ZbHtq3hF1q1T1Q6+EtcSaZhd'
        b'YInhuIOB08K+uHExdZI77ZtLl9gvJo4cVyX+Ye7pLaKTh15acO/m7tSwJdJtK+o74IV9P5oEfEN98n6yXb3FubTFLq8k3C7YtfiDLwoVHhLHb79+/2zDK1fmd7e9WNM8'
        b'/MKiBe1e+wvT7OPdvp8zWrrnu6xFr5yenSb8592qJT8FBdQc/Pv8lxHT/fk/7OO4Nz963n7h5e5rxi7fF1usHmDbprxVaj7teOSmolrzSvO/nRyKi9x296X6hs/vr/mn'
        b'w1tW+W2Ru75d+cmahmDTRS/uLlMEFRgfeeBnV/z5vS9vPrheev/MW9M/PeawumnJjoTD7fusv/3s3bGU7V/k3sr/8bsvK8qq5/z68G2jX7o+Xd255B8PxgMPJPxR9U7V'
        b'139wCj3/7ohLes2OG4rtB/7iutBw/uv/fNtPoNED3oeO7uAYfO7phiN2GQxQQi84EktU/vKC/B1jiA8lFtgHumsZCIYzoBfe0uegCuARGpxtNGGMQrEh7ynG0iWoDO5j'
        b'DHcywHpiUBONOIp1mI3IhdtnY0kf9kKGsQmT2OA0lC9izv1n0Ew+jzHsb5gS2MEtNIaYcAeHwD6G2ewHJ8BxzFxMwhHSs+C5xGdgG3qTEnBlArCY9zRipWQ0kM1iMSCT'
        b'm0qXY8VWsA92+Ws1W5vnMo6mLoIr83D5DMgivjmi7Oa2RnIcwYtwH6PIs5mDNWlRD7aiiUygFokM39qLDU6i6SUnZkym5rjF4EwVuKTl4IqkTAGdoJvCtYNrpk+2HUJt'
        b'3BXNcHkbYbdEn02CV+cwgJD9Aobd6oGHYD8uxxrIAh/j4LaBs4T1ZcN1qxA7lQEvCwODg/EVIaoqHGDDrgbQxxR0YCHqY425k56xE9bJ5EwTgsuk33jgAjhIku3M5lIc'
        b'FtiTR4NDc+MIU+eAsp3T6PGBDf5qUEZELesIIynOlhD22TBcT2FwsrYg2OPJNP1UADyiYcXhCVwY4cXhRtBPTLm4QJb5m1xp/WouWrIv+DBUfU3oomUmlyVrbKuc4TUG'
        b'S+UcPA8OqWHI4XNwH0UZERjy9Zx/y5ZKDz9CxcFGCSpzHTeJ44SdNGQzyNjP2FN8+47mrlgZ3ZUw6uj8qSUfqzePWHoqLD1lhXLWGYMBg1G+A/nPXn30HuH7oePcCD9E'
        b'wQ8ZpJX88MHwwYhhfjR6zYA0yj0U/KARftSg5wg/YchzjC+U8Y859juOuIUp3MIGw5T8qSP8eAU/fihJyU/Qluqv4PuP8EMV/NBBKyU/YjB5MAVDgzz9o2OI6eWMCPwV'
        b'An8lP2CEH6bghw26KfmRg7MGi4b5seQ95gK68pki5OhloHyWHL0Mm1zjokHPy8Fng0fCMxXhma/6KsOLRvjzhufM+0/TRQ96jfCnD4Xr9UCUwi1qCNU/boSfqOAn3kYt'
        b'TcGvneQS1KgRfoyCHzNkreRPY/K49rsOuuv6K1nJn8EMxITvxAx6j/CTh9LJK3umyYjnY87xStRmd3nYMD/oX7zTjvN4tFOY9X3Kyc/mYQzFd+iM6vZV2ng8iHWy8hqP'
        b'o6xsNeTxnqUPIhgm9p6l96iN/YiNl8LGS26jtAn8VM2nceWcEd94hW+8hhEV9ViMCELkKSOCKMRlcm6ZXDG5z6b90uh7FO2WhjGsbdMxAoSV7X6TTpPulPcshaP6X7F3'
        b'2N/W2SbjHDPrN1PaB3dw1KCiMrdhvqdWlXWY7zXq6Xsstz930F3hOXXEc5rCc9rQHKVnmlqDvwL7nLN37DB5XHnn30BrIXL2CWAttzAPchsF32t4kL8hHmSePU1bY82d'
        b'32Uo4kMqozIsY2wTpJIkXHgWDmbSROeSWB5KUvGTXBxMp7FPOXLo96O/RseiR8S+6WtsWOI35UkoLIzBIfGQHoODWBzE4dINNQZiml9YJYaYSTGGMMSAgWj1EkVLogKH'
        b'9ZZUpmUFSbOScsuK5xWkFanY0upmFQdjR6pM1C+K0oqLGGbtlhau5b+Snz0GvIL96pEA22JL17AI8MpDngVGVEHBPXeK7zRm6TPKD7/HZfEjN6fe41FOnmOWIaP8SPTE'
        b'KWpzjg5XJQLjqkwluCpqyJRADJkSrA+i4o+fBJInts5jlr4M0Ipt2Oa0nwzZZsEPjVlmBfRPhiZmMx46cMxCHpryzMJ+oFDw0JJtlkqPUzi8Z065uPXz++uGnULGXDzG'
        b'vHzHPH3GvP3knrJn0J8BD3mVrFT3w9NHzpHFaf64ecuaZaaamIubzLP7mTF3HHMac/OUFcuMx7z85ZGynHuulk7W4+78KdajfOce6Tgb/fqU79hTNM5FvzAcr1t/RL8U'
        b'JQ0eN8BPDClb134bXMK4EY4bU7YotYzfnTVuguOmqMk9Ullk98JxMxw3p2ydhp3Dxi1wxFKX2QrHrSlb9/4UXMdxGxzn697b4rgdytxTiSs/bo/jAl18Co47ULYu/WxZ'
        b'anf7uCOOO+nizjjuokvviuNCytahJ0XG6Y4bd8Nxd917DxS/54m6HDcFK42iRD/44IdePk7miAKKacrJtXuFPFPhGjXiGq9wjVe6Tlc6JowJHLtz5HYKp9ARp6kKp6lK'
        b'p2ilIOYel+1ovjn7oXEybeZ/n8LhwwxWqJnTAwoFOuyZlni4ndg9RBmoD79cyrKY/Qx8HpydwORrXJzfx9AhCVaTADRYEgwuwXFHfPs8C/S/AQFNsJgYK2JPinNiDVyo'
        b'IheiOWpUYhHJKeIy4BUayYOE+yxPC7xhSIA3cNwIxY1J3JDETVDclMSNSNwMxc1J3JjELVDcksRNSNwKxa1J3JTEbVCcT+JmTCuKXDU1LbINxnXlkZYZk5A1y4l67J8i'
        b'OwLs4Pr4m8nADv+iHPt/t5wgvd+pdBRdJCxhEdkPo9Rngl1cRhoVTZnUo4yLeXPS2w4EOMJKN3JFjrE00eFlY2eZkdwiJ5xCm9e6yFliUyswqvNzUxkSGLbsvDSxGzq3'
        b'tdcQUF7NM2FlvUgqFfpil+St1RKpqKEKr9ri6gY/Y2P/YozyyLgGxJ4uGyukjfXVzYy/SuzTsL4R62Nin4nVTc2Mm0uCPOkfbCxZQmGFbpWRqKpVLMW6mSoT9U+iYmnI'
        b'uI5Dj9lVNa0q9qIG9GxxdZW4ZTF6ZtiEarW0UVJVaTiJson4ai2lrzyvcR5K7NVwz3JQn3JRv/CInrOZ1rWEYbGee9AGIxeqRM/VRInRBDmaYZIRka499lTfgEN0D00x'
        b'48wGcbOYGAOqMZI1fStukDaLGiqrdRCc2s6IU0N06jx44pxqlVPsoNM3mVF0ZTyw+zG+8pKEam1jBi5Z2NKErZmjhVXiWnGzNHjSVxif9urvYDejT/kKeq35RoNQVN9U'
        b'Jwp60qdihZV16BOVxBmo1pmmeiSf3CbmrdA3FxEN+qTGp/xTWzR1cosQiTB+IFPTZwvrRRXV9UJf9FPfFaZf8CSnlGRQpOQrE6tC+sI3XK8pftoPITKME+YQ/COca2ZI'
        b'jtaFKNMsNFeKRJV12Cko+SbxyYqmiBogtaWivrpKPScm5ipAYWMD404U5ST4qCjOtFQ9k5g+yWzWOlUVqbulorp5aXV1gzBS6FvF+KX0I5MwRltxzdRhuomJCcVV6g6N'
        b'mNyhmvmldsapjgkl1bViKeoRNJfRlCfDGShsUXdrSwN2mvkvHctbMCLlnAIscKViQqPcqucbOzH2kvCWC2blGYNJtZuGAmIxqRVQ+OXlFOq7hNuQaGo5BzKoLzlBthTi'
        b'voWhCVObu/znUsTPu3uZwdNLhFdBB9bWLNEvtq/JFB6Fx41JuV/PNaUEFOUb6p0b5WVbRrVMp7AIMgxueWLJGo8UxJBUW2amMwWGwGYT0A/3pZJijSoZg/hQu8Vmjk0u'
        b'VEsEejiX0pmMTig1M6CIFEZNV9uKroG7jMDepfAAKcw1GEvMqdBQXr3dVEsO03YgA4eMnlQa3JyrlUvp1RGsBWdwLS+ZgCMlKaTcf9hgITZlGBr1Mt/FbSY6Z6CHIngB'
        b'nnxSub4ZaqGLXqHwMtyD4WNOmMDNNWFiu7rv2dITqBDLvzdteGe6ebKbqcH4D7l3BO98avTss07T7i6vzzN/+Stn6PHnlWmVneVFvZYbwaMRl/vsLFXy2R9vl9659ufg'
        b'Iark3o/cvPH5D9pnb4q/Hcs+aPpjTe5H2/yP//Frt3eMl2187fwCl7dO9Vz5YNeuL7ivhO38q1OE2/3eH5YsWbeXExA6+9vAOfdVJxfD2/UCXkuQ/FX5QNEXfWZflC9u'
        b'L+QERLz/zaLvSpflXmN9fOiWk7/ZhiY/Y8b+9Dq4BIc04jJ4BBzVisw4jk4+RJizAByvUWsrJK7Wx+WJg1dIIWGrDPUFbtmhKUTc5Qq7OfBMTTwRIGbMJujhWkJ6HhzV'
        b'k7ntmEeEfl7gSDCDWWeaTzGYdaAPHmYEguuFXCwqA1fUMkEayKrARvJuITi/AEuT5mSpJVs0OASvLSGyMXswAE4TyaWaPA6B9Xqiyz3wIoMYtBluBS9iMRsZbnhSohOz'
        b'wb1Q/gCfaarAdniYMcUNgufhJSmRxqJYDjmeBvGoXLAe9DkagOfNl/yPOTUC9GOl2Wkn4vzYMyCz99qmUB7e/ZVyvyMNSvepGKJnzMauo3n/6s7VShsfuZvSJoCA+sxU'
        b'OmQM8zNGPUMwqI8bSTRi76tg3LslKW2CSLJMpUPWMD8LcUX9RXLBkQVKtwgM9MOUuapzldLGW26ltPEnidOVDjOH+TPVPk56s1FKIyblss5lXQkyVKoX4ylO6ZA8zE/+'
        b'1MmVJPldhbv5HXPpd1G6hf3rpB5eHZw/WAofd4vxNmZ538HBMA4UOHgXB0ocvPev7dq0DjEm2bYRAcFnWLCATp1S7BD00c/YjnIKTc8iDsdm/S5XY3ipOswLp86ZTP/P'
        b'QIlqNYA62jPYbyET6chKA0xUgpqgB6/DnPA0x6wnQP7856BEapgd0zK9M9xvwctgRPu5uGYD2pq5TKoZOeno6vXf4CQZlWnOeU+rz3xcHx3ijitTH83B67GO+m/6iFOG'
        b'ToVPq0spqst9LfTOvAPzmDo5MnXSO0n+l/Wp1dQHHR6fVh8R7pvvaU3f+OqOmaLJ+FHS/1UnGZVpDoZPq1nVxFFzwCJ/vTPk/4yCNOfMp9Wl9vG6oNHSnlD16uLHIhJH'
        b'RvaoNajLq2TrfR2DaxOLOuKH0EjPCJZHWEXsosGI+CLEngjNSswjTbUmsQb/Q5PYWj9WSwmqjHFSVRX2ktNQvVR/1NHsIP5y0hBrwUQwvy2qqkIHcXR8F6k5K+IGB7tX'
        b'CBTWShpbmhiWWySsbFxcIW4gDtuNETn5azHD/AOF/vrwZihOENRQoorGxkX405jdJ7wE81nsHl7Hr2oLihMWNS7GXBUjDcBuItTIYqKKxhbGqw8eo+oqTVswJ4Od0Vfj'
        b'JlWJa2oQV4HWAIafmVhJdX8QTz+o2bVqpxZVWnaoUtRAuKGnsaZhUXoMndC3sYl4IarXsXb6/cCwPY9NO6FvUoWkurKuoaWhVqrmU4mrC1IR3bhIpeLaBjI0waSNegWp'
        b'HUwJxfq1FiOWD7F3pBQNKxdGOj0qVsvR4ZLD/AKxvEVYVV3RjMtFKSoRMybGkUoNk0moQEzSS6ubSdtjYtGYpWNDWyKvmUxa4mppnHZMUdniZnUCph/IEy3H6lvUWF+P'
        b'udRGP6G//2LMtqPPL/P31/L7pEYTSmAe6YqYiZrbEBSSgdbXhqcVxeCfqZnQRimpsBoT7YnpMbEyqfXJN1iYq+WXCTk3ViysrmwWkh5kaKgoPyYqNEwty8KiKoZ6g5/8'
        b'mQmGzHGT5AqtjeLKai3BJFfXV9fW4HR+wvlh4QueVES4uptbqpnqiRtIRfAsSE3NzZ03D9cUe77CVW0SLVtM/GRVS/DiGyhcjPpFy33rfTB84gfV3YcxDyb2J34yUTbC'
        b'UFeIhrLIZ5mjQjKqNKZ9nAcVHxG64PHZs6h6mUbSo0dm6Cmi0AapmPloYw0pVVS1EI0MaQ9OQJx9idrwb2ZuMzKgCYmkRCglrqxrFtfiqkgr6+rhdbSy1PvF6fIECdG4'
        b'FDVXt6DJrk2AKEAsVDcBzbDFiCLTSoKKRc0V1VgQV6XOiYaD8ZtT37J4UXWdRP04YtJjUpqopaa9pbkarUzY+6FwdqNESj6qzhMZJ0xqqamrrmjBpIgSJLU0N+L1cZE6'
        b'wdQ4YWZDlbhVjAa/vh4lKFksFTW3SyfVXJ066klV+NcNin5SNrHeZxc//bMxT8r/9HbFkobrumZSz5CgmBlpLDGb9N3HRlK/ejUS9HVf3FZtmaKK9pZaP93w6ScXRnvp'
        b'BnDCi7BYL90wNYSIdEMyMVmUl677dclQp2q/r5cmRv+x9tOxExKj72oXLDW0AZox6l9kfUZ7MJqLmqnuW8SskdoFVoeUECdMQREhE0N7hm82ilY3oP/RsArxmhOz4PFs'
        b'4ROzhU/KFj4hG4FbYJaM2UnFQZmpQt+Somb0F68vU7XJtHAMTNK0EjKT8QOhLyJK9RCjbtU1o0WCtvxKtFqkqH8FCvX2urSSWULfOfBonQQRGfpWpO5TekgPuszax+qP'
        b'arJKF7VIpH4Ttr/f2j7J1qnbCbVbWNIEYe2T9wSCNREnzMN/hPPDQxf8drJwJlk4SabrDQ1IhXrLVMfxAVu/nwliBUqC/6AXC4x1sySjWiJpCEmXiFpQUB8cki5Gu5lu'
        b'VpDXurmA0+noH2fQTQD9nIjq0+rQpoLmso70SVloz6liitFUDu2a1dXNeOXFf9EGETVh/6lobIsT4qsktP7X4F0SPUBtCJ2QCENpMKlE9UIcmZCiUtyMCQaFE7YfBh8E'
        b'v2F+kIyBeF8PigiLikI9rfsGhuJAH8B/JoxAjQjVLh0Rrf5DAtaBegD/Ec6PCp08LdRTQn+ENDAhccJk9IvZOeeHR094ryUtkmTiZcCE9mrARdQpmf7QTU4MIYK2kOSk'
        b'PNQduhlSIa5EGTJTUFGIQv6FO0y1QD7NiEVxnrXiYkNpmF6q9miyaQk4p7WxhlvBC7TayNo9gORyS+RQhjk8CiMk/DVwqhpXYjP6t6McHNNZgPetlpD01FR7KrD8vgEl'
        b'LF+RykdfIZrhz5nD88QiPBceD6aCV5kyhvyXBPCy2h77FLilwdeAp8HJAlLYmNsK+udSxOSFiuarFtRQxNvbspngXABKm4W9amBVSXAyK9cN7GcwHSl4FmybRbVFGtWG'
        b'wi5ie/qMO4PdOJyw3OaDuQfrJMxdxJJkyZOgG1Eh5vB6cQYjw9QHb4Q7QI+p3yJ4hAjQxFtbP+RIDRHH+dPlPz1f8EYWTORPXxq+rOXdVcnzU5KWXg0tDLRdf9pW6iOs'
        b'sh0eWngLlI2vviGOOBVa88Xt0KbSh2+ufPOm6MeNp5um/dV47lrxsXljTUEZv5oW/v2PsaPi3j8Ouv2lIDQ+6L3OluOtXnWexh7RS+J4mxxs78Q72bK/2f16yi/VfQlD'
        b'AV/9+lObX4xL++nrh7Y82H58+KEtjN8tPvDze4EtbyXI961w/IS3/PhrNSWfLx85vPivL7yS+s9/HAMv3Pvys9wLvLo3xfti3zkAeStfvvhm+wvX5E6vnRj4RLFiz/T6'
        b'hj9GxMZc6/yoYeCoV8KS57ylz25v9V9e0LrvyOw7OX/KCxzt+kYOvefKjjxqe/eMq1dLaNUnL/kZEr3KdHg2ReswpauYsRDkw0PERLCKBY7C50J1RoLgXGolkVrbRYAb'
        b'AXBLfiY4yQHbwYsUr57lHmHLuO4+tqBW30KwHe7QoEJeh1cfBOMkV2eAK78pjI6AHWp5tAF4PgB0E1k43AMu8jA2pD4yZCuUa8Ahl/sxlwJDzqhmK6SYEIJ8cVK4Cyu3'
        b'drDBIB+ueYAnG2+eaXZOJrgJemmKNYv2nw9kfhb/S4dRFtQEc7+JxisqU63EUmPxl0WrkfNcKGHgiGuofAnGtXfsblbaeHzs6DPq49ttitHPPGWt/YGD7BH7SIV95JhP'
        b'wEDRoM1g1VDU2frbEbeTh6NmjkTlKqJyX61URs1SBhUN+xR3c7pn95hiB928nmmMw+7O1FFbF5mn0tabFO3fjV9j39+92gRfYmH0DKVD4jA/EbugeVYeO2w3tYM9amPX'
        b'XTXiEqxwCVbaBBN8yhHHAIVjgNI+cJCrtJ/6oYv/cECe0iV/WJA/zmLbho2Fxg55Doem3bZ5NzQNK28SayMbhSBonMe2CiLKjZ4KvqesiGh8Br3LD1Lwpw5ylPypPz8w'
        b'oJy87lM0KsUlQJ6idAkdFoT+Os5GD359YEgJ3NA7q6AxBx85W+kQOMwPxO+sgn4hQITQzC6VQ0FP11QX6i7HONWRfdfcMNWOfdeOi3+7GKdOZd/1NUwNZd8N5aLfjJjd'
        b'ghGz6wRVWN/3dxktTaKCCb6nJ5gwsdHIL8TCdnwziIG/Ch1pOgyL2sMwcGHY79EhxA4tn4xETvCBOWokcm4JVcLTAmT+z9HIJQ+pSd6BXB/b3byY3a2uECP5UMLQmk0z'
        b'1sVMURundDeCU9KWwqmhGKUiFA6hWU2vdIc9OgTNMHAGHm4oMUH9Noea8yw8xpifnIGysiImGw2v5QZS8EIk3MJcFk9BmxKLmju44BsnZXAmY34TDTrABmyMBDcmUGA/'
        b'VQ1OgxuMBcpueA30YQsmZ3iBAnupStgPL5GSDs5W3w+nX/ONFFYxRkUrayyZe3Pvi+2zgx0YM5WSevVleiun5fUYGyZlk9SMubVOj138YmQCk/KvM9VX2ek+/N6lnkxK'
        b'y1D1Ha/3jujaojgm5eln1A9bv6/vWJXBPLyQpLmyDsn+oKmdQWlIAmeWFhUUFFAUnVqHoXieK2lh+rcHysHpiNBQjO4Dj2bBI/hyux9sJNkWW08tKuCDbgrbyL+I3khA'
        b'N8mWBPqkGrsnDrUadDB2T7vnkGw+sAteiAiFHfM0hk+ZVuQUkQo7gCxgCvZL5ka5gZtorPAIRqAPbvCcHYEoIpwKXwUOtuBpIo2x9wvARkzYgKkomkH66W3JnmCrBK75'
        b'U+BilaSFsdvvLS4qELKx4betL3iRB/rhfg3SzjUM6azDaIaXYom1km0tY0qEO/lvy4yYC3rv9PybSUKmP3MT1bf2rSKfmzOrGGKpAJuBvKgAng7C+rRwHSWCZzgMWlOt'
        b'WsEhuCRVYW9BMXgzHfCIoKgAbSkUFbcSHF5igihoExhgKPUwPAXXSM0iUGexwAke3ETBG4HPip/9Zg2HuA50TJ7zQnF8Iwi1TIg3+usPdWt+8D/qt/Ca8Opg8cKRc4M/'
        b'D8Z5hP1pTvO3qkcfSK0d/R1TU92/WrL0kz8tX/3zrXFjo0A30Qe7qV+tDwXN/+qvlgl/azfsGD/luu7LgH2vlUn+cYhdn7ym2OSZbfVJ79ztepZz7IqXcP/HhznjJ//Z'
        b'/dOI7weX/rzleMo3lR1uX68/kFLWPp99PeK7r3Ze3069YfBaQlfxpSTTPXs3rjty9fOx/XWxF5edXN/wQbtVXOjUrr64tWc6PjLpNFt3PbPzq59Tv1S9/dq7kYGnPPat'
        b'SrKzib1km91v3HzS+EM7sGnmz2d3W7aXH3lp9M7oH1aVrfz86J+3jL7xa/03gwsPfXc+5a21j2zkV12Xj74Sf9Xg+L67rmOmvPyir1Ossp0qDGa+0fn1xpmbVlee+sNf'
        b'N0e9vDG8eM5Y79CLc8IX94aKo177/k/vXei6LJ3/zbdvLbeBxT96v326++2TFfnmb/y5/iV3qHzl04CPZrXP/wyek8yLqr6aJE55+euG9bHFtx5Rcx8W3m2z8OM/CMFD'
        b'vA/uecJVeYDdpMtydDgBu8FOYukxjwYbAsiZB71Dq8kRQ3iNBTpXw27G4+5lVM4udAjOoSmOWyJcQ4Pns4uJ7VLDXLhZC09dCIcMMT416IK3GBORg+AUOKhv+AT2l2EP'
        b'sWsNHmBEF2OwKz47B1wtf9wiSZjGNQLnYCdjdrQnFF7Q2SQtA300kFmAa+QwB+Wr3AnYPrFHCo1jsPYNGZOkM7TbJIsktNyewyoW2Pc6mW6bXMTYcEpjNZUKbq1iucMN'
        b'YC9jcHQD3iBQDzpFHLAF7NXoT4hDGcdL8oz52nMmfCEdHTXhwXlEhyPOCWxLeiZ7gqcjc7COnbwQXmfquD4W7EFz7NAEXAdsrQS7YRepYzLYJMz1z9b3hGS+kp1aBW6R'
        b'T/AE8KpWfyLEBl7T6k8smspYmO3lYiwQrflRBDiI9TQ628lbXyCfpoMRxxsWNj8CvWpTqRtwDTyhr8axAx6Cg1o1jpNJZChhvxMH9dIKuEGnjaKniwKeg4f+Az/0ulMH'
        b'vgBU+6AnZ089H/QnWGrECVfigx57QzIZFXqOCEMVwlDGxH1EGNuRgSHH2zAiOQYydxbKbHufkbv1lHakfxoSjbHMT6zuSOv2lc1WOAQo+IGf8l0ZyxWZ5NjS/qWjAsdR'
        b'gYvMrsdiVCAcEQShM+AgOghGjgimD/FHBGm3+RjKt/jYvP55g7RSED4iiFEIYoaslMSKvs8Cm5LgTHKRUhA6aD1oMyyYil+YYwf1BN+8UCkIGWQNsocFkVh7O2PEKUzh'
        b'FDaxqKHkoZRhQSJ535fbk6sU+I8IQhUCbIckYOyQBDGTK5g4ZD8iyLqd/sTndbczRlJLFKklI6mlitTS4bJaZWrd70npzLS7tL90ELUgGvWHAnUJamUi6q9+G9ncI84K'
        b'DOXuTHpQ/R9uQCrRVjGXSeT0sMD/tx6iQkYFrqhC41MdQ+3uU46+9g+jKIFLZ2t3ndLe52G0o63fPQvKLW48naZc3fvqeupky5UuER0mH9sIPvX0Pjazf+Zv9jMp+TcG'
        b'hzRrxCtK4YWtoARxqBcUAmwFhTEvdLSgIYlxK6MgVD0jL/uH1rrqyQPu2Rh5RSG68u7MHedTAucO08dBw5+u9EJAwydPBYkDIvov2Xr2O2muNG09/nvtd2pwWSx6krcX'
        b'rTdAglPPVWPDctRq5NjrC0+LC8v7H+LC1qBjOJeedAx/HNDZIK+FOFLYnguvEE/wBRlo70LbExgozmCcmcPrBn48KgNuNGgCe1OZA+Rx2GsNu8AJ7JiVYteDAytosBZ2'
        b'R5MzHN/FPAB9qa1qCtVWB7cSm/WFsH+BF+gOyGdR9CwKHoDdi8RrCkw40gfo5ezcbxlvf1bYz1B32EvJMblT3ALN5Blbp7CD/3Hy7p/zizl/qfXJCsKe/XxyErqtvPte'
        b'FwDbuzvEa/32vM0+YHt32/yEza5Fwd1GsHWOrHd0z5oabsSmwQPJKT67wva4ZVheHgOmLhWmpi/kmJpyX+9nj21PAt3+Hntye4SBXF6ZEY/XIDQr9tv6QQ53Y/OzouCd'
        b'fhu93ubcEQVvyQ8aNlv/96849+cYXrMOfphRed5jj9Efvyi3E2zb4rbLa49Xhl3RSt8IkHunfDO/NLhjPKu2oGo46WcLecKOzOeSXHzZxTYv3y5/I/Cdjpdf7eFRkVHe'
        b'UfUn/CzIjmsvyiHdjji1aHQifI5GR4bzYCuz1eyG6xLwBgC3pTYSwxFDuI21MjeNbORWInSWwC+fQycK4lA+j+XkirZafFpYNWMuBjsFJ9Gb4Ezy2gQOsuD1ciEjmTm4'
        b'DG5A+Trs4YWlam1II3CMBY6A/eAM4/bjDA8cw77uuwOxXeuWHHQkMElkwW5wDJ5m3OQOgaPoXI7OCyHwLOzLD2JhQ2n/jHnk7QynefpOQzCY3doV7FpzB9JuRwyXgKqf'
        b'6doId6CTEq+U5dEGd5PKo70Y3gogVrdBwX4stIH3TQF9bLDBxo1BpeoB28FpXLUt8Iw4JI9L8aax7GtcyGd54FBpNiFcKIMdwYhyjfgs0O8ZytjhHof7IQbg2pGXZ8z0'
        b'WjJLgDiRXlJyZCgc1D9ihWPkp7OJ9szRbU1gLK5VANwXSABp5axAL9Z/DQWlEQrovL+rzLR7s1TUyrgQYakFQ1luFN9uf3Rn9P6EzgSZ54iNj8LGR558ZubAzDO5A7lD'
        b'niOBMxSBM24nv5J1J+vV5pHUYkVq8YcObsPu0UqHGGxZixZp0x7TXnO0u9vYMz6JR2x8FTa+crsRm1CFTeiYg5vMU86WP6t0iOtIGfUOOLaof9GLi3uMuzlotcaZZcXv'
        b'C0LvsSmfyE/59vszOzP3Zn/q6NwX3RPdl9CTIPcccQxROIaMChz6DHsMZfyD5hMKGXN2k7kf8+n3ORbYHyhvHixWuscNpb7nnHR71qiTS19GT4as+GDeQzblkkwrnJN+'
        b'wN/5xDnpfeekX6RYL+glrnWaJ/clT+O0CCN9z4wS9r/UemQ6nvHDOMGOkziSx9aDrhw9LJnlQpoWYD+Mv8dnCXEe4WeoMinD9poirB0jlXyBy/8TDr7BwXc4uIeDBzh4'
        b'iHNwiHCDgTgnsOeG2r2NRX7n+fGfaNLpRFP6dp3/hmboqzRxW9VcvVjKiKDINmintc60+h+KQPX6Hff0msn/MP3/Fq0OsK2TtJ4mFpz3OBwzyx9Msfd4dn9K97KzlXeK'
        b'XrO5nTk2xUkWcMXmStGQ0Wsp2Hd8IbYcTkikH7J9zLzvUSjAjuPRUw6Oz6I1pp1R2LQzhph2qj3dY/NPx6jN2TrTzqnYtDOamHbaOI5Zeo/yw9ATm4jNKbonCfhJIk0e'
        b'qbOF4mzh+jaimic/GKIGjFMs81y6R3rW5h75pbJ3PJDaP2XELVrhFj1kpHBLHnHLULhlKN2ylE7ZKhf3/tgRj1iFR+yQt8IjacRjpsJjptIjU+mShdrrnE3fp2hBDn2P'
        b'jct6yGuhzYJ+onB43wA/GSdPHjawY82cxykU/NBKo0r0eCjMXB6y+GYB4xQK7iPmyfU+juqsFeFZsLVeGgPPaTleLmXmwIJdHNDrR+eJDS6n0tJkNDyv/+xdXZjduDbR'
        b'8pCtXcGKbVtVhz/vcXwwfDQ35B9ceDAn48ADW5vrP+1/8Ki19apsy8HWPy7//ofrAwdfP9X8Vckq27+DN4Rzjz0Xntf/rb3xlyk//swe/6dx6y7ntz6wa+GsLI+8Iftz'
        b'qdR07dWe9X2U03emlw+VvuzxS0+sQY/1xhiH7+a/+swxRcXlwpXyoy3Hf33vBbfcuqyIA8q1+y4cdn5h2ebPHPKSnO92sCLc0yuMJTtWnn8lSfG3pfHrQn+6AvqFHmvB'
        b'i+83bNvB7X1WlNdj+E0Te387X/L63PbUS5k5jlePLFfNSrw2DQy0vXngS/DxtydD/Wf2vHLIYSTyywtXRIeKv8teW/OnN/5R8UzXO6vcgu82jv38h0OLq662Xcqtmhow'
        b'uyfq5NGUhDtzL5zoDX4+ZBSav55iPPOjmyvPLPv1jRltkkvjA1c/Wf3tL1n37Df4sZld5TpcOxVuQzwgHUMJ0e6ENlywgdxglIIXQa/m/gRtS5f0rBbgkcoHeNFDZ4b+'
        b'ZSZ4z5p0IaK5DQE9sX6ek6ej4VOD/4vJ/x8sF57M/phI/nls3Zi0gmCz+fpGUVVZmSQcLeNkz8R0+k+0Z0ZSZrbjHAMj+zEL647wbUu73bat6JHKwmWi/qm97fLC3tVn'
        b'PQclQ25nW4YKz7adD76T+qo1zFCG53wocOgO7xb1TO01kmUhzmvQHjGPw9PyFPZ5w7OKh0tmK2bNUdrP+dBOKLPuahi29MROjebS48aUNb8jqdN2c/LDSCsjz4cUDnx9'
        b'jIIeUigYx8HDYnqakUPH7AcU+vNwFe1p5NBt94BCf8bzaMrY8iFLwjEKeEjpwp9IiCatseU4eTnebEQJvOUmCvuIzaYPeYZGgod2EraRE0qOwp9IOL7QgBQ2ixSjC+8z'
        b'IS7sHnn583iSgDbKpMesXY+aDgelK4UzldYZw6YZzJ67Nckp1Za6a2uT6qu+IHFWsVBf/2cXIv839IIPreUT79qetNVg8iCBA6ERimH5wmjaEl+56AW/x8wBHylO8OKp'
        b'ayZJPLb41z86sKSn0KO73ydWb89s7DEGifzU1e3fexq7x3B8nBpk8y2Gb0S8n/XzIqubl+/dzFornNs7J822pfRcxVsbg+J/coqR/O3wpTo/ZVeife7qqz1n4m2n93G3'
        b'bntUdumb2hPtDb8s9Th7ZO8PKc8v+OHw1be/7Dj8M9+zeeyP4SUVs4KuvhFs8W7BhxtlMlF54Z3+ly1daI/tYXf4EW8qyp/bbPu+79mXzJc77cz9i2M75+yca8faVrOH'
        b'vnTPZ99CHAm5Nx2ABzFnAbfk42v67dkGVCKQm4BzLCgH6xeq71bBDt/s/CDsKzw/Hx/8reB1Nlq8LoP+UrCR2CKBXQbLwTawC+7CwiuwAx6Ha9Ezytya7QKOgt3M6re+'
        b'3jQ7M9c/1wCdpzeJOSxD0AmHyKtqcAZ7/gzhwXMJFF1EwSPwKLjK5LqEqnIxIIvrCI9RdDaFVszL4BLjxdwBrMcA5jvRNzFOP+gEu0z8WLBjbiFhD/Lh9hyp3vs58caZ'
        b'LDA424XBfjoIz8Cd2WTzQ0spOE5jXxFwKzsvKJQA7E4xhGe1yhOJcBD0RYaoUaOaZhN2OENt4y8Al0xtWPBCLrjBcFwb4S14DKCFOrBJnWTOCmNwngUugEvZjNzv2lKw'
        b'C6U4Zwo2L4UHape0wPNLTJe00JQ93MUG2yvRvkD0L3bC5yOzCUYWbglFlXmYgAMseDgWdJJNIR5u4uGuD8lGW8FOfPGNYwaUoycHMUDdYB04kuXn+2/vB/+/3B70Jr4v'
        b'2SgSNf88ZauYYOSEA7JP4CP3I7QI3HeguDajZvwRMxd0UDrYpjTzXZM+yjHelPNczrCV29GY9ziBH3DM0H8fcVw/4fh8wgn6iOPxkPeMJRctq7rwJxKOtwkpU/6afD0Z'
        b'lauKXV/doOJgZX0Vt7mlqb5axakXS5tVHCyBVXEam9BrtrRZouJWLGuulqo4FY2N9Sq2uKFZxa1B+xv6I8G6dNjpbFNLs4pdWSdRsRslVSoeYjSaq1FksahJxW4XN6m4'
        b'ImmlWKxi11W3oSSoeGOxVGParuI1tVTUiytVBgwIgFRlIq0T1zSXVUskjRKVWZNIIq0uE0sbsfq1yqylobJOJG6oriqrbqtUGZWVSatR7cvKVDxGvVm3D0jx8lD+tH+E'
        b'wkljgD2sSTFP8+jRI3z9bUXTVWy8Ak8M75Hw9yzKeOO6Y8hLElB3BCZJHuxfDGuwRn9lXbDKsqxM/Vt9avjFQR0XNokqF4lqq9VACaKq6qo8P0PCZKkMyspE9fVo2yN1'
        b'x7yYyhj1p6RZulTcXKfi1TdWiuqlKtNZWLl6cXUa7kuJiKUefoYQmMPKtMWNVS311QmSWhZjjyPNQcE4m6bpe6hpnHFzysRsjcEPnHpLmj9e6kYZWY0YOioMHbuzRgx9'
        b'FIY+w4EJd7yhrzIwa9TQcszYbtg+QmkcOcyJHKMsOwR/oBzI1/4/hz2IAQ=='
    ))))
