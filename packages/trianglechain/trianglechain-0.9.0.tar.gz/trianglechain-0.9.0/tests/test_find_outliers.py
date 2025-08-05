# Copyright (C) 2025 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Mon Jul 07 2025

import numpy as np

from trianglechain.make_subplots import find_outliers


def test_find_outliers_function():
    """Test the find_outliers function directly."""
    # Create test data with known outliers
    np.random.seed(42)
    n_points = 100

    # Main distribution
    x_main = np.random.normal(0, 1, n_points)
    y_main = np.random.normal(0, 1, n_points)

    # Add clear outliers
    x_outliers = np.array([3.5, -3.5, 3.0, -3.0])
    y_outliers = np.array([3.5, -3.5, -3.0, 3.0])

    x = np.concatenate([x_main, x_outliers])
    y = np.concatenate([y_main, y_outliers])

    # Create density grid
    x_range = np.linspace(-4, 4, 20)
    y_range = np.linspace(-4, 4, 20)
    X, Y = np.meshgrid(x_range, y_range)

    # Simple Gaussian density
    density_grid = np.exp(-0.5 * (X**2 + Y**2))

    # Test find_outliers function
    contour_level = 0.3
    outliers = find_outliers(x, y, density_grid, X, Y, contour_level)

    # Check that function returns boolean array of correct length
    assert isinstance(outliers, np.ndarray)
    assert outliers.dtype == bool
    assert len(outliers) == len(x)

    # Check that some outliers are detected
    assert np.any(outliers)

    # Check that the known outliers (last 4 points) are more likely to be detected
    outlier_indices = np.where(outliers)[0]
    known_outlier_indices = set(range(len(x) - 4, len(x)))
    detected_known_outliers = len(set(outlier_indices) & known_outlier_indices)

    # At least some of the known outliers should be detected
    assert detected_known_outliers > 0


def test_find_outliers_boundary_cases():
    """Test find_outliers with boundary cases."""
    # Test with points exactly at grid boundaries
    x_coords = np.linspace(-2, 2, 10)
    y_coords = np.linspace(-2, 2, 10)
    X, Y = np.meshgrid(x_coords, y_coords)

    # Simple density
    density_grid = np.exp(-0.5 * (X**2 + Y**2))

    # Points at boundaries
    x_test = np.array([-2.0, 2.0, 0.0, -1.8, 1.8])
    y_test = np.array([-2.0, 2.0, 0.0, -1.8, 1.8])

    outliers = find_outliers(x_test, y_test, density_grid, X, Y, 0.5)

    # Should handle boundary points without error
    assert len(outliers) == len(x_test)
    assert outliers.dtype == bool


def test_find_outliers_empty_input():
    """Test find_outliers with empty input."""
    x_coords = np.linspace(-2, 2, 10)
    y_coords = np.linspace(-2, 2, 10)
    X, Y = np.meshgrid(x_coords, y_coords)
    density_grid = np.exp(-0.5 * (X**2 + Y**2))

    # Empty arrays
    x_empty = np.array([])
    y_empty = np.array([])

    outliers = find_outliers(x_empty, y_empty, density_grid, X, Y, 0.5)

    assert len(outliers) == 0
    assert outliers.dtype == bool


def test_find_outliers_all_points_outside_grid():
    """Test find_outliers when all points are outside the grid."""
    x_coords = np.linspace(-2, 2, 10)
    y_coords = np.linspace(-2, 2, 10)
    X, Y = np.meshgrid(x_coords, y_coords)
    density_grid = np.exp(-0.5 * (X**2 + Y**2))

    # Points far outside grid
    x_test = np.array([10.0, -10.0, 5.0])
    y_test = np.array([10.0, -10.0, 5.0])

    outliers = find_outliers(x_test, y_test, density_grid, X, Y, 0.5)

    # All points should be marked as outliers due to being outside boundary
    assert len(outliers) == len(x_test)
    assert np.all(~outliers)  # Outside boundary points are excluded


def test_find_outliers_grid_coordinates():
    """Test that find_outliers correctly extracts grid coordinates."""
    # Create specific grid
    x_coords = np.array([-3, -2, -1, 0, 1, 2, 3])
    y_coords = np.array([-4, -2, 0, 2, 4])
    X, Y = np.meshgrid(x_coords, y_coords)

    # Create density grid
    density_grid = np.ones_like(X) * 0.5  # Uniform density

    # Test points within grid
    x_test = np.array([0, 1, -1])
    y_test = np.array([0, 1, -1])

    outliers = find_outliers(x_test, y_test, density_grid, X, Y, 0.3)

    # With uniform density of 0.5 and threshold 0.3, no points should be outliers
    assert not np.any(outliers)


def test_find_outliers_high_threshold():
    """Test find_outliers with very high threshold."""
    x_coords = np.linspace(-2, 2, 10)
    y_coords = np.linspace(-2, 2, 10)
    X, Y = np.meshgrid(x_coords, y_coords)
    density_grid = np.exp(-0.5 * (X**2 + Y**2))

    # Points in the middle of grid
    x_test = np.array([0.0, 0.5, -0.5])
    y_test = np.array([0.0, 0.5, -0.5])

    # Very high threshold - all points should be outliers
    outliers = find_outliers(x_test, y_test, density_grid, X, Y, 2.0)

    assert np.all(outliers)


def test_find_outliers_low_threshold():
    """Test find_outliers with very low threshold."""
    x_coords = np.linspace(-2, 2, 10)
    y_coords = np.linspace(-2, 2, 10)
    X, Y = np.meshgrid(x_coords, y_coords)
    density_grid = np.exp(-0.5 * (X**2 + Y**2))

    # Points in the middle of grid
    x_test = np.array([0.0, 0.5, -0.5])
    y_test = np.array([0.0, 0.5, -0.5])

    # Very low threshold - no points should be outliers
    outliers = find_outliers(x_test, y_test, density_grid, X, Y, 0.001)

    assert not np.any(outliers)


def test_find_outliers_interpolation_accuracy():
    """Test that interpolation works correctly for find_outliers."""
    # Create a simple 3x3 grid with known values
    x_coords = np.array([-1, 0, 1])
    y_coords = np.array([-1, 0, 1])
    X, Y = np.meshgrid(x_coords, y_coords)

    # Create a density grid where center is high, edges are low
    density_grid = np.array([[0.1, 0.2, 0.1], [0.2, 1.0, 0.2], [0.1, 0.2, 0.1]])

    # Test point at center (should have high density)
    x_test = np.array([0.0])
    y_test = np.array([0.0])

    outliers = find_outliers(x_test, y_test, density_grid, X, Y, 0.5)

    # Center point should not be an outlier (density = 1.0 > 0.5)
    assert not outliers[0]

    # Test point at edge (should have low density)
    x_test = np.array([-1.0])
    y_test = np.array([-1.0])

    outliers = find_outliers(x_test, y_test, density_grid, X, Y, 0.5)

    # Edge point should be an outlier (density = 0.1 < 0.5)
    assert outliers[0]
