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
        inp: A tuple as (args, feat_extracters, story_file, char_file, 
             output_file, tok_file, tmp_dir), where `args' is the parsed CLI 
             arguments object, `feat_extracters' is a list of feature extracters, 
             `story_file' is the path to the story file, `char_file' is the path
             to the character list file, `output_file' is the path to save
             results, `tok_file' is the path to tokenization file (could be 
             None or invalid, if so, no external tokenization will be load), and 
             `tmp_dir' is the path to save temporary files.
    
    Returns:
        A tuple as (story_file, success). `success' will be False if 
        processing failed.
    """
    args, feat_extracters, story_file, char_file, output_file, tok_file, tmp_dir = inp
    name = multiprocessing.current_process().name
    story_filename = os.path.basename(story_file)
    print("\n### {} processing {} ###".format(name, story_filename))

    try:
        # Read chapter
        chapter = Chapter.read_with_booknlp(story_file, char_file, args.booknlp, 
                                            tok_file=tok_file,
                                            coref_story=(not args.no_coref_story), 
                                            no_cipher=args.no_cipher_char, 
                                            tmp=tmp_dir)
        # Predict quote attribution
        chapter.quote_attribution_svmrank(feat_extracters, args.model_path, args.svmrank, tmp=tmp_dir)
        # Dump
        chapter.dump_quote_json(output_file)
    except Exception as err:
        print(err)
        return (story_file, False)

    return (story_file, True)


def predict(args):
    """Predict quote attribution with multi-processing.
    
    The function will process the story of / all stories under args.story_path
    with their corresponding character list files, by using book-nlp and 
    svm-rank, and write results into args.output_path.
    """

    # Check and process data path arguments
    args.tmp = os.path.abspath(args.tmp)
    args.booknlp = os.path.abspath(args.booknlp)
    args.svmrank = os.path.abspath(args.svmrank)
    args.model_path = os.path.abspath(args.model_path)
    if not os.path.exists(args.model_path):
        raise ValueError("Invalid model path.")

    story_files = []
    char_files = []
    output_files = []
    tok_files = []
    tmp_dirs = []
    if os.path.isdir(args.story_path):
        print("Read input directories")
        if not os.path.isdir(args.char_path):
            raise ValueError("--story-path and --char-path should be directories "
                             "at the same time")
        if os.path.isfile(args.output_path):
            raise ValueError("--output-path already exists and is a file instead "
                             "of a directory when --story-path is a directory")
        if not os.path.exists(args.output_path):
            os.makedirs(args.output_path)
        # Build data paths
        args.story_dir = os.path.abspath(args.story_path)
        args.char_dir = os.path.abspath(args.char_path)
        args.output_dir = os.path.abspath(args.output_path)
        if not hasattr(args, 'tok_path') or args.tok_path is None:
            args.tok_dir = None
        else:
            args.tok_dir = os.path.abspath(args.tok_path)
        for filename in os.listdir(args.story_dir):
            if filename.endswith(args.story_suffix):
                filestem = filename[:-len(args.story_suffix)]
                story_files.append(os.path.join(args.story_dir, filename))
                char_filename = filestem + args.char_suffix
                char_files.append(os.path.join(args.char_dir, char_filename))
                output_filename = filestem + '.quote.json'
                output_files.append(os.path.join(args.output_dir, output_filename))
                if args.tok_dir is None:
                    tok_files.append(None)
                else:
                    tok_filename = filestem + args.tok_suffix
                    tok_files.append(os.path.join(args.tok_dir, tok_filename))
                tmp_dirs.append(os.path.join(args.tmp, filestem))
    elif os.path.isfile(args.story_path):
        print("Read input files")
        if os.path.isdir(args.char_path):
            raise ValueError("--story-path and --char-path should be directories "
                             "at the same time")
        if os.path.isdir(args.output_path):
            raise ValueError("--output-path already exists and is a directory "
                             "instead of a file when --story-path is a directory")
        output_parent_dir = os.path.abspath(os.path.dirname(args.output_path))
        if not os.path.exists(output_parent_dir):
            os.makedirs(output_parent_dir)
        # Build data paths
        story_files.append(os.path.abspath(args.story_path))
        char_files.append(os.path.abspath(args.char_path))
        output_files.append(os.path.abspath(args.output_path))
        if not hasattr(args, 'tok_path') or args.tok_path is None:
            tok_files.append(None)
        else:
            tok_files.append(os.path.abspath(args.tok_path))
        tmp_dirs.append(os.path.join(args.tmp, os.path.basename(args.story_path)))
    else:
        raise ValueError("Invalid path: {}".format(args.story_path))

    # Build feature extracters
    feat_extracters = feature_extracters.build_feature_extracters(args)

    # Build multi-process inputs
    single_predict_inputs = []
    for story_file, char_file, output_file, tok_file, tmp_dir in zip(story_files, char_files, output_files, tok_files, tmp_dirs):
        single_predict_inputs.append((args, feat_extracters, story_file, char_file, output_file, tok_file, tmp_dir))
    num_tasks = len(single_predict_inputs)
    print("{} files to preocess ... ".format(num_tasks))
    
    # Check and process multiprocessing arguments
    if not isinstance(args.threads, int) or args.threads <= 0:
        raise ValueError("--threads should be a valid integer")

    # Do multi-processing
    try:
        print("Initializng {} workers".format(args.threads))
        pool = multiprocessing.Pool(processes=args.threads)
        # For the sake of KeyboardInterrupt, we use map_async with timeout
        # TODO: add progress bar
        res = pool.map_async(single_predict, single_predict_inputs).get(9999999)
        failed = []
        for story_file, success in res:
            if not success:
                failed.append(story_file)
        print("{} out of {} input files failed:".format(len(failed), num_tasks))
        for story_file in failed:
            print("  Failed: {}".format(story_file))
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
    else:
        print("Normal termination")
        pool.close()
    pool.join()

    print("Done.")
