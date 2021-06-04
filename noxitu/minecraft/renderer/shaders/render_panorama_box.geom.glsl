#version 330 core

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

out vec2 frag_coord;

void main() {
    gl_Position = vec4(-1, 1, 0.99, 1);
    frag_coord = vec2(-1, -1);
    EmitVertex();

    gl_Position = vec4(-1, -1, 0.99, 1);
    frag_coord = vec2(-1, 1);
    EmitVertex();

    gl_Position = vec4(1, 1, 0.99, 1);
    frag_coord = vec2(1, -1);
    EmitVertex();

    gl_Position = vec4(1, -1, 0.99, 1);
    frag_coord = vec2(1, 1);
    EmitVertex();
    
    EndPrimitive();
}  