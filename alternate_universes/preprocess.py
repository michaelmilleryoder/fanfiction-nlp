import sys
import _pickle
from collections import Counter
config_path = sys.argv[1]
config_section = sys.argv[2]
import configparser
config = configparser.ConfigParser()
config.readfp(open(config_path))

# get config parameters
stories_path = config.get(config_section,'stories_path')
stories_dir_path = config.get(config_section,'stories_dir_path')
tags_path = config.get(config_section,'tags_path')
aus_path = config.get(config_section,'aus_path')

# df_path = config.get(config_section,'df_path')
# labels_path = config.get(config_section,'labels_path')

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

def lower_list(a):
	return [i.lower() for i in a]

stories = []
for row in csv.DictReader(open(stories_path,encoding='utf-8')):
	stories.append(row)

tags =[]
tags_out = []
aus =[]
for i in range(len(stories)):
	tags.append(stories[i]['additional tags'])

for i in tags:
	this_tag = []
	for j in eval(i):
		j = str(j.encode("ascii", "ignore"))
#		print(i,j)
#		print([ch for ch in j if ch not in punctuation_set])
		j = ''.join([ch for ch in j if ch not in punctuation_set])
		j = j.split()

		j = lower_list(j)
		j = [str(lemmatizer.lemmatize(k)) for k in j]
		j = [k for k in j if k not in stopwords_set]
		j_out = ' '.join(j)
		if 'au' in j_out or 'alternate universe' in j_out:
			aus.append(j_out)
		this_tag.append(j_out) 
	tags_out.append(this_tag)

with open(tags_path,'wb') as f:
	_pickle.dump(tags_out,f)
f.close()

aus_c = Counter(aus)
with open(aus_path,'wb') as f:
	_pickle.dump(aus,f)
f.close()
# extract aus from tags


