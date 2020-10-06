"""
WriteTwice - open write connection between a buffer and a file
log_stdout(file) - set sys.stdout to also go to file
    file default is slips_data/logs/tasklog_YYYYMMDD_HH.MM.S.txt
"""
import os
import sys
from datetime import datetime


def log_stdout(logname):
    """wrapper for adding a log handler to sys.stdout
    @param logname - where to save file
    @sideffect - write to logname and stdout
    N.B. will not nest loghandlers"""
    if type(sys.stdout) == WriteTwice:
        print(f"# stdout already redirected to {sys.stdout.fname}.\n" +
              f"# NOT redirecting to {logname}.\n" +
              f"# unset with 'sys.stdout = sys.stdout.stream'")
        return

    print(f"# stdout now also to file '{logname}'")
    sys.stdout = WriteTwice(sys.stdout, logname)


# log to a file
# user2033758
# https://stackoverflow.com/questions/14906764/how-to-redirect-stdout-to-both-file-and-console-with-scripting
class WriteTwice:
    """object to mirror sys.stdout. so we can write to a log file and stdout
    use like:
    sys.stdout = WriteTwice(sys.stdout, logname)"""
    def __init__(self, stream, fname=None):
        if not fname:
            fname = default_logfile()
        self.loghandle = open(fname, 'w')
        self.stream = stream
        self.fname = fname

    def write(self, data):
        "write stream to std out and to file"
        self.stream.write(data)
        self.stream.flush()
        self.loghandle.write(data)

    def flush(self, *argv):
        self.stream.flush()
        self.loghandle.flush()


def default_logfile(outdir=None):
    """default location of log file:
    slips_data/logs/tasklog_YYYYMMDD_HH.MM.S.txt"""
    if not outdir:
        outdir = os.path.join("slips_data", "logs")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dt_fmt = datetime.strftime(datetime.now(), "tasklog_%Y%m%d_%H.%M.%S.txt")
    return os.path.join(outdir, dt_fmt)


