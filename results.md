# Results on MuST-Cinema en (from the en-fr split)

## \<eol> + \<eob> segmentation

| System       | window_size | ↓Pk    | ↓WindowDiff | ↑Precision | ↑Recall | ↑F1  | ↑BLEU |↑BLEUsame|↓TER-br| TER-same|
|--------------|-------------|--------|-------------|------------|---------|------|-------|---------|-------|---------|
| every42chars | 3           | 0.353  | 0.387       | 0.379      | 0.328   |0.352 | 63.81 | 66.08   | 12.59 | 10.40 |
| Segmenter    | 3           | 0.142  | 0.150       | 0.807      | 0.776   |0.791 | 87.80 | 89.57   | 4.79  | 3.77  |

*Note: BLEU and TER take into account the type of break here (no replacement with <eox>). TER-br on untokenised text.
  
## \<eob> only segmentation

| System       | window_size | ↓Pk    | ↓WindowDiff | ↑Precision | ↑Recall | ↑F1  | ↑BLEU |↓TER-br|
|--------------|-------------|--------|-------------|------------|---------|------|-------|-------|
| every42chars | 4           | 0.301  | 0.336       | 0.372      | 0.322   |0.345 | 78.05 | 7.84 |
| Segmenter    | 4           | 0.101  | 0.110       | 0.775      | 0.746   |0.761 | 94.19 | 2.07 |


## \<eol> only segmentation

| System       | window_size | ↓Pk    | ↓WindowDiff | ↑Precision | ↑Recall | ↑F1  | ↑BLEU |↓TER-br|
|--------------|-------------|--------|-------------|------------|---------|------|-------|-------|
| every42chars | 7           | 0.441  |  0.448      | 0.074      | 0.06    |0.066 | 75.02 | 8.15 |
| Segmenter    | 7           | 0.243  |  0.245      | 0.550      | 0.464   |0.503 | 86.39 | 4.34 |

