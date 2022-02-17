#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import argparse
from math import exp, log
import os
import re
import sys

from sacrebleu.metrics import BLEU

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

from evalsub.util.util import preprocess


LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'
LINE_HOLDER = 'µ'
CAPTION_HOLDER = '§'


def s_preprocess(file_path):
    tagged_txt = preprocess(file_path, line_tag=LINE_TAG, caption_tag=CAPTION_TAG, line_holder=LINE_HOLDER,
                            caption_holder=CAPTION_HOLDER)

    n_words = len(list(re.finditer(r"[^ %s%s\r\n]+" % (LINE_HOLDER, CAPTION_HOLDER), tagged_txt)))
    n_boundaries = len(list(re.finditer(r"%s|%s" % (LINE_HOLDER, CAPTION_HOLDER), tagged_txt)))
    alpha = n_boundaries / n_words

    # Removing boundaries
    txt = re.sub(r"%s|%s" % (LINE_HOLDER, CAPTION_HOLDER), r" ", tagged_txt)
    # Removing potential multiple spaces
    txt = re.sub(r" {2,}", r" ", txt)

    sents = txt.splitlines()
    sents = [sent.strip() for sent in sents]

    # Inserting spaces besides boundaries
    tagged_txt = re.sub(r"(%s|%s)" % (LINE_HOLDER, CAPTION_HOLDER), r" \1 ", tagged_txt)
    # Removing potential multiple spaces
    tagged_txt = re.sub(r" {2,}", r" ", tagged_txt)

    tagged_sents = tagged_txt.splitlines()
    tagged_sents = [tagged_sent.strip() for tagged_sent in tagged_sents]

    assert len(sents) == len(tagged_sents)

    return alpha, sents, tagged_sents


def s_process(ref_file_path, sys_file_path):
    bleu = BLEU()

    ref_alpha, ref_sents, ref_tagged_sents = s_preprocess(ref_file_path)
    sys_alpha, sys_sents, sys_tagged_sents = s_preprocess(sys_file_path)

    bleu_nb_score = bleu.corpus_score(sys_sents, [ref_sents])
    bleu_br_score = bleu.corpus_score(sys_tagged_sents, [ref_tagged_sents])

    alpha = sys_alpha
    p1, p2, p3, p4 = bleu_nb_score.precisions
    bleu_br = bleu_br_score.score
    bpp = bleu_br_score.bp

    pp1_ub = (p1 + alpha * 100) / (1 + alpha)
    pp2_ub = ((1 - alpha) * p2 + 2 * alpha * p1) / (1 + alpha)
    pp3_ub = ((1 - 2 * alpha) * p3 + 3 * alpha * p2) / (1 + alpha)
    pp4_ub = ((1 - 3 * alpha) * p4 + 4 * alpha * p3) / (1 + alpha)
    bleu_br_ub = bpp * exp((log(pp1_ub) + log(pp2_ub) + log(pp3_ub) + log(pp4_ub)) / 4)

    s = 100 * bleu_br / bleu_br_ub

    s_score = { "S": s,
                "alpha": alpha,
                "BLEU_br+": bleu_br_ub,
                "p'1+": pp1_ub,
                "p'2+": pp2_ub,
                "p'3+": pp3_ub,
                "p'4+": pp4_ub,
                "BLEU_nb": bleu_nb_score,
                "BLEU_br": bleu_br_score}

    return s_score


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--system_file', '-sf', type=str)
    parser.add_argument('--reference_file', '-rf', type=str)

    args = parser.parse_args()
    return args


def main(args):
    sys_file_path = args.system_file
    ref_file_path = args.reference_file

    s_score = s_process(ref_file_path, sys_file_path)
    print("S = ", s_score["S"])


if __name__ == '__main__':
    main(parse_args())