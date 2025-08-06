import numpy as np
# import timeit
import time
import fft_correlate
from scipy.signal import correlate
from tqdm.contrib.concurrent import process_map

def scipy_correlate(kernel):
    results = []
    for s, k in zip(signal, kernel):
        results.append(correlate(s, k, mode='same', method='fft'))
    return np.asarray(results)

# Create a test signal
kernels = np.load(
    '/home/truman/crimm/notebooks/fft_data/kernels.npy'
).astype(np.float32)[:10]
signal = np.load(
    '/home/truman/crimm/notebooks/fft_data/signal.npy'
).astype(np.float32)

print(len(kernels)*signal.size*signal.itemsize/1024**3, 'GB')

time1 = time.time()
n_orientation, n_grids, x,y,z = kernels.shape
# The kernels need to be zero-padded to the size of the signal, so
# we put the values of kernels in the last 3 dimensions of result 
# to save memory. The fft_correlate_batch function will read the values
# and overwrite them with the result of the fft correlation.
result = np.zeros((len(kernels), *signal.shape), dtype=np.float32)
result[:,:,:x,:y,:z] = kernels

# Perform the convolution
fft_correlate.fft_correlate_batch(signal, result, 1)
result = np.flip(result, axis=(-3,-2,-1))
result = np.roll(result, (3,3,3), axis=(-3,-2,-1))

time2 = time.time()
print('time:', time2 - time1)

time1 = time.time()

result_scipy = process_map(scipy_correlate, kernels, max_workers=4, chunksize=1)
result_scipy = np.array(result_scipy)

time2 = time.time()
print('time:', time2 - time1)

print(np.allclose(result, result_scipy))
print(np.max(np.abs(result - result_scipy)))
print(np.min(result))
print(np.min(result_scipy))

print(np.argmin(result))
print(np.argmin(result_scipy))
