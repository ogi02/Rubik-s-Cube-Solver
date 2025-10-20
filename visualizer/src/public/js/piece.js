window.Piece = class {
    constructor(x, y, z) {
        this.pos = window.createVector(x, y, z);
        this.highlighted = false;
    }

    show = () => {

        if (this.highlighted) {
            window.fill(255, 0, 0);
        }
        else {
            window.fill(200);
        }
        window.stroke(0);
        window.strokeWeight(2);
        window.push();
        window.translate(this.pos.x, this.pos.y, this.pos.z);
        window.box(1);
        window.pop();
    }
}