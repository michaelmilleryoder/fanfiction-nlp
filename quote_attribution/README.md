## Quote Attribution

The scripts for predicting the speaker of quotations in a fiction chapter given the raw text and the character list, and output to a json file.

## How To Run
### Preliminaries

* You need [BookNLP](https://github.com/dbamman/book-nlp) installed and make sure it works well.
* You need [SVM<sup>*rank*</sup>](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html) installed and make sure it works well.
* Python2 environment.

### Settings
Edit `run.sh` and update the following variables (absolute path is recommended):

* `SVMRANK_BASE`: the directory where SVM<sup>*rank*</sup> installed.
* `BOOKNLP_BASE`: the directory where BookNLP installed.
* `DATA_BASE`: the directory where you put the data. The script will also generate some temporary files in this directory.

### Data
For each fiction, the script takes two input files: the original text file, which is just a plain text file that contains the content of the fiction, and the character list file, which contains the characters that you want for quote attribution. In the character list file, each character takes one line with the following format:

```
<character_name>;<gender>[;<alias_1>[;<alias_2>[...]]]
```

* `<character_name>`: the primary name of the character (chould contain spaces). This should be unique for each character.
* `<gender>`: the gender of this character. The possible values are `M` or `F`.
* `<alias>`: **(optional)** the other names of this character, which should be following `<gender>` and separated by semicolons.

Put the data directly under the `DATA_BASE` directory (without sub-directory), for example, `DATA_BASE/myfanfic.txt` (original text file) and `DATA_BASE/myfanfic.charlist` (character list file).

### Command
From the command line, run the following:

```
bash run.sh <original_text_filename> <character_list_filename>
```

* `<original_text_filename>`: the filename of the original text file under `DATA_BASE` (without the path to `DATA_BASE`, for example, `myfanfic.txt`).
* `<character_list_filename>`: the filename of the character list file under `DATA_BASE`.

### Output
This script will output the quote attribution results to `<original_text_filename>.quote.json` with the format as:

```
{
	<character_name_1> : [
		<quote_1>,
		<quote_2>,
		......
	],
	......
}
```

Meanwhile, the script will also generate some temporary files:

* `<original_text_filename>.predict`: the scores predicted by SVM<sup>*rank*</sup>.
* `output/`: the outputs of BookNLP.
* `tokens/<original_text_filename>.tokens`: the tokenization results by BookNLP.
* `svminput/<original_text_filename>.svmrank`: the input file for SVM<sup>*rank*</sup>.