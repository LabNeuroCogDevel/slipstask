#!/usr/bin/env bash
set -euo pipefail
trap 'e=$?; [ $e -ne 0 ] && echo "$0 exited in error"' EXIT
cd $(dirname "$0")

#
# 20200727WF - init
#    generate timing scores
#
ntrs=55
tr=1
for trial_1d in seeded/[0-9]*/trials_val.1D; do
   tdir=$(dirname $trial_1d)
   [ ! -d $tdir ] && echo "bad 1D timing glob $trial_1d" && exit 1
   suffix=@${tr}_$ntrs
   time_out=$tdir/timing$suffix.txt
   # dont redo
   [ -r $time_out ] && continue

   3dDeconvolve -nodata $ntrs $tr \
      -num_stimts 2 \
      -stim_times  1 $tdir/trials_val.1D    'BLOCK(1.5)' -stim_label  1 val \
      -stim_times  2 $tdir/trials_deval.1D  'BLOCK(1.5)' -stim_label  2 deval \
      -num_glt 1\
      -gltsym "SYM: +val -deval" -glt_label 1 val-deval \
      -x1D $tdir/X.xmat$suffix.1D |
   tee $tdir/convolve$suffix.txt

  
   1d_tool.py -cormat_cutoff 0.1 -show_cormat_warnings -infile $tdir/X.xmat$suffix.1D | 
     tee $time_out
done
