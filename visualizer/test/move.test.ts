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

/**
 * Run Move(moveText).isRotation() in the page, through the module the dev server serves
 *
 * @param page - The page the dev server is loaded in
 * @param moveText - The move notation to construct the Move from
 * @returns Whether the move is a whole-cube rotation
 */
const isRotation = async (page: Page, moveText: string) => {
    return page.evaluate(async (moveText) => {
        const module = await import("/src/cube/move.ts");
        return new module.Move(moveText).isRotation();
    }, moveText);
};

/**
 * Build a real Cube for the given dimension, record which pieces a face move selects, complete
 * a view rotation on the cube (the same way Cube.completeTurn does for x/y/z), and record which
 * pieces the same face move selects afterwards - through the modules the dev server serves.
 *
 * @param page - The page the dev server is loaded in
 * @param dim - The cube dimension to build
 * @param rotationMoveText - The whole-cube rotation to apply between the two selections
 * @param faceMoveText - The face move whose selected pieces are compared before and after
 * @returns The sorted piece-position selections before and after the view rotation
 */
const selectionAcrossViewRotation = async (
    page: Page,
    dim: number,
    rotationMoveText: string,
    faceMoveText: string
) => {
    return page.evaluate(async ({ dim, rotationMoveText, faceMoveText }) => {
        const { Cube } = await import("/src/cube/cube.ts");
        const { Move } = await import("/src/cube/move.ts");

        // A settings object with just enough for the geometry; no rendering happens
        const settings = {
            cubeDimensions: dim,
            animationSpeed: 8,
            moveDelay: 0,
            cameraScale: 1,
            drawBlackFaces: true,
            showSubtitles: false,
            colorWhite: "W", colorYellow: "Y", colorGreen: "G",
            colorBlue: "B", colorOrange: "O", colorRed: "R", colorBlack: "K",
            p5Instance: null as any,
        };
        const cube = new Cube(settings as any);

        const faceMove = new Move(faceMoveText);
        const axis = faceMove.getAxis() as "x" | "y" | "z";
        const layerIndexes = faceMove.getLayerIndexes(dim);
        const selection = () => cube.pieces
            .filter((piece) => layerIndexes.includes(piece[axis]))
            .map((piece) => `${piece.x},${piece.y},${piece.z}`)
            .sort();

        const before = selection();

        // Apply the rotation and complete it immediately, as the cube does once an animation finishes
        cube.turn(rotationMoveText);
        cube.currentAnimation!.finish();
        cube.completeTurn();

        const after = selection();

        return { before, after };
    }, { dim, rotationMoveText, faceMoveText });
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
        test(`Rotation ${moveText} on a ${dim}x${dim} cube spans every layer index around ${axis}`, async ({ page }) => {
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

    const rotationFlags: [string, boolean][] = [
        ["x", true], ["x'", true], ["x2", true],
        ["y", true], ["y'", true], ["y2", true],
        ["z", true], ["z'", true], ["z2", true],
        ["R", false], ["U'", false], ["L2", false],
        ["Fw", false], ["3Rw2", false],
    ];
    for (const [moveText, expected] of rotationFlags) {
        test(`isRotation() for ${moveText} is ${expected}`, async ({ page }) => {
            expect(await isRotation(page, moveText)).toBe(expected);
        });
    }

    // A view rotation must never change what a face move addresses: the pieces it selects
    // (by their fixed x/y/z coordinates) before and after the rotation must be identical.
    const viewRotationCases: [number, string, string][] = [
        [3, "y", "R"],
        [3, "x'", "U"],
        [3, "z2", "L"],
        [3, "y'", "F"],
        [4, "z2", "Fw"],
        [4, "x", "Uw"],
    ];
    for (const [dim, rotationMoveText, faceMoveText] of viewRotationCases) {
        test(`${faceMoveText} on a ${dim}x${dim} cube selects the same pieces before and after ${rotationMoveText}`, async ({ page }) => {
            const { before, after } = await selectionAcrossViewRotation(page, dim, rotationMoveText, faceMoveText);
            // Sanity check: the face move actually selects a non-empty set of pieces
            expect(before.length).toBeGreaterThan(0);
            expect(after).toEqual(before);
        });
    }
});
