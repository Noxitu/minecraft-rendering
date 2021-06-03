from ctypes import c_void_p

import numpy as np
from OpenGL.GL import *


def create_buffers(*arrays, usage):
    vbos = glGenBuffers(len(arrays))

    for vbo, array in zip(vbos if len(arrays) > 1 else [vbos], arrays):
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, vbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, array.size * array.itemsize, array, usage=usage)

    return vbos


def read_buffer(vbo, *, into=None, like=None):
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, vbo)

    if into is not None:
        glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, into.size * into.itemsize, c_void_p(into.ctypes.data))

    if like is not None:
        buffer = glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, like.size * like.itemsize)
        return np.frombuffer(buffer, like=like)
