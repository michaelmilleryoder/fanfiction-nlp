# Experimental Scripts
NLP tools for fanfiction, based on David Bamman's BookNLP. Developed by CMU students beginning 2018.

# Running the scripts
* Entity sentiment analyzers using deep SRL: 
  Extracted relationship between entities by using Deep SRL and running Vader NLTK sentiment analyzer to extract positive or negative sentiments from the relation.

* Conversation creation: 
  Create conversations between characters from an entire fic series via quote attribution code

* Extract the surrounding context in conversations and use a classifier to predict the relationship to romantic or not.

# Steps to run Experiment 3

* Run Coref code
* Replace the makejson.py file from quote attribution code with the one provided in the experiments folder
* Run quote attribution code
* Place the remaining files in the quote_attribution folder
* Run the conversation.py file
    * Usage: python coversation.py <Directory_with_pipline_output> <Path_to_metadata_csv> <Output_dir>
    * Output is the Conversation files between two characters per series and mapping file from metadata to coref characters
* Run the create_train_test.py
    * Usage: python coversation.py <Directory_with_pipline_output> <Path_to_metadata_csv> <Output_dir>
    * Output is the Train, dev and test files used in BERT classification format
