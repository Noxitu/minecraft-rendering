import logging
import os
import sys
import threading

import cv2
import numpy as np

from noxitu.minecraft.map.biomes import BIOMES


LOGGER = logging.getLogger(__name__)

MAIN = sys.modules['__main__']
SELF = sys.modules[__name__]

COLORS = {
    'green': (0, 200, 0),
    'blue': (200, 0, 0),
    'gray': (150, 150, 150),
    'orange': (0, 100, 200),
    'purple': (200, 0, 200),
    'white': (200, 200, 200),
    'yellow': (0, 200, 200),
}

SIZE = 16

class DATA:
    offset = []
    canvas = np.array([])


if hasattr(MAIN, '_visualization'):
    _thread, _event = MAIN._visualization
    _event.set()
    _thread.join()
    del MAIN._visualization


if os.path.exists('data/biomes.npz'):
    LOGGER.info('Loading...')
    _data = np.load('data/biomes.npz')
    DATA.offset = _data['offset']
    DATA.canvas = _data['canvas']

    LOGGER.info('Loaded.  offset=%s  canvas=%s', DATA.offset, DATA.canvas.shape)

def visualization_thread(event, data):
    cv2.namedWindow('chunks', cv2.WINDOW_NORMAL)

    while not event.is_set():
        cv2.imshow('chunks', data.canvas)
        cv2.waitKey(25)
        
    cv2.destroyWindow('chunks')

    LOGGER.info('Saving...  offset=%s  canvas=%s', data.offset, data.canvas.shape)
    np.savez('data/biomes.npz', offset=np.array(data.offset), canvas=data.canvas)
    LOGGER.info('Saved.')


def require_threads():
    if not hasattr(MAIN, '_visualization'):
        _event = threading.Event()
        _thread = threading.Thread(target=visualization_thread, args=(_event, DATA))
        _thread.daemon = True
        _thread.start()
        MAIN._visualization = _thread, _event


def get_chunk(x, z):
    if len(DATA.offset) == 0:
        DATA.offset = z-z%SIZE, x-x%SIZE
        DATA.canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

    oz, ox = DATA.offset
    iz, ix = z-oz, x-ox

    if iz >= 0 and ix >= 0:
        ret = DATA.canvas[iz:iz+1, ix:ix+1]

        if ret.shape == (1, 1, 3):
            return ret

    nz, nx = z-z%SIZE, x-x%SIZE
    sz, sx, _ = DATA.canvas.shape

    min_z = min((nz, oz))
    min_x = min((nx, ox))
    max_z = max((nz+SIZE, oz+sz))
    max_x = max((nx+SIZE, ox+sx))

    new_canvas = np.zeros((max_z-min_z, max_x-min_x, 3), dtype=np.uint8)

    pz = oz-min_z
    px = ox-min_x

    LOGGER.info(f'Resized... ({ox}, {oz}) x [{sx}, {sz}]  ->  ({min_x}, {min_z}) x [{max_x-min_x}, {max_z-min_z}]')

    new_canvas[pz:pz+sz, px:px+sx] = DATA.canvas
    DATA.canvas = new_canvas
    oz, ox = DATA.offset = min_z, min_x
    iz, ix = z-oz, x-ox
    ret = DATA.canvas[iz:iz+1, ix:ix+1]

    if ret.shape == (1, 1, 3):
        return ret

    LOGGER.error('Failed to correctly extend canvas')


def handle_biome_data(x, z, biome_data):
    require_threads()

    avg_color = np.zeros((3,))
    by = 64
    
    for bz in range(0, 16, 4):
        for bx in range(0, 16, 4):
            idx = ((by >> 2) & 63) << 4 | ((bz >> 2) & 3) << 2 | ((bx >> 2) & 3)
            biome_id = biome_data[idx]
            avg_color += COLORS[BIOMES[biome_id]]

    avg_color /= 16
    get_chunk(x, z)[:] = avg_color


os.makedirs('data/chunks_raw', exist_ok=True)

def handle_chunk_data(x, z, section_mask, chunk_data):
    require_threads()
    # LOGGER.info('Protocol -- chunk_data -- %d %d', x, z)

    with open(f'data/chunks_raw/{x}-{z}-{section_mask}.bin', 'wb') as fd:
        fd.write(chunk_data)

    pass
