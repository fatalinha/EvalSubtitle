#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

""" Split file by subtitle blocks, one block per line """
import sys
from os.path import join
import re


infile = sys.argv[1]
outdir = sys.argv[2]
suffix = sys.argv[3]
tl = sys.argv[4]
line_tag = '<eol>'
caption_tag = '<eob>'


print("Splitting and tokenizing sentences in " + outdir)
with open(infile) as inf:
    for e, line in enumerate(inf):
        outfile = join(outdir, str(e).zfill(4) + '.' + suffix)
        # Tokenize and restore boundaries
        text = line.replace('< ', '<').replace(' >', '>')
        # Split sentences at subtitle boundaries
        text = text.rstrip().replace(line_tag, '\n').replace(caption_tag, '\n')
        # Removing spaces besides boundaries
        text = re.sub(r"( )?(%s)( )?" % '\n', r"\2", text)

        with open(outfile, 'w') as out:
            out.write(text)

print("Done!")
