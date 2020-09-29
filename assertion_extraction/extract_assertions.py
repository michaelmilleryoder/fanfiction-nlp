# -*- coding: utf-8 -*-
import sys
import os
import io
from os import listdir
from os.path import isfile, join
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

csv.field_size_limit(sys.maxsize)

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


"""
 input: para_dict -> key:paragraph ID, value: dict of segmented sentences from that para
        char_list -> a list of characters in the format $_canonical_name

output: char_dict -> key: canonical name of character, value: list of segments
"""
def extract_assertion(para_dict,char_list):
    char_dict = defaultdict(list)
    #For each paragraph and it's corresponding segments
    for (para_id,segments) in para_dict.items():
        #For each segment
        for (segment_id,segment) in segments.items():
            #For each character in character list
            for character in char_list:
                if character in segment:
                    #Added fix for quotation removal
                    segment = re.sub(r'".*?"', '', segment)
                    char_dict[character].append(segment)
    return char_dict


"""
 input: para_id  -> int, id for the paragraph
        para     -> the string (paragraph) to be segmented
        k        -> int, a hyperparameter for text-tiling
                        which defines the tiling window

output: segments -> a dictionary, key:segment_id, value:segments of the paragraph
"""
def get_topic_segments(para_id,para,k=1):
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
    if (1 == len(sentences)):
        segments[0] = para
        return segments
    
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
        return segments
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
    return segments


def main():
    #command line arguments
    input_dir = str(sys.argv[1])
    chars_dir = str(sys.argv[2])
    op_dir    = str(sys.argv[3])

    files =      [f for f in listdir(input_dir) if isfile(join(input_dir, f))]

    for f in tqdm(files, ncols=50):

        #get the story_chapter name from the story file
        #for matching with the characters file 
        if 'txt' not in f:
            fic = f.split('.coref.csv')[0]
        else: # only process CSVs
            continue
        
        char_f = chars_dir + '/' + fic + ".chars"
        char_list = []
        para_dict = {}
       
        #Get list of characters for each chapter
        char_file = codecs.open(char_f, "r", errors='ignore') #io.open(char_f,'r', encoding="utf-8")
        char_list = [character.rstrip() for character in char_file]
        
        #Get the segments for each paragraph in each chapter of a fic
        f = input_dir + '/' + f
        inp_file = codecs.open(f, "r", errors='ignore')#open(f)
        #csv_reader = csv.reader(inp_file, delimiter=',')
        #next(csv_reader)
        csv_reader = csv.DictReader(inp_file, delimiter=',')
        for row in csv_reader:
            #para_id = row[2]
            #para    = row[3]
            para_id = row['paragraph_id']
            para    = row['text_tokenized'] # after coref this column has <character tags>
            segments = get_topic_segments(para_id,para,1)
            para_dict[para_id] = segments

        #Extract the character assertions per file.
        if para_dict is not None and char_list is not None:
            assertions = extract_assertion(para_dict,char_list)
            j_file = codecs.open(op_dir + '/' + fic + '.json', "w", errors='ignore')#open(op_dir + '/'+ fic + '.json','w')
            json.dump(assertions,j_file)



if __name__ == '__main__': main()







##################################
# DEBUG ZONE
##################################
"""     

segments = get_topic_segments(1,para3,1)
#print (segments)
for k,v in segments.items():
    print (k,v)
"""
##The following paragraphs can be used for debugging
#para1 = """Lucy's jaw dropped at the sight. She suddenly stopped walking silenced herself after quietly singing along to ABBA that played loudly through her blue headphones. The place was huge. As she looked around the place she noticed occasional flashes of green light as more people arrived through a burning green flame. What she also noticed was that all the people wandering around were dressed on long draping cloaks or sometimes a 'normal' looking suit. It was also extremely crowded and the young adult had no idea where she was going. Lucy took a quick glance down at the piece of old parchment that was held in her hand which read 'The Misuse of Muggle Artifacts'. She could tell that the man was obviously excited and it made her slightly relieved that he wasn't like the blonde man who directed her to the office. Maybe she could fit in here. As she introduced herself she let a friendly smile spread across her face. "Hello, it's wonderful to meet you too, and it's such an honor to be here," She said with a small nod before adding "My name's Lucy, by the way. Lucy Harren." """

#para2 = """Angelina Johnson, Alicia Spinnet and Danielle Mcdonald showed a visible reaction when Harry introduced himself. However, they weren't as rude as the people in Diagon Alley. After a bit of awkward small talk and a few hesitant questions on their part, the girls began to share their knowledge on how to survive Hogwarts with him. Harry had no idea if they were teasing him or if they were serious. They described the teachers and the classes and he also received an in-depth explanation of Quidditch. Lee Jordan and the twins George and Fred Weasley joined them an hour later. Lee had to leave immediately since Danielle didn't want his tarantula anywhere near her but the Weasley Twins stayed a little while longer. These two knew the castle like the back of their hands and told Harry about two lesser-known shortcuts to make sure he will never show up late for Potions. They considered Gryffindor to be the best House in Hogwarts and showed a certain dislike of Slytherin. Hagrid had felt similar about the Houses. However, Harry was determined to stay open-minded."""

#para3 = """He could somehow understand Dumbledore's decision to place him with the Dursleys. They were his only family, after all. The real reason for Harry's suspicion were the articles which had been published about him in the last decade. According to the articles, Dumbledore had repeatedly assured the magical community that Harry was safe and happy, which, of course, wasn't exactly true. This meant that either Dumbledore hadn't bothered or had forgotten to check on him all those years and had just told them what they wanted to hear, or he knew about his life with the Dursleys and had lied. Both explanations didn't show Dumbledore in the most flattering light."""

