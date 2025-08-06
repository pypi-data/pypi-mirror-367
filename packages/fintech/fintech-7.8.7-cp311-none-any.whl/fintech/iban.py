
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
        b'eJzVfAlYVMm1/+0Numn2fRFsBIRml01wRxTZccF1VEBopBUBu2kUd3Gh2RdRWwTFHRFZxF1RpyozmckkE3BIJGQWJ8n7Z30ZMmMSM8kk/1NV3diok2TeN++97zXNpc+t'
        b'uqdO1ak653dOVfNzzugl0P/94jBcjnO53BpuI7eGl8s7yK3hKwTtQu41r1z+RR7HXeEZaJV5roDPKUQX4fOV8VqlnNr8DT7cN8kVTqxfzoO7poqXuPC4XNEyTrJRbvJl'
        b'nlni/Ng02ZaiXE2BQlaUJyvJV8gWl5XkFxXK4pWFJYqcfFlxds7m7I2KYDOzjHyl2lA3V5GnLFSoZXmawpwSZVGhWlZSJMvJV+RslmUX5spyVIrsEoWMcFcHm+VMMuqU'
        b'O/xKyUj8Ai4VXAWvgl8hqBBWiCpMKkwrxBWSCrMKaYV5hUWFZYVVhXWFTYVthV2FfYVDhWOFU4VzhUuFa4VbxaTjnNZN66S11Yq1ploLrVBrpTXT2mnNtRKtg5bTCrTW'
        b'WmetvVaktdQ6aqVaF62Jlq/laV21k7Q2ee4w7uLd7nyu0m3iWO72kHB8bpf7xLtwx2PiHR63x32PxzLO62vLtnHbBau5bTwYZ35ajrFWLeDXjgyAiX4qLOPkkrQCMVDH'
        b'vAUcmQn7onaYP9oj5DTeQODu3fgwrsaV6SlLsBbXpstxbeLyxUFmqMuE810oxA9thfTp7ERTzpzjrB8F7TK/sT2Q02TCTdSEbuLbuF9isSQBmNQkLk9AV/2wNjApFTcu'
        b'E+PKhOXAtA7XB0ADuC4hFdet8EtIwXVpKenL/aBAGwLNLUlIWu4XlIDO5SUG8lCnkCtBlQ5RS9ERTTiRsC0VHQTmE7kA2+oQvvWShMBkXAMNp+CqRBFXiuolazP8c3hG'
        b'I2JpGJEGuBy1qIBRoSoUgvpMQL1iUKoZKNEcFG2ptcqzpOqDyV0pfEl9fKo+3ivq47+iIt4evl59ry37evVJX6O+Tqa+C1lMAaHxMVm7N63j6M3P8/lUp6F5eTMShIXs'
        b'Zl+xmLOGe6Hx+TPXLchnN08Uijj4Kwst/czGX+nIXeYKzOB23UZn4TNbbt7i+T/3/Zx/c9onWc5cgQQK7i3UmQbysqy4eVlhH4bt2Lud3f5p2ueen03ym8xf/JT3d2fx'
        b'nhhulNOEQMHi6bgZtFQdssTPD1eFJAThKnQ5ww8mQn1gcGJQUiqPK7TCreimZDbuQ3fkIRoHsl5h8t3EV3C12hx0hnUcOjY/R2NP1JZrMwdVq1UiuF3NITKLLmjI0OC6'
        b'VatXoYtqlSl8ruVQ1UZ/ykqKLyzH5WFqfJNUauBQDboioqzQLTFu2WGuRnUwVPgMh9qs9mgcScExdFaJqwVQwoeSsxw6VYpP0iJciZvRiWX4qnorkaAe2kEXF7Gi87hn'
        b'OWpQqHEfaAkf5VADbt2osYWiomg/dFOt1pBHGjlUvTRG40Se6EXn0B18Ft9VW5BHTnPoRCmu1DgTGXpxBz6DmzLVuJ+IdxzYoX50j/YJ1W0198GX1aiGcGnlUAu++wZt'
        b'ySMxx1OllhKx24FbBDpBu2qNjwfi2gj1NnAJ+Bg8n4DraAGunLpgNzqituLYEzp0Yytr/wC6CEv4gjXutyDtX+XQadyJ21j7+9CxqZvxDSlVwxXyWPM2NqaXOT6ujEPV'
        b'oDeemEPduC+C9fV2MN6HbqILanyNqLSJQ/X4TihllzHTazmuxf0aARvtZnQbxKOa6ClED/BBfFmKe0lTPaAK79lU36ga6eK3blVv4zNuVau9KTM7yRR4oFeNbxGxT3Co'
        b'EV/2YDOkXlOaPUdtpddpCyoPp0+YT0a38ANP3C8mJec5dBKXe7J+9tpYQ/tnoYi0fglal8ro8KzGvTBdD8E07S8RsXbqQd/1VGoF7kJadMIK95ubsMfacK0jG9Y7uB3v'
        b'ww+mQhkZhg5gia+iQ/Q5FR5Ah5JLcD/uI7Kfg4koQ6fZQNzD5dPxpe1gU8lj3Rw6443aWFHbPHQO93JQpB+is7jHgWpDlJlZNAPuk3Ht5aBWFaqgBdsKEtG9Yhhx/bRr'
        b'XItus0l8Nwd1F6LroHUee+isOzpOizwlXujsIhCun5R0wjCBmT9GlbsBX8TdRdakzJTNlVPoDuqnY7jCiRPiJtCfXu42dAvVUCESUV0hOjVPKiYlNzl0IQAdpoqyDMed'
        b's6Ol+BphdgNESNtEH1iOj2S4oevSUhFr5IQYNbC58GDtEqvpUnyTDFsftDF1C9PsTFy/FvdCAelnP5nCt51pSS6+rlqGQKybItbGGdyaxXi1rXWNF6lLiFBaDh1WoAds'
        b'LhxNnoQOoV6pWshGGYySlo1ZHT6Nz6BzoVIz0swdDl2cAWpzI0XlUnQdVUfhBnQD1XhjrYgT4LO8dHQqXONKmJ7HbRJUXQpGpRYsiVYg4oT5PLTfPlMjI8U16D6+hA9M'
        b'11cJY3xEnATV8p3miOQCuugLcIPIDcxPNei5iCvCfVJ6e+EOfCcQ65JB3g3cBqSDNWVDZGqy9scH0c1kEDaXy9WE0Mr4oMeqDeoX3V7iSnGAedlefARr0ZUodFmUnYpq'
        b'8flNcRk70bk1qVyEWoSOmsGMIsO2OD8G9cvVdDFUcqhiBz6gkZMuHMQn3RkLvM8sCgzCUXAIhGEE3Dkq5CbhWqFkEx6gGla8kbUGH1Tj6zxmq+tQa6jGDwr2oquWjAvq'
        b'iwEz0kHYJKDucS5oQCjAt+0olw08dCcXd77wHah5tWYqEUYbF8G4pK2PQleNROliojQJTcyXsFXVa7sct6NGsLHEKpziUCu6b0JlidwGK+xIAjxzHHfAuIyzCSNiAZsg'
        b'kMQDVVFZSjahA7jNXq0is6YChsMaH6ZcUBO+sckwtt10bNH9TVIZrkYdK4R77bgkmak0HZfTyafGp53BST544fdsULkmmOjtbGDYOJdxSVAPriV/OuFOOT4n5IJUoq0p'
        b'uJGqunjdjoW4/IWj9FimCYXbCbh1Bu0W6VKtYAM+hR8yocBwtIDeUTUoPQHfNsE30Bl0gPkb151h0WDS6TIAm5w0jQ401OiCuWLgRnSFm8BCdkcJl3JuuF+Ae53xEbZ6'
        b'boBFPK9EPWozPlPXUUfUpImGomD0IEGvdKJx2iNjpXWkEvZdqSYbUrmt0OVT2WJidjYyS9tB3MAufEaNqoTMyrWCzb+pCYTCZE8LIlz3uPYEoI5KfBQdzgM3Ww6LrIWb'
        b'hk+LUB1vJrVwqFaCL6LrkcYwogvMPZniCTtxo36GV4frJWRTs5NNzSMCfB+fwPfpiPHW4Q7FZrUl6WwLzM2oGI0/aaAPnYthXJbjUxPXyWU2OSuEpmBhj9MJge+YoIeo'
        b'ycIIvDhl065t9Ap8MR8MQyZaPmG1ROwUoRMeMLfIyg3zFebZGUEd3LlAM41IVBVAVKhf/C+m1vkwYFLLFECYheF6EWrH5SbMTB7HJ3G3v7kxPkqjPXTAbeD52DgNbDSs'
        b'YYMqWRevCsW2+Czr4cn1uCs00whNecGcI5BSkoOaX5EL+HWx7sJSLqNTHlWJ1Ei3isGPW6gO96Be1A4MTZnDbk7bycqqwHNXzsUHXgA0EPS6JgDKZk4G361viyymZvCV'
        b'ZWSeoMMydHYFOrfFjkvFA6ZhDpup1E6m6Ago++ELQIcuvaEJgpI4PAATcoItRfdzcNsmfGCNXxQbADU6LcY1XqiF8vLehjt2JRrhP3wZHaWL3hom6C0DryuvrHoYgej1'
        b'ZACOidS4MpYus6X4gTfAkiY1c9FtxCo2Oen98IUSVBP5AjXi/jlUYxb4fIGhlat664+7wjfFxcnwEbBSdlw6PmUa7IKa6Tjmw5pvAiTQ+AKTQYtdVOKYCEBV48Zlgths'
        b'JmyxFMJ6vyfaBCjxNBXLGVd7QY+vq7eJ2ASoTU5jLqUH7wdUR7jZ4xq9Xia4FF8BvoebA2nH5bgDVaxcZowHj6JOjS81PQXggJlUVQY7RVfJVcLGDd8U4L7F7lQaFb62'
        b'KhKdAzY8Brmb9wQzxHsyPTAQHTeClYdc6TSNwgdQzUtLEZqYC7JOWItbRQCfayPoWkwpNMM9K9VWPAZEW8XoKpP0KkzSM9RkTZpiJKnB4wgEuCcSIBw1fNdwAz4qg9DI'
        b'CND24RY6dsWo21W/Bg+iejJjXlmD54SmaCCPzsBI3F26GhbOC/g7E2ZgFNEnuggh/iud0/MSomvm+AHuTo1dgK5OhbE7Kgbksi+HWQidL6pOX28EnHFvPJP8AepGA1wG'
        b'WDkKAGAuHgOrfIcOAegN3AZtMRjVGLnMOJmIi0DtIgB3d2G2kSaConIgfLwBGJvo/AKBqlenU6XsEZhOnIbEzp7JGB8DarHD8UkRzOQLqIfOIHUAgNZTacZo/gGuoj4T'
        b'37AA1YzbonGfS9hdKwVKACNhsSmSt0RkGo3LV1J+mVFgZHuw1jgEqNpMlwkawM17k6lXAy6EK34IJuTqOPSiwGspqjX1nIQ6mGe6Cw+d3g0msZ8BZuhuy1QR1bYHqsRV'
        b'xj7dwKUaN4cAo3B0A1ycBaqknKzTYJzqIZbstzRlEPccake1lBMsIjCvlFUEvjZhBnaytdIHUxBfMGOKBAsvAol6cD/zK9cAE0+CgMAHCr1Qt/8ExJIQhC4zZDAJlZOV'
        b'ewxdZjPlAG5ejnqkuH8rny26eoEDtUy4G5ZWD+OyHl99zYpAFQKYDpc5BubKV4D17ASb2b/VhFm/hhUzNVNo9LxIb0sMTNZC1BrFJzDlFiz/zD20R5txK5gNrcQ4NsNt'
        b'6AZjfwgd88bNwUbB2UJ8TR8boD5xBr5iFJyhkywxAYFBXeiSRKPwzBc8Mh3s46EAuCjCbEN3JhimbjbYvTDYqFNMm9iALsXCCjIK5gBrNLDo/lZy6kY/KNGvpiYrpKOL'
        b'aQk+40GtCTpTqp+xFA1df2FPruNTLDyGWK4v0x1gZD91jwA1jliu0YTR6GYOvvYq+MTn0J0Ig1Ggs2MabhEBm1tmzN/Wow7JQhEM5Q39gjoB1q2Krs+9Rpije1ysm6gz'
        b'wgAAGcOVItQwDyQiA/AGeMOD0TshZOWz0W8HfH6IzZPm9dsmejB0fxVqN/Jgi1NMY7AOdbOu3kCHCietMAp+wyHCJWAIP8iCBTvBcoCPmA9h+YSBC0cPRbCEmmECO+rj'
        b'4mNeuAsYilhkeg4fWEQtB6CiTRP48XP05swaH5mhRLejbJA2kodOzjNLQ42oUZ8Ogc5ULNtrHISrl9NwIm8dZtMYmPQb22KDXZcLAANdms1sxhl8I283mZUvAnZcnkU1'
        b'gA5DPHv7Nbjvyji4gGFqA3ihERUvyKDjlqQAFfahUxDlmzB2rXEKGgj4B+pjJXTPc8JEvsIm8h0BvhayjArlAjbmIr6ZapwqaMe9VI808mYybcOVL2FHfRj5UGiJbrO8'
        b'Rwy+siwTHZSKTVhwfx5fTqG2Z0rhbrau9ssn2IwuJk23AHcnOrCp0IBbiHb9XqQn/PYw+HEFnbV4Gcj5ohPGkyrQdLo4kapsDs33HFBKS/Su6AiM3hWmTW2QWxQ6ZJTn'
        b'QMdhfdIkRAc65blu74uEwso82rFAfGphIropLSXMLkOoJACnTxb0MheNIVJa9LoFTczhw7UMyqxE9wG+hEpLTVjy7rgYQhOSUk8BB9z1+kmJ+tdkYbiHD27C59Zwqs0Q'
        b'aUH4+4AyzFgBymnIeZGXwf3LaSyCT06BMXzFQIDKRLaoTaYPs7ogfFjvxUxDG2jz9GR8zSiXk4Av0hUzCx91G1/LE8CjwS6gu7icwN4johJ8iCWSlXOdkG69UQIIaQEj'
        b'EKGV0xdtRPuMEkDovj1Ty210CWo1YZ3UkqgeBqsjz4FZgcOkb692iI/6I4zcPzF4ZwCPJDhQp24pgKBoPIaglQBPTBiPbtHWSN5isWmUdSidY4m4XDmhr1SZXaINCJw8'
        b'vgeuO8xJhGosndmMrEMdq1h15V49stZrn+U10DWhEDDzfmop1uF9hXoIeBxdnKiXq2wpVQnFW71pZVyXDQ6ZTAlX3DDRrLBlN1OAB2agS9QfrIZ+XXvVcuDmdS9Zb3xE'
        b'BMH4LXxMzlyYOTroBWCjS2pJXOEDDnWioxAEURd21iTeElVKcZ9+GZ6JDGY2DEJhsFXnvaGIPHWbGNcHEfoyYF6LykOkEj7T4CXwZ5cZXq/xxmeDZFKNPqt9HJ3cQYWw'
        b'wjXQ/1NgNsYzfEvQSSbE3R2B+bDs1PqFego1mrP83VkIaishsrsPkIravgFibU7jCk0kBTBiKyg4grSGDN9V/eJEWpoTFEIvLq/NQNXLuZXrTOC5+/ikXKhxIW1eRq0y'
        b'XJ2SHpWEawScAD8AZ4AG0CE6r/PxWWkyrkox4fjredDExZAY6B9JORbCKuhLxnUhuDZgI7omJxtn5tYCByksI9LN2WA/qwPSonBLUIKQE87jgUB96vgc481gsqNDt5vI'
        b'/sJRE8OG6XFOy6M7Y3wtR3fHBFppnoTuiwn5XKXJS/tiIrovJnxlX0z0yt6XcI9Ivy/22rLxfbE8Of/TMdComczoFUc2gNWy7EK68yvLK1LJSrMLlLnKkrLgCRUnEIls'
        b'39l/c1FhSRHdQ/Y37DrLlMCtNFtZkL2hQBFIGS5SqLboG1CT5yaw2pBduFmWU5SroLvQhCvlp9ZsMexuZ+fkFGkKS2SFmi0bFCpZtkpfRZEry1ZP4LVNUVAQbDbh1ozi'
        b'bFX2FpkSmpkhy8hnG9xk53vDOJfg1z2wQZkzg3Rzo7JUURjIniICzk+MmyCBsvCVHpFXDgyMYnsJ6YIiOydfVgSVVK9tiPZNVWbcWIlBTBjKf7+dErLXr+cWLEvVqEtI'
        b'H8m4L0sPCp8WFSWLTVmcECsLew2TXMVrZVMrirOpYP7kk79MAVNDk12ioEcHsrIyVBpFVtYEeV/lrZefjTidWvq+yJYpCzcWKGQLNaoi2eLssi2KwhK1LFalyH5JFpWi'
        b'RKMqVM8Yb1FWVDg+SQPhbnx2gZreJoO8Tal+qTMT9oJF3Kt7wTZp8SzcaEd9+CHNvaEHYGdI/i0+lm70tsY7c+BGQ3flZ+1a4y7hKM6wNoEot5rDXWvAenOrwbedpJWT'
        b'lppxYPj83picZd7is5RtFWfYW3GTOE48NTQrsGPpKhZa+aMadIiljgbm0uwRqkDn5FY017lzfiEtmmNHS9ZhltnBN6QOdCvSP5RuRiIdoGyK2/JxN92KDAWzSnYj8bG5'
        b'1KBvBed+VL8TWQsekOxGWuAm2gcFOjuNbkSiI8l0L9Iqie5zSNKE0mJoxHQTCbGP2yto7SSwstKtcHtrDgH4J/GDJSzdeBvrCti2ZQbupDuXZ/fSHvrgw4B0+tUw3HCz'
        b'gQRATeuXMahQv2Cpfj/zYhHb0mxEnUwTjfgk2UYje5pe6+iuJu5Op0USfLOI7Wfuxr10SxPi31o6AJtgNMulZGg27ibO7hQ6GkDjTx98AZrup+n/bpJjJdvB3egWw6pn'
        b'0YVM9TbinE6RDDHIsY6hWD/cHk+zcYDv62lGzg9flAvoSHgtSGVF7atoCboYwyS/A777AGurcBFtCfc40UdWp/FpM6i8kLYiw0fZI/tQy2yWqKTejyQruYVyPhUdP0Rt'
        b'uEufxtTim7TUAV9igK9nI77P9rFhHpTTveww3EbnG8+fnmxY9a5vlvmHSQs45r51pW7hoaShSwD0IPg9gzuUX733iK/2ADWssPm8dulAGg61npO5q3Rd/lvl1naC+7yi'
        b'R9LQ0PbfT5f5T7ttu7DD3WbSzA0/aPYJqbRbeqnQXX5sSsCfv/rwLx98dTvTun/+CqtPgz23dY796A+f/VT8ZfqbS9ba/3bygZ7vbXW5srjH6/99NkkbNO27DkdUcf+Y'
        b'8tvVvd3lce7rjgX98FbIrjt3Ld1P/dHyHq/HIbD9zR+PrQjMump93to+ad3dg/mRDrkbvth//KuAxHf2SmqTDpp80GuqXOV56n5n4ed/jW1771cXl2yb2THz3V+lnfv9'
        b'hgSnpsSSdWHvu3n++q+nDn1vrbngh3/q/43Ld1cdOfcr7eYzHgHyme+9uaIgu//kd7/8ojc5r6az7ZBzU8yvBxSf1ygffpxx6wd1KVH+mk//YvuPjz78YLKDS+6Zjsbv'
        b'T5abPqPo6NbMvQFBfgloAD8I4nMmqIUfhK/OfiYj+jgKiOR6QHBioL88GNcH4kqSiO3EDTLhepgY1c8I6iERfktyehCqTMdVi2IAhEiX8HHdcnzpGVX4ddTiQs4O+Qfh'
        b'uj3BPGihnB9eUvCMbnvds4e13Y/rigrpwZ1t7OBOaZA/rgrhc8FoQISv2+CTVNIEp2W4OjUwcSbgrDqOM4ngW6IKfPaZF40t8IGgZPY0qsP1KRQmOUAEcRQfFODbqHWd'
        b'XDrK95OryMz9Rhc1OW4jk+0zvL50mJWnKtqhKJTlsfNpwcQZzxk1o64hkxA7jD7zCYs34Pp8Hze2WMTZO49xPAv3EadJDZoRO6fjM5pmNM5qnqVdMGJlO8ZJLXxHHF2O'
        b'K5uUjZubNzcIRuzcxzhTG89270shZ0N6vYemTB+eMp3eGuMLHXxG3HyeuAU9dgvqyB1yCx92C+9V3yq7VvbI9tGyoemJw9MTH7slDroljnj5tUeOCbhJSbznT918ht0i'
        b'QQgHnxeXkcneOo1OMyaAz8+fP3/qMkXn0h7eYTrkEjrsEgpVbDxH3GS6yBEnD0L4jnh4tnu2x7Z7teY3LBqxchzjbKBPrp6ng1qCToS0hjSYkr7NbZrbHjFk5zds5wdd'
        b'Axb0ad/FPLg6G65PSdNjInrDhHN0PZ7ZlNmeMeTgP+zgTzsKTw1OjRp0Im8qJ3TEefpTB5eJNYW0ZvvmQadp8B6vGPbUxf305JbJHU5DLtOGXaYZ9cXOiRK6RR1zBifF'
        b'wJvefj5i40BVpPPWqdp5OlWrX0fwoGs0vJnSHF11YbpYXVhzvpZ0XacctPKFNyu0d9dtHLaf+sQ+8LF9YEfGkH3YsH2YduGInbHarVxAXIuIESfPJ06Bj51IPaewYaew'
        b'Qeuwp/bOOhudrc62OUG3bch+aod9R3YvryOnywVYNfBGnPwGnfw6bIacAoadAjpKHjuFD1qHq4l7fVMcFBvNvRltNt9EgEQ8uJI9XU5uPiok83BUABBw1FQPqEaFBAGN'
        b'mmZmqjSFmZmj0szMnAJFdqGmGO788+UARpjLgpdhSajohgjxL8bT/hip2giX5+QFU18p5PGmwhj8ly9PLZ20ysrNNZv3Scf4Ip79iNRWO70ypibmqdBqX/L+1IOp+1JH'
        b'xFYjYjut9PmYiBNZT7y7L539qEk8c0oSwV23jOULwP3RoxlXU1ak+CaD1cDVabguPVHEWRYLovExdIeGdvhC4fLkFCgJsQebUxvA46Rr+Lgb3y1jGZrr4rzxAGy1MgRd'
        b'9soxnLclL6EBpe0jIRSfhVA0gOIgfDLJE9KwSQBh00shz24hDZsEr4RNwldCI8EeoT5sem2Z8XHCT0d4L4dN9LSsUdykKtoiyzZEOhNjmonxy0vxScY/CaNUiq0apYqB'
        b'52KFCkKpLQzlG47wTsS56Qb4C4L4L4UWlVsUC1WqIpU/ZZYNJbmvj46IvERcFiG93InXhgb6TrEnXu7h65og8VR8QfZGmZJFdTlFKpVCXVxUmAthAA2r1PlFmoJcEiYw'
        b'xE/jO31M9/qAYKGSdPlF/AGxZrYsLKhEUwxxhT7KoKMG4ZEfqRFIGpJ/w/BAlKaZBZSppdvrDsxWpvgnBaLODHp2lpz2rUxPSUzlcTPRPXQFVUpj8HV8KUP5btYDoXoJ'
        b'sFm7v/jk98Lazhy5oXt4sJFnudT5OK/syqdTUmvauqQNv7BpP3LniPzQs6lKl/DFkeEpgYcr9585duZY35EL2guHzxyeVivXnTnsqdsf7s59/EfLuNRyOf8ZOWuEjqA7'
        b'MVJ/WGu4EtekaggkQLfzARVMRv1C3ANU5bPJHD0WVYMHkoOTABqgWoPrd0XXFymEhfGL5Cb/wp6ZjLt3aslGpezkOHPkxgT15Is55snjTTl74swsFvA+cpwy6DV/yDFu'
        b'2DFu0DpuxMXriUvIY5eQXvFt30cRQy4Jwy4JlUnaBQ3e1MXzLKaMOLnpMhp2DFp7gg/SJn9BNMWMtemo2DB5R03101BFwI+KWCGV20TRTZkpJtIzK+xJrLCxzE9ItW16'
        b'Mwxibzbh8byJOf0Xl2/N2BLorpMEc92WswSamRw5tnfB4pUs2GVeNmDNg+gaKLM9ULAuOQLVbUVX0UU0YMZtwE0WAORuxbHo4h4EJOelpZYQm0G86G+Dr+DWbBrfLJo8'
        b'VVq6ldzXcuiGBrdC2MW2gOOD0QE1vjnH0ipMyPFxE88RHVzDIogj1mi/OkzF53hFnGMeupUBUQwpkK+1lpaWmgCzQ5xrEm7BJ/BdcBY0wjqEWnH/i4Tb0YwQSTFLt+Fz'
        b'hfpsmzW+Mp5tQ30Q0ZEnTWNxXQB4ER7HR3W8FZo4fAw3TPAUYsOC1XIvkm3gKURaQ7pNAh7DLE887jFeTrT993iMr74u0UZN3cQ029faS2JbSfV/na76miwSefh/PYmU'
        b'U0DFUitKXk0bvSQgGZeinBwNuIbCnFcFNSSOFi6OlcUB/FIR17EAXGROSZGqLFBWrNlQoFTnA6MNZbSm3pXFKaA/2QWv8JsPpiPYSLZsohQN/VqN/7K4DP9A+LNgAfkT'
        b'l750GvwF8fznh82nBXFx/oGvcDTqU3aBuui16S/SSTrOxSzpBVxziRcrK35pAMnr38IH4xyLil+FBeT170GDCcr7VrNu43jOyK1apcVTv4qPLyGnb/99z0rdavqiGHzT'
        b'jGY6NEXOwmxeFjHtuxYHLmDptqcltnm/5yUQgz9r/vopLGGXgvdvR9UcydZ5oFur8X18niZZlkXga6gaaeHnGDoAq9+OJ8F9+C7l1Otr6fElP5rjQrNSzieu5+R8mp2b'
        b'pJGRXb9p5LhG9TR0HHWw88F16A46Hg4dDuNEjmHJkZTH+3bWxX/kzeO44qyC79lsMvCYh+ozGRN8CZ2ehm4msaP2VxJROd1bXsxt3b4Yn8ZVlIt8tZnqA4Efx1lnBd5Z'
        b'nMBlKL/XV81TfwhFH4eUHVrSZ4ZCrQfWjp6/Wh5deeXu89ltdycHl8f5/6a9+mnx73/Wcjl57+ORH6+IezRPvO3Pn3/83nteZfycSm/VtjXiq9/7z7s9v39n9HfRwb47'
        b'Y7LEAZ8u/tmyzIVmk94w/0NfxcCjwrsHB1ytA0Ib9/E/7q4rbhJNEvEXdcVcnrTxoy9a/ohzXArsM4ai/v6PlkzfdZaoczD1k23VpQ+a53re2TKpxcdr4Ren9v+se656'
        b'9W8bTC63e3l/9VbTpPbvrw356jcK09CgFS2HTtYmfFKs67/uGRNSu+WLc0FWteqE6SGRq2POh7rIxc/03/fYt5lkXljWBV8z5wfF4fs0nbHGG+lewj4h6BRuMICfAnT4'
        b'GT1Z24fBRRKPgirT00Myg1BlCFQNIo8lm3LTcLtJYtobFCbl4Ev4lDQZ18j1/MJRI59zQBVCMTqJTz4jisoIRk3J6UE+VuCfSnmx4LaOUFFTUfNeksIJSSey7sGtgXx/'
        b'dN2F5Y+O4KtBNC/DkjJ+TnxLJ3yWpoYK0Mm9ybg2mSSPUI8bzR9ZhQo25trKJd8sB0NitvEUDMNpEhZsgmPZ8eIjxWgpPIbRdgFGczIKu20djsub5I0BzQHaOArFJBY+'
        b'EIOTJEAC7yPXqYO+8UOui4ZdFw3aLxrjC2w8Rzz8nnhEP/aIvm035DF72GN2w6KGRc8/Yo8YXWjeQBc5JoDPJHti594wQ5fTHj5k5zts5zvG8W18RtymnJ7ZMrNdfans'
        b'bNmZned3snTNi+TLUzuPJ3bej+2825cN2cmH7eTG+QJbrbohvHJ7zXZdWNUe7Z52r/bs81M74s4GtQfdFjw0v2v+aPlQdPJwdHJ7kOGJhmk1pTqXQasp8G7P6fA8n9cr'
        b'GZwaA299DUeW5AjXbW230albo9u3Xdp9dveZvef3PnaLGnSLMmSoGiLUxBB0O8QKuTeFZrG2gjdteHBlgFXK0CmxOqMCcI2vw6lfm1V7JYtAdvaNtPl7UrH6BXpdbcrj'
        b'TSb49L9w+VbTB62SMO6aZSwnkPNYeuC8y25cnYJb0H2j/Vl8C8Cd8bcMx93Gdo6lAei3DIV5/PFvE74E2/57vk345fsTPNtS5hm/JorNo0EoxWDGG5//22H/17pmwWtc'
        b's0kaDT0U+JCfwTHfN/v3fXPMZDfmx/ozUBPdTgv1oJtpIan0YMusjTFgNXFVKq5ZhrUpfNuFEKJoIZw5hC6gE0DIucXWpuTrbmhA6aDbI6KB889+euLk9yIgcO7TPSyz'
        b'eCl0Niehc5aLdc/hL+467/uNrvdycvb8SJv8yTObAsMP766Rruo98cG7+zrDaOC8eLLNT/8gkItY4HxtKep/2Xnw8QCq0jsPAe5llluLG9YbHBCu1pDMPzod/8yDdLUV'
        b'deK7NPOPTqGmF9l/mXD9vBm0CmpFtfnMoWzh9K0wfwLtHntGTy2c90XldGtgQUA6DZfo1kBBqZxvZAmIzTYYddONihJq0g0fqEHfwDGDvkf8tUH3hEz6y6lnnkXMR46y'
        b'Qc/pQ47Rw47Rg9bRI3buT+x8Htv5tOcO2QUM2wUMmgeoyAlQZtVEKvoNvNfF3CSjkvUi4p5BLJZBWGdY7OrN1F6BtFvEPB6J919/+bbs0RcESTVL/LlOy2jBv7Q2Qi33'
        b'P2pt8sDadE5YrMuKC5Ql6nGTwvbZwW7IyN08VfZGum/+knkxmKhsWcRrs2ETKvvFpS9Py1i6OlAWl7AwLnnZ8tRAGbSSnBmXvmBhoCw2jpZnpi1Pnb9wqfybWhKKXH1W'
        b'mXDmuT5CTpZV0O6h5jRkGoicYc1U45oA8mXzypQlCSwRQLIAuEmOLpuhE2Xwm4gqy8hpxl5Ua2JG1iCqpqcRpwJ81xk/D6YkCVU6E3/igTuE6GwQblJ+tO/vfHU+VO+L'
        b'/YCZjzKeIKrXXLsSl637ftv35ebymqspTcV9aw67Hk67GPb2lL/b5h18YH9RUTOvrSZ0j12O7zILwfwn/KkFNzVh537TqejKDoyPPO7yUYvzh65vi75vvorrfO+AS/QH'
        b'vLF2x5y/Z8uF1Fj4QN/2j6PVQz50m7Dd8hn5XwroQS4+bAwtwQ54JxFL4Ia62SbgYXwu+gVIxPdwbQTfcncsLUwvwneSKWx1w2f8TDiJMx+deQN1yYWvBQ5kWo+vv1Ez'
        b'CMrV+mSd0WdqNkr1ZmO9hLN3NjIPX7OBQ03E3CHHecOO8wat5/2LrZxpUL3dY8gxdNgxdNA6FO4en9U0q3FO85xBc8//kimJI6bEqA9+E6xJquR/wpqoiJ8EUEMPw+tW'
        b'TwJQA4AGVeP6EFQFYe0DZsZd9wrz0cXi15ubXcTcCA3ghvwDBf3+xv+MyTko53+67uX9DWOMQzcCCrO30LzIa6ANyYqQQzzFCrgBEGgi2Ehkhqcgu6REoZLlZANOmciU'
        b'Ip7sXLaF8kp6ZwKv8VTPv8r0sMzO/yXIJU7TzAHqDdyDm8CoPUTnv2FCJEaM+qit/VUQO6o05rF37ZvT57ODRsD2pjdAMXwP6fTfLHRBnRSNoZ6YeRPhGDoXBiDsFTR2'
        b'Ee+jDTzZaEL/Z0ZxSoF5wRRfTnkgOkioLoaS1JCP2N7G5Zf3NlLM277fln9WnvKTrNLGfN8P+N4fifd1ezn7XdsnOfk9xbz7ru//doOwM+fti8GHXH60oD3N/V5MY+7q'
        b'3tsnRfijrqZi9xvzHoZkvZUHtvjuT2PCuc9vTsrXnJKbPCMZfHQx0vEVAMfA2/1luIc3g52daENXthpCf3L6QrSabl/iOrDEqSJueprJHnQOn6dIjAe1a42SDV3oNNjv'
        b'U6iVob27fHwJwB6q3mV80oOc8hhAPbSKsAz1ERMPetxvZOaJkQ9GD2nSYuUMtJ+dA5kgx2TUJEQ3Z5LvNl4Ca/i1ASGxhkbbMOYUU8G0J4tqxwSKGvcLeuMeb/a1mJCG'
        b'zTOHrCYPW01uD3ts5TNo5UP33MMeO4X1zhxymjvsNHfQeu5TD/kTj5DHHiFDHtOGPaY1SEecpjxxCnrsRE5VOIUPO5Ew3Wb2R67egz4zh1xnDbvOGrSfNeLmo5vRvnnI'
        b'LWzYLax32rBbZIOYcg9+7BTcsX3IKXrYiUBNI19gOiolhj2zSEXQ4j8PldnmjtHGlCqV+IcJAzGDeAiNwUNsBQ/hQrzBv7h8q3s7xySBXJflDIFckJYWL+fFy/lp8crQ'
        b'NoFQ3Q5qMoldWdv0y5V2S6zf+qTQ7PIzxyoL6Z8+7sv5rkmUfcYz1wX2DmezUgK1edOzfhAb2GGT+reGvzV+vG7+O/Hawvf//qeB6epfvv+L+0N/a5j9C3FMXHfDzhRz'
        b'p5FDgcNhkXODJY1PZ/5l3m+ilJ88qHvXL/eHGQm5ipalJ1K/3xWWh2adTHrv0Fvbj3Uu+yz5tLjxg5/85lZD2Z4tW75I3lF6+Oe5Ax/zTyvvevzubdcDTbPf82r9ZNkb'
        b'vt5X8abTPnG/DvXv/625bs3Ch8Pyp60NqPD20/g5Zm+nxg75LNae1R7c0Nxwwc/rvSWxK1DcijMtXbFBMabqd8t06cHz3O9YV7/z1qr5P86R3zF/712HVYndaJPK4sfx'
        b'3l92ffDbq981UXlFNZ7sO/Rh51t9Fj991+R3sm0bnO647XxnYEfJZNd3v4qe5/Edz89D6xoW/fFvUyd51f98wYIqZZrv1qq/5l1vuLT18Kxq9S/Krjc5FTcWxM0sS/zs'
        b'b9fmfOYwe3T/lV9EDrg9nfHrhb5lgnW/SC05cqt45n8MH5j54Sdvzb7mtPu81Z/fNf2Vr+lYw7Of27gMPomd/eWqnufC9Hc3OnufztHu2n88N+Efn9kP7Fz+wdve263f'
        b'Do0fM+v5g0nRHwo/dDyC0n7k8oPbcz9Iby2aMrDZ/j9/sOWadazcz/Q7e/07NYfk+ZbvLPkipWqfPKsu3NczvU34H42uAYvvW72z58rNFQHnjrlorv2htPP9fcOPPkuo'
        b'XvPmznXndzzL3Bpme6loyn/W6pZ2RNtfWtrZHFDY43AurjTnydvrBpuW9ET/xfP9O3a//onNxhtLe2r69mb0vR9lOsf1l+Kfhn81Jjn9B9HPn//mxtSHirJ/rPhdScin'
        b'3oqqiiO7fvhR3Mi05TEukTsu5j2flvteTNx6y4EjX1Z++GVvwNV//OXW3I3FZT94/sd6jwLrIPTxX0wfbQiK/JsYDC5ZWj7cbHwFtQHY4XG8aA7XZaJbDNl2qZPQaXTh'
        b'JXBLrJ5s5zMKknr2mhjZanRru7G57tmLuxgAro9MwtUAf2uDoKUzJpzJer5XBO57Rg+f6PBdrAtICsLaRHTEKyVNxElRHx+35a58Rv5vWQ4+BwKA+4QK+KAS1ySSCj18'
        b'3Om6Tj7pm51oE3/d5Rufi3ut0SLijoOEeeS1b8KL2XZxZmZBUXZuZuaO8U/Upl8y1Z8Xooadx1k4jAlNJU7MkIdVbqvZpvOs2qXdpVPr1O1h7dnnI0/saN3RsaRlr25v'
        b'rzf8qG57XtfcXnJ9e1/w9eBHCx4teMf2zYTvJDwOSxkMS/nImeD+7NbIE5JWSXvSkHNwr9OQc/TgrLQhp7TBpRmDy1cML1352GnloNNKAu5tGwubCwetvckpslW8MTPO'
        b'1r4httlBO187//mYKU+SyBuxndwQdMF8MCh+SLZoWLZoyDZh2DZh0DwBejBmZuJqNsYZLlrLMXvO1mXExnnExm3MVOgCt+GitRizTOU5mI2YWw/a+owJyOen5tYNIWMi'
        b'8nHMhLOwAcKUEmJGSChhxggpJcyBGLT1G7OglCWlvMesKGWtL7OhlC17zI4S9rQoaMyBUo6U8hlzopQzq+hCCVdGuFFikr6eO6U89NRkSslYRU9KTNHL4UUpjl69WQUf'
        b'SkylFeRjvpTy00sjp5S//uEASgXqqSBKBeufC6FUqL5sGqXCWAPhlIhgRCQlovT1plMqWi93DKVmsIozKTGLEbMpMUcv1VxKzePpmcTyKD2fp2cTx+gFBnohz6jT7BrP'
        b'04u9iJUlGOhERicZnk1mdAqPyZHKyDQ9mc7IxXpyCSOX6slljMzQk8sZuUJPrmTkKj25mpFr9OQbjFxrkGsdo9frizMZmWUQM5vRGwx0DqNzDY8rGJ1nKN/46pDks7Jp'
        b'Y0pWtknf1GZGFhhGewujC/XFRYws1pNbGanSk2pGlhjk0DC6VF+8jZHb9WQZI3cYpNzJ6F364t2M3MPTT4O9jJ7H11eP5bN5wNdLGsfoBYbyhYyO5xt0z+gEA53INxqO'
        b'JD5nN2XE1mfEVk6vnoa3z9hq/suDp5WMreVzbt6nQ1pChlwDhl0DwKJIQuilMkkb1+Aw4uzzxDngsXPAkHPQsHMQAcmB9NIobOA1TBtxdj9t0WLRnt1hM+QcMOwc0CBq'
        b'EI3YB/c6DNlHaReOuE8+vaZlTYdoyD142D1Ym9iQU5mmTQOTZGY9IrHWOjXk6NQdcb25g5KZQ5KZw5KZY/zZkogx7htc/iDgzGbBk+SvdY3jmJAUwFjrW9B5tat7hYOS'
        b'yCFJ5LAkcoxvI3Ee477mQnhEQa1xXqRgKufkcnxT06ZBz4whx+XDjsu10qcSKyb+snavjgW9Dr2a2yseLXzHZzBg8aBkyZBkybBkyRh/KuH6DS6k1aU8eHS8eVKymPdi'
        b'sAYlrkMS12GJ6xjfXAJ6ePVCHnWDCuMsSMGk13KwlEwZ4169vMKBFMjGh3PZoMRzSOI5LPEc49tKYsa4f3YhPKZA1XFeE0rpMeDK2LnzbTlk6zo/UL8daD3Kz8z8d/cA'
        b'/x1AYf0iCpoIIlTLSTg0jh+8KH4whEJxPB7PmgQ73/rlW91GbJdEcTctY4UC5Z8aFXz1D+DW491rNQ3J0vJ59oc+u59S6yiav7B+YezcjqPJ2R2pt/3edLwrvf/+nNG7'
        b'qp+fLpiX1PzbR48mRf/y3i/f3/nG2Hz7zwUtytuxli4Z5toj7/x+3RuLvtj2H4E5R9vDWv689MOLz9P7Ss9GLI07f39FTHzz2ZY/ty7uGv34//VMUWy8m5u+t8tX8N6f'
        b'3jlVXvxlc/8nP7MZcVzW5Ffxnecl+3J/ElNXnPnTuZzX21FDm94Rex6Tz1oolsfVmbmXbK3jOzk/NfMpLK7463spM0OejDWdfvPeHp6r87Q3R1rlFvToAS4neW7y72PT'
        b'cT09mCBFjTx0jY878D18myJtDxm6T7I2faQWOWZgg+8LlLgNndmMK1iSoh51z0XVqB7Xk8QCqkX10VtNOUtbgQc+M/cZ/dpWA+q2TE5M9U/1xftNORMhX7x63jOye41q'
        b'EuwDkkQcL3lGEODtHQuekVSRYOqSlw/qoLqQ5KCV9v5wtwbXC7hFqM8U1W9BdfQLMS6oeu+LJ9CAE3vIhHNaIPRH5zbR9A1uMVufbI4fklQIMBtn5YZOCtFF3DidRQQP'
        b'/c1Jtj8ZV89Hl005YRAPXbXFl9mZ1jP4wnRcLQcOMGKV6Sn4PrrO46yWCJYjHeph+3z1qAtdN1QKJILTfQMeZ49rZfiGiLPS0PABHZ4zNyA9EFfR5mDwcd18/ICPb21E'
        b'92ivVG7oHu63wsdwDUQYIf5b9SGMq0aIDuPy1fIpXx9AfCthw7d4UU+hEcgrgcdLr/E4RFmoLGFxCPtE4xAlb/zIgSsnstuXRn5GLOyfWHg8tvBo2z5k4Tds4bcvfkRo'
        b'VpFSnjJo43khekgYOCwMHBQGjggt9iWSH/CUrh6DQscxvploDW9E7DJoeAN49/B74h7+2D18yD1y2D1yUOw6Irasl1ZJf2Q/dUjsOyz2HRT7johtn4jdHovddLFDYo9h'
        b'sceg2GPEyuWJ1dTHVlOHrPyGrcjepgR4m9vWp1WlDbqtGjJfPWy+etB89fPnf7ThzJ3GOL4o9MVlxMFFa6ZvadA+eEgcMiwOGTS8x0RQhYQujpuFIjDz/83XNRLO3B4s'
        b'If3yikg4P4pDUZ5xrgLswoMr8yeTRwUFisJRITlMOCqiW3+jwgKlumRUmKvMgWtRMRQL1CWqUdGGshKFelS4oaioYFSgLCwZFeWBb4A/quzCjfC0srBYUzIqyMlXjQqK'
        b'VLmjJnnKghIFEFuyi0cFO5TFo6JsdY5SOSrIV2yHKsDeTKlWFqpLsgtzFKMmNEefQ49lK4pL1KM2W4pyY6ZnstMqucqNypJRqTpfmVeSqSC581ELTWFOfrayUJGbqdie'
        b'MyrJzFQrSsgXbEZNNIUatSL3hZ9Uk0Wf9c9eMhnzermGC/m/zOogniFg/poXzGAbHi9fQHzX/+Xrt+Z2CWx500wSK+PelFnGBgu+FBu+xTdqnZmp/6zHFF+65k38D/Sy'
        b'wqISGSlT5KbJxeTbU7lFOaBP+JBdUADAJ1dvVUhyFu6bwdRRlai3KUvyR00KinKyC9Sj5sb7K6oDnD43zLLERMVfimex/3A/R0WOPpEtNvVuuIwJANSM8YU8IUB8uJhz'
        b'Uot9pmMm8TAcY5zRdakZJ7HRG44kZkxg8fMiBwPnPJr6aOqbft/xGwxMgveI2HrEzFEbOOgUPmQWMWwWMSiMGOGsBznrBuchznWYcx00vKl4/x+uq48r'
    ))))
