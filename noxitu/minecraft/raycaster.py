import ctypes
import logging

import numpy as np
from tqdm import tqdm

import noxitu.minecraft.map.load
from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS

LOGGER = logging.getLogger(__name__)

def use_material(material):
    # return material != 'water'
    return True

MATERIALS = [MATERIALS.get(name) for name in GLOBAL_PALETTE]
GLOBAL_COLORS = [MATERIAL_COLORS.get(material if use_material(material) else None) for material in MATERIALS]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)

def array(a):
    return (
        ctypes.c_void_p(a.ctypes.data),
        ctypes.c_int(len(a.shape)), 
        a.ctypes.shape,
        a.ctypes.strides
    )

_raycast_impl = ctypes.WinDLL('c++/build/raycast3d/Release/RayCasting.dll').raycast

def raycast(rays, world, mask):
    render_height, render_width, _ = rays.shape

    result = np.zeros((render_height, render_width), dtype=int)
    result_depth = np.zeros((render_height, render_width), dtype=float)

    _raycast_impl(
        *array(rays.reshape(-1, 6)),
        *array(world),
        *array(mask),
        *array(result.ravel()),
        *array(result_depth.ravel())
    )

    return result, result_depth

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
        [ [camera_x, camera_y, camera_z, x, y, 1] for x in np.linspace(-1, 1, render_width) ]
        for y in np.linspace(-1, 1, render_height)
    ], dtype=float)
    
    rays[..., 3:] = np.einsum('rc,nmc->nmr', P_inv, rays[..., 3:])
    rays[..., 3:] /= np.linalg.norm(rays[..., 3:], axis=2)[..., np.newaxis]

    LOGGER.info('Raycasting...')
    result, result_depth = raycast(rays, world, mask)

    LOGGER.info('Raycasting shadows...')
    rays[..., :3] = rays[..., :3] + rays[..., 3:] * result_depth[..., np.newaxis]
    rays[..., 3:] = [-1, 20, 10]
    rays[..., 3:] /= np.linalg.norm(rays[..., 3:], axis=2)[..., np.newaxis]

    result_shadow, _ = raycast(rays, world, mask)
    result_shadow_mask = (result_shadow != 0)
        
    result_colors = GLOBAL_COLORS[result]
    result_colors[result_shadow_mask] = result_colors[result_shadow_mask] * 0.6

    LOGGER.info('Displaying...')
    import matplotlib.pyplot as plt
    plt.imsave('data/viewports/p1.raycasting.png', result_colors)
    plt.figure()
    plt.imshow(result_colors)
    # plt.figure()
    # plt.imshow(result_depth)
    plt.show()

    LOGGER.info('Done...')

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )
    main()