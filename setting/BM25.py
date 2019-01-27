import pickle
import sys
from collections import Counter
import os

config_path = sys.argv[1]
config_section = sys.argv[2]
import ConfigParser
config = ConfigParser.ConfigParser()
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
output_path = config.get(config_section,'bm25_output_path')

test_txt_dir = config.get(config_section,'test_txt_dir')

k1 = float(config.get(config_section,'bm25_k1'))
b = float(config.get(config_section,'bm25_b'))
cutpt = float(config.get(config_section,'bm25_cutpt'))
percent = float(config.get(config_section,'bm25_percent'))

import csv
import copy
import math

import nltk
from nltk.stem import WordNetLemmatizer 
lemmatizer = WordNetLemmatizer()
# lemmatizer.lemmatize("power bank")
reload(sys)
sys.setdefaultencoding('utf8')

import nltk
from nltk.corpus import stopwords
stopwords_set=set(stopwords.words('english'))
stopwords_set = set([str(i) for i in list(stopwords_set)])
#print 'he' in stopwords_set

import string
punctuation_set = set(string.punctuation)


# with open(tags_path) as f:
# 	tags = pickle.load(f)
with open(df_path) as f:
	df = pickle.load(f)
with open(labels_path) as f:
	labels = f.readlines()
with open(fic2idx_path) as f:
	fic2idx = pickle.load(f)
with open(idx2fic_path) as f:
	idx2fic =pickle.load(f)
with open(keywords_path) as f:
	keywords = f.readlines()

N = df['totalN']
avg_doclen = df['avg_doc_len']

keywords = [i.strip().split('\t') for i in keywords]
queries = []
for i in keywords:
	if i[0]=='':
		queries.append([])
	else:
		queries.append([eval(j)[0] for j in i])


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
		for row in csv.DictReader(open(fname)):
			this_story+=row["text"]
		chap_words = story_words(this_story)
		fic_words.extend(chap_words)
	# return list(set(fic_words))
	return fic_words

def story_words(this_story):
	this_story = this_story.encode("ascii", "ignore")
	this_story = ''.join(ch for ch in this_story if ch not in punctuation_set)
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
	this_story = [i.encode("ascii", "ignore") for i in this_story]
	this_story = ''.join(this_story)
	this_story = ''.join(ch for ch in this_story if ch not in punctuation_set)
	words = this_story.split()

	words = lower_list(words)
	words = [str(lemmatizer.lemmatize(i)) for i in words]
	words = [i for i in words if i not in stopwords_set]

	return words

out = []
aus = []

def cal_BM25(doc_c,doc_len,query):
	if len(query)==0:
		return float('-inf')
	score =0
	for w in query:
		if w not in doc_c:
			continue
		idf = max(math.log((N-df[w]+0.5)/(df[w]+0.5)),0)
		tf = doc_c[w]/(doc_c[w]+k1*((1-b)+b*doc_len/avg_doclen))
		score+=idf*tf
	return score

if len(test_txt_dir)==0:

	stories = []
	for row in csv.DictReader(open(stories_path)):
		stories.append(row)

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
		# this_words = story_words(this_story)
		#print 'he' in this_words
			# au_words.extend(this_story)
		# au_Counter = Counter(au_words)
		this_doc_c = Counter(this_story)
		scores =[]
		for q in queries:
			scores.append(cal_BM25(this_doc_c,len(this_story),q))
		max_score = max(scores)
		if max_score<cutpt:
			continue
		labels = [(j,scores[j]) for j in range(len(scores)) if scores[j]>max_score*percent]
		assign_labels[i]=labels

	with open(output_path+'pkl','wb') as f:
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

			this_doc_c = Counter(this_story)

			scores =[]
			for q in queries:
				scores.append(cal_BM25(this_doc_c,len(this_story),q))
			max_score = max(scores)
			if max_score<cutpt:
				continue
			labels = [(labels[j],scores[j]) for j in range(len(scores)) if scores[j]>max_score*percent]
			assign_labels.append(labels)
			out.write(filename+':'+'\t')
			for label in labels:
				out.write(str(label)+'\t')
		out.write('\n')
		f.close()
	out.close()


# with open(output_path,'wb') as f:
# 	pickle.dump(assign_labels,f)
	







