#!/bin/bash
BOOKNLP_BASE=$1
tmptextfile=$2
booknlpoutput=$3
tokenfile=$4
logfile=$5
cd ${BOOKNLP_BASE}
./runjava novels/BookNLP -doc ${tmptextfile} -printHTML -p ${booknlpoutput} -tok ${tokenfile} -f -d > ${logfile}
