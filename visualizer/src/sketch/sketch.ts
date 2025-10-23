import p5 from "p5";

import { setBackground, setupCanvas, windowResized } from "./canvas";
import { Cube } from "../cube/cube";

/**
 * Cube sketch for p5 visualization
 * @param p - The p5 instance
 *
 * @example
 * new p5(cubeSketch, document.getElementById("visualizer") as HTMLElement);
 */
export const cubeSketch = (p: p5) => {
    const dimensions = 3;
    const speed = 50;
    let cube: Cube;

    /**
     * Setup function for the p5 sketch
     *
     * @example
     * p.setup();
     */
    p.setup = () : void => {
        // Set up the canvas
        setupCanvas(p);
        // Initialize the cube
        cube = new Cube(dimensions, speed, p);
        // Set initial camera position
        p.camera(
            1000, -1000, 1000,   // camera position
            0, 0, 0,      // look at origin
            0, 1, 0       // up vector
        );
    };

    /**
     * Draw function for the p5 sketch
     *
     * @example
     * p.draw();
     */
    p.draw = () : void => {
        // Set background and controls
        setBackground(p);
        // Activate orbit control for 3D navigation
        p.orbitControl();
        // Set scale for better visibility
        p.scale(50);
        // Show the cube
        cube.show();
    };

    Object.assign(p, {
        /**
         * Window resized event handler for the p5 sketch
         *
         * @example
         * p.windowResized();
         */
        windowResized: () : void => {
            windowResized(p);
        }
    })

    /**
     * Key pressed event handler for the p5 sketch
     * @param key - The keyboard event
     *
     * @example
     * p.keyPressed();
     */
    p.keyPressed = (key: KeyboardEvent) : void => {
        console.log(`Key pressed: ${key.key}`);
        if (key.key === 's') {
            let scramble = "D2 B' U' L' F2 B L U2 L' R2 F' D2 F' L2 B L2 D2 B D2 F R2";
            // let scramble1 = "Dw2 B' U' L' F2 B Lw U2 L' R2 F' D2 Fw' L2 Bw L2 D2 B D2 F R2";
            // let scramble2 = "3Rw' Dw D Bw B Fw 3Bw 3Dw' Bw2 Rw' R2 3Fw' B' Fw Uw' Rw' 3Dw D Lw2 Dw' Lw' Rw' L D' F' Uw' 3Uw"
            // let scramble3 = "R' D2 L Rw' Dw2 Bw' 3Lw2 F2 B2 Bw' 3Uw Dw' Fw' Uw' Rw' 3Dw 3Fw D 3Fw 3Dw2 Bw R' Rw' Bw2";
            // let scramble4 = "F2 3Fw D Uw Lw' Uw2 D2 3Bw Bw' D' U2 Uw' Bw D 3Bw Uw' 3Lw2 D2 3Dw2 F Lw2 3Dw' 3Uw2 F' R2;"
            // let scramble5 = "3Uw2 3Bw 3Uw2 L2 R' U Uw 3Dw' F2 3Uw' B R2 D2 Uw 3Dw2 L' 3Fw2 3Rw2 Bw Dw Rw2 B' L' R'"
            // let scramble6 = "3Lw' Dw2 Rw2 3Rw2 3Uw2 L' Fw' Uw2 3Rw2 3Lw2 R Dw Fw F2 3Dw' Lw2 Bw2 3Rw2 Dw' 3Rw F' 3Bw2 Bw' U Bw Uw' 3Rw2 Dw' 3Dw2 U' 3Rw 3Fw2 Bw Lw 3Fw 3Lw' Fw Rw Lw2 R U Lw U D2 3Rw2 Uw U' B' L2 3Fw 3Bw D Bw2 D' L R2 3Rw' B Bw 3Uw Dw2 B' L 3Lw' D' Lw' 3Fw' 3Uw Fw2 Bw2 U2 Rw Fw B' 3Rw2 3Bw2 L2 3Bw 3Uw2 B2 L 3Uw2 U2 Bw2 Rw2 3Rw' 3Lw2 3Uw 3Rw Bw D' B' L' 3Fw R U 3Dw 3Bw2 U' Dw'"
            // let scramble7 = "U D'";
            cube.applyMoves(scramble);
        }
    };
}
