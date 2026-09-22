import { test, expect, type Page } from "@playwright/test";

/**
 * Run Move(moveText).getTurn(dim) in the page, through the module the dev server serves
 *
 * @param page - The page the dev server is loaded in
 * @param moveText - The move notation to construct the Move from
 * @param dim - The cube dimension to pass to getTurn
 * @returns The turn's axis, angle and layerIndexes, or the message of the error that was thrown
 */
const getTurn = async (page: Page, moveText: string, dim: number) => {
    return page.evaluate(async ({ moveText, dim }) => {
        const module = await import("/src/cube/move.ts");
        try {
            return new module.Move(moveText).getTurn(dim);
        } catch (error) {
            return (error as Error).message;
        }
    }, { moveText, dim });
};

const HALF_PI = Math.PI / 2;

test.describe("Move", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("http://localhost:5173");
    });

    const rotations: [string, string, number, number, number[]][] = [
        // [moveText, axis, angle, dim, layerIndexes]
        ["x", "x", HALF_PI, 3, [1, 0, -1]],
        ["x'", "x", -HALF_PI, 3, [1, 0, -1]],
        ["x2", "x", Math.PI, 3, [1, 0, -1]],
        ["y", "y", -HALF_PI, 3, [1, 0, -1]],
        ["y'", "y", HALF_PI, 3, [1, 0, -1]],
        ["y2", "y", Math.PI, 3, [1, 0, -1]],
        ["z", "z", HALF_PI, 3, [1, 0, -1]],
        ["z'", "z", -HALF_PI, 3, [1, 0, -1]],
        ["z2", "z", Math.PI, 3, [1, 0, -1]],
        ["x", "x", HALF_PI, 4, [1.5, 0.5, -0.5, -1.5]],
        ["x'", "x", -HALF_PI, 4, [1.5, 0.5, -0.5, -1.5]],
        ["x2", "x", Math.PI, 4, [1.5, 0.5, -0.5, -1.5]],
        ["y", "y", -HALF_PI, 4, [1.5, 0.5, -0.5, -1.5]],
        ["y'", "y", HALF_PI, 4, [1.5, 0.5, -0.5, -1.5]],
        ["y2", "y", Math.PI, 4, [1.5, 0.5, -0.5, -1.5]],
        ["z", "z", HALF_PI, 4, [1.5, 0.5, -0.5, -1.5]],
        ["z'", "z", -HALF_PI, 4, [1.5, 0.5, -0.5, -1.5]],
        ["z2", "z", Math.PI, 4, [1.5, 0.5, -0.5, -1.5]],
    ];
    for (const [moveText, axis, angle, dim, layerIndexes] of rotations) {
        test(`Rotation ${moveText} on a ${dim}x${dim} cube turns every layer around ${axis}`, async ({ page }) => {
            expect(await getTurn(page, moveText, dim)).toEqual({ axis, angle, layerIndexes });
        });
    }

    const unchanged: [string, number, { axis: string; angle: number; layerIndexes: number[] }][] = [
        ["R", 3, { axis: "x", angle: HALF_PI, layerIndexes: [1] }],
        ["Uw", 5, { axis: "y", angle: -HALF_PI, layerIndexes: [-2, -1] }],
        ["3Rw2", 7, { axis: "x", angle: Math.PI, layerIndexes: [3, 2, 1] }],
    ];
    for (const [moveText, dim, expected] of unchanged) {
        test(`Face move ${moveText} on a ${dim}x${dim} cube is unchanged`, async ({ page }) => {
            expect(await getTurn(page, moveText, dim)).toEqual(expected);
        });
    }

    const invalid: [string, number, string][] = [
        ["Q", 3, "Invalid layer: null"],
        ["2xw", 3, "Invalid layer: null"],
        ["3y", 3, "Invalid layer: null"],
        ["Xw", 3, "Invalid layer: null"],
        ["4Rw", 3, "Layer amount 4 exceeds 1/2 cube dimension 3"],
    ];
    for (const [moveText, dim, expectedMessage] of invalid) {
        test(`Throws on ${moveText} with dim ${dim}`, async ({ page }) => {
            expect(await getTurn(page, moveText, dim)).toBe(expectedMessage);
        });
    }
});
