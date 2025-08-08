import pickle
import numpy as np
from crimm.Docking import FFTDocker
from crimm.Adaptors.RDKitConverter import create_probe_confomers, write_conformers_sdf
from crimm.Data.probes.probes import create_new_probe_set

with open('/home/truman/crimm/notebooks/2HYY.pkl', 'rb') as fh:
    chain = pickle.load(fh)

fft_docker = FFTDocker(
    grid_spacing=0.8, receptor_padding=8.0,
    effective_grid_shape='convex_hull', 
    rad_dielec_const=2.0,
    elec_rep_max=40, elec_attr_max=-20,
    vdw_rep_max=2.0, vdw_attr_max=-1.0, use_constant_dielectric=False,
    rotation_level=2, n_top_poses=1000, reduce_sample_factor=10,
    n_threads=24
)

fft_docker.load_receptor(chain)
probe_set = create_new_probe_set()
probe = probe = probe_set['urea']

# scores, conf_coords = fft_docker.dock(probe)
fft_docker.result = np.load('/home/truman/crimm/notebooks/docked_scores.npy')
top_scores, conf_coords = fft_docker.rank_poses()
mol = create_probe_confomers(probe, conf_coords)
write_conformers_sdf(mol, 'output/test_urea6.sdf')
