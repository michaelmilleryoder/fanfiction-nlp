# Assertion Extraction

Scripts for extracting statements with mentions of characters, given the stories (a directory of csv files) and a list of characters. The output is a JSON file.

## Prerequisites

* Python2 environment
* Numpy
* NLTK
* Sci-kit learn


## Data
*A directory of fan-fiction stories with files in the format fanficstoryID\_chapterID.coref.out .
Let's call this \<fandom_dir>

*A list of characters corresponding to each fanficstoryID\_chapterID.coref.chars . Let's call this \<chars_dir> 

##Command

	python extract_assertions.py <fandom_dir> <chars_dir> <output_dir>
	

## Output
The output will be JSON files, one per fanficstoryID_chapterID.

The format of each file is as follows:
	
	{
		<Character_name1> : [
				<assertion_1>,
				<assertion_2>,
				...
				]
		...
	}

