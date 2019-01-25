# -*- coding: utf-8 -*-
import codecs
import argparse
import json


tokens = []
characters = []


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--quote', help='Path to the quote attribution file', required=True)
    parser.add_argument('--featurefile', help='Path to the extracted feature file', required=True)
    parser.add_argument('--tokenfile', help='Path to the token file', required=True)
    parser.add_argument('--booknlpout', help='Path to the book.id.book file', required=True)
    parser.add_argument('--output', help='Path to the svm-rank format file', required=True)
    opt = parser.parse_args()

    quote = opt.quote
    tokenfile = opt.tokenfile
    output = opt.output
    booknlpout = opt.booknlpout
    featurefile = opt.featurefile

    '''
    with codecs.open(tokenfile) as f:
        next(f)
        for line in f:
            paragraphId, sentenceID, tokenId, beginOffset, endOffset, whitespaceAfter, headTokenId, originalWord, normalizedWord, lemma, pos, ner, deprel, inQuotation, characterId, supersense = line.strip().split('\t')
            tokens.append((originalWord, inQuotation))
    '''

    with codecs.open(featurefile) as f:
        metaline = next(f)
        metadata = metaline.split()
        paranum = int(metadata[1])
        characternum = int(metadata[4])
        for line in f:
            if len(line.strip()) == 0:
                continue
            if line[0] == '#':
                parmeta = line.split()
                parid = int(parmeta[2].strip(':'))
                
    with codecs.open(booknlpout) as f:
        t_characters = json.load(f)["characters"]

    ss = 0
    for c in t_characters:
        cid = int(c['id'])
        assert ss == cid
        names = []
        for name in c['names']:
            names.append(name['n'])
        characters.append(set(names))
        ss += 1
    assert len(characters) == characternum

    for c in characters:
        print c
