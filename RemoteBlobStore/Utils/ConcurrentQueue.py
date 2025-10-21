import threading
from RemoteBlobStore.Utils.Queue import Queue

class ConcurrentQueue(Queue):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

    def Enqueue(self, item):
        with self.lock:
            super().Enqueue(item)

    def Dequeue(self):
        with self.lock:
            return super().Dequeue()
        
    def Count(self):
        with self.lock:
            return super().Count()
        
    def TryDequeue(self):
        with self.lock:
            if super().Count() == 0:
                return None, False
            else:
                return super().Dequeue(), True
        
    