// sketch.js
const dim = 3;
const cube = [];

function setup() {
    window.setupCanvas();

    // Initialize cube
    for (let i = 0; i < dim; i++) {
        cube[i] = [];
        for (let j = 0; j < dim; j++) {
            cube[i][j] = [];
            for (let k = 0; k < dim; k++) {
                const len = 50;
                const offset = (dim - 1) * len * 0.5;
                const x = len*i - offset;
                const y = len*j - offset;
                const z = len*k - offset;
                cube[i][j][k] = new window.Piece(x, y, z, len);
            }
        }
    }
}

function draw() {
    window.setBackground();
    for (let i = 0; i < dim; i++)
        for (let j = 0; j < dim; j++)
            for (let k = 0; k < dim; k++)
                cube[i][j][k].show();
}
