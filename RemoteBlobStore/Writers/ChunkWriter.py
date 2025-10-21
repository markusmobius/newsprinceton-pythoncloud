from RemoteBlobStore.__BufferStore.BufferSet import BufferSet
from RemoteBlobStore.IntZip import IntZip


class ChunkWriter:
    def __init__(self, buffer):
        self.buffer = buffer
        self.intzip = IntZip()

    def Load(self, buffer):
        self.buffer = buffer

    def GetCursor(self):
        return self.buffer.GetCursor()

    def WriteBytes(self, setOrArr, offset=0, length=-1):
        if isinstance(setOrArr, BufferSet):
            self.buffer.WriteBytes(setOrArr)
        elif isinstance(setOrArr, bytearray):
            if length == -1:
                length = len(setOrArr)
            self.buffer.WriteBytes(setOrArr, offset, length)

    def Write(self, intOrString):
        # print(intOrString, type(intOrString))
        if isinstance(intOrString, int):
            number = intOrString
            offset, length = self.intzip.compress(number)
            self.WriteBytes(self.intzip.buffer, offset=offset, length=length)
        
        elif isinstance(intOrString, str):
            s = intOrString
            if s == None:
                self.Write(-1)
            else:
                arr = bytearray(s.encode('utf-8'))
                length = len(arr)
                self.Write(length)
                self.WriteBytes(arr)

    