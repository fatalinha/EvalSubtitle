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
import re
import sys

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst


def postprocess(tagged_txt, output_file_path, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG, line_holder=cst.LINE_HOLDER,
                caption_holder=cst.CAPTION_HOLDER):
    # Replacing 1-char placeholders with boundaries
    tagged_txt = re.sub(line_holder, line_tag, tagged_txt)
    tagged_txt = re.sub(caption_holder, caption_tag, tagged_txt)
    # Inserting spaces besides boundaries
    tagged_txt = re.sub(r"(%s|%s)" % (line_tag, caption_tag), r" \1 ", tagged_txt)
    # Removing potential multiple spaces
    tagged_txt = re.sub(r" {2,}", r" ", tagged_txt)
    # Segmenting in file lines
    tagged_txt = [line.strip() for line in tagged_txt.splitlines()]
    # Writing
    write_lines(tagged_txt, output_file_path)


def preprocess(input_file_path, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG, line_holder=cst.LINE_HOLDER,
               caption_holder=cst.CAPTION_HOLDER):
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


def replace_char(string, pos, c):
    return string[:pos] + c + string[pos + 1:]


def replace_substring(string, start, end, substring):
    return string[:start] + substring + string[end:]


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