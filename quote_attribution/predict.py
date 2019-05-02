#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-

import os
import multiprocessing
import time
from chapter import Chapter
import feature_extracters

def single_predict(inp):
    args, story_filename = inp
    name = multiprocessing.current_process().name
    filestem = story_filename[:-len(args.story_suffix)]
    print('### {} processing {} ###'.format(name, filestem))

    # process file names
    char_filename = filestem + args.char_suffix
    tmp_dir = os.path.join(args.tmp, filestem)
    story_file = os.path.join(args.story_dir, story_filename)
    char_file = os.path.join(args.char_dir, char_filename)
    svm_rank_input = os.path.join(tmp_dir, 'svmrank_input.txt')
    svm_predict_file = os.path.join(tmp_dir, 'svmrank_predict.txt')

    # parse features
    features = args.features

    # read chapter
    #try:
    #    chapter = Chapter(story_file, char_file, tmp_dir, args.booknlp)
    #except Exception as err:
    #    print(err)
    #    return (filestem, False)
    chapter = Chapter(story_file, char_file, tmp_dir, args.booknlp)
    chapter.extract_features(args, features)
    chapter.output_svmrank_format(svm_rank_input)
    # run svm-rnk
    os.system('sh run-svmrank.sh {} {} {} {}'.format(args.svmrank, 
        svm_rank_input, 'austen.model', svm_predict_file))

    return (filestem, True)


def predict(args):
    """
    Predict quote attribution with multi-processing
    """

    # check and process data path arguments
    if not hasattr(args, 'output_path'):
        raise ValueError('--output-path should be set in predicting')
    if os.path.isdir(args.story_path):
        print('Read input directories')
        if not os.path.isdir(args.char_path):
            raise ValueError('Paths should be directories at the same time')
        # build data paths
        args.story_dir = os.path.abspath(args.story_path)
        args.story_files = os.listdir(args.story_path)
        args.char_dir = os.path.abspath(args.char_path)
        args.char_files = os.listdir(args.char_path)
    elif os.path.isfile(args.story_path):
        print('Read input files')
        if os.path.isdir(args.char_path):
            raise ValueError('Paths should be directories at the same time')
        # TODO
    else:
        raise ValueError('Invalid path: {}'.format(args.story_path))

    # build paths
    args.tmp = os.path.abspath(args.tmp)
    args.booknlp = os.path.abspath(args.booknlp)

    # build multi-process inputs
    single_predict_inputs = []
    for filename in args.story_files:
        if filename.endswith(args.story_suffix):
            single_predict_inputs.append((args, filename))
    num_tasks = len(single_predict_inputs)
    print('{} files to preocess ... '.format(num_tasks))
    
    # check and process multiprocessing arguments
    if not isinstance(args.threads, int) or args.threads <= 0:
        raise ValueError('--threads should be a valid integer')
    try:
        print('Initializng {} workers'.format(args.threads))
        pool = multiprocessing.Pool(processes=args.threads)
        # For the sake of KeyboardInterrupt, we use map_async with timeout
        # TODO: add progress bar
        res = pool.map_async(single_predict, single_predict_inputs).get(9999999)
        failed = []
        for filename, status in res:
            if not status:
                failed.append(filename)
        print('{} out of {} input files failed:'.format(len(failed), num_tasks))
        for filename in failed:
            print('  {}'.format(filename))
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
    else:
        print("Normal termination")
        pool.close()
    pool.join()

