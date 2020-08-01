from soapy.lncdtasks import TaskTime, TaskDur, Keypress
from typing import List, Dict
from enum import Enum
# older python has TypedDict hidden away
try:
    from typing import TypedDict
except:
    from typing_extensions import TypedDict

# Types
Direction = Enum('Direction', 'Left Right None')
SO = Enum('SO', 'Stim Outcome')
PhaseType = Enum('PhaseType', 'ID OD SOA DD SURVEY')
TrialType = Enum('TrialType', 'GRID SHOW FBK ITI SCORE')
Deval2DList = List[List[int]]
DevalDict = Dict[PhaseType, List[int]]
TrialDict = TypedDict("TrialDict", {
                      'phase': PhaseType, 'ttype': TrialType,
                      'blocknum': int, 'trial': int, 'LR1': str, 'deval': bool,
                      'LR2': str, 'onset': TaskTime, 'dur': TaskDur, 'end': int})
# quick def of e.g. {'blocks': 3, 'reps': 2}
PhaseSettings = TypedDict("PhaseSettings", {
                          'blocks': int, 'reps': int, 'dur': TaskDur,
                          'itis': List[TaskDur],
                          'score': float, 'fbk': TaskDur, 'grid': TaskDur,
                          'ndevalblocks': int,
                          'combine': bool})
PhaseDict = Dict[PhaseType, PhaseSettings]
KeypressDict = Dict[Keypress, Direction]
