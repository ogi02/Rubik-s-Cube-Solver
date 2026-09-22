import type { CubeSettings } from "./cubeSettings.ts";

/**
 * The cube settings that can be overridden with environment variables
 */
export type EnvSettings = Partial<Pick<CubeSettings, "animationSpeed" | "moveDelay" | "drawBlackFaces" | "showSubtitles">>;

/**
 * Parse an environment variable holding a number
 *
 * @param name - The name of the environment variable
 * @param value - The raw value of the environment variable
 * @param allowZero - Whether zero is a valid value
 * @returns {number} - The parsed number
 * @throws {Error} - If the value is not a number, is negative, or is zero when zero is not allowed
 *
 * @example
 * parseNumber("VITE_MOVE_DELAY", "250", true); // 250
 */
const parseNumber = (name: string, value: string, allowZero: boolean) : number => {
    const parsed = Number(value);
    if (!Number.isFinite(parsed) || parsed < 0 || (!allowZero && parsed === 0)) {
        const expected = allowZero ? "a non-negative number" : "a positive number";
        throw new Error(`${name} must be ${expected}, got "${value}".`);
    }
    return parsed;
}

/**
 * Parse an environment variable holding a boolean
 *
 * @param name - The name of the environment variable
 * @param value - The raw value of the environment variable
 * @returns {boolean} - The parsed boolean
 * @throws {Error} - If the value is neither "true" nor "false"
 *
 * @example
 * parseBoolean("VITE_SHOW_SUBTITLES", "false"); // false
 */
const parseBoolean = (name: string, value: string) : boolean => {
    if (value !== "true" && value !== "false") {
        throw new Error(`${name} must be "true" or "false", got "${value}".`);
    }
    return value === "true";
}

/**
 * Read the cube settings overridden by environment variables
 *
 * Only the variables that are set, and not empty, appear in the result, so it can be spread over
 * the settings of any cube size.
 *
 * @param env - The environment variables to read
 * @returns {EnvSettings} - The overridden settings
 * @throws {Error} - If a set variable holds an invalid value
 *
 * @example
 * readEnvSettings({ VITE_MOVE_DELAY: "0", VITE_SHOW_SUBTITLES: "false" });
 * // { moveDelay: 0, showSubtitles: false }
 */
export const readEnvSettings = (env: Record<string, string | undefined> = import.meta.env) : EnvSettings => {
    const settings: EnvSettings = {};
    if (env.VITE_ANIMATION_SPEED) {
        settings.animationSpeed = parseNumber("VITE_ANIMATION_SPEED", env.VITE_ANIMATION_SPEED, false);
    }
    if (env.VITE_MOVE_DELAY) {
        settings.moveDelay = parseNumber("VITE_MOVE_DELAY", env.VITE_MOVE_DELAY, true);
    }
    if (env.VITE_DRAW_BLACK_FACES) {
        settings.drawBlackFaces = parseBoolean("VITE_DRAW_BLACK_FACES", env.VITE_DRAW_BLACK_FACES);
    }
    if (env.VITE_SHOW_SUBTITLES) {
        settings.showSubtitles = parseBoolean("VITE_SHOW_SUBTITLES", env.VITE_SHOW_SUBTITLES);
    }
    return settings;
}
