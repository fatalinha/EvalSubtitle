#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

DESCRIPTION = """
"""

import argparse
import os.path

import pandas as pd

from evalsub.eval.seg_eval import seg_process
from evalsub.eval.f1_eval import f1_process
from evalsub.eval.cpl_eval import cpl_process
from evalsub.eval.ter_eval import ter_process
from evalsub.eval.sigma_eval import sigma_process
import evalsub.util.constants as cst


def run_evaluation(ref_file_path, sys_file_path, results, window_size=None, nt=cst.DEFAULT_NT, max_cpl=cst.MAX_CPL,
                   srt=False):

    results[cst.SYSTEM].append(os.path.basename(sys_file_path))

    if cst.PK in results or cst.WIN_DIFF in results or cst.SEG_SIM in results or cst.BOUND_SIM in results:
        win_size, pk, win_diff, seg_sim, bound_sim = seg_process(sys_file_path, ref_file_path, srt=srt,
                                                                 window_size=window_size, nt=nt)
        if cst.WIN_SIZE in results:
            results[cst.WIN_SIZE].append(win_size)
        if cst.PK in results:
            results[cst.PK].append(pk)
        if cst.WIN_DIFF in results:
            results[cst.WIN_DIFF].append(win_diff)
        if cst.NT in results:
            results[cst.NT].append(nt)
        if cst.SEG_SIM in results:
            results[cst.SEG_SIM].append(seg_sim)
        if cst.BOUND_SIM in results:
            results[cst.BOUND_SIM].append(bound_sim)

    if cst.CPL_CONF in results:
        cpl_conf = cpl_process(sys_file_path, max_cpl=max_cpl, srt=srt)
        results[cst.CPL_CONF].append(cpl_conf)

    if cst.BLEU_BR in results or cst.BLEU_NB in results or cst.SIGMA in results:
        sigma_score = sigma_process(ref_file_path, sys_file_path, srt=srt)
        bleu_br = sigma_score[cst.BLEU_BR]
        bleu_nb = sigma_score[cst.BLEU_NB]
        alpha = sigma_score[cst.ALPHA]
        sigma = sigma_score[cst.SIGMA]
        if cst.BLEU_BR in results:
            results[cst.BLEU_BR].append(bleu_br)
        if cst.BLEU_NB in results:
            results[cst.BLEU_NB].append(bleu_nb)
        if cst.ALPHA in results:
            results[cst.ALPHA].append(alpha)
        if cst.SIGMA in results:
            results[cst.SIGMA].append(sigma)

    if cst.TER_BR in results:
        ter_br = ter_process(ref_file_path, sys_file_path, srt=srt).score
        results[cst.TER_BR].append(ter_br)

    if cst.PRECISION in results or cst.RECALL in results or cst.F1 in results:
        precision, recall, f1 = f1_process(ref_file_path, sys_file_path, cst.NEUTRAL_TAG, srt=srt,
                                           line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG)
        if cst.PRECISION in results:
            results[cst.PRECISION].append(precision)
        if cst.RECALL in results:
            results[cst.RECALL].append(recall)
        if cst.F1 in results:
            results[cst.F1].append(f1)


def run_evaluations(ref_file_path, sys_file_paths, results, window_size=None, nt=cst.DEFAULT_NT, max_cpl=cst.MAX_CPL,
                    srt=False):

    for sys_file_path in sys_file_paths:
        run_evaluation(ref_file_path, sys_file_path, results, window_size=window_size, nt=nt, max_cpl=max_cpl, srt=srt)

## MAIN  #######################################################################

def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--all', '-a', action='store_true',
                        help="Compute all metrics.")
    parser.add_argument('--standard', '-std', action='store_true',
                        help="Compute all metrics that require identical text.")
    parser.add_argument('--end2end', '-e2e', action='store_true',
                        help="Compute all metrics that do not require identical text.")
    parser.add_argument('--include', '-i', type=str, nargs='+',
                        help="Compute only these metrics.")
    parser.add_argument('--exclude', '-e', type=str, nargs='+',
                        help="Compute all but these metrics.")

    parser.add_argument('--system_files', '-sys', type=str, nargs='+',
                        default=[cst.CASCADE_FR, cst.E2E_BASE_FR, cst.E2E_PT_FR, cst.NMT_FR],
                        help="Segmented subtitle files to evaluate.")
    parser.add_argument('--reference_file', '-ref', type=str, default=cst.AMARA_FR,
                        help="Reference segmented subtitle file.")
    parser.add_argument('--results_file', '-res', type=str,
                        help="CSV file where to write the results.")

    parser.add_argument('--srt', '-srt', action='store_true',
                        help="Wether the subtitle files are in srt format.")

    parser.add_argument('--window_size', '-k', type=int,
                        help="Window size for the window-based segmentation evaluation.")
    parser.add_argument('--max_transpo', '-n', type=int, default=cst.DEFAULT_NT,
                        help="Maximum distance that can accounted as a transposition.")
    parser.add_argument('--max_cpl', '-cpl', type=int, default=cst.MAX_CPL,
                        help="Maximum allowed length for subtitle lines.")

    args = parser.parse_args()
    return args


def main(args):
    all_metrics = args.all
    standard_metrics = args.standard
    end2end_metrics = args.end2end
    included_metrics = args.include
    excluded_metrics = args.exclude
    if not all_metrics and not standard_metrics and not end2end_metrics and included_metrics is None and excluded_metrics is None:
        metrics = cst.DEFAULT_METRICS
    else:
        if standard_metrics:
            metrics = set(cst.STD_METRICS)
        elif end2end_metrics:
            metrics = set(cst.E2E_METRICS)
        else:
            metrics = set(cst.VALID_METRICS)

        if included_metrics is not None:
            metrics.intersection_update(included_metrics)
        if excluded_metrics is not None:
            metrics.difference_update(excluded_metrics)

    print('Computing the following metrics:', ', '.join(metrics))

    results = {metric: list() for metric in metrics}
    results[cst.SYSTEM] = list()
    # Window size is saved if Pk or WindowDiff is computed
    if cst.PK in results or cst.WIN_DIFF in results:
        results[cst.WIN_SIZE] = list()
    # Transposition span is saved if SegSim or BoundSim is computed
    if cst.SEG_SIM in results or cst.BOUND_SIM in results:
        results[cst.NT] = list()
    # Boundaries to words ratio (alpha) is saved if Sigma is computed
    if cst.SIGMA in results:
        results[cst.ALPHA] = list()

    sys_file_paths = args.system_files
    ref_file_path = args.reference_file
    res_file_path = args.results_file
    srt = args.srt
    window_size = args.window_size
    nt = args.max_transpo
    max_cpl = args.max_cpl

    run_evaluations(ref_file_path, sys_file_paths, results, window_size=window_size, nt=nt, max_cpl=max_cpl, srt=srt)

    # Write to csv file
    print('Writing results to csv file:', res_file_path)
    df = pd.DataFrame.from_dict(results)
    with open(res_file_path, 'w') as out:
        df.to_csv(out, index=False, header=True)


if __name__ == '__main__':
    main(parse_args())