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
                        help="Running mode. If `predict', the program will "
                             "predict quote attributions and output to json "
                             "files. If `prepare-train', the program will "
                             "prepare training data for svm-rank.")
    parser.add_argument('--story-path', required=True,
                        help="Path to the (coreference resolved) story csv file "
                             "or the directory that contains the story csv files "
                             "to be processed. If this argument is a directory, "
                             "--char-path, --output-path, and --gold-path should "
                             "also be directories")
    parser.add_argument('--char-path', required=True, 
                        help="Path to the (coreference resolved) character list "
                             "file or the directory that contains the character "
                             "list files")
    parser.add_argument('--ans-path',
                        help="Path to the golden answer quote attribution file "
                             "or the directory that contains the golden answer "
                             "quote attribution files")
    parser.add_argument('--output-path', required=True, 
                        help="(In `predict') path to save the output results; "
                             "(in `prepare-train') path to save gathered "
                             "training data")
    parser.add_argument('--model-path', default='austen.model', 
                        help="Path to read pre-trained svm-rank model. This "
                             "model should be corresponding to the features you "
                             "select")
    parser.add_argument('--features', required=True, nargs='*', 
                        choices=list(EXTRACTER_REGISTRY.keys()),
                        help="A list of features to be extracted. The features"
                             "will be extracted in the same order as this "
                             "argument")
    parser.add_argument('--gold-path', 
                        help="Path to the gold answer file or the directory "
                             "that contains gold answer files. This option is "
                             "used to generate training data for learning a new "
                             "model")
    parser.add_argument('--tok-path', 
                        help="Path to the tokenization file or the directory "
                             "that contains tokenization files (in book-nlp "
                             "format). As there might be mistakes in "
                             "tokenization and probability you want to manually "
                             "fix them, this option is useful when you want to "
                             "designate tokenizations results instead of doing "
                             "tokenization automatically.")
    parser.add_argument('--tmp', default='tmp', 
                        help="Path to the directory to store temporary files")
    parser.add_argument('--threads', type=int, default=1, 
                        help="Number of threads")
    parser.add_argument('--story-suffix', type=str, default='.coref.csv', 
                        help="(Needed when input path is a directory) suffix of "
                             "story csv filenames")
    parser.add_argument('--char-suffix', type=str, default='.chars', 
                        help="(Needed when input path is a directory) suffix of "
                             "character list filenames")
    parser.add_argument('--ans-suffix', type=str, default='.ans', 
                        help="(Needed when input path is a directory) suffix of "
                             "golden answer quote attribution filenames")
    parser.add_argument('--tok-suffix', type=str, default='.tok', 
                        help="(Needed when input path is a directory and "
                             "--tok-path is set) suffix of tokenization "
                             "filenames")
    parser.add_argument('--no-cipher-char', action='store_true', default=False,
                        help="Do not cipher character name")
    parser.add_argument('--no-coref-story', action='store_true', default=False,
                        help="Story files are not coreference resolved (useful "
                             "when you want to train a new model and use golden "
                             "character list; sometimes coreference resolution "
                             "cannot retrieve all correct characters)")
    parser.add_argument('--booknlp', type=str, required=True,
                        help="Path to book-nlp")
    parser.add_argument('--svmrank', type=str, required=True,
                        help="Path to svm-rank")
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
