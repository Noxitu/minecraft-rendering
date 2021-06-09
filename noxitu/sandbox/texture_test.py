from ctypes import c_void_p
import logging

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

import noxitu.opengl


SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

LOGGER = logging.getLogger(__name__)

VS = """
    #version 330 core

    layout(location=0) in vec3 in_position;

    void main(void)
    {
        gl_Position = vec4(in_position, 1);
    }
"""

FS = """
#version 330

in vec2 texcoord;
out vec4 out_color;

uniform sampler2DArray texture_atlas;

void main(void)
{
    out_color = texture(texture_atlas, vec3(texcoord, 1));
}
"""

GS = """
#version 330 core

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

out vec2 texcoord;

void main() {
    gl_Position = vec4(-1, 1, 0, 1);
    texcoord = vec2(0, 0);
    EmitVertex();

    gl_Position = vec4(1, 1, 0, 1);
    texcoord = vec2(1, 0);
    EmitVertex();

    gl_Position = vec4(-1, -1, 0, 1);
    texcoord = vec2(0, 1);
    EmitVertex();

    gl_Position = vec4(1, -1, 0, 1);
    texcoord = vec2(1, 1);
    EmitVertex();
    
    EndPrimitive();
}  
"""

def main():
    noxitu.opengl.init(SCREEN_WIDTH, SCREEN_HEIGHT)

    glEnable(GL_TEXTURE_2D)

    program = noxitu.opengl.Program(
        vs=VS,
        fs=FS,
        gs=GS,
    )

    texture_atlas = np.load('data/texture_atlas.npz')['texture_atlas']

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D_ARRAY, texture)
    glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA8, 16, 16, len(texture_atlas), 0, GL_RGBA, GL_UNSIGNED_BYTE, c_void_p(texture_atlas.ctypes.data))
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glActiveTexture(GL_TEXTURE0)

    program.use()

    clock = pygame.time.Clock()
    while True:
        glBegin(GL_POINTS)
        glVertex2f(0, 0)
        glEnd()

        pygame.display.flip()

        clock.tick(10)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or ev.type == pygame.KEYUP and ev.unicode == 'q':
                break

        else:
            continue
        break



if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s -- %(message)s',
        level=logging.INFO
    )

    main()
