from ctypes import c_void_p

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *    

import noxitu.opengl
from noxitu.minecraft.raycaster.buffer_renderer import create_buffer_renderer


pygame.init()
pygame.display.set_mode((400, 400), DOUBLEBUF | OPENGL)

print('GL_VENDOR   =', str(glGetString(GL_VENDOR)))
print('GL_RENDERER =', str(glGetString(GL_RENDERER)))

program_factory = noxitu.opengl.ProgramFactory(root=__file__)

program = program_factory.create('example2', type='compute')

x = (np.arange(256).reshape(1, -1) + np.arange(256).reshape(-1, 1)).astype(np.float32)
y = np.zeros((256, 256), dtype=np.float32).copy()

x_vbo, y_vbo = noxitu.opengl.create_buffers(x, y, usage=GL_STATIC_DRAW)

pygame_clock = pygame.time.Clock()
render_buffer = create_buffer_renderer(program_factory)

while True:
    glBindBuffersBase(GL_SHADER_STORAGE_BUFFER, 0, 2, [x_vbo, y_vbo])

    program.use()
    glDispatchCompute(256, 256, 1)

    render_buffer(256, 256)

    pygame.display.flip()
    pygame.time.wait(1)
    pygame_clock.tick()

    pygame.display.set_caption(f'FPS = {pygame_clock.get_fps():.01f}')

    for event in pygame.event.get():
        if any([event.type == pygame.QUIT, event.type == pygame.KEYUP and event.unicode == 'q']):
            pygame.quit()
            quit()

