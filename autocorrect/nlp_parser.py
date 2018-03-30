#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
NLP parser

"""

from _utils import words_from_archive, zero_default_dict


def parse(lang_sample):
    """tally word popularity using novel extracts, etc"""

    words = words_from_archive(lang_sample, include_dups=True)
    counts = zero_default_dict()
    for word in words:
        counts[word] += 1
    return (set(words), counts)


(NLP_WORDS, NLP_COUNTS) = parse('big.txt')
(MED_WORDS, MED_COUNTS) = parse('medCorpus.txt')

# parse('big.txt')


			