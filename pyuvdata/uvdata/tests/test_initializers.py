"""Tests of in-memory initialization of UVData objects."""
from typing import Any

import numpy as np
import pytest
from astropy.coordinates import EarthLocation

from pyuvdata import UVData
from pyuvdata.uvdata.initializers import (
    configure_blt_rectangularity,
    get_antenna_params,
    get_baseline_params,
    get_freq_params,
    get_time_params,
)


@pytest.fixture(scope="function")
def simplest_working_params() -> dict[str, Any]:
    return {
        "freq_array": np.linspace(1e8, 2e8, 100),
        "polarization_array": ["xx", "yy"],
        "antenna_positions": {0: [0, 0, 0], 1: [0, 0, 1], 2: [0, 0, 2]},
        "telescope_location": EarthLocation.from_geodetic(0, 0, 0),
        "telescope_name": "test",
        "unique_antpairs": [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)],
        "unique_times": np.linspace(2459855, 2459856, 20),
    }


def test_simplest_new_uvdata(simplest_working_params: dict[str, Any]):
    uvd = UVData.new(**simplest_working_params)

    assert uvd.Nfreqs == 100
    assert uvd.Npols == 2
    assert uvd.Nants_data == 3
    assert uvd.Nbls == 6
    assert uvd.Ntimes == 20
    assert uvd.Nblts == 120
    assert uvd.Nspws == 1


def test_bad_inputs(simplest_working_params: dict[str, Any]):
    with pytest.raises(ValueError, match="vis_units must be one of"):
        UVData.new(**simplest_working_params, vis_units="foo")

    with pytest.raises(
        ValueError, match="Keyword argument derp is not a valid UVData attribute"
    ):
        UVData.new(**simplest_working_params, derp="foo")


def test_bad_antenna_inputs(simplest_working_params: dict[str, Any]):
    with pytest.raises(
        ValueError, match="Either antenna_numbers or antenna_names must be provided"
    ):
        badp = {
            k: v for k, v in simplest_working_params.items() if k != "antenna_positions"
        }
        UVData.new(
            antenna_positions=np.array([[0, 0, 0], [0, 0, 1], [0, 0, 2]]),
            antenna_numbers=None,
            antenna_names=None,
            **badp,
        )

    with pytest.raises(ValueError, match="Antenna names must be integers"):
        badp = {
            k: v for k, v in simplest_working_params.items() if k != "antenna_positions"
        }
        UVData.new(
            antenna_positions=np.array([[0, 0, 0], [0, 0, 1], [0, 0, 2]]),
            antenna_numbers=None,
            antenna_names=["foo", "bar", "baz"],
            **badp,
        )

    with pytest.raises(ValueError, match="antenna_positions must be a numpy array"):
        badp = {
            k: v for k, v in simplest_working_params.items() if k != "antenna_positions"
        }
        UVData.new(
            antenna_positions="foo",
            antenna_numbers=[0, 1, 2],
            antenna_names=["foo", "bar", "baz"],
            **badp,
        )

    with pytest.raises(ValueError, match="antenna_positions must be a 2D array"):
        badp = {
            k: v for k, v in simplest_working_params.items() if k != "antenna_positions"
        }
        UVData.new(
            antenna_positions=np.array([0, 0, 0]), antenna_numbers=np.array([0]), **badp
        )

    with pytest.raises(ValueError, match="Duplicate antenna names found"):
        UVData.new(antenna_names=["foo", "bar", "foo"], **simplest_working_params)

    with pytest.raises(ValueError, match="Duplicate antenna numbers found"):
        badp = {
            k: v for k, v in simplest_working_params.items() if k != "antenna_positions"
        }
        UVData.new(
            antenna_positions=np.array([[0, 0, 0], [0, 0, 1], [0, 0, 2]]),
            antenna_numbers=[0, 1, 0],
            antenna_names=["foo", "bar", "baz"],
            **badp,
        )

    with pytest.raises(
        ValueError, match="antenna_numbers and antenna_names must have the same length"
    ):
        UVData.new(antenna_names=["foo", "bar"], **simplest_working_params)


def test_bad_time_inputs(simplest_working_params: dict[str, Any]):
    with pytest.raises(ValueError, match="time_array must be a numpy array"):
        get_time_params(
            telescope_location=simplest_working_params["telescope_location"],
            time_array="hello this is a string",
        )

    with pytest.raises(ValueError, match="integration_time must be a numpy array"):
        get_time_params(
            telescope_location=simplest_working_params["telescope_location"],
            integration_time={"a": "dict"},
            time_array=simplest_working_params["unique_times"],
        )

    with pytest.raises(
        ValueError, match="integration_time must be the same shape as time_array"
    ):
        get_time_params(
            integration_time=np.ones(len(simplest_working_params["unique_times"]) + 1),
            telescope_location=simplest_working_params["telescope_location"],
            time_array=simplest_working_params["unique_times"],
        )


def test_bad_freq_inputs(simplest_working_params: dict[str, Any]):
    with pytest.raises(ValueError, match="freq_array must be a numpy array"):
        badp = {k: v for k, v in simplest_working_params.items() if k != "freq_array"}
        UVData.new(freq_array="hello this is a string", **badp)

    with pytest.raises(ValueError, match="channel_width must be a numpy array"):
        badp = {
            k: v for k, v in simplest_working_params.items() if k != "channel_width"
        }
        UVData.new(channel_width={"a": "dict"}, **badp)

    with pytest.raises(
        ValueError, match="channel_width must be the same shape as freq_array"
    ):
        badp = {
            k: v for k, v in simplest_working_params.items() if k != "channel_width"
        }
        UVData.new(
            channel_width=np.ones(len(simplest_working_params["freq_array"]) + 1),
            **badp,
        )


def test_bad_baseline_inputs():
    with pytest.raises(
        ValueError, match="Either antpairs or unique_antpairs must be provided"
    ):
        get_baseline_params(
            antenna_positions=np.array([[0, 0, 0], [0, 0, 1], [0, 0, 2]])
        )


def test_bad_rectangularity_inputs():
    with pytest.raises(
        ValueError, match="Either baseline_array or unique_baselines must be provided"
    ):
        configure_blt_rectangularity(unique_times=np.linspace(2459855, 2459856, 20))

    with pytest.raises(
        ValueError, match="Either time_array or unique_times must be provided"
    ):
        configure_blt_rectangularity(
            unique_baselines=np.array([[0, 1], [0, 2], [1, 2]])
        )

    with pytest.raises(
        ValueError,
        match="Only one of baseline_array or unique_baselines can be provided",
    ):
        configure_blt_rectangularity(
            unique_times=np.linspace(2459855, 2459856, 20),
            unique_baselines=np.array([[0, 1], [0, 2], [1, 2]]),
            baseline_array=np.array([0, 1, 2, 3, 4, 5]),
        )

    with pytest.raises(
        ValueError, match="Only one of time_array or unique_times can be provided"
    ):
        configure_blt_rectangularity(
            unique_times=np.linspace(2459855, 2459856, 20),
            unique_baselines=np.array([[0, 1], [0, 2], [1, 2]]),
            time_array=np.linspace(2459855, 2459856, 20),
        )

    with pytest.raises(
        ValueError,
        match="If unique_times are provided, unique_baselines must be provided",
    ):
        configure_blt_rectangularity(
            unique_times=np.linspace(2459855, 2459856, 20),
            baseline_array=np.array([0, 1, 2, 3, 4, 5]),
        )

    with pytest.raises(
        ValueError,
        match="If unique_baselines are provided, unique_times must be provided",
    ):
        configure_blt_rectangularity(
            unique_baselines=np.array([[0, 1], [0, 2], [1, 2]]),
            time_array=np.linspace(2459855, 2459856, 20),
        )

    with pytest.raises(
        ValueError,
        match="If unique_times are provided, blts_are_rectangular must be True",
    ):
        configure_blt_rectangularity(
            unique_times=np.linspace(2459855, 2459856, 20),
            unique_baselines=np.array([[0, 1], [0, 2], [1, 2]]),
            blts_are_rectangular=False,
        )


def test_alternate_antenna_inputs():
    antpos_dict = {
        0: np.array([0, 0, 0]),
        1: np.array([0, 0, 1]),
        2: np.array([0, 0, 2]),
    }

    antpos_array = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 2]])
    antnum = np.array([0, 1, 2])
    antname = np.array(["000", "001", "002"])

    pos, names, nums = get_antenna_params(antenna_positions=antpos_dict)
    pos2, names2, nums2 = get_antenna_params(
        antenna_positions=antpos_array, antenna_numbers=antnum, antenna_names=antname
    )

    assert np.allclose(pos, pos2)
    assert np.all(names == names2)
    assert np.all(nums == nums2)

    antpos_dict = {
        "000": np.array([0, 0, 0]),
        "001": np.array([0, 0, 1]),
        "002": np.array([0, 0, 2]),
    }
    pos, names, nums = get_antenna_params(antenna_positions=antpos_dict)
    assert np.allclose(pos, pos2)
    assert np.all(names == names2)
    assert np.all(nums == nums2)


def test_alternate_time_inputs():
    loc = EarthLocation.from_geodetic(0, 0, 0)

    time_array = np.linspace(2459855, 2459856, 20)
    integration_time = (time_array[1] - time_array[0]) * 24 * 60 * 60

    times, ints = get_time_params(
        time_array=time_array, integration_time=integration_time, telescope_location=loc
    )
    times2, ints2 = get_time_params(
        time_array=time_array,
        integration_time=integration_time * np.ones_like(time_array),
        telescope_location=loc,
    )
    assert np.allclose(times, times2)
    assert np.allclose(ints, ints2)

    times3, ints3 = get_time_params(time_array=time_array, telescope_location=loc)
    assert np.allclose(times, times3)
    assert np.allclose(ints, ints3)


def test_alternate_freq_inputs():
    freq_array = np.linspace(1e8, 2e8, 15)
    channel_width = freq_array[1] - freq_array[0]

    freqs, widths = get_freq_params(freq_array=freq_array, channel_width=channel_width)

    freqs2, widths2 = get_freq_params(
        freq_array=freq_array, channel_width=channel_width * np.ones_like(freq_array)
    )
    assert np.allclose(freqs, freqs2)
    assert np.allclose(widths, widths2)

    freqs3, widths3 = get_freq_params(freq_array=freq_array)
    assert np.allclose(freqs, freqs3)
    assert np.allclose(widths, widths3)


def test_alternative_baseline_inputs():
    antpos = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 2]])
    ap = [(0, 0), (0, 1), (0, 2)]

    bls, ubls = get_baseline_params(antenna_positions=antpos, antpairs=ap)
    bls2, ubls2 = get_baseline_params(antenna_positions=antpos, unique_antpairs=ap)

    assert np.all(bls == ubls2)
    assert np.all(bls2 == ubls)


def test_empty(simplest_working_params: dict[str, Any]):
    uvd = UVData.new(empty=True, **simplest_working_params)

    assert uvd.data_array.shape == (uvd.Nblts, uvd.Nfreqs, uvd.Npols)
    assert uvd.flag_array.shape == uvd.data_array.shape == uvd.nsample_array.shape
    assert not np.any(uvd.flag_array)
    assert np.all(uvd.nsample_array == 1)
    assert np.all(uvd.data_array == 0)


def test_passing_data(simplest_working_params: dict[str, Any]):
    uvd = UVData.new(empty=True, **simplest_working_params)
    shape = uvd.data_array.shape

    uvd = UVData.new(
        data_array=np.zeros(shape, dtype=complex), **simplest_working_params
    )

    assert np.all(uvd.data_array == 0)
    assert np.all(uvd.flag_array == 0)
    assert np.all(uvd.nsample_array == 1)

    uvd = UVData.new(
        data_array=np.zeros(shape, dtype=complex),
        flag_array=np.ones(shape, dtype=bool),
        **simplest_working_params,
    )

    assert np.all(uvd.data_array == 0)
    assert np.all(uvd.flag_array)
    assert np.all(uvd.nsample_array == 1)

    uvd = UVData.new(
        data_array=np.zeros(shape, dtype=complex),
        flag_array=np.ones(shape, dtype=bool),
        nsample_array=np.ones(shape, dtype=int),
        **simplest_working_params,
    )

    assert np.all(uvd.data_array == 0)
    assert np.all(uvd.flag_array)
    assert np.all(uvd.nsample_array == 1)


def test_passing_bad_data(simplest_working_params: dict[str, Any]):
    uvd = UVData.new(empty=True, **simplest_working_params)
    shape = uvd.data_array.shape

    with pytest.raises(ValueError, match="Data array shape"):
        uvd = UVData.new(
            data_array=np.zeros((1, 2, 3), dtype=float), **simplest_working_params
        )

    with pytest.raises(ValueError, match="Flag array shape"):
        uvd = UVData.new(
            data_array=np.zeros(shape, dtype=complex),
            flag_array=np.ones((1, 2, 3), dtype=float),
            **simplest_working_params,
        )

    with pytest.raises(ValueError, match="nsample array shape"):
        uvd = UVData.new(
            data_array=np.zeros(shape, dtype=complex),
            flag_array=np.ones(shape, dtype=bool),
            nsample_array=np.ones((1, 2, 3), dtype=float),
            **simplest_working_params,
        )


def test_passing_kwargs(simplest_working_params: dict[str, Any]):
    uvd = UVData.new(blt_order=("time", "baseline"), **simplest_working_params)

    assert uvd.blt_order == ("time", "baseline")


def test_blt_rect():
    utimes = np.linspace(2459855, 2459856, 20)
    ubls = np.array([1, 2, 3])

    nbls, ntimes, rect, axis, times, bls = configure_blt_rectangularity(
        unique_times=utimes, unique_baselines=ubls, time_axis_faster_than_bls=False
    )

    assert nbls == 3
    assert ntimes == 20
    assert rect
    assert not axis
    assert len(times) == len(bls)
    assert times[1] == times[0]
    assert bls[1] != bls[0]

    TIMES, BLS = np.meshgrid(utimes, ubls)
    TIMES = TIMES.flatten()
    BLS = BLS.flatten()

    nbls, ntimes, rect, axis, times, bls = configure_blt_rectangularity(
        time_array=TIMES, baseline_array=BLS, blts_are_rectangular=True
    )

    assert nbls == 3
    assert ntimes == 20
    assert rect
    assert axis
    assert len(times) == len(bls)
    assert times[1] != times[0]
    assert bls[1] == bls[0]

    BLS, TIMES = np.meshgrid(ubls, utimes)
    TIMES = TIMES.flatten()
    BLS = BLS.flatten()

    nbls, ntimes, rect, axis, times, bls = configure_blt_rectangularity(
        time_array=TIMES, baseline_array=BLS, blts_are_rectangular=True
    )

    assert nbls == 3
    assert ntimes == 20
    assert rect
    assert not axis
    assert len(times) == len(bls)
    assert times[1] == times[0]
    assert bls[1] != bls[0]

    nbls, ntimes, rect, axis, times, bls = configure_blt_rectangularity(
        time_array=TIMES, baseline_array=BLS, blts_are_rectangular=False
    )

    assert nbls == 3
    assert ntimes == 20
    assert not rect
    assert not axis
    assert len(times) == len(bls)
    assert times[1] == times[0]
    assert bls[1] != bls[0]

    nbls, ntimes, rect, axis, times, bls = configure_blt_rectangularity(
        time_array=TIMES, baseline_array=BLS
    )

    assert nbls == 3
    assert ntimes == 20
    assert rect
    assert not axis
    assert len(times) == len(bls)
    assert times[1] == times[0]
    assert bls[1] != bls[0]