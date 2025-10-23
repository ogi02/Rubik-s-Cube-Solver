import p5 from "p5";
import {setBackground, setupCanvas, windowResized} from "./canvas";
import { Cube } from "../cube/cube";

/**
 * Cube sketch for p5 visualization
 * @param p - The p5 instance
 *
 * @example
 * new p5(cubeSketch, document.getElementById("visualizer") as HTMLElement);
 */
export const cubeSketch = (p: p5) => {
    const dim = 4;
    let cube: Cube;
    let lastTime = performance.now();
    let frameCount = 0;

    /**
     * Setup function for the p5 sketch
     *
     * @example
     * p.setup();
     */
    p.setup = () : void => {
        setupCanvas(p);

        p.camera(
            1000, -1000, 1000,   // camera position
            0, 0, 0,      // look at origin
            0, 1, 0       // up vector
        );

        cube = new Cube(dim, p);

        // let scramble = "R D2 L2 U F' L D U2 B R2 U2 D2 R2 B R2 B2 U L2 B Rw2 Uw2 D Rw2 R' B2 Rw2 D' R2 D2 R2 U2 Fw D2 L' Fw Uw2 Rw Uw2 F2 L D Rw' Uw";
        // let scramble = "R U Dw' Uw2 3Rw 5Lw'";
        // let scramble = "R U";
        // let splitScramble = scramble.split(" ");
        // splitScramble.forEach(moveText => cube.turn(moveText));
    };

    /**
     * Draw function for the p5 sketch
     *
     * @example
     * p.draw();
     */
    p.draw = () : void => {
        // FPS
        frameCount++;
        const now = performance.now();

        if (now - lastTime >= 1000) {
            console.log(`FPS: ${frameCount}`);
            frameCount = 0;
            lastTime = now;
        }
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
            let scramble = "Dw2 B' U' L' F2 B Lw U2 L' R2 F' D2 Fw' L2 Bw L2 D2 B D2 F R2";
            let splitScramble = scramble.split(" ");
            for (let i = 0; i < splitScramble.length; i++) {
                setTimeout(() => {
                    cube.turn(splitScramble[i]);
                }, i * 100);
            }
        }
    };
}
