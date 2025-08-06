
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
        b'eJzVfAlclNfV9zMrA8O+b+KgoAz7JqImKqLIDiruCwwwyCgCzoKiEXcYdhAXEBVQURRFEPc1ubdp0zRNIJiIJH2TNl2Svm2DCY1Z3jTfuffOIKhpm+/X7/f+vmnzMOe5'
        b'z3Puufee5X/OveMn3JiPwPD3yw1wOcJlc6u49dwqXjZvH7eKrxRsMOWe+2TzO3nsm9o0W8DnlKJOQ0sRpzFdzYc74myh8Zk9PKBNlKPv8Lhikek+ufjbHLO4eVHJsk0F'
        b'2bo8pawgR6bNVcpSi7W5BfmyGFW+VpmVKytUZG1UrFcGmpml5ao0xmezlTmqfKVGlqPLz9KqCvI1Mm2BLCtXmbVRpsjPlmWplQqtUka4awLNstzHiD4B/pOS0b4FlzKu'
        b'jFfGLxOUCctEZeIykzJJmWmZWZm0zLzMosyyzKrMusymzLbMrsy+zKHMscypzLnMpcy1zK3M/Qind9M76W31Er2J3kIv1FvpzfR2enO9qd5Bz+kFemu9s95eL9Jb6h31'
        b'Ur2LXqzn63l6V7273iZnAsytZMcEPlfuZpy3HR6mHJ97ZYKRhu8exu88rmRCiccSbvIL7m7htgpWclt4puvl/OSssWtkAf/ZkYEK6bIWc3LT5DwJfC8vFHDkXvCymaYL'
        b'SiZzOm8gJm3yx5W4PCVxEdbj6hQ5roX/VcctTQ0Qc1MXCPF9XI1P0tfnzhdz5hxnHVzUsrpbYsvp1sJNdA6fT8W9phaLYoFNVdzSWHTRB+v945Nw/RIJLo9dCmxrcK0f'
        b'dIFrYpNwzTKf2ERck5yYstQHGvRB0Nmi2PilPgHLV8bG+fPQeSGnReUOEfiKSBcOPTjviAPO41kAz8qgRbH+CbgKHcZXoN9EXBEn4opQremaRfhmFm/MfFga52MrXA5Z'
        b'lMGc0IUSwiKJYRElsHRmsFTmsJyWeqscS7pIoLrlwtFF4tNF4o1ZJP6Y5eCV8A2L9Mzd0UXa9+wiSZ9bpHNskdzcTMgsb7WQZ+T9KciGozcT3Plk5ayF/Iw8NCGT3fxq'
        b'mYSz5rjcr5QZ/lvBWOnNHzgRB39jL8ZnJP4iN5Y7x+WZwe1zJc7CEVtu7rBdcdSbHtdCfuXfwuUR+261beR1m3CyYJW934ehLSvmstsHk76wOmjF8xnOuMn9Y8WJxd9w'
        b'Q5wuABpW4/aFsBww+z4+uCIoNgBXoHML8NU0H1jxWv/AuID4JB6Xb2X6Mu7wkQfpHOCdXNyAjmrMYU3wzWW4kUOH/XANbUGHcFekRi3iOBNUgSs5pJ+Ad9OWGFS/WaM2'
        b'gUfqZuFqDlWgZlyncyT6gK6j4xp8Db664w5cx6EqJe7SOQGNSyfpNKgGZgpdAC1u49BxdBzrWVe3AlADNPIJ73Z8kkMn1oXpbKHFc6abZjOIgGptcS30FJBAX/BFx/I1'
        b'uEfMcUloFz4EgnjgBvrC2vUTNTp4wQvX4XoOVS6apCNLuc4C6TUW8HxUNm7hUBO65sZ6Pro2VoN7QSp8HO/FR4BT0Fw6FHx/EbqmQVXkaxduxcfgWZtc2hSNSvkaKQiL'
        b'96GjuJWwa8eNhknLw3s0W8B7L0MH8GEO1bji8zp7aLFG+/BxjRV8m4JbyEuN4vmso+O4MRv3WhAZLsfiixxqsUaHKDdcgWs3SckS4BY+7oR3cJeccgtEt9ENVAnrxpuY'
        b'KuFQlwKVMQHq88I1+DKsZxZ0cwAmDtdk0X7QlbX4JO7VgWwg7jEyywfnytlLBzSJUtxN+mlFPfgSzH/EfNrP/IgizRY+XbPThFtFCaqmr/ihczkafB2EdgFeTdBvGAhN'
        b'+lGhW6heY0VeqrAlvRzF+3EHfUnhvRP3SkhLO7qKT3OoeTK6yka6zxdmuVcCIrhG4bMgQDq6S1teKRHhXi0R7Q7MaBMZ0P65dE2jFoBzM4c1nbyevHEcnWUqbZuIT0AD'
        b'TEEKuJ8O4OWB7+ucyTjvo8t4N+7FPUQNW73xKdB3vEdqUIWX0X3wlvCewwzcxaE2J3yUjigEVQVAA1HDw6iUTM/JCHSYzs9s3K6AJphTKUx3N4dObVhIuc1xA+F0IBxu'
        b'wGeIytWjfVLKbQWu3ATLDd3AVO8j75xEFxcz+Y4khYB0vcQaO4DfeZgh1IXu0/fW4RYBaQS7A2UjenLCHR+jUkxzKYDlI2+Vw2yD6MeXCdmYavC+xVIJaalE18EuUftO'
        b'GX0lB12RSvFlYGYyC18FGXCdFZ3VLHQT3ZEWwWDXTyOdNK3hmJrutcINUnwNZi4ZbK4HOlmCrzHNqpGgE9AEo42F+ewFDcZ3Z1Gr1y7CN6CFTN1BCAzQURvqxfVUhJc8'
        b'8B2Nlkc9zXms51BpqhMVAV3ylUk1VLWOk9ludHNgyojKUbnUDLqZtR3f5NAZ1CvVuUJDAKrDR1FlxAbgXYeuoioRJ8AneSlLMnQEWeAefBh3ocqiHHBUB1E1qhBxwlwe'
        b'2o1OoArdRDobNfOhnTSGGjhE4IOcKarmO+EKZ7mA9h+Fr7vjSgGocxvHFXAF6Aou1dmQBg+0P0E4dznHZXKZ+K7hrjfqjEoQL0SXAZpx2agyji6JDJd70VHji7iMjhrv'
        b'CdT5QIsQty4FbdGjzgh0TqRIQtX49IZodGpVEhcOltujEaFDqBWdobKgcxvwFQ21i454XM6hMjMLyiXPMcTIpAsfwgfp13B0ZRvqxIeE4JarhabQ8VkqjL1OrMFXQJjp'
        b'6BTx1jXwzknKBt/22cn4oGuogzCKRV3A5/JkAx90VyggeksWLG0lvkBjyBx0g8aQ0ETGpC0anzJKc/GpNDnoIDgUKs0Bodg/g44IV6PWSeBwwT2kueITHDpmFa+bQqND'
        b'/HLcEIsuwLSM8ghFpTZELuARIMA3Zm9i+t614RWNmhh32Q5cxiHinw/ppkKLYy5opnFe6OSiOxukMnwhHyyjY5kdFy8zkbpJqCSy2aiTBr7Y1TTu4Tu4lQZYq+zE5+cW'
        b'XQLJOxPQngh0nsgToBZtBqNtZMtUi5sX0ljpZMVC5a4SXSA0bLDeaRwT6lDjakEmEwnW4SgsO6qEVY/FN8T4KtqDbzELLBU4gGsnXHum4xoIbuCvLum8SNOd1bqnUwRm'
        b'UsbWS7iYc8O9Atw9F3SSTJD/dtymMSOh6xQ4dFiqQyG4TBcBLfNWzhqz3tVjVgzv8qYq1JFE+F9IEmcmcZvRJQm6mbiArdwR3B6gQRUw73kTiK875p1OB4nvpQcQsRrx'
        b'XhDGuHoC8OPlIGVpDhjaUS4Et4hQjTlivgSfC8e3GIIAL3OUQoiCSKpNW/EeCDVjtYmqZG4Rm3d31CDAd2aCc6EB5SZqDdZYwkinQhQ9Cjq5Fvfo5KTl0s6CF1nIrnAi'
        b'INHJMqEJeLBuKs/L+IyAwZZ1MBMUtTSiO7pgArfg+Q7GCV/CNwm36vGiMVMJ3y5CTXH4AJ2r7VH4LkM6UdAzQTrzwyg3GwE8zZh1cmM1HW5Us/knzEJxrQicQBWL6QTg'
        b'oTqKkGxCKUAC59So82WgpTp5vAWzgeL9MQbDwReFErx3IpXLFd9fwRAVH+2niEqppGuY+XLYqFMyMgGGF4hQqHRKBDPkAPCpGrSb+cmMxbOAFcGHbekkYh9EXVm0QYdu'
        b'TqLoDN91ouhMiU5QYZehK4uNvZwnvUC8LCYqgkoXhMvQSbDPJHzXJHTNaupvciNUFMzhvVspmsuFyfWH+0unotOMjRfuMjpRMCq8d5VPBBu0BrVIcBU+qKEBFxIctMuA'
        b'/+6CWhL8h8+hi7ogioqSwY4ajIsw3t7RjczRoR8WacxxEx2hdoeHhoZoVGuOj4PWZaG9VORka9RCMeNyAF8EMq4R0JH7oQvLWB9WGDzIxVG/Hy0DZE4cUwo+YRI4F+1m'
        b'MTMJX6KADJA2xWMOoO9E2HB8HZ0ddQHV40QOAoW5xoYPuFG0AUIPs5G9RRrNFhKbzxeQJa9GJwCQE3/iEO5j4HX+qeL4Bxhc/1QBvp29kilgF9oTx3DgQgWFgeB89lCP'
        b'CzDwStBYv81M4kIMMRAh+KVrAlCSV+g64DZ8GQA6vk5iCN5FwPZBwG5nqJjp+BQqY4DyXBEFlA7oHNXNGZABV7LZy0VXRg3w3LMGuFmEGm3dKSCBkNDsp7Ei8bcOrBcw'
        b'6DF4/TKV2BOXTyYCd41hEeqK9hrMRSDAl9AVxCInqosJY1hWBGkMgbK4Tc0Mr94dXzCqzaUxdndvndHuToGDOYSYo0In1scz4JsATxLkGwK+OozATnxx61NHVT3OAiOE'
        b'6LJ5UtT86DR0cQqnxockAFsaOKYj00CTKWSWTaWAGXUL6GL5BoLm99J4D7Gjl6jh4TBnGmNhxqHt2fiIGoqiZSIuHLWKUIs/AHLCft10J0DXxGLa/HE7DDwF36EqiPfO'
        b'ZEEIn0f3RrVwrIulfjoMN4vQgZWGpOTMCnyVoXgXgIEExmeD56XsLiVCyjTqeqpHfQO9I4DxW2yYxluUgJtEJpHbJxiiB9qXwrB/Krhwgv0BE9LYPRVVoeoEGsHwodng'
        b'y1kYGY+zFqNqE090PpEx60S3Y2G+CEi28CNDPeqNL+v8iNhV+CwCzYsFB9xrMDkawSknErvD0FWIaqhsDmW1dRtuwr2WxC80RhBIewrtgQyCRDV0PMDkWSsJRQ0ATs8z'
        b'M+kBtSvC+6myLEWloCw0fKAuK8AC6EzaRKq7uCYWsuqnYQ2Wt2cUA7ijPWCygEUqmQ1c8UUNuHcz4dIIEBusrdYSUjQK2VpjeOP8PZXnlTyD6qIyAb6Fe1APY9SF63KA'
        b'kZjkneB6jxP3eclKN5lmwkGTx4xr3zTGik8QyXWwfHwngmJ3eFFP8lKakwHSamdJWTWuodq20ReslCZls4Q0KcOthdSh4pPbPFlStkhOUzLBFFZnqASwf5blZOhUMM3J'
        b'8IkFVMuXhDg/55BwtTeZLzLT3TDTbpBSETYlk9EtQwLXhK+xBA4SMroKGYn4OrQRM+qyJlZ0wASdpquwA/UuNXiQ88Ye0JUY0JFRF3LFHZ6l6nVvAYJclIbDo3MItGgQ'
        b'4326EDo2VO1oAAPN88bbUNeoJQjBQxwVoRPzAASyEH50MszjVZDZ25WYUlOUJ4UW6E4GJIKUnRq1G9gx/9gxlttyEaqDpOoSLaQE+YVClgoq4r6YzHvrSwqm+acs0G0D'
        b'rDiGbxstCJzF04iVmmgywxE1U6E2oXsOLNtNsWW57uUddIxCfFFJFwNSz1ujBn7x6ayxKQtD90WguCfREQY174QpgR0pSoHvhyT0lIlcF0rkugjBq2pcAORnGQSzBrlu'
        b'RNgESpF+Gg81zzVLBuzbwbSlZhGoB0u5c2GSSMa9AV+gjhxVknzy2cQjHHVDGGDLKRdA1D0EVuVCHt8NyFBvzNDPACgmKTqqc6fQZIpt7HMwygDtwE0cNmIJnajQmnkf'
        b'yMoDIKknptWBzhBexzwg9hA1TosHDs/qsVjIgp0bvinAl/EVNwN8vYw6WG0gfhutDODdsMAEB6/LQRdeiA/bIJQYcsX7QssVVnTivdDJ7VIJkaY2kqTxp9fiWqrykfgG'
        b'rOCzDiwQt7ARueEuAe4KUFKbnea1kxYjXubRUgRqwqfoTJsBrr9v0Pc7qjHAbYxO+ZtMR3sUzHLKUHucVEvSvGuAeMExN+BzQtpkhtuXs7IGJAtdtLDhh68ZnFUJqqfV'
        b'A3Qf9dD6AQy0h6VpNQpbaRFxQCcU+BwpSDSupuqOb0N6eGkcNDVoJ4ENT33i/UXbWIiFzG+vtIi4jVtWpGJ3BF3Fu6iGZuMDkPK/UEFR7ypwePs2oKbl+NQqTr1RQoow'
        b'kwwar8VltB6DOnfSgowqkMXHXrwbnyCi4fa0ZyNtp8jWkFxdIOnCXcBkxHOlQnrQy4o4xZAWkSLOtiwaHqcHBD+XqBszQQ3qNea2qEGkXZvGBLu2ZgUr+sycyGo+1Sms'
        b'itUDE7yPVX0gIO+mVR9cl0ElyEQ1mVJL4joPuOI7oNu4HFVRh7AKBmMAc7ht2/jhnBvn9NoAjaDaFdSutgkgPzYuT4DgeczRJdo8jZcqMYnwXc6suhnfsKGzdtl3vMe5'
        b'IMqEhUjiQp1EqOplkIqo93IXwbgUgK2+NUwOK2Cgy0JhBqpkrA9BXlv3gtwSYmwXQ73uuEIoidJQ1ushilQ/71/yJxmsb5YA38VXw6jy4G4lpGXMWit8x/ujcT4cN4hA'
        b'NW/gS3IJw/gNiZFSS1bzrcD3AOrjXkfm+prm4RYp7qFYqYsYZBu4wjPMVloc0BFoI+8dATx+AxxtNvgNGnhPr54gNSXY4bIHWcGzvDWsp858tF+qA9UKCSN6egTEvU41'
        b'ZbMY3aT1PHxfTet5SyFpoYbcy0uQaggqugDigZqcAHBzjCrRGui1BiAWcYAAbErxXfA5uCWDImOhTSRBX0hfxMp56KLBNpE+gpTvhJGgsmmocim3fK0YPNFxdEgupGhj'
        b'AnjpZlyZGI+rBJzAFfL2exARIJdqYWO4JspPgHk6uDRRzPHX8YLADg+yGuIJcJwtCbgGUkYOn/eTk70wc2uBA76H6qjEhXgX6vJLDogVQmy7g47N5YFMJ9GVLLKLZPyQ'
        b'/Ru6taSFyyGxcavzCKfn0d0uvp6jO14CvTTHlO51CflcuXh0r0tE97qEY/a6RGN2tYQlIsNe1zN3x+51/XYY1s5MNuYTTbZoNTJFPt2bleUUqGVFijxVtkpbHDjuwXFE'
        b'HNsZ9t1YkK8toLu8vsZ9YZkKuBUpVHmKzDylP2W4UKneZOhAQ94bxypTkb9RllWQraT7xIQr5afRbTLuPyuysgp0+VpZvm5TplItU6gNjyizZQrNOF5blHl5gWbjbs0s'
        b'VKgVm2Qq6GamLC2XbUGTvenMUS6BL3ohU5U1kwxzvapIme/P3iICzouLHieBKv+5EZFPFkyMcquWDEGpyMqVFcBD6hd2RMemLh7bmdYoJkzlv9+PluzGG7gFypJ0Gi0Z'
        b'I5n3JSkBYSEREbKoxNTYKFnoC5hkK18om0ZZqKCC+ZJvvjIlqIZOoVXSzf2MjDS1TpmRMU7e53kb5GczTlXLMBbZElX++jylbIFOXSBLVRRvUuZrNbIotVLxjCxqpVan'
        b'ztfMHO1RVpA/qqT+cDdGkaeht8kkb1FpnhnMuP1dEffs/q5Ncgz1bVpcO12z2RRVk9BFymlb4+jO7Qc2zhwg6dSs9RlrMnTmLM8uAWBwGFVymwBLcCu5lQAfj9KnnUzN'
        b'OHjAR+6SYd7v5Mc2fwVrrTh3YDExOCMvaLuEoyB7K76ZrpGuJ7UNWhRKiZVbMed8NgvpNVLASHuNbQByjjGvWYPOTNJsQTfwXvDPdJMRnWYAy7VEqbHC5/Bpjr3UuETN'
        b'NohQ3U6AzejOGuKFyRZjtjXltRMdwN1SdTguJSOmO4z38F76TpE3Oi0tRLc3kU4gkz6iQRfZnuzCVOlmkxJyGwB98xpDVoRvRPqgSnPI3Vp5HI/sSU5H7Www515CR3Gv'
        b'Bp2wIt4cMp0D4LPZXvISu0QNJptyraQkQ/YrQ/BNVho4gQ8vh/woGJeRrsh2ZQhgTtI0BZx8HaBadKWYiE32KyPxPSZFLT5fIN2CzkaSlyConQCMwaToSEQHca8aHUYH'
        b'yFvNkKwuRy0M/x3nHDVbfBlwPAJCrDFsc6JmOa7SbMEHFvOZeBWLcathOwjfkso1W3agZmPTQkPteQbepYaO8BF0xdjRZj/6Si6+gBs1W1YWGPtJghFRXjVztmtw7zp8'
        b'VMha6nYukvPZ7iMuw1ehDet9jW2odCPb1Z7gokFVJQQH0f3pJWgP1bX5mfQ0SOS7/hl5J7bM4qhULqgU9YQFo1pUR5BzA5cpx92qW4/PCGk57A8Oh3fU303Gwda/eKfo'
        b'7Rq3efsbjzp4fWya8Ylno+/7zbblrx3KrRyq/sOtyR6Tgn75epzv+Ve2Pv7mb3/6Ycf3X6dn3F60/fVracGRui0t/v89/Pa2w/1/QZWfNnpG3/pbSamJ1V/i3UPztsd8'
        b'ccPGIjru4urb2xy9z32b1bbbYuPPZ9tuf83i8hSv1a+aukS/Hrl6RnLaX99eWmnW3uJ75+dx1T3/2LNW8l34L3Oc/nKo+/qSC9oz/9D9ER+od/u7/73F14QHnax3bK79'
        b'6+3PmhvePhLcNb/trZiRd5bMQW2//i2qzvNpyfroZ4e/2fP71y85tx3r3vXz2b6P4ralvpxQKXn4XtaXn3Q92j4z7W5Zhv0FxaVr3WEbB31/+N5EdG5RvpVIbjJCJm1C'
        b'CTrlF+DjIo4N4HNidJQfAHBhxINoRhlq3ewXGOfvKw/Etf6A/DpxJcc5y4TrFLh3xI0j5zF60e6ElABUnoIrAFBI0Zlli/i4BtcljRAwArjtEq1glvvOKgwI5EEHe/hh'
        b'+DzeP0IStFBIYQ7DurPjNVvI8ZqIXFxTFOCLK4L4XCC6K8JX0D3UMEJLqJezcCOuTPIH+HchDtdwnDicb+kiGJFRrDepMIGdzwEvVUvgjwrvEXAOeJ8A34izlkuH+D5y'
        b'NdGpn3TRkKMyMtku4+dbh5dy1AXblPmyHHZSLJAE3dlDZjQEpBNi25jvfMKiHpTv613c41QRZ+886OQ+aOd0ZGb9zIaX9PMfWdkOOrocUdWrGjbWCR7ZTWj1OhvUFtTt'
        b'9WDS9GG+0MF70M37oVtAv1tAR/aAW1i35npxT/Grtq8uGZge965b3OBkn2EB5x7PeyzhXCe3hnWYPHAJHnSTPXLyGPTwbPVsjWrMrVv4yMpx0NWzJaApoDmozoT0Pqd+'
        b'Tmv4AzufQSePYY43NZX3mOM5p/I+nug16OByJL0+vTXtgYMvtPZNieh3ihh87n7rxn6nEHLbZULLxKaJHU4PXEJIv3ZOjQs7Zve7zyCEjUOjV6O6ldfo0xHY7xpJRu7o'
        b'2hjaGFWXq184aOXYqOq3mkru2k9oXN9vP+WhvX+/vX9H2oB9qH7BIzsyVY+sXAadPB86+fc7kQan0D7r0I/tnRttGm3rYhu3wEsd9h2Kbl6HS799aB3vkZNPh82Ak1+H'
        b'tt8prM867OvhBTzOfcpDt2n9btO+4HgO3o8meg0L4O+3GrKBfdtrfgT3swirBRLB6yY8uJJ9TE5uPiQkizckAHw0ZGJAG0NCAg+GTNLT1br89PQhaXp6Vp5Ska8rhDv/'
        b'XIfAU3EZ8DHqkZo4RDWxvrG6cpg8OgMu/7OLe6IS8nhTRji4/NbSqXLjLukwX8SzfyS1rZzxW6HVvqRBidUjid3Xj0WcyNpIfashrrFZ7Md1SiME4MNJ0UYlFySAMeDK'
        b'ZFyTEifaPJezLBRE4hNmOnI8EV9EZ9GdhMRkYjboOkB/Px4nXcXHXYrVzG3vc04m+cJuzpgvVPtnGY9uko/QCDVyCd7nM7xP0T4HWF+cI6QYXwAYfxSx7xBSjC8Yg/GF'
        b'Y9C8oERowPjP3B2H8Qd5z2J8evhyDMhXF2ySKYywfDwAHw+2nwHTaf8E86uVm3UqNUN6hUo14P5NDJIaT4SOB2UpRqwGgvguhh5Vm5QL1OoCtS9lpoCW7BdDeSIvEZfB'
        b'+WcH8UIcaxgUe+PZEb6oCwL+Y/IU62UqloJkFajVSk1hQX42YFaaA2hyC3R52QTTMnhKkxFDAvJi9LpARYb8FCxDYqSQhQZodYUAgg2QmM4aYHkf8oQ/6Uj+k7CsKFn3'
        b'Mgn3uEz5orOZ5Ym+8f7ofBo7pgkhpo3cTEmMS+JxqBOVS2fgmhVpKnXvBzxNPDHE5veb3ww93tZwtfH2vnqe2WLn5dGPkqqOX1j5lrlza8PNBvl+1bS0KdO3lpbvbjvc'
        b'drinoV3fXtpWGlItb2wr9WzcHTaBCyo2v12yV84f8STS2uGTUl8wJQiZVd55STpDPJuIeoX4EmqYPUJO5KB9uGpRQmC8RpjkH4eqWcwScK7oijDfFu2Vi/+FUxGPBibq'
        b'Toak7PQxC0FjCRqD5nAsBsWYcPYeHzpO6ps8b8Axus86etBl8kOXoH6XoG7Jjamvhg+4xJbH6+fXeZHI5OTWmFa3rc/aE2KGPuFLshrMQZoMSYwKOmRiUDU1gaBqEvXV'
        b'buMlNWHujwjLPB+ZpHEiPiSPkeO234Hr2yjm8bx+qtc7JPbm2qXBAqoZk1E5OkfqJ5tXjaugkJMj+9BlVIVa/QVrE8JRzWZ0EZ1Bd824THzAAh9HZ41nOS/iu+iWtAjt'
        b'jrYErA8pCO4MQGVsK7cG0P0ZaKvJ3kza9Bwt7pYxTH9QiSo0+JpVqJDjzwWuPEc3vI+50rbEPE3oSnxNzed4BRy6jquiDeeCLHCbtKiksEgM7PZz+KimSM42NCNxOz4B'
        b'/rcYVxv8LyQSJ1m9pgx14susXgOI6tKYgs2JnSzzyPXwS55F8BWP46MaXjQ6he+Nc94So20Vck+LNeC8RXpjucYUnLhZjmTUiYv/Y048B5z49z9WqKHeZ3yZ5kddGHF3'
        b'5PF/Xe74kSoEefl/vQiRlUfF0ii1z5cdnhGQzEtBVpYOvHV+1vOCGgsPC1KjZNGAUNTEm8+HqJWlLVAX+8sKdZl5Kk0uMMospk8aoku0EsajyHuO3zyw9MAxsinIoujo'
        b'Dyd8l0Sn+frDn/nzyZ/olMUh8BfE850XOo82REf7+j/HccyYFHmagheWT8gg6TwXsqIJcM0mgaW48JkJJJ9/K2SPciwofD5Sk8+/F63HLd5/tGozCqVGI51VcoxuNvEq'
        b't0LRLhbrIGH65/HumViXhzppxuw1hRR4undYZWS4N65IZyWbS5ttOS8uQ2PBZbyydqkfq/pAknWCHDYlR3eaaNnn2g7qT3TzcQWqRHqkB3O3swnnmeL2bMrn/WhLzp0L'
        b'jjMJzvBPm+bHQWJvDbfDi4vDOFLY2c2FcCEe7uzs63V8BO8JE3KWS7hQLhR88ynKY3axDSfjXtWJCzPMm8QTCQ8C0dF5VM4HLuDdCBNbGa3QyMnpr14TDt1Bd7hULjVy'
        b'GeXxe47UpfpSJdYZ/o7iFVyayvNGklDzBjT9usN3R2qU5Z5g6w+3382Xt58MeZz5++yTJjs/dvof/pMpU/6wTBJ70qngv3/ztWS26lxriM92VU7O+vW3n3zK2zej06VN'
        b'EdxxZntB7Lsesb/f/Nr2pKyBGV2JPNPJpSXbnqzhdvMP2E/7OvMv35rHfD8ca/fDR6db/rQlJyfi8KOvbjwYxrkn/rpGPa9j79LK/b+QPvnum8IDlvffTU34vDz+jfbo'
        b'N0/FmV5benPtzMD3Q3m/y7r+1lcfT/i7VrBgsHN197Eos2mdH/9sSUfjzNm8Q18HfvcPjVwyQgLDZtyBywXLIHMfzdtdUSWFH7jslWmj8COpEF0fjz88TEfI6YVlFuv8'
        b'COovTyHpexCuECUFBZA3Eky4ENwqjotZO0IyhBh8aoV0EW5PwFXyUSTjgMqEEme3EbKe2+NQaUJKAISYotX4JC8qBpXSdB01bt6QCaEJkv+gFCJjCd8XncGnWWN7LD5l'
        b't5lk86OZPDqFDo6QyEaOKu9PwNUJ6Ag+Y6g9cJxVsGD9QnRFbvrT8neyHzGavjOkZMpyLgge255+pSjpNwaU9AqgJCeSmdo6HJHXyxv89NGAhx45eX7oOqVvasyA68I+'
        b'+4XDfIGN56CHz0OPyH6PyBt2Ax4v1y18LAZ81ZjVGvbAbuqg26SWWU2zWjVni9uKT21/4BYGGfPHdh4P7bz67bxalzywk9MU17YurHJrY2hFSevkVkXblI7okwE3BPfN'
        b'b5q/uvRBZAIRAx4JKS9qdOm3mtSa1eHZltNt2j9lBn3ZsTGscXOrTWNk65azO9p2nNr5rlsEqzF8DZPpPAmyXhvPR24yyHptPFnW224zbw6H5phGSwXYjAdXBuqkDMGR'
        b'5RkSQDx6EZb70RLJc9ktOZYxZnr/xhmSW4LwVprweBO/hOR24k+FeU1iOXdOGi6Q89hG7GHf1NG9LnRwKtvr6lk07hdYo241g2MZKv0FljCHP/pLK8F/7JdWuXL+t2+P'
        b'8/CLWYT4kQQrh+ZHFIuM3UD6385IfzRECZ4LUeJk3UyyEsdnmLwgGVvs8i/CU346K0+f2SCkh3xxLZdrR39vdYDuOK/bBBg3JQBXJOGqJVifyLddANB+P2rHu0WoCb7L'
        b'uVRrE3RtlolqzgVLAU3o3n8nvvnNcEjoesYndOYkocuYdvBvmdybvZlvng1+LZE7+itLJ2VM6JGQSrsl6VMFid9/tQD8jJg71WPxbe/P5CLqK/EectTzqU8ddaj4cCD1'
        b'qRvmjNBN5V2oNIy6ZHS22OCVvXAZrabOhdh5eGw1lVZScRM6sM4K3aOudoNcKn3OzeKr+Kpk2lTKP1aZyoqtq3is3EpqrS8Xy/ljjJH4MaOjM1mv1FI3Z/xCnVycwcmV'
        b'SJ5NBZ/WJccWCT90lPV5Th9wjOyzjhy0m/DQzrvfzrs1e8DOr8/cTz2JMyaFIjUJTC/MAEkOn/E0/yMKMyqTM8+Q+32zi/v7JgmPZ/sTnMKXxCnUiz25Nqm/4F9avVDP'
        b'/T+xekhlvj0/zmiWFOaptJpR02b7hmC/MnI3R61YT/cBnzFzo6tQyMJfWDAZ97BPdMrS5LTFK/1l0bELohOWLE3yl0EvCenRKfMX+Muioml7evLSpHkLFst/mkVTLFUf'
        b'TLZYGnlSWYb/FM8gTjeLaHgb6Dz5qa0fKCqY9qJYmn/S3BNdQ3vxATk6Z4aaiuG/OFReDH5BbAaIsQc10GPX6DA6t3Ls+2DSm1AFdeAeuEOITop0qjrLrzkN+XlvTO1F'
        b'ZsgzKut5ggul76596/hbcnN51WLzq+bTzI8nKqsWfOj9VvBSeWJn27Zm51lNG5y9dl/wX5Y4MLNJ8ecNLhudK+uTMmIaU3Hj6zUfPPTyfs38mIp7H9l8cyRBLqT7H+vx'
        b'eZ+nKMrZnx+AO3yoOS7dFu6A2p63SIkK1TIQczceHN5TCIOqUAvfcn0i263oCbFIAFgVhG/hywE+Ys7UmY/aXnGSC18YQ8nsjxrIkBkkhRpDKWfMd2q+6cx8h9eZcvbO'
        b'o/b6fGGdmu2cAce5fdZzf6zCDs+0egw4BvdZBw/aOR95qf6lhtl95p7/V0YdTYx6jLA+Y+06yfSn2bWaKBsEeSKIxZRoFuNRJa4lB5CDUAXbbnLdKczFDXj3iw0/mxi+'
        b'0Bjuyc+tDcXo/6zxr5fzf7v22WL02KhPq7b5ik00Y35BsCf5MjkeUKiEGwAKxoffOOYC8hRaLaS/WQqI3OOZUgygyGb17ucS/3G8RosA/6oGwHL+/39AiCRZ9xIxyNsp'
        b'k8aAkLPo5r+bJdvnU593v8QlJ5LLIHDWPW+Bo+F3oaVBqQSbgH/rZGcmIFMpp+hkx2rVC8GJAZmEoHIKTlC5H2X/na3YLEMA3gFc6kOJH6fKu/MRX0P+/YujKbdYDfrc'
        b'OMiSaH78reOFJWZLrtkLouszpi5xzI4NE4jndkjFl3tXhCwlLrFqbnFR4jf2OY2mc58UogUrUz/Ee37vsSxOtlKq3ek4/YxqmrnkSeEZHmff76iJiJeLR+jv6arjMSAa'
        b'dIIcrnsG1bAy9bnUEXKGT7vMakyemEK3knANOMUkfDVJxE1PFpego+gs9aWoklNSXzrbxIB+tOgiyyI3zRmPfVAt3UhGlegUzfm2z5g/3tPiihXU2aJL+OAI+aci0HV0'
        b'HdclpETj688IIgKRDwjx8TS0H/zVj6YpxF+NqZebU/wBek6saNs4ivrZ7ZyhYm72DEwiCdusAauJraHvWnnT3cnQfqfQ7lkDTnP6rOd87CF/6BHU7xE04BFSJx10mvTQ'
        b'KaDfKaAj+4FT2IeuXn3eswZcX+qzf+mRm3frxgG30O6QfrdpdRLKJ7DfKbBj64ATQVpjfLDJkJQ41PQCNcFL/zwtY8X2MfsC6iTil8cNb+YYz/xkM3hml5+ahjWIJ3On'
        b'pIECuSA5OUbOi5Hzk2NUf//qC6GG/Lh19r1t+x88WTKQ4WwyPP2zVtWqr3z10icePpZr9BU3rvtE3nf0Se7gX9XJhq58fEEvcFq1U/VD7P1i1YbPh2YN3E754o8unzes'
        b'C2x4fVHAn2v+vCjlwSzvnyeEt1WsWHohsl1SPPezAsfMbt1XgWkTP1dmRbhszLzwdsVrJ5oVMR93Lwu97dm40rT+4Tsu6r6TdcV/NZOHRn8V5mcy0vrr8/ty3qvyXXUt'
        b'5c6NhXNbFv1u3daPF4TEn9lk0z81teLyvj3qtL74tP4ND/pWfZ074c+fuYf33Wxc+Kcs3lp9zC1J5We2/u2/6j7W9Wr8LbPOz1wvtP939+y2whaLyx/FhPcnDSY29+zP'
        b'n/bJYOlfr4hmfZr8l5O3e8quvfnpuiv9OwZTrFqPe8w3ednrS6tPJC9XZJl6q/6mdZ96Y3b5kpHwt/t6Ixd+z3/nVMO6VxcM7c/fFpdcsnL25w4udys2jtw6Jr4R9f2n'
        b'bXc/PcUbGWi+cejRZxF/K9zh9ORTTqyyfvKZwLxfUdVn7fFu952aNz6d/OhxyIm+s87t7wTHtHwiqn7zh7frBn7x1tBp/sTfOf9CuO53Dus+sfiv5NsH4tfUfrZ7Uv2W'
        b'06F/iuj/TeD8I77z55d3KB63fHg0sSsg06qTFzBnep70gyV//otu/vHhR6L/2v9e3cCa1zcItu02e2+bXda2FarfFp/EgZnTXvnyV5mzv/FLmbr4q7e2f/eBz7QPS/PT'
        b'XN8rffj5z74L+fXRd2YudJ/x3h8++2XaHy8uPHD1UInDRLMHkdKUMvnGWzcOf+Aw8bFpy2PRQMn6bzcWlc0p/fnLvpFrD/32E+1HX2ypuH1x9mefL/v8rTVzfr6mWOPg'
        b'8Nb7Td+HzZn1t1/mvPP7r/4Y7nF/wn2zkS3V+pi2xo+avm2d/N2D/M5vP1qeOfi+vNT+4pOg7286nfOPAHdHPdMVXw2ACB5HjqweiuRwjQqdZNtwdxzwSeZ68L7143Ae'
        b'uorLaf63EJ8tfib7C0PVT11lHdZTzCeY74Er/dFpfC4OVweIOfE6/mR0Fx2nLtAH4MtFv/gArM9F9XGJySJOinr4+Di6jRrpA/GoenICCV4BC0mUqoojT1zi4/P46FK5'
        b'+087uiL5sctPPgDzQidDxB2NzXPJZ9e4D/OwkvT0vAJFdnr6ttFv1LM6ijnue0CwMTzOwmFYaGLqRFxqaOWWRs+KV5o0raGtirZpzds6Fh3d2ePVrb7h2aO7sahna2/g'
        b'a/PfsMWx74YmfuhM4K6iaVqzaWt8v3Ngt1O/c2TfS8n9Tsl9i9P6li7rX7z8XaflBN7aNuT3WXsNCzjnFbxhM87Wvi6q3kE/7wux2NVMbzlsz9m6DNo4D9q4PTYRupjp'
        b'LYYtk3gOZoPm1n223sMC8v1jc+u6oGER+Tos5ixsgDChhIQRppQwY4SUEuZA9Nn6DFtQypJSXsNWlLI2tNlQypa9ZkcJe9oUMOxAKUdKeQ87UcqZPehCCVdGuFHC3fDc'
        b'BEp5GKiJlJKxBz0pMYnJ8XgypbxYkzclptAm+fBUSvkY5JBTytcgvh+l/A1UAKUCDe8FUSrY0BZCqVDWQRglwhkxjRIRhuemUyrSIPEMSs1kD86ixEuMeJkSsw1SzaHU'
        b'XJ6BSRSP0vN4BjbRjJ5voL9YwOgYnkHUhYyONdJxjI43vp/A6EQe6zuJkckGMoWRqQZyESMXG8gljEwzkEsZucxALmfkCgO5kpGrDORqRq4xyrWW0esMzemMzDCKqWB0'
        b'ppHOYnS28XUlo3OM07Ce0bmMDhlWMXqDgf1GRuYZZ3UTo/MNzQWMLDSQmxmpNpAaRmqNfesYXWRo3sLIrQaymJHbjJJvZ/QrhuYdjCzhGZZ7J6Pn8g2PR/HZevMNkkYz'
        b'er6xfQGjY/jG9WZ0rIF+HMfoeD5nN2nQ1nvQVk6vnsb/e3+xkj6hNx1ew+fcvFqCmoLed/Urj9dH1zkMOns/dPbrd/Z73zmgXljHqwsZdJ7QYtFk0arosBlw9qsXgadx'
        b'CfzYPrDbod8+Qr9gcMLEllVNqzpEAxMC9XF1WRXJw6acmz/4BDPrR6bWdVmNmo7o7uwHprOe8F82DX/MweVLAWf2ErlYDwuBJFNBH26c3KrpFj4wnfZ3vo2pM3kgwvAU'
        b'kGDCTi5HNtRv6PNMG3Bcqpd+bGpFOljSOrljfrdDt+7GslcXvOHd55f6wHTRE/4UU+fH3BTGZTHPwAZootkGyR6Yuo7wzU39SaOb4Qkgwd+MfcDSdNLYB4AEp8PEXfLA'
        b'1PMrvq3pDNJGn7J+LATy6+EsCc80jvfIduJp876AmAHZwgHb2D7z2G/pSbnyKOc4T+6XnnZx4YadCeshfnr6v7sd8e/EL+unIHl8zFIvJWh5NFyR4K+ZbUDK0Twez/oJ'
        b'B5fH5PJTMfNxcQB3URopUP09NJqv+RncuY0Ezb4fvP3g7Q+PLXs79Ljn/pD9nmVth9tKPSubeIKD3a+u6HTx1AZkWWQ5zjrzpv0Ur6uJ1kdtMmcmOCWYRU/ym7rvF++/'
        b'/uEvj71eq0IbfI6/YXYlyrpy9Y2+36A3uPA458rVjYvS9L+71rlCknsk0tFuhfWUwlBtsK67qFtXqJUUBW+R6PRFsUXd2je0b+jeOPv4TPfVQm2ILlQU5hN2MPbVkc5g'
        b'+3Lejnf6Xq/6TZD8guTLyS7bzH/l4ts42eVNlxkDnGeV77vzwuUWtLo9ETWjPbgyIQHS6hRcS3cRpegyH3eQ335SoOWAa1EzyZZ7UBXaS54ju4I2+I4AteGbMnbkuAG1'
        b'TYKcsBbXksQOMJYA1ZpwlrYCD9yUTTc+8Rlny4S4JN8kEw53JImFfAm+g+6M0E2EI3Eqv3gRYLxG3JnA4cYIpB8hP7xDBxA5iPzM9gSqCUqATP46wLkaSCZrBdxC1GOC'
        b'atE9JyrwZFSFD46+5DbD8JqYc5ov9E3n2M5AvQe6QGvyQQkBqAm1jvJyQ81CdAbvXTdCTmG+hC/kkbJnAq404YQBPHwOH0AXUaWGDjsXMN5uXCkHNjB35Sm2qBrCj9Ui'
        b'wVLgdYTm6yrc42J8wh/V4LsFQayCyuNk+KqI/KzhFk2kpUtQix/qQt0p/riCdgkrge/x8XV005KOC7cnbcS9uAqQaJDv5mnojgHzuuqEqDQ7VT7px3HkfwQ9/gcvmkkU'
        b'iD6HP5/5jMJRVb5Ky+Ao+0bh6D2O7kp+6cqJ7AYt7B9aePRbeBzbOmDhsytmUGhWlrg7sc/G83TkA6H/B0ILgICuHn1Cx2G+mWgV7wOJCyA/D5+HE8L6J4QNTJjWJ3Ed'
        b'lFjWSsulD+ynPJBMHZTYPpS49UvcGqMeSDwGrVweWk3pt5rywMpn0Ny2Nrk8uc9txXvmK5+INwpFM55w5DrMrqtMOXP7XSlfj2yGL05fcHxR8KCDi97MwL7PPvB9CcBS'
        b'uG04yyyc58shX/doUwGW8ODKfOfEIUGeMn9ISA7ODInotsKQME+l0Q4Js1VZcC0ohGaBRqseEmUWa5WaIWFmQUHekECVrx0S5YAfhD9qRf56eFuVX6jTDgmyctVDggJ1'
        b'9pA4R5WnVQKxSVE4JNimKhwSKTRZKtWQIFe5FR4B9mYqjSpfo1XkZymHxLTqmEVPDCoLtZohm00F2TOmp7NN4mzVepV2SKrJVeVo05WkGjhkocvPylWo8pXZ6cqtWUOm'
        b'6ekapZactx4S6/J1GmX205igIZqd8c8+Mhnz8NnGC/mXKTUpcPnhhx/IkWsbHi9XQPz7+Oswvf4Ub0+C2Gsm4ign7jUnadQkwbcS428FhqzT0w3fDRHmW9ec8f/irCy/'
        b'QCsjbcrsZLmEHDfPLsiCEcMXRV4ehMFsgy6TSg7cN4PJVWs1W1Ta3CFxXkGWIk8zZD62pqreyxkKSaykxGzhJfYv2s5WV3Kkom3YFhwWQIx7zBfyhJDCSC12mXwhjoEB'
        b'Dy8240xtDHocD1rd5z/7tSnYp98/flBi/cjMsc8pbMAsvE8Y/oizrnN+j3OlXf0fwCkDQQ=='
    ))))
