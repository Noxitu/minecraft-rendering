import logging


LOGGER = logging.getLogger(__name__)


def _sign32(value):
    if value > 0x7fff_ffff:
        return value - 0x1_0000_0000
    return value


def _sign64(value):
    if value > 0x7fff_ffff_ffff_ffff:
        return value - 0x1_0000_0000_0000_0000
    return value


def _varint(buffer, offset, max_length, sign):
    ret = 0

    for i in range(max_length):
        if offset+i >= len(buffer):
            return None, i+1

        val = buffer[offset+i]
        ret += ((val & 0x7f) << (7*i))

        if (val & 0x80) == 0:
            return sign(ret), i+1
            
    LOGGER.warning('Too long varint read.')
    return sign(ret), max_length


def varint32(buffer, offset=0):
    return _varint(buffer, offset, 5, _sign32)


def varint64(buffer, offset=0):
    return _varint(buffer, offset, 10, _sign64)
