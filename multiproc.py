import time
import multiprocessing as mp

def lidar_main(lq):
    while True:
        if not lq.full():
            lq.put("Test")

def server_starter(sq, lq):
    while True:
        if not lq.empty():
            print(lq.get())

 
if __name__ =="__main__":
    try:
        lidar_queue = mp.Queue()
        server_queue = mp.Queue()
        camera_queue = mp.Queue()
        output_queue = mp.Queue()

        lidar_process = mp.Process(target=lidar_main, args=(lidar_queue, ))
        server_process = mp.Process(target=server_starter, args=(server_queue, lidar_queue, ))
        #camera_process = mp.Process(target=start_camera, args=(camera_queue))
        #drone_process  = mp.Process(target=start_drone, args=(lidar_queue, server_queue, camera_queue, output_queue))
    
        lidar_process.start()
        server_process.start()
        #camera_process.start()
        #drone_process.start()

        lidar_process.join()
        server_process.join()
        #camera_process.join()
        #drone_process.join()
    
    except:
        lidar_process.kill()
        server_process.kill()
        #camera_process.kill()
        #drone_process.kill()
    
 
    print("Done!")
