class BufferPart:
    def __init__(self):
        self.data = None
        self.depth = 0
        self.bufferID = None
        self.offset = 0
        self.length = 0
        self.tag = None
        from RemoteBlobStore.__BufferStore.BufferStore import BufferStore
        self.BsStatus = BufferStore.status

    def __del__(self):
        from RemoteBlobStore.__BufferStore.BufferStore import BufferStore
        if self.BsStatus == BufferStore.status:
            BufferStore.ReplenishBlock(self.depth, self.bufferID, self.offset, self.tag)