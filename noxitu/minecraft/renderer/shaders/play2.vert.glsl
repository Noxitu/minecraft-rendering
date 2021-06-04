#version 330

layout(location=0) in vec3 in_position;
layout(location=1) in unsigned char in_direction;
layout(location=2) in vec3 in_color;

out unsigned char block_direction;
out vec3 block_color;

void main(void)
{
    gl_Position = vec4(in_position, 1);
    block_direction = in_direction;
    block_color = in_color;
}
