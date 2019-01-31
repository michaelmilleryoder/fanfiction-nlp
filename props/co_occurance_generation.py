import pandas as pd
import glob
import time
from collections import Counter
from sklearn.feature_extraction.text import TfidfTransformer
import spacy
import sys
import os.path
reload(sys)
sys.setdefaultencoding('utf8')


start_time = time.time()
if len(sys.argv) < 2:
    print "Data path missing"
    exit(0)

nlp = spacy.load('en_core_web_sm')
print "Model loaded"
path = sys.argv[1]
path = os.path.abspath(os.path.join(os.pardir, path))
print path
allFiles = glob.glob(path + "/*.out")
frame = pd.DataFrame()
text = []
count = 0
if len(allFiles) < 1:
    print "No files found at the location provided"
    exit(0)

for file in allFiles:
    df = pd.read_csv(file, index_col=None, header=0)

for row in df['paragraph']:
    # print row
    text.append(row)

character_dict = {}
text = ''.join(text)


processed_text = []
for word in text.split(" "):
    if word.startswith("($_"):
        character_dict[word[word.find('_') + 1: word.find(')')].lower()] = word
        processed_text.pop()
        word = word[word.find('_') + 1: word.find(')')]

    processed_text.append(word)

processed_text = ' '.join(processed_text)


doc = nlp(unicode(processed_text))
data_list = []
for token in doc:
    if token.is_stop is False:
        if len(token.ent_type_) > 0:
            data_list.append({'lemma': token.lemma_, 'pos': token.pos_, 'tag': token.tag_, 'ner': token.ent_type_})
        else:
            data_list.append({'lemma': token.lemma_, 'pos': token.pos_, 'tag': token.tag_, 'ner': 'O'})
df = pd.DataFrame(data_list)

# Filtering out POS tags
pos_tags = ['POS', 'JJ', 'WP', 'NN', 'FW', 'NNS', 'NNP', 'NNPS', 'JJR']

print "Subsetting the data"
dfsub = df[["lemma", "tag", "ner"]].loc[df["tag"].isin(pos_tags)]
tokens = dfsub["lemma"].tolist()
dfsub = dfsub.reset_index()
ngram = 4
chars = {}

print "Starting counter loop"
for index, row in dfsub.iterrows():
    if row["ner"] == "PERSON" and index + ngram < len(tokens) - 1:
        if row["lemma"] in chars:
            for i in range(1, ngram + 1):
                if len(str(tokens[index - i])) > 2:
                    chars[row["lemma"]].update({tokens[index - i]: 1})
                if len(str(tokens[index + i])) > 2:
                    chars[row["lemma"]].update({tokens[index + i]: 1})
        else:
            chars[row["lemma"]] = Counter()
            for i in range(1, ngram + 1):
                if len(str(tokens[index - i])) > 2:
                    chars[row["lemma"]].update({tokens[index - i]: 1})
                if len(str(tokens[index + i])) > 2:
                    chars[row["lemma"]].update({tokens[index + i]: 1})
print "Ending counter loop"

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

resfile = open("cooccurence.txt", "w+")
for key in new_char_dict:
    line = ""
    if str(key) in character_dict:
        line = character_dict[str(key)] + ": {"
    else:
        line = str(key) + ": {"
    for key1, value in sorted(new_char_dict[key].iteritems(), key=lambda (k, v): (v, k), reverse=True):
        if(value != 0):
            line += str(key1) + ":" + str(value) + "  "
    line += "}" + "\n\n\n"
    resfile.write(line)
resfile.close()
