import time
import numpy as np

arr1 = [i for i in range(10000)]
arr2 = [i % 2 == 0 for i in range(len(arr1))]

t = time.time()
for pavel in range(10000):
    arr3 = arr1.copy()
    arr4 = arr1.copy()
    arr3.sort()
    arr3.reverse()

    for i in arr3:
        if i % 2 == 0:
            arr4.pop(i)
        
print(time.time() - t)

t = time.time()
for pavel in range(10000):  
    arr = np.array(arr1)
    arr = arr[arr2]
print(time.time() - t)




