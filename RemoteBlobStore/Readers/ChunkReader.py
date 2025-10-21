import uuid

from RemoteBlobStore.Readers.ChunkReaderCore import ChunkReaderCore 


class ChunkReader:
    def __init__(self):
        self.workerGUID = str(uuid.uuid4())
        self.core = None

    def MoveCursor(self, offset):
        self.core.MoveCursor(self.workerGUID, offset)
        
    def GetCursor(self):
        return self.core.GetCursor(self.workerGUID)
    
    def ReadInt32(self):
        return self.core.ReadInt32(self.workerGUID)
    
    def ReadInt32Null(self):
        val = self.core.ReadInt32(self.workerGUID)
        if val == 0:
            return None
        else:
            return self.core.ReadInt32(self.workerGUID)
        
    def ReadInt64(self):
        return self.core.ReadInt64(self.workerGUID)
    
    def ReadInt32Null(self):
        val = self.core.ReadInt64(self.workerGUID)
        if val == 0:
            return None
        else:
            return self.core.ReadInt64(self.workerGUID)
        
    def ReadSingle(self):
        return self.core.ReadSingle(self.workerGUID)
    
    def ReadDouble(self):
        return self.core.ReadDouble(self.workerGUID)
    
    def ReadDoubleNull(self):
        val = self.core.ReadInt32(self.workerGUID)
        if val == 0:
            return None
        else:
            return self.core.ReadDouble(self.workerGUID)
        
    def ReadBoolean(self):
        val = self.core.ReadInt32(self.workerGUID)
        if val == 1:
            return True
        else:
            return False
    
    def ReadBooleanNull(self):
        val = self.core.ReadInt32(self.workerGUID)
        if val == 0:
            return None
        else:
            return self.ReadBoolean()
        
    def ReadString(self):
        return self.core.ReadString(self.workerGUID)
    
    def ReadStringStream(self):
        return self.core.ReadStringStream(self.workerGUID)
    
    def ReadDate(self):
        return self.core.ReadString(self.workerGUID)

    def ReadDateTime(self):
        pass # NEEDS REVISION

    def ReadSimpleLong(self):
        return self.core.ReadSimpleLong(self.workerGUID)
    
    def ReadSimpleInt32(self):
        return self.core.ReadSimpleInt32(self.workerGUID)
    
    def ReadBytes(self, length):
        return self.core.ReadBytes(self.workerGUID, length)
    
    def GetDiagnostics(self):
        return self.core.GetDiagnostics(self.workerGUID)
    
    def Dispose(self):
        self.core.Dispose()
    