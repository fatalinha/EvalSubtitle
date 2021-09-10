# coding: utf-8

DESCRIPTION = """
A script to convert subtitles from an srt file to a ttml file.
The color of the lines (not contained in srt) will be set to white by default.
"""

import argparse
import re

from srt import SrtReader
from ttml import TtmlWriter


def convert(input_file_path, output_file_path):
    print('Initializing...')
    srt_reader = SrtReader(input_file_path)
    ttml_writer = TtmlWriter(output_file_path)
    
    while srt_reader.read_caption():
        begin, end = srt_reader.current_time_span()
        lines = srt_reader.current_lines()
        ttml_writer.add_caption(lines, begin, end, 'white')
    
    print('Writing...')
    ttml_writer.write()
    srt_reader.close()


def convert_multiple(input_file_paths, output_file_paths=None):
    if output_file_paths is None or len(input_file_paths) != len(output_file_paths):
        output_file_paths = [re.sub(r"\.srt$", ".ttml", input_file_path) for input_file_path in input_file_paths]

    for input_file_path, output_file_path in zip(input_file_paths, output_file_paths):
        convert(input_file_path, output_file_path)

## MAIN  #######################################################################

def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--input_files', '-if', type=str, nargs='+',
                        help="srt files to convert")
    parser.add_argument('--output_files', '-of', type=str, nargs='+',
                        help="corresponding ttml files (by default only the extension is changed)")

    args = parser.parse_args()
    return args


def main(args):
    input_file_paths = args.input_files
    output_file_paths = args.output_files
    
    convert_multiple(input_file_paths, output_file_paths)


if __name__ == '__main__':
    main(parse_args())