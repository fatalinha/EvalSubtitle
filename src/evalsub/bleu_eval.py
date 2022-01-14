# coding: utf-8

DESCRIPTION = """
Computes BLEU and the difference between BLEU with and without breaks
"""

import re

from sacrebleu.metrics import BLEU

from util.util import preprocess

#reference_file = '/home/alin/Desktop/subtitling/02_data/Must-Cinema/en-fr/amara.en'#sys.argv[1]
#system_file = '/home/alin/Desktop/subtitling/03_scripts/EvalSub/02_contrastive_pairs/seq2seqSegmenter/generate-amara_en' #sys.argv[2]

LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'
LINE_HOLDER = 'µ'
CAPTION_HOLDER = '§'


def bleu_preprocess(infile, remove_eol=False, remove_eob=False, replace=False):
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

    return tagged_sents


def calculate_bleu(sys, ref):
    ref1 = [ref]
    bleu = BLEU()
    score = bleu.corpus_score(sys, ref1)
    signature = bleu.get_signature()
    return score, signature


def bleu_process(reference_file, system_file):

    ref = bleu_preprocess(reference_file)
    sys = bleu_preprocess(system_file)

    score, signature = calculate_bleu(sys, ref)

    # remove breaks
    ref_nb = bleu_preprocess(reference_file, remove_eol=True, remove_eob=True)
    sys_nb = bleu_preprocess(system_file, remove_eol=True, remove_eob=True)
    score_nobreak, _ = calculate_bleu(sys_nb, ref_nb)

    bleu_diff = score_nobreak.score - score.score

    # remove blocks
    ref_nb = bleu_preprocess(reference_file, remove_eob=True)
    sys_nb = bleu_preprocess(system_file, remove_eob=True)
    score_eol, _ = calculate_bleu(sys_nb, ref_nb)

    # remove lines
    ref_nb = bleu_preprocess(reference_file, remove_eol=True)
    sys_nb = bleu_preprocess(system_file, remove_eol=True)
    score_eob, _ = calculate_bleu(sys_nb, ref_nb)

    # replace with the same break
    ref_nb = bleu_preprocess(reference_file, replace=True)
    sys_nb = bleu_preprocess(system_file, replace=True)
    score_same, _ = calculate_bleu(sys_nb, ref_nb)

    print('BLEU with breaks:', score)
    print('BLEU regardless of type of break:', score_same)
    print('BLEU without breaks:', score_nobreak)
    print('BLEU only eol:', score_eol)
    print('BLEU only eob:', score_eob)
    print('BLEU difference without-with:', bleu_diff)
    print(signature)
    bleu_only = score.score
    return bleu_only