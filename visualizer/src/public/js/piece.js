window.Piece = class {
    constructor(x, y, z, len) {
        this.pos = window.createVector(x, y, z);
        this.len = len;
    }

    show = () => {
        window.fill(255);
        window.stroke(0);
        window.strokeWeight(8);
        window.push();
        window.translate(this.pos.x, this.pos.y, this.pos.z);
        window.box(this.len);
        window.pop();
    }
}