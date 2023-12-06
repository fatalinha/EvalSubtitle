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
import random
import sys

# We include the path of the toplevel package in the system path,
# so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst

DESCRIPTION = """
The script breaks sentences before a maximum length is reached. 
Selection of type of break <eol> or <eob> is done randomly by specifying the probability.
"""


def insert_symbol(in_str: str, max_pos: int, symbol: str = cst.CAPTION_TAG, prob: float = cst.PROBA) -> str:

    # If the string is too short, just return it
    if len(in_str) <= max_pos:
        return str(in_str + ' ' + symbol)

    buffer = []
    while len(in_str) > max_pos:
        # Look for the first space from the max length backwards to the beginning
        in_str_before = in_str[0:max_pos]
        first_space_pos = in_str_before[::-1].find(' ')

        # No space?Just return the input string
        # if first_space_pos == -1:
        #    return str(in_str + symbol)

        # Compute the space position in the non-reversed string
        last_space_pos = max_pos - first_space_pos

        # Select type of symbol randomly
        roll = random.random()
        if roll < prob:
            symbol = cst.LINE_TAG
        else:
            symbol = cst.CAPTION_TAG
        # Insert the symbol and return
        buffer.append(in_str[0:last_space_pos] + symbol)
        in_str = in_str[last_space_pos:]
    # Last break must be an <eob>
    buffer.append(in_str + ' <eob>')
    out = ' '.join(buffer)
    return out


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--input_file', '-if', type=str,
                        help="Text file with sentences")
    parser.add_argument('--output_file', '-of', type=str,
                        help="Text file with sentences separated by symbols")
    parser.add_argument('--max_length', '-ln', type=str, default=cst.MAX_CPL,
                        help="Maximum length of subtitle")
    parser.add_argument('--probability', '-p', type=str, default=cst.PROBA,
                        help="Probability of break being <eol>")

    args = parser.parse_args()
    return args


def main(args):
    infile = args.input_file
    outfile = args.output_file
    
    with open(infile, 'r') as inf, open(outfile, 'w') as w:
        for line in inf:
            line = line.strip()
            s2 = insert_symbol(in_str=line, max_pos=cst.MAX_CPL, prob=cst.PROBA)
            print("Input string: '{}'".format(line))
            print("With symbols : '{}'".format(s2))
            w.write(s2 + '\n')


if __name__ == '__main__':
    main(parse_args())
