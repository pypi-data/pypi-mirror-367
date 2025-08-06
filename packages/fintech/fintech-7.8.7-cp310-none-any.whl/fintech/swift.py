
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
        b'eJzVfAdYU9m66No7hRK6SBHU2AkhgIKIKA52OiqIXQgQIBICZCeAFRU1VLGDYqfYAGmCCoqzltPnOMWZo8M0z5x5c+45OmeccZplxrfW2kFRcd457757v/vkyzZZ9e//'
        b'v9b/J38Fz/0T4FcIfnFT8SMFLAVpYCmTwqSwW8BSViU4KkwRHGN0DilClagQ5ALOeRmrEqeICpnNjMpMxRYyDEgRxwKLVJnZA5Vl7KKwOXHSzKwUg0YlzUqV6tNV0nmr'
        b'9elZWukctVavSk6XZiuTM5RpKm9Ly7h0Ndc3NkWVqtaqOGmqQZusV2dpOak+Cw/VcSqpaU0Vx+FpnLdl8tB+4Evxaxh+SQgKWvwwAiNjZI0Co9AoMoqNZkZzo4XR0igx'
        b'WhmtjTZGW6Od0d7oYBxkdDQONjoZnY0uRlfjEKOb0d04NHUYRdx8/bAiUAjWD19jsW5YIVgE1g0vBAzYMGzD8Nh+7/OAxRaZIDq5PzUZ/LLHr0EEHCGlaCyQmUdrzPH7'
        b'Uh8W4DbpKkFi5NnM6cAwEjfCFgd/VIqKYyLnoyJ7HSqPkaHysIXzFGIwbrYQ9aRayRjDEDzQHJ3w48KiXslH21FZFCpjgGUYC5uVcFMy8xw/HfogiCcEYTBJ/g8ESXUw'
        b'Ic4UCTDiLEacoYizFFlmAxvb7z1GPO1fQ3w+j3hhghhYARC6R5oY6SAKALTxP+YICDXmFVklWi1fG8435kVbADsAAluTEjWdM+R84woHIcD/h9wISbSKnWUAp4DGEjd/'
        b'7eUi/NHBQ20L/jLuB7Zj/C/LLzIaC9yxRLefaTY7P4sNSZzw2YRlgR8D2uy66AfbPbbTC8zn3WJ+X+w3JhH0AoM37nBE5egM5kGpz3wPD1TiE6pAJfBUnEd4FKqYho56'
        b'eYcpwqMYoLW1CIZnR75AbbM+tAMJtQmlQargCT2Zf4me6QPR88nCT+gp4el53scGuAs/FwLfRK+lcUt5LIZGwUqMRJk8ApWh4sj5oWFeYQvBhIhY1D1nMNwTB0vhXpAm'
        b'MkNHYBdsMwzGUyJRKbzkBzuF5mg7lsRTIGc1OmYgW0rnAz/YLpTNxM2HQAY6geoNRKpcUfdIvwlA5Yjb94FkKTxAh8NjPrAD7RYBMB+1ewNvDayigH6rkABHq6UiYJeo'
        b'qV/rwbNzqcgBjF58XwxAort8vBaod98uYzkl7rGyWXg78T8SV6VGKt9N9f5KpgxV/iPRITk9VZN0JzFceS1V5hCulNlFKxtVJ5nTg9L+IyVcuQzsSg5VZql2CUvqmk/4'
        b'zlhSJnOXxgfdm/F6dL3NnB0XXrU6+Hcw56PB1/7WPLJexuqJ8bBHR1GdBNNpepYsyqDwxDxnwWBoFJr7ohK9Kx4R6IuJWIpKUAUqw2I6mZkmgS2oCjbJmF7WQyYT6AhP'
        b'+j1Y/HjgNDVVl7VGpZWm8rbOm8tTp+qn9VpSQ5aQotSryDjOiuA60oqxY8wZD/zSifuWkAl6RblKjUHVa5aQoDNoExJ6JQkJyRqVUmvITkh4YV8ZoyNSohORB1llFFkf'
        b'cwfYfSlmWUbMkKeQEf9OngY33DFCESgP9fKMhuUxWELQbrEIOKFNQtd18PScZLafCAoHkG1sTZ7INktthQDLNktlW0Dlmd0giO33fiDZ7lv8WdkWR1MJm4Sqx6DdWPwV'
        b'QAQ3KtChRVTC0IVYWI92Y33zwe0HfKJgER2+FJ2xpILnDeCRSG/YMFYtvW0n4IhGKFZeu33bIXHplR2wCrbvOLX7VGFL0bitFwrDDjJvphI5s0q9FWkG9p0yd972uYzR'
        b'E/LALtSTJodH0M5wBSoKi4wWAcx6Fh1KnWXi0ECspwzolfB8TtVkKfWU0UTcrTyFmMWYyZZPmCykTOsVpaiS1HodGaQjBkrG9mMsqyMurR93yXT5E+7eGIC7xA++Msy8'
        b'j7tYuU8sxY7FiwFumUK4czo8RPWvM2gQ488CD2nom5k3R6JIA1nQMhVWcfpZkQG+QsAmAVSPDSEdrXd2ZAJZ4DIv7UrmzcnJi6nhgPuGoXOcfuyoAF8GsCqATk2EF+nw'
        b'yxbOzFQWBNolXMtcvOG4C13cHhb5cXrUHhfgKwBsGkBn1i+io2+GujIhmCRHHb9Y7xL8apDBibB6G9a7XZw+TDyJAKMF6DQ6s4r3BPIhzCwWSJvVV9a7jHUwp6vHrYQV'
        b'ePVDSyf5soDNwqvPsuFBH+rOhLLArnnlx+sXxw22M7gQ0Gvmw3McakftsokEeFgIUBuqG0pnjBs9jIlkga+d3evrXcLmzjU4E3g2YsU/jqesdZvoK8IztgDUHriUTng/'
        b'V8rMY4F5iNv76xdvuOLOTzgwExk5HWpzpTtgiBrgYRPx5xeMZOII8Sf1rr+Z++pgHuPaiQLUZkAbDeMJxthOo7Zh7nT8haTRzGJMfrupn62vEp1LpBvATlQYhSc4LBlP'
        b'UMaWGLUPRXV0wrtTxzLLMQOuKD9cv3hMqJhuAA8VoH0cB5um+5ENCgBqskZ76fiWaR5MImHB5Ne4qrjPPej4NSMc8fKwGm4fTzgGDwB0fmoQHb8v3xOrPwgJWfwF56IR'
        b'exiIuUQt+bAEzwhGheN9zfCEaqyw8ChsolNeXaRg0jHX3o+/wVUt7YqjXPP0SUJt3DJUZmWJUUDnGP+Zc+hoR403o2FBol38G5xL4lwnivEYtHWtRAd3O1P5hPUAdaJj'
        b'qJFOiMoez2RjNkvd3uIWq8fF0Anjp6KtEtQCW2H9RDIFx0sCCdpDJ7wX7Mdg/Zy3cf5HXFWmVkhRXoWMsFtiiY7DvRMI19A+xkKRQLusxqBKCepALeGUPWgrw+CPVBE2'
        b'WNtxqC0a5NkQJI4xcliDPSUBYAiqd+IsYAM8ao2ayXo9TIA76uJxX4OOSHJGFxhQB8A9LcyYlYDXK6PnIE4SCPfq9GRKFTMMtvlQsR2EdqImTg8v4FilU0I6yxm5OSyh'
        b'01AN7BzE2ajReWtMTIGICYYbl1CzGbUun7OJ0FjbMEBgwYTAatRIIdgQ78vZoMbV1jkEofOMtwOs5SWlFB5bI7GG25ExG5YJgWAUE5KaRddaPXc+pxtuR3UgG6BGaJRT'
        b'0NBedAluw7DtRkUB/mLApmJ7ADet5tVtyyJ0muNQudSP6g7WtlbYA3fQTjU8peRQC9q3BrXZEgI2Mf6oGZ2jBJwkxEYAdUzEsQffeZrxQ9udZLaUh+YCfyYfa2qI7k3O'
        b'ZdiHfGSxwG0Ss44F2c2+n3I3Dc3+tLE9cjKzEavoraQbnIt31XLamJsexGxhQeiOVW9zLqvvamnj1zODmSKsm76q1zgX8TdOtHEvN40pY0H6rRFvczfdVgbQxnvJ05kd'
        b'WCuPJn6OleZXDW08LpnJ7GHBYt/gt3GjcSZttHCdxVQRdfR8n3MZ3TiDNm7Jn8McZEH+3ejPuKpx4VLaWJ8Zxhwliih/NcMlqXc+bXxrQyRzEqsOsIMZLpE719LG+IBo'
        b'pgFryF3FlYyqaf5zaSPjM59pxlqQOO+DDBfRoFTaaJYYy7RjSb/l9HmGi9/yBMr72R7oMidBPVGWRCqssFRUDuV534D51iXR2cEeG2ssR/ZMcCQ6Tjllgy6hRmwnO33M'
        b'8zgBlWY53AoreAHYDg/AOqwH0jnYShLZ3MOMdEANMiEFYon8DeagAOTbjUd5LjN/4kmgjn+TOYq9+V1bmFX1Srsvbdzh8Q5TKwAhzeLXsm4GLOKx/Sz3XeakAEgTzT/J'
        b'qopdnPBC/G3RF0rMAqDv8Pf0pANSLZ7E4sL/u1jczvR6Nl4JjjYMx++d0WElLI3Bh7KKdGyUisOivFExDiedEoXj4DYfisLrU+nBD/impuVEucp4YZUEmJNVfX1zS0P3'
        b'j7cBvGUvhkfN3ZdH+ESg7TFhInzo28KuDl9CjawXtngHYBtsh+1qdFwImCWEY8dRDWWCeQEqlHvgWLbIJ1qEOuOAVZrAFp4bbLCnDmb5WnSSgW0YiiAQtLxARwhHwXCz'
        b'E5HDldR37C/rdvhzQEMijuE48MNBqp1v/I6paXlUalDD3Nl+vhjColcA3AWUqBruNIzGHUF61BJBI+UKcjKNgBU+YbDRA16OYYBUL7LBgXQbDdXGWcMKP3+8UvkkAPeA'
        b'JP9xNGJJhxez5TjaoIdafAYLg7XeQjBIJsCfaq34vTdvQM342AHGwiJ67oBFY3nrch6b+DY/2CoEqBDuxiEg0KBi2MB71Ut56KKfH36zDx4F8DBIQ+WwiZqy+Smoy89P'
        b'DFCxBp9dwKoROJok7aGo0uAXAEAaPAdgFUixRkcM7mSfc9N9sIxXRIQTEKN53thkCwK1sJPfqxqegI1+ARiOzTkA7gcq7PM3GchhYxo6A/dEROJJPqhczqBaeAFIlmJb'
        b'hypRpYylpFHZePgFsMAZtgDsa1MZTFqK9w4fVOcXIAawYw3APjUN1azn/W0nbPJDpRGEZq3wgAgIhzHw+FrET8NWvgXTK4DBwKwA8CBId82hoX8ALIQn5IQ7qDgaNgrD'
        b'4U5gFSywHYXK+cClHNbDY34QeyVfeBFgqmnwWfEQ37cL7vdApZGYAstGC4AAXWZgdfZQQxTp25I9mosMC4uaj4qeHkA9vGWeUd4yBWsJ61Q4eK+HtR4e8JQTbIySy+Ae'
        b'VCt3hHucBqNaZ3iCBbDE0Q5HDKcTNL8+fvz4y0EmqUytnLh6yhreO0rRJRt5tCIU1qFyIRCGMPD0unSZI+85m93Rec5aZ8gGxDwdZkah9mxKK3hyPKpBbTY6A7ZglaSz'
        b'g5GhVrSLV7gKeBwHeG14pl0A6bzMyJfDi3TNaUNRM4fnLYAbeaM2HHUyvMU7nQ27uRyDJepG1SSI7GKk8DQ8Qy9q0OVZsBZ7rjzUDntQl4gGHyPgIbSZiko8FtpO1IZ7'
        b'rbOXMtT9Twh1o8BYKWC7xEYCK3B4ehYb4KXMMliK9tC+MByAbOf0lnlwy3oSAl1i3FEh6ubl5GjkatKFWmeR3TYx0mQxD+cm1DIftel1qH0WvEwiucuMGzrkyMvsxoQA'
        b'DrXqUdtEMWCwfqAKeGoU7wlqMb9qJObWlqgDnyoFk5hQtCmCEmXGCNiGFTrHyhZRqhxgxo2RU+WJtsqS2FhZeJGgRjCFCYPt603QzbHGLlxnM3E2xsmGmYQujuVp34HP'
        b'1O24C7VarwvHfSOZ6Sp0gm7jhLbZczk5VvNxtIXB7mCGrUJNtCcgEFVzljoDPg8Sfu1ipKh8GAVAvg4elOCeIFSOBdSB8V2tp9oFS0b5okOD8VEXG1HgtQqrCUFyLTxh'
        b'gKW2ltajc3IZIMTBBywPTeJJ07MaHibIoCPWJmS2wWralZ7hzAvTXlTaJ0yNHrzenRm0iEA2yakPsAYrHtEmDfadRMZga7pJyDxgMU+d/eYjiZCNRKdMQrZonUxIpy1B'
        b'9Tjqo9wLRTUm7pkbKBgq2LyCMA+eTeljHirKocYKbQz2x2LTycFzsBm1G7B1gBcZuAm78CYqoPDMbBEszUMd8PIUK1iMVQkVMXA/2jYPe75ourw1qkVVVBQTUZVJEi9n'
        b'UIBd0NaFRNiCR5lkDW615qNas6lUCHezJvmElbkyG16etqJLjhJLC6x2+7GWCYKYuQocA9KuHWiLJyHA5CkCGnWPQJthI+X0CFgHS4hO28DtJqXO9OH5cyQRh+TmOoMn'
        b'2oqXs2S8YRXazdP6zAysam1WmNY1kwQ0phwXhg7w6tDuBbGuG6x0PvAg6atjxqFDaBNd0xc7AxwTd+iDUSvhxBFm9BxUy8/bnYFasEZLLDTwEonYW5kAeBZtMUlqZbJE'
        b'h86hc6JBQspb7/RxVO4410yiQkp4kleh1YCK6fIUIEHnLHK4aWIgGMdMlkL+LIFK4LYY2oOMtjgy82CC7H0oThZY+uo4WJ6NWVbkDihSsuRw2peJzjpi0LJtPVAzjr1R'
        b'MTMW7oGVBnJVAPehWifNGiwMu2FFLtoDy2EJbAyAp7DwVqLdaN8iBoxaKRychTWBymILdhBd2ENtQ7txGOALfLnRhhjScWEBPIknYI8Fi55baA+qdHBGO/AWrbh/D2zG'
        b'p9O9+HMlNFrgk3slOgnPpK/CBh4fCC2wlF3CzHCkEnxwAaXpMKmJpCkpFKNxsDmPJyiqsTBR1AHtxa6SGvqdUnSOUmku3MQTcBnH9zTm4+iV9GAvw9PPV2+YT8A/DHtU'
        b'ElQegT1faJQ39VNyVL7aJSpcsQAVxcR6eEeFY9+GysNk8aE4BlmATyHt3CLADSbXpo2OfdendnCvgxVqWEUFxoDKnHntRB2uJu0c60U1bCbcGktVcJxXPwXEcnmBYrg4'
        b'E+6hPFsMO008w/p2GmNIb6B2RGIPUA23RngrPMMJ1E1CYBsv0KwYRvttnOGuKHiBeNlyGlLgKLGKhXuhUUsdngAdTMfhY6hXeIxCDDvCgSQC6w6sWkvJPhc1xhJ180AV'
        b'Jn0bl0njMHgYldjKw6MiFGTPaNTlIgIO8LAAM3Qz7FZ/lDKE4brw+eStE8dXxAXHDJ7ueMmv7eEXn/5SfPzK8aNFHiUjPYqGv/f6+0fHO3W8//nG1EHvrnXRpCZ9VZqT'
        b'/JPnoEElKxzkbsuSxxzquXLtSMh01d/3f7LJ47V37xzk3vv84bnq+H2nfG4Mc/3w6sixo+7c39ie6DooIv67bFbSq62Q1RzsqN82NPDHqnM+59T3jGmiSu6DS9/9VPLW'
        b'33MevvGzZNGEU7O97wa8apn1miJ26Teba2Yo96uWPkzfs822KcjrCvfxvXCz5REpeSvk+Y2dp+45hgrejDD6B38YDv+ZcVBQfHNN4T3hP7/LORwpjL5aWPWXSc7Hm4dv'
        b'MV6+l/322kDrr3fP3DZ1QnfU5++dr3C//nrzowMjvzr8J/1Hy44wD/709/ecihoT894bGdQcOiR1RMXfE4saxikMvpFLrT91X7Hu8y9fe+uvI47tW1XsODnmjeMFyin6'
        b'pqh1X2yJrI+7e/KrMtltXfxXxcsbPAe5WLzX6nNRsPRC8Pt/CRicd3tEbs7fr+wJMrsoXPduzZhffm8teLzpT+Pr4wK/Xe5Z0lXttPieSB/0c8CHnzQ4RsZ/89byH1/7'
        b'c7hnhXqsfXBmUY3BPsPytsOf/5d1y/SplzJ+kXeJCgZ3fe3aOXxV07f+O3sO+VYWeLeGR9fv2tdWdPZ2uPfD1odb0gyiwU13rQdtOvWPNyfUnz5z8sbhM7smTByaqtLb'
        b'rXz14+shN9ZCf31hzeiQaQ9vfeOw7K3vlqosp7ktH3ps+YNTQ/Pazua7T76Rv69meW+TNjpk0nf6Vyr084996i7Mu77wtvP53oLlixf/tWt+0WvRS0a1DP0spjhr+qTS'
        b'g+Mlt3VFa75q/LWz+uw/AnK/DujxjLrerpcsrJr2dcsBY/D7ih8vvyYpbrx+8rt3NieP71n/wX1B7gctK98rHe+Z0mP2ntm6T7+33dn1uLB2zNSHPdNj7n64/dtrQ9Me'
        b'Mz/nHfot2fn7S+y3R2ve81jzu/PpiuHXTihk1nrqIM/GkDDeKxpHqajCi7FFpUACz2CrOneZnqivj2GW3DvMa9kcT5k3HoCKsdeTCleiLcNpN6p+BXsNU3YAllrSBAFs'
        b'CYfNtFuPtmHz4o2K4CZrVOzFADHczirgebifphZ8I7AV3w+PRXh5hGJFw9qLt16Nuj31RD0XofNwV0RY1LQlnlFmQCxkzX3t9UQ9s+DuJHKzi1dExRj8ilxYKACDpghQ'
        b'dShq0NMszOlZqD0iRjFpPfZfucx0HL3oiaEKFA+Re8sWwxpU4gUwNA2sHzy9Wk+j+hM6fGgrjfJyRrvCSBJI7M/aTImmN+E4Di6OIBmliDAS0DPLUA+QpLCoOmEhRQRt'
        b'lcjT0E65J0aV4mkxhYVHRqBDFF47Yv8isHlC5VGKcK+wmegCtifovAAZh6MDMrvnb9H/sw+Zxb835+mtvQN/a6/XKbWckk8+08v7W/hhOcOcETOOjBVjzloyNowjfloK'
        b'zBkHxhy34VbGkr7s6F/fJ3P63oY1fWbFZiwjfmyFPzsxdqw5K2SEYpL9ccIriOn67EYbxom1wW2OjFCI+5/8kf6+J/7/Bwc7G7ymEM+0YWzobnh3dhh+OrD0hVchvWQ/'
        b'O1bMuOAeR9LLCDfisbjX5ndLIcZqI9gkfKCz6qOFTNBr1Z8E/dIS/x5lZYzOuo+2dPmZwJS0cO8ZIGnhQUIB1JknD0Vlo2jiwkeGz5jy6EhvXs7lYjAXNpjBPdJVMoaP'
        b's5vgxsURYTZyrzAcu+Lot/qViS/cChEY6IVNJKC3QiT/DV7MgKdaP7kdYv/VzPdPmXhxS2m/f/OIBHFS5bO1CrQAYnW2ShoVN9nfV5qlo28meD8z9ZkPYXqpTqU36LRk'
        b'LY2a05MlkpTaDKkyOTnLoNVLOb1Sr8pUafWcNC9dnZwuVepUeE62TsXhRlXKM8spOamBMyg10hQ1ZapSp1Zx3tLpGi5LqtRopLGz502XpqpVmhSOrqPKxxKQjFchYzTP'
        b'LEWTkvyo5CxtrkqHR5ESDYNWnZyVosJw6dTaNO4PcJv+FIrV0nQMGqkNSc3SaLLy8EyygCEZo64KevkSCkzDFJUuQadKVelU2mRVkGlfqcd0QyqGPY3jTH1rZM/NfHEO'
        b'5kdiYnSWVpWYKPWYoVpjSHvpZMICgubT/WbgFo1KrV+jTNc8P9rEq6eDI7K0+iytITNTpXt+LG5NUun648ERQAYenKTUKDEGCVnZKm0QJSeeoE1VYsJzSk1K1rPjTcBk'
        b'8rDMUiWrM7EoYEwJoQYammzQEQqtfgrNIlSbrjNoBxxNstlB9InXNCSn42Ec/mTIfBnUyZosTtUH9mxtyv8HICdlZWWoUkwwPyMv8Vgf9CotxUGapkrCq+n/Z+OizdL/'
        b'C6jkZunSsH3RZfwPxYYzZCYk61Qpaj03EC6xRG+kcw16Ljldp07FaEl9eKsrzdJqVv+34mQyAmot1VJiKKQm1FTagdCi1QB/gNUMlUbJ6en0/z+Q6h9OBD1xZ/190RN7'
        b'l53F6Z9fwCQZKi5Zp84mU15muQmvVeqkl0BMPJde2Sdci7DnwltpNC+RMNOmT8Xx2b1eLpr/Nt11KuxFsdIFSbGVwSMXoO7kjCR+g4HGE1uEkU/IUPVjVR9AmAQa1M1x'
        b'Ks0fTdVjB/8SIprWISMGBvYFjxth0KaotAN7TNO22EcO4Kuf3RiP+aM10nKf9btzCbdRbaqew5YqFQcxpHugidk6zABs85QD7zvP1K3SKqJ13i+D/pm9X4B7YP9vEoTn'
        b'YoBnJr80HuDnqvHWA08MmzE9+uVil5ClU6eptUSkXrQhMaa+JCqQWIGlc3SqzJS8l+p6/5X/BYHmh/+bxiRdib3NgCZvrioJdWO1HsAm/DcARtSA6hmxc8/AFYd7/ljZ'
        b'tMpM1VNrZ4qLpR7RuHlAOTXosmlc9MKMeJUuT6VNIWq5Jk+VnDHQbE6VrQzqH1jjBfpF9QPMWKbVrgiSLtRmaLPytE+j7pT+5wBlSgpuyFPr00mQrtaRKFWlUydL1Sl/'
        b'FOEH4YO0MpOYTQxTXPpzldvPTgwynXOC8LlgIM/w7Ohn0vHkrtcWPJ+Oj+NLYzdxtKoYHA3Ij9wXreVz3N9qaQGxFLzCae6FaIDBj1xfXIQt+K8UtsGSgGi0Ee2A52AZ'
        b'udU+DcvpHTc7HjXCRjAVNYjgUdgBz/K1riXoLDoL22ZZ4mPzFDAFFgbSTW6P5HPmR4VKr2PiLEBTAAHzMkjeehispnlrtNPHMAI3zyqAXfK+Yy7cjtqeHHVHDBcNQcYw'
        b'mbWBVHKuQQ0pqDQ0KjJMgbetwODtJyMjFGIwfLEQ1SrgbjpuFiwJRKU+4WSYTzi8lNJ3iysC41G5WI4ur6S5aHRaFf30ilcEYAcq4u94g/BK5G5s5jC0o1+WG7YP4hPd'
        b'qAGV02tiVAi3wYN9+Wx4Ee6SM6Z8dhEs5bPl25PhKVRKbn7CFSyAJ9Bmc3SBhSWwPoWC6w83w0NklzCMCz7xw2pYjSp8QknebriDEFVpVJRMa0es6DeK1FgU+2CopXmj'
        b'5aKpcA8GeQzNCKBW32fG0WKE6CgG5OTKYLcIHtCPprX262ErutBvJB5W6hOGx9mbjU4UheShEoOULLh5ECyUe8O9mEp4Oe/wKFTsJRMDN1QthDUx4ZQO06bCc3JvOiAs'
        b'CpWQfhmsdx4s9EVH0H66jiVszn3K5cqsZ5gMdy6iZdtKeNSNoyXICzzI9R4poVhELtRQGbykiFg4j+S6FynM4F7cUMzXwpZhlDv9JgjBAj8AK0HKgqWUu7ASXmL7szcH'
        b'GnnuSuFlOtMR7o/3myAiZSanSUFB+thZVExRiznecneoJ5/1gfuW8Lzuwmw/018cDsA2Xh5WobP8nltRJWrrEwdUOr9PGrBanZexNFGyAqtatR9szRYDJhLAS9AImxL4'
        b'at9RztNxB16mfgyp0MgYF0MTbstGky37BGjuAl58CjQyMX8BtNnN1c8vWwCYCIBaF8PGSNhCU0B+cAtq9fNDzSLALAB5o2E7rJdQzNdHoBN+fjo8JQZkZ8Ozs+BFupT0'
        b'FSEe34rHx2N0YSvsmDbTVEQB25DRz48Bg9EpAI+DDHeW79iKygL9/EQAFS0GsAZoUPkEagDcZc7ACxuA9+NU7h8yM3kDAA8uRBVcLGxmAJgNZnOQr6o1LrEnX10JDLHL'
        b'sjILMwMyAU3tDAlBW/rldeBhVMjndoYI+NKCEh069jQthMoAnxkaPJ2CNsgRFkeEeYWJQEKQUMjAIyq4y5Q20+cQ/HmSwUq0CzYOgj18LnUPOorOPiGaAm2G7aPWUT3F'
        b'5sHo3E9fXODFZ9QUbs6XmYjSNDSsj7yoSAbPeqFOmuoSwQs5TwiMje1mvGYzqqfqPTJYPJB6wyrURhR8hisvm925kYQNOthN2eCiNYzDzSG58OLASu8G9/Naj6pM9RHw'
        b'MAPrCMvEQ3mONaMztHYJnZ+Otg9kEFCJObEImE7VdIV8rNRYGIQAnhKQKqP0EWg71XF5GFaQME24ItobGwEPXsUFGAajENbloxq+dmaHRw6pipEpwvAKF90szFi4fbSY'
        b'SsJBuS3ARtPlrme+Zo5AAvi6piK8zHaelegwOkWZaQ4rqHnVyuGJ/kJyAu7khQRdWs1LSeUrBfJwRYTCMxqVZcH9DLBNE6iIr6NIz1o6ndRrHUS7+9VsYdLBRiFwixTC'
        b'XWh/Oh0IMQw5z5Z2TYCXaXUXQ0u74PlpVE5YdAhu4c0E3O7TzwDFx3kmi+AZaPTny5b2BsG9T2rbYAXspPVtboA3uz1wNyx/phQMU+vETL4UbIs9xU2HTdAuvgxJANAF'
        b'VMwXIjGwy+BJrPIE7Jv6aAOLUYUnqvdBJZEkUxNBvjM1AVaKw1Al3Ej1zX86rDGlSvGkC9it8rnS49gT0EzRRVQHd/ZVTKHSJEIjUjEFj9nLeJVcjoX6HF+KhXlVhU7S'
        b'Uixs4vbyKG+PgkdNdXmonXybgNTloQMRFGW03xNVm6oHn5YOwro5pHoQHXIykDgnP3O5BG3U4GgjFsQmhWKNI8WI61kzTtVnVqQmQZet8pHoxAD1jAbEaO1DZ1AtHT0t'
        b'xxnt9qXDFUCxeiQVPdkCvgJRmpIVaWTEgDcHZ1EJNJJcvxlAnWLMJZCQFUjFOA/2oDbY5osJj+MGAE+CLOz/eniJvVCAjqHdtjboHNprhg1xC5bZuJDhhgVkzVZ4Fhmf'
        b'ScATTamIRuWxqCgMt/ug4nkkER/KZ+Hnz4OtvrELQr3m854wAe0zeULYYG0XE+zLZ6xrcAyw86k5xMHITt4eonp4kqI40ksCMGHMm8M2WHm6xIA4zDUK7ik/1BFhKsnD'
        b'QpYmTmA9rVAZrz870YXgfla2Kp1fdfZCKjQSeFnUT/9Qo8ykfnv1vEvcEQ+eiwzM0HkaGRzji18fBFsDDIWH3dDcyAkrvXnxd0R1TnLv+UMGijmwOPUYFlEHAGtRLfcM'
        b'lTCJyDfXvBUeWMY8TUV4sYTARV7xoUS0qADPf0LNPlJ2S2HPWntYPoSlNXc9Ej5KvjtX5XU7fx4PlSc8r3hBQFHFICqgjU9cPOwYgiPmNn/i4ucD2IL9f+PSMCo10kx0'
        b'ifQwxLugdhw9NmG3vNfgT6btm2aJdkMsAjvRPrxA/9qSJhFsTfJFRxfok+C5iQymuHgJFiO+4h12DsO+um9VeHEGbIqzoI4+DV0c9wQQn0mwMTNDJuSLPtlkv4Ac7KLC'
        b'AarBvr4pSsFXvWxHdajezx/rzcUhJJ5SxczlC3Ka0qHRzz8X7xECorFfPIVK0nl0sTEowbugZkD8mmUqBhXulTG8tT+C4/lu3Dsed87BSrQC+/HuQMMM3Jc9O0hCwiSS'
        b'dPVBFbGo2Rq2+I+f90TuFyjiFzzPKGxVj1iifavRAbhlGVXncEd3eGY13CUGYB1Y5zecAuXpikE8EwBbWMA6gcl4k9MRcD9fug9rUA88MwyViQDYADbAQ0NMlafoKKzO'
        b'Rrv9LehXqLynmIqaYFdYJmZMowikpWIrBeAZdNAfTyEmTYqOze2nHcdX89rBxVPtkKFjuv7eqQWe4tVjtC9fS2UMxla1LQ91WDNA7MGiTsYfncf2i5AuSUDqyDuybTEv'
        b'jAa+mKkOttJqZcMU/BgDt22QREehckW8SexR8aLQ8IWhcTwlYRHshqewKYlSeEdHxojI4aPZEm6FDZbqdxeeEHEf46U+zotZvzCiwm22XdM/Dy95L19zNu/bP71ul5h3'
        b'b7TtSrfF5mjtpisO5sKt73wTD0u8ltxxUbAGSbH9h1t2zw8cIVm9Y+T3owJz3tyfPSN7xle22X9598bEL8bYjxhy4eKD6gOnz57p0Tqnho9Z4bded/VrxznlHzTrpisD'
        b'1JqmgzqlfW/zvAvXbAb3brugq4pZGOYi+PM7X7Nu27d/116acvqTm80fJR/6yT45MPHdjvJqbqLzJ0Pes9Z3ZC7MvVzU+NXSCl3dmx/6N5/+8XCH/fWCI9Ny/NXxj15f'
        b'47Jk4lebAzteZVJ+nTGCG7rf6JQVGKZu2FYgyABdr0e5fbtg36fm6w7U9f65SF0nnOKzs+DNRXsfT7m8atSDi4mSzZ+zHeZ3OkeyXTbXKy/OvRtXcX7K+xf+1n11aIXT'
        b'xF8PVHYfkU/zHd/6D9W632pSpnq4FoA/C3Jjmx8KH9rc/O3Ww7ZEo/Ch+KbgyobBd6a/epn9+f2QioU/X1/41eD62yWL6pq+OnfaewfaPNx+bdyd8S1vvDY2KaZo/eI7'
        b'YS2KlntJMcXBip/Lbs7t/nZ3wa8fFF84trzsdEbwgW1jqlR/S/WCSwr+fPqwV+HO8vvZ4Z/lGO6sePdMfsKIjKbt5z7+4K03xENuzr8T8XlF8JHvHYzJP33w8HjL1Tc+'
        b'uZr29Rt5b030jfl5VUVTb8ornqdy39xUir749JsNH/3t47IjO35fn1n9w5+Ckx5pVqUWbdt1LuOCeVD6J3P+eX9Y2GyLbu+M7ffvTKx694ZcfH3yNMkl11vv11a/kT9D'
        b'b/b5zO9bFj26u/bO33YLCpLiG169NiR/RVzj97F1m7/svd6Y4cx1WC9UjJijKpjx2G3tAx/202/e/+7SjUHnp1kr5lw5vKnA+8ajO1dvRR3YNavpyzE/TJ6vGfzLunD0'
        b'zpuP4e/3Ha49GrnBx+KX0PNZmx++0yXc55zz86gNovO5kpMtvuUf+Gz1/EISsXXIF8t8flvy+Y8nXr+x6/r3pxs2RPj/U/7LVcENpXNWwu5HlUbFr2dLe4LLrnzb3fjJ'
        b'rZmX8n4/9Il62Y8Ze/76xanv3T6cYtZzLWtNQcprX57OvrqqYeSPZzYO/2HZrvufdn0Z3vll2eWSipDX3fI+C3k4FJ7y1c2Iyl1wPvG7W8O3HMk/8pO06k9uG6Zl/rCk'
        b'bE3HO6WzDw3OXWPfZf/N+cKzmovX0qK60qfMc2m4oaloz13hvD4E5YYM73z9wfUex/sn0h+98/a9B18HrH/7t4nXx7YmVKX/2PNOlmRRweGkaeVT5nz3iP1x6PRKYXDs'
        b'scVr35Uv7nJt/GH2dydW3pOP+PVmdqFV3eXqOT9qWq27z3w04fa9Q7/NuPrnx48kv1p+N+LBiuLaCMdfHjMdi8+8Hvy1zFZPvo4RxaHLcr4gBVtQ013JxFhn2CEMHQVP'
        b'8YUr52EjrJB7estoQYwr2mexhIV1afP1NDTA1hbHN6VRXrQgJnMwKYmB29xpvYytdpW8r9wFFtvTyh60I5DWy4zF8Wbpk6oe7MYK+cqeLaiDfusYFmfDbU/KjlDxELwG'
        b'X3aEGuZQ4Fdh77ftmSIfAXAeQ2t80E54lhYvRarGkNqkp5VJ8DI6TaqT4G5fCj/a6YC2yaOjvMIJ+C7woDm8wOblruaRK4J7s3G0VeKjIF8bQyXiPNYbtifoTfcH9e4R'
        b'GHrT2rAEncMo+wrS0mCVnriFDK85T4KmmNkkZhLB7ZQwbrB6stxEULhnLC0ysoC1lDAT8UYH5fzXaYPh9iffqF0JN9NSoYkWDthjlkXgKCXb9GVsDErL4KlCgQRukQ3+'
        b'f10q9PLSFev//DovfBs4Uz/Z35cWFB0gNSoFoMDc4Wl5jyUtETKnJT0sY0MKi1hSvmPJsCzLDPwnvmduK6TFR1Z05hCGlBaR9y60SEn8m7mor5cfQUp/SLUN+9iOZX8X'
        b'CtjfhEL2kVDEPhSasfeF5uyvQgv2F6El+7NQwv4ktGJ/FFqz94Q27A9CW/Z7oR17V2jPfid0YP/JDiIQmN+2cZYyYryvkLFjXBg7gQ2G2wrv4I53c3/sSEuZ7FjLx2L8'
        b'P8HRiuELk0ghlKWAfv7NUkx7fhOKSasLaWUJJg4YA0sRKVYiVCAvISvGI8SsmB1NWgQsv6KpQMqStaKf3DEkjrh/CGPDl0w9Zh9bCjE9frcUWlE6CzeyP1jakR1IyZYV'
        b'Xo+0i/GeQlZn28c+maBXSC6x+5VA/ecFQ8bo7PpEg271DhEJEreBTaM7BiiMItE3PDE+wfR1blShgORrxC0krBySLUAXYInuha/VEwkLIQvTbxWRX3IBS9kUZqkghY2l'
        b'P1fSa0cv5WnBkm62TpelezCcv6an0qoz1R+pUqRKrVRF+r2jZcJe84QEktdISOi1TEjgf7IFv7dKSMgxKDWmHrOEhJSs5IQEXgWePijG5FtoXzOmC3tzYM7SC1krtHmq'
        b'xAZ16iUWBEuFzqT+UrTLBx0Ri0KtZcwc9ZD1U1huNp58pyQw+P23opGvo2jelOhPz8cG1VqrDr/Bqg4fK1N5ujk9urJwdFyxKGXr1W2zWguvlmR2Phrn07jFa+j94BU+'
        b'TT0Nv2zrMHjeujX0+/iK73xXlaV+UH3mN9fU7usLR29eeS3t8YVatEPn2pDaXbN8bnfAOhvXuzG/X105Ou37D5qypEPv5n9a4Fa3J67Dcw3rmjJT7pA/L2xMsGD1zWNl'
        b'76ZtY0tecR+zJ8xscKtlpXtIuftVu8ll9jrH5K8Dx74ZFrnzetWItPFzryVvWn7VYckbEy5sXti6aaJuqNvNq04dLYUr7iiHmwVetd+es3lsdNfPPhWB17K3S5Z/dTpj'
        b'zrakEnnhkK9Pzpy+/+3vRy89Xz/MYsWH6hUfuK7S3fuTTLZwjkq2/0TDUc2MvXtrlvsYl322Nf6RfHhk5VKrX9KNVpkJwpG37AVrUyY8EtzP7Ppe87bxvkxIC03h9tAg'
        b'fOhwnIVPN4HkDLQfNVIvgI/lFuS3Mfp+GQNW5Zl+HAMdT9CT6x5UibZGSjxJbSd2Uk9+QAN1xgyHbUJ0diI8QN2ZBl2O5mAj6pSERiueXI3Zox2kpvw4izWCKobDf6FB'
        b'F9Ojw8sf1FBj4dZkKVMSEqiV3owfrBPL+jNSYjEeExthztqxduasmFjQF17Eoj7/Ihb2+RexuPglFlpSy2V+Hxs73p4/dDcHBayFFePBEP/AujoxOud+1ojFSvXUFtn/'
        b'15CK0bk80VayOTFNtGzT+85LrJMC8/YCDpcqUC1DApqYSFgMK8yAjatgKDwKL6o9861YToVHznmzbOjr4202h9ht+6AgNc9an1S37daxbnh11bdedaPu31x2JWpi9z+2'
        b'bj2duv7cJ2/kZVx+sA8+zotdXHvgy+aNdX8//49TY7bslOl/POh6/tbyCznjxk/4Pt96Z43XiraPD/+jcvhrd1w+qrspM6PRBKrFcnaW/qRSzpIYevFnhgOOVhadHIQq'
        b'qYhPCEc1ETEK1ILHxMSQFFUp3GWPugXwmGcBFV1YD41BBDV4cSmqIJd7OJ4jqDkIhsFaAQ2G4F5YJIoIi5LCyr5a7VAvPpAqyURncQ/qgqef/FqTRMaiHaiQpTXiHs6w'
        b'gQuLykCbn/01J8chtJLbKQ12yMNhFyoX0RxH1Yi5fdoy7L8tGvr3xEf4h/ql1qr1Jv0iImVubWkqn/YSEIkHBcKFOtcnEi/tFWhU2l4hKZ7tFekN2RpVr5BkibFfVifj'
        b'JymA7BVwel2vKGm1XsX1CkkNTa9ArdX3iujPr/SKdEptGp6t1mYb9L2C5HRdryBLl9IrTlVr9Cr8IVOZ3StYo87uFSm5ZLW6V5CuysdD8PKWak6t5fSkaq5XnG1I0qiT'
        b'e82UycmqbD3Xa0U3nMBn6Xut+RhPzWUFBviO75Vw6epUfQL1m73WBm1yulKNfWmCKj+51yIhgcO+NRt7SrFBa+BUKU91mkd7mC6AvB9PHl7kQVykjmRKdBPIg6Q9dETE'
        b'dTLyIFf0OgV5jCUPYpl1PuRB78mJHOrIlbiOZBl1RKh1pNZaR3LfOl/yIMlTHbmG0xFt1pHThY7E67qJ5DGJPORPTALhjkUf/+bcf9Ek0BEPzPt++qjXLiHB9N5kXR8M'
        b'SX32J+Ck2iy9lPSpUqJl5jpicEgQodRosL2j0kB0odcSs0Kn50g5Qq9Yk5Ws1GAuLDBo9epMFY1gdJP7SPhc1NFrPpWPVaYxfZALgVBszvIy56hiaYT8vwE403Nc'
    ))))
