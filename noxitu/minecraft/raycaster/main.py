import logging
import numpy as np

from noxitu.minecraft.raycaster.core import chain_masks, raycast as raycast_cpp, normalize_factors, pyplot
from noxitu.minecraft.raycaster.opengl_raycaster import Raycaster
import noxitu.minecraft.raycaster.rays
import noxitu.minecraft.raycaster.io as io

from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS

LOGGER = logging.getLogger(__name__)

GLOBAL_MATERIALS = [MATERIALS.get(name) for name in GLOBAL_PALETTE]
GLOBAL_COLORS = [MATERIAL_COLORS.get(material) for material in GLOBAL_MATERIALS]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)
IS_WATER = np.array([MATERIALS.get(name) == 'water' for name in GLOBAL_PALETTE])

# render_height, render_width = 360, 640
# render_height, render_width = 720, 1280
# render_height, render_width = 1080, 1920
# render_height, render_width = 1080*2, 1920*2

RENDER_SHAPE = 1080, 1920

WATER_SURFACE_DIFFUSION_FACTOR = 0.5
WATER_DEPTH_DIFFUSION_FACTOR = 0.94
AMBIENT_FACTOR, DIFFUSE_FACTOR = normalize_factors(0.5, 0.5)

USE_OPENGL = True


NORMALS_IDX = np.array([
    0, 0, 0,
    -1, 0, 0, 1, 0, 0,
    0, -1, 0, 0, 1, 0,
    0, 0, -1, 0, 0, 1
], dtype=float).reshape(7, 3)

# SUN_DIRECTION = np.array([-0.5735764363510462, 0.8191520442889919, 0])
SUN_DIRECTION = np.array([1, 3, -3], dtype=float)
SUN_DIRECTION /= np.linalg.norm(SUN_DIRECTION)


def create_camera_rays(render_shape, viewport, offset):
    return noxitu.minecraft.raycaster.rays.create_camera_rays(
        position=viewport['position'],
        rotation=viewport['rotation'][:3, :3],
        camera=viewport['camera'][:3, :3],
        resolution=render_shape,
        offset=offset
    )

def reduce_size(offset, world, camera_position, camera_rotation=None):
    new_size = 1400
    middle_offset = -np.array([new_size / 2, 0, new_size / 2])

    if camera_rotation is not None:
        dx, _, dz = camera_rotation.T @ [0, 0, 1]
        middle_offset += [dx*new_size/4, 0, dz*new_size/4]

    new_height = slice(None)
    x0, _, z0 = (camera_position - offset + middle_offset).astype(int)
    x0 = max(0, x0)
    z0 = max(0, z0)
    offset = offset + [x0, 0, z0]
    world = world[new_height, z0:z0+new_size, x0:x0+new_size]
    
    if world.shape[2] % 32 != 0:
        remove = world.shape[2] % 32
        world = world[..., :-remove]
    
    world = world.copy()

    size = np.prod(world.shape, dtype=float)*2/1024/1024/1024
    LOGGER.info('  reduced to shape %s and size %.02f GB', world.shape, size)
    assert size < 2.0

    return offset, world


def main():
    LOGGER.info('Loading world...')
    offset, world = io.load_world()

    LOGGER.info('Reading viewport...')
    viewport = io.load_viewport()

    LOGGER.info('Limiting world size...')
    offset, world = reduce_size(offset, world, viewport['position'], viewport['rotation'][:3, :3])

    LOGGER.info('Computing rays...')
    rays = create_camera_rays(RENDER_SHAPE, viewport, offset)

    raycast = raycast_cpp
    primary_block_mask = GLOBAL_COLORS_MASK
    block_mask_without_water = GLOBAL_COLORS_MASK & ~IS_WATER

    if USE_OPENGL:
        LOGGER.info('Initializing OpenGL raycaster')
        raycaster = Raycaster(world=world)
        primary_block_mask = raycaster.set_mask('primary_block_mask', primary_block_mask)
        block_mask_without_water = raycaster.set_mask('block_mask_without_water', block_mask_without_water)
        raycast = raycaster.raycast

    def do_raycast_shadows(rays):
        n_rays = np.prod(rays.shape[::-1])
        LOGGER.info(f'Raycasting {n_rays:,} rays to find shadows...', )
        ids, _, _ = raycast(rays, world, block_mask_without_water)
        return (ids != 0)

    def do_raycast(rays, *,
                   block_mask=primary_block_mask,
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

            # Schlick's approximation of Fresnel formula:
            R0 = ((1.0 - 1.33) / (1.0 + 1.33)) ** 2
            cosine = rays[water_mask, 3:].dot([0, -1, 0])
            reflectance = R0 + (1-R0) * np.power(1 - cosine, 5)

            water_factors = np.stack([
                WATER_SURFACE_DIFFUSION_FACTOR * np.ones_like(reflectance), 
                (1-WATER_SURFACE_DIFFUSION_FACTOR) * (1-reflectance),
                (1-WATER_SURFACE_DIFFUSION_FACTOR) * reflectance
            ], axis=0)[..., np.newaxis]
            
            water_colors = colors[water_mask] * water_factors[0]

            if compute_underwater:
                LOGGER.info('Computing underwater rays...')

                underwater_rays = rays[water_mask, 3:]

                # Apply Snell's Law custom approximation for air -> water refraction:
                underwater_rays[..., 1] = 0.908 * underwater_rays[..., 1] - 0.41

                underwater_rays = noxitu.minecraft.raycaster.rays.compute_shadow_rays(rays[water_mask], depths[water_mask], underwater_rays)
                _, underwater_depths, _, underwater_colors = do_raycast(underwater_rays,
                                                        block_mask=block_mask_without_water,
                                                        compute_shadows=True,
                                                        compute_underwater=False,
                                                        compute_water_reflections=False)

                underwater_depth_factor1 = np.power(WATER_DEPTH_DIFFUSION_FACTOR, underwater_depths)
                underwater_depth_factor2 = np.power(WATER_DEPTH_DIFFUSION_FACTOR, -underwater_depths*underwater_rays[..., 4])

                # x = underwater_colors.copy()

                underwater_colors = underwater_colors * underwater_depth_factor1[..., np.newaxis]
                underwater_colors += ((1-underwater_depth_factor1) * underwater_depth_factor2)[..., np.newaxis] * colors[water_mask]

                # pyplot(underwater_depth_factor1, underwater_depth_factor2, x, underwater_colors / 255, mask=water_mask)

                water_colors += underwater_colors * water_factors[1]

            if compute_water_reflections:
                LOGGER.info('Computing water reflection rays...')
                water_reflection_rays = noxitu.minecraft.raycaster.rays.compute_shadow_rays(rays[water_mask], 
                                                                                            depths[water_mask]-0.01,
                                                                                            rays[water_mask, 3:] * [1, -1, 1])

                reflected_ids, _, _, water_reflection_colors = do_raycast(water_reflection_rays,
                                                                        block_mask=primary_block_mask,
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
    plt.imsave('data/viewports/raycasting.png', colors)
    pyplot(
        colors,
    )

    LOGGER.info('Done...')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )

    main()
