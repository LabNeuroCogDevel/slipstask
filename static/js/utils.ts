declare var jsPsych: any;
declare var FRTS: any;
const SETTINGS = {
    'version': '20200519.1-nothingyet',
    'ITI': 1000,
    'train_fbkdur': 1000,
}
/** Stimulus (outside box) or Outcome (inside box) */
enum SO { Stim, Outcome }
/** Key direction */
enum Dir { None = "None", Left = "Left", Right = "Right" }
/** Box has a 'S' stimulus outside, and 'O' outcome on the inside */
interface Box { S: Fruit; O: Fruit; }
// Keys to direction
const KEYS: { [key: number]: Dir; } = {
    // https://www.cambiaresearch.com/articles/15/javascript-char-codes-key-codes
    90: Dir.Left,  //z
    77: Dir.Right, //m
    37: Dir.Left,  //left arrow
    39: Dir.Right, //right arrow
}
const accept_keys = Object.keys(KEYS).map(x => parseInt(x))

/** warp around KEYS to return None if empty */
function key_to_side(pushed: number): Dir {
    const side = KEYS[pushed]
    if (pushed === undefined || pushed === null || side === null)
        return (Dir.None)
    return (side)
}

/** Fruits have a one-to-one mapping to the inside or outside of a box */
class Fruit {
    img: string;
    // SO and direction set by BOX
    SO: SO;
    direction: Dir;
    pair: Fruit;
    box: Box; // recursive cycle - used for drawing
    devalued_blocks: number[]; // on which Slips Block to devalue
    constructor(public name: string) {
        this.img = `static/images/${name}.gif`;
        this.direction = Dir.None;
        this.devalued_blocks = [];
    }

    /** render html for fruit (inside or outside) 
     * @param disabled True draw X over fruit
    */
    render(disabled: boolean): string {
        let boxtype = (this.SO == SO.Stim) ? "closed" : "open";
        let disabled_class = disabled ? "disabled" : "";
        return (`<div class='box ${boxtype} ${disabled_class}'><img class="fruit" src=${this.img}></div>`)
    }
    /** show empty box or reveal fruit
     * @param score previous trials score (correct key push>0)
     */
    feedback(score: number): string {
        //console.log('feedback', pushed_keynum, 'is', push_side, 'v', this.direction);
        const img = (score > 0) ? `<img class="fruit" src=${this.img}>` : ""
        return (`<div class='box open'>${img}</div>`)
    }

    /** slips of action score. works for Discrimination Devalue (baseline test) too
      * @param pushed_keynum  keycode pushed by participant
      * @param soa_block      current slips of action block. check against Fruit.devalued_blocks
      * @param rt             unused. could amplify points if fast
      * @return score (0 or 1). consider higher for rt
    */
    score(pushed_keynum: number, rt: number, soa_block: number): number {
        // is devalued any keypush is bad
        const devalued: boolean = this.devalued_blocks.indexOf(soa_block) > -1
        const push_side = key_to_side(pushed_keynum);
        if (devalued && push_side != Dir.None) {
            return (-1)
        } else if (!devalued && push_side == this.direction) {
            return (1)
        } else { // devalued no push, valued incorrect push
            return (0)
        }
    }
}

/** mkBox makes a box and sets Fruit variables
 * @param s stim 
 * @param o outcome
 * @param d direction to get outcome from stim
 * @return Box 
*/
function mkBox(s: Fruit, o: Fruit, d: Dir): Box {
    // update Fruit info -- one a box is made, the fruit is exhausted (shouldn't be used elsewhere)
    o.direction = s.direction = d;
    s.SO = SO.Stim; o.SO = SO.Outcome
    s.pair = o; o.pair = s;
    let box = { 'S': s, 'O': o };
    s.box = o.box = box;
    return (box)
}

/** Make dictionary of all fruits */
function fruits(): { [key: string]: Fruit; } {
    // build dictionary of fruits
    const fruits_string = ["apple", "bananas", "cherries", "coconut",
        "grape", "kiwi", "lemon", "melon",
        "orange", "pear", "pineapple", "strawberry"];
    var fruits: { [key: string]: Fruit; } = {}
    for (const f of fruits_string) {
        fruits[f] = new Fruit(f);
    }
    return (fruits)
}


/** make a trial that is a box selection
  * @param b box to use (has stimulus and outcome fruit)
  * @param soa_block optional slip of action block number (for devaluation)
*/
function mkBoxTrial(b: Box, soa_block: number) {
    return ({
        type: 'html-keyboard-response',
        stimulus: b.S.render(false),
        choices: accept_keys,
        prompt: "<p>left or right</p>",
        on_finish: function(data) {
            data.score = b.S.score(data.key_press, data.rt, soa_block);
            data.chose = key_to_side(data.key_press)
            data.stim = b.S.name;
            data.outcome = b.O.name;
            data.block = 'Train1';
        }
    })
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
        stimulus: function(trial) {
            // setup win vs nowin feedback color and message
            let prev = jsPsych.data.get().last().values()[0];
            return (FRTS[prev.outcome].feedback(prev.score))
        },
        on_load: function(trial) { },
        on_finish: function(data) {
            data.block = 'Train1';
            // TODO: update psiTurk if not null
        }
    })
}
/** Outcome Devaluation
  * @param devalued - Fruit to devalue
  * @param valued   - Fruit to value
  devalued and valued should not have the same side response!
*/
function mkODTrial(devalued: Fruit, valued: Fruit) {
    const outcomes: string[] = [devalued.render(true), valued.render(false)];
    // TODO shuffle outcome strings?

    return ({
        type: 'html-keyboard-response',
        stimulus: outcomes.join("<br>"),
        choices: accept_keys,
        post_trial_gap: SETTINGS['ITI'],
        prompt: "<p>left or right</p>",
        on_finish: function(data) {
            data.block = 'OD';
            data.score = valued.score(data.key_press, data.rt, 0);
            data.chose = key_to_side(data.key_press)
            data.devalued = devalued.name;
            data.valued = valued.name;
            console.log(`picked ${data.chose} for ${valued.name},`,
                `should be ${valued.direction} => ${data.score}`)
        }
    })
}
// NB. no OD feedback
