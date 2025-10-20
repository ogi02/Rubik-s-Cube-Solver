turnX = pieces => {
    pieces.forEach(piece => {
        if (piece.x === 1) {
            // Create rotation matrix for 90-degree turn around X axis
            let matrix = window.mat2d.create();
            // Rotate 90 degrees (π/2 radians)
            window.mat2d.rotate(matrix, matrix, Math.PI / 2);
            // Translate
            window.mat2d.translate(matrix, matrix, [piece.y, piece.z])
            // Update piece position
            piece.update(piece.x, Math.round(matrix[4]), Math.round(matrix[5]));
        }
    })
}

turnY = pieces => {
    pieces.forEach(piece => {
        if (piece.y === 1) {
            // Create rotation matrix for 90-degree turn around Y axis
            let matrix = window.mat2d.create();
            // Rotate 90 degrees (π/2 radians)
            window.mat2d.rotate(matrix, matrix, Math.PI / 2);
            // Translate
            window.mat2d.translate(matrix, matrix, [piece.z, piece.x])
            // Update piece position
            piece.update(Math.round(matrix[5]), piece.y, Math.round(matrix[4]));
        }
    });
}

turnZ = pieces => {
    pieces.forEach(piece => {
        if (piece.z === 1) {
            // Create rotation matrix for 90-degree turn around Z axis
            let matrix = window.mat2d.create();
            // Rotate 90 degrees (π/2 radians)
            window.mat2d.rotate(matrix, matrix, Math.PI / 2);
            // Translate
            window.mat2d.translate(matrix, matrix, [piece.x, piece.y])
            // Update piece position
            piece.update(Math.round(matrix[4]), Math.round(matrix[5]), piece.z);
        }
    });
}