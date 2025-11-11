import type { CubeSettings } from "./cubeSettings.ts";

/**
 * Map single-character color codes to actual color values.
 *
 * @param val - The color code (W, Y, G, B, O, or R). If the code is not recognized, colorBlack is returned.
 * @param settings - The cube settings containing color definitions.
 * @returns The mapped color value, or colorBlack if the code is not recognized.
 *
 * @example
 * mapColor('R', settings); // returns settings.colorRed
 * mapColor('G', settings); // returns settings.colorGreen
 * mapColor('X', settings); // returns settings.colorBlack (unrecognized code)
 */
export const mapColor = (val: string, settings: CubeSettings) : string => {
    const trimmed = val.trim();

    switch (trimmed) {
        case 'W':
            return settings.colorWhite;
        case 'Y':
            return settings.colorYellow;
        case 'G':
            return settings.colorGreen;
        case 'B':
            return settings.colorBlue;
        case 'O':
            return settings.colorOrange;
        case 'R':
            return settings.colorRed;
        default:
            return settings.colorBlack;
    }
};
