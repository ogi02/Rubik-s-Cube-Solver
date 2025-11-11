import type { CubeSettings } from "./cubeSettings.ts";

/**
 * Map single-character color codes to actual color values
 *
 * @param val - The color code
 * @param settings - The cube settings containing color definitions
 * @returns The mapped color value
 *
 * @example
 * mapColor('R', settings); // returns settings.colorRed
 * mapColor('G', settings); // returns settings.colorGreen
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
