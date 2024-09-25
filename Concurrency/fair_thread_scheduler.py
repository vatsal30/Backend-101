## Reentrant lock custom implementation
import threading
from collections import deque
import time
import random

class LegalReentrantLock():
  def __init__(self):
    self.mutex = threading.Lock()
    self.lock_owner = None
    self.thread_counter = 0
    self.thread_queue = deque()
    self.condition = threading.Condition(self.mutex)

  def acquire(self):
    current_thread = threading.current_thread()

    with self.mutex:
      if self.lock_owner == current_thread:
        self.thread_counter += 1
        return
      
      thread_event = threading.Event() 
      self.thread_queue.append((current_thread, thread_event))
    
      while self.thread_queue[0][0] != current_thread or self.lock_owner is not None:
        self.mutex.release()
        thread_event.wait()
        self.mutex.acquire()
      
      self.lock_owner = current_thread
      self.thread_counter = 1

  def release(self):
    current_thread = threading.current_thread()

    with self.mutex:
      if self.lock_owner != current_thread:
        raise RuntimeError("Cannot release a lock that isn't owned by the current thread")
      self.thread_counter -= 1
      if self.thread_counter == 0:
        self.lock_owner = None
        self.thread_queue.popleft()
        if self.thread_queue:
          self.thread_queue[0][1].set()
  

lock = LegalReentrantLock()

def thread_func(thread_id):
  print(f"Thread {thread_id} trying to acquire the lock")
  lock.acquire()
  print(f"Thread {thread_id} acquired the lock successfully")
  time.sleep(1)
  print(f"Thread {thread_id} trying to acquire the lock again")
  lock.acquire()
  print(f"Thread {thread_id} acquired the lock again successfully")
  time.sleep(1)
  lock.release()
  print(f"Thread {thread_id} released the one instance of lock")
  lock.release()
  print(f"Thread {thread_id} released lock completely")

threads = []
for i in range(random.randint(3,5)):
  thread = threading.Thread(target=thread_func, args=(i,))
  threads.append(thread)
  thread.start()

for thread in threads:
  thread.join()
