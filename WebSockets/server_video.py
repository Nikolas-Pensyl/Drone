import asyncio
import cv2
import websockets
import base64

async def video_stream(websocket, path):
    # Open a video capture device (0 is usually the default webcam)
    cap = cv2.VideoCapture(0)

    try:
        while cap.isOpened():
            # Read a frame from the video capture
            ret, frame = cap.read()

            # Encode the frame to JPEG format
            _, encoded_frame = cv2.imencode('.jpg', frame)

            # Convert the encoded frame to base64 for transmission
            base64_frame = base64.b64encode(encoded_frame.tobytes()).decode('utf-8')

            # Send the base64 encoded frame to the client
            await websocket.send(base64_frame)

    except websockets.ConnectionClosed:
        print("Client disconnected.")

    finally:
        cap.release()

# Start the WebSocket server
start_server = websockets.serve(video_stream, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
