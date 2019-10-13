import numpy as np

DTYPE = np.float32

def array(v):
	return np.array(v, dtype=DTYPE)

def asarray(v):
	return np.asarray(v, dtype=DTYPE)

def normalize(v):
	return v / np.linalg.norm(v)

def angle_between(v0, v1):
	return np.arccos(np.dot(v0, v1) / (np.linalg.norm(v0) * np.linalg.norm(v1)))

def project(target, source):
	return np.dot(source, normalize(target))

def triangle_normal(tri):
	return normalize(np.cross(tri[2] - tri[0], tri[1] - tri[0]))

def intersect_plane_sphere(tri, spos, svel, srad=0):
	tn = triangle_normal(tri)
	sclosest = spos - tn * srad
	distproj = project(tn, sclosest - tri[0])

	if distproj == 0: # on plane
		return (0, sclosest)

	velproj = project(tn, svel)

	if velproj == 0: # moving parallel
		return (np.inf * distproj, None)

	intersection_time = distproj / -velproj
	intersection_point = sclosest + svel * intersection_time

	return (intersection_time, intersection_point)

def identityM():
	return array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

def from3vecM(vx, vy, vz):
	return array([
		np.append(vx, 0),
		np.append(vy, 0),
		np.append(vz, 0),
		[0, 0, 0, 1]
	])

def translateM(v):
	v = asarray(v)
	return array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [v[0], v[1], v[2], 1]])

def scaleM(s):
	return array([[s, 0, 0, 0], [0, s, 0, 0], [0, 0, s, 0], [0, 0, 0, 1]])

def perspectiveM(fovy, aspect, zNear, zFar):
	f = 1 / np.tan(fovy / 2)
	M = array([[f/aspect, 0,                    0,                 0],
	           [    0,    f,                    0,                 0],
	           [    0,    0,   (zFar + zNear)   / (zNear - zFar), -1],
	           [    0,    0, (2 * zFar * zNear) / (zNear - zFar),  0]])
	return M

def lookatM(eye, center, up):
	eye, center, up = asarray(eye), asarray(center), asarray(up)
	f = normalize(center - eye)
	s = normalize(np.cross(f, up))
	u = np.cross(s, f)
	M = array([
		[s[0], u[0], -f[0], 0],
		[s[1], u[1], -f[1], 0],
		[s[2], u[2], -f[2], 0],
		[  0,    0,     0,  1]
	])
	return translateM(-eye) @ M

def spherical_to_cartesian(p):
	return array([
		p[2] * np.sin(p[1]) * np.cos(p[0]),
		p[2] * np.cos(p[1]),
		p[2] * np.sin(p[1]) * np.sin(p[0]),
	])
