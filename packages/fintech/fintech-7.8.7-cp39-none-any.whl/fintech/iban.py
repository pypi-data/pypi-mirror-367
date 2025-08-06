
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
        b'eJzNfAlYVFeW/6uVgkJAQdy13CkEccF9iYoadlzALSoUUEgpay24xH0rdgRcABVFcWERBBQwoCbn9HQn6UymM9NLmu6Z6XS6k04nk+50Mt2TrTPn3ltgAZp0///zfTPw'
        b'1avinbuce+7Zfue+4l1pwI+CXivoZVlKl2Rpm7RL2iZLliXLT0rb5EbFVWWyokZmnpKsNKpOSDmSZeYLcqM6WXVCdlxmdDHKT8hkUrJ6o+Saonf5IsUtbNXKaF16ZrIt'
        b'zajLTNFZU426dfutqZkZurWmDKsxKVWXZUjaY9hlnOnmFptqsvS2TTammDKMFl2KLSPJasrMsOismbqkVGPSHp0hI1mXZDYarEYdG90y0y1prBP/E+g1jl5atoYsutgl'
        b'u8wutyvsSrvKrra72DV2V7ubXWt3tw+xe9g97V72ofZhdm+7j3243dc+wj7SPso+2j7GPjZlHF+35tC4XOmEdGj8gWEHx52QNksHx5+QZNLhcYfHb3T6PIukRes+qVdE'
        b'JzkLVE6vIfTyZgwpuVA3Snq36DQNfT5gVEh0z2uCZ0Jk9NJRkm0q3fQcCVVYgHkxkesxF4tiXoRuPRaFxa0LVEvT1yjxMd6Ge7Zgtllj91DDYiyZQa2xODQKizdRl4Kg'
        b'9aEBEVBgxkIsDIvE/DCVlAMlrtvhMuTyeRMWqiV3etvrn+Aefsgs2XbSzWX4AEtj4Cy2uQ5ZH0oDF4bFhcIdP8wNCI/C0o0azAuNo+H7z+cXGonF0ZExcX5EyA0iRteH'
        b'hsf5BYaGBcigXilZIW/4fHy4J0k2QMs8eoWy4Tt2KcXDsQ+yXDntg5z2Qcb3Qc5lLzss3+j02bEPKQP3wZVeUYP2IU3sw6eruDy8Zk0bsb9q8maJ33xrD98cada01zaZ'
        b'lo0QN3OCNZIX3Zs1f9nez8bsETcXa5QSvetm5bzz/Gvbpkh1Upob3X5jw6jgKdrf0Z6+M/1P8vbZ+yMipTTGx1xFpeyui6S7uu/FOb+cs3n4aXE7Zc+fPM96yvykCX+S'
        b'/XVL2eRLUo9km0kEKI+AB7QhtLF+fpgfFBqI+VAX60fbUhIwMywQykaFR8mkDE/XZRvgij7INoI6rcTjcMniLsNaOCVJWCHBebgFDzkN7kIXPLKYVS7YRLQCCXKhCU7b'
        b'hjHmdPstZpf10EWEIgny14yxDafbowPxsgXbpYNQSYQzEhRm4GNOWYIlL1igWLnfjwg1ElzGGqx0TCNBPZHkemwl2jUJquEcnLL5EG3sQSiwZKuC4RFRSmgebJvACYFZ'
        b'/hZsUeMpuEOUcxKcGRfJ50nBG34WmwpLoZsIpRIU4N19nLIaztA8Q9TzoJwoVySohMsTOEUPNwwWbFPGk/bhBRoL2iDP5kuUHfgQ6yxQKMF9ZONdkqAq24V3wpZ5Wy1a'
        b'OZRPp89XaTQ8AXYbUxz5ghjLXoWKBCbheQmKnyd5ssHgGtyG8xZPCY7CZdGpYuVBLoMj0Azl2DZEiVewikh3JLiSjY94t3Sog1taswqqsZBIDdQLHg7nPBjw1mIooN27'
        b'QL1kGgmasGsM75S822TBVhl0YBv1KZOgBK9BISf5+dBIbTYF3sOXhLzPQrPYvlnh4Vq8q9qOTELNtBHYgF1c3tACl0ZZ9srjporh8reDIIzz2mbBDiWU4TGiVEpQmpbM'
        b'CfLNeNviKYd6vChmqToSwVUnYNVBbNPIpzFh10pwcVMKn3s2vkSupU2j0nCWb9Hsy8Zzec7RjcE2q2rzJjFByQxoEguBPGzFNnc1lo0UPS77wmMh6kuRWEQkGdSSn8fb'
        b'NNgRLBbqVgUXn8c2bFHiQ7I/vE4qPwZbOQ++ZAZ55Nlku14gSpMENavgLKdAWyzUEkWFZWYhm2vpvnwqPDEU2oii8IF8+ouU+fooqOMi2IOV7iRpdeJioXCl2BLBCVOx'
        b'Eatou2WLLKLLtSXufLAwuABniLk22TY8S6R6ko9mhm0Um+cY7e4tRnPBG3hUKEn1IezmHRV4CW7Q3smwDDsE75djxonJkrFTq5GlknFLZJpwwxurBecPfKBci60u0MqV'
        b'+z7x8dw03mcYFhq1OSpy6mKeSrg9jxPIXRQlabFd6ZPJTICJ3GIbyQid0AC5RFEvAqZWbaTBcBVaxHbc9AE70VQpUCMmqsGzW/jmGjfgJYtVhpcCiZArwekkszCvxyQB'
        b'rUWJD2YIeVdEYq6DhR3QoXVT4y1/tgYafF+ObQybpRNboRUK5uMZuA+FKhLKNdmwCTFDsJSz6K/AJijIwbNQBPkqSZkqW54DxzINNh1bMbm2XAd1DhsAKzPYGK5QJB+x'
        b'Bbv1CttQ1myERTEJCyg0ZUqZZB33bZ50N3ZsmB7qIygOJEqJrtv5wmi3Tluh4MUINYsiyXgdimxT6P6ofQewHHOhYV7UfKhTGaKgCGt3h8D1bVFSsEVFrq90pM2PuVi4'
        b'MFu0nE9jncOz/GMwNFjJmM8ppbFYpHSF3Hk2PTXePgG7RWNoh9usdSg0scbzMZ83hodKBdzFCtt0llHgufW9Q99xGroR2sPE0GVK9eYc2zS24kW7sDwUGonZvpZzaIp2'
        b'OM+bBiqw0zuac7xuz/4+hvnCoHu3VocFcHuTtxSucwE75mrh2HoersLJ8gcvD5qxiL3Vs7EDzaqReDGbDK/ONou6BMFNymsYM6HQxvgpUiSKWeA62VPtbiggIYZipxrv'
        b'4yO8yOWNNUlwwXkFTDBKuKDeIJFbUeBdTxLKYrZhtyeQ8T+RYdFA6dyOYmM0RiVBkzoxSsqGZg0F3GNQxdczHPKHQdsaNlNTn6wU5Bfz8BycTiGNrCIfd0UFxdCI7Vxe'
        b'WJ4h77cNYs/qsRZPik0rV2D3bL1oXJWlfJo61MEFi9gzu9LFDc6JXIBCWOKT1rSUCUP7zdHAugS/qCLLblpuC6IuIUa/3g6C+apN4q8GLolgplVKaQ6WqOAq1mm41uGF'
        b'5ZDbX+16ZQU3zYKrO0rN9Ol8BhXeh+L+c4iOjULWjXzPyTS1eMOyN9BGhi+9MBku9XapZ13Ii+5nAoXTOrhGahWFD11Gj5mDD2028iCSD5nxo745VAY4vkdoCJ7Y5jdf'
        b'rMECVzSU9J7ZZ5vD1lBKsz/o7dIwSBMdXJ1XkWeossBJzLMFMAnfwmqs79s9lWEyNDtMOUSH5VzlY7DaZWYa1HDljcVu6O7Tw6J+kwnhKaWZ0KWCU6674SSUiE0vTmK8'
        b'8U71zj5gL9q5eKcrsAsfhPDGE6fAjYGKHgx34miF1HQMtiuwhUzwNN8MODZd309B5mJbv35CQ7JVlG0Ukf0xt4GNUBflrODsE/kCOTzmzCgU2DycwixXjbsuB3vHb3ZW'
        b'jA2UUnHFuK50IX99hmOUg8Phmmg9Hc46GHJ2OEpodY9auRruTJNIrTTkn894chi0zAeODfI5ITuwVKeSguGqCq7g0Vi+YDKqcjIrpw1Q+/a3JO5z5uJFFZSNHMv3DAqh'
        b'HZufqCzjKpzy4ydboSDGhuyeJ1uvclnoruMqSJtQOiqCZsG2cKY9fRri7Ok3QJHLxFSs5XLd7B2SiQ+esMa9Gm/K/NlcuE9OwwIN3B2Pw6bAgZs8B+pTAsQet9AWYP5+'
        b'4fkK58b28xjc85FObSDPcpwUB/L9+PyeobH9zNKxreu3CSdkV+BLFBub+aAHFgQNnF5O6edJ5k07mIJVYxMfdNUUMpFB2tjkIxeM3iVG4TSeEGpeSw4716FZ9b2t4R7c'
        b'fo6s2aFa92J9+KYkZCzot6o1eN2xgU1OsWM2VlHGDA8pIeQ7STuPxf36RaQJlm4799qsovyrG+9y50O+5N4mJxMfBxcdCtZn4usiXRbhbWyxzWYJKSVfnc4aBjfWOXld'
        b'th6uYvBYRSG8FsoEa9fiwngnYquwV8vkSY6ZvGiizvlDKc7L4OIKt+iFW7l0909YMigq01JkWMnFpVdgByGSRzwY5GAVqfFAv9vr2B0OzqY6gp1Zo/Ect97gIwTPBm1e'
        b'A8XHXLF9DxRku+do3f7cTEhBqp4aBxq2eAlrf6z02A6X+W5DmZ5txUAdbnSlGM4Hb2KJWt5+ru8rdyid3Pn+7YM2IMBlwdSxnOmJcD6uX6zoFTrpwYU+VX58cIVtLtO5'
        b'BsKMnAtKZa4Nkju0bSMEcXI3Xt8mmfewQN+9TiiFfdmi7NFPTcxUwxxRvpFi5Dro5H7HNpGw7sBc60mCIRIdKFethmtWKN/HFQlPQ7Fn/ymuBPfG+35KXsM8XIdB9DqG'
        b'V62OXSiDItamaCCPTarsebJ1GhcKhXBPOPW7qeEZ4walIdCoSiQZRElzRqig0BTJd25cIF7rFykdEm7Ey+FCwK1KZSIW8oEnTybs/RQx3cG2tUIn8pWascnCARxXwdmn'
        b'KHTDcrzJ2y5RUNh4PEoYTGUELdpZn7dSmuWwgH7SKVfBpRXe+kiOG9Lxqh8hjV05DqCBxymUs0w9ZwletlhVo8m9YR7tL1zM5qhlObZBpwXvyazYKaoZxSMJerIu46B2'
        b'scVdtnWCo2byPFQLmHgrGcssUCg3chRWTUA07AXeI8gA7Raz0mUd3baTO4IaUa8gDHEswWJW4SleMmFFlokbOWUlXM20mF0o/l5yFFmwapSY5aHPEkL30mpaB7lzVuO4'
        b'FcLXuO8FKLG4yaEsWTB2Du+NENNUo/2wBfKVcHOMAKOX9gRzxl48rGQVmw1bHAUbeLCUr34kXMi0eMixhS++ihWGjlPeygZLt05mpZx9HNmzWg4hrzoBKcsXQSur5ZBS'
        b'XHUUc7aKhZqwNMeSrUrDm45SDiUNFwUi79gBx1g1JxDaHcUcvEkQmtHwJXIVFUR0WQ/nBP4/Cy0O5H0N8yHXYlPB0cOOWg8c9eE1hlHjvSxD1NAc5qj0+O7kCJDwQwfW'
        b'slLPCnzkqPXQnWsCsNVEbSGSyzorUS7TevW7Bd685HXQopWv5tUpXuh5IIo2pMn10GXZKz9A6xRVESyFUtGpYgQUWvaqZswQKyqCi6M501OwOZYVTMhYixwFEzNUcgZm'
        b'KmYTRfbCBlFoOjsCunpl0AblFk85XiHELWopOVgg6jIV2dhg8ZRB91RRTrk06zkhHDvWT2F1ls3zHXUWSv2q+E4kwm13VmiBjmBHoWUp1vPRtkPFAlZqOWBylFqwTKDx'
        b'5yn+l2Mb2cLwECGF8xsEflcks+qHu3IfE/UNmiY5UQigbRa5hTZ39bSpjtrMWgMnrPKEh6wyg90RjsrM0J18jmWeJJM2bHXxdxFDVcH1fWIt9/G+Cts8XOD+TlEMuI4l'
        b'KVw2iemsEykcxSump62sHOAoHoaPDcO2bDnkLhYCpZCbKsoRdijFOqKpn4OLYrPPHIgT8jwvj+HFIZ2LozYU6MO5C8bmeawytArzHaUhAtGchRQsm8AqQ2SF5x2lIcIs'
        b'1UJF8objVVYcIuBz1VEdwvxYsaraAAKpbTb1uPTe8lA7pQScwaoFTHg2mYFX4kjcZdAVKhZFruMckVTjwoXxlc/14brtSsCyhli/r8b2TULklXgGGzn3ixVQgW1D5G4B'
        b'gvmr0AG3BBdHtamsEpUA9xylKDL0k5ykg5eiiKQimHNJFHuuhxF6YKQELIEWXqfS7nKUqbAoQWhrHTzYystUa19wFKngEQhRLYROuKfFuyT3MkG7RMNcEJK/mriKFbDg'
        b'RoSjfuUTLeyyffFErUa9Co6J0lHt/BTeQYPleq1G5hPiKGtRcuKwvVNLs7RWJTZkCT0q9yaIzghbJuFZVu+au95R7VpNMZo71DppHqsoHYNGR0lpmqNsDfWeWKvNUU4M'
        b'YitjDrWDLJzvUec+uK3NUeO9FIlXZS8QQCzkHC/cM5sVz87z+iqrnk3z5YPFY8dCVjuDVih0VM+CFonBLmBHOCue4ZnA3uLZo21ig7rwgpXVzlLhaG/t7NZCPt5YwkEX'
        b'tB4yaHclSrdEMf20RazUFUq1HgqsYV79Ea0CquPFRF3QME+LLTLyJZVCcDUTbIKUtxRbiaQ4omHlPKap57FD7M1DPD1E6yrHisViolurRwtR26HLW2tTYsV8sdQL+nTH'
        b'bu6DY1qLEpriHOW7I2scYsvCq1qLCzxQidVUkyXe5n1mRR1h1Xo13qJsDh/STusyODocmo1HWS4BuY7iHdxxZHiQOx/PaPRwX8kKtAVx0uYdalrZKTynV3KrmGRbhAWR'
        b'4VtJ/QsVkgIfURZNrrGV79NY86IIzI90hRK1JN8pC1Jhp20sT1BphKYILIaWGUFYNEPPjqjcvRTDsWuqMOtCCjkzogOxaleoUlKukBE3drCvTWInQb0/akmcJ/GzpFCJ'
        b'H1+xYyt2hMWOrhR21xRXx6GVMld5QjqkOjDsoJIfWqn4QZXysGqj0+dZUrKCHx4q3/mjXJLcdE4/IezY06IzZPDzTl1KplmXY0gzJZus+2f2a9jvjzBx2uq/JzPDmslP'
        b'Tv17z1p1Jhotx2BKMySmGQP4gM8bzemOCSysX7+hEg0Ze3RJmclGfvbKRuXjWWzpvWe6hqSkTFuGlfY0PdFo1hnMjibGZJ3B0m+svca0tJlu/W4tzjKYDek6E02zWBeb'
        b'Ko512XlvYt8oM5/WIdGUtJgtc5cpx5gRIHoxBleFhfTjwJQxaEXsJ4kEY9xnZUswGpJSdZnUyPzUifjazPudJ7P2skmi/NvnsbITbsdoM3VRNouVrZHJfWNM4NzZ8+fr'
        b'VkauC12pm/OUQZKNT+XNYswycMb82Sd/nZFUw2awGvmBeUJCrNlmTEjox+/gsR38C4lz1XKsRbfRlLErzahbYzNn6tYZ9qcbM6wW3Uqz0TCAF7PRajNnWBb3zajLzOhT'
        b'0gC6u9aQZuG3mZD3miwDFjPowFwjDTyoHRq9lhs2dmzHmxEZlG46cs2Vm/kRbOWUUdKsWWdUUkLC9ivzx0g8V8RuLw8ooA9GqNsqEZSYzNt6Jmsln4OfqySvhIDJsSvE'
        b'GW7ufk9pbJpWIc1KSIPFWyXhBPPHKKAgmXJER4KYhtV6Tz526lYomDLyCWVVpogq9/DRujFQYdmrkMQZITbohWe5vQlKKMpcs7BzBX5ESAjhtoisbXhx9CJ2SDZEKbzt'
        b'FfJ1xb2009hMUeOY1qwS8ahiFTQKGoV0otXBTW2WQuRcF3bhDc77qEWT4RTatdkKEf0vLiUfyAhb4YYubA87XBQHi9S9TcSjynBsgdKJ2GZRiwykTIVHHVgmQkHJah47'
        b'eRQJcYltIR8tC+q2JbFMzaYQCezZvWF8pzRQ7R6jZoeOIkxUL9srskR4nDUlQcvl086CRAU2i/jxGCvNK+AGtvF1XmQZ/DmDIBXBzQnQMs6y10Xk9iXE9Et8uCB8yRXq'
        b'R1Ku7kjUIS9crxB70U0ZVbv2+Sc0PDmLj5eFtdCwDaqcphoBZ8SW1y8Lomyh8MlUR6LEMVgDNMfDXbzPQIYDYbBiuF4uAEgt5O3AMmhzIhPCvSfyLYIiFwjSVLMDZ5Gy'
        b'VhkCud5NULtI7vtWyiVdgvvRXbGSSDNcNmTh2bmzlOzsX0okgHzKFLr/93LLEJL+6p/+btmZyurZ4SErvU7vysn594gfd8M05YYtW7fuk8/QfjlduaRA9sqKlw95rSv7'
        b'vi7ypbHvpL87e+np6X/UvNJTWXoyPeXRkW8+t5e+PWTkC2feDjmW7vPqH+Q7T9S+8XppyCtvZI4o+0LXcvX33/tey8lFv+0aVXFEHbSo/t1Fj5ZPevvFrMNDCtb+eOI9'
        b'1x1/nvL74GPemycY5C8Me/3xqurQ6k17em55eZ6vOPJGS2f28ti/3vjqN68GXb7i/82mwzm/KcquOX75Lxvef3jm7e6HH26s21vxT1Pn/PHV9ln/+Oo3Uz1+nFP+q9fP'
        b'zViZKj/UOqbRoFryUcbl6V9nN/+sLvIT17xX3v/nt18aOv3D799dW7epc2XGezWq076nY478QpuyPDlb72IV+dL1jBmBfqGBckkNVfINskBvqLOyiM8KylEzZoYF+Otn'
        b'UmpbnBqAeQSBdcqdHsOs/PS1dcmKiJhAyIvBfJ13pFrSrpdj8V5ssorj+0ur2MM4/oEzZTT0cXnYkrkEAa2sDDL1AKHONsfzMHvF8zA5gf6YHySXZk49DA9VeA8vP28d'
        b'yUFG/nosiAoII1AvqYPlcXDaA1qxwzqRiNZ13hGiO7mLkkjMg9ZwltQMx5MK7NwK1Xp5j9xPz3RV0rvyt7/5wtzpF8OXppgzDxgzdCnisauZLNou73Hjvj+e/cGaWTYx'
        b'/3tE0itlSpmGvzxkcpmvzI3e3eiX3Xfn991kGrmaXWVProymlo3k7+wvD/pLySjysTIzGZMUzZnRq3uUbMYeBUXwHhdHPOxRsgDW4xIfb7ZlxMf3aOPjk9KMhgxbVny8'
        b'Xv3ta9QrzSwbM7NnbszMpszs6S8zy9L4vOfZ2saztR2VPhpLfMtlan6VfyWXUwYmk/7K/rJNohZLjVDM9mI8HOvdDqetgEeYT86FjUU5dOPmCKJhQTQWx+BxyA1TSR5Z'
        b'ioWUYXbaRrMmZw0LIyLJDVEDlmzKJO02OTbBqQTuaUZgK7zEstSw7SJJpZQ3SeEUCdnaXHoj4XKp7ykpZYrSkVwqchWUXCopuVTw5FLJE0rFYeVGp89OyeXbsoHJJX+S'
        b'zim7NGem6wy9+WD/zK9/ljcgi4v9lmTTbMy2mcwixcgyminhTBe5UO/jff2zgZjeJIEY8d9AM5rSjWvM5kyzPx/MQJTkp+eQjF/GrsgjBy7iqQmUY1Gix8AVPm0KlnWu'
        b'TTPs0plE7puUaTYbLVmZGcmULPHk05KaaUtLZsmUyIt4FuzIfJ+eNq0xsSU/ydIoIzfo5gRabVmUfTlyMS41SiL9WIsANpH+O5Io1aAkShVtY2oEBGjmOj84iG0Hep8d'
        b'zIv0Dw+A+ljxGCG7ERMZFiWT2AmBdhE+hLuxJt+4H8oty2ig4/E9HybMfE9vCDWkpaQlfpSw8+W3X3n7lTNw78yi03Xna867bWs5URfacLrm9OwifUXN6YkVx+YOkQJc'
        b'tNc/DdTLue+bvB6KtP5kHZiHhVE27j4pesqlCdCmxGZtopU90omF2aaImeHMf/KzWIdVjoZ7ygy49aJe3s8bPMsPcpfQoxWPjz5xex7C7SUzxzaMuzez5xN3perR9OpV'
        b'j4tDQ4S/cWcX9mxnv+kVZvY0idmLXVz7/BAb8GdOfqhh2Lf7ITNDqmLFvcuFZsx1LBkfwU2+lfgYO5Y7Aejp2C0wdB2eo+SnleDs1QDFjohgKM6GO3ATHrpROlE2BC/D'
        b'WWziWdLwCVCvzfGgBLOCWKCUFRsmuIr8qR2KZmtzsnd6MUIupS14yotT4qBoigXbPbWyOUpJjmUyX7gsE9WBsjk5ljlmuJZEK8qUoMPb8RiTFU9AszYnJylKTYOdkrAK'
        b'OrGMnClP1O3qGOYJ9RrhCSN3cLROKtEMFxlaPwYl/eC6f6bIf0/O3z+DvCtlwY9lkhyKZSGURRYN8qJ9eGIt86IK7kfFc6ZyuyZF0+dNlX+XN/36WVCdu4H+QP2ZvoT5'
        b'Hdb8uwHvM3Ao6/y/DkOT0jhbFqN1MPAcwCCTS2ZSko3cZkbSYEZ7oeeadSt1IZQBmJlbXU3hI8maaSYwmWVLTDNZUmmgxP28pcPNhxA4NRvSBo23imx3phNvBrYpNv44'
        b'uv/GkFj/AHpbvZq9hcRsmE3vxJ7/qjmrOCEkxD9g0IhOayJYm/lUAM0WyeWcJWAzjZrMPPz+rAECZD9/U+zsGzEza3DIZD9/W9jst3n/o7hdJj0Nt3sSbl/C/MJx7aGn'
        b'Pasu4s1D8zNDzt4pHCZN9RspzZL8ctwTEpa6jVjgeEL7kLc0RdJEeEgJS3ca4yXhtR4TOrzHYL8r+SyC/VgD9QLBvYQnlkAB5EIuRUhv8kJwxRW6E/lYH20g/C8lZBP+'
        b'j/wP36nk07ln2gUPsGMuw+uTpdnSbLz9PL8dAqX40lylNB8eSHOkOSvhMh/kXpqXpJP+OEyeleB+3juIDcLiAF7Flt00yJJANsaUbaJE6c0etXeRSCaXpHXSOnzgy8f4'
        b'apKb5CONXKLySnDvmrxSijUd/fJzpeUekX77dvDU4tkex1d4rfnG8FnAD+W7G9N+t/T4rj+6+Xy/OHHxsPwdq669tTZ41Isedz/zHX8y5EFB5Xtff/7p9PhXfxs5/OTS'
        b'ad1hhXfWdB16vlF94Ee2GT0zavI+Xljzrybra78NzbWsjRyvyxv5mtr44Zhu33f/xdX7wYHPtZmJPfcLwk+pf127Pscnccfxf3nuy8KoztHf7Fiojf43PCQfcWzzso/2'
        b'fnL2Mmb8488jzq38h59GJb7/u09urvrkKxkMm9cc/IFew1HWJKzGKgdCw/tYyFBaIAWUGit79CQW7sJNpywAz+IpB5ASaUAYVFjZMwOUXG/mDj8vhkG2IGoSyLpEuLBT'
        b'zNbZeFUdlhTAgZ/XSDy/LUwbgYV6R1ohl4aDXanZB00cM2K9HE8Q8qPAkSPDUri60guucGbhlhwqGOoLimHstsEF9WG5fzIc41AOjkMlNveBudS9BOc88L7JymHBFazA'
        b'9ggsimBwk2NNvIm5nrMUu7Bxh14mcgTN3wXfRNriKsAaBQ2etMwSScsRSepFa+wqJ9TlzvGZh0wpZyhsEr1GOl5mb6e05glm6lGQ/3bKZr4Lbimc4JZPX4bDxv7YKcM5'
        b'O/rZGY6Oib8KOrQCajVzqEX4m9D3ULQroHA3lOll/OFoV8JgR1mhf/eCJ3V+yIPiQV8o6YNK7JFPCvHyFHnfF0dkf9MXRxyB/Ys3+3m5DcJLPiPbT+HJOo/HzmX0/214'
        b'9Ew33Sut/m5aLZAB5ZWP8Lazn470+xuRwTG4LhLAfLiqE+XZh8t4hXZBNn+6Zj5eg1NkbpgftQLLsXAj5kbKh62BOjgFN6CSPuildV4u0J6ZZrrzVpPMwsLGzq5lHyYE'
        b'OCGMLS93nqkpl4XOvTErMDlgk3bjDEO0Qf3DWTMTPkjY8urIN16u9JA2ThuinletV1lZIg1VMUMdnmUU3uiDGL2OZTLe4XWeJLiJR4V/wtLhvIgUCCeGW8dwR7FjXl8F'
        b'SZSPVsBNnXKnyc/KvmumxFu+A/3MGSxgvsY8hrfYhiexka29AO/wQlNvmYkS93Jhj/KnGr3LLqO1z+S9ek1+IjN1XoSRmX37TLpOIYofT4UldTJB5KbKHwIh87HohKke'
        b'lX7v8WxjZSIw7faOiCEIciWwP/vnsf077FBul/6f7bC+nxpvzEozWS19xibOM8iidOxuitmwi59PDDC8XuM16IKfiqf7NfYLiYmLjt2wNUAXEromJGJjXBQB7ZXREfEh'
        b'MavXBOhWhnB6fHRc1Ko1G/Tfjr6fZmM8vr8R6rJqjESBRJeQdnyyj2RbQDcj0jawL9zNIC0iQ1sfKgpGDO4QRoI6N6jcT68wyNsvwWU1not1g1w8uoI/twkl2H7QuTcZ'
        b'1po1HB+Px9tKuAYPYkzjW67JLDHUOnPum8Nfaxl6VOe15pVvdK1K84d3XV+4KrcV6lZeXtS1cPHwf9mBP/nPxGRj9ZnYuOTFP38v7PSJsTNHz5/y2om36nz+bIz86tav'
        b'Wvb8xHqkMHjoW1806JU8JpJ+X8C8BXqnGmwgVmE5134/bMXWQYHYH1uUmhhX3t1EgBCqAp0LpB7saxXcNFMmekfwQO+nllxHGixyqMGHcLof6H669bgROrE4AX2fXgOa'
        b'reFRktU3Odwf3WdE5hEDhxvZZzaslV8/s+n5FrNhYfDQkM0zQgPgHFb5Rz+pWvhCl3I4NARRhGMVECiFGytZhCP7KsCSIMhnFgY1FrU0+ogydeLBZ1uYoyjIvzjZVxT8'
        b'e6wshWDsjoFFQeeAx6tnGYZ0DpieEucYXGLng1lGukHxsH/kCRO2lmawWgn9JBkoaPUflIc/Q7KoOw7Cff3G6sOA3wUBBeT7vxp/ZU/1DZpoGyuoTfbGzmejJBF7dVAz'
        b'OPzCKczj3uX8nlGEk6RZs8YPG5sbtFESB3s3KcbWkrM+8eTcVG7kTxBT8tyEl0RYHhST8bTXk7AM9XiCT9G4w8XxZdm12p96xEmmq4WjVZYtLMj8esO417lvUb68ZLx8'
        b'V+rLP1780XHf5XO9V0WVFn/vV/8hXxyXN39rUrHq9dcL3nM/9/v5Hxe0vPWjyoTUpnc/H37uzW7f5sMHRz33xsJPvs4qbA6t+HjEZ1/6Tg78qV7NS4WL8MawgaVCHse9'
        b'VlIkx3a5lT9wemwkdjhhhBheo8fiCKzbS91U0oJo9WGsc7UyyezChhHks+bB0T63dRCqxcFRMdROTH9uQOCnqD8froma5In0tdgFgz2bUkNZ1F0ObKbDaZeI/lwwFiZA'
        b'GSUC7Uq8jKf29IKC76pbuvNcgHSbWQ73Z769/mwN82LuMje5SArcZeaxfR5Nr+jRMg8Yn2lmmYRTevDUCYmbcX0ej42yuJ/He/Vb6pb8mwmlXnCOVjyKPec9aNG04KHA'
        b'viIfvVYvW6uXR681bRy6k8AtO9Y8Gx53ZmuM93qfH/zh4dwdNwN/tCrwV8Vfenw85qf+nZPXrpep7nzRlhAa+uPllZUjIubsjaz6L9m+1K9rq6+kmaavtpjLP42PMR+5'
        b'ceTH6a/c3Db64TsH4/P3vtE57KPPsupKspPePO+1640FPykO2rEpee3wn297Iy8TP9+Uubv7/F/rRvzkvYpNn7z9zs2JP/vn2V2N8y0bw0LObtv4m29+9+qNl6UT7ulL'
        b'jl0LzTOs9WsrcLteOPvNjD/fvXDoo/cllzWVv/KyG5fA+uLs7e3el37jc0t15Z2A9yuS8z/d/qtJF6YsmfQLY3b8O/4/63xzSMacfwys/+XN74/bH7f+4zkY8JffvF6b'
        b'Zfz406P2pb+eHVPx7gd/3p7c+MHCHfMaNu2ZMe1Hxz6JOz7j+OWX/zPqB/857t//o+rlr34a/37lX6LWqL7vYdvw6IPdew4uu7O6rmflxfv/8G/7lu7pajxVuc4+7Q27'
        b'ouYXoZ9eGvHCzq/2rNz9gw9bfpSzZcSuR4Z9rzV8r7T4y/3/+pPSL37Q9eqwH3a/c+fendCPI25PqSzXnrrr90v/P3zxeehfNnZnfljb9ab9Tlrzkk+vpKz+8tVbj3wX'
        b'5a19bvrDaPzt3KIpF9cE+mV+HdRTe/Njz7VkmMyPzVXvpPglC4ejkmwhGc4kuM7B8ES4pmPWQSlIxQALCcPL1sks+BXDUexgVr15zCC7JqueAu3cUDeO3oIFlBwUBaol'
        b'9U45dG2ffBCPCkOtVULjjPB1UB6IuWGR0SpJCy1yMq1qeCgweVcGPiKkiflbsYTaYGEYa9Msx/pR0PF3HqjqPf6+89dnjqMyszDw1As3d018fFqmITk+npv6e8wAJ8vl'
        b'clmwbPw3cjk7ah0m1yg0bnJmiF+rNfz9/97vPXW0l4z9amTDFKw8MfY5OTkoH283WstI2Vg/OaN48KsXu5rH97o98lzy+HgnhzXk/1/qMvOEPu/GJmI6aOH/QOTfp317'
        b'LpcCRVoogBJoi8cSFn0hD0pcJI9RinFRWGI6uuCfFJYL1O4XOzcF5gQWLHODFT4n30+ff2T0+rteq1+Z/JuZxxP1SxunFJnO1mqj/+z784svjUmuqvxDUqxPzGe/mxW2'
        b'p/uzf37t7G3Xf9UEb/uw8NfVh+v3G6ObUqN90//6SJPoM/ORW1S3JiP196OvR97wbH71F8F/WuG7+5v0Dz75Qr35g4800+690XkzCwP3Bv/y05ffTbpR+V7IO7N+XWj+'
        b'L9nLb+kTPv1QP4THUDgDHXiC/3uRGFoGK5xpoVWOt6GQXl1kuEw+cIvc9xWWFRyjzL6FNWaVsKHYrYCaLRZuVQsPop3JA6tnYwnz8FDE5TFMMR5vHuJGCy1wZlREWJQ/'
        b'FodHuUhqpVwDNSlWVkCFhrhYvKKbEa6SZBESViSus7Kv1GzA46MJOecNTIKgOCiC/EIxxZMShfQ8tLjQxFUBfEkEFG6Pgmb1wD5qacRqpX8c3ON1AMzHx8nYRgO0AXMC'
        b'Qf7ZDkcz2qaE07vwHC/9zU+iNoSlIrDARVIGkkwqZXBnC9j5IKOhFtojYlZNYrVHJ4bGwEUl3IQquMELBjFTsAEL9HBvNrUTyiKTPNcr4g5782GMnng0fB+14OQAtjiO'
        b'3GSSDu+rpFCsF37rwiRomRETQKwXiJ3CR3LK485ix0Zo6od/xv3POKX/wYte8SyvZsowWR1ejZV0pSEsaSE4plDKmGdgD5h48USGpTJuiikswQky6/q8woQeRZoxo0fJ'
        b'DlN6VBzU9ygJEFh7lMmmJLoSGMnoUVis5h5V4n6r0dKjTMzMTOtRmDKsPaoUcqr0ZjZk7KLepowsm7VHkZRq7lFkmpN71CmmNIIqPYp0Q1aP4oApq0dlsCSZTD2KVOM+'
        b'akLDu5kspgyL1ZCRZOxRcyiSxM+FjVlWS8/Q9MzkRQviRak22bTLZO3RWlJNKdZ4I4MIPUMIUqQaTBnG5HjjvqQe1/h4C4GtrPj4HrUtw0bI4Ym3E4sdZ2b/iMm8kF3Y'
        b'd9vM7OtwZpbnmln6bp7KLqwWbGY1NjN7ptrMvqpqZt/eM89nF2YjZpabmdlXycyL2GUeuzDpm5nVmVkJwsy++2xmNRsze7jJzDyjmR9Fs0KcmcET85w+38m2w63Pd/7X'
        b'6mf6Tt7yC03vg0c9XvHxjs+O8PbF6JT+/wtKl5Fp1TGaMTlar2GPBCVnJpGE6IMhLY0Cgs6hSCwPpvtutBlmq2WvyZrao07LTDKkWXrcnYGZ+blecTpdhDYuFf9wajlD'
        b'Zby+plQrFRqmcRE+MhaN/hsw5gZa'
    ))))
