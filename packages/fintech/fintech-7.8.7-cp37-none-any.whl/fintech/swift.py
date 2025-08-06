
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
        b'eJzVfAdYlFe68Pd9U4AZQERBLMBYYeg6iIgNGwJDUUHFCsMwwMgw4BSwYEUFBARFEUGsiIqiFAFBsJyziblpJptNYtj07E1MdM2/yW6KbpL/PecbFCz57z73v/e5V575'
        b'nDn17eWcd+YLpt8/AbxC4WWcDo8UZgWTxqxgU9gUbiezgtMIjgtTBCdYw7gUoUaUz2SIjX4rOY04RZTP7mA1Vhoun2WZFHEcY7NTbvVQI4lbFhEWL8vMSjHrNLKsVJkp'
        b'XSNbuMGUnqWXhWn1Jo06XZatUmeo0jR+Ekl8utbYNzZFk6rVa4yyVLNebdJm6Y0yUxYMNRg1MsuaGqMRphn9JGpXC+gyeLnBS0rAT4VHAVPAFnAFggJhgahAXGBVYF1g'
        b'UyApkBbYFtgV2BcMKnAoGFzgWDCkYGiBU4FzwbACl4LhBSMKRhaMKnBNdaNIW292K2Tymc3uG8V5bvlMHJPnns+wzBa3Le4JQB6KqCBG3Uc9Fl6D4TWEgCCkFIxj5NYx'
        b'Omt4HziTY4SBIhiTFDVmhpExj4NGV3wc5+NiXBmMi2KjFuFCXBorx6URSxb6ihmP+UJ8fdI8OWseCUNzUB0+Z4yIxntxSTQuYRlJBKfSoybUs17N9mOfYx8AMYQGLFDh'
        b'/0GDVEcLrmyhAHDlAFeW4spRXNktnAXX9KdxHf0MrqE8rt4hYsaWCdgkkiXZKieOY2jjD2IgAHPFk2OSfD5xdecb/7jAmnEA4nBJST4/zJjEN9ZkCBlr5q4TG5oU9coU'
        b'Z+Yco5NAc7XAJSRQcnc8w3zm8R3XPvFr1zWMzgY6mucettnLJQ1iQpMmfWh4VV/DN3/m//3WZldPd27hp+yvLqfNrUwvY/aDDnRI4wREL/Zf5OmJ9/iH++I96Fw8rkTb'
        b'PSOjcZmPX4RvZDTL6AfZzMD7Rg6grlUfygGEuoSyTKrgMf3Y36XfM7Ji9Qz9pDz9/pRkP2cFF8wwAUm6B0vW8VBvEKFLAHWJtxKX4KKoReERPhFLmEnKeeh6nBM6EI+K'
        b'0UEmTWSFj6ECdMjsBFOC3dAOBeqA5dE5xhHtWocr0DXzULIYgy8p0GXSU8ugYvcMfMaNduATWwMVkwiRKhl0DFepPVGPmQi1sxTV4AoRw/gxUo3fPHyNQuq7VeLwGuvJ'
        b'MA5Juu9XS3n+lVg5JsxmwuFd0vQg5XpGm7agQmhUwef3ey7fS7qbtDY1SvV6qt9+T1W46pskR3V6qi75vu6NpEjVm6nyxREq+UKlqlFzlm0YknY3JVK1ktmvDldlafYL'
        b'95xuOhMwZ3mJfJRsacj3c16OqbcPK++8aXtEy8RHOn366RtyzkQMAj6ESldJgVDyaLOveqYXcJljnFCB0Bq1c6YRMGI96sbbgJx7cBkuEfjhakY4lUXNQXinnO3lPOVy'
        b'gYFwpd+Dg8dD5+mphqyNGr0slTdgfsZcbappZq+EWqfEFJVJQ8YZbQmPx9iytqwDa816sgZx3xJyQa8oR6Uza3qtEhMNZn1iYq80MVGt06j05uzExGf2lbMGIicGEXmQ'
        b'VcaS9e3J+p84cGKWY8X0aR5F8C5ShXmH+3ih0g0xqDQWJETEOOPtwuHu+GCYmrPInvA5ggym4rEgc9QQCECQOSrIAirI3BbB8wxB34IDBVkcYyYNVrhnAa5g8TlcCLLC'
        b'+K5GVWZnAmc+voyKcYUAdaImhvFn/FEtaqcCOA3YUgeCtgh3EVnzw6dxqfbG5JOckSiB73fu95JW3ChHVehy+bmKc1865zeHj9nVmR9xhH0llUiWbeqnOpY51GAd+qcP'
        b'5ayJUAX14MKtg9EV70hfXBgRFSNipKiZw7W4CFdYePI8ZlOS90p5zqbqslQmyloi4YyXLSsExhokj9kqpGzqFaVokrUmAxlkIEZIzvVjJWcg3qkfP8l078f8fH8AP2XQ'
        b'MjUDNXvPRZ3AUsJPkNeiWB+WGZkpRPtQLd5lHgaDZibiStyCTxpNQQFChktmcD35SPtQE96dsAgVkz6W4TQMsOI8LqWUHr8Z7/RE3aRLwHBpDD4f7ELNBriheivpHKNp'
        b'CllPz+AGVDKU9mQI8AVctpL0cAyXBVNQhSfl6GjUJMxAp4z48mSyEcpncOu0hRQGL3zMRuZIe0TQs5PBl/E5VMkLQiO+OAc1oE6jgc6DJS/4b6IOD11GRegwKsT7cKt5'
        b'IoEE7BtuBY+3h8ISioq9FAtoH8AC5gpfnjqHIhYVAATZCyGCgszayuCLKRyFJD0GNdrgajoHUEbVDL6CeqbQvmB8KmAK2k37rKCvhsGdKD+KLjhn7SjrKNxqtJXATriN'
        b'DZyHmszDCfgHUQGuAii3SQ2U+KiewR34hANP/HZc4AJupVaKmyeTXnDbgvCFPOKH01DV8mSpZBJBG1eyNrgNrLYLmVYPi17ADQFS3E7xxrtYFlcvofOicGcOqhxhxK25'
        b'9gSYE6x3AjpLCZKciVpSYo02driJLHmdDVKjLtqTYzvX7CBdZ8btDHQ0s+PBV+ziwShCNaFaXGKUGkxkUhXrtg5d4aGvR8fQubihRhPukJK+UtYbXYmlBBmEdmd4ao32'
        b'dkAQgYidgQ/ivXSn1cNE+Bpqhh57lhHYsKG4GbfQndDFxTbLcQH0rCMoXWH9QBSr6U54G9qPd+PLMVK7bFQiZARj2dBF+AzPZXwF74xFhUQ+QHqyQWLsFlj43zbXBZWA'
        b'+AaKGS4VJHs0us4j1ROBClXJhP8iXhRb8IkcOsl6Xl5auBGAah1EqHeRDcStqylKsxxXOgFZ2y09DaxCsUYuo/6sQuTIBnKhWuuFNzJdJnnm0EZ2shMbzFWtFwbcyLwT'
        b'dNpIGx24Yex07lOdffaNzITp2+bRxi8GDWdDuXRfCXNjc8KY9HG00T1tJDuPO662CoXGwG+daONbm0ax4dwrG1jZjc13ktePoY1zI9zYKC7dzi7pxuYq/38LoY1/SZOx'
        b'C7njYyUOMFJ5bwttDHcfw8Zz1pxwITTGnVXRxukrx7EJ3E9z2QCy5s+JtLFJ6MGu4mTTxdnQ6BgzkzbWR8nZJC57hB1zw3gnM3YlbWyx9wKncHyrkLlpdPHP1dLGNF8f'
        b'Np27G2MTesOYsOVzfvqeMH9Wx2XnWofeNFYFXg7kI0H3iWw294q9RAYjh03k4XwpQsGauKSZNjKyZvw62qhaG8iu54KXSJJuGKtGVW2kjc5bgtg87pWNtkmw5tBoJW2c'
        b'5TeV3ca95StwADjXnDfw9BRMY3dyhSuFDjeNCRGSobSxNGwGW8hdiQbGGavc7w2mjal5s9gSLjhBsPCm8U5w72zaaJs1my3nPhVxAQDn+BMraGNW+Fz2APfWZvsAgHPh'
        b'pRTaKJg3n63ifhoNLDbeMeUvoo0JkQvYI5xnnCgb4FTWzKGNOl04e5xL2mTL3MhIsP2Q3323SzR7lksPB75nVGUGDaKNhYGx7AVuYbQg9GZGlcOPvDDYByxim7ikkSAM'
        b'GXdSpk2jjVMc4tjL3Csygexmxp2prjFUf2aAgT4CecFlo1RC1M6WDUXX8QHqgfGFqd4eblKDvR1o6mDQ1KMzqI7I506PBQ/YijtyjQJqLbzl+CBv1E7inixQhN1gZMBq'
        b'E9U/wI7BJa5yIU/qqFvsEYFLCpt9M9dl5kETbTzl8m/scUFAKghPVsLM7pG08V3Za2ydQOZgy9zMSpgoW0AbJ0x6gz0rCI5lQ29k3RmVZRwQX9v0RRIkAbXkb08yFybV'
        b'5nGsLfzdWDu1f4jiYHkNDFFmxpjdiV2qGmuPimOBfGW4KCLaDxdBqOiMT+YkCT1wu4KCfCNKYPu2gLxLst02PoWPcqs32ExYTtLOpCQdu3kEQ1kRicr9lfaowl+J98ZC'
        b'8GWNd3IbrBhK8ph5cah1sD/4NYi72eUMuoAu4KM8yQ/Z4YPenr5euNA/RoT3jWBs0wSDUOsmM4F76uplqBXgDgF37hDCzTcQSlEYih2E+h9YGBOapPubOoBv/GWBVV4l'
        b'A55EluRz2VrMUDlYFOakIKEei+vRfkYFxn0njTCiHWYrXf1oGFxGUkslKvOPQI2eLCMzieyHDaeQJ6Jm3KgIJIDuxLvQASYZjHy+maTbbCDa7w1ZFC6R4KuQl0JWFSFk'
        b'hsgFuATtXEZtLrgrE00pcDN4ykpGjWvQad5Ql+FSdFaBWgC5HHwcHWN06KSn2ZHK9E6lQkEnbUJHmbRRm/j05AyqRJUKBQTCqGs2OsGsjZDy7mU36kL1iiDy9gq45Com'
        b'RYpaKXHtV81RRhLIYnie2GcL7NHx4NlquiLagQ9MVwSRTKhtOjrMaND2cTT+wN2Q/zQpo2CWPy71ZqdC4rMCXAbaM0jO8XHSYXQItymCIP6DkKYNwonUEBe6qAduwAcU'
        b'QQTKMysglEjDFbMomEPRobG4GBKTaBEjdGNx0VZ0ckU6v9pp3IMOKYJAHVSAzREmPR4CPJKrZKIyK2/CFFwEAYxwNG5mbGeAeOyaTzeLjdmsQO3UV55FxxkdLgfyUqmq'
        b'dMI9uDgKkBcwAnyNRSeWoRotajBHQ6+nVGyMioiIJqcOj5NKTz+5VzTOR9v95L6cBJ3WoHoQmDpPT3TO2VuODuA676HogLMTrhuGznAM2jPUAR0X4i7dT7/99hueJgro'
        b'5Kg0+kzn7Hipj5sxxzvGN1zICENZ8LunINjbhurlQynouvUTjHYGMzFAR1l0fPBY1CClMZAZct0duNWe72tn49ApOcQLp/nIpAuE8Aputcy8xqr8vFFthkWk1MlGmMZb'
        b'LWDuRfehqJaXw07cHm5cZ5aQ+PQqK4qW4cs6Phu2SwLPn4svi2iM5j56dBJHKZiNq0i4CD12LI2cUHvMJAhLL/NxSxVY0EKpvRSVgXFdwc6NWYmq0Sm6pApVxRlNklwS'
        b'E/aws9HlUeJNvKCen7SFdJCttrOoyF5G6M8HftvQPrwft5oM+DIJT6+x+MTgkTMD+M6KmSojLkAVuMUkZljQCVwG2dMFSz41ATdJre0gnxBMYUei6nB8FTdS4SFT0EEI'
        b'a9fZEhSqWdyF8z3wMcynW/jQeHRcam8Lhhc8aAKqj4jS0o7Jy/whFDJAkCmwZ0ejC1Ni8TYe64u4ajx04RbiUsbAevGz54K3oXC0oMJFxnV0K9TORvq44UughRTv0jy8'
        b'xyjhWbafmKFSWZiEn9XqhZqltEvgyEJifiYAbYuhpi94tTuuADXyYTYO8/FHJyhKqHE9JBDFgyTrclh0fSIjhDgOlYLUnudNR3jgY4RQ54yIxK3UAtqa1vcTqJka+Rx7'
        b'Xu8apZOfwIXal8lGIB4byD1qiY98LGcRwd6+4ZQ6WVPRzidiNm24uztwgqYY+Diu6M9C69SR/hCgU7ltjJQZcb6pPwcPQDJGrM2y6ZABF+MOcLhmEYjBDkaIuli0XYmK'
        b'qSSulsej4lzcbouKhDq8G3AuZNHheRAlE0gzl6OuJ3IowYUrQZ07+QAgf/TiJ/LmbidbvYS2Z0z1fyKf+DAzKoKV21MwnfLQdanEBrcAO0JYtBPvXgAG9SgvhWcnoMNG'
        b'CxUrWVSDT40Gwu+hSyZN8HiizaPQ9bHmrbzi9QxB16TWlL8SdoS1H6oDG0TgNuBT2bjVlp8DTGyw8ojCZXRSvGkDCK2tgfSchjA93wPtntOn/odnGe1xO81YjrFea8ah'
        b'ckjIaF/FGHQFdFlqQzKdFlaGK4IkILhUzGqnjpQacBtuE1Jurlrv5wqaR51AYzza8Vh/DFvD0fY02uGFW+yluM1mnZgReLDaoVPR1TR+o1bUivfTLoi4PCGbKQqxwR18'
        b'3/F03GNEpdl8vnWRzQ2QL8YneCD2QOoEAGYPgqQFF7GoaewEsdAshy6ICMrIoQgqy8EHUCnagxqD0DlIrQ7himgbXLmMZcauETrlDqZSjivdM3CFFcMEMBuTA3A1pHrk'
        b'xBefmukMAngIH0KFTy1zAFrLYfkW+P8ApNEdCbgemsthaIENOKxD4D7Op68Fq96JjtuAqz6+lqKzFp3Hnf1oaoMagvDeSbyLKRq9oT9NUSPu8UMt6JrFRa7B24Y8oR8q'
        b'k0zFtfMpISLS0Ykn5MPn0Z4Q3OxlXkTod32CmxSXKsHjhUf7UQ/ljUujI30X48LYOE+/6Ehwarg0Qr40HMKNxbgJIt9lqCyXMTqRU9DGoX2noQ7ooKMtupJHN3QDTetH'
        b'+CW4bgIuDQU46YHhEdSIipV+vl6RZOOLQmbQUgHalatDJ/B2Phw4ELNeibvtQLFKaTwAsV0Vhw6igrFUM/ABAa6GqC/cJzLWVzxiHCNVghpMS6UkHI5PrOynNflo12hy'
        b'bGDmT6ccFntHRiuHo0ZfsnmMiHFERwXAoMNDtDNetRYY70KA8VNZ7er4aXFDZzs82PDhRx+vGzRfaD/YXXb0J6H78aNF80NDkw7eHB56cPawA0fNSzocVgXMlSW0bddk'
        b'Dh9yf4RLwq+cIDl57ljB3K07P3nd74DD67rb73/0yd8zgt7LP7aoKap5zazLKYXzKy5kf5KWInxtQnPKP9jEpK6//jhh/IE/vif1+0tVq3+73LnHv3NNttzps5g3j1dN'
        b'F8R4XOiYGl43+NyN0h1O+pfli8Lqd7x2uMyp2eXCiGXd261femg8b3vlyueTRxjGdywO+37hst3XS7hNbdG/ZIWuDf11Y93RsaX60c6jZ4e8I/r+Peu6Vrea7YH3A8IL'
        b'B03dNstpzPfT3j/4ls+Gi/uO3Ou+tXRGULVa/dGYJjvZF2dcqj/e6DFHfPUiN6Tzlqhs6w8+FcO/bJDeP49LchLiwyV5b99dZMgLGzEjLKy0s3vzhaZfayOmL5HFr/Dd'
        b'P+Z2jtch+551M7r/NOGaThrVHvzp66mH30v8YL98/Pxr+/dM1rQd/PRQs+2yku+uBon+8tXtvae+PqXodd405OXP3h3l+9Alcrlt8/1l0x68WTRhPnq0tWRezg9xokHX'
        b'eus/nqMf2/PG7PqIyOm1exL0rvO+O3A70HA8el13atNF1RvJq2+t/Zvd0S9qakYMmZuXEbfh/J/vjP/kb4/2ffXRLyFrP0t9e9kYp4jy/XYnFy/+ctOEcI3L/+m2Wfjt'
        b'tmG64etfOuCq9656M7b+8zPG2+9HfTA6Ljzyrk+ValHp5XMPJCsVk/1yzRew6u6DU/e8/qmPP3lj1RevBp+edOyB/LelQ2NHPxp99CuD1+ozm25/9uONR65ujw4qrn/s'
        b'Yxq0aIrTr9v1d3de3L/8i4PyP3xef+m9JX57C38a/M8v902pV8/d+8eL6/1//favn36U8+78sg/W90zI/CgoSnC0caz0wsNFs6IErW996jzmT5/9uXuB76WXVv044UTN'
        b'910f1nxVfbZ8k7xq8EdZ5g/Pr/q786zyzb++X7Sn/Pvfbl389PTm90/d+tS4JO/z8/uiv4hrOvtrZMHD2Va/bIn4956t//yj/zsLjsjt6AE+Oo46FbjYJwaCUlzmw6KK'
        b'VYwUnQdjitu30kNd3Rofb78IHy+5H/TjIoZxQXXRMuEaVIQbTFRhi3Ad2v74iJ+c7zuuQ82Q+ZSaiMJOmoPOe/tB8FXkw2ogfhajvZwv7hprInYNHcXnHJVLUa2PZzjo'
        b'JCg7bL5hBTpmou6iUIsPKiOivaKtQmczYiFnbVxhktFkEgx4IzmBD8H7YGGAoQSXCZgh0wS4BpdrTcRy6609lGjH8FhfcF857OwcfMFEvUattb+3nxzv8aG7AzwXOEWq'
        b'K+1LR9shwCmO9onAexnHeEYcyNmvR3voTQaqjF+iJBdDyggSw7MeBkaawuGaIZspmrh7wnKwnmO8LKgyNtM4dCzSjyfzRdyxSQnWDJfiS2OjfSPJhYEjviLABQKt3OHp'
        b'U/H/7ENu86/NeXIK78ifwpsMKr1Rxd8J08P4N+HBzLFnrVkxO5S15axZW9aeg3cQaFizjqw9S+5grFkJfQ2FPwf4v+8P3nP2/HtOYiVmyWwJ68w5kkM0kRBmO7DO0CaG'
        b'vxGwrjNtGSoUsv3/yNpCOgbec450PyE8h7L2dFcJ58C60R54cRJoFQJktvBZzLpAP7ST/6FnBLwMtn2YywW9tv0R7nep8K/RUc4a7PooSZefy/RdOVwf1f/KwYehx76H'
        b'Ub43f+PgL4fc0Tsmyo8XZG8xpBOyBeiCFcStHeiknOVdXxOudYKE7LwywgeSfyFD4sI6VDjgZIdAQA9g5jH0ZIfcSTPP3kqn2j0+4eFeeMIjoCc8wn9kwqISWb9/C4mU'
        b'GGWqgWUCtPZgQ7ZGFh0/NTBAlmWgbyb5DZg64EOESWbQmMwGPVlLpzWayBLJKn2GTKVWZ5n1JpnRpDJpMjV6k1GWm65Vp8tUBg3MyTZojNCoSRmwnMooMxvNKp0sRUtZ'
        b'qTJoNUY/2WydMUum0ulkcfMXzpalajW6FCNdR7Me+K6GVcgY3YCl6NUhP0qdpc/RGGAUqY4w67XqrBQNwGXQ6tOMv4Pb7CdQbJClA2ikLCM1S6fLyoWZZAGzGlDXhLx4'
        b'CV+gYYrGkGjQpGoMGr1aE2LZV+Y525wKsKcZjZa+jfKnZj47B/iRlBSTpdckJck852g2mtNeOJmwgKD5ZL850KLTaE0bVem6p0dbePVksDJLb8rSmzMzNYanx0JrssbQ'
        b'Hw8jAeT5g5NVOhVgkJiVrdGHUHLCBH2qCghvVOlSsgaOtwCTycMyT6PWZoIoAKaEUM8bqjYbCIU2PIFmGa5LN5j1zx1N7pxD6BPWNKvTYZgRPpkzXwS1Wpdl1PSBPV+f'
        b'8r8A5OSsrAxNigXmAfKyFPTBpNFTHGRpmmRYzfQ/Gxd9luk/gEpOliEN7Ish438oNkZzZqLaoEnRmozPwyWO6I1sgdlkVKcbtKmAlsyft7qyLL1uw38rThYjoNVTLSWG'
        b'QmZBTaN/Hlr0Bv93sJqj0amMJjr9fwdS/YOIkMfurL8vemzvsrOMpqcXsEiGxqg2aLPJlBdZbsJrjTb5BRATz2VS9QnXMvBcsJVO9wIJs2z6RBwH7vVi0fyX6W7QgBcF'
        b'pQuRgZWBkYtxtzojmd/geeOJLQLkEzM0/VjVBxCQQIe7jUaN7vemmsDBv4CIlnXIiOcD+4zHVZr1KRr98z2mZVvwkc/x1QM3hjG/t0ZazkC/u4BwG9elmoxgqVIhiCHd'
        b'z5uYbQAGgM1TPX/fhZZujd43xuD3IugH7P0M3M/3/xZBeCoGGDD5hfEAP1cLWz9/YsSc2TEvFrvELIM2TasnIvWsDYm19CVTgQQFloUZNJkpuS/U9f4r/wcEmh/+LxqT'
        b'dBV4m+eavAWaZNwNav0cm/DfABhRA6pnxM4NgCseen5f2fSqTM0Ta2eJi2WeMdD8XDk1G7JpXPTMjKUaQ65Gn0LUcmOuRp3xvNlGTbYqpH9gDQv0i+qfM2OlXr86RLZE'
        b'n6HPytU/ibpT+ucBqpQUaMjVmtJJkK41kChVY9CqZdqU34vwQyBZVmUSswkwxac/VTQ9cGKIJc8JgbzgeZ5h4OjHV+rkbNeZefpKPZYvXw01CWhJYMAEycraYZv4W+nT'
        b'IlLUy8gCJmROvbF6E2OmN8IHcCWHilEr2hOEy1EbKiGH1Q2olB5dcxNxI2pkpuMLaA8uF6Hjvvgqf6dRnTFpEoxthTR5GjMNHUcVfAWLwYqB/NYhwHny9HtaD4YeQeei'
        b'HoMCleNSS1WrGuejK2ZSuzwO1aA676dTXHQNFTGj3UUjJgbI7czjycE8LsQ1uDg8OirCF5HTJBip9BXj8+gk454gxHX4CK4wj4GRK1LycLF/JBnmH+UZGa3sO9GdiEvF'
        b'3qgEF9DTZldcucz7SS+qQgf6znybZ/DFb9fGZD65tEY70F7+4jp40FS6AupAZWg3uZw+K7PcT/fdTqN2eqy8Cl8GpIvRTrSPPzznGGvcyUH/+SQK68rVE8gOEYALZPq4'
        b'zD8clwrwGRHj7igk9z14DyWSEV0e0W8cKZQo8geMxuFLCd6i6U4sJdFSvH+UZVQyPsgPpDUFMdEsI0fdIlQtn0tL3oG87fYDNiYlAzBqHDqOryeJQlF5IK1MGI6vTfP2'
        b'w6WwlF9kNC7ykaOD4WJmJK4RolNOuJnSYQgqQOWWURHReI+PCp+Qi5lhTsIALwWt74gM9n+GxaZFlMH4FNpHS6uBuzusjL6kTHixZ7iPFy2E8EOdy8iRGbxdshCXCpll'
        b'vlbo4BS8nb/TOo/rRirwKVw5iZQOHGJSYoC5pCICnZ6Ju/pztwKXWLiLtwv4ycdX4AIFakR7J4ngUw2TPg0fpZKN8iPC0IWNloudAHQSH6HyMAtX2z2Rh1WsRRpwAWqj'
        b'/bG4C58AcUDlWwaKw6ktco6/eNpnhToUqCVbjPPtGTaKnP2V2/I3oK1L3BW4zQa10JNPJgN3Ay60nvgiqkaHQIr2hzwlRNvWyMX85N3oOj6rUGQLbJwYVsmgRlwi4XtK'
        b'cKWjQoGbRLMMDLuYQZe9cAe9VZsCWnRdoTAIpoYwbCyDLo0EYaNnoDtx62CY0kJ0oo5hl5Iayovz6KQlc3GXApVsVrAw7iQAeQTn89Qsd8clCtSKSxWEmqcYHSoPpvbA'
        b'z86Z8SH2YM05V++NUYx5EDT6oLrxYzRGWGU+M99tOV/gs9KBVPIEB+Ts8Lw6fSgjF/B355VO6JzSP/bpOx8vFe2ejs4M77sywmeXWm6NdFPQbv6GC9S2ixyJiUA8exih'
        b'kEXHkjXADsJo3abBhGaoB13gqeYYwN/H72VjKM1wUzpPtFUaqq4xqA4dflZhnX15fd2E6i1XbugkmLVGQl0VPsaT1zGTF4GOKSwlLj6EanniBqNOMykoDyLXvM9X8724'
        b'DfR87ioK3lh8yKxAZ9HZx1wojKILLLHXWabPGv5c9XcQ0AVc8EWhAlfjM328skZVdIFVIFSdz7cL9RwxC7v8KeHMYlSosF6sIFp3jElHZ3A5ZWFynD0DIusS4Cxfun3F'
        b'GEY+lFqRjbHrlRG+MX5gGjx59fcQCpiRqECITpOvAPAHmLWrxniPo3U5ct8IIWNjxaG9C3A93VCBLmdQLkak8TwctYpefUZYpSgXuT4tGrgkk69R2IY7cLl3pK/S1ytm'
        b'UwT5ws6gNIHGiPKpVQ0M1SgHFF0BqVCjZ46QGRklRPuDhlKaKJdD33Nqs2CbHlqftWok7w3OjUEl/UzO0Ng+g3MIvAFZCV0Fpu3gLQjaO8XRv59v8lKL0HnnHEqJvJVB'
        b'yjh0fkD5Gr6CS6llW4JOjuJrvfoKvQbhbXytVzS+QokyA1VkPLFTimiLnVqcyd+h1uG2UGKlroLy9jdTpng62xafGW2pV8JHWL5kqQYdwdVmLzK7KtZK2UdvVCQDdpb5'
        b'4z1R5HpHSQg8CR0SR+CjeDe/2TZ8CRWSG9kwfJ5eyvJXsqhjJH/v2oEu42JSV4UrIy2lVXxdVUccNUZubmCm+FotXOxIyrXAHO8Ppqq02CXH29N3Fu7iK/Zoud6oRZS1'
        b'MKg2Y2BFIerA+0hVISkprFtLpWqr4yAqVKtwGS9VGToe6lp0wNUbOFc0QBhRPeqhBTFRuCnCCndLIfKJY+KGT+UnnYAYqt0ibHg72ydtuCHaYm7Ak6A2EyqxmD1QwCLe'
        b'WNR54W1SMWolXy3B5yA+8kZlfH3BNXRxVmoarmDpNzdc0SW61Sa8e5kS71A+LfceuIeq4fEV9AtdAQGpfxzZGBPAmCdQ+QRKVj1H4NFxmUXi8W5vSvQUfA6GVeCrwJxD'
        b'4ARRGZMoQheoELvZavskOA9ffkaEifJRpJxRJ7oI/uB6dICAlKwwWagym4q3dOEkXDHIHrfhg2hfnhWhfDzYnTZadqCKFQyoOgCZiATOlcXg0jhcGAFd/rhoISlBCOfr'
        b'DxYtRC0BcYvDfRYNiBPQBTuHWBBDPtZD+/CFvMeFBU3gsS1uAp1ATZRkQ4KlDJhG6wCxMt7GtIqJB+9DZMwjeLqS1xIhPsgy4kTOC2/XU+uiAipderxom1XfmkvFvNs+'
        b'hRsNStwNVvQpNi1X0wGz8Tl0pn/Y5DnGEjWN96MwpTvYkQpSzwDxNHWs7WCGNyIdUnpl2j8ku4aq+mIy1I2OmpcSKs/D5cYBJAL6kG/bwYhqP19PUBkvS91hHDHKhT5L'
        b'w4m20BrHRc+Q8/qmwag0ZTQtMTwx15JF5Hxob5OmYCiJc9NmDNQ3m7w+bSt266vVrEBtaag1MFu81o5hF4HDHY3288b/JKQfbaSLBZNxkDrdi7huFk1QhmWjSzAVuL8P'
        b'V0JO0r+mZq8IXRShluTFpmTUNpkFlRAvX55Cd/NER2bRFdEF1MCvKFjE++CD+DwuoYDg9gQeEkWcXEidY/pgvF8RtE4gRNUMG0nA2Kem6usgQCUKj02BYhpqaiCwr+Sx'
        b'aoG1rikCc1hcHcWwoaBpyXxYthkXG2AX3MSsg/CT+PoWnU7O0j6WeoPWwIlM3kaGDYOQbyE6Yw4j6+1AV8C44FJcDOQs9sdlcbjJDjUHTlyISsSPxX6x79JnpB608pgE'
        b'7MoOvI9+X3Bm+AZUgGvQeYA5j8kb58cHeMeWg+qdD0LNHGqYxnDODG7IQQV86HMFn8b7VmxA5yE02MJsQUfQUeAeMUboFOzBoDbLFxD9po+2FGCiA0DOipC1qFFE6nEh'
        b'LF+PCmASjd4OrND26cgIfPix3tWm8N0tkzcp16x8pp7nYABlVGR6GCn8bLdjcX4Uw+EONpAFQIkjAqbuH9LPE+ljn+eIUAs4IgrlAVRmxVceaVA9LT6aMBH6aP1UQyiu'
        b'JD4K75nTz0dJvGnMhxsGuzwVvUA+19gXv4SjY7QU3EyK5cGmXQiRxkTjUt+lFnXDRcvCI5eEx/MsROfAdkX7wjLNfjFRsSIGQqcmCdolQCe1Xx/7iTG+D2vJmjab46eV'
        b'jZrv8ODB4aO1H9z66OMHH9e+P+oHlfMXrc12Yl3w7gJ3l4BXWOGWV3LiUWXYiI/edBy1eEpLgsrO8aZw3nviaX+w/tkqYd4whzE7C10dHB0cvzO/8fGG8falOVcf3vum'
        b'4dL5aw8+rNmzOO/eR05Ly5scT6G7+y5vGaxzf7VHedJa/+OFN9ve7hx13ufNg2+rtROPvbo46e8RjZJ7I2c8NAW/MjJu/tG3T3v98z6bN/07m9aVR+10b+yuD5t9suVW'
        b'WOonX+3bF3+vuBmU9FxWytc+mjmOv/3yQCLxaNyj/uz0tLC9W94QzX85cfbOS+ObFhSuWfD3WdGFr5QmMDVMxoSG8g9GtEVVCZt6JwgvLZVnyX/y/QP3W3Fz+NyPO155'
        b'ZP2o9/7m3W+PD7vE/TWgqwLXdI27tmgzq/xB9A/HyTn3D52791a3eOXbLa239i+d4HZs68EfZ3161qrcPCThWHNBiaswZ+gdxesPPV5+b5t524yaK10fp913cDn394lv'
        b'4dAeXUVDyf730ob/eO7zvBkfLbgdvTEIXfzHtapvHAe//ZnXnqO1up6QN7zGVBfu/cOOrvaj7apZZf+QLO8wZzecEufPYzexkxuvNn87pr5O2tb2Uog2eNY72YO/Tne8'
        b'M+HL0o8+PFVQ3/zVu2fXZtx8qb29TKD968+/LH7j7vwjqzTXa5y/Xeu09qcvJn/WNW3lsoVHW6RB8zqco4z3r7gWdyZevvlV8d1V7wbfntKge2dbTOgwt+y7t/yS84r+'
        b'wdbOObEvLn30O6+dfRhx8eGsl+f+MiMhtrwj7Eyk58RHmctU7bVW9aVrfFpvL1t4/+vVL315TVuRU2tYbfXnQycOO9zxbrpd4tQT8rem71b43DGq3W+/33n74CfL0+uK'
        b'fvoq54sz3k5ZGwXXpxzeevenM1PvZM1ZtyXH9cfJdR3bvK/u9FG+Yz254pUvfFZHpqx7L0ze7JHzMOeDhFtZrc6XWpxvP/jIrSm6TPUP172xX4+4n/vBx5F/Tvrx6Lnh'
        b'vxmXTAycfM/OKsz517tp3U6TQ8q++fmDsXfMXQtffXtbY7GTJHaXIj1392eMIvpQ8HeJj66P+96/+rXPp0tmLP7+0svvSD5zXp9XsePCrVVv9cxJ24r1wTXxn9/+MnrK'
        b'sfa7wrDJ94xpmzwuVczrmHa30O2Lf+/+pfavWza8ZYoaFoKvv5Oe6KnaFNS9e9qDYn/n/SHJv8p2Pfruy7jUvX+229dwz7ji34el1cf9Zf3Wk28VuK0Wp9X+sv2bBX9n'
        b'rw+Z8bC8eVrJ5p25cwZ9K/ti8OsXj4tvhr996829tb9eSm+a9PDI/5lX0nVS4tEpOdO09Fzq0r/93GVndSXNcc2U375yyl3+QHXLY5Xmb4cLH/wijYirFX57Tz7IRELT'
        b'TLTd1VLyBGaA2G5cLgCbMwy1C8NxB+qiBUUuc/Bhb3BxNV58NRJjs5xDpyFiaOTrlM7IfSylSLJQhpYiQUTQYKJ1yKh2rWWDuStZvqRqRSKtqMJlY3G+cj5uGlBRhaqN'
        b'tFgL7ZvvRMq9huMDloovS7lX3CQTPVTZgbf7kKKUJ0VVvng7X1flZcPXe10bvPxJRZj3eFoTJhOuiUbbaSHUormo1DsIN8RE+0TivRBvoU4udyPaRTtNkJKcgvhuj78v'
        b'5AWlgFYu5+eD2+jKm9AlmRJg5kvNCiF3gaUHBQjSxFJKkUGjUYslUkP7UDMfqoXxfagKVwn4sq5ZCHalVV0GISV0AN4FCUikrxOqH/C95OyZtMJtYZ4bbiVlXagxm5xN'
        b'4dpo8i326ULByCVyp//ftVkvrh6y+8+v88zXqTNNUwMDaAXXYlIktBX+HK371VTZ06oqa1pJxcEnR46vqZJwHPv8P2s6wsFSwyVhXTjyP5lBaqyGchK2/x+/kj0/94Vr'
        b'8uvaszJWzNnS1V0EDqw9rTITsm4wn9R4OXAyWsMFq1qqu6zpbs4C/inkYeBsOVIZ5sLRajO6P7w4ghUpvxrDcTBeyMNGaSDmJLR6TcKOYl1YZxg/AiAQsqSGrA8fB46v'
        b'cyPvyLfHCV5i2N9ATrpi+srIhOQqoF/52H+eo3LW4NDHU7rXa4SXpInZxnSMe/p77CF4FzrlPRy18WVluMyXxJQMMyJbgDtd8a4BvyZABCKULEciPw35ARpmBZfCrhCk'
        b'cPyPD/Q60AsNWuxlmG8wZBkeuvNXHFS4DJbaLU2KTKWXaUi/X4xc2GudmEjuhBITeyWJifwvzcB728TEdWaVztJjlZiYkqVOTOQl9smD4knC2r8AdLT00Jrjj7P3Z4+X'
        b'2uMOk9SG4BaCan0NvvzvTfjjY2IRmM3LcjZM+5eSCyKjO0zOK3ttRllnDA4dOj9N59HcWv5G0ZD3mr59ZD/75BcCT+vVe8ZK5Ysl2XNn5/u+4VI065Vbk+yte7786Pyp'
        b'3G8fGT4p6GqQNs/be79jdrvavOvtH+I7tk6O+fLroM71r87//Nhrj3bMkWV/q7idPfaR2SWiO2HLqx4TH4TvK7UfU5zso/hxeUlx/nWpdvaGhoZvTkQXGT6vD8r1utT9'
        b'VvLutZ+ftp/8TWD65++cjA4t8Gt9feJtrtjnbfVhp6XL1bV2QR8k17jmfKA+JrCfWv33xf820eOI4eWf/xDhO/5AfGXExar71YYD7htXZWu/O5dl7DpR3HVaWX/z3Y7A'
        b'ujORDbpXhuPe3W+cq/9uicPSK19OWNd6bOZO/XRr/dceO7ak3Mrxidu+fujHrw3yeZRwpLJcLjTRxOYQvqqHdIMl58mNbDCD99q40pJVGT4+lP6yB6OPNvv2+2UP4jlM'
        b'NE0F94OuSb1IWSu4imizNSqwDHRHrUJ8KTKF+hTXWU5G1Bge40u/wWip1B0MHhGy9Bo1SDgVdMf/QssqpuH7ix/UYoLY6rJUKYmJ1FyGEA1xJiYrEMwSKU0lxaoO1g5W'
        b'AwycyGK8BKO2MjYwlhjYEbasYVifRIMWcSDmT2zC4P8aFFmDy2P9IZuTKIEvPb3v9/Svl6CStT6omBwNkV9DQkWQNjH2k/KGC1wNc7WrNes5owZGhU95w/XlifY7Qh1W'
        b'39/99tbUXDtT8q7dd090o51r/+rZrPj5zspPoyde+2bXroaPV7T9+fPEjGs/H0Vbc+MS6qoTT3+99d04pfXYuLt3pyqybw7vNIyduO6riYP2ncrrSq2Z8e5tq5fedGmP'
        b'dZVbURe8AtLhq/RXN2JpcmcFHrqFc1+Oz0YPpzK0GO1F+crxqDvWFzeTYbG+HMhQtwCdmIb2U4FdOhd18liRo0RUSrFChcmOAjcPAR8j1OHd6KxyASqnJeW0oBwXjOID'
        b'n6O4Z76y388+SeUcqkKVuBxfRSUUyFk5uPapH4ZCh8ehJnQRF5jI6YEBIpYd3pEihg12VELSHIgO90m3239bGPGviY3wd/VBq9eaLPpADg4YO2uWd5XWAp+tNJhYYhj+'
        b'WNJlvQKdRt8rJCXAvSKTOVun6RWSu27wi1o1PEkZZ6/AaDL0ipI3mDTGXiGpBOoVaPWmXhH94ZdekUGlT4PZWn222dQrUKcbegVZhpRecapWZ9LAh0xVdq9goza7V6Qy'
        b'qrXaXkG6Zj0MgeUlWqNWbzSR2r9ecbY5WadV91qp1GpNtsnYa0s3nMTXGvTa8cGR1pgVHBQwsVdqTNemmhKpB+u1M+vV6SoteLVEzXp1r01iohG8XDb4LLFZbzZqUp7o'
        b'Mo+2m4F8GdowkTxIYbeBnCgYSBpgICdbBg/yICJmIF8+MxBnZvAlD3JiayCG1OBPHiRSNRBBNpCzDwO5LzWQi1WDJ3mQr2gbyBfLDeQa2EC+I26QkQeRTAOJng2TyWMK'
        b'eXg/NgWEOzaPTcHPYf1MAe17aN33A0u9DomJlvcWO/hwROrAX4+T6bNMMtKnSYmRWxuIiSGOXKXTgYWjckC0oFcCTDCYjKScolesy1KrdED/xWa9SZupoVGEYWof8Z7y'
        b'/L3W0/l4YSb5ROMSIQdKysuaZiixtOz/BTALpHo='
    ))))
