import os
from collections import Counter, defaultdict
import pdb

""" 
Script to select a subset of all characters found in fics in a fandom. 
Have to run in the top level of fanfiction-nlp directory.
"""

def clean_character_list(chars):

    new_chars = []

    for char in chars:

        # Don't consider if have a comma
        if ',' in char or len(char) < 5:
            continue

        char_words = char[3:-1].split('_')

        # Remove words with lowercase
        new_char = f"($_{'_'.join([w for w in char_words if w[0].isupper()])})"

        # Remove stopwords
        stopwords = ['The']
        new_char = f"($_{'_'.join([w for w in char_words if not w in stopwords])})"

        if len(new_char) > 5:
            new_chars.append(new_char)

    return sorted(set(new_chars))


def merge_chars(char_counter):
    names = defaultdict(set) # by length
    normalized_names = defaultdict(set) # name_variant: normalized_name

    # Filter out characters without a minimum number of mentions
    min_mentions = 1
    merged_char_counter = Counter(dict([el for el in char_counter.items() if el[1] > min_mentions])) # character counter with normalized names

    for char in merged_char_counter:

        char_words = char[3:-1].split('_')
        names[len(char_words)].add('_'.join(char_words))

    # Try to resolve single names
    for full_name in names[2]:
        first, last = full_name.split('_')

        # If matches a first name
        if first in names[1]:
            normalized_names[first].add(full_name)

        # If matches a last name
        if last in names[1]:
            normalized_names[last].add(full_name)

    # If full names with middle names are common enough, resolve here

    # Create normalized list of names
    for length in names:
        for name in names[length]:
            norm_name = name
            if name == 'Midoriya': pdb.set_trace()

            if name in normalized_names:
                name_options = [name for name in list(normalized_names[name]) if f"($_{name})" in merged_char_counter] # remove if already was replaced

                if len(name_options) == 1:  # 1 normalization option
                    norm_name = name_options[0]
                    merged_char_counter[f"($_{norm_name})"] += merged_char_counter[f'($_{name})']
                    del merged_char_counter[f"($_{name})"]

                elif len(name_options) == 2:
                    
                    # Surname first case (as in Japanese)
                    name_options = sorted(name_options, key=lambda x: merged_char_counter[f"($_{x})"], reverse=True) # sort descending by frequency
                    if name_options[0].split('_')[0] == name_options[1].split('_')[1]:
                        norm_name = name_options[0]
                        other_name = name_options[1]
                        if not f"($_{norm_name})" in merged_char_counter or not f"($_{other_name})" in merged_char_counter: pdb.set_trace()
                        merged_char_counter[f"($_{norm_name})"] += merged_char_counter[f'($_{name})']
                        merged_char_counter[f"($_{norm_name})"] += merged_char_counter[f'($_{other_name})']
                        del merged_char_counter[f"($_{name})"]
                        del merged_char_counter[f"($_{other_name})"]

    return merged_char_counter
            

def main():

    # I/O
    fic_collection = 'example_academia_100'
    base_dirpath = '/usr0/home/mamille2/fanfiction-project/data/'
    char_dirpath = os.path.join(base_dirpath, fic_collection, 'output', 'char_coref_chars')

    chars = []

    # Load, clean character lists
    for fname in os.listdir(char_dirpath):
        fpath = os.path.join(char_dirpath, fname)
        with open(fpath, 'r') as f:
            char_list = f.read().splitlines()
    
        chars.extend(clean_character_list(char_list))
        

    # Merge variants within lists of fics
    char_counter = Counter(chars)
    char_counter = merge_chars(char_counter)

    # Take most popular characters
    top_chars = char_counter.most_common(int(len(char_counter)/10))
    for char,count in top_chars:
        print(f"{char}: {count}")

    # Check character exists in external resource


if __name__ == '__main__': main()
