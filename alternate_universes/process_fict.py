import os
filenames = []
for filename in os.listdir("stories"):
    if filename.endswith(".csv"): 
    	filenames.append(filename)
        #print(filename)
    else:
        continue

fict_dict={}

filenames.sort()
prev_fictid=''
prev_chapid=''

import csv
for filename in filenames:
	fict_chap = filename.split("_")
	this_fictid = fict_chap[0]
	this_chapid = fict_chap[1][:-4]
	this_text=''
	for row in csv.DictReader(open("stories/"+filename)):
		this_text+=row["text"]
		this_text+="\n"


	if (this_fictid!=prev_fictid):
		prev_fictid=this_fictid
		prev_chapid=this_chapid
	else:
		# this_fictid=prev_fictid,check validation
		if (int(prev_chapid)+1) != int(this_chapid):
			print "wrong here",this_fictid,' ',this_chapid
			continue
		else:
			prev_chapid=this_chapid

	if (this_fictid) not in fict_dict:
		fict_dict[this_fictid] = this_text
	else:
		fict_dict[this_fictid] += this_text

for key, value in fict_dict.iteritems():
	with open('stories_txt/'+key+'.txt','wb') as f:
		f.write(value)
	f.close()
