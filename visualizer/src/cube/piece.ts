import { mat4, vec3, type mat4 as Mat4Type } from "gl-matrix";
import type p5 from "p5";
import { Face } from "./face";
import {roundToDecimal} from "../utils/math.ts";

/**
 * Class representing a single piece of a Rubik's Cube
 *
 * @class Piece
 * @property {number} x - The x position of the piece
 * @property {number} y - The y position of the piece
 * @property {number} z - The z position of the piece
 * @property {number} dimensions - The dimension of the cube
 * @property {Face[]} faces - The faces of the piece
 * @property {Mat4Type} matrix - The transformation matrix of the piece
 * @property {p5} p - The p5 instance
 *
 * @example
 * const piece = new Piece(1, 1, 1, p);
 * piece.show();
 * piece.update(2, 2, 2);
 * piece.show();
 */
export class Piece {
    x: number = 0;
    y: number = 0;
    z: number = 0;
    dimensions: number;
    faces: Face[] = [];
    matrix: Mat4Type;
    p: p5;

    /**
     * Constructor for the Piece class
     * @param x - The x position of the piece
     * @param y - The y position of the piece
     * @param z - The z position of the piece
     * @param dimensions - The dimension of the cube
     * @param p - The p5 instance
     *
     * @example
     * const piece = new Piece(1, 1, 1, 3, p);
     * piece.show();
     */
    constructor(x: number, y: number, z: number, dimensions: number, p: p5) {
        // Initialize transformation matrix
        this.matrix = mat4.create();
        // Set initial position
        this.update(x, y, z);
        // Set dimensions
        this.dimensions = dimensions;
        // Color faces
        this.colorFaces();
        // p5 instance
        this.p = p;
    };

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
    };

    /**
     * Color the faces of the piece based on its position
     * If the piece is on the outer layer, color the corresponding face, else color it black
     *
     * @example
     * const piece = new Piece(1, 1, 1, p);
     * piece.colorFaces();
     */
    colorFaces() : void {
        // Calculate the layer boundaries
        const leftBoundary = -roundToDecimal(this.dimensions / 2 - 0.5, 1);
        const rightBoundary = roundToDecimal(this.dimensions / 2 - 0.5, 1);
        // If the layer is on the outer side, color the face, else color it black

        // UP face
        if (this.y === leftBoundary) {
            this.faces[0] = new Face(vec3.fromValues(0, -1, 0), "#FFFFFF");
        }
        else {
            this.faces[0] = new Face(vec3.fromValues(0, -1, 0), "#000000");
        }

        // DOWN face
        if (this.y === rightBoundary) {
            // Down face
            this.faces[1] = new Face(vec3.fromValues(0, 1, 0), "#FFFF00");
        }
        else {
            this.faces[1] = new Face(vec3.fromValues(0, 1, 0), "#000000");
        }

        // RIGHT face
        if (this.x === rightBoundary) {
            this.faces[3] = new Face(vec3.fromValues(1, 0, 0), "#FF0000");
        }
        else {
            this.faces[3] = new Face(vec3.fromValues(1, 0, 0), "#000000");
        }

        // LEFT face
        if (this.x === leftBoundary) {
            this.faces[2] = new Face(vec3.fromValues(-1, 0, 0), "#FF9000");
        }
        else {
            this.faces[2] = new Face(vec3.fromValues(-1, 0, 0), "#000000");
        }

        // FRONT face
        if (this.z === rightBoundary) {
            this.faces[4] = new Face(vec3.fromValues(0, 0, 1), "#00FF00");
        }
        else {
            this.faces[4] = new Face(vec3.fromValues(0, 0, 1), "#000000");
        }

        // BACK face
        if (this.z === leftBoundary) {
            this.faces[5] = new Face(vec3.fromValues(0, 0, -1), "#0000FF");
        }
        else {
            this.faces[5] = new Face(vec3.fromValues(0, 0, -1), "#000000");
        }
    };

    /**
     * Display the piece
     *
     * @example
     * const piece = new Piece(1, 1, 1, p);
     * piece.show();
     */
    show() : void {
        // Set no fill for the box
        this.p.noFill();
        // Draw outline
        this.p.stroke(0);
        this.p.strokeWeight(2);
        this.p.push();
        // Apply transformation matrix
        this.p.applyMatrix(
            this.matrix[0], this.matrix[1], this.matrix[2], this.matrix[3],
            this.matrix[4], this.matrix[5], this.matrix[6], this.matrix[7],
            this.matrix[8], this.matrix[9], this.matrix[10], this.matrix[11],
            this.matrix[12], this.matrix[13], this.matrix[14], this.matrix[15]
        );
        // Draw the box
        this.p.box(1);
        // Draw faces
        this.faces.forEach(face => face.show(this.p));
        this.p.pop();
    };
}
