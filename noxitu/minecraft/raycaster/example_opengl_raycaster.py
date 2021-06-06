from ctypes import c_void_p
import logging
import time
from numpy.core.shape_base import block

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

import noxitu.opengl

from noxitu.minecraft.raycaster.main import *


# RENDER_SHAPE = 720, 1280
RENDER_SHAPE = 1080, 1920
RENDER_SHAPE = 1080*2, 1920*2
# RENDER_SHAPE = 500, 500

SCREEN_WIDTH, SCREEN_HEIGHT = 100, 100

PROGRAM_LOCAL_SIZE = 16, 16, 1

LOGGER = logging.getLogger(__name__)


def array_size_in_gb(array):
    return array.size * array.itemsize / 1024 / 1024 / 1024


def create_state(rays):
    shape = tuple(list(rays.shape[:-1]) + [6])
    state = np.zeros(shape, dtype=np.int)
    state[..., :3] = rays[..., :3]
    state[..., 4] = -1
    return state


def create_depths(rays):
    return np.zeros(rays.shape[:-1], dtype=np.float32)


def compute_workgroup_num(rays, local_size):
    local_size_x, local_size_y, local_size_z = local_size

    def ceil_div(val, div): return int((val + div - 1) // div)

    n_rays = len(rays.reshape(-1, rays.shape[-1]))
    size = local_size_x * local_size_y * local_size_z

    return ceil_div(n_rays, size), 1, 1


def main():
    LOGGER.info('Loading world...')
    offset, world = io.load_world()
    world = world[40:140]
    offset[1] += 40
    assert world.size % 2 == 0

    LOGGER.info('Reading viewport...')
    viewport = io.load_viewport()

    LOGGER.info('Limiting world size...')
    offset, world = reduce_size(offset, world, viewport['position'], viewport['rotation'][:3, :3])

    LOGGER.info('Computing rays...')
    rays = create_camera_rays(RENDER_SHAPE, viewport, offset).astype(np.float32)
    n_rays = rays.reshape(-1, rays.shape[-1]).shape[0]

    LOGGER.info('Creating result buffers...')
    state = create_state(rays)
    depths = create_depths(rays)

    LOGGER.info(f'  world = %.2f GB %s', array_size_in_gb(world), world.shape)
    LOGGER.info(f'  rays = %.2f GB %s', array_size_in_gb(rays), rays.shape)
    LOGGER.info(f'  state = %.2f GB %s', array_size_in_gb(state), state.shape)
    LOGGER.info(f'  depths = %.2f GB %s', array_size_in_gb(depths), depths.shape)

    LOGGER.info('Setting up OpenGL...')
    LOGGER.info('  Context...')
    noxitu.opengl.init(SCREEN_WIDTH, SCREEN_HEIGHT, True)

    LOGGER.info('  Buffers...')
    rays_ssbo = noxitu.opengl.create_buffers(rays, usage=GL_DYNAMIC_DRAW)
    state_ssbo, depths_ssbo = noxitu.opengl.create_buffers(state, depths, usage=GL_STREAM_COPY)
    world_ssbo = noxitu.opengl.create_buffers(world, usage=GL_STATIC_DRAW)
    block_mask = GLOBAL_COLORS_MASK.astype(np.uint32)
    block_mask_ssbo = noxitu.opengl.create_buffers(block_mask, usage=GL_STATIC_DRAW)

    glBindBuffersBase(GL_SHADER_STORAGE_BUFFER, 0, 5, [rays_ssbo, state_ssbo, depths_ssbo, world_ssbo, block_mask_ssbo])

    LOGGER.info('  Program...')
    # program = noxitu.opengl.Program(cs=f'compute2.orig.glsl', root=__file__)
    program = noxitu.opengl.Program(cs=f'raycaster.glsl', root=__file__)

    program.use()
    glUniform1ui(program.uniform('n_rays'), n_rays)
    glUniform1ui(program.uniform('ray_offset'), 0)
    glUniform1iv(program.uniform('world_shape'), 3, world.shape)

    LOGGER.info('Dispatching jobs...')
    raycasting_start_time = time.time()
    queries = []
    for _ in range(10):
        query, = glGenQueries(1)
        queries.append(query)

        glBeginQuery(GL_TIME_ELAPSED, query)
        glDispatchCompute(*compute_workgroup_num(rays, PROGRAM_LOCAL_SIZE))
        glEndQuery(GL_TIME_ELAPSED)

        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
        glFlush()


    LOGGER.info('Waiting for jobs...')

    elapsed_time = np.zeros((1,), dtype=np.int64)
    for i, query in enumerate(queries):
        glGetQueryObjectui64v(query, GL_QUERY_RESULT, c_void_p(elapsed_time.ctypes.data))
        LOGGER.info(f'  Compute #{i} took \033[31m{elapsed_time[0]/1e6:.0f}\033[m ms')

    glFinish()

    raycasting_end_time = time.time()
    LOGGER.info(f'  Raycasting took \033[32m{1000*(raycasting_end_time-raycasting_start_time):.0f}\033[m ms')

    LOGGER.info('Reading result...')
    noxitu.opengl.read_buffer(state_ssbo, into=state)
    noxitu.opengl.read_buffer(depths_ssbo, into=depths)

    # LOGGER.info('Original result')
    # rays = rays.astype(float)
    # raycasting_start_time = time.time()
    # ids2, depths2, _ = raycast(rays.astype(float), world, GLOBAL_COLORS_MASK)

    # raycasting_end_time = time.time()
    # LOGGER.info(f'  Raycasting (c++) took \033[32m{1000*(raycasting_end_time-raycasting_start_time):.0f}\033[m ms')

    # LOGGER.info('Displaying...')
    # colors = GLOBAL_COLORS[state[..., 4]]
    # # colors2 = GLOBAL_COLORS[ids2]
    # import matplotlib.pyplot as plt
    # plt.subplot(221).imshow(depths)
    # plt.subplot(222).imshow(colors)
    # plt.subplot(223).imshow(depths2)
    # plt.subplot(224).imshow(colors2)
    # plt.subplot(325).imshow(colors3)

    # plt.show()

    LOGGER.info('Done.')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )

    main()
