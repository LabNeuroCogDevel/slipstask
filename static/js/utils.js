//declare var $: any;   //jquery
var SETTINGS = {
    'ITI_ID': 1000,
    'ITI_OD': 1000,
    'ITI_SOA': 1000,
    'dur_ID_fbk': 1000,
    'dur_SOAcue': 5000,
    'dur_SOA': 2000,
    'dur_score': 2000,
    // Instructed discrimination
    //  8 blocks of 12 trials (96 total). each of the 6 fruit boxes seen 16 times.
    'ID_reps': 2,
    'ID_blocks': 8
};
/** for practice, show grid of what we have
*/
function cheat_chart(bxs) {
    var table = "<table>";
    for (var _i = 0, bxs_1 = bxs; _i < bxs_1.length; _i++) {
        var b = bxs_1[_i];
        var left = b.O.feedback((b.O.direction == Dir.Left) ? 1 : 0);
        var right = b.O.feedback((b.O.direction == Dir.Right) ? 1 : 0);
        table +=
            "<tr>" +
                "<td>" + left + "</td>" +
                "<td><font size=30>←</font></td>" +
                "<td>" + b.S.render(false) + "</td>" +
                "<td><font size=30>→</font></td>" +
                "<td>" + right + "</td>" +
                "</tr>";
    }
    table += "</table>";
    return (table);
}
/** generate boxes
   * @param frts dictionary fruitname=>Fruit
   * @param soa_boxes output of soa_assign (block index on which to be devalued)
   SIDE-EFFECT: update each fruit with soa_boxes and direction.
   * @return list of created boxes: outside fruit + inside fruit (with fruits now having devalue block number and direction)
*/
function allBoxes(frts, soa_boxes) {
    var fruit_names = jsPsych.randomization.shuffle(Object.keys(frts));
    var nboxes = soa_boxes.length;
    if (nboxes != fruit_names.length / 2)
        alert("nboxes != nfruits/2");
    var sides = jsPsych.randomization.shuffle(jsPsych.randomization.repeat([Dir.Left, Dir.Right], nboxes / 2));
    var boxes = soa_boxes.map(function (devalidxs, i) { return mkBox(frts[fruit_names[i]], frts[fruit_names[nboxes + i]], sides[i], devalidxs); });
    return (boxes);
    /*
  const boxes = [mkBox(FRTS['apple'],   FRTS['kiwi'],      "Left",  soa_boxes[0]),
             mkBox(FRTS['grape'],   FRTS['lemon'],     "Right", soa_boxes[1]),
             mkBox(FRTS['bananas'], FRTS['coconut'],   "Right", soa_boxes[2]),
             mkBox(FRTS['melon'],   FRTS['cherries'],  "Left",  soa_boxes[3]),
             mkBox(FRTS['orange'],  FRTS['pineapple'], "Left",  soa_boxes[4]),
             mkBox(FRTS['pear'],    FRTS['strawberry'],"Right", soa_boxes[5])];

    */
}
function random_IDidx(n) {
    // repeat 0-5 twice
    var idxs = [];
    for (var j = 0; j < SETTINGS['ID_reps']; j++) {
        for (var i = 0; i < n; i++) {
            idxs.push(i);
        }
    }
    // shuffle for number of blocks
    // typescript issue - without init to empty array, get DNE error
    var idxlist = [];
    for (var i = 0; i < SETTINGS['ID_blocks']; i++) {
        idxlist.push(jsPsych.randomization.shuffle(idxs));
    }
    //flatten and return
    return ([].concat.apply([], idxlist));
}
/** Instructed Discrimianation (first block)
  * @param boxes boxes (6)
  * @return timeline ready array of ID events
*/
// TODO: merge random_IDidx so we can add score
function mkIDblocks(boxes) {
    var fbk = mkIDFbk(FRTS);
    var IDidx = random_IDidx(boxes.length);
    var IDblocknum = -1; // -1 b/c this is not soa/dd
    var blksz = 12;
    // add feedback and score slide every blksz
    // NB. if every scoring with RT bonus, will need to change max given mkScoreFbk
    var allID = [].concat(IDidx.map(function (i, ii) { return [
        mkBoxTrial(boxes[i], IDblocknum, '1.ID_' + Math.floor(ii / blksz)),
        fbk,
        (ii > 0 && ii % 12 == 0) ? mkScoreFbk(blksz) : null
    ]; })).flat().filter(function (x) { return x !== null; });
    allID.push(mkScoreFbk(blksz));
    return (allID);
}
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
var NUMKEYS = [49, 50, 51, 52, 53, 54]; // keycodes for 1-6 in order
// Keys to direction
var KEYS = {
    // https://www.cambiaresearch.com/articles/15/javascript-char-codes-key-codes
    90: Dir.Left,
    77: Dir.Right,
    37: Dir.Left,
    39: Dir.Right
};
var accept_keys = Object.keys(KEYS).map(function (x) { return parseInt(x); });
//** save data if psiturk's uniqueId is defined and not null */
function save_data() {
    if (typeof uniqueId === 'undefined') {
        return;
    }
    if (uniqueId === null) {
        return;
    }
    psiturk.saveData({ success: function () { return; } });
}
/** warp around KEYS to return None if empty */
function key_to_side(pushed) {
    var side = KEYS[pushed];
    if (pushed === undefined || pushed === null || side === null)
        return (Dir.None);
    return (side);
}
/** wrap array in instruction dict for timeline
 * @param pagedate array of insturctions
 * @return jsPsych timeline ready dict object
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
        this.img = "static/images/".concat(name, ".png");
        this.direction = Dir.None;
        this.devalued_blocks = [];
    }
    /** render html for fruit (inside or outside)
     * @param disabled True draw X over fruit
    */
    Fruit.prototype.render = function (disabled) {
        var boxtype = (this.SO == SO.Stim) ? "closed" : "open";
        var disabled_class = disabled ? "disabled" : "";
        return ("<div class='box ".concat(boxtype, " ").concat(disabled_class, "'><img class=\"fruit\" src=").concat(this.img, "></div>"));
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
        var img = (score > 0) ? "<img class=\"fruit\" src=".concat(this.img, ">") : "";
        return ("<div class='feedback'>\n                <div class='score'>".concat(score, "</div><div class='box open'>").concat(img, "</div></div>"));
    };
    /** slips of action score. works for Discrimination Devalue (baseline test) too
      * @param pushed_keynum  keycode pushed by participant
      * @param rt             unused. could amplify points if fast
      * @param soa_block      current slips of action block. check against Fruit.devalued_blocks. -1 to always value
      * @return score (0 or 1). consider higher for rt
    */
    Fruit.prototype.score = function (pushed_keynum, rt, soa_block) {
        // is devalued any keypush is bad
        var devalued = this.isdevalued(soa_block);
        var push_side = key_to_side(pushed_keynum);
        //if (devalued && push_side != Dir.None) { // if any response is bad
        if (devalued && push_side == this.direction) {
            return (-1);
        }
        else if (!devalued && push_side == this.direction) {
            return (1);
        }
        else { // devalued no push, valued incorrect push
            return (0);
        }
    };
    /** do we value the box containing this fruit?
    * @param soa_block - block number
    * @return true if not valued on this block
    */
    Fruit.prototype.isdevalued = function (soa_block) {
        var devalued = this.devalued_blocks.indexOf(soa_block) > -1;
        return (devalued);
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
function fruits(input_fruits) {
    // build dictionary of fruits
    var fruits_strings = input_fruits ? input_fruits : ["apple", "bananas", "cherries", "coconut",
        "grape", "kiwi", "lemon", "melon",
        "orange", "pear", "pineapple", "strawberry"];
    var fruits = {};
    for (var _i = 0, fruits_strings_1 = fruits_strings; _i < fruits_strings_1.length; _i++) {
        var f = fruits_strings_1[_i];
        fruits[f] = new Fruit(f);
    }
    return (fruits);
}
/** make a trial that is a box selection
  * @param b box to use (has stimulus and outcome fruit)
  * @param soa_block optional slip of action block number (for devaluation)
*/
function mkBoxTrial(b, soa_block, block) {
    // ID and SOA/DD may have diffeernt ITIS
    var ITI = soa_block < 0 ? null : SETTINGS['ITI_SOA'];
    // if SOA, wait 1 second
    var dur = soa_block < 0 ? null : SETTINGS['dur_SOA'];
    return ({
        type: 'html-keyboard-response',
        stimulus: b.S.render(false),
        choices: accept_keys,
        post_trial_gap: ITI,
        trial_duration: dur,
        data: { block: block },
        prompt: "<p>left or right</p>",
        on_finish: function (data) {
            data.stim = b.S.name;
            data.outcome = b.O.name;
            data.isdevalued = b.S.isdevalued(soa_block);
            data.chose = key_to_side(data.key_press);
            data.score = b.S.score(data.key_press, data.rt, soa_block);
            data.cor_dir = data.isdevalued ? Dir.None : b.S.direction;
            if (DEBUG)
                console.log("".concat(data.stim, "/").concat(data.outcome, " is devl ").concat(data.isdevalued, ": ") +
                    "chose ".concat(data.chose, " should be ").concat(data.cor_dir, ". score ").concat(data.score, " w/rt ").concat(data.rt));
            save_data();
        }
    });
}
/** Feedback for Train Trials
*/
function mkIDFbk(frts) {
    return ({
        type: 'html-keyboard-response',
        //choices: ['z','m'],
        //post_trial_gap: SETTINGS['ITI'],
        choices: jsPsych.NO_KEYS,
        trial_duration: SETTINGS['dur_ID_fbk'],
        post_trial_gap: SETTINGS['ITI_SOA'],
        prompt: "<p></p>",
        stimulus: function (trial) {
            // setup win vs nowin feedback color and message
            var prev = jsPsych.data.get().last().values()[0];
            var frt = frts[prev.outcome];
            return (frt.feedback(prev.score));
        },
        //update
        //on_load: save_data(),
        on_finish: function (data) {
            data.block = '1.ID_score';
        }
    });
}
/** total all points score */
function sum_points() {
    return (jsPsych.data.get().select('score').sum());
}
/** get points since last score
    score blocks have a 'lastscore' element
    use that if it exists
    otherwise use total points so far
*/
function points_since_last_shown(total) {
    var lastscore = jsPsych.data.get().filterCustom(function (x) { return x.lastscore !== null; }).select('lastscore').values;
    var thisscore = (lastscore.length === 0) ? total : total - lastscore[lastscore.length - 1];
    return (thisscore);
}
/** mkScoreFbk
  * @return jspsych timeline obj to dispaly total score */
function mkScoreFbk(blkmax) {
    return ({
        type: 'html-keyboard-response',
        //choices: ['z','m'],
        //post_trial_gap: SETTINGS['ITI'],
        // only show for fixed duration
        trial_duration: SETTINGS['dur_score'],
        choices: jsPsych.NO_KEYS,
        stimulus: function (trial) {
            var totalscore = sum_points();
            var thisscore = points_since_last_shown(totalscore);
            if (blkmax === null) {
                var sum_prevmaxs = jsPsych.data.get().select('lasttotal').sum();
                sum_prevmaxs = sum_prevmaxs.length == 0 ? 0 : sum_prevmaxs[0];
                // N.B -- assume no RT bonus. assume max one point
                var nscored = jsPsych.data.get().filterCustom(function (x) { return x.score !== null; }).count();
                blkmax = nscored - sum_prevmaxs;
                if (DEBUG)
                    console.log("scoreFbk: not given block max. think it is ".concat(nscored, " - ").concat(sum_prevmaxs, " = ").concat(blkmax));
            }
            return ("<h3>You scored ".concat(thisscore, " of ").concat(blkmax, " possible points this round.</h3> Your total score is ").concat(totalscore));
        },
        on_finish: function (data) {
            data.block = 'score';
            data.lasttotal = blkmax;
            data.lastscore = sum_points();
        }
    });
}
/** Outcome Devaluation
  * @param devalued - Fruit to devalue
  * @param valued   - Fruit to value
  devalued and valued should not have the same side response!
*/
function mkODTrial(devalued, valued) {
    var outcomes = jsPsych.randomization.sampleWithoutReplacement([devalued.render(true), valued.render(false)], 2);
    // TODO shuffle outcome strings?
    return ({
        type: 'html-keyboard-response',
        stimulus: outcomes.join("<br>"),
        choices: accept_keys,
        post_trial_gap: SETTINGS['ITI_OD'],
        prompt: "<p>left or right</p>",
        on_finish: function (data) {
            data.block = '2.OD';
            var soa_block = -1; // not soa, no neg points for wrong
            data.score = valued.score(data.key_press, data.rt, soa_block);
            data.chose = key_to_side(data.key_press);
            data.devalued = devalued.name;
            data.valued = valued.name;
            // TODO: should we get -1 for bad choice?
            if (DEBUG)
                console.log("picked ".concat(data.chose, " for ").concat(valued.name, ","), "should be ".concat(valued.direction, " => ").concat(data.score));
        }
    });
}
// NB. no OD feedback
/** make all OD trials - all permutations: 1L & 1R of inside(outcome) fruits
  * @param frts all fruits (to filter on left and right and only inside (Outcome)
  * @param nreps number of times to repeat all(9) combinations(3 x 3). probably 4 => 36 total
  * @return array for timeline (ends with score)
*/
function mkODblock(frts, nreps) {
    var OD_left = Object.values(frts).filter(function (x) { return x.direction == Dir.Left && x.SO == SO.Outcome; });
    var OD_right = Object.values(frts).filter(function (x) { return x.direction == Dir.Right && x.SO == SO.Outcome; });
    // 1 block, 36 trials: each 3 R matched to each 3 L
    // generate factorized L and R 
    // and randomly assign top and bottom to either L, or R
    var OD_fac = jsPsych.randomization.factorial({ L: OD_left, R: OD_right }, nreps);
    var OD_order = [];
    // 9 combinations (expecting 36!)
    for (var i = 0; i < OD_fac.length; i++)
        OD_order.push(jsPsych.randomization.repeat(['L', 'R'], 1));
    var allOD = [];
    for (var i = 0; i < OD_fac.length; i++) {
        var sides = OD_order[i];
        var fruits_by_side = OD_fac[i];
        var top_1 = sides[0];
        var bot = sides[1];
        allOD.push(mkODTrial(fruits_by_side[top_1], fruits_by_side[bot]));
    }
    allOD.push(mkScoreFbk(allOD.length));
    console.log(OD_left, OD_right, OD_fac, OD_order, allOD);
    return (allOD);
}
/** devalue grid for SOA or DD (baseline test)
  * @param fruits     list of all fruits
  * @param sea_block  block (devalue if within devalued_blocks)
  * @param SorO       use outside Stim (DD) or inside Outcome (SOA) fruit?
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
    return ({
        type: 'html-keyboard-response',
        stimulus: grid,
        trial_duration: SETTINGS['dur_SOAcue'],
        choices: jsPsych.NO_KEYS,
        prompt: "Remember which fruits are bad"
    });
}
/** generate assignments for SOA - slips of action
  9 blocks w/ 12 trials each (2 outcomes per bloc), 108 trials total. (N.B. `6C2 == 15`)
  each outcome devalued 3 times (36 devalued, 72 valued)
  TODO: setup devalue per fruit in box creation
  * @param nblocks - number of blocks where 2/6 are randomly devalued (9)
  * @param nbox - number of boxes (6)
  * @param reps - number of repeats for each box (3)
  * @param choose - number of blocks per box (2)
  * @return per box devalued indexes e.g. [[0,5], [1,3], [0,1], ...] = first box devalued at block 0 and 5, 2nd @ 1&3, ...
  */
function soa_assign(nblocks, nbox, reps, choose) {
    /* would like to do something like
    const soaallbocks = jsPsych.randomization.repeat(Array.from({ length: 6 }, (_, i) => i), 3);
    const soaidx = jsPsych.randomization.shuffleNoRepeats(soaallbocks);
    var SOA_blist = [];
    for (i = 0; i < soaidx.length; i = i + 2) { SOA_blist = [soaidx[i], soaidx[i + 1]]; }
    but this may have e.g. 0,5 and then 5,0
    */
    var need_redo = false;
    var block_deval = Array(nblocks).fill(0); // # devalued boxes in each block (max `choose`)
    var bx_deval_on = Array(nbox).fill([]); // box X devalued block [[block,block,block], [...], ...]
    for (var bn = 0; bn < nbox; bn++) {
        if (bx_deval_on[bn].length >= reps) {
            continue;
        }
        var avail_slots = block_deval.map(function (x, i) { return [x, i]; }).filter(function (x) { return x[0] < choose; }).map(function (x) { return x[1]; });
        if (avail_slots.length < reps) {
            need_redo = true;
            break; // dont need to continue, draw was bad
        }
        var into = jsPsych.randomization.sampleWithoutReplacement(avail_slots, reps);
        bx_deval_on[bn] = into;
        for (var _i = 0, into_1 = into; _i < into_1.length; _i++) {
            var i = into_1[_i];
            block_deval[i]++;
        }
    }
    // if we had a bad draw, we need to rerun
    // N.B. there is no check to not recursise forever!
    if (need_redo)
        bx_deval_on = soa_assign(nblocks, nbox, reps, choose);
    return (bx_deval_on);
}
/** make all of slips of action/devalue discrimination
  * @param frts all the fruits
  * @param boxes all the boxes
  * @param so which part to show: outside=Stimulus(DD) or inside=Outcome(SOA)
  * @param nblocks how many blocks (9)
  * @param nreps how many repeats of each box per block (2)
  */
function mkSOAblocks(frts, boxes, so, nblocks, nreps) {
    var allbocks = [];
    // for psiturk, record what type of event this was
    var desc = so == SO.Outcome ? "SOA" : "DD";
    // TODO: 2 shouldn't be hardcoded. but number of devalued is unlikely to change
    var score = mkScoreFbk((boxes.length - 2) * nreps);
    for (var bn = 0; bn < nblocks; bn++) {
        allbocks.push(mkSOAgrid(Object.values(frts), bn, so));
        // each box seen twice. consider adding shuffleNoRepeats
        var boxreps = jsPsych.randomization.repeat(boxes, nreps);
        for (var _i = 0, boxreps_1 = boxreps; _i < boxreps_1.length; _i++) {
            var bx = boxreps_1[_i];
            allbocks.push(mkBoxTrial(bx, bn, desc + "_" + bn));
        }
        // after the end of a block, show score
        allbocks.push(score);
    }
    return (allbocks);
}
/** free form survey responses */
var surveyTextTrail = {
    type: 'survey-text',
    questions: [
        { name: "understand", prompt: "How well do you feel like you understood the task (0=not at all, 5=fully)?" },
        { name: "side_strategy", prompt: "What stategy or strategies did you use to remember the correct way to open boxes?" },
        { name: "pair_strategy", prompt: "How did you remember the inside-outside fruit pairs of each box?" },
        { name: "effort", prompt: "Were you able to concentrate while playing the game? Did you have to take any breaks?" },
        { name: "misc", prompt: "Do you have any other comments on the game?" },
    ],
    on_finish: function (data) { save_data(); }
};
/** create stim response or outcome response survey
    simliiar to mkBoxTrial or mkODTrial. but data out columns prefixed with "survey_"
  * @param frt a fruit
  * @return left/right html response trial
*/
function mkFrtSurvey(frt) {
    return ({
        type: 'html-keyboard-response',
        prompt: "<p>left or right</p>",
        choices: accept_keys,
        stimulus: function (trial) {
            // TODO: hard coded left and right
            // maybe: Object.values(KEYS).indexOf('Left')
            return ("<div class='survey_arrow' onclick='simkey(37)'>←</div>" +
                "<img src='".concat(frt.img, "'/>") +
                "<div class='survey_arrow' onclick='simkey(39)'>→</div><br>");
        },
        on_finish: function (data) {
            data.survey_type = frt.SO == SO.Stim ? "SR" : "OR";
            data.survey_prompt = frt.name;
            data.survey_chose = key_to_side(data.key_press);
            data.correct = frt.score(data.key_press, 0, -1) > 0;
        }
    });
}
/** send a keypress. useful for button push on keyboard trial
  * @param keyCode of character to send. see e.g. "a".charCodeAt(0)
*/
function simkey(key) {
    // for charcode see e.g. "a".charCodeAt(0) 
    // from jsPsych/tests/testing-utils.js:
    var dispel = document.querySelector('.jspsych-display-element');
    dispel.dispatchEvent(new KeyboardEvent('keydown', { keyCode: key }));
    dispel.dispatchEvent(new KeyboardEvent('keyup', { keyCode: key }));
    // record that it was simulated push instead of key 
    jsPsych.data.get().addToLast({ touched: true });
    if (DEBUG)
        console.log('sent', key, 'updated', jsPsych.data.get().last().values());
}
function numberFrts(Frts) {
    return (Frts.map(function (f, i) {
        return "<div class=\"survey_outfrt\" style=\"background-image:url('".concat(f.img, "')\" onclick=\"simkey(NUMKEYS[").concat(i, "])\"><p>").concat(i + 1, "</p></div>") + (i == 2 ? "<br>" : "");
    }).
        join("\n"));
}
function mkPairSurvey(frt, boxes) {
    return ({
        type: 'html-keyboard-response',
        choices: NUMKEYS,
        //prompt: "<p>Which fruit is this fruits pair</p>",
        stimulus: function (trial) {
            return ("<img src='".concat(frt.img, "'/> is paired with:<br>") + numberFrts(boxes.map(function (x) { return x.O; })));
        },
        on_finish: function (data) {
            var chosefrt = boxes[NUMKEYS.indexOf(data.key_press)].O;
            data.survey_type = "SO";
            data.survey_prompt = frt.name;
            data.survey_chose = chosefrt.name;
            data.correct = frt.pair.name == chosefrt.name;
            if (DEBUG)
                console.log("".concat(data.survey_prompt, " has pair ").concat(frt.pair.name, ". chose ").concat(data.suvery_chose, ". correct? ").concat(data.correct));
        }
    });
}
/** make confidence slider trial
   prev trials should have data with
    - conf_prompt
    - conf_show
    - survey_type
   @return trial
*/
function mkConfSlider() {
    return ({
        type: 'html-slider-response',
        stimulus: function (trial) {
            var prev = jsPsych.data.get().last().values()[0];
            var show = "<img src='static/images/".concat(prev.survey_prompt, ".png'/> ");
            var resp = "<br>opens from the " + prev.survey_chose;
            if (prev.survey_type == 'SO') {
                resp = " is paired with <img src='static/images/" + prev.survey_chose + ".png' />";
            }
            return ("How confident are you that <br><br>" + show + resp + "<br><br>");
        },
        labels: ['Not at all', 'Extremely'],
        //prompt: "<p>How confident are you about your answer</p>",
        on_finish: function (data) {
            var prev = jsPsych.data.get().last(2).values()[0];
            // recapitulate previous here for easy data parsing (just need this row)
            data.survey_rt = prev.rt;
            data.conf_rt = data.rt;
            data.survey_type = prev.survey_type;
            data.survey_prompt = prev.survey_prompt;
            data.survey_chose = prev.survey_chose;
            data.correct = prev.correct;
            // TODO: calculate summary stats
            save_data();
        }
    });
}
/** quickly get info about the box/fruit associations Stim-Response:Outcome
  * @param boxes boxes with fruits
  * @return stim name, direction, and outcome name
*/
function showSRO(boxes) {
    return (boxes.map(function (x) { return [x.S.name, x.S.direction, x.O.name]; }));
}
/** all survey into one block
 * @param boxes used for expreiment
*/
function mkSurveyBlock(boxes) {
    var conf = mkConfSlider();
    var S = jsPsych.randomization.shuffle(boxes.map(function (x) { return x.S; }));
    var O = jsPsych.randomization.shuffle(boxes.map(function (x) { return x.O; }));
    var P = jsPsych.randomization.shuffle(boxes.map(function (x) { return x.S; }));
    var TL = [];
    for (var _i = 0, _a = [S, O].flat(); _i < _a.length; _i++) {
        var f = _a[_i];
        TL.push(mkFrtSurvey(f));
        TL.push(conf);
    }
    for (var _b = 0, P_1 = P; _b < P_1.length; _b++) {
        var f = P_1[_b];
        TL.push(mkPairSurvey(f, boxes));
        TL.push(conf);
    }
    TL.push(surveyTextTrail);
    return (TL);
}
// cheaters way of making the module
if (typeof module !== "undefined") {
    module.exports = {
        mkIDblocks: mkIDblocks,
        mkODblock: mkODblock,
        mkSOAblocks: mkSOAblocks,
        mkSurveyBlock: mkSurveyBlock,
        mkBoxTrial: mkBoxTrial,
        mkIDFbk: mkIDFbk,
        mkBox: mkBox,
        fruits: fruits,
        soa_assign: soa_assign,
        allBoxes: allBoxes,
        showSRO: showSRO,
        Fruit: Fruit,
        Dir: Dir,
        SO: SO,
        KEYS: KEYS
    };
}
