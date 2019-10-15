import shape

def _autoloading_shape(filename):
	def _shape_constructor(scene):
		s = shape.Shape(scene, 5)
		s.load_file(filename)
		return s
	return _shape_constructor

Tetrahedron = _autoloading_shape('obj/tetrahedron.obj')
Hexahedron = _autoloading_shape('obj/hexahedron.obj')
Dodecahedron = _autoloading_shape('obj/dodecahedron.obj')
Icosahedron = _autoloading_shape('obj/icosahedron.obj')
