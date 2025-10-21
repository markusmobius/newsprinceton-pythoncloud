
class IntZip:
    def __init__(self):
        self.buffer = bytearray(10)

    def compress(self, num):
        v = num
        length = 0
        offset = 9
        while v >= 0x80:
            if length == 0:
                self.buffer[offset] = (v & 0x7f)
            else:
                self.buffer[offset] = (v | 0x80)
            v >>= 7
            length += 1
            offset -= 1
        if length == 0:
            self.buffer[9 - length] = v
        else:
            self.buffer[9 - length] = (v | 0x80)
        length += 1
        return offset, length