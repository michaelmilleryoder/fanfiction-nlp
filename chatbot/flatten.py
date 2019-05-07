import nltk
import sys
from nltk.tokenize import sent_tokenize
file_path = sys.argv[1]
with open(file_path,'rb') as f:
	lines = f.readlines()
out = open(file_path+'.flat','wb')
for line in lines:
	sents = sent_tokenize(line.decode())
	for sent in sents:
		out.write(sent.encode())
		out.write('\n'.encode())
out.close()

