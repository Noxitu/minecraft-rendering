#version 330

in vec3 in_position;
in vec3 in_color;

out vec3 v_color;
out float v_depth;
out vec2 v_shadow_texcoord;

uniform mat4 projectionview_matrix;
uniform vec2 depth_range = vec2(-1, 1);
uniform mat4 shadow_projectionview_matrix;

void main(void)
{
    vec4 projected = projectionview_matrix * vec4(in_position, 1.0);

    float normalized_depth = (projected.z - depth_range.x) / (depth_range.y - depth_range.x);
    gl_Position = vec4(projected.x, -projected.y, (2*normalized_depth-1) * projected.w, projected.w);

    v_color = in_color;

    vec4 projected_to_shadow = shadow_projectionview_matrix * vec4(in_position, 1.0);

    v_depth = projected_to_shadow.z;
    v_shadow_texcoord = 0.5 * vec2(projected_to_shadow.x, -projected_to_shadow.y) / projected_to_shadow.w + 0.5;
}
