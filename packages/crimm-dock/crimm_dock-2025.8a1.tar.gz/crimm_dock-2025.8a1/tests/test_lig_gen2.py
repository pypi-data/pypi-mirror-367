from crimm.Data.probes.probes import create_new_probe_set
from crimm.Docking.GridGenerator import ProbeGridGenerator
import numpy as np
import ctypes
from numpy.ctypeslib import ndpointer
from scipy.spatial.distance import pdist

GRID_SPACING = 1.0
probe_set = create_new_probe_set()
probe = probe_set['tertbutanol']
grid_gen_probe = ProbeGridGenerator(grid_spacing=GRID_SPACING)
grid_gen_probe.load_entity(probe)

# Define the argument dtype and return types for the C functions
nd_float_ptr_type = ndpointer(ctypes.c_float, flags="C_CONTIGUOUS")
# Load the shared library
lib = ctypes.cdll.LoadLibrary('/home/truman/crimm/src/lig_gen_cube.so')

class Vector3d(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float),
                ('y', ctypes.c_float),
                ('z', ctypes.c_float)]

gen_lig_grid = lib.rotate_gen_lig_grids_eps_rmin
gen_lig_grid.restype = None
gen_lig_grid.argtypes = [
    ctypes.c_float, # grid_spacing
    nd_float_ptr_type, # charges
    nd_float_ptr_type, # epsilons
    nd_float_ptr_type, # vdw_rs
    nd_float_ptr_type, # coords
    ctypes.c_int, # N_coords
    nd_float_ptr_type, # quats
    ctypes.c_int, # N_quats
    ctypes.c_int, # cube_dim
    Vector3d, # min_corner
    nd_float_ptr_type, # rot_coords
    nd_float_ptr_type, # elec_grids
    nd_float_ptr_type, # vdw_grids_attr
    nd_float_ptr_type, # vdw_grids_rep
]

charges = np.ascontiguousarray(grid_gen_probe._charges, dtype=np.float32)
epsilons = np.ascontiguousarray(grid_gen_probe._epsilons, dtype=np.float32)
vdw_rs = np.ascontiguousarray(grid_gen_probe._vdw_rs, dtype=np.float32)
quats = np.ascontiguousarray(np.load('/home/truman/crimm/notebooks/qua2.npy'), dtype=np.float32)
coords = np.ascontiguousarray(grid_gen_probe.coords, dtype=np.float32)
N_coord = coords.shape[0]
N_quat = quats.shape[0]

cube_dim = np.ceil(pdist(grid_gen_probe.coords).max()/grid_gen_probe.spacing).astype(int)
min_coord = grid_gen_probe.coords.min(0)
min_coord = Vector3d(*min_coord)

rot_coords = np.zeros((N_quat, N_coord, 3), dtype=np.float32)
elec_grids = np.zeros((N_quat, cube_dim**3), dtype=np.float32)
vdw_grids_attr = np.zeros((N_quat, cube_dim**3), dtype=np.float32)
vdw_grids_rep = np.zeros((N_quat, cube_dim**3), dtype=np.float32)

gen_lig_grid(
    GRID_SPACING, charges, epsilons, vdw_rs,
    coords, N_coord, quats, N_quat, cube_dim, min_coord,
    rot_coords, elec_grids, vdw_grids_attr, vdw_grids_rep
)

print(elec_grids[-1])
print(vdw_grids_attr[-1])
print(vdw_grids_rep[-1])
