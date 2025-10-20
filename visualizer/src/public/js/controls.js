window.keyPressed = key => {
    console.log(`Key pressed: ${key.key}`);

    switch (key.key) {
        case 'x':
            turnX(cube.pieces);
            break;
        case 'y':
            turnY(cube.pieces);
            break;
        case 'z':
            turnZ(cube.pieces);
            break;
        default:
            console.log('No action assigned to this key.');
    }
}