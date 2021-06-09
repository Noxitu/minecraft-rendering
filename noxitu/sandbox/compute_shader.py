from ctypes import c_void_p
import logging
import time

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

import noxitu.opengl


SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

LOGGER = logging.getLogger(__name__)


def main():
    # size = 16384 + 8192 + 4086
    size = 16384 + 4086

    xs = np.ones((128, 128)).astype(np.float32)
    ys = np.zeros((size, size), dtype=np.float32)

    LOGGER.info(f'size of single array = {ys.size*ys.itemsize / 1024 / 1024 / 1024:.02f} GB')

    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.iconify()

    LOGGER.info('GL_VENDOR   = %s', str(glGetString(GL_VENDOR)))
    LOGGER.info('GL_RENDERER = %s', str(glGetString(GL_RENDERER)))

    t0 = time.time()

    LOGGER.info('Creating program...')
    program = noxitu.opengl.Program(cs=f'compute.glsl', root=__file__)

    LOGGER.info('Creating buffers...')
    xs_vbo, ys_vbo = noxitu.opengl.create_buffers(xs, ys, usage=GL_STATIC_DRAW)

    LOGGER.info('Preparing dispatch...')
    glBindBuffersBase(GL_SHADER_STORAGE_BUFFER, 0, 2, [xs_vbo, ys_vbo])

    program.use()

    q = 32

    queries = glGenQueries(1)

    for query in queries:
        glBeginQuery(GL_TIME_ELAPSED, query)
        glDispatchCompute(32, 32, 1)
        glEndQuery(GL_TIME_ELAPSED)
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
        glFlush()

    LOGGER.info('Finish...')
    t1 = time.time()
    glFinish()
    t2 = time.time()

    LOGGER.info(f'  Compute took \033[32m{1000*(t2-t1):.0f}\033[m ms')

    for i, query in enumerate(queries):
        elapsed_time = np.zeros((1,), dtype=np.int64)
        glGetQueryObjectui64v(query, GL_QUERY_RESULT, c_void_p(elapsed_time.ctypes.data))
        LOGGER.info(f'  Compute #{i} took \033[31m{(elapsed_time[0]/1e6):.0f}\033[m ms')

    LOGGER.info('Reading...')
    noxitu.opengl.read_buffer(ys_vbo, into=ys)

    t3 = time.time()
    LOGGER.info(f'Total OpenGL took \033[32m{1000*(t3-t0):.0f}\033[m ms')

    LOGGER.info('Displaying...')
    actual = np.sum(ys.ravel())
    expected = 32*32*q*q*512
    LOGGER.info(f'  actual = {actual}    expected = {expected}')
    # import matplotlib.pyplot as plt
    # plt.imshow(ys)
    # plt.show()

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )

    main()
