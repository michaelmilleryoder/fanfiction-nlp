import skipthoughts.skipthoughts as skipthoughts
model = skipthoughts.load_model()
encoder = skipthoughts.Encoder(model)
import skipthoughts.eval_sick2 as eval_sick2
from keras.models import load_model
import gensim
import os
import collections
import smart_open
import random
import time
import numpy as np

import sys

# limit gpu usage
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.3
set_session(tf.Session(config=config))

prefix = sys.argv[1]

q_file = prefix+'_q.txt'
a_file = prefix+'_a.txt'
q_speaker = prefix+'_q_speaker.txt'
a_speaker = prefix+'_a_speaker.txt'
speaker = sys.argv[2]
top = int(sys.argv[3])
q_para_file = prefix+'_q_paragraph.txt'
a_para_file = prefix+'_a_paragraph.txt'

with open(q_file,'r') as f:
	q_file_lines = f.readlines()
f.close()
with open(a_file,'r') as f:
	a_file_lines = f.readlines()
f.close()

with open(a_speaker,'r') as f:
	a_speaker_lines = f.readlines()
f.close()

with open(q_para_file,'rb') as f:
	q_para_lines = f.readlines()
f.close()

with open(a_para_file,'rb') as f:
	a_para_lines = f.readlines()
f.close()
#preload the model for skipthoughts and doc2vec
bestlrmodel = load_model('skipthoughts/skipthought-best')
model = gensim.models.doc2vec.Doc2Vec.load(q_file+'.doc2vec.model')

while True:
	query = input('User:')
	start = time.time()

	# embed the query
	inferred_vector=model.infer_vector(query.split())
#	print 'inferred_vector',inferred_vector
	sims = model.docvecs.most_similar([inferred_vector], topn=top)
#	print sims
	# retrieved = sent2vec_vec.most_similar(positive=query_vec.sents, topn=20)
	print('finished retrieving '+str(top)+' sentences similar to query')
	max_sick_score = 0
	max_sick_sent = "EOF"

	max_sick_score_speaker = 0
	max_sick_sent_speaker = ''

	qs = []
	nos = []
	for pair in sims:
		# print pair[0]
		# break
		#calculate semantic relatedness score
		no = int(pair[0])
		qs.append(q_file_lines[no])
		nos.append(no)
		# sick_scores = eval_sick2.sick_score(encoder,bestlrmodel,q_file_lines[no],query)
		# print 'sick_scores:',sick_scores
		# print 'q_sent:',q_file_lines[no]
		# if(sick_scores>max_sick_score):
		# 	max_sick_score = sick_scores
		# 	max_sick_sent = no

		# if speaker.lower() in a_speaker_lines[no].lower():
		# 	if (sick_scores>max_sick_score_speaker):
		# 		max_sick_score_speaker = sick_scores
		# 		max_sick_sent_speaker = no
		# print 'a_sent:',a_file_lines[no]
#	print 'knn:',qs
	sick_scores = eval_sick2.sick_score(encoder,bestlrmodel,qs,[query]*len(qs))
#	print 'sick_scores:',sick_scores
	# max_sick_score = max(sick_scores)
	# max_idx = sick_scores.index(max_sick_score)
#	for i in range(len(qs)):
#		print(qs[i],sick_scores[i])
	sort_idx = np.argsort(-sick_scores)
	max_idx = sort_idx[0]
	max_sick_sent = nos[max_idx]
	print('matched q:',q_file_lines[max_sick_sent])
#	print('para:',q_para_lines[max_sick_sent])
	print('best reply:',a_file_lines[max_sick_sent])
	print('speaker:',a_speaker_lines[max_sick_sent])
#	print('para:',a_para_lines[max_sick_sent])
	# iterate the list to check the speaker
	for i in sort_idx:
		if speaker.lower() in a_speaker_lines[nos[i]].lower():
			max_sick_sent_speaker = nos[i]
			break

	if max_sick_sent!=max_sick_sent_speaker:
		if max_sick_sent_speaker=='':
			print('no reply retrieved for speaker',speaker)
		else:
			print('matched q by '+speaker+':'+q_file_lines[m0ax_sick_sent_speaker])
#			print('para:'+q_para_lines[max_sick_sent_speaker])
			print('best reply by '+speaker+':'+a_file_lines[max_sick_sent_speaker])
			print('speaker:'+a_speaker_lines[max_sick_sent_speaker])
#			print('para:'+a_para_lines[max_sick_sent_speaker])
	# print 'max_sick_score:',max_sick_score
	print('elapsed time:',time.time()-start)


