# coding: utf-8

from eval_segmentation import *
from f1_eval import evaluate_f1
from length_conformity import len_process
from ter_eval import ter_process
from bleu_eval import bleu_process

CAPTION_TAG = '<eob>'
LINE_TAG = '<eol>'
reference_file = '/home/alin/Desktop/subtitling/02_data/Must-Cinema/en-fr/amara.en'#sys.argv[1]
sys_file = '/home/alin/Desktop/subtitling/03_scripts/EvalSub/02_contrastive_pairs/every42chars/amara.42.en'#seq2seqSegmenter/generate-amara_en'
# TODO: pk, windiff

len_conf = len_process(sys_file, 42)
ter_br = ter_process(reference_file, sys_file)
bleu = bleu_process(reference_file, sys_file)
# TODO: average vs same
precision, recall, f1 = evaluate_f1(reference_file, sys_file, '<eox>', ttml=False, line_tag=LINE_TAG, caption_tag=CAPTION_TAG)

print(len_conf, bleu, precision, recall, f1)