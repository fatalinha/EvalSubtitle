#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

""" Script to replicate Experiment 2 from the LREC paper
 Evaluating Subtitle Segmentation for End-to-end Generation Systems. """

import argparse
from math import exp, log
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

from evalsub.eval.bleu_eval import bleu_process
import evalsub.util.constants as cst
from evalsub.util.degrade_tags import mixed as mixed_tags
from evalsub.util.degrade_txt import mixed as mixed_txt

OUT_DIR_PATH = 'mixed'


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--output_dir', '-od', type=str, default=OUT_DIR_PATH,
                        help="Path to save the degraded files.")
    parser.add_argument('--reference_file', '-ref', type=str, default=cst.AMARA_EN,
                        help="The reference file against which to compute BLEU.")
    parser.add_argument('--results_file', '-res', type=str, required=True,
                        help="csv file to write the metric scores.")

    args = parser.parse_args()
    return args


def main(args):
    out_dir_path = args.output_dir
    ref_file_path = args.reference_file
    res_file_path = args.results_file

    if not os.path.exists(out_dir_path):
        os.makedirs(out_dir_path)

    # Init dictionary to store metrics
    eval_metrics = {cst.SYSTEM: list(),
                    cst.P_TXT: list(), cst.P_TAGS: list(),
                    cst.ALPHA: list(),
                    cst.BLEU_NB: list(),
                    cst.P1: list(), cst.P2: list(), cst.P3: list(), cst.P4: list(), cst.BP: list(),
                    cst.BLEU_BR: list(),
                    cst.PP1: list(), cst.PP2: list(), cst.PP3: list(), cst.PP4: list(), cst.BPP: list(),
                    cst.BLEU_BR_UB: list(),
                    cst.PP1_UB: list(), cst.PP2_UB: list(), cst.PP3_UB: list(), cst.PP4_UB: list(),
                    cst.SIGMA: list()
                    }

    for p_txt in range(0, 100, 10):
        p_add = p_del = p_rep = p_txt / 300
        mixed_txt_file_path = os.path.join(out_dir_path, "amara.mixed_txt.%d.txt" % p_txt)
        n_words = mixed_txt(ref_file_path, mixed_txt_file_path, p_add, p_del, p_rep)

        for p_tags in range(0, 100, 10):
            system = "mixed.%d.%d" % (p_txt, p_tags)
            p_eol_add = p_eol_del = p_eol_rep = p_tags / 300
            p_eob_add = p_eob_del = p_eob_rep = p_tags / 300
            mixed_tags_file_path = os.path.join(out_dir_path, "amara.%s.txt" % system)
            n_eol, n_eob = mixed_tags(mixed_txt_file_path, mixed_tags_file_path, p_eol_add,
                                      p_eob_add, p_eol_del, p_eob_del, p_eol_rep, p_eob_rep)

            n_boundaries = n_eol + n_eob
            alpha = n_boundaries / n_words

            bleu_nb_score = bleu_process(ref_file_path, mixed_tags_file_path, no_break=True)
            bleu_nb = bleu_nb_score.score
            p1, p2, p3, p4 = bleu_nb_score.precisions
            bp = bleu_nb_score.bp

            bleu_br_score = bleu_process(ref_file_path, mixed_tags_file_path)
            bleu_br = bleu_br_score.score
            pp1, pp2, pp3, pp4 = bleu_br_score.precisions
            bpp = bleu_br_score.bp

            pp1_ub = (p1 + alpha * 100) / (1 + alpha)
            pp2_ub = ((1 - alpha) * p2 + 2 * alpha * p1) / (1 + alpha)
            pp3_ub = ((1 - 2 * alpha) * p3 + 3 * alpha * p2) / (1 + alpha)
            pp4_ub = ((1 - 3 * alpha) * p4 + 4 * alpha * p3) / (1 + alpha)
            bleu_br_ub = bpp * exp((log(pp1_ub) + log(pp2_ub) + log(pp3_ub) + log(pp4_ub)) / 4)

            s = bleu_br / bleu_br_ub

            eval_metrics[cst.SYSTEM].append(system)
            eval_metrics[cst.P_TXT].append(p_txt)
            eval_metrics[cst.P_TAGS].append(p_tags)
            eval_metrics[cst.ALPHA].append(alpha)
            eval_metrics[cst.BLEU_NB].append(bleu_nb)
            eval_metrics[cst.P1].append(p1)
            eval_metrics[cst.P2].append(p2)
            eval_metrics[cst.P3].append(p3)
            eval_metrics[cst.P4].append(p4)
            eval_metrics[cst.BP].append(bp)
            eval_metrics[cst.BLEU_BR].append(bleu_br)
            eval_metrics[cst.PP1].append(pp1)
            eval_metrics[cst.PP2].append(pp2)
            eval_metrics[cst.PP3].append(pp3)
            eval_metrics[cst.PP4].append(pp4)
            eval_metrics[cst.BPP].append(bpp)
            eval_metrics[cst.BLEU_BR_UB].append(bleu_br_ub)
            eval_metrics[cst.PP1_UB].append(pp1_ub)
            eval_metrics[cst.PP2_UB].append(pp2_ub)
            eval_metrics[cst.PP3_UB].append(pp3_ub)
            eval_metrics[cst.PP4_UB].append(pp4_ub)
            eval_metrics[cst.SIGMA].append(s)

    # Write to csv file
    print('Writing results to csv file:', res_file_path)
    df = pd.DataFrame.from_dict(eval_metrics)
    with open(res_file_path, 'w') as out:
        df.to_csv(out, index=False, header=True)

    # plot Sigma
    s_plot = pd.DataFrame(eval_metrics[cst.SIGMA], index=df[cst.SYSTEM])
    s_plot.plot(kind="bar")
    plt.xlabel(cst.SYSTEM)
    plt.ylabel(cst.SIGMA)
    plt.show()


if __name__ == '__main__':
    main(parse_args())