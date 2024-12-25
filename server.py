import asyncio
import websockets
import json

# Store connected WebSocket clients
connected_clients = set()

# WebSocket handler
async def websocket_handler(websocket, path):
    print("A client has connected.")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            # Forward the message to all connected clients
            await broadcast(message)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client disconnected: {e}")
    finally:
        connected_clients.remove(websocket)

# Broadcast a message to all connected clients
async def broadcast(message):
    if connected_clients:
        await asyncio.gather(*(client.send(message) for client in connected_clients))

# Main server function
async def main():
    print("Starting WebSocket server on ws://localhost:8081")
    server = await websockets.serve(websocket_handler, "localhost", 8081)
    await server.wait_closed()

# Run the WebSocket server
asyncio.run(main())
