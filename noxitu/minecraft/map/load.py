import os

import numpy as np


def _ch(idx):
    return slice(16*idx, 16*idx+16)


def load(path, tqdm=lambda x: x, x_range=None, y_range=None, z_range=None):
    chunks = []
    chunks_paths = []

    if x_range is not None:
        use_x = lambda c: x_range.start <= c < x_range.stop
    else:
        use_x = lambda _: True
    
    if z_range is not None:
        use_z = lambda c: z_range.start <= c < z_range.stop
    else:
        use_z = lambda _: True

    if y_range is None:
        y_range = slice(0, 256)

    for chunk in os.listdir(path):
        x, z = map(int, chunk.split('_')[:2])

        if use_x(x) and use_z(z):
            chunks.append((x, z))
            chunks_paths.append(chunk)

    chunks = np.array(chunks)

    min_x = np.amin(chunks[:, 0])
    min_z = np.amin(chunks[:, 1])
    min_y = y_range.start
    max_x = np.amax(chunks[:, 0])
    max_z = np.amax(chunks[:, 1])

    size_x = max_x - min_x + 1
    size_y = y_range.stop - y_range.start
    size_z = max_z - min_z + 1

    print(f'Allocating {1.0*size_y*16*size_z*16*size_x/1024/1024/1024:.01f} GB...')
    world = np.zeros((size_y, 16*size_z, 16*size_x), dtype=np.uint16)

    for chunk in tqdm(chunks_paths):
        x, z = map(int, chunk.split('_')[:2])

        world[:, _ch(z-min_z), _ch(x-min_x)] = np.load(os.path.join(path, chunk))[y_range]

    return np.array([min_y, 16*min_z, 16*min_x]), world
