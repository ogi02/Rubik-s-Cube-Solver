
const dim = 5;
let cube = [];

window.setup = () => {
    window.setupCanvas();

    cube = new Cube(dim);

    for (let i = 0; i < cube.pieces.length; i += dim) {
        cube.pieces[i].highlighted = "red";
        cube.pieces[i + 1].highlighted = "green";
        cube.pieces[i + 2].highlighted = "blue";
        cube.pieces[i + 3].highlighted = "red";
        cube.pieces[i + 4].highlighted = "green";
    }

    // let scramble = "R D2 L2 U F' L D U2 B R2 U2 D2 R2 B R2 B2 U L2 B Rw2 Uw2 D Rw2 R' B2 Rw2 D' R2 D2 R2 U2 Fw D2 L' Fw Uw2 Rw Uw2 F2 L D Rw' Uw";
    // let scramble = "R U Dw' Uw2 3Rw 5Lw'";
    // let scramble = "R U";
    // let splitScramble = scramble.split(" ");
    // splitScramble.forEach(moveText => cube.turn(moveText));
}

window.draw = () => {
    window.setBackground();
    window.scale(50);

    cube.show()
}

window.keyPressed = key => {
    console.log(`Key pressed: ${key.key}`);
    if (key.key === 's') {
        let scramble = "2Dw";
        let splitScramble = scramble.split(" ");
        for (let i = 0; i < splitScramble.length; i++) {
            setTimeout(() => {
                cube.turn(splitScramble[i]);
            }, i * 1000);
        }
    }
}