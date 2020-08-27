<<<<<<< HEAD
java -Djava.io.tmpdir=./tmp -mx49g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port $1 -timeout 150000 -preload tokenize,ssplit,pos,lemma,ner,parse,coref
=======
java -Djava.io.tmpdir=./tmp -mx16g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port $1 -timeout 1500000 -preload tokenize,ssplit,pos,lemma,ner,parse,coref -quiet -maxCharLength 1000000
>>>>>>> f247be7f951f3f2cec7be19a455cdf85caf45287
