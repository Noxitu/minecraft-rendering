from ctypes import c_void_p
import logging
import time

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

import noxitu.opengl


SCREEN_WIDTH, SCREEN_HEIGHT = 100, 100

PROGRAM_LOCAL_SIZE = 16 * 16 * 1
BATCH_SIZE = PROGRAM_LOCAL_SIZE * 10_000

LOGGER = logging.getLogger(__name__)

def create_state(rays):
    shape = tuple(list(rays.shape[:-1]) + [6])
    state = np.zeros(shape, dtype=np.int)
    state[..., :3] = rays[..., :3]
    state[..., 4] = -1
    return state


def create_depths(rays):
    return np.zeros(rays.shape[:-1], dtype=np.float32)


def ceil_div(val, div): return int((val + div - 1) // div)


def buffer_data(ssbo, array, usage=GL_STATIC_DRAW):
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
    glBufferData(GL_SHADER_STORAGE_BUFFER, array.size * array.itemsize, array, usage=usage)


class Raycaster:
    def __init__(self, *, world, init_pygame=True):
        if init_pygame:
            noxitu.opengl.init(SCREEN_WIDTH, SCREEN_HEIGHT, True)

        self._world_shape = world.shape
        self._world_ssbo = noxitu.opengl.create_buffers(world, usage=GL_STATIC_DRAW)
        self._rays_ssbo = glGenBuffers(1)
        self._state_ssbo = glGenBuffers(1)
        self._depths_ssbo = glGenBuffers(1)

        self._masks_ssbos = {}

        self._program = noxitu.opengl.Program(cs=f'raycaster.glsl', root=__file__)

    def set_mask(self, name, mask):
        mask = mask.astype(np.uint32)
        ssbo = noxitu.opengl.create_buffers(mask, usage=GL_STATIC_DRAW)
        self._masks_ssbos[name] = ssbo
        return name

    def raycast(self, rays, _, mask_name, times=10):
        rays = rays.astype(np.float32)
        state = create_state(rays)
        depths = create_depths(rays)

        buffer_data(self._rays_ssbo, rays)
        buffer_data(self._state_ssbo, state)
        buffer_data(self._depths_ssbo, depths)

        glBindBuffersBase(GL_SHADER_STORAGE_BUFFER, 0, 5, [
            self._rays_ssbo,
            self._state_ssbo,
            self._depths_ssbo,
            self._world_ssbo,
            self._masks_ssbos[mask_name]
        ])

        n_rays = len(rays.reshape(-1, rays.shape[-1]))

        self._program.use()
        glUniform1ui(self._program.uniform('n_rays'), n_rays)
        glUniform1iv(self._program.uniform('world_shape'), 3, self._world_shape)

        LOGGER.info('Dispatching jobs...')
        raycasting_start_time = time.time()
        queries = []

        for offset in range(0, n_rays, BATCH_SIZE):
            glUniform1ui(self._program.uniform('ray_offset'), offset)

            current_batch_size = min(n_rays - offset, BATCH_SIZE)
            current_workgroup_num = ceil_div(current_batch_size, PROGRAM_LOCAL_SIZE)

            for _ in range(times):
                query, = glGenQueries(1)
                queries.append(query)

                glBeginQuery(GL_TIME_ELAPSED, query)
                glDispatchCompute(current_workgroup_num, 1, 1)
                glEndQuery(GL_TIME_ELAPSED)

                glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
                glFlush()

        LOGGER.info('Waiting for jobs...')

        elapsed_time = np.zeros((1,), dtype=np.int64)
        for i, query in enumerate(queries):
            glGetQueryObjectui64v(query, GL_QUERY_RESULT, c_void_p(elapsed_time.ctypes.data))

            if elapsed_time > 10e6:
                LOGGER.info(f'  Compute #{i} took \033[31m{elapsed_time[0]/1e6:.0f}\033[m ms')

        glFinish()

        raycasting_end_time = time.time()
        LOGGER.info(f'  Raycasting took \033[32m{1000*(raycasting_end_time-raycasting_start_time):.0f}\033[m ms')

        LOGGER.info('Reading result...')
        noxitu.opengl.read_buffer(self._state_ssbo, into=state)
        noxitu.opengl.read_buffer(self._depths_ssbo, into=depths)

        infinite_mask = (state[..., 3] == 0)
        state[infinite_mask, 4] = 0

        return (
            state[..., 4].astype(np.uint16),
            depths,
            state[..., 5].astype(np.uint8)
        )
