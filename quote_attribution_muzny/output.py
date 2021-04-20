"""
Format quote annotator output for pipeline evaluation
"""
import os
import json
import pdb

import pandas as pd


class AnnotatorOutput():
    """ Class for holding and transforming quote annotator output """
    
    def __init__(self, fandom_fname, quote_dirpath, coref_dirpath, toks, cluster_ids):
        """ Args:
            quote_dirpath: dirpath of quote annotator output
            coref_dirpath: dirpath of coreference output
            toks: {fandom_fname: toks_dataframe}
            coref_type: {spanbert, gold}
        """
        self.fandom_fname = fandom_fname
        self.quote_dirpath = quote_dirpath
        self.coref_dirpath = coref_dirpath
        self.tmp_dirpath = 'tmp'
        self.toks = toks
        self.charmap = {fandom_fname: {val: key for key, val in cluster_ids[
            fandom_fname].items()} for fandom_fname in cluster_ids}
        self.coref = None # coref information, to be loaded

    def load_coref_input(self, fandom_fname):
        """ Load coref information and fic tokens """
        with open(os.path.join(self.coref_dirpath, f'{fandom_fname}.json')) as f:
            self.coref = json.load(f)

    def get_charmap(self, fandom_fname):
        """ Get coreference IDs for characters from annotation file """
        #fpath = os.path.join(self.coref_dirpath, 
        #    f'{fandom_fname}_entity_clusters.csv')
        #annotation_df = pd.read_csv(fpath)
        #charid2name = dict(enumerate(annotation_df.columns))
        self.load_coref_input(fandom_fname)
        charid2name = dict(enumerate([cluster['name'] for cluster in self.coref]))
        return charid2name

    def get_global2local(self, fandom_fname):
        """ Convert fic_tokenIDs to (chap, para, token) """
        global2local = self.toks[fandom_fname].set_index('fic_token_id')[
            ['chapter_id', 'para_id', 'token_id']].to_dict(orient='index')
        return global2local

    def transform(self):
        """ Transform output to pipeline annotation format """
        #for fandom_fname in sorted({fname.split('.')[0] for fname in os.listdir(
        #    os.path.join(self.tmp_dirpath, 'out'))}):
        output_path = os.path.join(self.tmp_dirpath, 'out', 
            f'{self.fandom_fname}.out')
        if not os.path.exists(output_path):
            pdb.set_trace()
        data = pd.read_csv(output_path, sep='\t')
        #global2local = self.get_global2local(fandom_fname)
        self.process(data, self.charmap[self.fandom_fname], self.fandom_fname)
    
    def process(self, data, charid2name, fandom_fname):
        """ Build, save output quote json """
        #if self.coref is None:
        self.load_coref_input(fandom_fname)
        quotes = {}
        for quote in data.itertuples():
            entry = {}
            quote_text = ' '.join(self.coref['doc_tokens'][
                quote.quote_start:quote.quote_end])
            if quote.char_id == 'None':
                print('skipped quote')
                continue
            speaker = charid2name[int(quote.char_id)]
            if speaker not in quotes:
                quotes[speaker] = []
            #mention_start = global2local[int(quote.mention_start)] \
            #    if quote.mention_start != 'None' else None
            #mention_end = global2local[int(quote.mention_start)] \
            #    if quote.mention_end != 'None' else None
            quotes[speaker].append(
                {'position': (quote.quote_start, quote.quote_end),
                'text': quote_text,
                #'start_paragraph_token_id': global2local[
                #    quote.quote_start]['token_id'],
                #'end_paragraph_token_id': global2local[
                #    quote.quote_end-1]['token_id']+1, # otherwise will not be in dict
                #'start_mention_token_id': mention_start,
                #'end_mention_token_id': mention_end,
                })
            #entry['chapter'] = global2local[quote.quote_start]['chapter_id']
            #entry['paragraph'] = global2local[quote.quote_start]['para_id']

        # Save
        outpath = os.path.join(self.quote_dirpath, f'{fandom_fname}.quote.json')
        with open(outpath, 'w') as f:
            json.dump(quotes, f)
        #print(f"Saved transformed output to {outpath}")
