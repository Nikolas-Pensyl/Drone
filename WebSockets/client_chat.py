import asyncio
import websockets

async def send_message():
    uri = "ws://192.168.4.1:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            # Send a message to the server
            message = input("Enter your message: ")
            await websocket.send(message)

            # Receive and print the response from the server
            response = await websocket.recv()
            print(f"Server response: {response}")
            websocket.recv()

# Start the WebSocket client
asyncio.get_event_loop().run_until_complete(send_message())
