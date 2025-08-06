
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
        b'eJzNfAlYlOe1/zcrywAqiqKCGXeGVXDfRVxANvfgCgMMMso6C+KOogw7CIKyqCAqogIC7hvpOXlykzZN097kNg9J06ZN2ptmu82992maps3/vO83AzNKmvb++zz3mmcG'
        b'mHc773nP+Z3fOe83+Y1g909GrxX0Mi6ht1Rhu7BH2C5JlaRKTwrbpTpZizxV1ioxTEuV6xSFwj6lMXiHVKdMVRRKTkh0TjppoUQipCo3CS7pGqev01yjVobHqTOzU80Z'
        b'OnV2mtqUrlOvP2BKz85Sr9FnmXQp6eocbco+7R5dsKvr5nS90dY3VZemz9IZ1WnmrBSTPjvLqDZlq1PSdSn71NqsVHWKQac16dRsdmOwa4qPVfYX6OVLLxWTP5XeLIJF'
        b'YpFaZBa5RWFRWpwszhYXi6tFZXGzuFs8LCMsIy2jLJ6W0ZYxFi/LWMs4i7dlvGWCZaLFJ82X79n5iG+xUCgcmXRQedi3UNgkHJ5UKEiEo75HJyWQdmifaRpZXIpNeVJ6'
        b'udNrNBNAzhW4SdC4xmU40+8HFskE9tmsGeOFswunCOYZ9Adcx+MbsQxL4mM2YDFWxGuwImoLFOCl9UFKYeZqOfZDQ4Z5DnVNm7qYOlZiVQD1xsrIWKzcSkPKQjZEBkZj'
        b'OZZHxcB1eIilUQohD6pcdgZDCV94Vb5ScBOEkbPS5CHb5q4RzLvZwn3Qguexz8V9QyRNWx61JRI6/bA4cF0snt7kjCWRW2hy62pwa6x1Qb/IGKyMi4nf4kdtxSEk7IbI'
        b'dVv8giKjAiVwXS6YoMRrXtL6FImdOXnYNLLme44kzcOqdEmxlJQuJaVLuNKlXOmSo1Kr0vfYK92FXrHPKb1RVPq/73cS964MOLh1vrvAP0zcKRVPIi9mTMl+nfihMsBZ'
        b'GEmfzVrjpbj4Yrr44UekS/qpnpXXNSVtv4fQIWS40sfTvMfL/8tTWHBC9sHML6V3QzvziiQZTI7KBQ3HrkuTRggrksLeC/v1pD8L/OPQQ18GHZ7k94J0/a8kf03wyosW'
        b'BgRzMDWsngtNpP0ybJkQssHPD0tDIoOwFDo2+9ExVAUGRwWti5UIWSNclpJJ3DGPpSFYh0+hA0/NMbqRkvGcAPWzsd88hpqc8aEAD+GS0aCgljIBioVFvGHu9I1Qgc1G'
        b'gxN9XiFAKdTv5w27EmVQYDbiXTZxtQDlJug1ezHzuIRnD6FljhEqSVPYKsD5daG8ZQ+cyN4ErdRA1o6XBLiAF2aYmfLXwqWoqCBjLlu8ii1SKhfnOo234ex+LyP2KJn8'
        b'AlSvkfLl4VocPD6Ed41mNua0AGWBm/gQvAK1sixoMbqzERcFaICno/gQbdh243oj9jGpztJMeBFvmsexIRXQKMcHUGeEcvZnswCN+6CdTxdMjeeNMqOKidzCZuuEJ6Js'
        b'p3QqbMRC436yVKwXoBKaI0QRqvOwER4sNI4QxEHnVHCLnwA8xvMKOKnHPncmRacAF6F3t3g4/ZlwExtnqPgJ3KBBUAh1XDsSPZyFxkNQRscmcRaga+UucZ1+NZ4elWrE'
        b'XnacNQJUQXu4eDhH8HxILPaZZaKiz6Ris7hK50yoTYMbKrzFlulmZ9AZK2q0JxX6oWaXcb9UnK001o03ZECpy7LJRrzHRG6gM4GbOeL6jyZi3XKoNo6wnmcjnHDlGiWT'
        b'68F+LIdr2OfMGi8L0LRlkai3c3Pgvi9pos+ZidBOIuxz4y0Hj3qOgirsMynEharoLE+LK3XireCF67DPTSkOOY9NweJsdaOh2F1OLUwH12gyd+wUT/XsSChKJePtwx4m'
        b'eRuZOzTO4GrIh7JtB7GAMIyN6hKgFZ5CF2/aCzcmYpkrNVkVdAkb4BxvmoCXsGYPnKI2ptdbArQlww1RjJOjYjyxmjRutbrTq/GeKMa1ZHyCLXiDzlwijrqE/SbxNNqS'
        b'oDEokSTsY03XSUnQl2D25lqCx9CAPc6s0Um0lQvQoebjXPE0duB9KKNjtG7gvGqy1fvSsHsd1qucWcNdAa4ooEY83959WZOgV4W9bLo71NNJJSr3+tJgI15W5SnEZRqw'
        b'CyutKlwKT/EqXFHhXabCHlpnL9SKAh4/CqfI5lupje25j2yZBpbytUbNczFkUINCXKmVdi/ijDeWeQdhl9HEpCsWoGgLWnjDGridH4iVKgbDTOvn8KmRN4z0gsvQi/0q'
        b'V7bKAwGujs03T2TC1cCFA1A2D6vhDpQrfPcKMrwkiSd/fcIFPJS5Ecry8AxUQKlia6QgT5fAceg3m9VscF+UG94KtXYIs84huECFdBzt46ZGZh7FDygYOwImYBmdd7aQ'
        b'nbvT7Mk+veGkhatQE02yJgvJU/ESlxTvU8RtJYfqiFayUJKKlUYeqbfj6anwNBxrsRhuzIMOhTaWzPLy3gho2x4rzDEqoC6PNM6DetX4mbZ+XYTXZ/ivc+AG1smF8HE+'
        b'WCF32faiWUNdlyfhU7Er3CU/o76R0GXrCgXpPvBELoMzcNk8k3q7JcTY5u20m/cm64z9kT5YI1cmUV8/JsTDSOpbGwk3SdjBzmFsEer82MUnSEbGd3Mj74xN0IPXB2VW'
        b'TM5ju4PHe1VqLINrW0cL69ROqqkbzSHcBt3m22+vAS5bZ4duOjj6cZ2tEWRQ5GIHGRoboxlHWGITpkKWTNb0RFwB2gh/L++FMtJiJN5X4p2jeME8lQl1c7onjVnsPbgF'
        b'phv5RmEi9snwFp6k0LWQyXMWm8RzKU236rHiWRVdi2WT3IxVJscKudDtDA/QstocSKN3wukXmWRdg2qSQQ2WYB0UpWGFkUyqUQjFiwqojNjMD2EP9BgdTkE8Mb5nOJvo'
        b'Q5ELH29YzY9XS7Hv6XCm0MF6B8B9H7TInaBgKVcSnoZLZLeD3W27WBLiYBZzDinIva/Em0PZmK6lIYM2ObgAMYou6lwh7p0NCsMqBbTMBgvfw9apGx2tzqYm1lUq98FO'
        b'uXM0PORSzcY7mXYrwPFjYncaelMUkdtfEDmo0RtPcKVm4K0A2xhSDDRtxDMEpweYVqFIDZfIomLxiROTyhzAzrB821JH14LHM6B+LxZu95snimWEi85Ynn5YtMHHy+GJ'
        b'bQBpxV3xjAlaZapXGCnsXhfXODeRApbt5Kz+a4BHeyMi1FjLrTweLzgFw6Px5iDWv9ndPGSzywOsSw3unktFvRV7wbLQ7M9G3JuCJ6xDrj/r+HgN6n1myvARXIMifgph'
        b'G7DN3kPFM+5knZXzJ+JdGfZALeESY4rxwo5nDIOGEOY4WkaugkIOkXYRAZpCodbetNlvNgCoxGs+Mhl274dHonIeM+JiW6L7WZvA9hd8sE3uhBV4g2cj0BoDVxwlwrtu'
        b'diYoJ5iIDV8FnTMEA9Y5E53KMU9nA59u2TYENFaYiVArCLCwbA60KOBi0ibzLBGKr9KEgydg9aGEnEHRuM/NxiaKjvhghzjoClw6NmhJcGHvICJZR8lILve9cyUbFE4L'
        b'EqGFn/R6uDM5mgMEdeP+c8Fp0EKsCE8M2mkyafcch/iQRQft4czWsWzyCOo6G+4QXODpGfyUV8BFp2dPOUwUfT48mIg9dArQOdo8hfpOcs5jss9aMYgXVsjzgRPMciwK'
        b'8WQL53g6OL3dyc6ABz5gkeFDPOXDYXQFVI2k9WMDHSSQMhi9xyzsATbxST3xovl5a+xic6bC/Yl4i+TEm+RLrPMYQvYGq21dt/WG26II29HCbOu2C5wyh1FnNRRTiHgO'
        b'BaEX7s+xWTPXRyg2KuCCG9EMdirpWCpxGMXW2AhNc2wAL455UQHVMxZxuB0PBcGODg6Pk+CqnYOvj3FaGIiXRbjtxO5xjubF8Lxqs+NuZkO/Aqr88jjcTgijaOMwpAWu'
        b'SlOsVkx6hvvzRkHxXAk0rXCNg1Yn8bxuE3e8/lwwtvqWDx730cjw3oK9fNsRSiiyO9xJeNumrxv20GZW5OAtd25heD3D8PzJcUTYCmcn4gMZ9sqJUDEVbXenTQ4H/SLj'
        b'6IWbPtgv94hdwntnU+eO542XSzANGidil4zo4lmo5vCXHkQbfQbE6ZCq7fUf6DT/MAUJNvk8vD7HLkg4av0Q3OVm3I9lLlzzWXOxyUHzE7FkUPHQt52Q6eRebNsuGPZR'
        b'dFdQrsYCkX60eVgmpvAk9Oq2BvebFBk9sEs0imuhqXbRfeJ4O7i34zZQqzChBQv5mNXQmPv8KliUP8dmJFbrbiVw27uJn/KYBcahvbM+UvItexG7FLlzJeudneZh4SK+'
        b'FUK2U0OQO8g84KYiGfoyoJKAJ2ycAsqhH0+LwLMPb9uFyEH98tM7RpDSK5cvxvP86PAO1MCwTIWHI+jDFh8slTvv1YrdT0HPtGHsWQx0p6HAZ7EMn8A9uMrPbhTxkePP'
        b'sxS4tP0ZX8ZaBTSHYrUmhufMlEDUBM9SDyUa2UfElOYhluJd7PM18iyzRAAL1EI3T4SIyd+CWy8Y8bZErGlUJkIhnw2bE9JTRw2VTWRwnydiMQeA0d9eI5SzLPcCBf5p'
        b'1MSSBOgI9NPLjQaWz1goP4zN40nC6HS8iLczh+oscGKHmLgVQkcI2crxoVLL4RA+JCV4K6EoZflMkEoByqBIJ6ZgbVgPD6Aaq42uUlGyOnKjx2KpoRjrdZl4zgilcjEl'
        b'bZZgEW/KwPOUuHXTUkPVmwMJYg7zQMDjCrXRg83XyDLm6zO4eKqsNdC+266mg1fxOG9xgaIpCWq7og40YwFvicfWmViyd6isQ+fYK9YHuihRasEyiV1hB5/k81EaqHMP'
        b'dqUGJ7EKcIYO+IKYqJZQWH4833uo5rMSWkVlF+jGR24eKvmscuG7WR01HurUdiWfkdAhznQVrrpk+RvF1Po87ROLpvMhS2ONcALr7Oo9zUmiZhrT/eFO7lB1BJs8uDbH'
        b'YRXt+Z6ncb9C3EkFVlNcZMvEwRnsJbZkVzuJTuQtCpk79M+mzyVivekM7d8qWilc9ZnjMVRToXSlTmyxQEk8dCuMIyRiRaV5PIVUbjuV0A4P1Z52xRbJDi71Ku+weHLl'
        b'oVILNqi4Rcerl2/db1dq2UnLc/+4oIXLRpKmT/SCFqabtnhxmc5NWf5wHPvc2G6u0CrBeM9aicKbeCHCbFeg8TRz7ayA69AxgeYYKtDgQ6VoBA2L8cousok+sSRxhW32'
        b'3BprwQfK3aFxHPZ5OIkFgbZIiXkCJ8p4ktL1VgLtPtHmegW4ijUUGfgxPcWzoUnzsC9XKmq2atEUsdZSDeXz8elOalGKZ16NXVIbJlyD/vwd9pWiXOjnetojMQSQpQ4V'
        b'isJCuIAJUCHdRtxxqEwE5wQugXphTMAsuxIRtmKjqL77mTMZzR+qEUHNYT4kELoPpBylBqvGa6B1mTikewo0uhF093GTJ7+rPbhO9P0KgtfrBNkWkvqOVekN+UfEmgn2'
        b'+kvDsM9dKgrdspRAge/0OiHcaTxB7jtUjTq8XGw7Di3+UAWF1KQQiz1teErFlU58upESggbota9VYQE2cN2yfC8m2L5ShQ/hIt8BUWysnzxVhbeUYlMz3D8iAtRpH6wP'
        b'g+N2NSx8fMxawx1J7EOjclaK9aPLeAZqeYs3LVIOF9cOlbfcKKvg5a1i6HLGM5tUJqtx1sa68CET8RoFET+7uhe0C9aq8+V52LpqqLK0doy4/Bksj/OAO6o8NlUHoWom'
        b'lvBF1k2LwXLsVuWxETcoZ9+IzRyAdmtfxNObh0poHm58hW3YGiuE2FXPIsS6dgQWKLAFztrVziSLRTPtwNvrjsbb1c7opG+ICmvACxuhb7PKg+39sUDxjyIyr1O5OWnd'
        b'Nqk8mMk9FeD64aPiiRYSElko3rWosMeqr9acWD7ZRpZaa7CSWtio+/ywJ3OhoxOwdkOuykUqrtKeaXUFrErxgIZAldlauj67cSFXynioUaTQOQ6V7i5P4gOCfadgpZPK'
        b'aNX7hRFwXtzIzdEHZMR+y0SjeEIHPJEST5YbLodHavq8FoqtlTvotDI8KOaVPjkpAMq2CDNnvLhLSaH0DPRo5KKN1u4lhvJkDZbFrMNymSDDp0SlyWKPc2HM8aHRWBqj'
        b'FKS7Jdi9LQTvLONlRLi2Ey5EY2UIVgRo2D0UYUGv20iZl3KqWMrEW4ciXwiIC4qUC/IVEriejDfWpLA7IPZPKYi3SPwGid17WgR+OcUuqtgFlczikuZivZqSF8sLhSOK'
        b'g8rDcn41peBXU/KjigQhVcbvA+Uf/Acp3VVt9y+C3Vwa1dosfmWpTss2qPO0GfpUvelAsENHhz+ixAtT/33ZWaZsfvnpb7suVetptjytPkObnKEL5BOu1RkyrQsY2TiH'
        b'qZK1WfvUKdmpOn59ymbl8xnNmbZrWW1KSrY5y6TOMmcm6wxqrcHaRZeq1hod5tqvy8gIdnX4aFGO1qDNVOtpmUXqzenizSy7sk0enCV4uAHJ+pRFbJt79Hm6rEBxFBNw'
        b'ZVSEgwT6rOd2xP6lkGJ0+Sa2BZ02JV2dTZ0Mwy7E92Y4YL+YySYmqfLvX8fELqmtswWrY81GE9sj0/um+KDZofPmqcNj1keGq8OGmSRVN6xsRl2Olgvmz37zV+vINMxa'
        b'k47feSclbTaYdUlJDvI+P7dVflHj3LSse1Fv0mftydCpV5sN2er12gOZuiyTUR1u0GmfkcWgM5kNWcZFgyuqs7MGjTSQPl2jzTDyj5mS9+uNz2zG4Q7cWXj2OnZU3Bru'
        b'wPOWQb2NSq5OIf7VO4NftAaEjBdmsdtXveHwtoR9IrTDiVC8B2VJ0MJQmHC40p13/tzkKpBXO88yHsm4Eh4iXtWqjnkIPhRbbvnvd3t/Z751hstJBwdZ4Omj0JCzQjOC'
        b'g/dqqJhuayEUfQoNh6CSt0h9sc12HYi9RMYr8YRInQhI59quAwmWW+BcJvZwfNHrianbrgOx6hBc3GDkAngn7LLdBcbjSXYdOJt/PjFopipHxrnUTqIQZ7F4MkdVNyle'
        b'VOVaWccjLODYJ4atGVOm2y4PiU2eoCStWCTIK9bvxT6jklMLHcXsmkw8yekFhdmSI0MXi0VEUKsoI6/iEjiPpChlu1tMGA1nFjuJgxqmw6XBm0WspGzuAqWmPSKVKSMS'
        b'8UjFtXOXNuoOF1KCRB5oCWF8k++1iTQ1k/46h7fFUWeI/Br3O3H+Pno+CXENukSiVzKJ7MHKxqcoyB5qdmpkYgxtUcN1WxNakiiKNBEj57SpFNspINoWYxQMqqHGk+9r'
        b'r9tR21Jw5ShUhUGLGEersV47mEUEQQ8JWIBdGikX0ZkyobrB1vRsqPbHevHQb0zKGrxSHj+N2O15eMAtrmSy+FzFig2GmJGGQMGaYSx1nz2LpoFaCmbYkOwFpXrLj5Ok'
        b'RkbVTAnvLa0OXxcR7lZU+9rrhzLvjNh/RR28K995XPCSguzWgHHT1V+1vHUgoFXR6vxx19p82SRMyZdWrV9SEPVyWNNrf5z57QtTel4IvavOLZA+8qv+pfybETVfrlxo'
        b'8Ds3rntcTZG6p+XnS3//8ss9Jyu/7Iz9Jf7If++3xk9n/GnUDy78wSlh3qW/rHz3ze4lloP//buX3z50DitPfllV/bvTe95u/O/JL7d1vfHLeT2P85Zt/WvHYcOHZ9+I'
        b'P3NMs3zpl6/cX/+D9/d1/Gd45Otf/OrrB28den2P5/j8vTvOpX34hce3b+XV/uqHdQHh6R4RvaqMJPdDn2Y3z/zs/r++u/nq/YjknMTGbXM/Sn3bbZ7f2xPuvRo7bntS'
        b'uvab/1JtiNa9/YskjZOJH3RVlm9AkF9kkFQYvVsJjdIgMvsHpknsoJvH4pWA4KhAf00wthInqQqkZF/wVst3Y89Wky8ntXT4V6PjgyitYswALlFOqdogxcq50GXilKJ9'
        b'B/lLGZb4BwVLiIzvVcIJ6WzyjQoTv/qqi/CiP8QnXfaLj7nkBfljaQi0ZEqFYHiiIIb2ZJVpPBPoAZZHYllsYBTl8EIKdCnnSD2I3V02TWOt56Ed70SLc7AyPLnLY5HH'
        b'eOFJdt12fpVGOiD10zDLFTQu/Mff/caQ9WuvJWmG7IO6LHWa+ABVMAu6ywZceQhIZH+wbsatDIqPCRq5RC5x5i8PiVQyln6OpJerhH3uxj93lThLlexdMvTO2pQSb/6T'
        b'/eVBf8lZi9RHwgobQhwXRqMckLMVB2QUyAecrGFxQM7i2IBTYqLBnJWYOKBKTEzJ0GmzzDmJiRrl396jRm5gRMzAHrIxMB8zsGe5DIyg8XXr2d5Gsr0VCJ/6kNxSiZK/'
        b'mydzS9rnugPa7A7AXvkyrCBo8eF4NAavYE1ANLViWRxWxkcpBI8c2QLoW21mx5z0Ij6NjokT+aSEcPVF1XYpdu3fJyYp9SOVgyw0e0wIZc0dKTJr+GO7cLKFvzBh8IEn'
        b'eZrcyiBlxTJikHJikDLOIOWcQcqOyq0MMp0Y5DuSZxkkf+LNjkIasjPVWhvpc6R3jlTuGaq2+W8wSoMu16w3iDwiR2cgVpkpEh7bY3iOIT/exgRIEP+NtKI+U7faYMg2'
        b'+PPJtNSSOjxRZPIycUWy+OwmhmVJ1k2JI57d4XBLMGq5JkO7R60XCW5KtsGgM+ZkZ6USI+IM05iebc5IZYxJJD+c6lrp7fDcaLWebXmIihHt1qrDgkzmHKJYVsLFtUZM'
        b'0Y/1CGQLaf4GU1I8x5QUcealjJ9shYvDPe5XEuO/LhCubxaf/GMfxMfIsScqlqDtBpSoFuJjaNusP3JWLTeyef4D//2TpOCmzb/VaCO1GWkZyZ8m7X7pnR+884NquF29'
        b'sKijvrW+p7Aj8kZRa1FoheZca9Hkc8dn+wqBzqrLb7ylkZrYDZL7Aryt8seKOHxCwmB5rJnjo1R4Afrk2A0dhLTs2Uus9CDvC15H8AidnlBh878JcFuetXiXRurg6N8F'
        b'cdzbB1TiM55DiOYhIloqwyxPjlyGEUNIpBhwthnVgJPVPEQocWNv7KFMh+VlBpZxGxiUiN04xLAJf24HMTc87SGGbXEGVIVHB8Md7OW7dNzipFDzck4BKAjdGkqAm6bY'
        b'cmB2fX4SeqEcWgJlu6LnQGUudMJVeOIqJGONO56n3u0inToN/btVeR5E94iGpsNDvEFMtJ3jz4ip2K/Ky2VNxcKLXthswCJxUNsB7NfzivCIMLkgxRrJWCj05jQmCasP'
        b'GsNIWZJs4q7EAu8txwtibuy9WZWXp6TZTglrsBkbsSiAgFJ8you48CDU+UJtCLRP5An3UmjPc8i3S/Us3WaXXJyFJTpPDSD8lAhSqJRowyKy8bYDRA5mCIsYRMo4SIrP'
        b'g0otzmnOg1Ap/5tQuYeg8i/flWxzH3dMtb8TKBiosO7fn7J+RybJBv+vJ5IpGVwso870fOr4jIBML9kpKWbCxKyU5wW1JY+r14erIyh4GxhmrqLYkGLKNlA6mGNOztAb'
        b'02mi5AO8pxXDIyi9NGgznptvJflmsJ1sWnYoZv5MuP+miM3+gfRj1Sr2IyJ+Yyj9JPH8V4at5A0REf6Bz81otydKTLOHTYHZJrmec8TEl2ZNZfB9IOcZBbJ/f1dgHJwx'
        b'O+f5eMj+/X0x0eHw/mmZt0QYLvMeQZk3q2lRSkM5698RUba7sphiF1DqR/J056W1LEX/ap0yKWnntyMMYta9ce1oYZrwUiQBzOE3x+YI4kXOtcNJUMbKsQRQlLfHporw'
        b'VCfDDiiDYiim4DdaAn1Q6OK9k8+zQMqy93yd06ykmMVbvAiszQyD56dD9WzK7bVCqBCaTYDFPgzGmztny4U0fCSECWGuPnyCyNiRglrwdlHlJGWsXbCGTcAQfvtSPEMT'
        b'eEEXm8EV28Qi6BNlNitzH8U7wnphPdTgTT5JtqdKGCO0rJSPTHLbNT9I2Kz/ZqBJbuyhpo6XRk+vDPWAWW6rP5sWO3DiXMLD3LFdb0pecXt/ijnyofoHK8PDDo2/NqL6'
        b'Uzefy5Yp+o8+OnLs2CezixpvOb3i7LLs1YEdWz+YM6XE5WL+4lulJ0I/kAXP8vEq/9mdv5avvzqt+6WauU1R+Ycs1xL+xT8ckn7eP9IcZdFu8frNyWnn/2P21A6PawML'
        b'JvzsT3vff1j9Wtxnpq/SssLuxf35l7936f/wF5Wv7zBtq/u3uK+v5N/+ovXAXyQfLpr7wcsWjbOJKT03GG8QqNdbMyyeX0HXMh7Xad91UhbYrVEd7h1xCOw52GHizxfc'
        b'i9UxNKcUi+VZIdQliI2IdhJWwOlQbFFGQRE0cg4AV7EJ61TRWK4ZpAkULiu8wCJ3VhhNzD4kLthNGRsFhzzJi5rwhXCDJ4KL8eoK2WiWqYXEM1GPSv3xSZSJFyUuHoSi'
        b'pCmDmRdLuyidahATvL5pB6OxIppyRDE/DAkdMUu2Bwr9NBIx2jv/QzmWSEBcxIyKwgOnH7NE+nFMEGwpFXuXUmrkwVMmD4lcylKlKfTytr4Mo+0IylBiMyAjpLbjJd+X'
        b'E8nscqIxg1yFzf25HVc5M+HZdAiaDPjYlgx141Wo5BmyMAotMihPxwca62XcFezBYi9sf6bo3rTF4Wscg1kNexyNArY0TTr4dQ3Jd35dw5rRfP2GA2ZtFDHvO4h5GufV'
        b'PLral7X/tzOZYUHXph1H0FXGmRczyzzOrrq+F3MDFoo8fghz3ZaKLCoZb/Nq6Uo8ye/ed48SH9ZrnIcXyIOwNDYGC7B8ExbHSD1XExE/BVeggX7RCOtHOsHdOb76iiW/'
        b'EYxMmMDc7E+SAu3ygISX7le31koiZ1+ZFZQauDVAG6dV/mhWcNLHSQmver/+UoOHsCmhboa7MtmgUZjUzOZG5dihhR1UxCmwOxNLxXJOYT422aGNDNuCnATuqAG+WbZi'
        b'jrWQsw9Pq+W781LFUs61VLjviBxe0D+HAYfTMhN/WvwsnowbqvUIKrgQy0o9eHmv6GXSYV3ZaY/ONOjII22OPJk5MK9/SAxjhxxVJtYdhk8bJGIjd0A2xpscxOgpOmCB'
        b'8HsPexfk91LHN2KpncDbk3hpCgvg4t/wLalF+Lt9K41867qDaW7KydCbjIMOJN4ZkJeo2adpBu0efgfwjDPZHFKrnjNsOuvQ2S8ifkvc5o3bAtURkasjojdtiaU8Nzwu'
        b'OjEiftXqQHV4BG9PjNsSu3L1Rs13J7/D+Q2Pw86kELeRCoWgTgps9psimBfQh+HQjpfZV9WWTwtg33cridkQOZSBYI0GOlyh4QC9oqDkgADnla5ENbpnmVlpDlujxrOx'
        b'AZR0tYuDyWc42k3Ca3K4NA8q9MnKSrlxAzuBA3/6JGnnS7fIPXoKQ09NPtVTF1XTWt9a1Fo4uelJ5JWToac6GnpKemR+U167VdBRmDs5JSjFPaXHd33R+Gmb8H7BgckR'
        b'sz55JNujEsqWjXrd6aJGzoNxArZLRNcYi0XWWHwGzvNaZ9BCuEzGf22jo/2T8UMXnuNRMCgZ79hCIFxRiVHwEhznpUk8BwUECjw4+ykFF2+4vl8KrZGuDgY8vIO4UgJh'
        b'tMu1x9h8JNRZ4sa9xEPMuL3/B37Cxvg5+MmAg58w1494Aa96rg2IDPSPG8qpx8IjuRdUUBTn4ewglrLzj1FnUitl11UhUCp61YRj8vRdUDq8R1lrcPwrh4M1uO/zqpOU'
        b'WO56tgZnH7R4sSpLm8lTmGFiFUtg2J1bjo4+oJjmGD2iRN/K0JpMlI+kaCnwOE7KQ5g2VSzzPZeJOcw1mJV9X1ImJmH/F2OoZFgscI7jeYsELi0aLoT2pQxbCxuKoUFQ'
        b'z8EkVeYtLFmvpQwlacm8ZZvFi8Fc6EwxzsQbg0+1TYniDzZ65seLcfX5oOoZMBhWsQPb+dxTfZyEVMqLCKjc2hQ6QS/Zf1ViTKCWdzuW+P6wZ1SBeqT8pcWTpHvSX3pr'
        b'0acnxi6bPXpl7Mu/+ky6aEvJvG0plYof/rDst251v5/3eZnq1z0/fbMhKb3rN3/yqnvj8djuo4fHL399wR/+klPeHXnu83H/9eexU/0CNEoTe1AcnhAHeCYYJ0weKsk1'
        b'7+SXG9CzF57aUXfyFzkvemMlQWisQpgfpzyaAvc4OmHXqqlDgRuewj2Cp34Nj81QDk8zA7A2wzF+U/CehjVi8a8MK7BWtRNuRD+PYPeieMKBJxdAkRgOh6SA9t0kyAtQ'
        b'I8fz8m02yv599UE3HtPJopm/cNAaawOt1Qyq3CSuUjG4u0kME+xga0DFYC4x28AYgR18DbsgSTNxEMjYLIscgOxVh/og/+qXBS7Aabstwq14m67FLeIVeKSRxcWt0UjW'
        b'aKRxa/QF7y1UGL+mef3/5LXl9M83jd4wxvLFk0cf31Yrb5U9Se72W/3pNb+9K8Lbjiq9Vh2/Fr5/7fSf/mJ12zt7fCa9+ujY5f2vebQZf/tGc+LSEftnLKnLvfHe+vAp'
        b'a8tfO3ps7VxVRYWi+WZSzEVjbXr7T3738qWQ99TFc1wv+S5rPzL1lVUzZpZ4fXg7pqxnhuab3E+MpfnhX39a4F32Ryf33cXyLZs3RQSZp3XscXEPnL56auycvvKPbiZN'
        b'v5Hw4wn/9jNY9G99xysykmfveOeH8+72FZ6/3Vv2i0+1IX9+5ycSD0MxYueF10ZV/uyVnoU41qf9vMeij38t/0Xzh2PaF+K2N3IvTArO2RBw9t8/6n2/681/2dL18WeL'
        b'9F+Pf/Mr5fzxqcU73puBvp//PqP9/c/189+b+aNZI/JfnbrG+6PQlCU//fJX2ZsD4sfvORF1RBdp3PVh/ivG3dV7Ss8+bvzkD5uf/nzLf67ZZipr/TxcF73jox2Bo2Zp'
        b'fux9V99x4F/DAvtuZswN+JdvLyvqr2yErVmfHX51o+5j/+i7Lp1/iVPde6XioVk1GoMbvsmZUmk6U5tz3Xf2xN/OzS4N/Tbx0zcvzX/l3ZofxH8Wk+r1r2Oka9/pX9ET'
        b'uPQPVX/0/SI35w+md8vf+IvhZNwr/33Kvz3O+MJXCa8d6q25tLkm/I8zl41rU/3i9LdzrtzZ9nTznJ843+6ua/58bu+MX341KbWteNmogL8qVsW/HXM7iZyaXzWfXIqd'
        b'yym0lcVIBMkCdvle48rJAVrgngue8XyWHZNvqfEqv3zE+gjssU/mr+BFh2weTx82scC+f188lhGHqAhSqnYJyt3SqQErTD58BmzGSwHrgrA4KiZOQaAYpIIeKZ43YI+Y'
        b'21uIO52LZlhMfbA8SiHgVXysgm4pXp8m/QfvMzUe/9j153fOozCw4DHsG4cK58TEjGxtamIih4lfM+edKpVKJXMkan7P6Sl1lo+ViP+5KqTkys78/f/ef85STwn7z1ky'
        b'RsZKDz7LpbSDMaNdaTfeEh8/qWTCCHqNkkoMPja4JMSTJibaAZ37/7/GJQbfQVRkCzFsFy9ofjnjuRuT9Yuxiz3GA1VYxSI0lECVk+AxXuaLp/COfufvqhXGBur4xfGz'
        b'QWVLXWHFmJO/y5zXv2ZMoPwtr5++Mjp/nCpFs+T2+o3pEyZ/fPK196cc2rR/9dWGPy1bs/oPLxVMqjW98iP1k5iSxjcrVrTdecMv+ONHf+18/TWXz96/9KMv3u4b9bLf'
        b'zm+8GvNHNf900oTysLpl30z54mevyjre+uu7r/9mrvLFT34yKia9ITf8g5qALv39D+offbJz9o+Xn8LiqT98d5zvTzTv//xbjbsY4O6RS/Xz/1dHPO2kPNopA5opBe2V'
        b'4jUvfCCGyVu75Iw/9LBO8CSR1bFG4WMZ+/L0cu7Js2bCA/Kj46I+WGCACq4PT9mkBTvEYlcZXIbH0VGx/rHQDmedBKVc6nwYik2MuORpFwasI9/shDZJNCP9/UdM/Htv'
        b'ldgPJ6xEKQaaB7kSVIZEEw5UUjCqkglroceJFi5ZaJossojWQ8+SK6UwC+6PWyX3h0JfnvavwHb+fHc5OX2If64VVHw2TjDL2bc5s0Shm8fDfZZh4dkF0VjmJMiDJNCZ'
        b'ZRDZSi1t9wmPivbC4KmRE6FJDldflPD0PlwgatW2Gss01FE0FokwYoNsi9cIPs2O3eutbbe3EwNhO+OpnERQ4x0F5QvVIkw9JrX0BsQHUsJQxs5Jg7cFFT6V4j2shXqH'
        b'RMX3n4NB/8Q3Sqy+A8T0WXqTFcQY1RDcGb+h9EwmlzAYYCnaSM55GOtxlU1jXCjEMGkQCF4YkGXosgbk7P5jQMGz/AE5ZQymAXmqPoXeKVvJGpAZTYYBRfIBk844IE/O'
        b'zs4YkOmzTAOKNMJQ+mHQZu2h0fqsHLNpQJaSbhiQZRtSB5Rp+gzKZQZkmdqcAdlBfc6AQmtM0esHZOm6fOpC07vqjfoso0mblaIbUPJcJYVf1epyTMaBUZnZqQvnJ4o1'
        b'11T9Hr1pQGVM16eZEnUshxhwp5wjXavP0qUm6vJTBlwSE42UjeUkJg4ozVlmSi2GAE7crK+B3Swa5rE39hUkAytkG5jeDOzLVAYGWQZWbTGwr6IZWJZoYKU1A6PNBvYU'
        b's4HZkoHZnYF9ycswn73NZm8s3BrYl7gMc9kbyxsMrEJhmM7emGMZmN8Y2JfTDaz0Zpg1CJfsOFwH4fKrVXZwydu+drY92DMwMjHR+rs1fn09Ic3x/5qkzso2qVmbLjVO'
        b'48weuUnNTiGd0C/ajAxC/UlW02EkmT53JfUbTMb9elP6gDIjO0WbYRxws8/VDEttCrR7E+1vifi/ZlrGbJQX0eRSucyZ2Vj0GBaaJP8PL6/V1w=='
    ))))
