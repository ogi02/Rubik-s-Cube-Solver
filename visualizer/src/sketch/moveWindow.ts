/**
 * Number of move slots shown at once by the message box
 */
export const MOVE_WINDOW_SIZE = 11;

/**
 * Index of the slot holding the move currently being executed
 */
export const MOVE_WINDOW_CENTRE = Math.floor(MOVE_WINDOW_SIZE / 2);

/**
 * Take the fixed-size slice of a batch of moves that surrounds the move being executed
 *
 * The slice always has MOVE_WINDOW_SIZE entries and the executing move always sits at
 * MOVE_WINDOW_CENTRE, so the highlight never moves and the moves scroll underneath it. Slots that
 * fall before the start or after the end of the batch are null, which the caller renders as blanks.
 *
 * @param moves - Every move of the batch being applied
 * @param index - Index within that batch of the move being executed
 * @returns The window of moves, with null for each slot outside the batch
 *
 * @example
 * moveWindow(["R", "U", "R'"], 0);
 * // [null, null, null, null, null, "R", "U", "R'", null, null, null]
 */
export const moveWindow = (moves: string[], index: number): (string | null)[] => {
    const window: (string | null)[] = [];
    for (let slot = 0; slot < MOVE_WINDOW_SIZE; slot++) {
        const position = index + slot - MOVE_WINDOW_CENTRE;
        window.push(position >= 0 && position < moves.length ? moves[position] : null);
    }
    return window;
};
