#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

DESCRIPTION = """
Script to compute the standard segmentation metrics for a pair of segmented subtitle files.
"""

import argparse
import json
import os
import sys

import segeval

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst
from evalsub.util.util import get_masses


METRICS = frozenset({cst.PK, cst.WIN_DIFF, cst.SEG_SIM, cst.BOUND_SIM})
EOB = "<eob>"
EOL = "<eol>"
EOX = "<eox>"
EOB_EOL = "<eob>,<eol>"
TYPES = frozenset({EOB, EOL, EOX, EOB_EOL})


def masses_to_sets(eob_masses, eol_masses, eox_masses):
    """
    Convert segmentation masses to boundary sets for subtitle segmentation.

    :param eob_masses: <eob> segmentation masses (segeval.BoundaryFormat.mass format)
    :param eol_masses: <eol> segmentation masses
    :param eox_masses: <eox> segmentation masses
    :return: boundary sets (segeval.BoundaryFormat.sets format)
    """
    eob_sets = segeval.boundary_string_from_masses(eob_masses)
    eol_sets = segeval.boundary_string_from_masses(eol_masses)
    eox_sets = segeval.boundary_string_from_masses(eox_masses)
    eob_eol_sets = tuple(eob_set.union(map(lambda x: 2 * x, eol_set)) for eob_set, eol_set in zip(eob_sets, eol_sets))

    return eob_sets, eol_sets, eox_sets, eob_eol_sets


def eval_seg(sys_file_path, ref_file_path, metrics=METRICS ,srt=False, ttml=False, eol_window_size=None,
             eob_window_size=None, eox_window_size=None, nt=cst.DEFAULT_NT, line_tag=cst.LINE_TAG,
             caption_tag=cst.CAPTION_TAG):

    sys_eob_masses, sys_eol_masses, sys_eox_masses = get_masses(sys_file_path, srt=srt, ttml=ttml, line_tag=line_tag,
                                                             caption_tag=caption_tag)
    ref_eob_masses, ref_eol_masses, ref_eox_masses = get_masses(ref_file_path, srt=srt, ttml=ttml, line_tag=line_tag,
                                                             caption_tag=caption_tag)
    sys_eob_sets, sys_eol_sets, sys_eox_sets, sys_eob_eol_sets = masses_to_sets(sys_eob_masses, sys_eol_masses,
                                                                                sys_eox_masses)
    ref_eob_sets, ref_eol_sets, ref_eox_sets, ref_eob_eol_sets = masses_to_sets(ref_eob_masses, ref_eol_masses,
                                                                                ref_eox_masses)

    results = dict()

    print('<eob> only segmentation:')
    results[EOB] = dict()
    # Window size is computed only if Pk or WindowDiff is computed
    if cst.PK in metrics or cst.WIN_DIFF in metrics:
        if eob_window_size is None:
            eob_window_size = segeval.compute_window_size(ref_eob_masses)
        print('  window_size =', eob_window_size)
        results[EOB]['window_size'] = eob_window_size
    # Case where Pk is computed
    if cst.PK in metrics:
        eob_pk = segeval.pk(sys_eob_masses, ref_eob_masses, window_size=eob_window_size)
        print('  Pk = %.3f' % eob_pk)
        results[EOB][cst.PK] = float(eob_pk)
    # Case where WindowDiff is computed
    if cst.WIN_DIFF in metrics:
        eob_window_diff = segeval.window_diff(sys_eob_masses, ref_eob_masses, window_size=eob_window_size)
        print('  WindowDiff = %.3f' % eob_window_diff)
        results[EOB][cst.WIN_DIFF] = float(eob_window_diff)
    # Case where Segmentation Similarity is computed
    if cst.SEG_SIM in metrics:
        eob_seg_sim = segeval.segmentation_similarity(sys_eob_sets, ref_eob_sets,
                                                      boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  S = %.3f' % eob_seg_sim)
        results[EOB][cst.SEG_SIM] = float(eob_seg_sim)
    # Case where Boundary Similarity is computed
    if cst.BOUND_SIM in metrics:
        eob_bound_sim = segeval.boundary_similarity(sys_eob_sets, ref_eob_sets,
                                                    boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  B = %.3f' % eob_bound_sim)
        results[EOB][cst.BOUND_SIM] = float(eob_bound_sim)

    print('<eol> only segmentation:')
    results[EOL] = dict()
    # Window size is computed only if Pk or WindowDiff is computed
    if cst.PK in metrics or cst.WIN_DIFF in metrics:
        if eol_window_size is None:
            eol_window_size = segeval.compute_window_size(ref_eol_masses)
        print('  window_size =', eol_window_size)
        results[EOL]['window_size'] = eol_window_size
    # Case where Pk is computed
    if cst.PK in metrics:
        eol_pk = segeval.pk(sys_eol_masses, ref_eol_masses, window_size=eol_window_size)
        print('  Pk = %.3f' % eol_pk)
        results[EOL][cst.PK] = float(eol_pk)
    # Case where WindowDiff is computed
    if cst.WIN_DIFF in metrics:
        eol_window_diff = segeval.window_diff(sys_eol_masses, ref_eol_masses, window_size=eol_window_size)
        print('  WindowDiff = %.3f' % eol_window_diff)
        results[EOL][cst.WIN_DIFF] = float(eol_window_diff)
    # Case where Segmentation Similarity is computed
    if cst.SEG_SIM in metrics:
        eol_seg_sim = segeval.segmentation_similarity(sys_eol_sets, ref_eol_sets,
                                                      boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  S = %.3f' % eol_seg_sim)
        results[EOL][cst.SEG_SIM] = float(eol_seg_sim)
    # Case where Boundary Similarity is computed
    if cst.BOUND_SIM in metrics:
        eol_bound_sim = segeval.boundary_similarity(sys_eol_sets, ref_eol_sets,
                                                    boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  B = %.3f' % eol_bound_sim)
        results[EOL][cst.BOUND_SIM] = float(eol_bound_sim)

    print('<eox> segmentation:')
    results[EOX] = dict()
    # Window size is computed only if Pk or WindowDiff is computed
    if cst.PK in metrics or cst.WIN_DIFF in metrics:
        if eox_window_size is None:
            eox_window_size = segeval.compute_window_size(ref_eox_masses)
        print('  window_size =', eox_window_size)
        results[EOX]['window_size'] = eox_window_size
    # Case where Pk is computed
    if cst.PK in metrics:
        eox_pk = segeval.pk(sys_eox_masses, ref_eox_masses, window_size=eox_window_size)
        print('  Pk = %.3f' % eox_pk)
        results[EOX][cst.PK] = float(eox_pk)
    # Case where WindowDiff is computed
    if cst.WIN_DIFF in metrics:
        eox_window_diff = segeval.window_diff(sys_eox_masses, ref_eox_masses, window_size=eox_window_size)
        print('  WindowDiff = %.3f' % eox_window_diff)
        results[EOX][cst.WIN_DIFF] = float(eox_window_diff)
    # Case where Segmentation Similarity is computed
    if cst.SEG_SIM in metrics:
        eox_seg_sim = segeval.segmentation_similarity(sys_eox_sets, ref_eox_sets,
                                                      boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  S = %.3f' % eox_seg_sim)
        results[EOX][cst.SEG_SIM] = float(eox_seg_sim)
    # Case where Boundary Similarity is computed
    if cst.BOUND_SIM in metrics:
        eox_bound_sim = segeval.boundary_similarity(sys_eox_sets, ref_eox_sets,
                                                    boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  B = %.3f' % eox_bound_sim)
        results[EOX][cst.BOUND_SIM] = float(eox_bound_sim)

    print('<eob>,<eol> segmentation:')
    results[EOB_EOL] = dict()
    # Case where Segmentation Similarity is computed
    if cst.SEG_SIM in metrics:
        eob_eol_seg_sim = segeval.segmentation_similarity(sys_eob_eol_sets, ref_eob_eol_sets,
                                                          boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  S = %.3f' % eob_eol_seg_sim)
        results[EOB_EOL][cst.SEG_SIM] = float(eob_eol_seg_sim)
    # Case where Boundary Similarity is computed
    if cst.BOUND_SIM in metrics:
        eob_eol_bound_sim = segeval.boundary_similarity(sys_eob_eol_sets, ref_eob_eol_sets,
                                                        boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  B = %.3f' % eob_eol_bound_sim)
        results[EOB_EOL][cst.BOUND_SIM] = float(eob_eol_bound_sim)

    return results


def seg_process(sys_file_path, ref_file_path, srt=False, ttml=False, window_size=None, nt=cst.DEFAULT_NT,
                line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG):

    sys_eob_masses, sys_eol_masses, sys_eox_masses = get_masses(sys_file_path, srt=srt, ttml=ttml, line_tag=line_tag,
                                                                caption_tag=caption_tag)
    ref_eob_masses, ref_eol_masses, ref_eox_masses = get_masses(ref_file_path, srt=srt, ttml=ttml, line_tag=line_tag,
                                                                caption_tag=caption_tag)
    sys_eob_sets, sys_eol_sets, sys_eox_sets, sys_eob_eol_sets = masses_to_sets(sys_eob_masses, sys_eol_masses,
                                                                                sys_eox_masses)
    ref_eob_sets, ref_eol_sets, ref_eox_sets, ref_eob_eol_sets = masses_to_sets(ref_eob_masses, ref_eol_masses,
                                                                                ref_eox_masses)

    print('%s=%s segmentation:' % (line_tag, caption_tag))
    eox_window_size = window_size
    # Window size is computed
    if eox_window_size is None:
        eox_window_size = segeval.compute_window_size(ref_eox_masses)
    print('  %s = %d' % (cst.WIN_SIZE, eox_window_size))
    # Pk is computed
    eox_pk = segeval.pk(sys_eox_masses, ref_eox_masses, window_size=eox_window_size)
    print('  %s = %.3f' % (cst.PK, eox_pk))
    pk = float(eox_pk)
    # WindowDiff is computed
    eox_window_diff = segeval.window_diff(sys_eox_masses, ref_eox_masses, window_size=eox_window_size)
    print('  %s = %.3f' % (cst.WIN_DIFF, eox_window_diff))
    window_diff = float(eox_window_diff)

    print('%s,%s segmentation:' % (line_tag, caption_tag))
    # Segmentation Similarity is computed
    eob_eol_seg_sim = segeval.segmentation_similarity(sys_eob_eol_sets, ref_eob_eol_sets,
                                                      boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
    print('  %s = %.3f' % (cst.SEG_SIM, eob_eol_seg_sim))
    seg_sim = float(eob_eol_seg_sim)
    # Boundary Similarity is computed
    eob_eol_bound_sim = segeval.boundary_similarity(sys_eob_eol_sets, ref_eob_eol_sets,
                                                    boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
    print('  %s = %.3f' % (cst.BOUND_SIM, eob_eol_bound_sim))
    bound_sim = float(eob_eol_bound_sim)

    return eox_window_size, pk, window_diff, seg_sim, bound_sim


## MAIN  #######################################################################

def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--include', '-i', type=str, nargs='+',
                        help="list of metrics to compute")
    parser.add_argument('--exclude', '-e', type=str, nargs='+',
                        help="list of metrics not to compute")

    parser.add_argument('--system_file', '-sf', type=str,
                        help="Segmented subtitle file to evaluate.")
    parser.add_argument('--reference_file', '-rf', type=str,
                        help="Reference segmented subtitle file.")
    parser.add_argument('--json_file', '-jsonf', type=str,
                        help="JSON file where to write the results.")
    parser.add_argument('--csv_file', '-csvf', type=str,
                        help="CSV file where to write the results.")

    parser.add_argument('--ttml', '-ttml', action='store_true',
                        help="Wether the subtitle files are in ttml format")

    parser.add_argument('--eob_window_size', '-eobws', type=int,
                        help="window size for the <eob> only segmentation evaluation")
    parser.add_argument('--eol_window_size', '-eolws', type=int,
                        help="window size for the <eol> only segmentation evaluation")
    parser.add_argument('--eox_window_size', '-eoxws', type=int,
                        help="window size for the <eox> (<eol> = <eob>) segmentation evaluation")

    args = parser.parse_args()
    return args


def main(args):
    metrics = set(METRICS)
    included_metrics = args.include
    if included_metrics is not None:
        metrics.intersection_update(included_metrics)
    excluded_metrics = args.exclude
    if excluded_metrics is not None:
        metrics.difference_update(excluded_metrics)
    metrics = frozenset(metrics)

    sys_file_path = args.system_file
    ref_file_path = args.reference_file
    json_file_path = args.json_file
    csv_file_path = args.csv_file #TODO?

    ttml = args.ttml

    eob_window_size = args.eob_window_size
    eol_window_size = args.eol_window_size
    eox_window_size = args.eox_window_size

    results = eval_seg(sys_file_path, ref_file_path, metrics=metrics, ttml=ttml, eol_window_size=eol_window_size,
             eob_window_size=eob_window_size, eox_window_size=eox_window_size)

    if json_file_path is not None:
        json.dump(results, open(json_file_path, 'w'), ensure_ascii=False, indent=3, sort_keys=True)


if __name__ == '__main__':
    main(parse_args())
