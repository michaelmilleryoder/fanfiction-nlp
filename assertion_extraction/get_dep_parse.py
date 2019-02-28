import spacy
import sys
from os import listdir
from os.path import isfile,join
import json

nlp = spacy.load('en')
input_dir = sys.argv[1]
op_dir = sys.argv[2]

agents = ['agent','nsubj','nsubjpass']
patients = ['dobj','oprd','pobj']
modifiers = ['acl','advcl','advmod','amod','appos','compound','meta','neg','nounmod','npmod','nummod','poss','prep','quantmod','relcl']

def is_agent(token):
    if token.dep_ in agents:
        return True
    return False

def is_patient(token):
    if token.dep_ in patients:
        return True
    return False

def is_modifier(token):
    if token.dep_ in modifiers:
        return True
    return False

files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
for f in files:
    d = open(input_dir + '/' + f,'r')
    
    op_f = f.split('.json')[0] + '.deps'
    op_file = open(op_dir + '/' + op_f,'w+')
    parsed_json = json.loads(d.read())
    for char in parsed_json:
        op_str = char + "\t:\t"
        segments = parsed_json[char]
        for segment in segments:
            dep_parse = nlp(segment)
            for token in dep_parse:
                #print token.dep_
                if is_agent(token):
                    op_str += "a:" + token.text + " "
                elif is_patient(token):
                    op_str += "p:" + token.text + " "
                elif is_modifier(token):
                    op_str += "m:" + token.text + " "
        op_str += "\n"
                
        op_file.write(op_str)    
