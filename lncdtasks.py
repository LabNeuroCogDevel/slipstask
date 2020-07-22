# core time relative to import
# careful not to load this too late
from psychopy import core
from warnings import warn

def wait_until(resume_at: float, maxwait:int = 30, verbose:bool=False):
    """
    @param resume_at core.getTime() when to resume
    @param maxwait longest time to wait without error (def 30sec)
    @return null. blocks from now until resume_at
    """
    now: float = core.getTime()
    waittime = resume_at - now - .001
    if resume_at - now > maxwait:
        raise ValueError(f"request to wait until {resume_at:.2f} is " +
                         f"{waittime:.2f} (>30 seconds) from now." +
                         "set maxwait to avoid error")
    if waittime < 0 and resume_at != 0:
        warn(f"resume time {resume_at:.2f} is after current time {now:.2f} ({waittime:.2f}s)!")
    if verbose:
        print(f'  waiting {waittime:.2f} secs until {resume_at:.2f}')
    core.wait(waittime)
 
def wait_until_blocking(stoptime:float, maxwait:int = 30):
    """
    just like core.wait, but instead of waiting a duration
    we wait until a stoptime.
    optional maxwait will throw an error if we are wating too long
    so we dont get stuck. defaults to 30 seconds
    """
    if stoptime - core.getTime() > maxwait:
        raise ValueError("request to wait until stoptime is more than " +
                         "30 seconds, secify maxwait to avoid this error")
    # will hog cpu -- no pyglet.media.dispatch_events here
    while core.getTime() < stoptime:
        continue
