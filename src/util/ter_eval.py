# coding: utf-8
from sacrebleu.metrics import TER

DESCRIPTION = """Computes TER-br with and without replacement of type of breaks"""


def mask(infile, replace=False, remove_eol=False, remove_eob=False):
    # Masks all words with ****, returns masked file
    outlines = []
    with open(infile) as f:
        for line in f:
            if remove_eol and not remove_eob:
                line = line.replace(' <eol>','')
            elif remove_eob and not remove_eol:
                line = line.replace(' <eob>','')
            elif replace:
                line = line.replace('<eol>','<eob>')
            line = line.strip().split(' ')
            words = []
            for w in line:
                if w != '<eob>' and w != '<eol>':
                    words.append('****')
                else:
                    words.append(w)
            outlines.append(' '.join(words))
        return outlines


def calculate_ter(sys, ref):
    # Calculates TER between masked system output and masked reference
    ref1 = [(ref)]
    ter = TER()
    score = ter.corpus_score(sys, ref1)
    return score


def ter_process(reference_file, system_file):
    ref = mask(reference_file, replace=True)
    sys = mask(system_file, replace=True)
    ter_score = calculate_ter(sys, ref)
    print('TER score on masked text: ' + str(ter_score))
    return ter_score

