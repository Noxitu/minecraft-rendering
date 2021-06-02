
auto raycast = [](auto &rays, auto &map, auto &cells)
{
    const int n = rays.shape[0];

    for (int i = 0; i < n; ++i)
    {
        auto &x = cells(i, 0);
        auto &y = cells(i, 1);

        auto inside = [&] { return y >= 0 && x >= 0 && y < map.shape[0] && x < map.shape[1]; };
        auto outside = [&] { return y < 0 || x < 0 || y >= map.shape[0] || x >= map.shape[1]; };

        const double x0 = rays(i, 0);
        const double y0 = rays(i, 1);
        const double rx_inv = 1/rays(i, 2);
        const double ry_inv = 1/rays(i, 3);

        for (int iter = 0; iter < map.shape[0]; ++iter)
        {
            double dx = std::numeric_limits<double>::infinity();
            double dy = std::numeric_limits<double>::infinity();

            if (rx_inv > 0)
                dx = (x-x0+1)*rx_inv;
            else if (rx_inv < 0)
                dx = (x-x0)*rx_inv;

            if (ry_inv > 0)
                dy = (y-y0+1)*ry_inv;
            else if (ry_inv < 0)
                dy = (y-y0)*ry_inv;

            if (dx < dy)
                x += (rx_inv > 0 ? 1 : -1);
            else
                y += (ry_inv > 0 ? 1 : -1);

            if (inside())
                map(y, x) = 255;
        }
    }
};
