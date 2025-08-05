# Copyright (C) 2023 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import matplotlib.pyplot as plt
import numpy as np
import pytest

from trianglechain import LineChain
from trianglechain.params import get_samples


def test_basic_plots():
    samples1 = get_samples()
    samples2 = get_samples()
    prob = np.random.uniform(size=(len(samples1)))

    line = LineChain()
    line.contour_cl(samples1, color="r", label="test")
    line.contour_cl(samples2, color="b", label="test2", show_legend=True)

    line = LineChain()
    line.density_image(samples1)

    line = LineChain()
    line.scatter(samples1)

    line = LineChain()
    line.scatter_prob(samples1, prob=prob, colorbar=True)

    line = LineChain()
    line.scatter_density(samples1)
    plt.close("all")


def test_errors():
    samples = get_samples()
    with pytest.raises(ValueError):
        line = LineChain()
        line.scatter_prob(samples)


def test_scatter_probs():
    samples = get_samples()
    line = LineChain()

    prob = np.random.uniform(size=(len(samples))) - 1
    line.scatter_prob(samples, prob=prob, normalize_prob2D=True)
    line.scatter_prob(
        samples,
        prob=prob,
        normalize_prob2D=False,
        colorbar=True,
        cmap_vmin=0.1,
        cmap_vmax=0.9,
    )
    plt.close("all")


def test_orientation():
    samples = get_samples()
    line = LineChain(size=(1, 1), orientation="vertical")
    line.contour_cl(samples, color="r")
    x, y = line.fig.get_size_inches()
    assert x < y
    line = LineChain(size=(1, 1), orientation="horizontal")
    line.contour_cl(samples, color="r")
    x, y = line.fig.get_size_inches()
    assert x > y
    plt.close("all")


def test_n_points_scatter():
    samples = get_samples(10000)
    prob = np.ones(len(samples))
    line = LineChain()
    line.scatter(samples, n_points_scatter=10)
    line.scatter_density(samples, n_points_scatter=10)
    line.scatter_prob(samples, prob=prob, n_points_scatter=10)
    plt.close("all")


def test_alpha():
    samples = get_samples()
    line = LineChain()
    line.scatter(samples, alpha=0.5)
    line.scatter_density(samples, alpha2D=0.5)
    line.contour_cl(samples, alpha=0.5, alpha2D=0.5)
    plt.close("all")


def test_axlines():
    samples = get_samples()
    line = LineChain()
    line.contour_cl(samples)
    line.axlines(samples[0])
    line.axlines(samples[1])

    with pytest.raises(ValueError):
        line.axlines(samples)

    plt.close("all")


def test_grid():
    samples = get_samples(
        n_dims=4,
    )
    rect = LineChain(grid=True)
    rect.contour_cl(samples)
    plt.close("all")


def test_colorbar_ax():
    line = LineChain(orientation="vertical")
    assert line.kwargs["colorbar_ax"] == [0.93, 0.1, 0.03, 0.3]
    line = LineChain(orientation="horizontal")
    assert line.kwargs["colorbar_ax"] == [0.93, 0.1, 0.03, 0.8]
    line = LineChain(orientation="horizontal", colorbar_ax=[0.1, 0.1, 0.1, 0.1])
    assert line.kwargs["colorbar_ax"] == [0.1, 0.1, 0.1, 0.1]


def test_orientation_error():
    with pytest.raises(ValueError):
        LineChain(orientation="diagonal").contour_cl(get_samples())


def test_scatter_outliers():
    """Test scatter_outliers functionality in LineChain."""
    # Use a larger sample to ensure we have natural outliers
    samples = get_samples(n_samples=5000, n_dims=3)

    # Test with LineChain horizontal (should identify natural outliers outside 95th percentile)
    line = LineChain(density_estimation_method="smoothing")
    line.contour_cl(samples, color="teal", scatter_outliers=True)

    # Test with vertical orientation
    line_vert = LineChain(orientation="vertical", density_estimation_method="smoothing")
    line_vert.contour_cl(samples, color="maroon", scatter_outliers=True)

    # Test with custom outlier kwargs
    outlier_kwargs = {"s": 25, "marker": "D"}
    line.contour_cl(
        samples,
        color="navy",
        scatter_outliers=True,
        outlier_scatter_kwargs=outlier_kwargs,
    )

    plt.close("all")


def test_scatter_outliers_no_outliers():
    """Test scatter_outliers when no outliers are detected in LineChain."""
    # Use tightly distributed samples where outliers are unlikely
    np.random.seed(42)
    samples = get_samples(n_dims=3)

    # Use a very low contour level so most points are inside
    line = LineChain(
        density_estimation_method="smoothing",
        de_kwargs={"levels": [0.01]},  # Very low threshold
    )
    line.contour_cl(samples, color="blue", scatter_outliers=True)

    plt.close("all")


def test_scatter_outliers_different_methods():
    """Test scatter_outliers with different density estimation methods in LineChain."""
    # Use a larger sample to ensure we have natural outliers
    samples = get_samples(n_samples=5000, n_dims=3)

    # Test with different density estimation methods (should identify natural outliers)
    for method in ["smoothing", "hist"]:
        line = LineChain(density_estimation_method=method)
        line.contour_cl(samples, color="blue", scatter_outliers=True)

    plt.close("all")
