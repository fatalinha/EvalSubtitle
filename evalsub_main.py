#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import os.path

import pandas as pd

from evalsub.eval.seg_eval import get_metrics
from evalsub.eval.f1_eval import evaluate_f1
from evalsub.eval.length_conformity import len_process
from evalsub.eval.ter_eval import ter_process
from evalsub.eval.bleu_eval import bleu_process
import evalsub.util.constants as cst


def run_evaluation(reference_file, sys_file, metrics, no_ter=False):
    window, pk, windiff, seg_sim, bound_sim = get_metrics(sys_file, reference_file)
    len_conf = len_process(sys_file, 42)
    bleu = bleu_process(reference_file, sys_file).score
    ter_br = -1 if no_ter else ter_process(reference_file, sys_file).score
    precision, recall, f1 = evaluate_f1(reference_file, sys_file, '<eox>', ttml=False, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG)

    # collect metrics to dictionary
    metrics[cst.SYSTEM].append(os.path.basename(sys_file))
    metrics[cst.WIN_SIZE].append(window)
    metrics[cst.PK].append(round(pk, 3))
    metrics[cst.WIN_DIFF].append(round(windiff, 3))
    metrics[cst.PRECISION].append(precision)
    metrics[cst.RECALL].append(recall)
    metrics[cst.F1].append(f1)
    metrics[cst.BLEU_BR].append(bleu)
    metrics[cst.TER_BR].append(ter_br)
    metrics[cst.LENGTH].append(len_conf)
    metrics[cst.SEG_SIM].append(seg_sim)
    metrics[cst.BOUND_SIM].append(bound_sim)


def write_csv(outfile, metric_dic):
    # write to csv
    eval_metrics = dict(System=[], Win=[], Pk=[], WinDiff=[], Precision=[], Recall=[], F1=[],
                        BLEU=[], TER_br=[], Len=[])
    df = pd.DataFrame.from_dict(eval_metrics)
    with open(outfile, 'w') as out:
        df.to_csv(outfile, index=False, header=False)

