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
* Download an external Stanford CoreNLP models jar file
	* Download Stanford CoreNLP 3.9.2 here: [http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip](http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip)
	* Unzip this file and copy `stanford-corenlp-3.9.2-models.jar` to the `CoreNLP` directory.

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
The pipeline takes settings and input/output filepaths in a configuration file. An example config file is `example.cfg`. Descriptions of each configuration setting by section are as follows:

`[Input/output]`

`collection_name`: the name of the dataset (user-defined)

`input_path`: path to the directory of input files

`output_path`: path to the directory where processed files will be stored


`[Character coreference]`

`run_coref`: Whether to run character coreference (True or False)

`n_threads`: The number of threads (actually processes) to run the coreference (integer)

`split_input_dir`: Whether to split the input directory into separate directories. Do this if the input directory contains many files and you want to do multithreading (multiprocessing). For effective multithreading, the number of threads cannot be fewer than the number of directory splits. Acceptable values: True or False

`max_files_per_split`: If splitting the input directory, the maximum number of files per directory split. 100 is a good choice for fast performance.

`delete_existing_tmp`: Coreference does some preprocessing of the input CSV files into text files and splits the directory (if specified). To delete any existing temporary files and redo this process, set this to True. Otherwise, set to False.


`[Quote attribution]`

`run_quote_attribution`: Whether to run quote attribution (True or False)

`svmrank_path`: Path to SVMRank installation directory (see [quote_attribution](quote_attribution))


`[Assertion extraction]`

`run_assertion_extraction`: Whether to run assertion extraction (True or False)


## Command
`python run.py <config_file_path>`

## Run a test
To test that everything is set up properly, run `python run.py example.cfg`, which by default will run the pipeline on test fics in the `example_fandom` directory.
The output should be placed in a new directory, `output/example_fandom`. This output should be the same as that provided in `output_test/example_fandom`.
