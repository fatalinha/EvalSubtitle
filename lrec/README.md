# Evaluating Subtitle Segmentation for End-to-end Generation systems

This directory contains the scripts to replicate the experiments presented in the paper Evaluating Subtitle Segmentation for End-to-end Generation systems.

## Experiment 1: Metric robustness/sensitivity
```
python degrade_and_eval.py --output_dir . --results_file results_exp1.csv
```

## Experiment 2: BLEU_br and BLEU_nb: content vs segmentation
```
python bleu-br_upper_bound.py --output_dir . --results_file results_exp2.csv
```

## Experiment 3: Boundary projection
This experiment requires the MWER Segmenter, which is downloaded from https://github.com/fatalinha/mwerSegmenter3.git (Please note this experiment only runs in Unix due to this dependency).

Run the boundary projection method
```
bash bound_proj.sh $(dirname $0)/../data/nmt.fr $(dirname $0)/../data/amara.fr nmt fr
```


This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
