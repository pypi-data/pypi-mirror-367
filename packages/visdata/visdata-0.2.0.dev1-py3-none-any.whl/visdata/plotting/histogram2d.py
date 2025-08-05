"""Module containing a 2D histogram with marginal histograms and 2D profiles."""

import numpy as np
from matplotlib import pyplot as plt

from visdata.plotting.marginal_plots import MarginalPlot, MarginalPlotGrid
from visdata.binned_data.profile2d import (
    Profile2d,
    Profile2dPlotter,
    Profile2dMeanPlotter,
    Profile2dMedianPlotter,
    plot_profile2d,
)


class Histogram2d:
    """Class to create a 2D histogram with optional marginal histograms and profiles."""

    def __init__(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        bins: int | tuple[int] = 10,
        x_label: str | None = None,
        y_label: str | None = None,
        c_label: str | None = None,
        profile_plotters: list[Profile2dPlotter] | None = None,
        marginal_grid: MarginalPlotGrid | None = None,
        marginal_cbar_int: bool = True,
        **marginal_options,
    ) -> None:
        """
        Initialize a Histogram2d object with x and y data and the number of bins.

        Parameters
        ----------
        x_data : np.ndarray
            Array of x-values.
        y_data : np.ndarray
            Array of y-values.
        bins : int or tuple of int, optional
            Number of bins for the histogram. Can be a single int or (x_bins, y_bins).
        x_label : str, optional
            Label for the x-axis.
        y_label : str, optional
            Label for the y-axis.
        c_label : str, optional
            Label for the colorbar.
        profile_plotters : list of Profile2dPlotter, optional
            Plotter objects used to create profile plots.
        marginal_grid : MarginalPlotGrid, optional
            Grid layout for marginal plots. Defaults to a standard grid.
        marginal_cbar_int : bool, optional
            Whether the colorbar for marginal plots should use integer ticks.
        marginal_options : dict, optional
            Options for marginal histograms (passed to matplotlib.axes.Axes.hist).
        """
        self.bins = bins
        self.x_data = x_data
        self.y_data = y_data
        self.x_label = x_label
        self.y_label = y_label
        self.c_label = c_label
        self.marginal_grid = marginal_grid or MarginalPlotGrid()
        self.marginal_cbar_int = marginal_cbar_int
        self.marginal_options = marginal_options
        self.profile_plotters = profile_plotters or [
            Profile2dMeanPlotter(),
            Profile2dMedianPlotter(),
        ]

    def configure_marginal(self, **marginal_options) -> None:
        """
        Update options for marginal histograms.

        Parameters
        ----------
        marginal_options : dict, optional
            Options for marginal histograms (passed to matplotlib.axes.Axes.hist).
        """
        self.marginal_options.update(marginal_options)

    def add_marginal_histograms(
        self, ax_hist_x: plt.Axes, ax_hist_y: plt.Axes
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Add marginal histograms along the x and y axes.

        Parameters
        ----------
        ax_hist_x : matplotlib.axes.Axes
            Axis for the top marginal histogram.
        ax_hist_y : matplotlib.axes.Axes
            Axis for the right marginal histogram.

        Returns
        -------
        hist_x : np.ndarray
            Output of `ax.hist()` for x-data.
        hist_y : np.ndarray
            Output of `ax.hist()` for y-data (horizontal).
        """
        if isinstance(self.bins, tuple | list | np.ndarray):
            bins_x, bins_y = self.bins
        else:
            bins_x = self.bins
            bins_y = self.bins
        hist_x = ax_hist_x.hist(self.x_data, bins=bins_x, **self.marginal_options)
        hist_y = ax_hist_y.hist(
            self.y_data,
            bins=bins_y,
            orientation="horizontal",
            **self.marginal_options,
        )
        ax_hist_x.set_yticks(ax_hist_x.get_yticks()[1:])
        ax_hist_y.set_xticks(ax_hist_y.get_xticks()[1:])
        ax_hist_x.set_ylabel(self.c_label)
        ax_hist_y.set_xlabel(self.c_label)

        return hist_x, hist_y

    def plot(self, marginal: bool = False, profile: bool = False, **kwargs) -> dict:
        """
        Plot the 2D histogram, with optional marginal histograms and profile overlays.

        Parameters
        ----------
        marginal : bool, optional
            Whether to include marginal histograms.
        profile : bool, optional
            Whether to overlay profile plots on top of the 2D histogram.
        **kwargs : dict
            Additional keyword arguments passed to `ax.hist2d()`.

        Returns
        -------
        results : dict
            Dictionary containing figure, axes, and histogram objects:
            - 'fig': matplotlib.figure.Figure
            - 'ax_hist2d': matplotlib.axes.Axes
            - 'hist2d': tuple of (hist, xedges, yedges, image)
            - 'ax_cbar': matplotlib.axes.Axes or None
            - Optional:
                'ax_marginal_x', 'ax_marginal_y', 'hist_marginal_x', 'hist_marginal_y'
            - Optional: 'profile2d'
        """
        # Get subplots
        if marginal:
            marginal_plot = MarginalPlot(
                self.marginal_grid, cbar_int=self.marginal_cbar_int
            )
            fig = marginal_plot.fig
            ax_hist2d = marginal_plot.ax_main
            ax_cbar = marginal_plot.ax_cbar
        else:
            fig, ax_hist2d = plt.subplots()
            ax_cbar = None

        # Plot 2d histogram
        hist, xedges, yedges, image = ax_hist2d.hist2d(
            self.x_data, self.y_data, bins=self.bins, **kwargs
        )
        ax_hist2d.set_xlabel(self.x_label)
        ax_hist2d.set_ylabel(self.y_label)
        fig.colorbar(image, cax=ax_cbar, label=self.c_label)
        results = {
            "fig": fig,
            "ax_hist2d": ax_hist2d,
            "hist2d": (hist, xedges, yedges, image),
            "ax_cbar": ax_cbar,
        }

        # Add marginal histograms
        if marginal:
            ax_hist_x = marginal_plot.ax_marginal_x
            ax_hist_y = marginal_plot.ax_marginal_y
            hist_x, hist_y = self.add_marginal_histograms(ax_hist_x, ax_hist_y)
            results["ax_marginal_x"] = ax_hist_x
            results["hist_marginal_x"] = hist_x
            results["ax_marginal_y"] = ax_hist_y
            results["hist_marginal_y"] = hist_y

        # Add profile
        if profile:
            data_profile2d = Profile2d(self.x_data, self.y_data, self.bins)
            plot_profile2d(ax_hist2d, data_profile2d, *self.profile_plotters)
            results["profile2d"] = data_profile2d

        return results
