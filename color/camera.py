import cv2
import numpy as np
from picamera2 import Picamera2,Preview
import time

def start_camera(camera_queue):

    cv2.startWindowThread()
    lower_range=np.array([30,99,133]) #Neon Yellow upper_range=np.array([80,255,255]) picam2 = Picamera2()
    camera_queue.put("Starting")
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888',"size": (640,480)}))
    picam2.start()


    x=250   #This is the minimum area an object needs to be in order to track. Detects our object up to 23 feet away
    cent_x = 256 # this is the top left corner of our center bounds used to determine when to move the drone
    cent_y = 192 # this is the top left corner of our center bounds
    cent_w = 128 # determines how long center bounding rectangle is
    cent_h = 96 #determines how tall "        "        "

    camera_queue.put(['search','search','search'])

    while True:

        frame=picam2.capture_array()

        frame=cv2.resize(frame,(640,480))
        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        mask=cv2.inRange(hsv,lower_range,upper_range)
    _,mask1=cv2.threshold(mask,254,255,cv2.THRESH_BINARY)
    cnts,_=cv2.findContours(mask1,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for c in cnts:
        
        if cv2.contourArea(c)>x:
            #print(cv2.contourArea(c))
            x,y,w,h=cv2.boundingRect(c)
            obj_middle = (x+w/2,y+h/2)
            if obj_middle[0] < cent_x:
                output[0] = 'LEFT'
            elif obj_middle[0] >cent_x+cent_h:
                output[0] = 'RIGHT'
            else:
                output[0] = 'CENTERED'
                
            if obj_middle[1] < cent_y:
                output[1] = 'UP'
            elif obj_middle[1] >cent_y+cent_h:
                output[1] = 'DOWN'
            else:
                output[1] = 'CENTERED'
            
            if cv2.contourArea(c)>1675:     #1675 is a number found during testing to represent the max of avg values of our object at 10 feet away
                output[2] = 'BACK'
            elif cv2.contourArea(c)<1450:     #1450 is a number found as the min average as described above
                output[2] = 'FORWARD'
            else:
                output[2] = 'CENTERED'
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.rectangle(frame,(cent_x,cent_y),(cent_x+cent_w,cent_y+cent_h),(0,0,255),2)
            cv2.putText(frame,("DETECT"),(10,60),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
            
        else:
            output = ['search','search','search']
    print (output)        
    cv2.imshow("FRAME",frame)

    if cv2.waitKey(1)&0xFF==27:
        break
cap.release()
cv2.destroyAllWindows()
