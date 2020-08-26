import numpy as np
import pandas as pd
import os.path
from psychopy import visual, core, event
from psychopy.data import TrialHandler
from typing import List, Tuple, Optional
from soapy import KEYS, NUM_KEYS, image_path
from soapy.fruit import Fruit
from soapy.lncdtasks import first_key, TaskTime, TaskDur, Keypress,\
                            dly_waitKeys, wait_until, Filepath,\
                            wait_for_scanner
from soapy.task_types import KeypressDict, PhaseType, TrialType, SO
from soapy.info import FabFruitInfo

box_states = {PhaseType.ID: "closed", PhaseType.OD: "open",
              PhaseType.SOA: "open", PhaseType.DD: "closed"}


def wait_numkey(onset: TaskTime) -> Tuple[int, TaskDur]:
    """ wait for keypress in use NUM_KEY and get numeric value
    @param onset time to make rt relative to last flip
    @return (index of resp, RT)
    """
    resp = event.waitKeys(keyList=NUM_KEYS)
    resp = first_key(resp)
    rt = core.getTime() - onset
    return (NUM_KEYS.index(resp), rt)


class FabFruitTask:
    save_path: Optional[Filepath]

    def __init__(self, win, info: FabFruitInfo, keys: KeypressDict = KEYS,
                 timing_method: str = "onset"):
        self.win = win

        # settings
        self.info = info
        self.fruits = info.fruits
        self.boxes = info.boxes
        self.keys = keys
        self.save_path = None

        # timing
        self.timing_method = timing_method  # alternative "dur"
        self.events = TrialHandler(info.timing.to_dict('records'), 1,
                                   method='sequential',
                                   dataTypes=['cor', 'resp', 'side',
                                              'rt', 'score', 'fliptime',
                                              'block_score', 'skip'])

        # display objects
        self.box = visual.ImageStim(self.win, image_path('box_open.png'))
        self.fruit = visual.ImageStim(self.win, image_path('apple.png'))
        self.X = visual.ImageStim(self.win, image_path('devalue.png'))
        self.confidence = visual.ImageStim(self.win, image_path("confidence.png"))
        self.hand = visual.ImageStim(self.win, image_path("hand_only.png"))
        # downsize hands
        if(self.win.size[1] <= 600):
            self.confidence.size *= .5
            self.hand.size *= .5
        # bottom align
        self.confidence.pos[1] = -1 + self.confidence.size[1]/2
        self.hand.pos[1] = -1 + self.hand.size[1]/2

        # score box for ID feeback
        (w, h) = self.box.size
        self.scoreBox = visual.Rect(self.win, lineWidth=2,
                                    fillColor='yellow', lineColor='black',
                                    pos=(0, h/2), size=(w/2, h/5))
        self.textBox = visual.TextStim(self.win)

    def draw_box(self, boxtype, box_number:Optional[int], offset=0, devalue=False) -> Tuple[float, float]:
        """draw a box and fruit
        @param boxtype - open or closed
        @param box_number - which box to draw
        @param offset - 0 is center (default).
                        -2 is above -1 is below
                        1 to 6 is grid (1-3 top left to right, 4-6 bottom L->R)
        @param devalue - should we draw an X over it?
        @param position of drawn box
        """
        self.box.setImage(image_path(f'box_{boxtype}.png'))
        # closed box see stim, open to see outcome
        sotype = SO.Stim if boxtype == "closed" else SO.Outcome
        if box_number is not None:
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
        if box_number is not None:
            self.fruit.draw()
        if devalue:
            self.X.draw()

        return positions[offset+2]

    def iti(self, onset: TaskTime = 0) -> TaskTime:
        """ show iti screen.
        @param onset - when to flip. default now (0)
        @return fliptime - when screen was flipped
        """
        wait_until(onset)
        self.textBox.color = 'white'
        self.textBox.text = '+'
        # same hight as box that will replace it
        # but text hieght is a little different. still not centered
        self.textBox.height = self.box.size[1]
        self.textBox.pos = (0, 1/16)  # try to offset cross
        self.textBox.draw()
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
        self.textBox.height = 0.1
        self.textBox.draw()
        wait_until(onset)
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
            self.draw_box(boxis, bi, bi+1, bi in deval_idxs)

        wait_until(onset, verbose=True)
        fliptime = self.win.flip()
        return fliptime

    def fruit_only(self, fruit: Fruit) -> Tuple[str, TaskDur, bool]:
        """ show only a fruit, and ask what side it opens from
        @param fruit - fruit to question
        @return (resp, rt, iscorrect)"""
        self.textBox.text = "Push the left or right key for this fruit"
        self.textBox.pos = (0, .8)
        self.fruit.pos = (0, 0)
        self.fruit.setImage(fruit.image)

        self.textBox.draw()
        self.fruit.draw()
        onset = self.win.flip()
        resp = event.waitKeys(keyList=self.keys.keys())
        resp = first_key(resp)
        rt: TaskDur = core.getTime() - onset
        correct: bool = self.keys[resp] == fruit.box.Dir
        return (resp, rt, correct)

    def get_confidence(self, mesg: str = "How confident are you?") -> Tuple[int, TaskDur]:
        """ put up confidence image and wait for 1-5 key push
        N.B. NUM_KEYS are reversed so using thumb ("1" returns "4", and pinky "5" returns "0")
        @param msg text shown, default "how confident are you"
        @return (resp, rt)
        """
        self.textBox.text = mesg
        self.textBox.pos = (0, .9)
        self.textBox.draw()
        self.confidence.draw()
        onset = self.win.flip()
        return wait_numkey(onset)

    def trial(self, btype: PhaseType, block_num: int, show_boxes: List[int],
              onset: TaskTime = 0, deval_idx: int = 1, dur: TaskDur = 1) -> Tuple[TaskTime, List[Keypress], Optional[TaskDur]]:
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
            self.draw_box(box_states[btype], bn, pos, deval_idx == i)

        # START
        # NB. neg wait time treated like no wait
        wait_until(onset, verbose=True)
        fliptime = self.win.flip()
        # wait for response
        resp: List[Keypress] = []
        rt: Optional[TaskDur] = None
        if dur > 0:
            print(f'  wait-for-response for {dur}sec')
            # NB. if two keys are held down, will re port both!
            # make this None
            resp = event.waitKeys(maxWait=dur - .01, keyList=self.keys.keys())
            rt = core.getTime() - onset
        return (fliptime, resp, rt)

    def fbk(self, show_box: Optional[int], score: int, onset: TaskTime = 0) -> TaskTime:
        """ give feedback - only for ID
        @param show_boxes - which box idx to show
        @param score - score to display (see Box.score())
        @param onset - when to flip (default to now (0))
        """

        if score <= 0:
            show_box = None
        self.draw_box("open", show_box, 0)

        self.textBox.pos = self.scoreBox.pos
        self.textBox.text = "%d" % score
        self.textBox.color = 'black'
        self.textBox.height = .1
        self.scoreBox.draw()
        self.textBox.draw()

        wait_until(onset)
        return self.win.flip()

    def fruit_fingers(self, stim: Fruit) -> Tuple[int, TaskDur, str, bool]:
        """ overlay outcome fruits ontop of hand image for a given stim
        @param stim - stim fruit. outcome pair will be among shown
        @return index of response (thumb to pinky), RT, picked, correct """
        self.textBox.text = "What is this label's pair"
        self.textBox.pos = (0, .8)
        self.fruit.pos = (0, .7)
        self.fruit.setImage(stim.image)
        self.textBox.draw()
        self.fruit.draw()
        self.hand.draw()

        print(f'testing {stim.box}')
        # fruits to show
        #  shuffle all outcomes but one we want to include
        this_outcome = stim.box.Outcome
        show_fruits = [f for f in self.fruits
                       if f.name != this_outcome.name and f.SO == SO.Outcome]
        self.info.seed.shuffle(show_fruits)
        # take out one at random (only have 5 fingers)
        show_fruits = show_fruits[0:(len(self.boxes)-2)]
        # and put the correct answer in
        show_fruits.append(this_outcome)
        self.info.seed.shuffle(show_fruits)
        print(f'{this_outcome.name}; showing {[f.name for f in show_fruits]}')

        # put a fruit on each finger
        fingure_ends = [
            [0.60, 0.55],  # thumb
            [0.25, 1.05],  # index
            [-.10, 1.10],  # middle
            [-.35, 1.03],  # ring
            [-.60, 0.75],  # pinky
        ]
        for i, pos in enumerate(fingure_ends):
            x = self.hand.pos[0] - (self.hand.size[0] * pos[0])
            y = -1 + (self.hand.size[1]*pos[1])
            self.fruit.setImage(show_fruits[i].image)
            self.fruit.pos = [x, y]
            self.fruit.draw()

        onset = self.win.flip()
        (resp, rt) = wait_numkey(onset)
        picked = show_fruits[resp].name
        corr = picked == this_outcome.name
        print(f"picked {picked}, is cor? {corr}")
        return (resp, rt, picked, corr)

    def survey(self):
        """ run through fruit and box survey"""
        outf = open(os.path.join(self.save_path), "w")
        outf.write("type disp f_resp f_rt pick iscorrect c_resp c_rt\n")
        # TODO make random order
        for f in self.fruits:
            print(f"showing {f}")
            (f_resp, f_rt, f_correct) = self.fruit_only(f)
            print(f"*  side: {f_resp}=>{self.keys[f_resp].name} vs {f.box.Dir}: {f_correct}")

            (c_resp, c_rt) = self.get_confidence()
            print(f"*  confidence: {c_resp}")
            outf.write(f"side {f.name} {f_resp} {f_rt} {self.keys[f_resp]} {f_correct} {c_resp} {c_rt}\n")

        for b in self.boxes:
            (f_resp, f_rt, f_pick, f_correct) = self.fruit_fingers(b.Stim)
            print(f"*  pair: {f_resp}=>{f_pick} vs {f.box}: {f_correct}")

            (c_resp, c_rt) = self.get_confidence()
            print(f"*  confidence: {c_resp}")
            outf.write(f"pair {b.Stim.name} {f_resp} {f_rt} {f_pick} {f_correct} {c_resp} {c_rt}\n")

        outf.close()

    def run(self, init_time: Optional[TaskTime] = None):
        """ run the task through all events """

        block_score: float = 0
        for e in self.events:
            # set clock if no prev trial, prev trial happens after next.
            # or current trial starts at 0
            prev = self.events.getEarlierTrial()
            prev_dur = 0 if not prev else prev.get('dur',0)
            if prev is None or prev.onset > e.onset or e.onset == 0:
                if prev_dur > 0:
                    print(f"waiting {prev_dur} for prev dur")
                    core.wait(prev_dur)
                # second round of MR. wait for scanner
                # this is maybe a condtion we will never see
                if prev is not None and self.timing_method == 'onset':
                    wait_for_scanner(self.win)

                starttime = core.getTime()
                block_score = 0

                print(f"* new starttime {starttime:.2f} and score reset")
                # if we don't start for a little bit of time, show fix cross
                if e.onset > 0:
                    self.iti()

            now = core.getTime()

            # re-adjust starttime if this is frist pass and we have an actual time
            # this will put us back on track if tehre is a little delay
            # between scanner trigger and actual setup
            if prev is None and init_time:
                start_offset = init_time - starttime
                print(f"# setting starttime to {init_time:.2f}, lost {start_offset:.2f}s")
                starttime = init_time

            # if we are using onset timing method, use preprogramed onsset times
            # if duration, wait until the previous duration
            #    -- duration will be changed when e.g. rt < max wait
            if self.timing_method == "onset":
                fliptime = starttime + e.onset
            
            # if timing "dur", should have set prev dur to 0
            elif self.timing_method == "dur":
                if prev and self.events.data['skip'][self.events.thisTrialN-1] == True:
                    prev_dur = 0
                fliptime = now + prev_dur
            else:
                raise Exception(f"Unknown timing_method {self.timing_method}")

            eta = fliptime - now
            print(f"@{now:.2f} (on{e.onset}|{prev_dur:.2f}pdur) ETA {eta:.3f}s blk {e.blocknum} trl {e.trial}" +
                  f" {e.phase} {e.ttype} {e.LR1} {e.top} {e.deval}")

            # how should we handle this event (trialtype)
            if e.ttype == TrialType.SHOW:
                # get top box
                bi = e.bxidx[0][0]
                bx = self.boxes[bi]

                if e.deval & (e.phase == PhaseType.OD):
                    deval_idx = 0
                    # if top is devalued, pick bottom box to score
                    bx = self.boxes[e.bxidx[0][1]]
                else:
                    deval_idx = 1  # 1 means nothing for ID DD and SOA

                print(f"  # score using {bx}")
                # e.g.
                #  self.trial(PhaseType.SOA, 1, [3])
                #  self.trial(PhaseType.OD, 1, [2, 3], deval_idx=0)  # top deval
                (fliptime, e.resp, e.rt) = self.trial(e.phase, e.blocknum, e.bxidx[0], fliptime, deval_idx, e.dur)
                print(f"  resp: {e.resp}")

                # indicate we pushed a button by changing the screen
                if e.resp and self.timing_method == "onset":
                    self.win.flip()

                # if we are running outside of scanner, don't wait for next
                if self.timing_method == "dur":
                    self.events.addData('skip', True)

                resp = first_key(e.resp)
                e.side = self.keys.get(resp) if resp else None

                this_score = bx.score(e.phase, e.blocknum, e.side)
                block_score += this_score
                e.score = this_score
                print(f"  #resp {resp} @ {e.rt:.2f}s is {e.side} =>  {this_score} pts; total: {block_score}")
                self.events.addData('score', e.score)
                self.events.addData('rt', e.rt)
                self.events.addData('resp', ",".join(e.resp) if resp else None)

            elif e.ttype == TrialType.ITI:
                self.save_progress()
                fliptime = self.iti(fliptime)

            elif e.ttype == TrialType.FBK:
                bi = e.bxidx[0][0]
                # bx = self.boxes[bi]
                this_score = self.events.getEarlierTrial().score
                fliptime = self.fbk(bi, this_score, fliptime)

            elif e.ttype == TrialType.GRID:
                fliptime = self.grid(e.phase, e.bxidx[0], fliptime)

            elif e.ttype == TrialType.SCORE:
                #self.events.data
                #d = self.info.timing.loc[0:self.events.thisN]
                #d[(d.blocknum == d.blocknum[-1]) &

                # print("score: %d" % self.events.getEarlierTrial().score)
                self.message(f'In this block you scored {block_score} pnts', fliptime)
                self.events.addData('block_score', block_score)

                # if score is the last in this block. wait for a key
                nexttrial = self.events.getFutureTrial()
                if self.timing_method == "dur" and (not nexttrial or nexttrial.blocknum != e.blocknum):
                    # TODO: change accpet keys to not be glove box?
                    # TODO: consider making this fixed duration e.dur
                    event.waitKeys()

                # TODO: show fixation for some period of time?
                if not nexttrial and self.timing_method == "onset":
                    core.wait(e.dur)
                    #self.iti()

            else:
                print(f"#  doing nothing with {e.ttype}")

            # update fliptime
            e.fliptime = fliptime
            self.events.addData('fliptime', e.fliptime)

        print("done")

    def save_progress(self):
        """save progress. probably at an iti or at end"""
        if not self.save_path:
            print(f"WARNING: trying to save buth no 'save_path' given")
            return
        self.events.saveAsText(self.save_path)

    def instruction(self, top: str, func, bottom="(push any key)", flip=True) -> Keypress:
        """print some text and run an arbitraty function"""

        # instructions are not timing sensitive.
        # and we need enough character columns to show the instructions
        if top:
            visual.TextStim(self.win,
                            text=top,
                            pos=(0, .7),
                            color='white',
                            wrapWidth=2).\
               draw()

        if bottom:
            self.textBox.height = .08
            self.textBox.color = 'white'
            self.textBox.pos = (0, -.8)
            self.textBox.text = bottom
            self.textBox.draw()
        if func:
            func(self)
        if flip:
            self.win.flip()
        key = dly_waitKeys(.5)
        return key
