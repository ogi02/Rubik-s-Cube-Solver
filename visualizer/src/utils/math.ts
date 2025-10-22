/**
 * Rounds a number to a specified number of decimal places.
 * @param num - The number to be rounded
 * @param decimalPlaces - The number of decimal places to round to
 * @returns The rounded number
 *
 * @example
 * roundToDecimal(3.14159, 2); // returns 3.14
 * roundToDecimal(2.71828, 3); // returns 2.718
 */
export const roundToDecimal = (num: number, decimalPlaces: number): number => {
    const factor = Math.pow(10, decimalPlaces);
    return Math.round(num * factor) / factor;
}
