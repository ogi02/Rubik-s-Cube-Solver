turnX = (pieces, angle, layerIndexes) => {
    pieces.forEach(piece => {
        if (layerIndexes.includes(piece.x)) {
            // Create rotation matrix for a turn around X axis
            let matrix = window.mat2d.create();
            // Rotate 90 / 180 / 270 degrees (π/2 / π / 3π/2 radians)
            window.mat2d.rotate(matrix, matrix, angle);
            // Translate
            window.mat2d.translate(matrix, matrix, [piece.y, piece.z])
            // Update piece position
            piece.update(piece.x, Math.round(matrix[4]), Math.round(matrix[5]));
        }
    })
}

turnY = (pieces, angle, layerIndexes) => {
    pieces.forEach(piece => {
        if (layerIndexes.includes(piece.y)) {
            // Create rotation matrix for a turn around Y axis
            let matrix = window.mat2d.create();
            // Rotate 90 / 180 / 270 degrees (π/2 / π / 3π/2 radians)
            window.mat2d.rotate(matrix, matrix, angle);
            // Translate
            window.mat2d.translate(matrix, matrix, [piece.x, piece.z])
            // Update piece position
            piece.update(Math.round(matrix[4]), piece.y, Math.round(matrix[5]));
        }
    });
}

turnZ = (pieces, angle, layerIndexes) => {
    pieces.forEach(piece => {
        if (layerIndexes.includes(piece.z)) {
            // Create rotation matrix for a turn around Z axis
            let matrix = window.mat2d.create();
            // Rotate 90 / 180 / 270 degrees (π/2 / π / 3π/2 radians)
            window.mat2d.rotate(matrix, matrix, angle);
            // Translate
            window.mat2d.translate(matrix, matrix, [piece.x, piece.y])
            // Update piece position
            piece.update(Math.round(matrix[4]), Math.round(matrix[5]), piece.z);
        }
    });
}