import objreader
import triangle

class Shape:
	def __init__(self):
		self.triangles = []

	def load_file(self, filename):
		with open(filename, 'r') as f:
			vertices, texcoords, normals = objreader.read_obj_np(f)

		wires = self.get_wires(vertices, texcoords, normals)

		for i, vt in enumerate(vertices):
			tt, nt, wt = texcoords[i], normals[i], wires[i]
			tri = triangle.Triangle(vt, tt, wt)
			self.triangles.append(tri)

	def get_wires(self, vertices, texcoords, normals):
		wires = []
		for i, v in enumerate(vertices):
			wires.append(self.get_wire(i, v, texcoords[i], normals[i]))
		return wires

	def get_wire(self, i, v, t, n):
		return None
