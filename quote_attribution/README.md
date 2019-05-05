# Quote Attribution

The scripts for predicting the speaker of quotations in a fiction chapter given the raw or coreference resolved text and the character list, and output to a json file.

Current version uses [BookNLP](https://github.com/dbamman/book-nlp) for tokenization and [SVM<sup>*rank*</sup>](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html) for prediction. This version also supports multi-processing.

## How To Run
### Preliminaries

* Python 3 environment.
* [BookNLP](https://github.com/dbamman/book-nlp) installed and make sure it works well.
* [SVM<sup>*rank*</sup>](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html) installed and make sure it works well.

### Command

The script has two running modes: "predict" or "prepare-train". In the "predict" mode, the script will take the input data to predict quote attributions and output results to json files. In the "prepare-train" mode, the script will the input data as well as the answer files to generate training data for SVM<sup>*rank*</sup>. You should further use SVM<sup>*rank*</sup> to learn the final model.

```
usage: run.py [-h] {predict,prepare-train}
              --story-path STORY_PATH --char-path CHAR_PATH
              [--ans-path ANS_PATH] --output-path OUTPUT_PATH
              [--model-path MODEL_PATH] --features
              [{spkappcnt,nameinuttr,neighboring,disttoutter,spkcntpar} [{spkappcnt,nameinuttr,neighboring,disttoutter,spkcntpar} ...]]
              [--gold-path GOLD_PATH] [--tok-path TOK_PATH] [--tmp TMP]
              [--threads THREADS] [--story-suffix STORY_SUFFIX]
              [--char-suffix CHAR_SUFFIX] [--ans-suffix ANS_SUFFIX]
              [--tok-suffix TOK_SUFFIX] [--no-cipher-char] [--no-coref-story]
              [--booknlp BOOKNLP] [--svmrank SVMRANK]
              [--neighboring-before NEIGHBORING_BEFORE]
              [--neighboring-after NEIGHBORING_AFTER]
```

#### Named Arguments

| Argument | Description |
| :------- | :---------- |
| {predict, prepare-train} | Running mode. If "predict", the program will predict quote attributions and output to json files. If "prepare-train", the program will prepare training data for svm-rank. |



From the command line, run the following (absolute path is recommended):

```
bash run.sh <story_dir> <character_list_dir> <quote_output_dir>
```

* `<story_dir>`: the directory that contains the story text csv files.
* `<character_list_dir>`: the directory that contains the corresponding character lists.
* `<quote_output_dir>`: the directory that the quotation attribution outputs will be stored.

### Data
For each fiction, the script takes two primary input files: the original text csv file and the character list file, which contains the characters that you want for quote attribution. In the character list file, each character takes one line with the following format:

```
<character_name>[;<gender>[;<alias_1>[;<alias_2>[...]]]]
```

* `<character_name>`: the primary name of the character (chould contain spaces). This should be unique for each character. (For now it should be like `($_XXX_YYY)`)
* `<gender>`: (optional) the gender of this character, either `M` or `F`.
* `<alias>`: (optional) the other names of this character, which should be following `<gender>` and separated by semicolons.

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

## How it works
Based on the following papers:
* He et al., 2013, "Identification of speakers in novels". Data and algorithm (SVM<sup>*rank*</sup>) came from this paper.
* Elson et al., 2010, AAAI, "Automatic attribution of quoted speech". Features mainly came from this paper.

### Features
Features for each utterance are specific to each speaker from the coreference step.
* Distance to utterance
* Number of times the speaker appears in whole text
* Number of times the speaker appears in the paragraph
* Speaker in the utterance
* Same features, but for neighboring utterances
