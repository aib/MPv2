import unittest

import numpy as np

import mp

def assert_close(v, t):
	assert abs(t-v) < .000001, "%s is not close enough to %s (delta %s)" % (v, t, abs(t-v))

class TestIntersectPlaneSphere(unittest.TestCase):
	def test_intersect_plane_sphere(self):
		p0 = mp.array([-.866, 0, -.5])
		p1 = mp.array([+.866, 0, -.5])
		p2 = mp.array([    0, 0,   1])

		t, p = mp.intersect_plane_sphere([p0, p1, p2], mp.array([0, .4, 0]), mp.array([0, -.1, 0]))
		assert_close(t, 4)
		t, p = mp.intersect_plane_sphere([p0, p1, p2], mp.array([0, .4, 0]), mp.array([0, .1, 0]))
		assert_close(t, -4)

		t, p = mp.intersect_plane_sphere([p0, p1, p2], mp.array([-1, -1, -1]), mp.array([.1, .1, .1]))
		assert_close(t, 10)
		t, p = mp.intersect_plane_sphere([p0, p1, p2], mp.array([-1, -1, -1]), mp.array([-.1, -.1, -.1]))
		assert_close(t, -10)

		t, p = mp.intersect_plane_sphere([p0, p1, p2], mp.array([0, .4, 0]), mp.array([1, 0, 0]))
		self.assertEqual(t, np.inf)
		t, p = mp.intersect_plane_sphere([p0, p1, p2], mp.array([0, -.4, 0]), mp.array([1, 0, 0]))
		self.assertEqual(t, -np.inf)

		t, p = mp.intersect_plane_sphere([p0, p1, p2], mp.array([0, .4, 0]), mp.array([0, -.1, 0]), .1)
		assert_close(t, 3)
		t, p = mp.intersect_plane_sphere([p0, p1, p2], mp.array([0, .4, 0]), mp.array([0, -.1, 0]), .2)
		assert_close(t, 2)
		t, p = mp.intersect_plane_sphere([p0, p1, p2], mp.array([0, .4, 0]), mp.array([0, -.1, 0]), .5)
		assert_close(t, -1)

class TestTriangleContains(unittest.TestCase):
	def test_triangle_contains(self):
		tri = mp.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
		self.assertTrue(mp.triangle_contains_point(tri, mp.array([.1, .1, 0])))

		self.assertFalse(mp.triangle_contains_point(tri, mp.array([1.5, 1.5, 0])))
		self.assertFalse(mp.triangle_contains_point(tri, mp.array([.4, -9, 0])))
		self.assertFalse(mp.triangle_contains_point(tri, mp.array([-5, .2, 0])))
		self.assertFalse(mp.triangle_contains_point(tri, mp.array([-1, -1, 0])))
		self.assertFalse(mp.triangle_contains_point(tri, mp.array([-.1, 9, 0])))
		self.assertFalse(mp.triangle_contains_point(tri, mp.array([5, -.8, 0])))
