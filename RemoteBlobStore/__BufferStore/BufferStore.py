import os
import threading
import uuid

from RemoteBlobStore.__BufferStore.BufferPart import BufferPart

from RemoteBlobStore.Utils.ConcurrentDictionary import ConcurrentDictionary
from RemoteBlobStore.Utils.ConcurrentQueue import ConcurrentQueue
from RemoteBlobStore.Utils.HashSet import HashSet
from RemoteBlobStore.Utils.PriorityQueue import PriorityQueue
from RemoteBlobStore.Utils.Queue import Queue


class BufferStoreDiagnostics:
    def __init__(self):
        self.AllocatedMaxBlocks = 0
        self.DeallocatedMaxBlocks = 0
        self.AllocatedBytes = ConcurrentDictionary()
        self.Lock = threading.Lock()

    def Allocate(self, tag, length):
        if not self.AllocatedBytes.ContainsKey(tag):
            self.AllocatedBytes.TryAdd(tag, [0, 0])
        with self.Lock:
            self.AllocatedBytes[tag][0] += length

    def Deallocate(self, tag, length):
        if not self.AllocatedBytes.ContainsKey(tag):
            self.AllocatedBytes.TryAdd(tag, [0, 0])
        with self.Lock:
            self.AllocatedBytes[tag][1] += length

    def Print(self):
        deallocated = 0
        allocated = 0
        for key in self.AllocatedBytes:
            value = self.AllocatedBytes[key]
            allocated += value[0]
            deallocated += value[1]
        print(f"A/D MaxBlocks: {self.AllocatedMaxBlocks}/{self.DeallocatedMaxBlocks} A/D Bytes: {self.allocated}/{self.deallocated}")
        for key in self.AllocatedBytes:
            value = self.AllocatedBytes[key]
            print(f"{key}: A/D  {value[0]}/{value[1]}")

    def getAllocationStatus(self):
        pass


class BufferStore:
    status = str()
    diag = None

    BaseBlockSize = 1024
    MaxDepth = 17
    FileDepth = 13
    WriteDepth = 3
    MaxBlockSize = 0
    FileBlockSize = 0
    WriteBlockSize = 0

    Buffers = None
    Blocks = None
    BufferPriority = None
    EmptyBuffers = None
    FullBuffers = None

    buffers = None

    BlocksLock = None

    def init():
        #print("MUST HAVE: Initialize static BufferStore!")
        BufferStore.status = str(uuid.uuid4())
        BufferStore.diag = BufferStoreDiagnostics()
        BufferStore.buffers = ConcurrentQueue()
        BufferStore.MaxBlockSize = (1 << (BufferStore.MaxDepth - 1)) * BufferStore.BaseBlockSize
        BufferStore.FileBlockSize = (1 << (BufferStore.FileDepth - 1)) * BufferStore.BaseBlockSize
        BufferStore.WriteBlockSize = (1 << (BufferStore.WriteDepth - 1)) * BufferStore.BaseBlockSize

        BufferStore.Buffers = [{} for _ in range(BufferStore.MaxDepth + 1)]
        BufferStore.Blocks = [{} for _ in range(BufferStore.MaxDepth + 1)]
        BufferStore.BufferPriority = [PriorityQueue() for _ in range(BufferStore.MaxDepth + 1)]
        BufferStore.EmptyBuffers = [HashSet() for _ in range(BufferStore.MaxDepth + 1)]
        BufferStore.FullBuffers = [HashSet() for _ in range(BufferStore.MaxDepth + 1)]

        BufferStore.BlocksLock = threading.Lock()

    def MeasureFragmentation():
        allocated = 0
        nonConsumed = 0
        for depth in range(BufferStore.MaxDepth + 1):
            with BufferStore.BlocksLock:
                for key in BufferStore.Blocks[depth]:
                    value = BufferStore.Blocks[depth][key]
                    allocated += BufferStore.MaxBlockSize
                    nonConsumed += BufferStore.BaseBlockSize * (1 << (depth - 1)) * value.Count()
                allocated += BufferStore.EmptyBuffers[depth].Count() * BufferStore.MaxBlockSize
        return 1.0 * nonConsumed / allocated

    def RetrieveMaxBlock():
        # print("START RETRIEVE MAX BLOCK")
        buf, removed = BufferStore.buffers.TryDequeue()
        # print("TryDequeue result", removed)
        if not removed:
            #! buf = [None for _ in range(BufferStore.MaxBlockSize)]
            buf = bytearray(BufferStore.MaxBlockSize)
            BufferStore.diag.AllocatedMaxBlocks += 1
        # print(type(buf), buf)
        return buf

    def ReplenishMaxBlock(buf):
        BufferStore.buffers.Enqueue(buf)
        while BufferStore.buffers.Count() > os.cpu_count():
            dummy, flag = BufferStore.buffers.TryDequeue()
            BufferStore.diag.DeallocatedMaxBlocks += 1

    def AugmentQueue(depth):
        # print("START AUGMENT QUEUE")
        newBuffer = BufferStore.RetrieveMaxBlock()
        bufferId = str(uuid.uuid4())
        BufferStore.Buffers[depth][bufferId] = newBuffer
        blocksize = BufferStore.BaseBlockSize * (1 << (depth - 1))
        count = (1 << (BufferStore.MaxDepth - depth))
        # print("blocksize", blocksize)
        # print("count", count)
        q = Queue()
        for i in range(count):
            q.Enqueue(i * blocksize)
        
        # with BufferStore.BlocksLock:
        #     print("get inside lock")
        #     BufferStore.Blocks[depth][bufferId] = q
        
        BufferStore.Blocks[depth][bufferId] = q
        
        return bufferId

    def ReplenishBlock(depth, bufferID, offset, tag):
        count = (1 << (BufferStore.MaxDepth - depth))
        BufferStore.diag.Deallocate(tag, BufferStore.BaseBlockSize * (1 << (depth - 1)))
        with BufferStore.BlocksLock:
            BufferStore.Blocks[depth][bufferID].Enqueue(offset)
            c = BufferStore.Blocks[depth][bufferID].Count()
            if c == count:
                if BufferStore.EmptyBuffers[depth].Contains(bufferID):
                    BufferStore.EmptyBuffers[depth].Remove(bufferID)
                else:
                    BufferStore.BufferPriority[depth].Remove(bufferID)
                if BufferStore.FullBuffers[depth].Count() > 0:
                    BufferStore.ReplenishMaxBlock(BufferStore.Buffers[depth][bufferID])
                    BufferStore.Buffers[depth].Remove(bufferID)
                    BufferStore.Blocks[depth].Remove(bufferID)
            else:
                if c == 1:
                    BufferStore.EmptyBuffers[depth].Remove(bufferID)
                    BufferStore.BufferPriority[depth].Insert(bufferID, -1)
                else:
                    BufferStore.BufferPriority[depth].ChangePriority(bufferID, -c)

    def RetrieveBlock(depth, tag="generic"):
        # print("GET RETRIEVE BLOCK")
        count = (1 << (BufferStore.MaxDepth - depth))
        BufferStore.diag.Allocate(tag, BufferStore.BaseBlockSize * (1 << (depth - 1)))
        # print("ALLOCATE SUCCESSFUL")
        bufferID = str()
        offset = 0
        with BufferStore.BlocksLock:
            if BufferStore.BufferPriority[depth].Count() == 0:
                # print("MUST BE HERE")
                if BufferStore.FullBuffers[depth].Count() > 0:
                    bufferID = BufferStore.FullBuffers[depth].First()
                    BufferStore.FullBuffers[depth].Remove(bufferID)
                else:
                    bufferID = BufferStore.AugmentQueue(depth)
                offset = BufferStore.Blocks[depth][bufferID].Dequeue()
                count -= 1
                if count == 0:
                    BufferStore.EmptyBuffers[depth].Add(bufferID)
                else:
                    BufferStore.BufferPriority[depth].Insert(bufferID, -count)

            else:
                bufferID = BufferStore.BufferPriority[depth].ExtractMax()
                offset = BufferStore.Blocks[depth][bufferID].Dequeue()
                c = BufferStore.Blocks[depth][bufferID].Count()
                if c == 0:
                    BufferStore.EmptyBuffers[depth].Add(bufferID)
                else:
                    BufferStore.BufferPriority[depth].Insert(bufferID, c)
        
        # print("CREATE BUFFER PART")
        part = BufferPart()
        part.data = BufferStore.Buffers[depth][bufferID]
        part.depth = depth
        part.bufferID = bufferID
        part.offset = offset
        part.length = BufferStore.BaseBlockSize * (1 << (depth - 1))
        part.tag = tag
        return part

    def Dispose():
        pass