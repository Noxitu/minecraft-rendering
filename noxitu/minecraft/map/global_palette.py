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

    return blocks, states


BLOCKS, GLOBAL_PALETTE = _load()

MATERIALS = """
    # Comment water entires for "nowater" layer.
    water
    minecraft:water
    minecraft:bubble_column
    minecraft:tall_seagrass
    minecraft:seagrass
    minecraft:kelp
    minecraft:kelp_plant

    # Add water plants as plants for "nowater" layer.
    # plant
    # minecraft:tall_seagrass
    # minecraft:seagrass
    # minecraft:kelp
    # minecraft:kelp_plant

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
    minecraft:glass
    minecraft:lantern
    minecraft:activator_rail
    minecraft:comparator
    minecraft:detector_rail
    minecraft:daylight_detector
    minecraft:powered_rail
    minecraft:end_rod

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
    minecraft:birch_button
    minecraft:birch_door
    minecraft:birch_fence_gate
    minecraft:birch_pressure_plate
    minecraft:birch_sapling
    minecraft:birch_sign
    minecraft:birch_trapdoor
    minecraft:birch_wall_sign
    minecraft:birch_wood
    minecraft:stripped_birch_log
    minecraft:stripped_birch_wood
    minecraft:cut_sandstone_slab

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
    minecraft:packed_ice

    grass
    minecraft:grass_block
    minecraft:slime_block

    metal
    minecraft:grindstone
    minecraft:brewing_stand
    minecraft:damaged_anvil
    minecraft:anvil
    minecraft:chipped_anvil
    minecraft:blast_furnace
    minecraft:chain
    minecraft:hopper
    minecraft:iron_block
    minecraft:iron_door
    minecraft:iron_trapdoor
    minecraft:light_weighted_pressure_plate

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
    minecraft:acacia_sapling
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
    minecraft:allium
    minecraft:attached_melon_stem
    minecraft:attached_pumpkin_stem
    minecraft:bamboo_sapling
    minecraft:dried_kelp_block
    minecraft:flower_pot

    snow
    minecraft:snow
    minecraft:snow_block

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
    minecraft:granite_slab
    minecraft:granite_stairs
    minecraft:granite_wall
    minecraft:jungle_wall_sign
    minecraft:jungle_wood
    minecraft:stripped_jungle_log
    minecraft:stripped_jungle_wood
    minecraft:polished_granite_slab
    minecraft:polished_granite_stairs

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
    minecraft:mossy_cobblestone_slab
    minecraft:mossy_cobblestone_stairs
    minecraft:mossy_cobblestone_wall
    minecraft:observer
    minecraft:polished_andesite
    minecraft:polished_andesite_slab
    minecraft:polished_andesite_stairs
    minecraft:andesite_slab
    minecraft:andesite_stairs
    minecraft:andesite_wall
    minecraft:lodestone
    minecraft:stone_brick_wall
    minecraft:stone_button
    minecraft:stone_stairs
    minecraft:dead_brain_coral_block
    minecraft:dead_fire_coral_fan
    minecraft:dead_fire_coral_wall_fan
    minecraft:dead_horn_coral_block
    minecraft:dead_horn_coral_wall_fan
    minecraft:dropper
    minecraft:cobblestone_slab
    minecraft:piston
    minecraft:infested_cobblestone

    wood
    minecraft:chest
    minecraft:trapped_chest
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
    minecraft:oak_button
    minecraft:oak_sign
    minecraft:oak_wall_sign
    minecraft:oak_wood
    minecraft:jukebox
    minecraft:note_block
    minecraft:piston_head
    minecraft:barrel

    quartz
    minecraft:diorite
    minecraft:white_glazed_terracotta
    minecraft:sea_lantern
    minecraft:polished_diorite
    minecraft:white_bed
    minecraft:white_stained_glass_pane
    minecraft:quartz_block
    minecraft:quartz_bricks
    minecraft:quartz_pillar
    minecraft:quartz_slab
    minecraft:quartz_stairs
    minecraft:smooth_quartz
    minecraft:smooth_quartz_slab
    minecraft:smooth_quartz_stairs
    minecraft:diorite_slab
    minecraft:diorite_stairs
    minecraft:diorite_wall
    minecraft:white_banner
    minecraft:white_concrete
    minecraft:white_concrete_powder
    minecraft:white_shulker_box
    minecraft:white_stained_glass
    minecraft:white_wall_banner
    minecraft:target
    minecraft:polished_diorite_slab
    minecraft:polished_diorite_stairs
    minecraft:chiseled_quartz_block
    minecraft:beacon
    minecraft:cake

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
    minecraft:acacia_trapdoor
    minecraft:acacia_wall_sign
    minecraft:orange_banner
    minecraft:orange_carpet
    minecraft:orange_concrete
    minecraft:orange_concrete_powder
    minecraft:orange_glazed_terracotta
    minecraft:orange_shulker_box
    minecraft:orange_stained_glass
    minecraft:orange_stained_glass_pane
    minecraft:orange_wall_banner
    minecraft:orange_wool
    minecraft:potted_acacia_sapling
    minecraft:potted_allium
    minecraft:potted_azure_bluet
    minecraft:potted_bamboo
    minecraft:potted_birch_sapling
    minecraft:potted_blue_orchid
    minecraft:potted_brown_mushroom
    minecraft:potted_cornflower
    minecraft:potted_crimson_fungus
    minecraft:potted_dark_oak_sapling
    minecraft:potted_fern
    minecraft:potted_jungle_sapling
    minecraft:potted_lily_of_the_valley
    minecraft:potted_oak_sapling
    minecraft:potted_orange_tulip
    minecraft:potted_oxeye_daisy
    minecraft:potted_poppy
    minecraft:potted_red_tulip
    minecraft:potted_warped_fungus
    minecraft:potted_warped_roots
    minecraft:potted_wither_rose
    minecraft:stripped_acacia_log

    color_magenta
    minecraft:magenta_bed
    minecraft:magenta_carpet
    minecraft:magenta_concrete
    minecraft:magenta_concrete_powder
    minecraft:magenta_shulker_box
    minecraft:magenta_stained_glass
    minecraft:magenta_stained_glass_pane
    minecraft:magenta_wool

    color_light_blue
    minecraft:light_blue_bed
    minecraft:light_blue_carpet
    minecraft:light_blue_concrete
    minecraft:light_blue_concrete_powder
    minecraft:light_blue_glazed_terracotta
    minecraft:light_blue_stained_glass
    minecraft:light_blue_stained_glass_pane
    minecraft:light_blue_wall_banner
    minecraft:light_blue_wool

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
    minecraft:sponge
    minecraft:beehive
    minecraft:glowstone
    minecraft:honey_block
    minecraft:honeycomb_block
    minecraft:yellow_banner
    minecraft:yellow_concrete
    minecraft:yellow_concrete_powder
    minecraft:yellow_glazed_terracotta
    minecraft:yellow_shulker_box
    minecraft:yellow_stained_glass
    minecraft:yellow_wall_banner
    minecraft:shroomlight
    minecraft:scaffolding
    minecraft:end_stone
    minecraft:end_stone_bricks

    color_light_green
    minecraft:melon
    minecraft:lime_carpet
    minecraft:lime_bed
    minecraft:lime_banner
    minecraft:lime_concrete
    minecraft:lime_concrete_powder
    minecraft:lime_shulker_box
    minecraft:lime_stained_glass
    minecraft:lime_stained_glass_pane
    minecraft:lime_wall_banner
    minecraft:lime_wool
    
    color_pink
    minecraft:brain_coral
    minecraft:brain_coral_block
    minecraft:brain_coral_fan
    minecraft:brain_coral_wall_fan
    minecraft:pink_bed
    minecraft:pink_carpet
    minecraft:pink_concrete
    minecraft:pink_shulker_box
    minecraft:pink_stained_glass
    minecraft:pink_terracotta
    minecraft:pink_wall_banner
    minecraft:pink_wool

    color_gray
    minecraft:gray_bed
    minecraft:gray_carpet
    minecraft:gray_concrete
    minecraft:gray_concrete_powder
    minecraft:gray_shulker_box
    minecraft:gray_stained_glass
    minecraft:gray_stained_glass_pane
    minecraft:gray_terracotta
    minecraft:gray_wool
    minecraft:polished_basalt
    minecraft:basalt

    color_light_gray
    minecraft:light_gray_bed
    minecraft:light_gray_carpet
    minecraft:light_gray_concrete
    minecraft:light_gray_concrete_powder
    minecraft:light_gray_glazed_terracotta
    minecraft:light_gray_shulker_box
    minecraft:light_gray_stained_glass
    minecraft:light_gray_stained_glass_pane
    minecraft:light_gray_wall_banner
    minecraft:light_gray_wool

    color_cyan
    minecraft:prismarine
    minecraft:cyan_bed
    minecraft:prismarine_slab
    minecraft:prismarine_stairs
    minecraft:prismarine_wall
    minecraft:cyan_banner
    minecraft:cyan_carpet
    minecraft:cyan_concrete
    minecraft:cyan_concrete_powder
    minecraft:cyan_glazed_terracotta
    minecraft:cyan_shulker_box
    minecraft:cyan_stained_glass
    minecraft:cyan_stained_glass_pane
    minecraft:cyan_terracotta
    minecraft:cyan_wool

    color_purple
    minecraft:bubble_coral
    minecraft:bubble_coral_block
    minecraft:bubble_coral_fan
    minecraft:bubble_coral_wall_fan
    minecraft:mycelium
    minecraft:purple_bed
    minecraft:purple_carpet
    minecraft:purple_banner
    minecraft:purple_concrete
    minecraft:purple_concrete_powder
    minecraft:purple_glazed_terracotta
    minecraft:purple_shulker_box
    minecraft:purple_stained_glass
    minecraft:purple_stained_glass_pane
    minecraft:purple_terracotta
    minecraft:purple_wall_banner
    minecraft:purple_wool
    minecraft:purpur_slab
    minecraft:purpur_stairs
    minecraft:chorus_flower
    minecraft:chorus_plant
    minecraft:shulker_box

    color_blue
    minecraft:tube_coral
    minecraft:tube_coral_block
    minecraft:tube_coral_fan
    minecraft:tube_coral_wall_fan
    minecraft:blue_bed
    minecraft:blue_carpet
    minecraft:blue_concrete
    minecraft:blue_glazed_terracotta
    minecraft:blue_ice
    minecraft:blue_stained_glass
    minecraft:blue_stained_glass_pane
    minecraft:blue_wool

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
    minecraft:brown_bed
    minecraft:brown_carpet
    minecraft:brown_concrete
    minecraft:brown_concrete_powder
    minecraft:brown_glazed_terracotta
    minecraft:brown_shulker_box
    minecraft:brown_stained_glass
    minecraft:brown_stained_glass_pane
    minecraft:brown_wool
    minecraft:dark_oak_button
    minecraft:dark_oak_fence_gate
    minecraft:dark_oak_pressure_plate
    minecraft:dark_oak_sapling
    minecraft:dark_oak_sign
    minecraft:dark_oak_wall_sign
    minecraft:dark_oak_wood
    minecraft:soul_campfire
    minecraft:soul_fire
    minecraft:soul_lantern
    minecraft:soul_sand
    minecraft:soul_soil
    minecraft:soul_wall_torch
    minecraft:stripped_dark_oak_log
    minecraft:stripped_dark_oak_wood
    minecraft:netherite_block
    minecraft:ancient_debris
    minecraft:conduit

    color_green
    minecraft:sea_pickle
    minecraft:green_bed
    minecraft:green_carpet
    minecraft:green_concrete
    minecraft:green_concrete_powder
    minecraft:green_shulker_box
    minecraft:green_stained_glass
    minecraft:green_stained_glass_pane
    minecraft:green_terracotta
    minecraft:green_wall_banner
    minecraft:green_wool

    color_red
    minecraft:fire_coral
    minecraft:fire_coral_block
    minecraft:fire_coral_fan
    minecraft:fire_coral_wall_fan
    minecraft:red_mushroom
    minecraft:red_mushroom_block
    minecraft:bricks
    minecraft:red_bed
    minecraft:red_banner
    minecraft:red_carpet
    minecraft:red_concrete
    minecraft:red_concrete_powder
    minecraft:red_glazed_terracotta
    minecraft:red_nether_brick_slab
    minecraft:red_nether_brick_wall
    minecraft:red_nether_bricks
    minecraft:red_sandstone_wall
    minecraft:red_shulker_box
    minecraft:red_stained_glass
    minecraft:red_stained_glass_pane
    minecraft:red_wall_banner
    minecraft:red_wool
    minecraft:redstone_block
    minecraft:redstone_lamp
    minecraft:redstone_torch
    minecraft:redstone_wall_torch
    minecraft:smooth_red_sandstone_slab
    minecraft:smooth_red_sandstone_stairs
    minecraft:brick_slab
    minecraft:brick_stairs
    minecraft:brick_wall
    minecraft:chiseled_red_sandstone
    minecraft:cut_red_sandstone
    minecraft:chiseled_nether_bricks
    minecraft:cracked_nether_bricks
    minecraft:nether_brick_slab
    minecraft:nether_brick_stairs
    minecraft:nether_brick_wall
    minecraft:nether_bricks

    color_black
    minecraft:obsidian
    minecraft:crying_obsidian
    minecraft:polished_blackstone
    minecraft:polished_blackstone_brick_slab
    minecraft:polished_blackstone_brick_stairs
    minecraft:polished_blackstone_brick_wall
    minecraft:polished_blackstone_bricks
    minecraft:polished_blackstone_button
    minecraft:polished_blackstone_pressure_plate
    minecraft:polished_blackstone_slab
    minecraft:polished_blackstone_stairs
    minecraft:polished_blackstone_wall
    minecraft:black_carpet
    minecraft:black_concrete
    minecraft:black_concrete_powder
    minecraft:black_glazed_terracotta
    minecraft:black_shulker_box
    minecraft:black_stained_glass
    minecraft:black_stained_glass_pane
    minecraft:black_terracotta
    minecraft:black_wall_banner
    minecraft:black_wool
    minecraft:blackstone
    minecraft:blackstone_slab
    minecraft:blackstone_stairs
    minecraft:blackstone_wall
    minecraft:wither_rose
    minecraft:coal_block
    minecraft:chiseled_polished_blackstone
    minecraft:cracked_polished_blackstone_bricks
    minecraft:gilded_blackstone
    minecraft:enchanting_table
    minecraft:ender_chest

    gold
    minecraft:gold_block
    minecraft:bell
    minecraft:heavy_weighted_pressure_plate

    diamond
    minecraft:prismarine_bricks
    minecraft:dark_prismarine
    minecraft:prismarine_brick_slab
    minecraft:prismarine_brick_stairs
    minecraft:dark_prismarine_slab
    minecraft:dark_prismarine_stairs
    minecraft:diamond_block

    lapis
    minecraft:lapis_block

    emerald
    minecraft:emerald_block

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
    minecraft:spruce_button
    minecraft:spruce_sapling
    minecraft:spruce_wood
    minecraft:stripped_spruce_wood
    minecraft:stripped_spruce_log

    nether
    minecraft:netherrack
    minecraft:magma_block
    minecraft:nether_gold_ore
    minecraft:nether_sprouts
    minecraft:nether_wart
    minecraft:nether_wart_block

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
    minecraft:crimson_button
    minecraft:crimson_door
    minecraft:crimson_fence
    minecraft:crimson_fence_gate
    minecraft:crimson_fungus
    minecraft:crimson_hyphae
    minecraft:crimson_nylium
    minecraft:crimson_planks
    minecraft:crimson_roots
    minecraft:crimson_slab
    minecraft:crimson_stairs
    minecraft:crimson_stem
    minecraft:crimson_trapdoor
    minecraft:crimson_wall_sign

    crimson_stem
    minecraft:stripped_crimson_stem

    crimson_hyphae
    minecraft:twisting_vines
    minecraft:twisting_vines_plant
    minecraft:stripped_crimson_hyphae

    warped_nylium

    warped_stem
    minecraft:warped_button
    minecraft:warped_door
    minecraft:warped_fence
    minecraft:warped_fence_gate
    minecraft:warped_fungus
    minecraft:warped_hyphae
    minecraft:warped_nylium
    minecraft:warped_planks
    minecraft:warped_pressure_plate
    minecraft:warped_roots
    minecraft:warped_slab
    minecraft:warped_stairs
    minecraft:warped_stem
    minecraft:warped_trapdoor
    minecraft:warped_wall_sign
    minecraft:warped_wart_block
    minecraft:weeping_vines
    minecraft:weeping_vines_plant
    minecraft:stripped_warped_stem
    minecraft:stripped_warped_hyphae

    warped_hyphae

    warped_wart_block

"""

# MATERIALS = """
#     water
#     minecraft:water
#     minecraft:bubble_column
# """

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
