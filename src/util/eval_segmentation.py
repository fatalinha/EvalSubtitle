# coding: utf-8

DESCRIPTION = """
Script to compute the segmentation metrics for a pair of segmented subtitle files.
"""

import argparse
import re

import segeval

from ttml import ttml_to_tagged_str

LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'

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

    # Caption segmentation (<eob> only)
    caption_str = re.sub(line_tag, r" ", file_str)
    caption_masses = [len(segment.split()) for segment in caption_str.split(caption_tag)]
    # Line segmentation (<eol> + <eob>)
    line_str = re.sub(caption_tag, line_tag, file_str)
    line_masses = [len(segment.split()) for segment in line_str.split(line_tag)]

    return caption_masses, line_masses


def eval_seg(sys_file_path, ref_file_path, ttml=False, line_window_size=None, caption_window_size=None,
             line_tag=LINE_TAG, caption_tag=CAPTION_TAG):

    sys_caption_masses, sys_line_masses = get_masses(sys_file_path, ttml=ttml, line_tag=line_tag,
                                                             caption_tag=caption_tag)
    ref_caption_masses, ref_line_masses = get_masses(ref_file_path, ttml=ttml, line_tag=line_tag,
                                                             caption_tag=caption_tag)

    print('Caption segmentation (<eob> only):')
    if caption_window_size is None:
        caption_window_size = segeval.compute_window_size(ref_caption_masses)
    print('  window_size =', caption_window_size)
    caption_pk = segeval.pk(sys_caption_masses, ref_caption_masses, window_size=caption_window_size)
    print('  Pk = %.3f' % caption_pk)
    caption_window_diff = segeval.window_diff(sys_caption_masses, ref_caption_masses,
                                      window_size=caption_window_size)
    print('  WindowDiff = %.3f' % caption_window_diff)

    print('Line segmentation (<eol> + <eob>):')
    if line_window_size is None:
        line_window_size = segeval.compute_window_size(ref_line_masses)
    print('  window_size =', line_window_size)
    line_pk = segeval.pk(sys_line_masses, ref_line_masses, window_size=line_window_size)
    print('  Pk = %.3f' % line_pk)
    line_window_diff = segeval.window_diff(sys_line_masses, ref_line_masses,
                                      window_size=caption_window_size)
    print('  WindowDiff = %.3f' % line_window_diff)

## MAIN  #######################################################################

def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--system_file', '-sf', type=str,
                        help="Segmented subtitle file to evaluate.")
    parser.add_argument('--reference_file', '-rf', type=str,
                        help="Reference segmented subtitle file.")

    parser.add_argument('--ttml', '-ttml', action='store_true',
                        help="Wether the subtitle files are in ttml format")

    parser.add_argument('--caption_window_size', '-cws', type=int,
                        help="window size for the caption (<eob> only) segmentation evaluation")
    parser.add_argument('--line_window_size', '-lws', type=int,
                        help="window size for the line (<eol> + <eob>) segmentation evaluation")

    args = parser.parse_args()
    return args


def main(args):
    sys_file_path = args.system_file
    ref_file_path = args.reference_file

    ttml = args.ttml

    caption_window_size = args.caption_window_size
    line_window_size = args.line_window_size

    eval_seg(sys_file_path, ref_file_path, ttml=ttml, line_window_size=line_window_size,
             caption_window_size=caption_window_size)


if __name__ == '__main__':
    main(parse_args())