import functools
import asyncio
import websockets

async def server_handler(server_queue, output_queue, websocket, path):

    while True:
        # Wait for a message from the client
        message = await websocket.recv()
        if not server_queue.full():
            server_queue.put(message)

        # Send a response back to the client
        if not output_queue.empty():
            await websocket.send(output_queue.get())
        else:
            await websocket.send("")

def server_starter(server_queue, output_queue):
    # Start the WebSocket server
    start_server = websockets.serve(functools.partial(server_handler, server_queue, output_queue), "10.42.1.1", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

#server_starter()
