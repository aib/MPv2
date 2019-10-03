#version 130

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

in vec3 position;
in vec4 color;

out vec4 vf_color;

void main() {
	gl_Position = u_projection * u_view * u_model * vec4(position, 1);
	vf_color = color;
}
