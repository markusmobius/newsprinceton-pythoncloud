class DiagnosticData:
    def __init__(self):
        self.block = 0
        self.offset = 0
        self.blockOffset = 0
        self.blockLength = 0
        self.totalBlocks = 0
        self.blockCursorStart = 0
        self.blockCursorCurrent = 0

    def print(self):
        print(f"             block:{self.block}")
        print(f"            offset:{self.offset}")
        print(f"       blockOffset:{self.blockOffset}")
        print(f"       blockLength:{self.blockLength}")
        print(f"       totalBlocks:{self.totalBlocks}")
        print(f"  blockCursorStart:{self.blockCursorStart}")
        print(f"blockCursorCurrent:{self.blockCursorCurrent}")


class _intReadBuffer:
    def GetCursorCount(self):
        pass

    def MoveCursor(self, readerID, offset):
        pass

    def GetCursor(self, readerID):
        pass

    def ReadByte(self, readerID):
        pass

    def ReadByteArrayDirect(self, readerID, length):
        # WARNING: originally in C#, "out int offset" is the last parameter 
        pass

    def ReadString(self, readerID, length):
        pass

    def ReadBytes(self, readerID, length):
        pass

    def GetDiagnostics(self, readerID):
        pass