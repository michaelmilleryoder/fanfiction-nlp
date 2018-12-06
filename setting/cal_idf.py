import pickle
import sys
from collections import Counter
# search_string = sys.argv[1]
#k = int(sys.argv[1])
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

#exclude_set = stopwords_set.union(punctuation_set)

#with open('tags_rm_sw_l_.txt') as f:
#	tags = pickle.load(f)

stories = []
for row in csv.DictReader(open("stories.csv")):
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
		fname = "stories/"+fic_id+'_'+chap_id+".csv"
		for row in csv.DictReader(open(fname)):
			this_story+=row["text"]
		chap_words = story_words(this_story)
		fic_words.extend(chap_words)
	return fic_words

# def chap_story(fic_id,chap_id):
# 	this_story = ""
# 	fname = "stories/"+fic_id+'_'+chap_id+".csv"
# 	for row in csv.DictReader(open(fname)):
# 		this_story+=row["text"]
# 	return this_story

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
#assert len(tags)==len(stories)
#for i in range(len(tags)):
#	this_aus =[]
#	for j in tags[i]:
#		if "au" in j or "alternate universe" in j:
			# if (len((search_string_set) & set(lower_list(j.split())))==len(search_string_set)):
#				out.append(i)
					# print j
#				this_aus.append(j)
#	aus.append(this_aus)
# out_join = [' '.join(i) for i in out]
# out_counter = Counter(out_join)
# print 'total occurence:',(len(out_join))
# print out_counter
#print 'total num of fictions:',len(out) 
# out = list(set(out))
# print 'total num of fictions:',len(out)
# out.sort()
au_words =[]
N = 0
for i in range(len(stories)):
	# print stories[i]['fic_id'],' chapter_count:',stories[i]['chapter_count'],' AU:',aus[i]
	# print ' AU:',aus[i]
	N+=int(stories[i]['chapter_count'])
	this_words = fic_story_words(stories[i]['fic_id'],stories[i]['chapter_count'])
	# this_words = story_words(this_story)
	#print 'he' in this_words
	au_words.extend(this_words)
au_Counter = Counter(au_words)
#print au_Counter.most_common()[-k:]

f = open('df_new','wb')
pickle.dump(au_Counter,f)
f.close()
# for i in au_Counter:
# 	f.write(i+"	"+str(au_Counter[i]))
# 	f.write("\n")
# f.close()
print 'total num:',N





