#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the SCICO package. Details of the copyright
# and user license can be found in the 'LICENSE.txt' file distributed
# with the package.

r"""
Deconvolution Microscopy
========================

This example partially replicates a [GlobalBioIm example](https://biomedical-imaging-group.github.io/GlobalBioIm/examples.html) using the [microscopy data](http://bigwww.epfl.ch/deconvolution/bio/) provided by the EPFL Biomedical Imaging Group.

The deconvolution problem is solved using class [admm.ADMM](../_autosummary/scico.admm.rst#scico.admm.ADMM) to solve an image deconvolution problem with isotropic total variation (TV) regularization.

  $$\mathrm{argmin}_{\mathbf{x}} \; \| M (\mathbf{y} - A \mathbf{x}) \|_2^2 + \lambda \| C \mathbf{x} \|_{2,1} + \iota_{\mathrm{NN}}(\mathbf{x}) \;,$$

where $M$ is a mask operator, $A$ is circular convolution, $\mathbf{y}$ is the blurred image, $C$ is a convolutional gradient operator, $\iota_{mathrm{NN}}$ is the indicator function of the non-negativity constraint, and $\mathbf{x}$ is the desired image.
"""


import glob
import os
import tempfile
import zipfile

import numpy as np

import imageio

import scico.numpy as snp
from scico import functional, linop, loss, plot, util
from scico.admm import ADMM, CircularConvolveSolver

"""
Define helper functions.
"""


def volread(path, ext="tif"):
    """Read a 3D volume from a set of files in the specified directory"""

    slices = []
    for file in sorted(glob.glob(os.path.join(path, "*." + ext))):
        image = imageio.imread(file)
        slices.append(image)
    return np.dstack(slices)


def block_avg(im, N):
    """
    Average distinct NxNxN blocks of im, return the resulting smaller image
    """

    im = snp.mean(snp.reshape(im, (-1, N, im.shape[1], im.shape[2])), axis=1)
    im = snp.mean(snp.reshape(im, (im.shape[0], -1, N, im.shape[2])), axis=2)
    im = snp.mean(snp.reshape(im, (im.shape[0], im.shape[1], -1, N)), axis=3)

    return im


"""
Download data or access it from cache directory.
"""
data_base_url = "http://bigwww.epfl.ch/deconvolution/bio/"
data_zip_files = ["CElegans-CY3.zip", "CElegans-DAPI.zip", "CElegans-FITC.zip"]
psf_zip_files = ["PSF-CElegans-CY3.zip", "PSF-CElegans-DAPI.zip", "PSF-CElegans-FITC.zip"]
cache_path = os.path.join(os.path.expanduser("~"), ".cache", "scico", "epfl_big")
if not os.path.isdir(cache_path):
    os.makedirs(cache_path)
    temp_dir = tempfile.TemporaryDirectory()
    for zip_file in data_zip_files + psf_zip_files:
        data = util.url_get(data_base_url + zip_file)
        f = open(os.path.join(temp_dir.name, zip_file), "wb")
        f.write(data.read())
        f.close()
    for zip_file in data_zip_files + psf_zip_files:
        with zipfile.ZipFile(os.path.join(temp_dir.name, zip_file), "r") as zip_ref:
            zip_ref.extractall(cache_path)

image_list = []
for zip_file in data_zip_files:
    image_list.append(volread(os.path.join(cache_path, zip_file[:-4])).astype(np.float32))
y = snp.stack(image_list)
del image_list
psf_list = []
for zip_file in psf_zip_files:
    psf_list.append(volread(os.path.join(cache_path, zip_file[:-4])).astype(np.float32))
psf = snp.stack(psf_list)
del psf_list

"""
Preprocess data. We downsample by a factor of 4 for purposes of the example.
Reducing the downsampling rate will be slower and more memory-intensive.
If your GPU does not have enough memory, you can try setting the environment
variable `JAX_PLATFORM_NAME=cpu` to run on CPU.
"""

channel = 0
downsampling_rate = 4

y = block_avg(y[channel], downsampling_rate)
psf = block_avg(psf[channel], downsampling_rate)


y -= y.min()
y /= y.max()

psf /= psf.sum()

"""
Pad data and create mask.
"""

padding = [[0, p] for p in snp.array(psf.shape) - 1]
y_pad = snp.pad(y, padding)
mask = snp.pad(snp.ones_like(y), padding)


"""
Define problem and algorithm parameters.
"""

λ = 2e-6  # L1 norm regularization parameter
ρ0 = 1e-3  # ADMM penalty parameter for first auxiiary variable
ρ1 = 1e-3  # ADMM penalty parameter for second auxiiary variable
ρ2 = 1e-3  # ADMM penalty parameter for third auxiiary variable
maxiter = 100  # Number of ADMM iterations


"""
Create operators.
"""

M = linop.Diagonal(mask)
C0 = linop.CircularConvolve(h=psf, input_shape=mask.shape, h_center=snp.array(psf.shape) / 2 - 0.5)
C1 = linop.FiniteDifference(input_shape=mask.shape, circular=True)
C2 = linop.Identity(mask.shape)


"""
Create functionals.
"""

g0 = loss.SquaredL2Loss(y=y_pad, A=M)  # Loss function (forward model)
g1 = λ * functional.L21Norm()  # TV penalty (when applied to gradient)
g2 = functional.NonNegativeIndicator()  # Non-negativity constraint


"""
Set up ADMM solver object and solve problem.
"""
##
solver = ADMM(
    f=None,
    g_list=[g0, g1, g2],
    C_list=[C0, C1, C2],
    rho_list=[ρ0, ρ1, ρ2],
    maxiter=maxiter,
    verbose=True,
    x0=y_pad,
    subproblem_solver=CircularConvolveSolver(),
)

t = util.Timer()
with util.ContextTimer(t):
    solver.solve()
solve_stats = solver.itstat_object.history(transpose=True)
x_pad = solver.x
x = x_pad[: y.shape[0], : y.shape[1], : y.shape[2]]

##

"""
Show the recovered image.
"""


def make_slices(x, sep_width=10):
    """
    Make an image with xy, xz, and yz slices from an input volume.
    """
    fill_val = -1.0
    out = snp.concatenate(
        (
            x[:, :, x.shape[2] // 2],
            snp.full((x.shape[0], sep_width), fill_val),
            x[:, x.shape[1] // 2, :],
        ),
        axis=1,
    )

    out = snp.concatenate(
        (
            out,
            snp.full((sep_width, out.shape[1]), fill_val),
            snp.concatenate(
                (
                    x[x.shape[0] // 2, :, :].T,
                    snp.full((x.shape[2], x.shape[2] + sep_width), fill_val),
                ),
                axis=1,
            ),
        ),
        axis=0,
    )

    out = snp.where(out == fill_val, out.max(), out)

    return out


fig, ax = plot.subplots(nrows=1, ncols=2, figsize=(10, 5))
plot.imview(make_slices(y), title="Blurred measurements", fig=fig, ax=ax[0])
plot.imview(make_slices(x), title="Deconvolved image", fig=fig, ax=ax[1])
fig.show()

"""
Plot convergence statistics.
"""

fig, ax = plot.subplots(nrows=1, ncols=2, figsize=(12, 5))
plot.plot(
    solve_stats.Objective,
    title="Objective function",
    xlbl="Iteration",
    ylbl="Functional value",
    fig=fig,
    ax=ax[0],
)
plot.plot(
    snp.vstack((solve_stats.Primal_Rsdl, solve_stats.Dual_Rsdl)).T,
    ptyp="semilogy",
    title="Residuals",
    xlbl="Iteration",
    lgnd=("Primal", "Dual"),
    fig=fig,
    ax=ax[1],
)
fig.show()

input("\nWaiting for input to close figures and exit")
