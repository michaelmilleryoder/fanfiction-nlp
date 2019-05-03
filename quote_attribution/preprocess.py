# -*- coding: utf-8 -*-
import os
import csv
import codecs
import argparse

if __name__ == "__main__":
    """Preprocess the input files"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--csvinput', help='Path to the csv story file', required=True)
    parser.add_argument('--charfile', help='Path to the character list file', required=True)
    parser.add_argument('--char_output', help='Path to the output character list file', required=True)
    parser.add_argument('--story_output', help='Path to the output story text file', required=True)
    opt = parser.parse_args()
    csvinput = opt.csvinput
    charfile = opt.charfile
    char_output = opt.char_output
    story_output = opt.story_output
    characters = {}
    with codecs.open(char_output, 'w') as outf:
        with codecs.open(charfile) as f:
            for _line in f:
                line = _line.strip()
                if len(line) > 0:
                    l = line.split(';')
                    characters[l[0]] = l[0][3:-1]
                    l[0] = l[0][3:-1]
                    outf.write(';'.join(l) + '\n')

    with codecs.open(story_output, 'w') as outf:
        with codecs.open(csvinput) as f:
            f_csv = csv.reader(f)
            headers = next(f_csv)
            for line in f_csv:
                text = line[3]
                for c in characters:
                    text = text.replace(c, characters[c])
                outf.write(text+'\n\n')
