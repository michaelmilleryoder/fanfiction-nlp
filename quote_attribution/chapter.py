#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-

import os
import json
import numpy as np
import csv
import codecs
from tokens import Token
from collections import OrderedDict
from feature_extracters import extract_features


class Chapter(object):
    """
    Class for storing a chapter with tokenized paragraphs, character list, 
    extracted features, and quote attributions, etc.
    """

    def __init__(self):
        super(Chapter, self).__init__()

    @classmethod
    def read_with_booknlp(cls, story_file, char_file, book_nlp, tmp='tmp'):
        """Preprocess and tokenize the story file using book-nlp, and read it 
           into a Chapter object

        Args:
            story_file: Path to the story file.
            char_file: Path to the character list file.
            book_nlp: Path to book-nlp.
            tmp: A temporary directory to save intermediate results. It will be
                 created if not exist.
        
        Return:
            A new Chapter object with tokenized story.
        """

        if not os.path.exists(tmp):
            os.mkdir(tmp)

        chapter = cls()

        # temporary file paths
        char_tmp = os.path.join(tmp, 'char_tmp.txt')
        story_tmp = os.path.join(tmp, 'story_tmp.txt')
        token_tmp = os.path.join(tmp, 'token_tmp.txt')
        booknlp_tmp = os.path.join(tmp, 'booknlp_output')
        booknlp_log = os.path.join(tmp, 'booknlp.log')

        # read character list from char_file
        chapter.read_characters(char_file, tmp_file=char_tmp)
        # preprocess story file with ciphered character names 
        chapter.preprocess_story(story_file, tmp_file=story_tmp)

        # run book-nlp
        os.system('sh run-booknlp.sh {} {} {} {} {}'.format(book_nlp, 
            story_tmp, booknlp_tmp, token_tmp, booknlp_log))
        
        # read tokens from book-nlp output
        chapter.read_booknlp_tokens_file(token_tmp)

        chapter.find_character_appear_token_id()

        return chapter

    def read_characters(self, char_file, tmp_file='tmp/char_tmp.txt'):
        """
        Read and preprocess character list file.

        For the sake of tokenization, it will change the coreference annotation
        marks to ccc_CHARACTER_ccc.

        Args:
            char_file: Path to the character list file.
            tmp_file: Path to save the temporary file.

        TODO: Relieve the need for the changing of annotation by trying to use 
              customized dictionary in tokenization
        """
        print("Reading Character File ... ")
        self.max_name_len = 0
        self.characters = OrderedDict()
        self.character_num = 0
        self.t_characters = {}
        self.ciph_characters = {}
        with codecs.open(tmp_file, 'w') as outf:
            with codecs.open(char_file) as f:
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

                        # Some times the name might be space separated. Store 
                        # splited name lists to handle this situation for the 
                        # sake of processing the tokens
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

    def preprocess_story(self, story_file, tmp_file='tmp/story_tmp.txt'):
        """Replace the original text with ciphered coreference annotation marks
        
        Should call `read_characters' first.

        Args:
            story_file: Path to the story file.
            tmp_file: Path to save the temporary file.

        TODO: Relieve the need for the changing of annotation by trying to use 
              customized dictionary in tokenization
        """

        if not hasattr(self, 't_characters') or not hasattr(self, 'ciph_characters'):
            raise ValueError("Should call `read_characters' first.")

        with codecs.open(tmp_file, 'w') as outf:
            with codecs.open(story_file) as f:
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

    def read_booknlp_tokens_file(self, token_file): 
        """Read book-nlp tokens output file
        
        Args:
            token_file: Book-nlp tokens output file.
        """
        self.tokens = []
        self.paragraph_num = 0
        self.paragraph_start_token_id = []
        self.paragraph_end_token_id = []
        self.paragraph_has_quote = []
        self.paragraph_quote_type = []
        print("Reading Book-nlp Tokens File ... {}".format(token_file))
        with codecs.open(token_file) as f:
            next(f)
            for line in f:
                paragraph_id, sentence_id, token_id, begin_offset, end_offset, whitespace_after, head_token_id, original_word, normalized_word, lemma, pos, ner, deprel, in_quotation, character_id, supersense = line.strip().split('\t')

                paragraph_id =int(paragraph_id)
                token_id = int(token_id)

                # Save token
                self.tokens.append(Token(paragraph_id, sentence_id, token_id, 
                                         begin_offset, end_offset, 
                                         whitespace_after, head_token_id, 
                                         original_word, normalized_word, lemma, 
                                         pos, ner, deprel, in_quotation, 
                                         character_id, supersense))

                # Get the paragraph start and end token id
                if paragraph_id >= len(self.paragraph_start_token_id):
                    self.paragraph_start_token_id.append(token_id)
                    self.paragraph_end_token_id.append(token_id)
                    self.paragraph_has_quote.append(False)
                    self.paragraph_quote_type.append('None')

                # Check whether the paragraph contains quotes
                if in_quotation != 'O':
                    self.paragraph_has_quote[-1] = True

                self.paragraph_end_token_id[-1] = token_id

        self.paragraph_num = len(self.paragraph_start_token_id)
        print("Done. ({} tokens, {} paragraphs)".format(len(self.tokens), self.paragraph_num))

    def find_character_appear_token_id(self):
        """Find the token ids of character mentions.
        
        Should call `read_characters', `preprocess_story' and read tokens first.
        """
        self.character_appear_token_id = {}

        if not hasattr(self, 'tokens') or not hasattr(self, 'max_name_len') or \
            not hasattr(self, 'characters'):
            print("Should call `read_characters', `preprocess_story' and read tokens first.")

        print("Find character mention token ids ... ")
        for c in self.characters:
            self.character_appear_token_id[c] = []
        i = 0
        mentions = 0
        while i < len(self.tokens):
            find = False
            # try to match name mentions as long as possible 
            for j in range(self.max_name_len - 1, -1, -1):
                # skip if overflow
                if i + j >= len(self.tokens) or self.tokens[i].paragraph_id != self.tokens[i+j].paragraph_id:
                    continue
                for c in self.characters:
                    for cname in self.characters[c][1]:
                        if len(cname) == j + 1:
                            mark = True
                            for wi in range(j+1):
                                word = cname[wi]
                                if word != self.tokens[i+wi].original_word.lower():
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

    def quote_attribution_svmrank(self, feature_extracters, model_path, svm_rank, tmp='tmp'):
        """Predict quote_attribution using svm-rank.

        Should do tokenization and read character list first.

        Args:
            feature_extracters: A sequence of feature extracters to be apply. 
                                Features will be extracted in the same order as 
                                the extracters. The features should correspond 
                                to the pre-trained svm-rank model.
            svm_rank: Path to svm-rank.
            model_path: Path to pre-trained svm-rank model.
            tmp: A temporary directory to save intermediate results. It will be
                 created if not exist.
        """

        if not os.path.exists(tmp):
            os.mkdir(tmp)

        # temporary file paths
        svmrank_input_file = os.path.join(tmp, 'svmrank_input.txt')
        svmrank_predict_file = os.path.join(tmp, 'svmrank_predict.txt')

        # Generate input file for svm-rank
        self.prepare_svmrank(feature_extracters, svmrank_input_file, answer=None)

    def prepare_svmrank(self, feature_extracters, svmrank_input_file, answer=None):
        """Generate input file for svm-rank"""

        # Find the quotes in paragraphs
        self.find_paragraph_quote_token_id()

        # Extract features given feature extracters
        quote_features = self.extract_features(feature_extracters)

        # Output features to svm-rank input file
        self.output_svmrank_format(svmrank_input_file, quote_features, answer=answer)

    def find_paragraph_quote_token_id(self):
        """Find the quotes in paragraphs."""

        self.paragraph_quote_token_id = []
        print("Find quotes in paragraphs ... ")
        num_quote = 0
        for i in range(self.paragraph_num):
            self.paragraph_quote_token_id.append([])
            if self.paragraph_has_quote[i]:
                j = self.paragraph_start_token_id[i]
                state = False
                while j < len(self.tokens) and i == self.tokens[j].paragraph_id:
                    if self.tokens[j].in_quotation != 'O' and state == False:
                        state = True
                        self.paragraph_quote_token_id[i].append(j)
                    if state == True:
                        if self.tokens[j].in_quotation == 'O':
                            state = False
                            self.paragraph_quote_token_id[i].append(j - 1)
                            num_quote += 1
                        elif j == len(self.tokens) - 1 or i != self.tokens[j+1].paragraph_id:
                            state = False
                            self.paragraph_quote_token_id[i].append(j)
                            num_quote += 1
                    j += 1
        print("Done. ({} quotes)".format(num_quote))

    def extract_features(self, feature_extracters):
        """Extract features given feature extracters."""

        print("Extracting features ... ")
    
        ret = []
        for i in range(self.paragraph_num):
            ret.append([])
            for j in range(self.character_num):
                ret[-1].append(OrderedDict())

        input = {
            'tokens': self.tokens,
            'paragraph_num': self.paragraph_num,
            'paragraph_start_token_id': self.paragraph_start_token_id,
            'paragraph_end_token_id': self.paragraph_end_token_id,
            'paragraph_has_quote': self.paragraph_has_quote,
            'paragraph_quote_token_id': self.paragraph_quote_token_id,
            'paragraph_quote_type': self.paragraph_quote_type,
            'character_appear_token_id': self.character_appear_token_id,
            'character_num': self.character_num,
            'characters': self.characters
        } 

        for extracter in feature_extracters:
            extracter.extract(ret, **input)

        print("Done.")
        return ret

    def output_svmrank_format(self, outputfile, quote_features, answer=None):
        """Output features to svm-rank input file."""

        print("Writing svmrank input file to {} ...".format(outputfile))
        answers = []

        # Build output directory if not exist
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

            print("({} paragraphs have quote)".format(qp))
            
            ss = 0
            for i in range(self.paragraph_num):
                if self.paragraph_has_quote[i]:
                    ss += 1
                    f.write("# paragraph {}: {}--{} type:{} ".format(
                        i, 
                        self.paragraph_start_token_id[i], 
                        self.paragraph_end_token_id[i], 
                        self.paragraph_quote_type[i]
                    ))

                    for quoteToken_id in self.paragraph_quote_token_id[i]:
                        f.write("{} ".format(quoteToken_id))
                    f.write("\n")

                    ans_char = None
                    if answer is not None:
                        if ss > len(answers):
                            break

                        c = answers[ss-1][0]
                        sent = answers[ss-1][1].split()

                        lll = len(self.tokens[self.paragraph_quote_token_id[i][0]+1].original_word)
                        ans = sent[0][:lll]
                        now = self.tokens[self.paragraph_quote_token_id[i][0]+1].original_word.lower()

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
                            f.write("1\t")
                        else:
                            f.write("0\t")
                        f.write("qid:{}".format(ss))
                        for k, feature in enumerate(list(quote_features[i][j].keys())):
                            f.write("\t{}:{}".format(k+1, quote_features[i][j][feature]))
                        f.write("\n")
        print("Done.")

    def read_svmrank_pred(self, predictfile):
        print('Reand svm-rank prediction output ... ')
        self.char2quotes = {}
        self.quotes = []
        for c in self.characters:
            self.char2quotes[c] = []

        paragraph2quotes = []
        ss = 0
        for i in range(self.paragraph_num):
            if self.paragraph_has_quote[i]:
                paragraph2quotes.append([])
                startId = self.paragraph_start_token_id[i]
                endId = self.paragraph_end_token_id[i]
                paragraphId = i
                qtype = self.paragraph_quote_type[i]
                for j in range(0, len(self.paragraph_quote_token_id[i]), 2):
                    quoteStart = int(self.paragraph_quote_token_id[i][j])
                    quoteEnd = int(self.paragraph_quote_token_id[i][j+1])
                    paragraph2quotes[ss].append((quoteStart, quoteEnd, qtype, paragraphId, startId, endId))
                ss += 1

        with codecs.open(predictfile) as f:
            scores = []
            for line in f:
                scores.append(float(line.strip()))

        ss = 0
        for i in range(0, len(scores), self.character_num):
            maxid = np.argmax(scores[i: i+self.character_num])
            guess_char = self.characters[list(self.characters.keys())[maxid]][4:-4]
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
                t_tokens = [token[7] for token in self.tokens[quoteStart: quoteEnd+1]]
                quote['quotes'][-1]['quote'] = ' '.join(t_tokens)
                for c in self.characters:
                    quote['quotes'][-1]['quote'] = ' '.join(quote['quotes'][-1]['quote'].replace(c, '').split())
                self.char2quotes[list(self.characters.keys())[maxid]].append(quote['quotes'][-1]['quote'])
            quote['replyto'] = -1
            if quote['type'] == 'Explicit' and len(self.quotes) > 0 and quote['paragraph'] - self.quotes[-1]['paragraph'] <= 2 and quote['start'] - self.quotes[-1]['end'] <= 200:
                quote['replyto'] = self.quotes[-1]['paragraph']
            self.quotes.append(quote)
            ss += 1
        print('Done.')

    def dump_quote_json(self, json_path):
        with codecs.open(json_path, 'w') as f:
            json.dump(self.quotes, f)
