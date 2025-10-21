const Direction = Object.freeze({
    CW: '',
    CCW: '\'',
    DOUBLE: '2'
})

toDirection = (text) => {
    switch (text) {
        case '':
            return Direction.CW;
        case '\'':
            return Direction.CCW;
        case '2':
            return Direction.DOUBLE;
        default:
            throw new Error(`Invalid direction: ${text}`);
    }
}