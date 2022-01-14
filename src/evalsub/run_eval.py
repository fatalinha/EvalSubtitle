# coding: utf-8

import os.path
import pandas as pd

from eval.seg_eval import get_metrics
from eval.f1_eval import evaluate_f1
from eval.length_conformity import len_process
from eval.ter_eval import ter_process
from eval.bleu_eval import bleu_process

CAPTION_TAG = '<eob>'
LINE_TAG = '<eol>'


def run_evaluation(reference_file, sys_file, metrics, no_ter=False):
    window, pk, windiff, seg_sim, bound_sim = get_metrics(sys_file, reference_file)
    len_conf = len_process(sys_file, 42)
    bleu = bleu_process(reference_file, sys_file).score
    ter_br = -1 if no_ter else ter_process(reference_file, sys_file).score
    precision, recall, f1 = evaluate_f1(reference_file, sys_file, '<eox>', ttml=False, line_tag=LINE_TAG, caption_tag=CAPTION_TAG)

    # collect metrics to dictionary
    metrics['System'].append(os.path.basename(sys_file))
    metrics['Win'].append(window)
    metrics['Pk'].append(round(pk, 3))
    metrics['WinDiff'].append(round(windiff, 3))
    metrics['Precision'].append(precision) #TODO: max val of pre,rec= 0.998
    metrics['Recall'].append(recall)
    metrics['F1'].append(f1)
    metrics['BLEU'].append(bleu)
    metrics['TER_br'].append(ter_br)
    metrics['Len'].append(len_conf)
    metrics['SegSim'].append(seg_sim)
    metrics['BoundSim'].append(bound_sim)


def write_csv(outfile, metric_dic):
    # write to csv
    eval_metrics = dict(System=[], Win=[], Pk=[], WinDiff=[], Precision=[], Recall=[], F1=[],
                        BLEU=[], TER_br=[], Len=[])
    df = pd.DataFrame.from_dict(eval_metrics)
    with open(outfile, 'w') as out:
        df.to_csv(outfile, index=False, header=False)

# TESTS
#reference_f = '/home/alin/Desktop/subtitling/02_data/Must-Cinema/en-fr/amara.en'
#system_f = '/home/alin/Desktop/subtitling/03_scripts/EvalSub/02_contrastive_pairs/shift/amara.shift.1.20'
