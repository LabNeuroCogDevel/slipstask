import numpy as np
import pandas as pd
from psychopy import visual, core, event
from psychopy.data import TrialHandler
from typing import List, Tuple, Optional
from soapy import KEYS, image_path
from soapy.lncdtasks import first_key, TaskTime, TaskDur, Keypress,\
                            dly_waitKeys
from soapy.task_types import KeypressDict, PhaseType, TrialType, SO
from soapy.info import FabFruitInfo
from soapy.lncdtasks import wait_until, Filepath


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
                                              'block_score'])

        # display objects
        self.box = visual.ImageStim(self.win, image_path('box_open.png'))
        self.fruit = visual.ImageStim(self.win, image_path('apple.png'))
        self.X = visual.ImageStim(self.win, image_path('devalue.png'))
        self.confident = visual.ImageStim(self.win, image_path("confidence.png"))

        # score box for ID feeback
        (w, h) = self.box.size
        self.scoreBox = visual.Rect(self.win, lineWidth=2,
                                    fillColor='yellow', lineColor='black',
                                    pos=(0, h/2), size=(w/2, h/5))
        self.textBox = visual.TextStim(self.win)

    def draw_box(self, boxtype, box_number, offset=0, devalue=False) -> Tuple[float, float]:
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
        self.fruit.pos = (0, 0)
        self.fruit.setImage(fruit.image)
        self.fruit.draw()
        self.win.flip()
        resp = event.waitKeys(keyList=self.keys.keys())
        rt = core.getTime() - onset
        correct = self.keys[resp] == fruit.Dir.name
        return (resp, rt, correct)

    def get_confidence(self, mesg:str = "How confident are you?") -> Tuple[int, TaskDur]:
        self.textBox.text = mesg
        self.textBox.pos = (0, .9)
        self.textBox.draw()
        self.confidence.draw()
        #self.fruit.size = (1, 1)
        self.fruit.draw()
        onset = self.win.flip()
        # TODO: show image of hand
        resp = event.waitKeys(keyList=["1", "2", "4", "5"])
        resp = first_key(resp)
        rt = core.getTime() - onset
        return (int(resp), rt)



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
            self.draw_box("closed", bn, pos, deval_idx == i)

        # START
        # NB. neg wait time treated like no wait
        wait_until(onset, verbose=True)
        fliptime = self.win.flip()
        # wait for response
        resp: Optional[Keypress] = None
        rt: Optional[TaskDur] = None
        if dur > 0:
            print(f'  wait-for-response for {dur}sec')
            # NB. if two keys are held down, will re port both!
            # make this None
            resp = event.waitKeys(maxWait=dur - .01, keyList=self.keys.keys())
            rt = core.getTime() - onset
        return (fliptime, resp, rt)

    def fbk(self, show_box: int, score: int, onset: TaskTime = 0) -> TaskTime:
        """ give feedback - only for ID
        @param show_boxes - which box idx to show
        @param score - score to display (see Box.score())
        @param onset - when to flip (default to now (0))
        """

        self.draw_box("open", show_box, 0)

        self.textBox.pos = self.scoreBox.pos
        self.textBox.text = "%d" % score
        self.textBox.color = 'black'
        self.textBox.height = .1
        self.scoreBox.draw()
        self.textBox.draw()

        wait_until(onset)
        return self.win.flip()

    def run(self, init_time: Optional[TaskTime] = None):
        """ run the task through all events """

        block_score: float = 0
        for e in self.events:
            # set clock if no prev trial, prev trial happens after next.
            # or current trial starts at 0
            prev = self.events.getEarlierTrial()
            if prev is None or prev.onset > e.onset or e.onset == 0:
                starttime = core.getTime()
                block_score = 0
                prev_dur = 0
                print(f"* new starttime {starttime:.2f} and score reset")
                # if we don't start for a little bit of time, show fix cross
                if e.onset > 0:
                    self.iti()
            else:
                prev_dur = prev.dur

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
            elif self.timing_method == "dur":
                fliptime = now + prev_dur
            else:
                raise Exception(f"Unknown timing_method {self.timing_method}")

            eta = fliptime - now
            print(f"@{now:.2f} ({e.onset}|{prev_dur:.2f}) ETA {eta:.3f}s blk {e.blocknum} trl {e.trial}" +
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
                (fliptime, e.resp, e.rt) = self.trial(e.phase, e.blocknum, e.bxidx[0], fliptime, deval_idx)
                print(f"  resp: {e.resp}")

                # indicate we pushed a button by changing the screen
                if e.resp and self.timing_method == "onset":
                    self.win.flip()
                
                # if we are running outside of scanner, don't wait for next
                if self.timing_method == "dur":
                    e.dur = 0

                resp = first_key(e.resp)
                e.side = self.keys.get(resp) if resp else None

                this_score = bx.score(e.phase, e.blocknum, e.side)
                block_score += this_score
                e.score = this_score
                print(f"  #resp {resp} is {e.side} =>  {this_score} pts; total: {block_score}")
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
                if not nexttrial or nexttrial.blocknum != e.blocknum:
                    # TODO: change accpet keys to not be glove box?
                    event.waitKeys()

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
        # text settings
        self.textBox.height = .08
        self.textBox.color = 'white'

        if top:
            self.textBox.pos = (0, .8)
            self.textBox.text = top
            self.textBox.draw()
        if bottom:
            self.textBox.pos = (0, -.8)
            self.textBox.text = bottom
            self.textBox.draw()
        if func:
            func(self)
        if flip:
            self.win.flip()
        key = dly_waitKeys(.5)
        return key
