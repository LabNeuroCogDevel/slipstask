#!/usr/bin/env python
from psychopy import visual, core
from soapy.task import FabFruitTask
from soapy.info import FabFruitInfo
win = visual.Window([800, 600])
info = FabFruitInfo(timing_files=['timing/seeded/1_445/1350647090/DD.csv'])
with open('static/images/fruits.txt') as f:
    info.set_names([x.strip() for x in f.readlines()])
task = FabFruitTask(win, info)
task.run()
task.events.saveAsText("exampe_out.csv")
core.quit()
