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


# RENDER_SHAPE = 1080, 1920
RENDER_SHAPE = 1080*2, 1920*2
# RENDER_SHAPE = 1080*4, 1920*4

WATER_SURFACE_DIFFUSION_FACTOR = 0.5
WATER_DEPTH_DIFFUSION_FACTOR = 0.94
AMBIENT_FACTOR, DIFFUSE_FACTOR = normalize_factors(0.25, 0.75)

USE_OPENGL = True

NORMALS_IDX = np.array([
    0, 0, 0,
    -1, 0, 0, 1, 0, 0,
    0, -1, 0, 0, 1, 0,
    0, 0, -1, 0, 0, 1
], dtype=float).reshape(7, 3)

FACE_UVS = np.array([
    0, 0,
    3, -2, -3, -2,
    1, -3, 1, 3,
    -1, -2, 1, -2,
])

FACE_UVS = np.array([
    [(1 if c > 0 else -1) if abs(c) == i else 0 for i in range(1, 4)] + [1 if c < 0 else 0]
    for c in FACE_UVS
], dtype=float).reshape(7, 2, 4)

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
    texture_atlas = texture_mapping = None

    LOGGER.info('Loading world...')
    offset, world = io.load_world()

    LOGGER.info('Reading viewport...')
    viewport = io.load_viewport()

    LOGGER.info('Loading textures...')
    texture_atlas, texture_mapping = io.load_texture_atlas()

    # LOGGER.info('Limiting world size...')
    # offset, world = reduce_size(offset, world, viewport['position'], viewport['rotation'][:3, :3])

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
        hit_mask = (ids != 0)

        # # Sky color
        # sunlight_diffusion = np.array([0.05, 0.1, 0.2])
        # # diffused from direct = 1-sunlight_diffusion
        # sunlight_strength = 255000

        # cosines = np.einsum('ni,i->n', rays[~hit_mask, 3:], sun_direction)
        # coeff = (1 + np.power(cosines, 2)) / 2
        # # colors[~hit_mask] = np.clip(255 * coeff, 0, 255)[..., np.newaxis]

        # diffused_color = sunlight_strength * (0.66 * sunlight_diffusion)
        # direct_color= sunlight_strength * (1-sunlight_diffusion) * coeff[..., np.newaxis]

        # # colors[~hit_mask] = np.clip(np.sqrt(diffused_color+direct_color), 0, 255)
        # colors[~hit_mask] = np.clip(np.sqrt(diffused_color), 0, 255)
        # colors[~hit_mask] = np.clip(np.sqrt(direct_color), 0, 255)

        if texture_mapping is not None:
            hit_ids = ids[hit_mask]
            hit_normal_idx = normal_idx[hit_mask]
            hit_rays = rays[hit_mask]
            hit_depths = depths[hit_mask]

            texture_idx = texture_mapping[hit_ids, hit_normal_idx-1]
            texture_mask = (texture_idx != -1)

            offsets3d = (hit_rays[:, :3] + hit_rays[:, 3:] * hit_depths[:, np.newaxis]) % 1
            face_uvs = FACE_UVS[hit_normal_idx]  
            offsets2d = np.einsum('nji,ni->nj', face_uvs[..., :3], offsets3d) + face_uvs[..., 3]
            offsets2d = np.clip((16*offsets2d).astype(np.uint8), 0, 15)

            grass_mask = (texture_idx[texture_mask] == 7)

            target_colors = texture_atlas[texture_idx, offsets2d[:, 1], offsets2d[:, 0], :3][texture_mask].copy()
            print(target_colors.shape)
            target_colors[grass_mask] = target_colors[grass_mask] * np.array([0x7C, 0xBD, 0x6B]) / 255 

            colors[chain_masks(hit_mask, texture_mask)] = target_colors

        diffuse_factors = noxitu.minecraft.raycaster.rays.compute_diffuse_factors(NORMALS_IDX,
                                                                                  sun_direction,
                                                                                  indices=normal_idx)

        if compute_shadows:
            LOGGER.info('Computing shadow rays...')
            shadow_rays = noxitu.minecraft.raycaster.rays.compute_shadow_rays(rays[hit_mask], depths[hit_mask], sun_direction)
            shadow_mask = do_raycast_shadows(shadow_rays)

            diffuse_factors[chain_masks(hit_mask, shadow_mask)] *= 0.3
            diffuse_factors[chain_masks(hit_mask, shadow_mask)] -= -0.2

        colors[hit_mask] = colors[hit_mask] * (diffuse_factors*DIFFUSE_FACTOR + AMBIENT_FACTOR)[..., np.newaxis][hit_mask]

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
                reflection_direction = [1, 1, 1] - 2 * abs(NORMALS_IDX[normal_idx[water_mask]])
                water_reflection_rays = noxitu.minecraft.raycaster.rays.compute_shadow_rays(rays[water_mask], 
                                                                                            depths[water_mask]-0.01,
                                                                                            rays[water_mask, 3:] * reflection_direction)

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
