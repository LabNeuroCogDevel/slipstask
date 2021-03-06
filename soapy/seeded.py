import sys
import os
from numpy import random
from typing import Optional, List, Tuple
from soapy import DEFAULT_PHASES, timing_path, read_img_list
from soapy.task_types import PhaseType
from soapy.info import FabFruitInfo
from soapy.lncdtasks import Filepath


class fake_rng:
    def __init__(self, seed=None):
        print(f"using old seed! {seed}")
        maxseed = 2**32 - 1
        if seed and seed > maxseed:
            seed = seed % maxseed
            print(f"too large using {seed}")
        random.seed(seed)

    def shuffle(self, x):
        random.shuffle(x)


if not hasattr(random, 'default_rng'):
    random.default_rng = fake_rng


def single_phase(p: PhaseType, seed_init: int,
                 mr_start: int = 0, mr_end: int = 0,
                 settings=DEFAULT_PHASES,
                 nbox: int = 6) -> FabFruitInfo:
    """ generate info from a seed """

    # use psudeo-random times?
    if mr_end != 0:
        timingfileseed = seed_init
        timing = timing_path(p, nbox)
        random.default_rng(timingfileseed).shuffle(timing)
        timing = timing[mr_start:mr_end]
        # reset seed?
        seed = random.default_rng(seed_init)
        print(f"MR: using timing files for {mr_start} to {mr_end}: {timing}")
        ffi = FabFruitInfo(timing_files=timing, seed=seed)
    else:
        # build task
        seed = random.default_rng(seed_init)
        if p == PhaseType.SURVEY:
            ffi = FabFruitInfo(seed=seed)
        else:
            print(f"non-MR {settings}")
            ffi = FabFruitInfo(settings, seed=seed)
    return ffi


def update_boxes(ffi: FabFruitInfo, obj_type: str,
                 outdir: Filepath) -> FabFruitInfo:
    """ set boxes based on saved file """
    # set fruits/animals/veggies. will use ffi.seed for random assignment
    ffi.set_names(read_img_list(obj_type))

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    boxfilename = os.path.join(outdir, 'boxes.txt')
    if os.path.isfile(boxfilename):
        print(f"# reading from {boxfilename}")
        ffi.read_box_file(boxfilename)
    else:
        print(f"# creating {boxfilename}")
        ffi.save_boxes(boxfilename)  # will error if boxes change order/name
    # DEBUG
    showbx = ["%s" % b for b in ffi.boxes]
    #sorted(showbx)
    boxes_string = "\n\t".join(showbx)
    print(f'# generated/using\n\t{boxes_string}')
    # print(f"# stored {boxfilename}\n\t", end="")
    # with open(boxfilename, 'r') as bfile:
    #     print("\t".join(["%s" % b for b in bfile.readlines()]))

    return ffi


def pick_seed(seed_file: Filepath, init: int = 0) -> Optional[int]:
    """ seed can be specified or read from file
        but if both and they dont agree, panic
    @param seed_file - file to read seed from
    @param numpy.random.default_rng(seed)
    @return numpy random seed object
    """
    seed = 0
    if os.path.isfile(seed_file):
        with open(seed_file) as f:
            seed = int(f.readline().replace("\n", ""))

    # use file if we have it
    # unless expliclty set set seed from dialog
    # then check against known seed
    if not init and not seed:
        seed = int(random.uniform(10**10))
    elif not seed:
        seed = init
    elif not init:
        pass  # didn't try to change the seed, left at 0 in dialog. use file
    elif init != seed:
        raise Exception(f"""
                already have seed {seed} in {seed_file}.
                you provided {init}
                Either set dialog value to {seed} or remove {seed_file}""")
        return None

    # write seed to file
    if not os.path.isfile(seed_file):
        with open(seed_file, "w") as f:
            f.write(f"{seed}")

    return seed


def mkdir_seed(seed_dir, seed) -> Optional[int]:
    """ find seed integer from directory or set
    @return seed read from file if exists
    @param seed_dir - dirctory with seed.txt (will make if DNE)
    @param seed - seed to pick or set
    @side-effect make directory
    """
    if not os.path.exists(seed_dir):
        os.makedirs(seed_dir)

    # reuse or pick new seed
    seed_file = os.path.join(seed_dir, "seed.txt")
    seed = pick_seed(seed_file, seed)
    return seed
