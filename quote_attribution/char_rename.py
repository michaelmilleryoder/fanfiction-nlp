# -*- coding: utf-8 -*-
import os
import codecs
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--charfile', help='Path to the character list file', required=True)
    parser.add_argument('--output', help='Path to the output file', required=True)
    opt = parser.parse_args()
    charfile = opt.charfile
    output = opt.output
    with codecs.open(output, 'w') as outf:
        with codecs.open(charfile) as f:
            for _line in f:
                line = _line.strip()
                if len(line) > 0:
                    l = line.split(';')
                    l[0] = l[0][3:-1]
                    outf.write(';'.join(l) + '\n')
