/**
 * Authenticate the client with the server to obtain a token
 *
 * @example
 * await client.authenticate();
 */
export const authenticate = async () : Promise<string> => {
    try {
        // Make a GET request to the authentication endpoint
        const response = await fetch(import.meta.env.VITE_TOKEN_URL, {
            method: "GET",
            headers: {
                "X-API-KEY": import.meta.env.VITE_API_KEY
            }
        });
        // Get the token from the response
        const data = await response.json();
        return data.token;
    } catch (error) {
        throw new Error(`Network or authentication error: ${error instanceof Error ? error.message : String(error)}`);
    }
}
