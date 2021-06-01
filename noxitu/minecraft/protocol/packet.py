import struct
import uuid

from noxitu.minecraft.protocol.protocol_core import varint32
import noxitu.minecraft.protocol.nbt


class Packet:
    def __init__(self, buffer):
        self._buffer = buffer
        self.offset = 0

    def boolean(self):
        return self.ubyte() != 0

    def ubyte(self):
        self.offset += 1
        return self._buffer[self.offset-1]

    def short(self):
        value, = struct.unpack_from('>h', self._buffer, self.offset)
        self.offset += 2
        return value

    def ushort(self):
        value, = struct.unpack_from('>H', self._buffer, self.offset)
        self.offset += 2
        return value

    def int(self):
        value, = struct.unpack_from('>i', self._buffer, self.offset)
        self.offset += 4
        return value

    def long(self):
        value, = struct.unpack_from('>q', self._buffer, self.offset)
        self.offset += 8
        return value

    def ulong(self):
        value, = struct.unpack_from('>Q', self._buffer, self.offset)
        self.offset += 8
        return value

    def varint(self):
        value, skip = varint32(self._buffer, self.offset)
        self.offset += skip
        return value

    def string(self, n):
        length = self.varint()
        value = self._buffer[self.offset:self.offset+length]
        self.offset += length
        return value

    def nbt(self):
        value, self.offset = noxitu.minecraft.protocol.nbt.parse(self._buffer, self.offset)
        return value

    def uuid(self):
        value = uuid.UUID(bytes=self._buffer[self.offset:self.offset+16])
        self.offset += 16
        return value

    def bytearray(self, length):
        value = self._buffer[self.offset:self.offset+length]
        self.offset += length
        return value

