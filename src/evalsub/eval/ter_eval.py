# coding: utf-8

DESCRIPTION = """
Computes TER_br with and without replacement of type of breaks
"""

import re

from sacrebleu.metrics import TER

from evalsub.util.util import preprocess


MASK_CHAR = '#'
LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'
LINE_HOLDER = 'µ'
CAPTION_HOLDER = '§'


def ter_preprocess(infile, remove_eol=False, remove_eob=False, replace=False):
    tagged_txt = preprocess(infile, line_tag=LINE_TAG, caption_tag=CAPTION_TAG, line_holder=LINE_HOLDER,
                            caption_holder=CAPTION_HOLDER)
    if remove_eol:
        tagged_txt = re.sub(LINE_HOLDER, r" ", tagged_txt)
    if remove_eob:
        tagged_txt = re.sub(CAPTION_HOLDER, r" ", tagged_txt)
    if replace:
        tagged_txt = re.sub(LINE_HOLDER, CAPTION_HOLDER, tagged_txt)

    # Inserting spaces besides boundaries
    tagged_txt = re.sub(r"(%s|%s)" % (LINE_HOLDER, CAPTION_HOLDER), r" \1 ", tagged_txt)
    # Removing potential multiple spaces
    tagged_txt = re.sub(r" {2,}", r" ", tagged_txt)

    tagged_sents = tagged_txt.splitlines()
    tagged_sents = [tagged_sent.strip() for tagged_sent in tagged_sents]
    masked_sents = [re.sub(r"[^ %s%s]+" % (LINE_HOLDER, CAPTION_HOLDER), MASK_CHAR, tagged_sent) for tagged_sent in tagged_sents]

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

