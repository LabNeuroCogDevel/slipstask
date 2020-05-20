var SETTINGS = {
    'version': '20200519.1-nothingyet',
    'ITI': 1000,
    'train_fbkdur': 1000
};
/** Stimulus (outside box) or Outcome (inside box) */
var SO;
(function (SO) {
    SO["Stim"] = "Stim";
    SO["Outcome"] = "Outcome";
})(SO || (SO = {}));
/** Key direction */
var Dir;
(function (Dir) {
    Dir["None"] = "None";
    Dir["Left"] = "Left";
    Dir["Right"] = "Right";
})(Dir || (Dir = {}));
// Keys to direction
var KEYS = {
    // https://www.cambiaresearch.com/articles/15/javascript-char-codes-key-codes
    90: Dir.Left,
    77: Dir.Right,
    37: Dir.Left,
    39: Dir.Right
};
var accept_keys = Object.keys(KEYS).map(function (x) { return parseInt(x); });
/** warp around KEYS to return None if empty */
function key_to_side(pushed) {
    var side = KEYS[pushed];
    if (pushed === undefined || pushed === null || side === null)
        return (Dir.None);
    return (side);
}
/** wrap array in instruction dict for timeline
 * @param pagedate array of insturctions
*/
function mkInstruction(pagedata) {
    return ({
        type: 'instructions',
        pages: pagedata,
        show_clickable_nav: true
    });
}
/** add task version to whatever object is passed in
 * @param data JSON string.
 * @return JSON string with 'taskver' add
*/
function add_version(data) {
    var d = JSON.parse(data);
    d.taskver = SETTINGS['version'];
    return (JSON.stringify(d));
}
/** Fruits have a one-to-one mapping to the inside or outside of a box */
var Fruit = /** @class */ (function () {
    function Fruit(name) {
        this.name = name;
        this.img = "static/images/" + name + ".gif";
        this.direction = Dir.None;
        this.devalued_blocks = [];
    }
    /** render html for fruit (inside or outside)
     * @param disabled True draw X over fruit
    */
    Fruit.prototype.render = function (disabled) {
        var boxtype = (this.SO == SO.Stim) ? "closed" : "open";
        var disabled_class = disabled ? "disabled" : "";
        return ("<div class='box " + boxtype + " " + disabled_class + "'><img class=\"fruit\" src=" + this.img + "></div>");
    };
    /** render html for soa grid
     * @param soa_block block number (see if in devalued_blocks)
    */
    Fruit.prototype.renderSOA = function (soa_block) {
        return (this.render(this.devalued_blocks.indexOf(soa_block) > -1));
    };
    /** show empty box or reveal fruit
     * @param score previous trials score (correct key push>0)
     */
    Fruit.prototype.feedback = function (score) {
        //console.log('feedback', pushed_keynum, 'is', push_side, 'v', this.direction);
        var img = (score > 0) ? "<img class=\"fruit\" src=" + this.img + ">" : "";
        return ("<div class='box open'>" + img + "</div>");
    };
    /** slips of action score. works for Discrimination Devalue (baseline test) too
      * @param pushed_keynum  keycode pushed by participant
      * @param soa_block      current slips of action block. check against Fruit.devalued_blocks
      * @param rt             unused. could amplify points if fast
      * @return score (0 or 1). consider higher for rt
    */
    Fruit.prototype.score = function (pushed_keynum, rt, soa_block) {
        // is devalued any keypush is bad
        var devalued = this.devalued_blocks.indexOf(soa_block) > -1;
        var push_side = key_to_side(pushed_keynum);
        if (devalued && push_side != Dir.None) {
            return (-1);
        }
        else if (!devalued && push_side == this.direction) {
            return (1);
        }
        else { // devalued no push, valued incorrect push
            return (0);
        }
    };
    return Fruit;
}());
/** mkBox makes a box and sets Fruit variables
 * @param s stim
 * @param o outcome
 * @param d direction to get outcome from stim
 * @return Box
*/
function mkBox(s, o, d, devalued_blocks) {
    // update Fruit info -- one a box is made, the fruit is exhausted (shouldn't be used elsewhere)
    s.devalued_blocks = o.devalued_blocks = devalued_blocks;
    o.direction = s.direction = d;
    s.SO = SO.Stim;
    o.SO = SO.Outcome;
    s.pair = o;
    o.pair = s;
    var box = { 'S': s, 'O': o };
    s.box = o.box = box;
    return (box);
}
/** Make dictionary of all fruits */
function fruits() {
    // build dictionary of fruits
    var fruits_string = ["apple", "bananas", "cherries", "coconut",
        "grape", "kiwi", "lemon", "melon",
        "orange", "pear", "pineapple", "strawberry"];
    var fruits = {};
    for (var _i = 0, fruits_string_1 = fruits_string; _i < fruits_string_1.length; _i++) {
        var f = fruits_string_1[_i];
        fruits[f] = new Fruit(f);
    }
    return (fruits);
}
/** make a trial that is a box selection
  * @param b box to use (has stimulus and outcome fruit)
  * @param soa_block optional slip of action block number (for devaluation)
*/
function mkBoxTrial(b, soa_block) {
    return ({
        type: 'html-keyboard-response',
        stimulus: b.S.render(false),
        choices: accept_keys,
        prompt: "<p>left or right</p>",
        on_finish: function (data) {
            data.score = b.S.score(data.key_press, data.rt, soa_block);
            data.chose = key_to_side(data.key_press);
            data.stim = b.S.name;
            data.outcome = b.O.name;
            data.block = 'Train1';
        }
    });
}
/** Feedback for Train Trials
*/
function mkTrainFbk() {
    return ({
        type: 'html-keyboard-response',
        //choices: ['z','m'],
        post_trial_gap: SETTINGS['ITI'],
        trial_duration: SETTINGS['train_fbkdur'],
        prompt: "<p></p>",
        stimulus: function (trial) {
            // setup win vs nowin feedback color and message
            var prev = jsPsych.data.get().last().values()[0];
            return (FRTS[prev.outcome].feedback(prev.score));
        },
        on_load: function (trial) { },
        on_finish: function (data) {
            data.block = 'Train1';
            // TODO: update psiTurk if not null
        }
    });
}
/** Outcome Devaluation
  * @param devalued - Fruit to devalue
  * @param valued   - Fruit to value
  devalued and valued should not have the same side response!
*/
function mkODTrial(devalued, valued) {
    var outcomes = [devalued.render(true), valued.render(false)];
    // TODO shuffle outcome strings?
    return ({
        type: 'html-keyboard-response',
        stimulus: outcomes.join("<br>"),
        choices: accept_keys,
        post_trial_gap: SETTINGS['ITI'],
        prompt: "<p>left or right</p>",
        on_finish: function (data) {
            data.block = 'OD';
            data.score = valued.score(data.key_press, data.rt, 0);
            data.chose = key_to_side(data.key_press);
            data.devalued = devalued.name;
            data.valued = valued.name;
            console.log("picked " + data.chose + " for " + valued.name + ",", "should be " + valued.direction + " => " + data.score);
        }
    });
}
// NB. no OD feedback
/** devalue grid for SOA or DD (baseline test)
  * @param fruits     list of all fruits
  * @param sea_block  block (devalue if within devalued_blocks)
  * @param SorO       use Stim (DD) or Outcome (SOA) fruit?
*/
function mkSOAgrid(fruits, soa_block, SorO) {
    var grid_fruits = fruits.filter(function (x) { return x.SO == SorO; });
    var grid = "";
    for (var i in grid_fruits) {
        var ii = parseInt(i);
        grid += grid_fruits[i].renderSOA(soa_block);
        if (ii % 3 == 0 && ii > 0) {
            grid += "\n<br>";
        }
    }
    console.log(grid);
    return ({
        type: 'html-keyboard-response',
        stimulus: grid,
        choices: accept_keys,
        post_trial_gap: SETTINGS['ITI']
    });
}
