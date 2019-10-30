import params
import shape

def _autoloading_shape(filename, name=None, symmetries={}):
	def _shape_constructor(scene):
		s = shape.Shape(scene, name, params.SHAPE_SCALE)
		s.load_file(filename)
		for k, v in symmetries.items():
			s.symmetries[k] = v
		return s
	return _shape_constructor

_hexahedron_symmetries = {
	3: [(0, 4), (1, 5), (2, 3)],
}
Hexahedron = _autoloading_shape('obj/hexahedron.obj', "Hexahedron", _hexahedron_symmetries)

_octohedron_symmetries = {
	4: [(0, 5), (1, 6), (2, 7), (3, 4)],
}
Octohedron = _autoloading_shape('obj/octohedron.obj', "Octohedron", _octohedron_symmetries)

_dodecahedron_symmetries = {
	6: [(0, 4), (1, 5), (2, 11), (3, 7), (6, 10), (8, 9)],
	4: [(0, 1, 2), (3, 10, 11), (4, 7, 9), (5, 6, 8)],
}
Dodecahedron = _autoloading_shape('obj/dodecahedron.obj', "Dodecahedron", _dodecahedron_symmetries)

_icosahedron_symmetries = {
	10: [(0, 16), (1, 17), (2, 18), (3, 19), (4, 15), (5, 14), (6, 10), (7, 11), (8, 12), (9, 13)],
	5: [(0, 7, 8, 19), (1, 9, 14, 15), (2, 10, 11, 16), (3, 12, 13, 17), (4, 5, 6, 18)],
}
Icosahedron = _autoloading_shape('obj/icosahedron.obj', "Icosahedron", _icosahedron_symmetries)
