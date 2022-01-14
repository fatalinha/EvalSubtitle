# coding: utf-8

import random
import re

from .util import postprocess, preprocess, replace_char, replace_substring


MASK_CHAR = '#'
LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'
LINE_HOLDER = 'µ'
CAPTION_HOLDER = '§'

## MIXED  ######################################################################

def mixed(input_file_path, output_file_path, p_add, p_del, p_rep, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):
    print('Initializing...')
    tagged_txt = preprocess(input_file_path, line_tag=line_tag, caption_tag=caption_tag)

    words = set(re.finditer(r"[^ %s%s\r\n]+" % (LINE_HOLDER, CAPTION_HOLDER), tagged_txt))
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
        tagged_txt = replace_char(tagged_txt, word_pos, MASK_CHAR)

    # Inserting spaces besides masked chars
    tagged_txt = re.sub(MASK_CHAR, r" \1 ", tagged_txt)

    print('Writing...')
    postprocess(tagged_txt, output_file_path, line_tag=line_tag, caption_tag=caption_tag)