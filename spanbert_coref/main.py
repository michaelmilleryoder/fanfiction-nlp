""" Run SpanBERT coref on a collection of fanfiction 
    @author Michael Miller Yoder, though calling code by Sopan Khosla
    @date 2021
"""

import argparse
import os
import subprocess
from multiprocessing import Pool
import itertools
import pdb

from tqdm import tqdm

import convert_text_to_conll


class SpanbertProcessor:
    """ Run SpanBERT coref on a collection of fics """

    def __init__(self, input_dirpath, coref_output_path,
        threads=1):
        self.input_dirpath = input_dirpath
        self.coref_output_path = coref_output_path
        self.threads = threads
        os.chdir('spanbert_coref')
        self.tmp_dirpath = 'tmp' # eventually delete, for intermediate files
        if not os.path.exists(self.tmp_dirpath):
            os.mkdir(self.tmp_dirpath)
        self.conll_dirpath = os.path.join(self.tmp_dirpath, 'conll')
        if not os.path.exists(self.conll_dirpath):
            os.mkdir(self.conll_dirpath)
        self.json_dirpath = os.path.join(self.tmp_dirpath, 'json')
        if not os.path.exists(self.json_dirpath):
            os.mkdir(self.json_dirpath)
        self.pred_dirpath = os.path.join(self.tmp_dirpath, 'pred')
        if not os.path.exists(self.pred_dirpath):
            os.mkdir(self.pred_dirpath)
        if not os.path.exists(self.coref_output_path):
            os.mkdir(self.coref_output_path)
        #self.out_dirpath = os.path.join(self.tmp_dirpath, 'out')
        #if not os.path.exists(self.out_dirpath):
        #    os.mkdir(self.out_dirpath)

    def run(self):
        """ Run coref on all stories in the input directory """
        # Find files that haven't been processed
        fpaths = []
        for fname in sorted(os.listdir(self.input_dirpath)):
            name = fname.split('.')[0]
            if not os.path.exists(os.path.join(
                self.coref_output_path, f'{name}.json')):
                fpaths.append(os.path.join(self.input_dirpath, fname))
        #fpaths = [os.path.join(self.input_dirpath, fname) for fname in sorted(
            #os.listdir(self.input_dirpath))]
        params = zip(
            fpaths,
            itertools.repeat(self.conll_dirpath),
            itertools.repeat(self.json_dirpath),
            itertools.repeat(self.pred_dirpath),
            itertools.repeat(self.coref_output_path),
            )
        
        if self.threads > 1:
            with Pool(self.threads) as p:
                list(tqdm(p.imap(process_fic, params), total=len(fpaths), ncols=70))
        else:
            # for debugging
            list(tqdm(map(process_fic, params), total=len(fpaths), ncols=70))

def process_fic(params):
    """ Run coref on an individual fic """
    fpath, conll_dirpath, json_dirpath, pred_dirpath, out_dirpath = params
    fname = fpath.split('/')[-1].split('.')[0]
    if os.path.exists(os.path.join(out_dirpath, f'{fname}.json')): # already done
        return
    # TODO: Replace bash calls with direct calls to functions in scripts
    if not convert_text_to_conll.convert(fpath, conll_dirpath):
        return
    #subprocess.run(['python3', 'convert_text_to_conll.py', fpath, 
    #    conll_dirpath], check=True)
    #os.environ['OMP_NUM_THREADS'] = '10' # not sure if this works
    subprocess.run(['python3', 'preprocess.py', '--filename', fname, 
        '--input_dir', conll_dirpath, '--output_dir', json_dirpath,
        '--seg_len', '384'], check=True)
    subprocess.run(['python3', 'predict.py', 
        '--config_name=train_spanbert_base_lit_toshni',
        '--model_identifier=Jan27_03-17-00_4200', '--gpu_id=-1', 
        f'--jsonlines_path={json_dirpath}/{fname}.english.384.jsonlines',
        f'--output_path={pred_dirpath}/{fname}.pred.english.384.jsonlines'],
        check=True)
    #subprocess.run(['python3', 'inference_fanfic.py', 
    #    f'{pred_dirpath}/{fname}.pred.english.384.jsonlines',
    #    out_dirpath], check=True)
    subprocess.run(['python3', 'inference_fanfic.py', 
        f'{pred_dirpath}/{fname}.pred.english.384.jsonlines',
        pred_dirpath], check=True)
    subprocess.run(['python3', 'post_process_wordnet.py', os.path.join(pred_dirpath,
        f'{fname}.json'), out_dirpath], check=True)

    # Remove tmp files
    tmp_paths = []
    tmp_paths.append(os.path.join(conll_dirpath, f'{fname}.conll'))
    tmp_paths.append(os.path.join(json_dirpath, f'{fname}.english.384.jsonlines'))
    tmp_paths.append(os.path.join(pred_dirpath, f'{fname}.pred.english.384.jsonlines'))
    tmp_paths.append(os.path.join(pred_dirpath, f'{fname}.json'))
    for path in tmp_paths:
        os.remove(path)


def get_args():
    """ Get command-line arguments """
    parser = argparse.ArgumentParser(description='Run SpanBERT coreference')
    parser.add_argument('input_dirpath', nargs='?', 
        help='Directory path to input stories.')
    #parser.add_argument('coref_stories_outpath', nargs='?', 
    #    help='Directory path where output stories with coreference tags will be saved.')
    #parser.add_argument('coref_chars_outpath', nargs='?', 
    #    help='Directory path where characters list output will be saved.')
    parser.add_argument('coref_output_path', nargs='?', 
        help='Directory path where coref output will be saved.')
    parser.add_argument('--threads', nargs='?', type=int, default=1, 
        help='Number of threads.')
    return parser.parse_args()


def main():
    """ Main entry point """
    args = get_args()
    processor = SpanbertProcessor(args.input_dirpath, args.coref_output_path, 
        args.threads)
    processor.run()


if __name__ == '__main__':
    main()
