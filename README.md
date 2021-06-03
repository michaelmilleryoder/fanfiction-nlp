# fanfiction-nlp
An NLP pipeline for extracting information related to characters in fanfiction.
For each input fanfiction story (or other document), the pipeline produces a list of characters.
For each character, the pipeline produces:
* mentions of the character in the text (such as pronouns that refer to the character)
* quotes attributed to that character
* ``assertions'', or any non-quote span, that contains character mentions. These assertions would include description and narration involving that character.

More information on the pipeline is available in the paper [here](https://www.aclweb.org/anthology/2021.nuse-1.2.pdf).
If you use it academically, please cite this work:
> Michael Miller Yoder, Sopan Khosla, Qinlan Shen, Aakanksha Naik, Huiming Jin, Hariharan Muralidharan, and Carolyn P Rosé. 2021. FanfictionNLP : A Text Processing Pipeline for Fanfiction. In *Proceedings of the 3rd Workshop on Narrative Understanding*, pages 13–23.

Contact Michael Miller Yoder <yoder [at] cs.cmu.edu> with any questions.

# Running the pipeline
This pipeline processes a directory of fanfiction files and extracts
 text that is relevant for each character.
 
The pipeline does:
* [Character coreference](char_coref)
* Character feature extraction
	* [Quote attribution](quote_attribution)
	* [Assertion attribution](assertion_extraction) (narrative and evaluation about a character)

## Requirements
A list of dependencies from which a Python 3 virtual environment can be created is at `requirements.txt'.
(The list is a bit bloated, so some packages may not be necessary.)

## Input 
Directory path to directory of fanfiction story CSV files. 

If your input is raw text you'll need to format it like the examples in the `example_fandom` directory. [Here's](https://github.com/michaelmilleryoder/fanfiction-nlp/blob/master/example_fandom/10118594_0004.csv) an example. Eventually we'll support raw text file input.

Please tokenize text (split into words) before running it through the pipeline and include this as a fourth column, `text_tokenized`. We are working on including this as an option.

## Output 
* Character coreference: 
	* a directory with a JSON file for each processed fic. The JSON file has the following keys:
		* `document`: string of tokenized text (space between each token)
		* `clusters`: a list of character clusters, each with the fields:
			* `name`
			* `mentions`: a list of mentions, each a dictionary with keys:
				* `position`: [start_token_id, end_token_id+1]. The position of the start token of the mention in the `document` list (inclusive), and the position 1 after the last token in the mention in the `document` list.
				* `text`: The text of the mention
	<!-- * a directory where fics (fanfiction stories) are stored with character mentions surrounded by cluster-level coreference names in XML tags, like this: "\<character name="hermione"\>she\</character\> and \<character name="harry"\>harry\</character\> walked through the woods".-->
	<!--* a directory with files with cluster-level character names for each processed fic, one per line.-->

* Quote attribution: 
	* a directory with a JSON file for each processed fic. Each JSON file has cluster-level character names as keys and a list of dictionaries as values, one for each quote spoken by the character:
		* `position`: [start_token_id, end_token_id+1]. The position of the start token of the mention in the coreference `document` list (inclusive), and the position 1 after the last token in the mention.
		* `text`: The text of the quote
		<!--* `chapter`-->
		<!--* `paragraph`-->

* Assertion attribution: 
	* a directory with a JSON file for each processed fic. Each JSON file has cluster-level character names as keys and a list of dictionaries as values, one for each assertion (narrative or evaluation) about the character:
		* `position`: [start_token_id, end_token_id+1]. The position of the start token of the assertion in the `document` list (inclusive), and the position 1 after the last token in the assertion in the `document` list.
		* `text`: The text of the assertion
Assertions are any text other than quotes that is relevant to seeing how a character is portrayed.

## Settings
The pipeline takes settings and input/output filepaths in a configuration file. An example config file is `example.cfg`. Descriptions of each configuration setting by section are as follows:

#### `[Input/output]`

`collection_name`: the name of the dataset (user-defined)

`input_path`: path to the directory of input files

`output_path`: path to the directory where processed files will be stored


#### `[Character coreference]`

`run_coref`: (True or False) Whether to run character coreference.

`n_threads`: (integer) The number of threads (actually processes) to run the coreference


#### `[Quote attribution]`

`run_quote_attribution`: Whether to run quote attribution (True or False)

`n_threads`: (integer) The number of threads (actually processes) to run the quote attribution


#### `[Assertion extraction]`

`run_assertion_extraction`: Whether to run assertion extraction (True or False)

`n_threads`: (integer) The number of threads (actually processes) to run the quote attribution


## Command
`python run.py <config_file_path>`

## Run a test
To test that everything is set up properly, run `python run.py example.cfg`, which by default will run the pipeline on test fics in the `example_fandom` directory.
The output should be placed in a new directory, `output/example_fandom`. This output should be the same as that provided in `output_test/example_fandom`.

# Notes
This pipeline was inspired by David Bamman's [BookNLP](https://github.com/dbamman/book-nlp).
