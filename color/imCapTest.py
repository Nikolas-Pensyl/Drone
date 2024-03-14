import time
from picamera2 import Picamera2,Preview
from picamera2.encoders import H264Encoder, Quality
import cv2
picam=Picamera2()
picam.configure(picam.create_video_configuration())
picam.start()
cv2.startWindowThread()
encoder = H264Encoder()
picam.start_recording(encoder,'test.h264',quality=Quality.HIGH)
time.sleep(10)
picam.stop_recording()
while True:
    
    time.sleep(1)
    picam.capture_file("test.jpg")
    print("start")
    im = picam.capture_array()
    time.sleep(0.1)
    print("here")
    gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    print("next")
    cv2.namedWindow("frame",cv2.WINDOW_AUTOSIZE)
    print("next2")
    cv2.imshow("frame", gray)
    print("showIM")
    cv2.waitKey(1)
