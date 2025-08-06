
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
        b'eJzVvAdcVFfaMH7vNMrQe2foDMPQmyhIlV4s2JU6FIUBp4BixcYAIiCWAUXHPhZ0EAt2PCfJmrqMmDiwKZq22bTFxGwSk91859wLiMbs9+7/9/7f7/v4Jdcz5zzPOc95'
        b'+rn3ufcTYsofc/zf71egyz6ihFhMlBGLyRJyK7GYIWKuMCB+91fCOEPSLYlBCZNBiNhnxkdqCanBEgbq4ZSwJmA2k+i3nmgShyTWsA3K+JynIsO5C9JmzeNVVZfIK0W8'
        b'6lKerFzEy10jK68W82ZViGWi4nJeTWHxysIyUYCh4bzyCukEbImotEIskvJK5eJiWUW1WMqTVSNQiVTEG59TJJUiNGmAYbHzFMpd0P9cvNkhdGkkGslGRiOzkdXIbuQ0'
        b'6jXqNxo0GjZyG40ajRtNGk0bzRrNGy0aLRutGq0bbRptG+0a7RsdGh0bnRqd9xEKJ4WtwkKhr9BT2CmMFSyFqcJQYakwUhgorBWEgqkwU1gp2AoThb3CRsFVOCg4CoaC'
        b'VDgqnBXmpS6IvfrrXRhEk9ME69a7GhAMYp3LxG/Udp1ok8QGlw2ucwmPl/TWEauZi4g60qCcz8guniomc/S/Jd4si5LsGoKvl12pj9ogkUmwaj5hEERB5r+y9Am5F+7c'
        b'By6KYQtsysmcDRWwNYcPW9PycoUcArbCGz7JLHh7SSyflGN2gl7YDw9J07LgTriDhOey0JUwTGMADVAvKCan0GAxQcMmdNlj3ojoQKwhELvYiCF6iH0GiG1cxDZjxCpT'
        b'xDRzxFTLUguKQUhzmiZ1az2DYhA5hUGMKawgNzDGGfRC7ySDtv7vGZRJM2hYrkcYEYSZasOKzEMuBgTVGbecQWBAFUtSOWrsTnf+VqxPmBFEUFy63N/PhkN31luzCfQv'
        b'L7dMWvmOhRtxiqg0RN2X4+1ZTyyIuDHLLuINxuXgeNMjZCU2rwM+XaRGjzAbTCsIeT8kOeU4QXXbsL833W1Kpi5b9JD8l10oZxkxSsiDMPsb4B7QimTVEjjb1xc2B6YK'
        b'YTM4Nc83PQu2+QekCdOzSAKcsRObGsRANWh7TiKsiU0XYYkwKYlgaRClzEmeM//beP47pdT7Hc+5NM/3zTQhnAgialNogVFnspiQB6BOeB7eykUb3SHIgDtgU+bs1DT/'
        b'tDwiJGOuNdg9D7SAPUQZO2GDHjwEz4NuORZoGjsyFFxBswevA6eIVVWL5Hg5Q05CKLiIeoGSA3qIlZ7gpNwaL9BpDA+HhmCmNoPjYC9RDC5WUxjOsFsAO9lgL0BbCyAC'
        b'wPE6is7XZxkSVgSxsMilINOUsZiWePhsS8ITdZ4xLpjxQXgJUfHB9cWkdDUamfnL3v1vzOhpaDrc2de5JtyDaXcsqHR/aJDV4z1xP8eZn8j+3C+Cw1E2e6u+/PgHq88r'
        b'bTnbDV9z95613Wqv4WtFZm8vfjMXEvO484ZfPQD2vvrWJnJTtP0c3fG4sLWGHsrSzEftRamNf/noVSOZqSWIuWN0QEiYRNt++20In/GEstT2OcVcxDt+llzohzSFQViv'
        b'E4JGlj64CNue2GEOnJDBW4jFzbAN7kB+YRpZUAD6VtnyWaMMX77EGIE8u0ix1HibNm16ajOjVFJdLxLzSmlHHSCtqyiVxY4aUl44v6RQJqqf0mZg5Bp0+WkT8TiJJMws'
        b'28Nb6pWzmze+b8MbcoseyNO6JQzbJA6ZJepsHJUlHZX3bAQq2T2bULVMkaKzclSKOnIUyTor232pHalKkSpBNVtZobZWr9KYqx00eQPBA7M1i4ec44at4hXJI5Y8lfWw'
        b'pc+Qkc/3WOkkWOv4nFF2bWGlXDSql58vkYvz80e5+fnFlaJCsbwG9bywUw66FPDwXiUmuNMUG/aUHXlgoDB0+XkT8Y9EkiQtH5nYtqzcxB1jsEmrEa5Fy7RHLNOtWTp9'
        b'0xF9y58eswm22cSvp1KsNLs47sQRrpBZzHiZeZZg82TgGEUZKDlpoIznnCLT4DnzQ23mFFNkbGCOG+gLvX/sFCcJmDRQTrbcDKvSVZf5sBO5EqHPWkK4jEFZCdhCgu2w'
        b'EyURgfCkPREIDhN0/yF+EbIeZDnwOGwgApLAxYpPvjdkSaMw2z4ewDZxuJPf0kEyjwWdCOot3ay5roy2b1k4171aOb3r9OAM7+3ZqnPv5i5DOm1P5G43OPXTAz75xB6h'
        b'e7qzBelCqCiIScvMZhNc0MeAPeAKuMpnvihEnNxMSHCUSwuvtLK6UFY/9QelnP60co7NIwlrh31ZHVkqD5V02EqAtMnUSmeHFLCL284esXRQhnfGDhm5ScyeKZYEO55R'
        b'domoqEImwSFPYvkSZaK0iVYmW6xMU0kQTGjTU6RNc5E2Ofyn2tTJ8SCOcgOYlD/a42BBhjGI1QvmDFYplyXUyvGC4Bg4Bw9KZRFBLBncRDCKkO0HgG4aocCKjEII3REI'
        b'waTFR26DXcM5MTiO4Ul4giQYIgKegjvLKHiz5bbkDAYRVCQfrNJN8/OUW2H4Zg5QYHim7yyCUUbAM2lRFHR/kj0ZxyDi7hgOrlcuvOYgpxzPVXg8VyqLDGLBnWArwRAT'
        b'8DRywpcojANFjmQSg0itSUQYnPnLKWcNjibCDozBWOJIMKrR/CvATQr8SoYTmcog9G95D67XmS6bR4Ez1hpI4cXwIJIPLxEMsIWA/c4WFPg9VxcyE+02pHJwvZ1fgS21'
        b'2xlwqwsFzxZaIvCtBLwIzkgo+Nv1bmQu2m2DJYJfby2muXPFDp6QStD8UInUHtNzVhJAwTev8CDnIfi3liHqzXZVUeQsr/eB/fLgIFbGUjT9HkQN3D+dAh+J9SIXMojy'
        b'lVGI+nwfASWtMhTddlEIDDsHhLAX0QOPcykEp3ofcinizq9yhJDYbUPT0w9vRkuloUEscIlNMDYi8UVCDQX/GZ9PFiD4DNNB6ULH5hyK/6AX7AL7qBWYs8vRCt0EHIiG'
        b'SgqDGS4gSxiEb67hHamd+V1biqSaMHCcgteDm+AxhLEfCbE6jEK4ECsky/GWcwaldsIDDhRJ6xKqYL/UyJABznsTDHiJDIMK0EfBG3kHkpUMgnczAy2Q6FhIq8RmoAQn'
        b'uBKkofAC1glwArG5fgmFwUgJImsYRG5mINqEB1dArcACl4GSC/vC0a6716I1dpBMrjMF/7FRKIlMO/Uf7nekyrg3oikhhIATcCvXMCSIdLJB0HtJgwiUN+CZasF+Py68'
        b'jORj7oJGtpEkOA+PU0OWYDNQSWF/nQkDbo1Eg4dJgWMYzfTj8Iip1MAYakjYX4CGbpMRBZ4Ut0zBVg53lRxeJuBBlHIwYB/pBTrdKDQneMRNypXISNgIkepAJekCdtjR'
        b'PLgW7C6VwStcEqjhDjTWSgrgQXiNIn8avAGOSE2MEUfPrSCYbDIGJzLY2axGSngIjZiQXHOCaYDMrZ4msBdsAbvQwCoWUOSg6QbIgMpFlLmmiMEBrnEN2MGaDs8RTA8y'
        b'btkiinIe0MBzWLPZQAUPEYwaNEsU7KMoME4HDcjEwziBpQSjFHkEpEK7qREfZC9bsf6xNxbS5nbBmi3HDhv0uIL9UtgH+00ZYNdMRMQ5pAkdsJsaXQB3zZDCy3gQtoAL'
        b'aPQ0GQr6YT/flJJjJCuMXM0goj4oQXIvkhlQnbuLIsh1yG8vLkXCtV1RTHWuTY0iNyE384vVoFRXtsqe6lxfMJ3ciiATbO9IdSsW0OiPnGNIBepckYcgbb6xojpPG88k'
        b'dzCIgp+W35EuXGs+jer0sYgn25GefhmMVvf1WU51xosTyd0Mwuz7aLS65AY9Z150EqlEdIbWIgsw+cCP6twomUUeQHN216LVU1Piqc5Q51RSxSDsljIHV9qZFa2gOvWS'
        b's0g1Wqg2BXVK5+dRnR2J2eRZZFWzE++sVAbXp1GdvNhcUoMWOsEfXKnM2JRKdR6xn0teRD5kjsedlTo3EW1/oAncBtukXEMTrMwqgmlExi1aQElrJWw25UpMjBnwZADB'
        b'NCdjwA1wnBqJsZqGXMmVOikzPYJSaAHUpFCqmbUCdiEzQE6SBI21aGw36Y58dgOfRZEQUvcn8gCTCLq4+k6dnf37nlTnjJTXSRWTiOpkD1bb6S2i/ddqjzfIYyg2/4V5'
        b'p3ohI4aOWR45b5FqJlHzIGmwWpnYN+e5U4vBRFYixsHKYPwcic8tz86QRKnB5AmG8992gil9MUEyI15MkGZmy90w45CZ9oOWHHQoboNNaVkBQA36YBPKuW0KWD5GsJna'
        b'ZosTdYwsIdHhe7u9FX1+cCzAx8jBCEZBQWWuqStBGcYceN4oIzADRcdWcDonDZ0p4VbGmhnIFThg2R6B3Sjp6QcX8bmGXITAuglwFvQEUjYc7LBG4Fjgi5J+RSBKkozK'
        b'mKZQAw7IcXaSBhqQ8+9nEYbVRDQRLQRtEkwERUljJD67KoOM4gr8M/nJdGdYFD4P3w0y5RX4u8XU0yleMAOcDAeXQqkT6S6iEGoy5Z64vRXugzszqANFG75BkAHaAtNA'
        b'ry9J8GQWYAfbpCiIDudnYW/uTHA7FOc9YDdRBHugmuIk3A5OhwjQyRbuyELnvhawDWoC01iEJZ8Jd4Dt4ARFwBp0aulnetKnN3RygwfpnBRegEdLFlWFggv4vHeIqExN'
        b'p/wdsoYuDjgALoeG4l8HiTJhHsUPFze4yQQcDQ1FaRqK5CvMDah55sLdixfC3aERGFpJlGTAy/Tdj+P5oDMjHROWDXdiwcB20GNSw4yC3TEUppl4BYpfB0MjMAFdhCgE'
        b'NFAyQ+pxzTkjLTYT4QXCVgFJcBcjZxgDNvMZtLc+gs72t+FeuCU0ArknJNFSsD2Czqivgk2LE3JCIzCR+3F6wKPD+E6DObAlA56D2xC32ATLhQRHTOFhisX1UBkCToOT'
        b'oRHImMABohxlcI0UKUlQLRUsBhosGNiUDXpZhFEM03QxcuaYV2UoBPTBLk4ouIzXUBGVpRWUUhrDzcg7tGTCvSHp+LzIhLdIsB9qlspzMP0a2BouzUxLA0dhYxa+jzR5'
        b'cvcN4PtlBfCFDENwXISi8AlwzNcXnLIR8MFueExgBXbbWMNjtuAkAx3FrcyAygfsqfzpt99+y7Bg4bspM8m4gkyxkxFBM2oXOOYoyIY9y4WpLIIVR4LTNrCXb0XpPjwE'
        b'r4NmqTHsiZfImchPHSQ9KsFWiiOhRoiofhPQXEIPXSb59nxqJBzsEcJ+45kr6IFbpABsraVGNoL2aKkJCvVnJXKScnuuRTYUm7w5etJVcPNauSHqB9dJngRuoqVyVs8I'
        b'BTXE++Y6eJFNJSZu8FgARfya3OUomXAAh+FFY5JKDELYCI+6H3FmLdzPNVkDrnFBG4NgLiaXJNZTI/OEcLdUVhJjWMdCS90knVDqcJDmhQJutUIpw3Zw3LAOL9VA8uZY'
        b'UUMkvFoG+2UJbAm8iDYFbpGO+aCFYhKbhD1SeEHGIUhwEAXx2wRsc4dnaMu8AHaDW1x9M3jc2BAlg5FkauAaOju5hDK42ygJrM1bZYRp7yZ94DZwgUY7l5jBNYEqhhFy'
        b'18zpJNaCHnrk8Ep4GkX4kDKJCdqVCRnpDa9QI5FF0agfoPzigjEacSfjwTUfSuGTVxUi3t6SUuuAy6RLUAKF4ZEL+6SGYS60mHaRPJQoN9CraMDWFK5hYQgeYlqQQdjP'
        b'0aZ/FRyE52EnB6W4RYQ/4T8LdlHqDC/kIe/aYmq4qpYkWPBcgSeJfp8AuykSio3mcE2Y4ODEfjLBEWq6xIVGSIdWiCdVaAa8SjHVFnYjig2RC2x6Rt7OdIq62DyczxvH'
        b'CJ7pV4sjNSI0ABelJr5w66R6FcJmPotieAA4BtVIhLC1/pkM4flptDR6kTu7MSlF27VIhvASuCl3RIPmKFfsBS3wCorXcuQXwLUEeJYEDaaIVkfKZ89BiWlLHbxsBJqQ'
        b'DUFFPTIU0LUEHuUzs7Mpyphs2IYk2jJrUhtXgzOUZvnFgstY52DrpM6VgsMUd9Z6C6Qyfbj9maZus+Wb0JbZCo+CM1xD0BpvAC8gIUWTKVFw+7j2wLP6UhMh2EEzaC/p'
        b'tngNJQabXBtkzPunTxqzbC0t1YOBXK4+PG9DyduQDIBXbKmp1i5dAfuN4AUDGuMc6SMDzbStHGR5IO0FhyuNJHjoOOkDdlpRq6ysi5CaLPSDl2VYCIdIzxKCZnJXPTiH'
        b'bNkFHOQiPWDAC2QESnt7qA2J5+pxJcgoetH/l1iUWAPi4LlxK9pQzdUHW8HJCSNaBtTUSDLyCy1ceMnb1GAVh2D6kNNmgPMUfWmwNxUNwC1ohCSYvmQ0bEL0Usf3nfC6'
        b'uRS01sJ9NehQQe2Lrx9M0bgMtlnjHLoZDtSYctBQE+kN9iLj80ODJSK4BelBJ2irhbuRdjeD3ghwCmxLh3tQpO6EexeQhMdylnUVh4qGsKl4BuzUQ/rhRgQRQQZQQ7l2'
        b'B6Baj4D3wX1AMXUeNMlu1NuO5r+A/t2NjPAK3IOOZXtQ3z7QaIAMfx9UgzPlKxjYDlUGoAscY1O7TUcx6xCi2xn0T7LW1I5i0aKMFK6Eg6Z4xtdAlIpRkkpAMQwxaXH+'
        b'BPfcMyl9iIItJOrP4E/wDpzPkiejgRWwA2zjwtYMlEocQAEvNSsgDUcnAWzNShfOgYqcub4BWek4rLWm8eenwpbAOSiUXZQuIKTWBNiebRa7iL4rDE9E5YL+ObkMgrQs'
        b'TifWw63FFNNAG3Iw2+YyUCpgifJJj9WrqV3k56GTcr9sodsz241dSjmedU7wynPGmTgf2SY4kEyr6dmQ+YgvEaB9Upz+oANtn8oieuaC2xkBQr90tCNwjkXEgTOm85mV'
        b'hAdl12uQV7iNg25r4CwUYnCWoQ+VDLCnZgG1sj3Sk0MZzCVwZ6p/eo6QQ3AzkFEFwn30yj3gTKzUBHQVTlphCfKVzlQY3GEkSM/KEKJ1wRZ4IAPllRbgIBOlCu1OFcrL'
        b'6SypP0rqrbclt+Zl5FjFm33bdXD9W7e2L1uoWyY3HyPPHfmJSB5SPvzk4Qfcpcc+eW2kxLTFTRFjW935VkPLI97y1Bnmv21vug1+K/iV3LCs/4PrA0cLO//We+70+eXL'
        b'3v3n6zElhVVbnMd6/76DnRlS+K69b8bsrzIXg/lrC7kf5s4pM57+w/mBW6/O2uDzz996NqfarxcJe9XMM7+8r/rZd3FJ9tOItdaf7Oe+p0qdVfm24uwhh0vuwir2moWb'
        b'5866fPHXzM3neuXbzvzq+wrnL0/ZrH1j/pKH01QSz8/umf/8zoyPMzJ2phr67VJzxKsUS9y/dRpYXmb5vpW6L5uZ93qDn+V58vSR1TdPv6Hw+9j7lT/J19m0LGeExn5a'
        b'tvnXG4wr0a/0eH67suZkbfFXl0IX/UYk9XxtVWmz07REM8Tbbx72jvGa6Jz3E//263nLomVpPWbruWc2bJi3YGn7Oxsc7CxbL945rP+uQ82yo8sXzT1ytezvsxvjTt7V'
        b'RXx0wqRpw8GrB287/2O+KLK35uOidgv/1JVh1wqcD4aGfGJr6X5QWxuh/VODpU6hnSW78de0lBO5P894t7zbfcdfBw3uzc44UXe2XJt6z7vlrVP+LtPn1XkZfK99U/P5'
        b'NtHN838qS1gdfObide6sK4wPFgl/uLn17l9ln04/rtlVLt355Z3RvT8HPLq+4++Gt85UnXn7lV/7FtvuLP45/Ozlcu3p4Adt6ery77b+Y+VZj8dvHo2+tnFzZdRnbT6f'
        b'rkoszfl6g/c/GpyrWpK7jotfb97fwJ0Xfqd/ehx7Whf8oKwqJvzk3S03Mr3yjHvaDhjNybq71V+59oRvC/imUjXzdsL3Nm/f3fVpWqTJEf/m9zeY2K9Y+Thr+BXhn5I7'
        b'36nyM/BZ2qooO/KL0a29dx98unHd1ZPr5UviPviwNbhpg0XQZxtHIq0fzuu40zP767O8c94DxR/vlMUu+fjcwsyv2Vsa3rkZyL/5S/k/Y2b+/UtOsV8bf1u5ZQfn+GCn'
        b'S+mbzqpyofGPl5+UW8T0OX0kO/HXfb8sftzz3ubXmu9tuul1tP/Ie5frG1Yc++Hu7PWr8g/F/ZruXpw8fEb04V69lIjcM4+vW/cyfmg/+xddzOEZD55esDVZ/skXjfDD'
        b'0B/fdv2BY/f2odN84yfYoivqgmALy9o/GyXKsM0fHQvAGeTeQbsd9RBnEezxFwSk+fvxA2AbuAWu+cMmgrDjsZbbgRb6Ic5eeQJ+hrN29uRTHNBnC9XU7PA8Ch1dggCU'
        b'JzahuTlg5xwThhBchVeo4QjQDRoy/H1T61B+0pqBvAVafA3YAo5SU4MDyHn3ZaRl+WXpERwWOn3dYuhHwWtPeHjqW6A5UpDq74dmRoGqFwWDHbCNSVhOZ8L9NqDhCXbL'
        b'PHBgbUaOEEXVWngGtKAM72gSNXUoOA23CAL4sNmfQGSdhZuXMEK9wK4nONx5wl2zYEuWfxrciQbDwH4LhgnYx3/iSh2T4GHQkwGV4CR+OJiRho8YiGslDLgfNOrRdG9B'
        b'JyeBH9q1iZjat8F0BjhUVUdxFJ0QDkZlIN+IAoAwPbbYHx3iLOAAE+XUzfP59i88RvifvUixk+a98Ldp4o9+lGFBPzqQSQrF0kK6AqL+JX3Ug40xFvVg40kSg7D3amfp'
        b'bB2VmVpbPmpZ2Smdhqy8dW5eqsLDtmpzdbDKqZ3VvrDDBAOldmx4YCvU2grv2wY+9PJrT1LadWTrvHHDvjNHZ22v9O1Y/sA6QGsdoJbetw596OKuCu4qUxWqipQrEZB5'
        b'R8ok9BiHcHI5FNkVqQrbH9OepHNwUa7q8mlP1Dm6HoruilYV75+pDlaHDDkGtCf9xc1LydbxvFRFqlUqA7qJ5qSajjxVUneMLjRKmaRyuecUpHN2V5V0L9MFhaMOx3tO'
        b'Qp2Lh0rWXaVhD1hdMNZ58tXzjmRpRAOyC1U6J57KvivngVOI1ilEE/6u07QJ5MAwhOxwz8l/oiMgFHXYd+fg35Va5xCMatOV+cApUOsUqGG/6xQxDvkoIFjjdWbFM2iM'
        b'LQhCv226M9HvQ8u6lh3If+gXiHqsuzPGTAhnj0OZXZljBOkXT+oSUx8zSb808glBOqeTDz191F6HMzReWs9IZbLO1UOV1r1Rx/NULTpsqmEM80I1ci1vxn1e6EO67wEv'
        b'QsuL0Mjf5cWMpZGEu/dYJknw3JEA53cYjTHYDhbtnDEjwsOn3ZTa+4EcxHhf//Mmp0w00mHf6Vorr/ZkZaiKPWLr0CVXW2u8T7nirbOU87uMVHlaO4HOL7DLdNTeV2fn'
        b'RPXlD9uFD1hp7WLu24WPGRPO/mhDSIcMOmYOeUdrLaMf+scNWg1W3HHV+s9GcrfpyFTZ3rPiY1Xhd+QP+cZqrWORxFWcrhkPHAVaR4F61n3HUF1g8mDJ3Wl3qrWB88cX'
        b'n6+18x/TJ1zclbN0zm6TFw9l6guXUaeYUawF9LBqnjJ78p8JtMfOphQneISj8yGfLh+Vp2rN4cBhh5AHDlFah6hhh+h2PZ2l9b6ojqghpwCN3nuWUToXN1VKV1V7is4l'
        b'BV2cXQ8t7lqs1tPYDjtPa5/1viC4y1TJVspVhTpPv5Pph9PVco1MUzrsGaM0GPEVqNPOmCiNdY6+6uB7jv46V081p3vjQ1/hee4priZxwPmuuXZa+rBvhoqt8xWqi9US'
        b'taEmbyCkb9GD8GRtePJg8d3g4fAsrW/WYbbOzVvtfcT1JcjU2JBftNYtGo8anTLSzB0Q3nXTRmcM+2YeZk+iDPtGIQm7uqvC99erl91zjR71jhhNTr+b+OfU11OH8ha/'
        b'nTPGJKOWkd8TpM9yEimm23Ly4XNa8KkgTLPoPcHMrgxlvHL1qKuPblrMQOlVp0GRdlrm3dnaaTkqlmr+YSP1QqSOOg+BuvaeR7guNHKA0zdjkKMNTVElqW2OZOq8hIiB'
        b'XlG6sKgBm77MQVttWNpQaDo9iLTJP45E6uTkpprVPfOhf7DGTROvTh/xC0fWGz+QoKkY9ot7zGYGumBj25+DtcNDVXogf9z0h52E3yWThH/I4xQmcnNTHs4ajRpNdYkv'
        b'ezz7X3HKRsREOcAUPyzxRZeXOd5EjDKNoIoDfkxkkKQDsvH//JmukuNLqLmhTD5J5+YasI2fkeafxoJ9FgQLHfn358A9z90nx7RSN6dr0WWP8fh9clxrRfy+2qrUePJ+'
        b'Oeu/s8rqhypEhuHU8JWLOSTlFT5fnUeV/K2pEfGy5k0LC+JVS6hGSMBzqM/9SJPxJCKZXCLGc1VWSGV4iqJC8UpeYXFxtVws40llhTJRlUgsk/LqyiuKy3mFEhHCqZGI'
        b'pKhTVPLcdIVSnlwqL6zklVRQciuUVIikAbz4Smk1r7Cykjc3OTeeV1ohqiyRUvOIViMhF6NZMEzlc1NRlSU0VHG1uFYkQVC4KFEuriiuLhEhuiQV4jLpv9lb/DMq1vDK'
        b'EWm4GrK0urKyug5h4gnkxWjroug/nkKIeFgikuRLRKUiiUhcLIoeX5fnGy8vRbSXSaXjY/X8FzB/j4PkUVCQXS0WFRTwfBNE9fKyP0TGIsDbfLZeAuqpFFXI6gvLK1+E'
        b'HpfVM+CMarGsWiyvqhJJXoRFvUUiydR9SDEhLwcuKqwsRDvIr64RiaMpdiIEcWkhYry0sLKk+nn4cWKqaFqSRMUVVUgV0E4xo14GWiyXYA6teUbNAnisXCIXvxQaFwlF'
        b'U1c0p7y4HIFJ0S951R9RXVxZLRVNkJ0sLvl/gOSi6uqVopJxmp/Tl/nIHmQiMbUHXpmoCM0m+797L+Jq2X9hK7XVkjLkXyQr/y/djVRelV8sEZVUyKQv28tcbDe8FLlM'
        b'WlwuqShF2+IF0l6XVy2uXPM/uqdxJ1AhpqwUOwre+NZE4pdtiyqv+je7ShBVFkplFPr/G5uamjFET4azqbFo0t/VVEtlL04wrhkiabGkogaj/JHnxrIWVRT9AcU4cskK'
        b'J5RrAYpcaKnKyj/QsPFFn6nj82v9sWr+x3yXiFAURUYXzUNeBkHOgTeKVxbRC7wMHvsitPn8laIpopogCLGgEt6QSkWV/w5VhgL8HzBxfB4M8XJifxdxM+TiEpH45RFz'
        b'fFkUI18Sq59fGMH8uznKap+PuylY2vBYqUyKPFUpSmLw8MsQayRIAMjnFb583dzxYZFYmC0J+CPqn1v7d3S/PP6PK8ILOcBzyH+YD9C4FWjplyOmJcRn/7Ha5VdLKsoq'
        b'xFilfu9DcsbHiiiFRAbMmyURVZXU/aGtT535v6DQNPh/6EzKC1G0eanLSxEVwRvIrF/iE/4HCMNmQNkZ9nPP0TUPjfx7YxMXVomeebvxvJjnm426X6qnckkNlRf9DmO+'
        b'SFInEpdgs6yvExWvfBm2VFRTGD01sUYTTMnqX4KxRCxeFs3LE68UV9eJn2XdJVPPAYUlJaijrkJWjpP0CgnOUkWSimJeRcm/y/Cj0UGxsAq7TUTTvPIX3lV6HjF6/JwT'
        b'jc4FL4sMz0M/V6BkSrxYoDSPfsUiNo9+g8UsfFXmIcZGurYnJYdFv6xSsi4zPU2PkOPiGHgb3IR7QQvoB80RsB1cAjvww77T+OnjbtDKCIa9oLcWDBAz4Fk2UIEDQEM/'
        b'8jwPzyPg/lC4j0EQ04np8Bi8Ri1jwKRfqRlbUVI5Nz2QoMG7QS9QgNNw82QRT0iuHN9YFsHzSQJ+OtwhyM4MgE34rrKAQ7i5wr3wINvBezXfmK41Ogw0sbAlNSszTQhw'
        b'wRGCzBByCNeFoAMeYsFjJUBFAzbPjIMtGUAZmI4hA8cfY+FHWMGwlSOAfeC0HN9aBp3gip1gyrAFOAg64QUm0ICDsId6wgYvwDNrpxQAgc1SNoHrfzId6fFzdUCZ8VyR'
        b'T7QLPAdagZou3eqBxy1gC775HFaULmQQ+vAqAzR7wWa5O0Y/IAJtePo0tJls0ArbAlNhK5NwtShns6BSAs5SYLWgJ3YKVA7cyYV7YBOu9vIUsGfA9mlyH4qpCfD61NlO'
        b'ROTQtVnZWSTBBzfYoNsWdlJcsoY7q59bGLbAa6AhMA1Behaw44Aa3KTWdgd99oIA2IqWDUjPgk3+fA7hCC7BdrifBY4CBbwld0JgIaUe41BpWbBZHzZgOFtrVhALHJbj'
        b'FyhAAzwNzr1M0OAoVLEd5sI9clyYD1oSE6TUCyxzfMNi8fMGXFe2AD/RQP/m5cJWFrFAqAf2+MJ99PPYW3oJC4EyNARXYO0jSmKDqEeY8GANaHxBujWwCQv3chatkm2w'
        b'Jxtt/FhoCJsqtCrfCG/T1QadSLc1sBNeApf0CPxofH0AXUOy08B6ija4ldLKQPJpZWiEV2Hn89pgYQ/PzQJ9fAb18D4WsbU5FFyo4RBkJjgEmglwDqnhabogaB9sSFgC'
        b'bqJxgipaWzkdnKAn7oZnoZJWI9AseaZHSZV8Dl2P3zXdKzS0hkmQGaA7jgC9dpCuazFbAW6EhkINmyDnrNlAgItmDvRie51iQ0MlCCEHXhFia94Mz1G3ntbCQ9YI4wLC'
        b'mA+7QRMBLnPgADUZnwl73OxDQ3GF2RFiJeiG3fRk++Fef9iUGRqKGXmUqIQnYAPlC77k2xJIqmaDGyrWjRIrCeq9LagA1+E1aUIumieZSI4spEAlG8wJ5A+iVNUbjTI3'
        b'SNBitBx74OkC+hl3COyb8owbOYEblI2tyF/27BE5YuoRFoGfka+A/RRr9KeX4BtpbILFAvs5JDiUBA4hceAhT9grGOeaAKgR15LgVbqmaxO8Dg5O8C0FXEeMA1tgB63J'
        b'x2B73UuNti4KGS3ycsfQ/JgvifAWOcHkXXAf4jLYsYwu170Nr0ZPcBkZUSficnodXRHZtxY0PG/tZOIzY1/FoURhl18FjoPtz2QxYEO921kCtiVNQQbXc3/nAoLTKLtZ'
        b'vHI1GAAnJ2WWMpOyd5sAcPoFxwBurJr0C/BUNoWdsl4Mz1eFhtJ1l+UC0EM5c6jOT8hIE2YHwGZ/X9rGmYSjM7gBGlng+AZvqrzFctpSXCrIh30SYRqLMNBj4KeWdMH0'
        b'a8updwPtHs6qzbTzYNDBg4FL/yeE6BeCZAgPr6Yt46w+m1YOcDlxinLMR8qMDTYxLEqQLswQ+mXDHWAbPE4SpmVMETgSTDlBuLuw/PnqVcQnXB/p6GKTyQK7kBdopUTO'
        b'3wBv/0GZK1r8CNtkPkExL9oN7KL9A9iJAg/DfNL7+BWzwRlH5AupZ7htYPs8qt43EV6fLPc1DKBrTjfNLphSEEsXwxoZMuGOMLiXQl/HgYdhS+ZEUWYNvEyC/aBvnRzf'
        b'o4b9yfBqRqQRxRTEEdCE9BM2Z+KnxRn45d0QsI+Ttj6SMp2qafBCxtTqEKQxB+DBOfA6RQobGdw2wfN1o/AA2GoKD0AVsk9Kk89uRA68JWO8IpW7hARHsrMpOucXQY1g'
        b'al1y4hJTZAfXqOgLDwsQG6aWUO8STVZQ8yIoR5EUhYsj++FxlGHMJebG+iO7wrf7eUBhLbXyot0HsgPKmBcih9AUB1q5Eg6a/RSKhnZSSlXrLBbBTtC6Gr/PRggRsTto'
        b'TTOl3+flEVX+S0r16EJsbKFoh6fhNVwApYeDBJEPd4G9tJ/bDtqACh6JAf1BTDSmJqrNV9JvNoAd7rDT1AQ2g5PwEtyjhxSVnBcJN8vnotEl4NRyXJM0WY+ETaMtG7bO'
        b'hYo01B8Im3JxZVIqXZY0OxcF1lPgQtDcOan+s5+LfOCssVkO3A5PUqualOU883zwwFLa8YEL9LtGs4up11f1VeUbjLI3rifmjUvMwm0uknngcsR3bDCcfIYf2OZOpytX'
        b'Zy6dMqNiNT3jEuRKcZDXB9dBE21uTLB7irmhJJHW3W1g25wpeUBl1UQaADrWUETNlxgTSDd8C4zkRqNm5gStC5dXg5bfJRlhM6kUw8tDPh/B+M6DDdJJ/iDegNPmcxBv'
        b'8IvRAUJfpGN+aXQZ8lzMXYX//FSsWpT2zv4dG2+vNQetAthBlR3X1dAvcQcZbKg0Ml5M0G74IOhAVjVFQTPgqUkFhfuF4yEdybsX9ID+MBzTZ8MmcBvFEWuUuGGdJGEv'
        b'iYdIFEUWwQYU7QU+cpz/mouQD+sESPodKM/djWLGKesppXbn2OBC0RxZEbgUTiJ+cxaJaymvXy4jJqbjw0Y0XUY8TcQWuAk0TRABNoMORMRG2Mpn0dlBY3BMaMQqFIfS'
        b'wX54BOGV+tEKvRM0m0LFqtAwDpU8ieAppOoYxQT2RYeG1aKV4vRCCaSNp1BGTM11KRvTADVod/NlIQS4MJMx/tBqHbwZjIaC0cgssAfuRDkMuGYqn0WdMtDxoB/ZAEoz'
        b'dyKZwba5UGMM+sKCcyeVfo5w/u/03QtcRr70kCHKgNRgN2X8NfBMBTiTWY4oXkesC11BhZR1oBH2gzMRoI9BMGzc0XEFnob7STpBbIU968CZOOSfiA3EBiEV/rF7WewN'
        b'1bBTHwywqde+F66kpvJFQugvBmeReHrZOLMiwBl4VR/hYJPTS3CeYiBXoIa2EL+NVDjyFa6gzSMILTolVelEXMUcMp+BXxypg5epYvAr2eAgGRavRw0ZwN3wqhReHq8C'
        b'9FxMesPmauptDfkMvIub4KgVNzsLtgrnj6s9bFqQmp6XOo/mJDiFfEiWMCA7M4cNe/2wYmoMUczbBPsrUjWNbOlsFKsb1r9/fP7b1UuSzT764K+tH/V/8orrKqfpafuj'
        b'sh3Ll5Uv89025qxaN9fNze3SyZ0Wj1JjZxy931y77eHmHes0Wze15KSqGxUbN3F/M6jLrvn4ra9Xf/TUfOYD/cqK2rra2trPr3z/+Nab/xx8urLqnRMbymp/Lf1GUcHJ'
        b'lDqxd7rU9Hx53llz+MbGbcFC9lcPdn99/mDT46ahlOzk10PP5GV4/eXDrx1rZrI/vv/WnPTan1UjH614s2LNWO7Jm8VfbMtXvSfbPM/wwP2YG3mBX1z8R56Dzc4fhy47'
        b'Njc6ln/EftVtWfj8hYJpc886Z341d4a3227TyqcbXxl0/ew1feOb74S/en3RjaNGDek9AZnf/tR81Nn+gkfvuou86zm3ZG/czff8l+gu/7et2xzfyHkSYPu3az47qjQX'
        b'cyJASIVFz8y06otPnX/4POfIXwz3/uIoabl7syVCfCTFqyB8u0fk6sHmPo8Es6si33ft0o8k81RLpR8OfnnXo0Tw7fbwtfDPd3ujxW9LNiZ9W//WL8Zv/uby8/7tM60e'
        b'tdcG6Hpiv116zNllw3f2W4QFH0l0l9+rUeecjf+XyTcRim8tbiY9CdH6a2OO5Jit3/WFhVZ0ZIFiudeoZ/3bQx6l/xq7f/eXpq+I6nOOx0ZH/vZjU1H02ShHr8Ilkb4H'
        b'X/s4i60pvrF11zuykIHRc69dlffEe4Y8cc9xZNWU7ftw9O63DhvaGjeHtsd8GP5J1JYLn+9+4z27pTML680XjKy5XHv8jdeyy7LCyi8uLfY8/f77wxs82ZFfVH3lV3bp'
        b'n2e+d3Od9+eKh1vqJU+mT3sU4pRy89j65k+9Ln3xccQmzmHRclVe6FcZtR+E/OuSdHj00Yk3hW1hubVfig58M+J/tLljodfmtD1232VbfvIP++8+6/guaHP1o69XPqmY'
        b'9ui9sqOdjx7fOPBgzRPpss+WcfamfT/w3vvR+Svbl+StaX/sV3ahw2zdO7kJQtMrTd+v2+p8I+i7XPHGjf6Fsouff7k6OKAw/EZJmMylQx6Yk5fQ4n0j4cm7XXefWpZM'
        b'z3c/d75w2bRXTGanxn0p3315+ReMkeXl+yw+TTo2/PNu/7/W263p8h+WRN+rMTvfw2GfbqvO9fTPFTkWX0iTJgzMjW+K1Pp8yP/4a2H3Z/r90/165zR+vE5P++GQ46/N'
        b'MZ+b1A4eU9T/JXke0+sNA4u/J1l8AIya6npMvi7fcns3+27qOkf7lqf3ebkWHyb+4vjbpduv3Q7J/eiH1D+9JX7aZgfe+Lr1evJPbxqVLPUuPNTxzRufeMY5uaoOJFz9'
        b'8pNPR78yuB656qNZdw7sCDhSZtswd7ntBx9899aGQGfNL8pH16yC8uZ5fWkWtfMrwc9ff7VH/dqIOPuHtyvqN3oGcRY8ZNpuIZeGr4osd/8xEb4aeM7m8f5XbveEVP+s'
        b'd+6K/loD165peXFOa4/43DVZ0xz+pOHHuNzze5muWtcHN/J27+/582Nlx5aeT/dl9f32Q8/2ZU1PPmx91fAX5TeaP0e6/8zhtrxfcLmn5M6n7ye+932syHRNzU+RucSh'
        b'uJ6HfFOqOrBqLXe86hA5b+S+wR4evjljCy6zUsERcOIJlax3WKMA6BfAhyoEgysBDRYx0CnmElBRdYDwsiga1wHCHsF4KSDDBJ4UUV8CmBcFbuMV9DEuXdrIEIJ20EbX'
        b'PR4DDZa4sBFeR/7uWWXj2eInTlRaArfrwZbniy7LwD54rmb6ExfqzkkWaHhW3Dhe2LhBwEQn2wOZ1BxBehnPCjO3zJysy8RvRFFViMFgd64gO8s/CexMx9Trg6uMumpw'
        b'jN6agp+F0rxmd9gdKEQ7q2OgExLspWaG5+EekwxENZ4azVuF8krCNIhZ5g82UcgLwVZwC6dsFusnM7ZquJkaq1kOdggC+Ab2E5WVjFDQC9oprpjV5VBfT3j27YQmG9gD'
        b'LsEBSmbgGrhoD/txUSXorRH6gW4U5KnvhsxgofQune/+f7Q48j8r2sGnr9/f7OZNKePZ9OLXIapk08KC6qf+oIooR/Tor0MU6BNWdvtmdswctvRUJOmsbRWzdFZ2imSd'
        b'o7MiU2fvrEjX2dgqUt63c2pnjVg6K0tUyfct/UYcfdSsYUdhe5LO1nHf2o61nevbWToHN1V8l6Bdb8TWUWflNFmDFqqZ965ltM7b7+SKwys0lprCYe+ojpz2+Ha5UvTQ'
        b'1knF2rV+xJE34hSglmuWawOT7jsl65zcD2V1Zam97jsFPfSP0gWG6fhCna+/zkeA5tH5B+mEwbqAEHwVBOr8AnT+AY8dTdwclOwxF8LXr9toxNl9xCVgKHDWXVttYO6w'
        b'y+whu9k6exeVZ7ezThiiZCtXDtv5TXQ4uqi8umboElL+JLgjuFs8nDBH6zRTmazy0zoJEU2LhgNnPgwMQx38YSd/jCTU2qNVA9E05ftNUceQe7rWPv2Rd7DGa4AxwNT4'
        b'DYgG46+W3/W4Wj3snY2r4go1DDV3xBNvcbZmlbp+2DP6sR6LItgQ14hlax1DdGHT0BoBw07BuPJSrHUO04VHo57AYaeQiVrMiOnK5CH3kGGnUKpn/7IpIHg3+53HGDY8'
        b'B50TXx02xkSth06eiOnWmlUD5hqHYe8ZY2zUOcYhnD1USWN6uK1POHupSsYMcNuQcEaCHePitgnh7IcmMcVtM8JZoE4aM8dtC8LZV201ZonbVoSzUF0yZo3bNvQ8trht'
        b'R8PY47YDPacjbjsRzt4q2ZgzbrvQNLjiNo9wDlDLxtxw252G8cBtT7rthdvehJePzoev8/P/ToB+K1ljAZhz5l1RdO3lfUfhiICurivUrBgMv2t+N2RwujYie1iQgwtY'
        b'uzJ1nt5dyQ8FgRr9U7ETPV7KZJ0/ktupzIFErf9MJUu5WGvnS1XdqtO1PpH3fGIG4u/5JAyaa10SlUzEOTdvlUidOMQL0mQM8WYq2TpXT9XcrvoHrsFa1+D7rqEP3b3U'
        b'5GEfZSKu8y1Wlai4CMbFVcnEkyZ2rXjgEqR1CbrvEoJITexbMZh4LyJFN4EzxiTQdJNQ7z6DGo5ImaiBTB7w6EsfJId9E7qMlRwVe4Qfppk/kDfMT0TkL+wy0QWEauI1'
        b'heoV6OcyrZ3gYcR0uuTwQUSaNiLtrudwRM5jJmkfprRSrtTa+6kTdU68IbdgLVIiO2elWGsnfGAXprUL08x7zy560kq81Fb3HIVouw9cA7WugRq9+65RD/kB5x1POWrm'
        b'DvOnqTgjHt6q2qPTNW73PEJH/KLHCHJGNqnLXYAWm7EQV2QKFuGKTK9F5GMOERCssRkg++zPLNcFhWuqtUGzBuu1QXNGAqYNeA+aX+UPzhsOSEdGEumuYqsqtbzQx0b/'
        b'W5zhgCSEEYUxqu7xwhCGTyRaMCqL1OXMR1RELaDqQhdSdaHoiuzAXRWgdQrWuGudwjWVWqfEB07pWqf0u+HvOlEOI0BrH/TQyeVQWlfakHfcoNewU6qSfOTlqzY/b3vK'
        b'VmN+xuFovs6Xf17vlJ6GPGM4gnyA2xWfPp8Bt37sBeRXxcPeWc+ZenJ3LK73TlYJ7yHnFhKJWv73nAIpNxKjtY95aOeEF/ZFgkHNRy4BiNagaF1MwmDK0IxMtImgLLwJ'
        b'12y8Cfts8qGb9670R/Yu2BNv7Niokt63FWisrjj3OQ/I7wcn37X6s/PrzkMLFt9PW/LIjoe2bO32wMpHa4WM8r6VcAQ5amt75RKtte+IlbdKrl6u9Zlx3ypGZ0V/M8jr'
        b'vpUv0o72ZJ2HV3umzs1rV/pDR57K5Z5j0O8dLB7QOgZpLLSOYTg0uKnm3bPl45r4mV0z1aH3HQM1SVfS+9IHpP05g4X3wlJ0nr5UvbH0aM4Dz+laz+kDSYMew56zHnhm'
        b'aj0z784d9pytTB7x8lMHnyrGhekDbu95zVCRYyyWWyapC4lEuuA7kDzoNlh4x+tqptoL+RNDIjhCUzhAagyxVngNkoOMAUov2Ew+0gvk7jx91RFHYnWxiaqkIX70Pc/p'
        b'Oi++ev7R5ci5qpLU9kdyvnMmvGOQT0KAxvc8InQRUSqWahnSQFx27jzsFKgJ0zpFvotlhtzEPXsBridfqrXze2AXrLUL1ni+Zxf56EXmjMVzCHvnx0kcwsx6xMxdFa52'
        b'0XpE3TebpjOz2WfcYawU3TfzfGRpP2LjPeSTOmyTNmSW9tDSXpH105NIwjfkO4KBtjziF6mNStX5zhz00fqmfc8kp2VQZpVJmRW6MjHUU6q4d9jaOC+S9W6k43wLPbpy'
        b'2GyUhR/V/n+sGH5pQoJvVRS8LP2Q4NP8c2nHmxg+lqBLiOdySNLiRwJdxvDlP60jPsDxJ85yI5nPPSaeKBv+Hu9vHyHCH/0kFjNKyMXMNQyDUj5z1Ix6Pk3V7kqSJZJq'
        b'yVNX+ok1RaZkvBRXVMIrFPNEeDwgm88a1c/Px4/48/NHDfPz6e91orZRfv4qeWHl+Ihefn5JdXF+PsVoulib4sJMzIXfLfspIlXKRkNbiY+Ngilw6rGGK37eyDWBV6aD'
        b'TTKuAcrUs4WS8c/cBcJDHDbsB/v45KwKbvbfmNIaNIvPQ52oIyUHxlltrfug6OSPjK029YH/+qBhKMO34dDg+hKDVcyMOM+Au7sefK4w27d02jbX1/ubmPqusX//dv+a'
        b'69N/2Ssf8Jh24WjU6aM3+21hgYV0+NyHn/n/NFjtsOOD8NsL3PLKe/M7tyzuWXFcw/nsCjgfZ1zWcG3FD6U7/vnVyUt5Rce+afshwtQqfuZHaxz7Px0y8HgyQ3r0oz8N'
        b'J887lvzebvN+ec6d4wqFmu8mdjxY/3Z73Hd7PLaFBW/xD26c0bfJvW9rSN9m8mPedkWekWVKULoTjOrbbvCx5wnFsNLtnaKdUW3sj933Kt5ceMfvPc3O6AhNE+eyptX5'
        b'6yLTX6K+OBY74PPILCVqlqWP86udbNtd7X97kha9cZb6SIFD1PHp5eKdITuuJkeK0w+VPepNc7Ve1cFb3+xkOC2sw5Y9O8Iy6soP4sCTY7+98muscPvet2sKKwp3Lvv5'
        b'/DuftJ19beA3sSjjm5POxj/+M+2f8beKfnw/6DZhPX3Vq+868VlP8B3FVaCB+mgECZujUHgh4E5DeIE6/Zn6zX7u84SwuYqwxt8nJHyeUA9jukFbMNcPv6mFTmATUGCn'
        b'HeEK+lnokNQHldQbXXkS2C0FvanZwoknTIJYwhy2M4HG0nbijS79f3v5//mNrjjqb9Pv/ujjB7KayurCkvz8+skWdfB4irT2X+jg4U8YW4+x9AxsR0wt2kNa6pRuzeu6'
        b'pKoQVeFh/GbH7O6NfZ4ayYBbn3xgdt/q/oA7SXctYOq9kMz37RyUIcrCrvD9Bqp0rV2AxlZrFzU0I1trmz00Z95Q3nztnAX3bBe8b8NTWXSKh8w8UU5lh2K9IWFh1R7f'
        b'Ya1I+AeLY+D7DzOWgfuYkT7PUGdk2m4zxsQteydlKd3y5qsj6FZoxACHbsUlDs6nWg8pDDZuURhUi8KgWhQG1aIwcAuFXWMzhKNHtx2cEdZ428cP4Y23wyIR5ng7nkwi'
        b'ETb1S5/GNqDbFPZ42z9kgDM4X2duqyxVR7ys+Z0pAhzSd0I5uYUd6qH/e8zluKNelx/NZjEMIp4Q+DqWyyIMzUYMzNqlyvD2lfcN3H9kzGMZOPxI4Ov3TMLQA1/Mxlj4'
        b'95hYH7WfMEiDkANrUAwyCKEGH+OOn8ZyTEiDNHLEwvWY0ZBw1jAvZdgidcgolY5MzfF2SYbEK4aWSc5MOjJZjTKQ7/zvi0svVVqrl8SqZ/EqDXvqSVXF96qlMePBik+S'
        b'ZjhWmf2AL/9prDrMCSb6uDOYFSisMKTrUE/KyRBRa4zhlji7pNszw0dP5e32/PD1xx4Cf5sjPaKvGdPFrhL9QPsSA9aBz7MeK9d8FLP28ZffJO50zrp4r3PW8bk2v1zq'
        b'8dgiji4tG379kKBj3dmvSqQWyk/mOhgZxW+2mma4W52buCp5i812R5cvtt8b+cqipPPgd4+4H/Y79nzhxdejbgXhT0Zcpz6OnAPbMsBhuCNDj+CCCwz8ed2VlANKAf1+'
        b'GTlC5JCacmSwLydHyMCf4GCCw0BpTkGUwwuwBbTg58kZnkXIm4FW0KZHmFgwXarqKT/paLksA5fcTLxsy9CHZ1fSN6uawM6sDPqDy4vhYeqDy1w+A7aD3gr6ftFtsCtg'
        b'/IvMcAu89eyTzHPcn1CPZDvLwGZBOhs/Z24nMwioBGfhPr7HH3vG/+P3b16qlh4TvvT3nvSlXrVCXCGjvSrdorxqCrr8uon43oFgW+qMrR4Yu2iNXQ6sHjb23TRLxzJs'
        b'zGzIHDJ3OxZ1n+X/Acv1LyzjHzm5euyQHwl8fUJdx0pMCCOrTTlTXjXjjTIrReJRFn6naZQtk9dUikZZuHgPJZIVxeiK30sZZUplklF20RqZSDrKwqXNo8wKsWyUTX0H'
        b'dJQtKRSXIewKcY1cNsosLpeMMqslJaOc0opKmQj9qCqsGWXWV9SMsgulxRUVo8xy0WoEgqY3rJBWiKUy/DLDKKdGXlRZUTyqV1hcLKqRSUeNqAVD6OLJUWM60ayQVkdF'
        b'BAWPcqXlFaWyfCqHGzWWi4vLCytQXpcvWl08apCfL0V5Xg3K2jhysVwqKnnmeKQ87CP+7R+PR/uLORMX/CU3Kf6gyG+//fZP5C1MSVLCxO7i+etj6vqfOA/sKu8YcOLt'
        b'iTv23HhP5lP9iU8Tj5rl54+3x/3VU4fS578vzxNXy3h4TFSSzdeXJGHlQUlqYWUlcrQU7fG4yxCxVyKT4srPUU5ldXFhJeLsHLlYVlElolJViWRCG55ltaP6M+g0OFaC'
        b'vwiN824pdp9jTJIkHzNYJGvMiOAab9L7jpWvR1qNJZkSBuYP9B21+o7K9Pv6PkP+sXe8oa/WP12nbzZiaDNkGzpsGDbEChshzNrt3iUcqKX+F/wJrhk='
    ))))
