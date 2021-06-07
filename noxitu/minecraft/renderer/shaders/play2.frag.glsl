#version 330

in vec3 vertex_color;
in float vertex_lighting;
in vec2 texture_coordinates;
flat in int texture_idx;

out vec4 out_color;

uniform sampler2DArray texture_atlas;


void main(void)
{
    vec4 base_color;

    if (texture_idx == -1)
        base_color = vec4(vertex_color, 1.0);
    else
        base_color = texture(texture_atlas, vec3(texture_coordinates, texture_idx));

    out_color = vertex_lighting * base_color;
}
