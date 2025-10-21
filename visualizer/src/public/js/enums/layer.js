const Layer = Object.freeze({
    U: 'U',
    D: 'D',
    F: 'F',
    B: 'B',
    L: 'L',
    R: 'R',
})

toLayer = (text) => {
    switch (text) {
        case 'U':
            return Layer.U;
        case 'D':
            return Layer.D;
        case 'F':
            return Layer.F;
        case 'B':
            return Layer.B;
        case 'L':
            return Layer.L;
        case 'R':
            return Layer.R;
        default:
            throw new Error(`Invalid face: ${text}`);
    }
}