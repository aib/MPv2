import numpy as np

def read_obj(f):
	vs  = []
	vts = []
	vns = []
	fvs  = []
	fvts = []
	fvns = []

	while True:
		line = f.readline()
		if len(line) == 0: break
		line = line.strip()
		if len(line) == 0: continue

		ls = line.split()

		if ls[0] == 'v':
			vs .append(list(map(float, ls[1:])))
		elif ls[0] == 'vt':
			vts.append(list(map(float, ls[1:])))
		elif ls[0] == 'vn':
			vns.append(list(map(float, ls[1:])))
		elif ls[0] == 'f':
			fvs.append(list(map(lambda fd: int(fd.split('/')[0])-1, ls[1:])))
			try:
				fvts.append(list(map(lambda fd: int(fd.split('/')[1])-1, ls[1:])))
			except ValueError: pass
			fvns.append(list(map(lambda fd: int(fd.split('/')[2])-1, ls[1:])))

	return (vs, vts, vns, fvs, fvts, fvns)

def read_obj_np(f):
	vs, vts, vns, fvs, fvts, fvns = read_obj(f)

	v = np.array(vs,  dtype=np.float32)[np.asarray(fvs,  'i')]
	t = np.array(vts, dtype=np.float32)[np.asarray(fvts, 'i')]
	n = np.array(vns, dtype=np.float32)[np.asarray(fvns, 'i')]

	return v, t, n
