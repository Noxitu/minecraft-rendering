import logging

import numpy as np
import pygame

import noxitu.minecraft.renderer.view as view


LOGGER = logging.getLogger(__name__)

HANDLERS = []

# Decorators

def on_mouse_drag(button):
    def decorator(call):
        HANDLERS.append((
            lambda event: event.type == pygame.MOUSEMOTION and event.buttons[button] == 1,
            lambda state, event: call(state, event.rel[0], event.rel[1])
        ))

        return call

    return decorator


def on_keyup(key):
    def decorator(call):
        HANDLERS.append((
            lambda event: event.type == pygame.KEYUP and event.unicode == key,
            lambda state, _event: call(state)
        ))

        return call

    return decorator


def on_quit(call):
    HANDLERS.append((
        lambda event: event.type == pygame.QUIT,
        lambda state, _event: call(state)
    ))

    return call

# Events

@on_mouse_drag(0)
def drag_with_left(state, dx, dy):
    state.camera_yaw += dx / 3
    state.camera_pitch -= dy * 180 / state.screen_size[1]

    if state.camera_pitch > 90: state.camera_pitch = 90
    if state.camera_pitch < -90: state.camera_pitch = -90

    # camera_roll -= dx / 12

    # if state.camera_roll > 12: state.camera_roll = 12
    # if state.camera_roll < -12: state.camera_roll = -12

    # print(camera_yaw, camera_pitch)

    state.redraw = True


@on_mouse_drag(2)
def drag_with_right(state, dx, dy):
    rotation_matrix = view.view(
        state.camera_yaw, state.camera_pitch, state.camera_roll
    )

    state.camera_position += 0.3 * (rotation_matrix.T @ [dx, 0, -dy, 1])[:-1]
    state.redraw = True
    

@on_mouse_drag(1)
def drag_with_middle(state, dx, dy):
    rotation_matrix = view.view(
        state.camera_yaw, state.camera_pitch, state.camera_roll
    )

    state.camera_position += 0.3 * (rotation_matrix.T @ [dx, dy, 0, 1])[:-1]
    state.redraw = True


@on_keyup('1')
def decrease_fov(state):
    if state.fov > 15:
        state.fov -= 5
    elif state.fov > 1:
        state.fov -= 1
    state.redraw = True


@on_keyup('2')
def increase_fov(state):
    if state.fov < 15:
        state.fov += 1
    elif state.fov < 175:
        state.fov += 5
    state.redraw = True


@on_keyup('4')
def save_viewport(state):     
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

    LOGGER.info('Saved viewport.npz')

    import noxitu.opengl
    import matplotlib.pyplot as plt

    image = noxitu.opengl.read_pixels(*state.screen_size)
    plt.imsave('data/viewports/viewport.png', image)

    LOGGER.info('Saved viewport.png')


@on_keyup('5')
def decrease_view_distance(state):
    if state.view_distance > 0:
        state.view_distance -= 1
        state.redraw = True


@on_keyup('6')
def decrease_view_distance(state):
    state.view_distance += 1
    state.redraw = True


@on_keyup('0')
def decrease_view_distance(state):
    state.experimental = not state.experimental
    state.redraw = True


@on_keyup('q')
@on_quit
def decrease_fov(_state):
    pygame.quit()
    quit()

# Handler

def handle_events(state):
    for event in pygame.event.get():
        for condition, handler in HANDLERS:
            if condition(event):
                handler(state, event)
