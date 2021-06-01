import pathlib
import sys

import numpy as np
from tqdm import tqdm

sys.path.append(str(pathlib.Path(__file__).parent.parent))

import noxitu.map.load
from noxitu.global_palette import GLOBAL_PALETTE, MATERIALS, MATERIAL_COLORS


GLOBAL_COLORS = [MATERIAL_COLORS.get(MATERIALS.get(name)) for name in GLOBAL_PALETTE]
GLOBAL_COLORS_MASK = np.array([c is not None for c in GLOBAL_COLORS])
GLOBAL_COLORS = np.array([c if c is not None else [0, 0, 0] for c in GLOBAL_COLORS], dtype=np.uint8)

if __name__ == '__main__':
    (oy, oz, ox), world = noxitu.map.load.load('chunks', tqdm)
    sy, sz, sx = world.shape

    ys, xs = np.meshgrid(np.arange(sy), np.arange(sx), indexing='ij')

    with open('cloud.txt', 'w') as output_fd:
                    
        def is_air(y, z, x):
            return not GLOBAL_COLORS_MASK[world[y, z, x]]

        for z in tqdm(range(1, sz-1)):
            for y in range(1, sy-1):
                for x in range(1, sx-1):
                    is_visible = not is_air(y, z, x) and any([
                        is_air(y-1, z, x),
                        is_air(y+1, z, x),
                        is_air(y, z-1, x),
                        is_air(y, z+1, x),
                        is_air(y, z, x-1),
                        is_air(y, z, x+1),
                    ])

                    if is_visible:
                        color = GLOBAL_COLORS[world[y, z, x]]
                        print(x, -z, y, *color, file=output_fd, flush=False)
        # for z in tqdm(range(sz)):
        #     section = world[:, z, :]

        #     colors = GLOBAL_COLORS[section]
        #     mask = GLOBAL_COLORS_MASK[section] & (ys > 55)

        #     for x, y, color in zip(xs[mask], ys[mask], colors[mask]):
        #         print(x, -z, y, *color, file=output_fd, flush=False)
