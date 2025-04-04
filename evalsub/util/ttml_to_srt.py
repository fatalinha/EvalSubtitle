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
import re

from srt import SrtWriter
from ttml import TtmlReader

DESCRIPTION = """
A script to convert subtitles from a ttml file to an srt file.
Some info such as the color of the lines cannot be transferred in srt.
"""


def convert(input_file_path, output_file_path):
    print('Initializing...')
    ttml_reader = TtmlReader(input_file_path)
    srt_writer = SrtWriter(output_file_path)
    
    lines = ttml_reader.read_caption(flat=False)
    while lines:
        begin, end = ttml_reader.current_time_span()
        srt_writer.write_caption(lines, begin, end)
        
        lines = ttml_reader.read_caption(flat=False)
    
    print('Writing...')
    srt_writer.close()


def convert_multiple(input_file_paths, output_file_paths=None):
    if output_file_paths is None or len(input_file_paths) != len(output_file_paths):
        output_file_paths = [re.sub(r"\.ttml$", ".srt", input_file_path) for input_file_path in input_file_paths]

    for input_file_path, output_file_path in zip(input_file_paths, output_file_paths):
        convert(input_file_path, output_file_path)


# MAIN  ################################################################################################################

def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--input_files', '-if', type=str, nargs='+',
                        help="ttml files to convert")
    parser.add_argument('--output_files', '-of', type=str, nargs='+',
                        help="corresponding srt files (by default only the extension is changed)")

    args = parser.parse_args()
    return args


def main(args):
    input_file_paths = args.input_files
    output_file_paths = args.output_files
    
    convert_multiple(input_file_paths, output_file_paths)


if __name__ == '__main__':
    main(parse_args())
