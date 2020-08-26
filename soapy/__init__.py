import os
from typing import Optional, List
from soapy.task_types import \
    Direction, PhaseDict, KeypressDict,\
    PhaseType
from soapy.lncdtasks import TaskTime, Filepath
import soapy

# ## default task settings for each phase
FIRST_ONSET: TaskTime = 3

DEFAULT_PHASES: PhaseDict = {
     PhaseType.ID: {'itis': [.5], 'dur': 2, 'fbk': 1, 'score': 2,
                    'blocks': 6, 'reps': 2},
     PhaseType.OD: {'itis': [1.5], 'dur': 1, 'score': 2},
     PhaseType.DD: {'blocks': 9, 'reps': 2, 'dur': 2,
                    'itis': [1.5], 'score': 1, 'grid': 5.0,
                    'ndevalblocks': 3},
     PhaseType.SOA: {'blocks': 9, 'reps': 2, 'dur': 2,
                     'itis': [1.5], 'score': 1, 'grid': 5.0,
                     'ndevalblocks': 3}}

KEYS: KeypressDict = {'left': Direction.Left,
                      'right': Direction.Right,
                      '1': Direction.Left,
                      '2': Direction.Right}

# thumb, index, middle, ring, pincky
# will use index to lookup
NUM_KEYS = ["0", "1", "2", "3", "4"]


def module_path() -> Filepath:
    """return path to files in module
    @return Filepath to module

    NB. may need to rewrite to use pkgutil if using egg archive?
   """
    return soapy.__loader__.path


def timing_path(phase: PhaseType = PhaseType.DD, nbox: int = 6) -> List[Filepath]:
    """find timing files for a given phase
    likely only to be for DD
    @param phase - PhaseType to find timing files for
    @return list of paths to timing files
    """
    from glob import glob
    mpath = module_path()
    root = os.path.dirname(mpath)
    tpath = os.path.join(root, "timing", phase.name, str(nbox))
    if not os.path.isdir(tpath):
        raise Exception(f"no path to timing for phase {phase.name}: {tpath}")
    return glob(os.path.join(tpath, "*.csv"))


def image_path(image: Optional[str] = None) -> Filepath:
    """ path to image folder. contains list txt files and disp images"""
    # data = pkgutil.get_data('soapy', 'images/X.png')
    mpath = module_path()
    root = os.path.dirname(mpath)
    ipath = os.path.join(root, "images")
    if image:
        ipath = os.path.join(ipath, image)
        # bad for testing
        # if not os.path.isfile(ipath):
        #     raise Exception(f"image {image} does not exist at '{ipath}'!")
    return ipath


def read_img_list(objs_type: str) -> List[str]:
    """read fruit/object names from txt file list in package data"""
    filename = image_path(f'{objs_type}.txt')
    if not os.path.isfile(filename):
        raise Exception(f"Missing {objs_type} list file {filename}")
    with open(filename) as f:
        names = [x.strip() for x in f.readlines()]
    return(names)


def example(task):
    """example on how to use task drawing"""
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
    from psychopy import visual
    import soapy.task
    import soapy.info

    win = visual.Window([800, 600])

    ffi = soapy.info.FabFruitInfo()
    fruit_names = read_img_list('fruits')
    ffi.set_names(fruit_names)

    # if we are testing
    # ffi.timing = ffi.timing.loc[0:10]

    slips = soapy.task.FabFruitTask(win, ffi, timing_method="dur")
    slips.run()
    slips.events.saveAsText("exampe_out.csv")
