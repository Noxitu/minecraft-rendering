from OpenGL.GL import *

def create_buffer_renderer(program_factory):
    program = program_factory.create('buffer_renderer')

    def render(canvas_size):
        program.use()
        glUniform1iv(program.uniform('canvas_size'), 2, canvas_size)

        glBegin(GL_QUADS)
        glColor(1, 0, 0)
        glVertex2f(-1, -1)
        glColor(1, 1, 0)
        glVertex2f(1, -1)
        glColor(1, 0, 1)
        glVertex2f(1, 1)
        glColor(1, 1, 1)
        glVertex2f(-1, 1)
        glEnd()

    return render
