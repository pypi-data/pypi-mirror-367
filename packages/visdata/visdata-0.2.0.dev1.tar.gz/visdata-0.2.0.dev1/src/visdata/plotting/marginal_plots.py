"""Module that provides tools for marginal plots."""

import warnings
from dataclasses import dataclass

from matplotlib import pyplot as plt


@dataclass(kw_only=True)
class MarginalPlotGrid:
    """
    A class to define the grid layout for a marginal plot.

    The layout includes the ratios for the main plot, colorbar, and marginals.

    Attributes
    ----------
    main_width_ratio : float
        The width ratio of the main plot.
    main_height_ratio : float
        The height ratio of the main plot.
    main_spacing : float
        The spacing between subplots.
    cbar_width_ratio : float
        The width ratio of the colorbar.
    cbar_spacing : float
        The spacing around the colorbar.
    misc_ratio : float
        An additional ratio for miscellaneous margins.
    """

    main_width_ratio: float = 5
    main_height_ratio: float = 5
    main_spacing: float = 0
    cbar_width_ratio: float = 0.5
    cbar_spacing: float = 0.15
    misc_ratio: float = 1

    def __post_init__(self):
        """
        Check if the misc_ratio deviates from the default value (1).

        Raises a warning if misc_ratio is modified.
        """
        if self.misc_ratio != 1:
            msg = f"'misc_ratio'={self.misc_ratio} may break the layout!"
            warnings.warn(msg, stacklevel=2)

    def get_width_ratios(self) -> tuple[float, float, float]:
        """
        Get the width ratios for the grid layout.

        This takes into account the main plot width, the miscellaneous
        margin width, and the colorbar width.

        Returns
        -------
        Tuple[float, float, float]
            The width ratios for the grid layout.
        """
        return (self.main_width_ratio, self.misc_ratio, self.cbar_width_ratio)

    def get_height_ratios(self, fig: plt.Figure) -> tuple[float, float]:
        """
        Get the height ratios for the grid layout, adjusted based on the
        figure size and the width ratios.

        Parameters
        ----------
        fig : matplotlib.pyplot.Figure
            The figure object to adjust the height ratios according to its size.

        Returns
        -------
        Tuple[float, float]
            The height ratios for the grid layout, including the adjustment.
        """
        # Get the figure ratio
        figsize = fig.get_size_inches()
        fig_ratio = figsize[0] / figsize[1]

        # Calculate the needed ratio value
        main_ratio = self.misc_ratio / sum(self.get_width_ratios())
        factor = main_ratio * fig_ratio
        fix_ratio = self.main_height_ratio * factor / (1 - factor)

        return (fix_ratio, self.main_height_ratio)

    def get_cbar_width(self, fig: plt.Figure) -> float:
        """
        Get the width for the colorbar, adjusted according to the figure size.

        Parameters
        ----------
        fig : matplotlib.pyplot.Figure
            The figure object to calculate the colorbar width.

        Returns
        -------
        float
            The width of the colorbar in inches.
        """
        figsize = fig.get_size_inches()
        return (
            self.cbar_width_ratio / sum(self.get_width_ratios()) * figsize[0]
            - self.cbar_spacing
        )


class MarginalPlot:
    """
    Class to create a plot with subplots on the x and y axes, along with a colorbar.

    Attributes
    ----------
    fig : matplotlib.pyplot.Figure
        Pyplot figure for this plot.
    ax_main : matplotlib.pyplot.Axes
        Pyplot axes for the main plot.
    ax_marginal_x : matplotlib.pyplot.Axes
        Pyplot axes for the x marginal plot.
    ax_marginal_y : matplotlib.pyplot.Axes
        Pyplot axes for the y marginal plot.
    ax_cbar : matplotlib.pyplot.Axes
        Pyplot axes for the colorbar.
    grid_spec : matplotlib.pyplot.GridSpec
        Pyplot grid spec used to create the axes.
    """

    def __init__(
        self, grid: MarginalPlotGrid | None = None, cbar_int: bool = True
    ) -> None:
        """
        Initialize the MarginalPlot with a specified layout grid and additional options.

        Parameters
        ----------
        grid : MarginalPlotGrid, optional
            The layout grid for the plot. If None, a default grid is used.
        cbar_int : bool, optional
            Whether to display the colorbar with integer ticks (default is True).
        """
        self._grid = grid or MarginalPlotGrid()
        self._cbar_int = cbar_int

        self._make_subplots()

    def _make_subplots(self) -> None:
        """
        Create the subplots for the marginal plot.

        Includes the main plot, subplots for the x and y axes, and the colorbar.
        """
        grid = self._grid
        fig = plt.figure()

        grid_spec = fig.add_gridspec(
            nrows=2,
            ncols=3,
            wspace=grid.main_spacing,
            hspace=grid.main_spacing,
            width_ratios=grid.get_width_ratios(),
            height_ratios=grid.get_height_ratios(fig),
        )
        ax_main = fig.add_subplot(grid_spec[1, 0])
        ax_marginal_x = fig.add_subplot(grid_spec[0, 0], sharex=ax_main)
        ax_marginal_y = fig.add_subplot(grid_spec[1, 1], sharey=ax_main)
        ax_cbar = ax_marginal_y.inset_axes(
            [1 + grid.cbar_spacing, 0, grid.get_cbar_width(fig), 1]
        )
        if self._cbar_int:
            ax_cbar.yaxis.get_major_locator().set_params(integer=True)

        plt.setp(ax_marginal_x.get_xticklabels(), visible=False)
        plt.setp(ax_marginal_y.get_yticklabels(), visible=False)

        self.fig = fig
        self.ax_main = ax_main
        self.ax_marginal_x = ax_marginal_x
        self.ax_marginal_y = ax_marginal_y
        self.ax_cbar = ax_cbar
        self.grid_spec = grid_spec

    def subplots(self) -> tuple[plt.Figure, plt.Axes, plt.Axes, plt.Axes, plt.Axes]:
        """
        Get figure and axes for the marginal plot.

        Returns
        -------
        Tuple[plt.Figure, plt.Axes, plt.Axes, plt.Axes, plt.Axes]
            The figure and axes for the main plot, marginal subplots, and colorbar.
        """
        return (
            self.fig,
            self.ax_main,
            self.ax_marginal_x,
            self.ax_marginal_y,
            self.ax_cbar,
        )
