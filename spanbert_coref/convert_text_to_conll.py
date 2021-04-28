import sys
sys.path.append('/projects/fanfiction-nlp-evaluation')
import re
import warnings
import unicodedata as ud

import nltk
import os
import pandas as pd
from configparser import ConfigParser
import argparse
import pdb
from annotation import Annotation
from pipeline_output import PipelineOutput
from booknlp_output import BookNLPOutput
import evaluation_utils as utils
from annotated_span import characters_match, spans_union

from tqdm import tqdm
from pandas.errors import EmptyDataError



def get_text(fic_csv_filepath):
    try:
        fic_data = pd.read_csv(fic_csv_filepath + ".csv").set_index(['chapter_id', 'para_id'], inplace=False)
    except EmptyDataError:
        tqdm.write("Empty file")
        return None
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        para_tokens = fic_data['text_tokenized'].str.replace(r'(\\x..){3}', '').map(remove_nonlatin).str.split().to_dict()
        if sum(len(el) for el in para_tokens.values()) == 0:
            return None
        #para_tokens = fic_data['text'].str.split().to_dict()
    return para_tokens


def remove_nonlatin(word):
    """ Remove non-Latin characters from a word """
    removed = ''
    for c in word:
        try:
            if 'LATIN' in ud.name(c):
                removed += c
        except ValueError:
            continue        
    return removed


def remove_problem_chars(text):
    """ Remove unicode characters. Not used """
    rep = re.sub(r'(\\x..){3}', '', text)
    if re.search(r'(\\x..){3}', text):
        pdb.set_trace()
    return rep


def convert(fic_csv_filepath, output_dirpath):
    #fic_csv_filepath = sys.argv[1]
    #output_dirpath = sys.argv[2]

    #print(fic_csv_filepath)

    fandom_fname = fic_csv_filepath.split("/")[-1][:-4]

    char_map = {}
    span_map = {}
    char_span_map = {}

    conll_output = []

    para_tokens = get_text(fic_csv_filepath[:-4])
    if para_tokens is None:
        return False

    count = 0

    conll_output.append(['#begin document (' + str(fandom_fname) + '); part 0'])
    for (c, p), tokens in para_tokens.items():
            count = 0
            if isinstance(tokens, float) or len(tokens) == 0:
                continue
            para = " ".join(tokens)
            sents = nltk.sent_tokenize(para)
            for sent in sents:
                    for x, t in enumerate(sent.split()):
                            i = x + count
                            ann = ''

                            for char in char_span_map:
                                    if (c, p, i, 0) in char_span_map[char]:
                                            if (c, p, i, 1) in char_span_map[char]:
                                                    ann += '|(' + str(char_map[char]) + ')'
                                            else:
                                                    ann += '|(' + str(char_map[char])

                                    if (c, p, i, 1) in char_span_map[char]:
                                            if (c, p, i, 0) not in char_span_map[char]:
                                                    ann += '|' + str(char_map[char]) + ')'

                            if len(ann) > 0:
                                    if ann[0] == '|':
                                            ann = ann[1:]

                            conll_output.append([str(fandom_fname), '0', str(x), str(t), str(c), str(p), str(i+1), '-', '-', '-', '-', '-', ann])

                    count += len(sent.split())

                    conll_output.append([''])

            conll_output.append(['#end document'])

    if not os.path.exists(output_dirpath):
        os.mkdir(output_dirpath)
    with open(output_dirpath + "/" + str(fandom_fname) + ".conll", "w") as f:
            for l in conll_output:
                    f.write('\t'.join(l) + '\n')
    return True
