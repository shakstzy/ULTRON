"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Cursor = exports.getRandomStartPoint = exports.createCursor = void 0;
const math_1 = require("./math");
const mouse_helper_1 = __importDefault(require("./mouse-helper"));
const utils_1 = require("./utils");
const trusted_types_1 = require("trusted-types");
async function createCursor(page, createCursorOptions) {
    var _a, _b, _c;
    let overshootSpread = 10, overshootRadius = 120, debug = true;
    if (createCursorOptions !== undefined) {
        overshootSpread = (_a = createCursorOptions.overshootSpread) !== null && _a !== void 0 ? _a : 10;
        overshootRadius = (_b = createCursorOptions.overshootRadius) !== null && _b !== void 0 ? _b : 120;
        debug = (_c = createCursorOptions.debug) !== null && _c !== void 0 ? _c : true;
    }
    if (debug)
        (0, mouse_helper_1.default)(page, trusted_types_1.trustedTypes);
    const randomStartPoint = await getRandomStartPoint(page);
    const cursor = new Cursor(page, randomStartPoint, overshootSpread, overshootRadius);
    cursor.addMousePositionTracker();
    cursor.addMouseTargetTracker();
    return cursor;
}
exports.createCursor = createCursor;
async function getRandomStartPoint(page) {
    const windowDimension = JSON.parse(await page.evaluate(() => {
        const windowDimension = {
            width: window.innerWidth,
            height: window.innerHeight,
        };
        return JSON.stringify(windowDimension);
    }));
    const { width, height } = windowDimension;
    const randomStartPoint = {
        x: (0, utils_1.randomValue)(0, width),
        y: (0, utils_1.randomValue)(0, height),
    };
    return randomStartPoint;
}
exports.getRandomStartPoint = getRandomStartPoint;
class Cursor {
    constructor(page, randomStartPoint, overshootSpread, overshootRadius) {
        this.actions = {
            click: async (clickOptions, moveOptions) => {
                let waitBeforeClick = [0, 0], waitBetweenClick = [20, 50], doubleClick = false, target = undefined;
                if (clickOptions !== undefined) {
                    waitBeforeClick = clickOptions.waitBeforeClick || [0, 0];
                    waitBetweenClick = clickOptions.waitBetweenClick || [20, 50];
                    doubleClick = clickOptions.doubleClick || false;
                    target = clickOptions.target || undefined;
                }
                const justClick = async (waitBetweenClick = [20, 50], doubleClick = false) => {
                    await this.page.mouse.down();
                    await (0, utils_1.sleep)((0, utils_1.randomValue)(...waitBetweenClick));
                    await this.page.mouse.up();
                    doubleClick && (await justClick());
                };
                target && (await this.actions.move(target, { ...moveOptions }));
                let correctTarget = typeof target === 'string' ? await this.compareTargetOfMouse(target) : false;
                await (0, utils_1.sleep)((0, utils_1.randomValue)(...waitBeforeClick));
                if (typeof target !== 'string' || correctTarget) {
                    await justClick(waitBetweenClick, doubleClick);
                }
                else {
                    doubleClick
                        ? await this.page.click(target, {
                            clickCount: 2,
                            delay: (0, utils_1.randomValue)(...waitBetweenClick),
                        })
                        : await this.page.click(target, { delay: (0, utils_1.randomValue)(...waitBetweenClick) });
                }
            },
            move: async (target, moveOptions) => {
                let paddingPercentage = 0, waitForSelector = 30000, waitBeforeMove = [0, 0];
                if (moveOptions !== undefined) {
                    paddingPercentage = moveOptions.paddingPercentage || 0;
                    waitForSelector = moveOptions.waitForSelector || 30000;
                    waitBeforeMove = moveOptions.waitBeforeMove || [0, 0];
                }
                await (0, utils_1.sleep)((0, utils_1.randomValue)(...waitBeforeMove));
                if (instanceOfVector(target)) {
                    const destination = target;
                    await this.tracePath((0, math_1.path)(this.previous, destination));
                    this.previous = destination;
                }
                else {
                    let elemBox;
                    if (typeof target === 'string') {
                        try {
                            await this.page.waitForSelector(target, { timeout: waitForSelector });
                        }
                        catch (error) {
                            throw new Error(`Selector ${target} is not present in DOM`);
                        }
                        elemBox = await this.getElemBoundingBox(target);
                    }
                    else {
                        elemBox = target;
                    }
                    const { height, width } = elemBox;
                    const destination = this.getRandomPointInsideElem(elemBox, paddingPercentage);
                    const boxDimension = { height, width };
                    const overshooting = this.shouldOvershoot(this.previous, destination);
                    const to = overshooting ? (0, math_1.overshoot)(destination, this.overshootRadius) : destination;
                    await this.tracePath((0, math_1.path)(this.previous, to));
                    if (overshooting) {
                        const correction = (0, math_1.path)(to, { ...boxDimension, ...destination }, this.overshootSpread);
                        await this.tracePath(correction);
                    }
                    this.previous = destination;
                }
            },
            randomMove: async (value) => {
                value ? value = 0.7 : 0;
                while (Math.random() > value) {
                    try {
                        const rand = await this.getRandomPointOnViewport();
                        await this.tracePath((0, math_1.path)(this.previous, rand));
                        this.previous = rand;
                        await (0, utils_1.sleep)((0, utils_1.randomValue)(20, 80));
                    }
                    catch (_) {
                        console.log('Warning: stopping random mouse movements');
                    }
                }
            }
        };
        this.previous = randomStartPoint;
        this.overshootSpread = overshootSpread;
        this.overshootRadius = overshootRadius;
        this.overshootThreshold = 500;
        this.page = page;
    }
    shouldOvershoot(a, b) {
        return (0, math_1.magnitude)((0, math_1.direction)(a, b)) > this.overshootThreshold;
    }
    async getElemBoundingBox(selector) {
        let viewPortBox;
        let elemBoundingBox = await (await this.page.locator(selector)).boundingBox();
        if (elemBoundingBox === null)
            throw new Error(`Selector ${selector} is not present in DOM`);
        let { y: elemY, x: elemX, height: elemHeight, width: elemWidth } = elemBoundingBox;
        let totalElemHeight = 10, vwHeight = 1;
        let totalElemWidth = 10, vwWidth = 1;
        while (totalElemHeight > vwHeight || totalElemWidth > vwWidth || elemY < 0 || elemX < 0) {
            elemBoundingBox = await (await this.page.locator(selector)).boundingBox();
            if (elemBoundingBox === null)
                throw new Error(`Selector ${selector} is not present in DOM`);
            elemY = elemBoundingBox.y;
            elemHeight = elemBoundingBox.height;
            elemX = elemBoundingBox.x;
            elemWidth = elemBoundingBox.width;
            totalElemHeight = Math.abs(elemY) + elemHeight;
            totalElemWidth = Math.abs(elemX) + elemWidth;
            viewPortBox = await this.getViewportBoundingBox();
            vwHeight = viewPortBox.height;
            vwWidth = viewPortBox.width;
            if (totalElemHeight <= vwHeight && elemY >= 0)
                break;
            if (elemY > 0) {
                await this.page.mouse.wheel(0, 100);
            }
            else if (elemY < 0) {
                await this.page.mouse.wheel(0, -100);
            }
            if (totalElemWidth <= vwWidth && elemX >= 0)
                break;
            if (elemX > 0) {
                await this.page.mouse.wheel(100, 0);
            }
            else if (elemX < 0) {
                await this.page.mouse.wheel(-100, 0);
            }
            await (0, utils_1.sleep)((0, utils_1.randomValue)(40, 80));
        }
        return elemBoundingBox;
    }
    async getViewportBoundingBox() {
        const viewportDimension = JSON.parse(await this.page.evaluate(() => JSON.stringify({
            width: window.innerWidth,
            height: window.innerHeight,
        })));
        return {
            x: 0,
            y: 0,
            width: viewportDimension.width,
            height: viewportDimension.height,
        };
    }
    async getRandomPointOnViewport(paddingPercentage = 0) {
        const windowBoundaryBox = JSON.parse(await this.page.evaluate(() => JSON.stringify({ width: window.innerWidth, height: window.innerHeight })));
        const randomPointInsideViewPort = this.getRandomPointInsideElem({
            x: 0,
            y: 0,
            width: windowBoundaryBox.width,
            height: windowBoundaryBox.height,
        }, paddingPercentage);
        return randomPointInsideViewPort;
    }
    getRandomPointInsideElem({ x, y, width, height }, paddingPercentage = 0) {
        if (paddingPercentage < 0 && paddingPercentage > 100)
            throw new Error('Wrong padding value, choose from scope [0-100]');
        const paddingWidth = (width * paddingPercentage) / 100;
        const paddingHeight = (height * paddingPercentage) / 100;
        return {
            x: x + paddingWidth / 2 + Math.random() * (width - paddingWidth),
            y: y + paddingHeight / 2 + Math.random() * (height - paddingHeight),
        };
    }
    async tracePath(vectors) {
        for (const v of vectors) {
            try {
                await this.page.mouse.move(v.x, v.y);
                this.previous = v;
            }
            catch (error) {
                console.log(error.message);
            }
        }
    }
    addMousePositionTracker() {
        this.page.on('load', () => {
            this.page.evaluate(() => {
                window.mousePos = { x: 0, y: 0 };
                document.addEventListener('mousemove', (e) => {
                    const { clientX, clientY } = e;
                    window.mousePos.x = clientX;
                    window.mousePos.y = clientY;
                });
            }).catch(() => { });
        });
    }
    addMouseTargetTracker() {
        this.page.on('load', () => {
            this.page.evaluate(() => {
                window.mouseTarget = '';
                document.addEventListener('mousemove', (e) => {
                    window.mouseTarget = e.target;
                });
            }).catch(() => { });
        });
    }
    async getActualPosOfMouse() {
        const actualPos = JSON.parse(await this.page.evaluate(() => JSON.stringify(window['mousePos'])));
        return actualPos;
    }
    async compareTargetOfMouse(selector) {
        const isEqual = await this.page.evaluate((selector) => {
            const actualTarget = window['mouseTarget'];
            const selectedTarget = document.querySelector(selector);
            const isEqual = actualTarget.isEqualNode(selectedTarget);
            return isEqual;
        }, selector);
        return isEqual;
    }
}
exports.Cursor = Cursor;
function instanceOfVector(object) {
    if (typeof object === 'string')
        return false;
    return 'x' in object && 'y' in object && Object.keys(object).length === 2 ? true : false;
}
//# sourceMappingURL=cursor.js.map