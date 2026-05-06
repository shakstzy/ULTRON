"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.randomValue = exports.sleep = void 0;
const sleep = async (ms) => await new Promise((resolve) => setTimeout(resolve, ms));
exports.sleep = sleep;
function randomValue(min, max) {
    min = Math.ceil(min);
    max = ~~max;
    return ~~(Math.random() * (max - min)) + min;
}
exports.randomValue = randomValue;
//# sourceMappingURL=utils.js.map