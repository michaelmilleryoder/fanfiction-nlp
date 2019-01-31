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
## Command

	python cooccurance_generation.py <fandom_dir>
	

## Output
The output will be a text file.

