import os
import re
import zlib

import numpy as np
from tqdm import tqdm

import noxitu.minecraft.protocol.nbt as nbt
import noxitu.minecraft.protocol.packet
from noxitu.minecraft.map.global_palette import BLOCKS, GLOBAL_PALETTE, MATERIALS


UNKNOWN = set()


def unpack_long(value, bits):
    if value < 0:
        value += 2 ** 64

    mask = 2**bits - 1
    for i in range(0, 64-bits+1, bits):
        yield (value >> i) & mask


def unpack_section(section_data, palette):
    global UNKNOWN

    if UNKNOWN is not None:
        UNKNOWN |= set(map(lambda i: GLOBAL_PALETTE[i], palette)) - set(MATERIALS)


    bits_per_block = 4

    while 2 ** bits_per_block < len(palette):
        bits_per_block += 1

    result = [val for packed in section_data for val in unpack_long(packed, bits_per_block)]
    result = result[:16*16*16]
    result = palette[result]
    result = np.array(result).reshape(16, 16, 16).astype(int)
    return result


if __name__ == '__main__':
    os.makedirs('data/chunks', exist_ok=True)

    PATH = R'C:\Users\grzeg\AppData\Roaming\.minecraft\saves\hc7\region'

    for chunk_file in tqdm(os.listdir(PATH)):
        try:
            match = re.match(R'^r\.(-?[0-9]+)\.(-?[0-9]+)\.mca$', chunk_file)
            global_x, global_z = [int(match.group(i)) for i in (1, 2)]
        except:
            tqdm.write(f'\033[31mFailed for {chunk_file}\033[m')
            raise

        with open(f'{PATH}/{chunk_file}', 'rb') as fd:
            data = fd.read()

        try:
            chunks = {(i%32, i//32): (4096 * (65536*data[4*i] + 256*data[4*i+1] + data[4*i+2]), 4096*data[4*i+3]) for i in range(1024)}
            chunks = {(x, z): (offset, size) for (x, z), (offset, size) in chunks.items() if size > 0}
        except:
            tqdm.write(f'\033[31mFailed for {chunk_file}\033[m')
            continue
        
        for (local_x, local_z) in tqdm([(local_x, local_z) for local_x in range(32) for local_z in range(32)], leave=False):
            try:                
                offset, size = chunks[(local_x, local_z)]
            except KeyError:
                continue

            x = 32*global_x + local_x
            z = 32*global_z + local_z

            if x < -210 or x > 150 or z < -120 or z > 130:
                continue

            if os.path.exists(f'data/chunks/{x}_{z}_chunk.npy'):
                continue

            chunk_data = noxitu.minecraft.protocol.packet.Packet(data[offset:offset+5])
            size = chunk_data.int()
            encryption = chunk_data.ubyte()
            assert encryption == 2

            chunk_data = zlib.decompress(data[offset+5:offset+4+size])
            chunk_data, _ = nbt.parse(chunk_data)

            assert chunk_data[b''][b'Level'][b'xPos'] == x
            assert chunk_data[b''][b'Level'][b'zPos'] == z

            chunk = np.zeros((16, 16, 16, 16), dtype=np.uint16)

            for section in chunk_data[b''][b'Level'][b'Sections']:
                y = section[b'Y']

                if b'BlockStates' in section:
                    palette = []

                    for entry in section[b'Palette']:
                        block = BLOCKS[entry[b'Name'].decode()]
                        if b'Properties' in entry:
                            properties = {key.decode(): value.decode() for key, value in entry[b'Properties'].items()}
                            n = 0
                            for state in block['states']:
                                if all(properties.get(key) == value for key, value in state['properties'].items()):
                                    palette.append(state['id'])
                                    n += 1

                            if n != 1:
                                raise Exception()
                        else:
                            n = 0
                            for state in block['states']:
                                if state['default']:
                                    palette.append(state['id'])
                                    n += 1

                            if n != 1:
                                raise Exception()

                    palette = np.array(palette)
                    chunk[y] = unpack_section(section[b'BlockStates'], palette)


            np.save(Rf'data/chunks/{x}_{z}_chunk.npy', chunk.reshape(256, 16, 16))

    # for chunk in tqdm(os.listdir('data/chunks_raw')):
    #     match = re.match(R'^(-?[0-9]+)-(-?[0-9]+)-([0-9]+)\.bin$', chunk)
    #     x, z, section_mask = [int(match.group(i)) for i in (1, 2, 3)]

    #     with open(f'data/chunks_raw/{x}-{z}-{section_mask}.bin', 'rb') as fd:
    #         data = fd.read()

    #     chunk = np.zeros((16, 16, 16, 16), dtype=int)

    #     for y, section in parse_chunk(x, z, section_mask, data):
    #         chunk[y] = section()

    #     np.save(Rf'data/chunks/{x}_{z}_chunk.npy', chunk.reshape(256, 16, 16))

    if UNKNOWN:
        print('Unknown items:')
        for item in UNKNOWN:
            print('  ', item)
        print()
