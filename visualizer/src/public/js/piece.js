// piece.js

// Face colors
window.colors = ['#FFFFFF', '#FFFF00', '#FFA500', '#FF0000', '#00FF00', '#0000FF'];

// Face indices
window.UPP = 0;
window.DWN = 1;
window.RGT = 2;
window.LFT = 3;
window.FRT = 4;
window.BCK = 5;

// Piece class
window.Piece = class {
    constructor(x, y, z, len) {
        this.pos = window.createVector(x, y, z);
        this.len = len;
    }

    show() {
        const r = this.len / 2;
        push();
        translate(this.pos.x, this.pos.y, this.pos.z);

        // Back
        push();
        fill(colors[BCK]);
        window.beginShape();
        vertex(-r,-r,-r); vertex(r,-r,-r); vertex(r,r,-r); vertex(-r,r,-r);
        window.endShape(window.CLOSE);
        window.pop();

        // Front
        push();
        fill(colors[FRT]);
        window.beginShape();
        vertex(-r,-r,r); vertex(r,-r,r); vertex(r,r,r); vertex(-r,r,r);
        window.endShape(window.CLOSE);
        window.pop();

        // Up
        push();
        fill(colors[UPP]);
        window.beginShape();
        vertex(-r,r,-r); vertex(r,r,-r); vertex(r,r,r); vertex(-r,r,r);
        window.endShape(window.CLOSE);
        window.pop();

        // Down
        push();
        fill(colors[DWN]);
        window.beginShape();
        vertex(-r,-r,-r); vertex(r,-r,-r); vertex(r,-r,r); vertex(-r,-r,r);
        window.endShape(window.CLOSE);
        window.pop();

        // Left
        push();
        fill(colors[LFT]);
        window.beginShape();
        vertex(-r,-r,-r); vertex(-r,r,-r); vertex(-r,r,r); vertex(-r,-r,r);
        window.endShape(window.CLOSE);
        window.pop();

        // Right
        push();
        fill(colors[RGT]);
        window.beginShape();
        vertex(r,-r,-r); vertex(r,r,-r); vertex(r,r,r); vertex(r,-r,r);
        window.endShape(window.CLOSE);
        window.pop();

        window.pop();
    }
}
