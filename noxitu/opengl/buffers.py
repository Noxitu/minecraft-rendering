from ctypes import c_void_p

import numpy as np
from OpenGL.GL import *


def create_buffers(*arrays, usage):
    vbos = glGenBuffers(len(arrays))

    for vbo, array in zip(vbos if len(arrays) > 1 else [vbos], arrays):
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, vbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, array.size * array.itemsize, array, usage=usage)

    return vbos


def create_empty_buffer(*, shape, dtype, usage):
    vbo = glGenBuffers(1)

    glBindBuffer(GL_SHADER_STORAGE_BUFFER, vbo)
    glBufferData(GL_SHADER_STORAGE_BUFFER, np.prod(shape) * np.dtype(dtype).itemsize, usage=usage)

    return vbo


def read_buffer(vbo, *, into=None, like=None):
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, vbo)

    if into is not None:
        glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, into.size * into.itemsize, c_void_p(into.ctypes.data))

    if like is not None:
        buffer = glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, like.size * like.itemsize)
        return np.frombuffer(buffer, like=like)


def read_pixels(width, height):
    buffer = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    buffer = np.frombuffer(buffer, np.uint8)
    buffer = buffer.reshape(height, width, 3)[::-1]
    return buffer
