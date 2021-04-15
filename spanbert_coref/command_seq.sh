filename=5k_11940_glee
#filename=10k_24333940_percy_jackson
#filename=20k_allmarvel398294
#filename=30k_homestuck1063383

python convert_text_to_conll.py /data/fanfiction_ao3/size_samples/fics/$filename.csv conll_dir

python preprocess.py --filename $filename --input_dir conll_dir --output_dir json_dir --seg_len 384

python predict.py --config_name=train_spanbert_base_lit_toshni --model_identifier=Jan27_03-17-00_4200 --gpu_id=-1 --jsonlines_path=./json_dir/$filename.english.384.jsonlines --output_path=pred_dir/$filename.pred.english.384.jsonlines

python inference_fanfic.py pred_dir/$filename.pred.english.384.jsonlines coref_output_dir/
