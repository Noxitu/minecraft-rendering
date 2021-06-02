import ctypes
import logging

import numpy as np
from tqdm import tqdm

import noxitu.minecraft.map.load
from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS

LOGGER = logging.getLogger(__name__)

GLOBAL_COLORS = [MATERIAL_COLORS.get(MATERIALS.get(name)) for name in GLOBAL_PALETTE]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)

def array(a):
    return (
        ctypes.c_void_p(a.ctypes.data),
        ctypes.c_int(len(a.shape)), 
        a.ctypes.shape,
        a.ctypes.strides
    )

raycast = ctypes.WinDLL('c++/build/raycast3d/Release/RayCasting.dll').raycast

def main():
    LOGGER.info('Loading world...')

    S = 10

    render_height, render_width = 720, 1280

    offset, world = noxitu.minecraft.map.load.load(
        'data/chunks',
        tqdm=tqdm,
        x_range=slice(-S, S+1),
        y_range=slice(0, 256),
        z_range=slice(-S, S+1)
    )

    offset = offset[[2, 0, 1]]

    LOGGER.info('Computing mask...')
    mask = GLOBAL_COLORS_MASK[world]

    LOGGER.info('Reading viewport...')
    viewport = np.load('data/viewports/p1.npz')
    P_inv = np.linalg.inv(viewport['camera'] @ viewport['rotation'])
    camera_x, camera_y, camera_z = viewport['position'] - offset

    LOGGER.info('Computing rays...')
    rays = np.array([
        [camera_x, camera_y, camera_z, x, y, 1] 
        for y in np.linspace(-1, 1, render_height)
        for x in np.linspace(-1, 1, render_width)
    ], dtype=float)
    
    rays[:, 3:] = np.einsum('rc,nc->nr', P_inv, rays[:, 3:])
    rays[:, 3:] /= np.linalg.norm(rays[:, 3:], axis=1).reshape(-1, 1)

    result = np.zeros((render_height*render_width), dtype=int)

    LOGGER.info('Raycasting...')
    raycast(*array(rays), *array(world), *array(mask), *array(result))

    result = result.reshape(render_height, render_width)
    result = GLOBAL_COLORS[result]

    LOGGER.info('Displaying...')
    import matplotlib.pyplot as plt
    plt.imsave('data/viewports/p1.raycasting.png', result)
    plt.figure()
    plt.imshow(result)
    plt.show()

    LOGGER.info('Done...')

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )
    main()