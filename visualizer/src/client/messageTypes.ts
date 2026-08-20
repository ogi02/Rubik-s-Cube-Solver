/**
 * Message types exchanged over the WebSocket connection.
 *
 * @example
 * MESSAGE_TYPES.CUBE_STATE // "cube_state"
 */
export const MESSAGE_TYPES = {
    CUBE_STATE: "cube_state",
    APPLY_MOVES: "apply_moves",
    DISCONNECT: "disconnect",
} as const;

/**
 * Union of all valid message type string literals.
 *
 * @example
 * const type: MessageType = MESSAGE_TYPES.CUBE_STATE;
 */
export type MessageType = typeof MESSAGE_TYPES[keyof typeof MESSAGE_TYPES];

/**
 * Names of the six sides of a cube.
 *
 * @example
 * CUBE_SIDES.includes("UP"); // true
 */
export const CUBE_SIDES = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'FRONT', 'BACK'] as const;

/**
 * Union of all valid cube side names.
 *
 * @example
 * const side: CubeSide = "UP";
 */
export type CubeSide = typeof CUBE_SIDES[number];

/**
 * Payload describing the full state of a cube.
 *
 * @example
 * const cubeState: CubeState = { dimensions: 3, state: { UP: ["W"], ... } };
 */
export interface CubeState {
    dimensions: number;
    state: Record<CubeSide, string[]>;
}

/**
 * Message sent by the solver to set up the cube with a given state.
 *
 * @example
 * const message: CubeStateMessage = { type: MESSAGE_TYPES.CUBE_STATE, data: cubeState };
 */
export interface CubeStateMessage {
    type: typeof MESSAGE_TYPES.CUBE_STATE;
    data: CubeState;
}

/**
 * Message sent by the solver to apply a series of moves to the cube.
 *
 * @example
 * const message: ApplyMovesMessage = { type: MESSAGE_TYPES.APPLY_MOVES, data: { moves: ["U", "R'"] } };
 */
export interface ApplyMovesMessage {
    type: typeof MESSAGE_TYPES.APPLY_MOVES;
    data: {
        moves: string[];
    };
}

/**
 * Message sent by either client to signal a graceful disconnect. Never relayed by the server.
 *
 * @example
 * const message: DisconnectMessage = { type: MESSAGE_TYPES.DISCONNECT };
 */
export interface DisconnectMessage {
    type: typeof MESSAGE_TYPES.DISCONNECT;
}

/**
 * Union of the messages the visualizer receives from the server.
 *
 * @example
 * const handle = (message: ServerMessage) => { ... };
 */
export type ServerMessage = CubeStateMessage | ApplyMovesMessage;
