from multiprocessing import Process
import time

def print_square(numbers):
	while(1):
		for n in numbers:
			time.sleep(0.5) 
			print(f'Square: {n * n}')

def print_cube(numbers):
    for n in numbers:
        time.sleep(1.5)
        print(f'Cube: {n * n * n}')

if __name__ == "__main__":
    numbers = [2, 3, 4, 5]

    p1 = Process(target=print_square, args=(numbers,))
    p2 = Process(target=print_cube, args=(numbers,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Done!")
