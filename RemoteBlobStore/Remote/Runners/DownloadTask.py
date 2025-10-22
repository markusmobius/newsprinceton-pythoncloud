from RemoteBlobStore.Readers.ChunkReader import ChunkReader
from RemoteBlobStore.Readers.ChunkReaderCore import ChunkReaderCore
from RemoteBlobStore.Writers.ChunkWriter import ChunkWriter
import json

class FileFilter:
    def __init__(self):
        self.name=""
        self.definition={}

    def WriteBinary(self, writer: ChunkWriter):
        writer.Write(self.name)
        writer.Write(json.dumps(self.definition,default=lambda x: x.__dict__))

class FilterPattern(FileFilter):
    def __init__(self, patterns : list[str]):
        self.name="pattern"
        self.definition={"patterns": patterns}

class RangeDate:
    def __init__(self, year: int, month:int, day:int, hour:int, minute:int):
        self.year=year
        self.month=month
        self.day=day
        self.hour=hour
        self.minute=minute

class FilterRange(FileFilter):
    def __init__(self, start: RangeDate, end: RangeDate, prefix: str, fileType:str, suffix: list[str]):
        self.name="range"
        self.definition={
            "start" : start,
            "end": end,
            "prefix":prefix,
            "fileType": fileType,
            "suffix": suffix
        }

class DirectorySet:    
    def __init__(self, paths : list[str] =[], filters: dict[str, FileFilter]={}):
        self.paths=paths
        self.filters=filters

    def WriteBinary(self, writer: ChunkWriter):
        writer.Write(len(self.paths))
        for path in self.paths:
            writer.Write(path)
        writer.Write(len(self.filters))
        for key, filter in self.filters.items():
            writer.Write(key)
            filter.WriteBinary(writer)
    
    def ReadBinary(self,reader: ChunkReader):
        count = reader.ReadInt32()
        self.paths=[]
        for i in range(count):
            self.paths.append(reader.ReadString())
        count = reader.ReadInt32()
        self.filters=dict[str, FileFilter]()
        for i in range(count):
            id=reader.ReadString()
            f=FileFilter()
            f.ReadBinary()
            self.filters[id]=f


class DownloadTask:
    def __init__(self,localRootDirectory : str, downloads : DirectorySet):
        self.localRootDirectory =localRootDirectory 
        self.downloads = downloads

    def WriteBinary(self, writer: ChunkWriter):
        writer.Write(self.localRootDirectory)
        self.downloads.WriteBinary(writer)

    def ReadBinary(self,reader : ChunkReader):
        self.localRootDirectory=reader.ReadString()
        downloads=DirectorySet()
        downloads.ReadBinary(reader)