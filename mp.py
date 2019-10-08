import numpy as np

DTYPE = np.float32

def array(v):
	return np.array(v, dtype=DTYPE)

def asarray(v):
	return np.asarray(v, dtype=DTYPE)

def perspectiveM(fovy, aspect, zNear, zFar):
	f = 1 / np.tan(fovy / 2)
	M = array([[f/aspect, 0,                    0,                 0],
	           [    0,    f,                    0,                 0],
	           [    0,    0,   (zFar + zNear)   / (zNear - zFar), -1],
	           [    0,    0, (2 * zFar * zNear) / (zNear - zFar),  0]])
	return M
