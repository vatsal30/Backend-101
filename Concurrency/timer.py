import time
import threading
from queue import PriorityQueue
from typing import Callable

class Task:
    def __init__(self, task_id: int, function: Callable, delay: float) -> None:
        self.task_id = task_id
        self.function = function
        self.scheduled_time = time.time() + delay

    def run(self):
        try:
            print(f"Task {self.task_id} started.")
            self.function()
            print(f"Task {self.task_id} completed.")
        except Exception as e:
            print(f"Task {self.task_id} failed with error: {e}")

    def __lt__(self, other):
        # PriorityQueue requires the less-than operator, prioritize by time
        return self.scheduled_time < other.scheduled_time

class TimeScheduler:
    def __init__(self):
        self.task_queue = PriorityQueue()
        self.task_lock = threading.Lock()
        self.condition = threading.Condition(self.task_lock)
        self.task_counter = 0
        self.shutdown_flag = False
        self.worker = threading.Thread(target=self._scheduler)
        self.worker.start()
        
    def _scheduler(self):
        while True:
            with self.task_lock:
                if self.shutdown_flag and self.task_queue.empty():
                    break

                if self.task_queue.empty():
                    self.condition.wait() 

                next_task: Task = self.task_queue.queue[0]
                current_time = time.time()

                if next_task.scheduled_time <= current_time:
                    task = self.task_queue.get()
                    worker_thread = threading.Thread(target=task.run)
                    worker_thread.start()
                    worker_thread.join()
                else:
                    wait_time = next_task.scheduled_time - current_time
                    self.condition.wait(timeout=wait_time)
                
    def schedule_task(self, function: Callable, delay: float):
        with self.task_lock:
            self.task_counter += 1
            task = Task(self.task_counter, function, delay)
            self.task_queue.put(task)
            print(f"Task {task.task_id} scheduled for {delay} seconds.")
            self.condition.notify()
    
    def shutdown(self):
        """Shutdown the scheduler gracefully, allowing tasks to finish."""
        with self.task_lock:
            self.shutdown_flag = True
            self.condition.notify_all()

        self.worker.join()

def task():
    print(f"task executed at {time.time()}")
 
if __name__ == "__main__":
    print(f"Scheduler is started {time.time()}")

    scheduler = TimeScheduler()
    scheduler.schedule_task(task, delay=10)
    scheduler.schedule_task(task, delay=4)
    scheduler.schedule_task(task, delay=6)

    scheduler.shutdown()
