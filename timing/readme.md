# MR timing for DD block

## Code
- `gentiming.py` runs through random seeds to generate files, esp `seeded/tr${TR}_dur${DUR}_${TIME}total/$seed/convolve.txt`
  * q.v. embeded `3dDeconvolve` call
  * contrasts: Left - Right, and valued - devalued

- `collect` makes `seeded/tr${TR}_dur${DUR}_${TIME}total.txt` on `_h` and `_LC` outputs
  * sorted by `val-deval_LC`
  * min is best

- `pick` - put the top 10 into ../soapy/timing/DD/*csv
  * will be included with python package (see ../MANIFEST.in)

> the optimal experimental design is chosen by minimizing the "norm. std. dev.".
https://afni.nimh.nih.gov/afni/community/board/read.php?1,42880,42890

## Picking Timing

In DD trials, valued boxes have either a Left or Right correct response.
The correct response to a devalued is no response.
Viewed this way, there are 3 trial types: `Lval`, `Rval`, and `deval`.

`sort -k6n seeded/tr1_dur1.5_454total.txt|sed -n '1,2p;$p' | column -t`

```
file                                   L-R_LC  Lval_h  Rval_h  deval_h  val-deval_LC
seeded/tr1_dur1.5_454total/1847595753  0.0871  0.0744  0.0685  0.0674   0.0647
seeded/tr1_dur1.5_454total/8787546028  0.0916  0.0793  0.0859  0.0764   0.0967
```
