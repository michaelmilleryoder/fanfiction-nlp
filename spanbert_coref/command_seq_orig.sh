python convert_text_to_conll.py /data/fanfiction_ao3/annotated_10fandom/test/fics/allmarvel_606106.csv ./conll_dir

python preprocess.py --filename allmarvel_606106 --input_dir ./conll_dir --output_dir ./json_dir --seg_len 384

python predict.py --config_name=train_spanbert_base_lit_toshni --model_identifier=Jan27_03-17-00_4200 --gpu_id=-1 --jsonlines_path=./json_dir/allmarvel_606106.english.384.jsonlines --output_path=pred_dir/allmarvel_606106.pred.english.384.jsonlines

python inference_fanfic.py pred_dir/allmarvel_606106.pred.english.384.jsonlines coref_output_dir/
