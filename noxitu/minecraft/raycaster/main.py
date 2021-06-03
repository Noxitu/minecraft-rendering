import logging
import numpy as np
from numpy.linalg.linalg import norm

from noxitu.minecraft.raycaster.core import chain_masks, raycast, normalize_factors
import noxitu.minecraft.raycaster.rays
import noxitu.minecraft.raycaster.io as io

from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS

LOGGER = logging.getLogger(__name__)

GLOBAL_MATERIALS = [MATERIALS.get(name) for name in GLOBAL_PALETTE]
GLOBAL_COLORS = [MATERIAL_COLORS.get(material) for material in GLOBAL_MATERIALS]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)
IS_WATER = np.array([MATERIALS.get(name) == 'water' for name in GLOBAL_PALETTE])

# render_height, render_width = 300, 400
render_height, render_width = 720, 1280
# render_height, render_width = 1080, 1920
# render_height, render_width = 1080*2, 1920*2

WATER_FACTORS = 0.6, 0.25, 0.07
AMBIENT_FACTOR, DIFFUSE_FACTOR = normalize_factors(0.5, 0.5)


NORMALS_IDX = np.array([
    0, 0, 0,
    -1, 0, 0, 1, 0, 0,
    0, -1, 0, 0, 1, 0,
    0, 0, -1, 0, 0, 1
], dtype=float).reshape(7, 3)

# SUN_DIRECTION = np.array([-0.5735764363510462, 0.8191520442889919, 0])
SUN_DIRECTION = np.array([1, 3, -3], dtype=float)
SUN_DIRECTION /= np.linalg.norm(SUN_DIRECTION)


def main():
    LOGGER.info('Loading world...')
    offset, world = io.load_world()

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

    def do_raycast_shadows(rays):
        n_rays = np.prod(rays.shape[::-1])
        LOGGER.info(f'Raycasting {n_rays:,} rays to find shadows...', )
        ids, _, _ = raycast(rays, world, GLOBAL_COLORS_MASK & ~IS_WATER)
        return (ids != 0)

    def do_raycast(rays, *,
                   block_mask=GLOBAL_COLORS_MASK,
                   sun_direction=SUN_DIRECTION,
                   compute_shadows=True,
                   compute_water_reflections=True,
                   compute_underwater=True):
        n_rays = np.prod(rays.shape[::-1])
        LOGGER.info(f'Raycasting {n_rays:,} rays...')
        ids, depths, normal_idx = raycast(rays, world, block_mask)
        colors = GLOBAL_COLORS[ids]

        diffuse_factors = noxitu.minecraft.raycaster.rays.compute_diffuse_factors(NORMALS_IDX,
                                                                                  sun_direction,
                                                                                  indices=normal_idx)

        if compute_shadows:
            hit_mask = (ids != 0)

            LOGGER.info('Computing shadow rays...')
            shadow_rays = noxitu.minecraft.raycaster.rays.compute_shadow_rays(rays[hit_mask], depths[hit_mask], sun_direction)
            shadow_mask = do_raycast_shadows(shadow_rays)

            diffuse_factors[chain_masks(hit_mask, shadow_mask)] *= 0.3
            diffuse_factors[chain_masks(hit_mask, shadow_mask)] -= -0.2

        colors[:] = colors * (diffuse_factors*DIFFUSE_FACTOR + AMBIENT_FACTOR)[..., np.newaxis]

        if compute_underwater or compute_water_reflections:
            water_mask = IS_WATER[ids]

            
            water_factors = normalize_factors(*WATER_FACTORS,
                                              mask=[True, compute_underwater, compute_water_reflections])
            water_colors = colors[water_mask] * water_factors[0]

            if compute_underwater:
                LOGGER.info('Computing underwater rays...')

                underwater_rays = rays[water_mask, 3:]

                # Apply Snell Law approximation for air -> water refraction:
                underwater_rays[..., 1] = 0.908 * underwater_rays[..., 1] - 0.41

                underwater_rays = noxitu.minecraft.raycaster.rays.compute_shadow_rays(rays[water_mask], depths[water_mask], underwater_rays)
                _, _, _, underwater_colors = do_raycast(underwater_rays,
                                                        block_mask=GLOBAL_COLORS_MASK & ~IS_WATER,
                                                        compute_shadows=True,
                                                        compute_underwater=False,
                                                        compute_water_reflections=False)

                water_colors += underwater_colors * water_factors[1]

            if compute_water_reflections:
                LOGGER.info('Computing water reflection rays...')
                water_reflection_rays = noxitu.minecraft.raycaster.rays.compute_shadow_rays(rays[water_mask], 
                                                                                            depths[water_mask]-0.01,
                                                                                            rays[water_mask, 3:] * [1, -1, 1])

                reflected_ids, _, _, water_reflection_colors = do_raycast(water_reflection_rays,
                                                                        block_mask=GLOBAL_COLORS_MASK,
                                                                        compute_shadows=False,
                                                                        compute_underwater=False,
                                                                        compute_water_reflections=False)

                water_reflection_colors[reflected_ids == 0] = 255
                water_colors += water_reflection_colors * water_factors[2]

            colors[water_mask] = water_colors

        return ids, depths, normal_idx, colors

    LOGGER.info('Raycasting...')
    _, _, _, colors = do_raycast(rays)

    LOGGER.info('Displaying...')
    import matplotlib.pyplot as plt
    plt.imsave('data/viewports/p1.raycasting.png', colors)
    plt.figure()
    plt.imshow(colors)
    # plt.figure()
    # plt.imshow(result_depths)
    # plt.figure()
    # plt.imshow(IS_WATER[result])
    plt.show()

    LOGGER.info('Done...')

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )
    main()