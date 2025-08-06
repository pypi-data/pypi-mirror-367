
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
        b'eJzsvQlcU1faMH7vzUKAsKPiHncCJKwiivsKhEUFl6IWAgkQDQlmQcVdUUBAVMDdKq7gggvuorbndGbamW4zbWc6TPt2m87UttOZzrx9O6/Tab/nnJuExCTU9v9+3+/7'
        b'/36fyOWefXvOs53nOfdj5ol/AvidDr/myfDQMPlMKZPPalgNV83kc1rBCaFG0MaaRmuEWtF2ppIxK5dxWrFGtJ3dxmp9tNx2lmU04lzGt0zu83ij3+wZeXMWy8qNGqte'
        b'KzOWyCxlWtn8dZYyo0E2V2ewaIvLZBXq4lXqUq3Szy+vTGe259VoS3QGrVlWYjUUW3RGg1mmNmhkxXq12aw1+1mMsmKTVm3RyvgGNGqLWqZdW1ymNpRqZSU6vdas9Cse'
        b'4jSs4fA7FH79ydAq4FHD1LA1XI2gRlgjqhHX+NRIanxr/Gr8a6Q1ATWBNUE1wTUhNaE1YTXhNf1q+tcMqImoGVgzqGZwzZCSoXQ6JBuH1jLbmY3DqkI3DN3OLGE2DNvO'
        b'sMymoZuG5Tq9x8EkwnSUyAXZxc7zzMHvIPgNIx0S0rnOZeT+2XoJvF8LETDPpwTCW6E0KTmasY6FV3QQ1VtwPa7LyVyAa3Fjjhw3pi+arxAz4+bMxfeF+CE+j07LWetg'
        b'yLypEl82p2fh3bghAZ3Pwg0s45fOoStVqFXOWftDDnw+YLUqPSZdxAiF+AjuYNFxdCmeFsYHZ7EkSYHrcEOWiAnEu1CdUJCNmqZDYTKtpiGVqB7viqmA/tzANbgBqvFD'
        b'XRy6PmSldRSp4tKwTZDjmhTVGtCtNautuGu1dLWVZQbgJgFqQFvxRejpaJLzJNqJHqB61BSrUkSRDuMmVD8HX0JNPszg0UK0vf+SYvYJCB1snzk9WUp+IZkft5Qlg23L'
        b'yNYCJG/kYBlZuowcXTp2E5fr9G5bxrInl5F0pr/bMg7nl/HGLB9GyjBl02WFMUxCGkMj143kGMiYkuxfKH1dOpWPXLJEwgQzjGTNykJ9ysAgPnJKipCBvxW/zyiUZiXn'
        b'Mx2M3o8Md0WE8ETeF2MY5sNxf+duxv9+7DRW7wsJb486xH66qSSImV6Y8G7ChLBRDI1GUX8P0sRGD+fmf8B+FzF6wxCmh7HGkoRda6tg/erxKXQsdkFkJN4Vm6aApe7I'
        b'i8zIwk0xynRFRhbLGIJ8p+BrqMltEfzt487kF8F1LzFkCUr8HZPMPfUkl3raK2K3SZZmm0gvrOHwyAhD7bmJUxcqFnMMJ2DwMbQn3xpGx4jbUU0u1BCE9o1iRuG7Y60h'
        b'ED82tyAX716/EBLKmDnojJlWg/etX4iboVZUi/fFMrGoHbXR7CvwtmzcDBNgFikYRRDutA6A2NXJqC4XtcD+WoAbRQy3nh2Ct+MbVlgapqKoDGa2IVolRicBpOsyF0Si'
        b'jpg0ul+VuEOEtqGtRbTueNy6AXXB+Dbg/ZOZySs36j4MeEZoPkIw1n3jilfjA1GcdIf6D1k91R25QS8MjDi09Bn1jP5F5YtuWkYs/Pr2HJxelbRwz55f/vHD9Q8b/JR/'
        b'f/Pr6+9OOfbnZmlSReGZ1CX/si7T3p6eunJVy9YPT1l8Wp8PW9U2Nn1W9K3fx/5t68d3E09c0Ax+uH/VBe2+t3d2PfxAfeBnBbGRU/99dFr94kfnNrYFHjlTFvn37X/I'
        b'/7fmg9DhL7//H5/tTflH2z/lIsswMr/N+ES6Ch/kcGM0bsxSZBCEEopvC3DNUvTQQvapEd20RGfgi8MUuDY9M1vE+KOrHKzQA9RB05ehZnQiWinPiLahm6CJ/fEWgRG3'
        b'rbcQXIO7B472R216Mn1WwBC7YjkmBN8VoEsygWUgyXAKV5twvRGfx7twE24QMMKJLLqqNsu5Hi5SbiIQI/enf37CgwDf4/6TS0zGKq0BaAulWkqgONrKqT0BJq1BozUV'
        b'mLTFRpOGZDXLCMROlbDBrIT1g5/+8BsIP+RvKPwN5kJZk9hes1zQI+YL9/gUFJishoKCHv+CgmK9Vm2wVhQU/OR+y1mTD3kXkQdpbhrpHCWJWMaJWY4V0yf3LcfB9mOZ'
        b'70jIOpKk30HPVUZnzMXbcKMqXYF2xQI62B2bwTJj0FVRAb5tctmd5J/Q9tdcBg8t4RiAW9Cw+QL4FeqYfBH8FWu4fB9NYA1TwmqEGlG1b76Evos1PtWSfF/6LtH4wrsf'
        b'T5xLBBo/jT+E/SEMyAXCUk0AhKUaluLioB7xQjp32XQuH30HG7RY4NQtMngfO+IgDI2jYh4rCWoFgJWEgJUEFCsJKSYSbBLmOr17Q/2cDQ26YiUhj/qnw8RLmE/zfacX'
        b'Sj+YFs/oninzZ805kDL5yzufF75S9GnhPk2t+rPChtKL2k8hnP/8cnwlat6e+B0LjrbtD3kxR92u1ovOs+cLfyncGzNUOkc5tMF/aeqWzyIGLozYNjDlTbbipeBNU1vk'
        b'Ygvha/AWtG9KtEohsthIaLQYMN5ZQRVqxPV0G6EWfHRqtJ3EXgkGOsxIYwQ+aCuq5rfRLtiSO1WJ8bg+EzgLuZiRoF3cWt+JlkF0F+IOVE1QmiodXQJ8nMLl4QMD0TWB'
        b'haDCkWhLGKrPAaZByIjwUXZwIL6bhvbxFR9A3Yuj0bblijTKb0jwdQ6qqi6Sc07wKvC08Sj49kgKCnQGnaWggG4wKZn8/GCW/IhZIVsVxAOB0p6L31iiHqFZqy/pERLm'
        b'sMenUmsyAx9pIotjImSxg7W3S/gsUwB5BDl2DGlkmWPHnAv2umPcWi/mntgXDgCcZAPAEs4GfhwligIAP46Cn4CCHLdJkOv07o0oMl7AzxpFFns3ah7lj2HtYbXrY3FT'
        b'bhq/qqGodsF8Sian4TZxiHyNbkrqAM4cB2WeW4g+LySgGFkcExqtzlR/URhcXFaiLxLuilcUflm49KWDayNeef4Qy5xYIdnStloupHBVhFrxCRW+hVtd4QZdRYctIyDD'
        b'nM34Ou4C3N6Em5SKCgDA6+gGxeKDNgnRDlGeJYL0+HIl3k4haMIgGwzhu6g13EKp+EXUPVTlh7bnKFiGq2RnTI3jF5nzCC+AQEu1Fp1FW24DGYL/mCI/VspWhTqWy5GF'
        b'r0pIQaBHaFCXa3uhxBTMNxPqgBEKHoRuFzvA43igd/Dw0N7/ORTlFUaiyaTeL0Q3PcEIARB0GR+2A4lwmq5j7mSBOQEKVSx42zOQfFHI7Uqwxr1j6Ik7HSdMrLjJMJ0K'
        b'ydZb/ykXUPyBToXhgyq+AeDtj9nBZGEe5SPMS+WuMELgI8yHQoh2IEUxBWtmO2MYfECM7/qiizYy6h17ADSY3aGh9AloMLtCg4hfbLLsPaJKtd7qBhMCJ5gIdwAGmeky'
        b'B2Ac7gNveGjaO+qYygMG4bDZEuH/BPpgbU24goYo26qEd3xxyBAiAObhWoVCuSAtYxGuzcnlGdg04GWVLGPBt9AVfN9X/EyVVU7Wt12K6/wtz3iBJzssDZmuY5s7OHM2'
        b'FPn9lbbPCz8DaNKXRPWPUqep9RSOKtS1ree17epPC18riqFQlqE+rw4uZl7uv4udc2jAFUtcjEZTVa1JU0tKPsgUMMmDgk6MGwEMKZnzAbi7xJ90FF0b5cotskk8Idvt'
        b'izpU6Nz6J9FVgYUoCcZlrXAHRHRrI4XEJDHFVTD0h0IKi/hBkQNZRY7l6+/AF+dF4/MxrtTuLr4mt1EcoVc+kwdYsbWCsJe9xE7vB7ykhPKRVQE2sOHzOKMuno45oNRt'
        b'SwAW66V0FFj7waPcAaytod6B1bVVN0nQFYFRYdyBwNha9qklPzctidAjlAqydUcHDRSYMyDi+rCVKnX9p2mlXwAg/bKorCRc3S66GjEgTqEhgFSnPq+9qOVeVhR2qpe/'
        b'tPRXy3Eeno/1eH7k2y8sFbwV8srzv+cY8cdBjQurgJ4RbqUQ7SxGF2arngCPbWH80u8NmILqQ/ApJ0R0F7cPphhKgdrwc7h++bMx6bgR5Dzxs9wodG4lLbgMXxXh+mHo'
        b'kBMDNTAPt3qGhr7wGcgJZovJhsuIQoCxBINkIQX4qArsRSokCy3VIeCX3DtkACvUCxREm2F1AEVjHxjsicbkXLaJqATkAYRhI2QUZBm/ggJeowfv0oKC1Va1nk/hUauk'
        b'GMCp1Gha1yOxMWhmyoT1iEt0Wr3GTPkwSm0pZqUQS3tox9J9im38gMgU5ZIBESwt4YSs7YcLlEhFUlGwhMryS4LxQ3+7nCORZuF9XCFqVnqXdAiedJF0uHyhRkAkm6Nc'
        b'vqiF0YhPgGTTxm5nQeqRUOD27RHPMQCuX/c4fLa2SGcxgvQYqzJpNfzrI57XeESaeBy6WGuqspaaK9RWc3GZWq+VJUISGdBjaabWUmXRyuaadGZLB0cn/dHPYcBfH4JJ'
        b'VRkNFmNqNkyyLHKGxqQ1m2GKDZZ1FbJFILqaDNqycq1BnuoUMJdqS+FpURs0HssZ1BbcbdIrZfNhiYxQdrHRZHiafJ4qW6XVGbSyGYZSdZFWnuqSlqqymqqKtFVaXXGZ'
        b'wWooTZ2zSJFJOgV/F+VaFOkg5ylTZxhgwrSpeUAy9bEzVqk1Stk8k1oDVWn1ZkJI9bRdg7nSaIKaq+xtmCypuRaTGh/Xps43mi0l6uIy+qLX6ixV6jJ9ag7koM3BzJvh'
        b'b5XVqbg9ULSG9I4I/TJbRyBKKcu3mqFhvVPnZfFeUxJSVVqDoUopUxlNUHeFEWozVKlpO1pbe1rZPNytt+hKZZVGg1tckc6cmqfVa0sgbaYW+NVVpN5IW5TcniabpwXY'
        b'wadLLGYySjKl7rll8zLlqXMUWWqd3jmVj5GnpvNwYnFOs8fJU+eq1zonQFCemgubGDqpdU6wx8lTZ6oNq+xTDnNEgq6zRmJWERhWZFvLoQKIysSniZZlFZk1fvohMn3m'
        b'jGySptWaSgBVwGvukvS5eYpZRlgb2+TTvaAzlAGskXps056mtlZYFKQdwDlFSlubtneXefcUT+beZRAJboNIcB9EgqdBJPCDSOgdRILzIBI8DCLB2yASnDqb4GUQCd4H'
        b'keg2iET3QSR6GkQiP4jE3kEkOg8i0cMgEr0NItGps4leBpHofRBJboNIch9EkqdBJPGDSOodRJLzIJI8DCLJ2yCSnDqb5GUQSd4HMd5tEOPdBzHe0yDG84MY3zuI8c6D'
        b'GO9hEOO9DWK8U2fHexnEeJdB9G5E2E8mnbZEzePHeSYrPl5iNJUDYlZZCaoz0DEANtaCVGUPVJgAIQP2M5grTNrisgrA1waIB1xsMWktJAekF2nVpiKYKAjO1hGGQavg'
        b'yd0Mq5kQlCpgGlKX4NNlJpg3s5k2QLAeT2P1unKdRRZpI73y1HyYbpKvCBINpSTfXHxar9eVAo2yyHQGWZ4a6KJTgVy6BiRlPtUGO1fWS8YV+dALQBiRpLhLgq08JI1x'
        b'L5DgvUCCxwKJspkmqwWS3cvR9CTvFSZ5rHC89wLjaYEsNU+X6ZwDXwL8CY2zaNdaHC+AiRyvic5ZzY5s/ELM1AI5LnWKGJOarzPAapD1p+2QpCqIIqQXsLRLMME1COhH'
        b'bbYAtTPpSiwEakrUZdB/yGTQqKEzhiIAW8eKW0z4dCkAUbpBo6tUyuby9MM5lOASSnQJJbmExruEkl1CE1xCKS6hia6tx7kGXXsT79qdeNf+xLt2KH68BzZFFrnQNqtm'
        b'G6Mh72WMPCXaeCVPSXb2yVuaA5V5SM/x3BrhuzzFu7Bi3sfQR7o37uzHZE7w3rILn/Y02QBVesrmQgKS3UhAsjsJSPZEApJ5EpDci42TnUlAsgcSkOyNBCQ7ofpkLyQg'
        b'2Tsdm+A2iAnug5jgaRAT+EFM6B3EBOdBTPAwiAneBjHBqbMTvAxigvdBpLgNIsV9ECmeBpHCDyKldxApzoNI8TCIFG+DSHHqbIqXQaR4H8REt0FMdB/ERE+DmMgPYmLv'
        b'ICY6D2Kih0FM9DaIiU6dnehlEBO9DwIQpJusEOdBWIjzKC3E2cSFOCc2Jc5FYIjzJDHEeRUZ4pxlgzhvQkOcy3hsXZxr0pZrzOsAy5QD3jYb9ZXASaTmzpk/Q0GplcVs'
        b'0pYAETQQmucxOsFzdKLn6CTP0eM9Ryd7jp7gOTrFc/REL8OJIwh9lQF3V5RYtGZZzvycXBsDR4i5uUIL8jDPTPYSc6dYO/l2ipqnLcLdhNI/wTaU8vE2rsEeSnAJJabO'
        b'tylXnAq7qV3i3aMS3KNAzNEToVhtIXypLNcK1anLtUBG1RarmbC1/Ghk5WqDFciLrFTLgymQQ09qALlTER0h7joNLfaDmT3U74Eoea7bPSNVMfXOjgyYb5mN5aVTWULS'
        b'bZPMvyc4vROZsFdT9ZhNze6QmIiO1UQU5SZi/MEfolCTMnKM3SMyV+h1FtMwhwov2FWZR1T0G12UeQKO5f4tFnEc9x2XyL1qpVra66EpZmKRUheDOoSMJFlZzG1Ct9f/'
        b'D2rzyuS+PX4ziouNVoMFpIeewJmw5LzUoa7Q6h/143V5RDP+eNBsAIJy4CyItlTGyz0AwjpAPJCFqGR7hIQDMhEzv6+7IWJROc/QGMsMWlmuUa+PTQOMZFCoqoh+pTfY'
        b'i+NSl6jyZXwxokcj2NOsM1v5CJLmHOb33Dyi9uP5e76hmYsUucVletwNa68HnsQ5mDpTq9eWashA+Feb0qX3PcEmH6XaZ4Ly+4Qh1Nq2tl1ok/FMkU3061VS2YQ+yqoT'
        b'cQ8yw+ayULHAVgNtTq+DDPRNZygxyhSyGSaLvSu2mHQDKflEJMmW4Clbglu2RE/ZEt2yJXnKluSWbbynbOPdsiV7ypbslm2Cp2wT3LKleMoGPEZObl48RKj4hSG8rpZG'
        b'JrhFQkCWpQV8adfEyqxKWa8mFiJ5WLarRpUywq/bpW5e5dq7jLLM6MzUuVbDKmrPqzWVAoKqIkiFxM9cJEuayJPZEnsWohL2FG+DGz7JQ4Wp+VQcIAM3latJogNEPKU4'
        b'QMVbsYS+inlO5EGoj2KeE3mQ6qOY50QexPoo5jmRB7k+inlO5EGwj2KeE3mQ7KOY50RSbGJfxTwn0uWO63O9PafSgn0DindIie8TVLyk0oJ9AouXVFqwT3DxkkoL9gkw'
        b'XlJpwT5BxksqLdgn0HhJpQX7BBsvqbRgn4DjJZXu+D4hB1JzLbi7eBWQrjVAfC2UMV2j1Zm1qXOBxPdiP0CHaoNeTXSL5pXqMhPUWqqFHAYtYYp6lY02ykkQ3gxrCVGL'
        b'OZCcnZZCEsG8vQRZFjnDUMUzxOQ8D5Bxls4CpFGrAQ5EbXki+Qk87F64F5M/mWbS45tmG5vgkpJGT3dKLMCVOMQqSkkUlN/xKAPYRmqj5kD6gdIQFrqEMs/lhMBbtDqY'
        b'FotDT5wOnK5FV6JbpXbG/vlUDHToj53ZDF54dDpHdGaT5mp5yUKrKyJJmbBq5GDMzHM23hk1Z90w9BtaVuut5au0ZXZFNiWClIsj5jDZpihvLGwMPLq9srCDuU+shPsN'
        b'RBfKzJmFuDYb746lrCxuUPkw/YqE0nBc78bISu2M7ErWlZFtEbf4t/hruJawljCeoW300cTUiGoCasJKBBp/jbTaF5haoVakCdAEVjOaIE1wI5cvhnAIDYfSsA+Ew2g4'
        b'nIYlEO5Hw/1p2BfCA2g4gob9IDyQhgfRsD+EB9PwEBqWkh6UcJqhmmHVkvwA2suwJ358NcMb/TSKGs7WW6FGphlBexvIj6rFr4UtISPzoU97qZGNvholNaMTUReQYCjr'
        b'oxmlGU3LBmliIU1UI6EOIqE0bYxmbLVvfjDEhkCfxmkioU8h0EaYRt5o92sIrAkqEWmiNNHVEqgl1HakH9cjmU1MwWflLn4c6ydz+mePlvEYhPddcsnRITIRc2sT8YJ5'
        b'RC3CiVfGI2qnQSQBufQRMbR5RG2biZlNb3bTBHt2Uwp5xJMsxNDhETUGINAg9+nxU2sqASmZCnSaHt9iQA0GC3kNVPNiS4EeeDtLWY+k2Aq7xlC8rkdCTFh1ar3NCMO/'
        b'RAfsXEE57Ngy2naPYM6ihbyVh2kiPIolTiDoZ/ultjrENMfFxcq3RlzjV+NT4mczC5LUSrYzG32rQjdIqFmQLzUFkmzyzXV6j2M0Apjmarnwa+KV4TJ75F86311dldZM'
        b'Xcscc66j5gzFWqVbEbeISSB1qMtlvVM1yeZUBpiFKIFsXmu2OVMbLG41kH+RMwEhWOzoSK6UzSDlAXUUy6j1oMxaIQMEOkGm0ZXqLGb3ftm64Vglz73gkz33wHHU8QN9'
        b'GP9DfXAFj0myTPqXdGFebKY91dYxs+e+EHJDED2QCaUsrwxQP+wCrcxsLdJrNaUwnqeqhbcj4WVUqEmmhiogzPdfpjcCGTIpZekWWbkVJJUircda1LbBF2kta7TkqFcW'
        b'qdGWqK16i5z6FKZ4Xwvbtpgkm2V7kxUTXWGk44TRScco91aLfUtNskOr2bGYxIXRaJJF8vYqq3C3qQrkbm8V2QykJlEhizAkUA0PIzYME6ktVcrGx8fFyCbEx3mtxmlP'
        b'T5LNJQEZDZDqSnQG2DXQR9k6rRo6FmXQriHHnZXJyiRlfJTcfaqewtxYyntEPDsqhJExTEpcgiVTq7cyVmIr6LMsDXXKcH0Wujgf16bjRlUsrptPjE3TMuW4PiZbgXbh'
        b'pswFaehSWnZWVnoWy+C96ITUKEenaa3vTgpgIhgmkolVS89MNjDWKRA5chGq91gn3o3rMnEjvo7vRKO6JyuuXidlhJtptRUbfYk/XtyW0s2Zv62ayTtgyvIG8i5dvD9X'
        b'mlIRlQG1o04hk4zqUPVysRnfi6NOabQStT91/wuWZej0E8tEjJVY8Q7Ee4Z66hveORPXQsX1MaSLDfLFTj1Dd0z+6BpuRzd024vucuYqqOfjq58OfeUPvlvipDs+PHvr'
        b'+t2dzbe3CSS/8YmNHZl9QjZw1oSvk8IDt/71XOTcfTvmjaoeU7ev2tA988i0u2/2X//mnKK27LfPTyoL+vr8l18fnxEy/2+DPlCbfyFs+kx93P/hgsG/3fnr0d9+deLl'
        b'njzVR1fXdaw59Yf+iQcnf38iWn53qVYu5T1OamPQTZjnuoRev00BEzRGUIIfDLZQz87TuANdQfU5vUt5AZ+DWWeZQXi7sAqfwQ95J7J9yei0P0wr6twsz7Jb7fZDNUIJ'
        b'OrLKQn2SduHDaB/UhXej/XgPXUZ+CVmm/wihv9BiIWaBI/GlgGhFZJqCY8SD0Rl0mFOghvG0kXHoYhqUd1q0UNxsRJ0CXI9uz7QQfV3m8E3RSjneBRyaOC8TXeQSjaiZ'
        b'WgXjOlUpjLXJaYHETGhCRKUA3UdtRgth+XA1akTVZLg2lo10z7bE6Cg6CeCEd4iVFQUW4h+oQlcKyHDqY6KUJCNuRPXoKm4CRg8gzSwKQN3oDm0bPVi3hOSk6kxoWwEt'
        b'o8OJ6IAA76hE9fz01OM78U5N47qSAMovDkK3hahej+7xBpN+P9EBrtcphlqdktVlNjMbxKyY+rmJbd5ugfAkvm4SjqSI2aoQO0V2uMdk2ztCLU6JU5ppOnnMII+Z5DGL'
        b'sXvizGb6NmiW8KV6K5npKEUr8eDT84h0n4ADs4U5NMy7bat7x12MnlnbL7UrJT3cwKzkDZjZbDnb41/Qy06YIhyT6OTRNFmvLi/SqKeGQC3/IDU6tWhPe2xD77a67KxA'
        b'JJANjcJo0K+Td7A9Ao2x+Md0za/AwWJ46pkpDR7hUN6UDi+Ph/M94It46MCPaTmowJWx8Nr8AEfz8j5Zjx/dkVK+I74FdsrutQuDHF0YOFNt1jpYgR/dZLW9SQdn7a3J'
        b'oY4mR3llFH5k42V845ICu/Obt7ZlvW17ZS5+2sClBc4yhLf2R/Wu+A9wJF564eKEQP3suBrG4Wf3Y1wQntKHSpCtG5KbLKLevvp9I+YP5b2iykq+YH7d8GrDR9IXpEcV'
        b'zNSHwm8Ug+QcJUBVY+fY0bgCHXZgcoLG8fXNlCigBnSaRTfQARdU7oTI0SW0qy/PN58Csrmc/Zw2w8+4qmAndEYz8GUGPFlThGNZnoHHWNbuz7wFft7tw8vNrX65X4+P'
        b'bbvylv5is8Wk1Vp6JBVGs4Ww0T3CYp1lXY8Pn2ddj7hSTaVT/2Jg5o3lvNQqsKhLe0RG2ASmYn+nBSGYPdC+KAvJevs7pM0AxzUEgfxNECWBNjjwr5UCHEgBDvwpHEjp'
        b'2vtvkuY6vdtkzhKQOd8TeZA5Z2g0ZhAqCGes0RaRbQn/i20WczItte9/CrGTCkVUolHLyqylWidBD2bIrANBScb7QBCZzay1KGU5APZu9RD8UE4OanTlFUYTkU/txYrV'
        b'BhB6SFEQmEzaYot+naxoHSngVom6Uq3Tq0mTVEYg9pZmJRmpjqjcYPPZqrTJWaROtzqgaqtZZyilPXJUI4uiixf1FDMy1zbaMqIsce+7W/5Ii9pUCm1o7IiKlJcRJaKZ'
        b'yCzm1VYyu0UmdfEqrcUsn/T0qgAebifJZrjQG9kyemy6wlsx0vIkGfV5WPaDng9ea+G3ySRZLv0rW2azw/Oa376dJsmIChSWioqoy5zt8LyWJRsQhFt4ypblmCze8/Fb'
        b'FLLyL7SNGFl6bo4iMT45WbaMqD29lub3NYitM/IU6bNly2xniSuilzn7dXhvvBcdEEGcD8hIRc7WxF6LAwKBySyDrQHb1Vxs0lVYbOSNwCnxDad7a4bebAT41Wo86hAA'
        b'nEhuQoz09HohuthK2WxekUC36Mhci7q8nLjHGUZ6VSnQzQCABR2osG0tjY5ecKSGaV2jA6KnXQsrbttw7vWQf9lGi5bfJnTzay1lRg1gklJrOQAa9EW9CjYgbBotzE6x'
        b'VmYE6u+xHn5IZNNQDYmZH6bO7NQlpWwuIDU7QvJYi/O2I/oUAHVyfVOxHgbM39xk1nouWWi7vMlYTHvOn7JMLrNYKsyTYmPXrFnD37Kh1GhjNQa9dq2xPJZnRGPVFRWx'
        b'Olj8tcoyS7l+VKy9itj4uLjEhIT42NnxKXHxSUlxSSmJSfFx4yckTpxaWPAD2gtCEd19DUOzrVQAPFryjDlTnqFQZhPnvmjUEYObyhlmdK6orB8+Si9ymYm3aRPRTvQQ'
        b'3uOZ+BFFVAvQLqS3+MgKU8wx2Wm5jJWwJzPwGbRVZSfxC3AtuTwlQ7GQeMoujCTup0twLa6bAlJ/ExB/kHwv++JWdBDtpBc0oZPD0RncBUJ3kzYbOAQfRoQPcVJ8E3VS'
        b'TQW8XB2Fu5Tk/g7ciNtRK66HFsgFLRwDRYX4bjq+TjUwC1cp0L6luAuk76xFeE+F6xjnk/OHRmBAFlXAIyczA7cKyUUR2/zx6coM6jg3tHQ2qs3wV8ozQGI97sf4ZnD4'
        b'+NA8K7HzmYC3oyO4Kx3KLsftLCNAB1i0ZT66biVcxbjNy/1xbawS16WjB0txYwzqyAABu5ZlZPNEwrBJ9AKfmYvxdtwVG8Uy3MopaWzyJvyATmuZTbnCmMuk2WsGMFbq'
        b'ZH4vVJ5ZbA7ArfgGaZRlJMu5ebgWbaUNTtajSyQxIECZXIb34huZ+Go03idgBqwToIshQ+jBy0R0abm/EkrDbKWTeRAw6L5fP3xHGGTBD3UX227yd/OcSehQvJblh+KC'
        b'RR9M0P3m/be+bPlycm305Q/6iYXvpf16xb2rfmY/3QvbH3MJ9U0DhiXGL1W/Leo6EjfzTM1HW9WXlWcEMUvLE8zvhL5a+eKj248/XLvms6ybBz+Rj9WLk6e8qsv273lj'
        b'X8n1k2Mu6XrefaPyn0svvPHPyo133zs7oXHX5v+I+8UfltyTv/da/2m/HHhhGapdVP395LaqfzMZv4le9yBYLqYMJyzcHdSM6nv1M/j4al5Fg/YMsESSCduBbuKzFBBx'
        b'Mzr3hNaCYaITRbgJ3ZFYyPSh86gGtRE9Ta+SZhW+R/U0+BhqoWqhyNkaF2XFMnTbzuXmF9JqcDfqQF3R2Yr09CxVDG6Us7C70P7+uFuYgO+hG9QLFzVzE9FWdFEVE5kG'
        b'nYGFRBe4dbhmnsudIYE/9VIfr861fmqNpoBn4igPPdbOQ6dJWSkrYfvTp/OPkF5EImGrwhw8cG8dNm1HAK+KyGfsBm/kahHTcvJYQR7PkkcBeRSSh5o8ihgX5YdnN2F/'
        b'vs7eSgodTRQ5mghwtKh2tEN5fA2pwoXH//1Y7zy+p/HJfXukGmIPaOOZegJ4TtgeFKvL6V9yCYu2x9d2Clys7fEnfAtwi8RGjO+RY9DFfk5Imehsgu1IeTFh9P1cWP1A'
        b'YPaDbOx+MGH3S4JtzL4fZfb9gdn3o8y+P2Xw/Tb55zq925j9UmD2m3z6ZvbVDls/GX9h01OwtHOIlwSfWwZ0FeYNuFXgFdTO9xYSfiJGVmoyWisgFdhotTudMpYX6Qxq'
        b'O+cSBUxNFCW5PMUlKgKHWSjpoENqdquJSNH/Tzr5/7N04rzdJpGF4mMcyrEfkFJc9idfno+yV+CRVVv2A7aiXpvj9z/fjm3L2+J4btdgJMoeE+VnDZ651DVGwk7qytV6'
        b'L/zwsj6sZUHK8Gwv67XHBFPx/S0yGleR/pIYpSzLBl1qGpYZi1bCwoPs7/nQ0UCko5TkuHib/owAAoh2pLplvZa0XjvhQJSTZIvMVrVeT3cGAE6lUVfs2I3LnAxx+xQQ'
        b'bYjWdRmoh94yZ2PdHxThSPEnxDgXk9D/C6Swmdo12lKbQc//k8T+L5DEEpPjElJS4hITkxLHJyYnj4/3KImRf32LZyKP4pmMP1xujuOFrLjkL/xrZwoYaxJEluDrqE2V'
        b'noV3xaQ7RK0nJCwqXuF9FZvRfd8kfNFMxRZ8r6KEl65Q9+Ze8SrQak0mrOmZ2dNUyowsYHC9Vrscd/CCWz2u90XnUGOulRxVpePjweacrBx0A7fYLkoiB35L8B4o1IRr'
        b'QczyA/GEcOO1+E7ucnQUHUanfBl0Ae/3z87GV6kYgxtXAdrNwI3pWTkqcr9S3GIEYlnETAHw+O3oCM2EduP9y8xRWXh3MToUSfh5ZTq6FMkyw0tFok24k5dqT6ALm/3x'
        b'LbR7oQQ3KrJBAuOYODY0UYDaMnG3dRzkyQbWfhvMRu+5N0hF6MZCdC2Q3GUaj+pFa/GJpXyjTUPwQVvP0mPk5FJUmIiz4fiUAN/Dl2PoWj2cLqALGVdyyHomfg5jJezq'
        b'UnQdH65CO/3FDJPH5E3CXXQJc1D9milD/Mk8wdzuxbfSQARtxM34BhFL69EFCGXi3WlESls+UDIPn8JXqCyOGvBxS9oG3EVmnUnPTudvg92C9+MTktREhkroqBkf5uOP'
        b'D0Y7BqP79O7XWCYW75mt/+f3338fXCriwar/YsnXM/L4Y/0hs8RU8oxLbhIFyqIYurLJA2Rkehpt4nxazGJyRXNsxiKAiTTckBspB8hI4y9kzgIBCt1cSGZPbAhg0YUV'
        b'ctxO72RG21C7PBe3JmYIGBZfXKFk8MVR46mcji+gi0J/2yIt7AUYiYe50cWjTrxPyKCaRb7PoDMjrcTk0Hd4/17BeEEkbs2VoK14R4DSWRCe1k8ciFqC6cXMAKSncL05'
        b'Q5GTBaNS4QOa2GybQCzHB0Xo+hL8gGojVm9A56P5q3PkYsYfPeTG4TO4Cx1BJ+gFxP8xOYd7UczIrJvUYX+IeCXwb4x1Gt1H0/ED3GXTfPD2GQBguC42J2tBpK0+YgYR'
        b'j046bDSOoXNSvAck0T1U+YBPomp0KRrE9UZjTBTLiFETFzt9DL3Mt6wMHVIR2XEU2sdwJjZFjZvkAis56A+eindCoWh02FEoaiWFBAnag6/SUiBTkUKT/eiF1+gqOoWb'
        b'XUdZiK7irgTUqVt+hxOap4Eg9VFF1oo9U7IF8cE7SvXG5CObv9sXUx09P/f0B4FJQwqFkdEjrs+W77n1wquyBbPfCj+yf9T81Z153Y23Tn71yvp/PFqnH/OXzwrnvJB3'
        b'uiNwvO+QiED/19srPnm7p/bXmoyt7y8Nyyk6sPf69y+l7skuV+Xv8X1p6kqfGzWHTwYufvV0feep7JoXWoYf7vD/9su37r/10kt7At77U8obU96Y+1jUOi1hyzDlo47o'
        b'U+9sTd66atzHQ5fEhL0+OOqbw1WdYYe+WLrbNPrl+OR3R/37xVsvf7772tHzurxCzbERq7o/MbUVt8tblp1pfeH3385fHPyHfSW/+w/J675flv3q9QkJqyKMX5Zr74ve'
        b'/kPSW2veXHck95MrNc3/rd7enRa3fsU3n3RvPNRcfzTwzvEFH654c9atLX/94Pu5/TZag0YfKLi5bYBx6cLMy19Fp5aE3j3zxVdB/7XAdMV3pDyAv/C3C9dHZpM7wZ+0'
        b'LNGXWIhAvhjdRQ2qXjOLIrIZXHUW+LmJVB2B7s+a6KqxQO2+VGMhRrvpfW1C/NwitkjlZBcStFigR8fQHnpv13rU4R8dpZSjBtRFLUN8n+HQmWFJ9MIvLerOiVbi2mKA'
        b'mroYAkm7OUWhhN5ZGYYO4suqzCgxas1muBXsBGugJZwqA8ToQmZWDMcIVfjICBZdWzuNvyFxfzC+CTShETfpgqgZiHgDNw7dQVcs5Eb1BdPxFt5gBF2MttuMONuLdFXQ'
        b'6zbxjeXjnzw+xA0b7SeI8kiaawlum2smFkYKQrToBIfAvtqPrgrQFXwF1fBdqkfn8Vmig1mDmnrVMH6osY+rt+TB/0NaGU/6mUCie+gVxamOJo+wB5vpDye1aWh69TTk'
        b'DmZeS0NDHLFQGQap4ayY2qkQmxX+9rRQCAdSKxY/jt6mNsBF49Hbqk2rI+U1K1ryKCGPUvIgtz+adOSx0qFt8aTQ8XmaS5z9+DpLHBVrHTWtdLQT4GiiV7VD7sXPd1Ht'
        b'tEd5V+14G2ixyIkBI+frrle+i2p8ahh6xsrW+FGFjH+N0HHlu6hWvJ3ZKK4K3SCiChgxVbqINolznd5tp+7VT566k8aGM09ye4E8t/confMLYclbYUzrCGAXaOyuMaLp'
        b'fxcEM8z0QunBRbEMT1Gv4qMrzKhRslrACNAhtCeQTRm1gd7QjruGTspFjXm4cVHWAnxjPr6xKCAZb3s2Lo5hhg4QAHG8h+5SAjdu9Ohc3Jg3Pg7vSiKM5moWXcIn4Kd7'
        b'Be9u2rIBn8qtSLdVxjKiKBYdDhxNyVAx3ocv0/vdJzO4tmgykNVrNKHfJnQZn0I35+IzAE5jmQh8fzolaqixYKEKX4tSxiUljOcY8SYWPYdvh/CfZmjTA8nMoFepx+Gt'
        b'jtvUQ9ED3boP2oXmP0Om+V/dm5NzH8iQ9ObHqi/PTa+vnv+HHa0+IAKXdHX+ZlHUya7E9z7aOy8tedhWn09ffPGljz9Yfnnm/ml//tfff58dHqapPdFa9fOAyIYv/9n+'
        b'6paQgBWWL0YOXczNiY/xmx167uvp61Om+idcGjFyydlXcsXTfhf3u/x02fgvEne/VBH4j1v7j4X6vJBwec03cfvfnPnpX3LTB3/eoWr6KvbjL9GNxN+1dox7YftYbFTu'
        b'Pu67+S9/enzt42mPa5b+RVb11aO52/NGlcyObDhy/ej7d37ZfP4732f/WnSw+1J11zeC92+9e/bMO7G/UazpfulLUc93QSd+M/8XsyrkoVRVPADdQscAb27H13B9rA/D'
        b'oZPsIli9O9SmDx0yRNrxLWodqgJ8m7+JIrcg9NwEHt1G43Z82YFw9/IWh+i22ILqy6Y4m+g5oVs/QJGEwFhxMzA6T1KqUehuiRDdpv1jRytU2THA+jXFovNCJhA9ECjD'
        b'CnDLIEpfNgAPdAfXq+jN90Ko4vwwFp2cHESvxsf70HbA4ba6Z8bZ7+yegvbxlPI8vogfuNydj7cIUH2CcYyJHgFsRs2RKidL2mFoNzGYRJeEg3Ftf5olE1+JUdkMY4ny'
        b'v5ulRpWhKwXoYkAgpbcSKXYmt860FjfMouR2K/SI9Ng3U0dsZJ2sJIOGCYr8n2XxA5q+efjcJ0gtPojv6fEufIG/K/xYqEAFbPoxF73/M8DM01OBAzJ8F+q3X/PvG0Au'
        b'+ke3kvkrpE/mRagy8GnXmzsnJdDEIeGoU7UR9i1wsrtzyL2saA9nrCh9Ojz8/+nrAXbTHP5bAZRklfSSrFhCkKi5JDWaFBJyxXHwlydfUoKt6Y+QEjH+uIGEeBNLiSPd'
        b'8fOhcISQC+T6c4SwOZvm8B3giZdPL9no8eFV1OYekdmiNll6BJDvx1IqkYl8VcdkcBAko4MqUYJE7pm9RAjSSDtB2sK87f1DBO7d/t9g72XzLXn8iZvmgXfwstjdSmwa'
        b'XL1NsWLSWqwmA00rl6nJAYGTnuaplOuyVdp1ZqinwqQ1E8tKXgFk02iZHVp9mzbIk1L8SYW/nlejke4UrbNoPSisXOir2HkCnUz16V3OuKNoNarH+1ETqgMCug9dQ5c3'
        b'LYHnVXRhAaoVMRFoi2D9dLyLikwT8V20DzeDqN85lFEyStRawH9G4sZy1EJJL6pfogDB+6SPSqkUMOGoToA68D18k5Lt8JXkezhpAo4plCqXqBhKm1H9UHTJUVY8ErcW'
        b'gXR+Gp9MYKLGi3CzPAXX51JRDt0vmQKiHMhxpfgqL8otzaZanDnoANpDCDy6EuJEljck8Z8/2mpA+6mgx3D98SWQ9HA3OsoLlTeW4+pcvgiHGll8CdUNUabowt4/JDRX'
        b'Q4aWfvlZr4wI5EDM+/CbkvzCgH2a2Bd890iSllY0B9wLnPbxktU7kz88kXSa++bI90dClt45ceWjhl98pXxhT785DWNfO992ttOnujPmM0vHRxVTPrxhLP3szzeOya+N'
        b'U43atv/7gNdvDlxwrTx62V83TcnLfjjmvRWHU1fv/HPQ+188/tlq/LdvuexhYx7PK5KLqXF4xHgQTJzPW3PwVvt5a3/cSaWUSHwgEhAyvZMYHRfw1xLvHE/TcDO+CfKE'
        b'MotjQGp/iNpZFRCVozy2PT56BlA2gqvT0TViU++v5fCJmFJKHxf2G+Ri647uuloq3jbRSsKHLgD6pC5yoVBGETorF/8ARvFi4ag2F5DdRtHoyF40qhcKQnleHv4SpEjO'
        b'a6X/FosiOCdcYiuc/YPmjyZ4/PEJdPXcUxlA2proYHuEFWpLmfc73Wcytruyyekl+SyE2HGvu/Cp7nUXUHNV4YcC1sPJZS8GI8jErK4kb3q9My57euc4MpBJsvQSWRR5'
        b'i5IBQjbzOnKCpbRriestURlHKat0FVExtCEbujR51jibyfWCGoeeW20qLtNVapWyHKKWX6Mzax0okdZBB0Czq2UlRj2Qgx/Ab2QRfd3wm4THb5noQnp0GmyX+UTj1PSs'
        b'PCMrE3XkpQF3UBujBMYhDe/0qShC++l3Ejbn91PB5srIUuK6kgzg4fJwLTCaC4A/UUSS62VU+KYPSM7PAT6kbEgbbsoCrvACVRcIUPs6PYu2RSRayTm2cUZ6tM+wbIZZ'
        b'y6zFh1E9lQSkuB51RS9ATTkAUgsZiN81XTew5xOR+SakXrypntKYSj4CtXNzqnz+s7njstmj7GpWXJ13s3Yr6/vLgzEtLwwOHZVrkr+2/c2Ml+r/PW1q/cRR+96Zfeuz'
        b'13bnV+3RvGrpyc+8/u+zyjWGkPpq5urqPcE1r7V/Pmfga375YS+N2h2anLJ4vE/gz3Njpqy/ObD5YMWlrweNC1ae+/L10W8eufXdoT81/s1o/NfNigNH6r4++k4/xcP+'
        b'L1QN/nPGW98OC1x8bnzG9xff2HAg43Xz9MVDKiOPT5szbNL65wPlQTx+OYL3mehcA/Sjs/jBBBZ1FuVQXhAdHbCUcKaEYaQM2Q38ENdzG9HdYJ77PVuxEHcFR+Pra2y6'
        b'G190jkOn8NVQ6uyzuXg5LV43Hd8C9l6czQ1BN+fToonoThWuX8bCuinT4QGoC1/hcPcCdMumYpLidtUKfDgG7c7hP2jgP50DVrQO3bR9JSAQ7yAf24vNwbvQReJPtImL'
        b'guRG+8d0di0k1EOuxE1kcLG4nQmKE5SuRad5XrQZfk7xWHfUYNtd8INQJ+3dcPJFrFhyLKFQyjlg4WsAKx4XoB0jy+ikzQLRhLLksXgHOgsynngyN2Aix3dsLzqB9qoc'
        b'oOrrrwnnUFs/fJ6KOzELyCcCG2FSinPJnMzkIjaupIh4NWqpdGKd0SV0lDDPswP5ddqVaqBdQrf8YC3EqJ2Lwbtn96Xm+QH87YSzhWT3uprTkB9fXlEjoU5DUuBq7YqX'
        b'YIitCnBgVFKax9gdti8dWBgXVYr3TnZwfN7e6+0r4fH9E4h9e/8+vnzg0g25zWV7DkNc/B1+0IBYbP/kIv4PB79hT9x1RazzNcbiggLqidQjqTAZK7Qmy7qn8YIi5vjU'
        b'Xodqdig3TWkUHQ/P0Yf/j6vd+lxVEzmf+ZixCTMSTij0Y8XfC8ncfR8+BmaT5b4TC37kX2GgAADAVkv/WACK74UC5vshCwZNCBwsYSlf54MOLjGni1fC7jEHBgqYgKEc'
        b'bkM1uNNKFJuoCV8b4o/ayTZo8CcHLvPJQcuQBD2+JxyFqi3/m77P5KbBslfvSoF8sunx1BLc5JvL4D1rGWYEM2IlOkUpx1R0fbRKia7EjSdq6ZvoPrrNrh6NT1upv+U2'
        b'2LJtNtUP7sKnHLofOW6gE7MpE+3FD6JxfXoM4bUShYBS67mMYJHulZYMgZnA7K+1Az4vXP78lT1tzfE7VrPFPh9zZ3dI/Qemzoj5U/jZ8D/tyCxMVn0d7Oe/tKXtpbPb'
        b'43e0bW9rTd/Hjg6jH8pYuSJk7eHX5CKKfgdWFji8JdFFdGkel4hODKbY71l0LdGOa3CH2vZBvrzNFBGZUDXaRrTmdpV5Kr7HKfDOHP4DG3Ux89A+o8pVTl9QTBOzUd1s'
        b'XIsukkNdPnEFp8Unh/XlEiMFGQu4GG0BsXCgSKi/MxIaTXS+BOkI4Wla79hNwh4hKdAjtjmruX0RitxCZ9rg2A2k5AjO7hu5xfbzoXeWkYfWOnwcPxcdmaFIi8lAjbH8'
        b'Ea0M789LEoWjZnzADaT62f6a/+580Uc0uewC4JbTCKp98wVaIf3CHkO+rdfI5YsgLKFhXxoWQ9iPhv1p2AfCUhoOoGEJhANpOIiGfSEcTMMhNOwHrflAa6GaMPJ1Pk0M'
        b'7BlW00/TH9qW2tIGaCLIxR4aBU0bpBkMaYEaJaSKqU+OUDNEMxTiyHUcbI0QSgzXyMglHC1+LVyLoETQImwRkR/NwBIO4shfgeMvH8s/hXwOp6fwyXfNiKNBUJdfbz1P'
        b'ltGMdI/7aU/NqKNhmtFHufwQbag2RDNmIHMirI3ZztLQWHuI5ginZoy8t5IE5sTHdvVIP2rg6EPnSaSRa6Igrr9mIMUycT2+BUCS1HOBNaau5m46elcBgzeVFNPvJ4od'
        b'mnnRU2vmn9Ifzo/XzDcoYU+u/ZOAmV6oz5UE8gfm+/WNTMQUkFbnFxq04cF85Gn9Rvafi/NETJx62aHywQz97hTanoXvRo138bJ3PchqwvU+TG6pJBh3+tF6vho1kpm9'
        b'/AxshkJu6Jg1zJ/tfaT+hLqeid9xZtL/1IeBQxuuBmyJkwrfz55ZKLx54pVh0unF8jl3nxfOTitZpT98b/OjrzMGBbG/KnsjafLeMdKqtuCVKRMSb71TP/H6G7/6WajP'
        b'e6evWOf3T6ta+3X/nx3alJ0wsOuPn13uKvzFwmntzw18Jmuz3JdXYbaiXbZP2aUr0B50V8BI8jiLykJT09LxcZCOD6Nj6DLVSovHcSHAGHfyvt4XUPsU5/NKdIWcDvAm'
        b'1tuLqTYWytfhO6hejrpyPEzOmIGiMtSQzJta3w3GDbzfenSkgs9UP3moDzNgiHDyCHSIHixCjjbifU76ixpHoXtU091ADgSPCFAb6kYdtG+VqDPXnquQ4PYsdJGBTK0C'
        b'YHR3baZ8calQi+pjgXFNh1pv4P0sI8G7yOevDuMjFnIj0sbJQ1H9GqiD0meoCYQeqKsuB10Ehne3UsxMVInRftycx6Php2Yye53Thzmj9wQx6yeSsBHUSd2mZ2WrQh1b'
        b'6ImPRvJa0R4RNXfqERJr2R5p73mYwdjjqzNUWC30XrBeBtTZJl1k2kbet5DHdsbOe2516WesG6F4sw8W1ENvf4zftaiADMOr7+0MzrZXnNtxuKAP6b3i1M0DV2lSEfzz'
        b'IzyRAwqc59Jrl2bbu/R4mFPz7t7nyh/n+N67ct4anudoeGi6PbPdbPNHt+vwNifAVFCu8+5+neFotj+RNmQlJmP5j2+v2rU99Vqv7WU52gun7RGj3p/YmrjAYrSo9V6b'
        b'mu9oamAeyWg3/vXa3v+cJ7fHL6ZyjPsnDykdWTuJt0qbPq0qUzJyDU+kpAre1KuQ08ZsD5/O6EaX/JfATFRIpqR68hXfNHWLJvJPKrW05NPCT5m/HxmYe/DFgdsGpixj'
        b'ThQWvin2aQuVsxaiRKpC+/BWz5hPF+WE99pxWx/MLBUDKZIjzs8OJLeYcK9VIc5o4umdvHPdcNHlPvSc7o08+h7+/Z/86K27UGVbwqHDhNRXZHqyNL9seOc0OkkL33oN'
        b'ajj0dzKG927rrnwrF5qJ51PjiBL+M8x7NEufP4gOout7OgSv3FKnqSsLyWclfZiV98Xb4hbKObp+QMy6Sm3rl+L7xAr2rh86BESVkHnVMHIajR+g53BdlEJJ5JxtXKIK'
        b'nepLVAkqoLbNuiptQZHeWLyq9wt/9pVeXjXQaQFcc7t8xlZEjXLdpZZ9jIs2ZC88lroBwPk+AMB7+y7b2A4DBPjsn7UVABQIfgIUuH0VkmU8H15RKDgw4xv2CwETWeG/'
        b'ctrLhmTevNQXP4hEF0bhM5C7CjZjSxBVvOIrm4KB5TqErsAcrGfWoxOonbd9rMsIR93jXBhR8j3UyGwFyyShOnHgkuHUQrR7CW94LEswS+tGD2aowePBYTmSk+LaAKaC'
        b'GDwaV8xgrKkQPT+KKI75q5+I1SOuh2bslo82OHK59qkNH/IDzgl4QopCqYtjKj40x0nCn4svUCHfgGt0n46YLTLXQp4b3YVjXiUa4whBYWrTotdmDlj8Vmrc4iL1H8Wv'
        b'xHx6/KW3Thf5qX4VvHrXH8+OtnRpNptQv2/+Ojjkw7hDL9a2zixF8pGz8tQRo2an/uUXh4oWKzMzP+t4MdB6r27U4a8u/zbv/YmfDO/a/97mS9fkssMvL/6vHcv6r4p/'
        b'6/130wvW7vy5qDnk3Tc2b3r/4sj2/zoo9+FVlncSyKd/HcrS6EUM1ZVWDadM6gLcjS/08rxb0Zbe659g6lso34hv4qMTPeNPfvcp8HWyAZl+PE+7FbXF+EfZOOMsK74c'
        b'ZFMhD0ddQnx5Fm6k29qAL+B2alVHreRwHbChNfg2iOL2usVMHDovHjJ2Az+URrxrqcMncTbu5t0Sz6M2mlwsR9t6NRf4RAZVXuDTeJvc8bVxr1pSccEak8722VcXHraA'
        b'mK9x7DDgYQfZzNqkbFWw00akBV0/Y602lZq9cKicqcUVCzTDY7kbFjjbx6c/3RrPLhY6bVCX02Xbt4upx57j28VCesYlgv0vpPtfRPe8cJMo1+m9LxFU5Lb/xdn0ONof'
        b'XYdt3Cyowg+ICdlwdExE5WTeQfgcqh4RvQDvRvsUixXEAsUnhBuGuvEVnSE8TWgm92iuSrR+Xvjb/suf34PeeeHdF67sudN8Z/udpTE75AdH7LizvWP7xMb0hhEHtyYK'
        b'mIvDJCuG/gNIPIE5dGYQAhIfq8RHiBoHAfRQQxSWGVwmRLWoBV+xL1Hf6nJxAfXkoIAQ7AwI+kBqBOIy+zQrrxwXO1kC0i9SUxWVKwnoEPKxT+SkYNAKD50bGBzq47PA'
        b'bh3xDgVEi10jAjgQU9UGgQWfnwALHjkCd3WEKJtfc0J+OEF+7mq0haw3yKMCfI/NQqfREZ10lq+A6kg2/Grh54UqdaQ28qN0npMr/LxQVxK1//PCR4WrSr7QfF7I7YpL'
        b'TrReOxNnHVB4pfLKmfi6eGFixVkBY3kgfVy/pJfzfSpjGZePkxMto9OChzsvuEnC2wMRY9R+TnPdW4avar93sDrgWN6D8DC6LW9zhPfl9dzkI3IM4X2hp/PbXWTb8KKf'
        b'sMhuBN/zhrcvMuG3cnADei5XsRi3ztEkpgkYkQ+LtqHtuFMX8128yEwcPo4NPPB5YbpjmdPUnxUq1Z8WfgFL/UVhsLqsJLM4tBhYPz3L/GZXu04SUT8Ddja1FWlC11A7'
        b'seVei45RW250H217+k8Q9wQW2C5idVpoFw6+iix0VYTTfLsUsOtCXHdtj7hEXWwxmrygeaHpiLedfhgea9xAoT7cOyh47Zo8iDdM7rVTJibKPQG9gv4q7bqegEqjtbhM'
        b'a6JF4l2DCT3+xeQSGy35qmy8cyChR6LRmfnbZ4i5c4+oUm0hdxlrrRYQb8l9u2T/9ki1a4vL1OQ2WIiSS+iRnIkIHibCdnm6NZkczuXTGonBVXyPn/2WGZ3GyS1/Gc1h'
        b'0Vn02h4J+SoJydzjT97sDu40ml5nRWtKMJ0kZXyIj2WRcS31ye8RVZQZDdoeQYl6bY9IW67W6XuEOijXIyjSFcu5Hp8Zs2blLMrO6xHOylk4x3SNNE38ltwYarLO5CDR'
        b'PJfsMYHjnitCXCUlkp/AWruRVoGtCdedVsyz1pvjNrD/5JilV1Yszq0tXs7wxs8ntHinGd8MMonQXbyD4fBZNmoTPke35Zq188yWSkjEN/xZxqcSPcCHucAI3GIla4Q7'
        b'rEuiiSXopci0LGV61gJcm40uxeCm2IwFaTEZsYRHboyWo5sFHPWWws3LpLPwMXyAMu+oPXcmbl5A6jmGuquYrEF4O+UAVlQAmT82PJHYarPjGNTMDKGHbkUC1LoW30kE'
        b'wE9kEseiTt6A7CS+gQ4uGArZAeAjGdSyHFfTzqNbJrPD7JVl/OPR/XwOdy4L5A3ITuEu1Dh1PpQTM6ycQa3oBD5PC+auQttw/VqGGPWOJx+Jv8riZuKaRWfxkDmKyYPF'
        b'jJvx6wGd2miG9mJQOb4L/P4JqA02XRSD9uOzGnruh44pxqiUCiXxLcxS4F2ZLDOgBHWi08LpK/Npha2+I5jp5GbdTZcY9VgzXyE+hQ6sHY+qoUIBw8Yw6OBYfJqakI9B'
        b'O9CNaHLxSjrwqSopcKpBqFFQhC9k0upqNg5gYoh/21RF4pdRC3kimo7OoGbAesehPh+GVTDoEAgzN2haGDo/FFhe8qklfCGbEcaw6C7aNoJWphk3ldnAMBFx68aWvlc2'
        b'nK8M7dXjc2gHbklMQldAnFMy6DA6OpWf9AZ0NoxYNGeBpOXbD5+I50A4b8E7aHXzB6uYFjJ3orjoLwYkMhQQxMNkAtRN6oL1jmXQEXxuEm/Id2TG3GhUH0FN46hVw05u'
        b'VEQOremMwubal/yeaN2GbNukVfvg/bgW3U5MSmborLUG+NBJW4j3ZqvI7TT1eDcsq2lalogJRNWCqdOiaXUvqycyFQwTF6d7K+lYUiFDATEB141Fd1OgMo4O8kDRHOom'
        b'uQBfM/KVZVPwWh9FAWwQahGiXdADOirrsytYAg/JYjqog3gPusi7ot30T7KVhvUD6XA/DC2wQpCCryylfbk4Nowh6C5uU8SyMWPj+UlajRu0+OKmxAQCrTCw/WVoB88S'
        b'H0WtIIHVL8ZXKLxyAK/XWNziF8A7UNTA9DehM8sTx8fBlCQQyDwxgE9q0KPO6NVTVcTwkGXEOm4gOreB3xzH8Q50Gx+pSJxASqVA/1EjS2eyHF2baYO+Xegyw0hREz40'
        b'WRCMbw+la5ALot4efGQ5lIRZmwSggffNoj2d7SdT8ZtRTgzppeiuMVjQD0DnOf4q6HX8nc1xcwtWdeqT+GHjo3noTDl0I4mhlR1KQdd5ODuNz86N9kXnAYxrcZMKoKOY'
        b'GzwdnedxS+Ozw9C5jVAMQCoV+qAF3EIGNgQ2eT3aiW+rVOT0gzOy01HTGh6qb6JOfBdfYaEU9HwyACJqtuFBMzAjh1SBgDMApTXgBpitMM53NTpLe/5pxHrmPwlUr3q8'
        b'PsIvle956szK2Wg76opLEjHsTAYdR9Uz+J6fnzUBJAuAAAHegvcAR/uABZhvMtG6Vs2ZxzSQ3bto4qg/LhjA42gdqsY3YSUvk+oAHcxiYBh7cSOPAM/jLahxqa8KcIuY'
        b'4Z5lY/FzE2hdw56JYOLIjAZGCLavXsR71OAd4/FOFcjhorlyRihkoWPX0XF+su+GTMS7cScxBiaWwPgEuk1N6NDRchC5iBfGQvwAX0kDyVqxmLeiw7VZMYCHGGZeqM/g'
        b'+eguvYMJH41BFx3+tOQQ6RKI5Qc5wLHX0ZneG7aHDuVsrsShwU1+o3ldD4j0XejM0mzcDHxpDBMjH0dVOvPRKXxf5XJgNkGOm4DgCAElnhdZ0faVFMxkgB+ha+gOOreA'
        b'uPwIGWEouwI14FY6/QXoFLoKm6ZRlYcbATrwIQZfwa3oCj3QD0YX0VZn7/CoaH4IY3JEOnQJ7+NhHF1LwgcBOo74k/ud4T+6KbJSxcUutGtNNExMFt6dpsggEmQXbgcp'
        b'Ml7IjM0TJaSg3XTkR+cNYpIIyGw6KoqJXWJDX2d88MXgCnwEmHH0EP7je/g+X227Pz7uUi1qN5FaOWbsIlEiuoKO8DDchE8V4i3FqgVAbll8kcH38Q7cTRd+BTqJtuQC'
        b'kW4ULcZnGG49OwQ1TeMRbdumFLxjhWoRPyNnGHwdIO6OlfdH9A9zcsJHW334CRmO6oX4JodP0a6PwHuWodqB+Aiwq6gb/sOKn+d9yk/gnaiZbHxlejaUTH9WrEgQMoPR'
        b'YaEedeGHPBPyHD6Cq9EWILJHBMQoHP6jC8Ao0B5cRecIcnPUgPeGKxI4qOKIsJzcuc0D7x0AsSaVH64nGwa2zE60n+Jb6PPxcGIByoNOAd4HvQ8KE6xE19dRNK9Ee+Hn'
        b'kgIR7/HhzPBi1EjbTQ5HW6L5C84A2GLT8clcat4xBN0Q4l347gzabjC6VOq/CR8RkevL4D/aim9ROM4BILu9QoXrgV9ZxazywQcpeOIbOuPkHJVCkY4uRmbANmTCpgtw'
        b'iwjV0lXS4ZPo0jPQ4hEpVHgd/gN6b+U5iWvoAtrtcL/pwmcc3q4HltFVGIbqc8bgLeaAAEBgsCnxJcDxFN50k/yYcAJvi/dNO2kMYXgn+6v9p+Fdvrgexm1kjGwIfz3B'
        b'pdxFwNKlEbf8BlWOAp/GD2k/ZYOF+EroAqoi7dSOYd+AYrI1huWbpv2xfBVf44IFqej8anTBpqZt8tOVj28Vmv8FnHB8z6QVv3nZEDYjWPzBZ8/9bHXoH8LCGmqOXflr'
        b'6tbREZz6fd9/lQSO2aoPf2Z/08f+/Rce3/OzsMyHXBAe9bch3+Z+2TB3SMy9Bx2d8iUHfFNfPH/hX4t+e7/2/oiAFt+F5brTme98FbqrI31Wa/umVR90vT5j0Ohfnhc/'
        b't3mJ79UvP7v62ffJ6kEf5X60R7X4V5flp7Ke/yTiUPbZkNdffLHrt823t03IWv12VOfEutl/klnHLZv9pxHLjiXNvjnjcHbR3r/sGZpdueuLbV9UXpunMbb9fepe0Uub'
        b'xvnMDpyZnDp5tOn2Gx+G7D21Y9IvZu+elZ0yUW46P//P1186tO1ov4k+E//6x20vzXlpzLj6kQdGLLlY+ud+jW//fPjH6l2q+EO/iTzybcGsnx9IxwdvfzfrFy371/3+'
        b'/N7v0g9dfuOPutJBEya9+fXP7+Zsf+bZlw3BC2e8axkfYvX9CpW82/n8+T1nJp/q+Trk8icDF21v/PDC76cEda0PvNMq/mfnmMOX028Yuyf/9n7Ag+fK9DP/6/jiS9ua'
        b'/nun5cHhY+Wyrm/ql23I1ZcXtYd9pZhoHmy+Paq57p+dL92v+9u/5dnpsY+GTHspuXl4xo55O/yaxnyfvul3IdP6rduvajxef/EPL9+c++3Mjw7895/mfPvZw/L2r1bt'
        b'nfDfh26FPvz4m8X/8DnwjwVfhGXf+PXnf44NudY6s2Cq9bO6Z0dn/WXSm5NaH34niAr5t/Gla/IwXqm7fwD3hGdzWIqT1UMQOkM9rwtmp+H7g6KJqp5Dh9ksdGw1b+Pa'
        b'ISsGpgkkDPFMQI/C2SwgiaZ+vKXEWdzoj+qDKqQmwF2NQZULFwT4iplwdFxghD1ZTV3lxquAbe1AN/xRR0ya3Z88BN8VAGJvm0Q1wEnx8G63sgUU/xxv+obOJlPL32Bg'
        b'Ow6h+lhq/AsMKD6mwqc48hWF9bxJdB2+6k/10bzmUIKvoVtZnCYV76BDgw18Z/FaoDA5ZHCV7IwZ83i99FXY5cejjf2dzOo4BdqCrlIFxqYp/XkfSHRhLSMkPpDAfTdR'
        b'g+HB0TpUz6mdjVHOJVNbjo3j8ClX1/l+40REKR+HT/EekhfwZXwuB1+xW4U8YThyvoi/NvAuoKT785FTNifLkap1/EWEt1FrFbFUIQcj6KyRCDrENNs2D9ETRcBedaE7'
        b'/NcOTqPTs2EWndSs+3F1r6o1iOU/K3EUGNe9Du9ImPgDdv8T9HA9bwd+cAM+4rBYgfmWoF28wUrnYk/fG/jRVrI9ArWG1/eshYdD37OZUYay/VkhG0otD4nveTD82n64'
        b'UNbth8R9JhkazI4mfupsBJQhv1JWwg1iZWwgLUNMqEneYJo/mA2HEPeFpH9VQK/6BvrjfFJgIoq7H+vsx/Glek8QrsPjPGc38N7i+HlnUB+W1S598m4EMB0eNfxXuJga'
        b'kUOhyFI1x080BSCNyZgn1RzjeDXHL4sJVxnMCplC6QFmMMNrGSlreRGfGouAu41D25hhzLDwcBo9Kx94j2aGKUKdzEBmINoTQomZIAnkNyHjj1qZBCYBHeCZ6shRREz5'
        b'W05AYWFMbGksQ48R/ZZLIPKNdVKIFKzoZ+NuB29k/8ltGSuNUy870E/FiwXx+GZkLjqSCIIJSKdMMW5A7TZJJzsJ39AmJomJnyyjRbfwDVpNygJyU2phoK+sMOY/5pv5'
        b'undvCIYJSFkSUFGoPxSSy/fii/UkUqaTVBRK724s4HN+wJEv7ASH+84v1O+PXcznrAiVQqQkOhAiKyIL+ZzfrCI8wtrSwODCzK7ERD7nMjmJjMvjILJVUspHPp5FuvRB'
        b'mL+sUH954EjGJtfgS3rNTMphLiJcuaiSBdxxr5IOL0+6ITEuDp0PAAZzNIP2gSjF+w/+RjqKmc08v0jAFBYFDA20ccJtUnSGsBGoDh0nrAR+AAw6SYlDJ6DwET9GHg4S'
        b'G/zHN/AJysYlaYAXPCJmRqxj0C34rwV5m7SswWfNuJklrPBZRsEo0Fl8nbacmk1VCOHc9MKY4cRzkWCUQrRjMm7GreQHBDe8E7isB8R84CBq4+8auogOD0ekvu7lzFBm'
        b'6Hp0iOfrLqxNRVsDnrTeRmdCaL9lz+bkKlBnKaIc9l42FF9ElyiY4QbfAdE+zDx0lzoVHRliJW4DupnB6ALDJLDMOmbdWJ69w51pgBEvcERg2UPOu/F+tJ8eLdNVeT6Y'
        b'nGVHTBJML8zUPDOQV1ErphXDzqlaRDZuVqXuoOKKyJwE22fulzfL96Zm4+nBO0srP+4+WvMPU9yHAT7T33pjhHJP9LcLR5+7unyWdsSdVzbfCqlc/yIbGXKuNoX9KLjh'
        b'd9lXgl997dv3v+yuNL1m/fkHNzIE7WM+mTR21KBfRpYlfeD769V4bVn+XP//vHjyo0Vhf7mR/ddfpw9749XW9W9vOy5/c6fx9492z/569PmHTb9ZveSd6e9cKWocueTn'
        b'MwVtpwZ9PbR1ecT3HY+Vz77+n/FXj26Y/pf/Xtw94381dyVwTR35/+UgBIgYEUXBIx5YwqGiaEVFoYIFuRQ88IRAAkTuhFREXQsIiAooWuqBIqitB8X7xGM7o9vt9ti2'
        b'2241tZe9du3armut1rb6n9/MS0ggQez2//n/jUzy3ps3M2/eHL/fzO/7+16ZmvWLy9++XFh47St5ybcJN52GvNmwPXjfF5/NG3ZdczW/uPqnis1eA/447csHf7sd+Yea'
        b'/KQffpyKhc9K57m8kb4h7Y25R2NUI1Le2JdRdWDuV7FX3Z/Svb2m4piH24PSxAO/rjteOr9PQp+QK8tDeo6MCSy5PuVsSOn3M1acPd5rW3Dr9efCP35vWMCB4w8EN8eV'
        b'Zfi2KPsVgicmfKwPeXl0Lxu9NMP2djY1JqkhczQFQh1HxyfFoMPUHCEuwBfkgpNCVC9DB+nsb1iGzlhAe4LJLHwJhI4XchiOcwcqxYfQKQ/eJpXZo0pxFZOqKtE5SuRE'
        b'ZuU6dBgUV/AUDS4AwkSolVq0UETTjqwY8LdFyjCb6MdVAkBEDQ2YThOJwq84Wolmikhrg9QWZvuPNxGl9DyUw0/EiXArqpEIiIJ3LpVdbcCNwQC68g3ITjfZzBDpayNv'
        b'G4vLXdrZpPDWELoY2jdJ7EU06VLq1gadwKVEuAGaKH/UyHwa0MUpN28RalmB9jOMwUZPEm09yDweaBsv9niSbKi40oYqk6CEqeNsyDTnhtEa753kaul1YRyqp2JFFt5J'
        b'JQ/ZEKiNKHywZyd5B7UuoFGyicpaRSSPSCKW7PcfORIWvUkx8QER3qxYykpyCB/RW1nvorWzo6FKwXzXcTR7LTsLh9I4NdEOnFg4hYwsaJcTEVjp2l4zPlKgwlUd0BR4'
        b'dxYzqrgoFlBhkwiKW80GEJ2NHxJ8WDMkAzSukYVYyq8gvKItHJXh8MFQ4L9iMhwIcBmkQXWQ4XAdqmaSbjPeNNcbbbUUvqjktXIWfS73sXn4OD4Krpfa3S6F4KMmQ4pu'
        b'7buJwcqwo8MFurEqE4iFJtcK7lT2ciefvuTTj3zg2JW6WXCnMdz4P/r5SjJA+KVkIHgSkgmJFPZIKoItWplQSuFsxa7tcg1kb2GE10WZ223yTpLgOxui1JYuduc6ZEnq'
        b'CEQW8rWRfsXR/7ptcODRAZRG7ZF1wCjHbJSp8TLYLRulJrtV0y/YvmLWnhSNBrZj1HSEGg7Q7WW6sWiUJc8MSwiLTZ49f2ZEolGk1xQaxeDvwOjCX0iMmJ1IRUb6sEwa'
        b'/e89bOj+QAJ/qDkwcpOK5L2eGHzm4Cp27eEqcZfKHU1+NSTU3kZi/bktdoNrpvPCjtdNn1vi7yS+rgLXhxKHfuF09XtSLtplacbkwMlno4bRogXBvTrteJsIb/RTOnL6'
        b'irf0pJy3PU3faqH5l6jaUT2cSMsAH+mZLlY7qqVmhl8ntTMF/ch4ht8e9NiVHgPDb096LKfHUsoA7EwZgGU8w29veuxOj50pA7AzZQCW8Qy/HvS4Hz2WbRGnc1Aqdf8G'
        b'4RYJwHqW9lB79ud2uwIAhj/2Mh17kL+9ghqB2pvHxDtSx1IulT0r5elOlCeYsveSa06Ui1dMAUPSBXKoDfWQakEl0xJklT2IjjBUPYzy9PZSD6DGyiN4nt7ouIgH9VbQ'
        b'8dkm3lhyiZH0KnyAPQU4s1S5amj62o70nlYHvrMBwc7TZJFfean6vGwg+AbgPfg3ZkSl4F9Zk1/IXHxTFH4Ht9M6cC6qdDQ68XxvwIXE/6T7zlLmchVYkdTpzxlFWbnk'
        b'XI5GrTXkkHPSfFLyZXk6ta6dKdgmRa+1Cy+TJ3Unol0589vJLmYXXk9C0puuFH9+u9skvVDZv5mk9/EcvZ34eG06IfiNHL0WL8VcDvDF3kUpyGV7ZchVqLLzM1UBtooS'
        b'rEjLJFmmUY/nXVMGd80YbIMd+Alq5LGMwaQ9MufQ4dPnKrJVqcBOT35a+ttWjuzgyZpR3NkshXXRad36jLGoChuF5wtC+sRj+IrtcRPb9lJhj6+4m9zENhNt5yv+L7iJ'
        b'Tf2eVTs7UmjV/Asb+7gXZhoseI/g/JFCp8nQ6kkNk0GKjGW0OfkrDPxrM+SCZ+7fRAHcky2svDuTri8onPNT/G8uSueYEchJpT0C4LRgJumvs+bpLQ+VydEpLU1yodSd'
        b'8+HyA4kOPnmr8zLOEAqyZVsuru+KVBivo3Q3kXgXOmuRcGO+DO9F9VE8XzGse5xJk8xMyf57al/G3juNaO+XuqIW9qOm4pAmfmUpb8Z9Bq11QU2xmG32no+EtY/7qp6K'
        b'FFnc8hWcYRyUuHoVau2Yrm4FTTnKL9HSKPx5XOuEXsDncDNNrqcHLCeF+julpGSHxLuyYoaiU842SYbXxpr1O76UL+M6czFPucDeJttHFifBuk1mkkCe4j80ajqjLVpR'
        b'hJtspesTyWswLFF39AKf5jl0yAWvXYyOaLPmjxDpN5A0Lo87FfBmWw9hmCxi1oqHS3zKnvmH6qVAF8XRjc+9Lu8zWjxS5LnbfemN6nFNhu+OB9RvmLhs/NmNfTYPfPE/'
        b'AR/H9/z7Oz+9Pt7/zOd/l07CdR9drTxb+0l4UP/qZuUnl5c9kE9uyygqv/TZW0QzXH3wTuJdtxed/zLqL1feGD913LKWu9yjV2vxaVXzibpFjxyqJqj2vaR0porWKrQP'
        b'VVtolkStxCX4OFUt8T6e2EaBa1CZ1Xq4cCozUs9DvCbdjPb0hWQC8UHLdubADcZbxfiwEjUxRXbbCBlVUS31U6KCnwMd1VvMK8pE6S9n+Hq8h/omBD7ieX2ocuSFLqEq'
        b'kxYdQTTDVqJFD0C826YGfB7vadcJ5fFCohIW4HXMPex+3Ih3UnXfUtXHLXrQ9nHtPPqw2UQp3wnaabtmOhaXUeV05FOFAZDLhfg8JsgGED3tlB4WMNBavBdWGGKoaBsg'
        b'4WLRGke08+nRv5uIbwZ5gvMJC31uNfcM5R0WSNo5iBkfMfXwaj4yEfsS8cMOIzGQd+n+CMGrECAIMASXIbjCcY8n5ZF2J5EeVs+kJGMmhSVZKHzPc9e68I/X+TmeBIjp'
        b'nGwWpexC9+aQMjFgaHteFtTEcKoLauLuY0PTTUyxFnKV3UIlmQr1YFCHElAp4bcxEzslm2Qou/kuNOc7mOX7u1Aii5OJ5GQ3zyXmPL1YnhbS1W9j4xUnEwHJbn4qc34+'
        b'7SKUqiMA97+gXTYJLXZLoDaXwBMWNCzkmt+cp1ktspdnhlWepJbN0pBFnkohw3LT1RGzgW5cmsiiKGAFD32ZWujGkYBuWIG/CyGvzDpTD8mydJnZJt6hWzbxJooqB7du'
        b'U1RpgKezuwxVNPKTEFRZElJ1ShIIqsxQa19/ha8l5pscUxg5iWRJr0OlXVYMYC3pvkZozmiiIjEvB/QKpoiDNzoeuK1KzTMU8rxPeiLB2qsb+AccKxqoErU2nTLwFPIS'
        b'uvVD8fVNvW6Sasvgfe3ZEI7hX5SZMUrVlbIXON5CxVH4mGhp7Cs7lvXKBPlOnVXhE5aq06Rl5gIjDq/5UY97Ngva3g70em1GLm0KjHemE/mZXqG1fCotUYIy7JDbmJSb'
        b'QPqSxwebdRzIKVDpD0snJipliGHmUk6zp5bRVqml9wMHF9TdhODuc3ilWz8QPLVWo//9GLh8gHGKcmUpFb6+OaB4k8dZ7uv7mzm5FD6UfyuA0Vg9SdJd8G916/4nZcNS'
        b'2GHxsseGNbJ7xbCCj3TJieVj5sQKVCoWBo6xz2llCUHhX6NBwx5Hm0sLCr0+PDw2dv58eDJbXnjhX75qeQ714avRwVTlTwnvzPqyRYHGdF2gLom6rFdPWG8ZZeopNovF'
        b'BCJLei+S/djR9pnaLAE7prUki25CzpIemavXskLlpdsmPlMvJS2D1gfcQB0Zq4rgdzc5n+BfmFUierqMpk3LLNRSYi99O+1c5z5rN80ARSCQamsMZHA1J0BasFbBVxEZ'
        b'oXJIj4uYEzBbVZiqgaVJ2zRkAQrSXJh71WxDTpYm03b9ByjGdohGc1MZ0osNhRoyc4BTa8XcPJ2eFspOGkETFWGG9ExNqgG6HrkhzFCYB/Nblp0bxk1UROWqtc9pSWPO'
        b'ziY3MHI8fYcnt3P3eFtFfvIKetpWMlqLYuU8WbEm2ErvyeolmFZke9U/puZtnpzNWjKsIXYo9xO3RMvHT9eRp/GBujWXSZVabMhQ2m9+lrcrnva23wCtIgYG24tJmlnu'
        b'qM68o+ziuI7JjLeXzPiukiGNwvx8XaQxwTKa3UcLtkrMxnPZndB4QCEZ4fhfVB4gMikZW01DuU8im2PtTtjteMWJimnAb8qOiIzjE00ONbnkjzRzBcxBE+xzcbYjHa2T'
        b'GdMhmTFdJkNBkVbkjD6UkTEc5ptxdm8zgyjZrRFz6EgNJxQ+pJPzTZy8dvvVYNABSSWZLabxv/wVFrJdxJwEhc88vDdTRzopKUuQ/aJY4DfbEzOf5gtlSkqfZdDpOxeq'
        b'K3HPnnhJRcnuS35mES3MajugezIMRZpOVMTBl2LhmNGLu3/bGHbbGHqb/bdhgrDyIiR/DOpzV+2A4lvJLfBFInaOZ38Ui9TodLmjputUBhJkjxw1XUukO/ujFo1uf6yC'
        b'dOyPT5CB/QGqq5zJqBSRSYQwMvbbH5po2YjMprZdDHuVR6RYjaYQJAv4JgLW+C7lu9S8ookK2F0m8lM6SK3kBKlz+y8VbgJ4MbtLla2Agy7vSNMWQockYZfiHkNVQ0z2'
        b'gybsD3J6wNjA8eNJS7NfJoAzkwLBV5ctMl1FnnY6GVS6ikQB0eQNwZdi4Xj7EflhzsQ/20WLNkG1JyqeIb+YJLxwzNNdxjd3bXqL9XZfl/VtAoDzd7L3Y3+wBuA3EdGe'
        b'CYsjr8f+iJiqTSMJRk0jWdvokZ0g27Cxb5Mq6xtO5OZLgeMpMb9E9+CoEQramoPPtMPrdCGclILrnkEH6U1fCB0S+nCMSWtz1lxmnovX4zNoSzQ6guoB/MdD/3agOnrL'
        b'S2EeRS2CJI5TpKwsHeTDbJXRGdyGX+HRgEsWj8QXcTWzdV2Dz2vaodXo4iLOBaDVQieaWIx85ayF3L/BN+ik+Q4JzDeoGzqHD/qR6MDBGA+mhahlRixzywT4h/UJXFEQ'
        b'3oiPOWXgbWEUZLTGNU64dUEt88OUNDzmBkepNA1oK95t6YjJ5IQJkopkexcWfpgmZHK4Gm2TKXE13qO9x21gJFt31/tW11yaIVLJL2f82PZIG7DhpGaje/1yYbRD2a+6'
        b'OmnloppQtLP85SPa0tqNkbviVkovjbonnNv2rzf1zb88t+Fwle7ZPpvH3Xz2i5sJH9fUb80Mquhz4f1lX/sfLzrjE/RwS6DrO1/+ecmP0nv9JYbXXT84+VLGglvafem7'
        b'vnbVDTjRUrD93soMlz0R+769+t5/NCfSf83SXi1eenvo3QNVBveGj/zKvvrrJ/feWnF/9Sd/01UEH4xaM+LaL/Kd8o9cvE66uekn/7Rr5/moOTL9OuXkbxp+CPibm8un'
        b'9y+H9J/wdMmdK2/dehS5zvHLwau/0c0IefNTpZRZEp5Ep6ZYOm2eiKuFAfgAvkChNUK8BpWgQ+jSGJ7ZUICO4f3B9FqCP9rkh6vio1CLmJNk48P5wqH4xQBGz1jB4W2m'
        b'TTW12NfC81NdUCF4asDNonEd95ks95hIo6zg95lwFT5QSJndLuFWfKHd/RNqFhms3D/hCrSB7vz1xmc99bgZN3aiQhShI0HodCGY908u8ouOiRJwwoRReL3AF21VdYaG'
        b'yH4np+pgFUc3uGAb12qDazUXL6VEhmKBq2A49QMFv8Hs0Jnf3BIKPCm5IXzLBcUy87aNSq2Os/Ih0r6YDTbeFjtaTk9UcKXYIpF2Z6fmJ1lqc1tr61D721pWZbaPCaE+'
        b'pcBuiasUm31KPSHtk66AJGI1ksIjdSYd9GYjqc9CB05a+GchuDaeNieXeTKYgg/J9AaACVeLObEKrcWHBaviBrcjRqY+hWtdyFEW3jKPm4f3oFIGmC3NG5pI78LnMzkB'
        b'buPwiQR0mGYUH7tScP85rYCMfisOe3kwVwJ4vRA1UWxHEOlmL3KaaEc2xB4RxFAsiAy1UjjIEdzIAMJJjpwsskFEBuSYCwNDGULjoUDOKdxfEXL5KbLx4V7M7L9tTC9O'
        b'IV8kIif9hyxNZzHLs3pw/WJawWdzTLxkEYvpHS/j+gVNdICTbxf0ZzGrp7lw7vJcR06ekt04yoXFvD4TrAdIjclT/At6O7OT5VMlnEwRLyRF8n/Nfz6bI0I13okzZ87k'
        b'cBPayQnCOVQStZRBkc/Fouqxo0eP5nBlIKmivRwuWYT3844d8DpcmTiTW40uAsjvJXJtBDrE5qnDsR4WGBJPXEJhJNuSGNi9dhSuJaniqmIeSOKO9xS7LuFWwQ6SX88h'
        b'3JAiTwqrmO3RbyxgbNagqjHcGNw8kaE32jjUCGgQMkacDeACQlELnVKX41dSzbAP9CIuAegHGTVj0HYKy00KxwcSZypEHD6JDnHoeB8JapobSydDAWpAJZawj+JCAH4E'
        b'4AsMmgGVfNTLiZOvNJBZPMVfVbCc1efoGHIyZqgETi7XTGP1OQ+fRWWkRtFpIO/GZZxqZS5Nggty53xSPnMg7Xfy9WcEDMyvdMdnE2ei3UrOwYubuMqFvIV9uIpeCg0p'
        b'1vcYO1qMX/EmNXwI4C8HUav25L8fcno/8vxvndyRsykEACDlGX93qrozuHLC8F/KG8rqSnf13b/LXRorvHXu2MZFujUf/6yIC33LaX+vvFvyWeF+8yc1nr/zyfnlW2Lq'
        b'67SquTfef+OF8//82JDufHTEhy9eGfF5rK48bvj6loI/Ha84Osv3xdQPItYu6jHufdG5Px1Nn/Paq5uXX4xIW1Wb3uvBIMXb1VmKH5uWnusXcDhz2pK3ZkcuGD6w7rv6'
        b'8Kbo1r0h7z2cahyp/Dll5rs7P5lU8W3P4W0Peu+563Go5tsb73xbs3rzoyM35wz44j3V4Avvqd45NG/zy6WBCTFFNevWPpJtLQktuzmlVFmxNSBjycfy15ZcOJjt1nBm'
        b'+1chiW8s+mfd/NsapIw7YJgbW3In5Kw4edib0cn6/5yYUfTzhaTxj7b4P42r/c/0OLvp/uceHnMLP9+wSulOTSZy8akxllOZFLd0nM34mQzVFFNTDg3aE+hHZ8cAYDOs'
        b'ysBtQrQpiUxe8IZkaCMuJeJQjACfd+PEQwRopx8qowYintGo1uymUIqPjQM3hRloO53L/QD22g5SLU1lGFVfkiw4SsDnUcU8IpxJSVPo6FxcEeHghDaiXTy3DxH/GpkZ'
        b'ymgXgHMI0O7QRcx+pSYJVTMoBwA5RPh5wHIoUSud9nElrojjDW7yUStvc0PtbSJCadpo54ynebQJhZpMzfyDcOjiIGrCkkI62WFUig50MqIBA5pn0TZaO6NQ0xQGesVH'
        b'XJlE4o3rGbCiCu1FJdFWmFVXdGgsKhM9g7fjMgpQkJKeusuKWnMkPg8gjwmxjALoCHp+UrQloNWVDP+lq0ThGatoBAfZYNQ2ydqIhlrQuOAKBtptXoyaTHY6uAyd4cRg'
        b'qYP3j2B2PKejp1kAN3qjVwC7McjkKf559EIcXhfVyZIHzHi4cGbrcwZtHgbVLJhgyx5p1VQ7BiyPcVBIiWeokFLcWUjJF/Ncy0IimsiFUmocL+fRrYCvkFOEhZB8O1uQ'
        b'Vsr5P/r5WuIl/Eo6wJmICGIeeyHnjeyF9yVOwntC8id15knXqLDQmdfN9kN0YHgD+cS3o3zyPLerK5+HHTPV6UGO+N+leUsnj2PoKK7Y5jhzjKMuV7xwG6oyk5wpZ8SS'
        b'7tJig+UMNWfTKVWT19/EWYaaUSUnAtKyZVI6FTr1xU1+jmQq9AWEYTGZIODsYlyW71eUZeIsy5qvDbt9VqwHSEfUxe+sKMt69x42rPd1QYFgo9wte9bmW46S4ZmvqZvW'
        b'Xym97FTnUjCiYeiQUY23Hg35ujQytfcHLq+/ue376MB3f9l/FOjL3I9GSuVeK5yOfp90qXr/h/3DsoTLL4chyTfXqkSOXyjrd12Iijlzy+A1Qt4658OxNyc2Gse+HX6/'
        b'7fTU0/kv71h7t+HqtfrkOykXqhNjZ/8qAMKy7Q+X7HnYEhTy114/3Tgybf4qQSmeMP1WoLInA4etGYb3MMaypXg9JwbCMjLgHKJd1nfcWEvGMnw8HwjL8FbUyMBYm1Ab'
        b'GS0oKRllJMMVfYUDkkZTxBcRzbbDOG9JSQZU90IiAqJyBkffjdbMIucsCc9ypwjRnjC0k0Gw6nFpbLQladlodAB4yzY60gKo8UE1Yy2jjGVECBL6EuHiBE09AR0MoAPK'
        b'BnzWxFtGHfFGo3qe8BG1gCsoRhXJSZasxM3CYXjrHKYCXsI1w4EjbNgMRlzGk5YZXGjWMnwBHWesZZSxLJWMVh74dF96bzEu1VlwlgnxRiAtI3raRTraK8Bikecto6xl'
        b'cSuE/fowljgVkUn2ts9WdTLeo8JFvIfmm/MHXOLH49EkaD85v0noH4xO/C7UZZReiw51vp2HutVcwNCu2ctglGhnL9Mt47oGgRVZZTuYnNP7dx6cnue+eCxfmSljMmxY'
        b'w0EYMExIv+KUbh3BYMs5zhIR1g07xrMc9TZeqMnRM0hXB1ayXv+VYtyNN3SBBENgHJ/LURoyiVwgo6RhfZW/lYRMBhPOIzFJRbHMbZJUwNyunR+g1EehE6jJJL85cD08'
        b'hUToPztQKYjTll4PEui9iGD8gevmiJpLCWWh8j/dc41UDBe7KeRurw+7L31uyvPlxn33K0aMVW75S2D1a2+Wxt8aNGbih9cf/vjz8U/X1+ob75bMmunxza9XHjZF113r'
        b'/82DZRVZ85Px2D2t+6Z+7O/95jLxo1fHvLu44bT+kGJb8s1treVDf36QeOjo6L+8N+/cyO9eXjPks/6VA25vT/vk3/WJb//0Z0PvoZeP3XH8fpO6UfrXq1mTW+SGKUP3'
        b'5A3f0TZdVZ0U+UvUn/q/f9kte03O9OmrvLfsffZ2w6qohdU5r7//YsGr3t//9MdBg3e4L9x7I7Z6/M2XNt59o0FSLaqs25H2oUOZ3/IFuod5bxe91npmmrvPlcWeIRPS'
        b'DucUvvT2NV/1e183n9p547PEzSm1MyZ/cHV/WLx70NT+C9MdN+iVIiqaoZfz0Q6AhW4FZ4cTiLCIT6EDtLd79xrhEk1GTSu3I7AetGAltbEeWIxLLPx6t6/qoMMiWNgp'
        b'xbs6L854/e+0wScOyLgjMvVBmwEFrUqTk7PzVOrkZDruwNIn5ykUCgVBgkGPhGSEkQjchFJPhbunr/tU96eEgokwEk2WilxdRqzmnhMKdB+aO5/IKExOtljd8fx/UAcC'
        b'3VVz34WSwuCjhw7G/SPUPlka9eey2TMVrSeqSy2uio8hQnytI+fan0yia0QD06K1S4d4CPS1JN5UyYWBVcFE+nB3eHRvQ9p38tDI7HWhqcFu844kXBuoeS+i+JeFa3a4'
        b'LXprw4iC5phhPYLuLFy1/MuSjJ3v31in/PVwr2Stt//71/qMmt34elP4Ue+1h3L0iXObZ/gt+ugrw7W1KmFJ0+5eqnd2l5fjvpP+VfDHXk81vPvqF6V+wtwzX5RkfOrd'
        b'iNzDV/+w/sYPImm+z49jQ4hcAaWfspJMYmRqjo/HtaT1n6VcyS7omBDvH4LLmcOaPfgiagGXWUchHszhvfD59BkAPF8XzBZMdyzH61glgCgP+iOpBLf4CNGgZAN16IOr'
        b'suZER8X6xjpyErEQHZgllRF9jV7ZgssT8PpRi1USTpAIHkJL0SV6BXDZM/xm4IoiB04QzRF5YjM6zYSWEwvwGkq3hzcQpel0LAC1XZRkAsd78RkqVgS448N6FgPXFtAI'
        b'zlFCdARXoot08vdfsSSaKr1Mj3IlU3ldqCgOt6RQn0YTXXtH8zsKuGGwADX2GkTT1eHqRVQgjcTrndBRKnHJegvxCR1qoXURhk8PJurPOn8ihI2Oo9ed0XEheDwjz0U9'
        b'FG3AF2aRKMdkaG0SrltWYMDHC2QFBgHngWtFaIOLjBYwZFjvaOpbISpvYSz4InRB24W4ORs3MMfuNTnA54VqR0WT8YY+JlqfkAQ17zVcjMpQWZCV4+WB//e9rGOnc3rM'
        b'wGNjHGrHWlAgeg8p8zZEyQdAn5OJpnQUh4Yz0YEOPYONomxNrlEM5rxGh0JDfrbGKM7W6guNYlCajOK8fHJZpC/UGR0oYb1RnJqXl20UaXMLjQ7pZAQkXzrY/Qcuk3xD'
        b'oVGUlqkzivJ0aqMkXZtdqCEHOap8o6hYm290UOnTtFqjKFNTRKKQ5J21ehO81CjJN6Rma9OMjgyBqze66DO16YXJGp0uT2fska/S6TXJWn0eGCgaexhy0zJV2lyNOllT'
        b'lGZ0Sk7Wa0jpk5ONEmbQZ+FQX8je9g/w+98QfAvB5xB8BsHXEHwMwT8gALJU3b8g+AqCGxB8B8E1CK5D8E8IbkHwCQSwz6T7DwTfQ/AlBLch+BSCjyAwQnAHgrsQ3LR6'
        b'fc7msfV+uN2xlcZ8IE0HG960zJFGeXIy/5ufhx548seKfFValipDw6OaVWqNOk4ppUIjcNuqsrN5blsqVhqdSf3rCvXAE26UZOelqbL1RlkCmBPmaCKg7nX3TLXYwTDf'
        b'KJ2ck6c2ZGsA+c6eQOwoFko7Nrin3SkK/38AjiPw8A=='
    ))))
