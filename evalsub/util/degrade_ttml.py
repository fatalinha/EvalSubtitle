#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import argparse
import random

from ttml import TtmlReader, TtmlWriter, f_to_hmsf, hmsf_to_f

DESCRIPTION = """
A script to degrade subtitle segmentation (in lines and captions) in a ttml file.
The degradation can be achieved by shifting boundaries, adding new boundaries, deleting boundaries, or replacing
boundaries with the other type.
"""

# Minimal number of frames between two captions
F_SPACING = 8
HALF_F_SPACING = int(F_SPACING/2)


# SHIFT  ###############################################################################################################

def shift_eol(lines, n, p_eol):
    n_eol_shifts = 0
    if len(lines) > 1:
        new_lines = list()
        prev_line = lines[0]
        for line in lines[1:]:
            roll = random.random()
            # Case where the eol boundary is shifted (probability p_eol)
            if roll < p_eol:
                n_eol_shifts += 1
                roll = random.randint(0, 1)
                # Case where the eol boundary is shifted on the right (probability 1/2)
                if roll:
                    # The first n units of the current line are removed...
                    shifted_units = line[:n]
                    line = line[n:]
                    # ... and added at the end of the previous line
                    prev_line += shifted_units
                # Case where the eol boundary is shifted on the left (probability 1/2)
                else:
                    # The last n units of the previous line are removed...
                    shifted_units = prev_line[-n:]
                    prev_line = prev_line[:-n]
                    # ... and added at the beginning of the current caption first line
                    line = shifted_units + line

            new_lines.append(prev_line)
            prev_line = line

        new_lines.append(prev_line)
        lines = new_lines

    return lines, n_eol_shifts


def shift(input_file_path, output_file_path, n, p_eol, p_eob):
    """
    Degrade a ttml file by shifting some of its boundaries.

    :param input_file_path: initial ttml file
    :param output_file_path: degraded (shifts) ttml file
    :param n: number of units by which boundaries should be shifted
    :param p_eol: proportion of eol boundaries to be shifted
    :param p_eob: proportion of eob boundaries to be shifted
    """
    print('Initializing...')
    ttml_reader = TtmlReader(input_file_path)
    ttml_writer = TtmlWriter(output_file_path)

    n_eol_shifts, n_eob_shifts = 0, 0

    # Reading 1st caption (it is considered that there is at least 1 caption)
    prev_lines = [line.split() for line in ttml_reader.read_caption(flat=False)]
    prev_begin, prev_end = ttml_reader.current_time_span()
    # eol boundaries are shifted in the 1st caption
    prev_lines, n_shifts = shift_eol(prev_lines, n, p_eol)
    n_eol_shifts += n_shifts

    lines = [line.split() for line in ttml_reader.read_caption(flat=False)]
    # For all the following captions
    while lines:
        begin, end = ttml_reader.current_time_span()

        roll = random.random()
        # Case where the eob boundary is shifted (probability p_eob)
        if roll < p_eob:
            n_eob_shifts += 1
            roll = random.randint(0, 1)
            # Case where the eob boundary is shifted on the right (probability 1/2)
            if roll:
                # The first n units of the current caption first line are removed...
                shifted_units = lines[0][:n]
                lines[0] = lines[0][n:]
                # ... and added at the end of the previous caption last line
                prev_lines[-1] += shifted_units
            # Case where the eob boundary is shifted on the left (probability 1/2)
            else:
                # The last n units of the previous caption last line are removed...
                shifted_units = prev_lines[-1][-n:]
                prev_lines[-1] = prev_lines[-1][:-n]
                # ... and added at the beginning of the current caption first line
                lines[0] = shifted_units + lines[0]

        # Putting aside the previous caption
        prev_lines = [' '.join(line) for line in prev_lines]
        ttml_writer.add_caption(prev_lines, prev_begin, prev_end, 'white')

        # eol boundaries are shifted in the current caption
        lines, n_shifts = shift_eol(lines, n, p_eol)
        n_eol_shifts += n_shifts
        # Reading next caption
        prev_lines = lines
        prev_begin, prev_end = begin, end
        lines = [line.split() for line in ttml_reader.read_caption(flat=False)]

    # Putting aside the last caption
    prev_lines = [' '.join(line) for line in prev_lines]
    ttml_writer.add_caption(prev_lines, prev_begin, prev_end, 'white')

    n_eob = ttml_reader.n_captions()
    n_eol = ttml_reader.n_lines() - n_eob
    p_eol_xp = n_eol_shifts / n_eol
    p_eob_xp = n_eob_shifts / n_eob
    print('n eol shifts:\n  %d (%.2f%%)' % (n_eol_shifts, 100 * p_eol_xp))
    print('n eob shifts:\n  %d (%.2f%%)' % (n_eob_shifts, 100 * p_eob_xp))

    print('Writing...')
    ttml_writer.write()


# ADD  #################################################################################################################

def add(input_file_path, output_file_path, p_eol, p_eob):
    """
    Degrade a ttml file by adding new boundaries.

    :param input_file_path: initial ttml file
    :param output_file_path: degraded (additions) ttml file
    :param p_eol: proportion of eol boundaries to be added
    :param p_eob: proportion of eob boundaries to be added
    """
    print('Initializing...')
    ttml_reader = TtmlReader(input_file_path)
    ttml_writer = TtmlWriter(output_file_path)

    n_boundary_slots = len(ttml_reader.read_all().split())
    n_boundaries = ttml_reader.n_lines()
    n_free_boundary_slots = n_boundary_slots - n_boundaries
    n_eob = ttml_reader.n_captions()
    n_eol = n_boundaries - n_eob
    # Probabilities to insert an eol/eob boundary in a free slot
    pp_eob = p_eob * n_eob / n_free_boundary_slots
    pp_eol = p_eol * n_eol / n_free_boundary_slots
    pp_eol += pp_eob
    ttml_reader.reinit()

    n_added_eol, n_added_eob = 0, 0

    lines = ttml_reader.read_caption(flat=False)
    # For all captions
    while lines:
        caption_length = sum(map(len, lines))
        lines = [line.split() for line in lines]
        begin_f, end_f = map(hmsf_to_f, ttml_reader.current_time_span())
        duration_f = end_f - begin_f
        limit_f = begin_f
        new_begin = f_to_hmsf(begin_f)
        new_lines = list()
        # For all lines in the current caption
        for line in lines:
            new_line = list()
            # For all free boundary slots in the current line
            for unit in line[:-1]:
                new_line.append(unit)

                roll = random.random()
                # Case where an eob boundary is added
                if roll < pp_eob:
                    n_added_eob += 1
                    # Putting aside the new line
                    new_lines.append(' '.join(new_line))
                    new_line = list()
                    # Putting aside the new caption
                    new_caption_length = sum(map(len, new_lines))
                    limit_f += duration_f*new_caption_length/caption_length
                    new_end = f_to_hmsf(limit_f - HALF_F_SPACING)
                    ttml_writer.add_caption(new_lines, new_begin, new_end, 'white')
                    new_begin = f_to_hmsf(limit_f + HALF_F_SPACING)
                    new_lines = list()
                # Case where an eol boundary is added
                elif roll < pp_eol:
                    n_added_eol += 1
                    # Putting aside the new line
                    new_lines.append(' '.join(new_line))
                    new_line = list()

            # Putting aside the last new line
            unit = line[-1]
            new_line.append(unit)
            new_lines.append(' '.join(new_line))

        # Putting aside the last new caption
        new_end = f_to_hmsf(end_f)
        ttml_writer.add_caption(new_lines, new_begin, new_end, 'white')
        # Reading next caption
        lines = ttml_reader.read_caption(flat=False)

    p_eol_xp = n_added_eol / n_eol
    p_eob_xp = n_added_eob / n_eob
    print('n eol additions:\n  %d (%.2f%%)' % (n_added_eol, 100 * p_eol_xp))
    print('n eob additions:\n  %d (%.2f%%)' % (n_added_eob, 100 * p_eob_xp))

    print('Writing...')
    ttml_writer.write()


# DELETE  ##############################################################################################################

def delete_eol(lines, p_eol):
    n_deleted_eol = 0
    if len(lines) > 1:
        new_lines = list()
        new_line = [lines[0]]
        # For all lines in the current caption
        for line in lines[1:]:
            roll = random.random()
            # Case where an eol boundary is deleted
            if roll < p_eol:
                n_deleted_eol += 1
                new_line.append(line)
            # Case where the eol boundary is conserved
            else:
                new_line = ' '.join(new_line) + '\n'
                new_lines.append(new_line)
                new_line = [line]

        new_line = ' '.join(new_line) + '\n'
        new_lines.append(new_line)
        lines = new_lines

    return lines, n_deleted_eol


def delete(input_file_path, output_file_path, p_eol, p_eob):
    """
    Degrade a ttml file by deleting some of its boundaries.

    :param input_file_path: initial ttml file
    :param output_file_path: degraded (deletions) ttml file
    :param p_eol: proportion of eol boundaries to be deleted
    :param p_eob: proportion of eob boundaries to be deleted
    """
    print('Initializing...')
    ttml_reader = TtmlReader(input_file_path)
    ttml_writer = TtmlWriter(output_file_path)

    n_deleted_eol, n_deleted_eob = 0, 0

    # Reading 1st caption (it is considered that there is at least 1 caption)
    lines = [line.strip() for line in ttml_reader.read_caption(flat=False)]
    new_prev_begin, new_prev_end = ttml_reader.current_time_span()
    # eol boundaries are deleted in the 1st caption
    new_prev_lines, n_deleted = delete_eol(lines, p_eol)
    n_deleted_eol += n_deleted

    lines = [line.strip() for line in ttml_reader.read_caption(flat=False)]
    # For all the following captions
    while lines:
        begin, end = ttml_reader.current_time_span()
        new_lines, n_deleted = delete_eol(lines, p_eol)
        n_deleted_eol += n_deleted

        roll = random.random()
        # Case where an eob boundary is deleted
        if roll < p_eob:
            n_deleted_eob += 1
            new_prev_lines += new_lines
            new_prev_end = end
        # Case where the eob boundary is conserved
        else:
            # Putting aside the new caption
            ttml_writer.add_caption(new_prev_lines, new_prev_begin, new_prev_end, 'white')
            new_prev_lines = new_lines
            new_prev_begin, new_prev_end = begin, end

        # Reading next caption
        lines = [line.strip() for line in ttml_reader.read_caption(flat=False)]

    # Putting aside the last caption
    ttml_writer.add_caption(new_prev_lines, new_prev_begin, new_prev_end, 'white')

    n_eob = ttml_reader.n_captions()
    n_eol = ttml_reader.n_lines() - n_eob
    p_eol_xp = n_deleted_eol / n_eol
    p_eob_xp = n_deleted_eob / n_eob
    print('n eol deletions:\n  %d (%.2f%%)' % (n_deleted_eol, 100 * p_eol_xp))
    print('n eob deletions:\n  %d (%.2f%%)' % (n_deleted_eob, 100 * p_eob_xp))

    print('Writing...')
    ttml_writer.write()


# REPLACE  #############################################################################################################

def replace(input_file_path, output_file_path, p_eol, p_eob):
    """
    Degrade a ttml file by replacing some of its boundaries with the other type
    (eol <--> eob).

    :param input_file_path: initial ttml file
    :param output_file_path: degraded (replacements) ttml file
    :param p_eol: proportion of eol boundaries to be replaced
    :param p_eob: proportion of eob boundaries to be replaced
    """
    print('Initializing...')
    ttml_reader = TtmlReader(input_file_path)
    ttml_writer = TtmlWriter(output_file_path)

    n_replaced_eol, n_replaced_eob = 0, 0

    new_lines = list()
    lines = ttml_reader.read_caption(flat=False)
    new_begin = None
    # For all captions
    while lines:
        caption_length = sum(map(len, lines))
        begin_f, end_f = map(hmsf_to_f, ttml_reader.current_time_span())
        duration_f = end_f - begin_f
        limit_f = begin_f
        new_begin = f_to_hmsf(begin_f) if new_begin is None else new_begin
        new_lines.append(lines[0])
        current_length = len(lines[0])
        for line in lines[1:]:
            roll = random.random()
            # Case where an eol boundary is replaced (by eob)
            if roll < p_eol:
                n_replaced_eol += 1
                # Putting aside the new caption
                limit_f += duration_f * current_length / caption_length
                new_end = f_to_hmsf(limit_f - HALF_F_SPACING)
                ttml_writer.add_caption(new_lines, new_begin, new_end, 'white')
                new_begin = f_to_hmsf(limit_f + HALF_F_SPACING)
                new_lines = [line]
                current_length = len(line)
            # Case where the eol boundary is conserved
            else:
                new_lines.append(line)
                current_length += len(line)

        roll = random.random()
        # Case where an eob boundary is replaced (by eol)
        if roll < p_eob:
            n_replaced_eob += 1
        # Case where the eob boundary is conserved
        else:
            new_end = f_to_hmsf(end_f)
            ttml_writer.add_caption(new_lines, new_begin, new_end, 'white')
            new_begin = None
            new_lines = list()

        # Reading next caption
        lines = [line.strip() for line in ttml_reader.read_caption(flat=False)]

    # Putting aside the last caption (if not already done)
    if new_lines:
        new_end = f_to_hmsf(end_f)
        ttml_writer.add_caption(new_lines, new_begin, new_end, 'white')

    n_eob = ttml_reader.n_captions()
    n_eol = ttml_reader.n_lines() - n_eob
    p_eol_xp = n_replaced_eol / n_eol
    p_eob_xp = n_replaced_eob / n_eob
    print('n eol replacements:\n  %d (%.2f%%)' % (n_replaced_eol, 100 * p_eol_xp))
    print('n eob replacements:\n  %d (%.2f%%)' % (n_replaced_eob, 100 * p_eob_xp))

    print('Writing...')
    ttml_writer.write()


# MAIN  ################################################################################################################

def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('mode', type=str, choices=['shift', 'add', 'delete', 'replace'])

    parser.add_argument('--input_file', '-if', type=str,
                        help="ttml file to degrade")
    parser.add_argument('--output_file', '-of', type=str,
                        help="degraded ttml file")

    parser.add_argument('--n_units', '-nu', type=int, default=0,
                        help="number of units by which boundaries should be shifted")
    parser.add_argument('--percentage_eol', '-peol', type=float, default=0.0,
                        help="percentage of eol boundaries to be affected")
    parser.add_argument('--percentage_eob', '-peob', type=float, default=0.0,
                        help="percentage of eob boundaries to be affected")

    args = parser.parse_args()
    return args


def main(args):
    mode = args.mode

    input_file_path = args.input_file
    output_file_path = args.output_file
    n = args.n_units
    p_eol = args.percentage_eol / 100
    p_eob = args.percentage_eob / 100

    if mode == 'shift':
        shift(input_file_path, output_file_path, n, p_eol, p_eob)

    elif mode == 'add':
        add(input_file_path, output_file_path, p_eol, p_eob)

    elif mode == 'delete':
        delete(input_file_path, output_file_path, p_eol, p_eob)

    elif mode == 'replace':
        replace(input_file_path, output_file_path, p_eol, p_eob)


if __name__ == '__main__':
    main(parse_args())
