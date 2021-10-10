# coding: utf-8

DESCRIPTION = """
Script to compute the segmentation metrics for a pair of segmented subtitle files.
"""

import argparse
import json
import re

import segeval

from ttml import ttml_to_tagged_str

LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'
PK = "pk"
WINDOW_DIFF = "window_diff"
METRICS = frozenset({PK, WINDOW_DIFF})

def get_masses(file_path, ttml=False, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):
    """
    Get the boundary segmentation from a segmented subtitle file.

    :param file_path: segmented subtitle file (ttml or tagged text)
    :param ttml: wether file_path is in ttml format
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
    # <eol> + <eob> segmentation
    eox_str = re.sub(caption_tag, line_tag, file_str)
    eox_masses = [len(segment.split()) for segment in eox_str.split(line_tag)]

    return eob_masses, eol_masses, eox_masses


def eval_seg(sys_file_path, ref_file_path, metrics=METRICS ,ttml=False, eol_window_size=None, eob_window_size=None,
             eox_window_size=None, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):

    sys_eob_masses, sys_eol_masses, sys_eox_masses = get_masses(sys_file_path, ttml=ttml, line_tag=line_tag,
                                                             caption_tag=caption_tag)
    ref_eob_masses, ref_eol_masses, ref_eox_masses = get_masses(ref_file_path, ttml=ttml, line_tag=line_tag,
                                                             caption_tag=caption_tag)

    results = dict()

    print('<eob> only segmentation:')
    results['<eob> only'] = dict()
    # Window size is computed only if Pk or WindowDiff is computed
    if PK in metrics or WINDOW_DIFF in metrics:
        if eob_window_size is None:
            eob_window_size = segeval.compute_window_size(ref_eob_masses)
        print('  window_size =', eob_window_size)
        results['<eob> only']['window_size'] = eob_window_size
    # Case where Pk is computed
    if PK in metrics:
        eob_pk = segeval.pk(sys_eob_masses, ref_eob_masses, window_size=eob_window_size)
        print('  Pk = %.3f' % eob_pk)
        results['<eob> only']['pk'] = float(eob_pk)
    # Case where WindowDiff is computed
    if WINDOW_DIFF in metrics:
        eob_window_diff = segeval.window_diff(sys_eob_masses, ref_eob_masses, window_size=eob_window_size)
        print('  WindowDiff = %.3f' % eob_window_diff)
        results['<eob> only']['window_diff'] = float(eob_window_diff)

    print('<eol> only segmentation:')
    results['<eol> only'] = dict()
    # Window size is computed only if Pk or WindowDiff is computed
    if PK in metrics or WINDOW_DIFF in metrics:
        if eol_window_size is None:
            eol_window_size = segeval.compute_window_size(ref_eol_masses)
        print('  window_size =', eol_window_size)
        results['<eol> only']['window_size'] = eol_window_size
    # Case where Pk is computed
    if PK in metrics:
        eol_pk = segeval.pk(sys_eol_masses, ref_eol_masses, window_size=eol_window_size)
        print('  Pk = %.3f' % eol_pk)
        results['<eol> only']['pk'] = float(eol_pk)
    # Case where WindowDiff is computed
    if WINDOW_DIFF in metrics:
        eol_window_diff = segeval.window_diff(sys_eol_masses, ref_eol_masses, window_size=eol_window_size)
        print('  WindowDiff = %.3f' % eol_window_diff)
        results['<eol> only']['window_diff'] = float(eol_window_diff)

    print('<eol> + <eob> segmentation:')
    results['<eol> + <eob>'] = dict()
    # Window size is computed only if Pk or WindowDiff is computed
    if PK in metrics or WINDOW_DIFF in metrics:
        if eox_window_size is None:
            eox_window_size = segeval.compute_window_size(ref_eox_masses)
        print('  window_size =', eox_window_size)
        results['<eol> + <eob>']['window_size'] = eox_window_size
    # Case where Pk is computed
    if PK in metrics:
        eox_pk = segeval.pk(sys_eox_masses, ref_eox_masses, window_size=eox_window_size)
        print('  Pk = %.3f' % eox_pk)
        results['<eol> + <eob>']['pk'] = float(eox_pk)
    # Case where WindowDiff is computed
    if WINDOW_DIFF in metrics:
        eox_window_diff = segeval.window_diff(sys_eox_masses, ref_eox_masses, window_size=eox_window_size)
        print('  WindowDiff = %.3f' % eox_window_diff)
        results['<eol> + <eob>']['window_diff'] = float(eox_window_diff)

    return results

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
                        help="window size for the <eol> + <eob> segmentation evaluation")

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