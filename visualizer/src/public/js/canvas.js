window.setBackground = () => {
    // Set the background color
    background(191, 224, 221);
}

window.setupCanvas = () => {
    // Create a canvas element that fills the screen
    // and disable the context menu on right-click
    createCanvas(window.innerWidth, window.innerHeight, window.WEBGL).elt.oncontextmenu = () => false;

    // Set a background color
    window.setBackground();

    // Initialize EasyCam
    window.createEasyCam();
}