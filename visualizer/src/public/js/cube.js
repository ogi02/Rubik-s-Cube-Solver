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
}