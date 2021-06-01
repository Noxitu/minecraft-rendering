#version 330

in vec3 v_color;
in float v_depth;
in vec2 v_shadow_texcoord;

out vec4 out_color;

uniform sampler2D shadow_texture;

void main(void)
{
    out_color = vec4(v_color, 1.0);

    float shadow_depth = texture(shadow_texture, v_shadow_texcoord).x;

    // out_color = vec4(v_color, 1.0)*0.001 + vec4(shadow_depth+90, shadow_depth+90, shadow_depth+90, 255) / 30;
    // out_color = vec4(v_color, 1.0)*0.001 + vec4(v_depth+90, 0, 0, 255) / 30;

    float behind_shadow_distance = v_depth - shadow_depth;

    if (behind_shadow_distance > 0)
        out_color *= max(0.7, 1-behind_shadow_distance);

    // out_color = vec4(v_color, 1.0)*0.001;

    // if (behind_shadow_distance > 0)    
    //     out_color += vec4(1-behind_shadow_distance/30, 1, 1-behind_shadow_distance/30, 255);
    // else
    //     out_color += vec4(1, 1+behind_shadow_distance/30, 1+behind_shadow_distance/30, 255);
}
