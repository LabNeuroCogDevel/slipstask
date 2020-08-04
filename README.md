# Slips of Action/Fabulous Fruits @ LNCD: jspsych (javascript) & psychopy (python) ports

Port of *Simplified Fabulous Fruit Game*, Sanne de Wit, 2019. Developed for remote administration. see [manual](./SimplifiedFFG_Manual_2019.txt).

* 12 fruits: apple, bananas, cherries, coconut, grape, kiwi, lemon, melon, orange, pear, pineapple, strawberry
  * uniquely 6 outside paired with 6 inside

## Example

### Javscript
https://labneurocogdevel.github.io/slipstask/

[<img src="./outline.svg?raw=True" height=400>](./outline.svg)

### 2018 ENEURO

[<img src="./task2018.jpg?raw=True" height=400>](./task2018.jpg)

## Papers
[de Wit et al. JEP-ABPP, 2007](https://doi.org/10.1037/0097-7403.33.1.1);
[de Wit et al. JNSc, 2009](https://doi.org/10.1523/JNEUROSCI.1639-09.2009);
de Wit et al. JCNSc, 2011;
Gillan et al. AmJPsychiatry, 2011;
[de Wit et al, JNeurosci, 2012](https://doi.org/10.1523/JNEUROSCI.1088-12.2012) *;
de Wit et al. Psychopharm, 2012;
[Sjoerds et al.  Front. 2016](https://doi.org/10.3389/fnbeh.2016.00234) *;
[de Wit et al. ENEURO, 2018](https://dx.doi.org/10.1523%2FENEURO.0240-18.2018)

## Task
* originally used <kbd>z</kbd> (left) and <kbd>m</kbd> (right) keys
* now  <kbd>←</kbd> and <kbd>→</kbd>
* measurements to calculate  devaluation sensitivity index [Sjoerds et al.  Front. 2016](https://doi.org/10.3389/fnbeh.2016.00234)
  > We calculated the DSI for the slips-of-action phase by subtracting percentages of responses made toward devalued outcomes from percentages of responses made toward still valuable outcomes, according to the following formula: ((N valued responses/N total responses) − (N devalued responses/N total responses)).


### Overview
* SRO e.g. Apple:Right-Kiwi
	* Stimulus: box labeled with Apple.
	* Response: right key opens the box.
	* Outcome: Kiwi is inside the box.

1. ID - Instructed Discrimination
  * Apple:Right-Kiwi
  * Pear:Left-Grape
  * ... [4 more]
1. OD - Outcome Devaluation 
  * trial: present 2 outcomes, devalued (X'ed out) Kiwi (prev used Right key to get) v. valued Grape (prev used Left key to get)
  * correct response is Left
1. SOA - Slips of action 
  * cue: devalue Kiwi, value Grape, [...4 more] 
  * "go" trial: Pear. Correct response: Left
  * "no-go" trial: Apple. Correct response: None (abstained)
1. DD - Discrimination Devaluation 
  * cue: devalue Apple, value Pear
  * "go" trial: Pear. Correct response: Left
  * "no-go" trial: Apple. Correct response: None (abstained)

### ID: Instrumental Discrimination (Training)
Instrumental Discrimination Stimulus Response-Outcome (SRO) training
* 7-8 min total
* 6 SROs to learn.
* 8 blocks of 12 trials (96 total). each of the 6 fruit boxes seen 16 times.
* score at top. feedback 
* ITI always ~1.5sec~ 1 sec

> During each of six blocks, each stimulus was presented twice, in random order.
[de Wit et al, JNeurosci, 2012](https://doi.org/10.1523/JNEUROSCI.1088-12.2012) *;

>This phase comprised eight blocks and a total of 96 trials. Dividing the task into blocks with randomized stimulus order within each block aided in measuring a learning effect across blocks, and ensured that participants learned all stimuli evenly divided throughout the experiment, instead of randomly seeing only a high amount of repetitions of one stimulus e.g., at the end of the training. Each stimulus was displayed 16 times in order for all participants to adequately learn the S-R-O associations.
[Sjoerds et al.  Front. 2016]

### OD: Outcome Devaluation - R-O knowldege
Instructed outcome-devaluation test assess response-outcome (R-O)
* The participant is presented two prevous outcomes (fruit inside box)
 * a Left and Right previous outcome (randomly stacked vertically)
 * One outcome is X'ed out.
 * should push the key that previously yielded the currently still valued (not X'ed) outcome.
* 1 block, 36 trials
* no feedback, score at the end


>  This phase was comprised of 36 trials. Participants were not directly given feedback on each trial, but instead were instructed that correct button presses would still earn them points and that they would be shown their total score at the end of the test phase.
[Sjoerds et al.  Front. 2016]

### Slips of Action
A *slip of action* is a failure to withhold a response towards a devalued outcome => S-R habitual control (cf.  goal-directed S-O-R) 
* Present
  * instruction: outcome 2/6 fruits devalued (superimposed X)
  * no response encouraged on stimulus leading to devalued outcome
* 2016: 9 blocks w/ 12 trials each (2 outcomes per bloc), 108 trials total. (N.B. `6C2 == 15`)
  * each outcome devalued 3 times (36 devalued, 72 valued)
* 2012: 6 blocks w/24 trials each
* 5s instructions, 1s response, 1s ITI

> However, unlike before, some of the fruits inside the box are no longer
> valuable, meaning you can no longer earn points for them. In fact, if
> you try and open a box which contains a non-valuable fruit inside, you
> will have points subtracted from your total!
[instructions in manual]

>Each of six 24-trial blocks began with a 5 s screen displaying all six fruit outcomes, with two of these (pertaining to different discrimination types and opposite key presses) shown with a cross superimposed indicating that these were devalued (Fig. 1c). Subsequently, participants were shown a succession of 2 s screens with closed boxes with the fruit stimuli on the front (separated by a 1 s intertrial interval). 
[de Wit et al, JNeurosci, 2012](https://doi.org/10.1523/JNEUROSCI.1088-12.2012) *;

> nine blocks, with a total of 108 trials. At the beginning of each block an instruction screen with six possible outcomes (open boxes with animal icons inside) was shown for 5 s, two of them superimposed with a cross. The cross indicated devaluation of those outcomes, and that responding to the stimulus associated with those outcomes would consequentially no longer earn points. After this screen, stimulus pictures were shown in rapid succession. Participants had to respond as fast as possible with a correct button-press to stimuli (closed boxes with an animal icon printed on the front) associated with still-valuable outcomes, and withhold their response for stimuli associated with devalued outcomes. Each stimulus remained on the screen for a fixed 1000 ms, during which the participant had to respond or withhold their response, respectively. The next trial started after an inter-trial interval (ITI) of 1000 ms. As in the outcome-devaluation phase, also in this phase no direct feedback was given, in order to prevent new learning. Instead, the total amount of points was shown at the end of the phase. During each block, each of the six stimuli was shown twice in semi-random order, with the exception that stimuli were never directly repeated. Throughout the nine blocks, each outcome was devalued three times, resulting in 36 trials where the outcome was devalued, and 72 trials with still valuable outcomes.
[Sjoerds et al.  Front. 2016]



### DD: baseline test
Discrimination Devaluation (?): Devalue stimulus instead of outcome to test. otherwise same as Slips of Action

## Hacking

The task exists in two implementations here: web based javascript, and MR ready python.

### Javascript
Using jspsych and psiturk libraries

* `utils.ts` contains mkBox and Fruit class/prototype (typescript compiled to `utils.js`)
 - `Fruit` has properties and drawing/rendering functions
 - `mkBox` modifies 2 fruits to be pairs, sets correct response, and which SOA blocks are devalued for the fruit

#### Heroku
 see `$HOME/.psiturkconfig` w/ `[AWS Access]` containing `aws_access_key_id` and `aws_secret_access_key`. also `psiturk-heroku-config`

### Python
The python task implementation came second. Warts from porting show: see `info.devalued_blocks` <-> TrialHanlder Dataframe, L0..R1 not generated using set_names, ...
min numpy version is 1.18 (need `numpy.random.default_rng`). 

This version pays more attention to timing and psuedo-randomizes Left/Right choices.

#### Usage
```
# install (once)
pip install -e 'git+https://github.com/LabNeuroCogDevel/slipstask'

# with e.g. ~/.local/bin in $PATH
SOA
```

Running `SOA` opens a dialog box.
Currently (20200803), only phase "DD" supports checking "MR."
If MR is checked, timing files will be loaded, and an additional prompt will ask for start and end block numbers.
Otherwise, the additional prompt will confirm timing and repitition settings for the randomly generated trials.

#### Timing
see `timing/gentiming.py`

#### Code

* `soapy/__init__.py` - default task settings
* `soapy/bin/SOA` - default launcher
* `soapy/images` has links from `static/images`: pngs and obj lists (.txt)
