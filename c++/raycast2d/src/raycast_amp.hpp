#include <amp.h>

auto raycast = [](auto &rays, auto &map, auto &cells)
{
    namespace amp = concurrency;
    const int n = rays.shape[0];
    const int width = map.shape[1];
    const int height = map.shape[0];
    const int total_steps = height * 10;
    const int executions = 200;
    const int steps = total_steps / executions;

    for (int outer_iter = 0; outer_iter < executions; ++outer_iter)
    {
        amp::array_view<const double, 2> rays_view(n, 4, rays.data);
        amp::array_view<int, 2> map_view(height, width, map.data);
        amp::array_view<int, 2> cells_view(n, 2, cells.data);

        if (outer_iter == 0)
            map_view.discard_data();

        amp::parallel_for_each(
            amp::extent<1>(n),
            [=](amp::index<1> idx) restrict(amp) {
                const int i = idx[0];
                auto &x = cells_view(i, 0);
                auto &y = cells_view(i, 1);

                const double x0 = rays_view(i, 0);
                const double y0 = rays_view(i, 1);
                const double rx_inv = 1/rays_view(i, 2);
                const double ry_inv = 1/rays_view(i, 3);

                for (int iter = 0; iter < steps; ++iter)
                {
                    double dx = INFINITY;
                    double dy = INFINITY;

                    if (rx_inv > 0)
                        dx = (x-x0+1)*rx_inv;
                    else if (rx_inv < 0)
                        dx = (x-x0)*rx_inv;

                    if (ry_inv > 0)
                        dy = (y-y0+1)*ry_inv;
                    else if (ry_inv < 0)
                        dy = (y-y0)*ry_inv;

                    // if (dx > 25000 && dy > 25000)
                    //     break;

                    if (dx < dy)
                        x += (rx_inv > 0 ? 1 : -1);
                    else
                        y += (ry_inv > 0 ? 1 : -1);

                    const bool inside = y >= 0 && x >= 0 && y < height && x < width;

                    if (inside)
                        map_view(y, x) = 255;
                }
            }
        );
    }
};
