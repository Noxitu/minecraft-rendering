import numpy as np
from tqdm import tqdm

import noxitu.minecraft.map.load


def load_world():
    RADIUS = 16

    offset, world = noxitu.minecraft.map.load.load(
        'data/chunks',
        tqdm=tqdm,
        x_range=slice(-RADIUS, RADIUS+1),
        y_range=slice(0, 256),
        z_range=slice(-RADIUS, RADIUS+1)
    )

    return offset[[2, 0, 1]], world


def load_viewport():
    # return np.load('data/viewports/viewport.npz')
    return np.load('data/viewports/p1.npz')
    # return np.load('data/viewports/p2.npz')
