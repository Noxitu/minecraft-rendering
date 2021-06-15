#version 330 core

in vec2 in_coordinates;

out vec2 texture_coordinates;

void main(void)
{
    vec2 rescaled_coordinates = in_coordinates * 2 - 1;
    gl_Position = vec4(rescaled_coordinates.x, -rescaled_coordinates.y, 0, 1);
    texture_coordinates = in_coordinates;
}
