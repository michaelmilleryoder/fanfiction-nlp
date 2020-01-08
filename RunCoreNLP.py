import shutil
import os
import sys
import csv
import io
import stat
import pdb
import time
import datetime
from pathlib import Path
from multiprocessing import Pool
import itertools
from tqdm import tqdm

def coref_dir(params):
    """ Run coref on a dir of files """

    dirname, data_dir, char_dir, output_dir = params

    split_data_dir = os.path.join(data_dir, dirname)

    print ("Running coref..")
    os.chdir("CoreNLP")
    #os.system("./run.sh " + data_dir +  " " + char_dir + " " + output_dir)
    os.system("./run.sh " + split_data_dir +  " " + char_dir + " " + output_dir)
        #os.remove(filename[:-4])
        #os.chdir("..")
        #if (not os.path.isdir(char_dir)):  
        #   os.mkdir(char_dir)
        #if (not os.path.isdir(output_dir)):       
        #   os.mkdir(output_dir)
        #os.rename("./CoreNLP/"+filename[:-4]+".chars" , "./"+char_dir+"/"+filename[:-4]+".chars" )
        #os.rename("./CoreNLP/"+filename[:-4]+".coref.out" , "./"+char_dir+"/"+filename[:-4]+".coref.out" )
        # pdb.set_trace()
        #shutil.move("./CoreNLP/"+filename[:-4]+".chars" , char_dir+"/"+filename[:-4]+".chars")
        #shutil.move("./CoreNLP/"+filename[:-4]+".coref.out" ,output_dir+"/"+filename[:-4]+".coref.txt")

    os.chdir("..")
    print("Processing the outputs..")
    #for filename in filenames:
    for filename in os.listdir(split_data_dir):
        
        fname = output_dir+"/"+filename[:-4]+".coref.txt"
        exists = os.path.isfile(fname)
        if(exists):
            f = open(output_dir+"/"+filename[:-4]+".coref.txt")
            #fin = open(test_csv_dir+filename, encoding='cp1250')
            fin = open(test_csv_dir+filename)
            reader = csv.reader(fin)
            header = next(reader)
            #fout = open(output_dir+"/"+filename[:-4]+".coref.csv","w", encoding='cp1250')
            fout = open(output_dir+"/"+filename[:-4]+".coref.csv","w", encoding='utf8')
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

        else:
            print (fname, " file not found")
            continue

def main():
    csv.field_size_limit(sys.maxsize)

    test_csv_dir = sys.argv[1]
    char_dir = sys.argv[2]
    output_dir = sys.argv[3]

    # Settings
    n_dir_splits = 100 # How many directory splits to make 
    n_threads = 10 # How many Java runs to run simultaneously

    timestamp = datetime.datetime.now().strftime('%m%d-%H%M%S')
    #data_dir = 'data.' + timestamp
    #data_dir = os.path.join(str(Path(test_csv_dir).parent),'fic_text')
    dataset_name = os.path.basename(str(Path(test_csv_dir).parent))
    data_dir = dataset_name + '_fic_text_split'

    filenames = []
    fict_dict={}
    if (not os.path.isdir(data_dir)): 
        os.mkdir(data_dir)  # input text file directory
    if (not os.path.isdir(char_dir)): 
        os.mkdir(char_dir)   # output directory for characters
    if (not os.path.isdir(output_dir)): 
        os.mkdir(output_dir) # output directory for corefs

    for filename in sorted(os.listdir(test_csv_dir)):
        if filename.endswith(".csv"):
            filenames.append(filename)
        else:
            continue
    print (test_csv_dir)
    print (len(filenames))

    """
    print ("Processing inputs...")
    # Print text files to data_dir
    for filename in tqdm(sorted(filenames), ncols=50):

        # Check if is already processed
        if os.path.exists(data_dir + "/"+filename[:-4]):
            continue

        this_text=''
        fic_id = ''
        #chap_id = ''
        #print (test_csv_dir+filename)
        # for row in csv.DictReader(open(test_csv_dir+filename, encoding='cp1250'))

        problem_chars = [
            "\u2028",
            '\u0092',
            '\u0093',
            '\u0094',
        ]

        with open(test_csv_dir+filename) as f:
            data = f.read()
            processed_data = data

            for char in problem_chars:
                processed_data = processed_data.replace(char, ' ')

        #for row in csv.DictReader(open(test_csv_dir+filename)):
        for row in csv.DictReader(io.StringIO(processed_data)):
            if row["chapter_id"] == "chapter_id": # header
                continue
            if len(fic_id)==0:
                fic_id = row["fic_id"]
            else:
                if fic_id != row["fic_id"]: #pdb.set_trace()
                    continue
                assert fic_id == row["fic_id"]

           # if len(chap_id)==0:
           #     chap_id = row["chapter_id"]
           # else:
           #     assert chap_id == row["chapter_id"]

            # this_text+=row["text"]
            
            this_text += ' # . '.join(row["text"].split('\n'))
            
            this_text+=" # . "

        # dump all the txt files in the DataDir folder 
        #print ("DataDir/"+filename[:-4])
        with open(data_dir + "/"+filename[:-4],'w') as f:
            f.write(this_text)
            f.close()
    """

    #print("Preparing directory splits...")
    #if n_dir_splits > 1

    with Pool(n_threads) as p:
        list(tqdm(p.imap(coref_dir, list(zip(
            os.listdir(data_dir), 
            itertools.repeat(data_dir),
            itertools.repeat(char_dir),
            itertools.repeat(output_dir),
        ))), total=90, ncols=50))

if __name__ == '__main__':
    main()
