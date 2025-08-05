"""Module that provides a Profile2d class and plotting tools for it."""

from enum import Enum

import numpy as np

from .binning import bin_centers


class Profile2d:
    """
    A class to calculate 2D profiles.

    Includes binning and calculation of statistics such as mean, standard deviation,
    median, and standard error of the mean for each bin.

    Attributes
    ----------
    bins : int
        The number of bins for the x and y data.
    x_data : np.ndarray
        The x data to be binned.
    y_data : np.ndarray
        The y data to be binned.
    binned_data : list
        A list of binned y-data corresponding to the x bins.
    bin_edges : np.ndarray
        The bin edges for the x data.
    means : list
        The means for each x bin.
    stds : list
        The standard deviations for each x bin.
    sems : list
        The standard errors of the mean for each x bin.
    medians : list
        The medians for each x bin.
    """

    def __init__(self, x_data: np.ndarray, y_data: np.ndarray, bins: int = 10) -> None:
        """
        Initialize a Profile2d object with x and y data and the number of bins.

        Parameters
        ----------
        x_data : np.ndarray
            The x data to be binned.
        y_data : np.ndarray
            The y data to be binned.
        bins : int, optional
            The number of bins to use for the profile (default is 10).
        """
        self._bins = bins
        self._x_data = x_data
        self._y_data = y_data

        self._calculate_bin_data()
        self._calculate_statistics()

    def _calculate_bin_data(self) -> None:
        """
        Calculate the bin data based on the x and y data using 2D histogram binning.

        This function bins the y_data based on the x_data, and stores the binned data
        along with the bin edges.
        """
        x_data = self.x_data
        y_data = self.y_data

        _hist, bin_x_edges, _bin_y_edges = np.histogram2d(x_data, y_data, self.bins)

        bin_data = [
            y_data[(bin_x_edges[idx] <= x_data) & (x_data < bin_x_edges[idx + 1])]
            for idx in range(bin_x_edges.size - 1)
        ]
        # Righthand-most bin is closed and not half-open!
        bin_data[-1] = np.append(bin_data[-1], y_data[x_data == bin_x_edges[-1]])

        self._binned_data = bin_data
        self._bin_edges = bin_x_edges

    def _calculate_statistics(self) -> None:
        """
        Calculate statistics (mean, std, sem, median) for each bin.

        The statistics are calculated for each x bin, and the results are stored
        as lists for means, standard deviations, standard errors, and medians.
        """
        self._means, self._stds, self._sems, self._medians = [], [], [], []
        for data in self.bin_data:
            if data.size > 0:
                mean = np.mean(data)
                std = np.std(data, ddof=1)
                sem = std / np.sqrt(np.size(data))
                median = np.median(data)
            else:
                mean, std, sem, median = np.nan, np.nan, np.nan, np.nan
            self._means.append(mean)
            self._stds.append(std)
            self._sems.append(sem)
            self._medians.append(median)

    @property
    def bins(self) -> int:
        """Return the number of bins."""
        return self._bins

    @property
    def bin_data(self) -> list:
        """Return the binned data."""
        return self._binned_data

    @property
    def bin_centers(self) -> np.ndarray:
        """Return the centers for the x bins."""
        return bin_centers(self._bin_edges)

    @property
    def bin_edges(self) -> np.ndarray:
        """Return the edges for the x bins."""
        return self.__bin_edges

    @property
    def bin_means(self) -> list:
        """Return the means for each x bin."""
        return self._means

    @property
    def bin_medians(self) -> list:
        """Return the medians for each x bin."""
        return self._medians

    @property
    def bin_stds(self) -> list:
        """Return the standard deviations for each x bin."""
        return self._stds

    @property
    def bin_sems(self) -> list:
        """Return the standard error of the mean for each x bin."""
        return self._sems

    @property
    def x_data(self) -> np.ndarray:
        """Return the x data."""
        return self._x_data

    @property
    def y_data(self) -> np.ndarray:
        """Return the y data."""
        return self._y_data

    def get_statistics(
        self, identifier: str, none_ok: bool = False
    ) -> np.ndarray | None:
        """
        Get the statistics for the requested identifier.

        Parameters
        ----------
        identifier : str
            The identifier for the statistic (e.g., 'mean', 'median').
        none_ok : bool, optional
            Whether to return None if 'None' is requested (default is False).

        Returns
        -------
        np.ndarray or None
            The requested statistic, or None if `none_ok` is True.
        """
        match Quantity.select(identifier):
            case Quantity.MEAN:
                return self.bin_means
            case Quantity.MEDIAN:
                return self.bin_medians
            case Quantity.SEM:
                return self.bin_sems
            case Quantity.STD:
                return self.bin_stds
            case Quantity.NONE if none_ok:
                return None
            case _:
                msg = f"Identifier '{identifier}' not recognized!"
                raise ValueError(msg)


class Quantity(Enum):
    """Enum for different statistical quantities (mean, median, etc.)."""

    MEAN = "mean"
    MEDIAN = "median"
    SEM = "sem"
    STD = "std"
    NONE = None

    @classmethod
    def select(cls, name: str) -> "Quantity":
        """
        Select a Quantity based on the string input.

        Parameters
        ----------
        name : str
            The name of the quantity (e.g., 'mean', 'std').

        Returns
        -------
        Quantity
            The corresponding Quantity enum member.
        """
        match name.lower() if isinstance(name, str) else name:
            case "mean":
                return cls.MEAN
            case "median":
                return cls.MEDIAN
            case "sem" | "standard error on the mean":
                return cls.SEM
            case "std" | "standard deviation":
                return cls.STD
            case 0 | None | False:
                return cls.NONE
            case _:
                msg = f"Value '{name}' not recognized!"
                raise ValueError(msg)


class Profile2dPlotter:
    """A base class for plotting Profile2d statistics."""

    def __init__(self, quantity: str, err: str | None = None, **kwargs) -> None:
        """
        Initialize the plotter with the specified quantity and error type.

        Parameters
        ----------
        quantity : str
            The statistic to plot (e.g., 'mean', 'median').
        err : Optional[str], optional
            The error type to plot (e.g., 'sem'). Default is None.
        kwargs : dict
            Additional keyword arguments passed to matplotlib.
        """
        self._quantity = quantity
        self._err = err

        self._add_default_options(kwargs)
        self._options = kwargs

    def _add_default_options(self, options: dict) -> None:
        """
        Add default options to the plotting options.

        Parameters
        ----------
        options : dict
            A dictionary of plotting options to update.
        """
        options.setdefault("linestyle", "")
        options.setdefault("barsabove", True)

    @property
    def quantity(self) -> str:
        """Return the quantity to plot."""
        return self._quantity

    @property
    def err(self) -> str | None:
        """Return the error type to plot."""
        return self._err

    @property
    def options(self) -> dict:
        """Return the plotting options passed to matplotlib."""
        return self._options

    def plot(self, ax, profile: Profile2d) -> None:
        """
        Plot the 2D profile statistics on the given axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis to plot on.
        profile : Profile2d
            The Profile2d object containing the data to plot.
        """
        x_center = profile.bin_centers
        y_data = profile.get_statistics(self.quantity)
        y_err = profile.get_statistics(self.err, none_ok=True)

        ax.errorbar(x_center, y_data, yerr=y_err, **self.options)


class Profile2dMeanPlotter(Profile2dPlotter):
    """A plotter for the mean statistics of a Profile2d."""

    def __init__(self, err: str | None = "sem", **kwargs) -> None:
        super().__init__("mean", err=err, **kwargs)

    def _add_default_options(self, options: dict) -> None:
        options.setdefault("color", "r")
        options.setdefault("marker", ".")
        options.setdefault("markersize", 5)
        options.setdefault("elinewidth", 1)
        options.setdefault("capsize", 2)

        return super()._add_default_options(options)


class Profile2dMedianPlotter(Profile2dPlotter):
    """A plotter for the median statistics of a Profile2d."""

    def __init__(self, err: str | None = None, **kwargs) -> None:
        super().__init__("median", err=err, **kwargs)

    def _add_default_options(self, options: dict) -> None:
        options.setdefault("color", "deeppink")
        options.setdefault("marker", "s")
        options.setdefault("markersize", 6)

        return super()._add_default_options(options)


def plot_profile2d(ax, profile: Profile2d, *plotters: Profile2dPlotter):
    """
    Plot the 2D profile using one or more plotters.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis to plot on.
    profile : Profile2d
        The Profile2d object containing the data to plot.
    plotters : Profile2dPlotter
        One or more plotters to use for plotting.
    """
    if not plotters:
        plotters = (Profile2dMeanPlotter(), Profile2dMedianPlotter())

    for plotter in plotters:
        plotter.plot(ax, profile)
