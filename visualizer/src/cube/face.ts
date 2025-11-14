import type p5 from "p5";
import { vec3 } from "gl-matrix";

import { roundToDecimal } from "../utils/mathUtils.ts";
import type { CubeSettings } from "../utils/cubeSettings.ts";

/**
 * Class representing a face of a Rubik's Cube piece
 *
 * @class Face
 * @property {vec3} vector - The normal vector of the face
 * @property {string} color - The color of the face
 *
 * @example
 * const face = new Face([1, 0, 0], 'red');
 * face.show(settings);
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
     * face.show(settings);
     */
    constructor(vector: vec3, color: string) {
        this.vector = vector;
        this.color = color;
    }

    /**
     * Apply rotation based on the face normal vector
     * @param p5Instance - The p5 instance
     *
     * @example
     * face.applyRotation(p);
     */
    applyRotation(p5Instance: p5) : void {
        // Apply rotation based on the face normal vector
        if (Math.abs(this.vector[0]) > 0) {
            p5Instance.rotateY(p5Instance.HALF_PI);
        } else if (Math.abs(this.vector[1]) > 0) {
            p5Instance.rotateX(p5Instance.HALF_PI);
        }
    };

    /**
     * Turn the face around the X axis
     *
     * @param angle - The angle to turn (in radians)
     *
     * @example
     * face.turnX(Math.PI / 2);
     */
    turnX(angle: number) : void {
        // Rotate the face vector around the X axis
        const newY = roundToDecimal(this.vector[1] * Math.cos(angle) - this.vector[2] * Math.sin(angle), 1);
        const newZ = roundToDecimal(this.vector[1] * Math.sin(angle) + this.vector[2] * Math.cos(angle), 1);
        this.vector = vec3.fromValues(this.vector[0], newY, newZ);
    }

    /**
     * Turn the face around the Y axis
     *
     * @param angle - The angle to turn (in radians)
     *
     * @example
     * face.turnY(Math.PI / 2);
     */
    turnY(angle: number) : void {
        // Rotate the face vector around the Y axis
        const newX = roundToDecimal(this.vector[0] * Math.cos(angle) + this.vector[2] * Math.sin(angle), 1);
        const newZ = roundToDecimal(-this.vector[0] * Math.sin(angle) + this.vector[2] * Math.cos(angle), 1);
        this.vector = vec3.fromValues(newX, this.vector[1], newZ);
    }

    /**
     * Turn the face around the Z axis
     *
     * @param angle - The angle to turn (in radians)
     *
     * @example
     * face.turnZ(Math.PI / 2);
     */
    turnZ(angle: number) : void {
        // Rotate the face vector around the Z axis
        const newX = roundToDecimal(this.vector[0] * Math.cos(angle) - this.vector[1] * Math.sin(angle), 1);
        const newY = roundToDecimal(this.vector[0] * Math.sin(angle) + this.vector[1] * Math.cos(angle), 1);
        this.vector = vec3.fromValues(newX, newY, this.vector[2]);
    }

    /**
     * Display the face
     * @param settings - The cube settings
     *
     * @example
     * face.show(settings);
     */
    show(settings: CubeSettings) : void {
        // Skip black faces
        if (!settings.drawBlackFaces && this.color === settings.colorBlack) {
            return;
        }
        // Set the color
        settings.p5Instance.fill(this.color);
        settings.p5Instance.push();
        // Translate to the face position
        settings.p5Instance.translate(0.5 * this.vector[0], 0.5 * this.vector[1], 0.5 * this.vector[2]);
        // Apply rotation
        this.applyRotation(settings.p5Instance);
        // Draw the face
        settings.p5Instance.square(0, 0, 1);
        settings.p5Instance.pop();
    };
}
