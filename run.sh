#! /bin/bash

# This script processes a directory of fanfiction files and extracts
# relevant text to characters, as well as fic AU metadata.
# 
# 
# Steps include:
#	* Character coreference
#	* Character feature extraction
#		* Quote attribution
#		* Assertion (facts about a character) attribution
#	* Character cooccurrence matrix
#	* Alternate universe (AU) extraction from fic metadata
#
#
# Input: directory path to directory of fic chapter CSV files
# Output:


# I/O
FICS_INPUT_PATH="example_fandom/" # will eventually interally come from command line
OUTPUT_PATH="output/example_fandom/"
mkdir -p $OUTPUT_PATH

COREF_STORIES_PATH="${OUTPUT_PATH}char_coref_stories"
mkdir -p $COREF_STORIES_PATH
COREF_CHARS_PATH="${OUTPUT_PATH}char_coref_chars"
mkdir -p $COREF_CHARS_PATH

QUOTE_OUTPUT_PATH="${OUTPUT_PATH}quote_attribution"
mkdir -p $QUOTE_OUTPUT_PATH

ASSERTION_OUTPUT_PATH="${OUTPUT_PATH}assertion_extraction"
mkdir -p $ASSERTION_OUTPUT_PATH

# Character coref
echo "Running character coreference..."
python2 RunCoreNLP.py "$FICS_INPUT_PATH" "$COREF_CHARS_PATH" "$COREF_STORIES_PATH"   # takes about 10G RAM
mv ${FICS_INPUT_PATH}*.coref $COREF_STORIES_PATH # can take out line when output handled differently


# Quote attribution
#echo "Running quote attribution..."
#cd quote_attribution
#bash run.sh "../$COREF_STORIES_PATH" "../$COREF_CHARS_PATH" "../$QUOTE_OUTPUT_PATH"


# Assertion attribution
echo "Running assertion extraction..."
python2 assertion_extraction/extract_assertions.py "$COREF_STORIES_PATH" "$COREF_CHARS_PATH" "$ASSERTION_OUTPUT_PATH"


# Character cooccurrence matrix


# AU 
# goes to JSON file at level of fic
