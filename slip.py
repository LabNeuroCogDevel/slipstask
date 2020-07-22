#!/usr/bin/env python

# python -m doctest -v slip.py

import numpy as np
import pandas as pd
from pyfields import field, autofields
from psychopy import visual, core, event
from psychopy.data import TrialHandler
from typing import List, Dict, Tuple, TypedDict, Optional
from enum import Enum
import lncdtasks

# Types
Direction = Enum('Direction', 'Left Right None')
SO = Enum('SO', 'Stim Outcome')
PhaseType = Enum('PhaseType', 'ID OD SOA DD')
TrialType = Enum('TrialType', 'GRID SHOW FBK ITI SCORE')
TaskTime = float
TaskDur = float
Deval2DList = List[List[int]]
DevalDict = Dict[PhaseType, List[int]]
TrialDict = TypedDict("TrialDict", {
                      'phase': PhaseType, 'ttype': TrialType,
                      'blocknum': int, 'trial': int, 'LR1': str, 'deval': bool,
                      'LR2': str, 'onset': TaskTime, 'dur': TaskDur, 'end': int})
# quick def of e.g. {'blocks': 3, 'reps': 2}
PhaseSettings = TypedDict("PhaseSettings", {
                          'blocks': int, 'reps': int, 'dur': TaskDur,
                          'itis': List[TaskDur],
                          'score': float, 'fbk': TaskDur, 'grid': TaskDur,
                          'ndevalblocks': int})
PhaseDict = Dict[PhaseType, PhaseSettings]
Keypress = str
KeypressDict = Dict[Keypress, Direction]
class Fruit: pass
class Box: pass


# ## default task settings for each phase
DEFAULT_PHASES: PhaseDict = {
     PhaseType.ID: {'itis': [.5], 'dur': 1, 'fbk': 1, 'score': 2,
                    'blocks': 6, 'reps': 2},
     PhaseType.OD: {'itis': [1], 'dur': 1, 'score': 2},
     PhaseType.DD: {'blocks': 9, 'reps': 2, 'dur': 1,
                    'itis': [1, 1, 1, 2, 2, 5], 'score': 1, 'grid': 5,
                    'ndevalblocks': 3},
     PhaseType.SOA: {'blocks': 9, 'reps': 2, 'dur': 1,
                     'itis': [1, 1, 1, 2, 2, 5], 'score': 1, 'grid': 5,
                     'ndevalblocks': 3}}

KEYS: KeypressDict = {'left': Direction.Left,
                      'right': Direction.Right,
                      '1': Direction.Left,
                      '2': Direction.Right}
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

    def __init__(self, phases: PhaseDict = None, timing_file: str = None, nbox: int = 6, seed=None):
        if seed is None:
            seed = np.random.default_rng()
        self.seed = seed
        # overwriten by read_timing when timing files exist
        self.timing = []
        self.nbox = nbox

        # ## timing
        if timing_file:
            self.read_timing(timing_file)
            self.phases = []
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

    def block_timing(self, ptype) -> List[TrialDict]:
        """ generate timing for most blocks (not OD). 
        creates events in trial (SHOW, ITI, sometimes SCORE and FBK)

        >>> ffi=FabFruitInfo(\
              phases = {PhaseType.SOA: {'blocks': 9, 'reps': 2, 'dur': 1,\
                        'itis': [1, 1, 1, 2, 2, 5], 'score': 1, 'grid': 5, \
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
        onset = 0
        for bnum in range(settings['blocks']):

            # mixup the order of things
            self.seed.shuffle(itis)
            self.seed.shuffle(boxnamedir)
            # LR12 will have 2 if SOA or DD
            # TODO: maybe hardcode check ptype in SOA DD and len(LR12)==2
            LR12 = [i for i, x in enumerate(devalued_at) if bnum in x]
            if len(LR12) == 2:
                trls.append(trial_dict(ptype, TrialType.GRID, bnum,  -1,
                                       LR1=sides[LR12[0]],
                                       LR2=sides[LR12[1]],
                                       onset=0,
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

    def to_df(self, fname: str = None):
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
        for ptype, settings in self.phases.items():
            if(ptype == PhaseType.OD):
                phase_trials = self.OD()
            else:
                phase_trials = self.block_timing(ptype)
            all_trials.extend(phase_trials)
        d = pd.DataFrame(all_trials)

        if fname:
            d.to_csv(fname)

        return d

    def read_timing(self, fnames: List[str] = None, td=List[TrialDict]):
        """read previously saved timings. see to_df()
        need fname or d
        @param fnames - list of filename of csv
        @param dt - timing dataframe
        @return dataframe w/catagorical phase and trial types
                also updated self.timing, self.nbox, and self.devals

        header/colnames matches dict returned by trial_dict

        phase, ttype, blocknum, trial, LR1, deval, LR2, onset, dur
        """

        # if not d, we should have fname
        if td is None:
            d = pd.concat([pd.read_csv(f) for f in fnames], ignore_index=True)
        else:
            d = pd.DataFrame(td)

        # make typed again
        d['phase'] = [PhaseType[x] for x in d['phase']]
        d['ttype'] = [TrialType[x] for x in d['ttype']]
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
        self.timing.loc[idx, 'bottom'] = [box_dict[bn][1].Stim.name for bn in self.timing.LR1[idx]]

        return self.timing


class Fruit:
    """Fruits or Veggies or Animals -- thing in or on the box"""
    name: str = field(doc="fruit/object's name")
    image: str = field(doc="file location of image")
    SO: SO = field(doc="Stim or Outcome")  # stim or outcome
    # get direction and devalued_blocks from box.*
    pair: 'Fruit' = field(doc="fruit opposite this one")
    box: 'Box' = field(doc="the box containg this and it's pair")

    def __init__(self, name):
        self.name = name
        self.image = "static/images/%s.png" % name

    def __repr__(self) -> str:
        return f"{self.name}: {self.SO} {self.box.Dir} " +\
                ",".join(["%d" % x for x in self.box.devalued_blocks[PhaseType.SOA]])


@autofields
class Box:
    """Box with an outside (stim) and inside (outcome)"""
    Stim: Fruit
    Outcome: Fruit
    Dir: Direction
    devalued_blocks: DevalDict  # should only use blocktypes is SOA or DD
    name: str  # like L0 to R2

    def updateFruit(self):
        "Fruits in this box should know about the box"
        self.Stim.SO = SO.Stim
        self.Stim.pair = self.Outcome
        self.Outcome.SO = SO.Outcome
        self.Outcome.pair = self.Stim
        self.Stim.box = self.Outcome.box = self

    def score(self, btype: PhaseType, bnum: int, choice: Optional[Direction]):
        """get score for box
        @param btype - blocktype
        @param bnum - block number
        @param choice - direction participant choose. can be None
        @return score (-1,0,1)

        >>> bx = Box(Fruit('s'),Fruit('o'), Direction.Left, {PhaseType.SOA: [1]}, 'TestBox')
        >>> bx.score(PhaseType.ID, 1, Direction.Left)
        1
        >>> bx.score(PhaseType.ID, 1, Direction.Right)
        0
        >>> bx.score(PhaseType.SOA, 1, Direction.Right)
        0
        >>> bx.score(PhaseType.SOA, 1, Direction.Left)
        -1
        >>> bx.score(PhaseType.SOA, 3, Direction.Left)
        1
        >>> bx.score(PhaseType.SOA, 3, None)
        0
        """
        if not choice:
            return 0
        if btype in [PhaseType.DD, PhaseType.SOA] and bnum in self.devalued_blocks[btype]:
            if self.Dir == choice:
                return -1
            else:
                return 0
        else:
            if self.Dir == choice:
                return 1
            else:
                return 0

    def __repr__(self) -> str:
        return f"{self.name}: {self.Stim.name} -> {self.Outcome.name} ({self.Dir})"


def devalued_blocks(nblocks: int = 9, reps: int = 3, nbox: int = 6, choose: int = 2) -> Deval2DList:
    """
    generate assignments for SOA - slips of action
    9 blocks w/ 12 trials each (2 outcomes per bloc devalued), 108 trials total. (N.B. `6C2 == 15`)
    each outcome devalued 3 times (36 devalued, 72 valued)
    * @param nblocks - number of blocks where 2/6 are randomly devalued (9)
    * @param reps - number of repeats for each box (2)
    * @param nbox - number of boxes (6)
    * @param choose - number of blocks per box (2)
    * @return per box devalued indexes e.g. [[0,5], [1,3], [0,1], ...] = first box devalued at block 0 and 5, 2nd @ 1&3, ...
    """
    need_redo = False  # recurse if bad draw
    block_deval = [0] * nblocks  # number of devalued boxes in each block (max `choose`)
    bx_deval_on : List[List[int]] = [[]] * nbox  # box X devalued block [[block,block,block], [...], ...]
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


class FabFruitTask:
    def __init__(self, win, info: FabFruitInfo, keys: KeypressDict = KEYS):
        self.win = win

        # settings
        self.info = info
        self.fruits = info.fruits
        self.boxes = info.boxes
        self.keys = keys

        # timing
        self.events = TrialHandler(info.timing.to_dict('records'), 1,
                                   method='sequential',
                                   dataTypes=['cor', 'resp', 'rt', 'score', 'fliptime'])

        # display objects
        self.box = visual.ImageStim(self.win, './static/images/box_open.png')
        self.fruit = visual.ImageStim(self.win, 'static/images/apple.png')
        self.X = visual.ImageStim(self.win, './static/images/devalue.png')

        # score box for ID feeback
        (w, h) = self.box.size
        self.scoreBox = visual.Rect(self.win, lineWidth=2,
                                    fillColor='yellow', lineColor='black',
                                    pos=(0, h/2), size=(w/2, h/5))
        self.textBox = visual.TextStim(self.win)

    def draw_box(self, boxtype, box_number, offset=0, devalue=False):
        """draw a box and fruit
        @param boxtype - open or closed
        @param box_number - which box to draw
        @param offset - 0 is center (default).
                        -2 is above -1 is below
                        1 to 6 is grid (1-3 top left to right, 4-6 bottom L->R)
        @param devalue - should we draw an X over it?
        """
        self.box.setImage('static/images/box_%s.png' % boxtype)
        sotype = SO.Stim if boxtype == "open" else SO.Outcome
        fruit_img = self.boxes[box_number].__getattribute__(sotype.name).image
        self.fruit.setImage(fruit_img)
        # set postion of box
        (w, h) = self.box.size
        positions = [
          (0,  h/2),   # -2 - top
          (0, -h/2),   # -1 - bottom
          (0,  0),     # 0 - center
          # top row
          (-w,  h/2),  # left
          ( 0,  h/2),  # center
          ( w,  h/2),  # right
          # bottom row
          (-w, -h/2),  # left
          ( 0, -h/2),  # center
          ( w, -h/2)   # right
        ]
        self.box.pos = positions[offset+2]
        self.fruit.pos = positions[offset+2]
        self.X.pos = positions[offset+2]

        self.box.draw()
        self.fruit.draw()
        if devalue:
            self.X.draw()

    def iti(self, onset: TaskTime = 0) -> TaskTime:
        """ show iti screen.
        @param onset - when to flip. default now (0)
        @return fliptime - when screen was flipped
        """
        lncdtasks.wait_until(onset)
        fliptime = self.win.flip()
        return fliptime

    def message(self, message: str, onset: TaskTime = 0) -> TaskTime:
        """show a message centered on the screen
        @param message
        @return fliptime
        """
        self.textBox.text = message
        self.textBox.pos = (0, 0)
        self.textBox.color = 'white'
        self.textBox.draw()
        lncdtasks.wait_until(onset)
        return self.win.flip()

    def grid(self, phase: PhaseType, deval_idxs: List[int], onset: TaskTime = 0) -> TaskTime:
        """ show grid of boxes (always same order)
        @param ceval_idxs - which to cross out
        @param onset - when to flip. default now (0)
        @return fliptime - when screen was flipped
        """
        for bi in range(len(self.boxes)):
            # offset by one for showing teh grid
            boxis = 'open' if phase == PhaseType.SOA else 'closed'
            task.draw_box(boxis, bi, bi+1, bi in deval_idxs)

        lncdtasks.wait_until(onset, verbose=True)
        fliptime = self.win.flip()
        return fliptime

    def trial(self, btype: PhaseType, block_num: int, show_boxes: List[int],
              onset: TaskTime = 0, deval_idx: int = 1, dur: TaskDur = 1) -> Tuple[TaskTime, Optional[str], Optional[TaskDur]]:
        """run a trial, flipping at onset
        @param btype - block type: what to show, how to score
        @param show_boxes - what box(es) to show
        @param deval_idx - for DD 0 to deval top, 1 to devalue bottom
        @param block_num - what block are we on
        @return (fliptime, resp, rt) - key of response, how long til push could both be None
        """

        # check things make sense
        if (btype == PhaseType.OD and len(show_boxes) != 2) or \
           (btype != PhaseType.OD and len(show_boxes) != 1):
            raise Exception('trail got wrong length (%d) of boxes for block (%s)' %
                            (len(show_boxes), btype.name))

        # for most this is just drawing the box centered
        # but if we have two boxes to draw, align vert. (block = OD)
        for i, bn in enumerate(show_boxes):
            pos = i - (2 if len(show_boxes) > 1 else 0)  # 0 or -2, -1
            print(f"  pos {pos}")
            self.draw_box("closed", bn, pos, deval_idx == i)

        # START
        # NB. neg wait time treated like no wait
        lncdtasks.wait_until(onset, verbose=True)
        fliptime = self.win.flip()
        # wait for response
        if dur > 0:
            print('  waiting for response for %f' % dur)
            # NB. if two keys are held down, will re port both!
            # make this None
            resp: Keypress = event.waitKeys(maxWait=dur - .01, keyList=self.keys.keys())
            rt = onset - core.getTime()
            # NB. not actuall ITI. maybe just blank screen?
            #     or maybe gray out current view?
            self.iti(0)
        else:
            resp = None
            rt = None
        return (fliptime, resp, rt)

    def fbk(self, show_box: int, score: int, onset: TaskTime = 0) -> TaskTime:
        """ give feedback - only for ID
        @param show_boxes - which box idx to show
        @param score - score to display (see Box.score())
        @param onset - when to flip (default to now (0))
        """
        bn: Box = self.boxes[show_box]

        self.draw_box("open", show_box, 0)

        self.textBox.pos = self.scoreBox.pos
        self.textBox.text = "%d" % score
        self.textBox.color = 'black'
        self.scoreBox.draw()
        self.textBox.draw()

        lncdtasks.wait_until(onset)
        return self.win.flip()



def trial_dict(phase: PhaseType, ttype: TrialType,
               blocknum: int, trial: int,
               LR1: str,
               deval: bool = False, LR2: str = '',
               onset: TaskTime = 0.0, dur: TaskDur = 1.0) -> TrialDict:
    """provide defaults for write_timing"""
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


def example(task):
    task.draw_box('open', 1)
    task.win.flip()
    task.draw_box('closed', 2, -2, False)
    task.draw_box('closed', 1, -1, True)
    task.win.flip()
    task.draw_box('open', 1, 1, True)
    task.draw_box('open', 2, 2, False)
    task.draw_box('open', 3, 3, False)
    task.draw_box('open', 4, 4, False)
    task.draw_box('open', 5, 5, True)
    task.draw_box('open', 0, 6, False)
    task.win.flip()
    task.draw_box('open', 1, 1, True)
    task.win.flip()

    task.trial(PhaseType.ID, 1, [2])
    task.trial(PhaseType.DD, 1, [3])
    task.trial(PhaseType.SOA, 1, [3])
    task.trial(PhaseType.OD, 1, [2, 3], deval_idx=0)  # top deval
    task.trial(PhaseType.OD, 1, [2, 3], deval_idx=1)  # bottom deval


if __name__ == "__main__":
    win = visual.Window([800, 600])

    ffi = FabFruitInfo()
    fruit_type = 'fruits'
    with open('static/images/%s.txt' % fruit_type) as f:
        fruit_names = [x.strip() for x in f.readlines()]
    ffi.set_names(fruit_names)

    # if we are testing
    # ffi.timing = ffi.timing.loc[0:10]

    task = FabFruitTask(win, ffi)
    for e in task.events:
        # set clock if no prev trial, prev trial happens after next.
        # or current trial starts at 0
        prev = task.events.getEarlierTrial()
        if prev is None or prev.onset > e.onset or e.onset == 0:
            starttime = core.getTime()
            print(f"* new starttime {starttime:.2f}")

        fliptime = starttime + e.onset
        print(f"@{core.getTime():.2f} ETA {fliptime:.2f} {e.blocknum} {e.trial} {e.phase} {e.ttype} {e.LR1} {e.top} {e.deval}")

        # how should we handle this event (trialtype)
        if e.ttype == TrialType.SHOW:
            if e.deval & (e.phase == PhaseType.DD):
                deval_idx = 0
            else:
                deval_idx = 1  # 1 means nothing for ID DD and SOA
            (fliptime, resp, rt) = task.trial(e.phase, e.blocknum, e.bxidx[0], fliptime, deval_idx)
            e.resp = resp
            e.rt = rt
            print(f"  resp: {e.resp}")
            # e.g.
            #  task.trial(PhaseType.SOA, 1, [3])
            #  task.trial(PhaseType.OD, 1, [2, 3], deval_idx=0)  # top deval
        elif e.ttype == TrialType.ITI:
            fliptime = task.iti(e.onset+starttime)

        elif e.ttype == TrialType.FBK:
            bi = e.bxidx[0][0]
            bn = task.boxes[bi]
            resp: Keypress = task.events.getEarlierTrial().resp
            if resp and len(resp) > 1:
                print(f"WARNING: pushed more than one key({resp})! considering no push")
                resp = None
            # want first (and only hopefully) key that was pushed
            if resp:
                resp = resp[0]

            side = task.keys.get(resp)
            score = bn.score(PhaseType.ID, e.blocknum, side)
            print(f"  #score {resp} is {side} = {score}")
            fliptime = task.fbk(bi, score, e.onset+starttime)

        elif e.ttype == TrialType.GRID:
            fliptime = task.grid(e.phase, e.bxidx[0], e.onset)

        elif e.ttype == TrialType.SCORE:
            #task.events.data
            #d = task.info.timing.loc[0:task.events.thisN]
            #d[(d.blocknum == d.blocknum[-1]) & 
            score = "unkown score"

            # print("score: %d" % task.events.getEarlierTrial().score)
            task.message(f'Total Score: {score}')

            lncdtasks.wait_until(e.onset+starttime)
            fliptime = win.flip()

        else:
            print(f"#  doing nothing with {e.ttype}")

        task.events.addData('fliptime', fliptime)
    print("done")
    task.events.saveAsText("exampe_out.csv")
