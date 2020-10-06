from psychopy import core
from soapy import KEYS
from soapy.task_types import PhaseType, TrialType, Direction, KeypressDict, TaskTime
from soapy.box import Box
from soapy.lncdtasks import first_key
import numpy as np


class ResponseOut:
    resp_raw: str
    side: Direction
    rt: float
    score: int
    keys: KeypressDict
    def __init__(self, box, rt, resp, isdeval, keys=KEYS):
        """
        KEYS should come from task
        """
        self.rt = rt 
        self.resp_raw = ",".join(resp) if resp else None
        resp = first_key(resp)
        self.side = keys.get(resp) if resp else None
        self.score = box.score_raw(self.side, isdeval)
    def __repr__(self):
        return f"{self.side} ({self.resp_raw}) @ {self.rt:.2f}s => {self.score}"


class EventOut:
    phase: PhaseType
    event: TrialType
    box: Box
    fliptime: TaskTime
    resp: ResponseOut
    def __init__(self, phase, box, ft=0, event=TrialType.SHOW):
        self.phase = phase
        self.event = event
        self.fliptime = 0
        self.box = box
        self.resp = None
    def read_resp(self, trl_info, isdeval=False):
        (fliptime, resp, rt) = trl_info
        self.fliptime = fliptime
        self.resp = ResponseOut(self.box, rt, resp, isdeval)
    def __repr__(self):
        msg = f"{self.phase.name} {self.event.name} @ {self.fliptime:.2f}s"
        if self.box:
            msg += f" [{self.box.name} {self.box.Dir}]"
        if self.resp:
            msg += f"| {self.resp}"
        return msg
        

    def write(self, tnum=0, block_score=0, bnum=0, starttime=0, fout=None):
        """
        @param tnum        trial number
        @param block_score total score for this block
        @param fout        what file to write to
        """
        total_time = core.getTime() - starttime
        print(f"@{total_time:.1f}={tnum:02d}: {self}; total: {block_score}")
        # headers like 
        # total_time, phase,ttype,blocknum,trial,LR1,deval,onset,cor_side,block_score_raw,fliptime_raw,resp_raw,rt_raw,score_raw,side_raw
        if fout:
            # need a fake resp object
            if self.resp is None:
                none_dict = {k: None for k in ["deval", "score", "resp_raw", "rt", "side"]}
                self.resp = type('',(object,),none_dict)()
            if self.box is None:
                none_dict = {k: None for k in ["name", "Dir"]}
                self.resp = type('',(object,),none_dict)()
            fout.write(",".join(total_time,
                self.phase, self.event, bnum, tnum,
                self.box.name, self.resp.deval, self.fliptime - starttime,
                self.box.Dir, block_score_raw, self.fliptime,
                self.resp.resp_raw, self.resp.rt, self.resp.score, self.resp.side))

def reset_cnt(d):
    """quick struct for counting reps"""
    return{'rep':1, 'dir': d}
def shuffle_okay(dirs, nstrikes=2):
    """do we have a good shuffle?
    cannot have more than 2 repeats twice
    >>> shuffle_okay([1,1,1,2,2,2]) # 2 reps of 3
    False
    >>> shuffle_okay([1,1,1,1,1,2]) # reps >2 twice (4 in a row)
    False
    >>> shuffle_okay([1,2,2,1,2,2])
    True
    """
    maxdir=reset_cnt(Direction.No)
    prevdir=reset_cnt(Direction.No)
    strikes=0
    for d in dirs:
        if prevdir['rep'] > 2:
            strikes += 1

        if prevdir['dir'] != d:
            prevdir=reset_cnt(d)
        else:
            prevdir['rep'] += 1
    # catch last
    if prevdir['rep'] > 2:
        strikes += 1
    return strikes < nstrikes

def shuffle_box_idx(boxes, seed, nbox=6, rep=2):
    """return indexes without repeats"""
    # ## one ID instance
    block_idxs = list(range(0, nbox))*rep
    while True:
        seed.shuffle(block_idxs)
        dirs = [boxes[i].Dir for i in block_idxs]
        if shuffle_okay(dirs):
            break
    return block_idxs

## SOA
# evenly distribute indexes of devaled box. make sure we have 1 left and 1 right
def deval_2(boxes, seed):
    """always devaluing one left and one right"""
    nbox = len(boxes)
    all_pairs = [sorted([x,y])
                 for x in range(nbox)
                 for y in range(x+1, nbox)]
    good_lr = [len(np.unique([boxes[i].Dir.name for i in x]))>1
               for x in all_pairs]
    deval_idxs=[all_pairs[i]
                for i, good in enumerate(good_lr)
                if good]
    seed.shuffle(deval_idxs)
    return deval_idxs

def deval_4(boxes, seed):
    """devalue 2 left and 2 right at a time"""
    nbox = len(boxes)
    all_pairs = [sorted([w,x,y,z])
                for w in range(nbox)
                for x in range(w+1, nbox)
                for y in range(x+1, nbox)
                for z in range(y+1, nbox)]
    good_lr = [len([i for i in x if boxes[i].Dir.name == "Left"])==2
               for x in all_pairs]
    deval_idxs=[all_pairs[i]
                for i, good in enumerate(good_lr)
                if good]
    seed.shuffle(deval_idxs)
    return deval_idxs
