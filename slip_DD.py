#!/usr/bin/env python3
from psychopy import visual
from slip import FabFruitInfo, FabFruitTask, PhaseType

win = visual.Window([800, 600])

OD = {PhaseType.OD: {'itis': [1], 'dur': 1, 'score': 3}}
info = FabFruitInfo(phases=OD)

with open('static/images/fruits.txt') as f:
    fruit_names = [x.strip() for x in f.readlines()]
info.set_names(fruit_names)

task = FabFruitTask(win, info)
task.run()
