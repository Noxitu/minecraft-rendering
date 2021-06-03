#include <amp.h>
#include <iostream>
#include <chrono>

namespace detail
{
    namespace amp = concurrency;

    const int OUTER_ITERATIONS = 64;
    const int INNER_ITERATIONS = 128;
    const int RAYS_PER_CALL = 500'000;

    enum state {
        STATE_NORMAL,
        STATE_HIT
    };

    constexpr bool LOG = false;

    inline unsigned int query_world(const concurrency::array_view<const unsigned int, 3> &buffer, int y, int z, int x) restrict(amp)
    {
        const unsigned int value = buffer(y, z, x/2);
        return (value >> (x%2*16)) & 0xffff;
    }

    inline unsigned int query_block_mask(const concurrency::array_view<const unsigned int, 1> &buffer, int i) restrict(amp)
    {
        const unsigned int value = buffer(i/4);
        return (value >> (i%4*8)) & 0xff;
    }

    inline double next_intersection(int c, double c0, double dir_inv) restrict(amp)
    {
        if (dir_inv > 0)
            return (c-c0+1)*dir_inv;
        
        if (dir_inv < 0)
            return (c-c0)*dir_inv;

        return INFINITY;
    }

    inline int advance(int &x, int &y, int &z,
                        const double x0, const double y0, const double z0,
                        const double rx_inv, const double ry_inv, const double rz_inv,
                        const int size_x, const int size_y, const int size_z,
                        const concurrency::array_view<const unsigned int, 3> &world,
                        double &depth,
                        int &normal_idx
    ) restrict(amp)
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
            return query_world(world, y, z, x);
        
        return -1;
    }

    void invoke_raycasting(
        const amp::extent<1> &batch, const int offset,
        int size_x, int size_y, int size_z,
        amp::array_view<const double, 2> &rays,
        amp::array_view<const unsigned int, 3> world,
        amp::array_view<const unsigned int, 1> block_mask,
        amp::array_view<int, 1> result,
        amp::array_view<double, 1> result_depth,
        amp::array_view<int, 2> state
    )
    {
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

                if (rx_inv > 0 && x >= size_x) return;
                if (ry_inv > 0 && y >= size_y) return;
                if (rz_inv > 0 && z >= size_z) return;

                if (rx_inv < 0 && x < 0) return;
                if (ry_inv < 0 && y < 0) return;
                if (rz_inv < 0 && z < 0) return;

                for(int iter = 0; iter < INNER_ITERATIONS; ++iter)
                {
                    double depth;
                    int normal_idx = 0;
                    const int block_id = advance(x, y, z, x0, y0, z0, rx_inv, ry_inv, rz_inv, size_x, size_y, size_z, world, depth, normal_idx);

                    if (block_id != -1 && query_block_mask(block_mask, block_id))
                    {
                        result(i) = 
                            block_id & 0xffff |
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
    }
}

namespace noxitu { namespace minecraft
{
    auto raycast = [](auto &rays_, auto &world_, auto &block_mask_, auto &result_, auto &result_depth_)
    {
        using namespace detail;
        namespace amp = concurrency;

        const int n_rays = rays_.shape[0];
        const int ray_elements = 6;

        const int size_x = world_.shape[2];
        const int size_y = world_.shape[0];
        const int size_z = world_.shape[1];

        if (rays_.shape[1] != ray_elements)
            throw std::logic_error("raycast: incorrect rays shape");

        if (n_rays != result_.shape[0])
            throw std::logic_error("raycast: incorrect result shape");

        if (n_rays != result_depth_.shape[0])
            throw std::logic_error("raycast: incorrect result_depth shape");

        if (size_x % 2 != 0)
            throw std::logic_error("raycast: require world.shape[2] divisible by 2");

        if (block_mask_.shape[0] % 4 != 0)
            throw std::logic_error("raycast: require block_mask.shape[0] divisible by 2");

        amp::array_view<const double, 2> rays(n_rays, ray_elements, rays_.data);

        amp::array_view<const unsigned int, 3> world(
            size_y,
            size_z,
            size_x / 2,
            reinterpret_cast<unsigned int*>(world_.data)
        );

        amp::array_view<const unsigned int, 1> block_mask(
            block_mask_.shape[0] / 4,
            reinterpret_cast<unsigned int*>(block_mask_.data)
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

                invoke_raycasting(
                    batch, offset,
                    size_x, size_y, size_z,
                    rays,
                    world,
                    block_mask,
                    result,
                    result_depth,
                    state
                );
            }
        }
    };
}}