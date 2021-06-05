import ctypes

import numpy as np

def array(a):
    return (
        ctypes.c_void_p(a.ctypes.data),
        ctypes.c_int(len(a.shape)), 
        a.ctypes.shape,
        a.ctypes.strides
    )

_raycast_impl = ctypes.WinDLL('c++/build/raycast3d/Release/RayCasting.dll').raycast

def raycast(rays, world, mask):
    result = np.zeros(rays.shape[:-1], dtype=int)
    result_depth = np.zeros(rays.shape[:-1], dtype=float)

    batch_size = 10_000_000

    for offset in range(0, result.size, batch_size):
        batch = slice(offset, offset+batch_size)

        _raycast_impl(
            *array(rays.reshape(-1, 6)[batch]),
            *array(world),
            *array(mask),
            *array(result.ravel()[batch]),
            *array(result_depth.ravel()[batch])
        )

    return (
        (result & 0xffff).astype(np.uint16),
        result_depth,
        ((result & 0x70000) >> 16).astype(np.uint8)
    )


def chain_masks(base, *masks):
    ret = base.copy()

    for mask in masks:
        ret[ret] &= mask

    return ret


def normalize_factors(*factors, mask=..., norm=sum):
    factors = np.array(factors, dtype=float)
    return factors / norm(factors[mask])



def pyplot(*buffers, mask=None):
    import matplotlib.pyplot as plt

    for buffer in buffers:
        if len(buffer.shape) == 1 or len(buffer.shape) == 2 and buffer.shape[1] == 3:
            canvas = np.zeros(mask.shape if len(buffer.shape) == 1 else (mask.shape[0], mask.shape[1], 3), dtype=buffer.dtype)
            try:
                canvas[:] = float('inf')
            except OverflowError:
                pass
            canvas[mask] = buffer
        else:
            canvas = buffer

        plt.figure()
        plt.imshow(canvas)

    plt.show()