java -Djava.io.tmpdir=/tmp -mx48g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port $1 -timeout 150000 -preload tokenize,ssplit,pos,lemma,ner,parse,mention,coref
