#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-

import os
import csv
import codecs
from collections import OrderedDict
from feature_extracters import extract_features


class Chapter(object):
    """
    Class for storing a chapter with tokenized paragraphs, character list, 
    extracted features, and quote attributions, etc.
    """

    def __init__(self, story_file, char_file, tmp_dir, book_nlp, ans_file=None):
        super(Chapter, self).__init__()

        self.story_file = story_file
        self.char_file = char_file
        self.ans_file = ans_file
        self.tmp_dir = tmp_dir
        self.char_tmp = os.path.join(self.tmp_dir, 'char_tmp.txt')
        self.story_tmp = os.path.join(self.tmp_dir, 'story_tmp.txt')
        self.token_tmp = os.path.join(self.tmp_dir, 'token_tmp.txt')
        self.booknlp_tmp = os.path.join(self.tmp_dir, 'booknlp_output')
        self.booknlp_log = os.path.join(self.tmp_dir, 'booknlp.log')
        self.paragraph_num = 0
        self.tokens = []
        self.paragraph_start_token_id = []
        self.paragraph_end_token_id = []
        self.paragraph_has_quote = []
        self.paragraph_quote_token_id = []
        self.max_name_len = 0
        self.characters = OrderedDict()
        self.character_appear_token_id = {}
        self.character_num = 0

        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        self.read_characters()
        self.preprocess_story()
        # run book-nlp
        os.system('sh run-booknlp.sh {} {} {} {} {}'.format(book_nlp, 
            self.story_tmp, self.booknlp_tmp, self.token_tmp, self.booknlp_log))
        self.read_booknlp_tokens_file()
        self.find_paragraph_quote_token_id()
        self.find_character_appear_token_id()

    def read_characters(self):
        """
        Read and preprocess character list file.

        For the sake of book-nlp tokenization, change the coreference annotation
        marks to ccc_CHARACTER_ccc.

        TODO: Relieve the need for this function by trying to use customized 
              dictionary in tokenization
        """
        print("Reading Character File ... ")
        self.t_characters = {}
        self.ciph_characters = {}
        with codecs.open(self.char_tmp, 'w') as outf:
            with codecs.open(self.char_file) as f:
                for _line in f:
                    line = _line.strip()
                    if len(line) > 0:
                        l = line.split(';')
                        # new coreference annotation mark
                        ciph_char = 'ccc_' + l[0][3:-1] + '_ccc'
                        self.t_characters[l[0]] = ciph_char
                        self.ciph_characters[ciph_char] = l[0]
                        l[0] = ciph_char

                        # output to the tmp file
                        outf.write(';'.join(l) + '\n') 

                        # Some times the name might be separated. Store splited 
                        # name list to handle this situation in processing the 
                        # tokens
                        c = l[0].lower().strip()
                        cnames = []
                        cnames.append(c.split())
                        if len(c.split()) > self.max_name_len:
                            self.max_name_len = len(c.split())
                        for name in l[2:]:
                            nl = name.lower().strip().split()
                            if len(nl) > self.max_name_len:
                                self.max_name_len = len(nl)
                            cnames.append(nl)

                        # Get gender
                        if len(l) > 1:
                            gender = l[1].strip().lower()
                        else:
                            gender = '<UNK>'
                        
                        # Store character name and gender
                        self.characters[c] = (gender, cnames)
        self.character_num = len(self.characters)
        print("Done. ({} characters)".format(self.character_num))

    def preprocess_story(self):
        """
        Replace the original text with ciphered coreference annotation marks
        """
        with codecs.open(self.story_tmp, 'w') as outf:
            with codecs.open(self.story_file) as f:
                f_csv = csv.reader(f)
                headers = next(f_csv)
                for line in f_csv:
                    text = line[3]
                    # annotate with new marks
                    for c in self.t_characters:
                        text = text.replace(c, self.t_characters[c])
                    text_split = text.split()
                    
                    # remove the mention before the coreference annotation marks
                    new_text_split = []
                    for i, t in enumerate(text_split[:-1]):
                        if text_split[i+1] not in self.ciph_characters:
                            new_text_split.append(t)

                    # save into the temporary file
                    outf.write(' '.join(new_text_split)+'\n\n')

    def read_booknlp_tokens_file(self): 
        """Read book-nlp tokens output file"""
        print("Reading Tokens File ... {}".format(self.token_tmp))
        with codecs.open(self.token_tmp) as f:
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
                # Save token
                self.tokens.append([paragraphId, sentenceID, tokenId, beginOffset, endOffset, whitespaceAfter, headTokenId, originalWord, normalizedWord, lemma, pos, ner, deprel, inQuotation, characterId, supersense])

                # Get the paragraph start and end token id
                if paragraphId >= len(self.paragraph_start_token_id):
                    self.paragraph_start_token_id.append(tokenId)
                    self.paragraph_end_token_id.append(tokenId)
                    self.paragraph_has_quote.append(False)

                # Check whether the paragraph contains quotes
                if inQuotation != 'O':
                    self.paragraph_has_quote[-1] = True

                self.paragraph_end_token_id[-1] = tokenId

        self.paragraph_num = len(self.paragraph_start_token_id)
        print("Done. (" + str(len(self.tokens)) + " tokens, " + str(self.paragraph_num) + " paragraphs)")

    def find_paragraph_quote_token_id(self):
        """
        Find the quotes in paragraphs
        """
        print("Find quotes in paragraphs ... ")
        num_quote = 0
        for i in range(self.paragraph_num):
            self.paragraph_quote_token_id.append([])
            if self.paragraph_has_quote[i]:
                j = self.paragraph_start_token_id[i]
                state = False
                while j < len(self.tokens) and i == self.tokens[j][0]:
                    if self.tokens[j][13] != 'O' and state == False:
                        state = True
                        self.paragraph_quote_token_id[i].append(j)
                    if state == True:
                        if self.tokens[j][13] == 'O':
                            state = False
                            self.paragraph_quote_token_id[i].append(j - 1)
                            num_quote += 1
                        elif j == len(self.tokens) - 1 or i != self.tokens[j+1][0]:
                            state = False
                            self.paragraph_quote_token_id[i].append(j)
                            num_quote += 1
                    j += 1
        print("Done. ({} quotes)".format(num_quote))

    def find_character_appear_token_id(self):
        """
        Find the token ids of character mentions
        """
        print('Find character mention token ids ... ')
        for c in self.characters:
            self.character_appear_token_id[c] = []
        i = 0
        mentions = 0
        while i < len(self.tokens):
            find = False
            # try to match name mentions as long as possible 
            for j in range(self.max_name_len-1, -1, -1):
                # skip if overflow
                if i+j >= len(self.tokens) or self.tokens[i][0] != self.tokens[i+j][0]:
                    continue
                for c in self.characters:
                    for cname in self.characters[c][1]:
                        if len(cname) == j + 1:
                            mark = True
                            for wi in range(j+1):
                                word = cname[wi]
                                if word != self.tokens[i+wi][7].lower():
                                    mark = False
                                    break
                            if mark == True:
                                # found a mention
                                find = True
                                self.character_appear_token_id[c].append(i)
                                mentions += 1
                                break
                if find == True:
                    i += j
                    break
            i += 1
        print('Done. ({} mentions)'.format(mentions))

    def extract_features(self, args, features):
        print('Extracting features ... ')
        input = {
            'tokens': self.tokens,
            'args': args,
            'paragraph_num': self.paragraph_num,
            'paragraph_start_token_id': self.paragraph_start_token_id,
            'paragraph_end_token_id': self.paragraph_end_token_id,
            'paragraph_has_quote': self.paragraph_has_quote,
            'paragraph_quote_token_id': self.paragraph_quote_token_id,
            'character_appear_token_id': self.character_appear_token_id,
            'character_num': self.character_num,
            'characters': self.characters
        } 
        self.quote_features = extract_features(features, input)
        print('Done.')

    def output_svmrank_format(self, outputfile, answer=None):
        print('Writing svmrank input file ... ')
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
            for i in range(self.paragraph_num):
                if self.paragraph_has_quote[i]:
                    qp += 1

            print("(" + str(qp) + " paragraphs have quote)")
            
            ss = 0
            for i in range(self.paragraph_num):
                if self.paragraph_has_quote[i]:
                    ss += 1
                    f.write('# paragraph ' + str(i) + ': ' + str(self.paragraph_start_token_id[i]) + "--" + str(self.paragraph_end_token_id[i]) + ' ')
                    for quoteTokenId in self.paragraph_quote_token_id[i]:
                        f.write(str(quoteTokenId) + ' ')
                    f.write('\n')

                    ans_char = None
                    if answer is not None:
                        if ss > len(answers):
                            break

                        c = answers[ss-1][0]
                        sent = answers[ss-1][1].split()

                        lll = len(self.tokens[self.paragraph_quote_token_id[i][0]+1][7])
                        ans = sent[0][:lll]
                        now = self.tokens[self.paragraph_quote_token_id[i][0]+1][7].lower()

                        if ans != now:
                            ss -= 1
                            continue
                        
                        nn = 0
                        for tc in self.characters:
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
                            
                    for j in range(self.character_num):
                        if ans_char is not None and ans_char == self.characters.keys()[j]:
                            f.write('1\t')
                        else:
                            f.write('0\t')
                        f.write('qid:' + str(ss))
                        for k, feature in enumerate(list(self.quote_features[i][j].keys())):
                            f.write('\t' + str(k+1) + ':' + str(self.quote_features[i][j][feature]))
                        f.write('\n')
        print('Done.')
