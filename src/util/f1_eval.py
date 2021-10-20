# coding: utf-8
from ttml import ttml_to_tagged_str
import re
import argparse

DESCRIPTION = """Script for computing precision/recall/F1 
 for the quality evaluation of subtitle segmentations
 based on Alvarez et al. 2016."""

LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'


def get_break_positions(line, symbol):
    # Get actual splits: word before <split> word after
    re_eo = fr'(?:\S+\s)?\S*{symbol}\S*(?:\s\S+)?'
    splits = re.findall(re_eo, line)
    return splits


def evaluate_f1(reference_file, system_file, symbol, ttml=False, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):

    breaks_ref = 0  # Number of total breaks in reference (used for precision)
    breaks_out = 0  # Number of total breaks in output (used for recall)
    correct_breaks = 0  # Total number of correct breaks (used for both pre-rec)
    # TODO: smoothing in case of no <eol> present in corpus?
    with open(reference_file) as r, open(system_file) as s:
        for lref, lseg in zip(r, s):
            if symbol == '<eox>':
                lref = ' '.join([br.replace(line_tag, symbol).replace(caption_tag, symbol) for br in lref.split(' ')])
                lseg = ' '.join([br.replace(line_tag, symbol).replace(caption_tag, symbol) for br in lseg.split(' ')])
            # Get splits
            splts_ref = get_break_positions(lref.strip(), symbol)
            splts_seg = get_break_positions(lseg.strip(), symbol)

            # Compare all splits ref-trans
            breaks_ref += len(splts_ref)
            breaks_out += len(splts_seg)
            correct_breaks += len(set(splts_ref) & set(splts_seg))
            ##TODO: Check in case splts have duplicate elements e.g. [2,2]

        # Calculate precision, recall, F1
        precision = correct_breaks / breaks_out
        recall = correct_breaks / breaks_ref
        f1 = 2 * ((precision * recall) / float(precision + recall))

        print("Scores for " + symbol)
        print("Precision: " + str(round(precision, 3)))
        print("Recall: " + str(round(recall, 3)))
        print("F1 score: " + str(round(f1, 3)))
        return precision, recall, f1


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--reference_file', '-rf', type=str,
                        help="Reference file")
    parser.add_argument('--system_file', '-sf', type=str,
                        help="Segmented subtitle file to evaluate.")
    parser.add_argument('--ttml', '-ttml', action='store_true',
                        help="Whether the subtitle files are in ttml format")

    args = parser.parse_args()
    return args


def main(args):
    reference_file = args.reference_file
    system_file = args.system_file

    # TODO: add ttml processing
    #ttml = args.ttml
    evaluate_f1(reference_file, system_file, '<eox>', ttml=False, line_tag=LINE_TAG, caption_tag=CAPTION_TAG)
    evaluate_f1(reference_file, system_file, CAPTION_TAG, ttml=False, line_tag=LINE_TAG, caption_tag=CAPTION_TAG)
    evaluate_f1(reference_file, system_file, LINE_TAG, ttml=False, line_tag=LINE_TAG, caption_tag=CAPTION_TAG)


if __name__ == '__main__':
    main(parse_args())
