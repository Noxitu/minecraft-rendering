import logging
import numpy as np

from noxitu.minecraft.raycaster.core import chain_masks, raycast
import noxitu.minecraft.raycaster.rays
import noxitu.minecraft.raycaster.io as io

from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS

LOGGER = logging.getLogger(__name__)

GLOBAL_COLORS = [MATERIAL_COLORS.get(MATERIALS.get(name)) for name in GLOBAL_PALETTE]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)
IS_WATER = np.array([MATERIALS.get(name) == 'water' for name in GLOBAL_PALETTE])

# render_height, render_width = 300, 400
render_height, render_width = 720, 1280
# render_height, render_width = 1080, 1920
# render_height, render_width = 1080*4, 1920*4


NORMALS_IDX = np.array([
    0, 0, 0,
    -1, 0, 0, 1, 0, 0,
    0, -1, 0, 0, 1, 0,
    0, 0, -1, 0, 0, 1
], dtype=float).reshape(7, 3)

SUN_DIRECTION = np.array([-0.5735764363510462, 0.8191520442889919, 0])


def main():
    LOGGER.info('Loading world...')
    offset, world = io.load_world()

    LOGGER.info('Computing mask...')
    mask = GLOBAL_COLORS_MASK[world]

    LOGGER.info('Reading viewport...')
    viewport = io.load_viewport()

    LOGGER.info('Computing rays...')
    rays = noxitu.minecraft.raycaster.rays.create_camera_rays(
        position=viewport['position'],
        rotation=viewport['rotation'],
        camera=viewport['camera'],
        resolution=(render_height, render_width),
        offset=offset
    )

    LOGGER.info('Raycasting...')
    result_id, result_depths, result_normal_idx = raycast(rays, world, mask)
    # visible_mask = (result_id != 0)
    result_colors = GLOBAL_COLORS[result_id]

    result_diffuse_factors = noxitu.minecraft.raycaster.rays.compute_diffuse_factors(NORMALS_IDX,
                                                                                     SUN_DIRECTION,
                                                                                     indices=result_normal_idx)

    LOGGER.info('Computing shadow rays...')
    shadow_rays = noxitu.minecraft.raycaster.rays.compute_shadow_rays(rays, result_depths, SUN_DIRECTION)

    LOGGER.info('Raycasting shadows...')
    result_shadow, _, _ = raycast(shadow_rays, world, mask)
    result_shadow_mask = (result_shadow != 0)
        
    result_diffuse_factors[result_shadow_mask] *= 0.3
    result_colors[:] = result_colors * (result_diffuse_factors*0.4 + 0.6)[..., np.newaxis]

    LOGGER.info('Computing water reflection rays...')
    water_mask = IS_WATER[result_id]
    water_rays = shadow_rays[water_mask]
    water_rays[..., 3:] = rays[water_mask, 3:]
    water_rays[..., 4] *= -1

    LOGGER.info('Raycasting water reflections...')
    water_result, _, water_normals_idx = raycast(water_rays, world, mask)
    has_reflection = (water_result != 0)
    water_with_reflection = chain_masks(water_mask, has_reflection)
    water_colors = GLOBAL_COLORS[water_result[has_reflection]]

    water_diffuse_factors = noxitu.minecraft.raycaster.rays.compute_diffuse_factors(NORMALS_IDX,
                                                                                    SUN_DIRECTION * [0, -1, 0],
                                                                                    indices=water_normals_idx[has_reflection])

    water_colors[:] = water_colors * (water_diffuse_factors[..., np.newaxis]*0.4 + 0.6)

    result_colors[water_with_reflection] = 0.75*result_colors[water_with_reflection] + 0.25*water_colors

    LOGGER.info('Displaying...')
    import matplotlib.pyplot as plt
    try:
        plt.imsave('data/viewports/p1.raycasting.png', result_colors)
        plt.figure()
        plt.imshow(result_colors)
        # plt.figure()
        # plt.imshow(result_depth2)
        # plt.figure()
        # plt.imshow(IS_WATER[result])
        plt.show()
    except ValueError:
        plt.figure()
        plt.imshow(result_colors[..., 0])
        plt.figure()
        plt.imshow(result_colors[..., 1])
        plt.figure()
        plt.imshow(result_colors[..., 2])
        plt.show()

    LOGGER.info('Done...')

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )
    main()