#version 130

uniform float u_time;

in vec4 vf_color;

out vec4 fragColor;

void main() {
	fragColor = vf_color;
}
