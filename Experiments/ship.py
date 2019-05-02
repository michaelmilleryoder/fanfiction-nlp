import csv
import glob


def mapping_dict(stories_dir, output_dir):
    # stories_dir = "/usr0/home/prashang/DirectedStudy/chatbot/output/example_academia_100/"
    meta_file = stories_dir + "stories.csv"
    with open(meta_file) as csvfile:
            story_csv_list = list(list(rec) for rec in csv.reader(csvfile, delimiter=','))

    story_csv_list = story_csv_list[1:]
    temp_meta_dict = {}
    for row in story_csv_list:
        temp_meta_dict[row[0]] = row[1:]

    # output_dir = "/usr0/home/prashang/DirectedStudy/new_fic_pipe/output/acad_full/"
    allQuoteFiles = glob.glob(output_dir + "quote_attribution" + "/*.quote.json")
    allQuoteFiles = set([file.split("/")[-1].split(".")[0].split("_")[0] for file in allQuoteFiles])
    meta_dict = {}
    for key in temp_meta_dict:
        if key in allQuoteFiles:
            meta_dict[key] = temp_meta_dict[key][6][1:-2].split(",")

    ship_dict = {}
    for key in meta_dict:
        ships = []
        for ship in meta_dict[key]:
            ships.append(ship.split("/"))
        ship_dict[key] = ships
    return meta_dict
