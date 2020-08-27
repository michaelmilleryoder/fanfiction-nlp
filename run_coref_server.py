"""
    @author: Shikhar Vashishth, modified by Michael Miller Yoder
"""


import sys; sys.path.append('./common')
from helper import *
from queue_client import *
from collections import ChainMap
from corenlp import CoreNLPClient
<<<<<<< HEAD
=======
from corenlp_protobuf import Document, parseFromDelimitedString
from multiprocessing import Pool
>>>>>>> f247be7f951f3f2cec7be19a455cdf85caf45287

#import scispacy, spacy
#from scispacy.abbreviation import AbbreviationDetector
#from pymongo.errors import BulkWriteError
import pdb
import traceback
<<<<<<< HEAD
=======

# Global variables 

#clients = []

>>>>>>> f247be7f951f3f2cec7be19a455cdf85caf45287

######################### Run CoreNLP on Entire Wikipedia


def run_corenlp(text, corenlp_ips):
    """ Run CoreNLP through server/REST API"""

    text_ = text.encode('utf-8')

    try:
        params = {
            'properties': '{"annotators":"tokenize,ssplit,pos,lemma,ner,parse,coref", "tokenize.whitespace": "true"}',
<<<<<<< HEAD
            #'outputFormat': 'json'
=======
>>>>>>> f247be7f951f3f2cec7be19a455cdf85caf45287
            'outputFormat': 'serialized',
            "serializer": "edu.stanford.nlp.pipeline.ProtobufAnnotationSerializer"
        }

        url = random.choice(corenlp_ips)
        r = requests.post(url, params=params, data=text_, headers={'Content-type': 'text/plain'})
        print('\tdone.')

        if r.status_code == 200:
            # Decode protobuf object
            doc = Document()
            parseFromDelimitedString(doc, r.content)            

            print(f'Processing annotations...')
            annotated_text, chars = process_text(doc, text)
            print('\tdone.')
            
            return annotated_text, chars

        else:
            print("CoreNLP Error, status code:{}".format(r.status_code))
            return None, None

    except Exception as e:
        track = traceback.format_exc()
        print(track)
        #print('Server {} not working'.format(url))
        print('Server not working')
        return None, None


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


def process_data(pid):
    q = QueueClient('http://{}:{}/'.format(args.ip, args.port))

    while True:
        if args.debug:
            file_list = [
            # large files
            #'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/776979.csv',
            #'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/8100271.csv',
            #'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/12317418.csv',
            #'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/2051274.csv',
            #'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/308287.csv',
            #'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/8008267.csv',
                # normal size files
                #'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/2416073.csv',
            #    '/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/4545384.csv',
            #    '/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/7030585.csv',
            #    '/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/15730266.csv',
            #    '/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics/3917902.csv',
            ]
            file_list = q.dequeServer()
        else:
            file_list = q.dequeServer()

        if file_list == -1: # Stops when no more in file list
            print('[{}] All Jobs Over!!!!'.format(pid))
            #time.sleep(60)
            break

        count = 0
        for fname in file_list:
            name  = fname.split('/')[-1]
            fic_id_string = name.split('.')[0]

            # Build fpaths, Check if already processed
            stories_dirpath = os.path.join(args.output, 'char_coref_stories')
            chars_dirpath = os.path.join(args.output, 'char_coref_chars')
            if not os.path.exists(stories_dirpath):
                os.mkdir(stories_dirpath)
            if not os.path.exists(chars_dirpath):
                os.mkdir(chars_dirpath)
            coref_text_outpath = os.path.join(stories_dirpath, f'{fic_id_string}.coref.txt')
            coref_csv_outpath = os.path.join(stories_dirpath, f'{fic_id_string}.coref.csv')
            coref_chars_outpath = os.path.join(chars_dirpath, f'{fic_id_string}.chars')
            if os.path.exists(coref_chars_outpath):
                print(f'Skipping {fic_id_string}; already processed')
                continue

            # Build text to send to CoreNLP
            with open(fname) as f:
                f.readline()
                text_aggregate = ''
                for data in csv.reader(f):
                    text = data[-1]
                    text_aggregate += ' # . '.join(text.split('\n'))
                    text_aggregate += " # . "
                
                #print(f'\tFic character length: {len(text_aggregate)}')
                print(f'Annotating {fic_id_string}...')
                annotated_text, chars = run_corenlp(text_aggregate, ip_list)
                if annotated_text is None and chars is None:
                    print(f"Could not process {fic_id_string}")
                    continue
                count += 1
                if count % 10000 == 0:
                    print('Completed {} [{}] {}, {}'.format(pid, name, count, time.strftime("%d_%m_%Y") + '_' + time.strftime("%H:%M:%S")))

            print('Writing output...')
            # Write out annotated story text (coref txt)
            with open(coref_text_outpath, 'w') as f:
                f.write(annotated_text)

            # Write out annotated story text (coref csv)
            output_txt2csv(coref_csv_outpath, coref_text_outpath, fname)

            # Write out character list
            with open(coref_chars_outpath, 'w') as f:
                for c in chars:
                    f.write(f'{c}\n')
            print('\tdone.')

#        else: # finished loop through file_list
#            break


def run_linker_client(args):

    # IP method
    #ip_list = ['http://127.0.0.1:{}'.format(args.start_port + i) for i in range(args.nums)]

    # Python wrapper method initialize CoreNLP servers
    #start_corenlp_servers(args.nums)

    # back to main run_linker_client function
    # for debugging, skip parallelization
    try:
        if args.debug:
            process_data(1)
            #with Pool(args.workers) as pool:
            #    pool.map(process_data, range(args.workers))
        else:
            with Pool(args.workers) as pool:
                pool.map(process_data, range(args.workers))

    except Exception as e:
        track = traceback.format_exc()
        print(track)
        #stop_corenlp_servers()


<<<<<<< HEAD

def run_corenlp_client(text, corenlp_ips):
    text_ = text.encode('utf-8')

   # with CoreNLPClient(
   #     annotators = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'coref'], 
   #     properties = {'tokenize.whitespace': 'true',
   #                   'coref.algorithm': 'clustering'},
   #     be_quiet = False,
   #     memory = '5G',
   #     timeout = 1500000,
   # ) as client:
        #ann = client.annotate(text)
        #ann = client.annotate('This is a test sentence Mr. Weirdo. He went to the store. Then he went all the way to the moon.')

    client = CoreNLPClient(
        annotators = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'coref'], 
        properties = {'tokenize.whitespace': 'true',
                      'coref.algorithm': 'clustering'},
        #properties = {'tokenize.whitespace': 'true'},
        be_quiet = False,
        memory = '5G',
        timeout = 1500000,
    )   

    ann = client.annotate('This is a test sentence Mr. Weirdo. He went to the store. Then he went all the way to the moon.')
    client.stop()
    pdb.set_trace()


def run_linker_client():
    ip_list = ['http://127.0.0.1:{}'.format(args.start_port + i) for i in range(args.nums)]
    #ip_list = ['http://misty.lti.cs.cmu.edu:{}'.format(args.start_port + i) for i in range(args.nums)]

    def process_data(pid):
        q = QueueClient('http://{}:{}/'.format(args.ip, args.port))

        while True:
            file_list = q.dequeServer()

            if file_list == -1:
                print('[{}] All Jobs Over!!!!'.format(pid))
                time.sleep(60)
                continue

            count = 0
            for fname in file_list:
                name  = fname.split('/')[-1]
                fw    = open(f'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics_proc/{name}', 'w')

                # Build text to send to CoreNLP
                with open(fname) as f:
                    f.readline()

                    text_aggregate = ''
                    for data in csv.reader(f):
                        text = data[-1]
                        text_aggregate += ' # . '.join(text.split('\n'))
                        text_aggregate += " # . "
                    
                    #res = run_corenlp(text_aggregate, ip_list)
                    res = run_corenlp_client(text_aggregate, ip_list)
                    pdb.set_trace()
                    print("Got result")

                # Write CSV output
                with open(fname) as f:
                    for data in csv.reader(f):
                        fic_id, chapter_id, para_id, text, text_tokenized = data
                        doc = {
                            'fic_id'    : fic_id,
                            'chapter_id'    : chapter_id, 
                            'para_id'   : para_id, 
                            'text'      : text, 
                            'text_tokenized': text_tokenized,
                            'coref_text'   : process_json(res)
                        }

                        fw.write(json.dumps(doc) + '\n')
                        count += 1
                        if count % 10000 == 0:
                            print('Completed {} [{}] {}, {}'.format(pid, name, count, time.strftime("%d_%m_%Y") + '_' + time.strftime("%H:%M:%S")))

    #res_list  = Parallel(n_jobs = args.workers)(delayed(process_data)(i) for i in range(args.workers))

    # for debugging, skip parallelization
    process_data(1)
=======
def run_linker_server(args):
    q = QueueClient('http://{}:{}/'.format(args.ip, args.port))

    if args.clear:    q.clear()
    if args.allclear: q.clear(); exit(0)
    if args.status:
        size = q.getSize()
        print('{}, Queue size. {}'.format(time.strftime("%d_%m_%Y") + '_' + time.strftime("%H:%M:%S"), size))
        return

    exclude_ids = set([])

    done_list = {}
    # for root, dirs, files in os.walk(f'/data/fanfiction_ao3/allmarvel/complete_en_1k-50k/fics_proc'):
    #   for file in files:  
    #       done_list[file] = 1

    file_list = []
    temp = []
    count = 0
    step = 500 # max number of files to serve at once
    for root, dirs, files in os.walk(args.input):
        n_files = len([f for f in files if '.csv' in f])
        file_list_size = min(int(n_files/10)+1, step) # number of file names in each list to be served by the server
        for file in files:
            if '.csv' not in file: continue
            fname = os.path.join(root, file)
            name  = fname.split('/')[-1]
            temp.append(fname)
            if len(temp) >= file_list_size: 
                q.enqueue(temp)
                count += 1
                temp = []
                print("Inserting {}".format(count * file_list_size), end='\r')
        final_nfiles = 0
        if len(temp) > 0:
            final_nfiles = len(temp)
            q.enqueue(temp)
            temp = []
        print("Inserting {}".format(count * file_list_size + final_nfiles), end='\r')

    print('\nInserted {} files, Total {} file lists in queue. Complete'.format(count * file_list_size + final_nfiles, q.getSize()))


def output_txt2csv(coref_csv_outpath, coref_txt_outpath, fic_csv_fpath):
    """ Convert output files from text to original CSV format """
    with open(coref_txt_outpath) as coref_txt_outfile:
        lines = re.split(r'\n+| # . ', coref_txt_outfile.read())

    with open(fic_csv_fpath) as fic_csv_file:
        reader = csv.reader(fic_csv_file)
        header = next(reader)
        with open(coref_csv_outpath, 'w', encoding='utf8') as coref_csv_outfile:
            writer = csv.writer(coref_csv_outfile)
            writer.writerow(header)
            for row,text in zip(reader, lines):
                row[len(row)-1]= text
                writer.writerow(row)
>>>>>>> f247be7f951f3f2cec7be19a455cdf85caf45287


def run_linker_server():
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--step',      required=True)
    parser.add_argument('--input',     help='Path to directory with input files')
    parser.add_argument('--output',     help='Path to output directory')
    parser.add_argument('--workers',   default=30,  type=int)
    #parser.add_argument('--ip',        default='misty.lti.cs.cmu.edu')
    parser.add_argument('--ip',        default='localhost')
    parser.add_argument('--port',      default=1234, type=int)
    parser.add_argument('--nums',      default=16, type=int)
<<<<<<< HEAD
    parser.add_argument('--start_port',default=7090, type=int)
=======
    parser.add_argument('--start_port',default=8060, type=int)
>>>>>>> f247be7f951f3f2cec7be19a455cdf85caf45287
    parser.add_argument('--clear',     action='store_true')
    parser.add_argument('--status',    action='store_true')
    parser.add_argument('--allclear',  action='store_true')
    parser.add_argument('--check',     action='store_true')
    parser.add_argument('--debug',     action='store_true')
    args = parser.parse_args()

    ip_list = ['http://localhost:{}'.format(args.start_port + i) for i in range(args.nums)]

    if   args.step == 'server':     run_linker_server(args)
    elif args.step == 'client':     run_linker_client(args)
