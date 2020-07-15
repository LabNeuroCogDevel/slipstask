#!/usr/bin/env python
import numpy as np
import pandas as pd
from autoclass import autoclass
from pyfields import field, make_init, autofields
from sspipe import p, px
from psychopy import visual, core
from typing import List, Dict, Tuple
from enum import Enum

Direction = Enum('Direction','Left Right None')
SO = Enum('SO','Stim Outcome')
BlockType = Enum('BlockType', 'ID OD SOA DD')
# prototype for typing
class Fruit: pass
class Box: pass


class Fruit:
    """Fruits or Veggies or Animals -- thing in or on the box"""
    name: str = field(doc="fruit/object's name")
    img: str = field(doc="file location of image")
    SO: SO = field(doc="stim or outcome") # stim or outcome
    # get direction and devalued_blocks from box.*
    pair: Fruit = field(doc="fruit opposite this one")
    box: Box = field(doc="the box containg this and it's pair")
    def __init__(self, name):
        self.name = name
        self.img = "static/images/%s.png" % name

    def __repr__(self) -> str:
        return f"{self.name}: {self.SO} {self.box.direction} " + ",".join(self.box.devalued_blocks[BlockType.SOA]) 


@autofields(check_types=True)
class Box:
    """Box with an outside (stim) and inside (outcome)"""
    stim: Fruit
    outcome: Fruit
    direction: Direction
    devalued_blocks: Dict[BlockType, List[int]] # should only use blocktypes is SOA or DD
    
    def updateFruit(self):
        "Fruits in this box should know about the box"
        self.stim.SO = SO.Stim
        self.stim.pair = self.outcome
        self.outcome.SO = SO.Outcome
        self.outcome.pair = self.stim
        self.stim.box = self.outcome.box = self
    def __repr__(self) -> str:
        return f"{self.stim.name} -> {self.outcome.name} ({self.direction})"


def devalued_blocks(nblocks: int = 9, nbox: int = 6, reps: int = 3, choose: int = 2) -> List[List[int]] :
    """
    generate assignments for SOA - slips of action
    9 blocks w/ 12 trials each (2 outcomes per bloc), 108 trials total. (N.B. `6C2 == 15`)
    each outcome devalued 3 times (36 devalued, 72 valued)
    TODO: setup devalue per fruit in box creation
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
            break # dont need to continue, draw was bad
        into = np.random.choice(avail_slots, reps, replace=False)
        bx_deval_on[bn] = into
        for i in into:
            block_deval[i]+=1

    # if we had a bad draw, we need to rerun
    # N.B. there is no check to not recursise forever!
    if(need_redo):
        bx_deval_on=devalued_blocks(nblocks, nbox, reps, choose)
    return bx_deval_on

def make_boxes(fruit_names: List[str], devalued_at: List[List[int]]) -> Tuple[List[Fruit], List[Box]]:

    fruits=[Fruit(f) for f in fruit_names]
    nboxes = len(fruits)//2
    sides = [Direction.Left, Direction.Right]*(nboxes//2)

    # randomize fruits, side to make Boxes
    seed=np.random.default_rng()
    seed.shuffle(fruits)
    seed.shuffle(sides)

    boxes = []
    for i in range(nboxes):
        boxes.append(Box(stim=fruits[i],
                         outcome=fruits[i+nboxes//2],
                         direction=sides[i],
                         devalued_blocks={BlockType.SOA: devalued_at[i], BlockType.DD: devalued_at[i]}))
        boxes[i].updateFruit()

    return (fruits, boxes)


if __name__ == "__main__":
    with open('static/images/fruits.txt') as f:
        fruit_names=[x.strip() for x in f.readlines()]
    devalued_at = devalued_blocks()
    (fruits, boxes) = make_boxes(fruit_names, devalued_at)
    print(fruits[0])
    print(boxes[0])
