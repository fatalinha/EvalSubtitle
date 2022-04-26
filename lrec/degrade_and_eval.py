#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

""" Script to replicate Experiment 1 from the LREC paper
 Evaluating Subtitle Segmentation for End-to-end Generation Systems. """


import argparse
import os
import sys

import pandas as pd

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

from evalsub_main import run_evaluation
import evalsub.util.constants as cst
from evalsub.util.degrade_tags import shift, add, delete, replace


OUT_DIR_PATH = '.'


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--output_dir', '-od', type=str, default=OUT_DIR_PATH,
                        help="Path to save the degraded files")
    parser.add_argument('--reference_file', '-ref', type=str, default=cst.AMARA_EN,
                        help="The file to be degraded")
    parser.add_argument('--results_file', '-res', type=str, required=True,
                        help="csv file to write the metric scores")
    parser.add_argument('--no_ter', '-nter', action='store_true',
                        help="Skip the computation of TER_br")
    parser.add_argument('--with_respect_to', '-wrt', type=str, choices=['n_bound', 'n_spaces'], default='n_bound',
                        help="whether proportions are relative to the number of boundaries or to the number of free slots (spaces)")

    args = parser.parse_args()
    return args


def main(args):
    out_dir_path = args.output_dir
    ref_file_path = args.reference_file
    res_file_path = args.results_file
    no_ter = args.no_ter
    wrt_n_boundaries = args.with_respect_to == 'n_bound'

    # Init dictionary to store metrics
    eval_metrics = {cst.SYSTEM: list(), 'Mode': list(), 'NU': list(), 'P': list(), 'Change': list(),
                    cst.WIN_SIZE: list(), cst.PK: list(), cst.WIN_DIFF: list(),
                    cst.PRECISION: list(), cst.RECALL: list(), cst.F1: list(),
                    cst.BLEU_BR: list(),
                    cst.CPL_CONF: list(),
                    cst.SEG_SIM: list(), cst.BOUND_SIM: list()}

    if not no_ter:
        eval_metrics[cst.TER_BR] = list()

    # start degrading
    print('Start degrading files.')
    for mode in ['shift', 'add', 'delete', 'replace']:
        print('Mode: ' + mode)
        # directory for each mode of degradation
        outpath = os.path.join(out_dir_path, mode)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

        if mode == 'shift':
            # step size of shift
            for nu in range(1, 4):
                for peo in range(20, 120, 20):
                    eval_metrics['Mode'].append(mode)
                    eval_metrics['P'].append(peo)
                    eval_metrics['NU'].append(nu)
                    degraded_file = os.path.join(outpath, '.'.join(['amara', mode, str(nu), str(peo)]))
                    print('Degraded file: ' + str(degraded_file))
                    prob_eo = peo / 100

                    stats = shift(ref_file_path, degraded_file, nu, prob_eo, prob_eo, line_tag=cst.LINE_TAG,
                                  caption_tag=cst.CAPTION_TAG)

                    # Collect the stats to compute the rate of change
                    n_eol, n_eob, n_eol_shifts, n_eob_shifts = stats[0], stats[1], stats[2], stats[3]
                    rate_eol = n_eol_shifts / n_eol
                    rate_eob = n_eob_shifts / n_eob
                    rate_change = nu * (peo * rate_eol + peo * rate_eob)
                    eval_metrics['Change'].append(round(rate_change, 3))
                    # Evaluate the degraded files with the metrics
                    run_evaluation(ref_file_path, degraded_file, eval_metrics)
        else:
            for peo in range(20, 120, 20):
                eval_metrics['Mode'].append(mode)
                eval_metrics['P'].append(peo)
                degraded_file = os.path.join(outpath, '.'.join(['amara', mode, str(peo)]))
                print('Degraded file: ' + str(degraded_file))
                prob_eo = peo / 100  # Probability as float

                if mode == 'add':
                    eval_metrics['NU'].append(0)
                    if not wrt_n_boundaries:
                        prob_eo /= 2
                    stats = add(ref_file_path, degraded_file, prob_eo, prob_eo, line_tag=cst.LINE_TAG,
                                caption_tag=cst.CAPTION_TAG, wrt_n_boundaries=wrt_n_boundaries)
                elif mode == 'delete':
                    eval_metrics['NU'].append(0)
                    stats = delete(ref_file_path, degraded_file, prob_eo, prob_eo, line_tag=cst.LINE_TAG,
                                   caption_tag=cst.CAPTION_TAG)
                elif mode == 'replace':
                    eval_metrics['NU'].append(0)
                    stats = replace(ref_file_path, degraded_file, prob_eo, prob_eo, line_tag=cst.LINE_TAG,
                                    caption_tag=cst.CAPTION_TAG)
                # Collect the stats to compute the rate of change
                n_eol, n_eob, n_eol_change, n_eob_change = stats
                rate_eol = n_eol_change / n_eol
                rate_eob = n_eob_change / n_eob
                rate_change = (peo * rate_eol + peo * rate_eob)
                eval_metrics['Change'].append(round(rate_change, 3))
                # Evaluate the degraded files with the metrics
                run_evaluation(ref_file_path, degraded_file, eval_metrics)

    # Write to csv file
    print('Writing results to csv file:', res_file_path)
    df = pd.DataFrame.from_dict(eval_metrics)
    with open(res_file_path, 'w') as out:
        df.to_csv(out, index=False, header=True)


if __name__ == '__main__':
    main(parse_args())