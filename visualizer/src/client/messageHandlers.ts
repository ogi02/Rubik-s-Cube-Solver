import p5 from "p5";
import { Cube } from "../cube/cube.ts";
import { type CubeSettings, loadCubeSettings } from "../utils/cubeSettings.ts";

/**
 * Handle incoming cube state message to set up the cube.
 *
 * @param data - Incoming message data
 * @param p - p5 instance
 * @return - Updated Cube instance
 * @throws {Error} - If the message is invalid or state format is incorrect
 *
 * @example
 * handleCubeStateMessage(data, p, cube);
 */
export const handleCubeStateMessage = (data: any, p: p5) : Cube => {
    // Validate
    if (!data.data || data.data.dimensions === undefined || !data.data.state) {
        console.error("Invalid cube_state message: missing required fields", data);
        throw new Error("Invalid cube_state message: missing required fields");
    }

    // Initialize cube with given dimensions
    const settings : CubeSettings = loadCubeSettings(data.data.dimentions, p);
    const cube : Cube = new Cube(settings);

    // Validate the state
    const expectedSides : string[] = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'FRONT', 'BACK'];
    const state : object = data.data.state;
    if (
        // State must be an object with exactly 6 sides
        state === null ||
        typeof state !== 'object' ||
        Object.keys(state).length !== 6 ||
        // Each side must be one of the expected sides and an array of strings
        !Object.entries(state).every(([side, stickers]: [string, unknown]) : boolean =>
            expectedSides.includes(side) && Array.isArray(stickers) && stickers.every(s => typeof s === 'string')
        )
    ) {
        console.error("Invalid cube_state: state must be an object with exactly 6 sides ('UP', 'DOWN', 'LEFT', 'RIGHT', 'FRONT', 'BACK'), each an array of strings.", state);
        throw new Error("Invalid cube_state message: invalid state format");
    }

    // Apply the state to the cube
    const sides = new Map<string, Array<string>>(Object.entries(state));
    cube.setUpFromState(sides);

    return cube;
};

/**
 * Handle incoming apply moves message to apply moves to the cube.
 *
 * @param data - Incoming message data
 * @param cube - Cube instance to apply moves to
 *
 * @example
 * handleApplyMovesMessage(data);
 */
export const handleApplyMovesMessage = (data: any, cube: Cube) : void => {
    // Validate
    if (!data.data || !data.data.moves) {
        console.error("Invalid cube_state message: missing required fields", data);
        throw new Error("Invalid cube_state message: missing required fields");
    }

    // Validate the moves
    const moves : string[] = data.data.moves;
    if (!Array.isArray(moves)) {
        console.error("Invalid apply_moves: moves must be an array of strings.", moves);
        throw new Error("Invalid apply_moves message: invalid moves format");
    }

    // Apply the moves to the cube
    cube.addMovesFromArray(moves);
};
