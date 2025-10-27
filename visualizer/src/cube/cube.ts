import { Move } from "./move";
import { Piece } from "./piece";
import { Animation } from "./animation";
import { turnX, turnY, turnZ } from "./turn";
import { roundToDecimal } from "../utils/math";
import type { CubeSettings } from "../utils/cubeSettings.ts";

/**
 * Class representing a Rubik's Cube
 *
 * @class Cube
 * @property {CubeSettings} settings - The settings for the cube
 * @property {Piece[]} pieces - The pieces of the cube
 * @property {Animation | null} currentAnimation - The current animation being performed on the cube
 */
export class Cube {
    settings: CubeSettings;
    pieces: Piece[];
    currentAnimation: Animation | null = null;

    /**
     * Constructor for the Cube class
     *
     * @param settings
     *
     * @example
     * const cube = new Cube(cubeSettings);
     * cube.show();
     */
    constructor(settings: CubeSettings) {
        // Store settings
        this.settings = settings;
        // Pieces of the cube
        this.pieces = [];

        // Define left and right boundaries for the pieces
        const leftBoundary = -roundToDecimal(this.settings.cubeDimensions / 2 - 0.5, 1);
        const rightBoundary = roundToDecimal(this.settings.cubeDimensions / 2 - 0.5, 1);
        // Create pieces for the cube
        for (let x = leftBoundary; x <= rightBoundary; x++) {
            for (let y = leftBoundary; y <= rightBoundary; y++) {
                for (let z = leftBoundary; z <= rightBoundary; z++) {
                    this.pieces.push(new Piece(x, y, z, this.settings));
                }
            }
        }
    };

    /**
     * Display the cube by showing all its pieces
     *
     * @method show
     * @returns {void}
     *
     * @example
     * const cube = new Cube(cubeSettings);
     * cube.show();
     */
    show() : void {
        // Set no fill for the box
        this.settings.p5Instance.noFill();
        // Set no outline for the box
        this.settings.p5Instance.noStroke()
        // Update the animation if it exists and complete the turn if finished
        if (this.currentAnimation) {
            this.currentAnimation.update();
            this.completeTurn();
        }
        // Draw the pieces
        this.pieces.forEach(piece => {
            this.settings.p5Instance.push();
            // Animate the piece if it has an ongoing animation
            this.animate(piece);
            // Show the piece
            piece.show();
            this.settings.p5Instance.pop();
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
                    if (this.currentAnimation.move.getLayerIndexes(this.settings.cubeDimensions).includes(piece.x)) {
                        this.settings.p5Instance.rotateX(this.currentAnimation.angle);
                    }
                    break;
                case 'y':
                    // Rotate around Y axis if the piece is in the moving layer
                    if (this.currentAnimation.move.getLayerIndexes(this.settings.cubeDimensions).includes(piece.y)) {
                        this.settings.p5Instance.rotateY(this.currentAnimation.angle);
                    }
                    break;
                case 'z':
                    // Rotate around Z axis if the piece is in the moving layer
                    if (this.currentAnimation.move.getLayerIndexes(this.settings.cubeDimensions).includes(piece.z)) {
                        this.settings.p5Instance.rotateZ(this.currentAnimation.angle);
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
     *
     * @example
     * cube.turn("R");
     */
    turn(moveText: string) : void {
        // Parse the move
        const move = new Move(moveText);
        // Animate the turn
        this.currentAnimation = new Animation(move, this.settings.animationSpeed);
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
        const timeoutInterval = 5000 / this.settings.animationSpeed;
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
            const layerIndexes = this.currentAnimation.move.getLayerIndexes(this.settings.cubeDimensions);
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
