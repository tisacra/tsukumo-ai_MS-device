from . import detect_bird
from multiprocessing import Process, Event, Queue, Pipe
import signal


#親プロセスからのリクエストを受け取る
GET_BIRD_REC = "get_bird_rec"


Conn = None

birdnet_start_event = Event()
birdnet_parent_conn, birdnet_child_conn = Pipe()

def listen(arg1, arg2):
    request = Conn.recv()
    if request == GET_BIRD_REC:
        birdnet_parent_conn.send(detect_bird.GET_ACCUMULATIVE_REC)
        data = birdnet_parent_conn.recv()
        payload = {}
        payload["BirdNET_rec"] = data
        #print("birdNET : ", payload)
        Conn.send(payload)

    else:
        pass

def Monitoring(conn, start_event):
    global Conn
    print("Monitoring system is starting...")
    Conn = conn
    detect_bird.setup()
    p_birdNET = Process(target=detect_bird.start_analyze, args=(birdnet_child_conn, birdnet_start_event))
    p_birdNET.deamon = True
    p_birdNET.start()

    print(" - Monitoring system is ready...")
    conn.send("M1")
    start_event.wait()

    print(" - Monitoring system start.")

    signal.signal(signal.SIGALRM, listen)
    signal.setitimer(signal.ITIMER_REAL, 0.5, 0.5)
    print("Starting birdNET analysis...")
    birdnet_start_event.set()
    
    while True:
        request = conn.recv()
        if request == "terminate":
            detect_bird.close()
            p_birdNET.terminate()
            break
    
    print(" - Monitoring system is terminated.")
    