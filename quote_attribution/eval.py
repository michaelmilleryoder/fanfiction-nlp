# -*- coding: utf-8 -*-
import os
import codecs
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--answerfile', help='Path to the ground truth file', required=True)
    parser.add_argument('--prediction', help='Path to the prediction file', required=True)
    opt = parser.parse_args()   
    answerfile = opt.answerfile
    prediction = opt.prediction

    ans = []
    qids = set()
    with codecs.open(answerfile) as f:
        for line in f:
            if line[0] != '#':
                l = line.split()
                qid = int(l[1].split(':')[1])
                if qid not in qids:
                    qids.add(qid)
                    ans.append([])
                ans[-1].append(int(l[0]))
    
    pdc = []
    with codecs.open(prediction) as f:
        for line in f:
            pdc.append(float(line.strip()))
    
    base = 0
    acc = 0
    for qry in ans:
        l = len(qry)
        predictions = pdc[base : base+l]
        maxv = predictions[0]
        maxp = 0
        for i in range(l):
            if predictions[i] > maxv:
                maxv = predictions[i]
                maxp = i
        #print(qry)
        #print(predictions)
        #print(maxp)
        #print('------')
        if qry[maxp] == 1:
            acc += 1
        base += l

    print('acc:' + str(float(acc) / len(ans)))
