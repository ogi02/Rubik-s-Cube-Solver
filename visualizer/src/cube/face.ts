import { vec3 } from "gl-matrix";
import type p5 from "p5";

/**
 * Class representing a face of a Rubik's Cube piece
 *
 * @class Face
 * @property {vec3} vector - The normal vector of the face
 * @property {string} color - The color of the face
 *
 * @example
 * const face = new Face([1, 0, 0], 'red');
 * face.show(p);
 */
export class Face {
    vector: vec3;
    color: string;

    /**
     * Constructor for the Face class
     * @param vector - The normal vector of the face
     * @param color - The color of the face
     *
     * @example
     * const face = new Face([1, 0, 0], 'red');
     * face.show(p);
     */
    constructor(vector: vec3, color: string) {
        this.vector = vector;
        this.color = color;
    }

    /**
     * Apply rotation based on the face normal vector
     * @param p - The p5 instance
     *
     * @example
     * face.applyRotation(p);
     */
    applyRotation(p: p5) : void {
        // Apply rotation based on the face normal vector
        if (Math.abs(this.vector[0]) > 0) {
            p.rotateY(p.HALF_PI);
        } else if (Math.abs(this.vector[1]) > 0) {
            p.rotateX(p.HALF_PI);
        }
    };

    /**
     * Display the face
     * @param p - The p5 instance
     *
     * @example
     * face.show(p);
     */
    show(p: p5) : void {
        // Set the color
        p.fill(this.color);
        // No stroke
        p.noStroke();
        // Draw the face as a rectangle
        p.rectMode(p.CENTER);
        p.push();
        // Translate to the face position
        p.translate(0.5 * this.vector[0], 0.5 * this.vector[1], 0.5 * this.vector[2]);
        // Apply rotation
        this.applyRotation(p);
        // Draw the face
        p.square(0, 0, 1);
        p.pop();
    };
}
