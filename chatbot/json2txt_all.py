# usage: python json2txt.py [json_dir] [txt_dir] [max_len], output filename would be a merge of all quotes 
import os
import sys
import json
import re

#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
# config_path = sys.argv[1]
# config_section = sys.argv[2]
# import ConfigParser
# config = ConfigParser.ConfigParser()
# config.readfp(open(config_path))

# test_csv_dir = config.get(config_section,'test_csv_dir')
# test_txt_dir = config.get(config_section,'test_txt_dir')
test_json_dir = sys.argv[1]
test_txt_dir = sys.argv[2]
# speaker = sys.argv[3]
max_len = int(sys.argv[3])
speaker = 'all'

filenames = []

char_dict={}

char_dict['Hank_Anderson'] = 'Hank'
char_dict['Gavin_Reed'] = 'Gavin'
char_dict['Connor_LED'] = 'Connor'
char_dict['Connors'] = 'Connor'
char_dict['The_Connor'] = 'Connor'
char_dict['Kara_Wonderland'] = 'Kara'
char_dict['Hanks'] = 'Hank'
char_dict['The_Hank'] = 'Hank'
char_dict['Captain_Fowler'] = 'Fowler'



for filename in os.listdir(test_json_dir):
	if filename.endswith(".quote.json"): 
		filenames.append(filename)
	else:
		continue

qtext = ''
atext = ''
aspeaker = ''
qspeaker = ''
q_para = ''
a_para = ''

for filename in filenames:
	with open(test_json_dir+filename) as f:
		data = json.load(f)
		para_dict = {}
		para_text = {}
	for i in data:
		para_dict[i['paragraph']]=i
		# this_speaker = i['speaker']
		# if speaker in i['speaker']:
		# 	print i['speaker']
			# process answer quote
			# if i['type']=='Explicit':
		this_text = []
		for q in i['quotes']:
			line = re.sub('``','',q['quote'])
			line = line.replace("''",'')
			line = line.encode("ascii", "ignore")

			# 	print filename
			# 	print i
			# 	break
			this_text.append(line)

		# store it into the dict
		para_text[i['paragraph']] = this_text

		# identify whether it is question or answer
		# if i['speaker'] == speaker or (i['speaker'] in char_dict and char_dict[i['speaker']] == speaker):
			# this_text = [j for j in this_text if speaker.lower() not in j.lower()]
		this_text = ''.join(this_text)

		# search for its question
		if i['replyto']==-1:
			continue
		if i['type']=='Implicit':
			continue
			# retrieve its question text
		a_speaker = i['speaker']
		q_speaker = para_dict[i['replyto']]['speaker']
		a_para = a_para+ filename+' '+str(i)+'\n'
		q_para = q_para+ filename+' '+str(para_dict[i['replyto']])+'\n'		
# if q_speaker == speaker or (q_speaker in char_dict and char_dict[q_speaker] == speaker):
			# if para_dict[i['replyto']]['type']=='Explicit':
			# 	continue
		this_q = para_text[i['replyto']]
		this_q = ''.join(this_q)
			# append it to the stream

		atext = atext+this_text
		atext = atext + '\n'

		qtext = qtext+this_q
		qtext = qtext+'\n'

		aspeaker = aspeaker + a_speaker
		aspeaker = aspeaker + '\n'

		qspeaker = qspeaker + q_speaker
		qspeaker = qspeaker + '\n'



	# dump the txt file
with open(test_txt_dir+speaker+'_a.txt','wb') as f:
	f.write(atext)
f.close()
with open(test_txt_dir+speaker+'_q.txt','wb') as f:
	f.write(qtext)
f.close()

with open(test_txt_dir+speaker+'_a_speaker.txt','w') as f:
	f.write(aspeaker)
f.close()

with open(test_txt_dir+speaker+'_q_speaker.txt','w') as f:
	f.write(qspeaker)
f.close()

with open(test_txt_dir+speaker+'_a_paragraph.txt','w') as f:
	f.write(a_para)
f.close()

with open(test_txt_dir+speaker+'_q_paragraph.txt','w') as f:
	f.write(q_para)
f.close()
