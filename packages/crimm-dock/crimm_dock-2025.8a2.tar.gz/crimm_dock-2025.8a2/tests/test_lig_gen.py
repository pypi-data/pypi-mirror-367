from crimm.Data.probes.probes import create_new_probe_set
from crimm.Docking.GridGenerator import ProbeGridGenerator
import numpy as np
import ctypes
from numpy.ctypeslib import ndpointer

GRID_SPACING = 1.0
probe_set = create_new_probe_set()
probe = probe_set['tertbutanol']
grid_gen_probe = ProbeGridGenerator(grid_spacing=GRID_SPACING)
grid_gen_probe.load_entity(probe)

# Define the argument dtype and return types for the C functions
nd_float_ptr_type = ndpointer(ctypes.c_float, flags="C_CONTIGUOUS")
# Load the shared library
lib = ctypes.cdll.LoadLibrary('/home/truman/crimm/src/probe_grid_gen_simple.so')

class Vector3d(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float),
                ('y', ctypes.c_float),
                ('z', ctypes.c_float)]

class Dim3d(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int),
                ('y', ctypes.c_int),
                ('z', ctypes.c_int)]

class Grid(ctypes.Structure):
    _fields_ = [('dim', Dim3d),
                ('N_grid_points', ctypes.c_int),
                ('origin', Vector3d),
                ('spacing', ctypes.c_float),
                ('coords', ctypes.POINTER(Vector3d)),
                ('lig_coords', ctypes.POINTER(ctypes.c_float)),
                ('elec_grid', ctypes.POINTER(ctypes.c_float)),
                ('vdw_grid_attr', ctypes.POINTER(ctypes.c_float)),
                ('vdw_grid_rep', ctypes.POINTER(ctypes.c_float))]



rotate_gen_grids = lib.rotate_gen_lig_grids_eps_rmin
rotate_gen_grids.restype = ctypes.POINTER(Grid)
rotate_gen_grids.argtypes = [
    ctypes.c_float, # grid_spacing
    nd_float_ptr_type, # charges
    nd_float_ptr_type, # epsilons
    nd_float_ptr_type, # vdw_rs
    nd_float_ptr_type, # coords
    ctypes.c_int, # N_coords
    nd_float_ptr_type, # quats
    ctypes.c_int # N_quats
]

gen_lig_grid = lib.gen_lig_grid
gen_lig_grid.restype = Grid
gen_lig_grid.argtypes = [
    ctypes.c_float, # grid_spacing
    nd_float_ptr_type, # charges
    nd_float_ptr_type, # vdw_attr_factors
    nd_float_ptr_type, # vdw_rep_factors
    nd_float_ptr_type, # coords
    ctypes.c_int, # N_coords
]

dealloc_grid = lib.dealloc_grid
dealloc_grid.restype = None
dealloc_grid.argtypes = [Grid]


charges = np.ascontiguousarray(grid_gen_probe._charges, dtype=np.float32)
epsilons = np.ascontiguousarray(grid_gen_probe._epsilons, dtype=np.float32)
vdw_rs = np.ascontiguousarray(grid_gen_probe._vdw_rs, dtype=np.float32)
quats = np.ascontiguousarray(np.load('/home/truman/crimm/notebooks/qua2.npy'), dtype=np.float32)
coords = np.ascontiguousarray(grid_gen_probe.coords, dtype=np.float32)
N_coord = coords.shape[0]
N_quat = quats.shape[0]

# r_min_3 = vdw_rs**3
# epsilon_sqrt = np.sqrt(epsilons)
# vdw_attr_factors = epsilon_sqrt * r_min_3
# vdw_rep_factors = epsilon_sqrt * r_min_3**2

# vdw_attr_factors = np.ascontiguousarray(vdw_attr_factors, dtype=np.float32)
# vdw_rep_factors = np.ascontiguousarray(vdw_rep_factors, dtype=np.float32)

print("Num coords:", N_coord)
print("Num quats:", N_quat)

# Call the function
grids = rotate_gen_grids(
    GRID_SPACING, charges, epsilons, vdw_rs,
    coords, N_coord, quats, N_quat
)
grids = [grids[i] for i in range(N_quat)]
# grids = ctypes.cast(grids, ctypes.POINTER(Grid))
# grids = grids.contents
for grid in grids:
    dealloc_grid(grid)
