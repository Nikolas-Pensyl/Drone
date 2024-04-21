import asyncio
import websockets
import cv2
import numpy as np
import base64

async def receive_video():
    uri = "ws://10.42.0.1:8766"
    async with websockets.connect(uri) as websocket:
        try:
            while True:
                # Receive the base64 encoded frame from the server
                base64_frame = await websocket.recv()

                # Decode base64 and convert to numpy array
                frame_data = base64.b64decode(base64_frame)
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Display the received frame
                cv2.imshow('Video Stream', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except websockets.ConnectionClosed:
            print("Server disconnected.")

# Start the WebSocket client
asyncio.get_event_loop().run_until_complete(receive_video())
