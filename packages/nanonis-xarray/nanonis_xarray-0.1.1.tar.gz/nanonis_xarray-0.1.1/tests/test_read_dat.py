"""Test read_dat."""

from datetime import datetime
from pathlib import Path

from pint_xarray import unit_registry as u

from nanonis_xarray import read_dat

data_folder = Path(__file__).parent / "data"


def test_a() -> None:
    """Test read_dat."""
    data_path = data_folder / "a.dat"
    data = read_dat(data_path)

    assert "sweep" not in data.data_vars
    assert "direction" not in data.data_vars
    assert data.attrs["Bias Spectroscopy"]["MultiLine Settings"][
        "Integration"
    ] == 0.1 * u("ms")
    assert isinstance(data.attrs["NanonisMain"]["Session Path"], Path)
    assert isinstance(data.attrs["Date"], datetime)


def test_df_v() -> None:
    """Test read_dat."""
    data_path = data_folder / "df_v.dat"
    data = read_dat(data_path)

    assert "sweep" not in data.data_vars
    assert data.direction.size == 2
    assert isinstance(data.attrs["NanonisMain"]["Session Path"], Path)
    assert isinstance(data.attrs["Date"], datetime)


def test_z() -> None:
    """Test read_dat."""
    data_path = data_folder / "z.dat"
    data = read_dat(data_path)

    assert data.attrs["Bias Spectroscopy"]["backward sweep"] is True
    assert data.sweep.size == 3
    assert data.direction.size == 2
    assert isinstance(data.attrs["NanonisMain"]["Session Path"], Path)
    assert isinstance(data.attrs["Date"], datetime)
