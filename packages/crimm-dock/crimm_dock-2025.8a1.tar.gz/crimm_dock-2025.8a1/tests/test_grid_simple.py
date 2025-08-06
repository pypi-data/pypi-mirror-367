import ctypes
import numpy as np
from numpy.ctypeslib import ndpointer

CC_ELEC = 332.0716
single_precision = False
use_cuda = False

if single_precision:
    nd_float_ptr_type = ndpointer(ctypes.c_float, flags="C_CONTIGUOUS")
    c_float = ctypes.c_float
    np_float = np.float32
    lib_kw1 = 'single'
else:
    nd_float_ptr_type = ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")
    c_float = ctypes.c_double
    np_float = np.float64
    lib_kw1 = 'simple'

if use_cuda:
    lib_kw2 = '.cuda'
else:
    lib_kw2 = ''
# Load the shared library
lib = ctypes.CDLL(f"/home/truman/crimm/src/grid_gen_{lib_kw1}{lib_kw2}.so")
# Define the argument dtype and return types for the C functions
cdist = lib.calc_pairwise_dist
cdist.restype = None
cdist.argtypes = [
    nd_float_ptr_type, # grid_pos
    nd_float_ptr_type, # coords
    ctypes.c_int, # N_coord
    ctypes.c_int, # N_grid_points
    nd_float_ptr_type # dists (out)
]

gen_all_grids = lib.gen_all_grids
gen_all_grids.restype = None
gen_all_grids.argtypes = [
    nd_float_ptr_type, # grid_pos
    nd_float_ptr_type, # coords
    nd_float_ptr_type, # charges
    nd_float_ptr_type, # epsilons
    nd_float_ptr_type, # vdw_rs
    c_float, # CC_ELEC
    c_float, # rad_dielec_const
    c_float, # elec_rep_max
    c_float, # elec_attr_max
    c_float, # vwd_rep_max
    c_float, # vwd_attr_max
    ctypes.c_int, # N_coord
    ctypes.c_int, # N_grid_points
    nd_float_ptr_type, # elec_grid (out)
    nd_float_ptr_type, # vdw_grid_attr (out)
    nd_float_ptr_type # vdw_grid_rep (out)
]

def cdist_wrapper(grid_pos, coords):
    N_coord, N_grid_points = coords.shape[0], grid_pos.shape[0]
    dists = np.zeros(N_grid_points*N_coord, dtype=np_float, order='C')
    cdist(
        grid_pos, coords, N_coord, N_grid_points, dists
    )
    return dists.reshape(N_grid_points, N_coord)

def gen_all_grids_wrapper(
        grid_pos, coords, charges, epsilons, vdw_rs,
        rad_dielec_const, elec_rep_max, elec_attr_max,
        vwd_rep_max, vwd_attr_max
    ):
    """Generate the electrostatic and van der Waals grids."""
    elec_rep_max = abs(elec_rep_max)
    elec_attr_max = -abs(elec_attr_max)
    vwd_rep_max = abs(vwd_rep_max)
    vwd_attr_max = -abs(vwd_attr_max)
    N_coord, N_grid_points = coords.shape[0], grid_pos.shape[0]
    elec_grid = np.zeros(N_grid_points, dtype=np_float, order='C')
    vdw_grid_attr = np.zeros(N_grid_points, dtype=np_float, order='C')
    vdw_grid_rep = np.zeros(N_grid_points, dtype=np_float, order='C')

    gen_all_grids(
        # Ensure contiguity of the arrays to pass to the C function
        np.ascontiguousarray(grid_pos), np.ascontiguousarray(coords),
        charges, epsilons, vdw_rs, CC_ELEC, rad_dielec_const,
        elec_rep_max, elec_attr_max, vwd_rep_max, vwd_attr_max,
        N_coord, N_grid_points, elec_grid, vdw_grid_attr, vdw_grid_rep
    )
    return elec_grid, vdw_grid_attr, vdw_grid_rep

if __name__ == '__main__':
    pdbid = '1AKA'
    vdw_rs = np.ascontiguousarray(np.load(f'../notebooks/{pdbid}_grid/vdw_rs.npy'), dtype=np_float) # 1d array with size of N_coords
    epsilons = np.ascontiguousarray(np.load(f'../notebooks/{pdbid}_grid/epsilons.npy'), dtype=np_float) # 1d array with size of N_coords
    coords = np.ascontiguousarray(np.load(f'../notebooks/{pdbid}_grid/coords.npy'), dtype=np_float) # 2d array with size of (N_coords, 3)
    charges = np.ascontiguousarray(np.load(f'../notebooks/{pdbid}_grid/charges.npy'), dtype=np_float) # 1d array with size of N_coords
    grid_pos = np.ascontiguousarray(np.load(f'../notebooks/{pdbid}_grid/grid_pos.npy'), dtype=np_float)

    # vdw_rs = np.ascontiguousarray(np.load('../notebooks/vdw_rs.npy')) # 1d array with size of N_coords
    # epsilons = np.ascontiguousarray(np.load('../notebooks/epsilons.npy')) # 1d array with size of N_coords
    # coords = np.ascontiguousarray(np.load('../notebooks/prot_coords.npy')) # 2d array with size of (N_coords, 3)
    # charges = np.ascontiguousarray(np.load('../notebooks/charges.npy')) # 1d array with size of N_coords
    # grid_pos = np.ascontiguousarray(np.load('../notebooks/grid_pos.npy'))

    # pdists = cdist_wrapper(grid_pos, coords)

    # print(grid_pos.shape)
    # print(coords.shape)
    # print(charges.shape)
    # print(epsilons.shape)
    # print(vdw_rs.shape)

    elec_grid, vdw_grid_attr, vdw_grid_rep = gen_all_grids_wrapper(
        grid_pos, coords, charges, epsilons, vdw_rs,
        rad_dielec_const=2.0, elec_rep_max=40, elec_attr_max=-20,
        vwd_rep_max=2.0, vwd_attr_max=-1.0
    )

    # print(pdists)
    print(elec_grid)
    print(vdw_grid_attr)
    print(vdw_grid_rep)
    print(vdw_grid_rep+vdw_grid_attr)
