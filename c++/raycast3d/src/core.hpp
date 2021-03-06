#include <array>

template<typename Type, int DIMS>
struct Array
{
    Type *data;
    std::array<int, DIMS> shape;

    Type &operator()(long long i)
    {
        static_assert(DIMS == 1, "1-d array requires 1-d index.");
        return data[i];
    }

    Type &operator()(long long i, long long j)
    {
        static_assert(DIMS == 2, "2-d array requires 2-d index.");
        return data[i*shape[1] + j];
    }

    Type &operator()(long long i, long long j, long long k)
    {
        static_assert(DIMS == 3, "3-d array requires 3-d index.");
        return data[i*shape[1]*shape[2] + j*shape[2] + k];
    }
};

template<typename Type>
Array<Type, 1> array1d(void *ptr, int dims, long long *shape, long long *stride)
{
    if (dims != 1) throw std::logic_error("array1d: Wrong dims");
    if (stride[0] != sizeof(Type)) throw std::logic_error("array1d: Wrong stride[0]");

    return {reinterpret_cast<Type*>(ptr), {static_cast<int>(shape[0])}};
}

template<typename Type>
Array<Type, 2> array2d(void *ptr, int dims, long long *shape, long long *stride)
{
    if (dims != 2) throw std::logic_error("array2d: Wrong dims");
    if (stride[1] != sizeof(Type)) throw std::logic_error("array2d: Wrong stride[1]");
    if (stride[0] != shape[1]*sizeof(Type)) throw std::logic_error("array2d: Wrong stride[0]");

    return {reinterpret_cast<Type*>(ptr), {static_cast<int>(shape[0]), static_cast<int>(shape[1])}};
}

template<typename Type>
Array<Type, 3> array3d(void *ptr, int dims, long long *shape, long long *stride)
{
    if (dims != 3) throw std::logic_error("array3d: Wrong dims");
    if (stride[2] != sizeof(Type)) throw std::logic_error("array3d: Wrong stride[2]");
    if (stride[1] != shape[2]*sizeof(Type)) throw std::logic_error("array3d: Wrong stride[1]");
    if (stride[0] != shape[1]*shape[2]*sizeof(Type)) throw std::logic_error("array3d: Wrong stride[0]");

    return {reinterpret_cast<Type*>(ptr), {static_cast<int>(shape[0]), static_cast<int>(shape[1]), static_cast<int>(shape[2])}};
}