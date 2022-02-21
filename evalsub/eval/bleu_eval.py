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
Computes BLEU and the difference between BLEU with and without breaks
"""

import os
import re
import sys

from sacrebleu.metrics import BLEU

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst
from evalsub.util.util import preprocess


def bleu_preprocess(infile, remove_eol=False, remove_eob=False, replace=False):
    tagged_txt = preprocess(infile, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG, line_holder=cst.LINE_HOLDER,
                            caption_holder=cst.CAPTION_HOLDER)
    if remove_eol:
        tagged_txt = re.sub(cst.LINE_HOLDER, r" ", tagged_txt)
    if remove_eob:
        tagged_txt = re.sub(cst.CAPTION_HOLDER, r" ", tagged_txt)
    if replace:
        tagged_txt = re.sub(cst.LINE_HOLDER, cst.CAPTION_HOLDER, tagged_txt)

    # Inserting spaces besides boundaries
    tagged_txt = re.sub(r"(%s|%s)" % (cst.LINE_HOLDER, cst.CAPTION_HOLDER), r" \1 ", tagged_txt)
    # Removing potential multiple spaces
    tagged_txt = re.sub(r" {2,}", r" ", tagged_txt)

    tagged_sents = tagged_txt.splitlines()
    tagged_sents = [tagged_sent.strip() for tagged_sent in tagged_sents]

    return tagged_sents


def calculate_bleu(sys, ref):
    ref1 = [ref]
    bleu = BLEU()
    bleu_score = bleu.corpus_score(sys, ref1)
    signature = bleu.get_signature()
    return bleu_score, signature


def bleu_process(reference_file, system_file, extra=False, no_break=False):
    bleu = BLEU()

    ref = bleu_preprocess(reference_file, remove_eol=no_break, remove_eob=no_break)
    sys = bleu_preprocess(system_file, remove_eol=no_break, remove_eob=no_break)

    bleu_score = bleu.corpus_score(sys, [ref])
    signature = bleu.get_signature()

    if extra:
        # remove breaks
        ref_nb = bleu_preprocess(reference_file, remove_eol=True, remove_eob=True)
        sys_nb = bleu_preprocess(system_file, remove_eol=True, remove_eob=True)
        score_nobreak = bleu.corpus_score(sys_nb, [ref_nb])

        bleu_diff = score_nobreak.score - bleu_score.score

        # remove blocks
        ref_nb = bleu_preprocess(reference_file, remove_eob=True)
        sys_nb = bleu_preprocess(system_file, remove_eob=True)
        score_eol = bleu.corpus_score(sys_nb, [ref_nb])

        # remove lines
        ref_nb = bleu_preprocess(reference_file, remove_eol=True)
        sys_nb = bleu_preprocess(system_file, remove_eol=True)
        score_eob = bleu.corpus_score(sys_nb, [ref_nb])

        # replace with the same break
        ref_nb = bleu_preprocess(reference_file, replace=True)
        sys_nb = bleu_preprocess(system_file, replace=True)
        score_same = bleu.corpus_score(sys_nb, [ref_nb])

        print('BLEU with breaks:', bleu_score)
        print('BLEU regardless of type of break:', score_same)
        print('BLEU without breaks:', score_nobreak)
        print('BLEU only eol:', score_eol)
        print('BLEU only eob:', score_eob)
        print('BLEU difference without-with:', bleu_diff)

    print(signature)
    return bleu_score