import type { MoveListener } from "../cube/moveListener.ts";
import { MOVE_WINDOW_CENTRE, moveWindow } from "./moveWindow.ts";

/**
 * How long the cube state message stays on screen, in milliseconds
 */
export const CUBE_STATE_MESSAGE_DURATION = 3000;

/**
 * On-screen message box overlaying the sketch
 *
 * Shows one thing at a time. A received cube state is announced for CUBE_STATE_MESSAGE_DURATION
 * and then fades out; a batch of moves takes the box over for as long as it is being applied,
 * cancelling any pending fade, and hides it again once the last move has finished.
 *
 * @class MessageBox
 * @implements MoveListener
 * @property {HTMLElement} element - The element the box is rendered into
 * @property {number | null} hideTimeout - Handle of the pending fade-out, if one is scheduled
 *
 * @example
 * const messageBox = new MessageBox(document.getElementById("message-box") as HTMLElement);
 * messageBox.showCubeState(3);
 * cube.setMoveListener(messageBox);
 */
export class MessageBox implements MoveListener {
    private element: HTMLElement;
    private hideTimeout: number | null = null;

    /**
     * Constructor for the MessageBox class
     *
     * @param element - The element the box is rendered into
     *
     * @example
     * const messageBox = new MessageBox(document.getElementById("message-box") as HTMLElement);
     */
    constructor(element: HTMLElement) {
        this.element = element;
    }

    /**
     * Announce that a cube state has been applied, then fade the box out
     *
     * @param dimensions - The dimensions of the cube the state was applied to
     * @returns {void}
     *
     * @example
     * messageBox.showCubeState(5); // "Applied 5x5x5 cube state"
     */
    showCubeState(dimensions: number): void {
        // Replace whatever the box was showing with the announcement
        const message = document.createElement("span");
        message.textContent = `Applied ${dimensions}x${dimensions}x${dimensions} cube state`;
        this.show(message);
        // Fade out on its own, unless a batch of moves takes the box over first
        this.hideTimeout = window.setTimeout(() => this.hide(), CUBE_STATE_MESSAGE_DURATION);
    }

    /**
     * Render the window of moves around the one that is starting, highlighting it
     *
     * @param moves - Every move of the batch currently being applied
     * @param index - Index within that batch of the move that is starting
     * @returns {void}
     *
     * @example
     * messageBox.onMoveStarted(["R", "U", "R'", "U'"], 1);
     */
    onMoveStarted(moves: string[], index: number): void {
        // One element per slot, so the columns line up as the moves scroll through
        const slots = moveWindow(moves, index).map((move, slot) => {
            const element = document.createElement("span");
            element.className = slot === MOVE_WINDOW_CENTRE ? "move current" : "move";
            element.textContent = move ?? "";
            return element;
        });
        this.show(...slots);
    }

    /**
     * Hide the box once the batch of moves has been applied
     *
     * @returns {void}
     *
     * @example
     * messageBox.onMovesCompleted();
     */
    onMovesCompleted(): void {
        this.hide();
    }

    /**
     * Show the given content, cancelling any pending fade-out
     *
     * @param content - The elements to render inside the box
     * @returns {void}
     *
     * @example
     * this.show(message);
     */
    private show(...content: HTMLElement[]): void {
        this.cancelHide();
        this.element.replaceChildren(...content);
        this.element.classList.add("visible");
    }

    /**
     * Hide the box and drop its content
     *
     * @returns {void}
     *
     * @example
     * this.hide();
     */
    private hide(): void {
        this.cancelHide();
        this.element.classList.remove("visible");
    }

    /**
     * Cancel the pending fade-out, if one is scheduled
     *
     * @returns {void}
     *
     * @example
     * this.cancelHide();
     */
    private cancelHide(): void {
        if (this.hideTimeout !== null) {
            window.clearTimeout(this.hideTimeout);
            this.hideTimeout = null;
        }
    }
}
