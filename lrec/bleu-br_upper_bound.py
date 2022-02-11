# coding: utf-8

import argparse
from math import exp, log
import os
import pandas as pd
import matplotlib.pyplot as plt

from src.evalsub.eval.bleu_eval import bleu_process
from src.evalsub.util.degrade_tagged_txt import mixed as mixed_tags
from src.evalsub.util.degrade_txt import mixed as mixed_txt


LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'
OUT_DIR_PATH = 'mixed'
REF_FILE_PATH = '../data/amara.en'
RES_FILE_PATH = 'results.csv'


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--output_dir', '-od', type=str, default=OUT_DIR_PATH,
                        help="Path to save the degraded files")
    parser.add_argument('--reference_file', '-ref', type=str, default=REF_FILE_PATH,
                        help="The reference file against which to compute BLEU")
    parser.add_argument('--results_file', '-res', type=str, default=RES_FILE_PATH,
                        help="csv file to write the metric scores")

    args = parser.parse_args()
    return args


def main(args):
    out_dir_path = args.output_dir
    ref_file_path = args.reference_file
    res_file_path = args.results_file

    if not os.path.exists(out_dir_path):
        os.makedirs(out_dir_path)

    # Init dictionary to store metrics
    eval_metrics = {"System": list(),
                    "p_txt": list(), "p_tags": list(),
                    "alpha": list(),
                    "BLEU_nb": list(), "p1": list(), "p2": list(), "p3": list(), "p4": list(), "bp": list(),
                    "BLEU_br": list(), "p'1": list(), "p'2": list(), "p'3": list(), "p'4": list(), "bp'": list(),
                    "BLEU_br+": list(), "p'1+": list(), "p'2+": list(), "p'3+": list(), "p'4+": list(),
                    "S": list()
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

            eval_metrics["System"].append(system)
            eval_metrics["p_txt"].append(p_txt)
            eval_metrics["p_tags"].append(p_tags)
            eval_metrics["alpha"].append(alpha)
            eval_metrics["BLEU_nb"].append(bleu_nb)
            eval_metrics["p1"].append(p1)
            eval_metrics["p2"].append(p2)
            eval_metrics["p3"].append(p3)
            eval_metrics["p4"].append(p4)
            eval_metrics["bp"].append(bp)
            eval_metrics["BLEU_br"].append(bleu_br)
            eval_metrics["p'1"].append(pp1)
            eval_metrics["p'2"].append(pp2)
            eval_metrics["p'3"].append(pp3)
            eval_metrics["p'4"].append(pp4)
            eval_metrics["bp'"].append(bpp)
            eval_metrics["BLEU_br+"].append(bleu_br_ub)
            eval_metrics["p'1+"].append(pp1_ub)
            eval_metrics["p'2+"].append(pp2_ub)
            eval_metrics["p'3+"].append(pp3_ub)
            eval_metrics["p'4+"].append(pp4_ub)
            eval_metrics["S"].append(s)

    # Write to csv file
    print('Writing results to csv file:', res_file_path)
    df = pd.DataFrame.from_dict(eval_metrics)
    with open(res_file_path, 'w') as out:
        df.to_csv(out, index=False, header=True)

    # plot Sigma
    s_plot = pd.DataFrame(eval_metrics["S"], index=df['System'])
    s_plot.plot(kind="bar")
    plt.xlabel("System")
    plt.ylabel("Sigma")
    plt.show()


if __name__ == '__main__':
    main(parse_args())
