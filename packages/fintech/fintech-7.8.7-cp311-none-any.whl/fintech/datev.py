
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
        b'eJzsvQlck0feOP7k5D4k4RYMcgZIuG8vQJEbFU+0hUACRGPAHKi0WupFEA9U1OBR8ajiWdRq8WhrZ9q9ut0lblqz7HbX3e0e7Xa3tLW7ffvuu/ufmScJCUms2+3u/30/'
        b'n18Ik3nmer4z8535HjPznd9QNh+W+ffzHcg5TEmpOqqFqmNIGduoOqaMNcimnHykzLMMirrIsDyrvKUsJiXjnEX+i9ZUHZTaeyUThXOlbPv0Wxgo1E02qRQGJeXUUh7N'
        b'Qu5XmzznFi6et1Swtk2qVcgEbc0CTatMsGCjprVNKSiRKzWyplZBu6RpjaRFJvb0XNwqV1vSSmXNcqVMLWjWKps08jalWiBRSgVNColaLVN7atoETSqZRCMT0C+QSjQS'
        b'gWxDU6tE2SITNMsVMrXYs2mqTV0j0L8XbqAPkNNNdTO6md2sbnY3p5vb7dbt3u3R7dnt1e3d7dPt2+3X7d89pTugm9fN7w7sDuoO7g7pDu0O6w7vnnqY0oXrgnUBOned'
        b'm85Hx9b56Tx1PJ23zkMXqKN0LJ2/jq/j6Hx1obognZcuRMfVMXUMXZhuqm5KcwTqDvdNEUyqJ9y+iTdFelBM6tkI+1AUEmkfwqA2R2yOrKWiXcatpzawVlDrGaj5mdVN'
        b'tp0dhv55uAG4ZgyppYSe1Qp39LRPyaQwgqRy905RdGRQ2nj0AAfgHnAb9sKemsqFUAd31wjh7rJZ4MySBSIuFT+PDV+HR+B1IUMbjlJrq8EJdVkV3AN3VcFdDPBKHeVZ'
        b'xgTD8HimkKkNQinAqfKNFSXwcllyGYdisxngBNSDE1rcL+B4jm8FChfBHrgLnAdHqziUL9zJqgZ98HWUHb9guZoJeuHO5HYE0a4yjgwcpjzBdSZ4eUGNdjqKryoCgyjB'
        b'NW+gW79OW+0Or6/zXqdlUMFwLwvsAq+BfQjSKJSwLrwF9IK9KRWiRAwt3Iuf3Ch5eXgMG2yFJ5OaGDatFm5ptQvIORjWjVoOdTIbdTGFutYNoYEHQgAvhAA+qNP9UPdP'
        b'QcjBQ0gQiBAgGCFAKOr8cN3U5nDS+WjE9LhN6nwm6XyGQ+czHTqYsZlp7nynca47P9hJ50fQnZ8fzKW8qZEST0GD9wcZQRQJHEnHGNGl8aUakjeGhdCBbya5U/5UgoLV'
        b'0KD4wrOCDjyzik25Uwlz3ec0JKfXBVHnKYUnCt4ZH1r9ktcfYinqV/GfMW+mfeT2D0rhgSJ+EqhnDLtRgtRQMfu7qhmzttDBp6Wf+fX7MRLGqecCf7t8jlhNjVHaZBTR'
        b'5BGNerw3ZWFCAty5aF5KqQjuBOcXJ5RXwb3J4jJReRWDUvp5zISD8Kxdz3lZqrwT95yXuec4dr1G4X5r9rL2DPvf3jPbJveMm5Oe8a5W4aYlw4Y3FY7ULhItZVJMFsUH'
        b'B+BxeAic1vqjqCzfpNrl4C6TQi+Ohv0MbQAeJ+AG3Fq7iFnZSlGt1Dz4Mk87BQWrkjnwgDABkYkUKgUcAltJCV65lfCA2hM1m4gSgaNsLYZEAU9oa6sWwt0civkMI5Mx'
        b'dWOANg6FpzwDXsaDL6kCjZqeyoUJ4HxyKZoMAuB5LiWG5zlgC7zGI0Col1aD67AbbEOVmkHNgEfd5GtSUplqI4rjvHf/6A9mHn++5+SB6wfWhEaz4GrBji7xlYDco88z'
        b'nnpve9RfNnrzWMWiYlGTTxNrpWdT/DKfrT4LznYHt4bN92mK/2v64N9Wx+n3TP8p/2zYdzilzdN/XjnHU+3pdeGjxOy+4wt47wzGXTs98D0//u+vSOZqQ1ctEywOXhlf'
        b'G8Y7Ui1T5K8b2Z213WdJzs93xA35/LD1bEVXpVtjhya8fUQTapx6qHqp9+FyJvT+UfG64ALfn/zo0HD0+V9TR97Z+mffBX84tTMz7Wy7uOGNZr/OH7pltDdT1KV9pcI/'
        b'zRFyHkWiqnXAQ/BUBdydBHdXicqTy0KBnkMFwBEW7K6H2x7hGXjF7KfBfrg1qVwEdWWV1RzKC1xlwuNTwMAjTK3AyXmgNykoWSwsT8KTIZoI/WAXqw1cAWfJK+ANqAMv'
        b'eOGm16IJbGfKZrCFSU2Bt1ngsrTwUSguY2t+PeqnnXAv3MWi2HkMsA3NqlejGoQ+Y8wEoQp3/Dd01D7IEQi6Jj5fBc1oVrV1ypSI6BJyLkakWNYxa8xHJVNKZap6layp'
        b'TSXttH9k4rJaENp92UWNP8uggsL6Fuvj9q3qX6UreX9q7GCzYarIOFU0Tvn6zGPQ7j73PkZflokX0jfTJJjeV6JP21fWV2YKnNZXN8gZVBsCk4yBSeOU15R5DJMgbijw'
        b'pYgLEcPqkbkGYaFRWGgQFLrM4kGyRA+yBued9DzjOSndEGdo/Wh8jiEw1xiYO0652Sd+IEi/L0gfzhhhGQQzjIIZk1+iMQQmGwOTxymONV/xYPEQ52T5mfKTfmf8Jr+M'
        b'PdRq8zIWyRR7zveU71CHQZBtFGRbMvw2LHo0JmuEjf6W3PK662WIKTaEzTWGzR3lzzXxgg7n7s/Vlxh40UZe9Kh39Od4plHhqUboO8al+2DMrb5epVXW14951dc3KWQS'
        b'pbYdhXxDxPBFToMdZqjItINng0mdPxun1yPnS9z7zzAYDP449W04D32DdfKeNbvWdHmNMzkMvskrQJfTk7cr7yHbr6vi+aptVV1VJnc/kztP5/XlOIfi+NuHdtXQf2pM'
        b'kI57ZFDXfQsZLLvZ2spmN2KiwjlMyTCTjVhsKaOOhf7ZcqqOg365Umadm9RDRzUzpOxtHnXuxMfZ5l5Hh3GRzxORH4aO2cySuqEnL8I9stGTO3ryljIQC90q9BzjLiKN'
        b'Vk1678O/ozHTxLIBiG0hH5sxQAyasT2MC6ZI0ZiyIZ6+ZxJPv4lNKBvLgbKxHagXazPbTNmcxrmmbCwnlI1N8xx/8cZMA2ICOu4qWjMbKPmv0vYw1Wg6pRIVRUd/MKP9'
        b'veMnD+T1Mrj5K2J+9XFInOBE3gtTvvMS57x0y6dBqRkNjCzvt7s+Wga/OJO69HlN+vQ/VkqGJApZkYn1Mkt82OPXV+/J9DvfLBgIHm68fv6Ax7txJYO33mj44YAvJWvg'
        b'h50yCbn0bNuzYH7SBB94SpvEpfzAWVYnHGgks3VapBuidn3ghCUNi/JOZrmBw/PITNsAdoIbFeD2AthbiXhjIZdyBzuZG4QrSebIDngV08uKMnCZori5TMRdXgtFbPXZ'
        b'RyEoWhIH7oDeGsT2sikOPMaAp8Dr8Hb1wkeYV0tlcJNEDaJSwiy7w5eZYBs4BY4JOa5HIMcyNZOBN+ZeXy9XyjX19Z1+NAaJLQFk8tVS9OSrYVLJqZdmjgQbkwoN/gl9'
        b'7H5v/WoTP6S/4gE/9j4/dnC1gZ9m5KcNFxr4WX0MU+T0Y2uGpg+lDU0/1oYSe5kipqEfTxMvGA3BKXEo5+GK/RWDbAM/1siPHbV8x1kokqRQ8axTEXeMrZYpmsfYWHob'
        b'c+uQqdRI0FMF4gRB1nph7GlowHMLPaNgZt+hTitxShWZU8isomYyGFF4UnDtfFuzxecYoQ97iKjLvgWsJqazsdlpHZv0yGxmknHJdMJxsjyc8JCOIxWNPeZmlnlcOo1z'
        b'LQtYwbIbl1oxeoLb4F1wxwvuRni7BzHdcG8tuAMPl9L4vXAB4UNnw5PcKeAcPC8fnn2IpZ6L8t3YMHb0B5lozJ48kIZG7Q9CereV63+1agf/4ne/U70jMZu7Q7bL2/ti'
        b'qORU1a45MytTf8GM+cJ9tOdsvP75DB/qS4PXwEuNQjYZUyrJqgrrcILbZWREIZb38CMsvIGLU8EleB0MbkDc0V64VyxqJ1wQkwrbzAbb0yRk9FR1VuOR5eFjHVu3gQ7s'
        b'f8RHce5wQFFRI2JQ8GUwyOxgFK4AXUKmzTjCPWgZRIgytsg0co1sLRpHAVacs4aRoVRgHkpzEX8eotcce2aUl4i+74fFjsbljyw2xBUawoqMYUWj/CJTcHh/5+HN+zcP'
        b'Sg3BScbgpFH/JJsBwVFF47eylZK1ssnDgEOGgXUUiPAocAIR7mm1gh4ICKZiFoMRgtHdqfOtDoGDHknURd881v8V8uRiGCSip4Xz4Fa7QUAGwKHCSWMAbm+TH2iq5pAh'
        b'8OBnNYhwORkCDgPg+I51lXOeqkzdHL/Vp1RUnMpqyac+TvEc3VgtZBHCAa4hOWKgwp6oKDaAYxGP8OQHtoAXQDe8bhkB4G6I3SBYPYOUgvC7azFNYOC+iXFwHr4gZE2m'
        b'HSyC8xNIr3aC9Go7pM8zI331EyB9NCYrnvpMg79glHxtaQBBeRWefMY4HRKF1gHxJ8//WfaYbwWrlbInAVUI9adhNHftfFv4r8LisfOpn+A9yzr1Y/UD1cz+D07/DnjP'
        b'cYL3nGqiawngKLAabjHUiUTihaXlS6CuphaJ+auWIkG/FMn8Ygalga96cOeCnSQDuAwugkPgRW/H0TKJXIwUy5frv89Sy1GuZTHpR3+QTjQAtw5cPSAP5dE6gMa/B5Rw'
        b'c0slq7gfXN7Rm5nWkX479c0fvJduTNVck77x1tt4SC3f9yjt3dTFV9NSB//4532sjxp3fBo8nNrAON7akZ6e3XEmlZ3RfpZFCZ/j7/7bHiSWY/WiBCH9HhuRuUJqkZjh'
        b'xSTCi1W3zs4FukkjbjW4TWgOvB0H9Hi4LYc3ndCcnCJCt3zgSbAdDzc5ODFBdtzgbRLLBEflq+D5JDuODl4G57+Wo7OKUmNcbTuWrTt9zLhPP5LRuMk8GpezqJDpfZ2D'
        b'MUNsQ7DIGCzCLFch430sLM42hM0xhs0Z5c8xTRWMU8wp8xm02zcXkaXBzDMFo8Fi9H0/UjiaOOse35A4zxBZYowsGQ0pGUflpjz05/d7PvCPuu8fNRhj8I83+sePWr42'
        b'I9qNHtEx2LEfyjZVc6PM1MwiJ87Co9q+Zmtxwg7KQsqWPZaUfftEjR7UthpFe36ORTSKRBNsJmRYgzhpMP4ndLvOCBmrWj709ldsNZ4UDZ8EYsoUtT3q+D405F48IEL0'
        b'6VBaeuql5m2fXlgeGrI6tOuz9n2cSu/l99IFT/v8/lbqmxfepN59N/299Kijr3aFHv1F/QdhJYsL1gys0a8OWa1f2/Vx5JLB/16+ZnRV4A/vDTCoS2H8JekFiIHDYykJ'
        b'dqXSIwnsCrQOpulZhDMDQ3WNS2bZiT234W4mGSPweXAYjIBuNCx7Ec3aLeJS3KeZ0WsVdOyxcrgDjcLLdiJVaPxTCOGeQD+BEU4gsJGP3BDp0KgQhfOdICX4mYynNvN4'
        b'amVR4dP0QYPR6E96Zo1herpxerohNL2Pa4qOP5P/IDrjfnSGITrLGJ2Fx1IccfZV9M3Vx5pCph7zehAivB8iHIoxhKQYQ1L6Ck2CWKvGJzimb9PgUkNwsjE4edQ/2ZEm'
        b'uhw8hCLajJ15eOxMqgaW79TtlFnJ0oLGTgAeHa6db23YpOAqMKtVuNOEPlgOxexsff2YZ309vbaH/N719eu0EgUdQ1N/9yY05lvaVBvH3M2SoFoVS+a9ZrlMIVUTwY/w'
        b'vYQFIDMGqfrXTaE22iiMn51mjUotjn+T7mjL30NesA7PhrpSU3AocoLCdPNNgcG6knE21wf1rivHn+WTPE45cTxZPkLsc3A8uT4JOO9jHH+OD5q/n8wh2KPF1QNnl8PX'
        b'vMqr4J6Ucgbl7p2Qx2wAV8FFBx4Afz5vwDMZY5Iai1nHlrKkbCnnGLOOw6T6KSl3kEs5+Ujd7Fd+7Z/q3KTutZRHi9BjjDtPibi0jV/x58oa5Zo2lUyZUqGSSWnvh/4E'
        b'Yz7E89hXAUtlqk5ti7pdolU3tUoUMkEGisLwfuVdKdN0amSCEpVcrTnPJAj24XfQeP1iIICiKtqUmraCaoRQgoRCqUqmViN0Umo2tguWKDUylVLWulamFBbYPKhbZC3I'
        b'1UiUUqf5lBINvKtSiAULEDq2obxL21TKJ0nnrLA1MrlSJihUtkgaZcICu7iCCq2qs1HWKZM3tSq1ypaCeUtElRgo9LukViMqk1arxAWFStRgsoLFiNlVpBSukUjFgvkq'
        b'iRQVJVOoMQusIO9VqjvaVKjkTss7VJqCWo1KAk/ICha0qTXNkqZW4lHI5JpOSauioAalIK9DLa9Gv51am+yWh8b1GDqsxRWYAUFBYkGdVo1erLABXpDmMia9oEKmVHaK'
        b'BRVtKlR2exsqTdkpIe+Rmd8nE8yHdxUaeYugo03pENYoVxcslilkzSiuSIZk5DW43ARzkNASJ5gvQ7gDzzRr1LiWuEkdUwvmVwoL5omqJHKFbSwdIiwoo/FEYxtnCRMW'
        b'lEg22EagR2FBLZqwEJAy2whLmLCgSKJcY2ly1Eb40b7VcMgajMOiau1aVAAKqoRnsNp8DW41uvlRYFlRYTWOk8lUzWhaRN7aZWUli0XFbahvzI1PxoJc2YpwDZdjbvZS'
        b'ibZdI8LvQfNro9j8TrPfrt2dheO2t6tEukMl0h0rke6sEul0JdInKpFuW4l0J5VId1WJdBtg011UIt11JTIcKpHhWIkMZ5XIoCuRMVGJDNtKZDipRIarSmTYAJvhohIZ'
        b'riuR6VCJTMdKZDqrRCZdicyJSmTaViLTSSUyXVUi0wbYTBeVyHRdiSyHSmQ5ViLLWSWy6EpkTVQiy7YSWU4qkeWqElk2wGa5qESWXSUmBiIaTyq5rFlCz4/zVVp4orlN'
        b'tRZNzBVaPNUpSR3QbCzTomnE/NCuQhMymv2U6naVrKm1Hc3XShSO5mKNSqbBKVB8o0yiakQNhR7nyjFzJBPR5K5Qq8YEpRMxSAXL4JlWFWo3tZq8AM96NI1VyNfKNYIE'
        b'M+kVFtSh5sbpGlGksgWnK4FnFAp5C6JRGoFcKVgsQXTRJkMt6QMcs4As9doWNkHGRXUICjRhJODsdhHm/Cgq1jFDuusM6U4zZAiKVFoNinbMR+IzXReY6bTALNcZskiG'
        b'KglNl0mbI74E8SckTCPboLF60Exk9WbYJlVbk9EdUSRD5LjFJiC2oE6uRL2B+5+8B0d1oiBMetEsbfeYbv+Iph+JWoOonUrerMFY0yxpRfCjREqpBAGjbERoa+1xjQqe'
        b'aUFIVKaUyjvEghKaftg+pds9Zdg9Zdo9Zdk9Zds95dg95do95dm/PdX+0R6aNHtw0uzhSbMHKC3LCZsiSFhkblW1mdEQTjBGziLNvJKzKAv75CrOOpU5ia9x/jbMdzkL'
        b't2PFXNfhMfGuuLN/JnG66zfb8WlPkgxNlc6S2ZGAbAcSkO1IArKdkYBsmgRkT8zG2bYkINsJCch2RQKybab6bBckINs1HctxqESOYyVynFUih65EzkQlcmwrkeOkEjmu'
        b'KpFjA2yOi0rkuK5ErkMlch0rkeusErl0JXInKpFrW4lcJ5XIdVWJXBtgc11UItd1JfIcKpHnWIk8Z5XIoyuRN1GJPNtK5DmpRJ6rSuTZAJvnohJ5riuBJkgHWSHVibCQ'
        b'6lRaSDWLC6k2bEqqncCQ6kxiSHUpMqTaygaproSGVLv6mEEsUcnWStUb0SyzFs3b6jZFB+IkCmrnLSgUEWqlUatkzYgIKjHNcxqc7jw4w3lwpvPgLOfB2c6Dc5wH5zoP'
        b'znNRnVQ8oa9RwrvtzRqZWlCzoKbWzMBhYq5ulyF5mGYmJ4i5TaiFfNsEzZc1wruY0k9iG1rocDPXYHlKt3vKKFhgVq7YZHZQu6Q5BqU7BiExR4GFYokG86WCWi0qTrJW'
        b'hsioRKNVY7aWro1grUSpReRF0CKj0RSRQ2dqAKFNFjkm7nIpyfa1iZ2U74QoOS/bMSFRMU20jgAx3wIzy0uashnHmxuZ9qfb+LFMOKGp+opRUH3eXVWC9Y/zsVNKmRc8'
        b'VWXYKcc6To66XSHXqCqwJoxBqy6xHs2stqwiaktah4aXetRLJqsthVhtGaorHedSQSmmwIRxN3aI7ziFHBTmSQWF9y0ZZ6dOKWb8tZFB+fF3yvqKe1bvWv1pCyMjKOwR'
        b'hRxdCf6j9Yhk+VivhTfVeC9rTzI4z6bcs1lwkLl5Gtj2/5smcZvQY8yzsKmpTYtaQtky5luE0I2WeCTtMsWHgbQeEevQvwqbixBwLeJqsE5cQMtcaPjI0aSHkuANfmNs'
        b'zH2pFiPvF3dRwJK1NDPV1qqUCWrbFIqUUjQbKkUVnVi3M/E4Mb8WLKuoE9DZsA4Pz9xquVpLB+A422d6vM/HKkdatqBfVLREVNvUqoB3Ed4pED9k+1hQJFPIWqS4IrTX'
        b'rPCZ8KebZbMCS0sQWQMzozLztGIRGAU0Q2YWOycUZGaBk4gJWNREidHA1hCRxFwCeZ1CjhIQn1zZ3CYQCQpVGgso5pAyJc45KRAnS3eWLN0hWYazZBkOyTKdJct0SJbl'
        b'LFmWQ7JsZ8myHZLlOEuW45As11kyxN/U1C5OQwEVdMdgPltGAtMdAtGDoEqG5mqLFligFQsmtMAokMZli1pWLMCygkXip9W9E90oqEyqLCjRKteQE1QyVQuaHDvxhIbD'
        b'i5YIMvNoEt9sSYLV0c7CzXhDRzkpsKCOiCK44qq1EhxpRRFnMVZUcZUt/XHZnEfSKPSYbM4jaZR6TDbnkTSKPSab80ga5R6TzXkkjYKPyeY8kkbJx2RzHomz5T0um/NI'
        b'0t2pj+1v57Ek4+MRxTWmpD0WVVzEkoyPRRYXsSTjY9HFRSzJ+FiEcRFLMj4WZVzEkoyPRRoXsSTjY9HGRSzJ+FjEcRFLRvxjMQfF1mrg3aY1iHStR8RXQ5ji9TK5WlZQ'
        b'gkj8xOyHpkOJUiHBek31akmrCpXaIkMplDLMkE0oOs2UE094hdpmrJKzTnIWWoqi8Mw7QZAFCYXKTpoZx2uJaDKukmsQaZRJEQci0UyKnjQPO2aemMknx6kUiPcyswl2'
        b'MaVkZalZg7gSq0hHKImI8DtO5Q9zTc3UHJF+RGkw+95MGPe1mMBrZHLULBqrjroMcdkaebN8jcR29q8jIqhVd23LZtCCq80api2bVCKjpRqZvBFHVaJew4tyapqzcc2o'
        b'2eqlEdzozRKFdu0aWatFiU6IIOHiliEurlq13Dn7jDeHd9owjndx/KLJLHS0DQudYwoUOGWhQ6bM+Gu6LQOdE47553B7/nka5p+vwxcU6koZvFEN96QQPhruqnCjAhvZ'
        b'3tVwix0T7W1houOYiInm2zPRiG3m9nv1e0mZ/bx+HmanL3HOIh73opsluwf6k8boODofHa+ZJfXa5mG/gaiOjQ91S723UVKfS75n0TsuWvcq1nFJnB+K83eIcyNxU1Bc'
        b'gEOcO4njoTi+Q5wHiQtEcUEOcZ4kLhjFhTjEeZG4UBQX5hDnjevXzJSGb3Ov8zG3CW/Sn8elqWc9US5Pu5aJ1THNbcOWRji0ja+lffs9+xnNuI3diGspMfIskg0uekyU'
        b'KI3T0Ts58ZFff1Sqm3SaQ6l+0niUiqNzJ0eDA0gqwTaPOn8UNgXVIgrVYgp5M+/SdHthx3y82Ffn18yRRm9zn1RygHlTRcKY+1x80q64dulXKZ4Cm48lWEDPo/SZebsU'
        b'5zmqBXhg4DHwIZbHVE9jH97FTeQhofeHGJwPcet/iPcGTyRXtViSq/DeMlUDToLb+0N83vZDjMlCtzFPibQDTc2qerl0zKMJTZBKDfb6SugxWK9AHK6mdcy9SYvmDmXT'
        b'xjF3fIxDLlGYt/x4NcsRU1u/Fs1breTdY6x5SxbRe4pUeAtpkzs18cGvJxvgDlGWzba2h/vJuV8GQgK2zg01LH3ql9vsSfbsITTu8Zy0Z8+D7Nlzd9iz5+GwL899s4d5'
        b'z57TONs9e18cQA1p1wv4U0ZXW94pUxPTCNa+k5ONKU0ysUMWh4B8JMNJ1gommjzfbBQBzdNYnWe2umBue4lS41AC/iQUoelVY5nchWJBIc6PJuImAdmWLdC2CxA5yhFI'
        b'5S1yjdoRLjMY1t52DgUd7RwC66LV18CQ9XUw2KNZvqCS/GIQ5qdUWmLNgKmdw4KJNyabiOiKBYtbESFFo0kmUGsbFTJpC6rPE5VC7wiiJX5UkkCCikDPNPwCRRsi6iqx'
        b'oEwjWKtFcl+jzGkpEnPlG2Wa9TK8aC9IkMqaJVqFRkhsYuS67gvz8MoXFJt9gias9U2wrhXbaIuFrkqxDM18C7aqrZ2JTXC0qQQJ9M6jNfCuqlOmcFmQeVtfPhFZMXuH'
        b'iqFxxDxTJchaxIKstNRkQU5aqstibOaGfEEJfhCQB1xcs1yJRg2CUbBRJkGAJSpl6/HCdUe2OFOclih0bKqv3RvvTR9ZdPPzpwQNI1yqvaGS25pBafH+w3ZwCB6HvVXg'
        b'0gKoK4O7K1JgD/LV5IAjtaWVQtibXC0CO+HeyoWl4HJpdVVVWRWDgvvAoHcbODKNlGtM8qZCBFfcqAUNijU5syktPk4UMh++6qTY2lK4B/ZUImYC9NgXGuJGwW0bvamm'
        b'fFLoYLw75a95lks1NHhf5CwzG/TYCU/T22ctJ/hLxaLEclQ8uMKmsuuSV3HVanCOmB4gpbzV4EZ5r/Lionp7D7Cfpqu8Cp4BOxxgG16HwYM6VG5vMgZxl3CpTZXBLZUX'
        b'uAbPSuRbF7Yw1IOonICCy7v3FviCVO85f/pbLdf3u4zbUuq24E0P07PUm2PnK1J6Mt5MmBY1fZ5Bfeqv/Q8ecXd+0JLQ2+fhJRR8t8BfOWP3r34me7oWvPXB55ufXT6l'
        b'cNEXF+P3N77y559/dG6l3/tn1X98917D2rt//eSTvyUf+nn8c4HK2x2GrVf+ePsvO77/0p9futk2BqoKvP8x9U5HB/fT8LPL/7D/k7M7fRu38N783A3WZEx7u0fo/Qjb'
        b'/gC7liSA3gljISzKD25xi2U1a2aSwwFT4YvwIOitselsuOWpSgYVBreyO+HAs+TUPrMA6r1Qo4OeRmGV1nx6IBB0s91hF7z4CG/3zUKlD6CC4B5wBN616WUGFRTFxq33'
        b'MtlBDbfCM+uTRAmlIibFBTtawRGmCB7pfER4zsvwYC3oRdm7a2y6NgBcYcFeYTnZnj2tE1xLEgvhzmSK4sLXwQC4xMxIAs+TAtJmC1H20yHYdIC1I7lUQAcLvMqEXY8w'
        b'GjGeCsT1rZbCEzRji6E0IwJFpcLtXDHYBQYfYUIOTsJh9IBq1ZucKEYJXwQXUNm74d4knFig5vi4NdKgH2gtBL3gVGkNrXJGrxahF4PDLLgdnigjTcSGg9nk1RMMNTgL'
        b'XkdMdRgYYSPA980Ten6Ds+uYf5h8bp2cMp1iIcf2Z2d9zIYLOtyoKHy0yccULepjG/0FJl5QX0afuk+tz9/3XP9zBl68kRc/FHWflzTKS3o/LGY0ttQQVmYMKxvll5mm'
        b'J6GsfhNZ8vZt7t9s4MUZeXFDU+6bT1OhLPMNYaXGsNJRfqkpSngu8lSkISrNGJWGMvvSmTXWbLZvyjGE5RrDckf5uabpiYPiocYHUTn3o3IMUXnGqDxnmW3fWWIIm28M'
        b'mz/Kn/8wPgtXLcYUk4J/o0xR0SRzdCypscN5Lh967zreQK/C289V67CDj2Wp1NjBWKHSUI/b3o5tTDSYPza73F30yIc4yxBFH/v60nz2q8aNwWhi4H3t3577rVoXOO2R'
        b'R93yLXRj2R0wYVjITwAhP89Sq61RZPmDUS1kjHnVT3B6SNjFzU2EXQFppq/cZygkaxulklk2bWUJmoLSkdd3UfrFxghRF0V67iszFTaXa+HYEhB1l4ralIqNwvOMMZa0'
        b'remfALaVBtaz3soPOsKq6rbvUguYfJSEHCnFYB6rt0A5jYaSLtAJkP8EdC00dH719pzik4MYbN+SaRYYhY9lNb8htOaO96i38HNPDmeYXVM+bQEztEiillnZw28IVqsF'
        b'LAuD+ORgRaAkqn6cgIAT7ZKx/FcAc683M5xPDpcAd6u1uZ6yNFe0S4b1X+lP73obTvbJYYzGXTqBemIr6n0NK+wCVOvpsQ3IOcg0H2qzmCj433WkzevkT5lqvHL+yT/m'
        b'YnsDz/ecvLzFfODacqBt8Nouk+xiVy6xLFC2y92fTQmZjwQoUxBDhjiM1xCj6shigBHQR3gMuHsZfAWcTprEZ1h5jFh4zqW1ALd6PI/U13f621ApEkLYBnyyHBOncg8q'
        b'JBwR/MxjswzBicbgxKHaodphvjGt0CAqMoqKDMFFo/5FDmYBnBFM2ioAJpI0ypzBKOPw9jiM1Wso81mwMo//xDEwMun0eyRSF3xzWULPMTfzVEif9eKqNSqZTDPm3t6m'
        b'1mCRdIzdJNdsHHOj02wc43ZIiMbIqwkJxm1raU0SSyNpGeO0oQlC1eRlgy2+FmzB1T/Idm7cEaG1j/kAtrvOT8fUeWI01/nrWDoPnVuzL0F3L4TuvpPQ3Zugu5cDuns7'
        b'oLTXZm8zujuNs9MGvc9xog0qlErVSNzHMqtU1ognQPRtMu9KFsjI/o8nUAgRdQXRNUgErdoWmY0KBrW3Wt6owCYy8Zk6rE1RyzRiQQ2aFxzKwTPxWrwgLV/b3qbCmiNL'
        b'tiaJUtAow1kFUrlK1qRRbBQ0bsQZHAqRdEjkCgl+JZHe8Z52tRjXVI6XFtDsZC7SrAHBZTqUgYrWquXKFgKRtRhBIkGFxCdokRJzbVuxOtQRdof0CRqJqgW9Q2qZ7nF+'
        b'AV4sUWNtgnqdFrduo0rStEamUQvzn1xJR4+CfEGhHWcgWEm2hzzlKht+c76AnCtb+bWny1yWQg+6fEEt+RWsNO91dpneMjjzBXipB3UVUR6ttN3r7DIvHs75gmLkClbW'
        b'qDSu09EDHiWlPeQdyYKy2hpRRlp2tmAlXt5xmZueJfIFSwsXi8rmClaa90w8lbTS9uyc65dPTC5YRUY/CHBBtic2XGZH0xFqzFY0NNBwVTep5O0aM5OA8RQbNSJjq1Ch'
        b'bkP4K5M61e4hdMKpMbVWEMO1pLPFgrm0io8M0em1GsnatfhMvHK6S2UfGQwIsRAA7eahJZUT07kS1Kzr5YgrkG1APW4ecI7l4E91m0ZGDxMy+GWa1jYpmklatGsRoiFY'
        b'JGvQAESDRoZap0kmaEMcltNy6CrhQUN0l2q6mnK1DUhiQQma1CwTktNSbIcd1nQiVMeGgZsUqMK0TWC1zHnOBrNZ4LYmAjm9mjyjVaNpV+enpKxfv542UyiWylKkSoVs'
        b'Q9vaFFquSJG0t6fIUedvELdq1iqiUyxFpKSlpmakp6elzE3LTU3LzEzNzM3ITEvNysnIm9VQ/w30igHVZJ0QvLrQU10pLBeJq/Gh9yRwPhnrFXfF1HJaxeAlYrwzZGEn'
        b'3A1fy0DeNCotHDxP1HOvF5mNqJWkB4k3syltDgpsXQWfr6iszq6jeZeFUIeNUZaLFmFjHIsSsM2YZVCHfxBLA/aDlzzgwefAEXrL3y54rgFeh3uIegZxPOs4cIDpDbe0'
        b'azED0sCKgdfFcHdFGTb2gYrFVi6Z1DTwIjsKdsPbcGixFtv2g+fWLIDXK+CuqiWwr92+agugrhpl3FWxRApOtqPfmspyeJBNwZ1gixc8A06CfnKKmQUugq1eYmE5uAtO'
        b'eFIe5UzGc/CEdD6JdGuGvfA66BKVoQIYKO1hBugCB6OJHWBwMjjCC+pSxLAHvTMZnC9H1dIxKMF8Tim4xQbH3bWYkUqDL8+E11MSGRSzlAFvgqHsVfAwadbnN2F7uJR/'
        b'avNOKjNORGmJTc0zfpnz3NQ+8CC8Qb/VfRVzfiO4RkwKgxeL4GUc6eMjhvvgjUp4NQnuZ1HBG1kLngGX4qpIT+fOA7e8xCg3arcyeB5xoAhAFhUIb7H9EuFO+V9z+Gw1'
        b'QAljPihaO1rhCeZ4cx9KIzfNvnf8hbdWbtg+OBguvFLuNa99H0v3syu3P91/Njpi3R/mvJ3zP/Gh91u+YHIu5f72b95vH+HfWym6E5kv+PlXmuEzv0t55qrxO5/xL8X3'
        b'hz2K+HvH/Z8d1SR90jvwvkL53iuc9Es/S7j0avSaW+/86JV1MTuPBSz8ePHOgPik8uPpC38nnXur9v2PR36ojxv89cnN10vrNtcmum85oyrTzrvwTH/oo/27uUuXdp97'
        b'+OPdHV+sSo1ivsG4/xu3gS2pns96mu3roW66s2FCe/osRfSnsazmQnj5ETYQ4lEP9ldY+GyzHjG1jdYkJmVw4F4GfJGoB2fBHfAlrEHF6lO4Jc1Wg3oBdtG2wbbAC+Aa'
        b'VjbasPdTwWWaw18Cz9EGVIeXwX1J1aKysqoK+GpsMtwtZFBB8C47HR6A+2kDqmdBV01FckIpwnXU0eAiE/aDcxvlpUL/f8V4qlPdI3bszGZaDVR4SqTSeprn6+RZWfqJ'
        b'QDtVZKUnFSbQBw1yBjVnNhlCs4yhWX1cEy9Un2LEWr10kzitr0Q/28BPmlA45ux7tv9ZAy/GyIsZ1Bjj80cWGuJn3efNGuXNIkrA4nsthtgqQ1i1Max6lF9tmi7s4/at'
        b'3+dnEmYiz2aDf5xpVlEfdzQ43+BfYIpJRIEbDVhDmIB8Hft8TcI0SzpBDPJp9/kgiLCJjFxTgnhINcwYUl3C5lbzDPxYkyhjuHC4aLjoUh0KmWXgJ5qCQkeDhPpVfSyT'
        b'P7/f94G/8L6/cCh6SGXwTzf6pz/wz7vvnzcSZ/AvNPoXjlq+NmLTFFpswqw4vd36HHawqlB1HjvYorcKM+mqS9i5jJ0rLgQtmx7DndMw8RFMWOhRjWDxy1lfCbEEBikb'
        b'JaVZT+nx7esp/+36Syx6XfAopKg3KN9CX5bQY8xbivfGm3nbMR9aYrE8ciVryS+28igb8zDvSmqSjXlh/hJx9XjPMt0P1i5osu7gQB9/C/HEPXnQzZl4d5gY8kaiHF7k'
        b'ZxAz7B66KUjUw2baia3+Zn8i4Hk6EfC8iIDn6SDgeTkIcZ6bvcwCntM4q4DXggS8vW6PF/Ak1u1IAtos7hOIMfPw6UM6tQDxUgi/kISC+EOJ7S0ImIdMFrSo2rTtKBaJ'
        b'ThJH3qRtbaNcKbFwq4mIkU0kbBbNZWEFnPW4BQbQqkpyKAmrlv6fRPp/WSK1Hbr5uKPoEKvq+mskU7uxTuengywFOGXPV37NOQiXr6PnEvo95unDHEZLOMo2rAFVERlG'
        b'6VwyWd+GRQj5WonChQy08jEnQZBk6fwsiEuI8axHw9vY1rYGw4tDxIIqM3ZJyLOgrXE16nhBm3NxCiEIkohzs1PTzJpnjAhInMfFrZw4JeISCOukmy9YotZKFAoyMhDi'
        b'dLTJm6yjcaXNIZPHKgXMk7Z9N5CT7yttD6J8rdiOs08S3e2OO/wvkLyLZOtlLebNqv9P+v5fIH1nZKem5+amZmRkZmRlZGdnpTmVvvHn8SI514lILqC3+vwuiUML1tk/'
        b'CrjzdCGlxYK3D3wF7Kgoq4I7k8ssEsvCSUI10IUTufo58KpHpiSSvttmO9wFXsVSNTgHT5glayJXg2EOEdnhViG4WSEGF5TlVVgodFU6LbL3wl4PVNLLG7XFuPRe8DI4'
        b'ra6pqjEb4NwLTgAkm/csg30oz16oq1jS7okEU1Qmer5VuwocA0fAaQ8KXISHvKo3w0Etlop8fJeq4faOcri7rKqmAhvvTGVTIUUsJKxeg6+RJOA0HPBTJ1bBPQl4s0dH'
        b'urgMXE5gUNNaOBz2Aq0A12QfC+72Qg21Z5E73C2q9gbnkADOpAIyWEiy35+gTSCi3A0wgNpjFzgPt1t3IpUll4Ebi/DNQmmgl7MBvLaRtF4wGKhR01CVJWezhfhSEj48'
        b'zYJ3wIWppLN+Ndd8d9HSp+UdVSpK64ceOD55sD/fC3XtYmpxSbI2E8N/OwJcbM3ywo2EGnMffKW0EpWMpL4bWCXRCy6ip0q4pxQL5atC3eeDoRByHwrYCq9wwM4p8Dp6'
        b'KKPKwNFmopWBt4oK5/mZlTLgArxLrlSZEbIxD+yDB+ibVlbUKL78xz/+EVpkxqiSqVO2x3vT26vEz1kUDUWZryxppbRFuNA7cIs3bpTdZvVNafJSfPlSSvkShAmlcFdt'
        b'ghB18vHiZaXW25YQ+pCW4yp9nuJUaWk7i+D6dN/VtfBgRjmLYsBLFLwEhtdoZ+K4o+AU1wvuBn1gi6gaddCiCVxxd9I64Arcz6ZA9xKPFc9WaJNQCeXsaROqkIUJ8GCt'
        b'u63iA+7dyKJmB3J9N8EuWj9yCbzeUrxEXS6qqUrByFNdRus+hFDPAS838Yn6KRkOg5eTaMt1wgg/LuUFXmdii4/x5IYg1uqazDtcnQ/VLuH9bHnK+j30fjQkrJ+Gl6Kl'
        b'8LpZ0UXvk0NYBXtSaqoWJpgLtN2OBo+Dc96wzwfso2+mug70c5LEAd5lyYkMigv2MlPAXTFRE8ErBXCwgugBmCpGDtieC6+kCVnmNn4aDiWJNfDiRD4B6CM4EypiWHOt'
        b'hDty4b6naRXbgARcttQxCFy2VLKcITf9RsJRb0KC4mwJ8/KiimqY6v9FTs9P6o8ElQsVuSXvrhQoU5nGcvftO+f9VmEamNkIT11UjsTwzlX/pqFjefmj5r/97q/fmfbT'
        b'eMmbpRmpv8la9/t77v/V/KPEpJJpr//8jNvOnJd/tTGouTV1NOLvOafAvNcOVq1m/vDMnaHw/y6puuAxHvjrs3Wf+b27rWzLuwGX4i6ujivmr8gs4r/00c9/vs5weOqd'
        b'j0Jlqvqjp7r/fnLh5r+vlxnfBn8s/mlP/t2GFs+kszd7QzqP3i5nb3rkm/jJgW0nYXbLxy1IvsxN/WxF7PbKnyxblJx0I+v9txsW/27+Gxt+UTnwc63ys8GveFXFGUq3'
        b'eN/39jas/vUvZ/wSDPz4UuJPio4I637/3qI/jgz0nDyY67V+aOqsCwlZ8PD+ut99MAAuRVz+6cyUW78LOZw/7SP1g5tZs9+p97x4rKt3dtZA26Wgt1oL1shVoaaRrreE'
        b'vT/b+KdXCl6/+uWFt86/e+jGL1Xpzx7/6Pl7XwSnbA/a/MtA+In2l/HPny7IWMD84NDQd6fd9dz86LvxQh/aZPA6uBNuQXhiv/UvltUMRmaSrW1wdzm4ELRisvbKRneF'
        b'eFlSFty1CGy16K4Sw+ZMqK6mw0O0we+DqzTgFDhSYbNpz28pS7GBIlv+YoVhSYnmLXvwaprHCiZ4EVyaTe9PfBHq4atJ4lVgB6YRyRgP9zBFYD984RFGxE3gBuyuqEzk'
        b'UsynGPClDTlh6bQh1t5ZqeCsElysrEpGE2gFA1xDVOoqAScQDkN809PuUjRR0zv1uM8y48GhGXTNb6K545DNpr69M6fabemDr8Fr9GL6i/DGCtDrPtX5Wjoq5CrRyYUk'
        b'gC41Hp6iuqmY3pHGngL7WGAYnFTT2x4vSgOsKrmwQKyU2wjPMISB37ZGzrWqDs8HhI/o6nKmr/PF6p4Jqb4z2E4PNBFB9HY3mbTebrMXFRajDxucN5R5aaYhNM8Ymof1'
        b'dhYV3QxDcIIxOMHAExp5wqG5xuTZ96IMycX3ecWjvGKipCu8V2mIXWAIW2gMWzjKX2iaLjYr6axlzDQEC43BQgMv0chLHFpsFM25l2YQzb3PmzvKm0vKKLr3lCF2kSGs'
        b'1hhWO8qvNc0ow1q9XIN/nikBq/A2GfxjbZR+8UlnNiH/swb/GBMvoi9fLx0sNvASjLwEbG06xRSeoJ85xDeEi43hYmJbGgfPY9C7Ekei0Z/0lvCu0BBrc2NRfJK1xFB9'
        b'4f78vnxTTn5fyWh4hoGfOcrPfDjxZIoQ6GsHgwZWHlv5ICLlfkTKMMsQkWmMyOzzRJXWJ47yYtB3iIf+6h6IZt4XzRxpojdW3Es3ikoMwvlG4fzvRd0XVowKKwhQld/r'
        b'NMSuMITVGcPqRvl17+cWjMwfmX+v5HtL36gxzFhsnLHYkLvEmLsEt0qmwT+LaDEZU2aYsgowUGkGfvrDqNgzoX2+Jl5wf/4g2yhIu89LG+WlmWIzhiWG2Jy+alNwGDav'
        b'HSkeZr/sMTJrNKi8j4XBjTGGJdKm802R042R4iG1MTKjbz5KjjW0g3nGcJEhWGwMFg/H3g/OGQ3OeT8yfjSh0hBZZYysGg2pehgcrm8ZbEE57xPr3aakFL3boJshJGE0'
        b'JMEUGjHoNsQ543s/VDwaKjYJRSiOM+D75cOE5OHF9xpHI8vQF70tOaNvrpEfM1hr4AtN/sF6D6P/dLPCNc7gn2b0Txu1fG0UrDxawXoLO7excwc7+HSd6lXsvEZZFKxP'
        b'qFudPOLwqyZrWq3K1h8jx+Ugq8MK1x9RdgpXNNzWeTIYcqIP/c+636ru9aJHIYN6g+Fb6MdqspjfwB/rhYf7KXs96WFK56bz0LHJlYdMnTe5acpHxzBffMhhUj2TDjtt'
        b'4hKdKMdBJ8p10HtyNnPNOlGnca73eDkTwHxpAQxUY57+D6UsqqGyDjH0i0lo+FN4vbOr0ndOg2L/Rh6lxde5bEqDL6jB7jxwyH0di2L5MnKnt2gxlZrlCe/Ugt2LO5EA'
        b'tntJ1UJ4YwG8scQnOzWVoiKCWeB5eBoc1pJVqu2gL64W7l6clQp3ZiK5hwcH3Ncx4KAS7qIX//TgXCEuCxcEtosYFCeRAY7UeRJWr7ME6sF1LlUJz5C7Dl8EAwQycN6r'
        b'AZ6GL86Fp9FkH4eJ3AGyfAnvSsDxCnFqZnrWU3Ank+JuZoAXxCiSiIsj4DB8Pakc7uuwvyEQsdUj8ukBN9jqKITbe+acOl57RwlTvc/EVGz+zs2xvVeLu/5S/xXnTz/f'
        b'XUoFlz6/5/lHDOZtqfvtzs/2n0j+yXs7f1seubrLv/pu9N5rGvHsN5pZ217b9+tf9zF8b74ceK3glZaf7ON113z56vWqHx/bMkWVB/eFr2vN+mHott95pxapV/61ceyZ'
        b'/zmflFW8LvnKzpkNqsY3y+J8o368JOV0aOA7Z17xfmdFa8i10YHBqd//n7eqHp7mwXl9P372vet/9nrdL/Gd333+5y8X/s/l8l2f7Xh5w8+evnGzZ0Plg5n5m/4++9U/'
        b'vRax5Ol5X81+PenzpfN+WPW3Z4s+Zcf9dOu+Ol/t96Zt/OUfpO9Eb9UHXT/p8acUZXH4lTsfN16cv+FWzuq35Bff7dy91+2HiM359RWfp9pPMSv+ETir+LX/Zt7/69o4'
        b'vZcw4BGeZeDrXrXgbDC5QdSNYoJTjCWZQE+inimHFxH7A3r9rRwQvNxKzkisAsczMf8zwfyAW+vj2eX0dRA9qwoZjbbsjx3z47PCvMxYjuRsO+4RDDxNGMhb8ARhs0qk'
        b'8FRFdTIS4/amgAtsqtTLF7zGqgc6P8Lx1KWB12FvxWovcgskO5KBOUR4mLCU4CrYB+4kVSDB6o791WTw4Ap66fWcF0Ijm2skF2bTF0m+horAAKrhCWZF5TowYHNKiUEh'
        b'kYQdHo/4QLzouglJPxV2J44YVAAYEq9mgUubwXmygpuzLriiErwGrrhkg0PKCEB88IoUnz2yOVbCne4XyXoa3taS5sisgkdtGWBwaR3mgTlmHhl2rYSvmDlAODSDXpfd'
        b'CLpBL81CD8DL4BS+9lIqmrj48irYM4X0KLyYVmm53qNoiflOgqfgDZqHvpoKr2JxDe6pKQMvgN1IWAd9zDY4uFEY8G9kKPHmYLNqyoGbdKun70y03c1JhxD+8V0z/7jc'
        b'hwqedlixX7FP2a/EHAXmx1oGJcdWDyUaeFlGXha+snKaKVxwLB/xYlOjjlX0zTOFRfYV9xU/DI88losDpx0rMweaeCH6TGN48n1e8igv2RQ+bTBqACUZZwrCAkz8sHEW'
        b'+n3ID+mvGucg3ziXCpyqL+wvN/Ljx91wgLs5oL9m3AM/e1oTxI174QBvKjCkr1jPOuF9xHs0NtsQkmMMyTHwc4383HEfnMCXCgwd98M+f+ybgn0B2MfDPj72BWJfEPKh'
        b'twRjfwj2V4+HYn8Y/QLPQSlml2eOxs4yhMwy8Gcb+bPHw3GCqSgxhjcCP0Si1KP8PH2xvniQQ67Z3GAQ5BoFuYapecapeePTcCIBSZRDErHOeZ/yHlpO38VpmJpjnJoz'
        b'HoUTTUeJxqOxLwZDUzUei/1xGJoyfeF4PH5KsDwJ8VOi5SkJPyWTlwj1c49VjYtwgBhXNQX7UrEvDfvSsS8D+zKxLwv7srEvB/tysS8P+/KxrwD7ZmDfTOybhX2zsY9C'
        b'Th93vIhBhYb3cR76Bx723u+tf0r/1FC2ISLdGJFu8M8w+meM+mdY4mpPLD+yfLBlSHJmtTEuxxCRa4zA0oHRP2/UP+9hZCzmhsXE6Ssx8UMPV+6vHOShv6Unw8+EG/gi'
        b'I180Sr6m4IjDz+x/ZjCLlkkeBKfeD04dDhnJMwTPMwbPG/WfZ8Ne+tLs5WUyHOhVT/UYR62RqDRjLDQU/jle0tfCS05iI/F18I6D7DLmH49Z+Ud8/YwPg5GMubl/3fnW'
        b'9lhjtdhJjxzqFd9CDut/3a7+FiHzq986KOFpOx4ay3l382KmwrzGoJJptColiVsrkOC1cpsliydaZxaskW1Uo3LaVTI1PidEr4WYF3fU1gVu88KIs/XhyWvfCnpFCYPT'
        b'uBEB/jV7/dyd8rVaIXoKzALXQS88BPaCHnAV7gfXloFr+HKOhUDHoUJAFwteAceeKdAS/TI4UuwND3DCwG6KElPi+b5ElwpPwK58NbzDALvd14HeZSJ4qEIsxleD97DA'
        b'eXC8hfDK7BlEK54Q6tPgfYUVTBFGF5yAZ1PVdD43CuyBfWzwIgPxmwdg3xijnnCtG4rB8SQxUWiuSSYqTel0LSaS8HYE3IqZYMR57MSMsJkLroIvk4xPq+ZgEgouwV6i'
        b'9cwFh0REu8qC27m1dAYm2I1ocu7UDrCdVrzejYRX4QECP6uQEQwHn4F3BfJlo+FMNRYoN9145+C+q54g1X/HJ6qy1V94PBuofeSzSlvgqb2/ROy3wD9nnX/UVun3f8yr'
        b'OOJZVci8vzX6+9s/+X30rYtuLz8cvLgntX9+wuLSiM/lXt3vPs3I1Vy4/vRB95KlW54PmA9/OOXA6Ft/uXPls8W/Zs/b3h+ivtA1Gnf5gfYzI29mTX3Nn3a1vvf2s7/p'
        b'e4f/efy1QPiu/mHVvuPbPwhc90HAkn+8+LvX+SlPv7fvo+fiCtyzTVv0Ob9Iff37KxrctJ8zuvpTo/7rv4RcwmQ1wv4Uuw1p9VGWEyfBgD7PCw4gHuY1641HQS34zqPZ'
        b'InJXJbxVCRATVyUKYaK2G2IgTktPdqhNqYSI8Xk2MwUzS2UiJuUlY8LBVNBPLgiMDoM3QS/YDwed691SN9Ms4q4OcMSGRWyEr9OXjXfA80L3J+Zi3K1cjJV3kajr8bC1'
        b'mVbNIYR3CTTvWVvkRwgQ4iJihWeqH8Tk3o/JNcTkG2Py8c3XhQza3VeJyHmwaVrUiY4jHaNx2SOskVrDtELjtMK+UtO0ZESwp+UgX1ziOcUpxXDGiJshbo4xbk7fPH3C'
        b'vpq+GlK6MSbzQUz+/Zh8Q8wMY8wMzBIVM2jXXHxYhF5yLI5wRSFhJ7hHuKPTUoZ5w02GkHxjSP4o+ZpCpg26GUMSHoSk3Q9JG04whBQYQwpGQwpwBOeY74OQlPshKcNc'
        b'mqkZJd9xN7YgqA/bD4rPGJSeQQCOxhWh70g8/WsB82Hw1D7vb3Tk53N7+mVu6A/sjvzM8/uP3Pz0InrfecYYu12iabW7DdEq6m/B1Ihjvg0RW7lx07mTC3G51hsRJ2kR'
        b'/j0X4v6KxXCyO2uCNGEqoZZ0YJ9CYUukntwcC26EfEFZsyAR+xIFiK1Q0/sAMPmRbcCms/CyeKK4U96emExeZKaDKuer6mp8NYHUupYvUTW1yjtkYkEN3nqwXq6WWWkd'
        b'KYNUgCSXCJrbFIip+RrC5eaEcLnThCu31C2pFE1gC0qR4FZeVQnOLy4Fl6EOXgNHk8VIlCuFO9zaxeAouUUY7CkXV6AJr7xKDHuQaLsYJexNWYgkN3Ab3BAlYHOyFfCm'
        b'GzgE9oBuWsVydj54CR4AF8kiRxDcz1IwwJZIcJFeadVtFCYh8OBh1gZqQwqgKc4KoH86qYZJwRvwPGMRBY+A4Vx5TGUER43HRE3d6eMLiX2JGwcezf+vysrhNzghI4yc'
        b'hq7yYdkcb+8udvHt4XmN8y4N3P5gf8iZoBfnrt5+2vvmidmf/NeOmimzCr/7TMI7gg2V8Zy31h4s8P3RGzlJhnd+Mfrh91Zqj31k0s1uvn7ipxG8ru96fnXzM9VHa0Dz'
        b'sZ5nQ76/pkAU+ocF8Yv+MCh47eavj51m8nJ+vOJex8uSbS15y1oD6rc37gzedvXSLsHPv7vtz5l/nd83rEk5/tWFj1af2KE5rAyPKVpz9uJ+4fmgvIIv/naAr9749r0v'
        b'ft/nFVv5y2WXN2yq+a+N2li/D9nN7QHBHb8NXeUfdTpBeHdz0uGPnw76ZenPsq8IacUBfIEN+kl3kd0Hl9g5DHBlSTstJp+EFzZggR+L4mUcSj7HHfYyN0F9BX0hul6z'
        b'EV6HL6/HJirgMXAihUl5gHNMcLo4gShNwFYl3BcTQkroSWZS3Grm1FXtJK8gnYkK7UkWl8GeVWAbivSCw0x4F3ELV2gxuweMaCqSwZ4aRAnB8Eoxg/Kaw4T6KEQJiYS/'
        b'G17XgENkI0NPSg22b7GZmQivwKs0bKe1KsxhCOHpNDHcS6rnl8pqgS+at23DU7CHBQdhl931gVLwCv32Q2DkmaQUhF+qpWUisZCJaN0JFmqfV+bTLdMDdAj9bsE+ovJI'
        b'qeZQ3BnMYNhfThp1zmx4pwKjPEH3cj8PPhOcpOjrpkFPcOCCeVhhZG6UImYIvMAliocleENEL9xJ6ySiwmitxDEZiQQnvcGBmJUEKtQZXDDETAZ62Cf0+qYqBS/Kbo2K'
        b'psdsPBN0+lhpBH4klPiamRKX+1P8oP6cw7P2zxqMoa1WYGku7/2wqNHpNoYkeIEo0cz9Mwf5tM0Ikmgo/aX8C/nDUkNSgTGpwGm+kKlY3h/wPebbxzHxgg/n78/fN6N/'
        b'xgNewn1ewlCQgZdq5KWOU55TkkxhUfr4wZgh1tAqQ1i+MSy/r9gUl3Ruzak1J9eeWYsKD0wjzoCnnq2XmkLCccGDi4cyDSGpxpDUUfI18YMPl+0v21fRX9FH/h6GRxzL'
        b'OTHryKyhGEN4ijE8BZcRb0KU3v2I+yAfA6b3tXsPMzCJOOb3RETpFw9OPxN/LvlU8pBmeLFher5xev7IXENEoTGiEJUWmnRvkWlq5InSI6WDiweqj1Xrq8dZKJREEedT'
        b'7Dyi7MKcOUjadBo8zrLARPRGb8UElXA53+GySzw9vuPDQC7NOHjQjMMXLriHyfiCJUirSEwzFO4MfBOrHbL8A3MTXZTlJtZn/J7sJtZ/00XjAx4p1Eu+M1lCsxU7fNWl'
        b'jWk4RLPMHyGH/mGif94kA+z4sLa0ram+ntgVGXNvV7W1y1SajU9iuQQfMyZ7/ckaFNEgEDaMNJ2Q/x9ZjMYEcPI69EQfSpHTabUP+BucoZJlZ+9ynM308UfohBx3yjdQ'
        b't2yQNaS+VzC6YpUpMmoob7ToaYS/vg0MhLbIfUTch/NKTAsXjbOi8bWXj3M+5UxkGmfj0HIGFTZdH2LyF436i0z87HEOMyz3Uwo5j7CjK0d8emiU3t3kj+9CNfGzUILQ'
        b'HJQgNOcRdnRlKEFknH65iSxCmvizUYLIQgQedh8RV1eN0oQI+jaY/JNG/ZNM/BSUJiQNJQlJe4QdYtvTNkEeTlCAExTgBAUkQfC0vlaTf+KofyKdIBgnCMYJggt081GC'
        b'8Gh9gslfPOovpsEIJ2CEEzCQq6sYd2f4YPnisS6XtLq+dlA9nHGP970MU4RgiDcSfS/je1Lc8otJyy8mjbiY8XDhEtPyVeMskU8Ryv+kLu4GSwnjbBL+NIPu7Ojh2nux'
        b'33O7N80UHqnX6BOHWQiG2tGlK0YlMvz6FvL6FpK5BQNbj8+RsGoYPunj1Dd3MUTWQtkkvJGZ5VOCAP6XXSUj1CdinHLlZNPtHT3qE2nwiTT6RI4zg3zQhPq1zqcsynea'
        b'Y/qJmxJmzwU31WXJZSK1ry+LWgiHfCKY8CS8Aq6RTZEcMAzOeoEhDWa5vPCmvQX54BW8X29qOjua4e383nhyxTTDem+8RXP3n7kzvvVJ7HG4VWsxIWpLBmfxVbpwL+iN'
        b'oqLgSAbN0G8B+toKMRhOhefgrSxsvOsmY90ceJnEwv3L6pKal5RPWuIcDqfXQJ+HryAWsyyZbAU6h4pkU+6gl1mO5Ihtcp+QWUz1UyjZ/vFBbATk5IF1DFb2sLduGdz4'
        b'1C7hLq+Qq+dZr9z8qGX6pedCF3yyeuTv4pJBcbPi9iL9Iv1hxjsr39l26hDnYl2Qd23ozpH80NqQ/NC6gZjQvir35oeVblTl/wSajt0Rcuh1o7PgppaYS2uFx7HFNGwt'
        b'LR3cplnKi3CrP1nTOm9h8Ah7txL2EYbULRqcSBKTjcF7gM66NUvvQxf9EmOdedFJM7fMvOQUA0/R3Ogr8CI8hrcb76kBfeA8jn+KKdOCl1xaH/FuV8mQ6Cmrx1vvO+2e'
        b'CLOHTdBg6j1nCsUPsbBgurkPeUGHc/fn6ueeKD9SPlB5rJLebKSbixm1gv0F+vVDHgZeupGXPhG0gd7ugwL8AvF0FmsKDtfP1y/Vz+/f1MdGqXQVtrqMMTYGYoxLG1ma'
        b'xJbQ+gzMgtCki4fZDzvooxD4agVl4T6e82cwwjBX4dT5Vq+xthsD/ubfzx9iI81eNkaa07FdETRAmds8sLlmGVvK2kYRM832Jow5JI6L4twc4rgkzh3FeTjEuZE4TxTn'
        b'5RDnTuJo086T4zxInC+K83OI80QwuyGY/be513lJM3SMZoY0AMHvbQ7nYTPL0kwSHojCfbFfx9V56Dyb2dIgFOInzUIhbJQ2BBs27vfsZ/azmln97H4O/pPym5koDP+y'
        b'rL90KO2y6RQ2LnuyXxp6zE9OScP6OQcY0vB+T+ROtZSF/BF0WuSLtPqmWX0CaRRyp1ufo62+GKsv1uqLs/rirb4Eq09o9SVafUkWn20dpMnHmC8ypKJjTGzeWRYgmyIV'
        b'h1pRaJBHOfnYT8X2xqDNZaT8K2UQaPhmC8i0/RvPZjdpKurhQGLK2o30KkeahkKCpHxioSp7zKMe8Y+SErlCRiyC2m01sir0dBS9vGSz1QjbWmajd1A6plmthzcYuf3b'
        b'Nxg5EC0W5Ui0POkNRi81k/341M3KBu/vy7zo/fiF+bupEAZVumRVgzggYTMd+K5qE+NLJpVwJFOycqfPPIoouKaVT7czo2qnZUeEAK+uHAFHalvc/X3gHVLOy/HR1FyK'
        b'St3o11B0fvVm6vcWKMlEKc+M5jLUWDsq8TMc/UE2ImpXD8S+wODqQ/IHClYcpm1b9TB+G7rwg9AFvz335R1EtBaFXH/j48ZIwVHhUc6b4gDOtYHrA28o/h6wdCTWW5g8'
        b'FJeZ1rFFIdnxs+/1Iwoy9oMYjweMftnzf+R+unzhBkV7ZHjfd31/f/Xc1me/+/yC8B/eG2BQb5+Zepq6LfQwbxCm1KC3BvE14WUiFuW+mKkBB+BBmnT1boA3QC94iWwe'
        b'boCD3HjmlHrwGtmbElgJL5DdzvCldHtbp2C7mGwgxqY6j5kNbMULJjVcbCinFdH842QlA/EEh1eh1Ii2YnsT+gQRnRKlC57KntEJTpGNKmvgmRICK7i2sAzsJjtyduEd'
        b'xEdZ4CQ/h1j/gidrwIskUSPoJYmqwCUKpTnIAqfhgTn0Vu2BJWAE9KZgtWUfwMcbGJQ73MkE2xAn8whrQuvgcDHoXY+ahfBzJYiBAbvB3hrEAPTUwD1iLpVXwQWH1qYJ'
        b'uV8jwWGsdLA4GmAddPYmR7GtPEz8Vk2hpsX0sfu96F2w/IEVx1agR89xT0oQrVcPzjBMSzVOS+3zNvGmDUbd50WP8qKHvIdV9xPyRhPyRhTfa7o/a+HorIVk32uBIWyG'
        b'MWzGKH+GKTYNm/OcbpqeNFQ8tGio+IyYGCeNiiXGPs0/kQLy5qiYQQ62etqH/mzIPK15GOOQo11jbHwyeMx7Ykemsm3MQ65s12rI/R7OFjZoXYR5hf7xbZKCWYKtlM3y'
        b'/MopDEYu5gCe2PlWV+GPeaRT13wLqW9gz5NTj5vKlf0/m8pbDAAWMm2NFNZ1me3/TZ244MLB4p9Y1YOS/POw+dTbduA/AeNcpp19zBQLkJE2QDpa8BT/8xB61luR6p8A'
        b'bz4CT7XbMvt+FVFmKcNyqPYbAtViMYmJB0H9WrlL05NOYCrHME3YxAzC2htBs6pt7b/YQhZgJBv+CWCq7IHhE2DwYe1/qV249Zo2jUTxT8CxwA7XV1rQKHQxLsdy8tsl'
        b'UP8bdsFsexK2hEOzJVUeLPc0FvY1KH7h70NzIKsLuXPELER2BQ3er6zIoOTsL/uZ6mwU896qh7QAjO1fLgqJ/dXHjWf532ngxu2o5ge+HRIasvQXsgzwbsYSxvcbuD/K'
        b'pOap3YukHkLGI2yJEuo3RtsQsklULBHspgnZRtDtSuKkrU1OsZ2dJ4xdplE0wZIGUCFT+zcNLjQGkzWFCFP4VH0afbwh85j5bMpQoSEYKwa/uc1LRyhqmbYr4E0B/7EV'
        b'8A//gT7/V5U6ZkT0n8JG8u5wEIfqUpjcBqrJ7rn/3nS8iRT74VeMX3TJX37bn03QUF16fgIN80NjfvUxZ5f38jmeTZ4/SY/j7ni3sn1mwldr56wO2bK9LjQ3g9o5z73F'
        b'530h8xE+SgoGwdkIMx7Ww+1OUJHGw5ngMNGpxMBrEXh9MFEkZlDwFniVC7YwM8DdBS71In715IS/vFNW36hoa1rTGWqDK/ZRBHNTzJjbHkAlJJ/ZNLzEGF/wIL7wfnzh'
        b'veh76w3xNcb4Gsz+6GUG/5hR8nXA2zEOOcT+NaqOYqzqcA3Ncnu9x1qEwvjckXPn29V7TJ5EsUDw+bOURdY7TF+ARDWz/oP46zCROtuvYL6s46uavzA+ZlEJ/qEbnntH'
        b'pqXIQQ0/BjwKLsIj61CNOqlOcAh0kXB4JxfuBRfFYDtq8GeoZ8CtUHJfhiiOxkfbM+qLE6pFDCoT9HDhZXjDF3SDW+SA97Iq+oB3u7K58tHMToqcWL63sIb5JpfaMFy2'
        b'NvnDkLqV/01p8zHKb0UyxoDlCg18ankO3G09uGxGe7vbM07CAU94ZFbThM4Z3ASvSSwq0gz2UqinNaQty+RNBZEcNV6d4h386ugPZqBxadge9ZcSUbFPcVqTXxKvOL7W'
        b'B6aXoIE5x5sh3PXTZMHt5bd3SBis7D6w7cLp5S/viNqedzT0TfH4W79OkZQs+v6WC9d6pkib4tVBvFWcizGrsi7UKZQXi1T1+/zeTM58cF2WUfj+G3s+8O3QrNekpzS8'
        b'8btXZHPuhv2oSTqn44/MpZdOvvH86uwLL/Df8zzrGbdt2vOSH+x4l1+deeKz9NSYjPiMn1I/nZlTG7IlNHcltbpM/Mx0o9CNqEDrwdXiCo90vOJvu9wPhheR7QBLveD/'
        b'V92XADR1bH/fbOwgS5DIGhCBQMK+i8i+hU0Wd2VLkFQ2CeBed0XcQFyioEZFjYqKO+52xr7a9r02oelfHq2t3dvX91p8tctr+16/mbkJBARr3+v7f98ncZJ779y5586c'
        b'mTlz5pzfuYyXmVHpIyJqVIB2slJ7YSZcN+oE5wG3GgwslVlkpWkKtgaYM+FtX91qdLBMN3CRDc/5oMUtGa42GsHTYIsdbM/BhRLOAF0ZYJt+vDKiAsEpI+cUsJF23bWB'
        b'1/Ruq6a1Op+FzQVEfWwPr6CLOrcDThTYq/M62A/3CNijLhlxVxwMiICkqcV1snrpMmuDEYScIcMYUx+kwpZyccd761NJ0pLU5+SGt7/d+3h83TTcunTXUmXIzlUtq1T1'
        b'51aeWtmTrwmI1wbEt6y6K7lfBhbeXfjQ1UctmKxxjdG6xqh5MYPTt8pW6yREc7fWQdTNQn9J500vmWoconoSex2mqh2m4t2lEEX9vqiOKBWn10mkdhI99PBXB2RrPHK0'
        b'Hjlq55w+nvMDnrCXJ9Tw/LU8fzXPH53psKTPqfI1vCAtL0jNC+rDXgdKDzV3EvpouZNU3HNOp5y6Z2oEsVpBrIYbS1/RkHTAXv+6BiOzET0ys0vqFshHlSuM9KOzbnjO'
        b'xsPzU5U7F4/KiwZH5Qbb/93N7z2mQqrLKpqVXcYebSonBnYMvT6OaOPwWM0sZ5ORmj2KgR2HjNTsp0ZqzlOjMftFjm6kHvWaoeH38JF6NPhT42x68O0AV21BG4tKgucp'
        b'N8otDO4i6kaCpTEb3pnux6B4MgoN4dPgGWL2BRUicBqcZlPwHDyMB3JjeEj2nsd1hjwOXR2wKmt/rY4VrNsWagF9r777avfWfWtKwkIyu7Zca7umEGwQKNw3XGuThee+'
        b'XPkH7p5rwpcsOkRU86cWtrdZSDrGGiVXcKQUbLFwDcAYJwB1bOI6xKCcKtigyWPFM/rnaoP+SRB0hrEQOUP6JyYWM1CuHTXB5QHPp5fnoxrfbd9jpOFN1fKmtnD6HJyx'
        b'wOza5+SiCB5goV+PJnopQ1Qc/Id9ia39DbjbeMhZog4LZXXYynak/GFM0RqWQQmkYCSLE/pkmMWXUDrtCoYptGMwsLHPryW/mxBiiugaxuCDcz1ROLMNGNwYsThWNpsS'
        b'Njf+X2Tz5xSoaXbG1e0ZDteCM8tAG3o7F8olykKmPBDGJJFIu4+91P5aLGLaM2sEG4IUazYftrv/lWTWH+7d7XZsclcqnHze6H31ylYbn9dM7P5W2FTKag5mFIYcOfVV'
        b'6ZeSA3/qezW8PWiDzF+O5kcjatYsG49zy/Vs8Ry2JMbUoC0JzbnmZN9Nx772BuwxdJrwcL6Oh+faUdwJLVMIp/Y5uLcsU05S2dHTAmZh7z5nN+xgtS+jI6MluY/nqbBQ'
        b'FqpSNLwQLS8EMfokH2W+ahL+UzsEqq0DDdja7DnYeuTrmA1x+aBydQZm9NHfpAZz+yYDbp/znNz+32J+H0TrF9iCZ1gPGBxD11OGWy5kiDfWDfKc/5uD/GjiuJ778abB'
        b'5BB4Ml8Uajsd7g5JY1EcYwZYC3aDS7KU3X9jyjFwdAQ81/5aNOoEx0gncN9wsu3a+laGlcKP4kVPmDxrDyN5OkyePOHUzAm83Jd7Faf6eFhufIvxsdKsN1WFhm6sfILX'
        b'K6oI4IllI3MeIyIZXEWLsjF5n6PnfR2IR5Eu4KSO+XkGLDPsCuH/MB3/Vw7jfzdlyBmWKlmV3D3pZGZXZk+4Rhiv8UnQ+iSoPRI1Dolq60QDDjcZweH9RuUlZfU1daOK'
        b'KCYGrE0z9lzM2GNSuRjz9koD3l74W3j7d0MtwGTvNw2kuq1iWYJxNEIEwYogqBEYP6LfckjRvFC6tN+ysaahrEJaR94iaPhhcL95GY5MIK2ul9YFGR4E95tIZHI6pAAG'
        b'n+jnNJbU4xC00ob6kiUkvCm25+u3kC4pqyjBwTfxqeMkJ3YPC+o304cEkEkMkIJPkBz1svpKKWovbGRYh9WbdVi9NFpo3Ox+k9KS6oW4yH5z/EuPhUtOk3gn5HnBdRIG'
        b'NkXEEIqlNUsIInE/p7aiplrazyovWdLPkVaVyCoFzH62DN3ZzyqVlaED4/jExJzC7IJ+dmJOXnJdPR4SGxgjlu0EMQF3x42UHg1iL0W2f7HPBZ4tqSazcpP/xQX8UwgQ'
        b'TqOMGGX0Al7EWWkvYSCeCiyZ/Lo/kv4IGFeLJFcOr4yr41BMeBxuqGP4+sloCIejaNXUJa9vRFfRspBBFYN9xnA/0wpsM2qIQhnA6niZH3ZPO+OTluWfnjUNNmWDM0K4'
        b'IyBjWpowA+6GTQFoIY4Wf3owNdg2xyIxMpZ+8FW4oxy2TUM/lwEF3E5lwStLyJUZYCvoCMGgEQxvuBPcpkBbRS6Z7Jd6ZIWg3heClVQHQlJgExFeF+WAnSg7k2L4RIPV'
        b'FNglBddo37wrcAfsGUSTYlA2UvPZTHgWHgCbyJ2Ok6EC3WlEMQTjwTEK7M6Em4hjnjvcDjrhFoy3H8amOPD8i3APA7aBFnieVKXK2s/ajYWY2bo4YW54LUU875aB7eAm'
        b'Ko5BMXyBEhymwJ6pUEWDtW0Fp8AGsb/IH0MOmoHTWSLYnMmgHEAnOw4tfltIqe2L3PP+h7GaomqLV5jl1tAaltwMuB4VyqIYwnmpFFBEwWu0Qdcp0LTED4Pyp8Pt8HAu'
        b'Wu5S48A2VinogKtpxI/48bMfMGdiJbfzBzEL6fYG7eC0KSrPmGKI5gAFBfaVghsEei1hohlaNQuxIwlbyIQ7GOA6apdNpCh10tT5j1k/UFRgse3HU1/UFbUPts8ICQXd'
        b'iCv9+RDV/H6rdBqN4wq4DS5hN7gsEYMyDQLKRCZQ2IeSsl7xEmd8wUQTsnVxRr3tBLruMCSdIy4LNXoAWAv3IEIl88klWXYl7elHrPk32k1jToSrM0hRXfPZkQXYiCiu'
        b'uDI6wFlH1il4De4ICUUDP0O4rAS1KjjtTtAW4Y6wiWIcumAL3C42gwcJhoMVWM+KhfvBNVJitzhS+BX1CM8ItrGLVlA0KN0NeB1uRSUiFvMHXRDV2l6w2ZUEcACbC8F2'
        b'utBszGjgcAzNa45gFxs0o0edpn1A4UUrVAJitQAzuAa1IzzlTpjUE6jgKV0B6PbjbNyQVrWsSHgkipB0I9HONpGB7auL50ZwYnX1dQtutQgJxqwrBJdhF+K1KriDqLGi'
        b'YDtU6niXiXj3ArgWy4C74CkLenF41WV+SFggqpxguFOC7pPm0P3xIDhX4yfGHpUMykj2wmTmhOw6+lkq0AQPh0TgeyJRt21F1C+cSfoJ6HoR9uiYsBmco6hpYKdFDMsa'
        b'nqCRZECPczi6EdVbNFCAQ4hDptgRDgnwjRHTvVKAYTqKOBbWLPsiuI+8cXq6Sfh+Fh83gnBXrINuoOoBPctCIkIREdFe4DriPnfU/8kLg13wBCIC4y2KEY+UwWMOTCdw'
        b'Ea4jL2wETjPRfYixJsOLMkQCr5xWXRYmisXYXIFZsxCsZsS5g9P0gw74CVF+RHMMPG2GO8xusJ0QLQEXWGI8om3FNgxGdmCLH9PUD9AhLhbwls+sYHyO2Xp6eOQCXTPd'
        b'mLUMXAwM5VCMBLgVqLC78L7JpLBIcD0YrYAzsFEFC96Ge+ABBmgPnUIK2zU1JfpzJo+Buq5vywsWuhpogptW4tLQWJAIb6+ggDIynEbTvFjKF6MBxYhizvcH6xgBybak'
        b'GFjJC53GLMYVueLsdBndJvC0CHSJ07FzDJvNmcMAh1ztidVpVRbYBNs42DEa7oVd/ubeDXhTq9gedWcMaZeXBjfniKbTjmewKUuYDm5BPHJTqbbGTnB7IGGJBArcHsTa'
        b'xJYeCnB1HBPsLgeb6CjIWEKb6sh88RcmvSn34jKaVZRwI7wC29C8JaTg1nyhBLaTHrYUbGlEY3h8zjB7IDTTsKlJ4BSnwQ+uJxXqAU+B1XDLNIw4hIYwW3Ac3mHMM55B'
        b'DwrX7SaKC+A2xAVw34JiCnangBOkePSqd2C32D/DG14eBhXLoCblcGTgJGii/aovLLGE7ebox20cg2MtuI2qpbUB47XAs0vAcT9UK+AOPJwFt6eJMmjdRhCb8irgBIOr'
        b'oJW0x7/qnLwgowJPG872pea68epKMGiH7ahawB3Kyx/cAWfRmyPup5JkkBRbM3VYoUzKq5ATAlc702NtN7gOz4unoemVAbsEoAONDeACaCdlM+DmqHw0MW9Ds/vyeNDD'
        b'cIZnGeRKErwVIC6kK+QYuOxDwUvjFtKAs1umrRiBycug3LCLfQUbXgkoIRw3H7Qmw3ZL7G5OwW3Z4Kb9AhKPJayE6F7ReJCN2+osbEkXBbMpJ7CfXQnPpNIM2AlOc2A7'
        b'C8fpoZZPAbd8QRs9PqtS/YduToOn0b1MdG87uwoo2bTX4iafZXALnhWoOBOZJ5oLMc9J4N4q7BxJyD00hVA8zo71Ag92E86G7eCaOVaIUW7UfLYbaJtNwtrAbVAZ70fH'
        b'tUFMFQBuTKfhd53BZTYazzYtpBtoEzy2ALZz8ERAVYCD4AboHkfKTQzA9lVIIllIMcDthRywjgYkvVOZKBaJ0kGXTwbuZnZxUfUsNAJfjqDLawF74CXYboF+XqKc4GVw'
        b'aZobuTEO3vDRwfXErhxErETD21YyD/nL4Gq5pSUamdCMfxBuouAZNAefIKwlXmoeXsfwwaxlwfUWUIS+ccaxcAt66xo06ifXgKOwh9RzwRTYiqS2NIzLu1WcIyJE8p2C'
        b'FrFhd46QbLPIgzwZlyyPIKaMq364ZOOEPrpAcAkcEWA9IbWMMipfxoCtsnBjOVO+GtXBpn9kHPuf1Jp3ArlU8c6/t3REX8lf3Lnc8+Hkh+ltx5efqw9w+DzR/P7ehIHD'
        b'gR+L17jWC5YJlr39qsMvr8ZOuuIZvGL8YcdA24wcNzfB/h2r/npHWDs3/EeqZsvn57zjVnxU/O3MV5prLty14ry14scfXDxF20WuUz/qOf/o4heRp+aUdL2y8qs/NXYk'
        b'rWVy4ZGz4w69Xn2187sn636yuDf7X3dENV61YGc2+FL6sMEn/tqOnHFJ5Z2imbkWlbU7H9+/xou2D/WyZYU/WXTWaPqn8sIVdle+e6Ozw1hr8XK0IJy76LXcd9Oas5Lf'
        b'lfhUe70sau55O7fD6+Wq5p6Hue/GN0+2X7T3cE879/uPV4QsT190yOOrCO6CtEXTbbJm/MDIi1HIN7h5vAyjPntsInAtvFe28cNFeTGtctecnR+e7PhQlhdztEm+8cNZ'
        b'eTEnmj6zfNm8c8k0m4BXS+9sPvOp6uUJ3fYbl680/f6L11+NdSn4+J8P2yHP/M4nb59qaWbPzZqa3GuVf9l/99s/9/zl8ZbkTxO05yQ3dktc392s+eVvb59fcjnb9n5x'
        b'/JldPySFvXH78Fb/hnO3xk8rnDj77YInH/MEtx/4W+c5r/lmxt0bM1T7++0Kkjcl/3Mf46OF17+8vfrYB/fZy17740dRn50K2NWcdeaQNMr7nOmDjQvWSH2//rxz7Uoh'
        b'+Lbk422LWhXyee98kxV8Ys5r+2/f+mrGEYevWz58+Njj3bb3S/vUvt8/2GHlavHZo5KzUUuSyn+OvFj3xcvenT+E5mvPipakNPtNWJC0cuOb6V8nfxqVEXD75x39p9y+'
        b'8ctbcWDhH2vSvhbdbLNcUqP4yLj3Z9XW68e6vssp+vI1n87xr8TekS9+QftdssPiV948Yl+0+VTTN5+4df4xoGbtIYEdCaUOzsA1qIdtycnEGHRPG5FiW0gBaKORzPaj'
        b'vtzmh7cfmWA/PFfJyAIHU+l4RevRAqAFyWRoRWNEsZOM0bQKbsXDY8TwkYdEzDawZVytRR28BLaNM4fNjZamRhQXHGLVzIcXCFBFohj2mIOTwjT9tpcNEiMPwrUscAbc'
        b'ktFPubkSA5INeTqsKmKA841gMw0moWChhc6WAJ0rqwk8mgOvMzE8ObxCu++utYC3CWoarUk3yQLXwGWmBOyFHU/IULMhDWxEPRy9XyM8CTYy4uG+LPLqk+aD27QfBe1D'
        b'4TGVKZoSQi6ZJGKvXR2GbWUVRrE9CTeT8jwp5qCJqpE3PBHKtBlHA1+YwiNTdXi8lO0wA9VtM8hmIDg+K5G2fR1mTIrkyVsYyHwXaCY1y0USxZ6hfHp7UlN4mQWOgvVz'
        b'6TY+ALqssQkr3ujFKyns/6yrA78ouCuUg5Z+PcvIc9lgJ2KILUObDhGzDbYd4CF4h+yM+hpJ9bAdRzPJwoDAdsyAO8i+orkz3ELbsOrtV4tADxOsl8P9/7Fj8XCQMlaJ'
        b'RLLMckj5hA6JXuwDjg7hw55y9dC6BHSH9LqEq13ie1CSfXdWi9lDroPC6JD5fvN9lh2WGq6Xluul4moFUT2+WkGyhpvcwuiz42LV8QzGQ8eJas+U+9w3J7w2QZ1f8Krz'
        b'H501noUax+lax+lq7vQ+Oxfl+F47b42ddx+Xt1e8U4y9jVHJymRViIYXoOUFGJxAf43dMm1AnMYvXusXr+ElaHkJQ9fDu727pvYk0DswBqeJg3Olxi9R65d4N0/DS9Py'
        b'0kZefoEu8m6whpei5aWMvFyu8Zui9ZvSU/fUM8nlCo3fVK3f1Lu2Gl6Slpc08vICjV+s1i/2LoO++9Fve3aVxi9J65d0t1TDS9fy0seiPEjDS9byksd6NlPDS9TyEn/j'
        b'ZZnGL07rF3fXY/TC9Zfdn/3eYxQu1fjFaP1ietCLxWt58b9y98ha+5UmGVH4Y5GT/fgnFEoGRiTRFM+jZZnSSzW+0797osYhXOsQjnfYZzH6BCIVVyVXybtDeox6Gm9a'
        b'3ZXfZ96VayPFDyKn9UZOU+cVaiKnayOnawJmaANmqAUzFUaKxn1WfQ4uivJdL+LQ0JKuF3odItUOkWQLPlbjOlXrOlWNuNPJrSMWPyVSNb07pWt+j+Rmda8oUy3K7BME'
        b'dBt1uSrYHVbPl8nFQ1GoDFf5aCeG6ICUU3RdSck8YXzE+BHeovfr5fmpUrqnncpQC2N7QtTC5LsT7zZqeNlaXnYfz/WQ2X4z5VR6R0fNm99jjK5OvFt+v0ibMk+TMF+b'
        b'MF8TOV/Nk6hLJX08FyUL/aWopmo9J2v4MVp+jIYXQ56i2wUdf9XxgmNPjiYoUxuUeR81wDQtb1rfr2dwURopGzutHvAjevkRPUYa/lQtHxE1deiRsVrPaA1/spY/WYNx'
        b'e0aWmKUJytAGZdyP17/Yr2QYqppEXYYMTVCqNih1cIwY4340xuRoeTlPv3SqJihJG2TYV0c8QKwJStMGpRlcHnZ/xn2OJihbG5Stzp2m4eVpeXlPF5GtCRJrg8T3Z2h4'
        b'hVpeYR/PaUBgLxj/mLJ3d3iCE/TLnvcEJwMkEVL2E1rEu8TKcA1X0KKDVTDYwzCn9zDwgum3gfLhWeUpRL4tBIBg2KxyCu9jNFN6o4tp9s9yAXx28rtuarSbBlHnraYO'
        b't/of3Kl7kaLRjsgeHda8U03Guj06xiga99/f9vipHWo+9bTG3ZvWuCsSCWLckg+YxRYHefkUvXFHBLMeM3gUtHFAD1xLUa6UKxJbVfQKd3VcHWijuKh1JlATYmE7sdqo'
        b'SLEMYcMLMooKpoLBLQEpfiHbFCs/fawXFlvMne1EEas5STg5mTa3rNiC45BH2zvH5hKPq+L+mJLlL9WMp2mYgCTCayGhbLQMh7cpsJsqGw+PExqCncGpkFAjyqmRAnsp'
        b'aeo8UkjPFBJbZYmzZ7HwiUsyXfIkgTWuAZ/3lhZbxNrE0DS85UBOFrfXF1sI8xLonBHGFhQP3Z6fVywcsPClczoI6JNwXrGwuaKIznmk3pxCfJ/2J5viyl8i5tE5rRvM'
        b'8MncLudiCwvWKvqkiRMhKXeTe3HlO6aJtLrWOxYcIkoPXkAh1hJxGhng+iwBrSk7714WEhjI5uZSDE8cq7c9jdaUvUhcyWofmxd7XHDzp1Xv6RXwKlrsIsmvg1g3uoB2'
        b'WlW1QQr3wnYzlxysvUGfOfAgre5bDY4kwXajiXADdjfGHsf7Aa2FBMccWLCNgSROxFkiSjQBdJAHT5lBAg5TyQnFlZw5yymizzDJhxtgG9yN/8BejJ3LgBspcBl2F5L2'
        b'qQYtbNDGwFjuLpQLvDaVaIKEiW609aJNLbZf1Ll3Xy+n1VddoHlRvgicZZuD1ai4VoYt2OZEk7Y6BNzxM54LzqKGQE1xAh4hT2HD62g5cZoyK6GopdRS1waSuwzsqcbR'
        b'W1vAEdqycy+fjFqkPV4NICabvDM5xZlrqHQaIbSi6l4Z9d4y3JMYWxfKuiQZLPlS1LmDHh48s0tcvS7OYuMCo7SEgx8zZDtvv1N26VbS2WKBbeUp/9ONf062ym14vdly'
        b'b1fbxpIY3objyR7sF39qf/+7ithbAYfvTa96mGnW+tE/5WsytV/940jcmZf/Z5t5fGf0H27Grc2wPx35aO0m9okfbG/s/+T8BNHrYqd7m2ZXuMwSnWmw/ezRWw7iVXvU'
        b'L892vjB9Tup3wU/2Ltwh2zTvRuoDL+EvTV/f/mR57uN5F66nzkzcEnZE2PVWyE9xRxcq1rzsfPGP751TTL9T3Fs8Xfxz/4N3Ga8fyPN/Y/rbFzb+ci8v8B3Z7imhva3x'
        b'R6dIvl36Zpt1+GuW++ZGWFn8k22WFPbtG+ffCxkoXqRYOeubnh8WtLKFf/rHvybZTa+10pRL/3bRdI6Gs+3IvJaeN3sF7d6y+SslGxf7/zHyeFmOYkrZg2tJkz7mfpx0'
        b'rF3yy703iko+O5e1bfqT/gs/XV38xrmV8he21b5+6M+fLs3589dJrH+kvf/1X7+ve++Ljm9fLIqq2fZX459X2i38oOY2I6eytfGNjwU84q2wAtwG6zmokcf0WKCtOS2Y'
        b'ND72OXgFHCLGu9nwyCyRL14GXWaCPeA0vE4vR3fB82CTfjmLlnin9IjRp3WgTp31rrRP4VVwTO8BObOUWIdNAfuBAq/psrIKmHi/ZxvchrGx41ng7DK4laxMra0zcEQp'
        b'jA6wGa1aX6zOY3p4T3rihbveYU/YCs/W6lwgR3OARItO2tPyTGkOpsIP3IYbsfL9LAMoF6IVM16ReyTDO4O28EZgLTgINzBDwOkYUgemQAXP4kfQAN9kD29pyPiZbCdj'
        b'cJogmS8AuwHOgfGu4H4c/AoTgl9kEgt0RYBN5CnLclDJBgvpI/Ak0wadOE6joSuswTpST7ALtj/lfOmeTftVXoQXwWY//+Xg6hAiOY1HvncuqdLJ8JA1KcYKrB3pnZkM'
        b'OkmbCYLgYbSwTRNWpPj7461bRCk8iYYqcJxNr9u3gx2gTecvauArCvaOx+6i8A4NBp4KN9eSTNvFXg0cis1kgINo6NpNt7uiYAFtlJvEzdHDMszKIibFjWB7OFFhjGr5'
        b'OwWcoI1/w2zJOnwJOAVUtEoEqMx0WhEmenBzCK0ZOF4Pbug0AwHwxtPKAQ644qYDP8MU6x1T98ELBo6pniU0o1woWUWCBB0WEwg9OkiQsva53FAN4J/62diZapnVkPiF'
        b'j8mqfg6NIDQw24HiOrSEtNS3Ru2KUjJ2xrbEEsuXR9bcXZYPrD17rT2V01TMc8anjPu4juTjgM13xVqu4AE3oJcb0M3QcIO13ODu4O6Q7hAtNwJdxiqAib0YJTq821PN'
        b'je3x7OPyWzKV3E4nrXtQd5CGG6blhj3gTu7lTu6J13BjtdxYXam+D7iBvdzAbhsNFxUW0p3QndidqOVG/upDHVoSFWwtz1fD9dNy/R5wg3q5Qd3uGm6olhvanded352v'
        b'5UbpsnWYtebsynnAFfRyBSqUR6jlClV5qnwVyhM0jP78bs9L/g+C03uD0+/7aILztcH5au4s9YxZ/0auiO5Jau6UnmCDugjvQS8SreVGP+DG9XLj7qK3Ri+bSOdwVtXR'
        b'b/mAG9nLjeyx1XBjtNwY/e1u3R7D6jGBRkanG2joqZHdXmpuQk8KOe+grwBzLc8Hyf+oQlUeqiCVh5Yreo6rOgYYiHAOsn1MOQvsnuDk+0iK67gzXOGjsZuotZv4OMrZ'
        b'ZhK6YDNpgCTRlI29npM01t5aa2+1tTfiL/qcxtpLa+2ltvbqs3PQ2k1S2dFw9Y90i1aOiv3AZ3KvD17fdZgrS/aPU/MCVIlqXjhahrNvmj9mMQTJGIQIpY8phjtJ7VPw'
        b'GXuMJkRSI0TBXvOd5opEjTVfa81XW/P7nn6+g+PeJTuXKNmdlnSQnhY2QcdXuqu5nkMW632ePp1Z3R5az7AHnjG9njE9MzSeyVrPZOJFVIpDpjs4tZg/bRP2HPhtZFty'
        b'GHwbxn4Y2X2/wssn7HxGVk+zHJ7lC/ffco3DE5+AQVYV6CsWI6Vhn9C6mfiXwwh0NuL4XWeODZsm4cQLJ97YVspE71mr/4WtpIhXKQ3Lhn2qiOU+sW0mdp/ERq7foig3'
        b'Pi8+q6hgVm5yfj9LLq3vZ2Oo8H5z3YX85IJ8svYkVfifaUqfAmRzwK0yhKghxA0SxB6OyGY0DsOnPTPxoLjOLZF9pDv0cYMHOExu6GMKJU9w0pSE2NbZU4EyBKitA/q4'
        b'oSiDczjK4Bz+BCdNmSNg1kIwzFoYhlkLwzBrYQRmzRAhTYgR0vwxQpo/RkjzfwpCzRdnEOIMQpxBSDLYu7Sk9Vn7qK19aBA2ewzCZo9B2OyDmpIHTFiW/gPUWIkZ0zKX'
        b'gZHpnpGamFtOHaDGShzZlgED1FiJhZFl0AD1nIk1yzIJA1H/empFuborucoKtXNAn+vEvkk+fZ7efV4CladyNv6aqJIo5w/98PRWsZXR+i93L2W90kJ/hMrxVMzu88BH'
        b'zhhtoUBp1jfJVxWqzBxws3ZG/RInHtwJtn1cF4V8gIV+PeI6KfIHOOgXrn53ZYhSjvL7DxjjMyaUvZvSDhczYIqPzSh7JwweocgYMMfHFqjBFHJlqOKFAUt8bEXZO6td'
        b'ggbG4QProZtt8LEtZe+hTMSEDtjhY+7QdXt8PB6H/CjDbzDggI95Q8cT8LEjZe+qZCmTFMsGnPCx89CxCz52Hcrvho/5lL2jIlHJVkQPuONjj6HrE/GxJ6l3RUafsxvJ'
        b'5I1PUoPJJG9nqwEKJYj30Yjg7KYIUaxQpWvdwh+4Te51m6xxm6J1m6JxitU6xfbxnBQsRaZqvNY58IFzWK9zGB3hQ8OL1PIiBzgsJ1QUSprEA2YJDEvfAeo/SNOYgZbO'
        b'A9RvTWgXQCxTu8BuoCTrIdAG9+nWRBzKuoA1u1A6TOtjrvv+Zj5GrrIxQK5iYLyqXexd43YZlzNRqvuWMPW/uljH0Yx02lhflCklcSMG56ZN48rZEuP1psMVULPZTErK'
        b'0eFYmY2CccWRmKNrFk9dMybXLNE1q6eumZBr49A166eumZJrNuia7VPXzMg1O3SN+9Q1c3LNHl0b/9Q1C1wnEj6uA4lDBxMdIcoxvtULlvo8Ep4BIpMVNcq/Z6M6jSht'
        b'wn9S2rKnznQytjMk7k1MonakzX3Nm8Y1WZebSpyearFxKJdpkxVpT+f1JrOtaY7ochleJnExYDVZNFmWcySu60cEjJttI3EkOA8e/TTsqDg7+cc9w/DGcWwO/SV+WWWJ'
        b'XM73ya2R1zdK6+Ql1RI8m8uk1YJh9ww78C3AsOflNXVVJfV89KumVF5TKa2XErT26pp6fmUNNunml5SVSWvrpRJ+6VIaut13OPB5XTmFPWP6TUskjTI5NvXuN9f9JBbb'
        b'JnQscnSaJSlv7GctrEbnqqQSWUMVOmdSiyhfXFMnIaIMbf2NLcLLTAyaazAUn4IydFfaxN7E2WS0yZj4T+PWYaN24aA6NSIuHJa6gHyI3zebjVAOmxLlsMlTymHTpxTA'
        b'Ji+a6pTDo14zdOD44DFrFBj89GpZvYz4oetitOgbTVYtry+pLpM+Pwj+YA1H60D0dZgvNeWkZJ1ZfAnG8EigjfFRhippnWD0iO7xfJ13Ax2+hd9QizFJIvgS2QJZ/SjY'
        b'/MOpwI07SAf6/Swq0OWxaKjml1TWVpSIRiMlil9WgR5ZhooYmxw9e41eJ/RVvk8W4mpEkrT636iRsF+rEcTX0XSHTJnOrywplVbyfdBPkRg9bplUVlaBOqI/v1DeUFJZ'
        b'uZSQJaOZQj4qFcNJJ3XrE2xQFaMQryME9a1ofibBhcSlpAZk6ptDVy1okMgvKatYWIOrAtGEiK6TojFgjBAJDaWVUoluEBheSi5Ka6ql1bqSSIQEdEzXlG7oGL2O0+v5'
        b'VQ3yen4pYhVdNZdK6xdLpdX8UL6PRFpe0lBZLyCjUOSYL6ofP+hqp4/4MomuwUJ+rcH0gw59u/6IXyddIJOjGkaDHRoTCTsJ+Q26ZmuobpBLJb8S9GE019xx9I5QXLQ1'
        b'tXVWKjbxFyoZ8VTDZIoi5r/n9dgFukB/uQS5YEjPOI3GLoD7auho6xviLKzhEdoMvj/fnupmTsNm8M7Xja3pGO5w1wsRo5ZZDU4OFouNxAsNg7gfqrWAnaBtNin3nVJL'
        b'KjAsgqJyiysfzGJTJNI9tjwfrWB2Xn6aPq4hQXYwwFroAU3m4LAj3EWKnRlmTNXWuWK/hMoAj3yqAbt8xYWjShiN3HS/fMOiVsMdpsuBCuC9kau0E0CRKUUt98Kbnpmx'
        b'4WK6ShNsx49SmvOMfNiUlaXXLo+g8Yo5OAp2RJJCjaVmVFKELzanzLy6YCJFHF584Zq5o5TKA6p8nzQhrT4dVuZ1cNocNsXmyYoCQxjyK6iIWdfubtsxBUfQ2HDgl87k'
        b'D2udleI9YGMko/RVhrVf/t75tqmc0w3C3WnTf9z14Pt/TPnJocLHZbsoULB6woKoOYW9Az91rfph5xv8yRev9y0r2hGROP7+si+vnz4SmH8xs1f4VtO+PQvyHG69tSHv'
        b'9tyJky/aXbs9q/KL0vfGrw/54I+dLV/y9oZ+ZNTq5HQWZt55bW7/pgPframykSzI/nD8vIvJP19cKZnbu/WdLe+yPtseFqKZ3MGfEnvZPnV5WpjAjI6/eSC0cITye/xM'
        b'Ngu0OiE5WUGU0lywa8ZgWPZBIzAkVd8yifeg45ffhmtBs2ExYqK5diuHh6GCDc/xTYghWB48nLAKbNCp0oer0VH776HDcmyCN+r8dGHcMY6wg1mICzxBa29vJFUTNT8L'
        b'3gRbdWr+GrCfjrlxLNlXp67mJMTQ6urgKqI1jzKGF+DlOHorYsRGBFxNx6ACnaDZk5lIFOcj1Obr4KknIoqgHCuq6K2V7IUieBFekZPNFXScSZYVIiMqC6w3Bgcmge7f'
        b'WTNCIP5s9DLGcNTDRToMiyUTqIleyonKMmWZSnC4urNa4xGm9QgjEIUkznn9rlV02AqVe6+dn9rOj+Abpmoc07SOaWpuWp9nAMY3dNflHgqpHt9rJ1LbiUj2dI1jhtYx'
        b'Q83NwItuO2W+Ml/FOzyvc57GPUTrHkIgEHVPe5GOf6Gy6SWhu8ntKRrHVK1jqpqbipaih9L3p+8Td4jRTab6m5a2xu6KVaInTlLbTaKDt2scE7SOCWpuwiNnN5L1P3yw'
        b'u+CE6xFXjXuQ1j3oN9w2cRKuHazjRJ+nIzCex0oxHCuk7iJOLuHkMk6u4OTqr3tkD8ZeHOGVPUbbC5BUKsfRwg1Dd+dMYDDySDjt3zv93SxCsDF6p2k0dd0q3uS3AEEu'
        b'0EMZDorLYyHkDdWVHiCvENWVAZIhLazrJd5RIBZ/KxCkjjaLIgMh+vmpm4mpOzhInesI6oigOETbvwO0qBemn58mvI1lAG3oRtOkl12fqrDfDrjILkLi9fPTMx/R880g'
        b'xOGs1Tq6nGi6DAT0f4umCj1NSNJ+fppKcB2pGfo68hmS0EtG4nfK/7PKMi3SS8bPT51keAs6Yq26gUj9H1WUaZFeuH5+ehY8TQ9quUEh3YAeAZPsYtD7GYN+29llLAMy'
        b'LSid4/ZOlOw2NQB6MCI6Axwwz7TJrMm8yQLrDJqsyi0GYR9Gomz/V0BPvuXYjqI1iJdIcLjWauliQx5Bfeq5ArcmozUenRlrdkokErSiQeuiEt0SmcRfxZHthPwFdTUN'
        b'tbRyp4RfVlNVKqsuwQFinyoSMavvIDasr5Dvawhli44JRi7KVFpTsxCTihVQZBFHk1G/tPY3KDoGHxTNz6+pwstlWk+FI/zpIGVLSmsa6HC0mDOkkrHqBv9LqanjS3GV'
        b'SGTl5Wh5h0YmeuE5/KV09U1C1KJqW6CLXzjKmg//Q+vYspJqsox9lg4jKNxg5c73qakl4Xcrx17DG9YrvT59apDg+8SX1knLKqobqhfIdQoNEsVwVEKH+EAuly2oJqzg'
        b'T+rEoGBdQGi+zPCtZGhtj9bxo5aqX7MHkUYOjxpcuuMnBQmEWLPIl0hL6/FzUI4ytKqW4YOysbQNhCtl5H65tJ7UXWTUc/BMCkaxIJrMkV1FJpVHPzfPIVpl9boC6Hon'
        b'ZwZVHz75NZWVWN1RI+D7+lZhfRJ6naW+vmMqpsgbDyuRPjVUZCqq3mpRQBqakap/S9E0Uq9Oe1EjJy+sQ+99rvtx56TvNuyu/vysQcUM6b41pS9Iy+r5pAVH7wP5OZHh'
        b'gUE6LTJWEtO90//5yBiGShI9QkHWWCMrkw4yfIK0UrqgHOcT8OcEBc97niKDdc3YIKVfR1ZNCMW9PikpK2vWLPxmo4Wsxv9qS5ZWkYDX0jo8DQr5VaieB9VABgQFP5sg'
        b'XfNggKTh7YXPDFcK0r0lQN9TRiWLFvIS0Evivo/LQI8PCRzz8cNwYPQqUoNugs6iHlktl9FE1ZSP+tQSyQuIM0h94BtI1O+SJfj36GPj6MrVYYXIiXZYVlZRL1uAX0Ve'
        b'VlEJb6KRvFLwdJ8ds0wRH/FNfr20AQ2ugwUgDpbxdVWERqgq1OOSC0UFJfWlUqxxl4xREmIXOmRtZUPVQmnF6PUv4oeMyEaeVtJQvqyhXopmDhzunj+9pk5OiBqjjNBo'
        b'fnxDeYW0tAF3PXRDfEN9DZ7fFo5xQ1g0P71aImuUIWaurEQ3FFbJS+qXyUe8+Rh3h49G8m+voIjRipEZkFX128iKHK2831YvUaQih6r+V2p+1JMFNCdj1fgIun8zJxq+'
        b'fnkdehsfXLeDNJWULmtYIBib/Qxv50dMGpsBh2UMihorJ2Kz6oCSsVlqeDHhYxUT/qxiEFMMvt8zyog0zDbmq0UNK2yU9xpzQtPhVKERTveLyANIJkVjq34o98mn59gx'
        b'J+whGKxofiI64NNHSMbxEaNDaTX6j9icj+egyDGHXAMAreHFBI8oJviZxRCsLXrKmB5fIEpP4vsU5tejbzzfhI152yA2F31rciEZqfEJvg/q5DoWR80+djU01CERuQzN'
        b'Fom6X0K+gWyXXJjH95kBOyvqUCdFtISOTYoBLNhQYYOndUTpi5IvbKiTP03Us8S9scRLIko+v+Q3KKLFD9vlej4ZhgCdRfOz8Rd/TnDgvOe/LZi+LZjcNnZr6BHUdCKk'
        b'7hgvzZ/FBwReDd2Cv1DGp/ONPYqlSevqqgNS6koaUFLpH5AiQ9Ld2KMWyT72WIXLGXt8wg8Ye4B61pPRqJRcgYQwNPaPPTQR2pDMJhmdjLEqD0mxUmk9lizwNxKwwp8p'
        b'35XWLInmY+MLJD+VY6kVnUB1Pnaj4pswbh19V0klHx88844yWT3ukCh9prhHg/XhnPQPUrAQy+mikKDwcMRpY9OEcfIQQfjrmRxZXoLeNgUNKs/KRJD2UAvhL/6c8LEz'
        b'6oY53RD3LI7WYwBG8xPQL1oSnhMc8cz8g12b3DJ8F/uZ9a1HFtTdSbfP2IM1xhNEIlpCfDZqnrFHxFJZGSowPRE9epQeOWwn2YQacyf57bms+v0kQ7HFmeBVNB5obhGf'
        b'8+Jw9CUm2C3xJnesjmYnBDAIWprwX41VtBOgIzwNjonTs1fSeFAMcMgOniTZNVEO0RyKwMetkAmSaLjdFHigWIcRVQQu+sd40DBgl+HRFHGmX+0gXhCNs9cKaLi8JsbK'
        b'MhaTIA/OaamxoBow7HsSuAS7/VDuDByQE/vpgK6MrGlp6S+yhekFFDwPtuRRS0JNF3j4Ekiaj6dlM++5hplStSV27/A+i26md3qXW4EDhrj/etD/qfY4tEAavdVmiPwP'
        b't4F9FgLQDPeSDRkZ98Z0ttySQVHur58+1no+G8ZZbKz6bGdolrLLpXiNQ1xXDMfF+kZycuupvzQ5blzP2PzShOvu/2N2WLgyvUPZubgwQrh04MDXP636KfZigPXFhD/0'
        b'B6b3GC0P+HRDpMpyjWe0u+2FfQludb3Wd7f/2P9eRU7nvtfufy15NLDuu2/Hb+ekWvqO+6n/RI1S+t6V667Lg57M6L75aY98peaa69spR/4WV3tU867Lgsy/9z3e9cPB'
        b'985rLdN/5hXMPCIxf+v9Ls0b9d+dX/7pnU8eyz97Ofvv2mlp4+xtc7P5f55rf/vx2QPvluzp+6p46YumS6+cmLtmyum09w/sqb9fpvp8m5nwUdiS1R/u+NrmQJXVRfl3'
        b'ne3/esnyyL/et/jX4YhfOCI3MctcLjAhm6iJfNiM2OmiIVQIU7TKiXbruQz3gxPgdGZqDg0WwgAX4DEJucaGt1zjwRU/uDknHXSxKaNKpocMKskOKzi+Cuwnu8QrwLYR'
        b'4exugDtPcDhAuB22Ye+cxbMoHAb4Wfun4IwT8VQKhdf8zPWxBhLghhHhBsCpucS7CnSDg7ZyzA8iHxIMdwd2rLqKGLCFBbrngg1PiI/nAbjDW5yZzqCYcrAzj+ELthYL'
        b'xv2e0cbHUcPQP0b4alsMasT1ACDndRu3ua4UX6h2C1QtwhHpnBT1ahKRrs8JxwKyF/R5+ygsaMBoT2Vjp7CbpXEI1TqE4ouFjD5vP2U9drDptuuW9IRfqrwbcjfhbog2'
        b'PPVBeFZveNb9Mk14njY8TyPK14ry1d4FCrZi+j6LPic3pVFHjNZJ2JLUktRn76r0VNt7oY/uqX593r4KnOtQ9P7ofTGDOT/Bm6JTNY5xWsc4NTcOh7Sdq4pSjw9rYfXZ'
        b'jVdItK7+ajv80UU/0Dr5aRyEWgdhN6fXIUztEPbQ1Vftl61xzdG65qh5OQNMln1QX2BUt2mPpzow+a4dSugP9jnyUdlpeCI1T/TDQydPTFbQUNLn6qeoUiVqXAO1roFq'
        b'XiDeAR1goQv4m82yEfVxRS1JWq6nMl+LPW5Eam4Y+nSz6e/Bzw8PHfgYREU0lPQ5eitEKpbGUah1FKq5Ql3RNiL0LQ/EvMy2SRxPwfFmiYEsyDdP9GNBPw7+HcpLsqLu'
        b'WZkl+bDu8cyTJrLuTeSg3/RG8Th6o3hobwNDzf0mKIARzDa0U/xMZnsB7xQrqSF842lODAauxN8r+d3cXz6nRgmrQ6ZLElaHrYtNxmmimox0wRr+d+KTLRAw6/5CjYh1'
        b'7DbKXD6JnsttFrFj+lk0juk/ls2nSDxvH9CdJG/AcIbb2FQQOICGMMZKuAF00igCeMPNshQeMUfNNYMCHeDmDHB5Nh0JfAO8vhjcBpvz6ZsZ8AYFLzXAs+RhW8tXWu7Q'
        b'wQC/hc7QPuBX4Xq4t74Ee/0Tn//aBjLf22XlMjFGLqpZDBAQkECKOFRu7HiVSYdPC5ppS3vtvzPZuhIw44hp29XSlbRD+EeeNrlWFDlp0bAoh875Q6JF7pesQGJX9pNA'
        b'hxnwSpRFXA990qIrlU/n/LzQLCGERVDtMq1DZtI5HbPNMvJpqDvhPfPp9Ml5GUbFnRRNUnuZDuw2D1wWg4NUfm5uLmqjJAqs4YNbNGriUQzttRreCgkMxLimsJOCa0x1'
        b'UI/w9kywOj9XLKIwLthxdAWj7RGEvkq4t5FgCxBkgamwh4ALgFa4nSADeMyCzSGBcrgegxdjfIFysJPgN7DEoBsj+7ujc5Xurv6k+VJAJ7wSwsaYDmBXfXAm2EOjFbbC'
        b'fXyIAxqIqBXghqh2FgGKXVAHbsOL4IQeGEAPCgA2gI2E7HxweEFMcH4uHyMrXrQ3AoeBCp4k95aA7bB9KLQRBY+BzQQewAvcoL33cW03e5vwW5l8PFJY/MlHV7GXGKax'
        b'UfTJzI1zV+jgKzaDPan5uW5ybKoN16Hyj0Ea4vJYsr1jPTMXs3LML35xdPYweAjuWFCUnwuUAoqKXmkOD1vRqLMRPB684Cy3DEEVxgSnMXblAQuZ2vkUmxgqBb0/5VjB'
        b'NSSSWR+Y9/41Z2/PR7Wc2+t2TlUed3rVI3Ta50cajJM7uaFNVtfqPjokqfywsPGyV1CXdM7kV9qXx/41Z8larm3an/8wL25lsNHGtrfm3H9nys1vUvfUWTnNGegINTv5'
        b'LbhSkmy8e3tl1vta25iPNolM4vy7LpvXznhvZvm+evVrlRMfpnyWOmdgw8STX8mlS1/WzAl+8qp4k8fiSVPvby5K+zr4zSYX1SKbtQFhzKMpqa8nOXyw7ZWdOSYHWCZT'
        b'LA+f88j1fO/FzlP1rE/joMU2+beKh9MVs6trVaXhBROPvLDVcclH0syOg5feieifMu1v/2oOq9i0oW3eofU7gyNP5Tz5Ofq4TLCc6x35cv6yN17raDtW8qe3rSs2fnfx'
        b'z/Ndy7bW7vnjpdkpKb+8WSj49g8VrErRzcA3DxWfqn+N3XV7//HdHrz0oj+ubDiZ3HjsO/v5v6wyW1zoKv7XzyrfN8O0sltLP/7F6/EvO2um/U3cv+7q20brjU3m32HY'
        b'ftK0/M6AgPsEBysDG2bxads1A8kLiWMnR5G+rsP1BEENXPIFzX7E9g9DfW+BF03gDSZoLZj/BHPY1FmgTZiFhP1MBsV2Z4AD1mHEFR52+MEufTgnyhleJfGcYJsP8fcG'
        b'66RMtBLYZYiRxwDn4Tq4nQhz+dNTxZnzYcfTLv/8ZI4p6JhEhNGVTOw/X05bA+osAeXgEHm+FG6CV3Qe/4sXEZ9/Zgi8DNpoSINt2Tx4Kulpq0enLDNye5nMYRCSAB6B'
        b'OzAsAdMDrA0ldoIViTQ+H7FgbG0YZsRYHkW/fzs8CzbATaBlEHMPidEZ8DSp1OUu08Q6KLxGCxoEwAqsYyVYl9Hkba6BJ/W4dZumDEEAiGGTzlARnoB39EVw4HYCAWC1'
        b'kpUEO1G7EVyHjuUVtCEj6JYOs2WEa5mExJlo4DkhEertJWlrSdgJdhESU0EHeoI+5BYFj2fQIbc6ymlhvwuuttQbU0aDi8PsKa0aiU3oNLi+DFfTerhjpFUoMQkFyniB'
        b'yXPLOngY4vMNbeK+oXBIniEhR14kkZXVE6l6nM4BP8+NmuDUwsHxmM37+J5afiCNeKXhR2n5UQOUh43gMU5a0uj4W0v2TemYMhjziwSOtt83u2O2yn3f/JaURwEROOjX'
        b'yVVdq1qSFT7K6RpHPw1X+Ijr9oDr1cv1UtadWHxkcR/PqY/nqhy/bxwqQ8sTddv18kLVvCk9XDUv+S6XDupS0Dmrm6HhBWt5wQ94kb28yB4bDW+yliBtdYx7wBP18kSq'
        b'Eg0vUMsL7LZFYr2dlheGr1np4n1NoxH7upk4mpiWF0p75KVpnYNGK7UnoSexJ1HLi9Nl68jS8Hy1PN8HvMBeHoYDIHBkOjgAXuQwwuN6HNS8jLspT5+suJumTSp8kDS/'
        b'N2m+umiBJqlCm1Tx3Nlc9DUxvxu9TISWF/GAN6UX1RN67ThCqqvSDv3NPOzS6aLB0c5cSNUOfdCbJHWk77PqsFLWqRjKOvRCz77g2sdzQ/QNhDkFjn9MOfk4PMHJ9+EU'
        b'z3Vno6JC4+CtdfB+HOFkL8DwdQIMWof4A/+KpNw8DlXsr1Au17iGaF1DEDvZ8QYoc5vwR55eJ1KPpD67bdye3aykHrSTMF4BL1rLi37Ai+vlYbwCHZbfEEPp+WrAxlSE'
        b'XsF0EnoFlHxvO+wVVH6P7UwnhSMm9WrNGuBSPJcWi6cjYD3bEpVEwPr17vYxXlc0UDqH+WS3/2Vf+Vy8hHqCR2zDMLJGlGGQN44uogdb5+KHw8kaDUbzGBn/578SjrPu'
        b'e2rEumG0GEDG2Q0+eGzdD882+qUhqS43Dc27aG4FJwvSwBnYJPQXGFFpcKNxFqt2xSKipINt4CZYi9LTxFqeVcmAm0EnWFsBeojYKUVTWNdycMXPmIaB2uFIo85vQxPB'
        b'Zr8cJsXIo+AuJJzuL50ie3Pjawz539HlU75526bdwA4Nl9puA3npWsvGe3fdBoxdlLaVrS08HmW6UVKy5V7zzJCGL3JKW2bvsj3ZsMv9uwMfTZ561EHxMSWdyc7htebf'
        b'Vr3w2TVYUhV5Yl/Gy+nCmg3O8++d89WceU9TX/n5l21viU7tPX47/IU//LlvU2tXeP5rd5NS0qpBRwF3t+02s8ren980a/xIFHVs36dmZwaCuPkx3pnTopoHFNbX33rX'
        b'LT7hL19d+LLsn3+rS1r+xeV4j0vTr/vv3rnwfEj++7+0lZ6tntDz9aTP4ziNj8raFlyO+uR77YGYxhPdq+W10oiDL9nbBL+2E7bvkJf+YmS8NyX5RoZgHO1esBcoQkjd'
        b'o3VnBAMegKfB2TBwncyJsbZIQkHzGO0/LIRKygRuYa7kAgUtKh0JgpfhFnAUnEZ5NmMMoGymMzgK19GT9nqwG+zEMonQP70KXiI5zGE3E94E1xaSiV8kRvP3RXhpscgX'
        b'3ACHiJrLFJxggqPRhfQj2l5ki4UY+mZzlmumP4Myj0MLOXgbbqWpPwR2M+AW3wy4OSBHxMRCiy/imyNE6KpDbKISDwYJveSvjxNqX0mcJ3gOcYi42yxhOtyGRD2j+cyJ'
        b'GfAUoWsRYslrfgSwWOQ/DlwWMJE8cogFNqQjaQM/GGwvBhvFcI0XlokCsjmUUQzTARyMIESXg1ZwVaznX3i9njLlMsHhSHiIXE6bCs+hBx+ESrhNV20JTB7YDZvJ5Xxw'
        b'J3O4nLgTbAfni2ErXSMKcAUq/YAqRoenbARUTCE4CJr/YwRfvVaFHv5MCNbi4PAnL2mko4ce0SnwMtwp7vhdEXtjd8YqPWkXC6xHilIldKWeyzqV1eOpEU7VCqeSk3cT'
        b'XskAGffrNUkF2qQCcuqho7vaI0LjGKl1jFRzIzHGqsV+CzyHIfnFzmFv9M7o1phdMQ/sfHrtfFTjNXaBWrtAHLnTr8/RXeGt9FSxVHM1jtFax+iWxD4vvxMLjyw8XNVZ'
        b'NaQs22emYCskaDbBBSsLVKH0PKQmnz6uw970nemtOsjKFvEjJ5eOiEOx+2NVnhqnAK1TAC7Du4/neMhkv4mSiwlTWA17DtPejyS657i4KwqUHp3eJ4RHhKr67gKNR7TW'
        b'I7onSeMSr3WJR6VN8Lub1+fseihtf5qyYF92R7Yie4CFzpJLJHmMkyfUsHOjJVg1N9rpAZaeJjkeC1+2H58cwXk5gp082fTlWAZK6fnQlJ4Pv/3VSZFmD7xtMahzG5M5'
        b'3Ngo62pKD8S5nP+r0U//S8FQSYhIAXuEEzZ9SF6fSX5nC2xHQsuYMShDfJnncG45xSARveulVXIaIOYbfe0IbH5HLbtBY+DqXz3yH90o53CjDPrYu2NB5U3mcCAZNtvS'
        b'GmOdWA9YUFb2TTOULGWiYml32d38+3Z30/smOCv9eux68ntM7yci1rSahvGPUPqEpANGVGwcY4DljTFnfjV5zDG4k43P5jGGIcyEY4SZSIwwE4kRZiIJwozTRIVPnzWO'
        b'YEpj1DhhjBonjFHjFN4kHoEwE4YRZiIwwkwERpiJIAgzdk4tqASCwcQNQhnsQlAGu5AnOGlKHJEhFmeIY+AccYwnJCV5DJ8SiJ8SjJ8SjJ8S/BTQzSgZTEjtop5olcVQ'
        b'yLvt6F90iiGd6hVJiiTlBK17RI+p1j3hgXtar3uaxj1D656hcRZrncV9rh4KiTJKOzGqx0s7Mf7BxNTeiamaienaieka1wyta8ZjFsNFjJuHl4krGaWo8w8+Y8CogWEp'
        b'GqB+n/SxMS7ziWHJ1awoS5cB6teTRgapCsVEtaWrxtJVa+k6wORaokHqV5PHLMrK7en8NMwJFjCc4T6wTj6o3eFg4NIOS0cmEg7XgA0CRrbM9tpDSj4bdYtOowkrd/wp'
        b'e12u9YbP6q7VCv4ZUHX42xNXnN6/t23yDP8sr3v37m0I11jfCMri1VatYIWvTDfOkJ087+lwv0N+O+r75Y6v920trHy5sWvVo9OfrGZsPhQawuj+4OLK3JhXf/7px+5C'
        b'jUmjrXOU9Iub0s9ufpX0zZ2Cr5ILD+3u+FIaxoi89udm7p2/+fzyoNXnXWOnqzf3vpH31dLPtRMOgaj+1vBDbzrw/75xy7HotPC/vFr2xo2bmyLirS6fTF3pqG5JCT2+'
        b'ujx03Lz6B9FvG71Lfen65srew+DT2WV+IQrJX9P8fObOOHw3/PSBcfd7fjl+PfGF6cv2fvue2zwvhw2JdQ5tjh///Q/Vmvt+k/8Reiwk+oS4N9R8yl9DFuTWtD7+c8Hi'
        b'ItMnO7MlN1uC5n2wvv/m8p7GvBt9RxV37pzLsbuw7y8fNp38KDrs8mvVS/1O//WT3ddWty0NyH7L46+H3/zHI4kf6wOrjleK3shuWPPe9wIWHaKhZSG8BbdkgltgHYNi'
        b'RFJwe3oN0Zw4g+PgqLkYXgBNIx1qTdzhFqI5yWaCTebD4qtvcTbY84TbwEaB58jh0OSZyX9j8P03hmtPWrSKI/+eGrdHjOD9JkVFlTUlkqKiZYO/iMz1P6xBj0c0iIdS'
        b'lvYDbGNTh75xtk3yluDNi7cuVrg3r2haoZAr5MpgZUln2L5lHctU0/avUqzq9kR/dT3ulxp6pl1act7/kv/dpLtJ921fSruX1hucqQ7OfMhzVAQrSjrC9pl2mCozNDz/'
        b'bgcNL1Idk61xyFbnFagLp2vzZvQ6zFA7zHg4nq+0ba3eVa229hxgUbyZjAEzypbbEr/LvimhKeGHAWOGaTqjz9atRXTMQi1K0fBTtfxUjW2a1jZNbZGGBZdIG1PPAep3'
        b'SXy8TdEQ9VuTxzh5MnSugBFj6jhAPStpmf4Yfz0ZOvsiwxP/fFaiGP8Yfz0ZOpvNoMysB5h1bFM0lv2/mD4m6RP6NwsRu3W8jtx6U4rnpTLXOIQ0WQwYmZgimW2sZHwd'
        b'y9QZlfdfTR+T9Inh+ReMSe3mkbf5v58+JukT+re+LkdmkmOfvub4qQl2FLBzTBDpds1d+plFRf/mLvl/ZyDDOvbi4XYeo8mgNkwsg+oHL7xglX9G6ZRlQQyGNZb0/99L'
        b'fjc/b7ySPmMaz6JeYlnF27BkW770Y8svo5NL3jxetS3KjBlvnby86A+cpFrImZv9sb1R0OdvWLySqar5pPQFyYeTXFIK2H7/+Fb1i+r1rVxZsOTV1hNxrc2nfaSC2i92'
        b'RjZnvNv5Q4jxNw+/bvjoscxFOqnmx0P5p9zEb+9Z1rZiZahz+6W52pNtrx8slIcIPr4fa2xl+U7Bx+Pb3y1/2C0+8K7Um8MNtRDOrq04ar5jteuPvOImmz8oipubosb7'
        b'dN8zW1jZ2NZ7iPnOxYfNPauYd3sCV2WlCsYRRU4GvDYJq3FysHnbVrExVAElZQ4uMNGP6wk0ivMueMNbHO6YI4LncUasjLGBN1ngcBJU0Tk2gUsZYAvYAXfgPRGw7QUj'
        b'sMOYsrJluXISaDusNQlgjzg9yzfLmDLyg5vYTBNsrUWLF0fB9glwS4ARPAPWUYx8Ch61lpENObh/yVy/DA5oBWcohpiCijk2NCzydnhHjAMAbkdPg1sZYBu4RZkLmLAl'
        b'K4goUmZMDJAPXZZMpszSmaAbdsM7ZLfIHV4Ti4lsiUQSbgQOsQqbWdkrfGlad7Jgu3gJuJI+aHAIb8PT5MnTqmE30U7SVnsc0FxHWdgx4SWgmknqcwrYNQ1jPQtr6Qzw'
        b'Ip8yAxeZ4BI8BM89wSIDuDkHnEF5LliApsWLGtDb7YUXF1ksamBQDnAHC2x1ADdJtYrhRpGYoJnjd0H3gZuoafYz4ZFl8AptKHY9eyWu9wAxEqu2Y0MxfGRM+ZQ7ebLB'
        b'ujJjgc9zC1X/T8pYBoOUD5G24vT/niFvDcOZMBkGLVLCMICXwOOWI8WxW52N//osuQ8sXXstXQ8s0Vj6aC19Vqf0sc02Za7NVNu4H4vUsIVatlDNFvaxLVen4z+DH27q'
        b'4Z8+trd6tE8fW6Qe7dPHnqge/hkwmm3NQfPI/1fpEj5lwV2dY7A749bPqpRW97OxW3U/p76htlLaz66Uyev72XjDpZ9dU4sus+T1df2c0qX1Unk/u7SmprKfJauu7+eU'
        b'o5kGfdVhL4x+DnGA7meVVdT1s2rqJP1G5bLKeik6qCqp7Wctk9X2c0rkZTJZP6tCugRlQcWbyeR69Lp+o9qG0kpZWb8xDRQo7zeXV8jK64ukdXU1df2WtSV1cmmRTF6D'
        b'HUX7LRuqyypKZNVSSZF0SVm/aVGRXIqoLyrqN6IdK4fmbzleCBU/6x+fP8SPJDHDt4mGseIo/xB32jAYEhaexf5/Tn+3CRiLUy+ZmcbzqZf4VvH+rB9NyrHnd1mFf791'
        b'UZHut046+dFRd8yvLSlbWLJAqoOKLJFIJdkCE6IO7DcuKiqprETCGGkZrDDsN0PcUlcvXyyrr+g3qqwpK6mU91vkYSfUKmky5pS6OKaOuWk2xy37o0lMVY2koVIaW5fC'
        b'pBEn5CtRMsBiMBj4ndkDFE6sKHPL1cYD7EprBneAMkjnu1OmNg9MnHpNnBQZGhNvrYn3AMVkhKmFsXe97nq95HPPRy3MQJ8+E+s+s/FNQrVDiMYsVGsWqmaH9lHWasq6'
        b'haehHLWUo1r/IeT9HyxQYic='
    ))))
