/** Stimulus (outside box) or Outcome (inside box) */
var SO;
(function (SO) {
    SO[SO["Stim"] = 0] = "Stim";
    SO[SO["Outcome"] = 1] = "Outcome";
})(SO || (SO = {}));
/** Key direction */
var Dir;
(function (Dir) {
    Dir[Dir["None"] = 0] = "None";
    Dir[Dir["Left"] = 1] = "Left";
    Dir[Dir["Right"] = 2] = "Right";
})(Dir || (Dir = {}));
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
    o.direction = d;
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
