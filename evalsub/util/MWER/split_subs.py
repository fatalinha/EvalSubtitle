# Split test by subtitle blocks, one block per line
import sys
from os.path import join
import re
from sacremoses import MosesTokenizer
from sacremoses import MosesPunctNormalizer


infile = sys.argv[1]
outdir = sys.argv[2]
suffix = sys.argv[3]
tl = sys.argv[4]
mt = MosesTokenizer(lang=tl)
mpn = MosesPunctNormalizer()
line_tag = '<eol>'
caption_tag = '<eob>'


def deescape_special_chars(sent):
    sent = sent.replace('&lt; ','<').replace(' &gt;','>').replace('&quot;','"').replace('&apos;', "'").replace('&amp;','&').replace('&bar;', '|')
    return sent


print("Splitting and tokenizing sentences in " + outdir)
with open(infile) as inf:
    for e, line in enumerate(inf):
        outfile = join(outdir, str(e).zfill(4) + '.' + suffix)
        # Tokenize
        text = mt.tokenize(line, return_str=True)
        # normalise
        text = mpn.normalize(deescape_special_chars(text))
        # Split sentences at subtitle boundaries
        text = text.rstrip().replace('<eol>', '\n').replace('<eob>', '\n')
        # Removing spaces besides boundaries
        text = re.sub(r"( )?(%s)( )?" % '\n', r"\2", text)

        with open(outfile, 'w') as out:
            out.write(text)
            print(outfile)
print("Done!")
