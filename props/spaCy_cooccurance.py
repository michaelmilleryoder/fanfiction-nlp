import pandas as pd
import glob
import time
from collections import Counter
from sklearn.feature_extraction.text import TfidfTransformer
import spacy
import sys
reload(sys)
sys.setdefaultencoding('utf8')


start_time = time.time()

# Filter out non english stories
nlp = spacy.load('en_core_web_sm')
lang_df = pd.read_csv("/usr2/scratch/fanfic/ao3_allmarvel_text/stories.csv")
lang_df = lang_df[lang_df["language"] == "English"]
eng_stories = set(lang_df["fic_id"])

# Reading and processing 10 stories at a time due to limitation on stringlen in spaCy
count = 0
path = '/usr2/scratch/fanfic/ao3_allmarvel_text/stories'
print "Reading files"
allFiles = glob.glob(path + "/*.csv")
frame = pd.DataFrame()
list1 = []
data_list = []
for k in range(0, 20):
    print "Creating dataframe"
    for file_ in allFiles[count:count + 10]:
        if (int(file_[48:len(file_) - 9]) in eng_stories):
            print "Reading file: ", file_[48:len(file_) - 9]
            df = pd.read_csv(file_, index_col=None, header=0)
            list1.append(df)
    frame = pd.concat(list1)

    text = []
    for row in frame['text']:
        text.append(row)
    text = ''.join(text)

    doc = nlp(unicode(text))

    for token in doc:
        if token.is_stop is False:
            if len(token.ent_type_) > 0:
                data_list.append({'lemma': token.lemma_, 'pos': token.pos_, 'tag': token.tag_, 'ner': token.ent_type_})
            else:
                data_list.append({'lemma': token.lemma_, 'pos': token.pos_, 'tag': token.tag_, 'ner': 'O'})
    count += 10

df = pd.DataFrame(data_list)

# Filtering out POS tags
pos_tags = ['POS', 'JJ', 'WP', 'NN', 'FW', 'NNS', 'NNP', 'NNPS', 'JJR', 'VB']

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
for char in dfnew["level_0"]:
    char_list.append(char)

dfnew = dfnew.drop(["level_0"], axis=1)

tfidf = TfidfTransformer(norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=False)
mat = tfidf.fit_transform(dfnew).toarray()
dffinal = pd.DataFrame(mat)
dffinal.index = char_list
dffinal.columns = col_names

new_char_dict = {}
char_dict = dffinal.to_dict('index')
for key in char_dict:
    new_char_dict[key] = char_dict[key]

resfile = open("marvel_ships_dict.txt", "w+")

for key in new_char_dict:
    line = ""
    line = str(key) + ": {"
    for key1, value in sorted(new_char_dict[key].iteritems(), key=lambda (k, v): (v, k), reverse=True):
        if(value != 0):
            line += str(key1) + ":" + str(value) + "  "
    line += "}" + "\n\n\n"
    resfile.write(line)
resfile.close()

elapsed = time.time() - start_time
print "total code elapsed time: ", elapsed
