from RemoteBlobStore.Readers.ChunkReader import ChunkReader
from RemoteBlobStore.Readers.ChunkReaderCore import ChunkReaderCore

class FileMetaData:
    def __init__(self):
        return

    def ReadBinary(self, reader : ChunkReader):
        self.cloudFileName = reader.ReadString()
        self.fileLength = str(reader.ReadInt64())
        self.checkSum = reader.ReadString()
        self.checkSumCRC32C = reader.ReadString()
        self.lastModified = reader.ReadDate()
        count = reader.ReadInt32()
        self.tags={}
        for i in range(count):
            self.tags[reader.ReadString()]=reader.ReadString()
        self.isPublic = reader.ReadBoolean()


class DirectoryStatus:
    def __init__(self):
        return

    def ReadBinary(self, reader : ChunkReader):
        self.lastUpdate = reader.ReadString()
        self.parentDirectory = reader.ReadString();
        self.directoryName= reader.ReadString();
        count = reader.ReadInt32();
        self.files = {}
        for i in range(count):
            id=reader.ReadString()
            meta=FileMetaData()
            meta.ReadBinary(reader)
            self.files[id]=meta
        count = reader.ReadInt32()
        self.directories=[]
        for i in range(count):
            self.directories.append(reader.ReadString())
        self.is_encrypted = reader.ReadBoolean()
