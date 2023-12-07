# EvalSubtitle

EvalSubtitle is a tool for reference-based evaluation of subtitle segmentation.

The repository contains the Subtitle Segmentation Score (Sigma), specifically tailored for evaluating segmentation from system outputs where the text is not identical to a reference (imperfect texts).
EvalSub also contains a collection of standard segmentation metrics (F1, WindowDiff etc.) as well as subtitling evaluation metrics: BLEU on segmented (BLEU_br) and non-segmented text (BLEU_nb), and TER_br.


More details can be found in the paper.


python>=3.6.0


## Reference-based evaluation of subtitle segmentation

### Metrics

The script `evalsub_main.py` allows the computation of the following metrics:

Standard segmentation metrics:
* `Precision`
* `Recall`
* `F1`
* `Pk`
* `WinDiff` (WindowDiff)
* `SegSim` (Segmentation Similarity)
* `BoundSim` (Boundary Similarity)

Subtitling evaluation metrics
* `BLEU_br`
* `BLEU_nb`
* `TER_br`
* `CPL_conf`
* `Sigma`

### File format

System and reference files should be in one of these formats: tagged text, or SRT.

Tagged text files contain text interspersed with segmentation symbols: `<eol>`, which indicates a change of line within the same screen, and `<eob>`, which indicates the end of a subtitle block and a subsequent change of screen.
A line of the file corresponds to a full sentence.

System and reference files should contain the same number of sentences for the computation of certain metrics (BLEU_br, BLEU_nb, Sigma, TER_br).
If not, the `auto_segmentation` option can be used to automatically segment system output according to reference sentences (implementation from [SubER Levenshtein alignment tool](https://github.com/apptek/SubER/tree/main#scoring-non-parallel-subtitle-files)).

### Parameters

* `--all`, `-a`: Compute all metrics.
* `--standard`, `-std`: Compute all metrics that require identical/perfect text.
* `--end2end`, `-e2e`: Compute all metrics that do not require identical/perfect text.
* `--include`, `-i`: Compute only the specified metrics.
* `--exclude`, `-e`: Compute all but the specified metrics.
* `--text`, `-t`: Whether the text from system subtitles is identical to the text from reference subtitles ("perfect"), or not ("imperfect"). (Can be used as a safeguard to prevent computing standard metrics with imperfect text)
* `--system_files`, `-sys`: Segmented subtitle files to evaluate (by default, the system files in data).
* `--reference_file`, `-ref`: Reference segmented subtitle file (by default, the reference file in data).
* `--results_file`, `-res`: CSV file where to write the results.
* `--srt`, `-srt`: Whether the subtitle files are in SRT format.
* `--auto_segmentation`, `-as`: Whether to use automatic segmentation for system sequences.
* `--window_size`, `-k`: Window size for the window-based (Pk, WinDiff) segmentation evaluation (by default, is computed as half of the mean reference segmentation length).
* `--max_transpo`, `-n`: Maximum distance that can be accounted as a boundary transposition error (by default, 2). Specific to SegSim and BoundSim.
* `--max_cpl`, `-cpl`: Maximum allowed length for subtitle lines (by default, 42).
* `--confidence_interval`, `-ci`: If set, compute (and print) the confidence interval (CI) for BLEU and Sigma. The CI is computed using bootstrap resampling (with 95% confidence).

Note: the metric names have to be written as in the list above.

### Example

Compute all end-to-end metrics but TER_br, for the automatic subtitles in data:

```
python evalsub_main.py -res results.csv -e2e -e TER_br
```

Compute only Sigma, BLEU_br and BLEU_nb, for the automatic subtitles in data:

```
python evalsub_main.py -res results.csv -i Sigma BLEU_br BLEU_nb
```

Compute all metrics that are compatible with imperfect text:

```
python evalsub_main.py -res results.csv -a -t imperfect
```

also equivalent to

```
python evalsub_main.py -res results.csv -e2e
```

### Citation

If you use EvalSubtitle in your research, please cite the following paper:

[Alina Karakanta, François Buet, Mauro Cettolo and François Yvon. (2022). Evaluating Subtitle Segmentation for End-to-end Generation Systems. In _Proceedings of LREC 2022_.](https://aclanthology.org/2022.lrec-1.328/)

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
