# usage: python csv2txt.py [csv_dir] [txt_dir], output filename would be ficid-chapterid.txt
import os
import sys
import csv


# config_path = sys.argv[1]
# config_section = sys.argv[2]
# import ConfigParser
# config = ConfigParser.ConfigParser()
# config.readfp(open(config_path))

# test_csv_dir = config.get(config_section,'test_csv_dir')
# test_txt_dir = config.get(config_section,'test_txt_dir')
test_csv_dir = sys.argv[1]
test_txt_dir = sys.argv[2]

filenames = []
fict_dict={}

for filename in os.listdir(test_csv_dir):
	if filename.endswith(".csv"): 
		filenames.append(filename)
	else:
		continue

for filename in filenames:

	this_text=''
	fic_id = ''
	chap_id = ''
	for row in csv.DictReader(open(test_csv_dir+filename)):
		if len(fic_id)==0:
			fic_id = row["fic_id"]
		else:
			assert fic_id == row["fic_id"]

		if len(chap_id)==0:
			chap_id = row["chapter_id"]
		else:
			assert chap_id == row["chapter_id"]

		this_text+=row["paragraph"]
		this_text+="\n"

	# dump the txt file
	with open(test_txt_dir+fic_id+'-'+chap_id+'.txt','wb') as f:
		f.write(this_text)
	f.close()


