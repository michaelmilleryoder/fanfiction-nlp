# -*- coding: utf-8 -*-
import os
import math
import json
import copy
import codecs
import argparse
from collections import OrderedDict
from pprint import pprint


tokens = []
paragraphStartTokenId = []
paragraphEndTokenId = []
paragraphFeatures = []
paragraphHasQuote = []
paragraphQuoteTokenId = []
paragraphNum = 0
characters = OrderedDict()
max_name_len = 0
characterAppearTokenId = {}
characterNum = 0


def build_character_appear_token_id():
    global max_name_len
    global characterAppearTokenId
    for c in characters:
        characterAppearTokenId[c] = []
    i = 0
    while i < len(tokens):
        find = False
        for j in range(max_name_len-1, -1, -1):
            if i+j >= len(tokens) or tokens[i][0] != tokens[i+j][0]:
                continue
            for c in characters:
                for cname in characters[c][1]:
                    if len(cname) == j + 1:
                        bj = True
                        for wi in range(j+1):
                            word = cname[wi]
                            if word != tokens[i+wi][7].lower():
                                bj = False
                                break
                        if bj == True:
                            find = True
                            characterAppearTokenId[c].append(i)
                            break
            if find == True:
                i += j
                break
        i += 1


def paragraph_quote_token_id():
    for i in range(paragraphNum):
        paragraphQuoteTokenId.append([])
        if paragraphHasQuote[i]:
            j = paragraphStartTokenId[i]
            state = False
            while j < len(tokens) and i == tokens[j][0]:
                if tokens[j][13] != 'O' and state == False:
                    state = True
                    paragraphQuoteTokenId[i].append(j)
                if state == True:
                    if tokens[j][13] == 'O':
                        state = False
                        paragraphQuoteTokenId[i].append(j - 1)
                    elif j == len(tokens) - 1 or i != tokens[j+1][0]:
                        state = False
                        paragraphQuoteTokenId[i].append(j)
                j += 1
    #print paragraphQuoteTokenId


def read_tokens_file(tokenfile):
    global paragraphFeatures
    global paragraphNum
    print "Reading Tokens File ... ",
    with codecs.open(tokenfile) as f:
        next(f)
        for line in f:
            paragraphId, sentenceID, tokenId, beginOffset, endOffset, whitespaceAfter, headTokenId, originalWord, normalizedWord, lemma, pos, ner, deprel, inQuotation, characterId, supersense = line.strip().split('\t')
            paragraphId = int(paragraphId)
            sentenceID = int(sentenceID)
            tokenId = int(tokenId)
            beginOffset = int(beginOffset)
            endOffset = int(endOffset)
            headTokenId = int(headTokenId)
            characterId = int(characterId)
            tokens.append([paragraphId, sentenceID, tokenId, beginOffset, endOffset, whitespaceAfter, headTokenId, originalWord, normalizedWord, lemma, pos, ner, deprel, inQuotation, characterId, supersense])

            if paragraphId >= len(paragraphStartTokenId):
                paragraphStartTokenId.append(tokenId)
                paragraphEndTokenId.append(tokenId)
                paragraphHasQuote.append(False)

            if inQuotation != 'O':
                paragraphHasQuote[-1] = True

            paragraphEndTokenId[-1] = tokenId

    paragraphNum = len(paragraphStartTokenId)
    print "Done. (" + str(len(tokens)) + " tokens, " + str(paragraphNum) + " paragraphs)"

'''
def read_output_file(outfile):
    with codecs.open(outfile) as f:
        data = json.load(f)
        t_characters = data['characters']
        for c in t_characters:
            t_id = int(c['id'])
            t_names = c['names']
            characters[t_id] = []
            for t_name in t_names:
                characters[t_id].append(t_name['n'])
            #print(characters[t_id])
'''

def read_character_file(charfile):
    global characters
    global max_name_len
    global characterNum
    global paragraphNum
    global paragraphFeatures
    print "Reading Character File ... ",
    with codecs.open(charfile) as f:
        for _line in f:
            line = _line.strip()
            if len(line) > 0:
                l = line.split(';')
                c = l[0].lower().strip()
                cnames = []
                cnames.append(c.split())
                if len(c.split()) > max_name_len:
                    max_name_len = len(c.split())
                for name in l[2:]:
                    nl = name.lower().strip().split()
                    if len(nl) > max_name_len:
                        max_name_len = len(nl)
                    cnames.append(name.lower().strip().split())
                if len(l) > 1:
                    characters[c] = (l[1].strip().lower(), cnames)
                else:
                    characters[c] = ('<UNK>', cnames)
    characterNum = len(characters)
    for i in range(paragraphNum):
        paragraphFeatures.append([])
        for j in range(characterNum):
            paragraphFeatures[-1].append({})
    print "Done. (" + str(characterNum) + " characters)"
    #print characters


def output_svmrank_format(outputfile, features, answer=None,):
    answers = []

    output_abs_path = os.path.abspath(outputfile)
    output_father_path = os.path.abspath(os.path.dirname(output_abs_path) + os.path.sep + ".")
    if not os.path.exists(output_father_path):
        os.makedirs(output_father_path)

    if answer is not None:
        with codecs.open(answer) as f:
            for line in f:
                l = line.split('\t')
                answers.append((l[1].lower(), l[2].lower()))

    with codecs.open(outputfile, 'w') as f:
        qp = 0
        for i in range(paragraphNum):
            if paragraphHasQuote[i]:
                qp += 1

        print "(" + str(qp) + " paragraphs have quote)",
        #f.write('# ' + str(qp) + ' quote paragraphs, ' + str(characterNum) + ' characters, features: ')
        #for feature in features:
        #    f.write(feature + ' ')
        #f.write('\n')
        #for idx in range(characterNum):
            #cnames = characters[characters.keys()[idx]][1]
            #f.write('# ' + str(idx) + " : ")
            #for name in cnames:
            #    f.write(' '.join(name) + '; ')
            #f.write('\n')

        ss = 0
        for i in range(paragraphNum):
            if paragraphHasQuote[i]:
                ss += 1
                f.write('# paragraph ' + str(i) + ': ' + str(paragraphStartTokenId[i]) + "--" + str(paragraphEndTokenId[i]) + ' ')
                for quoteTokenId in paragraphQuoteTokenId[i]:
                    f.write(str(quoteTokenId) + ' ')
                f.write('\n')
                #print '# paragraph ' + str(i) + ': ' + str(paragraphStartTokenId[i]) + "--" + str(paragraphEndTokenId[i])
                #print ss
                #print len(answers)
                ans_char = None
                if answer is not None:
                    if ss > len(answers):
                        break

                    c = answers[ss-1][0]
                    sent = answers[ss-1][1].split()

                    lll = len(tokens[paragraphQuoteTokenId[i][0]+1][7])
                    ans = sent[0][:lll]
                    now = tokens[paragraphQuoteTokenId[i][0]+1][7].lower()

                    if ans != now:
                        ss -= 1
                        continue
                    
                    nn = 0
                    for tc in characters:
                        if tc == c:
                            nn += 1
                    '''
                    if nn < 1:
                        print c
                        print "No char found!"
                    elif nn > 1:
                        print "More char found!"
                    '''
                    if nn == 1:
                        ans_char = c
                        #print '# paragraph ' + str(i) + ': ' + str(paragraphStartTokenId[i]) + "--" + str(paragraphEndTokenId[i]) + ' ' + ans_char +'\n'
                    #else:
                    #    ss -= 1
                    #    continue
                        
                for j in range(characterNum):
                    if ans_char is not None and ans_char == characters.keys()[j]:
                        f.write('1\t')
                    else:
                        f.write('0\t')
                    f.write('qid:' + str(ss))
                    for k in range(len(features)):
                        f.write('\t' + str(k+1) + ':' + str(paragraphFeatures[i][j][features[k]]))
                    #if ans_char == characters.keys()[j]:
                    #    f.write('\t2:1')
                    #else:
                    #    f.write('\t2:0')
                    f.write('\n')
            

def extract_feature_disttoutter():
    if (len(paragraphQuoteTokenId) == 0):
        paragraph_quote_token_id()
    if (len(characterAppearTokenId) == 0):
        build_character_appear_token_id()
    for i in range(paragraphNum):
        if paragraphHasQuote[i]:
            for j in range(characterNum):
                char = characters.keys()[j]
                dist = len(tokens)
                pid = 0
                while pid < len(paragraphQuoteTokenId[i]):
                    startId = paragraphQuoteTokenId[i][pid]
                    endId = paragraphQuoteTokenId[i][pid+1]
                    for cid in characterAppearTokenId[char]:
                        if (not(startId <= cid and endId >= cid)):
                            if abs(startId - cid) < dist:
                                dist = abs(startId - cid)
                            if abs(endId - cid) < dist:
                                dist = abs(endId - cid)
                    pid += 2
                #paragraphFeatures[i][j]['disttoutter'] = math.log(dist+1)
                paragraphFeatures[i][j]['disttoutter'] = 1.0 / (dist + 1)
            

def extract_feature_spkappcnt():
    if (len(paragraphQuoteTokenId) == 0):
        paragraph_quote_token_id()
    if (len(characterAppearTokenId) == 0):
        build_character_appear_token_id()
    for i in range(paragraphNum):
        if paragraphHasQuote[i]:
            for j in range(characterNum):
                char = characters.keys()[j]
                count = len(characterAppearTokenId[char])
                paragraphFeatures[i][j]['spkappcnt'] = math.log(count+0.0001)
    

def extract_feature_nameinuttr():
    if (len(paragraphQuoteTokenId) == 0):
        paragraph_quote_token_id()
    if (len(characterAppearTokenId) == 0):
        build_character_appear_token_id()
    for i in range(paragraphNum):
        if paragraphHasQuote[i]:
            for j in range(characterNum):
                char = characters.keys()[j]
                appear = 0
                pid = 0
                while pid < len(paragraphQuoteTokenId[i]):
                    startId = paragraphQuoteTokenId[i][pid]
                    endId = paragraphQuoteTokenId[i][pid+1]
                    for cid in characterAppearTokenId[char]:
                        if (startId <= cid and endId >= cid):
                            appear = 1
                    pid += 2
                paragraphFeatures[i][j]['nameinuttr'] = appear


def extract_feature_spkcntpar():
    if (len(paragraphQuoteTokenId) == 0):
        paragraph_quote_token_id()
    if (len(characterAppearTokenId) == 0):
        build_character_appear_token_id()
    for i in range(paragraphNum):
        if paragraphHasQuote[i]:
            parStart = paragraphStartTokenId[i]
            parEnd = paragraphEndTokenId[i]
            for j in range(characterNum):
                char = characters.keys()[j]
                parCnt = 0
                quoCnt = 0
                pid = 0
                for cid in characterAppearTokenId[char]:
                    if (parStart <= cid and parEnd >= cid):
                        parCnt += 1
                while pid < len(paragraphQuoteTokenId[i]):
                    startId = paragraphQuoteTokenId[i][pid]
                    endId = paragraphQuoteTokenId[i][pid+1]
                    for cid in characterAppearTokenId[char]:
                        if (startId <= cid and endId >= cid):
                            quoCnt += 1
                    pid += 2
                paragraphFeatures[i][j]['spkcntpar'] = parCnt - quoCnt


def extract_feature_neighboring_utterances(before, after):
    global paragraphFeatures
    global paragraphHasQuote
    newfeatures = copy.deepcopy(paragraphFeatures)
    for i in range(len(paragraphFeatures)):
        for j in range(len(paragraphFeatures[i])):
            pointer = i - 1
            kk = 0
            nowkeys = copy.deepcopy(newfeatures[i][j].keys())
            while pointer >= 0 and kk < before:
                if paragraphHasQuote[pointer]:
                    for key in nowkeys:
                        newkey = key+'-'+str(1+kk)
                        newfeatures[i][j][newkey] = paragraphFeatures[pointer][j][key]
                    kk += 1
                pointer -= 1
            if kk != before:
                for k in range(kk, before):
                    for key in nowkeys:
                        newkey = key+'-'+str(1+k)
                        newfeatures[i][j][newkey] = 0.0
            pointer = i + 1
            kk = 0
            while pointer < len(paragraphFeatures) and kk < after:
                if paragraphHasQuote[pointer]:
                    for key in nowkeys:
                        newkey = key+'+'+str(1+kk)
                        newfeatures[i][j][newkey] = paragraphFeatures[pointer][j][key]
                    kk += 1
                pointer += 1
            if kk != after:
                for k in range(kk, before):
                    for key in nowkeys:
                        newkey = key+'+'+str(1+k)
                        newfeatures[i][j][newkey] = 0.0
    paragraphFeatures = copy.deepcopy(newfeatures)

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    #parser.add_argument('--quotefile', help='Path to the book.id.quote.cands file', required=True)
    parser.add_argument('--tokenfile', help='Path to the token file', required=True)
    #parser.add_argument('--outfile', help='Path to the book.id.book file', required=True)
    parser.add_argument('--charfile', help='Path to the character list file', required=True)
    parser.add_argument('--output', help='Path to the output file', required=True)
    parser.add_argument('--features', help='A list of features to be extracted, separated using commas. \n Choices: disttoutter - Distance to Utterance; spkappcnt - Speaker Appearance Count; nameinuttr - Speaker Name in Utterance; spkcntpar - Speaker Count in the Paragraph', required=True)
    parser.add_argument('--answer', help='Path to the answer file')
    #parser.add_argument('--test', action='store_true')
    opt = parser.parse_args()

    #quotefile = opt.quotefile
    tokenfile = opt.tokenfile
    #outfile = opt.outfile
    charfile = opt.charfile
    output = opt.output
    features = opt.features.split(',')
    answer = None
    if hasattr(opt, 'answer'):
        answer = opt.answer
    #test = opt.test
    
    read_tokens_file(tokenfile)
    read_character_file(charfile)
    #read_output_file(outfile)
    
    if 'disttoutter' in features:
        print "Extracting 'Distance to Utterance' ... ",
        extract_feature_disttoutter()
        print "Done."
    if 'spkappcnt' in features:
        print "Extracting 'Speaker Appearance Count' ... ",
        extract_feature_spkappcnt()
        print "Done."
    if 'nameinuttr' in features:
        print "Extracting 'Speaker Name in Utterance' ... ",
        extract_feature_nameinuttr()
        print "Done."
    if 'spkcntpar' in features:
        print "Extracting 'Speaker Count in the Paragraph' ... ",
        extract_feature_spkcntpar()
        print "Done."

    extract_feature_neighboring_utterances(4,4)

    print "Output ...",
    #output_svmrank_format(output, ['disttoutter', 'spkappcnt',
    #                               'disttoutter-1','disttoutter-2','disttoutter-3','disttoutter-4',
    #                               'disttoutter+1','disttoutter+2','disttoutter+3','disttoutter+4'], answer=answer)
    output_features = list(features)
    #for f in features:
    #    output_features.append(f + '-1')
    #    output_features.append(f + '+1')
    output_svmrank_format(output, output_features, answer=answer)
    print "Done."

