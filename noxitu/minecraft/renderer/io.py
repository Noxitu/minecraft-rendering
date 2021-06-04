import numpy as np


def load_blocks():
    return np.load('data/block_buffers/output.npz')['buffer']
    # return np.load('data/block_buffers/small.npz')['buffer']


def load_viewport():
    # return np.load('data/viewports/viewport.npz')
    return np.load('data/viewports/p1.npz')
    # return np.load('data/viewports/p2.npz')
    # return np.load('data/viewports/viewport-grian2goat.npz')
    # return np.load('data/viewports/viewport-goat.npz')
