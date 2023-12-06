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

import numpy as np
from sacrebleu.metrics import BLEU
from sacrebleu.metrics.base import Score
from sacrebleu.tokenizers import tokenizer_13a
tokenizer = tokenizer_13a.Tokenizer13a()

# We include the path of the toplevel package in the system path,
# so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst
from evalsub.util.util import preprocess


def sigma_preprocess(file_path, srt=False):
    tagged_str = preprocess(file_path, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG, line_holder=cst.LINE_HOLDER,
                            caption_holder=cst.CAPTION_HOLDER, srt=srt)
    n_boundaries = len(list(re.finditer(r"%s|%s" % (cst.LINE_HOLDER, cst.CAPTION_HOLDER), tagged_str)))
    n_words = len(list(re.finditer(r"[^ %s%s\r\n]+" % (cst.LINE_HOLDER, cst.CAPTION_HOLDER), tagged_str)))

    alpha = n_boundaries / n_words

    # Removing boundaries
    string = re.sub(r"%s|%s" % (cst.LINE_HOLDER, cst.CAPTION_HOLDER), r" ", tagged_str)
    # Removing potential multiple spaces
    string = re.sub(r" {2,}", r" ", string)

    sents = string.splitlines()
    sents = [sent.strip() for sent in sents]

    # Inserting spaces around boundaries
    tagged_str = re.sub(r"(%s|%s)" % (cst.LINE_HOLDER, cst.CAPTION_HOLDER), r" \1 ", tagged_str)
    # Removing potential multiple spaces
    tagged_str = re.sub(r" {2,}", r" ", tagged_str)

    tagged_sents = tagged_str.splitlines()
    tagged_sents = [tagged_sent.strip() for tagged_sent in tagged_sents]

    assert len(sents) == len(tagged_sents)

    return alpha, sents, tagged_sents


def sigma(alpha, bleu_nb_score, bleu_br_score):
    p1, p2, p3, p4 = bleu_nb_score.precisions
    bleu_br = bleu_br_score.score
    bpp = bleu_br_score.bp

    pp1_ub = (p1 + alpha * 100) / (1 + alpha)
    pp2_ub = ((1 - alpha) * p2 + 2 * alpha * p1) / (1 + alpha)
    pp3_ub = ((1 - 2 * alpha) * p3 + 3 * alpha * p2) / (1 + alpha)
    pp4_ub = ((1 - 3 * alpha) * p4 + 4 * alpha * p3) / (1 + alpha)
    bleu_br_ub = bpp * exp((log(pp1_ub) + log(pp2_ub) + log(pp3_ub) + log(pp4_ub)) / 4)

    return Score("Sigma", 100 * bleu_br / bleu_br_ub)


def __bs_idxs(size, n_samples=1000):
    """
    Samples `n_samples` sets of size `size` for bootstrap resampling.
    """
    seed = int(os.environ.get('BOOTSTRAP_RESAMPLE_SEED', '12345'))
    rng = np.random.default_rng(seed)
    return rng.choice(size, size=(n_samples, size), replace=True)


def sigma_process(ref_file_path, sys_file_path, srt=False, confidence_interval=False):
    bleu = BLEU()

    ref_alpha, ref_sents, ref_tagged_sents = sigma_preprocess(ref_file_path, srt=srt)
    sys_alpha, sys_sents, sys_tagged_sents = sigma_preprocess(sys_file_path, srt=srt)

    assert len(sys_sents) == len(ref_sents)

    bleu_nb_score = bleu.corpus_score(sys_sents, [ref_sents])
    bleu_br_score = bleu.corpus_score(sys_tagged_sents, [ref_tagged_sents])

    sigma_score = sigma(sys_alpha, bleu_nb_score, bleu_br_score)

    if confidence_interval:
        bleu_nb_stats = bleu._extract_corpus_statistics(sys_sents, [ref_sents])
        bleu_br_stats = bleu._extract_corpus_statistics(sys_tagged_sents, [ref_tagged_sents])
        idxs = __bs_idxs(len(bleu_nb_stats))

        # convert to numpy array. float32 is more efficient
        bleu_nb_stats_np = np.array(bleu_nb_stats, dtype='float32')
        bleu_br_stats_np = np.array(bleu_br_stats, dtype='float32')

        # recompute scores for all resamples
        bleu_nb_scores = [
            bleu._compute_score_from_stats(_s.sum(0)) for _s in bleu_nb_stats_np[idxs]]
        bleu_br_scores = [
            bleu._compute_score_from_stats(_s.sum(0)) for _s in bleu_br_stats_np[idxs]]
        sigma_scores = [
            sigma(sys_alpha, _bleu_nb, _bleu_br)
            for _bleu_nb, _bleu_br in zip(bleu_nb_scores, bleu_br_scores)]
        bleu_nb_score.estimate_ci(bleu_nb_scores)
        bleu_br_score.estimate_ci(bleu_br_scores)
        sigma_score.estimate_ci(sigma_scores)

    return {
        cst.SIGMA: sigma_score,
        cst.ALPHA: sys_alpha,
        cst.BLEU_NB: bleu_nb_score,
        cst.BLEU_BR: bleu_br_score}


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--system_file', '-sf', type=str)
    parser.add_argument('--reference_file', '-rf', type=str)

    args = parser.parse_args()
    return args


def main(args):
    sys_file_path = args.system_file
    ref_file_path = args.reference_file

    sigma_score = sigma_process(ref_file_path, sys_file_path)
    print(sigma_score)
    print(cst.SIGMA, "=", sigma_score[cst.SIGMA])


if __name__ == '__main__':
    main(parse_args())
