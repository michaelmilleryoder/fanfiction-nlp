import pickle
import sys
from collections import Counter

config_path = sys.argv[1]
config_section = sys.argv[2]
import ConfigParser
config = ConfigParser.ConfigParser()
config.readfp(open(config_path))

search_string = sys.argv[3]

# get config parameters

tags_path = config.get(config_section,'tags_path')
aus_path = config.get(config_section,'aus_path')
stories_path = config.get(config_section,'stories_path')

import nltk
from nltk.stem import WordNetLemmatizer 
lemmatizer = WordNetLemmatizer()
# lemmatizer.lemmatize("power bank")

with open(tags_path) as f:
	tags = pickle.load(f)

import csv
stories = []
for row in csv.DictReader(open(stories_path)):
     stories.append(row)

def lower_list(a):
	return [i.lower() for i in a]

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
print 'total num of fictions:',len(out)
out.sort()
for i in out:
	print stories[i]['fic_id'],' chapter_count:',stories[i]['chapter_count'],' AU:',aus[i]


