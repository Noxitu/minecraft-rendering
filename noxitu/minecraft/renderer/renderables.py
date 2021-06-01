from ctypes import c_void_p

import numpy as np
from OpenGL.GL import *


class BlockRenderer:
    def __init__(self, *, buffer=None, path=None):
        if path is not None:
            assert buffer is None

            buffer = np.load(path)['buffer']

        assert buffer is not None
        print(f'shape={buffer.shape}    dtype={buffer.dtype}    size={buffer.size*buffer.itemsize/1024/1024:.0f} MB')
        self._buffer = buffer

    def init_gpu(self, program_factory):
        self._vbo = glGenBuffers(1)
        self._n = self._buffer.size

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, self._buffer.size * self._buffer.itemsize, self._buffer, GL_STATIC_DRAW)

        self._buffer = None

        # Render
        self._program = program_factory.get('renderer')

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(self._program.attribute('in_position'), 3, GL_SHORT, GL_FALSE, 9, c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(self._program.attribute('in_color'), 3, GL_UNSIGNED_BYTE, GL_TRUE, 9, c_void_p(6))

        # Shadow
        self._shadow_program = program_factory.get('shadow')

        self._shadow_vao = glGenVertexArrays(1)
        glBindVertexArray(self._shadow_vao)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(self._shadow_program.attribute('in_position'), 3, GL_SHORT, GL_FALSE, 9, c_void_p(0))

        # Clean state
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def before_render(self):
        pass

    def render(self):
        self.before_render()

        self._program.use()
        glBindVertexArray(self._vao)
        glDrawArrays(GL_QUADS, 0, 3*self._n)

        self.after_render()

    def render_shadow(self):
        self.before_render()

        self._shadow_program.use()
        glBindVertexArray(self._shadow_vao)
        glDrawArrays(GL_QUADS, 0, 3*self._n)

        self.after_render()

    def after_render(self):
        pass


class WaterRenderer(BlockRenderer):
    def __init__(self, *, buffer=None, path=None):
        super().__init__(buffer=buffer, path=path)

    def before_render(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_CONSTANT_COLOR, GL_ONE_MINUS_CONSTANT_COLOR)
        glBlendColor(0.75, 0.75, 0.75, 1.0)

    def after_render(self):
        glDisable(GL_BLEND)


class OriginMarker:
    def __init__(self):
        self._zero = np.array([0, 120, 0])

    def init_gpu(self, program_factory): pass

    def render(self):
        glUseProgram(0)
        glLineWidth(3)

        for row in np.eye(3):
            glColor3fv(row)
            glBegin(GL_LINES)
            glVertex3fv(self._zero)
            glVertex3fv(self._zero+10*row)
            glEnd()


class ChunksRenderer:
    def __init__(self, *, r, x=0, y=62.9, z=0, chunk_size=16):
        buffer = np.zeros((2, 2*r+1, 2, 3), dtype=np.int16)

        for i, c in enumerate(range(-r, r+1)):
            buffer[0, i] = (c, y, -r), (c, y, r)

            buffer[1, i] = (-r, y, c), (r, y, c)

        buffer[:, :, :, [0, 2]] *= chunk_size

        self._buffer = buffer.reshape(-1, 3)

    def init_gpu(self, program_factory):
        self._vbo = glGenBuffers(1)
        self._n = len(self._buffer)
        print(self._n, 'chunks')

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, self._buffer.size * self._buffer.itemsize, self._buffer, GL_STATIC_DRAW)

        self._buffer = None

    def render(self):
        glUseProgram(0)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_SHORT, 0, c_void_p(0))

        glDisableClientState(GL_COLOR_ARRAY)

        glLineWidth(1)
        glColor3f(1, 1, 1)
        glDrawArrays(GL_LINES, 0, 3*self._n)
