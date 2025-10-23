import type p5 from "p5";

import { Move } from "./move";
import { Piece } from "./piece";
import { Animation } from "./animation.ts";
import { turnX, turnY, turnZ } from "./turn";
import { roundToDecimal } from "../utils/math";

/**
 * Class representing a Rubik's Cube
 *
 * @class Cube
 * @property {number} dimensions - The dimensions of the cube (e.g., 3 for a 3x3 cube)
 * @property {number} speed - The speed of the cube's animations
 * @property {Piece[]} pieces - The pieces of the cube
 * @property {p5} p - The p5 instance
 * @property {Animation | null} currentAnimation - The current animation being performed on the cube
 */
export class Cube {
    dimensions: number;
    speed: number;
    pieces: Piece[];
    p: p5;
    currentAnimation: Animation | null = null;

    /**
     * Constructor for the Cube class
     *
     * @param dimensions - The dimensions of the cube (e.g., 3 for a 3x3 cube)
     * @param speed - The speed of the cube's animations
     * @param p - The p5 instance
     */
    constructor(dimensions: number, speed: number, p: p5) {
        // Dimensions of the cube
        this.dimensions = dimensions;
        // Speed of the cube's animations
        this.speed = speed;
        // Pieces of the cube
        this.pieces = [];
        // p5 instance
        this.p = p;

        // Define left and right boundaries for the pieces
        const leftBoundary = -roundToDecimal(this.dimensions / 2 - 0.5, 1);
        const rightBoundary = roundToDecimal(this.dimensions / 2 - 0.5, 1);
        // Create pieces for the cube
        for (let x = leftBoundary; x <= rightBoundary; x++) {
            for (let y = leftBoundary; y <= rightBoundary; y++) {
                for (let z = leftBoundary; z <= rightBoundary; z++) {
                    this.pieces.push(new Piece(x, y, z, this.dimensions, this.p));
                }
            }
        }
    };

    /**
     * Display the cube by showing all its pieces
     *
     * @method show
     * @returns {void}
     */
    show() : void {
        // Set no fill for the box
        this.p.noFill();
        // Set outline
        this.p.stroke(0);
        this.p.strokeWeight(2);
        // Update the animation if it exists and complete the turn if finished
        if (this.currentAnimation) {
            this.currentAnimation.update();
            this.completeTurn();
        }
        // Draw the pieces
        this.pieces.forEach(piece => {
            this.p.push();
            // Animate the piece if it has an ongoing animation
            this.animate(piece);
            // Show the piece
            piece.show();
            this.p.pop();
        });
    };

    /**
     * Animate a piece based on the current animation
     *
     * @param piece - The piece to animate
     *
     * @example
     * cube.animate(piece);
     */
    animate(piece: Piece) : void {
        // Animate the current animation if it exists
        if (this.currentAnimation) {
            switch (this.currentAnimation.move.getAxis()) {
                case 'x':
                    // Rotate around X axis if the piece is in the moving layer
                    if (this.currentAnimation.move.getLayerIndexes(this.dimensions).includes(piece.x)) {
                        this.p.rotateX(this.currentAnimation.angle);
                    }
                    break;
                case 'y':
                    // Rotate around Y axis if the piece is in the moving layer
                    if (this.currentAnimation.move.getLayerIndexes(this.dimensions).includes(piece.y)) {
                        this.p.rotateY(this.currentAnimation.angle);
                    }
                    break;
                case 'z':
                    // Rotate around Z axis if the piece is in the moving layer
                    if (this.currentAnimation.move.getLayerIndexes(this.dimensions).includes(piece.z)) {
                        this.p.rotateZ(this.currentAnimation.angle);
                    }
                    break;
                default:
                    throw new Error(`Invalid axis: ${this.currentAnimation.move.getAxis()}`);
            }
        }
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
        // Animate the turn
        this.currentAnimation = new Animation(move, this.speed);
        this.currentAnimation.start();
    };

    /**
     * Apply a sequence of moves to the cube
     *
     * @param movesString - The string of moves to apply (e.g., "R U R' U'")
     *
     * @example
     * cube.applyMoves("R U R' U'");
     */
    applyMoves(movesString: string) : void {
        // Split the moves string into individual move texts
        const moveTexts: string[] = movesString.split(" ");

        // Apply each move sequentially
        const timeoutInterval = 4000 / this.speed;
        for (let i = 0; i < moveTexts.length; i++) {
            setTimeout(() => this.turn(moveTexts[i]), i * timeoutInterval);
        }
    }

    /**
     * Complete the current turn if the animation is finished
     *
     * @example
     * cube.completeTurn();
     */
    completeTurn() : void {
        if (this.currentAnimation && this.currentAnimation.isFinished()) {
            // Get the move details
            const axis = this.currentAnimation.move.getAxis();
            const angle = this.currentAnimation.move.getAngle();
            const layerIndexes = this.currentAnimation.move.getLayerIndexes(this.dimensions);
            // Perform the turn immediately after the animation
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
            // Clear the current animation
            this.currentAnimation = null;
        }
    }
}
