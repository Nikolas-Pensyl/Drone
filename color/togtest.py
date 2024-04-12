import cv2
from picamera2 import Picamera2

cv2.startWindowThread()

picam2 = Picamera2()
print('here')
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888',"size": (640,480)}))
picam2.start()
print('2')

while True:
    im=picam2.capture_array()
    #print (im)
    grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    #print (grey)
    cv2.imshow("Camera", im)
    cv2.waitKey(1)