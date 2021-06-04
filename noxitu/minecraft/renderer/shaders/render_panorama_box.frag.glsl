#version 330

in vec2 frag_coord;

out vec4 out_color;

uniform sampler2D panorama_texture;
uniform mat3 ray_matrix;

const float PI = 3.1415926535897932384626433832795;

float to_yaw(vec3 pnt)
{
    float yaw = atan(pnt.z, pnt.x) / PI;

    return yaw;
}

float to_coord2(float y, float x)
{
    return y/x;
    float ret = atan(y, x) / PI;
    return ret;
}

vec2 project_to_panorama(vec3 point_in_world)
{
    float horizontal = length(point_in_world.xz);
    
    return vec2(
        to_yaw(point_in_world) * 0.5 + 0.5,
        to_coord2(point_in_world.y, horizontal) * 0.5 + 0.5
    );
}

void main(void)
{
    //out_color = texture(panorama_texture, frag_coord);

    vec3 ray = ray_matrix * vec3(frag_coord, 1);
    ray /= length(ray);

    vec2 tex_coord = project_to_panorama(ray);

    out_color = texture(panorama_texture, tex_coord);
}
