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
import os
import sys

# We include the path of the toplevel package in the system path,
# so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst
from evalsub.util.util import get_masses

DESCRIPTION = """
Script for computing precision/recall/F1 for the quality evaluation of subtitle segmentations 
based on Alvarez et al. 2016.
"""


def boundary_positions(masses):
    pos = 0
    positions = list()
    for mass in masses:
        pos += mass
        positions.append(pos)

    return positions


def f1_process(ref_file_path, sys_file_path, tag, srt=False, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG):
    sys_eob_masses, sys_eol_masses, sys_eox_masses = get_masses(sys_file_path, srt=srt, line_tag=line_tag,
                                                                caption_tag=caption_tag)
    ref_eob_masses, ref_eol_masses, ref_eox_masses = get_masses(ref_file_path, srt=srt, line_tag=line_tag,
                                                                caption_tag=caption_tag)

    if tag == cst.CAPTION_TAG:
        sys_masses, ref_masses = sys_eob_masses, ref_eob_masses
    elif tag == cst.LINE_TAG:
        sys_masses, ref_masses = sys_eol_masses, ref_eol_masses
    else:  # tag == cst.NEUTRAL_TAG
        sys_masses, ref_masses = sys_eox_masses, ref_eox_masses

    sys_positions = frozenset(boundary_positions(sys_masses))
    ref_positions = frozenset(boundary_positions(ref_masses))
    n_sys_boundaries = len(sys_positions)
    n_ref_boundaries = len(ref_positions)
    n_correct_boundaries = len(sys_positions.intersection(ref_positions))

    # Calculate precision, recall, F1
    try:
        precision = n_correct_boundaries / n_sys_boundaries
        recall = n_correct_boundaries / n_ref_boundaries
        f1 = 2 * precision * recall / (precision + recall)
    except ZeroDivisionError:
        precision, recall, f1 = -1, -1, -1
    print("Scores for", tag)
    print("Precision: %.3f" % precision)
    print("Recall: %.3f" % recall)
    print("F1 score: %.3f" % f1)
    return precision, recall, f1


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--reference_file', '-rf', type=str,
                        help="Reference file.")
    parser.add_argument('--system_file', '-sf', type=str,
                        help="Segmented subtitle file to evaluate.")
    parser.add_argument('--srt', '-srt', action='store_true',
                        help="Whether the subtitle files are in srt format.")

    args = parser.parse_args()
    return args


def main(args):
    ref_file_path = args.reference_file
    sys_file_path = args.system_file
    srt = args.srt

    f1_process(ref_file_path, sys_file_path, cst.NEUTRAL_TAG,
               srt=srt, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG)
    f1_process(ref_file_path, sys_file_path, cst.CAPTION_TAG,
               srt=srt, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG)
    f1_process(ref_file_path, sys_file_path, cst.LINE_TAG,
               srt=srt, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG)


if __name__ == '__main__':
    main(parse_args())
