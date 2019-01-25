import pickle
import sys
from collections import Counter

# topn = int(sys.argv[1])
# cutoff = float(sys.argv[2])
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
topn = int(config.get(config_section,'topn'))
cutoff = float(config.get(config_section,'cutoff'))

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


#exclude_set = stopwords_set.union(punctuation_set)

with open(tags_path) as f:
	tags = pickle.load(f)
with open(df_path) as f:
	df = pickle.load(f)
with open(labels_path) as f:
	labels = f.readlines()

split_labels = [i.strip().split(',') for i in labels]
idx2fic = [[] for i in range(len(labels))]


idx2keywords = [[] for i in range(len(labels))]


label2idx ={}
for i in range(len(split_labels)):
	for j in split_labels[i]:
		label2idx[j]=i

stories = []
for row in csv.DictReader(open(stories_path)):
	stories.append(row)
fic2idx = [[] for i in range(len(stories))]

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
		# fname = "stories/"+fic_id+'_'+chap_id+".csv"
		fname = stories_dir_path+fic_id+'_'+chap_id+".csv"

		for row in csv.DictReader(open(fname)):
			this_story+=row["text"]
		chap_words = story_words(this_story)
		fic_words.extend(chap_words)
	return list(set(fic_words))

def story_words(this_story):
	this_story = this_story.encode("ascii", "ignore")
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
# search_string_list = [str(lemmatizer.lemmatize(i)) for i in search_string.split()]
# search_string_set = set(lower_list(search_string_list))
search_string_set = set(label2idx.keys())
assert len(tags)==len(stories)
for i in range(len(tags)):
	# this_aus =[]
	for j in tags[i]:
		if "au" in j or "alternate universe" in j:
			result_set = (search_string_set) & set(lower_list(j.split()))
			# if (len((search_string_set) & set(lower_list(j.split())))>0):
					# out.append(i)
					# print j
					# this_aus.append((search_string_set) & set(lower_list(j.split())))
			if len(result_set)>0:
					for k in result_set:
						idx = label2idx[k]
						idx2fic[idx].append(i)
						fic2idx[i].append(idx)
	# aus.append(this_aus)
# out_join = [' '.join(i) for i in out]
# out_counter = Counter(out_join)
# print 'total occurence:',(len(out_join))
# print out_counter
#print 'total num of fictions:',len(out) 
# out = list(set(out))
# print 'total num of fictions:',len(out)
# out.sort()
# au_words =[]
f=open(keywords_path,'wb')

for i in range(len(labels)):
	# idx = label2idx[i]
	au_words=[]
	for j in idx2fic[i]:
	# print stories[i]['fic_id'],' chapter_count:',stories[i]['chapter_count'],' AU:',aus[i]
	#print ' AU:',aus[i]
		this_story = fic_story_words(stories[j]['fic_id'],stories[j]['chapter_count'])
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
	top = False
	top_score = 0
	for key, value in sorted(score.iteritems(), key=lambda (k,v): (v,k),reverse=True):
		if top==False:
			top_score = value
			top = True
			f.write(str((key,value)))
			f.write('\t')
			idx2keywords[i].append((key,value))
		else:
			if len(idx2keywords[i])>topn:
				break
			if value<top_score*cutoff:
				break
				
			f.write(str((key,value)))
			idx2keywords[i].append((key,value))			
			f.write('\t')
	f.write('\n')
			# idx2keywords[i].append((key,value))

	    	# print "%s: %s" % (key, value)
f.close()
with open('fic2idx.pkl','wb') as f:
	pickle.dump(fic2idx,f)
# print au_Counter.most_common(k)

	






