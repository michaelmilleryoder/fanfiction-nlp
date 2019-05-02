import pickle
import sys
from collections import Counter
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

# N = 73645
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
fic2idx_path = config.get(config_section,'fic2idx_path')
idx2fic_path = config.get(config_section,'idx2fic_path')
idx_wordcount_path = config.get(config_section,'idx_wordcount_path')
idx_prob_path = config.get(config_section,'idx_prob_path')


#exclude_set = stopwords_set.union(punctuation_set)

# with open('tags_rm_sw_l_.txt') as f:
# 	tags = pickle.load(f)
with open(df_path,'rb') as f:
	df = pickle.load(f)
# with open('clean_labels.txt') as f:
# 	labels = f.readlines()
with open(fic2idx_path,'rb') as f:
	fic2idx = pickle.load(f)
with open(idx2fic_path,'rb') as f:
	idx2fic =pickle.load(f)


stories = []
for row in csv.DictReader(open(stories_path,encoding='utf-8')):
	stories.append(row)

N = len(stories)

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
		fname = stories_dir_path+fic_id+'_'+chap_id+".csv"
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


f = open(idx_wordcount_path,'wb')

idxprob =[]
for i in range(len(idx2fic)):

	idxprob.append(len(idx2fic[i])/float(N))
	au_words=[]
	for ficidx in idx2fic[i]:
		this_story = fic_story_words(stories[ficidx]['fic_id'],stories[ficidx]['chapter_count'])
		au_words.extend(this_story)

	this_au_c = Counter(au_words)
	for w,c in this_au_c.most_common():
		f.write(str((w,c)).encode())
		f.write('\t'.encode())
	f.write('\n'.encode())

f.close()

with open(idx_prob_path,'wb') as f:
	pickle.dump(idxprob,f)




