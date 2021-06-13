#version 330 core

in vec3 in_position;
out vec3 frag_3d_position;

uniform mat4 projectionview_matrix;

vec4 project_from_camera(vec3 point_in_world)
{
    return projectionview_matrix * vec4(point_in_world, 1.0);
}

vec4 to_opengl(vec4 pnt)
{
    //float depth = pnt.z / 5000 - 1;
    float depth = 29000 / 15000 - 1;
    return vec4(pnt.x, -pnt.y, depth * pnt.w, pnt.w);
}

void main(void)
{
    gl_Position = to_opengl(project_from_camera(in_position));
    frag_3d_position = in_position;
}
