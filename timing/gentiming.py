#!/usr/bin/env python3
import sys
import os
import math
import numpy as np
import pandas as pd
sys.path.insert(1, os.path.realpath(os.path.pardir))
import soapy
import soapy.info
from soapy.task_types import TrialType, PhaseType
os.chdir(os.path.dirname(__file__))


# 9 blocks * 6 boxes * 2 reps = 108 trials
# each has duration DUR (1.5) + ITI duration (1-5s, mean 2) = 3.5
# each block starts with 5 second grid and ends with 2 second score
# run has 3 seconds of fix to start
# 3 + 108*3.5 + 9*(5+2)  = 444 seconds

# want maybe 10 seconds at the end to finish hrf
# total time = 454

TR = 1
MAX_DEVAL_REP = 15
# 36 devalued (9 blocks, 2 deval blocks rep 2x in each)
# dont want to have devalued box (cor resp is no resp)
# shown right after another one more than 7 different times

DD = {PhaseType.DD: {
    'itis': [1, 1, 1, 2, 2, 5],  # iti dur ratio: 3x 1s dur for every 1x 5s
    'dur': 1.5,                  # time allowed for response
    'grid': 5.0, 'score': 2,     # grid at start, score at end (durations)
    'blocks': 9, 'reps': 2,      # 9 reps with every box seen twice
    'ndevalblocks': 3,           # each box is devalued 3 times
    'combine': True,
    'total_secs': 454}}            # block onset times are combined into one run


# ITI dist accross 108 trials like
#      n iti_dur
#     54 1.0
#     36 2.0
#     18 5.0


# (avg iti 2 + 1.5 show + 1 fbk)*6*2 + 2
ID = {PhaseType.ID: {
    'itis': [1, 1, 1, 2, 2, 5],
    'dur': 1.5,
    'fbk': 1,
    'score': 2,
    'blocks': 1,
    'reps': 2,
    'total_secs': 56+12}}

OD = {PhaseType.OD: {
     'itis': [1, 1, 1, 2, 2, 5],
     'dur': 1.5,
     'score': 2,
     'total_secs': 140}}

def rep_cnts(x, rep_max=4, reset_every=12):
    """dumb quick way to count reps - almost `rle`
    @param x - series of e.g. L/R
    @param rep_max - above this, increment as this number
    @param reset_every - start again after this many. e.g. after a block

    we are counting times a side is repeated. not total length of sequence
    L L L => 2 repeats
    L R   => 0 repeats
    >>> seq = ['L','L','L','R','R','L']
    >>> rep_cnts(seq)
    {0: 1, 2: 1, 1: 1}
    >>> rep_cnts(seq, rep_max=1)
    {0: 1, 1: 2}
    >>> rep_cnts(seq, reset_every=2)
    {0: 4, 1: 1}
    """
    cntd = {0: 0}
    if x is None or len(x) <= 1:
        return cntd

    isreps = [x[i] == x[i+1] for i in range(len(x)-1)]
    cnt = 0
    for i, isrep in enumerate(isreps):
        if isrep and (i+1) % reset_every != 0:
            cnt += 1
        else:
            if cnt >= rep_max:
                cnt = rep_max
            cntd[cnt] = cntd.get(cnt, 0)+1
            cnt = 0
    # finish last one
    final = cnt if cnt <= rep_max else rep_max
    cntd[final] = cntd.get(final, 0) + 1
    
    return(cntd)


def rep_okay(cntd, min_single):
    """critera for if we have an okay number of reps
    @param cntd - from `rep_cnts`
    @param min_single - must have this many singles (eg. L,R,L,R is 4 singles)
    >>> rep_okay({4:3, 0:1}, 1)
    {4: 3, 0: 1} has too many 4+s
    False
    >>> rep_okay({2:7, 0:1}, 1)
    {2: 7, 0: 1} has too many 2s
    False
    >>> rep_okay({2:2, 0:1}, 1)
    True
    >>> rep_okay({0:1}, 5)
    {0: 1} has too few 0s (want 0: >=5)
    False
    """
    # total = sum([ v*n for v,n in zip(cntd.values(), cntd.keys())])
    if cntd.get(4, 0) > 1:
        print(f'{cntd} has too many 4+s')
        return False
    if cntd.get(3, 0) > 3:
        print(f'{cntd} has too many 3s')
        return False
    if cntd.get(2, 0) > 10:
        print(f'{cntd} has too many 2s')
        return False
    if cntd[0] < min_single:
        print(f'{cntd} has too few 0s (want 0: >={min_single})')
        return False
    return True


def timing_okay(d):
    """report if repeats are not crazy (not too many in a row) """

    # ## check deval box are not one after the other
    s = d[d.ttype == TrialType.SHOW].reset_index()
    dv_rep = sum(np.diff(s.trial[s.deval]) == 1)
    if dv_rep > MAX_DEVAL_REP:
        print(f"devalued box repeated {dv_rep} > {MAX_DEVAL_REP} times")
        return False

    # only grab SHOW. and only if not SOA or DD deval
    # don't count sequence:  R, devalued R (cor resp is no resp) as a repeat
    have_side = (d.ttype == TrialType.SHOW) &\
        np.logical_not(d.deval & [x in [PhaseType.SOA, PhaseType.DD]
                                  for x in d.phase])
    if np.where(have_side)[0].size == 0:
        raise Exception('no sides in dataframe')
    # cant have too many side repeates
    # also need at least 3 no repeats (e.g. L R L R R ...)
    a = d[have_side].groupby('blocknum').\
        agg({'cor_side': lambda x: rep_okay(rep_cnts(x.values), min_single=3)})

    return all(a.cor_side)


def write_1d(d: pd.DataFrame, bcol='blocknum', fname=None):
    """make afni 1D from onset column of dataframe d
    groups by blocknum column
    TODO: add '*' for empty block
    """
    x = d.groupby(bcol).agg({
            'onset': lambda x: " ".join(['%.02f' % a for a in x.values])}).\
        onset.values
    if not fname:
        return(x)
    with open(fname, 'w') as f:
        f.write("\n".join(x))


def gen_timing(_, phase_info=DD, seed_int=None):
    """make a random timing, check we don't repeat too much. run 3dDeconvolve
    """
    global TR

    # what phase are we working on?
    outname=[x.name for x in phase_info.keys()]
    if len(outname) !=1:
        raise Exception(f"expect only 1 phase key in {phase_info}")
    outname=outname[0]

    p = phase_info[PhaseType[outname]]
    TOTAL_SECS = p['total_secs']
    DUR = p['dur']
    # compute other setting variables
    nTR = math.ceil(TOTAL_SECS/TR)

    # gen random seed
    if not seed_int:
        seed_int = int(np.random.uniform(10**10))

    # setup path
    outdir = f'seeded/{outname}/tr{TR}_dur{DUR}_{TOTAL_SECS}total/{seed_int}'
    if os.path.isdir(outdir):
        return True

    # generate task
    seed = np.random.default_rng(seed_int)
    info = soapy.info.FabFruitInfo(phases=phase_info, seed=seed)
    
    # check again again incase we had a race condition when parallizing
    if os.path.isdir(outdir):
        return True

    # remove blocks so write_1d doesn't separate them
    # useful for 'combine': True -- when all(diff(onset)>0)
    info.timing['blocknum'] = 1

    # we dont want too many repeats of anything
    if not timing_okay(info.timing):
        return False

    print('okay')
    os.makedirs(outdir, exist_ok=True)
    info.timing.to_csv(f'{outdir}/{outname}.csv')
    print(outdir)

    # all onsets
    d = info.timing[info.timing.ttype == TrialType.SHOW]
    write_1d(d, fname=f'{outdir}/trial.1D')
    write_1d(d[d.deval], fname=f'{outdir}/trials_deval.1D')
    write_1d(d[np.logical_not(d.deval)], fname=f'{outdir}/trials_val.1D')

    for side in ['L', 'R']:
        # for DD and SOA, devalued has no correct side
        # whereas, for OD, devalued still has a left or right cor resp
        if outname in ['SOA','DD']:
            is_side = [x[0] == side for x in d.LR1]
            side_d = d[is_side]
        else:
            side_d = d[d.cor_side == side]

        write_1d(side_d, fname=f'{outdir}/{side}.1D')
        write_1d(side_d[side_d.deval], fname=f'{outdir}/{side}_deval.1D')
        write_1d(side_d[np.logical_not(side_d.deval)], fname=f'{outdir}/{side}_val.1D')

    run_decon(outdir, outname, nTR, DUR)
    return True


def run_decon(outdir, outname, nTR, DUR):
    """ run deconvolve -nodata to get timining correlations
    output to textfiles for later
    """
    global TR

    if outname in ['DD', 'SOA']:
        os.system(f"""
          cd {outdir};
          3dDeconvolve -nodata {nTR} {TR} \
             -polort 3 \
             -num_stimts 3 \
             -stim_times  1 L_val.1D    'BLOCK({DUR})' -stim_label  1 Lval \
             -stim_times  2 R_val.1D    'BLOCK({DUR})' -stim_label  2 Rval \
             -stim_times  3 trials_deval.1D  'BLOCK({DUR})' -stim_label  3 deval \
             -num_glt 2\
             -gltsym "SYM: +Lval -Rval" -glt_label 1 L-R \
             -gltsym "SYM: +.5*Lval +.5*Rval -deval" -glt_label 2 val-deval \
             -x1D X.xmat.1D | tee convolve.txt;
          """)
    elif outname in ['ID', 'OD']:
        os.system(f"""
          cd {outdir};
          3dDeconvolve -nodata {nTR} {TR} \
             -polort 3 \
             -num_stimts 2 \
             -stim_times  1 L_val.1D    'BLOCK({DUR})' -stim_label  1 Lval \
             -stim_times  2 R_val.1D    'BLOCK({DUR})' -stim_label  2 Rval \
             -num_glt 1\
             -gltsym "SYM: +Lval -Rval" -glt_label 1 L-R \
             -x1D X.xmat.1D | tee convolve.txt;
          """)
    else:
        raise Exception(f'unknown type {outname}')

    os.system(f"""
      cd {outdir};
      1d_tool.py -cormat_cutoff 0.1 -show_cormat_warnings -infile X.xmat.1D \
            2>timing_cor.warn | tee timing_cor.txt
            """)


if __name__ == "__main__":
    for _ in range(10000):
        gen_timing(_, DD)
        gen_timing(_, ID)
        gen_timing(_, OD)

    # from multiprocessing import Pool
    # p = Pool(2)
    # p.map(gen_timing, range(100))
