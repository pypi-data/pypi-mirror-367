"""Read a Nanonis spectroscopy .dat file into an xarray Dataset."""

from importlib.metadata import version

from .read_dat import read_dat

__version__ = version("nanonis-xarray")
__all__ = ["read_dat"]
