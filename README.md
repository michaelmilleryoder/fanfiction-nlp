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
	* [SVMRank](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html). Download the binary file appropriate for your OS. Then follow their instructions to unpack and install this tool.

## Input 
Directory path to directory of fanfiction story (fic) chapter CSV files. 

If your input is raw text you'll need to format it like the examples in the `example_fandom` directory. [Here's](https://github.com/michaelmilleryoder/fanfiction-nlp/blob/master/example_fandom/10118594_0004.csv) an example. Eventually we'll support raw text file input.

Please tokenize text (split into words) before running it through the pipeline and include this as a fourth column, `text_tokenized`. We are working on including this as an option.

## Output 
* Character coreference: 
	* a directory with a JSON file for each processed fic. The JSON file has the following keys:
		* `document`: list of tokenized text (space between each token)
		* `clusters`: a list of character clusters, each with the fields:
			* `name`
			* `mentions`: a list of mentions, each a dictionary with keys:
				* `position`: [start_token_id, end_token_id+1]. The position of the start token of the mention in the `doc_tokens` list (inclusive), and the position 1 after the last token in the mention in the `doc_tokens` list.
				* `text`: The text of the mention
	<!-- * a directory where fics (fanfiction stories) are stored with character mentions surrounded by cluster-level coreference names in XML tags, like this: "\<character name="hermione"\>she\</character\> and \<character name="harry"\>harry\</character\> walked through the woods".-->
	<!--* a directory with files with cluster-level character names for each processed fic, one per line.-->

* Quote attribution: 
	* a directory with a JSON file for each processed fic. Each JSON file consists of a list of "quote entries" for a unique speaker in a paragraph. Keys in each quote entry include:
		* `speaker`
		* `quotes`: a list of quotes, each a dictionary with keys:
			* `start_token_id`: the position of the start token of the quote in the `tokens` list (inclusive)
			* `end_token_id`: the position 1 after the last token in the quote in the `tokens` list
		<!--* `chapter`-->
		<!--* `paragraph`-->

* Assertion attribution: 
	* a directory where for each fic, there is a JSON file with cluster-level character names as keys and extracted assertions (narrative or evaluation) about the character as a list of values. Assertions are any text other than quotes that is relevant to seeing how a character is portrayed.

* Character cooccurrence matrix: 
	* a directory with 2 JSON files for each fic, 1 titled `{fic_name}_adj_cooccurrence.json` and the other `{fic_name}_ship_cooccurrence.json`. In each, keys are coreferenced character cluster names and values are adjectives (for the `adj` file) or other character names (for the `ship`, or "relationship", file). A cooccurrence measure is given for each adjective or character name that is between 0 and 1.

## Settings
The pipeline takes settings and input/output filepaths in a configuration file. An example config file is `example.cfg`. Descriptions of each configuration setting by section are as follows:

#### `[Input/output]`

`collection_name`: the name of the dataset (user-defined)

`input_path`: path to the directory of input files

`output_path`: path to the directory where processed files will be stored


#### `[Character coreference]`

`run_coref`: (True or False) Whether to run character coreference.

`n_servers`: (integer) Coreference runs by starting a number of local servers on whatever machine the processing is done on. This specifies how many servers should be run. More servers generally increases processing speed, though starting more servers than threads does not.

`n_threads`: (integer) The number of threads (actually processes) to run the coreference. Try setting this number to 3-4 times the number of servers used.


#### `[Quote attribution]`

`run_quote_attribution`: Whether to run quote attribution (True or False)

`svmrank_path`: Path to SVMRank installation directory (see [quote_attribution](quote_attribution))


#### `[Assertion extraction]`

`run_assertion_extraction`: Whether to run assertion extraction (True or False)


## Command
`python run.py <config_file_path>`

## Run a test
To test that everything is set up properly, run `python run.py example.cfg`, which by default will run the pipeline on test fics in the `example_fandom` directory.
The output should be placed in a new directory, `output/example_fandom`. This output should be the same as that provided in `output_test/example_fandom`.
