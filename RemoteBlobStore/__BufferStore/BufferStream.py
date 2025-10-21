from io import BufferedIOBase, SEEK_SET, SEEK_CUR, SEEK_END

from RemoteBlobStore.__BufferStore.BufferStore import BufferStore 
from RemoteBlobStore.__BufferStore.BufferSet import BufferSetElement

class BufferStream(BufferedIOBase):
    def __init__(self, set=None):
        super().__init__()
        self.set = set
        self.position = 0
        if set != None:
            (self.currentBlock, self.currentOffset) = self.set.GetCursor(0)
        else:
            (self.currentBlock, self.currentOffset) = (0, 0)

    def read(self, size=-1):
        count = self.set.Length
        if self.position + count >= self.set.Length:
            count = int(self.set.Length - self.position)
        print("ENTER READ BUFFER STREAM", count, self.set.Length, self.position)
        if count <= 0:
            return None
        bufOffset = 0
        readCount = count
        #! buffer = [None for _ in range(count)]
        buffer = bytearray(count)
        buffer_mv = memoryview(buffer)
        while self.currentOffset + count - self.set.Parts[self.currentBlock].Offset > self.set.Parts[self.currentBlock].PartLength:
            length = self.set.Parts[self.currentBlock].PartLength - self.currentOffset + self.set.Parts[self.currentBlock].Offset
            sourceArray = memoryview(self.set.Parts[self.currentBlock].Part.data)
            sourceIndex = self.currentOffset
            """ #!
            for i in range(length):
                buffer[bufOffset + i] = sourceArray[sourceIndex + i]
            """
            buffer_mv[bufOffset : bufOffset + length] = sourceArray[sourceIndex : sourceIndex + length]
            bufOffset += length
            count -= length
            self.position += length
            self.currentBlock += 1
            self.currentOffset = self.set.Parts[self.currentBlock].Offset
        
        if count > 0:
            sourceArray = memoryview(self.set.Parts[self.currentBlock].Part.data)
            sourceIndex = self.currentOffset
            """ #!
            for i in range(count):
                buffer[bufOffset + i] = sourceArray[sourceIndex + i]
            """
            buffer_mv[bufOffset : bufOffset + count] = sourceArray[sourceIndex : sourceIndex + count]
            self.position += count
            self.currentOffset += count
        
        #! return bytes(buffer)
        return buffer

    def write(self, buffer):
        print("??? TYPE OF BUFFER: ", type(buffer))
        count = len(buffer)
        if len(self.set.Parts) <= self.currentBlock:
            newPart = BufferStore.RetrieveBlock(BufferStore.FileDepth, "stream")
            bse = BufferSetElement()
            bse.Part = newPart
            bse.Offset = newPart.offset
            bse.Cursor = self.position
            self.set.Parts.append(bse)
            self.currentOffset = newPart.offset
        
        buffer_mv = memoryview(buffer)
        bufOffset = 0
        while self.currentOffset + count - self.set.Parts[self.currentBlock].Offset > BufferStore.FileBlockSize:
            length = BufferStore.FileBlockSize - self.currentOffset + self.set.Parts[self.currentBlock].Offset
            """ #!
            for i in range(length):
                self.set.Parts[self.currentBlock].Part.data[self.currentOffset + i] = buffer[bufOffset + i]
            """
            #! self.set.Parts[self.currentBlock].Part.data[self.currentOffset : self.currentOffset + length] = buffer[bufOffset : bufOffset + length]
            part_data_mv = memoryview(self.set.Parts[self.currentBlock].Part.data)
            part_data_mv[self.currentOffset : self.currentOffset + length] = buffer_mv[bufOffset : bufOffset + length]
            self.position += length
            bufOffset += length
            self.set.Length += length
            self.set.Parts[self.currentBlock].PartLength += length
            count -= length
            newPart = BufferStore.RetrieveBlock(BufferStore.FileDepth, "stream")
            bse = BufferSetElement()
            bse.Part = newPart
            bse.Offset = newPart.offset
            bse.Cursor = self.position
            self.set.Parts.append(bse)
            self.currentBlock += 1
            self.currentOffset = self.set.Parts[self.currentBlock].Part.offset
        
        if count > 0:
            """ #!
            for i in range(count):
                self.set.Parts[self.currentBlock].Part.data[self.currentOffset + i] = buffer[bufOffset + i]
            """
            #! self.set.Parts[self.currentBlock].Part.data[self.currentOffset : self.currentOffset + count] = buffer[bufOffset : bufOffset + count]
            part_data_mv = memoryview(self.set.Parts[self.currentBlock].Part.data)
            part_data_mv[self.currentOffset : self.currentOffset + count] = buffer_mv[bufOffset : bufOffset + count]
            self.position += count
            self.currentOffset += count
            self.set.Length += count
            self.set.Parts[self.currentBlock].PartLength += count

    def seek(self, offset, whence=0):
        if whence == SEEK_SET:
            self.position = offset
        elif whence == SEEK_CUR:
            self.position += offset
        elif whence == SEEK_END:
            self.position = self.set.Length + offset
        (self.currentBlock, self.currentOffset) = self.set.GetCursor(self.position)
        return self.position
        
    def GetBufferSet(self):
        return self.set
