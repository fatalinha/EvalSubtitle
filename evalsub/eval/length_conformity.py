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
import re
import statistics


def len_conformity(line, MAX_LEN):
    mean = []
    conforming = 0
    subs = re.split(r' <eob>| <eol>', line)[:-1]
    total = len(subs)
    for s in subs:
        sub_len = len(list(s.strip()))
        mean.append(sub_len)
        if sub_len <= MAX_LEN:
            conforming += 1
    return conforming, total, mean


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--system_file', '-sf', type=str,
                        help="Segmented subtitle file to evaluate.")
    parser.add_argument('--max_length', '-len', type=int,
                        help="Maximum allowed length for subtitles")

    args = parser.parse_args()
    return args


def len_process(system_file, max_len):

    conforming_subs = 0
    total_subs = 0
    mean_sub_len = []

    with open(system_file) as s:
        for line in s:
            conf, tot, mean = len_conformity(line, MAX_LEN=max_len)
            conforming_subs += conf
            total_subs += tot
            mean_sub_len += mean
        try:
            len_conf = round(conforming_subs / total_subs, 2)
            print('Length conformity: ' + str(len_conf) +
                  ' Number of subtitles: ' + str(conforming_subs) + '/' + str(total_subs))
            print('Mean subtitle length: ' + str(round(statistics.mean(mean_sub_len), 2)) +
                  ' Stdev:' + str(round(statistics.stdev(mean_sub_len), 2)))
        except ZeroDivisionError:
            len_conf = 0

        return len_conf


def main(args):
    system_file = args.system_file
    max_len = args.max_length

    len_process(system_file, max_len)


if __name__ == '__main__':
    main(parse_args())
