import pickle
import sys
prefix = sys.argv[1]
cut = int(sys.argv[2])
mapping = prefix+'_mapping_flat.pkl'
q_file = prefix+'_q.txt'
a_file = prefix+'_a.txt'


with open(mapping,'rb') as f:
	mapping = pickle.load(f)
with open(q_file+'.flat') as f:
	q_flat = f.readlines()
with open(a_file+'.flat') as f:
	a_flat = f.readlines()

q_out=''
a_out=''
for i in mapping:
	if mapping[i]>=cut:
		eles = i.split('-')
		q_out=q_out+q_flat[int(eles[0])].strip()+'\n'
		a_out=a_out+a_flat[int(eles[1])].strip()+'\n'

with open(q_file+'.flat.filter','w') as f:
	f.write(q_out)

with open(a_file+'.flat.filter','w') as f:
	f.write(a_out)
