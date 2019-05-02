import json
import csv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import glob
import nltk
from nltk.corpus import stopwords
from ship import mapping_dict
import Levenshtein
import re
import string
import sys
import os


stop_words = set(stopwords.words('english'))

sid = SentimentIntensityAnalyzer()

pipe_out_dir = sys.argv[1]
stories_dir = sys.argv[2]
out_dir = sys.argv[3]

# List of all output file in quote attribution
allQuoteFiles = glob.glob(pipe_out_dir + "quote_attribution" + "/*.quote.json")

mapping_directory = out_dir + "mapping/"
conv_directory = out_dir + "conversation/"

if not os.path.exists(mapping_directory):
    os.makedirs(mapping_directory)

if not os.path.exists(conv_directory):
    os.makedirs(conv_directory)

# Identify series of fics
series_dict = dict()
for file in sorted(allQuoteFiles):
    series_name = file.split("/")[-1].split(".")[0].split("_")[0]
    file_name = file.split("/")[-1].split(".")[0]
    # print(series_name, "    ", file_name)
    if series_name not in series_dict:
        series_dict[series_name] = list()
    series_dict[series_name].append(file)

meta_dict = mapping_dict(stories_dir, pipe_out_dir)

# Loop to append over series
for key1 in series_dict:
    print(key1)
    # Extract the relation dict for the series
    ships = [tuple(x.split("/")) for x in meta_dict[file.split("/")[-1].split(".")[0].split("_")[0]]]
    quote_data = []
    story_csv_list = []
    tokens = []
    character_dict = {}
    quote_dict = {}
    for file in series_dict[key1]:
        quote_file = file

        story_file = pipe_out_dir + "char_coref_stories/" + file.split("/")[-1].split(".")[0] + ".coref.csv"
        char_file = pipe_out_dir + "char_coref_chars/" + file.split("/")[-1].split(".")[0] + ".chars"
        story_text = pipe_out_dir + "char_coref_stories/" + file.split("/")[-1].split(".")[0] + ".coref.txt"
        possessive = set("his, her")
        third_person = set(["he", "she", "him", "her", "they"])

        # List of dicts from the quote json
        temp_quote_data = []
        with open(quote_file, 'r') as myfile:
            data = myfile.read()
        temp_quote_data.extend(json.loads(data))

        with open(story_file) as csvfile:
            story_csv_list = list(list(rec) for rec in csv.reader(csvfile, delimiter=','))
        story_csv_list.extend(story_csv_list[1:len(story_csv_list)])

        # Para ID : Paragraph dict
        para_dict = {}
        for row in story_csv_list[1:]:
            para_dict[int(row[2])] = row[3].strip()

        for row in temp_quote_data:
            try:
                updated_info = {}
                updated_info["quotes"] = row["quotes"]
                updated_info["speaker"] = row["speaker"]
                updated_info["paragraph"] = para_dict[int(row["paragraph"])].strip()
                quote_data.append(updated_info)
            except:
                continue

        with open(story_text, 'r') as text_file:
            data = text_file.read()
            tokens.extend([word for word in data.split()])

        chars = open(char_file).readlines()
        for char in chars:
            character_dict[char.strip('\n')] = char[char.find('_') + 1: char.find(')')]

    mapping = {}
    for ship in ships:
        for character in ship:
            score = 999
            for key in character_dict:
                if Levenshtein.distance(character, character_dict[key]) < score:
                    mapping[character] = key
                    score = Levenshtein.distance(character, character_dict[key])

    mapping_file_name = mapping_directory + key1 + ".csv"

    # Get mapping from meta data to character files
    with open(mapping_file_name, 'w') as myfile:
        csv_writer = csv.writer(myfile, delimiter=',')
        csv_writer.writerow(['Metadata character', 'Coref character'])
        for key in mapping:
            fline = re.sub('[' + string.punctuation + ']', '', key)
            csv_writer.writerow([fline.strip(), character_dict[mapping[key]]])

    # Create the conversations for 2 characters
    conv_file_name = conv_directory + key1 + ".csv"
    with open(conv_file_name, 'w') as myfile:
        csv_writer = csv.writer(myfile, delimiter=',')
        csv_writer.writerow(['Conversation_chars', 'Conversation_text'])
        for i in range(len(quote_data)):
            chars = set()
            chars.add(quote_data[i]["speaker"])
            chars.add(quote_data[max(i - 1, 0)]["speaker"])
            char_count = i
            while len(chars) < 2 and char_count < len(quote_data) - 1:
                chars.add(quote_data[min(char_count + 1, len(quote_data) - 1)]["speaker"])
                char_count += 1

            if tuple(sorted(list(chars))) not in quote_dict:
                quote_dict[tuple(sorted(list(chars)))] = list()
                quote_dict[tuple(sorted(list(chars)))].append(quote_data[i]["paragraph"])
        for key in quote_dict:
            csv_writer.writerow([key, ". ".join(quote_dict[key])])
