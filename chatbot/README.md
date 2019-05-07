# Retrieval based chatbot

Three steps to build the retrieval based chatbot:

  - Collect and preprocess dialog dataset
  - Use gensim doc2vec to get sentence embeddings
  - During retrieval, we firstly retrieve k-nearest neighbours of user input based on sentence embeddings from doc2vec, then we utilize the skipthought semantic relatedness classifier to choose the response that has the highest semantic relatedness score

### Build Chatbot
1.preprocessed .json data should be saved in data/
2.preprare model files and word embeddings used for skipthoughts package. These files are quite large(>2GB). You may refer to the README in skipthoughts/ to check the required package.
```sh
cd skipthoughts/params
wget http://www.cs.toronto.edu/~rkiros/models/dictionary.txt
wget http://www.cs.toronto.edu/~rkiros/models/utable.npy
wget http://www.cs.toronto.edu/~rkiros/models/btable.npy
wget http://www.cs.toronto.edu/~rkiros/models/uni_skip.npz
wget http://www.cs.toronto.edu/~rkiros/models/uni_skip.npz.pkl
wget http://www.cs.toronto.edu/~rkiros/models/bi_skip.npz
wget http://www.cs.toronto.edu/~rkiros/models/bi_skip.npz.pkl
```

3.extract dialogs from json file, the dialogs file would be saved to dialogs/
```sh
cd ../..
mkdir dialogs
python json2txt_all.py data/ dialogs/
```
4.train sentence embedding based on extracted q files
```sh
python train_doc2vec.py dialogs/all_q.txt
```
5.run the chatbot
```sh
python bot2.py dialogs/all Connor 10
 ```
Here, "Connor" is the name of a speaker. By specifying "Connor", we aim to extract replys from Connor. 
"10" is the K for K nearest neighbours when searching for the similar sentence embedding in the first stage. 


### Extract templates
When we test the chatbot, we find that the "question" and "answer" pair do not fit quite well since either of them could be long paragraph. We decide to extract the common sentence pairs of "question" and "answer" pair.

1.split the paragraph into sentences
```sh
python flatten.py dialogs/all_q.txt```
python flatten.py dialogs/all_a.txt```
```
2.count the mappings between sentences
```sh
python count.py dialogs/all```
```

2.generate new q and a file based on the mappings
```sh
python template.py dialogs/all 1
```
Here "1" means that, we would filter out the mapping sentence pair that occurs less than 1 times.

3.train doc2vec based on the template
```sh
python train_doc2vec.py dialogs/all_q.txt.flat.filter
```
3.run the chatbot based on the template
```sh
python bot3.py dialogs/all 10
```
bot3.py is similar to bot2.py, except that it is based on the template dialogs













