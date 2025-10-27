import socket
import struct

from RemoteBlobStore.__BufferStore.BufferStore import BufferStore
from RemoteBlobStore.__WriteBuffers.MemWriteBuffer import MemWriteBuffer
from RemoteBlobStore.Writers.ChunkWriter import ChunkWriter


class RunnerBase:
    def __init__(self, port, ClientType):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(("127.0.0.1", port))
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.intBuffer = bytearray(4)
        self.buffer =  BufferStore.RetrieveBlock(BufferStore.WriteDepth, "messenger")
        writer = ChunkWriter(MemWriteBuffer())
        writer.Write(ClientType)
        self.send(self.s, writer.buffer.Close())

    def Message(self, set):
        self.send(self.s, set)
        return self.read(self.s)

    def send(self, socket, set):
        self.intBuffer = bytearray(struct.pack('>I', len(set.Parts)))
        # print("debug",len(set.Parts))
        socket.sendall(self.intBuffer)
        for i in range(len(set.Parts)):
            self.intBuffer = bytearray(struct.pack('>I', set.Parts[i].PartLength))
            socket.sendall(self.intBuffer)
            offset = set.Parts[i].Offset
            part_length = set.Parts[i].PartLength
            data_mv = memoryview(set.Parts[i].Part.data)
            socket.sendall(data_mv[offset : offset + part_length])


    def read(self, socket):
        # print("empty socket:", self.is_socket_buffer_empty(socket))
        writer = MemWriteBuffer()
        self.ReadExact(socket, self.intBuffer, 0, 4)
        count = int.from_bytes(self.intBuffer, byteorder='big')
        # print("COUNT PARTS:", count)
        for i in range(count):
            self.ReadExact(socket, self.intBuffer, 0, 4)
            length = int.from_bytes(self.intBuffer, byteorder='big')
            while length > self.buffer.length:
                self.ReadExact(socket, self.buffer.data, self.buffer.offset, self.buffer.length)
                writer.WriteBytes(self.buffer.data, self.buffer.offset, self.buffer.length)
                length -= self.buffer.length
            if length > 0:
                self.ReadExact(socket, self.buffer.data, self.buffer.offset, length)
                writer.WriteBytes(self.buffer.data, self.buffer.offset, length)
                length = 0
        return writer.Close()


    def ReadExact(self, socket, buffer, offset, count):
        # print("Buffer from socket: ", buffer, count)
        buffer_mv = memoryview(buffer)
        while count > 0:
            data = socket.recv(count)
            if not data:
                raise EOFError("end of stream")
            read = len(data)
            buffer_mv[offset : offset + read] = data
            offset += read
            count -= read


    def is_socket_buffer_empty(self, sock):
        try:
            data = sock.recv(1, socket.MSG_PEEK)
            return not data 
        except socket.error as e:
            print("Socket error:", e)
            return None