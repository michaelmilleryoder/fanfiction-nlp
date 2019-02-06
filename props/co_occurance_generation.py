import pandas as pd
import glob
import time
from collections import Counter, OrderedDict
from sklearn.feature_extraction.text import TfidfTransformer
import spacy
import sys
import os.path
import json
reload(sys)
sys.setdefaultencoding('utf8')


start_time = time.time()
if len(sys.argv) < 2:
    print "Data path missing"
    exit(0)

print "Loading NLP Model"
nlp = spacy.load('en_core_web_sm')
print "Model loaded"
path = sys.argv[1]
script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

rel_path = sys.argv[1]
path = os.path.join(script_dir, rel_path)
print "Reading file from " + path

allFiles = glob.glob(path + "/*.csv")
frame = pd.DataFrame()
text = []
count = 0
if len(allFiles) < 1:
    print "No files found at" + path
    exit(0)
for file in allFiles:
    df = pd.read_csv(file, index_col=None, header=0)
    for row in df.iloc[:, -1]:
        text.append(row)

character_dict = {}
text = ''.join(text)

# Read all files for characters

rel_path = sys.argv[3]
char_path = os.path.join(script_dir, rel_path)
print "Reading characters from " + path
charFiles = glob.glob(char_path + "/*")

if len(charFiles) < 1:
    print "No character files found at" + char_path
    exit(0)

# Store the characters in a dict with normal names as keys
for file in charFiles:
    chars = open(file).readlines()
    for char in chars:
        character_dict[char[char.find('_') + 1: char.find(')')].lower()] = char.strip('\n')


processed_text = []
for word in text.split(" "):
    if word.startswith("($_"):
        # character_dict[word[word.find('_') + 1: word.find(')')].lower()] = word
        processed_text.pop()
        word = word[word.find('_') + 1: word.find(')')]

    processed_text.append(word)
processed_text = ' '.join(processed_text)

doc = nlp(unicode(processed_text))

data_list = []
for token in doc:
    # print token, "ss"
    if token.is_stop is False:
        data_list.append({'text': token.text, 'pos': token.pos_, 'tag': token.tag_, 'lemma': token.lemma_})

df = pd.DataFrame(data_list)

chars = {}
index = 0
ngram = 4
for row in data_list:
    if row['text'] in character_dict:
        if row['text'] in chars:
            for i in range(1, ngram + 1):
                if data_list[index + i]['pos'] == 'ADJ':
                    chars[row["text"]].update({data_list[index + i]['text']: 1})
                if data_list[index - i]['pos'] == 'ADJ':
                    chars[row["text"]].update({data_list[index - i]['text']: 1})
        else:
            chars[row["text"]] = Counter()
            for i in range(1, ngram + 1):
                if data_list[index + i]['pos'] == 'ADJ':
                    chars[row["text"]].update({data_list[index + i]['text']: 1})
                if data_list[index - i]['pos'] == 'ADJ':
                    chars[row["text"]].update({data_list[index - i]['text']: 1})
    index += 1


print "Creating co-occurence"
dfnew = pd.DataFrame.from_dict(chars, orient='index').reset_index().fillna(0)
col_names = list(dfnew.columns.values)
col_names = col_names[1:]
char_list = []
# Converting term counts to TFIDF
for char in dfnew["index"]:
    char_list.append(char)
dfnew = dfnew.drop(["index"], axis=1)

tfidf = TfidfTransformer(norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=False)
mat = tfidf.fit_transform(dfnew).toarray()
dffinal = pd.DataFrame(mat)
dffinal.index = char_list
dffinal.columns = col_names

new_char_dict = {}
char_dict = dffinal.to_dict('index')
for key in char_dict:
    new_char_dict[key] = char_dict[key]

sorted_dict = OrderedDict()
for key in new_char_dict:
    counter_dict = OrderedDict()
    for key1, value in sorted(new_char_dict[key].iteritems(), key=lambda (k, v): (v, k), reverse=True):
        if (value != 0):
            counter_dict[key1] = value
    sorted_dict[key] = counter_dict

rel_path = sys.argv[2]
output_path = os.path.join(script_dir, rel_path)

with open('result.json', 'w') as fp:
    json.dump(sorted_dict, fp)
