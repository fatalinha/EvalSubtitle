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

TOP_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR_PATH = os.path.join(TOP_DIR_PATH, 'data')
AMARA_EN = os.path.join(DATA_DIR_PATH, 'amara.en')
AMARA_FR = os.path.join(DATA_DIR_PATH, 'amara.fr')
CASCADE_FR = os.path.join(DATA_DIR_PATH, 'cascade.fr')
E2E_BASE_FR = os.path.join(DATA_DIR_PATH, 'e2e_base.fr')
E2E_PT_FR = os.path.join(DATA_DIR_PATH, 'e2e_pt.fr')
NMT_FR = os.path.join(DATA_DIR_PATH, 'nmt.fr')

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
BLEU_NB = 'BLEU_nb'
TER_BR = 'TER_br'
LENGTH = 'Length'
SIGMA = 'Sigma'

VALID_METRICS = [PRECISION, RECALL, F1,
                 PK, WIN_DIFF,
                 SEG_SIM, BOUND_SIM,
                 BLEU_BR, BLEU_NB, TER_BR,
                 LENGTH,
                 SIGMA]

E2E_METRICS = [BLEU_BR, BLEU_NB, TER_BR,
               LENGTH,
               SIGMA]

# DEFAULT_METRICS = [BLEU_BR, BLEU_NB,
#                    SIGMA]

DEFAULT_METRICS = [BLEU_BR]

SYSTEM = 'System'
WIN_SIZE = 'WinSize'
ALPHA = 'Alpha'
BLEU_BR_UB = 'BLEU_br+'
PP1_UB = "p'1+"
PP2_UB = "p'2+"
PP3_UB = "p'3+"
PP4_UB = "p'4+"