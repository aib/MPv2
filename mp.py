import numpy as np

DTYPE = np.float32

def array(v):
	return np.array(v, dtype=DTYPE)

def asarray(v):
	return np.asarray(v, dtype=DTYPE)

def normalize(v):
	return v / np.linalg.norm(v)

def translateM(v):
	v = asarray(v)
	return array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [v[0], v[1], v[2], 1]])

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
	s = np.cross(f, normalize(up))
	u = np.cross(normalize(s), f)
	M = array([
		[s[0], u[0], -f[0], 0],
		[s[1], u[1], -f[1], 0],
		[s[2], u[2], -f[2], 0],
		[  0,    0,     0,  1]
	])
	return translateM(-eye) @ M
