#include "core.hpp"
#include "raycast_amp.hpp"
#include <iostream>

#define ARRAY_ARG_SIGNATURE(name) void *name ## _ptr, int name ## _dims, long long *name ## _shape, long long *name ## _strides
#define ARRAY_ARG_VALUE(type, name) auto name = type(name ## _ptr, name ## _dims, name ## _shape, name ## _strides)

extern "C" __declspec(dllexport) void raycast(
    ARRAY_ARG_SIGNATURE(rays),
    ARRAY_ARG_SIGNATURE(world),
    ARRAY_ARG_SIGNATURE(world_mask),
    ARRAY_ARG_SIGNATURE(result),
    ARRAY_ARG_SIGNATURE(result_depth)
) try
{
    ARRAY_ARG_VALUE(array2d<double>, rays);
    ARRAY_ARG_VALUE(array3d<unsigned short>, world);
    ARRAY_ARG_VALUE(array3d<unsigned char>, world_mask);
    ARRAY_ARG_VALUE(array1d<int>, result);
    ARRAY_ARG_VALUE(array1d<double>, result_depth);

    noxitu::minecraft::raycast(rays, world, world_mask, result, result_depth);
}
catch(std::exception &ex)
{
    std::cerr << "Failed with exception " << typeid(ex).name() << ": " << ex.what() << std::endl;
}