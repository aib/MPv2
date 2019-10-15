import shape

def _autoloading_shape(filename):
	def _shape_constructor(scene):
		s = shape.Shape(scene, 3)
		s.load_file(filename)
		return s
	return _shape_constructor

Hexahedron = _autoloading_shape('obj/hexahedron.obj')
Icosahedron = _autoloading_shape('obj/icosahedron.obj')
