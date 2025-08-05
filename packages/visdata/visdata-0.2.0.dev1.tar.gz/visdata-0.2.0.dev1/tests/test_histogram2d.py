import numpy as np
from numpy.testing import assert_allclose
from matplotlib import pyplot as plt

from visdata import Histogram2d, Profile2d


def create_fixed_hist2d_data(range_pos=None):
    """Create some test data x, y for a 2d histogram."""
    if range_pos is True:
        x = np.linspace(1, 100, 200)
    else:
        x = np.linspace(-100, 100, 200)
    y = x**2
    displace = (5, 55, 75)
    for i in displace:
        y[i] += i * 500
    for i in range(140, 180):
        x = np.append(x, [i])
        y = np.append(y, [i**2])
    # x = np.append(x, [0] * 40)
    # y = np.append(y, [0] * 40)
    x = np.append(x, [220] * 2)
    y = np.append(y, [500, 10000])

    return x, y


def test_histogram2d_runs_without_error():
    bins = 20
    x, y = create_fixed_hist2d_data()
    hist = Histogram2d(x, y, bins=bins)

    result = hist.plot(marginal=True, profile=True, cmap="cividis_r", cmin=1)

    assert "fig" in result
    assert result["fig"] is not None
    assert hasattr(result["ax_hist2d"], "hist2d")
    assert "ax_cbar" in result
    assert hasattr(result["ax_marginal_x"], "hist")
    assert "hist_marginal_x" in result
    assert hasattr(result["ax_marginal_y"], "hist")
    assert "hist_marginal_y" in result
    assert isinstance(result["profile2d"], Profile2d)


def test_profile2d():
    bins = 10
    rtol = 1e-10  # or 1e-12?
    atol = 1e-10  # or 1e-12?

    x, y = create_fixed_hist2d_data()
    profile2d = Profile2d(x, y, bins=bins)
    expected_means = np.array(
        [
            7291.326686826091,
            3676.728097144012,
            1662.0141379005581,
            231.55980909572966,
            2041.615110729526,
            5920.305042801947,
            9314.158733365315,
            21777.5,
            28104.166666666668,
            5250.0,
        ],
        dtype=np.float64,
    )
    expected_medians = np.array(
        [
            7127.345269058862,
            2837.554607206889,
            404.28272013333014,
            145.7033913285016,
            1955.7586929622973,
            5834.448625034718,
            9309.108355849596,
            21756.5,
            28056.5,
            5250.0,
        ],
        dtype=np.float64,
    )
    expected_sems = np.array(
        [
            307.5552176245761,
            850.7389807136366,
            1177.6048031602645,
            42.50726075099274,
            148.0475765800593,
            254.97755089943965,
            167.96131247177476,
            351.1541209592544,
            483.612993805768,
            4750.0,
        ],
        dtype=np.float64,
    )
    expected_stds = np.array(
        [
            1739.7950397731372,
            4812.506418258751,
            6661.53873497978,
            240.457378613534,
            837.4835627039572,
            1442.370842330655,
            475.06633210313834,
            1404.6164838370175,
            2369.2101356077865,
            6717.514421272202,
        ],
        dtype=np.float64,
    )

    assert_allclose(profile2d.bin_means, expected_means, rtol=rtol, atol=atol)
    assert_allclose(profile2d.bin_medians, expected_medians, rtol=rtol, atol=atol)
    assert_allclose(profile2d.bin_sems, expected_sems, rtol=rtol, atol=atol)
    assert_allclose(profile2d.bin_stds, expected_stds, rtol=rtol, atol=atol)
