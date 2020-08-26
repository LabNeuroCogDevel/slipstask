#!/usr/bin/env python
from psychopy import visual, core
from soapy import read_img_list
from soapy.task import FabFruitTask
from soapy.info import FabFruitInfo
win = visual.Window([800, 600])
info = FabFruitInfo(timing_files=['timing/seeded/1_445/1350647090/DD.csv'])
info.set_names(read_image_list('fruits'))
task = FabFruitTask(win, info)
task.run()
task.events.saveAsText("exampe_out.csv")
core.quit()
