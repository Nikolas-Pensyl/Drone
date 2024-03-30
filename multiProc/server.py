
import asyncio
import websockets

async def server_handler(websocket, path, server_queue, output_queue):
    print(path)
    print("Testing")
    while True:
        # Wait for a message from the client
        message = await websocket.recv()
        if not server_queue.full():
            server_queue.put(message)

        # Send a response back to the client
        
        if not output_queue.empty():
            await websocket.send(output_queue.get())
        else:
            await websocket.send("ready")

def server_starter(server_queue, output_queue):
    # Start the WebSocket server
    start_server = websockets.serve(server_handler, "10.42.0.1", 8765, server_queue, output_queue)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

#server_starter()
