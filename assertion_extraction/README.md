# Assertion Extraction

Scripts for extracting statements with mentions of characters, given the stories (a directory of csv files) and a list of characters. The output is a JSON file.

## Prerequisites

* Python2 environment
* Numpy
* NLTK
* Sci-kit learn


## Data
* A directory of fan-fiction stories with files in the format fanficstoryID\_chapterID.coref.out .
Let's call this \<fandom_dir>

* A list of characters corresponding to each fanficstoryID\_chapterID.coref.chars . Let's call this \<chars_dir> 

## How the script works

Once the coreference resolution is done and we have the normalized files and the list of characters for each of the chapters of the fanfics, we perform text-tiling ( Adapted from: [TextTiling: Segmenting Text into Multi-paragraph Subtopic Passages](http://www.aclweb.org/anthology/J97-1003))

After text-tiling has been performed, we have a lookup table with paragraph IDs as the key and the segments from the paragraph as the value.

For each character in the character list we look through each of the segments in each paragraph and find the segment in which a character is mentioned. We do not use the part of the segment where the character in mentioned in a quote.


## Command

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

