# coding: utf-8

import argparse
import os
import pandas as pd

from run_eval import run_evaluation
from util.degrade_tagged_txt import shift, add, delete, replace


LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'
OUT_DIR_PATH = '/home/alin/Desktop/subtitling/03_scripts/EvalSub/02_contrastive_pairs/'
REF_FILE_PATH = '/home/alin/Desktop/subtitling/02_data/Must-Cinema/en-fr/amara.en'
RES_FILE_PATH = '/home/alin/Desktop/subtitling/03_scripts/EvalSub/03_results/results.csv'


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--output_dir', '-od', type=str, default=OUT_DIR_PATH)
    parser.add_argument('--reference_file', '-ref', type=str, default=REF_FILE_PATH)
    parser.add_argument('--results_file', '-res', type=str, default=RES_FILE_PATH)
    parser.add_argument('--no_ter', '-nter', action='store_true')

    args = parser.parse_args()
    return args


def main(args):
    out_dir_path = args.output_dir
    ref_file_path = args.reference_file
    res_file_path = args.results_file
    no_ter = args.no_ter


    # Init dictionary to store metrics
    eval_metrics = dict(System=[], Mode=[], NU=[], P=[], Change=[],
                        Win=[], Pk=[], WinDiff=[], Precision=[], Recall=[], F1=[],
                        BLEU=[], TER_br=[], Len=[], SegSim=[], BoundSim=[])

    # start degrading
    print('Start degrading files.')
    for mode in ['shift', 'add', 'delete', 'replace']: #'shift', 'add', 'delete',
        print('Mode: ' + mode)
        # new folder for each mode of degradation?
        outpath = os.path.join(out_dir_path, mode)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

        if mode == 'shift':
            for nu in range(1, 4):
                for peo in range(20, 120, 20):
                    eval_metrics['Mode'].append(mode)
                    eval_metrics['P'].append(peo)
                    eval_metrics['NU'].append(nu)
                    degraded_file = os.path.join(outpath, '.'.join(['amara', mode, str(nu), str(peo)]))
                    print('Degraded file: ' + str(degraded_file))
                    prob_eo = peo / 100  # Probability as float

                    stats = shift(ref_file_path, degraded_file, nu, prob_eo, prob_eo, line_tag=LINE_TAG,
                          caption_tag=CAPTION_TAG)

                    n_eol, n_eob, n_eol_shifts, n_eob_shifts = stats[0], stats[1], stats[2], stats[3]
                    rate_eol = n_eol_shifts / n_eol
                    rate_eob = n_eob_shifts / n_eob
                    rate_change = nu * (peo * rate_eol + peo * rate_eob)
                    eval_metrics['Change'].append(round(rate_change, 3))
                    # Evaluate the degraded files with the metrics
                    run_evaluation(ref_file_path, degraded_file, eval_metrics, no_ter=no_ter)
        else:
            for peo in range(20, 120, 20):
                eval_metrics['Mode'].append(mode)
                eval_metrics['P'].append(peo)
                degraded_file = os.path.join(outpath, '.'.join(['amara', mode, str(peo)]))
                print('Degraded file: ' + str(degraded_file))
                prob_eo = peo / 100  # Probability as float

                if mode == 'add':
                    eval_metrics['NU'].append(0)
                    stats = add(ref_file_path, degraded_file, prob_eo, prob_eo, line_tag=LINE_TAG,
                                  caption_tag=CAPTION_TAG)
                elif mode == 'delete':
                    eval_metrics['NU'].append(0)
                    stats = delete(ref_file_path, degraded_file, prob_eo, prob_eo, line_tag=LINE_TAG,
                                  caption_tag=CAPTION_TAG)
                elif mode == 'replace':
                    eval_metrics['NU'].append(0)
                    stats = replace(ref_file_path, degraded_file, prob_eo, prob_eo, line_tag=LINE_TAG,
                                   caption_tag=CAPTION_TAG)
                # Collect the stats to compute the rate of change
                n_eol, n_eob, n_eol_change, n_eob_change = stats
                rate_eol = n_eol_change / n_eol
                rate_eob = n_eob_change / n_eob
                rate_change = (peo * rate_eol + peo * rate_eob)
                eval_metrics['Change'].append(round(rate_change, 3))
                # Evaluate the degraded files with the metrics
                run_evaluation(ref_file_path, degraded_file, eval_metrics, no_ter=no_ter)

    # Write to csv file
    print('Writing results to csv file:', res_file_path)
    df = pd.DataFrame.from_dict(eval_metrics)
    with open(res_file_path, 'w') as out:
        df.to_csv(out, index=False, header=True)


if __name__ == '__main__':
    main(parse_args())