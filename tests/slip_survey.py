#!/usr/bin/env python3
"""
test survey components
"""
from soapy import quick_task
from psychopy.hardware.emulator import ResponseEmulator
import pytest

WAIT_TO_KEY = .3


@pytest.fixture
def task():
    task = quick_task()
    return task


def simulate_keys(time_push):
    responder = ResponseEmulator(time_push)
    responder.start()


def test_survey_lr(task):
    """
    test left right survey response
    """

    fruit = task.boxes[0].Stim
    # kludge. get a good and bad keypress. match expected response to each
    resps = {'cor': {'keypush': None, 'dir': None},
             'err': {'keypush': None, 'dir': None}}
    for keypush, side_dir in task.keys.items():
        desc = 'cor' if side_dir == fruit.box.Dir else 'err'
        info = {'keypush': keypush, 'dir': side_dir}
        resps[desc] = info

    simulate_keys([(.3, resps['cor']['keypush'])])
    (resp, rt, cor) = task.fruit_only(fruit)
    assert rt <= .3
    assert resp == resps['cor']['keypush']
    assert cor

    simulated_responses = [(.3, resps['err']['keypush'])]
    responder = ResponseEmulator(simulated_responses)
    responder.start()
    (resp, _, cor) = task.fruit_only(fruit)
    assert not cor

    task.win.close()


def test_survey_conf(task):
    """
    test conf survey response
    pink key on button box is high. but corrisonds to low confidence
    """
    thumb_push = '1'
    simulate_keys([(WAIT_TO_KEY, thumb_push)])
    (conf, rt) = task.get_confidence()
    assert rt <= WAIT_TO_KEY
    assert conf == 4

    pinky_push = '5'
    simulate_keys([(WAIT_TO_KEY, pinky_push)])
    (conf, _) = task.get_confidence()
    assert conf == 0

    task.win.close()


def test_survey_fruit_corrct(task):
    """
    test fruit pair survey response
    confidence swap of numkeys messed this up earlier
    make sure that the we have the keys we want
    -- sketchy capsys to get random order
    """

    outcome = task.boxes[0].Outcome
    fruits = task.fruit_and_four(outcome)
    resp_idx = fruits.index(outcome)
    correct_push = str(resp_idx + 1)  # '1' to '5' are index 0 to 4
    simulate_keys([(WAIT_TO_KEY, correct_push)])
    (f_resp, f_rt, f_pick, f_correct) = task.fruit_fingers(outcome, fruits)
    assert f_rt <= WAIT_TO_KEY
    assert f_resp == resp_idx
    assert f_pick == outcome.name
    assert f_correct

    task.win.close()


def test_survey_fruit_pinky(task):
    """
    test pinky and thumb push on fruit pair survey response
    """

    pinky_press = '5'
    outcome = task.boxes[0].Outcome
    simulate_keys([(WAIT_TO_KEY, pinky_press)])
    (f_resp, f_rt, f_pick, f_correct) = task.fruit_fingers(outcome)
    assert f_resp == 4

    thumb_press = '1'
    outcome = task.boxes[0].Outcome
    simulate_keys([(WAIT_TO_KEY, thumb_press)])
    (f_resp, f_rt, f_pick, f_correct) = task.fruit_fingers(outcome)
    assert f_resp == 0

    task.win.close()


if __name__ == "__main__":
    qtask = quick_task()
    test_survey_conf(qtask)
    test_survey_fruit_pinky(qtask)
    task.win.close()
