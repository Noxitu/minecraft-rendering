#version 430

layout(location = 0) in vec4 in_vertex;
out vec2 coord;

uniform int canvas_size[2];

void main() {
    gl_Position = in_vertex;
    coord.x = canvas_size[1] * (in_vertex.x+1) / 2;
    coord.y = canvas_size[0] * (-in_vertex.y+1) / 2;
}