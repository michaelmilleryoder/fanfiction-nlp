import pickle
import sys
from collections import Counter
import os
# search_string = sys.argv[1]
# k1 = float(sys.argv[1])
# b = float(sys.argv[2])

import csv
import copy
import math

import nltk
from nltk.stem import WordNetLemmatizer 
lemmatizer = WordNetLemmatizer()
# lemmatizer.lemmatize("power bank")
#reload(sys)
#sys.setdefaultencoding('utf8')

import nltk
from nltk.corpus import stopwords
stopwords_set=set(stopwords.words('english'))
stopwords_set = set([str(i) for i in list(stopwords_set)])
#print 'he' in stopwords_set

import string
punctuation_set = set(string.punctuation)

config_path = sys.argv[1]
config_section = sys.argv[2]
import configparser
config = configparser.ConfigParser()
config.readfp(open(config_path))

# get config parameters
stories_path = config.get(config_section,'stories_path')
stories_dir_path = config.get(config_section,'stories_dir_path')
tags_path = config.get(config_section,'tags_path')
df_path = config.get(config_section,'df_path')
labels_path = config.get(config_section,'labels_path')
keywords_path = config.get(config_section,'keywords_path')
# keyword_set_path = config.get(config_section,'keyword_set_path')
fic2idx_path = config.get(config_section,'fic2idx_path')
idx2fic_path = config.get(config_section,'idx2fic_path')
idx_wordcount_path = config.get(config_section,'idx_wordcount_path')
idxprob_path = config.get(config_section,'idx_prob_path')

test_txt_dir = config.get(config_section,'test_txt_dir')
output_path = config.get(config_section,'nb_output_path')


with open(df_path,'rb') as f:
	df = pickle.load(f)
with open(labels_path,'rb') as f:
	labels = f.readlines()
with open(fic2idx_path,'rb') as f:
	fic2idx = pickle.load(f)
with open(idx2fic_path,'rb') as f:
	idx2fic =pickle.load(f)
with open(idx_wordcount_path,'rb') as f:
	idx_wc = f.readlines()
with open(idxprob_path,'rb') as f:
	idxprob = pickle.load(f)
# with open(keyword_set_path) as f:
# 	keyword_set = pickle.load(f)
with open(keywords_path,'rb') as f:
	keywords = f.readlines()

keywords = [i.decode().strip().split('\t') for i in keywords]

all_keywords = []
for i in keywords:
	if i[0]=='':
		continue
	else:
		all_keywords.extend([eval(j)[0] for j in i])

all_keywords = set(all_keywords)

idx_wc = [i.decode().strip().split('\t') for i in idx_wc]
idx_wc_dict=[]
# idx_length=[]
for i in idx_wc:
	this_dict={}
	for k in i:
		if len(k)==0:
			break
		this_dict[eval(k)[0]]=eval(k)[1]
	idx_wc_dict.append(this_dict)


def lower_list(a):
	return [i.lower() for i in a]

def generate_chapter_id(chapter_count):
	out =[]
	for i in range(int(chapter_count)):
		out.append('0'*(4-len(str(i+1)))+str(i+1))
	return out

def fic_story_words(fic_id,chapter_count):
	fic_words =[]
	chapter_ids = generate_chapter_id(chapter_count)
	for chap_id in chapter_ids:
		this_story = ""
		fname = "stories/"+fic_id+'_'+chap_id+".csv"
		for row in csv.DictReader(open(fname,encoding='utf-8')):
			this_story+=row["text"]
		chap_words = story_words(this_story)
		fic_words.extend(chap_words)
	# return list(set(fic_words))
	return fic_words

def story_words(this_story):
	this_story = this_story.encode("ascii", "ignore")
	this_story = ''.join(ch for ch in this_story.decode() if ch not in punctuation_set)
	words = this_story.split()
	#words = [i for i in words if i not in stopwords_set]
	#print 'he' in words
	words = lower_list(words)
	words = [str(lemmatizer.lemmatize(i)) for i in words]
	words = [i for i in words if i not in stopwords_set]
	# return list(set(words))
	return words

def story_words_txt(this_story):
	this_story = [i.decode(errors="replace") for i in this_story]
	this_story = [i.encode("ascii", "ignore").decode() for i in this_story]
	this_story = ''.join(this_story)
	this_story = ''.join(ch for ch in this_story if ch not in punctuation_set)
	words = this_story.split()

	words = lower_list(words)
	words = [str(lemmatizer.lemmatize(i)) for i in words]
	words = [i for i in words if i not in stopwords_set]

	return words


# else:
out = []
aus = []


def nb_prob(story,idx):
	if idxprob[idx]==0:
		return float('-inf')
	this_idx_prob = idxprob[idx]
	this_wc = idx_wc_dict[idx]
	total=sum([this_wc[j] for j in this_wc if j in all_keywords])
	score=0
	for i in story:
		if i not in all_keywords:
			continue
		if i not in this_wc:
			w_c =0
		else:
			w_c = this_wc[i]
		score+=math.log((w_c+1)/float(total+len(all_keywords)))
	score+=math.log(this_idx_prob)
	return score

if len(test_txt_dir)==0:

	stories = []
	for row in csv.DictReader(open("stories.csv",encoding='utf-8')):
		stories.append(row)
# ficid2idx = [[] for i in range(len(stories))]
	assign_labels=[[-1] for i in range(len(stories))]
	for i in range(len(fic2idx)):
		if len(fic2idx[i])>0:
		# mark assigned fanfic
			assign_labels[i]=[-2]

	for i in range(len(stories)):

		if assign_labels[i]==[-2]:
			# already marked
			continue
		this_story = fic_story_words(stories[i]['fic_id'],stories[i]['chapter_count'])
		
		scores =[]
		for idx in range(len(idx2fic)):
			scores.append(nb_prob(this_story,idx))
		max_score = max(scores)
		# print scores
		# if max_score:
		# 	continue
		labels = [(j,scores[j]) for j in range(len(scores)) if scores[j]==max_score]
		assign_labels[i]=labels

	with open(nb_output_path+'.pkl','wb') as f:
		pickle.dump(assign_labels,f)

else:
	filenames =[]
	assign_labels =[]
	out = open(output_path+'.txt','wb')

	for filename in os.listdir(test_txt_dir):
		if filename.endswith(".txt"): 
			filenames.append(filename)
		else:
			continue

	for filename in filenames:

		with open(test_txt_dir+filename,'rb') as f:
			this_story = f.readlines()
			this_story = story_words_txt(this_story)
			scores =[]
			for idx in range(len(idx2fic)):
				scores.append(nb_prob(this_story,idx))
			max_score = max(scores)
		# print scores
		# if max_score:
		# 	continue
			new_labels = [(labels[j],scores[j]) for j in range(len(scores)) if scores[j]==max_score]

			assign_labels.append(new_labels)
			out.write((filename+':'+'\t').encode())
			for label in new_labels:
				out.write((str(label)+'\t').encode())
		out.write('\n'.encode())
		f.close()
	out.close()
	





