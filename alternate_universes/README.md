# Alternate Universe Tagger

Three steps to tag an unlabelled fanfiction:

  - Manually define a set of alternate universe and identify keywords typical of each alternate universe using tf-idf
  - Train Naive Bayes classifier 
  - Use Naive Bayes classifier or BM25 language model to tag the unlabelled fanfiction

### Training
1.create a new directory (eg. friends/) in params/ and set the following file paths in friends.ini

```sh
stories_path = /usr2/scratch/fanfic/ao3_friends_text/stories.csv
# directory where all the specific stories locate
stories_dir_path = /usr2/scratch/fanfic/ao3_friends_text/stories/
tags_path = params/friends/tags.pkl
aus_path = params/friends/aus.pkl
# documnt frequency for each word in the dataset
df_path = params/friends/df_new.pkl
# selected alternate universe labels
labels_path = params/friends/clean_labels.txt
# keywords for each alternate universe
keywords_path = params/friends/keywords.txt
fic2idx_path = params/friends/fic2idx.pkl
idx2fic_path = params/friends/idx2fic.pkl
idx_wordcount_path = params/friends/idx_wordcount.txt
idx_prob_path = params/friends/idxprob.pkl

```
2.run preprocess.py to get tags and aus mentioned in the training set
```sh
python preprocess.py [configuration file name] [configuration file section]
```

3.run cal_df.py to get document frequency for each word in all stories

```sh
python cal_df.py [configuration file name] [configuration file section]
```

4.Manully select alternate universe labels.
use tag_cluster.py to inspect high frequency words within au tags
```sh
python tag_cluster.py [configuration file name] [configuration file section] highFreq topN
 ```

then check which aus share the same high frequency word

```sh
python tag_cluster.py [configuration file name] [configuration file section] search_string
 ```

use tag_search.py to specify a word, it will return the list of fictions whose au labels contain this word.

```sh
python tag_search.py [configuration file name] [configuration file section] search_string
```

use tag_keyword.py to check the keywords identified by tf-idf for each search string. For two search strings, if their identified keywords look similar, we may conclude that aus contain these search strings are similar.
```sh
python tag_keyword.py [configuration file name] [configuration file section] search_string topN
```
write the list of alternate universe labels to labels_path defined in configuration file, eg.

```sh
fantasy,magic,medieval,royalty,dragon,fairy,tale
college/university,college,university,school
soulmate,soulmates
coffee
```

Each line denotes one au category, with words separated by comma. If au tag A is 'fantasy au' and au tag B is 'magic au', we classify these two to one au category


5.generate keywords using tf-idf algorithm for each au category by running
```sh
python generate_keywords.py [configuration file name] [configuration file section]
```
6.train naive bayes classifier by running:
```sh
python nb_preprocess.py [configuration file name] [configuration file section]
```

7.BM25 classifier does not require training, for usage, refer to prediction section.

### Prediction
run csv2txt.py to convert .csv file to .txt file

```sh
python csv2txt.py example_fandom/ example_fandom_txt/
```

set the following file paths in friends.ini

```sh
test_csv_dir = ../example_fandom/
test_txt_dir = ../example_fandom_txt/
```
run BM25 classifier
```sh
python BM25.py friends.ini DEFAULT
```

run Naive Bayes classifier
```sh
python nb.py friends.ini DEFAULT
```

labels are stored in bm25_labels.txt and nb_labels.txt, format for each line:
```sh
ficid-chapterid: (assigned label, confidence score)
```


clean_labels.txt:
	selected alternate universe labels, each line represents a group of similar alternate universes

friends.ini:
	input file path and parameters configuration file.

csv2txt.py:
	preprocess the csv file to txt file

generate_keywords.py:
	usage: python generate_keywords.py [configuration file name] [configuration file section]
	eg. `python generate_keywords.py friends.ini DEFAULT`
	this script identifies fics that explicitly mention their alternate universes in the metadata restricted to aus in clean_labels.txt file, and store it to fic2idx.pkl file, then for each label, we collect all the fics with this au label, remove non-ascii characters, punctuation and stopwords, perform lemmatization. Each fic is treated as a set of words. We use tf-idf score to rank all the words in the fics with the same label, and store the keywords information to keywords_path.

nb_preprocess.py:
	usage: `python nb_preprocess.py [configuration file name] [configuration file section]`
	this script generates word frequency file under each label based on idx2fic (train set)

nb.py:
	usage: `python nb.py [configuration file name] [configuration file section]`
	based on keywords.txt, this script assigns labels to unlabelled fic, avg_doclen should be precomputed and set in configuration file



BM25.py:
	usage: `python BM25.py [configuration file name] [configuration file section]`
	based on keywords.txt, this script assigns labels to unlabelled fic, avg_doclen should be precomputed and set in configuration file

tag_cluster.py:
	usage: `python tag_cluster.py:
 [configuration file name] [configuration file section] search_string`
 	or `python tag_cluster.py:
 [configuration file name] [configuration file section] highFreq topN`












