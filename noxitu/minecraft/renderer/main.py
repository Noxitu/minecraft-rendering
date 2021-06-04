from ctypes import c_void_p
import logging

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

import noxitu.opengl
from noxitu.minecraft.renderer.controls import handle_events
from noxitu.minecraft.renderer.state import create_default_state
import noxitu.minecraft.renderer.io
import noxitu.minecraft.renderer.view as view

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s -- %(message)s',
    level=logging.INFO
)

SUN_DIRECTION = np.array([1, 3, -3], dtype=float)
SUN_DIRECTION /= np.linalg.norm(SUN_DIRECTION)

# SCREEN_WIDTH, SCREEN_HEIGHT = 64, 36
# SCREEN_WIDTH, SCREEN_HEIGHT = 320, 180
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
# SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

LOGGER.info('Loading data...')
blocks = noxitu.minecraft.renderer.io.load_blocks()
# viewport = noxitu.minecraft.renderer.io.load_viewport()

def to_mega_chunk(position):
    return np.floor(position / 256).astype(int)

def compute_mega_chunks(blocks):
    LOGGER.info('Computing mega chunk keys...')
    keys = to_mega_chunk(blocks['position'])
    ids = 0x10000 * keys[:, 2] + keys[:, 0]

    LOGGER.info('Reordering blocks...')
    order = np.argsort(ids)
    ids = ids[order]
    keys = keys[order]
    blocks = blocks[order]

    LOGGER.info('Creating megachunks...')
    ids, unique_indices, sizes = np.unique(ids, return_index=True, return_counts=True)
    keys = keys[unique_indices]
    ends = np.cumsum(sizes)


    ret = {
        tuple(key): blocks[end-size:end]
        for key, size, end in zip(keys, sizes, ends)
    }

    LOGGER.info('Created %d mega chunks.', len(ids))

    return ret

mega_chunks = compute_mega_chunks(blocks)
blocks = None

def create_vao(array):
    vbo = noxitu.opengl.create_buffers(array, usage=GL_STATIC_DRAW)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(program.attribute('in_position'), 3, GL_SHORT, GL_FALSE, 10, c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribIPointer(program.attribute('in_direction'), 3, GL_UNSIGNED_BYTE, 10, c_void_p(6))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(program.attribute('in_color'), 3, GL_UNSIGNED_BYTE, GL_TRUE, 10, c_void_p(7))

    return vbo, vao, len(array)

pygame.init()
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)

print('GL_VENDOR   =', str(glGetString(GL_VENDOR)))
print('GL_RENDERER =', str(glGetString(GL_RENDERER)))

clock = pygame.time.Clock()

# program = noxitu.opengl.Program(vs='play.vert.glsl', fs='play.frag.glsl', gs='play.geom.glsl', root=__file__)
program = noxitu.opengl.Program(vs='play2.vert.glsl', fs='play2.frag.glsl', gs='play2.geom.glsl', root=__file__)
actual_attribute_locations = [program.attribute(attr) for attr in 'in_position in_direction in_color'.split()]
assert actual_attribute_locations == [0, 1, 2], f'Invalid attribute locations: {actual_attribute_locations}.'

mega_chunks_vaos = {
    key: create_vao(value)
    for key, value in mega_chunks.items()
} 

state = create_default_state(
    redraw=True,
    screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT)
)

while True:
    pygame.display.set_caption(f'FPS = {clock.get_fps():.01f}')

    handle_events(state)

    camera_matrix = view.perspective(state.fov, state.screen_size[0]/state.screen_size[1])
    rotation_matrix = view.view(state.camera_yaw, state.camera_pitch, state.camera_roll)
    location_matrix = view.location(state.camera_position)
    
    projectionview_matrix = camera_matrix @ rotation_matrix @ location_matrix

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    program.use()

    program.set_uniform_mat4('projectionview_matrix', projectionview_matrix)
    glUniform3f(program.uniform('sun_direction'), *state.sun_direction)

    camera_chunk = to_mega_chunk(state.camera_position)

    for chunk_key, (_, vao, n_blocks) in mega_chunks_vaos.items():
        if np.linalg.norm(camera_chunk - chunk_key, ord=np.inf) <= 1:
            glBindVertexArray(vao)
            glDrawArrays(GL_POINTS, 0, n_blocks)
    

    clock.tick()

    pygame.display.flip()

