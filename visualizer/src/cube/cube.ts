import { Move } from "./move.ts";
import { Piece } from "./piece.ts";
import { Animation } from "./animation.ts";
import { turnX, turnY, turnZ } from "./turn.ts";
import { roundToDecimal } from "../utils/mathUtils.ts";
import type { CubeSettings } from "../utils/cubeSettings.ts";
import { mapColor } from "../utils/colorUtils.ts";

/**
 * Class representing a Rubik's Cube
 *
 * @class Cube
 * @property {CubeSettings} settings - The settings for the cube
 * @property {Piece[]} pieces - The pieces of the cube
 * @property {Animation | null} currentAnimation - The current animation being performed on the cube
 * @property {string[]} moveQueue - Queue of moves to be performed
 * @property {boolean} isPerformingMoves - Flag indicating if the cube is currently performing moves
 */
export class Cube {
    settings: CubeSettings;
    pieces: Piece[];
    currentAnimation: Animation | null = null;
    moveQueue: string[] = [];
    isPerformingMoves: boolean = false;

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

    /**
     * Add moves from an array to the move queue and start performing them
     *
     * @param movesArray - An array of move strings to add to the queue
     *
     * @example
     * cube.addMovesFromArray(["R", "U", "R'", "U'"]);
     */
    addMovesFromArray(movesArray: string[]) : void {
        // Add each move to the move queue
        this.moveQueue.push(...movesArray);
        if (!this.isPerformingMoves) {
            this.applyMoves();
        }
    }

    /**
     * Add moves from a string to the move queue and start performing them
     *
     * @param movesString - A string of moves separated by spaces (e.g., "R U R' U'")
     *
     * @example
     * cube.addMovesFromString("R U R' U'");
     */
    addMovesFromString(movesString: string) : void {
        // Split the moves string into individual move texts
        const moveTexts: string[] = movesString.split(" ");
        this.addMovesFromArray(moveTexts);
    }

    /**
     * Apply the moves in the queue one by one with animation
     *
     * @example
     * cube.applyMoves();
     */
    async applyMoves() : Promise<void> {
        this.isPerformingMoves = true;
        while (this.moveQueue.length > 0) {
            // Get the next move from the queue
            const nextMove = this.moveQueue.shift()!;
            // Perform the turn
            this.turn(nextMove);
            // Wait until the current animation is finished
            await new Promise<void>((resolve) => {
                const checkAnimation = () => {
                    if (!this.currentAnimation) {
                        resolve();
                    } else {
                        requestAnimationFrame(checkAnimation);
                    }
                };
                checkAnimation();
            });
            // Optional delay between moves
            if (this.settings.moveDelay > 0) {
                await new Promise((resolve) => setTimeout(resolve, this.settings.moveDelay));
            }
        }
        this.isPerformingMoves = false;
    }

    /**
     * Get the sticker index for a piece based on its row and column
     * Calculates the index in a flattened array of stickers for a given piece position
     * based on the cube size and axis starting points.
     *
     * @param cubeSize - The size of the cube (number of stickers per side)
     * @param pieceRow - The row position of the piece
     * @param pieceCol - The column position of the piece
     * @param rowAxisStartingPoint - The starting point of the row axis (leftBoundary or rightBoundary)
     * @param colAxisStartingPoint - The starting point of the column axis (leftBoundary or rightBoundary)
     * @returns The index of the sticker in the flattened array
     */
    getStickerIndex(cubeSize: number, pieceRow: number, pieceCol: number, rowAxisStartingPoint: number, colAxisStartingPoint: number) : number {
        // Determine grid coordinate range
        const minCoordinate: number = -(cubeSize - 1) / 2;

        // Convert coordinates to zero-based indexes
        const pieceRowIndex: number = pieceRow - minCoordinate;
        const pieceColIndex: number = pieceCol - minCoordinate;

        // Determine direction multipliers based on axis starting points
        const rowDirection: number = -rowAxisStartingPoint;
        const colDirection: number = -colAxisStartingPoint;

        // Calculate row and column indexes
        const gridRowIndex: number = rowDirection === 1 ? pieceRowIndex : cubeSize - 1 - pieceRowIndex;
        const gridColIndex: number = colDirection === 1 ? pieceColIndex : cubeSize - 1 - pieceColIndex;

        // Calculate and return the sticker index
        return gridRowIndex * cubeSize + gridColIndex;
    }

    /**
     * Set up a side of the cube with the given stickers
     * For each piece on the specified boundary of the given axis, set the face color based on the stickers array.
     *
     * UP/DOWN - axis: 'y', rowAxis: 'z', colAxis: 'x'
     * LEFT/RIGHT - axis: 'x', rowAxis: 'y', colAxis: 'z'
     * FRONT/BACK - axis: 'z', rowAxis: 'y', colAxis: 'x'
     *
     * @param cubeSize - The size of the cube (number of stickers per side)
     * @param stickers - An array of sticker colors for the side
     * @param axis - The axis of the side ('x', 'y', or 'z')
     * @param axisBoundary - The boundary value for the axis (e.g., leftBoundary or rightBoundary)
     * @param otherAxesStartingPoints - A map of starting points for the other two axes
     * @param faceIndex - The index of the face to set (0: UP, 1: DOWN, 2: LEFT, 3: RIGHT, 4: FRONT, 5: BACK)
     */
    setUpSide(cubeSize: number, stickers: string[], axis: string, axisBoundary: number, otherAxesStartingPoints: Map<string, number>, faceIndex: number) : void {
        if (stickers.length !== cubeSize * cubeSize) {
            throw new Error(`Invalid number of stickers for side. Expected ${cubeSize * cubeSize}, got ${stickers.length}.`);
        }

        this.pieces.forEach(piece => {
            let pieceRow: number | undefined = undefined;
            let pieceCol: number | undefined = undefined;
            let rowStartingPoint: number | undefined = undefined;
            let colStartingPoint: number | undefined = undefined;
            let pieceOnBoundary: boolean = false;

            switch (axis) {
                case 'x':
                    if (piece.x === axisBoundary) {
                        pieceOnBoundary = true;
                        // Calculate the piece row and column
                        pieceRow = piece.y;
                        pieceCol = piece.z;
                        // Determine starting points for row and column axes
                        rowStartingPoint = otherAxesStartingPoints.get('y')!;
                        colStartingPoint = otherAxesStartingPoints.get('z')!;
                    }
                    break;
                case 'y':
                    if (piece.y === axisBoundary) {
                        pieceOnBoundary = true;
                        // Calculate the piece row and column
                        pieceRow = piece.z;
                        pieceCol = piece.x;
                        // Determine starting points for row and column axes
                        rowStartingPoint = otherAxesStartingPoints.get('z')!;
                        colStartingPoint = otherAxesStartingPoints.get('x')!;
                    }
                    break;
                case 'z':
                    if (piece.z === axisBoundary) {
                        pieceOnBoundary = true;
                        // Calculate the piece row and column
                        pieceRow = piece.y;
                        pieceCol = piece.x;
                        // Determine starting points for row and column axes
                        rowStartingPoint = otherAxesStartingPoints.get('y')!;
                        colStartingPoint = otherAxesStartingPoints.get('x')!;
                    }
                    break;
            }

            // Set the face color only if the piece is on the boundary
            if (pieceOnBoundary) {
                // Get the sticker index for this piece
                const stickerIndex = this.getStickerIndex(
                    cubeSize, pieceRow!, pieceCol!, rowStartingPoint!, colStartingPoint!
                );
                // Map and set the face color
                piece.faces[faceIndex].color = mapColor(stickers[stickerIndex], this.settings);
            }
        });
    }

    /**
     * Set up the cube from a map of sides
     *
     * @param sides - A map where keys are side names ('UP', 'DOWN', 'LEFT', 'RIGHT', 'FRONT', 'BACK')
     * and values are arrays of sticker colors
     * @example
     * const sides = new Map<string, string[]>();
     * sides.set('UP', ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W']);
     * sides.set('DOWN', ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y']);
     * sides.set('LEFT', ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']);
     * sides.set('RIGHT', ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R']);
     * sides.set('FRONT', ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G']);
     * sides.set('BACK', ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B']);
     * cube.setUpFromState(sides);
     */
    setUpFromState(sides: Map<string, string[]>) : void {
        if (!sides || sides.size !== 6) {
            throw new Error("setUpFromState requires a map of 6 sides.");
        }

        // Get cube dimensions and boundaries
        const cubeSize: number = this.settings.cubeDimensions;
        const leftBoundary: number = -roundToDecimal(this.settings.cubeDimensions / 2 - 0.5, 1);
        const rightBoundary: number = roundToDecimal(this.settings.cubeDimensions / 2 - 0.5, 1);

        // UP face (y = leftBoundary, z = row, x = col, rowStartingPoint = -1, colStartingPoint = -1)
        this.setUpSide(cubeSize, sides.get('UP')!, 'y', leftBoundary, new Map([['z', -1], ['x', -1]]), 0);
        // DOWN face (y = rightBoundary, z = row, x = col, rowStartingPoint = 1, colStartingPoint = -1)
        this.setUpSide(cubeSize, sides.get('DOWN')!, 'y', rightBoundary, new Map([['z', 1], ['x', -1]]), 1);
        // LEFT face (x = leftBoundary, y = row, z = col, rowStartingPoint = -1, colStartingPoint = -1)
        this.setUpSide(cubeSize, sides.get('LEFT')!, 'x', leftBoundary, new Map([['y', -1], ['z', -1]]), 2);
        // RIGHT face (x = rightBoundary, y = row, z = col, rowStartingPoint = -1, colStartingPoint = 1)
        this.setUpSide(cubeSize, sides.get('RIGHT')!, 'x', rightBoundary, new Map([['y', -1], ['z', 1]]), 3);
        // FRONT face (z = rightBoundary, y = row, x = col, rowStartingPoint = -1, colStartingPoint = -1)
        this.setUpSide(cubeSize, sides.get('FRONT')!, 'z', rightBoundary, new Map([['y', -1], ['x', -1]]), 4);
        // BACK face (z = leftBoundary, y = row, x = col, rowStartingPoint = -1, colStartingPoint = 1)
        this.setUpSide(cubeSize, sides.get('BACK')!, 'z', leftBoundary, new Map([['y', -1], ['x', 1]]), 5);
    }
}
