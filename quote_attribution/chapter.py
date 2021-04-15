#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-

import os
import json
import numpy as np
import csv
import codecs
import re
from tokens import Token, Token_BookNLP, Mention, CharacterMentionParser
from collections import OrderedDict
import pdb


class Chapter(object):
    """Class for storing a chapter with tokenized paragraphs, character list, and quote attributions, etc."""

    def __init__(self):
        super(Chapter, self).__init__()

    @classmethod
    def read_with_booknlp(cls, story_file, char_file, book_nlp, tok_file=None, coref_story=True, no_cipher=True, fix_inv_char=False, tmp='tmp', use_booknlp=False):
        """Read a chapter using book-nlp.
        
        The factory function to preprocess and tokenize the story file using 
        book-nlp, and read it into a Chapter object and return.

        Args:
            story_file: Path to the story file.
            char_file: Path to the character list file.
            book_nlp: Path to book-nlp.
            tok_file: External tokenization file to be loaded. If it is None or 
                      invalid, no external tokenization will be load.
            coref_story: Story files are coreference resolved.
            no_cipher: Do not cipher character names.
            fix_inv_char: Fix invalid character name (such as comma in name)
            tmp: A temporary directory to save intermediate results. It will be
                 created if not exist.
            use_booknlp: Whether or not to use BookNLP. If True, then will use original
                code from Huiming, if False will read new coreference format.
        
        Return:
            A new Chapter object with tokenized story.
        """

        if not os.path.exists(tmp):
            os.mkdir(tmp)

        chapter = cls()

        # temporary file paths
        char_tmp = os.path.join(tmp, 'char_tmp.txt')
        story_tmp = os.path.join(tmp, 'story_tmp.csv')
        token_tmp = os.path.join(tmp, 'token_tmp.txt')
        booknlp_tmp = os.path.join(tmp, 'booknlp_output')
        booknlp_log = os.path.join(tmp, 'booknlp.log')

        # read character list from char_file
        chapter.read_characters(char_file, coref_story=coref_story, no_cipher=no_cipher, fix_inv_char=fix_inv_char, tmp_file=char_tmp)

        if use_booknlp:
            if tok_file is not None and isinstance(tok_file, str) and os.path.exists(tok_file) and os.path.isfile(tok_file):
            #    print("Read external tokenizations.")
            #    # read tokens from external tokenization
                chapter.read_booknlp_tokens_file(tok_file)

            #else:
            #    print("No or invalid external tokenization file; do tokenization with book-nlp.")
            #    if book_nlp is None:
            #        raise ValueError("Invalid book-nlp path.")
            #    # preprocess story file with ciphered character names 
            #    chapter.preprocess_story(story_file, coref_story=coref_story, tmp_file=story_tmp)
            #    # run book-nlp
            #    os.system('sh run-booknlp.sh {} {} {} {} {}'.format(book_nlp, 
            #        story_tmp, booknlp_tmp, token_tmp, booknlp_log))
            #    # read tokens from book-nlp output
            #    chapter.read_booknlp_tokens_file(token_tmp)

            # Find character mentions
            chapter.find_character_appear_token_id()

        # read chapter from coref csv, extracts quotes and character mentions
        else:
            chapter.read_coref_output(story_file)

        return chapter

    def _fix_char_name(self, name):
        """"Remove comma in name"""
        return name.replace('_,_', '_')

    def is_start_quote(self, token):
        start_quote_chars = ['“', '``', '"', '«']
        return token in start_quote_chars

    def is_end_quote(self, token):
        end_quote_chars = ['”', "''", '"', '»']
        return token in end_quote_chars

    def in_quotation(self, tokens):
        """ Return BIO for quotations """
    
        start_quote_chars = ['“', '``', '"', '«']
        end_quote_chars = ['”', "''", '"', '»']
        
        result = []
        state = 'O' # Beginning, inside, end, outside
        transform_state = {
            'B': 'B',
            'I': 'I',
            'E': 'I',
            'O': 'O'
        }
        
        for tok in tokens:
            if (state == 'O' or state == 'E') and tok in start_quote_chars:
                state = 'B'
                
            elif state == 'B' and not tok in end_quote_chars:
                state = 'I'
                
            elif (state == 'B' or state == 'I') and tok in end_quote_chars:
                state = 'E'
                
            elif state == 'E' and not tok in start_quote_chars:
                state = 'O'
                
                
            result.append(transform_state[state])
                
        return result

    def extract_quotes(self):
        """ Quote extraction for tokens file, to be used instead of BookNLP quote extraction """

        tokens = [tok.word for tok in self.tokens]
        bio_quotes = self.in_quotation(tokens)

        for tok, bio in zip(self.tokens, bio_quotes):
            tok.in_quotation = bio

        # Calculate whether each paragraph contains a quote
        self.paragraph_has_quote = []

        current_paragraph = -1

        for tok in self.tokens:
            if tok.paragraph_id > current_paragraph: # new paragraph
                self.paragraph_has_quote.append(False)
                current_paragraph = tok.paragraph_id

            if tok.in_quotation != 'O':
                self.paragraph_has_quote[-1] = True

        if len(self.paragraph_has_quote) != self.paragraph_num:
            pdb.set_trace()

    def read_characters(self, char_file, coref_story=True, no_cipher=True, fix_inv_char=False, tmp_file='tmp/char_tmp.txt'):
        """Read and preprocess character list file.
        
        For the sake of tokenization, it will change the coreference annotation
        marks to ccc_CHARACTER_ccc if `no_cipher' is False.

        Args:
            char_file: Path to the character list file.
            coref_story: Story files are coreference resolved.
            no_cipher: Do not cipher character names.
            fix_inv_char: Fix invalid character name (such as comma in name)
            tmp_file: Path to save the temporary file.

        TODO: Relieve the need for the changing of annotation by trying to use 
              customized dictionary in tokenization
        """

        print("Reading Character File ... ")
        # Maximum length of separated name
        self.max_name_len = 0
        # Characters of the chapter
        self.characters = OrderedDict()
        # Number of characters
        self.character_num = 0
        # Temporary dictionary to save ciphered character names (name to ciphered name)
        self.t_characters = {}
        # Temporary dictionary to save ciphered character names (ciphered name to name)
        self.ciph_characters = {}
        with codecs.open(tmp_file, 'w') as outf:
            with codecs.open(char_file) as f:
                for _line in f:
                    line = _line.strip()
                    if len(line) > 0:
                        l = line.split(';')
                        # new coreference annotation mark
                        if not no_cipher:
                            if coref_story:
                                ciph_char = 'ccc_' + l[0][3:-1] + '_ccc'
                            else:
                                ciph_char = 'ccc_' + l[0] + '_ccc'
                        else:
                            ciph_char = l[0]
                        if fix_inv_char:
                            ciph_char = self._fix_char_name(ciph_char)
                        self.t_characters[l[0]] = ciph_char
                        self.ciph_characters[ciph_char] = l[0]
                        l[0] = ciph_char

                        # output to the tmp file
                        outf.write(';'.join(l) + '\n') 

                        # Some times the name might be space separated. Store 
                        # splited name lists to handle this situation for the 
                        # sake of processing the tokens
                        #c = l[0].lower().strip()
                        c = l[0].strip()
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

    def preprocess_story(self, story_file, coref_story=True, tmp_file='tmp/story_tmp.txt'):
        """Replace the original text with ciphered coreference annotation marks
        
        Should call `read_characters' first.

        Args:
            story_file: Path to the story file.
            tmp_file: Path to save the temporary file.

        """

        if not hasattr(self, 't_characters') or not hasattr(self, 'ciph_characters'):
            raise ValueError("Should call `read_characters' first.")

        with codecs.open(tmp_file, 'w') as outf:
            with codecs.open(story_file) as f:
                f_csv = csv.reader(f)
                headers = next(f_csv)
                for line in f_csv:
                    if len(line) < 4:
                        continue
                    #text = line[3] # for 'text' column
                    text = line[-1] # for 'text_tokenized' column

                    # annotate with new marks
                    for c in self.t_characters:
                        text = text.replace(c, self.t_characters[c])
                    text_split = text.split()
                    
                    if coref_story:
                        # remove the mention before the coreference annotation marks
                        new_text_split = []
                        for i, t in enumerate(text_split[:-1]):
                            if text_split[i+1] not in self.ciph_characters:
                                new_text_split.append(t)
                        text_split = new_text_split

                    # save into the temporary file
                    outf.write(' '.join(text_split)+'\n\n')


    def read_coref_output(self, coref_file): 
        """Read pipeline coref output file, already tokenized
        
        Args:
            coref_file: path to coref output file (csv)
        """

        # Chapter IDs for every paragraph
        self.paragraph_chapter_id = []
        # Paragraph IDs (restarting at chapters) for every paragraph
        self.paragraph_paragraph_id = []
        # List of tokens
        self.tokens = []
        # Number of paragraphs
        self.paragraph_num = 0
        # IDs of paragraph start tokens: needed for feature extracters
        self.paragraph_start_token_id = []
        # IDs of paragraph end tokens: needed for feature extracters
        self.paragraph_end_token_id = []
        # The token IDs of character mentions: needed for feature extracters
        self.character_appear_token_id = {}
        # Start and end story token IDs of quotes for each paragraph. Stored alternatively by start and end ids. [[start0, end0, start1, end1, ...], [], ...]
        self.story_quote_token_id = []
        # Start and end paragraph token IDs of quotes for each paragraph. Stored alternatively by start and end ids. [[start0, end0, start1, end1, ...], [], ...]
        self.paragraph_quote_token_id = []
        # Whether each paragraph contains a quote
        self.paragraph_has_quote = []
        # The type of quotes in the paragraph. Could be `None', `Implicit', or `Explicit'. Will be filled later by SVMrank output
        self.paragraph_quote_type = []

        print("Reading coref output file ... {}".format(coref_file))

        story_token_id = 0

        with open(coref_file) as coref_csv:
            #reader = csv.reader(coref_csv) # fic_id, chapter_id, para_id, text, text_tokenized
            #header = next(reader) # skip header
            reader = csv.DictReader(coref_csv) # fic_id, chapter_id, para_id, text, text_tokenized

            for line in reader:
                paragraph_token_id = 1 # start with 1 to match annotations
                paragraph_has_quote = False

                chapter_id = int(line['chapter_id'])
                #paragraph_id = int(line['paragraph_id'])
                paragraph_id = int(line['para_id'])
                text = line['text_tokenized']

                self.paragraph_start_token_id.append(story_token_id)
                self.story_quote_token_id.append([])
                self.paragraph_quote_token_id.append([])

                # Extract character spans
                parser = CharacterMentionParser()
                parser.feed(text)
                tokens = parser.get_tokens()
                character_tokens = parser.get_character_tokens()

                # Store tokens
                in_quote = False
                end_quote = False
                current_story_start_quote_id = None
                current_paragraph_start_quote_id = None

                for i, token in enumerate(tokens):
                    token_chars = character_tokens.get(i, [])

                    # Store character mention token ID
                    for character in token_chars:
                        #character_name = character.lower()
                        character_name = character
                        if not character_name in self.characters:
                            continue
                        if not character_name in self.character_appear_token_id:
                            self.character_appear_token_id[character_name] = []
                        self.character_appear_token_id[character_name].append(story_token_id)

                    # Check for quotes
                    if (not in_quote) and (self.is_start_quote(token)):
                        current_story_start_quote_id = story_token_id
                        current_paragraph_start_quote_id = paragraph_token_id
                        in_quote = True
                    elif self.is_end_quote(token):
                        if current_story_start_quote_id is not None:
                            self.story_quote_token_id[-1].append(current_story_start_quote_id)
                            self.paragraph_quote_token_id[-1].append(current_paragraph_start_quote_id)
                            self.story_quote_token_id[-1].append(story_token_id)
                            self.paragraph_quote_token_id[-1].append(paragraph_token_id)
                            paragraph_has_quote = True
                            end_quote = True

                    if in_quote and current_story_start_quote_id == paragraph_token_id:
                        in_quotation = 'B-QUOTE'
                    elif in_quote and current_story_start_quote_id != paragraph_token_id:
                        in_quotation = 'I-QUOTE' 
                    else:
                        in_quotation = 'O'
                    #self.tokens.append(Token(chapter_id, paragraph_id, story_token_id, paragraph_token_id, token, in_quotation, token_chars))
                    self.tokens.append(Token(chapter_id, paragraph_id, story_token_id, paragraph_token_id, token, in_quote, token_chars))

                    if end_quote:
                        in_quote = False
                        end_quote = False

                    story_token_id += 1
                    paragraph_token_id += 1

                self.paragraph_chapter_id.append(chapter_id)
                self.paragraph_paragraph_id.append(paragraph_id)
                self.paragraph_has_quote.append(paragraph_has_quote)
                self.paragraph_quote_type.append('None')
                self.paragraph_end_token_id.append(story_token_id)
                self.paragraph_num += 1

        print("Done. ({} paragraphs)".format(self.paragraph_num))


    def read_booknlp_tokens_file(self, token_file): 
        """Read book-nlp tokens output file
        
        Args:
            token_file: Book-nlp tokens output file.
        """
        # List of tokens
        self.tokens = []
        # Number of paragraphs
        self.paragraph_num = 0
        # IDs of paragraph start tokens
        self.paragraph_start_token_id = []
        # IDs of paragraph end tokens
        self.paragraph_end_token_id = []
        # Whether the paragraph contains a quote
        self.paragraph_has_quote = []
        # The type of quotes in the paragraph. Could be `None', `Implicit', or `Explicit'
        self.paragraph_quote_type = []
        print("Reading Book-nlp Tokens File ... {}".format(token_file))
        with codecs.open(token_file) as f:
            next(f)
            for line in f:
                paragraph_id, sentence_id, token_id, begin_offset, end_offset, whitespace_after, head_token_id, original_word, normalized_word, lemma, pos, ner, deprel, in_quotation, character_id, supersense = line.strip().split('\t')

                paragraph_id =int(paragraph_id)
                token_id = int(token_id)

                # Store token
                self.tokens.append(Token_BookNLP(paragraph_id, sentence_id, token_id, 
                                         begin_offset, end_offset, 
                                         whitespace_after, head_token_id, 
                                         original_word, normalized_word, lemma, 
                                         pos, ner, deprel, in_quotation, 
                                         character_id, supersense))

                # Get the paragraph start and end token id
                if paragraph_id >= len(self.paragraph_start_token_id): # new paragraph
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
        """ NOT CALLED ANYMORE except by prepare_train--integrated into read_coref_output
        Find the token ids of character mentions.
        
        Should call `read_characters', `preprocess_story' and read tokens first.
        """
        # The token IDs of character mentions
        self.character_appear_token_id = {}

        if not hasattr(self, 'tokens') or not hasattr(self, 'max_name_len') or \
            not hasattr(self, 'characters'):
            raise ValueError("Should call `read_characters', `preprocess_story' and read tokens first.")

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

        if svm_rank is None:
            raise ValueError("Invalid svm-rank path.")

        # temporary file paths
        svmrank_input_file = os.path.join(tmp, 'svmrank_input.txt')
        svmrank_predict_file = os.path.join(tmp, 'svmrank_predict.txt')

        # Generate input file for svm-rank
        self.prepare_svmrank(feature_extracters, svmrank_input_file, answer=None)

        # Run svm-rank
        os.system('sh run-svmrank.sh {} {} {} {}'.format(svm_rank, 
                                                         svmrank_input_file, 
                                                         model_path, 
                                                         svmrank_predict_file))

        # Read svm-rank output and build quote attributions
        self.read_svmrank_pred(svmrank_predict_file)

    def prepare_svmrank(self, feature_extracters, svmrank_input_file, answer=None, original=False):
        """Generate input file for svm-rank.
        
        Detect all quotations in this chapter and do quote features extraction
        using the feature extracters, and save features into `svmrank_input_file'
        
        Args:
            feature_extracters: A sequence of feature extracters to be applied. 
            svmrank_input_file: Path to save svm-rank input file.
            answer: Path to the quote attribution golden answers file (useful in
                    training)
            original: Whether to use methods specified in the original version by 
                    Huiming Jin
        """

        if original:
            # Find the quotes in paragraphs (now done in read_coref_output)
            self.find_paragraph_quote_token_id()

        # Extract features given feature extracters
        quote_features = self.extract_features(feature_extracters, original=original)

        # Output features to svm-rank input file
        self.output_svmrank_format(svmrank_input_file, quote_features, answer=answer, original=original)

    def find_paragraph_quote_token_id(self):
        """Find the quotes in paragraphs.
            Only called by prepare_train now, otherwise not used.
        """

        # Start and end token IDs of quotes in paragraphs. Stored alternatively by start and end ids
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

    def extract_features(self, feature_extracters, original=False):
        """Extract features given feature extracters.
        
        Some feature extracters may edit the property of the chapter object, 
        such as `paragraph_quote_type'

        Args:
            feature_extracters: A sequence of feature extracters to be apply.
            original: whether to use the original format from Huiming's version

        Return:
            Extracted features, a 2-D list of dictionaries indicates the 
            features at paragraph i for character j.
        """

        print("Extracting features ... ")
    
        # Extracted features will be stored in `ret'
        ret = []
        for i in range(self.paragraph_num):
            ret.append([])
            for j in range(self.character_num):
                ret[-1].append(OrderedDict())

        if original:
            quote_tokens = self.paragraph_quote_token_id
        else:
            quote_tokens = self.story_quote_token_id

        input = {
            'tokens': self.tokens,
            'paragraph_num': self.paragraph_num,
            'paragraph_start_token_id': self.paragraph_start_token_id,
            'paragraph_end_token_id': self.paragraph_end_token_id,
            'paragraph_has_quote': self.paragraph_has_quote,
            'paragraph_quote_token_id': quote_tokens,
            'paragraph_quote_type': self.paragraph_quote_type,
            'character_appear_token_id': self.character_appear_token_id,
            'character_num': self.character_num,
            'characters': self.characters
        } 

        for extracter in feature_extracters:
            extracter.extract(ret, **input)

        print("Done.")
        return ret

    def output_svmrank_format(self, outputfile, quote_features, answer=None, original=False):
        """Output features to svm-rank input file.
        
        Args:
            outputfile: Path to output svm-rank input file.
            quote_features: Extracted features.
            answer: Path to the quote attribution golden answers file (useful in 
                    training)
            original: Whether the format should match Huiming's original format
        """

        print("Writing svmrank input file to {} ...".format(outputfile))
        answers = []

        # Build output directory if not exist
        output_abs_path = os.path.abspath(outputfile)
        output_parent_path = os.path.abspath(os.path.dirname(output_abs_path) + os.path.sep + ".")
        if not os.path.exists(output_parent_path):
            os.makedirs(output_parent_path)

        # Get answer speaker and utterance
        if answer is not None:
            with codecs.open(answer) as f:
                for line in f:
                    l = line.split('\t')
                    #answers.append((l[1].lower(), l[2].lower()))
                    answers.append((l[1], l[2]))

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

                    # Save paragraph information into comment lines
                    f.write("# paragraph {}: {}--{} type:{} ".format(
                        i, 
                        self.paragraph_start_token_id[i], 
                        self.paragraph_end_token_id[i], 
                        self.paragraph_quote_type[i]
                    ))
                    if original:
                        for quoteToken_id in self.paragraph_quote_token_id[i]:
                            f.write("{} ".format(quoteToken_id))
                    else:
                        for quoteToken_id in self.story_quote_token_id[i]:
                            f.write("{} ".format(quoteToken_id))
                    f.write("\n")

                    ans_char = None
                    if answer is not None:
                        # More quotes extracted than gold answers. Skip
                        # redundant quotes.
                        if ss > len(answers):
                            break

                        t_ans_char = answers[ss-1][0]  # answer speaker
                        t_ans_sent = answers[ss-1][1].split()  # answer utterance

                        # Simply check whether the answer utterance is current
                        # sentence or not by try to match the first word.
                        first_word_len = len(self.tokens[self.paragraph_quote_token_id[i][0]+1].original_word)
                        ans_first_word = t_ans_sent[0][:first_word_len].lower()
                        now_first_word = self.tokens[self.paragraph_quote_token_id[i][0]+1].original_word.lower()

                        # Mismatch, back to last answer to check next paragraph
                        if ans_first_word != now_first_word:
                            ss -= 1
                            continue
                        
                        # Check whether there is only one character matches to
                        # the answer character
                        nn = 0
                        for tc in self.characters:
                            if tc == t_ans_char:
                                nn += 1
                        '''
                        if nn < 1:
                            print c
                            print "No char found!"
                        elif nn > 1:
                            print "More char found!"
                        '''
                        if nn == 1:
                            ans_char = t_ans_char
                    
                    # Output svm-rank training sample
                    for j in range(self.character_num):
                        if ans_char is not None and ans_char == list(self.characters.keys())[j]:
                            f.write("1\t")
                        else:
                            f.write("0\t")
                        f.write("qid:{}".format(ss))
                        for k, feature in enumerate(list(quote_features[i][j].keys())):
                            f.write("\t{}:{}".format(k+1, quote_features[i][j][feature]))
                        f.write("\n")
        print("Done.")

    def read_svmrank_pred(self, predictfile):
        """Read svm-rank output file and organize into quote attributions
        
        The function will pick the character with highest score as the guessed
        speaker, and try to guess conversation flow. Two quotes will be 
        considered as in a conversation flow if the latter's type is `Explicit'
        and they are close enough.

        Args:
            predictfile: Path to svm-rank output file.
        """

        print("Read svm-rank prediction output ... ")
        # Character to quotes
        self.char2quotes = {}
        # List of quotes in the chapter
        self.quotes = []
        for c in self.characters:
            self.char2quotes[c] = []

        paragraph2quotes = []
        ss = 0
        for i in range(self.paragraph_num):
            if self.paragraph_has_quote[i]:
                paragraph2quotes.append([])
                start_id = self.paragraph_start_token_id[i]
                end_id = self.paragraph_end_token_id[i]
                #paragraph_id = i + 1
                paragraph_id = self.paragraph_paragraph_id[i]
                chapter_id = self.paragraph_chapter_id[i]
                qtype = self.paragraph_quote_type[i]
                for j in range(0, len(self.paragraph_quote_token_id[i]), 2):
                    story_quote_start = int(self.story_quote_token_id[i][j])
                    story_quote_end = int(self.story_quote_token_id[i][j+1])
                    paragraph_quote_start = int(self.paragraph_quote_token_id[i][j])
                    paragraph_quote_end = int(self.paragraph_quote_token_id[i][j+1])
                    paragraph2quotes[ss].append((story_quote_start, story_quote_end, paragraph_quote_start, paragraph_quote_end, qtype, chapter_id, paragraph_id, start_id, end_id))
                ss += 1

        with codecs.open(predictfile) as f:
            scores = []
            for line in f:
                scores.append(float(line.strip()))

        ss = 0
        for i in range(0, len(scores), self.character_num):
            maxid = np.argmax(scores[i: i+self.character_num])
            #guess_char = list(self.characters.keys())[maxid][4:-4]
            guess_char = sorted(self.characters.keys())[maxid]
            quote = {}
            quote['speaker'] = guess_char
            quote['quotes'] = []
            for story_quote_start, story_quote_end, paragraph_quote_start, paragraph_quote_end, quote_type, chapter_id, paragraph_id, start_id, end_id in paragraph2quotes[ss]:
                quote['chapter'] = chapter_id
                quote['paragraph'] = paragraph_id
                quote['type'] = quote_type
                quote['start'] = start_id
                quote['end'] = end_id
                quote['quotes'].append({})
                quote['quotes'][-1]['start_story_token_id'] = story_quote_start
                quote['quotes'][-1]['end_story_token_id'] = story_quote_end
                quote['quotes'][-1]['start_paragraph_token_id'] = paragraph_quote_start
                quote['quotes'][-1]['end_paragraph_token_id'] = paragraph_quote_end
                t_tokens = [token.word for token in self.tokens[story_quote_start: story_quote_end+1]]
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
        """Dump quote attributions.
        
        Args:
            json_path: Path to dump quotes.
        """
        with codecs.open(json_path, 'w') as f:
            f.write(json.dumps(self.quotes) + '\n')
