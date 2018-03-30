#!/usr/bin/python
# -*- coding: utf-8 -*-
# tuple (probable_word_list, flag = 0 if symptom, flag = 1 if medicine)

from __init__ import spellMed, spellSymp, spellEnglish
from itertools import chain


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

            # print "exact", result, word

            if result is not -1:
                if word in result:
                    return word.encode('utf-8')

        for word in wordlist:  # search in english
            result = spellEnglish(word.encode('utf-8'))

            # print result, word

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
    a = findWord(wordlist, flag)
    for word in a:
        word = word.encode('utf-8')
    b = concatSlash(a)
    return b.encode('utf-8')



			