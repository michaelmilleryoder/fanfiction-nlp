"""
Format input for quote annotator
"""
import os
import re
import pdb
import sys
import json

import numpy as np
import pandas as pd
import spacy
from spacy.tokenizer import Tokenizer

sys.path.append('/projects/fanfiction-nlp-evaluation')
from pipeline_output import extract_mention_tags


def get_sent_ids(toks):
    sents = list(toks.sents)
    return [sents.index(tok.sent) for tok in toks]
    

class AnnotatorInput:
    """
    Match the input of Sims+Bamman Muzny+ reimplementation script

    Need to reproduce at least columns 0, 1, 2, 6, 7, 8, 9, 10, 12, 13, 14, 15  
     paragraphId, sentenceID, tokenId, headTokenId, originalWord, normalizedWord, 
     lemma, pos, deprel, inQuotation, characterId, supersense  
     
     Requires
     * tokenization (split on whitespace from gold tokenization)
     * sentence tokenization
     * lemmatization
     * part-of-speech tagging
     * dependency parsing
     * quote extraction (BIO)
     * character coref
     * supersense tagging (skipping since only use it for verb.communication and 
        there aren't many tools out there for this)
    """

    def __init__(self, fandom_fname, inp_dirpath, coref_dirpath):
        self.fandom_fname = fandom_fname
        self.inp_dirpath = inp_dirpath
        self.coref_dirpath = coref_dirpath
        self.coref_type = 'spanbert' # {gold, spanbert}
        self.tmp_dirpath = 'tmp'
        if not os.path.exists(self.tmp_dirpath):
            os.mkdir(self.tmp_dirpath)
        self.out_dirpath = os.path.join(self.tmp_dirpath, 'formatted_input')
        if not os.path.exists(self.out_dirpath):
            os.mkdir(self.out_dirpath)

        # to get extracted quote boundaries
        self.quote_extraction_type = 'pipeline' # {gold, pipeline}
        #self.quote_dirpath = \
            #'/data/fanfiction_ao3/annotated_10fandom/test/quote_attribution/'
        self.quote_dirpath = \
            '/data/fanfiction_ao3/annotated_10fandom/test/output/quote_attribution_spanbert_coref'
        self.tok_cols = ['paragraphId', 'sentenceID', 'tokenId', 'beginOffset',
            'endOffset', 'whitespaceAfter', 'headTokenId', 'originalWord',
            'normalizedWord', 'lemma', 'pos', 'ner', 'deprel', 'inQuotation', 
            'characterId', 'supersense']
        self.toks = {} # fandom_fname: toks doc, for later use
        self.cluster_ids = {} # fandom_fname: {char_name: id}, for later use
        self.coref = None # coref information, to be loaded

    def load_coref_input(self, fandom_fname):
        """ Load coref information and fic tokens """
        if self.coref_type == 'spanbert':
            fpath = os.path.join(self.coref_dirpath, f'{fandom_fname}.json')
            if not os.path.exists(fpath):
                return False
            with open(fpath) as f:
                self.coref = json.load(f)
                if 'doc_tokens' not in self.coref:
                    self.coref['doc_tokens'] = self.coref['document'].split()
            return True

    def load_input(self):
        #for fname in sorted(os.listdir(self.inp_dirpath)):
        #for fname in sorted(os.listdir(self.coref_dirpath)):
            #print(f'Processing {fname}...')
            #fandom_fname = fname.split('.')[0]
        fpath = os.path.join(self.inp_dirpath, self.fandom_fname + '.csv')
        try:
            fic_data = pd.read_csv(fpath, dtype={'text': str, 'text_tokenized': str})
            fic_data.para_id = pd.to_numeric(fic_data.para_id, errors='coerce')
            fic_data.dropna(subset=['text_tokenized', 'para_id'], inplace=True)
            fic_data.para_id = fic_data.para_id.astype(int)
        except pd.errors.EmptyDataError:
            return False
        if not self.process_input(fic_data):
            return False
        return True

    def process_input(self, fic_data):
        """ Process one input fic, saves token and coref files """
        if not self.load_coref_input(self.fandom_fname):
            return False
        self.toks[self.fandom_fname], tok_data = self.preprocess_tokens(fic_data)
        #global_token_id = self.get_global_token_id(self.toks[fandom_fname])
        coref_ents = self.build_coref()
        self.build_tokens(tok_data, fic_data, coref_ents)
        return True

    def preprocess_tokens(self, fic_data):
        """ Split, lemmatize, postag, parse tokens. """
        nlp = spacy.load('en')
        nlp.tokenizer = Tokenizer(nlp.vocab, token_match=re.compile(r'\S+').match)
        fic_data['token'] = fic_data.text_tokenized.map(nlp)
        fic_data['postag'] = [[tok.tag_ for tok in toks] for toks in fic_data[
            'token'].tolist()]
        fic_data['lemma'] = [[tok.lemma_ for tok in toks] for toks in fic_data[
            'token'].tolist()]
        fic_data['sent_id'] = fic_data['token'].map(get_sent_ids)

        # Need to get the -1 for roots
        fic_data['head_id'] = [[tok.head.i for tok in toks] for toks in fic_data[
            'token'].tolist()]
        fic_data['deprel'] = [[tok.dep_ for tok in toks] for toks in fic_data[
            'token'].tolist()]
        #fic_data['token_id'] = [[tok.i for tok in toks] for toks in fic_data['token'].tolist()]
        fic_data['word'] = [[tok.text for tok in toks] for toks in fic_data['token'].tolist()]

        fic_data['para_id'] = fic_data['para_id'] - 1 # 0-index instead of 1-index
        fic_data['para_id'] = fic_data['para_id'].astype(int)

        # melt on whitespace for string columns
        explode_cols = ['word', 'postag', 'lemma', 'sent_id', 'head_id', 
            'deprel', 'token_id']
        toks = fic_data.apply(lambda x: x.explode() if x.name in explode_cols else x)

        # Renumber ID columns to continue throughout the df instead of repeating
        toks['fic_sent_id'] = toks.groupby(['para_id', 'sent_id']).ngroup()
        toks['fic_token_id'] = range(len(toks))

        #fic_data['token'] = fic_data.text_tokenized.map(nlp)
        #tokens = nlp(' '.join(self.coref['doc_tokens']))
        #toks = pd.DataFrame(self.coref['doc_tokens'], columns=['token'])
        #toks['postag'] = [tok.tag_ for tok in tokens]
        #toks['lemma'] = [tok.lemma_ for tok in tokens]
        #toks['sent_id'] = get_sent_ids(tokens)

        ## Need to get the -1 for roots
        #toks['head_id'] = [tok.head.i for tok in tokens]
        #toks['deprel'] = [tok.dep_ for tok in tokens]
        #toks['token_id'] = [tok.i for tok in tokens]

        # Renumber ID columns to continue throughout the df instead of repeating
        #toks['fic_sent_id'] = toks.groupby(['para_id', 'sent_id']).ngroup()
        #toks['fic_token_id'] = range(len(toks))

        # Rename columns
        transform = {
            'para_id': 'paragraphId', 
            'fic_sent_id': 'sentenceID', 
            'fic_token_id': 'tokenId', 
            'head_id': 'headTokenId',
            'word': 'originalWord',
            'postag': 'pos',
        }

        tok_data = toks.rename(columns=transform)
        tok_data = tok_data[[col for col in self.tok_cols if col in tok_data.columns]]
        return toks, tok_data

    def add_coref_info(self, coref_ents, tok_data):
        """ Add coref info to tok file """
        # Build mapping from tokenId to coreference_ids
        coref_ents['span'] = [range(beg, end+1) for (beg, end) in zip(
            coref_ents.span_start, coref_ents.span_end)]
        coref_ents_toks = coref_ents.explode('span')
        tok2char = coref_ents_toks.set_index('span')['coreference_id'].to_dict()
        tok_data['characterId'] = tok_data.tokenId.map(lambda x: tok2char.get(x, -1))
        return tok_data

    def is_start_quote(self, token: str):
        start_quote_chars = ['“', '``', '"', '«']
        return token in start_quote_chars

    def is_end_quote(self, token):
        end_quote_chars = ['”', "''", '"', '»']
        return token in end_quote_chars

    def extract_quotes(self, fandom_fname, tok_data):
        """ Extract quotes, store in token data """
        tokens = tok_data['originalWord'].tolist()
        in_quote = False
        quote_bio = []
        for i, token in enumerate(tokens):
            # Check for quotes
            if (not in_quote) and (self.is_start_quote(token)):
                in_quote = True
                in_quotation = 'B-QUOTE'
            elif in_quote:
                in_quotation = 'I-QUOTE' 
                if self.is_end_quote(token):
                    in_quote = False
            else:
                in_quotation = 'O'
            quote_bio.append(in_quotation)
        return quote_bio

    def add_quote_info(self, fandom_fname, tok_data, global_token_id=None):
        """ Add quote information to token input file """
        # Load quotes
        quotes = []
        if self.quote_extraction_type == 'gold':
            quote_df = pd.read_csv(os.path.join(self.quote_dirpath, 
                f'{fandom_fname}_quote_attribution.csv'))
            if len(quote_df) == 0: # No quotes
                tok_data['inQuotation'] = 'O' 
                return tok_data
            for colname in quote_df.columns: # each column is a character
                for mention in quote_df[colname].dropna():
                    parts = mention.split('.')
                    chapter_id = int(parts[0])
                    paragraph_id = int(parts[1])
                    if '-' in parts[2]:
                        token_id_start = int(parts[2].split('-')[0])
                        token_id_end = int(parts[2].split('-')[-1])
                    else:
                        token_id_start = int(parts[2])
                        token_id_end = int(parts[2])
                    quotes.append(AnnotatedSpan(
                      chap_id=chapter_id,
                      para_id=paragraph_id,
                      start_token_id=token_id_start,
                      end_token_id=token_id_end,
                      annotation=colname
                  ))

            # Turn annotations into df
            if len(quotes) == 0:
                tok_data['inQuotation'] = 'O'
                return tok_data
            quote_data = pd.DataFrame([[annotation.annotation, annotation.text, 
                annotation.chap_id, annotation.para_id, annotation.start_token_id, 
                annotation.end_token_id] for annotation in quotes],
                columns=['character_name', 'tokens', 'chap_id', 'para_id', 
                    'start_token_id', 'end_token_id'])
            quote_data['span_start'] = [global_token_id[el] for el in tuple(zip(
                quote_data.chap_id, quote_data.para_id, quote_data.start_token_id))]
            quote_data['span_end'] = [global_token_id[el] for el in tuple(zip(
                quote_data.chap_id, quote_data.para_id, quote_data.end_token_id))]

            # Add BIO in quotations for tokens
            quote_data['span'] = [range(beg, end+1) for (beg, end) in zip(quote_data.span_start, quote_data.span_end)]
            quote_data_toks = quote_data.explode('span')
            quote_data_toks.reset_index(inplace=True)
            quote_data_toks.rename(columns={'index': 'quote_id'}, inplace=True)
            beg_quotes = quote_data_toks.groupby('quote_id').head(1).index
            quote_data_toks.loc[beg_quotes, 'inQuotation'] = 'B-QUOTE'
            quote_data_toks['inQuotation'] = quote_data_toks.inQuotation.fillna('I-QUOTE')
            tok2quote = quote_data_toks.set_index('span')['inQuotation'].to_dict()
            tok_data['inQuotation'] = tok_data.tokenId.map(
                lambda x: tok2quote.get(x, 'O'))

        elif self.quote_extraction_type == 'pipeline':
            tok_data['inQuotation'] = self.extract_quotes(fandom_fname, tok_data)
            # From PipelineOutput.extract_quotes
            #quote_predictions_fpath = os.path.join(self.quote_dirpath, 
            #    f'{fandom_fname}.quote.json')
            #with open(quote_predictions_fpath) as f:
            #    predicted_quotes = json.load(f)
            #for quote_entry in predicted_quotes:
            #    character = quote_entry['speaker']
            #    chap_id = quote_entry['chapter']
            #    para_id = quote_entry['paragraph']
            #    entry_quotes = quote_entry['quotes']
            #    for quote in entry_quotes:
            #        quotes.append(AnnotatedSpan(
            #            chap_id=chap_id, para_id=para_id, 
            #            start_token_id=quote['start_paragraph_token_id'], 
            #            end_token_id=quote['end_paragraph_token_id'], 
            #            annotation=character, 
            #        ))

        return tok_data

    def add_empty_cols(self, tok_data):
        """ Add empty columns for token output """
        empty_cols = [col for col in self.tok_cols if col not in tok_data.columns \
            and col != 'normalizedWord']
        tok_data['normalizedWord'] = tok_data['originalWord']
        tok_data.loc[:, empty_cols] = np.nan
        tok_data = tok_data[self.tok_cols]
        return tok_data

    def add_sent_para_ids(self, tok_data, fic_data):
        """ Add sentence and paragraph IDs. Unnecessary now (preprocess_tokens) """
        tok_data['paragraphId'] = fic_data.text_tokenized.str.split().explode().index
        return tok_data

    def build_tokens(self, tok_data, fic_data, coref_ents):
        """ Build token file """
        tok_data = self.add_coref_info(coref_ents, tok_data)
        tok_data = self.add_quote_info(self.fandom_fname, tok_data)
        #tok_data = self.add_para_ids(tok_data, fic_data)
        tok_data = self.add_empty_cols(tok_data)

        # Save tokens file
        tok_data.to_csv(os.path.join(self.out_dirpath, f'{self.fandom_fname}.tokens'),
            sep='\t', index=False)

    def get_global_token_id(self, toks):
        """ Get mapping from (chapter_id, para_id, token_id) to global token id """
        global_token_id = toks.set_index(['chapter_id', 'para_id', 
            'token_id'])['fic_token_id'].to_dict()
        return global_token_id

    def build_coref(self, fic_data=None):
        """ Build coref input """

        # Load annotated fanfiction coref output
        annotations = []
        annotations_set = set()

        if self.coref_type == 'gold':
            coref_anns = pd.read_csv(os.path.join(self.coref_dirpath, 
                f'{self.fandom_fname}_entity_clusters.csv'))
            for colname in coref_anns.columns: # each column is a character
                annotations_set.add(colname)
                for mention in coref_anns[colname].dropna():
                    parts = mention.split('.')
                    chapter_id = int(parts[0])
                    paragraph_id = int(parts[1])
                    if '-' in parts[2]:
                        token_id_start = int(parts[2].split('-')[0])
                        token_id_end = int(parts[2].split('-')[-1])
                    else:
                        token_id_start = int(parts[2])
                        token_id_end = int(parts[2])
                    annotations.append(AnnotatedSpan(
                      chap_id=chapter_id,
                      para_id=paragraph_id,
                      start_token_id=token_id_start,
                      end_token_id=token_id_end,
                      annotation=colname
                  ))
            fic_toks = fic_data.set_index(['chapter_id', 'para_id'], inplace=False)
            para_tokens = fic_toks['text_tokenized'].str.split().to_dict()
            for mention in annotations:
                if not (mention.chap_id, mention.para_id) in para_tokens:
                     raise ValueError(f"Chapter ID and paragraph ID in {mention}"
                         " not present in fic {self.file_path}")
                mention.text = ' '.join(para_tokens[
                     (mention.chap_id, mention.para_id)][
                     mention.start_token_id-1:mention.end_token_id])
            # Get coreference cluster IDs from annotation columns
            self.cluster_ids[self.fandom_fname] = {coref_anns.columns[i]: i for i in range(
                len(coref_anns.columns))}

        elif self.coref_type == 'spanbert':
            clusters = []
            for cluster in self.coref['clusters']:
                if 'name' not in cluster:
                    print('no name cluster')
                    continue
                clusters.append(cluster)
            char_names = [cluster['name'] for cluster in clusters]
            annotations_set = set(char_names)
            self.cluster_ids[self.fandom_fname] = {name: i for i, name in enumerate(
                char_names)}
            for cluster in clusters:
                for mention in cluster['mentions']:
                    if 'text' in mention:
                        annotations.append(AnnotatedSpan(
                            start_token_id=mention['position'][0],
                            end_token_id=mention['position'][1],
                            annotation=cluster['name'],
                            text=mention['text']
                        ))
                    elif 'phrase' in mention:
                        annotations.append(AnnotatedSpan(
                            start_token_id=mention['position'][0],
                            end_token_id=mention['position'][1],
                            annotation=cluster['name'],
                            text = mention['phrase']
                        ))
                annotations_set.add(cluster['name'])

            #coref_fic = pd.read_csv(os.path.join(self.coref_dirpath, 
            #    f'{self.fandom_fname}.coref.csv'))
            #with open(os.path.join(self.coref_dirpath.replace('stories', 'chars'),
            #    f'{fandom_fname}.chars')) as f:
            #    char_names = f.read().splitlines()
            #    self.cluster_ids[fandom_fname] = {name: i for i, name in enumerate(
            #        char_names)}
            #for row in list(coref_fic.itertuples()):
            #    mentions = extract_mention_tags(row.text_tokenized)
            #    for mention in mentions:
            #        mention.chap_id = row.chapter_id
            #        mention.para_id = row.para_id
            #        annotations.append(mention)
            #        annotations_set.add(mention.annotation)

        # Turn annotations into df
        coref_data = pd.DataFrame([
            [annotation.annotation, annotation.text, 
            annotation.start_token_id, annotation.end_token_id-1] \
            for annotation in annotations],
            columns=['coreference_name', 'tokens', 
                'span_start', 'span_end'])
        coref_data['coreference_id'] = coref_data.coreference_name.map(
            self.cluster_ids[self.fandom_fname].get)
        output_cols = ['coreference_id', 'tokens', 'span_start', 'span_end']
        coref_ents_data = coref_data[output_cols]

        # Save coref ents file
        coref_ents_data.to_csv(os.path.join(self.out_dirpath, 
            f'{self.fandom_fname}.ents'), sep='\t', header=False, index=False)

        return coref_ents_data


class AnnotatedSpan():
    def __init__(self,
            chap_id=None,
            para_id=None,
            start_token_id=None,
            end_token_id=None,
            annotation=None, # speaker for quotes, or character for character mentions
            text=''):
        self.chap_id = chap_id # starts with 1, just like annotations
        self.para_id = para_id # starts with 1, just like annotations
        self.start_token_id = start_token_id # starts over every paragraph, starts with 1 just like annotations
        self.end_token_id = end_token_id
        self.annotation = annotation
        self.text = text
        self.text_tokens = None
        
    def __repr__(self):
        return f"{self.chap_id}.{self.para_id}.{self.start_token_id}-{self.end_token_id},annotation={self.annotation}"
