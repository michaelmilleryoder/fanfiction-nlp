import shutil
import os
import sys
import csv
import io
import stat
import pdb
import time
import re
from pathlib import Path
from multiprocessing import Pool
import itertools
from tqdm import tqdm


def coref_dir(params):
    """ Run coref on a dir of files. Only 1 argument (due to use with map), a tuple:
            dirpath: data_dir, directory of text extracted from CSVs
            char_dir: path to character output,
            output_dir: path to character story output
     """

    dirpath, char_dir, output_dir = params

    print ("Running coref..")
    os.chdir("CoreNLP")
    os.system("./run.sh " + dirpath +  " " + char_dir + " " + output_dir)
    os.chdir('..')


def output_txt2csv(data_dirpath, csv_input_dirpath, csv_output_dirpath):

    print("Processing the outputs..")
    for filename in os.listdir(data_dirpath):
        
        fname = csv_output_dirpath+"/"+filename+".coref.txt" # output from the processing
        exists = os.path.isfile(fname)
        if(exists):
            txtfile = open(csv_output_dirpath+"/"+filename+".coref.txt")
            fin = open(os.path.join(csv_input_dirpath, filename + ".csv"))
            reader = csv.reader(fin)
            header = next(reader)
            fout = open(csv_output_dirpath+"/"+filename+".coref.csv","w", encoding='utf8')
            writer = csv.writer(fout)
            #lines = txtfile.readlines()
            lines = re.split(r'\n+| # . ', txtfile.read())
            writer.writerow(header)
        
            for row,text in zip(reader, lines):
                row[len(row)-1]= text
                writer.writerow(row)

            fin.close()
            txtfile.close()
            fout.close()

        else:
            print (fname, " file not found")
            continue


def input_csv2txt(input_dirpath, txt_data_dirpath):
    """ Convert input story CSVs into text files to be stored in a
        temp data dir.
    """

    filenames = []
    for filename in sorted(os.listdir(input_dirpath)):
        if filename.endswith(".csv"):
            filenames.append(filename)
        else:
            continue
    print (input_dirpath)
    print (len(filenames))

    # Delete any existing files in txt_data_dirpath
    for fname in os.listdir(txt_data_dirpath):
        os.remove(os.path.join(txt_data_dirpath, fname))

    # Print text files to data_dir
    for filename in tqdm(sorted(filenames), ncols=50):

        # Check if is already processed
        if os.path.exists(txt_data_dirpath + "/"+filename[:-4]):
            continue

        this_text=''
        fic_id = ''

        problem_chars = [
            "\u2028",
            '\u0092',
            '\u0093',
            '\u0094',
        ]

        with open(os.path.join(input_dirpath, filename)) as f:
            data = f.read()
            processed_data = data

            for char in problem_chars:
                processed_data = processed_data.replace(char, ' ')

        for row in csv.DictReader(io.StringIO(processed_data)):
            if row["chapter_id"] == "chapter_id": # header
                continue
            if len(fic_id)==0:
                fic_id = row["fic_id"]
            else:
                if fic_id != row["fic_id"]:
                    continue
                assert fic_id == row["fic_id"]

            this_text += ' # . '.join(row["text_tokenized"].split('\n'))
            
            this_text+=" # . "

        # dump all the txt files in the DataDir folder 
        with open(txt_data_dirpath + "/"+filename[:-4],'w') as f:
            f.write(this_text)
            f.close()


def main():
    csv.field_size_limit(sys.maxsize)

    test_csv_dir = sys.argv[1]
    char_dir = sys.argv[2]
    output_dir = sys.argv[3]

    # Settings
    n_dir_splits = 0 # How many directory splits to make 
    n_threads = 1 # How many Java runs to run simultaneously

    data_dirpath = 'tmp/text_data_split'

    if not os.path.isdir('tmp'):
        os.mkdir('tmp')
    if (not os.path.isdir(data_dirpath)): 
        os.mkdir(data_dirpath)  # input text file directory
    if (not os.path.isdir(char_dir)): 
        os.mkdir(char_dir)   # output directory for characters
    if (not os.path.isdir(output_dir)): 
        os.mkdir(output_dir) # output directory for corefs


    print ("Processing inputs...")
    input_csv2txt(test_csv_dir, data_dirpath) 

    #print("Preparing directory splits...")
    # TODO: combine split directory names with paths
    if n_dir_splits > 1:
        with Pool(n_threads) as p:
            list(tqdm(p.imap(coref_dir, list(zip(
                os.listdir(data_dir), 
                itertools.repeat(data_dir),
                itertools.repeat(char_dir),
                itertools.repeat(output_dir),
            ))), total=90, ncols=50))

    else:
        coref_dir((data_dirpath, char_dir, output_dir))
        output_txt2csv(data_dirpath, test_csv_dir, output_dir)

if __name__ == '__main__':
    main()
