#! /bin/bash

# This script processes a directory of fanfiction files and extracts
# relevant text to characters.
# 
# 
# Steps include:
#	* Character coreference
#	* Character feature extraction
#		* Quote attribution
#		* Assertion (facts about a character) attribution
#	* Character cooccurrence matrix
#
#
# Input: directory path to directory of fic chapter CSV files
# Output: directory of your choice

# I/O

COLLECTION_NAME="example_fandom"
FICS_INPUT_PATH="${COLLECTION_NAME}/"
# To put your own filepath here, you can do something like
# FICS_INPUT_PATH="/data/fanfiction/${COLLECTION_NAME}"
OUTPUT_PATH="output/${COLLECTION_NAME}/"

# If doing quote attribution
BOOKNLP_PATH="../../book-nlp"
SVMRANK_PATH="../../svmrank"

mkdir -p $OUTPUT_PATH

# Comment out anything below that you will not be running/using
COREF_STORIES_PATH="${OUTPUT_PATH}char_coref_stories"
mkdir -p $COREF_STORIES_PATH
COREF_CHARS_PATH="${OUTPUT_PATH}char_coref_chars"
mkdir -p $COREF_CHARS_PATH

QUOTE_OUTPUT_PATH="${OUTPUT_PATH}quote_attribution"
mkdir -p $QUOTE_OUTPUT_PATH

ASSERTION_OUTPUT_PATH="${OUTPUT_PATH}assertion_extraction"
mkdir -p $ASSERTION_OUTPUT_PATH

COOCCURRENCE_OUTPUT_PATH="${OUTPUT_PATH}cooccurrence"
mkdir -p $COOCCURRENCE_OUTPUT_PATH


# Character coref
echo "Running character coreference..."
python3 RunCoreNLP.py "$FICS_INPUT_PATH" "$COREF_CHARS_PATH" "$COREF_STORIES_PATH"
echo ""


# Quote attribution
echo "Running quote attribution..."
cd quote_attribution
python3 run.py predict --story-path "$COREF_STORIES_PATH" --char-path "$COREF_CHARS_PATH" --output-path "$QUOTE_OUTPUT_PATH" --features spkappcnt nameinuttr neighboring disttoutter spkcntpar --booknlp "$BOOKNLP_PATH" --svmrank "$SVMRANK_PATH"
cd ..
echo ""


### Assertion attribution
echo "Running assertion extraction..."
python3 assertion_extraction/extract_assertions.py "$COREF_STORIES_PATH" "$COREF_CHARS_PATH" "$ASSERTION_OUTPUT_PATH"
echo ""


### Person entity cooccurrence matrix
echo "Running entity coocurrence..."
cd cooccurrence
python3 co_occurance_generation.py "$COREF_STORIES_PATH" "$COOCCURRENCE_OUTPUT_PATH" "$COREF_CHARS_PATH/"
cd ..
echo ""
