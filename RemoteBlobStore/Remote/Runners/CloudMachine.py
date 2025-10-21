from RemoteBlobStore.__ReadBuffers.MemReadBuffer import MemReadBuffer
from RemoteBlobStore.__WriteBuffers.MemWriteBuffer import MemWriteBuffer
from RemoteBlobStore.Readers.ChunkReader import ChunkReader
from RemoteBlobStore.Readers.ChunkReaderCore import ChunkReaderCore
from RemoteBlobStore.Remote.RunnerBase import RunnerBase
from RemoteBlobStore.Writers.ChunkWriter import ChunkWriter
from RemoteBlobStore.Remote.Runners.DownloadTask import DownloadTask
from RemoteBlobStore.Remote.Runners.UploadTask import TagRule, BlobFilter
from RemoteBlobStore.Remote.Runners.DirectoryStatus import DirectoryStatus

class CloudMachine:
    def __init__(self, port, clientHash: str, serverUrl: str):
        self.cloud = RunnerBase(port, "cloudMachine")
        self.clientHash=clientHash
        self.serverUrl=serverUrl

    def Directory(self, cloudDirectory: str):
        writer = ChunkWriter(MemWriteBuffer())
        writer.Write("directory")
        writer.Write(self.clientHash)
        writer.Write(self.serverUrl)
        writer.Write(cloudDirectory)
        response = self.cloud.Message(writer.buffer.Close())
        reader = ChunkReader()
        reader.core = ChunkReaderCore(MemReadBuffer(response))
        if reader.ReadInt32()==0:
            return None
        output=DirectoryStatus()
        output.ReadBinary(reader)
        return output

    def Download(self, downloads: DownloadTask):
        writer = ChunkWriter(MemWriteBuffer())
        writer.Write("download")
        writer.Write(self.clientHash)
        writer.Write(self.serverUrl)
        downloads.WriteBinary(writer)
        response = self.cloud.Message(writer.buffer.Close())
        reader = ChunkReader()
        reader.core = ChunkReaderCore(MemReadBuffer(response))
        return reader.ReadString()

    def Upload(self, localDirectory: str, cloudDirectory: str, tagRules: list[TagRule], publicRules: list[BlobFilter], recursiveUpload: bool):
        writer = ChunkWriter(MemWriteBuffer())
        writer.Write("upload")
        writer.Write(self.clientHash)
        writer.Write(self.serverUrl)
        writer.Write(localDirectory)
        writer.Write(cloudDirectory)
        writer.Write(len(tagRules))
        for tagRule in tagRules:
            tagRule.WriteBinary(writer)
        writer.Write(len(publicRules))
        for publicRule in publicRules:
            publicRule.WriteBinary(writer)
        writer.Write(recursiveUpload)
        response = self.cloud.Message(writer.buffer.Close())
        reader = ChunkReader()
        reader.core = ChunkReaderCore(MemReadBuffer(response))
        return reader.ReadString()
            
