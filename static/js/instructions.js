var inst_o = new Fruit('olive');
var inst_b = new Fruit('blueberry');
var inst_box = mkBox(inst_o, inst_b, Dir.Left, [2]);

function IDexample(leftin, rightin){
    const empty="<font size=30>?</font>"
    const left = (leftin===null)?empty:leftin
    const right = (rightin===null)?empty:rightin
    return(
      "<table align='center' style='margin-top: 20px;'><tr>"+
      "<td>"+left+"</td>"+
      "<td><font size=30>←</font></td>"+
      "<td>"+inst_o.render(false) + "</td>" +
      "<td><font size=30>→</font></td>"+
      "<td>"+right+"</td>" +
      "</tr><table>");
}

const INSTRUCTIONS_DATA = {
 "ID": [
   "In this game, you will get the chance to earn points by collecting fruit from inside a box on the screen by opening the box by pressing either the right '←' or left '→' key. If you press the correct key, the box will open to reveal fruit inside and points will be added to you total score. However, if you press the incorrect key, the box will be empty and no points will be added to your total.<br> Your task is to learn which is the correct key to press. Sometimes it will be the left-hand one and sometimes it will be the right-hand one. The fruit picture on the front of the door should give you a clue about which is the correct response.",
	"The quicker you make the correct response the more points will be added to your total (ranging from 1 to 5 points). Your accumulated points will appear at the top of the screen.",
   "You should also try to learn which types of fruit you find inside the boxes following right and left key presses for each fruit on the outside of the boxes, because later in the game you will be asked to gather some rewards but not others"
   ],
 "OD": [
   "Now two open boxes will appear on the screen with different types of fruit inside them. One fruit was earned by a left response in the previous stage and the other by a right response. Although both types of fruit were valuable previously, one of them is now devalued and earns no points, whereas the other is still valuable and gains points. The devalued fruit will have a cross on it.",
   "You should respond by pressing the key that earns the valuable fruit. The points you earn now will not be shown on the screen but you will see your final total at the end of the game"
],
 "SOA": [
   "In the next part of the game, you’ll see a series of boxes with pictures of fruit on the outside and once again you can press left or right to open these and win points.",
   "The pictures on the box will be the same as the ones in the first game, and the correct response, left or right, will also be the same as what you learnt in the first half of the last game.<br> However, unlike before, some of the fruits inside the box are no longer valuable, meaning you can no longer earn points for them. In fact, if you try and open a box which contains a non-valuable fruit inside, you will have points subtracted from your total!",
   "You’ll be shown a screen at the beginning of each block of trials which will show you which (2 out of 6) fruits inside the boxes are no longer valuable by superimposing a cross. Look carefully at these and try to remember them.",
   "After that, the closed boxes will appear on the screen one after the other in quick succession, and you’ll have to respond very quickly to try and open them. However, if you think that inside that box is a devalued fruit you should not press anything at all and just wait for the next box to appear.",
 	"Obviously the idea is to earn as many points as possible. If the fruit inside is valuable and you press the correct key, you will still gain points. If the fruit inside is valuable and you press the incorrect key or fail to press any key, you neither gain nor lose points. You won’t receive feedback during the test, but you will be shown your final score at the end." ],
 "DD": [
   "In the next part of the game, you’ll see a series of boxes with pictures of fruit on the outside and you press left or right to open it and win points.",
	"The pictures on the box will be the same as the ones in the first game, and the correct response, left or right, will also be the same as what you learnt in the first half of the last game.",
	"However, unlike before, some of the boxes no longer contain valuable fruit rewards, meaning you can no longer earn points by opening these boxes. In fact, if you try and open one of these boxes, you will have points subtracted from your total!",
	"You’ll be shown a screen at the beginning of each block of trials which will show you the (2 out of 6) clues on the outside of the boxes shown with a cross superimposed to signal that these no longer contain a valuable reward. Look carefully at these and try to remember them. After that, the closed boxes will appear on the screen one after the other in quick succession, and you’ll have to respond very quickly to try and open them. However, if you think that a particular box no longer contains a valuable reward, you should not press any key all and just wait for the next box to appear.",
	"Obviously the idea is to earn as many points as possible. If the fruit inside is valuable and you press the correct key, you will gain points. If the fruit inside is valuable and you press the incorrect key or you fail to press a key, you neither gain nor lose points. You won’t receive feedback during the test, but you will be shown your final score at the end."
 ],
 "ID_wf": [
    "In this game, you will open tricky fruit boxes.<br>"+
      "The boxes look like this: <br>" +
      inst_o.render(false),

    "All boxes open from both the left and right. <br>"+
       "You can pick which way to open the box using the left (<kbd>←</kbd>) or right (<kbd>→</kbd>) arrow keys.<br>" +
       IDexample(null,null),

    "But the boxes have a trick to hide what's inside. <br>" +
       "If you pick the wrong side, the inside will appear empty and have no points.<br>" +
       IDexample(null, inst_b.feedback(0)),

    "You will get points for picking the correct side to open.<br>"+
       // "<br>You will get more points the faster you pick the correct side." +
       "Boxes labeled with the same fruit on the outside always open from the same side.",

    "The boxes have another trick.<br>"+
      "The fruit on the inside is different from fruit label on the outside.<br>"+
      "<b>Pay attention to this!</b>Later, you will get points for knowing what outside fruit label gives you the inside fruit." +
      IDexample(inst_b.feedback(1),inst_b.feedback(0)),

   "Learn how to open all the boxes and get the most points!<br>"+
      "Remember what fruits are inside the boxes too.<br>"+
      "Ready to play!?<br>"+
      "We'll start when you hit next."
 ],
 "OD_wf": [
   "You opened all the boxes we have! But we have too many of some of the inside fruits. <br>"+
     "You can now get points by picking only the inside fruits without an <font color=red><b>X</b></font> over them.<br>"+
    "<b>Pick a fruit by using the same side that opened the box the fruit was inside of</b>",

   "We'll tally up your score at the end. You wont know if you're right or wrong until then<br>"+
     "When you're ready to start, click next.",
     // <br>Go faster for more points."
 ],
 "SOA_wf": [
    "New box shipments are coming in, but some of the fruits inside have gone bad!<br>",
       "For each shipment, we have a chart showing good and bad fruits.<br>"+
       "Only open boxes with unspoiled fruits in them. Don't pick those with an <font color=red><b>X</b></font>  on them.",

    "You will still get points for opening boxes with good fruits inside<br>"+
      "But <b>do not even try to open a box with a spoiled fruit</b>.<br>"+
      "If you correctly open a box with spoiled fruit inside, you'll lose points!",

   "You'll have 5 seconds to memorize the good/bad chart for each shipment.<br>"+
      "Then, you will only have a second to open or pass each box in the shipment.<br>",
      "You'll see how well you did at the end of each shipment,<br>"+
      "but you wont know if you're right or wrong until then.",

    "Remember:<ul style='text-align:left'>" +
      "<li>5 seconds to memorize the chart for this shipment</li>" + 
      "<li>1 second to to pick or pass</li>" + 
      "<li>Don't open boxes with <font color=red><b>X</b></font>'ed fruits inside</li>" + 
      "</ul>When you're ready, click next.",
    //"Just like before, the faster you get unspoiled inside fruits, the more points you get"
 ],
 "DD_wf": [
    "Someone tried to intercept our shipments of tricky boxes and damanged some of them!<br>" +
      "For each shipment, we have a chart of what boxes were damaged.", 
    "You will still get points for opening boxes with good fruits inside<br>"+
      "Like before, <b>don't even try to open a damaged box</b>.<br>" +
      "If you open a damanged box correctly, you'll lose points!",
    "You'll see how well you did at the end of each shipment,<br>" +
      "but you wont know if you're right or wrong until then.",
    "Remember:<ul style='text-align:left'>" +
      "<li>5 seconds to memorize the chart</li>" + 
      "<li>1 second to to pick or pass</li>" + 
      "<li>Don't open boxes where the outside label is <font color=red><b>X</b></font>'ed out</li>" + 
      "</ul>When you're ready, click next.",
    //"Just like before, the faster you correctly open undamaged boxes, the more points you get"
 ]
}
