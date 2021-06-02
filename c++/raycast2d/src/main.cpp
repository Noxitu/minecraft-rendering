#include "core.hpp"
// #include "raycast_cpu.hpp"
#include "raycast_amp.hpp"

#include <chrono>
#include <cmath>
#include <iostream>
#include <vector>

struct Vec
{
    double x, y;
};

Vec angle(double a)
{
    Vec vec = {std::cos(a), std::sin(a)};
    return vec;
}

struct RayState { int y, x; double distance; };

auto traverse = [](auto &rays, auto &map)
{
    const int n = rays.shape[0];

    std::vector<int> cells_buffer(2*n);
    auto cells = view(cells_buffer, n, 2);

    for (int i = 0; i < n; ++i)
    {
        cells(i, 0) = static_cast<int>(rays(i, 0));
        cells(i, 1) = static_cast<int>(rays(i, 1));
    }

    std::cout << "Starting raycasting... " << std::endl;

    const auto time_start = std::chrono::high_resolution_clock::now();

    raycast(rays, map, cells);

    const auto time_end = std::chrono::high_resolution_clock::now();

    std::cout << "Took " << std::chrono::duration_cast<std::chrono::milliseconds>(time_end-time_start).count() << "ms" << std::endl;
};


int main() try
{
    const int size = 2048;
    const int n = 640*480;

    std::vector<int> buffer(size*size, 0);

    auto map = view(buffer, size, size);

    std::vector<double> raysBuffer(n*4, 0);
    auto rays = view(raysBuffer, n, 4);

    for (int i = 0; i < n; ++i)
    {
        const auto vec = angle(i*3.14159*2/n);

        rays(i, 0) = size/2.0;
        rays(i, 1) = size/2.0;
        rays(i, 2) = vec.x;
        rays(i, 3) = vec.y;
    }

    traverse(rays, map);
    
    imshow(map);
}
catch(std::exception &ex)
{
    std::cout << "Exception thrown: " << typeid(ex).name() << ": " << ex.what() << std::endl;
}
catch(int x)
{
    std::cout << "Int thrown: " << x << std::endl;
}
catch(...)
{
    std::cout << "Something thrown" << std::endl;
}