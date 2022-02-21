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
Computes TER_br with and without replacement of type of breaks
"""

import os
import re
import sys

from sacrebleu.metrics import TER

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst
from evalsub.util.util import preprocess


def ter_preprocess(infile, remove_eol=False, remove_eob=False, replace=False):
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
    masked_sents = [re.sub(r"[^ %s%s]+" % (cst.LINE_HOLDER, cst.CAPTION_HOLDER), cst.MASK_CHAR, tagged_sent) for tagged_sent in tagged_sents]

    return masked_sents


def calculate_ter(sys, ref):
    # Calculates TER between masked system output and masked reference
    ref1 = [ref]
    ter = TER()
    ter_score = ter.corpus_score(sys, ref1)
    signature = ter.get_signature()
    return ter_score, signature


def ter_process(reference_file, system_file, extra=False):
    ter = TER()

    ref = ter_preprocess(reference_file)
    sys = ter_preprocess(system_file)

    ter_score = ter.corpus_score(sys, [ref])
    signature = ter.get_signature()

    if extra:
        print('TER score on masked text:', ter_score)

    print(signature)
    return ter_score

