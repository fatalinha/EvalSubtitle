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