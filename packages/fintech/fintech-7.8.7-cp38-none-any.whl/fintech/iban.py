
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
        b'eJzNfAlYldeZ//nuxnIRcQcFvSoql1VQcV9BA7K6J25wgcuiyHIXXOMC6mUHUVxQFAQRFJVN3DW+77RNF5t00mlSJu1Ml7TTJk2myXTSyUza/3vOd1klTfv8+zwz8NyF'
        b'72zvefffe76PX7AhP0p6raCXeQm9pbCtLI1tlVKkFMVxtlVhVNapUpT1ksk7RWVUF7DdGnPgNoVRk6IukPIlo4NRUSBJLEWzgTml6h2+SHWOXLUyVrcnO8WaadRlp+os'
        b'6UZd/H5LenaWbk1GlsWYnK7LMSTvNqQZA52dN6ZnmHv7phhTM7KMZl2qNSvZkpGdZdZZsnXJ6cbk3TpDVoou2WQ0WIw6Prs50DnZcwD9U+jlRS8t30M6vdmYTbIpbEqb'
        b'yqa2aWwONkebk83ZprW52EbYXG0jbW62UbbRtjG2sbZxtvG2CTZ3m4dtom2SzTPVS+zb8XWvQlbAXp98wPmQVwHbwq4qNrBDkwuYxA57HZ78KnFJ7FcZmzyQkQp6jaDX'
        b'GE6ISjBzA9M7x2Y60vfOSUrGrzG3nMzYWXpmnUnfQ7ElAkuwKC56HRZiGZ6A+jg9lkVuig/QsFmrVfgM70G9dQF1hdNwh7qWYDlW+NEILI+IwfLNNKwkaF2EfxSWYmlk'
        b'NBZHqlkenKHeFU7boRVPi8UP7NUwF1raLWqf/yduo5h1B120jN6OnU4j1nEKSiM3RcAtHyz0XxuDpzY4YlHEJpp68Fo+EdFYHhsdt8mHGgqDiE68CJXrItZu8gmIiPSX'
        b'4IaKWaBoXCjcH5csDdEw117GrP0aCaW62mUgFSpIBgqSgdQnA4WQgXRYYZdB2lAZONEr5iUZ1MgymLTSQbBhdt7hkLQpXkxcfCNLIQQzO3XZjI89xsgXd4Q4MTe6NjvV'
        b'IfeU8xL54vTDKkafutnja6V8iytrYZnOXOQ+Hqr/GM1WHA3471mfKrqDNasmsUxOx2tOF6Q2B8a2xSWGvG/aMP0j+fKiEZ+NPDNSWuGd8K/Sn9yzAiJZD7MGUsPEefCY'
        b'izhonQ+ci/DB4qCIACyGlo0+JJQK/8DIgLUxEssa6bQUb2K7dTQNWXN4t9lFYr7jGJ5ncHYsXrSO48ryGC6vNpvUDFuhgGEJg8INO6xjqWVUmrfZ5MDgKN5nWMagOAIa'
        b'reP5LvDqHDN2M7YO8xlWMijFZuy0TqAmvI6ncs1QrmJ4OYxhPYNaaIDjVs7jZeb11KJg848wvMrgcgLcERSEwP215lw1W4vNDCtoHWjHC2LEPAPcNWO7hvmuY1jNoHLP'
        b'TkHZfhfsMlvVbCtf/xSDEug8IgZM8E4xj9CwiXCR4RUGF8ZityBrFB6HRjN2qtgOuo7naCrsgOti+RTSzJtmKCXmQyPDSwxqtkWLZeAJVkaYtQrmDcUM62i+w1NEw3oF'
        b'PDDvVTJ8dIDhWQbleHKhaNjrYTWPJC6cDBP9z2Ml3BUsg2qsgSLsHKFi6jiGtxhcSYdLogkfQjUc03IJnIUihjdp3KwQuekBXCJ2lJDYoAVPS44Mbs9xEyvh2ajJZuwg'
        b'07EwrGJQAeXymKSxeJyEQcSdxSeC0WcW4hnRtBQv4D0tttFKdw8xvEMygJqpgnEro/GEea+CYVGgmK54/2GZ7qcOeNqM91QMmrCW4QUGp1L2yk212Ibt5pEKNpJkwBeq'
        b'WYB3re6MM/Is3MVORwUDG82GjQwuwlmiSmyqDIuwjlrVDMocSWOIjKWuQhSLfbEbOy1qFo/tYq0KvOMlBs2DZriGnS4alu0rhtRCEzwSnNjllE4NEu2XJmumySZDlxiz'
        b'GsqwAjuxXcUi4RbDBtJ6r1SxENbM0ZFDk5iGFA5vM6h3h3NikBccS6QWNTvCtZFYdBXroEMsFIBNjJqUDBpXMWxj0BC2QN5RxTQspt1pWFqW0LtT5A9l64rct5uETuKr'
        b'miGGXMUnJHbOI6wykGl2YqfEpnDO3uA8OoldsnTLVTG8zYGlaYW2XPbViPkmzQwiAUosHNoE3bVkvtfFkEi4DY+1jhJzCWVkm3DNF+pEw3Y4JWmxgwy5I5METzRMzREO'
        b'wWHMIW0eCeGOt1jiwjKtbMLHsB2atNit4qLqYCQKqN2+W5a5zXMptWhIciOJF6TF0I2Nsh8555dNTZxxT8Qy9fBslyBAgw0LzBaJLQIbw0JGm3yaKxoivLFaS54Xj64T'
        b'rD5vwSeiIRyOw32ts4aZRpMNkOqZsdbqQQ0+o7ZASSi3Kii14ik1U+JVKQ6eHLDyKI/X8BE8hJI8PANlZDdVCjVTpUtwDEqirTz0w53Fe9JIk+QeIfI8auYEZYoJeCVC'
        b'r5SZX7cS2rAIGrGEolE2y4bjbsJIsHj/LJrsXhTFgCSWBHVEBGckdm6j7ueTojQ8hqTshhvWWXy1s3gXL+NpLISboau9oEVtiCGVbNwVBg1bY9hcsxqqZ+BRq576BkE3'
        b'3LR3hdtYjWf411W+oXPpcrWKeWKZyom43Wr15TMfhaopcm8a18y7R9CoG9jU1x+eqJRYeVBMjm2K8b1z3+qdG+sXUedWefIqlYauVMpkt762Hk9HQGso+Zzezs8mhYbw'
        b'hahzgBLvZ8AVkZSkYMPSPqrF9uDxLq0OS6B5s2fKGLZW56AND7bO5tM2Y2vcSzsMpUyljH/coCtPsVbFAkzqXPLWrfKgR+HEMZmYLqwngsqUSfIq0IA1xEsoIVZG4H0N'
        b'3p0L963efLuV0LZUHoRl++RNEHtCVevZJOxUYht0JljnC6cM57f2szEpVialj0XEn+YYvnRrjCYphuXCHUd4MNnR6kdjJ6fibb7GbTuXDmVhoRKqyLVVw8lU0qsaFoxX'
        b'1FBujRQyWEumf3KQELjEzohFbsgSO63Ex4fcrT58C6fQBidf4pbHbOrdIovMpnJ4dYrIBWj8iUn9fcsGrvAaXutVibkH1XDB08EaLDQiwdI7oqVfFjf5YGyeyzfOh4Rg'
        b'hRrq8CGeFnuAW+OUg7WOf39leW93T7ylcqSIdV2QhVXJ4S+tQQNbZQpJ8wLnkbihWG3Ga/vEkDGQ79A7hCvEGXKl+zlD4aQOrm6mON80hsXgE4cQvIMPxBBnimmNfcv0'
        b'qiAWbIVGOO0TKhNmhiuOWArNTkKp8BhF/4reMTdfUkWiDKrcOGln1WaoNwqTw5od8/vE12fIYdAJFTo8Teo+hsXhZYfABCdB1li8RebYa0VlgxayM+/JDBULhEfqXdFm'
        b'YXeR2DnbPuJGX9fWrX0WPUuJj7DELOxu1FJKqwfYKEk6Am9Q11u86yTsVmL74pnWEE54Iylj/RD16B0E1+Bhn37kquE8tEOhWAFvJxKXBig4fZsDJ/q8gFKJd3akympx'
        b'Xk+Kf7qXh3bSPeFyv140qBw8sdw6j3rvIdE9HY4ccUUFHS4xK8Ph1sztFH9NWO1I1lyXIOw6frFpsK/ZD10k6zCdms2FOjV5xwKTNUjgHzzuOZj5fSakh45ei5uDF9VQ'
        b'tT1eVooOyJ/Zr659PkkmS0lkjdg1T1qndsAGKF1waKfY+fa42CjhH5J9qesQ3RBOfj2UOUzNWCYEnLlsfj9RSmh0TOrtyX3YHLhL3sKBUjXOfhenGUPkCzUxxPwbsnzb'
        b'iftZcEaw5XUodrMTjjeD5J3a3Z0n5HOlaV4k1vfelDjIHrkDasWLfSIFmxIf7lBbp/EMW0fRSxCgyej3oAruQe+RbnngSTmyFFOIeziE0rSNxOHbMqFtRCjegceyDdXi'
        b'A/pTVqob9t7j8C759n6t6qKk95msuXe34aWXIwafuwwvwx27iFTkaGvUlMo2HxTSP6CldQaO4stxTSyD28r+MVvUpN9PoFqm7AwcWzDYvLlmheFlc691x0c7LMRnIVZ/'
        b'jhr9cgerV6+7zZ7Xt5c58EwNFQ7z5K1cxIqQQUMUyfY1SHZwP3QUFM7De0sluLjCOZbwT4EIA1AI9cuHxmIK/m19lqVX4r05JuFy3LSU8X+FTxdODQugkryaVZ2Dd72F'
        b'RmDZNswfIr0D2l6HMAkfKLFjPDlaTosZiqa/7PzztvRnKM9UrtBgFJ3HwaNlQ/W3kMgOkROOSXhbibf9sEkwf8IrUPCSByfeV8LlPub7O8x/jZjCdS4Or/WnSr1aZERb'
        b'vxZxRX62wk9EuuWkTvXDcx46t5IiHd+FDVuhdikz7aboPidKkLRIO3KQCiXjVbvu3VSPtgf3VgqNI6YJlSPUWz/zpQxL8KnXkYxbwAPKabWFsgIhLk+d23C6TTS+iicG'
        b'qHY9ObaE3WJIrDdpht3SWyOoQ9lLlqHOnSfFOzqErsYGsZHsgH7XLAiDponC/FrVSbT/GBYyQQ2lBCNuywpXocKCQZGROutjOGvlTBE6VCqs9ZS1p3iP4aUtHInsjUKe'
        b'WKxyTMJ24aRcY32H6nHM2D7VWazEJzlTZEu5RIH7/st6LAw4LW8AY06r4RIRe00vg/UtlARylAH5o2WUAW0OoiE9AhvNhCmD4BnBW4IwoXBaNMyEmnAzdkls2lZRxSif'
        b'TYhS5PnHVi3hpRLvULlUAld1Av1Y+YJmKFWwQ4Sw8DKDSwa4JYZs8oR2s4mgTPMGhjYGx5esFEOU+BRu8OoKGUCJXF3ZSkiTA6YJ0BbE6yv+0CSXV+A64QkBpUqi0wjb'
        b'MzYXuwgK0t9qIlkgzZMzoMTsrOA5bokgrhoeL5Qh7Ul3XzMUE1AvdBIg9BJe2SJaXEl23aJeox8vl2tW4n0Z6dSQANrMrgq2bRz9QVvVJMrrnF5JoIuXcaCag1Nexwle'
        b'IcakktNsEnWcaT5yHWfHUnnMsx2Qz+s4eBMq5ULOHGyRYeNJSmjLRSUHbsXJpZzQYEFcegK0UAOh09J9AvKfwcexMnHteCGVV3mWYbFc5YlfK5dlzo8gokdomEQMEGUe'
        b'b5nZlC3APVHlcSFsKqo8UYQJRFMdVhrNHFCHcuJquVSfbraOoqbcvMW8xmOeI5d45jnbCx9YMV9URGxwVi6JwLHN8vqNcDvHvJc2emmS2EtZ7lSBnEnvq6JEsQQvzZJr'
        b'JdS3QOxziQfcpCaJWfeIGtMZeIxPxXTj8PJMXkWZuEIuopDLkwsbeauxzDxSYjvgpiihXNLRZgRCf0BWckLUVxxInqK8sgTrZDVomrhX1FbWLZRLK1AJT+XC0GrsEMUV'
        b'zI+0F1dKoFYmvBwLArCT2wI+wwbBiLMh88WEU+FsHna6qJhlIwFsXqRohBrRcmiLJCoy5NlvyjUZPDFOVuBj2DBdFGVWEHwXRZksF7HSionzaR1ejHgIdWK+GijG8/Ko'
        b'O9P4rlwdmH6ZqAc0QIOsWgm7crCTqxyWw2NK1Rg0wSk7WL+HnROwM1fBouMEYytCR4jZdniTEuRqyLSsQt6U8sMp0bLmSKxcFcIzUXJVKADkApkvXtOKshDmz5DLQuRg'
        b'igXGDwiYLspCMWlyVei1ybIRe1Myy2tCWBck14Sg1FvM9RrcWy5qQnjJVy4KQRHK9o1X/AkcdFolJi0WvK7ajd2ivoEn4QnBxE7Seoopt4ThnYYOOCaYtxjOHCHK72oI'
        b'8DYJjl8g066XRfho9FjsHKHgZdx2QXsdJQoPBCkeWDJDVKFIAS7Zy1Bl0wUpU/CyKzWpec58VJR6GjyYPOGVPHgo16fWwwW5PuWMj0RbFIHxTrk+tYMXdXiBCksyZEu7'
        b'B/lGLbZpuJDqRdul1LHyvguT94rqFZZPkqtXWLxd1uhSHyjSOtKY43zMXbIxQmi3ZTNYA/m8rkVB6rpc2ZKmyBSWYre71kI+6h50CF06DQUkSaFLrQemiqJXGMVqUfSC'
        b'Tr2sMEfh4ixeW8rkxWNeXPIzCgmvXR6ozSOluBnBsIX83n65Jkm48bq3Nk/D1C6iNnsOGkhY3Odrs82ifnZ2slw/w6ce9hWwdqmon3nslatnDrnyLptjsVyUzygOd8n1'
        b'M7weJQY547UlonyGVcvk8tl4uQJLelAE97WuxLWqHQwfM2j2gzuCAD0Wh2pdlczdn+FTBjegW2ePEvhstxbbJTbrsOBYPd4m9MWbVpDfa6QmJQunQfe5vl6C88IPehh9'
        b'tE4K9rq8yPVNe8X21+E5bNBaiclVBMf5Ps+lBgt+LZdm8eLd1K1y7Q6b1oiN7POCY1qzA5t+WGzjMqlKgaDW8/A2KOF6oQ1n+IQkvD9bRPwtWkqoSsjrFfbW7W7Z8zoo'
        b'FKU+FXRuhJLNSzaxLTs0eMV3kl5lnchl/BgrfbAkei2WJsFxJY+1lD+T3twQhMzHJqiNwuJojU82U+yUgtRQZOWHfySpZqyPwvIgLPPT01LnJ1LEcFOOw3rskGuz7XgL'
        b'6vxiAyKgDW0qplohEXdvzluTLI7l7D8aJp8hifOjFUwcVfEjKn5cxY+plDanVCf7AZWqUFXAXlcfcD6k6jugUosDKtVh9assRbmBOaXrVT/7dwWpgm7ATxg/1jTrDFni'
        b'PFOXmm3S5RkyM1IyLPsDB3Uc9EekfJrquzs7y5ItTkZ9e89SdRk0W54hI9OQlGn0FxO+YjTtsS9g5uMGTZVkyNqtS85OMYqzVT6rmM9s3dN7ZmtITs62Zll0WdY9SUaT'
        b'zmCydzGm6AzmQXPtNWZmBjoPurQox2Ay7NFl0DKLdBvT5WNbfp6b1DdL4HADkjKSF/FtpmXkGbP85VGcwFWRYYMoyMh6aUf8J5kYY9xn4VswGpLTddnUyTTsQmJvpv0D'
        b'F7P0kkms/OvXsfATbPtsgboYq9nC98j5viEuYE5waKhuZXR8xEpdyDCTpBiHpc1szDEIwnz5N1+dkVTDarAYxYF4YuJGk9WYmDiI3pfnttMvc1yoln0vug0ZWWmZRt1q'
        b'qylbF2/Yv8eYZTHrVpqMhiG0mIwWqynLvKhvRV12Vp+S+tPVNYZMs7jMmbw3wzxkMy8djDuyoYeyo2Jl57IXGmeZc6FSrWZyhhmPneK8tWSLB5vND2Fde3YpRs1jcqJ2'
        b'l7LvNniko1yZAjKF5C4v0Tsx3JlRB8fZeZYVHQ475CPb1xNdmSdj7rM1M1bZDqUy4S+dsFFv1hJIPq9gcn4IT6FJP1Ke/6YmxqyFrqzetn1QL5zmHspWLpr3OkOjktkP'
        b'CItShRPM859iHknJ3zkmDznvv16OZfl5cIoCMT5LoE2L80GshmIxm2HnTK2JMp9jfNP8dBAeQKdwwVPcD2lzIqGbr0JJ1rml7uLy6DiKmLnhK/llCvYXl0bLMbH5EIXB'
        b'EhcfqKPMg58l4pWD8kbatydip3nqBnJpPOWogqNT5Sy4hah6SFjE119i8jkjNiSK2WZjC3RTprITmvk6/Jwx64g9+4NHfhTnR+zkBItTxovLxTpr4dEM7d59WMFHdPOG'
        b'Ez6iITt1CXaaHCU+4CLP1RrtZ8N6KE4y78VmFwcmEvoKPAXVomUEwdYH5r0xcFchU1bsAC16peDyxF2jzXvj8VRvC5w4IJYZH2mhZeD07N51lqOMxbDVGbvMe81g613n'
        b'dbwlB/Ni9grhhpw4ldxQ6QuX9AqxioRXF1HTyG29TW5xMnw8tdNCKNHDjX/nx8kHs4SCWST7LQUzQ4OTY+fLOkpZafPrc2bj5XUqXrhkSXghIWPVLi+1mfI1FuMauLQy'
        b'OFa50mX1737/vazRb24+dTVi7MYznsdG/+BOeN3qH41vHVv0440+LYqqdz5wfOT1rX91v3R0eviZ99aEv/PeJ299fs+/fVLwj3TtNuk/1+meOe0bUWVq8Fzocv7iu1GR'
        b'r1cuqPvtP/xDrmPAB49mnD/iFPRhc/mv34v9dEz+k1e2TE7cVHTgeF79toPjrTXPi0o+bzu61OmDKVPf8n7Lb94nYYWv7Lnw7EX7w9xlm//Ucsj08y3ff+vMEf3y5b//'
        b'zv23j9Z+vuni+l81VL73uOHDCesnz37LO+Tff9g9+8Wb/xLwp5bfzXxevXtL/tuKL1K2vAca1/d+sijui1/s/GTD+Z+PGV3w1rUH1g2xP3phKFmfmWPbfrdec3LiN18E'
        b'fbsh9Wf78/QOFs6xeVvG+gX4RAQomAZqFFvgbsCryRZ+/DePsoiTfoHLEyP9ffWBWOFPaJ+561Q7p2CH6ABXE6A6Ki4AiuIoLYBnQJm0dp0Cy+OxwCKs8DrkL+I32fgG'
        b'BEo0fb4iUjdnWbqFH/gQEG7BWkp65Rtd9so3uuQF+GIxNmBtkIIFwhM1dsXDBQvPIax4jdKIkhj/SELwTDNXETjSFR9Al2UqT6CddlP+Qdl+O5+E3EMFz2KUhAWPK/E+'
        b'Xo/XK3oUPnqTmpuAk/j4q9+4B/1i3JJUU/YBY5YuVb6TKpAH2GU9zsLdJ/A/eDfzZu5yjzC9SlJJjuLlKimk8ZKz5EYvZ4lfdxHXnSVHhYa/S/3vvE0juYtP/pcr/aXi'
        b'LQpPyUSGxGIFMXpNj4qv2KOkoN3jYA+BPSoes3ocEhJM1qyEhB5tQkJyptGQZc1JSNBr/vIe9SoTT7xM/JYaEzctE7+hy8QTMrHuWb43bn7sKPvIk+hWEE383cqZD90T'
        b'8VGULL9+1u/DWpn7E1aQFxHqcofyxCLIN0RRByyh3D0uUs1cc5QL8jYItKafOTkqOlbOI1/HEolptyrwtis8k31nMZSQuvEEdPQukYDiYyhLVg4IdnwvDr3BLpT13eyk'
        b'SlXZ80ZloZLyRhXljcq+vFEl8kblYZU9b0yjvPE9aWjeKG6CG5A4mrL36Ay9qd7gpG5wAjckQdv4F/JIkzHXmmGSs4cco4lyyT1ymtN7Z97gQB/XG/+JEN/1tGLGHuNq'
        b'kynb5CsmM1BLyvDpIaeXkyuniEM3MWxuZN+UPGLoDodbgieUazINaboMOa1NzjaZjOac7KwUyoNEXmlOz7ZmpvA8SU55RIJrT2qHz4hWZ/At9ydglGwbdCEBFmsOJVb2'
        b'NEtwjfJDH97Dny+k/5r8SP1SfqSOtS6l7y54G1qHu++vCGwJ0b5r/eHGRvkuQH4tLjoyhmD1TULeC/GReWPG6gtqyczn6TkY9mFi4K/0hghDZmpm0keJO9947/l7zyuh'
        b'q3LhyZaz9WfbC1oibp6sPxlcpj9ff3Lq+WNzRjD/Ue84aBtGdesVluly8mWbpvUl08AiLI2xckdJTnIKC4VOFd7BBrhh0YloiZ3BUYFryVFC2ab1veY4EbpUWXAVz+oV'
        b'g+z+qzyeMP4erXzvZ7+Dc5UdXAp3YaOFIzON7HdM6h7HXs3qcbDriOxZXPgbv0Fz0PJKEwfKJu5Z5G7C4/AJ3x3gcW6OHupx8CE8gRt8k9gczPc5aJe78IGQng9FjM7B'
        b'SPjUFg6GWygVPA4dlPDU+St3RM2F8ly4BU3wxJnShaoRWKslyCunMTvmavNcpRWUtUiUd+LNVHutDrvheIw2L1dSUAYpYSElJm7r5Wzt/rbdZuweGbIJi1VMgVXS+Jlm'
        b'uVxxHEvgqDnEpMDL2MSkbAb3xuEJuYaGzVu1eXkafAT3aL4TDGsOTiW/yR1fOnQEC7cHl6BRdnw1cMI6iU9ZFL2qH3jPxGd24H0R5Bt/VsDdGD/yqNIkR6aAciksA568'
        b'5DH74MEy7jGVwmfKt4YqbI6pjn2eU/W1npMj7i+/CnELkx+Mt7/Sb3Afw7t/PW79CjjJB/+vo8nkTEGW2Wh5GT8OIZDzJTs52UouMiv5ZUJ7EeTq+JW6MIrqJu5CwylU'
        b'JFuyTYQJc6xJmRnmdJooab/oaXfpYYQxTYbMl+ZbRVYaOIA2AxeKVdw17rshbKOvP32Eh/OPsLj1wfRJ5PmuClklGsLCfP1fmnHAngidZg+Lg/kmBZ9zZPRLs6Zwb74/'
        b'ZwgD+c9fFSf7ZszOeTk88p+/LkQOEt7fFX5LbDj4PZLgN/dQeqyCgmHjS19wOaAcNrychHqBgVLTPZKSlYkEwRO3N4VnyMi7bfHoRVnKCPqWuCQn0YUJFAXXp8AVO3CH'
        b'ig2vwcMlsr86i2UrKLMqTB8DhRQPx0hOYw+IaVoMI1M/Vy4gaJoY/daocHLdoq6Jd+D8mjn0JZg5eQRjw6vy9IXYhs/m0BZDCONtDYGWUDHJf8eMSmHSCsaIkC8zD/BJ'
        b'uFuHlgNwVJ4kNjE4YZfA2duwZg6vgbN48pVJ8auxTkzx9hZtykfMh5BeYvQXqa+wjRl/uH1RMndxBv7in2eUB7vCbMJz3jE9+e6nHua6Z70tveo3MuKU29pFm9rip17Q'
        b'WmID33hj5YGZP/Oo2rzzp59/fm9ZQ5DTtkQXt58VtO741nemHPAO/rnW5nVT5z592c9U957k7+zp8Rr16XZd2ltvVM27uO7+x9LKdtfVxwufblsW9vbCTz4p8XV/xTvj'
        b'xEX3yHkrvvGd55WxW97pORltWnvzy/m51fe7e74cH3d/4e9CU356NdL38+5/fPHjhj3af/rDyOVxoQtTD+gdBZ7Bx1i7cDxUDcBeAWCDShHst2PXgiGxntDSfR7vRbSH'
        b'Mz6WGdx9u8NV7t8JgXEYFkQpQQAfEuXAgrFOkxoeeQieWHiRdi3kz9dGYak+BvnhtD17GAc2leNcb4t8fHtRHxVH2lgdIDFFnrRyN3RYuIZ47cN87QgO44LiOKWHFb6e'
        b'rwp8h7dS8ZriwEBU5orNBouoJhfkhUZhWVQfchw5W7lkXJoHVOslOfo7/k0QTE5InGTARUFCpCOz5XTkCGO9iIu/Kwg5uQqM5SqpFBxJTaOXu/1lGjMgYenHPT1K8tcD'
        b'8pSvg0zKAZBpbF/uwuf+eEDucmbiwNxF3DPb7DZDgCW/CRwuceSsYaPQpoRSAsM1eklUzPOgXi+X4rEgtbcUD6VTXnq2ow/u8NI/hW5FqqLvGQ7pLz7DoRTP0ai++P4g'
        b'77Ve9n5fkbGnioRbxNmBVe7/bYjzle63l0uD3a8m1spTHWiPIKMa4n3hBpwZ7IGH879wUhJeLwYrsDTzAD+ll+unmjnihiY45oYPo+ICsDgGSzdgYbRi9GpogRNwDS5g'
        b'WR5917N4NwfohmJ9RuHBDxTmxTTqTP6lDxP9BUx4+7oMFF59435l/WkpYs612QEp/pv9DLEGzXdnByb+JvHVN92/98YFDdswY4Q6vlCvtvDbzLyxdPogv7EXm2SYINzG'
        b'enwifA/cT43zC8AnUNPveyhZvi88BXRGwFm/QHvRZz7e6av7wLU5Fq7CWIfda2RnQkusIFTR50ugFjssPDNdSqHtSl9tSLNntFwZwjK8KpueYlj7dkgzWvqs263Xuqdy'
        b'qxY1E8k0vs96W5RyrWJYbNEiyY3CKvkYd7Ic82jZKo+y37oOtEvur/BUFFT0F7PqZtlrWV7OX2NzChv7m23uxiCV3ZCTmWEx9xmWfLRA1qPjV1NNhjRxVDDEyHoN1aCb'
        b'Oyz+HdTZJyxuU+zG9a/568IiVodFbdgUQ8B4ZWxUQlhc+Gp/3cow0Z4Quylm1er1+r+MloezJzlfSHJgK5I8GNMluvyP92xmXcjZ+sAnmz/k5sefkiuKXhfRh1ZUWKWH'
        b'Fme4sN8ZTkElXIiEov0MajXOUBgPjVYBejtGKgeOJksSOG+yYQY2q+DqbMzP+DxKqzSvo841i9mHidt1rm+0kcm0FwSfmHqivTqyqv5s/cn6gqkXn0RcOx58ouVCe1G7'
        b'0mfat9uOthTkTk0OSB6R3O4Vf9LDewPeP7p/athsZdpEVqIbdft5hF4lW4uN3ylPcRqb8Xafvfitl2ug3WhjvbZw0DwgrL52yML1btpOicfHddjdFyKnYZuF17s8CJ5e'
        b'iKKgDeV4OyjAR8Oc3BVQz1wHgeThDcWZMIZ5ADAf22srwY6Si7AWVxmeT+yzF9OEodO591kI7+UzyEJ6XF+KXJfwcYJfhL9vbD/g5nefj4dHqnEr9ullbK7De/vskauD'
        b'MHYJVgRBsRzlJh5RpW8Y/dXmZK/YiYcT+yp2f41J8YrdjqEVu4GRTJS2sgx7BMIZJoBxfMPP5XKMdIEC3eCQEikbVqbBYiG4kmygaDR4UhHXDClyUfAloDZorj7Q9nWY'
        b'TcZo/1cDqzSsI3C0B9amBdAwfNmsCE/+xcA6Dc8KX7LR5LFvrCJR4Jq345zkW2im84d0zbkUtO/0xls4hmdFxMVqLB43KOJGY2F/0O2PuPF4Q6zw0WqN+2eSu/BWEzf6'
        b'sIwqQ6vS/Bq13J/+i94wLAfh3yamp0YbvpPqv/63idvfeO95W2Xw+foCg/TOqpOxbi8uwePK9veajs84oW697NF6eRN5HKn58l1N67ITciXP4ZP/+Ml49e5avUZU6Jxf'
        b'08kx+mbU4FKeiNGbJlr4DeuOnqMGJPZxomKO5eRnYtRsfiw0UhqeDl3Cw/jBA2zohxFrFykCcuCsZTKXxFWsi/YLJP/1aOghDlzcKhzYeiyFDm2Um8Yezvsd2BJPi3j8'
        b'p8VxqoiLh/DCYDqmQJWK0MRDfNqb0n9dPdFFhHdSbG42wm+N7/Vbq7m3ciF/I8d5F8nk2ee59MoeLfd0CdkmnhwMiPjDLkjUePV5Nj7LokGe7c1B9USeNu1IDBM7dF0+'
        b'3AbxNNTqlbGxa/TSGr0idk3G985cZeZPac651d/ddOrdDWPWjbV98uSRk/6MKvjok73f2LlOmfStYmef9B++VadZpwt936s6fO+EsqTPj9l++WL5O4++7dpg/tX3LyUs'
        b'Hbl35pLq3A9/Er9ymvmbvzz6rKHnxDfXjJu12/2dX7/v3fObz/YHf6K95/jbrepTXW9lJHz//Ju/nPGD/Etnv0xqjXE+8v6vHk/bXLlssc83k5QrCyZMi106Yu4/hud7'
        b'v/CvO3GiMf1aWd749vMz/I0e333t+drN7TXzWo1eH/74jTWh7RcCMo2TvDLTHBb/+BtZ/9l27vWPfv1GhC3NVBlmMe37fpv6lQVrawIfLlwz8lsLnx/+KDI2t2bOpWvn'
        b'zJfe/Y460BSZfe43v3De8oe8ssMa9x/+cdF896TzF9+fhns+/rfMcz/9eNf896d/1/Hz/W+EmUo/LQye/OH8G9WzSuc8b3wa0vog69MlH3i8tf95VNO+ee9+qN9SXVb8'
        b'b6PwN1ONUdtem/aGvmzEP3dt/HGXy3dbfba9+M7vl796dq3TtgcxH1Re8/3HTWc/Grv1v34X+nDU/HW1Pnnf/qVtw68jXlmYe/15cKdh52dN7n/4M7q+ONjwOMDjf374'
        b'/X2bg2Om5hz/8nDxuN8UHXn8yb6KgpLr/5xq+fjcdEtIU9APFzu9eP1fkwM++fbW4vWRmp9c+eP20o2PPvzTO2d+lPpf699ZMv3tpz8yPXz3zZpDvzhYWab7IrzrjxP+'
        b'o/udOZ+9TyYs7gi7wx/RLYmWGF5ylBbw+ygr4I5In109vPpSY2FLlD40CnuaBNUC3GPl4fGyA7hDIfVlDwDFr4tFds0cgyUErMsCtuzTMM1OxXTsxmsic1AE4TW/tQFY'
        b'GBkdG8ofudRCuwJrF6wQVj8Lrvvy49AK6oClkXDRm3e4o8Ab+ASv/o3nn3rXv+249CvnUZt4wBj2TfgGx4SEzGxDSkKC8AvhPMJMVygU0lxp8p8VCn4yOlrhqFKwYX6l'
        b'v9PV/1Y50zdJ8aXGUXz+3/vt0sS6SfzXURqt5HUOz+UK8pVjxzgTp9wlTx8Fb3EV72783TS51wOTE1UkJAzwnSP+/2Uqmab0OVq+EFdv+YzoX2YOdLICV5YE+0BJgBUq'
        b'CDRT0IciqHAgc1F6uUJ9RtCLF2rzBeqWWvSDgJKlzrBi7PFf7wl9tmasv+oH3xyzb4I2Wb+kK359um/kIkPHvTd/+sMdpzJSn1asW7dkdt23vGt/HxIRtOHqTMv0t9Nv'
        b'zSmO+uL2ET+zadWje//26cE/ZKqCnSccOTFzpyqty6ZpiL428tmbj0I95366wvfun0M/21f2/J++MKvGbE3dHn//l8W7J2bd/+DjRe9Gfxb3s9k/L/z0P9WTt+j/JaRD'
        b'P8IiP/MMLVPFPw6hbZTxN15t00KHApsd4LLwAV4q7OK5SDv1iuM1s1FYPgcfK6EeHm4RJopndsE5KIGiNM4OHm2gTLBjtHLyVF9Rj8Nbc7EpKlI7P8Y3xoFpVArHKU7C'
        b'LxBWurnLb62aSVH89v6neB7Pw2MLf6Jl0XZ+yDSkolEeFBXgG0cuq5xiW4WSvQLtDrTq6YNiP+qg2KEjNGxCuGoSXvXFummiT+rhaOzE0oB5c7EwyDfX7q0mWlVwEs9B'
        b'nUBJmXgriEO1KCxxYKqNUBEgwa0DWCW7vBNQHco50iFBESenl5ZJcFEFTfR7WUZTBZugGUv2LdFTNJbVRGIj1yk3JWOjKHjClVF4C0v0ARa4ynv4890JbCgR8rirZngZ'
        b'bKL+GDU22i/O3yUCiwVVJCJ8qsB7B7B7ELry+vt4t7/jm175Ve4xIyvDYnePPEVkI3iqRGBPqZK4E+CAz02kTzyBclZ687QqyKTrcwBTepSZxqweFT9w6VGLokGPijCI'
        b'pUeVkpFM74R/snqUZoupR52032I096iSsrMze5QZWZYedSp5Z/owGbLSaHRGVo7V0qNMTjf1KLNNKT2a1IxMQkc9yj2GnB7lgYycHrXBnJyR0aNMN+6jLjS9c4Y5I8ts'
        b'MWQlG3s0Av0ki1NiY47F3DNqT3bKwvkJcnk3JSMtw9KjNadnpFoSjByV9IwgFJNuyMgypiQY9yX3OCUkmAnf5SQk9GisWVYCK/2OTd6sl4n/TyUT//89Jn7QYOLPupn4'
        b'Q1kmbikmrk0mXj828buRTHP5WwB/4495mTgUNXE4a+IpsIk/+Wbi5QwTf+TWxLlv4g+qmfhj7yaOP0yL+Bt/jMvEFd7E00oTL+qZ+EGPKaTPTXJxOPe5yT+GD3CTou0L'
        b'x95bjHrcEhLs3+2R8YuJqYP/kZMuK9ui423GlFi9I7/5JyU7mXhCXwyZmeTtdXbV4fk2XXcm9pss5r0ZlvQeTWZ2siHT3OMyEP2ZlvcycMCbrH9L5P8WtYwHZlGaU2lU'
        b'SkeuY1FjJR5q/h9JRbbH'
    ))))
