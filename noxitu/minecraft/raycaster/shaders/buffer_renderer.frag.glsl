#version 430
in vec2 coord;

layout(location = 0) out vec4 out_color;

layout(std430, binding=1) buffer y_buffer { float y[]; };

uniform int canvas_size[2];

void main() {
    int ix = int(coord.x);
    int iy = int(coord.y);
    if (ix >= 0 && ix < canvas_size[0] && iy >= 0 && iy < canvas_size[1])
        out_color.x = float(y[iy*canvas_size[0]+ix]) / 512;
}