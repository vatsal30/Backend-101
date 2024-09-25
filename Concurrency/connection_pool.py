import queue
import threading
import time

class Connection:
  def __init__(self, connection_id):
    self.connection_id = connection_id
    self.in_use = False
  
  def connect(self):
    print(f"connection {self.connection_id} opened")
    self.in_use = True
  
  def close(self):
    print(f"connection {self.connection_id} closed")
    self.in_use = False
  

class ConnectionPool:
  def __init__(self, min_conn = 3, max_conn = 5, timeout = 5):
    self.pool = queue.Queue(maxsize=max_conn)
    self.lock = threading.Lock()
    self.min_conn = min_conn
    self.max_conn = max_conn
    self.timeout = timeout
    self.connection_count = 0

    self._initialize_and_fill_pool()
    self._start_min_size_maintainer()

  def _initialize_and_fill_pool(self):
    with self.lock:
      while self.connection_count < self.min_conn:
        connection = self._create_new_connection()
        if connection:
          self.pool.put(connection)
  
  def _create_new_connection(self):
    if self.connection_count < self.max_conn:
      self.connection_count += 1
      connection = Connection(self.connection_count)
      connection.connect()
      return connection
    return None
  
  def _start_min_size_maintainer(self):
    """Start a background thread to maintain the minimum pool size."""
    def maintain_min_size():
        while True:
            with self.lock:
                if self.connection_count < self.max_conn:
                    self._initialize_and_fill_pool()
            time.sleep(2)  # Periodically check every 2 seconds

    maintainer_thread = threading.Thread(target=maintain_min_size, daemon=True)
    maintainer_thread.start()
  
  def get_connection(self):
    try:
      connection = self.pool.get(timeout=self.timeout)
      if connection:
          return connection
    except queue.Empty:
      connection = self._create_new_connection()
      if connection:
          return connection
      else:
          raise RuntimeError("No available connections and pool limit reached")
  
  def release_connection(self, connection):
    if connection:
      print(f"connection {connection.connection_id} is released and put back on queue")
      self.pool.put(connection)

  def close_all_connection(self):
    while not self.pool.empty():
      connection = self.pool.get()
      connection.close()
  
  def __enter__(self):
    """Allow use with 'with' context."""
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    """Release all connections on exit."""
    self.close_all_connections()


def task(pool, thread_id):
    try:
        print(f"Thread {thread_id} trying to get connection")
        # Get a connection from the pool
        connection = pool.get_connection()
        print(f"Thread {thread_id} got connection {connection.connection_id}")

        # Execute thread
        time.sleep(4)

        pool.release_connection(connection)
        print(f"Thread {thread_id} released connection {connection.connection_id}")
    except RuntimeError as e:
        print(f"Thread {thread_id} error: {e}")

pool = ConnectionPool(min_conn=2, max_conn=4)

threads = []
for i in range(5):
    t = threading.Thread(target=task, args=(pool, i+1))
    threads.append(t)
    t.start()

for t in threads:
    t.join()



