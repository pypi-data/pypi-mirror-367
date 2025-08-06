
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
        b'eJzsvQlcVNfZMH5nZd+HXfCyM8AM++4GIrKjAi6owYEZYHQYcBZU3A2RUVDBDXCJEDdwxSURozHmnLZZmrdlxFSkpjVt+iZp08ZEk7xJ37b/c86dgRkZTGz7fu/3//0+'
        b'Eu+c+5zlPuec5zzb2X5PmfxxDL+PV6JHJyWlyqkaqpwlZTVT5WwZZ6UNNeFPyj7LYkIqGymHTcl4Zw0xjZTaZikbQfhSrjHNNhZ6t5KN5WFR63g2zUL+9xttszJK5yyk'
        b'6+qlWoWMrq+mNbUyet46TW29ks6WKzWyqlq6QVK1SlIjE9valtbK1ca0Ulm1XClT09VaZZVGXq9U0xKllK5SSNRqmdpWU09XqWQSjYxmPiCVaCS0bG1VrURZI6Or5QqZ'
        b'WmxbNcWkRn7onx1uhPfRo4VqYbWwWzgt3BZeC7/FqsW6xabFtsWuxb7FocWxxanFucWlxbXFrUXQ4t7i0eLZ4tXi3eLT4tsypZPS+eo8da46a52VzkHH1TnpbHVuOnud'
        b'jc5dR+k4OmedQMfTOeq8dR46O52Xjq9j61g6H90UnUu1H2py641+bGqHr7E5N/rbUGxqg5/xHYX9jWEWtclvk38JFWQBuoZay1lCrWHZVAvZRVWmXeeD/rnhinJJb6+j'
        b'hLZFCmvcp1I2xaVql9tSKwpcZQGUNhQBM+AZuAu2wh3FBfOhDu4qFsJduWXzRHwqDNyYN4cL3wTtsE/I0vqixPCKH0edWwh3w7ZC2MaibHPBNXidDQaqCoRsrQdKAXRw'
        b'OzyanxuVy6O4jfAQlwWOlS3R4o4AV2CfK4rZDC7kiuAOVASPcoQ7OUXwFh/lxuUXbIwBrXBnVANCqA2VYIvyHE9gg6vLeNpAXMT2ItiOUly2B7o188Abq7Xwymr71VoW'
        b'5Qn3cEBbvTNCNBgn3GedDlrBnuh8UQTGFu7Bb1bgAthB+QZzwYvw/Pwqlkmj+RobbS96HPBpQQ2H+pKLepJCPWiFetsG9bMd6mcH1LdOqJddEA24ob52R/3sifrZG/Wx'
        b'r25KtS/pYzQgdliN9TGb9DHLpI/ZJr3J2sQ29PFT0LE+rn26jz0n9LEf08dz3a2onkR/iqJXKIKLlRQB0tYcqu0FTPwrCn4pK2KAvCU2VEwSaqwVK+wdnFQM8HQ8j/qY'
        b'j0qftSLq081ZVD+lsEXgX3p55Q1ZfxpCUR+FfcV+LfYTURulwFxjkbCbJa2scULp4x7Eict9GPAOxWMnQVXUVPa8h6y/L/56+Q1qlNKKMQG11oGrqHNbo+eHh8Od0Tki'
        b'uBP0l4bnFcI9UfDFWnGuKK+QRSmdbKbDw8vMesjOWGUV7iE7Qw/xzHqHwv1TbTfWA9x/Ww80P90DVhN6wL5IhZtQi/smDF6E20sWiBayKTaHArvAUXgUvFSldcW0eTUA'
        b'7ith58LrFPpmEHglhICb4BG4q2QBm6ISQVctNSdso9YFgUvCuXAfB7QvpahoKroGXNK643a8AXbAZriPBW8gyhVRIvAK6CJfhs1z4cWSwvlwF49ir2eBU1lTENV3k7Eu'
        b'1oDteGRF5qMRsaNgfjjsdAf9UTlkuIthPw9sgzfnM0j2xzmCK3x4FeyhqGnUNNpVHpLyM476P1BcitWcw+9NP7p1R+++K/tWJQZxvDSrD8xaYm9vPd9z+8hRe/vYAnv7'
        b'V+1fbUtsc1AI244uS7RPmnXdf0aPzZTEtqMPznbTZ1qDS7pWel3p8o6ZZau2tSsoc/d9h9/nzZ8XP/JR9SNqzuAqL4l4y1nNS2ekf5LmVW07ezCjbNcHyl8JkrqaBuWp'
        b'84a7Pgq12VrArmxslnspa1v+WPmZdI7qxfChX55b/Lns7aE3bzb7ib2P/5yV0Gol8QwvXfF5aLbHdsEvoooK4l1i3d6/3e1IXbud3n6YI+Q9wZIBXJ4K2/Lhrki4q1CU'
        b'F5UbgZiTKxzkwBZ4fNoTb5TCVQiuReaJoC63oIgPdvMoO3CJDY/yC59g3pEAL0ZHioV5kQxjgyc9KCe4hVOvhfue+OPyX4vMsMNtrUUMaWc0PAEPsSkX+DoHnKfBQVIE'
        b'fEkei3pnJ9wD2zgUN5UFW8EZcAl2wWtCh1F2uFDljFL9kw+1A+YD9Jbxv+89plWr6ptkSiQtiRwWIxkqa5wx6qCSKaUyVYVKVlWvkjaZv7JxWV+jx39tob7cwKI8fLpC'
        b'9y3TZT+YEtJT/aspog7rdlZ74oibV/v0ETqwPbsrdm/uffepPbwe9V33yBE6tM/9ol+/34B6MGtYmKGnM55Ocp8O6plz3NYE3MfrWzMUlnzXPcUQd4+O09NxA/GDnGF6'
        b'mml+zV33KJSmd3Yf73jecSfTMrh9tUwZI3TIacdex77GYTqJSfCxT9BQcOJ17mDZDTt98Oxhn6whQdYjP8pP/MifEnh2pnSkdGUPuwUN2Qc9xiNfhYe+0HGUz7TIqFVF'
        b'hUqrrKgYtauoqFLIJEptA4L8k93kiJm0WT+pMBdQEQ5h3hUzcfpU9PhuC/XtehaLJfiGQo+PHD1bV22xe8TmsQT37VxbUz/iOjUXjlg73bd2+68veRTP2fj2vRrzq0P8'
        b'COqMXSLHjLuNaYwrMLPldVIyrC8ibVHKKuegf1w5Vc5Dv3wpu9xKaq2jqllSTrNNORPiNluX25AQD4VsEVtm6djVHCkfvdkRJYmL3qzQm/06lk2N0GaUv4BUqYi0bRXH'
        b'BBOukc9WY0xYjOLWiUukSJmY1SP9dMeYfrqRS1g9x4TVc02YOmcT18Dqn4JOzuo5E1g9lxG2N5Zyk95iOWNpaX+9YBElP7MjnqdejmLuKHIOvzftaO++1FaWm+ZyDvtd'
        b'r1C6NfVll9ByuwX/sa0/rdWv5Nx2SWJphW2Ve050UOMbQvvEtgX00q4Vgd20/2+clsnCSjqc54UleyTHvaVYIe3jZv7CnvqYdqltkwv5T7A+5Q50jpEG/SYbce49kXzK'
        b'CZziNIWD40+wEmgLtiC2kzauA3Eo+yiOFWxe/MQLRc/keOXD1gKk7gnBcQ2fsgY72Wvh9ibC7eApeDQAy4r8XHCeovgpnFi2N2gBh0nWJHgEhVuLkZrHpXjwSKqIBV+v'
        b'BJ1M1sEysC9SlIMibcBWHmUNr7JBM+iZIuRNTvc8I3si5D5qXVEhV8o1FRVNTgxliI0AwoBWMAzokYZNRcVcnN4/fdBTH5mhdw5v5+6371o5IvDqzO/IvycI0QtCelYO'
        b'C2IHMvSCxHbWiH/gsVXdq/oC+2K76lFauxG/qejH9r6bpyFPD/cDQcgjDiXwUrmNjXX+KFctU1SPcrGVMWrVKFOpkUGiwoJY5TFWBT4euivw4GWGbAAesk+jvxSnTECP'
        b'v26hvlGzWayA5xivjzHR7ecHUyfsojlVbEujpHJslDBjpJpNRgjbTBni2JipOqajBY0F9iaOYYQ8BZ3c5Bj7vMkI0UbgCHhiph2xL3YjnQ/uKclhKG7+PKwbrQSD1EzY'
        b'y3eBfWz52eq/s9UzUJ6/hx85/F4CGju9+2LR6Nkf6/HlgRi4FikS9mUKe/uz3gH/HZr9hVeP2KNg+ZLPuyqPNix/y/6IiDq/xzbxhd8IuU+wGkSDwc1G6ubX5jHEzXJ6'
        b'QqyIHVbwNXgF7ohxQ7J2j1jUQGQym/LZxAUvwS5wkxD5xixwE9kaXcVjZI6IHF5KfIJrug5ers4HFzcUi1gUu5GVAQZchGwTesadYyRmJBdqZBq5RlaH6Nl1jCDGYISk'
        b'kwwknYVpr0tzbH33er1bxAOfkKHQtMFSfWjGsE/mkCBzxNO3s6mjqXNTx6Ye6bBn5JBzpAmh8lS4fqNcpaRO9jR58gh5jlFnFKZOC8hUGQn0+y3U17M5LJbX8xLoXn4g'
        b'9YqdiPO/zMZ/HJFG4lbJg91mRAqOgvNmhMpQKbhSK3847RMOodJwdgHD4SdQ6Y0Xx+n0Z0WhPTM8CjYeRRrw5b1b4x2ov79o8+nmRiGHYZXbo5PGqJTKAIcImdaCi08w'
        b'8wDHcxWYTI1EOgf0m9CpH+wkZBrrD98ArZnwdTMy3Zon5DzNYzmEJseJUm2BKNVmRBlrIMqiHyDKIMR4O207bLsS7jjTpoyT0KNKhD/Ia5QotBOo8mmmmWBOlmPo1FIm'
        b'fLMQkeXU5yBLFTJcKcv8kpAjZ4xfYnOSqub+D/DMmqfJkTeBHHlFWtxSSzNWY/9JKdSJROL5OXllUFdcEk7stBxktYlZlAb1+PkXbPjgAEcrRDnipD6WmWwY3D5OvrCl'
        b'Rt55YRNbLUVZVvuDw+/FERvu+r5L++SJbhwvgbozJm5Whu3vV4bf2HFpn/6lgIW7t/Ye7N3euy+kdQeLg2g8/hvrAwNAG7/yuw9iSi/FxtDvr2B9JoV3u3+6Q/grm2uH'
        b'O3oRkXOov/63y6ppqQbTKnYZbMemDzjvarB+jJaPL7xJLJ9SeKIEDwM07k4xQ4GMA9AG9zMMe1/jWtOBQCyoTjBo5Ni35pFiQAs8Ca8gtQS0gwOmg+HVjWSkBIPeNKSX'
        b'wGMziXuK0UuswNYf1EvG1PBRvrYBW0lNDgYKZV7JWFnEjJUvF3Mor8Ce4D7uXU/RA2xazBz2mTUkmPXrKXR7FmLfPQmn03vT73iKH/gLhyJm3BboI+YM+2cPeWU/4lF+'
        b'AY/4lIs7Hkv3nAP0zgE9wR84h5mMKCtmRAXhh/lQMkHaijKweqP1MB2PKnOc66hxPv/toufk88yAMvXOmCsgHOKdId4zA2/H3hjO/5w3ZiJv5xTJe0unM8RuX6bEvDrg'
        b'pYCjHYjgT+4TIY59rrp5qOycvf2Rv75qPyuxoGvl5cWXPn3xjtj+0hl7+9hZy19te7Vg5M/vVL4tOCtpvr/s58tgKZwHFRzpt31XYqgP3yvnrFkUw6nhU21rXJbH3kJ6'
        b'B+Hoe8FVeNDA0/0qjaS8cj6hwMQN4BJRm8FL4OAYfZbGEZXFFfYnw9aoXLhr1RwRn+K/wA4CnXAvUeUjwHXiN0PqONzSwGjkbG+4D+5BFPEjzEpMETRtomAjo1WtUSHW'
        b'7zjOa/G7mXpdy6F8p3Z59Ab1SE+v6l01HBin945r548EhZ1O6027FxSvD4r/VVBiR357VlfIiNeUY3bddve8hHovYV/wsFd0ewYythkbG5F2cNKXfMorpGfhsGfUkHPU'
        b'RCkxKTkTGWFCzVmYmp/CW2skZ2QMf1ODyNn1ecgZuyYRSX32d0TSQgdsfWANCpn0thUVzHQECttXVKzWShRMDCPTrKvQSKqpV60btTYYBWpVMOET1XKZQqomNgBRtYhg'
        b'I+OQoP9DLMfE8sd002Swj0twfCLunWbqoZunDvMTXc6Ipzd6ePjo5o64e+qyv+byHUKfOHMcop7YchyE39jyHcK/deY5iEiTEych2BatsEuAN/IK4e7oPBZlbc9eAV6J'
        b'mCCf8N/jBXhEs55yAbDLuVKOlCvlHWGX89jUImqAkvJXOlAT/qRWxkkh42+51Tprxuifo0TSfd33gixZpVxTr5Ipo/NVMikT/MyZ9MlneEB/77pQpmrS1qgbJFp1Va1E'
        b'IaPjURTG8Hv7ApmmSSOjs1VytaafrZqDgJ/9DJHx192uFJVfr9TUpxehLqPDM6QqmVqNOkypWddAlyk1MpVSVlsnUwrTTV7UNbIa9NRIlFKL+ZQSDbypUojpeajD61He'
        b'hfUq5Y9JZ6mwVTK5UkZnKGsklTJhullcer5W1VQpa5LJq2qVWmVN+pwyUQFGCv2WlWhEudIilTg9Q4kaTJZeipQkRXTGKolUTM9VSaSoKJlCjVUnBfmuUt1Yr0IlNxm/'
        b'odKkl2hUEnhMlj6vXq2pllTVkoBCJtc0SWoV6cUoBfkcank1+m3SmmQ3vlSuwdhhnxRtQASBxHS5Vo0+rDBBno6dNCYuPV+mVDaJ6fx6FSq7oR6VpmySkO/IDN+T0XPh'
        b'TYVGXkM31isnwCrl6vRSmUJWjeIyZcjwWYXLDTeAhMY4eq4M0Q48Ua1R41riJp2Ymp5bIEyfIyqUyBWmsQxEmJ7L0InGNM4IE6ZnS9aaRqBXYXoJYgkISZlphBEmTM+U'
        b'KFcZmxy1EX41bzUMWYVpWFSkrUMFIFABPIGdgKtwqzHNj4C5mRlFOE4mU1UjxoOCJYtys0tFs+tR3xgan4wFubIW0Roux9DsORJtg0aEv4M4WKXY8E1D2KzdLcFx25tV'
        b'Im5CJeImViLOUiXimErEjVcizrQScRYqETdZJeJMkI2bpBJxk1cifkIl4idWIt5SJeKZSsSPVyLetBLxFioRP1kl4k2QjZ+kEvGTVyJhQiUSJlYiwVIlEphKJIxXIsG0'
        b'EgkWKpEwWSUSTJBNmKQSCZNXInFCJRInViLRUiUSmUokjlci0bQSiRYqkThZJRJNkE2cpBKJZpUYH4hoPKnksmoJwx/nqrTwWHW9qg4x5nwtZnVKUgfEjWXIODa+NKgQ'
        b'Q0bcT6luUMmqahsQv1YiOOLFGpVMg1Og+EqZRFWJGgq9Zsmx+iETMeIuQ6vGAqUJqSDpi+CJWhVqN7WafABzPUbGKuR1cg0dbhC9wvRy1Nw4XSWKVNbgdNnwhEIhr0Ey'
        b'SkPLlXSpBMlFkwwlpA9wzDwyjWRa2LgYF5UjLBDDCMfZzSIM+VFUyMQMcZNniLOYIZ7OVGk1KHpiPhKfMHmBCRYLTJw8QyLJUChh5DJpc6SXIP2EwDSytZqxAOJEY8F4'
        b'06TqsWRMR2TKkDiuMQGEpJfLlag3cP+T7+CoJgTCohdxabPXOPNXxH4kag2Sdip5tQZTTbWkFuGPEimlEoSMshKR7ViPa1TwRA0iolylVN4oprMZ+WH6Fmf2Fm/2lmD2'
        b'lmj2lmT2lmz2lmL2lmr+9RjzV3NsYs3RiTXHJ9YcodhEC2oKHb7A0Kpqg6IhHFeMLEUadCVLUUb1abK4MVZmIb7Y8tew3mUJbqaKTV6HZ8RPpp09T+K4yb9spqf9mGSI'
        b'VVpKZiYCkiaIgKSJIiDJkghIYkRA0jg3TjIVAUkWREDSZCIgyYTVJ00iApIml2PJEyqRPLESyZYqkcxUInm8EsmmlUi2UInkySqRbIJs8iSVSJ68EikTKpEysRIpliqR'
        b'wlQiZbwSKaaVSLFQiZTJKpFigmzKJJVImbwSqRMqkTqxEqmWKpHKVCJ1vBKpppVItVCJ1MkqkWqCbOoklUidvBKIQU6wFWIsGAsxFq2FGIO5EGOipsSYGQwxliyGmElN'
        b'hhhT2yBmMqMhxqw+BhSzVbI6qXod4jJ1iG+r6xWNSJNIL5kzL0NEpJVGrZJVIyGoxDLPIjjOMjjeMjjBMjjRMjjJMjjZMjjFMjh1kurEYIa+SglvNlRrZGq6eF5xiUGB'
        b'w8Jc3SBD9jCjTI4LcxOoUXybgObKKuFNLOmfUhtqGLhBazC+xZm9xafPMzhXTDJPcLvETgTFTQQhM0eBjWKJBuuldIkWFSepkyExKtFo1VitZWpD10mUWiRe6BoZQ6ZI'
        b'HFpyAwhNssixcJdLSbYfTGyhfAtCyXLZExMSF9N469BI+aYNKi9pymocb2hkJhxnEsY24binapSVXtRvrcrGHr65+JFDGSbKVLn4kYe9iDx1g0KuUeVjTxiLcQ5iH5rB'
        b'MVhIHIOMD20jjks3OgaF2DHorct5xKc8okfcw7+04no56nK+sqU8fB9xY1xms76tZFFOgh2y9tmtKx/XsOI9fHZkM+5B7G2eBw6DW2p4ZAleD7cjCvRzKesk9ibQo/0/'
        b'6CFsFtqM2mZUVdVrUQ2VNaOOmYiMGEtG0iBTfObO+AexB/l7nyxEWHVIW8EeYZqxpdCwkCNmhpLgFamjXKxVqUpR8OubCFBWxyhJ9bVKGV1Sr1BE5yAupxTlN2Gfzfjr'
        b'ON9MX5RfTjPZsG8Oc2S1XK1lADjO9J0Zx3OxK5GxGZgPZZaJSqpqFfAmoicF0nNMX9MzZQpZjRRXhAkaHDnj4TiDzZVubAliQ2AlU2ZgF0ZDkGYULYM5Oe74MhiSRP3H'
        b'JiRKjAashpgahhLI5xRylICE5MrqelpEZ6g0RlQMkFwlzvkUECeLs5QsbkKyeEvJ4ickS7CULGFCskRLyRInJEuylCxpQrJkS8mSJyRLsZQM6S3FJaWxCJDPdAzWn2UE'
        b'GDcBiF7oQhniwUbvLq0V0+PeXQRkaNnobhXT2AYwWvKMG3e8G+mCyIL0bK1yFdkuIVPVIKbXhBkVhmeW0QmpjOiuNibBbmZLcAPdMFEWCkwvJyYGrriqToIjx0jEUswY'
        b'qUyWLe5Z2SxHMiT0jGyWIxmSekY2y5EMiT0jm+VIhuSekc1yJEOCz8hmOZIhyWdksxyJs6U+K5vlSNLdMc/sb8uxJOOzCWVySol9JqlMEksyPpNYJoklGZ9JLpPEkozP'
        b'JJhJYknGZ5LMJLEk4zOJZpJYkvGZZDNJLMn4TMKZJJaM+GdSDoot0cCbVauQ6FqDhK+GKLtrZHK1LD0bifhx7ofYoUSpkGB/pXqlpFaFSq2RoRRKGVa0xh2YBsmJGV6G'
        b'thq72saYnFGWoijMeccFMh2eoWxilGw8R4iYcaFcg0SjTIo0EInmqein+PDEzOOc/Ok4lQK+pjaoCWYxOWTGqFqDtJIxU41IEhHRdyzaFYaaGqQ5Ev1I0mC1vJoo5HVY'
        b'wGtkctQsmjHfcy7SnjXyavkqiSn3Lyem5ZhP2lTNYAxSk7lJUzUpW8ZYKzJ5JY4qQL2GJ9vUjGYzuaJm6m9GeKMvSxTaulWyWqNznAhBosXhpTZFqsWW1WK8wrbJRHG8'
        b'ieNTjKpxkIlqnDziTpurxl4u076NG1eMk33H9WK8iQMOgDNh6oIiuDuaaMawLd+KcoeHN1Vy7ZcuMNON7Y26MZ+NdGOBuW5MtGE++meH/0nZ6OmG/2F9+RzvrBWT1Qb9'
        b'J6V1PJ2Dzo0sl7cxroYp5+INmVLrZkpqc872rGFhWzmfQO0Q1N4EakWgDgjqaAK1JlAnBHU2gdoQqAuCuppAbQnUDUEFJlA7AnVHUA8TqD3Gt5ot9Wy2Lncwq6fbD/yz'
        b'Oed11tak5gE6tqHuXKm3Sd0dzVsP/bNF/1jVxla0GguZl+5z1sZYujRQxyz2w7v5nNEXrKS+Jl9wkgaheJ7Omuz3cyXxU5ptyp0RzAXVzQ/VzWUMC7dz/ka7xbBj0FHn'
        b'VM2TTm22HivRdR0f2TPBo9ZZeIvN7JKF30fb0iZ/RjDNMENml6tZin6eah6mbmxqfYYXxKhewCG83pYYNUL7zzASn+F++Awv9BxPrqoxJlfhVZSqFTgJbunP8Ja6zzCl'
        b'Cq1GbSXSRsRfVRVy6ahNFeJySg0OOkqYgVShQGqqpnbUukqLGICyat2oNV7QLpcoDCte7KrlSDOtqEPMp7aoytpkKOBPkbVZmyjjWkvTrbdkGx8LdTZXZ4Uaj9nEx6+2'
        b'JcvGEJnusB1bNmZDlo1ZmywbszFZIGa9ycawbOwpqOkazK/3ocYxa1n8l8tURd4kU5MNymP9IScrQapk4glZJgDSkHElqaPHmzHNsDUZMVDsPzPsfTa0p0SpmVAC/gvP'
        b'RHxPY+S6QjGdgfMjDllFk/WztLaBRnIimZbKa+Qa9US8DGiM9aBlLJhoyxiMzRL9AA6JP4SDOemk0QXkF6MwN7rAGGtATG0ZFyxVsTxD0lBMl9YiCYdGiIxWaysVMmkN'
        b'qs+PKoVZgsOY4qgkWoKKQO8M/rSiHklblZjO1dB1WmSQVcosliIxVL5Splkjw7PkdLhUVi3RKjRCsjM9ZfK+MAyZNHq2IURXYTdr+NjkrIl7VjhZKcbhlmakVvVYZ+KN'
        b'8PUqOpxZ6rMK3lQ1yRSTFmRYqZZGbEmsd6FiGBoxcJ9wWY2YToyNiaKTY2MmLcZkvKfR2fiFJi+4uGq5Eo0ahCO9TiZBiEUoZWvwTHFjkjhBHBshnNhUP7A02p7ZcPVK'
        b'igtFU1RKg6ouavWcSEo7DTMvYT5sLQTn5kFdLtyVHw13zMMrpnMKhLA1qkgEdsI9BfNzwPmcosLC3EIWBTtAj70GHqiHB5aRUtuiHSgvigp/yFYpPkxPprR4ff8i0A5O'
        b'WSwX7oY7CpD8BzvGCwbbypmym9fZUy7gIilXssyaQtpJTEOerMDT04HZbz/fZa7pFtwcsSgiD5W+BtwAF7hU0jK+Gh4HOrKTmBTys818rEw4r1i4SXGzsITS4m1/cCd8'
        b'k7KEHNTBtlLQjSqOcWwTLjSpN7iusgOXUemn5C8KRSx1DyroveKwjXtiHUGM/Zy60/37Shv8xLenvy4N+HALa+FPfsehHfX5e3MGbR3OnAz//rtvNn8ZeTPj5iPr8m1L'
        b'eiPYnz1eve3xt4Vf6IZdHk5bdv6b7AVfbM1M/WmC8O6JrtCTZxcUfDV099zMP6zujuB+JPi7JvLdohb3/os532z3zPz8Xd2RxsNZL7h865t17/P/jKzMVf8xp/ODy3/q'
        b'X/vRXIczf3l4bOrD30SlPmkR2pMl5I5wnxS0KsEN071sTiGcatABusheiUzUqB2gtdi001mUDzhdB1/kNoEDa0g5cBt4dYkdavpp6cJC41p0d9DCtYaHYp5MRSniV4Cz'
        b'qBi4ex08adLNLMojgGsXHUgW6sKb1msiReE58DR4WcSm+OAQW5QAD5L8m+GFmSi/oVdBMziEu9UVXODAVqATPMFey7lVGyLFQtSHR+koCmU/x45fuvIJomtq5hp4ErTi'
        b'DcDGHgTNEUI+5drIAW/YwmNP8Gp/eBj0g05cV6Mi+hq4hLE0EAKiOPgSXyyLeYJXiathuxJXqDUqQowTwV1wTyRORKt58Dx8w2HTOrJBWZ4cgZMRhy/6shUYEKHvgk4O'
        b'fAn0RJKi4M3AGNPPMvqvD6KpdjDIBa0c2C+0/Sf2vGIF4en9rmTznItRDpvv/tNTzPLkRisqAO/4cxgJErVz7zrT9908OtRdafs2D7uF9QXccYt84BM8FJIz7JM7JMgd'
        b'CYxEaZ2YNKn7Ng27hfa53MG7WVCaucM+OUOCnJEA4Wn/Xv/hgFiU1BElbdfgnVY46VhxycM+KUOClJHAiFfEfZX3ApL1AcnDAakTMoyVnT3sM3dIMPdhWCJGMngkOBr/'
        b'BowEBOE8I0Eh7dwPzHbNODDroevxowE/VuMHPvZApcYPrG+pNNSzlkxjN/sKw5/JyulJWvUznAWz0n+gZv222IrFqmJ9TeHn824m7uHHIJ08nWO2N4BlZOdTCDvfQK2k'
        b'Jv6VUDbVQlaRkDVqVzGuQyH7DrcFse9ow9bQaQpJXaVUMsOkIkaQC8tITlRX6T0/0R0/ZtHz9wYBZyjYqAyFI8EpFdUrFeuE/axRjrS+6l/B27ZiTOmaiLZqu3nTGzEW'
        b'oCRk1xzG+FjFoQoG36kMvkyBFtD9V/B0qjBXzH48sp7mzRt7xy+WQVf4TNXuX0a8hkHcpsKoSf14lH3M2veFQy8wCHtnStSyMcXsX0aw2YigUUn78Qj6oSSqfTgBQSxo'
        b'UuXu39P51hUG9e/HY0jjXh9rwuWHlhswnVR9/Pdgal9homH+eGyDcIeP06j4jp/YQKM/oKNOgvXYzqIV6HGAbdjYZNxX/e/d1vQjtqxyiuQ/3/kiV403Vx/wKMAbpbfu'
        b'+G6/cRsq3tQ0z71gsKyUtTqGU2NHJXzH/4h/V8gmygkcFMGLplIeiXgl3MtI+cQ4okiVaeE1GTxlSc5jGZ+jnnSbs1UFZigVFU3OJgKGQIjUxlvG8P64PBvKy7cr4diM'
        b'7hnDnhH9JQOCe7EZ+tiMYVGm3jNzyDlzwn5mS2KO2c6MRRtDDccxNUz4cChrfFfQ17k2z7criLCNDn4A1WsXxRHajloZ2Bqz9Yev1qhkMs2odUO9WoPNuVFulVyzbtSK'
        b'SbNulN8oIR4UuypkVNbXMZ4VjkZSM8qrRwNbVWVn0tGOxo5uw/3KtXw8GaI8B8MeVWudk46ts8WUqHPWcXQ2OqtqR0KRdogiHcco0p5QpJ0JRdqb0J7dJnsDRT4FNfOY'
        b'fMiz4DHJkErVyCTGdp1UVokZFPq/yrBUlpaRRQk/wmlCTHpij0voWm2NzMRNgdpVLUdmPs1spcIeB7VMI6aL0RCdUA7mlHV4NlVe11Cvwt4VY7YqiRKZ7DgrMvdVsiqN'
        b'Yh1duQ5nmFCIpFEiV0jwJ4mFixdaq8W4pnLsF0eMwlCkwUuAy5xQBipaq5YrawhGY8XQEaTLI35Ei2QbaluL3YATcZ+QPlwjUdWgb0iNTBjnp7GnX40tbvVqLW7dSpWk'
        b'apVMoxam/XhHFkPtaXSGmTSnl5K1Dcsny4a/nEaTzU5Lf3DL06SlMIMrjS4hv/RSwwLcSdMbB2EajecpUFcRB8tS0wW4k+bFwzaNno2e9NJilWbydMzARkmZAPlGFJ1b'
        b'UiyKj01KopfiuYlJczPcII1emFEqys2ilxom/JdHLjXd0DX5x8eZCHYjMS80Lsh0G8Gk2RHbQY1Zi4YGGq7qKpW8QWMQ3ZhO8bEmZGxlKNT1iH5lUoseMEROODUWnApy'
        b'xCLpbDGdxbjByBANLNFI6urwBmNl4KQOMTIYEGEhBBoMQ0sqJ4c8SlCzrpEjAS1bi3rcMOAmloP/iuo1MmaYkMEv09TWSxEnqdHWIUJDuEhWoQGIBo0MtU6VjK5Heo/F'
        b'cpgq4UFD/HtqpppytQlKYjobMTUjQ7JYiumww95AROr4CMsqBaowc3qlWmY55wrDAZb1VQRzZip0Wq1G06BOi45es2YNcy6XWCqLlioVsrX1ddGMWRAtaWiIlqPOXyuu'
        b'1dQpgqKNRUTHxsTEx8XFRmfFpsTEJiTEJKTEJ8TGJCbHp85YUfHcvjfXIubsxT3I0D+hLhDmicRFeJdyJOiPoqzhfiq4hFcLd4OXyHl18S7gZDxSNa5upmKp2HRwlnix'
        b'Nm3iUtbUQ671rBUF10LKKS2ekHNfOC/fqGTMhzp89FqeaAE+cGNBON7svwifRwk6cBDpH2AvuGgDDwSD61qy0bpnZhO8AnfDPf5xSEWxoniwm22/AV4k5z8u2lgEr4jh'
        b'rvxcfC4CKjkUtuGT3djUVHCSC1+Hr4Ej2lm4mFuL4MvwSj5sKyyD7Q3mtZsHdWmwtwgV0ZZf1oAexQV58ACXgjvBNjt4AmyF17R4e240PFNsJxbmgZvgmC1lA5rz8tjw'
        b'mKqC7LXNi1gNr+SizCyKA7alg04W2AJfL9dij4oDvA6P2EFdtBjuQN+MAv0OUJeHUNWxKHouj7sUvMicqnkCHAM7YddSeCU6gkWxc1hJ8A0uaVlVsRVlT9V6ONEr7F/g'
        b'L6XIOZqgXwF2qh3gAfgq+TLsVFHWy9hzwf4Cpi+v2vjiaAcHMeyArxZYwwvwUiTcy6E813HAObgvjcx3BrK87cS5pOVyo3LBdnAA7uJQ7vA61wkep+TyZB1LfR1XMelB'
        b'3VC+47YYZ2qo+yD7DyUP/rhkWdP+3IKGFvHdWZVt35w4nLrlS+dldyT0YF/h6K2izcO3oJX9gOSXMrvV3v/xwGmI89HCJw3S0C9+ejl+X/klv9VL3nyiOrSjOGh95zca'
        b'6lPw0/P65j9P/9ufNwYuvf5WYXJDRF7Z9fCSD15Z9oesF8p0tmWBEWWF1z7avuXMh/s3Tn+7L3Bo9dDqwd/dp+fF93x85Gep12bs/nrtss2nRP94/2J9xuDWzRtZX3wb'
        b'OecfHoaTtFCH9G8GrdH5YHe5uX9RPu8JdtpmwTfgzTFaNfO1RYbB9nge3ANOeJCySuHV6djDaPAvzgGdRhdj6lKihHvCLRuf0sFdwY5aooPDk1XEGQfPwt0lkUWi3NzC'
        b'/Cg0Bo7NFbIoD3iTGwfOgB5ylAB8PdknPyo8B+HBoqzV4BA4y14HOsuFzv/KMYEW/XP4YXYk3dgpArYSqbSCUfaa3MaU73EgUfw/NSj+BbaUD93D69Gc3ti7cdg7sZ0/'
        b'4ubdFa13ixhyixsRx7Znd83UCyIZB13yvg3DbsE9mnthafqwtMH5+rAZd9xmEH/a7Ns1+pDCYZ+iIUHRSKCwnd++psNpRJiAApv0zqEjMzLb+UOeaXrn9JHgCARcp8fO'
        b'tnAUauxwHBHGGtPRwSik7XC47+Y9Ei7uUw2w+vCxg6l6QciIKH4gYyCzrxy9z9ALIkY8vO94CLuWtXNGnAWdjh2O95yFemdhX1Cfatg57p5zqt45dTD0A+cME9vFhbFd'
        b'TlLGdb2n8OM0fvThRz9+nMEPrHurzuHH+UmsHZPOwO2+YvyPHj+cRHUN20CWukGIzaBMFPuPv2L/ng327H1L/HtfPreXD0+in+YnU9fsMtgcoc2ovRSvgDYoi6MOjAlg'
        b'fOVL6sgvPjhNNmpjWKNSJRu1wwobUpPxClamEcbqX2VrIo2cjdJoN7aLrCzZRZ3k0FdkA+EZZBY5mtdG54JsJHx0LzmmudqZWEa2ZpaRHbGMbE0sIzsTG8h2k53BMnoK'
        b'anoEydd7rJ5tGUnGFqHQzJGNP0L/n4P3kjGpaaSEoE5Eqj1SrCSmB11j5SuKrlHVaxtQLLI5JBOFen1dpVwpMap5EUgDjCD6CaOeYM/S2OJ5jOCYO2RCSdg98v9Muf8/'
        b'm3KmQzQNdxQDGfPT/oBJZzammfwMyFiARb126Q+sfp/0cwzPYL5jYBMGGGMaKOuxF09FlH+lZZV+TT3WveV1EsUkxsPSZ6z/RyaZ5R0Ak2KMuRuDb2V9/SqML4aI6UID'
        b'dUnIO11fuRJ1PF1v2Q5BBIJMyZSkmFiDIxUTArKDcXFLx/cGTIrEGHNNo8vUWolCQUYGIpzGennV2GhcarK14JnWtIE5m3cD2ce81HT7wQ/auzj7Uzav2SL3/wtM1kzZ'
        b'GlmNYYni/zNb/y8wW+OTYuJSUmLi4xPiE+OTkhJjLZqt+O/Ztix/gi1LM+tI1hfxkDlqvd5+1grF7+WelBb7iOF5eAvuzM8thDujcsfsUnNzlDFFX/DcDN6wSQCDnsQU'
        b'XVkCLjKmKDZEYVsSY4suStYmo9i58FXQly/OK8Q7qW7B1mcXDVphqw043bCOsU53JYBT4MYidXFhseGAP/yNRbAdZdgDdcgqtUVWHCoQvV8vWQaOIDvguA0FzsKDdkXi'
        b'Gi1e9OC8QKLOg7tyC4vz8aGAMVyKNd8rk4OtTGQEYyW1HLSCcyjnOXVEIdwdjk0bcS44H86iptbweKAL7tNiywUch/2g3w5eA7sXWMNdoiJkr7KpxWtd4zmgd3MAWd4S'
        b'1DgdNYVheUsZuFIwH58DDF5dgI+YjwWtvLXwDbBfS+PiDqfAawbMcqOE+MD6cnBUAI9z4A1kSetIT30xBd9Z0edlRa1Q/ClZQzGH0w+Aq+CEHZ+av4kqRRbXSx5afHxq'
        b'7jRw2Q43EWrLDngtBxnru+A++Co24FvBWfRWAHfnYBMWbAOty7yt5yKT9jWtAJfYDgfgdniFokTgNSqXyoWnlcyndCvh0Xj0ey4E+zM8wJtaTFGwD74cC/ehkk7Pwufy'
        b'O4Ajiv/6xz/+EViFCasv32rWigLJygLDEp5GbKI/VDsiE30wMYDSYlXcaQa8CHcE4XbaZXCA5EQtxB6P6LwyRBQ5sK0kXIhII2fsvg0heI00I1/psBz0RjFukL5N4GoJ'
        b'PBCfB5pBP4diwXMUPAfbFpGlUaDXrdjO0FMO0gXjZGNtoZnABbiXS4GWMpslQAcPavGxZbAtZKPaoQxcN7oS5ofDAyXWBreBwWcw053vuBJ2avH0UYQfR50nKo6GbxZG'
        b'YzoqysXOFA4lhF08cBVejSAOEwloD47Mm+ZCjh8T8ik78CYbXlFlkMsjWsqL2T/hU2sHcuvsbZd/9sIqZpnXdOuV8Ar2EYGzznmiBcxSLERkcEd0ceH8cOYoM7MFT/Ao'
        b'OG2P6nzUh3zUBuytjRTnRkWwwJvgVYoP9rCjQT98nVyo4Axb3FVgaz4xp9kqVgo4Cd4Qckgbg95s2GrIeRi0GHK+CHtJzlCwBeyZCprHs8KTDiRfHTgHX4vMi6LMqylf'
        b'Kn8Q/nu2uhFZZe++terkgunFMMb51aPFYYWHTglDBKHZf898++/22a15O37SvtA6okaS3vgTMPPTYx9/fre3H2ad+Mkn69d88fKxx90bXbJvv8itdr90LOhPv1pYVvjo'
        b'PwLS7rg1ll/ad//oNv9HS+ut5XfeuFfjnWX1j2vfHs0M3tHwK69v3cDmwoaAm13Ov+MWF26xD6qYW9K2zfM77dt//vUD3fawwtiGd3Y5Feq6BYOSfzy8vean9zUXiod+'
        b'75mX8lV200r6dz6pvhUFMZ19D66ELXBbdfC2ZuGGj5+UvPhaqXTvrfb/zEgNl7vvKa05Vf7+e/E1c5TfJXdq+pqOedl/t3H+rIbdh90PRD95d+fPXmSvWdT09tm7C4fj'
        b'3q9p9P8i8NqV0bDiuJtf5Hz7i4rPds8PPPj7z/dOTz0f5CeNVAg2jrYF3Zn/i6sXGvXu9zjH3vvepewnf5V9MfwfD19Yfili18I3f/2n9DfufXn+Z/uHzyovXuL9fcmG'
        b'/J98eG349Tt/yz9wJrHpjOrEK4ty3/X96NdTSxartFZfCR0Yt0//In/s9Rl3+YBty8mqsr0bidsHbN2wmHh94EuwZ6Lnh7h9TrLIyjL1ImcTr080GzEG+CZx+4C2HHKE'
        b'IzwFO2PzjQvDLnApeJLntJCjSHEi/pwsuB/cgCezIiPw0jA09myWsMHJhllM3sOw1zNSjKVEFCsRtCIS3M0WgW647QnDpBJn2oHL+QURfIq9nJWs8HiC/QdhiKd1grMF'
        b'hVFzNiMums8Cl+Gx2cxRqTd9QAeSJ4bFYGDLHIq/gR0GjoPOJ3iidgPogy2gm1kLZ2npmIMD3E+WrBWDE44TJ4uTQ5jpYq8pxOe1ngMuqfHAFGFxh5oa3orgUC6wnQMG'
        b'rEAbaQBwGQ3G0/5R404t7NFaP1Xo/u92aE3u6cLjmagRW7ZYcnc5YpfKuFHf5GnmaxmPIG6v6WzG7bXJjvIJ7pnTl4DPqR/2Tm3nMx6uacOe4cNuwr6se1Ez9VEzbwfo'
        b'o2bfcZtNXFwZtwv0IfOGfeYPCeaPBIoZFxeTbfqwp3DYLaKv9J5oll4063asXpR1xy2LZMu8vVwfsmDYp2RIUDIyLRe7wVL0zqkj4djntVHvHGLiJQuLxG449LZB7xx8'
        b'382vS9oz+65b+H3f8D7BsK+4Peu+py+z3u160KD0hlAfYrgZA+U05MLuu4y9aSPJae3ZQ77xdwQJDw1BvSDhvh/d43F46T2/aL1f9ABn2C+h3XbEzaMrQu8W3O/WV35P'
        b'NF0vmj5YNSzKvB2nF2UPC+e+E3BHmE++WfBOkz5kybBP+ZCg/EFK+vW5t7PfWfhW8fC00uGUMlytBL1zIvbbJabj78XqBXEPA0JOe/d6tzuOuHl2pnWk9XDv0bF6OvaO'
        b'W+xISPyARB+S3F404ulzx1M85C8e4F6zuWQzOGPII6+dg9EKvucToUf/u0WM+Afe8xfr/cV9ar1/fPvc+54+Xck9qXpf0bCneCDkjmfyA/+wofCCYf/CIa/Ch56+XTU9'
        b'NSg5KngkMrrLqsfqjlf4iLdfj1Ufr9fxjrd4RChCUN4hx4fhUQOltyv1/rntc0ei4tuz7gmC9YLgnhK9QDji7Nllo3cONDgWQz9wjjXxJboxvsRB/MAOd9Xr+HEDP/D2'
        b'JtUblNGX+CPdiE8TPv7U007FMb/iL9BjUlovH/Mt4oOEV9uyWHLiW5SzHpPn8/oW+/gp1KBdBodTZTxeAP+NXf7URJn7ATspnZXORscl1z+xdfbkdhEHHctwCRSPTe0Y'
        b'2y+ykU98fjwTnx/fxLvH28Q3+Pyegk6+PmeigeHIGBgnSznUp+7kMhf7FYpUqpRAHzlzqXfyye1aBf8ZkcGcxQp7GsFxNdhlvZpDcRzBhflI9zgID5P5oU3rwaslYFcp'
        b'3FVWOB++Og++WuYQAw8nxcRQlJ8nB2xd5URUfLAVHIU3SuCu0sQYuDMBqfjWq8HLa1iwB5zKY/TEzgIpuOBoLIxF8ZAyc2gjPMOov+et4RVwBVVnmhypRtPAXnCemXi6'
        b'KAJb4HF4kk3B3tVUKOWFXo4SvJfCXeCEEFzNF8ckxCWyKf4mFnh51WpygATcSYEDhsuSkpYVGe9Kghez5PZ/28xSI8uCWvrKb3eV/LwIqT4PtK7JF/k7nfcstD7xd9vN'
        b't7t/vTMv+3ftbmc+9/XMX9Y0a0PWT2ZefulqxP3COcE//8Xnv/h8bd3m0mPO6hb61oVjHC9d2Tmbi99FF6U9br3WuvZ3bR/zpNPKGmaHBkerndJaVx/lBWz5+ZehSb94'
        b'79P4yFe75+b96g8Lq3j7le1qdffP175ptch/16/mHt/l8QfHA59vDq3ar91Yv+YxXx4z8kV3+ZXVn1R98E7T3fVfSX/1zYBPzfLaiBnrfvqN67XTS7/aIf9N2J2/Tl34'
        b'ZcXCI3/7r0GfryXO4amLj1++4LK46oLcPv3MrmjfO+7N79f8JXvlo02nZvilzR26IlxzzfXD33ake+9779KtlrlFTo139f3X9n57K2er7flbv/1t4rXSaZ2lf/7NXziC'
        b'+t+mNEkLrYuErsyi81a4H6kh+Oo0K4otBm3gFVYZW0IEPWxeVEnkPJby4FwuEvSg2Y6cRw1ehy3lY4J+A1J7sJyHA9Of4GnSzUuQ5WeQ8PAC0peflvKb4QCzcH6nAu42'
        b'15WcQqxAD6cakS8zZXUIXAPX8ouikLmyJxqc4VKO4Ba4AG5wKhLBADNltQUrUK355OY/rv8asIsFXoGXnRkVZxCetDdeZ7MAjQDDbTXesYyutqMRnDS5YAvfrgWu+3Lq'
        b'4YWFzBnxLyNAa775+n9E/zoPcJ7ri8yVK0yyV+DOVfl4CweykY+brO93XYknPnvBVqL/zAddrqbzfedfeFrxo8FxUm8luOKEN3SMbbngU07+8CQ8yHkBbheRPuAEwm2m'
        b'ip/Twhy4k6PY3MC0yrElHqBtsbnaA66JSWS9Cm/mGL8TzAp0sMAlqZSQhCcYTIuMG78/gpw07rKKfFNWDC6BY9OxUQJ3F+PT7kE7ux50VQld/wf1J1ej/jTxBqtRqwrm'
        b'9irTVXoMhKhLRxh16dFiB8pzaqeiQ7FP2c7BeklNj6R7ZV/EXbfEEV/6WFp3WnvWyJSAY/nd+e1zRnz8O2Y/9PU/ltKdgsFTj+V25xJw++wRN6+uhHu+UXrfqDtuUSO+'
        b'U3sCcKJHbNrHdUTg84iDfh8KvDoLOwof8VD4EZ9yn9KV0ZF3TxCmF4Q9ssIwawOss7ij+JENhtiOpQrVC0If2SHYl/aUu1cX55h9t/1QSNKwV/KwIOWRA07sSLl7P3LC'
        b'IWcccsEhVxxywyEBDrnjkAcKkU944jcv/FbUUfTIGxfugwu37ZFiRXG6Pmr6UMgMvdeMYcHMR7448RSU2ICxH373R8nvCFK7Z/fwyD1na4fplOEpqY+m4kiaRCajSM5p'
        b'+177vsXDdNLwlORHATgyEEU+CsKhYIwAbpcQ/BaK4HtzuzIeheG3cOObEL9FGN8i8VsUKV7YlXWssLvwkQiDxLiO0TgUg0OxOBSHQ/E4lIBDiTiUhEPJOJSCQ6k4lIZD'
        b'6Tg0DYem49AMFPpyJgq18x9lsihv33beQ2f3TvsO++7lfUnDfnF3neMNgK6SY4u7F/fU9El6V94LTdaHJg/7pdx1Tv29f0h79ojAu7Ogo6DXrWfhcd8PBKJHHGpq6ENP'
        b'v871Het7EpGOfc8zRu8ZM+A1mDrsOWfIeY6JNubIaGPnCFUzU3XqUZ5aI1FpRjmIop9P9XI0ql5PaV2/p8xXtDJj5TzLcOnb3/C1DQ4sVhS+9C3qeZe1vswXUxfsUjn/'
        b'm0udv//DBO8ts+1fY9yFa5gFUxic0yqZRqtSkrg6WoInWU183T9qgpJeJVunRuU0qGRqvLGCcaIbZgXUYzOjBo+6pYnFpydNFcxUBEancp1GZsHpb6YwWltQGMkVLrO0'
        b'MtAKD4I9YAe4tB4cgHvB5UVIjF8CZ+cDHY/yAls468EA7CX62lzQDM/AfUhDFoNB8DIlTgCvEBctvDB7EdElQesiETwIt2vzxWIOJQA7OKBfkU200JcdkZowDevaKwpm'
        b'cEOZI7/ANrhFbshpRXHBSbGEBTrBdnB6lFXBXDna4QLPMl4w7AELr2VH26qYW4FfBjq436hagktG7RK8qCRKpALc9B/zjsFuOJACr8ADRIlMAS2wD+mtZWBPJsrGRirB'
        b'lDzYTD64FJ6cC/fli8G1WagKnAzWenhqntwl5i2e+hKKThi2O9A+3ZYd65xdE7r5xl9sbm5fXN7EWcrryHgwJSPUarFz+iXn9BvL7nBf8ViSMfy+82+Cvzhst7y3hXrx'
        b'8bypF/94Y/EfXZPitySyuPYJi+tXHuzIjTm4aFtlyB9r1Z1/VydGr/5tuKD/Cb2y44/yC1eWP7724Wsjn63IuvJyNUf6uPUzh/s7JZ01G5Izk10qpL8bvfjgY7h6zbWM'
        b'+b+ofHvvF5esYp2m/T79u6LTonM906ex9myPcM6UCfnEF5IDu8hOxbEFQKvkYzvtxEDH6ATHUcfvZy4DIVeBrBWzg8CuqidEWT+zPj1SXMhGrdXHEsCb+RR8nehI8BXY'
        b'Go6UNKxn5IK9fiI2ZSdjwx54ArSRtf3wfEycia/GZprZ0n4lfIn4hqxmwG6iaTmAy+PKFqd+MzgttP7RqoD1mCowpgBI1BV4wJowNQOEKAAPKUYBWOBEuDoSxyHC00W9'
        b'RfeCU/TBKb8KTusoaJ/d5TkyNeBYY3fjUGjSIGewZHhqRnvOyNSovrX6qckoFBpxWtGrGIgftBoOndU+pyt8b/EjKyok/ZE9Ku1ecII+OOFecJo+OO1XwdMM5fn4dUm6'
        b'Q5Ea4eVzjN/NH5oaPeA2UPWBV9qI19QeK71X+D2vWL1X7ED4Xa90DOJ1O97zitZ7RQ/wP/BKfmTFpT3ac5BaEBbfI2U+rg/NHAxDD8P3naiQ6Ujqe/m12/9TWxu+MhcE'
        b'hjb72HRrwxyn57zw5ATK2M8a5TZINLVmF2ONWbR4c84BnuFiLHyqBb5lGV8oyB+7HGvMTP53XCj4EYdlYTHNuEDAvFktacQhhcJUNPz4oxlwZdPo3Go6AociaCRQ1cy0'
        b'LWb6srX4fBs8ixkhbpI3RESRDxmkj8ryJKganwsuHZt6laiqauWNMjFdjGeK18jVsjEJQ8ogFSDJJXR1vQKJ8x8QFxMvmbZm7lVE1vrLcZE5iH3My0E2R15hAehHpt7N'
        b'0hxwHuqixMgayIHbrRp8fUjyqoKZ+YjZ5BWK4Q5km5VCHUTD/XL0fGRyiMLx+Y758DUrcDBxJZkpmQo6EOdFBhL2Q3Nmg+MKFtgWD66RBb5gS4nrKnA2EuG2lloLr8Yz'
        b'0mEnvBUXWQFOFLMp1gJsDbaDg3Jhcxdb/QmKfk1L7Zp/yRbEOL+Rf2eloCMwcM7R/2ZbbZ6lafTQ2Dl6n+/JfH2Qt+ynez4tbhr5mW3syriP1377lw8//Lno1ot1Kx/t'
        b'+c8Z1bKtsqv1UwNbIjSf8jjluy6WB53Zu3lNVf2H5a//+Z77B4f3bftL8+PX//SJ4Ndum79eFjdw6UDeSF/fzXf0W4rATrsRRyqprSvqE772l5/4VK996z2vjw7Z0i/M'
        b'PLejwfFvQ7ffXvnLy81n7tTbNx/79ft/qntnV/aK3R+dFm+/Lir7+BXvj4H19G++236vpP+TjY9rA9550aYgAAbNXuyW/ekff3KvIev6eir196kHFvxc6MTY6q+As3ak'
        b'd5BSlQiak1ngghrsZTzvR8QB2EQ13HBvDfZi25G9MQDqiB1cYlOBpOPVNYZpBJvlK8FpNjieC64yZvIRlLwnARmYuIwdyOLnF7GngLNgO7HTU5AS8ToqekeUOJfE2oH2'
        b'OjjAhjfT4AnmgqpjYHdYfhTYXczcJWcnz57Fhl2rZzGC51TdbNgvwiVEF+O97ZvYEfAQvMzIl8vwFtiDJblQDPdElRTj+jnFcGo4cD+pNw9eAkiybDURXOwg/0bmduvX'
        b'y8GOyGg8ty4SLwJnhWwkVY5xwEu+ScSHEQiP2m9mEcs8uohH8aexPcE+R8aHsQ/qQHP+GGXbpDgK2KA3IoJp0KNg1waEWhf2chiaJJPtBW/ANxnXxS5wC75mYkSD18Ge'
        b'VGRFg07Yz7SpDp4Cl5aBfgY99HHQx44CPeCy0O6ftYTtKLOZBEYCcvH4b3IYY+X4lcg+PouRfXnOlMCjM7kjuXNGx4ye4LtuYQ98AoYCjVvO3dxJ3PSO6T2Cu26hfXEX'
        b'0/rTBqR3I9PNknlNwaboYcd2nsEXvm/aPbdwvVt4n8ddt5j7PgE9wX2cvmXDPmnISg6NxFd7narrtu3idklHvHxx3p7SvoQPvGKQURSW8FDg2ZnbkXsg/6Gv37Hk7mS8'
        b'ca8v+K5v9AgSmNbd1j2CI45PlXLfL6An8HRYb9jpqN6oPs1A6XBg2mDWXb+M2wtGpvgfy+nO6Sk9UvQth/LPZA35ZXyJP/NbvwwU/F6NjyP6SYrrHHfeT915c/xtGGlp'
        b'w0jLJ5OIzKdbnyi3KwyNz0hRKxa+As+s6f9htKWw53o9EqFeeDnsc993epAfSp2yi+UImSOaRjlzyhYUkXuoVHKMu3WR4U/IY37Y6J/bU0f/4t2T0vqqigqyR3/UukFV'
        b'3yBTadb9mFMA8N5HsviXeOqJ4UiUBlJnoeD/yMwZVkyfnjQbb3x8CV/T2OFXGEF1HYucyPYll+3g/JU15ejey+lX307XL1l23z+gL3Uo84UnHJbjCtbDOdkj8xd8wwly'
        b'CH3Mw4BHXBT8Mo9F+QTedxaNCJKe8Ng+Kbq8L/mUd8B956gRQSKCeCfrchHEP/S+c+yIYCaC+GewdEX4Cjr6vnPkiCAagbxidTnjkFQMSScQz6n3nSMYiGe6bi6C+Abd'
        b'dxYzBfmigvK/tmY5zGZ9xUeId5f0qi/Fv+X2bvx9P7rf7XrQW/HvSjHypayH88tGFi/7liNyyGRh7EsR9jj81QssXOOgSyVvhbxrdXvqfV//bk1XxCUOKqVEv3CJXiLD'
        b'BdSwkBZcgRdrc4pZDnFfUfiJy0ERXBz+tpKd6JDNekzh59dKlreD31dJGKWguw7+37I9HCIfcyjHqV/i0PjxzrBrJjiuzkWMOHyt2tGRQzn4sWEv7ATHyLocuBXszrUD'
        b'fRosouxywcnAQrh7Hl54MiWOGzRn5f/ixdO1P7xB2qpIiwmyFFzM3wAu4gvzAqgAJz4zCfIi3AZ7kEU5EANeFifi66lfY60G/W7EjJ0xF1yNzEOStYvMW4zNWhTDK8ym'
        b'mt5AgIQMEti7c6OwYRTPReK7lZ23ZJ3cJTeKrcaj//ZAPXN5dWxrB+vS25xz2+8sbxO2LXm/66tZy88Nas9XN3/GP1P1dmkn2A9uHrLJdQjzSIzKORUjuNQYdypGE5ez'
        b'9QOr+IZTLKruBRe7+Wohj8jlcNjiypwZsz3WeGYMeAneJGJ386wQ2FriM+4lxsKtrYqRndfi4Ulm5QC8CjqiWMzSAaGQSL5FSKB35IPBenM3cQDoIzI5fTXYkg+bXfAK'
        b'JBK5nC0rz5p0A7h9g0qGNG1ZBV4Y2mT2RqTcQoqRcrNcKIEXI5d0WQ/dPDpTOlK6so7ldecdLhgmh5cjsZXekd61ps9m2C1u/H3tsFu4Luu+k/uIp2/X3K6F7RvbuShO'
        b'l29qV41y8QdH+czhFj9wC7YblgpmmAawTe6/3uzMYvk870WSZgTqbPh9/Bt8DqSdyTmQ0XgrNxklNvhESBlXym6mpJxz3LGzFHkEykNQvgmUT6BWCGptArUiUBsEtTWB'
        b'WhMocyIk1+yUR67hRMhxqC3Cxwrh49RsXW4njdGxqllSZ4SbvQHugk90lMYSuBuCO+Kwjq+z0dlWc6UCBHGSxiEIF6V1x6clGk5mxKcxcqo56MlF/3jGf1JXck6jrSHM'
        b'eSpsjDf+co3pn/p9Gk7epR5HnOSU1BPn38eSeuF49Ott+g307mPMh8K+JuEpJmE/qT96TjWB0CbhAJNwoEk4yCQcbBIOMQmHmoTDTMLh4+Gn6ysVHmGfZEkjjrDx+ZMy'
        b'V5mLNJIsQA2jJvwZOajxbEpD+qgfm558RWA4mJE5csC22koqQlTgTk7PtCI9z5OKEcRjnatNszB+1KYCyXhJNrJ3zWbvx5wKWI/BjmWT2Xt89iMXFY6vgeePzdlb/dvm'
        b'7CeIDA71tMiwZebsVQU8SlDrjGfnowLtpzFrN0epNqohP5lNzVshTo0MY4C3uBtYa4ue8KgYSfpLWf6UFg/7kDzQbHqy25L5OWaLohBzbrWiSmqsneGr4Cgpp0AZSN2u'
        b'24lCKwIXKsqoT4w4En4mF9R9wlXjBQ/JwsWH30s6mrG2d9+lfSEvs/hdXmnd6UsWxWeuneWdLfDmdxV4zg6bbVuV5MaZHevZ/tP9fwa35wVT0tiaw5wlD0LOxWwURsVM'
        b'L2w7Srt1S+KOFgjthecW0LEegyud97i/9Db/k0usdZ83+K9Pe+cPU2I2hXBq0qguqU+perPQhggCsDvcndxbDDvic0UcyrqUrVlXSYQP6AN7QDNoBRcLCtcWYOMrjO0y'
        b'j5kTBlvBmyyyLA50g23mB65FSMkSOzd4FOV/av0Y01Qh3rzVsKcWaSavkpVmPPByGXM4WiTcB06Hi5i0KKXnFO60KbbMJ98MCCOYSjJzwS4ym92GV5od5oDeKaWkHNhP'
        b'g+1MbU6nk0SF4ByF0hzg4IUYpxhzdffKDNAajYxR+MrqXNjGoqzhTjbq4W11T8jC2MM8fAbbGlTIy0hbILoSKgvsKUZieEcx3C3mU6n5fHAwA7wh5P+A8ozHx4TDz1zH'
        b'xpL56WfrKEaKLnOhpga3c/fb4ZVWgsNLUND2S1uKDuqZNjw1pt1+xG1qT8Adt6A++wHVnfDUQcU7VXdmzCfLq9KHfaYNCaaNhMTik8gCRwIj+2b3LegR4/PRRgJCyLFk'
        b'hh9/Gn9iJCC4h9fOPeBgImgZk2yUR5b5j3LxLrFR+/F1Qcr6URu5skGrISd8W3JzMkaaYeLr2RWPZpvMei11YbFSsKWW8ryWWjdfSPXbJfxLp5PxKnBNJzuPyAR344FE'
        b'GWzT45PKD5UzxxFNGT+hesIBRGKVjnrqfvXnPInKocK0J54D2yy22RFf0Xf8ohl8/U3wnXgemfhfQda2YoxQngPTuQhTFT4uh8HPL9dYhnHT1L+MXrXxVC9M4hV18knP'
        b'zLKAXR7GbvxYLw9s+9LVqvq6fx2tGnO0JGufA61Cc7QEBC28Qe9fRaqWQYpfoanXSBTPgdE8s+Gx9NBSwwFtpbgc476/SdH7PzllXfPDmgSP0SSaUTHtpU4otCIqcd4i'
        b'RmngeVlRQ2HImKNXKDwS5lDyx673eeoYFPOnzVqjzchyOxGTx3638md52aHbizKvT1m5MD7zg7gy1rsr+L/woKa7WzVt/0jIehKJsiHxlEQkkAXpswheNwogeADsmcxk'
        b'Y47NcjFluOMHduFpaSxopK6U15TOjR0be+bf8Qwb8Z2CV8QmHJvejZci92XoPUVDzqJ//tCuiV8vYZtMbVW5/hNTW/+LLormH3ZRGKjkGIpCrbL4jM0WxeLpb3DISpCO'
        b'leEot9tDVCzrD2Xy/M5rLEIjTafcx2lEE5fDfjdq3fHqgm7BzwSnPiiYV5byZJR6Nw/TiDrSSp76QMgmZ8UqNkgnIxHxTHjUQCJgy0pmbkBnD1/Evn8wOCVCJMa+gm3s'
        b'eBvQM6nJ71RBtlbKm2QVlYr6qlVN3ia9aR5FaCrCQFMNrlR4FF6APlCmD0u/F5ahD8u4HXR7zXBYcTu306HDoUt2xzl4AlGN8sjGwR8w6jOxUT85IotNLfw6RF7ez23h'
        b'P82CsCL8GDs5GeOmk7ldgKrm/A8Q2IRFyBMnCQ2nZfvJvmF9zqHCV6xt3PxCZTSzd84HboH7wdkKcAwlb6Ka7ILIhrY0eAW8Cc7OAVdR66yn1jfB18l+PnCtxsXsvOrc'
        b'KG9wLbc0vEjEohLADr4jPAsPkb1v367He98ouqFaHXW2YQ1FNnN5LC8im7kaFte5/dqr1P1lSov1ONjf4Gw8v9pw7g+zoctAmwtzwJZMk6Ore2G3LTwEzjoyXkyioXcV'
        b'WMPWcU+cHLyKnXFAB67JA35xi0MWiVz5858OvzcNDRu9S9ZLAY1hnNmi2Q6zY6ucfN1mh5U4wJXZ/JgcyfuNkhXhHmcl72zbSb8oCO16vXKrz3bBfyrU/O2Bf3GtHpxm'
        b'V3Brh4tUGab2sPMoWRyyNbgg5MzfyhqSBamZBVtutImWchS+6Q+mNDbXzTqcEltX7nDS23vgRnCrb+ufUlac+t2dA6D8rdK3uF9xYvavvfSOGmzk7C+sLqq+zLq8vvFK'
        b'TGlcwykO9bY0TMKdIrQiU23B8BQ4mQ9OgT3G2TbjXNuahWRWKwO+CZrtmthme46Yk6z3sp/gYbYUvA66yOCvdHmGfSKF/WRhLDwNt02xi4C7NkxnltgaC50KrnDhRXgk'
        b'g5S6AR70JiuGsemFKAKcywO7jGUmwbN8Kgac4U8JgweZqbWb4DLYOb62NQK+hJe3csAhEq2Gl/NMlqgqwQXsfoQnYZ+Qa9FSwiQ+dpwx0jbWqOQaWZOzyVgnEMJrBhhe'
        b'87jRlfILaM+67zt1xIsmsmvfup74vZv7NBc39m8cLLkbnXFb+k4VWPXAP3xImD7sP23Ia9qYjOtz1ftGDXuKLnEGsq7Y6D1TB2ff8Zx539e/S3M4tY93x1f0IFA8FF00'
        b'HFg8NKV4xGvKPa8ovVfUXS8xnodz6HZg3vtK7nrFjjDLTXsChwUhfYKLvv2+A4uHhTP0ghl3BSFfuiM0TTgen+F4XImqRm1RmPKNXM94HyRmexOaYpkJt/tG6/pPzG/t'
        b'4wdRx+3EnKIqriWxRhaKsIw+HeLRweyPXc0lzI9rtlCER5gf14T58UzYHHcTz8D8noJOroNNPK7MqojwOXh8Prw1Nwbg+z6mIksZDpIz9ckSBngEXp7FFkaiBtNSWvAq'
        b'y7DVlwu3Wk8DZxnGCA6tkkeNbuCRazXf+d07h9+LO7r2M8axzzkR0xi3Ju5c9fZHr3eld7d6R3YvQL/VHFl1/KmB92U21Q8VLCr+nu3X+dlIWyNrr7aD1mmiDUhpwzur'
        b'ARouZNk2i/Kt5QJdANzyDIrfYkLxZMe+WTcTCKH4GIbiH81zo7z97nmF673C+zwG3Af5w14z23n3PaeM+Po94lBefh8FhZ7hDXmKh5zFJhRnNb6uVZWIH+6sCXqc2opi'
        b'rPYxaVvyNNkRfORGsvtvfOKQG4sV+jxC1hqVaUZtYzKOeBC5JtRmhegNew9tCM1Z/Q/Q3I+YdOIV/X/NfQdc1EcW/28bsNQFFlj6giAsvYOgSBdYmhS7UhdYpYUFC4oV'
        b'DYoFRAXEslgiWBAVFY0tMykml0tY14SSoimXSy7JHbaY5HKX/8z8FlgQjN7d///5G/Lb/c1v5u2b+b0pb+a976OFC6eCC6BTChoZFFp436CsKes1RtIwWMmS4biuvwkD'
        b'W98LRfPRmQ3ndjdsbTO+/be8+X9+k9J4yyrMcF/SpY+289aa2dha1n/ITn9DK03x1sfvBreeaywOyNVWLvoG6QAV1Gx7/W/rm4bf2AsczWpSI0eztBDpkIMOlSSZqL25'
        b'0WQiTkEqcVpkTPHN62cg4Rkws5M7thvfNXMfsLKVc1rj66MHBA7yjPYYpcAXSZij80nHXjOvXp6Xmlhpv4BYjedZe1TKRnbF5mBBm5jd0uH9ISxtC7G0PaReUuScx4vc'
        b'yMhSRKlvWpMBTlM1xHH+X4jbs+u7YXEjbrPNuqA1zX0O3Osby6I44Ky5JgNsjNaQHk+ax5QFoxyt17pb3wtGMnccyZz35o7GKzUNDO1mQbB5yPw5kc59vxzUzTitq+u1'
        b'xCLNxJIVSWCjk1Zyc85ooKELt7wzh0G7Fi+DmxczAtkWaDU+qbRxhqVN5TKbqQodpBI3gdr7G/OESJybSuKKRiSu38xW7nua1RHd5XgqoSdA4RaudI7otY9UmEX28iLV'
        b'pExrnJQNauRn51aUlk84dWqpiRctXNiNcXLmVqjL1zIsX0MvKV/kJ5s0nKgTOj4skQHtu0m8OIk/J/bsHNQb3bNbJlk1qLe8tDK3UFJOOPAee+szqJOLIW8lJRWScm/1'
        b'G59BrTypjMaqxW6hg5zl2RU4ppeksiJ7JYkthW1IBnUlK3MLs3HkI5x0nOTEVvDeg9rDWLPSPDW4utdIjgppRZEEtTU2bCnHM3/5MnzBJ9/jYo0lDWrhMMOY5KAO/jaM'
        b'CUeSCWA2+T2f8hwGNn/BEEM5pSsJLN4gp6ywtEQyyMrPXjnIkRRnS4tEzEG2FJUcZOVIc9GNZnhkZHJGUvogOzI5Nbq8HA8peLtpjGqG2xyrCo9KqGGv0SaKHGZhY1Y8'
        b'Y1C12vla/y8MFSyf6cS5tJIWUlnN+JlJpRz1zV79J/9silhTTmfBbTIgnwEvGZRzKCZ8jeGywoi2068H+2CnrGI5egQv6jAoTbg/y5mp72hHwGZKKipcsZfZGefYRI+4'
        b'xNmwNgmccVvtC3d5xs+OdYv3RLoW3OE6jCQCGxfqRsLrkWTisnQGh2HjbPwjLXlVVCKsm0Wbdu5lGILjHr7YrZThRIFGcAKeICWs4XHQ7stEitcuivKlfD1UaCrwMjjm'
        b'Ko1AJZgUw5kCe+JBHTHA0DWdOeJVx6B0FjjABibs9AXXSDH/ZHABXoVyVE6DYogosFdgTVQ9T7BlJe03CG/CHf5sbGjIgI1wN+wkbeji70qlI8XAwCSLGbvYUOVX2wgv'
        b'gaYC2I7IMSiGCwX2gWuwgXaT2AVPu4o93D0w6o423JXoDrclMCgzcIwdBrbHEaKNlUIqjKJ40Wuy1vxoqUHRLMLd4Mq0QESSRTHc0OALTlbQ72XDch9XDOQaR3QZsNOa'
        b'MgA7WDlLKwixCjtTCg1uKY3CLKvQKA36LduCHfqIqU5ETZNiuKNmB3IdmvebpuCgOAqchjtJ9HW2GwNcLbImpP7qPZNaQ1Er1wZkpYqnxtN8+YTHwgbQ4esHkNbD8KDA'
        b'/nghmR6K3MBFbMyfiNR1Lnjd2puJeL4B9hBSYnY8tQeRYgmylnYIAlXtdgWpbD3gVSYmht64JwVa4bYgQm0WvBFHey3A9bCRWEpuYU4p9yXUvHXZRP9/PzJLd/riBTQ1'
        b'cCYCnANd8JSvXwBFmmwv2ACbidcyPJQRKsZot3VwJ3EKLQFNlD6oYYVqgV2EpM6aaRRa8fESirN83KRS1YzXBl4FHeAIOIloMkltm+AVuIk2Xjq/oFo8A1wiZJNGZc0C'
        b'7GGDbZrOpLVmgLOwPR5sQuU1SAWb58ylOdoM9zJplpLIe4RNYDulX8YKSoM0RwGmRpQD4kiHk2XVu6qQ5gieQp3iNdgCbvj6YNF1w7J2EnbTkrHDZD4tvIvhCX8mkt3z'
        b'DLgH1oCztOv1q2Crcba9rz9avDN8UMFEeI60nDncA9a7ilFbr16AZFNDyjQHF+FGIjlojXkadMAzmb6BuFgQqoEB3VUQG+fgZpUkbgNnUZ+bbgGaWLxAlRfPyYWgMRx2'
        b'o4Ko6YKRoMArpqRvrpYIxXRribD3ri4PnChimcBjNMxwQQmJZeZcJ8nSzQjXoQV4DdwCT61D7yEQrfQxsRZw2I88yV5rjnjAaENFwWIkJrlMSx1atME2eABstQC7UCEk'
        b'XSGIA9AMj9DVOpAIz2eAm2IxPpBlljLCwHku7Yd+He4HDbkVqBBiezoSSdTiF0jjCzGUkRiPa9uNYAc+qdUwZnLtFhO2T1esprDR6FV+1hyGixPdWVITjOHJRHDBy49D'
        b'MSIocBhsn0N4MxRXwzpwsDAhHh8as+ANjPdzKYRQinCLobajHvx3xyztH14RqaT7qhW8hoass5gYGhEiKSCPhBdJZebnwH0r4SUxGlnQ0mkJwxN1qi2EVK+WOYVeW9n+'
        b'oqzpbxfEq0jVoy51UxwNLsRhE2Q2m4FG4wNFhOFY1LCvw0YOOAe7KcqD8gBys0pn9IAFjuQRx+/UWHB4Adya7I4RpOo80bif6IZGItRjjTQtGe5EuIWo5+8cwZvCB9rb'
        b'UeZmJtibCV8fDTi3wxsjblFhcnaW7heLU2ilBr9LsBE2athGUmggcxPBa5WOpAvrFIvHnd2jGYeNX3OnIzjJqZwDbpA3WLYYdsK62f5ey3hwGxrRjBiL4e4l5A36wJ1o'
        b'CtkCr4nT4Q4kE7CFgl2vgF0EUMpoyTwVeFrcaG+GLfCkYzJHCttAJ9HoVzKzYKvOfNyON9CfWQgNc92kicSwzjMR7ox1j6cVbm82lQrapqZzfMBNFcbYDXNLCgmwcKFV'
        b'ltXO9DhatkEbdtRq1VwCz2OrAvSnh2qCh5hYeM3gGapMSkcwNYPjC0+Ek+rywKZo2AiOiGejaZaAcl0HjRF0F+xkxqaBq/podt6BJvfVDKsc0EXbJ54FrVpgO2qIDLoh'
        b'jlOwG24CWwgYRBg4bqyGTgcvgia6NWxBHRvNdfVgJ/lp9LMbYRNs1bPhYaAf9IfmvUOE9dkVsFsMDqKJcycaH5JQ6Th3HzZlCfazi+AxWEPKR6Hpux22suCeKtzxcN/b'
        b'DW/QAZDlYrhVrOGnXpyJireyi1dBOdlFiXexh3Xo9YMaipJSUnBkbiXe0DSD++2wC8rwK4SvwUuUgTFrqT/sIBKmvSAfNLJgB9hP9msgmhdJreFJeBRud/UGh2iYdCRi'
        b'njQ2nRW4yIbb4L5lpFVXw0YD2IoHbLSWBa+jP7C9uBKfwTnM9IN1TKwTLKOW+VnSJrAtcdVid/c4cNp5bmQ87nDGYajC4LQLYca3mAFbddFEhWl1o78sV7rYRjReHlHz'
        b'5TeaRmEMpzht+s225oFLS2CTTE8PjVKo+8EzSRpExB5raFOoJ3vpWWcV8dxj6U5ljGeZOhasB3KKKqVKI8Ee0spO1lFoBReLseq2i5PdwS4+4VBoyYZdYgbZVj9m6Mjo'
        b'ZSGZXVFiZR7wVHyD3tgC+0LKwCm2ATxEtrBCUqSbw7+mZPjsJeDzpXv3zZcZhfPeKdgSNs/LwU7AMc7VXXqt9OjUqTFfVd+7PO8v6ceXrlq4Snj34e7L1efWnPuNtyZu'
        b'9VdJkd6ftex1aT556N+/X129/FLrvV9m2j9ck72uu8hDW7Fvw+6IU5d+Mzzb0lko2T5rz9MLlzoL5rSsXLX2g5+0o03WhnDsrvrseaPoT7BnSvD3ZtzNfm8mdSbf22eX'
        b'Z1bwq5jzCW/Z+3M2Vh5o9zwxa/XSubuuGc0OeG/Z2eCUXZFp1O85P5x9+tjn9aqdb/ySaPTT7q3H3rGu4W7x2lpzfpPXWzyX2P7vhQm+NdWx/f8QpptH6HE1rWrMt3jV'
        b'1WzSB1aRQXt+dfirOch2cAvSqtxSxuZ2WlbusbMSVx81NQcP7v61bKPdgSgg0vzCLzKo8VerD3xqZB1cVIDjsKiC5+Fd86fYni+Fbt41p2J78rWuv3czY5s7Y4ar5oxv'
        b'qz7ddGTjd3PCrX8w/3nn3yu6Dy7WS74w9TeR/dsPyy7/U5TzUfz7CXfXvvVxuKPy0sUr7Ad1Z1zuzP31M0u+/0LDPeeY5Te58zmbbySzXg/9+cOglW+uleXWzvUJKcuZ'
        b'knXTO4hxddsh36q9+xfeDylYGHm870uX3b9cPfB+X2sb+CVi5r8qGznOYnnP3vfbn7yh+xW3hTf3yY9v5ub2s3y2n2l1sv802/7eW6tXlN7/JrXmn7pfbEjsNXgQ6s7b'
        b'NmvTL397J84xOXXOwz3vfmU+0CgCsi1DGx14H86/mad1tvZ343SNs+b/siyPSKu5/Lu/SbvF5941T0XLfr717cy/Jcd0zAwp/xl43cgx0buWdi/AyetC3t5bxeKbJcYR'
        b'H21Y8cvrS/fskIhXtq5jGPg9yf6sWmRMMDTAXpZgYssuNNRcdTTnFMKtFNlg0JqakxPiik+UmGA/I5FH2zyvhD1sNB23z8QqjAbFjmKgkage7idetGBHgQjUZWYblOmW'
        b'w26ww2C5HleD4oPDrFK0DrtM24LVwk5wXAd0uMVWui8T0ccZhvAqC5yBNdNo0LHTOt5o+YlWROrG0zqrac+iTaA5HdR5qryCtKxQzqNMUAe2L6cPN5oswWvkMITeydWC'
        b'rbxEZh48m/2YbAQ2TnGCe+F61IVRxZYzwtnOxGLOmFFIG2QHga5he2xY405Cg9rA7iJwCp63VoG5MMD5aA1Syh52LaWt7MLhepWZXT64QE6LMoIiafA5eHXe2LOgGxok'
        b'cidodUPrTGzyhu3drsODYw3j0EqjlpwqFa/TGM4FtjHHGMaxDB9jq1FwGXZogbr5aRgkZgfRm7ArmaoFXKdxwCU0XveQLe9Fnk6I442gfcItb3iaSVoxBTbbqAG7JFvT'
        b'3sawLlzlr6axjDbEo63wOPbEDi8z+b/2zRoLT8LKzsur0hvdAEK3ZEvqBlvllmxC2dir0Mx8FdYBd6zDe9Al6db8eu1P+WbNGod1WnRa9ZT8qe38PtE0hWhaj4tCFK3g'
        b'R9czBoz5n1pM6XWIuc3/0Pxd89609D9ZKRwylBZzevlz+o2t5aZKYyd8OCRuEONTI0RJHt3uqxR4jtx1+LYv75IqPMOUruFKQcRoroAup46ZPRFKwUy1NOIXVqR0jbyV'
        b'qhTEjn+wFNG45aMUxIx/kK90ndFTPpY8eVCodJ15y0gpiBr/oEDpGnqLgUrcf9HfKFa6Rt3KUQriJuTKWymInvA3mEpB5As/kCpdw27ZT0CKPLCbrB4TkZIoXaf3IHbD'
        b'Jy0xvuaTNuIIqSfuliamD4Ipgb18artpm0fXlLtmAQMi9w5Zl2+PRs/yK/q3ZLeZvUHivqDZiqDZvakZyqA5Ss+5vaJ5zRrNy1v0+82sm/Mb1vaZuSjMXNrzzi7tWHrH'
        b'LIgcX4YqbWb2IlmwtD0cuj+0fU5XTMeSnrybJVdK7rgn9Is8uzQ6bJrZB/T/MMOAtb08oN1ZMcUXQ/fFqKRTzjyh2aZ5H59yuioEru0xXbM74u+4hfb43nGLvjXl1nKl'
        b'IKlfYHNYu0VbPlMp8L0jWNKj+caUW/m3MxUxi5URSxRBS+4I8npz8voF1m0seUz7TIVDiFI4XSGYTqiqzqxML1ucs+hJVnon3EYtNrv/eY+s5Rry5W36fcJAhTCwR0Mp'
        b'nKnAnYEmH6pwCFYKQxTYd388jUSld/ztcMLxpI9GqxqpehSv9J5Fd6qJyqCOmPxsRWYpvUeEfhw5sdI7dvjBmDLxtzlK76TelNlKQeqzxZKU3uLbc5WCjH6B5ZDIRGT6'
        b'iDKxM3tMmZgIMAyPeZN4t1geoOCL9qk7x+jQm+RYp3w5kBo8ZD6DULOVuFSOGTJPDm+UY5fK2SYMhgVGAXwZFxqyUd6s4Uy16/iONdQdOZDJp2hoAnIUg3dzqVpN1VEM'
        b'Y8wu7n9r8ffMLq6QGr+L60Tv4or9EZkS0koJi4JWUPT5DNkLbUaayDmAsVpstEAXZQM2TiFr9QIZPAOwKaY5POpHmUu8iPrEsoanfRF1HzRBdlE+68AFWik3QdcgO/wS'
        b'EmLzoihicNMv4FLOYnuSuArpYSTneUY1Y171E+ybYHkMKX00E4dgk7evH5sqAa+idRmVuwZp1+SBvGiJr58GBXbCU0hdpiRMSG8N3hZrUj9zzYm1IkyIpGl3ZvComnVR'
        b'SJnPSnjb1ITm4nU/HjU0gyQWzectoIqwpNXN0qX8TJBSnZKlO3UByfetkR4VluyLk9yWz5lPU0yN0qH6JW44vn2CaGEcTVFvhg7VM9MDJxatWiijE/OcNak9bFvMkNtd'
        b'nmrTBG7mLk7DenRZTAbedeAsZ4CrDkKiXYWghYUvPLbQC29bO1Bgt5RWxf7qZ0/5rcPxZLIi5I7aqv2N816gkT75jzKnqpDO/RppH4kmWvO1aqN1D9KvNdFVCveSB+uQ'
        b'hn0YtmrgFdEKuAld40Pp49+9IRWwEcmt+3J4gnIHdbCJ/Kw5h01ZeRph75KiJhs/lQ3TVXg9CTaiVSL6j4NUxi3gtVkUuAgOLKU3B7fB+ix8lkxZw0Y+ZQ3OgtO0In4F'
        b'ldpJmz+hFdahUWdE2IB0fdI2uwVJaWjF3OmOMecYsIFhBHaCDuIdCQ6kiQiAQ5QBWmY3eahMwI6BZoC7wirH+dQq0AQukPRccNIfYDex1fAEaKZWS+EuMqSQ1/LTEjZ1'
        b'N504zRQtzBbScFbH+5/ibsNIjKMYby2SOiRMYcjwCc2VXKuLe8OTQBh/y72Ehexwdo0233D20RjjppKKvxheA+LY9/QDCx9TVrdWanl8191ivuzXZN+3+6Nbr/1++Ow/'
        b'1vlKZx5J3t3d0Frm6nxznpvn1jlfRn+U6pIpTek8l9USI7cpu93w5V3qhP7SxFvtAx8sb377WKH7/ZOe/6j9OMeR80qu+6ELf+2MNw36/HON7d/MWXpRJ+OzVzf1P3pf'
        b'eX7VTxU2Ud+vvjO479JhRfqXWsm3fxYezxV9xnT8t+NbSbWrbUL21r7v7RZyh3062Kvo+uU7daG/OFV9851l6VuiVmbMiYd7Bg7e7tiouffvbxisaP5A/k7drXOzvok8'
        b'uOq24a7HovArf/3L/mqDBysT1i3+Mzc5aInDT9MPbfpg1/alU+sPb9W5z3/7u/KiDnnIie6q9L+ZpJw4uXZx56m/ufXr/S1f9OObu568WdC/bPf1j28U7HlaezXoQfK7'
        b'sscz3lnHjqxe8a2bzaL3Ohaad6yu0tlzAawQdF6b+zSw6sjbX+o8uVp9L6ZKJCCmwlbgBqhVMwQFF+GxCa3B1kpotEU5uADOEru/pGyw090FKzcXmWBfDNxJFu0M2IaE'
        b'Tg2YcM5CpDfBK6CTVqtOCOF5okmArvJhhyFvuIG2NLtsBC5jR55EvKuH9JAdGH4xHO4F9SzQiTi9Qn4CvMpHY+epWI14Aq+IJhuNtUx7uAW209rljhR4YYx6CWol6r5D'
        b'hfBoJXFemp7ujllxxTu6nel8BpBD1MFo5eIkPMBHOubllXDrqMEruORJtCFD1N0u4Z8QJRgRVElySGQ6j20JuoOJFrrAFp7GCuBODP2IecA1cQStoIYFTvuEEsVtOqrY'
        b'KVTdG85YeVNpbqJU4ooEusDpuBG9bFQn84X7kVpWwCcNMQ/WmI1DvlxlwiqdBk8RHhalFo5SGFbYYANoRErbDLCZ1ATUzMCaqmesm4cHPgpEXMIOuDuZBRutNAmVKD1N'
        b'lW+Vj3CcZxW8hqiQN7I3AwkGzrVTzKHYTCY4xACHwDW4l6jLlrAHHqWt+cAR0DDiTQzPZRJbZNANNr8yqe0gMRz0TdKwys4nP2aeBltp3dsfbibqN9G9DcA+4jeWB45G'
        b'YVaGldAE2DheDwWXPWm2z6RX0RqkNlPNkysLHKIhT7Z5wtMYdR0cjhgFXq/OeiGvLTWEiUE2dlKo0h9dD+F7okNqsWgo8AVmFN+svqJxmpyxO7Tf0vo+j49tnft4Dgqe'
        b'g3x2O/OsZodmP9+C/Jmpltx9fBFaxvXxPRV8zy6Gku/T5dPl28sPRI9pDMr2KQq++x1+QJfDHX5oj8MAXyjnn7Bss+yz81bYeXd5K/n+ffwQBT+kJ1zJDx2h6qLgu/Tx'
        b'vRR8ry5DJd+3K6IrEoOHPP9HB5Cmy+4TuCgELkq+ax/fW8H37rJT8v26UrvSevnTyHO8+m9Mpkm0o4du7ant6KH3eI7Tuhwue5zz6POJU/jE3XZW+qTd4c/vnTv/P80X'
        b'2OV4hz+jx0etBQIUdgE9iP/gPn6Ygh92C9U0Ej+2ai9HlerjByn4QT1GSv50uoxtm22X/Wh7RSj5M+kXMeZ3grqm3uFH9MSQR2Z0lZGiR6/flajO9u3evXz3P3g28p6H'
        b'Aq28jR5RViLjp0EU36IhoNlZaTzl8TQrQ8ehYMrQZFg87vKckMDQd3d5U/uNzfqMHRXGju3Gd4zd7qv0M047u885ROEcMqx9ZrcY3BF4tkfeEQQg7ZJ9U+eKziMWQxSN'
        b'Q//ZRTMeUwyTGAwzYWjSpNOg0xx5lyfsV/8VM4umlQ0r5ewTem16SjOPerYKM1Vu18t3GDFo7eU79js4n0hsS+yyVzj49zlMVzhM75mrdIhWmfPn4CCMZpb1Os+a7LwA'
        b'ngux1xkD53IM6x7j+trfh5WPX5DyMd+MwTDCVjov5TyCZxYRg6zeRYzv0Prmd+LX9B227ReZjcNsIe6K5TrY9MQRX3C0+XInbM2iNewxNvwN27EQzygarAV7KBB7XWI9'
        b'SSzbiAXSoG5mSnhqeGJm+vyU6LRBlkxSMcjGmJWDOqoHadHpaUTxIi3w3+2BPQPTYoYbddSH2w23ZyWT4LT8pGGgN/WBPcW3GuA59fN9HnOYfL/aqAcalJXDAM+zn++H'
        b'UqwCahNGYVh8MQyLP4FhUSGsuGGEFQ91zBUXnOJGUkysB3jONC6LiXdt9BMtlp7HE22mXgrjiZaO3swnFmw9z6e6GnreQxS6/MRj6UUxHuhTNnZt/LbCXivPAZspA47O'
        b'Aw5OA1NF7Q7yBeijY0p7nnzJ6BcHp3a2PHj4w26qvEKuO3xnYyd3aF4wYI/vrAbsHOTpcu0BR5d2P3nCA1ueldGQPd/cqJ9v3SIbYqFv9/mWLWlDHPQN4wbbtfm2yVBW'
        b'jyFNnKJFmdi2GWMKQ1x8r02ZoNxyfnP8kA6+10WVbZHJ/ZqXDunhe33KxKrX2nvIAN/wRgsb4nsjysS+LRLzOGSM7/mjz03wvSkq3JKLmR8yw/eC0XtzfG9Bmdi0seRR'
        b'zVVDlvjeavTeGt/bjOa3xfdCysSiJVLObg4essP39qPPp6D7Bw6oyXFVsAUoyvTQCSc6Olnpo3efzqCsbJvXtMcpbAP6bEMUtiFK2xlKy9ABgWVzQrupwsqrz8pfYeWv'
        b'tApUCoIecFiW+rXip9oRDD2XhxS+Po1leulZPaDQZdTTA7SUlJHF66LlKkcGDsVLZy2IgJfGaOc6qs9H9hhrw1ANa4OBETZUCBQG6H9NgqlgMPYujzn2/jTrlCZNkEvl'
        b'WRGrT26tQT47j13DHd4wWMBmUhKOCqNDcwxGBydPC6Vy1VI1Sao2StVRS9UiqbooVU8tlUtS9VGqgVqqNknloVRDtVQdkmqEUo3VUnXpGudZD9cqj3+ASdI0yJVgcyy1'
        b'oJ75l2dCMCKsn33yLKbEc+mYviidKrXvxxg7GXk2tUyytUOb6engoK753DyBWrsboOfcWn3yPsxrtBbwRt/vaYthWsRKl4XDw+Zz8ixrRgJBLDBcZcbNF9kO0pBU4qTo'
        b'X/eNAWLEUMHDj4S5RdkymdA5pVRWsVxSLssuycNjulRSIhpTZsyNSzrGg6TjOOIwrqU5stIiSQUdfBUHsCwqxaaXOICmpKyCjuFKMC3HxRUtx3tdIs1BbnbecqkMm2QO'
        b'6qi+EstKLTqmHkpm5eUvH2QtK0FpxZI8aWUxStMqQ5yvKC3Py9VSa/2RWBrrKXVb+uGYusR5DTc/GzU8BzWeBjF31lNF1EDiunUkam41l+ywaantsHHV9tK01nJVO2zj'
        b'UtV32L54wJoA+DOuRFohJU57Kizo4bchLZFVZJfkSl4c9nOk6YJVsKGjgWkxZZVdKo4z6xxBW8OiDMWSctHEIQfDhSrTYBomWlhZhh2oA4V50gJpxQRopGO5wG9thA8c'
        b'jfc5XKDHk/FQIswuKivMdp+IlWnC3EL0k7kk5u2kMV1VcjNxm9BPhc6JSFwRS5KS/6BF/P+oRZDA0uFBo2LmCIuycyRFQmf0VT3iqshjXCxTIhSyCbkYyzppW2cftaaY'
        b'gHkVI6jTBAsTCFwUpjLLM2EkMi7dLKj3p2XnFuJYtoQnEuoYde5JQGErc4okearePZZKCrqWltBRcRElggmL7umWUo0JE7dxXMVIrOJsVTPnSCpWSCQlQj+hcx4dzlRE'
        b'hpegSSs6PDDQzU7fCaV5qhfm+0cvbHg0UcWEVd0JyyUFUhlqYTSKocGOiJObsFL12ipLcGzWP4C5fdaJy4DeVo+NNMR77inOK7N0p8zLoAMBBoB6uHHYeVQVlCOFeI+q'
        b'gn/AbQmz1cMAbg7TdYRnefAcPEGo/pJiQjlTlHNfWNb0QltrqjIUJcIueIgzCdUq2KYijM04M9RpHy7Thcf81hC6hia6lICiynznZSV8VLyaqpyBElflgXPPkrWH27C3'
        b'6+i+kTrDoAfU6oA2Z0jv/a9y1aB0Ebvfu2Xp/lQRTlX6YHavlvuPIWvAGeY3zjVNndh6uIsL9gbT9pCfrONiM06hXn5WUUr6TJpFuBXKi5/lsRhsSk6DtaO7dON4vKQD'
        b'jqZnELJO9jrYvMl5vWVWgqPBK1Ql9pkDR8D1CVoUblyWnOY8vBM1huZVcEoH1mpBufQ731y2DPsd/GDrtflDsT7TTlfj/sPXsra/+tDmQkvClz2+JZ9e/Yp6O3JlnCL2'
        b'1ZSNiVp14PeLu35mc0VfHzW+pjjPXnPqU66T897M/hrXIZezBa+EMhd9mbH3AzfxPzx235aej1Nu8nvrzuN9Mb5/+uD9x1+d6N+Q05xzquWjbQdvhu2WHvOqt2pc49hy'
        b'IEZ2Z3nnhYPL3v/Xraj8Le89Xnfp0Y4KQWxD3OuJwdV3bl9leJRarg/x6/papE029PTgWdQyeMtQJTDgAjyt2jSE+8EmstfmC3fDQ2rRAmE3vDxisVG/gkTmiYaXwXV1'
        b'QvD6LDpwji1sZqNfOQfqiZGLl1/YMzuQsLvAkQVOg/MFZAOUORNec1VFFcTIgWBrkO+sxY9pW7/GmOHNUXA5AXYygFz3FbIvVg6O6o1u9qXBU0wGOJQGa0g9RfAkvPLM'
        b'Hi48zwnHW7jdC2i84K7k4rGbjsF82MGCjfA158fYj16TC/bQu9KwGbS4wwvwkozsSqOUBLLQd9egEkGNJjgILhT8j5VdgjVkOLyuGIuxZEbj8T5YaU5NmdqW2y46WqK0'
        b'98fwSAPGpvUVTesa1imNndrt7hi7EkClWUqL2F5+bL+DJwZUsiOZ+sycFXSEv/A7xu4kW5zSIr6XH4+0y7a0dsHRxUo7XwyyRNNc27BWaTy13fCOsQvJHKO0mNXLn6UK'
        b'atMqRjm5dM5VDasaQ+WIqiMdLFBpEdHLj7hvZUuyvBRxO9EJmzYbpZ33H2ed4ljP/ognfDYOyjm8G3EeXy7gSze+XMSXS/hy+Y+d/UYioIxz+JvkDYnQelGGJ4Lff8a+'
        b'peYMRioDB0FJfalYc3jYatPwps7pTP+v8KC0M0fWl5Oh3oxWYRj0JgNVQQ27iF7dDi8RJ4BX+s/xoFRgQbqZauvPF+dzHubz4AifNuP4JGusUS7/G+AgbubwivTFuVuI'
        b'uRsFM7KluRteAD7TiP9N+7Ez0Wr1xTlbgjh7NAJqNH//fJpDS5pDtfXuf8ld/jB3aAn74txl43brZQy3m/Po0jd7PMaX7H/3focXny/OZ97Y92uB9yXVVq3/LWc1w5wN'
        b'r2RfnLOCZzlD73VkRazGmYhJdoTpveERL8WkXJYaLxjynLgpkuCWXDVPYw2iiOO4G1wS4BKHt9Sr1c/XHfE71vxf+h0/4RhNoIqH5+XhWEslkhXq8oH62AtFXYpGihOd'
        b'Ge+DZOflITUBKRvZKr2TBE/CATLchAXlpZVl9FZItjC3tDhHWpKNozs9QxIJqssIYpyLm9BFHesO3RM4PZQpp7R0GWYVb9cQzYhmo2JV2UvsHoz8ULAwrbQY66D0rg4O'
        b'FKICmsvOKa2kY0lhCZDkTdY2+F9MablQgpskT5qfj3QmNFLR2tzYSqnam8SXQs1WoAqDMoEihf8h5TA3u4Tohs/bGPAOUFOHhc6lZSR2VtHkirF6u9JK3zMDhNA5PKdc'
        b'kltYUllSIFPtEpBgKBMyOioHMpm0oISIggdpEzXCqohqQql6raRIYUbK8YRUhxVhb/KSA6aN6MP4l7xFbngfTpgnyanAv4Ny5CJVVYpvcidT4YlUSkl5maSCtF3QtBeQ'
        b'mRjsm032/cZ3FalEFvzCMod4lVaoCNDtTlJG9hOc00qLivAeQqlI6OJSjDdpUHVWubhMuttDajyGIp00SnIWat4Sd89YNC+VvAxpGqFPtSVQKiMVVqH2vVB53Dnp0urd'
        b'1UOYOLLbQbpvac5SSW6FkLzBiftAWnJQgJe3as8Vb6nSvdPjxdgY42sfPG7XaXmpNFcyIvARkiJJQT7OJxIu9PZZ/CIkfVSvsVJCV0daQhjFvT4qKjFx/nxcs4nizeF/'
        b'Zdmrikm0Okk5nvjchMWonUf2VtQY8nk+Q6rXg2Ezxr4vnDJ2p43uLZ7DPWVCtujlXwSqJO77mAb6eV+vSX9+DLrB8L6jWjdBqahHlsikNFOl+RP+anbeUiQZpD1wARKy'
        b'L3sl/j7x2DjxjuUYIjKy5SrNLayQFuCqyHILi+A1NJIXiZ7ts5PSdBciuUmrkFSiwXWEAJJgqVDVRGiEKkY9LjrDPT27IkeCt7HzJqGExIWOfFVUWbxMUjhx+7sLfcdl'
        b'I7+WXZlfVVkhQTMHjhcpnFNaLiNMTULDL1gYXplfKMmpxF0PFQivrCjF89uySQr4BwvjSvKky6VImIuKUIGMYll2RZVsXM0nKR0wEcsv30CBE5GRqrFV/HJsBU1E7+Xa'
        b'ZRppyNGm/4OWnzAxnZZkvN88ju+XlkT16ueXo9o447Yd4Sk7p6qyQDS5+KkXFwY6Ti6AYzJ6T5ssJxKzEs/syUVqLJmAycgEPI8MEoqR+j2HRpB6tkmrNm0MsQnqNemE'
        b'pkJfQSOc6htZD6A1KRpbh4dy5zR6jp10wh4FdwkWRqIbIX2H1jjOYnQrKUH/IzEX4jkoaNIhVw0WZiwZn3FkfJ5LhiDI0FPGnPB097gooXNGWgX6xPON/6TFRhBn6KLR'
        b'GWSkxglCZ9TJVSKOXvvkzVBZjpbIuWi2iFR9cxOqre2iM1KFznPhscJy1EkRL36Ts6IGdjNKbCRZxdQwKdmyynLZs0w9b7k32fKSLCVffOU3skQLH3N09GJrGALfEyxM'
        b'wh/ChT5ei1+8mA9dzIcUm/xtDOMCqZaQqnusjD9PDghoECqCP1DGZ/NNPorFSsrLSzxjyrMr0aXIwzNGilZ3k49aJPvkYxWmM/n4hH9g8gHqeb+MRqXoQrQIQ2P/5EMT'
        b'4Q2t2fImZmOyxkOrWImkAq8s8CdaYAU8d32XU7oyWIhNFdD6KR+vWlECavPJXyouhNGY6FLZRUJ889wSudIK3CHR9bnLPRqCCuekvxDCbnid7u7rHRCAJG1ynjD6E2II'
        b'fzxXIvOzUW1j0KDyvEwEPwq9IfwhXBgweUbVMKca4p4n0cPIVsHCCPSNXgkv9Al8bv6Rrk2KjD0afm57D+NlqUrS72fywRqjZKElWkR4Eno9k4+IOdJcRDAuEv30BD3y'
        b'D4JWq45nO+czqQptPfQtS9dhSQRFkB5ywD64mYYZMQX1KqQRjDKiBWi0Jv1KNpUSz8cuI7pNiwppuA2ZdowYnwMdc1Jhn4AecJ1kr/Y2o37LXYQdf6bvYDBVIIuvl4Wo'
        b'4l/XwzOUxyJ4jAA0CGVwI8EjCQJnh0GmmLATnJ9JaN3Tq2ZMt36EnaMWXuGtoCox4Nw0cG65K8obj6NcYfcBcDo+EQMdx6VToBOehedAXSq10o9bEBFDwBceFtCYxl1x'
        b'P/oOCsqj9OhzadgMt8B99IEnb+ZYXGNMLJY+0Zqjfny8A7ToiuDxV8iBinTR999SMiaDony3bNub8noSDOMdmHE4c5rTDD/R7o3b9m3ZfVie+cDLaHPuW+HnRd9+HB0c'
        b'dcFp17du/2549G4Tv4l/uiJYWlCwfHlonWft54oYw+aqP8d/6X4yRGH51uyzJg5NzU84VIuBdufJiz86/WT+7vT37v9s5GjnnLSl4/tfVm8//clsWU6Ty9eVK69/c/eX'
        b'+cEz5591FH1VVt78b1+X15IMlpT/4y+bFqy+csxg9iz3uNn5divEH+24Xr7c4kn89NVXzrc0D1pdav5qn9Ucu91fKkp+ee3em5+vTT1z3NsgsFpjxTT3iJq6gtavDH7c'
        b'OrTF5G9gyrL0R0nz34o+tXOn4GDVXD3//uinhd/+vv237wzSz0TN+Fom0qLDl3VWW2JneXAVtMOtw97yhaCJdjO5yQWbCf6NA7yhcpdH8tBFHhrBOk1XuDUZnHWMA6fZ'
        b'lEYR0x7Ww0M0NMA2h9U6Y7CTl8Gz5AAW7IVycjgJzmYspQO8bIfH4p57OOkBjhM3e13QlYAhlEcBlHFEoFEQZXDImMaCPR4Fu2VYDEAbuOjujLPDXdjzo54FupIRNeL8'
        b'tVUTnhFrFCTEMShmKsMF7IJXRAb/y6CNGB1FOOoIP86zU3dk23vYFz5OFaY0xYYSut2x9Wp/BYeZsWyuUBhPGbB06ndybtbFEKEO8uVtbl2su2Z+A06uHWldxl15PQHn'
        b'im753oroDZjVF5CoCEi8nasMSFW6p/U6pTezm+e06PZb2so1Wqb3WbopLN0aovpNbOQOCpOphK5LM358OLgluHUkw9f4cHKm0iKslx+G48Etap/Wa+pfz+o3Nm3O67Px'
        b'UKA/Yw+C49xn6aqwdFWauXVx7pj5f2rj0uuapLRJ7hUkDzFZJt4DXtN6HHq9om8Z3/GKxu4NxA/XWCFwH9JgGbr3893ro/r4Dgq+gzyNeEW4K/Cffxdbyff/+bEmZeX4'
        b'kGIgOjau7ZFKG69egdc/h1go4Z+PtSiBHXpm6D5g4dTOUlq49fLd8DND918JWi/wMY0UUZBrG8WkoIgbOZMFfbQig1kwmIO+v8nkRglYb+poRRmz3jTmoO/0wasBffA6'
        b'erCAhe+lHHrHCcHoyetzhWApSw0Gc7Ylg+H9lEKXlzGwxyGuJo7gQeDz2aoIHpxaqlZDhSD9v43iUSNiln9HjYvSZ/vMDOdIz3ClWjSmXX1+me6aIFfa6zSDOVdWOdvf'
        b'C2M0oV7NAGdNquHu6lF8aQ/QZK0DXnNHzTWXmguPVBF0J4yJJEqbAuvpkgz4OgW7QT1oJ7/kobsG40DOSzFdbflOcSoN1u8UBS9j91zsmrvOXAK3RqvQuExXYm9e7Mpr'
        b'DvbkggNCQqOdRSyFeF0Zy4t+rk6mXWzLinnYhiqoN724aEeZBe22udqcTgzTlRUdM59H53TO1sP2S87ygPyE32K16JxSC2LU5Fyfv0p36Sv5dM54K2Lvo7V+Rr6bJCGa'
        b'zvmBgypxSUGRDs9H5bYrolmicvKKhqbz6cmev3ZOGjwON6SkpKD3E4XBE+EN2mm1Yzk47asNO7y8MLAdPIajkW4pop9tAbvAjrQUCsPEvEalwDa4wQK8RuZ9fbhrDXEE'
        b'HnEDvgw2gatw+3IamGlDBdzjq/IE1oB7wG54OpW0cDg8zk8DmyA+jLej7ODFGaSFdcBRuNMXXABy7ItN+cDmJXTL74Lbq2GjHpBjD1/K3QTsJ+/W0QXNG40hYLOaKy8F'
        b'Lq5xIIhaNmmwLW0paE4RsjB2n4kGaOPCehodsA12GaqHMQB1zPmJ8avBQdrHFrf2fFditOUVtjxftyhtHd2wTrZ0YlZItdtSoyqKhv7aDtZXp+FWpbBP8hW4O3sB2EF7'
        b'WqfxsdGbMMyldLqdNYeiRfIk2AL2pq0GV1OAXERRwdU6sA3NtO10gx9a7CrjgG49X9RwTHAKY5hdgh3SFbalHBk+xoxgfX0w/d0k6MU7+MrukorjOo7ux90i1rBn/Xu9'
        b'7+UG+/fPXE/fO+WDvVX3N/5c+29zo9/XH3xb4+u2+Njj86xvPvX558Kf9ZPrI5iiEhej32Zp3ChuOvx0aNsuW6qD18Xd2//F5zfeLHa9sP7igR95nU9C9PbUK+5Vace2'
        b'Zy1m9Pj+njKn2o1z/oN5kdt+SvjXZg1Z5qobnHlfRAhTKjeLZR9372rYefXd+9+HNLxzL7v0UY/f69/f+1MolPYssjJ8c8s059tFwfl/8rrYlxEaX5ebMZh0/FGkJD31'
        b'reikxUdThZ9cn/7JO5yu6h0H5bOt/xk7Lbuf9X2y6Il0fqXFN9d9clN+3HT94cGn3z7d01xy3G7Ht1G/v/2azYJ1f3cNunHoiOA94Xd7qvhO5059a/IVWgENGj9JL50Z'
        b'KRcFSrXdPaI5de4zdw3eXHbvveV3Wx5V5Qdv++D3mWmrdpQIvv4ta8c3SQVRCvGlWT+EttUdm+O2zuWTV6peXZz/iY6N/NAaht4vFZ+2vybiE4feebEptOHUxOuSaLBd'
        b'tTRh0OhB3uDVNFey3kGLFi34OtPGCDQYBRCcIjdDU1cmLz4xgUGx7Rjg4BJYSztGbkrUH43cAE4xwcWFq0Abj8Y+umG+GDvOwnNjkJMkYD1ZCcE9XLBxPDAgdigVRnP8'
        b'HLhgPaAjxoMaL+xSCjY6DTvoMoCcb0p+P3QaOIWD0bi484pGXHPPwg7ao7UWbEUD6rCB3ELNUefcoExCOkQ8G5wivsOLQO2w+/BSGTFfWwXkyeOt5jLhWSNsNYcW/Mcf'
        b'0yCsoCcWsbBl8SgY02xQQ3xdHcE+S3Hm0jF+u/pgEytC5Emer4FycNp1avBYt11W6RxIIzaBM9i9WmwKLqk77upXs6LmzyIZZs9PHmM6B3eDq0bEeO6VTGK5lwn36oC6'
        b'/MUj3rjYOk9G41btcQSvi8eE9AU34I5SeHUusT9MW4udgcfa7sF9bkbYds8AHiH2h7Phediibn+oZnx4FRyAZ+eB10VaL7zIwCOQUKhu3IUDlFfxRlcXssw8aS4dJ7iD'
        b'qYJcsqXMLes5OAahTr/QoU/opRB60TAvfcJp9bE4CMfKAzNwVA9rodykdUG7XcuS+pj7noE4sMepdfXRzc7yOQoLVwXf7T7flvbhlJefWNG2ol9g2S+wkZu2GKDSfQJ3'
        b'tNbrQgs+vzuCGT38O4LoW3yMa59+Yn7b/C6GUuDTJwhSCIJ6DJUER+awQYsBXag9Wynw6jLqMu4V+OMH+i36qngfs5UCzy5mF6tX4Ie9n2L7rLwVVt5jSfVE9ET2CsLI'
        b'88OJLYlKgUufwEshwB65AtojVxA0nsGwHrM7gvhbMROmF96K7YvKUERl9EUtUUQt6c0sUEYVvkxOa7reS9qWdKEaBPYJZihQk6BahqH2ajOWzztqrcChTaxJC6r+cAWi'
        b'iJWivry8ndErcJksERHpF+A4LEP+ll6mjyhLZ7OnAZTApmF5c6HSzOmnQEsT0ZABZRc8FMOgbO0PF7YUylcrbXzrdQaMBfcdpp6Y1TZr0nYmlCd5OaRafY4BCkfsDywI'
        b'7hOEKQTYHxhDPo3KwrBIDBly3RF7XEezp0aj7LW7PjDmOgYguZrakDjEpwTW9brPxs94vrEjiZ/xxx3ha9ZoDLSn0bYv6caajJWCR9S4QGgjYXhJyBaOCg6drfKzwgHR'
        b'NEag0EfjGfwP4lWV/zR+wf1sTAPNpEoMEpAA66tdY9FqKCUWbreE9SI0L4GO9FhwBta6eaDFZCzcolmWBmrp9cvri9GA3QhOrQXniHkzq4iB4VD4dECXraAbXMM4J1nr'
        b'VlIrncAVGlSlPavCNZlJgYb5jFQK7odnQIP0QHgaS/YNespJ+mjz7HPawIt3XZyzzMTQsOFIUqeH/r/X9yR/+8OiXvdNeelt2u9+aVpmMvPIzO+yLU1ylvp8vfLp559d'
        b'/9OMqvXFLkO7vgzNb2T+6dsgnXaLypOwOf0V96PV8VYuira53e4f/VQZ/cTipDz4i2t/+3Xau5/P6NMtyjN+t/ho+yLLu/KqL7a59usxLm1vfr9sx8l/yPyV17Ik28vE'
        b'HF4pr3NrGfdfb/W+c+PfR2ad7N65Yajvzw+/2nLJUPMbwb/+dqRFJtpcZ5pVY7r0y0dSp390fP392h8LHQs105qhoWxLvWHMt9+873vbe2AmQ6s6sN2kWmRAQyO0gvPw'
        b'VddY0ACukghT7EAG6EQt2ExP8mcXwAN4/Id1FJ+4XWrBOmY1bA6iJ+8tWa7oKagBl5LQTMKkNJKYVrP8yQaLJtzLxJO3m0ccItdGHuvALibEYLSHCXW3Fclo8dK9wt1F'
        b'25psknDBCSY4Ggau0tgcl8HxJLEbRnXYyilKQCsAnTAmbNZOJb+d4skhawNY65nszsRzuwushzX05PoqExzE85/IBXarx84CG71VkByXMUyyG9xWHgd3oBWRxhLmFEYl'
        b'XbhVAK+4YshHuFsc5+4hYqKZ+zALbC6E9fSm02GWD5pZ4SbQCbd6JnEojelMM3DZg27Q60gnExNhhZv4WF65fCaq/iYzUqdItLauR3zvQFJ3XNVmEUxBpT6Zt0Phdvgq'
        b'3jACV8BhtUUV2DaVTPmx8JKhq6c23EDjUWqAdqYbn/9f4yAOK/70cKRJQL1GhiNZ9nI6mtYvFD0px9tRfNOmwIbAptCGULnDXWOn9oizszpmnU3sSOxxuOs281bEO/Fv'
        b'xN+uuBuV/qmFXa99oNIiCANLoJFZt0W3VR9N6MZmTcENwY3T+4ydFcbO7aZ3jb0GLOzkDu2s9kVKi+D6yP6prieWtS17rbhFu5ndnIdGaFxWnt7u95HAa4hFOfnd55s1'
        b'xTXE7RXft7Q+HNgSeDi0JbTd4a6lZ7/A4rBWi5acf0B/HJUBazu5/QmnNqcTbm1u7RVd6Ur74J6ou9bht1L7rWwOx7bEytMPJD1lUTYRjF7r8Af4Z+5Zh6Ovv8qwieab'
        b'7kbR2py3tDnRxlz1EMjlj/9w1Kfbmw54PAbGYILWtmWrQaitFjIYAhzr+GWidpHwSSI22Y+gQ3OQcB1aIxMVk3xPEhmNBzTQZlDqqAYvYNl/kkGiMlZIimU0LMHD4WqJ'
        b'DP+HW5VqrYjbbf34f3RrnsWtOeLTa4en0MUMAl/wgM3W4z3UpfRN2lhtkc2rzuW+kfau8a24AXMruesV4ytpPdx3Ix+zGPqzMRZGaBjjKctJb+ojDklgo68PUhnDuAYB'
        b'GNcgiOAaWE4Z4HnQ2AeWAbXiUVwDf4xrEEhwDYwtB3hT+/neKMXYtzZyNCUUp4QxSJKqmBcu5qMOkDCc8lAL8T5EMfUTGS2yc8YPyLdBM8v9UW3mfXaBCrvAHq7CLqLP'
        b'LlZhF6u0i1daiQdt7Num9U2ZppgyrWeqYkp435RZiimzlFPilDbxD1gMazHjEcUQJDAesDCtpxqVDD33xxS+PtLEKUMk5WkJa5qe9cPlDPT7LVPu6tk8ZfL1XB8hdcf2'
        b'Af6m5qZ/YyFslWGddFUO0Uo5lJ4FE83OdS4iRpL04Jc72bIo9Dq4/7KSNHyYtCmM93bBhs3HH6+T6pz5aPDGxq0rPEM3PeWalQ5GOf6Us9/r/sDPvGt5r/7oUZyqX3Ow'
        b'9Ma9NSG/uetcHtKe/3N0Svu6n3/cfD+sZc9nC9avTbkWyrw28+DJb48tWuY/d5nB6eLTWz6XzDoq73b67Ppgi/Etkw8/dLy56dovc670Wu/vC7p35OCyg4IFH+7SWpj0'
        b'0fH6X/2OeCcWxvvuT4tfNphnGKOZIdI8tOFJ8/fcjoScp/KuuSFOd2y61x7m/iCrHtK72DJ31RmfPElFW89fzny86NAPs1+1/8bgyW/9DrGFcYHdR0JSuz/IsZq3zDc7'
        b'p+Djb0JXb3hl2u3qqfGLUg47JRpkmxReyvvmlxiuu3NWao3v1D+7dzxM3D11U2nqm283nD8R90boYP6UhP6WJZKyG1k6R34p+ORgUeBn51pDS39TVm8wMMyf9dWtpe+t'
        b'jRWxiOoOX1taBeuQ+oa05tIgCu70CaU9r1qAPGLs+YZJ9VR8vBG0jJxAGIDzIaMnFQ7SscEep4IOkcP4zqf13Mv/ja7+HwwODvSUFkb+PTNKjBsvBrUyM4tKs/MyM6tG'
        b'vpG5bgaS0n+juc6P0jMZYmtyzQYMjOp96lY0221b0yKT+8iz2/xbq9pn7193zqGrvMfuXGXP7HMrL3i8EXXbCMbe8Un4VGDR7NOc3eLfypXHI32pywypfL3TkxRmSb2p'
        b'6b0ZcxSpc++Yzf3UVCg3aizp5TngqHzzGEPalBG/PrzBpDbiqZ8h1+EnCl2eOjtx3Z9S6PJTOmM616J+zmMKffy0luHAtWg2fUyhj6EkBqXNe8osZ3Ndn1Kj1yfkijqr'
        b'Nm+IPByq4FKCqe06CjPfWt0nGlpcwVPTchbXCmVH1yfkOrRUkxBLJWRGrw/JlRB7QB7+PBQuYHDjGANGtsd0e91jlMJZSqPYXt1Yer7cFi6I0qLe1DKOslSdW1gPMjMz'
        b'/8Nziv878oK3krLGnoBNNLEYMvHEMiwjJHJpBEXrZt4MBg+fgtAX7IfGexk3NLwmOKkRTF3VCeewpF+8wWPJzqCkmTNrJdvjtEGKYNO96d0ZvDfagtbDrdcivov4/JMr'
        b'3SFf7Pp9yfSapvQF7DeKbtTUTP/4WGyjnXjndM629OnRUywbopw6vzz91mGPbzYKv19SnuV09uEPvzft+HXg5IbylYFWqxd4hN59V/LhyX8kaE87/+GGyMPFLuXvTp17'
        b'+p8/3HHeNRDH4Oix6oz0Td4e0mrO2mb+zbysrRauUUVd0Rusfwq63//xjpucSytWG52rZh1/1eP2nGNImSCYlB3emXhNnowP0beLNSkdcF4DdjNhO6gDDTRqeydsABvF'
        b'yTHgiDs8h7PixbshvMZCa+SDa8jYVW4fivLvgrs85uM9J7y1qUnpG7FsvGEnWQYL4eYScVyiS6Imic6jwWZqFcJaGnK9wS0D1mV4eWpQjDQKHoW7CslRKmLrhMQ1IjWe'
        b'QzHEGJJ1LzhBltxl8+FeHFNjJ44ttR2pGCL4OtjAhPUpHvRW2jHQM0WmlkE7LhkeZoIuhgE90N4Eh63EcW7aYHecu2qjTx9uYyXBi0sJoDu4uBQeF9MhXabZYsOGYHCK'
        b'FPUCLUvBKbSUj1VB2ugaVycyYTfogLSbsD7YDzcApA64lalyaIML4CZsYIJuWLuCxlK8Kk5AWc7rgtoV4KTRK5Xwwiu6r1QyKDO4iwW2g/XBpBr5c8AmMYFzxFXBxxv7'
        b'DQqY8AhsXENv1173TcWN7ilG88BOfBiN7zTB9irK0oENNsGuWJHzC88F/19ODWqd3plMEmHD/54zTYzxRNUa4yK8AF1+RwPAIwuKY9yvx+/Ts1Ho2RxYqdRzXh/Tz9Z+'
        b'NWFDQq+h3bGgu2y3T9h66O8ztu09ttM9tvtn7ClPNRbwOGhcHb0+IdehlUJKl78+WW1XyXaQVSQpGWRjt6VBTkVlWZFkkF0klVUMsvFG0SC7tAw9Zskqygc5OasqJLJB'
        b'dk5padEgS1pSMcjJR0MW+ijHVo44enpZZcUgK7ewfJBVWp43qJEvLaqQoJvi7LJBVpW0bJCTLcuVSgdZhZKVKAsiry2VDUOuDGqUVeYUSXMHNWnYGtmgjqxQml+RKSkv'
        b'Ly0f1CvLLpdJMqWyUuyIMahXWZJbmC0tkeRlSlbmDnIzM2USxH1m5qAG7bgwOhHIsLhnPe+fUDj6IsgFBwiVJeN38Pvv+DTakMHIY+EheOx1iFxfZkDGM9cbmhrhZtQb'
        b'Zjrh9qxftfKx71FuoccgLzNT9V01EfxqoboXlmXnLssukKigfbLzJHlJIi2iTg1qZmZmFxWheY/wjhWuQW3UnuUVshXSisJBjaLS3Owi2aBuKnaDKJZE47YsD2OqXj8t'
        b'CPRqZXpxaV5lkSS0PIZJezmSkLJDLAaD8QBVjT2kT+nordd8yC7iMfhDS+wormGflqVCy7I5/q6WU69b6BtTobPCLb5fizegbdpr5qvU9utl+w1QvHrBR5QF+an/A/Ka'
        b'gkk='
    ))))
