import os
import csv
import codecs

path_prefix = '/usr0/home/huimingj/fanfic/ao3_detroit_text/'
output_path = '/usr0/home/huimingj/fanficproj/data/origin_text/ao3_detroit/'

if not os.path.isdir(output_path):
    os.makedirs(output_path)

corpus = {}

with codecs.open(os.path.join(path_prefix, 'chapters.csv')) as f:
    f_csv = csv.reader(f)
    headers = next(f_csv)
    for line in f_csv:
        fic_id = line[0]
        chapter_num = line[2]
        filename = '%d_%04d' % (int(fic_id), int(chapter_num))
        print filename
        if fic_id not in corpus:
            corpus[fic_id] = []
        with codecs.open(os.path.join(path_prefix, 'stories', filename + '.csv')) as fch:
            fch_csv = csv.reader(fch)
            headers_ch = next(fch_csv)
            for line_ch in fch_csv:
                text = line_ch[3]
                corpus[fic_id].append(text)

for fic_id in corpus:
    print fic_id
    with codecs.open(os.path.join(output_path, fic_id + '.txt'), 'w') as textout:
        for par in corpus[fic_id]:
            textout.write(par + '\n\n')

