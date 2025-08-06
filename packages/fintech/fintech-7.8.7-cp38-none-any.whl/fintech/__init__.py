
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
        b'eJzcvQlYU1faAHzukoUQVpFN0bgTEhZBEffdsoO7opYEEiCCAbKo2KAgYlgEcd+rWLW4A+67Paf72Jnu01I7X9vpdLTtdNqZzkzHzrT/OecmISwu7fd/z/88P3m4ubn3'
        b'7Ofdz3ve80fQ7U+G/6fgf3MFvuhAFtAxWYyOPcTqOT2vZ6rYZiZLlA+yxDpOx28AWolOpBPjb+kab4vEIq0CVQwDFgLjJB7oPQplptUMyJIxYI1CJ9HLsj11UnyV03sv'
        b'evXWy9YzC8FooJNkyZbIFoHFwMguwr/mAo98pceD/rJ5BXpFZpmloNiomGUwWvS5BYoSbW6hNl8vU3L3JbiZ96X4YmLxpYOJymXcesPhf4nj2xyDL3aQx+hwfzZIy5ka'
        b'UAXK2TUyG1OFW3yYnQtsbBVgwFpmLWkBwC0oUHLpue7DI8b/Y/B/H1IgT4doLlAq0jvA38nreUWkKcv1PMDfipgFo0yf8Fngz0LebycfB722jhY2irSOtQM7l8e5Wsj8'
        b'8hY6C+7aQj7dGoXvA6X950ainahpHqpRL0A1qD56duK8xAjUgDYpUS3axIEZ81VwlxidHQNrDHMivgRmFc4Xs23oV5ovNUV5X2te/UK9NUKbqP1acycnILcgr4htXx+S'
        b'EAfWT81/Q7LwQquStQzBOaRo19OeuFwVKTXNGhmB6qJZMBCeQ5tFPDqLGuFWywCcbgS6BbfBergZbU4ZMBknhQ1wswR4+3MDRqALJjKcSq6DDVeaPMgk0wt5+MB3Qp6p'
        b'eI3eqMgTgGJSh7fWbNabLNk5VkORxWAk8GAm8wVC5Iw3Y/J0Zj3OdfB5VmNuhyQ722Q1Zmd3eGZn5xbptUZrSXa2knOriVyOMyYvck8wgxYSSgr2JgXf82XFDMvI6NU6'
        b'DD+Bt+CVySnqqPTICFib0TmuItTEAXWcCB0fD88UkWL7rnmVuSMCq2/abjM/Lnoz6n8AhR0+zMq+GPeNL9BU5gxYETbPATufTKZv3+tfyLzLAt/WcsMMmY9CyHJ5IQvI'
        b'RMcMD8v3nKcSHo6TiIEcAN8YcWrBai8xoNOP9qOWGZ6wRY2bVIM2z42ZI4BAuDouKjIc1URHJKUxYOkSaSrahZqVjHUQ6eogtN4T9yclEq6HG2ThqA6ehS08CIU3eLh3'
        b'GWyyknmE+2HbAjKP0RGoZhpqILcS4JnBoq3wtMQ6kNRegxqzx2c7JrvLVGOAOKvkrARmteHzUiKVyWkiIJ7Lrh4XiPaIrf3xcw08iZpS6IjCLcFJSZEs8IS7WdQyGG6l'
        b'7YQXrH1RfQaqS4ZH4ZW0KFSbCk/ywB9WcagCnYMVuALa0hPwOrwMz6KbKUnqpEgKnyLgjeq4dAussgbiJCvQpYnk5UBUJwI8z8CDcD+qoJ2YirGnVgBqX1ibloQalEm4'
        b'ErSNg1d1yI7HjIAH2g1rZqbExiWVjEYNKagxI0kEfAZx45ebHQlmz5tFXk9Du5LShNfe6Aw3MgNtdIw6uoqR0TMRz1QJqkebUkh/A9B+2IoucuiYLwYrjg7LXNy2dlSv'
        b'TkeNaFdskjpKjIflHIvODUQXhO6e18AqFWpMRZvhhoEpamVksgj0GcChbXALrLQSXH0a1cATKRmRSSo8urVJ6uToqMS01XCPGKiBCO1Bp9EWWhe0w2NTSGtUUQMMiWlR'
        b'DPBEh1l0Ce2FG60ROMEE2PBMCk1AepUZnoLRvhFtwpCWGSkG03ketohRBdyGmqyDcfIoFp3AqWszUmeHJ2ZMSkWN6akZ80lS9TjRTFQLW7tQNtad9u6nxNzOYJLJ2Xm7'
        b'yC62S+xSu4ddZve0y+1edm+7j93X7mf3t/exB9j72gPtQfZge4g91N7P3t8eZh9gH2hX2AfZB9uH2Ifah9mH20fYw+1Ke4RdZVfbI+1R9mh7jH2kPdYeZx9lH22Pzxvj'
        b'IMughsdkmcFkGbjIMkPJMibMDrKc350s+zgIR1eyXJ1OJ0C9rjwlEm3pSTYcNANdk1nDCFCc1mVSHEuPVA6C9khYQxDIX8PBM7K+1r5kijbAg4tRPQFL2MIBdh0zJSmW'
        b'wvTEZ3xUZTjDcXUihmm4gUFVA1ALfRVTivaqlJGoJRLVYEgUwxOsamJ/awgpbxu8sA7P0Z5cVKvGE84nMfAGOgGPWIPI29Oobk0Knv5GjGzkrQcDj6Zo6Lu14wei+tXw'
        b'SnQiauAAn8jAc/ASPGYNIP2ozUIXVVHKhAksYOFFJgs+x9FMMWgH3JUCT6jhwblJGA7ERWw4OuIjNOUo2oAqU9DuIagOYQqCqxvCwNPlc2lOdABtUVLQ84WnGFxqI5M6'
        b'CIMleactgi0ELGsxppzKUDNAHM8GRY+yBpN8l2A1OqtKRpsSxSkZuPNTWG8MsU1C/2pnwOu00AVR4ZE432p25GRUTelUNjrmjzE7fBBswJ0wMpOSOTqYaJcarcdENRme'
        b'm0jasZuZNQtdt/Yjr6rT0RWKH0qCztJiuAneYqG9GA8nnbyrsB3uQvVp6gScnLUxk1HdaNrKPHgRz/tJVKdGR+bjV/AcMw+nPkxfwm2+8FaKOn01rCDYxgNxKCvD3Js2'
        b'p38/PDn1iXimLmtxxnJmFp0F2rtd8PkVmGJGlaCLpKV1zFOwFtVRMgfPAkyT69WkQFVUEiZA6CSqSBeBoAI+tm8Q7Q6sWQPbU1SEHySTOfbwRlvELNwRAK/ksm6gT6C9'
        b'q5iDhRw74xJz2Bos1JRzGJ9YFz5xFJ/YtZwDn/KeTMzh0g0ptz9nzZPwg+++2fqV5vWce5qaA9fz7+E7/u1NU/Z6JMYxhjyF14uL1Z6LKifsrN60SR425d95TeMuem/U'
        b'iH8rB+/c9153/qhSYiFkOGYcvCkwLNSQoUQNSZRnpaDrIHAYz/mgepqKoER0L3wNboe7BqArsMoyAqdaCq+gNoq+6jQMYrVC0oWYqOPUA+EWHm1B11AzFYvEqGo1SZqB'
        b'qSNs7IuJNU4jQ00sEaDCaRJdALI7kqRGwVpaJcfBy0sH4cJPWAjKhKFKdFoVmYhZmQhLZOfZp+BhuGEyumQZSlq9FTWjPbRBlD1Q3gAb+sMzpKxhEaKM+escAlg3kYg+'
        b'pQJRB79Cay6kohaViNZKGeHjzcgYk78zrZLv4HRmSwdnNuWaSEIToYdKtrNIfE+m0hTgLJlmXucquKqLqEUxfj+smoaR6fiiNAymYsCrMTUIXPVwCTtWAD02j/3fytd8'
        b'b4B3pWA5ayZsLbg49CvN0tsjp735QtNLH7zQ9PL5pi1+r3rnfZLKgSlj+Af7RmEZmUxPejzam4JpwEF1OCaSKQyQwpNs2VjYZiHcVmXtK4CUyb+rsAQvLxEGle19RqwW'
        b'Q1Gn8LsOSH0ZU1/QKfxyxTnLe58ELOoGucafZKkhxfiSYirAA2/3GSDtxxxqC2pRwRNFVIrCBNnEYAH4clqXOWAc/3OdTbIJCM2kC40OdjW/sw/exuLs4pw8qzlXazEU'
        b'GzeRrJSksFTKnoHqc1G9WI/o+GQkqyLT04lMiyUNDqjgORHaW7jwCRpR8MhGeDhboG9yqz9MwPdmLEDW05rnwhPpBL/8URUHb1gNDwfAeAKADAFBrOTxvwAIe1A/BvRG'
        b'/URdEznp7kBX3ZTu2nlX3U9CeTf0VresNwR4NvOEyJyCH7z+Q+zJz+5rvtbc03yZK8+X5mm04dpXv4hoP3k5R9ei1+ha/O9pzmgL8k7pW7QF7Ov7Yo+Al74KHhw8OORv'
        b'uwdXXMdk2AJ+/1+vzduylYxFgUv0CENXzPB0YjrWUsg0108hM+2HlSosENegDUpGICJ8d0LVDTdE2bnaIgE55AJyBLKMnPHFBGtNqLnAkGfJ1ptMxaaoCUXFOKV5UhTN'
        b'4KRhvNaUb+4QF64i324o1ENlZE0Eg01hLmQi/HKnGzJ97e+OTAkEmfbBfT5YTkc1qSosA1KFGetO53B/azPSsdJTA68o4UXMCeolc8YCWDfZA8suW5MM7ItjObMSl5Ay'
        b'W1OYX5BflJ+em65N1S7/tEV/T3NCW/b9Pay4y/I+KWKA/g3xb0zDhO484ZB5ug2LO1Xp6ys2DXQllfc2DCZfV/9Jyu1u/f+mS/8J1cR6wQ1xt/6zWA5Z1w9exXrDIixU'
        b'PBSxelh2fiVdZ3uANZ8+z5C/JpM1E4b5zWc/pWixPJGfqOW3blIq4vvs1n2jkeZ9cgeAH0PyPxRXvPWmkreQvups6ABlzunqyPRx6KRAvf3geQ6LY9dXWSJxGs+xgmwR'
        b'jXXv8OTIKNiYgRoLME/erEqCp8MFlr4oW5oHj6NjlGMXw/WoEWdpCiBsv7FLwlC0g4fry2wCa982CVXDWxm0eGVyanpaMtauYCNJOHSIKAwdhefdocBtvr2sxtwCrcGo'
        b'12XrV+e6o8pAMSN8TApnFiXmJjhVJyocd0AVYxrkmnuS+lm3uf9c7j73pLlxyI6OqKimnIixe1NKGoYAjO6oDV0Vg2FrRBlBXl0myzn7hFs5SRtVBH8RWe1B2njQG2+X'
        b'pheREfheIZXqZoHV/aa/vnaf+cOlT+fHL+xbKgZUn4fPofPwnCoyCePnBQBEcegMOszAC4Fl1NjTwv7NZ3tG2UA28xPmp+Ctq/4pGGmyPQAx3YTXr9au0xXkCw9PLvIH'
        b'eFCmsF6ape1D5gHDH/+9lDUb8ZsF336botVpW/Qt+q81JdqayBb9lxjBv9QY8yLmHNeGybJuN8HzTX4RL0sDPE9o2RNbj+vPaE9pAyVfsm/LB2vGVX/IJAaF9v3buzF9'
        b'vwMv7ZmzqH9w63Hm9daOuHdj+4qZ92LFcSUXMRo8E/ZFwZ8x6aVM/upwMjENKdMyBEOFFDaxxXD36N4px2PpCV+gNRdQsFIIYDWCiIsy+hFERznLY5pM7xjTkE5QE2hq'
        b'J9XtvX5GSEYhj2Q+5gZ5d7tQHWqoOQ2fhduxFLkZNSdiMRLPf1+sw6rQvsdYaplullr2sdDWwyRABsGjB7TJ06mKDC9gZfUcMStdigAgGkTD/UUUPLYqRMS4nFmdqJH/'
        b'Mc1HgBkmlCOA67sfaNR35gcDk4h0v5dLB5Nt0NepOXMd/vHdvKORd1T+MCag+lPz3wr2yWyLmZQXFgKZWfLWbxXJAdtODB68aEb73K3N5pdGfLPn5/KaCBOs6Bs0YbP4'
        b'2acnvns3esThP3it91vIp67Ra2KnzV789Cu1A3xHfvWnpT8f1c4dMqtowUt5lz7+y4ktq5as/DlZFfX3f0S+F3Xldir8F1O5ZV/e/YaSgwO31g6588b3Sk8L4QGxqMbH'
        b'pW3BBrTXpXFRdQvtyKbJsJIDW8yT0Da1UonqUiMik5z25YglInhrENa3KE4+PzICnUuHpy3C29l+wAtVcKPmDaEyBayDu7huShuxBVAZewU6aiHEpRRWBqqiikuxkFFL'
        b'DAewkY1E7QmUyKI2Xz9YL4Nbu2l0nepcQCltCLqKrk9SJRPrSipWoYfDTZ6wjUUHPMstRC4YGzEbq9jqCIBuKqPQZizIYh1CwT8dDitpQ9F5dBxTc6rq4UoEcg+v9KHq'
        b'4EXJIgs1Athz41Pgsx5dVAm4bSHtxSIsrFaq0iOT8ICxAB1IlEs5adn0LvrXI3Q8cYk1p8gg8IJRAtKOY7GG549RVMwEMDy+soD9mWfx9Seew9f/8jy+/kcsEmO0lhNE'
        b'HuYqM7DX6oJdWEtSXnHD2te6qH7U8tA8B25ThaehOqz7inFfL6FW1MrCiiARrSJX7IZmRI+UOtFsMEdEfxsTAsrFNRKbuAZUseUSm8Scvsbbxh0CNnEzUy5dCIwBPLAw'
        b'hTJTAgPIZzEwBi7CwrFNSnLaxKSMCUDHkLymH2yikkUGUC6yiQ6xzWAGWNa0lC33KJeRGmweVawph9bF47tjNvEhrpmWcYinaQPKPWs4nM7TxuZxNlkjw4DSRuMUmkOO'
        b'Wyev8bCJqxjcXlmNlNxVMTSXlOaSuuV60SY3fVEjF1I724iff1+a08Qah9ISPavYJszAa5gaUCgmd7gdIh3bzAipmxjjf2g6xiLOY2na5BpPR9rkGpaU7Ur5Nk0ppqlK'
        b'akSOVPiuS6pTOu6QRMfrRBuwOjkDVDF4hL104kMSm9chqU6ikzaz5InNC+c9ovOweQWCci+7xO6JJTpOJ8P5pDaO5Cv3xv33rmJ00kJS49s2b50nng1v42DXcx4//1Yn'
        b'JzXavJuZQPKW13mVe9vYJtY0DreXoe1lTcE6bxvOEYTpdB6L0/kYFTbGxhZy+F2MzofcO55Ldb424W6wW/55Oj8hvysNqc3H5qPzH0O+vXCa9TZvevXR9bF527xIeeSd'
        b'0dvmQ96UbLJ5kd8WYX59cS98cS8CcC9Y0zc2X9I7XV88pqzppvAL5/kA30ldz98XfpHnuJd+ukD8G+iCqtkQYPOj7ffFtQfXeJEalstsvs422LgmzhRgYWw+Vcx6xii1'
        b'eAp3DrkoJH3eA0kR1r2NkSMfsGpFF2bIOhgi1aUJr8rHKLVMVs7YmOVgC1vKkyIc0mWHNDvbqF2hz85Wsh1sVEwHY+muZssmFBnMltziFSWTfnByQjGuZE3/3AJ9biFW'
        b'tTq1sc6kDzhFsekBo75PWvZAVpynsJSV6BXDzD2aKnLivsLZ1ECy9msjPJs18zW42VWMo9l5nY3DxFFJGebKR5BGE1kc/Q9waEWk1TJwn1T8wEerWKktsuoVuGXhw8xK'
        b'yn0fBJv1pVa9MVevMFj0KxTDDOT1iGHmEQ/86ANy63rE02sft5TO3A88FCusZosiR6944KM3WAr0JtxzPCD4et+XNv4BM+IBM/iBxzDzkqioqGX4OZFhH/ipFfnFFudY'
        b'jcP/SnmHyGDU6Vd3yBaQBs8kih5+hGs1d/C5xSVlHXyhvgyrvbjmYp2+wyOnzKLXmkxa/GJ5scHYITaZS4oMlg7epC8xmcLJoHnMwxXQkpT+HR65xUYL0ShMHRwuqYMn'
        b'ANEhpsNj7hCRtpg7pGZrjnAnoi/IA4NFm1Ok72AMHRx+1SE2CwmYwg6pwZxtsZbgl7zFbDF18CvJlVthzsfZSTM6RKXWYote6dWrNPpLLligTHfBqtQJkm+QOd9IQYwI'
        b'rzxD+KE3I+aI2Mrjj5TxdYi0ciaAldHf/vQ5Ts8G4vtQ/CSQ8RUH4HsxfhpIbabejC9L+KkcP8W/WMI9vVlBGPZnvallNZgJ+BnX+DPLBuBcmMOywvJCiwzeIipUGmpM'
        b'V6Oj65IlwDubG5uM1nexx0uB4MdAkeIzfMGsi7WBQ4Cyo99i1sWV8zbOHFoqt2BxlvwbMKvbzxEGZ2Nt3ASMPKZMzAyZQjH+xuwjBBxiMcnkQkAzZkSYMfGYHfCEgZh1'
        b'Nj6fweXxuOxMzMQ4wlwwI9yLUZCwCZGOlCfS8bgMjvzC35gxknJKCwSGYzqm40tadIRRi2wSWpfY8V4k1E7LYScA+pt3/OYngFK5jaX2M1E6xuI0Mo90MjPIJc11R54p'
        b'RaapZIo5s97SwWl1ug6xtUSntehN08lbaYeEQN8KbUmHVKfP01qLLBhoySOdIddiSnUW2CHVry7R51r0OlMmeUbsYUrxY+DMzfBJnBd02c5yB2BiZh5OwYzH4ELAzFcA'
        b'BQJsVG+SM8GsL+NLwUtwQdgX8nQKaoW76TJiEqyNJmt+acIKnQpeEqGdw5geighxbCBARGvrsawKyMJqnqdT27ExTgtKdyXJJWjp8KWGzDRTi9n+clDii6EMZzSNwpDh'
        b'hZ8whJlWMZ5Y66HsCsMEZoJMDVfjSe5riSsMjxtCqpfh5sjzpC6rpYeNJTDUm1JFAJuMJDV6fkEawduI7ADWHMYVc+Seyk+ZGORZXBluWhVTCHCz8J0NN6ScMwbS5okx'
        b'cM8id/gJT4DNxtFngTVEtsFokId/E5CnslegjZQ6rpyz0TJxuo01YgyoHJZteKOc3OPn9JeNNxURroMRCJdh42n+IixzRmGZk7eI8lgsd37AYHmSAWvkeJhEhDNTHyn8'
        b'bK3I6SOFkQMPWyPjMGRjKCOab4dkpdZE7ZRcPoZkTE1NhatMUwiEJQmw2GmanEMuFHRzKejrTSal9ImpYyfUyrMpXSzBFa8wT3XBLIZPFsOmN4ZRTABZQvwCKbmUs3IM'
        b'y4FYdQhl1sRoc3P1JRZzJ5fX6XOLTVpLVzNsZwWYM2tJ1aQfGKupcw59YCAPPH8tnec6JGTYMPIKRea4uufhalAC41yP4gSyPwAT39CQNaEP74NTmNCQ4grJvexXMSGN'
        b'qzkSR2WjGYe0BDjFELoSnIQqQlJS09Mj0eaQcKUYeEax6Ag6EdzD0Cl1fJsX4IseZGG5L4ulOC922jSyuO1SwcqBUdAjT0T9/aRVTBbvek7ogwTTBcEHkLwT2QEPssSU'
        b'5Eo6/Bz+erMMRfrUYq1Ob3r4ujA14rG4SEx83NYnuF++PuEkRT0c4Ebie3gE3Yg2w9PhiWlRSWmziVqfkZoUOQfVZMwNJ3SSup/AjX5wPWrxWOzDGO7+7rKwnjzwRspX'
        b'mq81X2oK8iJ2hlMPuFcFD7icrzW/zcm6ffeF7S+db9qyhWnZOPbZaR8Nqx60u/KcCMTd8dwwbpFSRFeK+6PT8egc3OuBNkUSf6tSh+Ei1MrDjagSVtOlXb9hyxyGCbgN'
        b'NnVd/Ns0nSbxihSWbjNQLdyCtrutAA+Cz4ZSk8CI6avI2m82vOBc/oUb0Ca0yzINv4wVo92wfpXLWYd6GSWhC8J4wDpSezSqS0Wbydr/JliLNmNaDaJCcZI9Xqg52LGK'
        b'8DhzH5b/DUaDJTvb3ZK8DhQQ2cabWRPaA0SinBlciy5mfVFeh7iIvn3EogvGsRJyX+ys20RspvkESYgJAFTgzz53A+CjKn84oI4TAJXDsE/4pDhP7AJW/rHA2oNd9b6Q'
        b'J0mny4wBZnje6U61GG1AjcSJ0Bue4HzRjXQrWfRY4I9u4gSCF2en4xUGa4e3wvNoH7yAyfzScAnazoRZo3EmtD7PKmQKD8fAlxiJ6uBptAMenxeenIY2q6OSIpPTGGD0'
        b'8ZgIb8ImK5Ho0V54FjbMjVyQiDYpk9NScWIH7sDn0B6cehTcKR663M/wKvsHkZlohr/Zc/ErzWs5LfoW7aLbu+HlprZFxzYoq49vnLq/eU9bbVvV8UXcq/nitsLgcYvO'
        b'fVhXVGHbGSoe2fqM1OZhlkyXmOPeYXd676ze9IJ8/33w3Wv+9xPKMQ5Rv5WWabNRPbG1jYXXRIAfwMDDaO9SihboKryMtlJzGrGl5QGXNQ2uh43UnOYL7ZnoHMU/n2Hd'
        b'MXAvOkNxBx2ZEq+KikyMZAE8g66J4RE2Bg91A0Vic5EuJSo5TZ0EG1x+ISLUCC+CYU+JsmClh3Nt7cnlPq9ckx7LmtkrinXWIj3FlQAnrpRSGxrLO0ziawb2BNsuuZ2I'
        b'SRABYw9haJ1YI3o4j2EF1DG58KcUX4xd8Gd7oDv+PK4hPZDIZe2e4kQip4hJUEma5/G/QSVSgUvXd6GSd7rgz3QZNaGznb6JsDrChUx9UTNFJngwAV50YRNZaO4FoVzI'
        b'FDHKGkkBjpveHZkwblyAtT2QSTXp0S4JDnbmcElQMh1MXndbiXRCkXZFjk47qRrnNJFM1vn4khqIzpkfQsrRVnglLgWeTkyDjS5oxdjuWlhWwotcrL8Zbpvjj04DeAph'
        b'5lcBd2kE79FtaUsdFvlNqF6Nmcz1eMpn5nAjQ/t16Y8IuLkbUCopCPAsmWIXleQoS+fx1HKuqeXp1HJr+Ue5HLg0C3cqOZ7MQD28sTqFrB5GCS4gcxNVxENwPuavkUrU'
        b'mJqE7+DhgU5EBfCQXoZxeRvcRtdOaktFgrf+ym258QuMgNJIuBOdKOtSKLwyWHCWxqKC4HBCfKVXrPMIRhdVVLZAzXicKlJSyAomli0wAC0UaORsF/jMH4unaylqk6Cz'
        b'q9FlQ9obISIzkQnPJoGTpvvUW+21vCh/pTZVW0TlCrXpS80bOa/n/DYnSbtV9+o/+uSc1t+b8tl7MWD+eGZ+XNU8e9znytaY7a16c9+jMbEVisyNR6tm7meG9nut6ZUA'
        b'5t2PX3jzhbuvBN+5vUcM3jsRfFJ6x+HYpkDn4ns6toFAWIWeHcZzhSpKTm2wIttBK6MjtIFdaKXHeLoYg3bkr+tKDcfCCjrOhBjiyami9aEGWEckDrpwnUFquyA4vnmh'
        b'di4Y7tDSZXN0cCQ6k4LR07G8HYWFWH/U/vRaDg/qlUHULwpuhk2j4OXFzmRkTdJzDIuV3Yv5tNFjMUt61t1bhLiK+JZRZ5FZPr+cNnsTF5DsElOxher1lDiHOonzOuDP'
        b'UjMP1s9Zf2KswXr4mtE9KaN+tT7XQRc7tYSuJQt4LxLUj04t7XErno6FUS9XBkq8rfiymXHykQr6+bs7+bYuwc/DbGs7CQe8Nbk77XgM4SDrk1vHojbRTHRlCrwwDB5X'
        b'gsFoR8DyMnS6iDTjVlII/70/mPJtn5DhL7IXRx4q8Ad0RRyadzOtEqBoLdPH3o3dkeEpPH5v9N98tvsw4Yolf2R+WtR/0CRg2NxxWGQ+jN9NH2sctumGF4zxrf7rh+lF'
        b'I7YnjpLfDv76NmhOCHnNMtRrrv7uJ4mTQvMS41/ye+/Hd/714qwHTW/KXt743QTlgmkjXl89veO7Oef+MLGfMdB//L3XpC/qL8TnjDm0clVk1EXruXUNxm+vF/7r/Nnb'
        b'lucOp8xtuaz5oH3J0hPzvu4T8dHvRg2ZsumHTdFb93q/ndc62X/ViOSr3yR3LDavO3qonf3L5p++4zYPUh2zpSu9KABa1+BhcltYXDXdtc/hPLxO1/zg2agyl5TilFEK'
        b'lz+dgE5TIWVOYgZWE3aiHb3qCVeeshDb9OThiyhCzUCXOuewBs8VnjxBHYjXiZctROeEFcIdq+ABLNNgDN9L5Boq08BjGQIWX4anYFMKxMPbdcJFoN9oHtZPn2SZiZON'
        b'RJXZTq0BaytHfoHm4NAblsBblB5keesc5MeVTQL6okoO7pSj84FwBx2mAaqpgocMaRO8Am/QgZzPhS8aRVdWCwegQ3QHATwG96RSp2p4lF2dBG8I0mBr2nw3F1l0PMSp'
        b'I6FbqI4myVRDexcGN9Li5G8svGkhTpCoMQW2ovpUBjAJoAzuw4N8POwhuOjxS9V6kYvMeLpRCEpjwp00Zq1LAGRlxApIbCj4jmf9fcT46sv6MmvCHklxuoiEYsezTroi'
        b'eZK2sqZVoIt6tRJfnukiHtr7u4uHj24SrpQuFciyHQ+yszvk2dmlVm2RsGBE1Tcqg9KaOrzIJi2t2ZyrxzTToR3+ClPKcabDw1ESLoV2ZAW+6ElHyC8p6ythmUA5JpBq'
        b'Mvmb82Gru2y1Ee7oAvAsGAdviOGeZ9DNHmYI5zK0mWyOcZpZ9JxOEIsA9QJlddwGD2JWoaYTEZVsRS7TSabWgsfPiMcuPZfvVrJLJZ2ALw5J2mG6zZM4xC2+RoLFLREW'
        b't3iXuCWi4hZPDIkPV0p7StIiQSldyMIdWI4OQtscQ+KSo+GBlUrWSqjXElFMp6iNmjCnRrU8PI8ugNAZfOKiIiqS25bDo+6pVBGJYvjcKBBq5ufDXT6GrSsH8WZisjzZ'
        b'r+wrzeLbTUSHfPXEhraqtqorewzMXEmKpFDy0bQvsjaGbhx8zntnwLGilQqvz/Ujx8S9H/Ni3O9j+LgjYOaqkfnjQMIHvrNfsih5gSqchC2oURWViTZ0I8BPs+iYoGLa'
        b'4bYRhFZeXewilWPRRiF71QislmcL6kEKrCXECUspeg6LztdW0uyseJSwr8lBkYYmsatR7RSn6PEk6Obuh5yHASCb6HGULPg7ycI6oJbJAxiek7JYK+zXA2KiXPkEZBF3'
        b'cLlF5g5pnrWIolgHX4LTdogtWlO+3vJYMYM3EW98UwW5VJLLehclWEvxqqus8WGwOy14VOuUbDoxXhNqYFpNLmWUHFIUXaG3FBTraAWmNc5h6bkg+4yrKeX48rzTMCpl'
        b'MRYTTok2lk/tRGIpbC/purNuvEIMn4dVsEHwppJxwobKWZqIb1QhoMdiSVfM67Jc4sI8QB0QH71LrIdft3P1oivmhQi2y77wsLcZS+PnPUut6CJm9JdQm2UluuC5Ejb4'
        b'lGB8rJGjNgAmomMi1Iqq0XrrZNL12lS0D+eqTU1HDar0+dRMlIS/ajMiyQ7gregA1XjhaVSjjoJtc6gB9Dy8KkO3BsD6x25Y5qibxv/S8bZXakMEgOz5y1WwJRXVT891'
        b'TB5OOI9D9dNmCF7DG5KLCaoJnUOn0RG0QwWPhzMgFG7hTV5ws6F06T7eTJbm3r9x6CvN63/+UpN1u7WpedvxquOvHq8aWV/KNF1o8ntV0rZn/O45wXN3B8ZWjVr9+fjg'
        b'9g/rvx4XHNhaMS8m1hIjijuC6UnJMQ68vcR/y6YhSpGF+DFxYcqV6BrWU1Ad5hZieIqNQxcXUCKA2uPgVlUipS38GGYmOg3PZMLDlIYUYLHlNDUboLpIIYlPyTpYyS2H'
        b'e9FOQULci54jKehmt00YIMcy6ORM2IZqgwW/zAu56FZKITzXxeMrANY/dsuOp7akRI9xj2B/V0vTOjCbLMwIDvEyZk0EpgvZRYZcvdGsz84zFa/IzjO4qy9uBTlrpZTh'
        b'EUZaRkhBcXUDvvyuG9k418XZi6zOQvukkSkZkUSOdM4zbMhQmaCdDA2+Fdhxd8UkRRgXTJ+F8dXBZ31X+MJrjv25ZWkqdBSdIWMbF88CEXqWwQxq62zKv9BN2LIO40zb'
        b'qpXofKlcWlIqL+UBuhQSOJ7LR1t4us4aj26gM2Z0HrV5eK30knlLUfsqgp2lIoD2Jgz158vh83Povlk/uE+UkoS2oGfVEcJkSmEri+X4jajKSkgIVo1rWHgSo/Al3MWI'
        b'ZDU8gbavUocT80Gqc2fLXKljjzYDUMUSeASe85wOG0dQG8go2I5F1CfNDptRK9xZJMM04sI4unG3AF0lHoYlpXDzKnQRXcJkBovBiLjVXbKKAG7q5qFzeVg5Loey7plw'
        b'q542dxdh7VjLqU+VAHhmlg/aws0RT7OS3W4meDOgR4mrUJtcJgbZ8NTQJB7WTYMHqQBMN1TCa+jCWniOBeh0GRgPxkthMx29gswFaFtGZBLaCc8mJklAEDwmn8iiZ9FB'
        b'1G4le7rS8cju84wkWxVTFgp9hpeeciN28AIlastQpQRex2OxzeqHs0XHwktzMam7PhTgDzwWTmn/wXIP4AtaEqQaTarPhPGgiNC7dm8JkIPgtd4KjbzNqmRpSm8P4rvd'
        b'5CMCmqJxZdmCI25zAdl2r/FicMoJccsAbeDYobOJEUVFLEO11BrUlRg72ocJcU0xrJCWz0g1PH3vPDCT1cbyi9PTmiamoyl77b7V+Sv/22d84783vzjsXlPmdv/ZbzKi'
        b'gDcbarYn7iwKrSvdNuP1OX6l6z/emFsCGm8nzYn9KmHB3o//9f3Nso4PPWwVtcc0W97Uesnfa1itH131rwbv62v77bu98Ujwxs98696taLj8lurC+vnfn0ia2/r1ewWf'
        b'GVI/TZ1vfvniRNNl3/a/f/d+0Ez0zw3/Ncbqn9n+9aLkfl9c3PflXy+sjv3oQXxY5jfb0+7d/nT0dV27V+wP1/+z7cz0s8MzVdzWm3/964IVukvbG1de2/Pm78q/uJC3'
        b'4kfvLz/xi/rU+5tPPRJa9/zdK8j6anNYYsS/Qk9uuby/Maxu7dO5Y3OG/dznwaS/7j0XMWbWuSzFgTvbS7JP3fu+f9Fnt0+ODFi4Ym18/dCf7xfsObO2fMjUjwrq7yi8'
        b'/rsvKOGpBT5N6p+Z+7aVh2+8q/SxEGm1eAnxym1QYdVOhjGkjtiCPFE7x8IKeIlScLItGTVjAoPx4iS6yq5kpsIdz1DFz2sEXO8g4HGrMQmHZ+CmMVTvXI2qYHNKakRU'
        b'IrL70wSeRSw6EgGPUVV7jHowrnA6OpBO55csvtWz5TorJexT0JkwVYYat6U+LQaDrAQ36CaLLs2D+wRv4Up0KixFPRvecifsqBmeotmLMYvbpkI1Seokyj5EYKrBZwKX'
        b'5432UNYCt+vyUsgCJy5aGZmOhZugVExfmvgpcAvcSjnTssCnVL7wZJS7U3Mslm5p7Y3oOTWVi1C9BEyGTXwkg0WDVnRNGK1DcAfco0pOw9pw4gJ+EAMPoHaNsAn2WigW'
        b'4oVCCSXGRWCgDoIXC9FZPhHtixLY1r6xsFUF96Mz7jwT2ifT6YIXYSUxUnSVy9ENMf90XNzjTHZPpsa6q9x9e+VvlCfO6eSJTxGOyFMvZl9WxvrK8D/rz5CrjPPFz4Jd'
        b'7g1y6sPlT7cvEG8vb/zcm/WnvmG+rJw1VTtZ8XH2F+rfbk6HpJCXuvHNG+7iNg32IVmn7oVtuvPM5ei8CDxtkcIdBqwDCls6T6N9aagetpWn0LAYjsU1zDZp/IFL6Jov'
        b'qk+Hp8luoktoJ7W9wgssOtpngJD/GDoFG1SR6bAZtkZGiPH0HmLj5sGLuVw3cS/QKfJl4UuPGA7AFcWB6RLHgbX3zQt0LSWIHrmUwNGlBP7ToXhCZQq3vzn6fIPZojeZ'
        b'FZYCffegQlGyLmmTLAqDWWHSl1oNJr1OYSlWEJstzoifkiAyZHuqoph4dObo84pNeoXWWKYwW3MEm0aXonK1RuKxaVhRUmyy6HVRioUGrNxYLQrqKmrQKRyQSFvlLBu/'
        b'sJThJnQpyaQ3W0wGYjLu1tpx1ENGQbS7cQoSOIncEc9RUqSjeNzDXrIU6suId6eQy/GjW0adYiUeM9ymXguwmvFLIbsr/cxpSdPn0jcKg86sCJ+nNxQZ9QUr9KbIpBlm'
        b'ZddyHKPtdGzVKkgfjfnEq1WrIH6/pDnOsqIU6cV44EpKcF3ESbRHSYY8mksYUDxXOVrSIDxXeG7MuSZDiaVHR3rYQLxBd63EM91KHFUWzof75kY71/fmLEzEQufcxGTR'
        b'nLFj4XGlDF0pGwt3TBk8ti+qLgeoCbXIQ2aiuh4o4OssP70rCgAHEjAuJGDtPnm+v2AFrYdJh1CQnuFHItNxOkpYenry9XR4cFiYXEt5T6Lt9Wpb6rnFTuTYhk1GxWD5'
        b'YD8wk1XonWHzv9JEfpGolefd09zXrMj7WpOk5bfcl7+xyZD6YdHMrLBNiu/S359w0ft9i+LjF959Afgb8izamvdOir46qW3Sga/0y/PufKGuy9GBIan7pIHZt1t977Rr'
        b'w8/f1yy7fbmpcktzVYhuWgyXLwb7pWH/QuuVLOVyQ+GhMpUlIDJcMP7sZSPRLXiEvjKjek8VaiRiNG/1W86gWqx32H/5opIoe5VJW0JZzYBOVrMODCPOw8GUjvsyAYyY'
        b'brJZozQ5SJabR5wDuN2ekBIdm/wF59NODvOYhh1nhAyUvZBN/4Nxy8yBneylAnzSZe2IWBaewlrEVZUTC9z3Kjv2KXdynpn+yuhkNYCbB4BZsMXHgBPue4wvGEftKr9s'
        b'r3oPe4oI9GZbkKRbZwASMgZehTvjYkbFxo8cHQcvwVaLxbSy1Gqmes951I71ljZ0AZ3zkc5h5DJvDy9PuBnWwE0scSO75IFOJ+ZQod8vLMW/mglngK8m4uMxOkETaOqf'
        b'tHQuo2CARhPxZ2uCA7Z/LlnOmJfiu1NTV/R9ZZB/RYycv31tlLieubl+ynec+rK3NODejPe+D/lLhnJ5/pCwoP1jda+ltn+2e1Xpd031UOs/LCnuP94loxs+fX+V4fUf'
        b'DorE73jsePGdpyJHLTDe+63P5aMB+umRGIrpgk89PJGI1eDh49y3hO0Ko2LkiDIsuXUxLuzGnWvDMvKRR/mIPN7dy1Rsyc4hKjUe8WB3yI4jkO2PYVpKneHXqJ8Iph3F'
        b'ORcwXD7Vj3YEoyk6IboeX2J6QPTbXXaDEi9veHMkOkIhevyAJ4FpVBcNazNi4zmwEtb7RuER3UvnHmQLEdm+lemKJnAxQNjRuROej8dFHITrMShEgagp8BZNHThaQkO1'
        b'ZcatVTfpMwXw+SJM8Ep4c2Fx0RuxOgF86Bt7mZRwjpg3VxnkPsoA4WFoUQrZXy/V+K1abs1YLDw8vdAPKABIyJy0NpW3zQfCLoEbSca5qAFtnz86BtXxQDyHwZr3Fnhq'
        b'Vh+a6Vh8KBiFS2odbup/IniAUJJ6XRtTwYHMLySfrNo98qo3DS00EJ6KGBE1F5KyUIMIcBpmUonRSkJ0YaVqQx9ql5uJLjtUXayToBp1MjE6Ev2EOkWgzSoi4sNalUxZ'
        b'Bi/RJeDnrRKA9f6YSWlA/mGwbew7gG6/3sMNl+4v94tlNKkpptzIMSWZv40P7cOyVsJFxdKp6FxYEWYuaSANtgpomek/DlhwT26DvNghISOEnuxkJ4MNACR+vbDCFJzU'
        b'NJQ+vBg9CdiwpqFZWxp7K266kPLSMDWjYUH4y+oK8wdzWpfRh4fi32fOc0D6aWBl8W7mh7n04S71LGY7Bq8gvrJwd2zpLPrQP6wvE0OCPEkryoNl7wfShxEJFvAtnpGr'
        b'nhUrFwV/niAE9Uufz7SwILGiYE1hfuYiofYHeVuYcDzirL4iPziwXxx9+GLBInAZAM33gyvWfOC3K4k+LF4zmEllQckFc0X57lFKXoDAQQMBpnElQxZV2BaFnJ5BHw70'
        b'SGUO4ZRAVVG4e/ldofFD4gMZNQkpKNOH/bNPolD7VPFbzCEOp1xWEP2bwVOFhzcWvghqGKD4ZHaB8vsMx3g259vADwCEa/K0C140yoSHn6/6GFxmQHiJprxsZEaa8LBv'
        b'uRfABCEcFObIv2BGCg8DVpaCCgYkLOc/yXm34Gq+oSr3OG8+hCfyVPL782f/xvjuFN+vyzr+8MaaXVOury675T9l7Odcwhc+/7w9vUT17xzDsPf3v3nntanPLh18MGHw'
        b'j+t+2L/fb6L3tDr1qlU7Ck9ce2VQ4YIXvt03RlUTaX33w6j7X3w89VKLeui7M78ccvKa/ughbXD907af74frTl++M0285G39ywn5+83x+9NitgxUzpC+ltA8VRFWvast'
        b'9DXVb01Dp6bfDR+bNzc1JWuuasiPjTH9Fo0dWzBiqe7Phwa260TeWa+t3ZLvFXhp9Z8C3vZ6aVHT52uflrz/3tWgN+r+cfjYIhGz5Df76nKZr977Js406dJd3wVf3WtV'
        b'Sz/cG7G4dXOu/b+TXp26eVTw3U8PbJr72xm7/vt8k3eg/blPbty5Zbx2X/XS3Lcm3ln/haFs1t2Xbiwo6xfQmKlp+DG87QVuwotDJrzcZ8JLcRNe8fzD10e3rX5pTPmd'
        b'd/YnNPx+fsjfsv9WZ/P/s2Ft1YhnMq7lpv3P1jUv3zgjesl+I+j0tx5/HrP/L091vOYT8MXqj+rMD7b+OCp814yZ0Td/Kn1/2IUv9eZx87+/9faNuwcrL44a9Nq9/T+L'
        b'/mfO0YsB//76s+hM++YLP51SSqk8hPavGqGYqepiSxgWRM0nOfC5HBWqiQY6tB+wsJnJXAlPUyNAIdZB96uSI1MiI9JFQC5m4U10Bt2YOYy+heeHYpmZ8qbBcQ7uBNvm'
        b'o+cErrYR3lzgEYrpRkYSPMWTEHGD0WW4j2b1HAyrVeaCKGWyyhHX0QdVcMWz11CeN2oa2uiwvLjsLvBkKLrUdyA1nQxHN7K6+w2hplloHwdbE/v/0rV931++Nv3E0qPU'
        b'ySkpm7W5s9lBcoZnA719ZTzjHouLfA/A38H4488MZcRsfyxcetM9amQN0Z8JJHu4u386n/3EsuxPYk5MmbeUbuqQ4xJ5sk4Q+nBWLsijIrrLpEPiUCw7RFRbdOPh//t9'
        b'eljmbST3dDvLZhfrJ6Gjwnqw/j9FuLP+sQSOt/j0fbwsC2spMxORBWIsAF63onYr2QK6GIuLt+j6osvGmw5PYyi+kCo4qEXD8yJ0CrPZCrrAUAJPoV2di3LUq9QXVXP+'
        b'sG0A1ihOUNr4QSmWIor+R4wJvvrjoQ6CWc9jucCCSfsUTVHYBIfVeY8BSxAxUyVAoVGfCZ4BDL+/lygyH8Rv0rJbwzZN9IYx8ll/GW545/yfxkhLR8QvOBK14MMlszSK'
        b'xJVGZuEnG3Z7Z7RPnrzO/+V/yjZ4HAxXRX3Q+qetqjNXPt0ZdP1zr+KyMZZ5TWX/3rCqyTiubuHhz/z3p33T/rvvjgV957/ttfm2Txn/Y1Mrvr579+aW/aeGZZZVbHjm'
        b'B8WJiWtfUpkjPgh6sPnGW95fnx61d+G6JWOeP3fwwNZP+H/8SfING73swFClhAYLhlvmwKPOaMEtqKlrxGAenVXOESI67EQn+7uMk3wksxQ24GE+hXYLTkxVa9e6S2jE'
        b'ITGVAaHSNPgsXwxbYCN1ICzLCHBPhYmEfwQ3aTZ+X7la8ELcje9vkDSCpYuGZ4V1nvAMNwPeyKRkKGTFHFgfHZkeiepSlWJMZtZH9eey/fsLkSEOrtTB+gyHxOOKTNYP'
        b'NsG9cAsPn0M3jE6VMfD/dTLxxETEibWUiES4E5H+xNeIZYbPklM0Z8nGVVbYuyWmZMO0Bad2KO0NpBt9/q/b3eRCaVK1pAdK/xjfIzxdiwE1OnEaXvLBurxPPJc339jr'
        b'8jP5M8uZTj8dHZPF6dgsXsdliXR8lhj/S/C/NB9keeBv2XZuO68TNQjx3MjKP68T6yR0G5SnXq6T6jw2AJ1M59nAZnnh33L624v+9sa/velvH/rbB//2pb/96G9fXCK1'
        b'hOIy/XV9Nkiz/Fy1Ma7aAnR9aW3++J2UfHSBDSS+GwlwGKQLpu/69PIuRBdK3wU4fvfT9cc19HX8CtMNwL8CdTy13gzs8E4VCHma1qjN15s+lXS3phKLX9c0Cuq60SXR'
        b'43IYzMS0R+2rujKjdoWBWFnLFFqdjtj/TPoVxSv1bubEroXjTDgRsd87zJWCrdBlhqQ5ohSZRXqtWa8wFluIiVVroYmtZhJIvovl0EySKPRGYlfUKXLKFI79vlEOY7A2'
        b'12JYqbWQgkuKjdQ2rCc1GovKuhoU55sFGzOuSmtyM4tS4/EqbRl9ulJvMuQZ8FPSSYsedxqXqdfmFjzE4usYBUetUXQwLSat0ZynJwZqndaiJY0sMqwwWIQBxd3s2kFj'
        b'XrFpBQ2sqFhVYMgt6G7hthoNuHDcEoNOb7QY8socI4X5e5eCHoQVWCwl5nHR0doSQ9Ty4mKjwRyl00c7IrI/GO58nYcnM0ebW9gzTVRuviGdhIkowRCzqtike7hViATJ'
        b'ozsE6carPNET7hHkqF2If1Dd09hsNFgM2iLDGj2e0x4AaTRbtMbc7ssB5M9h8Ha2WLB54x+GfCMev6mZSa5XPQ3cTxBKVJxON5Yw8Cx6tnNnCWxXOzeX9NhY4rHYSvbb'
        b'TppIIoE7ZRC0SU7CaqujotDm6GQGxMNd4mfmoVqlEG4PnsIc7ngKFjaq4YXUjEiyzaEhgwH+cD+HKtFRVGtYmvApbyZGFPmQ98lWrvDP7uOrOvC+JtGxOyFqQbg2Wcue'
        b'CwmKWRUTrVt6u72peduVKmX9haojq65UjayPrL6y63jVsGcnOvZCrn/G71pTLVYdKLuuhpdGCpw4Iasrxyb8Oh8eoew6Fu6AV3K03dkx5sXhvoJD3k74LKz0xL1WusQG'
        b'1BTVF9p5acgMQUs5CK+sU6HGAFidOIoHHLrGGA1rBW2jLRe14nEgY8AAn6UkvBmsRBsKLWRajMnDUX1KpAQo1SSkdAq6kUML7NsnEBeXOCp2NAfWLpasYdBeKTpE2xsK'
        b'a+ER2q2atFTxGFgJsOTHoCtoI9rr9PB/gkU+4v1KGXOgO2NeBwLkdLMBkcDXBHUFWtfuRYExHxf8fU0k7uTjvPuOs0Kyrpsn61inEa/C9fkhwN2v72EtePhOJ9IyG1ju'
        b'jAGrJO64zpWp44zQgK67nkwWfNmDm0I3PPWo0rkl6kHIQxe8cCWcrjj3iRpVIDRKmu3QVUz7HtKi/c4WPQhwW/Ryrp1F/ZIRkGYT4mrQmR9a2UFXZWpSmVNy62WNLbfI'
        b'gIl2pBnTbuWTNSJfaIRntn51icFE+cJD23HY1Y4hpB2dOQjj6T7wXat3EnMas5ESc0c4WrvIjZj/ioC0XYL8uJNRivkbfGDlWr+5qIEnQfUA9WqyC+HW9y2B++BJ4mSD'
        b'Kd4+fD0HT1D3sAnoPNyD6pOo5B7HY8XCJIX1bHKA3lDRdgmYyc6Zt0Qvh9W/5lcRI+eGjehvqHi5YBCXujzxadvSjR8rh0f/5euC0cdHXb8+9k3tvIR/b5u3/OLnCceO'
        b'51yReIU/85/co5EXx4nHr6jPOVvW8NrYwqw9k+5t7fOnfwPfoBB+zyylTAjiuR3tgI09FZrEIoFA4jcXKcWZPxZTcqxsJFEzP9moK0XXWEyGquAlqqx4rcxLcboJYh5x'
        b'na4EBKG9gkGlDd1Y7DSX8OlyeI2BrevgAcEdpGUKjYDvWieAGzwZ2BYIr9DXC+EFuN9F60BJlEDqFKiSUsmn4dWYFNQYTY4L4ePV6AQDr48spz4oq+GNLGdk8tEThc3p'
        b'8Ea04Pp4AF0gkf6dJ2eUKGnMSbQJNlEvkawlMhrSPpFS7aTsKMK2TnKYwO5G57sEtXsSSouxT2/MNZWVWCi5JQPqRm6VcurQIaMOkTROcA+S58jtvsfiyUJVOqIEd9Lc'
        b'I/hytBea+/Gjaa6jAf8nolNBr6LT9AKtMV8v+E84hR0n8ncTpLA89KQylFG/6klFp95jZ/KYjlH7CjyIgfI84eqwoqy7cJOHthmG3E7iqOfJP2VnvF4fHzglJoB/8+3T'
        b'e67/YI3PHRR+b9TYulODIt4Ib63WPX/3QV1IO/zN53H6D/sGDPD9/LkDth+rat8aMUERKA8eqa1eeuqnZUE1bR7XD/znffGde//0ad4TYIx4WukhuAEfXAibiKwwOcsp'
        b'eaAmJAAybByFsKiQQbaZwhPqgXBTOAO8UQOnh4cEkyS0L0igsC6am+iUUQRYh1vgDmGvQvXEIGKKgJv7oDoG8NHkpI0bcy3ERxU9h05PQdt4IbBuSgZsiO6UCGPQIfFY'
        b'VJdqIatTfdQxRNBBe80SenhGylPoJkXxxegE2fCBR7IGHab1CxJSjhetPTpnKOncRNREZSEqCa2DwiZ634L4TtqgDxFoQwo88MtR1CeXAly2Ezq6uy2TzzgZNUoGMGsG'
        b'dEOQbpkdZovdD0VM0x4XRpLosa29YOTbXTDyMRUquQ5xQbHZYtB1eGC4txgJr+8QCzz/4dt6KNbyri09IteWHtEjt/Q4sPbTaUw3RZ38TdXpiLJDMM1NcBCURBfbfii6'
        b'Cp0QkDUR3yfNcCJ9jtZY2BNlXVju6LOQM1P4iTOHp1iNWMWMTJrRiy+Qm1+RMydRqEm2Ln5Eyt7aa9JbrCajeZxCM89k1WuIO5AQmkCnVmhmaYvMwjNtEX6oK8NyDBGn'
        b'jJYnoDq9hr6ffMLKmolPwbXfjvtK8/TtN1/44IV3X2hvurKzuaq5amy9dl3bnrbswzvbNo6sP76xefOg/ZW1L2wf1DSoRjtyeszuRk0i057wDnhlmVf6X1OUnID659AN'
        b'tL2TOjhIA2or04vQZop8o9FJeIvgPkV8dHg4wX1zf7qDdODErJTUJFibkYbqZNmpUbAxmnqDKuEmETw9etIvR0JvrU6Xrc8x5JqpuEpx0LcrDqYQDFwT1g0duuZzKCdi'
        b'ge89Ty4t5HK8K8t0P5aCd0tW7EpLEfQkvtzoBUFf6oKgj27R/xkKPtUbCs6hxiyMhUYB7IiPmxsuupmx/v+HjSRb0twMhWCAsgj2Kqo25BmM2iKFTl+k7+mY9+R4qP/k'
        b'CkfxcIt2S294KGDhuxOfAA8LJmI8JEyah0dHOLAQnYW7OjFRPwxeFFj8CXh5ImXB+3UuFryowEJ2tME9g9BeVTJqQA3RKbCBYGNqFFZBtjnxcTJslPhPXfbL0dFPsIo+'
        b'BiOzKEZ2E8qiemR18MRT3TDPdNqFaGfx5U4viHaxC6I9tqLHHM/D2IHb8TyPDqrOUd2Vf5DTC4pReKO4YLSuyMFohUHMzXzcaZTNtZpMmPAXlbnp1L8W+nIT/8zQUGHP'
        b'2X9PTgBqbWqmcDey3kX9Z/Z9FNzlV3u2pA/BcEe0oOVZ6RTsZsJr7vRfD3fNE2xa5+eUE6DzgsdcQJeUbSGWQNhigc1E8cJKI6xdPUWAOgHiIsQY5K5IFEF+3Y5f6hXG'
        b'coutRovb9Jl7g7EcaW8w1iNrutM3sfihlF6wO1B4a8OXj3qBt+e9HwVvPSr9P4A340PhrdNP+YlhTREeQYQxg1GxMj5qVEQvlPfJYC91qoKnsNd3bYID9haldYe+R8Ae'
        b'k7/R8/hbQzHsKQgA1aMaeLW77IEa4EZOj67BLcL2mEQdhj9UsSTSBX+hIyxkHRHehHvRVuL/pY4SJBA36POG7QnQLsZKyla08Qlg0JeM6eNAcLkQGasbNHTP6aBy7Q+H'
        b'uvP48sdeoO5gF6h7XD3KoO67mSXZ2bri3OzsDj7bairq8CLXbOeySIenaxOKQWfaSzKR81JMh8iFRD6hxtgOaYmpuERvspR1SJ2WTery0CFxWA87ZG4WPGJLoOoLFZEo'
        b'+aY4Rbv4q6MnuJkDt+KLlQzVLEB2WvOePOP2YaVMgBdLDgb4Scw95Jv398Sp5HLG15v8e0vpYTDo6GB4FZ0bvsy1q/dCGtZdse7LgnBYKVqHzml6LKMQLJ8CHLvju67g'
        b'CnuOO/o49nk4po4Gp36gmLmahNIk9stcsonDZCTSmJv0lY41xK5TabrgGoZu9tEb+PIV69p6zgtbz+H1UamdW89Rq7NXzpWKiSOSZRK4eeAqKwmwko+eNzzKI/l0aKdT'
        b'cq8uyageVvageZ5OikFEI4cvP+h6ZmpncN9fc3AOqaSnCVaeruSEM0viZICMom/ey7nBfrFPUz/Pjd5i4uepALNSwZ8XLYvhQBHZpf2XoImi+8GDgp/J+NlzzBzTwuZJ'
        b'8ydnLrSOFM0eFdZQWhDbb/G4gUtWJVuvjjs2f8bMHxd/3+/n0DtjQteUqbSzpZLCgN+F/Z1FE+WjAhIuj6we9Ur5yrSEYevC+4wPn7968kU+2/9oydmBOdkfGc5LBs8/'
        b'otEnJBfe8fhL0kSVV1DBIpOoYvAXM1bKvjSvLAkP+nDmCc8Qr6vrfsZKwb3pSQzdjeqDDiJiEN0Ad7jMw9Q2nAObaF+nTyHBA8InegNNkWZFnMPrFJAzfQqeEgGNLWuy'
        b'w8H00IwgoAbSITKFxnZinVTYK4quolsDUX1aZBQ5C9cZQwxtTpH4wktoCzxehmpnwh2iYQBuGO6Bmj0CaFmpE8mR4xXZoima1MZ4P6GC4R5kM2p4oVihkYtVw4XItbtD'
        b'LuOpe2YsOdbi9wMM93++yZjt5PlbHw1ruObFjZRPV772r9LAhH6Lh4/XiRjl22FzOtLuhi/5YN+sl0cPHqBsSu57cfcHp7/bkzpuu+S/L06rTN64cXzo/Pb3jswetMz/'
        b'D5/abIm/n5W96szQqZc2vP5ydb9lkRdXPX/fZ5zGdPsZw9prs/pkf6BjYv/zTUja3Y/y3n9p4Wea/NS1g2/+dHLz8G3vbFPyggn4XDmqTClE21xGYMEE3AaP0M2Gc9C2'
        b'cE8OVvZ2wjiPzs5UU0ceWImeR+dVkcnEY6gFNpGBFAFPdJVFl+DBOYL5DKNWiArVRRDTVjp6nmxYG6ud29Or/NcGFnbfeW8ya7sYm8kyqBsXs/HUH48E85ayvoyCEFF8'
        b'b7rlLIYcXU5W+N2kp1/brOOM6QUX6SIV/LMXtrdJ4e5UQwZ+Nnwe7VdFpMNNbrLBYNTWDx7g4UnUsKwH8XGZaaf0SnxcQR9/1UGIva/9yJyEx3OAp0B44lPVy5f/Q04J'
        b'z4xICeg/L4LBDEP+4aLyhJ8EwvOf+YTwXMn/eWY/5ZXCzOwTA1sK2fxV/x8Tnm9H9JXRrqzgCV2R5vsAjTw2eKmA4efnULqikABN/1dM5cLSHH0zXkr2D9TEiKdo5B8X'
        b'DRce/sZAD4UP5BSaosMTOEDPURXJCwcXuy12UWrGTzS8Gl/JmItwgjda6yJ/0+aFyFaV559u/9pvw/kPX1W1mv8cMXOpkpm05IPf1OzbyN5t+uR/3vlLhWLlj7P1X4+Z'
        b'MDph4AeXJ088m3m1PHB6yvQ7x5vj2u9fjFjzwZi118IC08ybVOr69mf/uWs1/Gr0g6Vttp9GF4ZdeOuwkhG86+ajqxgx96c4T0eXLmP16EBBF3Hxl/njdkdDnb4TDYd2'
        b'RcN1wIcssAcIUgxFRTlFTBNyFXT7V7QAuvCNlCPlnHEEK9w+D/p3xzh0sgS2CBiXlOZAOLgeXemn4WEzqkP7emz0I/80CucCjIs1IiH+vY05BAimNbPlLL3ndDy+5ywM'
        b'eT8DNDHLvJey5Xw5iZIvqgEWlhzfYCpZ420THeJ0omamXLQQGAeQGPWFMlORcC4SfUfOTBIJMemNt23kbJ4YWgbJ327jTJtwKlGzcD6SmB4yEYprEpdLahibhETS10ka'
        b'cHqbeAIo3W5cS/OKqsgZOJzpVXKkA26/CLdTRCP3k7zSHnmlOO+bxmk0r3AiUUyPnP0flrOJKZXViIXU+Ammw7i0cOHkAMdpQ5k2oPMIwcTFJghAsnRMifX6klkmEk17'
        b'3gOR1ZIXmWAi2jcG0hfJJJMXJrIT20Si9yglpjwCfB56o3WF3kQOliACX4eYRIrX6Tvk840GckMFUyHvVAHGOiNBdhZLI/fTDU4k/quJhK/tYJb/0shScnKUizlW2Ggb'
        b'yjk2e5LY9nLHGRPCsSbkgBKZ41CTQLc7ueNbSg8ukTo8i5phZRE5w90EdydFxkeQff7U3V4xgMf8uxbt6uGV4IqATXDfBsxSHTMXkCOq6ASwrpMe6ECaxjo7QULkmh+i'
        b'NXrRrmVbirOLio354znnwaUc0U6ouxQ8kmQgzUyKxKopqhViEWJBywI3ScBwWC0qg7vg7h7HCbkctkbRtuqYQsYkJ1qGjrORw6AYHX8IkOOFcMtFgaCZsTFBgDA38oSy'
        b'MLGjH9SNgh22mm7tus8KHRKtyTMUFSnZDsbYwRQ8rHOkT6RvtJPTOEfoOjJx9JAFRwdvGqKIDk7CyG+mPcwQunsUnhOD4QNEZWgn2vyYjb9Mrxt/H3/aYY8wT4x70W5b'
        b'MTs3tjVmlwLLuhcYUKLJOzU8WHiYMvklcD0uiANTNAa51rE96aNnJKB1NiZxmI/93qQChi8Vdxl65Ej7PzVfaZbR+E4Xqo5XXdjzVvWDJYPeP7GzeWNz1aB9NxJPVlmZ'
        b'XK/psj9OO5b+/rTK0I2iVM+QOpHicJg67M5o+RublKn+U/wPs+EvS2OHVS+Wh1+sGFutH5Qbw+WHgnFHQ0pa3sEiKg2FsQUdm6cie4TTkh27hBei7ZR9yWbPXQAvdZ74'
        b'Jxz3NzaeemtMDSfR1heienU6ic21Wc3g9ydZdCYT3RQ80q77wd3wZDJRGlGtL6xlgHgtOzgt45fvMvZbUawbO0Y4PCNbZ8g3WLpHr3WEfZJSXCY4HMqY3nEVUvsk1dU5'
        b'q6MZU3pla5e67B4mWyasIeNwBxsyYNsoGsYXbkggBxeRQ3Ado5IAnxevxeBb+XB6QaxAApUgzK2ZoXSCTe8Qac25BgMWcV8BTr47uOvISAr0q4sMeWXzSXOp4wRHA17P'
        b'QOc1dMGdqF0S+GwqPMljjaGaxYqZvfzhLSF5ycEwlOkFkNOUSHvKHa1ztMv0LqCC9wxnqx4VpsvDanS0MauTehEphHo4xBTBehVqcDR1vJYs0OOWkthoBzAF3vuLxmyD'
        b's22m9x42Xh458aOEA8C0biNGVLV8WD8zJTaOOB+hM5MFcc1nEDceXZL/L4ars0m/f6LBws0TGGlet8Gi2mRVf7SHtDEprSTa4UCKznAjfVBdDxc118l2ZBe6jsH0nAhM'
        b'wBRuIdSeq2KxEAHKOeG0KxuLaTtbKrWxJbE2hpw8RZsuSu8YGjMyNm7U6PgxCWOnTps+Y+aspxKTklNS09IzMmfPmTtv/oKFixZnCZSfSJ+CiMBgacCwEuOsku8QCwsX'
        b'HaLcAq3J3CEmASzi4gXGL+3e+bh4YW5WcM5DNjjBDke4Nw3d4o0RaW9KbDzxqoLXnnFMUxA3Dl2ERx4+T3IHsOiE45byyKzcddaO6dEfegWVuHhhLlZ1Qy50GG5HO0kr'
        b'ktJg3XjnTBzhYtBpeFCYqoblaap0YinbDGviU8ghNhCr660atP4xpny2iyn/VwQi7P0sDhHxKSIt06JLozBdbhHsDZE06qfPQm4JrJklxC/bilp0ixKx9gTAErAEnkdX'
        b'DfypV1gziYa24IdtX2kW3S7OomtCGwfVt1WNrG7bNbI6af+g3ZVxHFiiFn2lalGy1PoxH+6H28hh0o2oPlpCfBYPe8SxWNq/bBRcA04PByRYMYl9jOklCQOVhglmn2gO'
        b'7Uib6GQTD5EdDObibIthhd5s0a4o6R5R1PnhpGLTH13zzHVIaY6uR0m462KM6XNnDTSfrVcusNHdik6NvRMwrbqJu0JiuUc7BjaJxLzej3YAMNwkWiebPKuHY1tXeybn'
        b'cGxzs2baGZc980lcSnuAAum1Tw9Q8EunCnMGnvIUzLwb0SYeiENRO2pgZQVlgmQyMBCQsMEpwzUT1gyRO7bc1zyDNetYtB1ehm2xMWAwkKQzcB+qhFuEsEqn4HPwFE5Q'
        b'NRZejIUXeJwA7mLgRViBzljJ7HgvgafQNhE8CKto6IBEG63NJywEYNHfd41GY0ucvVoQjoaWhAOsGShqizWD/VKXA1oArEpDNfAcWwJbAQmut26OsHEwhkS7A6u/Wq5J'
        b'TRjg2Hp+Rk9DDyz6LE0jPzQoDE8uPVwKtcObCnhgWkoSPKUWA74/A9tRK2qkeXJWTcHzCxT55ZrYPwxVCgX9jafb6hPhRI1/7GyHDWLJMGqDyBQP16j/WxgPDDtHfcSb'
        b'CR1ZPekfMzPbkvmp8rTYc3HXSi/c7OOpSrl1+1Zr5guxr34KA//S7+QOXahk0MLwtfCbg3v/1Ljt2wGVu3YF5fznfdndqtEvi3ccU/0xhA+6e676/vuLptyrv9j657ZV'
        b'XsMSl776XtHpl9aVDzcEnprXVjHsj3XTuLTxaP0fG2ZPrR67f2nS3956b8BSz8G21gfv+kz4YabfH/54+1bCsiGnjn6S9PGXZd7VyeFvZSaN+zT0zuLf3izlzqYZjvw/'
        b'7X0JeFTlufDZ5sySyWQhK2tI2CYbu4CyyRIIgQQBQRAZk5xJyDYJZyYscaIglJmRTRFBEFHcAVFAwaK49Bx7bavXXutztU61ttYNtaWtem1Tq//7vt85kwlJLO3tf5/+'
        b'/3MzT8453znfvrzf+77fuywLHRy05pNVHbvH1SX/8oWMeW88siF8qOXIW0953v7B4Ck/uP2jmy7f9YXt03VPvzOocNNM75EdbpmxG+/rf01ZKa8/HMfYWKnfwpiee8Y3'
        b'MqRRf1B/uhNx7K+H6Dusj+e1E/G61tqBdKFIu1u/gxBHv6yfKtOO27VThigwEwOeNZtSi5NnGzoStqkGs5RUJFK0c4TP5mlb9GfKSKcaaQahnp+mbyu7dH9w/wwGaWIL'
        b'7HVeD4CoiZeNGk3AaXJ34JQo8YxRCvub6OT7A+4qCxKfi6CF/CBm0TvmfFP9IAbGmPmQqKOmWa32esi3Yyc0+0e8sgkqehiMMzSCZW0VTSnijV1+X+dcDPyy9aP2grmF'
        b'+STXjSDwqVFjR+kPamclbggvaXfoW/SNZKpSLNWe0PZbEC0ZzA3WbptQbWos4l8XiaXVHCJW6MszAmQa+l8MI1VqCUpqYdAC/xJs55YsLg1iZUKcoHAvT0LBxtYZFhXR'
        b'TLdZZO6aIZaoVoWle+F9UDwsQM7M6aBU3o08jjkWxX2KvO2mMeI3CBlmkqtHw9dubTdfu4Tc9LxtkaPdYyIX5x44p6qxGagaJkrUk4tghlOJUUtrS4tXVfGYMioRdS1H'
        b'pYB3fQAwFczCX9fmjdr9XpRwCqDv23V1SmC1+jHGFxVvd/+/UMVP8Pl8bN464+tyv2gKp4o2g0Ui8QO/lUS0IUgDz+tHM8rQebm2e3QFo3nMPXyQfkjSn9QPZndDTGM9'
        b'i0OMiCnhzxzgz1nEz0Mv2jDk92Jfw36liNjXxO0T1CoYZkGRIIYYFNH/OLpYbRdxOCmHFfCWvIDjd4gtLuYUi8Gs6BgxeeW09U2NxQXTCMms89VOuTZ3+HUjrl0F1wI3'
        b'PhfnT1s5bSrh6+exsozt9UOOqEfcpKOy31upVq+OWmrV5taWqAV5TnBrbF4HQ/MSrc6oCKVErS0oGKb6ohboSkhgMwv9LvQ/GQ05QmqPGfmkaB5miJJp44CcpTKwIfHM'
        b'edPJlfqjZRVF+kb9ES2iPY4mabRIBTtzIguWVm6iW9b2abfot3fBQroceO6hAQH8X0jjkB5gRIwaQP0adQhe7+UPc/7ioKAAvRDkPKh5I6hT8UpfZgWBwvDA/yzuutR2'
        b'IowgNzEThobn1syl2I2x2DtZbF/fIK/upG/hi78Zttek8ijv6BBycmg8oANpxn5OCyFQWdcIi0PyNnqbYBy8a72N37H+os4W1RtAXVDs5h909q7T8HSczDPLEHhylcZm'
        b'uX6HvlEsGDFvQH6Rm8hTbTvrYh5g2H2WEdohfXPvqtjoC7zzIB9AE7dC9ErkhZJDT5N7xHq53rrCBu/Q+yS+s3qt9XbFaobQOyWANVTEtq1wKLkGhZCgOLfYVyQoeUY4'
        b'UXFB2Gm4ZJBCthqLkqQkQ5rELu9SlFR454q9kZQ+Shq8SeoSK13JgHfJpIDNrUhRhoTEGp5UrO0rUpWhFBqoDIJQH2UYpJGhBjnKYAinkQOIdBq44dGE2TAuXl9gBpB9'
        b'XWaeyYNcbALZTsY++U7mFMl8JhgNtCjfTuN//lv46+AvB2R9DkcqfySItTA20HHryUPrk1y3+1sqq71vxCg5oa1/XNWKL47YIylJdcWtFgl9mKuM60DKb4Jq4RHOBipr'
        b'e1I6i9pbGivrfB74HI2rQnp8FWIxupUtmGWnckzbrdllrkZD7+2IELV4cC+gVdGj2huumV93ErJtyfFlY9JuwxMr1knDgws+5tvtCBBn6LtN4nsu6cPOVnYje2Ks58bY'
        b'sBPM5xm7mc445uLpDvNjHBQVoUFQxynIrBAmo49iWD0Nsj9DsQRFvAPU5/H0Bt5YWaoMzoyr8OjS+zDb6G3lHfzIKJ/fIRSPxCHD2mJtVBEHj7+hw3JDfvtQP262zBe8'
        b'A6hLNeBfVwcbKW68pl4UGX9HMBPlW3ojUD0AamAv9pJd+U9EU9jL0L9CHzh9hVS+LbvLNIxPU97F0qYY33MDzUlIPRdgRwwCOS+HRWOqf4pqH2yXxd8KiAPiDD7FFFvE'
        b'BkQdseney/GDmg7p/8tEV7DqXacN5vjfqGRtZyXVNKypFTOsbGxUM/heMags+NTRpUp9Lq4S5NAjrKFaIQgJw1QKS4hyhGli18MU3CFQHXmzjuiZPWiy8I7wUYvP31TZ'
        b'AtXtG6uuzBwHGB4no1Yvq8elKUb3gxy+EQ0VVo5OnpL5ttT4trDse+/gUawpQqwpQqwpQnxTsLuhMYLJj8zmaReNa0gdmjgKuI3JgVYx1f78pap4D4CYktSlJakXtYTl'
        b'321QYmwqpI7CUNOwCC3JN2GCmoPICHOs3g6tQZwQV3JAMKaSGFvZIqzs6Qw9kNQUbBieUrLWJXg8gFfVBbxNHo+5W5Rxf9sKpDoI9R4k81SKcC7EvNoyuyzZzsx7H6lV'
        b'8ZOu+Lvax8bKlx8b1xJjXGErpHEVjXGVzLgG60cqVwfyJsqazQaPOuI6fNE51tAbfrPC5oDH7Exe2oAPhnxSJGMvNPvFJThIl79r38SK+hs+Q3mDK7uEFdPTFmrzeKqa'
        b'mxs9nn5S5w6a1rU4FoEw9iVdRsOkPJCDQFQtercPcjWI7vKI0B6EfWafsJM3xAJLoGsQdTMQxg0AmOt8gWgSIueKt7qxkomnotJ7oJkdPJt7AyZTh2B/02H3RVxlWfWi'
        b'26BBndPKyQvfSvDfdcWwaCU9NoKmVE6sEQpNG0XYIRFZxDORCJODL1WPHudD1T3mgyhq966vbmz11631RhNxX/MAkYml+j/HUc6BBvr8U3Jz6VgXINtQgsuwKzXCNmE2'
        b'0Y2ty8fLl92bqA6HD3nx8ED4Vha6bhxYpy7QABPGCJFX4VLH4XEFMgAAG1jFGkYbiQTzH0j4w3ikzmdzK4V2S7sctASFBhmIe1wrlmx0WiT4F7HnWh7vk40vADNkBO1r'
        b'nEGZvYcnrl5CyQ4oaSDkZ223Qcly0AqlWYM27NqgNZODmGshprXdHrSrZ4K8/5EgyoXY4bs4mfNJQTviLH4tKPg1hWpfD2nr2MyWjMNyXKIdljzEt9z2qBPWBlCTdY0K'
        b'DHfUGmj2KHXVARKYoP0BdpgAzK2qqB0j4kLyE57JCCArT/we2nsc1c0+P1P+i/IKnrZAplG+WpUxG6FaYQblCEk+z/W6uY6E2CNw6EbQ0EkE79LoSBUt/zv4VFrlsuG8'
        b'TyIbHl03YKMRZIwB8WJai26hpMTNl7gzLpZCptacNVujcrHG2XlGbSMRzTAExEVo96euoV2HIDSBIzUXL8N4Y/pRQ+I8bV0y9y/OBRfW5XXcoFEIwSbaJIF3SGhOzCEB'
        b'DS66nMlSspQmp8mp1jSHTXJJLgudDuXoIYsffYzuWKDvKFgzr7Dcwq0clT1dKtFv03YucfPkV0Z7eLi+R7tHidOp0sldJSZyy9wYRV6if89pHNoMsGjnylie6BZ2RwHP'
        b'Jdwo6Mf6aU90kyNEiEFiU64YhAjyO2OUCh9NaKps8Bq4ijqwBxhlNcZzTiegJaFh7aj23ASzaU9JVA2HdkjQt40a240CNgGXfwkXRwEnk6NAFGgHehcoSwloV54ZHFvB'
        b'PNELNaJB68podgziWBWnkgh3m+JSkrag2TK256dEnbNam5o2GLXtGV2OnYEyAga2Xj6OyuQ7qUzGb4CrSLwHSTHPQFU+tq0KvEErwD6JC4sIUDZzz1PHeRB598UQKVp8'
        b'Mnt3MZWEuhAVnVBS5gfCf1t6fIv+ETM06hV8L/unHfAUVpWrY+PKt2V0KTAWpXdUzThKJSTEIDRMTyDU5vk9TCiGgSEs83iuiSs866LWxiL1XvxUGkqFB4rQiTJshDUC'
        b'tFeHhKkjkCzfTE7q7hWQE6iOwYHsUmExDhbDSNFAUq8RupTDf+cRPYGcazuRHxsx5FzEjuupPZeM/axGzHx0rKyeRtDq8TR6fR6PEteFaRcVSRF65yBgPgGu1pTlIHgg'
        b'4ebSG8qF36AhcSV2m6IU4xJaiLRHSa+tIwhe/x3lMNwOq+y4eBchF6tTcPSmxXaF6XiZEdsa2AFw78N6OUSabw6rTXTINtEpJtsB7outaNszU7+5r9+t75jdT9+hHQ/E'
        b'4DvPDdTOSvq+67S9vYNA3HZNELhHrBfrpRUWLxNDQxaf5JXqrYC1GaEQX8MTeLStsDGmHIBEBiLtxFxzMGZGNLWiqt5bHSC7e0Y//QO8I9XWC8QgmBaIjYjYltm9vL+f'
        b'c6Q6votvtKFzy7lkELTFBEHqVL47Noozoj1uWg3soRHfBXlsZqmITbSlBjiD/iJsdBm0SgJ6tMGhXsYkiQkKiUE6mdgsyNxyFsMCMVRD1pi/VybqT4FY1k4K8DDPYpst'
        b'Y6G4o/1O+g7wmTRzokcdpUAprGfytgTLcCFEXVcS5tgaMCRxO2niSwFwG6UYu0ogAdo0AnEZ39F9BkWZcPHanNkFpWO43oSuS/WSPKJiPr7YAo1DxJwi83B8R432nP5E'
        b'hX7LvAXFKHu3Tbtj1PwFa+JW6gztYWue9oj2dO8rtW/cSiXUhE4TAV0xbCFE+5ntNyHTTDQSOr+5uaG1pctxpsWYP31ii8/YtcIwnsZqAIjfPwacLAyTlwIbWrzq3fho'
        b'j/HnetxV5UYqdacUY4bZ+Lbc76hfMUvQgzJgaWw5XrR6Sni01WysHgCFKLS8Tjuo76GetuexvtaOdQLENfrO0sJi/Qwevuu7iovQY/sah34gVzvY7egpxh9BGV3YyTni'
        b'ePSnFcYz+i+Ip3nQd2phGClALiwjaRvm6NlikLl8x19nklkU1F2ubvUHmpvq2rxKTiNQszl0Fq/mjPAGVK8XLaw2d85gd+/WXSn65WhXgkzLoPJzXa2vWYUyOtmmOZU+'
        b'JQepaDSDUakodczXVU6+QQWNcOfnMLq7q0J0XBW6FlHZ2Ni8zk+WbNRK9FOFhl59RaZhlxwDbfd3zQ7ILDqdFK9ZMB/WEBLl0YS4Mogn8fe6ZyuDod8nmYJ4NmY6jM5+'
        b'SQDkyXkZ2jb9hH56TBJANf0kCtbsnswsFj8Lzwe0bWjDbRdG4TnRx19VV9W7Z/FVcetO6TywkmssdFRmXyGSfJQMOyEek9lgl5ToYExUrIoNiQfFrjiAOJDjjsdsK6y0'
        b'X9oIO3ZFncaSWAD0j1pe0s1eSmw63suhqFQdTDOFPyi2SzHW3RCgEPg6lKbkank6okCaQlDDMXbd1KBgfAH0M5sDukJC9kBQ9PvwicJSNuSODAloC2P+CUFhFooYWCCd'
        b'xYxDzAnVZOTWCzXwfifPmx6pZOSdz8WFS8w99LLJ8MfOd+y4NOrwEO/ag5x12jcQX3IblmsoYiZxBltUb03deg+KaJK2RlTw+S/dyudjkqmCBKAZfn+VLThn0NC2RAa3'
        b'UX4g2fApGDv6orHoJHTiIYSVixMIOYpDgnslTIdaCTsMeUM8oLIoxAqdt5VxhlAOwH8ZcYsk4vP0DwhBCWUF2PmqYt2BXb3U5BvdKyk22IvXUwqcRDQgAIvkzTDQlMM8'
        b'eO8AyH0rxmFfjPcEkVDjZ7PA3qzpH2TmFRLKo5bFeHYUFWf7lKhUjo7KLUsrG1u7Hy3GsCV2tIhcLUVokA1OJBP/ENRFOE5LYrsF35MILdm2/CkKLpCJ0aKufVzd7AOI'
        b'EiDA5I+XNGGGRyFL4gN3cpGLiNJF7h9BIoMl5Se3f4xJhVgFwBXauES/d03U0qwqXhW5nP7WxgCRFk2drKfvkn1wda2fLpl6pbxpKdYhOHhBQKV7+RuX6BD6o0qbI41v'
        b'6/cd7ex2+hhjoOJ5Xi0uPZw9l7WLgHeRyBDpixXi/CKOvHiYjbYtKML+bVVtKIOCb+mdYIjEI2mDTFbAhr0w3jZPTSPKf/ioz0y26TLs2eV4WfE3cLDr4Pt7nUQms5Ob'
        b'SoJgF68co6Ae91aaVWEu/nAdBcGD2I4sPNwidgisqcMoDg7f2EkDfA3QkwhPcwMAjIJCBuzIN/MkoAFA6zBPWC6sFFgXCnI7fcnmG4yDZ6+KhT3BG+jTDIbFyuXsrFXw'
        b'eGiOdWRc7WvwNa/zdW6qOblD/bkd8g1D/XgUK6uF2GHJNPUYHFPLib7jDITWZLawWdadrogmenwo0IQWsiGDT7FbM+ImVrJxgJHBy0Iy39a3a/fGJ+0GnbCPidV2PRd/'
        b'1EnzBvEWxGAE9lQHRAiTWTJ0/xD6YArSSAzKQYnAfX5AYmdb9bAV1EAuhwQE+uaJrqxW8cb0UK/FC61COtcBWh2NzQMKbo1jPtlM7rI6CoN2xk+GtsQtyp5ZwQim/txJ'
        b'BkAficjwZb3VDXwbRYvlsAzsPZLn18YqTk2o7or4XxJu0kkMLIDUR80jFJuUkZ48CGh1F1HqQe3AWmJSbtcfYCipfnKBvh2NVA3MlLRntKMFPZovxz/ylxvDQ5KIEjfx'
        b'D+ZXwMQ+8MvFmAfSCwbeQeI4yLJkfNfkqG1+c3VDSV2jt1xFUcguuEcXoYh5HOPaMgLTnxYQFJ6WHiOjBfpGB58ZyK2ESQVXC/EsZeJfWlGDz2OLHQt29EFvwDlKs9fw'
        b'CIC4ZId1qL8Yhf1wuDZxdAbsx3i0rqLWyio/iiBEbSQQqNSpUSuKzje3BqIWTxP5viEnw1GrB2MAJh0nGRGVMAbq1najJ3AqJFhis8pJCEIqIQky35ZidlLPnE8EazGr'
        b'QWgyhkmIIssPdRPbksO43AAMIXBexvlWGkq+bTwAKJ5rA9ys3gJAXFQn34ypZHX+MiCy7xtGLEKWF98gqdcHrIqAfQ7vbIqR23gOwRyqXSzn1riALJdYjy+GkKHUbyk/'
        b'n0Iwrbq5tVGhzq6sJn8EOdhJHx3Yj39Hpi1x24HMg+6kLopamhqgg9UGfLZWLCZ6PWrxqirAnmZ86VzU6sPoxhd/o9fbYkC9qBW2G8pqda9LOSph6ekWU5WBd8Emmkwr'
        b'WSCNWBwF1NduS4z1P6boXZ2mkGO8JHWYQrMS5iRv9rw6DEZBMkfB6BncHS3UGDZBLHX+WJMtahM+EwPqYgq31YcVGWaJY5Oj25a2pFhFWYy/hVMxXFHpNBOu3tgbmxxN'
        b'HHkBlhVaOnlGyXHzkj723jX5ceXhxDT40gLjS9PxAnSNoX9NLHtJvQHr0mR2juqLVe1ijSSPB0AucltHWmLHxzbCrGHwUuMqaUTrJtaM/8s4A0+nEcwwuYHYPUymEw9X'
        b'Y2IFJKHjo3GqbmwGJBA7zpR4kTze9dU9MI0BxMDavSx+2BwXr28WB1kguGZ62TSoZ2iobsLLRrxsvhR2bg1EsloM4tUmuRyuFCeydK2tZFDlcf2wthUdV1XoO9eigqp2'
        b'WDtcauES60XHqvxu24PVuJNubow9hALnEhCgMRYRynSukJTkEHOmI4bkkK1GJtatHbaJFEaykjscPNGyw5bBDLfhuVY8sbranRqVShbOKukG/mIYB9L7Ac7AFUgAAElD'
        b'c/DgDvUKC/USqm5T2KIIAZmFjG3CNIHUkbBwAxY2JmftUH9HIgQMV+IQNDmNzHIX2httqaz1Rp1+b8DTojYrrdWA7TsxtWfp7EWLSyvKown4jazUArBK8HgMb9seDxNO'
        b'96DfFhNni9kE+K6xxLKv7JzwqSSgC0AgEYvtmXTsjQltaLB2pCyGmuQ0VfrIbieaokGYsL1zajOjMhcjktiyWBvmxgCE0JZKVenyubxLhZAbaDdhRDhu7HDpoQXzoMA4'
        b'XvWCuioM9Co+oRw70Jsi0Kiw3W9mUu/03C4CFi9mcihcTW8BAbhXZoIfhHfy6s1hwCAVy2ZhVzJgntK91qBgbmRXcYu4a5g8GGHkKO/+OTbTMXTo4tkLr8z5HDXTmOzj'
        b'etVb4yBUPSqsqzKmQ1QGRKClNUA9FrUorU0tfqYNjEQVnYpGLetQYMHgajLARn1KSYSa1Zeu/q3uxrMZiymrTerdMkoc0daVSjwpoAITaAxYxaL2ud7Gtd5AXXWlOgWz'
        b'IA1VvFSbLCf8S4oflXqe0UmHURaLp3FBDJ2ktqHPRWNVUR/TM1BFgLWL+CXMByxAH1rSOJRfRdscLNyPhW2K3G5XrO0Oxj1oT4DxTiA51z+2oxyKM5trTwza1RfNeMFE'
        b'GE3kS9yp2NsTfQMp7IDwGSUBvppl27DsNS1d6xJ0BgEJzeIaOPVtzFtxZnLZXMsvISdX0HUrr05WEoOuBis+BV2sHHgeGHTCFfO2GhAE8lRcQSvmqYjtdqiFi9WCUsJ3'
        b'lC9nZeJ3lHdRrEFLMDHoAITAXo/XhHqnkrIDSJGgQ23BWFBbmRZhavl5VC45j2Ow5DyO80ehjLde/Wrxl9NKiOfRIU6ZMoUGLip6AHrwSxjFyOdE+RlR68zmVrUOgA9f'
        b'6haiFp93nWc9u21wJzLdAAfJ8DbW+bx+BpSaKtXaOp8/2gcDla2BZgJmniqAVQ1RG76safYBgqs2t/oUdmISwtkqVXsbG6PSNQub/VFp/uySJVFpOT2Xz75miTuJzXAS'
        b'AJAoA4lUcSz+wAZAkBOwAp7V3rra1ZA1q40DI3gaoTpe4xnoWijConqhFlG5inFR7L7WJg+lYLLGEj7DW+/6AL3+m26sE5gEKUmGr8AFVE4LyGY4vnQRFigRe4HRwpLB'
        b'qiOdNLSaIvQnlp1MKdiiw+Umc/K3qKsGe3oyLbu4gnrkuNCepXJdVxidgvWnk3okdeYpQoRD/aqASKQU7qc25M5sNoyQZKNaCq/IQT6DyUtKihVhWsBisEjlGM0sEqOU'
        b'MX7tHX1nVKqoyJ0ztrlmEuPXky0Jf2uTir7yOgouRc29qDhnyMiCod2QqpjcGoIn0hVztUMrGDfA0BKrMbl2KFtr6omN74FAQgWxsCVeQWwQdTBWf+yknvTDzmOSDil/'
        b'qD+f1k05ENMfcQZzDvWOFJJfj4rQ2qiLZnkdEOvVzY3NqgHNWeYmCUeHdZ07c1f96HdjNdUhKboAZzwqNDFFyot4SmDAYiNbwnH30smkCYrVfXyvON9O3gD56jO8UUwc'
        b'o+DvtFXVyTLYAvlMscRYBslWm5TlShtB3nXStQP6Ob+2X9uX0LJG5AT9AD94UQsK7cUwAJJmE8vLTTV6bUuNftbQ8F+n3d2p4c8FUNBNJH/e+knHkArJ0Hd0aFswNWkP'
        b'37ZQpKUxSn6hrXSWBzq2pG7D7z/g/fsBybv+9ucWLPnzsj61aXf/eIty6uSFa1+wnPaFviq8cvpt4cisW1df4zzz8JR3fC8deGPFtfXH737y9I8nXfjA+o3164obPvrN'
        b'FU1JoZdfaf/qt80bj725Oavq8jlfPDlr+6cpJ8s+fXHL3khpUXL7O8MeerJk/qeTR98/Iby8KNX/9IzP3sg/OWdC+Nmnp3/2+oCq53+Z6/o4Y83Ce1JCX/Rdc82bkbyO'
        b'WycevevF0dclVP30pcs37L99eHDQS7N+cWH7H4p++lTp/NN/fajP5XeWPPfbJ99+6OWPsl858NE1Hy+cMGzxppB/4rv/da2vdsx7QmZmy2vnKs4PGf/5KffpnJ2TVo75'
        b'LPnqzB9feP3zMY/NWvl6wnVfl3sf/6LsyqUPzL1n954H88cfefmqW/WrVzY8/PE7Fd4RU5a8c/9DhV/mbPr0+5WNUw73efrJ2aN9/b4dXXLn7tor+04YPch7X/4Nn417'
        b'u/yh9+bOGPPo/TkN28fl3n7qp8+9fs0LVb946b6aFauGVy6Z+swfT2wR/nzzobwLn67KW/tJ5fK/Jo1+87Yhv9nz/qbGl/PeStj9/e+ll6tcee2QL8YdG//54o+alzeM'
        b'rDr4u08ioWF/XfTF13MzvNO3/rw10ronu3Zfa8WhL1/9xHpi6y+uCh1cMvmL/Kue+/yLl9Wqde8/Nn/hhh/95ML1d6c/9lTVZ2PSz7dk9muy9nvpD3vnFEeqQn8Zd+35'
        b'vVOXn/AP9P7nM29fJX91ou7hcZWtkz78+ImjA95KXPT9XT/b/9Bb3g8HNB2//quray94J58Y3baj/Zr77npnxg9PtW8t+vG4t0I/P/PZiMdzn34k9/7PTuyV1v7+R2+X'
        b'aB8//vvH1l51+pNK/brx+z749ehD19wY/f2+I8crf6q+s/UZ5fRfJp4IFr+3Jvzwa1PGVvzs41u+OP6bH639+PP3vr3+6rJHv6wOpv723v25Xz189tPZyzu+WvTU++4J'
        b'v3dPHXvgychfM4uunnT9Gz/9w/fe8fzbq42LB97+barnrXp5x0s3tG0f++abL+x/buzAp99eN3/y8m8u3GULBjdvfMYVOPuad+2nf3Bv+uhP//Xib1/5+JW63Reea1u/'
        b'5r0bW94Z8ZHzioZfXfF54r/NXzLh6KGrg7v2bf/yZ2/vaCiqO/IffxRXvfbHeQU79rQdn/jbuuqKsW/sWr/gFw0fls5JH/fEt8euX1pbcXvlmQ/ufPuq2pue+ObKtQt/'
        b'ffzVHxVeeH/41421uxP8bfxLn5bUPb3jrm35czzcHc//KnHss6/dtWP+nsjVLx4f0/FL1/KPHl9f9sNfPCL+26dn3ihe9edzj556+S8H3z6zZMOzz/96wB0XAqdvO33y'
        b'T+8u+/zru0L+Xz1w801c3Ztn3u3IdyeSwz/tyJgh2jZmaKtifmmRdkvuMG2XlUvXN4n6k9pJ/RjZ9tQeGsdjtAo8ENc3aXuKtZ0YLUU7J2q3T9R2kVl+hdf2oZ3UUm37'
        b'yJSGuYV6hONSta2i9uRw/RBTl79Ve9hDlnfLi/JRGX5vin5a0PY2afuZm9/Dl+k3G/6+1fVxHr9F7YR2RytZ2hi0Ttt4sUxqtXYChVLr9SeZkdHQ9fpGdqJrn1u4Wjuc'
        b'jxzTJO150aOf0+4IoHGS5WvzoRKkWmpkhc943q/tZGbHBi1lZ/7Byx2S/pT+fAB3pKXLtEdZ6cWLqfzSBWWF+g53d1GBm8ocnLbjqgAievo9+g60oBwv0bFbe7AnkY5z'
        b'2tnAeGzD/tXaY/5icpS0q7VHkYQN2kZW1Dr9gF0706o9Ta6bh2jbtTNUx43enpjG+u0Tmd2Du7V7NNgqnlvUuVPom6cDEvh3bUvfeXFP+Cdm9v/LxZ3LEIf/Jy4mH6yx'
        b'uVLxeMj+A2q0cZUyLwsy/3f8PpQGuOwuFD0X2X+qHbByq8CnpcJzH4EfsVDg+2bggXtuoSwMm5GV7bJkTZcEgc/iL2sU+GGtEM8m0ZH8kGS85tC1/yC8plroCvll2fEp'
        b'WcRrmuXiZ6fNfIPl5/bHUIaTvrvoCnkOa3Yi9fCtBLGwxlmDBX4gxMyyOnkn5TXQZaP7sGvx2nccXvPL1RdjZ3Zb/3f293LpJBCwt67nTLT7vvXx1jgQ1AuV2s7i6Z37'
        b'kxbBTceVLQ7Q9ui76h7b9ILkz4UpecjTXrS71PeL6cmzn5kUPnB8w96ia3fXLj+0ujb6vvOt9QPS+m/JnbBz3+7M2za9e/rllAf6Kbfd//5091qn8NdVy07e8p+JN179'
        b'QN6GieMGnz/9YcLhvMKE6yqv/NgemuH5eVrNlqeGff3YlvF9bizbcOsbc+q89q9GDA4G3Pd+1rD38z2/eUHa8+2jjyxc9t7MPo9+OW//9Ucyfrfr3b2f7Dg0auW8OWNX'
        b'vv+zrPTX+6cvOPH7Q98sjGzOnD100cmX/WN3Tc5vTb8j89XX3629Z+0bHQ+feeuVeXd9vWjOH4dOPbU3/RcpH/7pld99fmqQLeHtW0//qM/ysmCt3/vjDx4tnfO75cfC'
        b'A+ZdmLdyQf2jp0+99vSsrx4d/+LO4+N/WH789Iv/dfz0By+6rv734OuDm4/d/7tc/bcPPrH0s6xQ/XU/fOzuZ14avrf9uYw3fnPlmPfbTr38Q2XXw5dP2ZA3cGjeY8P+'
        b'srLU9aeSb5/fMdqzvPz73kkf3PbB4HuuHbjmzT/e+RetJrj74Knmhmvfq/3s2S8nec6Oebzfvyt/3H464eSj70f/MPms4n330xeX/Xj8hWETJpf5zuatG71txifFb3te'
        b'fV10H3rhjbdWrStoPt/0u6cW5QVr3z7+4cns5l8uvvBn/Y3bjv7hw7wvhx7qmNzx4r6F/9Hyq59Me/8Hc2T+1I8G7xJuGVFtTV9y1cwBieNem9FvQOC1mYNE58ltU7af'
        b'2CVuH/2DtNBEbXR5yy1jD1ZvTXhlTaRg5W/kp2xrvlpfIfZ9rmbZNz/zvLxn5NQjI/O/+lPSli/ffCDhvHsKIQbS1EkyYBJsQm1He11sRi0SR+uPabsZrrNZvz3PQHa0'
        b'o/p+wgg6kZ0bKsmwj35iQonphFM/sRb9cPLayZHaA2xr3ayf1fYUaI8VysNtsLNu4q+HiAcCzAZDbnpBWVE+oBTb0GCVvos88m0v07dZucGLLalaeBrDzR4dpJ1IIHPq'
        b'jyb2YFF9XAJhXe1ztef0/cvKIKK+3Y3xCmQuaYLYoB/SzpBXkDXaqcX6tpFz9R2106Cic3ntietc9EUPTde3lek7Rwj6QcAAfPxU/YTEWnB/gf58AVppr7Bw8nRBe6TQ'
        b'tVS7n8wSzdfPLSUkbkQRz8nrBb9rtH72CuqWK/U7xpfhN3cpoBs27fm+2v2CFupbRwmXaDurAUEs5PRz+gOcEOSnaYe1fczl6WMT9M3aMf2WQuy8uzhBe4JfUmv4NNX3'
        b'6bv6xtn3EvT79IhDu087Sq3Q7tUfTiSzi1zRdE5o50uytYPMIOg57Uyqvq2imNd2zII8b+HnLNWfpt7NnVoJxYUBdcsfqp+dq++FbkDEDDGxoeMss2xVbBA26gf0LQmA'
        b'rpYVafdkO9Dv9+PoPLWv9qykHbhOP0tIqVU72o9spkGvoLW0MkBKM1cPy5XGwNx5hNw5LgnmwiDM4x36LVCTO/mSfO04Vb+/o6FAD4+06nc3wIdH+GX6Ye02qn7yMO1u'
        b'fRtgfmKxtosTbuKn6/v122jUbdrNfcsIKupH9AdgnIho3yToD+qPZJNR06B+B8zibRUVRfpt40pxKBdYuNQrRO2Y63JCxpev03aPX1nGvNlWlFMWrhvFWdrucVRh/YGl'
        b'AGa3jZQ5fvF6/R5Ov79uCc0NcYOfWdzTty5E/7Q8Iuf6IzQBfCnQq9u0I9izo7Q7eE6q4mF+hnyUcsV1+oNlRe55UBN5saA9oz2eoT0OA4LVmaTfM4ZNYj2cXYrTJ0G7'
        b'U9Af0fYZfjc35S2BoQQMunWyIakrAXmxWdQ3jtC+R02u1+6YpZ2rKSstLC0yvOe69FvEcu209jibKWf178/Dz8u1fVBzidfuybyckQzP1C1gjdLuXrwAutxdCrnrt4va'
        b'09pD+m6ahldX62dmFhSUasdHuEfOK0TPE/eL2kaPsej1h1rqywrmlsKAnIRl1pfXDutPQlKy1LZzqXazvi0fWSyF+jH4fBWvPdNnInk0TwzomwrmWTi+TDtcxul3Nmlh'
        b'5ov04ZHLYVrjrHpI34smxuZDpwRhrbZozzO7tDcPBlJgG7rzBOpF5qRkXjsAjTzG3FE9MFM7VQYE0vixPGfVd4+9UpCvKaSm+LWnatD6pndmzJsDGgj1aw8ys2fb+6/H'
        b'z8v0M6a5d7LOqe+8ijpaXqg9NHxoGVmRNpelS7tXnKltZYBW271cNAyhzkKrSnE2W4HwCRGg1e9bjG5YyWDq94HYJPuunSZT56YRwVWkbVqDAKUIlkg+DBAs0d0AQ+ZD'
        b'oWEovUg7KnELtGNW7XmgbDZpT1sZED+qHdJPJyAN2oKpy3A+pekH9W03iPpDAJPYlHpW/55+N4GyYv1R7dm5C4p5qOV96Ivi/qnUw8GE5WQWeOfAJNgIcI09IehP5Ol7'
        b'qJ/m9VlaoO+cr+9K1zaWFbqLYBD7DBT12/VnZhMppj3A1ZZVFJViKyOlhfNGFs9dAKvtdpkr5Cz6fhirEMXDjpSNbWlHhRtoN20HbjkZQ7Vj2gFJnKNtpW4thvpuRQPS'
        b'FRXpACZ3kTmkBO0ULpMd+j0MYp3TT3Iw6lCvtdppyBmmHIDk+VYuW39CWq6fzqPJtbZa/x7aWTqphYAyhQzRmU+KDlvc4ekTafrM1XYNor7Tt9kdVk4q4rXj7gLWrh36'
        b'FhHrOxI2svX6WXMfwzr3GyJpm5tltt626kcKykoX5C+wcrIkLNGetU0dTMXrt+pHVpO1Ybe+RT8OLS6CztUfhAmS6/5b52mmOc0J/wL00b/cJXbOTLQayhpzCYJg4y/+'
        b'OYRki0RnJVlA6Qi8zP4FicfYLhbHOEFhFJyDSRcKDuMJcgBc3UZ5p5FqdefPSTljHDzQdJKStY0OOZ2CLK6/iev+myTzjGtuGDi1k8mF1haPp9MmoHn08EM+vqV4xMto'
        b'iK+ccTQEfesiAJGIa4hj4gf+F+FaxSl8PfwiS8NLUTYtMhzuAtwFuItwz4C7BPerw0vrOLg7wktR4zAyCOPXY0w+xIeWmtJ07RxK0jWKTVIkqcnSzjfJ7UKTtR2PFa2K'
        b'vdHWZG+X6NnR6GhKaLfQc0KjsymxXaZnZ6OrKandioeWgWTIPR3uKXDvA/dUuA+Eex+4oya0DPfBQS6cBPekIBkciiQE0awuH0mGeGlwT4V7OtxdcM+A+1AU8oa7NShF'
        b'chVrJFMRI1lKYiRbcUX6KUmR/kpyZICS0m5TUtvtSp9I36CocOFsFCSP5ClpEbeSHilWMiIVSmZkgZIVWahkR+YofSOlSr9IvtI/UqgMiBQoAyMjlEGREiUnMkYZHLlc'
        b'yY1MVfIi05QhkYnK0Mg4ZVhkvDI8MkUZEZmuuCOXKfmRyUpBZIJSGLlCKYpMUoojY5WRkdHKqEiZMjoyUhkTmaeMjSxWxkXmKuMjs5XLIlcqEyJFysTIVcqkyCLl8kh5'
        b'2LGZiwxRrojMCGTCU4oyOTJfmRKZqUyNLFGmRUYpfGRW0ApfcsJC0Ba012AvpYVcoczQoNCCGkmZrlwJ4+cIOiJOEnnptF3rCiWF0kIZEDMrlB3qG+oXGghpBoeGh4pD'
        b'I0OjQleGZodKQnND80JlocWhJaGrYT4MVmbE8rOFXWFb2L1ZiNhDzOk7y9dJOSeHUkKpoXQj9wGQd25oaGhYyB3KDxWGxoTGhsaFxocuC00ITQxNCl0euiI0OTQlNDU0'
        b'LTQ9NCM0C0ouDc0PVUCZxcrMWJkWKNNCZcpQHisJ8x8WKoAUc0KlNQnKrFjsxJBIDgUSIV5qqI9Rm5zQEKjJcKjJTCihPLSwpo8y20zTnhB2BROohGGUNgFKSaT+zIIe'
        b'6g+p8yj9CEhfECoKjYb6llA+V4UW1WQrJbHSRairSDlJNzpwHNud4aFhZzg/7Aw6w6Wbhc0oloBvCulNIXtzozOYQGIfc5jHAlIUYNL+CCV6l2vL4ZilczSo2WBX+wbQ'
        b'7AhXz5ty4YYGc0f6UP8Id04dEzWtzKlqrWsM1PncgroeoQ+d9+GG26vRLE+Nj9hmKL52n8VQH+bo4Fl9yVRxcUsA6Gq9gRoV1Sps3vXVJHJDKu54nN5cE3WaYkckbsSj'
        b'+ZMmgIzw5ECj3k0tqtfvh5DY2FyLOtAomaai4ZHz2OTzWOp5rNx5PJ08fxAvnClm3ax4Ab6SFQoUTo+KLc0tUQfkrnhrKlHtwVbjYee0TOOy00pFDCZH5RrKJ5pQ3eyp'
        b'VGvJ4Sf6KfU0rGv2NW6IvXLAKx/LLOqEZ3+g0jD1aYNQTWNlrT9qhSfKzE4PPn/AT19JpJ5KWFupdgZQbhdDlI4eXPRW9ZOwhK+Z8mmEAaysYglUr3ctWm/HAMpCUMBS'
        b'3eitVKNyYyUM8OioWFVXS+LoaBGHefSIOtALNHtm4kEvGYMcUCurvegz0uOB6FUeNpBWeELhhqjkUb01UZdHqfNXVjV6PdWV1auZqDFMDIWZbEO2QIcwwt3NgR9+RdKC'
        b'mccSmNsgFLZC41JoERZFB2bhIb1AqrbCZqB+1/Q1bH0ZqsTdjaX+LWNRODm/jkmpGdiAk03aLnVEcTTZrOM5+Bq2AqRzwsLKxpoEeYBBQg0qYQxUyFEPqWaI4RwSEZOC'
        b'UtjRYFNvDjvbLUEhnNAgqHPhWfaNoBCnrgo7E7h2S5hjImVhRzgVvrig7c5M7As5bIXwgM1CUA6nQ4mC74GgoO6GdwPDGTVoRmcvioZBOX2gnMcodhak7o+5+dbD+0Hh'
        b'FIr3YTgF4I6VdNey2m0Q0xpOg5gS7BXQ15tRRebFoAQ7CE/5yQ22W1E+WIZUdsq3H8Qyze44IAcjZdAOTw58IqdGEF7MsfaHecrjRkibFE5MMLXnxHAyfU3MQivBQO4p'
        b'QITgt6AA8DYxk2NqXWTV1M68HcRE7qg/Ic9DMA6OcF8oXcB+CVrSUK0li/UDfD9DNc40eyLYxfqF2/nfOtwY/C/AYv67uNA4q2U5JlHkYtgq4asoTSQLNpIZSoVfssj8'
        b'LDEpIuZlSQb8NouXRJfgEpL5/phOdJBPJpfQZbGkGPsPLZb/EIzF4oKhdhuLJS1+scBXEQcvLMEeNarL8sHBK4A0Ej3hxLcEJf/HYQtMRjmMvwwYdBGl94JW9eaglXR0'
        b'bEEojU0eWC59J3M+JdwvnBceBosgu8aCtqBg+i5sd4RR8s0BuSYEHeF+sCjfgImXlMBl48YswrMLn4NOWnaQTzABUMQkYwKTPCD7FnSQ9zBfeEg4MdxP4cN58D8M/geF'
        b'R9Tw4RQsJzwIF1caoJjwvm+YDyeHkxE1q7PS4rbgJIbFlBK0QWsSYcLDPQhLI+zK4tpd4VRACPCNK5ODZZNIiEICpCokf2MBygGea6DFO/l2i+8zeCOH8yHPpGBSOIu+'
        b'A0CA2iaFcyiUY4SGUGiIERpKoaFGaCCFBhqhvmY9KdSPQv2MUB6F8ozQMAoNM0L9KdTfCOVSKNcIDaDQACM0mEKDjdCgWL9hKJtC2RiqSYLNoQjR+yC3E8EmAgFoa3h4'
        b'OBFanBxMvlXwPxSU6GrFK82VTJwrkAf0fQ0aGTdak8mh9iD0Zx+cY5CrSBYhJOx5BN70viAo4fugZFp96TQgnvJ/Zd26i/8FYMf/PHyahvDpzk74hLKLgs0wnS2LLoJU'
        b'qRIpK+PvL5INv6JlVjR3kSoLHLzt/BcELtV4dvxJcqJyMxoAcwqpogPgmIvv9fd7KdUpJvOpog3PTb+RLE4Raf0ukM5UAiNIx+xhAiwDMjpsMyCdHObiIJ0YttD2DghM'
        b'2A4EAEA4JiEeM+vC9Ya1/BNcHFAHH5dN6wCsg0XskG6NspuNegQbJcGSQVxEAACdyhqymcRBAS+wQCOT0QAovZeCFBOamBiWca+GrkgCkJWIABxDKPoeduwaxmOuCeFU'
        b'XJLYWQTORAuA27B9AqCEk+OE3gH0ARAFMI8LE5+TIQUJcKMnJEprKuZ8Vwf2+Z+dyedkw2olR3MYVaAkq4PvL6LqT18RZ5Oj62xyxHe8gkgmIIThJESAYx0vGR0/gjo+'
        b'HdAy0V9IXzCcgWGyuj8LZpgTNYHpm2NXX+o61JK3ZpH2AYa6dDIgdWFrNmq8SrCjrAqK/ltMVJvH3CVAHHH/tag/R++WCE1h57LALgOD2G5tcyDTgVT40iQuwDU41J8w'
        b'2znMOyelycIc1uwhItwVSgYCPC2UWWM13OXY4kqxIXSHemSEE/GdmZrte4BN2GFVsXpa8BrL3Y4sD0q5EFLCO/hij6WM1QEQ1CGd7nd6UtiJGeuN+YREagQaDB1MTiXQ'
        b'cgR6+EEjls2FiJmS+n9NzGCWW4wKgSo1ijTkb/i/25ZH1FXn9zRX1XjWqSiordqsMW0ayTDySPPMzROZ/g85Ecn+VwL9b8uGipS5YJLh6qRNAIXY0YqljMaDBNwKHKKD'
        b'XK64eNnuFLOs+DbV6jKYt6m8O4txHoKYO7nfEP0b/OqP8N2P8fITvLzMJKnReo9ffYXUBtoa66rUf6fHpsrAavVVUsGGB28lOndQf0qqMHWKmkeZAlUeFSurgJ5fXelH'
        b'Re2o1TBLFbX6zYfaxuaqyka/O/Gf02XuZf8C3Pf/vfwjxxU4J29HhkMU57kgSBcfVbgsWXSkgMcH3Y8y2E/q4efs8e0//pON/1hYdoqpVkmcPx7XXk09XnOckjiqPz5N'
        b'nonrUrDJRDwKArWzHNVsTnPk0sETz9nzeIwV2VTZAssyoKrbeKbESwYJ2NnIS7TuZq+v9ragfSYVDzvxpKS6stXv9XiiaR6Pv7WFOILIPkMlFnib4OkMqBe62pWI03ad'
        b'3NSstDZ60fQcMzQqAWBJFgAZ6um85iauj/E+VyCTuqak3/8BiT7PTQ=='
    ))))
