import time
import multiprocessing as mp
from Controller import controller_main
from Video import video_main
 
if __name__ =="__main__":
    controller_process = mp.Process(target=controller_main, args=())
    video_process = mp.Process(target=video_main, args=())
   
    
    try:
        controller_process.start()
        video_process.start()

        controller_process.join()
        video_process.join()
    
    except Exception as e:
        print(e)
        print("Closing")

    finally:
        controller_process.kill()
        video_process.kill()
    
    print("Done!")
