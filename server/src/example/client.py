import asyncio
import json
import logging
import sys

import requests
import websockets

# Example client configuration
HOST = "127.0.0.1"
PORT = 8080
SERVER_URL = f"http://{HOST}:{PORT}"
WEBSOCKET_URL = f"ws://{HOST}:{PORT}/ws"

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
    response = requests.get(f"{SERVER_URL}/token", headers={"x-api-key": API_KEY}, timeout=5)
    token = response.json()["token"]

    # Connect to WebSocket
    async with websockets.connect(f"{WEBSOCKET_URL}?token={token}") as ws:
        logging.info(f"Connected as {ROLE}")

        async def receiver():
            """
            Receive messages from the WebSocket server.
            Handles incoming messages and logs them. Handles connection closure.
            """

            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    logging.info(f"Received: {data}")
                    print_prompt()
                except websockets.ConnectionClosed:
                    logging.info("Connection closed")
                    exit(1)

        async def sender():
            """
            Send messages to the WebSocket server based on user input.
            Handles 'exit' command to terminate the connection.
            """

            while True:
                msg = await asyncio.to_thread(input, PROMPT)
                if msg.lower() == "exit":
                    break
                await ws.send(json.dumps(msg))

        async def pinger():
            """
            Send periodic pings to keep the WebSocket connection alive.
            Logs the success of each ping.
            """

            while True:
                await asyncio.sleep(30)
                try:
                    pong = await ws.ping()
                    await pong
                    logging.info("Ping successful")
                    print_prompt()
                except websockets.ConnectionClosed:
                    logging.info("Connection closed during ping")
                    break

        # Start receiver, sender, and pinger tasks
        receiver_task = asyncio.create_task(receiver())
        sender_task = asyncio.create_task(sender())
        pinger_task = asyncio.create_task(pinger())

        # Wait for sender to finish
        await sender_task

        # Cancel other tasks and close connection
        receiver_task.cancel()
        pinger_task.cancel()
        await ws.close()
        logging.info("Disconnected")


if __name__ == "__main__":
    asyncio.run(main())
