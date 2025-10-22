window.Cube = class {
    constructor(dimensions) {
        // Dimensions of the cube
        this.dimensions = dimensions;
        // Pieces of the cube
        this.pieces = [];

        // Define left and right boundaries for the pieces
        const leftBoundary = -Math.floor(this.dimensions / 2);
        const rightBoundary = Math.floor(this.dimensions / 2);

        for (let x = leftBoundary; x <= rightBoundary; x++) {
            for (let y = leftBoundary; y <= rightBoundary; y++) {
                for (let z = leftBoundary; z <= rightBoundary; z++) {
                    this.pieces.push(new window.Piece(x, y, z));
                }
            }
        }
    }

    show = () => {
        this.pieces.forEach(piece => piece.show());
    }

    turn = (moveText) => {
        const move = new Move(moveText);

        const {axis, angle, layerIndexes} = move.getTurn(this.dimensions);

        switch (axis) {
            case 'x':
                window.turnX(this.pieces, angle, layerIndexes);
                break;
            case 'y':
                window.turnY(this.pieces, angle, layerIndexes);
                break;
            case 'z':
                window.turnZ(this.pieces, angle, layerIndexes);
                break;
            default:
                throw new Error(`Invalid axis: ${axis}`);
        }
    }
}