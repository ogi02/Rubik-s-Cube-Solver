import p5 from "p5";

/**
 * Set the background color of the canvas
 * @param p - The p5 instance
 *
 * @example
 * setBackground(p);
 */
export const setBackground = (p: p5) => {
    // Set the background color
    p.background(191, 224, 221);
};

/**
 * Set up the canvas
 * @param p - The p5 instance
 *
 * @example
 * setupCanvas(p);
 */
export const setupCanvas = (p: p5) => {
    // Create a canvas element that fills the screen
    // and disable the context menu on right-click
    const canvas = p.createCanvas(window.innerWidth, window.innerHeight, p.WEBGL);
    canvas.elt.oncontextmenu = () => false;

    // Set a background color
    setBackground(p);
};

/**
 * Handle window resize event
 * @param p - The p5 instance
 *
 * @example
 * windowResized(p);
 */
export const windowResized = (p: p5) => {
    // Resize the canvas when the window is resized
    p.resizeCanvas(window.innerWidth, window.innerHeight);

    setBackground(p);
};
