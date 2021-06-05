from types import SimpleNamespace

from OpenGL.GL import *
import numpy as np

import noxitu.minecraft.renderer.view as view


PANORAMA_WIDTH, PANORAMA_HEIGHT = 8000, 8000

##################

def to_mega_chunk(position):
    return np.floor(position / 256).astype(int)

##################

class DoubleBuffer:
    def __init__(self, buffer1, buffer2):
        self._buffers = [buffer1, buffer2]

    def swap(self):
        self._buffers.reverse()

    def active(self):
        return self._buffers[0]

    def busy(self):
        return self._buffers[1]


class EnsureFunc:
    def __init__(self):
        self._last_ensured = []

    def __call__(self, *args):
        if len(self._last_ensured) == len(args) and all(last is arg for last, arg in zip(self._last_ensured, args)):
            return
        
        if args:
            args[0](*args[1:])

        self._last_ensured = args


##############################

def use_panorama_framebuffer(context):
    framebuffer, _ = context.panorama_framebuffer.busy()

    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
    glViewport(0, 0, PANORAMA_WIDTH, PANORAMA_HEIGHT)


def use_screen_framebuffer(context):
    glBindFramebuffer(GL_FRAMEBUFFER, context.default_framebuffer)
    glViewport(0, 0, *context.screen_size)


#######

def use_panorama_program(context, frame):
    program = context.panorama_renderer_program
    program.use()

    glUniform3f(program.uniform('camera_position'), *frame.camera_position)
    glUniform3f(program.uniform('sun_direction'), *frame.sun_direction)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)


def use_panoramabox_program(context, frame):
    program = context.panoramabox_program
    _, panorama_texture = context.panorama_framebuffer.active()

    program.use()
    program.set_uniform_mat4('projectionview_matrix', frame.projectionview_matrix)
    glUniform3f(program.uniform('panorama_position'), *frame.panorama_position)

    glBindTexture(GL_TEXTURE_2D, panorama_texture)
    glActiveTexture(GL_TEXTURE0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)


def use_main_program(context, frame):
    program = context.main_program
    program.use()

    program.set_uniform_mat4('projectionview_matrix', frame.projectionview_matrix)
    glUniform3f(program.uniform('sun_direction'), *frame.sun_direction)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

#############

def panorama_renderer(context):
    while True:
        camera_chunk, view_distance = context.desired_area

        frame = SimpleNamespace(
            sun_direction = context.sun_direction.copy(),
            camera_position = context.camera_position.copy(),
        )

        context.ensure_framebuffer(use_panorama_framebuffer, context)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        mega_chunks = [
            chunk
            for chunk_key, chunk in context.mega_chunks_vaos.items()
            if np.linalg.norm(camera_chunk - chunk_key[::2], ord=np.inf) > view_distance
        ]

        for iter, (_, vao, n_blocks) in enumerate(mega_chunks):
            if iter != 0:
                yield False

            context.ensure_framebuffer(use_panorama_framebuffer, context)
            context.ensure_program(use_panorama_program, context, frame)

            glBindVertexArray(vao)
            glDrawArrays(GL_POINTS, 0, n_blocks)

        context.panorama_position = frame.camera_position
        context.panorama_area = camera_chunk, view_distance

        context.panorama_framebuffer.swap()
        yield True

################

def render_panoramabox(context, frame):
    if frame.panorama_position is None:
        return

    context.ensure_framebuffer(use_screen_framebuffer, context)
    context.ensure_program(use_panoramabox_program, context, frame)

    low_x, low_z = (frame.camera_chunk - frame.view_distance) * 256
    high_x, high_z = (frame.camera_chunk + frame.view_distance + 1) * 256

    low_y = min(0, frame.camera_position[1])
    high_y = max(256, frame.camera_position[1])

    glBegin(GL_TRIANGLE_STRIP)
    glVertex3f(low_x, high_y, low_z)
    glVertex3f(low_x, low_y, low_z)
    glVertex3f(high_x, high_y, low_z)
    glVertex3f(high_x, low_y, low_z)

    glVertex3f(high_x, high_y, high_z)
    glVertex3f(high_x, low_y, high_z)

    glVertex3f(low_x, high_y, high_z)
    glVertex3f(low_x, low_y, high_z)

    glVertex3f(low_x, high_y, low_z)
    glVertex3f(low_x, low_y, low_z)
    glEnd()

################

def render_close_chunks(context, frame):
    context.ensure_framebuffer(use_screen_framebuffer, context)
    context.ensure_program(use_main_program, context, frame)

    mega_chunks = [
        chunk
        for chunk_key, chunk in context.mega_chunks_vaos.items()
        if np.linalg.norm(frame.camera_chunk - chunk_key[::2], ord=np.inf) <= frame.view_distance
    ]

    for _, vao, n_blocks in mega_chunks:
        glBindVertexArray(vao)
        glDrawArrays(GL_POINTS, 0, n_blocks)

################

def frame_renderer(context):
    advance_panorama_frame = panorama_renderer(context)

    while True:
        camera_matrix = view.perspective(context.fov, context.screen_size[0]/context.screen_size[1])
        rotation_matrix = view.view(context.camera_yaw, context.camera_pitch, context.camera_roll)
        location_matrix = view.location(context.camera_position)

        camera_chunk = to_mega_chunk(context.camera_position)[::2]
        context.desired_area = camera_chunk, context.view_distance

        frame = SimpleNamespace(
            sun_direction = context.sun_direction,
            camera_position = context.camera_position,
            projectionview_matrix = camera_matrix @ rotation_matrix @ location_matrix,
        )

        for _ in range(10):
            if next(advance_panorama_frame):
                break

        frame.panorama_position = context.panorama_position
        frame.panorama_area = context.panorama_area

        if context.panorama_area is None:
            frame.camera_chunk, frame.view_distance = context.desired_area

        else:
            frame.camera_chunk, frame.view_distance = context.panorama_area

        context.ensure_framebuffer(use_screen_framebuffer, context)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        render_panoramabox(context, frame)
        render_close_chunks(context, frame)

        context.flip()
        yield True

