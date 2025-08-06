
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
        b'eJzsvQdYW9fZOH7v1UDsYTzwlDcCJPYy3hMQ04AHHiDQFcgICWt4YJvYxjbbeOCF99577+SctE3ypUnbtGlDkzZtkyZO/CVtmrZpvi/J7z3nSkIygjh9+vyf3/95fpa5'
        b'0tnjfc+7znvO/RPj8o+Dv6nwZ5kIDy1TzFQwxayW1XKbmGKOFy0Ta0X1rGmUVsxL6pkqqUW1iOOlWkk9u5HlvXiunmUZrbSA8dYpvL5e5zNzWuGsefJqk9Zm4OUmndxa'
        b'ycvzVlsrTUb5bL3RypdXyms05VWaCl7l41NYqbc48mp5nd7IW+Q6m7HcqjcZLXKNUSsvN2gsFt7iYzXJy828xsrLhQa0GqtGzq8qr9QYK3i5Tm/gLSqf8qH2IY2Av2Hw'
        b'50uGpYVHA9PANnANogZxg6RB2uDVIGvwbvBp8G3wa/BvCGgIbAhqCG4IaejXENrQv2FAw8CGQQ1hDYMbhjQM1Q2jUyFbN6yRqWfWDa+Vrh1WzxQwa4fXMyxTN6xu+AKY'
        b'NBh+pUKUU+46p4Phrx/pgJjOawGj8M0xyOB3XZmIeX0Q+VXql6sfztjGwE9pOmrGLbgpNysfN1rwbtyWq8BtGUV5SikzfpYYPy5EjxWsjVSqMKOHloxsdCoab8Wt2biV'
        b'ZXwyOHRldImCsw2ADMvnR6kzojIkDN6Ij4rFLDqML+GNtiGQhPaj9eg6SVXiJigsYQJwc9hgUU7UQihM5q8YX0PXUAtujlo5pgZ61Ar1+KDrHLohKrSNhgz4Mj6ONkKO'
        b'a36oEd9YunK5DV9f7rfcxjIDcbsItUaWQUfHkpy78OlpqAW1R6vxVbRFGUH6i9tJjBczZIwY1a9EF8pZ+5yJ4G+IY85KCdAEkDE/DGi6IXaAsY2Ar+s4ABhLAcZRgLF1'
        b'nB1gm1wBRhof2gNgwwWAJRdIl0YxgxhGXup3k49maGTRGm7pyyIKxawvw6YJkf+7xtunnJNDXKnfXi5OiJw1QWJYzgTBKis17AiWMQYfiHxYHiYeqnsC0/SH8V9wt2J/'
        b'E/81a/AmaLN436wfMaWBkDvu3biN48MYGn1ryd9GzxwWPoLLe5/9dsE40xSmi7FFk0m+iA7hkwColuj88HDcHJ2uxM3obGF4ZjZuj1JlKDOzWcYY6I0eo72TqoLdptvX'
        b'MeKpwnS7rw+GTLbO1zmd3PNPJ8F/SY/p9MsxkwTbIIKI99FlXF+AjqLTc5XzOIYTMfgg7phuC4ZEMdqL2gsg76yy0cxoNXpsC4HYHHRvcgE+Gj4XEiqZWQzabAsk0TOl'
        b'eCeMZtmMaCY6MIpWkI7vifBOGKpVrGSUa/F6G+lJ2RD0uGDkgux83CZhuDXs0KDptnEkfraIIHqkGrCzKSs/HJ2NQufxyXS6+FT4rARtjEFHaMWWqbgBXZcyTP/UiczE'
        b'ceiEPmP4YbHlMCTNXv+rJW+ODEExQZv/8F5217hXmg9tHC3fniKWvhtw7MyKiKCzIxt/MilFVv/nvDHyve+v+PNvX1gxwH/xB/vTHo977a3OgPaHrydYSk/uHLLntZoN'
        b'8xJunBHhOWHJERvWzDuelDln8/xX+0+uiUrznZAZt1b5q11v5zcPy6lrmLMr+dvaDf/6pc+Xb1oX3vjXE+0vNdtbto4qWVW58sSj2//ar/zXp0NCbKnmgXUKiXU4mffj'
        b'MJ1q3BaJ27KVmYRIoA50OATfEeGGuf2tZAGuxvdwQ2SmEjdmFKNDWTkSxhdd5fBBdFFkJWsEXY1dHKlSZEbaKUggvopv4vUikw0fshKyi3eg6/iEL0xjug0WfXM0x6zU'
        b'BQNI0EXvqdYwyKFCdxNhyk8uxs24HbeKGHEqi64ux0cUXBcXrjAT5FT40q8f/jjLfD1gos5squWNwBkoz1EBv+BXTO7yN/NGLW8uMfPlJrOWIKNFTvB1sowNYWWsD3wG'
        b'wF8AfMh3CHwHcaGsWUrqJnisEHVJhcJdXiUlZpuxpKTLt6Sk3MBrjLaakpJ/u9MK1uxFfpNVQ5ubQjoXQDqH5ZyU5VgpfdpGQswyfE0emYnb1Bl4+yQlao6Gtb41OpNl'
        b'xqKrkhJ/dM65EMk/sf3bUgkPnjB3YOxatlgEf2I9UyyBb6mOKfbS+jcwOlYr0oo3eRfL6G+JVrpJVuxNf3tpZfDbR+ClOpHWW+sDYV8IA92AsK/WD8J+WhaoQYUioEs6'
        b'l05UzpNvYSGWi+y9IAP0cZCGGMbBm6G8QGdEjSKgM2KgMyJKZ8SUzojqxL3xWVEPOiMWyHblEjED3/IjuS9EjTAXM/pfd4VJLDmQkrDb59PS18s+Lt2hbdR8UtpaUZpy'
        b'gf8YYl4ru6Sp1GVpQivO8OK/FgxaNmjRhmXrI/bGTRuj9pqx3Tdvy03Rma3bR24euXdD/DBmUWXg280HFFKK9QND0J5I/HCB2sHnIqVMIDolqgUufN9KGPd4dAZtjnSm'
        b'i/ppGb8okVcGumMdCMmGKrEat2QB11dI10xjZKiZW4U3LaJF0U50BuoBKqXOQBdBXMCPjSlcGGqOpcm1aBt+jFpyga+LGYkRlt8BFt9DZ9EWuqLRtmJ0IFKZToQCfADX'
        b'MzJ8g0ObgBXvV3AuOCh6FjPFDpTskpWU6I16a0kJXTR+ZPKLg1jykbJitjZQgLXKkUtYLJIusYU36LrERFzr8lrBmy0g2ZkJcMzeAtLb2yWIbvYnj0DnKiCNLHKugtNB'
        b'LqugR3vlnAuyO9FLZUcvHWdHLo4yMREgF0eRS0SRi6sT2ZFL54pcTC/IZVPA72q800eBrvniNgDKVmC+uL0gXYBefh7laFPwUWlwXpg+JXwUR3ui/QI3Lfm0lODZK7ro'
        b'kEhNluZpaVB5pc5QJm6O5WNXMu+85HdAyRz0l81450cKMQXdPHR6MLqNLzkxw44Xp/EB6yjSD3SgFl8HStyO21XKGju5xafQ3cF1YrQZn+BpNRBxq8KJIPgWOipgyF10'
        b'yEpERnwDH8Kb1LlKluHwbXx3BTutFp0ToMh5RAigehW8VW/lq+04QYgWU+bD+rG1IU7oOLMIVYkpjLvERk013xMNOHOwEw0oBoDMxJQ7MeBwgCsGeGjjP0ZjNj03GvgP'
        b'GubrI/0eJMAt6LY+/2c+nCUOiiyZE+4ZCZ6Wcs1xtpjfxJyIyZgnjq+5xTAXG2Rrr32kENFFvhAdwSfV3gHPYEInekwxAe8BpNjRAxfihjEUE9JQG60Fkh+g44AKMnTK'
        b'jg0EE7zxBjuD650GAMgtPUFe8QzILe4glwjwJJDtkqzQGGweAC9yAXw/J/SJzFfphH5nkGfoO5vzTALiBOgTyZbViZ+TDLjxGNZepTv8JTmC9L1rkIloU4W4UalU5adn'
        b'FuHG3ILwwegwkX6K0kGeVLGMFT/0lqLtuInijPfi/m5kA7VN8YA0aLdNf2Xi2xJLLhQ59O3fPi39BLDGoIsYEKFJ1xgAXy7kfVJao2ncdY4/o/m49I2y13XRO8I1mZpz'
        b'mqBy5tWBmZvqX953fcFP8YT1a2dvCd1SKn0jgVk9OWhi/A2QBYkgNwofWSlIaYHT7YRDkNJwZx7FlagpuLOb8IDke4WinBWdshIV2z9G3pP0DDEIhOewL5X08CHzFCfd'
        b'QVfxQ4pteNcSK9EC/IPRXTtfYtBJvFHgS0k1DsQQe5SXujFSaqshkl03TzL42MW4ILbW344jQh5XAiSwm240fBbngRJ1MySKi6GE1DpxcVeIKy66t+OmYLkTIarNOokQ'
        b'28j2qVC58SKxRyQU5ehHGLdzVKY5+6enak16xVNAktfKKnWhmjP8mZ9x18Ku7+0MWzyojC/buyysat/UawtfT2z9aevN1xOzEv0SX0/y2xz3B79hl9NbE6cuAe4TxiQO'
        b'DHx56Bw798F38BEpwYB8tNeF5qD9eL0A3YN1qJOCFzfi7U5iUmC19ofU8GU63BKVAbj+IBs0KelSbnTUdCrq4H15CwVhprqKijNEluko8gzvvkgSCOEWq9lOjshsM9Yg'
        b'NhQIEpCkgG4aQbI4yJv/98CedQE7GYXNCfY2NxL0TPUKLsdM9GmFP5GVCIMD1cCnpEQwb8Fvv5KS5TaNQUgR6KGsHBCmwmRe3SWzy0YWKv90SXV63qC1UBGIckFKDCkW'
        b'0j45SGuvKoVzhsxkUgrIEEhhGSdm7R8uQOYn8ZMEyag6XhePd/g6tAiZH4f3zy4FLrGlBxck/6g046ZIcMViIv5rvQ5wxZIORitbJtV617P1LCgVPpSh+ndJZxmBUq/+'
        b'OnQmX6a3mkATi1abea3w8wkZ5BPS669D5vHmWluFpUZjs5RXagy8PP4JGcnXflm8tdbKy2eb9RargqNqxZMfA+T/vg9mR20yWk1pOTC78vBpWjNvscDcGq2ra+RFoAKa'
        b'jXxlNW9UpLkELBV8BTytGqPWYzmjxoofmA0qeR7AxgRl55nMxufJ56myKl5v5OXTjBWaMl6R5paWpraZa8v4Wl5fXmm0GSvSZhUps0in4LuowKrM0OaYVWnTjDBZfFoh'
        b'MDtD9LQqjVYln2PWaKEq3mAhLNBA2zVaVpjMUHOtow2zNa3Aatbgw3xansli1WnKK+kPA6+31moqDWm5kIM2B/Nuge9am0txR6BsJekdUZ7l9o5AlEpebLNAwwaXzstj'
        b'e02JS1PzRmOtSq42maHuGhPUZqzV0HZ4e3u8fA5+YLDqK+QrTMYecWV6S1ohb+B1kDadBxGyitQbbo9SONLkc3jAHHxCZ7WQUZIp7ZlbPidLkTZLma3RG1xThRhFWoaA'
        b'J1bXNEecIm22ZpVrAgQVaQWweqGTvGuCI06RNl1jrHJMOcwRCbrPGompIjiszLFVQwUQlYVPEGtFFZk1YfohMmP6tBySxvNmHdAI+FkwP2N2oXKGCWBjn3y6FvTGSsA1'
        b'Uo992tM1thqrkrQDxKZMZW/T/ttt3j3Fk7l3G0Rcj0HE9RxEnKdBxAmDiOseRJzrIOI8DCKut0HEuXQ2rpdBxPU+iPgeg4jvOYh4T4OIFwYR3z2IeNdBxHsYRHxvg4h3'
        b'6Wx8L4OI730QCT0GkdBzEAmeBpEgDCKhexAJroNI8DCIhN4GkeDS2YReBpHQ+yASewwisecgEj0NIlEYRGL3IBJdB5HoYRCJvQ0i0aWzib0MItFtEN0LEdaTWc/rNAJ9'
        b'nGO24cM6k7kaCLPaRkidkY4BqDEPOpAjUGMGggzUz2ipMfPllTVAr40QD7TYauatJAekl/EacxlMFARn6omkwCsFdjfNZiEMpRakhbT5+ESlGebNYqENEKon8FeDvlpv'
        b'lYfb2a4irRimm+Qrg0RjBck3G58wGPQVwKOscr1RXqgBvuhSoIDCgKTkUauqa2XdLFxZDL0AghFOirsl2MtD0tieBeJ6LxDnsUC8fLrZZoXknuVoekLvFSZ4rDCx9wKJ'
        b'tEC2RuDLdM5BKgHphMZZ+VVW5w+gRM6f8a5ZLc5sAiCm88COK1wixqYV640ADQJ/2g5JqoUownqBSrsF49yDQH40FitwO7NeZyVYo9NUQv8hk1Grgc4YywBtnRC3mvGJ'
        b'CkCiDKNWv0Ilny3wD9dQnFso3i2U4BZKdAsluYWS3UIpbqFU99Zj3IPuvYl1706se39i3TsUm+hBTJGHz7XPqsUuaCi6BSNPiXZZyVOSQ3zqLc1Jyjyk53pujchdnuLd'
        b'RLHex9BHem/S2Q/JHNd7y25y2vNkA1LpKZsbC0jqwQKSerKAJE8sIElgAUnd1DjJlQUkeWABSb2xgCQXUp/UCwtI6p2PJfcYRHLPQSR7GkSyMIjk7kEkuw4i2cMgknsb'
        b'RLJLZ5N7GURy74NI6TGIlJ6DSPE0iBRhECndg0hxHUSKh0Gk9DaIFJfOpvQyiJTeB5HaYxCpPQeR6mkQqcIgUrsHkeo6iFQPg0jtbRCpLp1N7WUQqb0PAghkD10hxoOy'
        b'EONRW4ixqwsxLmJKjJvCEONJY4jpVWWIcdUNYnpTGmLcxmPv4mwzX621rAYqUw1022IyrABJIq1gVt40JeVWVouZ1wETNBKe5zE6znN0vOfoBM/RiZ6jkzxHJ3uOTvEc'
        b'ndrLcGIIQa8y4gc1Oitvkefm5RbYBTjCzC01POjDgjDZzcxdYh3s2yVqDl+GHxBO/4zYUCHE26UGRyjOLRSflmc3rbgU7mF0ie0ZFdczCtQcA1GKNVYil8oLbFCdppoH'
        b'Nqqx2ixErBVGI6/WGG3AXuQVvICmwA49mQEULkX0hLnrtbTY92b2UL8HpuS57p4ZqYmpe3bkIHzL7SIvnUodSbdPsvA7zuU30Qm7LVVfs2k5Cs5MDOZmuWBcJnv4ZrJn'
        b'o5CZye6bmdhEzcQOJ2yEENOqmRjguySWGoPeah7itPmxz9r3iCF/ncNESe17Io6VcRwnjrWRevLRbrzDQhw+mqLQWTEjS+LWFdWh0zX/IdNepcK/y2daebnJZrSCOtEV'
        b'MB1wQFBDNDW84QkxVz4hrg1fD54JOFENggaxmsoFNQgwWg906AkxxXaJiTjkZth7APFF1YKQY6o08vICk8EQnQ5UyqhU1xKbS3ewm+6lzVcXy4VixLZGKKpFb7EJESTN'
        b'NSyswznEFCjI/EJD04uUBeWVBvwA8MEAcoprMG06b+ArtGQ0wk+7Iab7d5xdZ0pzTAbVAYiQyNuXu0ORkwuCkl0d7DZc2RVBKr4TFRAyw4KzUlXBXgNtzqCHDPSX3qgz'
        b'yZXyaWaroyv2mAwjKflMJMkW5ylbXI9s8Z6yxffIluApW0KPbImesiX2yJbkKVtSj2zJnrIl98iW4ikbyB25BYWxEKEWAEPkX55GxvWIhIA8mwca6rDOym0qebd1FiIF'
        b'hHaYS1VyIsM7NHHBDNsNRnlWZFbabJuxinq68uYKIFq1hNCQ+OlF8oRUgfXqHFmImdhTvB1vhCQPFaYVUxWBDNxcrSGJThTxlOJEld6KxfVVzHOigEJ9FPOcKKBUH8U8'
        b'Jwoo1kcxz4kCyvVRzHOigIJ9FPOcKKBkH8U8J5JiqX0V85xIwR3TJ7w9p9KCfSNK75gS2yeq9JJKC/aJLL2k0oJ9oksvqbRgnwjTSyot2CfK9JJKC/aJNL2k0oJ9ok0v'
        b'qbRgn4jTSypd8X1iDqQWWPGD8ipgXSuB+VqpsLqS11v4tNnA57upH5BDjdGgIfZGyzJNpRlqreAhh5EnglK3AdLOOQnBm2bTEVOZk8g5eCkkEcrbzZDl4dOMtYKQTPb4'
        b'gBhn663AGnktCCEa6zPJz9DhnoW7KfmzaWYDvmWxiwluKel0x0dnBanEqWpRTqKkQo9HvcA+Ujs3B9YPnIaI1ToqUFcTBm/l9TAtVqftOAOkX6tep6/SuFL/YqoaOm3K'
        b'rmKGoFC67C26ikmzeUHb4PVlJCkLoEY2yyyCZNO7tOZqL4Z+Q8sag626iq90GLcpEyRM0kzcq4n0G0lE1ShB+lWS36rnkH7N48mjD9k3HB4PPMq+YTbi7ByLdqZZsnLw'
        b'1mgq/+JWtRc+GMz0LxP7ocZ8NwG4n0MAXsa6C8Ad0g7fDl9tQke/jn7aRG2SNqjNS5vcIGnwb+inE2n7aUM3gThcLOYl2v7aAZsY7UDtoDauWArhMBoeTMNeEB5Cw0Np'
        b'WAbhYTQ8nIa9ITyChuU07APhkTQ8ioZ9ITyahsfQsB/pgY7TjtWO2yQr9qe97PfMx1s7vs1Hm9LA2Xsr1oZrFbS3AcKoOnw6WB0HOb3o01Eqos1bm0pd5iT0rEUQlPXS'
        b'RmqjaNlA7QRIkzTI6EmMEJqm1Ko2eRcHQWww9ClaGwN9CoY2+mlj2xzHCgIaAnUSbZw2fpMMagnRhlA34bQu2Uzimz2jYN7X0T5yl3+OaLlAdoSjQG45BJ2KKFNPqIM2'
        b'QbInxLOjW4N4QrxxnhDvkCcUdwjuPSEuEU+Ir8YT4l+h8Ory0WhXAMUyl+i1Xd7lQDeMVvIzQCOoNSUGEPyslV2ychssKWP56i4Z8TrVawx2dw1fnR5kvZJqWM6VXaJZ'
        b'RXNzymV2fPJhXLyAJjPPHEXybpA2+DR46XzsPkGyRlk9s867VrpWRn2CvKlPkKzOewGjFVGfIPHfyVkHt2kg/zKE/uhreQs9cuWcPD11cCjnVT2K9IiYADqHplrePRcT'
        b'7IetgK4Qs5D9NJd9UjRGa48ayL/w6UAOrA5ipFDJp5HyQDjK5dT7T26rkQP5TJZr9RV6q6Vnv+zdcILBcy+EZM89cG5+fE8fEr+vD+7wnyDPot+kC3Oisxyp9o5ZPPeF'
        b'MBtC5oFJqOSFlUD4AZ15ucVWZuC1FTCe56pF8CwRNFSoSa6BKiAs9F9uMAETMqvkGVZ5tQ30lDLeYy0a++DLeOtKnmz+ysO1vE5jM1gV9KxdSu+wsOP9BPkM+y95ObEe'
        b'hjv3HF2sjoreanGsmQkObLU4gUmO9pnM8nDBg6UKPzDXgtbdW0V2X6kJVMUi4ghUI+CInVSE8xUqeWJsTJQ8OTam12pcFu0E+WwSkNMAqU6nN8KqgT7KV/Ma6FiEkV9J'
        b'NkBXJKkSVLERip5T9T3+wn7CmYSrs4IYOcOkxCRJxTG2oYxtEkSixkFLcUs2upCHGzNwmzoaN+URN9L0LEVGKG6JylGiZtyelZ+OLqbnZGdnZLMM3o6O+JnQJtRAq/21'
        b'vx85nxYeM+6i8sbMF4RqV+E7UR6rteBGvBU3ZQFTRE3PVrxptR+DrnvRamfmeZNzazExs5evQXWlDD3VN2Am43paKl2ljCBHUdAlMZO0WIpOB1okaCc96EXryAv2YoDM'
        b'BsXoyjJ+tdibsREiaECXF3nqGnSsFQZM+taqmOfsFkSvZxl01+yLruFtqfq2U59LLKugHvG+28Ne/633+hi/zX84dfvGvS0772wUyX7hdTF6VE7ptLhbp4/WyNZO2RX1'
        b'YPDIqIyOMb/8i8/Bbw8NX2Q4vufl6QfPFdl+9vK3YZ8ULfn7T4/Iwu9IV6W89/Cl47V3/oESl+GumM5NUyYnLNxvzJiYNOKb4daflA3Y+c8R1RZFyON1Cj/hVMY1jS9q'
        b'ibaf6JDk43YREzhWpJOWWImlD11Cl6WoJTdLQYCIzo4T4Mgyg3G9uNZviHAg69YYvN4XJlOR7Tgs1R/fx49Qg1j2Qiz1s12Bz2ugGjeYscyA+fEjxb5ydJE68KNL/dG5'
        b'SGV4upJjpKiTw7esyrqF1IlTmVYApV3AVCsOQZdEuEWTQJ1w0S3GO1KlwM0gn0nRBS4LHY9HG9BOK+Gs6Eh5AGohh7SccJEyCehYyAoReogvo11WghOTFseTcdolLdJB'
        b'CtXV6DBuAvzBm6UqJlDwUr+lmEHG0hIVoSL5cBtujySZ5BZJQoI/umWlrsmpldUkF7VaQqtKKTNrfAjaI8KbF2lov1Zy6E53k7Pm2sU7ZjC6I0YtL6CDgsjo828cx+qW'
        b'L4l4QD1LyQld5gVmrZSVskGszP4kB8Vk9LCYjCMpUrY22MF4nSdTchwdoV6lBPnN5GiXeSp5TCOP6Yzj2MsMpm/XVJlQqruSac5StBIPB2iekO4T50pmPbNvuKv/as+u'
        b'Ol2XWfsf9Rsl/VnLLGOouMbmKNgu35JuGcHhLit2m7ku2USDprpMq5kcDPVYSJ0u7TnSvrZTbXttDg4fDtxAqzQZDasV0JhIayr/3o5tEjrmU+KUGjz3yzwHHqGOLn09'
        b'QmhfKOSh+edtN7DEXVLoo/GBzsYVfUoTP6gblUI3vEscjLqPDgx2diBsusbCO3n7vzNu7xIHT++jwWHOBkf3yvd/QNN2HJSV2KWAPlqWd7fcq6TwwwftV+IiOPTR+uhu'
        b'SH+PcOGhD26HB+gxNq6BcR5j+76jA89xfkmUo7/xdhFHj78e6+onnEgyLq3UPWV+3vrT1j/60cMAk4+Lf/vyRAVH2dCc+WXACfbjeje6LFBl1LmAkvcQ/xw7VUbn8eNu'
        b'tdtOl9HW6r7OlHmVkAXkerjoBfiMrw1yIVU0Qy++/Fwvbvzz4DGOgIN40QMhXM+863aWrEf9Cp8uL/uCFDz1pRarmeetXbIak8VKZN8ucbneurrLS8izuku6QkN1Rt9y'
        b'kMBN1YIuKbJqKrokJkB1c7mvHRSkVwEOcMwmkPV1qoT+zvP3AcJlB7oAO8R9G/0A4n4AcV8KcT8Kcd86PxfF8D2JB8VwmlZrAcmfiK9avowsNvhfbnd0k/PUJf85dEOq'
        b'uVC1QyOvtFXwLtoYzIhFD9qMXDizQBQrC29VyXMBoXvUQ1Z9NdlL0VfXmMxEiXQUK9cYQTMhRUGrMfPlVsNqedlqUqBHJZoVGr1BQ5qkgjxxk7SoyEj1xCoGy8pepV0Z'
        b'InX2qAOqtln0xgraI2c18ggKrIjnmJHZ9tFWEtNEz773yB9u1ZgroA2tgwCR8nJi57MQxcKy3EZmt8ysKa/irRbFhOfX1wU8nSCf5sZB5IvozuaS3oqRlifI6VGFRd97'
        b'YKHXWoRlMUFeQL/li+zuc73mdyyfCXJipQRQUT1ykav7XK9lyYIDDRSe8kW5Zmvv+YQlCVmFH7SNKHlGQa4yPjYpSb6IWCZ7LS2sY9AtpxUqM2bKF9m3+5ZELnI9jtF7'
        b'493Ln2jLQkBOKnJ1Au61OBAMmMxKWBqwXC3lZn2N1c62CJ6SY9R0bU0zWEyAv7zWo6IP6ERyEzZjoHfjUGCr5DMFbZ8u0VEFVk11NTmwZhzVq95PFwMgFnSgxr60tHp6'
        b'O48GpnWlHtgZvwogbl9wPesh/3JMVl5YJnTx89ZKkxYoSYUNVH3SF00VLEBYNDzMTjkvNwFf91iPMCSyaKgZwyIMU29x6ZJKPhuImoMgeazFddkRowegOrl7qNwAAxau'
        b'HbLwnkuW2m8eMpXTngsbIRMrrdYay4To6JUrVwqXTKi0fLTWaOBXmaqjBcEyWlNTE60H4K9SVVqrDaOjHVVEx8bExMfFxUbPjE2JiU1IiElIiU+IjUlMjk+dXFrSh4nB'
        b'87UHITk2wqbxYbx1hWUpbs1SZCpVOeT8XSQ6C7rdmAJJ5ehB9M6UxeNT4+ErlkG7fWKHa6mi/rpBUlsoXFOTNaOqH2NLJpXtmhelduh1+biRXBuSWYguKOeSo6pzw8np'
        b'z/mgnsMXMHm0A132xruWrqP3FOEGtOsFfB3UVqLheTGSGVPwPs6vBj20EVFhyUg1vq6il1i04RaoGKpG93Wgv45AJ8X43rBcG9Fx8G7UAMrnddCQs4vwtpqsATlu48rD'
        b'jTlQtlVdVAOP3KxMvEvM4Ga00RefSMcNtCfoBl6v9lUpMtEDdNiH8c7k0M6F+PAQVE8Pv5kn4Hv4egYUZxkRuosPoD0sWh88gnYTbcR3+/nixmgVboImo9DZTNyaORc3'
        b'sox8jkSMNqXa6InGW7gJncDXo9FJfC2CZbh0Ngk/SqczuzhJGnCMpfcHReUHzmaoX8443DDG4o934Zu0YXRLwsgWc3NEwg0f2UMLSaK/vwpvxzez8NVI/GAO3iFiBq4W'
        b'oQuD8QYK6oFoL97jq4IKYO4yyIyImP74rhjdQ+cD44r0Uwb+hrF0QkZVdLzyjUkBKMZPUpo2pbpr3JUN95YHjbv0Yv+okTd9mwe9tXn9BwUxy/OWjun4Q0XNzounJ0bq'
        b'L+PpvzIUpq8adzTxg517kw5mPNz6Wv9AxYA1J3714X/hxoLJeR+Ojxz9ZLv1Sv2wp38Qi27UrGe3Xvlm4ksdUzo3jXn003fvFfw2I/TrN9Ne/+u3u755+95//9Hn9zUf'
        b'/dG3NmzlUv2qb5jJb0S8Of1t++UZ+EgxvtJtSrEbUtDVNboMdNRK9nlQKzqO9jlxEZ1Fp5x2BmI/iIyX4Ha8dyU1H8xZg84/Y1NBDeIFk2Qs6qSmmUoNucIqFz0W95Rl'
        b'cQu+QA0nLD5hjsxRZmRkq6Nwm4JlBuAHYnygJm6hPzWc4Me+gFdR4enQB5aRofMc3hay2lTnJocG/JsXwvR+5tVHo9WWCJIbFZTHOQTldHLsVcYOoE/Xj5he1CFja/s5'
        b'Bd3uOuwGCn9BXp7POLbhFpDHQvIoJg9yE4d5MXksIY+l5FHiLn57Pr3rK9TZXckSZxMlzib8nS0udbZDRXcNleVdRfd3xrmK7p5GpPDu8tMSbz27aNTlLwi8jqBUU02/'
        b'ybUkfJe3fT+2nO/yJeIJCIXEW0vog3OY5T522kuMKkEO2ptJ5HcfNwk+AGT4QLsUH0SkeF2QXYb3oTK8L8jwPlSG96UyvE+dr12GrwAZvt2rbxle43S0kwvXED2HpDqL'
        b'nFkQcsuBXcI8gRAKIoDG9S49IiZEySvMJlsNpIJ0rOnJfkzVZXqjxiGQRICsEkE5qcBIiT7vdNIkHXSquT1qImrv/1M6/v+sdLgurwkEUEKM04r1PcqH23oUygtRjgo8'
        b'SmCLvsdLs9fmhPUutGNf4vY4QYg1moh1xkzFVKNn4XOliUiJ+mqNoRcxd1EffqqgPHj2VO21x4QyCf0tM5mqSH9JjEqebccuDQ3LTWXLAPCg0nve8DMSpSclKSbWbu4i'
        b'iAAaG6luUbcPa6+dcBLGCfIii01jMNCVAYizwqQvd67GRS4usH3qfXbC6g4Gel5ukaub7PdqZqT4M9qZmzPm/wXK1XR+JV9hd6X5fwrW/wUKVnxSTFxKSkx8fEJ8YnxS'
        b'UmKsRwWL/Otd6yLySM87WOTCxu6/6oTL5n62uNzvH9HJjI1cPDQ/Ch1SZ2Tj5qgMpw5lm+hJc3oBPfROQO3DqLoSiDYrqd7UkedQnYjiNBEftCVCcghuWahWZWaD2Oqs'
        b'NhhfzPeokbXgFm902muujewS4QeoHd+w4L1Fudm59iuISAPz8TYo0Y4bQYnyAa0DKoXw3YLF6ADqRMe9GXQe7/bNwRtRG/WrqkJteIclE7dlZOeqcdt4/DAjP0bMDJou'
        b'wq0TR9Isuumo2TLFFpGNt4YTEV2VgS6Gs8yICokEbxxKNSvcgW6hc774Nto6V4bblDmgW3Eggz9CHfEidFSGj9rCBQVs/QSYju4dZ9B00E0Q/q/MJRd0xqIWySq8eTHV'
        b'iNB9tAWdt3ctI0pBbvoMRdDD4yJ8v0hNQfWCgqNwDFpZYTiXOYahF3uijiSJby3aKmWYQqYQ3yqmUz1yTYEv2g9KGswTzOh2fDsdFMw2vBPfJEpnCzoPoSy8NZ1oXovD'
        b'ZHPwVnSJ3jWKb64VQaePo5sQyGAy0ONS2k5lDN4cj5v0VPuOjcGnbOReFvxIhbdArY9xE8jM0Uw0uldtIIcmXooRds//IrdFHXxBAGLnQHSNTEUbNa/fQ82gl6dHzQOI'
        b'tUVnFgECpOPWgnAFoEE64J5wRbAC3aKTJTX6L7FUUo11PDo5ogDvis8UQaevg7JzgcEX0qbayDXQc9CFFF87SOZ2I4coS+ZhJtAlvEPMoIYi74UYsMVG3Px8QvHNbu02'
        b'PxzvKsCXZ8pc1FnQZaf0lwagC7MEZDhQZrJkKnOzK1F9NEGYHLs+q8B7JeiGNzpI7y/GpzW5kcI9NQop44se43p0nIOJvraWXpM7e3kO97KUWXUlQ7nmZ4P2yaYJ/gZo'
        b'g8QXX6fGC3RJoZxL3SAINuGm6Nzs/HB7jfNcHSEOotN+MPR6fIdO1+IJuDlShS7iGxlRoN9LUTsXja6XUGCjzTOkanwljOqBnJlNCZ6qEAnX3D7KQlciVfl4V3cpvBnV'
        b'03uavdEh/FiNjkMrjoID0AZKArxDxroNcxluI6N8gO4bvvruu+9eypVQalPjW+d3qHARo/dfvVVsmQR6kvzPHy7ZNikHTw3aXLHiJysOjAj5dscg1P+MYm6N1+CAmFE7'
        b'lCO1c4/acFL9zOD8gjyLOOKNXc0f/ab/T994kHz4d29c2u5vWDzX6r9Q1089as4W/JrvuROPfjfBtvt1xReRi0LSv7k3+pspXww/sffzjMA4NnV6dn7DmbBP7hjGi6xn'
        b'm7KPnf+9Mrnpf8eNe7PklVe2+7/3kezjkZWnjzd/MmLYjNy3v0z52fFLov8etefYW6/4fxpVs+vtNf/F7Wl6Y9SnRRvGTPrxljUnDm+avHr/4E/P3p03a/bbYddOpV2a'
        b'n7R5QsOOuKqhb/yj4YvmmPveOaszatpX/K/1/N92e3/2UvLkVXk4QvL391a8NPCXsn8ELRmatGCety76t9sHfPNfM6N9JnxQZ/X5vHPE7y/fU3/FfXe74KDp2sgl676W'
        b'Ll2JO+99GfI4ZF/Gk61f/HTE7Ozlp9a8qPCn1oMsvHkCakGH0eNn7BE6SQh1d8DHcHOxYIoIRbdcPR6clohIg+DdcQG1oT3PmCJC0Xni3TFMTJ1IfLR4oxpdGO7ioBE4'
        b'T2QYh3bRq7KW4WOWSNSSGmH30PBeyKGTsiTBc6N9VmakKpVcvtUURbBrK6fE1/AhevsWuos68SG114CsCCnDLWGT8RZ0yEqoTXDyAnQ+KzuKQ1enM2I1i67VhtKB2/Am'
        b'fB64Qhus4zt2vwzpWm482ofarGMoLUbXslHLRNTq2YPDHzd60X3AddDYfheXkLIQt33AJfiR4F1yCe1G+yxk1SkJ5yITLUY3mGC8TYSu4CMrBTebY3gf7lBnoNuutpbV'
        b'c9CVPq7AUgT9hwwvnkwwAcTY0K2LUzNMocMM8wLD+dmNMN2mGHInnWCIoSGO+I0Mh9RQVkq9R4gnSQiEyaXDMi6A+pb4cCRcO9DNxNHdqt1w4ycYT8rIg8gqZnLhvZkn'
        b'Dx15VDgNKp5sNl7Pczexj1BnubPiMmdNFc52/D1YbwibK3az3pyJcLXe9Da0cold5iI80P2WckmDVwNDd0fZBh9qc/FtEDtvKZc0SuuZddJa6VoJtbFIqY1FUif1dKke'
        b'qXxED4EuQBDolttASvCTQHRplGxhJVMo+O9JgfCugiFNLfX7pXI+Q+k4PgkL5IAFtcmWV5eKGFEAmxKNm23Ee3057sB3ClBbIW4rys7HN/PwzSK0F53wT4qJYZhhA0Vo'
        b'AxCT0/TmfdsadKkAtxUmok14ZwxuTgCRSracxUfQiWTKTBJG45tQFz4ylFbHMpIIFnUmjBZ4UAPurKFXk+OL6O5EZmJIgRB/fyK+h4/jk/7LAU3HMYMCOMrPktDeSWrV'
        b'5AUxCXGJHCOtY9EhoBhHKZctwHdA3KI3gDuv/96PbuKDRWX6wbtvsRbiVTQ5fNWs3Ps5M2L9bv5p/7tzjipDpsuLyj6csXdB2N57Cy+Gjgk6OOipwm/4v1rrpk9Z39S0'
        b'/c2Xnjzsf818wLL2acqWMJ/wio4F5dv/KvXL/M17C/fk/zy28v0jX14LPdNcXjQ1Y+PNfYc0/5S/YvVvfvdOXPary1/Tv3Zx+z9XDPUdoB2Ev3l4+KXGnaUHb3vPz/uk'
        b'etyX95K/8J9grGr/W/3fav6YdOfT138VPe4npktbD4/+tvbD//3yxy8YjDff2Ti7abUxo3OC5GjcZ1+UdVlSz30e2fLPK49+abX+c8fsb/r9fl7ui+uWNn43puQvL14P'
        b'GX70u69E1pSc5j/eUoRQqjkW7ZpErtkPCY72Yjh0jC3KE1MqPAzkwE5KUNGemZxAUNEZdFa4evloxAxKUQUaiQ6ifYSi4gf4qnU0ATo6TVwEZwV6pqdoN75BSbMZXQdh'
        b'nBjIUZPYjSdVBtIM4Qq0TZ0DkvEtr2zcHo3OiZkA9EhUgk/ia4K1+jq+gW7gFrKRMiJdwoiHs+hYNL5C7e/oego+5HI1NbmYGrehnV5QXOiACbXz5Nb34WhD98Xv60Um'
        b'1AhchbK6DahlpFrwdRQcHfFeI8sMQBfFQxiBGw4dhi6rn3FjDFkmWgLiJr43lbLWEnxvobqHIyG5tDbMzlmX4ssO1nreTDxRoUHvOQ7XxMDhoqV4L7BAMvladBrVqylj'
        b'vePKW/HeaZS3Zi5Ej9VR4/1ducogdIlebZmLH6PLUD29oB7Vz7DfUZ+7iKYOw1tC1JC6r8D1Lt4AYJNkqvPwZnJxapseGP/W3AwgGWgbZxqufj5q++9eIe/mSCNcdE8Z'
        b'k7abMUUTtkNdFanDopgwJY6Db4FJ+QFNFj5iyqqEfQMSEtwbZc50x0fKibkAbgDnA4zM1Y1GaF5gUF7drKHLS7BDW7okFqvGbO0SQb4fyo0kZnITq7nKyXQMTs5Dmc4y'
        b'eFxk7TdeUqaznvmVvBd/H6Gj/wG/KxH1wxN//WEPA4JwQsrqOJlhN8Qa7PYRM2+1mY00rVquIXZ+F3PLc9nI5VX8agvUU2PmLcSPUbDj2A1TFqdx3m7U8WTbftZubxCs'
        b'YaQ7ZautvAe7k5OHSu1/z3q728hhHLweH8U70Dl0A7Xg3agdNaGrEL42HwjkVXQ+HzVKmEFovWhN/BhBad4cj67jnXPxbQCkilGhtklUOSzH7egg5a+oZb4S78YX0Bm1'
        b'SiUC1b5JhM6ixoGUOVdViKhif2SdJSreWyG4qwMVAwbrLCwdhXeV+Jahh/gEPhbHRCRKUvCjAhsRmPGdufhmpGrl9G5VTRss7GSfR6c4BxcnbBck6wZgvWuWU/5fh+6j'
        b'e2pCQtAmHVXjcCc+J4gGx/COeHQ2pEAoyaE2duj4Qv0bYUqxZTOk/1I2I7v1aED91KCZFSs/z1xelP1VUx17bXDBwnUbjhpnvGWxNS6xSX+UvHJG0J1XX3/wz83lT+ZH'
        b'hBf+9eX/ib2682/NKPO12UWLC7M+q2k6PChsftLeL796b3ZUwY0nRxqO7KxQd05I0U9eE/XpyRmvdhU2r33Pskg/+e5HC5ImPMUy7PvfHwVmpY95Z/1FhVRwV9+XON/d'
        b'6RrdRBsdm6KnwwVZvA3fhE9LlBnVA2m2X+uL7qCNlEmi/YVzI1XZXCVuhcGeYdWoZRgliSv65QD3ou+sUHKML/9CHoePVOO9VrJ7CcJFA3npULcH+X3gVG6Og2fRXcqo'
        b'ktFhvL377SPoPj5hZ0QD8V6F9HtIRy9uhxpLCVl03e8DEailQSwKpYJ5KHwT2kf2V0OA2rkQEHvRnB/okWiCxwfP0KhDvfgk2ptQsF3iGo210vM950mM/YJpsvNIXnkg'
        b'dd51Lu71rnM7zfqDiPWw69hNtggFsWhWkF8GgysBe/5DZaTjE+QZOnkE+RUhB6prEezbhDTxq8iBVWLujVDV6msiomhDdhpp9mwttpCL+rROG7XGXF6pX8Gr5LnEpL5S'
        b'b+GddJDWQQdAs2vkOpMBaH4fRM3t/QFOoiYTrvxH5/ADPjIdVkheOogcmdlZ6GxhOrqIt7G4MUoFskA63uJVE+NjI4cNQXo/jIE4NEVlZqtwE8hlhaCtt0Tnp8dOheUT'
        b'Tq5kUeNbXmh3IjpIHUPQpVC8LxLdxjvRearxiwws2oi3LqP2Q9xagrdEguYyvGIVswofyqSEkzWjzshcjmHnovoqBqjPQX993f3XRZYrkPiTtyST2qjzx+bDB0PDXyj7'
        b'mE2ZEfjiyxKmKY4pOOWXLtkS0LQpZkZSkm5r5o5Mw+Fvnn4u4TWKyqNVtooZ03N99Ke/uLT1wppmxUc3rmx+cXRlWtBvjubHrtv0ccyEqR2njU9K52xMzPnV9klrPnxl'
        b'99aDIeNufCRdPtxXtmfdZ50ntvx2/BcJwUcXfeNvM8kORFdMSxuQtPkva/5w860Vwy/+9fiGl6SLhv6srt/nGQ15j+pWdiYOOdSsCKQnWgygBj2egnfTqQZsT2bRpdW8'
        b'QIROolsgG4KgaX9BmQy3WIzcunW5gjB7dR6QKRB3VxKLC34wL5pjvNFpDh0vxjsEWfgMboAspIKmKNB+xGhvDjd04AIq6c6U4kfkVWxRqgzcFKKFdF98hcMP0AncTJsf'
        b'DtzstjoKbc0FKuljU7GM71QO70X3y6hUORgdzyTlo3PJWZyJI+q4CJBI71OhFR8Fbnia8AoFvoNOqXA7HVxgjKgCH8ui4x44eI5wazqhrfj0WEJem020Z3izNzoQCbpl'
        b'FLpalqFUKTggfYdFaDPeN0OYmA3oMjpCRexoUNyk+DDeMJEbyKPzQnKzFt1RA6oKeOodiu+P59BR9NhKZ0W5Fm8iuop9UkagK9O5QfhsBE2cPLbaho47BGK7NDwB76fi'
        b'MNoGLHk97RlAQ4q2G9EZLsqGL/VloPkeYu1CoMVk8br7upCPt2BikdFDOECZQVYVTCYhEFvr7ySgpHSO2/3/Ne5Uuo9OckLebspthsd3z1Du+gFu7wNwaxgqdx5TNieQ'
        b'Bz0LnyhUTsi2mTjaKfzMKeR3KnlMII/eSgnn59PIg5jqzZOEEdDsM+GRI1RKagOSZf+nkAhfHPz1e+bUPXG715rKS0rogaEuWY3ZVMObrauf57AS8aynPjrU1ENFb8rb'
        b'6DQJUx76H7fD9YksZrLx9ifG7pwjE4s5Ynpj2NAxnF2D+d4nFyDyA4xi2AEqPzaUG5o3ODlgiPD6xN2B+K6FvD3REhAgYvyHcWp0DWTce3iDTU5Ih2KYLzpjJVTJl+y9'
        b'5JE9l6FxYrwjfzQIwPf/v3tNkVeOsLF0C93Jx5fQQXKYZSQzEtfjuwKXOY87UYNaha7EJKJ9vtAjfItdrsDC9gO+jHYsdRiAqkWON8Cl4i3UUoXX26S4JSOKiGDxYtBu'
        b'W/A5fJjLxI/QRv1w2SDOQhAx/8V+5C1blbqPtVma18uewu9lukrdU/HVVXhvwd65e/fve9GwO3TAlfAZ27O9yn1meM2I3DlGlD5u74Z4f2YoDrw1EysklCbW4O0zhSOK'
        b'pvnCIcV4tGmxQHpOJE11UCUdvmInTPj0Slpw0gD0IFJF7eM+yXYLuX6w8O6KY7YBhBA7NXTQExo4U6iIEnHUis9NI3u3QuoSdEjH8ZWGvk6v+IECBtIOX0K8GCi1GuBK'
        b'rcYQsy6hTmJ4mm3O9SHuEpMCXVLh7Jin1yKtJFErnBhOyo7kHPWvt3/+4Co+0s1Qf7R/WmR4pjI9KhO1RQsbsHK8W7IEXQ3V4j1uGNTf/m35wvX+ixhyBwSgJacVbfIu'
        b'FvFirVgr2cRopVqvNq5YAmEZDXvTsBTCPjTsS8NeEPajYX8alkE4gIYDadgbwkE0HEzDPtCaF7QWou1HXiynjYMlwdJbNbyL/expA7WDyH0X2niaNlg7BNICtAmQKqUH'
        b'ZsTaodphEBeoTYQ4MZQYoZWTuyk6fDq4DpFO1CHukJCPNkzHQRz5Fjm/hVjhKRZyuDzFz/7WjjwQCHX5dNfzbBltUs+4f++pDT/QT6s4wBUH8yF8sDYijFnWr56pZ2ko'
        b'0hGiOUKpM6JwlEgGc+KljdIqYdb6UzdFLzpPEq1KGw1xA7RhlKAkd3mXAN/SzAaBmZqN3Ezw7mqG4Owopa/9kzoN75LnN7x7Jlk+guH9dz5AUdJPexE/dH2eVThFfnpW'
        b'KzOoqJFh8kpzfi9bIET+RbGW/Wr4qywTo1l0YrUfY4sly/rUDNzcfUAdJK+NWfnpbpfAAKlo8WIKKmRBQCiEA/RZBaOZmeGzoVOlo4JmD2Q+cnTzb+Shj/PKE1tI9/8Y'
        b'OXdY63eaq/7rY/zEv986o1R868jrw/2mljeNWlLKcTveGdzw589Kah9uf1XqO2BR7gfebUsHdfhs/dFPZy1b0RCybPLCkz+fJS3xKt/844aPfjcz7U9vTvOq+MWNf/46'
        b'/2rZvSln7oet2Jal8KYEaD4+NVB4cZLSf5iIkRVyVnwDdQjv8DqxDreAUnyZbOKBlHcNbRnPBaO76CxV5PEOvGG0rxo9BM70jAu0DJ9AB6nhuXZiuIvCjZtmoLvOqRkb'
        b'Jqkci7bRLTp8s2QVOQCOTpbBnIYrhRmETAOHiieiZnRAyNVYNVboLYjVe/TUig1CYjDeL0JH8W18SLAwHMUPFzuyBaIduD0bXWAg1y4ROr4MtwuvF20DCRW1RIMIm4Fb'
        b'ZwIfluFm8rbC8+iiNZJS/AVBqGXlONwB9VBeC7Wh9lwAe1Mu3qqSMqlqKdpNuixQ2OcWNLsPfA93pdxxUtZHImMH0YPfdvspWxviXC/PvPVQsHd2Sai3UpeYOLt2+XXv'
        b'bRlNXd56Y43NSi/U8mwqkJjJlZ7mNeRRxzjkz7Vu/YzuwQHechNDPfTveQ8SS0pIp/s42zqNc5zqdmnFeax7aPd1oD1OuKqg1gxCXp6zK/4lrjPXR5dmOrr09XCX5nue'
        b'6VY9b8s+JU4o9dHsHGezwzIc2R0+lv9Oq94lBG1KqvV9HWzOdDY6gOgacp3ZVP3DWqtwb02zqo/Wsp2thdLWiPftD2nLfm5aWmI1WTWGPhrKczYUVkiyOnx0Pbb271vq'
        b'PbIjjun5hj/KGeZUipi1lWQPutTPa6Ze4DzNE6VMR+0w+kbwydq5jP7D902chViHPnp8mgi96VmDNR3a8D+rNX66j0s/Zr7YH1aw9+WwjWEpbzGlNyVP3t+vYOmxlkGT'
        b'ioGW9UHISmOIi8ToPgRPqoRRqkXfUuagWvOIpFkb7EoF/t2z0wU9SM1lN1ulh0aI+vkf0nYqvl90sMPqVRBayNmMqeP+ql0wZ1wInZDdVa9C6atjoVJ29b/0Z4v2iyxk'
        b'a/7LY+eElwBv077y3mdlWZoszTLdJ8zfqgfNHUThpE2RKt87ouAo05mIzqILHiE1drkL0yEvPqTahQzfgE8LbopQqkDvkIjQRi4eVK7DfWkQgSXUrVhfy5eUGUzlVd1v'
        b'tXMAdXFtmMtcu+d2e8WqhPrDelImWhk3e0YLPBb0gO85N/j23qZzOTpATEQXxytXRQBk0XMCedOzr9zsualkd8z49dB/sk9FTPi22uop79YtZAQvh8MTRei8Bl+G3LVM'
        b'LdqKrlJz6Vx8JAmdX44vwAjXMGs0ZfSF79IsesrLzaO0MDxHyTIJqElKNh8C8P6ltLVl6YKn3YtZfNauLDlDvQybfR1ehtWGs4XXgl9hbATfs9EZdMpxrRF1NrR7Gi4a'
        b'4VjSrh6GIA3t88Gdxf3MtVBYcG+8BB1rclWtrfgkauEyV/lSv79bwYKX8dSl1VE/XyliaOT9bKGLcrbU8H6qhNGfnfhT1rIVqquWXR/bdjSAiw2aWXH7IWK5OZ9F1xyY'
        b'+oWXLNQ4I/38pZUbt5UtKNjwQb0+NfnVB8l/u3PjK92Bmm8ebIsxeu1RTMsI/83yw++PvHBj2tN+L4v7/U/TyxEPFQW6N6994jMpLa0wcnJVwYDF76/a3xr1bcKa8/LC'
        b'nyRfK+y8fmGI9cN30vS7AmJSymoGyt6o/HzKoZpRP190U+FFDYlzhqSrq2YRC6ir9TNFQnfsVxpnuDjLzZviEFvR4Sl0GWbie/ish2WYpHaT/dB6vFFwWLuCj6F23wi7'
        b'6A/VBqBtgjg8Al0X48vF6Bylw7ijXxC9l4hIt4AU6ALozA5KHCuVMjHonHSod5ngd9cwc1L3uT/iak08B3zC6RBk+DI642pYOI13k+3/AHyr+323vZo6pSUrzXr7G03d'
        b'hNASQs45Vg5C6GC7V5kfWxvksjJpQff3LGvMFZZeaDxn3upOCNrgsbgHITjl9s7LHs3llIvta1bK9HzrLj0T53zrrpjuREmABIgpCZBQEiCuk/RG53s620tz6KpeNHks'
        b'ItcgjpiH65kR+KCFaqyCw+3mxCWR+Up0DJ2YpyT+Hl7B3PC56JD+hV0y1kIUxKMvrKAcWvO09LPSSt1n2s9KVQPUGh9duuaz0k9Kc8pDymUh7+nez/Jijn4ok21JBE5N'
        b'FKbh6HoAqCXEjIIAKehbcWERt6OWIZViRBzuOx2T37c1W1pCz0hQEAe5gtgQQP0u3GaZZnWoMd0udvQtydQs1IPCi4X4Z/JSELfDQ98DxPtCegMxbdwzhAm9a5AAjKXU'
        b'pEDg7PWccH4OU4AkR4Ao6eeKNZEFSoDlbpYR4fvoehabPRtt0t/dKRFbiDVaeXHgp6VqzSt/Dv9jBpW2shZ9XPppqV4XsfvT0ielVbqn2k9LueaYpHjbtZMxtisrrpyM'
        b'bYoVx9foGMZa4Pev81y3LPpcDihub8QmpjsXeIa6wtMsEzxsiBNnf5dp7S7zfID1fK62Dzhvg4epB5x3DnKFs+cOPSHOQp4hniCsaYl9VUueE9qVz0Jb0iu0BWe6k+gg'
        b'wBvvik8XjUWPGYkXizbWher7Tb7KWsilBTsHvfFpaYYT3umaT0pVmo9LnwLEn5YGaSp1WWQF695/nWHOsF7fXPv6lddgBVPnhPW4baw6K0LKo0uCR/QG2fO/SbcroMR+'
        b'iagLvN0k7loC79pBLhPrVsAzsLukOk251WTuhUyLzTt7g/IOhlyD9yyUW0JdodxrZxSBgidvt2Mv8ent8u/Wtqv41V3+K0y28kreTIvEugfjunzLyW0uPHkraqxrIK5L'
        b'ptVbhGtYiH8wee+7lVyty9usmlX0dliyl9Tlx68qr9SQu0tJVJ87X4p+9BR5l4T4NMV2+TiuWdFrXY6oL6A5rHqrge+SkTdnkMxdvuSX4+g3jab3N9Ga4szkdoQuL3Ia'
        b'scy0ip5P75LUVJqMfJdIp1nVJeGrNXpDl1gP5bpEZfpyBdflNW3GjNyinMIu8YzcubPM50jT5xkXk4ZDFibSgIWMyH7br5S6LrMNMp3s39noIfgwqMfiKRekYtWadexX'
        b'xkUcE6MZkhMmF+6YAEHoGNpqwbfQ8emBgDQcPsVGoC34Ht3FQZ3ogcRiXYnur8C3AvFNX5bxwp1cAD6Lz9tIt2fORScjidvkxfD0bFVGdj5uzEEXo3B7dGZ+elRmNEi4'
        b'IFeRo0XoPj5CtrrwzkV+Myagw9Sfagm+ia/hnfnwsxbdWQLi8WV8S/C0ah4xNR6fwu3ExZkdz6Cdg/FDG/ERL0GbhsRz5NrJlHgGsqDNVLwPHTYgHt1YmBDDMWw4gzrQ'
        b'uUhhn6olGO9XZ81dYDdjsoxvMYcvLUAP6e5XaklFvBF3JMRIGVbBoF3oIN4mXAjSMQufE1xhE8l76c9H4qss3omaM+hkipZGMoXMiywTVMp9GlfHCJWhk4p4ICHXE2JA'
        b'k4yAybUkCdssI3CjWqVUETkwW4mbs1hmILkKxFs8FW9ArcItqIPkzNSEUBFTUzqxfaGKodOAHqJ6fCjeS5IQI2LYKAbtnYybaf+iwjSR5MoRE76TIYiRgahNVIb3JtLa'
        b'/qgdwERVhnCMvHTxj3Xx9toOhovj8UF0PiHGi2GVDNqH7k+iNLUEPSInxrYWetM3AImjWHQPN6PTtK4riinMWvkYMRNTavZZbRXqWoqa+sWvwXcS0BXQxlQEVe5WUpQC'
        b'UffCWuJ/lQ3akncsOorOcmivBu+llf09JpPpCHpJDBO3LGBtAEM9zdF6dBN1xqM7UVAdwDuaQfvxqbmUueurhwjeZsRtAN+2oS3c6HkRtK5r2aDrpFyQMFNLDT9X9heE'
        b'AdSEbuAH8XibLiGJoXO2axE+Sk8c4nYtQDST+AOjnSa8VU19lAPQJtFk1LicVnlreipTk+XDMqWlcZ0V4+3e+5sxKGLx+NKIhCSODnbPFHTORkQ+fHsNPi5UmZPlRLHB'
        b'qEOM96GTqBlfUQr4fAHdQSfjR+KTCUlSOsC9pePoGhPj+hJ7nzbPyhFAGVAjSoGVuYF2aZS0HzNm6O8A5Usn5oRkCdPvh7atgflKiiOIC2PcjTvwFmFFH7egDjvicoC4'
        b'lzLwNRZ3rKuk5caF4/Xx6AS6kAgaOBsHBcW4k6ZIQ30j1cSpj2WkSWi7ngvD9yfSFBZtCo5Ht/snkyIp0HN0ALcLi6TTgvYCGqKr/aNVGYAwl6FnE0VBw7V0TUJbGfEz'
        b'8K1ksignQG5JGtVhtbPxJkC21fheNKUO58SMX5CoP6ycTjriYUoZE7Q2kgAhqyK8xA6EHfjI0ni0BzUnA80n1e1D7QvokEvQPrwdukEOIaoBS8pyy7kh+DG6Q7uftxy1'
        b'xqPzk5MTALPSoBf4ET5I1yuHTkeq0fYYNdli4Ezs1AB0we6uuRlfgiHjDckJ0PWJgI4v4D2C/r0F3R2kJnStFbfCVOGD+GA/zhs9xA9o3wMza5kvmVMSwO8Br6kXCtAa'
        b'gB5Auet4X15MgoRhpzPocL+xNCVhJgt6QkX/TLIXIsKPWLS/roxWpJHMYVprCrxgBfvUhBYJFSWMs6HroFDsi0kAejADiCA+miis7QfoYZ3aOByIi5ThlrLR6BC6TytK'
        b'5sKYGDnDwWwOXaEcI1Q0fhV+rM5AVwcSbxyxmEWH0XUbnRQvvBHdxDtBfkhHe4iH7Um83hYBCYXoEGAxOcQwNx10XuU8wUsNN2ZHAQUiJ0Iv4jMhXkNWsRQoKeWrnUdQ'
        b'iQq8dzDexqFdvj7dFz93ThEx4kLiJVIaNT/fKByzxXcCJuOd5JBKx5woJqrfCBvV0o9au2+ZcmzRdaLdwG3EzFh0TmKLq6KgC0P7xLglPzEGNwMdiwwNYZesRo10ZFGm'
        b'BPWiVYW4DfAA72PwFXQ4k/pkBOAj+KrbeelBk2mvx+ZK9Ay+LNCVK8Wgwu33hY5tBJr2iEGPkvBVWl40DN2NhLnIxlvTlZlU79OPyYgVM+MKJXH4zCo62MKCIUzC1LGE'
        b'8K29LQliKDObiw/3x/u9YPUtAkEWPZ5nphVmjcbnn6kQ34vKiOWYcUWSeKOGrq6loyeoSwLzgafSg7kP+6MGCtrKIehCQfYEdDqfHG3m1rBD8fXxNEWpCFdnjy8SJuAk'
        b'g2/gk7CQ6ebcnf5612PoGfgYnYARqEUMssFWHZ2CBYV4L94PgiZ6jPegBwTnDuHjAmm9X4B3wpoGMpADJTOUcWJmCOoUl/kY8OHBAobuQ+fm4v0iMpXw+yEwt1UJwpHs'
        b'xzlou1thDgrvF+fgndXoXhQdrR/Q0+OYmCKXxusZPWpBLXQ9egHVOE2cJ3Pi8CUH/Q3sJ1pmWyiY/drxPtxEbQHo3KARzIjkKjriZd4DI4UruwCX7J4PQ9FNMd6KtuHm'
        b'FHSJwmdVfAreD0sBH+TRfQbdVwbZiD6uNehwC6BxMT5axVQtnW2jF1SdWYu3qJXKDHQhPBNvQofJ0uo3VYQ7UOc62pdI/HgN3u8HWc/FoRsMujFvsOAzdDnASs6goE3I'
        b'7RDKcixQMHwRN5gtgdn+/kCMYKnhi2j3VIpUNV4+TOiC74gYEuVTGC2sINHiZNwiIpzlmokxTQXsJxAKGrYKxLR0chK9VZ2rzByFN5AOyoeI8ZUho6jRckbeGPZnUFC+'
        b'Mqf44xSDd6VgOcU7RuSi8yBOTkPbieX0EL6nr9swjbP8C8TZn8fpl/ziHeNbeUHS91N/ot6ftPzdvOlL3p7+zj9vTlUfyTvyVP3O7ZpY7tXdeVrzk3drNn0Q+YHvy/V/'
        b'SZnIvPnS56+e5ZcHj/3bal3cIYt5yrh5TTmit+u3HQz2L/rsR13b8u+OSAublTBn9K6zN5Kt7/DR/4jjCwe++fhs64Lx9/KemD74+qusK2/2m/1fl19d/NHw5FHa4n3T'
        b'Jw4LTm4bvdz3u4RXN+S/eyuk+fWpE+bdanx9+q3iJ82G+tcXNs3888jfXnwa9I73Ozx/+5VDxR9Jtj/ctm7egFn/mJE0fqLcfCXpDyO345uT58zcOn3rwlSV+djbH514'
        b'5WzngQGpotSqDw+8svoVSaR61MCRe1rLdf37f/Jfh999aUD0nI7yN3/zv78/YJ6f5F/+xzdWDst/9/0PzZ9OOfNl/8FT2k7/zDZhuc/BX1x5NfJD7+nF2RFf/nr1b/sv'
        b'35iy5N3W/1EukKc+jBifvviDC/NTp21dhOe/dn34ror/tkT/4y/vvZFQsqtOtFT1pfzDqn0/rg7/fdWvwr/KfaR66/Lum0u0AXXL202NF9v8101/pEi8faXlt9cObvv1'
        b'rM9aN3/etfLAH9bw/r/fExC4bNjgt4dnfnv8kwcz6qK+OLEjaUr/d64kJ31QETLlsrHklehv7wdX1ym+OHdutfKvQ+qqEh5fT/38R5OPnGtfOKUuYPvF0D+bFZ9pa5sS'
        b'/p6WNeSXX30ZOGbMR98NeKjoR82nWiAPl93cBAC9wpO7vQQS0Xl62DgZH0H7IvEmvJtY0TnUyWbnBQv+WQ2w6K6AAIW2TAHlQcqIZ7LAT49YqT/sOlj2B1FLYI2fGd9A'
        b'bYEr/L2lTCg6LKoNMukC6LXDoARsyPRFZ6PSbcqIJegWNd4G43si4Ei70WXBZ+CqL7pLvcCuoEcu/qloKzREe3HKBKGWaLuHqgwfH9WfQy3hftSeOwV1WKjxV7DpybKn'
        b'sZwWXdNZCZWwFQ1Uo6Ojcsm4VrDTcNsKWsY7B9+xe5YRv7IzCuJahjZUU7ez2v74ADBTfDyKOGjQE4ED8WY6UxlLEro9N9DtxPFc8MRawbv3zpDlPS6tw6cmimUjFlD3'
        b'iZnoxjKnk0U7upvp6mQRhrbT6VoWn+qS50Gii4cFSPGnhPMWdzT4MHXqODec7FMQpYV4M9vHH5kqQbemL6OOHYVTc3saPYdUiqH8LeCYjbMEt+Yt+AyuJ2oBbpzkfjzw'
        b'MW6m87W8INrp1EFdOsqWcGhTcranW+5/sNNnl0ijFQwyVng4DTIvMCriCixmQ6jbnQ91EQ5xfLgQtscH4gZ7BbFjyClsdjCUIH9+rIwbzMrZAFoiiA2gOYNo7iA2lNTO'
        b'1fp3W1qgL27exsSD6ocecuOEUt3meYAic45Ye8hkOq0965nfDHbzPXbrhefNcmrIE97KxDRInIY8ltoinvNScVLxcOZZW4RCsEXsKqDnsCojvUqzSuYOZwTrHsk6GT0a'
        b'jXZK8HpyLcpwZjg6VUGZWuSEMLSTMcP6CAMZrx21C9wd5JEp8WIgEIcZJo6Jm4gbhfs0K+hrSWTrDKWGHXMUgrj5mzVr2a84Jm9SmibtxRkjBWY5JjIgPgE/DIfeoF1M'
        b'ufccwSm2FT8siE9ATTYQRNEehlegzbQOn/lSer9fq7w066atSqj4Ih9MXtmSF20u9ftFqZ8QeSjbn9hiBvHFpVG/854pRF7OAn4NYsV/9y+NWjP6BYZqUUPq8I6CbJDW'
        b'ioBencIg0EpWgP6N9mfRvixjxuDW6PgYYggZQy5Q3Ylu0cr2FI1mZkJlRWxp2dkJSwWJElIP+QO3XrqCbnPiR0payapotB3v97GhY/RtHrAyNy6nskU8akMn8H4pCHwb'
        b'IOk2/A+dK9RUj+6l4Z0svgbAUTLKUSm01XUGusG46umc0qjOCXV2M9INdNsb78S7yOeFXNBx8BYG3axeI9R0D9+G8exkhwCyDmOG+Q6039SSZHNuZKKbkdRNmMsEGfOU'
        b'sFFzGwS3R6NxRwHdpmHxdjaE3IdC6yQ6+bxIr5ip0BVmFT6GNghNbQzGJ9B5phztZ5jVzOrYDBrtC7r4IXSemzaIbvLOR+vpjio1zu6sPF3ObHtEMJadeYvul/50uYyg'
        b'T3pkeanhQXawsIkaPVR4Mc+ltaV+36yw76yOmUlfq7PqxtzSKKNhlhD55QsUyqUHB5ZGMZEFQuTSWfSenqnFqtKof41aJUSap9PJzOuvLo16WhokRLbPp7u1QYbs0ih/'
        b'dq0QGbCSRqY/Updm/UkSyOiL5aNEFuA4zN9Fr1Rvz8gRxQbNOv/09fKKcZtWF49++8qMxfL5X80dU/HWa4PnDZgbbQl6mV0wKmdDCvvHoLVp2ZUjB9z6dMqvz7yWcH3p'
        b'UfX1zNI/71g4fuuh/ME/DlvQkTfu6qUPXjvzs8+Dvqg89dL5jZ/84tL/ae9KwJo61vbJQgirbG7gEq1L2FdBFBEQVGQRQeuCCoEECITFhChSFUHcCohaVBR3UXGpCy5V'
        b'cbmd6aJt7WKrtbneahe1t7XaWr213i7/LOeEBJKIvf2f/3+e/xcZck7OmZkzZ87M+5353u8tmpTwIOWDxEf7d35Rd+DHay3f1eYHfZvnoZi15GDc3M3HUi/eXnc8qTx1'
        b'++XxG+32Vuw/fyX/dOiI2R+HNfpW7L166ZdxlRU7mxZNKj5zrzX1m7WPxwvjJ8dPvjb4gvu5bfYFs2btvHDtka2gIbD2t+mf7qrPdCv/9zZZrU15Te+h/8x++0CY+55e'
        b'UeeKfPy9lnr5H1/e+LDfj7Wnew5YCPwKRmf3aAzLvrRr+XXvO6+ft3P94ecB953Lj83/4OHPC7yKqpac6vv6myduvDvz25pi17sv/fFGgmevUuyDExPpb9GnBmx2w/6B'
        b'm1OIM6UvWCokzgDJmCe+C89NJ/hgvQtcTabywGlpnHt5wQIWVoxPIS6acHHv4ayLZj+4mfXRrKTABgGRJdl4ik3CdicObpxo58VjXKIF4FDyWFLwOLg9HRyAzXD1BEJj'
        b'X4lwxCL+QLhsCMFeC+E5547QSw+8RHB9HmiQEmwjRY/mSlwPb7AKVOMXDYd4YDtYE0/Xqg8iyNQKa9JlnC8K9kTJjqZMqVW8YL1AEUYB8ICKx/SYJvTgwXpyHTlWsM5A'
        b'ewilk3EbuQwWgIMqF9oM28GJQaCmIJNDNQjSwB29CXwIhrvg2nY8ggELqLTnMEskqKMKReDlZG+/WCuO1cliB9gGl9HGrIyAVe25IEgzbxwHaip8COx5AZ5EOLPGf7yP'
        b'nx9+QR0EzqNawn0C+Aoy+XaTykyIgaupllG7HyumI1Nf1hIEZXFz+kmxhwE6alUCqAq0YoR8HBqjBW4m3aFoZCy3th8ymCX2O1PfhLngtHUHFwLYCla2uxGwTgSgSkTZ'
        b'WHsDEjlICreqCCpFmHQCqCG9GG6CO4fjinRCaHAJXMeiNNQsZ+idrAMXQK0eYU3RcG6zqIetYOM/DI/wplGEwNZkNpCQFLzCrRt3aQ1MiF3xCNDKNAZaanuekM/FD3Aj'
        b'MMsN/fRAP73QD952JLEE3MgRLuwv/uEC4tjzbXkSPl4vteeLCbOr3LEdzuCCzbiuWaBvGXqyvYqS+yYQVIPRilmHIlEORD0SDdJ/oM+HSKbJ5L96DUPQ6rN5W8mePTsq'
        b'nWKYocZglXr1Endf7OmrE3P+n9wnvApFPCcp2Qq/JCG+GmQ1nyz1kpVAnX1GSnRqdFLG5OkpcWk6gUZRqhPiyAA6O/aLtLjJaQRGkpagbfmfx5pQYx02H9ysuPpigZNz'
        b'lxhWVo5CRwdHkZvYyZqLKiEiPUFk9GMroD2EbvE7fMv9OFk58twEvWLJmxrQOgo0oPF/IVirnwKsGKfJghkieNJoJZqTZNFEdtR8FTZ0I5qo3bi/8qH6T9Z11nIpQs+Y'
        b'R9EtBzNe7PQKsPZyh2pG7ijvxirAOpFtZ7KNFWBdyLYr2cYKsG5kuzvZxgqwPch2T7KNFWB7ke3eZBsrwLqTbQ+ybd8gzGFwreR9NvMbRJjfku8g79ubyXfETBB2ux+3'
        b'3RP9buCv4sk9WZq4NQmiZLe823KnHBu5RD6Aqrui72yIVqtQPlD+QrV4hhNuDfmgOt5yajXYL3dANgPRnUXHO8v7E9cdL1bHNSE57ul6I2b1ZE6OFH1FRVwlUqz3gfWb'
        b'ZEVy3MmVHVUjjTa8JmOCNyvYhD4VZ2mKVVg1GvPSceheqn+JQwcrSkpp9GpCUu8QUdk8D9NaZ8NqkGEFH/YjWTwW0wijWMtHnjNXJygoQvsKFXKlthDtE5egq5lXrJaT'
        b'MYL6vBoKvxpHruJihNsgw8uWXQ6200euepb0a7Wn8IsfBV2VfsVt/aelX5+t/NpJ5dUkRf9PKr8atL++HjjKuIVaoK/N1aFIIlOV5Ml8TVUlXJKdh4rMJrG8LQvRWtah'
        b'NaE5+xwt8kwdWtT1aNjj2LEvSlSyLKx4jj4aRpL29OsQo5kqrZmshXHVSdtKgwyawkTl2Yqg7v8MFVxziremYziYU8HtouKtyUzbVXAlf17xlnvEabPTLYlSzt6w4Gfd'
        b'MG5cYGNds1sStSJXqUEtjMYoNJSR7uQj0bK3TVuEY04/t7BsN/rOxW64MxWW7dHSN65sJkMcOAbBbRUmFWDhJrC3HfQb6b8ujbJ3is4geb5j252RMowkoF+U66HIUYwW'
        b'e+2AZmRlnO6YK9gFX2Mla9lciV6LYcbbSuxhM5qOSdbXBjlQwdoXGyJ9FR4MiToLX1VNN6kKuyV/vIEBYlhdcAqssAM7yitIruoFnNZsi+ZhaCRDYvjCelew22QrxHun'
        b'jUfQvsogu8Ww3gasS3Yg2TmGs/K3c+17j4vvQVV1YUs/gclK7gLn4Ip2a69DLU/agV3ZY0m2o7uRFwjigB6Pe/3DJpPRYi7/NPwOw1S+CwuknE1jlOUZcMAOroDNoE75'
        b'ce5EgeZllMmRv430fe9dh5hA+9iPhleMli6J+aaSf33a+Ii5K2zFdlPHeH7yhrxht/b+9bAP+i2zn3NOdPjQSL9Xxi3aOjtrzsX0BTOavzgpHAmDCu9/pRsaapMUnZ3n'
        b'1XT8rvOtpev7zr7l8HvlvPLKKYvyv0vLXvmu2+2et99qPTxxy6oTfW+NfjLn6cJNM04Jz/3Gu+Iedjo7zNOWvNIOdk8l5iU4r+9s1LwEx/tTy24d3APO4LfesHpSB6pi'
        b'1BSqGLsn3NPQRgVrSqlrR3/YKISHC+FG4p6LQy0TTRe2p4AasMGbODwQWxWuQ2YVsVaxQbrP289zaKZe8TbYkU9MpCzQglcJXFORLc3Z0XADqwYDd4At8CAyyA6gro6t'
        b'Q9Y0nAJWEAt0Ojg/Q2/wo5o0km7AmvyuMaQ9+kQGszYq2ACO4XvKGamBLqWYGAOOasB6+vIChwA/qSEvL+JdnXziEwmS9RUxSaDaGlXlBDz0l2F4Pe8RAyMDq66CiSHy'
        b'tjxRu9Qtlb0lIUv1W5yaLIIdZoRvT+HkNE7O4KQNJ2dxcg4n5xnm2Q6v4q5k4mB0TZ7oRA22tQ3MvcXMZ0bB4DrXvOtys3rAZIHVNkVgrICLSzJQwMW7LCrgdo0umcuJ'
        b'kxqgJwuVmsZV6mm/DjUgaOA5VFFz9NqzLE6yUGq6vtT+tNT/WHlXmIGwkYUSZ+tL9KAlGiCo5xfYFWYgAGShNJm+NGk7SJJ1ZKM+n7avXmqXgyQWypfry3fHLzEMcMuf'
        b'UhPmcIuFEnONSkTtq8c6hn2YT0nM5CWH3l02OVvAVgS7meOnlfjLYpd+sjKFIzrwWSvVloT5tc+x1zudW5l1OmeDmj22cumylJICy0R2VUmJHPw8QkqGwkmdssRCSnqe'
        b'sZePxMuQ7oy2CX8aHWQoA0OwK60GVtfoun2nL2iEJK24EFsJ1KrGkddYzrIsq1hbyuoTaRAeNdc2+B/WAlHgJpErc4hSTCmLt40vim1vElYSNVsuG1fOBNTF/+L1ykYy'
        b'S6ZbYKiBwSKRcvIp5k0Xw3alsLzTgymRRmepFdl5RVi5hbXjSHQ5kxVt7wcajTK3iHQFqo/SSaRLI1EaXpUSmTS5ZkRYOFMlkNzk0HC9xYJLCvT0we9BOCVffIReyjfb'
        b'nJFFeqWSnI+1onDbDQ/vutZUjvEF4atWKjR/nVKUFCsjEU0nT4mXVyE2o9HlzPfy+tPaURIp0YnypXJLz5O1BZ2oLp3/vKpNEjNqU+ZUm/y6Vg0j0oZF7SapXrsp0FOS'
        b'HhhkXnvJkPjB3katgl6OsohUlGirxyYlTZ+Or8xUmFn8r0Q2v5AEqVWo8cTkQ4TZ9NavQYWCLFfIoqCU8bsQ+rT4c0+KyWpR2GMoQ4WKDw4wryhmSJPh3gwZPCZoL3oi'
        b'izRKWqniHNMCXfJ81DNIe+ATSKReWRn+3EVtIvwv2igTDXkppszOK1USASpNuzxa52fWbJ6+kkCs6azQosFVnwHqwUoJ20RohCpET1zcFN/JstIsBX7RaFouy1eCugsN'
        b'JarSFhYo8ky3v68kuMNhpDSZNqdcW6pAMweO0ix5sVitIZUyk0fICEm0NidPkaXFjx46IVpbWozntwIzJwwbIYkvkivnKlFnVqnQCVTETdPhys2cHWqqys/fQGGmslEa'
        b'VKvw+ao13FR+z9cu4aQh25v+GS1vcudk2pPxG8EO9X7unmh4+TlqdDVS3Lb6OsmyyrW5nua7n+HpkrDB5jug0YGB4eaORN2syL+zPib9cljHbELNZRNqKRvUKfTXZyGP'
        b'4YaHmb20cKPMTFyX2QmNpfGhEY79RPAAwqRobOWGcmkanWPNTtjtLEGsyY6mQrqFMI40AW0qitAv6uYSPAcNtyDrrucXGmcT1CGbIIvZECqikYiglCgHxuL5ZpjZ0/TU'
        b'RXpq3BQyUuMdEil6yNkujm67+WbQqrGYItalZz/5SAywXdyUVIl0KmzOU6OHFNUlxHxVDFiT7Znpd7OV4rLSFGjVms6VsgT3zMFLAiW7jvz0EC3a6OV+1zAM4XmOkCTj'
        b'P5L0oIBZXT8tiJ4WRE4zfzc4AikLIdltbCxb6geEXYpOwX/QgZ2PMz+KjVeo1UX+Y9UyLUpUfv5jlQjdmR+1yOHmxyqcj/nxCRdgfoCyVDIaleLyEAhDY7/5oYnUDWE2'
        b'uelqmGs8hGIVilKMLPBfBLBCLeK7rOKyERK8VIzwUw5GrWgHanPzNxWfhMm99CyZSoI3LJ6RrSzFDyRKLcI9ymXGR9IPJGMfjNN9gwNDQ1FPM18nTCZGFcJ/LPbIHBm6'
        b'2rFoULF0EKEjozuE/0jSQ80fyA5znE6qhR7NEaVHSGLQJ4qE04PCLB6vf7TJKcaLdxbbm6Nfs2fS+2N+sMa0awTRYqKT0e0xPyJmKbNRhvFjUNEmnkgjAnVnp2U2rJD7'
        b'fP5AnQB/yrSPmOBHnXeVYMWivO7GTDc+WOcMmsg5H5Va9SrjOTGYojqlqBflCcPXeoFdCfGEH7SAkO/mCcnRLYoeM/z403DQsAXV4yKpR+8weAisJYQ8P6Ykym883EoK'
        b'7pECjyQkGrCawbZiPjwEd4aSrPiuCwXT+T9YMQGykYLQAoaEmgcXcsA2a3DIG52CtQMnYm9BcHBCEo1vxMCjoCaVKQuxyQXNIYQSVOimj2Nk75vae6gNXYeLAytBtak4'
        b'Rjib8XQZAmzjG6kl1oGN9p5gS4DyYO9lVpovUC7H78YuXTUqHysR3r084UD/Je9mPt5XW3/LtdnhjTmjV0gqxR7DHNfW+FTOyVbzp0am/xB4tmlU1MuVX5wLuxnxZtuK'
        b'37tvlhy8kf7zzifTVoZHv9oqd1B+/9mofR+l/tQsjv/9soN20DX408ad53d/PbdRWdbwZf0d/qvrgj5MfDty/u285odPQKzt5RnB2VUvzrrW8/6euBsRzfc/m/X2zB6B'
        b'86d5Kq8uuzF4kd1Km3TdR0fezzu+8PtF0cFLIjecaRw++15e/5dEjy8eDqkOj2hu+/BI3phPg51smmKfVKb/8YFT+Z5vv3ecHT9uwo79nmIaNT0GHqVEkAGwllPhAxsW'
        b'0dWmJmu4jYrtMU5gL2GCJIF64kroWgTxCtXEeNgaAw4KGZGKP9BmOtU2apqpNKaCgCp4iKyKSWBVqT8+pBKuxiSOjktFxgtFo8B6a7AlDxwm4koL4DlQA7eC/YYBkQyj'
        b'IcFTsIVG6lwH22w4Xb4VmGRHZaGoMN+smYQZUwZaF8BNoxMS43kMP5XnlWHVmcxh/xdF9cZ+a2SFCgclN1qhqmAmiom0npDnyBtEQiPhz9iH0JZdneITD0R39LcHz4VX'
        b'bq9fh5HJ5clGYTna31Nj53GDJSmb56q4p9Agk/YAnvoryTe5LtU40HBdyqiWppkcJMwSdililgv1YZaeJVKU839PpEhocuBn2SpvqbHvvVhjHZXp82+pFQ1DMwnuk2m0'
        b'mGhcJ2TQg+EOj/MWgmUDKZWFUBTOwOokOwEDtiQzU5mpYOUwEuwgBS5XpdHTwMpgHmxj4HEbdrpI7I0pKpIAHhq17ycNovnYlYLFwSFgdw7LRQliZ5FaZ9gaHPJCPktd'
        b'AUfgBpLJjy7YxyGAz5NkqnIHs+SX8izCXvDvVpKpuhwXTHfmORL2QneHlEyf6CksR2X0FOx80JjOOGUmDhjjwRDGq03i8DSGCYTLmQHMgDHwIGkCuBXTPYIDsFAh3Au2'
        b'8GAzAyvHKUk2ZwodmT7M9TJRQKb9dOlAyhMZCbd4c1QXTHMBr3jxwJmxoJGweawSwEGW5zKtHwPWhsNzhKPjUAJfC0atdaECc3xE4DCpkhYHE+Ex4PxAzE4ZHUyiKfBA'
        b'LWjhiChWqI1AM6WiwFWupFrJ8YXMdUYyyTElc+za7D4MOWsBupKWDuHq94FT/Akj4QFCFCGn/t0RO3s4MfzMTJVN77l0p99gN0bKLC52jMqMODRXSndmCV5nFvMuhjqW'
        b'ZDpf7SujQS5gpSc4o3EIRtc3BB7igwMMGmsvLCDsDncf7JsjHicoyfSJimDJIUdSsAeMeJA4JVNVMjeT7nxYju/O9gpbp0zVC3k96c6hEsxKelKCcIMqWhNA+0exW/e0'
        b'lJQUTMzfzItFs0E4G/PEGR60TUthMAlzD9ztjirWbzYlyMML6dwXXuFofw5YT0hC4vnwFM0Lrp1E8lKA06RkbSFuk4AoJjPT3kU0m5Yc4QlXpeGjGbhEXsrIQAPcSI7+'
        b'kFzmCgebkszEcF85o/y2YhlPMxKNXE0+vxauOZ0Mo9zibnq8/Vnfi1VjwPnb3tJfmEG2Xs3iWZ4BIcl50nv51V9f2bbsCRN7OSylZGjyTreLVy7+/F7TvJsPfTa+N2ii'
        b'x8cxN/ecPpp19VKd29OSpo0zU796pA2q/2Vo8o4xl6o+mfZVi+yKZH1B/FWRWGXVvXrrD5Gxj9/02dMyuL7l7jtnp4RsPjps6+yrhYKkOyOrzzatWR0SP2PQOO8vZ8Xs'
        b'bS688pWvbkbqndfj48MW9R+eFPnRZ98Ubx48enKhh+zTf27q2frkzfk74tc1p32+o+2gennR+QkPeq//x9tVfgMfPXn80+LAyBnbP/9ldBXPr9eFsNWfNa6b6zxSuz+o'
        b'/oHVmPT4fUFJ4V+8uWGb+82fr38QqZm5/rdb+QUxr0y5e/5M5Nh3vx379aTw7672liVeeKrzv7311DbB/bH3m398ZP1Tipof28/TjfiF+IMjTKe5HlbBjfGdHUOWR1F/'
        b'lcULQbM3ARHoOzFsQ0izlQ/WwJ0aAj+Gw73wGAKKiTymHC4RDuCBLWCHLeXDuoFlCQZau2DXQv58cHQB+TIY1KGxT68DE9eLUGL6WFMvnGZw9qVOoRxqrBlJ3DRw1srG'
        b'BawmLFgFPDmOUFYETN9+1NEmnYaHjALHQFuZW3voVBI4tX4sxUXnwWZw2oix4iuiHkWB4DUaG33TArAhEWVywIhVA86IiJfOKFhfBGoywCFDSgvrIxQNllHQ1oag8nYW'
        b'tcHaTILasgYTnsVU1/gEAzKLgIGHAx3BEkEMXAv3kiNGhIEl7QJlVpjTd5xSYevAIcpWrgwF6xPaySxozz4nx4WC2FlgP7l1AeDITFAz2lfPZuG8hOaVkmv0T8VhB1kn'
        b'JATO1hBHJLgErCMMlpe04JiRssWYOH4xPAeXEWg3GZ6yRSdXoufWgJzE+inBU87E6coGZdZs2M56l6t5aGyHh2dGmI1KZxnHFXM4rqgzjivBuI1VWuM78SlXwIml7GIm'
        b'iRPCcX3QXieE69o1KJ3YXz6r0GaLVSlZhokTyxnAei6spBpBVJZV20xfWif9Ngzi+nQEcYuZrcbxFDsWivLBkkJ/sYxb9f/LuHWCfaZl3KypNuU09MBuMiXjptdwywar'
        b'rUtAKzxMJviy7EgDRTZfGQ9U4aCfBMJ0m1KOJdnK0DN2lClzgqcI4AlCD2klVmWTxfNS0bgEKrsp703jCTTYAvBIvj3qMhFls7qVO9TqnW29hjNZ8q+ZxJnMaqlA5TxG'
        b'1Mwfs1z+es3QaeF+8d5HF67/bevVsrJU70fT8kNzb069tOfjj0e4lK/pcd4ptjq/5fGoygcjk/8+Nu1a76WN4y8P/Fs3YfrMO7mr+iRJMkSOYxtT+ns3z5dKbqz6/vCk'
        b'f/+8JeL9gSFNFfBMQUqR/9B8gd1I7183xnkc3LbnWkPLrSOw39BPbt4TvPNdt4+UQf+KnuLZjcZQuACa4S69HBvcCJbzwCFQl0aGPbhagkYiKsl2DBmnrCwbfyGROiah'
        b'wxaPQWMup7kGT8KDomR+H7ithA6Kp15E1icnu+ZT4MDJrsHjA0kB8S846jXd/ME+sJoTdYP7wQU6452GxzI4XTY/uEXACrMNhWfJuB4YiGZHTpgNLIYNaGLwQjYEKb4W'
        b'jYeLE4zDEoPNwwW5LgGUPrcOnJujF2YDB/yw7qUWUKHhYLAnlKqfcaJsYDmoFIClds50UlplBw/oZdnQpVeKIvg9wV7YSFpG5gyPUFk2WAnXUGk2Ptjh603b/QBocWnX'
        b'ZRsQJIrh9wKtYDHNutUDLDGUZcsBS9F8zKDpEFc7DYHkFk6YrWKMCOuyoWs995cIsxGVLzKae3UezSsY34GWtdnwoPiXa7P1F3KRkxd3+PnKhEobVwVLKm1Cyu4h3xOu'
        b'H58Wjv8ke7p0ZPZhdzgDel8XfFZbGRKwvVRRqKH8vA4Kas7/0TuULtzGkygZIGBfrohFQj6adPk9pF0XTMM3uBdPMs9lJLG4JmSBtRo9VrViHNz54EQuMtzOwSZPXrKy'
        b'bd9JocYDzVZrHZm4VZeTQZTb0geJ6d90S7H9bVz1uDl3Baec5vkku7u69NDVrVRtHvLa433n0jwuD7p8o/h+eMYFWK/Z9rhyUkrPu7/JH3zY/dK92p/G7fti3rKC6RV5'
        b'XxfMT6h4afaExu7VvyxRtM6b8/n7r1YVf7KhfE/Bvotbf7+ev+LtKz3PLNu7TyYue8v58PA7w4rL3vW8e/buGNcBsZ/8suTn8Q+3ij+4XhDhc+TeAp+682vO3giz9X4j'
        b'5suJQe9vH3Jy7ECf3r0fj9wxqN+bmn/tLgzXrb20Yc6l7p8ueLvfgyY3D9XgtmG6lqYYnb/aPWRun/jiZWftRFOfHn/06x+at6za1q5K2d5Qqnx0q3Z2QemQ3KDv77QW'
        b'bll7K/uV7TG+G8tD8j90tTo82mdDjhPPzlNAUDrYjp7sWliTyPOHh3CAPjSI1PVkR9xEX6OXhPBoD+o5LwdN1HX+lDs4Y/pdn60bAq6wuvMLO4//ns723Akahfjcw2Yy'
        b'IXxkcUaGqlgmz8ggoxAO5M648/l8XghPgkYdEc+FL3aXuLl7uY12GxqBx6RRYoGj3ZAKZq76iv75Euj4GRkGQ477/4Kr56k/1j+euKZ4qKfRhr+JMtR5wyOdIhWsBjWg'
        b'Hs0AKycmgpWg3ppx7A02Jwn65sIG5YuuvwqJHEDrd/f6rrxkC6KcrNpyt/Xq/nrd9lsP438HTgPeuxExZOjS3D96FJ+YkzwlbnByg3LnGtGifWETIx5uf2XTrMDdfwz7'
        b'0vvV6o0j2r5c+m1weIP0pHDOicKid2ImK5cWtJ318Q5MlAS4hQy0dz9+pGRa9hLfude/WvzCiLLNJWP/ZjX1RsmDtq/Tngg/yvht+5NfebtOSQNX8hCqIOGd6uF5ZI6g'
        b'aXkiODwEr1lg1Wc7ZKrCFng8h0zOnq5+CWAn3DXRFx5Fx03E87czPCsAOyZ6U7twVyqy+EgTYEMFW8eoCVwSegn6gar+5EFygadi/cDJhPgkryRrBo1xYrAHriDGqD3c'
        b'IYM1/iKGlwb22mAmyVLYykWMbvT2nmDF8BLA1lgGNhaAOirvkeRIIuqFo8exNglHNLLz5MPVIbPInBxYAl7WxCcVIgub+9o2ng+OFDqQr5083BPI6EgNREf4MqhJEiTP'
        b'gBeo+XkMnkAGHF1BGkhWkOBhcI60FjgBd4O9BIaCswvGs+Rme1c+PA4PwDVkXJg7GO5ELfqyTxZYWsIeYQuO8cHxGNhE1gHAOtCAuwxstUcY9hismjdHC4/NsZ+j5TE9'
        b'Yb0A1KphAx1j9ruCzThMQu1LYm+shoijrWziowJWo9rivGaBKgVuef8EhMk2oBFmFV4pwHusGY9BQoRN9oPTRiGt+/7PP14dnzabZ4w1Joaeds4M0aR1ENNAUUSWAdus'
        b'9oLIjnhoEIUFZMzprxOoFEU6IXbg1lmVaktUCp1QpdSU6oTYSNQJi0vQ1wJNqVpnRV5v64RZxcUqnUBZVKqzykGDHvqjxv4eWOqlRFuqE2TnqXWCYrVcJ0LmUqkCbRTK'
        b'SnQCZInprGSabKVSJ8hTlKFDUPa2Sg1HD9aJSrRZKmW2zpoSqDU6O02eMqc0Q6FWF6t1Dsjy0ygylJpi7JKqc9AWZefJlEUKeYaiLFtnk5GhUaDaZ2ToRNSFs30cpRfa'
        b'V/0Af/4OJ3dwcgMnf8cJXiVUX8fJVzj5HCdYeE99Cyf/wMk/cfIJTj7Fydc4+QYnn+HkS5x8j5NvcXITJ/dwosPJNZxcxcl9nPyAk9tGt89WP6g+iTUYVMl3T8U52E87'
        b'O89P55SRwX5mJ5un7uw2MoizC2S5CpaGLpMr5MmeYgIBsaouMn9ZVV0CEnW2qMXVpRpsMOtEquJsmUqjs0/FLqOFijjc2uqHXLt1IFvoxBGFxXKtShGJyRLkrYOQj8aw'
        b'jl0szI2ES/gvLsOS5Q=='
    ))))
