import { mat4, type mat4 as Mat4Type } from "gl-matrix";
import type p5 from "p5";

/**
 * Class representing a single piece of a Rubik's Cube
 *
 * @class Piece
 * @property {number} x - The x position of the piece
 * @property {number} y - The y position of the piece
 * @property {number} z - The z position of the piece
 * @property {Mat4Type} matrix - The transformation matrix of the piece
 * @property {string | null} highlighted - The highlight color of the piece
 * @property {p5} p - The p5 instance
 *
 * @example
 * const piece = new Piece(1, 1, 1, p);
 * piece.show();
 * piece.update(2, 2, 2);
 * piece.highlighted = "red";
 * piece.show();
 */
export class Piece {
    x: number = 0;
    y: number = 0;
    z: number = 0;
    matrix: Mat4Type;
    highlighted: string | null;
    p: p5;

    /**
     * Constructor for the Piece class
     * @param x - The x position of the piece
     * @param y - The y position of the piece
     * @param z - The z position of the piece
     * @param p - The p5 instance
     *
     * @example
     * const piece = new Piece(1, 1, 1, p);
     * piece.show();
     */
    constructor(x: number, y: number, z: number, p: p5) {
        // Initialize transformation matrix
        this.matrix = mat4.create();
        // Set initial position
        this.update(x, y, z);
        // Highlight flag
        this.highlighted = null;
        // p5 instance
        this.p = p;
    }

    /**
     * Update the position of the piece
     * @param x - The new x position
     * @param y - The new y position
     * @param z - The new z position
     *
     * @example
     * const piece = new Piece(1, 1, 1, p);
     * piece.update(2, 2, 2);
     * piece.show();
     */
    update(x: number, y: number, z: number) : void {
        this.x = x;
        this.y = y;
        this.z = z;
        mat4.fromTranslation(this.matrix, [this.x, this.y, this.z]);
    }

    /**
     * Display the piece
     *
     * @example
     * const piece = new Piece(1, 1, 1, p);
     * piece.show();
     * piece.highlighted = "red";
     * piece.show();
     */
    show() : void {
        if (this.highlighted === "red") {
            this.p.fill(255, 0, 0);
        } else if (this.highlighted === "green") {
            this.p.fill(0, 255, 0);
        } else if (this.highlighted === "blue") {
            this.p.fill(0, 0, 255);
        } else {
            this.p.fill(200);
        }
        this.p.stroke(0);
        this.p.strokeWeight(2);
        this.p.push();
        this.p.applyMatrix(
            this.matrix[0], this.matrix[1], this.matrix[2], this.matrix[3],
            this.matrix[4], this.matrix[5], this.matrix[6], this.matrix[7],
            this.matrix[8], this.matrix[9], this.matrix[10], this.matrix[11],
            this.matrix[12], this.matrix[13], this.matrix[14], this.matrix[15]
        );
        this.p.box(1);
        this.p.pop();
    }
}
