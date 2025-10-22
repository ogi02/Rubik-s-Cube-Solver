import { test, expect } from "@playwright/test";

test("Builds and runs without console errors", async ({ page }) => {
    // Navigate to the application
    await page.goto("http://localhost:5173");
    // Collect console error messages
    const consoleMessages: string[] = [];
    page.on("console", (msg) => {
        if (msg.type() === "error") {
            consoleMessages.push(msg.text());
        }
    });
    // Wait for a few seconds to capture any console errors
    await page.waitForTimeout(3000);
    // Assert that there are no console error messages
    expect(consoleMessages).toEqual([]);
});
