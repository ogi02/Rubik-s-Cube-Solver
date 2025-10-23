import { mat4, vec3, type mat4 as Mat4Type } from "gl-matrix";
import type p5 from "p5";
import { Face } from "./face";
import {roundToDecimal} from "../utils/math";

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
 * @property {number} leftBoundary - The left boundary of the cube layer
 * @property {number} rightBoundary - The right boundary of the cube layer
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
    leftBoundary: number;
    rightBoundary: number;
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
        // Calculate the layer boundaries
        this.leftBoundary = -roundToDecimal(this.dimensions / 2 - 0.5, 1);
        this.rightBoundary = roundToDecimal(this.dimensions / 2 - 0.5, 1);
        // Create initial faces
        this.faces = [
            new Face(vec3.fromValues(0,-1,0), "#000000"), // UP
            new Face(vec3.fromValues(0,1,0), "#000000"),  // DOWN
            new Face(vec3.fromValues(-1,0,0), "#000000"), // LEFT
            new Face(vec3.fromValues(1,0,0), "#000000"),  // RIGHT
            new Face(vec3.fromValues(0,0,1), "#000000"),  // FRONT
            new Face(vec3.fromValues(0,0,-1), "#000000"), // BACK
        ];
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
        // Define face configs
        const faceConfigs = [
            // index, axis, boundary, color
            { index: 0, axis: 'y', boundary: this.leftBoundary, color: "#FFFFFF" }, // UP
            { index: 1, axis: 'y', boundary: this.rightBoundary, color: "#FFFF00" }, // DOWN
            { index: 2, axis: 'x', boundary: this.leftBoundary, color: "#FF9000" }, // LEFT
            { index: 3, axis: 'x', boundary: this.rightBoundary, color: "#FF0000" }, // RIGHT
            { index: 4, axis: 'z', boundary: this.rightBoundary, color: "#00FF00" }, // FRONT
            { index: 5, axis: 'z', boundary: this.leftBoundary, color: "#0000FF" }  // BACK
        ];

        // Draw faces based on configs
        faceConfigs.forEach(config => {
            // Check if the piece is on the boundary for the given axis
            let isOnBoundary = false;
            switch (config.axis) {
                case 'x':
                    isOnBoundary = (this.x === config.boundary);
                    break;
                case 'y':
                    isOnBoundary = (this.y === config.boundary);
                    break;
                case 'z':
                    isOnBoundary = (this.z === config.boundary);
                    break;
            }
            // If on boundary, color the face, else color it black
            this.faces[config.index].color = isOnBoundary ? config.color : "#000000";
        });
    };

    /**
     * Display the piece
     *
     * @example
     * const piece = new Piece(1, 1, 1, p);
     * piece.show();
     */
    show() : void {
        // Don't draw inner pieces
        if (
            this.x > this.leftBoundary && this.x < this.rightBoundary &&
            this.y > this.leftBoundary && this.y < this.rightBoundary &&
            this.z > this.leftBoundary && this.z < this.rightBoundary
        ) {
            return;
        }

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
        this.p.noStroke();
        this.p.rectMode(this.p.CENTER);
        this.faces.forEach(face => face.show(this.p));
        this.p.pop();
    };
}
