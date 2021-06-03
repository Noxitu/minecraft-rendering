#version 430
layout(local_size_x=1) in;

layout(std430, binding=0) buffer x_buffer { float x[]; };
layout(std430, binding=1) buffer y_buffer { float y[]; };

void main() {
    uint width = gl_NumWorkGroups.x * gl_WorkGroupSize.x;
    uint index = width*gl_GlobalInvocationID.y + gl_GlobalInvocationID.x;
    y[index] = x[index];
}