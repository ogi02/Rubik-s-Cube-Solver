import { Move } from "./move";
import { Piece } from "./piece";
import { turnX, turnY, turnZ } from "./turn";
import type p5 from "p5";

/**
 * Class representing a Rubik's Cube
 *
 * @class Cube
 * @property {number} dimensions - The dimensions of the cube (e.g., 3 for a 3x3 cube)
 * @property {p5} p - The p5 instance
 * @property {Piece[]} pieces - The pieces of the cube
 */
export class Cube {
    dimensions: number;
    p: p5;
    pieces: Piece[];

    /**
     * Constructor for the Cube class
     *
     * @param dimensions - The dimensions of the cube (e.g., 3 for a 3x3 cube)
     * @param p - The p5 instance
     */
    constructor(dimensions: number, p: p5) {
        // Dimensions of the cube
        this.dimensions = dimensions;
        // p5 instance
        this.p = p;
        // Pieces of the cube
        this.pieces = [];

        // Define left and right boundaries for the pieces
        const leftBoundary = -Math.floor(this.dimensions / 2);
        const rightBoundary = Math.floor(this.dimensions / 2);
        // Create pieces for the cube
        for (let x = leftBoundary; x <= rightBoundary; x++) {
            for (let y = leftBoundary; y <= rightBoundary; y++) {
                for (let z = leftBoundary; z <= rightBoundary; z++) {
                    this.pieces.push(new Piece(x, y, z, this.p));
                }
            }
        }
    }

    /**
     * Display the cube by showing all its pieces
     *
     * @method show
     * @returns {void}
     */
    show() : void {
        this.pieces.forEach(piece => piece.show());
    }

    /**
     * Perform a turn on the cube based on the move text
     *
     * @method turn
     * @param {string} moveText - The text representation of the move (e.g., "R", "U'", "L2")
     * @returns {void}
     */
    turn(moveText: string) : void {
        // Parse the move
        const move = new Move(moveText);
        // Get turn details
        const { axis, angle, layerIndexes } = move.getTurn(this.dimensions);
        // Perform the turn based on the axis
        switch (axis) {
            case 'x':
                turnX(this.pieces, angle, layerIndexes);
                break;
            case 'y':
                turnY(this.pieces, angle, layerIndexes);
                break;
            case 'z':
                turnZ(this.pieces, angle, layerIndexes);
                break;
            default:
                throw new Error(`Invalid axis: ${axis}`);
        }
    }
}
