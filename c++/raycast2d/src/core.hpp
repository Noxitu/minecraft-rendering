#include <array>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <vector>

template<typename Type, int DIMS>
struct View
{
    Type *data;
    std::array<int, DIMS> shape;
    std::array<int, DIMS> stride;

    Type &operator() (int i0) const
    {
        static_assert(DIMS == 1, "Wrong dimensions for operator()");
        return data[i0*stride[0]];
    }

    Type &operator() (int i0, int i1) const
    {
        static_assert(DIMS == 2, "Wrong dimensions for operator()");
        return data[i0*stride[0] + i1*stride[1]];
    }

    Type &operator() (int i0, int i1, int i2) const
    {
        static_assert(DIMS == 3, "Wrong dimensions for operator()");
        return data[i0*stride[0] + i1*stride[1] + i2*stride[2]];
    }
};

template<typename Type>
View<Type, 2> view(std::vector<Type> &buffer, int rows, int cols)
{
    return {buffer.data(), {rows, cols}, {cols, 1}};
}


template<typename T>
struct Matrix
{
    std::shared_ptr<std::vector<T>> data;
};

template<typename Type>
void save(const char *path, const View<Type, 2> &view)
{
    std::ofstream out(path, std::ios_base::binary);
    for (int y = 0; y < view.shape[0]; ++y)
        for (int x = 0; x < view.shape[1]; ++x)
        {
            auto &value = view(y, x);
            out.write(reinterpret_cast<char*>(&value), sizeof(Type));
        }
}

void imshow(const View<int, 2> &view)
{
    save("imshow.txt", view);
    std::stringstream script;
    script << "python -c \""
           << "import matplotlib.pyplot as plt;"
           << "import numpy as np;"
           << "buffer = open('imshow.txt', 'rb').read();"
           << "array = np.frombuffer(buffer, dtype=int).reshape(" << view.shape[0] << ", " << view.shape[1] << ");"
           << "plt.imshow(array);"
           << "plt.show();"
           << "\"";

    system(script.str().c_str());
}
