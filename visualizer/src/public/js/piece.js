window.Piece = class {
    constructor(x, y, z) {
        // Initialize transformation matrix
        this.matrix = window.mat4.create();
        // Set initial position
        this.update(x, y, z);
        // Highlight flag
        this.highlighted = null;
    }

    update = (x, y, z) => {
        this.x = x;
        this.y = y;
        this.z = z;
        window.mat4.fromTranslation(this.matrix, [this.x, this.y, this.z]);
    }

    show = () => {
        if (this.highlighted === "red") {
            window.fill(255, 0, 0);
        }
        else if (this.highlighted === "green") {
            window.fill(0, 255, 0);
        }
        else if (this.highlighted === "blue") {
            window.fill(0, 0, 255);
        }
        else {
            window.fill(200);
        }
        window.stroke(0);
        window.strokeWeight(2);
        window.push();
        window.applyMatrix(this.matrix);
        window.box(1);
        window.pop();
    }
}