import shape

class Hexahedron(shape.Shape):
	def __init__(self, scene):
		super().__init__(scene)
		self.load_file('obj/hexahedron.obj')
