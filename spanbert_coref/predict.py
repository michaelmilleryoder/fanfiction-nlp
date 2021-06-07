import json
import pdb
from spacy.lang.en import English
from spanbert_coref.preprocess import get_document
import argparse
import spanbert_coref.util as util
from spanbert_coref.tensorize import CorefDataProcessor
from spanbert_coref.run import Runner
import logging
logging.getLogger().setLevel(logging.CRITICAL)


def create_spacy_tokenizer():
    nlp = English()
    sentencizer = nlp.create_pipe('sentencizer')
    nlp.add_pipe(sentencizer)


def get_document_from_string(string, seg_len, bert_tokenizer, spacy_tokenizer, genre='nw'):
    doc_key = genre  # See genres in experiment config
    doc_lines = []

    # Build doc_lines
    for token in spacy_tokenizer(string):
        cols = [genre] + ['-'] * 11
        cols[3] = token.text
        doc_lines.append('\t'.join(cols))
        if token.is_sent_end:
            doc_lines.append('\n')

    doc = get_document(doc_key, doc_lines, 'english', seg_len, bert_tokenizer)
    return doc


def main(config_name, model_identifier, gpu_id=None, seg_len=512, 
    jsonlines_path=None, output_path=None):
    """ Main entry point """
    runner = Runner(config_name, gpu_id)
    model = runner.initialize_model(model_identifier)
    data_processor = CorefDataProcessor(runner.config)

    if jsonlines_path:
        # Input from file
        with open(jsonlines_path, 'r') as f:
            lines = f.readlines()
        docs = [json.loads(line) for line in lines]
        tensor_examples, stored_info = data_processor.get_tensor_examples_from_custom_input(docs)
        predicted_clusters, _, _ = runner.predict(model, tensor_examples)

        if output_path:
            with open(output_path, 'w') as f:
                for i, doc in enumerate(docs):
                    doc['predicted_clusters'] = predicted_clusters[i]
                    f.write(json.dumps(doc) + "\n")
            #print(f'Saved prediction in {output_path}')
    else:
        # Interactive input
        model.to(model.device)
        nlp = English()
        nlp.add_pipe(nlp.create_pipe('sentencizer'))
        while True:
            input_str = str(input('Input document:'))
            bert_tokenizer, spacy_tokenizer = data_processor.tokenizer, nlp
            doc = get_document_from_string(input_str, seg_len, bert_tokenizer, nlp)
            tensor_examples, stored_info = data_processor.get_tensor_examples_from_custom_input([doc])
            predicted_clusters, _, _ = runner.predict(model, tensor_examples)

            subtokens = util.flatten(doc['sentences'])
            #print('---Predicted clusters:')
            for cluster in predicted_clusters[0]:
                mentions_str = [' '.join(subtokens[m[0]:m[1]+1]) for m in cluster]
                mentions_str = [m.replace(' ##', '') for m in mentions_str]
                mentions_str = [m.replace('##', '') for m in mentions_str]
                #print(mentions_str)  # Print out strings
                # print(cluster)  # Print out indices

def get_args():
    """ Get command-line arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_name', type=str, required=True,
                        help='Configuration name in experiments.conf')
    parser.add_argument('--model_identifier', type=str, required=True,
                        help='Model identifier to load')
    parser.add_argument('--gpu_id', type=int, default=None,
                        help='GPU id; CPU by default')
    parser.add_argument('--seg_len', type=int, default=512)
    parser.add_argument('--jsonlines_path', type=str, default=None,
                        help='Path to custom input from file; input from console by default')
    parser.add_argument('--output_path', type=str, default=None,
                        help='Path to save output')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    main(args.config_name, args.model_identifier, args.gpu_id, args.seg_len,
        args.jsonlines_path, args.output_path)
