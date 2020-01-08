import sys
search_ficid = sys.argv[1]
search_chapid = sys.argv[2]
fname = "stories/"+search_ficid+'_'+search_chapid+".csv"
import csv
story = []
for row in csv.DictReader(open(fname)):
     story.append(row)
print story
