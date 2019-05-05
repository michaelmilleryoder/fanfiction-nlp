#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-

import os
import multiprocessing
from chapter import Chapter
import feature_extracters


def single_train_organize(inp):
    """Preprocess training data for svm-rank on single process.
    
    Args:
        inp: A tuple as (args, feat_extracters, story_file, char_file, ans_file, 
             tmp_dir), where `args' is the parsed CLI arguments object, 
             `feat_extracters' is a list of feature extracters, `story_file' is 
             the path to the story file, `char_file' is the path to the 
             character list file, `ans_file' is the path to the gold answer file
             and `tmp_dir' is the path to save temporary files.
    
    Returns:
        A tuple as (story_file, svmrank_input_file, success). `success' will be 
        False if processing failed.
    """
    args, feat_extracters, story_file, char_file, ans_file, tmp_dir = inp
    name = multiprocessing.current_process().name
    story_filename = os.path.basename(story_file)
    print("\n### {} processing {} ###".format(name, story_filename))

    # Process file names
    svmrank_input_file = os.path.join(tmp_dir, 'svmrank_input.txt')
    
    try:
        # Read chapter
        chapter = Chapter.read_with_booknlp(story_file, char_file, args.booknlp, 
                                            coref_story=(not args.no_coref_story), 
                                            no_cipher=args.no_cipher_char, 
                                            tmp=tmp_dir)
        # Generate input file for svm-rank
        chapter.prepare_svmrank(feat_extracters, svmrank_input_file, answer=ans_file)
    except Exception as err:
        print(err)
        return (story_file, None, False)
    
    return (story_file, svmrank_input_file, True)


def prepare_train(args):
    """Prepare training data for svm-rank with multi-processing
    
    The function will generate and gather training data by using the story of / 
    all stories under args.story_path with their corresponding character list 
    files with multi-processing, and output gathered data to args.output_path.
    """

    # Check and process data path arguments
    args.tmp = os.path.abspath(args.tmp)
    args.booknlp = os.path.abspath(args.booknlp)
    args.svmrank = os.path.abspath(args.svmrank)
    if os.path.exists(args.output_path) and os.path.isdir(args.output_path):
        raise ValueError("--output-path already exists and is a directory. "
                         "--output-path should be a path to file when "
                         "prepare-train.")
    output_parent_dir = os.path.abspath(os.path.dirname(args.output_path))
    if not os.path.exists(output_parent_dir):
            os.makedirs(output_parent_dir)

    story_files = []
    char_files = []
    ans_files = []
    tmp_dirs = []
    if not hasattr(args, 'ans_path') or args.ans_path is None:
        raise ValueError("--ans-path should be set in training")
    if os.path.isdir(args.story_path):
        print("Read input directories")
        if not os.path.isdir(args.char_path) or not os.path.isdir(args.ans_path):
            raise ValueError("--story-path, --char-path, --ans-path should be "
                             "directories at the same time")
        # Build data paths
        args.story_dir = os.path.abspath(args.story_path)
        args.char_dir = os.path.abspath(args.char_path)
        args.ans_dir = os.path.abspath(args.ans_path)
        for filename in os.listdir(args.story_dir):
            if filename.endswith(args.story_suffix):
                filestem = filename[:-len(args.story_suffix)]
                story_files.append(os.path.join(args.story_dir, filename))
                char_filename = filestem + args.char_suffix
                char_files.append(os.path.join(args.char_dir, char_filename))
                ans_filename = filestem + args.ans_suffix
                ans_files.append(os.path.join(args.ans_dir, ans_filename))
                tmp_dirs.append(os.path.join(args.tmp, filestem))
    elif os.path.isfile(args.story_path):
        print("Read input files")
        if os.path.isdir(args.char_path) or os.path.isdir(args.ans_path):
            raise ValueError("--story-path, --char-path, --ans-path should be "
                             "directories at the same time")
        
        # Build data paths
        story_files.append(os.path.abspath(args.story_path))
        char_files.append(os.path.abspath(args.char_path))
        ans_files.append(os.path.abspath(args.ans_path))
        tmp_dirs.append(os.path.join(args.tmp, os.path.basename(args.story_path)))
    else:
        raise ValueError("Invalid path: {}".format(args.story_path))

    # Build feature extracters
    feat_extracters = feature_extracters.build_feature_extracters(args)

    # Build multi-process inputs
    single_train_inputs = []
    for story_file, char_file, ans_file, tmp_dir in zip(story_files, char_files, ans_files, tmp_dirs):
        single_train_inputs.append((args, feat_extracters, story_file, char_file, ans_file, tmp_dir))
    num_tasks = len(single_train_inputs)
    print("{} files to preocess ... ".format(num_tasks))

    # Check and process multiprocessing arguments
    if not isinstance(args.threads, int) or args.threads <= 0:
        raise ValueError("--threads should be a valid integer")

    # Do multi-processing training data organizing
    success_files = []
    try:
        print("Initializng {} workers".format(args.threads))
        pool = multiprocessing.Pool(processes=args.threads)
        # For the sake of KeyboardInterrupt, we use map_async with timeout
        # TODO: add progress bar
        res = pool.map_async(single_train_organize, single_train_inputs).get(9999999)
        failed = []
        for filename, single_train_file, success in res:
            if success:
                success_files.append(single_train_file)
            if not success:
                failed.append(filename)
        print("{} out of {} input files failed:".format(len(failed), num_tasks))
        for filename in failed:
            print('  Failed: {}'.format(filename))
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
    else:
        print("Normal termination")
        pool.close()
    pool.join()

    with open(args.output_path, 'w') as f_o:
        for svm_input_file in success_files:
            with open(svm_input_file) as f_i:
                f_o.write(f_i.read())

    print("Done.")
