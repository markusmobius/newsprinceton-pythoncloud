class BufferSetElement:
    def __init__(self):
        self.Part = None
        self.Offset = 0
        self.Cursor = 0
        self.PartLength = 0


class BufferSet:
    def __init__(self, buffers=None):
        self.Parts = []
        self.Length = 0
        if buffers == None:
            return
        currentCursorOffset = 0
        for i in range(len(buffers)):
            self.Length += buffers[i].Length
            for j in range(len(buffers[i].Parts)):
                bse = BufferSetElement()
                bse.Part = buffers[i].Parts[j].Part
                bse.Offset = buffers[i].Parts[j].Offset
                bse.PartLength = buffers[i].Parts[j].PartLength
                bse.Cursor = currentCursorOffset
                self.Parts.append(bse)
                currentCursorOffset += buffers[i].Parts[j].PartLength

    def GetCursor(self, position):
        if len(self.Parts) == 0:
            return (0, 0)
        bottom = 0
        top = len(self.Parts) - 1
        currentPart = -1
        while True:
            half = (top + bottom) // 2
            if self.Parts[half].Cursor > position:
                top = half
            else:
                bottom = half
            if top - bottom <= 1:
                if self.Parts[top].Cursor <= position:
                    currentPart = top
                else:
                    currentPart = bottom
                break
        currentOffset = int(position - self.Parts[currentPart].Cursor) + self.Parts[currentPart].Offset
        return (currentPart, currentOffset)
    
    def Extract(self, position, length):
        output = BufferSet()
        output.Length = length
        pos = self.GetCursor(position)
        cursorOffset = 0
        (currentPart, currentOffset) = pos
        while length > 0:
            if currentOffset + length > self.Parts[currentPart].Offset + self.Parts[currentPart].PartLength:
                l = self.Parts[currentPart].Offset + self.Parts[currentPart].PartLength - currentOffset
                bse = BufferSet.BufferSetElement()
                bse.Part = self.Parts[currentPart].Part
                bse.Offset = currentOffset
                bse.PartLength = l
                bse.Cursor = cursorOffset
                output.Parts.append(bse)
                cursorOffset += l
                currentPart += 1
                currentOffset = self.Parts[currentPart].Offset
                length -= l
            else:
                bse = BufferSet.BufferSetElement()
                bse.Part = self.Parts[currentPart].Part
                bse.Offset = currentOffset
                bse.PartLength = int(length)
                bse.Cursor = cursorOffset
                output.Parts.append(bse)
                length = 0
        return output

    def ExtractFresh(self, position, length):
        pass

    def ToArray(self):
        pass

    def loadFromFile(filename=None):
        if filename  is None:
            raise Exception("invalid file name to load from")
        from RemoteBlobStore.__WriteBuffers.MemWriteBuffer import MemWriteBuffer
        writer = MemWriteBuffer()
        with open(filename, 'rb') as reader:
            data = bytearray(reader.read())
            writer.WriteBytes(data, 0, len(data))
        return writer.Close()

    def saveToFile(self, filename=None):
        if filename is None:
            raise Exception("invalid file name to save to")
        with open(filename, 'wb') as writer:
            for i in range(len(self.Parts)):
                offset = self.Parts[i].Offset
                part_length = self.Parts[i].PartLength
                data_mv = memoryview(self.Parts[i].Part.data)
                writer.write(data_mv[offset : offset + part_length])


        