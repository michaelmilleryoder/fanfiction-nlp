# fanfiction-nlp
NLP tools for fanfiction, based on David Bamman's BookNLP beginning 2018. Contact Michael Miller Yoder <michaelmilleryoder [at] gmail.com> with questions.

# Running the pipeline
This script processes a directory of fanfiction files and extracts
 relevant text to characters, as well as fic AU metadata.
 
The script does:
* Character coreference
* Character feature extraction
	* Quote attribution
	* Assertion (facts about a character) attribution
* Character cooccurrence matrix
* Alternate universe (AU) extraction from fic metadata

## Requirements
* Parts of the pipeline require [this Stanford CoreNLP models jar](http://nlp.stanford.edu/software/stanford-corenlp-models-current.jar). Download this file and move it to the `CoreNLP` directory.

* Python 2 and Python 3 (we're moving everything to Python 3 soon).

* Python packages: spaCy

## Input 
Directory path to directory of fic chapter CSV files. 

If your input is raw text you'll need to format it like the examples in the `example_fandom` directory. [Here's](https://github.com/michaelmilleryoder/fanfiction-nlp/blob/master/example_fandom/10118594_0004.csv) an example. Eventually we'll support raw text file input.

No tokenization or other preprocessing is necessary: that is completed in the pipeline.

## Output 
* Character coreference: 
	* a directory where fics are stored with cluster-level names appended after mentions, like this: "she ($\_hermione) and harry ($\_harry) walked through the woods".
	* a directory with files with cluster-level character names for each processed fic, one per line.

* Quote attribution: 
	* a directory with a JSON files for each fic. Each JSON file has cluster-level character names as keys and extracted and attributed quotes as keys.

* Assertion attribution: 
	* a directory where for each fic, there is a JSON file with keys as cluster-level character names and values with extracted assertions (statements or facts) about the character.

* Character cooccurrence matrix: 
	* description of output

* Alternative universe (AU) extraction:
	* a directory where for each fic, there is a list of predicted AU metadata tags, as well as confidence values in those predictions

## Command
`./run.sh`

<!---
`./run.sh <input_dir_path>`

`<collection_name>` of fics to be processed will be extracted from the directory name of the `<input_dir_path>`.

Output is automatically stored in `output/<collection_name>`.
--->

