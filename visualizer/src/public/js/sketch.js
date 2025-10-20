
const dim = 3;
let cube = [];

window.setup = () => {
    window.setupCanvas();

    cube = new Cube(dim);

    cube.pieces[2].highlighted = true;
}

window.draw = () => {
    window.setBackground();
    window.scale(50);

    cube.show()
}