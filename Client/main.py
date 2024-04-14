import time
import multiprocessing as mp
from Controller import controller_main
from Video import video_main
 
if __name__ =="__main__":
    controller_queue = mp.Queue()   

    controller_process = mp.Process(target=controller_main, args=(controller_queue,))
    video_process = mp.Process(target=video_main, args=())
    
    try:
        controller_process.start()
        video_process.start()

        while True:
            if not controller_queue.empty():
                print(controller_queue.get())

        
    
    except Exception as e:
        print(e)
        print("Closing")

    finally:
        
        controller_process.kill()
        video_process.kill()
    
    print("Done!")
