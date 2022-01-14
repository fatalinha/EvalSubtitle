# coding: utf-8

import os
import re


LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'
LINE_HOLDER = 'µ'
CAPTION_HOLDER = '§'


def preprocess(input_file_path, line_tag=LINE_TAG, caption_tag=CAPTION_TAG, line_holder=LINE_HOLDER,
               caption_holder=CAPTION_HOLDER):
    r"""
    Preprocess the text from a tagged txt file.

    Removing potential multiple spaces.
    Removing potential spaces in the beginning of file lines.
    Removing spaces besides boundaries.
    Replacing boundaries with 1-char placeholders.

    Exple:

    INPUT - "The cat <eol> is black. <eob>\\nHe's sleeping. <eob>\\n"
    OUTPUT - "The catµis black.§\\nHe's sleeping.§\\n"

    :param input_file_path: tagged txt file
    :param line_tag: end-of-line tag
    :param caption_tag: end-of-bloc/caption tag
    :param line_holder: placeholder for end-of-line tag
    :param caption_holder: placeholder for end-of-bloc/caption tag
    :return: Preprocessed string
    """
    tagged_txt = open(input_file_path).read()
    # Removing potential multiple spaces
    tagged_txt = re.sub(r" {2,}", r" ", tagged_txt)
    # Removing potential spaces in the beginning of file lines
    tagged_txt = re.sub(r"\n ", r"\n", tagged_txt)
    # Removing spaces besides boundaries
    tagged_txt = re.sub(r"( )?(%s|%s)( )?" % (line_tag, caption_tag), r"\2", tagged_txt)
    # Replacing boundaries with 1-char placeholders
    tagged_txt = re.sub(line_tag, line_holder, tagged_txt)
    tagged_txt = re.sub(caption_tag, caption_holder, tagged_txt)

    return tagged_txt


def write_lines(lines, file_path, newline=True, add=False, make_dir=True, convert=False):
    mode = 'a' if add else 'w'
    if make_dir:
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
    if convert:
        lines = map(str, lines)
    if newline:
        lines = map(lambda l: l + '\n', lines)
    with open(file_path, mode) as file:
        file.writelines(lines)