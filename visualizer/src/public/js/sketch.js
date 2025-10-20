
const dim = 5;
const len = 50;
let cube = [];

window.setup = () => {
    window.setupCanvas();

    for (let i = 0; i < dim; i++) {
        cube[i] = [];
        for (let j = 0; j < dim; j++) {
            cube[i][j] = [];
            for (let k = 0; k < dim; k++) {
                const offset = (dim - 1) * len * 0.5;
                const x = len*i - offset;
                const y = len*j - offset;
                const z = len*k - offset;
                cube[i][j][k] = new window.Piece(x, y, z, len);
            }
        }
    }
}

window.draw = () => {
    window.setBackground();

    for (let i = 0; i < dim; i++)
        for (let j = 0; j < dim; j++)
            for (let k = 0; k < dim; k++)
                cube[i][j][k].show();
}