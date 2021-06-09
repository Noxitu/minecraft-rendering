#version 430
layout(local_size_x=48, local_size_y=32) in;
// layout(local_size_x=1024) in;

struct Ray
{
    float x, y, z;
    float rx, ry, rz;
};

struct State
{
    int x, y, z;
    int status;
    int block_id;
};

layout(std430, binding=0) buffer rays_buffer { Ray rays[]; };
layout(std430, binding=1) buffer state_buffer { State state[]; };
layout(std430, binding=2) buffer depth_buffer { float ray_depths[]; };
layout(std430, binding=3) buffer world_buffer { uint world[]; };
layout(std430, binding=4) buffer block_mask_buffer { uint block_mask[]; };

uniform uint n_rays;
uniform uint ray_offset;
uniform int world_shape[3];

bool in_range(int value, int size)
{
    return (value >= 0) && (value < size);
}

bool is_inside(int x, int y, int z)
{
    return in_range(y, world_shape[0]) && in_range(z, world_shape[1]) && in_range(x, world_shape[2]);
}

uint read_world(int x, int y, int z)
{
    const int index = y * world_shape[2] * world_shape[1] + z * world_shape[2] + x;
    const int shift = (x%2) * 16;
    return (world[index/2] >> shift) & 0xffff;
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

const uint work_group_size = gl_WorkGroupSize.x * gl_WorkGroupSize.y * gl_WorkGroupSize.z;

void main() {
    // const uint index = ray_offset + 1024 * gl_WorkGroupID.x + 32 * gl_LocalInvocationID.y + gl_LocalInvocationID.x;


    const uint work_group_index = gl_WorkGroupID.z * gl_NumWorkGroups.x * gl_NumWorkGroups.y +
                                  gl_WorkGroupID.y * gl_NumWorkGroups.x + 
                                  gl_WorkGroupID.x;

    const uint index = ray_offset + work_group_index * work_group_size + gl_LocalInvocationIndex;

    if (index >= n_rays)
        return;

    int status = state[index].status;

    if (state[index].status != 0)
        return;

    const Ray ray = rays[index];

    const double rx_inv = 1/ray.rx;
    const double ry_inv = 1/ray.ry;
    const double rz_inv = 1/ray.rz;

    int x = state[index].x;
    int y = state[index].y;
    int z = state[index].z;

    if (ray.rx > 0 && x >= world_shape[2]) return;
    if (ray.ry > 0 && y >= world_shape[0]) return;
    if (ray.rz > 0 && z >= world_shape[1]) return;

    if (ray.rx < 0 && x < 0) return;
    if (ray.ry < 0 && y < 0) return;
    if (ray.rz < 0 && z < 0) return;

    uint final_id = -1;
    double final_depth = -1;

    for (int iter = 0; iter < 500; ++iter)
    {
        double depth;
        int normal_idx;

        advance(x, y, z, ray.x, ray.y, ray.z, rx_inv, ry_inv, rz_inv, depth, normal_idx);

        const bool inside = is_inside(x, y, z);

        if (inside)
        {
            const uint block_id = read_world(x, y, z);

            if (block_mask[block_id] != 0)
            {
                final_id = block_id;
                status = 1;
                final_depth = depth;
                break;
            }
        }
    }

    state[index].x = x;
    state[index].y = y;
    state[index].z = z;
    state[index].status = status;
    state[index].block_id = int(final_id);

    ray_depths[index] = float(final_depth);
} 