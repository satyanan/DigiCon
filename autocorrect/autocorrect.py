#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Spell function

"""
from itertools import chain
from itertools import izip
from nlp_parser import NLP_COUNTS, MED_COUNTS
from word import Word, common, exact, known, get_case, \
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




def concatSlash(*args):
    """reversed('th'), 'e' => 'hte'"""

    try:
        return '/'.join(args)
    except TypeError:
        return '/'.join(chain.from_iterable(args))


def findWord(wordlist, flag):
    if flag is 0:
        for word in wordlist:
            result = spellSymp(word.encode('utf-8'))

            # print result, word

            if result is not -1:
                if word in result:
                    return word.encode('utf-8')

        for word in wordlist:
            result = spellEnglish(word.encode('utf-8'))

            # print result, word

            if result is not -1:
                if word in result:
                    return word.encode('utf-8')

        for word in wordlist:
            result = spellSymp(word.encode('utf-8'))
            if result is not -1:
                return result

        for word in wordlist:
            result = spellEnglish(word.encode('utf-8'))
            if result is not -1:
                return result

        return wordlist[0].encode('utf-8')
    elif flag is 1:

        for word in wordlist:  # exact match with medicine
            result = spellMed(word.encode('utf-8'))
            if result is not -1:
                if word in result:
                    return word.encode('utf-8')

        for word in wordlist:  # search in english
            result = spellEnglish(word.encode('utf-8'))
            if result is not -1:
                if word in result:
                    return word.encode('utf-8')

        for word in wordlist:  # match with medicine
            result = spellMed(word.encode('utf-8'))
            if result is not -1:
                return result

        for word in wordlist:
            result = spellEnglish(word.encode('utf-8'))
            if result is not -1:
                return result

        return wordlist[0].encode('utf-8')


def correctWord(wordlist, flag):
    if len(wordlist) < 3 or flag == -1:
        return wordlist
    c = []
    c.append(wordlist)
    a = findWord(c, 1)
    b = concatSlash(a)
    return b.encode('utf-8')


def correctSent(sentence, flag):
    wordlist = sentence.split()
    result = ''
    for word in wordlist:
        result += correctWord(word, flag) + ' '

    return result

def correctPage(sentenceList, flagList):
    page = []
    for sentence, flag in izip(sentenceList, flagList):
        page.append(correctSent(sentence, flag))

    return page