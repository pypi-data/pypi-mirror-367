
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
        b'eJzVfQdYVFfa8LlT6FV6HzrDMENHRFRAUDoo9gYIQ1EYcIrYRWNkUFAQ1AFRR0Ud+wioqNjOySYm2U1myOw6YVNIsptN9kuymJje/nPuBZVI8u/3P7v7/R9eD+ee/vb3'
        b'3PPeywfgqR/26O8vduLkICgFS0A5WEKVUjvAEpaYreaACX5KWacoAM5RY/dSq1I2C4i5p3D+3ONWa4HMaikLl5uUcsa3307hUlPxL0ahQCm3AJhX8E2+E1sULMyYNY9X'
        b'XVOqqBLzasp48goxL3+9vKJGwptVKZGLSyp4tcUlq4vLxSILi3kVlbKxtqXiskqJWMYrU0hK5JU1EhlPXoObSmVi3uiYYpkMd5OJLEq8noLJG/+3JIj4CCcNoIFqYDWw'
        b'GzgN3AaTBtMGswbzBosGywarBusGmwbbBrsG+4ZJDQ4Njg1ODc4NLg2uDW4N7g0eDZ4NXgeB0lPpopykNFOaKl2V1kqO0lZpoXRQWinNlU5KoGQr7ZSOSq7SRummdFZa'
        b'Kt2VJkqWklJ6KL2U9mXeGPVmm71ZoNFzPDo3+5gDFtjkPb4Ul/iML6HAFu8tPgXA/1fr6sA69mJQR5mX81m5JU8T1h7/dyBIMBnlhgLAN82tMsN36yNYgDCDHWu9Vduq'
        b'CqAIxDdCCWxDu1FjXjbchwbmICVqzuOj5oz5+UITEJzGQXdQfQifUriSATaslWXkoD3BcagpBzVRwCKDBbVJFiXUUwuYNLYAFU722zfgRWB8AYxDLsaSKcapOcalJcal'
        b'NcafLcakPca0Q9kkGmuYrRp/wYSbWTTWqGewxnoGM9QW1ijWJqx7jLUd/wzWchisPbfIFFild3MBr8hqnd0sQBfGTmcDTn4uF4CisFfMBExhJ98M2HkWmoKiouzV0z2Y'
        b'wleTuMCs6mcKJBVVXc12AGdAlQUuXix35TyaBJJGHNZTf05SRQ5u/hOoMscVXA8V9VaG2Ba3j3pLKgp2YIp/CP/CNsBP6MPKH6Z+WrR0nQwMAUUErlgH69ExTMDd4XNC'
        b'QtCu8HQh2gXPzAvJzEF7oRoNhIkyhJk5FJDYmk/DxO0YRyvOGNgbCK3YNK0InUAZ+zE12P92ajzDw6YTUMOSoUaMwnZFOTsegIii7OdWzGdwgLrhDXQTI6FJkIWaUGP2'
        b'nPSMsIz5ICqrwAm2z4O74X6A6mF7OdcUHV2CLioccackdGVjNLyGUQDPoJsxYA3a7a1wIqPtXAV7omEfqTmMK8FqeNScqWlAN+GV6CichQemwUugBDb7KAjDw/oldagN'
        b's4MImMBWERzIo1drAixcT4EQLHJFYat4fgxHnPBwsMui0nGuyPPelEJQeer5eo5sHb5vnxX6/rFDryQe3tZ4rO1y23o3fzZaxdtZ7/hiVZnd8oB5LBf2rihF1MLLkRHq'
        b's9Wsv+cWv1ZGnSvPLOYXZRdfEGuKwVnuLnnkaa0wKYpN1d9wnWtc2hHQmmYscNWnuhbEt6QN6pcN/c5KPsPhxvfPucUvBYKj7h9t6OGzHhHdiVrgLoUlxiA/R7EJCEMx'
        b'N7GAE2zgmEENGnjkTuA8B/uWYUTvQntRExug2xacKRS8jC758DlDrBC+1Bo3epLICIPx6uvrv3NOLJPWbBBLeGWM6hfJ6irL5NOHLGi9XlhaLBdveCrPIp0bcPJNPRhJ'
        b'pYCdg1LWEtu4oWmDas6urcqtbzvzdL4J/fP1vil655kG55k6u5lGZw9V6b4qnbNALdc5R2vkytlGRw+VuDVPmWZ0dDmYvi9dJVanqOeoU7oqNU6aNVp7jey8u3Z+f2T/'
        b'nP7oviU6ryS9Y7LBMRm3d+C1TFM76R2CDQ7BOqvgLwhbSglf8k2GuGuLqxTiIdPCQqlCUlg4ZFlYWFIlLpYoanHJLxBAOLiIR1AgtSGFtjh5GlB/0qiWAEognUlRlMMI'
        b'+K1k2MZFWdm4uml1veUIi0s5Gi0nKSc3TmmaMsyxrc/alrMjpz7HaGZrNHNQWn4zwgVcu/Gl9XnMPxlhxf3mAnDOZgp7VglrIq2wiTRhEUtK6wXqsV5gTaCl2eYTSDou'
        b'YT8j+6wt7FG9MGHdr2vpxwt7Si+Y5CpIEVJPE6E2agHajU0aEMLzaBstmBLMqHdQGxsdwDIfDsLjq2nhh3vQbdSJJTYJdhGhFaErqyvf5a5iyZJw7fW6H4kUHmurpNhx'
        b'LVAF+5oatxXHOmR37z7TdlkZ+/z1tjN/aLb4fcnKjzh/X/Gi2TxkVuDw+7sdFBhKtBR6fcmnHnngYRaK4TlBpnAaXoIyIxsbC0t4mYUOw1vwGJ/9S0YhXtwYlwxZMgxS'
        b'VlVTLN/w9A0tF/GjcjGPAk7uB3P25aj91TK9o8DgKMCca+uI+cQ6wOiKWb/DsoVrdHBvmayKbZ3ePl1n5Su1e8LIUmL1hril4pWVcilBltRhAualuZdhXhfCvE8vR0Ba'
        b'raG5lyyoALOvO+HSX0/+pex7wDwMnLdJYNNq9S/rHKgYFghJskPVKoc8dwVZ7QJ4B+6WyeMi0AV4kwNYKwE6tRH20x2+XOFExbOAa4v/q9VGj14nhTNhjCtofwTpULqa'
        b'AiwxQGdQK9pOt8+NdaESWSA+YhqsXlR91IZuv2oJbKXHv7ycDVjlAJ1D2+F1uv2BLDcqCRMsovzBZtdF6lX0guAx1Ih2yuSTI1DnFLwgCUBnk9BluoN5sjuVygI8O+6D'
        b'zcZJNXaMzTmAjotIe9iawAKsGjxDtB/dXMTzotJZwC7feWjzoi3ySpqxF1Utl6G+2IiqOLx8+BxAvQWpdOs6Cx8qmwUiRpa8udmYuNBb4UYGb+aiAbo92ubFxR12ANQH'
        b'u9A5usvZ9b5UPguYqdl/3qzim09jEHR4gUgmjY2Qw0MUvZzz2M84QLdPr/aj5mEKRDgPbl7kPt2G9hlhFzxainoVkRH2aB8GmJji3lx0ke7xsWcAtQiTIEL87mZXr9Vs'
        b'ugdqdKumO6DT8DAGGR7Ai/JDZ+geSeXB1DJMBG3py5uNK3yrGRzVw55NMll0BNxZhKfYCtDFsCq6uS/gU0WYBvnWD2QqX7NcGgTrrZbM+G0iTDPYCVA/7PKg278/K5Qq'
        b'ZYGk4cDXZIvm77GlsQRPogH0PNPlGOw3xX0OAXQ9kCHDZy5hVAWmGm+tTubK4UUxMOxCN+B11Cuzspi9AcOArlAxeJA9dA+Wl4iqYoGiiNQhmatlbCLdIwUdQW2W0rgI'
        b'CTpC0HQKoGtwN7pJ9/h6XSRVi0kdMeWPMqMsbzbNSkKoKrNElzHtbsNjuAt2yNkSeJvu0CiNorCyyI9IfyBzXfcxYEh3MgoetbSIikA7/THt0AHKHJ7eSldlor45lugq'
        b'BvD4KjLU8xSFVFto5Fqg46Uy1FtnM8+CAHKMEljCkzSvrZy8QWZujbTSGDLaHSoO9gfQo7Gwo9RiuUaBrkJ1JLm9TAUKrOlFowF4He6XWUrl3BTSS0V5w27USdcloa7V'
        b'Mjm6hoGC+0llMyWAO0LpIYkgN8psrC2gEqOOzaWmYYocplV/ZXUKrrCBA6iFAmxzKqmikJnqILwJm3HVmnLYQoDqp0RoP6P/WQtdLa1rYZMDVHIA259Kgv0ieh50eja6'
        b'Q/gb7q3DAlEL0IWNsJkZrxn2crGsx2BX8zkTwCrDymE99phIHS58nmbAa+gqlxG8HtghYXjhmil8ToYuo15bdAK1ECRepGKsRKO8BXctlKGruBJD2EMqz1LR66Gab0sT'
        b'8nvLGGodFtsk4Qsy4/Qv0ujCnAWTqU0sUKu1f0umYiUH0YWCvHiqHkvr8PRXZaqAjWvpwk25U6kdLJCuFdyTqTy7XOhCuGkapcRyqlv7rsw1O7CAYUrTGVQTC1S0TBmU'
        b'qYI6UujCP0uSKbxgV5CrlxmnOC5j9FpcCtXOAovqrV+XGbP2uNGF3RaplIooRzGWgoUKRiXncmZRXSywDri+LlNxg2fShT7eGZSaiGTm4GqjWGpFF14LzqY0WIiGeW+u'
        b'Nia8yxQGVuRR57GcjKS8tHpR3idSuvDdDXMoLRaF4eCXVrsG/JWBCPELqD7M7naRutXG+bmTRzWnBDXLLC1sfLEuZFtRSeg81NIck20VZCm1sc5DzZiV7KlpXNhCE78C'
        b'nXNAvehanaxiKptmaQELiz1NxIFJqB6LAVaWFkhLmLOd8kM3U/kcegG2YS9RXWywrqjg9TpVTb87XWiIuU+psV3XVb5co7I+xABlF/QK1c0GSXb+92uMFb1My0mTfk9p'
        b'2ICny9bVGBfGCMZt0szHvB7yfGe/+eiGmmzTnmymQZn54w2byb99w1bxS8fMDjzrmM3IVfgSxCnhAXQS7s5De7Af1JiRI9qCub0R7yycizjB6ISCRsCWQPJoQmVuBoqq'
        b'zNcEMhulP+bi/TSISDAvKgpr90oECrIDSV6JTmaFZ6E9eRlcAHfCk2ZoB2s9bEPtjH29lciBvbCPbN/y4EVqMYDn4bmldFd4xSFCEIL3Ncpw7IxZlbNRE1TZYuV/SUEA'
        b'oIrLYC8HbEFNIAEkbI6SkjXQC+ky4wAz4BrOxnv4rA0SptA8yhRYYQtjySsK665xBjRn+aJu/1WoI5rsSuE+UGyK6hUBOL8cG9WDWfS2aS9GRFMW3BueAS+EUCABXuHJ'
        b'uTauaIAeoMgSHoLtrOgYMkA7WIn6hQryjMsGPQevCfAGn37ygnf7GRywkeXAxzBsWU17ukmROQsDR/emeGM6AM/TA4aXwD1updGwh2xnj4Iq2GlGl0/HVq3ZLzg6mnQ4'
        b'AsrhvhS6fBU8Z5GPN7nRJsRZAasWwJ2Mx9yzGLbBDqvoOHKjAqVQKVB4EtLlwJasTLKm3FGiXIJXbGrZ8Zi2tBzCjknwJureGB1HltABxLhBI02QBNS+LCsbdwtHzQIK'
        b'WC5hYRt5EF2s5vNZjDdTbYOOwwPRcVhfYDtdBpvQIXqVs/yxJT6zLDqOrPIQKA/H5bQ6vQX74QW0G29ic7gA2+BLHG8KHo93ZDTCRdSDzubBxmisEbBnAirgkSK6HwU7'
        b'4S4BoQhqzIUXOMBqGtveyZaqpZdR4VKFTlVEw6tkBjXG4X50llYYJXnhaHd2JtkKh7DY6DYFD81GDYpsMtextWtk2RkZOeSRGv1cYokTeTIRIuKH5oj4QpYFPCmGp9Ap'
        b'2B0SAs84C/iwHXULHGG7sxPqdoGnWQDucrSD6nWwpeqbn3/+OWMyYcJhikoqyr6yKQkwuD2CtqNOQa4wnQMq13GSKHjWZwmfgRbeyUbnZdZSBRtMhodY6AjlP2kmIySH'
        b'lsLtqNeGVOXBNha6SvGnoaN0XRG8gR00uhdsiWNhmATYRnUwSrAPHoAXZbgfBdB+pCJK0EeBzTBB0iZ40Um2RmFBgUAhC96keLAlZdTJxG2PYxtXh/q4YN1G4qj4wovw'
        b'DlN7Ee2EJ7B/gfqsKZC5gDgLUdhOKhlzfBF1CS1tLOFeFrCBfewl1NIEdJLxZk7PhXdkcos6DkBXvFnwFuUJj2UzlvqEC9KSKswCDWkstA0vZh+8yfijPajfC/XKpaiP'
        b'DVLhJRa8TXkgtQ2NstB81ClDPXITsHAxhaUC7bWCAzR0kbCrwNLM2gIPvoPPnkylY/+AwcktJ+wP9CrWWGGcXIYDLNRJBadjl4GMtwUe4lraWJkTcTvBnkplQA3aRdfM'
        b'RbdzsM2X2rDA/By2DTUZ70jPMSx8Ht7GewTsLPRYs4jv2cj2o5Knwu0MaMfwbBdla+jpWixZ8CrljY4VMwQ/gJlXZkFI5476WGgfxROZ06s3id9gSZcjDWpmT6IiymEP'
        b's20+sAyTp80E46kMhIEweIFFI5ftPCNtKdxta7FmLQU42F+BzcnwNq1nEiIUDEiwm0tAWhDO8FS7NdYBDE/BC540T2VgzUqTah8acGMWBg9l0gsrhFcZeDrRIdkovwWY'
        b'MOx2GBOfrjuDBvIYboN7CGYxt8Ft+XwODe2KWPcxMhbJaCrCs350PwrLp5YhYzo8zdARnucryJ4c7uCizkpMqN3oGrblCi7gwBsU3IZOhtP16CzRTvD0Eri7Dl21go0c'
        b'DL6Sgh3hnnx2bi7DQgNQhZpHudIEPU+4Ep6G3QwRejJmjbLefoxNwnu55TQRMt3SGXadizpodhWgTj7Dd5jf++MsLcxRDxuYWrATqNlwbw5dMxUe3CijkYoOVRKX3Rf2'
        b'imk6uK3Zygh3noiW7S1cukMEVqBqSzMa162RbAtKtAz1M7J0J8QK9VqRmtJE4oMGYze9ge5UhhpSMA9bSdkgq5aFTlLBc0fBWZq8UmaDrsoxCfbxWegoFbACGwSaOjdQ'
        b'P8J+7VVLzAtV8SzUQ8XFw05GKI7x0AlLKbqCrnBAHTpF6CrywzxHhpTAE5ajonQT7qNlSeXM4O5MZLYlumK+xgTkWLODqSnwDDxK465wMdxJ11BgFjrCDqESuFKGFn1b'
        b'QmWwuRZh3QybJAQsPrwNbzHLuAL34x0Aulprizm83oyFGqkgeMdNEUYrwXhM6N2oDe5di9phM9wFL8TBM1hXHURt6MBCDLFyg/8KjhMaWMLgbwfSonrUZordDrQDRIAI'
        b'vHO5rsgjVSfRTTfc6yDecyh/MVo7Lm3Bs/Tg3+1Qi3cI+/H9Qdhgjs6igxbYH9DAcxWrsKhfh2pz2LEBSwaZLgIeXjuK3bjFNHaxjWKcnEXwwqwx7MI9njR2Ewl9mHVu'
        b't8DcyaARHgomeES7ZjOC2IMa4KFRRNq5ETwKUIsiFVdV4uUftkTNWdgGpueIaLslQM05mcK5SJmH1VFBiCgnE1s71JzBX5COPZC5GB19soVA5oQRkms3fUoRM8dVGboO'
        b'e+fmY4guwFOUA9g8Z3SnhlrgqZwCXL4vE7uZ/rAT8xxReanoEuwbE2Z4eDEjzcfgCUZkD4dhpN2WPiOyqhnMhDfjcsdofDqXpjHqisfIoH2+0xlVWSJhaCaB7CJGVwO8'
        b'aLuAXVVmRo+9LAAdIEcGzYwHsgLuN8NmDXPN4c00B01OKsKuZnpYZp7QBFhmsQj8R+C2RJpdazjo7KhsnpHQslmIjQzx1pAaHogVZOZkCcm82NmEe5F6EjzChtpoqjL+'
        b'kg9Hlog3Bu/fiDu8ICfPkOR65OO+tz/t8dHe7eFt73n/Gk89/NKGiPeONwY/Mgl+p7QkbvG+lWb3OnbrZ7ZN++T5daBtp6to2Q/UigGPPT95v5v7qqS8y/2DoDeqj3b8'
        b'bf2MDw9fm/Zoepv6du6Gr/6UlxxPJWSItmyf9frrZqeLrPO19Zszp33gfrPjB1tdi2rL6fjXvsu7mVb73Sf3D3i8/WXF386dSstZ0jI17YfzM/6WV7klirfraPz3DSe9'
        b'7jccyDhcMN9LlrztpLRkjXuU/xtzO4bPbEnNVNXcuBLgOtvnmPr3Q0qnGJMP4qyunDx6+1W37wqbfvhHnF04f93i93crFw7lbv9zxFsH3vnE+eGWgHt/G7nt/sFP8vbW'
        b'eberS5ZlN+/e91ncqqbQr17q/tHrhZecBoIefq3M++R3X/395+J/mH3b1ij5nd89zW0TxenukzX9n+97/17fC3dkU2Pc3giN/rB2ccfbhffWfaSKr+34s6lIGjvj+vP9'
        b'TbwbFqfKHlw693pEb82np/+r3avd7M2yPy9YduLtoZ8/tYla+M4st45m+fCu2nqzhX9cErw0PHXP31IeuL47f76sLe1LfljT/c9fiv/i3Fsf2nxWvrhsXZzTzE2nqt9b'
        b'e7D/vx70LV64O/7gnv7vo4Z+d68qYrvz3+8pd4X+GHzSWtY66/SZynlzShYvd/uwKXKyQVUXvP3vM063LZHcT2xz/nTv6vgP1yx7ac2JtKUcyZHUB0uDH/5QPbCkdvaK'
        b'8Pi6va/2FyxenvHmtD++EVGzUqMQfn4v9SO3D26/9MXpii/O11yb/SPmkC96dn6hDUn8i3PTivUJCx3XJX/VH3HGLWhnf8lr8UfmNS39wOWhfO/D4396LmuAs2Lpn+5s'
        b'3TPw/cvmW1/ruO5y4ufAEE/1g84tb60vb/+a/VzHPIVVx5d3C/a/7/DOm0k1BybVnPrp783ln5/q3f7DX2+pDhVPaZt6pDrvVZ+2xX/cWHZG+OZPia/ZsDdIU9+jwkrn'
        b'qV988YrtnfjQr7Z1fn/v5svte65eMzauqDmeNsfZacXDwo9/MGye8l+cz3d9kuC0KGft8bOHdfOfd7tj39m/RVjy49DwbafNsYbAD6w/++OJHfq7Z/W3GyJ2x6ZeuWT7'
        b'6aHhh5ef35C3z2arcleeQ9rsDy92/L7r0SefTWmxfn/zD9a11yJelLrzrekzK/hcFdSi3WG52LdGe8PwJgKew8oSHUUX/VEf/Rh+bizcKxBlhIXyRWjvOm4YagTAlcdZ'
        b'sQBefUSbkP78SU+OtEpM6BMtC3ibPvBCarSjJB/2CETYjW/E45vAPSwhbEbPP6KdtdZIeDYrLCQdizkFotDzZnj69d7o6iOimVLg0XS88WvPysgJzTEFJhyWWS6sp9dd'
        b'ShxSQXpYKB4Ue3tNaC8bxC5zmMpGh+xgxyNi8/DWMSsrT0gBU9TKWkslo8PoDnMIt90BXcfG94xAxEe7sC0zgedZ0dhv3M3A01zoSPZBaHdOWAbag6tjWDYS2PmIaKaE'
        b'eag+i5yUZmWQk1KMr1LWJtSBDsHz6AoDUjvssBGEjsGLGleYT2XBo1IT5ozwPLo+NwsrS2wahJlheLvnBVsnoX42algFr/LdfnGs8Z9NZGT9vF/81I/9MEcrk5jjC7m0'
        b'WCIrZsJLNkxQRh+0lJiMHkCygFvgCEhjWcc9pNMWjtHFQ5VtcOHjnKOrylPnGGT0DVQXd7to7DWRGoduzxZOy6JWG9IsvX3LAxfhoItQ7xJucAkfAZH204cDQ1tSVa6t'
        b'ucYgknFrzWvNMzq5qULaVzxwEg06iTQyvVO0wSl6BAhxa28/dWRXubpYvVK9sms17mDfOvupniMmwNP76OTOyeqYjmld01pSje7eqjVdwS0zjR4+RxM6E9QlHTO6ZuCF'
        b'RWmiDB4i3MAXwxPgNP0hSVRcIy8QD71GvbLbnLmhZ6JvPHjq1M5pqmnG6HhVqtpb7xmh84wwevmpSzuXq5YbI2JxqYfeU6jzFBq9/dXyzmpVtZbb79hjrbU2BvA1847n'
        b'qHO04n55T7W22ujJU7t15T3wjBr0jNLG6j2nGDyn6OjryZDhMXhId71nmM4z7EmpKBqXunXkqfJIWZXOKwpfZDznruwHnuGDnuFart4zzuAZp6Ovxz2HRZGaEm3gmVXn'
        b'Vz09AjOqIAKXOXdkq7Jx2dHlncs7CrsKR4Ct2/Th0HBc5dSRpcoasQFe/kezO7NHABWaTBlnpj9kU6EZ1ENAeWVSj+h0hE6HA4I1gceytIH6gMmqNKOPvzqja+sIYHtN'
        b'N/IC1Iu7bbUsHS8aXwZetFah5yUyd3r6GmaaPODFDfLiSO00A2+ajjcNZ4Z9fDE/LWi1GmFx3Se1mIxYAf/gFttRdI4AE/vpdIIJGxJ2yeasjVamD5lqCJmqdwxsSVNF'
        b'q7lGF/cRwMG0VtC/NE7aII2PxoeglaNa0GWlnq93FRgxzLYqW6NbCAbHabrR1ZOuKtS5xuLL4Brb76h3ncbc6V1jvzE6uKjM22foghJ0DuQaDku663i38gUfQ9gczJvO'
        b'7dlqF70jX+fIJ7zNby/UhUzXOZEL86XapCvxgYdg0EOgmaX3iDZ4RJNJF1LG8LS7pfenvFBjCF8wurYFetewETPg7aeaZfTyfZz4q9J/mXhO09GXkWZTmlOZpup5qtzH'
        b'v8aGGPGydZ+EqU2jlAc8vI4GdwarA9Tru8P17lEG96gH7vGD7vF69wSDe0KLqdHB6WD8vnidp0hrqneINzjEPwRB9nFGb1/17I7qltlG79k48fI5uqRzicZU66L3mmLw'
        b'mtIyyyiIHAF+Tlh34KTDVsVVKdTFxoDQ05nHMzUKrVxbpg+YZgiYpjI3hgg0bE3GGZvzNipro0eIJnLQI0znEWb0CdCYdG5VbR0OEV6yPGupndnvdd9ePyVTH5JlCMnC'
        b'5A0Rako0Uk3JeQvt/P6ovsUPYtMGY9PultyP1MfmGGJz9CE5ai5u5xukCTruo/b5tYHoJrrQBJ0vuUgrq7NW2oJ+4X1ffUKWPiTbEJJNWj3urw+JN4TE424+fiqZOrZj'
        b'Q9cGzfJBnwSdT4IxKE5HX8a0zLvz786/P/P19FfSdfOXvJz3+7z7+N8Im4pfTsQoeAURI5xiFvBdQQ2P48q/CmK0i/WCGQbBDMzkblkUk2LJTFatM/oEjwCuVxZlnDKt'
        b'v2zA867YMCX7/hzDlDw1R72g20qzSM+LM/oLNGsH/WN1/rHG6Mn9Jn2Jd00M0bPVqRrnY9nqbGOgUOsyGBivC4w3xsT3O/dl33UxxGToojOZFt8QJTirc4ZqxnBYpNZX'
        b'm6z1P59pDI3VCLBeS+5P6U/pq9SHJhlCk0a47HBvLO/h3oyq6cgjbOuvLussVBU+0ZXffjuSxSF2hLEpT53JWw1ZPW2FJjqV/2fsoBUYizp5yvRJQ3Ayka2bSbpgP2E0'
        b'BoX1fz3E/w8e8R8yjwSXbWaw+RS95SrBjsr2rIywDKEZB3AABQ9VweZxpyUEfvooggC033r0tISEHoJngw/LrB+fmnD+7acmZXzWl9V4eRZPeyf5hBoyXvH4yFY6XHZ9'
        b'rZiXM29KTASvRkpnokTjuo67yZDzpGK5QiohY1VVyuRkiJXFktW84pKSGoVEzpPJi+XiarFELuPVVVSWVPCKpWLcp1YqluFCcem44YplPIVMUVzFK62keaRYWimWiXjJ'
        b'VbIaXnFVFa8gLT+ZV1YpriqV0eOI12GGKsGjkDZV44aig6WYViU1krViKW5FAnoVksqSmlIxXpe0UlIu+w3Ykp+sYj2vAi+NRBKX1VRV1dThnmQARQkGXZzw60MIMQ5L'
        b'xdJCqbhMLBVLSsQJo/PyQpIVZXjt5TLZaN0G/i96PtsH06OoKLdGIi4q4oWkiDcoyn+1MyEBAfPJfCm4pEpcKd9QXFH1y9ajtHrSOKtGIq+RKKqrxdJftsWlK8XSp+GQ'
        b'kYVM3HhlcVUxhqCwplYsSaDRiTtIyoox4mXFVaU149uPLqaaWUuquKSyGrMChpQgaqKmJQopwdD6J6tZiLorpArJhK1J3FsCneIxFSUVuJkM3ymqf23VJVU1MvHYstMk'
        b'pf8Llryypma1uHR0zeP4ZQGWB7lYQsPAKxevxKPJ//+GRVIj/ydAWVsjLcf6Rbr6/1NoZIrqwhKpuLRSLpsIlgIiN7zZCrmspEJaWYbB4oUzWpdXI6la/x+FaVQJVEpo'
        b'KSWKgjcKmlgyEVh0BN9vQJUiriqWyenu/zuAeto7SXhszp62RY/1XW2NTP7LAUY5QywrkVbWki6/prkJrcWVK39lxcRyyYvHmGshtlx4qqqqX+Gw0UmfsOP4uX6dNf/b'
        b'eJeKsRXFQpfAw1oGt5yLBkpWr2QmmKg90UUY+MLV4qdINbYgjIIqNCCTiat+q6scG/hfQeLoOKTFxIt9xuJmKSSlYsnEFnN0WmwjJ7DV4yfGbX5rjPK14+3ubEJt1F0m'
        b'l2FNVYadGFI9UcdaKSYA1nnFE8+bP1otlghzpaJfW/24uZ9Z98T2f5QRfuEDjOv8q/4A07cSTz1xx4yU5NxfZ7vCGmlleaWEsNSzOiRvtG4lzZBYgHmzpOLq0rpflfWn'
        b'R/4nGJpp/t9UJhXF2NpMqPJmi1eiASzWE+iE/8DCiBjQckb03Lh1zcM1vy1skuJq8RNtN+oX80JycfGEfKqQ1tJ+0TM9FoildWJJKRHLDXXiktUT9ZaJa4sTnnas8QBP'
        b'efUT9FgqkSxP4M2XrJbU1EmeeN2lT+8DiktLcUFdpbyCOOmVUuKliqWVJbzK0t/y8BPwprS4mqhNvKZ5Fb94z298x4TRfU4C3hdMZBnGtx4XpmYLng1Tm8e8VxRhSgLQ'
        b'jPGmoCj7tcWlTIjX64Uk5KY2kpNUlP2TiQwowskT8BszU+Fu2LvZFO6KQy3wCmwiR71nYTN98MuKRBfgBZCIznOhOhx2KkiQ/UITqIK9LIA6IsFUMHURE12pqTABVuCj'
        b'Sg6vqKrLMRwwcVbPmaMD0VEAj3KGCeVa7q7g4QrHPLhfALejS/xM1CTIzRYxxwYCE+Drw3UPD+JbK/xI/76qWLR7BUjPyc4QQnKogZtlCU2AzyIO6kYX8YpIQJoCV91E'
        b'u8MzSaPwzJysZHh97LAyEjWbCMrgKQV54D8JtcKWp44y4X68JuYo0xwepyPA0qaiAyQCDO6CNx5HgZEIsAw8BjmBEa9D3VnZuavgiadDvS7CRrSfPi7FUJ2GR9Bu5ryZ'
        b'ZQo1wAxdZ+ElalCPgrwi4wIvwJtZUFWAp8nA8OTCZrQ3PB01s4HPJA5SFcALdLQhbOesyHrShgQdNpJgv4CwBQJuIjlaD8atouLh3nGt6Li83BwKakwBHw5wYSc8BHtp'
        b'RFFIlZD19Kwk9i6HAgFQi04XcZNQF9IqfAiNMzF9RKgZjyfKzEGNYXwT4JFkjw5xMNj1c2lMCR3hNtImzQ63yshBu0gjFydOBDoQSw/iNgW1CFzAhCQugrcVQsKAbfBo'
        b'jYx+PWtuCDlBIvGEC8lxDf49H+1cno+aOWCh0BTun59A89TUYng5OoqDG57EKMKMj/rD6PXAFnR53lPELZw+StrVsJGJyDgaAPujo7hQhY7QkXYV6Go6HX6yDNXnk1gI'
        b'NFBOQiHQnkSaXdBJeB2eprmh2XccM8C98AAT8XVqfgjmBnglaBw3zKrjs+gogUXodlC02zLYU2sCqGwAL063o6FA3anTomEPSIAn6JDF1fBkKnPGf33llMfMUwn7Rpkn'
        b'Cu7hmzBxB5d8i6K90M7oWjagsgC8YM9EvaNji5ZGw1NQE420XEDNxcIDT80aC/a4jO5Ewz50JVqKe+UBeGmanMZJORb47dEOaHc06sG9FgB41cuRnicPXkXq6GjKJxcv'
        b'6jhYHYS6GZluhUfXRUdz0fFV+OYEqEKtm2gN4J/lDMKAsQbwijxXLKoFNGZRT1aAjMLgdYI0kAYb4D66bailHeABDduktqhqxI8D+GwmYGnAGu54EsIAL9cAJoRhWQ2D'
        b'nBNpsVkiIdyx9HEMBIl/gP1iGs4yMdxNnqdx52Le4HAoeBQdgjswJeiwJLUVuhAdhi4+RpwX3MNEe51ej45Ew52w4wnqZuA6IoO58GhVlsDhVyQV3vIZHR3Ww7OoMxrd'
        b'mfsYw9QcuiZwDToaDU/juR9jOD6UVoJV1vYTije8GoHlu2b0HRi40xxTAR1FzzN0QKdKFUE0o8CrZhMK/iRqVO63jEa5WUrRaUwxMepjKFZiRmvXHHQgdUJtsAa2YWUA'
        b'lb4MaIcxaI3R0QTe/XTcbYVlFg1Acp13VoYwV4RFP2Ts3Ndj/UbYwIEn0Q3ExMXCm/BqIQkZ5QszOP5IA8xNWXAPvIxO0pygt7IBniBJbBlRVBW2royxG6iBS9GEFAkZ'
        b'Onqja4xy3WOGTj3FID1YihkO2QL7aRaKRDvhYUGmEOu8a1nC0FzyZrdtOVuMWqbQaEMXUDtW4OOilzHWSJisRwLans2B+9D2eJr2NZKyLJnrRHHOJMg5FB2hdSrqC0G3'
        b'mZhhuCf8ifoRoksgtIQLz8kwFeijbJX90rFg7zx4DDCx3q3VNCpRM9pTOT4kGj4HrwE6KBodqWaiKS/CAxWjMbo1WHkwQbqu8JoilAxxeZPlY9Rgc7Q3HO2CavhcNokF'
        b'yCJ4iIIHTTLQlbX0cjaZ+ZNoIHgn90lA0BG0n00TbVmxNQkgXoX6n4ohtoWHscEefa/pZOi80chkeB41Azoyee1oXGfdVLEgRJgPbz+JTrcNQudonboGNsJ+OoI+iTsa'
        b'Q/84gL5mLh27HoeOLrZkAWvi0hSYoj1YxIjfYTUf3caqxAddJKokAe2lWSUa9qdYSk2SoJrEWGIfYzHaxWie/agTG6s2CqzwI29R+iyk+S26wBzYgfpik6KiqqKohWCU'
        b'NLAVm+c2dNDUHfXj+72gkDycZxTuodh82BvB9iUR3xpQMxt1MYzdgXYiFWqztUFX0H5TwJkL6znUPHg7TTEXV+ejerR9XAwakZG9uai5ACkz0OGpuCocNeYjZV5BOhOK'
        b'Nicf9kQUzE0PmzNmAGnrB89b2+WhK1x6Vle0h4VV4BZ0YJwKRM0MeMISS+AIQiwt7IqqnKtXgHmYXkQ1xk3DTDpmokw2osZCVuhUS9pusjAYl/CQ6Dy8Nl6tdsjoKUUr'
        b'0NmnZG4bf1TkAlfRZh62xsADtLOwj/cLTwBq0DV6We6p1sAVaGdy84uqjgVYAbrjElgve8bJKMbiSLyM2T6KhbgNH10tlY3DDkYN+TwAvAzbRMIQzGCho2HpBQS/yrAF'
        b'6eTlDDr8fc4zmLyz0R4run2mdBB6rT8Xe8TrUrhJRVWxCV7MotBNqOHS/Flu+0v+pOCFMXV/He7Ohr1Qmx1DDPscbE1WhzNm5mol2g97U1NiainalFxEzSX0i/0p+e7Y'
        b'28Gkb0UHsHP9dGjlRS7sWTlXvnzOSngllsK4NllcnMcMdxKrXtjrWvx4uHnwOYZn96JTWCH0xsPGx2vAWuQUnzP6glcAOh8Nd8C+uDXYIGWShVxDF2jREIYsio4xgW2o'
        b'm/agxGnldPEGa3QoOpQVsxbPlATgGUsePZInuoQ92t5NFjFIC2gD1oOU8DSfYuZpQMexG92L9mbGROLqWdibgc0SRQotVksEWALQbkyR3eFobwHSWsPLMZH5j/l9rnDB'
        b'M+yO9ehRC1TvgTprljOSvM0abofnTEAk3AE2gU3eGxgEbMuBXfAc3rXsjYOXWYDlDNBZdLOA7pM6FxPyHBe4oaNgC9gSCM9hypEtU3ayC/m2wQZH8qL01KLR+PUr/pg0'
        b'F7gU1lCoA+BBz7iMxlyifrz4XiweVO044ZiRSZubwpVRT0RDggZGRQMjbA+zyO2ow5m8EHDVmpKi3VjYrlExOegWrbvcKouZWE90KxLQsZ4z7OkXdRRTcCKH590sc3NQ'
        b's3DBKM+jxoXpmfPT5zFohGfy01yRMkcoys3O42IvBmkt4POwfVNlSfd7LFkdVldfWSsvuOTUeKTJy9Y+eOfLoT0OL11oC2r+IsO38tt0fuGHJwL7Nr2xyzL9D2fymtX7'
        b'5v+pZZbeyjTAZtasRSlm5t8OW15/NHeNqPa4qeSR7Qj7G/Nl674fuFr34s2AC6sEr0f/Y+M7h75+5y8NcO/5+Z9e7n6d+ult789un/ks4nf1/D13WFuFw69I5l9bFNz7'
        b'4yEpZ/UfMk8rPklSt7umc6e/vzfrb/X+B2y1r7Tm7u3dsVfi8G2V3ffvvXIgt+3a61dWTWsNMHUe0oXVfVJke2FR41txrm8tbM0Tz1twPcqyw2OH7d/3ma7+6OeMl32n'
        b'Rn8+Z6pl+b4vPwkQ7Nu7xuJjlsfPn0XU3nx+S+nUtSdC1/cq1wqGMzbOKFnyw64Te6/ff+m8XD/1jvcR46ofdrdvSl3csF1etzi/TZLpaHHjnXN+j9x2KT73CvI7vLX1'
        b'+Xuf5fXlD3kZDzdp7/ivtbhccSN2b3kY+/slTX47XacP3ZO/O3Ma+37BNukyC8UffBckBe754+adJct3S9du+qgg9vOPLV94zepyr/1XBS8c0a2c7DLnamuUzxzP411N'
        b'IQdbe3Sn5etqv3YwiS16V7aoKfEv2vbPfD8XOnxtcW/+9tUcH/+PHBLTRtZsz7MLm9TF68+tfW64cnt5Sj+C4YlvXtny4Ssz8w7MWvGoq7vrv750Om+VN+z67ZJB2eUZ'
        b'a0Uf35O6+oScW3ai/ubvVD/UX+2Wur68LOzrvC8/UHqek78ufW9Vqi0nfvL6eV9sCRH82O8z8khUsP6F723XDp7y/1G1oPDOUQt/tXZJ6XvUlQ8VbuvK8jf22C3eaHah'
        b'znnflXcW550rfa7Q9Zb1wrOaZWf/cPz3Hoq/3bMQ+w1wDw0JR4qEx6v+/vDv4n0D9b2zZlxON/0yKHbbuYI55Y1fDra/9nHH4V7k8e5Kp+kev/vap7I4bW7Y9sLI0DdT'
        b't7728ZLtR/cMmc83L1GkHGhaUdAY9tXGL2Qv33KrjO7h5C6ZYbZxTtjC11f/KPEOLFTOKTTIuOEKYfulB9+/dezwHxqufiFdlffp0vWBfYP9eeWbY8U2ldd3PFj5X180'
        b'fGiMlb310cqd4UV1mS/9NOn0wKEA9qUT7c72sRlrVJ+sb/wh5VpxakjOK+su5A8MrptsfXixMbNTUpxdmXvL/u1hqxzVlqbVfafOx5W1/s3vxfrJof03Us9N+utwTsf+'
        b'rxStP3jnL3hJ8vO2f+zcO/KHtmXWNW5/1G7rup762jXFa2WB+7/wmnn6o/jqhbvam6aWzP+0z6Wb/Y/3+a8nvlK34If9u+IufrTBdv3Sk+9UdmkXfOKVn9vcp8/Zfqf1'
        b'jRkWwUoPORz2zvzLXj+9IEB6OG36pz95Xf5HTnGpc33B14eiNsls8l/69NgR4dUfO0I3Zue+LK0qG74449v335ifM3nBwTf/JvN/VRCm+Vzb4/yGrLjsQ+c/904vu/bN'
        b'N927Vhx+sT3qh62XBFrW6fd+XMTdoLVfsPz7hPdnKG/9mBif8426rfLdF5YL12707PdcWXHgvX8cMe5+PbvcJ1r6hxtBH32qqtzaUFcWceXD1p9HbsevCOz4KvznrSU+'
        b'D7fyz3/cdktQcsDY8Ps/f2v7hzV6TpA/3/YR/fSmAw7ISawpdq+OMqGho49vXOBVTjpUb2IiQA/BnmpBKBP+iep9gPliFt4/KOEuJmh1ANubK0/iP9HFeTEsG3Qc7aUD'
        b'RG1jbZ6Es2bCfXRE6x2kocM/S83hhbGAVnQFtgI6ojUaNtDho5NE8BqJtq0l3Z8KuL2I525/RL/v2Y5Ooc7xka14n3gM0LGtaM8aOiZ3KjriJBBloJ4kJiz3cVAuf/Ej'
        b'en/ZnxgnyM0Jy8TrN4EX8SKus+pyN9ErxLb1OGrDjuCucCEB7jLaUccSoct1NOycTQ5ZeO2oc/bjcW0j2OXowBQa9uAqdPSJU4ftZi/26gpgFxM5e6LE8UlMbQu8QcfV'
        b'9q9kcL6tDnbjXZLn0nFf80AHo5jA2plxqBeTisL+D7xQO/b1nEQOew06zff7H42L/e8FDxE+fPZBOO+pcKL6X36opFo+JSZiw9M3dPxskgUTP1tkBhxdD87YN0PvEGBw'
        b'CFCmGp1clLOMjq7KNKOHlzLb6OalzDQ6uyhnG109R0AS23ou9ZD51cIxOni1JKhK1Wl6h1CDQ+gIoOxFRo9gVaKGo/cQGjyELalGF4+DG/dtbN3cvhm3d/dVJ3cIWkxx'
        b'KWnsZXT0fBy5F62dp3dIMDgkPATrWfZzKWNQ6OlVx1dpHbTF+qB4Q1B8a15LcotCJR528VRz9m1u2Wz04I0Alluk0VOk8xRpFNoVhvBUvWeawTNN55lm9PQ7mtOZownU'
        b'e0YY6IDD4bB4Y3iMkS80hoQZgwV4AmNYhFEYaRRFkVQQbgwVGcNEIx42vu4jACcq7og3CAlVWXVYGb38RoCccsqljN4iHb7CZ9130Yfn673nGLzn6FznGN281QGdXiov'
        b'ozBKxVWt1ruG4utJqYe3OlCVqEo0psx+SQAF90v0KXMNKXP1njNUaepQvacQr3+xPnwGvobDY3AZX+8Zhi8yglDnFo4vEgPKVVV02HbY4lKdX6bOjVzDQZHq1drAflY/'
        b'u5/dF9ovvps8UHHf/0aNPijXEJRL4g+LtSxN6XlLY4BITcIa52jXaAvOb9AHJBgCEkZMOQRcDg2uBfD0VefqPKLwZYyZgpch0ntG4ovE5Up0XjH4MsYm4PJwvWcUvp7E'
        b'68ZNVaXp/HBZNL6eFD9u/O0oLjq8RljOPHejJ18TM8LGuWHPAPUq9Sqtk3ZNv71W1ueuD0o0BCWOcHHdiAnw8lenjpiSvBnwClSXjpiTvAXwCtZwRixJ3gZ4heKxbEne'
        b'DngJNKkj9iQ/CXiFaBxHHEjeEXgJNaUjTiTvzIzjQvKuTBs3kndnxvQgeU/gFaSWj3iRvDezBh+S5wEvkUY+4kvyfkwbf5IPYPKBJB8EAoONwXxjaNiIgNyDsUTFGRER'
        b'BNt3xTPhtYyUjACuW5BREKtJoIMWi/tn9q26G3vf/n7UfccXpurjcvWCPIMgjwmHNgYEqdJUacOCcK3Z+eljZYGqNGNYpDbwfHb/zMGwGSqOaoneNYSO+tZkGoIn64Kn'
        b'9SfrglPu2uu9Z6rYGK2+QWqxZqa60sCL0GbpeDNUXKNPgLqga8MDn8hBn0i9T7TBJ5qIV+iwX6CGOhasmkmiz0vUperSbkvc2ttHxSYTzOxa9cA7YtA7Qu8dZfCOwnLt'
        b'ForhIDDMHIybrYubbRwbYIQN8Bz/9w5jEaxp/f59mXcpfUiKISSlw1plouYa+TEaD+2C/vl6/kwDfyYGdFGHjVEUrU3WFmtnnl+FC5brXQXDcVPHwj8fxGUMxmXcD9DH'
        b'5Rni8h6yKbcYlSOWT7dQzUyjJ0/nG0nY2NVLJTG4Ch+4xgy6xmBN5JpgcE3QuSbgzFMyHKhxHPQQ6jyEGFcPfMIHfcK1pnqfeINP/AiY5LWIGuaLLnmc9dAW6PlTDPwp'
        b'ahOjf5A6Wr322NTuqVrfQf9onX+0MTRBF5qAoU7EuiR/IV5Q4iISaCtYTAJtcYqrAnFqAkSRmgKtcz/V53ZmxfkVxohYbY0hYtbdDYaIuUbRFM3q/qC79gP8u/P0okyD'
        b'KBPL8WSso3Ci5qqr9LzoEat/cgS9KNUgwjLGiSf940n/aj0vRseLwUNg3gmKw0uKz6GMeQvwauMX0mHBi+iw4EV0WPAislos8SKDZ6TWz+AZq60yeM584Jk56Jl5P1bv'
        b'OcfgOUdHXwSXIp1bBL6GPb2PZnRm6IKS7mIVnW7wTFdRw4Eh6gKN/SWXsy5a+zPu592PFXYXGkP4l0zPmmqpMxbnLYy0svO9FtwT3O97OZRWd4obEn1QjiEo51lVltY5'
        b'XTWdvB+RphYy70cMR03GN1izhus8w2k1Ok3nRq5hV0+yuhCdWyi+8N0wregxfBEJxmkpd2frErMx+BE5BHyfXAI+Tgn35lLDvkEtma2Zw27eI0BAbBe2elv3bVXL9C4C'
        b'g4sAi5GTr9bxmlePV79CH5lmiEyji+47vu71ipdu4RJ9xlJDxlK67D1XHkamk+8Dx+BBR6yO9I5Cg6NQ5yh8E9tKJzfVUp1TCL6MjkE6xyC1QrPCEJyod5xmcJymc5xm'
        b'dGQ+OhaodwwxOIboHEMwh7ekGf0DW7KNvoH0Gj14am+DRwSJ6J/7q8ZstJF2ksEjhhhxX/W8QRe+3oVP3lqZ0TlDE633CDd4hI8AR7d4beq1zJ7MftnlvL68u8WDMbN1'
        b'MbONASF0DL3sWF533oOAqYMBU/tT7/rrA2YZAmY9CMgeDMi+X6APmGMImINVV2Coer4mUlMy9jZIv68+MNEQmIitsBeTqKkRDsc3mzJGTcbsHNKfdtf3bvG9wIFsTaA6'
        b'VZ36zdvBkRh9uMHTqTF0skaoi0/HlzFkxt1gfUgGpuCULEI7nBKhy6aFLpsWOpyySbdvvvkG25rIOG1xP6Ut6bNgRCXwLnWXdZf1WFy4bD4WF5youbh1QIgm7vh09XTj'
        b'9JnqVB0/QR8wVRcw1RjI1yw4vkK9AltHdarG7VjeNw+9CEg80sHa4E8ky2uKMS5ezVEvxzJLXhvx0tG8afAM18boPSczd3r6MrphhT7oJtC5CcgbIMsMrqEPXCMHXSO1'
        b'AXrXyQbXyTrXyTgzPDFVh8n351jWgUY7P52dnzpW423wj9fbTTHYTdHZTTHaOR+03metEuvtAgx2ATq7gGEHN/K9ukzK6Bykw1dwut45w+CcobPLwFXKHDqW3ejrsCiW'
        b'Y4z1W+xiygTK2w1xSLTA/2OA/IR+L3mOXjSRlytNBE++e0d7t6+S9sfBaMR8gQlFTSKh7//K5F8WRU8+H3TUPBZcsUlms8eFQ4yFzX9BHqwdBGLy0WiwhFVKLWGXsgqA'
        b'+Q4+e8iOjsSgo9SlaVJpjfQ7HyY2g8aGdDToXFzKK5bwxKRelMvnDJkVFpJglsLCIYvCQuarzjhvVVi4RlFcNVpjWlhYWlNSWEjTk3kFgkb2DILsZ6b9C16sjDyVr3/8'
        b'b9gqUjd20f2Zs6UmuBv2WNqga3JLc7wLzRVKXdCt0e1YODpqwjUP41OzKt8HjZRsJx710Zdem1tfzkJJrr8rj8ronLd69acf3jac/Oz725fmP/zw5RMjSuVwsmXmvd2O'
        b'UY2z7cNXfHryp9Ytl/8Yl2b9l8kv/37jP74v+zBwlWzp5ecvDHVeuNMT/Eaphcxvz5y/NO3/SDhjeCH0qHn91XP5S+4cXHR47rz24O7s7/bn/yxdv6Tip+uZuUFfRyPj'
        b'nf1fDsyy+sutGv/X7xhinV5dP/m9Ls2H9x6VJ0p7L+5cvazulNvXCdl/7XMv1/3j/OvXXco/2fOquum+JlCXH7HM6aUo3nMHtuffk1/J2hm04+gUv4qgWfqUJt/cbF5G'
        b'9rH9xp1rV5omNC7/KOgr9UFjQ8xlH/YLyVb20a5Be4ra43eueZ8T1FigetGqLLJhfViRfdaiFy0WXHZcu1NRVfSF8IfXlnOXGl+0WXv561M3UqRn0pPfnjzn5z/MbVvz'
        b'6gvTP02uW/JRgHvXjjcq+D6mPy3PqrnTHJV6MeLbeZ9/HBX0QZT4+Raha9pg+9lrf/t+Y9EK6YH3tHdr2984F7y8+/vQxneXi0ynij/8XbDIbcOthvf4HHrfvxa2oIvk'
        b'SXcD3EVhfwCQmAXYRO+wl4rNLbME8Br9fdqnv06LOuE++ulJRAC8YxlKXk5tRE2P2/jAXritjIMuoV3rHpHzivnwEOqWwQvpuRRsEj4+hrVHLWyo9Vo79hKr2W8m/+aX'
        b'WJPon/pnfphtN5avqpri0sLCDY9z9IabfFTgG+YH66UwYO00wjE1dzHaTlLKWqIa65rqVL67Nik3qWQqmTpKXdzNvK81h7xapg3A/6T9vn2K/jl96y6L+kR3U++m3p90'
        b'L/2F9MGobF1U9tuu7qooVXFXbId5l7k6U+8q0rroXeN1ibl6l1zd3Hm6+QsMcxcOuizUuSx825mnntQqaZdgFY89clfsvVmASY4tye1OyhRlyjcjppR5BmWc5NMiPGml'
        b'E87S82YbeLP1k9INk9J1Vum0dTQxDxkBv5nYccyJN/lbiZUZz8JoZdviPMImOTdPVRmTC+Jr4phcdFy/CZNLmnl3AZ0bpntwSY7uQefoHnSO7kHn6B4kh/0pazvcx5TJ'
        b'u3vhXqP54FDcbzQfMxn3HM0nU6kU7k3fmTG9zZk83Xs0HxbVb3J3gdHeRVWmiZsoO2JLGoKxRGfmiTeck1xxHXONWJr44Sqc6My8R+xmscyxQ/AvSvM5wMLOaG6ndGmR'
        b'qWJbVuvM/fTmfgaMd9Y8jjl2k/9d6UM2sPDH85Dfdk3OIxy6SmKG70ZYlDnZ8D2THF7/kPx6RJKxfuPb0s7GruQZKQ4AOrinCNmMs+E4xMJ26l/nakwo9o4TuB9PXJAM'
        b'YhUfCzsxhLIbY/4Hn6LsiM/wH0n+pX5Jt3kCuGGTbMau5Lz3NVu2HRex5lVVN0+z2Z7kmnpnhlLnu99dP3X989ZO8gPGjk+0ty6f7HlvX4qZ3aRTnRnvvLrJ4vUVAxu+'
        b'31cy2+mW5tieyuC8pd/X8L7bK33eYmjV6Y172poDnwv84v2HcwTnTtxNvPXSvbt2qcpWXtpOf2lIbvwHLOQ0+a1Xf//m93bd+00D/+qTtc5rrsGTb0pbCXQbnlhG/2WE'
        b'PLTDhw4IMQWWsIeFNFCFOmiT5MkNysoTosukUZ6QhU3IABuejoDH0C10jR6lAPXC09gj2Yv2ksgP2Ixzd+BuU2Azie29gEcbPaRCAw5ZGVANzz31nQgN89T5clpwFvmb'
        b'C+YVo39zwZLPQi2ZsJN+jl4E++AR+m8yFG14+m8ywDNpj0gAyNalZoJMLliDuqksPE9+Et//143b//ij5wnlwn/MHD5rDCc0jJWSSjljGJkcbRj/DEYNIxYXd8B1qM8l'
        b'/4zWjg+svQetvQ+v01uHGKxD6mcZORYN2duzdfa+J+P1nDADJ0zHCTNyfHTjLyPHuj6D/BsxyTflYuXxP5SW2gArx/q8p94g5g2xq8SSIQ55fXSIK1fUVomHOCROGm+Y'
        b'KktwSl4BHGLL5NIh7sr1crFsiEPeIhliV0rkQ1z6q95DXGmxpBz3rpTUKuRD7JIK6RC7Rlo6ZFJWWSUX45vq4toh9obK2iFusayksnKIXSFeh5vg4S0qZZUSmZy8NzZk'
        b'UqtYWVVZMmRaXFIirpXLhqzoCaOYOPUha2ZDVSmriY+LiByylFVUlskL6U3EkLVCUlJRXIk3FoXidSVD5oWFMrzRqMXbBhOFRCETlz7RxjIekYPf/OHxGCU6dywhukcW'
        b'Qz12ln7lBzOLLUVJ2UTx/e9P/2WamxjJe1bmyX7gnp9NcgT7O7OxP+owZFdYOJoftVTfuZeN/1s/PEmNnEfqxKW5fDMp+fQY2QoWV1VhE0sTKJkUWWAekspl5E2CIZOq'
        b'mpLiKsw+cxUSeWW1mN4QSqVjLP9k7/idWSKz2ZwuJX9Og+xvZZtxMsKmKGqExaE42CfEiRWwtK43HeEUmlKOI+CpNNUWmNs/MPMYNPNQZerNgg1mwSOARcXqwqbfDbob'
        b'dC/khRBdWCa+jGZ2RgtnZZjOJVpvEWOwiNFxYozATgfsWlz1wN0A3HVjF728/wMtkwFm'
    ))))
