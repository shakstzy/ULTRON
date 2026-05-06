"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const playwright_core_1 = require("playwright-core");
const cursor_1 = require("./cursor");
(async () => {
    try {
        const browser = await playwright_core_1.chromium.launch({
            channel: 'chrome',
            headless: false,
        });
        const browserContext = await browser.newContext({
            viewport: null,
        });
        const page = await browserContext.newPage();
        const cursor = await (0, cursor_1.createCursor)(page);
        await page.goto('https://www.google.com');
        const randomPoint = await cursor.getRandomPointOnViewport();
        await page.waitForTimeout(5000);
        await cursor.actions.move(randomPoint);
        await cursor.actions.move({ x: 70, y: 70 });
        await cursor.actions.move({ x: 500, y: 500 }, { waitBeforeMove: [500, 1500] });
        await cursor.actions.move({ x: 50, y: 10 });
        await cursor.actions.move('#L2AGLb > div', { paddingPercentage: 30 });
        await cursor.actions.move(randomPoint);
        await cursor.actions.randomMove();
        await cursor.actions.randomMove(0.7);
        await cursor.actions.move('#L2AGLb > div', {
            paddingPercentage: 50,
            waitBeforeMove: [1000, 2000],
            waitForSelector: 30000,
        });
        await cursor.actions.click({ target: '#L2AGLb > div', waitBetweenClick: [20, 50] }, {
            paddingPercentage: 50,
            waitBeforeMove: [1000, 2000],
            waitForSelector: 30000,
        });
        await cursor.actions.click({
            target: 'body > div.L3eUgb > div.o3j99.ikrT4e.om7nvf > form > div:nth-child(1) > div.A8SBwf > div.RNNXgb > div > div.a4bIc > input',
        });
        await cursor.actions.click({ waitBeforeClick: [500, 1000], waitBetweenClick: [20, 50] });
        await cursor.actions.move({ x: 50, y: 10 });
        await cursor.actions.click({
            target: 'body > div.L3eUgb > div.o3j99.ikrT4e.om7nvf > form > div:nth-child(1) > div.A8SBwf > div.RNNXgb > div > div.a4bIc > input',
        }, { paddingPercentage: 70, waitBeforeMove: [500, 2500] });
        await cursor.actions.click({ waitBetweenClick: [20, 50], doubleClick: true });
    }
    catch (error) {
        console.log(error.message);
    }
})();
//# sourceMappingURL=example.js.map