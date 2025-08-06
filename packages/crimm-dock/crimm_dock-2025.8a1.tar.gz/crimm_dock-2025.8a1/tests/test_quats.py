import ctypes
import numpy as np
from numpy.ctypeslib import ndpointer

# Define pointer type
nd_float_ptr_type = ndpointer(ctypes.c_float, flags="C_CONTIGUOUS")

# Load the shared library
lib = ctypes.cdll.LoadLibrary('/home/truman/crimm/src/quat_rot.so')

# Define the ctypes structures
class Quaternion(ctypes.Structure):
    _fields_ = [('w', ctypes.c_float),
                ('x', ctypes.c_float),
                ('y', ctypes.c_float),
                ('z', ctypes.c_float)]

class Vector3d(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float),
                ('y', ctypes.c_float),
                ('z', ctypes.c_float)]

# Define the return type of QuaternionRotate function to be Vector3d
quat_rot = lib.QuaternionRotate
quat_rot.restype = Vector3d
quat_rot.argtypes = [Quaternion, Vector3d]

batch_quat_rot = lib.BatchQuatornionRotate
batch_quat_rot.restype = None
batch_quat_rot.argtypes = [
    nd_float_ptr_type, # quats
    nd_float_ptr_type, # coords
    ctypes.c_int, # N_quats
    ctypes.c_int, # N_coords
    nd_float_ptr_type, # rot_coords (out)
]

# Assuming these are your numpy arrays:
np_quaternion = np.array([1,0,1,0], dtype=np.float32)
np_3dpoint = np.array([1,0,0], dtype=np.float32)

# Convert numpy arrays to ctypes structures
quaternion = Quaternion(*np_quaternion)
point3d = Vector3d(*np_3dpoint)

# Call the function
result = lib.QuaternionRotate(quaternion, point3d)

# Result is a ctypes structure. If you want a numpy array:
np_result = np.array([result.x, result.y, result.z], dtype=np.float32)
print(np_result)

# Batch version
pdbid = '1AKA'
quats = np.ascontiguousarray(np.load('/home/truman/crimm/notebooks/qua1.npy'), dtype=np.float32)
coords = np.ascontiguousarray(np.load(f'../notebooks/{pdbid}_grid/coords.npy'), dtype=np.float32)
N_coord = coords.shape[0]
N_quat = quats.shape[0]

# Allocate memory for the rotated coordinates
rot_coords = np.zeros((N_quat, N_coord, 3), dtype=np.float32)

# Call the function
batch_quat_rot(quats, coords, N_quat, N_coord, rot_coords)

# Result is a ctypes structure. If you want a numpy array:
np_rot_coords = np.array(rot_coords, dtype=np.float32)

print(np_rot_coords[:10])
np.save('rot_coords.npy', np_rot_coords)
