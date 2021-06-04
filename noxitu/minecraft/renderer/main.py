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


LAZY_RENDERING = True

# SCREEN_WIDTH, SCREEN_HEIGHT = 64, 36
# SCREEN_WIDTH, SCREEN_HEIGHT = 320, 180
# SCREEN_WIDTH, SCREEN_HEIGHT = 640, 360
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
# SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

PANORAMA_WIDTH, PANORAMA_HEIGHT = 8000, 8000

LOGGER = logging.getLogger(__name__)


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


def create_vao(array):
    vbo = noxitu.opengl.create_buffers(array, usage=GL_STATIC_DRAW)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_SHORT, GL_FALSE, 10, c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribIPointer(1, 3, GL_UNSIGNED_BYTE, 10, c_void_p(6))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_UNSIGNED_BYTE, GL_TRUE, 10, c_void_p(7))

    return vbo, vao, len(array)


def create_program(name, **defines):
    return noxitu.opengl.Program(
        vs=f'{name}.vert.glsl',
        fs=f'{name}.frag.glsl',
        gs=f'{name}.geom.glsl',
        root=__file__,
        defines=defines
    )


def main():
    LOGGER.info('Loading data...')
    blocks = noxitu.minecraft.renderer.io.load_blocks()
    # viewport = noxitu.minecraft.renderer.io.load_viewport()    

    mega_chunks = compute_mega_chunks(blocks)
    blocks = None

    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)

    print('GL_VENDOR   =', str(glGetString(GL_VENDOR)))
    print('GL_RENDERER =', str(glGetString(GL_RENDERER)))

    clock = pygame.time.Clock()

    panorama_framebuffer, panorama_texture = noxitu.opengl.create_texture_framebuffer(PANORAMA_WIDTH, PANORAMA_HEIGHT)
    default_framebuffer = 0

    panoramabox_program = create_program('render_panorama_box')
    panorama_renderer_program = create_program('play2', PROJECTION_FUNC='project_to_panorama')
    program = create_program('play2')
    actual_attribute_locations = [program.attribute(attr) for attr in 'in_position in_direction in_color'.split()]
    assert actual_attribute_locations == [0, 1, 2], f'Invalid attribute locations: {actual_attribute_locations}.'

    mega_chunks_vaos = {
        key: create_vao(value)
        for key, value in mega_chunks.items()
    } 

    state = create_default_state(
        experimental=False,
        screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    redraw_panorama = True

    while True:
        pygame.display.set_caption(f'FPS = {clock.get_fps():.01f}')

        handle_events(state)

        if state.redraw or not LAZY_RENDERING:
            state.redraw = False

            camera_matrix = view.perspective(state.fov, state.screen_size[0]/state.screen_size[1])
            rotation_matrix = view.view(state.camera_yaw, state.camera_pitch, state.camera_roll)
            location_matrix = view.location(state.camera_position)
            camera_chunk = to_mega_chunk(state.camera_position)[::2]

            projectionview_matrix = camera_matrix @ rotation_matrix @ location_matrix

            if state.experimental or True:
                # redraw_panorama = False

                panorama_renderer_program.use()

                glUniform3f(panorama_renderer_program.uniform('camera_position'), *state.camera_position)
                glUniform3f(panorama_renderer_program.uniform('sun_direction'), *state.sun_direction)


                glBindFramebuffer(GL_FRAMEBUFFER, panorama_framebuffer)
                glViewport(0, 0, PANORAMA_WIDTH, PANORAMA_HEIGHT)

                # glBindFramebuffer(GL_FRAMEBUFFER, default_framebuffer)
                # glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                glEnable(GL_DEPTH_TEST)
                glEnable(GL_CULL_FACE)

                for chunk_key, (_, vao, n_blocks) in mega_chunks_vaos.items():
                    if np.linalg.norm(camera_chunk - chunk_key[::2], ord=np.inf) > state.view_distance:
                        glBindVertexArray(vao)
                        glDrawArrays(GL_POINTS, 0, n_blocks)

            if not state.experimental or True:
                glBindFramebuffer(GL_FRAMEBUFFER, default_framebuffer)
                glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

                panoramabox_program.use()
                panoramabox_program.set_uniform_mat3('ray_matrix', np.linalg.inv(projectionview_matrix[:3, :3]))

                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, panorama_texture)

                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                glEnable(GL_DEPTH_TEST)
                glEnable(GL_CULL_FACE)

                glBegin(GL_POINTS)
                glVertex2f(0, 0)
                glEnd()

                program.use()

                projectionview_matrix = camera_matrix @ rotation_matrix @ location_matrix

                program.set_uniform_mat4('projectionview_matrix', projectionview_matrix)
                glUniform3f(program.uniform('sun_direction'), *state.sun_direction)

                for chunk_key, (_, vao, n_blocks) in mega_chunks_vaos.items():
                    if np.linalg.norm(camera_chunk - chunk_key[::2], ord=np.inf) <= state.view_distance:
                        glBindVertexArray(vao)
                        glDrawArrays(GL_POINTS, 0, n_blocks)

            clock.tick()

            pygame.display.flip()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )

    main()
