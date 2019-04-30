import sys

config_path = sys.argv[1]
config_section = sys.argv[2]
csv_dir = sys.argv[3]
txt_dir = sys.argv[4]
output_dir = sys.argv[5]

import configparser
config = configparser.ConfigParser()
config.readfp(open(config_path))

# get config parameters
config.set(config_section,'test_csv_dir',csv_dir)
config.set(config_section,'test_txt_dir',txt_dir)
config.set(config_section,'nb_output_path',output_dir+'nb_labels')
config.set(config_section,'bm25_output_path',output_dir+'bm25_labels')

with open(config_path, 'w') as configfile:
    config.write(configfile)


