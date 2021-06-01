#version 330

in vec3 in_position;

out float v_depth;

uniform mat4 projectionview_matrix;
uniform vec2 depth_range = vec2(-1, 1);

void main(void)
{
    vec4 projected = projectionview_matrix * vec4(in_position, 1.0);

    float normalized_depth = (projected.z - depth_range.x) / (depth_range.y - depth_range.x);
    gl_Position = vec4(projected.x, -projected.y, (2*normalized_depth-1) * projected.w, projected.w);

    v_depth = projected.z;
}
