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

    batch_size = 100_000

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
        print(ret.shape, mask.shape, np.sum(ret))
        print(ret[ret].shape)
        ret[ret] &= mask

    return ret
