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

COLLECTION_NAME="emnlp_dataset_6k"
FICS_INPUT_PATH="/usr0/home/mamille2/erebor/fanfiction-project/data/ao3/harrypotter/${COLLECTION_NAME}/fics/" # will eventually come from command line
OUTPUT_PATH="/usr0/home/mamille2/erebor/fanfiction-project/data/ao3/harrypotter/${COLLECTION_NAME}/output/"
#COLLECTION_NAME=$1 # command-line argument
#FICS_INPUT_PATH="/usr0/home/mamille2/erebor/fanfiction-project/data/ao3/harrypotter/emnlp_dataset_6k_splits/${COLLECTION_NAME}/fics/" # will eventually come from command line
#OUTPUT_PATH="/usr0/home/mamille2/erebor/fanfiction-project/data/ao3/harrypotter/emnlp_dataset_6k_splits/${COLLECTION_NAME}/output/"
mkdir -p $OUTPUT_PATH

COREF_STORIES_PATH="${OUTPUT_PATH}char_coref_stories"
mkdir -p $COREF_STORIES_PATH
COREF_CHARS_PATH="${OUTPUT_PATH}char_coref_chars"
mkdir -p $COREF_CHARS_PATH

QUOTE_OUTPUT_PATH="${OUTPUT_PATH}quote_attribution"
mkdir -p $QUOTE_OUTPUT_PATH

#ASSERTION_OUTPUT_PATH="${OUTPUT_PATH}assertion_extraction"
#mkdir -p $ASSERTION_OUTPUT_PATH

#COOCCURRENCE_OUTPUT_PATH="${OUTPUT_PATH}cooccurrence"
#mkdir -p $COOCCURRENCE_OUTPUT_PATH

#AU_OUTPUT_PATH="${OUTPUT_PATH}aus/"
#mkdir -p $AU_OUTPUT_PATH


# Character coref
#echo "Running character coreference..."
#/usr/bin/python3 RunCoreNLP.py "$FICS_INPUT_PATH" "$COREF_CHARS_PATH" "$COREF_STORIES_PATH"   # takes about 10G RAM
#echo ""


# Quote attribution
echo "Running quote attribution..."
cd quote_attribution
python3 run.py predict --story-path "$COREF_STORIES_PATH" --char-path "$COREF_CHARS_PATH" --output-path "$QUOTE_OUTPUT_PATH" --threads 15 --features spkappcnt nameinuttr neighboring disttoutter spkcntpar --booknlp /usr0/home/huimingj/book-nlp-master/
#cd ..
#echo ""
 
 
### Assertion attribution
#echo "Running assertion extraction..."
#python3 assertion_extraction/extract_assertions.py "$COREF_STORIES_PATH" "$COREF_CHARS_PATH" "$ASSERTION_OUTPUT_PATH"
#echo ""
 
 
### Person entity cooccurrence matrix
#echo "Running entity coocurrence..."
#cd props
#python3 co_occurance_generation.py "$COREF_STORIES_PATH" "$COOCCURRENCE_OUTPUT_PATH" "$COREF_CHARS_PATH/"
#cd ..
#echo ""


## AUs 
#echo "Running AU prediction..."
#TRAINED_MODEL_CONFIG=friends.ini
#FICS_TEXT_PATH="${FICS_INPUT_PATH::-1}_txt/" # text from CSV
#mkdir -p $FICS_TEXT_PATH
#python csv2txt.py $FICS_INPUT_PATH $FICS_TEXT_PATH # convert fic to txt
#cd setting
#python config.py $TRAINED_MODEL_CONFIG DEFAULT "$FICS_INPUT_PATH" "$FICS_TEXT_PATH" "$AU_OUTPUT_PATH" # modifies config file
#python BM25.py $TRAINED_MODEL_CONFIG DEFAULT 
#python nb.py $TRAINED_MODEL_CONFIG DEFAULT 
