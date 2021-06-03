import logging

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *    

import noxitu.opengl
from noxitu.minecraft.raycaster.buffer_renderer import create_buffer_renderer

from noxitu.minecraft.raycaster.core import chain_masks
import noxitu.minecraft.raycaster.rays
import noxitu.minecraft.raycaster.io as io

from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS

LOGGER = logging.getLogger(__name__)

GLOBAL_MATERIALS = [MATERIALS.get(name) for name in GLOBAL_PALETTE]
GLOBAL_COLORS = [MATERIAL_COLORS.get(material) for material in GLOBAL_MATERIALS]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)
IS_WATER = np.array([MATERIALS.get(name) == 'water' for name in GLOBAL_PALETTE])


# SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

LOCAL_GROUP_SIZE = 1536
COMPUTE_BATCH_SIZE = 64*16*LOCAL_GROUP_SIZE


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
        resolution=(SCREEN_HEIGHT, SCREEN_WIDTH),
        offset=offset
    )

    LOGGER.info('Initialize pygame...')
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)

    LOGGER.info('GL_VENDOR   = %s', str(glGetString(GL_VENDOR)))
    LOGGER.info('GL_RENDERER = %s', str(glGetString(GL_RENDERER)))
    LOGGER.info('GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS = %d', glGetIntegerv(GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS))
    LOGGER.info('GL_MAX_COMPUTE_WORK_GROUP_SIZE = %d %d %d', glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, 0)[0],
                                                             glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, 1)[0],
                                                             glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, 2)[0])

    program_factory = noxitu.opengl.ProgramFactory(root=__file__)

    raycaster_program = program_factory.create('raycaster', type='compute')
    render_buffer = create_buffer_renderer(program_factory)

    rays_vbo, world_vbo, world_mask_vbo = noxitu.opengl.create_buffers(rays, world, mask, usage=GL_STATIC_READ)

    ray_depths = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH), dtype=float)
    ray_depths_vbo = noxitu.opengl.create_buffers(ray_depths, usage=GL_STATIC_DRAW)

    pygame_clock = pygame.time.Clock()

    while True:
        raycaster_program.use()
        glUniform1iv(raycaster_program.uniform('world_shape'), 3, world.shape)
        glBindBuffersBase(GL_SHADER_STORAGE_BUFFER, 0, 4, [rays_vbo, world_vbo, world_mask_vbo, ray_depths_vbo])

        LOGGER.info('Before compute')
        total_rays = np.prod(rays.shape[:-1])
        glUniform1i(raycaster_program.uniform('count'), total_rays)

        for offset in range(0, total_rays, COMPUTE_BATCH_SIZE):
            glUniform1i(raycaster_program.uniform('offset'), offset)
            glDispatchCompute(COMPUTE_BATCH_SIZE, 1, 1)
            glFlush()

        LOGGER.info('After compute')

        glFinish()
        LOGGER.info('After barrier')

        import matplotlib.pyplot as plt
        noxitu.opengl.read_buffer(ray_depths_vbo, into=ray_depths)
        LOGGER.info('Drawing')
        plt.imshow(ray_depths)
        plt.show()
        break

        render_buffer(SCREEN_HEIGHT, SCREEN_WIDTH)

        pygame_clock.tick(24)
        pygame.display.flip()

        pygame.display.set_caption(f'FPS = {pygame_clock.get_fps():.01f}')
        pygame.time.wait(1)

        for event in pygame.event.get():
            if any([event.type == pygame.QUIT, event.type == pygame.KEYUP and event.unicode == 'q']):
                pygame.quit()
                quit()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )
    main()
