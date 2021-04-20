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
import sys
import subprocess
import pdb
import traceback

from quote_attribution_muzny.attribute_quotes import attribute_quotes


class Pipeline():

    def __init__(self, collection_name, input_path, output_path, modules=[],
                    coreference_settings=[], quote_attribution_settings=[]):
        self.collection_name = collection_name
        self.input_path = input_path
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
        self.coref_stories_path = os.path.join(self.output_path, 'char_coref_stories')
        self.coref_chars_path = os.path.join(self.output_path, 'char_coref_chars')
        self.modules = modules
        self.coreference_settings = coreference_settings
        self.quote_attribution_settings = quote_attribution_settings
        self.coref_stories_path = os.path.join(self.output_path, 'char_coref_stories')
        self.coref_chars_path = os.path.join(self.output_path, 'char_coref_chars')
        self.coref_output_path = os.path.join(self.output_path, 'char_coref')

    def run(self):
        if 'coref' in self.modules:
            print("Running character coreference...")
            self.coref(*self.coreference_settings)
        if 'quote_attribution' in self.modules:
            n_quote_threads = self.quote_attribution_settings[0]
            self.quote_attribution(n_quote_threads)
        if 'assertion_extraction' in self.modules:
            self.assertion_extraction()

    def coref(self, coref_alg, n_servers, n_threads):
        """ Run character coreference """
        if coref_alg == 'spanbert':
            self.coref_spanbert(n_threads)
        elif coref_alg == 'corenlp':
            self.coref_corenlp(n_servers, n_threads)

    def coref_spanbert(self, n_threads):
        """ Run coref using SpanBERT """
        subprocess.run(['python3', 'spanbert_coref/main.py', self.input_path,
            self.coref_output_path, '--threads', str(n_threads)], 
            check=True)

    def coref_corenlp(self, n_servers, n_threads):
        """ Run coref using modified CoreNLP """
        if not os.path.exists(self.coref_stories_path):
            os.mkdir(self.coref_stories_path)
        if not os.path.exists(self.coref_chars_path):
            os.mkdir(self.coref_chars_path)
        if not os.path.exists('log'):
            os.mkdir('log')

        try:
            with open('log/coref_corenlp_servers.log', 'w') as logfile:
                # Start CoreNLP servers
                server_proc = self.start_corenlp_servers(n_servers, n_threads, logfile)

                # Start Flask filename queue server, add filenames to it
                print('Starting filename queue server...')
                if subprocess.run(['pgrep', '-f', 'queue_server.py 1234']).returncode != 0:
                    subprocess.Popen(['python3', 'queue_server.py', '1234'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.call(['python3', 'run_coref_server.py', '--step', 'server', '--clear', '--port', '1234', '--input', self.input_path])

                print("Processing files...")
                # Start client processing
                #client_proc = subprocess.run(['python3', 'run_coref_server.py', '--step', 'client', '--port', '1234', '--output', str(self.output_path), '--nums', str(n_servers), '--workers', str(n_threads)])
                client_proc = subprocess.Popen(['python3', 'run_coref_server.py', '--step', 'client', '--output', str(self.output_path), '--nums', str(n_servers), '--workers', str(n_threads)])

                while True:
                    for line in server_proc.stderr: # Does this ever end?
                        logfile.write(line)
                    if client_proc.poll() is not None:
                        break

                print("Stopping coreference servers...")
                # Stop CoreNLP servers
                subprocess.call(['python3', 'run_corenlp_servers.py', '--stop', '8060', str(n_servers)])

        except Exception as e:
            print("Stopping coreference servers...")
            # Stop CoreNLP servers
            subprocess.call(['python3', 'run_corenlp_servers.py', '--stop', '8060', str(n_servers)])

            track = traceback.format_exc()
            print(track)

    def quote_attribution(self, n_threads): 
        """ Run quote attribution with Muzny method """
        os.chdir('quote_attribution_muzny') # seems unstable to do this
        quote_output_path = os.path.join(self.output_path, 'quote_attribution')
        attribute_quotes(self.input_path, self.coref_output_path, 
            quote_output_path, n_threads)
        os.chdir('..')

    def quote_attribution_he(self, svmrank_path):
        """ Run quote attribution with old method (not used anymore) """
        quote_output_path = os.path.join(self.output_path, 'quote_attribution')
        if not os.path.exists(quote_output_path):
            os.mkdir(quote_output_path)
        os.chdir('quote_attribution')
        cmd = [ 'python3', 'run.py', 'predict', 
                '--story-path', self.coref_stories_path,
                '--char-path', self.coref_chars_path,
                '--output-path', quote_output_path,
                '--features', 'disttoutter', 'spkappcnt', 'nameinuttr', 'spkcntpar',
                '--model-path', 'models/austen_5features_c50.model',
                '--svmrank', svmrank_path
            ]
        subprocess.call(cmd)
        os.chdir('..')

    def assertion_extraction(self):
        assertion_output_path = os.path.join(self.output_path, 'assertion_extraction')
        if not os.path.exists(assertion_output_path):
            os.mkdir(assertion_output_path)

        subprocess.call(['python3', 'assertion_extraction/extract_assertions.py',
            self.coref_stories_path, self.coref_chars_path, assertion_output_path])

    def start_corenlp_servers(self, n_servers, n_threads, logfile):
        print("Starting coreference servers...")

        # Start subprocess, wait until the servers are ready to return
        proc = subprocess.Popen(f'python3 run_corenlp_servers.py --start 8060 {n_servers}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        line_count = 0
        while True:
            line = proc.stderr.readline()
            logfile.write(line)
            if 'StanfordCoreNLPServer listening' in line:
                sys.stderr.write(f'\t{line}')
                line_count += 1
            if line_count == n_servers: # TODO: sometimes doesn't happen (not sure why). Should wait and then just move if not, or raise an Exception
                break

        return proc


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
        coref_alg = config.get('Character coreference', 'coref_type')
        coreference_settings.append(coref_alg)
        n_servers = config.getint('Character coreference', 'n_servers')
        coreference_settings.append(n_servers)
        n_threads = config.getint('Character coreference', 'n_threads')
        coreference_settings.append(n_threads)

    # Quote attribution settings
    quote_attribution_settings = []
    if run_quote_attribution:
        modules.append('quote_attribution')
        n_threads = config.getint('Quote attribution', 'n_threads')
        quote_attribution_settings.append(n_threads)

    # Assertion extraction settings
    if run_assertion_extraction:
        modules.append('assertion_extraction')

    pipeline = Pipeline(collection_name, input_path, output_path, modules,
                        coreference_settings=coreference_settings,
                        quote_attribution_settings=quote_attribution_settings)
    pipeline.run()


if __name__ == '__main__':
    main()
