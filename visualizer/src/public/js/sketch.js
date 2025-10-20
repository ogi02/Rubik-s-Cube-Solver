
const dim = 3;
let cube = [];

window.setup = () => {
    window.setupCanvas();

    for (let x = -1, xIndex = 0; x <= 1; x++, xIndex++) {
        cube[xIndex] = [];
        for (let y = -1, yIndex = 0; y <= 1; y++, yIndex++) {
            cube[xIndex][yIndex] = [];
            for (let z = -1, zIndex = 0; z <= 1; z++, zIndex++) {
                cube[xIndex][yIndex][zIndex] = new window.Piece(x, y, z);
            }
        }
    }

    cube[0][0][2].highlighted = true;
}

window.draw = () => {
    window.setBackground();
    window.scale(50);

    for (let i = 0; i < dim; i++)
        for (let j = 0; j < dim; j++)
            for (let k = 0; k < dim; k++)
                cube[i][j][k].show();
}