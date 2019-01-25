#!/bin/bash
SVMRANK_BASE="/usr0/home/huimingj/svm_rank"
BOOKNLP_BASE="/usr0/home/huimingj/book-nlp-master"

SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
FEATURES="disttoutter,spkappcnt,nameinuttr,spkcntpar"

if [ ! -d $3  ];then
  mkdir -p $3
fi

cd $1
filenames=$(ls *.coref.out)
for file in ${filenames};do
    filename=${file##*/}
    farr=(${filename//./ }) 
    filename_stem=${farr[0]}
    echo Processing ${filename_stem} ...

    tmpdir=${SHELL_FOLDER}/tmp/${filename_stem}

    if [ ! -d ${tmpdir}  ];then
        mkdir -p ${tmpdir}
    fi

    tmpdir=${SHELL_FOLDER}/tmp/${filename_stem}
    booknlpoutput=${tmpdir}/booknlp_output
    tokenfile=${tmpdir}/${filename_stem}.tokens
    charfile=$2/${filename_stem}.coref.chars
    svmrankinput=${tmpdir}/${filename_stem}.svmrank
    predictfile=${tmpdir}/${filename_stem}.predict
    tmpcharfile=${tmpdir}/${filename_stem}.tmpchar
    tmptextfile=${tmpdir}/${filename_stem}.tmptext

    cd ${SHELL_FOLDER}
    python2 preprocess.py --csvinput $1/${file} --charfile ${charfile} --char_output ${tmpcharfile} --story_output ${tmptextfile}
    cd ${BOOKNLP_BASE}
    ./runjava novels/BookNLP -doc ${tmptextfile} -printHTML -p ${booknlpoutput} -tok ${tokenfile} -f -d
    cd ${SHELL_FOLDER}
    python2 quotation_attribution_feature_extract.py --tokenfile ${tokenfile} --charfile ${tmpcharfile} --output ${svmrankinput} --features ${FEATURES}
    ${SVMRANK_BASE}/svm_rank_classify ${svmrankinput} ${SHELL_FOLDER}/austen.model ${predictfile}
    python2 makejson.py --svmfile ${svmrankinput} --charfile ${tmpcharfile} --tokenfile ${tokenfile} --predictfile ${predictfile} --outputfile $3/${filename_stem}.quote.json
done

#cd ${BOOKNLP_BASE}

#./runjava novels/BookNLP -doc ${DATA_BASE}/$1 -printHTML -p ${DATA_BASE}/output/$1 -tok ${DATA_BASE}/tokens/$1.tokens -f -d

#cd ${SHELL_FOLDER}

#python2 quotation_attribution_feature_extract.py --tokenfile ${DATA_BASE}/tokens/$1.tokens --charfile ${DATA_BASE}/$2 --output ${DATA_BASE}/svminput/$1.svmrank --features ${FEATURES} 

#${SVMRANK_BASE}/svm_rank_classify ${DATA_BASE}/svminput/$1.svmrank ${SHELL_FOLDER}/austen.model ${DATA_BASE}/$1.predict

#python2 makejson.py --svmfile ${DATA_BASE}/svminput/$1.svmrank --charfile ${DATA_BASE}/$2 --tokenfile ${DATA_BASE}/tokens/$1.tokens --predictfile ${DATA_BASE}/$1.predict --outputfile ${DATA_BASE}/$1.quote.json
