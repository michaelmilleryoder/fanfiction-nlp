import gensim
import os
import collections
import smart_open
import random
import sys

q_file = sys.argv[1]

def read_corpus(fname, tokens_only=False):
    with smart_open.smart_open(fname, encoding="iso-8859-1") as f:
        for i, line in enumerate(f):
            if tokens_only:
                yield gensim.utils.simple_preprocess(line)
            else:
                # For training data, add tags
                yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])

train_corpus = list(read_corpus(q_file))
model = gensim.models.doc2vec.Doc2Vec(vector_size=300, min_count=2, epochs=40)

model.build_vocab(train_corpus)
model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)

#sample and infer
#print train_corpus[-2]
#inferred_vector=model.infer_vector(train_corpus[-2].words)
#sims = model.docvecs.most_similar([inferred_vector], topn=20)
#print sims
model.save(q_file+'.doc2vec.model')
