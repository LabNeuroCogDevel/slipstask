import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from soapy.task_types import \
    Direction, PhaseDict, Deval2DList, KeypressDict,\
    PhaseType, TrialType, TrialDict
from soapy.lncdtasks import TaskTime, TaskDur
from soapy.box import Box
from soapy.fruit import Fruit

# ## default task settings for each phase
DEFAULT_PHASES: PhaseDict = {
     PhaseType.ID: {'itis': [.5], 'dur': 1, 'fbk': 1, 'score': 2,
                    'blocks': 6, 'reps': 2},
     PhaseType.OD: {'itis': [1], 'dur': 1, 'score': 2},
     PhaseType.DD: {'blocks': 9, 'reps': 2, 'dur': 1,
                    'itis': [1, 1, 1, 2, 2, 5], 'score': 1, 'grid': 5.0,
                    'ndevalblocks': 3},
     PhaseType.SOA: {'blocks': 9, 'reps': 2, 'dur': 1,
                     'itis': [1, 1, 1, 2, 2, 5], 'score': 1, 'grid': 5.0,
                     'ndevalblocks': 3}}

KEYS: KeypressDict = {'left': Direction.Left,
                      'right': Direction.Right,
                      '1': Direction.Left,
                      '2': Direction.Right}

FIRST_ONSET: TaskTime = 3


def example(task):
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

    task.trial(PhaseType.ID, 1, [2])
    task.trial(PhaseType.DD, 1, [3])
    task.trial(PhaseType.SOA, 1, [3])
    task.trial(PhaseType.OD, 1, [2, 3], deval_idx=0)  # top deval
    task.trial(PhaseType.OD, 1, [2, 3], deval_idx=1)  # bottom deval


if __name__ == "__main__":
    from task import FabFruitTask
    from info import FabFruitInfo
    from psycopy import visual

    win = visual.Window([800, 600])

    ffi = FabFruitInfo()
    fruit_type = 'fruits'
    with open('static/images/%s.txt' % fruit_type) as f:
        fruit_names = [x.strip() for x in f.readlines()]
    ffi.set_names(fruit_names)

    # if we are testing
    # ffi.timing = ffi.timing.loc[0:10]

    task = FabFruitTask(win, ffi)
    task.run()
    task.events.saveAsText("exampe_out.csv")
