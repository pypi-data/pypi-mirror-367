
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
        b'eJzVfAdYVFfa8L3TgKEqitjHCkMXEBWxN5CqoGKFAWZgBGZwitiwgdJEUMCKXVRAkCKIiKLvSTGb7JpNNSTZJKav2Zi+JpvE/z3nggGi+Xef7/++5/vl4Tqc+vZyznvn'
        b'Q67PPzH+zsRfYxA+krgVXDK3gk/ik0Q53AqRWnxSkiQ+xRvGJknU0mxuPWf0WilSy5Kk2fxOXm2hFmXzPJcki+asNEqLn9Ty6GUh82MU6fokc5paodcoTClqRdRGU4pe'
        b'p5iv1ZnUiSmKDFViqipZ7SWXx6Rojd1jk9QarU5tVGjMukSTVq8zKkx6HGowqhVda6qNRpxm9JInDu8BvgJ/R+CvNUXBgI9cLpfPFeWKcyW50lxZrkWuZa5VrjzXOtcm'
        b'1zbXLtc+1yG3X27/XMfcAbkDc51yB+U65w7OHZI7NHdY7nDNCIa4ZdaIPC6byxq5qf+WEdncMm7LyGyO57aO2DoyusdnHyQXIp6iFEck9qQoj7/98NeRgiRhVI3mlJYR'
        b'aZa0c4qIk3Dbx9lw8WnfykWceSw2khxyjJwihSQ/MmwRySNFkUpSFLIkytNZL+Nc5klIR5ZOyZuH4FCLmXDGGBJO9pI94WQPz8lDRKPgBNSHOSfyfbjavxuGFZQsPBLm'
        b'/0IWTf8u9Pk8MaIvQvR5hr6IocxvFUX3+NyFfvKT0B/1O/RnCuhXhFpwNhzncNJZ69EhC+VYo9qR0oTjSvy32rhvXCo0fuBsyTlwnI9irM7m04UqoXGbVsrh/4r6uYke'
        b'UmtrropLk2Oz95LBkp+T7o/DWS7fiFomfDk1gk+zwg7NqEN8vQXn/Kc58b7vGF5Z9RXHmst039qX2fMpV1e/z//qbDLUcp2c2Ycy4hSchKvIiDpSRAq9F7m6kgLvYE9S'
        b'AFUxrgvDSbGHV4jnwnCe09lbTYPr+t/R3KIbcapNjN6cRvyYqvy/TdWcJ1H18eKPqWotUNVpsh03jMsYLfGJD3slbA1n9qK4lMJVKENc9riHkj0kP2xRcIhHyBLONzR6'
        b'ILbvVMRAIZRzyVILcmJrknkAnXIydrQfXMHlh0AJVHHroHSmeSB2wPZIuOQHl7EHzg2BY1wqHFhqpgLWbykc8vOlQEEtHOASTTIzBRH2DICDpFTKkVoJ58V5zYXdDNKG'
        b'QDk3gMtbZesQH7bfKkbg6vRtjtxY7oKTHRe/6pHLSk67+se7vFGFPXsSF9+P/yx+rSZM9ZLGa7+rKlj19/j+zWMSUzRpCV/EL1T9RaNcHKJSRoWqatUX+GrH5M+SFqpW'
        b'cvsTg1V69X5JQWX9eZ/Zy/cohymWBn47+7mIc3bzS67esqkYzMWEDbx3Mk0pMg2jiBf49rdGKinDzZ5uyHIRN3C6I+RKLMmZ5SZnRpkoHklZQIrJHjEnmcJDfQg0THJS'
        b'8p0iV6VSbKAs6fEQ4eMnpyCNQb9JrVNoBNPnZczUakzTO+XMrsUlqUxqOs5oQxk82oa34R14S96VN8i6l1CKO6XrVWlmdadFXJzBrIuL67SOi0tMU6t05oy4uN/tq+QN'
        b'VEgMUvqgq4yh61MMufccRDJexMvYU/SzSIQixXO/0r/MQ7HfH3ZMcA/2cIuAokiUEynnRHbI4Yxk8BbJ/ERRD0mUPEHM0bw8FnMRMx5iFHMRE3MxE23RVnF0j89Ps53d'
        b'G/QWc1mEmRrUIesdSSkqAuz29uQ8XeEQE9pgcp6UkFLUPjgPF705b5LrxkQTdsEJco4KIbfBiDI4erb28szvJEaqHCdT/O7Hr7hZAofgcklVaVV2Q/DoXVezQyr42xoq'
        b'bzaa98PE3MGv/7rHcvSHp5S8iZIoMYzkui/0JHkhYRFSztqWFEKDiByDY6S6i1tPEgPGjE5rgeeaNL3KxJhOBZ9zs+ElyHKD/DHDJYyBndIkdYLWZKCDDNRiKUU9mCwy'
        b'UG/Xg9N0uvtjTr/5B5ymrjOEXE5aZdvNa+Z1PHhuaLoE9mUOMQ+ilGueBa2jyA2jKcBHwokSOHIOCuC80HcBCheSG2Q37eQ5kZojVXBsHOsbRupGwTlSR7vEnCiZIzVw'
        b'BMoYm7LgymqoGGk0TaJL6jhSnapltoXsnuUePY62iziRnk5pgXNsOZK9KUMODUZyeSLdCbI50iQj+8xUIUeTZlJoC+2sU4qdORy5DEczBHPVQo6thBshRgObiIteNIxm'
        b'08K2wnE0bWdJk3kChQMNIGkibamsE06T6qHL0RHTTgQG7Rm5TErGC3hnw75BpAmajEY/OnMbR+qWkKtsItlFrlqREyPYREQcjnCkVUPKmMdGqWyFM7ilsKkFdh/lyFXY'
        b'J2Kw2jqSMj20kSajDYYDItLM+zs4mp2wZzzZA+fGkIvWBsYFOMeRK6KxbNIaLZSYVlqThom0B+MAMTkoMw+mu53B/UqgEU5Zy30p8uQAbwXtcI31kuOwAwlcM8aatDD8'
        b'yS6eR9YKNIViOL1hMLluJE2ZdhSWU7w7uUJOMvwnk7026B4PGa1sST1dt4MP8IZLAqN2ykg1qZprvc5MWjjsa+DHOZLdwqJ7SC05AlfCjdYGE513iB9BGsgegag5sB3a'
        b'ZsiMJnLFmnYW8e5wfpHARBS0rRlkj9HOFgkjlvLTkqGUidJmkj1kHjmPHXY8J7biZ5J9AxnFkO/FWVAYiT3rKHKtvJeSXBS69s2EfDgfZG2bAXsknHgMzto9Ttjo6Iox'
        b'5LyZCgsKUga6rE3kEOtZmOaCXrQexdlfxok0KOmkdCDDahqcsiL1pJIKg1QQzUayD6oFcdgPbetIO/Yiok32lJJ1vH+WlHUqkauNZAe5ZCQtXZ3VvN+MSUoF84UtYx35'
        b'i4NTJVzUzfS7MVudWOPPGQP4IA5R8rmZ7rxgXCBrFAU68a6bN0m4DBy5vnkia7xnN5g/NCYHzcTNrENBmpGscenkIfx30wsl3MybWbHbXktjjdGrh/MObvslnOJmlvPY'
        b'LzeyRs8lI/mzy45JuPibWXdXh6ewRlg+in/ofkbCOeCauhFa1rjRYzTvM7iOwpl1V+UzV3DkvmP5z+ZepnBi4/y1rLEj1IU/5H+NwpkVK9KqWeMnvko+WPIMhdMYG/Ag'
        b'Sdjd3Z0fMOEONt4yxvp7DWONFmM8eZ9+r1Hgjc4bVroIVLLz4iVub2PjLaOzRunGGmdNmcB/NvgTipHx0EISyhpvuvnxLy/9HBtvGQ/N0Qgb1S/w51vX/0DRNN7VuS5n'
        b'jYa5k/iXp/yCjbjmNO9trNHLdTI/zIGXIu7Gu9PWzGSNo8dP5bfY2WMjjox5SaDnuoxpfJKzgxQJYnRO/NyDNVZumsFfdh2BjThywgMBpJiomfxlzRgpUsl4V/9yJmtU'
        b'rp/Dn9UpsRFx199NZo2vi+fxHj4TpEg6491gsSVrfHfzfH6A3VRsvIWNYUbWOGdBMH9z0iz0BjdT79qfW8Ua76jD+cmDFkmRdKmxQ98RKF+oiOBz4ldj463Uu+NHDmeN'
        b'5YOi+Ly4BCmSLvXQuP3CmplO0fyqDB024kif24sEPcoldevQDhQZreVU+2xQj2pDmFrC1WRLyPW0NtjZor7246dBgYWgD2Xk3Hyo3IaW9kqmUcxshzs5F8dMgJkc7Ueq'
        b'k9DmoCmnJqCMHx0NZ5USBkMQ9xwfnBBogchm3k2/0p813lfd5pNWzET/d1N/aMpbGtYoD/oTP3ZOBDbe0t/l1yxgjaesXuJjx0VbIAX0zgl34n8Xr1t1xxrBHNedOP6W'
        b'H3Eaq8exu+Tfjt01fYMah67f3kHNtAizglKtWjcPTRYmdMUkPyTci+Rj9OkUj+Zjn8QFDo1ieEyaJGRIPus7tFuW2Ath87AgIUPymb95RPJqd47ROiEYToZ6h5K9kSHu'
        b'cA6zJZIj2gj1g1hnImz3hCa4TAN5fgZULefgIhr9A4KfqiBt5Iq7ysMVQ+A8b4xwbJLF9iQHaoXcIAezACiDfdCEkARygSo4b6AkZLDkrZCwxMxn6QfbhulThcaXnYVk'
        b'z0fzwxpRKgJIBcgPdkCbH022YD8UkcucitSjGxnLBIi06EJZkF1ME1wdNIdCsXcI1LrynMIktSMVMQIsZ1SkzM+fTimzcOcSoIOcMY9iVh6DvmqE84Y7Zm4sRcY0LkTC'
        b'OSrFZM8StPJMUNsjQ1jOAge8SBNSpREdIIWNnCYF8/ygkaY5J6aR61wahng3mCswYLJU5+dHJx2HUjjLJSvJQZbqrBpHqv38MNiGU0PIXm4tnB7K2lcs9vYLoOMPTSX7'
        b'uSQ4TGrMND7LGhUBh8jx0IUUtgjKKClnlyGeTK6TSjaRHHGd7xdAYTgMO505NSleyJy3K6kzhfrPCsM53qTIneesV6BjSSHlSpGAVuEcaPULwDASjqwhxzgNnAlngbBm'
        b'gYVfAAXwKMkfxCUvIeWCKl+e4bFJTgox7wmXcpIRPMY/rfFsqS3yWL8AGmlXYDDWwqWQk3CEwTDRfot7P3KMsoTkRwAmdzbTUEiuStmKc8g1qPbDCTjzpJk0c2lQDnvY'
        b'xHVwdjCS9wYpDFtIUygxucHD0QiyyxyKvWuHDTWGhYSE08OPx+mqK+w3eCndwr2UniI5VKoxsjwHZ11docrJXYkZ7Fn3AVDmNJCcHQTnRRwUDHCAk4qotIePHj1SRnaJ'
        b'oywp9VJiiiB5UL0WqhZo3SM8gyWcZCaPglJDCpQDGMaZKZAziRww2hrM1EAd58cYfdksFzdyAirDSZOd0NPCK2OgRhCXi2vhqsmBNHVNusG728MxIbBph+OkbTlUG3Ga'
        b'YNVG6uGUEKI1Y8R1Bm5AmXGdWU4D22u8AhOVq2ymKSwFg8NjGB1kkstSFtyNglMhQpx1abQjOUYqMD4jl215Fmj5TlouYFeGUpU3aLC1nTUUo/1dwa8klbwATPUilN4a'
        b'yDea5Jk0krzOD4OdGUzY1s+wH0gu0g661w5eMV0IcOgpFMmD1vmkyWQgl2lQe4MfmihnC44np7caSaNJxvEY9hyB4xwphmKZoJsXoHQ9HLG1trTFtEQ8iQ+OGSJQ6xg5'
        b'OVU8HYPgdTYU9CO8C9njzYBQiA24X7m1nQ3aY/FUPsRFxpTOk1RakpMbMEwyYDwqtuMnbUNrRGekRw1TY7htTxqprxnNz5o4g22y2RUTjr2bjOvYHtCCsWY26h2dMjvB'
        b'SxxtlAus2s8rPLu52OiKNnBHqDXrEvfnfTB+vsymOJDiiTj/LClF7fHgPCB3ODOVpJQ0OUOhvXzdep6TYHBHLmIiWURqNQIJDpv7kcZhv6EzEcNdFgufh2aMhiun9JQm'
        b'tDoMjjFmkg9lo3pAiJF6s8DAnXAdauaT/J6i5pcgyMRxaBgB5aSxh6RJSINSIkhF6SByOXNqLyaOt2MTteQwae3iojyd8ZBchyYBwabh+LmQXEGfbEbbAG08VLnCDi8b'
        b'ZsLIaS84CoWZpMUG8lGXSB4/AY3oYbhO2tD5RQh5XQPJTSQFq3oIpMmH9Uigbs5icraH0A0nRwTK1ZIamdf0HnI6MkgpgEtqrEj1DCizlluRRuRTIL8AqlBnGJZ1s7I8'
        b'BF0Ts4xnFNmJgsJId5Q0TSGnhvRQbDRmJUJfHjSQNighN6wtGe/lvBecDxFYVU8OYuqyEypJk40wtY538fRkE/nRmCSeo0mb2cZAuyp5F7iaIkxsWw9tg6DEaEdaWL5z'
        b'gh+LXrZdQKIcNxiHSRRpsbaiiVIjHwDZE9jEhVA1hp7kWhswtW2WMCZ7QaMzI9l0qEZBPAwXflOrMXOEJTELGY7W8IQ1abZaJ+PELvwUOO4uiPYuaN5C6sh11ofRmisf'
        b'yE1kXbOgZNUmvRGKMoSMrY5XboICIUmsc0PTeB0qEMoMe0x8SD4/nhShk/ZgMqyHiiwkTiGmRsXrSRkUoTmrDUBmlJODqBkHlvHcmDWSgesw57THCSkeqpDRpBQDMx/O'
        b'Z90ycyTTEDg9E8cexHXy+qxRhq0luHYj/l8G9TxpgCvYXIJDc1EEsPUC1KSsRYt/FU5aweEoUszoFwy1y6CWXO5F2w4QfN0c2M6TK1G9aJuwAR0nk4PTuPFOZOfuHjQc'
        b'Pl0QrVpSPJ7sTOxBQQtyw7wIuxYrOGtSFIquMDjcKyQc9pGD6L/cSVH4Qs/FJC8y2tUrfCH6O1IUolwajHHIYuTVZeMyzjiQHr3WovcSjmAdoLy/DbRMYcCsXIEBUsn6'
        b'3hqLoQY9gCLF6ER6aSUS8iKm9KXbBH7XwKVQctyrJ+M2jUIsqdI6QC16AKgI9fJ0W0jhxuTNfqk4jZyFIiEz3bKAet4iGlwk63gMHQ+JoHy0m7D1/sQxoZj/XiV7gz0W'
        b'RnrKOOtQ1Ca0nNlsa5OfGAOuXT1UEOOkMrYxeroOez8ocF8YHupJd8bQsj8cF0P9sEDtiJQcifFPGLMEVHesjpmqd5zlcDyr4h9TOxQz+x91GLHjqwCH/qJ9+6LKfE+f'
        b'OhU8tqBfP9/Gj0Ln7lg/LmdW2zdz8xe/Uzn/x1FlA34WbRWfnr3lWube4IJ33/7lxmF9crLGuyo9qvpKx3LfZ07PWdr6INp3pzo3tvGnPd4+7/7TmOt77daftJml2f2N'
        b'P5RPr0x42PyRdJmxX4f3wAGly25+eej7lXXqV/JWvT/3ltwl8aByjPGW6oMPnee6tJxYrj5J9i2Y+MYi7ak9n/w087kZe3YazkSeESvCFR1Br7jt+0GRt+3DzWsVixuG'
        b'qsybHM6O/jJh4sc+Fx0Gn87d5DX3A7NGceu79lfeWvx5xfNvTAtYneD3wEHdLk36IWf28ysfjMvb9sWXf/Oc9pfNQV+7GaWffCNPe081f6qHVeN2b+dp4RF3gs8k374w'
        b'ODN1pPvFbU7ux+0tpyytOXu75ljri0OXXSvMuhcaEN9YvvO9k/842LK2evku708TQpenj7usdvtw4pmfL4Zvv/bj9ejPHt7e01KuejMm49f3+tc+/Lbm2R+rnKe0v31q'
        b'7gZ9aV7Cg6lWP2ypjCSVr8zfdJTsfKG6vaQw5ssR47/JuSO6d374Ov+6hFUk9pnWG2PW5+mHtf74yaxb74HHjy0nXKZn/rDy9vb7QSd2rEpqrkjzrNKMem9i86rnjmw+'
        b't3vYmw+P2+5YMN7UWhT20eavs++UNpodk5bE9K+OH5ofUNRQH/7qRxknowc+4jNHLln69aAzvtLXxy9oKnux8eCnv9REBRVPffPq8yqv1erc+19tfv8Xu+KfAfStljqr'
        b'txZ/nZnxfeKqmNgPpymfuddWOyXKa2/Ow1E/b2r1a/ugueJcw0PXXy99uoY8u1e3oXlc+ost4VNfX5cIiZfHT/RJj+n484t5kc/febHNY7PT6qAK8ZV7V185uizwdvHm'
        b'QZ/Jp61V7F1wfMHByF89Q6T3v/Ge4NTe9mDtt85ro+u33vNb1H5zYsqFRfqcio6TX706Q/Whq3XoMKUtOy1eqZWSwtTJHhEYy5JiDwzXoQbtLJyDEyZ6DLvcBsrcvUI8'
        b'3JRe2E3yOc5ZQXYMl6yBKrhool5Y5QYt5Dy09r54aIBz403MgUNdprsXBk75uLgM9oqipZ6kXsOmepFcciXUwzUY1Y3sgHbUZtx9IzQ4mpifrQgjZaEh4W7hFpxMIkqR'
        b'WE7MMimYgwrCQLKDnQ7juhhx7CHFYs5xqpgcxY5LbLY7OWURGumJzi0BitbzszCoqTcx+3PGd6G7l5IUoKOQwUXRHLjmZ72JXaBARYCSFIZ7hGCKxMn8RbBPZwdnIZeR'
        b'IsKLZIeSsgB6WRUaQqN/pFaSiG15kuEzDbJJhbubgO1UjB05q6kiODGKnGP3N2HRCePHh6LdQuPruZDeXvQnrWKSC5dIi9Kh76n8f/WhtPrP5vx2C9BfuAUwGVQ6o0q4'
        b'52aXAe9wNECV85a8jB/A24gseRveToSfxLStPy/n6e2QJS9nv/152SMJ/RU54F/dP/hZZCd8FsktZLzokUxkg385iRxwPYlMwu6XnPApwx9nXN+Jt8OWARIJ3/OH9nY/'
        b'Jd/IHPqznYXZdmx/Oe47Ap/96a9Ijq3YS3fDdrqynEHsROHg7X61kch5g003HZTiTpue6Pe44vjPqKrkDbbddGXLz+G6L0A6hj39AkRJk4QQONN1/eGtxGzUPSLMS5B0'
        b'dxm3AC6OcrfAgAoDBSXPotJlsNeggbOhIR4hGOxymLcucv/dSRIFhh3wRHHsJInetHO/v2vX2D4+URL9WydKYnYbLPk+HTeQK3r8i6KiZFSoetdHsKKLjRlqRXjMFH8f'
        b'hd7APvh69Zra648Qk8KgNpkNOrpWmtZookskqHSpClViot6sMymMJpVJna7WmYyKzBRtYopCZVDjnAyD2oiN6qRey6mMCrPRrEpTJGkZh1UGrdropZiVZtQrVGlpiuh5'
        b'UbMUGq06LcnI1lFvQHFIxFXomLReS7GbT2FUol63Xm3AUbQsxKzTJuqT1AiXQatLNv4BbrN+g2KjIgVBo/UoGn1amj4TZ9IFzImIujrw6Ut4Ig2T1IY4g1qjNqh1ierA'
        b'rn0VrrPMGoQ92Wjs6tuk7DPz93OQH/HxEXqdOj5e4Tpbvcmc/NTJlAUUzd/2m40taWqtaZMqJa3v6C5e/TY4VK8z6XXm9HS1oe9YbE1QG3riYaSAPHlwgipNhRjE6TPU'
        b'ukBGTpyg06iQ8EZVWpK+9/guYNIFWOaqE7XpKAqIKSXUk4Ymmg2UQht/g2YZOZtiMOueOJpemQeyJ65pTkzBYUb8y5z+NKgT0/RGdTfY83RJ/x+AnKDXp6qTumDuJS9L'
        b'UR9Mah3DQZGsTsDVTP+7cdHpTf8GKuv1hmS0L4bU/6XYGM3pcYkGdZLWZHwSLtFUbxQLzCZjYopBq0G0FN6C1VXodWkb/0dx6jICWh3TUmooFF2oqXVPQouVGfwBVrPV'
        b'aSqjiU3//wOpnrFF4GN31tMXPbZ3GXqjqe8CXZKhNiYatBl0ytMsN+W1WpvwFIip5zKpuoVrGXou3Cot7SkS1rXpb+LYe6+ni+Z/THeDGr0oKl2gAq0MjlxM2hNTE4QN'
        b'njSe2iJEPi5V3YNV3QAhCdJIu9GoTvujqSZ08E8hYtc6dMSTgf2dxw0165LUuid7zK5t0Uc+wVf33hjH/NEayet7+90FlNvkrMZkREulwSCGdj9pYoYBGYA2T/XkfaO6'
        b'utU6zwiD19Og77X37+B+sv/vEoQ+MUCvyU+NB4S5Wtz6yRNDZs+KeLrYxekN2mStjorU721IZFdfAhNIVGDFfIM6PSnzqbrec+V/Q6CF4f+hMUlRobd5oslboE4g7ajW'
        b'T7AJ/wOAUTVgekbtXC+4YrDnj5VNp0pX/2btuuJihWsENj9RTs2GDBYX/W7GUrUhU61Lomq5KVOdmPqk2UZ1hiqwZ2CNC/SI6p8wY6VOtzpQsUSXqtNn6n6LupN65gGq'
        b'pCRsyNSaUmiQrjXQKFVt0CYqtEl/FOEHYkatSqdmE2GKSelTLd57YmBXnhOIecGTPEPv0b2u8OkZvBPX9wo/Uii//XCqeIBGTD/Fe5xYohEuv09tli5eK3bguJnxNmHu'
        b'c4X6YtjjOAIKoQkKAkgJNMMeeuhdDUXk/Ap2Ci6aQGqhlgsiF6VwMom0sbJHqPG3gCZMnqdyUGQ1dZkrW1/jauHxK+fMcYr4sDkSf45dWK1ZT3L8fDlyiJTS220u0VHP'
        b'igzI8WWT3HunulA+GrPdUSOlQ+CsWWnLrs9d3MaRwuDwsBBPoAdOOC50vounjBsZKyFn4Sy5Zh6No3TqyaTQeyEd5N3jSHcCKZKRnZ7uSeQAO/aNGQmF7MgXtqf0OvWN'
        b'hgrhXLgEGklh33twT8VkKMoUKhIuRJC20K77bhdS1n3lPUMvdFcvhjpSKBy4izhLclUUiOQr8A9jyHi7kH108RDEAjN9UuwdDLtDSJGYG9lfQg5pXYTS+/NwYBsbhnzZ'
        b'JwylxRj5tABirLs0CE4HmcfhwMxIcr3HcpFCmUJEOJ8ElzkltEvhSPIKM623TbIm24UVj0R3702rEMJ5bmy8dCYrKaBMSfGHA5ZQ5e5FinA9r4XhJN9DKeOGkqMSOLOG'
        b'5LFBaaSGnOwaEhJOCnAE7IAd3KCBEh9ohRPmkVTs4pf14e5m2NXN3b0msyel1v5YqDKy6ubFrvR0by/Ctoyep+H/S6IcXUmRhFvmaQHlU0mdcPXRSvv8fCVwHBrxz4Nc'
        b'EpwbY6ZvW5Dr5DTZzbhrQ5p6cZcUBHVd5W2AHX6+Usgnl+g1HJeydS7rGEBK3Luug+AgHPKBM6SZ1aUOJ63Q0lccyGGonuxOihnHoxaHdosDwpTdLQ+kcmDXTQ5CVUZO'
        b'+EHjhA0ZMo4P46AO1SubXaGtWBGCHRwq3w1axMGlkmtQIFxnXiQ3RvUWpOG4bwEcIUeUwk005A1O8PMj50hthpjjQ+m10LnQrlpZOIZK5wc5SaReyvGLObgM19exWXPI'
        b'xWjsaYVCA86K5OASaRcKLGaTAgs/v9HBpBGnLOWgBa7YslqNWaNJhZ8fH0gK6L0Ul+rgJlym5sJeaPbzk1pCHS3y5NIgW6gm8/UfFHtTHEvtQNA81QaOmYxhTjFGnuPm'
        b'cQjb2XliKGZDp0n6bXDlZ3JcRrxNP5shnFLM6E5OjoTdj29+uu993KEcrpJDwnVwx8Rtfa6NrGB/GpxzZoKyBHLJQXo6Jo1E4yWR8HACDkuRJexNgBynMD8/o6abbslk'
        b'L6NAysAZSJrDEx4TzQIlnpqXrXB4cB+91aO8dest2efWXe+yh7Rl4hqHJndTd4RAdmzSYPul9Y+pm0mOsLXHhEE1Wzs8/gmqjmrawci3LSgDeUAuRAs8WLzaPB5b/cll'
        b'oWzndyYAGuy6TIDTWEH4OywDkVmkaJHALJTLNmZFYDfUww62iDu58STrUAunBezK4IK/n59kky0tRuJSUOIaGRe/HW+vmcJNRv2Jt/lr+FBOOYChBpWkkpwZ4Bsa4hnh'
        b'hXbCtfvsfijkSqASGsayy90QaLCmBTZKzxAJZ2UhIuUalKwGqBdUvtnOmTESbgR1MXI32S5Y25Ili/oICa2wL/dVCN2taGHcF3qGerpF0PeS7JPFw+GomjRPYGa2f4IP'
        b'qVjdo7YrFCjpaAHR0DAJ7Ce7yE5G5FH4qaX3OFoARo6Q/O4isFOQL6htK6mDo8wIOW3qZYPSLZjtXDveXjAnsLeHo1ozi3NLlEJN+lxGkPnkMDoZoWJOKJfLhMMboVwt'
        b'GLr9kIu6IBST6ble5WQxyWyBYeO9+hqtAUMmJ6PEUboEbSDXum0WuQRnu21WwEahzGY7KVV11USJxnRVRZHsAWY32pm9ethjkqMdLfYmBWH0IiiUUtgXDsrglH8IuQAt'
        b'jHlxqo2hwu3sYk33/ezsbWybjWvWuXfVbDnHPq7aum7JOrclU+hZFRhcmdNVCNZALjHsfNKhyF2oCIQLbt1FgVUkn5EHLk3w7lu8SOoWc07xEhd7C0GkTsIxE5Mp0jZJ'
        b'kCk5Ocpo4wborXsK4yJSDnvJZTgmvL9RrE61xrAnGmV7YTSchhIhbGhFFarpLWrQAQVqUqlHy8BmtpG2AMEAps+fBxfIBWYXJkPpPGuDDCrgAhK3CgMkcmyumVZmzlQt'
        b'YW+WeHKOJM9z5BxBvppnwb4+Ir8W9y4nRwcxTfxebLlmOK+g/tdmlWm88C7fEHSB+XMHPl3U4cA0ZhgTRrjSCggL2O1AceXiEtKZIpNDcGTcE+Q2c4Ugt7JRQm0UFKFr'
        b'a/IRbyQ7aKjE6QPRslKWRZB9c+AwutVSezvSTMotKNVjyEmpmV5NbBmY3rNqYRG1E8URpCia5GFwFOpN8qNo7UKwULiwKAoafaIXB3ssehwpkOMbaKgAF20dIuHMXKE6'
        b'oFJDqvt4iAGkMI20CWXpFmutY4+IXTnOId5GttSNi0HXQ0VvELRDlXpDaHdFoyxO5EaOwz4mHnOhZXqfNcV+aaSFlLI9dSPj+jCH1MjRaZWSbObWoGHcwN6Bk3yDEDYd'
        b'JNUMqtmDbGx+EmFcHhVv82OSjmOxVATZuQJObHlyVDbU0hxL73vgDFQbe1EIyUPfF/TydEVNcQuB63BUqGaMpgTO81gaTJWEKeGiXtSkpOzY3A+1jOSw2sXXp0oCOSFx'
        b'8HC3ShKggpINZFdfTbP3Zoq2BGq6PKLruJnQ5I/O5jKNfhaht10n+KMxy+XYoYDtGTxztnXTyWEzq5/NJx0ZpBSQ9/vIAUxBelbj1EmhMWGxKYEKafNEHqktWz6JtDDx'
        b'G0/aJbjkJijqXpJURglFKEXz4QB2bd7WDQR67yalhAHiPRPK/QJQyRvXoc9eiNMSlnUlOQv8/PxlKnsWaKr1QUxH0JxjEOkvX7MeN5nJQdX8lUKcVzEBe5r8YR/GDxzz'
        b'8Y1ryDUlL0BQOx11Bwmxa9IE7JxPS3ZzRptnY9ci0jbSmr7biYQs9CbF0bGkmtTbQoP/hKjHIr/Yc+nivjzCBdFuHQlPYtCODxqPiojKxA2EA1s8ut4xyUKFPAw1ASlA'
        b'XwzjRE4cqZ6YIXjzIjQ2HVAjxfiGWwVFW+H8tq4AiZyPhfPsLTUvtKeDvWBXmmA4K8dHIWdqpYtn0YIppBBcgQ6cRHUjhpTL++gGySHlafxIQfabV2EO0ieka0NvXr6M'
        b'7BMoWOVKjtE60hZbHi2LiFzh/cmpTHY/qkk0/bHb8SaNIRg05wgFb6cMrFw1w15Gssk+oeooGnYIhuE6HIHLXW4Jznt1+6VNUChUv9euhrLBoU8JWiyWsgpz8xRK3IHQ'
        b'aB0RToo8l3bpGslfFrxwSXCMwD+ocvRHyxXu6RURFinlkKT1ctg1ntRpN098yBtfwoV2px8xLwkvHjrPofbLwy3Px11b8/a1obncHMtRocGW/H4Hmw/GpMH42cFzRWeL'
        b'njlVptgzf8Oepdvbpjwze8jkP2ufvWVxRzrqmcEfO6+bm+e3IOchP2zyunvmoszE/HlnzMs6quo2Lfn+3CRrTczLy26lG575aMDSoonxH4NHa9jGjzXvHn4ptrQqP8I7'
        b'qfNIvuHunZhZsXPeuP/R7NTn9HvvXZzw6rDY6M+Cwjq2R94clXhleGtBTdvtpVd9X/t8dc0rQTXLn319enjZ6NCml6thZef8sEdZOscFry59wdt+/+alRdteyEsNWDUn'
        b'Z6r8rn3emgXfvZeec7uI5/8lizVeMJaPuHegaL3l0lfnv/+622stu997ZftX14JOjt1vfNHwZVZFauE/tbOWSd4Vdfb7bo1M/6VvVtW/JKHf52+eM+3rL5Zdvf/XlMCL'
        b'8pXfVl9xKXjz3I7XOrw+fRD82pzbm/rFxtWvvmUnnmr3Ba/65Xr8gu3m7dMmf5f1S0x97s1gl8wd0238g+8YDi9aF3Rnw8xBg/71+citSZ3GiRUF//L3k45OAPUAv0se'
        b'XjXLF8xd+eEZ8b26Gpf0u8X3svKfqbOLMH/3/t0o8WababX/an4wZuvt8W+O3DY2ULthxttf9fvxod2UlyDgB0NxZnriezWLfnhjRyH5KC31vfvnDc8Xn9Ed+3XtSsO5'
        b'8vt/vbK18dsrQ6pf1b0w79Br+9Mjgi45ig8P1AenT9w6+4eh6nPLd0XOduQzUp73TMxafJkvmn1s4qW/rBp39LOHys8fxgXMfCCO7RilL48cFKX66dvjbaum1twN+KTe'
        b'bfrUqPvRm9f+efbbmg/Pf+Ri15J88qDl3Vfr70T4z/Cz/eqTt/j8T5/jj995YU9oh/HlBY5f33nwbOQbC/+2hd92x/rR7W8jfes7LJt3fb7y4dIxW/nW9e63G31rTiXL'
        b'N7ar5bs8/tbpOuAvNu0tWQF//arwNAn/6wdXf/G2SCt13PCv/c+8F7H35o2xP1iEDP1iTcuSoX97ZdycleZbri1u9s/PuHf8wjfun605tNXi2l8uOa0dVvj9inyIPiP7'
        b'MNX52buDb3jsexT00Gl5+wtbnB7sCHvk8Tfnf07N8VaUXLqwf2mO9bmDR7+zv2urbxqx+9usVx8ke07PX3Ln03de+PtFn/t2n6jGt/rpt/6j7cTIluFv7/rTV/e/f8sl'
        b'vO7T05muU5xecQm9+mPasn3bGj/JWnr8zc1ln/lZB5Yf1dQtStqQVT0he4R+56Wv12ZHXLr9y8sf1ux81+EL23fsNaYxU+SbrV8/+vV7W/78tvjSz57i+W9UnN8u+8z1'
        b'7zPGff/8hmV/V//t/rN7X2h3+/yNR++88zBuwtZBv75Zee27gNd1v1hbTj90d9Q6pb2JBksayIHsriIotB3UXnvKSBvkYWjRIgkm16aZhJJ7e0d3t67KJKvlIkw4LkKl'
        b'HI6w2iQzNJPmENLYsz7JDoqnsioruGgxD3aO7lVo5RkylU0c5AR5XUVWQoGVG1RsdIV6E0sdjmK+eIwUdhWAkYYFj2vAgshpNgRj2hxHodSK1KzqXW21PIqVRkE72ZHR'
        b'q0wMioZyzgrJGlIfyoAYHQe73CPCPRZSyC3hqsienM1cB60M+oFzSKUNycawrsDbExHLFHnBPnKNLY2xYcO2UIT9cQGavY84HPYkkxqoZfVcWTGzkjf3Ds4OwF6BLIWb'
        b'nKeT5p7VXn6j4bLwNv1uspNc6npTekIsfVeavShNTsB50yght81DA91Eq72gNkN45V6FEAwMkojhKqlXDvx/XbP19Doi2//6Or97zTvdNMXfh1V2pdE6oW3409+yR42V'
        b'nFVyWbK6KhFvx/cXCRVWcpGIf8rPtzJ7OoZ+Q4ANm+/MqrvoHFpxZfeLTCrne/4Iq9kJs5++Lv25Lxtkxyt4Wi9Gd3AWO/B2rAZNwg/D5wBaJyZyeCTnZayyC9fuqvoS'
        b'PZKJ2d+/yGVs119sZLTVUowwiWxEtHKsvwCZSM7gwV8RrV2TiWh51miRCOdLBGiF6jORUOsmx52d+QE4YwjbSfaI1sLZ/SqTCNjZibor4xxEdrgSxVbGW4oMtOQ8orvU'
        b'TELvBXqUmP3Xea3kDQ7d3GZ7vUi5TJWZ285dGfv0wjMm93tR5vOdPbuKz0ixJw08MWfMEJOrqB3lv/suBCo9M+kONK1V02/m4VaIkvgV4iSR8PUJnQ7swoMVgxnmGQx6'
        b'w08jhSsQJomGrtoudZJCpVOoab9XhFLSaRkXR++M4uI65XFxwlfw4GebuLh1ZlVaV49FXFySPjEuThDv3x4MdRoFf4TQsfpFSxFLfQeShgHWduSKydqKIuhp6PouDW9y'
        b'QgPXZVI4BSeV/Hztl9vviY0jcfKcSdJpxVcjyMwB85LTXBqaSv6c7/hG/QOHHzyDTVs46cuVk33nnR3wvjxftvLIhP7bSorVwxw2/fnasgUP/vbPj2/Ym5cMSsgf9pY+'
        b'8q29rw+c/3b0u7++Pvnw+bc/uqcclL/N64G1fMfN6y8GkaIv3lSN/TrhR+XIZ1vHzAsIzPMoaHjpneQJXj888jor/biqujo3YNyf8o92vlPd/s3swsHV+QcDX7vw6sn8'
        b'yMIAfnjbS77PB1l7NM4tVi+NVReZA+4mFaavv6suzrKbfDZu6IzPK/eP2Tvlg7Km/NIVC12rPEpXTXhr4seuM76b/Cl89KlpziBz6MGw7Bf12uDI8pi3Svx2N9sejQ7/'
        b'uEZxMeNZ8z3NjCzLd1sHveMTLMm+vfcfsedEXyvaD460einWlJCjlAhVtUesyXbMTVCWJpMTqzlMXQ5CjWBpW+cY+3xvCeT6B0osocmX+cet49dZu9G62F2knbqXx+NG'
        b'QpOEXILacFb260QqyCEj1AZHeHaH4I6wg+tHSsRQb6RcE4S//3+jHZaxWP/pD2ZfUW7T9KqkuDhmXGlGxzlR4+bPj3gkEtHSVjSlIgdLB4ueplDyo8ymy9T9S2Y5bBtn'
        b'JUKD4UrN8mARbxjULdqoTiKU99/sRb//HlR5g/NjRaKbUy4LpatfeD3dgrCIoVS5ALNLerKUHxkG+VBswZGzpNlusHj4kiztaFEtZ1RTmxE2e/hzE+x2znTY/ddtmkxb'
        b'U0Ll7vdPtcMza//hUTnmx7srb4ZPbP/7rl3Vmqzmt57PTL3x0wF4lBkde/bIe5Wft/69alzOPqXpu4rBre+vurrOZYLv1xts953xWN30+vG/F4YeHPnsF86vzZuutBAC'
        b'nZJUKGFfIxLJskQLdPeNIjg4mVyApkVMvuAUZrL7QyM9SQMdFukpQtlqF0MBNKBRqIxj8cjc1YsF1OhRJCbMiJqCFNr1F48YDVeYJqRCO5wMDXHy7y5ct8Q4oljQhL2Q'
        b'nRra44uxrJUibw0pwRV3swryjVAV0+eLs7wHQr0YjgnxzCnMn3e5LyTFgKk4H0rvUHeTxm7BH/E/Fo/8Z5Ik+UNV0eq0pi5VoYcQnK1ldyW52GMbi0qWGAY/Fn5FpzhN'
        b'reuU0PLhTqnJnJGm7pTQe3J0o9pEfNIS0E6x0WTolCZsNKmNnRJaRdQp1upMnVL2zTadUoNKl4yztboMs6lTnJhi6BTrDUmdMo02zaTGP9JVGZ3iTdqMTqnKmKjVdopT'
        b'1BtwCC4v1xq1OqOJ1g12yjLMCWnaxE4LVWKiOsNk7LRhG/oKdQqdtkKUpTXqJwf4TOi0NqZoNaY45t06bc26xBSVFj1enHpDYqdVXJwRPWAG+jOZWWc2qpN+U28B7REG'
        b'+pa2YQJ90BfcDNRuGqi7NtB3xA0u9EHl3EDPRgzU0RnohaqBXlcY6IWvwZs+qJAZqBwb6Nm9gX7LkIEe3Rlc6YO+OW6gJQAGeg1koGdvBqoZBiq8BnpUYphIH5Pow/2x'
        b'daDcsXpsHX6c/1TrwEb+ZNn9TVOdDnFxXZ+7DOZPQzS9v4BPodObFLRPnRShtDRQ/aIuX5WWhiaQSQU9neqUI0sMJiMtzOiUpekTVWnIjcVmnUmbrmbxhmFKNyn7xAid'
        b'lkFCZDGdRjEsgpFQnRUkTz0Aobbk/w9mrxFI'
    ))))
