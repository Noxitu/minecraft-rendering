import math

import numpy as np


TRANSFORM_TO_NORTH = np.array([
    1, 0, 0, 0,
    0, -1, 0, 0,
    0, 0, -1, 0,
    0, 0, 0, 1
]).reshape(4, 4)

def perspective(fov_x, aspect, near, far):
    fov_x = math.pi*fov_x/180
    f = 1 / math.tan(fov_x / 2)

    return np.array([
        [f, 0, 0, 0],
        [0, f*aspect, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0]
    ])

def rotation_matrix(angle, axis):
    angle = math.pi*angle/180
    sin = math.sin(angle)
    cos = math.cos(angle)
    idx = [i for i in range(3) if i != axis]
    idx = [y for y in idx for _x in idx], [x for _y in idx for x in idx]

    ret = np.eye(4)
    ret[idx] = cos, -sin, sin, cos
    return ret

def view(yaw, pitch, roll):
    return rotation_matrix(-roll, 2) @ rotation_matrix(-pitch, 0) @ rotation_matrix(yaw, 1) @ TRANSFORM_TO_NORTH


def location(pos):
    ret = np.eye(4)
    ret[:3, 3] = -pos
    return ret
