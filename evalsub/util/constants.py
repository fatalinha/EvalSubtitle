# coding: utf-8

import os


REF_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'amara.en')

CAPTION_TAG = '<eob>'
LINE_TAG = '<eol>'
LINE_HOLDER = 'µ'
CAPTION_HOLDER = '§'
MASK_CHAR = '#'

PRECISION = 'Precision'
RECALL = 'Recall'
F1 = 'F1'
PK = 'Pk'
WIN_DIFF = 'WinDiff'
SEG_SIM = 'SegSim'
BOUND_SIM = 'BoundSim'
BLEU_BR = 'BLEU_br'
TER_BR = 'TER_br'
LENGTH = 'Length'

SYSTEM = 'System'
WIN_SIZE = 'WinSize'