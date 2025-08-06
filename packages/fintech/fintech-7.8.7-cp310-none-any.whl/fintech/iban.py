
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
        b'eJzNfAlYVFey/+3bt5sGZBHc1zZuNKsg7iviArKJgLtCAw00QcBexH0DaXZUXFAERTQKKoKouIAmVZkkM5NkskzmZZjJJHmZzGQm8yYvy7yZMS/Jq3MutCBkMvP93/e9'
        b'P350N/fcW6dOnapf/eqc034kPPWjpN/F9GueTy+pwgYhXdigSFWkigXCBtGgPC+lKusVJo9UyaDKF7YL5uEbRYM6VZWvOKQwOBjEfIVCSFXHCY4ZOofHaU7hS0KitVtz'
        b'Uq1ZBm1OmtaSYdCu2mnJyMnWLjdmWwwpGdpcfcqz+nSDv5NTfIbR3HNvqiHNmG0wa9Os2SkWY062WWvJ0aZkGFKe1eqzU7UpJoPeYtAy6WZ/p5QxvfQfT79j6deZjSGL'
        b'XmyCTWETbUqbZFPZ1DYHm8bmaHOyOdsG2VxsrjY3m7ttsM3D5mkbYhtqG2YbbhthG2kbZRttG5M2lo9bs3dskZAv7B23y3HP2HxhrbBnXL6gEPaN3TcurtfnPMGxQKeM'
        b'TultTJF+XejXkykjcYPGCTqn6CwNff7NHqWwdNUg+pSU9c74eME6mT7ijcnYgaVYHBMZi0VYHqPDcrizIzxhlZ9amLpMwker4YZ1Ot051NUfa610awVW+tD9WBEWhRVr'
        b'6KHSgNgw3wgsw7LwSCwJVwnbodJxEzzYwLsNynYQlm4lE2mTsh54hQvWLXQxAw7CIWxzdIkNI4ll4QlhcN0Li3xXRuHROA0WhyWQ3L4deYVFYkV0ZEyCFzUUBWB5eGzY'
        b'yrnQnODlFxbuq4AmSbBA8dCZeCkhRfGUg7n22CT6ByYozbV7ChRFIk2BSFOg4FMgcrMr9olxvT7TFKQ9PQWO9OvUbwpa5CnIXeEg0AS4JyXqs7qmaQR+cfZapcBuzE3P'
        b'GDRpnKt8scpbI7gLwjRtqCUrPnaUfFEbqxLoXXsg1Br5tTFQaBSyWFcJ3iOkrzyExc/r/z71C/FOYFVwuCKL6XFiWLWixUHQThuZPfK/B7/sOlHgl5+f+oXbcTeF138K'
        b'+33H74TkSqFLsAZQA1yEO1BKE1I6D9oDYr28sCQgzA9LoDHei2am0tc/3G9llELIdnNcgCcNugDrEHpqDRbnmAeRyfFIJlYLcBIPPmP1oIbhanhkNqkEITMUSwUoivfk'
        b'98cNgYNmk4MgWNCG5QKUQIWJN4TEQr4Z7zA/hkt4RICyJVutw5iTNmVCpRkqyEpwAjqwXoDaYT78GYd9qdRAfj8GGvGCAHVZWGFltk+Ek1vM26jz8XARK6kXjwjrULpu'
        b'hM4tZmxVC8IebMATAhyBshW8Be9AJ5aarfRMnoBHBSj1gnreAhV4aaTZhZ7BEiWeE+D0FpRbsGNwiBnbSLEREXiKhOEZaOYtXlOw0Axl7OnTK/GsAGdS8I4sLR9vQ5nZ'
        b'mZReNx/PU/tmtHGdh2D+LnMeOSyWPoMnqdu18vihQSBLurH+6uAme6Qarkfy8a/GRiu2uZACYaF4XYBzVqiRNbuny3Vmxoc72IRX6ZEM6OC9LItKhFKaLwU8ytQI0Dyf'
        b'RPAnCmYON+NNmkgDRdgxASrR5m4dTi2xUAjHsc1KmimgjJn5ON7F67yNZqop2BlbqKcwsvQNmgIshXuyxAv4CE6Z82ikexRMYokPdvCWSXhhjRnb2YSenY+nBTiagyd5'
        b'yzB4CNfNbuyR0aynM3AAjnC9jYnjsE1DDS7QhhcFqLEs5dYZglclaiAF8ORKvMwUKIMK2dS2KUgwY6G24X6sm8r5WC27VIE4BNsG0ZSuhqPsoVqalgLrCPbQQ2iEu9TI'
        b'XPoWzf0VJrJutDzcWyugCtuwlVRfAA3YwPz9UJgs8zja4ByhGj3omIvNAtRPIZuzphi8tJka2HRcw2ZmpQtQZOAzmOyaTi1KbslH2EKTnaHkXW1IhXIyOvO6QrzP3O4o'
        b'HgKb3FU1XEDqyoW6WrWYPXVhG1zhY96AZ8aTgm3UMgtPYhMZalu3fkW5DqyFQk+BD5i31KWSt8getnUlTSI9o8FWpnktlOBVeRJvh0GRs4aNaQcFJ4tMPMUNhUU6qHPG'
        b'myQPjhFu3GajKiYN5ZiB8lXO22nEIygyqa/TcDyoWw2sSHLGO2RBn5XYyvoqxypZjfIsqKUmGnPGImwjd8aTcJFbA2uhLZ2amAmv+rO+6qEA27lnrAlwMVtIwRgLFgnk'
        b'q+1wi+tghXNwz5mhcNomZvNqvAcHumNQAY3OTsy2F6EQ7wnwXPBy6zjWUgs1cAtKZ+IRoDAlMDykEpR4QRFDf7RYR7NbTuJhK5Rux+NQDiV7sEIlSBkKOIgVEVZGBwgb'
        b'sRVKNdDEbwmSJakERygXh4s+OiWfdyicCjYKlePwkCY/R8jZBWXWwWykJZvwZERoCKmdLCTDI1cOpmS/crwUAe3b1CynpC7awG92n+jGhz55Dx96QLh1EgvYyGexCovg'
        b'6kxoVOmjSM3m/XgxMxQaNkQJwWYVnBi2QLZqEcWszcwChFS5jsUUMnB4onUqtfnio3k9UprxBHk3//hgTTBcxROSMAbLJUfvcfKcVsQHm/EWi5hKCiTC7orBZC0mZqqK'
        b'0IKLoeRyhckJg+aZnnigRwx0Skq9P59IcdQunkmC4bycSaqXWnVMBtzG4h5drtt1ycXOYIonrssxSQ11a2WPvb7Ah6CXkGIazW0dQUwk3rdOoZZQRyzBqjC4RnaxS9mS'
        b'EcT0IiF+SrwLR3P59GBjwkaziQFUM9agTYCClXutPkwGPqAUZLfLIyyVLdyR6awlG15Z4yms1Do4YxXclbW5Aac1PA1iBwEGS4S+WqsftQTCFXhglzQy/omNbxAJo7cm'
        b'ppWfSbVNRYDKlEoyL+WZcymZhmVOPIMXrf4sdWaMt4+rXJks60O9UXsmlNKkh2En9XVXjbdzsFUeYHFgLME9fdo6FCso240j/3uGNVzB04k90tJyemZMWi2MxjYlYc1C'
        b'PlcpywabncjG4+n+apaXj+mss5ijdrrlsEE5YnH3lJf3nbVguBLFZF+LUidHCdvghgbuaZPlsDyID/3NUEJm18EBBnlnx+ZZpzGlzkId+UsV06Rn7pRwjLziBBSmkXuc'
        b'ogGeEQLxnIoQ++ww7pXpVnxOJhRk6U7OKIisWr359GLLvD4exSTj+cBg2epjoEpJxPgGdHLFvKEMzpldabhroRXPkGvCGQV3TWxIJzv3D5OjeDSYKcp80yY5eKznRl+0'
        b'HGplIoOdfpzHaAI59aKkUEeP2+WU99Fr+JjuYAnerYLTO0DOYQYCujKZ/fgTKDP2g4c9uLg10BZgR4AnSl2V5Z5QBsseH4SVKjg/OoRPaIh+FSdMNJyznDH5z+EOD8fm'
        b'YmXfCObS8DIc65YzBq9Lmsko55KpcAquyhQL7xFPYBwr3cpncSReXmJXC85SHHULI8HXZN14OPtBicoM9TLFSYeTQ0kcuf3KRJbDj1vxAld4W4SBszWs8uF0DRsmyTT2'
        b'PlSLPd00Qb7cDaXPncxZoFALFyhIo7DTIQivUELgmafRCRpkildA4cc4HhSn8/EvGrH8KTDtyMT8DV67F8yUR2+Gcxqqfo4QW2Sixs1jXtfG5xif46wQzu2TNSuGAwk9'
        b'wq4mDu0X8d2jP6kiMIX7HKIXUw4hWsyyNpTEYi2DxQd4QM4hBbo5nEgmwi3OJBdTDHOvfDB+qt27udIM/kO1qgzCJQZRMVjn4A+3t8thdxsuzeU0jeaknBO1fRM4rswb'
        b'BMU9UAA1ubKSV3vNGjeAPzxQZa7AJhnvTqnBZs5jjtSykk1+ObbouFIJ2EbsQZbW9GTopdDakwqmKvFBHNbJYyuegg9ljhi1iVPEifM4iGPT3B29QZwFyAK4HszCRSKM'
        b'uqPE1jH+XJcFaMsgEZRRNhCVOMt461mLnPgur8N2TjPxACENJ5oP8QQf9PLdcPapSLR3hOc29oQioXL1MmjiyhrwRrrZjfpJoi4uMjMemcGzH55UGHujFpdRj8U9KUep'
        b'JIw578MdZw7cgOdkiusMZzjFVcBRqxczxqOJRBaqenylx3bOUG2PwAbJQbuEj1oXukHmw3B2k8yHH2IJr+FjM72hcPNAY+NXJLg5KCpkKVyfIpjwhAaPhJMPMs0coHyG'
        b'TKOhMofzaALUM3Lg3FqA7cQqWe53imJOeBJqlsgTVa2HU/bOukMHWpZmkh+yFK+Cc7uhRPbAxixPYtw011PIuS/RyOHaBGsgE3IVm8Unue0plH1ubzdeT8caFaWDAjzL'
        b'52OmIk9m91A9l7P7Z6hc8efkam/6E2CUs6w0yy5QSRZwyZyhiFU5zMaHefIIL3kukquBWMofvBiopXzMoGETXo2M4LmMJDwVbJxrrU4gPlTuMCHeUaZJ+dgygYzFKfN9'
        b'DzbQMyM38uCAo1A+56kczsWUbojHK1HCdLhNmc2IRVzQJnJXqshcmZx2vMnIbcPIIO4qBBxnAp6OD8Lq6iDZUqOxlXxugqdcztRCA9HoNp5EaJDEB+A51XI+favx0Br7'
        b'7JFHH+zFBMbAIQpVSlkPZDEHsJyKlLZtJGU/XGaRVgn3V3MxqesD+2QiJsFtUo//g01Jtc0pb85xQ6bGkAyaNR8tw7kjm/M4m8XqsP12EDr8TI8QkRGSdgp2vE819yiO'
        b'DNhO2UuuzvAGdcvKMziMJd3lQANVpLw8i6f4YvVZeBw3pzKOGAQvz/DqPl6dYTUe4g9ZMN8i12eBI3l1RpTjMje0P54f1M/OJXHBzD+ZmVvIzORWLVzMcLiySS7m0kGu'
        b'5eCIXObBA7gdQU2MOzeuZAF0DG9hM0cPT2jf3Y0eTXbrYwXVJ3b0uDUJz8tlaxPZ4QwJYqOozWHkogqbKScFM8u0Eit61J+mBMsgQO5xv5tuBuIZFVGtWijlgWSNDCJ7'
        b'3mZ58fwYFkmnFbt4IIVB54o+8phuwTLbWwaXeqStVcERLDRxKz87k7maC/nIRIIMMv95uAsnuPdv2kaEqU++oiRL+SoktztfrYp0mAN38JZceNZTIi+Qq98kKvBZ+Uu+'
        b'WMFZdVKEa1+4sLOowXt7DDcdHqmgch0e5HoF6+AmCWPoVoIHWEXaAMfTOGHxJO5fONTQR6CY0q2eO+P4MwdD0QwF1Cx2ioZ6SZ7RU2gL6S7B4UIQL8Hh0TDOO6m8eoTF'
        b'/WoQUvJ+D5LrlOTF52bJgFG5fHt3yb6GLMRK9nFYyScAWuYQ6bNHVuGufjRPJhNWVS7W7JSRrBjPLaEyn2ZzwmQm7CzRzmYZq1vTqWp9ypsXz+jOdaPxnhJv6nfIWN2W'
        b'rZfXCojc3eeLBQH7+CzOnOE+EE88jcftJeMjyRVrnHi0x4zBFmcN6TLvGVbOX9ywQ86Y9Ynz+oVVR3KQPJzR2Kwkr747lYuIF1bzlYkFk+WViYI8buSNcCO2H2Ujb8Im'
        b'lthlf/J1mJUChzmPhKJshbOFIGMOBSxBclW8pzzQ58bkdS9v3N0or26c2929fECTcZyvH2Sn8tUDbBohtzx0ne68nWRZCJcbqSwiT73Dx5XrNtfOSXvGFe1lD2UGhI8g'
        b'Xy1PVCmczXHeTuJDyHBXmUfdhyvWIM7V1EQATq4c2CWhbQMhcUEmNmwQTM9SYQWn0rleweR0Nr4cg41z+XKMD1ELXyaweT3xgwGQ4arKA25nWXlVdY3KBLy6RvbJZl/o'
        b'lNdvJlFnbAEnB29wfkv8XLKHMdhG9CGKvUpaqFJZ4EG4bLGSBRZ5yUdQ8yUfMvMJjj274aarvOKDN8P5is+EVLl0vbkcHjq7svC6kokd9Dreyvuf70zV2QBD4VbKxkI7'
        b'xtUT9xiqkyuv20F47cnMlPcDSNW2GYpVbJlE4zBzhZ+crC+szuxXPMI1VTKzf7t7lBA0XEVc4Z6Fz3yAP4VwD+m3u/SVSJp7efECbkrS4CmcURAwnu9Fmp4EUQHYuhnu'
        b'GCyRNNlUt+jklPdgYz84wYsePRE3T0mF8SNs4GSK8mf7lv51YXDP7LTbDVSlgrPueECnkdlyBYXNLWdXyoIziJA9pGRDBFBe6J4+QXLGVgVbuW1kUViP97qXf0OJNLRQ'
        b'Gz01dRTeJVhNpHTEIm7cnGxnR8Y47lPVRvN3edcC2e876PHjzlaWvu9tYG56ai5RDHmFCS7Ccb6YBxVRfDXPDOd7lucLsNzZzAL1dh5zlLqUhVxv0xYaVykHPKjbgJ2E'
        b'MvgccVqWEsdg/jxqq4Ki7oU8uN4dmVDEF/8kcuGL0BYPpQnC2s1qPBearJPkBcCi3WTS0siVWKYUlPhQQSZ+SBhfjB3cP/2wxsUNqyKwJFItiFsUAVixmBOU+Xpsi8CK'
        b'AAqbayt8dGzPapC7cqgfQTobYxYcW+cT7RcmCdJiBSl0Fpq2QPPyFLY71PPD4oRt4vD9paUC385i21hsS4ttZSltjmmO3ZtYUpGUL+xV7XLcI/FNLBXfuJL2qeJ6fZb3'
        b'ET/8T5oOJ22vn1C2+2nW6rP5tqc2Lcek3a7PMqYaLTv9+9zY549wedPV+9mcbEsO30D17tly1RpJ2na9MUufnGXw5QJXGExbuzsws+f6iErWZz+rTclJNfAtWCaVyzNb'
        b't/Zs7epTUnKs2RZttnVrssGk1Zu6bzGkavXmPrLyDFlZ/k59Ls3N1Zv0W7VG6mauNj5D3t1l277Jdin+Az2QbEyZy4aZbtxuyPaVn2IKLgkP7aOBMbvfiNhPChnGsMPC'
        b'hmDQp2Roc+gm04Ad8bGZdvbuzNKjJpnyn+/Hwja6u6X5a6OsZgsbI7N7XIzf9MCZM7UhkavCQrRBAwhJNQyom9mQq+eKebNP3loDuYZVbzHwffOkpHiT1ZCU1Eff/rK7'
        b'9Zctzl2reyzaOGN2epZBu8xqytGu0u/casi2mLUhJoP+KV1MBovVlG2ea+9Rm5Ntd1Jfurpcn2Xml5mR84zmpwbTb+9cIzy9cTs4ejkPaUse1rPVMXw0SuCLY3hHz/dk'
        b'f2oeIcyOSyLembTHqt8j8FV5qHFyh1L6sD5+mbAebubyW6+vcRLmr/Bn+79ZvwjdKu/pNmW6ChrTXEGYluS7PCJR4Ii2nlLmebawMy9P4Os6cA3adG4cO1dSVc+aMsfJ'
        b'TUqU0Va7jxAxTyk4QY3ANw/hLsqbHVHzd7PNQ2CbQXzzkFJMAZel2jeFbx5CQ4wg7x7KOTmICHEj2z0Mp1HwzcMovMOfiMEmL+dcpbAXTgqsFj7lFsqvD9s933mbUoDD'
        b'2QKj4zV4wV3G5jq/eXy3kdLGaQXbboRHm+R6pW40lmKbWU2oT3Uaq1eOQStc5sDth5fxGN+MnEqJQ96MLIBajpLTmXH4bqQ3Vgh8N3IWlvLeRs2BU3wvMmedIG9FFkKV'
        b'XH8R5J5xJvPMxnaBpam6UXCDz+yyMCdso6FiA54WsIbKTouVD8knF0+Y8xyETIvAFvEq8WaknAwboX4bWy2jMqmK61ZCozqvU/KnVqFtIm88ES+37fCWl7NuaSfyfoLg'
        b'qNxN8Fg5593FG3CEdYQX4Ybc1Yz1vGkQXoArfClxNsotR8xQqRNlNQ5CAdzlrSI+klutUCJvfscF8L3nwDkC33rG6iDubB3T1YLXlFHsLMYg85x1AifRE+bHT58msQGW'
        b'EPcVkmfNNe6JNyjMlB+E6pXjZ7zRulIZ4q7+4HTte/MaiouGTThR7pY0NyIxJE4K/W3pOpciR+nXqo+XrFbhxdvDs19wsKYtvXPvm7T0bztPrHvmo0GT/mvVhyNUX3Qe'
        b'2J9/cX7CCtehX1rMExrdPHwya6tn/6Llwp7pDp+ew8dBmS8HbW/X3Kn79aLFX3W8sfD4vJ/VX/hyzrYvR07JnVTfMfiL+V9cW9M27vDffjv2y3zrtRvvOfzxZ3+8/Efn'
        b'v/r8dfpfLj1e9c07nTOGN637zfzW12qPvNvx+qehJ/KXqsf9cmyH6W+78/e37Q5f9Z3JbYnnJ1XffO16Z9XDzXHfvjncGNk5K/Bv80f9KvvFH29Pebc+eOOvJ567AYPU'
        b'AY+atm6+8Pw0nYOF+eosaNjj4+dFjtcR5icKajgj+uFNsFlGc39wgys+/uG+3jp/rPTFYkFY4T1CK23Zn25hST+SioD8iOzkGD8ojuGUwDlWJDpzPZXLTlypYudvvLfA'
        b'XT9/Bck+JE6Hg3jKwuidL16DFmKP8lGYPPkozHY/bywJEAV/6EyB+yq8FY4neU9EHg/AcSyN8qVAqgmn6BDUwaIr1MyysI0dOKzYESGLIMpUKdMXaIeqoVigxLtz8ZRO'
        b'7BK9dGyvStA58rd/+oXB5+Oh89NMObsM2do0+bSVP8uuC7ucONYnsj/YbeZkhrf7JZ2k0CjYr6tCVAxTqBXSd66iWiF+5yRKdH0Qb3Ni94jit05Kdi9r63mX7xAPDOH3'
        b'squuCon/c1KMEQcp2EaZrJdO3SWxzruUlLy7HLpTYZfEcleXQ2KiyZqdmNjlnJiYkmXQZ1tzExN16n88XJ1kYiTMxI7fmFhkmdj5LxMjZ7zbk2yYLISFg2M+VYsiDY69'
        b'Sgr1t+yV77MRqjdDVfeExFmeTIk8HVAwhSCFbUkTI32A1RFwcj41Y2k0VsSEqwTXXOVsPAY3ZUZ6nFzkSEQktW3FeuKXPgrBeYOIzckbZSpu9KTi98ITRkqlxNEUZa/0'
        b'x0bl0JP+5gr2Y1JSmtTNJpVFSmKTErFJJWeTEmeQyn1SXK/PeewknvLDdxVPs0l+gq4XnTTlbNXqewhgX6rXl9Y9Rdvi/wG7NBm2WY0mmVPkGkzEMLfK5KfnWF/f9B/T'
        b'wwpIEe/V1KNxq2GZyZRj8ubC9NSSOjBpZPoydWXi+PQgBmRM3YOSn3h6hAN1wWjm8ix9utYok92UHJPJYM7NyU4ldsTZpjkjx5qVytiTTIQ47e2mugPzpGVGNuQntIwo'
        b'uF4b5Gex5hLd6iZf3GrEGr3YHb6sI90PsCZVP9akirYuZI5bBpegTT4yOAE6+54aLI70XukLTfHyAUJ2ISYyPEohEMgWO8+BGl28ccdcV4V5AYPQLbGfJvmn+ejD9Flp'
        b'xz7NSv5T0pbn333h3ReOwK0jcwobT9afbM1vDLtVWF8YWK6rri+cUH1wulLQPe9c8qMmnWhhq8jwHD6CSmdvig0sxrIoq5/3ImzmQDoe2iS8MRIaLOz4RizewosR/iuj'
        b'fMM9+dmU7rAcBbekbEW2TuwDA9+HhRwLupzlk6NPoM9Vhr5UjcJDIcOfyc0OU6ouTY9ndTl0+4iMM+zUpomd7OzTu9LEyKbJnb042vGHyfu3J/jj0TQA/rBxrsczO/kw'
        b'sWNt+FPDhLuxVnYgN5Aq8mP9quRGtvwKN6EMzvsqvRdtjgiGim1ULT8HnU5CMh5zwdpAaOVMJGzGHB+odt7uqhAUxErx6vQQmb00w7VNUKtz3r6NtRSxDf6r2MzbdsZg'
        b'oRnvuAUxZnNMkQZnhz050dWIB5aFQ5E5iEymyGHp624CbxmH1TMID284b9+uJomHBTwTE63rXmMvWEvIWUPT+gQA70CTDJ0leFArF+Uh0PKkKMe2RfLCQxsc3hQ91oeg'
        b'VSGIUKEIJdg+2A877aXDEoadSo6e8vFS0aZJ09gxVPqnMfSb76vIefD3rce/F0EY2rDbf7iu/Z5ykz38f15tpmRxtcwGS//68ikFmV1yUlKsBJbZKf0V7akwl60K0YZS'
        b'tjcxMF1KSSPFkmOimjHXmpxlNGeQoOSd/M5ucA+lGtSkz+onbwnFq38v3fRsUqz88Ll3XGi8ty+9LV3K3kJjVgfSO6nnvSRoCW8IDfX27Sex15ioes0ZsE5mg+R2zpWr'
        b'Y5KaynB9Z+5TBmQ//1TGtEvMye2fKNnPP5cs+0ze/2p5rhAGKs/dqDyfR39kYdVSlmeCsf7p0+n/OM/4T+WF0WeBI4RpVJhPNSbteXX4drk035zlIVDm2PF3l6T5sYOc'
        b'5NJ+/BqJauINeIQAVFjvhCW8mA1bSIBYCkUEo51QRGnRU+FIeHaEy/mL1k0YIwi53y5Mity/2osw3MogexCcnjVdgMuzCWaFwOhn5ZWDm7HYMl0i+KQqXAgaP5FLmDVl'
        b'sKClqm2RJSmyfed4JoGvg7Nl2arpbL2Ry6BC4Zp8xBfKNmObA16kWlxYRTVpRSSX88JyZ4EenPbFqCTfmPCRQrzR/f5ElbmZmr5VTpxc0ekK0wYV/Mx45g14/ievjLZ8'
        b'NPb+mn9Pb//JquLZPhMaSxa3rJpwuj3s/eMXT5z6bM/CTws60jK1Q6Z9uCJ50+SunN3JM96y1a2xrFri2UnZ4OeftL1cd+R3h453hAYFJq/4uGn4oWGeXzh6/j3z29Kk'
        b'1V3j0044l7+4/vImvxd3Obw+3PVkVEfTKf+shrZRH1QeLX3lYyGvbsHHXXc3tn3TtDm+0Xrq3sydHcZVm757f06Qpf2+TsNrJziTCmd9UvG8n5e9LoNCrLJMpMatTtDu'
        b'7A2VVGA/Sfm98j0eV1nY1tcsPIxFPtHrxlJZVBzDqrQAusuPPRHhQEY9rw6XsNyiFfgptE68i+ex0zkCy3R2gUPBJmncsNDCptB5wsKImCUmP8oW2xUhUJdp4WV+/iZ/'
        b'LHUOwOKAGKbqPtEbrm6Qy7ZOvA93sHQyHiLO0VO1YR3e5vUltCjwbgSWL5waYS8w3aYp07EhV6eQiYDmXyrTZGriKBdllCU4MZkmE5P9MilhryLVU4MUcj3GKitWcT1D'
        b'7yO6f4m6eD6hLk/qoS4l4XUvxvJDpZSyVyk1xM5imOg/P2Exo6oGYDGsOJoKxVQb9VS1rL7ODlALg9GmhDK32TqFvGHcviWt93p9Fh6EGqzV9/uiiL0CminwCkhME+1f'
        b'CFH8s18Iefx6HxhbLcPg95D4NM7BecLtvRz+f131fC8O91iqLw6ro62sZoTLMz0H+obQP8TgIUvmhGTJeFbqiNfwrAc/hshXWUelyqd2LkOjS0SMH5ZEYVkcPX+SZlP0'
        b'WMbOg1CJcZo+6IRV7g5E6i7DLWP1zWUqM0sLO+++8WmSb3fdwKqGdc+f//rukfoqRdj0S9P8Un2H+euj9eqfTvNP+kPSuldGvPr8aVdh1d5B//HtdzoVrxqo56vQ6ezt'
        b'A/kDo4g3XrdwQluyN88HbLm9kaiEIph9N8w6JcW+PoTVcICHMFshwg44YGFevBPOjLFDyhgKfTuqEJw9srAvnK1ghzTIBpRibH0WklR4Xo5BccA4d0g3WOxR7s6jnOJ8'
        b'gqZ7bcVJYRrW80CjUl7LGLDaaFTIjTw62SMjKHjMI3h0CgddPxkgPhm4eQRgJdO6GGuyeymNJ7Q/EHyiTfiXg6+Agq+pj+/G5WYZLWZ7hMmbERRGWnY1zaRP55sLT0Vb'
        b'T8TqtcED1sZ9bvYKjUmIjl+93lcbGrYsNCIuIYqK5pDoiMTQmKXLfLUhobw9MTohasmy1bp/XEkPFFg8cS8boxZu7R/Nv0S3Lc5NsM5m0VYzeRD79pwP++5dcWRsGC9i'
        b'eAWDx3TsROvpnfQbDsU7BahVwyEXJygaDPl89Wkzli30T+j9OBbJADkOr0hwIVNp3DLHqDLH0L3hzz4e+uMJHge0Q5a9mTdh/dZJwz4epkmzRp678NGrecNb4lrrPgq2'
        b'ds5ednjqpITTm6b+as8qeO2wW3jmC1ue+UN82YLK4u9G+G33O/MLt8L6wQWbq3USz4g6P+hki6o3E+0RE4GXuK/PXpvXL8HizfWSBhuH8sS/mP5u4gudF2Y9Wedsi7SM'
        b'ZC6HV/FkBE/iXnA7RC04jhChfiPc6lM8DxwtTlRxmHvV60O6A0YTyJYYNXyJkb2bRtmfG/60tBH2MGE3efUJk3cHCBM24nTNHp8wX+9ovL/hSSk+DB5IQyNWUBKbwKa7'
        b'wXednMSgdM0crAyAEjmgRu2XMqgwr/3+gOpez+NferSv5/0LQfXh5qfX83onNb7wla3fyqueAXIZq3nYXl6ugS5QzuubXcLl0MrSWyxUwqToKTH1FcpTnD5VXjLsV7z1'
        b'kWUv5H6ojpPrtv9fc6xiQCjQRPNSZyOewmos3Rr+L6bZOS4ZHEr843ipM63l2bRNH83RCPIiR5knnOlOu5Hs2y4lxJAO8RMpQyjd1PXKvT1512ld38w7GG9z+VfVav4d'
        b'V0GzK3J0QpJgHLfnl4I5gVoOO63vm43/mJSRFqn/SZqvx5+SNj3/7gstRwKr6/P1ireXFEa7v3YWOo60rmsumHxYda1u5LW6hGP1JxVX6m4vXq2+VjddKVT9eehor/d0'
        b'ak724SHWbCa2f2rswGkanguysEObCrfNbCWnm+jH8AV1uE5puYLwJkolzIpW7wMbnLewJaUwKNnhk7K0V0rfBAU8o8OtMfjUns8IrWcOZfQ7WCmXCgfwzsb+INaE5wjF'
        b'bmMp1xoP7xEiYpyVdlV61BgPxySsxZvQ3EPxf2ilcRBP8+TVLGY4dA3ryfXLNMTjKdeLLN+zT6YxPc/qlF3ODOsSc0yMI/TK/AP2R8qMtYMbEzK3N7h5vDQAuPGl11qX'
        b'hRExvQaJ91b0GWcZtumU0dHLdYrlOjF6ufHSL59TmJeTgvUFpQlvOcR5hoxQf/BeZ0SYZrPUmpxzJba14ULyZxeSFZ8+6x47pMjlM1+pc15wSdqfYj2Dt3/X8NnWoLLX'
        b'X5tvTnyvM7IwXxnb/qLLpEmp7W++/8Gj0HccXyqs8PkyMHLR79ccqt230P+lx4feEZfdFuvTFr38MLshYNQpzdTfns/yXKDX/ffL10t8hky9eO61n+06GH3wlStfRR4/'
        b'P8TgFTP6ziceVxYbVl5w+ihjxktvj/r5W45XGjwDi6NfGjJ36NsZC557e2R1eLp+Zm3+Pcu4372tWhc2uqXI/yWPUT966/hv5/z0q4cfZ1z0aTnWDJn3X7qR4veLN6dc'
        b'uzy65ejMFM/3rl3d+MaS9uTR71WMtUzd/uZ79/e7/ddbe989d2zOdxeVs1/5m/uGP+jH1K94c3nlh7MXHKy6NXbsV8cf/t34TWe65S++r7/55eOZz6tGhU7tLPLf5fje'
        b'V0HNQ6L/+ELCS//2RsTXb8R8dDc654MpnYd/ZRHyrlx6f+vmzquzfoN7Hwv5wQf1NRMeu1deadg/b+37v/ky3exhHfFSyvwQj5jPB03cUef68cXLm04E3rywzPLzdp+N'
        b'XT/xODwb3m2JijBE/rTl1Ws33yn609YXnSPe0Wy89/HpA5duvpVwMsvjWvBdQ/Yr19+IGdF4sTgx+ujEsR8vPbv65TLV5x43CuHb737sWvaXws/nGj+YNW9i4OFZOzZ+'
        b'onn89ef+Pgs+j/ls98XPFeM/L/5V0NmvP9JED/uywOPyoXu+y7/8su7VmA/Nq4dt3x+S7XUxb/g3a+Ou7f1R+57Xpjvd/uzvc/48I3nKvg/I8tKb3lC7X3GoYfDMnPcJ'
        b'IxiUTt2rpPypEBTjEmaztZM2OMrJN5zH0mFyqGKJb5+aXsT7fOs0hMrFg733DjJH91lKKPHmtGQ0Vq7FUqrhy/3wAt5VC+ot4kS4OIaTmgRsgg6flX6Ey5ewNjwyWiU4'
        b'Q6uItaPxONcDO4LdIhiq+63By3RXWTi744ZIoFEPbf/ihqzO9V/bv/1eOSoTS0UDvnDg0SQmZuXoUxMTOejkEiCIE0UxWKFlCwnfqUXiTaJGKTqJCsKGb0QHtnnLNnQl'
        b'pfiNJIn/LanEryW1+FhyEP9OBv+b5Cj+VXIS/0tyFv8iDRK/klzELyVX8QvJTfxcchf/UxosfSZ5iH+WPMX/kIaIf5KGip9Kw8Q/SsPFP0gjxE+kkeLvpVHi76TR4sfS'
        b'GPG30ljxI2mc+O/SePFDSSt+IE0Q35eeUf9Gmii+J00Sfy1NFn8lTRG7pKniLyUv8V1JJ/6b5C3+QvIR35F8xZ9LfuLbkr/4lhQgvilNE9+QAsWfSUHi69J09WtSsPiq'
        b'NEP8qTRT/Ik0S/yxNFt8RZojvizNFV+S5ok/kuaLL0oLRJQWiiAtEl+QFovPSyHiI2mJ+FAKFTulpVKHuIxZ5sk/zS33aHeFu4LtEIlKV8UYhbhokGKIwslTFEewv7x4'
        b'iyt/ddcoRilM43rBuZiY2AvFXf7f519hGm+HfNYRy1ucFk95/3s2ltymQTGUQiVlVSIg9LnSQXAd6YGtyrFQALXGm37Pq8zVTEKHh19plBNMG1Lw+0t/um/sepyvGl7y'
        b'ieP8whW5E/wPr1j7Vrkqtqt22mt+Z2rOFL2a9ruvRwz90Vjlrsi3TmvzvwoyZCbPEqN+savh7sc5f934+k9VW7e+OfRGg3bZh29f/blv0Qcl279+0Stu6L/7fO4fM//Y'
        b'6a79NQ7zo9/0++r3mrRblk2x68yvubjk/frLN3zfMX6uW7D8bOyMxEuhXv/x13U6Fx6wztA2mf/XKDE0krKIjWEOdOmmiFcCsEYGjpKhU/EK3mPsqJXdx1b2BmOHEurn'
        b'Yz7fTNyFh/CRbAyW8aCcG8NjGh5UjoPadE4zNklwLiI8yjvKQVBLk+C8qMFLaRyx8MQssPmsNKtUgiJCYN9JSbCwM8vR2Ony9DoLVAREEHRVUDKtJAZzRimsgFYHqAzD'
        b'u5yQrIdGV/bMFDzf+zG1MHyp5A3FSTJrKcTDU7ANywilAry3yVBIOVoYZZWgMCiT2wVa4SyB52W4zMrHCCx1ECQ/BbGoBjzP0RKvwjFXnvCfqKTEDgdhNNRIxMTINoxG'
        b'4JFdKViqY2sD3FMUglssHA1RJmAr3OOrL0EZeLrnDt9gLGBj5MWqQtDibX5m65F8BueMcolPjC+WcI1ijDRT+FDE9mAo6FP0jf3fAcX/xRed8vtQ1ZhttHSjKmOuGhcn'
        b'+ZiLUqT3Qfy4i/itRnLqXsaZpORkL8CktaPB+C5lliG7S2L7Ql0qvpLRJVFZZOmSUo0p9EolWXaX0mwxdamSd1oM5i4pOScnq0tpzLZ0qdII1unNpM9Op6eN2blWS5cy'
        b'JcPUpcwxpXap04xZVLB1Kbfqc7uUu4y5XSq9OcVo7FJmGHbQLSTeyWg2Zpst+uwUQ5eaF2QpfFvbkGsxdw3empM6Z1aivAidakw3WrqczRnGNEuigRVKXS5UWGXojdmG'
        b'1ETDjpQux8REM5WcuYmJXWprtpXqpycoJw92rIltWJvYwoiJfdfRxM5PmZjlTGwJ0TSZvbBVbhOrakzsCLiJfV/IxL4xYmJLTiZWZZuY35nYYXnTHPYyg72wbQITCzwT'
        b'+4a7iX1tgh3ZFEzseL+JIaKJ+b2J1WcmdmDBFGTHTDYdTj2YufRv/TGT3/FY03Nkqss9MbH7c3difTwqre9/XqXNzrFoWZshNVqnYSeYUnNSyDL0QZ+VRQlA2+1CrBag'
        b'6040CSaLOc9oyehSZ+Wk6LPMXYN6l6WmRT1m7PUi++F8+X/IWshqUjM7LigJklrDfW1IhMgLiv8BIIR4Bw=='
    ))))
