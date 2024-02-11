import asyncio
import websockets

async def server_handler(websocket, path):
    while True:
        # Wait for a message from the client
        message = await websocket.recv()
        print(f"Client: {message}")

        # Send a response back to the client
        response = f"Server received: {message}"
        await websocket.send(response)

# Start the WebSocket server
start_server = websockets.serve(server_handler, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
