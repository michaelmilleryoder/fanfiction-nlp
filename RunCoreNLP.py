import shutil
import os
import sys
import csv
import stat
import pandas as pd

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
        shutil.move("./CoreNLP/"+filename[:-4]+".coref.out" ,output_dir+"/"+filename[:-4]+".coref.out")


	f = open(output_dir+"/"+filename[:-4]+".coref.out")
	fin = open(test_csv_dir+filename,"rb")
	reader = csv.reader(fin)
	fout = open(test_csv_dir+filename+".coref","wb")
	writer = csv.writer(fout)
	lines = f.readlines()
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
