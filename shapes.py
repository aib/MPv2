import shape

def _autoloading_shape(filename):
	def _shape_constructor(scene):
		s = shape.Shape(scene)
		s.load_file(filename)
		return s
	return _shape_constructor

Hexahedron = _autoloading_shape('obj/hexahedron.obj')
