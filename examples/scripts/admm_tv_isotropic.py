#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the SCICO package. Details of the copyright
# and user license can be found in the 'LICENSE.txt' file distributed
# with the package.

r"""
Isotropic Total Variation
=========================

This example demonstrates isotropic total variation (TV) regularization.
It solves the denosing problem

  $$\mathrm{argmin}_{\mathbf{x}} \; (1/2) \| \mathbf{y} - \mathbf{x} \|^2 + \lambda R(\mathbf{x}) \;,$$

where $R$ is the isotropic TV: the sum of the norms of the gradient vectors at each point in the image $\mathbf{x}$.
The same reconstruction is performed with anisotropic TV regularization for comparison;
the isotropic version shows fewer block-like artifacts.

In SCICO, switching between these two regularizers is a one-line change:
replacing an [L1Norm](../_autosummary/scico.functional.rst#scico.functional.L1Norm) with a [L21Norm](../_autosummary/scico.functional.rst#scico.functional.L21Norm).

"""

import jax
import jax.numpy as jnp
import jax.scipy as jsp

from scico import functional, linop, loss, plot
from scico.admm import ADMM, LinearSubproblemSolver

"""
Create a ground truth image.
"""
N = 256  # Image size

# these steps create a ground truth image by spatially filtering noise
kernel_size = N // 5
key = jax.random.PRNGKey(1)
x_gt = jax.random.uniform(key, shape=(N + kernel_size - 1, N + kernel_size - 1))
x = jnp.linspace(-3, 3, kernel_size)
window = jsp.stats.norm.pdf(x) * jsp.stats.norm.pdf(x[:, None])
window = window / window.sum()
x_gt = jsp.signal.convolve(x_gt, window, mode="valid")
x_gt = (x_gt > jnp.percentile(x_gt, 25)).astype(float) + (x_gt > jnp.percentile(x_gt, 75)).astype(
    float
)
x_gt = x_gt / x_gt.max()

"""
Add noise to create a noisy test image.
"""
sigma = 1.0  # noise standard deviation
key, subkey = jax.random.split(key)

n = sigma * jax.random.normal(subkey, shape=x_gt.shape)

y = x_gt + n

"""
Denoise with isotropic total variation
"""
reg_weight_iso = 2e0
f = loss.SquaredL2Loss(y=y)
g_iso = reg_weight_iso * functional.L21Norm()

# the append=0 option makes the results of horizontal and vertical finite differences
# the same shape, which is required for the L21Norm
C = linop.FiniteDifference(input_shape=x_gt.shape, append=0)
solver = ADMM(
    f=f,
    g_list=[g_iso],
    C_list=[C],
    rho_list=[1e1],
    x0=y,
    maxiter=100,
    subproblem_solver=LinearSubproblemSolver(cg_kwargs={"maxiter": 20}),
    verbose=True,
)

solver.solve()

x_iso = solver.x

"""
Denoise with anisotropic total variation for comparison.
"""
# we tune the weight to give the same data fidelty as the isotropic case
reg_weight_aniso = 1.74e0
g_aniso = reg_weight_aniso * functional.L1Norm()

solver = ADMM(
    f=f,
    g_list=[g_aniso],
    C_list=[C],
    rho_list=[1e1],
    x0=y,
    maxiter=100,
    subproblem_solver=LinearSubproblemSolver(cg_kwargs={"maxiter": 20}),
    verbose=True,
)

solver.solve()

x_aniso = solver.x

"""
Compute the data fidelity.
"""
for x, name in zip((x_iso, x_aniso), ("isotropic", "anisotropic")):
    df = f(x)
    print(f"data fidelity for {name} TV was {df:.2e}")

"""
Plot results.
"""
plt_args = dict(norm=plot.matplotlib.colors.Normalize(vmin=0, vmax=1.5))
fig, ax = plot.subplots(nrows=2, ncols=2, sharex=True, sharey=True, figsize=(11, 10))
plot.imview(x_gt, title="Ground truth", fig=fig, ax=ax[0, 0], **plt_args)
plot.imview(y, title="Noisy version", fig=fig, ax=ax[0, 1], **plt_args)
plot.imview(x_iso, title="Isotropic TV denoising", fig=fig, ax=ax[1, 0], **plt_args)
plot.imview(x_aniso, title="Anisotropic TV denoising", fig=fig, ax=ax[1, 1], **plt_args)
fig.subplots_adjust(left=0.1, right=0.99, top=0.95, bottom=0.05, wspace=0.2, hspace=0.01)
fig.colorbar(
    ax[0, 0].get_images()[0], ax=ax, location="right", shrink=0.9, pad=0.05, label="arbitrary units"
)
fig.suptitle("denoising comparison")
fig.show()

# zoomed version
fig, ax = plot.subplots(nrows=2, ncols=2, sharex=True, sharey=True, figsize=(11, 10))
plot.imview(x_gt, title="Ground truth", fig=fig, ax=ax[0, 0], **plt_args)
plot.imview(y, title="Noisy version", fig=fig, ax=ax[0, 1], **plt_args)
plot.imview(x_iso, title="Isotropic TV denoising", fig=fig, ax=ax[1, 0], **plt_args)
plot.imview(x_aniso, title="Anisotropic TV denoising", fig=fig, ax=ax[1, 1], **plt_args)
ax[0, 0].set_xlim(N // 4, N // 4 + N // 2)
ax[0, 0].set_ylim(N // 4, N // 4 + N // 2)
fig.subplots_adjust(left=0.1, right=0.99, top=0.95, bottom=0.05, wspace=0.2, hspace=0.01)
fig.colorbar(
    ax[0, 0].get_images()[0], ax=ax, location="right", shrink=0.9, pad=0.05, label="arbitrary units"
)
fig.suptitle("denoising comparison (zoomed)")
fig.show()

input("\nWaiting for input to close figures and exit")
