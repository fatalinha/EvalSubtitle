#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import random
import os
import re
import sys

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst
from evalsub.util.util import postprocess, preprocess, replace_char, replace_substring

## MIXED  ######################################################################

def mixed(input_file_path, output_file_path, p_add, p_del, p_rep, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG):
    print('Initializing...')
    tagged_txt = preprocess(input_file_path, line_tag=line_tag, caption_tag=caption_tag)

    words = set(re.finditer(r"[^ %s%s\r\n]+" % (cst.LINE_HOLDER, cst.CAPTION_HOLDER), tagged_txt))
    space_positions = [m.start() for m in re.finditer(r" ", tagged_txt)]

    n_words = len(words)

    # n_word_shifts = round(p_shift * n_words)
    n_word_additions = round(p_add * n_words)
    n_word_deletions = round(p_del * n_words)
    n_word_replacements = round(p_rep * n_words)

    # Sampling the words to delete
    words_to_delete = random.sample(words, n_word_deletions)
    words.difference_update(words_to_delete)

    # Sampling the words to replace
    words_to_replace = random.sample(words, n_word_replacements)

    # Sampling the words to add
    words_to_add = random.sample(space_positions, n_word_additions)

    # Deleting words
    for word in words_to_delete:
        tagged_txt = replace_substring(tagged_txt, word.start(), word.end(), (word.end() - word.start()) * ' ')

    # Replacing words
    for word in words_to_replace:
        tagged_txt = replace_substring(tagged_txt, word.start(), word.end(), (word.end() - word.start()) * 'x')

    # Adding words
    for word_pos in words_to_add:
        tagged_txt = replace_char(tagged_txt, word_pos, cst.MASK_CHAR)

    # Inserting spaces besides masked chars
    tagged_txt = re.sub(cst.MASK_CHAR, r" %s " % cst.MASK_CHAR, tagged_txt)

    print('Writing ' + output_file_path)
    postprocess(tagged_txt, output_file_path, line_tag=line_tag, caption_tag=caption_tag)

    n_words += n_word_additions
    n_words -= n_word_deletions
    return n_words