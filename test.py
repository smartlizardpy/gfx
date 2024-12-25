import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8081"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")

            # Example: Sending a message
            message = ' {"type": "ticker","action": "hide"} '
            print(f"Sending: {message}")
            await websocket.send(message)

            # Example: Receiving a response
            response = await websocket.recv()
            print(f"Received: {response}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the WebSocket tester
if __name__ == "__main__":
    asyncio.run(test_websocket())
