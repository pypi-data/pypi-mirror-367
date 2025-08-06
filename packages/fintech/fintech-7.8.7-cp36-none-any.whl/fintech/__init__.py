
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
        b'eJzcvXdcm8f9OP4sDYQAGWMMGGN5I5AAL2zjhTdTOOCJnSCBJBAWAmvYgIWNjY3YxnvvhTfe227umsZJnJ02CU3SpGkznKTJJ/20TWmbfu/ukYRk8Oqv3+8fP/Pyo2fc'
        b'eN/de9/77j6nvP7J0P9k9N9ajS46KpfSSXJpHVvM6Fk9p6drmBo6V1BI5Qp1nE6wjtKKdEKdCP2KKwJtIpu4hqqhaWoBZZ7MUXq/pRJLOU3lSmiqcpBOrJfk+ev80FVK'
        b'7gPINVAvWUsvoBZROrFOnCtZLFlImZmF6CmH8itS+HdGSuYW6eVzKmxFpWb5LKPZpi8okpdpC5ZqC/WSr0UIyK/F6NJBxxXQriaw6L/E9WtVoouTMtA6WsesE1fRdVQN'
        b'VcVUCh10DZVDOZgaiqZW0atwlRSpklUXuPtCiP6PRf9744I40h85lGKAuoP6M/4814RrHpIioOqYENRrGuWQwSOpL/m8P0zpBg8pJgHDwzgpJ2tgPTDRj4Wp0Bsmd4G+'
        b'MHFq+wh0DzfOMMIWuDtHBbfB1rmwTjkf1sHG+OdS5qbEwGbYpID1sImlZswTwnOgHt403hGqBdZYlDV9Reg3mgcak+Fbzb0vlJtitCnabzVHyu/nhxQUGUzMhbXh40ZR'
        b'a6eKFlhyFYxtEMoBdkoL4dYif1RwLC42066KgQ3xDDUAXORQ8bUhtgG4f4bDbaARbIAb0nuDJpQMNIMNIiowmI0CN8HuE5SC7WCiFRY/lJa/4F7tlE00WEor9Wa5gR/z'
        b'yR2BWqtVb7Hl5duNJpvRzOAOwCNEhUvpQNri786KyuMMdnNBhygvz2I35+V1+OflFZj0WrO9LC9PwXrVhC8K2iLF93iESCERuOBAXPBXMkZIM7SQXO1D0JsSpiRdGadW'
        b'xYD6LNKhcLfD1afKUQJ4Ah6ER0241PmD7tH3BRS10/YL+h9h4WWTKIIsv42322K5r2SUZk1+lLFzugtZPp1Cvv5xcTEtHnZOQMk1/WzGYD7LdJqlriVieDQZtvAo/qVo'
        b'mZBqDUbdK9co24O1lD0evSxEgOz3B21K9FsHN+QkZPODHx2nioZ18eA4OBKTmklTSxaLM8DhPAVtH4iHcTu8qvdXq+Dmkph0lSQaNoBzoI2jIsBtDuwCjUF2PIoo8zZw'
        b'Bo9jPGo3/hVR/lkMhcZ1E9iVYO+PsW//qFzXSMOmkfCU10gPDFaw9r4ozRJU+N10lSItE9VzVkAJc5jQbNBoj8T510wCp9JJt6amqhjKH+xgwD64H7ZJjPYolGBOBtwH'
        b'G8GO8izYkJYZB+szwCmOCgY1LKxmU1EN4SjR1ACwLz1VmaqKMBKsFFCBsIFVJz1P6gcHp8rTwWVwEaUQUBxHg/3wNjxL2ggvTZTEwmsUyZaZCpsVqah0uJkFN8B1sBn1'
        b'F26lA56EF9JRz5weOQqlSYctWaikoIHshFzYgtLgloAroBWuS18YiZKkZvIpAuFZdgRsnIiS4LZw8FaWfwoaqjLYCJvScXtD4B42pwweAxumoLbgcioK4VrYqFTDllRl'
        b'nBB1yEUGbNLBi6AF3CQJlsC2ebF9TLAlA3W6UqFKE1C9o1i4GawHtfzoXgtKTM9SpcaiXq1PVabFzwW34lIyhZSSEsCdJWCdvR9OtRtezsRwxKJvcTTlDw8x8MRQeHVI'
        b'hl2Bvg9VxKaTz7gx8GLInOh0ROstCP035MxRCanpnBBWw+1gF6lzoQnsRKnrszKei07JgC3qjKx5OJUyaV6sYCZoGexhZow3g91BOLWTRtyRdXJOgVPoFDnFTj+nxOnv'
        b'lDoDnIHOIKfM2csZ7OztDHH2cYY6+zrDnOHOCGc/Z6SzvzPKOcApdw50DnIOdg5xDnUOcw53RjsVzhhnrFPpVDnjnPHOBOcI50jnKOdo5xhnomGsiwNTdRziwDTiwBTh'
        b'wDThwIgHuziwwZsDB7l4hC8HrlHbh+KevB6u8uUQCnAZ3vJiESPhXoIA4DY4Hk8ISq1SqEAdJpXg59UaFpwFu6T2UJSkHKH7DtiIsIylmEpuNZ2MWSnBY3gUXATXY8GJ'
        b'xAFKJIA4sI6GNQ4/Hsf3wONFsQoVrBsSjxBPCE4ysamwllDHALCpHx4bcBVeUKKR5lJpBEgr3Gfvg0vdN1ufDutHizLwJz8aHB0Ed9vDcJm74DYVYiYjy1MwNFwKjeo/'
        b'AZtItoFGcDk2TsFQDDywEFyhc+FOsJV80UtWpIOTylRwEt5BGCA0MdEDl5IC52avSkcsoBnshYhhoNoG04i/3CwmUKLeaIMXCMbRqNCtatBCZ4BacIR8TUSlnU4nGOYH'
        b'TihpSpjI9AW7wTVSZdHcubFpiKKKwI4s1PhkJhCeGm3HAzYAbgSbSaHR8Dy4oUIZy5kR4DrcZg8h5A+3c4ico1E76EVmenIhuEqGoXAcQLDEpyFQwBa4F+ygZw2A20mR'
        b'saigS+GVhDgUmIbF4C4DnMWgneSETnh8KmzMREoIUwBPOegpoBE2EDADYI0MnIIN+JNuGrhIz52HGhBBiBFsLE3HRA93wc2wiaOEEYwErAN37RjllqZjaFLAGZQxmqui'
        b'Z/WZz9d1CDQgfGvMQkPHZMAToIGePUlMWFb2CANcg+hbiUk2Ni4V9Y5aQPUt4kbCDa4Ov6TRrxqWHouZfxoeYD8hA7b6w90FjAvruW5KDFJhnLRHiWHqkNpSxSISYggJ'
        b'sYSEmFVsTyTkpn1fEmLVxkGfv85ZJ6IXmxab+7z6YgAllzLJuafq/zy+evVv3hIVLI9qDLIMPDBkXcBQWJu5+8oi50t/mj+c+XHVz6Vi/z9Pvj8icDb7K4WIKB4V4ycQ'
        b'abRLhTCsOUsBm1N5gRQ6lGMTp9gwEcJWfahHZHnkFTwykY0Sg922wSjJ5Cn9CJUqMxG7q+9KllcxAGzk4EY/sMeGOxlslgbghFkILUOmIQ6N0khgKwMuysEZG5Fvm9SI'
        b'8PgkGXGgnlTGjlezAysUNkLUV6M0sSrYNCyFSCcxvMSAdYtURNsSwXNJBI4uXk/ggKfiqKExgqwVo13Kz0PqDXlLlJsOrkRrXcp4tJtVYpr/C6QltEXmUZ+4DlZntXWw'
        b'VkuBJQC/xakVjJfGxFh64ftgj9qEM6/2FFzjozaFkYZNglsRHUSBBoSDQopTYmI/o+1ZRY7jsYsxME+pIK97soKMcOuUUEZbsXxqt9PfRAo19/O/0tzL/1aTUlBs0HEX'
        b'asLHvUslvcsd2zsMKbh4OJaNDUxXRiN+l04juj7FDAPOCrhzLkGubHAYnOyGOVP1WKu9Ba/wPcn0PAx2m9HUpb2upsQy2tKb6tJe2dL84kf0PG0J8XQ6zlKHi8G9T1VT'
        b'nYEPd3s4OArPIoTaloHlD+KxFhrclcJ6T7fTrv85bmgcPKnSah4WV3Vi3wYEmkvzSvMNdmuB1mYsNTfhzIRNMPZh6BoS44fYIemarLRYlVqN9dHTAVhZYKlYcFEAd01B'
        b'jOXxMKx7Agx+bgD0rV7VYzosB2dgO2KDfNWIjIIZeAzWsOD2HLCxZ4QbiRGOxiiHrDLuP0E6ukekE3QlcLPPAZ76CPt0cp76nsRAix6uT9YTkhf+4hptTUMv/vqv5lN/'
        b'eKD5VvOV5kGB1KDRRmvvfRFzQaNr06P/wQ80Z7VFhtP6Nm1RvrSwTofkeW5tUq24duKx3FqxfMKONaNYCoQE6FvLFTTPKg8sKJvLWMGZFDUyJ+r54ewFW1nQLsWKL4+g'
        b'3MPs5yHkF+QVaE089kt57A9lEPuRITZUGWEtMhpseXqLpdQSN9FUilJaJ8eRDG7OxGkthdYO4dIV+NeLRroZdYwFE4Al3EMtmKC3eVHLt8He1JKI3o0G2x2xSELWZcQi'
        b'3Y3Yssi2uYiaWp+lxnrcFaRXN4qyx8NzuRRomOIHr8K9SmPJnguMFSvJSlnw0sKi/J8LTYXqArU2Q1v8WZv+K81J7VfIqpYYPs0QUfp24dnr/3Tj9VN1mL9Xp3gzjT4y'
        b'oSWii2nwNuxjOsTbysX5tnj1xZ98+gKzSAtYO8+rL8CmTN607wducEg1ay3smZC6OVuekW931wk49Vzj6BVq2oqt74DktnTUm3WFrwhTtNymJoU8sfcO3Z80YtK5hR8I'
        b'V2cFKzjCn0fDW0iPwrJWrVSpCXsuy6F6gUssaIEHV9uwvQyPwFPwOBGq2EKuBxuj01RxoCULNXxDbCo4E83L6IV5YgO4NcpG9Pu17BxehPukgU2FVATcyoG18DJ0EoEd'
        b'Ap1gbVg5KV6RlqHOTEOmEK8WDBks6A+rU7zxwGvEA+zmgiKt0azX5enLC7xJZYCQ5v8s/bpGvoNFqbxGnnaPd6RnvHHqfV7j/Qep93jjZsFLSJrdiCXmbAoi7ab0TH8d'
        b'GnlE7UJqaKUgC9SALZ6hco95Xy9mRoy2p2aePsyMc/33HXmx2oSbLaX9xLpZlFy/+vUKU9y5UbtDOka2RrIUUZWnIyPkCtyyKlaVimjzMoVs2kM0su63LSdOmCjqz9On'
        b'RUYPYOZ8Sv+88Mp8O+88GammGVRhefuUkb3SQ0r5l/tSe1MYxxICS7IvPSeijOPUpxlrOXozJ+rddK1O26Zv058u+kpTpq0706Z/gOj6gcZsiMk+pX01P0VbbFjXMIJ5'
        b'aVDMtOId1Q90xTuXhi3d8dKapDWja8Q71Nrl1DvrDZ9J1zv6JI3JmKlKHn8sJFQkND2oHnn6r9LLGeufk//lM+mYphele1TUH2YMfPvf21e9jfgubiNsmwy2pHscDXAf'
        b'IwatTCk8Nrpn3vFEjsIVaa1FBK3kPFoNFyMO7P4jCiFCDCm5Q5pJfy8mE+bLZHqun+aTEczDmY95Yd5Hwd1UwwZ4Ht5EBk3OaqQaIkTog6xO6Ex6jPeUfsh7yjw9quFm'
        b'S7uhmlRNLCtYi5DoLtzMIqC0VDwVn5dGUGO5hqPE1LiogGSNKTQul8eXiRJkBVPJ6RylkeaskFAWAW5vD5cOOs/46YyBtLUWPRxa/ScVMlJAgmzG2zsv7/2lou0VwThJ'
        b'3xS6/+sNiP2s7TfkuEXSmFPQWNS44NuvVqtnSthhpmuf2a/UNf24Rb8kfsaEl5omBK/9cEfY6eyhjbv8BI2Lzn2X5x9nK/61/sRy578+e0vpuHbjHwsq/7Lz+9IzgS8O'
        b'NwQvy0hR3q+9fHf4WPj9lHuBA6PW9VL42/DQhwWJwbUlvBLbzUDyh7dtWBIMlMA7VqVCARsyYlSpbhfv8/B2zGIBuJsBt/OmTdMMcB5eVCNLx5UCblscAKvZ0WljiXUk'
        b'B0cSH1aXE8Aa7BuUhdqw/dqLei42DtYhcbtvNLbpQQuj8p9twzQJd1XO9LbBQpZ6yuBtMLBzHKGVUHAeHA2Pik1TwbrUDGTj+oPzDLLYb0h5E20PvBYFNoJ9yAZWxiji'
        b'4AakmqJ+kHMv5E0gSk5REg0aongGj2ri+T+x4q7AQ1YbVifm54H9HrMAtGdhy6ACnAabbdisTwCn+1FBsWpVKuozhpKKWXFGoY8K/xgDTVhmzzcZeZY/hKfNJAaZZ8GE'
        b'6YfQHLryJpsE3UkQjUppywAv+gzxpc8elIAu8wHnu+5Fmq/4WG3Ei9kO6mbAEwGx0ZmISuszhMgibWdANRJyxwqELorCRmCgm6LiWKy+O+hwqkpYJ3II66gapkrkEFnV'
        b'FYEOtphyCGvoKvECyhzCUTZ6qcQyjqbw3yLKHLoQqbwOMc7pEOIyJlI6GudtpS2cQ1CWa6SqBOWHHIJiROAzqOe3LWGq/KokuBaHXw1jMZD6OHR31iEsRspzlbDcgO44'
        b'kjqkyr+ORSn9HYyBdUhaaJpatgXBMYPkkiIopXV+BDph+ZA6SZ0Y39fQJKeY5BR75XxjAeWQWn6sk/I53PDOoZYZFlCtjHkIKdW/hkGwK+voOmqpEN8haAQ6pobmU7fS'
        b'5n+SdLRNaGBI2vl1/q608+sYXLYn5TskpZCkctQJXKnQnU+q0zq2WMTPy9WhVuMWVAXohMUiR0CxWCfSifHsXVWAIwDlbdf5OQJCqaoAp8jpj3Q2VidB+cQOFuerCkQ9'
        b'EFhD68RLcY2fOAJ1/mhkAs2DPO859P6fOimuEb8JxV85XUBVoINpZSyzELw0gZexDNEFOlCOvog1GxiULsgsd9AOZimLvk3UBeF713uxTubg7wZ55dfoevH5PWlwbUGO'
        b'IF3wWPwbgNK0OALJNUjX2xHoCMDl4W/mQEcQ/lK2wxGAn238GMtQK2SoFSGoFYyl0yHDrdNFoD5lLK/yTyjPH9AdwkddP/L+9/wTfo9a2UvXFz1TurD1TDjl6EXgl6Ha'
        b'w+sCcA3FEofMDYODbWUtchvtCKqh19Jmsc2fv3NN7UWq53aKTMiQNqtGdDJKuUfuMS7ZR+xiTLaFiLSel1TRDrqY2sgs43B2lwrZIc7LM2tL9Hl5CqaDiUvooG0PGcyd'
        b'kokmo9VWUFpSNvknymUxC6nKyIIifcFSZE11GVxdCTtZeamlk1Z+TZMSSg1yW0WZXj7U6gOkwE39cjeQoXia1YEFM2Pl6hDANbQPwG7vyGAiHpc/hiVasHL6zy54v8aV'
        b'dgZp5cu1JrtejiCKHmpVEDnbGWbVL7PrzQV6udGmL5EPNeLPw4dah3f2Ii/wrecVR669vVK6c3f6yUvsVps8Xy/vDNIbbUV6C2ox6gh0/Rrzyk56eCc9qNNvqHVxXFzc'
        b'8+gt1ig6eynlhaU2dw8lof+ohaNxG8bwre26l3YIjGadvrxDMh83Yya27dArBIu1gysoLavo4JbqK5Cdi+Ap1ek7/PIrbHqtxaJFH4pLjeYOocVaZjLaOjiLvsxiwdZG'
        b'h99cVDEpSRHc4VdQarZhE8LSwaKSOjiMHB1C0mnWDgGG0dohttrz+TsB+YBfGG3afJO+gzZ2sOhTh9DKJ6CXdoiN1jybvQx95GxWm6WDW46vbIm1EGXHYHQIltlLbXpF'
        b'QI/q57NckJhK8chEsRtBX6dcQQkUg+UfR2PJGEgLWSwPeckY7NJgA+lQRkKescwk8pIJRU8RSJ8NpWXCECJRxegeuz4DaRmD80tJ/kAGy9VABudCb5hAUl4YHYnKCsVS'
        b'lyEOczu8MRfbSpmwRQ23ZyrTRFRgHjveluhxmIu9SeMBuiABxpR/4qCKKSKS3kECjK3iHKw1clmgDemu+L8RCb09bJXAIXAwDnYiIiJLNhKL9FIh+kXCI5wqZhDDZMNJ'
        b'mAUSTBwSBhwWH1aDgyukq7jyhQ4OlT4HCWAWCxckEPfVEcGL8uMSBToOlcLiJ/TL8QEby0y8wLGc1HFlp3VYaAscIlKbkP++gELChkBASmIm8s+c65mbSC0LRGKRIUxN'
        b'oEY0PRuPIRnIVHyZ7bnD7xQCywQ8vKxVb+tgtTpdh9BeptPa9JZJ+Ku4Q4Qxr0Rb1iHW6Q1au8mGEBa/0hkLbJZZ7gI7xPryMn2BTa+zYKeXZSbOLHwCjnl5MnEsgS7P'
        b'XW4UYmvWYQTFOIQMGMVkPBpgRCPIJaXDGBl6liF0IBEBw+KCXVPWoD4enFAijKiHNXALnkGLBVcFcFvxdB/zA4cYYIOcVNRttpPC850Gf7dt46DdUyfe5pDYjVY6dKnD'
        b'g0zXI4lfTJXJEJKhTJbRCC0C0Bsay9Ea2h/ZOURSkfgdxJ3ZOn98X48DUTgEBK5agkCRGsQed6Sfg8Ho8/DcDVb8sPufeDK/xQBwDqwyUBVt5S+galkH5VKd1FUMKoLF'
        b'gNXQSylLIr5zIDCqWHMIAU6I8DoF36E3zBykAJI3YXVYpUH4b0DPGNeJ0hW2gCqf5sDlJlWxDlIqSttQJ0Q4yqL6ObMU36P35MnBWcqw6EHUg8pxcKSMsgU4NCkOKZ+c'
        b'TWBgkAL6CY3USpqqDEQdJcBimYQiob8qwSoBH4qEKAN1XAtNMJtWI/TCdmuHaLnWQryRbCFCYcRCLUtXWJIwak3nkbDLAZmBLwRnnyc4r7dYFOKnZold6CrNI8ywDFVc'
        b'Yp3qQVaEogyDUVSKuR/DoOcwhiArI0VIHIZQNYKuTNAWFOjLbNYuQa/TF5RatDZfZ2tXBUhkLcZV43a4HYzkBUYFhf9/ytzZDhHuNkS1fJFLPM3z8wA0jnbPJbE8r49C'
        b'fDcivDLi0W1w6xS5uDg9vpf8R5In1wOOyFXZGNrlK6BY+WAywT55+lCwrzg9Q61WRSuElH8cA4+A/Tk+rkyx69c6H130VC7S93IZQuxCt+sil90i5p0ZiP78DIgh67h1'
        b'4ho6l/O8x4xBhBiCSCfQCck3gZPiqFwhcWyIOnq5IuJmGU36jFKtTm/pecKWOOkYVBziOF4zDuzTzzi4eU+3uLNR6B7sB4dlVnAmOiUzLjXzOWzFZ2WkqrJhXVZONGaK'
        b'8+BduBvHgCDbsc1vURXcaPyp9X3OOhllDvU78Y3mW80DTerFIkPMtmgSeXaPjzvL/1bzRv6r+X/SvJpfbNDpqJPalsJUrdjwqYmmVCn+CXKbQkDcFClwE7gOL8ImZPnH'
        b'xyxzOSEi7BzcIQW14MJ04gAYRsu7z/ZG9Gej4DW4jXcRnIV7K7vN0fadxA5cCM7ZMClMA3tksSp+hhbuBZv4WdqsZNsM9DEHHFgCGlfwsTLJ4BhSD0h8Tyq8zHcJaMDV'
        b'x8OGDLgBNiEwQD3cgPgzhRLsDIAHp8LrrrmOJ/ACpPEbzUZbXp63g3g1VYQ1mEC6MqIbYsS5M3jmUqx6k6FDaCJfHz+XUozvje66LUXoUoipAhv/VDX62+3t13tc5T2j'
        b'ZyKPnizCdiwShQahB0W5x6LoU0zCidQk3AZuTCn1imFqZSk0FHWB4CQrGwhb7NixOAWuV+OZSxIu6Uk6B2Gzyzl2OZuiZsxbEi2CW8BWeNCuovAc6w54CudKBtXxz0VH'
        b'I7xLUcEGcGJudFom3KCMS1WlZdKUOchvUvJgEkwFT4wHtTmq+SmwSZGWmYFSuugFJRsNtglBDdw2BNaBBuO1S5mMFdt/q282fKN5Jb9N36a9l5+hNRmU2xTaNO1JrayQ'
        b'J5KY31A/7pz6bURt4G9MVwb1k+8/WjtVqswDH724adtbL350f8tL77z4zv2w+7/YKaQ+KA9OniJDdMPHERUshY3pJE6Oi+pTSYND4A5Yyzv1amGD2eMqG5rpcZYtBMfI'
        b'JAu43ScVXhwd253qQC1cH0rIBZ5HxeyNjVOlqBhKCG+PAUeYBHhuEnHsgTrEF9alx6VlKlNBs8cLKaCGzhaAatCSCw71ck9oPL1WF1Bg0SNNMq+kVGc36Ql9hLjpYxnx'
        b'mzG8VSClKwd0R1Wf3G5ixMiPKAZLrS5KETxakDA8uZg8NLMUXcw+NLMl1JtmngRIz4Qz0U04bg0Sk4/Y4PeU5GN4eBrGY7B4yCdQbZfjYTwNz4BGnoCGw4NuGiL0A9rh'
        b'RjuWMKAJXoJXHk1CO8FpNxkRIoowkLhV4ATncOQS2NWfhKs+joZGwWOPjhxwSS1P5EAHbXg4bkA80aQtyddpJ6/HY4FLsc9Dl0FwGzxl9QDsy7PhpnRwJiUTtHgQFG71'
        b'mRdmcwaPDLaCzdnB8AyF2ljbC1RL4G3SceBCGGh1+dib0lG2RqVLqmSzI+LgeU9rBJRXhABhiLxqzuCR9TBElshsDo0oS0aUIyPKruIeFSXg3xNDxGpqtAo0p+MZvzh+'
        b'Mj8nJRY2wA3zECWrFLAlI3Weh/HBa8UCChzQS+AdsAneIPMf9+MEVF1VHxz2bto9rYwiHBRcBSfBRp9S+RBkpAjgeIyBA9RKzOZKVvuFgfWgic90hB6Qno4nHZHqEA3r'
        b'F2B2CPYnZmU854FgHg51PS+C54rhZuO6tXqBFdNTZf47p2xfI93gK80rhrhghRazRswOlZYHmtfzB5e9mv9Gfqp2k+5e/hn9V8m//3UCNW8CPW9UzVznqD8o2hO2tOut'
        b'fY4mjKyWz6k9WjNzDz2k3yutL4fQ7338ImKaLyN2+SFD/Xp+2L3zRxQiomb4g/MR7gkTsCvjoTkTB6whEyvT++DJEB+uCE6NdDHGeLiDJIoZBa/0zPmsslx4JpqoIwEz'
        b'wTbXdHOWq6IAeGE6rGPD+ieRFOakPumwxT0hHQePJSKNNHgVC5tWgmYypwEOjwNX3GnwFKL/WLgWnGYQyW2FawkjHwv3wMNeoR3loq7gjvnw2rOz4EActJFXZim1EeOc'
        b'8OAINw9eTQUzxE/D0TJkt0jJDEflmO4MUF+uL3Cxvy6N37dkntIFvCnRZXE9aY7SNZUp9WQgPLoUXTbQbnFRTf7+7M2l7Xm4P9fCmvj/mFfgcPJN4+F5wUx4Hc99JoPL'
        b'Q8EJBeJAW0OK4XbQaMKgnCwI5/43mEr+oXcFPavvlRG9xnxNkSntLfN20u0iSp4Qbh4/Pf9qpj//+sfsPwdtCaKjf6BWZ2waGtjvb5Rx38X9jBXP+r+ZUzO0aQKZc1xh'
        b'enn/umBFgOjTsI/WsOvy9UPe3bhlWe/ZP75TZoh87vWs0l8O7WydwxzW3FE2bH0rRdDvl2+8vy33N3/57MOyq5uvpcbPkt9pe68+NvmbqFzHhRLr6sxVEkfRvy3f37Md'
        b'P7l0wYnOog/O/67KPDdiZMSE05cGTWtatzb+Qq4633/cnvp/bLxgvhl8szjKHDLvuQOfj5i4OvZEzM+bOhUBBEmHBee7NfNW1Eneq0Tg8em8OtIM1psfnrkTCLgX4Jox'
        b'hKJgOzxY6aY7sMXiq5AMCLZh7Wsq2JWAa1qyIMszhEgN2YCHj2fMiTrh80pwmExKMqNhS2wc2Amref0FKy9TZpP4jsVacMs91jvhIS8S7jeGQzVsSbdNw0Ddje/rsQie'
        b'1hwYW+YxCMoC+cU2zX3gMRfn8eQUUX3gmqRQFl4qgZdt/UhtYM0wPqJFq8OgkU6cx0ZLVpLJywxQA7bzsfkIV+v8cMDyUab8heG8PrcOXlngMn4UYG+X/cMOROz5EOnk'
        b'0QvhObc4gzcjfcQZMgPrySxoIlwfBxszaIoeB3cMpRBrugMPPoIU/Z7VQhd4uIy/F4MgLCbazWJWedQ8BgeXcdhljO44JjhIiK4yRkZX9n8sw/FR/ISud11sRfQ0sDKW'
        b'ZZSP4YSGlVrpowQ6I72VwMeDhColrn5JnutFXl6HNC9vmV1r4id/iGFGNE1SU0cAXvektVoL9Ihluuy+/8gr0uHnKgmVQhpSiC562qV2iRmZKCzAjoO/BiI9qt3FG2E1'
        b'1w3fGSoJ3BZiegJNPq4F93SyNYbqcpfoWR2vAVEkLpPRsev8sHuEuEAEvKfZ4wKZo7WhfjOjPlMXcF6lenTlceji0pNdfleDyKVVcXUipFUJkFbFEa1KQLQqDnsAu+vJ'
        b'WKvqHq6EtCrCpNqihvmamVhFhseqZP2VJLIuB1yHjd4p4Dl/JJxhPUdFzOBS+i3n1e1z8ECcdypwfURsTIqQirBy82BtjIKx48kzpJlN8ElVD454FYaobi0xfuWrwFWf'
        b'OvcxntKSM403s1sEVuyaL3shGduZKdjCvBCj/VbzrcZseDX/geZrzXeapYazyP6MHvmNJlX7ikH0TvILodZRBQHTJ1oDrq6ZnjBdIrMeo6m+gqCTvzErOMKOpkqDfBj2'
        b'0CJiP4Jz4BBhr6XgmtRtGoIjOgZZhqfAJsKL4G14ZTqBOR3Ux5MlS8i0uBqsZ5GCfWY10X0QRzyPjI9GN25hXoae9pcjjWqLW2l5Gkr1Diw2IBzKw4Ye4SjBbo6ymlJK'
        b'pCE0x4oZZDb264Z0cZ58PJ0JO9gCk7VDbLCbCHV2cGUobYfQprUU6m1PVFA4Cw49s1TgSyW+rPQwkRXocuIhLeXDMG828jjoFIwau7AxI7FY8MVKOCmh7hK9rahURyqw'
        b'2Nzd0lMUid0DzHJ0Oe52kGLfsx3zYHAc1o52sYGpsAbhnNh3qdsEuRAcT80klsTzeczy51h8pzE1pc2nfGZLfKnXZ77EQ70UCTZ89OqtdQ9PX3S3iSLUxBRZSYOtVqRB'
        b'XPJfZodXkFpwFZ63LYeX/aeCu8tBc1CZFJ6nqEnwmAC2g43gph37L2MngWqUpz5DDZtj1fOI2ZuKfuqzVK7Vt/PBsRRwBtYp48D5bOIFvQRuSJCsPggPP3aVMEsCM/7D'
        b'YNruPEqgJusc42ejcQFtGS6G4AeP4cC73nNZZIJvgQdImqSC/piu+DbBrbHgRDRNpSVGgI2cZSo4boytP8la8bzGHr/XvtG8+uUDZIUVGb7SPdDEINvrfv595sKu8DUO'
        b'2e7rNYr1I9af2Bk+5Hcvzl7W+voLuvdfbH2JyX7x3lsvhtxvBTLik9p1pVfyr19RCIjLSAsOwfbYOAVZHCWEG+YgY2WUCdziHVYIRmsswqZLZqwBcmNpcDYcthENsd8C'
        b'cJZ4H8CNPNigSiE6YhBYwxbLB/OxlBvhDRlKgexceHQIXpLHjafBeQvYRj6DneBahc+SD3AWvYGX+j9xbY2/tqxMj0gME7mvx2k19RyehZGSqUQJXRmDyD/PZCzQm636'
        b'PIOltCTPYPS2b7wKctdKGMBjw7oqPQRZhS5vPsQdLvqEdj2HW7oGXga70rNUWN90DzNoziIuAPTLC20vyyUathPjxdU7iCXzvasD+2QlobCODxjbiYz667FYNRyVyFDg'
        b'FNwtgPtocGkFPErkkF07G1HK+RXLA+EueGmZVFy2TLqMo0InsIXweigfiXx0cI4VXoLn/QKWB0gCxfDCCkyQywTDwVpqSDBXBXeALWTR6gBwpSgdCRdkKVzEVbJoxNoZ'
        b'UJsMDhG6ROCfQ4buKbgZkXF9RkyaEpyEW1Yoo7F/IYOsSsEOCjFAzeRXSMfQFDgCLvpPr4Ktdjw9DS+AevZJ+eEBuLYr/zaTBK7Xwut2rMj0gkfgOtBYtgxsWIGlF+It'
        b'NqQ6X0WWylW7IBHupobkcGANOBrKL0DeU8YSeLdjIY5MocYMERUEN0pFbDa4tZqsroEnIo3dSlwBz0slQnoFNSSVAw1J4BRRkklQK6hlcJsYPSLWCdQERCA3SO+FJPvB'
        b'zVnw1lRVKtwGzqWkiijpJAbuy4AnCStEaLDe4a/CKwbTF/AtdrM3cCEET3dfJqzsebhGBG4lyuw4NAbBo8wRlmN2MoQaMktM+LtCJMZrVcrf0WgyTvcN5MNngVGEA3Fl'
        b'QQM10mtlBfzL7YNxTC1V9FWARilfNYUic0vpUrAeG3Wx2EVUT3xCvqzWBUgpqAZXksRVJlinYEhxgqmkuHJtoMZUp4nj62i1k4o1VUM1Gf+zaAZlzFhTzlqnIYrZODgz'
        b's/W2GiaErH/T/vOuRNXdmPxC3af0yPlNdfsHKk0LVJajKZnbpYHTm9t23hucMOLPculE6s1s7XDjr18Zk/TlT47JN94fdQuuC960Y/S8OdFnz/R9J6fsztt33n3tvZ9G'
        b'ag4mXGlp/VuAri3idujS0/DEy1H/OHe7IWPI4MAvDi1UPOiYntny0d/b/lLxdvuk11aN2dk6qeWq8m/9vjD8rbj9/d/fO/KXP87cHlRxZH3T35Pf5bLqP3Z2+PVdvfOb'
        b'CbbK2rQtpcJt5R/+rn3W+fMT/vr3opuH/T7618ttP24ZLorYun/NMufKiYcytsb3/i737MlkgaXIunJYm3H8+VW/fPnK5oYvd4X2HvptnuDsu9elV9vOf6BL2Be86ydd'
        b'nPLvJ7j9+6b/KkJ99N67cVN2OxP/rYpfces7xaolsYeX/uuN1uG15R+p7w4aGiXL+jdtt9qOXv9KEcQ7nGrABnA2PQTuwztDNCoxT2Epf3iBRag4mxiI8CbYC3Yj/kOD'
        b'LcEUs5yeOgist2F8TY0YF8uzFm7sPBox91ljCW8eDU+CQ+ng9AsZMXH8d38TnnbdWclz9r1SvLZXqYaNUiRqm8jyyUamah6/eAnsSQe7Y0eAm1kYGqyFiBBAdxhEitvh'
        b'PiJYBJbnMHNLg80e7l9RBa4Qs3llXkgsrANX56YqU5F4gQ0CKmgia0gMIXXTYF9gOp78RMUqVGqk3kxK6ZvBJVeyRJyBM8mhfGSzkqaKwS0S2VwEGsjHleC2hcADG0UU'
        b'pxo7iUbQnwTnbJh9q+FuSWxaJrKjuYFgrZkGe4UcMcKnLVW4SsT8GeXGOsWZlX3BFaT0H4a7SB8njQKn3VI0e4QQC1FVFVHLJ6iwq9DbkTIPtmDFvML8JB/f0xm+3kZ6'
        b'nx7lHZGR2V0ycjaWkByJaJYxEkYmQf+ZYBpfJawMvYvAKxKQQS8hUV8SEpIjJvFdSK4ygST+QUYHM1LGssotmpEB/mwWu1fgIS7kpYfk6G1vLZtwyQFwb2yPUtSY2yVH'
        b'BdQLNixlGsAa1y4YcHdCGrICYwa75t3wrNs2uJOsX5ymQyJjC6yFjWpwJsPlsQWXGXgUHFCT3Op0sD8W4dkgeCdGiAynA8wo0A4uFbAuxQ/3fahb+cPhB932U6A8OyrQ'
        b'PnsqMM4+hlDPTIPgkTMNLNE3uc+GoGGUyL3+ZesLjVab3mKV24r0D2/XEyfxSZtqkxutcot+md1o0evktlI5du2ijOgt3r8Fry2Vl+J4zny9odSil2vNFXKrPZ/3ffgU'
        b'VaA143hNY0lZqcWm18XJFxiRJWO3yUmgqFEnd+EfgcpdNvpgq0Ag+JRk0VttFiP2LD8EbRIJipFjUy5Jjrckwnc4bhQX6SoetbCHLEv1FTiKk8/lengoo06+HPUZgqnH'
        b'AuxW9JHP7kk/c1rq9BzyRW7UWeXRc/VGk1lfVKK3qFJnWBW+5bh62x3WqpXjNpoLcUyrVo6jfTE47rLi5OpS1HFlZaguHAzarSSjgeTiOxSNVb4WA4TGCo2NtcBiLLN1'
        b'a4iP78SzWsBjl/ir7di8A1ei4NEciJT/ePe0X/aCFKR85qSkCbLHjwcnFBJ4vWI82Jo8aHwfCrbCNml4Jtjhg/ieVbFpvohPuVCf9qA+4wwyyJ5yWs3HAYQ5hbxbI5Tq'
        b'nk05T2yDy/Xkmcp75gXG3Q06Tk0YrfGD28mMFbv8MuHqbzSqL1IKxIavNF9rSgzfalILqI1fJ49sVuw+k3KqpteQT17Z9fJvXtwVeCTWlLQjKSw5//WmOOn5pMuavWOk'
        b'mzRViuS39543vXEour1e87ay1pDwWu3Bt+Ii772abzJodF9phDt5i+27V6MW7f6rgiF+HCk4OiNWFZ2iqgTXsCtnF6OCzSLySYKUc2QStGDlOBRZj3Ya1g9UPPuMkiBv'
        b'hUVbRsRGVJfYWE0N5UiImwTxZD7cNwQvJVZYXIzIK7TNhbJeb3CJbhuLhI92SYsniUGaz0BERTW6DEKQWUO7REU19anPxBE2SMBRcMkY60ZtFbjew/LiLjkyM1gRn4ZE'
        b'9yzQFmQEx+Y+JrCLJY6Rp19K7oNZAqqnaX+R2o7DGMGJ6c+PShg9MnHEmFHgKmi3wWPTbJbly+xWYsRcgheQEXIeXoYXg8RSSaBfgD9S/epAEzL+jsCrfvCMSki0bltW'
        b'GrUlYSdNyTRpzgA1r4rXD0ihWkO+EFAaTUzC8hh+uZyx/0eUwIrn2co/mdzn5YPByckhgrdW/u7Ood0vnktZe8BfcmpSiXPn1hSw0vjaqsR3dvb+etynjmPBDSGG8PN/'
        b'OXWtPDqhftMfR/0zsWxM82fvrfxpy1+n9JYe6z+y/tQLsjFv7xh/uCMvvDXkg4+qXKgbvbKct2kZsM6j9g0nGmHuap3LV8A7CpaCPeD83OmPC/t4ctSWpdSWl4+tY9Tb'
        b'Yd6IPIojyBtCIlOC6UrlU6Gwqzj3bIUnCPrx8VwkRRcCr0GXhG4I/I7PWk08l4WUbbMHfx+PvHD98mAFnveuzxqZyFLLQaMsbhw4TMb9eDhv5mWzGumvInq57NSDSPFt'
        b'gJsFRfEUFUfFJcHtJHG/EcReE98arpGeS+vLY05nlQAHWJZ3pmmkz0/R8JhDvuyKIsZm2KxCTca+AQr+5Q06Da93H/fzAE3xkhkz+ZeyXr0wF9eElGtMG1KlFLGKQ6Py'
        b'cpABsGXemATYAHbBzRwlzKbBaRF0kkyjpkZQo1GmkgGaJWcWDORL+l/5eTqyhBVR1KcrPmCrFpCS4Gm4SZeDHdHzYDPYBPcKKFZDTwZbwBWy24ABXJrr8bClg1vImkUm'
        b'BKxTpmGvITYnSPQDUtSxfg7qYyUKcC2HTPauGyGU6elxeJ9G6YcLHWWVFFkpHZs8XCxeRCUcG3p92bZ+46KrlryZuG/OJ5QdR2tXwOYkeJHWzEEygsoE7ZEEcsPwJMqG'
        b'+vGmTJM9L38h3xzlgsnU/QJ/mppTbdkhG1BFXn5hnUI5ELVox2osh8a7tqarWK6kuTjIUfJq6wf+cDjf2QN/Q2+JQOa9bE3pB+GHVpGXe8fMou/3j0XDtGZp2LC01eTl'
        b'3Iw+dMiAfIQK1VVhsU4JednfYKOWjPoMybvq5WELe+WTl8f6zaXbGCr6+77a9PRlSr721JhWekv/54SUprowbNaiF8jLqsyFVFmClUYgVe6YOsq1r17+YHpi4V6OKquu'
        b'+qAiSURefiYeQE1MR307p9rxwZDr0eRlR3QmvTA+WYCyL10YaYrj14sbQ2klQyXkDtRUvT9Jxtf+zbS36AMsJW7L18bfnefiaHuFv6TqEJP731SNYkfJVBd6jHZQPyF8'
        b'e36JJvTj1cP4lytkH1PXaCpZkaMZLysP4F9e7hVAIZ4QHfqcxjTHkca/nLFkGXVgLId0ik/z38t+abbxiyFVtLUNddAUefa87MzS9xJk/Td8N+7Dj4/9Mfa3yremHRT8'
        b'TDuj/k6nTAoZcu3A8chgo+Cm+O1Xx1+P/tPRVzf2vtuwH675H/P6dYNWGl544ZNb9f0b39xcpN/6jeS9VmXVLDbgw09rv07ot3yXVOLY+je/MdB8+KD2yPzDN376WhE6'
        b'9fm+56vPfH2j9caWG1uKhnYU9f4k+ELJr2OuHahULzrwQvofkhtudYzUvzn25imjek3vyrTo3KpThbd+9NtbvapMJc1gG18A62s+XH3trxHmqcZzdUfzSg/9kDTq5F/u'
        b'/DBvtqJRcuXzksTeOjv122/+KPr23vY/rm2fkBWhn3nvy/fKhqa9MHr+9o2Le7dd/mDzidPvrzp8sTPkz4lw7wHdyJW//f63X5Rk3814sCy4+ac+2681rpz6t0XvXdsg'
        b'akt4eXKx8gfZhh/CRON+2XviSxvv//X+qH2v3Z0cOnb4J5/OzHn5x76/m/P9pv1/Ka27aM3dF9b54Eb9/3Yejp50aFJvp/r36fUfrsz9cULnnTuv1eXckjwIqFL+Y2Lx'
        b'/jd+1fzPoVOG7694/+uN758bG/6v1+7fO5Xz1ofbXsy+vbW34rZ67PDPXvp13oH6lpp9ToWY9y6fQ1aa02W3g22BrjXO4XArkTYsbAGXY2EdYn8MOEjDo7B+TiSSuFhI'
        b'rIJ3cmLTVOmqGDW4BC8KKKmQgbdH8+4HGdjnwHIKHIU7PbIKnKdAK+8w371iOOIhWangNAebObwH2yDQZCIOc7AH7p0fGxeco0iLdW2WGASr2VJkgR7jZ9g2zFwW6/GZ'
        b'gNNwv9tvAprKiSvieegE162Id18N6L4xDGjXP+v8vuzZ56efWocUuwUokb5LvKXvQCleIxYok3C097ZY+DcK/Yahv2B6GBKGkbSQfJFgZZMNpkOJzBaSvRLExDcRiHJg'
        b'P0VlxKMluDtsCS8K6RC5jMIOAbH0vET3f2EtHWupwfdk9ck6j8RfizltN4n/xxhviY9NsmhwN8kl8QPA+ScIfQGO5ERK3620GXyg8ylYJyGTTB7XLXFpnA3nvRrx4JIA'
        b'ntYhgUhQ7fC0SjKNBnY+zztScJyoDK5no5ZLCSf8Vs0iK4nshCoVZaXw7DFdLKD+UCojcYjVs1X8yzEpQur06kiyPervskdQxl/F6TjrQfRFf2hjfxwMlSyd8Z1p8u5M'
        b'MFa8LFydPLtxi2Frytzog5wk9JWL73+2bkdI1oWX32TH/mbFj5E/vb4wddCs7FeOtmbHnNAPTP/w3vwv1MurPu9dOjnxh81vfdTSnjZhb6vgxo4PZvT7rfMFzdvC3h83'
        b'fnos6g/vXr9+58Kb7bV//vsa5vs+81f+E8RYJX8K/teXbxSJVihiXm+8e2bxsYt793707s5XPxP98k7cl9rzrkBDsHbIVM/OusZxD+2tC3fH8OE+W0ELv6Why38IL6Zj'
        b'B+IBcJ3sXZdG4R1cu0aIBa042DCDpiLAPq4U1IL1xD0aDbbk8+nMS/iUiBMEx7CgDdyETj426CBShy7hRF1uqUBwFjgHszOSwXECDjjTB1wHjfEqtQo2ZCiEVFAkvGVn'
        b'8ybBo3y4dzWyGQ6AxiyXpqNcAfe6GUY/ZBuCw7lat2UY+l/nA0/NJdxk6xtShP8icUBR9Gwp8VMyeG0pE8rwuzFgrmBZj9KqvWmbJz5Cd11U3fv/clseQfMYOFE3mv9H'
        b'4sM7skTq4AkXzcMbajxbH5TIGqYm+UwuC1y/VindFa+jo3NZHZPL6dhcgY7DW4TnitB/cSGV64d+JVvYLZxO0MzvtIZn8DmyeThe1uSvl+rEOr91lE6i829mcgPQs5Q8'
        b'B5DnQPQcSJ6DyHMQepaR517kWYZKJN5NVGawrvc6cW4vT220p7YQXR9SWzD6JsZ/utBmvAsb3mqwry6MfOvdw7dwXQT5FuJ67qeLRDX0cT3110Whp1AdRxxFAzoCM3gm'
        b'n6k1awv1ls9ED3tJsSfPN42cxF/4JHpSDqMVu+yI31RXYdaWGLH3tEKu1emwX8+iLyldrvdyE/oWjjKhRNgb73JD8j5Aj3uR5IiTzzHptVa93Fxqw65TrY0ktlvx1us+'
        b'HkErTiLXm7G/UCfPr5C71uzGuZy82gKbcbnWhgsuKzUTn68e12g2Vfg6CudZed8xqkpr8XJ3EqfwCm0FebtcbzEajOgtbqRNjxqNytRrC4oe4cl19YKr1jjSmTaL1mw1'
        b'6LHjWae1aTGQJmOJ0cZ3KGqmbwPNhlJLCdntUL6iyFhQ9LDn2m42osIRJEad3mwzGipcPYVkv09Bnf2LbLYya1J8vLbMGFdcWmo2WuN0+njXJuedw9yfDWgw87UFS7un'
        b'iSsoNKrxlg9lCGNWlFp0PTuG8G4DZMUfWVJlEDzFmj+XV79zfXfnsdloM2pNxko9GstuiGi22rTmgofd+/ify4HthpT3YaMHY6EZ9dvUOameT90d1k+IZRGqyfIrcPIF'
        b'fvkVXjcSD7Y/ZunI4nAygT4GNIZ7KyXR8CY4m6KMi4Mb8Ba/iWC7cOXwaAVNZuRfADcnYQGbjlJmqfCahuYsmgoGe1i4xgh3Gqfk5HJWNUr4+dkQHDl378sH6KoM/VqT'
        b'oq04wS9GiJsfrU3TMhfDL+6YsGN3+MWFu8KTdk7YcWHhhB1r8k2K+7cz+iv/51uF9EXpHiNlGij74RaHLAasBBhTgrHAlSCB75lc6pLeNLxKdHTNsL5usQx29fNIZnYG'
        b'PAEOEvGeAffl+6PmKjxqRB/g5EA7bBGXwVPEDYY0/AOzYmFLymgOrolCxshN2ryqjDcSUJ3gAO4BZLkcRr2AvWStDFiTjowEnDcKtsDTqI9UClgvQsZLC52eDav51V/b'
        b'luF9BFNmwQ2jR45hKVElDXeFgZM21/5Ca5cRtaMuM0NIIV0QGT01NLwOri9wC9GnmKnDQa9EVId6i+rVVIiULDHASnllX1+c9SxHVHuH+VoafOV0z5F5DJ/M6FN/A+N2'
        b'51V7/n4K8Y7JexQEPa9mwlDhnSJcu7GSCFz3JBPSkIyeHujqBjO67GRci5q6Vede9tQZ/si5K1QJqysteFqAxHkus+Ux8Oxxw9MZ4jV75Z4Ei3tiVUXuqjAnNeqsj6lq'
        b'v6cqJa7KrcP1MFVWYDIiHq2yIlateGoQ/PP05WVGCxEBj4HikAeKwRiKrjxYyjzc5V2Vuzl3Xw/ndu0O6xR4ce5n2GDbvXlQN56JXwykZuSos7AvgAKXKbBhOrxOfISg'
        b'Zel8cIrGb5dUUVV+ZXxE87Yp4A5sTCXxTsgcaBrFIfpvZNLAySjjxt/cYawLUKqA9xtVB9Jeey2gOkFa89k41Ya4X+SfnkP/KP1asb0ps23c3zcfnZIW/dKygjq/XkbH'
        b'Oy1tyriXHTcu5BanfJr3R/Br/S9+oWq83ffl0y8m/vu9o8cvfSlo+jRUV+FQSIgdg4yG5slehgxcM9uHFcLjWcQAiYSt8Db2nabCZsTRrmCHPrzJgPo+/Ugcx3KwW8t7'
        b'++FRjdvbD8+DFuIpAXslplgbvODyhHBqGrQnwVbCyEz2ObBRlu41GwDOw+vwBm+GXR3ssrPcjIyuHILYWCM4QBhk+HRJ+lB4G7bE44M1uEQa3ILOkaTcBaPBcbKaPBSs'
        b'82z5DWpNxLMzHx7RunZ+hGvhPvwdb/0ItpYQ8YAaewwcInvBp/Dyiabg2VHB4BQLa8FpuMtn37mn4aWI0vTmAktFmY0w1EhfhqqQkrgLCYljJDv2dmNqrtw+XPWpNo10'
        b'7dfbxVW3osvRHrjqx4/nqi4A/qs6kaFHnWh6kdZcqOcDHdxajJvAH9KQkKLztMqRWb/iaXQi90YyD08Hu850mQ7rQRNoATU96S1ISTpiLP3i1zSJDXnL1jfg1djg6gQZ'
        b'9/bOIf+MXMBy4zIk5wtT3ts1lVow7ELe5aI5tk+ee6Wt6MXPTstyx/77i1enpQvi6/qH+8+PnNN+9uPb0y8N/LNf2vdFX+44r72xKlfQO3POEIUfv4P6NNDsUioODOGV'
        b'CrgOHOH3k94BziBdLAuvFQUnldE0vAtrqEDYzOpBfRbRbMLghnngcpwvhvPonWonMU7zphuxvwE20Pl+FBdPg4sDgZP4GiZOEfJ72aZngeb4FHAObPHoeAnwgHD8NLCH'
        b'13zal4dj5QUcBhdc2ss0uJWwi1mwdjHRew4M9VJ7wsEZ8hWeBhs43Lp00NSl3CwGu/iAtBuxsNrDE0aOJVwBcQxnxrNTZVABwbU8N2I8HGCM/5IkZAOYELoy6iGaeCjz'
        b'f0Pl2Y4u7T0Q5zs+xPkEQBRsh7Co1Goz6jr8ECnYzFjEdwh5Ud/zEh5CwJxn+Y7As3xH8MjlO+5QJRzh2Y2epup02KDBROelJfAGoEdKP5JyeeB5uk1B96kz3PSfrzUv'
        b'7U69HoJ3tZXPOYd/RJmj0+1mZD6qUmf0EL/jFQvkzomNZZzNJ/ZH0RO8Fr3NbjFbk+SauRa7XoNDePjNBXRKuWaW1mTl32lN6KWuAqktWHcy257AgPy6MSBWbfzDq70Z'
        b'K46drtQmf6N5I/8rsrWL0cB+c1b/leYr9MZk+PbLE/rT2vv5J7VfFYgNYp04v06TQl8Yt5iKZv3H/faEgiX2QVhxX2/+gHkDvAa2sfrpYA2hQLAJboXtLgZAwZpywgHg'
        b'7Xiba0/rXWBtekYqYieZsCEjDrTEk+jMcnhOAZoE4MxicPjZiTFQq9Pl6fONBVailRJalPnSYjqmxMr+D6G/bz4XGQp5qsJnH1l24ssuX4L0Bo/zSmb0pCUEuQddbvdA'
        b'kC/5EOTjIfqvkhySmZ/N7onksoljClGdmUczHIfmRXteLqn//1EfzpaakyXnnUk23vdErAKD0aw1yXV6k7578NzT0Z2W/oWA0N1b4497090jqe7YLQ/djaKGf+kf2Zzo'
        b'ojuwEazP7aI8sHUgT3ysPljNW/UHdMtdVJcOjvNyF24Ge23RFL8KG9yKJXHU8emgOWsW3gbJi/ymgBZRcGz0s1NeL96p+QTiyyXE95AKFtct63+X/vA6+/s90N8VH/p7'
        b'IlCPOQ+HdlJe5+E8estzltisXGd+D5RH0JCQiNleko+oDWGel4e4y+9aYLdYEP83VXjZ0f8JUk5h6mgr3vJ0jDL7G839/CJDm/6r7f9CCHn/MWLgXepjiZ/tXiBCRxK7'
        b'3wz34AX162GDrzBg9WORgUUEwSl4GV53CwLODK9hlKyCtwhGFiM5sQ4pg/HIcuRlQRi85cbHGCFCyOsi+VB45KEzjnpEwYJSu9nmNWLWnlAwX9wTCnbLqnbHHhofjXO0'
        b'l9Z1AF1+2wOSHQ98HJJ1q/a/hGSFCMnMj0Syrrjip0YweXQMVsSMZvnyxLjRMT1w4Scj3NEzrTzCDZ8a7EG4ntDtY503wtEf+/vZP12GEA6bHcHwwEwX+yuEbV7ohs9V'
        b'JHaNCNZLMLZZwWaCcIQBtg6yYf+yuT8kpx8q40C9cZa35oFQbRxwClHSW2FPgWsy3INPQrVifherh8b84ZzPimmH0OXzHjBtvw+mPalWRd+HlxmL8vJ0pQV5eR1cnt1i'
        b'6gjA1zz3VEeHv2eZiFFnwadKWTbgy0Z82Uy5PK0d4jJLaZneYqvoELtdl2S6s0PkchJ2SLrcbsSNQMwVoiIRPk3oiDTxP94Rwcvrh091sDOuOG+xP8fgME7PHxMZyJDg'
        b'kG5XJtg/MiAyKDIoUMyve9wLj4KDXeuI8YGcTekZ8HhaFpKZ0WCNYHXMIp85EUzGyZRrjbrvFCx/aHBHb9cCDNc4kd2hO+Uzy/G2ltgnWYBXV1jMWAXzUrnUSND5jpvl'
        b'sKfND/k8T6HLN4xn+TdHk10gwC3QvtoKG0ENPO7ec6Dd3TD3FESaRAQ2+M20420TYfXzC/gw43BwxxVp/ExhxvDmGB+25vGN4A5yRd9TvkeKdm2y+4Q4fB/HKi68e7R0'
        b'kJqEnZzLliQuouagO7lp4SLFXBKtOW6RKHkN5YrWDGuKuEGZMvGArZoo+DrseuG/Z/ZTXF86J+/kgLalNxaujd6l/tW40YualXuzzkw4mvR8/3djDuX/S9mZuTrgi34B'
        b'VbfmtUevmz4m7Ut1xdTPooQRksiPFk7L/XzyzWF7sqfMre+/JebWgMXT4lOzy98POl/63egOdmNMdtnIyKNjjgTc9/sudVJsQN+ihRZB9aAvZiyXPLAuL4vu++HMk/7h'
        b'ATdW/xtp/u1VxYHkZJ2gYeCA2+nrcvgGgY1pFXAbaalqJg7hFWcylEb6/Eo9H3VzMA4fobPDX0hpHNOLiviXn4wJpZTUW3mMXOMY5h9KkY3i4E31XNiYqYrDR8O6t/yC'
        b'G9JFcCM4UQHrZ4KtgqFUIDgM1g3zgwcTQD0pK7kvDvt9K9I/WaM0zwrlK3jPJKSkVOsioVxjWjgrm983tvLEejRkfRh8usTlBwqWX/pp8RcuYvjh+WD0+KFkeA6YRPOL'
        b'3cOz8EHsB/zw/HrSpP+nw0NnPM3wzBl3iTV+mf2GwIqDOQbOCxzaPCEQJkinK177+7jvovrdzpCs+v6t2CLL1QOHb8/t/97i2bNCe20ISbm+4gOdaXft4H4LUuZ2XnxJ'
        b'uFOiW5V8YvPrv0pr1r1S/vLnfx+4aOudPy1JrT3SFKW8dMB2+YPcvbXnLsFy59/e+Wl55q/utEr+aRa8+ifV4FPfxo4NeCPsn9M69+aMGbpGe03B8TbDKXAHXOs6poi4'
        b'yk71KgV74Ql+A6P14M7IR5wVflMGz80ewrvS98wXx6rw+a0oWUMk3CCg/OENBl5VBrjWS56WxsIGDbgTgz1yePHbeHgHnu4e5f6fblDsvajfYtX6OMRxQ7yEr4MjgYAy'
        b'sgRRRssZvCBRRlvOeGQL28Hh8AIvkfsf75tMW8562C6u4K89yOcmuXcwD57ADkheERujBk285uyE7bw60w/s5cCpibk964Jeu0p6MU3PrpLPdLiXzwkRHoYZwDNMyzJ/'
        b'KpoSSxhEkTsEe/sRiqRUIorSTHQxzON9l/EUKfX7v02RTkVB3m+Nl0SD5h3R6MelLX0aijywPJwjTZkWzFA/xOFx1kh/pXDFbv+2oDc1JzMFv1yiGB9HWbBrhXw5HcFR'
        b'c8JDcdhiRtnQZfzLu4NFVFFFfxy2aPoqy8ifcQbOgSManhVPSOqafYOnZ7jY2p0xEtSJcm0Qljq9qrWkE8sCRNRb3CRXJ/7T7y98J95J/L/dif8ao33mTvx05D1/4+nP'
        b'36LIro6/PDha9Spha+ycV++/eX3N25fHvtpnnfTrL05MHxku+GDxAsWtOtmAqtvyutfvvFf+pd8AicPx6Uud/2usyf7bTOle/9/HCZrfzvzY8Db819rJisqbym1fXLvb'
        b'PnXL5bm/+z395r8njf3Dv0TjHf1zfxOuoPkQ6dbV1nSspVCgjjCv5xk9qF3uox4/Wxjzw0xEp+9iIkN8mchqKojjVzIT9oEZiZSwFcu5LjbC034XF3nmTdO6eAcuVcy6'
        b'92Os9vrrjHyYeyAe3Poczz9SM+PAdsrFPTQcOFgI2n1WROIlKGTv0iLEU+oE/JkA+KwazDVqmCqG3LM6Dt2zrXR5tI3GaWZQrfTzEUuYKq4Knx0gqKNsDD7PAin4gQ5B'
        b'MasToHIECyhzFN61f6nEUsYfGUW+4cN8BIvILv3m+w58VFEyKQPnv+FgLa0oFfFTlp9Fd0Jy7gauS1glqqMdInzGgE7UjHI4hBOpZbtQLbUkv6AGHwvEWt7CZ1zgOsrN'
        b'CFoBOdUA5xd3yy9G+TtQ/lkkP39QU7Ind7Qnd+SjcrfS+ISDOiGfA71D0gWVqVzgOl/BdRRTvoPS+YVjrssfHyRRIwmj15fNsmCmPbdTYLcZVOM8JwohFG7Hg44/WrAv'
        b'xBJLkbXwGoyafnqzvURvwaduTMHPQrybvk7fIZ1nNuIbYjDweSfwWNe1w2ZXseR0A7KYLAtf8L4nHXTxs+67JcVn3FhH8iuTIzB+JhG5JCaxtvikFv68l2ByEAdH1siF'
        b'ed1JXb9isp+omLZjWT0UbAdXyQH0qkS4OT4G74ZA9n6QR3HwPKiFtT7xH56ICdxMB2UV6+gcCp/fRQaAqXHZVWrSiZZRHvKkO2jrI4z4ANKsPFtpnqnUXDiBdW2ZR7HY'
        b'PCTxaODkELCVhxG0xMN6ZNlsAztwqANWiKlhYL2gQj2327FQHuc8Qgh6KW2RYqtPxzrwKVm0jium8AlMCGpBKD6ghe5LYbGN3xABLXS1AcPSyQwtJwvovmb4xggqDUaT'
        b'ScF00OYOuuhRDcPtwe0iDZyGGyZxDRhHjtYhVu1iTSX2haCW4JPLUduywHG4hTRWSA2LEiBdHxx4zLppusd1048/8LHbumkh1X11a9eKwYbeZdSnyExLMJtnFfWbyL/8'
        b'OYAs5JL/YmRx6rAKLf8yo5jfs6a1coXpQvQUyvi7ue2U1YC+fNwp/kbzOtkA60zZN5oHmhKDTVt3+aS+TfuV5p4h/p2v0dfTWryv3gOdKuSk9l5+sSE6dG3d8nZbwvsJ'
        b'o0cdS0ilUusaylqjB78+/96eEMOIA0WhVkn6qIIEtlBILVkf9s3wRqRqkz1J+4DDsSrohEei+Y3zdjGqGfzGHnA3uAUbfI8/zBwH9wJnKvFsFc4Wkz1S6jPgBiWNPp9i'
        b'4C54G54F10Az0a8XDowEp9IGIPRrxOGRSMNexQyi4fpnX7Ddq6RUN34sf6BIns5YaLQ9vAuwa3csMc2fsSSmI2nLLzxE9f9pSTYuJr1HIXfVZ1m2An2tnB2JGtucBc6P'
        b'Hi0lmyTjU53wMcCubhoHjgtXgVNCH17hOaoYO+R4DoFFHaGvdQpG3SHQWguMRgTVJcojgbsf9isq0pebjIaKeazrjDOKJREcOrgJbAan4SYS/ED2PAKnOGQLrWfgDbAL'
        b'HuqZcWF/OT49h0jAEBzChkGqcgHoAs3yIg/KZC/AHrO1mZ/d7AIyt4t9YQWFsFg93A+OxeLt273h7C2GO+eycC9cD+4+U7e5YXtsp/nlJ47mj0bTenUbJgCpMjB95KhU'
        b'jxkaBNeCqwPZCeBY+P/DDkPg8ZLU8FCHYWwcmgxbMYxY3yShuvD68/AsOyJV5RMO6Dn6D4tBHY14OlKhygc5kIC1YZ7P1jBIlaCqWP44MAeDODyzTIKP4CpLdND4YC7i'
        b'uxKoO4YkjBg5avSYxLHjxk+dNn3GzFmzU1LT0jMy1VlznsvOmTtv/oKFi3J5CYB1U15FoJE2YFyOaFjBdQj56aIOQUGR1mLtEOIdP0Yl8oJf/HDbRyXyQ1PCus8lIbJO'
        b'SPbnIYOUBbaI0kcmdjkLgsBGc182CdxZ1vMgSV24onMfR4WG5GUPo6AtrzwCS0Yl8sOwwgtLsPIiWwFuYQA8QyAohkfYBLWWBDzOgTcnJ8JTsepMsgkbPuAH3GBgO2zz'
        b'2q2/+9wJ4zN38gwuxZ6PLRHgWC7eI5Ku430mKrILajq4EbSAXQwOg538wvlTqWAdsggp0JZLLaYW54MrxkOfJNPW4ejj7YOSbzTLz90jEyH48JBvNRnab/UZ2uBCfGg6'
        b'S+XUCra+qFYwhPmPSYbbYlUTKlNRwxvjRZTfKAYcFIObxMMzU1OC9/JCbBFvgJWJ+GLveHZqKdyaDw67pcMjVAWjtTTPZizRW23akrKHt1V1/7FioeUNz6CyHWKSw/fA'
        b'Dd/5ijfdNZB8jh7Zfa33jAVRScCliS+QhhCNBHcrOATOxKXCJhVFDbMIVsN98O4snwBCX28y6wog9PIlO2mPN/mZ9t7ATQ3uNvS91PzJ2NfgbVM6ktYtsImjhBHMONgk'
        b'gRtDiC6SH9GXUpb3RSqKxmEY1I8ieL0KrIXXR40E50cmUIMokZoGl+aB3fCQlXckbO4Pb6GvV0aCyxz6DLbTdtgMriRV2jEMcNuoiXAz4gKmyjgqDm4Gu0lFs0aGUwmR'
        b'/yOiNBqHKVvMa0LDUqOpORN/xi8ZNl/DbzEA2wWjwEXUbxlLJlAT4CZ+d9e4SX6UTLqVRUmVa4v78PnvpXKUOKVVSCVrpFtS56HBJC3GC4yPpqeC00ohxUXSoKkCXABI'
        b'pPDL6MOSqeqQD0VUmcbypcyfL2jpyimUo+h1hkrQBK/VuLZ72LVQSEnFpQLUNxkfjYiljP/4oZixfoC+bHpj4szW82ncVGntv3V/e92wYvnnxfplwxcs7uTurG9eq5/z'
        b'4XrV/H4D3x0X+QfJS7OXh765uVX205//GLSs4ruQFT/86qXnyj+83jQnxiYLeq25cVrFm4sjdVEnZ0WMDj1b/OMbn9+dfCFxvaTvqz/85mjrj798rTHn2N87xm/WSoef'
        b'/LXtyI28k7LPbl9M+su87+vLGzc73rXMXAjnVHVuLZfutN57+5WFK7cG35o/6R9HAn41bGzSwsxJU744sTLCsvSMYGvAlXuvHDqqmO9MT7f/4yXVz7em/FC98/vzPx9d'
        b'/TOdHpT8D9luxf9p70vApKiuRmvr6nV6VmaFYVgGmRVwY3HYZR0YlGET1HZmqgdm6x6qe2AYe1wA6W72qCigokhYFEE2jQtKUpVEYzaNSUw6MUZ//Q0mcYmJC27vnHOr'
        b'erphUJL/f//Le99jPrrqVt26+zn3nHPPIpMco0pbnxVHarbrBH2Dts3bkkVH5BO1k9eVad/OOys09iQr0+g4MFmLxp3UoV26ttNaMbyKaWpu1u/XDxtq1aZK9W79ES2q'
        b'36t9iwjLaVb9aJKFST99LxmZ2PRDNzGPf7fpu6TqGW59v/aIxAnN/Hj9idkXHgXvv0Ocm9IOu5fXA9ho1OXDRxAeqjoXD6VIPBPrSrxbdAFN6gLsIfEDeYFsvDMoFqjL'
        b'sA1XX4xjLOZ8JeZo9KsNXg+FsuxBXP+K13VBfYnjEt20YF3rRFMv+5akv8+TJL8kcD+sn7q2bHp5KWnKA75bOUL7zvBLhkvcYF5Cn6fjyWXnJUXat5HOGMBd4wPa/1sN'
        b'pmWnzCVwTnjyGuExcmkU2C8MOBlBRtMSktTykAX+S7A/W3K5LMiVA3lCMMGkY23siBFREc3v1ogsNDXkEtX6iNQMzwFNClAyY06lmiRuN94IXIsUXziL8bIhKCyH4lqe'
        b'N7ow0Si9b0sUWvigSRnIXFdRfasfWBWmnNVbOGRGGIkxS0d7u1dVcTOIScQqyzEp6O0MAsmBRQSaurwxe8CLOmNBjOy7skkJLlNfxvyi4j033jE08Fd4/8v4UnUltmWP'
        b'aO6YJA3BVQjrUUBvieQF/rJZVjRMiM5BrkV7XD/Ys0X3B6DTT1TKSaRlXByPs4qkJRHAHBDAuSSjYyFCYQZhiDEWpohDTBI8Qa2HmRUUCXKIIRHDrDdThCmcQSphMTyl'
        b'IOf4HnKLtZxiMUQOZ4ZWXTu+s621smw8kYhNvqVjlwy86LqhS66H37ISvK8sHX/t+HFEcJ/GxpLQypBqAQeIFHhMDnjr1IZlMctS1d/RHrOgzAgurf6VMCvEOEgxEeqJ'
        b'WdtRy071xSwwivCBzaz266j3NPRXCV97zMxHRfOgRZRMxw8UCZYhCYknV7/6LqGRPEGmtmmPouceLTrHMN2IksgJmq/drT+qPxUnLZLOkg/QXADhLmRxSMozBkRdiyyJ'
        b'iwsMxWszUJMuTr04JChA7oc4DxopCfB2Kl6Nt7NCArwROvNDKO3M6Cb2BsoVc2B+eG753IXmV6GErx5kX/kKQzzcs/f3nvveoF6lmhjvOCMUFdH0wGjSyn2NACJY19SK'
        b'517eVm8bTIp3hbf1a6Aw5mpXvUG0mMUx/17PULtIJu4g3xoOcu1mE3JZyF3tGe0p/VDZ0JlocAjsE3Cc2kY26Dw3QHvQMnR2Tu/G6hj5vEdTAhATt1j0ShR3k8PYmneK'
        b'zXKzdbENnmG8TXxm9Vqb7YrVTGE8TkBqaKpuW+xQBhpkv1NxrbUvdiqDjHSK4oa0ywheIYVtjRYlVUmDb1KSnqUrGfDMHX8iKZlKFjxJTcrVR8mGZ2lkos4tTlcGh8VG'
        b'nozQ7YszlGJKFSr9IZWpDIFvZGhBkTIA0lkUKqMPAeBFMecUmBOvLzgJ+Lf4KkyKM48otkdmT5GiUWaP9xaDoZRh7rsZWPJjTn8F/9T3OKLHJ3I9ge9mxmc5AbI8BKkU'
        b'qT7QXtfg/XWcLxO6+ia0rfLsjOeIEKixuLMiWIQQMHjTVk9Q3ydEG6xb2ruhXsze3lrX5PNAhlhCA/okNiCeo3f7wAyjZr/bBEui7LH2mMWDWwEBw3kMBRFYXu9hSbvS'
        b'EmvGj5PmJt5dF80NQr0Sr45XP/z6QafK/rOnm0l8Tdyquj0+7Yj6OxeRzJs3wjhPx6MbFrY5BEuhRVAvV1DqIFRxy3Phib1Fbq9R5JCIV0D/vGJdwwdyFRv7Kpsz8y6E'
        b'8jF8uTFXjpoz/LAYX3pGqBzG/AVje9R3cYr4G89YbiztLkaxevwVbr0s7r0DOEk1GFjZBNvqBK7HmoXc4M+iAtrPx4x6AOHAzuwlD/vviKZKHSEZG8ULyhey+K68pPWY'
        b'+E1N3N+oyJ0lSaLVSGMYZKcGAoVrZycHtDpF9XNshSXQASQEUg8+xVTLw8bHHPE1f54TBfVL+PlINPhFbHby+sES/8UGru1poPoFNsaKhdUBfZPQQvUr7rwUFQLImaSm'
        b'ZZ7dNCgtaXXHlyDKUCKwrCIS0iERWum4IDcJ1FbebCtGow+Zgjk8rPAF2uraoYXw3Gi2zEIoGFARs3pZGy7Mmhy2SO5L0bAB5sjddBrflZHYD1Z80iDHuzGcdUOId0OI'
        b'd0NI7AYOOXSErQvsCLU/uRtN6CgqaA7+aPwR+Qu1ipcgpyQl9SPjrH6w8s/ZCOIqIBFoZwQIc7XUxA1qERIoLJZ8N06QcaIUFIzFJIZMUa4I0D2BkQeSegZbdEN8XTk9'
        b'HiCymoLeNo/HxF1TuG92n6nKaFEimUdNRIAhGdaVkwSsPYX3PkfXJy61yq/rG5slX2l8RqcaMyooIs2oaMyoZOaNE0iqhTeoV3NuLWwY0Fo6YZZhLALxsRB7xoKQ+YVN'
        b'tRUKS5eMDdEcFbfgIMcHySMTr+prgqjyhoh1nile7W0PtXk89X5/q8dTIPVsoVnJlbEMBvE+Lz4XOA9YEQo3iZWN0B7eiMQvj6TtvbDP3C1s5g1VoqkwLG9ycVJxFSDj'
        b'Jl8wloo0uuJtaK0zrfJjtqCfnR+b+wF+pjpxrPO43kTEsurF6Ej9pTjOcp0FIyzD1HMaTwupKN54hRaLImySiC/imZ4Di1BWE5MaRlzqQ3NHFmApZvd2NrR2BJpWeGMp'
        b'uId5gL3EGgMfYvuKoGO+wNiBA+l0FuADXSzFrLADtcK2YHYtDXuVjj+v99Y11Q2vBknm8QOJK5I3CmxTHPbxkzgrEoOfJmBBOpsRd5HSxPWsW7R1SLDmgWlfg2fifB53'
        b'rdBt6ZZDlpDQIqsKwQeQisDqC4F57H4pj9cq4w3gCBmR+HJ3SGbPl7sXcp3lUJeEyhpQWyGUae22wRM5BLREtzVkw8ENWXM4yB0iBsbabQ/Z1WdDfOBICJU97JBDrOJ8'
        b'UsiO9AqwLD8LCfirQE8gP5TQxDOzBePsGwH0jGUQElwl9pgL4AKYyqZWBaY8Zg36PUpTQ5D0HmhPgF0lCGurPmbHjAhEASI0GevzN46EPLTfOBr8vgAzoIzxCh6aQKEx'
        b'vkH9AN8KDQpzzDXT/Pg8m2k2VDpUMj2QoTSKuCHmYzBNcPFZFNpQNoIbsvgJyRuu0QkiFJEwtkOR80qEqVNL+Kkl2WcreVNv9pu9Uf8S79yHHGO6kZdm1AHSILTb09DQ'
        b'XkO4mVCRasOfFN5YhNSRhHBiFy7yS4wzhq15WTRgzibaJJfFJrgsbsntSpPSpCw5S86wZjlsEjyxsIDva7WnxwcwAOum2fqmsuU+YWZ5jYXLmyBNvUnbN6+E78ADEv24'
        b'tl07aFqrFethDNpAwVvxoxKZu1iR5w0YB7lJy/Xpafou/SF9a3W8XJ5z3iToB29uPsf3BilDueMoIsRv5nu8pzjb6lq8JmEi9OjV9HJCbMzotB5ES/4S0RnnIn2bdk8g'
        b'oS0ObZegb7BOTGJ/TdwVmMclsL9pFE8RzQWA2QW2UgLGlWf+2BZbmL1no2gwujJ6ZYM8VsWlpMDVpriV1LXo1Y11KT3murKjrW2V0dRzKWTaXVCjgzEwsOfyCSwm38Ni'
        b'MiED/IokcJAMhVK5Rv0rZ+ynxCEQz8kYTwsBFnGfbOX+kobNgwS7L04+EfDJ7NnZPBLKweb00EoyXwj/u/okdunC/fUsZXzZQP68e6cd6BPWkPnxOeW7spOqi2fpnTwz'
        b'TkSJ+DAWlSn2pBqn9rqUGN2FeMzjWZRQde5ZPY1n6r3ycTSPCg+coAvV0IhOBHyvDo708OMCBuIDOkkAyupinMWE5vboUFkY0UsTiCNGJFISSXh+SR1hnCU9dI+NZ9Fh'
        b'UCjXW5cuiPCh4/4ys57zTKDV42n1+jweJWEMs86qkDL0LrfAMoLcUq5HZsHHJNxVzk9r4VvoREJ956xOynEBvZv6NT0j1N38NbUwkg6b7Dh7+0AgUgfjHBbHt4MhRAPH'
        b'9wTbN0zoAMg0y5xQm+iQbaJLTLMDuhdJ8OfS168IlCCq1g4FQ9qmBMRXqD0p6Xdfrz3cO+ZDow8T890pNovN0mKLlymUoVhP8krNVkRCLBXmARMiVrQttjFBHGBChhnt'
        b'JFBz0FjaYhlz6pu9DUHyRmgM0j8hMDLEVbi9fpO4KBifE7Er59xKL1xq1HjhUqNVPRvOBSGhZReEhGh1dCcsscJeunM+FBQ/iG/F9qUFOYP9MthQCRjRFoc6nGkIEzIS'
        b'Q3RCgQ2EtxZ4qxj6w3yzTGzfYiQme1g/LKenUwn6GgkMnY1YN1riMccMYBA6mabsByYIxNwTiVjsCBo6tHEG+J/BbbdIceGUAJSem/6jmOr8Y2bwkc6zgbOETyTmGJVX'
        b'mAyrFxjwFUvymSy4TWJEmEvsQJx5U6VVW6M/rB+fo6+fObsS9ec2zJq9PAFMJ2n7rYO0+/VtvYNpfgKYEjlCh4dAohguJWIFZsdNnDQZ/abO8vtbOtrjJ5cWLkHPjCDP'
        b'2KwiMJcGQQFYXoyjJAsj3KXgqnavuhlv7XEx3Hm2UrmV6tzcwzkCfzXwa1pXyT7oxbhyWLwd58BKObzaYMIKIEHkRoZrJ7TjCUOsHQyaA6wf1faXLdc3zyiv1B9HrVt9'
        b'S2UFUIrbljv0ndfoR5NOnuJgjApmsIVzJODoSxDFE8uEekukw6+WR5D541CvHaGD7i0m5XHmi8nkSwaNvhs6AkF/W1OXVylqBTa2iE7c1aKh3qDq9aLLWX/Pwi05v7tb'
        b'yj4GnXOQPx60Gm9a6vOrUEePfLSozqcUIfuMvkTqFKWJBfUqKjXYnqElpUWM4U62JE9oQnIVda2t/pUBcv+j1mFALvR866swveEUGeR6ILk4gGg6lRQXzZ4FoIPceMyZ'
        b'UAcJIf7Z6HMjYOLvlkwFOhtzuUYHvqgBrFaM0jboR/THAJF1ZulHOf1YlraNXmknb56rbdC2NA5j70Uff3Xe1b2HWr8+AdqUnnMpudFCJ2L2xSLpOsmw+eFpmA02RonO'
        b'v0TFqtiQTVDsigPYADnhFMy22EpbpI3AzB1zGaAwG/gdtWZqkpOZuETu2xyqPjXB0lL4e8VuKS6dGwy8AN+E2o/cUp7OIZB7ENSNcYncuJBgvAFaM48DDkJCOUBIDPjw'
        b'jtLAYygcyh+gH0y+J3T2DQlXoiaBBb60mLlIGhFcyPVIahvhzWaeN49cZBSQVyLAkgSvP/4QtdjzjJ2IxhweEkx7YFGx3QLpI9PdCGX8ilZKu+ptbOr0oEolcYExwRe4'
        b'cL+nhyXTKlEQUEFFwJWCzsglckqeRuERXSQ4iB9w0Uz08DMmTrByCZKtYzghuCfCQlgq4ck/CoJ4IFq7xc7bQ3gstJ4JgvDUPzCKhEMSiXUKO31BISShbgA7RFWsm3Co'
        b'F5iComZJscG+G6JvcAnRlAAGktfAVFMZNfDcARj7TszD3hjPCQ+hvc4agT1ZCDUu5ELM7YmzJmapxaOhmDjFp8SkGgy8bllQ19rhPUezNOEIEcVYitQiUxkWg/4fhXM0'
        b'hqctO35v4uleVF/J/+fPcT6wlq6K5NFu8PsAowQJMQUSlUuYW1YokoS+cRrDFExZUPBHuMiQQgUowiGTS51hmIU2LzHgXR6z+FXFq6JYM9DRGiSmoq1H2vR1Wg/u5Bbq'
        b'kiFq4XiXwVg5YG0JAiryZsF9XzRUc+TyXQVf08+kw8a4eBGbshRBcByto8u7RaC3SDuI7L4qca2R+F00Zt1Bx45W1YG6J/gUny1khydrSUAsoJA4JsOAeWHabZ7GVlT8'
        b'8NGQmQLTcTi0E/BnIv/1tNeV8P6NHr5SMg5PyJHwWUBkVHTOxkqLK8IlHqajBneIh27k4vEVSUAEQ4sb3rFTBXgbpDsR7qYHASeFBLTfWc2TKgZgrzU8EbUAMAAeCso2'
        b'fWnmE8yDJ62Khd3BExjSbBNzsZNVweNhCyx7vq/F51/p69lRiwYWBwaekW8sDuDBq6xm4mB9ih/JDJmplxIccCYtK/bQ+erl/DkQEUvx+FCBCf2GQwF/xiHNTlhTacZR'
        b'RTYvC2l8V37y0CZ+moSkcDGRbE3hEg80ackIBukisLsm4DQ6hzBFJcN0D1EQfsPM7OSQRDi/HHC+ZJxhwY7QCCXtEhDzmwIdWZ3BG0tDRVeCDADpBAfYc3S9D2S3NUHU'
        b'ZDNlyWoOwq2dSY+hLwnw2Lvgdybk/7SH9IcxElG8m0FjdQ4WN6oWawAE7L3y5JPiDacuzEwm9i8wnm8PA3AJfP9wDwOQ3SetP7DobtI5vEbWt8XFkdqusWX60dn6RnT6'
        b'VZgjaU+P0yLneHXHfxQIOE6JpBL7bVIgLMSCSX/gm7NpD+QTDMqD9G5QPMnmLS1mm+VvaJna1OqteZtV9cfxcQrEtLKII6UIsea4mgJZQQGZw9W8wToL9I5ON7NROimF'
        b'gLH0WEhGKZO80oq2dx6bwV5INWcyMcxxkeL3GsERkIo8Yy0OVKJmH84VnffLTQHMR0AVs9bVB1DDIGYj7T+lSY1ZUQve3xGMWTxtFCKIoifHrB7MATR0guJDTMIc6jy+'
        b'N04CV4LTEl9ULiITMohUkPmudHOYzhVz4gjFY6qiUx6mBorQhjaFnStWpUUQ3mB0EDEv5HwLDEPdFTxgJ57rGhNCzMW3iOq41fidrE4neSArh2+R1GuDVpQTrgaqq9mm'
        b'GOVcg6qHUAIaTSxPA0ZcYmNdC6mFJj1mqTmdTsiswd/RqtBA1zVQWIYiHKC3d+7Afw+Nn1diB/YOhpKGJ2Zpa4HBVWvpYG1OLfHoMYtXVQHpLMSHrrkdPsxuvAm0er3t'
        b'BrqLWWGPoaLqzwvDMQlr72MxdXXJelUgRxEOcv8j0QygvXVXSnzs8ZvejaXKDUynDlFoPSILZo65OgRSkjn+xrjghmihrrClYWkKxDtsUdvg3hA29cLZdviwIUMsCfJw'
        b'NN7pSo03lOXoXdJlKmUhtZgocWo8vzwcvUJ5AYmVW3qkQmkJK5Je9m4ZVJpQGy5JQwQtMBE0HSPAwBjW0iRvk8jJnjrfHBp1QU/DerEh8ngA16JkdZglrnZgI8oapi4j'
        b'oZFGtiTNZfyPx/1k8k/zl22K/3BwTAXO+FAZCjgLaJYaWv1A9DXycZlRTPJ4Oxt6EQ4DagGIvTxxwhxnQzXLg2KPGp4suXvbKWhksEZ1Kf6gIb/aciGC29mQyWox2FWb'
        b'5Ha4010ovLWyk7gH9c36SXRtNUffvELf4NN2UlT0lGbRkXV50o5gNa60t8clQahKLgHXGZcGob7mYklJC7NQQmJYDtsaZRLR2mFnSGd8KgUDwgMrO+wSzLUdHlslcqhL'
        b'SzJi0tSrrpyahO/ip3fomyrIGXQBHfEjL2jOGS4tBRWlJaTRKG1RhKDMUsauYIoPzzivWoUVXVy0ojhwJgUSRnB0SJoCxWU0oeiVtb1uqTfmCniDnnbVr3Q0AFHvwq89'
        b'C6bMrZ0xpybmxHfkwxfwk9PjMeKHezxM8dyDEWtM+qzncPFrphDrntizxjNIzRygPgWrPZdbPJ+M2ThlOJNeC60oaqvzkYdT9IGDSCDYs5qZR4qzCUbsVbz90+P4QOjK'
        b'oGYkva6JNwZZC7uJEiJJc4ZmeCgrMOlC9fqIREJhUlEH1lIEdpQ0HUnDge67gd0IiTkcqkzTU9jnm2Wm0kHl8OrqCFCJimWNsCWtWwJm1xoS2K6lcFdzc7lFJnMiM9vR'
        b'D7GLjuLi2ilXTSz6EKXYTIOxE5h/B5HjMWFlvbEMYjLs9+0dQRqtmEXpaGsPkIiJVB3pnDNmWYkqCIbgkuExGk/6RGhcduF22moXHrpYTL1rssOWyYcCkpsZtFNl8V1O'
        b'Gn/WsJh9urd1hTfY1FCnjsQiyHQUfxpM2VJq4oy08owPWoN6VTzNiUw6VMgB8WtEA5JofOkeuB6gy0V8E+GDFmD/LFlkMoKOM1i6gKVtitxtV6zdDiYk6HZ2fg6z7SS9'
        b'1fe7XUDfu/K47pSQXf2hmTOUAnOJAoidir07xVdIaQekn1Cc8Nas3Ya1L1eTWxNyhYDSzOVaOPUPWLbiyuHyuPY/QknukNv/FyUl5G6xbuXVqpCb1QL3hSEX/GLJVgNr'
        b'QImKO2TFEhWx2w5tcLM20JfwHnXFWY34HrVXFGvIEkoJOWCvtzfjr7PZpaRvkqE8h6piruUqsMRMhJFRcxq9w5/GWZh3Gmf57XD2b3/2ce0/xk8l4cYZcezYsTRtMdED'
        b'OIOfZyh0F8X4STHrZH+H2gQoh5+B+sw+70pPJ7usKklhWv4O0sNtbfJ5AwwVtdWpS5t8gVgmJuo6gn5CYZ56wFAtMRs+bPT7gIpV/R0+hR2H+HGtSg3e1taYtOgqfyAm'
        b'zZoydV5Muobua6YsmleSytY3HehLVIBExjWWQHAVUMFObIBnmbdp6TIomrXGgRk8rdAcr3EPnCtUYVG90IqYXM9EJHZfR5uHvmD6whLew1NvZ5Aef2MkbyfTAiVl78UW'
        b'g4PgjMChLjqsSSPrEObagPmDdBjOS8iZidCXcsqUg4GcZIAc6moRwCVUkiRMkc0dSuWSYQvxlz+fTt6Rj5mpCFEO7aSCIvFJuHPaUOyyxvANkofGJrwih/hspvUoofY2'
        b'zwUthgRUjnPDIslBmVzXfiZ/Up2KttVFl/gbRzMxPLl6CHS0qf/AtVR2IVbnFZVFg4eVFSdRTXGpMCIksvdyd/MRg883LL2WmYI41Io1bb369sr5oJlXxNxJZK6rPw0s'
        b'Nv2S0b1ZeZ0mAJFKiwOlBCs1wCL/gjOkbWhCpJDeeUyEnsbctLKbgAVv8Lf6VQN/s8JN3uyXyXtwsg3zC/F2YuCd1RZT6oS+oMjqEAX/BvY1iiUi9iYky+LIV735/ETd'
        b'Ct5A8uoe3qgmgf3/px1J9QgCEK2PtcQFAWlWm5TrzhragainRF97c8CpnxLbl4ucoO/kBwSGEHFbU1Nj6FLpu4NACGqRc+zs87XVqJ8mknW7vm+MfpDZJ+ph7Y4B+uPj'
        b'sASy871usJC/VMC7G1yn+rVD66Y2vbjpeTGwAwi4kVWXz573aW3mNWm7Bg2+Y8NnDimj6v0Fm4uKbvj+lQOnX9p3annFlldXvPjB76+79pVXf/TuguL5r34ofnX8tRtP'
        b'zi3bNuzDZ7880/Vq5rG31r+3ddDLExaWfnd7lbBiRmbu3aXDBxQ/cNE93/32pbeU7OD3vVU6fJD3hgXZt7461/rR87NvePQnwmeK8zfDXrlVPMb3vVP849ZrZfePS9uv'
        b'fFeY5u23/Q7va6N/MsWy6z+to7a81PncBnVUn/YXXr7yuZZrdk+5Y96fFrU97f2PJ6fXnvmtveJPatXrTwfX16w8+Xi/t/q8/bvgup+98+HaN3fveL3D98mInfsCO/ut'
        b'fqf8k+s6d+13rm95cvfsu7akDpe3XP/u2xnD1Lxn+xxW7yv4/ZvTbrqr8hd7azKuPvP6ByM/ntDh3Fk68otR1+0ri/06c/HulHvWL5/82dtpdatTP8+6bm9L6aB5OwaV'
        b'HdkT/Okbo/ZfPSd6d3rT2g9Pbviy9tLJx/ttaSx+dcWeJxas+tPP9o7eaR0/bP93bzyWOerW6uIPYpvblgvLS0PhkZ8WvveJffEDf37iJf7Yg996cdvGS/++P+qfn+/v'
        b'+/u/vXG0+qvvDrP/fEPVc2LV2sNlB/asH/W7A1fc/IsrHu7/QPHiBf3e+GH97iW1n9bow9YULHn9ssKw2n/baw/0mffEL1a86J17etm2X4/JPtTvB7HKJ6RXNw5fOPY+'
        b'37v/cU3g53sOdBUcn1m7w7djSf7Ip8rVv+f9Ktv/2YzF+3930c4Fdz/rv+yx23cszHxm4YHm+r83fzb84KvPTC5Y99eXW2+76Hu//tPhumlH+zUffyFy7LbFb5yYsaRr'
        b'2huLb+Y/69jy+KauRYG7/77uyXn7P1t3/y8/X7Ws/1WnqvT2V3desfTEFSdaPnnkjaYtH/3q+kFzJv35hfe7p89+eXf4p6lX/6qqeewDzzXLhwY/cdcf3hu966tnHyr4'
        b'PC2zc9Kcx4bsbfjKWX3fx1v/kTd25IfV91yx5O3P/uh5sbr2pw989ElqYcPz/3B+0fXglh9OKvhwxW/euq3/e2vfS3+p7CdntpVL13U9XrnrjTdffv1ovz57cwe3f/T9'
        b'va88F6k/eO+U4EfrhC8qx4x5+NDD0/r4T/erf+blGxsKqte3HDm5P/VIaOvirVnf6bdm7N6/lnz/zPT7b/hsbVXJ/IllH9Zaai/uM1ib9btfPDl/6Vd7vpwYvEo/nL3K'
        b'cePfCr7wvTu4oPEt1xdHH9721O+2/+HAw13iA1UP/vz5v19z2NK0zT7/+xvnPuP/7MCHc84IP8j5Ff9GR0FLzuOhdXe/+Fbb738/5JWjz9z80sKhp16Yu3XE0feHlVs+'
        b'z34+dvz28Gvc6BOP33Pq2ZIUFtLrZOBGbcNKPKtEX1dzZs2o0NZrW6xcH/1WUT+hRfXbKchVjfaQfgpzzaFzbW0z5km/8WLtpKjdoT+lbWfhku/Twvp96FJ2hrZx2PRy'
        b'PcpxGcBmrtPWidqJSdptZANvv84xV3+Igj/WVJSiIftjgnaXdqedIhwXrLo5oB1KDmJ+v36KApm3auspzxD92VkJOqX6Y/ptca1SSX+QHGWMvuYSdjprR+NrDJ9bUKyd'
        b'Ej3aAW1XEL3fjujU1kEDyEDUKEmLZmjHzB4y31/s7D40xiHljwiOgM9G6U+7E+qeMbu6XN9Ugsf9i5zJB/43Vzu4NP1wELcv/VH99uw8/ZlvUsoo0Y8E0Z3YFfrR7EAl'
        b'hYza0hFXLDg5pRe9gpX6Trv2uH5LAzl4HaQ/dkm8eTBwT50l/A1Ukh+AKv2YHHBqR26O7wyZ2g4g9P6ZbegbNqmR/42F/b/yUzKQEQr/V/yYgq1Wf53i8ZCjhjfgh6uT'
        b'ycHBhf85RLfdLbngL8uRZsvOzMoS+OFXCXx+tsAPrpCFIZNy89yW3AmSIPC5/OWtQ1e4eJsNU0PSBX4g/C8sEvgsGf7b8h0CnyEJfLbcc3Xb2X0GXAf2RRFvtgv+p+Jd'
        b'Vloh7/CjUr5bSLPkD8ziXX3TeIfVxbtEfF/otsG1L+9aAr+XCXwR76pRH4lL24QE7xH/f0H38tND4eOg3cCZlPODnYmeMEj++OSYG+L7jLZ92SwtipuIO0/sd5O2qWlO'
        b'7DkuUACr7KK9Eypuf873uwlp61Zec+X8gyt/1Ox75wf77lvxo0vefCNw5Kq09SdHjZs5bq385X1LCovDVTMLh+qbJt5wyr90lP5byylHsXjT8688e/vRb/d5uX7XiLbG'
        b'zaeHfzbr7mte+fL64e+d+Gps3ZTPXsvYfMeZoofK/8hbPrlxyd47P96575GZd+wfu+3T8nmPl/7ms9iGt2Yse2+o+6Mtr617Y5P75fHqtFfHK7dvf6F49LaX//C9VWf2'
        b'/O3NZ2zbFg480XTolVv3/K1tt8P659PvHT/4s/pPa3e2vjO446Oh4pcZ1xVUH++zI2/nPd13fTy2cXPzyf88vfoV4dV7+n68e+PRgUueWxT96/obc3R13oCS26JTVy8Y'
        b'PWb4goanRyxYek9ey5FNGy/79Pt3lX7w/UNvjlvz0YApP93Tx3nsxN4X2iY+vuPpybV65V+3bzuS84+H8u+rHZf/4t5ZNdenhF/a+sJLkZkvbfe99dXvtr/46/dX56+7'
        b'+9JLTz542+uXPZbiP/DjR257ednUww8dOv7zH6368/FRv616tF/5qr/debTPkp2BTe392qZv/3jn65fHXloVrP7xnzYvDuX8+LsLD6354sddXfNW37XvlS9+NHrM9yb/'
        b'5LKfrBzz6f1DujJOLvzr26lHfzD/jj/ueae96oOO96OXp209csOH49/87hRH4S+eL9rQ92+jJqcX33n1xD6X/fKlCZkVJ16amDP278s38+ty6zbaK9ujZdf+h1z7k+HP'
        b'CdWPHPmhvOQv7Ruu+OSJ18YfOPzOM/vmvPvS7H2h5ds+GXjxZzf/8vVfvfiz4pKxtMeJ2l36AWMpbdQ3aMe0Y+XGYporjtBO6huDRZBtjPaw/h1tQ8vMs6gWolm0zQNZ'
        b'gMBt1+nHgRZZc2lSUFGfvpO8PGpPace1HWXa4XL5Gn0D7JS38jdMzKbAZqp2BN5UV5SiZyh9CwUZ3Fitb7Bq+xdwA2otGdo92gPM6fo67VvDznG6vkjfw/yuP+qcT24j'
        b'R8/zVUMmfWOJdqt2P2Ytk7nUkWLLTVYWXudJ7Zi+Dvp7XBw2Xd8ELZ1OcdaGsgCKezJvqtY3DxX0k9oJTvDx42CENtFm3zFXW1uGztznLNHusXDyBMG9rIRcFclTgM5B'
        b'Qmxohb51Cs/JncII7d5VVF1Dt/ZwNb4smVEh1E/hbNopQQtr9zqYI6GT+r08UHrlSPTdxgkhfvzSgdSQEn3HQu2gvr6cG6Ef4wTtOD9vtH4P8/B8MqAdNnxpefXd5E7L'
        b'EWxkBd6SMZu8F8L0ruOEbn6qdmoxvQnpd2k79A1zKnl92zwocD0/bWEtRZfUjuoP5EBdEaDASqfrd0H/kbBCasqjh4svtVy5YBktBX1XX32ns6bCmV5aXeEYqq/XHsUY'
        b'sPnaM5K2cyRQr4ig2rVDY8glGYwHOiKrBooyZ5mkb5QuXqGfCCJDXT1f0TcMm8kv0e6Dhmznp9bpjwWRQZ7cZ26ZHhlmbRgFzw/wC1dpe6jt2qkru/UNQI2J+t04TDfz'
        b'E1wu8tU0SduqPVpNyBCmhtjuWwX9QVXfq+8bRjnG6RsQYd4+ds6cihk4f7MtXMYVIvZXu8VwNOoeVs0C8s4ZrJ+ooXLcN4lXXi9RcwEU7nRDg2WOr+XSxup7BuosLCYA'
        b'0C3a42Xa3UBYJ4TZhUbTPBWOnAoTf7AMiH7y5iHV89qztVMYRKyp0G+triiZOVvf7YTFVCtkd+vfoeaM0DYOYCt4BiwZ6NB2YbF+Qj9wo7aROtS3ATq3YVxmgtKsBPzB'
        b'GlG/ZdQ0KmF+p7apekb5jIriQUa73Pp6sUZ/UrudGjZEW63dXq0fqYQ80GaJ1+7X1ukH2BxDpoVl2nr4ED+dDYNeMgPK1+8Qtaf0B4up45bxGAlFOzS0RFs/YNjMco5L'
        b'1feI2i1SCXXOAizPLdXaA9qasukzAMDyeW33VZcSOIzXH4Ph3DBNewwBHtgS6Wpee1qPttL869u0fdqBspkWjq/m+vXRt4s+6rK2fcBQWNW4qNApJwxKSGjWDun3AjAz'
        b'bqjgEv1pGOz1+kEWtlhK44Fjiuph8ggGhP0911YDc3PZJfzCuZxVv12QtbXaARqtq/Rvzaoeoh9LcrU5QLxCf+Rael+gHVaqh2t7k9xcHhZH6Gvc1Li5QQQZdMVcfp22'
        b'zfBw59YeECfzMN4IEuna0RvPdX2aPVF/Cni6E8TzlU7SbinTvqM9cY7zUfQ8OkrfT8wW4Kl9ywF1PaPv0zdWAKSU4jTNQseqs2fR4GysrtAelrjZ2kGrfqt23yxi9G66'
        b'zuJENrId8VA1Lqos/V5Ri+i36ftqtTVsLT8zvpFwWOX02ZU8NPBBwXet/p10bTW9bsjGuNmIc2AHQCg7LlRrj+rHr2Vj0OmuLIPe7NQ3z9K3VJeXVMAUZhaK+h3aLn0L'
        b'sciwog42VyMIQg+jM8pnDoMh20lOIMthwezQH5hP6+8S7TA0nO1Km+aUAA+mbcL9JrtYEmvEgI2mZJF+1yh0xTxnDu0WVmjPMWHmaP3AgCwqZJx27+Uw3QoA+eZZK0gi'
        b'B3yilcvTj0vXdJgxew/rJ6qrZ0lzKvSjWBSGJkrXYVfbDQvyOK2bbi3qguG+bxbbkjipgtcOLdZYj9Ah7Fhs6TBt16SEDQxbWzBY0taUNBE0jNA3a09Xz5hdOjt1mpWT'
        b'JQG2AP02tq4P67u7yF8vdrQCxlXfK8zXTuhPaac6LsBHsMEh/p9ncv7tfuLHwMRwPQA/nFMQbPzZfw5gZ5j+CnrCk3jM42ZvjAMOg/li6n2Cw7iD7wQMfGUjz05ZSWW6'
        b'qDzMg6eNLrJpttEJpEuQxc6buXP/Rss8E3Az5QRU1Qh4gx3tHk8P52SeEhziE/uH56+MV/jYlcAr0Lu4NgKWgT5JUBcg8H34rUfvNfAXXRBZgGcr0YvgKsBVgKsI1+zI'
        b'gkYOrvMjC5rw6ogsQBu/aH/Mj+fNUT7Mhxc0Csy0rJtDfYVWsU2KprZZuvk2uVtos3bjmZ+s2FptbfZuie7trY42Z7eF7h2trraUbpnuna3uttRuK54oBtOg9D5wTYdr'
        b'Jlwz4FoI10y4ou2xDNcBIS6SCtfUEJ2kRJ0hMvCIpkG+LLhmwLUPXN1wzYZrcYi0JKPWkBQdqMjRHEWM5iquaJ6SEi1Q3NG+Smq0n5LWbVPSu+1KRjQ/JCpcJA+VuaOD'
        b'lMxoiZIVrVT6ROco2dHZSk70KiU3Ok3Ji85Q8qOlSkG0XOkbLVP6RYcqhdGpSv/oxUpRdIwyIDpOGRgdrwyKjlIGRy9ViqOXKUOiY5WLohOUodHLlZJolVIaHamURa9Q'
        b'yqOjlYroJUpldIQyLFqtDI8OU0ZEZyoXR2uVS6LTlUujU5TLohOVy6MVysjo1cqo6FxldLQm4ljDRQcrY6KTgjlwl65cEZ2lVEUnK2Oj85Rx0eEKH70yZIU3RREhZAvZ'
        b'G3GUssLucE64f3h2o6SMVybA/DlCjqiL9E96PMG6w6nhrHA25MwN54XzwwXhQvhmQPiicGV4WHh4eGJ4SnhqeHp4Zrg6XBueF54P62GAMjFeni3ijtgiJWuEqD3MQtWz'
        b'cl1Uclo4PZwR7mOU3g/KHhguDg8Jl4RLw+Xhi8OXhC8NXxa+PDwyPCo8OjwmfEW4Kjw2PC48PjwhPCl8JdQ8IzwrPAfqrFQmxeu0QJ0WqlOG+lhNWP6QcBl8MS08o9Gp'
        b'TI7nTgmL5I8/BfJlhDON1hSFB0NLLoKWTIYaasJXNWYqV5rfdDsj7pCTahhC3zqhlhQaz1wYob7w9SD6fih8XxauCI+A9k6lcq4Oz23MU6bEaxehrSKVJN3kwHnsdkWK'
        b'I65IacQVckVmrBFIZwCflNOTcvbkJlfISfoYU5njf/KsQUfevauV4YbIDKEiXItdzQ+igw+umTd1sUlzSKg506c4MLSkqIlpeNYV1Xc0tQabfCWCegMinIEJO875nFF5'
        b'Gn0k5kLdsQctcXcdeBisPmpal5RIgN2WeoONKtoz2LydDaQAQ4bkeMTtb4y5TAUgUvzh0dVIG6BDuHOgD+y2dtUbCEBKbPUvRXNjVA1Tn4ayT2OnT2Otp7FxpzvxB2Ml'
        b'nsYhIeVmv+IFpEqeHlAlPCa2+9tjDihd8TbWoZ2BrdHDzlGZj58eTxBxRByTG6mcmLPB76lTl1JQUoym6mlZ6fe1roo/csAjHyss5oL7QLDOcKhpg1Rja93SQMwKd1SY'
        b'nW58gWCA3pIiO9Wwok7tSaDCLKboO7px01M1QAoMPj+V0wpTWFfPPlC93hXo6BwTqJ9ACUtDq7dOjckUWWVETKxvWkpK4Oh1hgXBiDkwejW7Zwo7J4xJDqp1DV6Mcenx'
        b'QPZ6D5tIK9yhwkFM8qjexpjbozQF6upbvZ6GuoZlTMcXFobC3KIh+XVGGFqSFIkQ3yB3QoFA0IbPdF2PbpsizJlbNvmBdJNHSXJS1M0v77uQ+dDqMdk9x+bzm1wx4eL8'
        b'PK4vRiSAw1y08TaiYphstvGH8CZiBfTmArDKw3aEeEA8QiOaPRQqFNOGjCHESBEpbEkhKeJosamrI65uS0iIOFsEdTrcy76hlOLU6yMuJ9dtiTBLRSHiiGTAGzf03ZWD'
        b'YyFHrJDut0YIyZE+6MHUdxidwgTuhKeFkexGdFmzHVW1oKZMqOkI5c+F7/tieb5b4Hn/SDrl+0skHdCNtbOIDMdyu22Q1xrJgrwSbBKiYY/0PIyshE5rqEy5xbaVV4dH'
        b'ZPjS3llJpRdATtPJjQNKMb4O2eHOgXcUCwjtW+y1HBuJCE/lRODr1EiK0zBhC4mRNHqbkou+eIG/U7iQE9+FBEC3KTkcs6wib6J2FiAgrgpHIwtlHoAZcUTyoX4BRyhk'
        b'yUKTklw2HvD+u9TmHHNEQoJhEMFWjeu/dCQx4N9AivxPCZpxbcuwngM1hKTdjFAlUhV1dmTBRto8GfgnSqRB6SJCOJeIWZnP5vN5SXQLbiGN74vfiQ54BnAjxEEm3diD'
        b'CGR+KRgg44ZpLjFAJisRZOCtiBMXkWCfGp4ERDhxZfCNRHe4/C0hKfCXCAbEkiP4l72GzKm6YSGrq0NWso6xhaA2tnAAaPKrON+ySEFkUGQIAEJeowWW8fMhOyzfq7od'
        b'EdRJc0C5zpAjUgDA+RtYdqlOLg93ZRHu3XgfchH4QUkhJ9CHqcbydWIO9i7kqOKW37WQ8/kigyMpkYJGLjII/g+B//0jQxv5SDrWFOmPIJYFFCY8z4/wkbRIGlJmTVYC'
        b'cwsuYgCn9JANepQCCx6uIQCNiDuX63ZHMoAewCfuHA7AJoXoBCd8VU6hujqpBLhvhF5v5rstvr/AEzlSCmWmhlIjufQeEAO0NzVSRKkiIzWYUoONVDGlio1UIaUKjVS+'
        b'2U5KFVCqwEgNotQgIzWEUkOMVF9K9TVSAyk10Ej1o1Q/IzWAUgOMVP/4uGEqj1J5mGpMhW2iAqn7ELcZESgiAehr5KJICvQ4LZS2VWhfHZLo17pVCDxM6yUH1wuUAWPf'
        b'iK68jd7kcI3k+y6SiesMShXJ+YKEI0/+wvB5WUgiDUopCYGk/28B2ZLKfwO08T+PmsYjalrdg5pQoVCwGW6qZdHNYqVJAs/+ZIpJgybDWZAzSzZDVqN76zQJDYnRr5ZL'
        b'yBAdgLDc/Pn+MgSXmAYIDwNb54suEXn5ODoz3cwSOmNOJQFhSbB4bAY6kyNcAjoTIxbayYFSidiBwAc0xlSzDfMI09d+b7P+Xw8RQMN4SDbt7tkwijgQSR1ymh16GDsk'
        b'ATwgySEABs5gnWDamOi2G/XEI2lrBLWc3kghygsdTIlghBCEolTASCkRK0uhxnnEsWUIj+U6IxkIcThUhK1EC+DTiH0k0H5VCbrmgNkARxr60nifFrEx3ekQOdZHaEyC'
        b'ut6HL/N/drWelBOsoySBjNWtDr6viHdsHTl61hF+lmEOuw8pSaD6IqlI5caHXWLD7h9Cg94HqC4xwIYd09mYRgqG/KUDhQhrbia9dWzJp4FDK3RrLqn8YyppiIFmi1hh'
        b'2wKaFLaLZSExsNGkp3ksXwLqELbPzqkhi/p7jPuIyBI2JgtsIjCJ3dZVjhCpf8M2lyVxQa7Fof6MeaJh8Svpm1wsY/n2hRwx2W5g+DPDWeGcRqsRXMbWUxNQjRZSGO8b'
        b'ScFn5vdsYwOSwQ5QRW3trApZ4NoYr8GOQg36dhF8C8/gjT3+bbwdQIWWL0yI6JtoIZPk7zYeKREZD+gyDDPFZ0D/DBgPBz1D+suR9CQT+wQnVGJMCNarGrKKP+b/aS8Z'
        b'MXdTwOOvb/SsVFFPWrVZ4+YrEqlSOxg7Ajw48uP/UhCOvH8nBP972bBJSgAZgemNo/54BqByWZLIUh91X9DUEHky2e4Wc634NMPqNsS0GXxJLhMwkELvBI5cCKwKqEfw'
        b'2VH8OYY/x8npQAN6xgmoJ0hjv6u1qV59jG7b6oLL1MfJvhluvHUYLkH9DtmgNClqPyoUmO+YWFcPbPuyugBaQceshnOnmDVg3ixt9dcDy1+S8t8zZCUL/w3k6f//5185'
        b'gMA1iVGoyAstJwjS2YcPbksuHRfg0cC5hxPsT+rlz9Xr03/9Tzb+x9OyS8ywSuKsywACxcZm/C1ySeLwvnhXNRnhUrDJxB0KAvWzZl6JqOJpi4o4le5KUtU9HMVK8CRK'
        b'9DweA0Tb6toBToOqGuCZ5SyZ/7ODkEcJEKd0Nnjb0RWSipsrHos01HUEvB5PLMvjCXS0kyQQxWZoVAJPnZ6ehPpKsheHBDPTqja/0tHqHUfnIejJUxKATBSAOurtcOZm'
        b'LtN4PlAgd7WmRt7/AhcGGLE='
    ))))
