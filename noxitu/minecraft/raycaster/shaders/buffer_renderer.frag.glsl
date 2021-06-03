#version 430
in vec2 coord;

layout(location = 0) out vec4 out_color;

layout(std430, binding=1) buffer y_buffer { float y[]; };

uniform int canvas_size[2];

void main() {
    int ix = int(coord.x);
    int iy = int(coord.y);

    int width = canvas_size[1];
    int height = canvas_size[0];

    if (ix >= 0 && ix < width && iy >= 0 && iy < height)
        out_color.x = float(y[iy*width+ix]) / 512;
}