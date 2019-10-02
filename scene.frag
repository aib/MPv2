#version 130

uniform float u_time;

out vec4 fragColor;

void main() {
	fragColor = vec4(abs(sin(u_time)), 1, 0, 1);
}
