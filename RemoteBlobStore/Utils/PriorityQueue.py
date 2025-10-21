class PriorityQueue:
    def __init__(self):
        self.H = []
        self.HIndex = {}

    def parent(self, i):
        return (i - 1) // 2
    
    def leftChild(self, i):
        return ((2 * i) + 1)
    
    def rightChild(self, i):
        return ((2 * i) + 2)
    
    def shiftUp(self, i):
        while (i > 0) and (self.H[self.parent(i)][1] < self.H[i][1]):
            self.swap(self.parent(i), i)
            i = self.parent(i)

    def shiftDown(self, i):
        maxIndex = i
        l = self.leftChild(i)
        if (l < len(self.H)) and (self.H[l][1] > self.H[maxIndex][1]):
            maxIndex = l
        r = self.rightChild(i)
        if (r < len(self.H)) and (self.H[r][1] > self.H[maxIndex][1]):
            maxIndex = r
        if i != maxIndex:
            self.swap(i, maxIndex)
            self.shiftDown(maxIndex)

    def swap(self, i, j):
        temp = self.H[i]
        self.H[i] = self.H[j]
        self.H[j] = temp
        self.HIndex[temp[0]] = j
        self.HIndex[self.H[i][0]] = i

    def Insert(self, ID, priority):
        size = len(self.H)
        self.H.append([ID, priority])
        self.HIndex[ID] = size
        self.shiftUp(size)

    def ExtractMax(self):
        result = self.H[0][0]
        self.H[0] = self.H[-1]
        self.H.pop()
        del self.HIndex[result]
        if len(self.H) > 0:
            self.HIndex[self.H[0][0]] = 0
        self.shiftDown(0)
        return result
    
    def ChangePriority(self, ID, p):
        i = self.HIndex[ID]
        oldp = self.H[i][1]
        self.H[i] = [self.H[i][0], p]
        if p > oldp:
            self.shiftUp(i)
        else:
            self.shiftDown(i)

    def GetMax(self):
        return self.H[0][1]
    
    def Remove(self, ID):
        i = self.HIndex[ID]
        self.H[i] = [self.H[i][0], self.GetMax() + 1]
        self.shiftUp(i)
        self.ExtractMax()

    def Count(self):
        return len(self.H)