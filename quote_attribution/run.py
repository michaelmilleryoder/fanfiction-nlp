#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-
"""
Predict quote attribution on one or across multiple CPUs.
"""

import os
import argparse
import feature_extracters
from predict import predict
from prepare_train import prepare_train
from feature_extracters import add_extracter_args, EXTRACTER_REGISTRY


def main():
    """The main function of quote attribution.

    Run it in either the 'predict' mode or the 'train' mode. 
    
    In the 'predict' mode, the program will take directories or single files 
    (output by the coreference resolution pipeline) as input, and produce quote 
    attribution json files to the designated path.

    In the 'train' mode, the program will take preprocessed quote annotation
    datasets (also output by coreference resolution pipeline) to train a new
    svm-rank model.
    """

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('predict', 'prepare-train'),
                        help="running mode; if `predict', the program will "
                             "predict quote attributions and output to json "
                             "files; if `prepare-train', the program will "
                             "prepare training data for svm-rank")
    parser.add_argument('--story-path', required=True,
                        help="path to the (coreference resolved) story csv file "
                             "or the directory that contains the story csv files "
                             "to be processed; if this argument is a directory, "
                             "--char-path, --output-path, and --gold-path should "
                             "also be directories")
    parser.add_argument('--char-path', required=True, 
                        help="path to the (coreference resolved) character list "
                             "file or the directory that contains the character "
                             "list files")
    parser.add_argument('--ans-path',
                        help="path to the golden answer quote attribution file "
                             "or the directory that contains the golden answer "
                             "quote attribution files")
    parser.add_argument('--output-path', required=True, 
                        help="(in `predict') path to save the output results; "
                             "(in `prepare-train') path to save gathered "
                             "training data")
    parser.add_argument('--model-path', default='austen.model', 
                        help="path to read pre-trained svm-rank model; this "
                             "model should be corresponding to the features you "
                             "select")
    parser.add_argument('--features', required=True, nargs='*', 
                        choices=list(EXTRACTER_REGISTRY.keys()),
                        help="a list of features to be extracted; the features"
                             "will be extracted in the same order as this "
                             "argument")
    parser.add_argument('--gold-path', 
                        help="path to the gold answer file or the directory "
                             "that contains gold answer files; this option is "
                             "used to generate training data for learning a new "
                             "model")
    parser.add_argument('--tok-path', 
                        help="path to the tokenization file or the directory "
                             "that contains tokenization files (in book-nlp "
                             "format); as there might be mistakes in "
                             "tokenization and probability you want to manually "
                             "fix them, this option is useful when you want to "
                             "designate tokenizations results instead of doing "
                             "tokenization automatically.")
    parser.add_argument('--tmp', default='tmp', 
                        help="path to the directory to store temporary files")
    parser.add_argument('--threads', type=int, default=1, 
                        help="number of threads")
    parser.add_argument('--story-suffix', type=str, default='.coref.csv', 
                        help="(needed when input path is a directory) suffix of "
                             "story csv filenames")
    parser.add_argument('--char-suffix', type=str, default='.chars', 
                        help="(needed when input path is a directory) suffix of "
                             "character list filenames")
    parser.add_argument('--ans-suffix', type=str, default='.ans', 
                        help="(needed when input path is a directory) suffix of "
                             "golden answer quote attribution filenames")
    parser.add_argument('--tok-suffix', type=str, default='.tok', 
                        help="(needed when input path is a directory and "
                             "--tok-path is set) suffix of tokenization "
                             "filenames")
    parser.add_argument('--no-cipher-char', action='store_true', default=False,
                        help="do not cipher character name")
    parser.add_argument('--no-coref-story', action='store_true', default=False,
                        help="story files are not coreference resolved (useful "
                             "when you want to train a new model and use golden "
                             "character list; sometimes coreference resolution "
                             "cannot retrieve all correct characters)")
    parser.add_argument('--booknlp', type=str,
                        help="path to book-nlp")
    parser.add_argument('--svmrank', type=str,
                        help="path to svm-rank")
    add_extracter_args(parser)
    args = parser.parse_args()

    # Make the temporary directory.
    args.tmp = os.path.abspath(args.tmp)
    if not os.path.exists(args.tmp):
        os.makedirs(args.tmp)

    print('Running in {} mode ... '.format(args.mode))

    if args.mode == 'predict':
        predict(args)
    elif args.mode == 'prepare-train':
        prepare_train(args)
        

if __name__ == '__main__':
    main()
