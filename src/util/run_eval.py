# coding: utf-8
import os.path
import pandas as pd
import sys
from eval_segmentation import get_metrics
from f1_eval import evaluate_f1
from length_conformity import len_process
from ter_eval import ter_process
from bleu_eval import bleu_process

CAPTION_TAG = '<eob>'
LINE_TAG = '<eol>'
#reference_f = '/home/alin/Desktop/subtitling/02_data/Must-Cinema/en-fr/amara.en'#sys.argv[1]
#system_f = '/home/alin/Desktop/subtitling/03_scripts/EvalSub/02_contrastive_pairs/shift/amara.shift.1.20'
#outfile = sys.argv[3]


def run_evaluation(reference_file, sys_file, metrics):
    window, pk, windiff = get_metrics(sys_file, reference_file)
    len_conf = len_process(sys_file, 42)
    bleu = bleu_process(reference_file, sys_file)
    ter_br = ter_process(reference_file, sys_file)
    precision, recall, f1 = evaluate_f1(reference_file, sys_file, '<eox>', ttml=False, line_tag=LINE_TAG, caption_tag=CAPTION_TAG)

    # collect metrics to dictionary
    metrics['System'].append(os.path.basename(sys_file))
    metrics['Win'].append(window)
    metrics['Pk'].append(round(pk, 3))
    metrics['WinDiff'].append(round(windiff, 3))
    metrics['Precision'].append(precision)
    metrics['Recall'].append(recall)
    metrics['F1'].append(f1)
    metrics['BLEU'].append(bleu)
    metrics['TER_br'].append(ter_br)
    #metrics['TER_br'].append(0)
    metrics['Len'].append(len_conf)
    return metrics

# write to csv
#eval_metrics = dict(System=[], Win = [], Pk=[], WinDiff=[], Precision=[], Recall=[], F1=[], BLEU=[], TER_br=[],Len=[])
#run_evaluation(reference_f, system_f, eval_metrics)
#df = pd.DataFrame.from_dict(eval_metrics)
#df.to_csv(outfile, index=False, header=False)
