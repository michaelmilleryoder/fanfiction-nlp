import shutil
import os
import sys
import csv
import stat
import pdb

test_csv_dir = sys.argv[1]
char_dir = sys.argv[2]
output_dir = sys.argv[3]

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
	#for row in csv.DictReader(open(test_csv_dir+filename, encoding='cp1250')):
	for row in csv.DictReader(open(test_csv_dir+filename)):
		if row["chapter_id"] == "chapter_id": # header
			continue
		if len(fic_id)==0:
			fic_id = row["fic_id"]
		else:
			if fic_id != row["fic_id"]:
				pdb.set_trace()
			assert fic_id == row["fic_id"]

		if len(chap_id)==0:
			chap_id = row["chapter_id"]
		else:
			assert chap_id == row["chapter_id"]

		this_text+=row["text"]
		this_text+=" # . "

	# dump the txt file
	print ("CoreNLP/"+filename[:-4])
	with open("CoreNLP/"+filename[:-4],'w') as f:
		f.write(this_text)
	f.close()
	os.chdir("CoreNLP")
	os.system("./run.sh "+filename[:-4])
	os.remove(filename[:-4])
	os.chdir("..")
	if (not os.path.isdir(char_dir)):	
		os.mkdir(char_dir)
	if (not os.path.isdir(output_dir)):       
 		os.mkdir(output_dir)
	#os.rename("./CoreNLP/"+filename[:-4]+".chars" , "./"+char_dir+"/"+filename[:-4]+".chars" )
	#os.rename("./CoreNLP/"+filename[:-4]+".coref.out" , "./"+char_dir+"/"+filename[:-4]+".coref.out" )
	shutil.move("./CoreNLP/"+filename[:-4]+".chars" , char_dir+"/"+filename[:-4]+".chars")
	shutil.move("./CoreNLP/"+filename[:-4]+".coref.out" ,output_dir+"/"+filename[:-4]+".coref.txt")


	f = open(output_dir+"/"+filename[:-4]+".coref.txt")
	#fin = open(test_csv_dir+filename, encoding='cp1250')
	fin = open(test_csv_dir+filename)
	reader = csv.reader(fin)
	header = next(reader)
	fout = open(output_dir+"/"+filename[:-4]+".coref.csv","w", encoding='cp1250')
	#fout = open(output_dir+"/"+filename[:-4]+".coref.csv","w", encoding='utf8')
	writer = csv.writer(fout)
	lines = f.readlines()
	writer.writerow(header)
	
	for row,text in zip(reader, lines):
		#row["paragraph"] = text
		#print (row["paragraph"])
		#print (text)
		row[len(row)-1]= text
		writer.writerow(row)
		#print (row['paragraph'])

	fin.close()
	f.close()
	fout.close()
