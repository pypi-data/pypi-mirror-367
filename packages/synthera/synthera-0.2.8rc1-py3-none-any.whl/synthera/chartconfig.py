from typing import Any

from cycler import cycler

rcParamsSynthera: dict[str, Any] = {
    "font.size": 12,
    "image.cmap": "viridis",
    "figure.figsize": (8, 5),
    "figure.dpi": 300,
    "axes.prop_cycle": cycler(
        "color",
        [
            "#440154",
            "#21918c",
            "#31688e",
            "#35b779",
            "#9c179e",
            "#a52c60",
            "#cf4446",
            "#ed6925",
        ],
    ),
    "axes.titlesize": 16,
    "axes.labelsize": 12,
    "axes.grid": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "ytick.labelsize": 12,
    "xtick.labelsize": 12,
    "legend.fontsize": 11,
    "grid.linestyle": "--",
    "grid.alpha": 0.4,
    "grid.linewidth": 0.8,
    "legend.frameon": True,
    "legend.loc": "upper right",
    "patch.facecolor": "#348ABD",
    "lines.linewidth": 1.5,
    "lines.markersize": 3,
    "savefig.dpi": 500,
    "savefig.transparent": False,
}
