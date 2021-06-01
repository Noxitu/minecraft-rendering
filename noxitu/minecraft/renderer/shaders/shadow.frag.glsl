#version 330

in float v_depth;
out highp float out_depth;

void main(void)
{
    out_depth = v_depth;
}
