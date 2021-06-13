import numpy as np
from tqdm import tqdm

import noxitu.minecraft.map.load
from noxitu.minecraft.renderer.world_faces import compute_face_mask, compute_face_colors, compute_face_ids, compute_faces
from noxitu.minecraft.map.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS

GLOBAL_COLORS = [MATERIAL_COLORS.get(MATERIALS.get(name)) for name in GLOBAL_PALETTE]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)


def main():
    print('Loading world...')

    texture_mapping = np.load('data/texture_atlas.npz')['texture_mapping']

    S = 4000
    # S = 40
    # W = 140
    # H = 100
    W = 100
    H = 60

    # offset, world = noxitu.minecraft.map.load.load('data/chunks',
    #                                                tqdm=tqdm,
    #                                                x_range=slice(-W, W+1),
    #                                                y_range=slice(16, 256),
    #                                                z_range=slice(-H, H+1)
    #                                             )

    offset, world = noxitu.minecraft.map.load.load('data/chunks',
                                                   tqdm=tqdm,
                                                   x_range=slice(-207, 114),
                                                   y_range=slice(2, 256),
                                                   z_range=slice(-82, 126)
                                                )
    offset = offset[[2, 0, 1]]

    print(offset, world.shape)

    print('Computing faces...')
    n_faces, face_coords = compute_face_mask(world)
    face_colors = compute_face_colors(face_coords, world, GLOBAL_COLORS)
    face_ids = compute_face_ids(face_coords, world)
    world = None

    if False:
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
        np.savez_compressed('data/face_buffers/output.npz', buffer=buffer)

    else:
        face_directions = np.concatenate([
            [i]*len(colors) for i, colors in enumerate(face_colors)
        ])

        n = len(face_directions)

        buffer = np.zeros((n,), dtype=[('position', '3int16'), ('direction', 'uint8'), ('color', '3uint8'), ('texture_id', 'int16')])

        buffer['direction'] = face_directions + 1
        
        for i in range(6):
            ys, zs, xs = face_coords[i]
            buffer['position'][face_directions==i, 0] = xs
            buffer['position'][face_directions==i, 1] = ys
            buffer['position'][face_directions==i, 2] = zs
            buffer['color'][face_directions==i] = face_colors[i]
            buffer['texture_id'][face_directions==i] = texture_mapping[face_ids[i], i]

        buffer['position'] += offset

        print(f'Storing buffer with size {buffer.size*buffer.itemsize/1024/1024/1024:.02f} GB')

        np.savez_compressed('data/block_buffers/output.npz', buffer=buffer)

if __name__ == '__main__':
    main()
