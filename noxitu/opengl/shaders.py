import logging
import os

from OpenGL.GL import *


LOGGER = logging.getLogger(__name__)


def _create_shader(shader_source, shader_type, root=None, defines={}):
    if root is not None:
        if os.path.isfile(root):
            root = os.path.join(os.path.dirname(root), 'shaders')
        
        with open(os.path.join(root, shader_source)) as fd:
            shader_source = fd.read()

        for key, value in defines.items():
            shader_source = shader_source.replace(f'#define {key}', f'#define {key} {value} //')

    try:
        shader = glCreateShader(shader_type)
        glShaderSource(shader, shader_source)
        glCompileShader(shader)

        if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
            info = glGetShaderInfoLog(shader)
            raise RuntimeError('Shader compilation failed: %s' % (info))

        return shader

    except:
        glDeleteShader(shader)
        raise


_ALLOWED_SHADER_COMBINATIONS = {
    (True, False, False, False),
    (False, True, True, False),
    (False, True, True, True)
}


def _check_shader_combination(*args):
    args = tuple(arg is not None for arg in args)
    return args in _ALLOWED_SHADER_COMBINATIONS

class Program:
    def __init__(self, *, cs=None, vs=None, fs=None, gs=None, root=None, defines={}):
        if not _check_shader_combination(cs, vs, fs, gs):
            raise Exception('Invalid shader types provided.')

        self._program = glCreateProgram()

        shaders = []

        try:
            if cs is not None:
                shaders.append(_create_shader(cs, GL_COMPUTE_SHADER, root=root, defines=defines))

            if vs is not None:
                shaders.append(_create_shader(vs, GL_VERTEX_SHADER, root=root, defines=defines))

            if fs is not None:
                shaders.append(_create_shader(fs, GL_FRAGMENT_SHADER, root=root, defines=defines))

            if gs is not None:
                shaders.append(_create_shader(gs, GL_GEOMETRY_SHADER, root=root, defines=defines))

            for shader in shaders:
                glAttachShader(self._program, shader)

            glLinkProgram(self._program)

            if glGetProgramiv(self._program, GL_LINK_STATUS) != GL_TRUE:
                info = glGetProgramInfoLog(self._program)
                glDeleteProgram(self._program)
                raise RuntimeError('Error linking program: %s' % (info))

        finally:
            for shader in shaders:
                glDeleteShader(shader)

    def use(self):
        glUseProgram(self._program)

    def uniform(self, name):
        return glGetUniformLocation(self._program, name)

    def attribute(self, name):
        return glGetAttribLocation(self._program, name)

    def set_uniform_mat3(self, name, matrix):
        glUniformMatrix3fv(self.uniform(name), 1, GL_TRUE, matrix)

    def set_uniform_mat4(self, name, matrix):
        glUniformMatrix4fv(self.uniform(name), 1, GL_TRUE, matrix)


class ProgramFactory:
    def __init__(self, root):
        self._programs = {}
        self._root = root

    def get(self, name):
        return self._programs[name]

    def create(self, name, type='render'):
        program = self._programs.get(name)

        if program is None:
            LOGGER.info(f'Creating program "{name}"')

            if type == 'render':
                program = Program(vs=f'{name}.vert.glsl', fs=f'{name}.frag.glsl', root=self._root)
            elif type == 'compute':
                program = Program(cs=f'{name}.comp.glsl', root=self._root)

            self._programs[name] = program

        return program
