#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-

import os
import multiprocessing
import time
from chapter import Chapter
import feature_extracters

def single_predict(inp):
    """Do quote attribution prediction on single process
    
    Args:
        inp: A tuple as (args, feat_extracters, story_filename), where `args' is 
             the parsed CLI arguments object, `feat_extracters' is a list of 
             feature extracters, and `story_filename' is the base file name of 
             the coreference resolved story file.
    
    Returns:
        A tuple as (story_filename, success). If `success' is False, it means
        that the processing failed.
    """
    args, feat_extracters, story_filename = inp
    name = multiprocessing.current_process().name
    filestem = story_filename[:-len(args.story_suffix)]
    print('### {} processing {} ###'.format(name, filestem))

    # process file names
    tmp_dir = os.path.join(args.tmp, filestem)
    story_file = os.path.join(args.story_dir, story_filename)
    char_filename = filestem + args.char_suffix
    char_file = os.path.join(args.char_dir, char_filename)
 
    
    json_filename = filestem + '.quote.json'
    json_output_path = os.path.join(args.output_path, json_filename)

    # read chapter
    #try:
    #    chapter = Chapter(story_file, char_file, tmp_dir, args.booknlp)
    #except Exception as err:
    #    print(err)
    #    return (filestem, False)
    chapter = Chapter.read_with_booknlp(story_file, char_file, args.booknlp, tmp=tmp_dir)

    chapter.extract_features(args, features) 
    chapter.output_svmrank_format(svm_rank_input)
    # run svm-rnk
    os.system('sh run-svmrank.sh {} {} {} {}'.format(args.svmrank, 
        svm_rank_input, model_file, svm_predict_file))
    chapter.read_svmrank_pred(svm_predict_file)
    chapter.dump_quote_json(json_output_path)

    return (story_filename, True)


def predict(args):
    """Predict quote attribution with multi-processing.
    
    The function will process the story of / all stories under args.story_path
    with their corresponding character list files, by using book-nlp and 
    svm-rank, and write results into args.output_path.
    """

    # check and process data path arguments
    if not hasattr(args, 'output_path') or args.output_path is None:
        raise ValueError("--output-path should be set in predicting")
    if os.path.isdir(args.story_path):
        print("Read input directories")
        if not os.path.isdir(args.char_path):
            raise ValueError("--story-path and --char-path should be directories "
                             "at the same time")
        # build data paths
        args.story_dir = os.path.abspath(args.story_path)
        args.story_files = os.listdir(args.story_path)
        args.char_dir = os.path.abspath(args.char_path)
    elif os.path.isfile(args.story_path):
        print("Read input files")
        if os.path.isdir(args.char_path):
            raise ValueError("Paths should be directories at the same time")
        args.story_dir = os.path.abspath(os.path.dirname(args.story_path))
        args.story_files = [os.path.basename(args.story_path)]
        args.char_dir = os.path.abspath(os.path.dirname(args.char_path))
    else:
        raise ValueError("Invalid path: {}".format(args.story_path))

    # build paths
    args.output_path = os.path.abspath(args.output_path)
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)
    args.tmp = os.path.abspath(args.tmp)
    args.booknlp = os.path.abspath(args.booknlp)
    args.svmrank = os.path.abspath(args.svmrank)
    args.model_path = os.path.abspath(args.model_path)

    # build feature extracters
    feat_extracters = feature_extracters.build_feature_extracters(args)

    # build multi-process inputs
    single_predict_inputs = []
    for filename in args.story_files:
        if filename.endswith(args.story_suffix):
            single_predict_inputs.append((args, feat_extracters, filename))
    num_tasks = len(single_predict_inputs)
    print("{} files to preocess ... ".format(num_tasks))
    
    # check and process multiprocessing arguments
    if not isinstance(args.threads, int) or args.threads <= 0:
        raise ValueError("--threads should be a valid integer")
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
        print("{} out of {} input files failed:".format(len(failed), num_tasks))
        for filename in failed:
            print('  {}'.format(filename))
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
    else:
        print("Normal termination")
        pool.close()
    pool.join()
