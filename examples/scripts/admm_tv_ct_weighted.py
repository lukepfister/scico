#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the SCICO package. Details of the copyright
# and user license can be found in the 'LICENSE.txt' file distributed
# with the package.

r"""
Low-Dose CT (ADMM w/ Total Variation)
=====================================

This example demonstrates the use of class [admm.ADMM](../_autosummary/scico.admm.rst#scico.admm.ADMM) to solve a low-dose CT reconstruction problem with anisotropic total variation (TV) regularization.

  $$\mathrm{argmin}_{\mathbf{x}} \; (1/2) \| \mathbf{y} - A \mathbf{x} \|_W^2 + \lambda \| C \mathbf{x} \|_1 \;,$$

where $A$ is the Radon transform, $\mathbf{y}$ is the sinogram, $C$ is a 2D Finite Difference operator, and $\mathbf{x}$ is the desired image.

The weighted norm is an approximation to the Poisson negative log likelihood; see :cite:`sauer-1993-local`.
"""

import numpy as np

import jax

from xdesign import Soil, discrete_phantom

import scico.numpy as snp
from scico import functional, linop, loss, metric, plot
from scico.admm import ADMM, LinearSubproblemSolver
from scico.linop.radon import ParallelBeamProjector

"""
Create a ground truth image.
"""
N = 512  # Phantom size

np.random.seed(0)
x_gt = discrete_phantom(Soil(porosity=0.80), size=384)
x_gt = np.ascontiguousarray(np.pad(x_gt, (64, 64)))
x_gt = np.clip(x_gt, 0, np.inf)  # Clip to positive values
x_gt = jax.device_put(x_gt)  # Convert to jax type, push to GPU

"""
Configure CT projection operator and generate synthetic measurements.
"""
n_projection = 360  # Number of projections
Io = 1e3  # Source flux
alpha = 1e-2  # Attenuation coefficient

angles = np.linspace(0, 2 * np.pi, n_projection)  # Evenly spaced projection angles
A = ParallelBeamProjector(x_gt.shape, 1.0, N, angles)  # Radon transform operator
y_c = A @ x_gt  # Sinogram

"""
Add Poisson noise to projections according to

$$\mathrm{counts} \sim \mathrm{Poi}\left(I_0 exp\left\{- \alpha A \mathbf{x} \right\}\right)$$

$$\mathbf{y} = - \frac{1}{\alpha} \log\left(\mathrm{counts} / I_0\right).$$

We use the NumPy random functionality so we can generate using 64-bit numbers.

"""
counts = np.random.poisson(Io * snp.exp(-alpha * A @ x_gt))
counts = np.clip(counts, a_min=1, a_max=np.inf)  # Replace any 0s count with 1
y = -1 / alpha * np.log(counts / Io)
y = jax.device_put(y)  # Converts back to float32

"""
Setup post processing.
For this example, we clip all reconstructions to the range of the ground truth.
"""


def postprocess(x):
    return snp.clip(x, 0, snp.max(x_gt))


"""
Compute an FBP reconstruction as an initial guess.
"""
x0 = postprocess(A.fbp(y))

"""
Set up and solve the un-weighted reconstruction problem

  $$\mathrm{argmin}_{\mathbf{x}} \; (1/2) \| \mathbf{y} - A \mathbf{x} \|_2^2 + \lambda \| C \mathbf{x} \|_1.$$

"""
rho = 2.5e3  # ADMM penalty parameter
lambda_unweighted = 2.56e2  # regularization strength
# rho and lambda were selected via a parameter sweep (not shown here)

maxiter = 50  # Number of ADMM iterations
max_inner_iter = 10  # Number of CG iterations per ADMM iteration

f = loss.SquaredL2Loss(y=y, A=A)

admm_unweighted = ADMM(
    f=f,
    g_list=[lambda_unweighted * functional.L1Norm()],
    C_list=[linop.FiniteDifference(x_gt.shape)],
    rho_list=[rho],
    x0=x0,
    maxiter=maxiter,
    subproblem_solver=LinearSubproblemSolver(cg_kwargs={"maxiter": max_inner_iter}),
    verbose=True,
)
admm_unweighted.solve()
x_unweighted = postprocess(admm_unweighted.x)


"""
Set up and solve the weighted reconstruction problem

  $$\mathrm{argmin}_{\mathbf{x}} \; (1/2) \| \mathbf{y} - A \mathbf{x} \|_W^2 + \lambda \| C \mathbf{x} \|_1 \;,$$

where

  $$W = \mathrm{diag}\left\{\exp( \sqrt{\mathbf{y}}) \right\}.$$

"""
lambda_weighted = 1.14e2

weights = counts / Io  # scale by Io to balance the data vs regularization term
W = linop.Diagonal(snp.sqrt(weights))
f = loss.WeightedSquaredL2Loss(y=y, A=A, weight_op=W)

admm_weighted = ADMM(
    f=f,
    g_list=[lambda_weighted * functional.L1Norm()],
    C_list=[linop.FiniteDifference(x_gt.shape)],
    rho_list=[rho],
    maxiter=maxiter,
    x0=x0,
    subproblem_solver=LinearSubproblemSolver(cg_kwargs={"maxiter": max_inner_iter}),
    verbose=True,
)
admm_weighted.solve()
x_weighted = postprocess(admm_weighted.x)

"""
Show recovered images.
"""


def plot_recon(x, title, ax):
    plot.imview(
        x,
        title=f"{title}\nSNR: {metric.snr(x_gt, x):.2f} (dB), MAE: {metric.mae(x_gt, x):.3f}",
        fig=fig,
        ax=ax,
    )


fig, ax = plot.subplots(nrows=2, ncols=2, figsize=(11, 10))
plot.imview(x_gt, title="Ground truth", fig=fig, ax=ax[0, 0])
plot_recon(x0, "FBP Reconstruction", ax=ax[0, 1])
plot_recon(x_unweighted, "Unweighted TV Reconstruction", ax=ax[1, 0])
plot_recon(x_weighted, "Weighted TV Reconstruction", ax=ax[1, 1])
for ax_ in ax.ravel():
    ax_.set_xlim(64, 448)
    ax_.set_ylim(64, 448)
fig.subplots_adjust(left=0.1, right=0.99, top=0.95, bottom=0.05, wspace=0.2, hspace=0.01)
fig.colorbar(
    ax[0, 0].get_images()[0], ax=ax, location="right", shrink=0.9, pad=0.05, label="arbitrary units"
)
fig.show()

input("\nWaiting for input to close figures and exit")
