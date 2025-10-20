window.setBackground = () => {
    // Set the background color
    window.background(191, 224, 221);
}

window.setupCanvas = () => {
    // Create a canvas element that fills the screen
    // and disable the context menu on right-click
    createCanvas(window.windowWidth, window.windowHeight, window.WEBGL).elt.oncontextmenu = () => false;

    // Set a background color
    window.setBackground();

    // Initialize EasyCam
    window.createEasyCam();
}

window.windowResized = () => {
    // Resize the canvas when the window is resized
    window.resizeCanvas(window.windowWidth, window.windowHeight);

    window.setBackground();
}