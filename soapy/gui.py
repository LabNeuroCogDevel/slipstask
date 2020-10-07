"""
gui for launching task
"""
from datetime import datetime
import os
from typing import Optional, Tuple, Dict
from psychopy.gui import Dlg
from soapy.seeded import pick_seed
import sys


def show_error(msg) -> bool:
    """quick dialog popup to report issues"""
    d = Dlg(title=msg)
    d.addText(msg)
    d.show()
    return d.OK


class DlgInfo:
    """hold onto dialog inforamation"""
    def __init__(self, name, val, choices=None, isfixed=False, show=True):
        self.name = name
        self.val = val
        self.choices = choices
        self.isfixed = isfixed
        self.handle = None
        self.show = show

    def add(self, dlg):
        """add this info as a field in a dialog box"""
        if not self.show:
            return None
        if self.isfixed:
            self.handle = dlg.addFixedField(self.name, self.val)
        else:
            self.handle = dlg.addField(self.name, self.val,
                                       choices=self.choices)
        return self.handle

    def __repr__(self):
        return f"{self.name}->{self.val} ({self.choices})"


def ymd() -> str:
    return datetime.strftime(datetime.now(), "%Y%m%d")


def setup_outdir(d):
    """@side-effect: update d with outdir. must have id and date"""
    d.update({'outdir':
              os.path.join("slips_data",
                           str(d['id']),
                           f"{d['date']}")})


def mkdir_seed(d) -> Optional[int]:
    """ given dict with outdir and 'seed' interger
    return seed read from file if exists
    @side-effect make directory
    """
    if not os.path.exists(d['outdir']):
        os.makedirs(d['outdir'])

    # reuse or pick new seed
    seed_file = os.path.join(d['outdir'], "seed.txt")
    # N.B. this should also update the gui
    seed = pick_seed(seed_file, d['seed'])
    return seed


class SOADlg:
    def __init__(self):
        SEQUENCE = ['ID', 'OD', 'SOA', 'DD', 'SURVEY']
        self.data = [
          DlgInfo('id', 10000),
          DlgInfo('date', ymd(), isfixed=True),
          DlgInfo('start', 'ID', SEQUENCE),
          DlgInfo('OnlyOne', False),
          DlgInfo('Instructions', True),
          DlgInfo('FullScreen', True),
          DlgInfo('seed', 0)]

    def get_data(self) -> Dict:
        """turn self.data's list into a dict"""
        self.names = [i.name for i in self.data]
        d = {i.name: i.val for i in self.data}
        setup_outdir(d)

        return d

    def set_data(self) -> Dict:
        """use a dialog to set info data"""
        dlg = Dlg(title="Slips of Action/Fab Fruits")
        self.handels = {i.name: i.add(dlg) for i in self.data}
        dlg_data = dlg.show()
        if not dlg.OK:
            sys.exit(1)

        # update SAODlg
        for i, d in zip(self.data, dlg_data):
            i.val = d

        okay, msg = self.validate()
        if not okay:
            if not show_error(msg):
                sys.exit(1)
            else:
                return self.set_data()
        return self.get_data()

    def validate(self) -> Tuple[bool, str]:
        """validate id and seed
        also make output directory, and change seed if already exists
        @return (OKAY?, MSG)
        """
        d = self.get_data()
        if not d['id']:
            return (False, "Bad ID!")
        try:
            d['seed'] = int(d.get('seed',0))
        except ValueError:
            return (False, "bad seed: must be a whole number")

        try:
            seed = mkdir_seed(d)
            # update gui if we have seed there
            self.data[self.names.index('seed')].val = seed
        except Exception as err:
            return (False, f"{err}")

        return (True, "all good")


