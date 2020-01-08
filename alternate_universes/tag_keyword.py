import _pickle
import sys
from collections import Counter

config_path = sys.argv[1]
config_section = sys.argv[2]

import configparser
config = configparser.ConfigParser()
config.readfp(open(config_path))

search_string = sys.argv[3]
k = int(sys.argv[4])

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

stories_path = config.get(config_section,'stories_path')
stories_dir_path = config.get(config_section,'stories_dir_path')
tags_path = config.get(config_section,'tags_path')
df_path = config.get(config_section,'df_path')

import string
punctuation_set = set(string.punctuation)



with open(tags_path,'rb') as f:
	tags = _pickle.load(f)
with open(df_path,'rb') as f:
	df = _pickle.load(f)

N = df['totalN']

stories = []
for row in csv.DictReader(open(stories_path,encoding='utf-8')):
     stories.append(row)

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
	return list(set(fic_words))

def story_words(this_story):
	this_story = str(this_story.encode("ascii", "ignore"))
	this_story = ''.join(ch for ch in this_story if ch not in punctuation_set)
	words = this_story.split()
	#words = [i for i in words if i not in stopwords_set]
	#print 'he' in words
	words = lower_list(words)
	words = [str(lemmatizer.lemmatize(i)) for i in words]
	words = [i for i in words if i not in stopwords_set]
	return list(set(words))


# if search_string == 'highFreq':
# 	count = sys.argv[2]
# 	AU_all_words_counter = Counter(AU_rm_sw_l)
# 	print AU_all_words_counter.most_common(int(count))

# else:
out = []
aus = []
search_string_list = [str(lemmatizer.lemmatize(i)) for i in search_string.split()]
search_string_set = set(lower_list(search_string_list))
assert len(tags)==len(stories)
for i in range(len(tags)):
	this_aus =[]
	for j in tags[i]:
		if "au" in j or "alternate universe" in j:
			if (len((search_string_set) & set(lower_list(j.split())))==len(search_string_set)):
					out.append(i)
					# print j
					this_aus.append(j)
	aus.append(this_aus)
# out_join = [' '.join(i) for i in out]
# out_counter = Counter(out_join)
# print 'total occurence:',(len(out_join))
# print out_counter
#print 'total num of fictions:',len(out) 
out = list(set(out))
print('total num of fictions:',len(out))
out.sort()
au_words =[]
for i in out:
	# print stories[i]['fic_id'],' chapter_count:',stories[i]['chapter_count'],' AU:',aus[i]
	#print ' AU:',aus[i]
	this_story = fic_story_words(stories[i]['fic_id'],stories[i]['chapter_count'])
	# this_words = story_words(this_story)
	#print 'he' in this_words
	au_words.extend(this_story)
au_Counter = Counter(au_words)
# combine the df statistics
score ={}
for word in au_Counter:
	# print word,' ',df[word]
	idf = math.log(N/df[word])
	tf = au_Counter[word]
	score[word]=tf*idf
count = 0
s = sorted(score.items(),key=lambda x:x[1],reverse=True)
#for key, value in sorted(score., key=lambda (k,v): (v,k),reverse=True):
for key,value in s:
    if count==k:
    	break
    print ("%s: %s" % (key, value))
    count+=1

# print au_Counter.most_common(k)

