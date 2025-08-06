
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
SWIFT module of the Python Fintech package.

This module defines functions to parse SWIFT messages.
"""

__all__ = ['parse_mt940', 'SWIFTParserError']

def parse_mt940(data):
    """
    Parses a SWIFT message of type MT940 or MT942.

    It returns a list of bank account statements which are represented
    as usual dictionaries. Also all SEPA fields are extracted. All
    values are converted to unicode strings.

    A dictionary has the following structure:

    - order_reference: string (Auftragssreferenz)
    - reference: string or ``None`` (Bezugsreferenz)
    - bankcode: string (Bankleitzahl)
    - account: string (Kontonummer)
    - number: string (Auszugsnummer)
    - balance_open: dict (Anfangssaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_close: dict (Endsaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_booked: dict or ``None`` (Valutensaldo gebucht)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_noted: dict or ``None`` (Valutensaldo vorgemerkt)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - sum_credits: dict or ``None`` (Summe Gutschriften / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - sum_debits: dict or ``None`` (Summe Belastungen / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - transactions: list of dictionaries (Auszugsposten)
        - description: string or ``None`` (Beschreibung)
        - valuta: date (Wertstellungsdatum)
        - date: date or ``None`` (Buchungsdatum)
        - amount: Decimal (Betrag)
        - reversal: bool (Rückbuchung)
        - booking_key: string (Buchungsschlüssel)
        - booking_text: string or ``None`` (Buchungstext)
        - reference: string (Kundenreferenz)
        - bank_reference: string or ``None`` (Bankreferenz)
        - gvcode: string (Geschäftsvorfallcode)
        - primanota: string or ``None`` (Primanoten-Nr.)
        - bankcode: string or ``None`` (Bankleitzahl)
        - account: string or ``None`` (Kontonummer)
        - iban: string or ``None`` (IBAN)
        - amount_original: dict or ``None`` (Originalbetrag in Fremdwährung)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - charges: dict or ``None`` (Gebühren)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - textkey: int or ``None`` (Textschlüssel)
        - name: list of strings (Name)
        - purpose: list of strings (Verwendungszweck)
        - sepa: dictionary of SEPA fields
        - [nn]: Unknown structured fields are added with their numeric ids.

    :param data: The SWIFT message.
    :returns: A list of dictionaries.
    """
    ...


class SWIFTParserError(Exception):
    """SWIFT parser returned an error."""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzVfAlYU1fa8Lk3IewBERE3iDthCQiIiLtVJAQQFRVxgZAEiIYEs4D7jmwCLqCI4ooLgsomKFKdnvfrMtNO93Zaaqd2mWk7dex0nLbTTpf/nHMDgtX+3zzf/33P95sn'
        b'l3jWd1/uee/9GPX7x5PvbPK1TCcXLUpD2SiN03Jafg9K43WitWKtaDdnGqMV6xx2o3USi2Ilr5NoHXZzuzido47fzXFIK1mCnLPljt/rXJYsV8amyHJNWptBJzNlyaw5'
        b'OlnyRmuOySiL1RutOk2OLE+tWafO1ilcXFJy9JbesVpdlt6os8iybEaNVW8yWmRWExlqtuhk9jV1FguZZlG4aEbZQZeRrx/5ulLws8ilCBVxRXyRqEhc5FAkKXIscipy'
        b'LnIpci1yK3IvkhZ5FHkWDSryKhpc5F00pMinaGiRb9GwouFFI4pGFo3K8mNIO231K0a70Vb/TZItfrvRErTFfzfi0Da/bf6phDwE0Sy5KEnTSz2OfAeR72AKgphRcAmS'
        b'OyUZnMjv6Ek8EkeuJ2MyDNUzHJBtAmnEVyJmQhmULExYBMVQvlAO5UpogM6lySESNHG+GG6T3utyzuZPB1/Ex6DCokyECtiXCOX4KuzjkIuSx824Fh/RcHYwROTr1QtG'
        b'EqUER2jxf6FElpcdY65YRDDmCcYcw5hnGHPbeDvG2Y9iPPEXGM8SML49XYLcEPIMy4JlFwKcEGusjxEhOjAsajZXk2IQGufpnJAnaQuTREe6J2wQGt/lHRD5KwvzCU1K'
        b'GuuKDC6kMWvaMPE/vNDs/dFfT/w73zEpcMbfkMGZdLyQcpRrdkSelxIzwu+Y/1xQIzSvXvvAo8qDQ9MW3eV+8tUlfoF6kE1BOlbBZXyZELcsdFFAAJSGxoVAKW5IwRVw'
        b'MSA+ESqDFcqQ+EQOGT2cZ4yVD6CtSy/CYZS2lK4oS9RHPe5XqZfzKPUkv6Ceq0C9ytlSNBLJNruEZbjVrFMhWwhphEbbFAL0viAV7IOShEVxymDlUhSuWjIEV6XgMlyN'
        b'sh0cs+AonBwHF21UCJyN+Eh4WgTuJOvjBrTeKdJGt8t7ajs0QVcEbqftdWhdWq6Nii5c8hqqSIwIp+J2GGkmrWWjn8JXcRMcckA+uAIpkCIXdjMYP1S4IG8UMNzRMyPh'
        b'yOQUgW83F3mhcWjDWBHKWPUbUS7SX/fcLbao6eKlz32R8VnG2qwE9UtZioMB6jj1XzK8NDlZhsx7GfHql7Pki5VqebJKfVl3kbs0OPszbbz6Rf63k+qbO8OV/LOL31ni'
        b'ezr4OW+pZ1DdjaMthxp2D9LmhRnDRNkSFFc8pOJioZy3Dif7LHTTuhICyRNtIYGLFxPm8mgILhI7DX3KOoopHVyAZuiE04SUpVAJ+4hITuVwCz6Gm+RcDx8gl4vMlNMP'
        b'Lw3oe5/pWWbTJp1RliXYLoWlQJ9lndnjwgxTulZt1VHzaXGjrB3jxrlxnpwTF8CZKYvNlL1yUY9Dvtpg0/U4pqebbcb09B7X9HSNQac22vLS03+xqZwzO9LfDvRCVxlL'
        b'15fS9T/w5CUcz0nY1UZtH66CDtwaFBccmITLFyqDiThfUxKOwU7xMCjG52I1vF3sxI+RYWIj+mSYZxZARGSYZzIsYjLMbxM9zub1KsVAGZYkMWnaEDYYDnEb4ApCISgk'
        b'H04ykRw9hFD/kGgmHEEoFIXiEzGsGd/Ogf1EyGbgJkSFTOOgT37BibdQuV/9zcIvMn6XGadOUK/N+ov2LxnBB+PU9zO8slHrsJia2mG7h0VHoEXDyrHjq/ueknPWoWSO'
        b'Mnx1UHwIFCsTkhxMG5ErbuGhTpdm58QjpGatjNA9rgI/swwmtZUxlAo1CnTjxISdZpc+ZooZc3octLpMvdVMB5mpxZHz/RjIm6k76sdFOj2oj4t/GMDF0ZQIRavUvTxk'
        b'jiGYQyNwLTTkivEBKIKnbb501EHyn50WXAZd1qgwMeIzEZzHDVttFG/iJHYGWKDIlXRxiNch4lAO4HahrzMD9lqkbJoI8dnEoOD9uMbmTfq2TJ9mmY0rrFPogkZiCWD3'
        b'aJsPnVSSgU9acO1U0sUj3kQmwZkCG9U0KNmKb1jgabJn+2S6G96NoA13wzlhu9Pxqy24DvbSXgfSuwdBu5uJ9UEzLobbFrgSbWYzybJNeO8ghl/MtnCySiMBehIFhpg1'
        b'aINC3MD2JFjvwS2koRXKST+BiFgqaMc3jWzdaXAjzYKv47OWCDp3O4IreA+U2IYw66bxhrahW8k0gj2uRXA9Io3t6OUPhdC2DBpIlyPpOobgBnGrbQIBqje7EHh243aL'
        b'mwvZD65xkbONbEXP9GjX7bjQzLiAzyPoxIXr2CS4nr/SdSo+CC2TaR9x1aJNUMjM6Vg46OQaq3cJp3jDYc4ZrWWgj4f9ca6wk3w6GN5QyHG4egnrmwKHYT+h5SZoK5BS'
        b'GE5zQbOghQGBT8P5jRbXeGd3aKYr3uaiDIsEInfijhWusEux3gYdJLyDFm48PuMl9FVAc4YF7+RdzVY6q4bzw+1wzDaM9j2ND+PLFjgwzgqdrrS3nAvC5VDD4IcdCzYS'
        b'Es+TuhNqiBy4GSKBGCs88WFLPLRL3aUcEjlzs/EhOMB6wqDYbIGbcErqvp4idp1TjHETYN/jPtMVqke45+F9YiQay81ej6+wntGxUosCHzEzyclDxF/X4oOMtJMIe8ss'
        b'UDzLGhUpQXwWlfDGBIbUtvXQTvQC7yXcdxDEsRXvjBXYeCpWYdEFAZEdD0rBK1wk7tIIXbfzect4b+iwd13iInDxRrmMObQF6YO5SB4F3PX518Z3VJPSWGNKqjcXzSPf'
        b'u8teUacufGcma/xu3lBuOo+i70bdzfMddlfJGn0XDuNmE0NyVzpxbc3cHSLWmDN+ODePR7K7xhp1KvejA2us3jiKi+OR512p2uSrK3BhjX8b48cl8Cjs7rajWl8P6XrW'
        b'GCodzSXzyOnumvhM33XDc1nj5lFjuBQKp+KNzHdGGJ1Zo3zjeC6VwrktUl8TUDqYNUboJ3KrKJzS/Px3rN9yrPGjiAAug8K50WpJjXJRCHBqgohTQLPvTpWZagYptKyx'
        b'iA/hcijwzk06363fCyBV5ys4A48y7jp/bnlnaqEwcsHsMC6PYqR8oEud85EjazyWFM4Ry5p8V3nP4Du4UiCy59DJ3AaKpjJlk6900HzWuGfMFG4Lj/LuTjVl+m7MCWSN'
        b'yZKp3A6Ku/K3Jt81rwlwxsXGcHt4FHdX/iC3Jtk5XyDdyBlcMSWIMjOnZmNAljB90yxuH49y7sqH2WqWVllZ47rFc7j9lEob0zLemf5zCmssMc/lqniUencFNqZ6709k'
        b'jYtj53M1lHTKV/JSdUskrHF49gLuOI823JXLttc4rxSAvx2j5E5Rek7+KSM1pFLOGp+ekchdpKQbkq1JlZQGsEapPIlroqRbOtic6rF3Amv8ZPwirpmSbsgza33zx09j'
        b'jd+sXcy1U9JNvpvp67NxoqCOnaEyy8pAVxeqdW7cbLg9nxl0qEhe6boEbpql7kRNB3EzcIULM3awYwIxym0cVENngUXELEYQvpjLVB8fDYYqC5zERdBmgXaq+1XcGFxp'
        b'lIsZCN2bn+eOiwiu65ZvTjWdFkTPzf+33Cni8e4WhBtSdYZ41hi5/UWuXkRkxxHW+RYUbWGNFt+XuIsiQgDHidpU0czlj4+safppz94eZiwoy7kvyhb/56NskligIb+I'
        b'UJKSBH97zCUaly0ktrASSsj3sDJRASUkYPTJEE/EHbicAf0PjZC01HAZCZfdRwtx7vtpLGkJqNNkGNKMc5FA2taZGSq4pglVQcVCEn45wR5+Yy6+LJCWJGyLcBtup1E3'
        b'twJOrkIkrC4hXoHZ3AaoVwQFhARCcWgS7M12QG7ZIg8d3BDs5EW4hEtwm9iEbxAHiWLgFt5rpvGJkEH5iWmylDMuIcNQNTpEaFwezhKw5OfHZwRPT4pELMxKmo/3RNCo'
        b'jxuMDyI1rlXaaFg5f3qMigXDlTS7VHmSEKMyVIkvB3BIZnWQQgPBgQnV1UVwIiKS2mdciqtQ5jhoYvEnnMBX8M0gkkvR5HQfSayU4vVwDQ2Wi2CfGncyUY1a6CvkFsfx'
        b'SZpf+ONWwRddwHuhOAK30mykFnfjk8gAl7MYwKKlSyIiyN+5xB+fQNkkHBEIsl+N6yIiSFgMh2AfPo3W4rIstonDU1AeEUVXLcS7cA3Smmba/JibVMIeVTyFLYlxBzfA'
        b'aSTNE0WTUOMg20uNW+ZHRBEgVg7HR5EO6hxsI5nnmIArVAlkViiUBw3DrRxyTSMOBG71esTd+GxsRBRhB25yJHFFlnExA3IwHMFVEVEESFwKFSSqyM4i5KI9Knw6DMpI'
        b'lpLoIB+DxH4cPrNiGFsLN+HqaRFRRC9mxeHjKAefCmPyEbrIL4gyBEqSSObaCsRdus0QeeinM77Y3KE1AhMfj+bgTnwKGfDtKEHozoyfB2UJBG0R7ohHIrjFkTynkFCR'
        b'3hrA58J8LAlKZSK9/9CXVgYo5IGJCnkI7oQjvAs+p8PnSXxZHxCAG3yC5CTTqA/yxlU+Q6B+KL7AE9y8PfEpfHY5gyQv1S8oKSROjI8lIfFsDl+aAZUMsaSpqy3uZpto'
        b'1FxiU05wY/Gu2WwCbp26AdqkpGcFCb2gg5N7rWReOZnEiN3QRufgE+NJ1y0uaJIQasSTIOm4hczhBm1kFsp/EFwV4q5bhhjLepsLB91QQiKAm5wMVwkUhNuwN9MCHQXQ'
        b'7gDlJDagUdnoXKgWgmoS1YpJdAXt7txaaGXBUjhcm8NWzYQTg1ylrriSh2pchkRp3Eo4sEWQ3d2TiKW0uhSIcQW+RHZ8mhs5hcgTRa3AiGtol8NMaCEL7uRkq2IFO7Eb'
        b'l1uhzWqGdpEGTpBZt7gRaXBJQOEQ1Kot0GqVIA6fyHgKQeVaXMwWdN4CJa5O7i4IynyQaAoXh1vkAm4HFSQwbrOtd+PgGq4nm9VyE4mlucZWTILjcM1V6uaMYmEXEk3j'
        b'lHATn2Ir5kMZ3knCHrOUX7YdiaTclA0pbM6cRBoSe0CrO28hlkI0hptDrJnAsTNDDZb1dKuGwQT0Ds5v9iDG4ml5XhYXwq4MyuKDnAxOhwsyfXKooyvtCMbXkciLC5sv'
        b'6DaFuQQOSXBdHELBKHj6aIEVu3I1uMzDBe/DLevzOSQmsRou90oRco4rUDKOzOu0ZBAhaLc5IDHu4vDO7ZGsm4NafAuXFUCHF+x0wyViMruYw0e9t8ilTHTSvfEBVxdn'
        b'aBXl4VYkiuEWhGNBJ+cSa3yaCpXICAdZZD56QbyQOLRGbWOyi4vD7cK7QzA2uFa12tWJ9jQrkMiFU0RvExjciU/6QJsb7TnlwaLNiXAYHxbyoiK4EEyY5WYW4XJ30nmO'
        b'm+iIqxjZU4nQN5EUrcPKqdNI10luHOyZyqBwwrdDifi6OqOwFaSnlYuCG/lsQUeog9OuZrgG18SRJH+mqqLIMgiGcq+jUhCZ47iFyQxPMj7W0/rULFe45rxeAnXEzk7k'
        b'pq7GXaxnpmMA6+CIOyhHogAuZjs+w8CbqxtjweV5JJuYhY8wtOT4gllYrgbfTiXw5XlIRMNIVwk3YUiCcNvq5jLoJiw7hCvzoQqXE89xOYpY32o4QmT98HIO6nEzGrtG'
        b'PAQqJghu5iCcxdVwyHEFsfkojCQQt0y2BLrJYZEjmXOEGNbivrXmLBNWqyLt+8kureRvFXEXnaRtPxlZ5Eyy2SNwETfmrCXm6gY+5YyPKjzZTim4c5ZA1JxYgagKf4GD'
        b'Z3HZEjtNZ+sEkuIWe3LCwWm4aKddiZ7RbsFY1jON7HdAIJ42jpEOX1pmW0KD4YW43RXKVcSGxyUqmMkNgvLE+JDFULxwSYAiMZ4gcYTYaihXypfFEQ+6GJpJOrMcWYbQ'
        b'm3uXvXtv8nniai83ksfsZSyZgVtTBLLDpSCB7vjYNjkvaEsh7vZSKUIC4+nOV8QjCNc8lokM3AwbuxdWRYhZQpwRddnl1LtxJGapISk3lG1hZEiUjiexTFxw/MIQfM0o'
        b'Qa4qIv/b8PHeew0XqbQSKc9TCRqD98Mu5jShE05MD4pPVIXQrZMcPKciL3yC6Ikv1BPgqPJsEEMt85ouJOEkXhP2a1n7LKIpxwW3ecaVes05asM/f/7558i1LMqJvq/K'
        b'CNbLHJDcm7FwMNxaw7RzmkRQTj0xv0wiq6fADcG1DPEWXMtmdyHhOyEZJ3iWJDgpeJZ5WLC+G0jQcIa5lkTcKPgWXDpWMPVN46FWcC5VUCM4Fw3Yg7t63AEVdu+C68cK'
        b'zgXXjxDMczeuJg5G8C6420nwLma4JZBxh+8IwbuQEPEs8y74Ji4UIN3lCM3MvcAB/LTgXnJyGd7DocKdeZestYJzWdNrXxpnkGRd8C6jRwnOJR86Bfc8TN7nWogRI75l'
        b'iZnZYvfFQwUz0cIzK7FgubDWRXw+R3AsuNJH8CvBxBsx43cb11uZW1ngyryKj2Au3eCSVXApgSOZSyFy3CZQsHoi0U7Bq8AVwnPqVkaGM8gy8Qkl8yq4USl4Fc9QAYR9'
        b'uH098yv4tIPgWIimnBPI0+6XyjwL3kGdFHEtJM66zKTljUB2gICeeSoj+P5MF8Qa/cNYo1NAbIbbnYBURCSRGXhiLKSCPuPrJqbP7guEnsY5IkGdibDfZAq9ZI3+2Q0G'
        b'B8vHRHK9m1atTpm20HuR962r79ZtbSl1Upx6boH3pNMyl2LVmeLSeHVmi8/+1OOzj08+dm92y7NPe0snLPGNaDnf2hz2E++6dq0qyFW1fc8HMyI8T18vuP/jy1M/OP78'
        b'lENHn3klctWgo+9GW7HLwZAP67crnIOU18Ty1/3/Js7q6e6cN86r5ceDu/gHP53reEH7pUp9JCVJ270yLMfrpR3vOX85ymWsTjfmq1jlcNNzIa8vG38wcOO+Q0dHNq0o'
        b'cfvTc61v+KxK0ZU9cyNtg37dxbeXfhXa+MwaU9lPU2Tusu3DhgXuz5rygjY4L+YNhwffOCVlD7tZ8Ubz83lzt13kfiip2njnxpVdup03Yl2uPNh3eVJUWsbCrvEZx2an'
        b'XfB97t3NU97y2731THGN9oeItlUvTfpgdUb6jKzy51+XuXx2cPJZ/GCF7vc1zZte+sPvb+B/FWw7c2Hn7Atfd7+6692kt14fZPrRLbTT4XLXjj1B7gHfrhg04urqdw+f'
        b'9Xpf+UlX/nPyvzUmPNu47IHRsOP7f96fmna8bvKVN0d0+l0dmlNiCfh0qvZS+pf/LEhqnxc49SdN4INpjS6DrJ0hm9oKKzNP7r7jVa2fcOBoz8y4txpqhr0p6/jkq65d'
        b'k8tsQ74Y/nbk++en1n4Qnrzv1LGVtU8b1csjn/3Xok/wT56bPrz2Ql2c1nsCLtRPvfTqjBETAqX61/Z+VhD37WqHDW8tm37/UvKnE1fqbPfXv9Le+K4sUNOasXfBjMkd'
        b'0sIpht2Bqw8d3eDbEXX+ysdfLlsw/CX3S2s8SwLf/HHf7SGJryzaWu7TcDBg1ud/DP/ocPT9v0VfOfj818bffMNvfeMr/3fWTjS8dWfE1M+qbBkjVv/1QZzDjNl3xvxF'
        b'0tXQ3fXHF3/Onrahc8m37z41wvR29Qhz4nvzPnnzgOPbr7423TA4Lef1yPDI9Skv5dReftVm8uqY2jHktcg/zC364QhfXvNTyvPbqz3e/djxUuhPMXrnTz/6eWfYyNv4'
        b'77dOvjb2b98pruRNMU+eKSm7fzV/3qx7GX+8Ok/3pf+1ZYFn82rl7tYRRBFi8Bl/KAtOIgkCVAaPnEtyINxIlfigkh2r6NyhPUihDA6ci/fLFWQICb+Rr0y8Bq6TYIaZ'
        b'yPNQbeo7c8EdkcKxi3Qpu1+/ssAQpCBZyA3iwYI5JMEVfEg4nLYyJ0Ri2quqMHw8OCCOOBPio8jWGxVubCI+h4uhSqVMxEdnBiY6IomYd/KH41aalRJ3Wa6nN9TJmiTS'
        b'3AeVInx8Pho8TQTH8AVosbLsrWr0JNXCEA7x+cSinSNx7gq28CKTT5BCDh3E15cGIwJREx+Bd81nEMG1UNwCZYnBYjilhArSG8lLR+JKRgp4GhqcVPSgTqWkGRUu9iXU'
        b'0vJwDHYvZ6RQhcPuIGhcFUgxpug6T+PxyWhotLJMtTED2lXEGZPwICQ+WOmwjngFL7gugiK8Z4nc89HDi//qRe787815eFjiJRyWWM1qo0UtnNWzM5M3EY0VpZwTJ+G8'
        b'OTfeiXPjpDz5RUJkJ86Lk3L0gMyJc2Ffb/LxJH97P+Q3LxV+8y6OEo7OduF8eC/eiUcc/Yh5MVnDk/MhPRLyGU5W92Et3mIx1/9DdxCzMeQ378V2FZOrNydle7vwnpwf'
        b'6yFf3oW0igl8buT/Es6X9JN2+pf0DCdfs1sv/nJRj1t/tPudAP171JRzZvdeerLln0K950O3R/Y/H6IH7fEpUBg0RyqcEIXKSVYflJSgECQ7SIIW0NsPVXNz5Jzgu65C'
        b'qbdqtFEZrCRpEKKJ/7l1A+640Z3ZjbF5iN1xozUC6JdVAlnufXfe+CfeeROxs0Hx17lkURdZv3/JVEYsMvXA4g1WEbIxTydLTJkaGSYzmdmPcMWAqQP+o7TKzDqrzWyk'
        b'axn0FitdIlNtXCdTazQmm9Eqs1jVVl2uzmi1yApy9JocmdqsI3PyzDoLadRpByyntshsFpvaINPqGQvVZr3OopDNMVhMMrXBIFsyP3mOLEuvM2gtbB3dBsJvDVmFjjEM'
        b'WIqd6gqjNCZjvs5MRtGaFZtRrzFpdQQus96YbfkV3OY8hGKjLIeARotlskwGg6mAzKQL2DQEdV3Mk5cIITTU6szpZl2WzqwzanQx9n1lAXNsWQT2bIvF3rdJ/sjMX84h'
        b'/MjISDIZdRkZsoC5uk227CdOpiygaD7cby5pMej01k3qHMOjo+28ejhYZTJaTUZbbq7O/OhY0pqpM/fHw0IBefzgTLVBTTBIN+XpjDGMnGSCMUtNCG9RG7SmgePtwOQK'
        b'sMzTafS5RBQIppRQjxuqsZkphTY+hGY51OeYbcbHjqblADHsSta0aXLIMAv5ny33SVBrDCaLrhfs+Ubt/wcgZ5pM63RaO8wD5GUZ0QerzshwkGXrMslq1v/duBhN1v8E'
        b'KvkmczaxL+Z1/0uxsdhy0zVmnVZvtTwOlyVUb2QLbFaLJseszyJoyUIFqyszGQ0b/0dxshsBvZFpKTUUMjtqOuPj0GJlFr+C1VydQW2xsun/fyDVP3iI6XNn/X1Rn73L'
        b'M1msjy5glwydRWPW59EpT7LclNc6feYTIKaey6ruFa7lxHORrQyGJ0iYfdOH4jhwryeL5r9Nd7OOeFGidDEyYmXIyMXQrVmXKWzwuPHUFhHk09fp+rGqFyBCAgN0Wyw6'
        b'w69NtRIH/wQi2tehIx4P7C88rspm1OqMj/eY9m2Jj3yMrx64MRnza2tk5w/0uwsot6E+y2ohliqLBDG0+3ET88yEAcTmqR+/b7K9W2cMSTIrngT9gL1/Affj/b9dEB6J'
        b'AQZMfmI8IMzVk60fP1E5d07Sk8Uu3WTWZ+uNVKR+aUMW2vsymUASBZbFmnW52oIn6nr/lf8TAi0M/zeNSY6aeJvHmrwFukzoJmr9GJvwPwAYVQOmZ9TODYArhfT8urIZ'
        b'1bm6h9bOHhfLApJI82Pl1GbOY3HRL2Ys05kLdEYtVctNBTrNusfNtujy1DH9A2uyQL+o/jEzVhqNq2NkS43rjKYC48OoW9s/D1BrtaShQG/NoUG63kyjVJ1Zr5Hptb8W'
        b'4ceQVFmdS80mgSkl55FS9oETY+x5TgzJCx7nGQaO7it1oDmfD3q01GGNUFAcbhGhPH9aYpERPNpqL2L4a5oDcnInc2ZnBE8OmIRs7HS+GTeRTxlum4wv4tIo2I+v4X30'
        b'yOYSLmeHLvwkWj6NpkOTAz6VDR3sbnA07HHCbTw9AmnA59A0LXSzPcI8JOhVWpsvywj+7cg5SDhCvID3wC17oXHyCKTBVwpYlTuULFIGCYntYtjVL7cd7e8wXMvL3Vm5'
        b'Ar4FO+OgLC4xQRmi8celrHxjnypEgvxTxVBPAD1hG8fu82+H41AWGq8MwaWh7DBiIxxk5xFoEpRLgjRwjh2EQAOcHB8Un+gKh3sPLOzHFSZoE84zCvF+Xf/yASTNg4NS'
        b'UTRUS4UliuAkFPWVCeBDuMxeJzAG3xZOW0rg9FQoE0594DI088gJbvAE/G6os42hNwAmQz3dQ0mQMUMXSfKhMjQOykXI30sMNVAcxspWeMXa3lGsUrQCSkIJwONw25Ag'
        b'h+m4LJndLIC6xfjygHGswCMpkUNy3A17TQ64ForzGdk3Bej6jSTDykKVZNy4YIcMh9lzRjOiE7Z24kNBCigna+GbWxTxiVASLJegEXBMjM/COdjHCi3g4ALotA9T8rGJ'
        b'UEoHDR0iDsOnCDEpAs5j4JCdy5nQ9QiXoR0OsHPDxAg4YwkJhNLQxQH0Hh6tTFlOb5iRv0uToVyMluOL+SGOuFqPDwsnElVBQRHhtIrkSBq0Iy00xguUP4RbvQh78YGV'
        b'j7CXFkWxs6JiIjR7IsId6KkWroOrKGd0HKtiXgKNk+GQI61irHVBYSN07FwsY23YI8IwYqMoesUKduqWOD6/Tw68cXNvuch13M72WrcJt0Xg1jwJ4giutxIQvpK9XTj3'
        b'rJw/hvQwyYXLUWidBuyi046vQ1ev7OArcKxXdvBZjp3fqLLXR0TkiRDnOUSF8GV8NEA4cWnBjbRQBpodyG7n4NxistaGBUKhQQ2cw5cjIsxkFlz1XYjw1cXQJZx+NkFX'
        b'KpnVSmbhK7h1GcIdsMteJpOXvDwigqOnc4kE1nVwMIcBb4TGsIgISsCzUO2BDPgWbmQWQDx9KEpRpFMLMF1qHI1stCYL7w9zs5BF5sNZNZoftpSN3DrZE9V4ziVbZBi+'
        b'jpEjuYjpniPen6fqPaHMhKt9h5SncI1w+nZqypR+p5zIY1mqr8gARR6CsTmo51TKYMIlsRi6p3P4pL8zk+gt9LCoV+6hKf9RfcMX/QVzs0+37rEKNx0uUYU7BLuYxm3B'
        b'ldD6RI3DZRFE45zxXkGb6hIHP1bl4AjUEaXDde6CSOyA23AkIoIK9clteD/KGTRWqGRcKkUjbdFELjMS6jPD6GkoNSG4CK7gQpUyJEmBu4KJ7gXYb3yjEbhIjM/NmWyv'
        b'QYgdTOt95CHKPNwiRs6OPK6YjFhfsiexY730uombCMHgOuxmor2Fy+7jhDvU9XJCCQeF8+Zi3GoOig9RhQQm0ceTPLIjoU2kc8NnhQeeLkHp5IeFZrsnEuQxpRC+LEYj'
        b'EsT4IH0qwzYesTqPK3hHv6I03AiHVAOq0hxUgm4cdcDdRLmhOv0R5YaDSaw4bSznJygrrgh9eCKNAjUFPg64UTVMKCw/QeS2TiWU7uF90fbqPbiZLFi1FnEILW/DRwmD'
        b'+krchPq2SXOEOrFyfNXjEauAOzxE0cPhpOBD6tXQ1WcZYqHLbhnwTnzVRg9Z8BF8k54rsHotWqwFbUvpweMNfNMWwKyUGV/poz/xJ5WhUJoAlWFDqQATeofjIxLlUA+m'
        b'3tPTuN6j+8gc+8l92hKBTe1TcO3DcrIxw4ViMvqAETMah/GhAHt5GhL7wYlEDp9Zb2KWIQI3h/SVKR7FF4Q6xdnzhadQLqQTk9pbUKl8Cjf3r6fcobIfy3tN6ROvpplU'
        b'uorimRoPgjp83S6Vq3GzXSoHw1XBuDfg3bjIlUQYS9bgU8Qu33JjRIuAp6MHiByux8UiHb4JgrnF5QG41JU+QQMN46aReAPOQjfTrVH4HJG+Q8QKhRA570IhY/EpQRYK'
        b'x2zoI/O82F4pnwFnhapqF2cUGUgQzshIaPfagAQj0bxxcZ+4bg34hWQX4N0CcffiNuikRSzEp+DKyXAApePC0cwv+ucGP15QOR0RVDFcY2Avw5W4CreFiejxfAguRKbk'
        b'YMabIDOtqPGQwjWodkRid0JCLiWEhDiLEKtQuDlpQAEKtQyVSVC+BIqVpD0USpLx/qG0GiVOKENZlIxbw5YsjgteNMDr4iZ3z4XbkhjLVsOu/IGWVzRYZBiHK4UiaGdX'
        b'1C0mvtwzw7A2ZQNKIQbdXjhyPlAlqAGHJBlD0/lAOCUVXE/7utCBK6rmiAyTTIzXKXgX3tvHmWWbejnjRUIs9pBkzaIlvaEHcfpX+wcfh/EeBtTvZrgh5BtF7FyGm/uI'
        b'DCTUr97cvN4+cSlueyS0wReW2ZaSQfm4zWYZQBpCF/oIoSIkgOhDoL2OcgklbHHwsjiqBkzLFv2ChLcX4J2bB+Fyx3Fs+yx8Gg4+VJzlw/rpDXThTibI2zJJhBdJwwZq'
        b'EhYRLx9HeMucxE44wdE+DnFDU4iLv5IUbKNVs/HEtNyEQ5gw+AAcJrF7cb8KrCsOuDVzsTUTX5vMqcxpsE+yAl/2ZrZjFjE5lRFR60lkEA2348mCREsvMO+v24IbIyJp'
        b'cc6R1UlINwyOC1rWDWcWRkTmEwhwacJsoq1uUCWU850cvZjABs20bqoErpFYopUgWyFIwhH5aNI5ifQRJ3gtlgY+RVBom0/6pCR0uUQkFsoIWcpCoXIJNLvjlshJyX3y'
        b'uThk2WI4A4WP0pdo0EkXqN0Ch5jpiJ1JQoVGCfX4NbgBbXHFx4UIqIILxI1RuIU+RtQNbT4ILrkLVoon/qYBN5JwZhu04XJyPYP3CeHE+W0L6dOQSEGmHEIKMqzvuayd'
        b'LoTYl0kfHI2EG4ggUAZdcp6pymBoyhko2BrYIzLkbmeSPRKXTOkTbLgAlb2iPXQ8I9RKfFZFC4g63GlNfufaIC4SX4SbzK1KjSse4xS4kf2dgt9cgd51G3CFUC5Ga8Xg'
        b'5lJuwnpoYABGQZW512NAhdLuMuQkxqKBBbGaF1RCXNE6/ZdxBS5dwOrRbdMQreW5NNQ1KRHKQ5bZNQRKlsfFL41LETiIG5KhODHEGTcpkhIWOhC/Ac0uuBDvgE57RQ63'
        b'EFfZY2RcGEdD5HFwlPFsKT4/oi9GroYdaB3h1C25hAXra5ynC1Fwmp5GweaZAmNaCBtO24Ng3DSNxsBEqE4L9vgWSWaLhSgYF0MdDYPHwSUhrqwmQlnbGwfvh50sDr4J'
        b'e4Xz1c6ZkfZAmIQOTSQSPge1DIzEgln2SBjv90MG43I7VrgWX9IJAJJIqY2C+NQIAYp2fBvv7I3Tr0E9hdESY6+Uw9ViKBRAXDCUArh+PaPFULwX6h+CV0rBcxhNJtEI'
        b'e3JsvhBg759LLreEDGPE2Bi7K4QTsJM6w+sLWGXUpSkOaMtcb3orIGFw2hpaGcXgOga7obvX7JSaqNWBA1sFbK4nGe1GJzOaGh1ohgtyMYNsPgnlqgUDshEfZQakFV8Q'
        b'yLZrGMk6BAuCm6AS6aBTzHoWJavtFqQbOqgJwR34DOuJ88VNvTbEhm9QExKl7j3mvrnZajch06zMgBxkJYaUEevh8hy7rlZakSJnOmPrJuILd/cpKvGm7VRTL0Mbo0R3'
        b'lBgFTPJklOgJjkL68+cuIMvrxNtuqHjLljKtcuR8z/v3j554fub9t7+orvxqlOTwszs83svwi3reUx38VcxvJPcNL1fEv9NzILazTVz0ZrnntN+PbZozpmbHCz3FvqN/'
        b'RmWf8XP3eE7iRnOjR6f/4d6ooPU57e+9lb58+dbVX9uW/zG16qN1X3Y079pT7TsktrL+6y8yvkz502ofW54lw3au/Iq2obR9ceyR1zNnHj73m88OpQ16e8qmTbbwSz2a'
        b'+X7TU/46tODDjw8srPnrhqjm0+UJcXPOlzrG+nywrOWA94QzVYt9J31TrlUdLf6P7bff23VmReeHqZu/u3XgjZNBc1q+WijDR7ze2TrPNPp7/wlzP8kP3PH7HbbwpS9m'
        b'lndN+B2fOmPwzuWdVdNctqkafvOzOfDvxd+GPJiJb3377r/4s1tjp+xco7Pe3jVl/Lhbi0t2jB88Z2LE0phvGqui213UQWm2fLk+989ffXf1q59ujvxarX0ffcNpvvWd'
        b'5nAvsnlI1o8iTSX6QrQ5wGL7cVfLgmfi/uSxY6bkzaCoi78N0Ee/smHekKFffD5z05ao5kn57oMnvT1+zBlI9J4x693mqb93GVNbE9tw6j86/u53b2LzH2VPvcdf8Fmb'
        b'F7PkNyfmJa40Jqz6j+PWy/kFKybmfprdoxiztcahY/fGf8m+/ccJvf+ma8d60vJa3n86YnZX0bZZkyM2DZ+4/Nmr51+82XWtdsvt8asKPv3is+crWlVRczsPJ1yw3nm5'
        b'/k5o2qcPnv2H2yt/OGb4eMfLc4f65X32vEIz/fnvdySdfvUdefvh74ak/Dh9+Y+mj0//5Nf0wYEp9dmqgJZ//mm2umO5w/miNU2tr3yafM/iWHp5yxtj/xrzpy5px9BT'
        b'R53eedCcHjDk6egHzX9fHPiO5UenV8rufPrcl16Rr8/54YjHR59OHP7HfwzaNuKlWeYfHrjc6zwVffud57aWf7b07u/8njqs+dh3MszQun47csXxa9Jx9W9+/p5OM+o2'
        b'TrujDVkT0z0j49iswrdyKxZ+N/zeF4Yv/zyjefPv9zz387zJbok5T//2hRd6Tv5U3Dmm/sWLJ9LvFL1/5g+qqaNabOfmfNiQJ/nry2HD1Oc/lyz46cFnR7RfzbesOL7g'
        b'8oW1X71Vs/wzzWfBf066FBMgecnh/UbbV0PvdbQpdT9t+eP6B+uPvJyZ8mDmt99+0+ijtN70SF/90Z+6vyuf8dO7yjemPH864odp5RPmOk9rfs3n/vXQmat/l1b8XZ33'
        b'/caYn8Mtd66UrcoNzalOP34j6cDH5Ufn+kv+MSH6i4+mpMw63/nPOt9X39v3fua9Ud2DN5ldhxXV5J6RPJPy2s2Xk+p+mjI5ddjWRRvGzF+9qPDBqkJL6rqUiKv/zHx/'
        b'wtg7Ec5XR/z8oPRmcEHzxzOutF6f8NG0n1Hd0eqCD9+Ve1hp3D2O+IP9QUIxFpRMI/GJ/XbiUNwhjpuOL7OCsASoiAoKVMiJ83OdjpDzCh6fg1tSq/AYyHziA8oSg4Vq'
        b'MIV3JC+FnfGsWCxl5cKg3kIvCbRBC61tw8VeQiXZ8QKoVQmFbXPS7KVtcNokVIK1k2xw38OyO528t+wO9uNLwpAd+JwqKC4YDon7VbkJJW6LFcKQq7gKallxnhyKFg0o'
        b'zmvbxqAwEQKUBiUlBseTUKt1M33Y4AZfoFxhZQb2VIIHyQ5KQ0kgL4GDTgW8YquYrcwTs96sIpD3Vfx5hOHjcFSUjUtwN1t5Jcn52x6G+hJcRGJ9G3SxTs9tcCmIEZTW'
        b'15WSTxMfMRnXCPWCLVAR2PsMf+RUB/sz/Pxc4TUOLXn0sfB9KhJf58GedHafkEdDpotFqVPkQ/5f18g9uX7L/b++zi/ePpBrnRoZxirpFtNyre3k4+XUr6pNyuranFgt'
        b'G0/+58ULVW0uPM89/uPERnjaa+lcOF+e/qUzaJWbN+/C9f8IK0mFuU9cU1hXysk4Ce/GVvcVeXJSVu0n5vzIfFpl58nLWBUdWdVeX+fEdvMRCVexAAPvxtPaPF+eVf2x'
        b'/cmXp1jRArgxPE/GiwXYGA0kvAurInThRnK+nA8ZP5xAIOZoFV8vPp68UG9If9GXLVC8JGR/swehalJvIZ+YHsr0K+D7r3NUzpk9e3nK9nqR8pI2oR2oc1z/sj526NGd'
        b'CXvs732AyhCa4iA0PEedJ4IbUD5pwNs2qDzMpquxXIy+nwml8VouTaTlhdfz9HiykyVWdWeebzabzN/7C2dNTLbM9iI6nVamNsp0tF+RJBf3OKWn08O59PQel/R04UVM'
        b'5Ldbevp6m9pg73FMT9eaNOnpgsA+vDA0abj1CYGOVYA68cJNvFOecN5VCp1WVziidqYYhpjtmhoKJyUOJLUqlHOx+s9rjjhY/MjsMmnSjMobSTDbc2/B00mZE/esSjqe'
        b't/dft0xz5zwvSvbs8j55Z148ZwzIaT63euxXko2pb+94Ne7sd9u31m7/8xubRxytlY/3mrrsKmx57nPnxrcq7/+w9s6diLoXvrlT+eys5U7iZ5OTu16Z8WL5Wy8GHN5Q'
        b'8sP+hZmvV48JHfycdNsYy7crEn4Ht91XKP/VdX7EgTMJ478Of7ZOsXaW+WL4se+Pqspj3Gvbnd50y3ljdL2qcuqfV2QcGH/48zYcuK6p7ZkJKw1toNh8z/Kb0Qve2DZh'
        b'6p/3LHk5+mTX0bOFh3tafrv02Oo/XJGOOemqyN32TGTiu+2Jz67J+3p8yOdflJ5o+aRJV61z7TonGhW79MoN5dM/XChQ13rsWilpyPBsnDc+fHDxgg8vfOB4L3Vr3mm5'
        b'WCh5rh2GC0kCcwzXJpBoOZrksbgZqplJ9ofylX2vv4FST3yq9/03cA3XWmkmFwrtvGsgTTOJsxCGhdJ3XiB/3CaGq3ifH1tJ5I8vWvAxHb4clxTSl+0Ngv0i3IzmEBFn'
        b'ku7132haJSyjfPKFmUwiuAaTWpuezuxlDNURH2qzIoldotXBtGrY08nTcYCFc7BbL9HI7ciZjKUWdrgbZx7aK9NEj3gi6A+NwqD/HhQ5s2+fBtHNae4kVP/eUzz6jp+p'
        b'm6AOl9G7ivSVYcTDVjoiKa7Ap4eJRsF+2KG/OmUnb9GSkVXnuFHPTZLuIlr02vasAndr5rm9d0934z27murGp9RuuXd5cvdfCgsvra+Iupx276/+62796yD+uWBJan1t'
        b'+rnPr/+lYfyeA3LrP44Pu3531Y31EyeFf1VT9MKiW6vb3j/xl0/9K8N9pfHJckcrtV0u+CScZO+qWUjr+qEQzqsciatu5eEilBkEX32VvoRGle25MARa6MiFITwRpG4R'
        b'Pq1XsVWGLoLdAmr0pjMuZ6hB3RwvkR/ej0+yMITkqq1wWKVMDExda6/zT9Fa2X31RnwlT9X7ZrSKMfSmh6ucJzTZbWQD8Bn69F/vu9PwqZl9r05LyLKyezrXcD3cCIon'
        b'ebQK+c2FGjne3yvhfv9jscS/JzriX9UJvVFvtesERRC5O3GCv3QSBW9nEcVS87A+aZf1iAw6Y4+YVmT3OFhteQZdj5iWHhDnqNeQK62q7RFZrOYeh8yNVp2lR0wLs3pE'
        b'eqO1x4G9LKnHwaw2ZpPZemOezdoj0uSYe0Qms7ZHkqU3WHXkP7nqvB7RJn1ej4PaotHre0Q5ug1kCFneRW/RGy1WWorZI8mzZRr0mh5HtUajy7NaetzYhuFC6UePuxAh'
        b'6S2m6KiwST2ulhx9ljWd+bEed5tRk6PWE9+Wrtug6XFOT7cQX5dHPJfEZrRZdNqH+iyg7WemLwowT6KXYHphh/A0IzDT0gQzPdQzU1toltMLLSkw05NpM73rZqZ3/c2h'
        b'9ELPDMxU0s2B9ELfMGemYm2mhzZmeiPWTN+5YKY+0UzfnmCm+mymommmN//Mk+llCr0E9ZkDyh3nPnPwXWw/c8D6vnfqfRVZj2d6uv233RZ+Pzxr4CsWZUaTVUb7dNok'
        b'uZOZmhnqztUGA7FyTA7ofaYeF8IEs9VCq1t6JAaTRm0g9F9sM1r1uToWS5in9hLvEf/f4zRdiBpm0v+x6ETMExUVZE3nTa0t938ABSTMiA=='
    ))))
