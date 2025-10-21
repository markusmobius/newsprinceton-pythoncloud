from RemoteBlobStore.Writers.ChunkWriter import ChunkWriter


class BlobFilter:
    def __init__(self, ftype: str, filterDefinition : str):
        self.ftype=ftype
        self.filterDefinition=filterDefinition
        if ftype not in ["ending","contains", "pattern"]:
            raise Exception("invalid blobfilterType")

    def WriteBinary(self, writer: ChunkWriter):
        match self.ftype:
            case "ending":
                writer.Write(0)
            case "contains":
                writer.Write(1)
            case "pattern":
                writer.Write(2)
        writer.Write(self.filterDefinition)


class TagRule:
    def __init__(self, key:str, value: str, kvFilter: BlobFilter):
        self.key=key
        self.value=value
        self.kvFilter=kvFilter

    def WriteBinary(self, writer: ChunkWriter):
        writer.Write(self.key)
        writer.Write(self.value)
        self.kvFilter.WriteBinary(writer)

