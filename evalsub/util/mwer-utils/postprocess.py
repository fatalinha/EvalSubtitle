# concatenate aligned files adding the breaks from the reference
import sys
from os import listdir
from os.path import join
from sacremoses import MosesDetokenizer

indir = sys.argv[1]
outfile = sys.argv[2]
reference = sys.argv[3]
tl = sys.argv[4]
md = MosesDetokenizer(lang=tl)


def collect_reference_boundaries(reference_file):
    bound_dict = dict()
    with open(reference_file) as ref:
        for e, line in enumerate(ref):
            boundaries = [i for i in line.rstrip().split(' ') if i in ['<eob>', '<eol>']]
            e = str(e).zfill(4)
            bound_dict[e] = boundaries
    return bound_dict


lines = []
sub_boundaries = collect_reference_boundaries(reference)
print("Post-processing hypotheses in " + indir)
for f in sorted(listdir(indir)):
    if f.endswith('.hyp'):
        # Get the line number and the corresponding breaks in the ref
        line_no = f.split('.')[0]
        breaks_line = sub_boundaries[line_no]
        print(line_no)
        with open(join(indir, f)) as inf:
            # get number of subtitles in resegmented output
            new_lines = []
            for i, sub in enumerate(inf):
                print(sub)
                try:
                    boundary = breaks_line[i]
                except IndexError:
                    boundary = '<eob>'
                sub = md.detokenize(sub.split(' '))
                print(sub)
                new_lines.append(' '.join([sub.rstrip(), boundary]))
            lines.append(' '.join(new_lines))

# write output file
with open(outfile, 'w') as out:
    out.write('\n'.join(lines))
print("Written output file " + outfile)
