import numpy as np
import fft_correlate
from scipy.signal import correlate

# Create a test signal
signal = np.load('/home/truman/crimm/notebooks/fft_data/signal.npy').astype(np.float32)
kernel = np.load('/home/truman/crimm/notebooks/fft_data/kernel.npy').astype(np.float32)
# kernel = np.load('/home/truman/crimm/notebooks/fft_data/padded_kernel.npy').astype(np.float32)
# signal = signal.reshape(1,*signal.shape)
# kernel = kernel.reshape(1,*kernel.shape)

result = np.empty(signal.shape, dtype=np.float32)
# Perform the convolution

fft_correlate.fft_correlate(signal, kernel, result)

result = np.flip(result)
result = np.roll(result, (3,3,3), axis=(1,2,3))
# Compare with the scipy implementation
result_scipy = []
for s, k in zip(signal, kernel):
    result_scipy.append(correlate(s, k, mode='same'))
result_scipy = np.array(result_scipy)

print(np.allclose(result, result_scipy))
print(np.max(np.abs(result - result_scipy)))
print(np.min(result))
print(np.min(result_scipy))

print(np.argmin(result))
print(np.argmin(result_scipy))
