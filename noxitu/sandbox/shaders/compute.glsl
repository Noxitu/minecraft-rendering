#version 430
layout(local_size_x=32, local_size_y=32) in;

layout(std430, binding=0) buffer x_buffer { float xs[]; };
layout(std430, binding=1) buffer y_buffer { float ys[]; };

const uint size_x = 128;
const uint size_y = 16384;
const uint n = 512;

void main() {
    uint x = gl_GlobalInvocationID.x;
    uint y = gl_GlobalInvocationID.y;
    uint index = size_y*y + x;

    if (index >= size_y*size_y)
        return;

    float result = 0;

    for (uint i = 0; i < n; ++i)
    {
        result += xs[(index + i)%(size_x*size_x)];
    }

    ys[index] += result;
} 