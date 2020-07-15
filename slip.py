#!/usr/bin/env python

# python -m doctest -v slip.py

import numpy as np
import pandas as pd
from autoclass import autoclass
from pyfields import field, autofields
from psychopy import visual, core
from typing import List, Dict, Tuple
from enum import Enum

# Types
Direction = Enum('Direction', 'Left Right None')
SO = Enum('SO', 'Stim Outcome')
BlockType = Enum('BlockType', 'ID OD SOA DD')
Deval2DList = List[List[int]]
DevalDict = Dict[BlockType, List[int]]
# prototype for typing
class Fruit: pass
class Box: pass


# Classes
class Fruit:
    """Fruits or Veggies or Animals -- thing in or on the box"""
    name: str = field(doc="fruit/object's name")
    image: str = field(doc="file location of image")
    SO: SO = field(doc="Stim or Outcome")  # stim or outcome
    # get direction and devalued_blocks from box.*
    pair: Fruit = field(doc="fruit opposite this one")
    box: Box = field(doc="the box containg this and it's pair")

    def __init__(self, name):
        self.name = name
        self.image = "static/images/%s.png" % name

    def __repr__(self) -> str:
        return f"{self.name}: {self.SO} {self.box.Direction} " +\
                ",".join(["%d"%x for x in self.box.devalued_blocks[BlockType.SOA]]) 


@autofields(check_types=True)
class Box:
    """Box with an outside (stim) and inside (outcome)"""
    Stim: Fruit
    Outcome: Fruit
    Direction: Direction
    devalued_blocks: DevalDict  # should only use blocktypes is SOA or DD

    def updateFruit(self):
        "Fruits in this box should know about the box"
        self.Stim.SO = SO.Stim
        self.Stim.pair = self.Outcome
        self.Outcome.SO = SO.Outcome
        self.Outcome.pair = self.Stim
        self.Stim.box = self.Outcome.box = self

    def __repr__(self) -> str:
        return f"{self.Stim.name} -> {self.Outcome.name} ({self.Direction})"


def devalued_blocks(nblocks: int = 9, nbox: int = 6, reps: int = 3, choose: int = 2) -> Deval2DList:
    """
    generate assignments for SOA - slips of action
    9 blocks w/ 12 trials each (2 outcomes per bloc devalued), 108 trials total. (N.B. `6C2 == 15`)
    each outcome devalued 3 times (36 devalued, 72 valued)
    * @param nblocks - number of blocks where 2/6 are randomly devalued (9)
    * @param nbox - number of boxes (6)
    * @param reps - number of repeats for each box (3)
    * @param choose - number of blocks per box (2)
    * @return per box devalued indexes e.g. [[0,5], [1,3], [0,1], ...] = first box devalued at block 0 and 5, 2nd @ 1&3, ...
    """
    need_redo = False # recurse if bad draw
    block_deval = [0] * nblocks # number of devalued boxes in each block (max `choose`)
    bx_deval_on = [[]] * nbox # box X devalued block [[block,block,block], [...], ...]
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
        bx_deval_on = devalued_blocks(nblocks, nbox, reps, choose)
    return bx_deval_on


def make_boxes(fruit_names: List[str], devalued_at: Deval2DList,
               seed=np.random.default_rng()) -> Tuple[List[Fruit], List[Box]]:
    """ make boxes for the task. consistant across all blocks
    @param fruit_names - list of names. should have images in static/image/{name}.png
    @param devalued_at - output of devalued_blocks(). currently use same pairs for DD and SOA
    @param seed - optional random seed
    @return (fruits,boxes)

    In this example we fix the seed so the fruit shuffle is the same as the input.
    From the 4 "fruits" we get 2 boxes. Stim fruits on the front, and Outcome fruits inside.
    >>> (frts, bxs) = make_boxes(["s1","s2","o1","o2"], [[1,2],[3,4]], np.random.default_rng(1))
    >>> [b.Stim.name for b in bxs]
    ['s1', 's2']
    >>> [b.Outcome.name for b in bxs]
    ['o1', 'o2']
    >>> frts[0].SO.name
    'Stim'
    >>> frts[2].SO.name
    'Outcome'
    >>> [len(bxs), len(frts)]
    [2, 4]
    >>> bxs[0].devalued_blocks[BlockType.SOA]
    [1, 2]
    """

    fruits = [Fruit(f) for f in fruit_names]
    nboxes = len(fruits)//2
    sides = [Direction.Left, Direction.Right]*(nboxes//2)

    # randomize fruits, side to make Boxes
    seed.shuffle(fruits)
    seed.shuffle(sides)

    boxes = []
    for i in range(nboxes):
        boxes.append(Box(Stim=fruits[i],
                         Outcome=fruits[i+nboxes],
                         Direction=sides[i],
                         devalued_blocks={BlockType.SOA: devalued_at[i],
                                          BlockType.DD: devalued_at[i]}))
        boxes[i].updateFruit()

    return (fruits, boxes)


class FabFruitTask:
    def __init__(self, win, fruit_type="fruits"):
        self.win = win
        with open('static/images/%s.txt' % fruit_type) as f:
            fruit_names = [x.strip() for x in f.readlines()]
        devalued_at = devalued_blocks()
        (self.fruits, self.boxes) = make_boxes(fruit_names, devalued_at)
        # display objects
        self.box = visual.ImageStim(self.win, './static/images/box_open.png')
        self.fruit = visual.ImageStim(self.win, 'static/images/apple.png')
        self.X = visual.ImageStim(self.win, './static/images/devalue.png')

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


if __name__ == "__main__":
    win = visual.Window([800, 600])
    task = FabFruitTask(win)
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
