/* define timeline to be used by jspsych 
 * see utils.ts for most
   20200518WF - init

 */

// [{fruitname => Fruits(render(), side, soa devalue indexes)}, {...}, ...]
var FRTS = fruits(); // boxes side effects will change values inside here

// 9 blocks of 6 boxes each repeated 3 times. 2 devalued per block
// devaule for on Slips Of Action and Discrimination Devaluation 
const soa_boxes = soa_assign(9, 6, 3, 2);
const boxes = allBoxes(FRTS, soa_boxes);

const FrtsStim = boxes.map(x=>x.S);
const FrtsOutcome = boxes.map(x=>x.O);

/* 1. Instructed Discrimination. (6 boxes * 2 reps)*8 blocks */
const allID = mkIDblocks(boxes);

/* 2. OD - outcome devaluation */
const allOD = mkODblock(FRTS, 4); // 4 repeats of 3Lx3R = 36 trials

/* 3. SOA - slips of action
      9 blocks w/ 12 trials each (2 outcomes per bloc), 108 trials total. (N.B. `6C2 == 15`)
*/
var allSOA = mkSOAblocks(FRTS, boxes, SO.Outcome,  9, 2);
/* 4. DD - devalued discrimination */
var allDD  = mkSOAblocks(FRTS, boxes, SO.Stim,     9, 2);

/* Instructions */
// 20200525 - defined in instructions.js
/*
var INSTRUCTIONS_DATA = {}; 
// expect to be run from root, but cannot use / for github pages
// TODO: instructions.json into .js file?
// jquery imported in templates/exp.html and index.html
$.getJSON('static/js/instructions.json', function(data) {
   INSTRUCTIONS_DATA = data;
});
var instructions = [mkInstruction(INSTRUCTIONS_DATA["DD_wf"])];
*/


/*
  we will do SOA and DD in random order
*/
const SOADDinst = {
  SOA: mkInstruction(INSTRUCTIONS_DATA["SOA_wf"]),
  DD: mkInstruction(INSTRUCTIONS_DATA["DD_wf"]) }
var SOADDtl = {SOA: allSOA, DD:  allDD}
const blockorder = jsPsych.randomization.shuffle(['SOA','DD'])
// update block name
for(let i=0; i<blockorder.length; i++) {
  let bname = blockorder[i];
  for(let j=0; j< SOADDtl[bname].length; j++) {
    if(SOADDtl[bname][j].data === undefined) continue
    if(SOADDtl[bname][j].data.block === null) continue
    SOADDtl[bname][j].data.block= i+3 + "." + SOADDtl[bname][j].data.block;
  }
}


var debrief_trial={
    type: 'html-keyboard-response',
    stimulus: function(trial){
      // setup win vs nowin feedback color and message
      return(
          "<h2>Thanks for playing!</h2>" +
          "You accumulated " + sum_points() + " points!<br>" +
        "<b><font size='larger'>Push any key to finish!</font></b></p>")

    }
}


var TIMELINE = [
  // 1. ID
  mkInstruction(INSTRUCTIONS_DATA["ID_wf"]),
  allID,
  // 2. OD
  mkInstruction(INSTRUCTIONS_DATA["OD_wf"]),
  allOD,
  // 3. SOA or DD
  SOADDinst[blockorder[0]],
  SOADDtl[blockorder[0]],
  // 4. DD or SOA
  SOADDinst[blockorder[1]],
  SOADDtl[blockorder[1]],
  // 5. survey
  debrief_trial].flat()


var get_info = {
  type: 'survey-text',
  questions: [
    {prompt: "Your Name?", name: "name"}, 
    {prompt: "Your Age?",  name:"age"}
  ],
  on_finish: function(data){
      // add task version
     data.responses= add_version(data.responses)
  }
};
