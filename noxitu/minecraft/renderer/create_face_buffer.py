import numpy as np
from tqdm import tqdm

import noxitu.minecraft.map.load
from noxitu.minecraft.renderer.world_faces import compute_face_mask, compute_face_colors, compute_faces
from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS

GLOBAL_COLORS = [MATERIAL_COLORS.get(MATERIALS.get(name)) for name in GLOBAL_PALETTE]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)


def main():
    print('Loading world...')

    S = 24

    offset, world = noxitu.minecraft.map.load.load('data/chunks',
                                                   tqdm=tqdm,
                                                   x_range=slice(-S, S+1),
                                                   y_range=slice(16, 256),
                                                   z_range=slice(-S, S+1)
                                                )
    offset = offset[[2, 0, 1]]

    print(offset, world.shape)

    print('Computing faces...')
    n_faces, face_coords = compute_face_mask(world)
    face_colors = compute_face_colors(face_coords, world, GLOBAL_COLORS)
    world = None

    print('Computing vertices...')
    print(f'  size = {n_faces*3*4*2/1024/1024/1024:.01f} GB')
    vertices, vertex_colors = compute_faces(face_coords, face_colors)
    face_coords = face_coords = None
    vertices += offset
    
    print('Creating buffer...')

    n = len(vertices)

    buffer = np.zeros((n, 4), dtype=[('vertices', '3int16'), ('colors', '3uint8')])
    buffer['vertices'] = vertices
    buffer['colors'] = vertex_colors
    vertices = vertex_colors = None

    print('Saving buffer...')
    np.savez_compressed('data/output.npz', buffer=buffer)


if __name__ == '__main__':
    main()
