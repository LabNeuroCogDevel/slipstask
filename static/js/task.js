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

/* 1. Instructed Discrimination. (6 boxes * 2 reps)*8 blocks */
const allID = mkIDblocks(boxes);

/* 2. OD - outcome devaluation */
const allOD = mkODblock(FRTS);

/* 3. SOA - slips of action
      9 blocks w/ 12 trials each (2 outcomes per bloc), 108 trials total. (N.B. `6C2 == 15`)
*/
const allSOA = mkSOAblocks(FRTS, boxes, SO.Outcome,  9, 2);
/* 4. DD - devalued discrimination */
const allDD  = mkSOAblocks(FRTS, boxes, SO.Stimulus, 9, 1);

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

