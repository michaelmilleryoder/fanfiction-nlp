#!/bin/bash
SVMRANK_BASE="/usr0/home/huimingj/svm_rank"
BOOKNLP_BASE="/usr0/home/huimingj/book-nlp-master"
DATA_BASE="/usr0/home/huimingj/pipeline/example_data"

SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
FEATURES="disttoutter,spkappcnt,nameinuttr,spkcntpar"

cd ${BOOKNLP_BASE}

./runjava novels/BookNLP -doc ${DATA_BASE}/$1 -printHTML -p ${DATA_BASE}/output/$1 -tok ${DATA_BASE}/tokens/$1.tokens -f -d

cd ${SHELL_FOLDER}

python2 quotation_attribution_feature_extract.py --tokenfile ${DATA_BASE}/tokens/$1.tokens --charfile ${DATA_BASE}/$2 --output ${DATA_BASE}/svminput/$1.svmrank --features ${FEATURES} 

${SVMRANK_BASE}/svm_rank_classify ${DATA_BASE}/svminput/$1.svmrank ${SHELL_FOLDER}/austen.model ${DATA_BASE}/$1.predict

python2 makejson.py --svmfile ${DATA_BASE}/svminput/$1.svmrank --charfile ${DATA_BASE}/$2 --tokenfile ${DATA_BASE}/tokens/$1.tokens --predictfile ${DATA_BASE}/$1.predict --outputfile ${DATA_BASE}/$1.quote.json
