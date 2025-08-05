# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Wed Jan 31 2024

import matplotlib.pyplot as plt
import numpy as np
import pytest

from trianglechain import RectangleChain
from trianglechain.params import get_samples


def test_basic_plots():
    samples1 = get_samples(n_dims=4, names=["a", "b", "c", "d"])
    samples2 = get_samples(n_dims=4, names=["a", "b", "c", "d"])
    prob = np.random.uniform(size=(len(samples1)))

    rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"])
    rect.contour_cl(samples1, color="r", label="test")
    rect.contour_cl(samples2, color="b", label="test2", show_legend=True)

    rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"])
    rect.density_image(samples1)

    rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"])
    rect.scatter(samples1)

    rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"])
    rect.scatter_prob(samples1, prob=prob, colorbar=True)

    rect = RectangleChain(size=(2, 3), params_x=["a", "b"], params_y=["c", "d"])
    rect.scatter_density(samples1)
    plt.close("all")


def test_errors():
    samples = get_samples(n_dims=4, names=["a", "b", "c", "d"])
    with pytest.raises(ValueError):
        rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"])
        rect.scatter_prob(samples)


def test_scatter_probs():
    samples = get_samples(n_dims=4, names=["a", "b", "c", "d"])
    rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"])

    prob = np.random.uniform(size=(len(samples))) - 1
    rect.scatter_prob(samples, prob=prob, normalize_prob2D=True)
    rect.scatter_prob(
        samples,
        prob=prob,
        normalize_prob2D=False,
        colorbar=True,
        cmap_vmin=0.1,
        cmap_vmax=0.9,
    )
    plt.close("all")


def test_n_points_scatter():
    samples = get_samples(n_dims=4, names=["a", "b", "c", "d"])
    rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"])
    rect.scatter(samples, n_points_scatter=10)
    plt.close("all")


def test_alpha():
    samples = get_samples(n_dims=4, names=["a", "b", "c", "d"])
    rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"])
    rect.scatter(samples, alpha=0.5)
    rect.scatter_density(samples, alpha2D=0.5)
    rect.contour_cl(samples, alpha=0.5, alpha2D=0.5)
    plt.close("all")


def test_axlines():
    samples = get_samples(n_dims=4, names=["a", "b", "c", "d"])
    rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"])
    rect.contour_cl(samples)
    rect.axlines(samples[0])
    rect.axlines(samples[1])

    with pytest.raises(ValueError):
        rect.axlines(samples)

    plt.close("all")


def test_grid():
    samples = get_samples(n_dims=4, names=["a", "b", "c", "d"])
    rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"], grid=True)
    rect.contour_cl(samples)
    plt.close("all")


def test_colorbar_ax():
    rect = RectangleChain(params_x=["a", "b"], params_y=["c", "d"])
    assert rect.kwargs["colorbar_ax"] == [0.93, 0.1, 0.03, 0.8]

    rect = RectangleChain(
        params_x=["a", "b"],
        params_y=["c", "d"],
        colorbar_ax=[0.9, 0.1, 0.05, 0.8],
    )
    assert rect.kwargs["colorbar_ax"] == [0.9, 0.1, 0.05, 0.8]


def test_scatter_outliers():
    """Test scatter_outliers functionality in RectangleChain."""
    # Use a larger sample to ensure we have natural outliers
    samples = get_samples(n_samples=5000, n_dims=4, names=["a", "b", "c", "d"])

    # Test with RectangleChain (should identify natural outliers outside 95th percentile)
    rect = RectangleChain(
        params_x=["a", "b"],
        params_y=["c", "d"],
        density_estimation_method="smoothing",
    )
    rect.contour_cl(samples, color="purple", scatter_outliers=True)

    # Test with custom kwargs
    outlier_kwargs = {"s": 15, "marker": "^", "edgecolors": "black"}
    rect.contour_cl(
        samples,
        color="orange",
        scatter_outliers=True,
        outlier_scatter_kwargs=outlier_kwargs,
    )

    # Test with filled contours
    rect_filled = RectangleChain(
        params_x=["a", "b"],
        params_y=["c", "d"],
        density_estimation_method="smoothing",
        fill=True,
    )
    rect_filled.contour_cl(samples, color="green", scatter_outliers=True)

    plt.close("all")


def test_scatter_outliers_with_prob():
    """Test scatter_outliers with probability weights in RectangleChain."""
    # Use a larger sample to ensure we have natural outliers
    samples = get_samples(n_samples=5000, n_dims=4, names=["a", "b", "c", "d"])
    prob = np.random.uniform(0.5, 1.0, len(samples))
    prob = prob / np.sum(prob)  # Normalize to sum to 1

    rect = RectangleChain(
        params_x=["a", "b"],
        params_y=["c", "d"],
        density_estimation_method="smoothing",
    )
    rect.contour_cl(samples, prob=prob, color="blue", scatter_outliers=True)

    plt.close("all")
