# coding: utf-8

DESCRIPTION = """
A script to degrade subtitle segmentation (in lines and captions) in a tagged txt file.
The degradation can be achieved by shifting boundaries, adding new boundaries, deleting boundaries, or replacing
boundaries with the other type.
"""

import argparse
import random
import re

from .util import postprocess, preprocess, replace_char, write_lines


LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'
LINE_HOLDER = 'µ'
CAPTION_HOLDER = '§'

## SHIFT  ######################################################################

def shift_boundary(tagged_txt, n, slot_positions, i):
    # The boundary initial slot is filled with a space
    slot_pos = slot_positions[i]
    boundary = tagged_txt[slot_pos]
    tagged_txt = replace_char(tagged_txt, slot_pos, ' ')
    # The target slot is distant of n units
    # (either on the right or on the left, 50-50),
    # unless it crosses another boundary
    t = i
    step = random.randint(0, 1) * 2 - 1
    while 0 <= t < len(slot_positions) and tagged_txt[slot_positions[t]] == ' ' and abs(t - i) <= n :
        t += step
    # The boundary is reinserted in the target slot
    t -= step
    slot_pos = slot_positions[t]
    tagged_txt = replace_char(tagged_txt, slot_pos, boundary)

    return tagged_txt


def shift(input_file_path, output_file_path, n, p_eol, p_eob, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):
    """
    Degrade a tagged txt file by shifting some of its boundaries.

    :param input_file_path: initial tagged txt file
    :param output_file_path: degraded (shifts) tagged txt file
    :param n: number of units by which boundaries should be shifted
    :param p_eol: proportion of eol boundaries to be shifted
    :param p_eob: proportion of eob boundaries to be shifted
    :param line_tag: tag which represents an end-of-line in a caption (default '<eol>')
    :param caption_tag: tag which represents an end-of-caption (default '<eob>')
    """
    print('Initializing...')
    tagged_txt = preprocess(input_file_path, line_tag=line_tag, caption_tag=caption_tag)

    eol_positions = [m.start() for m in re.finditer(LINE_HOLDER, tagged_txt)]
    eob_positions = [m.start() for m in re.finditer(CAPTION_HOLDER, tagged_txt)]
    space_positions = [m.start() for m in re.finditer(r" ", tagged_txt)]

    n_eol = len(eol_positions)
    n_eob = len(eob_positions)
    n_eol_shifts = round(p_eol * n_eol)
    n_eob_shifts = round(p_eob * n_eob)
    print('n eol shifts:\n  %d (%.2f%%)' % (n_eol_shifts, 100 * n_eol_shifts / n_eol))
    print('n eob shifts:\n  %d (%.2f%%)' % (n_eob_shifts, 100 * n_eob_shifts / n_eob))
    eol_to_shift = random.sample(eol_positions, n_eol_shifts)
    eob_to_shift = random.sample(eob_positions, n_eob_shifts)
    boundaries_to_shift = frozenset(eol_to_shift + eob_to_shift)

    slot_positions = sorted(eol_positions + eob_positions + space_positions)

    for i, slot_pos in enumerate(slot_positions):
        if slot_pos in boundaries_to_shift:
            tagged_txt = shift_boundary(tagged_txt, n, slot_positions, i)

    print('Writing...')
    postprocess(tagged_txt, output_file_path, line_tag=line_tag, caption_tag=caption_tag)

    stats = [n_eol, n_eob, n_eol_shifts, n_eob_shifts]
    return stats

## ADD  ########################################################################

def add(input_file_path, output_file_path, p_eol, p_eob, line_tag=LINE_TAG, caption_tag=CAPTION_TAG,
        wrt_n_boundaries=False):
    """
    Degrade a tagged txt file by adding new boundaries.

    :param input_file_path: initial tagged txt file
    :param output_file_path: degraded (additions) tagged txt file
    :param p_eol: proportion of eol boundaries to be added
    :param p_eob: proportion of eob boundaries to be added
    :param line_tag: tag which represents an end-of-line in a caption (default '<eol>')
    :param caption_tag: tag which represents an end-of-caption (default '<eob>')
    :param wrt_n_boundaries:
        wether proportions are relative to the number of boundaries (True),
        or to the number of free slots (False, default)
    """
    print('Initializing...')
    tagged_txt = preprocess(input_file_path, line_tag=line_tag, caption_tag=caption_tag)

    eol_positions = [m.start() for m in re.finditer(LINE_HOLDER, tagged_txt)]
    eob_positions = [m.start() for m in re.finditer(CAPTION_HOLDER, tagged_txt)]
    space_positions = [m.start() for m in re.finditer(r" ", tagged_txt)]

    n_eol = len(eol_positions)
    n_eob = len(eob_positions)
    n_spaces = len(space_positions)
    if wrt_n_boundaries:
        n_eol_additions = round(p_eol * n_eol)
        n_eob_additions = round(p_eob * n_eob)
    else:
        n_eol_additions = round(p_eol * n_spaces)
        n_eob_additions = round(p_eob * n_spaces)
    n_eol_additions = min(n_eol_additions, n_spaces)
    n_eob_additions = min(n_eob_additions, n_spaces)
    print('n eol additions:\n  %d (%.2f%%)' % (n_eol_additions, 100 * n_eol_additions / n_eol))
    print('n eob additions:\n  %d (%.2f%%)' % (n_eob_additions, 100 * n_eob_additions / n_eob))
    boundaries_to_add = random.sample(space_positions, n_eol_additions + n_eob_additions)
    eol_to_add = random.sample(boundaries_to_add, n_eol_additions)
    eob_to_add = set(boundaries_to_add)
    eob_to_add.difference_update(eol_to_add)

    for eol_pos in eol_to_add:
        tagged_txt = replace_char(tagged_txt, eol_pos, LINE_HOLDER)

    for eob_pos in eob_to_add:
        tagged_txt = replace_char(tagged_txt, eob_pos, CAPTION_HOLDER)

    print('Writing...')
    postprocess(tagged_txt, output_file_path, line_tag=line_tag, caption_tag=caption_tag)

    stats = [n_eol, n_eob, n_eol_additions, n_eob_additions]
    return stats

## DELETE  #####################################################################

def delete(input_file_path, output_file_path, p_eol, p_eob, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):
    """
    Degrade a tagged txt file by deleting some of its boundaries.

    :param input_file_path: initial tagged txt file
    :param output_file_path: degraded (deletions) tagged txt file
    :param p_eol: proportion of eol boundaries to be deleted
    :param p_eob: proportion of eob boundaries to be deleted
    :param line_tag: tag which represents an end-of-line in a caption (default '<eol>')
    :param caption_tag: tag which represents an end-of-caption (default '<eob>')
    """
    print('Initializing...')
    tagged_txt = preprocess(input_file_path, line_tag=line_tag, caption_tag=caption_tag)

    eol_positions = [m.start() for m in re.finditer(LINE_HOLDER, tagged_txt)]
    eob_positions = [m.start() for m in re.finditer(CAPTION_HOLDER, tagged_txt)]

    n_eol = len(eol_positions)
    n_eob = len(eob_positions)
    n_eol_deletions = round(p_eol * n_eol)
    n_eob_deletions = round(p_eob * n_eob)
    print('n eol deletions:\n  %d (%.2f%%)' % (n_eol_deletions, 100 * n_eol_deletions / n_eol))
    print('n eob deletions:\n  %d (%.2f%%)' % (n_eob_deletions, 100 * n_eob_deletions / n_eob))
    eol_to_delete = random.sample(eol_positions, n_eol_deletions)
    eob_to_delete = random.sample(eob_positions, n_eob_deletions)
    boundaries_to_delete = eol_to_delete + eob_to_delete

    for boundary_pos in boundaries_to_delete:
        tagged_txt = replace_char(tagged_txt, boundary_pos, ' ')

    print('Writing...')
    postprocess(tagged_txt, output_file_path, line_tag=line_tag, caption_tag=caption_tag)

    stats = [n_eol, n_eob, n_eol_deletions, n_eob_deletions]
    return stats

## REPLACE  ####################################################################

def replace(input_file_path, output_file_path, p_eol, p_eob, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):
    """
    Degrade a tagged txt file by replacing some of its boundaries with the other type
    (eol <--> eob).

    :param input_file_path: initial tagged txt file
    :param output_file_path: degraded (replacements) tagged txt file
    :param p_eol: proportion of eol boundaries to be replaced
    :param p_eob: proportion of eob boundaries to be replaced
    :param line_tag: tag which represents an end-of-line in a caption (default '<eol>')
    :param caption_tag: tag which represents an end-of-caption (default '<eob>')
    """
    print('Initializing...')
    tagged_txt = preprocess(input_file_path, line_tag=line_tag, caption_tag=caption_tag)

    eol_positions = [m.start() for m in re.finditer(LINE_HOLDER, tagged_txt)]
    eob_positions = [m.start() for m in re.finditer(CAPTION_HOLDER, tagged_txt)]

    n_eol = len(eol_positions)
    n_eob = len(eob_positions)
    n_eol_replacements = round(p_eol * n_eol)
    n_eob_replacements = round(p_eob * n_eob)
    print('n eol replacements:\n  %d (%.2f%%)' % (n_eol_replacements, 100 * n_eol_replacements / n_eol))
    print('n eob replacements:\n  %d (%.2f%%)' % (n_eob_replacements, 100 * n_eob_replacements / n_eob))
    eol_to_replace = random.sample(eol_positions, n_eol_replacements)
    eob_to_replace = random.sample(eob_positions, n_eob_replacements)

    for eol_pos in eol_to_replace:
        tagged_txt = replace_char(tagged_txt, eol_pos, CAPTION_HOLDER)

    for eob_pos in eob_to_replace:
        tagged_txt = replace_char(tagged_txt, eob_pos, LINE_HOLDER)

    print('Writing...')
    postprocess(tagged_txt, output_file_path, line_tag=line_tag, caption_tag=caption_tag)

    stats = [n_eol, n_eob, n_eol_replacements, n_eob_replacements]
    return stats

## MIXED  ######################################################################

def mixed(input_file_path, output_file_path, p_eol_add, p_eob_add, p_eol_del, p_eob_del,
          p_eol_rep, p_eob_rep, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):
    print('Initializing...')
    tagged_txt = preprocess(input_file_path, line_tag=line_tag, caption_tag=caption_tag)

    eol_positions = set([m.start() for m in re.finditer(LINE_HOLDER, tagged_txt)])
    eob_positions = set([m.start() for m in re.finditer(CAPTION_HOLDER, tagged_txt)])
    space_positions = [m.start() for m in re.finditer(r" ", tagged_txt)]

    n_eol = len(eol_positions)
    n_eob = len(eob_positions)
    n_spaces = len(space_positions)

    # n_eol_shifts = round(p_eol_shift * n_eol)
    # n_eob_shifts = round(p_eob_shift * n_eob)
    n_eol_additions = round(p_eol_add * n_eol)
    n_eob_additions = round(p_eob_add * n_eob)
    n_eol_deletions = round(p_eol_del * n_eol)
    n_eob_deletions = round(p_eob_del * n_eob)
    n_eol_replacements = round(p_eol_rep * n_eol)
    n_eob_replacements = round(p_eob_rep * n_eob)

    # Sampling the boundaries to shift
    # eol_to_shift = random.sample(eol_positions, n_eol_shifts)
    # eob_to_shift = random.sample(eob_positions, n_eob_shifts)
    # eol_positions.difference_update(eol_to_shift)
    # eob_positions.difference_update(eob_to_shift)

    # Sampling the boundaries to delete
    eol_to_delete = random.sample(eol_positions, n_eol_deletions)
    eob_to_delete = random.sample(eob_positions, n_eob_deletions)
    eol_positions.difference_update(eol_to_delete)
    eob_positions.difference_update(eob_to_delete)

    # Sampling the boundaries to replace
    eol_to_replace = random.sample(eol_positions, n_eol_replacements)
    eob_to_replace = random.sample(eob_positions, n_eob_replacements)

    # Sampling the boundaries to add
    boundaries_to_add = random.sample(space_positions, n_eol_additions + n_eob_additions)
    eol_to_add = random.sample(boundaries_to_add, n_eol_additions)
    eob_to_add = set(boundaries_to_add)
    eob_to_add.difference_update(eol_to_add)

    # Deleting boundaries
    boundaries_to_delete = eol_to_delete + eob_to_delete
    for boundary_pos in boundaries_to_delete:
        tagged_txt = replace_char(tagged_txt, boundary_pos, ' ')

    # Replacing boundaries
    for eol_pos in eol_to_replace:
        tagged_txt = replace_char(tagged_txt, eol_pos, CAPTION_HOLDER)
    for eob_pos in eob_to_replace:
        tagged_txt = replace_char(tagged_txt, eob_pos, LINE_HOLDER)

    # Adding boundaries
    for eol_pos in eol_to_add:
        tagged_txt = replace_char(tagged_txt, eol_pos, LINE_HOLDER)
    for eob_pos in eob_to_add:
        tagged_txt = replace_char(tagged_txt, eob_pos, CAPTION_HOLDER)

    print('Writing...')
    postprocess(tagged_txt, output_file_path, line_tag=line_tag, caption_tag=caption_tag)

    n_eol += n_eol_additions
    n_eol -= n_eol_deletions
    n_eol += n_eob_replacements
    n_eol -= n_eol_replacements

    n_eob += n_eob_additions
    n_eob -= n_eob_deletions
    n_eob += n_eol_replacements
    n_eob -= n_eob_replacements

    return n_eol, n_eob

## MAIN  #######################################################################

def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('mode', type=str, choices=['shift', 'add', 'delete', 'replace'])

    parser.add_argument('--input_file', '-if', type=str,
                        help="tagged txt file to degrade")
    parser.add_argument('--output_file', '-of', type=str,
                        help="degraded tagged txt file")

    parser.add_argument('--n_units', '-nu', type=int, default=0,
                        help="number of units by which boundaries should be shifted")
    parser.add_argument('--percentage_eol', '-peol', type=float, default=0.0,
                        help="percentage of eol boundaries to be affected")
    parser.add_argument('--percentage_eob', '-peob', type=float, default=0.0,
                        help="percentage of eob boundaries to be affected")
    parser.add_argument('--with_respect_to', '-wrt', type=str, choices=['n_bound', 'n_spaces'], default='n_bound',
                        help="wether proportions are relative to the number of boundaries, or to the number of free slots")

    args = parser.parse_args()
    return args


def main(args):
    mode = args.mode

    input_file_path = args.input_file
    output_file_path = args.output_file
    n = args.n_units
    p_eol = args.percentage_eol / 100
    p_eob = args.percentage_eob / 100
    wrt_n_boundaries = args.with_respect_to == 'n_bound'

    if mode == 'shift':
        shift(input_file_path, output_file_path, n, p_eol, p_eob)

    elif mode == 'add':
        add(input_file_path, output_file_path, p_eol, p_eob, wrt_n_boundaries=wrt_n_boundaries)

    elif mode == 'delete':
        delete(input_file_path, output_file_path, p_eol, p_eob)

    elif mode == 'replace':
        replace(input_file_path, output_file_path, p_eol, p_eob)


if __name__ == '__main__':
    main(parse_args())