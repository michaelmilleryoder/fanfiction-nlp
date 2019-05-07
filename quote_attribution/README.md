# Quote Attribution

The scripts for predicting the speaker of quotations in a fiction chapter given the raw or coreference resolved text and the character list, and outputing to a json file.

The current version uses [BookNLP](https://github.com/dbamman/book-nlp) for tokenization and [SVM<sup>*rank*</sup>](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html) for prediction. This version also supports multi-processing.

## File Structure

```
quote_attribution
├── example_train_data                                  (organized example training data of Pride and Prejudice (Austen. 1813))
│   ├── README.txt
│   ├── pride_prejudice.ans                             (manually annotated Pride and Prejudice quote attribution)
│   ├── pride_prejudice.chars                           (character list of Pride and Prejudice)
│   ├── pride_prejudice.csv                             (Pride and Prejudice raw story csv)
│   ├── pride_prejudice.tok                             (Pride and Prejudice tokenization in BookNLP format)
│   └── pride_prejudice.txt                             (Pride and Prejudice raw text)
├── feature_extracters                                  (feature extracter modules; new extracters should also be set in this directory)
│   ├── __init__.py                                     (necessary helper functions)
│   ├── base_feature_extracter.py                       (base class for feature extracters)
│   ├── name_in_utterance_feature_extracter.py          (`nameinuttr' feature extracter)
│   ├── neighboring_feature_extracter.py                (`neighboring' feature extracter)
│   ├── speaker_appearance_count_feature_extracter.py   (`spkappcnt' feature extracter)
│   ├── speaker_count_in_paragraph_feature_extracter.py (`spkcntpar' feature extracter)
│   └── utterance_distance_feature_extracter.py         (`disttoutter' feature extracter)
├── README.md
├── austen.model                                        (svm-rank model pre-trained with the Pride and Prejudice corpus using feature `disttoutter', `spkappcnt', `nameinuttr', and `spkcntpar')
├── chapter.py                                          (class to process chapters)
├── predict.py                                          (code for `predict' mode)
├── prepare_train.py                                    (code for `prepare-train' mode)
├── run-booknlp.sh                                      (helper shell script to run BookNLP)
├── run-svmrank.sh                                      (helper shell script to run SVM-Rank)
├── run.py                                              (main python script you will run)
├── tokens.py                                           (class to process tokens)
└── train_pride_prejudice.sh                            (example shell script to prepare SVM-Rank input file to train the `austen.model' using the Pride and Prejudice corpus)
```

## How To Run
### Preliminaries

* Python 3 environment.
* [BookNLP](https://github.com/dbamman/book-nlp) installed and make sure it works well.
* [SVM<sup>*rank*</sup>](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html) installed and make sure it works well.

### Command

The script has two running modes: "predict" or "prepare-train". In the "predict" mode, the script will take the input data to predict quote attributions and output results to json files. In the "prepare-train" mode, the script will use the input data as well as the answer files to generate training data for SVM<sup>*rank*</sup>. You should further use SVM<sup>*rank*</sup> to learn the final model.

```
usage: run.py [-h] {predict,prepare-train} 
              --story-path STORY_PATH --char-path CHAR_PATH 
              --output-path OUTPUT_PATH --features
              [{spkappcnt,nameinuttr,neighboring,disttoutter,spkcntpar} [{spkappcnt,nameinuttr,neighboring,disttoutter,spkcntpar} ...]]
              [--booknlp BOOKNLP] [--svmrank SVMRANK] [--ans-path ANS_PATH]
              [--model-path MODEL_PATH] [--tok-path TOK_PATH] [--tmp TMP]
              [--threads THREADS] [--story-suffix STORY_SUFFIX]
              [--char-suffix CHAR_SUFFIX] [--ans-suffix ANS_SUFFIX]
              [--tok-suffix TOK_SUFFIX] [--no-cipher-char] [--no-coref-story]
              [--neighboring-before NEIGHBORING_BEFORE]
              [--neighboring-after NEIGHBORING_AFTER]
```

#### Named Arguments

<table >
<thead>
<tr>
<th width=240>Argument</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>{predict, prepare-train}</code></td>
<td>running mode; if "predict", the program will predict quote attributions and output to json files; if "prepare-train", the program will prepare training data for svm-rank</td>
</tr>
<tr>
<td><code>-h, --help</code></td>
<td>show the help message and exit</td>
</tr>
<tr>
<td><code>--story-path</code></td>
<td>path to the (coreference resolved) story csv file or the directory that contains the story csv files to be processed; if this argument is a directory, --char-path, --output-path, and --gold-path should also be directories</td>
</tr>
<tr>
<td><code>--char-path</code></td>
<td>path to the (coreference resolved) character list file or the directory that contains the character list files</td>
</tr>
<tr>
<td><code>--output-path</code></td>
<td>(in "predict") path to save the output results; (in "prepare-train") path to save gathered training data</td>
</tr>
<tr>
<td><code>--features</code></td>
<td>a list of features to be extracted; the features will be extracted in the same order as this argument</td>
</tr>
<tr>
<td><code>--booknlp</code></td>
<td>path to book-nlp</td>
</tr>
<tr>
<td><code>--svmrank</code></td>
<td>path to svm-rank</td>
</tr>
<tr>
<td><code>--ans-path</code></td>
<td>(useful in "prepare-train") path to the golden answer quote attribution file or the directory that contains the golden answer quote attribution files</td>
</tr>
<tr>
<td><code>--model-path</code></td>
<td>(useful in `predict') path to read pre-trained svm-rank model; the model should be corresponding to the features you select

Default: austen.model</td>
</tr>
<tr>
<td><code>--tok-path</code></td>
<td>path to the tokenization file or the directory that contains tokenization files (in book-nlp format); as there might be mistakes in tokenization and probability you want to manually fix them, this option is useful when you want to designate tokenizations results instead of doing tokenization automatically</td>
</tr>
<tr>
<td><code>--tmp</code></td>
<td>path to the directory to store temporary files

Default: tmp</td>
</tr>
<tr>
<td><code>--threads</code></td>
<td>number of threads

Default: 1</td>
</tr>
<tr>
<td><code>--story-suffix</code></td>
<td>(needed when input path is a directory) suffix of story csv filenames

Default: .coref.csv</td>
</tr>
<tr>
<td><code>--char-suffix</code></td>
<td>(needed when input path is a directory) suffix of character list filenames

Default: .chars</td>
</tr>
<tr>
<td><code>--ans-suffix</code></td>
<td>(needed when input path is a directory) suffix of golden answer quote attribution filenames

Default: .ans</td>
</tr>
<tr>
<td><code>--tok-suffix</code></td>
<td>(needed when input path is a directory and --tok-path is set) suffix of tokenization filenames

Default: .tok</td>
</tr>
<tr>
<td><code>--no-cipher-char</code></td>
<td>do not cipher character name; for the sake of tokenization, the script will change the coreference character annotation marks to ccc_CHARACTER_ccc if this argument is not selected</td>
</tr>
<tr>
<td><code>--no-coref-story</code></td>
<td>story files are not coreference resolved (useful when you want to train a new model and use golden character list; sometimes coreference resolution cannot retrieve all correct characters)</td>
</tr>
<tr>
<td><code>--neighboring-before</code></td>
<td>number of utterances before the current one to be incorporated in neighboring feature

Default: 1</td>
</tr>
<tr>
<td><code>--neighboring-before</code></td>
<td>number of utterances after the current one to be incorporated in neighboring feature

Default: 1</td>
</tr>
</tbody>
</table>

### Data Format
For each fiction, the script takes two primary input files: the coreference resolved or raw text csv file and the character list file, which contains the characters that you want for quote attribution. You may also need gold answer files (in "prepare-train") and tokenization files.

#### Text csv

The text csv file should have three columns and multiple rows, where the first row is the header, the first column is the chapter ID, the second column are the paragraph IDs, and the third column is the text.

`example_train_data/pride_prejudice.csv` is an example of raw text csv file.

#### Character list

In the character list file, each character takes one line with the following format:

```
<character_name>[;<gender>[;<alias_1>[;<alias_2>[...]]]]
```

* `<character_name>`: the primary name of the character (chould contain spaces); this should be unique for each character (if it is from coreference resolution, it should be like `($_XXX_YYY)`)
* `<gender>`: (optional) the gender of this character, either `M` or `F`
* `<alias>`: (optional) the other names of this character, which should be following `<gender>` and separated by semicolons

`example_train_data/pride_prejudice.chars` is an example of character list (not from coreference resolution).

#### Gold answer

The gold answer files are required in the `prepare-train` mode. The gold answer file contains the correct speakers and their utterances, and follows the following format:

```
<chapter_id>	<character_name>	<paragraph>
```
where `<chapter_id>`, `<character_name>`, and `<paragraph>` are tabs (`\t`) separated.

* `<chapter_id>`: chapter ID of the utterance (not actually used)
* `<character_name>`: the primary name of the character (should be corresponding to the character list file).
* `<paragraph>`: the utterance contents in the paragraph (assuming that one paragraph has only one speaker); non-utterance content should be replaced by `[x]`.

`example_train_data/pride_prejudice.chars` is an example of gold answer file.


#### Customized tokenization

The customized tokenization files are optional. The script uses BookNLP to tokenize input text, however, there might be mistakes in tokenization results. If you want to use customized tokenization or fix mistakes in BookNLP results, you could provide tokenization files with the command-line argument `--tok-path`. Tokenization files should be in the format of BoolNLP tokenization results.

`example_train_data/pride_prejudice.tok` is an example of tokenization file.

### Output
This script will output the quote attribution results to `<quote_output_dir>/<story_filename>.quote.json` (when `--story-path` pointing to a directory) or to the file `--output-path` point to (when `--story-path` pointing to a file) with the format as:

```
[
    {
        "speaker": <character_name>,
        "quotes": [
            {
                "start": <quote_start_token_id>,
                "end": <quote_end_token_id>,
                "quote": <quote_content>
            },
            ...
        ],
        "paragraph": <paragraph_id>,
        "type": <quote_type>,
        "start": <paragraph_start_token_id>,
        "end": <paragraph_end_token_id>,
        "replyto": <reply_to_paragraph_id>
    },
    ...
]
```

The output json file is organized by paragraphs. In summary, the output json file contains a list of paragraph quote attributions (assuming that each paragraph has only one speaker) represented as key-value directories.

* `speaker`: the primary character name corresponding to the character list file.
* `quotes`: a list of quotes in the paragraph, with start token IDs, end token IDs, and quote contents
* `paragraph`: the paragraph ID
* `type`: either "Explicit" or "Implicit"; quote attribution has higher confidence with "Explicit" quotes
* `start`: paragraph start token ID
* `end`: paragraph end token ID
* `replyto`: quote attribution will guess the conversation chain and try to guess the ID of the paragraph that this paragragh's quotes are replying to

Meanwhile, the script will also generate some temporary files in `<tmp>/<story_filename>/`:

* `booknlp_output/`: the outputs of BookNLP
* `booknlp.log`: BookNLP log output
* `story_tmp.txt`: the temporary file for processing the story text
* `char_tmp.txt`: the temporary file for processing the character list
* `token_tmp.txt`: the tokenization results by BookNLP
* `svmrank_input.txt`: the input file for SVM<sup>*rank*</sup>
* `svmrank_predict.txt`: the scores predicted by SVM<sup>*rank*</sup>

## Scalability

The script contains five feature extracters: `spkappcnt`, `nameinuttr`, `neighboring`, `disttoutter`, and `spkcntpar`. You can create new feature extracters by extending the `BaseFeatureExtracter` class. New feature extracter can be added to quote attribution with the decorator `register_extracter`, for example: 

```
@register_extracter('extracter_name')
class YourFeatureExtracter(BaseFeatureExtracter):
    (...)
```

Registered feature extracters will be automatically added to the choices of the `--features` argument.

It is required to implement the `extract(self, ret, **kargs)` function and the `build_extracter(cls, args)` functions for feature extracters. You can also implement the `add_args(parser)` function if you want to Add feature-extracter-specific arguments to the command line parser.

## How it works
Based on the following papers:
* He et al., 2013, "Identification of speakers in novels". Data and algorithm (SVM<sup>*rank*</sup>) come from this paper.
* Elson et al., 2010, AAAI, "Automatic attribution of quoted speech". Features mainly come from this paper.

This quote attribution script assumes each paragraph has only one speaker, and will conduct the following operations:

1. Preprocess the character list and story text. For the sake of tokenization, the script will cipher the characters' name if `--no-cipher-char` is not selected.
2. Do tokenization using BookNLP.
3. Extract features in the same order as the argument `--features`.
4. Output features into SVM<sup>*rank*</sup> input format and use SVM<sup>*rank*</sup> to predict speakers.
5. Read the SVM<sup>*rank*</sup> output file, guess conversation chain, and output to the destination json file.

### Built-in Features
The features extracters will extract quote attribution features for each character on each paragraph. The following are the built-in features in the script:

* **Distance to utterance** (`disttoutter`): This feature captures the distance between the mention of the character and the utterance. The intuition is that near character is likely to be the speaker. This feature will be represented as 1 / (dist + 1). 
* **Speaker mention count** (`spkappcnt`): This feature is the count of the mention of the character in the text (represented as frequency), which could be considered as the prior probability that the character speaks.
* **Speaker mention count in paragraph** (`spkcntpar`): This feature counts the number of appearance of the character in the paragraph of the utterance but not in the utterance. Although the character in the utterance may not be the speaker, the character appears frequently in the same paragraph of the quotation is likely to be the speaker, which means the character is locally active. This feature is original.
* **Name in utterance** (`nameinuttr`): This binary feature represents whether the name of the character appears in the sentence of the utterance. Except for some rare scenarios (e.g., "My name is ..." or using selfs name as the replacement of "I" in utterances), the characters appear in the utterance are usually not the speaker, for example, "How are you, Kate?".
* **Neighboring** (`neighboring`): The above features of the same character with regard to neighboring utterances are also incorporated. The intuition of this feature is the nature of "conversation chain" that neighboring utterances is not likely to be spoken by the same character without additional cue.
