# -*- coding: utf-8 -*-
import os
import json
import numpy as np
import codecs
import argparse

tokens = []
characters = []
paragraph2quotes = []
char2quotes = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--svmfile', help='Path to the svm input file', required=True)
    parser.add_argument('--charfile', help='Path to the character list file', required=True)
    parser.add_argument('--tokenfile', help='Path to the token file', required=True)
    parser.add_argument('--predictfile', help='Path to the prediction file', required=True)
    parser.add_argument('--outputfile', help='Path to the output file', required=True)
    opt = parser.parse_args()
    svmfile = opt.svmfile
    charfile = opt.charfile
    tokenfile = opt.tokenfile
    predictfile = opt.predictfile
    outputfile = opt.outputfile

    with codecs.open(tokenfile) as f:
        next(f)
        for line in f:
            paragraphId, sentenceID, tokenId, beginOffset, endOffset, whitespaceAfter, headTokenId, originalWord, normalizedWord, lemma, pos, ner, deprel, inQuotation, characterId, supersense = line.strip().split('\t')
            tokens.append(originalWord)

    with codecs.open(charfile) as f:
        for _line in f:
            line = _line.strip()
            if len(line) > 0:
                l = line.split(';')
                characters.append(l[0])
                char2quotes[l[0]] = []

    character_num = len(characters)

    ss = 0
    with codecs.open(svmfile) as f:
        for line in f:
            if line[0] == '#':
                paragraph2quotes.append([])
                l = line.split()
                rng = l[3].split('--')
                startId = int(rng[0])
                endId = int(rng[1])
                quoteTokenIds = l[4:]
                for i in range(0, len(quoteTokenIds), 2):
                    quoteStart = int(quoteTokenIds[i])
                    quoteEnd = int(quoteTokenIds[i+1])
                    paragraph2quotes[ss].append((quoteStart, quoteEnd))
                ss += 1

    with codecs.open(predictfile) as f:
        scores = []
        for line in f:
            scores.append(float(line.strip()))

    ss = 0
    if len(scores) > 0 and character_num > 0:
        for i in range(0, len(scores), character_num):
            maxid = np.argmax(scores[i: i+character_num])
            for quoteStart, quoteEnd in paragraph2quotes[ss]:
                char2quotes[characters[maxid]].append(' '.join(tokens[quoteStart: quoteEnd+1]))
            ss += 1

    with codecs.open(outputfile, 'w') as f:
        json.dump(char2quotes, f)
