import numpy as np
from tqdm import tqdm

import noxitu.minecraft.map.load


def load_world():
    if True:
        # offset, world = noxitu.minecraft.map.load.load(
        #     'data/chunks',
        #     tqdm=tqdm,
        #     x_range=slice(55, 125),
        #     y_range=slice(0, 256),
        #     z_range=slice(-75, -37)
        # )

        offset, world = noxitu.minecraft.map.load.load(
            'data/chunks',
            tqdm=tqdm,
            x_range=slice(-500, 0),
            y_range=slice(20, 256),
            z_range=slice(-20, 580)
        )

        if False:
            np.savez('data/goat.npz', offset=offset, world=world)
    elif False:
        RADIUS = 15

        offset, world = noxitu.minecraft.map.load.load(
            'data/chunks',
            tqdm=tqdm,
            x_range=slice(-RADIUS, RADIUS+1),
            y_range=slice(0, 256),
            z_range=slice(-RADIUS, RADIUS+1)
        )

        if False:
            np.savez('data/tmp.npz', offset=offset, world=world)

    else:
        # fd = np.load('data/tmp.npz')
        fd = np.load('data/tmp-goat.npz')
        offset, world = fd['offset'], fd['world']

    # _, _, x = -offset + [0, 0, 1000]
    # world = world[:, :1000, x:].copy()
    # offset += [0, 0, x]
    # world = world[30:130]
    # offset[0] += 30
    
    size = np.prod(world.shape, dtype=float)*2/1024/1024/1024
    print(world.shape, ' = ', size, 'GB')

    return offset[[2, 0, 1]], world

# load_world()

def load_viewport():
    return np.load('data/viewports/viewport.npz')
    # return np.load('data/viewports/p1.npz')
    # return np.load('data/viewports/p2.npz')
    # return np.load('data/viewports/viewport-grian2goat.npz')
    # return np.load('data/viewports/viewport-goat.npz')

def load_texture_atlas():
    fd = np.load('data/texture_atlas.npz')
    return fd['texture_atlas'], fd['texture_mapping']
