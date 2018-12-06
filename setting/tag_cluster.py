import pickle
import sys
from collections import Counter
search_string = sys.argv[1]
with open('AU_all_u.txt') as f:
	AU_all = pickle.load(f)

with open('AU_rm_sw_l_u.txt','r') as f:
	AU_rm_sw_l = pickle.load(f)

with open('tags') as f:
	tags = pickle.load(f)

def lower_list(a):
	return [i.lower() for i in a]

if search_string == 'highFreq':
	count = sys.argv[2]
	AU_all_words_counter = Counter(AU_rm_sw_l)
	print AU_all_words_counter.most_common(int(count))

else:
	out = []
	for au in AU_all:
		if search_string in lower_list(au):
			out.append(au)
	out_join = [' '.join(i) for i in out]
	out_counter = Counter(out_join)
	print 'total occurence:',(len(out_join))
	print out_counter
