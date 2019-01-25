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

### Data
For each fiction, the script takes two input files: the original text csv file and the character list file, which contains the characters that you want for quote attribution. In the character list file, each character takes one line with the following format:

```
<character_name>[;<gender>[;<alias_1>[;<alias_2>[...]]]]
```

* `<character_name>`: the primary name of the character (chould contain spaces). This should be unique for each character. (For now it should be like `($_XXX_YYY)`)
* `<gender>`: (optional) the gender of this character, either `M` or `F`.
* `<alias>`: (optional) the other names of this character, which should be following `<gender>` and separated by semicolons.

### Command
From the command line, run the following (absolute path is recommended):

```
bash run.sh <story_dir> <character_list_dir> <quote_output_dir>
```

* `<story_dir>`: the directory that contains the story text csv files.
* `<character_list_dir>`: the directory that contains the corresponding character lists.
* `<quote_output_dir>`: the directory that the quotation attribution outputs will be stored.

### Output
This script will output the quote attribution results to `<quote_output_dir>/<story_filename>.quote.json` with the format as:

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

Meanwhile, the script will also generate some temporary files in `tmp/<story_filename>/`:

* `booknlp_output/`: the outputs of BookNLP.
* `<story_filename>.tmptext`: the temporary file for processing the story text.
* `<story_filename>.tmpchar`: the temporary file for processing the character list.
* `<story_filename>.tokens`: the tokenization results by BookNLP.
* `<story_filename>.predict`: the scores predicted by SVM<sup>*rank*</sup>.
* `<story_filename>.svmrank`: the input file for SVM<sup>*rank*</sup>.