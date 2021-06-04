from types import SimpleNamespace  

import numpy as np


SUN_DIRECTION = np.array([1, 3, -3], dtype=float)
SUN_DIRECTION /= np.linalg.norm(SUN_DIRECTION)


def create_default_state(**kwargs):
    return SimpleNamespace(
        fov=80,
        camera_yaw=0,
        camera_pitch=0,
        camera_roll=0,
        camera_position=np.array([0, 100, 0], dtype=float),
        sun_direction=SUN_DIRECTION,
        redraw=True,
        view_distance=1,
        **kwargs
    )