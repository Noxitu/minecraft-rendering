import numpy as np

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import noxitu.pooling
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

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
SHADOW_WIDTH = SHADOW_HEIGHT = 1024*8

MODE_VIEW = 'view'
MODE_SHADOW = 'shadow'

ENABLE_SHADOWS = True


def init_rendering(program_factory):
    print('Reading data...')

    renderables = []

    # renderables.append(ChunksRenderer(r=25))
    # renderables.append(OriginMarker())
    # renderables.append(BlockRenderer(path='data/face_buffers/output.npz'))

    # renderables.append(BlockRenderer(path='data/face_buffers/test-nowater.npz'))
    # renderables.append(WaterRenderer(path='data/face_buffers/test-water.npz'))

    renderables.append(BlockRenderer(path='data/face_buffers/hermitcraft_s7_fresh.npz'))

    # renderables.append(BlockRenderer(path='data/face_buffers/hermitcraft_s7_fresh-nowater.npz'))
    # renderables.append(WaterRenderer(path='data/face_buffers/hermitcraft_s7_fresh-water.npz'))

    print('Creating OpenGL programs...')
    program_factory.create('renderer')
    program_factory.create('shadow')

    print('Creating OpenGL buffers...')

    for renderable in renderables:
        renderable.init_gpu(program_factory)

    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    # rbo = glGenRenderbuffers(1)
    # glBindRenderbuffer(GL_RENDERBUFFER, rbo)
    # glRenderbufferStorage(GL_RENDERBUFFER, GL_R32F, SCREEN_WIDTH, SCREEN_HEIGHT)
    # glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, rbo)

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_R32F, SHADOW_WIDTH, SHADOW_HEIGHT, 0, GL_RED, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

    rbo2 = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rbo2)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, SHADOW_WIDTH, SHADOW_HEIGHT)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rbo2)

    render_shadow = ENABLE_SHADOWS

    def draw():
        nonlocal render_shadow

        if render_shadow:
            print('Rendering shadow...')
            glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT)
            glBindFramebuffer(GL_FRAMEBUFFER, fbo)
            glClearColor(float('inf'), 0, 0, 0)
        else:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glClearColor(0, 0, 0, 0)

            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        for renderable in renderables:
            if render_shadow:
                renderable.render_shadow()
            else:
                renderable.render()

        if render_shadow:
            print('Max pooling...')
            buffer = glReadPixels(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT, GL_RED, GL_FLOAT)
            buffer = np.frombuffer(buffer, np.float32)
            buffer = buffer.reshape(SHADOW_HEIGHT, SHADOW_WIDTH)
            buffer2 = noxitu.pooling.max_pool(buffer)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_R32F, SHADOW_WIDTH, SHADOW_HEIGHT, 0, GL_RED, GL_FLOAT, buffer2)

            # buffer = glReadPixels(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT, GL_RED, GL_FLOAT)
            # buffer = np.frombuffer(buffer, np.float32)
            # buffer = buffer.reshape(SHADOW_HEIGHT, SHADOW_WIDTH)

            # print(np.amin(buffer), np.amax(buffer))
            # import matplotlib.pyplot as plt
            # plt.figure()
            # plt.imshow(buffer)
            # plt.figure()
            # plt.imshow(buffer2)
            # plt.show()
            print('Shadow done.')

            render_shadow = False
            glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            draw()
        else:
            pass
            # buffer = glReadPixels(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
            # buffer = np.frombuffer(buffer, np.uint8)
            # buffer = buffer.reshape(SCREEN_HEIGHT, SCREEN_WIDTH, 3)[..., ::-1]

            # glDrawPixels(SCREEN_WIDTH, SCREEN_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, buffer)

  
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
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)

    print('GL_VENDOR   =', str(glGetString(GL_VENDOR)))
    print('GL_RENDERER =', str(glGetString(GL_RENDERER)))

    fov = 80
    perspective_matrix = noxitu.minecraft.renderer.view.perspective(fov, SCREEN_WIDTH/SCREEN_HEIGHT, 50, 5000)

    ortho_matrix = np.array([
        [0.003, 0, 0, 0],
        [0, 0.003, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])

    program_factory = ProgramFactory()
    draw = init_rendering(program_factory)
    rendering_program = program_factory.get('renderer')
    shadow_program = program_factory.get('shadow')

    camera_yaw = 0
    camera_pitch = 0
    camera_roll = 0
    camera_position = np.array([MID_X, 100, MID_Z], dtype=float)

    rotation_matrix = noxitu.minecraft.renderer.view.view(camera_yaw, camera_pitch, camera_roll)
    location_matrix = noxitu.minecraft.renderer.view.location(camera_position)

    # shadow_matrix = perspective_matrix @ rotation_matrix @ location_matrix
    # shadow_matrix = ortho_matrix @ noxitu.minecraft.renderer.view.view(0, -90, 0)
    shadow_matrix = ortho_matrix @ noxitu.minecraft.renderer.view.view(90, -55, 5)

    sun_direction = (noxitu.minecraft.renderer.view.view(90, -55, 5).T @ [0, 0, 1, 1])[:3]
    sun_direction = sun_direction / np.linalg.norm(sun_direction)

    marker_position = None
    marker_rotation = None

    mode = MODE_VIEW

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
                    camera_pitch -= dy * 180 / SCREEN_HEIGHT

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
                    perspective_matrix = noxitu.minecraft.renderer.view.perspective(fov, SCREEN_WIDTH/SCREEN_HEIGHT, 5, 5000)
                    redraw = True

                elif event.unicode == '2':
                    if fov < 15:
                        fov += 1
                    elif fov < 175:
                        fov += 5
                    perspective_matrix = noxitu.minecraft.renderer.view.perspective(fov, SCREEN_WIDTH/SCREEN_HEIGHT, 5, 5000)
                    redraw = True
                    
                elif event.unicode == '3':
                    mode = {MODE_VIEW: MODE_SHADOW, MODE_SHADOW: MODE_VIEW}[mode]
                    redraw = True

                elif event.unicode == '4':
                    np.savez('data/viewports/viewport.npz',
                             camera=perspective_matrix[:3, :3],
                             rotation=rotation_matrix[:3, :3],
                             position=camera_position)
                    print('Saved projection matrix.')


            if any([
                event.type == pygame.QUIT,
                event.type == pygame.KEYUP and event.unicode == 'q'
            ]):
                pygame.quit()
                quit()

        if redraw:
            pygame.display.set_caption(f'({", ".join(f"{c:.0f}" for c in camera_position)})    FoV = {fov}')
            
            redraw = False

            rendering_program.use()
            if mode == MODE_VIEW:
                rendering_program.set_uniform_mat4('projectionview_matrix', perspective_matrix @ rotation_matrix @ location_matrix)
                glUniform2f(rendering_program.uniform('depth_range'), 1, 5000)
            else:
                rendering_program.set_uniform_mat4('projectionview_matrix', shadow_matrix)
                glUniform2f(rendering_program.uniform('depth_range'), -5000, 5000)

            rendering_program.set_uniform_mat4('shadow_projectionview_matrix', shadow_matrix)


            shadow_program.use()
            shadow_program.set_uniform_mat4('projectionview_matrix', shadow_matrix)
            # shadow_program.set_uniform_mat4('projectionview_matrix', ortho_matrix)
            glUniform2f(shadow_program.uniform('depth_range'), -5000, 5000)
            # glUniform2f(rendering_program.uniform('depth_range'), 1, 5000)

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