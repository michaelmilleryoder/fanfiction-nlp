# -*- coding: utf-8 -*-
import sys
import os
import io
from os import listdir
from os.path import isfile, join
from multiprocessing import Pool
import itertools
import ctypes as ct

import numpy as np
import csv
from collections import defaultdict,Counter
import nltk
from sklearn.metrics.pairwise import cosine_similarity
from builtins import any
import json
import re
import pdb
import codecs
from tqdm import tqdm

#csv.field_size_limit(sys.maxsize)
csv.field_size_limit(int(ct.c_ulong(-1).value // 2))

"""
 input: i2w            -> dictionary, key:word_index, value: word
        formatted_sent -> a string of word indices that needs to be decoded

output: sentence       -> a decoded string where the word indices are replaced by the words
"""
def decode_sentence(i2w,formatted_sent):
    sentence = []
    for _id in formatted_sent.split():
        sentence.append(i2w[int(_id)])
    sentence = ' '.join(sentence)
    return sentence


def extract_assertion(para_dict,coref_info):
    """
     input: para_dict -> key:paragraph ID, value: dict of segmented sentences from that para
            coref_info -> 

    output: char_dict -> key: canonical name of character, values: dict with 'position' and 'text' as keys
    """
    char_dict = defaultdict(list)
    #For each paragraph and it's corresponding segments
    for (para_id, (segments, segment_ranges)) in para_dict.items():
        #For each segment
        for (segment_id,segment) in segments.items():
            segment_range = segment_ranges[segment_id]
            #For each character in character list
            for cluster in coref_info['clusters']:
                if not 'name' in cluster:
                    continue
                character = cluster['name']
                mention_positions = [m['position'] for m in cluster['mentions']]
                if any(pos[0] >= segment_range[0] and pos[1] <= segment_range[1] \
                    for pos in mention_positions):
                    char_dict[character].append({'position': segment_range, 
                        'text': segment.strip()})
                #if character in segment:
                #    #Added fix for quotation removal 
                #    #(would be ideal to use the same as quote attribution does 
                #    #if possible)

                #    # Replace quote tags so don't interfere
                #    segment = re.sub(r'<character name="(.+?)">', r'<character name=|||\1|||>', segment)

                #    #segment = re.sub(r'\s".*?"\s', '', segment)
                #    #segment = re.sub(r'(^|\s)(“|``|"+|«).+?(”|\'\'|"+|»)(\s|$)', ' ', segment)
                #    segment = re.sub(r'(^|\s)(“|``|"+|«).+?(”|\'\'|"+|»)', ' ', segment)
                #    segment = re.sub(r' +', ' ', segment)

                #    # Put quote tags back in
                #    segment = segment.replace('|||', '"')
                #    char_dict[character].append(segment.strip())
    return char_dict


def remove_quotes(segment_range, segment):
    """ Removes quotes from span with character mentions. """
    pass


def get_topic_segments(para_id,para,offset,k=1):
    """
     input: para_id  -> int, id for the paragraph
            para     -> the string (paragraph) to be segmented
            offset   -> the beginning token ID for the paragraph in the whole text
            k        -> int, a hyperparameter for text-tiling
                            which defines the tiling window

    output: (segments -> a dict, key:segment_id, value:segments of the paragraph,
             segment_range -> a dict, segment_id:range of token IDs,
             new_offset)
            
    """
    # Build the vocabulary for this paragraph
    vocab = defaultdict(lambda: len(vocab))
   
    #para = para.decode('utf-8')
    #The UTF-8 decode is not required if the Terminal locale is set properly using
    #export LC_CTYPE=en_US.UTF-8
    #export LC_ALL=en_US.UTF-8
    
    # Get list of sentences in the paragraph
    sentences = nltk.sent_tokenize(para)
    
    segments = defaultdict(str)
    #if there's only one sentence in the paragraph, return it as a segment
    if 1 == len(sentences):
        segments[0] = para
    else:
        formatted_sents = []

        # Convert all the words to ints
        for sentence in sentences:
            temp = [str(vocab[word]) for word in sentence.split()]
            int_text = ' '.join(temp)
            if int_text != ' ':
                formatted_sents.append(int_text)

        #dict for the reverse mapping from integers to words
        i2w = {int(v): k for k, v in vocab.items()}

        #sentence vector is a dict of list of counts for the entire vocab per sentence
        #it is basically a co-occurence matrix of sentences and the words in the vocabulary
        sentence_vector = defaultdict(lambda: [0] * len(vocab))

        #Build the co-occurence matrix
        for idx,sent in enumerate(formatted_sents):
            word_ids = sent.split()
            word_ids = [int(_id) for _id in word_ids]
            #For each sentence, idx,
            #increment the count of each word , _id, encountered in the sentence
            for _id in word_ids:
                sentence_vector[idx][_id] += 1
                
        sim_scores = {}        
        for i in range(k,len(formatted_sents)-k):

            left_vectors = []
            #the left half of the text-tiling window
            for j in range(i-k,i):
                left_vectors.append(sentence_vector[j])
            left_aggregate = np.sum(np.array(left_vectors), axis=0)
            
            right_vectors = []
            #the right half of the text-tiling window
            for j in range(i,i+k):
                right_vectors.append(sentence_vector[j])
            right_aggregate = np.sum(np.array(right_vectors), axis=0)

            if np.sum(left_aggregate) == 0.0 or np.sum(right_aggregate) == 0.0:
                sim_scores[i] = 0.0
            else:
                sim_scores[i] = cosine_similarity([left_aggregate], [right_aggregate])[0][0]
        
        # Compute the depth score for each sequence gap index
        depth = {}
        for gap in sim_scores:
            left_peak = sim_scores[gap]
            right_peak = sim_scores[gap]

            # Compute the peak for left diff
            for i in range(gap, 0, -1):
                if sim_scores[i] > left_peak:
                    left_peak = sim_scores[i]
                else:
                    break

            # Compute the peak for right diff
            for i in range(gap+1, len(sim_scores.keys())):
                if sim_scores[i] > right_peak:
                    right_peak = sim_scores[i]
                else:
                    break

            left_diff = left_peak - sim_scores[gap]
            right_diff = right_peak - sim_scores[gap]
            depth[gap] = left_diff + right_diff

        # Compute the segment indexes (gap value indexes) from the thresholding depth scores
        depth_scores = np.array(list(depth.values()))
        
        #Collect only non_zero scores
        non_zero = [score for score in depth_scores if score > 0.0]
        boundaries = []
        if len(non_zero) == 0:
            #No non zero depth scores. Putting all the sentences in one segment
            segments[0] = para
        else:
            threshold = np.mean(non_zero) - np.std(non_zero)/2.0
            for idx,score in depth.items():
                if score > threshold:
                    boundaries.append(idx)

                # Compute the segment membership and return the resultant dictionary
            idx = 0
            j = 0
            for b_idx in boundaries:
                for i in range(idx, b_idx+1):
                    segments[j] += ' '+decode_sentence(i2w,formatted_sents[i])
                idx = b_idx+1
                j += 1

            # Assign the last tail of sentences
            if idx < len(formatted_sents):
                seg_id = idx
                for i in range(idx, len(formatted_sents)):
                    segments[j] += ' '+decode_sentence(i2w,formatted_sents[i])

            #print ("SEGMENTS",segments,"SEGMENTS")

            # Check for quotations splitting segments incorrectly
            #for segment_id, segment in segments.items():
            for segment_id in list(segments):
                segment = segments[segment_id]
                if segment.endswith('"') and segment.count('"') % 2 == 1:
                    # Move ending quotation mark to next segment
                    segments[segment_id+1] = segment[-1] + segments[segment_id+1]
                    segments[segment_id] = segments[segment_id][:-1].strip()

    # Go through segments to get range of token IDs (probably could incorporate this earlier)
    segment_ranges = {}
    for para_id, text in segments.items():
        n_segment_toks = len(text.split())
        beg_ind = offset
        end_ind = offset + n_segment_toks
        segment_ranges[para_id] = (beg_ind, end_ind)
        offset += n_segment_toks
    return (segments, segment_ranges, offset)

def process_file(params):
    fname, fic_dir, coref_dir, op_dir = params
    fandom_fname = fname.split('.')[0]

    # Check if has already been processed
    if os.path.exists(os.path.join(op_dir, fandom_fname + '.json')):
        return

    #get the story_chapter name from the story file
    #for matching with the characters file 
    #if 'txt' not in f:
    #    fic = f.split('.coref.csv')[0]
    #else: # only process CSVs
    #    continue
    #
    #char_f = chars_dir + '/' + fic + ".chars"
    #char_list = []
    para_dict = {}
   
    ##Get list of characters for each chapter
    #char_file = codecs.open(char_f, "r", errors='ignore') #io.open(char_f,'r', encoding="utf-8")
    #char_list = [character.rstrip() for character in char_file]

    # Load coref info
    coref_fpath = os.path.join(coref_dir, fandom_fname+'.json')
    if not os.path.exists(coref_fpath):
        tqdm.write('no coref file, skipping')
        return
    with open(coref_fpath) as coref_file:
        coref = json.load(coref_file)

    # Load quotes (to remove them from assertions)
    #quotes_fpath = os.path.join(quotes_dir, fandom_fname+'.quote.json')
    #if not os.path.exists(quotes_fpath):
    #    tqdm.write('no quotes file, skipping')
    #    return
    #with open(quotes_fpath) as quote_file:
    #    quotes = json.load(quote_file)
    # TODO: add in quote processing here
    
    #Get the segments for each paragraph in each chapter of a fic
    f = os.path.join(fic_dir, fandom_fname + '.csv')
    inp_file = codecs.open(f, "r", errors='ignore')#open(f)
    #csv_reader = csv.reader(inp_file, delimiter=',')
    #next(csv_reader)
    csv_reader = csv.DictReader(inp_file, delimiter=',')
    offset = 0 # token offset for paragraphs
    for row in csv_reader:
        #para_id = row[2]
        #para    = row[3]
        #para_id = row['paragraph_id']
        para_id = row['para_id']
        para    = row['text_tokenized']
        segments, segment_ranges, offset = get_topic_segments(para_id,para,
            offset,1)
        para_dict[para_id] = (segments, segment_ranges)

    #Extract the character assertions per file.
    if para_dict is not None and len(coref['clusters']) > 0:
        assertions = extract_assertion(para_dict,coref)
        j_file = codecs.open(op_dir + '/' + fandom_fname + '.json', "w", 
            errors='ignore')#open(op_dir + '/'+ fic + '.json','w')
        json.dump(assertions,j_file)


def main():
    #command line arguments
    fic_dir = str(sys.argv[1])
    coref_dir = str(sys.argv[2])
    quote_dir = str(sys.argv[3])
    op_dir    = str(sys.argv[4])
    n_threads = int(sys.argv[5])
    #files = [f for f in listdir(fic_dir) if isfile(join(fic_dir, f)) and \
    #    not f.startswith('.')]
    files = [f for f in listdir(coref_dir) if isfile(join(coref_dir, f)) and \
        not f.startswith('.')]

    params = zip(files,
                itertools.repeat(fic_dir), itertools.repeat(coref_dir),
                itertools.repeat(op_dir))
    if n_threads > 1:
        with Pool(n_threads) as p:
            list(tqdm(p.imap(process_file, params), total=len(files), ncols=70))
    else:
        list(map(process_file, tqdm(params, ncols=70, total=len(files))))
        #for f in tqdm(sorted(files), ncols=50):


if __name__ == '__main__': main()
