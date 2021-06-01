

BIOMES = """
    0    ocean   blue
    1    plains
    2    desert  yellow
    3    mountains  gray
    4    forest
    5    taiga
    6    swamp
    7    river  blue
    8    nether_wastes
    9    the_end
    10   frozen_ocean  blue
    11   frozen_river  blue
    12   snowy_tundra  white
    13   snowy_mountains  white
    14   mushroom_fields  purple
    15   mushroom_field_shore  purple
    16   beach  yellow  yellow
    17   desert_hills  yellow
    18   wooded_hills
    19   taiga_hills
    20   mountain_edge  gray
    21   jungle
    22   jungle_hills
    23   jungle_edge
    24   deep_ocean  blue
    25   stone_shore  gray
    26   snowy_beach  white
    27   birch_forest
    28   birch_forest_hills
    29   dark_forest
    30   snowy_taiga  white
    31   snowy_taiga_hills  white
    32   giant_tree_taiga
    33   giant_tree_taiga_hills
    34   wooded_mountains
    35   savanna
    36   savanna_plateau
    37   badlands  orange
    38   wooded_badlands_plateau  orange
    39   badlands_plateau  orange
    40   small_end_islands
    41   end_midlands
    42   end_highlands
    43   end_barrens
    44   warm_ocean  blue
    45   lukewarm_ocean  blue
    46   cold_ocean  blue
    47   deep_warm_ocean  blue
    48   deep_lukewarm_ocean  blue
    49   deep_cold_ocean  blue
    50   deep_frozen_ocean  blue
    127  the_void
    129  sunflower_plains
    130  desert_lakes  blue
    131  gravelly_mountains  gray
    132  flower_forest
    133  taiga_mountains
    134  swamp_hills
    140  ice_spikes  blue
    149  modified_jungle
    151  modified_jungle_edge
    155  tall_birch_forest
    156  tall_birch_hills
    157  dark_forest_hills
    158  snowy_taiga_mountains  white
    160  giant_spruce_taiga
    161  giant_spruce_taiga_hills
    162  modified_gravelly_mountains  gray
    163  shattered_savanna
    164  shattered_savanna_plateau
    165  eroded_badlands  orange
    166  modified_wooded_badlands_plateau  orange
    167  modified_badlands_plateau  orange
    168  bamboo_jungle
    169  bamboo_jungle_hills
    170  soul_sand_valley
    171  crimson_forest
    172  warped_forest
    173  basalt_deltas
    174  dripstone_caves
    175  lush_caves
"""

def _parse_biomes(biomes):
    for biome in biomes.split('\n'):
        biome = biome.strip()
        if not biome:
            continue
        biome = biome.split()
        biome_id = int(biome[0])
        biome_name = biome[1]
        biome_color = biome[2] if len(biome) > 2 else 'green'

        yield biome_id, biome_color

BIOMES = dict(_parse_biomes(BIOMES))
