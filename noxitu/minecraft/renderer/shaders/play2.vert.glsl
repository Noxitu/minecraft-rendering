#version 330 core

layout(location=0) in vec3 in_position;
layout(location=1) in uint in_direction;
layout(location=2) in vec3 in_color;
layout(location=3) in int in_texture_idx;

out uint block_direction;
out vec3 block_color;
out int block_texture_idx;

void main(void)
{
    gl_Position = vec4(in_position, 1);
    block_direction = in_direction;
    block_color = in_color;
    block_texture_idx = in_texture_idx;
}
