"""
    @author: Shikhar Vashishth, modified by Michael Miller Yoder
"""


import sys; sys.path.append('./common')
from helper import *
from queue_client import *
from collections import ChainMap
from corenlp import CoreNLPClient

#import scispacy, spacy
#from scispacy.abbreviation import AbbreviationDetector
#from pymongo.errors import BulkWriteError
import pdb
import traceback

# Global variables 

clients = []


######################### Run CoreNLP on Entire Wikipedia


def run_corenlp(text, corenlp_ips):
    text_ = text.encode('utf-8')

    try:
        params = {
            'properties': '{"annotators":"tokenize,ssplit,pos,lemma,ner,parse,coref", "tokenize.whitespace": "true"}',
            #'outputFormat': 'json'
            'outputFormat': 'serialized',
            "serializer": "edu.stanford.nlp.pipeline.ProtobufAnnotationSerializer"
        }

        url = random.choice(corenlp_ips)
        res = requests.post(url, params=params, data=text_, headers={'Content-type': 'text/plain'})

        if res.status_code == 200:
            data = res.json(strict=False)               
            return data
        else:
            print("CoreNLP Error, status code:{}".format(res.status_code))
            return None

    except Exception as e:
        print('Server {} not working'.format(url))
        return run_corenlp(text, corenlp_ips)


def run_corenlp_client(text, output_dirpath, fname):
    coref_text_outpath = os.path.join(output_dirpath, 'char_coref_stories', f'{fname}.coref.txt')
    coref_chars_outpath = os.path.join(output_dirpath, 'char_coref_chars', f'{fname}.chars')

    client_num = random.choice(range(len(clients)))
    client = clients[client_num]

    #test = 'This is a test sentence Mr. Weirdo . He went to the store . Then he went all the way to the moon .'
    #text = test

    #print(f'Text character length: {len(text)}')
    print(f'Annotating {fname}...')
    ann = client.annotate(text)
    print(f'\tdone.') 
    print(f'Processing annotations...')
    annotated_text, chars = process_text(ann, text)
    print('\tdone.')

    # Write out annotated story text
    with open(coref_text_outpath, 'w') as f:
        f.write(annotated_text)

    # Write out character list
    with open(coref_chars_outpath, 'w') as f:
        for c in chars:
            f.write(f'{c}\n')


def extract_characters(annotations):
    """ Returns id2char dictionary,
        with similar character names merged """
    
    id2char = {}
    ids = []

    # Build id2char
    for chain in annotations.corefChain:
        if chain.character != '':
            id2char[chain.chainID] = chain.character
            ids.append(chain.chainID)

    # Merging character names
    for i in range(len(ids)):
        for j in range(len(ids)):
            id1 = ids[i]
            id2 = ids[j]
            char1, char2 = id2char[id1], id2char[id2]
    
            if char2 in char1:
                id2char[id2] = char1
            elif char1 in char2:
                id2char[id1] = char2
            elif char1.lower() == char2.lower():
                id2char[id2] = char1

    return id2char


def process_sentence(sent, id2char):
    """ Adds tags around coref mentions for a sentence """

    replaced_sent = ''
    chars = set()

    # No coref mentions; just take text and replace . # with paragraph break
    if len(sent.mentionsForCoref) == 0: 
        text = ' '.join([tok.word for tok in sent.token])
        #if 'Goddamn' in text:
        #    pdb.set_trace()
        if text == '# .':
            replaced_sent = '\n'
        elif text.endswith(' # .'):
            replaced_sent = text[0:-4] + '\n'
        else:
            replaced_sent = text + ' '

    else:
        replaced_sent, chars = add_coref_tags(sent, id2char)

    return replaced_sent, chars


def build_replacements(sent, id2char):
    """ Returns data structure with locations of coref mentions and 
        the character each mention refers to 
    """

    words = [] # new sentence tokens with modifications, joined to a string at end
    replacements = []

    for mention in sent.mentionsForCoref:
        char_id = mention.corefClusterID
        char = ''
        if len(words) == 0:
            for word in mention.sentenceWords:
                words.append(sent.token[word.tokenIndex].word)

        if char_id in id2char:
            char = id2char[char_id]
            processed_char = process_char(char)
            
            if char != '': 
                replacements.append((
                        (mention.startIndex, mention.endIndex),
                        processed_char
                        ))
        
    replacements.sort(key = lambda x: x[0][0])
    
    return replacements, words


def replace_tokens(replacements, replaced_words):
    """ Replace untagged tokens with tokens with coref tags """

    chars = set()

    for replacement in replacements:
        begin_tag = f'<character name="{replacement[1]}">' 
        end_tag = '</character>'
        tagged_word = ''

        # Add tags
        if replacement[0][0] + 1 == replacement[0][1]: # 1-word mention
            tagged_word = begin_tag + replaced_words[replacement[0][0]] + end_tag
            replaced_words[replacement[0][0]] = tagged_word

        else: # multi-word mention
            # begin-tag first word
            tagged_word = begin_tag + replaced_words[replacement[0][0]]
            replaced_words[replacement[0][0]] = tagged_word

            # end-tag after last word
            if replaced_words[replacement[0][1] - 1] == "'s":
                tagged_word = replaced_words[replacement[0][1] - 2] + end_tag
                replaced_words[replacement[0][1] - 2] = tagged_word
            else:
                tagged_word = replaced_words[replacement[0][1] - 1] + end_tag
                replaced_words[replacement[0][1] - 1] = tagged_word

        chars.add(replacement[1])

    return replaced_words, chars


def add_coref_tags(sent, id2char):
    """ Adds tags around coref mentions for a sentence """

    # Build up list of where will add tags (replacements)
    replacements, replaced_words = build_replacements(sent, id2char)

    # Do the replacing
    replaced_words, chars = replace_tokens(replacements, replaced_words)
    replaced_sentence = ' '.join(replaced_words) + ' '
    #if 'Goddamn' in replaced_sentence:
    #    pdb.set_trace()

    # Replace # . to paragraph breaks
    replaced_sentence = replaced_sentence.replace('# .', '\n')

    return replaced_sentence, chars


def process_text(annotations, text):
    """ Take CoreNLP-processed annotations and add coreference tags to the text """

    out_text = '' # outputBuilder
    id2char = extract_characters(annotations)
    chars = set()

    # Add the character tags to the text and process the paragraph delimiter "# ."
    for sent in annotations.sentence:
        replaced_sentence, sent_chars =  process_sentence(sent, id2char)
        out_text += replaced_sentence
        chars |= sent_chars

    return out_text, chars


def process_char(char):
    """ Process a character name """

    processed_char = char

    # Punctation, 's
    processed_char = processed_char.replace('’s', '')
    processed_char = processed_char.replace("'s", '')
    processed_char = re.sub(r'[,\.\!\?“”’…–]', '', processed_char)

    # Regular spaces, horizontal non-breaking spaces
    processed_char = processed_char.replace(' ', '_')
    processed_char = re.sub(r'[^\S\n]', '', processed_char, flags=re.UNICODE)

    # Underscores (substituting them and handling them)
    processed_char = re.sub(r'_+', '_', processed_char)
    processed_char = re.sub(r'^_', '', processed_char)
    processed_char = re.sub(r'_$', '', processed_char)

    return processed_char


def process_data(pid, args):
    q = QueueClient('http://{}:{}/'.format(args.ip, args.port))

    while True:
        if args.debug:
            #file_list = [
            #    '/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/2416073.csv',
            #    '/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/4545384.csv',
            #    '/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/7030585.csv',
            #    '/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/15730266.csv',
            #    '/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/3917902.csv',
            #]
            file_list = q.dequeServer()
        else:
            file_list = q.dequeServer()

        if file_list == -1: # Stops when no more in file list
            print('[{}] All Jobs Over!!!!'.format(pid))
            time.sleep(60)
            continue

        count = 0
        for fname in file_list:
            name  = fname.split('/')[-1]
            fic_id_string = name.split('.')[0]
            #fw    = open(f'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics_proc/{name}', 'w')

            # Check if already processed
            output_dirpath = '/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/output/'
            char_output_fpath = os.path.join(output_dirpath, f'char_coref_chars/{name}.chars')
            if os.path.exists(char_output_fpath):
                continue

            # Build text to send to CoreNLP
            with open(fname) as f:
                f.readline()

                text_aggregate = ''
                for data in csv.reader(f):
                    text = data[-1]
                    text_aggregate += ' # . '.join(text.split('\n'))
                    text_aggregate += " # . "
                
                #res = run_corenlp(text_aggregate, ip_list)
                run_corenlp_client(text_aggregate, output_dirpath, fic_id_string)

                count += 1
                if count % 10000 == 0:
                    print('Completed {} [{}] {}, {}'.format(pid, name, count, time.strftime("%d_%m_%Y") + '_' + time.strftime("%H:%M:%S")))

        else: # finished loop through file_list
            break


def start_corenlp_servers(n_servers):
    """ Initializes client objects """

    print('Launching CoreNLP servers...')
    for i in range(n_servers):
        client = CoreNLPClient(
            endpoint = f'http://localhost:{9000+i}',
            annotators = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'coref'],
            properties = {'tokenize.whitespace': 'true',
                          #'coref.algorithm': 'clustering'
                        },
            be_quiet = True,
            max_char_length = 1000000,
            memory = '16G',
            timeout = 1500000,
        )
        client.start()
        clients.append(client)
    print('\tdone.')


def stop_corenlp_servers(clients):
    """ Stops a list of initialized client objects """

    print('Stopping CoreNLP servers...')
    for client in clients:
        client.stop()
    print('done.')

    return clients


def run_linker_client(args):

    # Old method with ip lists
    #ip_list = ['http://127.0.0.1:{}'.format(args.start_port + i) for i in range(args.nums)]
    #ip_list = ['http://misty.lti.cs.cmu.edu:{}'.format(args.start_port + i) for i in range(args.nums)]

    # Initialize CoreNLP servers (through Python wrapper)
    start_corenlp_servers(args.nums)

    # for debugging, skip parallelization
    if args.debug:
        #process_data(1, args, ip_list)
        process_data(1, args, clients)
        #res_list  = Parallel(n_jobs = args.workers)(delayed(process_data)(i, args) for i in range(args.workers))
    else:
        res_list  = Parallel(n_jobs = args.workers, require='sharedmem')(delayed(process_data)(i, args) for i in range(args.workers))
        #res_list  = Parallel(n_jobs = args.workers)(delayed(process_data)(i) for i in range(args.workers))

    stop_corenlp_servers()


def run_linker_server(args):
    q = QueueClient('http://{}:{}/'.format(args.ip, args.port))

    if args.clear:    q.clear()
    if args.allclear: q.clear(); exit(0)
    if args.status:
        while True:
            size = q.getSize()
            print('{}, Queue size. {}'.format(time.strftime("%d_%m_%Y") + '_' + time.strftime("%H:%M:%S"), size))
            time.sleep(20)

    exclude_ids = set([])

    done_list = {}
    # for root, dirs, files in os.walk(f'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics_proc'):
    #   for file in files:  
    #       done_list[file] = 1

    file_list = []
    temp = []
    count = 0
    for root, dirs, files in os.walk('/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics'):
        for file in files:
            if '.csv' not in file: continue
            fname = os.path.join(root, file)
            name  = fname.split('/')[-1]

            if name not in done_list:
                temp.append(fname)

                if len(temp) > 500: 
                    q.enqueue(temp)
                    count += 1
                    temp = []
                    print("Inserting {}".format(count), end='\r')

    print('\nInserted {}, Total {} in queue. Complete'.format(count, q.getSize()))


def process_json(data):
    """ Extract character coreference assignments from CoreNLP output and
        embed with <tags> in the text
    """
    pass


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--step',      required=True)
    parser.add_argument('--workers',   default=30,  type=int)
    parser.add_argument('--ip',        default='misty.lti.cs.cmu.edu')
    parser.add_argument('--port',      default=1234, type=int)
    parser.add_argument('--nums',      default=16, type=int)
    parser.add_argument('--start_port',default=7090, type=int)
    parser.add_argument('--clear',     action='store_true')
    parser.add_argument('--status',    action='store_true')
    parser.add_argument('--allclear',  action='store_true')
    parser.add_argument('--check',     action='store_true')
    parser.add_argument('--debug',     action='store_true')
    args = parser.parse_args()

    if   args.step == 'server':     run_linker_server(args)
    elif args.step == 'client':     run_linker_client(args)


if __name__ == '__main__': main()
