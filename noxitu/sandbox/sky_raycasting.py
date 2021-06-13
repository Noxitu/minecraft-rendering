from ctypes import c_void_p
from noxitu.opengl.buffers import read_texture
import pathlib
import logging
from types import SimpleNamespace

import numpy as np
import pygame
from OpenGL.GL import *

import noxitu.opengl
import noxitu.opengl.controls
import noxitu.minecraft.renderer.view as view


# SCREEN_SIZE = 400, 300
SCREEN_SIZE = 800, 600
# SCREEN_SIZE = 1280, 720

LOGGER = logging.getLogger(__name__)


def ceil_div(val, div): return int((val + div - 1) // div)


@noxitu.opengl.controls.on_mouse_drag(0)
def drag_with_left(state, dx, dy):
    state.camera_yaw += dx / 3
    state.camera_pitch -= dy * 180 / SCREEN_SIZE[1]

    if state.camera_pitch > 90: state.camera_pitch = 90
    if state.camera_pitch < -90: state.camera_pitch = -90


@noxitu.opengl.controls.on_mouse_drag(2)
def drag_with_right(state, dx, dy):
    rotation_matrix = view.view(
        state.camera_yaw, state.camera_pitch, state.camera_roll
    )

    state.camera_position += 300.3 * (rotation_matrix.T @ [dx, 0, -dy, 1])[:-1]
    

@noxitu.opengl.controls.on_mouse_drag(1)
def drag_with_middle(state, dx, dy):
    rotation_matrix = view.view(
        state.camera_yaw, state.camera_pitch, state.camera_roll
    )

    state.camera_position += 300.3 * (rotation_matrix.T @ [dx, dy, 0, 1])[:-1]


@noxitu.opengl.controls.on_keyup('p')
def daytime_add(state):
    scale = abs(abs(state.daytime) - 3.14159 / 2) / 0.0314159
    state.daytime += 0.003 * (1 + scale)

@noxitu.opengl.controls.on_keyup('l')
def daytime_sub(state):
    scale = abs(abs(state.daytime) - 3.14159 / 2) / 0.0314159
    state.daytime -= 0.003 * (1 + scale)

@noxitu.opengl.controls.on_keyup('o')
def daytime_set(state):
    state.daytime = 3.14159 / 2

def main():
    noxitu.opengl.controls.register_quit_handler()

    noxitu.opengl.init(*SCREEN_SIZE)

    clock = pygame.time.Clock()

    program = noxitu.opengl.Program(
        vs='render_texture.vert.glsl',
        fs='render_texture.frag.glsl',
        root=__file__
    )

    sky_program = noxitu.opengl.Program(
        cs='generate_sky.comp.glsl',
        root=__file__
    )

    glEnable(GL_TEXTURE_2D)

    precomputed_p = np.load(pathlib.Path(__file__).parent / 'precomputed_p.npy').astype(np.float32)

    precomputed_p_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, precomputed_p_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_R32F, 1000, 100, 0, GL_RED, GL_FLOAT, c_void_p(precomputed_p.ctypes.data))

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, *SCREEN_SIZE, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glBindImageTexture(0, texture, 0, GL_FALSE, 0, GL_READ_WRITE, GL_RGBA32F)

    sky_program.use()
    glUniform1i(sky_program.uniform('output_image'), 0)

    state = SimpleNamespace(
        fov=80,
        camera_yaw=0,
        camera_pitch=0,
        camera_roll=0,
        camera_position=np.array([0, 6371000 + 10, 0], dtype=float),
        daytime=0
    )

    while True:
        pygame.display.set_caption(
            f'FPS = {clock.get_fps():.01f}    '
            f'{state.camera_position}    '
        )

        clock.tick(30)

        noxitu.opengl.controls.handle_events(state)

        camera_matrix = view.perspective(state.fov, SCREEN_SIZE[0]/SCREEN_SIZE[1])[:3, :3]
        rotation_matrix = view.view(state.camera_yaw, state.camera_pitch, state.camera_roll)[:3, :3]

        sky_program.use()
        sky_program.set_uniform_mat3('camera_projection_inv', np.linalg.inv(camera_matrix @ rotation_matrix))
        glUniform3f(sky_program.uniform('camera_position'), *state.camera_position)

        sun_direction = np.array([np.cos(state.daytime), 2*np.cos(state.daytime), np.sin(state.daytime)])
        sun_direction = sun_direction / np.linalg.norm(sun_direction)
        glUniform3f(sky_program.uniform('sun_direction'), *sun_direction)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, precomputed_p_texture)
        
        queries = []
        for _ in range(1):
            query, = glGenQueries(1)
            queries.append(query)

            glBeginQuery(GL_TIME_ELAPSED, query)
            glDispatchCompute(ceil_div(SCREEN_SIZE[0]*SCREEN_SIZE[1], 1024), 1, 1)
            glEndQuery(GL_TIME_ELAPSED)

            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            glFlush()

        # LOGGER.info('Waiting for jobs...')

        elapsed_time = np.zeros((1,), dtype=np.int64)
        for i, query in enumerate(queries):
            glGetQueryObjectui64v(query, GL_QUERY_RESULT, c_void_p(elapsed_time.ctypes.data))
            LOGGER.info(f'  Compute #{i} took \033[31m{elapsed_time[0]/1e6:.0f}\033[m ms')

        glDeleteQueries(len(queries), queries)
        glFinish()


        program.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)

        glBegin(GL_TRIANGLE_STRIP)
        glVertex2f(0, 0)
        glVertex2f(1, 0)
        glVertex2f(0, 1)
        glVertex2f(1, 1)
        glEnd()

        pygame.display.flip()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )

    main()
