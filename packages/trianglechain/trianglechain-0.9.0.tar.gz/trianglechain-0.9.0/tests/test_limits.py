# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import numpy as np
import pytest

from trianglechain.limits import (
    PJ_HPD,
    get_levels,
    get_one_tailed_levels,
    get_uncertainty_band,
    hdi,
    percentile,
    sigma_to_cdf,
    uncertainty,
)

np.random.seed(0)


def test_percentile():
    samples = np.random.normal(0, 1, 1000)
    lower, upper = percentile(samples, credible_interval=0.68)
    assert lower < 0
    assert upper > 0


def test_uncertainty():
    samples = np.random.normal(0, 1, 1000)
    unc = uncertainty(samples, model=percentile, credible_interval=0.68)
    assert unc > 0


def test_hdi():
    samples = np.random.normal(0, 1, 1000)
    lower, upper = hdi(samples, credible_interval=0.68)
    assert lower < 0
    assert upper > 0


def test_PJ_HPD():
    samples = np.random.uniform(-10, 10, 1000)
    lnprobs = samples**2
    lower, upper = PJ_HPD(samples, lnprobs, credible_interval=0.68)
    assert lower < 0
    assert upper > 0

    lower, upper = PJ_HPD(samples, lnprobs, credible_interval=0.95)
    assert lower < 0
    assert upper > 0


def test_PJ_HPD_which_changed_cases():
    # Create a sample distribution where we have clear outliers on both sides
    # to trigger both which_changed == 1 and which_changed == 2

    # Create samples with a clear distribution and some outliers
    np.random.seed(42)  # Fixed seed for reproducible test

    # Main distribution centered around 0
    main_samples = np.random.normal(0, 1, 800)

    # Add outliers on the left side (should trigger which_changed == 1)
    left_outliers = np.random.uniform(-6, -4, 50)

    # Add outliers on the right side (should trigger which_changed == 2)
    right_outliers = np.random.uniform(4, 6, 50)

    # Combine all samples
    samples = np.concatenate([left_outliers, main_samples, right_outliers])

    # Create corresponding log probabilities (higher for main distribution)
    lnprobs = np.concatenate(
        [
            np.full(len(left_outliers), -5.0),  # Low probability for left outliers
            np.random.normal(-1, 0.5, len(main_samples)),  # High probability for main
            np.full(len(right_outliers), -5.0),  # Low probability for right outliers
        ]
    )

    # Test different credible intervals to increase chance of hitting both branches
    for ci in [0.5, 0.68, 0.9]:
        lower, upper = PJ_HPD(samples, lnprobs, credible_interval=ci)
        assert lower < upper
        assert lower < 0
        assert upper > 0


def test_get_levels():
    samples = np.random.normal(0, 1, 1000)
    (lower, upper), _, _ = get_levels(
        samples, levels_method="hdi", credible_interval=0.68
    )
    assert lower < 0
    assert upper > 0
    (lower, upper), _, _ = get_levels(
        samples, levels_method="percentile", credible_interval=0.68
    )
    assert lower < 0
    assert upper > 0
    lnprobs = np.random.uniform(0, 1, 1000)
    (lower, upper), _, _ = get_levels(
        samples, lnprob=lnprobs, levels_method="PJ_HPD", credible_interval=0.68
    )
    assert lower < 0
    assert upper > 0


def test_get_uncertainty_band():
    lower = 0
    upper = 1
    unc = get_uncertainty_band(lower, upper)
    assert unc == 0.5


def test_one_sided_tail():
    samples = np.random.normal(0, 1, 100000)
    _, two_tail, _ = get_levels(samples, levels_method="hdi", credible_interval=0.68)
    assert two_tail

    samp = samples[samples < 0]
    _, two_tail, _ = get_levels(samp, levels_method="hdi", credible_interval=0.68)
    assert not two_tail

    samp = samples[samples > 0]
    _, two_tail, _ = get_levels(samp, levels_method="hdi", credible_interval=0.68)
    assert not two_tail


def test_errors():
    with pytest.raises(ValueError):
        sigma_to_cdf(0.68, side="middle")

    with pytest.raises(ValueError):
        get_one_tailed_levels(np.random.rand(100), side="middle")

    samples = np.random.normal(0, 1, 100000)
    (lower, upper), _, _ = get_levels(samples)

    # PJ_HPD without lnprob
    (lower_test, upper_test), _, _ = get_levels(samples, levels_method="PJ_HPD")
    assert lower_test == lower
    assert upper_test == upper

    # Unknown levels_method
    (lower_test, upper_test), _, _ = get_levels(samples, levels_method="by_eye")
    assert lower_test == lower
    assert upper_test == upper
