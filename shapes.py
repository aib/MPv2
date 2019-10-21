import params
import shape

def _autoloading_shape(filename, symmetries={}):
	def _shape_constructor(scene):
		s = shape.Shape(scene, params.SHAPE_SCALE)
		s.load_file(filename)
		for k, v in symmetries.items():
			s.symmetries[k] = v
		import pprint
#		pprint.pprint(s.symmetries)
		return s
	return _shape_constructor

Tetrahedron = _autoloading_shape('obj/tetrahedron.obj')
Hexahedron = _autoloading_shape('obj/hexahedron.obj')
Octohedron = _autoloading_shape('obj/octohedron.obj')
Dodecahedron = _autoloading_shape('obj/dodecahedron.obj')

_icosahedron_symmetries = {
	10: [(0, 16), (1, 17), (2, 18), (3, 19), (4, 15), (5, 14), (6, 10), (7, 11), (8, 12), (9, 13)]
}
Icosahedron = _autoloading_shape('obj/icosahedron.obj', _icosahedron_symmetries)

#print(Icosahedron.symmetries)
