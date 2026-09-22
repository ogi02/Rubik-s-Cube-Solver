import { test, expect, type Page } from "@playwright/test";

/**
 * Run readEnvSettings in the page, through the module the dev server serves
 *
 * @param page - The page the dev server is loaded in
 * @param env - The environment variables to read
 * @returns The overridden settings, or the message of the error that was thrown
 */
const readEnvSettings = async (page: Page, env: Record<string, string>) => {
    return page.evaluate(async (env) => {
        const module = await import("/src/utils/envSettings.ts");
        try {
            return module.readEnvSettings(env);
        } catch (error) {
            return (error as Error).message;
        }
    }, env);
};

test.describe("readEnvSettings", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("http://localhost:5173");
    });

    test("Returns nothing when no variable is set", async ({ page }) => {
        expect(await readEnvSettings(page, {})).toEqual({});
    });

    test("Ignores empty variables", async ({ page }) => {
        const env = { VITE_ANIMATION_SPEED: "", VITE_MOVE_DELAY: "", VITE_DRAW_BLACK_FACES: "", VITE_SHOW_SUBTITLES: "" };
        expect(await readEnvSettings(page, env)).toEqual({});
    });

    test("Parses every variable", async ({ page }) => {
        const env = {
            VITE_ANIMATION_SPEED: "12.5",
            VITE_MOVE_DELAY: "0",
            VITE_DRAW_BLACK_FACES: "true",
            VITE_SHOW_SUBTITLES: "false",
        };
        expect(await readEnvSettings(page, env)).toEqual({
            animationSpeed: 12.5,
            moveDelay: 0,
            drawBlackFaces: true,
            showSubtitles: false,
        });
    });

    const invalid: [string, string, string][] = [
        ["VITE_ANIMATION_SPEED", "fast", "a positive number"],
        ["VITE_ANIMATION_SPEED", "0", "a positive number"],
        ["VITE_ANIMATION_SPEED", "-5", "a positive number"],
        ["VITE_MOVE_DELAY", "abc", "a non-negative number"],
        ["VITE_MOVE_DELAY", "-1", "a non-negative number"],
        ["VITE_MOVE_DELAY", "Infinity", "a non-negative number"],
        ["VITE_DRAW_BLACK_FACES", "yes", "\"true\" or \"false\""],
        ["VITE_SHOW_SUBTITLES", "TRUE", "\"true\" or \"false\""],
    ];
    for (const [name, value, expected] of invalid) {
        test(`Throws on ${name}=${value}`, async ({ page }) => {
            expect(await readEnvSettings(page, { [name]: value })).toBe(`${name} must be ${expected}, got "${value}".`);
        });
    }
});
