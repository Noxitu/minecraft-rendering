import pygame


HANDLERS = []


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


def register_quit_handler(q=True):
    def quit_handler(*_):
        pygame.quit()
        quit()

    on_quit(quit_handler)

    if q:
        on_keyup('q')(quit_handler)


def handle_events(state):
    for event in pygame.event.get():
        for condition, handler in HANDLERS:
            if condition(event):
                handler(state, event)
