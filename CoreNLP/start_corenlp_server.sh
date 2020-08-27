java -Djava.io.tmpdir=./tmp -mx16g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port $1 -timeout 1500000 -preload tokenize,ssplit,pos,lemma,ner,parse,coref -quiet -maxCharLength 1000000
