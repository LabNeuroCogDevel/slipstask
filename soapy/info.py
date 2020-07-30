import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from soapy import DEFAULT_PHASES, FIRST_ONSET
from soapy.task_types import PhaseDict, PhaseType, Deval2DList, TrialType, TrialDict, Direction
from soapy.lncdtasks import Filepath, TaskTime, TaskDur
from soapy.box import Box
from soapy.fruit import Fruit


class FabFruitInfo:
    """store timing, boxes, and fruits for Task
    generate or read timing
    """
    # init, or DEFAULT_PHASES
    phases: PhaseDict
    nbox: int  # default to 6, reset by read_timing
    # defined by read_timing
    timing: pd.DataFrame
    devals: Dict[PhaseType, Deval2DList]
    # defined by set_names
    fruits: List[Fruit]
    boxes: List[Box]

    def __init__(self,
                 phases: Optional[PhaseDict] = None,
                 timing_files: Optional[List[Filepath]] = None,
                 nbox: int = 6,
                 seed=None):
        if seed is None:
            seed = np.random.default_rng()
        self.seed = seed
        # overwritten by read_timing when timing files exist
        self.timing = []
        self.nbox = nbox

        # ## timing
        # use timing files if we have them, otherwise phases if given those
        # if neither, use DEFAULT_PHASES
        if timing_files:
            self.read_timing(timing_files)
            self.phases = None
        elif phases:
            self.phases = phases
        else:
            self.phases = DEFAULT_PHASES

        # if we dont already have timing
        # we have phase. make that into timing
        if self.phases:
            d = self.to_df()
            # set nbox, deval, and timing
            self.read_timing(td=d)

        sides = [Direction.Left, Direction.Right]*(self.nbox//2)
        seed.shuffle(sides)

    def OD(self):
        """ timing for OD trials
        deval column is bool. refers to top if OD
        does not use 'reps' or 'blocks' in settings

        expect only 1 block with 36 trials.
        3^2 * 2 (R on Top/L on Top) * 2 (top devaued, bottom devalued)
        >>> ffi = FabFruitInfo(phases={PhaseType.OD: {'itis': [1], 'dur': 1, 'score': 2}}, nbox=6)
        >>> d = pd.DataFrame(ffi.OD())

        each side with top devalued(or not) is evenly distributed

        >>> d[d.ttype == 'SHOW'].assign(LR=lambda x: [y[0] for y in x.LR1]).groupby(['LR','deval']).agg({'LR':len})
                  LR
        LR deval    
        L  False   9
           True    9
        R  False   9
           True    9
        """

        # pull out OD
        settings = self.phases[PhaseType.OD]
        # L0 to R2 (3 of each side)
        # ## want equal parts T,F for R on top and L on top
        sides = {s: [f'{s}{d}' for d in range(self.nbox//2)] for s in ['L', 'R']}
        binfo: List[Tuple[bool, List[int]]] =\
            [(d, [R, L] if Lfirst else [L, R])
                for L in sides['L']
                for R in sides['R']
                for d in [True, False]
                for Lfirst in [True, False]]
        self.seed.shuffle(binfo)

        trls: List[TrialDict] = []
        itis = settings['itis'] * (len(binfo)//len(settings['itis']))
        onset = 0
        for i in range(len(binfo)):  # 36 trls
            LR = binfo[i][1]
            deval_top = binfo[i][0]
            # SHOW
            trls.append(trial_dict(PhaseType.OD, TrialType.SHOW, 1,  i, LR1=LR[0],
                                   LR2=LR[1],
                                   deval=deval_top,
                                   onset=onset,
                                   dur=settings['dur']))
            # ITI
            trls.append(trial_dict(PhaseType.OD, TrialType.ITI, 1, i, LR[0],
                                   LR2=LR[1],
                                   onset=trls[-1]['end'],
                                   dur=itis[i]))
            onset = trls[-1]['end']

        # SCORE
        trls.append(trial_dict(PhaseType.OD, TrialType.SCORE, 1, -1, '',
                               onset=trls[-1]['end'],
                               dur=settings['score']))

        return trls

    def block_timing(self, ptype: PhaseType, onset: TaskTime = 0) -> List[TrialDict]:
        """ generate timing for most blocks (not OD). 
        creates events in trial (SHOW, ITI, sometimes SCORE and FBK)

        >>> ffi=FabFruitInfo(\
              phases = {PhaseType.SOA: {'blocks': 9, 'reps': 2, 'dur': 1,\
                        'itis': [1, 1, 1, 2, 2, 5], 'score': 1, 'grid': 5.0, \
                        'ndevalblocks': 3}},\
              nbox=6)
        >>> d = pd.DataFrame(ffi.block_timing(PhaseType.SOA))
        >>> d[d.ttype=='SHOW'].groupby('blocknum').agg({"trial":len})
                  trial
        blocknum       
        0            12
        1            12
        2            12
        3            12
        4            12
        5            12
        6            12
        7            12
        8            12

        we should see each block have 4 devalued
        >>> d[(d.ttype == 'SHOW') & d.deval].groupby('blocknum').agg({'deval':len})
                  deval
        blocknum       
        0             4
        1             4
        2             4
        3             4
        4             4
        5             4
        6             4
        7             4
        8             4

        and we should have a GRID for every new block
        >>> d[(d.ttype == 'GRID')].groupby('blocknum').agg({'trial':len})
                  trial
        blocknum       
        0             1
        1             1
        2             1
        3             1
        4             1
        5             1
        6             1
        7             1
        8             1
        """

        settings = self.phases[ptype]
        devalued_at: Deval2DList = [[]]*settings['blocks']
        if ptype in [PhaseType.DD, PhaseType.SOA]:
            devalued_at = devalued_blocks(settings['blocks'], settings['ndevalblocks'], self.nbox)

        # assume we have equal number of left and right opening boxes
        # ## sizes
        n_per_side = self.nbox//2
        sides = [f'{s}{n}' for s in ['L', 'R'] for n in range(n_per_side)]
        ntrl_in_block = settings['reps']*self.nbox

        # ## initialize
        # each box is shown once for each repetition
        trls = []
        # repeats of L1 L2 L3 R1 R2 R3
        boxnamedir = sides * settings['reps']
        # maybe make these long enought to span blocks?
        if len(settings['itis']) > ntrl_in_block:
            itis = settings['itis'][0:ntrl_in_block]
        else:
            itis = settings['itis'] * (ntrl_in_block//len(settings['itis']))

        # start at time zero

        onset=FIRST_ONSET
        for bnum in range(settings['blocks']):
            # maybe we want all blocks in this phase to be together (MR block)
            if bnum > 0 and settings.get('combine', False):
                onset = trls[-1]['end']
            else:
                onset = FIRST_ONSET

            # mixup the order of things
            self.seed.shuffle(itis)
            self.seed.shuffle(boxnamedir)
            # LR12 will have 2 if SOA or DD during grid (first event only)
            # TODO: maybe hardcode check ptype in SOA DD and len(LR12)==2
            LR12 = [i for i, x in enumerate(devalued_at) if bnum in x]
            if len(LR12) == 2:
                trls.append(trial_dict(ptype, TrialType.GRID, bnum,  -1,
                                       LR1=sides[LR12[0]],
                                       LR2=sides[LR12[1]],
                                       onset=onset,
                                       dur=settings['grid']))
                onset += settings['grid']

            # generic SHOW, ITI, end of block SCORE
            for tnum in range(ntrl_in_block):
                LR1 = boxnamedir[tnum]
                side_devalued = devalued_at[sides.index(LR1)]
                # Show box(es)
                trls.append(trial_dict(ptype, TrialType.SHOW, bnum,  tnum, boxnamedir[tnum],
                                       deval=bnum in side_devalued,
                                       onset=onset,
                                       dur=settings['dur']))

                onset = trls[-1]['end']

                # FBK (only for ID)
                if ptype == PhaseType.ID:
                    trls.append(trial_dict(ptype, TrialType.FBK, bnum, tnum, boxnamedir[tnum],
                                           onset=onset,
                                           dur=settings['fbk']))
                    onset = trls[-1]['end']

                # ITI
                trls.append(trial_dict(ptype, TrialType.ITI, bnum, tnum, boxnamedir[tnum],
                                       onset=onset,
                                       dur=itis[tnum]))
                onset = trls[-1]['end']

            # SCORE
            trls.append(trial_dict(ptype, TrialType.SCORE, bnum, -1, '',
                                   onset=onset, dur=settings['score']))
        return trls

    def to_df(self):
        """
        >>> phases = {\
            PhaseType.SOA:\
            {'blocks': 9, 'reps': 2, 'dur': 1, 'itis': [1, 1, 1, 2, 2, 5], 'score': 1, 'grid': 5, 'ndevalblocks': 3},\
            PhaseType.OD:\
            {'itis': [1], 'dur': 1, 'score': 2}\
        }
        >>> ffi = FabFruitInfo(phases=phases, nbox=6)
        >>> d = ffi.to_df()
        >>> d[d.ttype == 'SHOW'].groupby('phase').agg({'phase':len})
               phase
        phase       
        OD        36
        SOA      108
        """

        all_trials = []
        for ptype in self.phases.keys():
            if(ptype == PhaseType.OD):
                phase_trials = self.OD()
            else:
                phase_trials = self.block_timing(ptype)
            all_trials.extend(phase_trials)
        d = pd.DataFrame(all_trials)

        ## add correct side
        # cor side is probably the direction of the top
        d = add_corside(d)

        return d

    def read_timing(self, fnames: Optional[List[Filepath]] = None, td: Optional[List[TrialDict]]=None):
        """read previously saved timings. see to_df()
        need fname or d
        @param fnames - list of filename of csv
        @param td - timing dataframe
        @return dataframe w/catagorical phase and trial types
                also updated self.timing, self.nbox, and self.devals

        header/colnames matches dict returned by trial_dict

        phase, ttype, blocknum, trial, LR1, deval, LR2, onset, dur
        """

        # if not d, we should have fname
        if fnames is None and td is None:
            raise Exception("Must provide timing names or dictionary!")
        elif fnames:
            d = pd.concat([pd.read_csv(f) for f in fnames], ignore_index=True).fillna('')
        else:
            d = pd.DataFrame(td)

        # make typed again - maybe need to remove PhaseType. and TrialType.
        d['phase'] = [PhaseType[x.replace("PhaseType.","")] for x in d['phase']]
        d['ttype'] = [TrialType[x.replace("TrialType.","")] for x in d['ttype']]
        self.timing = d
        self.nbox = d.LR1[d.ttype == TrialType.SHOW].unique().size
        allphases = d.phase.unique()
        devalphase = [p for p in allphases if p in [PhaseType.SOA, PhaseType.DD]]
        self.devals = {p: extract_devalued(d, p) for p in devalphase}

        return d

    def set_names(self, fruit_names):
        """replace L0-R2 with fruit names, add column with index
        @param fruit_names: names for the box stim and outcome labels
        @return new dataframe
        also update self.timing and create self.fruits and self.boxes
        >>> ffi = FabFruitInfo(nbox=2) # use default phase settings, but different number of boxes
        >>> d = ffi.set_names(["s1","s2", "o1", "o2"])
        """

        (self.fruits, self.boxes) = make_boxes(fruit_names, self.devals, self.nbox, self.seed)
        self.timing['top'] = ''
        self.timing['bottom'] = ''
        self.timing['bxidx'] = [[[]]] * self.timing.shape[0]
        # box_dict['R1'][0] => index,  [1] => box
        box_dict = {b.name: (i, b) for i, b in enumerate(self.boxes)}

        # ## add top and bottom column names

        idx = np.where([x in [TrialType.FBK, TrialType.SHOW, TrialType.GRID] for x in self.timing.ttype])[0]
        for i in range(len(idx)):
            ii = idx[i]
            box_idxs = [box_dict[self.timing.LR1[ii]][0]]
            lr2 = box_dict.get(self.timing.LR2[ii])
            if lr2:
                box_idxs += [lr2[0]]
            self.timing.loc[idx[i], 'bxidx'] = [[box_idxs]]

        # set stim to "top" for SOA, ID, OD for all the SHOW trialtypes
        idx = (self.timing.LR1 != '') & (self.timing.phase != PhaseType.DD)
        self.timing.loc[idx, 'top'] = [box_dict[bn][1].Stim.name
                                       for bn in self.timing.LR1[idx]]

        # DD is outcome instead of stim
        idx = (self.timing.LR1 != '') & (self.timing.phase == PhaseType.DD)
        self.timing.loc[idx, 'top'] = [box_dict[bn][1].Outcome.name for bn in self.timing.LR1[idx]]

        # OD bottom
        idx = (self.timing.LR2 != '') & (self.timing.phase == PhaseType.OD) & (self.timing.ttype == TrialType.SHOW)
        self.timing.loc[idx, 'bottom'] = [box_dict[bn][1].Stim.name for bn in self.timing.LR2[idx]]

        return self.timing


def devalued_blocks(nblocks: int = 9, reps: int = 3, nbox: int = 6, choose: int = 2) -> Deval2DList:
    """
    generate assignments for SOA - slips of action
    9 blocks w/ 12 trials each (2 outcomes per bloc devalued), 108 trials total. (N.B. `6C2 == 15`)
    each outcome devalued 3 times (36 devalued, 72 valued)
    @param nblocks - number of blocks where 2/6 are randomly devalued (9)
    @param reps - number of repeats for each box (2)
    @param nbox - number of boxes (6)
    @param choose - number of blocks per box (2)
    @return per box devalued indexes e.g. [[0,5], [1,3], [0,1], ...] = first box devalued at block 0 and 5, 2nd @ 1&3, ...
    """
    need_redo = False  # recurse if bad draw
    block_deval = [0] * nblocks  # number of devalued boxes in each block (max `choose`)
    bx_deval_on: List[List[int]] = [[]] * nbox  # box X devalued block [[block,block,block], [...], ...]
    for bn in range(nbox):
        if len(bx_deval_on[bn]) >= reps:
            continue
        avail_slots = [i for i, x in enumerate(block_deval) if x < choose]
        if len(avail_slots) < reps:
            need_redo = True
            break  # dont need to continue, draw was bad
        into = np.random.choice(avail_slots, reps, replace=False).tolist()
        bx_deval_on[bn] = into
        for i in into:
            block_deval[i] += 1

    # if we had a bad draw, we need to rerun
    # python wil stop from recursing forever
    if(need_redo):
        bx_deval_on = devalued_blocks(nblocks, reps, nbox, choose)
    return bx_deval_on


def make_boxes(fruit_names: List[str],
               deval_dict: List[Dict[PhaseType, List[str]]],
               nbox=None,
               seed=None) -> Tuple[List[Fruit], List[Box]]:
    """ make boxes for the task. consistant across all blocks
    @param fruit_names - list of names. should have images in static/image/{name}.png
    @param deval_dict - what box name is devaled at each block for each phase.
                        boxnames are like L0..R2
    @param seed - optional random seed
    @return (fruits,boxes)

    In this example we fix the seed so the fruit shuffle is the same as the input.
    From the 4 "fruits" we get 2 boxes. Stim fruits on the front, and Outcome fruits inside.
    >>> deval_dict = {PhaseType.SOA: [["L0"],["R0"],["L0"],["R0"]]}
    >>> (frts, bxs) = make_boxes(["s1","s2","o1","o2"], deval_dict, seed=np.random.default_rng(1))
    >>> [b.Stim.name for b in bxs]
    ['s1', 's2']
    >>> [b.Outcome.name for b in bxs]
    ['o1', 'o2']
    >>> frts[0].SO.name
    'Stim'
    >>> frts[2].SO.name
    'Outcome'
    >>> bxs[0].Dir
    <Direction.Left: 1>
    >>> [len(bxs), len(frts)]
    [2, 4]
    >>> bxs[0].devalued_blocks[PhaseType.SOA]
    [0, 2]
    >>> bxs[1].devalued_blocks[PhaseType.SOA]
    [1, 3]
    """

    if not nbox:
        nbox = len(fruit_names)//2
    fruits = [Fruit(f) for f in fruit_names]
    sides = [Direction.Left, Direction.Right] * (nbox//2)

    if not seed:
        seed = np.random.default_rng()

    # randomize fruits, side to make Boxes
    seed.shuffle(fruits)
    seed.shuffle(sides)

    # name e.g. L0 to R2
    names = []
    cnt = {Direction.Left: 0, Direction.Right: 0}
    for s in sides:
        sn = "L" if s == Direction.Left else "R"
        names.append(f"{sn}{cnt[s]}")
        cnt[s] += 1

    boxes = []
    for i in range(nbox):
        bxname = names[i]
        devalued_blocks = {
            pt: [b_i for b_i, b in enumerate(d_blks) if bxname in b]
            for pt, d_blks in deval_dict.items()}
        # find devalue index
        # add box
        boxes.append(Box(Stim=fruits[i],
                         Outcome=fruits[i+nbox],
                         Dir=sides[i],
                         devalued_blocks=devalued_blocks,
                         name=bxname))
        boxes[i].updateFruit()

    return (fruits, boxes)


def trial_dict(phase: PhaseType, ttype: TrialType,
               blocknum: int, trial: int,
               LR1: str,
               deval: bool = False, LR2: str = '',
               onset: TaskTime = 0.0, dur: TaskDur = 1.0) -> TrialDict:
    """provide defaults for block_timing() and OD()"""
    d = locals()

    # for mypy. match keys
    # d: TrialDict = {l[k] for k in TrialDict.keys()}

    # remove Enum
    d['phase'] = d['phase'].name
    d['ttype'] = d['ttype'].name
    # set end
    d['end'] = d['onset'] + d['dur']
    return d


def extract_devalued(d, phase: PhaseType) -> Deval2DList:
    """ find devalued pairs for each block
    currently looks at GRID, but maybe should look at the trials?
    >>> d = pd.DataFrame([\
      {'blocknum': 0, 'LR1':'A', 'deval':True, 'phase': PhaseType.SOA, 'ttype': TrialType.SHOW },\
      {'blocknum': 1, 'LR1':'B', 'deval':True, 'phase': PhaseType.SOA, 'ttype': TrialType.SHOW },\
      {'blocknum': 1, 'LR1':'C', 'deval':True, 'phase': PhaseType.SOA, 'ttype': TrialType.SHOW }])
    >>> extract_devalued(d, PhaseType.SOA)
    [['A'], ['B', 'C']]
    """
    # d = d[(d.phase == phase) & d.ttype == TrialType.GRID]
    f = d[(d.phase == phase) & (d.ttype == TrialType.SHOW) & d.deval]
    csv = f.\
        groupby('blocknum').\
        agg({'LR1': lambda x: ",".join(np.unique(x).tolist())}).\
        LR1.tolist()
    devalued_at = [x.split(',') for x in csv]

    return devalued_at


def add_corside(d: pd.DataFrame):
    """add correct side.
    @param d - dataframe with LR1 (values like L0..R2), ttype, phase, and deval
    @return d with corside column
    pass by refrence, so no return value"""
    d['cor_side'] = ""
    show_idx = (d.ttype == TrialType.SHOW) | (d.ttype == "SHOW")
    d.loc[show_idx,'cor_side'] =  [x[0] for x in d.LR1[show_idx]]
    # flip L/R if OD and devauled
    flip_i = d.deval & [x in [PhaseType.OD, "OD"] for x in d.phase]
    d.loc[flip_i, 'cor_side'] = ['R' if s == 'L' else 'L' for s in d.LR1[flip_i]]
    # no correct resp if SOA or DD
    none_i = d.deval & [x in [PhaseType.DD, PhaseType.SOA, "SOA", "DD"] for x in d.phase]
    d.loc[none_i, 'cor_side'] = ""
    return d
