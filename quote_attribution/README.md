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
              --story-path STORY_PATH --char-path CHAR_PATH --output-path
              OUTPUT_PATH [--ans-path ANS_PATH] [--model-path MODEL_PATH]
              --features
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
<td><code>--ans-path</code></td>
<td>(useful in "prepare-train") path to the golden answer quote attribution file or the directory that contains the golden answer quote attribution files</td>
</tr>
<tr>
<td><code>--model-path</code></td>
<td>(useful in `predict') path to read pre-trained svm-rank model; the model should be corresponding to the features you select

Default: austen.model</td>
</tr>
<tr>
<td><code>--features</code></td>
<td>a list of features to be extracted; the features will be extracted in the same order as this argument</td>
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
<td><code>--booknlp</code></td>
<td>path to book-nlp</td>
</tr>
<tr>
<td><code>--svmrank</code></td>
<td>path to svm-rank</td>
</tr>
</tbody>
</table>

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
