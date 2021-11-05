# coding: utf-8
#import sacrebleu
from sacrebleu.metrics import BLEU

DESCRIPTION = """Computes BLEU and the difference between BLEU with and without breaks"""

#reference_file = '/home/alin/Desktop/subtitling/02_data/Must-Cinema/en-fr/amara.en'#sys.argv[1]
#system_file = '/home/alin/Desktop/subtitling/03_scripts/EvalSub/02_contrastive_pairs/seq2seqSegmenter/generate-amara_en' #sys.argv[2]

def process_breaks(infile, remove_eol=False, remove_eob=False, replace=False):
    if remove_eol and not remove_eob:
        file = [line.strip().replace(' <eol>', '') for line in open(infile, 'r')]
    elif remove_eob and not remove_eol:
        file = [line.strip().replace(' <eob>', '') for line in open(infile, 'r')]
    elif remove_eob and remove_eol:
        file = [line.strip().replace(' <eol>', '').replace(' <eob>', '') for line in open(infile, 'r')]
    else:
        if replace:
            file = [line.strip().replace('<eol>', '<eob>') for line in open(infile, 'r')]
        else:
            file = [line.strip() for line in open(infile, 'r')]
    return file


def calculate_bleu(sys, ref):
    ref1 = [(ref)]
    bleu = BLEU()
    score = bleu.corpus_score(sys, ref1)
    signature = bleu.get_signature()
    return score, signature


def bleu_process(reference_file, system_file):

    ref = process_breaks(reference_file)
    sys = process_breaks(system_file)

    score, _ = calculate_bleu(sys, ref)

    # remove breaks
    ref_nb = process_breaks(reference_file, remove_eol=True, remove_eob=True)
    sys_nb = process_breaks(system_file, remove_eol=True, remove_eob=True)
    score_nobreak, _ = calculate_bleu(sys_nb, ref_nb)

    bleu_diff = float(str(score_nobreak).split(' ')[2])-float(str(score).split(' ')[2])

    # remove blocks
    ref_nb = process_breaks(reference_file, remove_eob=True)
    sys_nb = process_breaks(system_file,  remove_eob=True)
    score_eol, _ = calculate_bleu(sys_nb, ref_nb)

    # remove lines
    ref_nb = process_breaks(reference_file, remove_eol=True)
    sys_nb = process_breaks(system_file,  remove_eol=True)
    score_eob, _ = calculate_bleu(sys_nb, ref_nb)

    # replace with the same break
    ref_nb = process_breaks(reference_file, replace=True)
    sys_nb = process_breaks(system_file,  replace=True)
    score_same, signature = calculate_bleu(sys_nb, ref_nb)

    print('BLEU with breaks: ' + str(score) + '\n' +
          'BLEU regardless of type of break: ' + str(score_same) + '\n' +
          'BLEU without breaks: ' + str(score_nobreak) + '\n' +
          'BLEU only eol: ' + str(score_eol) + '\n' +
          'BLEU only eob: ' + str(score_eob) + '\n' +
          'BLEU difference without-with: ' + str(bleu_diff) + '\n' + str(_))
    bleu_only = str(score).split(' ')[2]
    return bleu_only



