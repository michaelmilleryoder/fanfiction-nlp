import sys
import json
import os
from collections import Counter
from os import listdir
from os.path import isfile, join
import pdb
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
stops = stopwords.words('english')
from nltk import Tree

# import benepar
# benepar.download('benepar_en3')

import benepar, spacy
#nlp_spacy = spacy.load('en_core_web_md')
nlp_spacy = spacy.load('en')
if spacy.__version__.startswith('2'):
    nlp_spacy.add_pipe(benepar.BeneparComponent("benepar_en3"))
else:
    nlp_spacy.add_pipe("benepar", config={"model": "benepar_en3"})
    
import inflect
p = inflect.engine()

DEBUG = False
DEBUG_2 = True
MEN_TO_REP = True
prev_quote_len = 5


def canonical_character_name(names):
    """ Returns a chosen canonical character name.
        This is simply the most frequent capitalized variant
        that is not a stopword.
        Args:
            names: a Counter of name variants
    """

    if len(names) == 1:
        return list(names.keys())[0]

    # Remove stopwords
    # Choose most frequent name that has a capital letter
    processed_names = Counter()
    stops = ['he', 'him', 'his', 'himself',
             'she', 'her', 'hers', 'herself',
             'they', 'them', 'their', 'theirs',
             'i', 'me', 'my', 'mine',
             'we', 'us', 'our', 'ours',
             'you', 'your', 'yours', 'yourself',
            'mr.', 'mr', 'ms', 'ms.', 'miss', 'miss.', 'mrs', 'mrs.',
            'sir',
            ]
    for name, count in names.items():
        if name.lower() not in stops:
            processed_names[name] = count
    if len(processed_names) == 0:
        processed_names = names

    capitalized = Counter({
            name: count for name, count in processed_names.items() \
            if any(letter.isupper() for letter in name)})
    if len(capitalized) == 0:
        capitalized = processed_names

    return capitalized.most_common(1)[0][0]


def remove_men(mrange, d, remove_pattern_i, remove_pattern_you, speaker, representative):
    total_removal = 0
    removed = [[],[]]
    for i in range(5):
        for c, clus in enumerate(d['clusters']):
            for m, men in enumerate(clus):
                if (men[0] >= mrange[0] and men[1] <= mrange[1]) and " ".join(d['doc_tokens'][men[0]: men[1]]).lower() in remove_pattern_i:
                    if not any([(x in representative[c]) for x in speaker.split()]):
                        removed[0].append((men, c))
                        del d['clusters'][c][m]
                        total_removal += 1

                elif (men[0] >= mrange[0] and men[1] <= mrange[1]) and " ".join(d['doc_tokens'][men[0]: men[1]]).lower() in remove_pattern_you:
                    removed[1].append((men, c))
                    del d['clusters'][c][m]
                    total_removal += 1

    return removed, total_removal

def is_camel_case(s):
    if s != s.lower() and s != s.upper() and sum(i.isupper() for i in s[:]) >= 1:
        return True
    return False

def preproc_cluster_rep(d, gold = False):
    reps = []
    reps_all = []
    clusters = d['clusters']

    for c, clus in enumerate(clusters):
        occs = {}
        #rep = " ".join(d['doc_tokens'][clus[0][0]: clus[0][1]])
        rep = " ".join(d['doc_tokens'][
                    clus['mentions'][0]['position'][0]: \
                    clus['mentions'][0]['position'][1]])
        rep_all = []
        for m, men in enumerate(clus['mentions']):
            str_men = " ".join(d['doc_tokens'][
                            men['position'][0]: men['position'][1]])

            if is_camel_case(str_men) and 'PRP' not in nltk.pos_tag([str_men])[0][1] and str_men.lower() not in stops: 
                if len(str_men.split()) <= 10:
                    if str_men not in occs:
                        occs[str_men] = 0

                    occs[str_men] += 1
                for s in str_men.split():

                    if 'PRP' not in nltk.pos_tag([s])[0][1] and s.lower() not in stops:
                        if s not in occs:
                            occs[s] = 0
                        occs[s] += 1

        if occs:
            more_than_3 = False
            kv_ulta = []
            for k,v in occs.items():
                if len(k) > 3:
                    more_than_3 = True
                    break

            for k,v in occs.items():
                if more_than_3:
                    if len(k) > 3:
                        kv_ulta.append((v,k))
                else:
                    kv_ulta.append((v,k))

            rep_all = sorted(kv_ulta, key = lambda x: (x[0],len(x[1])))
            rep = sorted(kv_ulta, key = lambda x: (x[0],len(x[1])))[-1][1]

        reps.append(rep)
        reps_all.append(rep_all)

    return reps, reps_all

# Reference: https://stackoverflow.com/questions/32654704/finding-head-of-a-noun-phrase-in-nltk-and-stanford-parse-according-to-the-rules

def find_noun_phrases(tree):
    return [subtree for subtree in tree.subtrees(lambda t: t.label()=='NP')]

def find_head_of_np(np):
    noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']
    top_level_trees = [np[i] for i in range(len(np)) if type(np[i]) is Tree]
    ## search for a top-level noun
    top_level_nouns = [t for t in top_level_trees if t.label() in noun_tags]
    if len(top_level_nouns) > 0:
        ## if you find some, pick the rightmost one, just 'cause
        return top_level_nouns[-1][0]
    else:
        ## search for a top-level np
        top_level_nps = [t for t in top_level_trees if t.label()=='NP']
        if len(top_level_nps) > 0:
            ## if you find some, pick the head of the rightmost one, just 'cause
            return find_head_of_np(top_level_nps[-1])
        else:
            ## search for any noun
            nouns = [p[0] for p in np.pos() if p[1] in noun_tags]
            if len(nouns) > 0:
                ## if you find some, pick the rightmost one, just 'cause
                return nouns[-1]
            else:
                ## return the rightmost word, just 'cause
                return np.leaves()[-1]

def is_head_a_person_wordnet(name):

    # Reference: https://github.com/nikitakit/self-attentive-parser

    doc = nlp_spacy(name)
    sent = list(doc.sents)[0]
#     print(sent._.parse_string)

    from nltk import Tree

    tree = Tree.fromstring(sent._.parse_string)
    for np in find_noun_phrases(tree):
#         print("noun phrase:")
#         print(" ".join(np.leaves()))
        if " ".join(np.leaves()).lower() == name:
            head = find_head_of_np(np)
#             print("head:")
#             print(head)
            name = head
            break

#     print(name)

    # Reference: https://subscription.packtpub.com/book/application_development/9781782167853/1/ch01lvl1sec14/looking-up-synsets-for-a-word-in-wordnet

    syns = wordnet.synsets(name)
    if len(syns) > 0:
        syn = syns[0]
    else:
        return False
#     print(syn.hypernym_paths()[0])
    return len([s.name() for s in syn.hypernym_paths()[0] if "person" in s.name()]) > 0

def post_process(data):
    men_to_pred = {tuple(m['position']): c for c, clus in enumerate(data['clusters']) for m in clus['mentions']}
    #mentions = sorted([tuple(m) for c, clus in enumerate(data['gold_clusters']) for m in clus])

    PRPs = ["it", "this", "that", "they", "them", "we", "these", "those", "our", "ours", "their", "theirs", "there", "its", "here"]

    plurals = ["they", "them", "we", "these", "those", "our", "their", 'people', 'parents']

    remove_PRPs = ["you", "me", "he", "she", "my", "mine", "your", "her", "his", "female", "male"]

    removable_mens = []
    out = {'document': data['document'],
            'clusters': []}

    # Remove any PRP mentions
    for i, clus in enumerate(data['clusters']):
        cluster = {'mentions': []}
        for j, men in enumerate(clus['mentions']):
            if not men['text'] in PRPs:
                cluster['mentions'].append(men)
        if len(cluster['mentions']) > 0:
            out['clusters'].append(cluster)

    # old code
    #for men in men_to_pred:
    #    mention = " ".join(data['doc_tokens'][men[0]: men[1]])
    #    if mention.lower() in PRPs:
    #        c = men_to_pred[men]
    #        if list(men) in data['clusters'][c]['mentions']:
    #            data['clusters'][c].remove(list(men))
    #        for m in data['clusters'][c]:
    #            if list(m) in data['clusters'][c]['mentions']:
    #                data['clusters'][c].remove(list(m))

    #########################################################
    #### Remove clusters with lower-case representatives ####
    #########################################################
    #remove_clusts = []
    #for c, clus in enumerate(data['clusters']):       
    #    if len(clus) == 0:
    #        remove_clusts.append(clus)
    #for c in remove_clusts:
    #    data['clusters'].remove(c)
    
    clusters = []
    for clus in out['clusters']:
        mentions = [m['text'] for m in clus['mentions']]
        name = canonical_character_name(Counter(mentions))
        if (name.lower() == name) and (name.lower() not in remove_PRPs):
            if (p.singular_noun(name) is not False and name != p.singular_noun(name)):
                continue
            elif (not is_head_a_person_wordnet(name)):
                continue
        clus['name'] = name
        clusters.append(clus)
    out['clusters'] = clusters

    #for clus in out['clusters']:
    #    mentions = [m['text'] for m in clus['mentions']]
    #    clus['name'] = canonical_character_name(Counter(mentions))
    #    if (name.lower() == name) and (name.lower() not in remove_PRPs):
    #        if (p.singular_noun(name) is not False and name != p.singular_noun(name)):
    #            out['clusters'].remove(clus)
    #            continue
    #        elif (not is_head_a_person_wordnet(name)):
    #            out['clusters'].remove(clus)
    #            continue

    #cluster_reps = preproc_cluster_rep(data)[0]
    #for c, rep in enumerate(cluster_reps):
    #    if (rep.lower() == rep) and (rep.lower() not in remove_PRPs):
    #        if (p.singular_noun(rep) is not False and rep != p.singular_noun(rep)):
    #            if DEBUG:
    #                print(rep, p.singular_noun(rep))
    #            data['clusters'][c] = []
    #        if (not is_head_a_person_wordnet(rep)):
    #            if DEBUG:
    #                print(rep)
    #            data['clusters'][c] = []

    #######################################################

    #remove_clusts = []

    #for c, clus in enumerate(data['clusters']):       
    #    if len(clus) == 0:
    #        remove_clusts.append(clus)

    #for c in remove_clusts:
    #    data['clusters'].remove(c)

    #men_to_pred = {tuple(m): clus for c, clus in enumerate(data['clusters']) for m in clus}

    #cluster_reps = preproc_cluster_rep(data)[0]
    
    return out


model_out_path = sys.argv[1]
model_out_file = model_out_path.split("/")[-1].split(".")[0]
post_prod_dir = sys.argv[2]

#print(model_out_path, model_out_file, post_prod_dir)

if not os.path.exists(post_prod_dir):
    os.mkdir(post_prod_dir)

if os.path.exists(model_out_path):
    with open(model_out_path, "r") as f:
        data = json.load(f)
        
    #cluster_reps = preproc_cluster_rep(data)[0]
        
    #print(cluster_reps, '\n')

    data = post_process(data)

    with open(os.path.join(post_prod_dir, model_out_file + ".json"), 'w') as f:
        json.dump(data, f)
        
    #cluster_reps = preproc_cluster_rep(data)[0]
        
    #print(cluster_reps, '\n')
