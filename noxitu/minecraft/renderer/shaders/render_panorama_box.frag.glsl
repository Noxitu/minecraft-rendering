#version 330

in vec3 frag_3d_position;

out vec4 out_color;

uniform sampler2D panorama_texture;
uniform vec3 panorama_position;

const float PI = 3.1415926535897932384626433832795;

float to_yaw(vec3 pnt)
{
    return 2 * atan(pnt.z, pnt.x) / PI + 2;
}

float to_coord2(float y, float x)
{
    return 0.5 * y/x;
}

vec2 project_to_panorama(vec3 point_in_world)
{
    point_in_world -= panorama_position;
    float horizontal = length(point_in_world.xz);
    
    return vec2(
        to_yaw(point_in_world) / 4,
        to_coord2(point_in_world.y, horizontal) / 2 + 0.5
    );
}

void main(void)
{
    vec2 panorama_coord = project_to_panorama(frag_3d_position);
    out_color = texture(panorama_texture, panorama_coord);

    // Make "panoramabox" visible due to different bg color:
#define BOX_VISIBILITY_FACTOR 0.0

    out_color.xyz = (1-BOX_VISIBILITY_FACTOR) * out_color.xyz + BOX_VISIBILITY_FACTOR * vec3(1, 1, 1);
}
