import playwright from 'playwright-core';
import { Vector, BoundingBox } from './math';
export declare type createCursorOptions = {
    overshootSpread?: number;
    overshootRadius?: number;
    debug?: boolean;
};
export declare function createCursor(page: playwright.Page, createCursorOptions?: createCursorOptions): Promise<Cursor>;
export interface Cursor {
    page: playwright.Page;
    previous: Vector;
    overshootSpread: number;
    overshootRadius: number;
    overshootThreshold: number;
    shouldOvershoot(a: Vector, b: Vector): boolean;
    getElemBoundingBox(selector: string): Promise<BoundingBox>;
    getViewportBoundingBox(): Promise<BoundingBox>;
    getRandomPointOnViewport(paddingPercentage: number): Promise<Vector>;
    getRandomPointInsideElem({ x, y, width, height }: BoundingBox, paddingPercentage?: number): Vector;
    tracePath(vectors: Iterable<Vector>): Promise<void>;
    addMousePositionTracker(): void;
    addMouseTargetTracker(): void;
    getActualPosOfMouse(): Promise<Vector>;
    compareTargetOfMouse(selector: string): Promise<boolean>;
}
export interface Actions {
    click(clickOptions?: clickOptions, moveOptions?: moveOptions): Promise<void>;
    move(target: string | BoundingBox | Vector, moveOptions?: moveOptions): Promise<void>;
    randomMove(value?: number): Promise<void>;
}
export declare type clickOptions = {
    target?: string | BoundingBox | Vector;
    waitBeforeClick?: [number, number];
    waitBetweenClick?: [number, number];
    doubleClick?: boolean;
};
export declare type moveOptions = {
    paddingPercentage?: number;
    waitForSelector?: number;
    waitBeforeMove?: [number, number];
};
export declare function getRandomStartPoint(page: playwright.Page): Promise<{
    x: number;
    y: number;
}>;
export declare class Cursor {
    page: playwright.Page;
    previous: Vector;
    overshootSpread: number;
    overshootRadius: number;
    overshootThreshold: number;
    constructor(page: playwright.Page, randomStartPoint: Vector, overshootSpread: number, overshootRadius: number);
    actions: Actions;
}
