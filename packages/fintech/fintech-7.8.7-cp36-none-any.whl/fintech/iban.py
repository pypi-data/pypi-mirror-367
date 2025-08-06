
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
        b'eJzNfAlYVNmV/6uVpQARRdFGLHcKARUV27VbEQRZXXBrFQoopJS1XhVquwtS7CiKCCLKoigICChuiOlzkk73JOlkepLpNDM9SW9Jp9NJupNMpruTSebc+6qQrdM9//98'
        b'3wx8tfDudu655/7O75z7Hu8LQ37k9HqRXuIqeksRdgn7hF2yFFmKPF/YJTco9itTFHmyrJkpSoMqTzigFgNfkhvUKao82WmZwcEgz5PJhBT1FsEpX+fwZapzxLq1MdqM'
        b'rBRLukGblao1pxm0cYfNaVmZ2jBjptmQnKbN1icf0O8zBDo7b00ziva6KYZUY6ZB1KZaMpPNxqxMUWvO0ianGZIPaPWZKdpkk0FvNmhZ72Kgc7K3Tfbp9JpGLw2TP4Xe'
        b'rIJVZpVbFValVWVVWx2sjlYnq7NVY3WxulrdrOOs7tbxVg/rBOtEq6d1knWy1cs6xTrV+pzVO3Uan7PjsWmFQp5wzOdl9dFpecIW4ahPniATjk877rODtEPzTNUpYpKH'
        b'Ks+TXhOYAEquwC2Czjkm3ZG+H0xQCOaFLvQtMT3D4CNY5tJXrJ+EpViCRZC/PzZqExZiWawOyyLi4wLUwrxQJT7FenxsCaaqCmiGIqpajhXzsSgWy8OjsXwbtcjfgCUL'
        b'NoX7R1JPpRFRWByhEnKhwmk3duNJPnSuv1o4GjtVELSJLsFJToLlJbqYOTkWe5xcN4VTn6UR8eHQ7ouF/huj8dwWRywKj6eehw/lGx6F5TFRsfG+s+ZTUeECknNT+MZ4'
        b'34DwCH8ZtCoFMxR5Bs+C7mSZTSEKernZFRL2NSuS6mbTuaxQTjqXk85lXOdyrnPZcblN5/uG6tyJXltG6bxG0nlIhlogjbsvDEtL3yeEC/ziFaVCYBXdp4v+k7bkSBdn'
        b'zXQU3AVh4Z3JR6OCZh+XLobMVQn0qb2WY/FvmjpDSHemi48XT1H6hnw0RxDenfd7ee+i97Z8IUtnUmyOv2ScqEgcJ7yYGPSvQSnKzwR++W+Lf3/seR/f6fK4n8v+6vVJ'
        b'xHFhQLAEUAF0wm0nUj4tnq8vFi8ID8BiuLXVl5agwj8wImBjtEzInBg6zmm1BostbH7Y47FCdFmzkNSLlwS4GIpP+HUvi79oehnrVXS9RAAyCblU/zyeCRFNyxc40Pcy'
        b'AYp1gZZJdH07XsB6EXuhCltYtbMClB5JsEym7zq8iG0ilEM1XCElYYMAV/DkXMtEtpLHsJmKphwkO8dGAep34HU+DlxMPyHmBG5i41fQMHBpnIXtAwcschOxC5snqKmk'
        b'SoCz++EcL4GHeEoULdPxFmtzToCSTLjMZcNLSmgWXZOhibW5KkANlEELlw1vUCURe/DuEiZaNfWHzdjMm82ietdEKN2BF1jNOgFql0Op1GMjdKWIGniK15jg11iXdcl8'
        b'RrOgKU48CJfxMVkqXhSg3GcXL0gLxSJxHD6haUpNLsUc4YLPhGqSwBWaoITJ0C7AVcdkSdml0OGkMa08xmbURi1W7uFd7YYqHyhxgbqtMkHmKEDHS1jHC3Lx4Usidu/d'
        b'wJazUoAKqD7C5wmNOlrDHgt0Q7FCUvUFaEvk46+iGRdq8A6eTGXjdNIq+MXwVhOhEk+LB7EJO+RSh8XUSxkvWwoVUSLeByu2MKlrBDhHauzhPWI7Vh4Rx0HHWtuy1uLd'
        b'UKmkBq167HF8wY2VNAtwGS7O46InTppD17EcnjAhWkgIyxSu6wC4g9exx7wLHqikgSrk8ID3FqMmfOpxwevQrZYaXdm7jDfy0pOiqaRyMdPETeqNkKuXCz4ebzBVYJd8'
        b'NhO8iUwNG8nq+LpWB9Fke5ywFy+whh0CNGxK4mvx/K50KnDACzYdNc7fbjMFTyae00E4xRR7R4Cm8fBQmuxFOd4mlWyHGpvhnfPx5o1mYlUSW/KTcFkmNWqExgW8aIk/'
        b'SUqKxMfARWglHRkSJWPtUGErK4M7UOggmUr99E12xVavoEWEtuM2wa8kxkr74hHmr9M47oOHrKBXgOvQuVcqqYaabRrshrwM1ts9kiLUlwshw2rs0+Tuw7sqaZga6l/S'
        b'OXY+hw0a7I2BQqa+LhrIO8MyhZXcw2bopyIysio24R6yZOiHu7zLmAnwlMrwbrZKGqsBT0OlpMIa6MRG0XwUO5mIhQIUHKbF4kVX4Ra0aMQIqFBKer8E3du4wWDliXCN'
        b'M1z0YEM9FOAG3DBbnmPTqlDroCQYz8I9KFUJCmycgg2yWLiOVgvz6wRRVXAbSnLxAuFAsUpQpvlihQxOYdcyC3P2Sb6rbaVBUifpBpXgBGXyySZ4pFNYPNjoF16GPizJ'
        b'nUuLniVkbceH/HIYPj0aiU+Y5xKShCR4JIECPiDdRkIe9qiZN0mhxS3izlqBD+UEqYXQFgy3VPpoKMNmP7i+PwSadkULS0QVVMGFaRZfqmrC06RhW90OrCLAZV+XQBtW'
        b'KadOFryxTOkEp82WeWxA64REqS70wk1WORw6bHXxzEbBG54oFWkbLTqmjzPQR+Paem4f0vNtqq0Ip54rlWp4Es97JhdzbymeD4fbJPFg3SA2iBLbjwveAQp8EBps8aO6'
        b'M+BO6qDEfHbQt1+jxRK4uW2CsFGLl7HIQUMmUiV5rza8sXj0DMk4ythHK40gBJj2YKcqx+BjWUgtLGQOt5kwl7BJEqhMkSQNA01Yi837oYT0GI4P1HhvCVywzKJGc+LE'
        b'ofKTYrAa2oOVm4XnsEdBW6hxiWU5E+cklk0dosSykeq5Gc06uR2tTooWctLxJHQ6wkN4mGRZQK21eJ/anmdqt+sJO7FQQZBaRPZXkEqGVSsswqsqKJ9JztiXK0C3fdg6'
        b'SIvGJr4L8mnRziuwD+on8mXDqjh4PJY90GhKqDPQslmVDonYxsUhH3yfDGiw+rPJhIdFD5qGsOSICmrS4aLUphIrpwxa57P1aMMyY6ikAdYmCCtUcI0YA1tyAtqCXcMt'
        b'z64tqmvAyyRWu9IRziTzBcQu2t/Fo8agprclEW/zRYdif7ypEvelWOZToymT9PYWrawF4ephplIo0EIjGVY0PnHEaw5BSfCU21Wo05rhe4zMA/PwLpbu8g2W5iCSzyVv'
        b'W4SXLIuoRQY+gBJ7m7ZRlmgT6iItRpNKJP9UyueO93cQibWvn2037w9ZGh2ixfPc5GOx3iHQgE0Wf6qe7rdp0A7Lhg0kaU4pBMJj6I9U7T+xlZuHF1pZ/7xJ6wgAIGw5'
        b'I3jPU+DjqWaOLB6HMH+EmVPVdrZLK0Wy9F4Fds0MtARS1Xg/uD/CMqQmc7B2iGnkqOBSLJ6VLPUJNNL4Q8ybfZNQINZP8FYosBO6sF2yCXLyOGiqnSNsApp1ZBNNSgc8'
        b'c8iylHFCbICRlvrM+pTQ7RK9dj20zyVErHJ8MZAg+grWSqhXi5XQOwpxQrQqyHMSlsA1FVx1h7N8iaFjM5NpqP5tmwivz+bCcbxZjJdVtGXLsY+rKizuebyG/c8MtmzQ'
        b'CvkVBUnnun+pbJPK4fmVayVU64+FvEiymUI9t5yR5sGRfjOUOczAvGC+dBOwf88zyRRJ62bYqzIwWwz3CDImS1XxHFzzHLnMQVx0nwxa5S5ah4U7LHNY1RbtM5TvsNfF'
        b'VgZ83nCaLMdAWMEX99F0t2Fb8tna0r6ooNpWBT7apJG6zadIs2GECNClD5YzPL1PVoa3fSQ/04TnA0ebZAfrtgiKqPYdkhZrdHwtT8ADYguSgbXaa8NdLoUr9nMTu3v4'
        b'OF9LT+yeNhYSdlD0c2qI81iEtSqonwblHHuoqHCItTyT6CZ5xPNDm21XwdmNJ/gkPJJouw/b4szAXsC8wT0eF+WwHO4kcHPBmpXBw21MglzfmGeToQV9qoIKPbbwuSho'
        b'8NphbeTJtlHcaYQHweOhcKkMLr/oDPehJWZhkOSV66b4jHLK0v7Ce/sEb52CqPr9HC4UtBx7thuHw/ozcLMQ1S9VZWcsk5auDK4SMR61dgwYdsAVWrqHCuzeQ1GIHw+B'
        b'8pjrG8MHcPrxeD7t96dKt5lYIFlQgfeK0SbMxJh5nHruUGBHdjQXI9ZMEddIJA8xwrlnyvd3WDYHyrgZz1o8eZibGGJAcDpJsuKn8XCegw5x+OtE6MbUO/TswjLM349N'
        b'uwTTAUdy9Nco2GyDZml/X4XaZ2LZzG9ngDRflYfNzd8mFwlVzhL0FGzGU6P41jOOIREdMsE2bFGZ8fpz3FydDuDVMd099O4dZuMNhHJ404kLN5E4M2vks12qUDZqi6hy'
        b'lsriHB2CZdglObE7x/DBcBIyPpRp7rYqiRQRLQRNVkEpeaILEra3TcXiYZ7Spma2fquJsHtDt1IJT6GWr6DjUjg/1iTa+aJEkWEUKx3xBlbwFcyiQKdvDLNmZjQeqgXv'
        b'lQoK827mWoI4oGfAhdFmzTZBK9QN09B5FdSJWK6LkmKM3l34UDQTg7hjDz/GkUNhvD1TD9dF8yE4x2KWIgGsuXCNt/GDHrwr4t3tZpmU7CjHClIgK3KDU3BXdIGzcNWe'
        b'VIH6pRYvLiJtvHIRSkPhAYt/62nfEhGp4YGVZjZUiiayuHIW6VgFyI8hWsh6TDkCJ6nECrWD2ZhaOCelSa5M1Yom+RZ7NgY7w6VkgysJjt1bjrH5lQtQYoDrkgj90Ixt'
        b'ojN2YJ9cEq+KTLlSyhKUplEcBsU5cFIpBax1FGzekuK+PHiyTMTerGh7escApVJwUw1PV4tuvniZdVhL8527UmpStFfD8j6P4Jo977MrlUuxH+uhnoqIYV6xZ36wgBTB'
        b'+tvmNVfMIfmu23M/BjjF9ZA4B2+IxBgvQJE9+ZMC7XyoafvCWFbozhIHKUVwAey94ZPtiaIFOpLsWSEseEGKpmvoe6voSjMbTAs9oBCRN3qsfJllha4k2rNCx52kKVVj'
        b'2VYqgZalbKQrNFl1khRMX4o2iJrF2D6YELqLDbwkkFarRTxIoXuzPYvi6cdL5Ds3igdp0a6qpOmUkTHYEhFn4NZxkSh70ZbB7Mq9RbwoAh+ms5IqqJRJaakL7hRAsehz'
        b'xXS5OG7ZOnvSZSXY0jENRBOui+M0oTIp6VIHZ8dLC14BnW4s7fIAC+wJGTMhIhsnJwUbqYjwpcSekYHLy3iHWz1ow/aYoWSLPSMDF9OkHEA7Tfs2y6dBrZ9M0sRF8mgn'
        b'JbWeW3gIe1ygfxeb1HUa7LgfLzjo6ciyNbeh3p7HWe0tLVK3FxvKBS5MGEzkdGAhNyKsIxRm+ZBuo6+D1F8t7b0OSbUUEp7GHre1WQ5S3qAJ7sZIO6AlmghjD9ll4U42'
        b'526WOmgkTs6aLfcj8OnJgSK4KpeUWxEiZTHxjFEqqoMbamnpz2LTNqmsPZwQp4cMMN9ozylB8ypJxe1Q5Yk9TnHQa88okXIu8GmHYO1LVOQyy55TwqoVXPdwf9sxloaq'
        b'ggf2pJIZpKwkdJ4geGeZvDn2pNKL2MqFd/UiMkYl91bYNF+Jjf62DAsWuLKiJ9Cjkrbi+X1ZkjoukC7ohfeCpDQVab8mnpggt5wnoZHY44p39sgl2a/BjTlcdKjAficq'
        b'mmy0J7CMG6ShCJB3stzWaXJeUoKoaUa0JHrRFi+evurbbM9sQZ6rtJanSHllrHB2qj2zBY2Qz6VIIMbLUlunoFEtldVtz5XkK84wU0kqNtuTXk5EKrh8BROxVuMoC1FL'
        b'2aZmLdRwxIzElkCNo4+/PRnmTqSF7Z3YdR4acyjcslnmeZNkmSLUZWmYjTywp8jSnaU8HRb4aZzJFT0azD+dsa0D5puwW5O7OZj1dYsBbJMtq463l6VpcrHrGGvTJkC1'
        b'cjzvbA/kwXlNLjxV2vNthAp3JFw5swjOabA3ZLw93RYFFVy0BeHYwTJq+UvtybaVLpI59u/mTYiG3bMn2+bhbUm2Cwos0rhtimLz7xOI61pJAbxV1ww4qXHDK3CP2Vy/'
        b'AK3EAfuk5enTQKuGlqgYn9oU10Cwf0Va8Tp/vMoKT2OFQsp1NTmYJOHzoV+pcSLfcVIujdeycpt0vgDdGRqLeqst4129gCCMXQ+OwzaNmCI5QZbui1RJtnMbmv00Yhzc'
        b't61DPbGhZsmCWwmjrhKY3zHOYJp4QqtNrKfKspgJdxMvTGWxPBTa8n3QbuODUBgcv4kl+JTQsxVK4oXte9R4dfk0nZJD2USs84TWFVgStRFLFYIC+4l1U8sHEpS1vLQn'
        b'Eouj1IJ8r+wo1C+Ygeel7GLBug2ReJl2XPkCLJuvY6lAF3eFJ9YRxPCW17flyk3zYwLClYLyRRm0qjE/LJmdHrEfmoDAjoT42RM7MLUK/FiLHXGxoy2F1SnVyXaopSxU'
        b'5gnHVC+rjyr5oZaKH2opj6t2CCkKfqilfPdT0ruzdshPCDvyFLX6TH7WqU3NMmlz9enGFKP5cOCwisP+iJBOWv0OZGWas/ipqZ/9nFVrpN5y9cZ0fVK6wZ93uMFgyrAN'
        b'ILJ2w7pK0mce0CZnpRj4uSvrlfcnWjLs57n65OQsS6ZZm2nJSDKYtHqTrYohRasXh/V10JCeHug87NKKbL1Jn6E10jArtFvTpCNddtabNNhL4FgNkozJK9g09xlzDZn+'
        b'Uism4LqIkGESGDNHzYj9JJNiDIfMbAoGfXKaNosqmcYciM/NdHjoYGa7mKTKbz6OmZ1u23oL1EZbRDObI9P7ltiAxYuCg7Vro+LC12qDxugkxTCmbKIhW88F82Pf/LQG'
        b'Mg2L3mzgh+WJiVtNFkNi4jB5R/dtk1/SODct21y0W4yZ+9IN2lCLKUsbpz+cYcg0i9q1JoN+hCwmg9liyhRXDI6ozcocNFJ/uhqmTxf5Zabkg0ZxxGSGHZ57CSMPcrUx'
        b'YXwj7vV1FnNoS/fbeaYbXuNntDMVUwSKuBYu3J19VDd9miAx7RYKy8ugJHgf/bFT2BkL7bxygEFDUZbgmJiaHeXvFSqd8v5psZvgzcb2zo265LFakDZ+z/PLRM3LUGtn'
        b'iHjHk2PbjAhsIn5YD5X2I0NiTP0SgF5cuU8ch90cytiZISHYTV6ighthzDUXe9kPDQMo7uUQf3Y2nNaYoM9oPzbE8xkSF3lEKJSvycb+FxUSm6qGFtu5zvFErNTkEGCf'
        b'sTGOy15Eu9nMMzcthBKXEMizHTZCRZKE+3e37MUekdz2Y7XEKSpfgqvSQC05WELxhz/m208iCWhr+UC581YSEyFX3zR4EPkghLeaMBOb2TlkJ5y2H0TCFZouH+wesZlK'
        b'zcFxcQrJ/9STf5POiCLJE3VhjwnLsYu1u0zMbJx0Kg0nj0ADUex6bHSQiHyFH3Ty1YhbBveppH+qnZOboE2SvSYHThPFdyDvbCP/0ImS0vF0CHRT/OYDvYJED2vNS/mK'
        b'vz/Jgd8W8C0XY1T74fGCZTxdNB6dtXjhZB/qBs4LSbHQqJMOsQ8epAhRQ3TSajeFECyxDaDGCvFgPFTbTWEVRXrcei6GYL84Lo2mZzOFRQd4k3VmikXJEE7jSbslbF0p'
        b'zeTpLOwlQ6iTzlS5JdzDFt4qgHR7T5O92NluCBQsF0itGiheaCNTaMY8uymINt8F52YTPyhxgarZNmOYeIz7YDO5/y5mDFfwgt0YiPfUSGvXM9eXjAEe4+PBc+kCd160'
        b'FK7DeTKHJbPtxoC38AaX40UK3O+TOZihZdAailEK94joXxunOUhOttFuDqZNXJDtNM4TMgYKOvvsxkB0Xwp+sZlkKKNV78KTdnugPs/pFLzXNUTM28SDyZg/eNr9cA4X'
        b'0ymEtg5Z2GN8aO8UT0uRNjzYgGRIJ2SDHZ5ZpZPzGciwxoNFkRRyD95ccB8aJLZ1d93zZEik5Bq7JRExfmR89MVehehCakr6t79En+3aqFzkXjCvJuU/7rrPr169/eq3'
        b'Bua5R14OuPvovUv7Fd+t2QrTHDdd+vWfZny7xX36tzd8qqubopzzgw/+PPcP496Nm/RB2M8Xrj0TkvjaD122Kb7bN+m3r22vfiu22nveDxtWfBYe3vBl/hfbEn6G7weH'
        b'/23imzl7l/+o6S+y4Hn+/1n6k+r2DxPPfTHx1uF/X73nc++zObk7b85pvH6v8k9vhP/y1g+yvkwVk/8S9XnLp2s/t342//09lsUfLFg0+VbVx//yr7dWvO65vTR7foRi'
        b'1oLK+H9e+pc3X3zxSeYff/bXTe+cf1JzYHF9l1X3cdYneoee+QdfbTLf/mD61KXBMzx+uvuTP/7zlh+/5HDkuz94I37D9z7YoPV696MPHR7lJK93+ZHOwcw3R+9abJ8/'
        b'd0OAb3iAXFATkAZMOWxmt2hhJRRA2fzACH8/XSBW+GMRLQrhr1a5l6ywxOzNGZs3PIqMDYCiWMbbCPi7BM0mOZbL4IJZyn5AkxuWLFiORX4BgTIa4LR88QurzPyw7Ryc'
        b'3k4LdDPQdgfTQekOptwAPyxeIBcCaYuR9XTN44KuSCBQLDl8KNo/AsuJ0y2Ru22aaGZnjyRNOzyMlBqzpBEjlxvnKgRPzFdQFH4Km3XyAbmvzsTclc6Jf3zTt1vCl56r'
        b'Uk1ZLxsytanSzXCBjAetGXDmXjmB/cF8oriDeccTgk4pU8oc+ctNJpdNok93ejnL2HUXmZp/l9Onmj4d6d2FPtm7kuqpZV68FqvtRn8pWS25t8xEG0GIMamY/OoBJRtz'
        b'QEHsasDBxlUGlIxcDDgkJJgsmQkJA5qEhOR0gz7Tkp2QoFP//SnqlCZ2A5SJUWQTw10TuzPPxFgzH/cim507m91J4RNvuZpJz98tM5n2rxxfNUL3y6B9UPmV2ENIwNMY'
        b'D4RlkRvZbXQxWB4bcUyuEtyyFc/PDOOla/FUSqRlX1SMRPFlgmaXHDvw0SHuLh1DYgYDgzDsXIA3M5IVNkKiGsrug4TBm9eUqUobp1cUKojTK4nTKzinV3JOrziutHH6'
        b'NOL0P5WN5PT85sUhpN6UlaHV22n4cMI9nFyPIM9b/w7HNxlyLEaTxOyyDSbi+RkSBbXfUTmchMXauRkJ4reZRjRmGEJNpiyTH+9MTyUpY1N3Ji8TV6LvIycxJm+1TUpq'
        b'MXKGYw3ByH5Yun6f1iiFHMlZJpNBzM7KTCGOyjm/mJZlSU9hHFaiozz4sAUcY7PVUCOb8jNyTIGQXhsUYLZkE+m1UWCuNeLuvqyGPxtI93e4q3IUd1XFWFYz+2xfQU56'
        b'xI2b0BPM7t0sivLb6A+tW+lryQJ2+2dRbFREtEyANijSLDdD71bjz5p+qRBZP6lhx3+dGPgLnT5cn56anvRJ4hv0+iQxXL8/tVzfarhp+CTR781W/U19VLJz6k29Y+rP'
        b'699OlwkzfqPJaF+mk5v5proFVXM1frQRsAhLoy0MEZdGESZOhx4ldrriE7OWqnlgE3ZGBm4kTIQyrIASZymungp3lZkUW+vkw3b5WACgsm/1AY10u+4zQHOTAC2FQZkH'
        b'BzTTuGcwpBpwtBvVgIPNPCQcYffOmlxZnaHDK0yMvZkYjkjVOL6wDt8agi9tHkPxxYdRW6yUPZtiVM7RZzMUidCvYY2hHe6OykfcwqoNRMDyoZuc0DV/xZ7IJVCeQ1Vv'
        b'wBNnIQkrXYlYNWO/FIm0TXxBk+tGBIwI4hoLth3UckqRDU3Qp8nNYQWFAtxQYB08hXsSryyBtvR4o4i944KUgpzknCQsk/hL11o3McgkF2RZwipogPtY6ykVNOH5UE1u'
        b'rpq6OyN4LMXaozkEj6zIf49+EOKgfBlBHM1uKhUcft4hkthW94jcxxq4z6UQsSBrPqGmTJBDuQx7UkLWQtXY4LiCgaOCw6N0V6/c6pjqOAiSyr8LkvkEkv/5VYkPvruH'
        b'pz2+EiIYnLDqX58++IqonjX+Xw/qk9O5WKLBPDqMHyEg00tWcrKF0DAzebSg9kA+NG6tNoR8tomh5XryCsnmLBOF5tmWpHSjmEYdJR3mNW3oHUKhvkmfPqq/dbQrA4fI'
        b'pmeLYuE39vttCdnq508f69ezj5DYzYvok8TzWxe0jheEhPj5j+pxyJz06WLWmOkINkmu52wpCUG9pjDgPpw9QoHs5xu5xMEes7JHe0L288284bDF+x/LgrA75zWjPIlH'
        b'TBh3JXA/evtIT4Jd0P71rgR7xvPQ1yOMpUsezBYSE49+tHK3lAG584KHMFu4RNs4cXd+XJTAc+w6rDsMJSwpDi0sh6KP4XCyER5PhRIohEJyexNkfjuc4hW8k+mp4wRv'
        b'ITxUtTAxavduVymoxts7Fy8W2EFes7BIWDQjTrof8y52Zy5WCmosEIKEIOyew3u4tmi8oBXivMZlJ7r8Kmm7JEZo7noK7ykmh0YhToiDuixe1+0Ey+QUxqvcE12EbW7C'
        b'Vgrj2ICroTV4MeOEZjaeCfukAW/jnSQaEO9nsgEPQydV54dwcA0rqL7uZVYdeuEhR+09FM6e48Nec2WjOsND45pUhUK8Q4VbZuOc8kVusNAl9Dezo6/5GfS/enXng3UO'
        b'XisPbWx2c9N4+Ctni6d88k7l/TFqdntf39+e9v+76v2COw5rxzmt8b3osOizQ6Gbna4eOvCdQ3MufSrb5zVO3bHix0fX+W6vnewesG335lX/+spzXf0bzy50+17Cp72H'
        b'su++/+Bm68JfXTvkMfufZPHzj2wI1itWtR947cPbrsHHF79V8x+v/D7r9Yk/fPvAa0/iq+Pfnrbkh3Oa9oz7l7emz/RY3Kc+onOUArL8XZg3P8B32rzBgGzRDCnOKcwJ'
        b'H8IJmDu0RUoSK1iHTWZ2/9Jz2ImlzCVQVMZCswVUJ4C1iXQQFmHHIrymjnDeyGO8tVCP1ZpILNVJHIP68gRrBjxROlLJIzM3b1rThxTjkYPJlc2Tr02GIjPzS9iGnbQs'
        b'JVi0YDfmxzJhj8v9oBIuSpFfexB0Y0m0Pz6ZNBixKaeaGdk/siAuEssibWGlIGx3G7dQsQ+u5ehkEllw/MYx2jP+4iTFY+RjOHtZKLGXE8T4bAEZe5dTWOXGQy83mVLO'
        b'wqzZ9PKyvUwThvCbZ0HRgILgfgit+bp4SjEknpo4SHVY378dQnUuTB1JdbbBNWdbKOWYAeU8pBbGo1VBBKYvSCeTjpCXRVmmjThAuf3CsEd5Bh0+uzOJ3L08VT74yI7s'
        b'Kx/ZsTn5L98YhnibJcT8CkKfyvk4981DDyj+tyOgMSGb/chHQbY6xvICs9br2EHkbIzHtobitQs+GQOyL2O3lEAr8owVc1RYMc+W+8aHeF+6Za0P+rGD9hAWR2PpFiyM'
        b'kntAA54NJZ5/Bq5DDX3RCXHuDtB7Ai4ZX/pzmJKTNceV7/w60Z+HEicPS8HEa0npqR+lCG9G6aJ+UPqd/XO+r/t+4pRX/S+6FaS+mqh+w0VYpXHReHboVObZTKTTy/G6'
        b'HTP6p9tDiUHIwCrMN/Pzvl68sGb+YBKIYolueYAHtJrZvft4EktzhyaChMT9PA+ERKZ5HihJDReGwcgUfwYkSkcPrOAV4IwW8liiqDPQliuS8kTslhlpv8nH3NQO+wzm'
        b'wS3tbt/SM9hWduT5E9OkZ1tWIWUvxo4/ZFIh34r8aRbaMaKHtBVPCh+7Dd2MXOJG1/BI0sTDweyWJDEUwaW/s9vkVuEb77Y02m2tw4x1S3a60SwObinpPIj2jZZdTTXp'
        b'9/HznRHby75F9dolYwbGwyr7hsTGx2zdvNNfGxIeGhK5JT6aIua1MZEJIbHrQ/21a0N4eUJMfPS60M26rw6jFWPsJO7x/xhse5Yv962Fl9fMEyzLmI4O4lX2/OJ89vBj'
        b'UdSmcFswkz2fwhms1MEtZ6g5TK8IKDoswBW1MxTKaPPwWxkfT5EPbUu7h2OfD0VInZuU0Ig1eNqYWVyoFGOZfcx82/P1LteTC12U3zrR8mLp2frlO0577q5x27zCVf16'
        b'enTa7yoLvvW95nVfhIdaZ3XFfvfNmx59l0L8oipfifnlw3Ld355vVwZ//z8c0vq/P8H9R24pOiX3ZngHGtwG90dLLHPLu6GHO1GwmqBulBOFc/CUvOhdke+vlVBBxl5i'
        b'T146bSJnSJvvGu88IzoxkjtpX7Xg5MVu/ZJDw9Ejw8x37O3hTNGIOCRkn2jfIYscZS58j7hJgbvX/8MuYW18h+2SgWG7hCeJy4/g6fnh/n4xPDpn6b2b8EQhTILHSs+Y'
        b'NTopR/giNC2VXBYxzIoFUBy7Bp/wLTX1hDINe7B37B1ly+bxB1EHs3nfwIe9u2dkNm+oG+Npr0x9Bg+JxvBeLCBi56nZBrpAXm64P4mQ9la63mym+CZZT65oeKfcqelT'
        b'pIThqMhuWF+DUd7XBXlSUPd/0avKxvSqjjGWlfTdPRtbR/lUaFj8tWHQrEkcS37l4yUs9LqhoCho95nE6YJ0/tgwM4XcLHGiPJufZYdT/OkPvB0RM9zL4uWgMZwsXoC7'
        b'fIAjhxwEF/MrKkGbmN61zEswhgyoVeI2Ktm5fJ3d9UqO9+PEtNQo/T+k+m/+OPH7ScrPTk9Z4dV9qXbKirVLRGdxcXJXtFOks2bH6sU7VrfNDglQxK32WHrAdccx5xCi'
        b'tiuEfo+JvUp3nZq7ZU9owYs2t7wMbo9yy3Spi1P5gHi4PITJx/L0OZYT1kSrhGVOrjHq4+ug3sxvd9IcsOPTbjjJ8Al7ocnMHt6z7Egn741Pljxz4NIxTmMGd86LjuYw'
        b'+JIHDQMwpSP2g5WnIydnYp50yhPmPUyE6VCpxCtwbo2duH9dktGF+3MyZrZVOGRNskNWKAMqF5mzXHLsLjLT1CGgNaBhIJeQZWJsYAh4jTkgSfPcIIyxXlYMg7HXPEYe'
        b'YuyPnBX5TMHuUDBigvXHdYqYmDCdLEwnjwkztvYUyMXPqc+86Ivx54xbJqx1L9iXumzGu24zrfcPXT109ea1Q02NN2Wq0GMutb7O61Xv/HviP74T2nTo+J3Pnf4afuT8'
        b'xOs/Wbrlnd/9ZPrLwWuWem91WBTbJP7z+hM/Tv7QsKvq+9tyYqpSP3HUbJ7yxaxVnZPMXWGhfTs3/eMUfeP3dr6Ph6Phn/5pRXvYS3eL/dJee66yvvxHsqW73k6IcUze'
        b'ujl06dIfb96wWjd1x/pZJcbGmkm7dsLmi111nrdTPNuMya4Hdn735eA756LTUzUvvf1q7sDbr8Tkdl1e/Ylh+p+XL3zTZ8D7A3frry7d3/2d8eWm0phHz7/h9Gj567oY'
        b'saCn7v1Vq3e7/2Jm9UdVvw3a/tH7rea3HsTUHq9xePBKtHrKe5PuT/lF+aGV1x/P//jIt44FlX560pry+meF3y39h+85/SG/pXRR4Etq1a+TTq/64aE3NHNr3vvwaGza'
        b'3COK8/dW/aS94JFDWduexW//4mbQm7MLPxwof32g/MOf1uf8oM7nz+e39Zmizpui46rLlof9NsX7nYb8P1/ZtjbjrOPHJVXf1v30L5/OP/qb557+Q+dnv4mqe6uvRvdv'
        b'3ykLSDvfF7DjLxMN8a9+Wv6r7pk+Gd/6g/nmX//xjU/rx32urJxU/Lvqzm/v1D3X+p8vv5L6xY7fWx998N6WtdU9mqP1ERN75v/1/dLshEvzcxrif9F/8WjlAUN6/2dP'
        b'Pom+9uXWoD9Mrhbe/MVfPGkfM8BbCxczyK/JDDJB9jz5wkNwRyLMhRM9hxKCdLDatlQqXOaxfKI3tA2J5WVYNBwAzhL1Zv53DTyegiXEGsoC1IJ673Tsl8+CWujgYfSs'
        b'2XHzMQ86NwZgYURUjErQQJccr8Rt5kJ4pYdEQpmaoS+VY2kEK++UYyt0Qsd/8xRU5/bfqv7V/ahMbNOP+cbxwTEhIT1Ln5KQwLHhPbZjZ8nlctkSmZYfnnrIHZWTZNKv'
        b's0pO+9eRv//f+3WUe8jYr6NsooJlHbxfkNMMJk5wptl4ybx95bKp4+g1Xi4zedsxkmBOnpAwBN1c//81LjNNG4RCNhCzPulo52dzR7G5U0HeUEJUtYK5Y4p0KhwEtylw'
        b'D28rpmHXfuP+7GaVWE0V1xW/HFDy2BlenLj+l5nBsbOcJ51Oe3/y5wsmvbr5wY71EQ3G/OZd+u4Tv8k8a0x9Y+FM/daJsaVeP9qYVVcaFH75ptM7jkt2/brsvYvHPz5s'
        b'2Bv4UfmkY3+9ubdMG/bu+50/+nbRz4t/++PEyl7zu5MPXw3zCb/+p59Ncvud7sGufRsWNhhe9TxzIPPB9XfLj/j8NvIHS/42yWfCG76/e2FOyLzVv8nWuXLLXwKP9Cwv'
        b'FRtLE2FZLw1Fs9CcgDeV5NBYDXi0G+4zptDFarHc1XgHuIx9CmgIXcWP1rAf2RNLXBnMFUAZV4YHnFmr8NmCZVKurmc5XI2MiPaLdhDw4ja1Uu44N9PM/MziRGiZv/HY'
        b'ApUgixTwkh47zPwppTI8BeWjDhnLF0TS9i8n31OBD3IUwgbocqCBbxILYHmh0IjpI5v4H1ILk9cr/Y5jERc3Car43fKltNUX+OXYwCT2pakWJRQswxIOJnhnWTaLpGZC'
        b'QySWOAjKABm045mFnJPgaRrvIveCz6RRsJs0Gp6Dy0q4EUngxrwqNkCvEkt0VFGyE5kwbpPrIkX80nDekeo5PGsv9ocaaGfT46GbTNCym6eJiUmLcBdvQeP8WH8sZlKx'
        b'dSJ4m7wD78OttGFRybT/GfT5H3yjKOor4MuYaTTb4IsxOMGV0RmKxRRKGQMAFo+5c4rDSI6zYjajPgtMPoMQMH1AkW7IHFCyk5MBFY/nB5QUG5gHlCnGZHqnuCRzQCGa'
        b'TQOqpMNmgzigTMrKSh9QGDPNA6pUQk/6MOkz91FrY2a2xTygSE4zDSiyTCkD6lRjOkUtA4oMffaA4mVj9oBKLyYbjQOKNMMhqkLdOxtFY6Zo1mcmGwbUPCpJ5se7hmyz'
        b'ODA+Iytl+bIEKdGaYtxnNA9oxDRjqjnBwKKFAVeKLtL0xkxDSoLhUPKAU0KCSHFXdkLCgNqSaaEg4hm0SZOdZmJpLhP7v0kmtj9M7LlLE9ObifF5EwMrE8urmNgNQyYW'
        b'D5rY0+om/s8blrA3hlsmxuFM7PF6E8s2mNidnSZmiyb2vJ6JPYtoYg/WmZ5nbyypYJrB3tjOMbF/S2Bi0Ypp4SBQsuVwHgTKz9cPAUpe9qWj/V6gAfeEBNt3m+f6cmrq'
        b'8H+apc3MMmtZmSElRufI7tFJyUomndAXfXo64b2PzXQYJ6brzqR+k1k8aDSnDajTs5L16eKAy9CozLTarsAhb5L9rZL+M9cadonny5RypcKR2VjkROaUZP8Fj2LCeg=='
    ))))
