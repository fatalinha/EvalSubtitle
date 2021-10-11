# \<eol> + \<eob> segmentation

| System       | window_size | Pk    | WindowDiff | Precision | Recall | F1  |
|--------------|-------------|-------|------------|-----------|--------|-----|
| every42chars | 3           | 0.353 | 0.387      | 0.379     | 0.328  |0.352|
| Segmenter    |             |       |            | 0.807     | 0.776  |0.791|


# \<eob> only segmentation

| System       | window_size | Pk    | WindowDiff | Precision | Recall | F1  |
|--------------|-------------|-------|------------|-----------|--------|-----|
| every42chars | 4           | 0.301 | 0.336      | 0.372     | 0.322  |0.345|
| Segmenter    |             |       |            | 0.775     | 0.746  |0.761|


# \<eol> only segmentation

| System       | window_size | Pk    | WindowDiff | Precision | Recall | F1  |
|--------------|-------------|-------|------------|-----------|--------|-----|
| every42chars | 7           | 0.441 |  0.448     | 0.074     | 0.06   |0.066|
| Segmenter    |             |       |            | 0.550     | 0.464  |0.503|
