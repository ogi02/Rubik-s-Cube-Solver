const Move = class {
    constructor(moveText) {
        // Parse the move text into layer, direction, and layerAmount
        const moveInfo = this.parse(moveText)[0];
        // Initialize properties
        this.layer = toLayer(moveInfo.layer);
        this.direction = toDirection(moveInfo.direction);
        this.layerAmount = moveInfo.layerAmount;
    }

    parse(fromText) {
        // Match examples: R, R', R2, Rw, Rw', 3Rw2, 2Uw', etc.
        // Regex breakdown:
        // \d*      - optional number at the start (layer count)
        // [RLUDFB] - one of the face letters
        // w?       - optional "w" for wide moves
        // [2']?    - optional modifier at the end (either "2" or "'")
        const tokens = fromText.match(/\d*[RLUDFB]w?[2']?/g);

        if (!tokens) {
            return [];
        }

        return tokens.map(token => {
            // Extract layer count (if any)
            const layerAmountMatch = token.match(/^\d*/);
            let layerAmount = layerAmountMatch ? parseInt(layerAmountMatch, 10) : null;

            // Extract face (R, L, etc.)
            const layerMatch = token.match(/[RLUDFB]/);
            const layer = layerMatch ? layerMatch[0] : null;

            // Check for wide move (contains "w")
            const isWide = token.includes('w');
            if (!(layerAmount)) {
                if (isWide) {
                    layerAmount = 2; // Default to 2 layers for wide moves
                } else {
                    layerAmount = 1; // Default to 1 layer for normal moves
                }
            }

            // Extract direction (last char if "2" or "'")
            const directionMatch = token.match(/([2'])$/);
            const direction = directionMatch ? directionMatch[1] : "";

            return {
                layer: layer,
                direction: direction,
                layerAmount: layerAmount
            };
        });
    }

    getAxis = () => {
        switch (this.layer) {
            case 'U':
            case 'D':
                return "y"
            case 'F':
            case 'B':
                return "z"
            case 'L':
            case 'R':
                return "x"
            default:
                throw new Error(`Invalid layer: ${this.layer}`);
        }
    }

    getAngle = () => {
        switch (this.direction) {
            case '':
                // 90 degrees clockwise
                return Math.PI / 2;
            case '\'':
                // 90 degrees counter-clockwise
                return -Math.PI / 2;
            case '2':
                // 180 degrees
                return Math.PI;
            default:
                throw new Error(`Invalid direction: ${this.direction}`);
        }
    }

    getLayerIndexes = dim => {
        let indexes = [];
        const leftBoundary = -Math.floor((dim - this.layerAmount) / 2);
        const rightBoundary = Math.floor((dim - this.layerAmount) / 2);
        switch (this.layer) {
            case 'U':
            case 'F':
            case 'R':
                for (let i = rightBoundary; i > rightBoundary - this.layerAmount; i--) {
                    indexes.push(i);
                }
                return indexes;
            case 'D':
            case 'B':
            case 'L':
                for (let i = leftBoundary; i < rightBoundary; i++) {
                    indexes.push(i);
                }
                return indexes;
            default:
                throw new Error(`Invalid layer: ${this.layer}`);
        }
    }

    getTurn = dim => {
        return {
            axis: this.getAxis(),
            angle: this.getAngle(),
            layerIndexes: this.getLayerIndexes(dim)
        };
    }
}