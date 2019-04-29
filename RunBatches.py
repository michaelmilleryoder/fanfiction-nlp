import shutil
import os
import sys
import csv
import stat
import pdb

test_csv_dir = sys.argv[1]
char_dir = sys.argv[2]
output_dir = sys.argv[3]

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

filenames = []
#Get list of all files
for filename in os.listdir(test_csv_dir):
	if filename.endswith(".csv"):
		filenames.append(filename)
	else:
		continue

it = 0
chunk_size = 50
chunks = 0

dir_name = ""
print ("Splitting into chunks of size: ", chunk_size)

#Split into chunks of 50 files
for f in filenames:
    if 0 == it % chunk_size:
        chunks += 1
        dir_name = test_csv_dir + "chunk" + str(chunks)
        if (not os.path.isdir(dir_name)):
            os.mkdir(dir_name)
    it += 1
    shutil.move(test_csv_dir + "/" + f,dir_name) 

file_chunks = get_immediate_subdirectories(test_csv_dir)
chunks = len(file_chunks)
print ("Split into ", chunks," chunks")
print_every = chunks//10
print (file_chunks)
#Call RunCoreNLP for every chunk
for i, dir_name in enumerate(file_chunks):
    if os.path.isdir("DataDir"):
        shutil.rmtree("DataDir")
    run_cmd = "python3.5 RunCoreNLP.py " + test_csv_dir + dir_name + "/ " + char_dir + " " + output_dir
    print (run_cmd)
    if 0 == i% print_every-1:
        print ("Running CoreNLP on ", str(i), "th chunk")
    os.system(run_cmd)  
