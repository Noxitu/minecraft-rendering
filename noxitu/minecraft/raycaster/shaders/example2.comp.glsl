#version 430
layout(local_size_x=1) in;

layout(std430, binding=0) buffer x_buffer { float x[]; };
layout(std430, binding=1) buffer y_buffer { float y[]; };

void main() {
    uint index = 256*gl_GlobalInvocationID.y + gl_GlobalInvocationID.x;
    y[index] = x[index];
}