
const dim = 3;
let cube = [];

window.setup = () => {
    window.setupCanvas();

    cube = new Cube(dim);

    for (let i = 0; i < cube.pieces.length; i += 3) {
        cube.pieces[i].highlighted = "red";
        cube.pieces[i + 1].highlighted = "green";
        cube.pieces[i + 2].highlighted = "blue";
    }
}

window.draw = () => {
    window.setBackground();
    window.scale(50);

    cube.show()
}