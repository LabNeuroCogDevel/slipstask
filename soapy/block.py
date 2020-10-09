from psychopy import core
from soapy import KEYS
from soapy.task_types import PhaseType, TrialType, Direction,\
                             KeypressDict, TaskTime, TaskDur
from soapy.box import Box
from soapy.lncdtasks import wait_for_scanner, wait_until, first_key
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
        self.deval = isdeval
    def __repr__(self):
        return f"{self.side} ({self.resp_raw}) @ {self.rt:.2f}s => {self.score} (deval? {self.deval})"

def block_out_header(fout=None):
    """ write header for log run log file
    @param fout - file to write to. default: None (no write)
    see also see EventOut.write
    """
    if not fout:
        return

    fout.write('total_time, phase,ttype,blocknum,'+
               'trial,LR1,deval,onset,cor_side,block_score_raw,'+
               'fliptime_raw,resp_raw,rt_raw,score_raw,'+
               'side_raw,fruit_outside,fruit_inside,extra\n')


class EventOut:
    phase: PhaseType
    event: TrialType
    box: Box
    fliptime: TaskTime
    resp: ResponseOut
    def __init__(self, phase, box, ft=0, event=TrialType.SHOW):
        self.phase = phase
        self.event = event
        self.fliptime = ft
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
        

    def write(self, tnum=0, block_score=0, bnum=0, starttime=0, fout=None, extra=None):
        """
        @param tnum        trial number
        @param block_score total score for this block
        @param fout        what file to write to
        """
        total_time = core.getTime() - starttime
        print(f"@{total_time:.1f}={tnum:02d}: {self}; total: {block_score}")

        # also see block_out_header
        # headers like 
        # total_time, phase,ttype,blocknum,trial,LR1,deval,onset,cor_side,block_score_raw,fliptime_raw,resp_raw,rt_raw,score_raw,side_raw, fruit_outside, fruit_inside, extra
        if fout:
            # need a fake resp object
            if self.resp is None:
                none_dict = {k: "" for k in ["deval", "score", "resp_raw", "rt", "side"]}
                self.resp = type('',(object,),none_dict)()
            if self.box is None:
                none_dict = {k: "" for k in ["name", "Dir"]}
                self.box = type('',(object,),none_dict)()
                fruit_inside = ""
                fruit_outside = ""
            else:
                fruit_inside = self.box.Stim.name
                fruit_outside = self.box.Outcome.name
            fout.write(",".join([str(x) for x in [total_time,
                self.phase, self.event, bnum, tnum,
                self.box.name, self.resp.deval, self.fliptime - starttime,
                self.box.Dir, block_score, self.fliptime,
                self.resp.resp_raw, self.resp.rt, self.resp.score,
                self.resp.side, fruit_outside, fruit_inside, extra]]))
            fout.write("\n")

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

## SOA/DD 
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


def slips_blk(task, DURS, seed, phase=PhaseType.SOA, fout=None):
    """   
    @param task - FabFruitTask object with boxes
    @param DURS - dict with durations. keys: grid, score, iti, timeout, OFF
    @param phase - DD or SOA [default: SOA]
    @param fout - where to save file [default: None]
    
    @side-effect: execute ~10min run for given phase type

     blks: dv0 OFF 2dv2 OFF 2dv4 OFF 2dv2 OFF 2dv4 OFF
     time:  40  40   80  40   80  40   80  40   80  40 | 560 (9.33 min)
     trls:  12   0   24   0   24   0   24   0   24   0 | 108

    
     5 second grid
     2 second score
     12 x 
       1.3 seconds avg rt in 3 pilot MR is 
       1 second iti 
       + (extra .7 ontop of rt for correct no resonse
          for the 2 or 4 devalued (each box seen twice)
     blk total = 12 * (1+1.3) + 5 +2  # 35 seconds (+ .7*2*2 or .7*4*2)
     2 per 80 seconds => 2 ON for each 40s OFF 
    
     2 reps of: 1x dv0 , 2x dv2, 2x dv4. 5*80 + 3*40 == 520 == 8.67 min
    
     have 9 L/R matched pairs for each dv2 and dv4. using 8
      len(deval_2(task.info.boxes,seed)) == 9
      len(deval_4(task.info.boxes,seed)) == 9
    """
    
    all_deval_idxs = {
        0: [[]]*9,
        2: deval_2(task.info.boxes, seed),
        4: deval_4(task.info.boxes, seed)}

    for k in all_deval_idxs:
        seed.shuffle(all_deval_idxs[k])

    draws = [0, 2, 2, 4, 4]
    seed.shuffle(draws)
    switch_blocks=[] # len == len(draws) == 5
    deval_idxs = []  # len == 9 (len(draws)*2 - 1)
    i=0
    # draw twice from all but 0 devalued (only one dv0)
    for d in draws:
        deval_idxs.append(all_deval_idxs[d].pop())
        if d != 0:
            deval_idxs.append(all_deval_idxs[d].pop())
            i+=1
        switch_blocks.append(i)
        i+=1


    starttime = wait_for_scanner(task.win)
    next_flip = starttime
    for bnum, block_devaled_idxs in enumerate(deval_idxs):
        extra_col = f"{phase.name}_{len(block_devaled_idxs)}"
        # grid
        show_boxes = shuffle_box_idx(task.info.boxes, seed)
        block_score = 0
        fliptime = task.grid(phase, block_devaled_idxs, next_flip)
        event = EventOut(phase, None, fliptime, TrialType.GRID)
        event.write(0, block_score, bnum, starttime, fout, extra_col)
        next_flip = fliptime + DURS['grid']

        # trial
        for trl_num, box_idx in enumerate(show_boxes):
            box = task.boxes[box_idx]

            # 2 second timeout matches javascript
            event = EventOut(phase, box)
            trl_info = task.trial(phase, [box_idx],
                                  onset=next_flip, dur=DURS['timeout'])
            event.read_resp(trl_info, box_idx in block_devaled_idxs)
            block_score += event.resp.score
            event.write(trl_num, block_score, bnum, starttime, fout, extra_col)
            rt_fliptime = trl_info[0] + trl_info[2]

            # 1second iti matches javascript
            fliptime = task.iti(rt_fliptime)
            event = EventOut(phase, box, fliptime, TrialType.ITI)
            event.write(trl_num, block_score, bnum, starttime, fout, extra_col)
            next_flip = fliptime + DURS['iti']

        fliptime = task.message(f"You scored {block_score} pnts\n\n" + 
                                f"Block {bnum+1}/{len(deval_idxs)}!", next_flip)
        event = EventOut(phase, None, fliptime, TrialType.SCORE)
        event.write(trl_num, block_score, bnum, starttime, fout, extra_col)
        next_flip = fliptime + DURS['score']

        # moving to different number of devalued items. need OFF period
        # N.B. currently have wait block at very end
        if bnum in switch_blocks:
            fliptime = task.iti(next_flip)
            event = EventOut(phase, box, fliptime, TrialType.ITI)
            event.write(trl_num, block_score, bnum, starttime, fout)
            next_flip = fliptime + DURS['OFF']
            print(f"# OFF waiting {DURS['OFF']} seconds until {next_flip:.2f}")
            # default trial() intentionally errors if waiting more than 30seconds
            # get around that by waiting here for a bit
            wait_until(fliptime + DURS['OFF']-.1, maxwait=DURS['OFF'])

    fliptime = task.message(f"Finished {phase.name}!", next_flip)
    wait_until(fliptime + DURS['score'])

    
def ID_blk(task, DURS, seed, fout=None):
    # mprage takes 6.5 minutes.
    # allow 6 seconds to end and display score 
    show_boxes = shuffle_box_idx(task.info.boxes, seed)
    block_score = 0
    have_time = True
    bnum = 0
    starttime = wait_for_scanner(task.win)
    nextflip = starttime
    while have_time:
        for trl_num, box_idx in enumerate(show_boxes):
            box = task.info.boxes[box_idx]
            event = EventOut(PhaseType.ID, box)
            trl_info = task.trial(PhaseType.ID, [box_idx], onset=nextflip, dur=None)
            event.read_resp(trl_info)
            block_score += event.resp.score
            event.write(trl_num, block_score, bnum, starttime, fout, 'ID_mprage')
    
            # give feedback
            fliptime = task.fbk(box_idx, event.resp.score, side=event.resp.side)
            event = EventOut(PhaseType.ID, box, fliptime, TrialType.FBK)
            event.write(trl_num, block_score, bnum, starttime, fout, 'ID_mprage')
            nextflip = fliptime + DURS['fbk']
            if core.getTime() - starttime > DURS['mprage']:
                have_time = False
                break
    
        fliptime = task.message(f"In this block you scored {block_score} pnts!", nextflip)
        event = EventOut(PhaseType.ID, None, fliptime, TrialType.SCORE)
        event.write(0, block_score, bnum, starttime, fout, 'ID_mprage')
    
        # reset block for next go
        show_boxes = shuffle_box_idx(task.info.boxes, seed)
        block_score = 0
        bnum += 1
        nextflip=fliptime + DURS['score']
    
        # when mprage is just about over. we wont start a new block
        # so need to wait here so participant has time to read score
        if not have_time:
            wait_until(nextflip)

    fliptime = task.message(f"Finished ID!", nextflip)
    wait_until(fliptime + DURS['score'])
