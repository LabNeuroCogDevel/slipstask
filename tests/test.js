const u = require('../static/js/utils.js');
require('../static/js/jspsych/jspsych.js');
require('../static/js/jspsych/plugins/jspsych-html-keyboard-response.js');

// nice things
const rk=39; // right key
const lk=37; // left key
function a_box(){
    var a = new u.Fruit("apple");
    var k = new u.Fruit("kiwi");
    return(u.mkBox(a, k, u.Dir.Right, [1]))
}

/** count how many are devalued in each soa phase*/
function cnt_soa_phase(soa, nphase){
   // soa = soa_assign(9,6,3,2)
  var cnt=Array(nphase).fill(0);
  for(e of soa) for(i of e)  ++cnt[i];
  return(cnt)
}


describe("Boxes", function() {
  test("make fruit", function(){
    const f = new u.Fruit("apple");
    expect(f.name).toBe("apple");
  });

  test("make box", function(){
    var a = new u.Fruit("apple");
    var k = new u.Fruit("kiwi");

    const b = u.mkBox(a, k, u.Dir.Right, [1]);
    expect(a.direction).toBe(u.Dir.Right);
    expect(k.direction).toBe(u.Dir.Right);
   });   
      
  test("score devalued box", function(){
    const b = a_box();
    const as = b.S.score(rk, 500, 1);
    const bs = b.O.score(rk, 500, 1);
    // both -1 for incorrect
    expect(as).toBe(bs);
    expect(as).toBe(-1);
    // no response no score (considered good)
    expect(b.O.score(null, null, 1)).toBe(0);
    // wrong key is no harm of devalued
    expect(b.O.score(lk, 500, 1)).toBe(0);
  });
      
  test("score valued box", function(){
    const b = a_box();
    // correct directoy, get points
    expect(b.O.score(rk, 500, -1)).toBe(1);
    // wrong key is no harm of devalued
    expect(b.O.score(lk, 500, -1)).toBe(0);
    // no response no score
    expect(b.O.score(null, null, -1)).toBe(0);
  });
});


describe("randomized?", function() {
  test("devalued in phase", function() {
    expectarr = Array(9).fill(2);
    // run 10 times to try to catch random errors
    for(let i=0; i<10; i++){
      boxassign = cnt_soa_phase(u.soa_assign(9,6,3,2), 9);
      expect(boxassign).toStrictEqual(expectarr);
    }
  });
  test("boxes", function(){
    const soa = u.soa_assign(9, 6, 3, 2);
    var frts1 = u.fruits(); // boxes side effects will change values inside here
    var frts2 = u.fruits(); // boxes side effects will change values inside here
    const boxes1 = u.allBoxes(frts1, soa);
    const boxes2 = u.allBoxes(frts2, soa);

    // definetly should not be exactly the same
    x = u.showSRO(boxes1);
    y = u.showSRO(boxes2);
    expect(x).not.toBe(y);

    // count times the two random assingments have fruits that match
    // assigned openside, paired fruit, and stim or outcome
    sidesame=0; pairsame=0; stimsame=0;
    for(let f of Object.keys(frts1)) {
	pairsame += (frts1[f].pair.name === frts2[f].pair.name)?1:0;
	sidesame += (frts1[f].direction === frts2[f].direction)?1:0;
	stimsame += (frts1[f].SO === frts2[f].SO)?1:0;
	/*console.log(frts1[f].direction, ' vs ', frts2[f].direction, ' = ', sidesame, " ; ",
	            frts1[f].pair.name, ' vs ', frts2[f].pair.name, ' = ', pairsame, " ; ",
	            frts1[f].SO,        ' vs ', frts2[f].SO,        ' = ', stimsame);
         */
    }

    // totally random but unlikely to be all the same (all 12 match)
    expect(pairsame).toBeLessThan(12);
    expect(stimsame).toBeLessThan(12);
    expect(sidesame).toBeLessThan(12);
    
  });
});

