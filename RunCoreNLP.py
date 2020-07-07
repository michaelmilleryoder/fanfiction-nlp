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


def coref_dir_splits(n_dir_splits, n_threads, data_dir, char_dir, output_dir):
    """ Run coref on split data directory with multiprocessing """

    # Run multiprocessing
    with Pool(n_threads) as p:
        list(tqdm(p.imap(coref_dir, list(zip(
            [os.path.join(data_dir, subdir) for subdir in os.listdir(data_dir)], 
            itertools.repeat(char_dir),
            itertools.repeat(output_dir),
        ))), total=n_dir_splits, ncols=50))

def output_txt2csv(data_dirpath, csv_input_dirpath, csv_output_dirpath, n_dir_splits):
    """ Convert output files from text to original CSV format """

    print("Processing the outputs..")

    if n_dir_splits > 1:
        filenames = []
        for dirname in os.listdir(data_dirpath):
            filenames += [dirname + '/' + fname for fname in os.listdir(os.path.join(data_dirpath, dirname))]
    else:
        filenames = os.listdir(data_dirpath)

    for filename in filenames:
        
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


def input_csv2txt_file(params):
    """ Extracts text from fic CSV file. Just one argument for map multiprocessing
        Args:
            params: (outpath, filename, input_dirpath)
    """

    outpath, filename, input_dirpath = params

    # Check if is already processed
    if os.path.exists(outpath):
        return

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
    with open(outpath,'w') as f:
        f.write(this_text)
        f.close()


def input_csv2txt(input_dirpath, txt_data_dirpath, n_dir_splits=1, n_threads=1, delete_existing=True):
    """ Convert input story CSVs into text files to be stored in a
        temp data dir.

        Args:
            delete_existing: whether to delete current files in the tmp data directory
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
    if delete_existing:
        print(f"Removing any existing files in {txt_data_dirpath}...")
        shutil.rmtree(txt_data_dirpath)
        os.mkdir(txt_data_dirpath)

    # Split data directory
    if n_dir_splits > 1:
        n_to_pad = len(str(n_dir_splits))
        format_str = f'{{:0{n_to_pad}}}'
        name2split = {name: format_str.format(i % n_dir_splits) for i, name in enumerate(filenames)}

    # Create outpaths
    outpaths = []
    for filename in sorted(filenames):
        if n_dir_splits > 1:
            split_dirpath = os.path.join(txt_data_dirpath, str(name2split[filename]))
            if not os.path.exists(split_dirpath):
                os.mkdir(split_dirpath)
            outpath = os.path.join(split_dirpath, filename[:-4])
        else:
            outpath = txt_data_dirpath + "/"+filename[:-4]
        outpaths.append(outpath)

    # Print text files to data_dir
    print("Printing/loading text files...")
    if n_dir_splits > 1:
        
        # Run multiprocessing
        with Pool(n_threads) as p:
            list(tqdm(p.imap(input_csv2txt_file, list(zip(
                outpaths, 
                filenames,
                itertools.repeat(input_dirpath),
            ))), total=len(outpaths), ncols=50))

    else:
        for outpath, filename in tqdm(list(zip(outpaths, filenames))):
            input_csv2txt_file(outpath, filename, input_dirpath)


def main():
    csv.field_size_limit(sys.maxsize)

    test_csv_dir = sys.argv[1]
    char_dir = sys.argv[2]
    output_dir = sys.argv[3]
    dataset_name = sys.argv[4]
    n_threads = int(sys.argv[5])
    split_input_dir = sys.argv[6]
    max_files_per_dir = int(sys.argv[7])
    delete_existing_tmp = sys.argv[8] == 'True'

    # Settings
    #max_files_per_dir = 100
    #n_dir_splits = 0 # How many directory splits to make 
    #n_dir_splits = 100 # How many directory splits to make 
    if split_input_dir:
        n_dir_splits = int(len(os.listdir(test_csv_dir)) / max_files_per_dir) + 1
    else:
        n_dir_splits = 1
    #n_threads = 15 # How many coref runs to run simultaneously

    data_dirpath = os.path.join('tmp', f'{dataset_name}_text_data_split')

    if not os.path.isdir('tmp'):
        os.mkdir('tmp')
    if (not os.path.isdir(data_dirpath)): 
        os.mkdir(data_dirpath)  # input text file directory
    if (not os.path.isdir(char_dir)): 
        os.mkdir(char_dir)   # output directory for characters
    if (not os.path.isdir(output_dir)): 
        os.mkdir(output_dir) # output directory for corefs


    print ("Processing inputs...")
    input_csv2txt(test_csv_dir, data_dirpath, n_dir_splits=n_dir_splits, n_threads=n_threads, delete_existing=delete_existing_tmp) 

    #print("Preparing directory splits...")
    if n_dir_splits > 1:
        coref_dir_splits(n_dir_splits, n_threads, data_dirpath, char_dir, output_dir)

    else:
        #TODO: add in other parameters
        coref_dir((data_dirpath, char_dir, output_dir))

    output_txt2csv(data_dirpath, test_csv_dir, output_dir, n_dir_splits)

if __name__ == '__main__':
    main()
