import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def regression_plot_with_errors(
    xs,
    ys,
    x_err=None,
    y_err=None,
    hue=None,
    ax=None,
    cmap="tab10",
    point_kwargs=None,
    errorbar_kwargs=None,
    line_kwargs=None,
    xlabel="x",
    ylabel="y",
    annotate_r=True,
):
    """Scatter + regression line with per-point x/y error bars and Pearson r.

    Parameters
    ----------
    xs, ys : array-like
        Point coordinates.
    x_err, y_err : array-like or None
        Per-point error magnitudes (symmetric). Passed to ax.errorbar.
    hue : array-like or None
        Per-point category labels used to color points/error bars. The
        regression line and Pearson r are computed over ALL points.
    ax : matplotlib Axes or None
        Draw onto this axes, else create a new figure.
    cmap : str
        Named colormap used to assign one color per hue level.

    Returns
    -------
    fig, ax
    """
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    x_err = None if x_err is None else np.asarray(x_err, dtype=float)
    y_err = None if y_err is None else np.asarray(y_err, dtype=float)

    point_kwargs = {"s": 40, "zorder": 3, **(point_kwargs or {})}
    errorbar_kwargs = {
        "fmt": "none",
        "elinewidth": 1,
        "capsize": 2,
        "alpha": 0.6,
        "zorder": 2,
        **(errorbar_kwargs or {}),
    }
    line_kwargs = {"color": "black", "lw": 2, "zorder": 4, **(line_kwargs or {})}

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    else:
        fig = ax.figure

    # --- points + error bars, colored by hue -------------------------------
    if hue is None:
        groups = [(None, np.ones(len(xs), dtype=bool))]
    else:
        hue = np.asarray(hue)
        levels = list(dict.fromkeys(hue.tolist()))  # preserve first-seen order
        colors = plt.get_cmap(cmap)(np.linspace(0, 1, max(len(levels), 1)))
        groups = [(lvl, hue == lvl) for lvl in levels]

    for i, (label, m) in enumerate(groups):
        color = None if hue is None else colors[i]
        ax.errorbar(
            xs[m],
            ys[m],
            xerr=None if x_err is None else x_err[m],
            yerr=None if y_err is None else y_err[m],
            ecolor=color,
            **errorbar_kwargs,
        )
        ax.scatter(xs[m], ys[m], color=color, label=label, **point_kwargs)

    # --- regression over ALL points ----------------------------------------
    finite = np.isfinite(xs) & np.isfinite(ys)
    xf, yf = xs[finite], ys[finite]
    slope, intercept, r, p, _ = stats.linregress(xf, yf)
    xline = np.array([xf.min(), xf.max()])
    ax.plot(xline, slope * xline + intercept, **line_kwargs)

    if annotate_r:
        ax.annotate(
            f"Pearson r = {r:.3f}\np = {p:.2g}\nn = {finite.sum()}",
            xy=(0.05, 0.95),
            xycoords="axes fraction",
            va="top",
            ha="left",
            fontsize=11,
            bbox=dict(boxstyle="round", fc="white", ec="0.7", alpha=0.9),
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if hue is not None:
        ax.legend(title="hue", frameon=False)
    return fig, ax