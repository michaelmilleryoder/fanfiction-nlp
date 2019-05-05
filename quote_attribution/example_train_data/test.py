import os
import csv

lines = []
with open('pride_prejudice.txt') as f_i:
    for line in f_i:
        line = line.strip()
        if len(line) > 0:
            lines.append(line + '\n')

with open('pride_prejudice.csv', 'w') as f_o:
    writer = csv.writer(f_o)
    writer.writerow(['fic_id', 'chapter_id', 'para_id', 'text'])
    for i, line in enumerate(lines):
        writer.writerow(['0', '1', str(i+1), line])
