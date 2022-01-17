# coding: utf-8

DESCRIPTION = """
Script to compute the standard segmentation metrics for a pair of segmented subtitle files.
"""

import argparse
import json
import os
import re
import sys

import segeval

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

from evalsub.util.ttml import ttml_to_tagged_str


LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'
PK = "pk"
WINDOW_DIFF = "window_diff"
SEG_SIM = "segmentation_similarity"
BOUND_SIM = "boundary_similarity"
METRICS = frozenset({PK, WINDOW_DIFF, SEG_SIM, BOUND_SIM})
EOB = "<eob>"
EOL = "<eol>"
EOX = "<eox>"
EOB_EOL = "<eob>,<eol>"
TYPES = frozenset({EOB, EOL, EOX, EOB_EOL})
NT = 2


def get_masses(file_path, ttml=False, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):
    """
    Get the segmentation masses from a segmented subtitle file.

    :param file_path: segmented subtitle file (ttml or tagged text)
    :param ttml: whether file_path is in ttml format
    :param line_tag: end of line boundary tag
    :param caption_tag: end of caption/block boundary tag
    :return: segmentation masses (segeval.BoundaryFormat.mass format)
    """
    if ttml:
        file_str, _ = ttml_to_tagged_str(file_path, line_tag=line_tag, caption_tag=caption_tag)
    else:
        file_str = ' '.join([line.strip() for line in open(file_path).readlines()])

    # Quick pre-processing before splitting
    # Removing (potential) multiple spaces
    file_str = re.sub(r" {2,}", r" ", file_str)
    # Removing spaces around boundaries
    file_str = re.sub(r"( )?(%s|%s)( )?" % (line_tag, caption_tag), r"\2", file_str)
    # Removing (potential) ending boundary
    file_str = re.sub(r"%s$" % caption_tag, r"", file_str)

    # <eob> only segmentation
    eob_str = re.sub(line_tag, r" ", file_str)
    eob_masses = [len(segment.split()) for segment in eob_str.split(caption_tag)]
    # <eol> only segmentation
    eol_str = re.sub(caption_tag, r" ", file_str)
    eol_masses = [len(segment.split()) for segment in eol_str.split(line_tag)]
    # <eox> (<eol> = <eob>) segmentation
    eox_str = re.sub(caption_tag, line_tag, file_str)
    eox_masses = [len(segment.split()) for segment in eox_str.split(line_tag)]

    return eob_masses, eol_masses, eox_masses


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


def eval_seg(sys_file_path, ref_file_path, metrics=METRICS ,ttml=False, eol_window_size=None, eob_window_size=None,
             eox_window_size=None, nt=NT, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):

    sys_eob_masses, sys_eol_masses, sys_eox_masses = get_masses(sys_file_path, ttml=ttml, line_tag=line_tag,
                                                             caption_tag=caption_tag)
    ref_eob_masses, ref_eol_masses, ref_eox_masses = get_masses(ref_file_path, ttml=ttml, line_tag=line_tag,
                                                             caption_tag=caption_tag)
    sys_eob_sets, sys_eol_sets, sys_eox_sets, sys_eob_eol_sets = masses_to_sets(sys_eob_masses, sys_eol_masses,
                                                                                sys_eox_masses)
    ref_eob_sets, ref_eol_sets, ref_eox_sets, ref_eob_eol_sets = masses_to_sets(ref_eob_masses, ref_eol_masses,
                                                                                ref_eox_masses)

    results = dict()

    print('<eob> only segmentation:')
    results[EOB] = dict()
    # Window size is computed only if Pk or WindowDiff is computed
    if PK in metrics or WINDOW_DIFF in metrics:
        if eob_window_size is None:
            eob_window_size = segeval.compute_window_size(ref_eob_masses)
        print('  window_size =', eob_window_size)
        results[EOB]['window_size'] = eob_window_size
    # Case where Pk is computed
    if PK in metrics:
        eob_pk = segeval.pk(sys_eob_masses, ref_eob_masses, window_size=eob_window_size)
        print('  Pk = %.3f' % eob_pk)
        results[EOB][PK] = float(eob_pk)
    # Case where WindowDiff is computed
    if WINDOW_DIFF in metrics:
        eob_window_diff = segeval.window_diff(sys_eob_masses, ref_eob_masses, window_size=eob_window_size)
        print('  WindowDiff = %.3f' % eob_window_diff)
        results[EOB][WINDOW_DIFF] = float(eob_window_diff)
    # Case where Segmentation Similarity is computed
    if SEG_SIM in metrics:
        eob_seg_sim = segeval.segmentation_similarity(sys_eob_sets, ref_eob_sets,
                                                      boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  S = %.3f' % eob_seg_sim)
        results[EOB][SEG_SIM] = float(eob_seg_sim)
    # Case where Boundary Similarity is computed
    if BOUND_SIM in metrics:
        eob_bound_sim = segeval.boundary_similarity(sys_eob_sets, ref_eob_sets,
                                                    boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  B = %.3f' % eob_bound_sim)
        results[EOB][BOUND_SIM] = float(eob_bound_sim)

    print('<eol> only segmentation:')
    results[EOL] = dict()
    # Window size is computed only if Pk or WindowDiff is computed
    if PK in metrics or WINDOW_DIFF in metrics:
        if eol_window_size is None:
            eol_window_size = segeval.compute_window_size(ref_eol_masses)
        print('  window_size =', eol_window_size)
        results[EOL]['window_size'] = eol_window_size
    # Case where Pk is computed
    if PK in metrics:
        eol_pk = segeval.pk(sys_eol_masses, ref_eol_masses, window_size=eol_window_size)
        print('  Pk = %.3f' % eol_pk)
        results[EOL][PK] = float(eol_pk)
    # Case where WindowDiff is computed
    if WINDOW_DIFF in metrics:
        eol_window_diff = segeval.window_diff(sys_eol_masses, ref_eol_masses, window_size=eol_window_size)
        print('  WindowDiff = %.3f' % eol_window_diff)
        results[EOL][WINDOW_DIFF] = float(eol_window_diff)
    # Case where Segmentation Similarity is computed
    if SEG_SIM in metrics:
        eol_seg_sim = segeval.segmentation_similarity(sys_eol_sets, ref_eol_sets,
                                                      boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  S = %.3f' % eol_seg_sim)
        results[EOL][SEG_SIM] = float(eol_seg_sim)
    # Case where Boundary Similarity is computed
    if BOUND_SIM in metrics:
        eol_bound_sim = segeval.boundary_similarity(sys_eol_sets, ref_eol_sets,
                                                    boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  B = %.3f' % eol_bound_sim)
        results[EOL][BOUND_SIM] = float(eol_bound_sim)

    print('<eox> segmentation:')
    results[EOX] = dict()
    # Window size is computed only if Pk or WindowDiff is computed
    if PK in metrics or WINDOW_DIFF in metrics:
        if eox_window_size is None:
            eox_window_size = segeval.compute_window_size(ref_eox_masses)
        print('  window_size =', eox_window_size)
        results[EOX]['window_size'] = eox_window_size
    # Case where Pk is computed
    if PK in metrics:
        eox_pk = segeval.pk(sys_eox_masses, ref_eox_masses, window_size=eox_window_size)
        print('  Pk = %.3f' % eox_pk)
        results[EOX][PK] = float(eox_pk)
    # Case where WindowDiff is computed
    if WINDOW_DIFF in metrics:
        eox_window_diff = segeval.window_diff(sys_eox_masses, ref_eox_masses, window_size=eox_window_size)
        print('  WindowDiff = %.3f' % eox_window_diff)
        results[EOX][WINDOW_DIFF] = float(eox_window_diff)
    # Case where Segmentation Similarity is computed
    if SEG_SIM in metrics:
        eox_seg_sim = segeval.segmentation_similarity(sys_eox_sets, ref_eox_sets,
                                                      boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  S = %.3f' % eox_seg_sim)
        results[EOX][SEG_SIM] = float(eox_seg_sim)
    # Case where Boundary Similarity is computed
    if BOUND_SIM in metrics:
        eox_bound_sim = segeval.boundary_similarity(sys_eox_sets, ref_eox_sets,
                                                    boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  B = %.3f' % eox_bound_sim)
        results[EOX][BOUND_SIM] = float(eox_bound_sim)

    print('<eob>,<eol> segmentation:')
    results[EOB_EOL] = dict()
    # Case where Segmentation Similarity is computed
    if SEG_SIM in metrics:
        eob_eol_seg_sim = segeval.segmentation_similarity(sys_eob_eol_sets, ref_eob_eol_sets,
                                                          boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  S = %.3f' % eob_eol_seg_sim)
        results[EOB_EOL][SEG_SIM] = float(eob_eol_seg_sim)
    # Case where Boundary Similarity is computed
    if BOUND_SIM in metrics:
        eob_eol_bound_sim = segeval.boundary_similarity(sys_eob_eol_sets, ref_eob_eol_sets,
                                                        boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
        print('  B = %.3f' % eob_eol_bound_sim)
        results[EOB_EOL][BOUND_SIM] = float(eob_eol_bound_sim)

    return results


def get_metrics(sys_file_path, ref_file_path, ttml=False, eox_window_size=None, nt=NT, line_tag=LINE_TAG,
                caption_tag=CAPTION_TAG):

    sys_eob_masses, sys_eol_masses, sys_eox_masses = get_masses(sys_file_path, ttml=ttml, line_tag=line_tag,
                                                                caption_tag=caption_tag)
    ref_eob_masses, ref_eol_masses, ref_eox_masses = get_masses(ref_file_path, ttml=ttml, line_tag=line_tag,
                                                                caption_tag=caption_tag)
    sys_eob_sets, sys_eol_sets, sys_eox_sets, sys_eob_eol_sets = masses_to_sets(sys_eob_masses, sys_eol_masses,
                                                                                sys_eox_masses)
    ref_eob_sets, ref_eol_sets, ref_eox_sets, ref_eob_eol_sets = masses_to_sets(ref_eob_masses, ref_eol_masses,
                                                                                ref_eox_masses)

    print('<eox> segmentation:')
    # Window size is computed
    if eox_window_size is None:
        eox_window_size = segeval.compute_window_size(ref_eox_masses)
    print('  window_size =', eox_window_size)
    # Pk is computed
    eox_pk = segeval.pk(sys_eox_masses, ref_eox_masses, window_size=eox_window_size)
    print('  Pk = %.3f' % eox_pk)
    pk = float(eox_pk)
    # WindowDiff is computed
    eox_window_diff = segeval.window_diff(sys_eox_masses, ref_eox_masses, window_size=eox_window_size)
    print('  WindowDiff = %.3f' % eox_window_diff)
    window_diff = float(eox_window_diff)

    print('<eob>,<eol> segmentation:')
    # Segmentation Similarity is computed
    eob_eol_seg_sim = segeval.segmentation_similarity(sys_eob_eol_sets, ref_eob_eol_sets,
                                                      boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
    print('  S = %.3f' % eob_eol_seg_sim)
    seg_sim = float(eob_eol_seg_sim)
    # Boundary Similarity is computed
    eob_eol_bound_sim = segeval.boundary_similarity(sys_eob_eol_sets, ref_eob_eol_sets,
                                                    boundary_format=segeval.BoundaryFormat.sets, n_t=nt)
    print('  B = %.3f' % eob_eol_bound_sim)
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
