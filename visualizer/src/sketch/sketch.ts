import p5 from "p5";

import { Cube } from "../cube/cube.ts";
import { authenticate } from "../client/authenticate.ts";
import { setBackground, setupCanvas, windowResized } from "./canvas.ts";
import { loadCubeSettings, type CubeSettings } from "../utils/cubeSettings.ts";
import { handleApplyMovesMessage, handleCubeStateMessage } from "../client/messageHandlers.ts";

/**
 * Cube sketch for p5 visualization
 * @param p - The p5 instance
 *
 * @example
 * new p5(cubeSketch, document.getElementById("visualizer") as HTMLElement);
 */
export const cubeSketch = (p: p5) => {
    let settings: CubeSettings;
    let cube: Cube;
    let socket: WebSocket;

    /**
     * Setup function for the p5 sketch
     *
     * @example
     * p.setup();
     */
    p.setup = async () : Promise<void> => {
        // Set up the canvas
        setupCanvas(p);
        // Set initial camera position
        p.camera(
            1000, -1000, 1000,   // camera position
            0, 0, 0,      // look at origin
            0, 1, 0       // up vector
        );

        // Create a default 3x3 cube
        settings = loadCubeSettings(3, p);
        cube = new Cube(settings);

        // Set up server connection if needed
        if (import.meta.env.VITE_CONNECT_TO_SERVER === "true") {
            await setUpServer();
        }
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
        p.scale(settings.cameraScale);
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
     * Set up server connection and WebSocket
     *
     * @example
     * await setUpServer();
     */
    const setUpServer = async () : Promise<void> => {
        // Authenticate and get token
        const token: string = await authenticate();

        // Create socket connection with token
        socket = new WebSocket(`${import.meta.env.VITE_WEBSOCKET_URL}?token=${token}`);

        // WebSocket open event handler
        socket.onopen = () : void => {
            console.log("Connected to server");
        }

        // WebSocket message event handler
        socket.onmessage = (event: MessageEvent) : void => {
            // Parse incoming data
            try {
                const data = JSON.parse(event.data);

                // Handle cube state message
                if (data.type === "cube_state") {
                    cube = handleCubeStateMessage(data, p);
                }

                // Handle apply moves message
                if (data.type === "apply_moves") {
                    handleApplyMovesMessage(data, cube);
                }
            } catch (error) {
                console.error("Error handling message:", error);
            }

        };

        // WebSocket error event handler
        socket.onerror = (error: Event) : void => {
            console.error("WebSocket error:", error);
        }

        // Handle graceful disconnect before unload
        const beforeUnloadHandler = () : void => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ type: "disconnect" }));
            }
        }
        window.addEventListener("beforeunload", beforeUnloadHandler);

        // WebSocket close event handler
        socket.onclose = (event: CloseEvent) : void => {
            window.removeEventListener("beforeunload", beforeUnloadHandler);
            console.log("Connection closed:", event.reason);
        }
    }
}
