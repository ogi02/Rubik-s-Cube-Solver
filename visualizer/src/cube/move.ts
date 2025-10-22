import {roundToDecimal} from "../utils/math";

/**
 * Class representing a single move on a Rubik's Cube.
 *
 * Parses move notation and provides methods to get the axis, angle,
 * and layer indexes for the move.
 * Examples of move notation: R, R', R2, Rw, Rw', 3Rw2, 2Uw', etc.
 *
 * @class Move
 * @property {string | null} layer - The face of the cube being turned (R, L, U, D, F, B).
 * @property {string} direction - The direction of the turn ('', "'", '2').
 * @property {number} layerAmount - The number of layers to turn.
 *
 * @example
 * const move = new Move("R'");
 * console.log(move.getTurn(3));
 * // Output: { axis: 'x', angle: -1.5707963267948966, layerIndexes: [1] }
 *
 * const move = new Move("Uw");
 * console.log(move.getTurn(5));
 * // Output: { axis: 'y', angle: 1.5707963267948966, layerIndexes: [-2, -1] }
 */
export class Move {
    layer: string | null;
    direction: string | null;
    layerAmount: number;

    /**
     * Creates an instance of Move.
     *
     * @param moveText - The text representation of the move.
     */
    constructor(moveText: string) {
        // Parse the move text into layer, direction, and layerAmount
        const moveInfo = this.parse(moveText)[0];
        // Initialize properties
        this.layer = moveInfo.layer;
        this.direction = moveInfo.direction;
        this.layerAmount = moveInfo.layerAmount;
    };

    /**
     * Parse the move text into its components.
     *
     * @param fromText - The move text to parse.
     * @returns An array of parsed move components.
     *
     * @example
     * const move = new Move("3Rw2");
     * console.log(move.parse("3Rw2"));
     * // Output: [{ layer: 'R', direction: '2', layerAmount: 3 }]
     *
     * const move = new Move("U'");
     * console.log(move.parse("U'"));
     * // Output: [{ layer: 'U', direction: "'", layerAmount: 1 }]
     */
    parse(fromText: string) : {
        layer: string | null;
        direction: string | null;
        layerAmount: number;
    }[] {
        // Match examples: R, R', R2, Rw, Rw', 3Rw2, 2Uw', etc.
        const tokens = fromText.match(/\d*[RLUDFB]w?[2']?/g);

        if (!tokens) {
            return [{
                layer: null,
                direction: null,
                layerAmount: 0
            }];
        }

        return tokens.map(token => {
            // Extract layer count (if any)
            const layerAmountMatch = token.match(/^\d*/);
            let layerAmount = layerAmountMatch ? parseInt(layerAmountMatch[0], 10) : null;

            // Extract face (R, L, etc.)
            const layerMatch = token.match(/[RLUDFB]/);
            const layer = layerMatch ? layerMatch[0] : null;

            // Check for wide move (contains "w")
            const isWide = token.includes('w');
            if (!(layerAmount)) {
                if (isWide) {
                    layerAmount = 2; // Default to 2 layers for wide moves
                } else {
                    layerAmount = 1; // Default to 1 layer for normal moves
                }
            }

            // Extract direction (last char if "2" or "'")
            const directionMatch = token.match(/([2'])$/);
            const direction = directionMatch ? directionMatch[1] : "";

            return {
                layer: layer,
                direction: direction,
                layerAmount: layerAmount
            };
        });
    };

    /**
     * Get the axis of rotation for the move.
     *
     * @returns The axis of rotation ('x', 'y', or 'z').
     * @throws Error - Will throw an error if the layer is invalid.
     *
     * @example
     * const move = new Move("R");
     * console.log(move.getAxis());
     * // Output: 'x'
     *
     * const move = new Move("U'");
     * console.log(move.getAxis());
     * // Output: 'y'
     */
    getAxis() : string {
        switch (this.layer) {
            case 'U':
            case 'D':
                return "y";
            case 'F':
            case 'B':
                return "z";
            case 'L':
            case 'R':
                return "x";
            default:
                throw new Error(`Invalid layer: ${this.layer}`);
        }
    };

    /**
     * Get the angle of rotation for the move.
     *
     * @returns The angle of rotation in radians.
     * @throws Error - Will throw an error if the direction is invalid.
     *
     * @example
     * const move = new Move("R");
     * console.log(move.getAngle());
     * // Output: 1.5707963267948966 (90 degrees clockwise)
     *
     * const move = new Move("U'");
     * console.log(move.getAngle());
     * // Output: -1.5707963267948966 (90 degrees counter-clockwise)
     *
     * const move = new Move("L2");
     * console.log(move.getAngle());
     * // Output: 3.141592653589793 (180 degrees)
     */
    getAngle() : number {
        switch (this.direction) {
            case '':
                // Default 90 degrees clockwise
                // D, B, L are reversed
                if (['D', 'B', 'L'].includes(this.layer!)) {
                    return -Math.PI / 2;
                }
                return Math.PI / 2;
            case '\'':
                // 90 degrees counter-clockwise
                // D, B, L are reversed
                if (['D', 'B', 'L'].includes(this.layer!)) {
                    return Math.PI / 2;
                }
                return -Math.PI / 2;
            case '2':
                // 180 degrees
                return Math.PI;
            default:
                throw new Error(`Invalid direction: ${this.direction}`);
        }
    };

    /**
     * Get the indexes of the layers to be turned based on the cube dimension.
     *
     * @param dim - The dimension of the cube (e.g., 3 for a 3x3 cube).
     * @returns An array of layer indexes to be turned.
     * @throws Error - Will throw an error if the layer amount exceeds half the cube dimension.
     *
     * @example
     * const move = new Move("R");
     * console.log(move.getLayerIndexes(3));
     * // Output: [1]
     *
     * const move = new Move("Uw");
     * console.log(move.getLayerIndexes(5));
     * // Output: [-2, -1]
     */
    getLayerIndexes(dim: number) : number[] {
        // Ensure layerAmount does not exceed half the cube dimension
        if (Math.floor(dim / 2) < this.layerAmount) {
            throw new Error(`Layer amount ${this.layerAmount} exceeds 1/2 cube dimension ${dim}`);
        }

        let indexes: number[] = [];
        // Define left and right boundaries of the cube
        const leftBoundary = -roundToDecimal(dim / 2 - 0.5, 1);
        const rightBoundary = roundToDecimal(dim / 2 - 0.5, 1);
        // Determine indexes based on the layer being turned
        switch (this.layer) {
            case 'D':
            case 'F':
            case 'R':
                for (let i = rightBoundary; i > rightBoundary - this.layerAmount; i--) {
                    indexes.push(i);
                }
                return indexes;
            case 'U':
            case 'B':
            case 'L':
                for (let i = leftBoundary; i < leftBoundary + this.layerAmount; i++) {
                    indexes.push(i);
                }
                return indexes;
            default:
                throw new Error(`Invalid layer: ${this.layer}`);
        }
    };

    /**
     * Get the complete turn information for the move.
     *
     * @param dim - The dimension of the cube (e.g., 3 for a 3x3 cube).
     * @returns An object containing the axis, angle, and layer indexes for the turn.
     *
     * @example
     * const move = new Move("R'");
     * console.log(move.getTurn(3));
     * // Output: { axis: 'x', angle: -1.5707963267948966, layerIndexes: [1] }
     *
     * const move = new Move("Uw");
     * console.log(move.getTurn(5));
     * // Output: { axis: 'y', angle: 1.5707963267948966, layerIndexes: [-2, -1] }
     */
    getTurn(dim: number) : {
        axis: string;
        angle: number;
        layerIndexes: number[];
    } {
        return {
            axis: this.getAxis(),
            angle: this.getAngle(),
            layerIndexes: this.getLayerIndexes(dim)
        };
    };
}
