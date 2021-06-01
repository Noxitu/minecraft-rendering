import numpy as np
from numpy.testing import assert_allclose

import sys
print(sys.path)

import noxitu.minecraft.renderer.view


def expected(x, y, z):
    ret = np.zeros((4, 4))

    for col, row in enumerate([x, y, z]):
        value = 1 if row > 0 else -1
        row = abs(row) - 1
        ret[row, col] = value

    ret[3, 3] = 1

    return ret


def test_view_north():
    rotation_matrix = noxitu.minecraft.renderer.view.view(0, 0, 0)
    assert_allclose(rotation_matrix.astype(int), expected(1, -2, -3))


def test_view_east():
    rotation_matrix = noxitu.minecraft.renderer.view.view(90, 0, 0)
    assert_allclose(rotation_matrix.astype(int), expected(3, -2, 1))


def test_view_west():
    rotation_matrix = noxitu.minecraft.renderer.view.view(-90, 0, 0)
    assert_allclose(rotation_matrix.astype(int), expected(-3, -2, -1))


def test_view_down():
    rotation_matrix = noxitu.minecraft.renderer.view.view(0, -90, 0)
    assert_allclose(rotation_matrix.astype(int), expected(1, -3, 2))


def test_view_roll():
    rotation_matrix = noxitu.minecraft.renderer.view.view(0, 0, 90)
    assert_allclose(rotation_matrix.astype(int), expected(-2, -1, -3))


def test_view_down_with_yaw():
    print('path = ', sys.path)
    rotation_matrix = noxitu.minecraft.renderer.view.view(-90, -90, 0)
    assert_allclose(rotation_matrix.astype(int), expected(2, -3, -1))


def test_view_down_with_roll():
    print('path = ', sys.path)
    rotation_matrix = noxitu.minecraft.renderer.view.view(0, -90, -90)
    assert_allclose(rotation_matrix.astype(int), expected(2, -3, -1))