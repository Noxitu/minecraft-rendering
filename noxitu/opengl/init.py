import logging
from OpenGL.GL import glGetString, GL_VENDOR, GL_RENDERER


def init(width, height, iconify=False):
    import pygame
    from pygame.locals import DOUBLEBUF, OPENGL

    logger = logging.getLogger(__name__)

    pygame.init()
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)

    if iconify:
        pygame.display.iconify()

    logger.info('GL_VENDOR   = %s', glGetString(GL_VENDOR).decode())
    logger.info('GL_RENDERER = %s', glGetString(GL_RENDERER).decode())
