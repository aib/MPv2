import numpy as np

DTYPE = np.float32

def array(v):
	return np.array(v, dtype=DTYPE)

def asarray(v):
	return np.asarray(v, dtype=DTYPE)

def clamp(x, a, b):
	return max(a, min(b, x))

def norm(v):
	return np.linalg.norm(v)

def normalize(v):
	return v / norm(v)

def dot(v0, v1):
	return np.dot(v0, v1)

def cross(v0, v1):
	return np.cross(v0, v1)

def angle_between(v0, v1):
	return np.arccos(dot(v0, v1) / (norm(v0) * norm(v1)))

def project(target, source):
	return dot(source, normalize(target))

def triangle_normal(tri):
	return normalize(cross(tri[1] - tri[0], tri[2] - tri[0]))

def reflect(normal, incident):
	return incident - (2 * dot(incident, normal) * normal)

def intersect_plane_sphere(tri, spos, svel, srad=0):
	tn = triangle_normal(tri)
	behind = dot(tn, svel) > 0
	sclosest = spos - (-tn if behind else tn) * srad
	distproj = project(tn, sclosest - tri[0])

	if distproj == 0: # on plane
		return (0, sclosest)

	velproj = project(tn, svel)

	if velproj == 0: # moving parallel
		return (np.inf * -distproj, None)

	intersection_time = distproj / -velproj
	intersection_point = sclosest + svel * intersection_time

	return (intersection_time, intersection_point)

def triangle_contains_point(tri, p):
	tn = triangle_normal(tri)
	edgeperp0 = cross(tri[1] - tri[0], tn)
	edgeperp1 = cross(tri[2] - tri[1], tn)
	edgeperp2 = cross(tri[0] - tri[2], tn)
	edgeside0 = dot(p - tri[0], edgeperp0)
	edgeside1 = dot(p - tri[1], edgeperp1)
	edgeside2 = dot(p - tri[2], edgeperp2)
	return all([edgeside0 <= 0, edgeside1 <= 0, edgeside2 <= 0])

def identityM():
	return array([
		[1, 0, 0, 0],
		[0, 1, 0, 0],
		[0, 0, 1, 0],
		[0, 0, 0, 1]
	])

def translateM(v):
	v = asarray(v)
	return array([
		[1, 0, 0, v[0]],
		[0, 1, 0, v[1]],
		[0, 0, 1, v[2]],
		[0, 0, 0,   1 ]
	])

def scaleM(s):
	return array([
		[s, 0, 0, 0],
		[0, s, 0, 0],
		[0, 0, s, 0],
		[0, 0, 0, 1]
	])

# https://en.wikipedia.org/wiki/Euler%E2%80%93Rodrigues_formula
def rotateM(axis, theta):
	axis = asarray(axis)
	axis = axis / np.sqrt(dot(axis, axis))
	a = np.cos(theta / 2)
	b, c, d = -axis * np.sin(theta / 2)
	aa, bb, cc, dd = a * a, b * b, c * c, d * d
	bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
	return array([
		[aa + bb - cc - dd,   2 * (bc + ad),     2 * (bd - ac)  ],
		[  2 * (bc - ad),   aa + cc - bb - dd,   2 * (cd + ab)  ],
		[  2 * (bd + ac),     2 * (cd - ab),   aa + dd - bb - cc],
	])

def perspectiveM(fovy, aspect, zNear, zFar):
	f = 1 / np.tan(fovy / 2)
	M = array([
		[f/aspect, 0,                0,                                   0               ],
		[    0,    f,                0,                                   0               ],
		[    0,    0, (zFar + zNear) / (zNear - zFar), (2 * zFar * zNear) / (zNear - zFar)],
		[    0,    0,               -1,                                   0               ]
	])
	return M

def lookatM(eye, center, up):
	eye, center, up = asarray(eye), asarray(center), asarray(up)
	f = normalize(center - eye)
	s = normalize(cross(f, up))
	u = cross(s, f)
	M = array([
		[ s[0],  s[1],  s[2], 0],
		[ u[0],  u[1],  u[2], 0],
		[-f[0], -f[1], -f[2], 0],
		[  0,     0,     0,   1]
	])
	return M @ translateM(-eye)

def spherical_to_cartesian(p):
	return array([
		p[2] * np.sin(p[1]) * np.cos(p[0]),
		p[2] * np.cos(p[1]),
		p[2] * np.sin(p[1]) * np.sin(p[0]),
	])

def unproject(winpos, modelview, projection):
	ndc_near = array([2 * winpos[0] - 1, 2 * (1 - winpos[1]) - 1, -1, 1])
	ndc_far  = array([2 * winpos[0] - 1, 2 * (1 - winpos[1]) - 1, +1, 1])

	vp_inv = np.linalg.inv(projection @ modelview)

	unp_near = vp_inv @ ndc_near
	unp_far  = vp_inv @ ndc_far
	unp_near /= unp_near[3]
	unp_far  /= unp_far[3]

	return (unp_near[0:3], unp_far[0:3])
