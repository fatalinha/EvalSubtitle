#!/bin/bash

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

# Boundary projection method for projecting the subtitle breaks
# from output file to the reference. Corresponds to experiment 3 of LREC paper.

system_file=$1
reference=$2
system_name=$3
tl=$4

SCRIPTDIR="$(dirname $0)/../evalsub/util/mwer-utils"
SEGDIR="/home/${USER}/mwerSegmenter" #$(dirname $0)/../evalsub/util/mwerSegmenter
OUTDIR="$(dirname $0)/output"
mkdir -p "$OUTDIR"


# check if MWER is downloaded
if test -f "/home/${USER}/mwerSegmenter"; then #'$SEGDIR/segmentBasedOnMWER.sh'; then
  echo "MWER segmenter exists"
else
  echo "Installing MWER first"
  current_location=$(pwd)
  cd "/home/${USER}/" #$(dirname $0)/../evalsub/util/
  git clone https://github.com/PeganovAnton/mwerSegmenter.git
  #wget https://github.com/PeganovAnton/mwerSegmenter/raw/main/mwerSegmenter
  #wget https://raw.githubusercontent.com/PeganovAnton/mwerSegmenter/main/segmentBasedOnMWER.sh
  cd "$current_location"
fi

# Tokenize and segment into subs
mkdir -p "$OUTDIR/tmp"
python3 "$SCRIPTDIR/split_subs.py" $reference $OUTDIR/tmp ref $tl
python3 "$SCRIPTDIR/split_subs.py" $system_file $OUTDIR/tmp sys $tl

for sysr in $OUTDIR/tmp/*.sys
do
	# sgm
	echo $sysr
	perl $SCRIPTDIR/txt2sgm.pl < $sysr > $sysr.src.sgm   # FAKE SOURCE FILE
	perl $SCRIPTDIR/txt2sgm_ref.pl < $sysr > $sysr.subs.sgm  # REFERENCE FILE


	sys_file="${sysr/.sys/.ref}"
	bash "$SEGDIR/segmentBasedOnMWER.sh" $sysr.src.sgm $sysr.subs.sgm $sys_file $system_name $tl $sys_file.sgm -usecase 1
	sed -e "/<[^>]*>/d" $sys_file.sgm > $sys_file.hyp
	rm $sysr.src.sgm
	rm $sysr.subs.sgm

done

python3 "$SCRIPTDIR/postprocess.py" -i "$OUTDIR/tmp" -o "$OUTDIR/projected.$tl" -sys "$system_file" -tl "$tl"
rm -r $OUTDIR/tmp/

