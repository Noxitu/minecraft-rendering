import os
import re

import numpy as np
from tqdm import tqdm

import noxitu.minecraft.protocol.packet
from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS


UNKNOWN = set()


def unpack_long(value, bits):
    mask = 2**bits - 1
    for i in range(0, 64-bits+1, bits):
        yield (value >> i) & mask


def parse_chunk(x, z, section_mask, data):
    global UNKNOWN
    data = noxitu.minecraft.protocol.packet.Packet(data)
    section_mask = [(b == '1') for b in bin((1<<16) | section_mask)[3:][::-1]]

    for y in range(16):
        if not section_mask[y]:
            continue

        _block_count = data.short()
        bits_per_block = data.ubyte()

        if bits_per_block < 4:
            bits_per_block = 4

        if bits_per_block <= 8:
            palette_length = data.varint()
            palette = np.array([data.varint() for _ in range(palette_length)])
            # print('   ', palette_length, 2 ** bits_per_block, *map(lambda i: GLOBAL_PALETTE[i], palette))
            if UNKNOWN is not None:
                UNKNOWN |= set(map(lambda i: GLOBAL_PALETTE[i], palette)) - set(MATERIALS)
        else:
            palette = np.arange(2 ** bits_per_block)

        section_data_length = data.varint()

        section_data = [data.ulong() for _ in range(section_data_length)]

        def get_result():
            result = [val for packed in section_data for val in unpack_long(packed, bits_per_block)][:16*16*16]
            result = palette[result]
            result = np.array(result).reshape(16, 16, 16).astype(int)
            return result

        yield y, get_result

    assert len(data._buffer) == data.offset


if __name__ == '__main__':
    os.makedirs('data/chunks', exist_ok=True)

    for chunk in tqdm(os.listdir('data/chunks_raw')):
        match = re.match(R'^(-?[0-9]+)-(-?[0-9]+)-([0-9]+)\.bin$', chunk)
        x, z, section_mask = [int(match.group(i)) for i in (1, 2, 3)]

        with open(f'data/chunks_raw/{x}-{z}-{section_mask}.bin', 'rb') as fd:
            data = fd.read()

        chunk = np.zeros((16, 16, 16, 16), dtype=int)

        for y, section in parse_chunk(x, z, section_mask, data):
            chunk[y] = section()

        np.save(Rf'data/chunks/{x}_{z}_chunk.npy', chunk.reshape(256, 16, 16))

    if UNKNOWN:
        print('Unknown items:')
        for item in UNKNOWN:
            print('  ', item)
        print()