import logging

import numpy as np
import pygame

import noxitu.minecraft.renderer.view as view


LOGGER = logging.getLogger(__name__)


def handle_events(state):
    for event in pygame.event.get():
        if event.type == pygame.MOUSEMOTION:
            if event.buttons[0] == 1:
                dx, dy = event.rel

                state.camera_yaw += dx / 3
                state.camera_pitch -= dy * 180 / state.screen_size[1]

                if state.camera_pitch > 90: state.camera_pitch = 90
                if state.camera_pitch < -90: state.camera_pitch = -90

                # camera_roll -= dx / 12

                # if state.camera_roll > 12: state.camera_roll = 12
                # if state.camera_roll < -12: state.camera_roll = -12

                # print(camera_yaw, camera_pitch)

                state.redraw = True

            if event.buttons[2] == 1:
                dx, dy = event.rel

                rotation_matrix = view.view(
                    state.camera_yaw, state.camera_pitch, state.camera_roll
                )

                state.camera_position += 0.3 * (rotation_matrix.T @ [dx, 0, -dy, 1])[:-1]
                state.redraw = True

            if event.buttons[1] == 1:   
                dx, dy = event.rel

                rotation_matrix = view.view(
                    state.camera_yaw, state.camera_pitch, state.camera_roll
                )

                state.camera_position += 0.3 * (rotation_matrix.T @ [dx, dy, 0, 1])[:-1]
                state.redraw = True

        if event.type == pygame.KEYUP:
            if event.unicode == '1':
                if state.fov > 15:
                    state.fov -= 5
                elif state.fov > 1:
                    state.fov -= 1
                state.redraw = True

            if event.unicode == '2':
                if state.fov < 15:
                    state.fov += 1
                elif state.fov < 175:
                    state.fov += 5
                state.redraw = True
                
            elif event.unicode == '4':
                camera_matrix = view.perspective(
                    state.fov, state.screen_size[0]/state.screen_size[1]
                )

                rotation_matrix = view.view(
                    state.camera_yaw, state.camera_pitch, state.camera_roll
                )

                np.savez('data/viewports/viewport.npz',
                    camera=camera_matrix,
                    rotation=rotation_matrix,
                    position=state.camera_position,
                    sun_direction=state.sun_direction,
                    fov=state.fov,
                    camera_orientation=(state.camera_yaw, state.camera_pitch, state.camera_roll)
                )

                LOGGER.info('Saved viewport.')


        if any([event.type == pygame.QUIT, event.type == pygame.KEYUP and event.unicode == 'q']):
            pygame.quit()
            quit()
