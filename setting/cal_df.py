import pickle
import sys
from collections import Counter

import csv
import copy
import sys  

reload(sys)
sys.setdefaultencoding('utf8')

import nltk
from nltk.stem import WordNetLemmatizer 
lemmatizer = WordNetLemmatizer()
# lemmatizer.lemmatize("power bank")

import nltk
from nltk.corpus import stopwords
stopwords_set=set(stopwords.words('english'))
stopwords_set = set([str(i) for i in list(stopwords_set)])
#print 'he' in stopwords_set

import string
punctuation_set = set(string.punctuation)

config_path = sys.argv[1]
config_section = sys.argv[2]
import ConfigParser
config = ConfigParser.ConfigParser()
config.readfp(open(config_path))

# get config parameters

stories_path = config.get(config_section,'stories_path')
stories_dir_path = config.get(config_section,'stories_dir_path')

df_path = config.get(config_section,'df_path')

stories = []
for row in csv.DictReader(open(stories_path)):
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
	all_word_count=0
	chapter_ids = generate_chapter_id(chapter_count)
	for chap_id in chapter_ids:
		this_story = ""
		fname = stories_dir_path+fic_id+'_'+chap_id+".csv"
		for row in csv.DictReader(open(fname)):
			this_story+=row["text"]
		chap_words,word_count = story_words(this_story)
		all_word_count+=word_count
		fic_words.extend(chap_words)
	return fic_words,all_word_count

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
	return list(set(words)),len(words)


words = []
word_counts =[]

N = 0
for i in range(len(stories)):
	# print stories[i]['fic_id'],' chapter_count:',stories[i]['chapter_count'],' AU:',aus[i]
	# print ' AU:',aus[i]
	N+=int(stories[i]['chapter_count'])
	this_words,this_word_count = fic_story_words(stories[i]['fic_id'],stories[i]['chapter_count'])
	# this_words = story_words(this_story)
	#print 'he' in this_words
	words.extend(this_words)
	word_counts.append(this_word_count)
word_counter = Counter(words)

# insert N as an entry to the word_counter
word_counter['totalN']=N
word_counter['avg_doc_len']=sum(word_counts)/float(len(word_counts))

f = open(df_path,'wb')
pickle.dump(word_counter,f)
f.close()

print 'total num:',N
print 'avg_doc_len:',word_counter['avg_doc_len']




