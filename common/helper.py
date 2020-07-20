import os, sys, pdb, numpy as np, random, argparse, codecs, pickle, time, json, csv, itertools, bz2, re, requests
import logging, logging.config, itertools, pathlib, socket, pandas as pd

from tqdm import tqdm
from glob import glob
from pprint import pprint
from string import Template
from termcolor import colored
from pymongo import MongoClient
from scipy.stats import describe
from urllib.parse import urlencode
from collections import OrderedDict
from joblib import Parallel, delayed
from collections import defaultdict as ddict, Counter
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.metrics import f1_score, classification_report, roc_auc_score

# Global Variables
if os.environ.get('USER') == 'rjoshi2':
	PROJ_DIR	= '/projects/tir5/users/rjoshi2/medical_entity_linker/med_ent'
	WIKI_PATH	= '/projects/tir5/users/rjoshi2/medical_entity_linker/wikipedia/wikiextractor'
	DATA_PATH	= '/projects/tir5/users/rjoshi2/medical_entity_linker/med_ent'
	UMLS_DIR	= '/projects/tir5/users/rjoshi2/medical_entity_linker/umls/2019AB/META/'
	PUBMED_PATH     = '/projects/tir5/users/rjoshi2/medical_entity_linker/med_ent/pubmed'
else:
	PROJ_DIR	= '/projects/re_mty'
	WIKI_PATH	= '/data/med_ent/wikipedia'
	PUBMED_PATH	= '/data/re_mty/pubmed'
	DATA_PATH	= '/data/re_mty'
	UMLS_DIR	= '/data/bionlp_resources/umls/2019AB'
	WD_DIR		= '/data/bionlp_resources/wikidata'
	RE_DIR		= '/data/re_mty/re_gen'
	BIO_RE_DIR	= '/data/re_mty/med_re'
	WD_PATH		= '/data/bionlp_resources/wikidata'
	FB_PATH		= '/data/bionlp_resources/datasets/freebase'
	RE_DATA_DIR 	= '/data/re_mty'
	
WD_URL  = 'https://query.wikidata.org/sparql'
c_mongo	= MongoClient('mongodb://{}:{}/'.format('brandy.lti.cs.cmu.edu', 27017), username='vashishths', password='yogeshwara')

def partition(lst, n):
	if n == 0: return lst
	division = len(lst) / float(n)
	return [ lst[int(round(division * i)): int(round(division * (i + 1)))] for i in range(n) ]

def get_chunks(inp_list, chunk_size):
	return [inp_list[x:x+chunk_size] for x in range(0, len(inp_list), chunk_size)]

def mergeList(list_of_list):
	return list(itertools.chain.from_iterable(list_of_list))

def dump_pickle(obj, fname):
	pickle.dump(obj, open(fname, 'wb'))
	print('Pickled Dumped {}'.format(fname))

def load_pickle(fname):
	return pickle.load(open(fname, 'rb'))

def make_dir(dirpath):
	if not os.path.exists(dirpath):
		os.makedirs(dirpath)

def check_file(filename):
	return pathlib.Path(filename).is_file()

def str_proc(x):
	return str(x).strip().lower()

def set_gpu(gpus):
	os.environ["CUDA_DEVICE_ORDER"]    = "PCI_BUS_ID"
	os.environ["CUDA_VISIBLE_DEVICES"] = gpus

def count_parameters(model):
	return sum(p.numel() for p in model.parameters() if p.requires_grad)

def get_logger(name, log_dir, config_dir):
	config_dict = json.load(open('{}/log_config.json'.format(config_dir)))
	config_dict['handlers']['file_handler']['filename'] = '{}/{}'.format(log_dir, name.replace('/', '-'))
	logging.config.dictConfig(config_dict)
	logger = logging.getLogger(name)

	std_out_format = '%(asctime)s - [%(levelname)s] - %(message)s'
	consoleHandler = logging.StreamHandler(sys.stdout)
	consoleHandler.setFormatter(logging.Formatter(std_out_format))
	logger.addHandler(consoleHandler)

	return logger

def to_gpu(batch, dev):
	batch_gpu = {}
	for key, val in batch.items():
		if   key.startswith('_'):	batch_gpu[key] = val
		elif type(val) == type({1:1}): 	batch_gpu[key] = {k: v.to(dev) for k, v in batch[key].items()}
		else: 				batch_gpu[key] = val.to(dev)
	return batch_gpu


class ResultsMongo:
	def __init__(self, params, ip='brandy.lti.cs.cmu.edu', port=27017, db='re_mty', username='vashishths', password='yogeshwara'):
		self.p		= params
		self.client	= MongoClient('mongodb://{}:{}/'.format(ip, port), username=username, password=password)
		self.db		= self.client[db][self.p.log_db]
		# self.db.update_one({'_id': self.p.name}, {'$set': {'Params': }}, upsert=True)

	def add_results(self, best_val, best_test, best_epoch, train_loss):
		try:
			self.db.update_one({'_id': self.p.name}, {
				'$set': {
					'best_epoch'	: best_epoch,
					'best_val'	: best_val,
					'best_test'	: best_test,
					'Params'	: vars(self.p)
				},
				'$push':{
					'train_loss'	: round(float(train_loss), 4),
					'all_val'	: best_val,
					'all_test'	: best_test,
				}
			}, upsert=True)
		except Exception as e:
			print('\nMongo Exception Cause: {}'.format(e.args[0]))

def read_csv(fname):
	with open(fname) as f:
		f.readline()
		for data in csv.reader(f):
			yield data

def mean_dict(acc):
	return {k: np.round(np.mean(v), 3) for k, v in acc.items()}

def comb_dict(res):
	return {k: [x[k] for x in res] for k in res[0].keys()}

def get_param(shape):
	param = Parameter(torch.Tensor(*shape)); 	
	xavier_normal_(param.data)
	return param

def sigmoid(x):
	return 1 / (1 + np.exp(-x))

def mongo_bulk_exec(bulk, main):
	from pymongo.errors import BulkWriteError

	try: 
		bulk.execute()

	except BulkWriteError as e: 
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print('\nException Type: {}\nCause: {}\nType:{}\nfname: {}\nline_no: {}'.format(exc_type, e.args[0], e.details.get('writeErrors', ['None'])[0], fname, exc_tb.tb_lineno))

	except Exception as e:
		print('\nException Cause: {}'.format(e.args[0]))
		
	finally:
		return main.initialize_unordered_bulk_op()


def tune_thresholds(labels, logits, method = 'tune'):
	'''
	Takes labels and logits and tunes the thresholds using two methods
	methods are 'tune' or 'zc' #Zach Lipton
	Returns a list of tuples (thresh, f1) for each feature
	'''
	if method not in ['tune', 'zc']:
		print ('Tune method should be either tune or zc')
		sys.exit(1)
	from sklearn.metrics import f1_score, precision_recall_fscore_support, precision_score
	res = []
	logits = sigmoid(logits)

	num_labels = labels.shape[1]

	def tune_th(pid, feat):
		max_f1, th = 0, 0		# max f1 and its thresh
		if method == 'tune':
			ts_to_test = np.arange(0, 1, 0.001)
			for t in ts_to_test:
				scr  = f1_score(labels[:, feat], logits[:, feat] > t)
				if scr > max_f1:
					max_f1	= scr
					th	= t
		else:
			f1_half = f1_score(labels[:, feat], logits[:, feat] > 0.5)
			th = f1_half / 2
			max_f1 = f1_score(labels[:, feat], logits[:, feat] > th)

		return (th, max_f1)
		
	res = Parallel(n_jobs = 1)(delayed(tune_th)(lbl, lbl) for lbl in range(num_labels))
	return res

def gsearch(text):
	return f"http://googl.com/#{urlencode({'q': '{}'.format(text)})}"

def get_hash(s):
	return abs(hash(s)) % (10 ** 8)

class COL:
	HEADER = '\033[95m' 	# Violet
	INFO = '\033[94m'	# Blue 
	SUCCESS = '\033[92m'	# Green
	WARNING = '\033[93m'	# Yellow
	FAIL = '\033[91m'	# Red

	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def color(s, col):
	if   col == 'head': return f"{COL.HEADER}{s}{COL.ENDC}"
	elif col == 'info': return f"{COL.INFO}{s}{COL.ENDC}"
	elif col == 'warn': return f"{COL.WARNING}{s}{COL.ENDC}"
	elif col == 'succ': return f"{COL.SUCCESS}{s}{COL.ENDC}"
	elif col == 'fail': return f"{COL.FAIL}{s}{COL.ENDC}"
	elif col == 'def': return f"{s}"
	return s

def convert_token(token):
	""" Convert PTB tokens to normal tokens """
	if   (token.lower() == '-lrb-'): 	return '('
	elif (token.lower() == '-rrb-'): 	return ')'
	elif (token.lower() == '-lsb-'): 	return '['
	elif (token.lower() == '-rsb-'): 	return ']'
	elif (token.lower() == '-lcb-'): 	return '{'
	elif (token.lower() == '-rcb-'): 	return '}'
	return token