
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
        b'eJzcvXdclEf+OD5P2cKyFBERrGtngQUUKxrFTgcBGxZ2YRdYwQW3qOCiKL0K9q7YuyKiYs9MertcergUTe4SUy+53OXuvFzym5lnd1mK0eS+n39++uLZ3XmmvGfm3ec9'
        b'M5+CLv9k+C8C/5nM+KEFqUDLpDJa9hCr43S8jilhm5hUURZIFWs5LV8KNBKtSCvGn9JCqVlilpaAEoYBC4FWkgx4oHMpmMiAVBkDCt21Ep0szVUrxU85/e5Gn+462SZG'
        b'K0mVLZGtYdYAl2yly8MBspRsnSKxwJydZ1DM0RvMuoxsRb4mI0eTpZMpuS8kGLQvpPhhZPGjnQnOYJx6wOE/ie3TNBY/KkAmo8V9KJUWMZWgBBSxhS5WpgRDaWVLAAPW'
        b'M+vZZKfvGIosJRef4TwsYvw3Af/1JpXydGiSgVIR3w5+IK9Tcgk4fzPwAH8qEpdkyH1HTAOfC2W/m3YK9AghrWwigZCtABVcJueAknkiKLO7QmmvvDOUfLxlNP4O96NG'
        b'WJysQjvgxn6oIQVVBi1AlagmZF5kSmQAqkO1SlSFajkwa74YXYCHF+prfCaKTIG4aOvX475Sf7ndrM7N/Frtrwv6RKWJ1HytfiXdOyM7M5e9tMlvYhjYmC2JXfWdkjUP'
        b'wSXyli51xXWKCgNJnXEWVQCqDmHBYNjC47qPwDrzIJxrNqxFV2ANPJUGN6PNMTgjrIObJcDdixu0xttIxlTJtbP+SqMLmW36IIkPPadkGvMKdQZFpoAdU9vdNSaTzmhO'
        b'S7foc816A0EME5k0uZ87wzNGV3vRU1w7n2kxZLRL0tKMFkNaWrtrWlpGrk5jsOSnpSk5p5bI4xRjdCPfCVnQSvqRir3xw/OBmGUZMUOePCP+mTwtw/CLMFQHj8YEBcer'
        b'AmBVgvPABoWJp4vQKU6VS6oO1L/AvCICE+9FFI18b9HepH2AItE63sxW6r/xBOqN6Qey359sQ6J70+jbhtkrmLdY4JkYnT55u4gVilzI5wCZ7UOj8nLDV5uExDvhYiDH'
        b'YH6nWBPbAHyBJZjgwMW4Ka7wZBCGpxJtTg5NEhDAP1jljypDAqLixqE6BixdIo2Ft2CrkrGQuYS30Tl0xRX3J2Yu3KeS+aNqeAGe5EE/eIuHe9b3t5C5hFvREdSKJ3Nz'
        b'CO4z+ZQA1wQWnZuPtrhPp1lGwWvwMnnTMdfTg4XZRiUZSs5CxnW6KjxGpYyOEwHxINiUzPoEw5OWAaSBvRvgvhg6nlFRKha4wl0s3AM3oZPLGYuCZDiKjsGrqCYBVUfH'
        b'BaOqWHiGB16wJGUuh4rRpRG4gf44W9pMv5iooCgVRcwUeE4E3FE1Fw+Pwr2Wvvg9ugHL4C6SRQR43iWagQfhCdRGm0B7p6ALAkrHRaE6ZRRuAG1dgLZx8Do6iK7jESMI'
        b'4uNjiRkThjPEoPoEXI3HENg2hZssRftxBtKXAngVXidZouKEHO7o/Ep0gBu9Cl5SCr1Be9CFRNdIPFX5qAbXfQPVxpBue6N9HDo+2AP3hjSFTsFrVlQTFI/qo4KCxXhU'
        b'WlilEbU8NY52Fm2P8w1E9bF4xIOUqmgR6D1Imc+hrbDY3TIUvx8PG/GgJqiiAvG4VkUFRYcER8aJQRDw2SBCu+Eh2EZnDu2Hm+AZDEdtIH4fzABXdJg1wRZ0FZ1H2y1K'
        b'Mvq7BsHLMTQL6VSifwym+XpUi9EsUSUGM3kOlYlR8ZIFtF11rBrV4IG9jaoSYuf5R8ai+vjYhPkkZ1C4aHYuvNCJsbHO7PcQ5ekVDOaaXAVfIaoQV0gqpBUuFbIK1wp5'
        b'hVuFe4VHhWdFrwqvit4V3hV9Knwq+lb4VvhV9KvoXzGgYmDFoIrBFYqKIRVDK4ZVDK8YUTGyYlSFf4WyIqAisCKoQlURXBFSEVoxumJMRVjF2IpxFeMzJ9g4M6jkMWdm'
        b'MGcGlDMzlBtjfpzs9L0n+eFhYx2dOXNpPOUYc+GewZRhFER1ZxmYYaDDEXQWZnmhBkpg8SqlClZiCsPS1UvNwfN4oI9b+pD5RLfRVlSDUY9bngfYDUwEvDPc4kvpE25f'
        b'EAhPBUWKvFAN4GEpg0rQxdn0pTe6OjpQqUKVGBXF8DSLTk8KRHtRDSUIX1QdiOe1KiiYMaIDgI9i4C1UM5O2By8sgsdiMK0FM9M9Ae/CwGPTV1l88Bs3eH415i2RGJJB'
        b'qwEfycCWCajZQgZgtGZKYLCSnQ7LAQuvMKmDUSMtsg7ti4+BpzFtioE4l0VlZn9YHGrxw69WxKbEoGqEOQeDe7gR8MMYeA7tQgLJZs2D1RTzGLQdXsOV1jOxaOswWqkI'
        b'1qYTtKxKCGKAeDy7ZEVfVCqnrGZuH0lgNCarBNzpCHbgSHdYb6D1BWTm0Or8VbjIWhZecx2N9qNdAnvYDs9Ow3Ttj5PhTsAamKmwCpbR0ZgEL43CfY5mpsEdGIpdzJxe'
        b'6CIleAXcjo7GoL3wJqlYSQhZCu+wsGI67gIZE3EMuoBq4oIAbEsDrJWZNn0YbW7cUxGY8Kpx+iZ4GNfZwqSgPXA/nTVUt9IthlA+quWBuB+7ADbJMAPcSDuHxWxpAKqJ'
        b'hOdAJAfYImaOegF9AYvzxmImGczAmxtwhdXM3OQoyiuSPRNRzdDMIFJfYHAUHph4EeibzY9ZLad9WIkZQmuMBDYEEgEQjScWuIhZ3LHtsC2DdUJ2gt+d9Rus3VQwDv2G'
        b'rcRaTBGHqYilVMRRymHXc8lO3zEVlT6ZfsPF62PO7eRNU3HC3ZCZX6lfSn+grsx6gD/5N2oj9rhEhjH6TIXbM4uDXBdtnLKjrLZWPjDi35kN4Vfcy9XiIV++ZgZvPnBf'
        b'f3iWUkKVF3TFP1sQU6guQYnqoqhWgm74Ap8RPDcXnTUPJigZ1VWYSdC28VSawSNot5lQtlsRrmjlWEyyQXGYFVZ1qDiDYSOPGkPhVVrXWMxKz5LKEjCewnqSAbZ5y1AD'
        b'nvDR6LaZyr+SYSNsWWKDMcrh5o4VAXeOGzJ0iJmKgrYpaFegKpJILrhRD6ToMgtLsVQ+ZCYstyBoMileAM+EdAgEAZgRAaIE2KiyKVxdVCCaShWgdn6lxpRDVSt3/JCu'
        b'lzLkvzsjIyqWlz2vkm/ntCZzO2cyZhhJRiPhfkq2o0r8nUyh0dteMy28AdhVq5IeVCvCBeJ6wWOESFC9GJ6BZwAfRLjAQXjo0er1eAH92Ez2NyrXmT0hH98T8vX+Zitr'
        b'IiMsu533lXrp3defbnj2vacbnrvc0NjrBfc+KzLvxUpAxET+P9UzsXZMiDoUtXnEBPnrRmLuGMNgTnCGLYCbU80KMoubMrCGLmDfBXlnnRiehTeEIWZ7nh+LWZ/rUH3B'
        b'Bk8pnpc+oEP15fLSV/Q8JVjR7euYDVKkklRDGCjY6P7vHuaDMCA/eAMdDqSaFINuoWOANzLwjrul03Qwtr9kO1xW/BXbLky8ALmvow8dHXE35KXlpWdaTBkasz7PUIvT'
        b'fiD94lmqa6Br8HoSZqR0lBLGwZLoQFV8PNFqsbrBgUDYIsLq0zl47n8GxMUOha6BpBEyo7wQ7fLG4qgmQWg4SoSOFmBNsISDtyb1fjQyhhNkZAg6YmuP/40I2Y0bMqAn'
        b'bijqnMnOiwc72qe8uIJ3tP+k3LibTkPal/VEEId9mnnTLJwwcVvwmU8eqL9Wv6BdNPiBOhW+97zva56v3IWJMFH57AuJL999IfHZd55eil5/ZdHLiej1Z3ax3mcy/LOC'
        b'su7FckBTLw/bK1cylCwkqBbuM8FzkfGqWfP87TPdCzVw8CJGvXolI3AWviv36kIiorQMTa5AI56URlgfT8zBpBilpcXsz4X9TNn6THOazmjMMwZPyc3DuU1Tg2khO3Pj'
        b'NcYsU7s4Zw35dKKmbrYjaxxIvg9y0BXBnB0ddOX1VQ90NQ6/6QvgWay1o8rYQKwPUtsZbcEiogpLh3isPsArWIOvkSRNArA6I2yaC7raF5Xrv39jFGsi5LEcvZ6TlZ2V'
        b'mxWfEa+J1ay4f1L3QH1a8wCb77JMMrK6C+KfTpxTviH06AlHztVpZJx5TB+Z2KhwZJX3NBJGT8cQkJzbnIbgmx6GgPBSeDUZlXQZA+8VLOgPr/PwJLqJTj+azLo5ff4H'
        b'js92Q3A+PkVf8PInwDQcp9ycL5Z9H6Mh+kakht9Sq1SM771L+61aSpl+1nviDWstSl7QKop5eJgK8PggVTxl6rAVngS94GUO1qvhUbOK9PtWaiDV8bFJ7h+tCob1Cah+'
        b'FpZymwOj4Dl/KvfBojRpJtYlT5kJCOEYLVoExaAe51I/1ZGvH9rOw00x6DJVANDtFG+sfwo2ujI6Nj4uGptdgrYxfJho4GI/Z3xwmnk3iyEjW6M36LRpurVU0zPJ6dyL'
        b'B4vJ3BHpP8ReRImlDM7VQRenbPjFGIc6sIDkPtCBBfJPe8AC0jd9GqoKpGZ0P1QRiWm+NiYOYwNmA2IwohArLVvh1k5TZscDIsvs7I6aif87u+VBT/JfGp9LxmLgCBep'
        b'dg5Q6Da8WpAbfCV0edZ4l5x1HBD09APwdlCgKgptNQyErdgkQYcZ2DrIh7qBPl/wg4f3+uDBbOI95mffQXGfCO6bCWEMC/j3/GT5msG542YLiWd9vMBwMJHlgdo6OGkx'
        b'0C9pShaZ8shULPw0RqPVnNSd1H2tztdUtp7VfYlJ/ku1ITPA67Qm9W4DvNzQK+A5qfebZzXs6U/O6M5rzmp8JF+yb8iHqsPL3mci+0b7XHo7tM/73LO7kxYN8L14innp'
        b'YnvYW+yrQe+wSvHpTDlFaXnvgRfjHmCmTFgbvI3xaX+M3c+BtYF9WJlpYPPQbnSnZ4byWDbDZ2tM2RTHRlIck46SYv2S/Be0TRnD/pcXyW2/+J/YYl5kHN6BfQLP7eDK'
        b'PUPBCNkoMpLCx51Y0p8eoX1Go2a0HVtUWP0EY9EFwPfB1i5qQk2Pce4yXZy77O/jRmRMXLrhnzzeQrrpqx6MtuKmXXJCQIh/JsWWvb48kC6K50GEOnf2GE5AIWNvDvDy'
        b'EEBcMNuVE4BRRBJ7eLQzafqGn5qAiSiC5Z5zVa+MdoehnrP+uLt14POV9QHjsu7zSs8+rwbM/jCmwV/hxU7qU7dZ87H3kllLbqbP/eXTrcNf8734Se1/Pkq/P3TrTY9Z'
        b'N1y9hy2v3PXqSy/kbg+Y/ZY88tru55v/m/P0X+LPXR/6tuHNvB9ffebMmRsbns3xtx5Y0fqHIZcaFq3u1ViVhtr79zo+eLRk6It+4UpXysmGpMM78A7a2d1IoxYaLEmh'
        b'OkOUQWYKUipRdWyAKsqiCnBFW6kXOmCJCN5JQBfNxOqdjG6LUEs8PGcuVNq81G6omBuLds6gptloeAAdttt51bC5k0JuVZkJZgQY4OnAYFSJqrBBshkWAzGsZ1VL0XHz'
        b'CEIlxXCjjtTgMf8RZiC8PYqaeNhm364PjCZ+mFhsey9FW11hM4v2oytoh2ADVgSmjcnGxnlQgDIYbcYaL556Bb8cXoIHKbSwwYiqBGGA2xGkwCg1NSSveMCTFNpZqBFV'
        b'YvNDMD42wFJqf8xAVfRtGhYslwPjVVF45Fji7Tgql3JSWLekkwH3K0aiON+SnqsXxIQ/JWE23J3xxBTF/iJmvTE18TbiJeQrFskYOf6PRchIRz0+PTbh66BYkrOtg2I9'
        b'X+iBYgl9k5FbF4huwnr/OKyuV8WKsVF8kYXF6DrcSZvKEDtRGDFCpXYK8+KIgWBl/ECRuFJiFVeCErZIYpWYRhZKrNwhYBU3MUXShcDgwgMzU9CfAeT/YmBwXYP1ZquU'
        b'lLOKSQ1TgJYhJY3FVlF+oB4UiayiQ2wTmAWWxS1li1yKZKR+q0sJayyiLfH4W4pVfIhronUc4mleeZFrJYfzuVrZTE4PrLKjTD3DgFVzDENpKTmGT17pYhWXMBhiWaWU'
        b'fCthaEkpLSntUjLDKjeurpQLJeywMpSvrAolT1qvK4ZmSyVTCVYD4xYMjUjLNjG2ftnzMGZxJovzHat0pfmOVbKk1i65xDjHlUoRzYE/O+fQcockWl4rKsWW5yxQwuDR'
        b'ddOKD0msboekWolW2sSSFKub8Q9aF6ubDyhyq5BUuGI1j9PKcCmplSOlitxxv91LGK00hzX+xequdcXz4G7wdKTyxh+0ctKW1b2J8SHvWK1bkbuVbWCMvhhKhkCJv0u0'
        b'7lacvy9mypkszudhGGplrGwOh9/11nqQ77Z0H62nVfjWy6n8CG0voTx9w+M8pDUPq4fWawL5dMN5pljd6dND29vqbnUj9ZF3BonVg7zJn251I7/NwpySPnjiPnjn8LiU'
        b'0epJ+qbtsxrgX6nCL1wmC3+T2tPztMIvko572Uvrg38Dbd8y1g9Ye1H4PXHrvpVupIUVMqunHQYr6WepmbF6lDCbGLOr8ImVIr/4lIeSXGyVG1SjH7JBik6yj7XJP2ph'
        b'E09OFiahZaIixsqsAI3sKizjXEptSma7NC3NoFmpS0tTsu1scGg7Y+5qfMum5OpN5oy8lflT/0VqZCmNFg7IyNZl5GDjq8M+68j4kFPkGR8yQV8QuB7K8jIV5oJ8nWKE'
        b'qRugIjulK+yAupL1YSsR0KyJrcRAlzA2oDM7QMNsMICKx9W/wgSNQfjxkx3mQeAL0uhDD41itSbXolNgqPxHmJRUzj70NelWWXSGDJ1Cb9atVIzQk9ejRphGPexFE8hX'
        b'RxJPn72dctpLP3RRrLSYzIp0neKhh05vztYZca/xYODnF54U8IfMqIfM0IcuI0xLgoODl+F0oro+7BWkyMoz28cpHP8p5e0ivUGrW9suW0AAnk1sPpyEWzW18xl5+QXt'
        b'fI6uABvBuOU8ra7dJb3ArNMYjRr8YkWe3tAuNpryc/Xmdt6oyzcaiVHa7pKCG6A1Kb3aXTLyDGZiUhjbOVxTO09QoV1Mh8fULiKwmNqlJku68E1EX5AEvVmTnqtrZ/Tt'
        b'HH7VLjYJGZicdqnelGa25OOXvNlkNrbzq8mTW2nKwsUJGO2iVZY8s07p1qMG+lseWH1McGCp1I6Or5L5ricyhCUOUZZxp3KN/UXKS21Sz9OmyMoZH5wu40iKj00eYvn4'
        b'A/+Ll6cXTvFkvPCft9iLvvPB+YmU9GR4Vow/vfAvd0bGyonjgpXSFHeWOGJ9GSxff2Fx3d6sD64R18sKkrAc3kLHsJoeGYfqp8Nt8UHRWINJ4yahHehmJ+c9wWGxnTQ+'
        b'wQ8ssFgrOASoEMrCAosr4q2cyW2V2Iw1WPKnxwJuH0fEmpW1clMwCRn9sQhkMJv3t2Jx4QcOsZhhcn6gCYsdLIp4LAR4IjBMY6x8FoPr43Hd/lhscUSYYDERhwmRiAeR'
        b'ltQn0vK4Do78wp9YHJJ6Vo0VhIwxWcvnp2iJcBZZJbQtse29SGid1sNOAfQ3b/vNTwGrxFbKkZSieEzL8WRG6bQmkke84xtJU4qMM8hkcyaduZ3TaLXtYku+VmPWGYmf'
        b'SyltlxA8XKnJb5dqdZkaS64Zoy9J0uozzMY4e4XtUt3afF2GWac1ziNpsaSw+DEY5+QWJdEN2jR7vYMYm5XEs54U4TwZGzLQqSco48t44ncEnbBKRJXRazHotm0VPTwU'
        b'VoWQFcE4uoAHAuFVEYkOmdLN7iCRD0RZpq11W3kFZO0109Vu4FiZZJu3sKtd5FCutPhRSWaaqcLifgXIl2IswwWN/TBmuOEUhojSEsYVqwZUWGGcwCKQqeQqXcn3KhIw'
        b'w2NASPMyDI48U+pwZ7pYWYJDyY8I4yEjSb2hDwgQvJVoDaBwPm6YI9+pxhSAUZ7FjWHQSpgcgMHC36wYkCLO4ErBE2PkHka+4RSWAYZeVo6mjaskOg0mA6JpVYoJ0tu0'
        b'LQw4rnlwEWel9eK8syvFGFk5rNfwBjH5jtPpLytvXEjkDyYiWo+Vt9UxEeubXljf5M2iTLYgh8G6JAMKeTxYIiKftfj3ehGJo8KkgcnSypByFMWZeIxnhBO0S1ZrjNSD'
        b'yWVhXMac1Zizxjid4Fi0gI0dTksixwXk1VLk12FWLn1iTtmBt/I0yiPzccMrTdMJ1oYSbCAYy7pT5oYZJGZgvgxbTJgnNghYHrMybNs/9JJIiWf2F3e2MFSTkaHLN5s6'
        b'5L5Wl5Fn1Jg7u2o7msKyOp0AQXqEKZxG8tCEFSTB9fdyf65dQgYQE7JQZYajoy4OgCYy9lUyjgiDQbiP/ViZX2G/R/fBrl5oSHW55Lvsd4kmjQMcia2xcYzNZaDg+GHU'
        b'JTU1JiImNj5e5a8UA9dgeEvHoqPoMtzVzf8ptX2aFuCHDqRiHEtlKf2L7S6NVG6bVHByYHJ0yRTRyEBpCZPKO9IJr5BgHiFEC5J3ogrAg1QxJVJJey9blN8cfa4uNk+j'
        b'1RkfvaBMvXosrhIzIqdFDO73LWLYWVOPIXM5SXCTCZ7zj4wLjoqbR+z7hNgoVRKqTEj2J3xzfqJqDtoiBiQIyWUxahijT41/jaML0T9ceP4r9dfqL9XZmQGfKWm43AtC'
        b'uFz61+rX0lPvfvD0tmcvNzSa4huZk+WTDowoG7JrY9hAMBq5LhH9VSkS1gJ3wyM8akG1KjFsJQFaq2wein4WHpYPYanJP3AGPNplHRq4e8HjsJQbhO70onkYtAs2dl48'
        b'Bu4cOrKEG4LbqDUTlChC5ehmoGoQaqAryLbl48hp5tn45eJoeBLdQLdhzRpHiA+JS6qNQq3CqMBqAkIIqo5Fm1EtBgVWoc2YgQOcYbcbaoK1MtsCymOYBbYL9Aa9OS3N'
        b'ydEMNsiy3bGOI2MK+3VDlWB7AccCjUmXm9kuzqVvf2WBBtPaKvI93962kbhSswixkAEBG8FGr93dXQu/BsKj0XaqgLYcpgQiQcWZYgfq8r8vGqLn9T9JPI0VWooOw40d'
        b'4ViogQPu8DTat47z7AUPWAj/DSOhG2QVlUaA2rIWLkT1iRjTbT611iRclb8EbUONYTSCEO1EW1YLhfz94Yl0jI6RKlQNT6X4R8ehzUHBUaroOCwPPVyemohqLcQBhGrg'
        b'Zbg5WbUgEtUqo+NicV4bKeGMY+EO8WBYOhxunaK3ngKcicicPw09/5X6xfSTupOaRXd3wWsNzbsulCrLTpVP39e0u7mqueTUomk1/AtZ4uYc3/BFL/tW/7nYuqOfePRF'
        b'q4tJMlNiCnuT3eG+o6z2afm+L8DnbV7nl5zBFEVWtWeuXopqCJ2IANwxjR/EwMOS9TR6Ys18WNHZsTZ5MHGtZZiF1ZuDGtRASZHSoScqdibFRLSRVo8uKbMCg1WRKhaI'
        b'gyfDo2xoPtpDy29ABzNigqPjgqJgncNluWihCIyYK0qFO1GlfRnuybVBtwyjDmugaSvztJZcHaUWbxu1iFcRIUpEqpTaDYWDu6Nsp9J20iSkgOmHiLYOuhE9WtqwAvGY'
        b'HBRkxA+DMwX5bOmBgh4HTjcycji+Z9nJyK5+EmKSZrr8RmLqFjpNGnF4BBzE5B5PI6PUvotihkzpSkycJ6xXUjnhj9Oqu1ISpaM8UXdKugjrLGSpbwi8nmKnJGcymgnP'
        b'daEkuHPSr0cyEGCxbLNFMiiZdiazqzNFOiVXszJdq5laxtjcEjywLAQ0cPciajQ9gq2jLTHwXGQcrHcgLdreaSWaG+NlgluTvNA5AM+i8l5oP7wNi3370CBWz0lwO6xB'
        b'jXAzddTXopogm/BJ4kbDq+s69UoEnEIVKLsUdHyWzLSDXXJU0vN4hjk6wzydVW49n+z0vacZJk05DBBndjkJf58jg3diyEpjsBBakBwZSMIN8TzMx/SuUqL62Kj5DraI'
        b'mcchnQzdRo1T6aLKomX82iDGE4AIdVDL3HmAsle4NRDWdapTCLbG2oMtagTP7soNLlPgbV94BJ4XCl3CA1UaE0OWOrHK4Y+qFgq8cp6j8fmEuTdLRCp0YXxvfcXHeZxJ'
        b'j0uOufHdmaQvaezbi5nBnwRoYjW5VNkISvpa/Wr6S+mvpUdptmhfSD+nexDxyduhYH4gOz+sJKUi7M/fXwrddnH+l2FjihWJ+260HSuZvY8ZvtD9rXefbnjx9advljZv'
        b'Ho11Ew6s3dz3G29/pYSGtsHTcC/nvACTBM87r8FsgWfoWg0shsfXdjBOG9dEzaiYcs4p8A6tDl0Lg+UxqG5OVx5p45D7YYOw5Hg8M8e22J1ga84NXeJk83zRWTPdVDAK'
        b'ncVziertC+LTFwZjJddrPYdq/dAxoZItRXCvPUtClAidh5eA6wQW1U2EJwXN6yw8GiCEm+A5cIXnO8WbbPb77dzanYSQpOUb88zU/qfsepCNXYMNrBe1gYiljpk2X0yW'
        b'RKjNM647p9St1WXY+GSHFdG5doENiATzpMOee9yqqG3x1M1RgLL01fixmTCNfjaWjpn6dz2suCzFb2d7w52/m5WgrRhtJmHUOOoimo3aImDrCHhKCYai7d4r0GGfXAKN'
        b'yseP/7sXiPiu9/qRf2OvjH5l2H6GrqOPG71rxCRW7YFpcMwHxgL9UkCTQ60/jECD/YXl9UWiQW8DfeC4PwLTUfzO95bXiNgY902h3tY32ZVPXxtzX7H87uS1YOnNsc0x'
        b'Q84/eG7L39u+lzesTYxZ+uqGZ/jCra/Lniv/fqJywYynRtxUvLo2IPWv+wLP9/UKe3DKqzJuxblncyO+N6TmZkdn/uz79b21z/9Y9fzuL6IXfx6efOV2Olrd3Hx2Rt95'
        b'Vz6MDZvy7fDt10pDplauCI/cevfbWR/86G35IjjVX5/56odlN6Nll++E/8IN+yYo48dCpRvFx16wEREtfz/mFN22ysCtucLqYBkqDemkw6DShXR9UKSlSkivFKzwdSVF'
        b'TIbJ2FooxwrjfjPdJEJ2UdgWEe0zCSvxpOFZxEr9VXiCNDxeK16GDsFNVO+BW9bCLUTxWaIjqg9RfGQRtnDGfildp10E+o/jPTNxC5eVZiLQFy9AN50siytYZPxG62Jk'
        b'fxoLgxFqOyy3cSVHQQm8Mxf0QRs5dBmVpVIOgEXSUdgCawYkk1AbAh0dzPmcPzq7RIim3TsCZ68RaiHR2sfYYX3WwkPoCrWo0KbluOqacbiazkYVNwQziyO0kRBYvRrW'
        b'uCb3IPtGAzPR1XxH56GaWAbu9gDMRECi+B8ZN+HyW90AIgfrcXXiGE7LslhNXG9XE2XUg0h8LzKWxzxI7MEz3qwn68MUDvxVDtRJcRTb0jr4jORJYGWNa0EnM2wNfqxz'
        b'ViIHlPWgRP46YLhpuuwgS7MlpKW1y9PSVlk0ucKyEzX2qL5K22t3I/vANCZThg5zUpst+TscMKeYdhdbTbgW2h0DfugYmzErBZ4sK/FhWPlQxkJWklzgbnha4Jlop3d3'
        b'tsmCcHhLDHcHDe7muLAvXptIPXbnjI7TCloToEGmrJYrdSHOGOpwEQn+bofDJVFjxuNnwGMXn8F3qdlhukbgh03ftjl/MyU2bYyvlGBtTIS1MZ5qYyKqgfHrcTsd3x9l'
        b'vHbXt0WC8YoaA9Z1t11PyDhPzJdalawQIbgF3fJ1zoUFei8S9cCDfrP4SLQlRMjW6IJOO2cLDIANsCVSDPqZ+PnwMNqinxhykDNF4bwvbX36K/Xiu8NjG4jNGXmltLmk'
        b'uaRtt55JlsRIciR/mvFZanm/8qFfuO/wPj5mjsLtz7rRE8LeCX0m7N1QPuwoGJ3VD6iMnuznD5W8Tc8YBI85GDI8ig47IjZSsqnTxWMoOk34JtaaN9s5JypHrULxk8ts'
        b'NnwMrKIbs9aMA146Dp5dha7RYA3YOhfzVcqkuGV2NrUWVWrs+smT0J9zuHMmxoU0Yv51MifBBlmQtxzzB474ZflvCvt3Q59gR0mBcsTtXEauqV2aacml9NbO5+O87WKz'
        b'xpilMz9WE+GNxeT7RvLYRB4lDuawgRJZJ3XE950e2MOvwahk44k/nDAIYwF5FFI+Sal2pc6cnaelzRjX2Yen+1qv1QHQevw4wdgsMSlg2UEM9XssgbVjbHS9GW4nyCe1'
        b'b+cTtvJNVojhCf/l1ITYFcWCsZOJ5qXOzcpPA92WYDpTY6dFGAc1Ahrb+Du2pxHIHSa2gxr94qnLJwAWe5qw2nDZdZUFy+ZKdBU1m1ejVtfVsM4jX46aAXgqyg8dF2E7'
        b'crvc8hTBy02rdbhEVWw8qguMn49N4sXwJOZp+FtVgsq+7RieQ5VBwbA5iWz7g5fhdRm6g02Cx+6V5mjUx/8YzgkexYAI5U2FVVwgPBnrYBu+eNR7p3CoBrbyFiL/fdGe'
        b'xYTwhB6i7YHwlD/j4Qn6wUbemLVWb927kDOR5b13Ykb1qW52Kw6V8x8P9t/Fjk5ekL8xuyFJW57lui65uf2Tb+PXfHKjZuMzc1ctvfR8+rz2v30y8vqklvl9j9clV55z'
        b'L3nv/oOJ3w5+fr9XUmm8UkSZBjw2Eh0JhBVwW7CSbA3DbOMsG5ZfRPeWoMZR6GQgQbSx8Co28icwWB85qKM6zfJJLHU4oOqCtapIyos84EZuxTSGhsLBMzOoylNNdSx4'
        b'hgP8JAY2w2Y836Q4VnjOh4+FWx2xYzRwDFWglsfuHHLV5OfrMPERJkBZi4+Dtcjn8dRHJaXbiPj/FAZgBpGWq8/QGUy6tExj3sq0TL2zqeNUlb1dyiJ+xdHLCDkouZbh'
        b'xx868w/Piz2YM2TZd850dDwmQUWUTftUw7oE6hrAn4KYdtgwAetsVoxtfDDPFsZYCw94rsQmbTVdepkT7RJIBjhsPAtUqEyEDjDwMjowj6IV3LxyKiac5jVw69TV6PIq'
        b'uTR/lXwVD3wmc1krYCXdLjpmLjxowhPV7OK22k3mLkWX1hDqXCUCw+G2Xl58Eauh8aoTQ9DRmKigdXEBpDkOz9ZFFqv59SmWyQRPDqrC4Bm0FVNzVWxAdBAWsNvWBPkT'
        b'b0OsfStNsjRYhY4OoXvDGUA0ZteZS+BFWr4I1aFNHcVV6PajarAX35ErQ2VwIzpKuaOrKADW5K+Cm9egK+gq5i9mrCZfxSzkqgV3JCw8mcdZm+FuYQt6MzwwOwwrSgTg'
        b'nTHErsdyMVYCPFAjl4TKNYKjuRUX2NOt1jWoWS4T48G5MCeKh9VsIlWNLb1IvXfg6aWwBWOkImoymGyOpZt71LB8DtqaoIpCO+CFyCgJkC9GR55i0YHx6LwljDS0G21f'
        b'5KoiGyVjFgr9xaNRAS8IvA5jBWylTG0Z2iiBN+EVeMZCQnCksAntS8bM1i14OBg+II5yfpErVgmtb4mAWp07RbRcCNN9d6EYyGN/YoFCLV/h+RTWkWlyxmgW8KGVuAZ1'
        b'0AljtJB3OWbf8olpYpw3F9uagG4hQedgcwqx9QKJL6mK+o/szOpQbmco82CxtAjj4DH9jdt/YEwRmDiy5hyLS5wcjyK8rec+yJtWv3/i/d6Vs2ZzkkOHm5hVXIOn6MPe'
        b'OzZ5v1jPv2ooabyUMmDjh8F9i7cE5oPCZ0avzRm14HLqX2uzPsrOCvO/12fpGNHmUkble7J+l2uI26yP1H2+/+l15YUo312hM3fpJVNHuy2vFAVtWRe15a2YFX/8x/Gn'
        b'3vA4fD30WnQC+87XX6+98JeWN5/be+mf1/9YmqBcsu7Ux2vrb5x6ek60+TNV2qmZ/UT3w9pla13WuFydzs0LydrXOnAes2Ci+h/WliX/ePbDh5dbvv3MvG/dy+fGvuHB'
        b'LrJwfPVC1b+nfuHyyscH3+v7rirviHVQ+pfvrTjy34ZR/zo71Xdz9s4fpr18rNdPqeHHd8a8dveNcP2surGfffvxnNc/Yv4VFDEr66dbm7bf/kX6dtrnZV9OGDlv3R++'
        b'/etPJ3ZH7HnGfdzUjAU/cYZRlsnYbPegFnmCfFIMHnJs+hGWwQHXCFiKLnEsJqVKMwk3jYbb3AiDuZDOAHY1M501UyYOb6OtqZSJA3RpnY2JH14jcOE76FZQTGxAsMBc'
        b'XA3odC6LjsK9VsGyPc8TlTAoHh2Dx+ksk6W8GrYI414TZfOoYsPYwIQg6rGujZEAV3QrGd1m0dUMLVUqdUNQPWZhZG+fE5sPhVXUvYbOwi1BgagyKiiKShIRFiE7UPkU'
        b'LhPtQ220115D4MEYsmyKq1eq4lWsD9wF+sbyEWjvStqF3sHIES+NMRVtpPHSmDmcowAMhidGUthQjQS2eQNeRbZ5XoC1dGwGwL2oOTA6LpbB7GI34IcwcD88GEit8v6Y'
        b'1dgqJjwZV6ESe0WDvvAKNghaFwk6842haEugTXLCnfAAlZ7wyBI6OMaB8FInF0o+ukYV9hnmxzn7nszYdTbM+/Qo6ah8JM40lhEkJD+HxJHJqZTEhjork3myXthUx99Y'
        b'T86T8WXtARRyuhlXxgz4RU7jwVghAu2fcldPlpfIH9I4sl94kfxnY7ldQJ9if6O97hTmSCp5tosufr0HWUpc2zPR7TXdZenK0Z2kqQgsN0vhdrQbnldywq4LWIu22Nbs'
        b'lGg/oGt26Bq6RRU1XNsRdBLVxMNzscJJGq6wdeg4Fh0LQJfp/v+RsD4hECNhgBirSYfYQlgVBiuSMrguaqCPXRVcjh/dzpUAjpMlmE5nS7AVfTJ9HAsToidamMhUcveH'
        b'4zmWKZz+Jemy9CazzmhSmLN1Xc88CpZ1yhtlVuhNCqNulUVv1GkV5jwFcf7igjiVHG1Ddswq8khAabouM8+oU2gMBQqTJV1wg3SqKkNjIAGj+pX5eUazThusWKjHxo/F'
        b'rKCRqnqtwoacFCp73fiFuQCD0Kkmo85kNuqJ77kLtOE0FEdBbMBwBTnXiXwjgaukSlv1uIc9FMnRFZDgUqGU7UeXglrFajxmGKYeK7CY8EuhuCP/7BlRM5PpG4Vea1L4'
        b'p+j0uQZd9kqdURU1y6TsXI9ttO1xtRoF6aMhiwTVahQk5JiAY68rWBGfhwcuPx+3RWJUu9Wkz6SlhAHFc5WuIQDhucJzY8ow6vPN3TrSzWXiDrpaLK7xFnIyilcCKk0O'
        b'sS/BJy2MjEe1yZHRoqRJk+AppQy1FUyC2yOGTuoDUANW6Legk3K/CbCmGx142htI6kwHwEYJjIMS2AqPTM/fuCjXzfAk/KT7uSiqeJyPspnuMYTdAypsninHCuHv3u9J'
        b'muq+w09k2x5ORkf/XPsFkYkEjRQ8FfqVWpUZpZFnPlB/oV6Z+TW4NF0bPjMso1+y38zGbMmwyJtbx21uKxk3MHJNqCW0eNYev2W+6c/mPP1whe9wv7uFu/f4xfjVmP38'
        b'7o7c9E3vZ/uGBvEtub6yv4Qv6hsarFVrH6jFuz1fubvbHZSKBm4IMNiODlgOd4YGqvxphAHcw8JNsFHVC5bSdx7wEqwPRPVE216u4y0MqoJ70I7fvlYlSltj1OR3WaLC'
        b'cmgEz/hiCSJmPRlvzOK9aNxyodJoY15OQXg2NHdKITXajiEQYl87hM5jADvFCAWoxMEaDxiKITMNcEgcsNHngx5kDvFDrEK3UgLtRIGw7dPDNuoOcTTbSxkSjZWCOfCk'
        b'h37CzMeEoHHUCfPb99F3QzsR6MkTIYm3kIjjaXPHh4WOHTN+9LgweBVeNJuNq1clu1lM1FS6jC5hM6cZ2z0tHlK5zN3FzRVuhpWwliWHYV11QedGwjPURjgZFU22XUsP'
        b'9V2/4gNPqWA45BRFggYAQu8WmqN/1E2xofjH42pYqn7EtKzu83xTr+JQT/7ujT/sTQHS8swHwDU4TOr9YEOfWS9Fho84uT/OvC9/R+LR0JerMz569tmZG6O2BH343eS7'
        b'b48tizl4LPDTDQt8Y0eN9VoTm6rPfQd+4Pmxx5kXvKf22Y6xmQh3dBNe88O6ptnL+SSMO6hU0NQ2oxLq3qwWDFg+aQPxR/S2/FpEyuPDy4x55rR0Yn3bFxjs6B3GY5T2'
        b'pkhNAvULg54IsW3V2RdCHHHdvx54RnN0oDU54SK0K1p7vdYDWpP1MgXajzZ24PVjcBpVh8AquA9tSxgzngOrYY1nMCpdRTHg0igWLIoggKpjd3KrgHBy0BV4AB1CWzE2'
        b'BKMDsBUE+/gJPso8CYiNxuxaoQ5aZAgUkCh8lAi8vrY3iX2INQ4yC0hE37yW6QKCfIbhutVBiamjhUSJRwxI1AUzwFMdkJAcLiRO9O0FXjBEAJCvji0Z7AVo0M2UcO9k'
        b'bFVvmz8uFFXz8ACsBOIkBp7tD+tpoZ2j+gF+cA4WWeqlJ136CjUl8ReZYiwmvpscq/mX5q/+VAVUDx+WDOvSY3FdqE4EODUzNQfus5CjYeCRRdi0qOnwVGKzBVUGRRMf'
        b'JTFhaNgFHs1WYyAxtmBVoEyZL6Mry+JEMcCzpXg9nJO/v+j5gIWA7gQfqhsplS4GocdHtK3a0f+a4bPE18Y/1L7I0wOiUC0swbZdC5Y0cfCWGsSha/A4BfyP/SaDv8//'
        b'mvTG+Ldof6E3M1ymgVIA/CMm5aYZC15bJhwQWDgN7FrwC8YXtVfS8Hgh5zP9VIyaBZ53J9XqoobVCIcF6t3eYS5zIPLuBPmqN9iXl9DEjwxzmW0siLg7LmhdQr/bRTTx'
        b'2dQ+DEG/u1NrC0/NP+VLE+ctsoDv8GfE5NysNaOfDqeJTVHzmb9nLhQBT03MvgV+QuulCY2MP4cZSVjsyMt9+ypo4s+LFoFruD8RT8mHu8btdaWJ30wYysSyYOLdqUFp'
        b'X497L4wmXh86CMwi3Zya6/YBW9qPJp73jmMOkR6Nq52+OznFSBOnKXyY/IilPMbAZcOYTKH1n8L/yOxznS4Bak3CLt04IfH10GeAgvXhMFpG3QUaIbElugj49v+BAYnq'
        b'1dr1I4XEz7gPwKGZJg4nTjqxIFRI3DlJDq5FYrMlUR07ca1KSByxOB8U46nLH71izfPa4ev013z2A9MenPJT3LT5iVH1b0V4vnL21dUhhvJn6/bq3ttZwM1dHjHYU2Jo'
        b'OlBybEf2sCGJb79YnBOcfUBtulf5mcfNkgn59xmtn4vL9n2Nvfq89tIriy4XXP7b9pXuHyUl3PqqZf1HIQ//8tr06RtemZkUd6dd77vo/k/3K04sMlsXPMOeP94yY63y'
        b'pvflTePbj3qU5u577+4Lc90DdMNEqpNz0v/207vK5l3py9/cE779razS9xWvndr0/ddbwyVFSa0TLz7Y9lbM9bUXf0p4d/mwjxOr+yjvPz3r+3HHv3nmVbfWZdprc0bk'
        b'TkOiW9OmK39+uzxfv//npfNL0+Mmz4+689GA4MP9XoksebYxNv3Wj1fmVeSNHjwgeHNQy3tflP31TbeBwUlvT6yZc33rgXzRwskDl751rVyWs3RunZvh3kjD/fH1qyRr'
        b'Vnn8U7dFsvx+U+6Pjebv3+s/ZdK5jH9vT3u9r2z3hG8SIueG6DdoH6wMaf3x577J4Ulr3l/1An9Qdn3h5c/XeH8+8Yt/Tbq1esjm9qwXv//s6pqpOX+fdLVFeWTD7kmf'
        b'I/bysSqlZnvush8vvbkkunDVQ0nkveo31xuUUkHQtIT2DwyGu9AZm9eBehzisUAlilOfdaglEFWGoDaIyY2FTUwixPKVvitAx7WB0aoYVUC8CJ0MAnIxi27xw2wOc1gt'
        b'cpJPk2AFKsESCt1YKrR6ZjQ8jBlHPNydEAXP8uRUu6FoO9pKS2ejawMCg5XRwnmSIuCBisOCuDzMI3YJu8FPGeBVJ0eNCrYBV+qoMU2i3o41qHEyiVFKgWdomJJzjBIH'
        b'd/zWkAHP377Y/cQapdQuOKnUzXaSuvIhPOPDerqzMvumcHfbWQ9kz4Qv/u/FDMBCcADL03N6ZGQbHOPF+WBJLWPYn1lW+jPP8TRmijhA2J/lnAyX5akjhP+lsN+jpbig'
        b'j4roFpd2ic3EbBdRu9FJfP/vGwaxzruZfKd7aRocUr8OPwZ2lfoB93uQ+iRGMSkW7XsSoT8BHgiMFwFYAbEGeBNts1Dn+FzUirPVCA5hLfUGY+HW4TcJgZdF6OzYVLoA'
        b'34uZYF++Q6fhxsB4Gr7qicq4QbAthDLDtydhhs/Kqepwf0aMwCGrxvEg0tWHKAO5oRlDhMQ5wyXg5tQBVG2QjPcF+mutkxnTEfzmw7KIcbVx7psi5HOWiMs1YMPo51zX'
        b'Mps/SXLbW84Vx1juN1w2ud461efTT0Z88+67Cda8CxG+31VdulfqdiJ30uebYs6vfc60/Ps9E5bFuez+o+hmyVto+cS7+97wX1zcUmUxN7d9MXvf2Kdn/QK+R9OL3zjV'
        b'VjhEd8k7YbWEufrdnJQb06q+CrmTcjHu74OXHBn43vGkFQc2rPxwzP4P/7xo07CflM95/I0Jafz2H0oJDSyCdegaaiFHGtsONEZnZnY60xjtXih4Z6+GwVvoENagbA5M'
        b'm/dyn0wIUNoDT+Wg8511NBLtGMuAfvAAnzca3RDii85J0HV7piB0jOTDPMIrgIMn0SYFdcVKUSmNldrcMYvu8DxqGMLNGgXPUnBEHiRsLEQVr0LVsUox8BiwAh3k0mBp'
        b'oNCtFnh2Jby4GNYk2BQfxyFq/WEjD4+MgPvs5qPP/3P28MTMw07BlHkEOTEPfoCUYdmRjHwODZgUdsuyJIyJHEvkThjGf4xbHLWRzbnK3v/XgDc66Ju0LOlK3+P/+Yjz'
        b'ZdA2f3haIPDhhmASIOAxnstEZeYe163JP5Oc6Yj70TKpnJZN5bVcqkjLp4rxnwT/SbNAqgv+lG3jtvFaUZ1w/ByJGuC1Yq2EbsZy1cm1Uq1LKdDKtK51bKob/i2nv93o'
        b'b3f8253+9qC/PfBvT/q7F/3tiWukrlJcp5e2d6k0tZejNcbRmre2D23NC7+Tkv9anzpyFB05m7Gv1pe+693DOz9tP/rO2/a7v3YAbqGP7ddA7SD8y0fL07P8Bre7xwq8'
        b'PU5j0GTpjPclXV2txB3YOY+Cxn10yvS4EnoT8ftR56u2wKBZqScu2AKFRqslzkGjbmXeap2Tr7Fz5bgQzkT8/TZfpuBIdPgoaYlgRWKuTmPSKQx5ZuJ/1ZhpZouJHILf'
        b'ya1oIlkUOgNxOmoV6QUK2w7kYJunWJNh1q/WmEnF+XkG6jjWkRYNuQWdvY3zTYIDGjelMTr5TKlneY2mgKau1hn1mXqcSjpp1uFO4zp1mozsR7iDbaNgazWYDqbZqDGY'
        b'MnXEe63VmDUEyFz9Sr1ZGFDczc4dNGTmGVfSgyAVa7L1Gdld3d8Wgx5XjiHRa3UGsz6zwDZSWOR3qujhwGyzOd8UHhKiydcHr8jLM+hNwVpdiO0Q+Ycj7a8z8WSmazJy'
        b'uucJzsjSx5PDK/IxxqzJM2of7SSaAmz7FOmGr0zRb9ypmK3kHpZ190Yb9Ga9JldfqMPz2g0pDSazxpDRdb2A/LN5xO1QC05x/EOfZcBjOD0xyvGquwf8CU5BFQuRQtkF'
        b'6EzHjhZ0HpY+cnPYDHSF7kePwtLHrpUQlcQ/Mig4GG0OiWbA+DhUB3eK1+VabEeiT4G1qJwcNj0I7khQkV0VdQkM8IL7OLQRXYI39Fe/mcKZyJ79P+/eSzaQ+aeTZ9Bn'
        b'X6ojbZshgn38NdEatsWvb+gal89DQ7RL715qaNraVqKsaS1pKxldoypr23mqZMSBp8h+zBYRWHe1194ZJ7AVQcIQBpGQZSfJHejZSXYPG0TFshU1wgM456blXSQzNysB'
        b'7hcMhyO917viHivjLCqZWNAj+sAKXrrGTwjiqZ22PBDVR66Fx8fygEM3GAM6Aw/Rsq6wCTaQUYC3p+JRYOiJa3AjqoTXaVm/pagM1cSoJIBFR1ADrGdisA5QLrR7GG1D'
        b'B0nNqMV/7JhxHJAUMlgnOYaEun3QLbibdrAyLlYMRHAjvIDOMqht1TT7loInWBUkgbVdgnyopu9NT9nEQtmHKezbGXc77+E8JcQTG3cC8NhNC6dYIVvnTZzVrN13vdH+'
        b'3/uHHoIEHwXGo7dbEfisYIV9w5WShPval7FOMQIYnbdeGS34sZu1HWErBt0ate/Meuj3yPUx3Aynzct4IrBKBbCkaTaDxrjvETDtw/AY9+MvD72d1sjsS23BT9RYpr0x'
        b'wm71WtMjGzvoaCyINGZX6XpYksvI1WM2rjJhbq58MiBsPXZN063N1xuppHgkHIcdcAwjcHSUIKKo68B3bt7O3unhkpS9287SrRA5sfffuQrQ6UgiZ8ZKiAiWwN1oVzKq'
        b'48GycABbiWv8iEU4zv0ivLwWnmFIRFYN2geKEtBe4YjiQ/Mj4FG4C9VEUaU+jMecooaNRtfRNv3Y7CGcKRXnep9zH1jzottdhZxf4zYpW1F3TDRr+IrQC9alfzaUfzHW'
        b'/cLAutVBu803rRMP5fcb+e+tKak/jl2lSn62RezmO+7n5jcmfDxKvH39rFXvjG1bUbh46skX696Y6tnHj922TCkT9oldRXdgg51pxsOmrhZPRoTgK7mzDNbkTiRO1yhh'
        b'LQDdYGHVU/2pHbMKtfbHFumJLqGH+9FlYbNGC7yE2rBpBkuwKUacKXw8Ay9K0W4h4mUr3D+E+Gni4Q27q4YENp6EFfR9P3gVM1Ub23OLw4yPMj0suY5TlpoDrzMk6KwV'
        b'HQ8hF5/w4xl4c1SisEhxYWB4BLpuO3fdfuh6C2wRWq7VYjv9BjroOCRTOCCTLNlRM2+LN2qkp/RH4uGh7NwLbmHhGQ6Vw1ZRpzP3noT3YkLUGTKMBflmyoCp3dHBgJUy'
        b'enaQ4ESha3fd+J+ttPO2jic7UdN22HEHGyZHah7rgQ2/9yRs2AbG/5l2ldWjdjUzW2PI0gkxGHZ9yM4RuuhaWGV6UjXLoFvzpNoV6W73Pao8Zm40OhQ1zUTX4JasGAFX'
        b'OilASahVn7daxpjIySGfZVzs88oQHxjqPeuPu39K2yPzedrr+g5Z/Py4FP44++bpoWImd8j7etT2+fujfF4I+HhkyLbtifPaZjZkTf7XjW8/2FWE+j4z0OWjAXOmfFL5'
        b'jx+Hfz/hqrfxXfedstH/rDqoSEuHpfctM8ew/zrqs3TtJ0oXQWWpmoA2Ec1iLI/aJgg6Sxi8IGxMO45J4A6sSSCbYeHpIH8m0B24ozpO12cBDVpLCYNVaZO70gEhAnQ9'
        b'jFafOt2V+DFQNYNVlGOAD2EIXQ2jLGYOKplKjrYiV3nAupBIeCDVoUSGokPiSVNkdLeVyArP2jSj2QVUL6qZQQOqNRi8W2RQPZc6aVTuVoHAb6F6CVWZ9gZ0qEyjYL1A'
        b'4G1Yby13Upkw51iMDqI2IPntxOuRQREwzY4tPShRsnB3Ggk24Jd+bOGgLmTTpbhQ8+5H0qxxj4NYT+LHxR6I9dUeiPUxrSq5dnF2nsms17a7YHIwG4he0C4W9INHbzKi'
        b'BM07NhiJHBuMRE+6wej+DKaLqU/+TddqialEiNBJ0RDMTIeYfyQlCx0R6DgSf4+aZecH6RpDTndqdjAAW7+FkonCT1zYP8ZiwEaqKmpWD6FGTmFL9pLEJCfFOoUpKXuC'
        b'16gzW4wGU7hCnWK06NQk2kg4UkEbpFDP0eSahDRNLk7UFmC9h6hfBvPvYkhcvL7o5UyRiRxp9t8rs75SL7/7+tPvvV/39FtPX2po29FU0lQyqaZ5d/PBqzuay0fXnCpv'
        b'2jxk38aqIWUbRdK9u/38NvnJ/ap1L/n5+UWEelUmF6fv04PYV93mb9mo5IQg1j2JGhu7QHcGUI4h8At0EVsqhCLiUUuyjSEs9xLYQT68Rnech69ZEBMbBasSVknjUHVs'
        b'MKwn/k8WKGGtCJ4jltJvp0x3jVabpkvXZ5iooksJ06sTYbrHkPWH4b8UDuxCHp1LCvaNWJCTp8jjNHmc6SxinS/m4J2y5TvyUqo9hx+3eqDauz3tlvxVsP5P6XJuT3SZ'
        b'RH1kmDQNAi6SuDonAnXyjv3/j0RJsajkBIXg1zILbjBqe2TqDZpchVaXq+seDPjkxNnqPYelxOlpUdqI04k0D//zNxLnFyD2NbcFEW6YOKlhcUMnd5blwB2eTCTEuQ7u'
        b'E/YnNbMJhDbhdSUmT5usboMXzUry8gTci8oDo1EdqgsZC1tiYF1CJzKdBuslXvAY+9uJtJfgd30Mnaba6LSLRhfcrbBQ8/ku9Gi84CC/Zvx4pQfya+6B/B7b2mOuMGIq'
        b'gNMVRk92hDxxIab3QHgUCymFGCwr0zGxYcRz8lV3eIAzLEYjlhG5BU7m+u/FybhDz4pMkThhzHlfckvSxYYmio2jH4uLI152wsUhy/Xgvb+4nk25iLGRjLsn1rxuUHTE'
        b'qliVAyUJPqagcoqPobANltmEBcHGaBeMj1fgVTPZNg3Ph5ErDOpDSKwRLCOXjTihY4AY42ObRIGuw/IuN1j1iIEZeRaD2WlWTT1goDT9ERjYrbA9XjL/kdJBcHNQbGzB'
        b'jz91x0b3w0+Ajd1a/j/CRsMjsbEjnvqJMVHhH0C0Or1BsXp88NiAHrj1k2HmDN07LMXMe9n3H4uZ9/7zaNwUMJN/3cYnn4JX0BmBUapFzniZBK9QvByI6snVAna8XD8P'
        b'80m4GV0R+ORlbPzcEu5dxDiJLvp0RsuJsEIMW5aj4idAS08yto/DyhU2rBzcBTe6lhXqvfxoRLyCH5/2gIh7ejoI7DGNKft23aQtSUvT5mWkpbXzaRZjbrsbeabZF2za'
        b'XR3bafRa415S6BB5HCYPcuQLdQ63S/ONefk6o7mgXWr3sNL4jHaJzYvZLnPyJBJHBjWQqL5FuT4lNtrR331OhJNbcit+WMiARVIU5VnelWc6/ktZb4Z1EzMsGTSu508v'
        b'Xurqzcjlnozc3ZNxd/eS0tUVdCB2sCOQYws6GBiPWuOwmYwtbBb4w42iDfBM327rO4T2I+wY0nl5mXp8ufbeth0qttmjp3o/VMxeS04bJa7UDLL9xGggOp2TDhePzdDO'
        b's2m86hiJLq7aO/jxFevYVI/HhKGHpg2ChyQdBwxhc8AWQ2G7YRodR9UgWibBZHQRNVrI0ZWwLTOsWwi1EEBtQpueIIYaXUNXuvFDVzsnIXNm24YAOt9F23Ei8u+9z5s0'
        b'1N0nLI9XckKIZIIMkNCee4mBubs0z46nYakX54vBgIh8EZ5B+fuLXpX+F+SSqCPJ5CmiL3zbsn6Z3V/ZlpOYdnrwyZzrizb574l/buLYxXVB+xPOTT4WvmzgmwGH0/8b'
        b'9DBug9tn/d2Kbs6/6F86c1z05/EF0+8PEveTDfhg0YzUT6feGLkvaVpK1cBtATcHL5kREpW09l2P5rxvxrZzjQFJ+WMGHBv32awftQfml7uODWpjI3r9sCJn1mrZl6bV'
        b'+f5935992tXP7fqGX7Ch4R/ysnBjciY8Ee1wVKNr42y+arh3DO1pWi4HrGsJYqhzG1KDhLiiAaG9wd2BZJu2eoo5cbyQ+Ka2LzgbuJwEG03RJS4Hwn7dU6gVI02cKphc'
        b'Mmw/VA1tjpGgRniqAFXNhttFIwAsHekCm9ehJnhVRit7TiEC700WznV7z8sstDC1lwScNPiSFmJNmlThlN8rn6SSmWMUQwGTs07/0qSRHL04B9XqR9Q1uyOFfNYfdpUm'
        b'WjxOxvxy6s69pqSrJ4cF6Vb9wv48ds5ia+Gad/YnlgW/VJjz7bXANZX9/571DxH0+2RwdkrUwr/MKdNG/etfn/57xOL+/32lbQvv4vL2qcDzf5ye9vbhJRP2/Hxo4EuT'
        b'z+787Ko+5UpZg2bNy9m5y3ctzlpShfwy/ub6fRG7o3Rktug1JS8cNzJ1iN0RjSpQjc0ZXZQseOprUCM64IhxGmfpcm17MpZMdAfoMVSag6rhlUAVuT2XDKQIuKLrLDkY'
        b'QiU4A3et9AlE1QEqeBuVBjN0590kXtE9EP73nsHsfLSA0aTp5PQmPoAOucZbZdTdTRzenqyCclPy3fi0vRpyJTwJQ3DSsH4vWKcYI3KwMNLAj93loKKih/gf4t0dtgg1'
        b'BgbEw1qHadVnMAP6w/08PCOGe7qxIBc7Z3A6E9OJBTnOxPzdR2T0vCQls7OfI3NdKfvxnPNnzXtjx82i7OfdiTQqXnoxCrMf39Z5BoH9eHs+9f+E/cQOuD26bOzzRavj'
        b'Jo7Y4N97sv/8tdOu8Glex/IvDE5P+5P+smTo/KNq3cTonFdcvol6KtCtb/Yio6h46Gc9sp+16//rQbtyU8alR7NSyl+emeUmEHr/Gb0nhjCRlL/0yvAHRiKK6JuRw/j1'
        b'1ZzAF9wm2HbTuOaJzWtYgS8oLUrhnlDYCKu0qEYOyzovwsGzaLueuXeMN63Eud4OCFC93OyGQuX83RPLL30yfv+9+ZfKFio+OGpauXBG8R98vj/eBCYM/5eu3z/Nk4dU'
        b'fng7xe8/xSfEn2+a8M8Tn/eJvjrtmdff8DSteFCbe/1c9aAfqz42nJj95oBPZS8fPnvivyN+vvePfkXnd12dFnBkYNTYlUpGMNLLxBEx6Fi8/QZ66TJWh1rgjk7q5G+L'
        b'IO5KlFpdB1EO70SUmCw9pOSuCkqOhDDlQrguY3zWURH8HRA846A+Uo+Us13v0kF9YOOAv/dAfyQTPKBaJdBfVBwlP3QGHcMEqOZhE1YSqrttXCR/9LDSSEyalSLhJgEr'
        b'cwgQwmtii1j6ndPy+DtnZsj7WWDZpqVsEV9EbhsQVQIzS+9NGlcosYoOcVpRE1MkWggMOeSM/4Kxwp1S9A25bUq0GBiWr8FEa9xCS5OS862ccQbOIWoS7pUS02s63HAb'
        b'4iJJJWOVkLsItJI6nN8qnkJui3qKlhXhsiZcVk0uxcBwizB8IgofKSvtVlaKy2oNg2lZMb0R6snLFVeKhbz4N7CSize8hXsX6C1NTVagdfHDnMUqxFTI4jE71uny5xhn'
        b'4rFNeSiymDNVE42jADU4niNzS14YyR12xjGAblrPIjjnojNYVuqM5FKOOeS3mJysr9W1y+cb9OQL1VKFsjME1Oo4GbOjWnrnAd2YRU68N5LjfduZFb/1IC05uRDHNEbY'
        b'L9yPsx3bJOWETfzutsth8OcvPL0shuw48yZXwrDO34Vvwk0eJHaGHv+Si2rR9RiMn1Gq8QHkGAOyNwCVwCtAMYhHzbASbewWNOE4JpxQvhUzcy2TDMidXnQWWMdlGXQ8'
        b'jeH2vpCDhE2PsCndaA/TzHlpuXmGrMmcTVUnofjuwlUjhumzKJhoN9qownYrqhKOZSR6FxgJy0QFVnil27VMjuCysRRULZPDGMXE8NByVnKZFqPlDwFyTRMGXOQDmhgr'
        b'0xcQGUdSqHkitnWDgPOQHbGW7kj7ghX6IyrM1OfmKtl2xtDOZD+qb6RLpGu0jzNI32R0+oTbeKSMhdyDMhSeIZs/SH9gObYsNtMeJtCZEYORg0QF6AI6/pgNzEyPG5h/'
        b'5xWRjHP1TjtJO/bkDXRbBe4BMDE07CPTF6HThcS77LMYGYDi4qyMuZdDC4XEj8eIgRwL91BxSO8XlqmAXqqbyNCLW2bf++gr9TLiJtnaWnKqpHX3H8uGLLiyo6m8qaSp'
        b'tjnycomFyXCbKft0xvH4d2bU9ysXxbr6Vc8fcnhg0MBXxslfrVXGekV4HWb9n5OOGVG2WG552/9K8aQy3ZCMUC7LFQTn+2X652J9lca9nFs9VdjtnIhO0Q3PqlGo1Sxc'
        b'RYM22a9KRAcyycEP9KrEOnhQ0FLL4a459ByUqli0OQgeQU0MznOGRed9oHCeFdoC9wXCM9HEnERVDDyJ9gLxenZoeu/fvmW618o87aQJwuUjaVp9lr6nAAywQTpPTiPg'
        b'hLtOfBjj245qqp+kwRp7g7RgTE/yzacH9zM9aFKJu427WpcAm9G+SWPp4cfkOihyxTAdIwZMhCfE6ycveDT/IMcDCFyDSLkmgeDY+HaRxpSh12P190Vgl8LDOg+QJFu3'
        b'NlefWTCfswXCuXNUQxo5Komu+9MdKfAMjy2JsuABLLoObwc+Gg4yw+SmHSoDZeR6KgJNkQ02G1TGdwBVyWfbYfq1E8pcLAYbhKkEQnpTEEdiZYRTJPejE8mBqK4TqCZ4'
        b'gh4Ktx9thdW/acyy7dAZ333UeLmkjx8r3K6mwTUZ38dpdFssOiZJiBkTFuW4dPdQKPAYwk3uj3b+D8PVAVD7Ew0WBk6QrpkEuA8IcGQyU+AFdJNAZ9Mq4cYhwB2d50Zr'
        b'0aVuoXSOmwLJsX5aBnN2ojIBYx8z4ftcCYsVClDECTeHWdm+9B4yk9jK5vezMuQeLwq3KL59eOjoMWFjx42fMHHS9BkzZ82eMzcyKjomNi4+IXFeUnLK/AULFy1OFaQA'
        b'vSiYKg0M1g/0qzHVKvl2sbAO0i7KyNYYTe1icjJH2HhBFZB27XnYeGFaVnK2G37o7jPhsref5RydJHg5CV6MGTPeEfU1Cu4DHn25cO2qR0+S3IYnWvvlVXhK7tlbxxzp'
        b'kx6xJGy8MBFrONux/jKOelR0qCKeQGCbCbUST8RRLhS1rqYQKkLgkcD4OHqSGrkDCF6HFyA24S9a5jzG98928v3/TtOy57tLRCTQiUDXRwbPCxutVOTYU4BOz/JYyC2B'
        b'u1EjPUhNEhCLrSgwPgYsAUtQuVr/YKC7yERUxPtPL/9KvYj68F+PbCofUtNcMrqseefosqh95IIdN7AkQPTFzf5KVojeuYWu5JKbuevRtT6oJkQCXMJYrO1fRKeF8Lyq'
        b'VHiGnN6FWSQ57CouiIEn0FnQO4RD2w0OMfEILUJvyksz61fqTGbNyvweXO5UIHCeYuPnjlnm2qW0ROcLOJxNMsb4wN4CLWfl7C6Pjc7/3X/pQQoQrSwSluJhJF3C2tg2'
        b'WBtiG+YoVKvC3Ngo2oCq0+d0C7zr7O/kbIF3Tt7OCsbh73zSGNhup8GQIfDohhW9hBhYtynodgwW5/UzvVAtD8T9WBlqMFNdpT2kLwgCUg8XhXrA/sCxtlvXi3VwV1i6'
        b'aQxsHhMKhgJJPAP3wmujBS66C95GB8MkmjHwyhjYyuPXcCcDr8BqmYW0DhvleFy2igA8PwEEg+Bw1EZb+iTLD4SCiBGcWm39Iti2L3z3eH+QCCImsmo1208+AVAUzchB'
        b'ZeRkwdhhYDKY3NuH5tyWJgWe4F6Aq1otfyUzSyj+spnHPVcM5iPUQcrw5XiKLfQMuC2w3i0mCp4NEgN+BiwdwMBLqGWF4IOcFwGKwb1lbvlqr4Xpi23HebhPxdzjUCIb'
        b'qh4zYrVVSHzbR4LVuIbxjEItf77IBfx/7X0HeBzV1ei0rVqtqtXc5CLba0nu2ODebVmWZFxwoSySZiVLWq3k2ZWLWAFGwO66g21sDAYXTHHFYIyxjUlmSCEJCaElLKE9'
        b'SIhDCCFACCbgd865M6uVJRGT/3//l/e+p/00M3fm9nLuOeeeUnPHr2aI/lfgy87i9TNKX5wjTnF8e/e9b5zf9FRmUv072v6G96ZIm6c8PzXpUO72X/xoyuxuLXe+NeaK'
        b'AwdSzyX/49uK3+fZfeUvrNv76eOPj5i6fF/L8WEFR6y3T1qzseWNlb+8S4qkjbuvvurTB3svfXn6xu6LduZ3tzWsPjX64IlnRxx9KEt747Wiic9UzfrN9Nu/fOjohR/t'
        b'viX905xV79yuDTp7YNIfe0/9fU7tqPn33DAn4Q/XDrl5uWf3HR8u3PqL1/rsGHj/sZ+s+fjEK7meO66off3RNWmhoS8+8OypHx5/Wnt2zC3vJn7zSu/Stya/ujfLZSbu'
        b'Y1VLoFg7ou6PZ22oT3AM59urnvG3udgepO5geOOMgcQV8WdrdzEDckXdDS1x9YTaSpKAlr7qgWL1YeUSEeWcOUzI8aF+U5lORw908BKn1FHfh5BZn7ZV21dMeuBCrXpG'
        b'e5yfdKW2+fId6v13MEsTG2GD87gBMl05ethwgkkTO8AkKVFXnsZNTewBG5uZl4S+QLTayb1kFt+DCFJSt+aFfyjnY/CL2T+J2qsalEqPmxxktoGxf8ednaD8iePiLaVg'
        b'WXd2DvNyv+gE5ulqrlsd+bMLBmun60n2HKHf08NGDpO4/rykbteOak/QolU3aMdvxG2/T+GNXJ+R3SsNTUv8aycWhSrsYR69okaAXENPlmGkTk1BSckImuBfgq3clMWl'
        b'Q6xMiBMU9vAkqaxvnWFRFo10rSJzeA2xRGV4WNqDzofFvQLkzFBZqbQDmRxz0YqoHXkvtjMiOAgZZpLTzHYOl+N9FxNi0/mmRY6LDxmoRA+uObfC2wAUDZNU6szhMsOm'
        b'xKipqbHRoyizcPglorHNUSngWR0AHAWz8Nc0e6I2vwcFqALoTXhVjRxYrvwZ44uyp6M3ZajgX/D549jkdcTXZb+oGyhHpoqVjAL04qWLkogWD4k+1/YkaieK0e97GSNy'
        b'jB38CXUt11t7QNJOaDtv6YCWxnoWhxjRUkKcOUCcHcTPQz/kMOR7sK9hg5JF7Gvi9gnKcBhmQZYghhgU0X87OqttEXE4KYdCeEv+0/E7xIYdUWYm+c2lFwaNv27S6nrv'
        b'kPxJhGDW+KonXNt34PWDrr0BrvkufB4yeNJ1kyYSon4eK8uYYD/hiHJEMidq9nvKlcrlUVO10tDUGDUhBwpu3oZVMDgv0BKNilBK1NKIkmeKL2qCzoQEVqPQ78L7k9Fg'
        b'JaR2G5GPizpTSRIRYqST2QWDlysZlKdVO5FJph+BPAgDhR4pY3gxWei0cFe6zNpT6np1R1ZaO7yj3fHnPhoNQPyFdA5JAUa6KBNQBUhJxesefi/nzwwKMpAKQc6NykGC'
        b'0huv9KVvEMgHN/xP5663tRA5BLmJmTAuPLeiP8UeHYs9jsUmz/TIm+SVuRRjVixGafsYMlNEkkqjvP2CkJtLQwN9SdP3S1oVgfIaL6wUyeP11MOQeFZ6vN+xFKOORsUT'
        b'QHVW7PEfijo3wSEy61TJ5OM3mZ6li+lIql4kUjWj8pb8QXMKXUSjqhtYl/PTtee4Puo+0yA1sqRrfXJ0s9524A9wilsmeiRy6Mmh085tYq251rLMCu/QkSe+s3gstTbZ'
        b'YoTQ0SfAONQmty6zy311ciFBdtxuW5YQCyfKTgg7dD8VUshaZZKT5GRIk9juXYqcCu+csTeSnCanw5ukdrG6yRnwLpm0yLllKXK/kFjFk564bVmq3J9CveTeEEqT8yCN'
        b'GWqQK/eBcDp5xehGUHZANGEGjIzHF5gK9F+7mWgwJhcYELeNy08uqTlZMp4NopRvoRlw/iL8XeDHAt6OmPNjusO8q2NDHbe43LRY3agA6G8sr/S8HoPDQnOPuKoNuTRi'
        b'pzQl1RU3XyT3YdYyzgOpysF84xHsBsqrO9OTi9oaveU1Pjd8jhpVcAjN3eKrEIvRoWzBKDuVYwp6DRZjder6go8JUZMbtwZaF51q6uGqec/gFCWLzcnxZWPSDsMTK9ZB'
        b'w4MAQI4VyCuJPObPd17SH4yS7EIHwifGj/bGhp02AJ7xoOnooz8e9TD30EFRFuoEJUdGvoUwHt0+w+pZyfmHyqagiHfYAng8zoE3FpYqgzPiyjx6StfZatbSC/zQKD/4'
        b'gjBkKAwZmQ3G2igWHDz+pgummwa35Plx7/U3emsCUTsQmkrAv6oG9lXchw39LbJ9j30T5Ru7olXdAGxga/aQWf0/ifrwGXpidiGHTxaEW+18c3a7iRifqrSdMVExvu96'
        b'GdOQ+i7ADh4E8goPy4aWDI8+2LOxZSZ/E2ASiET4ZEP4EZsQtccmfBeHEkp3SP93HEyJKp/Kt584mON/oZJVbZVUcrCmFsyw3OtVevBdIlS94dMFZJKht/bmtEurA6k7'
        b'hTRUI9SpD8NECkuIfYRpWtfCBNwoUP14o37o7j7IVrcAkz1q8vnryxuhqn1iVTUzrwm6w86oxcPqcXkK3X0hh29FXefWDlQBYlvNqfFtYdl33bnDWFOEWFOEWFOE+KZg'
        b'V0NjBL0xSi5Pu2hcQ2rQcFPApU+MyXjpx1+uanp/iClJcS1J7dASln+HQYlxq1AhIgw1DYvQkm4GRFCSETVh3upboDWIHuI6Dgj6NBKDButXhHU9maEHkpKJDcPjS9a6'
        b'BLcbUKyagKfe7Tb2irncvzZrqQxAHQtJP6iy60hYMt+c2W65tmXe9UjdGD/psr6rfWysEMrGRra/PrKwFdLIivrISvGxoQ+kUiWPN/DXXDZ81BVofjtutKE//EaVjSGP'
        b'mc68vCEfBPmkSPpeyHoGzagzKwTteydW1L/wtmpwzBeyYjrbQq1ud0VDg9ft7o5oOnIemtPbF8Y+E/K+sN1oGEQInXIhyheGlRLkqhD55RG9vR92mYf4TcZsmgkd808u'
        b'hjCuAaBc4wtEkxBPlz2V3nImx4pa+oEGdiJt7AyYTMnH3qZT8EuYy2bFg26TehvTiiwsXQQK+2L7FcOizey0ETSlcmONkGnayMJGiSgknklHGDiTVDl8lA/1B5kPpqjN'
        b's7rS2+SvWemJJuKu5gaKE0v1f4ZjnAsN9Pkn9O1LJ70A2QoIJsOO5IUtwmjiMGzdcLx81bGJyhD40K8NHmDbANNpt2lgndpBA0wYI0t+CZcaOplAXgDgAkNZw2gTkWD2'
        b'AzW/Fw/Z+WzuOqHF1GIOmoLCSqgSrRRTNvpsEvwu9lzN4328/gVghhlB+wpz0MzewxNXK6GwB5SUBPlZWqxQsjlogdIsQSt2bdCSyUHMcRDT0mIL2pRrg7x/IRCnS4M2'
        b'+C6O53xC0IYYi788KPjLZap9LaSt4Y21SefnuEAvmPohtuWyRR2wMoCwrPHKMNxRS6DBLddUBkiSgvYH2GECMLcqojaMiMvIT1gmI4ASeOL/0N5jr2zw+Zn2YZSX8dAF'
        b'Mo3ylYodsxEqZWYmj1Dkj7kuN9bREHsQDh3KoEkE79LpbNVJ6zuV1riZZ14N0TkCkqbtN2C9EY8RSkwL0SXMnOniZ7oyLhVUpqacMZqiSLGWJfKM6kZimqEGiITQtk/9'
        b'QlsOgWeCRIoLL4W8PveoFXFuxi6bGRjnfwzr8oqod4SVs4qCBMSgJGCz4ckpJjuSpXQp3ZxqTrdY7U7JKWWZmD750ZQKP/ph3ViibcxfMaegVN1RY+KyJ0sz1ae1PQtd'
        b'fBOeqWj3ao8U6hpbqK6lkStPTOIycyNkbUeqeWFQPQaxySXDQ+od2r3FsWx5LuFm9dYbBO1Qprqvg3whwgmSoUqNwYgawGV08KZbF0moL6/z6BiL0rsTSGXRR3WWpJMr'
        b'yQIdgg0O3OyPq4hdfaBwHrrA2ja/Aw1sAC//Qi6OBk4m/4ko+g4UL9CWElCvPLObtszElCKrRJ3aNaP1NIhjkR1yItytslNOuh2tr/F0nJcSdUxvqq9fo9e1c3SZNhk8'
        b'Z2MkDGy/fBydybfRmYz3AFeR+BCSTuyYShVTbGM18zq1ADslLi4iQdkE/pi6zY3Iuy+GTNECNLN3l9JJqDhRZkBKM98LlhYsp27xLfp+1nOY0RZlGt/FDmoDXIVVZZEx'
        b'qma+OaNdgbEoXaNr+qkqoSHxTtIN7Kqkk+nEsDCEZ273EsmgDfnmrEtaG4vUdfETaShlHmhCMwq4EeYIEF9JDVNHIGGOFYOBFpAxqGQTPtVW4eUxsaw8hgrTQFKvEcI0'
        b'kP/Oo3qCPNca6A8Dgk7iznXensvGfwg7HxErq7MRtLjdXo/P7ZaNLgRUO/2SIilC1zwEzCfAVTMhBd3ekoQbTFdIF36DhhgzxtrJFKUYl9FCPICf2WXrCJDXInI3Bwm7'
        b'S0vRsbuJbN+7ZDMhz7MzcPRmxTaHIrzMje0Q7DS462FFWwdzJV26xMrZRavZISaLVptVdIjE/lZ3WdTjfhdCbfVIoA0K9lY3c73UZyRth/aYerprOIh21Aw4uE2sFWul'
        b'ZSYPE1FDTp/kkWotgL7poRBfxROMtC6zMt4cwEUGJ23EY7PTnLFGU8sqaj2VAbIhqHfX92Qh0RJ2dAE2CLAFcFicOCyZHUv7fuwjZEwoSd/FPFqDhSXDx8uGQcsNGKTM'
        b'5DuipDglWjBPlCpu7tVJA74L8MQ0HNGxcbMtwOkEGCGki6FFEpCka3KYZDGBIDFIpxStgplbyr6b1ozRJY/5PWYi/oZBHEsbAbiXZ3GNNrGQLpHYRtgBNpNjzO+ovQiI'
        b'hNVMBpdAGM7/qHMKIY1NAV06t40cvhy4dqukzxEB6HgHoH+IBGagWO03XXecTkwmXLooS9qhdAzXm9R+jV6WO1jMx9e2MtsQMYeYJZKZRO0BdYt2WHtS3aXdWaatm1My'
        b'BOXv1s8tWRGHq0xVH7H0UyPqya5XaE7cCiW8hE4WAVcRGR4f7W70gQGYpqGh07kNDXVNje2ONk367EmLLTp9ywobJxskjdQvBplMDJWXAmsaPcqD+GiLMec63VLNXip1'
        b'k2So9OHp0MXmvt9RwyEsSSdagwtiS/GStTMPPqyXdOERK5csNqEss3ZM3d6gPRnravVQYIr2eBveq20qKhiinURJXm3zkEIAndtX2NHEz+EOx1ExLgnmC3s5R1wPJy0y'
        b'nlGBQTzewwOjjDDSgVzYjARumKNn014dCbnwzTSyzoKaz5VN/kBDfU2zR871Ak2bS2f0Su4gT0DxeNBUbEPbVHZ1baaWoo9FSxZk4QZVp2uqfQ0KlNHGOM0t98m5SEuj'
        b'4Y1yWa5hHr1yB+u00CDX4FxGfbdXp46rQvsiyr3ehlV+MqijlKM3LrRY6ys07Mvk6mi7v312QG/RcaW4pGQuLCYkzaMJcWUQZ+L7eqNbBKO/Q9Lhrd3KHMqixD3RAuoW'
        b'9a5p6noY+Kd49Xgdx2vHOe0J9ai6gYnbPJiOZupIcfQpXpzOiT7+6pSGDqsv5nP9hrjVJ7edWpmrTHReZlsmkpiUGfZBPCuzwh4p0emYKFtkK9IPsk22A31gjjsjsy6z'
        b'0G5ppVnijDr0ZVECBJBSOrODmZbYfETlZhlIpzDgLveLLVKMg5cKRAJfg9KVXDVP5xRIVgjK9BjPrndQ0L8ABprNAWkhIZcgKPrH4BOFpWzIHfkS0BbGAxSCwnQUOjBB'
        b'OpMRh3gUVxn83FpBNgMxJyExxxtgxIIs9Pm4gInLh85GGRrZ9m5oG5iN2t3Ey3Yjl502E8SdXLr9HIrdk/iEjYqnqma1GyU3Sa0jKvj8l2+t9KikqygJgoBMoG/sJiuZ'
        b'EEc02Uzs7mQSeUnlc/jYQRgNShvREw8rLFycrAgqkFfDuOzDXhaQT8RDGCVboQenMS4Rigf4s4lzJBHPxxEQghKKEBAFysnSRuzvfIOHtEdCZSFlLKWA+cVGBSCSuRVG'
        b'm3LoB+8tAMRnYhz2RX9PcAkVgloF9maFA0URED8DaBs1LcBzpKg4wydHpVJ03m66ptzb1PGYMYY0sWNG5HHJwkpGiOpUCyz064ivG9s6+M7kask0568MrN3BNRe27+PK'
        b'Bh/AlgCBKH+8GAqznAqZEle4jac8iqhe5AYSTNJZVH5yc8iYVohqAIShfUz0e1ZETQ2K7FGQ6+lv8gaIzKhvY0V9l1iEs339NGM2WXlm8dbO23FeCWSU/lu72AM1e4RU'
        b'u/AXKa25+3e0tMNpZIylOpPmFK5amBXdW0RAxUieiNTJMnCWEY9e3MvGXAqKMr+Sx7W+R8C39M4QM0ZCB9mugBh7YMyt7iovCof4qNcMRmo59i1OAUX+F6hZNXz/XwYG'
        b'xCz+plIvCLdKHVaPXlSnOy3NLVSjjlOqg2sQW+IIklf7PYiUintRVhy+sbOHlbgu8EmEp/4BgExBIQP259t4Et4ACLaXJ8QXVgysjxHIAfVZjTcYB09jZRN7gjfQqxmM'
        b'GDCXstNXAWg7nGcXMhb56nwNq3xtW2xu3zx/3wvmm/L8eDhrVkZil2XQ9GOwTFmCb6ZwOqZrMF9opi3rSGREE90+lHhCo9+QwUfYsShOyFTCknl2pJGBYEpI5Ztz2ndv'
        b'fNIOECrGfKvi4o8+aeYgFoP4jMCeaoAmYSJNuqofQiFMQSqLQXNQItjfLSCx865a2BeQm72Pn88Ze4DB0DMrXl6fJooHL7Qe6bwHKHi0pA/4uSWOJWU1+M7KGAzaGKcZ'
        b'WhS3PDtnEtdD/K+MqYg9ZRclgfVZr46AXC9aLIXlYOuUaPfEKk5NqG9PFVwWvtJGKSyG1AcNfMXKZUjJ3ZJ7W20ZTtLzG6Y9O7WNeakdL9E2lBYKAaTeMyX1DCC1Wzq1'
        b'zI5/5L0zhpwkEXFuICXMbYKBkuCXS9ERJCV0ZIQEdZCVyVg+yVHr3IbKupk1Xk+pgg7U2yEk7cQl5nCMn8soT789IMg8LUFGWwv0jQ5FM5CLCZMLribiZZqJr2lBhT+3'
        b'NXZgeCENnSPnyg0e3eEBYpgXLHn+ISgViANGQgLmGj/Go/UVtZRX+FE0IWolyUG5RolaUL6+oSkQNbnrydsP+VyOWtwYA/DrOJmJqIQxlJWdEOk4GRJM+rzClYjeMM30'
        b's/PNKUYndc4RRfBmN/oJfYQwQVJkBaIqo41rtoZx4QFAQkC9mPMNJ33gKTwAKp5rzgvC8pKFOlHpdRumMiuDFgMFjmDsZpJH0/Pj6yRlRAD6Efsd3lllieVnxPXZ2X0V'
        b'vwpP5qjnF3ArrMRHXng+hQBcZUOTV6YeL68knwu52FMf7roX/x6b5LIBFQhdSt0UNdXXQScrTfhsKVtARH3U5FEUgENr8KVjfpMPo+tf/F6Pp1GHgFELbD6UVU2XCzoq'
        b'YeHdTLr8LyrSCqRQS2d3pIRDGpq3Cl+ZbRIvfNacGBsLTNm19g1TN63llG7UEzh3eWMMlEwYD8kYj3YSf8QkBEQTG8cmjanGH+sCk1KPz8SnupQgbvJhhQaY9PXPHNYA'
        b'pvmNJDQnxSrNYv0rzIvhlDF5J0CHwl2x1dF+kgegXIHJQLb45uS4+Uofu+6mwXHl4YTV+dgC42PTcQR0U0yZm0fq/Q6syyqjg5TVsapdqszkdgMwRu7sUJOhckvYt5mE'
        b'NOIqqUfrIBWN/4s5Hfui0UwwGIfYPUwqFA9keUNekyR6VtNYVXobAFHEjjOkZCS3Z3VlJ0xmAD2wpkebYqchSCQ42q97Fge5JriMuthOqGdoqCJ4WYeXjZfD/m2ESBaT'
        b'wdXnnJLT7khBFrDDwg7hnhmhPoyWn8q0TSunaw/pztUTa0V76ewO24ZFv5N6b4yjhPLqElCrMa4SSoEuk+TkEPMhJIbMIWuVmbi8Ntg+Uhh9S16A8ATMBlsJMxSH52Dx'
        b'lO3trtSoNHPe9I6qZjGMBE+qApyOS8CmATiEwOhIYwDhDnULC7USaoFTGIBiwMxC+hbCGRI3CfPWYIEjclfm+S8kQkB3sQ5Bg03JTIOhXdTG8mpP1OH3BNyNSoPcVAlU'
        b'gQNTu6+ZMX9BUVlpNAG/kXldAGIJbrfuhdztZhLubnRZY+B1MSMD3zWeWPYUY9JnkGAvwrTmRCy2cxKzK661rv16IWUB1CS3vtxHtkXRwA3ChXvapjczVXMpsokti7Vh'
        b'NlSJeNvNqVSRdh9L21XHxMUxnx+IGz1cfGiXPSgwDlmtoAwNA2WLTygID5SpCNQsIAKtTGyenltEwPPFTA4FtOktoAZ7zExchDBToPjCgGPKplZhsxNwU2mPJSiw7U2G'
        b'aSRxrSKTIxvO+Wet4hlDeykXky0zM33Xz0jwIy9vwYx5U3I/Qy03JkW5WvFU2QnFjwqrKvQpEjUD4tDYFKBejJrkpvpGP9MuRnFLOl2Nmlah8IPOIGUAj/qZkghVyy9f'
        b'p1y5H894TLpkopOQDAdNCweJrSFny34R0NlvYcdIoPFh1YvaZnu8Kz2BmspyBc8fmeorXioN7hX+oU6OzRixG3lGZe1F6S6exgzxe5ICh/EQ9fVG/U/PQFMBzi/ilzAf'
        b'MAF9aUrnUB4WTYCwcHcWtsrmFptsabEzHkRLAsyFBJKbDbQ4gHJwZHMtiUGbUmHECybCSFth250r21oSfUkUtkP4WjmhxR4r24plr7iyfV2CjiCgrllcHaf4MG/Zkcll'
        b'c40NkJMz6FTulRODTqAK7w069TLWBx3KWjze0GEK5CU7gxbMSxZbbD4nxcTS78WvKKXOSsKvKDcjW4KmYGLQDgiDrRavCbUOOWWjGXKzK4cxFtTRzKBe6XnUWDmPPb/w'
        b'PI7xh6GMN3755YIvJs0kbskFccKECTRcUdEN0IRfyKhMPjfKT41apjU0KTUAjPgilxA1+Tyr3KvZbY0rkekY2EkS2Fvj8/gZkKovV6prfP5oGgbKmwINBNzcFQC76qJW'
        b'fFnV4ANkWGlo8sns+OUunKlSpcfrjUpL5jX4o9LcGTMXRqWl9Fw6Y8lCVxKb3SREIFEGEun3mPyBNYBMJ2AF3Ms9NdXLIWtWGztGcHuhOh79GWhhKMKkeKAWUXMF477Y'
        b'fE31bkrBJJYlfIa3ntUBev0v/XsnMElUki9fhosH7SAzt6IOQrCSmVFF3aSKpLP4mLYbmmXpQbaIGNvCTKflbKmZL6IRQmJhJNNiiyuoUz4N7WOrufbrio7TnHTaj2RR'
        b'nixEOFTZCohEduEea0WeTqtu3yQblV142RzkM5jcpSRbEMoFTDqP1dyOzhZ1XivbZW0XcqaWK6gdnjuyoeoqxvcnExX+pnolFcb5Qv7l6M4XDsntPzQ/rwO6FZOCQw0g'
        b'UkKztEBbGB9BVz9bbnD9JnNtCmjjOyGpUPMsbCClGVxzb+pkrPzIqzpTPDufjytDGpznH0xrpxTI7484nbGH6kwyScJHRWhr1EkzvQbI+8oGb4OiQ3OWuUHy0dlf227d'
        b'Xun6/Vg9X4Skt8VQLyGdVCORu9WX16Ewy5ad/UvKHmxrDAwre/kuscGdvA70lR/xekFxzIXvaQmrjc2wCfKZYIqxGZIlqyVLSndmMOfonnJ1oz+hcYWYp23jBG0X30c9'
        b'p55DIcAYZlBKWHJpKWrn40nKanVnsL3tgF5Ngva4unE1is6JTXiAOFo9ou0lTcqq2Vwf7Rn1ICYnleRWmDtbMrGSNxa8evMcruaHR1J5/32A/h2saipZ+NXitOr03Xn9'
        b'Ry797dOTc39oespXMGXyXeHI9C3LlzhOPjLhtb9fVbusblHt9QOGDLzqw2e/WnuRv7jgky8/7fmm9t4I/zstX3cPrvc+k3XlBz8d9dL2EcMGfP2DITXc+/P5AQ9ZP5fF'
        b'Pxb33Lkt+8Y5Q/hX5gtVcspvNx8pvOLGzYeFmzwZvx143w9ufkbosaXp3T3jOecLpncfP8zN+mB048LXb1261Hn/wDcG/eqVYNInlaPe/nRfwdt/W/3zX0//Sd3SvTO2'
        b'bvtkSf0Zz/vPTF5w4Q1b4R+fGJ9yKnBb6cqzJ3v+Pj3zt4F1pR99aXthykit7rqkilEl1aPGSa/V/HXcX8cXf5j+G2XafRMnv/Hzb677YMaQHz7yi25HV+zufra3/Mfx'
        b'1//xH3/9S2jEB70e9U1e8N7M5EfWB4rebJ6af6J8wfCjtRcL+s79a2tu0Y6amZ7bBrfceMXHgxY9deUvXa9e/YFnes57PT7Z80n/F1++7if7ryp66q1BRxf1Oq3UPLDu'
        b'3fWKcHbgmyUf/vSA6dNzY0/+yPa867PCt98dd7Zn/z/aCyvuFuUZ/fbm1zz20YPmm/Pn3/KHG08Xh4Y89e6H2meWB97ne039jefVq6fcX/jq7nF/6fla0ksjrl/Us2L+'
        b'8ZeOHAwOfG/Hj58/+mlTr5CStN29v9vCUy+vfOnAsUBg9zXjMo70ej465JS0ve+fFzQcuO/r1a//Yk36oobyWa7TU+qq5rw/c8eUTRP3Rz848oNH7ls48fUTpz8/+9rr'
        b'66rciZ/fsPfaATOPnUx68vQbTQdzTpY96XlAuum+0Y5x6w7Ny1w0dVvJq6mPlJze39Dv6BcfNi6+duHIP5W/uPs3O37/8vWnq/9R9OKDd5wsffPOj17/Xfb+t/Zer1Wn'
        b'l90UcL818m/9TxyV3jF/fJ9zwnX/nLXwis3LbnnowVedyyaeKrtw9MPV33594OhnLd53qy/MqLt77N+rl9SeXX/4uZenPfnctnvfyHnHdDF888jXHLWbh/41a9rRdyKb'
        b'vvj1kuWV7zjPnP3rO2NSVn++U/jz2C13VO14+8j6R66csPeR0MqFW9SrhU8eOPX5n1/6tvbNwdX87ivOJ32TOHbswSMHZ3W75WX/881HP/nx6Hv6Ly7/av0NP/jb1IMl'
        b'7t+tdPz9oZMDUz5qaLa9WfxB0UH7svMXFw3LWzArMuytkwHfa28MfHVS2Hnw1GtC2XulN/y6buTWuTvvWhB4fN/202/uPPfougvCnn+G3s59pfszv5v72NxH+1Zt+9NN'
        b'b07bffHlawe9fdCZfOzNJWcafz/y7O1DGiqU7tdpX5zb/+W8czsOVEWfV29xv/B+wwOHr//5J0Fx1wdPi1tvdCWSjVBtjxohV1n7c5gxr7K5RYXqOnWzheumrRW1E9dl'
        b's3i3wcejeJxaRqfr6iaIgt6QU9SzorpVPavuIytN5QtuRrusReqGobMLtAjn0e7iUtU7RfWEuls9S1r3ZdcVa+uXqKe0DfmlhYNR6f4pQb1nsXYmkIsF3Zm+EH2gtzlA'
        b'59WI7gNdPaq1khkPp/qUtqm9oKt2Wt3FJF0L+lNNoDln7Ox42Da7YHBpoZBTwiWpz4lu9XHtrgCZkd1n7QN1IPVVPSt8Zu1jls1IfkDboD7BBcfapbH5gSsw3RH1Li0c'
        b'V35RSXGBttGFggfa4Zr2sge3FNs5dZ12kIzTazt8U4GK35b+3WIiy7XbAygzOhdKjviHkGeozU1dCzhod1i4Vdoum3pSfUi9L0CWoh9Ub1Of68hvVg9XMH6zeo92J7PJ'
        b'dXDWMtowtJ0ZbMOAXI8DSvi9tqfvvLjG/Ddm9v/KxdWXIRD/V1wMTpm3oVx2u8nORBaPclrmG9E+g5m//J/0B2dPpw1l2gUR/1N5wQaYuiWdF1LhOW0QL8zL4YUMARAw'
        b'c8EAIWuqMzvLJE0WhCx+NC94B/BCE5DLVjza788LyQKfS9cevNAb5cYEE10tWZAv8pIFUUDzi6b2zw5esLI3WH5fXugh8Bm84KDvTromD+AdDRKpYwsi1FCCHPv0gphZ'
        b'vMPioLx68VYn3qFO1wo81HqUwA/mHaXKL2PnfqH/P/+7uLSRCthbN3K6/YfVnTi4IO0GwGNPAla63tioYOfavEK938I5s8WeztSae+7qKfl7wdwcuDO78O4XfG9OdtxZ'
        b'fWLJ2++3rPrz829U/uSNbYEzn2c3u5oLwie2Hyje9Xf5w3mWf4SennjbNw8feHjtrV+d6zNj3ciXFs8Ye3doWtrdN9SdSx6rPvFSt4zbH2gc9PkdJeUzV9epvecsGfne'
        b'09u+rmnZds09jZtTVcsO4Wfn5Kv2CGVXOedO/mrzOntT3sRRP1x2bJvtntr3vv2n97Ebztu0A4FRmnvsxquHv3j1r6WETz5N2H7l6msW9u12ZvyYz366f/7iq9e8N35m'
        b'2cSPD3/Ru/7Je7eP/urApg+Kg97C/JP9fvHpM2996JmUnHGqT91dSXLhp7tf3J6348kBPZ+pPtJ3Zf9n81dc8djx138286PUnkvrwruX1K3bvbQu8vHSup9Heh7c9dXD'
        b'096+ZtZb76x7s7j6yG+HO187ve76cas2lxV+HSw8/JNW+adfyDvWvxBOamr+28zxpT++ruTvp+7+82cbv72le9q5J8a/e8/v+2wu3Ly6ds0vrv952l8S7vu0RvnxuSP1'
        b'kQef/DJafVrx3DBm1wsfZNdlVix94an31ygv/OzcbyLH7q57u8S3+p7fKbP+UpFxx6vXn7rli/e3pf/Ke+zM9qc/H/3ltY+lnBv+l2s+e37u6IbHvvzc99Hs1+TPHriQ'
        b'WtbSq+Xd4kHLr2z8fe+/vduvlVv6wZZZ/Ixtx1vtBx/du8m8a/nejc7Tf9y7mb/ztz+yVv65vHdaj3eTZ135Y1vpijv9c4drpj+ceh7Q7dZrbz9106lH+ET3E/m3nD/m'
        b'+Vn1g68O3P71t0mLTr4mnb/eNYEhGodWXanPpQ3a+gKcTLBjboHZNF8crj1VT5HUHdWOS5AexHi82lZAelao2wih6ac+uRydkRqeSLUNubx6fI12mtllfkjbod6er4a0'
        b'J9WjBWbYYdfyN1rVJwNkyGZtuvZUfnHhYKC9ANcht4Mb0uYXI2bVZ4EpVX1UPUeeqldqp6bHLLmjHXdvWpwld+2Yn0wWlVivKoZI2gYXRsvXDs8yc0ljxDrtMKBnWBm7'
        b'9kSTtn7obG0jVHT2RG09eijZoh4JdIOPJlndV6zuHqdtGiRwgo+fqJ6CapLLxN3aFi2Sj9bhy0xotjN9suAEHOgR5un1bu2odo58OAwq5Dlzr6TVwnBo9mbm+u2gtlY7'
        b'VoyfXUWFAmdVnwN0aK+ghtQzQwgB0Z7RNs6C78/1LimALSXIT4Jmr6UqLdAOD1MPjdN2auvwk/okv3DkjWQTKqAeUreS+TAyHqYeXJMj2K3TKZVVfRYNuZ7RHpytHoFk'
        b'LfzM8fPpSyXU84i2Pkd9oGwID/mt42dleGgklmgnU9VDaFrDNXi2dg96hwXkbGP+Ei3Ec3mjTNPT1KNsStwqFyQA4lqsHXQW2gdp69Rj6EI2R31WUnfZtDA1uqlpIplk'
        b'gy4Zoj1aUAQdV2riMpdLI9T9CtVf3aM9CkPhUo+jV0tB3cnPhCo/TLXU9kOn3ZEv9dDCQy3w7VF+sdVEX9QDpZna+tnaiSIcQeEWfnJQ20dDb9buUM8VE2CEYSIqfq0w'
        b'vId2YJ52lKqUpD6shdX1ZWWFRTiQJSYudVz2ShHavEs9QBhzjfaQdqCYefYtK4VM1KNlZs55szgdxnc3q/W+BmjU+qFmjl+g3a+1cuSR/AAN4xxtbS2bnuit1zKbB4R9'
        b'rULTTjtngp5drz5Gpks4qYIP8Oo51zy2QLapz0GHF7rmQEJzi/bEAiFD2werB/VlFfXxUWxKF+HkSVB3CtrhHO3RLOho3BOGqfeu1NbHSQJLQG60qs/Uitqtaus8Rgk8'
        b'BPNpe3FRQVEhVS9Vvc3EObV1Yql2CNYF9mszejErJoe/kqQdTObVB9NclDhVO3INa1UJ9LmrCPLXtq5YLqqn1S3aEYpSqm1U784vUo8Mcg2dU6Dt1g5Db2v7RfVW9YC2'
        b'jeHYaxdpDxfnzy6CZZejHVR38+re8hto9fRUI3O09QgANsPHq2Exb+XVM73UU8zFaaq2P3+OieOLtW0o37pTPT6BNWqjtkO7FeYCzjK0XwqdExQG+2FU7lK30GClLq+D'
        b'KUVeTKXkPO1ZXt0Fo/00fZPVQ8FiIJuuGMlzFu3uJPUpwaxo65lT+WMt2qF4k6RcUp/6YnHcQDVMU61UO14UZxMUDYKa1GcBaG4D2gOnWtpy9blismPN1ufgcRKQbHvE'
        b'aUBphpgx37C6d3kHM7GCVKyd1k63MFONu/wDLzXQyqUt7N9D1Har6yYE0ACB9mAwAQFLIQz2Wlgsg2GgYNXeDSToXOqWDcWF6kGJK1EPWbS13UtoAfsmaPckIHHaCEkf'
        b'AEpyQzFOrXTtflF7uJf6kO6wcqV6jEDakNklACoStH2C2tpHe1q7F3qXYjyn3ltE9ohxa8D19qSg7QkCdfeYepitOBjLHfnaprna5uICVyGMYlovy02ithU2hEPUDWNW'
        b'BIpxPUIzI0UFc4aSbcwCbnGCSbu3hiPnl83qzhR9m9pY5tIOaSeApFM34kaUkSeJs3Qoq66t0h5B49VlZbiFFFugPk8I18AseTQ1l/pz9ogADDjUplHdu5JYfUB6Wrhs'
        b'7UlpqXZ3EdWnDCjsZ6FG2nHMCH0KpWhn1VZOVPcO1DYye3unlqkbsGNoj5IKte0eHgboaYAyWN1abXsfrO5Q6Pi7V8e2Naxu9/6S2prWQuuhRtvCFxeVDC6xAOjeOk0S'
        b'rLCG7qUCRmbdQEaNXdDOQuhW7YBwbY12Ok0N/6uTNsN655j/AHrpP+4SO5Um2m0PPiRYBSvf/mfnkwXJ5CBz1j0A7xZ4q+DUv7BTFUMmSjdJIdj152TBjLkJ6AUivV2e'
        b'DjqZofgCavRIFMvOzmCE1WJ7W4XsZ77KzDMeui42biNjDk2Nbneb/UHjIOJXfHz78MiX6AjHlx3pCIrRTlwiEf5RhweFFfzPw7WCk/la+EWuCV+DEm6RgXAX4C7AXYR7'
        b'BtwluC8KX1PDwd0evgb1GSO9MX4txuRDfOgaQyavhUN5PK9YL0WS6k0tfL25Rai3tOCBo0W2ea31thaJnu1ee31Ci4meE7yO+sQWMz07vM76pBYLHmYGkiH3bnBPgXsa'
        b'3FPh3gvuaXCH73gcG+kT5MJJcE8KkkGjSEIQbffykWSIlw73VLh3g7sT7hlwz0PRcbhbglKkr2yJZMpiJEtOjGTLzkh3OSnSQ06O9JRTWqxyaotNTovkBEWZC2ejeHqk'
        b'n5weccndIkPkjEiZnBkpkbMi8+TsyCw5J1Ikd48MlntECuSekXy5V2SQ3DsyU86NjJD7RMbKfSMT5X6RSXL/yJVyXmSUPCByhTwwMkEeFJksuyKj5cGR8XJ+ZIxcEBkn'
        b'F0aukodERspDI8PlYZFieXhkqDwiMkceGVkgj4rMlq+IzJBHR6bIYyKF8pWRq+WrIvPlsZHSsL2Vi/SXx0WmBjLhKUUeH5krT4hMkydGFsqTIsNkPjI9aIEvuWEhaA3a'
        b'qrCX0kPOUGaod6ikSpIny1Ng/OxBe8RBAjJt1nGdoaRQeigDYmaFskM5oe6hXpCmT2hgaEhoaGhYaEpoRmhmaHZoTqg4tCC0MLQI5kMfeWosP2vYGbaGXa1CxBZibu9Z'
        b'vg7KOTmUEkoNddNz7wl59w3lhQaEXKHBoYLQiNDI0KjQFaHRoTGhK0NXhcaGxoXGhyaEJoYmhSaHpoamQ8lFobmhMihziDwtVqYJyjRRmWYoj5WE+Q8I5UOKWaGiqgR5'
        b'eix2YkgkLwaJEC81lKbXJjfUH2oyEGoyDUooDc2rSpNnGGlaEsLOYAKVMIDSJkApidSfWdBDPSB1P0o/CNLnhwpDw6G+Mymfq0Pzq7LlmbHSRairSDlJN9txHFsc4byw'
        b'Izw47Ag6wkWtAgqD0JsCelPA3tzsCCaQgNAs5iKBDIm0qZ90LQWHeAHT+QpzTbySGCDxyVrekDLX9aMvdMvzD3Ll1jCB1fLciqYab6DG5xKU2xAGubAg5JZ3aZTLXeUj'
        b'FhoKu+0z6apzDjqSVn5taM64JAB31Z5AlYKqGlbP6koSzyEFejxob6iKOgwBJRJM4tHASj3AR3iyo/Xw+kbF4/dDSPQ2VKOGNcqxKS9B3uexyeex1PNYufN4nH0eZffO'
        b'c4a4doPsAShLpi5Q1D0qNjY0Ru2Qu+ypKkdFCmuVm53eMsXONlMYMcgcNVdRPtGEygZ3uVJN7kjRmaq7blWDz7sm9soOr3wss6gDnv2Bct2yqBVCVd7yan/UAk+UmY0e'
        b'fP6An76SgD6VsLJcaQug9C+GKB09OOmt4icxCl8D5eOFASyvYAkUj2clmonHAEpJUMBU6fWUK1GztxwGeHhUrKipJrF2tLnD3IhE7ejTmj0zoaEX9EEOKOWVHnRf6XZD'
        b'9Ao3G0gLPKHYQ1RyK56qqNMt1/jLK7wed2V55XImsAwTQ2Ym4ZCFf0EY5OrgPhC/IgLPDHAJzEcRCmah+So0P4tCBdPx4F4gbV6hFcjfFYlBPl5PuaNt1n9ljgon5z9j'
        b'QpyEEziMSduujiT6atTxBHwNWwDSOWBhZWNNgjzAIKEKVTqSyA4nR4oeYjiXxMmkoBS2N3HKlLCjxRQUwgl1aILK0WL2pVMIFnPYkcC1mMIcEz8L28Op8MUJbXdkYl+Y'
        b'wxYI92wVguZwNyhR8M0LCkoRvOsVzqhCQz3FKDAG5aRBOYspdhak7oG5+cbC+97hFIrnD6cA3LGQWpyjxQoxLeF0iCnBXgF93YoqNxVBCXYQnvIzQ353hc2Qxka5doc4'
        b'OBJOaKEd0uvpgjZ4suMTelIK2hZwrO1hHtKfhXRJ4cQEQyVPDCfTt8QsNEYMBJ7MBRPwW1AASJuYyTE1MbKfamMuFWKCeawnfwH9bw/nQLkC9kfQlE6qfrEe+A3VNdPo'
        b'gWA7fXaX4790wNHnP4DJ/L340DibzWbdVoLTwFUFpvRlhmczqQymoswRmW11kNHWDMJzzYD3ZqBskegUkoUehOVaxXRekqzfAIAX2i2TFH3noWXysqAvEycMtUtfJunx'
        b'ywS+ijh8YQl2p6x2CweHLx/SSPSEU94UlPyBsAkmojmMvwwYdhHl+IIWZUrQQro+1iCUxiYPLJSc8ZyvNtw93C88AKZ/dpUJ7UzB1B3UYg+jNJwdck0I2sPdYTnWwcRL'
        b'SuCycUsW4dmJz0EHLTjIJ5gAyGGSPoFJMpB9C9phus/xjQn3DyeGu8t8uB/8D4D/3uFBVXw4BcsJ98ZllQ7IJbzPCfPh5HAyImU1FlrWJpzGsJBSglZoTSJMeLgHYWmE'
        b'nVlcizOcCqgAvnFmcrBsEglFSIBUgBwoZyg9PMkoeWxGqaoWk28lvDWHB0OuScGkcBbFAWAA9U0K51IoVw/1p1B/PZRHoTw91ItCvfRQjlFTCnWnUHc91I9C/fTQAAoN'
        b'0EM9KNRDD/WlUF891JNCPfVQHwr10UO9Yz2HoWwKZWOoKgk2hkJE7YPcJgSZCAigreGB4URocXIweQvaEZPoasErzZZMnC2QB/R+FVoz11uTyaEmIvRoGs4yyFUkcxMS'
        b'9j0CbnqfH5RISlcyPNC0WSpP+T+ydl1D/gPgx/88jJqEMGpDDEY5daNoKOVo5p3k1SyVFySBZz/pa6vVTlZf00liUvgKPQLgL11AWUjpH3YHuaaT7OYMwQ7wC358Vz/p'
        b'r47UZDEVYBuemErfOkwOstHeDr4ZqmME35iFTYBgQDaHrTp8M4e5OPgmhk20nQPCErYBwg9wjUmP6xowhjeCzubAf92NAnXqEbMuUqcDfhGAvNShUVajUWexURIsE8Q9'
        b'BADLNtaQVhIMVdJQmD2cjCZF6b0UpJjQxMSwGXdo6IokAFSJCLYxhGLxYfvmLB5zTQin4jLEziIgJpoAyIZtYwAFHN9OIN5nHc75Z8SLwwMQBHAKAF/Un5MhFxLqRsdL'
        b'lJ+hKfNdnZr2Pzujz5pjYvEwhwW82i09eDMMQirfg+aY/dI5Zo8fjmZENQEtDCchGhwbDkkfjnQajm6Anon+DPqC4QwMk6H/vjDvHKhdTN/sm1Op81AD35JF+goY6qTr'
        b'x7XrekD4wpZs1KyVlJNB0V9qoOA8licBQom7s0lpQmebCGlhXzPBDgSD3WJpNiEzgtQDbRIX4NbUGzn7+FUcpchi6f2LiDh3hpKBME8PZVZZdEc91rhSrAj5la3hRHxj'
        b'pGZ7ImAatiqhTlJOQV1Ox3K2IRME0hyBNPAG3ttiaeJLvy9eYU5XuxJLO1X9iZkKjvmoREoFGg3dTt4t0GAF+hdCE5oNGYi76uYGDFNdLjEqBCqUD8iYD/+9bYhEnTV+'
        b'd0NFlXuVguLditWi0zASL+kmdWn+uXgi4f8tlybZ/0lbw+/MurYwW0goHO8QHLQxYHN7fGuXJLJehJ5JUX2aOYGR0D+pXfokK91usQqpvMOCX3Ebges/pZelQol3ZTEe'
        b'RQuWRX5BRP8av/IyvnsFL6/i5TUmiY2GhPzK66R60OytqVB+Q4/15YHlym9J6RsePOXoc0J5g1RpamSlP2UK9HtULK8Ayn95uR9Vw6MW3T5W1OI3Hqq9DRXlXr8r8b+n'
        b'A12L/wN49P//8u8cauCc3IqsCfR0KAhWqf2BhlPIMjl49ut44MF+Uic/R6dv//2fWf9vCzvMqaJkmStKV9j5KlGqtfO5ouQYJko97Px4UZpmRwsjViQ3AYUTqJ2lqKrz'
        b'NEfOJdzxPEC3W1+R9eWNsCwDirKdZ8rBZAKBnaX8mtbdjNWVnka0EqXggR2erFSWN/k9bnc03e32NzUS7xAZbagIA28T3G0B5av29izitGjH1zfITV4PKkkwjA/2SSkZ'
        b'DfV2esLD3WJNY3ehL+pGGjKEEup6X/jff4FRbg=='
    ))))
