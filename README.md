# fanfiction-nlp
NLP tools for fanfiction, based on David Bamman's [BookNLP](https://github.com/dbamman/book-nlp). Contact Michael Miller Yoder <yoder [at] cs.cmu.edu> with questions.

# Running the pipeline
This pipeline processes a directory of fanfiction files and extracts
 text that is relevant for each character.
 
The pipeline does:
* [Character coreference](char_coref)
* Character feature extraction
	* [Quote attribution](quote_attribution)
	* [Assertion attribution](assertion_extraction) (narrative and evaluation about a character)
* [Character cooccurrence matrix](cooccurrence)

## Requirements
* Parts of the pipeline require [this Stanford CoreNLP models jar](http://nlp.stanford.edu/software/stanford-corenlp-models-current.jar). Download this file and move it to the `CoreNLP` directory.

* Python 3

* Python packages: [spaCy](https://spacy.io/usage), [nltk](https://www.nltk.org/install.html) with the `punkt` resource downloaded.

* For quote attribution, you will need to install:
	* [BookNLP](https://github.com/dbamman/book-nlp). Make sure this is working properly by running the test described in their README.
	* [SVMRank](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html). Download the binary file appropriate for your OS. Then follow their instructions to unpack and install this tool.

## Input 
Directory path to directory of fanfiction story (fic) chapter CSV files. 

If your input is raw text you'll need to format it like the examples in the `example_fandom` directory. [Here's](https://github.com/michaelmilleryoder/fanfiction-nlp/blob/master/example_fandom/10118594_0004.csv) an example. Eventually we'll support raw text file input.

No tokenization or other preprocessing is necessary: that is completed in the pipeline.

## Output 
* Character coreference: 
	* a directory where fics (fanfiction stories) are stored with cluster-level coreference names appended after mentions, like this: "she ($\_hermione) and harry ($\_harry) walked through the woods". We have preprended `$_` to these cluster-level names to distinguish them from regular character mentions.
	* a directory with files with cluster-level character names for each processed fic, one per line.

* Quote attribution: 
	* a directory with a JSON file for each processed fic. Each JSON file has cluster-level character names as keys and extracted and attributed quotes as values.

* Assertion attribution: 
	* a directory where for each fic, there is a JSON file with cluster-level character names as keys and extracted assertions (narrative or evaluation) about the character as values. You can think of assertions as anything other than quotes that is relevant to seeing how a character is portrayed.

* Character cooccurrence matrix: 
	* a directory with 2 JSON files for each fic, 1 titled `{fic_name}_adj_cooccurrence.json` and the other `{fic_name}_ship_cooccurrence.json`. In each, keys are coreferenced character cluster names and values are adjectives (for the `adj` file) or other character names (for the `ship`, or "relationship", file). A cooccurrence measure is given for each adjective or character name that is between 0 and 1.

## Settings
To use the pipeline, modify the input and output settings in `run.sh`. You'll also need to add paths to BookNLP and SVMRank if you are running quote attribution. Comment out any modules that you are not running. Commands within this shell script will likely not need to be modified.

## Command
`./run.sh`

## Run a test
To test that everything is set up properly, run `run.sh`, which by default will run the pipeline on test fics in the `example_fandom` directory.
The output should be placed in a new directory, `output/example_fandom`. This output should be the same as that provided in `output_test/example_fandom`.

<!---
`./run.sh <input_dir_path>`

`<collection_name>` of fics to be processed will be extracted from the directory name of the `<input_dir_path>`.

Output is automatically stored in `output/<collection_name>`.
--->

