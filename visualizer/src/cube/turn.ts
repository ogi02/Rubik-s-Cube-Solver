import { mat2d } from "gl-matrix";
import type { Piece } from "./piece";
import {roundToDecimal} from "../utils/math";

/**
 * Turn pieces around X axis
 * @param pieces - Array of pieces to turn
 * @param angle - Angle to turn (in radians)
 * @param layerIndexes - Indexes of layers to turn
 *
 * @example
 * const pieces: Piece[] = [new Piece(1, 0, 0, p), new Piece(0, 1, 0, p)];
 * turnX(pieces, Math.PI / 2, [1]);
 */
export const turnX = (pieces: Piece[], angle: number, layerIndexes: number[]) => {
    pieces.forEach(piece => {
        if (layerIndexes.includes(piece.x)) {
            // Create rotation matrix for a turn around X axis
            let matrix = mat2d.create();
            // Rotate 90 / 180 / 270 degrees (π/2 / π / 3π/2 radians)
            mat2d.rotate(matrix, matrix, angle);
            // Translate
            mat2d.translate(matrix, matrix, [piece.y, piece.z]);
            // Update piece position
            piece.update(piece.x, roundToDecimal(matrix[4], 1), roundToDecimal(matrix[5], 1));
            // Update faces position
            piece.updateFaces('x', angle);
        }
    });
};

/**
 * Turn pieces around Y axis
 * @param pieces - Array of pieces to turn
 * @param angle - Angle to turn (in radians)
 * @param layerIndexes - Indexes of layers to turn
 *
 * @example
 * const pieces: Piece[] = [new Piece(1, 0, 0, p), new Piece(0, 1, 0, p)];
 * turnY(pieces, Math.PI / 2, [1]);
 */
export const turnY = (pieces: Piece[], angle: number, layerIndexes: number[]) => {
    pieces.forEach(piece => {
        if (layerIndexes.includes(piece.y)) {
            // Create rotation matrix for a turn around Y axis
            let matrix = mat2d.create();
            // Rotate 90 / 180 / 270 degrees (π/2 / π / 3π/2 radians)
            mat2d.rotate(matrix, matrix, angle);
            // Translate
            mat2d.translate(matrix, matrix, [piece.x, piece.z]);
            // Update piece position
            piece.update(roundToDecimal(matrix[4], 1), piece.y, roundToDecimal(matrix[5], 1));
            // Update faces position
            piece.updateFaces('y', angle);
        }
    });
};

/**
 * Turn pieces around Z axis
 * @param pieces - Array of pieces to turn
 * @param angle - Angle to turn (in radians)
 * @param layerIndexes - Indexes of layers to turn
 *
 * @example
 * const pieces: Piece[] = [new Piece(1, 0, 0, p), new Piece(0, 1, 0, p)];
 * turnZ(pieces, Math.PI / 2, [1]);
 */
export const turnZ = (pieces: Piece[], angle: number, layerIndexes: number[]) => {
    pieces.forEach(piece => {
        if (layerIndexes.includes(piece.z)) {
            // Create rotation matrix for a turn around Z axis
            let matrix = mat2d.create();
            // Rotate 90 / 180 / 270 degrees (π/2 / π / 3π/2 radians)
            mat2d.rotate(matrix, matrix, angle);
            // Translate
            mat2d.translate(matrix, matrix, [piece.x, piece.y]);
            // Update piece position
            piece.update(roundToDecimal(matrix[4], 1), roundToDecimal(matrix[5], 1), piece.z);
            // Update faces position
            piece.updateFaces('z', angle);
        }
    });
};
