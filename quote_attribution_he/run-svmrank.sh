#!/bin/bash
SVMRANK_BASE=$1
svmrankinput=$2
modelpath=$3
predictfile=$4
${SVMRANK_BASE}/svm_rank_classify ${svmrankinput} ${modelpath} ${predictfile}
