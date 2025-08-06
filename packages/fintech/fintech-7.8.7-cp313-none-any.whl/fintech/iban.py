
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
IBAN module of the Python Fintech package.

This module defines functions to check and create IBANs.
"""

__all__ = ['check_iban', 'create_iban', 'check_bic', 'get_bic', 'parse_iban', 'get_bankname']

def check_iban(iban, bic=None, country=None, sepa=False):
    """
    Checks an IBAN for validity.

    If the *kontocheck* package is available, for German IBANs the
    bank code and the checksum of the account number are checked as
    well.

    :param iban: The IBAN to be checked.
    :param bic: If given, IBAN and BIC are checked in the
        context of each other.
    :param country: If given, the IBAN is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param sepa: If *sepa* evaluates to ``True``, the IBAN is
        checked to be valid in the Single Euro Payments Area.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def create_iban(bankcode, account, bic=False):
    """
    Creates an IBAN from a German bank code and account number.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.

    :param bankcode: The German bank code.
    :param account: The account number.
    :param bic: Flag if the corresponding BIC should be returned as well.
    :returns: Either the IBAN or a 2-tuple in the form of (IBAN, BIC).
    """
    ...


def check_bic(bic, country=None, scl=False):
    """
    Checks a BIC for validity.

    :param bic: The BIC to be checked.
    :param country: If given, the BIC is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param scl: If set to ``True``, the BIC is checked for occurrence
        in the SEPA Clearing Directory, published by the German Central
        Bank. If set to a value of *SCT*, *SDD*, *COR1*, or *B2B*, *SCC*,
        the BIC is also checked to be valid for this payment order type.
        The *kontocheck* package is required for this option.
        Otherwise a *RuntimeError* is raised.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def get_bic(iban):
    """
    Returns the corresponding BIC for a given German IBAN.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...


def parse_iban(iban):
    """
    Splits a given IBAN into its fragments.

    Returns a 4-tuple in the form of
    (COUNTRY, CHECKSUM, BANK_CODE, ACCOUNT_NUMBER)
    """
    ...


def get_bankname(iban_or_bic):
    """
    Returns the bank name of a given German IBAN or European BIC.
    In the latter case the bank name is read from the SEPA Clearing
    Directory published by the German Central Bank.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzNfAlcVEfW7+2VhmbfF4EGUWj2TcFdRJEdRDpxBVpopJW1L+0aDRpU9kVFFjfccUFR3NekKjNvkpnJwJAJyPhlksn3ZTI7Js6YSb5J3qmq7gaXzEzem+/9Xv+SS59b'
        b't06dqjrL/5y67SfchI/I8PeLTXBp45ZyOi6M0wmWCtw5nXCVKMuce+GzVDhNwL4FGO6o5XBXtEriy00z3JkF/xdA33jhKqkvt1Rs7KERrDLz5VaZOCi4tRLztUrpV4UW'
        b'SQvi0hUlZQX6Yo2irFBRWaRRZG6uLCorVSRoSys1+UWKcnX+evVaTaiFRXaRljc+W6Ap1JZqeEWhvjS/UltWyisqyxT5RZr89Qp1aYEiX6dRV2oUhDsfapE/acJEPOF/'
        b'OZn7e3DJ4XIEOcIcUY44R5IjzTHLkeWY51jkyHMsc6xyrHNscmxz7HLscxxyHHOccpxzXHJcc9xy3HM8cia1cSoPlYvKXiVTmamsVGKVjcpC5aCyVJmrnFScSqSyVbmq'
        b'HFUSlbXKWSVXuamkKqFKoHJXTVLZRXuSlV4nK/XM9hhfvVIvL07lOU6rvMa/K7g4zzgvP87nJXcLuTkib65QYF6oFKbnT9wzK/jfgUxVTLd5Lac0Ty+Wwfc980Tc+0Ky'
        b'y3nFx8LtOf0U+IpP4JqtuB7XZqQuwTW4Ed0QZChxY5IqM0TK+S8S4wfF+ADt/nq6lKvKdwMB8izds1ScfiXcXOwfhvvNrZYkAouGJFUi6g3ANcHJabh1qQzXJqqAZRNu'
        b'DsK187dl4KbENNz0SkBiKm5KT81QBUBTTRiMtSQxWRUQkpgULEDnxFwlqnWajg4t1JMJV+Jz+B7wZkyMLIBrfdiSxODKySm4AcZNxXVJEm4DajZfhXfhhnzBhOWwNi7H'
        b'FrjMtcqBJaE7JYZdksIuymDvLGCvLGE/rVU20daGXRJkiyfskhB2STBhl4TP7IcgTkh36YW7pl0qen6X5C/s0lm2S0tmm4W+I3Ily1ycqV7A0Zv5dqLkAk5Gt+5OyDZ2'
        b's63YPLEOBuLy8lJvSJLYzXc5SbJAaMtx8/OKo12Wc2e5Ygu4XbjKzeuJ7DPY8Y/9Pxdej3hg8ZmgmKjCJG2HoM+MU4TPaJj3KHJ9rANHb4e6fW6z30YQMKbYKPvGddHU'
        b'n3GjnD4MGtBudBddhR2BDQgIwHVhiSG4Dp3NDoA9bw4OTQpJTnPGBwRcqY35nDD8QBmmdyK96uc78JPRDkvYGdzBoQOoA9fqyfzxgzRcw0/P0kngez2HajKX6B3J/fNo'
        b'ZzFvP1NnBt8bOVQ3Cd/VuxJWvbmokcc38HF8nTzXwqEG1IXa9S5AJYNm9PK4D+9ATbCw+BiHDqNWL9o2F9eguzw+hVpQkxDajnPoiA3up1IkV6Jq3hHtriBSNMNofov0'
        b'znB/K96J2njUixrwZSk0tXGoRaFnU9qJ9s7i0bk4PenTClPEF0qZ6EdQtSePun2sSJejHOqUF1IJ8CV0E/Xxyy1wPxGuHZihK/gaHQmdxcejeXxrHWogTx7iUJcWnWL8'
        b'dqVm84X4rpxI3Q3skvB52jC5AvXzi9CBjeDZ8QEONaEuBzqdlSWh/EbUasOxDh3orj8dZClYUxXuL8X3rIgAvRw6uhw1UV5LiQDyxEV0H85DH3w+ijYsQrvsUT06UQR7'
        b'J5Bx6CJqW0MbVnqu59eja/gK2dO9HGqWol46+hbXzbh/7Qa9iC3yfh4dY1O8pneXL0XHcR8Z4xIsP76JWmgXJT42h8/C1zcKGa+6laW0y2a8B1/k9egevkEE7uRQaw7q'
        b'pOsfB0Mf5tEddNbGsJtdqRoqWKW5Ge7H/Wkycv8khw764RbaBTeXSHH/q2i/jAhwhgjwhpaJ1hBUjPvRFXS3UsLGaY5DbbST3Tx0GpoeoGuWUtbrcEYgbZk5A8EwmZVU'
        b'qXuAG7oMm0k22gJ14d24P2k1vkzEPgEKj0+iBqa/LegGuggcr24wJx0vcugYrP11piEH8HHg0g+assvcsErHE2ypjPgW7pqP+3Wo1pysbB+HTmSgA6xbD6j1bdw/C+/X'
        b'G3SudQ6+zfT00qIsGO1+tJWA9Tq+GvUxveopC8H9q0pxP2k5BwuV4613Jw3ncBNqgk4tIHe/GdOUI7BxPbTfLHQfHZSHvYr7DPIf3pTH1vdBIDovx+02MtJwnUOn8CU/'
        b'1vKGYrEcX0jEVwi3ayDEPBCdzuoM2o+vyGG5bmyQsJE6S3xpUzSq08nRXmt8nSziZWrK6Cab1JFts+XgiC7j62S+/aDIcalUk2ZkZMvTBfi6hI1zbAPeQe+jExuW8/PR'
        b'tUoiWg24MWemYXi/HNfK8VV8iRez9e5YgatolxW4r0SeuMWCjHCLQ6fR6SK9B9Vj6xhUPx23oGuoQcKJ8HEBOp+RgQ6hy3SHS8ICUP0GvB81ojoJJy4SRKxDO4T4uN4L'
        b'GqNSCgyNkUYG5qhRmPu6C6rGTUqR3o4IVY12r8b1sM1lnM26sqhUvS0Zt6YoOQWEXMPlF63Bp4r01L4PrShMAQkLuOmbClalU8Fd3afy+Fimaaoc6max/mRBAd4HbvD8'
        b'dHRWok5DjVnb8Ml18ejEijQumpegNnRTTLfYDt104YPQKWoNtRzag3pD9EoCLkAL77pD0DWwuYjb8H76NRqdx21ibhJuFJsL8TG6Tf5zcQ/vXICvCpijbkLn0Rk9gZKo'
        b'ySn+dTvGBV1HPYRNIrpo4oLuiUXoFj5E51O+SszjM1pT8ODRDsrktWRUNw/tMMrSO0GWC0yWvWIpfhDGbGRnNj7Pg87sRg3EMRzhYMOaAvWBNKZAh3u4HdRgXyK6AKtj'
        b'YhVJZANWISJ80wq10tVZ4IP28g54l45ozB4OVaPW7fqpZHU8TOt7ka4vurtOrsD1qOcVBy5ZYWaH7smTKukWuwet5j0VpqjnaqEPpXESV4W/uLboEgAz+HOOiBKikyze'
        b'WIEvYeafZKgTXeLRTfyGKVR6qGiodgNfX2WaUKNoDRMIncBdsOswVAuqg41PxDel+Nr2TGYOeyM38S4Aoq4QogkEgt25rZ9MMA/qxIeM7JSoyrhl4izOA/eLcJ/CEP56'
        b'8FkzfhJusBCy/WpL1OlnkIY66F8/Yc8bn9+1njTC/EKadA0+PC2Nq0CXZOiW0py56P2FABRWoH2oTsxc3CFU70ZX7RW0G98hkl007ZwI7cW1uA3tLgQb6+Ii8FEJ7luG'
        b'mrT4Il21/Hm4hUcXnMcxRAq6T5VqtvdyCMo9zygV08xzTDP3ifDdWfgUZTM3CdfzcficNZlqF8E1bWgXZSPH1aU56S8zk7NMNfeIzXAzxASyZOvQLXSTT84dBy1+GrqF'
        b'MRCiWvE+VONl5NP4nFDUXKK3SmBzbqxnit4I/vs0L4ceJpwzC2Iv4Zecic7gfSs9DT5gXMHOU8bRTNkjcbMEdaPL0VQ4PT7qwaM3fEzYCB/xo1PE95fgllWvP2vExp1k'
        b'k+wVy8JW0O0r2bQV0A0gMxOOwlXoBhUqB99eaXJLRh7A7wKbLDXlEHCl9riVfx3voey06MIMfjYwvGzG4vV+iH/3qPuFMXrxXZAYYIcJmnWj08zAunB3hHGwc2QwCJWb'
        b'iaKg3Qp0HMw0Dd8zQ/vzIyEU72Wx5vZ2VMMDVLlqwnNeWxgWbsXnIATtKwI5JjhVsDH8xoqA6WwReHRUhhsglNaxSHhpGt7NJ8MmmTBgUaI+knCDaIkvG2U7/4LxG9bh'
        b'gATwwk2ylifp9qDjqnJeZsPi9GFQwXx0ksl9uALd4F9BR024Ee+fpA+ClgD0hjko1X1816DjVGwSCeIVcJ84qwx8xCwUN65kGP2oazK/3s8EzvDVErqYwfqocffyjNBM'
        b'G8RcKLojwSeL1wGc3MH8y1VfiLSW6OxGCVODRlSLrtLQgt6IxXfLIAoyludeiCz+InwHcNgZKpPfqkg+BZbGhAuXFrLAUoN3CFGj+URHziyllzDxwNdFsMiNG+gSrYRw'
        b'cI2fBtmEgGHu/XngVYl79p0dwGfMMSHLpcyj4hvobBHeNwd0Y6I5nn3eHCskgLnvzGXbcNHWnvdG/TYChkYPgWWd1/sTbrdhWS6ia54TXRf5Zow5IhG+5O3P1KbdPo5A'
        b'104TqEU7vehmgt5fxL1oH75pVJ1LL9rhCbHZUgPgcgUnBdjUFx80oeBYdJxqIG5aOW/cYzU+6yLE6IplWtxCyymodyqnw20y3FKxiSHabtQMYLx/Pj5sQs/4Mupibrup'
        b'BATfjB4wENBNoHBfFt2qEkiudgL62/1CzIxXSAD9dUvQUYhRjI8DKOtegKSHZ1uSHT9FVuBQmj6c5KqZEND24VaPiao40eNSxx2FD0ogKFzBDVR/vJdBAtkfoDKBeh9f'
        b'ymwWJAFt496Ihd048JpGdiJYB6t10wRLJGax+PxmNsn6VUIA7X3W46nAddDqEJrHWvml0KgGHJ6zNnRCjC5BBM5CjWY+0L+a+a/rHgtgorshflG0DFPtAuowRSqQGBzE'
        b'Z54L6pRXPTCKQtckgGWOoqYADY0FMPVTr+N+Ca62NmPo9gRg6DoKVpxe98M18uftJJKtlge+DMqHL7HUYyMAaty/DJIMGlGuABiWont6X2haH4vumPYvIXECKJiEdoLB'
        b'Ohcz/a3dQlyeEp2vEDJTa56zlUWRTnwlBl2TPRMBJloB2iPCtzfkMzZnN8HaROH2Cinzdi1SSEoIts2EJesyTaZ9q5GLkKCTG8Tmz4Em0ezmKlh9PTy+A/bElJ+h47As'
        b'VJv7c8G3Qi6ID47nZ+3oLFvPtkLo1O+Fm03ZGe5BDFKovfApwhX3mvKztNfoFENQhwO6sPhFl3SRLXUfWepeY5J6p9IT98fOMyVyMPht6un91NHA//RUvcGQ9uLW2XTu'
        b'ZpV2vqjb4EXOGdmjq+Nu5Kr9HOaM9tgDzu2fFkYjIwCNfag+XR9FWm4B0DiC922G8PkCZLk4AX5G4C4J6Pc1SHaIaqwD5AWLGRaDrxksqXMJxNpwithQ9xyIJ2cKJ3Bk'
        b'E++ZyPBVCYCBG7iXoccqfznuX4BuWQnZ4nfLM6mfwxeyEcBPtAtmOsGOiLcwRa3MVLMZcegcizQ7wFbuglXtnmLKfHUx1M8lgg3thC7XcdtEl9H7/MpFoQcScG3HwPbo'
        b'5l9CVSBpP27OtZKwjPSEB26my+cEbqPxmWAozDdIZwsj3ZxuB+G9D9VME6CD8y3SgdEDuiHzVwbDnl5XjefguMqPRgd0WmCueklCYvTpShG+EYOq6KKV4jt5uH974Xiy'
        b'vmkx9T5rJqO+F6CVEe0ZEIVeko12l+Nd7nSS8/D1Cjm4u0O4T8p4HQLf3c9E2js1DKBM84uKfJ4p8i0RvuJfwVDobVxVIQeN6hgvE+BbGXQrp8CK3IARdrwUOhrSyAdi'
        b'az/cR4Pxa8IE+ZLlMilL6U9KSyheEHqBFV8hTJ73YBeYNBdFEF3v4f3MRZ/Ae3CTfFPmeG1iD95JfaoEkpzzIFLTtOdQ3ATFCjaLQX0xhvLeghy5C75QaYhD+1BfEp1y'
        b'EEyhVa6DMGWqcsDsz7HlOApzPSvHe9BOUz1hI0RkogM5S1GvnCRXGwjHs+BkcI+C6XwDvmahGc9wX7Rt4hwfgOX20Unml+MWObSd3kDGOM+B67gLYIMY40yzZS9XT9S/'
        b'Ajxz9bpkkP7ECk63HlKuLaiJAb8DyQvk+LKVqTKTMJkCP0g1ol9aAZDYG9KtCxL0Bq4FZFCNTjHjOYmvhcm9IKKPV3Mu4k7mKG4oVC8k8eMZIst60T4JOol6K0WY4Zgy'
        b'vD9KjtsBxZpKQKjOhu3QbbxjgXxLyngVaIY1KySIYH3C3ayJCtzlUM+rkNBT59cPQQEy040g5UvytYnO7xiAElCq+/oI6JcAuzZhc14AHhcl6CrurJgmyJSZTQebb6WK'
        b'mwfJ+qEX8kt0QbIG9iKNi3SRhIODbfBbSIPHFtQ/CbKeZ/ICgwqwIge6IhYvgQ1T0tiGz8mj579sb3qZWdWJZegcpLoEAcSGoB50ZftLXAyzwVkifG+rkEHDmxlEZnfw'
        b'9s85k+ecOYZtOgQBtFYpo0uuw0dt5Dx+w5rExPsASCom0+0TQoB9Q74AA1I0GOQxdNmOqsp61IA65BCQqwGEkKHBeItRL3UFczZtlscFmwvZBp4p8qQbbuk5WY4uQGZg'
        b'qGq3L8VNrH4Mo1yWozuoylTdW4DusDjbG4sPyktRP28w1iMrDJEDAuteAahDo5L5wHugvPop+hhocgSHc4poCqoxFPhQr8EsUQ2tCIpRE3iE/mxUr+JeXS3FRyEKHlSK'
        b'DUcXq61wfWoybhBxInxf4ALLf1AFeRwd9WpMeAqug2hwI1XKCXMEYfgEBBdacHyQiqtScFMYLHQfH6Qkp2SWtiInfLSAVeJjooLSQxLFnHi+wDsXtvcQPpRPzpWMH3Ki'
        b'Qw+bNsBlrtR4/tnGqQT0BEyo4ugpmEgljzY3nH+Js6UTzr8kXpxqwnmYSvLMSZc4TkLPv164azr/WqsUqmfDrlnEk9NaXqEupce0isIynWKDulhboK3cHGphkcQOgwPX'
        b'l5VWltGD3UDjUbBCC702qLXF6jXFmmDacbFGV2JgxJN+FmvUpesV+WUFGnocTDhRHry+xHjMrM7PL9OXVipK9SVrNDqFWmd4RFOgUPMWGzXFxSDFzHK1Tl2i0AK7mYrs'
        b'InaiTI6a15ieDjU+tEabP1MBYq/VbtCUBrMnyeALkuKf4a4tpRIq4JMPk9NsqiQiadT5RYoyaNCZGFL5dJsnMq00igBL8I/5VZLDcgOHUEWanq8kMpM1WpoREhUxfboi'
        b'LjUzMU4RaehYoDGNy2vK1XTQQPItUKGBbdGrKzX0jD0vL1un1+TlPSML42GQh60O3UqDbIql2tK1xRrFIr2uTJGp3lyiKa3kFXE6jRrG1Gkq9bpSfqaJs6Ks1KQIwXA3'
        b'QV3M09tkcTZqeRD0mfNTCff8+aldegK1hkzIMNv80T3eVLDSr6dHo2YRrhyEm/Dw7O2r3iybzVH/lIp3QKSpz0d9QCznllviPfThXxfJOeAmy9uqKe7VbWGHq16brblJ'
        b'kELbmldYXo6bxNHxopcnokMlvKnKAoj9hNKG2nTxMvAN5/EbExo7cBUDBAcBgbSBo63iTcd3EaiNymS2MgjvjeZNx3er8B7mP7pwcykEvBu433R+hw8DECdizPPH581n'
        b'ycfP706j3axAdAK1TI/wlZeLWG7aXgz5BI3uPSU5VlJ5hSFbOYguZdH7YgmXQdbEeOA3GbFiZ9HkVyEPBTDIS1nysBffNxyiNFoGobOW/PhZIAjWSJtewYcicWcoIEjj'
        b'cSCw7qaCrcpMwacBI5qOA1FjHBWgaDW42Dtz5XRhIDIcSdjOBEDNcrR3Le6nkzwI2V+CoUaHdxcEluEafqMZq6k1o9MA7qhb7c3GHVvwDd5UvQL82qMUMbkv42P4ENo7'
        b'c7zV11DZnQ/opc4eX5sw2MplVOxtqNd1Azo9YawzU2kXgS+uQrsV/ITT3V5vpZB1AvioxPUT2mJltJOj/wpI/tr58WNf1B/CNNBRyllynG1LnNoy32UtR+PfKtek1YVR'
        b'4cAE7ePWbEH3tK4zxzheAetuFz+yLetyFg63bHP4cfoK4XBt7y4vkTz/gK6y8JPQrHmKjffQz708HryFvl1z7fLv6/dtqg2+9/Rzv80rvxEcXHvz0D3hl9nF7pJ3zt75'
        b'82D5p4//GMOt3fdZQ8n8Ms/R6M11py/8KVr4gSQl75d5dYWfDP7pVxvmh/ivXtu+6YtPrr63etujivsbLBNyf69v/LjpeGpiAra79Le/Dv9XxZWVk377s6l/dzq+6Afn'
        b'Lb4pql7ZVL7W7obXx+8tvhlj93R7x+8/ff+TDXzgGwecHP/XXOcl+qkHfbuT4xsez+gM/v0M+4BLbpqHP33tzZSRL803bJs3/PQatzniF47fJs322fFFddhvLFTV7n5z'
        b'laEf9C31SrlxcKN6dt261nMriv7jkVfef62a9FFI7ltxbbnf/jBptqf7UqXZE1peuYt6UVVQSEAi3q0MEXJS1CUM2YpbnpDTOdTonhcUmhQcqAzFzWgfvhGMa8HeFeIc'
        b'3IF2PPGkSAgftUjJCEG1GegaPo3rIFrLlwhxE2D73U9IgQHdyptG3qgJDIGM8WCoAIbYKYzC3aj1CQF0U9AeB9y/lqQj9KWWjeyllg0hgbguTMiFonsSgHG9iidUQw8X'
        b'TsH1acFJAWG4ieOk0UJrDbr9xIfyOYUOpbDOCFiloq4ZFFo44WoRvjnLVSkfFQYodfYEhX2fC0/eTVEoqoyfUafZhbqyLZpSRSF7OyuURMa5oxbU9+cSQkd0XEj6XgdN'
        b'/LKK+2umhHN0HXGZNOLg0j6zdea+2TULP7SxH3F2a9e2avetbxF96ODZ7Xcm7FhYn9+wb8ygb8yYUOw0ZcRjyrBHyKBHSE/BkEdUH39j8+XNb9q/uXQoJmnII2lkcsCY'
        b'iJuULHgs49wnd0f1mA27hQ+6hY94KD508Rrx8un26Y7rKGpZ/KGN84i7z9GQzpCDYS1mRIZ5rfO6o4cdAgYdAkZcvMY4gX+m4AtO4Jop+Mjbb0xCvoxJOWf39tzW3O7s'
        b'YafAQadAeHBg6vQhl+kj8IiIc435yMntufbu9UMuEYbmyI/cPI96d3r3uAy7RQy6RRCpHFw6FvfMHZo0A4gvP7Rz6vDr0HULOgJ6QofcY8nyOLt3RHbEtRTVLB6xce7Q'
        b'Dtn4k7uOnh1rBx2nDjsGDzoG92QPOUbWLPrQgaznhzZuIy4+wy7Bgy6kwSVywDbyI0fXDrsO+5bEjo3QqcexR90n6HEbdIxsETx0CeixG3IJ6qkcdIkasI36cmyRgJs0'
        b'ddhj2qDHNJi/05SHRHj4+xVP9v4tmykJ9twP7W0Tpoh+6CeAKzlV5JSWo2Kyz6MiwDujZgaEMSomUGHULDdXpy/NzR2V5+bmF2vUpfpyuPOPVcyS5EHwMaqZjuYKjsbL'
        b'AfIMOTP87yruqVYsEEz9CweXj61d6tdXyceEEoHjQ7l9/YyPxTbVaSMym4cyhy8fSziJrZH6iicu9JA0mLsgjxGBuyc42g7tCEsBE8H16bgpI0nCWUNCuMcjFt3KopVB'
        b'm1W4LyUV2lCXJ2DtIAEnXyHEF/Fd5vhRr9iHIPQHeL8BoXPb8o0vVZKP2IhJ1hGYLWQwm4JsDiC2NFpsgNai7AlAuVQM0Fo0AVqLnwHRojgxhdYv3DVB62qA1psEBFrT'
        b'1x8nYGtdWYlCbUTJz2LjZ3Ewfc3yu2G3TlOh1+oYyCvX6AB6lzCkaXwPM9QiwwjTYMDALOCsLdEs0unKdIGUgRpaCsaRNZGFiMLQ9fMCmiCpQUj21PMST8TfCcXqtQot'
        b'Q/j5ZTqdhi8vKy0A+ElhOF9Upi8uIPCUoU6K9RUM648D0UVaMoVxfAv5hVoRGVKpLwcMa0C0dOYAswPIE8GEufKfwlJJup68IZtmC3rzkvcYa1MDk4PRuWz2SiO5kZGa'
        b'lCbg0PmY9ahWPiME78zWfpNXLObTgctAzMr+/M53bdG5tziB8pGl5WBDpnV8+Anl/sPvuiL3t39SJVjQEd+xszM1/umxyFOplpaSBp/g8CH7Hb+2a5iaGmh5zDLQ8pAb'
        b'd/NDmWZvilL4hJTwvXAf6pIHgsLjWtyQpqeBaCV5S8Ib9YvxpezcJwqi/rWQknelhCbj1goISKgRQg6NN+7oqrg0UaqU/hObl5rCCrX2UTl7X5cFEG9jACGLRQJIghnn'
        b'6PXI2Xdg8oIh5/gB2/gRt8nDbmGDbmF9spv+b0YPuSXWJrOg4uLRsmXA1gfcfE3KF2QXmM8yG5UZFW3UzKA+OhJUdW7k4v6sdGbMIxEBmTPyNl6Gjc7oa3BG66UCgR+E'
        b'D4Hf93VGB6RTudPyCJF+Donrbahm+wuFhLNwuxpdQQ2oO1i0OiUaNVUAWDmN7llwa/BeK3y3EB/WohYGbI+UuMk34IYZ1gDTIX2APGMP6mW1tna0E7fLN7grKkhbDeBK'
        b'QCLXGFJujNrE4+s2kWJOiPcKMvAtZ60vOxtowWchVYksm6ETcoIyDt1Yhq9Sx7ckiYz0wHGDFLjt4nAXupILLpU0eU5WEJd4Al83uMT5uJf62pWLcDUrWYBO7x2vWaCD'
        b'qSz/6S9AfUHpqD8LNwk4IWoSxAPfrmf8qcxoTDpuvGwB/lSiMhYuzMGvWkTLTH5V+m/0q4XgV9UTSxbUmTxXsJjohYiXIo+8vFDwHXk96fA/mtbnF9MheU3li4n8c4OT'
        b'uZXl5+vBgZbmMyGMqfyizDhFPMR2HXGqCyEY5FeW6SBRL9evKdbyRdB5zWb6pMGZx0Oyr1MXUx4LwAhDJ8igJguop2/+By6Nzw4Mhj8LF5I/8RlZEfAXxAhcELmANsTH'
        b'BwZTLhPkVRfzZS8tPJAJ0LUqZ+UG4FRAfPrmclgQwuRfinImLmXlLLiRnv9agPu/r2uYMIQpgNikJ+hnAuGsmP+vBJCNnuMhhAQQdGsJTSdXxZPqx5uONnl5s1MqFhre'
        b'K9/qwPlxPZMEXN6q3LU6Tm9PXcRCtAfVk9JzPSmJBEewc+lG3IPO43NoB6pHNagG/LWDwDwtljL6Jp1URoriLMPzgkWVGg7SXvLKIuRHfZFRHFewnYvgIrYuZ69i1qP7'
        b'qDFKTF6hPspFcpFrF1IekwNswQbfFFuX51mKsiOMPNyL/aPIATK6Qng4LaM8ghPJSZwZh6twJ5fJZZaiasrD2ZKUbXrMrG3zLN+ycuGytT9cdlbMvw9N3Z9u3NaaZr0z'
        b'3HZX7spuhXv77c/3vP22vO+tz3xGI7r6fB+XnViZ8ettp3bZi1Bx192/ffj71K2yeYr7i1Qu0kduFT8YOHt17tFDJz+pd5i//ZOmHatic764mn7rSovloiTlg4NJVl8I'
        b'N5snZnV8nqz90wi3uOez5pXnbr6e3v5otPHsOwOTQmYmbt+youA3uiNtH19b+8HgfVVhwpKh0ovWW3S3Dnzg/acG54dv/yhw8glHpyldMR0rfT/4uaj22K/e+fC9bd6X'
        b'Ws0uhi3ZP68fXfnDoz6XlEfLnnwp/KDLd82bC5WyJ8SZFuFT+EHQTHwRslpjShuDe56Q1/Yi8e0sCNy7nw/wxuiOzk+jael8Lb4WRLBvMzoIuS1JcMPgsRDSJcWMi8Dd'
        b'0iR8Eh2keTK+bIOq5Sm4QZmmz0LVBoZOaI9Ylo9bn5AdmpocrcPtkCiDd98giINY1/GExF18bXMWroeE9TiuDcsg0m4XBuIDqJZl5yfdluP6THwWEIYx4UW3cTNLvXfi'
        b'TtSYghtTSHpOU3MIl7ttwkVrdSql+fdLcklN3JTjMkBizhJacOa6ECMc+a0BjrwGcMSFpGb2Tu3KVuW+oJp4gB4fuvg8cp864J8w5L54wHHxmFBk5zPiFTDsFTvoFXvT'
        b'YchrTsvix1IAMh353VHDDv6DDv4jHr5HZ3XO6ubPbD62+cTWYY+oQY8oyCA/cvAadvAbdPDrXjrsoBx0UMJgD23sW6LqN3VE1m/vntytPja1J/5EyE3RA8tblm+qhmNT'
        b'BmNTiEjwVETthg63IRvf7vwen2OFfeZDU2fQZNG5I6qjotuuI7Z745ltx7adeH3IYzrLyr+EJXX1hRTQzuehhwJSQDufr3hSYrpqFx/K4VCL+FkiPFMAV4am5Aw6EXUb'
        b'FUFUeRmI+s5qwguZXojx8qeJ4Gq5mUDg/QTAlff3BVdd0kDunHyaSCmgvmp2etjEgxZ8MRyUuglfeuaXQSZXu4Zj6Rr9ZZA4Wmj6BZDo3/gLIEjTthyxyGLx4TsylUKa'
        b'dFB0MPFw4/9VevZMIBK9EIik6fq5xAo70UF8+J+Eot3owPP5DAlGQeynI/jmQtTCV7ijG8YSfdFkfTAJDVV54G0yQnBdGm5YimtShfgKemC/CJ1Fu9Ap1AlflFymrRm6'
        b'7izQCmMvc3wm9Nq2dmt/fhdkRT0vy4psSVaUeqwyVJR5xGnp3A7zQmGd1R/KNxf6ebi+ETUlNiJNpq46m6n+qFjA8Y/MNcG5Sgn1nIvwHXTipW5TiWvAcwbhy08IcHbF'
        b'V1YHhQQsiDf53gx8lbrJ7XboeFAoLNcdQ0lxvJx4FNwk+YFicUCWPCXCkXrSiW4UVvkOrSZ6BlSwaiOrNOJq1EWrjTekSuEEKyPOyujHzNZqKqkXm270YqkGL7Zd9nxS'
        b'NV6ee65K9shZMeATM+QcO2AbO+LgOewwZdBhSnfBkEPQgGWQTsEZsyyJjqzBS1MqkgxPSKimGy+uYIV8NHz5G4hUIhMI7L+HuX9BzH0vAP3j8hDRP7VnsYr7H7LnIrDn'
        b'LRZLy4u1lbzJaNnJGFipgtwt1KnX0lMvMGCj4asV0S+tKVgExGeo0rOzlgcr4hMXxacsVaUFK4BbSm58xsJFwYq4eNqem65KW7AoS/nPbZXCoelBZpwlN2Juo8izdCr3'
        b'5/SxcJO8/3yd/F4ziPx6sjZ1SSLN02iOhvcq0VkL1JmImzfDnyRUu5lDh6UWqCYkg75rhmpRU9LEzmCk1M964fu+uEeMjuNDK7Wq61MkPBHxZtIfmGlOevtHzAp5GR8e'
        b'Hz5ZHu8VHxAv2zcts8Q3RhQfHZWqqTEP36fMfj0wX7Y0QBTU4vR2nXaNLCp1tVd+wAlpdrTkF8GF1cuPNcT94eZ/nEJvdlpzXzXK/yytUIpZpbx1ZlbQOP5BPfhKSJaC'
        b'mpBkYynDKtHxz9iYyJ9ijpmAPm7QIrsBcehRk/VifJI2huDzk1MoEAqQcuZW4a5CdAz14x1K8UuDHdkAk8aPWkAOxhsKHHONtpjLbHEsx5xzdDUZ34t1YGqA84ac5w/Y'
        b'zv+ugjA80+015Bw+YBs+4uDaPrt19r65A5Y+/0fmOdd4CZhonmnm3888deQ1CYjCpLCE2lPELAwD5G/Eu3BzGKpjfsz9dXFRALr9cvstJPYrNsZj8jtdU+n032vD5K0E'
        b'J1I6nRiWaR2yVF1CE9SXRGOSnpIz7XIN3ICoHWqRxCy5WF1ZCdlmvhrC7LOMaJBWF7CK7Av5tIUpn/5n6TRLpf//QAMyhgZs0ZXJRixwDu/+F2ubBAvgHnybOqmMfMhM'
        b'N+2RAkp87d1Zao7Vh/bhPrwf79g2fowPDLrpW05T3IKfwQjj+MAW3xiHCMX5lP2nRVLOMmAd+UF1sPu2WE4b+5OvxHwZtLg1pbNq6smX4YYLb9sKf2MWtXx5RLifRST3'
        b'F2lEVB5XneykmFXjtHSXcv97GvG7/fnvmkXh1PkVqVs9/FcdkbxTEhxQmi9Z3m6mc4s5feuYpay94rSI+3WlNX68XCmlsAI9mIb7XgoryHEh4Ar7LU/o7yFq8QO0l6Zk'
        b'LB3LoEcXqBk/wE3gztIkXEy6dHvxPOqnNqJLuDcoDJ2fkAKiPbiFJk5z8C3UOn6u2YXeMAERN3+WWvXhGn9DQhcSaIGvjHtJbxcqdjw6vChlXAyjCN5oL+pDfWJ8WO0N'
        b'zuY7swDibCbUfi0pRAFtJvahW2z0jds5Q/HX4jmcQjKhWUM23t2RQzZT6AFY5KBLZN+sIZd5A7bzPvJSDnuFDXqFDXlFtMhHXHyHXUIGXUJ6CoZdogZdoh65+w1MmTXk'
        b'PnvAcfZDjynd64c8IvsiBj2mtcgoq9BBl9CeTUMuBOpMcJ1mo3LiuXPLdBRM/cN8h5WPJ1S36ZzoZabAkOGAO31aAe7UjZSP3b5vhrNf6sedlIeJlKL09ASlIEEpTE/Q'
        b'vtVVKeD3wNI57I/d9f6elfbqSWZjT63jPuKc/FfEul/PDOrri/bYv/yVz+8F/Xhn8OLlLVb9JVv/fOXe8K8ePs2ZcbX7zCeb5278899/+PWdrVXWuait3P9qtf/Hh+0P'
        b'L4o71h4j+w+XJdWzu6+mySJcHTq/zvzj3YONowVX2wZ/1xlgUfibDruR3raf2FgMHl1e/+hIk217gGXn8HstvlEFi/s3zM/v/em5XT8+556182G6Mre/6oPzJ++OvSn3'
        b'rusq1g76ZjbsPSmcl6x1e1crCdQ6Ca+6T6u0/vTninVaz99pRZ8O/m3ZfJfjraFozW1xym8jq4scurTyA/5Of+pf8NeVteGN3W0X0Tr3aZ8UYffbzn+8Kvp9kf8HQ1aR'
        b't+0OFlke/K1z5WDvZ6d/WfDNhicDniOd2Ws+Tb8z8GP9pO6Zlrc9thZ5//Xn2z4783VF1dT//M+kv90101Ryez5Tz/ipYvdn4Qmf2U06dSI2oXly20Nlo8Oq5o/95uwa'
        b'emL5w98uTx3gYzPCPvK953cp7MefOT2ssH/1t9NWnYkp3/chKtmy+P6dO7qvthaWpMZxTx9zNo9lzY/FGY8vvOO2NKvr4g/ki96ze+dQyqJX220/OWebvz3+v/37ffe5'
        b'TX//ZlBMf9ikJWcu/fyPP12X0Wbb1eOwqbTHZ8/mxZfq1t+atrvr79fX7/75j/iMp5Wncs62j7XbtXjPy1koH8MB0x/tLtzv5rQ75g9v/nhdxO8mqS6Y9/Kjc89/0Hy2'
        b'x2re8uXOrzz+nbdT038PfXxt2up3/7L4ZzGb6jduarY59OvJX38buerRsf372jwEH369//Wj+3/5u50/WzIlasglKmbtcfQgclrh9p+2d35eEPUg7el/Wh4pF9z/zR9/'
        b'P8nuL5/+sldr+/e//oG/3fubQ397tejGL+rUP5j2uYfVZx+ELDMDF0fgxozoPHBU+9H9VAEniOXAg+1EJ2m6sxL3z5dvmJPyQr4jxDuf+BFHdCYOHX3OO6LjclO5Cu9B'
        b'9bTmNXN1NK4HyNYYIuWkOUK8P3sy7kLttMaE9i1EZ4KSQ3DN695JqekSTo4uC/FhnSeVQa/HbSkkYoUsTICY0pBE2i8J8Tl33KSc9P3el5B91+V7v3XxUq9CxFUYP/PJ'
        b'p+qZD3Omstzc4jJ1QW6uLsPoSG2lHPd3AJkJAs7KaUxsZu5CPGhk/cYOn/rXOvnuyG71sWkHt/QsOfj6Zb8+3U2fy/qbSy5v6g99a+GP7HHiUGTqI1eCSNWd0w6adycP'
        b'uob2uQy6xg7MTh90SR/Iyh5QvTKY9eqQy6sEgdrvKx2wpa9ALBOMWXD2ji1xrU41Cz6XSt0taqzHHDl7txE71xE7j8dmYjeLGqsx6zSBk8WIpe2A/ZQxEfn+kaVtS9iY'
        b'hHwdk3JWdkCYUULGCHNKWDBCTglLIAbsA8asKGVNKb8xG0rZGtrsKGXPujlQwpE2hYw5UcqZUlPGXCjlyh50o4Q7IzwoMcnwnCelvAyUN6UU7EEfSvgyOR5PppQfa5pC'
        b'iam0STnmT6kAgxxKSgUaxA+iVLCBCqFUqKFfGKXCDW0RlIpkA0RRIpoR0ygx3fBcDKViDRLPoNRM9uAsSsxmxBxKzDVINY9S8wUGJnECSi8QGNjEM3qhgf58EaMTBAZR'
        b'FzM60UgnMTrZ2D+F0akCNnYaI9MNZAYjMw3kEkZmGciljMw2kCpGvmIgX2XkMgO5nJErDORKRq4yyrWa0TmG5lxG5hnFVDN6jZHOZ3SBsbuG0YXGZVjL6CJGR4xpGb3O'
        b'wH49I4uNq1rC6FJDcxkjyw1kBSN1BpJnZKVxbD2jNxiaNzJyk4HczMgtRsm3Mvo1Q/M2Rm4XGLb7dUbPFxoejxOy/RYaJI1n9EJj+yJGJwiN+83oRAP9OInRyULOwXfE'
        b'fsqIvZJefYz/Tfl8OX2ixnxslZDz8Dsa1hn2gXtQbXJN/IjrlGHXoEHXoA9cQ1rFLYIRV8+jVp1W3eoh16C9kscizi30I8fQPqdBx+k1i0Y8vY+u6FzRIxnyDK1Jasmv'
        b'T39sznkEgzewsH1obtuS38H3xPcVDJrPeiqcYx79BUcuIs5iNrnYjomBJItAH+6Y3M33iQfNpz0V2pm7kgemG54CEozXxa19Xeu6AZ/sIWdVjfwjcxsywNLuyT0L+5z6'
        b'9DdfeXPRj6YMBGUOmi95KpwKDLipjEuWwMAGaKLTBskGzd3/IrQ0DyaNHoYngARPM/EBa3PfiQ8ACe6Gibt00NznqdDefAZpo0/ZPhYD+eVYvkxgniR4aO990nIgJGFI'
        b'sXjIPnHAMvEr+tJVbdykJE/uHU+HpHBDYd92VAiR41+s5v8rQct2HAo/G6hoeKIXklDwcw2YOF4gENg+BUxs+zm5fF9gfEQayl2UzxBpD26pEvI/gDu/mJytb/mpxc75'
        b'jqMrd/35v89K7Jz+uvhsXP1f/+tKjqLo402v7rStXhi+02bo6+nRdW1Dxe9ZHtp6P+rp1fe07+m+ESf5HTomrq6O+03B3Vs/eLsoqcWvdFj52z3t7o2pM19dtWCK8Aud'
        b'Y8ryyD9MffvaKwscEg6E/v1XoXafnaw9Jf9a9+W3y++sKOs6czYqxbmsv+X4fLM5k3xwxFc35zcFWYbPtjzZX73nTFHyjb4dxR/+5E754fsxgrqH305ZlCL7+ErYRz9a'
        b'EJD452+Ebl94NTSEKK1oYoYadPgkgKkzSsieM3AzPYyToytC3GMrZO+sdm+FZCwDHU8KwZfJQ+RQzQ7fFaFjy/AF9kibFXmhG1LHZkBeBaiP/Par2Yyzthd52ZXR8hnq'
        b'123Avag2JSktMM2Mk4qFsjzcR0/yUDWu1wQlSyQKTpDC4Q4e73lCfg3/KjqEDz5/DoCa8JWEsBSAbU2QJjaLuMXoshlqnos76UurGZDVHni+j9Q9iXNZKA7EN/EV+qoR'
        b'7pmzheaaExl5QHJstQKdRheXUpCXo0e0ipmC6804MbqJa0MEqBfvNH9CfzNzzo38MlUJTHCzy3xSehBwNktEqvIKijPRKRk6bGwPRk1htJyJrm6FxxT4moSbjG7RYYrX'
        b'bAlKssoIxnV0MFh8fF+Ib6R70awY4GjdKtyPGwBrhgVWGBCtu16MduAzaDeqwVeVvt+NF/8tKPHfeOF9KeB8AWc+9zHBTm2pthKcR44Rdr7F0YO8L9w5icOIleOwldeg'
        b'ldehTUNWAVUJI2KLPak7UgfsfE7Gvi8O/qXYCqCeu9eA2HlMaCFZIfilzA0QnlfAsGfUoGfUkOe0AZn7iMy6WV4rf99x6vsy/xGZ/bDMY1Dm0RH3vsxrxMZt2GbqoM3U'
        b'YZuAQZuAEUv75vTa9AGPZe9bLn8qXS+WzHjKketjeh1bYc5ZOlZlfPmkAr64fMEJJeEjTm41FoYRBhxDP5ABAoXb7BT0jnhBGIfCPONtRNhaAFfmLL1HRcWa0lExeaVk'
        b'VEIL+aPiYi1fOSou0ObDtawcmkV8pW5UsmZzpYYfFa8pKyseFWlLK0clhQDT4Y9OXboWemtLy/WVo6L8It2oqExXMCot1BZXaoAoUZePirZoy0claj5fqx0VFWk2wSPA'
        b'3kLLa0v5SnVpvmZUSouF+fTVNk15JT9qV1JWMCMmlx1iF2jXaitH5XyRtrAyV0OKe6NW+tL8IrW2VFOQq9mUP2qem8trKsm7uqNSfame1xSMBwGevPeW948+CgVz6TnG'
        b'C/lXBnni27/99lvy1q6dQFAkIl792etjev0+Pp5Erbdk0jhX7i1Xedxk0Vcy42voo7a5uYbvhgToK/fCZ/8BUUVpWaWCtGkK0pUy8qpyQVk+zBi+qIuLDapLNJnUoeC+'
        b'BSyurpLfqK0sGpUWl+Wri/lRy4klUt02zlAfYpUiZgmz2T9QOle3C0hS06YnbmMiiGyPhWKBGLIVuVWV2efSBJjwWJYFZ25nUOXkYZn/oMx/IHjuW1NxwFBw8ojM9qGF'
        b'84BL1JBF9IA4+iFn2+L6C86djva/ASbKaPo='
    ))))
