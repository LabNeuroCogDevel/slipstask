import numpy as np
import pandas as pd
from psychopy import visual, core, event
from psychopy.data import TrialHandler
from typing import List, Tuple, Optional
from soapy import KEYS, image_path
from soapy.lncdtasks import first_key, TaskTime, TaskDur, Keypress
from soapy.task_types import KeypressDict, PhaseType, TrialType, SO
from soapy.info import FabFruitInfo
from soapy.lncdtasks import wait_until


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
                                   dataTypes=['cor', 'resp', 'side',
                                              'rt', 'score', 'fliptime',
                                              'block_score'])

        # display objects
        self.box = visual.ImageStim(self.win, image_path('box_open.png'))
        self.fruit = visual.ImageStim(self.win, image_path('apple.png'))
        self.X = visual.ImageStim(self.win, image_path('devalue.png'))

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
        self.box.setImage(image_path(f'box_{boxtype}.png'))
        # closed box see stim, open to see outcome
        sotype = SO.Stim if boxtype == "closed" else SO.Outcome
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
        wait_until(onset)
        self.textBox.pos = (0, 0)
        self.textBox.color = 'white'
        self.textBox.text = '+'
        self.textBox.height = .5
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
            rt = onset - core.getTime()
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

    def run(self):
        """ run the task through all events """
        block_score: float = 0
        for e in self.events:
            # set clock if no prev trial, prev trial happens after next.
            # or current trial starts at 0
            prev = self.events.getEarlierTrial()
            if prev is None or prev.onset > e.onset or e.onset == 0:
                starttime = core.getTime()
                block_score = 0
                print(f"* new starttime {starttime:.2f} and score reset")

            fliptime = starttime + e.onset
            now = core.getTime()
            eta = now - fliptime
            print(f"@{now:.2f} ({e.onset}) ETA {eta:.3f}s blk {e.blocknum} trl {e.trial}" +
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
                if e.resp:
                    self.win.flip()

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
                fliptime = self.iti(e.onset+starttime)

            elif e.ttype == TrialType.FBK:
                bi = e.bxidx[0][0]
                # bx = self.boxes[bi]
                this_score = self.events.getEarlierTrial().score
                fliptime = self.fbk(bi, this_score, e.onset+starttime)

            elif e.ttype == TrialType.GRID:
                fliptime = self.grid(e.phase, e.bxidx[0], e.onset)

            elif e.ttype == TrialType.SCORE:
                #self.events.data
                #d = self.info.timing.loc[0:self.events.thisN]
                #d[(d.blocknum == d.blocknum[-1]) &

                # print("score: %d" % self.events.getEarlierTrial().score)
                self.message(f'In this block you scored {block_score} pnts', e.onset+starttime)
                self.events.addData('block_score',block_score)

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
