from soapy.task_types import PhaseType
from soapy import DEFAULT_PHASES, read_img_list
from soapy.task import FabFruitTask
from soapy.info import FabFruitInfo
from soapy.lncdtasks import dly_waitKeys
from typing import List

def ID_example(t, left, right):
    """draw boxes by example"""
    t.draw_box("closed", 1, 5)
    t.draw_box("open", left, 4)
    t.draw_box("open", right, 6)


chartsec = "5"
respsec = "2"
obj_type = "fruit"
example_type = "veggies"
INSTRUCTIONS = {
PhaseType.ID: [
    ["In this game, you will open tricky "+obj_type+" boxes.\n" +
     "The boxes look like this: \n",
     lambda t: t.draw_box("closed", 1, 5)],
    ["All boxes open from both the left and right.\n" +
     "You can pick which way to open the box using the left or right keys.\n",
     lambda t: ID_example(t, None, None)],

    ["But the boxes have a trick to hide what's inside. \n" +
     "If you pick the wrong side, the inside will appear empty and have no points.\n",
     lambda t: ID_example(t, 2, None)],

    ["You will get points for picking the correct side to open.\n"+
     "Boxes labeled with the same "+obj_type+" on the outside always open from the same side."],

    ["The boxes have another trick.\n" +
     "The "+obj_type+" on the inside is different from "+obj_type+" label on the outside.\n" +
     "Pay attention to this! Later, you will get points for knowing what outside "+obj_type+" label gives you the inside fruit.",
     lambda t: ID_example(t, 2, 3)],

    ["Learn how to open all the boxes and get the most points!\n" +
     "Remember what "+obj_type+"s are inside the boxes too.\n" +
     "Ready to play!?\n" +
     "We'll start when you hit next."],
    ],
PhaseType.OD: [
     ["You opened all the boxes we have! But we have too many of some of the inside "+obj_type+"s. \n" +
      "You can now get points by picking only the inside "+obj_type+"s without an X over them.\n"+
      "Pick a "+obj_type+" by using the same side that opened the box the "+obj_type+" was inside of"],
     ["We'll tally up your score at the end. You wont know if you're right or wrong until then\n"+
     "When you're ready to start, click next."],
     ],

     "SOA": [
     ["New box shipments are coming in, but some of the "+obj_type+"s inside have gone bad!\n",
      "For each shipment, we have a chart showing good and bad "+obj_type+"s.\n"+
      "Only open boxes with unspoiled "+obj_type+"s in them. Don't pick those with an <font color=red><b>X</b></font>  on them."],
     ["You will still get points for opening boxes with good "+obj_type+"s inside\n"+
      "But <b>do not even try to open a box with a spoiled "+obj_type+"</b>.\n"+
      "If you correctly open a box with spoiled "+obj_type+" inside, you'll lose points!"],

     ["You'll have 5 seconds to memorize the good/bad chart for each shipment.\n"+
      "Then, you will only have 2 second to open or pass each box in the shipment.\n"],

     ["You'll see how well you did at the end of each shipment,\n" +
      "but you wont know if you're right or wrong until then."],

     ["Remember:\n" +
      " 5 seconds to memorize the chart for this shipment\n" +
      " 2 seconds to pick or pass\n" +
      " Don't open boxes with X'ed "+obj_type+"s inside\n" +
      "When you're ready, click next."],
    ],

PhaseType.DD: [
    ["Someone tried to intercept our shipments of tricky boxes and damanged some of them!\n" +
     "For each shipment, we have a chart of what boxes were damaged."],
    ["You will still get points for opening boxes with good "+obj_type+"s inside\n"+
     "But, <b>don't even try to open a damaged box</b>.\n" +
     "If you open a damanged box correctly, you'll lose points!"],
    ["You'll have " + chartsec + " seconds to memorize the good/bad chart for each shipment.\n"+
     "Then, you will only have " + respsec + " second to open or pass each box in the shipment.\n"],
    ["You'll see how well you did at the end of each shipment,\n" +
     "but you wont know if you're right or wrong until then."],
    ["Remember:\n " +
     chartsec + "  seconds to memorize the chart\n " +
     respsec + " second to pick or pass\n " +
     "Don't open boxes where the outside label is X'ed out\n" +
     "When you're ready, click next."]
 ],
PhaseType.SURVEY: [
    ["You are almost done!\n"+
     "We just have a few questions we want to ask you about the game.\n" +
     "We want to know how well you feel like you learned about the tricky boxes."],
    ["In this section, we'll ask you about\n" +
      "  the way to open the box labeled with or containing each "+obj_type+".\n" +
      "  what outside "+obj_type+" label pair with which inside "+obj_type+".\n" +
      "  and how confident you are about each answer.\n"],
    ["When answering, " +
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
