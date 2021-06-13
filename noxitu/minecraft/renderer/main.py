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
import noxitu.minecraft.renderer.renderables2 as renderables


LAZY_RENDERING = False

# SCREEN_WIDTH, SCREEN_HEIGHT = 64, 36
# SCREEN_WIDTH, SCREEN_HEIGHT = 320, 180
# SCREEN_WIDTH, SCREEN_HEIGHT = 640, 360
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
# SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
# SCREEN_WIDTH, SCREEN_HEIGHT = 800, 100

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
    glVertexAttribPointer(0, 3, GL_SHORT, GL_FALSE, 12, c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribIPointer(1, 1, GL_UNSIGNED_BYTE, 12, c_void_p(6))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_UNSIGNED_BYTE, GL_TRUE, 12, c_void_p(7))

    glEnableVertexAttribArray(3)
    glVertexAttribIPointer(3, 1, GL_SHORT, 12, c_void_p(10))

    return vbo, vao, len(array)


def create_program(name, *, gs=True, **defines):
    return noxitu.opengl.Program(
        vs=f'{name}.vert.glsl',
        fs=f'{name}.frag.glsl',
        gs=f'{name}.geom.glsl' if gs else None,
        root=__file__,
        defines=defines
    )


def main():
    LOGGER.info('Loading data...')
    blocks = noxitu.minecraft.renderer.io.load_blocks()
    # viewport = noxitu.minecraft.renderer.io.load_viewport()
    texture_atlas, _ = noxitu.minecraft.renderer.io.load_texture_atlas()

    mega_chunks = compute_mega_chunks(blocks)
    blocks = None

    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)

    print('GL_VENDOR   =', str(glGetString(GL_VENDOR)))
    print('GL_RENDERER =', str(glGetString(GL_RENDERER)))

    clock = pygame.time.Clock()

    panorama_framebuffer = renderables.DoubleBuffer(
        noxitu.opengl.create_texture_framebuffer(PANORAMA_WIDTH, PANORAMA_HEIGHT),
        noxitu.opengl.create_texture_framebuffer(PANORAMA_WIDTH, PANORAMA_HEIGHT)
    )

    texture_atlas_tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D_ARRAY, texture_atlas_tex)
    glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA8, 16, 16, len(texture_atlas), 0, GL_RGBA, GL_UNSIGNED_BYTE, c_void_p(texture_atlas.ctypes.data))
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D_ARRAY)

    panoramabox_program = create_program('render_panorama_box', gs=False)
    panoramabox_program_debug = create_program('render_panorama_box', gs=False, BOX_VISIBILITY_FACTOR=0.5)
    panorama_renderer_program = create_program('play2', PROJECTION_MODE='PROJECTION_MODE_PANORAMA')
    main_program = create_program('play2')

    actual_attribute_locations = [main_program.attribute(attr) for attr in 'in_position in_direction in_color'.split()]
    assert actual_attribute_locations == [0, 1, 2], f'Invalid attribute locations: {actual_attribute_locations}.'

    mega_chunks_vaos = {
        key: create_vao(value)
        for key, value in mega_chunks.items()
    } 

    state = create_default_state(
        ensure_framebuffer=renderables.EnsureFunc(),
        ensure_program=renderables.EnsureFunc(),

        panorama_framebuffer=panorama_framebuffer,
        default_framebuffer=0,

        texture_atlas=texture_atlas_tex,

        panorama_renderer_program=panorama_renderer_program,
        panoramabox_program=panoramabox_program,
        main_program=main_program,

        mega_chunks_vaos=mega_chunks_vaos,

        flip=pygame.display.flip,
        panorama_position=None,
        panorama_area=None,

        screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),

        experimental=False,
    )

    frame_renderer = renderables.frame_renderer(state)

    while True:
        pygame.display.set_caption(f'FPS = {clock.get_fps():.01f}    '
                                   f'@ ({", ".join(f"{c:.01f}" for c in state.camera_position)})    '
                                   f'FoV = {state.fov}    '
                                   f'view distance = {state.view_distance}    ')

        handle_events(state)

        if state.experimental:
            state.panoramabox_program = panoramabox_program_debug
        else:
            state.panoramabox_program = panoramabox_program
        
        next(frame_renderer)

        clock.tick()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )

    main()
