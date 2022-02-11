# Evaluating Subtitle Segmentation for End-to-end Generation systems

This directory contains the scripts to replicate the experiments presented in the paper Evaluating Subtitle Segmentation for End-to-end Generation systems.

## Experiment 1: Metric robustness/sensitivity
python degrade_and_eval.py --output_dir . --reference_file ../data/amara.en --results_file results.csv

## BLEU_br and BLEU_nb: content vs segmentation
python bleu-br_upper_bound.py --output_dir . --reference_file ../data/amara.en --results_file results.csv

## Boundary projection
