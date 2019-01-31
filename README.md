# fanfiction-nlp
NLP tools for fanfiction, based on David Bamman's BookNLP. Developed by CMU students beginning 2018.


The search engine (WIP) has all the data under /usr2/scratch/fanfic indexed as of 10/30/2018 . Queries can be formed and run this way-
/path/to/search_engine/indri-5.0/runquery/IndriRunQuery -query="#uw2(Bilbo Baggins)" -count=5 -index=index


# Running the CoreNLP component for coreference clustering:

1. Git clone the repository.

2. Standford jars are present in the location mentioned in CoreNLP/jar-dir.

3. Copy the jars to the CoreNLP directory

4. Come back to the parent directory to run the RunCoreNLP.py file. The command runs the CoreNLP code over all the csv files    present in the folder specified and generate the formatted csv files with coref resolution done in the same folder.

5. Example Command: python RunCoreNLP.py example.fandom/ CharsOutputDir CorefOutputDir
   example.fandom/ : Directory containing all the csv files to be processed.
   CharsOutputDir  : Output Directory for all the characters files.
   CorefOutputDir  : Output Directory for all the coref resolution outputs (txt ) files. 

6. CharOutputDir Directory contains the Character names (InputTextFileName.chars)
7. CorefOutputDir Directory contains the Coref resolution for the files. ("InputTextFileName.coref.out"
8. Example.fandom directory contains all the orginal csv files and the modified csv files after coref resolution.

