#version 330 core

#define PROJECTION_MODE_CAMERA 0
#define PROJECTION_MODE_PANORAMA 1

#define PROJECTION_MODE PROJECTION_MODE_CAMERA

#if PROJECTION_MODE == PROJECTION_MODE_CAMERA
    #define PROJECTION_FUNC project_from_camera
    #define MAX_VERTICES 4
#endif

#if PROJECTION_MODE == PROJECTION_MODE_PANORAMA
    #define PROJECTION_FUNC project_to_panorama
    #define MAX_VERTICES 8
#endif

layout (points) in;
layout (triangle_strip, max_vertices = MAX_VERTICES) out;

in uint block_direction[];
in vec3 block_color[];
out vec3 vertex_color;

uniform mat4 projectionview_matrix;
uniform vec3 sun_direction;
uniform vec3 camera_position;

const float DIFFUSE_FACTOR = 0.4;
const float AMBIENT_FACTOR = 1.0 - DIFFUSE_FACTOR;

const float PI = 3.1415926535897932384626433832795;

vec4 project_from_camera(vec3 point_in_world, float _unused)
{
    return projectionview_matrix * vec4(point_in_world, 1.0);
}

float to_yaw(vec3 pnt)
{
    return 2 * atan(pnt.z, pnt.x) / PI + 2;
}

float to_yaw(vec3 pnt, float primary_yaw)
{
    float yaw = to_yaw(pnt);

    if (yaw > primary_yaw+2)
        return yaw-4;

    if (yaw < primary_yaw-2)
        return yaw+4;

    return yaw;
}

float to_coord2(float y, float x)
{
    return 0.5 * y/x;
}

vec4 project_to_panorama(vec3 point_in_world, float primary_yaw)
{
    point_in_world -= camera_position;
    float horizontal = length(point_in_world.xz);
    
    return vec4(
        to_yaw(point_in_world, primary_yaw) / 2 - 1,
        -to_coord2(point_in_world.y, horizontal),
        horizontal-1,
        1.0
    );
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

    float primary_yaw = to_yaw(gl_in[0].gl_Position.xyz - camera_position);

    gl_Position = to_opengl(PROJECTION_FUNC(block_position + p1, primary_yaw));
    EmitVertex();

    gl_Position = to_opengl(PROJECTION_FUNC(block_position + p2, primary_yaw));
    EmitVertex();

    gl_Position = to_opengl(PROJECTION_FUNC(block_position + p3, primary_yaw));
    EmitVertex();

    gl_Position = to_opengl(PROJECTION_FUNC(block_position + p4, primary_yaw));
    EmitVertex();
    
    EndPrimitive();

#if PROJECTION_MODE == PROJECTION_MODE_PANORAMA
    bool next_quad = false;

    const float BORDER_THRESHOLD = 0.01;

    if (primary_yaw < BORDER_THRESHOLD)
    {
        primary_yaw += 4;
        next_quad = true;
    }
    else if (primary_yaw > 4 - BORDER_THRESHOLD)
    {
        primary_yaw -= 4;
        next_quad = true;
    }

    if (next_quad)
    {
        gl_Position = to_opengl(PROJECTION_FUNC(block_position + p1, primary_yaw));
        EmitVertex();

        gl_Position = to_opengl(PROJECTION_FUNC(block_position + p2, primary_yaw));
        EmitVertex();

        gl_Position = to_opengl(PROJECTION_FUNC(block_position + p3, primary_yaw));
        EmitVertex();

        gl_Position = to_opengl(PROJECTION_FUNC(block_position + p4, primary_yaw));
        EmitVertex();
        
        EndPrimitive();
    }
#endif
}  