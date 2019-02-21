import os
from collections import Counter
import pdb

""" 
Script to select a subset of all characters found in fics in a fandom. 
Have to run in the top level of fanfiction-nlp directory.
"""

def clean_character_list(chars):


def main():

    fic_collection = 'example_fandom'
    data_dirpath = os.path.join('output', fic_collection, 'char_coref_chars')

    chars = []

    # Load, clean character lists
    for fname in os.listdir(data_dirpath):
        fpath = os.path.join(data_dirpath, fname)
        with open(fpath, 'r') as f:
            char_list = f.read().splitlines()

        chars.append(clean_character_list(char_list))
        

    # Merge variants within lists of fics (ideally handled by coref)


    # Take most popular characters
    char_counter = Counter()


    # Check character exists in external resource


if __name__ == '__main__': main()
