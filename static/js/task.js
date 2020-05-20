/* define timeline to be used by jspsych 
 * see utils.ts for most
   20200518WF - init

 */

var INSTRUCTIONS_DATA = {}; 
$.getJSON('/static/js/instructions.json', function(data) {
   INSTRUCTIONS_DATA = data;
});

var instructions = [mkInstruction(INSTRUCTIONS_DATA["DD_wf"])];

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


var timeline = [get_info, instructions].flat()
