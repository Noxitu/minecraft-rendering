import pathlib

from OpenGL.GL import *


SHADER_DIR = pathlib.Path(__file__).parent / 'shaders'


def _create_shader(shader_source, shader_type):
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


class Program:
    def __init__(self, vs, fs):
        with open(SHADER_DIR / f'{vs}.glsl') as fd:
            vertex_shader_source = fd.read()

        with open(SHADER_DIR / f'{fs}.glsl') as fd:
            fragment_shader_source = fd.read()

        self._program = glCreateProgram()

        vertex_shader = _create_shader(vertex_shader_source, GL_VERTEX_SHADER)
        fragment_shader = _create_shader(fragment_shader_source, GL_FRAGMENT_SHADER)

        try:
            glAttachShader(self._program, vertex_shader)
            glAttachShader(self._program, fragment_shader)
            glLinkProgram(self._program)

            if glGetProgramiv(self._program, GL_LINK_STATUS) != GL_TRUE:
                info = glGetProgramInfoLog(self._program)
                glDeleteProgram(self._program)
                raise RuntimeError('Error linking program: %s' % (info))

        finally:
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)

    def uniform(self, name):
        return glGetUniformLocation(self._program, name)

    def attribute(self, name):
        return glGetAttribLocation(self._program, name)

    def use(self):
        glUseProgram(self._program)

    def set_uniform_mat4(self, name, matrix):
        glUniformMatrix4fv(self.uniform(name), 1, GL_TRUE, matrix)


class ProgramFactory:
    def __init__(self):
        self._programs = {}

    def get(self, name):
        return self._programs[name]

    def create(self, name):
        program = self._programs.get(name)

        if program is None:
            print(f'Creating program "{name}"')
            program = Program(vs=f'{name}.vert', fs=f'{name}.frag')
            self._programs[name] = program

        return program
