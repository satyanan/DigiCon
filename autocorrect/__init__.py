#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Spell function

"""

from autocorrect.nlp_parser import NLP_COUNTS, MED_COUNTS
from autocorrect.word import Word, common, exact, known, get_case, \
    isMedicine, isSymptom, isEnglish


def spell(word):
    """most likely correction for everything up to a double typo"""

    w = Word(word)
    candidates = common([word]) or exact([word]) or known([word]) \
        or known(w.typos()) or common(w.double_typos())

    if len(candidates) is 0:
        return -1
    correction = max(candidates, key=NLP_COUNTS.get)
    print candidates
    return get_case(word, correction)


def spellMed(word):
    w = Word(word)

    candidates = isMedicine([word])

    if len(candidates) != 0:
        for x in candidates:
            x = x.encode('utf-8')
        return max(candidates, key=MED_COUNTS.get).encode('utf-8')

    candidates = isMedicine(w.typos())

    if len(candidates) is not 0:
        for x in candidates:
            x = x.encode('utf-8')
        return max(candidates, key=MED_COUNTS.get).encode('utf-8')

    candidates = isMedicine(w.double_typos())

    if len(candidates) is not 0:
        for x in candidates:
            x = x.encode('utf-8')
        return max(candidates, key=MED_COUNTS.get).encode('utf-8')

    # candidates = (isMedicine([word]) or isMedicine(w.typos()) or isMedicine(w.double_typos()))

    if len(candidates) is 0:
        return -1


def spellSymp(word):

    w = Word(word)

    candidates = isSymptom([word])

    if len(candidates) is not 0:
        return candidates

    candidates = isSymptom(w.typos())

    if len(candidates) is not 0:
        return candidates

    candidates = isSymptom(w.double_typos())

    if len(candidates) is not 0:
        return candidates

    # candidates = (isMedicine([word]) or isMedicine(w.typos()) or isMedicine(w.double_typos()))

    if len(candidates) is 0:
        return -1


def spellEnglish(word):

    w = Word(word)

    candidates = isEnglish([word])

    if len(candidates) is not 0:
        return max(candidates, key=NLP_COUNTS.get).encode('utf-8')

    candidates = isEnglish(w.typos())

    if len(candidates) is not 0:
        return max(candidates, key=NLP_COUNTS.get).encode('utf-8')

    candidates = isEnglish(w.double_typos())

    if len(candidates) is not 0:
        return max(candidates, key=NLP_COUNTS.get).encode('utf-8')

    # candidates = (isMedicine([word]) or isMedicine(w.typos()) or isMedicine(w.double_typos()))

    if len(candidates) is 0:
        return -1



			