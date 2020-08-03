# MR timing for DD block

- `gentiming.py` runs through random seeds to generate files, esp `seeded/tr${TR}_dur${DUR}_${TIME}total/$seed/convolve.txt`
  * cf. embeded `3dDeconvolve` call

- `collect` makes `seeded/tr${TR}_dur${DUR}_${TIME}total.txt` on `_h` and `_LC` outputs
  * contrasts: Left - Right, and valued - devalued

## Picking Timing
`sort seeded/tr1_dur1.5_454total.txt -k6n|sed -n '1,2p;$p'|column -t`

```
file                                   L-R_LC  Lval_h  Rval_h  deval_h  val-deval_LC
seeded/tr1_dur1.5_454total/4946843090  0.0858  0.0724  0.0697  0.0746   0.0707
seeded/tr1_dur1.5_454total/5581004258  0.0881  0.0792  0.0772  0.0789   0.0839
```
