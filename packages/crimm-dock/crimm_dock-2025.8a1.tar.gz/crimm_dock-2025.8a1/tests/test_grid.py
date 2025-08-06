import ctypes
import numpy as np
from numpy.ctypeslib import ndpointer

CC_ELEC = 332.0716
nd_float_ptr_type = ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")
# Load the shared library
# lib = ctypes.CDLL("/home/truman/crimm/src/grid_gen1.cuda.so")
lib = ctypes.CDLL("/home/truman/crimm/src/grid_gen.so")
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

gen_elec_grid = lib.gen_elec_grid
gen_elec_grid.restype = None
gen_elec_grid.argtypes = [
    nd_float_ptr_type, # dists
    nd_float_ptr_type, # charges
    ctypes.c_double, # cc_elec
    ctypes.c_double, # rad_dielec_const
    ctypes.c_double, # elec_attr_max
    ctypes.c_double, # elec_attr_max
    ctypes.c_int, # N_coord
    ctypes.c_int, # N_grid_points
    nd_float_ptr_type # elec_grid (out)
]

gen_vdw_grid = lib.gen_vdw_grid
gen_vdw_grid.restype = None
gen_vdw_grid.argtypes = [
    nd_float_ptr_type, # dists
    nd_float_ptr_type, # epsilons
    nd_float_ptr_type, # vdw_rs
    ctypes.c_double, # probe_radius
    ctypes.c_double, # vwd_softcore_max
    ctypes.c_int, # N_coord
    ctypes.c_int, # N_grid_points
    nd_float_ptr_type # vdw_grid (out)
]

gen_all_grids = lib.gen_all_grids
gen_all_grids.restype = None
gen_all_grids.argtypes = [
    nd_float_ptr_type, # grid_pos
    nd_float_ptr_type, # coords
    nd_float_ptr_type, # charges
    nd_float_ptr_type, # epsilons
    nd_float_ptr_type, # vdw_rs
    ctypes.c_double, # CC_ELEC
    ctypes.c_double, # rad_dielec_const
    ctypes.c_double, # elec_rep_max
    ctypes.c_double, # elec_attr_max
    ctypes.c_double, # probe_radius
    ctypes.c_double, # vwd_softcore_max
    ctypes.c_int, # N_coord
    ctypes.c_int, # N_grid_points
    nd_float_ptr_type, # dists (out)
    nd_float_ptr_type, # elec_grid (out)
    nd_float_ptr_type # vdw_grid (out)
]

def cdist_wrapper(grid_pos, coords):
    N_coord, N_grid_points = coords.shape[0], grid_pos.shape[0]
    dists = np.zeros(N_grid_points*N_coord, dtype=np.double, order='C')
    cdist(
        grid_pos, coords, N_coord, N_grid_points, dists
    )
    return dists.reshape(N_grid_points, N_coord)

def gen_elec_grid_wrapper(
    dists, charges, rad_dielec_const, elec_rep_max, elec_attr_max
):
    N_coord = charges.shape[0]
    assert dists.size%N_coord == 0
    N_grid_points = dists.size//N_coord

    elec_grid = np.zeros(N_grid_points, dtype=np.double, order='C')
    gen_elec_grid(
        dists, charges, CC_ELEC, rad_dielec_const, elec_rep_max, elec_attr_max,
        N_coord, N_grid_points, elec_grid
    )

    return elec_grid

def gen_vdw_grid_wrapper(
    dists, epsilons, vdw_rs, probe_radius, vwd_softcore_max
):
    N_coord = epsilons.shape[0]
    assert dists.size%N_coord == 0
    N_grid_points = dists.size//N_coord

    vdw_grid = np.zeros(N_grid_points, dtype=np.double, order='C')
    gen_vdw_grid(
        dists, epsilons, vdw_rs, probe_radius, vwd_softcore_max,
        N_coord, N_grid_points, vdw_grid
    )

    return vdw_grid

def gen_all_grids_wrapper(
        grid_pos, coords, charges, epsilons, vdw_rs, 
        rad_dielec_const, elec_rep_max, elec_attr_max, probe_radius,
        vwd_softcore_max
    ):
    """Generate the electrostatic and van der Waals grids."""
    N_coord, N_grid_points = coords.shape[0], grid_pos.shape[0]
    dists = np.zeros(N_grid_points*N_coord, dtype=np.double, order='C')
    elec_grid = np.zeros(N_grid_points, dtype=np.double, order='C')
    vdw_grid = np.zeros(N_grid_points, dtype=np.double, order='C')

    gen_all_grids(
        # Ensure contiguity of the arrays to pass to the C function
        np.ascontiguousarray(grid_pos), np.ascontiguousarray(coords),
        charges, epsilons, vdw_rs, CC_ELEC, rad_dielec_const,
        elec_rep_max, elec_attr_max, probe_radius, vwd_softcore_max,
        N_coord, N_grid_points, dists, elec_grid, vdw_grid
    )
    return dists.reshape(N_grid_points, N_coord), elec_grid, vdw_grid

if __name__ == '__main__':
    vdw_rs = np.ascontiguousarray(np.load('../notebooks/1AKA_grid/vdw_rs.npy')) # 1d array with size of N_coords
    epsilons = np.ascontiguousarray(np.load('../notebooks/1AKA_grid/epsilons.npy')) # 1d array with size of N_coords
    coords = np.ascontiguousarray(np.load('../notebooks/1AKA_grid/coords.npy')) # 2d array with size of (N_coords, 3)
    charges = np.ascontiguousarray(np.load('../notebooks/1AKA_grid/charges.npy')) # 1d array with size of N_coords
    grid_pos = np.ascontiguousarray(np.load('../notebooks/1AKA_grid/grid_pos.npy'))

    # vdw_rs = np.ascontiguousarray(np.load('../notebooks/vdw_rs.npy')) # 1d array with size of N_coords
    # epsilons = np.ascontiguousarray(np.load('../notebooks/epsilons.npy')) # 1d array with size of N_coords
    # coords = np.ascontiguousarray(np.load('../notebooks/prot_coords.npy')) # 2d array with size of (N_coords, 3)
    # charges = np.ascontiguousarray(np.load('../notebooks/charges.npy')) # 1d array with size of N_coords
    # grid_pos = np.ascontiguousarray(np.load('../notebooks/grid_pos.npy'))

    eps_softcore_repulsion_max = 40
    eps_softcore_attraction_max = -20
    vwd_softcore_max = 2.0
    radial_dielec_const = 2.0 # Dielec
    probe_radius = 0.0
    # probe_radius = 2.300
    
    # pdists = cdist_wrapper(grid_pos, coords)

    # elec_grid = gen_elec_grid_wrapper(
    #     pdists, charges, radial_dielec_const, 
    #     eps_softcore_repulsion_max, eps_softcore_attraction_max
    # )

    # vdw_grid = gen_vdw_grid_wrapper(
    #     pdists, epsilons, vdw_rs, probe_radius, vwd_softcore_max
    # )

    pdists, elec_grid, vdw_grid = gen_all_grids_wrapper(
        grid_pos, coords, charges, epsilons, vdw_rs,
        rad_dielec_const=2.0, elec_rep_max=40, elec_attr_max=-20,
        probe_radius=0.0, vwd_softcore_max=2.0
    )

    print(pdists)
    print(elec_grid)
    print(vdw_grid)
