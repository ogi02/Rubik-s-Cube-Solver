# Python imports
import asyncio
import json
import logging
import sys

import requests
import websockets

# Example client configuration
HOST = "127.0.0.1"
PORT = 8080
SECURE = False  # Set to True if server uses HTTPS/WSS
SERVER_URL = f"http{'s' if SECURE else ''}://{HOST}:{PORT}"
WEBSOCKET_URL = f"ws{'s' if SECURE else ''}://{HOST}:{PORT}/ws"

# Example client role - choose either "solver" or "visualizer"
ROLE = "solver"

# Example API key - replace with your actual API key
API_KEY = "example-api-key"

# Example logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="[Client] %(asctime)s [%(levelname)s] %(filename)s:%(lineno)d — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Example prompt
PROMPT = "Enter message to send (or 'exit' to quit):\n"


def print_prompt():
    """
    Print the input prompt. Called after logging messages to keep the prompt visible.
    """

    sys.stdout.write(f"\r{PROMPT}")
    sys.stdout.flush()


async def main():
    """
    Main function to run the example client.
    """

    # Get JWT token from the server
    try:
        response = requests.get(f"{SERVER_URL}/token", headers={"x-api-key": API_KEY}, timeout=5)
        response.raise_for_status()
        response_json = response.json()
        token = response_json["token"]
    except requests.RequestException as e:
        logging.error(f"Failed to get token from server: {e}")
        sys.exit(1)
    except (ValueError, KeyError) as e:
        logging.error(f"Invalid response from server when requesting token: {e}")
        sys.exit(1)

    # Connect to WebSocket
    async with websockets.connect(f"{WEBSOCKET_URL}?token={token}") as ws:
        logging.info(f"Connected as {ROLE}")

        async def receiver():
            """
            Receive messages from the WebSocket server.
            Handles incoming messages and logs them. Handles connection closure.
            """

            try:
                while True:
                    msg = await ws.recv()
                    try:
                        data = json.loads(msg)
                        logging.info(f"Received: {data}")
                        print_prompt()
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to decode JSON message: {msg!r} — {e}")
            except websockets.ConnectionClosed:
                logging.info("Connection closed during receive")
            except asyncio.CancelledError:
                logging.info("Receiver task cancelled")

        async def sender():
            """
            Send messages to the WebSocket server based on user input.
            Handles 'exit' command to terminate the connection.
            """

            try:
                while True:
                    msg = await asyncio.to_thread(input, PROMPT)
                    if msg.lower() == "exit":
                        break
                    await ws.send(json.dumps(msg))
            except websockets.ConnectionClosed:
                logging.info("Connection closed during send")
            except asyncio.CancelledError:
                logging.info("Sender task cancelled")

        async def pinger():
            """
            Send periodic pings to keep the WebSocket connection alive.
            Logs the success of each ping.
            """

            try:
                while True:
                    await asyncio.sleep(30)
                    pong = await ws.ping()
                    await pong
                    logging.info("Ping successful")
                    print_prompt()
            except websockets.ConnectionClosed:
                logging.info("Connection closed during ping")
            except asyncio.CancelledError:
                logging.info("Ping task cancelled")

        # Start receiver, sender, and pinger tasks
        receiver_task = asyncio.create_task(receiver())
        sender_task = asyncio.create_task(sender())
        pinger_task = asyncio.create_task(pinger())
        tasks = {receiver_task, sender_task, pinger_task}

        # Wait until any task completes
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # Cancel all remaining tasks
        for task in pending:
            task.cancel()

        # Wait for cancellation to finish
        await asyncio.gather(*pending, return_exceptions=True)

        # Close WebSocket connection
        await ws.close()

    logging.info("Disconnected")


if __name__ == "__main__":
    asyncio.run(main())
