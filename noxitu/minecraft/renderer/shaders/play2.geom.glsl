#version 330 core
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

in uint block_direction[];
in vec3 block_color[];
out vec3 vertex_color;

const float DIFFUSE_FACTOR = 0.4;
const float AMBIENT_FACTOR = 1.0 - DIFFUSE_FACTOR;

uniform mat4 projectionview_matrix;
uniform vec3 sun_direction;

vec4 project(vec3 point_in_world)
{
    return projectionview_matrix * vec4(point_in_world, 1.0);
}

vec4 to_opengl(vec4 pnt)
{
    float depth = pnt.z / 5000 - 1;
    return vec4(pnt.x, -pnt.y, depth * pnt.w, pnt.w);
}

void main() {
    int direction = int(block_direction[0]);
    int idx0 = (direction - 1) / 2;

    bool positive = (direction == 2 || direction == 4 || direction == 6);

    int idx_step = positive ? 1 : 2;
    int idx1 = (idx0+idx_step) % 3;
    int idx2 = (idx1+idx_step) % 3;

    vec3 p1 = vec3(direction == 2, direction == 4, direction == 6);

    vec3 p2 = p1;
    p2[idx1] += 1;

    vec3 p3 = p1;
    p3[idx2] += 1;

    vec3 p4 = p2;
    p4[idx2] += 1;

    vec3 normal = p1 - vec3(direction == 1, direction == 3, direction == 5);

    float diffuse_factor = dot(normal, sun_direction);
    diffuse_factor = (diffuse_factor > 0 ? diffuse_factor * 0.7 + 0.3 : diffuse_factor * 0.3 + 0.3);
    vertex_color = block_color[0] * (AMBIENT_FACTOR + diffuse_factor * DIFFUSE_FACTOR);

    vec3 block_position = gl_in[0].gl_Position.xyz;

    gl_Position = to_opengl(project(block_position + p1));
    EmitVertex();

    gl_Position = to_opengl(project(block_position + p2));
    EmitVertex();

    gl_Position = to_opengl(project(block_position + p3));
    EmitVertex();

    gl_Position = to_opengl(project(block_position + p4));
    EmitVertex();
    
    EndPrimitive();
}  