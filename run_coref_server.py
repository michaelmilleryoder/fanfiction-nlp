"""
    @author: Shikhar Vashishth, modified by Michael Miller Yoder
"""


import sys; sys.path.append('./common')
from helper import *
from queue_client import *
from collections import ChainMap

#import scispacy, spacy
#from scispacy.abbreviation import AbbreviationDetector
#from pymongo.errors import BulkWriteError
import pdb

######################### Run CoreNLP on Entire Wikipedia

def run_corenlp(text, corenlp_ips):
    text_ = text.encode('utf-8')

    try:
        params = {
            'properties': '{"annotators":"tokenize,ssplit,pos,lemma,ner,parse,coref", "tokenize.whitespace": "true"}',
            'outputFormat': 'json'
            #'outputFormat': 'serialized',
            #"serializer": "edu.stanford.nlp.pipeline.ProtobufAnnotationSerializer"
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
        pdb.set_trace()
        return run_corenlp(text, corenlp_ips)

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

                with open(fname) as f:
                    f.readline()
                    for data in csv.reader(f):
                        fic_id, chapter_id, para_id, text, text_tokenized = data
                        res = run_corenlp(text_tokenized, ip_list)
                        print("Got result")
                        pdb.set_trace()
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


if __name__ == '__main__':
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
    args = parser.parse_args()

    if   args.step == 'server':     run_linker_server()
    elif args.step == 'client':     run_linker_client()
