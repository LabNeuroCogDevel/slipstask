#!/usr/bin/env python3
import slip
import numpy as np
import os

DD = {slip.PhaseType.DD: {
       'blocks': 9, 'reps': 2,
       'itis': [1, 1, 1, 2, 2, 5],
       'grid': 5.0, 'dur': 1.5, 'score': 2,
       'ndevalblocks': 3}}

def rep_cnts(x, rep_max=4, reset_every=12):
    """dumb quick way to count reps"""
    cntd={0: 0}
    if x is None or len(x) <= 1:
        return cntd

    isreps = [x[i] == x[i+1] for i in range(len(x)-1)] 
    cnt=0
    for i, isrep in enumerate(isreps):
        if isrep and i < reset_every:
            cnt += 1
        else:
            if cnt>=rep_max:
                cnt=rep_max
            cntd[cnt]=cntd.get(cnt,0)+1
            cnt=0
    return(cntd)

def rep_okay(cntd, n):
    """critera for if we have an okay number of reps"""
    #total = sum([ v*n for v,n in zip(cntd.values(), cntd.keys())])
    if cntd.get(4,0) >1 :
        print(f'{cntd} has too many 3+s')
        return False
    if cntd.get(3,0) > 1:
        print(f'{cntd} has too many 3s')
        return False
    if cntd.get(2,0) > 3:
        print(f'{cntd} has too many 2s')
        return False
    if cntd[0] < n/4:
        print(f'{cntd} has too few 0s')
        return False
    #print(f"{cntd} is good!")
    return True

def timing_okay(d):
    """report if repeats are not crazy (not too many in a row) """
    # flip left right for devalued OD (cor key is inverse of top fruit)
    flip_i = d.deval & (d.ttype == slip.PhaseType.OD)
    d.loc[flip_i,'LR1'] = [ 'R' if s=='L' else 'L' for s in d.LR1[flip_i]]

    # only grab SHOW. and only if not SOA or DD deval
    have_side = (d.ttype==slip.TrialType.SHOW) &\
                np.logical_not(d.deval & [x in [slip.PhaseType.SOA, slip.PhaseType.DD] for x in d.phase])

    a = d[have_side].groupby('blocknum').agg({'LR1': lambda x: rep_okay(rep_cnts(x.values), 7)})
    return all(a.LR1)


for _ in range(100):
    seed_int = int(np.random.uniform(10**10))
    seed = np.random.default_rng(seed_int)
    info = slip.FabFruitInfo(phases=SOA,seed=seed)
    if not timing_okay(info.timing):
        continue
    print('okay')
    os.mkdir(f'timing/{seed_int}')
    info.timing.to_csv(f'timing/{seed_int}/DD.csv')
    x='\n'.join(info.timing.groupby('blocknum').agg({'onset': lambda x: " ".join(['%.02f' % a for a in x.values])}).onset.values)
    with open(f'timing/{seed_int}/trial.1D', 'w') as f:
        f.write(x)
    break

