# This script processes a directory of fanfiction files and extracts
# relevant text to characters.
# 
# 
# Steps include:
#	* Character coreference
#	* Character feature extraction
#		* Quote attribution
#		* Assertion (facts about a character) attribution
#	* Character cooccurrence matrix
#	* Alternate universe (AU) extraction from fic metadata
#
#
# Input: directory path to directory of fic chapter CSV files
# Output:

from configparser import ConfigParser
import argparse
import os
from subprocess import call
import pdb


class Pipeline():

    def __init__(self, collection_name, input_path, output_path, modules=[],
                    coreference_settings=[], quote_attribution_settings=[]):
        self.collection_name = collection_name
        self.input_path = input_path
        self.output_path = output_path
        self.modules = modules
        self.coreference_settings = coreference_settings
        self.quote_attribution_settings = quote_attribution_settings
        self.coref_stories_path = os.path.join(self.output_path, 'char_coref_stories')
        self.coref_chars_path = os.path.join(self.output_path, 'char_coref_chars')

    def run(self):
        if 'coref' in self.modules:
            self.coref(*self.coreference_settings)
        if 'quote_attribution' in self.modules:
            self.quote_attribution(*self.quote_attribution_settings)
        if 'assertion_extraction' in self.modules:
            self.assertion_extraction()

    def coref(self, n_threads, split_input_dir, max_files_per_split, delete_existing_tmp):
        if not os.path.exists(self.coref_stories_path):
            os.mkdir(self.coref_stories_path)
        if not os.path.exists(self.coref_chars_path):
            os.mkdir(self.coref_chars_path)

        call(['python3', 'RunCoreNLP.py', self.input_path, self.coref_chars_path, 
                self.coref_stories_path, self.collection_name, str(n_threads), str(split_input_dir), str(max_files_per_split), str(delete_existing_tmp)]) 

    def quote_attribution(self, svmrank_path):
        quote_output_path = os.path.join(self.output_path, 'quote_attribution')
        if not os.path.exists(quote_output_path):
            os.mkdir(quote_output_path)
        os.chdir('quote_attribution')
        cmd = [ 'run.py', 'predict', 
                '--story-path', self.coref_stories_path,
                '--char-path', self.coref_chars_path,
                '--output-path', quote_output_path,
                '--features', 'disttoutter', 'spkappcnt', 'nameinuutr', 'spkcntpar',
                '--model-path', 'models/austen_5features_c50.model',
                '--svmrank', svmrank_path
            ]
        call(cmd)

    def assertion_extraction(self):
        assertion_output_path = os.path.join(self.output_path, 'assertion_extraction')
        if not os.path.exists(assertion_output_path):
            os.mkdir(assertion_output_path)

        call(['python3', 'assertion_extraction/extract_assertions.py',
            self.coref_stories_path, self.coref_chars_path, assertion_output_path])


def main():

    # Load config settings, directory paths
    parser = argparse.ArgumentParser(description='Extract characters and quotes from fanfiction')
    parser.add_argument('configpath', nargs='?', help='path to the config file')
    args = parser.parse_args()
    config = ConfigParser(allow_no_value=True)
    config.read(args.configpath)

    collection_name = config.get('Input/output', 'collection_name')
    input_path = config.get('Input/output', 'input_path')
    output_path = config.get('Input/output', 'output_path')
    
    run_coref = config.getboolean('Character coreference', 'run_coref')
    run_quote_attribution = config.getboolean('Quote attribution', 'run_quote_attribution')
    run_assertion_extraction = config.getboolean('Assertion extraction', 'run_assertion_extraction')
    modules = []

    # Coref settings
    coreference_settings = []
    if run_coref:
        modules.append('coref')
        n_threads = config.getint('Character coreference', 'n_threads')
        coreference_settings.append(n_threads)
        split_input_dir = config.getboolean('Character coreference', 'split_input_dir')
        coreference_settings.append(split_input_dir)
        max_files_per_split = config.getint('Character coreference', 'max_files_per_split')
        coreference_settings.append(max_files_per_split)
        delete_existing_tmp = config.getboolean('Character coreference', 'delete_existing_tmp')
        coreference_settings.append(delete_existing_tmp)

    # Quote attribution settings
    quote_attribution_settings = []
    if run_quote_attribution:
        modules.append('quote_attribution')
        svmrank_path = config.get('Quote attribution', 'svmrank_path')
        quote_attribution_settings.append(svmrank_path)

    # Assertion extraction settings
    if run_assertion_extraction:
        modules.append('assertion_extraction')

    pipeline = Pipeline(collection_name, input_path, output_path, modules,
                        coreference_settings=coreference_settings,
                        quote_attribution_settings=quote_attribution_settings)
    pipeline.run()


if __name__ == '__main__':
    main()
