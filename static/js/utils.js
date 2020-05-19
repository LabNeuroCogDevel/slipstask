var SETTINGS = {
    'version': '20200519.1-nothingyet',
    'ITI': 1000,
    'train_fbkdur': 1000
};
/** Stimulus (outside box) or Outcome (inside box) */
var SO;
(function (SO) {
    SO[SO["Stim"] = 0] = "Stim";
    SO[SO["Outcome"] = 1] = "Outcome";
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
/** Fruits have a one-to-one mapping to the inside or outside of a box */
var Fruit = /** @class */ (function () {
    function Fruit(name) {
        this.name = name;
        this.img = "static/images/" + name + ".gif";
        this.direction = Dir.None;
    }
    /** render html for fruit (inside or outside)
     * @param disabled True draw X over fruit
    */
    Fruit.prototype.render = function (disabled) {
        var boxtype = (this.SO == SO.Stim) ? "closed" : "open";
        var disabled_class = disabled ? "disabled" : "";
        return ("<div class='box " + boxtype + " " + disabled_class + "'><img class=\"fruit\" src=" + this.img + "></div>");
    };
    /** show empty box or reveal fruit
     * @param pushed numeric value of key pushed. should be in KEYS*/
    Fruit.prototype.train_feedback = function (pushed_keynum) {
        var push_side = key_to_side(pushed_keynum);
        //console.log('feedback', pushed_keynum, 'is', push_side, 'v', this.direction);
        var img = (push_side === this.direction) ? "<img class=\"fruit\" src=" + this.img + ">" : "";
        return ("<div class='box open'>" + img + "</div>");
    };
    /** score (only for stim)
     * @param pushed_dir participant pushed Left/Right
     * @param rt  reaction time in ms. not used
     * @return score (0 or 1). consider higher for rt
    */
    Fruit.prototype.score = function (pushed_keynum, rt) {
        var push_side = key_to_side(pushed_keynum);
        console.log('score', pushed_keynum, 'is', push_side, 'v', this.direction);
        return ((push_side === this.direction) ? 1 : 0);
    };
    return Fruit;
}());
/** mkBox makes a box and sets Fruit variables
 * @param s stim
 * @param o outcome
 * @param d direction to get outcome from stim
 * @return Box
*/
function mkBox(s, o, d) {
    // update Fruit info -- one a box is made, the fruit is exhausted (shouldn't be used elsewhere)
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
    var fruits_string = ["apple", "bananas", "cherries", "coconut", "grape",
        "kiwi", "lemon", "melon", "openbox", "orange", "pear",
        "pineapple", "strawberry"];
    var fruits = {};
    for (var _i = 0, fruits_string_1 = fruits_string; _i < fruits_string_1.length; _i++) {
        var f = fruits_string_1[_i];
        fruits[f] = new Fruit(f);
    }
    return (fruits);
}
function mkTrainTrial(b) {
    return ({
        type: 'html-keyboard-response',
        stimulus: b.S.render(false),
        choices: accept_keys,
        //post_trial_gap: SCOREANIMATEDUR,
        //trial_duration: trialdur,
        prompt: "<p>left or right</p>",
        on_finish: function (data) {
            data.score = b.S.score(data.key_press, data.rt);
            data.chose = key_to_side(data.key_press);
            data.stim = b.S.name;
            data.outcome = b.O.name;
            // update psiTurk if exists
        }
    });
}
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
            return (FRTS[prev.outcome].train_feedback(prev.key_press));
        },
        on_load: function (trial) { },
        on_finish: function (data) { }
    });
}
