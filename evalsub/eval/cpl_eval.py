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
Computes the percentage of subtitles conforming to a max. length
"""

import argparse
import os
import re
import statistics
import sys

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst
from evalsub.util.srt import SrtReader


def cpl_process(sys_file_path, max_cpl=cst.MAX_CPL, srt=False, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG):
    if srt:
        srt_reader = SrtReader(sys_file_path)
        captions = srt_reader.read_all()
        lines = list()
        for caption in captions:
            lines += caption

    else:
        tagged_str = ' '.join([line.strip() for line in open(sys_file_path).readlines()])
        # Removing spaces around boundaries
        tagged_str = re.sub(r"( )?(%s|%s)( )?" % (line_tag, caption_tag), r"\2", tagged_str)
        # Removing (potential) ending boundary
        tagged_str = re.sub(r"(%s|%s)$" % (line_tag, caption_tag), r"", tagged_str)
        # Split at boundaries
        lines = re.split(r"%s|%s" % (line_tag, caption_tag), tagged_str)

    cpls = [len(line) for line in lines]
    n_cpls = len(cpls)
    n_conforming_cpls = sum([cpl <= max_cpl for cpl in cpls])
    cpl_conformity = -1
    try:
        cpl_conformity = 100 * (n_conforming_cpls / n_cpls)
        # print('Length conformity: %.2f %% (%d/%d)' % (100 * cpl_conformity, n_conforming_cpls, n_cpls))
        # print('Mean line length: %2.f Stdev: %2.f' % (statistics.mean(cpls), statistics.stdev(cpls)))
    except (ZeroDivisionError, statistics.StatisticsError):
        pass

    return cpl_conformity


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--system_file', '-sf', type=str,
                        help="Segmented subtitle file to evaluate.")
    parser.add_argument('--max_length', '-len', type=int, default=cst.MAX_CPL,
                        help="Maximum allowed length for subtitles")
    parser.add_argument('--srt', '-srt', action='store_true',
                        help="Wether the subtitle files are in srt format.")

    args = parser.parse_args()
    return args


def main(args):
    sys_file_path = args.system_file
    max_cpl = args.max_length
    srt = args.srt

    cpl_process(sys_file_path, max_cpl=max_cpl, srt=srt)


if __name__ == '__main__':
    main(parse_args())