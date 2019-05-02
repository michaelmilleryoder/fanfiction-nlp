import csv
import glob
from ship import *
import re
import string
from nltk.corpus import stopwords
import random
import sys


stop_words = set(stopwords.words('english'))

pipe_out_dir = sys.argv[1]
stories_dir = sys.argv[2]
conv_dir = sys.argv[3]

mapping_dir = conv_dir + "mapping"
mapping_files = glob.glob(mapping_dir + "/*.csv")
meta_dict = mapping_dict(stories_dir, pipe_out_dir)

file_mapping = {}
for file in mapping_files:
    mapping = {}
    with open(file) as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            mapping[row['Metadata character']] = row['Coref character']
        file_mapping[file.split("/")[-1].split(".")[0]] = mapping


conversation_dir = conv_dir + "conversation/"
conversation_files = glob.glob(conversation_dir + "/*.csv")
feats = []
labels = []
true_count = 0
for file in conversation_files:
    conv = {}
    filename = file.split("/")[-1].split(".")[0]
    ships = [tuple(x.split("/")) for x in meta_dict[file.split("/")[-1].split(".")[0].split("_")[0]]]
    with open(file) as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            conv[row['Conversation_chars']] = row['Conversation_text']

    new_ships = set()
    for ship in ships:
        try:
            temp = [file_mapping[filename][re.sub('[' + string.punctuation + ']', '', x).strip()] for x in ship]
            new_ships.add(str(tuple(sorted(temp))))
        except:
            continue

    for key in conv:
        if key in new_ships:
            talk = " ".join([re.sub('[' + string.punctuation + ']', '', conv[key]).strip()])
            talk = " ".join([word for word in talk.split()])
            feats.append(talk)
            labels.append(1)
            true_count += 1
        else:
            talk = " ".join([re.sub('[' + string.punctuation + ']', '', conv[key]).strip()])
            talk = " ".join([word for word in talk.split()])
            feats.append(talk)
            labels.append(0)

new_feats = []
new_labels = []

for i in range(len(feats)):
    if labels[i] == 1:
        new_feats.append(feats[i])
        new_labels.append(labels[i])
    else:
        if true_count >= 0:
            new_feats.append(feats[i])
            new_labels.append(labels[i])
            true_count -= 1
        else:
            continue


c = list(zip(new_feats, new_labels))

random.shuffle(c)

feats, labels = zip(*c)

train_split = int(0.7 * len(feats))

with open("train.tsv", 'w') as myfile:
    csv_writer = csv.writer(myfile, delimiter='\t')
    for i in range(0, train_split):
        csv_writer.writerow([i + 1, labels[i], 'a', feats[i]])

with open("dev.tsv", 'w') as myfile:
    csv_writer = csv.writer(myfile, delimiter='\t')
    for i in range(train_split, len(feats)):
        csv_writer.writerow([i + 1, labels[i], 'a', feats[i]])

with open("test.tsv", 'w') as myfile:
    csv_writer = csv.writer(myfile, delimiter='\t')
    csv_writer.writerow(['id', 'sentence'])
    for i in range(train_split, len(feats)):
        csv_writer.writerow([i + 1, feats[i]])
