#version 330

in vec2 texture_coordinates;

out vec4 out_color;

uniform sampler2D image;


void main(void)
{
    out_color = texture(image, texture_coordinates);
}
