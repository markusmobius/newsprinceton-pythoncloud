class HashSet:
    def __init__(self):
        self._data = {}

    def Add(self, value):
        self._data[value] = True

    def Remove(self, value):
        if value in self._data:
            del self._data[value]

    def Contains(self, value):
        return value in self._data

    def __len__(self):
        return len(self._data)

    def Count(self):
        return self.__len__()

    def __str__(self):
        return "{" + ", ".join(str(item) for item in self._data.keys()) + "}"
    
    def First(self):
        if len(self._data) == 0:
            raise Exception("Hash set is empty")
        return next(iter(self._data))