"""This module provides various tools for data visualization."""

from importlib.metadata import version, PackageNotFoundError

from visdata.__util import get_module, get_numpy
from visdata.binned_data import (
    Profile2d,
    Profile2dMedianPlotter,
    Profile2dMeanPlotter,
    Profile2dPlotter,
    plot_profile2d,
)
from visdata.output import Table, object_vars_str
from visdata.plotting import (
    Measurement,
    MeasurementResultPlotConfig,
    MeasurementResult,
    CompareMeasurementsPlot,
    Histogram2d,
    MarginalPlot,
    MarginalPlotGrid,
)

try:
    __version__ = version("visdata")
except PackageNotFoundError:
    __version__ = "dev"

__all__ = [
    "CompareMeasurementsPlot",
    "Histogram2d",
    "MarginalPlot",
    "MarginalPlotGrid",
    "Measurement",
    "MeasurementResult",
    "MeasurementResultPlotConfig",
    "Profile2d",
    "Profile2dMeanPlotter",
    "Profile2dMedianPlotter",
    "Profile2dPlotter",
    "Table",
    "get_module",
    "get_numpy",
    "object_vars_str",
    "plot_profile2d",
]
