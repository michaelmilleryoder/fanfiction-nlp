# Co-occurence matrix

Script for creating a co-occurence matrix with respect to entities classified as "Persons".
The script identitifies the co-occuring characters and adjectives for a character and ranks them via TF-IDF.

## Prerequisites

* Python3 environment
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
Creates 2 JSON files per input fic. One file lists the co-occuring characters for each entity and the other lists the co-occuring adjectives for each entity.

