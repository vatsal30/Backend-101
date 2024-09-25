import threading
import time


lock_a = threading.Lock()
lock_b = threading.Lock()

def function_a():
  print("Inside function_a and trying to acquire lock_a")
  with lock_a:
    print("Inside function_a and lock_a acquired")
    time.sleep(1)
    print("Inside function_a and trying to acquire lock_b")
    with lock_b:
      print("Inside function_a and lock_b acquired")
  
def function_b():
  print("Inside function_b and trying to acquire lock_a")
  with lock_a:
    print("Inside function_b and lock_a acquired")
    time.sleep(1)
    print("Inside function_b and trying to acquire lock_b")
    with lock_b:
      print("Inside function_b and lock_b acquired")
  
thread1 = threading.Thread(target=function_a)
thread2 = threading.Thread(target=function_b)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
    
  