import type { Move } from "./move";

/**
 * Class to handle animation of a cube in 3D space.
 *
 * @class Animation
 * @property {Move} move - Move object containing animation parameters.
 * @property {number} angle - Current angle of rotation.
 * @property {number} speed - Speed of the animation.
 * @property {boolean} animating - Flag indicating if the animation is in progress.
 * @property {boolean} finished - Flag indicating if the animation has finished.
 *
 * @example
 * const move = new Move("R");
 * const animation = new Animation(move, 5);
 * animation.start();
 */
export class Animation {
    move: Move;
    angle: number = 0;
    speed: number;
    animating: boolean = false;
    finished: boolean = false;

    /**
     * Constructor for the Animation class.
     *
     * @param move - Move object containing animation parameters.
     * @param speed - Speed of the animation.
     */
    constructor(move: Move, speed: number) {
        this.move = move;
        this.speed = speed;
    };

    /**
     * Start the animation.
     *
     * @example
     * animation.start();
     */
    start() : void {
        this.animating = true;
        this.finished = false;
        this.angle = 0;
    };

    /**
     * Finish the animation.
     *
     * @example
     * animation.finish();
     */
    finish() : void {
        this.animating = false;
        this.finished = true;
        this.angle = this.move.getAngle();
    };

    /**
     * Check if the animation is finished.
     *
     * @return {boolean} True if the animation is finished, false otherwise.
     *
     * @example
     * if (animation.isFinished()) {
     *     // Do something
     * }
     */
    isFinished() : boolean {
        return this.finished;
    };

    /**
     * Update the animation state.
     *
     * @example
     * animation.update();
     */
    update() : void {
        if (this.animating) {
            // Speed is percentage of the angle to be covered per update
            const rotationStep : number = this.move.getAngle() * (this.speed / 100);
            if (Math.abs(this.move.getAngle()) === Math.PI / 2) {
                // For single turns, use full speed
                this.angle += rotationStep;
            }
            else {
                // For double turns, speed is halved
                this.angle += rotationStep * 0.5;
            }
            if (Math.abs(this.angle) >= Math.abs(this.move.getAngle())) {
                this.finish();
            }
        }
    };
}
