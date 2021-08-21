# Comparing existing segmentation metrics

| Metric | Needs ref | Suited for end-to-end | Implementation |
|--------|-----------|-----------------------|----------------|
| F1     | yes       | no                    |                |
| Pk     | yes       | no                    | [SegEval](https://pypi.org/project/segeval/) |
| WindowDiff | yes   | no                    | [SegEval](https://pypi.org/project/segeval/) |
| Segmentation Similarity | yes | no         | [SegEval](https://pypi.org/project/segeval/) |
| Boundary Similarity | yes | no             | [SegEval](https://pypi.org/project/segeval/) |
| Boundary Edit Distance | yes | no          | [SegEval](https://pypi.org/project/segeval/) |
| BLEU(-br) | yes    | yes                   | [SacreBLEU](https://github.com/mjpost/sacrebleu)? | 
| TER-br | yes       | yes                   |                |

## Contrastive pairs

Possible rules to use for crafting an error example from a reference:
- shift a boundary of *n* words on the right or left
- insert new boundaries into free slots, and/or remove existing boundaries
- change the type of a boundary (end-of-line/end-of-block)
