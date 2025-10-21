import collections
import threading


class ConcurrentDictionary:
    def __init__(self):
        self._data = collections.defaultdict()
        self._lock = threading.Lock()

    def __getitem__(self, key):
        with self._lock:
            return self._data[key]

    def __setitem__(self, key, value):
        with self._lock:
            self._data[key] = value

    def __delitem__(self, key):
        with self._lock:
            del self._data[key]

    def __len__(self):
        with self._lock:
            return len(self._data)

    def ContainsKey(self, key):
        with self._lock:
            return True if key in self._data else False
        
    def TryAdd(self, key, value):
        with self._lock:
            if key in self._data:
                return False
            else:
                self._data[key] = value
                return True
            
    def TryRemove(self, key):
        with self._lock:
            if key in self._data:
                value = self._data[key]
                del self._data[key]
                return True, value
            else:
                return False, None