import _pickle
import sys
from collections import Counter

config_path = sys.argv[1]
config_section = sys.argv[2]
import configparser
config = configparser.ConfigParser()
config.readfp(open(config_path))

search_string = sys.argv[3]

# get config parameters

tags_path = config.get(config_section,'tags_path')
aus_path = config.get(config_section,'aus_path')


with open(aus_path,'rb') as f:
	AU_all = _pickle.load(f)

with open(tags_path,'rb') as f:
	tags = _pickle.load(f)

def lower_list(a):
	return [i.lower() for i in a]

AU_words = [i.split() for i in AU_all ]
AU_words = [j for i in AU_words for j in i]
if search_string == 'highFreq':
	count = sys.argv[4]
	AU_all_words_counter = Counter(AU_words)
	print (AU_all_words_counter.most_common(int(count)))

else:
	out = []
	for au in AU_all:
		if search_string in au:
			out.append(au)

	out_counter = Counter(out)
	print ('total occurence:',(len(out)))
	print (out_counter)

