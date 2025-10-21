from RemoteBlobStore.__WriteBuffers._intWriteBuffer import _intWriteBuffer
from RemoteBlobStore.__BufferStore.BufferSet import BufferSet, BufferSetElement
from RemoteBlobStore.__BufferStore.BufferStore import BufferStore


class MemWriteBuffer(_intWriteBuffer):
    def __init__(self):
        self.MemSet = BufferSet()
        self.block = 0
        self.offset = 0
        self.cursorOffset = 0

    def WriteBytes(self, arrOrSet, arrOffset=0, length=-1):
        if isinstance(arrOrSet, bytearray):
            assert length != -1
            arr = arrOrSet

            if len(self.MemSet.Parts) <= self.block:
                newPart = BufferStore.RetrieveBlock(BufferStore.WriteDepth, "memwrite")
                bse = BufferSetElement()
                bse.Cursor = self.cursorOffset
                bse.Part = newPart
                bse.Offset = newPart.offset
                bse.PartLength = 0
                self.MemSet.Parts.append(bse)
                self.cursorOffset += BufferStore.WriteBlockSize
                self.offset = self.MemSet.Parts[self.block].Offset

            arr_mv = memoryview(arr)
            while self.offset - self.MemSet.Parts[self.block].Offset + length > BufferStore.WriteBlockSize:
                subLength = BufferStore.WriteBlockSize - self.offset + self.MemSet.Parts[self.block].Offset
                destinationArray = memoryview(self.MemSet.Parts[self.block].Part.data)
                destinationIndex = self.offset
                destinationArray[destinationIndex : destinationIndex + subLength] = arr_mv[arrOffset : arrOffset + subLength]
                self.MemSet.Parts[self.block].PartLength += subLength
                self.block += 1
                newPart = BufferStore.RetrieveBlock(BufferStore.WriteDepth, "memwrite")
                bse = BufferSetElement()
                bse.Cursor = self.cursorOffset
                bse.Part = newPart
                bse.Offset = newPart.offset
                bse.PartLength = 0
                self.MemSet.Parts.append(bse)
                self.offset = newPart.offset
                self.cursorOffset += BufferStore.WriteBlockSize
                arrOffset += subLength
                self.MemSet.Length += subLength
                length -= subLength

            if length > 0:
                destinationArray = memoryview(self.MemSet.Parts[self.block].Part.data)
                destinationIndex = self.offset
                destinationArray[destinationIndex : destinationIndex + length] = arr_mv[arrOffset : arrOffset + length]
                self.MemSet.Length += length
                self.offset += length
                self.MemSet.Parts[self.block].PartLength += length

        elif isinstance(arrOrSet, BufferSet):
            assert length == -1
            set = arrOrSet
            for i in range(len(set.Parts)):
                self.WriteBytes(set.Parts[i].Part.data, set.Parts[i].Offset, set.Parts[i].PartLength)        

    def GetCursor(self):
        return self.MemSet.Length
    
    def Close(self):
        return self.MemSet