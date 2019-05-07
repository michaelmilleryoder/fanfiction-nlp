import numpy as np
import sys
from nltk.tokenize import sent_tokenize
import pickle
from collections import Counter

#q_file = sys.argv[1]
#a_file = sys.argv[2]
prefix = sys.argv[1]
q_file = prefix+'_q.txt'
a_file = prefix+'_a.txt'

with open(q_file) as f:
	q_lines = f.readlines()
with open(a_file) as f:
	a_lines = f.readlines()
with open(q_file+'.flat') as f:
	q_flat = f.readlines()
with open(a_file+'.flat') as f:
	a_flat = f.readlines()
q_flat = [i.strip() for i in q_flat]
a_flat = [i.strip() for i in a_flat]

#index mapping
q_sent2idx={}
for i in range(len(q_flat)):
	q_sent2idx[q_flat[i]]=i
a_sent2idx={}
for i in range(len(a_flat)):
	a_sent2idx[a_flat[i]]=i
f.close()
mapping = []
stop = False
for i in range(len(q_lines)):
	if stop==True:
		break
	q_sents = sent_tokenize(q_lines[i])
	a_sents = sent_tokenize(a_lines[i])
	for q in q_sents:
		if q.strip() in q_sent2idx:
			q_idx = q_sent2idx[q.strip()]
		else:
			print(q.strip()+' not found!')
			stop=True
			break
		for a in a_sents:
			if a.strip() in a_sent2idx:
				a_idx = a_sent2idx[a.strip()]
			else:
				print(a.strip()+' not foun!')
				stop=True
				break
			pair = str(q_idx)+'-'+str(a_idx)
			mapping.append(pair)
print('map ended')
counter = Counter(mapping)
#print(Counter(el for el in counter.elements() if counter[el] >= 2))
with open(prefix+'_mapping_flat.pkl','wb') as f:
	pickle.dump(counter,f)
with open(prefix+'_q_sent2idx_flat.pkl','wb') as f:
	pickle.dump(q_sent2idx,f)
with open(prefix+'_a_sent2idx_flat.pkl','wb') as f:
	pickle.dump(a_sent2idx,f)

