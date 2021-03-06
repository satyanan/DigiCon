#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Word lists for case sensitive/insensitive lookups

"""

from _utils import words_from_archive

# en_US_GB_CA is a superset of US, GB and CA
# spellings (color, colour, etc). It contains
# roughly half a million words. For this
# example, imagine it's just seven words...
#
# we (lower)
# flew (lower)
# to (lower)
# Abu (mixed)
# Dhabi (mixed)
# via (lower)
# Colombo (mixed)

LOWERCASE = words_from_archive('en_US_GB_CA_lower.txt')

# {'we', 'flew', 'to', 'via'}

CASE_MAPPED = words_from_archive('en_US_GB_CA_mixed.txt', map_case=True)

MEDICINE = words_from_archive('Medicines.txt')
SYMPTOMS = words_from_archive('Symptoms.txt')
ENGLISH = words_from_archive('english.txt')

#  {abu': 'Abu',
#  'dhabi': 'Dhabi',
#  'colombo': 'Colombo'}
#
# Note that en_US_GB_CA_mixed.txt also contains
# acronyms/mixed case variants of common words,
# so in reality, CASE_MAPPED also contains:
#
# {'to': 'TO',
#  'via': 'Via'}

MIXED_CASE = set(CASE_MAPPED.values())

# {'Abu', 'Dhabi', 'Colombo'}

LOWERED = set(CASE_MAPPED.keys())

# {'abu', 'dhabi', 'colombo'}

			