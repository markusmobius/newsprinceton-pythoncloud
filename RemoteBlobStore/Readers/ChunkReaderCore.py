import struct
import threading

from RemoteBlobStore.__BufferStore.BufferStream import BufferStream
from RemoteBlobStore.Utils.ConcurrentDictionary import ConcurrentDictionary 


class ChunkReaderCore:
    def __init__(self, buffer):
        self.buffer = buffer
        self.readerIDs = ConcurrentDictionary()
        self.readerIDsLock = threading.Lock()

    def RegisterReader(self, readerGuid):
        if self.readerIDs.ContainsKey(readerGuid):
            return self.readerIDs[readerGuid]
        else:
            with self.readerIDsLock:
                count = len(self.readerIDs)
                if count >= self.buffer.GetCursorCount():
                    raise Exception(f"max reader count per memory buffer is {self.buffer.GetCursorCount()}")
                self.readerIDs.TryAdd(readerGuid, count)
                return count

    def MoveCursor(self, workerGUID, offset):
        self.buffer.MoveCursor(self.RegisterReader(workerGUID), offset)

    def GetCursor(self, workerGUID):
        return self.buffer.GetCursor(self.RegisterReader(workerGUID))

    def ReadInt32(self, workerGUID):
        readerID = self.RegisterReader(workerGUID)
        num = 0
        v = self.buffer.ReadByte(readerID)
        while v >= 0x80:
            num = (num << 7) + (v & 0x7F)
            v = self.buffer.ReadByte(readerID)
        num = (num << 7) + v
        return num if num < 0x80000000 else num - 0x100000000


    def ReadInt64(self, workerGUID):
        readerID = self.RegisterReader(workerGUID)
        num = 0
        v = self.buffer.ReadByte(readerID)
        while v >= 0x80:
            num = (num << 7) + (v & 0x7F)
            v = self.buffer.ReadByte(readerID)
        num = (num << 7) + v
        return num

    def ReadString(self, workerGUID):
        readerID = self.RegisterReader(workerGUID)
        length = self.ReadInt32(workerGUID)
        if length == -1:
            return None
        else:
            return self.buffer.ReadString(readerID, length)

    def ReadStringStream(self, workerGUID):
        readerID = self.RegisterReader(workerGUID)
        length = self.ReadInt32(workerGUID)
        if length == -1:
            return None
        else:
            return BufferStream(self.buffer.ReadBytes(readerID, length))

    def ReadStringDummy(self, workerGUID):
        length = self.ReadInt32(workerGUID)
        if length != -1:
            self.MoveCursor(workerGUID, self.GetCursor(workerGUID) + length)

    def ReadSingle(self, workerGUID):
        readerID = self.RegisterReader(workerGUID)
        offset, arr = self.buffer.ReadByteArrayDirect(readerID, 4)
        return struct.unpack_from('f', arr, offset)[0]

    def ReadDouble(self, workerGUID):
        readerID = self.RegisterReader(workerGUID)
        offset, arr = self.buffer.ReadByteArrayDirect(readerID, 8)
        return struct.unpack_from('d', arr, offset)[0]

    def ReadSimpleLong(self, workerGUID):
        readerID = self.RegisterReader(workerGUID)
        offset, arr = self.buffer.ReadByteArrayDirect(readerID, 8)
        return struct.unpack_from('q', arr, offset)[0]
    
    def ReadSimpleInt32(self, workerGUID):
        readerID = self.RegisterReader(workerGUID)
        offset, arr = self.buffer.ReadByteArrayDirect(readerID, 4)
        return struct.unpack_from('i', arr, offset)[0]

    def ReadBytes(self, workerGUID, length):
        readerID = self.RegisterReader(workerGUID)
        return self.buffer.ReadBytes(readerID, length)

    def GetDiagnostics(self, workerGUID):
        readerID = self.RegisterReader(workerGUID)
        return self.buffer.GetDiagnostics(readerID)

    def Dispose(self):
        self.buffer = None