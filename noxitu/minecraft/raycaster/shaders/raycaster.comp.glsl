#version 430
layout(local_size_x=1536) in;

struct Ray
{
    double x, y, z;
    double rx, ry, rz;
};

layout(std430, binding=0) buffer rays_buffer { Ray rays[]; };
layout(std430, binding=2) buffer mask_buffer { unsigned char mask[]; };
layout(std430, binding=3) buffer ray_depths_buffer { double ray_depths[]; };

uniform int world_shape[3];
uniform int offset;
uniform int count;

bool in_range(int value, int size)
{
    return (value >= 0) && (value < size);
}

bool is_inside(int x, int y, int z)
{
    return in_range(y, world_shape[0]) && in_range(z, world_shape[1]) && in_range(x, world_shape[2]);
}

int world_index(int x, int y, int z)
{
    return x + z * world_shape[2] + y * world_shape[2] * world_shape[1];
}

const float infinity = 1.0 / 0.0;

double next_depth(int c, double c0, double rc_inv)
{
    if (rc_inv > 0)
        return (c-c0+1)*rc_inv;

    if (rc_inv < 0)
        return (c-c0)*rc_inv;

    return 1e30;
}

void advance(inout int x, inout int y, inout int z,
             const double x0, const double y0, const double z0,
             const double rx_inv, const double ry_inv, const double rz_inv,
             out double depth, out int normal_idx)
{
    const double dx = next_depth(x, x0, rx_inv);
    const double dy = next_depth(y, y0, ry_inv);
    const double dz = next_depth(z, z0, rz_inv);

    if (dx < dy && dx < dz)
    {
        depth = dx;
        x += (rx_inv > 0 ? 1 : -1);
        normal_idx = (rx_inv > 0 ? 1 : 2);
    }
    else if (dy < dz)
    {
        depth = dy;
        y += (ry_inv > 0 ? 1 : -1);
        normal_idx = (ry_inv > 0 ? 3 : 4);
    }
    else
    {
        depth = dz;
        z += (rz_inv > 0 ? 1 : -1);
        normal_idx = (rz_inv > 0 ? 5 : 6);
    }
}

void main() {
    const uint width = gl_NumWorkGroups.x * gl_WorkGroupSize.x;
    const uint height = gl_NumWorkGroups.y * gl_WorkGroupSize.y;
    const uint index = offset + height * width * gl_GlobalInvocationID.z + width * gl_GlobalInvocationID.y + gl_GlobalInvocationID.x;

    if (index >= count)
        return;

    const Ray ray = rays[index];

    int x = int(ray.x);
    int y = int(ray.y);
    int z = int(ray.z);

    const double rx_inv = 1/ray.rx;
    const double ry_inv = 1/ray.ry;
    const double rz_inv = 1/ray.rz;

    ray_depths[index] = infinity;

    for (int iter = 0; iter < 64*128; ++iter)
    {
        double depth;
        int normal_idx;

        advance(x, y, z, ray.x, ray.y, ray.z, rx_inv, ry_inv, rz_inv, depth, normal_idx);

        const bool inside = is_inside(x, y, z);

        if (inside)
        {
            const int w_index = world_index(x, y, z);

            if (mask[w_index] != 0u)
            {
                ray_depths[index] = depth;
                break;
            }
        }

    }

    // for (int y = 256; y >= 0; --y)
    // {
    //     bool inside = is_inside(x, y, z);
    //     int w_index = world_index(x, y, z);

    //     if (inside && mask[w_index] != 0u)
    //     {
    //         break;
    //     }
    // }
}