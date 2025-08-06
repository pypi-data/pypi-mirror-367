
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
SWIFT module of the Python Fintech package.

This module defines functions to parse SWIFT messages.
"""

__all__ = ['parse_mt940', 'SWIFTParserError']

def parse_mt940(data):
    """
    Parses a SWIFT message of type MT940 or MT942.

    It returns a list of bank account statements which are represented
    as usual dictionaries. Also all SEPA fields are extracted. All
    values are converted to unicode strings.

    A dictionary has the following structure:

    - order_reference: string (Auftragssreferenz)
    - reference: string or ``None`` (Bezugsreferenz)
    - bankcode: string (Bankleitzahl)
    - account: string (Kontonummer)
    - number: string (Auszugsnummer)
    - balance_open: dict (Anfangssaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_close: dict (Endsaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_booked: dict or ``None`` (Valutensaldo gebucht)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_noted: dict or ``None`` (Valutensaldo vorgemerkt)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - sum_credits: dict or ``None`` (Summe Gutschriften / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - sum_debits: dict or ``None`` (Summe Belastungen / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - transactions: list of dictionaries (Auszugsposten)
        - description: string or ``None`` (Beschreibung)
        - valuta: date (Wertstellungsdatum)
        - date: date or ``None`` (Buchungsdatum)
        - amount: Decimal (Betrag)
        - reversal: bool (Rückbuchung)
        - booking_key: string (Buchungsschlüssel)
        - booking_text: string or ``None`` (Buchungstext)
        - reference: string (Kundenreferenz)
        - bank_reference: string or ``None`` (Bankreferenz)
        - gvcode: string (Geschäftsvorfallcode)
        - primanota: string or ``None`` (Primanoten-Nr.)
        - bankcode: string or ``None`` (Bankleitzahl)
        - account: string or ``None`` (Kontonummer)
        - iban: string or ``None`` (IBAN)
        - amount_original: dict or ``None`` (Originalbetrag in Fremdwährung)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - charges: dict or ``None`` (Gebühren)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - textkey: int or ``None`` (Textschlüssel)
        - name: list of strings (Name)
        - purpose: list of strings (Verwendungszweck)
        - sepa: dictionary of SEPA fields
        - [nn]: Unknown structured fields are added with their numeric ids.

    :param data: The SWIFT message.
    :returns: A list of dictionaries.
    """
    ...


class SWIFTParserError(Exception):
    """SWIFT parser returned an error."""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzFfAdYVMfa8DlbaEvvnaWzLLt0BKSIFOlFip0iLCXiglvsRuwgoCCWRQRXRV3EsooFjQVnchPT2awJC2mk596bey8ab0w1/8w5oJD4ff+9/3P/79vEYXbmnZl33j5n'
        b'3rOfE9M+zMm/361FxQEin5AQgYSEzCcdCQljKXO+IfGHTz4jnKRrfpMtZRzUylzK9iDCJ1tmo38VaGwiY6meB5HPmhohIpfqexBLn87AJarYhtt5ej+JjPIXpKUUcFfW'
        b'VchrRdy6Sq6sWsTNXSerrhNzU2rEMlF5Nbe+rHxFWZVIaGRUUF0jnYKtEFXWiEVSbqVcXC6rqRNLubI6BCqRiriTc4qkUjRMKjQqd5m2D1f0j4O3/i4qiolisphRzCxm'
        b'FbOL9Yr1iw2KDYuNijnFxsUmxabFZsXmxRbFlsVWxdbFNsW2xXbF9sUOxY7FTsXOxS4HiELnQrtCy0KDQv1C+0KTQlahWaFRoVWhcaFhoU0hUcgsNC+0LmQXmhY6FNoW'
        b'cgodC/UKGYVkoVOhS6FFmCsm9gsGYtcC52cEFLu5EoWuz74Xuj2rc4kE1wQ3L8L9Oa2VRCzTjagkDat4jOzy6WyzQP+s8HZZFKerCJ5+dq0BqkeuZ9peZuJaqfEbVvGE'
        b'3BNV59bBG7AZNuVIEzPzYCNszeHB1rTCXIEe4ZvMgnfgtvU8Uo5JCFrAcXBYmpYF98AWuA9czYItJGGUxgDq5WCgnJyGguUUCltREWdRjNBAtCEQvdiIIvqIfoaIbhxE'
        b'NxNEKzNENQtEVaswy0kKkQXTREzMQBQip1GIMYMWZAKDotAfWp9SqPr/TqFMmkJ/dtcnjAnCPKjoQcySwmCCakxfxiAwYFDKbxv96mPoxm/CDAlz1BYU0e7fxbKkG7+t'
        b'ZBPoLzcoomT5a9mpRB9Ra4SaV4U6sB5ZEnMmpJlBDxlXg1dV2ZC1WN/Ejp3kWZdKM2JOaciHkhPrtATVbM95aDZeJHRj5I6TT+wDNnoSY4RcgDnQBG75IWY1B+b5+cHd'
        b'gamCJXK4G/QV+KVnwb0BwjRBehZJiM0MYxnw6gyGsKZ2XIEZwqQYgplBhDGfkpz5HyT5H4RS/w8k59Ak37zKtPoMGYlIWRqwY44nvdE1oCcU7bOFn4EkrSkzLzUtIK1Q'
        b'CLYRIRn5NmB/AWgGaA62PjwKu03k1mgEbIPnrUPBNTQ96AspIlblgmtyvGCmX1AouIybu5PBEWKFEdhBDQCHBAGhIbhyEF5+kSiHCnCR7lDCm/AA7GAThJAAjWuEsDmM'
        b'wnQDx0j4KzaF5qW1+vJsmuUVmyxLlUQq1qmYfcwVRM3qv5EM6WZMkYenB8p7XjcHqpfNQe3r9wi9uy1FXxobN200NtbkWijt8w0GhE5MZmaWf7mBNGigkMPcJjihV5Dl'
        b'YcXcxkgM4sz1YnuAw6+aG4WV2Pnte8P5TduX32wgG04FswYGGqq/L00Jesv+zbtAabamUCg1sLrEL7SP1BI7U99ytmD3H+UxHjkhLPw2h3IQEXlZ8rCFAn8kMwzCBuxi'
        b'GcCGMqq/DhzMQJTeDffCFibBikIqvoUEF2EnOMVjjTH8eBITBPWskGL+cRsaGsZsYyoldetFYm4lbbSF0jU1lbK4MSPKIpdUlMlEEjMEzMCj6lHxQwPxIIkkzK3awpvX'
        b'K/KaN39oyx12jx4s1LjP1domDpsn6mydFBXttSO2fKVsxDZUJWucp7N2UojacxqTddZ2h1LbUxUi5VxlnqJGZaNapbZQOaoLB4MH89SLh13maK0TGpNHrbhKG62V77Cx'
        b'73dY7iRY8Hh6Y+zVZbVy0Zh+SYlELi4pGeOUlJTXisrE8nrU8rst6mFucvEmJaa40WyqwPZSGoaKHxuIx4kkSVp9amrXvKKBM8Fgk9ajHMvmqE9ZZtuzdAZmowZWPzxg'
        b'E2zzqW8/SbG4dOh5Eic4QmY543nKWYmVk4E9FKWe5DT1ZMywiEzXGcpXyJyhiIwEJqWef2j9r9XzKQpP1VMvW46tuG95DOxggIvImAgIAdg+qVWwVwoPwg6TIhRWBBKB'
        b'4DrcKsdW1QQccIUddZso5RGC7RU1q39D+oCjBPeOTlofrF++10BuddjWmdnJ/XbpKfMUE9Xarn4Pfu6eqO1pdh5vK1n364zeuwCGOknCsECv/ceTPPKRI150x/pYqNjA'
        b'TxfAxrTMbDbBARcZsDsa7OMxf89DHO5MMXCMQ4tkZW1dmUxiNyWTAbRMThSQhI3joaz2LKWnUqq15jcmf2xmrbNHctfJaWOPWjkqwjviho3dJebP5EmCNzvGrhAtr5FJ'
        b'MJ0kVs+RIUqIaBmymyr4UzL0E5KhfCRDjv+uDO3X8yJ6OYFMyv64GliSYQzCbzwi090spTiAMmE8cCJSKosIYhGM5b7wHAFPsVdQ0L4O1mQkg7AfjwgoGuNuXyy3QY3O'
        b'8GgIhiYJhsge3iZgH+gJosDzA+3IGAYROR7xpvNlY9/N1OS58Bg8juGZBKNqmYCA/UnuFLRJmQM5B1F2PK7Fc0vlGRe5PebZ1nBwRCqbhXERI6uylYBn4C3YSY3I8XIi'
        b'kxgEdzzuW8+EFT3eclvUGAgG3PEABsGog1vs0fzwONxFwa8kXMhUBmE+HhdgORAeu5yCB9us5kvh5XCMP9gWHknAAbAnk4I3N3AjMxlE0Hhc7XzuouVucgfUWAQugD3U'
        b'ADYasB0oowh4GcVAO6ghZ9a5k7kMwgChtJobF+ZJbTl62WaphFqgDl7dQMCzG2EzBd2x0pMswNSPO8vPNHs1kUJonjwWDsiD8Y7BAXjICCEEm9gU/PpV3uRCTP+4b10W'
        b'z/mmWo4lApw1saUGoB2DgwtWIXTAbniJGmDl7EsuxRyI+zZin10vi97xDqgEHVJpKF5iMzOXgOfhZQ8Kfp+MR5ZiHkQF+H672FxKwacWgavUAohj4HDqegIOwqYiCj6l'
        b'1p+sYBBzxqPOViyrOhRDz38oREjB6yP4rnA2Aa/DU94UvCIhgKzGHIs665eZkJNJb6ARdsHDcEBqbIS2AK+UwT4yLH0lNSCuQkjWMojS8Shjsdmm+FRKKEA7ctynORJK'
        b'QsEpcN2LgNdA10JqhMWmYLIeMznq2/Rutm4xtUQC6t/LgRfD8QgUE/SvI5lgVwhNI6MQUsYgcsej3qxcxY/xpfYAD6834hiFYJ7Bg57wNmkIFLCDkvciuIXPgVcpBsEd'
        b'hmtIEuzIoHqAUr9MCgfWmOJtHPNAnpBfxKe3eAncSpMamkA1nvCOfSwZAVRwB913wsOMs0oOryK7Ai9CNVCS3vHwFDWjGA5uknIkMjxKAW57kq7u8CJNg9414IZUBq9x'
        b'cF9rHGgg+eA0mhIPg5cDwXmpqQmiJ5NtCQ6TsUCdT+1rHbiBCG1qYkoSTMNI2EHOAWdg3+SWDcBZ1LUK72sQ7C8nhfDYakqAo+bmckzqQQuLYHrCQ0vIOXBbDT3mODjC'
        b'wLKNdKG+Fpwg4Ll6eJaWggtwMAzpeZgewaiMB/3ILqSBy5QKIa3ZBtuxAGIV2gYOg5MEvOQKr8spM30LHIK3pIgUA2aYkOdhB7xDhvmC2xS54CVPJLzw6mTvGUkKGQq2'
        b'BfHMKGZuzA0n12KVjQqQ21QtK6AaP182i9zIIOqREHHb633KqMbWtVFkA9bUqIBFvKwYE6pxS3A0uZ1BpI5HZc592frrNVTjkuBYshFraVTmsmRJjTXVOCiNI1sYRPV4'
        b'VO3moYLeVVTjTUYC2Yb1M+rb1RfWfGZINe5fO5fczyAWIshN7/NS6IVcuUmkAitmVIDpL7WBRlTjdtd55BEGsRZBFozEldOrR5mnkkqskuEtzmRsGD08JTuLVGE9Cv9W'
        b'+lsMYUo1vjcvhzyLdSXcOD9ceno51TjskkuqsTqEB0R62SylCUIY5pOXsciHn106lJdUTjFMBk9BhZRjhEXDGHTBW+ScYtBDy9OZoDqOxNQEiZMFskktZCw8x6MG8Y0T'
        b'kHm6tgY5TCTXoBdcJvmbX6C5fAV5gmNIH5CxxDK6H6ocSI9EeIjHopCon/8KeYSJdjs70wdYSsOpxoNB90glcr7js4zNbmZX8WgGFL9B9jKRlZn1Zsq4k6SS9kVz3yRV'
        b'TESCWS1rH1UU+s04rxhOxSM4cIwznDxA4hPLs8MjEWb49Oyi9x88u1T+PjgyJ34fHMVny90wWffaxYPmHHQe3gub0sA5eCdLCJtQiG1byvJ1sKW2eTsWhdXWu3A4kJkV'
        b'KqVPDV96odOjOYOFQoTaJzx3gtabPuRZ92YEZsA9OWnoIAm3o/+2MNY5BVPd4Cw8Bw+AAXAJlZfxkYZchBrjwH5arfYw8vkba/1QkN8YiGIj4yqmGdy+horWLJC2tYAB'
        b'Fj4mbYomom3gZQlGg8Il2o5FGKRaIidQarzTrHryzGuDDsKZfvoEtzRgX6GQoE9Gu+1fDA3ClX2JUEWUgS1wu9wbr90BBhHm1CliL346kAH2BqbFwS3gnB9JcGVs0zrQ'
        b'T8WHmTagLxRHP2C/tTOxPC1U7o6/nISNC/noRAtbspBxbw5MYyHhO0ZY8ZgI79PIF1G7WLpw8sA2C3YR5UANb9NW+5r18lBwCR/xjlqA/UQtuAH20VFqS51vaCgG6YGD'
        b'xUQVuL2ACmrjQH92aCgK0cAxeNaJeGFtIa0ljVFQGRqB4RXwMDhLVLjBS3InaoMp4HpGOsZtIdyRTTPItJ4ZuSmU2hZ3w5rQCIxAZ7gtIQL9+jRDG1zByQwHeDITjQiE'
        b'rXyS4CxG9lCWymPQh9ZtcKtxaAQyDsiEtsQQlfXIbVCIn1yVHBqBEexyh31EFQrgKCYLQDcD7AQNsBmd6bLYBMuVBMcZttSYikhWaATSIXAE9sJrRHUCcndYjbPBeWc+'
        b'UJQh+fSDTdngHIswjmWaGc2lUdg3jx0KrlLOzxAxtRb2ZdDipoCnctYiP92cmY6PhkzkQ0EXsuw35bl43BEkg8ekmWlpWfip0dOTup+Q558l5AkYRuCkCJyCp0Cvnx/o'
        b's+XDE/AWD+yHvXxrsN/WBvbagdMMJFLW5kAJBq1qf/jtt9+EPCT2C3dhUaz9tLyWoPZlDzvEdh78bEEqi2DNIcEZfYJnTbnQFHAY+a8z8JDURCLH9quH9IS94Bzt2S7l'
        b'FsOtiFQDpnTnVZKXbEJ7tibYoe8QDgcmh90m+cFIxiib1wLOIAO5E/kvNIyyeqQbkoXbkwM3mubB3dJVciMcbL5EcsFWcIp259uMwKlQqEaObQ28zMZBCum+GDZQ42zg'
        b'fm9ONQos4GUTPOdFMgTss6bRvAK2gPOR8RxTDtiLzPNicokZ6KWYnQyugP4q2CWVGa3BcdIt0hkeA100267F5kSDXbgLr7WF5FpWU3hwPFFw17EGDsgk8DKO926TTvAa'
        b'PEoJuFMIUEgTZsFLMj2CBD3IfoFWkuqZj6TqvCXYwjEwMSII5iwy1Rd00gH8YCU8BE8hNyBfZYyRP0z6whOAnhD0wa3wTg7o4ZgaI5PNnE2mWddRPVVgNxceXoqcvARF'
        b'U0xTcpY7fIlC3Xv9PNCxAHXAS9gfeZAJ5q70SntRyLEd7gYHpKuopcBV0hUeNaCkINcXHTr8pEY0x/aRXEYG1V4VHAB2wa0cqoNpSQblmNMEagZtYCfsQDoE+0MCiAAB'
        b'PEDL9Tl0CjkAms2MVq0mCRY8T0aiyKwV9LCo+QSrZcVg27PtvAiPU/Mt3hzPWjRdlsCJORQDDUELPA0vCqahFgC7qS5BjANQgD3T5Qwc8aYJ1w56UjfDs9OkrGo+j0XJ'
        b'IDoeXQH7o1GINZ2J4EouHW1eATtspbA7ZToXL6bSZqrJxAA0w2vIYcuRcQA3SNjgjqz0SWSn8d4rqpBGNK+BV41BE1Im2Ii0CcVynZVJPGZ2Ni2P58GFqrW108QRXoH9'
        b'9Mr9MaApH1yYJnTgKthKm84rYFdhPOybJqsRXJ4pPWVfDNwei3lkCC8hJkWT80BPLK01p8CVQNAL+6WThD1IovgYYUtp29lwcMUpebpyd8IT9HLtQnjJCbRyDCi2G5FC'
        b'PrxFDzoXnz8HtsEBY3rUedIXXJg8pty2LwW30WFyQG4swX0nUd/tdbTsHUFu6yXYhDGBV6lw/SjpVb6Qdq07YU8FvLMW6TbHEAf5l8gI2LOUZtYWFO72ILE9w5EgSl1h'
        b'UXwWRtZTeMaQsBV77WdqBffaUz2+ObAb7qvmwCuGq/QIpi8ZBa+volbLqkFyewgqqS4UyvmR0cjAqml6HYI9yfHguhS01tPnjfMkT4qicmrrZ5yroQKFgPBqvRkK2mET'
        b'6WO/hHqeCreDJi6SjA6wdzU8PQvuRwK/G5yLQPqLTqgoPj+4gCQ8i1k24CIyn9hFrk1B8V6HPpp1CyuICHIFh+RZFAI+Jgj8EDwEGlfPnGY/am1DK1xCf/cDNbiG2toQ'
        b'3C5DdOI/BFWgv/oFZPCvA6WHqyHohM12NAHPWyAaHqTQfkbdg/AGzbOBtQvQ4fLmDOLGmSH/SWmRwgcc5GROIyK4toQaFwBOoDPy1eRpREQRxWH5XNS3uTQmwYsDWzOQ'
        b'Q0zNElIOjA9bs9IF82FjTr6fMCsdOT3YmsYrSkWxyHyohpelCwipDQF2ZpvHgcEyyiK4VMHbKBrbBXbOz2UQpBWxKaSKIh0KP/ZI85FTdwQHPAlP2OBAsSduHRywcJ6h'
        b'0yRspAOFfcERv9PbW7ABbMnfTHHdDwXzN2Abezpj0emzA1EBU1C0AdzJEKK4ry0nHe/qPIswK2LWMtzkzpT2gWZwBHvnVjoEMYAKJ3CZAQ68uIBa3MALtGQYwga4JzUg'
        b'PUegR3AykLLBXZNP+gry8sDV1dP0s8CTsjULwJU1/PSsDAFeM5tdFEBYgh4mUCeAyzXfO8czpdnoFFAvvttauKhOO8f84yvd8Lr2ctqS9CXvdnjOW/Lu1g0xDdxP725f'
        b'f8mP4Z7X52x270yB+xNGPOHl9SIx9zPfiZfdPuucVfnqx61a+4KMq2uqvu7aULn323dqg5aULetfUPVm1VYyJ2jpquuXOsdL78Xaly5+eH9sqPuXjDOvjr6sNfyt69Pf'
        b'wpq/2T7XNKNt/2/Cf9x5b/6baby2v0ysivIVRVx6hVWp+fvWNz1TNzSl1Wzl13xjp98RE8Z6PD/45s7P2EteaDdoMfvHlxblRveNHXoXD74+fJ0XcC868XJQ09XL7r4r'
        b'V32dt4/9o8GtOY/kx+26j5IuI96v3vX7snqZz0+Mc6e9fu1N12TPP/Kt/Yos0d9CpPrb+5Nk2R1vH0o62jTcn7R53qOxOO36ysCTX3t++lWqa4oot2/e23mvx6T9lr50'
        b'gcdiu8YnWe8G5keR6bkfDd7JfaflUHfS3cKy8DZpxSf1VxJs3wis9G3pORgdvtsvwNVxV0HevdaeI11fF+T9/egb82698ZFl+aKlV7wr0z4rG80hvutIT9nxT9cTAl77'
        b'w4fBrkvz3/243PfIR4ldJitXZr2gnX0/bOOcH1+fn3To3vdKX0H8n5cbJM9f07Olx7ndlyyZv6HL8bvv00rvvHkkxmV/WmLeeWvB3RSJUpj369Wvjno8abXYtaDlgeTL'
        b'5fOO2npFFEGj5PYrgy8ueLAMrnH5pNW2LlgXc/CTv75690eTXxzrO24bSfsXDcW8nLM9KPR1nwsxr534iybH7IVi71dO7Exd08KJK9N7aefPLjldHlk2ip0H605s70wz'
        b'hIFG/6hK2nnqzQG10d9/XtTe2Oz5vfVPp1Zdvxu2uiT7nWs3723720aw8RfuxxH//OTg2eODNbuKvnLX3lNeS18e9LntqtuH1amjZ//06VBRo/Kdn/bmfmBb0/9kQVfs'
        b'+XOfzPnwak9C5c2r9kt/LImWBWTufqs65MtuM5XIof98QZXa8yyzuLTe6fBFm+OrXn5vNE31Kz/u43XvfB2W8jU5+4l7peW52J8Fu8tdFjXKvD7afNz83Ka8XrEQnD98'
        b'4QZ/deLt0j1iq5GeLzyuZ2+X5ry45KHpUe+Pi3Wf2n7o3hdWWAG3zt6UeyDYSFyw6buPVjo2yrcueU/et+/7tI60/afDNpmC7+y2PDr/5Xl2/6w3X/zVTr3nzQrPdJ7J'
        b'I3ytbQ5OB6Hwpts5IBtF3HBvADpWgH7kClB03Uxd6vDjwXm+MC3An5cItwgRBGxCcTSXVSwRUQ/SGbC3BuzAp5lnFz8kuOgPjz2iguDz3nAnX4i8ThOaWw/sYcArGwTg'
        b'mMcje8q0boXqjAC/VKT3yJqA/iLYx1gXFfiI8kG7QFt4RlqWf5Y+ocdivAD6DED3hkdc3LUFtNnxUwP80azI0bbAvUzYD9sJq9lM2IVM3iMqbDsA98HtGSs9cgTIB68m'
        b'EwxAGz3xtlJLvpAHdwcQCKOzDObKULjbhka3Cx14WmFzVkAa3IN6w5ALiTcNBzcpaoF+fJuVkcDG94kZafiUguhVwUBeRbniEWUh29FB9Szff2rDhrPRueI0AxxdBG9Q'
        b'5FwBuuMykO1EPkKQHpDGnjOfsISDTLirIofn8LuLh//ZQor3z/3dp2HqQ19+WNKXHzJJmVhaRudNSHA+B3UHMs6i7kAeJTEIB+82ls7OSZGpseOhmrW9wnnY2kfn7q0s'
        b'O2anslAFK53bWG0L200xUGr7iyN2Ao2dYMQuUGMXOO7t35aksG/P1vn4Kxw6cnQ2Dgq/9uIRG6HGRqiSjtiEamxCx109lMGdVcoy5XLFCgRu0T5vEnxCj3B2PTqrc5Yy'
        b'rCu2LUnn6KpY1enblqhzcjsa3RmtLO+KVwWrQoadhG1JH7p7K9g6rrdyuXKV0pCuohmpqhNXmdQVqwuNVLpqnYN0Lh7Kiq5luqBwpZPWWaBz9VTKulaq2YPWAyY6L56q'
        b'4ESWWjQoG1ipc+YqHTpzRpxDNM4h6vD3naOmhgaGKR21zgFTX4WhSoeuHPytVusSgofZdmaOOAdqnAPV7PedIybhPhUGq737X1AkTUHjsfwgpW1XJvp2dFnnsqMlnSXj'
        b'/oFKm66MCVPCxfNoZmfmBEH6J5C6xNQHTNI/jXxEkC7p5LiX77EMtbfGa5YiWefmqUw7ulnH9VIuOmamZmi5oWq5hhvzHjd0nG4b4UZouBFq+Qg39kEaSXj4TGSSBNcD'
        b'sa2o3XiCwXa0bNObMCY8fdvMqD0fyUHE9gu4YNpnqpZq/WZrrL3bkpXsj+0ce+Qqm343tGFFUaexslBjz9f5Bx42+8TBT+Gms3emWku09uGD1hr72Pfswx+YEC4BaCtI'
        b'agzb44d9orVW0eMBc4ash2ruumkC8hC7bdszlXbvWvOwbPDaS4b94rQ2cYjDSr3OmBEnvsaJr0oZcQrVOIXqApOHKu5F3a3TBBYpWNRaRRr7gAkDwtVDkaJzcX9aeCpS'
        b'f1eMOceOYdbT3coCRfbTP1PDHriYUYTgEk4uR307fZVeynXHArWOISOOkRrHSK1jdJu+zsrmUGR75LCzUK0/YhV53ypS5+qunNe5sm2eznUeKlzcji7uXKzS17pEtaV8'
        b'yA/uNFOwlWU6L//T6cfSVXK1TF2p9YpVGI768VVp/aYKE52TnypY6xSgc/NS6XVtHvcTXOD0cdSJgy73LDRR6Vq/DCVb5ydQlaskKiN14WDIxUUj4cma8OSh8nvB2vAs'
        b'jV/WMbbO3Uflc8LtOYOpvmH/aK17NO417jNW5w8K7rlrojO0fpnH2E+HaP0ilexRNw9leNd61TKtW/SYT8QHyen3Et9JfS11uHDx2zkTTDJyGfkdQfoWk0go3YvJ8Wly'
        b'8AU/TL3ofX58Z4Yi4RM3X8VaXVTsYOV15yGRJirzXp4mKkfJUhYdM1YtRKKo8+SrVms9w3Whswb1LsYM6WlC5ymTVLYnMnXeArXde96RurDIQduLmUN2mrC04dB0uhNJ'
        b'U8AcEomTs7sypSt+PCBY7a5OUKWP+ocjjU0YnKuu0frPecBmBrpiJTuSg0XDU1nZU0Ip+31nwaNkkggIeTiPiczatHtb4zHjGXbwOTe3/4rVNSamEgSmGVrKqFJFIoaJ'
        b'IibTBBgk6fhP4v/hnrdTj0f0ccKYPPoRjQNowg4sIA2d3IlIdPoGXZyaGQ/NMW7Uc2qc4hdnMvnQHGdcEX/MuQozefrwnPWffXguT0NnXaNc7HWk3LKZqXlUvt+6ehE3'
        b'qyAqLIhbJ6EqIUIjozQZVyKSySViPKa2RirDoMvLxCu4ZeXldXKxjCuVlclEK0VimZS7prqmvJpbJhGhMfUSkRQ1iiqMyqRcuVReVsutqKH4WyapEUmF3IRaaR23rLaW'
        b'm5+cm8CtrBHVVkipsaK1SBjK0UgMU2tEZYjQPeV14tUiCerBGYZycU15XYUIrS+pEVdJEa4Jz1ZYx61Gy+IUxsq62tq6NQgCA8rL0VZE0UZGArTHCpGkRCKqFElE4nJR'
        b'9OQ8XL8EeSVav0oqnexbz0PQf4RDNCotza4Ti0pLuX5zRevlVTMGYBJh9J7NOxe11IpqZOvLqmsxxCT9ngFk1IlldWL5ypUiCe5HteUiyXS8pHiRZwDLy2rLEEYldfUi'
        b'cTS1dQQkrixDxJCW1VbU8Yxw2IEWWkmvkyQqr1mJ2ICwxRuc6i6XS/DO1j1baQHsrZbIxU8hcM5QNFWisfLyatQlRd/kK6djUV5bJxVNoZEsrvhfQGF5Xd0KUcUkDjP4'
        b'U4RkSCYSUzhxq0TL0Qyy/1ncxHWyfwG11XWSKqRLkhX/Q9hJ5StLyiWiihqZ9Hm45WNZ486Ty6Tl1ZKaSoQmN5C2DNw6ce26/xiOk4pQI6YkGCsIdxJVkXgKTSqn57/B'
        b'cq6otkwqo4b87yA53YNFPzWV023eUx2ur5PK8KBJDomk5ZKaegz2X1kXTH9RzfJp2GCrKCubYuwCZBXRlLW107j7B/bPnHOmKPxLNJKIkPVFghrNRZqGeufDm+UrltMT'
        b'TcFgHUQbKFkhmkbKqcXQNmrhTalUVPt7cBky+v/F5ifHYohniPzBamfIxRUi8TMLPDk9srnPsfEzF0Awvx9XtXqm7Z6HOQB7K2VSpKGVyGnh7ingegkiFtLvsufPnzvZ'
        b'LRILsiXC6ZjNWOMPOD3zFZPM+Z2/mDFghu+g4WvQEs8HTpubkD2T5SV1kpqqGjFm7R/1K2eybzklDEgBuCkS0cqKNTP0418QoH9Z0arLkBV8rqrPEy2HN5EqiP/ji2Lx'
        b'omQW6/eMNQtQzx8FV1y2UvRMyydjEK5fNmp+KhdyST3lE/8AVSSSrBGJK7BYr18jKl8xNUIqqi+Lnh7EoEHToqNJqCVi8bJobqF4hbhujfhZVFMxPYYqq6hADWtqZNU4'
        b'CKqR4GhCJKkp59ZU4Egpur5MUrYSmwW0XkH1717UEBpFT8Z80dyE51oyodGMTAwz4veZGAV0Fvm4DxNFxWquEVFaK3dk0kkMbmE4Hb90EWNOacCSvCxCLsTD42eDZjAA'
        b'dkfANnAFtODrizOglbrMYATDc+AcEQOOVcKzbKDcZE89AkdA3clggEGA9lxiNjE7Eiip+a+E4LcF7JeacksDPDLS6evq1fAO7Md5CnngDAEOEuVpmXIPfPaA3bCPz+OD'
        b'2+mwhZ+dKaSfgfH1CHc3tiPsgzt4JnQyxT74ElDC5lRwDJzPykwTAPyMDsf+Aj3CbSEL9sKtnjTkNtCRBJsD0zFM4LNn8QTsgmeDYasePxvukuOHYGzQAXqnPa0nQHMZ'
        b'/bgedpD0NUG3ly2d4DCZ3QDOg304wwHuovMBNhDCjOl5DKAXNDDgeSG4QV0HuMPt4DBspu9RGMRScMEAXmeA3eCKJ/WaCdjvAC9lpIM9VbAlDe0lG7TCvYGpsJVJuFmy'
        b'oALeiqfgZoHWTRiPKZieDTi9pglntHjx2TFgADbLfaiHfvNA7zTAHDr5JDuLJObV8sBNNjhcC65SlIenMuCRaaCxbATZHJiGQL1K2XPAgblUEgq8HQ+u8IWwFU0mTM+C'
        b'TQE8PcIJdhWDNhY4AQ8mUy/BwNvgPIuGMoaHc9Ky4G4MZ2fDCoIHi+mJunPgQT7PVfxcRjfDw9SVXAXoBF1SKiV/vh9+KroHdK9BCC7ATyHR38Jc2MoiFgj0EX5+9JX2'
        b'YWsiNIRFgKOWBDiEJmiGJyjugrNLYNt07i4GF2juGkI6XSDLJSA0BPF0G9iPKEdUgx3wNJ1ocn0jzs/TJ2BrLhFEBJXBLRQ7feAAUM2Qh1UWlDQ02NLiMlgMTs+QB6jC'
        b'z4nPg/YN6ARIXd1tL4M7QsEl0AJV9XoEmYlFSlVGnWX9wHY+6sI31uAWAXqIFfA0fdcFO00TnomRYTktRYnpPD0KXx/fzaGh+vPrmQSZga/yj8Or9N3nVbA7NjQUHgf9'
        b'UM0myPkEuCwR0HfF5yXgGuraAo9L0LAcAlxYb0T1LF8BLqGO3YvgJTSkCE0CDy2gLxYPmoIToaEkTt09QIDjCD+VEW0LroPtYaGhbGL9iwQ4QdTCJjqz2r3AjgggVIbG'
        b'3NKYg8nzCSotCDSwVkhJosCMSCaSwVGwjwKdF2aBTs0/rDetL61tk8kIHpPmYoMruD3tng7s8jSACgY4gKyUmiZ6E1DNxTd9U9d8SOY78FUfOOZBUcGIgCfxEwJkAVRQ'
        b'zWKR4CgLdk9eljrAvQWhoaB/3RTxQANsp/ZkWO+DyLDP5inlohMpXbSHu0gkAyfAsefrLFCunZxbAvfnhoYyoHqKwsiw3KF63MBuKzT5thVPaWwMdtMWoQ/eTJimllWw'
        b'fYaqz0VwWHbD3eBLFCv66mlO3IHnKRNQYQ0PP98CrFxEWwB4CPbSXDu0vBYzLQ+00FwbtKEtaCO4DvdOm6QA3JphHOAFsI+61F2Z7RsayiIY8Uj9iGp4DHTIvShBQZbg'
        b'XEaaIFuIDIHf5L0G4QR2wX5zFjgJTyLeUdfcbWBHDE6S4gnSWITBekN9BtgDesA5SiQ6F5kRzkRkkUFQqfHqDbMm0+3OOCZOcnNfHMVMfRvKFJck5U2Tk2X8STHpB02U'
        b'mIALCI1j/HRBhsA/G7+iBy5ChVkVUxQDFRTh+KvBpZnJeohsOC/MKRPegodZYB9UIzvgi9G+BK8iRYe7QRvi1/TsvqepfWAnvEwxVBQEr9AmA+yZ7o1C5vqXsxF2t+BO'
        b'OkulB/138GmeYyLsMoDbGevgTdBJK8J10B46MxuQWBtI5QKuiqZzeBrgrcSpxDSgfnEyN60HbqWR3i6Iekog0IRkFu7OxPdcGZgaKYEh4JBe2nJr+uq9y9coY9rVNzgE'
        b'zuDr790xFNuibcBJ/ozMOU9wm2lWXoGUlrp7OlIETk9l44FBFyohDxwElyhjFjvbjz8tIVMG9jDNUIRxhfIk4aDBczJ5FPTKYFPatNxR07mU0LnD6/Akh0HogUYin8gH'
        b'7WKkb5Rh6bYGB5FlAWcp0xKfQifa7FsCGzkSPSIYHkXqgoQTNIA2akAWOIt8bAdJBJTi93isEimx+0DPgDAnBtcalJYae20g6QAmtDAKZ3joE2wZAfYSJR7IxOJ2+VwJ'
        b'GAhiEjygIICKqIO9iykSyNd5IyuEuHfcFF6BB/QJJKr4Bb1O+XyM02UkDldnZFtgLdmbDVvzYWMaag+ETbk47yKVTrrIywWXgvLnO3mmBuTNcIXgrIl5jjuSNSxDoNnK'
        b'bIYlVOdhQ4i8ayu1szCREWFNVG8izEuNZ69dRxQgfmGOSKwBYtYeC3CbVh69EoY/kpwrlCyYw7OwZ/qstfA8nnXZStr8dvjAjmmKVwCP0ZonBC204F6AbfF0bGCDZXta'
        b'bOBeR6FlHY3iRcKANMktzTydlEa/gYusRAe89ZzIA/a54sjjAtgqL0RwHiXW0mc0Ml+EqIQIhN8FFQr8kIz5T6Zi5mMCNwYUpWLRooQ37w+0vLPBArSCE+A6lXf5N3cc'
        b'KLcxTFGgrAxfSsi5eLsXVlVMyWcDcgEzBBR2xEya/hJ4gQ8GwhhwO3byedivNG6mpNcxYhbqSIurJymvct7UQY4zf+HFOBTidgDE/HZ4EIXdU4lE/mArDsbPs8Gl5fNl'
        b'y8GVcBJRW2+RPXiJDij2m8AtaEbQCE9PzQmvrKSjbkcUTg2ELVk8hQSXxaMT+mw8nEIjHBNXIceUjiOQg7CNsq5V80FbaJgecrPlOJoS4etz+l0JH7gzNCwd9K1Ga8zB'
        b'bqpnAyU7hvAKuIkWMYGDUE1QzuwSOAIGeSStfe3rUAw8EAYvuQWj3hQU1vgj94MvA8rhhY0cfEWNiNkcCPfmQ7UJMsot8ERYcO5TuZ8vKJr/e0Yh5TlqBA8XR1IUzcRJ'
        b'QaBfj5gFLxIbiY32hhRh1gQiR9KPzzPHwEUGwbAl4Bnkoujo5yV4oh70Ix/SAvuJF4kXEdRZxDpMmuWzkHR1sPELUx34dT24dTLFsE2C3GIHOMcm1sDrKCQjQH8ePIlG'
        b'YSnnIMO8e4bu9cJrVBRyACgoPeJsguen6UnaKlpN1oPt9PQqcDQHJ8NeNcFKdIIBr5FhMis6/DudBrZN5jmBXaCZynWCW1lUuro8GhVOYHAhJzsLtgqKJqUfNi1ITS9M'
        b'LaCIGgab7UAfMihZAmF2Zg4yyqeh2gjsqIf7amQ2pUzpWnR05HkEnSvKqPsgxbw4LuJ4AP9q5hsP+S/6rf42rH3/+0Wu6fsfHXh9kzoz0mvIo5pDpktqGoma4XyzqEfD'
        b'rITAlWax3xdZ/63v0JOGnvV/uXPvWPzxAfjlPts+ncCfHPji2sAnMatXHxzp/yR4s0a78O8jBz7f9ifTZnt1Ksx7VUMIQn5N7jL54e7eluQPS8SXGn7mLIstvshfYCp4'
        b'5Zedir+mP2nU/zDU5wOwzurRwbUhzJ6JlraR6y1LnVzfucBm/vhqgFnLp3XGf1t/krHJav+T8kdffvrrPaP0+uN2x189VH/g1C8lyV0rvrmj510W2bR8G/tN/tedTMGJ'
        b'Y/q26l/uwKEXFny+1NT48ef3x1Rb3/9Llt6XQ7Xdqec+em/4Jd5DU82EYcFqv7mP9T7TbvdkFzD/euZRlNro8/M+LXvln/KPfOh+tCzlYbjdybbZ6867Pw548KeIFZZf'
        b'N75j8fdj104HzbLVDWUGv+AxL+iT2XM+Eb1ocW7bypDNB8Lkqi5/4cJqp/0/przytseo5qM75iWvj79h+RvzwYFMYZH3k9mfnTaYZVjS8UNg4wXORqWJW9DqLXf11Dnh'
        b'uv2uNcOZsXN/CXtL3P6hz7qdX5i+ZvTasn1VabfnPvR6zWHf16k9vqMeo7aX4Mtu0Ss/P2V7QCPJr3ij/4vHvCjOGSOnFl5dlOgGTzL2ekFF7k6tx3L1Cd4ao08i1tmu'
        b'TMn/NH+sm7N8jfkntmt/sKrlXD5adFP4gt3a3S3LveI6DkzU5AY73PRf7XPY9KjLrJ0W/no2f3qYWZC5/UHSexM/XoxSd708NrF4/j8TCiVPOK4WJwYiXvFWf5TmO++F'
        b'v5xZMf7DxA7Vk4m6wj+LdMe/81pd8471P6q++Lmn8f3+r9aVlXSnbrP/pmJe6A+X+e/4/LMbFOdnb3hrjvRCafca3r6SVW8PHf6NcfRoflIo+2CgT39hUdzsG3VJA0+M'
        b'3v/0bPRd+aV9j85lfL7pjRLLsaGBW1bli0/VFtvui74XsNS999AXluevmtx/yUfCjfp+zxffVIV7Qfnd8SeZH390T17YuWxt9xdOVqErT3auvgNi7qRt+rPwo3lXtm68'
        b'tYNf4ZXX+suFdau39PRMnBnc/c/7f0trt/3rt7w9lje7/zbkYXVfVDdfXv+XPauK33/QJPlW+Pkvs61tLg1G3Da5/0GY6B/cXzaWuN054FFeGl35/SvOm5KuifP+dKur'
        b'f9D0z+9zZJ84jbgIMu9vin+1ucrw1xs7+I/Ar190dpRHe24Z0rf+x/eb7/xj4JN5937KWr9+76o7bmeSbrq0/PC245Oo4K73lt7/pEP8ueiG8vHt5Ld8e68/CsmqO1m6'
        b'2u1rUaGLxverX+Qt+SfEwafPfnf+l4cDowlmV74NP2JSe6OvvmV2lGho91cdcf53glW7/H1OnyvPegfu+kvG+IrIQP/RGs+RmEHG6QuvNIeNHL++oqXw5R7p11Z/ueq0'
        b'a7V+yfjBOX3ffaYb+Tn6x1eW6F5yc9gr++nU+NuH7pd9Lv6A+9FrtzyXrPjwx7L5bIM7T07/4+3Ex96LXuruC7v6p4jR7vcqRE0mX7/sv3lg0TeLbjx0/avTX7/tKbr9'
        b'm5nkVrixZSvP7BF+QFCAHF8DnV/1Ip0MNfl0xw5cZaVWwhtUnhXsWl/B959MeQL7nAwXMcBJcNqY6gSHrTNgcxY6nzxNejJF54mzVK7UsrUhfOHClGn5WwJ4czE9rh8f'
        b'mqaSt6rAcQPQz1i3wOQR9WzjELyB47UZeWXID7Sic70Pl8qmEiwkZ6ZwERnwMJXBBRsJKlkqaRm8QuWegWZ/3vTcM1cbKvcMnE4GzfzsrIB0jHcu6DEA1xlrkE/ooHCH'
        b'/XBwZUZgLjrNBQrQvtYwhH7wNpWnNR9sgW0ZCPGn08LBNLMgZpUXPPeIytO+EG+Ogjt4Z92z4M4d7KT6SgvzEcWP+j7LIAsFHaCZQskJHWGaZrxVrpfBgN3gTA3FLuSH'
        b'WlFoN4Bv30Ev2AHO1U/9kkIMiwn7E3ke/6tJYP9e7gJ+Ivb7jDHq0zD9M+O9+ZWyqLAgCX6Hn8oZe02ffm++1ICwtj8U3x6vtfJqTNLZ2DWm6KztG5N1Ti6NmToHl8Z0'
        b'na1d47wP7Z3bWKNWLooKZfKIlb/Gyn/UyVfF0joJ2pJ0dk6HNrRv6NjUxtI5uisTOvlt+h/bOY1aOz9NwAlVF4xYRb9rFa3z8T/9wrEX1FbqMq1PZHtOW4JCNG7nrGR1'
        b'bPrYiTvqLFTJ1cWawKT7zsk6Z4+jWZ1ZKu/7zkHjAZG6wDAdT6DzC9D58tEsuoAgnSBYJwzBJT9Q5y/UBQgfOJm6OyrYE66En/9h449dPEZdhcOBKffsNIG5Wte8Yfs8'
        b'nYOr0qvLRScIUazQ2vtPfXVyVXp3xejmznuVf5d/r1w7d77GOV6RrPTXOAsQRou0gfHjgWFKHk4jQ0MEWge0YqCiussMfR32SNc6pH/qE6z2HmQMMtX+g6KhhOvV9zyv'
        b'12l9snE6UJmaoeKMeuHN5alXqdZrvaIf6LMoVI1weky21ilEFxalFGqdg3GqmVjrEqYLj1YGap1DplLPImYPe4RonUOnvuNujXPIj9QWjrhMMGy5jjpnnipsgolq485e'
        b'iMo26lWDFmpHrU/MBBs1TugRLp7KpAl9XDcgXLyVFROGuG5EuCBmTnBw3ZRw8UeTmOG6OeHCVyVNWOC6JeHip7KesMJ1a8JFoKqYsMF1W3oeO1y3p2EccN2RntMJ150J'
        b'Fx+lbMIF111pHNxwnUu4CFWyCXdc96BhPHHdi65747oP4e2r8+Xp/AMe8tF3BWtCiElm0RlJ55uNOAk0ToJRPp1UVKZ+YSj8nsW9kKHZmohsLT9HkYTT+3RePp3J4/xA'
        b'tUFf3FSLtyJZFxDclzmYqAmIV7AUizX2fjpXT1W6xnfWiG/sYMKI79whC41rooKJCOfuo0oc5gapMzTceAVb5+bVuX7ELVjjFjziFqpxCx338FaRx3wViTiTsULJQSCu'
        b'bgommq/zhRHXII1r0IhriMY1RC26+MJQojZinm5qwASTQJM9A9JOAb0XMW8q3yv5YvoQqfWb22mi0BvlhamLtLxEhPHCTlOdMFSdoC5TvYC+LtPY88cjZtOpVSMRaZqI'
        b'tHte2oicB0zSIUxhrVihcfBXJeqcucPuwUhydPYuCrHGXjBiH6axD1MXvG8f/VQdvFXWSLXRLkfcAjVugWr9EbdIjVvkOE94wanPSZ2v5UUp9UY9fZSrT8xWu2s9Q0f9'
        b'oycIMiab1OUuQOvFLMSpZ/xFOPXMexH5QI8QBqttB8mLDv3FuqBwdZ0mKGVovSZo/qgwatBnyOI6b6hAK0xHSjHLQ8lW1mq4oQ+M/69jtMIkNCISj1j5LjcMjfCdhRaM'
        b'zCJ1OUUIi8gFVALcQioBDpVI/D2UQo1zsNpD4xyurtU4J444p2uc0++Fv+dMmQah1iFo3Nn1aFpn2rDPnCFvrXOqgvzU209lccGuz05t0e94okTnx7ug36evJvuNRpHO'
        b'u1/zveg76D6AtV5+Xaz1yZqh2sldcTiVVfAuMmIhs5QB7zoHUiYjVusQO27vjBf10zr4o+qnrkKEZ1C0LnbucEwmQj8oC6Pvlo3Rd8gmx919OtK/cnDF5nZz+2aldMSO'
        b'r7Hjq62vuVx0GZSPBCdrgpPvWb/j8prL8ILFI2lLNGlLPrPnol3buI9Y+2qskTretxaMIbNs46BYorXxG7X2UcpVxRrfmPvWsTpr+udTvO9b+yEZaUvWeXq3ZercvTvS'
        b'x524StcRp6A/WlPcoXEKUltqnMKwI3BXFmjteDjjN74zXhU64hSocQpUJ11Lv5g+KB3IGSrThs3TeflR6ZXSEzkjXrM1XrMHk4Y8tV4pI16ZGq/Me/larzxF8qi3vyq4'
        b'rxxn4A66v+8doyQnWCz3TFIXMgtJhN9g8pD7UNld7+uZKm9kTIyI4Ah12SCpNsKy4T1EDjEGKelgM3lIOpCt8/JTRZyI08UlDvOitV6zdd48VdHJYmRUVQ4nclBQ5BOL'
        b'jBECMhnxjNBFRCpZymVIBnF+rYvWOVAdpnGe9T7mnKdSpnXg4+TZpRp7/xH7YI19sNprxH7Wp7+nzYMEPcLB5fskPcLcZtTcQxmuctV4Rt43j9KZ2x4yaTdRiO6be31l'
        b'5TBq6zPsm6q1TRs2Txu3cmjM+uHRLMIv5DuCgbY76j9LE5mq84sf8tX4pX3HJKMyKMXKpBQLlUwM9ROVy3g/3mRBFGskynmhjT6dKGk+xsJ3tv+PCZLPDTxwFmbp88IM'
        b'KrKgijcwXBxBJ07m65Gk5WMCFQ9w8e9mT3brCYhznEjmjPvjqWzJ73DYd4BYin8AkZAw8kkJM58hYeUzJewqluF2HnvMnLqoppIYJckSSZ2k5gs0+Cc3+v6aioskkwmL'
        b'ogpumZgrwkBCinrZPL0xg5ISfHNfUjJmVFJC/34hqhuXlKySl9VO9piVlFTWSKSy2hqxSFyHGvRLSirqylHFpqQEZzvWlJeUyWSSmuVymUhaUkJNTmezUnSLmyowalI2'
        b'quwkvjAOpiDo24mb4Npmjim8JgPX/TmGKHDPFkgmY9dAeFSPnQfVPDKlJrXoIVNaiybJivETtS/KAbnmO75efWL/pnkFEY/ZSQI/v0aO8J3Tj5t6X3lZ4PXP90o++00+'
        b'lnt/rdvtD65L3/aSRr9+AxQufe+9pR+F3652PrevQ7yvfDWbrb98Iu1RzLEfZ1t3l9gtC//m+8ElP/157s/nHswehv7DC5pOfXf4yTthi5d6vPvwzlsHDazvJn3ys3X5'
        b'Bcf1FibLAo/fUHzR+e6+ms4rhS/7h4XGmpiFeAiWJHx4oQpoZ29n7dvL4PV2OlR0Rn3Rybbu9N7fmaEKOnQRLE0+sCixe3ROx/Wd8q/0IjqX6Cr/Xnro+q5NlZyVX5HR'
        b'kS9b7Ck70eyaXb87Ti8SRu20v5Jv9SlvcMj+0CCQL/mugNfrUfix+2tLKnqFnNXWs+767OyQLj8i0zR9F9Fxu/Sc9+chd8es+8OLnEICOZdqX7H2rf/rhhvfnQU/bzuy'
        b'tPOHox8WGjzO93zzUv+T99Z91upY4Hv6w96+26kfGln9lvai6v1vCpM+uUN25eS/2u/JY1FvvKyDRzbi53DNmSTyPwS+X3GgX1xp85BP/nSbwB9ctnj2223gzIuPqAfH'
        b'J9B/Vzn++NUUdBrDcBSQGxgAW7JZ8EJy3iP8MxUlcBCeloJzqdmCpzdUFrAtqpgJ1Gvgual3WAz+2+L/8zssc6hPwx8+9EEEaVNtXVkFUoH0qVMIG5VP0CkkgDCxmWDp'
        b'G9qNmlm2hTSvUbg3b+yUKkOUZcdwhnte1+aLXmrJoPtF+WDexbUDwrtJ9yxhqjYk80N7R0WIoqwzvMtQma6xF6rtNPaRwzHZGrvs4fkFw4VFmvkLtHYLPrTlKi07xMPm'
        b'XijcskehgBFhad2W0G7TOPcxS8/Q77E5y9BjgsCFsQHXSGds1mY7wcQ1B2dFJV3z4aki6FpoxKAeXZuTOFRE1capEWxco0ZQNWoEVaNGUDVqBK4hv2xijsbo03VHFzRq'
        b'su7rj8ZN1sNmoZGT9QQyiUSjqW8G9GhDuk6NnqwHhAzqDRXpLOwUlaqI51UfmiHAYQNnFK5b2qMW+v8HHD0P1Or62DyFYRjxTwKXE7kswsh81NC8TaoIb1uhMfR4zChg'
        b'GTo+JnA5QZXfMQkjT1yYT7CoVrEBqj9ikIYhR9YhX2UYQnU+wA0/TOSYkoZp5KilW6/xsCBFy52ntUwdNk6lPdjuBOckc+Jlc6skTybtwazHGEhc/nP+67mia/0cn/bM'
        b'r6VPFfjBhjR20q/xSNIcuzXz73Hx77q143ohxCVOLLNG/2UHtvRFAr9XvFTUGmu0bY590p348FP5fJsOgWR771vkZWm3v3rlnIV1n29KXMggT6/Lj6nsOTSUsFXvg9cG'
        b'TjdFMN5K33Xz2xHXI/ZyzfXIw8VPlqbJPpF3177p8dKj/fOYiW3u85pC/e9XK6s1Do+P7Sobsvl78bq/VscmL/oi5cufmfCIVX9XBU+fenSUmQu2Ur8imwP3gja4A7Zk'
        b'6BMccIkBVQKooh7f+HvDmxk5AngRQ+UsBoMCBrJCN5ngWIY/NQcDKhmgGV9G4+tU0Ar26hOmlkxbgSs4Ce48om4zjsWIn75dOKeYYQC6QQf9Et/5ODKD/mlaoALHqJ+m'
        b'5fAYsM0RbKfMKeyGB8TSKQizZ79dCwfAVsoSG8Ne0MhPZ+PsCHgFnIaKfCbP87+2jf/rz3KeK5KeU9b0j7b0uXa1RlwjQ4qSP2VX56HilwYcIbGtdCbWIyauGhPXI2u1'
        b'Jn4NKTqW0a7MLZnDFu69kfdZAR+x3D5gmTzWy9VnhzwmcPlPqpyoMCWMrRtypr14wx1j1orEYyz87scYWyavrxWNsXDCH4oza8pRid8tGGNKZZIx9vJ1KNoZY+HU3zFm'
        b'jVg2xqZ+uHGMLSkTV6HRNeJ6uWyMWV4tGWPWSSrG9CpramUi9GVlWf0Yc31N/Ri7TFpeUzPGrBatRSBoeqMaaY0YRVTictGYXr18eW1N+Zh+WXm5qF4mHTOmFgyhkybH'
        b'TOhnXjXSusiIoOAxjrS6plJWQkV3YyZycXl1GYrWKkpEa8vHDFGUhiLAehSw6cnFcqmo4pm9kXKxafhvP1wubSbypwr8o1fSHFT89ttvvyJLYUaiuBSbipnlQ6r8dwwH'
        b'tpB3jfQSHIm7jpwEb+ZPBlO/2TpmjmNQqj7pYX9yrJz5I9xccZ2Mi/tEFdk8A0kSlhsUqJbV1k6KjWQObjJC5JXIpDgTdEyvtq68rBZRdr5cLKtZKaICaIl0ShqehbBj'
        b'BjF0bBwnWUfQ4bk0ExUTTJIkHzBYJGvCmOCYNOg/ZJXok9YTSWaEocWIgZPGwEmRPmLgqzHwHQ6Iu+sD/bQB6ToD81Ej22G7UK1R2DArbJQwb7N/j3CkVvs/nKs2Yw=='
    ))))
