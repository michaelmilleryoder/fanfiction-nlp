import os
import json
import sys
import pdb
from collections import Counter

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

def main():
    # base_dir = "/projects/presidio_analysis/Patient_Doctor_Conversations/COREF_RESOLUTION/fanfiction_coref"

    fic_in_file = sys.argv[1]
    fic_out_dirpath = sys.argv[2]
    # fic_in_file = "./data/litbank/dev.preds.384.spb_lit_tosh.jsonlines"
    # fic_out_dirpath = "./data/litbank/output_spb_lit/"


    data = []

    with open(fic_in_file, "r") as f:
        for l in f.readlines():
            data.append(json.loads(l.strip()))

    for d in data:
        doc_key = d['doc_key'][:-2]
        #print(doc_key)

        clusters = []

        #print(d['predicted_clusters'][0][-1])
        for c, clus in enumerate(d['predicted_clusters']):
            cluster = {}
            cluster['mentions'] = []
            names = []
            # Change output from subtoken indices to full token indices
            for e, ele in enumerate(clus):
                tok_beg = d['subtoken_map'][ele[0]]
                tok_end = d['subtoken_map'][ele[1]] + 1
                phrase = ' '.join(d['tokens'][tok_beg:tok_end])
                cluster['mentions'].append({
                    'position': (tok_beg, tok_end),
                    'text': phrase})
                names.append(phrase)
            # Assign cluster canonical character name
            #cluster['name'] = canonical_character_name(Counter(names))
            clusters.append(cluster)
        
        #print(d['predicted_clusters'][0][-1])
        #for c, clus in enumerate(d['clusters']):
        #   for e, ele in enumerate(clus):
        #       ele[0] = d['subtoken_map'][ele[0]]
        #       ele[1] = d['subtoken_map'][ele[1]] + 1
        
        output = {
            #"document": " ".join(d['tokens']),
            "doc_tokens": d['tokens'],
            #"subtoken_map": d['subtoken_map'],
            #"tokenized_doc": d['sentences'], 
            #"clusters": d['predicted_clusters'],
            "clusters": clusters,
            #"gold_clusters": d['clusters']
        }

        with open(os.path.join(fic_out_dirpath, 
                doc_key + ".json"), "w") as f:
            json.dump(output, f)

        #print("Saving done!")

if __name__ == '__main__':
    main()
