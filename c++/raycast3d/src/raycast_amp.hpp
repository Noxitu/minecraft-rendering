#include <amp.h>
#include <iostream>
#include <chrono>

namespace
{
    constexpr bool LOG = false;

    inline unsigned int query_world(const concurrency::array_view<const unsigned int, 3> &buffer, int y, int z, int x) restrict(amp)
    {
        const unsigned int value = buffer(y, z, x/2);
        return (value >> (x%2*16)) & 0xffff;
    }

    inline unsigned int query_world_mask(const concurrency::array_view<const unsigned int, 3> &buffer, int y, int z, int x) restrict(amp)
    {
        const unsigned int value = buffer(y, z, x/4);
        return (value >> (x%4*8)) & 0xff;
    }

    inline bool advance(int &x, int &y, int &z,
                        const double x0, const double y0, const double z0,
                        const double rx_inv, const double ry_inv, const double rz_inv,
                        const int size_x, const int size_y, const int size_z,
                        const concurrency::array_view<const unsigned int, 3> &world_mask,
                        double &depth,
                        int &normal_idx
    ) restrict(amp)
    {
        double dx = INFINITY;
        double dy = INFINITY;
        double dz = INFINITY;

        if (rx_inv > 0)
            dx = (x-x0+1)*rx_inv;
        else if (rx_inv < 0)
            dx = (x-x0)*rx_inv;

        if (ry_inv > 0)
            dy = (y-y0+1)*ry_inv;
        else if (ry_inv < 0)
            dy = (y-y0)*ry_inv;

        if (rz_inv > 0)
            dz = (z-z0+1)*rz_inv;
        else if (rz_inv < 0)
            dz = (z-z0)*rz_inv;

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

        if (inside && query_world_mask(world_mask, y, z, x) != 0)
            return true;
        
        return false;
    }
}

namespace noxitu { namespace minecraft
{
    enum state {
        STATE_NORMAL,
        STATE_HIT
    };

    auto raycast = [](auto &rays_, auto &world_, auto &world_mask_, auto &result_, auto &result_depth_)
    {
        namespace amp = concurrency;

        const int OUTER_ITERATIONS = 64;
        const int INNER_ITERATIONS = 128;
        const int RAYS_PER_CALL = 500'000;

        const int n_rays = rays_.shape[0];
        const int ray_elements = 6;

        const int size_x = world_.shape[2];
        const int size_y = world_.shape[0];
        const int size_z = world_.shape[1];

        if (rays_.shape[1] != ray_elements)
            throw std::logic_error("raycast: incorrect rays shape");

        if (size_y != world_mask_.shape[0] || size_z != world_mask_.shape[1] || size_x != world_mask_.shape[2])
            throw std::logic_error("raycast: incorrect world_mask_ shape");

        if (n_rays != result_.shape[0])
            throw std::logic_error("raycast: incorrect result shape");

        if (n_rays != result_depth_.shape[0])
            throw std::logic_error("raycast: incorrect result_depth shape");

        if (size_x % 4 != 0)
            throw std::logic_error("raycast: require world.shape[2] divisible by 2");

        amp::array_view<const double, 2> rays(n_rays, ray_elements, rays_.data);

        amp::array_view<const unsigned int, 3> world(
            size_y,
            size_z,
            size_x / 2,
            reinterpret_cast<unsigned int*>(world_.data)
        );

        amp::array_view<const unsigned int, 3> world_mask(
            size_y,
            size_z,
            size_x / 4,
            reinterpret_cast<unsigned int*>(world_mask_.data)
        );

        amp::array_view<int, 1> result(n_rays, result_.data);
        amp::array_view<double, 1> result_depth(n_rays, result_depth_.data);

        std::vector<int> state_buffer(4*n_rays);
        amp::array_view<int, 2> state(n_rays, 4, state_buffer.data());

        for (int i = 0; i < n_rays; ++i)
        {
            state(i,0) = static_cast<int>(rays(i, 0));
            state(i,1) = static_cast<int>(rays(i, 1));
            state(i,2) = static_cast<int>(rays(i, 2));
            state(i,3) = STATE_NORMAL;
        }

        for (int outer_iter = 0; outer_iter < OUTER_ITERATIONS; ++outer_iter)
        {
            for (int offset = 0; offset < n_rays; offset += RAYS_PER_CALL)
            {
                const int batch_size = min(n_rays-offset, RAYS_PER_CALL);
                amp::extent<1> batch(batch_size);

                const auto time_start = std::chrono::high_resolution_clock::now();

                if (LOG)
                    std::cerr << "Starting batch: " << offset << ".." << offset+batch_size << std::endl;

                amp::parallel_for_each(
                    batch,
                    [=](amp::index<1> idx) restrict(amp)
                    {
                        const int i = idx[0] + offset;

                        if (state(i, 3) != STATE_NORMAL)
                            return;

                        const double x0 = rays(i, 0);
                        const double y0 = rays(i, 1);
                        const double z0 = rays(i, 2);
                        const double rx_inv = 1/rays(i, 3);
                        const double ry_inv = 1/rays(i, 4);
                        const double rz_inv = 1/rays(i, 5);

                        int x = state(i, 0);
                        int y = state(i, 1);
                        int z = state(i, 2);

                        for(int iter = 0; iter < INNER_ITERATIONS; ++iter)
                        {
                            double depth;
                            int normal_idx = 0;
                            const bool hit = advance(x, y, z, x0, y0, z0, rx_inv, ry_inv, rz_inv, size_x, size_y, size_z, world_mask, depth, normal_idx);

                            if (hit)
                            {
                                result(i) = 
                                    query_world(world, y, z, x) & 0xffff |
                                    (normal_idx << 16) & 0x70000;

                                result_depth(i) = depth;
                                state(i, 3) = STATE_HIT;
                                break;
                            }
                        }

                        state(i, 0) = x;
                        state(i, 1) = y;
                        state(i, 2) = z;
                    }
                );

                const auto time_end = std::chrono::high_resolution_clock::now();

                if (LOG)
                {
                    const auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(time_end-time_start);
                    std::cerr << "  batch took " << duration.count() << "ms" << std::endl;
                }
            }
        }
    };
}}