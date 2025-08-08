import numpy as np
from numpy.random import randn
import fft_correlate

rand_sample = randn(100000).astype(np.float32)
inds = fft_correlate.argsort(rand_sample)
np_inds = np.argsort(rand_sample)

print(np.alltrue(inds == np_inds))
print(np.where(inds != np_inds))
print(inds[inds != np_inds])
print(np_inds[inds != np_inds])
print(rand_sample[inds[inds != np_inds]])
print(rand_sample[np_inds[inds != np_inds]])