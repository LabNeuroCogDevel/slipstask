from soapy.task_types import PhaseType
from soapy import DEFAULT_PHASES, read_img_list
from soapy.task import FabFruitTask
from soapy.info import FabFruitInfo
from soapy.lncdtasks import dly_waitKeys
from typing import List


def ID_example(t, left=False, right=False):
    """draw boxes by example"""
    t.draw_box("closed", 1, 5)
    if left:
        t.draw_box("open", 2, 4)
    if right:
        t.draw_box("open", None, 6)


chartsec = "%s" % DEFAULT_PHASES[PhaseType.DD]['grid']
respsec = "%s" % DEFAULT_PHASES[PhaseType.DD]['dur']
obj_type = "fruit"
example_type = "veggies"
INSTRUCTIONS = {
PhaseType.ID: [
    ["In this game, you will open tricky "+obj_type+" boxes.\n" +
     "The boxes look like this: \n",
     lambda t: ID_example(t, left=False, right=False)],
    ["All boxes open from both the left and right.\n" +
     "You can pick which way to open the box using \n" +
     "your index or middle finger\n",
     lambda t: ID_example(t, False, False)],
    ["This box opens from the Left",
     lambda t: ID_example(t, True, False)],

    ["The boxes have a trick to hide what's inside. \n" +
     "If you pick the wrong side, the inside will appear empty and have no points.\n",
     lambda t: ID_example(t, False, True)],

    ["You will get points for picking the correct side to open.\n" +
     "Boxes labeled with the same "+obj_type+" on the outside always open from the same side."],

    ["The "+obj_type+" on the inside is different from "+obj_type+" label on the outside.\n" +
     "Pay attention to this!\nLater, you will get points for knowing what outside "+obj_type+" label gives you the inside fruit.",
     lambda t: ID_example(t, 2, None)],

    ["You have to pick quickly.\n" +
     f"You only have {DEFAULT_PHASES[PhaseType.ID]['dur']} seconds to choose!"],
    ["\n\nLearn how to open all the boxes and get the most points!\n" +
     "Remember what "+obj_type+"s are inside the boxes too.\n" +
     "\n\nReady to play!?\n"],
    ],
PhaseType.OD: [
     ["\n\nYou opened all the boxes we have!\n" +
      "But we have too many of some of the inside "+obj_type+"s. \n" +
      "You can now get points by picking only the inside "+obj_type+"s without an X over them.\n"+
      "Pick a "+obj_type+" by using the same side that opened the box the "+obj_type+" was inside of"],
     ["\nWe'll tally up your score at the end. You wont know if you're right or wrong until then\n"+
      "\nWhen you're ready to start, click next."],
     ],
PhaseType.SOA: [
    ["\nNew box shipments are coming in,\n"+
     "but some of the "+obj_type+"s inside have gone bad!\n"+
     "For each shipment, we have a chart showing good and bad "+obj_type+"s.\n"+
     "Only open boxes with unspoiled "+obj_type+"s in them." +
     "\nDon't pick those with an X on them."],
    ["\nYou will still get points for opening boxes with good "+obj_type+"s inside\n"+
     "But do not even try to open a box with a spoiled "+obj_type+".\n"+
     "If you correctly open a box with spoiled "+obj_type+" inside, you'll lose points!"],
    ["You'll have " + chartsec + " seconds to memorize the good/bad chart for each shipment.\n"+
     "Then, you will only have " + respsec + " second to open or pass each box in the shipment.\n"],
    ["You'll see how well you did at the end of each shipment,\n" +
     "but you wont know if you're right or wrong until then."],
    ["\nRemember:\n " +
     chartsec + "  seconds to memorize the chart\n " +
     respsec + " second to pick or pass\n " +
     "Don't open boxes where the outside label is X'ed out\n" +
     "When you're ready, click next."]
    ],

PhaseType.DD: [
    ["Someone tried to intercept our shipments of tricky boxes and damanged some of them!\n" +
     "For each shipment, we have a chart of what boxes were damaged."],
    ["\nYou will still get points for opening boxes with good "+obj_type+"s inside\n"+
     "But, don't even try to open a damaged box.\n" +
     "If you open a damanged box correctly, you'll lose points!"],
    ["\nYou'll have " + chartsec + " seconds to memorize the good/bad chart for each shipment.\n"+
     "Then, you will only have " + respsec + " second to open or pass each box in the shipment.\n"],
    ["You'll see how well you did at the end of each shipment,\n" +
     "but you wont know if you're right or wrong until then."],
    ["\nRemember:\n " +
     chartsec + "  seconds to memorize the chart\n " +
     respsec + " second to pick or pass\n " +
     "Don't open boxes where the outside label is X'ed out\n" +
     "When you're ready, click next."]
 ],
PhaseType.SURVEY: [
    ["You are almost done!\n"+
     "We just have a few questions we want to ask you about the game.\n" +
     "We want to know how well you feel like you learned about the tricky boxes."],
    ["\n\nIn this section, we'll ask you about\n" +
      "  the way to open the box labeled with or containing each "+obj_type+".\n" +
      "  what outside "+obj_type+" label pair with which inside "+obj_type+".\n" +
      "  and how confident you are about each answer.\n"],
    ["\n\n\nWhen answering,\n" +
      "  to pick left or right, push the keyboard arrow keys or click the arrow.\n" +
      "  to pick a "+obj_type+"'s pair, push the number label on the keyboard or using the mouse.\n" +
      "  to rank your confidence, move the slider and click continue.\n" +
      "When you're ready to start, press next."],
 ],
}


def show_instruction(win, phase: PhaseType):
    """ present instructions
    @param win - window for fake task
    @param phase - phase to give instructions on
    """
    # doesn't actaully matter what phase for this part
    ffi = FabFruitInfo({phase: DEFAULT_PHASES[phase]})
    # set fruits/animals/veggies. will use ffi.seed for random assignment
    ffi.set_names(read_img_list(example_type))
    t = FabFruitTask(win, ffi)
    j = 0
    while j < len(INSTRUCTIONS[phase]):
        i = INSTRUCTIONS[phase][j]
        func = i[1] if len(i) > 1 else None
        resp = t.instruction(i[0], func)
        if resp == "left" and j > 0:
            j = j - 1
        else:
            j = j + 1


def practice(win, obj_type='animals'):
    """run a practice version of the task
    @param win - psychopy window
    @param obj_type - fruits|animals|veggies"""
    pass
