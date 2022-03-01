import random
import time

arr_len = 10
arr = [0 for i in range(arr_len)]


while True:
    arr.insert(0, random.randint(50, 100))
    arr.pop(-1)
    print(arr)
    time.sleep(0.50)