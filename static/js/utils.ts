/** Stimulus (outside box) or Outcome (inside box) */
enum SO { Stim, Outcome }
/** Key direction */
enum Dir { None, Left, Right }
/** Box has a 'S' stimulus outside, and 'O' outcome on the inside */
interface Box { S: Fruit; O: Fruit; }

/** Fruits have a one-to-one mapping to the inside or outside of a box */
class Fruit {
    img: string;
    // SO and direction set by BOX
    SO: SO;
    direction: Dir;
    pair: Fruit;
    box: Box; // recursive cycle - used for drawing
    constructor(public name: string) {
        this.img = `static/images/${name}.gif`;
        this.direction = Dir.None;
    }

    /** render html for fruit (inside or outside) 
     * @param disabled True draw X over fruit
    */
    render(disabled: boolean) {
        let boxtype = (this.SO == SO.Stim) ? "closed" : "open";
        let disabled_class = disabled ? "disabled" : "";
        return (`<div class='box ${boxtype} ${disabled_class}'><img class="fruit" src=${this.img}></div>`)
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
    o.direction = d;
    s.SO = SO.Stim; o.SO = SO.Outcome
    s.pair = o; o.pair = s;
    let box = { 'S': s, 'O': o };
    s.box = o.box = box;
    return (box)
}

/** Make dictionary of all fruits */
function fruits(): { [key: string]: Fruit; } {
    // build dictionary of fruits
    const fruits_string = ["apple", "bananas", "cherries", "coconut", "grape",
        "kiwi", "lemon", "melon", "openbox", "orange", "pear",
        "pineapple", "strawberry"];
    var fruits: { [key: string]: Fruit; } = {}
    for (const f of fruits_string) {
        fruits[f] = new Fruit(f);
    }
    return (fruits)
}
