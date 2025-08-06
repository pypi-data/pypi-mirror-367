
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
        b'eJzcvQdYlEf+OD5v2QIsRUQEbKtRw7JLEewVa+igWLGwC7vAKi6wBYEsigIuTcHeC8YCVrBjjTOpl+SSS3J3huTuZ8olMab+LpdLvLvkNzPv7rI0Nbnv9/k/zx+efffd'
        b'ead8ZubT5zPzfgy6/LnjTzT+mDbgixakAS2TxmjZw6yO0/E6ppxtZNJE2SBNrOW0fAXQSLQirRh/S0u8zBKztByUMwxYBAzRPNC5FZcwIM2dASXBWonOPd1DK8VXGb33'
        b'pFcvnfsGZhFYArSSNPel7gZ34TsCROCUVOCWrXB7ONB9fo5OnlJszskzyOfoDWZdZo48X5O5SpOtc1dw9yUY0PtSfDGy+NLOhGUyLv3h8Edi/zaNxxcbyGK0uEcV0lKm'
        b'CpSDUrbE18qUY5itbDlgwFpmLZvqco8hARiSLAWXlOk6UGL8GYc/fUnFPB2sVKCQJ7WDv5PH83MJSBPUPJBKFWIQrZYtW8GCz4Sy305rBj1CSSubTKBkbcDGZXFOSJkn'
        b'hjSnK6SOBjpDyidZwvA9PDNvUWoo2oka5qMq1UJUhWrhNv/wuTHzY0LQJlSnQNWojgOzFojRudl5+nM3WnmTkpSLv/dA/YU6N+tLdbBOtTVEE6P5Uv06OzDDLzMnK5c9'
        b'vyFw/FKwYYfEErZBwZqH4hJDYTnc4TGDwdUqSaWJltAQVBPOgiHwAo/OzelnHoRzsXDPMlgL61F9PM4CN8F6CfDSxvpyg2FjnpGMqYJrZ4MVRjcy4/RCEh/6TM4y5pXo'
        b'DPIsAUOmtntpTCad0ZyeYdHnmvUGghwmMmkgUMZ4MUYPR9Fmrp3Pshgy2yXp6UaLIT293SM9PTNXpzFY8tPTFZxLS+TSzBg9yT0hFFpJEKl4IKn4cx9WzLCMmF7Zf7Ms'
        b'nhgG/Ex+WYaTMTvojS7Fq8KSQkNgdbLL8EbCa0AVJULNJf65pI1kz1eZ10Wfy73zn2f+tTg8qxpQbFrra17xrfhzH6Ben3Ew4sR4Ozbdm0afVsWtZN5lpzBArp708lit'
        b'UCQ7lwV8wGg862rV06IiIbFmrQTIAp4hOVWmwIXAEkqAq3Tv5wGbVBigKlSfGjGPoAK6Pix8bnBYaDCqCg+JTWTAsqXShGVop4KxkCn1gacYD9yb+FD3YFQDz8EmHqDa'
        b'fkHwJg/3wqvopGUwzhU+CW2GtagZX+vDca/J9EqARzKLtqJdI2iWfLTXvduswy3RZNr3LFNwFn+cSeqJnosPVcQlioA4lZ2Edvuj3eiIhYw/M4qNt8I9dEhjY0NZ4AF3'
        b's6gJnnaj1S8NQLdRbTKqiUtMQ1vCUHUCPMUDX1jOoTJtPq5+ABmA2nnobHysKjaUYqcIeOWiC6iGSwr0svTHz9FpVD2MPBfBG+ga4HkGHloHbbQBdHPlYAGpEwtksWiT'
        b'IhZXj7Zx8BpaD0/h0SL4gbajergxPjIKZ1i7JB5tTo4VAe+h3CS0fgzOQmAYuciNPI/1RIcShede6Cw3CjbDapxjCM6hCkStHjF4lvLx7NTFk776of0cPGJGx9GtZ3Ff'
        b'CBUhmwcem1rceJ0qCW2OVYWJ8ZBcYNEFuM+djtjMSei2Em1OwCM+c5RKERonAn0Hc2gbmE1nFu0rgNXxyaGxSjyk1bGquPCwmESxKBiogAjtGQLLKLjZsMUb1YYEoTol'
        b'fhzGAA90hEVX4CW036IgQ9pcoosncCpjcXdSguMxxW9GdRi9UkLFYCYvRoeCURncq7U8RXI35MGNOHd1csLc4JgEtDkpIQueTV5A8qomimY/gw534musKwc+Slm7jcGM'
        b'k7PxNpFNbJPYpDY3m7vNwyazedq8bN42H1sfm6+tr83P1s/mb+tvC7AF2oJsA2wDbYNsg21DbHLbUNsw21O24bYRtpG2p23BNoUtxKa0qWyhtjBbuC3CNsoWaYuyjbaN'
        b'sY3NGmdnzqCKx8yZwcwZUObMUIaMWXKqy72dOVd0Zc7edg7SmTlXJgkMoyIb3eyBYfjDRk5gGNMmUPyDlzSUfsKTQhWhsIqQj6+a80PN8CxqKRTQ9wq6DdtQLUY+DkTA'
        b'Hew6Jhra5JZA8uwUPIFqlLBZFQNvBokADysYVG6ELZTunkHPwRrlsysVoagKY6QYnmSVkwcLBfczyEamTBUGG9MZwMcy8CY6Ditok3BHFKyJx9QWBveiw/ipGwOPrehn'
        b'CSAlyzAubka14TFo05J4DvAxDLwAzwy0kIEoXTpLGaZgATwPq1h4mUkLk1KkhTfgbriFYNQNeBITqhiIc9lgdBVdFqA5gmzQFo9qEGYks9Nwg08x8AwHT9JuoM1TSP8x'
        b'MjJg8GIWbmYSFqGLFNAgeAruj0dVUyj2qRggHsv2n59OAYXNfnC/Et2EzXGY3pJx/6NZr/6wmRZcsxxdxALzyjhca3AoLlfEjoIXBlr6kfbO4qE5hMk8mAXGKNbATJ0M'
        b'K4Vx2eYJ9+OuxzFY/KJrLNzNzClG9ZSkkC1yCO4gPJSG55pQtxTeZqENnYAbhFqvYKLG3UhUATArhLUy09C+ARY//CRLLYKnUA1OX46pEF5g5mezQsfbgH982NOEEaA6'
        b'HoiDWHdUNpQ+WgbLC1BtDDyDgaqDz7GlzBy0JZA2VIR2+GGeiYkatoxlYQ3zzHh4xCLHT6LgdTzktSpSnTIsFo9KEtwBd4tA/xw+0h2dpf3IMaDWeCVsQeVEMMQRpHMT'
        b's3AHKnfPZF3wn6B8Z80H6z02xqn5sFVYvynlMHGxlLg4SlDsWi7V5d5OXNlPpvlwSfrrzAesaSpOsH4NHqh/l/G5uir7c/zNv10XvdctJorRZ8k9X1ii8li8fvLOyrrB'
        b'v6+TDYr+Kath4mWvjWrx7/3BuyKvfa++rJBQzWYerOknSC+0KVmBNsVSATbJH/iP4Dk8d2fMZNjQLVSJKoR88EKEi6AjUu6o1jwCZ0qCl+dTQlYlokt5mFVWd+QbArfw'
        b'aAvaGGMmgkBW8BQ6D3eRzMkYaeFmksUdNeCZx1N5mipTcLcVttIcsG0NpcNq2iDHDR08z0xQMS8dnVCGxhCpBqToIjsQy+0K9XAz4T6oGm7AyEagEQQFERMCKCNCRGgz'
        b'kxynsWtkXXQkmko1pHZ+tca0iupeXmQ21koZ4d+LcWeMvo68Cr6d05rM7ZzJmGkkGY2ELyrYjirxPZlFo5+jZlp4HXDoXuWP0L0IGadg0t5MyAZrIdueEQNehVnDUrij'
        b'dzV8ooCMbBb7G5TwbnzegevdUHFQA+RMw3BC6sPjD9TLnn/rTsOLd+80vHSxYUufV7yy7uUy354D0QtEAVGHsCJN5mwg2rEy3lOnCsasM57BDOIUW6xDR+iM+8KjhV0U'
        b'KXhVQVFs6kxhqNme58li1ud26MjrgNSHMfYDHToyl5exsuepwRpxf+eskCJVpBoilkAZeOj16HnJcYdHlVTjwuh2AbNsIwNvox2FneaFsX9SHfBZBUOHSRJ6EODsS0eH'
        b'vAx56XkZWRZTpsaszzPUkaKU8bBUNZmG1blTGCfoWCXHKUOTklQUinrMo2wcUMILIrSXQ5efAJCKRwLi5oBC1+ACAxme/nA3Oo95rNA6pkBfVM6lwX1YhF5F9b1jJmFc'
        b'WNMhRiKXxf8G7OxmzDKgJ0Yp6pzJwaqHOGGgrNrGO2H4Ncy6m5lKYHDviUIOrbKwpgQCQMKqU76fq79Uv6L9XJ0G774c8Huf15+HKTDl/vOvpLyGPyP+cGcZeuv1xa+l'
        b'oLf47Zte47UxTM2fR31SMD2HkycwX3yYy4A5E72jK2YqGDMhOlT9FLptgmdikrCNQ6efg3XoKuiDGjjYAq/D6wpG4D98Vx7XhYBE6ZmaXIGCZAIF+bOMD+ZzUqYkyJSj'
        b'zzKn64zGPGPY5Nw8nNM0NYwWcLA/XmPMNrWLV60h3y501s38ZI2E3xkHOSmOSNudLhT3pW/vFEfUZXgZtvXFqj+qSlBi+6QBa5bUEEdb4QU8BNXJSVjzgJfRNlgrmTcB'
        b'wJppbuiK3EM/5N7fGBMhHX1o8qrsnOzc7KTMpM/3aRI0Kz9s0n2uPqn5XJ2b5Z5173UAdK3ic59eEPr2hOPn4TJGrnyon4/YOMSZVdbTmBh9nINBcm53GYyvHzEYZP7h'
        b'QaxTXnKMBhkJGUudEgPgNR429UVXeyfDbt6k/1I8sN2Qn0+ar88+o+dMRBxn/LwzXkMUlRgN/13z1jqFfGzf3dqv1VIiI0D2P8T785CCp1JgmjyXSv0kVWgSkQGobqQE'
        b'9IEXObhZVGAm1j7auNSPSnZs2wfHhYbBzcl4DOqVT6MLsfBMsKAnLE6XZsED6KCZWGfZQ1MFXYNkE/IMxvo5zhaEdvBwgz/cRvMVqzEjxxlhFboarohLSEqMw6acoJ4M'
        b'f0o0SIa2ueKFCwZ4WgyZORq9QadN1xVlulLSEDEj/BvljiIKLJFwrg5KabbjGWMc6sQGkvugCzZ8IusdGwjsXmwctnexyh6DOUFdfCK6iQ5jpMDsQQxGlIiS0Ra206w5'
        b'0IGIPwdHpPbnb+LK3dRXHvSkM0iTcsmwbPOSsiKfV2RM9O/W7jO9t2xF9thRUUMZIBhKNyVolzI0BR2MxXR8CWCj/QiDzfJts6h/6XPV3723e29ZIkq5x/y8OCAtXfAL'
        b'nV8H8v8lBlKQrxlyfFySkLgqsG/0y0wMvlNbhwxeB/TXrTM4kwH/vvzms/EaraZJ16T7Up2vqQpt0n2BucAXakNWyLxmTdrzDfBiQ5+Ql6R+Hic17MmtzbqzmtMaf8kX'
        b'7NuyYeqJle8xMf2D+v3fdyP6fQde3HP1/XmLBwa0NDO/a2mPejeyn5j5Y6Q4Kv84A9jlg175bBNm2MTGgzVTvOLpHBHviBQ2sOhidh6smdszg3ks2+FzNKYcimtyAdee'
        b'JtqpO/0XNFUZyzMy4Y4xPtWBfwIf7uDUPbfPCNkoOpLCx13Q8YNHMCdincFjqxOwdYZVVg0uwffD1jNsG/kYxzHTxXHM/namRIbFrRv+yZIsRPWGDeiEGG1De5dhGMJB'
        b'+BQPii7LxTxGICAvG6pXZRcrBRyav4qjiNyS8KwsYEIMMIrIcPRwaWfS9dq397OmGvwjdHhC6OujvGCEz6w/7Ll04AW/dz9h392/weNo9PzRyooNsxh91f6alz7y+yGx'
        b'dfbFF5WF33+2evsrfab47//27pKE/Z+EfDNl7jeyF8s4ds6FiIglx+L8x0wZ9vWnxad/mZffPPdUWHzrhdVLVi+6vvKTF3f85fbbJ9+0lsZfip8asW33WGb9liHo7QH3'
        b'8qZNOPOUb8T7Cg9qcvlkWRxm3ihlh6FHzTxUGUDzSBe5mVQKBapJCAnttzrW4eMOWSrCau22ODPBhowI1IQuJMEzZvp0NrbwgScq40aXoFtmghtumOse7azGL0BbBEsx'
        b'JdVM/ScbF0crw1AVqibuCriZRRtmhq5FG6kVidpi4Z6Ufg5Dsgcrsg/cRUFBW9E+D2VcqBaeRVWxCUki4AFbWXQAT+wlKkoQ1haCsJWvykJHQhRhqB5ryQAEyPkVADN8'
        b'wmrhVmxj3haszL1YnyWKfLXTGL1snmumHGnTWngF7TPHdzJbYDmsp93RLIENyqRQbG5WxuLhY4FMykkHwU2dTMBHmJnifEtGrl4QGiqBkCeyWPnywWQrZvwYHl/5X3iW'
        b'/5nn+P/wPP9vsUiMSVxGiHqEsy7/HpsJcFIwydnmQsGvPsLqpD7lTfwCZXB/aEtENdj+xrwVtbCwDNbYhWCm2IXcCFVJHeQWzBHjwsoEglJxlcQqrgLlbKnEKjEllHhZ'
        b'ucPAKm5kSqWLgMGXB2ameCxDW14CDP4RWNe2Skk5q5jUMBloGVLS+LNVlL9QD0pFVtFhthHMAst3L2NL3UrdSf1Wt3LWqKYt8fiuySo+zDXSOg7zNG9AqUcVh/N5WNks'
        b'Tg+s7keZzQwDCuoMs2gpGYZPVuVmFZczGGL3Kim5K2doSSktKe1S8iWrzPhllUwo4YAVpz8sUDewhuG0Vo9ytoExjqxiqkAhIHcYHpGWbWSE3A2M4d80H2MWZ7E0b0qV'
        b'hz1vShVL6nbmfJvmFNNchVUiey581ynXaS13WKLltaIKbMfOAuUMHmdPrfiwxOp5WKqVaKWNLEmxeuKyJ7VuVk9/UOppk9g8sCrIad1xOamVI+VKvfAYeJUzWukq0uJd'
        b'q5fWA8+Kl2GYM53H6T9oZaRFq1cj40+e8lrPUi8r28AaozG8DIWXNQ7Wellxif6Ya2exOJ+3QW5lrOwqDj8bq/Um9/Z0qdbHKtwNcymfpu0jlHfmIa15W721vuPItyfO'
        b'U2X1oldvbV+rl9WT1EeeGbys3uRJ/larJ/ltFubYB/fCB/fCD/eCNX5v9SG90/bDY8oaXxB+4TJ/xXdSZ/oHwi+SjnvZR+uPfwNt/0o2EFj7UPh9cOsBVZ6khZXuVh8H'
        b'DFaugTMGmRmrdzmzgTFIzR7CnV1uBSbNfyjJxXa+IXTUQ1Yl7yQiWbuYpDY7cR9lY8Ja7l7KWJmVYAtbwBNj1K6StkvT0w2a1br0dAXbzoZFtDPmrua8++Rcvcmcmbc6'
        b'f+qPJJFQcMnAzBxd5ipsunVYdx3ZHnLyPONDRnWfQPXQPS9Lbi7O18lHmLqBKXJQv9wBpj9ZpLYSKc6a+CoMcjljBzmrAzDMJBVUeBY+gkUayartvx0Q3ydNPvTWyAs1'
        b'uRadHMMUPMKkoDL4YYBJV2DRGTJ1cr1Zt1o+Qk8ePz3C9PTDPjSB3DqTeHrt65LTUfqhm3y1xWSWZ+jkD711enOOzoj7jIcCX+/7ULAfMk8/ZIY9dBthWhoWFrYcpxPN'
        b'9mEflTw7z+wYpYn4o5C1i/QGra6o3X0hAXg2sRJxEm7V1M5n5uUXt/OrdMXYgMYt52l17W4ZxWadxmjU4Acr8/SGdrHRlJ+rN7fzRl2+0RhMhsttPm6A1qTwbXfLzDOY'
        b'ifFhbOdwTe08QYN2MR0eU7uIwGJql5osGcKdiD4gCXqzJiNX187o2zn8qF1sEjIwq9qlelO62ZKPH/Jmk9nYzheSK7falI2LEzDaRQWWPLNO4dmjjvprLljNTHJiqNSB'
        b'jG8QVNpIkYuotDxDJKKMEXNEmeXxvxTLR0HRlTEBrDv97U/TcX7Wn/FlgmiKj9gP34txqj913GK5yhKJKsOp+BdL5KgXK6jIvqwXde8GMH6/4BZ/YVk/XArLWpZaJqY0'
        b'N2JfJaLNSao4bF/tx1pNOjfBBx7ptCxA0FbsoIaP8AXLLdYKDgMqi36P5RZXyls5U1CBzIw1W/LRYzm3nyPSzcpaucmYaowpWBIyhQB/Y5kRCA6zmE9ygaARSx8skXgs'
        b'A3giNUxaK5/N4Pp4XHcKll4ckShYCu7FtEdkg0hL6hNpeVwHR37hbywVST0FOYKUMR7X8vlNWiKjRVYJbUtsfy4SWqf1sJMB/c3bf/OTQYHMylJ/mCgJk28imUY6l8nk'
        b'kui8I2kKkXE6mWHOpDO3cxqttl1syddqzDrjTPJU2i4hyLdak98u1eqyNJZcM8ZZkqTVZ5qNCY4K26W6onxdplmnNaaQtHhSWPwYNHPxrJKICm26o97BmIuZRlIs4zG2'
        b'ECzzETABY4GYGlMEu3wY8u/LWIgOpUKXJscLq/WwOpysOyaS5YnRaDsDlPCKCO2chY53s0VItAXRqmhr3ZZ6AVnszfJwGD5WxuFk7GovOXUsLb5UkZlmqrGsXwnyfTCW'
        b'4YLG0RgzPHEKQyRoOeOBDR8qozBOYMnHVHFVHuS+mgTp8BgQ0rw7BkeWJXV6Qt2sLMGhnux6gthkJKkj9XsCBG8lCgMoOYkb5sg9VZzmY5RncWMYtHJmFcBg4TsrBqSU'
        b'M/hT8MQYueeQO5zCY2TLtXI0zb+KKDSYDIjCVSUmSG9XuvytpOappZyV1ovz1lSJMbJyWKnhDTJyj9PpLytvzCciBxMRrcfK2+vIx2pnBFY7ebMoiy3+iMEqJQNK/PBg'
        b'iYhQpvFcOG2tyOAufJN4LkwmmEStDKnD7rzHOEdskHZJocZI3Z9cNsZrzFqNq9YYowm+xQqY2eHxnEcuFJEzKSHojEaF9IlZZQcOy9Ipk8zHDa82TXdiMMZWlvWhXBJz'
        b'Q5ZwwiDKO2WsDGN2EMbfwUxJhCYzU5dvNnUIe60uM8+oMXf27nY0gAW0hjRN+oFpnMYP0QQ9SfD4rUyfa5eQYcOkLFSZ4eyemxOg8Yxj6Y0TZMBgzImDAkuCeu+DQ6dQ'
        b'k+pWkXv33ySR1E5wJPbGxjB2RwLg5E8JjqpaWDswPiEpKTRYkYs2iYFHGItN332orpt7VGr/Ni3EFx1Iw8pfGkt5gNjh7kjjtksFBwgmSbcsEY1RlJYzabwznfALCeYT'
        b'QtwieSayAR6kiakiKWnvY48wnKPP1SXkabQ6Y+/L1dTjx+IqMTNyWQPhnngNpNs6jINFdQvVi8D3c6HNaoJngmMSw2ITYdPIucT6T06IDZ2HqpJTgwkXpbEycANqclsi'
        b'TdN/fmGXsMqd/R/rA/WXaq+xX6hzskJ2BtNgvVeEUL2ML9W/z0h7/oM721+82LBlC9O0ccLBEZVDd6+/IAJRr3tUXBApRNSzMToSbUEXUF1oYgCJBiuwezaCLDzcCLco'
        b'6Bp3HNqMfzgdF+g5ZccSN2qAlbQieBoehZvsC9cJYTp4oGNZOgIep24+D7gfrUc75rquTcOKFXCDeQ5+inaho+gQrF3jjC2i0VCx6JIwILCGQBCOahJQParDkKAbeliN'
        b'6jEnBzjPHk/UWIxs9qWXx3AKbBHoDXpzerqrQ3odyCF6jxdTEtQNX8IcBZxLOyZdbla7OJc+fcTSDia5fHKf52jbSLys2YzDN1mG//f17jJ8FCi94/AMAYc5TBZEpIqz'
        b'xE485n974EXP64mSJOoU8Q3L6AgKQw0c8IInn+7L+aCqCIrnhbAMbSBLszQK1Z4z3x9tTsEIbw+wuIQFwbJgCdo+FV21x7HCvX2EQsHBGDFjQlENbJ4fHJeI6lVhsaFT'
        b'Q+ISGWDwdiMxPg0Wwu1zUBvckhqajDYujEF1irjEBFzATlM472i4Uzw8XKd/a8M7nIkYj1tffPWB+tWMJl2TZvHzu+HVhtbFxysUlc0bp+9v3NNa3VrevJh7JVvcuipg'
        b'4uLXAmpyy6w7g8SjWqxuJslMiSnq5X7vsDu9dlbW3ZHtDwT/t8T3m9N1mLQoF2ydhDai2nhUjpsnoYf8YAYegReQ4KSbDlunGNF24oXr7IJzx9QyhHKGk1MoaQqECa/q'
        b'XWgzcQmNGkDXVkYow0JjMH1uDGWBGB5lI8bAM8Iq6BnUiJriw+K42YmqWLjJGcgiAiOeEaXBFnfHKt6Ta4memUYd1kzTV+dpLbk6Sjx+DuIpoK43lrd71UuGdMfcTqUd'
        b'lEooA5MTEXgdZCTqXQaxAi0ZnQRVgC+GTgS13b93gnocWN2oyuksj3FQlUM9JbQlzXL7DbTVTUaQhpyOAidteSXRkAJ+xFIHbcEmVO2kL0xdh+FJSl7waH94sSt5dSau'
        b'SR30NZ+n5IUruvgMLQT3wtaeScxBYKb5j46ZsHfLHjOhYNqZrK5OFunkXM3qDK1maiVjd1hYFhMoNhWji6ZemD7aGo+ZQAusiEmEm50YjHZ0WtXmIn1NcNs8X3QGiyG0'
        b'sQ9mNYfRXjp00+aic3b3fh2JbrvC28XSPG7UTEWnLomASyQE5aCCHcCS2XZyUI5qAjyeZY7OMk9nllvLp7rcP4qDOg0VVw46Ad97DZ4VTxYqw4SQhdQYJYl5XICpP1SB'
        b'NifELnDOpQjAwzp0Ybg7ugWvQhtdjSkawgOpuY8IRKtVKGINsIRTpnt7KKkTneKd1ZII8HCsZTgCVPD8rl7nFoBOwDZLFJmOo7CaiSfitS42cW4wql4kcM+5tHl4El4k'
        b'ICzAmIRaJXhwd6Ct+oe+TbxpNeED5XdOGe/T2LtXs8J8FZoETS7VRlTGL9RvZPwu4/cZn/wtVrNV+0rGGd3n0R/9MQIsmMQsiCqfb4v65NXWiO0tC0aOiiyTp+w/Vj57'
        b'PzO8/6sNL2vBu+/faXj1rTs3KlrrR+1eH8UBfmTg0NZJCgldm4Z16Brc0S1UD1aohUWc5fAEVWMGoG3ohgtDdXBTeEGJGerkdIFp7olLxyyTMszF8EYXnonK4G5aFzyK'
        b'qsY6Vs4vwQ3J9kUjT3SeC4A7FlIGvmZ6SDwJjyd5DqK9qF4ZphAD37UcqoNn0VlhJabMD7Y6cpHFTw89bB7Hok0Y52/TWtCtRX2FWBZ4WOUIZ7GHsqBTYb+eh3uRCJX0'
        b'fGOemXoLKBMPcjDxdcCXpb4jbPWzvnQlxZcpGdOdZ+qKdJl2jtlhbXSuWeAEIsGM6bD2Hre4al+D9XQWoEzegi/1hMkPczD5MvD33tm8ZTmZpVOwKfmRnAXrnHsfxVlI'
        b'tP/WCahVNBu1RcNLI2CzAgxDO/xWxg3KJWC9ti6Q/94XRH/bt3ho45DLo75e/jGgi/GH/HYPYDi1NybHyA+MsfN4IXnn9L9r3hgSPIQla/QBYwLeAPq6tO9FNND95yS3'
        b'EQkXZ1/3hBF+1uxJl7elDPtDBMhs4biKj16V7hp+pGbAQEX9xkDf6ukFsyy/9O1/P3GGR4Dy4ceHF7sNCv5Y1Pqf5pybBWOXJQ4/+055n6o3Vza/cCb6u7Np1osjTOvq'
        b'bp0qRp9WP6O+9tbpz1Yef0+CNv/nk9QlL45tzH1/yxz+g9i6dwPTrQ3vtvTdd+cfB69OSHn72HMvbN77fpRoR7+cZ8/kTUswqdo+fKDwpEuZ8BRW1Vs7TIJkzw6LwGsE'
        b'VW+Ss+CGzroNOtKHqDeoTUnrWDzQIhDjcb9ulkf8MjNxbK+EzegCaUU3Itk5i7AKTxaeQYGPj9WKl6MKWGcmi3zDi0KVYdgMORoa41CGJsE2StfJmHTP4QnHTLXWdb5F'
        b'YMAYHtaiVpN5FunY1lno1GNMkIZnOlkhXUwQ0xrKlFDj5Cl2luQsKQFGtLsfWs+hi5hvNtNhGpMKrwghOzGJqAWVCyE1Xgu44OxxZqJXj07DdnOtUAkLcOdPS+Extghz'
        b'/lo6jAMxkp5xml1oV1CH2YU2Bgmm2Y2hgS4y0JjSIQKxaGijQ1cwAV5DtQkMgJWwiRmPVQN4CF7phULdfq3TQORkPh4ufINynmAH51nrVB9Zd+JxJB4afMezvt5ifPVj'
        b'fZiSQY/kQ50USrE9rYPbSJ4EVta4BnSy1grx5dlOyqVtYO/K5aMBxCDQNQr3dHtCenq7LD29wKLJFdanqG1I9Vnabrsn2bOmMZkydZiv2k3P3+C2aWba3ew14Vpot4iw'
        b'1pFukV9S1kfCMv4yzDbJMvuIAajMhBnhnl6ogAUT4U0xfrweNXRzdDjWvk0hoMOho+O0giYFaGwrq+Uq3IgDhzppRFRxFDmdNCkaMx4/Ax67pEy+S81OC5cQq10PtzuN'
        b'syR2DY2vkmANTYQ1NJ5qaCKqlfFrcTsd94+Kme2uh4uS6AYs2IYaU7tZuWjnZM5nobeCpfsoxg/xd82BRTuq5oG6T9AsPgaT4F6aCTUmwQOu2ZQhMWKArsCmIBO/YOQS'
        b'/dYjCt5E/KSHcn0fqJc830AM01dOVrSWt5a37dEzQ19LlcRLVknen/Fp2sagjcMueO30Ox45R+75iW7UuKg/RbwQ9ecIPuooGJUtBhM0PovSoIKn/GYZqoR7lWFRiq5W'
        b'px42mUmY9xL/Z4lBKfDPp+FxNmIWvECLlkiJMUv2p8FqzK5yxyViZUbHwdP5aKMQdnIWHYPnCbOCW1GdgCkCszqQ7FBTnoQIXcOsszAipBPbkDILXwezWAdU7jI/huek'
        b'LLY0B3TDnDBnOYFoxO1cZq6pXZplyaWk1s7n47ztYrPGmK0zP1Yl4Y1kT4KxjFzWk8sGJ39YS+mrs17yXkDvHOJRsCrYJOI+JzzCWEQuxWQMPCjhrtaZc/K0tDljiWOQ'
        b'uq8MP+sErBRfTjhcs1IW07aCoHDVOLTVNBGddCKftPO+w0lyMTwB96mpUWFZLoR43YvPSGgYHgy6Ld50psdOyzdOegQ0WvLJdtJ1ix8nRO80wJ30GCj4TtFJb1hrwlrE'
        b'RY8CC7qMLs3H8vEKajUXoksehXCTd74MtQIwBR0XoZan0XYLcZv2Q7vScJHqhCS0SZm0gNrKsfirOjl0oWAbxWC9sEoVBlsj4fV51Pd6EV5zR7dh5aPi9+0bvDkaMfI/'
        b'tMG7R05EpH50EdqmhE0JBPiJaA+dSJx1PocTrkYKGy+xHUd0X3tH0Q4l1qYOoXPBDAiCW3jjQFivb29qZ0xk8VD0qf6B+neffaFOe76loXFbc3nzK83lo2oLmIZLDX1e'
        b'kbTumbR7XkDqbv/I8k8mBfwuoPbLiQH+LWXzIyLNEaKooxHBn/JR+cc58PZ7vjtX3FSIqG/KQ4O2YosH1aiw2bUPTyU8zUYpdVTdmLUgE2skZ5QxlP/w4xh4tgArNFRb'
        b'2Y+NOcFTiGpkcFeokMcbrudWKtF+gdPcwLOxF9t4u3A+sjGwDuPpBAZig7Setj0E7Yf74lUJA1zj0uJkj93Y5KHJz9dhaiTcobN3ax2YSxaLZHQZ1J0pCcF8Iz1Xn6kz'
        b'mHTpWca81elZeldTyKUiR6uUczzCU8wIOSj1VuDLm13YyoVHxKWRheS8yehmfHIoUUiFWefRCWUS3JRMHQn4W5DiXS0ce/AeZurCSGvhQZ/Vw3PopkZ3dHGgkoxv1Fg2'
        b'dg4QoYMMvJg1j25atoRCGyak1jUMvF2ILhbIpPkFsgIe+E/isjNQNV0SDuNCTFjbbXXzLPR095Ki82uwsr6TUGyBCAz35UsxXIeEoLrLAbA8HkslYTalE9E22MLCjbno'
        b'lmUKeb5dhlqw3bENE3h1QkicCgve7WuwQVxF+qqiMmcfdXBI7TvbGUICFzxmoua+FrLtC20ajqVTr+U7l/WLAnBnrjuWltvgFso50U54Bpv8+QWwfg3mNVcw3zFjgX4F'
        b'3ZiLFfcrFtyfVB6u9+1LCdRjFdpDod1FNABsJNUm+K+SAG+0hZu3Umx5mlRYJSfLHV0qXIPOcKhV5i4Gw2N5WDMgnSrPNDiXRU0WeAGj5aSieWASrlbYrx26sBRtSw6N'
        b'RTtRG1oPz8XESoBsCosODiu1RJKRu4YOoGqPULKzMx5dhdsWCX12YX/wEuVzy9F6CbwRk0BbCw4MScXcdzimpDZ83QiPUpGwo1QK+CQMv1qtGjAnVwgFVmaKgXQ0pky5'
        b'WhWXE4PVaJp8bCYLbvQhyK5WrelbKuTNWCUGnxcGkbyyi0kDgOB0ah42kViDSuJ3qia+prnWnmHMg2XSUrgD3dZX1y1lTLMxjfj89XZiSmsSwmbzm0lvH0/08Gu697RP'
        b'rqxf3wz1yRfKAu4eTGveMWzMjt37j00/ueTwIXV4Vfi9+N27f6zbfOOz4wt077W985frP07eOK7lVX6gb4nqTnTBy8smrI4uen7LvZ+enxM2Unf4TdnQvCX51W5FzTtb'
        b'EubsHT373Bu+qzPfPlx0sqbyzsQp3y1uNb08YMDBz+68r/0m+63tq+Zd+8c8ZdHXa1K/uulXkDVgxalBX5T8bd7Eb4s83gy8Mp078ubaCQ9S3gqI063/4z//Y3hx7/VL'
        b'n+e8/8ZLkf8sWLjyueXvzwycwk5/4dTb1kN/7bfz8un8tSa3gD/1zevb9nr817MD9921FG28rVRtfP3au39/5eriD3Nz/G6nqdb18U+atHTp6vmV5skLvvxXZE3S7+8c'
        b'G8x7ym+f/cc7/X/oP23SlZZpscOb+t7+++vD/nEsttJj9BfM23+YNqO1+Ly+WuEtWPYbYQMsiyenedSqKGutRhc44IHOc+zAp8xEGA0ZjXkGZjNn+jGALWSmw5rBwlrE'
        b'bdTg3cHR18Iz8CzarKDPCofCy/EJIWHk6SRs2njksuhotpYyc3gLm5qVuLkkOs8iIO0Lz6FatnQ51iup2n3FCo8okwk4REvRwrMSDNAtcibBhuFC3PQpWCXpCEIOg42E'
        b'30+w0vrXzrQqUVWsKhZuh3upVBEB78lcFobupiBN9qK6sfFkDRbXrghNMiRjPah/Ah8NdxTRdUvUBg/C7Y7AbHRuEI3NDl2WKmxeuI2u4ioIaKhWAvhQJgRb52eG5VFJ'
        b'B7doUK0yLhGb1vxQzDyt8ACsUFMn4jDVOnudhB8TvboJ7sMo3h9e5mPQ6VA6cvBcKnUckj3gYzMEIYo296WThdttQGc7vCzRcJNDnc9BbY9zCT6ZQexqvPfrUeZROTmv'
        b'Q04+Q6QkT12HPqw76+OOP6wvQ67unA9OC3CGYcho4Fkw3Ynhi8t44XQvloQYkWA0GWusdIjnZvZXWvIuMZKkkhe7yNKbvavoVLVcgm29a3ZhumaUgxV1laUisMIshTsG'
        b'wPX200xGoPWpxEqqSzSJ7At+o+EVyqbd4NV+qDYJnkkgjl7UNIJE5V9i0bH4YGFfSEX8ICVsiQ5NCg0R43k+zEaFoVOZXBd10N+hEpK4kG6nYgDnuRhMp5MxWFu/LH/n'
        b'CoboiVYwOLqCwX84HE+wu9zlb54uW28y64wmuTlH1/XwpjD3TnljzXK9SW7UFVj0Rp1Wbs6TEx8xLohTyfk8ZBevPI+EpWbosvKMOrnGUCw3WTIE/0inqjI1BhJ2ql+d'
        b'n2c067Rh8kV6bBJZzHIa76rXyu2YSaFy1I0fmIsxCJ1qMupMZqOeuKi7QDuRRvbIiYU4UU4OqCJ3JPyVVGmvHvewhyKrdMUkRFUoZf/RpaBWXojHDMPUYwUWE34oFHfm'
        b'nz0jdmYqfSLXa03y4Pk6fa5Bl7NaZwyNnWVSdK7HPtqO6FyNnPTRkE1CczVyErZMwHHUFSZPysMDl5+P2yKRrt1q0mfRUsKA4rnK0BCA8FzhuTFlGvX55m4d6eZH8QJd'
        b'rRePJMtYco8uT08Nd6wwzlsEK0pjsDaaGhMnmjdhAmxWuKO24glwR/SwCf0AZnFNskB02rMbKfg46l/YmRSAnRgYJzGwNu8sn9+wgNdt8xThLN0PdglNwvkow+kel9g9'
        b'JsPutXKuKP7Xe7y77yYU2Xeuk1HS39xmYU1ktXxn2+kH6tBPYzSyrM/V99Wrs75U54bEavgt92Vv1OkTdLLZaYPq5N8l/WnyZa8/meV/ufPuHeCrzzJrqv54SvTglKZB'
        b'Cx7oVmapdKqaDC3YJ/VPf77F5/XzmuCL99XLn7/asH5LY3mgdkYEl+0BDhYNDvpwuoKlPqWVIo0yNFjwKe1lDag2FG0Fgs5QgU7AaiXajFVu0UDAWxhUHYAafv2ilih9'
        b'jVGTT0XR4A5RtA6MIBHRWOBgPu/D+DFiLGakTInCaGdhLpF9dmR3SSE12g9KEEJqOyTQYwBrZoQCVPyQgxOGYcjofl+7+CkD9x6xdkVcCXBfbIbSQSI97OJ22HjKpNm+'
        b'EdGK8DgVAHNgk7ce3g59THAbRx01/0Mb/EWgJzeFJMlCgpdj+nqOTIiKGB05dtSYKHgFtpjNxsICiwlbTS3YLDyPzZ5WdAld8JbK3L3cPD3IBmNYx5Ll1Stu6AwxuajN'
        b'8MmKOLIBXBphiWaXL4wXDIkBPjGgAYCIiNknpu3yCbRj+0n9+4yJLP5VMS/3e3moV1mED//8Xx4EqsQ/urMverfc2xu9gS09sfJh3Q8n/MbsiXnZLdtrSeS20+M/Xb5s'
        b'snb3rNi334mV3eaWJWZe/cfyvZE/Z6+/Y54x4rvv53ps2jHg2gPu6gm/7CIxRmyqGG6YHeIwnw/AHY79b1uyBL3yGrqFNpRgHO/spEBHYeujAlweH7xmzDOnZ2CTnIx5'
        b'gCu6RxF098WILqVh/yWqJ0J0e3WO9RNn+Pijw9pojg40r8WXiG5o/vYjdsOSqPdpqdlPiuVYBQ6H1cmRYzlQKB4Ia33C4GZ4m6LCwbUs8PMhYXzq3Bf75ALhUKWdaD06'
        b'jbZhtAjDBkUrCCuGx4QDHEMloKoogJigCRUjAgV0ei+PB/snYTSOVqvOJeYL6CSEVnhIQbT/cGry/jLjaSFxQUYcsMaGM8BHHZLBRAiJOvc+QD3oGQDy1QlX1X7AfgRd'
        b'LDyYijah7QuGhoyJQDU8EM9j4GnYFEQLRT87AOQOzMXyTL3sZY/VQk1/9mlhPimWYMK9t2b3opZ44RipS5gmGlKxlr8dXYb7F6BNIsCpmamwPsYyhvBZuLOow+O3IAab'
        b'NKhKFbdyEPFsEgOHxnBgc4JYCZjtuitWwst0XbpxrQQMlFeIQDSQvRewL/5HQLejnxo8UipdAiI2roiON2aGjstP+f3YI+EakYWI3ixVKrqA5U9iRh+QiDatoHDXPz0R'
        b'yIq/JJ2JTJU9K3Tmsv9U8G6mJwNSyox3x/wwnCaemDkVfDv/Xxhp1L7pYfZRvThaxby77HkeyMtMi8ddXUsTd8r+xHzC6SXAZ31ewJq31tDEQRFzGL9oJZ6k9asCZN+O'
        b'oYmipf2Ye+4ZmA2VlS5+9nth8/LecRZwN/IzDGlZ4d3QAUtp4q6iBQyIni8CPhpleEax0Pop0xZGNShFDNRl2YsjfBU0cfOqJeATSyGDQSq52yc2S2goexgzS3+AB/m4'
        b'odD7Qus/jR0M6kZvBrib1ruZa1bTxGcVCUzR1FkiXHzVXVYVSxN/AP5MvmEF7qZ60CdBk4XWpxe9xSSsmikBao33F1Psm6yv5L0IXmD7cRgr9db+/kLiawtLQdOg/4vH'
        b'U+2fPvMZIbEs7QOQH2XicOKEJkOekHi/0BMMXIR1rhS1asK6cULiDzH5oGwZj7WTexnv9tfF68N+elpkOoIH6K2B3IK51ze/G+3z5cFdX72/9BtjWf/wvPFfgz4fSHz+'
        b'2r+FYacvjLwTp2wdyWx6qnzyLrmt4odSn/SZdZ9/N3T46L1fnzUmJv5zvPYfkYvfK77J5zU993tL7LgHXteL/3b48O3jidrEK02jZafVX//0mnfy0FU/DfMIXBbbf8+9'
        b'Zflh78VdvjNnrXz4xxXiORONz2WMmfdc439GnNqye3K6YkRWakJ82txTw/61NT+iymiMOFiqzT6cd9JP5LV0xNot/T0//eW79lVHV9W0ykf8c8zIKsOqkrO7jnwW+mJI'
        b'xAcLly/w9bg655u/Dt1lqh2jaavxqt3QcKZpXuWPRQV3vykPej2m/MUxe14t+Wq1+b3bnvfv5Y8+/7rul79e3ndr3uR+f0HTI94+833Vg6t/+OIl0aZ9wS0wdPvij8d+'
        b'fS/s6w+nDr43dPCHrQmFX/Y7+Er8oZhxJ/56774t8pNd/665lbrthc1fHGr464p3vr771omjn715e/dHvt8Uv5Y47Kc92n9uLPyiDsreXDr1xD+Lt4m/2tb0+U8f531j'
        b'Pf/HmyfTE/r951TCuR+yD3smxrhN3LVu6Ln59z1nTz31MxgfVL9k9gaFlMaWDoPHSXgFqoK30V7nbvFQuGEIVbjWTpymRFXhxGV4ER2BjUwK3JdHwwmgbTk6qYwLjYcb'
        b'4JHQkCQRkIlZdJMcj0MlWgC0FTrEFbqV65BYtUMEP8tueG4t5h7J4+H1WHiaJyf1DcuBl4T1QbQbnVeGKeKU9qM2vVEZqjdzeXDXZMFdUaFAG6kfx4Iaqb/E6cephPuo'
        b'8180CZ3pdHDPU4mOWCdYC6t+beSBz69fK39ijVPqEKRUCme4SuGhMoZn/b183HnG9WQ08j0Yfwfgf19mOBaKA7FC6kU365G1TF/GH3+7/8yy7M9STkxLSem2FRkux5NV'
        b'h6De5bmgqYroPpp2id0EbRdRu9JFkP/32xKxNryZ3NMNO/VO+U/O4hrUTf7/LaR3+U+c8n4YQVserQEMh06RJsL4C7FmeAM2RlrIMim6rsECrVZwHPcfJbiOHT4WEQiH'
        b'F0XoNFwfSY8/hccgWcOzr/3BPeiSMonGxPqgSm4wuu1FueNfvFmQEEgGTK064D5MYJkP5vDgrYI+VDmQDJotJHpGi0H0+AHUk+1XYgX6d4cf4kyH8JNvwKhBdVO8YIRs'
        b'zlcj9e9c/Ns4acHTYxceDVv43tI5anlMoYFZdK9it1fy+WnT1vm+9IN7hduhYGXY3Za/bVWebfvwD/U7+9/4xDOveJx5fkPxTxVrGgwTaxYd+ch3f+LX59/87nj/73y3'
        b'vfoh43t8etmXH3xwa8v+0yNSissqnv1RfnLK2heVppC7/R/W3/yD15dnRu9dtG7puBMXDh3Yeo//x98kX7Phy7dqFBLhQImd8Cxs8+h2dDM8gVqF45vhRV6g+5uWp2BV'
        b'sauPE54ZD2tpaFUiA4+SeQqAdR1+MlSfQNYZD/J56OoCStrB6OY4h0KXDfeRbJhH+IZwsAmT/xaaZx3aTw4/RPUdU+gFz6LnVnCzYCs8IYTVV+filsNDk0JRTYJCDLwH'
        b'ot1FXLoS3aLQwO1B6DasTTYk2bUflSNkcgDcwsPn5JEO49L/f5w5PDHrcFAxZR0hrqxjIIl/YpmRc2SU7Fmyb5f1p7vVxJRZGLfg3HbzfhPpRt//bbgbnCROmpZ0I/F/'
        b'je2dxOmEtUyFNieJwwsqFniP5bIKYH2P693kzyRjOoKHtEwap2XTeC2XJtLyaWL8keCPNBukueFv9+3cdl4r2iQcnUcCD3itWCuhu8A8dDKtVOtWAbTuWo9NbJon/i2j'
        b'vz3pby/824v+9qa/vfFvH/q7D/3tg2ukrlVcp6+2b4U0rY+zNcbZmp+2H23NFz+Tkn+t/yZyhB45ZLK/NoA+69vDs0BtEH3mZ/89QDsQt9DP/muQdjD+5a+lxwIohrR7'
        b'JQh8PlFj0GTrjB9Kurplieuwcx45jRzplOlxJfQm4iOkjlptsUGzWk/ctcVyjVZLHIlG3eq8Qp2LX7Jz5bgQzkQWBux+T8Hp6PRn0hJh8pRcncakkxvyzMRXqzHTzBYT'
        b'Ofm/kwvSRLLIdQbioNTKM4rl9u3PYXavsibTrC/UmEnF+XkG6mTWkRYNucWdPZMLTIKzGjelMbr4V6kXeo2mmKYW6oz6LD1OJZ0063CncZ06TWZOL65j+yjYWw2jg2k2'
        b'agymLB3xdGs1Zg0BMle/Wm8WBhR3s3MHDVl5xtX0IEv5mhx9Zk5XV7nFoMeVY0j0Wp3BrM8qto8UFv+dKno4KMdszjdNDA/X5OvDVublGfSmMK0u3H5q/sORjsdZeDIz'
        b'NJmruucJy8zWJ5GjMvIxxqzJM2p79yFFA/sGSbq5LEv0K7dI2pcVHlZ2914b9Ga9JldfosNz2w0xDSazxpDZdX2B/Nk96A7IBSc6/qHPNuBxnJ4S63zU3WP+BMe5ipPo'
        b'XgqsdGxAx7pvRusDD3bbLDMJltPNaHAjOhDkUE+IchIcoxqdGxaG6skx0WPhLvGzU+A++yHw8MISZItfLcX5kkPJbo1NyQzwhfs5tB4eRrf0z3x+mDMRf0ud4RbZshb8'
        b'0X18VfnfV8fYN1mELQzWxGnYC4H9I9ZEhGuXPX++oXFbW7mi9lJ5W/mo2tC+hZVtu5rLRxycQraCRg0CG1b0Ofgqi20KejJwGzzHubhcsFVQ3kmSw4ujBRvihHR4NyHN'
        b'rUyflZpH12tXZCs9cH8VWKHAFsAOQanoB228NALuom5fNzU8p4RX0WG0OWY0Dzh0nTGgowyV72PhSXgwXhgEBh6GrfQ8OLg+m6Wrz+MXzkK18aESwMLN6qeZeCO8TlUU'
        b'eKxwqJJUFzmGg60FQFLCoL1z4WVaJ9mekYnNDNK5qsQEMcBaIYPaAtBexx6FJ1hGJLG5VGD7uwrsdcBPRrdLEE29pH9nrHVu1RQEdrMQm2wkB3s+LuawmRWydd43WsM6'
        b'NrWXOf9/9Os92rA3eHrfy0XgtIKVjhNwFSR02LHy1cwI4HTe12U048seDJhwak7XJh2bvh4G9rqghhvhtHmZTwRUjgCUNN1u4Rj39QLRfgdED/1cFtUca3Nhv2YEpOmE'
        b'5+q1pl4bO+RsTEUac+h3PazhZebqMS8PNWGWrvhVQHik64ry9UYqLnqF44gTjqcIHB0liDzqOvCdm3fweHrsZTToOAjYJnLh8U++UtDjwYPdVwowdyUxdirYMiMVbZox'
        b'gCfvPQCwHt4aR8OQiuPhXngKHpiBYS0FpQa4m7pCE+BOtA3VxlLtPgquh7t4zCdq2bjk1fqtnhc501KcSfq3EYNqX/Usi5Dxaw7kH2WCnquUHn333o17H0buTxpV/FXO'
        b'xcxXj3744Rtele9EvHLo6NvnT6zP3BtycEwTavqufsflHye+1fx9aM3N43eWvPPa99N37Q8Gum8kPlGBcu1DhTu1NtLG9xOYCgnz7m77jEaVlP+g22ibljhgY9GmeH+0'
        b'hQFSdJ2F1WFWIcbjkhntt68jLPawryKUTKUOmbHocAgxz6rhNWETcRIDW+BmWEO53lK4czBx1wxa6Lq+UO0v8OndgSscLA9Wo6MOtjcDCZYUah6NDpLwtMtwVzh5yws/'
        b'loE34DW4Tyi+BTaSY7zJXn14Eu127NcPhDYKWXquu+PMTtQCtwvnduYNQseps2cyOlFCX0IQY2flwDcDboSnOLQxAe3sdALgk3BfTIM6Q6axON9MWTA9Hb6DBSvIyR6+'
        b'1MXiTgM0uzM+e2nXPSJPdtan/WjmDj5M9mod64EP/+XX8GE7OP8faFkzczSGbJ0Qu+HQixyMoYvOhVWnJ1W3DLo1T6plkS533wTLJ9nVICM66gUPoZPxPelBlWn6ke8/'
        b'B0y5OOMX0d796ob6lkf4if7Pa7+k5P9ximjZeqV84oIxc/uMuXS4qajqbeXwcat3HxijXPh6Q7+vR765/W+gf0rK1RkNT7//4/Uzy3Zb7zAfbZaey51z4+xTf30n5cGr'
        b'z51s2FuS4/GCufrf4p8u1O7+w7qf/9nqHyfdp3ATCPU5/3GoCl5Vuugt8ICJaj1yVL8c1iaTDbzwpCoYrketDPBCmzgdPDZJ2MnZxAx+FjZ0oQpKEmgPfI56boek5j5L'
        b'3icRjpVLBvDhDLygXyCoZxvQJXhSOMY4PhluCo9RCYrkvLUMiECHxROYYBpxNgydQ9uJjjQb1VM1iYmfCtsoSQ9B+2CLfWAHQBtjV63gLdRI+zeCH2DXoWDdEk7QodKQ'
        b'sFMNXZyMNjo1KLhtnJ2bwL1o668nZ+9MiobpDpzpGmxN/ie6U+dnMFMyuAv5dClsd4fs7pWIjXuc1EuO6m3pgXrffgT1PqZ5BdcuzskzmfXadjdMG2YD0RXaxYLO0PsW'
        b'JkrhvHP7ksi5fUn0RNuXOOoX4D8kgrEbwU3XaokNRajSRQERbFCn+O+VtIXOCIQdg+9jZzkYRIbGsKo7eTs5gr3vQskU4ScuHBxvMWALNjR2Vg8xSy7xT46SxF4nxTrF'
        b'Oyl6gteoM1uMBtNEuXq+0aJTk7Al4TAHrUqunqPJNQlpmlycqC3G+hBRywzm38ShyEsL5C8Cul+isC3vgXrF82/duXvn3TvnG9p2NpY3lk+obd3Tai1NP7mzdeOo2uaN'
        b'jfVD96+vHlq5XiTdtycwcEOgLLAmVBYQcCfCtyq1LGN/IEiY6zl+RJOCo8TpgXZOd2EgTMZkgX2EwAOCuL7uhxoJZ4CX0Wknd4Dn4SkzwWUdps2K+IRYeBSdhNXJiagm'
        b'IQxuJn5SFihgnQiegUfgxl9PqV4arTZdl6HPNFEtmBKqT2dCjSdkWjKoC5V0Lme3gMSCID1BLk3k0txZBru+gYR3yZbnzEup+BS+3OyBil98BBU/Gr7/VTolYZTP9ESn'
        b'86hDDZOqQcBNErDnQrAurrT//5EsKRabmiwXnGBmwWdGbZQsvUGTK9fqcnXdowyfnFiTn7nPUmLd9/0KSqwvPuhOrk9MrKEgYbXnfNsuTKxUGrYq5tqJdTg8S+nVLux3'
        b'DhFUhctw30C7HIc7rAKxLphDF17cp2uUcWgT2hSeNi0ebupMq9PgZonvfHjt11NqH8E9+xhiTaPE2kXVC+tW1C5TT3chSuMZJw2ew5fXe6DBy4+gwcc2+5g3NzE24PLm'
        b'pic7Bd+hCmf0QH0UFSmZGCyrMzDFYexz8W53+IwzLUYjFhy5xS62/W9FzKo3p3OmZ3BC0eCr5OVQLQ2NOz3/QFBy1GNRclMnlLyb4NEk+xmjJLG4jPA0OYCtQ4AQhETN'
        b'6CpGyrOFFCknhZHTBgTdEtt9+yhSrnQzk+1Iw6bPxcplODZhO0uPEDFGyXo9bJPIYTPa0eX1XT3iYWaexWB2mVRTT3iYIe0JD7sVTXJEYOb1KigEbwjFyVZ8eb8HnDzR'
        b'+wurHg/C/xJOVmCcNPSKkx0x20+Mj/LgEKLw6Q3ywrFho0N6YNxPhp+f+7wFKH5qfpY68PNx2Dn4373hZxNrZ5kRRUu7YudIuBcj5wV4mzozJLCcc2JnLXyOYidqmk/R'
        b'Ex4qRrvsL6Xsip+rxOOhTQwvPA2vPwF6+pCBfRx2rhSOMOuCGl1L2pnk+d4R8iK+fNwDQh56BEI+rlVF/65bxCXp6dq8zPT0dj7dYsxt9yTXdMdiT7uHc8+OXmvcSwqR'
        b'1+cYD5PLEWD3LLdL8415+Tqjubhd6nDM0jiPdond+dnu7uKAJE4QaktRVYzKAkp8tMO/+aAKF2/mVnyxkIEjR0NKWd6DZ1z+WSnj54mHj2F/FnO9fPO+HjiXTMb4eJGP'
        b'l5TuSEUn0JEJHfu/0aVEbE5je3iNmAXYaBetg61ofbdVIcIBooH9BILOC9NCVH57X/s+GPvc0RPIH8pnF5EjUon/NZNscjEaiILnotAlYXu181waLznHoYt/9ya+PGCd'
        b'G/p5hr7hGV3SBXQccYRaUDW8gdYLnXMEdMS5S2A93AFPWugZN9vjsx0x2aNm/oao7A3oQDeW6OFgJCQqyL7NAXR+YW/HKc7/zTu1SGPdvciyJAVHY3K8Sz0AHtDxQR7y'
        b'3N2LNHNpdOug5WK/N5jxgEa3LuaS14JcohfOWTdZdD+gLfuX2QMUbatS0k8OaVp1bfGG4L1JL40fvWST6kDymUnHJi4f9M7KkphZs/+15PsBvwS9Pi6opFipmSuVrPJ7'
        b'c9DfWTRFNtpv/NVRlaNfLi1MHD9iXXDfScELiqZd5tN9j+WfG5KR/r7+omTYgqNq3fi4Va+7fRU7RenZP2exUVQ27NNZhe5fmArzg/u/N/ukR6DntXW/YNPjR0WkmL5E'
        b'0bSyj9PBLTi34a4hcUE87eelZ1kQkUPOyFIniIdIhYCk2py+QGYgxxSqlzELFwiJb5X4g7ppK0iUktXLIxFYRhOsuRWGnkO1iaFhSQnJC0is3cV8ui0Y1cdL0BbYXIyq'
        b'Z8MdohEAVox0w2bnbbib1ha1igfBPv1oIJRRlS808U0/MVhmoYFQuU0aN+Fo4vtfbSMTx+zmALPyoH5m+Esikw0QL2fUiE3XPblRspmKV/9Z4D9+wJKRk7Qiy30vxVcj'
        b'kxpzNXlBgX+uKjoaHbLgbkbGlZeyI++nDP6+r4coJDDo65z5ry7cNqfSHNtvWlHl378buXxA6QdtW/m/+IYM6G8wX7r71wPHp31e9irzzbGfvgpKtGpe+/Z69uiCvH1L'
        b'+qdXlx8Y9VP1j//hTp0e2XJgv4KnRjdqRLthW+d3T8UU5eHBKRMOl2sZktg9QopER8EtE9A5WIbKqXDzYGGDMpS8TJiMoQgb82WoDV1j0ZUZS6lwm7QOXVaimqHofAhx'
        b'+5H9fRPQEXSre2T9bz052vUYA6NJ08lfTnc+dkg3K0+DDsnZ7VLWh5ETdorvjbcd1TRz7TyJYHBRuH4rWM2M8Y6Th5EGfuhBHNbJe48hkpNpOjj4WWVIEqyz6w/T4BWi'
        b'QgyAB3h4aiJs6saP3BwswuXQThd+5Dy087/iRT2vaLk7eNHKKe6EFwGfdWNyd3sUFlFeNDJWDDDC5E+MJ5H2u4ZPFnjRi5IpT8aLQo5k/Ef1MHGd56cDPEtvLGgJrpg5'
        b'Ju6zpOLpHw4WB7kP/GDxjLSPp14fuX/etPnVg7aH3BiydEZ47LyiP3u35n01up3bEjIvP3LgsTGfzvpBe3DBRo9PgksfwYuC580S0a7weEZIB7/NNcsaJi4XyF4V4guI'
        b'Z/rwfMvkrWGBwsIjfXJOIqLvC5Ovy1cdzIwWEmUREiDDoxGdbpWdjJ0ibI4IgXtWduZy6CpsZON4tFP/9kElTz39g/75VOhrrZ4oQsY/f2LF+S/7VFx87xVli+mzD94K'
        b'mb1MwUxdenffRvaDhnv/552vyuSF/5qr+3Lc5DHjh9y9Om3KuZRrpf4z42e+3twYdf7+5ZCSu+PWXh/kn2iqU6pqzx/8YVcRfDDm4bJW689jVg26dPCBgqFO9BkB+ngi'
        b'UClPWI7q0W5WN1zSSbv8dbHIXalTq+ugzuGdqXMd8CbhBH6CmkMpVEbp1YicFT3/GyCATjIk9Ug5x+lrZS7/D3s/3IwegYXaRg4UCDE2EdOhKJ2SoZqHjfloc7etkuRD'
        b'j1Odj+mzSiS8D8HKHAaE+hrZUpbec1oe33NmhjyfBRqY5bJlbClfSt6aIKoCZpa8zsNoKPGyig5zWlEjUypaBAwDybsKilcKr8iiT8jLs0RLgAHTq+F5K3k9UxitgZRu'
        b'sXLGGpxL1Ci8KktMXzkShNsRl0qqGKuEvFdBK9mE81vFk0HBVsNaWlaEy36Jy75EXvCBoRdhKEX0PQ6krLRbWSku+3vDDFpWeClVWLeSA3sr2cAUSKvEQm6cgtk0ri1Y'
        b'eI+E/YVTSVagdQvEbMb+jmL3JMyodbr8OUayv3T+Q5HFnBU63kjYK0bWF8hkkwdGctyvcRSgm+ezCBK66QyW1Tojec3IbPJbTN4UoNW1yxYY9OSGKrBC2ekCrnWc4NlR'
        b'LX1zA90DtoBcyM75dmblrz3lS0be62OKFDYsB3F2w5q820Bmf+OI8I4b8rYad/sbbvxd7mT2byl9i42UodHeg9DOZ+KxpRkbOjaEHJ9AtxsMRUflg3nUCk/C2m7BF86z'
        b'zYm8tgKTVMukAvKSMjr+bLld1U+i42ic4OgDOevY1Iut6Ul7lm7OS8/NM2RP4hxvwOWIFWMhdL8KVUYLYGJzFivv9almeugG1sPASFgpKkbHjN1eKeUMUhtNIdUyqxij'
        b'jJgiWs5KXgbGaPnDgLxiCsMt8geNjJXpD4isIykUb8T2XtBYEXZEEd3tdp8VuiMqydLn5irYdsbQzuT01jXSI9Iz2sUZnP0sQTJrPH2nED2FCh0InECsdtwf8sb5anJO'
        b'ZesE2l8xGDlYVCyb/Zgt00yPW6af/AWYPR7C7GzCZcdqx4a/yMICcA8bEc+bisR/nGaP9j+/7EWMDFjFTX829o/jYoTEI5mCTLs3vChhQGku0Afe+Janr6CZvvDyA/Vy'
        b'eprWpfLm8kt7/lA59E8ndzZubCxvrGuNOVVuYTI9Z7p/PON40p9mrA/aKErwCKwRyY8MUg16fUzbx7I36hQJvtG+R9jgl6SRIyqXyIIvl02o1A3NpNurJ88O3DayWiFE'
        b'54tk8KJjfzXaDG1wLxsKj6EtgoJbhbYMV8aFOl8EuT1PeBdkWwB9PhY+B2/Tw1eqE1C9igEe5tXwFIvOpouEKJDDaH0/eCqOmJioGiuuyAa3rWWHxcKqX79Lu8/qPO2E'
        b'ccJLVNK1+my9uevpw/ajtqSUpgktBzHGd5yVVD9JczWO5mjB+B7F3JVH7L4mVjU8i26g66gWHptDDr1uHU3PZyYvuCLvVLaP1Hh4Qry2LzzfOyMhTiWBfRCR1yi8IodN'
        b'ahdpTJl6PdaMXwYOuTys80hJcnRFufqs4gUEfBokwlGuhq2V2+gQDSGgpzjBU+jGEB6bG5UsugbPo+d6B4b4iMkbhKg89COv3SIgldoBtINmfBdQlX2WA7BHnZbmZjHY'
        b'wUzr4GxEUREOoDuD9paSw8ddgOXJGXXwODyKEbACtfyqkctygGf8Y2+j5pYxdrTwrjiNy7hRND4ED0+Oj4yKdVp63kM5VDlyUti4/4kRM/75icYLgyeI2awu40WXlNoK'
        b'1QRCh9rphc5y8Bq6NortMqs8cHn3IT1Pg8Ecn2hTwBhsJvKAK2exjgFKOeHVaFYWc3+2QGpl8yOtDHlNGeWLoqT24RGjIqNGjxk7bvyE6TNmzpo955mY2Lj4hMSk5JS5'
        b'81LnL1i4aPGSNEE2EGElaBAMVhb0hZiUFXy7WFg3aRdl5miMpnYxOSckaqygF0i79j5qrDA5qznHS1c4wZ9HzvsR9orcUqJz8ZFjOwxy7/5c2PCJvom9z5LMjipa4cVc'
        b'FWROPnA0jXnUX3tElKixwkyscUEUeloUPLWUANAxC0c5eDA7Al6DrRTESdlRyqREeqibIhmWiTFLxWZ+y0TY/Jh1ArbTOsF/eeZH9/ewiEgAFUX1YynrBHdFaFhMohhu'
        b'QTuA9yJuKWxZQCMqx09KgbUsiTgCYClYio7I9PXqbzkT8bK7vRf5QL1Y8PhvHFrbWj7qH89Vtu4aVRm7fyg9eX+pSvTgG5GCpREJZIveUWVoLB6M2nAJcIti4YGhsLEA'
        b'NgnxToeJ075WBS+MwWNJT95KxGyzbziHdsANJof46EW90Jvy0s361TqTWbM6v+vpr45/Tio2fuyca65dSkt0fpWIq83GGD9xtEDLWXuUDht7d85TJpwyZjQ5HW0z1WjI'
        b'OC+LD4tFdVhwjDSK1j2Fds/pFtfX2T/K2eP6XLyjNsbpH/01UbbdtBvqBO2GHH2SLMI+PnTimXgs6zdjfnwZ1fFAHMS6q1ZRXWbDPH+gwhUsGKm2jtXPFg5RCJw7ISoS'
        b'tkZGgGFAMjQkiYH79EssJPzTpzASP7kcCS/x+BHa/AzcxcDLsG6ZpQ9p6faU+WibCJ3DqB8GwkaYaRPXfQIBthGic1apJ3PDlwo61PrhwQCbEIs/Uqszpq/RABoPjG7B'
        b'A5PgBRa1oRuY5sAkWFlEc8dbpOTgn2j/lWrZjGf9hCq2Z9P3k6tfjVGr/EXD8DzTI7XQuQR0ID4WnlaJtTGAH8jA856oTTjGMHA6nmiQM7VE7ZuaxwrVDJoxDfMRENEy'
        b'TR25z2uGkHg7QkxUvAhWqVZtWmMB+jfmX+dNf8FPXivxm51yJ+6FaFli5Dt7xi58c7lP/eAXvb8Nn1x1b5Tqoxnef6zd2jZe+l75R09fXLfy/7X3JeBRVNnCtfWaTieE'
        b'kIUlhD2djV0U2cWwBBKWoLJIm6Q6IaHTCdUdlthREaW72QUHETcWBZFFFEEUl5kqHcYZ3/BG/9Fnu8y4i8vguIxOxuWdc25Vp0MSxHnvf9/8//fIR3Xdqlt3P+eec+5Z'
        b'fluY9/ZYYfDgwc99e7zbScvSDYm5M+/49XBr4cnqhJc3PnLTv6fXXXem8lz36VtObjn42oL1P7bMeCn/mgMVfPGvu926fMTYHmk9H95oz33x7femb9185G9/XpD89po/'
        b'7r/hz78avO7ztBv/+r29vMB05uxVp+fmlE2aNCGydvpLtlev+73yt43iUyMeuG1xL+WG5w68/rcBNS9lj/mleforD6760Pbyrtced7/xqz6X/2rv/htHbw4kfFL/5Ge9'
        b'dz016YUvrnSZmVnFQ5doW1olIau0e68VPAu1XQT/vbV7RzDScoH6RGuY8S4q0yYcpx7OZg7u1O3TDRP1/j11D67qfnWzoRLNc9YKhTSi1Y3aKaI760aPNYxIdAOSHtpa'
        b'tCGRJwZwgahPXF2WOL+YrNCFWn68eq8Wufiggf8dQtbEBtjxPG7AU5deMmQoYagx7TFUosQzYSvscqKD74mhWgWJ78sLxKym8Bn0jIVrVd6P4TLmhiVqr6pXKj1uCgfa'
        b'itL+mdB9gvIBx8U7bMG61oqGAepNbf6+u4A8Fmk76wpta97U/FzSdgdMqO0bpj4+ZPgQievPS+ovtJPqvkbEQOpm9eapc3NUgGGuD3Df96g3VRpGnvivjaLVEg7JLYwG'
        b'GwEGDyN4hpGZNQUlJT9ogv8SbPOmDC4VcqVDnqCwiyflaH1XDYuyaHy3RmRRviGXqFSEpV3wPCjuFqBknumDlLTjqmOhaZHuo0DNqYxnDkKB6RQstNMwzUTxdLyVUYzm'
        b'g6LObDdlV3jrgfthWk8dRZZmRJYYNTU2NHgUBc8/oxIx5OaoFPCsDAD1gkX4a5o8UZvfg8pYAQycvKJGDixRPsL8ouxpHzYamvcx3p+NLWFHfFv2ioYKrmjVRSoSn/Wj'
        b'JKIvR5r1pVbtzmKMeV/K+CBjR8+SARNI2mPq3pXtCNXYoOLsIqFKBDUHBHUGCf8w7jrM9i4cZtirZBGHmUSDglIBMyzIEuQQgyJGrsf4vM0iziSVsACeUtx4fA+5YYOU'
        b'TUSWm0tacsYsGr+yzluYN56Izhpf9diFfQddm7NwMVzzXHhfmDt+0fhxRMCfxcYyKdnzHDGZyAFFzX5PuVK5JGqqVuobG6ImFFHBj7d+BczMaYLTqAi1RC0NqMKm+KIm'
        b'GEn4wGpUeiF+IBn9acLXbiPzI6Lh0EmUDLcQFGmXIRCJb0RYXazdpe4l35Tqw+jQR42UErms7p9aSn5ELdylLrN6R/HCNmRIm5PT22k2gBkQUjlkDhhLowTQ5kjpj9dd'
        b'/G7OXxgUZGAegpwbrZEEZRxe6c3kILAbbvg/mbs2pZnYJChNTId54bllUym3N5Z7E8vt6x7klU30Lnz+O929mFQS5e0tQnY2TQaMHq3WLwkIAuU1XgAMyeP11MEkeJZ7'
        b'vBeAu6ijQfEE0GwWx/hXrUPr0ENkJ1MgY3YIlspCGKt3ZamP5uVML3ARu6puYCPMAy2b30fdY8rRbtO2dm62jrHjW7UDACdxC0SPRAFLOQxKertYa661LLDCMwxUis8s'
        b'HkutTbYYKQxkCvgMjdatC+xyX51rSJAdt9gWJMj99HSi7IS0Q4+pIYWsVSY5SU6GbxLbPOsip8AzZ+yJJHeVU+FJUptc3eQ0eJZMxurcgi5y/5BYxZM5um1BijyAUgDj'
        b'kOoqD4RvzNCCbLkPpFMpgkc3wqiDoglXwsR4fIFJwAS2WXqGzHKugV1bzwAo7DYnS8Y9cXDAmfLNtADO/gj/WvjRQLmjRtIBPfjfrNhMx0GTm6DTjSaG/obySs8rMdZO'
        b'aOoZ17TC8zN2yFtSW3HLRb4fFisTQpAxnqCYeESygfLqjizxorYGb3mNzw2vo3FN6BbfhFiOdnULRt0pHDMBrHca4KibPx4QoiY3bgQEFh3aAiLQvN3K2TYlx9eNn7ab'
        b'nli1DpoehHjZsD48AJwahuyT+I5r+qC1l+0Yn5io2hubdsL4PBNP04HIVDwIYiGwg6IsLBWUETKKLoQxGNoaoGc550+TTUERfwHn83jUA08s7Ks0zsgr8xgNfjfb4a0l'
        b'LfzgKJ/bIhQOxinD1mJrFBEnj7++xXR9bvMAP+60/gZvTSBqB1ZTCfhX1MAuiruuYSZGXvkRz0T5hs64VTfgGtiIPeTw/2PRUCjTzdEwpFF3IYVvymyzDOO/KWnj3lSM'
        b'H7ksYxHSyAXYgYRAce8BaAybWFHpiv0y+RuBakCCwScbWpPYgag9ttw7OaxQusH3fxN1thGb3nbZYIn/hUZWtzZSScWWWrDAcq9XSeM7JZ0y4FVLmyZ1Pb9JUEKHuIZa'
        b'hSgkDEspLCHBEaaFXQtLcKNAbeSNNu7meS7I69KjA3zU5PPXlTdAc7vHmmtmER308KNRi4e14+Jsx3tACT+Iul0vR5R/Mt+UEt8XVnznAzyEdUWIdUWIdUWI7woON3Qm'
        b'JgrL5GkbjetIDXqLCrj0xTEeLz35i7WC7wU5JalNT1LO6wkrv92kxERWyCWFoaVhEXqSa+AEJRupEZnI7GboDVKECMkBQV9KYtBAwSJA9gRGH0hKF+wYHmmy3iW43UBV'
        b'1QQ8dW63sVsUcz/tVVPpjfYZknGKRRQX0l1N6W1AtrXwzmdqcfyiK7xQ/9hc+XJj81qkzytshTSvoj6vkpFXx8lSiZLFGwRrJps8Ggj0fBo31zAafqPBxoTH/HZe3IT3'
        b'gXK6SPpeaIyLU7CTu4O2YxOr6idCxTL8LJSUsWo62kKtbndFfb3X7UaDcGMHTW1bHctA9HpZm9kw+A6UI5CpcBggJchVIb3LI0V7N+wz9/ObeN2hbREMDZJuOsW4ChBz'
        b'jS8QTULSXPZUesuZ0it6AgjUs1NqY2/Az5T+ON50Mn6emNmseDDCU+/WZeXghR8l+N8WYli2og47QUsqO9YJmZaNLGyUiCnimfaEQTVJlUNH+NAekYWLito8Kyu9jf6a'
        b'5Z5oIu5rbuAwsVb/lzjL2dBBn39s377EmQJmG0B4GXYlL2wTRhdd2LtcvHzdvovKIHjRLx4fCD+ahbYbB7apDTbAD2OcyO/hUsPh4QVy/kANLGYdo41EgvUPvPtuPIDn'
        b'M7lFQrOp2Rw0BYXlHHD1CCumTIwvJfjnsPtqHn/H6G8AZ5gRtS9zBM3sOdxxtRKqgUBNWVCepdkKNZuDFqjNErTi0AYt6RzkXA45Lc22oE05EeT9DwI/+mjQBu/FMZxP'
        b'CtqQZvGrQcGvytT6Wvi2htd5GHa4jiDaYuqH9JbLFnUAbAAvWeOVYbqjlkC9W66pDJB2Be0PsMMEYG1VRG2YEQHJT3Qm44AsPMl9aO+xV9b7/MySMcrLePYChUb5SsWM'
        b'xQiVMvPNR0TyWa7TzXUw5M6RDAE4hWywk+tgFn7BzqcQlJv1WIwSuTlpuwHrnSAPFUgXEyy6hKIiF1/kSjtftZl684TRG4WLdc7GM14bWWhGISAtQrs/DQ3tOoShCR0p'
        b'ffEykNeXH3UkLijaRUsB46KlYVteFnXFRKtolQTeLqEnNrsEHLjodCRLyVKqOdWcYkm1WyWn5DSRPtQITt3nx7ixG2dqG/OWTTerG/JLTFzmBKloRW6Zi6dIPyPLtFt1'
        b'gy8099KOaTdpFIIUv3GZuWGyuUzbUudiZ2CDs6zFsRIv1Z7luYQbBO2gGhrTTvkQcQTpV6XE8EMN0DE6aqvSHYfUlS/16NSKktUBlrLoMzqlFdXSUVj3JrG1a9pJ7Sae'
        b's6v3Ctr6Edrudjywgbr8ZVwcD5xMsR5RTx44XuAtJeBeeeaebYGJmVRWiTq3a0YnbZDHIjvkRPi1yk456RZ08sagqkvUMbmxrm6V3tqOCebYmShjYWDz5eP4TL6Vz2Qi'
        b'B7iKJH6Q9KM2U4nCxzZWgde5BdgpEbSIBWVr9ywNnBvJd1+MlCLwM7Nn5/NJaGNR2oonzXwW/G/qFt+jn+edh+hpXrmc72QHtQGlwpoyLzavfFNamwpjWTon1vTTVSJD'
        b'9FqNgCzU5xkdLChGgyE2c7uvias847zexjJ1Xv04mkqZB57QgSpvRDcCvlf6h2kgkDHHhsFECygJVIbhRMY1uFVhK4sRwjSRNGpEMGXzFzyzJ6SzsJX8sZJAzkniuI76'
        b'c9H0D2kzDI3V1dEMWtxur8fndstxQ5h6XpWUoXMZApYT4Kq5NTHZBR+VcHvpjOjCd9CRuBrbLVHKcRE9ROWIok57Rzi89gL1MOoOm2w/fx+hKLljcfbGx/aFCXiZFNsc'
        b'2Hlw59M6GjLNMKbVKtrNVtEhJtsA84vMc9sxr7bO70KcrR4OxLAgzw3THs9Sn5C0O7Tb1Vs6x4K49xpY8HaxVqyVFpg8TH0N5XySR6q1AOmmp0J8FU8Y0rrAyiRzgBUZ'
        b'lrSRhM3OJBrRlNKKWk9lgBwV6kP1TwiQFGsnSIPQWiA2KWJTevv6fp74iKqzX0h4tKp117loLLTEwELKOL49SYqLojluZWV10IkLIZ+YUSTGYG5KCXA6E0Yk6dXQKwmY'
        b'0lUjmOYxoSExSEcTawQzN5+9N63y6ZrJ/C4zsX/XQR5LKwu4m2d5jV6xVJylQSuDBwRNqrHOo/ZpwCqsZNq5hMoQDqLOiUQ6NgZ0vd1Wpvhi8NtNUkxeJQA37wAiEEnB'
        b'tAsMnc5SJpwPmle0oekYsTeqLaReVPRaLMcXg884SswhNuJ5mqyd0u7UjpXCJaytmz6zEJXy1s+YuSwOVCep+y393P07B9LucUBKhAkdIwKxopuMR3sY3Tfw0hXoUHVG'
        b'ff3SxoY255gmfel0jcGdvmeFYTr1KQV83zOGmkyMkpcCqxo8yj14a4vJ5zrcU81eqnWTFBOGWfmmvhdoXyH7oAMLw2kxSDwPcIrgxXoDcAARoopzVYr2LI6zPsbqwVZk'
        b'uEzbNC2/UDuhRbT704Gc3VxYAIjzF8vs2k5ZXd/u7CkmH0FtKNjHOZJ49CTg4hn/F8SzPBg7JT+MHCAXNiNrG+bo3qSzuXzL91eQjxc0kq5s9Afq62qaPHK2F7jZbDqT'
        b'V7JzPAHF40FvtPWtC9jVuSdcyj4a/V+Qnxy0sq6p9tUrUEer2DS73CdnIxeN7jrKZbmGBRjLztW5oBxXbjbju9taXsc1oW0V5V5v/Qo/ueVRyjE4GDrF9RUYXmqydaLd'
        b'37Y4YLPobFK8ZuYMACFkyqMJcXWQTOLnxsgrhqm/QzLU8qzMkxod/KImR6O2Y4a6XjuqHee57vN47RFOe1Q7mkR6QJke7S51vboZ36oPL+I50cfPVg+rOzsPDb84Du7k'
        b'1gMrc5WJjspsC0TSkDLDJojHZFbYICU6GBNli2xF1kG2yXZgDcxxx2PWBRbaKq20SJxRhw4SM4H7UUqK2vl3iS1HNGWWgW8KA9lyt9gsxUR3/YE/4GtQt5Kr5umIAjkK'
        b'QQnHxHXjgoL+BojPTA64CgnFA0HR78M7SkuZUDoKJKAvTPgnBIXJqFtggu9MRh4STiiGILdWqEJOTkJOjjd2UjPKz6ci8JKA71K8EAXZ+oydmUbtbpJfu1G6TlsHUkwu'
        b'3fcOZUwn6WCD4qmqWelGpU0y74gKPv/FO0M9Ihm2S4Cd4e97swnXDfopl8hfOSoQJOvBHWPHXzQfraxOPJawcHHaIGhcXg1TsgcHWEDZEA9pVGmFwVvLJEOoBeAfRtIi'
        b'ieQ8GQEhKKGmAPGdnCxtxKG+ypAb7ZLQfEgJ0BewtNiEAC4yr4GJphKK4LkFMPcGzMPe6M8JI6F50BqBPVmWgRoHMDFWQLJR01w8PYqKV/rkqFSCMeZNV5V7G9sfLsZI'
        b'JXa4iHItWVjOxfMqAOJzcJbKYvsF35FKLbn8PIOKC6RZUtB2hCvrfYBTAoSa/PGKJswfKxRJkuBWOXIBcboo/yNcpAul/BRtkYmpkKwAzEJbl+j3LIua6hXZo6Cc09/o'
        b'DRBrUdcqfLqQ7oOzbfs0ybBSpTAZKGuyC3ZeENCY3/yDU7QLPdESzp7KN/W4QD/bnT/GRKhFtJ4QWGFFXNIsAuFF2kJkXJaPK4xk8uJuNt/WoCjzy3nFijoo+JSeCTrn'
        b'hqwNilmBFPbAfFvdVV7U//DRmBmC06txZOfjZcFPEGHXwvt3WplM5kw4hVTCzocbvaIOd1daVWEu/ngdFcOD2I8MPN4icQhAxm5UD4d37KxhOUIE3olwNzUA6CgopMGe'
        b'fDNPOhqAtnbzROQCrABkyCjv9CUbTzAPnr7KJnYHT2BM0zjDzIhOWwW3m9ZYS9o831Jf/Qpf67aa3XeAv2+L+foBfjyMNSv5OGDJtPQYFlNKiL/jdIrWELawVdaeqYgm'
        b'un2oz4R+xKGAT3BYyWMzz/w0J+tHGGm8WUjmm7q3Hd74T9vhppi4rYqLP+ykdYOUC9IwArurAQ6E6SzppoKIf/ALMl8MmoMSIfzcgMROt2phM0DZ9R5+TgzxGye7ZqWC'
        b'1xeJshAvBIt0vgMcOzroB0rcEieCshpSZmUIJm1Mrgw9igPNjkXCiKz+3soNwEiJKPhlY9YOhetViyUADLYOmfSFsYZTFyrb0v8XRaO08gQz4euHjKMUq5TWLbk3cOzO'
        b'RkQbpf20e+KElY/M1DagMy311uSsdEk9pR7q3aGnd/xHsYtj5EgS8eIGGcJCMRhECL45nwBBtkEnP0grB+WW7HwrOWqdUV+5tKjG6ylRUCe6DQnSRjdiOsfEt4zF9KcG'
        b'BJkn+GOMtEDv6PwzDUWWsLLgaiLBpZmEmBY0/HNbdZVwqaSlK0ZmzpbrPXoQBSQpWywD/IWo8IeztZqjo2A/5iPgilrKK/yoiRC1klKgXKNELahOX98YiJrcdRRNiAI+'
        b'Ry1uzAEEdZyCRFTCHIq3A34cV0KCKbaoHEQjpBCdYOabuhiD1LH4E3GbnYvTWmMaoij3Q5PGpuQwwhzgIsTQV3O+CjILvokHHMVzTdODAFnAiYnK6JvxG7NScjUw2ojB'
        b'biCNM700fqmkVAQssoCjDs+ssl6ekXeZk/0OQRZdYuM+l8OnBKWmkrNdCL1V1jd6ZRry8koK5JCNQ/Xhzjvx34HxZS4b8HwwqDRQUVPdUhhmZSneW0rnEu8eNXkUBdBQ'
        b'PT50zGn0YXb9jd/r8TToCDBqgZ2HilrSKTxHJay9m8mwseOdsJ8mk/hSoGgyOBeo6tuUGJsF/KJzY5t8jsmUlIEyrU1Ymbwx/spAmAvJmIsY11uEzC5vLBNTjT/WZZNS'
        b'h/ckiDqf3W30YUMGmuIk5tjgpqRYQ1mOnyKvGOEYk0UB1XNDZxJz9KLkAYSWb2qVHSXHrU562fnQ5MbVh8tTF1ELTERNJw0wNLrlNp3NSMr12JY6Y3AUX6xp59srud2A'
        b'd1HwOtgUO0u2EokNk5cS10g9WzvlZvx/NacT7DSDaYZUEIeHaXjiSStvGJaQuo6P5qnSWw/0IA6cof4iuT0rKzuQHwOiAQi+JH7a7OdDOcuD8hCEmU52DhoZmqob8XIT'
        b'XtZcjGS3CjJZTDona5WcdmcXB0p3LY0Ug+4h7V71MPp/KtU2Lacg7jOKTFxirWjXTkrt9giL/ksmvTFREWqdS8CMxsRFqN+5QJKTQywIkRgyh6xVZpLg2mCv6MLYVwoj'
        b'hGdbNtg3mNc4POGKZ1yrXClRqWjW5KJ2ODBGe0zlUKSvUw2wQwC1IDA20Zg/+IW2hYVaCU2/KW2ShYCZpfT9whAztiTMWoUVDstePsDfkggJPZ47JA3BI/MPhv5SG8qr'
        b'PVGH3xNwNyj1cmMl0P4O/Np91ZVz5k4rLYkm4DtywQv4KsHt1kOeu91MU92NMW8MCi7mUOBC04l1T2xd82mksQt4IBGr7ZiN7EwerR9KtHSZCy3Jriv3kb9RdHODaGFD'
        b'6+pmDmvOJyuxZ7E+TI3hCKEphZrS5nVJmwahdDAmVL47bv4Q+tCle1BgErBaQVkcBv4V71CrHfhPEXhW2PfXMB14um8WgaYX0znUtqanQAnsMjNFEKJCeWV7GOhJ2bRG'
        b'2Nwd6FBplyUosP1MhoUkcWuAKPclD+X8G4ZwTEw9n9N1xqqQZkeN+C+xxfYBA+ZeOWti9pdov8b0I1cqnio7EfNRYUWFvkSiZqASGhoDNIpRk9xY1+BnNsTIdtG5adS0'
        b'ApUadMknw3c0zvSJULXk4u3Ila14emMyFLrJTtyMWklE2KeQ3CqHb0qgeWENi9qmerzLPYGaynJlLBZBNq14qTTEUvgPrWtsxkzV8oyT2o36WjzNFdLwpNkN8yDqkEbj'
        b'TvfANwFdL+KbMB8wAQdpSuVQxxWdfbB0D5a2yuZmm2xptjMJQ3MCrIEE0oX9ohl1VRyZXHNi0KY8Z+QLJsIMW2GP3SHbmhN9WZS2Q/qEnABvjbqtWPeyhrZtCTqCQKFm'
        b'cEs55Q0sW3akc5lcw1tQkjPo3MIrY+TEoHM5j3dBJ6sH7rOCDrhi2RYdq0CZsjNowTJlsdkGrXCyVtCX8B510Fmd+B51YmRL0BRMDNqBTrDV4jWh1iF32QhsStCuNGAu'
        b'aK2ZADOl5Cxan5zFOSg7i/P8YSjttd9/M/fr8UUkFWkRx44dSxMXFd2AUfgyxlPy2VF+UtRyRX2jUgMIiZ/mEqImn2eFeyX7WeVKZAYEdtLz9db4PH6GqOrKleoanz/a'
        b'FRPljYF6QnDuCsBfS6NWfFhV7wPqV6lv9MnsUCWEq1Wq9Hi9UemaWfX+qDTjyqKyqDSf7kuuvKbMlcRWOKkISFSARLY6Jn9gFVDPCdgA9xJPTfUSKJq1xo4Z3F5ojke/'
        b'B84XqjApHmhF1FzB5Cw2X2Odm75g+sgS3sNTz8oAPf7J0OEJTMuUtMcXmHRzVE6PUOogrdRkMjSx6tyypIvyyH4N3bAIPUmkx6KTMqBDcHP8iFZtsNEnE9DFVdOhRIZ2'
        b'spVcW/iiY7KedJKPXNB0WYhwaHoVEInLwl3WitKbNbpbk0y0XOFlc5BPYxqVkmxBLBcw6UJUcxueWtSFqUxAbGvpPqlcQQvw7OH1VZcxuT45pvA31ikYf7Al72KM4wsK'
        b's/sPzhvQjt6K6bchiiJjMmcz9IXJDHQzsiWGbA91cA1DspEdcFB44hU2cbqcrzcNMTZ9+GUdGZCdxewtUu4Afy7BTQkw2h9yuvgOLZNk0nGPitDTqJNWeQ0w8pX13npF'
        b'x+ascIO/o/O81t26rUH1n2Kt1ODTm02GFAt9V5GhI54k6LhYL5ZI3+10eGmgYuUOvlNScBOvo3zlFK9XEydE+JlOsFrFCbdAOWNNMXFCssUqZThTc8js+Xr15kv8CQ3L'
        b'1JPLRE7QdvJ9tP1VqNcXIwpI4U0sKSnRtbbGjdb2x/wCOETDLYC2uxFV4URmDXnX5TPnao+q2ziyhlTv1x7A78nM+PvFIkHHLHOF94vLmmFki2pq1z8p+u8E6m9H9oaZ'
        b'ZX+/umt16j0v3CI/+si5hb80HfflT5xwWzgyecuSaxwn9o9903d65ysLFtYevuex4y9cdu59yw+W70qv//Ddy+uSQr97sfmbz+pvOvjqmoyK0VO+emzyhk+6PFL8yXO3'
        b'bI9MK0hufnPgvseKZnwyZujeUeH5BSn+Jyd9+kruI1NGhZ9+csKnL/eqePatvs6P0pbNWvrBfV1CX3Vfds2rkX4tWy596K7nhl6bUHHm9OhVd24bFOx9evLr5zb8teDM'
        b'49NmHP9+X9fRO4qe+eyxN/b97sPMF3d+eM1Hs0YNnLs65L/0T39b6Kse9o6Qnt7wh6dKz/Yf+eWjruPZmy5bNOzT5HnpL5x7+cthRyYvejnh2u9KPA9/VTzxqvun3rf1'
        b'9gdyRx743ewt2rxFS/d/9GapJ2ds2Zt79+V/nb36k5Pl3rG7uz752JVDfT1+HFq0Y2v1xO6jhvb27Mm9/tMRb5Tse2fqpGGH9mYv3TCi77ZHzzzz8jW/rHj99J6qBYsH'
        b'lZeNO/XF0VuEv998b79znyzut/zj8vnfJw199bb+797+3mrv7/q9lrD15K3dShSupLr/VyMOjvxy7of185cOrrj7Lx9HQgO/n/PVd1PTPBPW/kdjpPH2zOo7Gkvv/fr3'
        b'H1uOrn19dujusjFf5c5+5suvfqdUrHjvyIxZq37z23PX3dPtyOMVnw7rdrYhvUedpcfpv26fUhipCP1jxMKz28fNP+rP8vzx1Buzzd8crdk/orzxsg8+OvZQr9cS55zc'
        b'/NKd+17zfNCr7vB138yrPucZc3Ro08bma/bc9eak5x9tXlvwwojXQv9x4tOch/s++WDfvZ8e3S4t//w3bxSpHz38+ZHls49/XK5dO/KO998eeu81N0Q/v+PA4fIzyptr'
        b'T8nH/3Hp0WDhO8vC+/8wdnjpSx+t++rwu79Z/tGX7/x43bziQ19XBlM+23Vn32/2P/HJlfNbvpnz+HuuUZ+7xg3f+Vjk+/SCeZdd98qZv976pvvXv/fOzdr2Y4r7tVrz'
        b'xtPXN20Y/uqrv7zzmeFZT76xYsaY+T+cu8saDK656ZQz8MQfPMs/+atr9Yff/u25z1786MWareeeaVq57J0bGt7M+dBx+dI/X/5l4q9nlI166N55wc13bPj6pTc2Li2o'
        b'OfDvX4iL//DF9LyNtzcdvvSzmsrS4a9sXjnz9aUfTJvSbcSxHw9ed1V16bbyE+/veGN29Y3Hfpi4fNbbh3//m/xz7w36zlu9NcHfxJ/+pKjmyY13rc+d4uZ+8eyfE4c/'
        b'/Ye7Ns64PTLvucPDWt5yzv/w4ZXFz7/+oPjrT068Urj4708devR3/7j7jRNlq55+9u1evzgXOH7b8Ue+/dPVX353V8j/5/ujP3I1X5/4PuHvrkQWdHibqD1Nh6CbgbGc'
        b'Ma1AXadunj3dwnXTVovaY9ovLglkQ7Yxamg+5iqlg3N1k7rZwnVRnxK1h4Ep3WZdQnGE1I39J6Jn1mnqhsFT87UIx6Woa0WbXX1sgPYE2eSXqU9MQ8513pS8koJcjCV2'
        b'XFC3Jy0ipxtdrUPbBFBn4dO1k9p96lFtw0zyFD9RO6Ctj9da7TrFUFodre6hVjjVJ7Ud7MjXhnbeBQKXpD4r+rXV7qk3BIZBjl6LBkP1ZHuql4P3m4Yuo64xH2ZMJSA4'
        b'2i6pR7ST9Flf7dS1cVVPm1mcr210xakSsI/mag9yNxbbucnahgBuZxgj/mrUQ1jf74LqHku09YHhmH/tCG23v5DiR21ubK0vMOf8mrgV2k6beqLfbBZlaUc3bX8HgmTt'
        b'QfU2JkneN54CNS1U15pph7h1tL5DZGvHgPT7WZvRBS+uUf+Nhf3/cnH1ZeTC/xMXQyjmrS+X3W7yEIG2bly5mTwr/Iy/D6ReTpsTldJF9j/FBrS4ReBTU+C+q8DnzBL4'
        b'7ml4DN833ywMnJSR6TRlTJAEgc/gL/EK/MBGyGeV6KC+fzJes+naszdeU0x0hfIybHiXLOI11XT+vcNqPMH6+/bEVJqD3jvpCmUOrHcgz/CjBLmwxRl9BD4LcmZYgEug'
        b'srKcVvoduBCv3UfgNbdEeS52lrf2f1d/J5dWlgBH6zpOt2/i9qz8Cf/Jj4xRH2jdoNQIbj1O9SktnCn2sqs7a84kvy/6+8ESLU7+S8HWF+a8PiF5bfVj17z1TTO/5rVf'
        b'7Zi55bOt1b8Z8GFZepl8dtLUkktCOx66sWX7lKN/yg6NmZ6Vc9j2wEN/f+bsVY837fvqyts2vff2v99y/9U7z9y66Wh+4FbT7kE9bc3lxTu6vLXj84Mpr8z8dosy6vDm'
        b'l36b8pdZk1aemzPhtTvyP3SdXm3L+XH27N27n5sy8JqzDwz71aR/e7P+2YI/5o0tP7llU9VX1+4fmrvvstyd1/1l7A+7Uyxn1k2/v+KO6qq0VWUfu3LP3HP62dJx865q'
        b'2X/itRfn3PXdpClfDBj32PZuB63+YO03q15LutXk++2C98bOLw4u9XteeP/QtCl/WXhwXa+p52oXFX986Pijf1g7+fHDI5/fdOj4cyWHjj+//FDje885//ii980B9Xv3'
        b'vpX0/D23HpvzaUbo47HPH7nn1JnT28VnUi55p3zYO0WPPv+8fNc3jU1fVI0p+fWi4uUnd376xfEfbuzR9ZnH3nj3xPvjNhckffviF1uu3z5lTPKJd95975bmha+njfec'
        b'O37mtZd+serNJbnbqg/ds94z4NVI9QumvH8sHvXMjCMr8574oEbRrn1ifU3qnPq//KBkjd/2zoHPGk99lfZWi6/fSHXUr99ccu+OF1oKvr7vrbqeB3Ye+tPLE945cGZP'
        b'UpA3JVqOfHdFVlBOfiiUvb7nFzm7wsNyH9yzdnT3JXtuvWT0R3tC48wZFbcUeCs39Pq04uaxn77LhS5Vh5Y0rBs+Y9mmzMKGSN6id819fOfOLZm6945PX3J/m3fnF68N'
        b'+nra+1k/8FulVw/NtLrGBvrAmlJXa2s1Y1FtQD9fbFXleueIQ7WD6hqiR9THnbUGzaM90S+e7FG3lQ1lPiafAILhFMYxpSim2t4GPZDpEwI5EgLqaLO6NU89km/mtJvV'
        b'DYK2mr+u5mpy0F42Bfiu4oJcbdN07T4keChE4YZibb2F6zPXlDIT2kGOSB/spd6ve3JXn1ZPnOfNXXu4bAnRRtoDo9QdxZBP2+BCCirPzCWZ1C2jxKXqw9ovyDf0cPXx'
        b'dG394KnaRtGlPsJJU3n1mKs8gGqfg9xTi7VNOQKXvkzw8eN6a5upA4VBbVceOocvNXHmCYK2Js+pHVMfJ2pOVA8EKX5DTgHPmVcKM7XIUG2ndjt5WJo1VH2gGN+6pgER'
        b'YlWfFbRTvBrSwkvJCVKBqG0FWjGf4xZpjwtBfrxL20YVXq/dj8FWtXXwSrvzckE9xpdNU3ex0by5WVvPnIAxB2A3qEft5RbqGtCtITc5bIT7O0cLzXyR+vDVVNeQknxt'
        b'fWkhz40aIqjr+ClATq5lJNMhRYGqwkDG5U7VthdTKFyiyAZojxeNME1Wn+3FpuAZ7YT6VALQrMUF9hxtnfowBp0t1DZ2V5+W1J3qXmg8LplUdZ+2hRyswaigY7ViIE7T'
        b'l0jaMe2pYTO7UyeWqI+hZ0kMo649qD0rqDv4IlE9RqRZV/Xp5jwtPNjCzVgqqA/yV8PCCNFYa/doa2Bs1wN1J6Jn1FPCjfwE9WQJkbzVc68rVncATkQUCZPlQh5+tQBL'
        b'/Ii6hXJoR1K1w+r60tKCaY6uOJ8zTVzK5aJ6UN2i3c1y3LJIO1bMgqiXllAZTm2Nuu8GcfKyHGoclH90ETTczPFzOXXzcG2vemQExdNN0h68hvntM2kHta0s0q92WHuW'
        b'OtzVmaStVw+QN5I+6l2cVMGrz9jMrMwnpcXFBa7p0BzzXEG7OTNNO+RhkBVRH+pSrB7PpwU9DRdRgrpD0B7MbSSORLsHZu5xmFckqrVtxYW6l84UdY2o3ZQTIF9ds9Rt'
        b'6p7iafnTCljrOGf+QG2dWAKdfJLq76PtnYXvTTBlnCTx6n3q0/OpfICzw+pe1quZ2u7LYOBd06B4bRu6tjyYR+X7HOrdedPUwzmuwdNhvSZVadu0vaJ6EwxVhMof3ld7'
        b'ujhv6jTRpD3JSd15dbd2XyaN2YDhl2vrc1HoIqp3qrdx0mweSPRb1EeYj7AQJO7Pm27i+GIuww4MzZHZNCwTfQIM5uH8qfnkCS8yA4YlKGh3Z6rrqFhYaSdgtVOkU231'
        b'GE5K5tWdgHlWs9Bu+3trO4un55eMHM5zFm2roJ2sNS8uJYC1NGqHmJtRWMytnkYvL5nI1scD2h7tCHn5VMPaoThPn0NHLmVOEx8F7LS2mPxVGzDqlNF9qXhFrraDMK/2'
        b'sHpY2wHtW60ejPetyrzA2tQQg8ut2mrtIcMBq3oc8GmcE1YAhWPq7QEUoA8qGYEopgBAJhcjTc8gpDKDhmZDcYH6kBTUHuVmqgct2urahQz3H9C25Scge9qAnxbjwkrV'
        b'7hZnAiu7D0DzAertmDT1PhjnU+p+BOSpMwF5JGh7BFhw29STNPUyMMcntPXDtYPYV2DMEOaOCdC01f0YN7w+W12dp22aoW0u1o5fke8qgNnsmiXCEtldx3jvLYAsDhYD'
        b'TGJXI9Pypw9Gt5faI8O4fM6k3dk8n7KN7Ad7CNurNpa6gMFTN+I+lDZAUvfPEbVHtPuoPpuoPghNPjoD4LeUNhILtOhRgBh1Sz6rD3CIF2Yf2rScpH3Ah1oAmagnMrVj'
        b'0nztxGgqaLa6ozc0CgqODC8sBZQhACMOe95u7ZB6nJBREuCiCI0e7FUe7RAnFfDqYWGkjiv5PGzuYNra2L6G7b1cO9Wjv6Su8Wrb2VoMw9TeWjxtZu5MC2eWBO3ORKt6'
        b'3wQG/HeXDNHWz1uld7gAxlZ7ABaIdvvUnzprM3xzjvoX4KL+5S6xc2ni6B6CC5cgCFb+/D+7kGyS6BwlA/ghoM7Zf0HiMbeT5dFPVxifZ2e6iYJdv4MSgKK3UtmpZJrd'
        b'+uegkjEPs9eRBFYePBfM4sobufZ/l5l5JlFnOhSoVeL3BBob3O5W34LGkcTzfHxP8fiXcRrfODrlNChnGxUKjE+EGAYVGPzPwbWCk/la+ItcFb4KVdwig+BXgF8BfkX4'
        b'TYNfCX7nha+q4eDXHr4KrRcjvTF/LebkQ3zoKkMpr5lDhTyvWCdFkupMzXyduVmoszTjAaRFtnmtdbZmie7tXntdQrOJ7hO8jrrEZjPdO7zOuqRmCx5vBpKh9G7w2wV+'
        b'u8JvCvxmwW9X+IX3eFAb6RPkwknwmxQk90WRhCA67OUjyZAvFX5T4Lcb/DrhNw1+B6DKOPxaglKkr2yJpMtiJENOjGTKzkgPOSnSU06O9JK7NFvllGab3DXSPSjKXDgT'
        b'1dIj/eTUiEvuFimU0yKlcnpkppwRmSVnRqbI3SPT5B6RXLlnJF/uFcmTsyI5cu9IkZwdGSb3iYyW+0bGyf0i4+X+kUvlAZER8sDISHlQZKycE5kguyKXyLmRMXJeZJSc'
        b'H7lcLohcJhdGhsuDI0PlIZFieWhksDwsMl0eHpkrj4hMlUdGrpQviUyUR0UK5Esjs+XLInPk0ZGSsH0NF+kvXx6ZFEiHuy7ymMgMeWzkCnlcpEweHxki85HJQQu8yQ4L'
        b'QWvQVoWjlBpyhtJDvUMzqyR5gjwR5s8etEccpDTT6gvXGUoKpYbSIGdGKDPUPdQjlAXf9AkNChWGBoeGhCaGrgwVhaaGpoeKQ3NDZaF5sB76yJNi5VnDzrA17FojRGxU'
        b'sqSX66CSk0NdQimhbnrpvaDsvqEBoYEhVyg3lB8aFhoeGhEaGbokNCp0aeiy0OjQ5aExobGhcaHxoQmhSaHJUPO00IxQKdRZKF8Rq9MEdZqoTjPUx2rC8geG8uCLKaFp'
        b'VQny5FjuxJBIEQ0SIV9KqKvemuxQf2jJIGjJFVBDSWhWVVf5SuOb5oSwM5hANQykbxOglkQazwwYoZ7wdT/6Pge+zwsVhIZCe4uonNmhOVWZclGsdhHaKlJJ0g12nMdm'
        b'R3hA2BHODTuCjvC0NQKqh9CTfHqSz57c4Agm0NHpFBYqgQ4jmeUA4ozOFeOyOeZGHf1yNvJK9wA6MeFqeUPHXPcG09JtgD/HlV3DNFbLsysaa7yBGp9LUFYiLqKTQdyA'
        b'O3XB5a7ykagN9d/2mHRTZI6OqJXThrGMSwK0V+0JVCloomH1rKwkhR0yl8eD9/qqqMNQWiJlJR6dqdQBnoQ7O/oMr2tQPH4/pERvfTXaU6Nqm4JuTM5il89irWexcWfx'
        b'HPMs6vuc5Qxl7XrZA9iWfFqgontUbKhviNqhdNlTVY4mFNYqNzvRZeabrT4vYhg6aq6icqIJlfXucqWa4pVi0FX30hX1Pu+q2CM7PPKxwqIOuPcHynWvoVZIVXnLq/1R'
        b'C9xRYTa68fkDfnpL6vlUw/JypTWB6r+You/oxklPFT+pVfjqqRwvTGB5BftA8XiWo2d4TKDWBCVMlV5PuRI1e8thgodGxYqaalJqR/86LJ5I1I6xr9k9UyQ6rU9yQCmv'
        b'9GBcS7cbsle42URa4A7VIKKSW/FURZ1uucZfXuH1uCvLK5cwjWVYGDJzAIfUcYuQ42oXWBDfIlXFnG0JLF4Rqmqhqyp0LItqBpPxKF8gu11hDXDIy7oH+XjPCO39rv6U'
        b'6ylcnN/FdNx02sDBFm2bNqIym9lo41PwNmwBTOcAwMrElgR5wEFCFRp0ZMkUI4jMPMRwNimYSUEpbG/klJvDjmZTUAgnLBWUqXBv9uVQilMWhx0JXLMpzDGFtLA9nAJv'
        b'nNB3RzqOhTlsgXSvNULQHO4GNQq++4OCshWeZYXTqtApz3ZUIoN6ukI9Ryh3BnzdE0vzrYTnvcNdKN8H4S6AdyxkCZfRbIWclnAq5JRgr4CxXoPmNs8FJdhBeCrP3Mht'
        b'QQVjM3xlo3J7QC7DiY8dStC/DNrgzo53FE8J0nM51v8wT2XcAN8mhRMTDFs8MZxMbxMz0NkwsIEyF0zAd0EB8G1iOseMxMhJqo1FUogp7NF4Qpn3wjzYw92hdgHHJWhK'
        b'RROZDDYO8P4EtTjdGIlgG08aLsd/6UCkz7+AWPpnSa5xVZthFftLCD07Ge0qGGZfZsFK2kUp8JcsshBPTN+IBXgyA7WbwUuiU3AKyXxP/E60Uzgop9AGWLro+w8By/8R'
        b'dGBxwlS7dGBJjQcWeCvi5IUl2KOGtAEfnLw8+EaiO1z4pqDk/yhsgsVoDuNfGky6iHp+QYtyc9BC9j7WINTGFg+AS/cxnE8O9wj3Cw8EIMisMqFnKVi+s5rtYdSRs0Op'
        b'CUF7uAcA5Suw8JISuEzcmEW4d+J90EFgB+UEE4BETNIXMGkOsndB+xhu2e0+X7h/ODHcQ+bD/eD/QPjfO5xTxYe7YD3h3ghcqUBiwvPuYT6cHE5G0qzGQsBtwkUMwNQl'
        b'aIXeJMKCh98ggEbYmcE1O8MpQBDgE2c6B2CTSIRCAnyVT6HOVlIJcE/Gq2bUt2o2+T6Fp+ZwLpSbFEwKZ1AeQArQ4qRwNqWy9VR/SvXXUwMoNUBPZVEqS091N9pKqR6U'
        b'6qGn+lGqn54aSKmBeqonpXrqqb6U6qunelGql57qQ6k+eqp3bOwwlUmpTExVJcEGUYAkfpDbhKgTEQH0NTwonAg9Tg4mbxH8DwUlulrwSuslHdcLlAHjX4X+yvXepHNo'
        b'jQhj2hXXGZQqkoMJCUcfETg9zwtK+DwoGQFoWn2Rd/m/Aruuwn8B/PE/j6PGI45a14qjUNNRsOquuM2ik7BVikSmz/j3D8mKb9HXayqab5qNWNXoxNvxreRA42h0IuYQ'
        b'0kQ7YC8n3+nf51KKQ0zmU0QrnrD+IJkcIvL7bfCbYUFG+I351AQMBsxz2KrjN3OYi8NvYthEmzqQLWEbkP2A15hWuW6OYsQd6GgF/NfDJdCQHjYbHgbYkIo4IO06ZTU6'
        b'hVEDwhIACVIgAqDlFNaRNaQwCtSACTqZjE5E6bkUpJzQxcSwGXdoGIokQFSJiLYxheryYfvmITyWmhBOQSDEwSIkJpoAyYZto4AQHNNeUX5dvKI8IEFAp4DwRf0+GUoh'
        b'pW+Mt0TlGa6TLzSoXf9n1/NTZkOGQysZrakki53vKaIVUaGIK8zedoXZ4ydjOZKbQBqGk5AUjk2GpE9GDk1GNyDQRH8+vcF0GqbJl/9kWHUOtC+md/bN/Wno0PrekkFW'
        b'DJjqYOCXtxl4IPnClky0rZVgv2kIiv57DUKcxxolICtxdzYpH2PYTcSzsK+ZYP+ByW62NNlRJEF2gikSF+BWvWGUjUFD6YsM/H7Zg8SgO0PJwJynhtKrLHpoHmtcHVbE'
        b'+luw54n4zPia7YlAadiqhKWslSa8xkq3oTiEvqyAL+EZvLHFvoy1AYjXS1pD/HRkDhRzCxyLVYmcCnQXhpziVqCPCowmhO4y6/ORal1uMNtFhgxQCFQoUeQv3+V/tteQ'
        b'qLPG766vqHKvUFDhW7FaYnY6ku5OklaeiycW/p8KW5L5r7QlvIEgNDkOhJLh6qDNAVXhBwLqN6OXIgG3CLtopyAvQLzaHGKGBZ+mWJy6mDeFd2UwqUQQS6coH6J/lV/5'
        b'DT57AS+/xcvvmD42+gnyKy+S8UGTt6ZC+Te6rSsPLFF+T0becOMpxyASyhkyqKmRlX5UKHDsUbG8Anj9JeV+NAWPWnTfV1GL37ip9tZXlHv9rsT/niFzXf0vIKf/38s/'
        b'c7CBa3IbCiOiuM4FQTr/UMNpyqDDBzxoaH/oYdX9d7T/c3T49J//M+v/Y2mzQ0yxSOKMkQh7VbV4zXZI4pCeeDfmCoRLwWomxlIQqJ8laKxznKPgEe54qZ/brUNkXXkD'
        b'gGVAUdbzzEKYXB6wU5TTBHdXrqz0NKAnKAUPRvFMpbK80e9xu6Opbre/sYGkhShaQ2MYeJrgbk0o59r6r4gzpR1TVy83ej3o3445NJUAsSQLQDJ1dLJzI9dVf94XQyU7'
        b'Y9qF/wky4n/L'
    ))))
