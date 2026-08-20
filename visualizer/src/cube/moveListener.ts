/**
 * Listener notified as a cube works through a batch of moves
 *
 * Implemented by anything that needs to follow the progress of a batch, such as the on-screen
 * message box. The cube owns the batch and reports its position in it; the listener only renders.
 *
 * @interface MoveListener
 *
 * @example
 * class Logger implements MoveListener {
 *     onMoveStarted(moves: string[], index: number): void {
 *         console.log(`${index + 1}/${moves.length}: ${moves[index]}`);
 *     }
 *     onMovesCompleted(): void {
 *         console.log("done");
 *     }
 * }
 * cube.setMoveListener(new Logger());
 */
export interface MoveListener {
    /**
     * Called just before the animation of a move begins
     *
     * @param moves - Every move of the batch currently being applied
     * @param index - Index within that batch of the move that is starting
     * @returns {void}
     */
    onMoveStarted(moves: string[], index: number): void;

    /**
     * Called once the last move of the batch has finished animating
     *
     * @returns {void}
     */
    onMovesCompleted(): void;
}
