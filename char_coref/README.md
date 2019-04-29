# Running the CoreNLP component for coreference clustering:

1. Git clone the repository.

2. Standford jars are present in the location mentioned in CoreNLP/jar-dir.

3. Copy the jars to the CoreNLP directory

4. Come back to the parent directory to run the RunCoreNLP.py file. The command runs the CoreNLP code over all the csv files    present in the folder specified and generate the formatted csv and txt files with coref resolution done.

5. Example Command: python RunCoreNLP.py example.fandom/ CharsOutputDir CorefOutputDir

   example.fandom/ : Directory containing all the csv files to be processed.
   
   CharsOutputDir  : Output Directory for all the characters files.
   
   CorefOutputDir  : Output Directory for all the coref resolution outputs (txt and csv ) files. 

6. CharOutputDir Directory contains the Character names (InputTextFileName.chars)

7. CorefOutputDir Directory contains the Coref resolution for the files (txt and csv format). ("InputTextFileName.coref.txt", InputTextFileName.coref.csv")

8. Example.fandom directory contains all the orginal csv files.

To run coref in batches, use:

python3 RunBatches.py <raw_input_dir> <char_output_dir> <coref_output_dir>
Note, <char_output_dir> and <coref_output_dir> must be present inside the CoreNLP directory


# How it works
We use Stanford CoreNLP coreference with a few additional constraints and modifications. 

The coreference works as follows, with modifications noted:

1. Mention extraction

	Extract mentions using CoreNLP mention extraction, only keeping mentions that have been annotated as proper nouns or pronouns. Mentions with 4 or more words are also discarded.

	We add to these mentions named entities labeled as Person or Organization by the CoreNLP NER.

2. Mention clustering

	We cluster mentions using CoreNLP, but additionally track a cluster name and character gender for each cluster. 

	To obtain a cluster name, we first merge any mentions that are substrings of other mentions, keeping the longest mention that is not longer than 4 words. We then select the most frequent mention as the cluster name (can keep pronouns?). 

	Cluster gender can be 'male', 'female', or 'other'. Clusters are labeled 'other' until male or female pronouns are added to the cluster, at which point the most frequent gender of the pronouns gives the cluster gender. We do not allow merging clusters of different genders.

3. Output

	The coreference produces:
	* a list of cluster character names
	* a text and CSV files with the cluster character name added after each mention. For example, "She ($_Wonder_Woman) sat on the bus".

## Notes on the code
* `RunCoreNLP.py` is the main entrance point to the code and runs our modified version of CoreNLP in `CoreNLP/run.sh`.
* Entry point to coref: CoreNLP/src/edu/stanford/nlp/coref/CorefSystem.java
* `CoreNLP/src/edu/stanford/nlp/coref/statistical/StatisticalCorefAlgorithm.java`: 
	Adds NER for character names into mentions to cluster (just take Person or Org)
	Constrain mentions to only Proper nouns
* CoreNLP/src/edu/stanford/nlp/coref/data/CorefCluster.java: 
	When merge cluster, check to make sure gender is not different in the same cluster
	Decides a character name (highest frequency after merge names that are subsets) and character gender for each cluster (majority male or female pronouns, unk if no gendered pronouns are used)
* Checks if character name too long (consider strings of 3 or fewer words for cluster-level character name)
