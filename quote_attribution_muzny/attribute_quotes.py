""" Main file for running Muzny quote attribution
@author Michael Miller Yoder (though this reimplementation of Muzny's quote attribution is from Sims+Bamman 2020)
@year 2021
"""

import os
import itertools
from multiprocessing import Pool
import pdb

from tqdm import tqdm

from quote_attribution_muzny.input_format import AnnotatorInput
from quote_attribution_muzny.quote_annotator import QuoteAnnotator
from quote_attribution_muzny.output import AnnotatorOutput


def attribute_quotes(fic_dirpath, coref_dirpath, quote_dirpath, threads):
    """ Attribute quotes """
    if not os.path.exists(quote_dirpath):
        os.mkdir(quote_dirpath)
    fnames = []
    for fname in sorted(os.listdir(fic_dirpath)):
        name = fname.split('.')[0]
        if not os.path.exists(os.path.join(
            quote_dirpath, f'{name}.quote.json')):
            #fpaths.append(os.path.join(fic_dirpath, fname))
            fnames.append(name)
    params = sorted(zip(
        fnames,
        itertools.repeat(fic_dirpath),
        itertools.repeat(coref_dirpath),
        itertools.repeat(quote_dirpath),
        ))
    
    if threads > 1:
        with Pool(threads) as p:
            list(tqdm(p.imap(attribute_quotes_file, params), total=len(fnames), 
                ncols=70))
    else:
        # for debugging
        list(tqdm(map(attribute_quotes_file, params), total=len(fnames), ncols=70))

def attribute_quotes_file(params):
    fname, fic_dirpath, coref_dirpath, quote_dirpath = params
    inp = AnnotatorInput(fname, fic_dirpath, coref_dirpath)
    inp.load_input()
    annotator = QuoteAnnotator(inp, quote_dirpath)
    out = annotator.annotate()
    out.transform() # transform to pipeline output format
