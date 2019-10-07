import numpy as np

def get_intersection_time(p0, p1, p2, bpos, bvel, brad=0):
	tn = get_triangle_normal(p0, p1, p2)
	t_to_b = bpos - p0
	pproj = project(tn, t_to_b)
	vproj = project(tn, bvel)
	if vproj == 0: return None
	return (pproj - brad) / -vproj

def get_triangle_normal(p0, p1, p2):
	return normalized(np.cross(p2 - p0, p1 - p0))

def angle_between(v0, v1):
	return np.arccos(np.dot(v0, v1) / (np.linalg.norm(v0) * np.linalg.norm(v1)))

def project(target, source):
	return np.dot(source, normalized(target))

def reflect(normal, incident):
	return incident - (2 * np.dot(incident, normal) * normal)

def normalized(v):
	norm = np.linalg.norm(v)
	if norm == 0: return v
	else: return v / norm

def test():
	def assert_close(v, t): assert abs(t-v) < .000001, "%s is not close enough to %s (delta %s)" % (t, v, abs(t-v))
	arr = lambda v: np.array(v, dtype=np.float32)
	p0 = arr([-.866, 0, -.5])
	p1 = arr([+.866, 0, -.5])
	p2 = arr([    0, 0,   1])

	t = get_intersection_time(p0, p1, p2, arr([0, .4, 0]), arr([0, -.1, 0]))
	assert_close(t, 4)
	t = get_intersection_time(p0, p1, p2, arr([0, .4, 0]), arr([0, .1, 0]))
	assert_close(t, -4)

	t = get_intersection_time(p0, p1, p2, arr([-1, -1, -1]), arr([.1, .1, .1]))
	assert_close(t, 10)
	t = get_intersection_time(p0, p1, p2, arr([-1, -1, -1]), arr([-.1, -.1, -.1]))
	assert_close(t, -10)

	t = get_intersection_time(p0, p1, p2, arr([0, .4, 0]), arr([1, 0, 0]))
	assert t is None

	t = get_intersection_time(p0, p1, p2, arr([0, .4, 0]), arr([0, -.1, 0]), .1)
	assert_close(t, 3)
	t = get_intersection_time(p0, p1, p2, arr([0, .4, 0]), arr([0, -.1, 0]), .2)
	assert_close(t, 2)
	t = get_intersection_time(p0, p1, p2, arr([0, .4, 0]), arr([0, -.1, 0]), .5)
	assert t < 0 or t is None
