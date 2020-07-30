#!/usr/bin/env python3
import sys
import os
import math
import numpy as np
import pandas as pd
sys.path.insert(1, os.path.realpath(os.path.pardir))
from soapy.task_types import TrialType, PhaseType
from soapy.task import FabFruitInfo
os.chdir(os.path.dirname(__file__))


DD = {PhaseType.DD: {
       'blocks': 9, 'reps': 2,
       'itis': [1, 1, 1, 2, 2, 5],
       'grid': 5.0, 'dur': 1.5, 'score': 2,
       'ndevalblocks': 3,
       'combine': True}}
TR = 1
TOTAL_SECS = 445

# computer other setting variables
nTR = math.ceil(TOTAL_SECS/TR)
trial_dur = DD[PhaseType.DD]['dur']


def rep_cnts(x, rep_max=4, reset_every=12):
    """dumb quick way to count reps"""
    cntd = {0: 0}
    if x is None or len(x) <= 1:
        return cntd

    isreps = [x[i] == x[i+1] for i in range(len(x)-1)]
    cnt = 0
    for i, isrep in enumerate(isreps):
        if isrep and i < reset_every:
            cnt += 1
        else:
            if cnt >= rep_max:
                cnt = rep_max
            cntd[cnt] = cntd.get(cnt, 0)+1
            cnt = 0
    return(cntd)


def rep_okay(cntd, n):
    """critera for if we have an okay number of reps"""
    # total = sum([ v*n for v,n in zip(cntd.values(), cntd.keys())])
    if cntd.get(4, 0) > 1:
        print(f'{cntd} has too many 3+s')
        return False
    if cntd.get(3, 0) > 1:
        print(f'{cntd} has too many 3s')
        return False
    if cntd.get(2, 0) > 3:
        print(f'{cntd} has too many 2s')
        return False
    if cntd[0] < n/4:
        print(f'{cntd} has too few 0s (n={n}, min={n/4})')
        return False
    return True


def timing_okay(d):
    """report if repeats are not crazy (not too many in a row) """
    # only grab SHOW. and only if not SOA or DD deval
    have_side = (d.ttype == TrialType.SHOW) &\
        np.logical_not(d.deval & [x in [PhaseType.SOA, PhaseType.DD]
                                  for x in d.phase])
    if np.where(have_side)[0].size == 0:
        raise Exception('no sides in dataframe')
    a = d[have_side].groupby('blocknum').agg({'cor_side': lambda x: rep_okay(rep_cnts(x.values), 7)})
    return all(a.cor_side)


def write_1d(d: pd.DataFrame, bcol='blocknum', fname=None):
    x = d.groupby(bcol).agg({
            'onset': lambda x: " ".join(['%.02f' % a for a in x.values])}).\
        onset.values
    if not fname:
        return(x)
    with open(fname, 'w') as f:
        f.write("\n".join(x))


for _ in range(100):
    seed_int = int(np.random.uniform(10**10))

    outdir = f'seeded/{TR}_{TOTAL_SECS}/{seed_int}'
    if os.path.exists(f"{outdir}/timing_cor.txt"):
        continue

    seed = np.random.default_rng(seed_int)
    info = FabFruitInfo(phases=DD, seed=seed)

    # remove blocks so write_1d doesn't separate them
    # useful for 'combine': True -- when all(diff(onset)>0)
    info.timing['blocknum'] = 1

    if not timing_okay(info.timing):
        continue
    print('okay')
    os.makedirs(outdir)
    info.timing.to_csv(f'{outdir}/DD.csv')

    # all onsets
    d = info.timing[info.timing.ttype == TrialType.SHOW]
    write_1d(d, fname=f'{outdir}/trial.1D')
    write_1d(d[d.deval], fname=f'{outdir}/trials_deval.1D')
    write_1d(d[np.logical_not(d.deval)], fname=f'{outdir}/trials_val.1D')

    for side in ['L', 'R']:
        side_d = d[d.cor_side == side]
        write_1d(side_d, fname=f'{outdir}/{side}.1D')
        write_1d(side_d[side_d.deval], fname=f'{outdir}/{side}_deval.1D')
        write_1d(side_d[np.logical_not(side_d.deval)], fname=f'{outdir}/{side}_val.1D')

    # run deconvolve -nodata to get timining correlations
    # output to textfiles for later
    os.system(f"""
      cd {outdir};
      3dDeconvolve -nodata {nTR} {TR} \
         -polort 3 \
         -num_stimts 2 \
         -stim_times  1 trials_val.1D    'BLOCK({trial_dur})' -stim_label  1 val \
         -stim_times  2 trials_deval.1D  'BLOCK({trial_dur})' -stim_label  2 deval \
         -num_glt 1\
         -gltsym "SYM: +val -deval" -glt_label 1 val-deval \
         -x1D X.xmat.1D | tee convolve.txt;
      1d_tool.py -cormat_cutoff 0.1 -show_cormat_warnings -infile X.xmat.1D \
        2>timing_cor.warn | tee timing_cor.txt
      """)
    #break
