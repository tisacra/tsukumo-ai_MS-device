from multiprocessing import Process, Event, Queue
import time


def print_square(numbers, start_event, data_queue):
    start_event.wait()
    for n in numbers:
        time.sleep(0.5) 
        result = n * n
        print(f'Square: {result}')
        data_queue.put(('Square', result))

def print_cube(numbers, start_event, data_queue):
    start_event.wait()
    for n in numbers:
        time.sleep(0.5)  
        result = n * n * n
        print(f'Cube: {result}')
        data_queue.put(('Cube', result))

if __name__ == "__main__":
    numbers = [2, 3, 4, 5]

    start_event = Event()
    data_queue = Queue()

    p1 = Process(target=print_square, args=(numbers, start_event, data_queue))
    p2 = Process(target=print_cube, args=(numbers, start_event, data_queue))

    p1.start()
    p2.start()

    time.sleep(1)
    print("Starting tasks...")
    start_event.set()  

    p1.join()
    p2.join()

    while not data_queue.empty():
        item = data_queue.get()
        print(f"Processed {item[0]}: {item[1]}")

    print("Done!")
