
| Rendering | Raycasting |
| --- | --- |
| ![Rendering example][docs/rendering.png] | ![Raycasting example][docs/raycasting.png] |

## Rendering

Renders scene using Python bindings to modern OpenGL.
 [x] Uses geometry shader to render single points as block faces.
 [ ] Has separate water layer for blending with underwater blocks. (implemented in deprecated `opengl_renderer`)
 [ ] Computes and uses shadow map texture. (implemented in deprecated `opengl_renderer`)
 [ ] Renders shadow map texture in projection appopieate for current view.
 [ ] Renders far chunks as part of sky box to provide high fps with large view distance.

In current implementation using `4000x3000` chunks of freshly generated Hermitcraft Season 7 seed (`WLLBYUG`) has 4 frames per second. 

## Raycasting

Renders scene using custom raytracer. Vector manipulation is done in Python using Numpy, while the core raytracing is run on GPU using Microsoft AMP library.
 [x] Raytraces all target pixels to find first block.
 [x] Raytraces all pixels in direction of sun to find shadows.
 [x] Performs light refraction according to Snell's Law while rendering underwater objects.
 [x] Performs light reflection according to Schlick's approximation of Fresnel formula.

In current implementation huge limitation is size of buffer describing world, which needs to fit fully in GPU memory.

## Input files not on repository

##### Docker/VanillaServer/minecraft_server.1.16.5.jar`
Official Minecraft server release.

##### noxitu/minecraft/map/blocks.json
Generated from Minecraft using following command:
 
    java -cp minecraft_server.jar net.minecraft.data.Main --all

Read more: https://wiki.vg/Data_Generators

## Intermediate files not on repository

##### data/chunks_raw/*
Generated using `noxitu.minecraft.protocol.proxy_server` module.

Each of files has filename with format `{x}-{z}-{section_mask}.bin` and contain Minecraft "Chunk Format" data (see: https://wiki.vg/Chunk_Format).

This module opens a server on :25566, that connects to server running on :25565. It then intercepts all chunk messages and stores each of them in `data/chunks_raw/` directory. It also uses and stores `data/biomes.npz` to provide life visualization of recieved chunks (this process can be quite slow, especially while generating new chunks).

Currently target server must be running in offline mode, since encryption is not supported.

For scraping following setup could be used:
 - Set both server and client view distances to 32. This allows collecting `1024x1024` area without interaction.
 - Navigate world using `/tp` commands. To capture area of about `4000x3000` around `0, 0`:
   1. `/tp -2048 300 -1536` to move to starting position,
   2. `/tp ~1024 300 ~` to move to next block in same row,
   3. `/tp -2048 300 ~1024` to move to start of next row.

Seeing how server strugles to generate chunks at decent speed this step probably could be replaced to generate `data/chunks/*` in the future.

##### data/chunks/*
Generated using `noxitu.minecraft.map.chunk_data` module using `data/chunks_raw/*` as input.

Each of files has filename with format `{x}_{z}_chunk.bin` and contain a `uint16` numpy array with shape `(256, 16, 16)`. Each entry describes ID from global palette (the same as in `blocks.json`).

This directory together with a single viewport is used as input for `noxitu.minecraft.raycasting.main` (via `noxitu.minecraft.map.load`).

##### data/face_buffers/*
This will be removed soon.

Generated using `noxitu.minecraft.renderer.create_face_buffer` module using `data/chunks/*` as input (via `noxitu.minecraft.map.load`).

Contains a buffer ready for rendering using GL_QUADS. Internally this buffer has shape `(n, 4)` (4 vertices per face), and dtype `[('vertices', '3int16'), ('colors', '3uint8')]`.

This buffer is limited only to visible faces - faces of opaque blocks with transparent blocks in front.

A single buffer is used as input for `noxitu.minecraft.rendering.opengl_renderer` (deprecated).

##### data/block_buffers/*
Generated using `noxitu.minecraft.renderer.create_face_buffer` module using `data/chunks/*` as input (via `noxitu.minecraft.map.load`).

Contains a buffer ready for rendering using GL_POINTS, preferably with geometry shader converting each point into square face. Internally this buffer has shape `(n,)`, and dtype `[('position', '3int16'), ('direction', 'uint8'), ('color', '3uint8')]`.

This buffer is limited only to visible faces - faces of opaque blocks with transparent blocks in front.

Direction is enum with following meaning:
 1. West face (negative x)
 2. East face (positive x)
 3. Bottom face (negative y)
 4. Top face (positive y)
 5. North face (negative z)
 6. South face (positive z)

A single buffer is used as input for `noxitu.minecraft.rendering.main`.

##### data/viewports/*
Current viewport can be saved from `noxitu.minecraft.rendering.main` (or `noxitu.minecraft.rendering.opengl_renderer`) by pressing `4`.

Viewports are used as input for `noxitu.minecraft.raycasting.main`.
