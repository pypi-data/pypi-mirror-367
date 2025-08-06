
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


"""The Python Fintech package"""

__version__ = '7.8.7'

__all__ = ['register', 'LicenseManager', 'FintechLicenseError']

def register(name=None, keycode=None, users=None):
    """
    Registers the Fintech package.

    It is required to call this function once before any submodule
    can be imported. Without a valid license the functionality is
    restricted.

    :param name: The name of the licensee.
    :param keycode: The keycode of the licensed version.
    :param users: The licensed EBICS user ids (Teilnehmer-IDs).
        It must be a string or a list of user ids. Not applicable
        if a license is based on subscription.
    """
    ...


class LicenseManager:
    """
    The LicenseManager class

    The LicenseManager is used to dynamically add or remove EBICS users
    to or from the list of licensed users. Please note that the usage
    is not enabled by default. It is activated upon request only.
    Users that are licensed this way are verified remotely on each
    restricted EBICS request. The transfered data is limited to the
    information which is required to uniquely identify the user.
    """

    def __init__(self, password):
        """
        Initializes a LicenseManager instance.

        :param password: The assigned API password.
        """
        ...

    @property
    def licensee(self):
        """The name of the licensee."""
        ...

    @property
    def keycode(self):
        """The license keycode."""
        ...

    @property
    def userids(self):
        """The registered EBICS user ids (client-side)."""
        ...

    @property
    def expiration(self):
        """The expiration date of the license."""
        ...

    def change_password(self, password):
        """
        Changes the password of the LicenseManager API.

        :param password: The new password.
        """
        ...

    def add_ebics_user(self, hostid, partnerid, userid):
        """
        Adds a new EBICS user to the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: `True` if created, `False` if already existent.
        """
        ...

    def remove_ebics_user(self, hostid, partnerid, userid):
        """
        Removes an existing EBICS user from the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: The ISO formatted date of final deletion.
        """
        ...

    def count_ebics_users(self):
        """Returns the number of EBICS users that are currently registered."""
        ...

    def list_ebics_users(self):
        """Returns a list of EBICS users that are currently registered (*new in v6.4*)."""
        ...


class FintechLicenseError(Exception):
    """Exception concerning the license"""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzcvXdclEf+OD5P2cKyFBERsa3GwtIVRezYqYsNC2rYhd2FVVhgC4IuNsQFAcHeC3YUFbBiiWYmyZmcueQu+eQSLpdLcrn0eiWX8+6T+87Ms7vsArb73u/7xw9ePDxl'
        b'+rz7vOc9fwRuPzL8l4D/zBvwRQsygZbJZLTsMVbH6XgdU8E2MpmiXJAp1nJafjPQSLQirRj/l5b5WiQWaQWoYBiwGBin8EDntUpmKmVApowBaxRaiU6W5a2V4quc3vvQ'
        b'q69OtolZDLQSrSRTtky2BCwFRnYJfl4AvDYrvR4OkC3M0ynmllnyCo2K2QajRZeTpyjS5KzS5OpkSu4LCW7mF1J8MbH40sFE5TCOnnD4T+L4b47AFzvQM1rcl83ScqYK'
        b'VIBydo3YxlSABcDGVgAGrGPWkZoBrZlT5TiHRIz/xuG/3qQgng7LAqBUqDrAX8jnhfmk+ruzREAdFYAHT51/KpgHnwl5v5/aBLq1iBYUQ1rE2oGd03OuVjFP3ypngZ6t'
        b'4lXWKHwPD4aPXxCJ9qRqUcNCVBWxCFWhmuh5iQsTw1AdqlWialTLgZkZYnQJ1sQapi6sYMzhON/JyMlfqb8c/Yk6X/+1+v6nETvCNImar9UPsgNz8vT5bNumfvGxYNM0'
        b'yeJ+v1SyliE4hwK2T/HGhcr5cFJomjUyDG2NZsFgeJlHl/qhTZb+ONUcrQXWwHpUn4KTwDpYLwG+heMCuEEZE01k9JRcBxuqNHmReaQX8vKh/yS9qXCNzqjQC/M+pcNX'
        b'YzbrTJasbKsh32Iwkik3k+kB/eSML2PydmbF5fF6qzGnQ5KVZbIas7I6vLOycvJ1GqO1KCtLybnVRC5KxiQn9wT4aSEhpGBfUvDn/qyYYRkxvVqfw29ml8CjKWjH4ogo'
        b'VWQYrE53H9GIWBFqkkzLJ4WOV9xnHogS53oV3WP+uWRv+HlAAaVyiIW1SEFRQq8/rPtAm+vrAJQPp9Kvr4euZNSG8yKgUPevT+ojZAnL5ECV0g/fqeXpfnHCyxVTJaAl'
        b'cgCeAXXqGqACVgJQ8AIe5n3e8GwEbk8VPAB3oPoFMfOF2Q+NigxFVdFhSWkMWL5MmgoPzlQy1kE42/MTw/3jvXF3UiJloWgrvATP8iAE3uHhAXR+mXUwKfniZLSZzGE0'
        b'7i+sQU3wJplF73QW7QiGN60DcRq/HJzAOc2mUOdE42lGVSolZ+1Dyjmzok9KpDI5TQTEC8yolg2C18ZbyXgnDUcVKXQwk5L8VZEs8Ib7WHQWbhlnJYCG7sD9aAuqSUdb'
        b'k9OiUHUqPM8DdCI+AFZwaEMJvIsrGEDSHUFN01KSIpIi0X4fCpIi4Iu2ciq4W0VbgA6hPdoUETyL04gAzzPw6Jx5tP2ZcEuQAMVpSahOmYTLr50egHZy8GZQLzxUJA1u'
        b'Qnt2yuhYnCAFbUvHJfjBdr8h3ETYAKtwGgLtU+Fe1EbSJKUJSVYv9kUXuVEZcBNOQUZzJdzo5w3rkhPxPBWhGlSbkoQ7HIgOcei0D2xxdAUP8ynYgmoiVGhbUoRpRpQY'
        b'j8llFl2eAjcJjdk9a0w42paKBzxCGZksAugkauw9iEM7Y+EpCqzy6Wh7CqpHtemRSeF4bKuTIpKjoxLTxCACiNB+ZEettCR4AV1DF0lLwvFXtBdti2KANzrOousrOauS'
        b'1HVlCqpMoSlIt+aGpmBM34ZqMYDNNflFisEMXow2ZKM9tF54ay28hBNXp6fOQ21xoYmpaJsqNT1jLk4YMUE0C7fKRclYd/q6jxJqO4NJI2fn7SK72C6xS+1edpnd2y63'
        b'+9h97X52f3sve4C9tz3Q3sceZO9rD7b3s4fY+9sH2AfaB9kH2xX2Ifah9ufsw+zD7SPsI+2hdqU9zB5uj7BH2qPs0fYY+yj7aHusfYx9rD1OP85BfkEVj8kvg8kvoOSX'
        b'oeQXE+CeyK+fg0p4kt9KlXU4vk9Fp9GhlE4CcRxt7EokZj9Hxz1iEGqlWKWKVEbCKlgfIpWAADUHL5bA89a+ZCTtcFcifAHdQjUY5jjArmcS0IU59FtMal44bIpIxGAM'
        b'NzPweBqqQI1oL/0WjI7A+nBlJKrCADgZbhfDc2y43kpRDW2EB5PJ7ETgWeaTGLQLnoZ34Fm0QaiydsXIFIxh5KMXEwlvwFO4+UKxqxeh7ZiYJJKm8IkMD/fCy6glz0rG'
        b'ATapo+FW7/AoJQtYeI3JnDrYGkzen4Kb0O0UeA4jpRhTALRPnM+GPhdn7Uc+HoWbIIbRrRhK63GFzzG+szAZax1nDSKMIwne8FZSqGNwmduYVDyY54RS98Ejw1IojEUw'
        b'AMPyPnEc25dbLpS6BV5HG8OTMWali8gYHhInsL7wYCrtBGpDm/rSQkMjGZCM7OJSdtSCNbQTvSZ4cxS3Q3EnjMwUuCWCVjcW7sdFnoMVuPfJpC37mNnwHDwhEB37pASK'
        b'G0qCx1K0Bx2Fd1lc7WZ0hxKd5wrRDnStD6pJw5IIa2OmorPoBaEbu2EFvIw7cwieR1vJV3iZWbhURD8OxST8UgrBf1TLg4nomjiElaEtI+jYoMuT0fWp61FNIryAs5Uz'
        b's9E1TInJpyHoPDw7Ad7F5DKKtHUrMwdPDKX16MKCYZikkBLDc+H+qCQ8RCoR6JvHjxbDDXTwQvVZKeGEDSSTWfaCN5PELNyNKo05rAP6+W6SDJZj7IxLkmGrsOxSzmFU'
        b'YikqcRSV2HWcA5VynyzJcCrDyjfPM+Yp+MWPW379lfq17M/VVbmf4//8b2oTDnglxjIGvcLnpaUR3ks2TtpTWVsrH5jwD/2PoGHCNd8tavGvLOCtz33XVaQoJZahuJAZ'
        b'cEd/gTuhunQlqksi7AldR3YJCBrOc+hUkYWQ5kHoMDqKalZ3k1cwG5uN9lhGkDk7BpvxjBG8jUjDJLDamSy3VIIln+082l6CLlD5CF3hUANJmY7hFG4jJcE2dEiGGvA8'
        b'w9vwBQshA0NRJdqUPNWRLjUKVtMqOW5IKKy3UJw8OnlWeGQi5lmF8JoIg9gVFm4e6W8ZRuo4jWe6gjbHyQxQnT4yWWj48DBR+sRSh1jURfChb6nY08EXaMyrWJfcs07K'
        b'CL++jIwx+bsEK76D05otHZzZlGPyIW9JaiXrJkuxpl7kPsAlUJHM610FV3gIVBSOG5hhBDHQNjHgI5jJqzH67y/sWWqOEmCN1bNPKTPru0Ia3xOkXT3vz5sJkFyoyf9K'
        b'vfzemy82vPzuiw2vXGnY3uu+b+oC/YepEpAQz//zYwuWeykJ3RIPr6REhGJCmMLg6diPKeh5tgydXUinHbbiKTnjgiG4E11wg6Mo2CiMJtvzVFgthvxO2XY9kPozpt6g'
        b'U7blCrNXPmL0GVOga+BJlipSDJkBsAE89O069EZ0aUB4JGFLmPKamPVr4F24d7lr6BnH3wJnW2xkSPOUjEpoiaMyqWfzfY2FWYXZeqs5R2MxFBprSWZKOFgqSGBydx2j'
        b'XQ2ig5OeHB6pKg5XEYEVyxIcCIeXRegARtLTT2hG7hOa4eVsg67BrQVEPotZTikjqVkVkRToJQIBqILDDPBIfM9QN5pAHUPgDmtr/H8CeQzoicaJOhM4KepgV32Uotp5'
        b'V33PRFNJfbKeIL3l+z2cORm/WH3b9/wnX6q/Vn+u/jJHrldrQjX3Pw1rU2vP6vBfwOfqi5o8fbPurCYvW56byIyWw8wtE7ZItyRumXRaqojetzGWw1zWJ8erUMkIIN8C'
        b'r+Sb4YVEFVYzHJPZCzVwI7A60YI57gk8TxRE+a5EqAv4i7JyNPkC/MsF+A9iMRHyx8RoTYg5z6C3ZOlMpkJT1KT8QpzSPCWKZnDSJ15jyjV3iFetJv/dsKSb0seaCIs1'
        b'9XPhC6Gze9zw5esAd3yJw++GJaK9WOBGVanhWLCjqi7agQWgakzc4yaoMP+H19BOWCOZPx7ArVO90HUsOm00SCe9IjIT2P9oYMOq3Lzc/FxVjkqTqln50Vndggufq89p'
        b'Pscat0z/4QMAdK3iSyvfdAL2Uw2Yt9uguJONPv5iU0gn2RB03McMiLsWTPLtchuLbz3GgpDKCHgU1TkGA+2Dtc4BYUF/eJOHZ+eU94xM3Uwxz0jA2W5gzasWGmYPvcqb'
        b'CTN849b3KRoiKSRq+B1RX9UqFXG992m/VUspDc99V7w+KE3JWxQ46XjUIKIsVwWbyyIiVQKB7gWvcJhRt6MjFtJUFboMqwalU+6KFejQ5MgouC0dd7s+PAleCBU49ZIs'
        b'qT4ZbaTceAaPRfqdsF5g5p7pQtBuHm4K4WnCpWgz1tFJucrkVFVaMlaRBAFh2HOwDdaIBs6Bre5w4DbjPlZjTp7GYNRps3SlOe6oMljMCL+m/p0z38HhVG4zzzjne4Br'
        b'vknqI27z/Ym8q92j7+Ap4VQwTsS4XZuShucbI7sYDEe34I41onR4M8I1T84J7+tGzahC99TU00PZ4kFPfFuqyiedHmzykmpnA0XGopfXHTS/t/z53Lh+o8wiQEl9CrqB'
        b'zoRj6epGZBJGzKsAa73HGXh1BTxPjTQzBv7Fb5cfE/o9WC//NmP4yijBuNI0hGFxjaUN81dnrcwyCi/PjOoNyLwdMxQM+H1UKjAM9Q3kzWX4zeGbb6VotJqzurO65rzP'
        b'1UWaqgtndV9itP5SbdSHzT+vybzXAK809Ap7RRpYc1bapGHP7WzSXdQ0a4IkX/K/CY+RD1VPqHyPSex7oDI28M8Zn78d0+cq+NO++UsGBLc0ca+1dMS+PbrP7I1v22Pf'
        b'jhHHFp3GUvmIIb8Kr8Ckl9Awy4hlKQ57BLrjg6VD2MAWcuhCz5TjifSEz9OY8yhQKQSgGinF9Nf5S4VCDBZyeoclk4FuJCbYk8T0XD8jJKNwRzKfdoO79z3oDEk3Cd0F'
        b'WMfB4iEGgj7MCNiO9cljsO0xZlWmi1mVfXpQI9326gZqcpWg4G5auQTtXIR24CqjQTQW7M9SyGgfzAP8X3EsfX3+kLVrBHAZM4elQLshRif/zk8FTCLS3x4uHUyW4fPP'
        b'MllzNX6oTPkm8sEoXxjjP/PX+68efkl59lVRvKxvIjPw9a1Dt4du6j/szCb4ceCPacUzr7wcXvLXLPuw6t7i5hsfFl+Ryk1727NUL5Vs7bV4Zqpep72WvHvoSvGwB/rx'
        b'hf/OLGqfd/5i4tX3Clbfev2lg9NDz99afyoj66d/vbNyb7l2SK+HVfdfuq75pu77o4MX/+O5lTkDld5Ua4JH18ArHmrTBKzyU0JJtCZ4rIBqTf4+cMvsKHOEUom2poZF'
        b'JjnNwGHLRPDuckCVnAC0CTajyyp4wUK/8vAOC3zQBm5MGqqnpaCLmmRPvQudmCqIzPAWbLcQVo2OzIIXwqNQFarGar8SXhfDbWykEbZZiOUlBu3q69LLojI6NTOnXobV'
        b'7TZqkobb0U1kD08mBpJUrADHoVvesJVFh8fMtxCyaAyDFeFRSRFhyihUD0/AbVhCBSBYwT8/aCDlHhGYfJ8UiDzWAAX6ji7PpJrdtfFwC22tCW4cBHd4dyoKVEnYC28L'
        b'SsRBoieEqyKT8MCxAG5D2+VSThqH9njI9I/R2sRF1ux8g8ABhgnIOoHFOlsA5QGBDI+vgh4nw3cyjLRyxjTYDWEDPRG2B5mgU58g+drdcPVVD1WOdHfe8lnhoWloK9Zh'
        b'xUAaBDeiFhZuQJcm0+pyxA4kI7qh1IlkURwR6G1MP1AurpLYxFWggi2X2CRmVZmvjTsGbOJGply6GBgDeWBhVslM8Qwgv0uBMWgJFoNtUpLTJiZlTAJahuRtYEy8TVSU'
        b'aQDlotLjNtExthHMBCv2LGfLvcplpBabVwVr0tP6eHx30SY+xjXickr1+I6nqQPLvas4nNLbxuo5m2wbw4DiXbgdM2kuOW6lvMrLJq5gcK5hVbIqKbmvYGhOKc0pdcv5'
        b'q8XAJjf9uUou5HC2dy4o1i8GDaxxGC3Vu4LFbY+oYqrAKjG5w60RadlGRkjdwBj/RdMxFrGepWkXVXk70i6qYknZrpS/oSnFNJWtSuRIhe88UjVruWMSLa8Vbca64kxQ'
        b'weDR9tGKj0lsPsekWolW2siSNzYfnLdF62XzCQLlPnaJ3RvLcJxWhvNJbRzJV+6LR8C3gtFKV5EaP7D5ar3xzPgah7re8/j9v7RyUqPNt5EJIl95rU+5r41tYE2zcXsZ'
        b'2l7WNEzra8M5+mJqrWdxOj+jwsbY2FUc/jZJ60fuHe+lWn+bcDfULb9a20vI70pDavOz+WkDxpH/PjjNNpsvvfppe9t8bT6kPPLN6GvzI1+K9tl8yLNFmGN/3At/3ItA'
        b'3AvW9NDmT3qn7YPHlDW9JjzhPJ/gO6nr/cfCE3mPe9lLG4SfgbZvJdsP2HrR9vvj2oOrfEgNK2U2f2cbbFwDZ1JYGJtfBbOJMUot3sKdVtC/+6kWPpTkY+3aGDnqIRuh'
        b'cLFC1sEOqaZMEDcXo9YKWTljY1aC7WwxT9idQ6bskGZlGTUFuqwsJdvBRsV0MJYuKvRD2aR8g9mSU1hQNOUn4NChxWDNgJw8Xc4qrF51amCdCR9yikLTQybiC4aWUKhX'
        b'WMqKdIrhZo9GipzYr3A2MogsytoIr2bNfBVucAXjaHBeZ7MwWXyOcsySxxBFE2EE/+ps7xek0od+GkWJJt+qU+AWhQ43KynrfRhs1hVbdcYcncJg0RUohhvI55HDzSMf'
        b'9qIvyK3rFU+vvd1SOnM/9FIUWM0WRbZO8dBPZ7Dk6Uy4x3gg8PULf9rwh8zIh8zQh17DzcuioqJW4PdEeH3YK0KRW2hxjtEE/KeUd4gMRq2utEO2iDR4FlHr8Ctcq7mD'
        b'zyksKuvgV+nKsIqLay7U6jq8ssssOo3JpMEfVhYajB1ik7ko32Dp4E26IpOJcPEOr4W4AlqSMqDDK6fQaCHag6mDwyV18AQMOsR0eMwdItIWc4fUbM0W7kT0A3lhsGiy'
        b'83UdjKGDw586xGYhAbOqQ2owZ1msRfgjbzFbTB18CblyBeZcnJ00o0NUbC206JQ+Pcqez3LBLCnRxf+kTlB8HTh8FgBLeB3PEC7oy4g5wvsELhjgEF99mSBWRp8Jf6S8'
        b'kQ3CTyFYmA1i/MWBlHtK8T2xffoy/izJL6f5fVnCQ31Zkgu/YX1pecHMAFxWEOGwrLDA0iJGZ1LQ5RlYW0pD21QRyViKyeLGL/dxmdClQPAsoFjwJb5gXsWWfmADxwDl'
        b'Pr/BvIor522ceUCxrwVLruTPgPnbIa5cZBPZWBs3CeOLaT7mgMwqMf6P+UQ/cIzFtJHrBxoxz8E8iMd0nyecwqy38blMOV+6xMbj0udiXssRPoJ53xGMd4QjiLSkRJGW'
        b'x6Vw5An/x5yQlFScL/AW0zktX9SsJfxZZJPQ2sTC98UA8xXaAloSO0l45h3P/CRQ7Is5IEsNVSIVRt85ZBLpTCaRyxzXHXmnFJkmkvnlzDpLB6fRajvE1iKtxqIzTSZf'
        b'pR0SAnoFmqIOqVan11jzLRhiySutIcdimu0ssEOqKy3S5Vh0WhOxeZlmkcziJwCZmyWT+Blos5zlDsIUzDyCwhiPoYHAmL8ABwTSKHTJmWDWHz/7Y3iwUtt8xbwCx6o2'
        b'rI6GTRGFIzBE0LW1cHhdhPawqM5D+SDuB0Q+pRV1WwcFZCVU7+3UbGwM5QdYf3FXhlyilRZfqsgkM9WYua8ERf4YyHAm0xgMFj74DUNYZgXjjbUcypQwOGBWx1RxVd7k'
        b'vpr4p/C4EaRqGW6KXC91WSO9bCwBn64mGgLTZPCoIfNr0gDeRqQDUHa29HlcLUeeqJSkKmdxERxpWAWzCpjiyJ0NN6OcMwbSxokxXCeSO/yGnYtlPfomuIpILxj+9fiZ'
        b'wDqVr4IXg9LpNlLuhHLORkvFabdWiTGMcliC4Y1yco/f0ycbbyoiXAZjDy7HxtMyihYT16UoLGfyFpGexbLmBwyWIBmwRo4HSkQ48GI8VFr8bp3I6aqEMQMP3DaGapKM'
        b'CoMX0Vo7JCUaE7VEcrkYhDENNa1abZpAQGuGAISdxsdUcqEwu4LCvM5kUkqfmiZ2gqs8i1LDIlxxgXmaC1gxiLIsAVE5IX8si5+DWQqsrBwDcTAG1RBmTYwmJ0dXZDF3'
        b'8nStLqfQpLF4Glo7K8C8eBmpmvTDaVykLwgoKL3/U+rOdUjIsGGsFYpc7uqel6tB8YxzNYkTiP0gTHhD+q0JeXQfnOJDJilOR+5l/xHryXQ1R+KobCzjsBQATvEc1YJQ'
        b'qzkkJVVF7OB3UbNSDLyjWHQSNfT1sGNKHf/Ni/BFBzKxcJfJUnQXO00XmdwuqWDMwBjopRdRnztpBZPJu94T0iDBJEHwwyPfRHbAg0wxJbSSjl4On7nZhnxdaqFGqzP1'
        b'vIhLjXQsLg7THLclB+7/dhmXV1lj8T28gergdjO8EJqYFpWUNo+o7+mhvVOTIuejqvQFocSLgTqHwE3orNdSuBNeMzzYm8vS5V/+7alfqb9Wf6nO04ftyekXSn3S7gs+'
        b'adlfq3+VnXnv/Rd3vXylYft25uyW8UeGVw6hyxOxLd55+b2UIguRGaNhBbqOLsPDWB+tjSR+UMUOG0WIlYdb0HG4yULXx2/0R3e7GCFeAIIRInq+YKY4pNJ6LNWiBnRJ'
        b'WK5F12ALVe17wy3wDlmwHQcPEj8jYcEWHkUnLIQJwaYwuBvWrOb6uDxqqB9QErpKfGaSIuFW0oJotDWVeO+QJcRqVI8JNcAJ9vugRnQHVTlWPJ5AFbCYbzAaLFlZ7mbi'
        b'9SCPCDO+zJqQbgAS5czgWlEx6/L1HeJ8+vXxKyoryb3BWbcpD19yCX4QjR9swL8H3e17j6u8ZzCNE8CUw1BPmKNYL3aBKv9YUN385NU4iYr6ZlnhXdSYgmqK4R7HzKAG'
        b'DvjCc5w/PIluC/6VO5LXkhXMKSOoU2WnVxSGa4dzwdX5ACwPlaBd82xCluvw+HiSJ3peaCiGu0QO7olEW2HTwtDkNFQfEZUUmZzGAKOf1+SxqMHhcoWq4JUFkYsSUa0y'
        b'OS0Vp6V4k0o8+OAJdGwM3CMeFgg3GV55ScuZidKnP6n/Sv1q9lndWc2Se/vgjYbWJac3Kyubtkw71Li/tbq1omkJdz9X3LoqeMKSy+9tzd9g2xMiHtVi8zJLZkjMsW+x'
        b'e3z3VNa+KD9UcN4Afrgf8HnFaIw/ZKlYg07PQTUpsD6TutTxgxh4PM5GLWEYGs/Cs4KxDNbCO1G4O05jGboKmwRHiEtz1qPLFPUy4OWu2HcEVVioc97u8UvCoyITI1kA'
        b't5eK4Uk2ZlKKsLx4J2ZxSlRyWkQSrHPZIhXwqggMnyPKRK2DnasaTy/e+eSYdFikzCoo1FrzdRQ9Ap3oUUytZaygH8iZNYO7Q6pHbicuEtjHCEPYVyeiiB7NUVgBW/Jd'
        b'KLMKX4weKLMryB1lntQQD7xxWbInOfHGKUoS7JHqvZ4Se/K6rsa49HcX9viqrBQWjixFJzrdBJ2oQwDdHx6Adms0TlTkmyNgwuNxBx4bg3bBW/E0jwZeRIdoLkz6Khw4'
        b'9AgEggdTH+08oO3iw9DB6Lu6Dkgn5WsKsrWaKZU4p4lkspLsBaFwh5m0VzW5B4qNdqTAC4lpcJsLOtFux9KwsDDMjQ4ww53zA9AFAJvRll5wQwagK6mpcCO64bCx16Ka'
        b'CIf3z3wOE4DtozBu3HT1RgTc3AQoMRQEdJZMq4sYcpRv83g6OTqdPJ1Obh3f03SSol0agzsxHA+od95ZkELW/aLImv6ahah+QWI4cdbLwCw0Uom2pSZluCZOBOAxnQy9'
        b'AF8YT5dA3jPwQLp8CgsS1KlDp0wHlBBiTtug6CwSFyi4J2M5YA1qdzhl4IksWO8VnBBtJYLJCLhhekoKWXbEokMoql4skMF5roozMLygC7hZrRJ0CVdQYegXsowxE1x6'
        b'p7D9vOUL6j32qj4qQKlJ1eRTsSHC9KX69ezXsn+VnaTZob2ffUH3ecLH/xMDMiYyGbEVC+2xnyhbYna16Mx9TsWM3qCYu+VUxZ7KWYeYYf1fbfhFIPP2719888X3fxH8'
        b'4N57LPifRcH3JyY4HM3ggRDU1sXTzAvudy6ZoJ2CixA6Ph0ec1BETA7h8TXuFBGey6GFoVMq1NCN7lGihw4MzRwPz1GpZRbAmCAsOKcnCesdPsNhG2rjglHrFEFqOQ73'
        b'ZqWgbc5V6aihqB3LpgHrOFS7AF6iix6oOYpIampnMuK87D0Oq6hzMBUn6N0f3Vnu7uNxFO1x+nnAFni94NmJsC/x3cgqMhVaqJ5OqXCIkwqvBwEstdnwjD9WYeR0ZWPN'
        b'2O4kUFeqy3EQwE7h37NkAd1FglbRqXw9abHSsaYpd2WgVLoQX+oZJ8PYQH//4k6nrc8TSDiIjvU1P0LCeyK9II7nO8ajVtEs1J4Arw6HTUowFO0ORLvHrUT74Kl80pLP'
        b'RMG2VO/PhwPw0cg/s9dGvTBQCejKdpZ+H9Oyarkc497o90f/Muu68Ppj1V/8dnm/M4Cd+yHzc/DasSww/OHOL4H5OKFvZ/53eO0dHxjjX/nde6r8kbsSx8jvBX99DzTG'
        b'L71vGaZ7/8PEKSH6xLiXe/3PP9/6+0uzHza8KXtlyw+TlIumj3ytdEbHD/MvfzC5vzEoYOLnr0pf0l2Nyx53rGR1ZNQ16+X1dcbvb6/6+0t3rly6ZzlxPGXB2Rvqd9uW'
        b'LT+38OveYb97Y8xzCbU/1UbvOOD7G33L1IDVI5NvfpvcsdS8/tSxNvab+p9/4OqHhp85GKX0odCei8nS/h4cNPvNHZSMKuliI6xWwlbX+p1THIHN8ObzS2dTfOiTOVjA'
        b'voNl3bSB3vAKdf7Agv1FuENALOcswio8YXgGBSodpxWju/oV5fA6ddNMQs3whkOAIdKLGN2MGQI3U1SWotuJZMpRG7ruPu0i0H8sD2vQ4VjLdFLntQnPYc2gG9QEyZ9O'
        b'M1gSQsmLr2Wxgwa5cklAH7SRw33aga706k+HCV2MRYcE3xYCinQcMzh0KSsU1s4R1ijtMniGelnD0/BKKvVvhqfY0nIZnYpkVC3q7raK2VnzEHRsIu23EtXgDz2wN2iH'
        b'jaMwj2uiot8CdGsKqkllABOP2U4cplGX4aZHIKXXs6rtIhe98XYjFZTYhDqJzTqXyMcSbzOeGJLxHc8G+Inx1Z/1Z9YMfCzp8RACxY53nQRG8jRtZU3FwEOHKsKXtR4C'
        b'oX2Au0D4+CbhSukCgCzL8SIrq0OelVVs1eQLiz9UR6NSJ62pw4dslNKYzTk6TDwdKuB/ZCrp8HKUhEuhHcnFFx3jkMKkrL8k2EdwCK2fK30UkWTBhPXwDLwjhvsH9fYw'
        b'NTjXks1hoNN8ouO0gjQEqKMmq+U2exFzCTWJiKgaKHKZROZqLHjQjHjAVDm8W6kuZTMeXxwCs8MSq5c4JCy+SoIlLBGWsHgqYYmohMUTq2DP6mZ3gVmkojtAFgN4QZCX'
        b'ZXJPZXMDOqJkhb1Pl+GBSQ6hGjWspakwi0bVPAiZySeOXU0V1wGwgWz2EVLVltBU4WGJYhBi5jPmA8ONhvcZM7Gw74yM/kq99F4DUQ/vn9vcWtFa0b7fwCyQpEhWSX43'
        b'/dPMLSFbhl723RN4Or9E4fOJbtS42HdiXor9bQwfexKMyr2xMATE/9Z/7mGk5AWp4YVwN18Jw5hO5e+6THBev1KK2ihVnAxvCYQxxtfh+g7rYWsxbXUKrCZUCDWpsFSi'
        b'42BzDi94fJxEJxIkVmE3kYv+wENzncLG0+CVu2OwHk96FlHRKP4HOPF/PYiQyQMZnpOyWOHr3w1Kolz5BKwQd3A5+eYOqd6aT3Gpgy/CaTvEFo0pV2d5omDBm0rJPfEf'
        b'M60hl7UulF+NL01dpIv3gt2R/nGtU7IqYoUmaG8ykYuZ0j2KiwU6S16hllZgsjiHpSevD6urMSX4csZp4yTmY4q0k8aj9k6klXpuZJuIWmGbQowR93YOVQROJgi+UA0r'
        b'V6eGjAkDHisenvjmsebhwjdA3QWfcm+WcwnCE9/6qageOR0D3Gkz5vxXvIut6Brm5tdRq6UEXfUugXV+RXLUCsDk+fAmOi1CLaMUVrLehCXv86NxlupUFaoLV2Xoc6na'
        b'mpSRiEEy0rm5Fl5AVRFRsHU+tWNegTdl6K4MXXvs9l+OelE8nUtkN2trjzSFMOX0qagxHJ5NdcwPrJUT57neCznMiW9NpTrnWrTJi2CU0CO0Oxw2hTJitBOEwO28CbPo'
        b'M4bKF4/w5jScNu78H79Sv/bZl+rMey0NjTubKpruN1WMqilmGq429Lovad0/cd/84AX7gkZXfDIxuO29mq8nBAe1bFgYM9oSI4o9ialG0epv9QD8ZnnAjvfblSLqsoiu'
        b'DUOHwqOUdMuTGDaHoC1sLLq2mNqa4NUlXuEYpE6NI5SEH8dg3b+tnJKLtYWpghFga2RiBNyFpw+n8IMbuZXZaDcVWJbCpnE4CVZRYb2Z7LfjxzOwFV2FLQKxOoVuwoOC'
        b'QxaWPa65nLJOwl1P3CTjrSkq0mE0I4juaS9aD+aRxRQ5XRGUMWvCMAnIyjfk6IxmXZbeVFiQpTe46yZuBTlrpUTgsa5Ya1xIWY4vb3ShEJc93LHS8fscrMxtTEmPJBKi'
        b'c6phXTrV3/F/gdO6lI4YtNOhdzjc1TA9TqS0XAuP+BckraDumPxYuDGcSHKxcSwWORNE6AgDr4QNptYfeARuQXcxprSujkG7S9CVYrm0qFhezIOgiVzusLXUkZiBu+E5'
        b'Mx771iLg5VPiI/OVorbVBCOLRWBYAF+ul9NlFDmqQAdTkiKk6jBSH4fnqYWFWyL8rWQZDR0cpoPncZOv456FJUfAc2gX2jZmdUQoMQ6kOjeULJA6dj0zAJ6El71nxA6l'
        b'2eGmoeiQZ+7HZd0jQ3fyZagyEG2zEoFDj1Eb1hQVw0tY4K9fja6h65imWOiGshZ03Yo7soCHG1PRWdpltAkD22m4ZxFt8V7Cu7HmUpMqAX5oOzcftqNrViKHrsPkCZeK'
        b'Z+eIR6mrUatcJgbDkngsx9+Ap6k8S11SUY0BXoSX8VQchpvARDAx3LFP+RY8txbtTI9USJLQHngpMUkC5JNZdAS2wYN0r/j0CfCidyTatsAHU+3FQs8pdRNoG7xK6dgK'
        b'tFECb2NKvs1KGCXOf0CzQAzKpoFhYBg6Bo/mCxKiFPiD0udEanVEU+9swQH29EgxkIMb8d4KdcSxMTlYtKWv/9YPoyTYl+0H1KltoxOFtJ/PIGnflLI47d/ysoF1DJmj'
        b'mt5LiYoWTkw/1dTc4wTiE+ioZzsL4QZpOTxXavjdrmGseTpGjQeKyLSGW8nctODKN6auTYob9x2zNuUHZliGf8oP85vrfl+/nQ9qi1v2YNOw6a+89vai2LpKv+yPYn+K'
        b'eHF93EH12M+KXhj/YH+vD9Qfj4oYNT6scXvW1sVxb37/wm8af/sG17ujavfsrAFDVvV7d8niNY1BS16qZyQDXohLGV1XXHGi+rXcA1/++O6vl9+/UNhcvmdx/oJ33whb'
        b'cO3VV7f8adHLywsKr/77amnb5R9fTjq8uv2zXWmlv/i1aNCENvuYSaP+N638Dxd/+9yuc6Wj/I//dDcm61UY9F1B0IH7fyj/bvdG3/zfNcoXxBiLatYGfjbhysDPJv7q'
        b'tcQ518LbD6W8Zv94ze3vEsdEGya8nfyz8s91H5y68Yql9OxuyGe+Xu03IvmG34Wfvg+OK/5+5Yb8uZ/N2bnkz0c/tvwyJeXnbyb2s362eGtzTtU/f/6T+cD2RasTj/wM'
        b'Aj5YE7ZKrfSjnrJecP+qFLLVoyaCEA4OeKO7RaiNY6N9LYT8eKF9YkxkeqGrDGBLmGnwADxONToruqgKpxQEi/wCFd8/glL/ZDUWelPDogTy4t0/NJ9FJ/PgYVofOhjn'
        b'Sze9n0en6RST1bMatnwduiDorGfgHtQcnk5aQyQOCfBWogPoBRZdXx8ryJu3M3phGjYV2t28blOnUfoPd6FNk8NRVZItKiKJMhIR8JvE6eFddIRqtIPgLXQxhaxU4rKV'
        b'kapIFp3JAH1T+QR0AzUKvsMX4XF0zuWEvB61UidkdByeEpjb9WAZbRqqkcyCbYCPZLBw0FRMG1eI2mzhyWmpDCYCtwE/hIGHMaGroHVnlugcpRKSjAuIFD9fAPrCa3wi'
        b'3D2MDmowOjnVyTcnRmDOycYqJwiS9AvDYbuHyQNtDRPk8HruSRa5p1NO3RXpPj1yOMoV53dyxTmEJ/LU79iflbH+MvzHBjDkKuP88bsQspEAK93UrwpfiaOClHrX+GNW'
        b'5ksdF/yZAFbOmtY5mTFWkp9Nq3ZzDiSFvNyFc95xl62to/D7REh4zyM5J6xc54DM5y1SzM7OTldywtL/IVSHpY8U5xoZasSE+Dg8MIgS5SFz4F5Uo4IXUtG2dDzJxLoK'
        b'r7LoFAa53XRDZnAQloowzIWJAdosE8NjbCw8nZTDuUl8QU6pj/gNdAuSAFxhEhiPQAmsvY8+yLU8IHrk8gBHBU3+o2F4ImUKt5/5ulyD2aIzmRWWPF3XSDxRMo+0SRaF'
        b'waww6YqtBpNOq7AUKogpFmfEb0lYFrItVFFIvC6zdfpCk06hMZYpzNZswULhUVSOxki8Kg0FRYUmi04bpVhswBqM1aKg7pwGrcIBgbRVzrLxB0sZboJHSSad2WIyEEtw'
        b'l9ZOoP4sCqLCTVCQaEPkjnh3kiIdxeMe9pBlla6MeGAKuRwPXTJqFSV4zHCbeizAasYfheyu9LOmJ81YQL8oDFqzInShzpBv1OUV6EyRSTPNSs9yHKPtdD7VKEgfjbnE'
        b'81SjID65pDnOsqIUqkI8cEVFuC7iyNmtJIOe5hIGFM9VtoY0CM8VnhtzjslQZOnWEQ8jh283hcRbRfdN9oWbBiyIdi7TzZ+XtThRhWoXJCaL5o8fD5uUMtReNh7uThg6'
        b'vg+xuZ6V98Oi/UYPsPd3lp3sCfbAAfiMC/BZu5/e/ylXwjz0RkIpusf0iFThNJSAqHpW5Vw+CQ5TkWsZ7pn2uJGiu+9xEwk1U7JrGP+nw5yZKPOZhxd/pY78NDGrRCPX'
        b'f67+Ql2g/1qdpOG3fyF/vdaQ+l7+rMyBtYofVO9Muub7jkWxQvPWi2+/CAJW6S2aqv9pEn3VrGnQgq/0K/UPPo3Yyh6UBq241+L/oE0TesVb0hYUE6VVaz9Xi/f707Wt'
        b'fyUOHjjgIyUraGabJq0OjwxNxILxdmLIOcBGwpv9KV8Lngzt4agJ68rbiMjMWxlUHYYOPfuKkChrtUlTRBnJoE5Gsh4M56m3mgxTacF1N5DsCFaaHITJzUvNAcJub0iJ'
        b'Tj2LeoJ28o8nMUZGyECZxwZ8GYpbZg7qZB4bwIceCz/Eb3VwwYBwJ7S7Ngh3bg/u5CmzApTRyZiTz4ZnZxX5GdCR7Me4Z3HUOPL0O8I9/DJFoCeDgURlJe5I8fDw2NiY'
        b'MaPjRo2NhdexpmwxlRRbzVSZuYLasCKCFWh02U8ql/lGo2tePt6wHlbBWhYrVei6F7qAzqLDVJCP659M9g0n5PRWrxwzxkeQ7r8ZlwgaAJi7eJVa9nesKArgPIVfzZiz'
        b'8d2+UE2fXzQGJMz1F7259u8Fv379w8XDpr0pqvxRv297IjTO/yD3+zNHLJ/OnLAo/tKQymHV1/+6pGPp8knD9s1sH95/XfiNA6+0fPWe7tTPb0jEb4mjq08c8vf5+W+N'
        b'P/ypKvufYNjxPps++yuGXsGSWIxuOJTbgYFOxf8S2kINB/B0Nu4qtRwQbVOL2qnlAF6RPs6B48nuV6ZCS1Y20ZbxwAe7A3QsT4E4kPqYBDBrIp4KlB3FOdcaXH7Nj3fM'
        b'oik6AXkjvsR0A+TfeGy+JItRQ9HJpKeGZLQ1Glanj+4NT8VxoATW+EeVw90UAPSL2RFR1MtAnfpdfIaguq7WoX1oJwaFKLAcXYxCR+EemjggXpzazAWTyGb5v01eKYDQ'
        b'4TEirR/rT+LrpS6TDRFAiH5RBXnJqjgFLlotLxcVCC/9E5NXlnGhDPBXy/5Z/JzwUqPotWYRmwBAkTqiaO4gIITuuaSFTQuwer4rY+zg5Bi0lQfi+QxsxirmfporcX1/'
        b'I8Pl4TLVky5nWYWiWhe2MBswF/h+Yq0OGT/3o17/8Co6iY4vgKSsIDxQdSLAqZkpOegyZYLwIujVaXLLSMQqBqqKSI5chBWBnaiKqBzUowHVhxOtCFaHy5RsMl21NcWI'
        b'wQBQVeqVAOTvLVncWwHo1udM4wipdCmIOT28vXhP//jQxOVvxO3Ij+EEy8BBVDMGXcZ8JQ23DO5PWzeTNv2ziImz5cznpD8Bv0sJFPrzYO4UsBmA0ITxzf1f1F8dRF9+'
        b'EDVF/Qn7E4YU9egzyrFCygl8BKNmgf+98fmL7nNRVmGvq/gd5goHEu+Nq52gKL21mr4M957D7GJBwr2x+bONoUdG0pfcgj4MAbx7U+QrCstm59GXR/Ks4Hv8P2GiXCct'
        b'0Ynpy/8JzehXws4VAX/NKqvXIqH2Cq6BCeVAzL1Y+bL43lUDhcmOXApu4H8Jk1OHxnnHR9GXzSnPMaksiL83JTUqZGHCevoyy2cQmEm6OeVBv+/k87Loy2tDUpljpEdj'
        b'8xce8oo20ZcvzQwSfccs4TEQDvyb2VuovSHozYyBIEEC1JpowGmEl4h7Ke5txp/DkJmUIlssvCyIts02cN8zYK66ZC1QCC8nB76/yI8t4vDL8TGpDkh6ZYHP6J+4GEwd'
        b'1RHVieuFlwtXFoMNeOaKRiXrmhaYVxgaUBNvPonfrG7jMubd2vZ2gv/XZR0f3PlblKT0hz+ve/+HKqnUy+v+uPiEht2HlmRWj31xyOszp3zS/sknVd9r/+13FEne/OOs'
        b'xPumxavbT99cO6BN30d+t+zypnfnzzn8zQ7jBwOtNa9Nn77i5JS2m8sWyUK2rPp1zXdTB1Y299m79L465eaDG79q/1U/nxNeI/7MDel3ZqV/4pyPdA9m/3nrvG3D7ldX'
        b'7MiJe/nKybFXR7cVel3euHtnRQmcVeL7cEjKog/P7v66b9k76h8GXzo0/WZjsPeO99/46t7NzL8fX9r6/NuBlxXqVWX344Nanv9mynOfmX/po7m6zfeXmxouNO0Q/TO+'
        b'5N3vKgb8NbHiRZ8PXo3/U6rlvfWyL9TFk2Qf/PJf31w7+ML8SX1+jyLyjuzJfSnt/ZW7r0/7KE7WXCwZHnejZu2Neklp1ZzS2pGlrx2cbA4YaXvrzKTXzWd+OB42Y13k'
        b'pfsji4982re0Lbbj8MqHe6alvx377d+WzbW9u/bXsqMxL2ivDDaMnPrmP0Y8+OFcn+8+T/n2rWPLA8be+Vdy7ifNKSv/55ef/m3Xr++m/t30b/GVyaHDFn/3j/Xfp2Ws'
        b'TNn+RtTPQPVufcuvZiilwsr5xX7IsVMZXZkZwQBqJID74UlqNuk/Em0IR1XRGBwDWdjIzFWiRipjoZYpseHJkSmRioIwlQjIxSy6E+dHGRjcho6SwGVb50cLTEqwbR8a'
        b'TM0OpbAencO0Iz0J1g6CzZiQ5bNDoX0MtXsw8CCsCY9SJpMIh83pVEH1Qxu4Qhs8LJgPGtBluNVhVpmbIRhWqFUlHVVR5x94Nx+dNsMLmN03d43yAlvSRz/rsrz/sy8r'
        b'P7UQKXVyTsp2l7uz3SFyhmeDfP1lPOMe5Ir8H4T/B+PfAGYY5oIDGDH9IiPSJhfABFFmLaZRD6R0e5kvzkFMF2tCHs26nX5HZINHh8ShJXaIqOrnxrP/CxvjOFMFuac7'
        b'STa7WP0mfBnYjdX/Kcyd1ZPwi+PmJoUH93kqXk8j6mGx7zbaMF9Ywr+q9aeLTbANtbustQ5DR5IIRMMrItRciKooy12OLg/vXE2DV+frozD1RpXcoMlrKfkrHkuWC/dF'
        b'y7C48LthDsaTMIwEWbi/QpSglqv8HTZmXxmxGycW+2BZ4fuSxcDQ+IFOZD5KKPC5bwb6ra+d7Atj5LO/GWF468qfxkmLR8YtOhm16L1ls9WKxBIjs/jDzft809umTl0f'
        b'8MqPss1eR0PDo95t+dOO8IvtH+3pe/sTn8KycZaFDWX/2Ly6wThh6+LjHwccSvu27Y0fTvf9IWDnqx8xAaenbfj6/fdf2H6oefjcsg2b1/6kODd53cvh5rB3+z6sv/Nr'
        b'368vjDmweP2ycWcuHz2840P+b3+SfMtGr3hH7vAVXAvbjCR8bpfgufoRNHwuHsgNAmaL4A6nQZFYE1FVPLwAby2mOxvWoitwo/v0EEfBVAZgarA/BB7hC+csEnY2tCah'
        b'F9zTpSl4EQgI4+DZDLSTJoH2tKEkhQrWFLkmzxde5GbCw6hSsJ8enpQJa6Ij4S3UpIpEW1OVYuA3gMuCm+Ex2hwR2oSBpybdId64AnuVivvD7TwWq2oinDph0H+dADw1'
        b'eXDiq6cLEPkdQByAQufIqc2SJTtE2SBWiJ9AyIGpEqdVuSO1gHUU4TrRuff/x315BLKTxkm6Ifs/47oGaoC7BirDUSvc78R3FvjFcfqRZd0WmMmPWc50+thomUxOy2by'
        b'Wi5TpOUzxfhPgv+kuSDTC/+X7eJ28VpRnRAujazh81qxVkK3Jnnr5Fqp1msz0Mq03nVspg9+ltNnH/rsi5996bMfffbDz/70uRd99sclUkMnLjNA23uzNLOXqzbGVVug'
        b'tg+tLQB/k5JfbVAdCaVGggb21QbTb717+NZPG0K/BTqe+2sH4Br6OJ4GagfhpyAtTxXrwR2+qQJ5T9MYNbk600eSrgZTYtTzTKOgLhgeiZ6Uw2Am1jtqQtWWGTUFBmJI'
        b'LVNotFpi4jPpCgpLdG4WQ8/CcSaciJjmHRZJwRzosjTSHFGKufk6jVmnMBZaiBVVY6GJrWYSYN3DOGgmSRQ6IzEdahXZZQrHztsoh71Xk2MxlGgspOCiQiM1/+pIjcb8'
        b'Mk+bYYZZMCPjqjQmN8sntQ+v1pTRtyU6k0FvwG9JJy063Glcpk6Tk/cIo65jFBy1RtHBtJg0RrNeR2zQWo1FQxqZbygwWIQBxd307KBRX2gqoDELFavzDDl5XY3YVqMB'
        b'F45bYtDqjBaDvswxUpjrexT0cGCexVJknhAdrSkyRK0sLDQazFFaXbQjjPnDEc7PejyZ2ZqcVd3TROXkGlQkRkMRhpjVhSZtz2YhskpKd+3R7VB60VPs23MY+B9Wdrcj'
        b'Gw0WgybfsEaH57IbIBrNFo0xp6uln/w4bNnOlgrmbPxgyDXicZs2N8n1qbvt+gmhOcUqayS+50rRjc6tUyPgmUfu/DDA6zQCMzq6sJQwzOWw0rl6HJoYERWF6knw3ji4'
        b'V7w2hFEy1Gkhfyi6QcIdp0di0fYq2ZRQl86AAHiIQxsxs9xqiHvpJ9Y8F6dckZBEdleFfvwFvkYEfaFOdOwliFoUqknWsJf79Y1ZHROtXX6vraFxZ3uFsuZqRTs6VTGq'
        b'JrKyfW9TxfAjk+nWRB+waUWvwzUFWFGgwbLvyNAGN8Y8GB508nDKv9HVaGGfVQ08jg4K/JkwZ3QT1bgYtA9qFoT0TcgO67xxp5VpVniVc4gUfaCdl8LD8CZVMVbAQ+jU'
        b'8oJwtC1xDA84dIsxToa3BRtZnagAj0YZPIMHJIqhscTgxnHorLA/63isEtWk+MO7kRIajzkFbYgW1jwv2hhcHjw+O3HM6LEckKxh0AHY+DxVhdbimk+ShsNd01BVWqoY'
        b'SwnNDGovmOpkpE+xckccVSm7DnJn1+tBoJxuECAS+Zq+nmDr2k2ocnfNNW315NU9++exQjKDR/1bWacRb4Pr96dAd8+8R7Wg5w1JpFU2sBI4N48Tr1nnkhOWkgyuEegc'
        b'BiO+7MfNoPuSulXn3Ln0sN8jV7JwJZy2MOeJDdILDZJmOXSWx7TnkLM9DwPd1rKcS2JRT6wq11kVIaYGrfkxVR11VRVBqnLKcT0snOXkGzCZjjRjaq18chMcvfXO0pUW'
        b'GUyUCzymFcddrXiOtKIzD2E0XYe8s3In8e7rIt6OKK92kRvxfoY4rx6xdNzJJqlBAveHLkB18ABq54mORnxt96D91Do4IW8lPM8A1AJrQTkoR7thKw2YKEcnIQ0134i2'
        b'UtE9FmtdsIZNtgw0wPVxIjPZ4i8+8NPAmld9NsTI+dWHi04yIScqpSff/vD2hx+NPqQaVfZN3pWcV09+9NHrvq8PqHwr5v7Rk79pO7Mx50DYkbFn0dkf6ndf+2nCm01/'
        b'jdx65/SLS9/65V+n7T0U+p3EP7af4vUIpYySRGMiiZrtpIhY+bga7kESl8MmSnUGrRGlwAvyyNAkRxzmWyysRgfzBYN+kwadTImAN9Ap9/BrPrCS5oUti4KUZM1KOCSC'
        b'VzGwBR6A1cLHA9Ho+pBRncsB1NKSwlP/DwVWcLbT5gm0DGtLlJyhG0voUtgydHKlEZ5OQduiyUkafBwDb6MjgwTvlr3wKGwPj4SXihOT3HaG34anKP0t6kv2T9aJ4A3H'
        b'+RI0mGMkqqLa10IlrKQB3xNRtXSaQKED4HkObRlZ6BEz7mkoKsY3nTHHVFZkoWR1gCdZVcqpN4aM+jPS4LvdSJsjtwdtfaoIkI7Qu520dTe+nOqBtv7+8bTV0YD/B8LR'
        b'jDyNMVcnOD84xRknmncRlbDE87RSklG3+mmEo56DUvIqx/EtWrh/HBVgEtCtSE/5BUOiodT3Ld68BKd7edIJn9fCgzYoAvk3+5X+fGDZgoo47xdRiGLpK8eMTMm5cVmt'
        b'CS/8+c9tp29M/8fHYWGx/NK/jvzDqNhRmZDLnnVvc7/+n2T/5btr02tXfPiNdu3gFnX8lLPjAo+Gxim9qGzA6CZTgQLeRHUOoSLIIpgWt5VB+xgFrEknuz7huYhQBvii'
        b'Ok4H69ENwfBwCFaGCYA9QkJlMRdgozM+AkZeK5lODA8YIc+j/Qzgoxl4Gd0aTWPpTkXXpUJo2pR0WAdPw23RneJeDDomHi8KppJPnwHoDKqRwc0pLgHmMtxAMW8h2pZB'
        b'hxEd9OuUfObDKvp1AryO7tL+laF6l4Ajhq0CVtdjWfE2IQn5KncBB9aufHa09MuhwJblhIyunsbkd4KMBnQJZNYM6oIUXTL/NySfvfjS0gN2/sYDO5/QECXXIc4rNFsM'
        b'2g4vjAsWI+H0HWKB4/e8AYdiMO/afCNybb4RPXLzDUe3N/MfEQ/Qbgg1Taslqg3BOjdhQVAFXcz6kagrNF5A3ER8nzTTSQCyNcZV3dHXhfGOvgo55wqPOHNoitWIFcnI'
        b'pJk9OPW4OQg5cxK1mWTzcAhS9tRek85iNRnNExTqhSarTk38eoQYAdoIhXq2Jt8svNPk45faMiy9EBHKaHlmCsSpDFu/ecDQ6AIJx37+Sv38vTdffPfFt19sa2jf01jR'
        b'WDG+5k9bW/e3Hj2zp3XLqJqmLY31Q/YNaRhSNWTTENH9j1MlIM7Xu3BAkpKjSKREp7MEGiFJ9aAS58yCW+duuC1twnCBCDgJQI2fsE/aPrcwJTUJVqenoa049zYpqowm'
        b'zptACWtF8MKEuc+Oh74arTZLl23IMVO5lKKhvycaphAkXDOwC+R75nNgoFhAKHLAkWk/uRzwxEX35vFuyQyutBQXD+HLnR5w8WUPXHx8i/7r2DanJ2ybT61TGOGMAoQR'
        b'vzQ3tHOzS/3/D/FItqQF6QrBomQRDFBUL9AbjJp8hVaXr+vuTPd0KDfbflEI6NFQda4byv2hD0a6R6PcAwDi/LyLvMZhlCOceRY8P8rFluFZWOFCunHwBcEesBnLtgLK'
        b'wesqJ9btgZssI/HX5anoZngyqkN10Smwzol7BPEYiHXlqXCbJGAUPPjsuNdLsG0+Af0yKfp1EcCiumX972IgCZP/oAcMvOaBgU9s1GMOuGHswO2Am0dHL+eo2YB/mN0D'
        b'7lFApEhitBZkY3zDsOdmKO40v+ZYTSZM/PPL3HTp/4gT9MriqS/kKtkNcoZOZltLQyPlAqMeA5CpHPjiW6/7Y05ggKSCYAvcAm+6SYrwYqwDImWwWWAD11bgVBQipyxx'
        b'ACTcwFvIKg46gJrgdSwJKidFo7rwTnYQLThVT4XtEsUgdKLLiUU9QmBOodVocZswc08QmC3tCQK7ZVU5nQ8NjwY5xk3iOoYvv+sBxs74Pg7GulX7X4IxTOIfGh8JY52O'
        b'xk8NX4rQMCKEGYyKkrioMWE9kOEnwxviigR4a007ROCtZ2jLVnjCWz4DvpR7faqc6oA31IRuYMUENo/pqptgdf6aoHhcRCfQCXep42QsvLx0joWufN+wwk3CUXqdwAbb'
        b'4GUHwMVDuxjTy7ZRTwFx/mQcnwRwK4VwVF1mvmvOZ4U3Ev7jjz3A21EPeHtSrcq+XXcdS7KytIU5WVkdfJbVlN/hQ65ZzmWPDm/X/hGD1kTOiTLVk8t2ctkJHCbXDmmR'
        b'qbBIZ7KUdUidNky69tkhcVgLO2Sd9jdqSaAKC5WUKLGm2ES7+B+HM3Az/23BFyvr8PuWevMs8eJ0/bIDfFnqItLtygZ4D/AZ4DfAz1dK9wRmwTZRpxcEupoGm6Ow+opV'
        b'XxaEwo2i9TODPVZHCConAMeGdc/FWMHXt6O3Y1eGY5ZouOeHilmlJEwlMU3mkC0XJiORw9zkLhXmdZ6zZjrh6nEX0+d5fPmKde0F5xkrOTUY3YCV8KSwG9zbjwYxaHH2'
        b'y+nSkCyTwHovbytZr8bodgJt7OZvPBTWPsLluAd/47oSD9rm7aQQZIQczvjA8/TQzqi5T3DL94iORQrvbmCVq5ScsMcx0xsQvuMvXrBqiXV/EfXWvDhWAsjBvB8GiOXv'
        b'BW+YUwjyyTbqdfMnib4Ibs/996z+yvZVc7PODT676uaSTaEHVK/Ej1laF3E4/cLEUxNWDHwr7Hj2/0Y8TFvv82l/n/LbGS2hm2eMTf5MVTbto0HiENmA95dMz/zjlFsj'
        b'Ds2furB64K6w24OXTY9Oml/6W7/Wwm/GdHDbw+YXjR5wauynM3/UHsnY4j0mon3oa74bhn46s0T2pbmkKLTve7POeffzubn+31gDCI5aKKIuARPhrYWoJsll9F2EdhO7'
        b'ryEknzCOQWEc4LUH8Z064sd5tO8gvjcYNvcheWV7bXaw4JCzdEkQiJh0QQIU6kmfJvQBNPrn2mJy8mVkFDkB1hm+C9WnSNB22FSG9qKzqHoW3C0aDuDmEV6oEZ2CzbSw'
        b'LzgRkI6pFhGn36/nTxVqWJ4tBvLSTxjiHiwunyMEgrX+/SqZssCBDGB+PG6Yt7taZLbjF7vf/ufwuls+3Cj5DOWrfy8Oiu+/dMRErcj6ha/ymxGqxnxNYUi/31aVnkwI'
        b'y3g3O/v6K7mjv5g76K+9vUVh/UK+zVv46qKdsystSaWVf/lhxIr+5e+37+B/H9Dy+7D+fY2Wq+9+cPj01M83vMp8d+of34Sk2TS//P5W7pjiwoNL+2ZVVxwe9Y/qn/6X'
        b'O988omXRaSVPOcmUebA5xXVwsNQGNxHbrmaNEDZsx8xc4go0x7+nk7TJ8bwWx0m9+8rCI8nJpqHwNhlHEfBGN1mMOBu0wkrcoXlwRzjaGhYpWRlFvA6PseNRBbrW3S38'
        b'Pw3S674j3mTWeFiRSVfc2JWNpw50/sSCzPozClbKBJJDgy64qDHXwZPFeTcm9R/HDmZMF12kilTwYw8crVbh7gtDoqv4qNDZ8DAVrE1Hh6G9UwroDw/z8HwAvO1BaVyy'
        b'iFtIRTdK4wqp+ExUpudlHJmTyvT3dVCZuD9qlkhzl1Mqk9aH+ISDvCUpxCe8fs0Rgcq8tvIZqczkeyEPxoWsKQvXzJNKVgW+MfAvLJosHxMYf2NU5ZhflJekxQ9fH9p7'
        b'YmhG6dRrfFbAqaJLg7Ozfme4IhmacVKti09e9cDrm6TJ4T5985aYRI+iMkumJ8lpV+I1LJD70rPMU1cnWgSUvjo8APxroIq8nDRqrlFYWaNfvksUgSJdEHH7z+8/yuEE'
        b'nhggAUvGDyIbBCIujuklnPQ1FpFttDVwozTJY90Kbepl2D9xFGMmy3bh36LIX7b6LFmPYuT8vTPPtx3qtfnKe/fDW2IafpUhuxXA2q61jPMR3Rjy4t0zv2Omff3jidfe'
        b'nThpbPzRUvPasuePWf4ZsWXPln0LZuRq3yrI+GtL4b9KJkYc+DR48ZIg3eSCwT9s/u2qv7Z/2PozMzZ94P7JvkpG0KA3wYvwSEoCanaeBy5dweqy4TUPaezZfGe7YqBW'
        b'14mBwzwxcD3wI4vjgTSgVSDFQjnFSdOlThwUEKcTBZ85wFYn4pFSpZwzit8Gt9+H7nGraMgitCEbkyqKe2vh7qQ0J+apedg4H9702JlH/mjYyzyMjlUiIai8jTkGCMI1'
        b'suUsvee0PL7nGpjSUAtD0swEDcyKkOVsOV9Ogs+LqoCFJQciYHnS1yY6xmlFjUy5aDEwDiJh31fJTEXC8UL0Gzl6SCSEeTc+sJFjbRJoGST/TRtnasCpRI3kkKGL+E5M'
        b'D24gdYnLJVWMTUKC1GsldTiHTTwJFB/AtWyh+UUV5AgZzvQmOSQB90NUasStFdGw+CS/tFt+Kc7fgfPPpvmFQ30SXLlDXbkHPCp3A0NC5FeJhRz4HSbNuMyIxY4A/Y5j'
        b'e7JtQOvVjxAsYa1ZpsLkWacrmm0i9G7hQ5HVoo+Md50+g0G4hUw6+WgiJMpEBEKlxKQmoOmlM1oLdCZybMNU8iwm4di1ug55htFAbqiEKuSdKEBdZ1zGzmJpeHy6dYnE'
        b'NDGR8BsdzMpnjfokJ6ekmEcL+2NDCHxOoCRdSv08yVkfwokhAfQkB57uyAp2u5M7/kvpPnWpcAYmaozAHJ0ebB4XFqUkJ25vpY7zikE8ll93oAsefgeumNOkmzZglmqZ'
        b'BYCc9UQngKWHKZBNoXQQTbEu9GQ6GPMjdEYf2q0sS2FWfqExdyLnPP2TI9qIlR5WvR22+QlthNuiUbUQE5CIX2AEupUCK0VlcLvS43QelyPWGNpOLbOKMcmJmqHlbORE'
        b'JUbLHwPktB7calEQaGRsTF9AOB55Q3mb2NEH6iLBDi+l27W+YIXOiNboDfn5SraDMXYweY/qGOkP6Rft4HTSMZljwnh6OAv181qKDqKNRP3G/SHHX+PepTvOmR/hh+oH'
        b'4b5VBj1m2y7T47bdx58X2C16rqtIt22VnfvTvlhZBD7ETOuTcrW4bdoM4aVp7kt44kH86SS1clcvX8emoTUSIAcg1D9UHbEuLQ8YDkee480kbN6aYPSVegWNvnQVXqho'
        b'qri6/9eVQ945t6dxS2PFkIN3Es9UWJkcnxmyP04/rXpnemPIFlGqd7+tlYrjAyMGPhgrv/3S67XK1ICEgONDBwx7TTp6ZOVSeejNDeMrdUNyYrjcCeDGrpBtH8djMZWs'
        b'kc4zwia6yRedGevY5KtH++kSzajZgzuPzPOG59EdemYeOoC2CtJpXTi8Q4N3VKei+ggGpzk1FZ5n0cXhsIlyw2itPzyfTHRFVG2GV7F8uo4diq7Cg8++UbhXQaF2/Djh'
        b'TIosrSHXYOkaPdYRmUnKCOf0SJkBjOmeC63+r7YCk2JSemRz1z22AxNyNWM2vIh7XJcOW8fQuLrkUCByiqxjkOJZtBeeEa8LH9kzuSAmIIFIEG7XKBw1wqo6RBpzjsGA'
        b'm3UFuJhw98NiJXm60nyDviyDcxyJBTjqNjAT0gArNG4ZbokC3YTneaxLVLLopnpWzy0h+cjxK5QDBpLDikh7yh2to8jBqkwvCu2Y4taqxwTV8rIaHS3M7CRfREChJHY8'
        b'OoG2hqO6zobiZh9CNTyNZ3YY3bU99ZjlurXtsSPmlR03RjhcS+M2ZnT3w0GLLWV0bJJDiYMvoEoR8BvCTYS7Yv8fjhhun8BK9V1GjEaneWHRStJGQdqE54mHKLrIjYJ3'
        b'hno4orkOiiOMUMtgqo6FqNKhNsxiLYTqcxUsFiZAOSecKGVjMY1ni2XkFKeiOBtDznaizRepOobFjBodO2Zs3Lj48dOmz5g5a/acxKTklNQ0VfrcefMXLMxYtHjJ0kyB'
        b'BxDpVBASGCwPGEowDiv5DrGwSNEhysnTmMwdYhJ5IjZOYP3Srp2PjRMmp4BzHmhBuZ2YRooRNvWenL8qZXScU9eegm7hWerLTUCb0J6ep0nuABetcKQRBZVfuCgFY3r1'
        b'EYASGydMxGo3QCGEMBDtXEla4JiEZnSRzMJJLgZdQJVChK76MNgQrkqjscDWwRfIOTEQ6/EtmDK2PsZwz3oY7p8hZOCjzqBXOraENKN2TTiqXjsB1aZFRiWmiYHfYm6Z'
        b'UWrthb8aUPtgrE7ZsJy2DCyDlRMMX4d/zZvJGuDra09+pV4i2N+3DKm5Mb21YlRl695RlUmHhHNYlkWIvpKdd+zBn5ufim6gPeGRSbjjNdES4BXLwkZ0Z57gvdyGWfk5'
        b'EmkKU0cSnCktYtpqBvSO5tBudAwecTKJR8gMBnNhlsVQoDNbNAVFXaN7On85qdj0K9fUch1SmsPzxAZPO/kbzhpoPluPVH+Lu6WcGnjHTiigHaFyCR3TJFQbSaLZX0YH'
        b'TaL18IBmtofnmqcRk3N4rrmZMO2My4j5TLEfSEf9us18LxUNOYSaxqxPwQx7G6rlgTiEHcbK4MkkYQN4fF8QUbqCKNrLj/TOADQAYCDcCe/Ejoato+FmWwwYCiQqBh7M'
        b'GS4AUc2KgfjbtdHwAmbuPP4I9zLwWsIY6nSqgXXwnLDl3z8VRMFDSNjxHxvfD0hzc8gW/gFRsumCNPTO8FDQkH+SvJw+XL4CUDBUwwvLSLQ7MLHfFDARNSbSpNt5L/DJ'
        b'oiEkacSkKY7jup8fyoPERTRiQIQ6V4HnkXZ3PqwWo8NeKRgnI8SAH8DAtmRUTXMcHT0N3PMVMaBIPb9x5FqhmD0rpoCZif8km+AD0ntHO84Hz5SAROkAGqJAHjQWGErf'
        b'hSLz70hXFn04q+HF5JcS5Fv+rT19OG5R+to7r7zb541B5ewfYM2mXyiyG+1fzrq/vHn6j8d+kn5zcMLL1uHD+J9t/5ix/Ej/l31um4pTJz1/48HczLzoQa+E9638s+S7'
        b'lr2N4SGGN28Uzds5btC//7b/ambex9Wjb5fsT2z/7IdfK98q+uLQqzH25zJWTZj7evRV/4+uto7+W8a31aXVd/5Pe18CHkWZLVpbL+l0OgshJKwhEMgOCIoi+xIIgQQk'
        b'7GqbpDohpNMJ1R0IsYIianezKi4guIALCoiyigrinSrHda7LOBfv9OgsjjOKOuOCMyp3HN8556/qdENAnDfvvnnvu+Sja/v3/z/nP+f8Z1HfbqtYoM9SI3c9nXyP/+W3'
        b'Xlmw+K78tt3tX5YtHj33mZ+/Pv3jU/03vTdpS+Pe4se8ByZVZBT/5cDl3qK7/lT/zjenV+l9rCd+embLX7+zPfzZxOPH3sy3EgBP127Uw4TXtKD2tCnOyNUeo69l2pPD'
        b'YynEA8LUFfp92u7ZzH75dm2rdjDqOM2qbZzcAcSl9jxTortlvr4N3SCUTXPGqPNqO7QtRFwunqI9axg2FBe4GjvtGvSn9LvJpnpusrYWZ1bihKVL9If4cWjndtGh1P4Z'
        b'8tCkFti/PG5ARJdfNnQYoaDR56KgJIlnclGJd4lOoEqdgDgkPocXyLg4jSJKOg2jZOXNKLJi7j4ijrpmpdbjpniInTjrH/HSLShvcVysYxCs61bR1Aa+Me7vb9lno7hB'
        b'2nptf+G0ogJSzkZcd3To8KESN1DWd/KSdpe2LY0FTt+m7+42Z5yOeoX9uf767frNtaZxYZwOEh74hXgMgRkGNgwjF4aQ4bSoklKkWuC/BJu0JZNLh1Q9II0q7OBJu9fY'
        b'EUOiLJr51ogsnDGkEpWakLQD3qviTgFKZnSXVBHH9UajcVKIAYxJm854WhUK60EBEuNC6MZGpCVKpetdicLR7jXJAyvXnl3jbQaGhakGdRVCl5FHYsTS2tLiURTcDSIS'
        b'sczWiBTwtAWA7sAi/A3tnkiC34MaSwGMEbuiQQ4sUd7G9KLsOTdGLjTwP/D+F9Hl6oxty0OiuWGSVARXIqxJAb33MaOqI/qeunKM7l3J2Jd1Q1am4xbNc/30+yX9sHaf'
        b'/kQciRkdUpxXJDGJEuaAEs4kaR2GloZ53oGDjIEVRRxkkuUJSg3MrSBLkEJURQzOjcFIO0ScQyphEbyl0Nj4HVKLczjZQjSPteJM3uirx7U1eUsKxxGp2OCrH7M4Z/A1'
        b'eYuvhd/CfLwvKRh39bixRHmfwsaS+MqQbwEniKR4xOr3VCu1SyKWeqW5tSViQekRXLzNK2BeiIWQIiLUE7G1oJaX4otYYBwhg92s9kJkfAp6UITcbjPxAdE8rxAl0+8A'
        b'OUZkqEJi3GS6/lwhuSbUnkR3MVOcWriSEbrkMtLGQfO1LfqN2r4odRF3irmV5gIIeCGdQ5KecSJKGxrCKAPxdwe/E4hNVZCB5Fc5N5rICMpY/KUvk1UB3gptPVWUd6Z1'
        b'EH8D5Yk9YF54btn0+SxHSzTHZpbD11Pllc30bf3Z3wyPaFJFhHecEbKzaTpg9Git/oZAIFDd4MXjIo/X0wST4Fnu8V4A7iLOFsUTQDNNHOOfdA4tW9l4JmUlCwc8mUpn'
        b'zGb/9rGFedOL84nL1NYnac+zMea5/tqDljztudqu7aMxOnbnkTwgIm6R6JEoXCOHIRnvFJdal9oW2eEdhmnEdzaPbWmCbDOfMIwjIDG0jrYvcsg5BpmfKDtvTliUKA8w'
        b'npNkFzw7jRgHUtBeZ5GT5RTIkxT3LlVOg3eu6BtJ7ianw5vkuFTd5Qx4l0JW0dyiVHlgUKzjye45YVGanEtPfeV+8NRNHgR5rNCCbLk/PKdTRIXuhEYHRxKnwIx4fIGJ'
        b'wLVF15wpSJxjotROWT2FFuZkybxngRlg5jto1k99D//O8KOA8p7AdcZImx6d3hgQchNIUiBzf0t1redklA8T2nvHNKvk7ITnsIHUTtxIkUeH1clkBmQWJiifE04NVNd3'
        b'bRMWSWjxVjf43JAgEtOA7rENiKaIq1kwa07jmClas8uEQNMuTohY3Ij1CQrOY5OGUPK7Tha0PSW2ZswcNy3RSp00LQjicqcJonL6woNOlf2xs5txPExUdNwSnXHE8W0L'
        b'SMzNG6F/p+FpDQv1q4qy0Cgol8koZhBGc8sy4Y3UaPVnyhZVxCvgeR5PYuCNjeXK4My086F8DHltzJW94gw/JMIXnBFKhkAPyFkttkj5DCeJv/6M5fqCjlw/7q0sRLoD'
        b'OEUl4F/RAPvmeK7TToI8rc+gTC3nYzbdgF9g6/WQE/ePRVNVi3CKnYLI9AS80p4Vtwpj81REHVyKsSPX11yDNHIBdjwgUGBvgBcjeB1gRgxxD/1oBRoByQOfbKp7YeMj'
        b'juhKP8/RgfJ3+PmraHCE2Oz4VYMl/oMNrO9soPIdNsaGhVUDARPTQuV77rwkE4LGmbimdTu7aVDaOagmKiQJwWIKSUhmhGh9L4VlskGgtvJmWzFuuWqKUvFUwudvqm6B'
        b'FvK82Wwr89JvwELE5mFtuDhzZdgJub+LhpEpxyLJ8+1psf1gxXc9yENZN4RoN4RoN4TYbuCQ82ZgdewItT++Gw3ohihgDj7G9VNE/mLNriVIKUlx/Ug7qx+s/LjpiAqa'
        b'kPsJQTtDIvSjwMQISjbSHyzqeAf0BSlAhOGAYCwmUTXl3CLA9HhGDUgKahvR2SLrWaLbDTRUQ8DT5HabGGsK98NeGRUrGixI5pmSEbodllmPOGDtLLzrObo2dqmVXKhv'
        b'bJZ8BdEZLTVmFPY/mlHRmFHJTGscNUkVioU3iFNzbi1sGObjT+csw1j4o2Mhdo4FofCLm2obFJYqGdugOSouwUGW9fEjE63qAoE2Tel2lSlE7WrntLvdNc3NXre7l9S5'
        b'cabHV8YSGLR5VXQuTA4DZQfEr1IAea4OaVseqdd7YXfZImw011EpDMsHXJQyXAnIuMEXiCQjCS57ar3Vptl3xB5oZgfF5n6A2ZREHOssritBsFXxYBCeflIUZznPghGW'
        b'oPScxtNCyo42XqbFIgsbJGJ7eKbQQJsbEEhS7bARPjSkY3F8Igmetlpvq79huSeShHuYG/hHrNF/GtuXDR3z+cfk5NAxLMAHuvGJ2GAH8sK2YHYtBXuVij+/66prigs+'
        b'DZDMYwaSScRvFNimKOxjliincRJ+GoDDaFuK2wVpR1zLukVbhwRrHrjynXj4zWdxVwsdlg6ralGFRqsiE3xYsjDwj+CvYvf1PF5HG18AR1gRiS9zqVb2fplrPtdWBFAl'
        b'oVYG1NYXyrR12KF2q2qDGm2qHQdXtfXgILVKfIqtI0FNUE6ovH+/ilodCZBCHM35JDUBqRT/q6rgf1WGXkBayN1gyg7YATcC5xnLACSx8hMiToAJ4BcbvDJMd8QWaHbL'
        b'DbUBUm6g/QB2lACsq5pIAiZEAPITacm4nC85kuLQXuOobfb5mVlehJfxXAQKjfC1yhf4VaiVmeen6Wbm82ykGVBpnmS6uEJxE3GVzHtdiuDk0wXGCLFodxJ50ojfbI1O'
        b'EGmIpHACj2boQmlpPl+an3G26jD15lGzN8qn0c6d5hg/jWwyowyQ/qCdnoaG9hnCy4SGFDv+JPHGAqSOxESsuniZXmwoK2zN26IBb3bRLjktdsFpcUkuZ4qUIqVb061p'
        b'tnSHXYI3Fjoj1e9p1Q74MTbnhpnZl+kbCpdNL6qwcFnjpdJEPVyVz1PYlhXaeu2ZGDMonYI7zoTk+fpa/UYrd4lsrZqqb81nsVkWafdgiAAqVN+gPabfWchziasEfa9f'
        b'C8XpBCKyIJ0nVxRBqLyBz5i7iqbqRo9Jlgid6jNdnAIbczq1E82yHj5u1df6o425bxW0xaHdL+jrtEf1p+PYXRN1+au4GHY3hcLsoR46MLfARkrAqPLM5dciFqVdqBMN'
        b'xtaKjr8gjU12yklwtcsuOflmdBzG+pQacU5ubWpaabT1XAKZNhfU3GBcC2y5fAxLyXeylEykAL8iiRck41DEUqH8iTO2U+XPnMEZwO6IYEXcJlu3v6AhcyOp7osSTgR6'
        b'VvbubJ4IBVyVnVSSle8L/9u7x/bmx7qCUXL48+6aCUCZsIbMjc4n354RV100SdeEmXHiSWSHUacp0aQaS7tcRoziQizmdi+IqTrzrJ5GE3Vd+ViaQpkHzs+JmmZEIQKm'
        b'VwaGaBCQ/8ZmwQQLKONTLsEJjGnukqialIWRuzSBOGJEHMURg+cXwRG+WdxJ8dhJ3uYiaVtXXbookgf5Cda0C5A9Nrfb6/G53XLMGKafVSEl6FpagGUEuHqmQWDgAgn3'
        b'lPNTWfgVOhFT3zmrk1L8QO+QySi9QM8IcS+9QC2MmMMmO87ePBCIlIE4h7nRzWAQUb/RHcH+AxPaHxLNMCfULjqsdtEppiQAshfpxKJl6ER/PiJqbV+AkN5kfTsiap7r'
        b'qz0j6Vvq9W1d4zz0/2XivDvFpeJSaZHFw1TGUIAneaSlNiDWjKcgX8cTPrQvsjORG+BAhhMTSHTmoDVsj6RV1iz11AbI1Z0xRj9CPrSEbcm4t/6QdCgQnRKxvce5lV68'
        b'kKju4oVEKzv3movCQXUXhYNocXTErLC+XXTnfBjIblbtxfalBDiD7zL4Twk40EaHMpTpABMuElU6ecAGwlcLfJUNDWF+h5X4vUWQwtbJ82E5nZ2KOY+P4eTsxLPRCo84'
        b'yoAzaGO6sF+YEBBxTSBKsTVgaMlGOd8fg9pulKJSKQHIPBf9R/nU+cfMYCATz4bNfD6WkmMkXt94UL3IgKJYks/kve0So8CcIp1tTJ6irdUPVeprp88sQe24dTNmLjNp'
        b'E4DRiddrW7RHbQP66pu6htKeMVBKdAidCgJtYphKR3qZ/TYx0iT0yTmjubmxtSV6JGkxFku3KOAZW1UIptJgzAHHi1GEZGFEuxRY2eJRNuJtQlT8dp6N1OqlOjd2cozA'
        b'V+VcoHUlLEMX5npDou04B1SK4NM6E1QABWKIVX11tr47ZpC1vYHoEC/TN66SyopK9KdQpVbfVFKMbjeWOfRtiSVxp0lRGQgqj8HuzZFUozdBE4+80g7g0naShr5SFEKO'
        b'jwtZkZENcXRv2WkQHWe+m0SuSdCOuLbVH2huamj3yNle4F2z6Sxdyc7zBBSPB32ZNncu2vzz+1Gl5KPQ4QO5d0FD5IZ6X7MCdXQKRbOrfXI28szon6JalhtY4KjsAoPf'
        b'ycsvyGZcdrxxckwT4quo9nqbV/jJm4xSjUGf0KWqr9h0rpJtUOn++OIAmumkUVwwcwaADbLgkcSYOkjy8GNjnA2DWd8imcpxdubCi45xyR7l+QbgOXZkaev0/Rizj9cP'
        b'cPpB/TmBvtr1/UspWDt9E328vm/xbH2X/mDX0bevjQE4ufMMylpnodOvhEUiKTJZYfvDky87bI0SnXWJsk22I4sgJ8gOYAGsMSde9kU22iTtBGmuiNOAhpnA7CgVpXHu'
        b'S6IL8WEO9ZoaYIHJ/L1ihxQVzA0EPoBvQP1Grp6ngwfkHARlfVQYN1YVjC9AbGZxwD1IKAJQRb8P7+hZyoLSUfQA/WCiPaGttypMRi0BC+S0mKlIEBGYz5lC2qVCHXzZ'
        b'yEdFelaUjZcgzJLwrh/+ELnY+Y6dfUYcbpJJu2Fpsf0CCSTTjQUl/J7WS4viqWtoc6PSJLGAEcHnv3ifmk9IptmeIKACioDrBZ1dS+T0OoVC8TlJbhA90aKZ6GRoTMxg'
        b'42J0OQ7ihOCuCAuhXsIzfZQB8UC1dohtm1U8B1rLZEB4nu+/nORCEkl0+rb5AoIq4ak/OzCVbRtwqOeZMqIdkmyHnVelPLiEaEoAD1nXwFRTGRXw3gFI+05Mw74Y7wkb'
        b'oU3OGoG9mQ81zudUtkckVkQsc/BUKCJO8ckRqQJDe1vmVXtbPV1TZuzMECVYstBojTXhAOC+HGdpVAyC7kKllTxKvoEqCOTSszh+jGubfYBNAoSU/LHqIszRJxRJUt4o'
        b'bWFKoywo6SM8ZIie/BRBjwmjzjCsQruW6Pcsi1iaFdmjoBzT3+oNEC/R1CliupAWgyu+hbpkyFc43mnwUw5YUYKACrrpcN8bTdAcmXx7rwv0M+5MMSomxabUI+CNpdVz'
        b'WYcIdBbp+5BFVwmuMJK3izvZXDtUETZum+JAXRJ8i+/ms9MSOvYRUCgcscJ4eWCu7e46L+px+GjETAHpWBzZ8fgzgb8wyTUZvr/fyU1KxmEJeaY9C3KMis7ZU2lFhbjY'
        b'03JUzFaxF5l4XEUiD4CpnaicDd/YKQJ8DdCdCHfTAoCIVCEDduKbeNKzAJS1kydaFqAEYEJGeaYvxXyDafA8VbawO3gDI5rBRBHWCnZ6KrjdbH1lzPU1+ppX+Do30+yc'
        b'XH/OGev1uX48XLUq3XCwvsVMVobBlBEEBpxJwoqd5L1yGX8OQESS3D7USEJf1FDAJzikGTFLKsU4msjgrUIK394zfmhjs8ZhJhxfkqbJXOwBJq0YpFWQahHYXQMwGG2D'
        b'mN6RYZOHeAfzkL2galUlQvRFgOgldma1FLaBOijpfgHRvckpWZUy3lgaCjqlY/BHJzbAlKM7d6C2bTECJrspP1Z6INgmMIkx9CUGHLsW9k6H9N92UvwwRiKKdNNorM5B'
        b'3UbVYgWAQEKXnPjEaMOpC9PjafyLDBjbSfcPh/x7Oun+jO4p/YAxd5FqmXaTfnhAVApZqB+Yqe3TVuvr0YFb3x6Sdkzbph09x1k4/qNgs1EKJJkYb5PyYJ77TboDv5xN'
        b'cyCLYFAcpFuDIkkmUkmJ2Gc01zaWNng9FR+yqn47Lkp5xKk64JSEiCnHBeVPDwgyT6DHmGaBvtGBZgZKJCUVWEq3heSSVpJR2tCuzm03GEWp4kw3DKWbLTd7DJ/7SEOe'
        b'seX6S1BbD6eLjvitDX5MR3AVsVXX+FGpIGInjT65QYnYULG9uTUQsbibKOYMReiN2NyYAijoGF2HiIQplCq+KyYCF0OiJbqunEQepBGJYOXbU81hOle+iUjNYY4S+ndh'
        b'qp0o3EN7wbblK1NCCHKAhhA1z+d88wwj3OU8ICiea79cBbACFC4qY2/CfFZlGgkCWTl8o6RcHbDJAo42vLPLRjkyhwgOzSAWcstSgAWX2FjPgaf5Jh1mqTiVSvistrnV'
        b'K9NAV9eSt/9sHKAPt92D/3aPq8pPAM4OhpKGJ2JpaoTBVebQWVrlHOLOIxaPogDemY8vnVe1+jC58cXv9XhaDIwXscE2Q0XVnBeMIxLW3t1i6uCSZapAHhQc5ElGohlA'
        b'W+r2pOjYY56uLVuKOCY4UgbJtB5hNfLmmCuDYPwlc/wNHSDcEy3UFbY0LA3+aIctShPcG2KmLpjaVh82ZJAlRhCOZjntydGGshQXoqQYlShH5Vu8Und+QTg6GPIAHiuy'
        b'dMqDUmJWJH3semAKYmrDJWnIngUme6ajAxgYwxKaWiKR0zZlrjk0yrzOhnVhHOR2A7pFkeoQS1TTwE4UNUxdWkwjjWRx2sj4H0/4yZyf5i/DFPzh4DC1TDw85WN0t0Rq'
        b'UcRS620Gso+GzdBdkdyettoupMKAWgBiL4udMMfZUM3SoMSjgicr7a42CxoZrFGpxx800lcaL0ZiOxMS2SwGs2qXXA5XqhOltjYKzqA9rB2crR8CjnQHqR0vN+JuJy0V'
        b'Hdpm7fG4PcFmXGmDj4qBUEFcAn4zKgpCrcxFkpwSZDFqxKA1aK+zkng2AfaGVMahUpQZPKZKgH2CeUvDw6pY3rQ+Py0ilc6aXBqH8aJkxmQOhfQGcUDn+sgFmrMGV2hT'
        b'SFgqoQU1PVtkIWBlT8a+YBpxnUmctRIruiR7ea7/TBI8GAG44dEUJi6hKUVPny3V9Z6I0+8JuFuUZrm1Fgh7J+Z2z5ty1ZyyyopIIn4jl7CAoRLdbiNGtdvN1MndGArF'
        b'JNI6zxQvMIlY94TOVZ5GKrYA90lY7bl84vnky4xqEs6kzoFWZDdV+8hrJrqHQTQQ6FzPzN/E2VQj9ira/mlRjCC0p1Ez4j5XRBuD0r4EEymEYuYMYQ3dhasCE2ktFZRr'
        b'Q8CU4h2qnQNTKQIjCvv6GqakTvcdIpDrYg8O1aHpLez0O6xMj4OITF65KQSkomxZI2xK6ZCAzbWpgrlvzeau4hYwBqUOSe+fQHtOYxcdublzpsyakH0arcSY2mIbsP0O'
        b'oskjwooaYxlErLDjt7QGaLQiFrm1qcVPIibSb6QjzohlBeoeGFJLhsloPCmLULfk4m2wlXY8b7GYutVkY20lDwlIc6bRXpXOtyfS+LOGRRKmebzLPYGG2moF484xs1D8'
        b'qTWlSsmxM9LCM2ZoJypT8TQnSIiTnjWMt2hAEo0v3QPrA8S5iF9CfMACLKAlnUPFU3SLwZ57sWe7bO1IkG0dDiYe6Ei8jWv7O8x3IimpftnhBDLfmcV1JKkJystmWjUJ'
        b'ZhOFD/fKCR1Jvr707IDnZ+VE+GrWb8f6lwXi26M6VaA2M7lGTvktli07e3BZXMv7UJJLdaFLDzlJdTXa8E51sXrgPkd1wq8LjxkMzAFlyi7VhmXKYkcCtMLFWkE54Ttq'
        b'hbM68Tuqrsg21aImqQ7Y/xOW4m/iUqecusEK5TmUAKZCqZVqZXit4hTaU53Cmag6hTP9YTDjl69/Pecv40pJtHFGHDNmDE1dRHQD3uCrGHPIZ0f4iRHbpOZWpQHQDl+G'
        b'6ss+zwp3G7uszE9i2vwOUsD1Nvg8foaOmqqV+gafP9INH6pbA82Extw1gKUaI3Z8WdfsA1pWaW71yew4pBnXq1Tr8Xoj0oJZzf6INGNKaVVEWkj3FVMWVOUnszVO5/kS'
        b'FSCR2YzFH1gJtHAiNsC9xNNQvwSKZq1xYAK3F5rjMe6BhYUqLIoHWhGx1jBRSYKvtclNOZiisIT38NbTFqDXPxgZOpGpf5Ju9yKLwUdwRjxKJx3WpJDVB4s3yRwMOgz3'
        b'JOSuROhNkjkr5WBgJxlgh0paBHQxlZwjVKFdSuHi4YuOtHrTwTtyM9NlIcyhBVRAJG4Jd087il/WGN4/stCIhJetKp/B1B0l2YbYLGAx5J/WKFsskhSUSXUTzvScWK2g'
        b'6XT28Oa6K5gonlw5+FublL/gWiq8GKvy4pLsgUMKc+Nop6gCGiIlsuRydUAPGMNv2HDVmwI5VIc1rbh6d8n/IIMaMncTK9fejwYWmz78iq7st04RgEgFuf4CgpUK4JV/'
        b'zhlSNzQNkknhPCJCTyMuWtkNwIvXNnubFQOHs8JNDu0X8ftwvHHyq9F27oXW32QxxU/o7YlsClH4b2Bgo1giZVchcRZFwMoN5yftlvMGolce4o1qYuQAP9pVVKdEwAsl'
        b'jbFEJQIpNruU6UrPa0XUox0QMvyJLctETtC38dqdjf0H5aPWXXTPJ3U0saIC7dfx2C93epFpTZ+tPRm1ph+snUBFNZEVemu+vn8OenblmCHiA/paLICMerfOEgkybhvV'
        b'5v15YgI0tbRh7lWreP89QNUl1WyZWfXt/G716fe9crN88MBni//NcsRXNGH87aHw5NuWLHA+9eiY93wvbTu5aPHSffcdPvLKFZ/9wfZ3298qr//w91c2JQdf+1nH139q'
        b'vnHvO2sya0ZN/erw5PWfpB4o/+SFm+8OlxWndLw3aNfh0hmfjB720MjQwuI0/7MTPz1ZcGDqyNBzz47/9O0+Nc//Osf1UcayWQ+kBr/quWzBO+EBZ267fM/2F4Zdk1jz'
        b'xkujVt5zx2C130uTf/XZ+i+K3zhaNuPId7u6jdpaeuJPh9/d9dqHWT/b9uGCj2aNHDRnddB/+W/+uthXf8n7Qo8eLW8drzw18NLTB/OPZG+84upLPk2Z2+OVz94+fckT'
        b'k69+O/Gav1V4nvyqfMK8h6c9sPnORwou3f3a7Nv0uVc3PvrRe5WevDFV7z20q+gv2as/ebraO2Znt2cPTxnm6/X9sNKtm+sn9Bw5rJ/nwYLrPx3xbsWu96dNvOTxh7Ib'
        b'14/IuePgGyfeXvBvNb966cG6RdcOrq4ae+zL/TcLuQXf3nT/gM8+uXbA8o+rF36XPOyd2wf+/s4PVntfG/DLxM1P39K9QuEq6gd+NWLvpafnfNi8sHFIzb1//jgcHPTd'
        b'VV/9bVqGZ/yt/9kabr0zq35La+X9f3n9Y9v+W381O3hv1eivCmafOP3Va0rNig+emDFr5cuvfnbdfd2fOFrz6SXdT7X06NVk6/XSF3dPLQnXBP9rxOJTd49duN/f1/Mf'
        b'x96dbf16f8OjI6pbr/jjR4f29Pll0lVPb/r5Pbt+6fljn6Z91309t/4zz+j9w9o3dCx4cPt7E396sOPW4ldG/DL4n099mvdkzrOP5Tz06f67peWfv/xuqfbRk58/sXz2'
        b'kY+r9Wsu3fKH3w27f8GqyOdbdu+rfkN579Zj8pH/uny/WvL+stCjb40ZXvnzj9Z+te/3Ly//6PT73183t/zxv9SqaX/acU/O148+88mUhWe+vuroB/kjP88fO3zb4fB3'
        b'PYrnXnHdyTe+uOU994uve+f0veP7NPcvl1o3vHR9+/rh77zzb/ecGN732XdXzBi98O+fbber6pobj7kCz7zlWf7JF/mrP/zmry/86Wcf/axh82cn2tuWvb+q5b28D51X'
        b'Nv72ytNJL86oGrnn/rnqpi3r//Lzdzc0FjfsfvNL8dq3vpxeuOHO9n2X/6mhtnL4yU1tM3/V+Meyqd1HHPp+73Xz6ivvqH7qD1vfnV1/w6G/T1g+63f7Xn+56LMPBv/N'
        b'W7850d/Ov/RJacOzG7avK5jq5u56/rdJw597a/uGGXeG576w75Izv3Yt/PDJtvKf/uox8cVPnjpZcu23xx8/+Np/3fvuU1Urn3v+d33u+ixw5PYjB775zfzTf9se9P/2'
        b'4Ztu4Breeeo3E9/MT6IAMNreCRijmDm3qtTWartmlBXDZZON666vFvXD+pphzM3m3mu0HZgQmMmyInTWvGmqvs/GpWrHRe0O/X79RrI1L3cMRJelZdr6IdOK9HCGtpHj'
        b'0rRbRe2wU3+YQjHpN+ZpO8nnbUVxAUaLCWr36EcE7e5+2l7mWvoJdZRf29cZKXsBb8bK1o/7mbfzG9v0Rwyxp29ZnHrpfP12FvTvuPaMdjc7q01AS+tiC3rWT9aeF93a'
        b'Cf1EAH109dMfL4ZmkCEolqVt9DHv50YfmccvdpyvjnJI+tP6bZRReyC1rFPsuqxsZnmRviF/GWTT9mj3xusB3FDuwDg3R8nR+kTtkaoLKWpMnoN6GuKVAVTW1LbpBwf7'
        b'Syg20aZWTPaQvjqqcHCWusEKfVuC9tQ0/ThNV2W9dku8XPjAlBix8AL9aTL8L8lJjNksbpP767cJQPv9mJ3pB/atkf/Ewv5/+cnPYbTD/xM/psTL21wtu93kmeF9+OGq'
        b'reTR4OL/HKIrwSU54S/dkWLP6JaeLvB5swS+Z4bADyy2CoMmZma5LJnjJUHgM/nLvHnLnbzdjk+DUgU+B/73zRb4dCv8t/d0CHyaJPAZ1s6rK4Hdp8E1pzfKfjOc8D8Z'
        b'79JT+vKOZicyAEKKpWdOOu/sncI7bE7eKeL3vi47XHvzzsXwe6nAZ/POCuXxqBhOiHEX8T8LuoufTqIfB+06ziSmH2w723VprnZvRXS/6Y5qVGHcbFxZYh8tpAcblg2Y'
        b'KvhzYJlN/0Ys3vzKVb8an3Jr/eEFv/7iRC/ni3WX1nWTj32Qpfzu3o9zui98NmXjZcGte244c/fU/b/JDo6e3jdvX8Ije749cWre0fZdX829feMHv3vz5off2Tbk5o37'
        b'iwK3WHYO7u3oqJ6zNfXX2z4/lnZyxjfFf5iwqN8jd+W++9DNn7/1yI0Hn1z4+pyNYrdZfz/04MRrwskz958s9Nz0yKKnx61avGdku9aS3+ffW24vr62a4a8a8RPt+jOT'
        b'cl3Xpt817aclb/z76C8f+8Xcqmsvr7zhgY7Iwk8eiNQNL2z6srzPK1u+eXnRPO/Urb8ffuyN11ZlF7VMOpnT79VF71+5vbC8pH7mKOWNRVO8Bc8VLrt094GTr5Z+kvbe'
        b'oZMpVz51Mv3KIyfTfnX05N3drqy69PTM4PF9G59d5zy65fVFB2p772ntfmz5n/s+sOCv3y5asMn2ym2fvFLS444x93/01Qcb2u5c//S2T/25V/y213ffX/ai6ln5cvFr'
        b'CZuKHlV9K1+45rXaPydu/6JMefXEvqbwAwe+Pvmh+odXj/tG3PHK8JMlLxzc3PjS6Q8239XxZDd3lZL7zvHt735e9MwfNr770yLH7mMtN1xRmfxwW9317+07/sjRZ34z'
        b'fcPn9y07uu2luuMrK5/7MHnx1D0vbt/0iy1tH5/+qJt74gR9deH3t9n6ZUkv5wRHO/IeXN+nataUpNYRb05ObAq8OSW5wzn0hZK/DtXGuoa+2H/Q1vftL13+k/zXWzZm'
        b'lQx9KfeJlg293s154b3fj0la8s22a74tv6F4zolvHj7x2LufjLul2zuaKzd/DKNMtmqbBhtLar2+TjukhYqMRXWVOEx7VDvKXGRtU7TN8QSMDSgAg37ZNZ18gPcHguew'
        b'vm7k8LjwlVXJFEAF3jyaVKg9UWTlePQcvpq/TntAP8zoqGfz+MLy4gLgox4HegaoFopzub5cX2fj+s+xpBXpewJ0Yrtdv6UE/ZWjt/KD2n3neCzXjkGDiQ56slY/Xg4p'
        b'9fX5+k59DRJDhVYueaTYuFLfTR4nh2v3ZwMptfmqIdP0DdDYabx2KJ0F7NMezNAeLNc35gmcfp++WvDxY1u1u2jTr7JMKkQ/6JUWzjpe371KcDV5KY9+25xRRJnlFfOc'
        b'tc2zShimr24jqk17XLtVf6Acv+aXabf3B0LCrj0vaMEr9DsCKDPQn8pYDJRfEQZJfkhQ+XHFpVTZzBlLtL36Wnh/xQpBO8RXaQcvodGcWT8yxn2Wvvk6waE/rm9iDblT'
        b'X3cteS7kOI92r9DBl2rPlbBIyk/3StXXVZbwQIONF7S1/NRK/XGaAnX2aKgpBHRYwTT9bug60ldIVOWOsOh3NkzWtupHAoiCrlL1zdqmHolAf5YXO/L0tdqTGG60p/ac'
        b'pG3zDA30x/7uysOIodoJ7eYibGMhOiErBxqzxxLpEu1m7QQ1RntOPzhNX4fBEjMnCNpWaOaDS6h3A/XdsPr10BAbp+2cLGiP8fP1u/W9NCRl1+u3YKhYmDF9bUC4gR8/'
        b'KJXcPM1ptpYTXoTZmbSSWPHVgv7IpF7MzdPh2Tdo6yori8tw9mZauIJxaVeK0OXnfUR6NyRCC1nw10ptR1kFzJSVc60SJ8OKfo7maHB6Daxtbc0QWMBzOP0h7cTV1Fh1'
        b'mbaxEDq7LTak66hrqE3Xa7dUwqc1wBPsZi49pBpeOzG8Nw2AR9veWF6cPx0yWecs1PcKGVfrxxiJvkM/oO9iy7cMCFdtJyyZRG2roD/Wpm+lBrdnQOPXxejTStyYgWna'
        b'GlG/cfHV1GVB39JcXoYeeNfqW43GufS1YsXIXrRO6vQNPctL9ZspIKwk8QCOt2hPELhP0e7RdrGIADNhqPPLJG6hvjlNv0PUntU26/eyVX3iylWFZdq+vPws/fEh02GR'
        b'JusPidqNAL23Uf/6L0ZXv3f3L5xWBuDVk9d2akcuJUzhAtC9R183awCC/Cb4OJsHyA3m0kAvKM8v1G7SDk23cHw5p2/Vtk9jg/Ksfod+DBY2rikM5vCUdwaMiiro9+o7'
        b'K5irr/v0fVZ9XYu2msXDlFJ4bZt2RHuSvjYAiNxXDszOpfoO/fHhPGfTNwuwaNZS4N5Kbbc1xsumhbM3oY/NkfqDNJqAGTdot3a6uLRww0vJw+X1vQgu9L366nnl5Im5'
        b'SLtXO2wAp0vbIU7StvSiOctM1O7vdCm6alqn69N8/QANfGBgw1luRyWAE+0Wcjt6nf5MYBg2ZXeu9ggik2IAkQIYCADVzbDMntNXz5xBY7O+vFjbI3Eztb02ffXgWdRA'
        b'7bgempQ4bBZyli2Yu7wMFlW6fq+o79IOumgMSuZeRiisZNrMan01oIlE/UFBP1qrr6EZd2qbryY/u7AH6Ee0HSUIZIcE/VCjdoh54t3LLSrUN87QN5UX5RfDBHbTQt36'
        b'ijBvG7Q1hBrGa+u1deU9MxEQoaPhsqLpQ8jtYxFn0e/RHp5Dw1A7wgewuEd7mPalDZX5wIzB8MOek5EridJ1rLLH9PVJ6Ia5shI3C+1wS7kN2nMQgEScTF0WF2rbtX1Z'
        b'MOXQpuUkpQOe0cZl6YekhWPrqRT9Vu3ovPLKYgA4KAjj4Lh6puqwre1cpG1i6/ywdj+N913aQ8aeJBXzMEFh7Q6KG91Wa9V3agdwexzCdjHawbC5vQZKAP2HmBdKbYu+'
        b'Tbu5vGxmwUwbZ5VgXT4s2PVntEdZQw7CVrOVPPZid3ntsWIYXv0RWB2z5lyEl2CDYfy/z/P8y/1ED4uJ/9oBP1yiINj5s/8cwN0wPRf0hCfxmMbFvhhHIAYvxjQBBYdx'
        b'B/kEjLVkp4gH6XFlOqk8TINnkk4yebbTOaVTsIptN3Dn/l1h5ZkInCkxoEqH3xNobXG7Oxkp8xxhHx/bPzylZazD184Y1oG+RXUWsAx0V4JaA/4X4LeGk/ml8BeeF5qH'
        b'OmThwXAV4CrAVYRrBlwluM4NzWvg4OoIzUMjwHA/TL8UU/JBPjjP1Hrr4FDjzSs2SeHkJksH32TtEJpsHXgqaJMTvPamhA6J7h1eR1Nih4XuE73OpqQOK907va6m5A4b'
        b'njkGUqD07nBNhWs3uKbBtS9cu8EVDZOtcO2vcqFkuCar5OwnnKiiU1o+nALp0uGaBtfucHXBNQOuuaiIDVebKoVzZFu4hyyGM+WkcJbsCveSk8O95ZRwHzm1wy6ndSTI'
        b'3cI9VVHmQlmo7B0eIKeH8+Xu4RI5I1wp9wjPlDPDs+Ss8FS5Z7hM7hUukHuHi+Q+4UK5bzhP7hculbPDl8j9w6PknPBYeUB4nDwwfLmcGx4hDwpfKg8Oj5HzwuPl/PBl'
        b'ckF4tFwYHikXha+Ui8NXyCXh4fKQ8DB5aLhcHhYeIl8Sni4PD8+RR4SnyZeGp8iXhSfII8PF8uXh2fIV4avkUeGKkGMNFx4oXxmeGOgBd6ny6PAMeUx4kjw2XCWPCw+V'
        b'+fBk1QZfskOCalcT6nCU0oOuYI9gv+DMOkkeL0+A+XOojrCTtFQ63cC6gsnB9GAGpMwMZgV7BnsF+0Ke/sHBwZLgkODQ4ITglGBpcFpwerA8OCdYFZwL66G/PDFanj3k'
        b'CtlD+WuEcEKQBUhn5Tqp5JRgajAt2N0ovQ+UnRPMDQ4K5gcLgkXBS4LDgyOClwYvC44MXh68IjgqeGVwdHBMcGxwXHB8cGJwMtRcFpwRrIQ6S+RJ0TotUKeF6rRCfawm'
        b'LH9QsBByTA2W1SXKk6Opk4Ii+eRPgnRpwW5Ga7KDA6Elg6Elk6CGiuAs4KGnmHk6EkMuNZFqGER5E6GWJBrPTBih3pB7AOXPg/yFweLgMGhvKZUzO3hVXZZcGq1dhLaK'
        b'VJK0yoHz2OEM5YacoYKQU3WGytYIa1CzAN8U0Zsi9maVU00krY2pzPk/KfMzQ3PEEF3roOEOy2ymQlxjgtIzgA5AuKW8qbttKOSd6Z7rz8vPbmDqoNXZNa0N3kCDL19Q'
        b'rkOskxOz7ZzPWZW7zkeiL1Q0e9ASdeeBZ8bKk6YJSr4EKK7eE6hT0OjB7mmrJV0ZMjfHk/DmuojT1BUiHSEeXZE0AU6EOwd6wm5qUTx+PzyJ3uZ6NEpGPTLlGIfBvPAH'
        b'az2FjTvVhj8Yo+8UDgkpQzfLHsCs5A0CVcgjYktzS8QBpcueumo0S7DXudlxK/MB1OktIoqNI9Y6KieSWNvsrlbqKSQmxvJ0N65o9nlXRl854JWPFRZxwr0/UG141LTD'
        b'U523ut4fscEdFZZANz5/wE9fSfGdalherXQ+oHYtPlE+unHRW8VPeg6+ZirHC1NYXcMyKB7PcvR3jg+oxkAPllqvp1qJWCnEyrCIWNNQT0rj6JWGRcOIODB4Mrtnuj2H'
        b'jUkOKNW1Hoyt6HZD8ho3m0gb3KFeQkRyK566iMstN/ira7wed2117RKmEAwLQ2au0pC+PyPk5ceFwMMvyGFRRBA091tjuLBHt07obrWDb8sgd5AucijJA9YHbndZ7/nM'
        b'x9aSqGXvOaahP+SqCRfn36KqZUQHOMxFG20j6pBZzTa+AF9CNsBxTgCrLGyHygP2EerQTKKvTMFtyHhCDGWTbpekSiFHo125KeTssKhCKLFRUKbBvdWXR0+ccm3Imch1'
        b'WEIc0wULOUJp8MUFfXf2wLGwhmzw3GeNoFpD3aFGwfe4Kiib4V3fUEYdOrS5G3W6oJ5uUM8TlDoTcvfG0nw3wvt+oVRK93EoFTCOrS2bbMsyO+yQ1hZKh7QS7BMw2mvQ'
        b'iOVFGFcJ9g+eyrQ22m/jlZKQFXImtJVQ6b0gpekCxwGlGLnVBLhz4B2FBLJDOQlzODYOIZ7KuRVyJ4eSEg0rN1UMpdDXpEx0xQtMnsypifhNFQDjJvXgmPEVuRJNYFEC'
        b'ojpzNK5Q5i6YD0eoJ9Qv4PiolnQ0QMlk4wHfT1Cbe5gjosZ7pHD+bx1S9P8XkCv/KNEzrmwrrGZ/BaFoF6NViVpFxR6rYCeVnzT0XSoy9SAn0cKZRM9a+Qy+Jy+JLsEl'
        b'pPC9MZ/ogHcANUIUYFKNHYgA5heCATAumOZ8A2DSYwEGvoo4cSEJdqmhcSCEE1cIeSS6w8VvUSX/pxQ13hrCvwyYcBHV71SbcpNqI1sauwq1sYUDINNzNOdbEuoVGhAa'
        b'BICQVWeBZfyymgDLd1aHI4SKaw4oN1F1hHoBaP4nLLvkRC4LN2YR7l14rzoJ+KAkNRFIxGRj+SZiCvZNdYzmlt09n/P5QgNDSaFeMh8aAP8Hwf9+obw6PpSKNYX6IYil'
        b'A5EJ73uG+FBKKAWJswYbAbkFFzGAU6pqhx4lwYKHqwqgEXJlch2uUBqQBPjG1YMDsEkiUiERchVRxK42KgHu66DXG/kOi+9TeGMNFUCZyWpyKJO+A2KA9iaHsukp23ga'
        b'SE8Djadceso1nvrSU1/jqafZTnrqRU+9jKcB9DTAeBpET4OMp9701Nt4yqGnHOOpDz31MZ7601N/46lfdNzwKYuesvCpLhk2iWIk8FVuI6JPRALQ19DgUBL0OEVNuU3w'
        b'71El+rXhL62XHrheoAwY+zr05G30pgeHVn4wnt1wnUGpInlokHDkEYnT+0JVwveqZBrpR/WF8lP/j8Btfsm/AO7478dP4xA/3dSJn1D1ULAbjqqtoovFTZMEnv1ZKTwN'
        b'mhanQ8p0qxktGR1cp0hocIzut5xCmugArOXiz/eXJjjFFD5NxJjKPUWniDx9FKeZRlmE05jfScBawC6H7AZOs4a4GJwmhiy0mQOxEkoAQh9wGVPkjiNYuqRP/gmhAmgY'
        b'91lNK302jCIORFyHEswOPYYdkgAokOoQAA2nsU6sIb1NZRDqlIdS0MkmvZdUSgndSwphkBAEpGRASkmIpvEJtdNDjk2DeCw1MZSGQIcDRQhLtABKDSWMBOJvdIxeOiA3'
        b'QJOAzBH08D4FcpCeNcYIorxcnB+Xrgev23/vWj1ujbGlkgQ0SJJsDr63iKY4bBU5OleRI3bQUUMRSEcUasA6iQ66ZAx6Hg16dyC8RH8RfcHnDHwmH/aTYWU50SKXvjk2'
        b'9aRhQ0t1WyYZB+BT3AAD0Raywb4FJCnsF3Wq6F9rktM8li4BeQj7Z1upalEiGP8RsSXsTBbYRWAKO2wrHShWIGO6dIkLcI0O5WfMXw2LY0l5MrEM3AuJ0XYB098tmB7s'
        b'UWczosvYO2sCshGgBNrSM5SE78z8bGcDmiEBIIra2jZatcBVjtaQgIINyjsP8sI7+JIQzRttB5ChBfNNIyax4hxbmqg73GjEROQ7oMswyBSfAX04YEAcdBzZXIS0J5nh'
        b'L+n0VCVGhECNoiGn+Br/o/1pRFwNfndzTZ17hYLa1IrdFjV0kUjh2sG4EWDBkR3/hwJxZP0rIfd3rYb1kgkwKfDrJDSPWuZpgMatkkR2/agOg2aJyJJZE1xipg3fptlc'
        b'hqg2jc/PZPIFUvsdz5HDgZV+ZT++O4A/B/HnELkoqEUHOn7lMOn1t3sbapQjdNtUHViiPEXm0HDjqcZgCcpRslZpkJU+VCjw3hGxuga49iXVfjSajtgMF1ARm9+8qfc2'
        b'1wDHn5/0zxmy/Pn/AjL1//n5Rw4hcE1iJCp/BNe5IEhnH0C4LJl0ZIDHA+ceULA/qYs/Z5dv//E/q/E/+mx1imk2SZxxKUCgWLcUf7Odkji0N96NnoRwKditxB4KAvWz'
        b'Au1gHuIoXoI7Vn7ndhsQ2VTdAmAZUBQ/z4xqyTkAO/t4kuBuSlutpwV9JCm4k+JJSG11q9/jdkfS3W5/awvJ/VBIhpYm8DbR3fmgvBPv4yHGAnV0U7Pc6vWMpSMQ1BWV'
        b'BKAIBSCEujqPuYHrZrzPEciBramT978AsTwV2w=='
    ))))
