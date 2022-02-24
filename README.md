# EvalSubtitle

This repo will be used to share document and code related to the evaluation of caption segmentation.


python>=3.6.0


This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

## Evaluating subtitle segmentation with a reference file

### Metrics

The script evalsub_main.py allows the computation of the following metrics:
* Precision
* Recall
* F1
* Pk
* WinDiff (WindowDiff)
* SegSim (Segmentation Similarity)
* BoundSim (Boundary Similarity)
* BLEU_br
* BLEU_nb
* TER_br
* CPL_conf
* Sigma

### File format

System and reference files should be in one of these formats: tagged text, or srt.

Tagged text files contain text interspersed with segmentation symbols: \<eol\>, which indicates a change of line within the same screen, and \<eob\>, which indicates the end of a subtitle block and a subsequent change of screen.
A line of the file corresponds to a full sentence.

System and reference srt files should contain the same number of sentences for the computation of certain metrics (BLEU_br, BLEU_nb, Sigma, TER_br).

### Parameters

* --all, -a: Compute all metrics.
* --standard, -std: Compute all metrics that require identical text.
* --end2end, -e2e: Compute all metrics that do not require identical text.
* --include, -i: Compute only these metrics.
* --exclude, -e: Compute all but these metrics.
* --system_files, -sys: Segmented subtitle files to evaluate (by default, the system files in data).
* --reference_file, -ref: Reference segmented subtitle file (by default, the reference file in data).
* --results_file, -res: CSV file where to write the results.
* --srt, -srt: Wether the subtitle files are in srt format.
* --window_size, -k: Window size for the window-based segmentation evaluation (by default, is computed as half of the mean reference segmentation length).
* --max_transpo, -n: Maximum distance that can be accounted as a boundary transposition error (by default, 2).
* --max_cpl, -cpl: Maximum allowed length for subtitle lines (by default, 42).

Note: the metric names have to be written as in the list above.

### Example

Compute all end-to-end metrics but TER_br, for the automatic subtitles in data:

`python evalsub_main.py -res results.csv -e2e -e TER_br`

Compute only Sigma, BLEU_br and BLEU_nb, for the automatic subtitles in data:

`python evalsub_main.py -res results.csv -i Sigma BLEU_br BLEU_nb`
