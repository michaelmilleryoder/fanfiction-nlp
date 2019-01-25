# Alternate Universe Tagger

Three steps to tag an unlabelled fanfiction:

  - Define a set of alternate universe and identify keywords typical of each alternate universe
  - Train Naive Bayers classifier 
  - Use Naive Bayers classifier or BM25 language model to tag the unlabelled fanfiction


### Prediction
run csv2txt.py to convert .csv file to .txt file

```sh
python csv2txt.py example_fandom/ example_fandom_txt/
```

set the following file paths in default.ini

```sh
test_csv_dir = ../example_fandom/
test_txt_dir = ../example_fandom_txt/
```
run BM25 classifier
```sh
python BM25.py default.ini DEFAULT
```

run Naive Bayes classifier
```sh
python nb.py default.ini DEFAULT
```

labels are stored in bm25_labels.txt and nb_labels.txt, format for each line:
ficid-chapterid: (assigned label, confidence score)


### Todos

 - Refactor code for training model




clean_labels.txt:
	selected alternate universe labels, each line represents a group of similar alternate universes

default.ini:
	input file path and parameters configuration file.

test_preprocess.py:
	preprocess the csv file to txt file

generate_keywords.py:
	usage: python generate_keywords.py [configuration file name] [configuration file section]
	eg. `python generate_keywords.py default.ini DEFAULT`

	this script identifies fics that explicitly mention their alternate universes in the metadata restricted to aus in clean_labels.txt file, and store it to fic2idx.pkl file, then for each label, we collect all the fics with this au label, remove non-ascii characters, punctuation and stopwords, perform lemmatization. Each fic is treated as a set of words. We use tf-idf score to rank all the words in the fics with the same label, and store the keywords information to keywords_path.

nb_preprocess.py:
	usage: python nb_preprocess.py [configuration file name] [configuration file section]

	this script generates word frequency file under each label based on idx2fic (train set)

nb.py:
	usage: python nb.py [configuration file name] [configuration file section]
	based on keywords.txt, this script assigns labels to unlabelled fic, avg_doclen should be precomputed and set in configuration file



BM25.py:
	usage: python BM25.py [configuration file name] [configuration file section]

	based on keywords.txt, this script assigns labels to unlabelled fic, avg_doclen should be precomputed and set in configuration file

