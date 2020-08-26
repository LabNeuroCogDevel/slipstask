#!/usr/bin/env python3
from psychopy import visual
import pandas as pd
from soapy import read_img_list
from soapy.info import FabFruitInfo
from soapy.task import FabFruitTask
from soapy.task_types import PhaseType, TrialType

# run this now b/c it can take a few seconds
win = visual.Window([800, 600])

from psychopy.hardware.emulator import ResponseEmulator
simulated_responses = [(1,   'left'),
                       (2.1, 'space'),
                       (3,   'right'),
                       (5.1, 'space')]
responder = ResponseEmulator(simulated_responses)


OD = {PhaseType.OD: {'itis': [.5], 'dur': 1, 'score': 3}}
info = FabFruitInfo(phases=OD)

# reset timing info
info.timing = pd.DataFrame([
    {'phase': PhaseType.OD, 'ttype': TrialType.SHOW,  'blocknum': 1, 'trial': 0, 'deval': True,  'onset':0, 'LR1': 'R0', 'LR2': 'L0'},
    {'phase': PhaseType.OD, 'ttype': TrialType.SCORE, 'blocknum': 1, 'trial': 1, 'deval': True,  'onset':2, 'LR1': 'R0', 'LR2': 'L0'},
    {'phase': PhaseType.OD, 'ttype': TrialType.SHOW,  'blocknum': 2, 'trial': 3, 'deval': False, 'onset':0, 'LR1': 'R0', 'LR2': 'L0'},
    {'phase': PhaseType.OD, 'ttype': TrialType.SCORE, 'blocknum': 2, 'trial': 4, 'deval': False, 'onset':2, 'LR1': 'R0', 'LR2': 'L0'},
])

info.set_names(read_img_list('fruits'))

task = FabFruitTask(win, info)

responder.start()
task.run()

assert task.events.data['score'].sum() == 2
