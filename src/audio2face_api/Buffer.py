import threading
from queue import Queue, Empty


class Buffer:
    """A thread-safe buffer."""

    def __init__(self):
        self.lock = threading.Lock()
        self.queue = Queue()

    def add(self, data):
        with self.lock:
            self.queue.put(data)

    def remove(self):
        with self.lock:
            try:
                return self.queue.get_nowait()
            except Empty:
                return None

    def flush(self):
        with self.lock:
            items = []
            while not self.queue.empty():
                items.append(self.queue.get_nowait())
            return items

    def get_size_buffer(self):
        with self.lock:
            return self.queue.qsize()
