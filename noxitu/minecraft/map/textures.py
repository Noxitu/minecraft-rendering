import pathlib
import json
from numpy.core.defchararray import split

from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt


WEST, EAST, BOTTOM, TOP, NORTH, SOUTH = range(6)


def _read_json(relative_path):
    path = pathlib.Path(__file__).parent / relative_path

    with open(str(path)) as fd:
        return json.load(fd)


def _read_image(relative_path):
    path = pathlib.Path(__file__).parent / relative_path
    img = plt.imread(str(path))

    if img.itemsize == 4:
        img = (255*img).astype(np.uint8)

    return img


def _load_blocks():
    blocks = _read_json('blocks.json')

    max_id = -1

    for block in blocks.values():
        for state in block['states']:
            max_id = max((max_id, state['id']))

    states = [None] * (max_id+1)

    for block_id, block in blocks.items():
        for state in block['states']:
            states[state['id']] = block_id, state

    return states


BLOCKS = _load_blocks()
BLOCKSTATES = {}
MODELS = {}


def split_id(minecraft_id):
    try:
        namespace, name = minecraft_id.split(':')
    except ValueError:
        namespace = 'minecraft'
        name = minecraft_id
        minecraft_id = f'{namespace}:{name}'

    return minecraft_id, namespace, name

def get_blockstates(block_id):
    block_id, namespace, name = split_id(block_id)
    ret = BLOCKSTATES.get(block_id)

    if ret is not None:
        return ret

    ret = BLOCKSTATES[block_id] = _read_json(f'../../../data/minecraft_data/assets/{namespace}/blockstates/{name}.json')
    return ret


def read_texture(texture_id):
    texture_id, namespace, name = split_id(texture_id)
    return _read_image(f'../../../data/minecraft_data/assets/{namespace}/textures/{name}.png')


def get_model(model_id):
    model_id, namespace, name = split_id(model_id)

    ret = MODELS.get(model_id)

    if ret is not None:
        return ret

    ret = MODELS[model_id] = _read_json(f'../../../data/minecraft_data/assets/{namespace}/models/{name}.json')
    return ret


def match_variant(properties, variants):
    matching = []

    for available_variant in variants:
        variant_properties = [item.split('=') for item in available_variant.split(',') if item]
        
        if all(properties.get(key, value) == value for key, value in variant_properties):
            matching.append(available_variant)

    assert len(matching) == 1
    return matching[0]

def main():
    import noxitu.minecraft.map.load
    RADIUS = 4000

    # _, world = noxitu.minecraft.map.load.load(
    #     'data/chunks',
    #     tqdm=tqdm,
    #     x_range=slice(-RADIUS, RADIUS+1),
    #     y_range=slice(0, 256),
    #     z_range=slice(-RADIUS, RADIUS+1)
    # )

    # world = np.unique(world)

    world = range(len(BLOCKS))

    textures = []
    texture2index = {}
    block2textures = np.full((len(BLOCKS), 6), -1, dtype=int)

    def assign_texture(state_id, texture, *dirs):
        texture_idx = texture2index.get(texture)
        if texture_idx is None:
            texture_idx = texture2index[texture] = len(textures)
            img = read_texture(texture)

            if img.shape[2] == 3:
                tqdm.write(f'Missing alpha channel for \033[033m{BLOCKS[state_id][0]}\033[m')
                h, w, _ = img.shape
                img2 = np.full((h, w, 4), 255, dtype=np.uint8)
                img2[..., :3] = img
                img = img2

            if img.shape != (16, 16, 4):
                tqdm.write(f'Unexpected texture shape for \033[031m{BLOCKS[state_id][0]}\033[m: {img.shape}')
                img = img[:16, :16]

            if img.shape != (16, 16, 4):
                raise Exception()

            textures.append(img)

        block2textures[state_id, dirs] = texture_idx

    for state_id in tqdm(world):
        block_id, state = BLOCKS[state_id]
        properties = state.get('properties', {})
        variant = ','.join(f'{key}={value}' for key, value in properties.items())

        blockstates = get_blockstates(block_id)
        
        if 'multipart' in blockstates:
            # print('  \033[031mmutlipart\033[m')
            continue

        # print(state_id, block_id, variant)
        models = blockstates['variants'].get(variant)

        if models is None:
            sub_variant = match_variant(properties, blockstates['variants'])
            models = blockstates['variants'].get(sub_variant)

        if isinstance(models, dict):
            models = [models]

        model = models[0] 
        # print(' ', models)

        model = get_model(model['model'])

        if block_id == 'minecraft:grass_block':
            assign_texture(state_id, 'block/grass_block_top', TOP)
            tqdm.write(f'Grass is {texture2index["block/grass_block_top"]}')
            assign_texture(state_id, 'block/grass_block_side', WEST, EAST, NORTH, SOUTH)
            assign_texture(state_id, 'block/dirt', BOTTOM)
            # tqdm.write(block_id)
        
        elif model.get('parent') == 'block/block':
            tqdm.write(f'\033[33m{block_id}\033[m inherits from block')
            

        elif model.get('parent') == 'minecraft:block/cube_bottom_top':
            assign_texture(state_id, model['textures']['top'], TOP)
            assign_texture(state_id, model['textures']['side'], WEST, EAST, NORTH, SOUTH)
            assign_texture(state_id, model['textures']['bottom'], BOTTOM)
            # tqdm.write(block_id)
        
        elif model.get('parent') == 'minecraft:block/cube_top':
            assign_texture(state_id, model['textures']['top'], TOP)
            assign_texture(state_id, model['textures']['side'], WEST, EAST, NORTH, SOUTH, BOTTOM)
            # tqdm.write(block_id)
    
        elif model.get('parent') == 'minecraft:block/cube_column':
            assign_texture(state_id, model['textures']['end'], TOP, BOTTOM)
            assign_texture(state_id, model['textures']['side'], WEST, EAST, NORTH, SOUTH)
            # tqdm.write(block_id)
        
        elif model.get('parent') == 'minecraft:block/cube_column_horizontal':
            assign_texture(state_id, model['textures']['end'], TOP, BOTTOM)
            assign_texture(state_id, model['textures']['side'], WEST, EAST, NORTH, SOUTH)
            # tqdm.write(block_id)
        
        elif model.get('parent') == 'minecraft:block/cube_all':
            assign_texture(state_id, model['textures']['all'], WEST, EAST, BOTTOM, TOP, NORTH, SOUTH)
            # tqdm.write(block_id)

        # print(state_id, block_id, properties)
    print()

    print(len(textures))
    print(textures[0].dtype)
    texture_atlas = np.stack(textures, axis=0)
    print(texture_atlas.shape, texture_atlas.dtype)
    np.savez('data/texture_atlas.npz', texture_atlas=texture_atlas, texture_mapping=block2textures)
    # plt.imshow(texture_atlas)
    # plt.show()


if __name__ == '__main__':
    main()
