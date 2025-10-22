import { test, expect } from "@playwright/test";

test("Builds and runs without console errors", async ({ page }) => {
    // Collect console error messages
    const consoleMessages: string[] = [];
    page.on("console", (msg) => {
        if (msg.type() === "error") {
            consoleMessages.push(msg.text());
        }
    });
    // Navigate to the application
    await page.goto("http://localhost:5173");
    // Wait for the page to finish loading before asserting
    await page.waitForLoadState('networkidle');
    // Assert that there are no console error messages
    expect(consoleMessages).toEqual([]);
});
