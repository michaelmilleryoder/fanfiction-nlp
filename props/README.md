# Co-occurence matrix

Script for creating a co-occurence matrix with respect to entities classified as "Persons".

## Prerequisites

* Python2 environment
* spaCy
* en_core_web_sm model for spaCy
* Sci-kit learn


## Data
*A directory of fan-fiction stories with files in the format fanficstoryID\_chapterID.coref.out .
Let's call this \<fandom_dir>

*Output directory for the JSON file to be written. Let's call this \<output_dir>

*A directory of files containing the list of characters. Let's call this \<char_dir>
## Command

	python cooccurance_generation.py <fandom_dir> <output_dir> <char_dir>
	

## Output
The output will be a JSON file.

