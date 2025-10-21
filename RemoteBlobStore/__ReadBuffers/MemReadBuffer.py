
from RemoteBlobStore.__BufferStore.BufferSet import *
from RemoteBlobStore.__ReadBuffers._intReadBuffer import DiagnosticData, _intReadBuffer


class MemReadBuffer(_intReadBuffer):
    def __init__(self, set=None, simple=False):
        if set == None:
            self.MemSet = None
            self.cursor = []
        else:
            if isinstance(set, list):
                self.MemSet = BufferSet(set)
                self.createCursors()
            else:
                self.MemSet = set
                if simple:
                    self.cursor = [0, 0]
                else:
                    self.createCursors()

    def createCursors(self):
        self.cursor = [0 for _ in range(1024)]
        if len(self.MemSet.Parts) == 0:
            return
        for i in range(len(self.cursor) // 2):
            if len(self.MemSet.Parts) > 0:
                self.cursor[2 * i + 1] = self.MemSet.Parts[0].Offset

    def GetCursorCount(self):
        return len(self.cursor) // 2
    
    def MoveCursor(self, readerID, offset):
        newCursor = offset
        if offset < 0:
            newCursor = self.MemSet.Length + offset
        cpos = self.MemSet.GetCursor(newCursor)
        self.cursor[readerID * 2] = cpos[0]
        self.cursor[readerID * 2 + 1] = cpos[1]

    def GetCursor(self, readerID):
        return self.MemSet.Parts[self.cursor[readerID * 2]].Cursor + \
            self.cursor[readerID * 2 + 1] - \
            self.MemSet.Parts[self.cursor[readerID * 2]].Offset
    
    def ReadByte(self, readerID):
        if self.cursor[readerID * 2 + 1] - self.MemSet.Parts[self.cursor[readerID * 2]].Offset >= self.MemSet.Parts[self.cursor[readerID * 2]].PartLength:
            self.cursor[readerID * 2] += 1
            self.cursor[readerID * 2 + 1] = self.MemSet.Parts[self.cursor[readerID * 2]].Offset
        b = self.MemSet.Parts[self.cursor[readerID * 2]].Part.data[self.cursor[readerID * 2 + 1]]
        self.cursor[readerID * 2 + 1] += 1
        return b
    
    def ReadByteArrayDirect(self, readerID, length):
        if self.cursor[readerID * 2 + 1] - self.MemSet.Parts[self.cursor[readerID * 2]].Offset + length < self.MemSet.Parts[self.cursor[readerID * 2]].PartLength:
            offset = self.cursor[readerID * 2 + 1]
            self.cursor[readerID * 2 + 1] += length
            return offset, self.MemSet.Parts[self.cursor[readerID * 2]].Part.data
        else:
            #! arr = [None for _ in range(length)]
            arr = bytearray(length)
            arr_mv = memoryview(arr)
            offset = 0
            while self.cursor[readerID * 2 + 1] - self.MemSet.Parts[self.cursor[readerID * 2]].Offset + length > self.MemSet.Parts[self.cursor[readerID * 2]].PartLength:
                sublength = self.MemSet.Parts[self.cursor[readerID * 2]].PartLength - self.cursor[readerID * 2 + 1] + self.MemSet.Parts[self.cursor[readerID * 2]].Offset
                sourceArray = memoryview(self.MemSet.Parts[self.cursor[readerID * 2]].Part.data)
                sourceIndex = self.cursor[readerID * 2 + 1]
                """ #!
                for i in range(sublength):
                    arr[i + offset] = sourceArray[i + sourceIndex]
                """
                arr_mv[offset : offset + sublength] = sourceArray[sourceIndex : sourceIndex + sublength]
                offset += sublength
                self.cursor[readerID * 2] += 1
                self.cursor[readerID * 2 + 1] = self.MemSet.Parts[self.cursor[readerID * 2]].Offset
                length -= sublength
            if length > 0:
                sourceArray = memoryview(self.MemSet.Parts[self.cursor[readerID * 2]].Part.data)
                sourceIndex = self.cursor[readerID * 2 + 1]
                """ #!
                for i in range(length):
                    arr[i + offset] = sourceArray[i + sourceIndex]
                """
                arr_mv[offset : offset + length] = sourceArray[sourceIndex : sourceIndex + length]
                self.cursor[readerID * 2 + 1] += length
            offset = 0
            return offset, arr
            
    def ReadString(self, readerID, length):
        if self.cursor[readerID * 2 + 1] - self.MemSet.Parts[self.cursor[readerID * 2]].Offset + length < self.MemSet.Parts[self.cursor[readerID * 2]].PartLength:
            offset = self.cursor[readerID * 2 + 1]
            data_bytes = self.MemSet.Parts[self.cursor[readerID * 2]].Part.data[offset : offset + length]
            #! data_str = bytes(data_bytes).decode('utf-8')
            data_str = data_bytes.decode('utf-8')
            self.cursor[readerID * 2 + 1] += length
            return data_str
        else:
            #! arr = [None for _ in range(length)]
            arr = bytearray(length)
            arr_mv = memoryview(arr)
            offset = 0
            origLength = length
            while self.cursor[readerID * 2 + 1] - self.MemSet.Parts[self.cursor[readerID * 2]].Offset + length > self.MemSet.Parts[self.cursor[readerID * 2]].PartLength:
                sublength = self.MemSet.Parts[self.cursor[readerID * 2]].PartLength - self.cursor[readerID * 2 + 1] + self.MemSet.Parts[self.cursor[readerID * 2]].Offset
                sourceArray = memoryview(self.MemSet.Parts[self.cursor[readerID * 2]].Part.data)
                sourceIndex = self.cursor[readerID * 2 + 1]
                """ #!
                for i in range(sublength):
                    arr[i + offset] = sourceArray[i + sourceIndex]
                """
                arr_mv[offset : offset + sublength] = sourceArray[sourceIndex : sourceIndex + sublength]
                offset += sublength
                self.cursor[readerID * 2] += 1
                self.cursor[readerID * 2 + 1] = self.MemSet.Parts[self.cursor[readerID * 2]].Offset
                length -= sublength
            if length > 0:
                sourceArray = memoryview(self.MemSet.Parts[self.cursor[readerID * 2]].Part.data)
                sourceIndex = self.cursor[readerID * 2 + 1]
                """ #!
                for i in range(length):
                    arr[i + offset] = sourceArray[i + sourceIndex]
                """
                arr_mv[offset : offset + length] = sourceArray[sourceIndex : sourceIndex + length]
                self.cursor[readerID * 2 + 1] += length
            #! data_str = bytes(arr[0 : origLength]).decode('utf-8')
            data_str = arr[0 : origLength].decode('utf-8')
            return data_str
        
    def ReadBytes(self, readerID, length):
        output = BufferSet()
        output.Length = length
        bsCursor = 0
   
        while self.cursor[readerID * 2 + 1] - self.MemSet.Parts[self.cursor[readerID * 2]].Offset + length > self.MemSet.Parts[self.cursor[readerID * 2]].PartLength:
            partLength = self.MemSet.Parts[self.cursor[readerID * 2]].PartLength - self.cursor[readerID * 2 + 1] + self.MemSet.Parts[self.cursor[readerID * 2]].Offset
            bse = BufferSetElement()
            bse.Part = self.MemSet.Parts[self.cursor[readerID * 2]].Part
            bse.Offset = self.cursor[readerID * 2 + 1]
            bse.PartLength = partLength
            bse.Cursor = bsCursor
            output.Parts.append(bse)
            length -= partLength
            bsCursor += partLength
            self.cursor[readerID * 2] += 1
            self.cursor[readerID * 2 + 1] = self.MemSet.Parts[self.cursor[readerID * 2]].Offset

        if length > 0:
            bse = BufferSetElement()
            bse.Part = self.MemSet.Parts[self.cursor[readerID * 2]].Part
            bse.Offset = self.cursor[readerID * 2 + 1]
            bse.PartLength = int(length)
            bse.Cursor = bsCursor
            output.Parts.append(bse)
            self.cursor[readerID * 2 + 1] += int(length)

        return output
    
    def GetDiagnostics(self, readerID):
        diag = DiagnosticData()
        diag.block = self.cursor[readerID * 2]
        diag.offset = self.cursor[readerID * 2 + 1]
        diag.blockOffset = self.Memset.Parts[self.cursor[readerID * 2]].Offset
        diag.blockLength = self.MemSet.Parts[self.cursor[readerID * 2]].PartLength
        diag.totalBlocks = len(self.MemSet.Parts)
        diag.blockCursorStart = self.MemSet.Parts[self.cursor[readerID * 2]].Cursor
        diag.blockCursorCurrent = self.cursor[readerID * 2 + 1] - self.MemSet.Parts[self.cursor[readerID * 2]].Offset + self.MemSet.Parts[self.cursor[readerID * 2]].Cursor