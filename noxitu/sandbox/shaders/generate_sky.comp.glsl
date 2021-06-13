#version 430
layout(local_size_x=32, local_size_y=32, local_size_z=1) in;

layout(rgba32f, binding = 0) uniform image2D output_image;

uniform sampler2D precomputed_p;

uniform mat3 camera_projection_inv;
uniform vec3 camera_position;
uniform vec3 sun_direction;


const double EARTH_RADIUS = 6371000;
const float NORMALIZED_ATMOSPHERE_TICKNESS = 7994;
const double ATMOSPHERE_RADIUS = 6371000 + 5 * NORMALIZED_ATMOSPHERE_TICKNESS;

//const vec3 WAVE_LENGTH = vec3(700e-9, 530e-9, 470e-9);
const vec3 WAVE_LENGTH = vec3(680e-9, 550e-9, 440e-9);
const vec3 WAVE_LENGTH_POW_4 = WAVE_LENGTH * WAVE_LENGTH * WAVE_LENGTH * WAVE_LENGTH;

const float K = 9.026027093131954e-32;

const vec3 RAYLEIGH_SCATTERING_COEFFICIENT = K / WAVE_LENGTH_POW_4;
const vec3 RAYLEIGH_ATTENUATION_COEFFICIENT = 4 * 3.14159 * RAYLEIGH_SCATTERING_COEFFICIENT;

const vec3 MIE_SCATTERING_COEFFICIENT = vec3(2.10e-5 / 4 / 3.14159);
// const vec3 MIE_SCATTERING_COEFFICIENT = vec3(1.5e-6 / 4 / 3.14159);
// const vec3 MIE_SCATTERING_COEFFICIENT = vec3(0);
const vec3 MIE_ATTENUATION_COEFFICIENT = 1.11 * 4 * 3.14159 * MIE_SCATTERING_COEFFICIENT;

const uint work_group_size = gl_WorkGroupSize.x * gl_WorkGroupSize.y * gl_WorkGroupSize.z;
const uint offset = 0;

// Some math:

double sum_vec(dvec3 vec)
{
    return vec.x + vec.y + vec.z;
}

vec3 normalized(vec3 vector)
{
    return vector / length(vector);
}

float exp_(double p)
{
    return exp(float(p));
}

vec3 exp3(dvec3 p)
{
    return vec3(exp_(p.x), exp_(p.y), exp_(p.z));
}

// More constants:

//const vec3 sun_direction = normalized(vec3(20, -0.25, 0));

// Some physics:

float computeElevation(dvec3 point)
{
    return float(length(point) - EARTH_RADIUS);
}

float computeAirDensity(float elevation)
{
    return exp(-elevation / 7994);
}

float computeAreosolsDensity(float elevation)
{
    return exp(-elevation / 1200);
}


float rayleighPhaseFunction(float cosine)
{
    return 3.0 / 4.0 * (1.0 + cosine*cosine);
}

float miePhaseFunction(float cosine)
{
    const float g = 0.66;
    const float g2 = g*g;
    return 3.0 * (1 - g2) / 2.0 / (2 + g2) * (1.0 + cosine*cosine) / pow(1 + g2 - 2*g*cosine, 1.5);
}

dvec2 intersectWithSphere(dvec3 ray_origin, dvec3 ray_direction, double radius)
{
    const double a = sum_vec(ray_direction * ray_direction);
    const double b = 2 * sum_vec(ray_origin * ray_direction);
    const double c = sum_vec(ray_origin * ray_origin) - radius * radius;

    const double delta = b * b - 4 * a * c;

    if (delta < 0)
        return dvec2(-1 / 0, -1 / 0);
    
    const double sqrt_delta = sqrt(delta);
    dvec2 ret = (-b + dvec2(-sqrt_delta, sqrt_delta)) / (2*a);

    if (ret.y < 0)
        return dvec2(-1 / 0, -1 / 0);

    if (ret.x < 0)
        ret.x = 0;

    return ret;
}


dvec3 computeAttenuationToSun(dvec3 position)
{
    const dvec2 earth_hit = intersectWithSphere(position, sun_direction, EARTH_RADIUS);

    if (earth_hit.x > 0)
        return dvec3(1e20);

    const dvec2 atmosphere_hit = intersectWithSphere(position, sun_direction, ATMOSPHERE_RADIUS);
    const double ray_length = atmosphere_hit.y;

    const int NUMBER_OF_STEPS = 10;
    const float step_size = float(ray_length) / (NUMBER_OF_STEPS-1);

    double air_result = 0;
    double areosols_result = 0;

    position += sun_direction * step_size / 2;

    for (int i = 0; i < NUMBER_OF_STEPS; ++i)
    {
        const float elevation = computeElevation(position);
        const double air_density = computeAirDensity(elevation);
        const double areosols_density = computeAreosolsDensity(elevation);

        air_result += air_density * step_size;
        areosols_result += air_density * step_size;
        position += sun_direction * step_size;
    }

    return RAYLEIGH_ATTENUATION_COEFFICIENT * air_result + MIE_ATTENUATION_COEFFICIENT * areosols_result;
}

// double computeAttenuationToSun2(dvec3 position)
// {
//     const double len = length(position);
//     const double elevation = len - EARTH_RADIUS;
//     const double cosine = dot(position / len, sun_direction);

//     const vec2 p_coords = vec2(elevation / 10 / NORMALIZED_ATMOSPHERE_TICKNESS, (cosine+1) / 2);

//     return texture(precomputed_p, p_coords).x;
// }

dvec3 computeLightFromDirection(dvec3 ray_position, vec3 ray_direction, double ray_length)
{
    const int NUMBER_OF_STEPS = 20;
    const float step_size = float(ray_length) / (NUMBER_OF_STEPS-1);

    const float ray_cosine = dot(ray_direction, sun_direction);
    const float rayleigh_phase_function = rayleighPhaseFunction(ray_cosine);
    const float mie_phase_function = miePhaseFunction(ray_cosine);

    dvec3 result = dvec3(0, 0, 0);
    dvec3 attenuation_to_origin = dvec3(0, 0, 0);

    ray_position += ray_direction * step_size / 2;

    for (int i = 0; i < NUMBER_OF_STEPS; ++i)
    {

        const dvec3 attenuation_to_sun = computeAttenuationToSun(ray_position);

        const float elevation = computeElevation(ray_position);
        const double air_density = computeAirDensity(elevation);
        const double areosols_density = computeAreosolsDensity(elevation);

        result += RAYLEIGH_SCATTERING_COEFFICIENT * rayleigh_phase_function * air_density * exp3(-attenuation_to_origin-attenuation_to_sun) * step_size;
        result += MIE_SCATTERING_COEFFICIENT * mie_phase_function * areosols_density * exp3(-attenuation_to_origin-attenuation_to_sun) * step_size;

        attenuation_to_origin += RAYLEIGH_ATTENUATION_COEFFICIENT * air_density * step_size;
        attenuation_to_origin += MIE_ATTENUATION_COEFFICIENT * areosols_density * step_size;

        ray_position += ray_direction * step_size;
    }

    dvec3 light = result;

    if (ray_cosine > 0.9995)
        light += exp3(-attenuation_to_origin) * ray_length * 1e-6;

    return light;
}

void main() {
    const uint index = offset + gl_WorkGroupID.x * work_group_size + gl_LocalInvocationIndex;

    // const uint WIDTH = 400;
    // const uint HEIGHT = 300;

    const uint WIDTH = 800;
    const uint HEIGHT = 600;

    if (index > WIDTH*HEIGHT)
        return;

    const ivec2 imageCoords = ivec2(index%WIDTH, index/WIDTH);
    const vec2 inputCoords = vec2(imageCoords) / vec2(WIDTH, HEIGHT) * 2 - 1;
    const vec3 projectiveInputCoords = vec3(inputCoords, 1);
    vec3 ray = camera_projection_inv * projectiveInputCoords;
    ray /= length(ray);

    vec4 color = vec4(0, 0, 0, 0);

    const dvec2 earth_hit = intersectWithSphere(camera_position, ray, EARTH_RADIUS);
    const dvec2 atmosphere_hit = intersectWithSphere(camera_position, ray, ATMOSPHERE_RADIUS);

    if (atmosphere_hit.x >= 0 && (earth_hit.y < 0 || earth_hit.x > 0))
    {
        const double ray_length = (earth_hit.x > 0 ? earth_hit.x : atmosphere_hit.y) - atmosphere_hit.x;

        const dvec3 light = 20 * computeLightFromDirection(camera_position, ray, ray_length);
        color = vec4(sqrt(light), 0);
    }

    if (earth_hit.x > 0) 
        color = vec4(0.2, 0.6, 0.2, 1);

    // if (dot(ray, sun_direction) > 0.999)
    //     color = vec4(1, 1, 0, 1);

    imageStore(output_image, imageCoords, color);
} 