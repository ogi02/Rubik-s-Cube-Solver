
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

    // let scramble = "R D2 L2 U F' L D U2 B R2 U2 D2 R2 B R2 B2 U L2 B Rw2 Uw2 D Rw2 R' B2 Rw2 D' R2 D2 R2 U2 Fw D2 L' Fw Uw2 Rw Uw2 F2 L D Rw' Uw";
    let scramble = "R U Dw' Uw2 3Rw 5Lw'";
    let splitScramble = scramble.split(" ");
    let moves = [];
    splitScramble.forEach(moveText => moves.push(new Move(moveText)));

    moves.forEach(move => {
        console.log(move.layer);
        console.log(move.direction);
        console.log(move.layerAmount);
        console.log(typeof move.layer);
        console.log(typeof move.direction);
        console.log(typeof move.layerAmount);
    })
}

window.draw = () => {
    window.setBackground();
    window.scale(50);

    cube.show()
}