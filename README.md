# LNCD jspsych port of Fabulous Fruits

Port of *Simplified Fabulous Fruit Game*, Sanne de Wit, 2019. Developed for remote administration. see [original manual](./SimplifiedFFG_Manual_2019.txt).

* 12 fruits: apple, bananas, cherries, coconut, grape, kiwi, lemon, melon, orange, pear, pineapple, strawberry
  * uniquely 6 outside paired with 6 inside
* 12 permutations: 2 sets (A, B) over shuffle # 1 to 6
  * see [`SROmap.csv`](./SROmap.csv)


de Wit et al. JNSc, 2009;
de Wit et al. JEP-ABPP, 2007;
de Wit et al. JCNSc, 2011;
Gillan et al. AmJPsychiatry, 2011;
de Wit et al, JNeurosci, 2012;
de Wit et al. Psychopharm, 2012

## Stages
### Training
Instrumental Discrimination Stimulus Response-Outcome (SRO) training
* 7-8 min total
* 6 SROs to learn.
* 8 blocks of x trials (84 total)
* ITI always 1.5sec

### OD: Outcome Devaluation - R-O knowldege
Instructed outcome-devaluation test assess response-outcome (R-O)
* The participant is presented two prevous outcomes (fruit inside box)
 * a Left and Right prevous outcome (randomly stacked verticlly)
 * One outcome is X'ed out.
 * should push the key that previously yieled the un-X'ed outcome.
* 1 block, 36 trials

### Slips of Action
A *slip of action* is a failure to withhold a response towards a devalued outcome => S-R habitual control (cf.  goal-directed S-O-R) 
* Present
  * instruction: outcome 2/6 fruits X'ed (devauled)
  * quick sucession of boxes
    * no response incorraged on stimulus leading to devauled outcome
* 1 block, 108 trials (6min)
* 5s instructions
* 1s response

> However, unlike before, some of the fruits inside the box are no longer
> valuable, meaning you can no longer earn points for them. In fact, if
> you try and open a box which contains a non-valuable fruit inside, you
> will have points subtracted from your total!


### DD: baseline test
Discrimination Devaluation (?): Devalue stimulus instead of outcome to test. otherwise same as Slips of Action

