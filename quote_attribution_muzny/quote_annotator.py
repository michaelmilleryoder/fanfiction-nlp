#!/usr/bin/env python
# coding: utf-8
"""
* Prepare input for running quote annotation
* Run quote annotation (Muzny+2017 reimplementation by Sims+Bamman2020)
* Transform output to fanfiction pipeline format for evaluation

@author Michael Miller Yoder
@year 2021
"""

import os
import subprocess
import pdb

from quote_attribution_muzny.input_format import AnnotatorInput
from quote_attribution_muzny.output import AnnotatorOutput


class QuoteAnnotator:
    """ Runs Muzny+2017 quote annotation """

    def __init__(self, inp, out_dirpath):
        """ Args:
                inp: AnnotatorInput object
        """
        self.inp = inp
        #self.out_dirpath = \
            #'/projects/quote_annotator_muzny/annotated_10fandom_test/output/spanbert_coref_pipeline_quotes'
        self.out_dirpath = out_dirpath
        self.tmp_dirpath = 'tmp'
        self.tmp_out_dirpath = 'tmp/out' # confusing
        if not os.path.exists(self.tmp_out_dirpath):
            os.mkdir(self.tmp_out_dirpath)
    
    def annotate(self):
        """ Run annotation """
        # Get fandom_fnames
        fandom_fnames = sorted({fname.split('.')[0] for fname in os.listdir(
            self.inp.out_dirpath)})
        for fandom_fname in fandom_fnames:
            if len(fandom_fname) != '':
                self.run_cmd(fandom_fname)

        out = AnnotatorOutput(self.out_dirpath, self.inp.coref_dirpath, 
            self.inp.toks, self.inp.cluster_ids)
        return out

    def run_cmd(self, fandom_fname):
        """ Run quote_attribution.py for a fic """
        tok_fpath = os.path.join(self.inp.out_dirpath, f'{fandom_fname}.tokens')
        ents_fpath = os.path.join(self.inp.out_dirpath, f'{fandom_fname}.ents')
        outpath = os.path.join(self.tmp_dirpath, 'out', f'{fandom_fname}.out')
        cmd = ['python', 'quotation_attribution.py', tok_fpath, ents_fpath, outpath]
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(e)
