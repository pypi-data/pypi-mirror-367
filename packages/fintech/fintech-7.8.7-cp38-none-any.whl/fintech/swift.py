
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
        b'eJzVfAdYlFfW8Pu+MwwwVLFhHztDV7BhwwLSRUHFCsMwwMgwA1PE3kCHKnbAgtgF6SiIImbvSd20TbKbdUk2MWUTEzeb3SS7abvJf+59B8WW79v/+7/v+X55eB1uOff0'
        b'c+69552PuEf+SfA3FH9Ns/CRxq3iMrhVfBqfJhRwqwSNpEaaJjnNG8elSTV2+VyWzOS/WtDI0uzy+d28xl4j5PM8lyZL4BwzlPY/aOQJKyLDExXZhjSLTqMwpCvMmRpF'
        b'/CZzpkGvCNfqzRp1piJHpc5SZWj85fLETK2pd2yaJl2r15gU6Ra92qw16E0KswGHGk0ahQ2mxmTCaSZ/uXpEH/QV+DsSf50oCevxYeWsvFWwSqxSq51VZrW3OlgdrXKr'
        b'k9XZ6mJ1tbpZ3a39rB7W/tYB1oHWQdbBVk/rEOtQ6zDrcOuI9JGMcIdtIwu5fG7bqM3yrSPzuRXcGSGB2zoqn+O57SO3j0pCNiHBmUpJnLovJ3n87Ye//SkqUsbNBE7p'
        b'EKdzwM9rBSFqFE8/peg0Bi1nGY8fNw+GA1ACRYtjlkAhlC1WQlnksng/GTcRdpOuMCncItZFSt4yDMfCRbtoU2Qs7INSOJ0YC6U8J48USDM5Za/mH5GnRy8WSylDeGTJ'
        b'f8CQdA8b4XyhBAkXkHD+PuECI5zfLtgIT38S4aMfIzxUJDzcx16+U/BESaXoqhamcKzxxkDJrO9s3PC1DxMbfdwcnEt5FGhKinPE9kVi44QhdoMGS9xRR1NidCNSuFpO'
        b'J8fmXw0ZIv3Ggwv9a/9N/Due5rUu83/P6xyxQ7m4il8j17jh+MnvTh4U/CXHmk8P/8rtlbnKUUL8Hf6npM+DPuR6OIs/dgyGW0YUQUnAEi8vKA6I8INiUpvoFRUL5b7+'
        b'kX5RsaQdinhO7+Y4mxzs9xin7XvJDqacplzm0iX3ecn/h7zMeBIv7wO9z0snkZcnM1254RznGRjuaPGYZhApgNoBcJ2U2yMVpT7RqB1FMUsiIn0jl3GToxMGksOJpIQc'
        b'4TLs7OHUOLBaKOBtUJFL2uYEkQ5cgdRyuVq9ZQC2qxfOgTOkJohcoe0nuSxyehKbQOrgmr6fJGgy/XyUU5PqFRaq6uTItplZ0+GQHcf5c/7k4EaGZion5xCcQ+CGSQv9'
        b'9DJRkH6CBzcO/w9c92vvFxdEcNoUpZOdSYUtiWnv3ku5m7I+PUb1Srr/QS9VhOrzlOfe9FBnputS/5wSpXotXbk0UqWMj1Y1aC7xdf0z7qZFqVZzB9URKoPmoLT4fPPF'
        b'wPkrS5XDFctDvp7/fNwF1/D9nb9yPvEZlxg98IOoN5SCGbnGDYPTzirY44Q8UsZa/LxR3AI3kFilDtk5bAAcJ+XkCPKxGMqhVMJJZ8Bl2MuTlhSoVPI9gpdSKTFSmfR5'
        b'CPj4YdCsdKNhs0avSBd9nL8pT5tuntMjZw4sOU1l1tBxJmcq4THOvDPvzjvwXrxR1gtCKemx26DSWTQ99snJRos+ObnHKTlZrdOo9Jac5OTH1lXyRqolRjv6oFDGUviu'
        b'FP777oKMF3g5e1qorySXoHOIT4SvdxwpWxzpS86Mi7TjBsEu6RAlKQ5XC33UT/oEnUYPcl+nBeYfJKjTwn2dljCdFrZLnuYYewE/rNOyOAv1U9AcQZrgEOq9n8d4zo+c'
        b'ShWbWwPgBhxCGwtw8uACyJUUpnCzVppFbYMD2zn/TOjUhvqd40zUDua8o7mXsuqZ/aSSXNlfe2j7/tr8logxezrzI0/wL6ZT/XJOvxNjz1WUOYx9doGSN1OvypMbcNon'
        b'yg8KI2Pi7Dgn0iLAfic4qSQ7bXJ5ksAZ23ucROmm6wwqMxMvVXPO25mXonCN8vuilTJR9dilaVK1ZiMdZGSeSugjTsFIA1gfmdLpPvdl+vuHZEp9Lbk4kFT1ypTFEF8e'
        b'NfxUaLaUHCC7odIyiHLxIHRDvsk8NVDKCZvjUzm4MBQKLZ60az+5QC7SLp4T0kiDBh0JXCHlloEU+uFA0kj7JJwgTM/g0A7OeDBPMCdsgMk8jYIjN5L1HNRtW8NmpGdH'
        b'0HaBE2Av6TTgjCxywjIYexbCSb0Jrkyh68ABDcnnoA1a54j4nSHFAazTjhNmTCYFHFzRjBLxQzfUYDKK0xrITQRZD03kMoNJilzCoM0yieGxE8rQwUGbaiubOI4cGsv6'
        b'KC43SDv6K7jCk0aG5uLFpMNkCqLz3Mn+HRw0OpPzlqF0vVOkltSziUg0Tssnxzi45k/KGKakIHcp67TnBD3UkeMcdDqFi8gchqZp0GZyluOKa6fCVT4YJ+9lyKQQ60In'
        b'I2M/tJMb5AIHHaQazjN3O28EeiNomUJ7Z+7AiC5JzGVYToH8FCf5ZEr6FrgFR3lHObnI1lpBah2coJ0RDl3kFuzh+bHQKOJRSG4OMkFbniviMYmchNO8z3ZkGEV/BpwE'
        b'q8nRBZoRJjnvC7f4qZNmsK6w2dOcci3QzmFH0yJo4cfDLrjFII6GOjhucjKa6aRKOAGV/EgduWAZQlfbB51wy2SGDifsVcAeKON9cPwupibOsVNMri7IEAlUkg47fnZi'
        b'KiO5n1s0trvynIScI1WOfCi56caWMsAxUodduVSil33hGu+PUq9hfXBpwRYnlxxSKkVwh6FqLB+KzNzFWLVpHamgWoL6s5KcyuFw0rltbKnJO1JQg4NlnLCMdKWjdoeT'
        b'40wmpILsDqZKYEeVVaAK2Uo6oVqU8/HUuSZogTY3ZOIqch4a+eDUWYxiOJmBKEK72Ef2oduq44McoVmpYBFud44HHyxwXndkdprbS2qHscYBzgP46QLneUfGZXg65vqw'
        b'xoOywfwsgZt+Z8PivMoRk5ayRmukJx+KDuOO6wd6z1GFQazxg35D+YUCp7jjas3zzFGOZI1vDh7BRwic+x3/cVuSJN+tYY0fbhjFxwhc4J05Ozd7DlufwBonb1bw8QLn'
        b'cCfOXpcU9K3AGv/hMYZPpHjGFehvBzy7WISZN55PonjO2W9MSisIZ43SWRP5NRTPuL+mVU4hA1jjH8Z48SkUz01/zLk9vt3AGhPcvDFAcKF3NpnUt2PdnVjjlCxfPpMi'
        b'r33ekLQiJZ01XosN4HUCl3LH8Zr5tuanANa4b/skPodSpPyX2tMDFrBG1/6TeXSs8XccPTd6jtfPYY1d0VP4jZTMITXZnv4zRCYfGDWN3ypwOXci39/iGZMvZ43NA6fz'
        b'Oyntjls2Vbq/PI41Zphn8gUCF3HHcbYlaXmXHWs8Y5nNF1KGRH6Q6jnaI541etnN5UsFLvPODNeNSdqzE1njTkMov59yyTHc7BnMubHGj2Ln84cFLunOJqOhcnisiPyf'
        b'1yzkKynrNn25xdPokcMaqzcu4k8I3MY72i3rPQPHiIJbJ43gayg/p3yV4RlNRGUQhsXwlyjrBjZoKg2XRNalj1/M11PWheVt8IxaOVmUUcISvpmyTvPRltsjvx4sJorr'
        b'lvJXKOvs3tzqOXD6EGYQmfZwxeQkp8YHJ4Oc+dDVUMNsaJ0UdjsZXV3QWknpmn78bLTNDlHlO+AM7EV/3ZFnQq8IZzLQcfhk9Hrh43EW9Dfov9ED+EMBHObHQMUspZTh'
        b'oNj2An9CgsT6SNI9I+dqWSPX70W+BoP6nbzhW5MmfezOGk3JL/PnJKg8Kz7XJsXNCmWNLiNe5S9JkAMZKdtvb0hc/Vjq7dibUYRyXO+e78EGh0t3vJ+GS//9LY277ffh'
        b'lGVOnBh7m2fNIiWLcStWDkWRsf5QhInkIHIQDqdIJ0I1FDACFuYKnHQ4OgQuxdcly17MgpcrHDl3KXrMlJSYZscIjoUe0p1HaqIDomHfYrJbjbmZAxQIm6CWHBT9VScp'
        b'm0vayBWalpMWqOBXcqTewSy64bNQQop8vDCdLQzADMY5Qwp7JW76HSyLmuJIOkgbTeaPzQvhQuBCpJGyjqES1l/KOWz04nGnpNs0b47YqF8h45xjnpPibi1maIAzJ2YD'
        b'J3CbeT0okKrgcHKQU2GKVWWhGedgUkNuRbN8uRzZcWkblEaT8oBI0oBwFWY719gZDAK0hKDK0XwSmuAIOcylWjBDGUVhH9u80Qd3XlAaS67LcPdSEhAp5forJVBKjmOq'
        b'Qn3yEIxz19jeA6qgiu0/OqGCxZmx8c5BpBUJXEeOklOcDrqmiiifh3bnoCD6qZJGXC4D8i1shj25FhsUhClzPOwip7n1CihjmeXUsYuCptIlrLNJJZeW42uhxwpkN6na'
        b'Fh1F8YpD8aBsXOEc2ZUjmU6s5LRIWz5UkK6gqYiEUyCp4jSQj1kU3U+Qg6R4VXQMTgyAMh+ec1pFSrMEaCT15LhSEPG8NJ5UB01FJYGr0ZhwpJNjcJJZK7lKDi4PmoqI'
        b'piHA41zGSpLPJD5mKwaeEtzExNqRI6SRk47kyRlyHWPlAMbfXJIfNBWNRT2WnOAy0ZS7xfODVugm9T5UNFAURxqknPPsoDyJWxJp7k3FdhqDSDtLMk6SGspLclacWjsQ'
        b'Y31JDLJBAhdgP/qPbh6lUw83LLG0/8BicsYUExkZS48x7m9CvfyV3rH+Sj9BTs5ryAW4QM55eWGSdWzaIB8lJk3nfAaQw4MGwrnB5KLAkeIB7qTGI1333c8//7xtPRqB'
        b'7247qptDeImohjOnhPjE+UVIMd2r4qShPKkju1cqBzDsM/xIscnFaJGgfVxFR1XNjx0FB8TsYb8vjeeu2KmBPTQP45Xk3FTRg51VwjFooxNNXtjVjSnMfjjIOLlFQnaa'
        b'cBY/dzL2HOZHpdoyZ1KWRYpMuRY5T1qhgCbCvAKuEltnEdrjacwS8uCK3aR4nFnKj84i+1jnNAc01zbsceFJCdzEzhZ+cjx0iAI/MFfh5OpEygU4lchJVvGrBTOjOwLz'
        b'e5NZnieN3YKL3eSHk5beNH0/uSynXXZQZUFou3hFnJyttAZurYQ2sxGuSMjuQJzWzQ+DQ2gDLLWuWILyglazjPPGrA2tA623ANlFYXrghszJwUWOUoVOTjKNjyDHMxmz'
        b'Vs0nZZgC5zrjjhhu4XLH+Ikp5CjrM6FVnHdydXbkUCePcpKZfCQpJtUik4uz0YDb3IyuAtr+RU7iyk+DisEiu6oz4Ar2QauLgKpVxknG8PO2ISq0Mxoz5YOmXLpgB5Uc'
        b'aedHwhGbfWCSei7dJEfJxcxDXA7yCnOOyJRdC6HKiXYI5BIn8eADYaeBTbFHT1oJh9CkyDm46sv5kpYwUUW6vdGhu8lzN/CcFDO+eeGkbBJcYf4igRxxZoRB41hGl/sI'
        b'tswSYh0hatW2XFGpsm3uyn4U7GSIoXrsE1GLJ7bs8qgEMWD6Jlkl6hupHcLgjUAfeJnpmyfZIyqcv0kMwvs89b2ybIAKUZjkImlnRGmjkkRRLoYboij58cz7YEJ9AU24'
        b'BDowQFvsOCm5zsPBCLIrCs2ahZ0CUgU3SUkeukpSJEXKC3nJBFI1LpvhaoZyB5s+7oUzTCFJx0TGkwWkK5Sp3RCNqHUzNQyX0FmLmaKSVn9RU4dDrdKVkRc9mBx3kjtC'
        b'q0RPrnKSEH7RQLjGerx5UkDplkB1DEI7yo8mtXJRLNXOcI1ZNW78rotW3R8KGArhcd5ODrSn0I2TyHl/Ur5VVLaGqGBoc6bcP06u4JxGfuI60iYq21UMXOdRhZ2NEjlB'
        b'RsJ5fqI7XBSN4gAUkDKTK7SbeVLrip2n+HFkp6cItSZ7Ndq0kyM3lzRjVys/FS25ieGfARWRTka4ClelG8cymfp78Iwdw8lZD9GUOgOZJWWgr2VrnUXNvuoEVx1zZVAY'
        b'z0km8jPIZbKTwRsXRlpYF6KRwkm8+BDSGSfG+lbSnmMiZTm4WYPWcYw4JRwg4l6fVCyFC4hkjptMiWFBgCJ+QtZGCz1EiKAnQKgJh0j5BjhMytA0G6aSWrSlpk1QgX7h'
        b'6AqeG7tOOnBIEEsbtoWQG3DIniplWSAXOBS1l/r5eLg0DgdXYLwrfATOYWzdj/Bb8f/DmC10YNv+uEAcaXXETWEFXCKXM9cLNJepcaRqZycyomniSJGvcJGcFxlL0yrW'
        b'uQPqySEbZzcpRc6S3VCCoZNJ8wR6ExsTw0iZyMRyOMeYOBjaFopMhG44xrg4a7RlCV3y1sT+TlAWjXEwItY/MpZU7MCo5QNlsVF+S6FwcYKXf2wUBjsoi1Quj8B0ZCk0'
        b'Y968gjMNpCepDQN6T1TdyREPZ3JmtYhMN6kiR0Tuh8tF5qNtdSCu1BYzSFdCtL+fdxRduFHKuUElWJdLdCi8M2KqUI3mf5YGzjLMFbzSMFtwgEqBHImBTmasYeRaOiaI'
        b'Eb5Ri/1knFM0OReO9oAcOMVUzY/stRONqEwlGtHAYAZ4RhA0+0TFRvs5DaWLY4boQaolpBmjlFW7LeVtO9OrmHxMPeuyNvHluAHzBjSseD3m21cCi+WvFH4X2m/JEvew'
        b'3Bhn1Wdxg/0VubkfPXulKm3o8gvek+JiNv8hWp1k/pr3LR2VuuY7u+350R/VvuPSb9Cytdteu3nxL5dnZuuKXvnzVhORH1z7wbkdc/ovP/i5fOm5uR85vvLNpi+L1wxI'
        b'/dbObuAnX2RtO/DSB78vrkgMSPvq9NLfjEviDRPr308Yu2L5II9pUW9eG2LobK/bP+DonOp5ZuOnnW8NChkwaX3OPm+nbJcp6iP/vDL01w3dniM4reT7V19cuMf8oeL7'
        b'/E+rktKN08hnuuFpk/s/+9kHwZ9NOuE+5Ix182jNZxb/5SlHV3629bx5V0vs8xe8dSGN/Duyyaao0y+/vUX54agf391y5IWw5xOWV/lNSl6R8uPItufV2v325peOKT/4'
        b'e31r+qqk2V+0fZKk+tflWW+sUcSrb/pfSbma0Nn19c0b7w42P2c3bk3Dxx3Pvpa1ouPvXeErnDobTubKe7wTXtr7u65hwxTTtn8rX7vvlaErhv2j/vXvDXve/u6nzZt2'
        b'TFg08ktLmPcf3rnQuvXTyN2z194r+WC95uztT5rTvgp5dfDkhBvW2pA/BZV/91zoyKZ7SdOaBzXrU/3e9Ft15h1JfmQ/c0bNHz733xD2cteoTe+9cyp0xD//mTtCXjVN'
        b'/sFQ7Wy3z7qzB3hPupI67JI5f/lah1mtp19Ymza2+sXyNX5fHJv64r27ExN/1b5UvVr9WU97rEo3uewHz8071937uOR3nXvXHz8zZMml9Wc+/e6d3wRbXzl+Zb7q9NYd'
        b'1uN/Xa2+9eUL21WfTVvDfes+5a2X3HJe7b8mcdVHl98sfO71NTPfnrMv8Tdjv2tQZLzy7Oop45//6tA/b13e4jdqZvqHr7Yb+zeqZ1ZFTijfWF90Nu62a3rNgpLC18c1'
        b'1f3Fd3LJypGv7V6d2vjVhfP+n390y/WVvUNix+yzfOK2f9PfrZFZ01f8XNxy7oUfu6ctrvmkYdo1j6zhXyRk3n2jx2HKDiX51VynAmXKsleVLuxo12UUpn0lvnGYikK5'
        b'L2bf5HIsT7Pvrv5mltqfJ03rffwjfb2V/jgAijjOE5PgfQrpuuEYUIexLOoSes7e+4DhgMn2DEx+MI6cNrMAtXeVn48/5rxFCF9G9mGy5+U3b5GZnSdeGQuno329IjBd'
        b'7YaqaDRoclnYRGrTzNRBLYOiOdGRsd6x9pxMKkDHFAeomc5uIUa46Om5LhStjkKk0COUS7j+MyVwnFzyZVNJYQCcil7sx3OboEbYwM+DBpIv4rOTlGzy8VdCsS+H+NQL'
        b'YaQkyGGOmQaPgePhOJTE+kZiTsLJggVSSo64wmVSyBYdCl320fQGKTqSJu/IrTTcax0S4Pi0UDPz1Kf7GX28Ga071Eit40yBnILacLOChR6MBa3RuMlBN0pqk/yifHGn'
        b'5AHXJGCFYtKidH/0FP2/+lA6/ntzHpzae4in9majSm9SiVfN7PD+XXxw8+W8Ay/jB/DOggPvzLsK+ElC2zx4OU/vbRx4Ofv14GU/S+mv4I5/9f7gZ8FV/CzI7WW88LNM'
        b'cMa/BgnuCE8qk7Kbn0H4lOGPJ8IfxLtiywCplO/7Q9eQsjH411cydw+2sjjbla0vx3VH4tOD/gpybMVeuhq2U8hyhvEgigfv+pOzVM4bnXv5oJT0OPclv8+VxL/HVSVv'
        b'dOnlKwO/gOu9sLg1vO+FBc1BnEk7VPvAaXJTvLQIUOJ20icuxl/UcR8Zt4jU25PD5PQoJc9iuANpDImO9I3EzFSI5eiGsxHaHjsGohiwU5oIjh0D0Xtu7vGb7nSX+8dB'
        b'wi8eB0nYraz079kIWK7o8y+e6o1JoXq4HoEVOWzK0ShiE2cEByoMRvZhsv9DUx/6I9KsMGrMFqOewtJpTWYKIlWlz1Ko1GqDRW9WmMwqsyZbozebFHmZWnWmQmXU4Jwc'
        b'o8aEjZq0h8CpTAqLyaLSKdK0TJwqo1Zj8lfM05kMCpVOp0gIi5+nSNdqdGkmBkezEWWvRih0jO4hUOwCUhylNug3aIw4ipZhWPRatSFNg3gZtfoM0y/QNu8BFpsUmYga'
        b'rf9IN+h0hjycSQFY1Ei6JuTpIPyQh2kaY7JRk64xavRqTYhtXYXXPEs64p5hMtn6Nisfmfn4HJRHSkqcQa9JSVF4zddstmQ8dTIVASXzwXrzsUWn0Zo3qzJ1j462yerB'
        b'4GiD3mzQW7KzNcZHx2JrqsbYlw4TReTJg1NVOhVSkGzI0ehDGDtxgj5dhYw3qXRphofH25DJFnFZqFFrs1EVkFLKqCcNVVuMlEObHmCzAs5lGi36J46mN9ch7IkwLepM'
        b'HGbCvyzZT8NarTOYNL1oh+nT/j9AOdVgyNKk2XB+SF+Woz2YNXpGgyJDk4rQzP+7adEbzP8JUjYYjBnoX4xZ/0upMVmyk9VGTZrWbHoSLQnUbhSLLGaTOtOoTUeyFAGi'
        b'11UY9LpN/6M02ZyAVs+slDoKhY00jf5JZLEagF+gar5GpzKZ2fT/P4jqm0iE3A9nfWPRfX+XYzCZHwVg0wyNSW3U5tApT/PcVNYabepTMKaRy6zqVa4VGLlwKZ3uKRpm'
        b'W/SBOj681tNV89/mu1GDURSNLkSBXgZHLoUudVaquMCTxlNfhMQnZ2n6iKoXIWSBDrpMJo3ul6aaMcA/hYk2OHTEk5F9LOJGW/RpGv2TI6ZtWYyRT4jVDy+MY34JRsaG'
        b'h+PuIiptOJduNqGnSsckhnY/aWKOEQWAPk/15HXjbd0avV+c0f9p2D+09mN4Pzn+2xThkRzgoclPzQfEuVpc+skTI+fPi3u62iUbjNoMrZ6q1OM+ZLGtL5UpJBqwItyo'
        b'yU7Le6qt94X8n1Bocfi/6UwyVRhtnujyFmlSoQvN+gk+4X8AMWoGzM6on3sIr0Ts+WVj06uyNQ+8nS0vVnjFYfMT9dRizGF50WMzlmuMeRp9GjXLzXkaddaTZps0OaqQ'
        b'vok1AuiT1T9hxmq9fm2IYpk+S2/I0z/IutP67gNUaWnYkKc1Z9IkXWukWarGqFUrtGm/lOGH4PZZlU3dJuKUmPlIdfbDE0Ns+5wQ3Bc8KTI8PPqh+3e6/xvEPXr/vlgs'
        b'g73jLLB6wv1R2519hkwVb66njrbjHGg9+KANvq85BHOWSfTU4tysKaSEtJHiqbCfXCUt5DQppWfWdaSMnWALk6CBNHCzoN6O1HiSs2Lt4a4BbqQthpTjbnkmNxN2bhVX'
        b'mGjP4S7Xfed2rfO8gbmcbZPaRK7b6mLXkcOcGqxQaBmDf8+ZBod8lKQG9j660R09ym4o1JFipQu7RCcHVsMlKIkgLUmxMZF+hJ424dBoPxk3KkkK56AryUIrZ6HRCTqg'
        b'JCCKjgmIgp1QFhvtZzvVnQRlMp+kcFbv6TACitmZr60P9pEW8dSXdLqya20oJpdIQZ97baiEvXaca45k+hzSzYBACzSt73t5TQ6SW6sE3IPvgbPimfX5+VADJT7QDMfY'
        b'8bnAOUCnQIrJrQTGgXQzdEVHkSs8lEYiPbjph/KACCiTcKM8pLjivoFs2BJyFKwUF9sgWlhRRGsZxvlAvo/drOm8RUmXKyPn4UjvOFINJ9lYVnsQF8tzStJlR46RpsEi'
        b'UysN5FofoDiqJCASh40jlaQyxS50wUQLPbrSr/b18YcyhOQfFQtFvkoZNwyOS9NIKzlL9sAFsYB2v8cq26jIWCimgwYP3JgpDSQH4AAD4wOdY32UI8mBJ8naBActvjio'
        b'H1yGDhMrPF7qRY/49iFuK+iRGv6/LD7OG8qk3Ao/e3LEbQy75BoBO1VBk2n5RsVKqOTSSHMYu5An9TOgqq+E7YNF+c7bwebp59F6CTtaobMcDnKZ0DWB1Tgsg6o5cGj2'
        b'MnuOC+QCx0ABk+Na0g51fXXhhL2oCtASxi43cocM66sImuFUDThSZ6thcEHbCiKt0BqbI+P4GI40wtHtrGc0Wl4RdlGUq0khOcRlaQzsOkO9ktxA1clD3emrObDbRylj'
        b'FxpD7eBgUBAUTciRcHw0RxqmwU1G2/oF+qAgHaLcbMfxSzlyZbuLeO1b0J+UBQWRixYjzljMkSYXaBd78mG3DmHtHQStOGc5R9q3ZjFYUg3cDAriccgZE1RwWTqoYnxa'
        b'qp0aFETZd9YYx+mGECuz/23ZgzhfWhbkbRl+OiaMs9ACIaiAyhRT5lYEEsaFjYxmI2XyfvTFlOnc8lTnvcOGckqJyOglqL9QSk5J2S3P/TseOAzX2QXfDnIp5cE10Vpy'
        b'Tcq5LZfoVjiI16EF5MASeiBmR4t3q6VSnpzKht0oBUpLaiLpQCLL5vYybEh/di24mtyMDAqiN/C9DCPHYSezkdnrZqB5dsGVp9hnDdQjcApkPDkBhxH6JXKtl7sjSDNb'
        b'd+bcuUFBE6D1Pm/1gQy4O7rauida9QILGjXsJY22+m+oW28Tgls/LmtrrmjtN8hFuD8favo/0dgvkj1iVTIK1yYxqJ7N6aBxJHMt0DRY/RQnsA19QDC0iRpyFA6ANSiI'
        b'WtqpAHKSyySF/ZgkS3Ld2BsX+2N3xMi3LOWUA5i5w02ld3SkX5w/OgOv3kP6YcQqJWcHkPNjU8Tr2guwP9gneho5B6VKv0gp52gvkH1ScpNJ0xGukA5RmuQAOcSkqUb9'
        b'Y763ejScpJeBFRMf0ZRj0MBMcv26fj5RftF+3nFQOnAmz7llSDRIRSsLFFGwh7Q9qMqiJVnINVryMyxGmrqDHISOSPb+0cCNpAXHoa+r6DO2T/kWas1N0QMWkLYlfT1O'
        b'/GJbRNlFasTodNMDukUvQvYFkKYZfQZ7q+3IZXJoOGNL2gpcNADtpjVarKgSq90uDWSRKWljmq0crLcWDPI9WDkYwq0UcamdCXv6+Csvclz0V6QJatgS3stJZV+PBSfj'
        b'qctat4x5T8wI4KStnIkqTLGtnKkIblm8qBVOI429N7E+pAj50h0RAMUx9BIomr53NZlUyCLjN7OlDEnL+1zLQktitADVpIJcEkPk4a3Q/lDN1UDSOFviRs6h9lM5Dpi2'
        b'zVbLRasTDrNaLjhB8sUCjSJylO9T2gd1izMkbmBFDWKlc1UzJj5ehpgCheScdKLTMLEo4MQoclXUMi00MyVbgdMpdB7ql/hEY5g/2Vc9oQkqmV3qoBpuOKFdd2AWlMAl'
        b'rBbvkwnmEnD9vu7BGaiwad+BdegsqPecHEiqTKONokfEYHBRLJOrWr7Bib6qArXQSrqozZ0JFT3APre5cGgLOUffAeH8xsIuseqsHJpSkTU6aH/YCKLUzDTPL3GgJZqB'
        b'OSPydFucwsU36uCUhBx8muqvJl3kYC4UiSUdFeTqPFrNgMGQlE+Fai6ZnEQNo7qMaZLpviq7QdVjqtwKxbYyQ7IrjrQFSthLNjtDOAO5MEUs2mmVQoMxEg65ucJVOGLP'
        b'Ie8TEa/zrAhhdBLU9C1CWEKdSHkclCVAYSStb0tCCymKp+UIEWItwpJ40hqYsDTCd8n9fIFmC6TexX1xlC18DIdbUP4gfkRIxPDhMY3xK2eD+FbWb7y0zreGR3CJGJWY'
        b'lp1JhypM645H99qLLFnwJt1QLZYR1QaQ2gdAyZm5IlTMm5vEAScDA6NpZWDBI77qIqY9VE8xUd3t9Fj65EEuSgMxIaoS68cjnTm0B6+ds9NiLsXP50TvfUyA5idlZ56Y'
        b'i56FGkQgiQ6zkk64bnqIT8gk+kqfv58X2o63rTAxgXK50Hd5BCbEbdSwmWUueYynt7b0I2Xz17JKRMc5UrateCZA4yyZNoNj7l8NzUlPsLzpkC9FiyQFaAhMxVDPMRtu'
        b'Cw6AfJoaLcGoTI6miOawW4kBsi2YHFDl8CwuN6q8Laxg9VKKAg4R1IMDcBT3KH1LbRrtSGvqUnOqAPnk6hQe2S5bOQQNdiALKOUGCrCofy9AUrKK5VJyyxbsCCMXe5GA'
        b'w15KqVhFd0GWEzR10YpcjOpRNHPrtpWVwZn15HhQMK2Vq9hBjnEaKBNf2dlG7TcoWAt1G3CZUPTG6O+uM3rVExDvtmCozIZmjiUDraiRxUqxGgp2w85t2O3phTszPhwz'
        b'wtkGy0KO3rrfgja0BihBhpYEQHkCNLuQluBJ8fd1f6nfcsw9Sh9TfzTQU3I45pjIHMlyUuhNLkNLDGK9ldsKxwKYj/WfgUHq8lTMOA6RFoETBnFQBwdIgYjVyclI8+W5'
        b'5AZmD9u57eQEabRlVOvhKClFiq7OEl9vXEf2syne09KwtcGOlSPvduTIZX4RTqE+KwNaDA9sBTow1WPGQvZMFMuJz0ItKYpmnmXvw+YSB4cYE8eTfUG0RrTdhec2QL0A'
        b'HXwwXE1mSVEIKYT2h0LTmFmPR6YRUCuWTTvFigVJHGpaIytJQocjeqcGsKb0jVtnp9O4tSRKtLv8qKFPzG5WQRPuwa6QelZFbglh7kFBTjrFxUIZikg0OihaERG1LCJR'
        b'lCKpRTcW6+cfF7MYE8QdmNU1y3FjVbxKW+10nTe9ipDmf3LLsiy6fFiY+19e+Gbj8+Vrm774Y9kCrr8izdHRXeGoUswiQnTB/sJnFwwrWlC00HnoB5PmO1hMhXuCI4Z/'
        b'MuBPd/I/3e3+YamxdPqZwqBFrt/zJ6bnfHhv6JfPe5SEVzf+dOH65/fqmt7ZU10StfVik3xixPSiJarfjlsbf7fkjHPTlZPK0il7TtT9c83p+qoo6/drlgvq0PUJ1545'
        b'9tLMj5a8ccznzbcT65y/Mtw5q1S8suGq01oIa5+nqvtq9fJPNP1WR5adroxS1lfaL1/+3tKpY/72/qd1NZlv135/JORG9p8+jhvt1f4r2Zg1Fc9sD/9mwpmftWMX6scL'
        b't2NTvkg8MnnuwhHDzo+uby975nLCS2vtbh1ZeOfmsULfDy2Xu/6irr/X+q0y/Peef+R71N9s4A2fH/puuYud74wBwRG/+21b8sXuRSUyXdi996qjeiq17/08oenWa0vc'
        b'Rt/blLLgeX3gBs/bk1K+nXTvlOdMod7+zz/99vd/93l+JDf2yB+FHxTxJ09dCDl77o0xH/HL1jRe3HH39B+eeS5pytDizlr3fiMaz1Y+91r43/VT+73xvDm432/zXq13'
        b'+lG1tenAgazdCf2nbBy37JmRYbHHtw//ofDUQeXvPj3VErfqvdfbty4MObrX9WZzw813Dw1rv/rl7+qy7j3z3GlTe9uXf8+affaFZsORn/Uzuy4k1P3NrbutpElel6B/'
        b'Luzub4uzF89u+sjx2+L2z9dsNEya/drXDSFvzTrX/zcFMtcvri0rXdw8tWbJpaB/fO6raS8rPvVx8c+aKeubVP/a1eUSsmzenu8NWz43/nHMlbXfqE5u6y5YderdhKx+'
        b't/2HvD/+/dzmbfLNRTtnu/z4TeIbQUFlAa9P2D27w/WvW/dtWfPjyV1zegp3bAjY3r7k6wum72a//s+xr8/1eeanWb8d9PGXH9aHfyPk/Ont/ZrskWfTPTZ1abyLfN/r'
        b'qRv39rh178wZlvVd2NsfTL3311d+eol/58/Tu7uf/Vte29jmgOZtfvd2//HldlX+4sRXfzP1xMjyet/8lwKuTRz6jbxu8Mdzif7Ny0dOlN7e3BD+QW2z/UffBo5Upd8d'
        b's6h7y1/9Wrce+t73PUnVTyu7J/1lmcPE0K+V8q8LO2u2nH/pS6LfdDxxqO8n2XNP5d2Vhl+9a2rKPLiwactda9WHr3V9dfPejm23/6Eb5Q3v3DN5Hc6RDL5Z/taIwoDl'
        b'b04Y895hMjfsx5EBr/95wYFat6OHf5336vzzL/7th5jTTpIemfrQ+/O+UG/ONxTyN1+6rXn+PeKier6i7WxzXvOOoO+Pv/ePDR9evaV+5qVjbfNLpFPC7OKMdl15DZVh'
        b'Vyuynh/h9HX0z6a8j95P/arfPwNytz23ZUz3PwIa361a7vKW0s1Mg37awnhbZRQ6ENtp1mDSTuoxyY1YsICVJMEe2Bnh4z2L3LCVLDmuFNC/lO9gxUxLSGkA1GNo71O0'
        b'5BqeIBZX3YBLWtI98KHiKz9yBTpYsRJpcFsa7etA8mn1VW/lFRzxNLPN1RFoXvtQYdgODNSX6cnW4c2sMmxa8kaxAut+/RU5TmrEGqzDBlYZluQDJY/UjinIhTDpukw7'
        b'Rhq5PpSU+sT1I8difaMo8g6kU8iLA6tYwdUM9RN8VJjjFQf4IWF5gv/EMIYcphKYryPSNrhbyB6OcwuUZJACKGSQ7TF16SSd6Q9na8egXSzTOkT2k3JSlNK3CiwocDZD'
        b'eim05fZ919kaQ193Pon5QJ1t8bOh0EZrwEhDTu/78bPgZqBUsshJOfD/dQ3X0+uKXP7rcB57TTvbPCM4kFV66WgJ0Q788XB4qOaKVl05sDorgXflPQSx4kouCPxTfr6W'
        b'udEx9F1+Zzbfk1V70Tm0Asv1XzI7Od/3R4TmKs5+Olz6c0822JVX8LR+jK7gKXHnXVlNmpQfjs8BtG5McP9ZzstYpRfCtlWBCT/LJOzvf8llbNV/Octoq4MEcRKcBVpJ'
        b'5iFiJsgZPvgr0Fo2mYA//BhBwPlSEVvGGZkg1r7JcWVPfgDOGIoY0Rm0Ns71J5lUpM5V6K2UcxdcEZIzK/9yEIxuyO+43tIzKb066FNy9l+XtZI3uvdKm631MpUybeJ2'
        b'ch3jHntz/jDpUtjenIdyP5poctxQch3KcyTQGU8aH/vuAqovoRQmTTI19OtxuFVCGr9KkiYkcI4FSJQ7uwVhFWLGMKPRYPxhlHgvwnTPaCv40qQpVHqFhvb7xymlPQ7J'
        b'yfQiKTm5R56cLH4PDn52Tk7Otah0th775OQ0gzo5WVToBw9GLN1tf4zYsQpGB4Elb6ZQ0ubkio7QyZHS6Ef25xptthwAp2R2Sr2SD9f+4a0aqWkETh089uTs8s44CB0Q'
        b'lqGb2NIWEHeiee+29/McPEaMCp13d+nwzqLDwprRb6REB4V/6PZVS6lkftOmbz+/+8cfu9/99kDjZ/N9D6h/zK78Imm26srst04mlx3adH2Bf3Xuge8+/aq7xt3hXesr'
        b'Qe/e3j4izCPg6KmvVsZcX5p2Nv/FM54vv7Ktn/++Qx/+9cv5q+Kr62rDMxPOnLhW++rNX/sEXLm0NLrrt6fj8if4be0xO9x9U71v06CktCLND/XNvx56T9f80qB3/tz8'
        b'8sgfh+e82O+Ft7Z7z/jgcNBrnZUhtecLDv568ksDD61dse+rBeXRjTHb46ZZlnRYXgq+9tPRvd8kRh5xWTmlPvv2ifXKZDvVnmH6/tN+/GzB3U/O3tk3b4znwg26FyYP'
        b'LJz4wfi5/puSOrkQpVR01+UL2O7kzMYY3PJM52BfNCkSa4iPJ5G+XygCBfG93ylCLrmZqTxWD4528qaVsUX0TOuIufeLR0aRNik04T6kicVLU7ydiTRExPnRhLsA9w4s'
        b'7vSD/RLSnAmtqONM1T3+G72ujGX1T38wb4o6qzOo0pKTmSs1U/MYRF1ZMD/yZ0Ggha3oOAV3B3d73GmJP/z/1afvZc42V/ijzGH4Ds5RQIfiRd32EIE3Du41BDQ+Aa3j'
        b'gT/p99/DHN7oed/s6OJ0gyWWuv7Z/zEP00o6eFJCj57odzuRIlJuz7kOkaDnKR0BbaRD6zheKpg01FVlHhnx/CTX3aHue9/YkZ7nYk7ds/fu6S5SsP4Lr5ag72+vvhM7'
        b'qfvzPXvq3lt19Z0Pk7O6v68mO/ISks4dSz7/2Y7fJUQ7TEodm3D37oygnF8N6TSOnZT76SS3A2e3Xk8/Pvt3r9s/95pne/R4pT1TVriZbmTfFLIY8ToJrRjo7TELaBXg'
        b'EpybzbQQ9glQF73YD1roMFI1aLGfgErYJSGncf99lmUJTtMGibTRY0tSxmjzkARDy0g45S6WoRfALmiOhsMz7he4O8BOb5a+eE50jha/xWp6JPsSKyelAPvhpILBJnVw'
        b'lTT1fs1VCVx78D1XaoOZvSXZOAKsPmtDo+zoLQdU4jb6TK9xjPwfy1D+Pd2R/qI5afVas82cKIGci0NvrbnEdwfLU5YZh9xXd0WPRKfR90hpzXGPndmSo9P0SOnlOgZW'
        b'rRqftG60R2IyG3vsUjeZNaYeKS096pFo9eYeO/ZdNT12RpU+A2dr9TkWc49EnWnskRiMaT2ydK3OrME/slU5PZLN2pweO5VJrdX2SDI1G3EIgpdrTVq9yUyLDXtkOZZU'
        b'nVbdY69SqzU5ZlOPM1twsljc0OMi5l1ak2H61MBJPU6mTG26OZlFvx4Xi16dqdJiREzWbFT3OCYnmzBC5mC8k1n0FpMm7YFBi2SPNNJ3s430Tt9Ir1KN1LUaqbEZ6d27'
        b'cSJ9UCU30nMSIz3ENfrRxwT6oPdRxgD6oJsHI9U0ozd90O8NMlLFN9KDfyM9fjPS19yN9CzZSN9XNyrog55zGmkKbZxCH9Pow+e+P6DScbzvD74P7+MPWN8PDr3fC9Xj'
        b'npxs+2xzoz8MTX/4e/EUeoNZQfs0aXFKByP1MzQJUOl06OaYHtCzqR45CsFoNtH6jR6ZzqBW6ZD/Sy16szZbwzIQ44xe5j2SNfQ4zBJzjTk0r2E5jZRaqKhrmgGItQP/'
        b'fwBeTAQU'
    ))))
