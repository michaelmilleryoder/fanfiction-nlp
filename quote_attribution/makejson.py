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
quotes = []

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
                paragraphId = int(l[2][:-1])
                rng = l[3].split('--')
                startId = int(rng[0])
                endId = int(rng[1])
                qtype = l[4][5:]
                quoteTokenIds = l[5:]
                for i in range(0, len(quoteTokenIds), 2):
                    quoteStart = int(quoteTokenIds[i])
                    quoteEnd = int(quoteTokenIds[i+1])
                    paragraph2quotes[ss].append((quoteStart, quoteEnd, qtype, paragraphId, startId, endId))
                ss += 1

    with codecs.open(predictfile) as f:
        scores = []
        for line in f:
            scores.append(float(line.strip()))

    ss = 0
    for i in range(0, len(scores), character_num):
        #print(' '.join(tokens[quoteStart: quoteEnd+1]))
        #for j in range(character_num):
        #    print(scores[i+j], characters[j])
        maxid = np.argmax(scores[i: i+character_num])
        guess_char = characters[maxid][4:-4]
        quote = {}
        quote['speaker'] = guess_char
        quote['quotes'] = []
        for quoteStart, quoteEnd, quoteType, paragraphId, startId, endId in paragraph2quotes[ss]:
            quote['paragraph'] = paragraphId
            quote['type'] = quoteType
            quote['start'] = startId
            quote['end'] = endId
            quote['quotes'].append({})
            quote['quotes'][-1]['start'] = quoteStart
            quote['quotes'][-1]['end'] = quoteEnd
            quote['quotes'][-1]['quote'] = ' '.join(tokens[quoteStart: quoteEnd+1])
            for c in characters:
                quote['quotes'][-1]['quote'] = ' '.join(quote['quotes'][-1]['quote'].replace(c, '').split())
            char2quotes[characters[maxid]].append(quote['quotes'][-1]['quote'])
        quote['replyto'] = -1
        if quote['type'] == 'Explicit' and len(quotes) > 0 and quote['paragraph'] - quotes[-1]['paragraph'] <= 2 and quote['start'] - quotes[-1]['end'] <= 200:
            quote['replyto'] = quotes[-1]['paragraph']
        quotes.append(quote)
        ss += 1

    with codecs.open(outputfile, 'w') as f:
        #json.dump(char2quotes, f)
        json.dump(quotes, f)
