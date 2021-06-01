import json
import pathlib


def _load():
    path = pathlib.Path(__file__).parent / 'blocks.json'
    
    with open(str(path)) as fd:
        blocks = json.load(fd)

    max_id = -1

    for block in blocks.values():
        for state in block['states']:
            max_id = max((max_id, state['id']))

    states = [None] * (max_id+1)

    for block_id, block in blocks.items():
        for state in block['states']:
            states[state['id']] = block_id

    return states


GLOBAL_PALETTE = _load()

MATERIALS = """
    none
    minecraft:air
    minecraft:cave_air
    minecraft:barrier
    minecraft:wall_torch
    minecraft:rail
    minecraft:torch
    minecraft:iron_bars
    minecraft:tripwire
    minecraft:tripwire_hook
    minecraft:lever
    minecraft:repeater
    minecraft:ladder
    minecraft:redstone_wire
    minecraft:glass_pane
    minecraft:grass_path

    sand
    minecraft:sand
    minecraft:sandstone
    minecraft:cut_sandstone
    minecraft:birch_fence
    minecraft:birch_log
    minecraft:birch_planks
    minecraft:birch_stairs
    minecraft:smooth_sandstone
    minecraft:smooth_sandstone_slab
    minecraft:smooth_sandstone_stairs
    minecraft:birch_slab
    minecraft:chiseled_sandstone
    minecraft:sandstone_slab
    minecraft:sandstone_stairs
    minecraft:sandstone_wall
    minecraft:bone_block

    wool
    minecraft:cobweb
    minecraft:mushroom_stem
    minecraft:white_carpet
    minecraft:white_wool

    fire
    minecraft:lava
    minecraft:fire
    minecraft:tnt

    ice
    minecraft:ice

    grass
    minecraft:grass_block

    metal
    minecraft:grindstone
    minecraft:brewing_stand

    plant
    minecraft:grass
    minecraft:birch_leaves
    minecraft:oak_leaves
    minecraft:poppy
    minecraft:tall_grass
    minecraft:cornflower
    minecraft:oxeye_daisy
    minecraft:dandelion
    minecraft:azure_bluet
    minecraft:cactus
    minecraft:lilac
    minecraft:lily_of_the_valley
    minecraft:peony
    minecraft:rose_bush
    minecraft:sugar_cane
    minecraft:spruce_leaves
    minecraft:white_tulip
    minecraft:acacia_leaves
    minecraft:bamboo
    minecraft:cocoa
    minecraft:beetroots
    minecraft:fern
    minecraft:jungle_leaves
    minecraft:dark_oak_leaves
    minecraft:red_tulip
    minecraft:pumpkin_stem
    minecraft:wheat
    minecraft:vine
    minecraft:sweet_berry_bush
    minecraft:pink_tulip
    minecraft:orange_tulip
    minecraft:potatoes
    minecraft:potted_cactus
    minecraft:potted_dead_bush
    minecraft:potted_spruce_sapling
    minecraft:large_fern
    minecraft:melon_stem
    minecraft:blue_orchid
    minecraft:carrots
    minecraft:lily_pad
    minecraft:potted_dandelion
    minecraft:sunflower

    snow
    minecraft:snow

    clay
    minecraft:clay
    minecraft:infested_stone

    dirt
    minecraft:dirt
    minecraft:granite
    minecraft:polished_granite
    minecraft:brown_mushroom_block
    minecraft:jungle_button
    minecraft:jungle_door
    minecraft:jungle_fence
    minecraft:jungle_fence_gate
    minecraft:jungle_log
    minecraft:jungle_slab
    minecraft:jungle_trapdoor
    minecraft:farmland
    minecraft:coarse_dirt

    stone
    minecraft:stone
    minecraft:cobblestone
    minecraft:gravel
    minecraft:andesite
    minecraft:coal_ore
    minecraft:iron_ore
    minecraft:lapis_ore
    minecraft:redstone_ore
    minecraft:gold_ore
    minecraft:diamond_ore
    minecraft:emerald_ore
    minecraft:bedrock
    minecraft:stone_brick_slab
    minecraft:stone_brick_stairs
    minecraft:mossy_cobblestone
    minecraft:mossy_stone_brick_slab
    minecraft:mossy_stone_brick_stairs
    minecraft:spawner
    minecraft:cauldron
    minecraft:stonecutter
    minecraft:chiseled_stone_bricks
    minecraft:cobblestone_stairs
    minecraft:cobblestone_wall
    minecraft:cracked_stone_bricks
    minecraft:dispenser
    minecraft:stone_bricks
    minecraft:sticky_piston
    minecraft:smooth_stone_slab
    minecraft:smoker
    minecraft:stone_slab
    minecraft:mossy_stone_bricks
    minecraft:stone_pressure_plate
    minecraft:smooth_stone
    minecraft:mossy_stone_brick_wall
    minecraft:jigsaw
    minecraft:furnace
 
    water
    # minecraft:water
    # minecraft:bubble_column
    # minecraft:tall_seagrass
    # minecraft:seagrass
    # minecraft:kelp
    # minecraft:kelp_plant

    plant
    minecraft:tall_seagrass
    minecraft:seagrass
    minecraft:kelp
    minecraft:kelp_plant

    wood
    minecraft:chest
    minecraft:jungle_planks
    minecraft:jungle_stairs
    minecraft:oak_fence
    minecraft:oak_log
    minecraft:oak_planks
    minecraft:oak_stairs
    minecraft:oak_trapdoor
    minecraft:dead_bush
    minecraft:composter
    minecraft:crafting_table
    minecraft:bookshelf
    minecraft:cartography_table
    minecraft:smithing_table
    minecraft:lectern
    minecraft:oak_slab
    minecraft:oak_door
    minecraft:oak_fence_gate
    minecraft:oak_pressure_plate
    minecraft:stripped_oak_log
    minecraft:stripped_oak_wood
    minecraft:fletching_table
    minecraft:loom

    quartz
    minecraft:diorite
    minecraft:white_glazed_terracotta
    minecraft:sea_lantern
    minecraft:polished_diorite
    minecraft:white_bed
    minecraft:white_stained_glass_pane

    color_orange
    minecraft:red_sand
    minecraft:pumpkin
    minecraft:terracotta
    minecraft:acacia_log
    minecraft:jack_o_lantern
    minecraft:acacia_door
    minecraft:acacia_fence
    minecraft:acacia_fence_gate
    minecraft:acacia_planks
    minecraft:acacia_pressure_plate
    minecraft:acacia_slab
    minecraft:acacia_stairs
    minecraft:acacia_wood
    minecraft:orange_bed

    color_magenta

    color_light_blue

    color_yellow
    minecraft:horn_coral
    minecraft:horn_coral_block
    minecraft:horn_coral_fan
    minecraft:horn_coral_wall_fan
    minecraft:bee_nest
    minecraft:hay_block
    minecraft:yellow_bed
    minecraft:yellow_carpet
    minecraft:yellow_stained_glass_pane
    minecraft:yellow_wool
    minecraft:wet_sponge

    color_light_green
    minecraft:melon
    minecraft:lime_carpet
    minecraft:lime_bed

    color_pink
    minecraft:brain_coral
    minecraft:brain_coral_block
    minecraft:brain_coral_fan
    minecraft:brain_coral_wall_fan

    color_gray

    color_light_gray

    color_cyan
    minecraft:prismarine
    minecraft:cyan_bed

    color_purple
    minecraft:bubble_coral
    minecraft:bubble_coral_block
    minecraft:bubble_coral_fan
    minecraft:bubble_coral_wall_fan
    minecraft:mycelium
    minecraft:purple_bed
    minecraft:purple_carpet

    color_blue
    minecraft:tube_coral
    minecraft:tube_coral_block
    minecraft:tube_coral_fan
    minecraft:tube_coral_wall_fan
    minecraft:blue_bed

    color_brown
    minecraft:brown_mushroom
    minecraft:dark_oak_fence
    minecraft:dark_oak_log
    minecraft:dark_oak_planks
    minecraft:dark_oak_stairs
    minecraft:dark_oak_door
    minecraft:dark_oak_slab
    minecraft:dark_oak_trapdoor
    minecraft:brown_wall_banner

    color_green
    minecraft:sea_pickle
    minecraft:green_bed
    minecraft:green_carpet

    color_red
    minecraft:fire_coral
    minecraft:fire_coral_block
    minecraft:fire_coral_fan
    minecraft:fire_coral_wall_fan
    minecraft:red_mushroom
    minecraft:red_mushroom_block
    minecraft:bricks
    minecraft:red_bed

    color_black
    minecraft:obsidian
    minecraft:crying_obsidian

    gold
    minecraft:gold_block
    minecraft:bell

    diamond
    minecraft:prismarine_bricks
    minecraft:dark_prismarine

    lapis

    emerald

    podzol
    minecraft:spruce_door
    minecraft:spruce_fence_gate
    minecraft:spruce_log
    minecraft:spruce_slab
    minecraft:spruce_trapdoor
    minecraft:spruce_wall_sign
    minecraft:campfire
    minecraft:podzol
    minecraft:spruce_fence
    minecraft:spruce_planks
    minecraft:spruce_stairs
    minecraft:spruce_pressure_plate

    nether
    minecraft:netherrack
    minecraft:magma_block

    terracotta_white
    minecraft:white_terracotta

    terracotta_orange
    minecraft:orange_terracotta

    terracotta_magenta

    terracotta_light_blue
    minecraft:light_blue_terracotta

    terracotta_yellow
    minecraft:yellow_terracotta

    terracotta_light_green
    minecraft:lime_terracotta

    terracotta_pink

    terracotta_gray

    terracotta_light_gray
    minecraft:light_gray_terracotta

    terracotta_cyan

    terracotta_purple

    terracotta_blue
    minecraft:blue_terracotta

    terracotta_brown
    minecraft:brown_terracotta

    terracotta_green

    terracotta_red
    minecraft:red_terracotta

    terracotta_black

    crimson_nylium

    crimson_stem

    crimson_hyphae

    warped_nylium

    warped_stem

    warped_hyphae

    warped_wart_block

"""

MATERIALS = """
    water
    minecraft:water
    minecraft:bubble_column
"""

# MATERIALS = """
#     fire
#     minecraft:barrier
# """

def _parse_materials():
    material = None
    for item in MATERIALS.split('\n'):
        item = item.split('#')[0].strip()
        if not item:
            continue    

        if item.startswith('minecraft:'):
            yield item, material
        else:
            material = item

MATERIALS = dict(_parse_materials())

MATERIAL_COLORS = """
    grass                    127, 178, 56
    sand                     247, 233, 163
    wool                     199, 199, 199
    fire                     255, 0, 0
    ice                      160, 160, 255
    metal                    167, 167, 167
    plant                    0, 124, 0
    snow                     255, 255, 255
    clay                     164, 168, 184
    dirt                     151, 109, 77
    stone                    112, 112, 112
    water                    64, 64, 255
    wood                     143, 119, 72
    quartz                   255, 252, 245
    color_orange             216, 127, 51
    color_magenta            178, 76, 216
    color_light_blue         102, 153, 216
    color_yellow             229, 229, 51
    color_light_green        127, 204, 25
    color_pink               242, 127, 165
    color_gray               76, 76, 76
    color_light_gray         153, 153, 153
    color_cyan               76, 127, 153
    color_purple             127, 63, 178
    color_blue               51, 76, 178
    color_brown              102, 76, 51
    color_green              102, 127, 51
    color_red                153, 51, 51
    color_black              25, 25, 25
    gold                     250, 238, 77
    diamond                  92, 219, 213
    lapis                    74, 128, 255
    emerald                  0, 217, 58
    podzol                   129, 86, 49
    nether                   112, 2, 0
    terracotta_white         209, 177, 161
    terracotta_orange        159, 82, 36
    terracotta_magenta       149, 87, 108
    terracotta_light_blue    112, 108, 138
    terracotta_yellow        186, 133, 36
    terracotta_light_green   103, 117, 53
    terracotta_pink          160, 77, 78
    terracotta_gray          57, 41, 35
    terracotta_light_gray    135, 107, 98
    terracotta_cyan          87, 92, 92
    terracotta_purple        122, 73, 88
    terracotta_blue          76, 62, 92
    terracotta_brown         76, 50, 35
    terracotta_green         76, 82, 42
    terracotta_red           142, 60, 46
    terracotta_black         37, 22, 16
    crimson_nylium           189, 48, 49
    crimson_stem             148, 63, 97
    crimson_hyphae           92, 25, 29
    warped_nylium            22, 126, 134
    warped_stem              58, 142, 140
    warped_hyphae            86, 44, 62
    warped_wart_block        20, 180, 13
""".replace(',', ' ')

MATERIAL_COLORS = MATERIAL_COLORS.split()
MATERIAL_COLORS = {key: [int(c) for c in (r, g, b)] for key, r, g, b in zip(MATERIAL_COLORS[0::4], MATERIAL_COLORS[1::4], MATERIAL_COLORS[2::4], MATERIAL_COLORS[3::4])}
