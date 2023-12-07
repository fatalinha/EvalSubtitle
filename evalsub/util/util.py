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

import suber.data_types as subertyp
from suber.hyp_to_ref_alignment import levenshtein_align_hypothesis_to_reference
from suber.utilities import segment_to_string

# We include the path of the toplevel package in the system path,
# so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst
import evalsub.util.srt as utl_srt
import evalsub.util.ttml as utl_ttml


def get_masses(file_path, srt=False, ttml=False, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG):
    """
    Get the segmentation masses from a segmented subtitle file.

    :param file_path: segmented subtitle file (ttml or tagged text)
    :param srt: whether file_path is in srt format
    :param ttml: whether file_path is in ttml format
    :param line_tag: end of line boundary tag
    :param caption_tag: end of caption/block boundary tag
    :return: segmentation masses (segeval.BoundaryFormat.mass format)
    """
    if ttml:
        tagged_str, _ = utl_ttml.ttml_to_tagged_str(file_path, line_tag=line_tag, caption_tag=caption_tag)
    elif srt:
        tagged_str, _ = utl_srt.srt_to_tagged_str(file_path, line_tag=line_tag, caption_tag=caption_tag)
    else:
        tagged_str = ' '.join([line.strip() for line in open(file_path).readlines()])

    # Quick pre-processing before splitting
    # Removing (potential) multiple spaces
    tagged_str = re.sub(r" {2,}", r" ", tagged_str)
    # Removing spaces around boundaries
    tagged_str = re.sub(r"( )?(%s|%s)( )?" % (line_tag, caption_tag), r"\2", tagged_str)
    # Removing (potential) ending boundary
    tagged_str = re.sub(r"%s$" % caption_tag, r"", tagged_str)

    # <eob> only segmentation
    eob_str = re.sub(line_tag, r" ", tagged_str)
    eob_masses = [len(segment.split()) for segment in eob_str.split(caption_tag)]
    # <eol> only segmentation
    eol_str = re.sub(caption_tag, r" ", tagged_str)
    eol_masses = [len(segment.split()) for segment in eol_str.split(line_tag)]
    # <eox> (<eol> = <eob>) segmentation
    eox_str = re.sub(caption_tag, line_tag, tagged_str)
    eox_masses = [len(segment.split()) for segment in eox_str.split(line_tag)]

    return eob_masses, eol_masses, eox_masses


def postprocess(tagged_str, output_file_path, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG,
                line_holder=cst.LINE_HOLDER, caption_holder=cst.CAPTION_HOLDER):
    # Replacing 1-char placeholders with boundaries
    tagged_str = re.sub(line_holder, line_tag, tagged_str)
    tagged_str = re.sub(caption_holder, caption_tag, tagged_str)
    # Inserting spaces besides boundaries
    tagged_str = re.sub(r"(%s|%s)" % (line_tag, caption_tag), r" \1 ", tagged_str)
    # Removing potential multiple spaces
    tagged_str = re.sub(r" {2,}", r" ", tagged_str)
    # Segmenting in file lines
    tagged_lines = [line.strip() for line in tagged_str.splitlines()]
    # Writing
    write_lines(tagged_lines, output_file_path)


def preprocess(input_file_path, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG, line_holder=cst.LINE_HOLDER,
               caption_holder=cst.CAPTION_HOLDER, srt=False):
    r"""
    Preprocess the text from a tagged txt or srt file.

    Removing potential multiple spaces.
    Removing potential spaces in the beginning of file lines.
    Removing spaces around boundaries.
    Replacing boundaries with 1-char placeholders.

    Exple:

    INPUT - "The cat <eol> is black. <eob>\\nHe's sleeping. <eob>\\n"
    OUTPUT - "The catµis black.§\\nHe's sleeping.§\\n"

    :param input_file_path: input file
    :param line_tag: end-of-line tag
    :param caption_tag: end-of-bloc/caption tag
    :param line_holder: placeholder for end-of-line tag
    :param caption_holder: placeholder for end-of-bloc/caption tag
    :param srt: wether the input file is in srt format
    :return: Preprocessed string
    """
    if srt:
        tagged_sents, _ = utl_srt.srt_to_tagged_sents(input_file_path, line_tag=line_tag, caption_tag=caption_tag)
        tagged_str = '\n'.join(tagged_sents)
    else:
        tagged_str = open(input_file_path).read()

    # Removing potential multiple spaces
    tagged_str = re.sub(r" {2,}", r" ", tagged_str)
    # Removing potential spaces in the beginning of file lines
    tagged_str = re.sub(r"\n ", r"\n", tagged_str)
    # Removing spaces around boundaries
    tagged_str = re.sub(r"( )?(%s|%s)( )?" % (line_tag, caption_tag), r"\2", tagged_str)
    # Replacing boundaries with 1-char placeholders
    tagged_str = re.sub(line_tag, line_holder, tagged_str)
    tagged_str = re.sub(caption_tag, caption_holder, tagged_str)

    return tagged_str


def replace_char(string, pos, c):
    return string[:pos] + c + string[pos + 1:]


def replace_substring(string, start, end, substring):
    return string[:start] + substring + string[end:]


def suber_format(tagged_str, line_holder=cst.LINE_HOLDER, caption_holder=cst.CAPTION_HOLDER):
    # Inserting spaces besides 1-char placeholders
    tagged_str = re.sub(r"(%s|%s)" % (line_holder, caption_holder), r" \1 ", tagged_str)

    tagged_sents = tagged_str.splitlines()
    suber_segments = []
    for tagged_sent in tagged_sents:
        tokens = tagged_sent.split()
        token_list = []
        for token in tokens:
            if token in (line_holder, caption_holder):
                if not token_list:
                    continue  # ignore line break symbol at the start of the line
                else:
                    token_list[-1].line_break = (
                        subertyp.LineBreak.END_OF_BLOCK if token == caption_holder else subertyp.LineBreak.END_OF_LINE)
            else:
                token_list.append(subertyp.Word(string=token))

        suber_segments.append(subertyp.Segment(word_list=token_list))

    return suber_segments


def suber_auto_seg(ref_tagged_str, sys_tagged_str, line_holder=cst.LINE_HOLDER, caption_holder=cst.CAPTION_HOLDER):
    ref_suber_segments = suber_format(ref_tagged_str, line_holder=line_holder, caption_holder=caption_holder)
    sys_suber_segments = suber_format(sys_tagged_str, line_holder=line_holder, caption_holder=caption_holder)
    sys_suber_auto_segments = levenshtein_align_hypothesis_to_reference(hypothesis=sys_suber_segments,
                                                                        reference=ref_suber_segments)
    sys_tagged_str = "\n".join([segment_to_string(segment, include_line_breaks=True)
                                for segment in sys_suber_auto_segments])

    # Removing spaces around boundaries (it is important to keep cst.LINE_TAG and cst.CAPTION_TAG here)
    sys_tagged_str = re.sub(r"( )?(%s|%s)( )?" % (cst.LINE_TAG, cst.CAPTION_TAG), r"\2", sys_tagged_str)
    # Replacing boundaries with 1-char placeholders (it is important to keep cst.LINE_TAG and cst.CAPTION_TAG here)
    sys_tagged_str = re.sub(cst.LINE_TAG, line_holder, sys_tagged_str)
    sys_tagged_str = re.sub(cst.CAPTION_TAG, caption_holder, sys_tagged_str)

    return sys_tagged_str


def write_lines(lines, file_path, newline=True, add=False, make_dir=True, convert=False):
    mode = 'a' if add else 'w'
    if make_dir:
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
    if convert:
        lines = map(str, lines)
    if newline:
        lines = map(lambda line: line + '\n', lines)
    with open(file_path, mode) as file:
        file.writelines(lines)
