import pathlib
import sys
from OpenGL.GLU import projection

import numpy as np

sys.path.append(str(pathlib.Path(__file__).parent.parent))

import noxitu.minecraft.map.load
from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS

GLOBAL_COLORS = [MATERIAL_COLORS.get(MATERIALS.get(name)) for name in GLOBAL_PALETTE]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)


CUBE_VERTICES = np.array(np.meshgrid([0, 1], [0, 1], [0, 1], indexing='ij'), dtype=np.int8).T.reshape(-1, 3)
CUBE_FACES = np.array([
    [2, 6, 4, 0], [7, 3, 1, 5],
    [1, 0, 4, 5], [2, 3, 7, 6], 
    [3, 2, 0, 1], [6, 7, 5, 4],
])
CUBE_FACES = CUBE_FACES[:, ::-1]
FACE_COLOR_MUL = [0.9 * pow(0.92, i) for i in range(6)]
# FACE_COLOR_MUL = [1.0 for _ in range(6)]

def compute_face_mask(world, tqdm=lambda x: x):
    sy, sz, sx = world.shape
    print(f'  size = {sy*sz*sx/1024/1024/1024:.01f} GB')

    print('  mask[world]..')
    mask = GLOBAL_COLORS_MASK[world]

    coords = []
    # face_mask = np.full((sy, sz, sx), 0b111111, dtype=np.uint8)
    # face_mask[:] = mask.reshape(sy, sz, sx)

    def _full_idx(idx, direction):
        direction = slice(1, None) if direction == -1 else slice(None, -1)
        return tuple(direction if i == idx else slice(None) for i in range(3))

    def _border_idx(idx, direction):
        direction = 0 if direction == -1 else -1
        return tuple(direction if i == idx else slice(None) for i in range(3))

    def work(idx, direction):
        face_mask = mask.copy()
        face_mask[_border_idx(idx, direction)] = False
        face_mask[_full_idx(idx, direction)] &= ~mask[_full_idx(idx, -direction)]
        
        ys, zs, xs = np.where(face_mask)
        coords.append((
            ys.astype(np.uint8),
            zs.astype(np.int16),
            xs.astype(np.int16)
        ))

    all_args = [
        (2, -1), (2, 1),
        (0, -1), (0, 1),
        (1, -1), (1, 1),
        # (0, mask[:, :, 1:], mask[:, :, :-1]),
        # (1, mask[:, :, :-1], mask[:, :, 1:]),
        # (2, mask[1:, :, :], mask[:-1, :, :]),
        # (3, mask[:-1, :, :], mask[1:, :, :]),
        # (4, mask[:, 1:, :], mask[:, :-1, :]),
        # (5, mask[:, :-1, :], mask[:, 1:, :]),
    ]
    
    for args in tqdm(all_args):
        work(*args)

    n_faces = sum(len(cs[0]) for cs in coords)
    print(f'  len = {n_faces}   size = {n_faces*5/1024/1024/1024:.01f} GB')

    return n_faces, coords


def compute_face_colors(coords, world, colors):
    return [colors[world[ys, zs, xs]] for ys, zs, xs in coords]


def compute_faces(face_coords, face_colors):
    pts = np.concatenate([
        np.stack([xs, ys, zs], axis=1).reshape(-1, 1, 3) + CUBE_VERTICES[CUBE_FACES[i]].reshape(1, 4, 3)
        for i, (ys, zs, xs) in enumerate(face_coords)
    ])

    colors = np.concatenate([
        (FACE_COLOR_MUL[i] * colors).astype(np.uint8).reshape(-1, 1, 3) + np.zeros((1, 4, 3), dtype=np.uint8)
        for i, colors in enumerate(face_colors)
    ])

    return pts, colors

def main():
    offset, world = noxitu.minecraft.map.load.load('chunks')

    world = world[65:85, 20:52, 0:31]
    # world = world[:3, :2, :2]
    colors = GLOBAL_COLORS[world] / 255
    face_mask = compute_face_mask(world)

    compute_faces(face_mask, colors)

    # import matplotlib.pyplot as plt
    # ax = plt.subplot(111, projection='3d')

    # # ys, zs, xs = np.meshgrid(*map(np.arange, world.shape), indexing='ij')

    # # print(xs.shape, colors.shape)

    # # mask = face_mask[..., 0] | face_mask[..., 1] | face_mask[..., 2] | face_mask[..., 3] | face_mask[..., 4] | face_mask[..., 5]
    
    # # ax.scatter(xs[mask], zs[mask], ys[mask], c=colors[mask])

    # colors = np.array([[1, 0, 0]]*8)

    # ys, zs, xs = CUBE_VERTICES[:, 0], CUBE_VERTICES[:, 1], CUBE_VERTICES[:, 2]
    # colors[CUBE_FACES[4]] = [0, 1, 0]
    # ax.scatter(xs, zs, ys, c=colors)
    # plt.show()


if __name__ == '__main__':
    main()