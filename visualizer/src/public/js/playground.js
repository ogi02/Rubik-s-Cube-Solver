import {generateCanvas} from "./canvas";

function setup() {
    // Create canvas
    generateCanvas();


    // Connect to the server
    socket = io(); // connects automatically to the same host

    // Listen for 'mouse' events from other clients
    socket.on('mouse', (data) => {
        console.log(`Got: x=${data.x}, y=${data.y}`);
        fill(0, 0, 255); // blue circles for remote users
        noStroke();
        ellipse(data.x, data.y, 20, 20);
    });
}

function draw() {
    // Nothing in draw
}

function mouseDragged() {
    fill(255); // white circles for local user
    noStroke();
    ellipse(mouseX, mouseY, 20, 20);

    // Send mouse coordinates to server
    sendMouse(mouseX, mouseY);
}

function sendMouse(x, y) {
    const data = { x, y };
    console.log(`sendMouse: x=${x}, y=${y}`);
    socket.emit('mouse', data);
}