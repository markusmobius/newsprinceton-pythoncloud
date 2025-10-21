from collections import deque

class Queue:
    def __init__(self):
        self.queue = deque()

    def Enqueue(self, item):
        self.queue.append(item)

    def Dequeue(self):
        return self.queue.popleft()
    
    def Count(self):
        return len(self.queue)