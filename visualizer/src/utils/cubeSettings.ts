import p5 from "p5";

/**
 * Settings for different cube dimensions in the visualizer.
 *
 * @interface CubeSettings
 * @property {number} cubeDimensions - The dimensions of the cube (e.g., 3 for a 3x3 cube)
 * @property {number} animationSpeed - The speed of the cube's animations (in percentage of the angle)
 * @property {number} moveDelay - The delay between moves in milliseconds
 * @property {number} cameraScale - The scale of the camera
 * @property {boolean} drawBlackFaces - Whether to draw black faces (for rendering optimization)
 * @property {string} colorWhite - Color for the white face
 * @property {string} colorYellow - Color for the yellow face
 * @property {string} colorGreen - Color for the green face
 * @property {string} colorBlue - Color for the blue face
 * @property {string} colorOrange - Color for the orange face
 * @property {string} colorRed - Color for the red face
 * @property {string} colorBlack - Color for the black face
 * @property {p5} p5Instance - The p5 instance
 */
export interface CubeSettings {
    // The dimensions of the cube (e.g., 3 for a 3x3 cube)
    cubeDimensions: number;
    // The speed of the cube's animations (in percentage of the angle)
    animationSpeed: number;
    // The delay between moves in milliseconds
    moveDelay: number;
    // The scale of the camera
    cameraScale: number;
    // Whether to draw black faces (for rendering optimization)
    drawBlackFaces: boolean;
    // Color settings
    colorWhite: string;
    colorYellow: string;
    colorGreen: string;
    colorBlue: string;
    colorOrange: string;
    colorRed: string;
    colorBlack: string;
    // The p5 instance
    p5Instance: p5;
}

// Default settings for a 3x3 cube
export const DefaultSettings: CubeSettings = {
    cubeDimensions: 3,
    animationSpeed: 50,
    moveDelay: 20,
    cameraScale: 200,
    drawBlackFaces: true,
    colorWhite: "#FFFFFF",
    colorYellow: "#FFFF00",
    colorGreen: "#00FF00",
    colorBlue: "#0000FF",
    colorOrange: "#FF9000",
    colorRed: "#FF0000",
    colorBlack: "#222222",
    p5Instance: null as unknown as p5
}

// Settings for 1x1 cube
export const Settings1x1: CubeSettings = {
    ...DefaultSettings,
    cubeDimensions: 1,
    cameraScale: 300,
}

// Settings for 2x2 cube
export const Settings2x2: CubeSettings = {
    ...DefaultSettings,
    cubeDimensions: 2,
    cameraScale: 250,
}

// Settings for 4x4 cube
export const Settings4x4: CubeSettings = {
    ...DefaultSettings,
    cubeDimensions: 4,
    cameraScale: 150,
}

// Settings for 5x5 cube
export const Settings5x5: CubeSettings = {
    ...DefaultSettings,
    cubeDimensions: 5,
    cameraScale: 120,
}

// Settings for 6x6 cube
export const Settings6x6: CubeSettings = {
    ...DefaultSettings,
    cubeDimensions: 6,
    cameraScale: 110,
    drawBlackFaces: false,
}

// Settings for 7x7 cube
export const Settings7x7: CubeSettings = {
    ...DefaultSettings,
    cubeDimensions: 7,
    cameraScale: 100,
    drawBlackFaces: false,
}

/**
 * Load cube settings based on the given dimensions.
 *
 * @param {number} dimensions - The dimensions of the cube (e.g., 3 for a 3x3 cube)
 * @param {p5} p5Instance - The p5 instance
 * @returns {CubeSettings} - The settings for the specified cube dimensions
 * @throws {Error} - If the dimensions are less than 1
 *
 * @example
 * const settings = loadCubeSettings(3, p);
 */
export const loadCubeSettings = (dimensions: number, p5Instance: p5) : CubeSettings => {
    // Validate dimensions
    if (dimensions < 1) {
        throw new Error(`Unsupported cube dimensions: ${dimensions}.`);
    }
    // Return settings based on dimensions
    switch (dimensions) {
        case 3:
            return {...DefaultSettings, p5Instance}
        case 1:
            return {...Settings1x1, p5Instance};
        case 2:
            return {...Settings2x2, p5Instance};
        case 4:
            return {...Settings4x4, p5Instance}
        case 5:
            return {...Settings5x5, p5Instance};
        case 6:
            return {...Settings6x6, p5Instance};
        case 7:
            return {...Settings7x7, p5Instance};
        default:
            return {
                ...DefaultSettings,
                cubeDimensions: dimensions,
                cameraScale: 750 / dimensions,
                drawBlackFaces: false,
                p5Instance: p5Instance,
            };
    }
}
