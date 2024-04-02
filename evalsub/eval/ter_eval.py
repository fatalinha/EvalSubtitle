#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import os
import re
import sys

from sacrebleu.metrics import TER

# We include the path of the toplevel package in the system path,
# so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst
from evalsub.util.util import preprocess, suber_auto_seg

DESCRIPTION = """
Computes TER_br with and without replacement of type of breaks
"""


def ter_preprocess_aux(tagged_str, remove_eol=False, remove_eob=False, replace=False):
    if remove_eol:
        tagged_str = re.sub(cst.LINE_HOLDER, r" ", tagged_str)
    if remove_eob:
        tagged_str = re.sub(cst.CAPTION_HOLDER, r" ", tagged_str)
    if replace:
        tagged_str = re.sub(cst.LINE_HOLDER, cst.CAPTION_HOLDER, tagged_str)

    # Inserting spaces around boundaries
    tagged_str = re.sub(r"(%s|%s)" % (cst.LINE_HOLDER, cst.CAPTION_HOLDER), r" \1 ", tagged_str)
    # Removing potential multiple spaces
    tagged_str = re.sub(r" {2,}", r" ", tagged_str)

    tagged_sents = tagged_str.splitlines()
    tagged_sents = [tagged_sent.strip() for tagged_sent in tagged_sents]
    masked_sents = [re.sub(r"[^ %s%s]+" % (cst.LINE_HOLDER, cst.CAPTION_HOLDER), cst.MASK_CHAR, tagged_sent)
                    for tagged_sent in tagged_sents]

    return masked_sents


def ter_preprocess(ref_file_path, sys_file_path, srt=False, auto_seg=False):
    ref_tagged_str = preprocess(ref_file_path, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG,
                                line_holder=cst.LINE_HOLDER, caption_holder=cst.CAPTION_HOLDER, srt=srt)
    sys_tagged_str = preprocess(sys_file_path, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG,
                                line_holder=cst.LINE_HOLDER, caption_holder=cst.CAPTION_HOLDER, srt=srt)

    if auto_seg:
        sys_tagged_str = suber_auto_seg(ref_tagged_str, sys_tagged_str, line_holder=cst.LINE_HOLDER,
                                        caption_holder=cst.CAPTION_HOLDER, sys_file_path=sys_file_path)

    ref_sents = ter_preprocess_aux(ref_tagged_str)
    sys_sents = ter_preprocess_aux(sys_tagged_str)

    return ref_sents, sys_sents


def calculate_ter(sys, ref):
    # Calculates TER between masked system output and masked reference
    ref1 = [ref]
    ter = TER()
    ter_score = ter.corpus_score(sys, ref1)
    signature = ter.get_signature()
    return ter_score, signature


def ter_process(ref_file_path, sys_file_path, srt=False, auto_seg=False, extra=False):
    ter = TER()

    ref_sents, sys_sents = ter_preprocess(ref_file_path, sys_file_path, srt=srt, auto_seg=auto_seg)

    assert len(sys_sents) == len(ref_sents)

    ter_score = ter.corpus_score(sys_sents, [ref_sents])
    signature = ter.get_signature()

    if extra:
        print('TER score on masked text:', ter_score)

    print(signature)
    return ter_score
