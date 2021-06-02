import numpy as np


def create_camera_rays(*, position, rotation, camera, resolution, offset):
    render_height, render_width = resolution

    P_inv = np.linalg.inv(camera @ rotation)
    camera_x, camera_y, camera_z = position - offset

    rays = np.array([camera_x, camera_y, camera_z, 0, 0, 1], dtype=float)
    rays = rays.reshape(1, 1, 6) + np.zeros((render_height, render_width, 1))
    rays[..., 3] += np.linspace(-1, 1, render_width).reshape(1, -1)
    rays[..., 4] += np.linspace(-1, 1, render_height).reshape(-1, 1)
    
    rays[..., 3:] = np.einsum('rc,nmc->nmr', P_inv, rays[..., 3:])
    rays[..., 3:] /= np.linalg.norm(rays[..., 3:], axis=2)[..., np.newaxis]

    return rays


def compute_shadow_rays(rays, depths, sunlight):
    rays = rays.copy()
    rays[..., :3] = rays[..., :3] + rays[..., 3:] * (depths - 0.05)[..., np.newaxis]
    rays[..., 3:] = sunlight
    rays[..., 3:] /= np.linalg.norm(rays[..., 3:], axis=-1)[..., np.newaxis]
    return rays


def compute_diffuse_factors(normals, sunlight, *, indices=None):
    diffuse_factors = np.einsum('ni,i->n', normals, sunlight)
    diffuse_factors[diffuse_factors < 0] = 0

    if indices is not None:
        diffuse_factors = diffuse_factors[indices]

    return diffuse_factors