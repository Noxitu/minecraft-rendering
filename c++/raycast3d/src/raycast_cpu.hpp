#include <iostream>
#include <chrono>

namespace detail
{
    const int OUTER_ITERATIONS = 256;
    const int INNER_ITERATIONS = 128;

    enum state {
        STATE_NORMAL,
        STATE_HIT
    };

    constexpr bool LOG = false;

    inline double next_intersection(int c, double c0, double dir_inv)
    {
        if (dir_inv > 0)
            return (c-c0+1)*dir_inv;
        
        if (dir_inv < 0)
            return (c-c0)*dir_inv;

        return INFINITY;
    }

    template<typename Array>
    inline int advance(int &x, int &y, int &z,
                        const double x0, const double y0, const double z0,
                        const double rx_inv, const double ry_inv, const double rz_inv,
                        const int size_x, const int size_y, const int size_z,
                        Array &world,
                        double &depth,
                        int &normal_idx
    )
    {
        const double dx = next_intersection(x, x0, rx_inv);
        const double dy = next_intersection(y, y0, ry_inv);
        const double dz = next_intersection(z, z0, rz_inv);

        if (dx < dy && dx < dz)
        {
            depth = dx;
            x += (rx_inv > 0 ? 1 : -1);
            normal_idx = (rx_inv > 0 ? 1 : 2);
        }
        else if (dy < dz)
        {
            depth = dy;
            y += (ry_inv > 0 ? 1 : -1);
            normal_idx = (ry_inv > 0 ? 3 : 4);
        }
        else
        {
            depth = dz;
            z += (rz_inv > 0 ? 1 : -1);
            normal_idx = (rz_inv > 0 ? 5 : 6);
        }

        const bool inside = (x >= 0 && y >= 0 && z >= 0 && x < size_x && y < size_y && z < size_z);

        if (inside)
            return world(y, z, x);
        
        return -1;
    }

    auto invoke_raycasting = [](
        int size_x, int size_y, int size_z,
        auto &rays,
        auto &world,
        auto &block_mask,
        auto &result,
        auto &result_depth
    )
    {
        const int n_rays = rays.shape[0];

        #pragma omp parallel for schedule(dynamic, 1024)
        for (int i = 0; i < n_rays; ++i)
        {
            const double x0 = rays(i, 0);
            const double y0 = rays(i, 1);
            const double z0 = rays(i, 2);
            const double rx_inv = 1/rays(i, 3);
            const double ry_inv = 1/rays(i, 4);
            const double rz_inv = 1/rays(i, 5);

            int x = static_cast<int>(x0);
            int y = static_cast<int>(y0);
            int z = static_cast<int>(z0);

            int state = STATE_NORMAL;

            for (int outer_iter = 0; outer_iter < OUTER_ITERATIONS; ++outer_iter)
            {
                if (state != STATE_NORMAL) break;

                if (rx_inv > 0 && x >= size_x) break;
                if (ry_inv > 0 && y >= size_y) break;
                if (rz_inv > 0 && z >= size_z) break;

                if (rx_inv < 0 && x < 0) break;
                if (ry_inv < 0 && y < 0) break;
                if (rz_inv < 0 && z < 0) break;

                for(int iter = 0; iter < INNER_ITERATIONS; ++iter)
                {
                    double depth;
                    int normal_idx = 0;
                    const int block_id = advance(x, y, z, x0, y0, z0, rx_inv, ry_inv, rz_inv, size_x, size_y, size_z, world, depth, normal_idx);

                    if (block_id != -1 && block_mask(block_id) != 0)
                    {
                        result(i) = 
                            block_id & 0xffff |
                            (normal_idx << 16) & 0x70000;

                        result_depth(i) = depth;
                        state = STATE_HIT;
                        break;
                    }
                }
            }
        }
    };
}

namespace noxitu { namespace minecraft
{
    auto raycast = [](auto &rays, auto &world, auto &block_mask, auto &result, auto &result_depth)
    {
        using namespace detail;

        const int n_rays = rays.shape[0];
        const int ray_elements = 6;

        const int size_x = world.shape[2];
        const int size_y = world.shape[0];
        const int size_z = world.shape[1];

        if (rays.shape[1] != ray_elements)
            throw std::logic_error("raycast: incorrect rays shape");

        if (n_rays != result.shape[0])
            throw std::logic_error("raycast: incorrect result shape");

        if (n_rays != result_depth.shape[0])
            throw std::logic_error("raycast: incorrect result_depth shape");

        auto zero = std::chrono::high_resolution_clock::now();

        auto ts = [zero]
        {
            auto now = std::chrono::high_resolution_clock::now();
            return std::chrono::duration_cast<std::chrono::milliseconds>(now-zero).count();
        };

        if (LOG) std::cout << ts() << "ms -- " << "Running raycasting..." << std::endl;

        invoke_raycasting(
            size_x, size_y, size_z,
            rays,
            world,
            block_mask,
            result,
            result_depth
        );

        if (LOG) std::cout << ts() << "ms -- " << "Raycasting done." << std::endl;
    };
}}