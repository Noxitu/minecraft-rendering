#version 430
layout(local_size_x=16, local_size_y=16, local_size_z=1) in;
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
    int normal_idx;
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

bool is_inside(const ivec3 p)
{
    return in_range(p.y, world_shape[0]) && in_range(p.z, world_shape[1]) && in_range(p.x, world_shape[2]);
}

uint read_world(const ivec3 p)
{
    const int index = p.y * world_shape[2] * world_shape[1] + p.z * world_shape[2] + p.x;
    const int shift = (p.x%2) * 16;
    return (world[index/2] >> shift) & 0xffff;
 }

const float infinity = 1.0 / 0.0;

struct AdvanceData
{
    dvec3 offset;
    dvec3 ray_inv;
    ivec3 direction;
    ivec3 normals;
};

AdvanceData compute_advance_data(const Ray ray)
{
    AdvanceData ret;

    const dvec3 p0 = dvec3(ray.x, ray.y, ray.z);
    dvec3 ray_inv = 1 / dvec3(ray.rx, ray.ry, ray.rz);

    // This might not be required, but would be necessary in case of negative 0 in ray direction.
    if (ray.rx == 0) ray_inv.x = infinity;
    if (ray.ry == 0) ray_inv.y = infinity;
    if (ray.ry == 0) ray_inv.y = infinity;

    const dvec3 is_positive = dvec3(greaterThan(ray_inv, dvec3(0, 0, 0)));
    ret.offset = p0 + is_positive;
    ret.ray_inv = ray_inv;

    ret.direction = ivec3(sign(ray_inv));
    ret.normals = ivec3(ret.direction-1) / -2 + ivec3(1, 3, 5);

    return ret;
}

void advance(inout ivec3 p, const AdvanceData data,
             out double depth, out int normal_idx)
{
    const dvec3 depths = (p - data.offset) * data.ray_inv;

    if (depths.x < depths.y && depths.x < depths.z)
    {
        p.x += data.direction.x;
        depth = depths.x;
        normal_idx = data.normals.x;
    }
    else if (depths.y < depths.z)
    {
        p.y += data.direction.y;
        depth = depths.y;
        normal_idx = data.normals.y;
    }
    else
    {
        p.z += data.direction.z;
        depth = depths.z;
        normal_idx = data.normals.z;
    }
}

const uint work_group_size = gl_WorkGroupSize.x * gl_WorkGroupSize.y * gl_WorkGroupSize.z;

void main() {
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

    ivec3 p = ivec3(state[index].x, state[index].y, state[index].z);

    if (ray.rx > 0 && p.x >= world_shape[2]) return;
    if (ray.ry > 0 && p.y >= world_shape[0]) return;
    if (ray.rz > 0 && p.z >= world_shape[1]) return;

    if (ray.rx < 0 && p.x < 0) return;
    if (ray.ry < 0 && p.y < 0) return;
    if (ray.rz < 0 && p.z < 0) return;

    const AdvanceData advance_data = compute_advance_data(ray);

    uint final_id = -1;
    double final_depth = -1;

    for (int iter = 0; iter < 500; ++iter)
    {
        double depth;
        int normal_idx;

        advance(p, advance_data, depth, normal_idx);

        const bool inside = is_inside(p);

        if (inside)
        {
            const uint block_id = read_world(p);

            if (block_mask[block_id] != 0)
            {
                final_id = block_id;
                status = 1;
                final_depth = depth;
                break;
            }
        }
    }

    state[index].x = p.x;
    state[index].y = p.y;
    state[index].z = p.z;
    state[index].status = status;
    state[index].block_id = int(final_id);

    ray_depths[index] = float(final_depth);
} 