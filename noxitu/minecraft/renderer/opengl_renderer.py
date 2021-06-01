import numpy as np

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import noxitu.minecraft.map.load
import noxitu.minecraft.renderer.view
from noxitu.minecraft.renderer.world_faces import compute_face_mask, compute_face_colors, compute_faces
from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS
from noxitu.minecraft.renderer.renderables import *
from noxitu.minecraft.renderer.shader import ProgramFactory

GLOBAL_COLORS = [MATERIAL_COLORS.get(MATERIALS.get(name)) for name in GLOBAL_PALETTE]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)


MID_X = 0
MID_Z = 0

def init_rendering(program_factory):
    print('Reading data...')

    renderables = []

    renderables.append(BlockRenderer(path='data/test-nowater.npz'))
    # renderables.append(ChunksRenderer(r=25))
    renderables.append(OriginMarker())
    renderables.append(WaterRenderer(path='data/test-water.npz'))

    print('Creating OpenGL programs...')
    program_factory.create('renderer')

    print('Creating OpenGL buffers...')

    for renderable in renderables:
        renderable.init_gpu(program_factory)

    def draw():
        for renderable in renderables:
            renderable.render()
  
    print('Initialization Done.')

    return draw


def draw_marker(marker_position, marker_rotation):
    glLineWidth(3)
    for row in np.eye(3):
        glColor3fv(row/2 + .5)
        glBegin(GL_LINES)
        glVertex3fv(marker_position)
        glVertex3fv(marker_position+2*(marker_rotation.T @ np.append(row, [1]))[:-1])
        glEnd()


def draw_sample_markers():
    draw_marker([0, 150, 0], noxitu.minecraft.renderer.view.view(0, 0, 0))
    draw_marker([5, 150, 0], noxitu.minecraft.renderer.view.view(45, 0, 0))
    draw_marker([10, 150, 0], noxitu.minecraft.renderer.view.view(90, 0, 0))

    draw_marker([0, 155, 0], noxitu.minecraft.renderer.view.view(0, 0, 0))
    draw_marker([5, 155, 0], noxitu.minecraft.renderer.view.view(0, -45, 0))
    draw_marker([10, 155, 0], noxitu.minecraft.renderer.view.view(0, -90, 0))

    draw_marker([0, 160, 0], noxitu.minecraft.renderer.view.view(0, 0, 0))
    draw_marker([5, 160, 0], noxitu.minecraft.renderer.view.view(0, 0, 45))
    draw_marker([10, 160, 0], noxitu.minecraft.renderer.view.view(0, 0, 90))


def main():
    pygame.init()
    screen_width, screen_height = 1500, 720
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)

    print('GL_VENDOR   =', str(glGetString(GL_VENDOR)))
    print('GL_RENDERER =', str(glGetString(GL_RENDERER)))

    fov = 80
    perspective_matrix = noxitu.minecraft.renderer.view.perspective(fov, screen_width/screen_height, 50, 5000)
    ortho_matrix = np.array([
        [0.003, 0, 0, 0],
        [0, 0, 0.003, 0],
        [0, -1, 0, 0],
        [0, 0, 0, 1],
    ])

    program_factory = ProgramFactory()
    draw = init_rendering(program_factory)
    rendering_program = program_factory.get('renderer')

    camera_yaw = 0
    camera_pitch = 0
    camera_roll = 0
    camera_position = np.array([MID_X, 100, MID_Z], dtype=float)

    marker_position = None
    marker_rotation = None

    redraw = True

    while True:
        if camera_roll != 0:
            eps = 0.3
            if camera_roll > eps:
                camera_roll -= max(eps, min(camera_roll / 10, 3*eps))
            elif camera_roll < -eps:
                camera_roll += max(eps, min(-camera_roll / 10, 3*eps))
            else:
                camera_roll = 0
            redraw = True

        rotation_matrix = noxitu.minecraft.renderer.view.view(camera_yaw, camera_pitch, camera_roll)
        location_matrix = noxitu.minecraft.renderer.view.location(camera_position)

        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.MOUSEMOTION:
                if event.buttons[0] == 1:
                    dx, dy = event.rel

                    camera_yaw += dx / 3
                    camera_pitch -= dy * 180 / screen_height

                    if camera_pitch > 90: camera_pitch = 90
                    if camera_pitch < -90: camera_pitch = -90

                    # camera_roll -= dx / 12

                    if camera_roll > 12: camera_roll = 12
                    if camera_roll < -12: camera_roll = -12

                    # print(camera_yaw, camera_pitch)

                    rotation_matrix = noxitu.minecraft.renderer.view.view(camera_yaw, camera_pitch, camera_roll)
                    redraw = True

                if event.buttons[2] == 1:
                    dx, dy = event.rel
                    camera_position += 0.3 * (rotation_matrix.T @ np.array([dx, 0, -dy, 1]))[:-1]

                    location_matrix = noxitu.minecraft.renderer.view.location(camera_position)
                    redraw = True

                if event.buttons[1] == 1:   
                    dx, dy = event.rel
                    camera_position += 0.3 * (rotation_matrix.T @ np.array([dx, dy, 0, 1]))[:-1]

                    location_matrix = noxitu.minecraft.renderer.view.location(camera_position)
                    redraw = True

            if event.type == pygame.KEYUP:
                # print(event)
                if event.unicode == 'c':
                    marker_position = camera_position.copy()
                    marker_rotation = rotation_matrix.copy()
                    redraw = True

                elif event.unicode == '1':
                    if fov > 15:
                        fov -= 5
                    elif fov > 1:
                        fov -= 1
                    perspective_matrix = noxitu.minecraft.renderer.view.perspective(fov, screen_width/screen_height, 5, 5000)
                    redraw = True

                elif event.unicode == '2':
                    if fov < 15:
                        fov += 1
                    elif fov < 175:
                        fov += 5
                    perspective_matrix = noxitu.minecraft.renderer.view.perspective(fov, screen_width/screen_height, 5, 5000)
                    redraw = True

            if any([
                event.type == pygame.QUIT,
                event.type == pygame.KEYUP and event.unicode == 'q'
            ]):
                pygame.quit()
                quit()

        if redraw:
            pygame.display.set_caption(f'({", ".join(f"{c:.0f}" for c in camera_position)})    FoV = {fov}')
            
            redraw = False
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            rendering_program.use()
            glUniformMatrix4fv(
                rendering_program.uniform('projectionview_matrix'),
                1,
                GL_TRUE, 
                perspective_matrix @ rotation_matrix @ location_matrix
                # ortho_matrix
            )
            # glUniform2f(rendering_program.uniform('depth_range'), -256, 0)
            glUniform2f(rendering_program.uniform('depth_range'), 1, 5000)

            glEnable(GL_DEPTH_TEST)
            glEnable(GL_CULL_FACE)
            draw()

            if marker_position is not None:
                # print(marker_position)
                draw_marker(marker_position, marker_rotation)

            # draw_origin_crosshair()
            # draw_sample_markers()

            pygame.display.flip()
        pygame.time.wait(10)


if __name__ == '__main__':
    main()