/* define timeline to be used by jspsych 
   20200518WF - init

 */

const task_settings = {'TASKVER': '20200518.1-init'};

var instructions = {       
    type: 'instructions',     
    pages: [
    '<div>Fabulous Fruits</div>',

    '<div>Ready? <br>The game starts after this page<br><br>' +
    '</div>',
    ],        
    show_clickable_nav: true      
}    

var get_info = {
  type: 'survey-text',
  questions: [
    {prompt: "Your Name?", name: "name"}, 
    {prompt: "Your Age?",  name:"age"}
  ],
  on_finish: function(data){
      // add task version
      resp = JSON.parse(data.responses)
      resp.taskver = task_settings['TASKVER']
      data.responses=JSON.stringify(resp)
  }
};


var timeline = [get_info, instructions, trials].flat()
