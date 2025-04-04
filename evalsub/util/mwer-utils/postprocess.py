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
from os import listdir
from os.path import join

from sacremoses import MosesDetokenizer


def collect_system_boundaries(system_file):
    bound_dict = dict()
    with open(system_file) as ref:
        for e, line in enumerate(ref):
            boundaries = [i for i in line.rstrip().split(' ') if i in ['<eob>', '<eol>']]
            e = str(e).zfill(4)
            bound_dict[e] = boundaries
    return bound_dict


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_dir', '-i', type=str)
    parser.add_argument('--output_file', '-o', type=str)
    parser.add_argument('--system_file', '-sys', type=str)
    parser.add_argument('--target_language', '-tl', type=str)

    args = parser.parse_args()
    return args


def main(args):
    indir = args.input_dir
    outfile = args.output_file
    sys_file = args.system_file
    tl = args.target_language

    md = MosesDetokenizer(lang=tl)

    lines = []
    sub_boundaries = collect_system_boundaries(sys_file)
    print("Post-processing hypotheses in " + indir)
    for f in sorted(listdir(indir)):
        if f.endswith('.hyp'):
            # Get the line number and the corresponding breaks in the ref
            line_no = f.split('.')[0]
            breaks_line = sub_boundaries[line_no]
            with open(join(indir, f)) as inf:
                # get number of subtitles in resegmented output
                new_lines = []
                for i, sub in enumerate(inf):
                    try:
                        boundary = breaks_line[i]
                    except IndexError:
                        boundary = '<eob>'
                    sub = md.detokenize(sub.split(' '))
                    new_lines.append(' '.join([sub.rstrip(), boundary]))
                lines.append(' '.join(new_lines))

    # write output file
    with open(outfile, 'w') as out:
        out.write('\n'.join(lines))
    print("Written output file " + outfile)


if __name__ == '__main__':
    main(parse_args())
